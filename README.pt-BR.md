# 📈 Stock Analysis

[🇺🇸 English](README.md) | 🇧🇷 Português

Ferramenta em Python que analisa ações da bolsa de valores combinando **análise técnica**, **análise fundamentalista** e **sentimento de notícias**, com o objetivo de apoiar a decisão de compra, venda ou espera sobre um ativo.

O usuário informa o ticker de uma ação (ex: `AAPL`, `PETR4.SA`) e o programa coleta os dados, calcula os indicadores relevantes, e apresenta um relatório consolidado com uma recomendação (Strong Buy, Buy, Hold, Sell ou Strong Sell) baseada em um sistema de pontuação.

> 🚧 **Status: projeto em desenvolvimento ativo.** O fluxo principal (coleta → análise → recomendação) já está funcional. Refinamentos de tratamento de erro, testes com múltiplos tickers e melhorias na interpretação de sentimento seguem em andamento.

---

## ✅ Funcionalidades implementadas

**Análise técnica** (dados de preço via [yfinance](https://pypi.org/project/yfinance/))
- Coleta de histórico de preços com período configurável (`1d`, `1wk`, `1mo`, `6mo`, `1y`, etc.)
- Média Móvel (20 e 50 dias) — identifica tendências de curto e longo prazo
- Bandas de Bollinger — identifica volatilidade e possíveis extremos de preço
- RSI (Relative Strength Index) — identifica sobrecompra/sobrevenda
- MACD (Moving Average Convergence Divergence) — identifica momentum de alta ou baixa

**Análise fundamentalista**
- P/L, ROE, Dívida/Patrimônio, Dividend Yield, Margem de Lucro, Crescimento de Receita, Free Cash Flow e Beta, extraídos via `yfinance`

**Análise contextual**
- Preço-alvo médio de analistas de mercado, comparado ao preço atual

**Análise de sentimento**
- Coleta de notícias recentes sobre o ativo
- Análise de sentimento de cada notícia com [NLTK VADER](https://www.nltk.org/api/nltk.sentiment.vader.html)
- Cálculo de sentimento médio consolidado

**Motor de decisão**
- Sistema de pontuação que combina todos os sinais acima (técnicos, fundamentalistas, contextuais e sentimento)
- Tradução do score final em uma recomendação (Strong Buy / Buy / Hold / Sell / Strong Sell)

**Interface web**
- Aplicação interativa com [Streamlit](https://streamlit.io/), incluindo gráfico de preço com médias móveis e Bandas de Bollinger sobrepostas ([Plotly](https://plotly.com/python/))

## 🚧 Roadmap (próximas etapas)

- [x] Tratamento de dados ausentes (ex: `pe_ratio` e `debt_to_equity` indisponíveis para alguns tickers)
- [x] Testes com maior variedade de tickers (B3 e mercado americano)
- [x] Interface web com [Streamlit](https://streamlit.io/), incluindo gráfico de preço interativo
- [x] Indicadores adicionais: Bandas de Bollinger, Revenue Growth, Free Cash Flow, Beta, preço-alvo de analistas
- [ ] Comparação do P/L e outros múltiplos com a média do setor/índice
- [ ] Melhorar a formatação e explicação da recomendação final (justificativa por indicador)
- [ ] Explorar alternativas ao VADER para textos financeiros (ex: FinBERT), já que o VADER foi treinado em linguagem coloquial e pode interpretar mal jargão de mercado

## 🛠️ Tecnologias

- **Python 3.14**
- [yfinance](https://pypi.org/project/yfinance/) — coleta de dados de mercado (preço, fundamentos, notícias)
- [pandas](https://pandas.pydata.org/) — manipulação e análise de séries históricas
- [NLTK (VADER)](https://www.nltk.org/) — análise de sentimento de notícias
- [Streamlit](https://streamlit.io/) — interface web interativa
- [Plotly](https://plotly.com/python/) — gráfico de preço interativo

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

# Baixe os dados necessários do NLTK (rodar uma única vez)
python -c "import nltk; nltk.download('vader_lexicon')"

# Execute a versão de linha de comando
python main.py

# Ou execute a versão web (interativa, com gráfico)
streamlit run app.py
```

Na versão de linha de comando, o programa pede o ticker da ação no terminal. Na versão web, um campo de texto na página permite digitar o ticker (ex: `PETR4.SA` para ações brasileiras, `AAPL` para ações americanas) e clicar em "Analyze" para ver o relatório completo, incluindo o gráfico de preço com médias móveis e Bandas de Bollinger.

## 🧠 Como funciona a recomendação

Cada um dos seguintes critérios soma ou subtrai pontos de um score:

| Critério | Condição | Pontos |
|---|---|---|
| Preço vs Média Móvel (20 e 50) | Preço acima da média | +1 cada |
| RSI | < 30 (sobrevendida) / > 70 (sobrecomprada) | +1 / -1 |
| Bandas de Bollinger | preço abaixo da banda inferior / acima da superior | +1 / -1 |
| P/L | < 15 (barata) / > 25 (cara) | +1 / -1 |
| Dívida/Patrimônio | < 50 (saudável) / > 100 (alavancagem alta) | +1 / -1 |
| Crescimento de Receita | > 10% / negativo | +1 / -1 |
| Free Cash Flow | positivo / negativo | +1 / -1 |
| Preço-alvo de analistas | upside > 10% / downside > 10% | +1 / -1 |
| MACD vs Signal | MACD acima / abaixo da Signal | +1 / -1 |
| Sentimento médio das notícias | positivo / negativo | +1 / -1 |

O score final é traduzido em uma recomendação: **Strong Buy**, **Buy**, **Hold**, **Sell** ou **Strong Sell**.

> Esse sistema é uma simplificação didática para fins de estudo e portfólio — não deve ser usado como única base para decisões reais de investimento.

### ⚠️ Limitações conhecidas

Nenhum sistema de pontuação simples como este substitui o julgamento de um analista humano. Alguns exemplos concretos encontrados durante os testes:

- **P/L muito baixo nem sempre significa "barata"** — pode ser resultado de um lucro atípico/não recorrente em um único trimestre, distorcendo o indicador. O sistema atual não diferencia lucro recorrente de eventos pontuais.
- **O motor não tem memória de contexto histórico** — não sabe se a empresa já passou por crises recentes, mudanças de gestão ou eventos relevantes que um investidor experiente levaria em conta.
- **VADER (análise de sentimento) foi treinado em linguagem coloquial**, não em jargão financeiro — títulos como "Earnings Call Highlights" podem ser classificados incorretamente como neutros ou negativos, mesmo quando o conteúdo é positivo.
- **Os critérios e faixas de pontuação são arbitrários** (definidos por mim, com base em regras gerais de mercado) — não são validados estatisticamente contra desempenho histórico real.

Por isso, a recomendação gerada deve ser tratada como um **ponto de partida para investigação**, não como uma conclusão definitiva.

## 📚 Motivação

Este projeto foi criado como forma de praticar Python aplicado a um problema real, unindo lógica de programação, manipulação de dados financeiros e conceitos de análise de investimentos, como parte de uma transição de carreira da área de Administração para Tecnologia.

## 📄 Licença

Este projeto está sob a licença MIT — sinta-se livre para usar, estudar e adaptar.
