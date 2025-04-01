import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="ToroFX Gold Dashboard", layout="wide")
st.title("📊 ToroFX Market Sentiment Dashboard - Gold (XAUUSD)")

uploaded_file = st.file_uploader("Upload your Gold Futures Excel file (.xls or .xlsx)", type=["xls", "xlsx"])

if uploaded_file:
    try:
        # Clean CME-style file by skipping headers
        raw_df = pd.read_excel(uploaded_file, skiprows=4)

        # Rename columns to standard names expected by the dashboard
        df = raw_df.rename(columns={
            'Futures': 'Date',
            'Total Volume': 'Volume',
            'At Close': 'Open Interest',
            'Deliveries': 'Deliveries',
            'Block Trades': 'Block Trades',
            'Change': 'OI Change'
        })

        # Drop rows where Volume or Open Interest is missing
        df = df.dropna(subset=['Date', 'Volume', 'Open Interest'])

        # Format and compute additional fields
        df['Date'] = df['Date'].astype(str)
        df['Price'] = None
        df['% OI Change'] = df['Open Interest'].pct_change().fillna(0) * 100
        df['% Volume Change'] = df['Volume'].pct_change().fillna(0) * 100

        df['Signal'] = df.apply(
            lambda row: "📈 Bullish Spike" if row['% OI Change'] > 5 and row['% Volume Change'] > 2
            else ("⚠️ OI Drop" if row['% OI Change'] < -3 else "🔄 Stable"), axis=1)

        df['Sentiment Score'] = df.apply(lambda row: round(min(max(
            row.get('% OI Change', 0)/10 + row.get('% Volume Change', 0)/20 + row.get('Block Trades', 0)/1000 + row.get('Deliveries', 0)/1000, -1), 1), 2), axis=1)

        def generate_commentary(row):
            if row['Signal'] == "📈 Bullish Spike":
                return f"On {row['Date']}, market sentiment turned notably bullish as open interest and trading volume increased significantly."
            elif row['Signal'] == "⚠️ OI Drop":
                return f"On {row['Date']}, a drop in open interest was observed, suggesting possible profit-taking or position unwinding."
            else:
                return f"On {row['Date']}, gold futures remained stable with no major changes in open interest or volume."

        df['Commentary'] = df.apply(generate_commentary, axis=1)

        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader("Open Interest & Volume")
            chart_data = df.copy()
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
            st.dataframe(df[['Date', 'Price', 'Signal', 'Sentiment Score']], use_container_width=True)

        st.subheader("AI-Generated Commentary")
        for _, row in df.iterrows():
            st.markdown(f"**{row['Date']}** — {row['Commentary']}")

    except Exception as e:
        st.error(f"Failed to process file. Reason: {e}")
else:
    st.info("Please upload a CME Gold Excel file with columns like: Futures, Total Volume, At Close, Deliveries, Block Trades, Change.")
