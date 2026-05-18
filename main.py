from __future__ import annotations

import json
import os
import random

from aluno import Aluno
from dados import carregar_exercicios
from pln_nb import classificar
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/nivel")
def obter_nivel(acertos: int, tempo: int):

    taxa = acertos * 10

    nivel = inferir_nivel(5, taxa, tempo)

    return {
        "nivel": round(float(nivel), 2),
        "acertos": acertos,
        "tempo": tempo
    }

try:
    from fuzzy import inferir_nivel

    FUZZY_PRONTO = True
except ImportError:
    FUZZY_PRONTO = False

    def inferir_nivel(
        sentimento: float, taxa_acerto: float, tempo_gasto: float
    ) -> float:
        base = 5.0
        base += (sentimento - 0.5) * 4.0      # confiante -> mais dificil
        base += (taxa_acerto - 0.5) * 2.0     # acertando -> mais dificil
        base -= (tempo_gasto - 0.5) * 2.0     # demorando -> mais facil
        return max(0.0, min(10.0, base))


try:
    from ga import recomendar 

    GA_PRONTO = True
except ImportError:
    GA_PRONTO = False

    def recomendar(
        nivelIdeal: float, pool_exercicios: list[dict], n: int = 5
    ) -> list[dict]:
        ordenado = sorted(
            pool_exercicios,
            key=lambda e: abs(e["dificuldade"] - nivelIdeal),
        )
        return ordenado[:n]


DIR_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_HISTORICO = os.path.join(DIR_BASE, "data", "historico.json")

# Pipeline (esta funcao sera consumida pela FastAPI)
def processar_resposta(
    aluno: Aluno,
    exercicio: dict,
    feedback: str,
    acertou: bool,
    tempo_gasto: int,
    pool_exercicios: list[dict],
    n_recomendados: int = 5,
) -> dict:
    # 1) registra a resposta
    aluno.registrar_resposta(exercicio, acertou, tempo_gasto, feedback)

    # 2) Camada I — PLN
    classe_sentimento, prob_confiante = classificar(feedback)
    # converte sentimento
    mapa_sentimento = {
    "frustrado": 0,
    "neutro": 5,
    "confiante": 10,
    }

    valorSentimento = mapa_sentimento.get(classe_sentimento, 5)

    # 3) Sinais para a Camada II
    taxa = aluno.taxa_acerto_movel(janela=5) * 100
    tempo = tempo_gasto
    # normaliza tempo gasto em [0,1] usando 20 min como teto

    # 4) Camada II — Fuzzy
    nivelIdeal = float(
        inferir_nivel(
            valorSentimento,
            taxa,
            tempo
        )
    )
    # 5) Camada III — GA
    recomendados = recomendar(
        nivelIdeal, pool_exercicios, n=n_recomendados
    )

    return {
        "classe_sentimento": classe_sentimento,
        "prob_confiante": round(prob_confiante, 3),
        "taxa_acerto_movel": taxa,
        "nivelIdeal": round(nivelIdeal, 2),
        "recomendados": recomendados,
        "camadas_implementadas": {
            "fuzzy": FUZZY_PRONTO,
            "ga": GA_PRONTO,
        },
    }


def salvar_historico(aluno: Aluno, caminho: str = CAMINHO_HISTORICO) -> None:
    """Grava o estado do aluno em JSON."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(aluno.to_dict(), f, ensure_ascii=False, indent=2)

# Demo de terminal — usada na apresentacao do trabalho
FEEDBACKS_SIMULADOS = [
    "Nao entendi nada, to completamente perdido",
    "Foi ok, deu pra fazer com algum esforco",
    "Mandei muito bem, achei facil demais",
    "Travei na parte mais dificil, demorei demais",
    "Resolvi tranquilo, gostei do exercicio",
    "Achei meio chato mas consegui terminar",
    "Foi razoavel, precisei pensar bastante",
    "Que dificil, errei tudo de novo",
    "Mandei rapido, foi tranquilo",
]


def demo_sessao(n_iteracoes: int = 10, seed: int | None = 42) -> Aluno:
    """Roda uma simulacao no terminal exercitando o pipeline completo."""
    if seed is not None:
        random.seed(seed)

    pool = carregar_exercicios()
    aluno = Aluno("Alice")

    print("=" * 64)
    print(f"  DEMO ADAPTIVELEARN — aluno: {aluno.nome}")
    print(f"  Pool: {len(pool)} exercicios")
    print(
        f"  Fuzzy: {'OK' if FUZZY_PRONTO else 'STUB'}   "
        f"GA: {'OK' if GA_PRONTO else 'STUB'}"
    )
    print("=" * 64)

    proximos = random.sample(pool, min(n_iteracoes, len(pool)))

    for i, exercicio in enumerate(proximos, 1):
        print(f"\n----- Iteracao {i}/{n_iteracoes} -----")
        print(f"Exercicio {exercicio['id']}: {exercicio['titulo']}")
        print(
            f"Topico: {exercicio['topico']}/{exercicio['subtopico']}  "
            f"Dificuldade: {exercicio['dificuldade']}"
        )

        acertou = random.choice([True, False])
        tempo_gasto = random.randint(3, 20)
        feedback = random.choice(FEEDBACKS_SIMULADOS)

        resultado = processar_resposta(
            aluno=aluno,
            exercicio=exercicio,
            feedback=feedback,
            acertou=acertou,
            tempo_gasto=tempo_gasto,
            pool_exercicios=pool,
        )

        print(f"Feedback do aluno: '{feedback}'")
        print(f"Acertou? {acertou}    Tempo: {tempo_gasto} min")
        print(
            f"[I]   sentimento={resultado['classe_sentimento']:10s} "
            f"conf_confiante={resultado['prob_confiante']:.2f}"
        )
        print(
            f"[II]  nivelIdeal={resultado['nivelIdeal']:.2f}  "
            f"(taxa_movel={resultado['taxa_acerto_movel']:.2f})"
        )
        print(f"[III] top recomendados:")
        for ex in resultado["recomendados"][:3]:
            print(
                f"      - id={ex['id']:3d} dif={ex['dificuldade']} "
                f"{ex['topico']}/{ex['subtopico']}"
            )

    aluno.resumo()
    salvar_historico(aluno)
    print(f"\nHistorico salvo em: {CAMINHO_HISTORICO}")
    return aluno


if __name__ == "__main__":
    demo_sessao()
