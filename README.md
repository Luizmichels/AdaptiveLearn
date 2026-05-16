# Alunos
 - André Luiz Michels da Silva
 - Gustava Antonio da Costa Pereira
 - Luiz Felipe
 - Maria Eduarda
 - Rebeca Clara

## Estrutura dos arquivos

```
AdaptiveLearn/
├── pln_nb.py                    # módulo principal (API pública)
├── treinar_modelo.py            # script de treino + avaliação
├── testar_pln.py                # teste interativo (demo)
├── requirements_pessoa_a.txt    # dependências
├── data/
│   └── feedbacks_treino.csv     # 213 frases rotuladas (71 por classe)
└── models/
    ├── pln_nb.joblib            # modelo treinado (gerado pelo treino)
    ├── relatorio_avaliacao.txt  # métricas (gerado pelo treino)
    └── matriz_confusao.png      # matriz de confusão (gerado pelo treino)
```

## Setup (primeira vez)

# 1. Instala dependências
python -m pip install -r dependencias.txt

# 2. Baixa recursos do NLTK (faz uma vez só, ~10MB)
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('rslp')"

# 3. Treina o modelo (gera pln_nb.joblib em models/)
python treinar_modelo.py

# 4. Demo interativa
python testar_pln.py 