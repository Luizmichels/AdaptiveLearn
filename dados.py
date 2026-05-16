import os
import pandas as pd


DIR_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV_PADRAO = os.path.join(DIR_BASE, "data", "exercicios.csv")


def _gerar_titulo(enunciado: str, max_chars: int = 60) -> str:
    """Extrai um titulo curto a partir do enunciado."""
    e = str(enunciado).strip().strip('"').strip("'")
    if not e:
        return "(sem titulo)"
    if len(e) <= max_chars:
        return e
    # corta na primeira pontuacao razoavel, senao trunca
    for sep in (". ", "? ", "! ", ", "):
        if sep in e[:max_chars]:
            return e.split(sep)[0]
    return e[:max_chars].rstrip() + "..."


def carregar_exercicios(caminho: str = CAMINHO_CSV_PADRAO) -> list[dict]:
    df = pd.read_csv(caminho)

    exercicios = []
    for _, row in df.iterrows():
        enunciado = str(row["enunciado"]).strip().strip('"').strip("'")
        exercicios.append(
            {
                "id": int(row["id"]),
                "titulo": _gerar_titulo(enunciado),
                "topico": str(row["topico"]),
                "subtopico": str(row["subtopico"]),
                "dificuldade": int(row["dificuldade"]),
                "tempo_min": int(row["tempo_estimado"]),
                "enunciado": enunciado,
            }
        )

    return exercicios


def estatisticas_pool(exercicios: list[dict]) -> dict:
    """Resumo rapido do pool — util para sanity check e para a demo."""
    if not exercicios:
        return {"total": 0}
    dificuldades = [e["dificuldade"] for e in exercicios]
    topicos: dict[str, int] = {}
    for e in exercicios:
        topicos[e["topico"]] = topicos.get(e["topico"], 0) + 1
    return {
        "total": len(exercicios),
        "dificuldade_min": min(dificuldades),
        "dificuldade_max": max(dificuldades),
        "topicos": topicos,
    }


if __name__ == "__main__":
    pool = carregar_exercicios()
    print(f"Pool carregado: {len(pool)} exercicios")
    print(f"Primeiro: {pool[0]}")
    print(f"\nEstatisticas:")
    stats = estatisticas_pool(pool)
    for k, v in stats.items():
        print(f"  {k}: {v}")
