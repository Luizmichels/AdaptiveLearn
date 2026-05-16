"""
Classifica feedbacks textuais de alunos em três classes:
- frustrado: aluno teve dificuldade significativa
- neutro:    aluno teve desempenho mediano
- confiante: aluno dominou o exercício

Pré-processamento: tokenização, remoção de stopwords PT-BR, stemming (RSLP).
Vetorização: TF-IDF.
Modelo: Multinomial Naive Bayes.
"""

from __future__ import annotations

import os
import re
import unicodedata
from typing import Optional

import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Setup do NLTK (baixa recursos na primeira execução)
def _setup_nltk() -> None:
    # Garante que os recursos do NLTK estejam disponíveis."""
    recursos = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("stemmers/rslp", "rslp"),
    ]
    for caminho, nome in recursos:
        try:
            nltk.data.find(caminho)
        except LookupError:
            nltk.download(nome, quiet=True)


_setup_nltk()

# Pré-processamento
_STEMMER = RSLPStemmer()
_STOPWORDS = set(stopwords.words("portuguese"))

# Removemos algumas stopwords úteis para sentimento (negações principalmente).
_STOPWORDS_PRESERVADAS = {"não", "nem", "nunca", "jamais", "nada"}
_STOPWORDS = _STOPWORDS - _STOPWORDS_PRESERVADAS

def _remover_acentos(texto: str) -> str:
    """Remove acentos para reduzir variações lexicais."""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def preprocessar(texto: str) -> str:
    """
    Pipeline de pré-processamento para um único feedback.

    Etapas:
    1. Lowercase
    2. Remoção de pontuação e números
    3. Tokenização
    4. Remoção de stopwords (preservando negações)
    5. Stemming RSLP

    Retorna o texto pré-processado como string única).
    """
    if not isinstance(texto, str) or not texto.strip():
        return ""

    # lowercase
    texto = texto.lower()

    # remove pontuação, números e caracteres especiais
    texto = re.sub(r"[^a-záàâãéèêíïóôõöúçñ\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    # tokenização
    try:
        tokens = word_tokenize(texto, language="portuguese")
    except LookupError:
        # fallback se punkt_tab não estiver disponível
        tokens = texto.split()

    # stopwords (mantém negações)
    tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 1]

    # stemming
    tokens = [_STEMMER.stem(t) for t in tokens]

    return " ".join(tokens)

# Classificador
CAMINHO_MODELO_PADRAO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "models", "pln_nb.joblib"
)

def construir_pipeline() -> Pipeline:
    # Constrói o pipeline TF-IDF + Naive Bayes.
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    preprocessor=preprocessar,
                    tokenizer=str.split,
                    token_pattern=None,
                    ngram_range=(1, 2),
                    min_df=2,
                    sublinear_tf=True,
                ),
            ),
            ("nb", MultinomialNB(alpha=0.5)),
        ]
    )

# Rota para as outras camadas
_modelo_carregado: Optional[Pipeline] = None


def carregar_modelo(caminho: str = CAMINHO_MODELO_PADRAO) -> Pipeline:
    """Carrega o modelo treinado do disco (cache em memória)."""
    global _modelo_carregado
    if _modelo_carregado is None:
        if not os.path.exists(caminho):
            raise FileNotFoundError(
                f"Modelo não encontrado em {caminho}. "
                "Rode 'python treinar_modelo.py' antes de usar."
            )
        _modelo_carregado = joblib.load(caminho)
    return _modelo_carregado


def classificar(texto: str) -> tuple[str, float]:
    """
    Interface principal consumida pela Camada II (Fuzzy).
    Exemplo:
    classificar("Resolvi tranquilo, gostei do exercício")
    ('confiante', 0.87)
    """
    modelo = carregar_modelo()
    classe = modelo.predict([texto])[0]
    probs = modelo.predict_proba([texto])[0]
    classes = modelo.classes_
    prob_confiante = float(probs[list(classes).index("confiante")])
    return classe, prob_confiante


def classificar_lote(textos: list[str]) -> list[tuple[str, float]]:
    """Versão batch de `classificar` (útil para avaliação)."""
    modelo = carregar_modelo()
    classes_preditas = modelo.predict(textos)
    probs = modelo.predict_proba(textos)
    idx_confiante = list(modelo.classes_).index("confiante")
    return [
        (str(c), float(p[idx_confiante]))
        for c, p in zip(classes_preditas, probs)
    ]


if __name__ == "__main__":
    # Teste rápido se rodar o módulo diretamente
    exemplos = [
        "Não entendi nada, muito difícil",
        "Foi ok, deu pra fazer",
        "Mandei super bem, achei fácil",
    ]
    for t in exemplos:
        try:
            c, p = classificar(t)
            print(f"[{c:10s}] (conf={p:.3f}) {t}")
        except FileNotFoundError as e:
            print(e)
            break
