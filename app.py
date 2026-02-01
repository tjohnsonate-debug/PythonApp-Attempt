import streamlit as st
import pandas as pd
import numpy as np

# Page config makes it look better on mobile
st.set_page_config(page_title="My iPhone Dashboard", layout="centered")

st.title("📱 My Dashboard")

# Metric cards look great on mobile
col1, col2 = st.columns(2)
col1.metric("Temperature", "72°F", "1.2°F")
col2.metric("Stock Price", "$154.20", "-0.5%")

st.subheader("Weekly Activity")
# Sample data for a chart
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Steps', 'Water', 'Sleep']
)
st.line_chart(chart_data)

if st.button('Refresh Data'):
    st.success("Data Updated!")
