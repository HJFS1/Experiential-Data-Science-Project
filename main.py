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

# ─────────────────────────── TABS ─────────────────────────────────
tab1, tab2 = st.tabs(["📊 Bar Chart", "📋 Data Table"])

with tab1:
    # --- Bar chart of the selected metric ---
    mean_df = filtered.groupby("RegionName")[selected_metric].mean().reset_index()

    fig_bar = px.bar(
        mean_df.sort_values(selected_metric, ascending=False),
        x="RegionName",
        y=selected_metric,
        color="RegionName",
        title=f"Mean {selected_label} by Borough",
        labels={"RegionName": "RegionName", selected_metric: selected_label},
    )
    fig_bar.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    # --- Raw data table ---
    st.dataframe(
        filtered.sort_values("RegionName"),
        use_container_width=True,
        hide_index=True,
    )
    # Download button
    csv = filtered.to_csv(index=False)
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv,
        file_name="filtered_boroughs.csv",
        mime="text/csv",
    )

# ───────────── PRICE INDEX OVER TIME ───────────────

st.divider()
st.subheader("📈 Price Index Over Time")
st.caption("Shows growth per property type for a single borough.")
 
price_cols = {
    "Detached":      "DetachedPrice",
    "Semi-detached": "SemiDetachedPrice",
    "Terraced":      "TerracedPrice",
    "Flat":          "FlatPrice",
}
 
# Controls
ctrl_col1, ctrl_col2 = st.columns([2, 1])
 
with ctrl_col1:
    trend_borough = st.selectbox(
        "Select borough",
        options=sorted(df["RegionName"].unique()),
        index=sorted(df["RegionName"].unique()).index("Tower Hamlets")
        if "Tower Hamlets" in df["RegionName"].unique() else 0,
    )
 
with ctrl_col2:
    available_years = sorted(df["Date"].dt.year.unique())
    base_year = st.selectbox(
        "Base year (index = 100)",
        options=available_years,
        index=available_years.index(2015) if 2015 in available_years else 0,
    )
 
# Build indexed series
borough_df = (
    df[df["RegionName"] == trend_borough]
    .copy()
    .sort_values("Date")
)
borough_df["Year"] = borough_df["Date"].dt.year
annual_df = borough_df.groupby("Year")[list(price_cols.values())].mean().reset_index()
 
base_row = annual_df[annual_df["Year"] == base_year]
 
if base_row.empty:
    st.warning(f"No data found for {trend_borough} in {base_year}. Choose a different base year.")
else:
    indexed_df = annual_df[annual_df["Year"] >= base_year].copy()
    for label, col in price_cols.items():
        base_val = base_row[col].values[0]
        indexed_df[label] = (indexed_df[col] / base_val * 100).round(1)
 
    latest_year  = indexed_df["Year"].max()
    prev_year    = latest_year - 1
    latest_row   = annual_df[annual_df["Year"] == latest_year]
    prev_row     = annual_df[annual_df["Year"] == prev_year]
 
    kpi_cols = st.columns(4)
    for i, (label, col) in enumerate(price_cols.items()):
        with kpi_cols[i]:
            curr_val = latest_row[col].values[0] if not latest_row.empty else None
            prev_val = prev_row[col].values[0]   if not prev_row.empty  else None
            base_val = base_row[col].values[0]
 
            if curr_val and prev_val:
                yoy_delta = ((curr_val - prev_val) / prev_val * 100)
                total_chg = ((curr_val - base_val) / base_val * 100)
                st.metric(
                    label=f"{label}",
                    value=f"£{curr_val:,.0f}",
                    delta=f"{yoy_delta:+.1f}% YoY",
                )
                st.caption(f"{total_chg:+.1f}% since {base_year}")
 
    #Chart 
    plot_df = indexed_df[["Year"] + list(price_cols.keys())].melt(
        id_vars="Year",
        var_name="Property type",
        value_name="Index",
    )
 
    color_map = {
        "Detached":      "#185FA5",
        "Semi-detached": "#1D9E75",
        "Terraced":      "#D85A30",
        "Flat":          "#7F77DD",
    }
 
    fig_line = px.line(
        plot_df,
        x="Year",
        y="Index",
        color="Property type",
        color_discrete_map=color_map,
        markers=True,
        title=f"Price index for {trend_borough}",
        labels={"Index": f"Index ({base_year})", "Year": "Year"},
    )
 
    # Baseline reference at 100
    fig_line.add_hline(
        y=100,
        line_dash="dot",
        line_color="rgba(100,100,100,0.4)",
        annotation_text=f"Base ({base_year})",
        annotation_position="bottom right",
    )
 
    fig_line.update_layout(
        hovermode="x unified",
        xaxis=dict(tickmode="linear", dtick=1),
        yaxis=dict(title=f"Index ({base_year} = 100)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig_line.update_traces(line_width=2.5, marker_size=5)
 
    st.plotly_chart(fig_line, use_container_width=True)
 
    # Annual Averages
    with st.expander("View annual average prices for this borough"):
        display_df = annual_df[annual_df["Year"] >= base_year][
            ["Year"] + list(price_cols.values())
        ].copy()
        display_df.columns = ["Year"] + list(price_cols.keys())
        for col in price_cols.keys():
            display_df[col] = display_df[col].apply(lambda x: f"£{x:,.0f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
 
# ─────────────────────────── FOOTER ────────────────────────────────
st.divider()
st.caption("Built with Streamlit · Data: Housing Price Index: Office of National Statistics ")
