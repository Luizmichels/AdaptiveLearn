from __future__ import annotations

import random
from typing import Optional

# Parâmetros do GA
TAM_CROMOSSOMO = 5       # número de exercícios por sequência
TAM_POP        = 30      # tamanho da população
N_GERACOES     = 50      # número de gerações
TAX_MUTACAO    = 0.10    # probabilidade de mutação por cromossomo
TAM_TORNEIO    = 3       # participantes no torneio de seleção
N_ELITE        = 2       # indivíduos preservados por elitismo
TEMPO_MAX      = 60      # minuto(s) restrição de tempo total

# Pesos da função fitness
W1 = 0.50   # proximidade de dificuldade
W2 = 0.30   # diversidade de subtópicos
W3 = 0.20   # penalidade de tempo

# Índice auxiliar (construído uma única vez por chamada a recomendar())
def _construir_indice(pool: list[dict]) -> dict[int, dict]:
    """Mapeia id → exercício para acesso O(1)."""
    return {e["id"]: e for e in pool}

# Função fitness
def _fitness(
    cromossomo: list[int],
    indice: dict[int, dict],
    nivel_ideal: float,
    tempo_max: int = TEMPO_MAX,
) -> float:
    # Avalia a qualidade de um cromossomo e retorna um valor entre 0 e 1 onde maior é igual a melhor
    exercicios = [indice[eid] for eid in cromossomo if eid in indice]
    if not exercicios:
        return 0.0

    n = len(exercicios)

    # componente 1: proximidade de dificuldade
    dif_media = sum(e["dificuldade"] for e in exercicios) / n
    # nivel_ideal está em [0, 10]; dificuldade também em [0, 10]
    comp_dif = 1.0 - abs(dif_media - nivel_ideal) / 10.0

    # componente 2: diversidade de subtópicos 
    subtopicos_unicos = len({e["subtopico"] for e in exercicios})
    comp_div = subtopicos_unicos / n

    # componente 3: penalidade de tempo 
    tempo_total = sum(e.get("tempo_min", e.get("tempo_estimado", 0)) for e in exercicios)
    if tempo_total > tempo_max:
        penalidade = (tempo_total - tempo_max) / tempo_max
    else:
        penalidade = 0.0

    return W1 * comp_dif + W2 * comp_div - W3 * penalidade

# Inicialização da população
def _populacao_inicial(
    ids_pool: list[int],
    tam_pop: int = TAM_POP,
    tam_cromo: int = TAM_CROMOSSOMO,
) -> list[list[int]]:
    """Gera uma população de cromossomos aleatórios sem repetições internas."""
    pop = []
    for _ in range(tam_pop):
        cromo = random.sample(ids_pool, min(tam_cromo, len(ids_pool)))
        pop.append(cromo)
    return pop


# Seleção por torneio
def _torneio(
    populacao: list[list[int]],
    scores: list[float],
    tam: int = TAM_TORNEIO,
) -> list[int]:
    """Retorna o cromossomo vencedor de um torneio aleatório."""
    participantes = random.sample(range(len(populacao)), min(tam, len(populacao)))
    vencedor = max(participantes, key=lambda i: scores[i])
    return list(populacao[vencedor])


# Crossover de 1 ponto (sem duplicatas)
def _crossover(
    pai1: list[int],
    pai2: list[int],
    tam_cromo: int = TAM_CROMOSSOMO,
) -> list[int]:
    #Pega os primeiros 'ponto' genes do pai1 e completa com genes do pai2 que não estejam presentes, sem duplicatas
    ponto = random.randint(2, tam_cromo - 1)  # [2, N-1]
    filho = pai1[:ponto]
    for gene in pai2:
        if gene not in filho:
            filho.append(gene)
        if len(filho) == tam_cromo:
            break
    return filho


# Mutação: substitui 1 gene por outro do pool
def _mutar(
    cromossomo: list[int],
    ids_pool: list[int],
    taxa: float = TAX_MUTACAO,
) -> list[int]:
    #Com probabilidade 'taxa' substitui um exercício aletório
    if random.random() < taxa:
        cromo = list(cromossomo)
        idx = random.randrange(len(cromo))
        candidatos = [eid for eid in ids_pool if eid not in cromo]
        if candidatos:
            cromo[idx] = random.choice(candidatos)
        return cromo
    return list(cromossomo)

# Loop principal do GA
def _executar_ga(
    ids_pool: list[int],
    indice: dict[int, dict],
    nivel_ideal: float,
    tam_pop: int = TAM_POP,
    n_geracoes: int = N_GERACOES,
    tam_cromo: int = TAM_CROMOSSOMO,
    n_elite: int = N_ELITE,
    taxa_mutacao: float = TAX_MUTACAO,
    tempo_max: int = TEMPO_MAX,
    historico_evolucao: Optional[list] = None,
) -> tuple[list[int], float]:
    #Roda o GA e retorna (melhor_cromossomo, melhor_fitness). Se 'historico_evolucao' for uma lista, acumula o melhor fitness de cada geração nela.
    populacao = _populacao_inicial(ids_pool, tam_pop, tam_cromo)

    melhor_cromo: list[int] = []
    melhor_score: float = -1.0

    for _ in range(n_geracoes):
        # avalia toda a população
        scores = [
            _fitness(c, indice, nivel_ideal, tempo_max)
            for c in populacao
        ]

        # atualiza o melhor global
        idx_melhor = max(range(len(scores)), key=lambda i: scores[i])
        if scores[idx_melhor] > melhor_score:
            melhor_score = scores[idx_melhor]
            melhor_cromo = list(populacao[idx_melhor])

        if historico_evolucao is not None:
            historico_evolucao.append(melhor_score)

        # elitismo: copia os N_ELITE melhores para a próxima geração
        ordem = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        nova_pop: list[list[int]] = [list(populacao[i]) for i in ordem[:n_elite]]

        # preenche o restante com filhos
        while len(nova_pop) < tam_pop:
            pai1 = _torneio(populacao, scores)
            pai2 = _torneio(populacao, scores)
            filho = _crossover(pai1, pai2, tam_cromo)
            filho = _mutar(filho, ids_pool, taxa_mutacao)
            nova_pop.append(filho)

        populacao = nova_pop

    return melhor_cromo, melhor_score


# Interface pública (consumida por main.py)
def recomendar(
    nivel_ideal: float,
    pool_exercicios: list[dict],
    n: int = TAM_CROMOSSOMO,
    tempo_max: int = TEMPO_MAX,
    seed: Optional[int] = None,
    historico_evolucao: Optional[list] = None,
) -> list[dict]:
    """
    Retorna uma lista de `n` exercícios recomendados pelo GA.

    Parâmetros
    ----------
    nivel_ideal        : saída da Camada II (Fuzzy), em [0, 10].
    pool_exercicios    : lista de dicts com chaves id, dificuldade,
                         subtopico, tempo_min (ou tempo_estimado).
    n                  : tamanho do cromossomo / sequência desejada.
    tempo_max          : limite de tempo total em minutos (default 60).
    seed               : semente para reprodutibilidade (opcional).
    historico_evolucao : se passada como lista vazia, será preenchida
                         com o melhor fitness de cada geração.

    Retorna
    -------
    Lista de dicts de exercícios (mesma estrutura do pool).
    """
    if not pool_exercicios:
        return []

    if seed is not None:
        random.seed(seed)

    # normaliza n para não exceder o pool
    tam_cromo = min(n, len(pool_exercicios))

    ids_pool = [e["id"] for e in pool_exercicios]
    indice   = _construir_indice(pool_exercicios)

    melhor_cromo, _ = _executar_ga(
        ids_pool=ids_pool,
        indice=indice,
        nivel_ideal=nivel_ideal,
        tam_pop=TAM_POP,
        n_geracoes=N_GERACOES,
        tam_cromo=tam_cromo,
        n_elite=N_ELITE,
        taxa_mutacao=TAX_MUTACAO,
        tempo_max=tempo_max,
        historico_evolucao=historico_evolucao,
    )

    return [indice[eid] for eid in melhor_cromo if eid in indice]

# Teste rápido (python ga.py)
if __name__ == "__main__":
    import os, sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dados import carregar_exercicios

    pool = carregar_exercicios()
    nivel = 6.0  # simula saída do Fuzzy

    historico: list[float] = []
    resultado = recomendar(nivel, pool, seed=42, historico_evolucao=historico)

    print(f"\nNível ideal: {nivel}")
    print(f"Sequência recomendada ({len(resultado)} exercícios):\n")
    for ex in resultado:
        print(
            f"  id={ex['id']:3d}  dif={ex['dificuldade']}  "
            f"tempo={ex.get('tempo_min', ex.get('tempo_estimado', '?'))}min  "
            f"{ex['topico']}/{ex['subtopico']}"
        )

    dif_media = sum(e["dificuldade"] for e in resultado) / len(resultado)
    tempo_total = sum(e.get("tempo_min", e.get("tempo_estimado", 0)) for e in resultado)
    subtopicos = {e["subtopico"] for e in resultado}

    print(f"\nDificuldade média:  {dif_media:.2f}  (ideal={nivel})")
    print(f"Tempo total:        {tempo_total} min")
    print(f"Subtópicos cobertos: {subtopicos}")
    print(f"\nEvolução fitness (primeiras/últimas gerações):")
    print(f"  Gen  1: {historico[0]:.4f}")
    print(f"  Gen 25: {historico[24]:.4f}")
    print(f"  Gen 50: {historico[-1]:.4f}")