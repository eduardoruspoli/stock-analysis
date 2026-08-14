import streamlit as st
import plotly.graph_objects as go

from main import get_stock_data, calculate_moving_average, calculate_bollinger_bands, calculate_rsi, calculate_macd, get_fundamentals, get_news, analyze_sentiment, get_average_sentiment, get_latest_values, calculate_score, get_recommendation

st.title("📈 Stock Analysis")
st.write("A tool that analyzes stocks combining technical, fundamental and sentiment data.")

ticker_input = st.text_input("Enter the stock ticker symbol:")

if st.button("Analyze"):
    with st.spinner(f"Analyzing {ticker_input}..."):
        stock_data = get_stock_data(ticker_input)
        ma20 = calculate_moving_average(stock_data, window=20)
        ma50 = calculate_moving_average(stock_data, window=50)
        bollinger_upper, bollinger_lower = calculate_bollinger_bands(stock_data)
        rsi = calculate_rsi(stock_data)
        macd, signal = calculate_macd(stock_data)
        fundamentals = get_fundamentals(ticker_input)
        results = get_latest_values(stock_data, ma20, ma50, rsi, macd, signal, bollinger_upper, bollinger_lower)
        results.update(fundamentals)
        news = get_news(ticker_input)
        sentiments = analyze_sentiment(news)
        average_sentiment = get_average_sentiment(sentiments)
        score = calculate_score(results, average_sentiment)
        recommendation = get_recommendation(score)

    st.subheader(f"Results for {ticker_input}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'].values.flatten(), name='Close Price', line=dict(color='#00cc96')))
    fig.add_trace(go.Scatter(x=ma20.index, y=ma20.values.flatten(), name='MA 20', line=dict(color='#636efa', dash='dot')))
    fig.add_trace(go.Scatter(x=ma50.index, y=ma50.values.flatten(), name='MA 50', line=dict(color='#ef553b', dash='dot')))
    fig.add_trace(go.Scatter(x=bollinger_upper.index, y=bollinger_upper.values.flatten(), name='Bollinger Upper', line=dict(color='gray', width=1)))
    fig.add_trace(go.Scatter(x=bollinger_lower.index, y=bollinger_lower.values.flatten(), name='Bollinger Lower', line=dict(color='gray', width=1), fill='tonexty', fillcolor='rgba(128,128,128,0.1)'))
    fig.update_layout(title=f"{ticker_input} Price Chart", xaxis_title="Date", yaxis_title="Price ($)", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.metric("Latest Price", f"$ {results['latest_price']:.2f}")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Technical Indicators**")
        st.write(f"Moving Average (20): $ {results['latest_ma20']:.2f}")
        st.write(f"Moving Average (50): $ {results['latest_ma50']:.2f}")
        st.write(f"Bollinger Upper Band: $ {results['latest_bollinger_upper']:.2f}")
        st.write(f"Bollinger Lower Band: $ {results['latest_bollinger_lower']:.2f}")
        st.write(f"RSI (14): {results['latest_rsi']:.2f}")
        st.write(f"MACD: {results['latest_macd']:.2f}")
        st.write(f"Signal: {results['latest_signal']:.2f}")
    with col2:
        st.write("**Fundamentals & Sentiment**")
        st.write(f"P/E Ratio: {results['pe_ratio']}")
        st.write(f"ROE: {results['roe']}")
        st.write(f"Debt/Equity: {results['debt_to_equity']}")
        st.write(f"Dividend Yield: {results['dividend_yield']}")
        st.write(f"Profit Margin: {results['profit_margin']}")
        st.write(f"Revenue Growth: {results['revenue_growth']}")
        st.write(f"Free Cash Flow: {results['free_cash_flow']}")
        st.write(f"Beta: {results['beta']}")
        st.write(f"Analyst Target Price: {results['target_mean_price']}")
        st.write(f"Average Sentiment: {average_sentiment:.2f}")

    st.subheader(f"Final Score: {score}")
    st.subheader(f"Recommendation: {recommendation}")