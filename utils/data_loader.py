import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data(file_dir="data"):
    """
    Loads aviation data from the data directory.
    Attempts to read all CSVs matching 'On_Time_Reporting' pattern.
    """
    all_files = os.listdir(file_dir)
    csv_files = [f for f in all_files if f.endswith('.csv') and 'On_Time' in f]
    
    if not csv_files:
        return pd.DataFrame() # Return empty if no data found yet
    
    # Load all available files
    dfs = []
    for f in csv_files:
        p = os.path.join(file_dir, f)
        try:
            # Read header first to check columns if needed, but simple read is fine for now
            d = pd.read_csv(p, low_memory=False)
            dfs.append(d)
        except Exception as e:
            st.error(f"Error reading {f}: {e}")
    
    if not dfs:
        return pd.DataFrame()
        
    try:
        df = pd.concat(dfs, ignore_index=True)
        
        # Select key columns to reduce memory usage
        
        # Select key columns to reduce memory usage
        cols_to_keep = [
            'FlightDate', 'Reporting_Airline', 'Tail_Number', 'Flight_Number_Reporting_Airline',
            'Origin', 'OriginCityName', 'OriginState',
            'Dest', 'DestCityName', 'DestState',
            'DepDelay', 'DepDel15', 'ArrDelay', 'ArrDel15', 'Cancelled', 'CancellationCode',
            'AirTime', 'Distance', 'CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay'
        ]
        
        # Filter columns that actually exist
        cols_to_keep = [c for c in cols_to_keep if c in df.columns]
        df = df[cols_to_keep]

        # Convert Date
        if 'FlightDate' in df.columns:
            df['FlightDate'] = pd.to_datetime(df['FlightDate'])
        
        # Create 'Airline' readable name mapping (Simplified)
        # In a real app we'd load L_UNIQUE_CARRIERS.csv lookup, 
        # but for now we rely on the code or a simple map if needed.
        # df['AirlineName'] = df['Reporting_Airline'] # Placeholder
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def calculate_kpis(df):
    if df.empty:
        return {}
    
    total_flights = len(df)
    total_cancelled = df['Cancelled'].sum()
    on_time_flights = len(df) - total_cancelled - df['DepDel15'].sum() # Simple proxy: DepDel15=1 means delayed
    # Actually better metric: On-Time Arrival (ArrDel15)
    on_time_arrival = len(df) - total_cancelled - df['ArrDel15'].sum()
    
    otp = (on_time_arrival / total_flights) * 100 if total_flights > 0 else 0
    avg_delay = df[df['DepDelay'] > 0]['DepDelay'].mean()
    if pd.isna(avg_delay):
        avg_delay = 0
    
    return {
        "Total Flights": total_flights,
        "OTP": otp,
        "Cancelled": total_cancelled,
        "Avg Delay (min)": avg_delay
    }

# Hardcoded coordinates for major US airports (to avoid needing external DB)
AIRPORT_COORDS = {
    'ATL': [33.6407, -84.4277], 'DFW': [32.8998, -97.0403], 'DEN': [39.8561, -104.6737],
    'ORD': [41.9742, -87.9073], 'LAX': [33.9416, -118.4085], 'CLT': [35.2144, -80.9473],
    'MCO': [28.4312, -81.3081], 'LAS': [36.0840, -115.1537], 'PHX': [33.4341, -112.0080],
    'MIA': [25.7959, -80.2870], 'SEA': [47.4502, -122.3088], 'IAH': [29.9902, -95.3368],
    'JFK': [40.6413, -73.7781], 'EWR': [40.6895, -74.1745], 'FLL': [26.0742, -80.1506],
    'SFO': [37.6188, -122.3749], 'MSP': [44.8848, -93.2223], 'BOS': [42.3656, -71.0096],
    'DTW': [42.2121, -83.3533], 'PHL': [39.8729, -75.2437], 'LGA': [40.7769, -73.8740],
    'BWI': [39.1754, -76.6684], 'SLC': [40.7899, -111.9791], 'SAN': [32.7338, -117.1933],
    'IAD': [38.9531, -77.4565], 'DCA': [38.8512, -77.0402], 'MDW': [41.7868, -87.7522]
}

def get_airport_coordinates(df):
    """
    Adds OriginLat, OriginLon, DestLat, DestLon to dataframe based on Airport Codes.
    Returns df with coordinates, dropping rows where coords are missing for map.
    """
    df = df.copy() # Ensure we don't mutate the cached dataframe or view
    # Map coordinates
    def get_lat(code): return AIRPORT_COORDS.get(code, [None, None])[0]
    def get_lon(code): return AIRPORT_COORDS.get(code, [None, None])[1]
    
    df['OriginLat'] = df['Origin'].apply(get_lat)
    df['OriginLon'] = df['Origin'].apply(get_lon)
    df['DestLat'] = df['Dest'].apply(get_lat)
    df['DestLon'] = df['Dest'].apply(get_lon)
    
    # Filter out routes where we don't have coords (to prevent map errors)
    return df.dropna(subset=['OriginLat', 'OriginLon', 'DestLat', 'DestLon'])
