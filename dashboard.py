# dashboard.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import altair as alt
from streamlit_autorefresh import st_autorefresh

# --- AUTO REFRESH EVERY 5 SECONDS ---
st_autorefresh(interval=5000, key="crypto_refresh")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Live Crypto Dashboard", layout="wide")

# --- DARK THEME STYLING ---
st.markdown(
    """
    <style>
    body {background-color: #0E1117; color: #FFFFFF;}
    .stMetric {background-color: #1F222A; border-radius: 15px; padding: 20px; text-align:center; box-shadow: 0 0 20px #111;}
    h1, h2, h3 {color: #FFFFFF;}
    .neon {text-shadow: 0 0 5px #00FFFF, 0 0 10px #00FFFF, 0 0 20px #00FFFF;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- HEADER ---
st.markdown("<h1 class='neon'>🚀 Live Crypto Dashboard</h1>", unsafe_allow_html=True)

# --- COINS TO DISPLAY ---
coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Binance Coin": "binancecoin"
}

# --- FUNCTION TO GET DATA FROM COINGECKO ---
def get_coin_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=true"
        r = requests.get(url, timeout=10).json()
        market_data = r['market_data']
        return {
            "Name": r['name'],
            "Symbol": r['symbol'].upper(),
            "Price": market_data['current_price']['usd'],
            "24h High": market_data['high_24h']['usd'],
            "24h Low": market_data['low_24h']['usd'],
            "24h Change %": market_data['price_change_percentage_24h'],
            "Market Cap": market_data['market_cap']['usd'],
            "Volume 24h": market_data['total_volume']['usd'],
            "Sparkline": market_data['sparkline_7d']['price'] if 'sparkline_7d' in market_data else None
        }
    except Exception as e:
        st.warning(f"Error fetching {coin_id} data: {e}")
        return None

# --- DISPLAY COINS ---
for coin_name, coin_id in coins.items():
    data = get_coin_data(coin_id)
    if data:
        st.subheader(f"{data['Name']} ({data['Symbol']})")
        # Create 5 columns for main metrics
        col1, col2, col3, col4, col5 = st.columns([2,1,1,1,2])
        
        # Price box
        col1.markdown(f"<div class='stMetric'><h3>Price</h3><h2 class='neon'>${data['Price']:,}</h2></div>", unsafe_allow_html=True)
        # 24h High
        col2.markdown(f"<div class='stMetric'><h4>24h High</h4><h3>${data['24h High']:,}</h3></div>", unsafe_allow_html=True)
        # 24h Low
        col3.markdown(f"<div class='stMetric'><h4>24h Low</h4><h3>${data['24h Low']:,}</h3></div>", unsafe_allow_html=True)
        # 24h Change %
        change_val = data['24h Change %']
        arrow = "▲" if change_val >= 0 else "▼"
        change_color = "lime" if change_val >= 0 else "red"
        col4.markdown(f"<div class='stMetric'><h4>24h Change</h4><h3 style='color:{change_color};'>{arrow} {change_val:.2f}%</h3></div>", unsafe_allow_html=True)
        # Volume + Market Cap
        col5.markdown(
            f"<div class='stMetric'><h4>Volume 24h</h4><h5>${data['Volume 24h']:,}</h5><h4>Market Cap</h4><h5>${data['Market Cap']:,}</h5></div>",
            unsafe_allow_html=True
        )
        
        # --- SPARKLINE CHART ---
        if data['Sparkline']:
            spark_df = pd.DataFrame({
                "price": data['Sparkline'],
                "time": pd.date_range(end=datetime.now(), periods=len(data['Sparkline']))
            })
            chart = alt.Chart(spark_df).mark_line(color="#00FFFF").encode(
                x="time:T",
                y="price:Q"
            ).properties(height=100)
            st.altair_chart(chart, use_container_width=True)
