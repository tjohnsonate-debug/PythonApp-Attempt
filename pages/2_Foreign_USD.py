import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

st.set_page_config(page_title="Global Reserves", page_icon="🌍")
st.title("🌍 Global USD Demand")
st.markdown("### US Dollar Assets Held by Foreign Authorities")
st.caption("A proxy for global central bank USD reserves held at the Fed.")

@st.cache_data
def get_reliable_fred_data(series_id):
    # This URL uses the standard FRED export format
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            date_col = df.columns[0]
            df[date_col] = pd.to_datetime(df[date_col])
            df.set_index(date_col, inplace=True)
            df[series_id] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
            return df
        return None
    except:
        return None

with st.spinner('Accessing Fed Balance Sheet...'):
    # WRESBAL = Reserve Bank Credit: US Dollar Assets Held for Foreign/International Accounts
    df = get_reliable_fred_data("WRESBAL")

if df is not None:
    # 1. Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    # Scale to Billions for easier reading
    df_billions = df / 1000 
    ax.plot(df_billions.index, df_billions["WRESBAL"], color="#2a9d8f", lw=2)
    
    ax.set_ylabel("Billions of USD")
    ax.set_title("Total USD Reserves Held at the Fed")
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig, use_container_width=True)

    # 2. Stats
    current_val = df_billions["WRESBAL"].iloc[-1]
    prev_val = df_billions["WRESBAL"].iloc[-52] # 1 year ago
    delta = current_val - prev_val
    
    st.metric("Total USD Holdings", f"${current_val:,.0f}B", f"{delta:,.0f}B vs Last Year")
    
    st.info("Note: This tracks 'Custody Holdings'—the actual dollars global central banks store at the NY Fed. It is the most transparent real-time measure of USD reserve demand.")

else:
    st.error("Data connection failed. Please ensure 'requests' is in your requirements.txt.")
