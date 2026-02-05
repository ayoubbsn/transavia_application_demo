import streamlit as st
import pandas as pd
import plotly.express as px
from utils.charts import (
    create_otp_bar_chart, create_delay_donut_chart, create_daily_trend_chart,
    create_seasonal_trend_chart, create_scatter_chart, create_day_of_week_chart,
    create_route_map_layer
)
from utils.data_loader import calculate_kpis, get_airport_coordinates

def render_overview_tab(df: pd.DataFrame):
    """Renders the Overview tab content."""
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("On-Time Performance by Airline")
        st.plotly_chart(create_otp_bar_chart(df), use_container_width=True)

    with col_chart2:
        st.subheader("Delay Cause Breakdown")
        st.plotly_chart(create_delay_donut_chart(df), use_container_width=True)

def render_trends_tab(df: pd.DataFrame):
    """Renders the Trends & Analysis tab content."""
    st.subheader("Daily Flight & Delay Trends")
    st.plotly_chart(create_daily_trend_chart(df), use_container_width=True)

    st.markdown("---")
    st.plotly_chart(create_seasonal_trend_chart(df), use_container_width=True)
    
    col_adv1, col_adv2 = st.columns(2)
    with col_adv1:
        st.subheader("Reliability vs. Distance")
        st.plotly_chart(create_scatter_chart(df), use_container_width=True)
    with col_adv2:
        st.subheader("Day of Week Analysis")
        st.plotly_chart(create_day_of_week_chart(df), use_container_width=True)

def render_route_insights_tab(df: pd.DataFrame):
    """Renders the Route Insights tab content."""
    st.subheader("Top Busiest Routes")
    if not df.empty:
        # Create Route Column
        df = df.copy()
        df['Route'] = df['Origin'] + " → " + df['Dest']
        
        route_stats = df.groupby('Route').agg({
            'Flight_Number_Reporting_Airline': 'count',
            'ArrDelay': 'mean'
        }).reset_index()
        route_stats.rename(columns={'Flight_Number_Reporting_Airline': 'Total Flights', 'ArrDelay': 'Avg Delay'}, inplace=True)
        
        # Sort by Volume
        top_routes = route_stats.sort_values('Total Flights', ascending=False).head(10)
        
        fig_routes = px.bar(
            top_routes, y='Route', x='Total Flights',
            orientation='h',
            template='plotly_dark',
            color='Avg Delay',
            color_continuous_scale='Viridis',
            title="Busiest Routes (Color = Avg Delay)"
        )
        fig_routes.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_routes, use_container_width=True)
    
    st.subheader("Origin Usage")
    if not df.empty:
        airport_vol = df['Origin'].value_counts().reset_index()
        airport_vol.columns = ['Airport', 'Flights']
        top_airports = airport_vol.head(15)
        
        fig_map = px.bar(
            top_airports, x='Airport', y='Flights',
            template='plotly_dark',
            color='Flights',
            color_continuous_scale='Tealgrn'
        )
        fig_map.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_map, use_container_width=True)

def render_comparator_tab(df: pd.DataFrame, all_airlines: list):
    """Renders the Head-to-Head Comparator tab."""
    st.subheader("⚔️ Airline Face-Off")
    if len(all_airlines) < 2:
        st.warning("Insufficient data to compare.")
        return

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        airline_a = st.selectbox("Airline A", options=all_airlines, index=0)
    with col_c2:
        airline_b = st.selectbox("Airline B", options=all_airlines, index=1 if len(all_airlines)>1 else 0)
    
    if airline_a == airline_b:
        st.warning("Select different airlines to compare.")
    else:
        # Filter for specific airlines
        df_a = df[df['Reporting_Airline'] == airline_a]
        df_b = df[df['Reporting_Airline'] == airline_b]
        
        kpi_a = calculate_kpis(df_a)
        kpi_b = calculate_kpis(df_b)
        
        # Display KPIs side-by-side
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.metric(f"{airline_a} Flights", f"{kpi_a.get('Total Flights',0):,}", delta=f"{kpi_a.get('Total Flights',0) - kpi_b.get('Total Flights',0):,}")
        with c2:
            st.metric(f"{airline_a} OTP", f"{kpi_a.get('OTP',0):.1f}%", delta=f"{kpi_a.get('OTP',0) - kpi_b.get('OTP',0):.1f}%")
        with c3:
            st.metric(f"{airline_a} Avg Delay", f"{kpi_a.get('Avg Delay (min)',0):.1f}m", delta=f"{kpi_a.get('Avg Delay (min)',0) - kpi_b.get('Avg Delay (min)',0):.1f}m", delta_color="inverse")
        with c4:
            st.metric(f"{airline_a} Cancelled", f"{kpi_a.get('Cancelled',0)}", delta=f"{kpi_a.get('Cancelled',0) - kpi_b.get('Cancelled',0)}", delta_color="inverse")
            
        st.caption(f"Comparison against {airline_b}")

def render_map_tab(df: pd.DataFrame, selected_airlines: list):
    """Renders the 3D Network Map tab."""
    st.subheader("🗺️ 3D Interactive Route Map")
    
    deck = create_route_map_layer(df, get_airport_coordinates)
    
    if deck:
        # Using a unique key to force redraw when selection changes
        st.pydeck_chart(deck, key=f"map_{'-'.join(selected_airlines)}")
    else:
        st.warning("No coordinate data available for selected routes.")
