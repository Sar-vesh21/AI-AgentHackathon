from typing import Dict, List, Any
import requests
import pandas as pd
import logging
from datetime import datetime

class HyperliquidDataService:
    """Service class for fetching and processing Hyperliquid data"""
    
    def __init__(self):
        self.api_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"Content-Type": "application/json"}
        self.cache = {}

    def get_historical_orders(self, user_address: str) -> List[Dict[str, Any]]:
        """Fetch historical orders for a user"""
        cache_key = f"orders_{user_address}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        payload = {
            "type": "historicalOrders",
            "user": user_address
        }
        
        return self._make_api_request(payload, cache_key)

    def get_user_trades(self, user_address: str) -> List[Dict[str, Any]]:
        """Fetch user trades"""
        cache_key = f"trades_{user_address}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        payload = {
            "type": "userFills",
            "user": user_address
        }
        
        return self._make_api_request(payload, cache_key)

    def _make_api_request(self, payload: Dict[str, Any], cache_key: str) -> List[Dict[str, Any]]:
        """Make API request with caching"""
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            self.cache[cache_key] = data
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            return []

    def process_trades_to_dataframe(self, trades: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert trades to DataFrame"""
        if not trades:
            return pd.DataFrame()
            
        df = pd.DataFrame(trades)
        
        # Convert time to timestamp
        if 'time' in df.columns:
            df['timestamp'] = pd.to_datetime(df['time'], unit='ms')
            
        # Convert numeric columns from string to float
        numeric_columns = ['px', 'sz', 'startPosition', 'closedPnl', 'fee']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # Convert side to lowercase for consistency and add position type
        if 'side' in df.columns:
            df['side'] = df['side'].str.lower()
            df['position_type'] = df['side'].map({'a': 'Short', 'b': 'Long'})
            
        # Calculate position value and size
        if all(col in df.columns for col in ['px', 'sz', 'side']):
            # Position value (negative for shorts, positive for longs)
            df['position_value'] = df.apply(
                lambda x: -float(x['px']) * float(x['sz']) if x['side'] == 'a' else float(x['px']) * float(x['sz']),
                axis=1
            )
            
            # Position size (negative for shorts, positive for longs)
            df['position_size'] = df.apply(
                lambda x: -float(x['sz']) if x['side'] == 'a' else float(x['sz']),
                axis=1
            )
            
            # Calculate cumulative position
            df['cumulative_position'] = df.groupby('coin')['position_size'].cumsum()

            
            # Calculate weighted average price (VWAP)
            df['vwap'] = df.groupby('coin').apply(
                lambda x: (x['px'] * x['sz'].abs()).sum() / x['sz'].abs().sum()
            ).reset_index(level=0, drop=True)
            
        return df 