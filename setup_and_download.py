import os
import requests
import zipfile
import io

def setup_project():
    dirs = ['data', 'utils', 'components', 'assets']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Directory verified: {d}")

def download_data():
    # Try Jan 2024 first, then Dec 2023 if not available
    urls = [
        ("2024_1", "https://transtats.bts.gov/PREZIPPED/OT_CARRIER_REPORTING_2024_1.zip"),
        ("2023_12", "https://transtats.bts.gov/PREZIPPED/OT_CARRIER_REPORTING_2023_12.zip")
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    save_path = "data"
    
    for name, url in urls:
        print(f"Attempting to download {name} from {url}...")
        try:
            r = requests.get(url, headers=headers, stream=True, verify=False) # verify=False because BTS certs sometimes act up
            if r.status_code == 200:
                print(f"Download successful. File size: {len(r.content)} bytes")
                try:
                    z = zipfile.ZipFile(io.BytesIO(r.content))
                    z.extractall(save_path)
                    print(f"Extracted to {save_path}")
                    # Rename the CSV to something standard
                    csv_files = [f for f in os.listdir(save_path) if f.endswith('.csv') and 'On_Time' in f]
                    for f in csv_files:
                        print(f"Found CSV: {f}")
                        # Keep original name or rename if needed, but for now just logging it
                    return True
                except zipfile.BadZipFile:
                    print("Downloaded file is not a valid zip.")
            else:
                print(f"Failed with status code: {r.status_code}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")
    
    return False

def generate_dummy_data():
    print("Generating 4 years of dummy data (2021-2024)...")
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    years = [2021, 2022, 2023, 2024]
    airlines = ['United', 'Delta', 'American', 'Southwest', 'JetBlue']
    airports = ['JFK', 'LAX', 'ORD', 'ATL', 'DFW', 'SFO', 'MIA', 'DEN', 'SEA', 'BOS'] # Added a few more for variety
    
    os.makedirs("data", exist_ok=True)

    for year in years:
        print(f"Generating data for {year}...")
        # Generate 5000 flights per year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        days_range = (end_date - start_date).days
        
        dates = [start_date + timedelta(days=np.random.randint(0, days_range)) for _ in range(5000)]
        dates.sort()
        
        data = []
        for dt in dates:
            dep_delay = np.random.choice([0, 0, 0, 15, 30, 45, 60, 120, 240], p=[0.55, 0.1, 0.1, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01])
            is_delayed = 1 if dep_delay >= 15 else 0
            is_cancelled = np.random.choice([0, 1], p=[0.98, 0.02])
            
            row = {
                'FlightDate': dt,
                'Reporting_Airline': np.random.choice(airlines),
                'Tail_Number': f"N{np.random.randint(100,999)}XX",
                'Flight_Number_Reporting_Airline': np.random.randint(100, 9999),
                'Origin': np.random.choice(airports),
                'OriginCityName': 'CityName', 'OriginState': 'State',
                'Dest': np.random.choice(airports),
                'DestCityName': 'CityName', 'DestState': 'State',
                'DepDelay': dep_delay,
                'DepDel15': is_delayed,
                'ArrDelay': dep_delay - np.random.randint(-10, 15) if not is_cancelled else 0, # Slight variation
                'ArrDel15': 1 if (dep_delay - 5) >= 15 else 0, # Rough approx
                'Cancelled': is_cancelled,
                'CancellationCode': 'A' if is_cancelled else '',
                'AirTime': np.random.randint(45, 360),
                'Distance': np.random.randint(150, 3000),
                'CarrierDelay': 0, 'WeatherDelay': 0, 'NASDelay': 0, 'SecurityDelay': 0, 'LateAircraftDelay': 0
            }
            
            # Simple logic correction for ArrDel15 and delays
            if row['ArrDelay'] >= 15 and not is_cancelled:
                row['ArrDel15'] = 1
                # Distribute delay reasons
                cause = np.random.choice(['Carrier', 'Weather', 'NAS', 'LateAircraft'], p=[0.4, 0.15, 0.25, 0.2])
                if cause == 'Carrier': row['CarrierDelay'] = row['ArrDelay']
                elif cause == 'Weather': row['WeatherDelay'] = row['ArrDelay']
                elif cause == 'NAS': row['NASDelay'] = row['ArrDelay']
                elif cause == 'LateAircraft': row['LateAircraftDelay'] = row['ArrDelay']
            else:
                row['ArrDel15'] = 0 if not is_cancelled else 0

            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Save as Parquet for performance
        save_path = f"data/On_Time_Reporting_{year}.parquet"
        df.to_parquet(save_path, index=False)
        print(f"Saved {save_path}")
        
        # Also clean up old CSVs if they exist to avoid confusion
        csv_path = f"data/On_Time_Reporting_{year}.csv"
        if os.path.exists(csv_path):
            os.remove(csv_path)

if __name__ == "__main__":
    setup_project()
    if not download_data():
        print("Download failed. Using dummy data.")
        generate_dummy_data()
    print("Data setup complete.")
