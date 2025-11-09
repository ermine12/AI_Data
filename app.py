import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import zscore
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Benin Solar EDA",
    page_icon="☀️",
    layout="wide"
)

# --- Constants & File Paths ---
FILE_PATH = './data/benin-malanville.csv'
CLEAN_EXPORT_PATH = 'data/benin_clean.csv'
DAYTIME_GHI_THRESHOLD = 5  # GHI > 5 W/m^2 is considered 'daytime'

# --- Helper Functions ---

@st.cache_data
def load_data(filepath):
    """Loads and caches the raw data."""
    if not os.path.exists(filepath):
        st.error(f"Error: File not found at {filepath}")
        return None
    df = pd.read_csv(filepath)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.set_index('Timestamp')
    return df

@st.cache_data
def perform_cleaning(df_raw):
    """
    Applies the "best one" cleaning strategy:
    1. Imputes weather variables with median.
    2. Drops rows with null solar data during the day.
    """
    df = df_raw.copy()
    
    # 1. Impute weather-related columns with their median
    impute_cols = ['Tamb', 'RH', 'WS', 'WSgust', 'WSstdev', 'WD', 'WDstdev', 'BP', 'TModA', 'TModB']
    for col in impute_cols:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
    
    # 2. Drop rows where key solar data is missing *during the day*
    daytime_nulls = df[(df['GHI'] > DAYTIME_GHI_THRESHOLD) & (df['GHI'].isna() | df['DNI'].isna())].index
    df = df.drop(daytime_nulls)
    
    return df

@st.cache_data
def calculate_outliers(df, cols):
    """Calculates Z-scores and flags outliers."""
    df_outlier = df.copy()
    for col in cols:
        if col in df.columns:
            df_outlier[f'{col}_zscore'] = np.abs(zscore(df_outlier[col], nan_policy='omit'))
    
    # Flag rows where any Z-score is > 3
    z_cols = [f'{col}_zscore' for col in cols if f'{col}_zscore' in df_outlier.columns]
    df_outlier['is_outlier'] = (df_outlier[z_cols] > 3).any(axis=1)
    return df_outlier

# --- Main Application ---
st.title("☀️ Exploratory Data Analysis: Benin (Malanville)")
st.markdown(f"Analysis of `{FILE_PATH}` for the `eda-benin` branch.")

# Load Data
df_raw = load_data(FILE_PATH)
if df_raw is None:
    st.stop()

# --- 1. Summary Statistics & Missing-Value Report ---
st.header("1. Summary Statistics & Missing Values")
st.markdown("Full descriptive statistics for all numeric columns.")
st.dataframe(df_raw.describe())

st.subheader("Missing Value Report")
missing_values = df_raw.isna().sum()
missing_percent = (missing_values / len(df_raw) * 100).round(2)
missing_report = pd.DataFrame({'Null Count': missing_values, 'Null %': missing_percent})
st.dataframe(missing_report)

cols_over_5_percent = missing_report[missing_report['Null %'] > 5].index.tolist()
if cols_over_5_percent:
    st.warning(f"Columns with >5% missing data: {', '.join(cols_over_5_percent)}")
else:
    st.success("No columns have more than 5% missing data.")

# --- 2. Outlier Detection & Basic Cleaning ---
st.header("2. Outlier Detection & Basic Cleaning")

# Apply cleaning strategy
df_clean = perform_cleaning(df_raw)

# Calculate outliers on the cleaned data
outlier_cols = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'WS', 'WSgust']
df_clean = calculate_outliers(df_clean, outlier_cols)

st.subheader("Outlier Report (Z-Score > 3)")
outlier_count = df_clean['is_outlier'].sum()
st.metric("Total Outlier Rows Detected", f"{outlier_count} ({outlier_count / len(df_clean) * 100:.2f}%)")
with st.expander("View rows flagged as outliers"):
    st.dataframe(df_clean[df_clean['is_outlier']])

# Export the cleaned DataFrame
os.makedirs('data', exist_ok=True)
df_clean.to_csv(CLEAN_EXPORT_PATH)
st.success(f"Cleaned data exported to `{CLEAN_EXPORT_PATH}`")

# --- 3. Time Series Analysis ---
st.header("3. Time Series Analysis")
st.markdown("Line charts of key variables over time. Data is resampled to daily mean ('D') for performance.")

# Resample for plotting
df_daily = df_clean.resample('D').mean(numeric_only=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Solar Irradiance (GHI, DNI, DHI)")
    fig_solar_ts = px.line(df_daily, y=['GHI', 'DNI', 'DHI'], title="Daily Mean Solar Irradiance")
    st.plotly_chart(fig_solar_ts, use_container_width=True)
with col2:
    st.subheader("Ambient Temperature (Tamb)")
    fig_temp_ts = px.line(df_daily, y='Tamb', title="Daily Mean Ambient Temperature")
    st.plotly_chart(fig_temp_ts, use_container_width=True)

# Filter for daytime data for solar-specific analysis
df_daytime = df_clean[df_clean['GHI'] > DAYTIME_GHI_THRESHOLD].copy()
st.info(f"Solar-specific analysis (correlations, scatters) will use **daytime data only** ({len(df_daytime)} rows where GHI > {DAYTIME_GHI_THRESHOLD} W/m²).")

# --- 4. Cleaning Impact (from original 'Cleaning' flag) ---
st.header("4. Impact of Original 'Cleaning' Flag")
st.markdown("This analyzes the `Cleaning` column from the *original* CSV file.")
if 'Cleaning' in df_raw.columns:
    impact_df = df_raw.groupby('Cleaning')[['ModA', 'ModB']].mean().reset_index()
    fig_impact = px.bar(impact_df, x='Cleaning', y=['ModA', 'ModB'], barmode='group', title="Average Module Output by Original Cleaning Flag")
    st.plotly_chart(fig_impact, use_container_width=True)
else:
    st.warning("Column 'Cleaning' not found in the original data.")

# --- 5. & 7. Correlation & Relationship Analysis ---
st.header("5. Correlation & Relationship Analysis (Daytime Data)")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Solar & Temperature Correlation Heatmap")
    corr_cols = ['GHI', 'DNI', 'DHI', 'TModA', 'TModB', 'Tamb', 'RH', 'WS']
    corr_matrix = df_daytime[corr_cols].corr()
    fig_heatmap = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation Heatmap (Daytime)")
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col2:
    st.subheader("RH vs. Ambient Temperature")
    fig_rh_tamb = px.scatter(df_daytime.sample(min(2000, len(df_daytime))), x='Tamb', y='RH', opacity=0.5,
                             title="RH vs. Tamb (Daytime Sample)")
    st.plotly_chart(fig_rh_tamb, use_container_width=True)

st.subheader("Wind & Solar Scatter Plots")
col1, col2 = st.columns(2)
with col1:
    fig_ws_ghi = px.scatter(df_daytime.sample(min(2000, len(df_daytime))), x='WS', y='GHI', opacity=0.3,
                            title="Wind Speed vs. GHI (Daytime Sample)")
    st.plotly_chart(fig_ws_ghi, use_container_width=True)
with col2:
    fig_rh_ghi = px.scatter(df_daytime.sample(min(2000, len(df_daytime))), x='RH', y='GHI', opacity=0.3,
                           title="Relative Humidity vs. GHI (Daytime Sample)")
    st.plotly_chart(fig_rh_ghi, use_container_width=True)


# --- 6. Wind & Distribution Analysis ---
st.header("6. Wind & Distribution Analysis")
st.markdown("Using the full cleaned dataset for wind analysis, and daytime data for solar histograms.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Wind Rose (All Data)")
    # Create bins for Wind Direction
    wd_bins = np.arange(0, 361, 45)
    wd_labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    df_clean['WD_Bin'] = pd.cut(df_clean['WD'], bins=wd_bins, labels=wd_labels, right=False)
    
    # Group by bins to get mean wind speed
    df_wind_rose = df_clean.groupby('WD_Bin')['WS'].mean().reset_index()
    
    fig_wind_rose = px.bar_polar(df_wind_rose, r='WS', theta='WD_Bin',
                                 title="Wind Rose (Mean Wind Speed by Direction)",
                                 template="plotly_dark", color='WS')
    st.plotly_chart(fig_wind_rose, use_container_width=True)

with col2:
    st.subheader("Histograms (Daytime GHI & All-Day Wind Speed)")
    fig_hist_ghi = px.histogram(df_daytime, x='GHI', title="GHI Distribution (Daytime)")
    st.plotly_chart(fig_hist_ghi, use_container_width=True)
    
    fig_hist_ws = px.histogram(df_clean, x='WS', title="Wind Speed Distribution (All Data)")
    st.plotly_chart(fig_hist_ws, use_container_width=True)

# --- 8. Bubble Chart ---
st.header("7. Temperature & Humidity Bubble Chart (Daytime)")
st.markdown("GHI vs. Ambient Temperature, with bubble size representing Relative Humidity (RH).")

# Use a smaller sample for the bubble chart for performance
df_sample = df_daytime.sample(min(2000, len(df_daytime)))
fig_bubble = px.scatter(df_sample, x='Tamb', y='GHI', size='RH', color='RH',
                        title="GHI vs. Tamb (Bubble Size = RH)",
                        hover_name=df_sample.index, size_max=15)
st.plotly_chart(fig_bubble, use_container_width=True)