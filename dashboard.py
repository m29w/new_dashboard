import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- AUTO REFRESH EVERY 5 SECONDS ---
st_autorefresh(interval=5000, key="btc_refresh")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Live BTC Dashboard", layout="wide")
st.title("🚀 Live Bitcoin Dashboard")

# --- FUNCTION TO FETCH BTC DATA ---
def get_btc_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin"
    try:
        response = requests.get(url)
        data = response.json()
        market_data = data.get("market_data", {})
        price = market_data.get("current_price", {}).get("usd", "N/A")
        change_24h = market_data.get("price_change_percentage_24h", "N/A")
        low_24h = market_data.get("low_24h", {}).get("usd", "N/A")
        high_24h = market_data.get("high_24h", {}).get("usd", "N/A")
        return price, change_24h, low_24h, high_24h
    except Exception as e:
        return "Error", "Error", "Error", "Error"

# --- FUNCTION TO FETCH BTC PRICE HISTORY ---
def get_btc_history(days=1):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": days}
    try:
        res = requests.get(url, params=params).json()
        prices = res.get("prices", [])
        if prices:
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        else:
            return pd.DataFrame(columns=["timestamp", "price"])
    except Exception as e:
        return pd.DataFrame(columns=["timestamp", "price"])

# --- FETCH LIVE BTC DATA ---
price, change_24h, low_24h, high_24h = get_btc_data()
history_df = get_btc_history(days=1)

# --- DISPLAY CURRENT BTC METRICS ---
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"<h1 style='color:white'>${price}</h1>", unsafe_allow_html=True)
with col2:
    change_color = "green" if isinstance(change_24h, (int, float)) and change_24h >= 0 else "red"
    st.markdown(f"<h3 style='color:{change_color}'>{change_24h}% 24h</h3>", unsafe_allow_html=True)

st.markdown(f"<p style='color:#a1a1a1'>24h Low: ${low_24h} | 24h High: ${high_24h}</p>", unsafe_allow_html=True)

# --- PLOT BTC PRICE HISTORY ---
if not history_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df["timestamp"],
        y=history_df["price"],
        mode="lines",
        line=dict(color="#00cc96", width=2),
        name="BTC Price"
    ))
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Price history data not available.")
