"""
Script de treino e avaliação do modelo.

Uso:
    python treinar_modelo.py

Saídas:
    - models/pln_nb.joblib            : modelo serializado
    - models/relatorio_avaliacao.txt  : métricas (precisão, recall, F1)
    - models/matriz_confusao.png      : matriz de confusão visual
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score,
)
from pln_nb import construir_pipeline

DIR_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DATASET = os.path.join(DIR_BASE, "data", "feedbacks_treino.csv")
DIR_MODELOS = os.path.join(DIR_BASE, "models")
CAMINHO_MODELO = os.path.join(DIR_MODELOS, "pln_nb.joblib")
CAMINHO_RELATORIO = os.path.join(DIR_MODELOS, "relatorio_avaliacao.txt")
CAMINHO_MATRIZ = os.path.join(DIR_MODELOS, "matriz_confusao.png")

SEED = 42

def carregar_dataset(caminho: str) -> tuple[list[str], list[str]]:
    df = pd.read_csv(caminho)
    print(f"Dataset carregado: {len(df)} amostras")
    print(f"Distribuição:\n{df['classe'].value_counts().to_string()}\n")
    return df["texto"].tolist(), df["classe"].tolist()

def treinar_e_avaliar() -> None:
    os.makedirs(DIR_MODELOS, exist_ok=True)

    textos, classes = carregar_dataset(CAMINHO_DATASET)

    # split estratificado 80/20
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        textos,
        classes,
        test_size=0.20,
        stratify=classes,
        random_state=SEED,
    )
    print(f"Treino: {len(X_treino)} | Teste: {len(X_teste)}\n")

    # constrói e treina
    modelo = construir_pipeline()
    modelo.fit(X_treino, y_treino)

    # avaliação no conjunto de teste
    y_pred = modelo.predict(X_teste)
    acc = accuracy_score(y_teste, y_pred)

    relatorio = classification_report(
        y_teste,
        y_pred,
        digits=3,
        zero_division=0,
    )

    # validação cruzada 5-fold
    cv_scores = cross_val_score(
        construir_pipeline(),
        textos,
        classes,
        cv=5,
        scoring="f1_macro",
    )

    # salva relatório de avaliação
    with open(CAMINHO_RELATORIO, "w", encoding="utf-8") as arquivo:
        arquivo.write("RELATÓRIO DE AVALIAÇÃO DO MODELO PLN\n")
        arquivo.write("=" * 45 + "\n\n")
        arquivo.write(f"Quantidade total de amostras: {len(textos)}\n")
        arquivo.write(f"Quantidade de treino: {len(X_treino)}\n")
        arquivo.write(f"Quantidade de teste: {len(X_teste)}\n\n")

        arquivo.write(f"Acurácia no conjunto de teste: {acc:.3f}\n\n")

        arquivo.write("Relatório de classificação:\n")
        arquivo.write(relatorio)

        arquivo.write("\nValidação cruzada 5-fold usando F1 macro:\n")
        arquivo.write(f"Scores: {np.round(cv_scores, 3)}\n")
        arquivo.write(f"Média: {cv_scores.mean():.3f}\n")
        arquivo.write(f"Desvio padrão: {cv_scores.std():.3f}\n")

    print(f"Relatório salvo em: {CAMINHO_RELATORIO}")

    # gera e salva matriz de confusão
    matriz = confusion_matrix(y_teste, y_pred, labels=modelo.classes_)

    disp = ConfusionMatrixDisplay(
        confusion_matrix=matriz,
        display_labels=modelo.classes_
    )

    disp.plot(cmap="Blues", values_format="d")
    plt.title("Matriz de Confusão - Naive Bayes")
    plt.tight_layout()
    plt.savefig(CAMINHO_MATRIZ, dpi=300)
    plt.close()

    print(f"Matriz de confusão salva em: {CAMINHO_MATRIZ}")

    # treina o modelo final com TODOS os dados e salva
    modelo_final = construir_pipeline()
    modelo_final.fit(textos, classes)
    joblib.dump(modelo_final, CAMINHO_MODELO)

    print(f"Modelo final salvo em: {CAMINHO_MODELO}\n")

if __name__ == "__main__":
    try:
        treinar_e_avaliar()
    except FileNotFoundError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
