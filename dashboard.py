import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# --- AUTO REFRESH EVERY 5 SECONDS ---
st_autorefresh(interval=5000, key="btc_refresh")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Live BTC Dashboard", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    .big-font {
        font-size: 48px !important;
        font-weight: bold;
    }
    .metric-label {
        font-size: 18px !important;
        color: #a1a1a1;
    }
    .metric-value {
        font-size: 36px !important;
    }
    .green {
        color: #00ff00;
        font-weight: bold;
    }
    .red {
        color: #ff4c4c;
        font-weight: bold;
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
    except Exception as e:
        return "Error", "Error", "Error", "Error"

# --- FETCH BTC DATA ---
price, change_24h, low_24h, high_24h = get_btc_data()

# --- DISPLAY BTC PRICE ---
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"<div class='big-font'>${price}</div>", unsafe_allow_html=True)
with col2:
    change_color = "green" if isinstance(change_24h, (int, float)) and change_24h >= 0 else "red"
    st.markdown(f"<div class='{change_color}'>24h: {change_24h}%</div>", unsafe_allow_html=True)

st.markdown(f"<div class='metric-label'>24h Low: ${low_24h} | 24h High: ${high_24h}</div>", unsafe_allow_html=True)
