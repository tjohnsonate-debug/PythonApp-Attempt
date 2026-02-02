import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

st.set_page_config(page_title="Global Reserves", page_icon="🌍")
st.title("🌍 Global Reserve Composition")
st.markdown("### USD Share of Global Foreign Exchange Reserves")

@st.cache_data
def get_fred_data(series_id):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            # FRED often uses 'DATE' or 'observation_date'
            date_col = df.columns[0]
            df[date_col] = pd.to_datetime(df[date_col])
            df.set_index(date_col, inplace=True)
            df[series_id] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
            return df[[series_id]]
    except:
        return None

# --- NEW SERIES IDs ---
# USD Share of Allocated Reserves (World)
# Note: FRED ID 'RRGRAUSRT' is the standard for World USD share percentage
with st.spinner('Fetching IMF Global Data...'):
    df_usd = get_fred_data("RRGRAUSRT")
    # Adding Gold as a comparison (Gold as % of Total Reserves)
    # This gives the "multiple lines" feel you wanted
    df_gold = get_fred_data("RRGRAAUVRT") 

if df_usd is not None:
    # Combine data
    df = df_usd.rename(columns={"RRGRAUSRT": "US Dollar Share (%)"})
    if df_gold is not None:
        df["Gold Share (%)"] = df_gold["RRGRAAUVRT"]

    # 1. Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df.index, df["US Dollar Share (%)"], label="US Dollar", color="#1f77b4", lw=2.5)
    if "Gold Share (%)" in df.columns:
        ax.plot(df.index, df["Gold Share (%)"], label="Gold", color="#ffd700", lw=2)

    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Global Reserve Composition (Allocated Shares)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig, use_container_width=True)

    # 2. Stats for iPhone
    st.subheader("Current Snapshot")
    c1, c2 = st.columns(2)
    latest_usd = df["US Dollar Share (%)"].dropna().iloc[-1]
    c1.metric("USD Share", f"{latest_usd:.1f}%")
    
    if "Gold Share (%)" in df.columns:
        latest_gold = df["Gold Share (%)"].dropna().iloc[-1]
        c2.metric("Gold Share", f"{latest_gold:.1f}%")

    st.info("The USD share has trended down from ~70% in the early 2000s to ~58% today as central banks diversify.")
else:
    st.error("FRED is currently restricting access to the COFER series. Try refreshing in a few minutes or check your requirements.txt for 'requests'.")
