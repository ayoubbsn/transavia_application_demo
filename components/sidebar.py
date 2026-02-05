import streamlit as st
import pandas as pd
from typing import Tuple, List

def render_sidebar(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Renders the sidebar filters and returns the filtered DataFrame.
    
    Args:
        df: The full dataset.
        
    Returns:
        Tuple containing:
        - filtered_df: DataFrame after applying date and airline filters.
        - selected_airlines: List of selected airline codes.
    """
    st.sidebar.header("Filter Analytics")
    
    # Airline Filter
    airlines = sorted(df['Reporting_Airline'].unique())
    selected_airlines = st.sidebar.multiselect(
        "Select Airlines",
        options=airlines,
        default=airlines[:3] if len(airlines) > 3 else airlines
    )
    
    # Date Filter
    min_date = df['FlightDate'].min()
    max_date = df['FlightDate'].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Apply Filters
    if isinstance(date_range, tuple) and len(date_range) == 2:
        mask = (df['FlightDate'].dt.date >= date_range[0]) & (df['FlightDate'].dt.date <= date_range[1])
        mask &= (df['Reporting_Airline'].isin(selected_airlines))
        filtered_df = df[mask]
    else:
        filtered_df = df[df['Reporting_Airline'].isin(selected_airlines)]
        
    return filtered_df, selected_airlines
