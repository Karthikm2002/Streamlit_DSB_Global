# dashboard.py (Corrected and Final Version)

import streamlit as st
import json
import os

DATA_FILE = "all_project_metrics_dsb.json"

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Watsonx Metrics Dashboard")

# --- Custom CSS for the Metric Boxes ---
# This CSS creates the card-like appearance for each metric.
st.markdown("""
<style>
.metric-card {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 10px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
    min-height: 150px; /* Use min-height to ensure cards are at least this tall */
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-bottom: 20px; /* Adds vertical space between rows of cards */
}
.metric-card-label {
    font-size: 16px;
    color: #333333;
    font-weight: normal;
    margin-bottom: 10px;
}
.metric-card-value {
    font-size: 42px;
    font-weight: bold;
    color: #0072C6; /* A nice blue color */
}
</style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.title("Watsonx Deployments Metrics Dashboard")

# --- Helper Functions for Formatting ---
def format_label(metric_name):
    """Converts a key like 'pii_input' to 'PII Input' or 'average_api_latency' to 'Average API Latency'."""
    # Special handling for known acronyms
    name = metric_name.replace('pii', 'PII').replace('hap', 'HAP')
    # Capitalize all words
    return ' '.join(word.capitalize() for word in name.split('_'))

def format_value(value):
    """Formats values nicely: percentages, rounded floats, and large numbers."""
    if isinstance(value, float):
        # Format values between 0 and 1 as percentages (excluding exact zero)
        if 0 < abs(value) <= 1:
            return f"{value:.2%}"
        # Format other floats to 2 decimal places with commas
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return value if value is not None else "N/A"

# --- Data Loading ---
@st.cache_data
def load_data():
    """Loads the metrics data from the JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error(f"Error: The file '{DATA_FILE}' is not a valid JSON file.")
            return None
    return None

data = load_data()

# --- Dashboard Display ---
if not data:
    st.warning(f"Data file not found or is empty! Please make sure the file `{DATA_FILE}` is in the same directory and contains data.")
else:
    st.info(f"Displaying metrics for {len(data)} deployments.")
    
    # Loop through each deployment from the JSON file (THIS IS THE CORRECTED LOGIC)
    for deployment in data:
        deployment_name = deployment.get("deployment_name", "N/A")
        
        # Add a divider and a sub-header for each deployment for context
        st.divider()
        st.subheader(f"Metrics for Deployment: {deployment_name}")

        summary = deployment.get("metrics_summary", {})
        
        # Consolidate all available metrics into a single list
        all_metrics = []
        if isinstance(summary.get("generative_ai_quality"), dict):
            all_metrics.extend(summary["generative_ai_quality"].items())
        if isinstance(summary.get("model_health"), dict):
            all_metrics.extend(summary["model_health"].items())
        if isinstance(summary.get("mrm_risk"), dict):
            all_metrics.extend(summary["mrm_risk"].items())
        
        if not all_metrics:
            st.info("No metrics available for this deployment.")
            continue

        # Dynamically create a grid of metric boxes
        cols = st.columns(4) 
        
        for i, (metric_name, metric_value) in enumerate(all_metrics):
            col = cols[i % 4] 
            
            # Use st.markdown with our custom CSS to create the styled card
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-card-label">{format_label(metric_name)}</div>
                    <div class="metric-card-value">{format_value(metric_value)}</div>
                </div>
                """, unsafe_allow_html=True)