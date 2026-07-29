# 📈 Stock Analysis

Ferramenta em Python que analisa ações da bolsa de valores combinando **análise técnica**, **análise fundamentalista** e **sentimento de notícias**, com o objetivo de apoiar a decisão de compra, venda ou espera sobre um ativo.

O usuário informa o ticker de uma ação (ex: `AAPL`, `PETR4.SA`) e o programa calcula indicadores relevantes, interpreta os resultados e apresenta uma leitura consolidada do cenário atual daquele ativo.

> ⚠️ **Status: projeto em desenvolvimento ativo.** As funcionalidades abaixo estão sendo construídas e documentadas conforme avançam. Este README é atualizado a cada etapa concluída.

---

## ✅ Funcionalidades já implementadas

- **Coleta de dados históricos de preço** via [yfinance](https://pypi.org/project/yfinance/), com período configurável (`1d`, `1wk`, `1mo`, `6mo`, `1y`, etc.)
- **Média Móvel (Moving Average)** — suaviza o preço para identificar tendências de curto e longo prazo
- **RSI (Relative Strength Index)** — identifica se um ativo está tecnicamente sobrecomprado ou sobrevendido

## 🚧 Roadmap (próximas etapas)

- [ ] MACD (Moving Average Convergence Divergence)
- [ ] Coleta de dados fundamentalistas (P/L, ROE, dívida, dividend yield)
- [ ] Coleta e análise de sentimento de notícias recentes sobre o ativo
- [ ] Motor de decisão que combina os sinais técnicos, fundamentalistas e de sentimento
- [ ] Relatório final consolidado (texto e/ou visual) com recomendação e justificativa

## 🛠️ Tecnologias

- **Python 3.14**
- [yfinance](https://pypi.org/project/yfinance/) — coleta de dados de mercado
- [pandas](https://pandas.pydata.org/) — manipulação e análise de dados

## 🚀 Como rodar o projeto

```bash
# Clone o repositório
git clone https://github.com/eduardoruspoli/stock-analysis.git
cd stock-analysis

# Crie e ative um ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Instale as dependências
pip install -r requirements.txt

# Execute
python main.py
```

Ao rodar, o programa vai pedir o ticker da ação que você deseja analisar (ex: `PETR4.SA` para ações brasileiras, `AAPL` para ações americanas).

## 📚 Motivação

Este projeto foi criado como forma de praticar Python aplicado a um problema real, unindo lógica de programação, manipulação de dados financeiros e conceitos de análise de investimentos.

## 📄 Licença

Este projeto está sob a licença MIT — sinta-se livre para usar, estudar e adaptar.
