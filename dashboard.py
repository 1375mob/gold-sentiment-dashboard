import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="ToroFX Gold Dashboard", layout="wide")
st.title("📊 ToroFX Market Sentiment Dashboard - Gold (XAUUSD)")

uploaded_file = st.file_uploader("Upload your Gold Futures Excel file (.xls or .xlsx)", type=["xls", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded and loaded successfully.")

        # Fallback sample structure (adjust this based on your real Excel file)
        futures_data = pd.DataFrame({
            'Date': ['Mar 26', 'Mar 27', 'Mar 28'],
            'Price': [2188.4, 2204.7, 2221.3],
            'Volume': [239000, 248000, 250631],
            'Open Interest': [467637, 512637, 574824],
            'OI Change': [17500, 45000, 62187],
            'Deliveries': [88, 123, 521],
            'Block Trades': [1967, 2453, 3071]
        })

        futures_data['% OI Change'] = futures_data['Open Interest'].pct_change().fillna(0) * 100
        futures_data['% Volume Change'] = futures_data['Volume'].pct_change().fillna(0) * 100

        futures_data['Signal'] = futures_data.apply(
            lambda row: "📈 Bullish Spike" if row['% OI Change'] > 5 and row['% Volume Change'] > 2
            else ("⚠️ OI Drop" if row['% OI Change'] < -3 else "🔄 Stable"), axis=1)

        futures_data['Sentiment Score'] = futures_data.apply(lambda row: round(min(max(
            row['% OI Change']/10 + row['% Volume Change']/20 + row['Block Trades']/1000 + row['Deliveries']/1000, -1), 1), 2), axis=1)

        def generate_commentary(row):
            if row['Signal'] == "📈 Bullish Spike":
                return f"On {row['Date']}, market sentiment turned notably bullish as open interest and trading volume increased significantly."
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
            st.dataframe(futures_data[['Date', 'Price', 'Signal', 'Sentiment Score']], use_container_width=True)

        st.subheader("AI-Generated Commentary")
        for _, row in futures_data.iterrows():
            st.markdown(f"**{row['Date']}** — {row['Commentary']}")

    except Exception as e:
        st.error(f"Failed to process file. Reason: {e}")
else:
    st.info("Please upload a gold futures Excel file to begin.")
