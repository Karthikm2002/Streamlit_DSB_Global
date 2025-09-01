# dashboard.py (Updated to read from the database)

import streamlit as st
import pandas as pd

# --- Page Configuration and CSS ---
st.set_page_config(layout="wide", page_title="Watsonx Metrics Dashboard")
st.markdown("""
<style>
.metric-card {
    background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 10px;
    padding: 25px; text-align: center; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
    min-height: 150px; display: flex; flex-direction: column;
    justify-content: center; margin-bottom: 20px;
}
.metric-card-label { font-size: 16px; color: #333333; font-weight: normal; margin-bottom: 10px; }
.metric-card-value { font-size: 42px; font-weight: bold; color: #0072C6; }
</style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.title("Watsonx Deployments Metrics Dashboard")

# --- Helper Functions ---
def format_label(metric_name):
    """Converts a key like 'pii_input' to 'PII Input' or 'average_api_latency' to 'Average API Latency'."""
    name = metric_name.replace('pii', 'PII').replace('hap', 'HAP')
    return ' '.join(word.capitalize() for word in name.split('_'))

def format_value(value):
    """Formats values nicely: percentages, rounded floats, and large numbers."""
    if pd.isna(value):
        return "N/A"
    if isinstance(value, float):
        if 0 < abs(value) <= 1:
            return f"{value:.2%}"
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return value

# --- Data Loading (Reads from the database) ---
@st.cache_data(ttl=60) # Caches data for 60 seconds
def load_data():
    """Loads the flattened metrics data from the cloud database."""
    try:
        conn = st.connection("metrics_db", type="sql")
        # The table name must match the one in your local script
        df = conn.query("SELECT * FROM latest_metrics;")
        return df
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return pd.DataFrame() # Return an empty DataFrame on error

# --- Dashboard Display (Works with the flat database table) ---
df = load_data()
if df.empty:
    st.warning("Could not load data from the database. Please ensure the reporting script has been run.")
else:
    st.info(f"Displaying metrics for {len(df)} deployments.")
    
    # These are columns we DON'T want to display as metric cards
    id_columns = ['deployment_name', 'prompt_template_name', 'deployment_id', 'error']
    
    # Loop through each row in our DataFrame (each row is a deployment)
    for index, deployment_row in df.iterrows():
        st.divider()
        st.subheader(f"Metrics for Deployment: {deployment_row['deployment_name']}")
        st.caption(f"Template: {deployment_row['prompt_template_name']}")
        
        # Get only the columns that contain metric values
        metric_columns = [col for col in df.columns if col not in id_columns]
        
        cols = st.columns(4)
        col_index = 0
        for metric_name in metric_columns:
            # Check if the metric exists for this deployment
            if metric_name in deployment_row and pd.notna(deployment_row[metric_name]):
                metric_value = deployment_row[metric_name]
                col = cols[col_index % 4]
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-card-label">{format_label(metric_name)}</div>
                        <div class="metric-card-value">{format_value(metric_value)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                col_index += 1
