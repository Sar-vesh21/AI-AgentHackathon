import sqlite3
from typing import List, Dict, Any
import json
from datetime import datetime

'''
This class is the class used to store the data in the database.
INPUTS:
    db_path: The path to the database file
OUTPUTS:
    None
'''
class TraderDatabase:
    def __init__(self, db_path: str = "hyperliquid.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create traders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traders (
                    address TEXT PRIMARY KEY,
                    display_name TEXT,
                    account_value REAL,
                    daily_pnl REAL,
                    daily_roi REAL,
                    daily_volume REAL,
                    weekly_pnl REAL,
                    monthly_pnl REAL,
                    all_time_pnl REAL,
                    last_updated TIMESTAMP,
                    raw_data TEXT
                )
            ''')

            # Create trading_history table for historical data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trader_address TEXT,
                    timestamp TIMESTAMP,
                    metric_type TEXT,
                    metric_value REAL,
                    FOREIGN KEY (trader_address) REFERENCES traders(address)
                )
            ''')

            # Create trader_analysis table for storing analysis results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trader_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trader_address TEXT,
                    timestamp TIMESTAMP,
                    trading_style TEXT,
                    risk_profile TEXT,
                    performance_metrics TEXT,
                    market_behavior TEXT,
                    recommendations TEXT,
                    raw_analysis TEXT,
                    FOREIGN KEY (trader_address) REFERENCES traders(address)
                )
            ''')

            conn.commit()

    def store_traders(self, traders: List[Dict[str, Any]]):
        """Store or update trader data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()

            for trader in traders:
                cursor.execute('''
                    INSERT OR REPLACE INTO traders (
                        address, display_name, account_value, daily_pnl,
                        daily_roi, daily_volume, weekly_pnl, monthly_pnl,
                        all_time_pnl, last_updated, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trader['address'],
                    trader.get('display_name', ''),
                    trader.get('account_value', 0.0),
                    trader.get('daily_pnl', 0.0),
                    trader.get('daily_roi', 0.0),
                    trader.get('daily_volume', 0.0),
                    trader.get('weekly_pnl', 0.0),
                    trader.get('monthly_pnl', 0.0),
                    trader.get('all_time_pnl', 0.0),
                    now,
                    json.dumps(trader)  # Store complete raw data
                ))

                # Store historical metrics
                self._store_historical_metrics(cursor, trader, now)

            conn.commit()

    def _store_historical_metrics(self, cursor, trader: Dict[str, Any], timestamp: str):
        """Store historical metrics for tracking changes over time"""
        metrics = {
            'account_value': trader.get('account_value', 0.0),
            'daily_pnl': trader.get('daily_pnl', 0.0),
            'daily_roi': trader.get('daily_roi', 0.0),
            'daily_volume': trader.get('daily_volume', 0.0)
        }

        for metric_type, value in metrics.items():
            cursor.execute('''
                INSERT INTO trading_history (trader_address, timestamp, metric_type, metric_value)
                VALUES (?, ?, ?, ?)
            ''', (trader['address'], timestamp, metric_type, value))

    def get_trader(self, address: str) -> Dict[str, Any]:
        """Retrieve a specific trader's data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT raw_data FROM traders WHERE address = ?', (address,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None

    def get_top_traders(self, limit: int = 100, min_account_value: float = 0) -> List[Dict[str, Any]]:
        """Get top traders by account value"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT raw_data FROM traders 
                WHERE account_value >= ?
                ORDER BY account_value DESC 
                LIMIT ?
            ''', (min_account_value, limit))
            return [json.loads(row[0]) for row in cursor.fetchall()]

    def get_trader_history(self, address: str, metric_type: str, 
                          start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """Get historical data for a specific trader and metric"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT timestamp, metric_value 
                FROM trading_history 
                WHERE trader_address = ? AND metric_type = ?
            '''
            params = [address, metric_type]

            if start_time:
                query += ' AND timestamp >= ?'
                params.append(start_time)
            if end_time:
                query += ' AND timestamp <= ?'
                params.append(end_time)

            query += ' ORDER BY timestamp'

            cursor.execute(query, params)
            return [{'timestamp': row[0], 'value': row[1]} for row in cursor.fetchall()]

    def store_trader_analysis(self, trader_address: str, analysis: Dict[str, Any]):
        """Store analysis results for a trader"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()

            cursor.execute('''
                INSERT INTO trader_analysis (
                    trader_address, timestamp, trading_style, risk_profile,
                    performance_metrics, market_behavior, recommendations,
                    raw_analysis
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trader_address,
                now,
                json.dumps(analysis.get('trading_style', {})),
                json.dumps(analysis.get('risk_profile', {})),
                json.dumps(analysis.get('performance_metrics', {})),
                json.dumps(analysis.get('market_behavior', {})),
                json.dumps(analysis.get('recommendations', {})),
                json.dumps(analysis)  # Store complete raw analysis
            ))

            conn.commit()

    def get_trader_analysis(self, trader_address: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Get latest analysis for a trader"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT raw_analysis FROM trader_analysis 
                WHERE trader_address = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (trader_address, limit))
            return [json.loads(row[0]) for row in cursor.fetchall()]

    def get_traders_by_style(self, trading_style: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get traders matching a specific trading style"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.raw_data, ta.raw_analysis 
                FROM traders t
                JOIN trader_analysis ta ON t.address = ta.trader_address
                WHERE ta.trading_style LIKE ?
                ORDER BY t.account_value DESC
                LIMIT ?
            ''', (f'%{trading_style}%', limit))
            return [{'trader': json.loads(row[0]), 'analysis': json.loads(row[1])} 
                   for row in cursor.fetchall()]

    def get_all_trader_analyses(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get all trader analyses from the database
        
        Args:
            limit (int, optional): Maximum number of analyses to return. If None, returns all.
            
        Returns:
            List[Dict[str, Any]]: List of trader analyses with all fields properly parsed
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT id, trader_address, timestamp, trading_style, risk_profile,
                       performance_metrics, market_behavior, recommendations, raw_analysis
                FROM trader_analysis 
                ORDER BY id
            '''
            if limit is not None:
                query += ' LIMIT ?'
                cursor.execute(query, (limit,))
            else:
                cursor.execute(query)
            
            results = []
            for row in cursor.fetchall():
                analysis = {
                    'id': row[0],
                    'user_address': row[1],
                    'timestamp': row[2],
                    'trading_style': json.loads(row[3]) if row[3] else {},
                    'risk_profile': json.loads(row[4]) if row[4] else {},
                    'performance_metrics': json.loads(row[5]) if row[5] else {},
                    'market_behavior': json.loads(row[6]) if row[6] else {},
                    'recommendations': json.loads(row[7]) if row[7] else {},
                    'raw_analysis': json.loads(row[8]) if row[8] else {}
                }
                results.append(analysis)
            
            return results 