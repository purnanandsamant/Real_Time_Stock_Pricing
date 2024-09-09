import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime, timedelta

st.title("Real-time Stock Price Dashboard")

# Define the list of ticker symbols
TICKERS = ['AAPL', 'TSLA', 'NVDA', 'GOOGL', 'META', 'MSFT', 'SPY', 'QQQ', '^GSPC']

# Create a dropdown for ticker selection
selected_ticker = st.sidebar.selectbox("Select a ticker", TICKERS)

# Get the data of the selected stock
stock = yf.Ticker(selected_ticker)

# Create placeholders for the plot and table
plot = st.empty()
table = st.empty()

# Function to get the start of the current minute
def get_start_of_minute():
    now = datetime.now()
    return now.replace(second=0, microsecond=0)

# Function to wait until the start of the next minute
def wait_until_next_minute():
    now = datetime.now()
    next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    time_to_wait = (next_minute - now).total_seconds()
    time.sleep(time_to_wait)

# Function to create an interactive candlestick chart
def create_candlestick_chart(data, ticker):
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'])])
    
    fig.update_layout(
        title=f'{ticker} Stock Value on {datetime.now().date()}',
        yaxis_title='Stock Value',
        xaxis_title='Time',
        xaxis_rangeslider_visible=False
    )
    
    return fig

# Loop to fetch and update stock values
while True:
    # Wait until the start of the next minute
    wait_until_next_minute()
    
    # Get the current date
    current_date = datetime.now().date()
    
    # Get the historical prices for the selected stock (only for today)
    historical_prices = stock.history(start=current_date, interval='1m')
    
    if not historical_prices.empty:
        # Create the interactive candlestick chart
        fig = create_candlestick_chart(historical_prices, selected_ticker)
        
        # Display the chart
        plot.plotly_chart(fig, use_container_width=True)
        
        # Get the last 20 minutes of data
        last_20_minutes = historical_prices.tail(20)
        
        # Create a DataFrame with the required information
        table_data = pd.DataFrame({
            'Time': last_20_minutes.index.strftime('%H:%M:%S'),
            'Open': last_20_minutes['Open'].round(2),
            'Close': last_20_minutes['Close'].round(2),
            'High': last_20_minutes['High'].round(2),
            'Low': last_20_minutes['Low'].round(2)
        })
        
        # Sort the table data in descending order of time
        table_data = table_data.sort_values('Time', ascending=False)
        
        # Display the table
        table.dataframe(table_data)
    else:
        st.write(f"No data available for {selected_ticker} today yet.")
    
    # Sleep for a short time to prevent excessive API calls
    time.sleep(5)