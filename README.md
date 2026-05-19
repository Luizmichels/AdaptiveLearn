# AdaptiveLearn — Backend

Backend do sistema AdaptiveLearn desenvolvido em Python utilizando FastAPI, PLN, Sistema Fuzzy e Algoritmo Genético para recomendação adaptativa de exercícios.

---

# Integrantes

- André Luiz Michels da Silva
- Gustavo Antonio da Costa Pereira
- Luiz Felipe Schroder Marcon
- Maria Eduarda Nunes de Souza
- Rebeca Lara de Souza

---

# Tecnologias Utilizadas

- Python
- FastAPI
- NLTK
- Scikit-Learn
- Scikit-Fuzzy
- NumPy
- Joblib

---

# Estrutura do Projeto

```txt
AdaptiveLearn/
│
├── data/
│   └── feedbacks_treino.csv
│
├── docs/
│   └── prints/
│
├── models/
│   ├── pln_nb.joblib
│   ├── relatorio_avaliacao.txt
│   └── matriz_confusao.png
│
├── outputs/
│   ├── fitness_ga.png
│   ├── evolucao_dificuldade.png
│   └── taxa_acerto_sessao.png
│
├── aluno.py
├── dados.py
├── fuzzy.py
├── ga.py
├── main.py
├── pln_nb.py
├── treinar_modelo.py
├── testar_pln.py
├── utils.py
│
├── dependencias.txt
├── relatorio.md
└── README.md
```

### Principais componentes

- `pln_nb.py` → classificação de sentimentos utilizando PLN
- `fuzzy.py` → cálculo do nível ideal com lógica fuzzy
- `ga.py` → recomendação adaptativa utilizando Algoritmo Genético
- `main.py` → integração geral e API FastAPI
- `utils.py` → geração de gráficos e visualizações
- `models/` → arquivos treinados e métricas do PLN
- `outputs/` → gráficos gerados durante as execuções
- `docs/prints/` → capturas de tela da demonstração do sistema

---

# Funcionalidades

- Classificação de sentimentos utilizando PLN
- Sistema Fuzzy para definição de dificuldade
- Recomendação adaptativa de exercícios
- Integração com frontend em Next.js
- API REST utilizando FastAPI

---

# Como Executar o Projeto

> Todos os comandos abaixo devem ser executados no terminal PowerShell.

---

## 1. Clonar o repositório

```powershell
git clone LINK_DO_REPOSITORIO
```

---

## 2. Entrar na pasta do projeto

```powershell
cd AdaptiveLearn
```

---

## 3. Criar ambiente virtual

```powershell
python -m venv .venv
```

---

## 4. Ativar ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Se aparecer `(.venv)` no início do terminal, significa que funcionou.

Exemplo:

```powershell
(.venv) PS C:\Users\Usuario\AdaptiveLearn>
```

---

## 5. Instalar dependências

```powershell
python -m pip install -r dependencias.txt
```

---

## 6. Baixar recursos do NLTK

```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('rslp')"
```

---

## 7. Iniciar o backend

```powershell
uvicorn main:app --reload
```

---

## Outros comandos

## 1. Treinar o modelo PLN

Este comando gera:
- `pln_nb.joblib`
- `relatorio_avaliacao.txt`
- `matriz_confusao.png`

```powershell
python treinar_modelo.py
```

---

## 2. Executar demo interativa do PLN

```powershell
python testar_pln.py
```

---

# Endpoint Principal

```http
GET /nivel?acertos=8&tempo=20
```

## Exemplo de resposta

```json
{
  "nivel": 8.14,
  "acertos": 8,
  "tempo": 20
}
```

---

# Integração com Frontend

O backend se comunica com o frontend através de requisições HTTP utilizando FastAPI.

O frontend do sistema está disponível em:

[PyEvolve Frontend](https://github.com/Madu3304/PyEvolve-FrontEnd.git)

Exemplo de chamada no frontend:

```ts
fetch("http://127.0.0.1:8000/nivel?acertos=8&tempo=20")
```

---

# Objetivo do Projeto

O projeto tem como objetivo criar uma plataforma de aprendizagem adaptativa capaz de ajustar dinamicamente a dificuldade dos exercícios com base no desempenho e feedback do aluno.