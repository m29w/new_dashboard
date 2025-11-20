import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# --- AUTO REFRESH EVERY 5 SECONDS ---
st_autorefresh(interval=5000, key="btc_refresh")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Live BTC Dashboard", layout="wide")
st.title("🚀 Live Bitcoin Dashboard")

# --- DARK THEME CSS ---
st.markdown("""
<style>
body { background-color: #0e1117; color: #ffffff; font-family: Arial, sans-serif; }
.price { font-size: 60px; font-weight: bold; }
.change-positive { color: #00ff00; font-size: 28px; font-weight: bold; }
.change-negative { color: #ff4c4c; font-size: 28px; font-weight: bold; }
.metrics { font-size: 20px; color: #a1a1a1; }
</style>
""", unsafe_allow_html=True)

# --- CONTAINER FOR FULL DASHBOARD ---
btc_container = st.empty()

# --- FUNCTION TO FETCH LIVE BTC DATA ---
def get_btc_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin"
    try:
        res = requests.get(url, timeout=5).json()
        market = res.get("market_data", {})
        price = market.get("current_price", {}).get("usd", "N/A")
        change_24h = market.get("price_change_percentage_24h", "N/A")
        low_24h = market.get("low_24h", {}).get("usd", "N/A")
        high_24h = market.get("high_24h", {}).get("usd", "N/A")
        return price, change_24h, low_24h, high_24h
    except:
        return "Error", "Error", "Error", "Error"

# --- FUNCTION TO FETCH BTC PRICE HISTORY WITH RETRIES ---
def get_btc_history(days=1, retries=3):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": days}
    for _ in range(retries):
        try:
            res = requests.get(url, params=params, timeout=5).json()
            prices = res.get("prices", [])
            if prices:
                df = pd.DataFrame(prices, columns=["timestamp","price"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df
        except:
            time.sleep(1)
    return pd.DataFrame(columns=["timestamp","price"])

# --- UPDATE DASHBOARD EACH REFRESH ---
with btc_container:
    # Fetch data
    price, change_24h, low_24h, high_24h = get_btc_data()
    history_df = get_btc_history(days=1)

    # --- DISPLAY METRICS ---
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown(f"<div class='price'>${price}</div>", unsafe_allow_html=True)
    with col2:
        change_class = "change-positive" if isinstance(change_24h,(int,float)) and change_24h>=0 else "change-negative"
        st.markdown(f"<div class='{change_class}'>{change_24h}% 24h</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metrics'>24h Low: ${low_24h} | 24h High: ${high_24h}</div>", unsafe_allow_html=True)

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
            margin=dict(l=20,r=20,t=30,b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("⚠️ Price history not available. Showing current price only.")
