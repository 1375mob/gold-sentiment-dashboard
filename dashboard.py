import pandas as pd
import altair as alt
import streamlit as st

# Page config
st.set_page_config(page_title="ToroFX Gold Sentiment Dashboard", layout="wide")

st.title("📊 ToroFX Market Sentiment Dashboard - Gold (XAUUSD)")

# --- Sample Data (you can update this manually or automate later) ---
futures_data = pd.DataFrame({
    'Date': ['Mar 26', 'Mar 27', 'Mar 28'],
    'Price': [2188.4, 2204.7, 2221.3],
    'Volume': [239000, 248000, 250631],
    'Open Interest': [467637, 512637, 574824],
    'OI Change': [17500, 45000, 62187],
    'Deliveries': [88, 123, 521],
    'Block Trades': [1967, 2453, 3071]
})

# Calculate %
futures_data['% OI Change'] = futures_data['Open Interest'].pct_change().fillna(0) * 100
futures_data['% Volume Change'] = futures_data['Volume'].pct_change().fillna(0) * 100

# Signal Logic
futures_data['Signal'] = futures_data.apply(
    lambda row: "📈 Bullish Spike" if row['% OI Change'] > 5 and row['% Volume Change'] > 2
    else ("⚠️ OI Drop" if row['% OI Change'] < -3 else "🔄 Stable"), axis=1)

# Sentiment Score (-1 to +1)
futures_data['Sentiment Score'] = futures_data.apply(lambda row: round(min(max(
    row['% OI Change']/10 + row['% Volume Change']/20 + row['Block Trades']/1000 + row['Deliveries']/1000, -1), 1), 2), axis=1)

# AI Commentary
def generate_commentary(row):
    if row['Signal'] == "📈 Bullish Spike":
        return f"On {row['Date']}, market sentiment turned notably bullish as open interest and trading volume increased significantly. Gold prices advanced to ${row['Price']}, reflecting strong institutional participation."
    elif row['Signal'] == "⚠️ OI Drop":
        return f"On {row['Date']}, a decline in open interest was observed while gold prices remained near ${row['Price']}, indicating potential profit-taking or position unwinding."
    else:
        return f"On {row['Date']}, gold markets exhibited stability around ${row['Price']}, with no significant shifts in open interest or volume to indicate directional conviction."

futures_data['Commentary'] = futures_data.apply(generate_commentary, axis=1)

# --- Dashboard Layout ---
col1, col2 = st.columns([3, 2])

# Chart
