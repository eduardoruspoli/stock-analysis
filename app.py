import json
import os
import time
from datetime import datetime, timedelta
from html import escape
from pathlib import Path

import streamlit as st  # type: ignore[import-not-found]
import plotly.graph_objects as go  # type: ignore[import-not-found]

from database import (
    init_db,
    get_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
    save_snapshot,
    get_snapshots,
)
from main import (
    get_stock_data,
    calculate_moving_average,
    calculate_bollinger_bands,
    calculate_rsi,
    calculate_macd,
    get_fundamentals,
    get_news,
    analyze_sentiment,
    get_average_sentiment,
    get_latest_values,
    calculate_score,
    get_recommendation,
    get_price_change,
    normalize_ticker,
    is_brazilian_ticker,
    get_brapi_token,
    get_fmp_api_key,
    save_api_keys_to_env,
)

st.set_page_config(page_title="Stock Analysis", page_icon="📈", layout="wide")

LEGACY_JSON_FILE = Path(__file__).parent / "watchlist.json"
STALE_AFTER_MINUTES = 30


# ---------------------------------------------------------------------------
# Database setup (+ migração de watchlist.json e normalização de sufixo .SA)
# ---------------------------------------------------------------------------
def migrate_legacy_watchlist():
    if not LEGACY_JSON_FILE.exists():
        return
    try:
        with open(LEGACY_JSON_FILE, "r") as f:
            tickers = json.load(f)
        for ticker in tickers:
            add_to_watchlist(normalize_ticker(ticker))
        os.replace(LEGACY_JSON_FILE, LEGACY_JSON_FILE.parent / "watchlist.json.migrated")
    except (json.JSONDecodeError, OSError, AttributeError, TypeError):
        pass


def normalize_existing_db_tickers():
    for raw in get_watchlist():
        clean = normalize_ticker(raw)
        if clean != raw:
            add_to_watchlist(clean)
            remove_from_watchlist(raw)


init_db()
migrate_legacy_watchlist()
normalize_existing_db_tickers()


# ---------------------------------------------------------------------------
# Custom CSS: dark theme with orange accents
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 { color: #f0f2f5; }

.stock-card {
    position: relative;
    background: linear-gradient(145deg, #161b22, #0d1117);
    border: 1px solid #21262d;
    border-top: 3px solid #ff6a00;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
}

.status-dot {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
}
.dot-buy  { background-color: #00d964; box-shadow: 0 0 8px #00d964; }
.dot-hold { background-color: #ffcc00; box-shadow: 0 0 8px #ffcc00; }
.dot-sell { background-color: #ff3b30; box-shadow: 0 0 8px #ff3b30; }
.dot-none { background-color: #484f58; }

.card-header {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    padding-right: 24px;
}

.ticker {
    font-weight: 700;
    font-size: 16px;
    color: #e6edf3;
    letter-spacing: 0.5px;
}

.market-tag {
    font-size: 9px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    background-color: #21262d;
    color: #8b949e;
    letter-spacing: 0.5px;
}

.card-footer {
    font-size: 11px;
    color: #8b949e;
    margin-top: 8px;
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


# ---------------------------------------------------------------------------
# Analysis (cached in memory) and snapshots (saved in the database)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=STALE_AFTER_MINUTES * 60, show_spinner=False)
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
        "stock_data": stock_data,
        "ma20": ma20,
        "ma50": ma50,
        "bollinger_upper": bollinger_upper,
        "bollinger_lower": bollinger_lower,
        "results": results,
        "average_sentiment": average_sentiment,
        "score": score,
        "recommendation": recommendation,
        "price": price,
        "change": change,
        "change_pct": change_pct,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
    }


def store_snapshot(ticker, analysis):
    save_snapshot(
        ticker,
        float(analysis["price"]),
        float(analysis["change"]),
        float(analysis["change_pct"]),
        int(analysis["score"]),
        analysis["recommendation"],
        analysis["fetched_at"],
    )


def refresh_tickers(tickers):
    """Atualiza um ticker por vez sem interromper toda a carteira caso apenas um ativo falhe."""
    refreshed = []
    for ticker in tickers:
        try:
            store_snapshot(ticker, get_full_analysis(ticker))
            refreshed.append(ticker)
        except Exception:
            pass
        time.sleep(0.25)
    return [t for t in tickers if t not in refreshed]


# ---------------------------------------------------------------------------
# Sidebar: Configuração das API Keys (salva direto no .env local)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.subheader("🔑 API Keys")
    st.caption("Salve suas chaves gratuitas aqui (gravadas automaticamente no `.env` local):")

    current_brapi = get_brapi_token()
    current_fmp = get_fmp_api_key()

    brapi_input = st.text_input(
        "BRAPI_TOKEN (B3)",
        value=current_brapi,
        type="password",
        placeholder="Cole seu token da brapi.dev",
    )
    fmp_input = st.text_input(
        "FMP_API_KEY (Global)",
        value=current_fmp,
        type="password",
        placeholder="Cole sua chave da FMP",
    )

    if st.button("Salvar Chaves e Atualizar", use_container_width=True):
        save_api_keys_to_env(brapi_token=brapi_input, fmp_api_key=fmp_input)
        get_full_analysis.clear()
        st.session_state.force_refresh = True
        st.success("Chaves salvas no .env!")
        st.rerun()

    st.divider()
    st.caption(
        f"**Status:**\n\n"
        f"• B3 (brapi.dev): {'✅ Configurada' if get_brapi_token() else '⚠️ Ausente'}\n\n"
        f"• Global (FMP): {'✅ Configurada' if get_fmp_api_key() else '⚠️ Ausente'}"
    )


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def currency_symbol(ticker):
    return "R$" if is_brazilian_ticker(ticker) else "$"


def market_label(ticker):
    return "B3" if is_brazilian_ticker(ticker) else "GLOBAL"


def badge_class(recommendation):
    if recommendation in ("Strong Buy", "Buy"):
        return "badge-buy"
    elif recommendation == "Hold":
        return "badge-hold"
    return "badge-sell"


def dot_class(recommendation):
    if recommendation in ("Strong Buy", "Buy"):
        return "dot-buy"
    elif recommendation == "Hold":
        return "dot-hold"
    elif recommendation in ("Sell", "Strong Sell"):
        return "dot-sell"
    return "dot-none"


def time_ago(iso_text):
    minutes = int((datetime.now() - datetime.fromisoformat(iso_text)).total_seconds() // 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} h ago"
    return f"{hours // 24} d ago"


def is_stale(snapshot):
    if snapshot is None:
        return True
    updated = datetime.fromisoformat(snapshot["updated_at"])
    return datetime.now() - updated > timedelta(minutes=STALE_AFTER_MINUTES)


def watchlist_card_html(ticker, snapshot):
    safe_ticker = escape(ticker)
    m_label = market_label(ticker)
    if snapshot is None:
        return (
            '<div class="stock-card">'
            '<span class="status-dot dot-none" title="No data yet"></span>'
            f'<div class="card-header"><span class="ticker">{safe_ticker}</span><span class="market-tag">{m_label}</span></div>'
            '<div class="card-footer">No data yet. Click "Refresh all".</div>'
            '</div>'
        )
    change = snapshot["change"]
    change_css = "change-up" if change >= 0 else "change-down"
    arrow = "▲" if change >= 0 else "▼"
    recommendation = snapshot["recommendation"]
    return (
        '<div class="stock-card">'
        f'<span class="status-dot {dot_class(recommendation)}" title="{escape(recommendation)}"></span>'
        f'<div class="card-header"><span class="ticker">{safe_ticker}</span><span class="market-tag">{m_label}</span></div>'
        f'<div class="price-sm">{currency_symbol(ticker)} {snapshot["price"]:.2f}</div>'
        f'<div class="change {change_css}">{arrow} {change:+.2f} ({snapshot["change_pct"]:+.2f}%)</div>'
        f'<div class="card-footer">{escape(recommendation)} · {time_ago(snapshot["updated_at"])}</div>'
        '</div>'
    )


# ---------------------------------------------------------------------------
# Session state + callbacks
# ---------------------------------------------------------------------------
for key, default in (
    ("detail_ticker", ""),
    ("detail_input", ""),
    ("new_ticker_input", ""),
    ("pending_refresh", []),
    ("force_refresh", False),
):
    if key not in st.session_state:
        st.session_state[key] = default


def add_ticker(raw_ticker):
    ticker = normalize_ticker(raw_ticker)
    if not ticker:
        return
    add_to_watchlist(ticker)
    if ticker not in st.session_state.pending_refresh:
        st.session_state.pending_refresh.append(ticker)


def add_from_input():
    add_ticker(st.session_state.new_ticker_input)
    st.session_state.new_ticker_input = ""


def remove_ticker(ticker):
    remove_from_watchlist(ticker)


def show_details(ticker):
    st.session_state.detail_input = ticker
    st.session_state.detail_ticker = ticker


def analyze_from_input():
    ticker = normalize_ticker(st.session_state.detail_input)
    st.session_state.detail_input = ticker
    st.session_state.detail_ticker = ticker


def request_refresh_all():
    st.session_state.force_refresh = True


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.title("📈 Stock Analysis")
st.caption(
    "Prices come from brapi.dev (B3) and Financial Modeling Prep (Global). Your watchlist is saved locally and "
    f"only refreshes stocks older than {STALE_AFTER_MINUTES} minutes (or when you click Refresh all)."
)

head_col1, head_col2 = st.columns([5, 1])
with head_col1:
    st.subheader("Watchlist")
with head_col2:
    st.button("Refresh all", key="refresh_all", on_click=request_refresh_all, use_container_width=True)

add_col1, add_col2 = st.columns([3, 1])
with add_col1:
    st.text_input(
        "Add a ticker",
        key="new_ticker_input",
        label_visibility="collapsed",
        placeholder="Add a B3 or Global ticker (e.g. PETR4, B3SA3, MXRF11, AAPL, NVDA)",
        on_change=add_from_input,
    )
with add_col2:
    st.button("Add", key="add_button", on_click=add_from_input, use_container_width=True)

watchlist = get_watchlist()
snapshots = get_snapshots()

first_run_of_session = "auto_refreshed" not in st.session_state
st.session_state.auto_refreshed = True

if st.session_state.force_refresh:
    st.session_state.force_refresh = False
    get_full_analysis.clear()
    to_refresh = list(watchlist)
elif first_run_of_session:
    to_refresh = [t for t in watchlist if is_stale(snapshots.get(t))]
else:
    to_refresh = []

for ticker in st.session_state.pending_refresh:
    if ticker in watchlist and ticker not in to_refresh:
        to_refresh.append(ticker)
st.session_state.pending_refresh = []

if to_refresh:
    with st.spinner(f"Updating {len(to_refresh)} stock(s)..."):
        not_refreshed = refresh_tickers(to_refresh)
    snapshots = get_snapshots()
    if not_refreshed:
        st.warning(
            f"Could not refresh: {', '.join(not_refreshed)}. Verify BRAPI_TOKEN (for B3) or FMP_API_KEY (for Global) "
            "in the left sidebar (API Keys), or check if the rate limit was reached."
        )

if watchlist:
    cards_per_row = 4
    for i in range(0, len(watchlist), cards_per_row):
        row_tickers = watchlist[i:i + cards_per_row]
        cols = st.columns(cards_per_row)
        for col, ticker in zip(cols, row_tickers):
            with col:
                st.markdown(watchlist_card_html(ticker, snapshots.get(ticker)), unsafe_allow_html=True)
                button_col1, button_col2 = st.columns(2)
                with button_col1:
                    st.button("Details", key=f"details_{ticker}", on_click=show_details, args=(ticker,), use_container_width=True)
                with button_col2:
                    st.button("Remove", key=f"remove_{ticker}", on_click=remove_ticker, args=(ticker,), use_container_width=True)
else:
    st.info("Your watchlist is empty. Add a B3 or Global ticker above to get started.")

st.divider()


def render_detail(ticker):
    try:
        with st.spinner(f"Analyzing {ticker}..."):
            analysis = get_full_analysis(ticker)
    except ValueError as error:
        st.error(str(error))
        return
    except Exception as error:
        st.error(f"Could not fetch data right now ({error}). Please check your API keys or try again later.")
        return

    if ticker in watchlist:
        saved = snapshots.get(ticker)
        if saved is None or saved["updated_at"] != analysis["fetched_at"]:
            store_snapshot(ticker, analysis)
            st.rerun()
    else:
        st.button("★ Add to watchlist", key="add_detail", on_click=add_ticker, args=(ticker,))

    stock_data, ma20, ma50 = analysis["stock_data"], analysis["ma20"], analysis["ma50"]
    bollinger_upper, bollinger_lower = analysis["bollinger_upper"], analysis["bollinger_lower"]
    results, average_sentiment = analysis["results"], analysis["average_sentiment"]
    score, recommendation = analysis["score"], analysis["recommendation"]
    change, change_pct = analysis["change"], analysis["change_pct"]
    symbol = currency_symbol(ticker)
    m_label = market_label(ticker)

    change_css = "change-up" if change >= 0 else "change-down"
    arrow = "▲" if change >= 0 else "▼"

    st.markdown(
        '<div class="stock-card">'
        f'<span class="status-dot {dot_class(recommendation)}" title="{escape(recommendation)}"></span>'
        '<div class="card-header">'
        f'<span class="ticker" style="font-size:20px">{escape(ticker)}</span>'
        f'<span class="market-tag" style="font-size:11px">{m_label}</span>'
        f'<span class="badge {badge_class(recommendation)}" style="font-size:13px; padding:6px 14px; margin-left:auto; margin-right:12px;">{escape(recommendation)}</span>'
        '</div>'
        f'<div class="price-lg">{symbol} {results["latest_price"]:.2f}</div>'
        f'<div class="change {change_css}" style="font-size:16px;">{arrow} {change:+.2f} ({change_pct:+.2f}%) today</div>'
        f'<div class="card-footer">Data fetched {time_ago(analysis["fetched_at"])}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data["Close"].values.flatten(), name="Close Price", line=dict(color="#ff6a00", width=2)))
    fig.add_trace(go.Scatter(x=ma20.index, y=ma20.values.flatten(), name="MA 20", line=dict(color="#58a6ff", dash="dot")))
    fig.add_trace(go.Scatter(x=ma50.index, y=ma50.values.flatten(), name="MA 50", line=dict(color="#00d964", dash="dot")))
    fig.add_trace(go.Scatter(x=bollinger_upper.index, y=bollinger_upper.values.flatten(), name="Bollinger Upper", line=dict(color="#8b949e", width=1)))
    fig.add_trace(go.Scatter(x=bollinger_lower.index, y=bollinger_lower.values.flatten(), name="Bollinger Lower", line=dict(color="#8b949e", width=1), fill="tonexty", fillcolor="rgba(139,148,158,0.08)"))
    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_title="Date",
        yaxis_title=f"Price ({symbol})",
        height=480,
        autosize=True,
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font=dict(color="#c9d1d9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Technical Indicators</div>', unsafe_allow_html=True)
        rows = [
            ("Moving Average (20)", f"{symbol} {results['latest_ma20']:.2f}"),
            ("Moving Average (50)", f"{symbol} {results['latest_ma50']:.2f}"),
            ("Bollinger Upper Band", f"{symbol} {results['latest_bollinger_upper']:.2f}"),
            ("Bollinger Lower Band", f"{symbol} {results['latest_bollinger_lower']:.2f}"),
            ("RSI (14)", f"{results['latest_rsi']:.2f}"),
            ("MACD", f"{results['latest_macd']:.2f}"),
            ("Signal", f"{results['latest_signal']:.2f}"),
        ]
        for label, value in rows:
            st.markdown(f'<div class="data-row"><span>{label}</span><span>{value}</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="section-title">Fundamentals & Sentiment</div>', unsafe_allow_html=True)
        rows = [
            ("P/E Ratio", results["pe_ratio"]),
            ("ROE", results["roe"]),
            ("Debt/Equity", results["debt_to_equity"]),
            ("Dividend Yield", results["dividend_yield"]),
            ("Profit Margin", results["profit_margin"]),
            ("Revenue Growth", results["revenue_growth"]),
            ("Free Cash Flow", results["free_cash_flow"]),
            ("Beta", results["beta"]),
            ("Analyst Target Price", results["target_mean_price"]),
            ("Average Sentiment", f"{average_sentiment:.2f}"),
        ]
        for label, value in rows:
            st.markdown(f'<div class="data-row"><span>{label}</span><span>{value}</span></div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-top:20px; text-align:center;">'
        '<span class="section-title">Final Score</span><br>'
        f'<span class="price-sm">{score}</span>'
        '</div>',
        unsafe_allow_html=True,
    )


st.subheader("Detailed Analysis")
detail_col1, detail_col2 = st.columns([4, 1])
with detail_col1:
    st.text_input(
        "Ticker",
        key="detail_input",
        label_visibility="collapsed",
        placeholder="Enter a B3 or Global ticker (e.g. PETR4, B3SA3, AAPL, MSFT)",
        on_change=analyze_from_input,
    )
with detail_col2:
    st.button("Analyze", key="analyze_button", on_click=analyze_from_input, use_container_width=True)

if st.session_state.detail_ticker:
    render_detail(st.session_state.detail_ticker)