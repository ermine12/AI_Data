# ☀️ Data Analysis for Solar Farm Feasibility: Benin (Malanville)

## Overview

This repository contains the complete Exploratory Data Analysis (EDA) and Predictive Modeling performed on minute-by-minute solar irradiance and meteorological data for the Malanville site in Benin. The goal is to assess site viability for a utility-scale PV (Photovoltaic) project and identify key environmental constraints that impact efficiency.

The analysis demonstrates proficiency in data cleaning, statistical rigor, and translating analytical findings into **actionable engineering recommendations** that maximize solar energy production.

-----

## Key Project Artifacts

The project deliverables are organized into the following files, showcasing the end-to-end data science process:

| File Name | Description | Status | Contribution Demonstrated |
| :--- | :--- | :--- | :--- |
| **`benin_eda.ipynb`** | **Jupyter Notebook.** Contains the step-by-step code for data loading, quality checks (Z-score outlier detection), data imputation, and initial correlation analysis. | **EDA Complete** | Proactivity, EDA Techniques, and Statistical Understanding. |
| **`model.py`** | **Predictive Regression Model.** Quantifies power loss by using GHI and TModA to predict power output (`ModA`). | **Predictive Modeling** | Quantifying statistical findings for actionable engineering insights. |
| **`time_series_analysis.py`**| **Time Series Decomposition.** Isolates long-term panel degradation (Trend) and seasonal performance cycles. | **Advanced Analysis** | Isolating time-based effects beyond simple correlation. |
| **`eda_report.md`** | **Executive Summary.** A formal report summarizing the findings, statistical evidence, and the most crucial actionable insight. | **Documentation** | Clear communication and presentation of results. |
| **`app.py`** | **Streamlit Web Application.** An interactive dashboard used for initial data visualization and summary statistics. | **Visualization** | Ability to deploy interactive tools for data exploration. |
| **`data/`** | Contains the raw source data (`benin-malanville.csv`) used for all analysis. | **Source Data** | |

-----

## Project Methodology and Key Findings (KPIs)

### 1\. Statistical Understanding & Outlier Handling

  * **Technique:** Used **Median Imputation** for minor weather variable gaps and applied **Z-score $\mathbf{> 3}$** criteria to identify and filter outliers across key solar and power columns (GHI, DNI, ModA, ModB).
  * **Result:** Verified the dataset is clean and statistically robust, with only a minor percentage of anomalies, making it reliable for advanced modeling.

### 2\. Actionable Insight: Thermal Constraint

The core contribution of this EDA was the identification of the primary efficiency constraint:

  * **Evidence:** The correlation analysis showed the strongest statistical relationship was between **GHI** (energy input) and **TModA** (Module Temperature) with a high coefficient of **$0.88$**.
  * **Actionable Recommendation:** The **`model.py`** script quantifies this problem. Its resulting negative coefficient for **TModA** provides the economic basis for investing in thermal mitigation strategies (e.g., cooling systems or high-temperature-tolerant panels) to maximize long-term energy yield.

### 3\. Solar Potential Assessment

  * **Finding:** The site exhibits excellent solar potential, with an estimated average daily energy yield of **$5.76$ kWh/m$^2$**. This validates the initial viability of the Malanville location for large-scale PV investment.

-----

## Running the Code

To replicate the analysis, clone the repository and execute the Python scripts.

1.  **Clone the Repository:**

    ```bash
    git clone [YOUR GITHUB LINK HERE]
    cd solar-eda-benin
    ```

2.  **Ensure Data is Present:**
    Place the `benin-malanville.csv` file inside a folder named `data/` at the project root.

3.  **Install Dependencies:**

    ```bash
    pip install pandas numpy scikit-learn statsmodels streamlit
    ```

4.  **Run the Predictive Model (Key Insight):**

    ```bash
    python model.py
    ```

    *(This script prints the crucial TModA coefficient to the console.)*

5.  **Run the Time Series Analysis (Trend Insight):**

    ```bash
    python time_series_analysis.py
    ```

    *(This script generates the decomposition plot for trend and seasonality.)*

6.  **View the EDA Dashboard (Optional):**

    ```bash
    streamlit run app.py
    ```