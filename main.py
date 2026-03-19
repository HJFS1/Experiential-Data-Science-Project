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
