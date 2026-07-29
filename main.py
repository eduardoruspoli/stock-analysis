import yfinance as yf  

def get_stock_data(ticker, period="6mo"):
    data = yf.download(ticker, period=period)
    return data
ticker_input = input("Enter the stock ticker symbol: ")
stock_data = get_stock_data(ticker_input)
print(stock_data)


def calculate_moving_average(data, window=20):
    return data['Close'].rolling(window=window).mean()
print("Calculating moving average...")
print(calculate_moving_average(stock_data, window=20))
print(calculate_moving_average(stock_data, window=50))


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

print("Calculating RSI...")
rsi = calculate_rsi(stock_data)
print(rsi)