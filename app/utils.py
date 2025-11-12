"""
Utility functions for data processing and visualization in the Solar Dashboard
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats


def load_country_data(country_name):
    """
    Load cleaned CSV data for a specific country.
    
    Args:
        country_name (str): Name of the country (Benin, Sierra Leone, or Togo)
    
    Returns:
        pd.DataFrame: Loaded and processed dataframe
    """
    file_mapping = {
        'Benin': 'data/benin_malanville_clean.csv',
        'Sierra Leone': 'data/sierra_leone_bumbuna_clean.csv',
        'Togo': 'data/togo_dapaong_clean.csv'
    }
    
    if country_name not in file_mapping:
        raise ValueError(f"Unknown country: {country_name}")
    
    df = pd.read_csv(file_mapping[country_name])
    df['Country'] = country_name
    
    # Parse timestamp if available
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    return df


def load_all_countries():
    """
    Load and combine data from all three countries.
    
    Returns:
        pd.DataFrame: Combined dataframe with all countries
    """
    countries = ['Benin', 'Sierra Leone', 'Togo']
    dfs = [load_country_data(country) for country in countries]
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df


def compute_summary_stats(df, metrics=['GHI', 'DNI', 'DHI']):
    """
    Compute summary statistics for specified metrics grouped by country.
    
    Args:
        df (pd.DataFrame): Combined dataframe
        metrics (list): List of metrics to analyze
    
    Returns:
        pd.DataFrame: Summary statistics table
    """
    summary_stats = []
    
    for country in df['Country'].unique():
        country_data = df[df['Country'] == country]
        
        for metric in metrics:
            if metric in country_data.columns:
                summary_stats.append({
                    'Country': country,
                    'Metric': metric,
                    'Mean': country_data[metric].mean(),
                    'Median': country_data[metric].median(),
                    'Std Dev': country_data[metric].std(),
                    'Min': country_data[metric].min(),
                    'Max': country_data[metric].max()
                })
    
    return pd.DataFrame(summary_stats)


def create_boxplot(df, metric, countries=None):
    """
    Create an interactive boxplot for a specific metric across countries.
    
    Args:
        df (pd.DataFrame): Combined dataframe
        metric (str): Metric to plot (GHI, DNI, DHI)
        countries (list): List of countries to include (None for all)
    
    Returns:
        plotly.graph_objects.Figure: Interactive boxplot
    """
    if countries:
        df_filtered = df[df['Country'].isin(countries)]
    else:
        df_filtered = df
    
    fig = px.box(
        df_filtered,
        x='Country',
        y=metric,
        color='Country',
        title=f'{metric} Distribution by Country',
        labels={metric: f'{metric} (W/m²)', 'Country': 'Country'},
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
    )
    
    fig.update_layout(
        showlegend=False,
        height=500,
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig


def create_bar_chart(df, metric, top_n=3):
    """
    Create a bar chart ranking countries by average metric value.
    
    Args:
        df (pd.DataFrame): Combined dataframe
        metric (str): Metric to rank (GHI, DNI, DHI)
        top_n (int): Number of top countries to display
    
    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    avg_values = df.groupby('Country')[metric].mean().sort_values(ascending=False).head(top_n)
    
    fig = go.Figure(data=[
        go.Bar(
            x=avg_values.index,
            y=avg_values.values,
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1'][:len(avg_values)],
            text=avg_values.values.round(2),
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f'Average {metric} by Country',
        xaxis_title='Country',
        yaxis_title=f'Average {metric} (W/m²)',
        height=450,
        showlegend=False,
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig


def create_time_series(df, metric, country=None):
    """
    Create a time series plot for a specific metric.
    
    Args:
        df (pd.DataFrame): Dataframe with timestamp column
        metric (str): Metric to plot
        country (str): Specific country to filter (None for all)
    
    Returns:
        plotly.graph_objects.Figure: Time series plot
    """
    if country:
        df_filtered = df[df['Country'] == country].copy()
    else:
        df_filtered = df.copy()
    
    if 'Timestamp' not in df_filtered.columns:
        return None
    
    # Sample data if too large
    if len(df_filtered) > 10000:
        df_filtered = df_filtered.sample(n=10000).sort_values('Timestamp')
    
    fig = px.line(
        df_filtered,
        x='Timestamp',
        y=metric,
        color='Country' if not country else None,
        title=f'{metric} Time Series{" - " + country if country else ""}',
        labels={metric: f'{metric} (W/m²)', 'Timestamp': 'Date/Time'},
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
    )
    
    fig.update_layout(
        height=500,
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig


def perform_anova_test(df, metric='GHI'):
    """
    Perform one-way ANOVA test on a metric across countries.
    
    Args:
        df (pd.DataFrame): Combined dataframe
        metric (str): Metric to test
    
    Returns:
        dict: Test results including F-statistic and p-value
    """
    countries = df['Country'].unique()
    groups = [df[df['Country'] == country][metric].dropna() for country in countries]
    
    f_stat, p_value = stats.f_oneway(*groups)
    
    return {
        'metric': metric,
        'f_statistic': f_stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }


def create_correlation_heatmap(df, country=None):
    """
    Create a correlation heatmap for solar metrics.
    
    Args:
        df (pd.DataFrame): Dataframe
        country (str): Specific country to filter (None for all)
    
    Returns:
        plotly.graph_objects.Figure: Heatmap
    """
    if country:
        df_filtered = df[df['Country'] == country]
    else:
        df_filtered = df
    
    # Select numeric columns of interest
    columns = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS']
    available_columns = [col for col in columns if col in df_filtered.columns]
    
    if not available_columns:
        return None
    
    corr_matrix = df_filtered[available_columns].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title=f'Correlation Matrix{" - " + country if country else ""}',
        height=500,
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig


def get_top_regions(df, metric='GHI', n=5):
    """
    Get top N countries/regions by average metric value.
    
    Args:
        df (pd.DataFrame): Combined dataframe
        metric (str): Metric to rank by
        n (int): Number of top regions to return
    
    Returns:
        pd.DataFrame: Top regions with average values
    """
    top_regions = df.groupby('Country')[metric].agg(['mean', 'median', 'std']).round(2)
    top_regions = top_regions.sort_values('mean', ascending=False).head(n)
    top_regions.columns = ['Average', 'Median', 'Std Dev']
    return top_regions.reset_index()
