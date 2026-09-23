import json
from pathlib import Path

import streamlit as st  # type: ignore[import-not-found]
import plotly.graph_objects as go  # type: ignore[import-not-found]

from main import get_stock_data, calculate_moving_average, calculate_bollinger_bands, calculate_rsi, calculate_macd, get_fundamentals, get_news, analyze_sentiment, get_average_sentiment, get_latest_values, calculate_score, get_recommendation, get_price_change

st.set_page_config(page_title="Stock Analysis", page_icon="📈", layout="wide")

WATCHLIST_FILE = Path(__file__).parent / "watchlist.json"


def load_watchlist():
    if WATCHLIST_FILE.exists():
        try:
            with open(WATCHLIST_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_watchlist(watchlist):
    try:
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(watchlist, f)
    except OSError:
        st.warning("Could not save your watchlist to disk.")


# --- Custom CSS: dark theme with orange accents (Rico-inspired) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 { color: #f0f2f5; }

.stock-card {
    background: linear-gradient(145deg, #161b22, #0d1117);
    border: 1px solid #21262d;
    border-top: 3px solid #ff6a00;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.ticker {
    font-weight: 700;
    font-size: 16px;
    color: #e6edf3;
    letter-spacing: 0.5px;
}

.badge {
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    color: #0e1117;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-buy { background-color: #00d964; }
.badge-hold { background-color: #ffcc00; }
.badge-sell { background-color: #ff3b30; color: #fff; }

.price-lg {
    font-family: 'Roboto Mono', monospace;
    font-size: 30px;
    font-weight: 700;
    color: #e6edf3;
    line-height: 1.2;
}

.price-sm {
    font-family: 'Roboto Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: #e6edf3;
}

.change {
    font-family: 'Roboto Mono', monospace;
    font-size: 14px;
    font-weight: 600;
    margin-top: 4px;
}

.change-up { color: #00d964; }
.change-down { color: #ff3b30; }

.section-title {
    color: #ff6a00;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
    margin-top: 10px;
}

.data-row {
    display: flex;
    justify-content: space-between;
    font-family: 'Roboto Mono', monospace;
    font-size: 13px;
    color: #c9d1d9;
    padding: 4px 0;
    border-bottom: 1px solid #21262d;
}

.stButton>button {
    background-color: transparent;
    border: 1px solid #ff6a00;
    color: #ff6a00;
    border-radius: 8px;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #ff6a00;
    color: #0d1117;
    border: 1px solid #ff6a00;
}
</style>
""", unsafe_allow_html=True)


st.title("📈 Stock Analysis")
st.caption("Price data has a short delay (not millisecond-level real-time). Watchlist recommendations are cached for 10 minutes to avoid excessive API calls.")


@st.cache_data(ttl=600)
def get_full_analysis(ticker):
    stock_data = get_stock_data(ticker)
    ma20 = calculate_moving_average(stock_data, window=20)
    ma50 = calculate_moving_average(stock_data, window=50)
    bollinger_upper, bollinger_lower = calculate_bollinger_bands(stock_data)
    rsi = calculate_rsi(stock_data)
    macd, signal = calculate_macd(stock_data)
    fundamentals = get_fundamentals(ticker)
    results = get_latest_values(stock_data, ma20, ma50, rsi, macd, signal, bollinger_upper, bollinger_lower)
    results.update(fundamentals)
    news = get_news(ticker)
    sentiments = analyze_sentiment(news)
    average_sentiment = get_average_sentiment(sentiments)
    score = calculate_score(results, average_sentiment)
    recommendation = get_recommendation(score)
    price, change, change_pct = get_price_change(stock_data)
    return {
        "stock_data": stock_data, "ma20": ma20, "ma50": ma50,
        "bollinger_upper": bollinger_upper, "bollinger_lower": bollinger_lower,
        "results": results, "average_sentiment": average_sentiment,
        "score": score, "recommendation": recommendation,
        "price": price, "change": change, "change_pct": change_pct,
    }


def badge_class(recommendation):
    if recommendation in ("Strong Buy", "Buy"):
        return "badge-buy"
    elif recommendation == "Hold":
        return "badge-hold"
    else:
        return "badge-sell"


if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = ""

st.subheader("Watchlist")
add_col1, add_col2 = st.columns([3, 1])
with add_col1:
    new_ticker = st.text_input("Add a ticker to your watchlist:", key="new_ticker_input", label_visibility="collapsed", placeholder="Add a ticker (e.g. AAPL, PETR4.SA)")
with add_col2:
    if st.button("Add", use_container_width=True):
        ticker_to_add = new_ticker.strip().upper()
        if ticker_to_add and ticker_to_add not in st.session_state.watchlist:
            st.session_state.watchlist.append(ticker_to_add)
            save_watchlist(st.session_state.watchlist)

if st.session_state.watchlist:
    cards_per_row = 4
    for i in range(0, len(st.session_state.watchlist), cards_per_row):
        row_tickers = st.session_state.watchlist[i:i + cards_per_row]
        cols = st.columns(cards_per_row)
        for col, ticker in zip(cols, row_tickers):
            with col:
                try:
                    analysis = get_full_analysis(ticker)
                    price, change, change_pct = analysis["price"], analysis["change"], analysis["change_pct"]
                    recommendation = analysis["recommendation"]
                    change_css = "change-up" if change >= 0 else "change-down"
                    arrow = "▲" if change >= 0 else "▼"

                    st.markdown(f"""
                    <div class="stock-card">
                        <div class="card-header">
                            <span class="ticker">{ticker}</span>
                            <span class="badge {badge_class(recommendation)}">{recommendation}</span>
                        </div>
                        <div class="price-sm">$ {price:.2f}</div>
                        <div class="change {change_css}">{arrow} {change:+.2f} ({change_pct:+.2f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception:
                    st.markdown(f"""<div class="stock-card"><span class="ticker">{ticker}</span><br><span style="color:#8b949e">Data unavailable</span></div>""", unsafe_allow_html=True)

                button_col1, button_col2 = st.columns(2)
                with button_col1:
                    if st.button("Details", key=f"analyze_{ticker}", use_container_width=True):
                        st.session_state.selected_ticker = ticker
                with button_col2:
                    if st.button("Remove", key=f"remove_{ticker}", use_container_width=True):
                        st.session_state.watchlist.remove(ticker)
                        save_watchlist(st.session_state.watchlist)
                        st.rerun()
else:
    st.info("Your watchlist is empty. Add a ticker above to get started.")

st.divider()

st.subheader("Detailed Analysis")
ticker_input = st.text_input("Enter the stock ticker symbol:", value=st.session_state.selected_ticker)

if st.button("Analyze Stock"):
    with st.spinner(f"Analyzing {ticker_input}..."):
        analysis = get_full_analysis(ticker_input)

    stock_data, ma20, ma50 = analysis["stock_data"], analysis["ma20"], analysis["ma50"]
    bollinger_upper, bollinger_lower = analysis["bollinger_upper"], analysis["bollinger_lower"]
    results, average_sentiment = analysis["results"], analysis["average_sentiment"]
    score, recommendation = analysis["score"], analysis["recommendation"]
    change, change_pct = analysis["change"], analysis["change_pct"]

    change_css = "change-up" if change >= 0 else "change-down"
    arrow = "▲" if change >= 0 else "▼"

    st.markdown(f"""
    <div class="stock-card">
        <div class="card-header">
            <span class="ticker" style="font-size:20px">{ticker_input}</span>
            <span class="badge {badge_class(recommendation)}" style="font-size:13px; padding:6px 14px;">{recommendation}</span>
        </div>
        <div class="price-lg">$ {results['latest_price']:.2f}</div>
        <div class="change {change_css}" style="font-size:16px;">{arrow} {change:+.2f} ({change_pct:+.2f}%) today</div>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'].values.flatten(), name='Close Price', line=dict(color='#ff6a00', width=2)))
    fig.add_trace(go.Scatter(x=ma20.index, y=ma20.values.flatten(), name='MA 20', line=dict(color='#58a6ff', dash='dot')))
    fig.add_trace(go.Scatter(x=ma50.index, y=ma50.values.flatten(), name='MA 50', line=dict(color='#00d964', dash='dot')))
    fig.add_trace(go.Scatter(x=bollinger_upper.index, y=bollinger_upper.values.flatten(), name='Bollinger Upper', line=dict(color='#8b949e', width=1)))
    fig.add_trace(go.Scatter(x=bollinger_lower.index, y=bollinger_lower.values.flatten(), name='Bollinger Lower', line=dict(color='#8b949e', width=1), fill='tonexty', fillcolor='rgba(139,148,158,0.08)'))
    fig.update_layout(
        title=f"{ticker_input} Price Chart",
        xaxis_title="Date", yaxis_title="Price ($)",
        height=480, autosize=True,
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        font=dict(color="#c9d1d9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Technical Indicators</div>', unsafe_allow_html=True)
        rows = [
            ("Moving Average (20)", f"$ {results['latest_ma20']:.2f}"),
            ("Moving Average (50)", f"$ {results['latest_ma50']:.2f}"),
            ("Bollinger Upper Band", f"$ {results['latest_bollinger_upper']:.2f}"),
            ("Bollinger Lower Band", f"$ {results['latest_bollinger_lower']:.2f}"),
            ("RSI (14)", f"{results['latest_rsi']:.2f}"),
            ("MACD", f"{results['latest_macd']:.2f}"),
            ("Signal", f"{results['latest_signal']:.2f}"),
        ]
        for label, value in rows:
            st.markdown(f'<div class="data-row"><span>{label}</span><span>{value}</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="section-title">Fundamentals & Sentiment</div>', unsafe_allow_html=True)
        rows = [
            ("P/E Ratio", results['pe_ratio']),
            ("ROE", results['roe']),
            ("Debt/Equity", results['debt_to_equity']),
            ("Dividend Yield", results['dividend_yield']),
            ("Profit Margin", results['profit_margin']),
            ("Revenue Growth", results['revenue_growth']),
            ("Free Cash Flow", results['free_cash_flow']),
            ("Beta", results['beta']),
            ("Analyst Target Price", results['target_mean_price']),
            ("Average Sentiment", f"{average_sentiment:.2f}"),
        ]
        for label, value in rows:
            st.markdown(f'<div class="data-row"><span>{label}</span><span>{value}</span></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:20px; text-align:center;">
        <span class="section-title">Final Score</span><br>
        <span class="price-sm">{score}</span>
    </div>
    """, unsafe_allow_html=True)
