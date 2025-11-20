import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# --- AUTO REFRESH EVERY 5 SECONDS ---
st_autorefresh = st.experimental_rerun  # will refresh manually via st_autorefresh later

st.set_page_config(page_title="Live BTC Dashboard", layout="wide")

# --- DASHBOARD STYLING ---
st.markdown("""
<style>
body { background-color: #000000; color: white; font-family: Arial, sans-serif; }

/* Metric cards */
.metric-card {
    background-color: #111111;  
    border-radius: 12px;
    padding: 25px;
    text-align: center;
    margin-bottom:10px;
    box-shadow: 0 0 15px rgba(255,255,255,0.1);
    border: 1px solid #333;  
}
.metric-card .label { 
    color: #ffffff; font-size:18px; font-weight: bold;    
}
.metric-card .value { 
    font-size:32px; font-weight:bold; color: #00ffff; 
}
.metric-card .delta { 
    margin-top:5px; font-size:16px; font-weight:bold; color: #ff5555; 
}

/* Order book table */
table { color: white; background-color: #000000; }
td { padding: 5px; text-align: center; }
.bid { background-color: #00ff00 !important; color: black; }   
.ask { background-color: #ff0000 !important; color: white; }
</style>
""", unsafe_allow_html=True)

# --- SYMBOL ---
symbol = "BTCUSDT"

# --- FETCH CURRENT PRICE ---
price_res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
price = float(price_res.json()["price"])

# --- FETCH 24H STATS ---
stats_res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}")
stats = stats_res.json()
high = float(stats["highPrice"])
low = float(stats["lowPrice"])
change = float(stats["priceChangePercent"])
volume = float(stats["quoteVolume"])

# --- METRIC CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='metric-card'><div class='label'>Price</div><div class='value'>${price:,.2f}</div><div class='delta'>{change:+.2f}%</div></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'><div class='label'>24h High</div><div class='value'>${high:,.2f}</div></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'><div class='label'>24h Low</div><div class='value'>${low:,.2f}</div></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric-card'><div class='label'>24h Volume (USDT)</div><div class='value'>{volume:,.2f}</div></div>", unsafe_allow_html=True)

st.markdown("---")

# --- FETCH ORDER BOOK ---
depth_res = requests.get(f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=10")
depth = depth_res.json()
bids = pd.DataFrame(depth["bids"], columns=["Price", "Amount"]).astype(float)
bids["Type"] = "Bid"
asks = pd.DataFrame(depth["asks"], columns=["Price", "Amount"]).astype(float)
asks["Type"] = "Ask"
order_book = pd.concat([bids, asks]).reset_index(drop=True)

# --- FETCH HISTORICAL DATA FOR CHART ---
klines_res = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=24")
klines = klines_res.json()
df_chart = pd.DataFrame(klines, columns=[
    "Open Time","Open","High","Low","Close","Volume","Close Time",
    "Quote Asset Volume","Number of Trades","Taker Buy Base","Taker Buy Quote","Ignore"
])
df_chart["Close"] = df_chart["Close"].astype(float)
df_chart["Open Time"] = pd.to_datetime(df_chart["Open Time"], unit="ms")

# --- LAYOUT: CHART + ORDER BOOK ---
chart_col, order_col = st.columns([3, 1])

with chart_col:
    st.subheader(f"{symbol} Price Chart (Last 24h)")
    st.line_chart(df_chart.set_index("Open Time")["Close"])

with order_col:
    st.subheader("Order Book (Top 10)")
    def style_orderbook(row):
        return ["background-color: #00ff00; color: black" if t=="Bid" else "background-color: #ff0000; color: white" for t in row["Type"]]

    st.dataframe(order_book.style.apply(style_orderbook, axis=1).set_properties(**{"background-color": "#111111", "color": "white"}))

# --- AUTO REFRESH EVERY 5 SECONDS ---
st.experimental_rerun()
