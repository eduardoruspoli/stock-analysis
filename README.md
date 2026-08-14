# 📈 Stock Analysis

A Python tool that analyzes stocks by combining **technical analysis**, **fundamental analysis**, and **news sentiment**, aiming to support buy/sell/hold decisions on a given asset.

The user enters a stock ticker (e.g. `AAPL`, `PETR4.SA`), and the program collects the data, calculates the relevant indicators, and presents a consolidated report with a recommendation (Strong Buy, Buy, Hold, Sell, or Strong Sell) based on a scoring system.

> 🚧 **Status: active development.** The core pipeline (data collection → analysis → recommendation) is fully functional. Error handling refinements, testing with more tickers, and sentiment analysis improvements are ongoing.

---

## ✅ Implemented features

**Technical analysis** (price data via [yfinance](https://pypi.org/project/yfinance/))
- Historical price collection with configurable period (`1d`, `1wk`, `1mo`, `6mo`, `1y`, etc.)
- Moving Average (20 and 50 days) — identifies short- and long-term trends
- Bollinger Bands — identifies volatility and possible price extremes
- RSI (Relative Strength Index) — identifies overbought/oversold conditions
- MACD (Moving Average Convergence Divergence) — identifies bullish or bearish momentum

**Fundamental analysis**
- P/E ratio, ROE, Debt/Equity, Dividend Yield, Profit Margin, Revenue Growth, Free Cash Flow, and Beta, pulled via `yfinance`

**Contextual analysis**
- Average analyst target price, compared against the current price

**Sentiment analysis**
- Collection of recent news about the asset
- Sentiment analysis of each news item with [NLTK VADER](https://www.nltk.org/api/nltk.sentiment.vader.html)
- Calculation of consolidated average sentiment

**Decision engine**
- Scoring system that combines all the signals above (technical, fundamental, contextual, and sentiment)
- Translation of the final score into a recommendation (Strong Buy / Buy / Hold / Sell / Strong Sell)

**Web interface**
- Interactive app built with [Streamlit](https://streamlit.io/), including a price chart with moving averages and Bollinger Bands overlaid ([Plotly](https://plotly.com/python/))

## 🚧 Roadmap (next steps)

- [x] Handling of missing data (e.g. `pe_ratio` and `debt_to_equity` unavailable for some tickers)
- [x] Testing with a wider variety of tickers (B3 and US market)
- [x] Web interface with [Streamlit](https://streamlit.io/), including an interactive price chart
- [x] Additional indicators: Bollinger Bands, Revenue Growth, Free Cash Flow, Beta, analyst target price
- [ ] Compare P/E and other multiples against the sector/index average
- [ ] Improve the formatting and explanation of the final recommendation (per-indicator justification)
- [ ] Explore alternatives to VADER for financial text (e.g. FinBERT), since VADER was trained on colloquial language and can misjudge market jargon

## 🛠️ Tech stack

- **Python 3.14**
- [yfinance](https://pypi.org/project/yfinance/) — market data collection (price, fundamentals, news)
- [pandas](https://pandas.pydata.org/) — historical series manipulation and analysis
- [NLTK (VADER)](https://www.nltk.org/) — news sentiment analysis
- [Streamlit](https://streamlit.io/) — interactive web interface
- [Plotly](https://plotly.com/python/) — interactive price chart

## 🚀 Running the project

```bash
# Clone the repository
git clone https://github.com/eduardoruspoli/stock-analysis.git
cd stock-analysis

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download the required NLTK data (run once)
python -c "import nltk; nltk.download('vader_lexicon')"

# Run the command-line version
python main.py

# Or run the web version (interactive, with chart)
streamlit run app.py
```

In the command-line version, the program prompts for the stock ticker in the terminal. In the web version, a text field on the page lets you type in the ticker (e.g. `PETR4.SA` for Brazilian stocks, `AAPL` for US stocks) and click "Analyze" to see the full report, including the price chart with moving averages and Bollinger Bands.

## 🧠 How the recommendation works

Each of the following criteria adds or subtracts points from a score:

| Criterion | Condition | Points |
|---|---|---|
| Price vs Moving Average (20 and 50) | Price above the average | +1 each |
| RSI | < 30 (oversold) / > 70 (overbought) | +1 / -1 |
| Bollinger Bands | price below lower band / above upper band | +1 / -1 |
| P/E Ratio | < 15 (cheap) / > 25 (expensive) | +1 / -1 |
| Debt/Equity | < 50 (healthy) / > 100 (highly leveraged) | +1 / -1 |
| Revenue Growth | > 10% / negative | +1 / -1 |
| Free Cash Flow | positive / negative | +1 / -1 |
| Analyst target price | upside > 10% / downside > 10% | +1 / -1 |
| MACD vs Signal | MACD above / below Signal | +1 / -1 |
| Average news sentiment | positive / negative | +1 / -1 |

The final score is translated into a recommendation: **Strong Buy**, **Buy**, **Hold**, **Sell**, or **Strong Sell**.

> This scoring system is a didactic simplification for study and portfolio purposes — it should not be used as the sole basis for real investment decisions.

### ⚠️ Known limitations

No simple scoring system like this one replaces the judgment of a human analyst. Some concrete examples found during testing:

- **A very low P/E doesn't always mean "cheap"** — it can be the result of an atypical, non-recurring profit in a single quarter, distorting the indicator. The current system doesn't distinguish recurring earnings from one-off events.
- **The engine has no historical context** — it doesn't know whether the company has recently gone through crises, management changes, or other relevant events that an experienced investor would factor in.
- **VADER (sentiment analysis) was trained on colloquial language**, not financial jargon — headlines like "Earnings Call Highlights" can be incorrectly classified as neutral or negative even when the underlying content is positive.
- **The criteria and score thresholds are arbitrary** (defined by me, based on general market rules) — they are not statistically validated against real historical performance.

For this reason, the generated recommendation should be treated as a **starting point for further research**, not as a definitive conclusion.

## 📚 Motivation

This project was created as a way to practice Python applied to a real-world problem, combining programming logic, financial data handling, and investment analysis concepts, as part of a career transition from Business Administration to Technology.

## 📄 License

This project is licensed under the MIT License — feel free to use, study, and adapt it.