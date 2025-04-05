from typing import Dict, List, Any
import requests
import pandas as pd
import logging
from datetime import datetime

'''
This class fetches correct data from the Hyperliquid API.
We use the singleton pattern to ensure that the data service is a singleton.
INPUTS:
    None
OUTPUTS:
    A list of dictionaries containing the order data
'''
class HyperliquidDataService:
    """Service class for fetching and processing Hyperliquid data"""
    
    def __init__(self):
        self.api_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"Content-Type": "application/json"}
        self.cache = {}
        self.leaderboard_url = "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard"

    def get_user_orders(self, user_address: str) -> List[Dict[str, Any]]:
        """Fetch historical orders for a user"""
        cache_key = f"orders_{user_address}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        print(f"Fetching orders for {user_address}")

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
    
    def get_top_traders(self, 
                       limit: int = 10, 
                       min_daily_volume: float = 0,
                       min_daily_pnl: float = float('-inf'),
                       min_roi: float = float('-inf')) -> List[Dict[str, Any]]:
        """Get top traders with optional filtering"""
        try:
            response = requests.get(self.leaderboard_url)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('leaderboardRows'):
                return []
                
            # Convert to DataFrame for easier filtering
            rows = []
            for row in data['leaderboardRows']:
                # Extract performance metrics
                performances = {p[0]: p[1] for p in row['windowPerformances']}
                
                row_data = {
                    'address': row['ethAddress'],
                    'account_value': float(row['accountValue']),
                    'display_name': row['displayName'] or 'Unknown',
                    'daily_pnl': float(performances['day']['pnl']),
                    'daily_roi': float(performances['day']['roi']),
                    'daily_volume': float(performances['day']['vlm']),
                    'weekly_pnl': float(performances['week']['pnl']),
                    'monthly_pnl': float(performances['month']['pnl']),
                    'all_time_pnl': float(performances['allTime']['pnl'])
                }
                rows.append(row_data)
            
            df = pd.DataFrame(rows)
            
            # Apply filters
            df = df[
                (df['daily_volume'] >= min_daily_volume) &
                (df['daily_pnl'] >= min_daily_pnl) &
                (df['daily_roi'] >= min_roi)
            ]
            
            # Sort by account value and get top N
            df = df.sort_values('account_value', ascending=False).head(limit)
            
            # Convert back to list of dicts
            return df.to_dict('records')
            
        except Exception as e:
            logging.error(f"Error getting top traders: {str(e)}")
            return []
    
    def _make_api_request(self, payload: Dict[str, Any], cache_key: str) -> List[Dict[str, Any]]:
        """Make API request with caching"""
        try:
            print(f"Making API request with payload: {payload}")
            print(f"API URL: {self.api_url}")
            print(f"Headers: {self.headers}")
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            print(f"Data: {data}")
            self.cache[cache_key] = data
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            return []
        
    def process_orders_to_dataframe(self, orders: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert historical orders to DataFrame"""
        if not orders:
            return pd.DataFrame()
            
        # Extract order details and status into a flat structure
        processed_orders = []
        for order_data in orders:
            order = order_data['order']
            status = order_data['status']
            status_timestamp = order_data['statusTimestamp']
            
            processed_order = {
                'coin': order['coin'],
                'side': order['side'],
                'limitPx': order['limitPx'],
                'sz': order['sz'],
                'origSz': order['origSz'],
                'oid': order['oid'],
                'timestamp': order['timestamp'],
                'orderType': order['orderType'],
                'tif': order['tif'],
                'reduceOnly': order['reduceOnly'],
                'status': status,
                'statusTimestamp': status_timestamp
            }
            processed_orders.append(processed_order)
            
        df = pd.DataFrame(processed_orders)
        
        # Convert timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['statusTimestamp'] = pd.to_datetime(df['statusTimestamp'], unit='ms')
        
        # Convert numeric columns
        numeric_columns = ['limitPx', 'sz', 'origSz']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # Convert side to lowercase for consistency and add position type
        if 'side' in df.columns:
            df['side'] = df['side'].str.lower()
            df['position_type'] = df['side'].map({'a': 'Short', 'b': 'Long'})
            
        # Calculate PnL for filled orders
        if all(col in df.columns for col in ['side', 'limitPx', 'sz', 'status']):
            # Sort by timestamp ascending for calculations
            df = df.sort_values('timestamp')
            
            # Calculate position size (negative for shorts, positive for longs)
            df['position_size'] = df.apply(
                lambda x: -float(x['sz']) if x['side'] == 'a' else float(x['sz']),
                axis=1
            )
            
            # Calculate cumulative position
            df['cumulative_position'] = df.groupby('coin')['position_size'].cumsum()
            
            # Calculate entry price for each position
            df['entry_price'] = df.groupby('coin')['limitPx'].transform('first')
            
            # Calculate PnL for filled orders
            df['pnl'] = df.apply(
                lambda x: (
                    (float(x['limitPx']) - float(x['entry_price'])) * float(x['sz'])
                    if x['side'] == 'b'  # Long position
                    else (float(x['entry_price']) - float(x['limitPx'])) * float(x['sz'])
                    if x['side'] == 'a'  # Short position
                    else 0
                ) if x['status'] == 'filled' else 0,
                axis=1
            )
            
            # Calculate cumulative PnL
            df['cumulative_pnl'] = df.groupby('coin')['pnl'].cumsum()
            
            # Calculate ROI
            df['roi'] = df['cumulative_pnl'] / (df['entry_price'] * df['position_size'].abs())
            
            # Sort back to descending order (newest first)
            df = df.sort_values('timestamp', ascending=False)
            
        return df

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
            
            # Sort by timestamp ascending for calculations
            df = df.sort_values('timestamp')
            
            # Calculate cumulative position
            df['cumulative_position'] = df.groupby('coin')['position_size'].cumsum()
            
            # Calculate weighted average price (VWAP) with zero size handling
            def calculate_vwap(group):
                """Calculate VWAP for a group of trades, handling zero sizes"""
                total_value = (group['px'] * group['sz'].abs()).sum()
                total_size = group['sz'].abs().sum()
                return total_value / total_size if total_size > 0 else group['px'].mean()
            
            # Calculate VWAP for each coin and transform to fill all rows
            df['vwap'] = df.groupby('coin').apply(calculate_vwap).reset_index(level=0, drop=True)
            
            # Sort back to descending order (newest first)
            df = df.sort_values('timestamp', ascending=False)
            
        return df 