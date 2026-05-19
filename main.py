from __future__ import annotations

import json
import os
import random

import matplotlib.pyplot as plt
import numpy as np

from aluno import Aluno
from dados import carregar_exercicios
from pln_nb import classificar
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FeedbackRequest(BaseModel):
    feedback: str
    isCorrect: bool
    timeSpent: int

@app.post("/feedback")
def receber_feedback(dados: FeedbackRequest):

    classe_sentimento, probabilidade = classificar(dados.feedback)

    return {
        "mensagem": "Feedback recebido com sucesso",
        "feedback": dados.feedback,
        "sentimento": classe_sentimento,
        "confianca": round(probabilidade, 3),
        "acertou": dados.isCorrect,
        "tempo": dados.timeSpent
    }

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
def _plot_fuzzy_pertinencias(
    valorSentimento: float,
    taxa: float,
    tempo: float,
    nivelIdeal: float,
    iteracao: int,
) -> None:
    """Plota as funcoes de pertinencia das 4 variaveis fuzzy da iteracao."""
    import skfuzzy as fuzz

    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    fig.suptitle(f"Funcoes de Pertinencia Fuzzy — Iteracao {iteracao}", fontsize=13)

    x_s = np.arange(0, 11, 0.1)
    axes[0, 0].plot(x_s, fuzz.trimf(x_s, [0, 0, 5]),   "r-", label="frustrado")
    axes[0, 0].plot(x_s, fuzz.trimf(x_s, [2, 5, 8]),   "b-", label="neutro")
    axes[0, 0].plot(x_s, fuzz.trimf(x_s, [5, 10, 10]), "g-", label="confiante")
    axes[0, 0].axvline(valorSentimento, color="k", linestyle="--", linewidth=1.5,
                       label=f"entrada={valorSentimento:.1f}")
    axes[0, 0].set_title("Sentimento")
    axes[0, 0].set_ylabel("Pertinencia")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].set_ylim(-0.05, 1.1)

    x_t = np.arange(0, 101, 0.5)
    axes[0, 1].plot(x_t, fuzz.trimf(x_t, [0, 0, 50]),    "r-", label="baixa")
    axes[0, 1].plot(x_t, fuzz.trimf(x_t, [25, 50, 75]),  "b-", label="media")
    axes[0, 1].plot(x_t, fuzz.trimf(x_t, [50, 100, 100]),"g-", label="alta")
    axes[0, 1].axvline(taxa, color="k", linestyle="--", linewidth=1.5,
                       label=f"entrada={taxa:.1f}%")
    axes[0, 1].set_title("Taxa de Acerto (%)")
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].set_ylim(-0.05, 1.1)

    x_g = np.arange(0, 61, 0.3)
    axes[1, 0].plot(x_g, fuzz.trimf(x_g, [0, 0, 20]),  "r-", label="rapido")
    axes[1, 0].plot(x_g, fuzz.trimf(x_g, [10, 30, 50]),"b-", label="medio")
    axes[1, 0].plot(x_g, fuzz.trimf(x_g, [40, 60, 60]),"g-", label="lento")
    axes[1, 0].axvline(tempo, color="k", linestyle="--", linewidth=1.5,
                       label=f"entrada={tempo:.0f} min")
    axes[1, 0].set_title("Tempo Gasto (min)")
    axes[1, 0].set_ylabel("Pertinencia")
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].set_ylim(-0.05, 1.1)

    x_n = np.arange(0, 11, 0.1)
    axes[1, 1].plot(x_n, fuzz.trimf(x_n, [0, 0, 5]),   "r-", label="facil")
    axes[1, 1].plot(x_n, fuzz.trimf(x_n, [2, 5, 8]),   "b-", label="medio")
    axes[1, 1].plot(x_n, fuzz.trimf(x_n, [5, 10, 10]), "g-", label="dificil")
    axes[1, 1].axvline(nivelIdeal, color="k", linestyle="--", linewidth=1.5,
                       label=f"saida={nivelIdeal:.2f}")
    axes[1, 1].set_title("Nivel Ideal (saida)")
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].set_ylim(-0.05, 1.1)

    plt.tight_layout()
    os.makedirs(os.path.join(DIR_BASE, "models"), exist_ok=True)
    caminho_fig = os.path.join(DIR_BASE, "models", f"fuzzy_iter_{iteracao:02d}.png")
    plt.savefig(caminho_fig, dpi=100)
    plt.show()
    plt.close()
    print(f"      [grafico salvo: {caminho_fig}]")


def _plot_evolucao_dificuldade(
    historico_niveis: list[float],
    historico_acertos: list[bool],
) -> None:
    """Grafico final: evolucao da dificuldade media recomendada na sessao."""
    from matplotlib.lines import Line2D

    iteracoes = list(range(1, len(historico_niveis) + 1))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(iteracoes, historico_niveis, "b-o", linewidth=2,
            markersize=6, label="Nivel ideal recomendado")

    for idx, (nivel, acertou) in enumerate(
        zip(historico_niveis, historico_acertos), start=1
    ):
        if acertou:
            ax.plot(idx, nivel, "g^", markersize=10, zorder=5)
        else:
            ax.plot(idx, nivel, "rx", markersize=10, markeredgewidth=2, zorder=5)

    if len(historico_niveis) >= 3:
        janela = 3
        movel = [
            sum(historico_niveis[max(0, j - janela):j]) / min(j, janela)
            for j in range(1, len(historico_niveis) + 1)
        ]
        ax.plot(iteracoes, movel, "b--", linewidth=1, alpha=0.5,
                label="Tendencia (media movel)")

    extras = [
        Line2D([0], [0], marker="^", color="w", markerfacecolor="g",
               markersize=10, label="Acerto"),
        Line2D([0], [0], marker="x", color="r", markersize=10,
               markeredgewidth=2, label="Erro"),
    ]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + extras, fontsize=9)

    ax.set_title("Evolucao da Dificuldade Recomendada ao Longo da Sessao",
                 fontsize=13)
    ax.set_xlabel("Iteracao (exercicio resolvido)")
    ax.set_ylabel("Nivel Ideal (0–10)")
    ax.set_xticks(iteracoes)
    ax.set_ylim(0, 10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    caminho_fig = os.path.join(DIR_BASE, "models", "evolucao_dificuldade.png")
    plt.savefig(caminho_fig, dpi=120)
    plt.show()
    plt.close()
    print(f"\nGrafico de evolucao salvo em: {caminho_fig}")


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

    historico_niveis: list[float] = []
    historico_acertos: list[bool] = []

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

        historico_niveis.append(resultado["nivelIdeal"])
        historico_acertos.append(acertou)

        mapa_sentimento = {"frustrado": 0, "neutro": 5, "confiante": 10}
        valorSentimento = mapa_sentimento.get(resultado["classe_sentimento"], 5)

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
        if FUZZY_PRONTO:
            _plot_fuzzy_pertinencias(
                valorSentimento,
                resultado["taxa_acerto_movel"],
                tempo_gasto,
                resultado["nivelIdeal"],
                i,
            )
        cromossomo = [ex["id"] for ex in resultado["recomendados"]]
        print(f"[III] cromossomo vencedor: {cromossomo}")
        print(f"      top recomendados:")
        for ex in resultado["recomendados"][:3]:
            print(
                f"      - id={ex['id']:3d} dif={ex['dificuldade']} "
                f"{ex['topico']}/{ex['subtopico']}"
            )

    aluno.resumo()
    salvar_historico(aluno)
    print(f"\nHistorico salvo em: {CAMINHO_HISTORICO}")
    _plot_evolucao_dificuldade(historico_niveis, historico_acertos)
    return aluno


if __name__ == "__main__":
    demo_sessao()