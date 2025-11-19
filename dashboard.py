# dashboard.py
import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# --- AUTO REFRESH EVERY 5 SECONDS ---
st_autorefresh(interval=5000, key="crypto_refresh")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Live BTC Dashboard", layout="wide")

# --- DARK THEME STYLING ---
st.markdown(
    """
    <style>
    body {background-color: #0E1117; color: #FFFFFF;}
    .stMetric {background-color: #1F222A; border-radius: 10px; padding: 15px; text-align:center;}
    .stText {color: #FFFFFF;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- FUNCTION TO FETCH LIVE BTC DATA FROM COINGECKO ---
def get_btc_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        response = requests.get(url, timeout=10).json()
        market_data = response['market_data']
        return {
            "Price": market_data['current_price']['usd'],
            "24h High": market_data['high_24h']['usd'],
            "24h Low": market_data['low_24h']['usd'],
            "24h Change %": market_data['price_change_percentage_24h']
        }
    except Exception as e:
        st.warning(f"Error fetching data: {e}")
        return None

btc_data = get_btc_data()

# --- DISPLAY DASHBOARD ---
if btc_data:
    st.title("🚀 Live BTC Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Price (USD)", f"${btc_data['Price']:.2f}")
    col2.metric("24h High", f"${btc_data['24h High']:.2f}")
    col3.metric("24h Low", f"${btc_data['24h Low']:.2f}")
    
    # Change % with color indicator
    change_val = btc_data['24h Change %']
    change_color = "green" if change_val >= 0 else "red"
    col4.markdown(
        f"<div class='stMetric'><h3 style='color:{change_color};'>{change_val:.2f}%</h3></div>",
        unsafe_allow_html=True
    )
else:
    st.warning("Could not load BTC data.")
