import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# --- AUTO REFRESH ---
st_autorefresh(interval=5000, key="btc_refresh")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Live BTC Dashboard", layout="wide")

# --- DARK THEME ---
st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    .price {
        font-size: 60px;
        font-weight: bold;
    }
    .change-positive {
        color: #00ff00;
        font-size: 28px;
        font-weight: bold;
    }
    .change-negative {
        color: #ff4c4c;
        font-size: 28px;
        font-weight: bold;
    }
    .metrics {
        font-size: 20px;
        color: #a1a1a1;
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("🚀 Live Bitcoin Dashboard")

# --- FUNCTION TO FETCH BTC DATA ---
def get_btc_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin"
    try:
        response = requests.get(url)
        data = response.json()
        market_data = data.get('market_data', {})
        price = market_data.get('current_price', {}).get('usd', "N/A")
        change_24h = market_data.get('price_change_percentage_24h', "N/A")
        low_24h = market_data.get('low_24h', {}).get('usd', "N/A")
        high_24h = market_data.get('high_24h', {}).get('usd', "N/A")
        return price, change_24h, low_24h, high_24h
    except:
        return "Error", "Error", "Error", "Error"

# --- FETCH DATA ---
price, change_24h, low_24h, high_24h = get_btc_data()

# --- DISPLAY ---
st.markdown(f"<div class='price'>${price}</div>", unsafe_allow_html=True)

change_class = "change-positive" if isinstance(change_24h, (int, float)) and change_24h >= 0 else "change-negative"
st.markdown(f"<div class='{change_class}'>24h: {change_24h}%</div>", unsafe_allow_html=True)

st.markdown(f"<div class='metrics'>24h Low: ${low_24h} | 24h High: ${high_24h}</div>", unsafe_allow_html=True)
