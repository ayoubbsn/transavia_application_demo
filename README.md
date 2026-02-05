# SkyStream Analytics Dashboard ✈️

A premium Business Intelligence dashboard for analyzing US Aviation Data, built with Streamlit and Python.

## Features
- **Executive Summary**: High-level KPIs (Total Flights, On-Time Performance, Cancellations).
- **Airline Analysis**: Comparative performance of major carriers.
- **Delay Factors**: Detailed breakdown of delay causes (Weather, Carrier, NAS).
- **Interactive Filtering**: Filter by Date Range and Airline.
- **Premium UI**: Custom Dark Mode and Glassmorphism design.

## Data Source
- **US Bureau of Transportation Statistics (BTS)**
- Dataset: Reporting Carrier On-Time Performance (1987-present)
- Automatic download via `setup_and_download.py`

## Setup & Run

1. **Install Dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Download Data**:
   ```bash
   python setup_and_download.py
   ```

3. **Run the Dashboard**:
   ```bash
   streamlit run app.py
   ```

## Technology Stack
- **Python**: Core logic
- **Streamlit**: Web App Framework
- **Pandas**: Data Manipulation
- **Plotly**: Interactive Charts
- **Pydeck**: Mapping (Optional/Future)
