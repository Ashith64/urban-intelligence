"""Page 7: Correlation and Statistical Distribution Analysis."""
import streamlit as st
from src.data_loader import get_final_merged_data
from src.analysis import compute_correlation_matrix
from src.charts import (
    plot_correlation_heatmap,
    plot_regional_boxplots,
    plot_metric_histogram,
    render_static_seaborn_pairplot,
)

st.set_page_config(page_title="Correlation & Distribution - BISL504", page_icon="📈", layout="wide")

st.title("📈 Correlation & Statistical Distribution Analysis")
st.markdown(
    """
    Investigate statistical associations between economic indices and air pollution concentrations. 
    Evaluate parametric (Pearson) and monotonic non-parametric (Spearman) relationships, 
    and inspect regional distributions via interactive box plots and static Seaborn density estimates.
    """
)

df = get_final_merged_data()

# 1. Correlation Matrix Heatmap
st.subheader("1. Correlation Matrix Heatmap")
col_corr1, col_corr2 = st.columns([1, 3])

with col_corr1:
    method = st.radio("Correlation Method:", ["pearson", "spearman"], format_func=str.capitalize)
    st.markdown(
        """
        - **Pearson**: Measures linear association ($r$).
        - **Spearman**: Measures monotonic rank order ($\rho$), robust against non-normal outliers.
        """
    )

corr_df = compute_correlation_matrix(df, method=method)

with col_corr2:
    fig_corr = plot_correlation_heatmap(corr_df, title=f"{method.capitalize()} Correlation Matrix")
    st.plotly_chart(fig_corr, use_container_width=True)

st.caption("Heatmap Takeaway: Cost of Living, Rent, and Groceries exhibit high positive collinearity (r > 0.85). Local Purchasing Power has a moderate negative correlation with PM2.5, indicating higher-income cities generally enjoy cleaner air.")

st.markdown("---")

# 2. Regional Box Plots & Histograms
st.subheader("2. Metric Distributions & Regional Variations")

metrics_dict = {
    "Local_Purchasing_Power_Index": "Local Purchasing Power Index (NY=100)",
    "Cost_of_Living_Index": "Cost of Living Index (NY=100)",
    "Rent_Index": "Rent Index (NY=100)",
    "PM2_5_2024_ugm3": "PM2.5 Concentration (µg/m³)",
    "Relative_Net_Income_Index": "Relative Net Income Index",
}

sel_dist_metric = st.selectbox(
    "Select metric for distribution analysis:",
    list(metrics_dict.keys()),
    format_func=lambda k: metrics_dict[k],
    index=0,
)

col_box, col_hist = st.columns([1, 1])

with col_box:
    fig_box = plot_regional_boxplots(df, sel_dist_metric, metrics_dict[sel_dist_metric])
    st.plotly_chart(fig_box, use_container_width=True)
    st.caption(f"Box Plot Takeaway: Displays regional medians, quartiles, and interquartile spread for {metrics_dict[sel_dist_metric]}.")

with col_hist:
    fig_hist = plot_metric_histogram(df, sel_dist_metric, metrics_dict[sel_dist_metric])
    st.plotly_chart(fig_hist, use_container_width=True)
    st.caption(f"Histogram Takeaway: Shows frequency distribution with dashed lines marking the mean and median.")

st.markdown("---")

# 3. Static Seaborn / Matplotlib Figure (SPEC requirement)
st.subheader("3. Static Bivariate Density & Regression (Seaborn / Matplotlib)")
st.markdown("Rendered via `st.pyplot` for publication-quality statistical visualization.")

fig_static = render_static_seaborn_pairplot(df)
st.pyplot(fig_static)
st.caption("Static Visual Takeaway: Left panel illustrates bivariate KDE contour densities by region with the WHO 5.0 µg/m³ threshold. Right panel demonstrates positive linear correlation between Cost of Living and Local Purchasing Power.")
