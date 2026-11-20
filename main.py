import os
import re
import urllib.parse
import xml.etree.ElementTree as ET

import pandas as pd
import requests
from nltk.sentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

BRAPI_BASE_URL = "https://brapi.dev/api"
FMP_BASE_URL = "https://financialmodelingprep.com/stable"


def _env_file_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _read_env_file_value(key):
    """Lê uma chave do arquivo .env na mesma pasta do script, se existir."""
    env_path = _env_file_path()
    if not os.path.exists(env_path):
        return ""
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                k, v = stripped.split("=", 1)
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")
    except OSError:
        return ""
    return ""


def save_api_keys_to_env(brapi_token="", fmp_api_key=""):
    """Salva as chaves no arquivo .env local e atualiza os.environ da sessão atual."""
    env_path = _env_file_path()
    existing = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and "=" in stripped:
                        k, v = stripped.split("=", 1)
                        existing[k.strip()] = v.strip()
        except OSError:
            pass

    if brapi_token is not None:
        clean_brapi = brapi_token.strip()
        existing["BRAPI_TOKEN"] = clean_brapi
        os.environ["BRAPI_TOKEN"] = clean_brapi

    if fmp_api_key is not None:
        clean_fmp = fmp_api_key.strip()
        existing["FMP_API_KEY"] = clean_fmp
        os.environ["FMP_API_KEY"] = clean_fmp

    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in existing.items():
            if v:
                f.write(f"{k}={v}\n")


def get_brapi_token():
    token = os.getenv("BRAPI_TOKEN", "").strip()
    if token:
        return token
    return _read_env_file_value("BRAPI_TOKEN")


def get_fmp_api_key():
    key = os.getenv("FMP_API_KEY", "").strip()
    if key:
        return key
    return _read_env_file_value("FMP_API_KEY")


def normalize_ticker(ticker):
    """Padroniza o ticker removendo sufixo .SA e espaços."""
    ticker = ticker.strip().upper()
    if ticker.endswith(".SA"):
        ticker = ticker[:-3]
    return ticker


def is_brazilian_ticker(ticker):
    """Identifica tickers da B3 (ex: PETR4, B3SA3, MXRF11, TAEE11) com ou sem .SA."""
    raw = ticker.strip().upper()
    if raw.endswith(".SA"):
        return True
    clean = normalize_ticker(raw)
    # 4 caracteres alfanuméricos começando com letra + 1 ou 2 dígitos (cobre B3SA3, PETR4, MXRF11, etc.)
    return bool(re.fullmatch(r"[A-Z][A-Z0-9]{3}\d{1,2}", clean))


# ---------------------------------------------------------------------------
# Provedor 1: B3 (brapi.dev)
# ---------------------------------------------------------------------------
def _fetch_brapi_quote(ticker, range_period="3mo", include_fundamentals=True):
    clean_ticker = normalize_ticker(ticker)
    token = get_brapi_token()

    params = {"range": range_period, "interval": "1d"}
    headers = {}
    if token:
        params["token"] = token
        headers["Authorization"] = f"Bearer {token}"
    if include_fundamentals:
        params["modules"] = "defaultKeyStatistics,financialData"

    url = f"{BRAPI_BASE_URL}/quote/{urllib.parse.quote(clean_ticker)}"
    response = requests.get(url, params=params, headers=headers, timeout=15)

    if response.status_code == 401:
        raise ValueError(
            f"Token da brapi.dev ausente ou inválido para '{clean_ticker}'. "
            "Insira seu BRAPI_TOKEN na barra lateral esquerda (API Keys) ou no arquivo .env."
        )
    if response.status_code == 429:
        raise ValueError("Limite de requisições da brapi.dev atingido. Aguarde alguns minutos.")
    if response.status_code == 404:
        raise ValueError(f"Ativo B3 '{clean_ticker}' não encontrado na brapi.dev.")

    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise ValueError(f"Nenhum dado retornado para '{clean_ticker}' na brapi.dev.")
    return results[0]


def _get_b3_stock_data(ticker, period="3mo"):
    quote = _fetch_brapi_quote(ticker, range_period=period, include_fundamentals=False)
    history = quote.get("historicalDataPrice", [])
    if not history:
        raise ValueError(f"Sem histórico de preços para '{ticker}' na brapi.dev.")

    df = pd.DataFrame(history)
    df["Date"] = pd.to_datetime(df["date"], unit="s")
    df = df.set_index("Date").sort_index()
    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
        "adjustedClose": "Adj Close",
    })
    df = df.dropna(subset=["Close"])
    if len(df) < 2:
        raise ValueError(f"Histórico insuficiente para '{ticker}'.")
    return df


def _get_b3_fundamentals(ticker):
    try:
        quote = _fetch_brapi_quote(ticker, range_period="1d", include_fundamentals=True)
    except Exception:
        # Fallback caso o plano gratuito não inclua módulos avançados neste ativo (ex: FIIs)
        quote = _fetch_brapi_quote(ticker, range_period="1d", include_fundamentals=False)

    stats = quote.get("defaultKeyStatistics") or {}
    fin = quote.get("financialData") or {}

    def v(val):
        return val if val is not None else "N/A"

    return {
        "pe_ratio": v(quote.get("priceEarnings") or stats.get("trailingPE")),
        "roe": v(fin.get("returnOnEquity")),
        "debt_to_equity": v(fin.get("debtToEquity")),
        "market_cap": v(quote.get("marketCap")),
        "dividend_yield": v(stats.get("dividendYield") or quote.get("dividendYield")),
        "profit_margin": v(fin.get("profitMargins") or stats.get("profitMargins")),
        "revenue_growth": v(fin.get("revenueGrowth")),
        "free_cash_flow": v(fin.get("freeCashflow")),
        "beta": v(stats.get("beta")),
        "target_mean_price": v(fin.get("targetMeanPrice")),
    }


# ---------------------------------------------------------------------------
# Provedor 2: Global / EUA (Financial Modeling Prep - FMP)
# ---------------------------------------------------------------------------
def _require_fmp_key(ticker):
    key = get_fmp_api_key()
    if not key:
        raise ValueError(
            f"Chave FMP_API_KEY não configurada para buscar o ativo global '{ticker}'. "
            "Insira sua FMP_API_KEY na barra lateral esquerda (API Keys) ou no arquivo .env."
        )
    return key


def _get_global_stock_data(ticker, days=120):
    clean_ticker = normalize_ticker(ticker)
    api_key = _require_fmp_key(clean_ticker)

    url = f"{FMP_BASE_URL}/historical-price-eod/full"
    params = {"symbol": clean_ticker, "apikey": api_key}
    response = requests.get(url, params=params, timeout=15)

    if response.status_code in (401, 403):
        raise ValueError(
            f"Chave FMP_API_KEY inválida ou sem acesso ao ativo '{clean_ticker}' no plano gratuito."
        )
    if response.status_code == 429:
        raise ValueError("Limite de requisições da FMP atingido. Tente novamente mais tarde.")

    response.raise_for_status()
    payload = response.json()

    records = payload if isinstance(payload, list) else payload.get("historical", [])
    if not records:
        raise ValueError(f"Ativo global '{clean_ticker}' não encontrado na FMP.")

    df = pd.DataFrame(records[:days])
    df["Date"] = pd.to_datetime(df["date"])
    df = df.set_index("Date").sort_index()
    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    })
    df = df.dropna(subset=["Close"])
    if len(df) < 2:
        raise ValueError(f"Histórico insuficiente para '{clean_ticker}'.")
    return df


def _get_global_fundamentals(ticker):
    clean_ticker = normalize_ticker(ticker)
    api_key = get_fmp_api_key()
    if not api_key:
        return _empty_fundamentals()

    def v(val):
        return val if val is not None else "N/A"

    try:
        ratios_resp = requests.get(
            f"{FMP_BASE_URL}/ratios-ttm",
            params={"symbol": clean_ticker, "apikey": api_key},
            timeout=10,
        )
        metrics_resp = requests.get(
            f"{FMP_BASE_URL}/key-metrics-ttm",
            params={"symbol": clean_ticker, "apikey": api_key},
            timeout=10,
        )
        profile_resp = requests.get(
            f"{FMP_BASE_URL}/profile",
            params={"symbol": clean_ticker, "apikey": api_key},
            timeout=10,
        )

        ratios = (ratios_resp.json() or [{}])[0] if ratios_resp.ok else {}
        metrics = (metrics_resp.json() or [{}])[0] if metrics_resp.ok else {}
        profile = (profile_resp.json() or [{}])[0] if profile_resp.ok else {}

        return {
            "pe_ratio": v(ratios.get("priceToEarningsRatioTTM")),
            "roe": v(metrics.get("returnOnEquityTTM")),
            "debt_to_equity": v(ratios.get("debtToEquityRatioTTM")),
            "market_cap": v(profile.get("marketCap") or metrics.get("marketCap")),
            "dividend_yield": v(ratios.get("dividendYieldTTM")),
            "profit_margin": v(ratios.get("netProfitMarginTTM")),
            "revenue_growth": "N/A",
            "free_cash_flow": v(metrics.get("freeCashFlowPerShareTTM")),
            "beta": v(profile.get("beta")),
            "target_mean_price": "N/A",
        }
    except Exception:
        return _empty_fundamentals()


def _empty_fundamentals():
    return {
        "pe_ratio": "N/A",
        "roe": "N/A",
        "debt_to_equity": "N/A",
        "market_cap": "N/A",
        "dividend_yield": "N/A",
        "profit_margin": "N/A",
        "revenue_growth": "N/A",
        "free_cash_flow": "N/A",
        "beta": "N/A",
        "target_mean_price": "N/A",
    }


# ---------------------------------------------------------------------------
# Interface Unificada (Roteamento B3 vs Global)
# ---------------------------------------------------------------------------
def get_stock_data(ticker, period="3mo"):
    clean_ticker = normalize_ticker(ticker)
    if is_brazilian_ticker(clean_ticker):
        return _get_b3_stock_data(clean_ticker, period=period)
    return _get_global_stock_data(clean_ticker)


def get_fundamentals(ticker):
    clean_ticker = normalize_ticker(ticker)
    try:
        if is_brazilian_ticker(clean_ticker):
            return _get_b3_fundamentals(clean_ticker)
        return _get_global_fundamentals(clean_ticker)
    except Exception:
        return _empty_fundamentals()


def calculate_moving_average(data, window=20):
    return data["Close"].rolling(window=window).mean()


def get_price_change(stock_data):
    latest_close = float(stock_data["Close"].iloc[-1])
    previous_close = float(stock_data["Close"].iloc[-2])
    change = latest_close - previous_close
    change_pct = (change / previous_close) * 100
    return latest_close, change, change_pct


def calculate_bollinger_bands(data, window=20, num_std=2):
    ma = data["Close"].rolling(window=window).mean()
    std = data["Close"].rolling(window=window).std()
    upper_band = ma + (std * num_std)
    lower_band = ma - (std * num_std)
    return upper_band, lower_band


def calculate_rsi(data, window=14):
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0)
    average_gain = gain.rolling(window=window).mean()
    loss = delta.where(delta < 0, 0).abs()
    average_loss = loss.rolling(window=window).mean()
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ma = data["Close"].ewm(span=short_window, adjust=False).mean()
    long_ma = data["Close"].ewm(span=long_window, adjust=False).mean()
    macd = short_ma - long_ma
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal


def get_news(ticker, max_results=5):
    """Busca notícias em PT-BR para B3 e em EN-US para ações globais via Google News RSS."""
    clean_ticker = normalize_ticker(ticker)
    if is_brazilian_ticker(clean_ticker):
        query = urllib.parse.quote(f"{clean_ticker} ações bolsa")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    else:
        query = urllib.parse.quote(f"{clean_ticker} stock market")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    try:
        resp = requests.get(rss_url, timeout=8)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        articles = []
        for item in root.findall("./channel/item")[:max_results]:
            title = item.findtext("title") or ""
            description = re.sub(r"<[^>]+>", "", item.findtext("description") or "")
            articles.append({
                "content": {
                    "title": title,
                    "summary": description,
                }
            })
        return articles
    except Exception:
        return []


def analyze_sentiment(news):
    sentiments = []
    for article in news:
        content_data = article.get("content", {})
        title = content_data.get("title", "")
        description = content_data.get("summary", "")
        content = f"{title} {description}"
        score = analyzer.polarity_scores(content)
        sentiments.append({
            "title": title,
            "description": description,
            "sentiment_score": score,
        })
    return sentiments


def get_average_sentiment(sentiments):
    if not sentiments:
        return 0.0
    total_score = sum(item["sentiment_score"]["compound"] for item in sentiments)
    return total_score / len(sentiments)


def get_latest_values(stock_data, ma20, ma50, rsi, macd, signal, bollinger_upper, bollinger_lower):
    return {
        "latest_price": float(stock_data["Close"].iloc[-1]),
        "latest_ma20": float(ma20.iloc[-1]),
        "latest_ma50": float(ma50.iloc[-1]),
        "latest_rsi": float(rsi.iloc[-1]),
        "latest_macd": float(macd.iloc[-1]),
        "latest_signal": float(signal.iloc[-1]),
        "latest_bollinger_upper": float(bollinger_upper.iloc[-1]),
        "latest_bollinger_lower": float(bollinger_lower.iloc[-1]),
    }


def calculate_score(results, average_sentiment):
    score = 0

    if results["latest_price"] > results["latest_ma20"]:
        score += 1
    if results["latest_price"] > results["latest_ma50"]:
        score += 1

    if results["latest_rsi"] < 30:
        score += 1
    elif results["latest_rsi"] > 70:
        score -= 1

    if results["latest_price"] < results["latest_bollinger_lower"]:
        score += 1
    elif results["latest_price"] > results["latest_bollinger_upper"]:
        score -= 1

    if isinstance(results["pe_ratio"], (int, float)):
        if results["pe_ratio"] < 15:
            score += 1
        elif results["pe_ratio"] > 25:
            score -= 1

    if isinstance(results["debt_to_equity"], (int, float)):
        if results["debt_to_equity"] < 50:
            score += 1
        elif results["debt_to_equity"] > 100:
            score -= 1

    if isinstance(results["revenue_growth"], (int, float)):
        if results["revenue_growth"] > 0.10:
            score += 1
        elif results["revenue_growth"] < 0:
            score -= 1

    if isinstance(results["free_cash_flow"], (int, float)):
        if results["free_cash_flow"] > 0:
            score += 1
        else:
            score -= 1

    if isinstance(results["target_mean_price"], (int, float)) and results["latest_price"] > 0:
        upside = (results["target_mean_price"] - results["latest_price"]) / results["latest_price"]
        if upside > 0.10:
            score += 1
        elif upside < -0.10:
            score -= 1

    if results["latest_macd"] > results["latest_signal"]:
        score += 1
    else:
        score -= 1

    if average_sentiment > 0:
        score += 1
    elif average_sentiment < 0:
        score -= 1

    return score


def get_recommendation(score):
    if score >= 6:
        return "Strong Buy"
    elif score >= 3:
        return "Buy"
    elif score >= -2:
        return "Hold"
    elif score >= -5:
        return "Sell"
    else:
        return "Strong Sell"


def main():
    ticker_input = normalize_ticker(input("Enter the stock ticker symbol (e.g. PETR4, B3SA3, AAPL): "))
    symbol = "R$" if is_brazilian_ticker(ticker_input) else "$"
    try:
        stock_data = get_stock_data(ticker_input)
    except ValueError as error:
        print(error)
        return

    ma20 = calculate_moving_average(stock_data, window=20)
    ma50 = calculate_moving_average(stock_data, window=50)
    bollinger_upper, bollinger_lower = calculate_bollinger_bands(stock_data)
    rsi = calculate_rsi(stock_data)
    fundamentals = get_fundamentals(ticker_input)
    macd, signal = calculate_macd(stock_data)

    results = get_latest_values(stock_data, ma20, ma50, rsi, macd, signal, bollinger_upper, bollinger_lower)
    results.update(fundamentals)

    news = get_news(ticker_input)
    sentiments = analyze_sentiment(news)
    average_sentiment = get_average_sentiment(sentiments)
    score = calculate_score(results, average_sentiment)

    print()
    print("=" * 32)
    print("       LATEST ANALYSIS")
    print("=" * 32)
    print(f"Ticker: {ticker_input} ({'B3' if symbol == 'R$' else 'Global'})")
    print(f"Latest Price: {symbol} {results['latest_price']:.2f}")
    print(f"Moving Average (20): {symbol} {results['latest_ma20']:.2f}")
    print(f"Moving Average (50): {symbol} {results['latest_ma50']:.2f}")
    print(f"Bollinger Upper Band: {symbol} {results['latest_bollinger_upper']:.2f}")
    print(f"Bollinger Lower Band: {symbol} {results['latest_bollinger_lower']:.2f}")
    print(f"RSI (14): {results['latest_rsi']:.2f}")
    print(f"MACD: {results['latest_macd']:.2f}")
    print(f"Signal: {results['latest_signal']:.2f}")
    print(f"P/L: {results['pe_ratio']}")
    print(f"ROE: {results['roe']}")
    print(f"Debt/Equity: {results['debt_to_equity']}")
    print(f"Dividend Yield: {results['dividend_yield']}")
    print(f"Profit Margin: {results['profit_margin']}")
    print(f"Revenue Growth: {results['revenue_growth']}")
    print(f"Free Cash Flow: {results['free_cash_flow']}")
    print(f"Beta: {results['beta']}")
    print(f"Analyst Target Price: {results['target_mean_price']}")
    print(f"Average Sentiment: {average_sentiment:.2f}")
    print("=" * 32)
    print(f"Final Score: {score}")
    print(f"Recommendation: {get_recommendation(score)}")


if __name__ == "__main__":
    main()