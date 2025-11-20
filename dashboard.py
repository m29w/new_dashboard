import streamlit as st
import pandas as pd
from binance.client import Client
from streamlit_autorefresh import st_autorefresh

# --- AUTO REFRESH ---
st_autorefresh(interval=5000, key="crypto_refresh")  # refresh every 5 sec

# --- PAGE CONFIG ---
st.set_page_config(page_title="Live BTC Dashboard", layout="wide")

# --- BINANCE CLIENT (Public data only) ---
client = Client("", "")  # empty strings for public data

symbol = "BTCUSDT"

# --- FETCH LIVE DATA ---
ticker = client.get_symbol_ticker(symbol=symbol)
price = float(ticker["price"])

stats = client.get_ticker(symbol=symbol)
high = float(stats["highPrice"])
low = float(stats["lowPrice"])
change = float(stats["priceChangePercent"])
volume = float(stats["quoteVolume"])

# --- FETCH ORDER BOOK ---
depth = client.get_order_book(symbol=symbol, limit=10)
bids = depth["bids"]
asks = depth["asks"]

# Prepare dataframe for order book
df_bids = pd.DataFrame(bids, columns=["Price (USDT)", "Amount (BTC)"])
df_bids["Price (USDT)"] = df_bids["Price (USDT)"].astype(float)
df_bids["Amount (BTC)"] = df_bids["Amount (BTC)"].astype(float)
df_bids["Type"] = "Bid"

df_asks = pd.DataFrame(asks, columns=["Price (USDT)", "Amount (BTC)"])
df_asks["Price (USDT)"] = df_asks["Price (USDT)"].astype(float)
df_asks["Amount (BTC)"] = df_asks["Amount (BTC)"].astype(float)
df_asks["Type"] = "Ask"

# Concatenate and reset index
df_orderbook = pd.concat([df_bids, df_asks]).reset_index(drop=True)

# --- FETCH HISTORICAL DATA (24h chart) ---
klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=24)
df_chart = pd.DataFrame(klines, columns=[
    "Open time","Open","High","Low","Close","Volume","Close time",
    "Quote asset volume","Number of trades","Taker buy base","Taker buy quote","Ignore"
])
df_chart["Close"] = df_chart["Close"].astype(float)

# --- CSS STYLING ---
st.markdown("""
<style>
body { background-color: #0f1117; color: white; font-family: Arial, sans-serif; }

/* Metric cards */
.metric-card {
    background-color: #1a1a2e;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 3px 3px 15px rgba(0,0,0,0.6);
    margin-bottom:10px;
}
.metric-card .label { 
    color: #ffffff;       /* bright white headers */
    font-size:16px;       /* slightly larger font */
    font-weight: bold;    /* bold for emphasis */
}
.metric-card .value { 
    font-size:28px; 
    font-weight:bold; 
}
.metric-card .delta { 
    margin-top:5px; 
    font-size:14px; 
    font-weight:bold; 
}

/* Order book table */
table { color: white; }
td { padding: 5px; text-align: center; }

/* Vivid colors for order book */
.bid { background-color: #00ff00 !important; color: black; }   /* bright green */
.ask { background-color: #ff0000 !important; color: white; }   /* bright red */
</style>
""", unsafe_allow_html=True)

# --- DASHBOARD HEADER (METRICS) ---
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='metric-card'><div class='label'>Price</div><div class='value'>${price:,.2f}</div><div class='delta'>{float(change):+.2f}%</div></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'><div class='label'>24h High</div><div class='value'>${high:,.2f}</div></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'><div class='label'>24h Low</div><div class='value'>${low:,.2f}</div></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric-card'><div class='label'>24h Volume</div><div class='value'>{volume:,.2f} USDT</div></div>", unsafe_allow_html=True)

st.markdown("---")

# --- MAIN LAYOUT: CHART + ORDER BOOK ---
chart_col, order_col = st.columns([3, 1])

# --- PRICE CHART ---
with chart_col:
    st.subheader(f"{symbol} Price Chart (Last 24h)")
    st.line_chart(df_chart["Close"], use_container_width=True)

# --- ORDER BOOK ---
with order_col:
    st.subheader("Order Book (Top 10)")
    def style_orderbook(row):
        return ["background-color: #00ff00; color: black" if t=="Bid" else "background-color: #ff0000; color: white" for t in row["Type"]]

    st.dataframe(
        df_orderbook.style.apply(style_orderbook, axis=1).set_properties(**{"background-color": "#1a1a2e", "color": "white"})
    )
