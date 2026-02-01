import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# 1. Page Config
st.set_page_config(page_title="US Debt Dashboard", page_icon="📈")
st.title("🇺🇸 US Debt/GDP Dashboard")
st.caption("Last 75 Years: Government vs Private Sector")

# 2. Data Fetching Function (Cached to make it fast!)
@st.cache_data
def get_fred_data(series_id):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        df = pd.read_csv(io.StringIO(response.text))
        date_col = 'observation_date' if 'observation_date' in df.columns else 'DATE'
        
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)
        df[series_id] = pd.to_numeric(df[series_id], errors='coerce')
        return df
    except:
        return None

# 3. Main Logic
with st.spinner('Fetching latest FRED data...'):
    df_gov = get_fred_data("GFDGDPA188S")
    df_private = get_fred_data("QUSPAM770A") or get_fred_data("TOTCCWG1USA300N")

if df_gov is not None and df_private is not None:
    # Processing
    df_gov.columns = ['Gov']
    df_private.columns = ['Private']

    # Resample to Yearly
    df_gov = df_gov.resample('YE').mean()
    df_private = df_private.resample('YE').mean()

    # Merge and filter
    df = pd.merge(df_gov, df_private, left_index=True, right_index=True)
    df = df.tail(75)

    # 4. Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df.index, df['Gov'], label='Gov Debt (% of GDP)', color='#e63946', lw=2)
    ax.plot(df.index, df['Private'], label='Private Debt (% of GDP)', color='#457b9d', lw=2)
    
    ax.set_ylabel("Percent of GDP (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()

    # Display in Streamlit
    st.pyplot(fig)

    # 5. Mobile-friendly Stats
    col1, col2 = st.columns(2)
    latest_gov = df['Gov'].iloc[-1]
    latest_priv = df['Private'].iloc[-1]
    col1.metric("Latest Gov Debt", f"{latest_gov:.1f}%")
    col2.metric("Latest Private Debt", f"{latest_priv:.1f}%")

    # Optional: Show raw data
    with st.expander("View Raw Data Table"):
        st.dataframe(df.sort_index(ascending=False))

else:
    st.error("Unable to load data from FRED. Please check your internet connection.")
