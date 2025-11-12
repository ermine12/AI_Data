"""
Solar Potential Dashboard - West African Countries
Interactive Streamlit application for visualizing solar irradiance data
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import (
    load_all_countries,
    compute_summary_stats,
    create_boxplot,
    create_bar_chart,
    create_time_series,
    perform_anova_test,
    create_correlation_heatmap,
    get_top_regions
)

# Page configuration
st.set_page_config(
    page_title="Solar Potential Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6B6B;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load data with caching for better performance"""
    return load_all_countries()


def main():
    # Header
    st.markdown('<p class="main-header">☀️ Solar Potential Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Comparative Analysis of Solar Irradiance: Benin, Sierra Leone & Togo</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data...'):
        df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Country selection
    st.sidebar.subheader("Select Countries")
    all_countries = df['Country'].unique().tolist()
    selected_countries = st.sidebar.multiselect(
        "Choose countries to compare:",
        options=all_countries,
        default=all_countries,
        help="Select one or more countries to analyze"
    )
    
    if not selected_countries:
        st.warning("⚠️ Please select at least one country to display data.")
        return
    
    # Filter data based on selection
    filtered_df = df[df['Country'].isin(selected_countries)]
    
    # Metric selection
    st.sidebar.subheader("Select Metric")
    metric = st.sidebar.selectbox(
        "Choose solar irradiance metric:",
        options=['GHI', 'DNI', 'DHI'],
        help="GHI: Global Horizontal Irradiance, DNI: Direct Normal Irradiance, DHI: Diffuse Horizontal Irradiance"
    )
    
    # Visualization type
    st.sidebar.subheader("Visualization Options")
    viz_type = st.sidebar.radio(
        "Select visualization:",
        options=['Boxplot', 'Bar Chart', 'Time Series', 'Correlation Heatmap'],
        help="Choose how to visualize the data"
    )
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visualizations", "📈 Statistics", "🔬 Analysis", "ℹ️ About"])
    
    with tab1:
        st.header("Data Visualizations")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="Countries Selected",
                value=len(selected_countries),
                delta=f"{len(selected_countries)}/{len(all_countries)}"
            )
        with col2:
            st.metric(
                label="Total Records",
                value=f"{len(filtered_df):,}",
                delta=f"{len(filtered_df)/len(df)*100:.1f}% of dataset"
            )
        with col3:
            avg_value = filtered_df[metric].mean()
            st.metric(
                label=f"Average {metric}",
                value=f"{avg_value:.2f} W/m²"
            )
        
        st.markdown("---")
        
        # Display selected visualization
        if viz_type == 'Boxplot':
            st.subheader(f"📦 {metric} Distribution Comparison")
            fig = create_boxplot(filtered_df, metric, selected_countries)
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("ℹ️ How to interpret this chart"):
                st.write("""
                - **Box**: Shows the interquartile range (25th to 75th percentile)
                - **Line in box**: Represents the median value
                - **Whiskers**: Extend to show the range of the data
                - **Dots**: Represent outlier values
                """)
        
        elif viz_type == 'Bar Chart':
            st.subheader(f"📊 Average {metric} by Country")
            fig = create_bar_chart(filtered_df, metric, len(selected_countries))
            st.plotly_chart(fig, use_container_width=True)
            
            # Show ranking table
            st.subheader("🏆 Country Rankings")
            ranking_df = get_top_regions(filtered_df, metric, len(selected_countries))
            st.dataframe(ranking_df, use_container_width=True)
        
        elif viz_type == 'Time Series':
            st.subheader(f"📈 {metric} Time Series")
            
            if len(selected_countries) == 1:
                country_for_ts = selected_countries[0]
            else:
                country_for_ts = None
            
            fig = create_time_series(filtered_df, metric, country_for_ts)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Time series data not available for this dataset")
        
        elif viz_type == 'Correlation Heatmap':
            st.subheader("🔥 Correlation Matrix")
            
            if len(selected_countries) == 1:
                country_for_corr = selected_countries[0]
            else:
                country_for_corr = None
            
            fig = create_correlation_heatmap(filtered_df, country_for_corr)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("ℹ️ Understanding correlations"):
                    st.write("""
                    - **Red colors**: Positive correlation (variables increase together)
                    - **Blue colors**: Negative correlation (one increases as other decreases)
                    - **Values close to 1 or -1**: Strong correlation
                    - **Values close to 0**: Weak or no correlation
                    """)
            else:
                st.warning("⚠️ Correlation data not available for this dataset")
    
    with tab2:
        st.header("Summary Statistics")
        
        # Compute summary stats
        summary_df = compute_summary_stats(filtered_df, ['GHI', 'DNI', 'DHI'])
        
        # Display by metric
        for metric_name in ['GHI', 'DNI', 'DHI']:
            st.subheader(f"{metric_name} Statistics")
            metric_stats = summary_df[summary_df['Metric'] == metric_name]
            
            if not metric_stats.empty:
                # Create columns for each country
                cols = st.columns(len(selected_countries))
                for idx, (_, row) in enumerate(metric_stats.iterrows()):
                    if row['Country'] in selected_countries:
                        with cols[idx % len(cols)]:
                            st.markdown(f"**{row['Country']}**")
                            st.metric("Mean", f"{row['Mean']:.2f} W/m²")
                            st.metric("Median", f"{row['Median']:.2f} W/m²")
                            st.metric("Std Dev", f"{row['Std Dev']:.2f}")
                            if 'Min' in row and 'Max' in row:
                                st.metric("Range", f"{row['Min']:.2f} - {row['Max']:.2f}")
            
            st.markdown("---")
        
        # Full statistics table
        st.subheader("📋 Complete Statistics Table")
        st.dataframe(summary_df[summary_df['Country'].isin(selected_countries)], use_container_width=True)
    
    with tab3:
        st.header("Statistical Analysis")
        
        st.subheader("🔬 ANOVA Test Results")
        st.write("Testing whether there are statistically significant differences between countries")
        
        # Perform ANOVA for each metric
        metrics_to_test = ['GHI', 'DNI', 'DHI']
        
        for test_metric in metrics_to_test:
            with st.expander(f"📊 {test_metric} Analysis"):
                if len(selected_countries) >= 2:
                    result = perform_anova_test(filtered_df, test_metric)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("F-statistic", f"{result['f_statistic']:.4f}")
                    with col2:
                        st.metric("P-value", f"{result['p_value']:.6f}")
                    with col3:
                        significance = "✅ Significant" if result['significant'] else "❌ Not Significant"
                        st.metric("Result", significance)
                    
                    if result['significant']:
                        st.success(f"""
                        **Interpretation:** The p-value ({result['p_value']:.6f}) is less than 0.05, 
                        indicating statistically significant differences in {test_metric} values between 
                        the selected countries.
                        """)
                    else:
                        st.info(f"""
                        **Interpretation:** The p-value ({result['p_value']:.6f}) is greater than 0.05, 
                        indicating no statistically significant differences in {test_metric} values between 
                        the selected countries.
                        """)
                else:
                    st.warning("⚠️ Please select at least 2 countries to perform ANOVA test")
        
        st.markdown("---")
        
        st.subheader("💡 Key Insights")
        
        # Calculate some insights
        top_ghi_country = filtered_df.groupby('Country')['GHI'].mean().idxmax()
        top_ghi_value = filtered_df.groupby('Country')['GHI'].mean().max()
        
        st.markdown(f"""
        - **Highest Solar Potential:** {top_ghi_country} shows the highest average GHI at {top_ghi_value:.2f} W/m²
        - **Dataset Coverage:** Analysis includes {len(filtered_df):,} records across {len(selected_countries)} countries
        - **Metrics Analyzed:** GHI (Global Horizontal Irradiance), DNI (Direct Normal Irradiance), DHI (Diffuse Horizontal Irradiance)
        """)
    
    with tab4:
        st.header("About This Dashboard")
        
        st.markdown("""
        ### 📖 Overview
        This interactive dashboard provides comprehensive analysis of solar irradiance data 
        from three West African countries: Benin, Sierra Leone, and Togo.
        
        ### 🎯 Purpose
        - Compare solar potential across different regions
        - Identify optimal locations for solar energy installations
        - Understand patterns and variations in solar irradiance
        - Support decision-making for renewable energy projects
        
        ### 📊 Metrics Explained
        
        **GHI (Global Horizontal Irradiance)**
        - Total solar radiation received on a horizontal surface
        - Best indicator for overall solar potential
        - Measured in W/m²
        
        **DNI (Direct Normal Irradiance)**
        - Solar radiation received perpendicular to the sun's rays
        - Important for concentrated solar power (CSP) systems
        - Measured in W/m²
        
        **DHI (Diffuse Horizontal Irradiance)**  
        - Solar radiation scattered by the atmosphere
        - Important for PV systems in cloudy conditions
        - Measured in W/m²
        
        ### 🛠️ Technologies Used
        - **Streamlit**: Interactive web application framework
        - **Plotly**: Interactive visualizations
        - **Pandas**: Data processing and analysis
        - **SciPy**: Statistical testing
        
        ### 📝 Data Sources
        Data has been cleaned and processed from solar measurement stations in:
        - Benin (Malanville)
        - Sierra Leone (Bumbuna)
        - Togo (Dapaong)
        
        ### 👥 Usage Instructions
        1. Select countries to compare using the sidebar
        2. Choose a metric (GHI, DNI, or DHI)
        3. Select visualization type
        4. Explore different tabs for detailed analysis
        
        ---
        
        **Note:** This dashboard reads data locally. Ensure CSV files are present in the `data/` directory.
        """)
        
        st.info("💡 **Tip:** Use the sidebar controls to customize your analysis and compare different countries and metrics.")


if __name__ == "__main__":
    main()
