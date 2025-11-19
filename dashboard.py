# advanced_dashboard.py
import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- AUTO REFRESH EVERY 5 SECONDS ---
st_autorefresh(interval=5000, key="live_refresh")

st.set_page_config(page_title="Advanced Crypto Dashboard", layout="wide")

# --- CSS STYLING ---
st.markdown("""
<style>
body { background-color: #0E1117; color: #FFFFFF; }
.metric-card {
    background-color: #1F222A;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 0 20px #00FFFF;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
    transform: scale(1.03);
    box-shadow: 0 0 40px #00FFFF;
}
h1 { text-shadow: 0 0 5px #00FFFF, 0 0 10px #00FFFF; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Crypto Dashboard Clone")

# --- COIN & TIMEFRAME SELECTOR ---
coins = {"Bitcoin": "bitcoin", "Ethereum": "ethereum", "Binance Coin": "binancecoin"}
coin_name = st.selectbox("Select Coin", list(coins.keys()))
coin_id = coins[coin_name]
timeframe = st.selectbox("Timeframe (days)", ["1","7","30","90"])

# --- FETCH HISTORICAL DATA ---
url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
params = {"vs_currency": "usd", "days": timeframe}
res = requests.get(url, params=params).json()

prices = res["prices"]
volumes = res["total_volumes"]
df = pd.DataFrame(prices, columns=["timestamp","price"])
df["volume"] = [v[1] for v in volumes]
df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
df.set_index("time", inplace=True)

# --- COMPUTE TECHNICAL INDICATORS ---
df["SMA50"] = ta.sma(df["price"], length=50)
df["EMA20"] = ta.ema(df["price"], length=20)

# --- PLOTLY CANDLESTICK + VOLUME ---
fig = go.Figure()
# Approximate OHLC with price (since CoinGecko returns only price)
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["price"], high=df["price"], low=df["price"], close=df["price"],
    name="Price"
))
fig.add_trace(go.Bar(x=df.index, y=df["volume"], name="Volume", yaxis="y2", marker_color="#00FFFF"))
fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", name="SMA50", line=dict(color="yellow")))
fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20", line=dict(color="magenta")))

fig.update_layout(
    yaxis=dict(title="Price (USD)"),
    yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
)

st.plotly_chart(fig, use_container_width=True)

# --- FETCH CURRENT SNAPSHOT DATA ---
coin_data = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}", params={"localization":"false"}).json()
md = coin_data["market_data"]

price_current = md["current_price"]["usd"]
high_24 = md["high_24h"]["usd"]
low_24 = md["low_24h"]["usd"]
change_24 = md["price_change_percentage_24h"]
market_cap = md["market_cap"]["usd"]
vol_24 = md["total_volume"]["usd"]

# --- DISPLAY METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='metric-card'><h4>Current Price</h4><h2>${price_current:,.2f}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'><h4>24h High</h4><h3>${high_24:,.2f}</h3></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'><h4>24h Low</h4><h3>${low_24:,.2f}</h3></div>", unsafe_allow_html=True)
arrow = "▲" if change_24>=0 else "▼"
color = "lime" if change_24>=0 else "red"
col4.markdown(f"<div class='metric-card'><h4>24h Change</h4><h3 style='color:{color}'>{arrow} {change_24:.2f}%</h3></div>", unsafe_allow_html=True)

col5, col6 = st.columns(2)
col5.markdown(f"<div class='metric-card'><h4>Market Cap</h4><h3>${market_cap:,.0f}</h3></div>", unsafe_allow_html=True)
col6.markdown(f"<div class='metric-card'><h4>24h Volume</h4><h3>${vol_24:,.0f}</h3></div>", unsafe_allow_html=True)

# --- OPTIONAL: Sparkline mini chart ---
st.subheader(f"{coin_name} Price Trend (Mini Chart)")
spark_df = df[-50:].reset_index()
st.line_chart(spark_df[["price"]].set_index(spark_df["time"]))
