**Project Handover Prompt: Multi-Site Solar Data Analysis**

**Objective:**
I am submitting three solar energy time-series datasets (CSV files) for a comprehensive Exploratory Data Analysis (EDA). The goal is to consolidate the analysis of all three sites into a single, cohesive, and easily reviewable output, such as a Python script or a Jupyter Notebook.

**Files Provided:**
1.  `benin-malanville.csv`
2.  `togo-dapaong_qc.csv`
3.  `sierraleone-bumbuna.csv`

**Required Data Processing and Methodology:**

For each of the three datasets, the analysis are:

1.  **Data Loading and Preprocessing:**
    * Load the data, ensuring the 'Timestamp' column is converted to datetime objects and set as the index.
    * Provide a data summary (`df.describe()`) and a missing value report (count and percentage).

2.  **Data Cleaning:**
    * **Imputation:** Impute all weather-related columns (`Tamb`, `RH`, `WS`, `WD`, `BP`, `TModA`, `TModB`, etc.) using their respective **median** values.
    * **Daytime Null Handling:** Drop any rows where key solar variables (`GHI` or `DNI`) are null, but the `GHI` reading is greater than 5 W/m² (the daytime threshold).

3.  **Outlier Detection:**
    * Calculate the Z-score for key variables (`GHI`, `DNI`, `DHI`, `ModA`, `ModB`, `WS`, `WSgust`).
    * Flag any data points where the absolute Z-score is greater than 3 as an outlier. Report the total number and percentage of outlier rows detected.

4.  **Visualization and Analysis (Apply to all three sites):**
    * **Time Series:** Plot the daily mean time series for Solar Irradiance (`GHI`, `DNI`, `DHI`) and Ambient Temperature (`Tamb`).
    * **Correlation:** Generate a correlation heatmap (e.g., for `GHI`, `DNI`, `DHI`, `Tamb`, `RH`, `WS`) using **daytime data only** (where GHI > 5 W/m²).
    * **Relationship Scatters (Daytime Only):** Create scatter plots for `WS` vs. `GHI` and `RH` vs. `GHI`.
    * **Wind Rose:** Create a Wind Rose chart (using `WD` and `WS`) to show wind speed by direction (using all data).
    * **Cleaning Flag Analysis:** If the 'Cleaning' column exists in the raw data, analyze and report the average output (`ModA`, `ModB`) based on the 'Cleaning' flag (0 vs. 1).


