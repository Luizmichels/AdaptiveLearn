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

    # validação cruzada 5-fold para robustez 
    cv_scores = cross_val_score(
        construir_pipeline(),
        textos,
        classes,
        cv=5,
        scoring="f1_macro",
    )

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
