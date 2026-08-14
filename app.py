import streamlit as st

from main import get_stock_data, calculate_moving_average, calculate_rsi, calculate_macd, get_fundamentals, get_news, analyze_sentiment, get_average_sentiment, get_latest_values, calculate_score, get_recommendation

st.title("📈 Stock Analysis")
st.write("A tool that analyzes stocks combining technical, fundamental and sentiment data.")

ticker_input = st.text_input("Enter the stock ticker symbol:")

if st.button("Analyze"):
    with st.spinner(f"Analyzing {ticker_input}..."):
        stock_data = get_stock_data(ticker_input)
        ma20 = calculate_moving_average(stock_data, window=20)
        ma50 = calculate_moving_average(stock_data, window=50)
        rsi = calculate_rsi(stock_data)
        macd, signal = calculate_macd(stock_data)
        fundamentals = get_fundamentals(ticker_input)
        results = get_latest_values(stock_data, ma20, ma50, rsi, macd, signal)
        results.update(fundamentals)
        news = get_news(ticker_input)
        sentiments = analyze_sentiment(news)
        average_sentiment = get_average_sentiment(sentiments)
        score = calculate_score(results, average_sentiment)
        recommendation = get_recommendation(score)

    st.subheader(f"Results for {ticker_input}")
    st.metric("Latest Price", f"$ {results['latest_price']:.2f}")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Moving Average (20):** $ {results['latest_ma20']:.2f}")
        st.write(f"**Moving Average (50):** $ {results['latest_ma50']:.2f}")
        st.write(f"**RSI (14):** {results['latest_rsi']:.2f}")
        st.write(f"**MACD:** {results['latest_macd']:.2f}")
        st.write(f"**Signal:** {results['latest_signal']:.2f}")
    with col2:
        st.write(f"**P/E Ratio:** {results['pe_ratio']}")
        st.write(f"**ROE:** {results['roe']}")
        st.write(f"**Debt/Equity:** {results['debt_to_equity']}")
        st.write(f"**Dividend Yield:** {results['dividend_yield']}")
        st.write(f"**Average Sentiment:** {average_sentiment:.2f}")

    st.subheader(f"Final Score: {score}")
    st.subheader(f"Recommendation: {recommendation}")