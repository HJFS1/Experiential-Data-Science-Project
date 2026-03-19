import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────── PAGE CONFIG ───────────────────────────
st.set_page_config(
    page_title="East London Housing Prices Dashboard",
    page_icon="📊",
    layout="wide",
)

# ─────────────────────────── LOAD DATA ─────────────────────────────
@st.cache_data
def load_data(path: str):
  df = pd.read_csv(path)
  return df

df = load_data("UK-HPI-full-file-2025-10.csv")

df["Date"] = pd.to_datetime(df["Date"])

# ─────────────────────────── SIDEBAR FILTERS ───────────────────────
st.sidebar.header("🔧 Dashboard Filters")

# Borough selector
boroughs = st.sidebar.multiselect(
    "Select boroughs to compare",
    options=sorted(df["RegionName"].unique()),
    default=["Tower Hamlets", "Hackney", "Newham", "Southwark", "Barking and Dagenham", "Havering", "Redbridge", "Waltham Forest"],
)

# Metric selector
metric_options = {
    "Detached House Price": "DetachedPrice",
    "Semi Detached House Price": "SemiDetachedPrice",
    "Terraced House Price": "TerracedPrice",
    "Flat Price": "FlatPrice" 

}
selected_label = st.sidebar.selectbox("Primary metric", list(metric_options.keys()))

selected_metric = metric_options[selected_label]

# Apply filter
if boroughs:
    filtered = df[df["RegionName"].isin(boroughs)]
else:
    filtered = df

# ─────────────────────────── TITLE ─────────────────────────────────
st.title("📊 Housing Types average Price ")
st.caption("Comparing average price for different housing types")

# ─────────────────────────── KPI CARDS ─────────────────────────────
# Create 4 columns for average price for each property type
filtered = filtered[filtered["Date"].dt.year == 2025]

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_detached = filtered["DetachedPrice"].mean()
    st.metric("🏠 Detached House Price", f"£{avg_detached:,.0f}")

with col2:
    avg_semideteched = filtered["SemiDetachedPrice"].mean()
    st.metric("🏠 Semi Detached Price", f"£{avg_semideteched:,.0f}")

with col3:
    avg_terraced = filtered["TerracedPrice"].mean()
    st.metric("🏠 Terraced Housing Price", f"£{avg_terraced:,.0f}")

with col4:
    avg_flat = filtered["FlatPrice"].mean()
    st.metric("🏢 Flat Price", f"£{avg_flat:,.0f}")

st.divider()
