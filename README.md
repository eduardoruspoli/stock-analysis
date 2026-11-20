# 📈 Stock Analysis

[🇧🇷 Português](README.pt-BR.md) | 🇺🇸 English

A Python tool that analyzes stocks and REITs by combining **technical analysis**, **fundamental analysis**, and **news sentiment**, supporting buy/sell/hold decisions on a given asset across both **B3 (Brazil)** and **Global markets**[cite: 1, 7, 9].

The user enters a stock ticker (e.g. `AAPL`, `PETR4`, `B3SA3`, `MXRF11`), and the program collects the data, calculates the relevant indicators, and presents a consolidated report with a recommendation (`Strong Buy`, `Buy`, `Hold`, `Sell`, or `Strong Sell`) based on a scoring system[cite: 1, 7, 9].

> 🚧 **Status: active development.** The core pipeline (data collection → analysis → recommendation) is functional, and multi-provider routing (`brapi.dev` for B3 and `Financial Modeling Prep` for global tickers), SQLite persistence, and the Streamlit dashboard are active[cite: 7, 9]. Error handling refinements, automated tests, and sentiment analysis improvements are ongoing.

---

## ✅ Implemented features

**Technical analysis**
- Historical price collection with configurable window (`3mo` default for B3, recent history for global tickers)[cite: 1, 9]
- Moving Averages (20 and 50 periods) — identifies short- and long-term trends
- Bollinger Bands — identifies volatility and possible price extremes
- RSI (14) — identifies overbought/oversold conditions
- MACD & Signal line — identifies bullish or bearish momentum

**Fundamental analysis**
- P/E ratio, ROE, Debt/Equity, Market Cap, Dividend Yield, Profit Margin, Revenue Growth, Free Cash Flow, and Beta

**Contextual analysis**
- Average analyst target price, compared against the current price

**Sentiment analysis**
- Collection of recent news about the asset via Google News RSS (`pt-BR` for B3 and `en-US` for global tickers)[cite: 1, 7, 9]
- Sentiment analysis of each news item with [NLTK VADER](https://www.nltk.org/api/nltk.sentiment.vader.html)[cite: 1, 7]
- Calculation of consolidated average sentiment

**Decision engine**
- Scoring system that combines all the signals above (technical, fundamental, contextual, and sentiment)
- Translation of the final score into a recommendation (`Strong Buy` / `Buy` / `Hold` / `Sell` / `Strong Sell`)

**Web interface**
- Interactive app built with [Streamlit](https://streamlit.io/), including a price chart with moving averages and Bollinger Bands overlaid ([Plotly](https://plotly.com/python/))[cite: 2, 7]

---

## 🖥️ Dashboard and watchlist

- **Personal watchlist:** add or remove symbols, and open each stock’s detailed analysis from its card[cite: 2, 7].
- **Portfolio overview:** see latest available close, daily price movement, market badge (`B3` / `GLOBAL`), currency (`R$` / `$`), and a rule-based classification.
- **Interactive charts:** closing prices, 20/50-period moving averages, and Bollinger Bands in Plotly[cite: 2, 7].
- **Usability:** dark theme, responsive Streamlit layout, 30-minute staleness check (`STALE_AFTER_MINUTES = 30`), in-memory caching, and manual **Refresh all**[cite: 2, 7].
- **Local storage:** watchlist entries and snapshots are stored in SQLite (`stock_analysis.db`), with automatic migration from legacy `watchlist.json`[cite: 2, 4, 7].
- **API keys:** configured dynamically via environment variables, local `.env`, or the sidebar[cite: 2].
- **Two entry points:** `python main.py` for CLI and `streamlit run app.py` for the web dashboard[cite: 1, 2, 7].

> Market data from third-party APIs can be delayed and subject to free-tier limits[cite: 2, 7]. The classification is a didactic rules-based signal, **not investment advice**.

On Windows, after installing dependencies in the `venv` environment, you can also use `Stock Analysis.bat` to launch the app.

---

## 🚧 Roadmap (next steps)

- [x] Handling of missing data (e.g. `pe_ratio` and `debt_to_equity` unavailable for some tickers)
- [x] Testing with a wider variety of tickers (B3 and US/global market)[cite: 7, 9]
- [x] Web interface with [Streamlit](https://streamlit.io/), including an interactive price chart[cite: 2, 7]
- [x] Additional indicators: Bollinger Bands, Revenue Growth, Free Cash Flow, Beta, analyst target price
- [ ] Add automated tests, better validation of invalid tickers, and clear API error messages
- [ ] Compare P/E and other multiples against the sector/index average
- [ ] Improve the formatting and explanation of the final recommendation (per-indicator justification)
- [ ] Explore alternatives to VADER for financial text (e.g. FinBERT), since VADER was trained on colloquial language and can misjudge market jargon

---

## 🛠️ Tech stack

- **Python**
- [requests](https://pypi.org/project/requests/) — market and RSS data collection (`brapi.dev`, FMP, Google News RSS)[cite: 9]
- [pandas](https://pandas.pydata.org/) — historical series manipulation and analysis
- [NLTK (VADER)](https://www.nltk.org/) — news sentiment analysis
- [Streamlit](https://streamlit.io/) — interactive web interface[cite: 2, 7]
- [Plotly](https://plotly.com/python/) — interactive price chart[cite: 2, 7]
- **SQLite** — local watchlist and snapshot persistence[cite: 2, 4]

---

## 🚀 Running the project

```bash
# Clone the repository
git clone [https://github.com/eduardoruspoli/stock-analysis.git](https://github.com/eduardoruspoli/stock-analysis.git)
cd stock-analysis

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download the required NLTK data (run once)
python -c "import nltk; nltk.download('vader_lexicon')"

# Configure your API keys (.env, sidebar, or environment variables)
# BRAPI_TOKEN=your_brapi_token
# FMP_API_KEY=your_fmp_api_key

# Run the command-line version
python main.py

# Or run the web version (interactive, with chart)
streamlit run app.py

---

### 2. `README.pt-BR.md` (Português)

```markdown
# 📈 Stock Analysis

[🇺🇸 English](README.md) | 🇧🇷 Português

Ferramenta em Python que analisa ações e FIIs combinando **análise técnica**, **análise fundamentalista** e **sentimento de notícias**, com o objetivo de apoiar a decisão de compra, venda ou espera sobre um ativo na **B3** e no **mercado global**[cite: 8, 9].

O usuário informa o ticker de um ativo (ex: `AAPL`, `PETR4`, `B3SA3`, `MXRF11`) e o programa coleta os dados, calcula os indicadores relevantes e apresenta um relatório consolidado com uma recomendação (`Strong Buy`, `Buy`, `Hold`, `Sell` ou `Strong Sell`) baseada em um sistema de pontuação[cite: 8, 9].

> 🚧 **Status: projeto em desenvolvimento ativo.** O fluxo principal (coleta → análise → recomendação) já está funcional, com roteamento entre provedores (`brapi.dev` para B3 e `Financial Modeling Prep` para ativos globais), persistência em SQLite e dashboard em Streamlit[cite: 8, 9]. Refinamentos de tratamento de erro, testes com múltiplos tickers e melhorias na interpretação de sentimento seguem em andamento.

---

## ✅ Funcionalidades implementadas

**Análise técnica**
- Coleta de histórico de preços com período configurável (`3mo` por padrão na B3 e histórico recente para ativos globais)[cite: 8, 9]
- Média Móvel (20 e 50 dias) — identifica tendências de curto e longo prazo
- Bandas de Bollinger — identifica volatilidade e possíveis extremos de preço
- RSI (Relative Strength Index) — identifica sobrecompra/sobrevenda
- MACD (Moving Average Convergence Divergence) — identifica momentum de alta ou baixa

**Análise fundamentalista**
- P/L, ROE, Dívida/Patrimônio, Market Cap, Dividend Yield, Margem de Lucro, Crescimento de Receita, Free Cash Flow e Beta

**Análise contextual**
- Preço-alvo médio de analistas de mercado, comparado ao preço atual

**Análise de sentimento**
- Coleta de notícias recentes sobre o ativo via Google News RSS (`pt-BR` para B3 e `en-US` para ativos globais)[cite: 8, 9]
- Análise de sentimento de cada notícia com [NLTK VADER](https://www.nltk.org/api/nltk.sentiment.vader.html)
- Cálculo de sentimento médio consolidado

**Motor de decisão**
- Sistema de pontuação que combina todos os sinais acima (técnicos, fundamentalistas, contextuais e sentimento)
- Tradução do score final em uma recomendação (`Strong Buy` / `Buy` / `Hold` / `Sell` / `Strong Sell`)

**Interface web**
- Aplicação interativa com [Streamlit](https://streamlit.io/), incluindo gráfico de preço com médias móveis e Bandas de Bollinger sobrepostas ([Plotly](https://plotly.com/python/))[cite: 2, 8]

---

## 🖥️ Dashboard e watchlist

- **Lista de acompanhamento:** adicione ou remova tickers e abra a análise detalhada de cada ativo pelo cartão[cite: 2, 8].
- **Visão geral:** confira o último fechamento disponível, a variação diária, a etiqueta de mercado (`B3` / `GLOBAL`), a moeda (`R$` / `$`) e uma classificação calculada por regras.
- **Gráficos interativos:** fechamento, médias móveis de 20/50 períodos e Bandas de Bollinger via Plotly[cite: 2, 8].
- **Experiência:** tema escuro, layout adaptável em Streamlit, controle de atualização a cada 30 minutos (`STALE_AFTER_MINUTES = 30`), cache em memória e botão **Refresh all**[cite: 2, 8].
- **Persistência local:** watchlist e snapshots são salvos no banco SQLite (`stock_analysis.db`), com migração automática do legado `watchlist.json`[cite: 2, 4, 8].
- **Chaves de API:** leitura dinâmica via variáveis de ambiente, arquivo `.env` local ou barra lateral[cite: 2].
- **Duas formas de uso:** `python main.py` no terminal e `streamlit run app.py` na web[cite: 1, 2, 8].

> Os dados de mercado via APIs externas podem apresentar atraso e estão sujeitos aos limites dos planos gratuitos[cite: 2, 8]. A classificação é um sinal didático gerado por regras, **não uma recomendação de investimento**.

No Windows, depois de instalar as dependências no ambiente `venv`, também é possível iniciar o aplicativo por `Stock Analysis.bat`.

---

## 🚧 Roadmap (próximas etapas)

- [x] Tratamento de dados ausentes (ex: `pe_ratio` e `debt_to_equity` indisponíveis para alguns tickers)
- [x] Testes com maior variedade de tickers (B3 e mercado americano/global)[cite: 8, 9]
- [x] Interface web com [Streamlit](https://streamlit.io/), incluindo gráfico de preço interativo[cite: 2, 8]
- [x] Indicadores adicionais: Bandas de Bollinger, Revenue Growth, Free Cash Flow, Beta, preço-alvo de analistas
- [ ] Criar testes automatizados, validar tickers inválidos e melhorar as mensagens de erro da API
- [ ] Comparação do P/L e outros múltiplos com a média do setor/índice
- [ ] Melhorar a formatação e explicação da recomendação final (justificativa por indicador)
- [ ] Explorar alternativas ao VADER para textos financeiros (ex: FinBERT), já que o VADER foi treinado em linguagem coloquial e pode interpretar mal jargão de mercado

---

## 🛠️ Tecnologias

- **Python**
- [requests](https://pypi.org/project/requests/) — coleta de dados de mercado e RSS (`brapi.dev`, FMP, Google News RSS)[cite: 9]
- [pandas](https://pandas.pydata.org/) — manipulação e análise de séries históricas
- [NLTK (VADER)](https://www.nltk.org/) — análise de sentimento de notícias
- [Streamlit](https://streamlit.io/) — interface web interativa[cite: 2, 8]
- [Plotly](https://plotly.com/python/) — gráfico de preço interativo[cite: 2, 8]
- **SQLite** — persistência local da watchlist e dos snapshots[cite: 2, 4]

---

## 🚀 Como rodar o projeto

```bash
# Clone o repositório
git clone [https://github.com/eduardoruspoli/stock-analysis.git](https://github.com/eduardoruspoli/stock-analysis.git)
cd stock-analysis

# Crie e ative um ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Instale as dependências
pip install -r requirements.txt

# Baixe os dados necessários do NLTK (rodar uma única vez)
python -c "import nltk; nltk.download('vader_lexicon')"

# Configure suas chaves de API (.env, barra lateral ou variáveis de ambiente)
# BRAPI_TOKEN=seu_token_brapi
# FMP_API_KEY=sua_chave_fmp

# Execute a versão de linha de comando
python main.py

# Ou execute a versão web (interativa, com gráfico)
streamlit run app.py