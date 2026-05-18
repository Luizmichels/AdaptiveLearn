import os
import random

import matplotlib.pyplot as plt

from aluno import Aluno
from dados import carregar_exercicios
from ga import recomendar
from main import processar_resposta


DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_OUTPUTS = os.path.join(DIR_BASE, "outputs")

CAMINHO_FITNESS_GA = os.path.join(DIR_OUTPUTS, "fitness_ga.png")
CAMINHO_DIFICULDADE = os.path.join(DIR_OUTPUTS, "evolucao_dificuldade.png")
CAMINHO_TAXA_ACERTO = os.path.join(DIR_OUTPUTS, "taxa_acerto_sessao.png")


def gerar_grafico_fitness_ga():
    os.makedirs(DIR_OUTPUTS, exist_ok=True)

    pool = carregar_exercicios()
    nivel_ideal = 6.0

    historico = []

    recomendar(
        nivel_ideal=nivel_ideal,
        pool_exercicios=pool,
        seed=42,
        historico_evolucao=historico
    )

    plt.figure(figsize=(10, 5))
    plt.plot(range(1, len(historico) + 1), historico, marker="o")
    plt.title("Evolução do Fitness do Algoritmo Genético")
    plt.xlabel("Geração")
    plt.ylabel("Melhor Fitness")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CAMINHO_FITNESS_GA, dpi=300)
    plt.close()

    print(f"Gráfico salvo em: {CAMINHO_FITNESS_GA}")


def gerar_grafico_dificuldade():
    os.makedirs(DIR_OUTPUTS, exist_ok=True)

    random.seed(42)

    pool = carregar_exercicios()
    aluno = Aluno("Alice")

    dificuldades = []

    feedbacks = [
        "Nao entendi nada",
        "Foi razoavel",
        "Gostei bastante",
        "Muito dificil",
        "Foi tranquilo"
    ]

    proximos = random.sample(pool, 10)

    for exercicio in proximos:
        try:
            resultado = processar_resposta(
                aluno=aluno,
                exercicio=exercicio,
                feedback=random.choice(feedbacks),
                acertou=random.choice([True, False]),
                tempo_gasto=random.randint(3, 20),
                pool_exercicios=pool,
            )

            dificuldades.append(resultado["nivelIdeal"])

        except KeyError:
            dificuldades.append(5.0)

    plt.figure(figsize=(10, 5))
    plt.plot(
        range(1, len(dificuldades) + 1),
        dificuldades,
        marker="o"
    )

    plt.title("Evolução da Dificuldade Recomendada")
    plt.xlabel("Iteração")
    plt.ylabel("Nível Ideal")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CAMINHO_DIFICULDADE, dpi=300)
    plt.close()

    print(f"Gráfico salvo em: {CAMINHO_DIFICULDADE}")

def gerar_grafico_taxa_acerto():
    os.makedirs(DIR_OUTPUTS, exist_ok=True)

    random.seed(42)

    pool = carregar_exercicios()
    aluno = Aluno("Alice")

    taxas = []

    feedbacks = [
        "Nao entendi nada",
        "Foi razoavel",
        "Gostei bastante",
        "Muito dificil",
        "Foi tranquilo"
    ]

    proximos = random.sample(pool, 10)

    for exercicio in proximos:
        try:
            processar_resposta(
                aluno=aluno,
                exercicio=exercicio,
                feedback=random.choice(feedbacks),
                acertou=random.choice([True, False]),
                tempo_gasto=random.randint(3, 20),
                pool_exercicios=pool,
            )

            taxas.append(aluno.taxa_acerto_movel(janela=5) * 100)

        except KeyError:
            taxas.append(aluno.taxa_acerto_movel(janela=5) * 100)

    plt.figure(figsize=(10, 5))
    plt.plot(
        range(1, len(taxas) + 1),
        taxas,
        marker="o"
    )

    plt.title("Evolução da Taxa de Acerto do Aluno")
    plt.xlabel("Iteração")
    plt.ylabel("Taxa de Acerto (%)")
    plt.ylim(0, 100)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CAMINHO_TAXA_ACERTO, dpi=300)
    plt.close()

    print(f"Gráfico salvo em: {CAMINHO_TAXA_ACERTO}")

if __name__ == "__main__":
    gerar_grafico_fitness_ga()
    gerar_grafico_dificuldade()
    gerar_grafico_taxa_acerto()