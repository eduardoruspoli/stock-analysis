import yfinance as yf

def get_stock_data(ticker, period="6mo"):
    data = yf.download(ticker, period=period)
    return data

def calculate_moving_average(data, window=20):
    return data['Close'].rolling(window=window).mean()

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

def get_latest_values(stock_data, ma20, ma50, rsi, macd, signal):
    latest_price = stock_data['Close'].iloc[-1].iloc[0]
    latest_ma20 = ma20.iloc[-1].iloc[0]
    latest_ma50 = ma50.iloc[-1].iloc[0]
    latest_rsi = rsi.iloc[-1].iloc[0]
    latest_macd = macd.iloc[-1].iloc[0]
    latest_signal = signal.iloc[-1].iloc[0]
    return {
        "latest_price": latest_price,
        "latest_ma20": latest_ma20,
        "latest_ma50": latest_ma50,
        "latest_rsi": latest_rsi,
        "latest_macd": latest_macd,
        "latest_signal": latest_signal
    }

def main():
    ticker_input = input("Enter the stock ticker symbol: ")
    stock_data = get_stock_data(ticker_input)
    print(stock_data)

    print("Calculating moving average...")
    ma20 = calculate_moving_average(stock_data, window=20)
    ma50 = calculate_moving_average(stock_data, window=50)
    print(ma20)
    print(ma50)

    print("Calculating RSI...")
    rsi = calculate_rsi(stock_data)
    print(rsi)

    
    macd, signal = calculate_macd(stock_data)
    results = get_latest_values(stock_data, ma20, ma50, rsi, macd, signal)

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
    print(f"RSI (14): {results['latest_rsi']:.2f}")
    print(f"MACD: {results['latest_macd']:.2f}")
    print(f"Signal: {results['latest_signal']:.2f}")
    print()
    print("=" * 32)

if __name__ == "__main__":
    main()

