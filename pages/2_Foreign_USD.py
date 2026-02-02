import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

st.set_page_config(page_title="Global Reserves", page_icon="🌍")
st.title("🌍 Global Reserve Composition")
st.caption("USD Share of Total Global Foreign Exchange Reserves")

@st.cache_data
def get_fred_data(series_id):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = ['Date', series_id]
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            return df
    except:
        return None

# Series IDs for Currency Shares of Global Reserves
# USD Share (COFER)
df_usd = get_fred_data("RRGRAUSRT") 
# Euro Share (Starts 1999)
df_euro = get_fred_data("RRGRALERURT")
# Yen Share
df_yen = get_fred_data("RRGRALJPYRT")

with st.spinner('Loading Global Reserve Data...'):
    if df_usd is not None:
        # Combining data
        df = df_usd.copy()
        if df_euro is not None: df = df.join(df_euro)
        if df_yen is not None: df = df.join(df_yen)
        
        # Clean names for the legend
        df.columns = ['US Dollar', 'Euro', 'Japanese Yen']
        
        # Plotting
        fig, ax = plt.subplots(figsize=(10, 6))
        for col in df.columns:
            ax.plot(df.index, df[col], label=f"{col} %", lw=2)
        
        ax.set_ylim(0, 100) # Percentage scale
        ax.set_ylabel("Share of Allocated Reserves (%)")
        ax.set_title("Currency Composition of Global Reserves")
        ax.grid(True, alpha=0.2)
        ax.legend()
        
        st.pyplot(fig, use_container_width=True)
        
        # Latest Stats
        st.subheader("Latest Global Allocation")
        latest = df.iloc[-1].dropna()
        cols = st.columns(len(latest))
        for i, (currency, val) in enumerate(latest.items()):
            cols[i].metric(currency, f"{val:.1f}%")
            
        st.info("Note: Individual country breakdowns (e.g., 'What % of China's reserves are USD?') are not publicly disclosed by central banks.")
    else:
        st.error("Could not fetch global reserve data.")
