"""
Modelo de estado do aluno (Camada de dominio).

Mantem historico de respostas, calcula metricas (taxa de acerto cumulativa
e movel, tempo medio) e oferece serializacao to_dict/from_dict para que
o futuro endpoint FastAPI possa persistir o estado entre requisicoes.
"""

from __future__ import annotations

from typing import Any


class Aluno:
    def __init__(self, nome: str):
        self.nome = nome
        self.historico: list[dict] = []
        self.acertos = 0
        self.erros = 0

    # -- registro de respostas ------------------------------------------------
    def registrar_resposta(
        self,
        exercicio: dict | int,
        acertou: bool,
        tempo: int,
        feedback: str,
    ) -> None:
        """
        Registra uma resposta no historico.

        Aceita tanto o dict completo do exercicio (legado) quanto so o id.
        Internamente normaliza para guardar id + dificuldade (suficiente
        para metricas e serializacao limpa).
        """
        if isinstance(exercicio, dict):
            exercicio_id = int(exercicio.get("id", -1))
            dificuldade = int(exercicio.get("dificuldade", 0))
        else:
            exercicio_id = int(exercicio)
            dificuldade = 0

        self.historico.append(
            {
                "exercicio_id": exercicio_id,
                "dificuldade": dificuldade,
                "acertou": bool(acertou),
                "tempo": int(tempo),
                "feedback": str(feedback),
            }
        )

        if acertou:
            self.acertos += 1
        else:
            self.erros += 1

    # -- metricas -------------------------------------------------------------
    def taxa_acerto(self) -> float:
        """Taxa de acerto cumulativa da sessao inteira."""
        total = self.acertos + self.erros
        if total == 0:
            return 0.0
        return round(self.acertos / total, 2)

    def taxa_acerto_movel(self, janela: int = 5) -> float:
        """
        Taxa de acerto considerando apenas as ultimas N respostas.
        E o sinal preferido para entrar na Camada II (Fuzzy), porque
        reflete a tendencia recente em vez da media da sessao toda.
        """
        if not self.historico:
            return 0.0
        ultimas = self.historico[-janela:]
        acertos_recentes = sum(1 for h in ultimas if h["acertou"])
        return round(acertos_recentes / len(ultimas), 2)

    def tempo_medio(self) -> float:
        if not self.historico:
            return 0.0
        tempos = [h["tempo"] for h in self.historico]
        return round(sum(tempos) / len(tempos), 2)

    # -- serializacao (preparacao para a FastAPI) -----------------------------
    def to_dict(self) -> dict[str, Any]:
        """Estado serializavel — pronto para JSON."""
        return {
            "nome": self.nome,
            "acertos": self.acertos,
            "erros": self.erros,
            "historico": list(self.historico),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Aluno":
        """Reconstroi um Aluno a partir do dict produzido por to_dict()."""
        a = cls(str(data.get("nome", "")))
        a.acertos = int(data.get("acertos", 0))
        a.erros = int(data.get("erros", 0))
        a.historico = list(data.get("historico", []))
        return a

    # -- exibicao no terminal -------------------------------------------------
    def resumo(self) -> None:
        print("\n===== RESUMO DO ALUNO =====")
        print(f"Nome: {self.nome}")
        print(f"Acertos: {self.acertos}")
        print(f"Erros: {self.erros}")
        print(f"Taxa de acerto (cumulativa): {self.taxa_acerto() * 100:.0f}%")
        print(f"Taxa de acerto (ultimas 5):  {self.taxa_acerto_movel() * 100:.0f}%")
        print(f"Tempo medio: {self.tempo_medio()} min")
