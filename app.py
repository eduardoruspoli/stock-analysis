import streamlit as st

from main import get_stock_data, calculate_moving_average, calculate_rsi, calculate_macd, get_fundamentals, get_news, analyze_sentiment, get_average_sentiment, get_latest_values, calculate_score, get_recommendation

st.title("📈 Stock Analysis")
st.write("Ferramenta de análise de ações combinando dados técnicos, fundamentalistas e de sentimento.")