from typing import Dict, Any, List, Optional
from datetime import datetime
from .HyperliquidDataService import HyperliquidDataService
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import logging
import json

logger = logging.getLogger(__name__)


class HyperliquidAnalytics:
    """Analytics class for Hyperliquid trading data.
    
    This class provides comprehensive analysis of trader performance based on their order history.
    It calculates various metrics, analyzes trading style, and generates visualizations.
    The class also calls the data service to get the data for the trader.
    
    Attributes:
        data (HyperliquidDataService): Service for fetching trader data
        memory (List[Dict]): List of historical analyses
    """
    
    def __init__(self, data_service: Optional[HyperliquidDataService] = None):
        """Initialize the analytics service.
        
        Args:
            data_service (Optional[HyperliquidDataService]): Service for fetching trader data.
                If None, a new instance will be created.
        """
        self.data = data_service or HyperliquidDataService()
        self.memory = []

    def analyze_trader(self, user_address: str) -> Dict[str, Any]:
        """Analyze a trader's performance based on their order history.
        
        This method performs a comprehensive analysis including:
        - Basic trading metrics
        - Trading style analysis
        - Reputation scoring
        - Data visualizations
        
        Args:
            user_address (str): The Ethereum address of the trader to analyze
            
        Returns:
            Dict[str, Any]: Analysis results containing:
                - user_address (str): Trader's address
                - timestamp (str): Analysis timestamp
                - metrics (Dict): Trading performance metrics
                - trading_style (Dict): Trading style characteristics
                - reputation_scores (Dict): Reputation score components
                - visualizations (Dict): Base64 encoded visualization images
        """
        logger.info(f"Starting comprehensive analysis for trader {user_address}")
        
        # Get data
        orders = self.data.get_user_orders(user_address)
        orders_df = self.data.process_orders_to_dataframe(orders)
        
        # Calculate metrics
        metrics = self._calculate_metrics(orders_df)
        
        # Analyze trading style
        style = self._analyze_trading_style(orders_df)
        
        # Calculate reputation score
        reputation = self._calculate_reputation_score(metrics, style)
        
        # Create visualizations
        # visualizations = self._create_visualizations(orders_df)
        
        # Record this analysis in memory
        self.memory.append({
            "timestamp": datetime.now().isoformat(),
            "user_address": user_address,
            "reputation_score": reputation.get('overall'),
            "trader_style": style.get('primary_style', 'Unknown')
        })
        
        return {
            "user_address": user_address,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "trading_style": style,
            "reputation_scores": reputation,
            # "visualizations": visualizations
        }

    def _calculate_metrics(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trading performance metrics from order data.
        
        This method calculates various metrics including:
        - Activity metrics (total orders, frequency, etc.)
        - Trading patterns (hourly/daily distribution)
        - Asset diversity metrics
        - Performance metrics (PnL, win rate, etc.)
        
        Args:
            orders_df (pd.DataFrame): DataFrame containing order history
            
        Returns:
            Dict[str, Any]: Dictionary of calculated metrics
        """
        metrics = {}
        
        if orders_df.empty:
            return metrics
            
        # Basic activity metrics
        first_date = orders_df['timestamp'].min()
        last_date = orders_df['timestamp'].max()
        total_days = (last_date - first_date).days + 1
        
        metrics['first_activity'] = first_date.isoformat()
        metrics['last_activity'] = last_date.isoformat()
        metrics['active_days'] = total_days
        metrics['total_orders'] = len(orders_df)
        metrics['activity_frequency'] = metrics['total_orders'] / total_days if total_days > 0 else 0
        
        # Trading patterns
        orders_df['hour'] = orders_df['timestamp'].dt.hour
        orders_df['day_of_week'] = orders_df['timestamp'].dt.day_name()
        
        metrics['hourly_distribution'] = orders_df.groupby('hour').size().to_dict()
        metrics['daily_distribution'] = orders_df.groupby('day_of_week').size().to_dict()
        
        # Find peak activity hours
        peak_hour = max(metrics['hourly_distribution'].items(), key=lambda x: x[1])[0]
        metrics['peak_activity_hour'] = peak_hour
        
        # Overall position bias analysis (including all orders)
        if 'side' in orders_df.columns and 'sz' in orders_df.columns:
            # Calculate total volume for buys and sells
            buy_orders = orders_df[orders_df['side'] == 'b']
            sell_orders = orders_df[orders_df['side'] == 'a']
            
            total_buy_volume = buy_orders['sz'].astype(float).sum()
            total_sell_volume = sell_orders['sz'].astype(float).sum()
            
            metrics['total_buy_volume'] = total_buy_volume
            metrics['total_sell_volume'] = total_sell_volume
            
            # Determine overall position bias
            if total_buy_volume > total_sell_volume * 1.1:  # 10% threshold
                metrics['position_bias'] = 'Long'
            elif total_sell_volume > total_buy_volume * 1.1:
                metrics['position_bias'] = 'Short'
            else:
                metrics['position_bias'] = 'Neutral'
            
            # Calculate overall long/short ratio
            total_volume = total_buy_volume + total_sell_volume
            if total_volume > 0:
                metrics['long_short_ratio'] = total_buy_volume / total_sell_volume if total_sell_volume > 0 else float('inf')
                metrics['buy_percentage'] = (total_buy_volume / total_volume) * 100
                metrics['sell_percentage'] = (total_sell_volume / total_volume) * 100
        
        # Asset diversity
        if 'coin' in orders_df.columns:
            coin_counts = orders_df['coin'].value_counts()
            metrics['asset_distribution'] = coin_counts.to_dict()
            metrics['most_traded_asset'] = coin_counts.index[0] if not coin_counts.empty else None
            metrics['asset_count'] = len(coin_counts)
            
            # Calculate concentration
            total_orders = coin_counts.sum()
            if total_orders > 0:
                concentration = sum((count/total_orders)**2 for count in coin_counts)
                metrics['asset_concentration'] = concentration
                
                if concentration > 0.5:
                    metrics['diversification'] = "Low"
                elif concentration > 0.3:
                    metrics['diversification'] = "Moderate"
                else:
                    metrics['diversification'] = "High"
        
        # Order type analysis
        if 'orderType' in orders_df.columns:
            order_type_counts = orders_df['orderType'].value_counts()
            metrics['order_type_distribution'] = order_type_counts.to_dict()
            metrics['most_common_order_type'] = order_type_counts.index[0] if not order_type_counts.empty else None
        
        # Time in force analysis
        if 'tif' in orders_df.columns:
            tif_counts = orders_df['tif'].value_counts()
            metrics['time_in_force_distribution'] = tif_counts.to_dict()
            metrics['most_common_tif'] = tif_counts.index[0] if not tif_counts.empty else None
        
        # Performance metrics
        if all(col in orders_df.columns for col in ['limitPx', 'sz', 'side', 'status', 'coin']):
            print(f"ENTERED")
            # Sort by timestamp for position tracking
            orders_df = orders_df.sort_values('timestamp')
            
            # Initialize position tracking
            positions = {}  # {coin: {'entry_price': price, 'size': size, 'side': side}}
            trades = []     # List of completed trades with PnL
            
            # Process each order
            for _, order in orders_df.iterrows():
                
                if order['status'] != 'filled':
                    continue
                print(f"ORDER: {order}")
                    
                coin = order['coin']
                side = order['side']
                price = float(order['limitPx'])
                size = float(order['sz'])
                
                print(f"COIN: {coin} SIDE: {side} PRICE: {price} SIZE: {size}")
                
                if size == 0:
                    continue
                if coin not in positions:
                    print(f"OPENING NEW POSITION : {coin} {size} {side}")
                    # Opening a new position
                    positions[coin] = {
                        'entry_price': price,
                        'size': size,
                        'side': side
                    }
                else:
                    # Closing or reducing an existing position
                    print(f"REDUCING POSITION")
                    pos = positions[coin]
                    # Check if this is a closing order
                    if (pos['side'] == 'b' and side == 'a') or (pos['side'] == 'a' and side == 'b'):
                        # Calculate PnL
                        if pos['side'] == 'b':  # Long position
                            pnl = (price - pos['entry_price']) * min(size, pos['size'])
                        else:  # Short position
                            pnl = (pos['entry_price'] - price) * min(size, pos['size'])
                            
                        trades.append({
                            'coin': coin,
                            'entry_price': pos['entry_price'],
                            'exit_price': price,
                            'size': min(size, pos['size']),
                            'pnl': pnl,
                            'entry_side': pos['side']
                        })
                        
                        # Update or remove position
                        if size >= pos['size']:
                            del positions[coin]
                        else:
                            pos['size'] -= size
                    else:
                        # Adding to existing position - update average entry price
                        total_size = pos['size'] + size
                        pos['entry_price'] = ((pos['entry_price'] * pos['size']) + (price * size)) / total_size
                        pos['size'] = total_size
            
            # Calculate metrics from completed trades
            if trades:
                print(f"Trades: {trades}")
                trades_df = pd.DataFrame(trades)
                metrics['total_trades'] = len(trades)
                metrics['total_pnl'] = trades_df['pnl'].sum()
                metrics['win_rate'] = (trades_df['pnl'] > 0).mean()
                metrics['avg_win'] = trades_df.loc[trades_df['pnl'] > 0, 'pnl'].mean()
                metrics['avg_loss'] = abs(trades_df.loc[trades_df['pnl'] < 0, 'pnl'].mean())
                
                if metrics.get('avg_loss', 0) > 0:
                    metrics['risk_reward_ratio'] = metrics.get('avg_win', 0) / metrics.get('avg_loss', 1)
                else:
                    metrics['risk_reward_ratio'] = float('inf')
                
                # Calculate drawdown
                cumulative = trades_df['pnl'].cumsum()
                running_max = cumulative.cummax()
                drawdown = (cumulative - running_max) / running_max
                metrics['max_drawdown'] = abs(drawdown.min()) if not drawdown.empty else 0
                
                # Position size metrics
                metrics['avg_position_size'] = trades_df['size'].mean()
                metrics['max_position_size'] = trades_df['size'].max()
        
        return metrics

    def _analyze_trading_style(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trading style and patterns from order data.
        
        This method determines:
        - Average holding period
        - Primary trading style (Scalper/Day Trader/Swing Trader/Position Trader)
        - Position sizing consistency
        
        Args:
            orders_df (pd.DataFrame): DataFrame containing order history
            
        Returns:
            Dict[str, Any]: Dictionary of trading style characteristics
        """
        style = {}
        
        if orders_df.empty:
            return style
            
        # Calculate average holding time
        if 'coin' in orders_df.columns and 'timestamp' in orders_df.columns and 'side' in orders_df.columns:
            holding_times = []
            
            for coin in orders_df['coin'].unique():
                coin_trades = orders_df[orders_df['coin'] == coin].sort_values('timestamp')
                
                if len(coin_trades) > 1:
                    buys = coin_trades[coin_trades['side'] == 'b'].reset_index()
                    sells = coin_trades[coin_trades['side'] == 'a'].reset_index()
                    
                    for i in range(min(len(buys), len(sells))):
                        if sells.loc[i, 'timestamp'] > buys.loc[i, 'timestamp']:
                            holding_period = (sells.loc[i, 'timestamp'] - buys.loc[i, 'timestamp']).total_seconds() / 3600
                            holding_times.append(holding_period)
            
            if holding_times:
                avg_holding = np.mean(holding_times)
                style['avg_holding_period_hours'] = avg_holding
                
                if avg_holding < 1:
                    style['primary_style'] = 'Scalper'
                elif avg_holding < 24:
                    style['primary_style'] = 'Day Trader'
                elif avg_holding < 168:  # 7 days
                    style['primary_style'] = 'Swing Trader'
                else:
                    style['primary_style'] = 'Position Trader'
        
        # Position sizing consistency
        if 'sz' in orders_df.columns:
            sizes = orders_df['sz'].dropna()
            if not sizes.empty:
                size_std = sizes.std() / sizes.mean() if sizes.mean() > 0 else 0
                style['position_size_consistency'] = size_std
                
                if size_std < 0.3:
                    style['sizing_approach'] = 'Very Consistent'
                elif size_std < 0.7:
                    style['sizing_approach'] = 'Moderately Consistent'
                else:
                    style['sizing_approach'] = 'Variable'
        
        return style

    def _calculate_reputation_score(self, metrics: Dict[str, Any], style: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate reputation score based on metrics and trading style.
        
        The reputation score is calculated using:
        - Experience (trading duration and volume)
        - Consistency (position sizing)
        - Risk management
        - Performance (win rate)
        
        Args:
            metrics (Dict[str, Any]): Trading performance metrics
            style (Dict[str, Any]): Trading style characteristics
            
        Returns:
            Dict[str, Any]: Dictionary containing reputation score components
        """
        scores = {
            'overall': 50,  # Base score
            'experience': 50,
            'consistency': 50,
            'risk_management': 50,
            'performance': 50
        }
        
        # Experience score
        active_days = metrics.get('active_days', 0)
        if active_days > 365:
            scores['experience'] = 100
        elif active_days > 180:
            scores['experience'] = 85
        elif active_days > 90:
            scores['experience'] = 70
        elif active_days > 30:
            scores['experience'] = 55
        else:
            scores['experience'] = 40
            
        # Activity volume adjustment
        total_orders = metrics.get('total_orders', 0)
        if total_orders > 1000:
            scores['experience'] = min(100, scores['experience'] + 15)
        elif total_orders > 500:
            scores['experience'] = min(100, scores['experience'] + 10)
        elif total_orders > 100:
            scores['experience'] = min(100, scores['experience'] + 5)
            
        # Consistency score
        if style.get('sizing_approach') == 'Very Consistent':
            scores['consistency'] = 90
        elif style.get('sizing_approach') == 'Moderately Consistent':
            scores['consistency'] = 70
        elif style.get('sizing_approach') == 'Variable':
            scores['consistency'] = 40
            
        # Risk management score
        risk_profile = style.get('risk_profile', '')
        if risk_profile == 'Conservative':
            scores['risk_management'] = 90
        elif risk_profile == 'Moderate':
            scores['risk_management'] = 75
        elif risk_profile == 'Aggressive':
            scores['risk_management'] = 50
        elif risk_profile == 'Very Aggressive':
            scores['risk_management'] = 30
            
        # Performance score
        win_rate = metrics.get('win_rate', 0)
        if win_rate > 0.6:
            scores['performance'] = 90
        elif win_rate > 0.5:
            scores['performance'] = 70
        elif win_rate > 0.4:
            scores['performance'] = 50
        else:
            scores['performance'] = 30
            
        # Calculate overall score (weighted average)
        scores['overall'] = int(0.25 * scores['experience'] + 
                              0.20 * scores['consistency'] + 
                              0.25 * scores['risk_management'] + 
                              0.30 * scores['performance'])
                              
        return scores

    def _create_visualizations(self, orders_df: pd.DataFrame) -> Dict[str, str]:
        """Create data visualizations from order data.
        
        This method generates:
        - Hourly trading activity distribution
        - Asset trading distribution
        
        Args:
            orders_df (pd.DataFrame): DataFrame containing order history
            
        Returns:
            Dict[str, str]: Dictionary of base64 encoded visualization images
        """
        visualizations = {}
        
        if orders_df.empty:
            return visualizations
            
        # Time distribution visualization
        if 'timestamp' in orders_df.columns:
            try:
                plt.figure(figsize=(10, 6))
                orders_df['hour'] = orders_df['timestamp'].dt.hour
                hourly_counts = orders_df.groupby('hour').size()
                hourly_counts.plot(kind='bar', color='skyblue')
                plt.title('Trading Activity by Hour of Day')
                plt.xlabel('Hour')
                plt.ylabel('Number of Orders')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                visualizations['hourly_activity'] = img_str
                plt.close()
            except Exception as e:
                logger.error(f"Error creating time distribution visualization: {str(e)}")
        
        # Asset distribution visualization
        if 'coin' in orders_df.columns:
            try:
                plt.figure(figsize=(10, 6))
                coin_counts = orders_df['coin'].value_counts()
                if len(coin_counts) > 10:
                    coin_counts = coin_counts.head(10)
                coin_counts.plot(kind='pie', autopct='%1.1f%%')
                plt.title('Distribution of Trading Activity by Asset')
                plt.ylabel('')
                plt.tight_layout()
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                visualizations['asset_distribution'] = img_str
                plt.close()
            except Exception as e:
                logger.error(f"Error creating asset distribution visualization: {str(e)}")
        
        return visualizations 