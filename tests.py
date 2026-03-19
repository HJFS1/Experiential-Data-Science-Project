import pytest
import pandas as pd
import numpy as np
from io import StringIO


# ─────────────────────────── FIXTURES ──────────────────────────────

@pytest.fixture
def sample_df():
    data = {
        "Date": ["2015-01-01", "2016-01-01", "2020-01-01", "2025-01-01",
                 "2015-01-01", "2016-01-01", "2020-01-01", "2025-01-01"],
        "RegionName": ["Tower Hamlets"] * 4 + ["Hackney"] * 4,
        "DetachedPrice":     [400000, 450000, 550000, 620000, 380000, 420000, 510000, 590000],
        "SemiDetachedPrice": [300000, 330000, 400000, 460000, 290000, 320000, 390000, 445000],
        "TerracedPrice":     [280000, 310000, 370000, 420000, 265000, 295000, 355000, 405000],
        "FlatPrice":         [250000, 270000, 320000, 370000, 240000, 260000, 310000, 360000],
    }
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


@pytest.fixture
def df_2025(sample_df):
    return sample_df[sample_df["Date"].dt.year == 2025]


# ─────────────────────────── TESTS ─────────────────────────────────

def test_date_column_is_datetime(sample_df):
    assert pd.api.types.is_datetime64_any_dtype(sample_df["Date"])


def test_required_columns_present(sample_df):
    required = {"Date", "RegionName", "DetachedPrice", "SemiDetachedPrice", "TerracedPrice", "FlatPrice"}
    assert required.issubset(set(sample_df.columns))


def test_borough_filter(sample_df):
    filtered = sample_df[sample_df["RegionName"].isin(["Tower Hamlets"])]
    assert set(filtered["RegionName"].unique()) == {"Tower Hamlets"}


def test_year_filter_returns_2025_only(sample_df):
    filtered = sample_df[sample_df["Date"].dt.year == 2025]
    assert list(filtered["Date"].dt.year.unique()) == [2025]


def test_kpi_mean_flat_price(df_2025):
    assert df_2025["FlatPrice"].mean() == pytest.approx((370000 + 360000) / 2)


def test_groupby_produces_one_row_per_borough(df_2025):
    grouped = df_2025.groupby("RegionName")["FlatPrice"].mean().reset_index()
    assert len(grouped) == df_2025["RegionName"].nunique()


def test_price_index_base_year_is_100(sample_df):
    borough = sample_df[sample_df["RegionName"] == "Tower Hamlets"].copy()
    borough["Year"] = borough["Date"].dt.year
    annual = borough.groupby("Year")["FlatPrice"].mean().reset_index()
    base_val = annual.loc[annual["Year"] == 2015, "FlatPrice"].values[0]
    annual["Index"] = (annual["FlatPrice"] / base_val * 100).round(1)
    assert annual.loc[annual["Year"] == 2015, "Index"].values[0] == pytest.approx(100.0)


def test_price_index_grows_over_time(sample_df):
    borough = sample_df[sample_df["RegionName"] == "Tower Hamlets"].copy()
    borough["Year"] = borough["Date"].dt.year
    annual = borough.groupby("Year")["FlatPrice"].mean().reset_index()
    base_val = annual.loc[annual["Year"] == 2015, "FlatPrice"].values[0]
    indices = (annual.sort_values("Year")["FlatPrice"] / base_val * 100).tolist()
    assert indices == sorted(indices)


def test_nan_mean_uses_remaining_values(sample_df):
    df = sample_df.copy()
    df.loc[df["RegionName"] == "Hackney", "DetachedPrice"] = np.nan
    filtered = df[df["Date"].dt.year == 2025]
    assert filtered["DetachedPrice"].mean() == pytest.approx(620000.0)


def test_csv_export_preserves_shape(df_2025):
    reloaded = pd.read_csv(StringIO(df_2025.to_csv(index=False)))
    assert reloaded.shape == df_2025.shape
