import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# --- AUTO REFRESH EVERY 5 SECONDS ---
st_autorefresh(interval=5000, key="crypto_refresh")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Live Crypto Dashboard", layout="wide")

st.title("🚀 Live Crypto Dashboard")

# --- FUNCTION TO FETCH COIN DATA SAFELY ---
def get_coin_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url)
        data = response.json()
        market_data = data.get('market_data')
        if market_data:
            price = market_data.get('current_price', {}).get('usd')
            change_24h = market_data.get('price_change_percentage_24h')
            low_24h = market_data.get('low_24h', {}).get('usd')
            high_24h = market_data.get('high_24h', {}).get('usd')
            return {
                "price": price if price is not None else "N/A",
                "change_24h": change_24h if change_24h is not None else "N/A",
                "low_24h": low_24h if low_24h is not None else "N/A",
                "high_24h": high_24h if high_24h is not None else "N/A"
            }
        else:
            return {"price": "N/A", "change_24h": "N/A", "low_24h": "N/A", "high_24h": "N/A"}
    except Exception as e:
        return {"price": "Error", "change_24h": "Error", "low_24h": "Error", "high_24h": "Error"}

# --- LIST OF COINS ---
coins = ["bitcoin", "ethereum", "binancecoin"]

# --- DISPLAY DATA IN DASHBOARD ---
for coin in coins:
    data = get_coin_price(coin)
    st.subheader(coin.capitalize())
    st.metric("Price (USD)", data["price"], delta=f"{data['change_24h']}%")
    st.write(f"24h Low: {data['low_24h']} USD | 24h High: {data['high_24h']} USD")
    st.markdown("---")
