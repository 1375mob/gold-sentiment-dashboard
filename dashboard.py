import pandas as pd
import altair as alt
import streamlit as st
import requests

st.set_page_config(page_title="ToroFX Gold Dashboard", layout="wide")
st.title("📊 ToroFX Market Sentiment Dashboard - Gold (XAUUSD)")

# Pull live data from CME JSON endpoint
try:
    st.info("Pulling live gold volume and open interest data from CME...")

    # Live endpoint for Gold Futures volume/OI data
    url = "https://www.cmegroup.com/CmeWS/mvc/Volume/OpenInterest/Details/FUT/G"
    response = requests.get(url)
    data = response.json()

    records = data['volumeOpenInterestRecords']

    # Parse relevant fields
    futures_data = pd.DataFrame([{
        'Date': r['tradeDate'],
        'Volume': int(r['volume'].replace(',', '')) if r['volume'] else 0,
        'Open Interest': int(r['openInterest'].replace(',', '')) if r['openInterest'] else 0,
        'Deliveries': int(r['deliveries'].replace(',', '')) if r['deliveries'] else 0,
        'Block Trades': int(r['blockTrades'].replace(',', '')) if r['blockTrades'] else 0,
        'Price': None  # Placeholder since price isn't in this feed
    } for r in records if r['productCode'] == 'GC'])

    futures_data = futures_data.sort_values(by='Date')
    futures_data['OI Change'] = futures_data['Open Interest'].diff().fillna(0)
    futures_data['% OI Change'] = futures_data['Open Interest'].pct_change().fillna(0) * 100
    futures_data['% Volume Change'] = futures_data['Volume'].pct_change().fillna(0) * 100

    futures_data['Signal'] = futures_data.apply(
        lambda row: "📈 Bullish Spike" if row['% OI Change'] > 5 and row['% Volume Change'] > 2
        else ("⚠️ OI Drop" if row['% OI Change'] < -3 else "🔄 Stable"), axis=1)

    futures_data['Sentiment Score'] = futures_data.apply(lambda row: round(min(max(
        row['% OI Change']/10 + row['% Volume Change']/20 + row['Block Trades']/1000 + row['Deliveries']/1000, -1), 1), 2), axis=1)

    def generate_commentary(row):
        if row['Signal'] == "📈 Bullish Spike":
            return f"On {row['Date']}, market sentiment turned notably bullish with open interest and volume rising significantly."
        elif row['Signal'] == "⚠️ OI Drop":
            return f"On {row['Date']}, a drop in open interest was observed, suggesting possible profit-taking or position unwinding."
        else:
            return f"On {row['Date']}, gold futures remained stable with no major changes in open interest or volume."

    futures_data['Commentary'] = futures_data.apply(generate_commentary, axis=1)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Open Interest & Volume")
        chart_data = futures_data.copy()
        chart_data['Date'] = pd.Categorical(chart_data['Date'], categories=chart_data['Date'], ordered=True)

        volume_bar = alt.Chart(chart_data).mark_bar(color="#40E0D0").encode(
            x=alt.X('Date:N', title='Date'),
            y=alt.Y('Volume:Q', title='Contracts'),
            tooltip=['Date', 'Volume']
        )

        oi_line = alt.Chart(chart_data).mark_line(color='orange', point=True).encode(
            x='Date:N',
            y='Open Interest:Q',
            tooltip=['Date', 'Open Interest']
        )

        st.altair_chart(volume_bar + oi_line, use_container_width=True)

    with col2:
        st.subheader("Daily Sentiment Metrics")
        st.dataframe(futures_data[['Date', 'Volume', 'Open Interest', 'Signal', 'Sentiment Score']], use_container_width=True)

    st.subheader("AI-Generated Commentary")
    for _, row in futures_data.iterrows():
        st.markdown(f"**{row['Date']}** — {row['Commentary']}")

except Exception as e:
    st.error(f"Failed to fetch live data. Reason: {e}")
