import streamlit as st
import pandas as pd
from utils.data_loader import load_data, calculate_kpis
from components.sidebar import render_sidebar
from components.tabs import (
    render_overview_tab, render_trends_tab, render_route_insights_tab,
    render_comparator_tab, render_map_tab
)

# --- Page Config ---
st.set_page_config(
    page_title="SkyStream Analytics",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Custom CSS ---
def local_css(file_name):
    """Loads local CSS file."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

def main():
    """Main application entry point."""
    
    # --- Header ---
    st.title("SkyStream Analytics")
    st.markdown("### Operational Performance Dashboard")

    # --- Data Loading ---
    with st.spinner("Loading Aviation Data..."):
        df = load_data()

    if df.empty:
        st.warning("No data found. Please run the setup script to generate or download data.")
        st.stop()

    # --- Dataset Overview ---
    with st.expander("📊 Dataset Overview", expanded=True):
        st.markdown("""
        **Welcome to the US Aviation BI Dashboard.** 
        This dataset aggregates flight reliability metrics from the **Bureau of Transportation Statistics (BTS)**. 
        It tracks domestic US flights, analyzing **on-time performance, delay causes, and cancellations** across major carriers. 
        
        > 🎯 **Project Context:** This interactive application was designed and developed to demonstrate technical proficiency in **Data Analysis, Python, and BI Visualization**, specifically tailored for the **Data Analyst & BI** opportunity at **Transavia**.
        """)
        d_c1, d_c2, d_c3, d_c4 = st.columns(4)
        d_c1.info(f"**Period:** {df['FlightDate'].min().strftime('%b %Y')} - {df['FlightDate'].max().strftime('%b %Y')}")
        d_c2.info(f"**Total Records:** {len(df):,}")
        d_c3.info(f"**Airlines:** {df['Reporting_Airline'].nunique()}")
        d_c4.info(f"**Airports:** {len(set(df['Origin'].unique()) | set(df['Dest'].unique()))}")
        
    st.markdown("---")

    # --- Sidebar & Filtering ---
    filtered_df, selected_airlines = render_sidebar(df)

    # --- Top Level KPIs ---
    kpis = calculate_kpis(filtered_df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Flights", f"{kpis.get('Total Flights', 0):,}")
    with col2: st.metric("On-Time Performance", f"{kpis.get('OTP', 0):.1f}%")
    with col3: st.metric("Cancelled Flights", f"{kpis.get('Cancelled', 0):,}")
    with col4: st.metric("Avg. Departure Delay", f"{kpis.get('Avg Delay (min)', 0):.1f} min")

    st.markdown("---")

    # --- Main Dashboard Tabs ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Trends & Analysis", "Route Insights", "⚔️ Head-to-Head", "🗺️ 3D Network"
    ])

    with tab1:
        render_overview_tab(filtered_df)

    with tab2:
        render_trends_tab(filtered_df)

    with tab3:
        render_route_insights_tab(filtered_df)

    with tab4:
        # Pass full df for ability to select any airline for comparison
        render_comparator_tab(df, sorted(df['Reporting_Airline'].unique()))

    with tab5:
        render_map_tab(filtered_df, selected_airlines)

    # --- Raw Data Export ---
    with st.expander("View Raw Data Sample"):
        st.dataframe(filtered_df.head(100), use_container_width=True)

if __name__ == "__main__":
    main()
