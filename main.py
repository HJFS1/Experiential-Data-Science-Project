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
