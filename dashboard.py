# dashboard.py
import streamlit as st
import pandas as pd
from binance.client import Client
from streamlit_autorefresh import st_autorefresh

# --- AUTO REFRESH (every 5 seconds) ---
st_autorefresh(interval=5000, key="crypto_refresh")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Live BTC Dashboard", layout="wide")

# --- BINANCE CLIENT (Public data only) ---
# Use no args for public market data
client = Client()

symbol = "BTCUSDT"

# --- SAFE FETCH FUNCTIONS ---
def safe_get_ticker(symbol):
    try:
        return client.get_symbol_ticker(symbol=symbol)
    except Exception as e:
        st.error(f"Error fetching ticker: {e}")
        return None

def safe_get_stats(symbol):
    try:
        return client.get_ticker(symbol=symbol)
    except Exception as e:
        st.error(f"Error fetching 24h stats: {e}")
        return None

def safe_get_order_book(symbol, limit=10):
    try:
        return client.get_order_book(symbol=symbol, limit=limit)
    except Exception as e:
        st.error(f"Error fetching order book: {e}")
        return None

def safe_get_klines(symbol, interval, limit=24):
    try:
        return client.get_klines(symbol=symbol, interval=interval, limit=limit)
    except Exception as e:
        st.error(f"Error fetching klines: {e}")
        return None

# --- FETCH LIVE DATA ---
ticker = safe_get_ticker(symbol)

if ticker:
    try:
        price = float(ticker["price"])
    except Exception:
        price = None
else:
    price = None

stats = safe_get_stats(symbol)
if stats:
    try:
        high = float(stats.get("highPrice", 0))
        low = float(stats.get("lowPrice", 0))
        change = float(stats.get("priceChangePercent", 0))
        volume = float(stats.get("quoteVolume", 0))
    except Exception:
        high = low = change = volume = None
else:
    high = low = change = volume = None

# --- FETCH ORDER BOOK ---
depth = safe_get_order_book(symbol, limit=10)
if depth:
    bids = depth.get("bids", [])
    asks = depth.get("asks", [])
else:
    bids = asks = []

# Prepare dataframe for order book (bids = buy, asks = sell)
def build_orderbook_df(bids, asks):
    df_bids = pd.DataFrame(bids, columns=["Price (USDT)", "Amount (BTC)"])
    if not df_bids.empty:
        df_bids["Price (USDT)"] = df_bids["Price (USDT)"].astype(float)
        df_bids["Amount (BTC)"] = df_bids["Amount (BTC)"].astype(float)
    df_bids["Type"] = "Bid"

    df_asks = pd.DataFrame(asks, columns=["Price (USDT)", "Amount (BTC)"])
    if not df_asks.empty:
        df_asks["Price (USDT)"] = df_asks["Price (USDT)"].astype(float)
        df_asks["Amount (BTC)"] = df_asks["Amount (BTC)"].astype(float)
    df_asks["Type"] = "Ask"

    if df_bids.empty and df_asks.empty:
        return pd.DataFrame(columns=["Price (USDT)", "Amount (BTC)", "Type"])

    df = pd.concat([df_bids, df_asks], ignore_index=True)
    return df

df_orderbook = build_orderbook_df(bids, asks)

# --- FETCH HISTORICAL DATA (24 hourly closes) ---
klines = safe_get_klines(symbol, Client.KLINE_INTERVAL_1HOUR, limit=24)
if klines:
    df_chart = pd.DataFrame(klines, columns=[
        "Open time","Open","High","Low","Close","Volume","Close time",
        "Quote asset volume","Number of trades","Taker buy base","Taker buy quote","Ignore"
    ])
    # Convert and prepare for chart
    df_chart["Open time"] = pd.to_datetime(df_chart["Open time"], unit="ms")
    df_chart["Close"] = df_chart["Close"].astype(float)
    df_chart = df_chart.set_index("Open time")
else:
    df_chart = pd.DataFrame(columns=["Close"])

# --- CSS STYLING ---
st.markdown("""
<style>
body { background-color: #0f1117; color: white; font-family: Arial, sans-serif; }

/* Metric cards */
.metric-card {
    background-color: #1a1a2e;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    box-shadow: 3px 3px 12px rgba(0,0,0,0.6);
    margin-bottom:10px;
}
.metric-card .label { 
    color: #ffffff;
    font-size:14px;
    font-weight: 600;
}
.metric-card .value { 
    font-size:22px; 
    font-weight:700; 
}
.metric-card .delta { 
    margin-top:6px; 
    font-size:14px; 
    font-weight:600; 
}

/* Tables */
table { color: white; }
td { padding: 5px; text-align: center; }

/* Vivid colors for order book rows (these are applied via pandas Styler) */
</style>
""", unsafe_allow_html=True)

# --- DASHBOARD HEADER (METRICS) ---
col1, col2, col3, col4 = st.columns(4)

# Price card
if price is not None:
    delta_color = "green" if change is not None and float(change) >= 0 else "red"
    change_text = f"{float(change):+.2f}%" if change is not None else "--"
    col1.markdown(
        f"<div class='metric-card'><div class='label'>Price</div>"
        f"<div class='value'>${price:,.2f}</div>"
        f"<div class='delta' style='color:{delta_color}'>{change_text}</div></div>",
        unsafe_allow_html=True
    )
else:
    col1.markdown("<div class='metric-card'><div class='label'>Price</div><div class='value'>--</div></div>", unsafe_allow_html=True)

# 24h High
col2.markdown(
    f"<div class='metric-card'><div class='label'>24h High</div>"
    f"<div class='value'>{f'${high:,.2f}' if high is not None else '--'}</div></div>",
    unsafe_allow_html=True
)
# 24h Low
col3.markdown(
    f"<div class='metric-card'><div class='label'>24h Low</div>"
    f"<div class='value'>{f'${low:,.2f}' if low is not None else '--'}</div></div>",
    unsafe_allow_html=True
)
# 24h Volume
col4.markdown(
    f"<div class='metric-card'><div class='label'>24h Volume (USDT)</div>"
    f"<div class='value'>{f'{volume:,.2f} USDT' if volume is not None else '--'}</div></div>",
    unsafe_allow_html=True
)

st.markdown("---")

# --- MAIN LAYOUT: CHART + ORDER BOOK ---
chart_col, order_col = st.columns([3, 1])

# --- PRICE CHART ---
with chart_col:
    st.subheader(f"{symbol} Price Chart (Last 24 hours)")
    if not df_chart.empty:
        st.line_chart(df_chart["Close"], use_container_width=True)
    else:
        st.info("Chart data not available at the moment.")

# --- ORDER BOOK ---
with order_col:
    st.subheader("Order Book (Top 10)")
    if df_orderbook.empty:
        st.info("Order book data not available.")
    else:
        # Styling function for rows: highlight bids green and asks red
        def highlight_order_row(row):
            color = "#00ff00" if row["Type"] == "Bid" else "#ff4d4d"
            return [f"background-color: {color}; color: black" if row["Type"] == "Bid" else f"background-color: {color}; color: white" for _ in row.index]

        styled = df_orderbook.style.apply(highlight_order_row, axis=1).format({
            "Price (USDT)": "{:,.2f}",
            "Amount (BTC)": "{:,.6f}"
        })
        st.dataframe(styled, use_container_width=True)
