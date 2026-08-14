import yfinance as yf
from nltk.sentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def get_stock_data(ticker, period="6mo"):
    data = yf.download(ticker, period=period)
    return data


def calculate_moving_average(data, window=20):
    return data['Close'].rolling(window=window).mean()


def calculate_bollinger_bands(data, window=20, num_std=2):
    ma = data['Close'].rolling(window=window).mean()
    std = data['Close'].rolling(window=window).std()
    upper_band = ma + (std * num_std)
    lower_band = ma - (std * num_std)
    return upper_band, lower_band


def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    average_gain = gain.rolling(window=window).mean()
    loss = delta.where(delta < 0, 0).abs()
    average_loss = loss.rolling(window=window).mean()
    RS = average_gain / average_loss
    RSI = 100 - (100 / (1 + RS))
    return RSI

# RSI above 70 → "overbought" stock (rose too fast, might be overpriced, risk of a downward correction)
# RSI below 30 → "oversold" stock (fell too fast, might be undervalued, possible buying opportunity)
# Between 30 and 70 → neutral territory

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ma = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ma = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ma - long_ma
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal


def get_fundamentals(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    pe_ratio = info.get('trailingPE', 'N/A')
    roe = info.get('returnOnEquity', 'N/A')
    debt_to_equity = info.get('debtToEquity', 'N/A')
    market_cap = info.get('marketCap', 'N/A')
    dividend_yield = info.get('dividendYield', 'N/A')
    profit_margin = info.get('profitMargins', 'N/A')
    revenue_growth = info.get('revenueGrowth', 'N/A')
    free_cash_flow = info.get('freeCashflow', 'N/A')
    beta = info.get('beta', 'N/A')
    target_mean_price = info.get('targetMeanPrice', 'N/A')
    return {
        "pe_ratio": pe_ratio,
        "roe": roe,
        "debt_to_equity": debt_to_equity,
        "market_cap": market_cap,
        "dividend_yield": dividend_yield,
        "profit_margin": profit_margin,
        "revenue_growth": revenue_growth,
        "free_cash_flow": free_cash_flow,
        "beta": beta,
        "target_mean_price": target_mean_price
    }


def get_news(ticker, max_results=5):
    stock = yf.Ticker(ticker)
    news = stock.news
    return news[:max_results]


def analyze_sentiment(news):
    sentiments = []
    for article in news:
        content_data = article.get('content', {})
        title = content_data.get('title', '')
        description = content_data.get('summary', '')
        content = f"{title} {description}"
        score = analyzer.polarity_scores(content)
        sentiments.append({
            "title": title,
            "description": description,
            "sentiment_score": score
        })
    return sentiments


def get_average_sentiment(sentiments):
    if not sentiments:
        return 0.0
    total_score = sum(item['sentiment_score']['compound'] for item in sentiments)
    average_score = total_score / len(sentiments)
    return average_score


def get_latest_values(stock_data, ma20, ma50, rsi, macd, signal, bollinger_upper, bollinger_lower):
    latest_price = stock_data['Close'].iloc[-1].iloc[0]
    latest_ma20 = ma20.iloc[-1].iloc[0]
    latest_ma50 = ma50.iloc[-1].iloc[0]
    latest_rsi = rsi.iloc[-1].iloc[0]
    latest_macd = macd.iloc[-1].iloc[0]
    latest_signal = signal.iloc[-1].iloc[0]
    latest_bollinger_upper = bollinger_upper.iloc[-1].iloc[0]
    latest_bollinger_lower = bollinger_lower.iloc[-1].iloc[0]
    return {
        "latest_price": latest_price,
        "latest_ma20": latest_ma20,
        "latest_ma50": latest_ma50,
        "latest_rsi": latest_rsi,
        "latest_macd": latest_macd,
        "latest_signal": latest_signal,
        "latest_bollinger_upper": latest_bollinger_upper,
        "latest_bollinger_lower": latest_bollinger_lower
    }


def calculate_score(results, average_sentiment):
    score = 0

    if results['latest_price'] > results['latest_ma20']:
        score += 1
    if results['latest_price'] > results['latest_ma50']:
        score += 1

    if results['latest_rsi'] < 30:
        score += 1
    elif results['latest_rsi'] > 70:
        score -= 1

    if results['latest_price'] < results['latest_bollinger_lower']:
        score += 1
    elif results['latest_price'] > results['latest_bollinger_upper']:
        score -= 1

    if isinstance(results['pe_ratio'], (int, float)):
        if results['pe_ratio'] < 15:
            score += 1
        elif results['pe_ratio'] > 25:
            score -= 1

    if isinstance(results['debt_to_equity'], (int, float)):
        if results['debt_to_equity'] < 50:
            score += 1
        elif results['debt_to_equity'] > 100:
            score -= 1

    if isinstance(results['revenue_growth'], (int, float)):
        if results['revenue_growth'] > 0.10:
            score += 1
        elif results['revenue_growth'] < 0:
            score -= 1

    if isinstance(results['free_cash_flow'], (int, float)):
        if results['free_cash_flow'] > 0:
            score += 1
        else:
            score -= 1

    if isinstance(results['target_mean_price'], (int, float)) and results['latest_price'] > 0:
        upside = (results['target_mean_price'] - results['latest_price']) / results['latest_price']
        if upside > 0.10:
            score += 1
        elif upside < -0.10:
            score -= 1

    if results['latest_macd'] > results['latest_signal']:
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
    ticker_input = input("Enter the stock ticker symbol: ")
    stock_data = get_stock_data(ticker_input)

    print("Calculating moving average...")
    ma20 = calculate_moving_average(stock_data, window=20)
    ma50 = calculate_moving_average(stock_data, window=50)

    print("Calculating Bollinger Bands...")
    bollinger_upper, bollinger_lower = calculate_bollinger_bands(stock_data)

    print("Calculating RSI...")
    rsi = calculate_rsi(stock_data)

    print("Fetching fundamental data...")
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
    print()
    print(f"Ticker: {ticker_input}")
    print()
    print(f"Latest Price: $ {results['latest_price']:.2f}")
    print(f"Moving Average (20): $ {results['latest_ma20']:.2f}")
    print(f"Moving Average (50): $ {results['latest_ma50']:.2f}")
    print(f"Bollinger Upper Band: $ {results['latest_bollinger_upper']:.2f}")
    print(f"Bollinger Lower Band: $ {results['latest_bollinger_lower']:.2f}")
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
    print()
    print("=" * 32)
    print(f"Final Score: {score}")
    print(f"Recommendation: {get_recommendation(score)}")


if __name__ == "__main__":
    main()