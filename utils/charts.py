import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pydeck as pdk
from plotly.subplots import make_subplots

def create_otp_bar_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generates a bar chart showing On-Time Performance (OTP) by airline.
    
    Args:
        df: Filtered DataFrame containing flight data.
        
    Returns:
        Plotly Figure object.
    """
    if df.empty:
        return go.Figure()

    airline_perf = df.groupby('Reporting_Airline').apply(
        lambda x: ((len(x) - x['Cancelled'].sum() - x['ArrDel15'].sum()) / len(x)) * 100
    ).reset_index(name='OTP')
    
    fig = px.bar(
        airline_perf, x='Reporting_Airline', y='OTP',
        color='OTP',
        template='plotly_dark',
        color_continuous_scale='bluyl',
        labels={'OTP': 'On-Time %', 'Reporting_Airline': 'Airline'}
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_delay_donut_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generates a donut chart visualizing the breakdown of delay causes.
    """
    if df.empty:
        return go.Figure()
        
    delay_cols = ['CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay']
    delays = df[delay_cols].sum()
    delays_df = pd.DataFrame({'Cause': delays.index, 'Minutes': delays.values})
    
    fig = px.pie(
        delays_df, names='Cause', values='Minutes',
        hole=0.4,
        template='plotly_dark',
        color_discrete_sequence=px.colors.sequential.Bluyl
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    return fig

def create_daily_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generates a line chart for daily average delay trends.
    """
    if df.empty:
        return go.Figure()
        
    daily_stats = df.groupby('FlightDate').agg({
        'DepDelay': 'mean'
    }).reset_index()
    daily_stats.rename(columns={'DepDelay': 'Avg Delay'}, inplace=True)
    
    fig = px.line(
        daily_stats, x='FlightDate', y='Avg Delay',
        template='plotly_dark',
        markers=True,
        title='Daily Average Delay (min)',
        color_discrete_sequence=['#38BDF8']
    )
    fig.update_traces(line=dict(width=3))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_seasonal_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generates a dual-axis chart showing Monthly Traffic vs. Average Delay.
    """
    if df.empty:
        return go.Figure()
        
    df['Month'] = df['FlightDate'].dt.month_name()
    df['MonthNum'] = df['FlightDate'].dt.month
    
    monthly_stats = df.groupby(['MonthNum', 'Month']).agg({
        'DepDelay': 'mean',
        'Flight_Number_Reporting_Airline': 'count'
    }).reset_index()
    monthly_stats = monthly_stats.sort_values('MonthNum')
    monthly_stats.rename(columns={'Flight_Number_Reporting_Airline': 'Total Flights', 'DepDelay': 'Avg Delay'}, inplace=True)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Total Flights (Bar)
    fig.add_trace(
        go.Bar(
            x=monthly_stats['Month'], 
            y=monthly_stats['Total Flights'], 
            name="Total Flights",
            marker_color="#1E293B",
            opacity=0.5
        ),
        secondary_y=False
    )

    # Avg Delay (Line)
    fig.add_trace(
        go.Scatter(
            x=monthly_stats['Month'], 
            y=monthly_stats['Avg Delay'], 
            name="Avg Delay (min)",
            line=dict(color="#F472B6", width=4),
            mode='lines+markers'
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="Monthly Traffic vs. Average Delay (Selected Period)",
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    fig.update_yaxes(title_text="Total Flights", secondary_y=False)
    fig.update_yaxes(title_text="Avg Delay (min)", secondary_y=True)
    return fig

def create_scatter_chart(df: pd.DataFrame) -> go.Figure:
    """Generates scatter plot for Distance vs Arrival Delay."""
    if df.empty: return go.Figure()
    
    fig = px.scatter(
        df, x='Distance', y='ArrDelay',
        color='Reporting_Airline',
        template='plotly_dark',
        opacity=0.6,
        title="Impact of Flight Distance on Arrival Delay",
        labels={'ArrDelay': 'Arrival Delay (min)', 'Distance': 'Distance (miles)'}
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_day_of_week_chart(df: pd.DataFrame) -> go.Figure:
    """Generates bar chart for Average Delay by Day of Week."""
    if df.empty: return go.Figure()
    
    df['DayOfWeek'] = df['FlightDate'].dt.day_name()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    day_stats = df.groupby('DayOfWeek')['DepDelay'].mean().reindex(days_order).reset_index()
    
    fig = px.bar(
        day_stats, x='DayOfWeek', y='DepDelay',
        template='plotly_dark',
        color='DepDelay',
        color_continuous_scale='Redor',
        title="Average Delay by Day of Week"
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_route_map_layer(df: pd.DataFrame, get_coords_func: callable) -> tuple:
    """
    Prepares the Pydeck Deck object for the 3D route map.
    
    Args:
        df: Filtered Dataframe
        get_coords_func: Function from data_loader to map coordinates (passed to avoid circular import)
        
    Returns:
        pdk.Deck object
    """
    map_df = get_coords_func(df)
    
    if map_df.empty:
        return None

    route_map_data = map_df.groupby(['Origin', 'Dest', 'OriginLat', 'OriginLon', 'DestLat', 'DestLon']).size().reset_index(name='Count')
    
    layer = pdk.Layer(
        "ArcLayer",
        data=route_map_data,
        get_source_position=["OriginLon", "OriginLat"],
        get_target_position=["DestLon", "DestLat"],
        get_source_color=[56, 189, 248, 160], # Cyan
        get_target_color=[236, 72, 153, 160], # Pink
        get_width="1 + (Count / 50)", 
        get_tilt=15,
        pickable=True
    )
    
    view_state = pdk.ViewState(
        latitude=39.8283,
        longitude=-98.5795,
        zoom=3,
        pitch=45,
        bearing=0
    )
    
    return pdk.Deck(
        map_style=None,
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{Origin} -> {Dest}\nFlights: {Count}"}
    )
