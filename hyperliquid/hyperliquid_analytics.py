from typing import Dict, Any, List, Optional
from datetime import datetime
from llm_agent import LLMAgent, LLMProvider
from hyperliquid_data_service import HyperliquidDataService
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import logging
import json

logger = logging.getLogger(__name__)

class HyperliquidAnalytics:
    """Analytics class for Hyperliquid trading data"""
    
    def __init__(self, 
                 llm_agent: Optional[LLMAgent] = None,
                 data_service: Optional[HyperliquidDataService] = None):
        """Initialize the analytics service with optional LLM and data service"""
        self.data = data_service or HyperliquidDataService()
        
        if llm_agent is None:
            # Create LLM agent with Anthropic (API key will be loaded from environment)
            self.llm = LLMAgent(
                provider=LLMProvider.ANTHROPIC
            )
        else:
            self.llm = llm_agent
            
        self.memory = []

    def analyze_trader(self, user_address: str) -> Dict[str, Any]:
        """Analyze a trader's performance"""
        logger.info(f"Starting comprehensive analysis for trader {user_address}")
        
        # Get data
        trades = self.data.get_user_trades(user_address)
        trades_df = self.data.process_trades_to_dataframe(trades)

        print(trades_df.head())
        print("\nColumns:", trades_df.columns.tolist())
        print("\nData types:", trades_df.dtypes)
        
        # Calculate metrics
        # metrics = self._calculate_metrics(trades_df)
        
        # # Analyze trading style
        # style = self._analyze_trading_style(trades_df)
        
        # # Calculate reputation score
        # reputation = self._calculate_reputation_score(metrics, style)
        
        # # Generate insights using LLM
        # insights = self._generate_insights(metrics, style, reputation)
        
        # # Create visualizations
        # visualizations = self._create_visualizations(trades_df)
        
        # # Record this analysis in memory
        # self.memory.append({
        #     "timestamp": datetime.now().isoformat(),
        #     "user_address": user_address,
        #     "reputation_score": reputation.get('overall'),
        #     "trader_style": style.get('primary_style', 'Unknown')
        # })
        
        # return {
        #     "user_address": user_address,
        #     "timestamp": datetime.now().isoformat(),
        #     "metrics": metrics,
        #     "trading_style": style,
        #     "reputation_scores": reputation,
        #     "insights": insights,
        #     "visualizations": visualizations
        # }

    def _calculate_metrics(self, trades_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trading metrics"""
        metrics = {}
        
        if trades_df.empty:
            return metrics
            
        # Basic activity metrics
        first_date = trades_df['timestamp'].min()
        last_date = trades_df['timestamp'].max()
        total_days = (last_date - first_date).days + 1
        
        metrics['first_activity'] = first_date.isoformat()
        metrics['last_activity'] = last_date.isoformat()
        metrics['active_days'] = total_days
        metrics['total_trades'] = len(trades_df)
        metrics['activity_frequency'] = metrics['total_trades'] / total_days if total_days > 0 else 0
        
        # Trading patterns
        trades_df['hour'] = trades_df['timestamp'].dt.hour
        trades_df['day_of_week'] = trades_df['timestamp'].dt.day_name()
        
        metrics['hourly_distribution'] = trades_df.groupby('hour').size().to_dict()
        metrics['daily_distribution'] = trades_df.groupby('day_of_week').size().to_dict()
        
        # Find peak activity hours
        peak_hour = max(metrics['hourly_distribution'].items(), key=lambda x: x[1])[0]
        metrics['peak_activity_hour'] = peak_hour
        
        # Asset diversity
        if 'coin' in trades_df.columns:
            coin_counts = trades_df['coin'].value_counts()
            metrics['asset_distribution'] = coin_counts.to_dict()
            metrics['most_traded_asset'] = coin_counts.index[0] if not coin_counts.empty else None
            metrics['asset_count'] = len(coin_counts)
            
            # Calculate concentration
            total_trades = coin_counts.sum()
            if total_trades > 0:
                concentration = sum((count/total_trades)**2 for count in coin_counts)
                metrics['asset_concentration'] = concentration
                
                if concentration > 0.5:
                    metrics['diversification'] = "Low"
                elif concentration > 0.3:
                    metrics['diversification'] = "Moderate"
                else:
                    metrics['diversification'] = "High"
        
        # Performance metrics
        if 'position_value' in trades_df.columns:
            metrics['total_pnl'] = trades_df['position_value'].sum()
            metrics['win_rate'] = (trades_df['position_value'] > 0).mean()
            metrics['avg_win'] = trades_df.loc[trades_df['position_value'] > 0, 'position_value'].mean()
            metrics['avg_loss'] = abs(trades_df.loc[trades_df['position_value'] < 0, 'position_value'].mean())
            
            if metrics.get('avg_loss', 0) > 0:
                metrics['risk_reward_ratio'] = metrics.get('avg_win', 0) / metrics.get('avg_loss', 1)
            else:
                metrics['risk_reward_ratio'] = float('inf')
                
            # Calculate drawdown
            cumulative = trades_df['position_value'].cumsum()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            metrics['max_drawdown'] = abs(drawdown.min()) if not drawdown.empty else 0
        
        return metrics

    def _analyze_trading_style(self, trades_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trading style and patterns"""
        style = {}
        
        if trades_df.empty:
            return style
            
        # Calculate average holding time
        if 'coin' in trades_df.columns and 'timestamp' in trades_df.columns and 'side' in trades_df.columns:
            holding_times = []
            
            for coin in trades_df['coin'].unique():
                coin_trades = trades_df[trades_df['coin'] == coin].sort_values('timestamp')
                
                if len(coin_trades) > 1:
                    buys = coin_trades[coin_trades['side'].str.lower() == 'buy'].reset_index()
                    sells = coin_trades[coin_trades['side'].str.lower() == 'sell'].reset_index()
                    
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
        if 'size' in trades_df.columns:
            sizes = trades_df['size'].dropna()
            if not sizes.empty:
                size_std = sizes.std() / sizes.mean() if sizes.mean() > 0 else 0
                style['position_size_consistency'] = size_std
                
                if size_std < 0.3:
                    style['sizing_approach'] = 'Very Consistent'
                elif size_std < 0.7:
                    style['sizing_approach'] = 'Moderately Consistent'
                else:
                    style['sizing_approach'] = 'Variable'
        
        # Risk profile
        if 'leverage' in trades_df.columns:
            leverage = trades_df['leverage'].dropna()
            if not leverage.empty:
                avg_leverage = leverage.mean()
                style['avg_leverage'] = avg_leverage
                
                if avg_leverage < 2:
                    style['risk_profile'] = 'Conservative'
                elif avg_leverage < 5:
                    style['risk_profile'] = 'Moderate'
                elif avg_leverage < 10:
                    style['risk_profile'] = 'Aggressive'
                else:
                    style['risk_profile'] = 'Very Aggressive'
        
        return style

    def _calculate_reputation_score(self, metrics: Dict[str, Any], style: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate reputation score based on metrics and style"""
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
        total_trades = metrics.get('total_trades', 0)
        if total_trades > 1000:
            scores['experience'] = min(100, scores['experience'] + 15)
        elif total_trades > 500:
            scores['experience'] = min(100, scores['experience'] + 10)
        elif total_trades > 100:
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

    def _generate_insights(self, metrics: Dict[str, Any], style: Dict[str, Any], 
                          reputation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights using LLM"""
        prompt = f"""
        You are an expert cryptocurrency trading analyst. Analyze the following trader data from Hyperliquid and provide 
        insights and actionable recommendations. Focus on identifying strengths, weaknesses, and actionable suggestions.
        
        METRICS:
        {json.dumps(metrics, indent=2)}
        
        TRADING STYLE:
        {json.dumps(style, indent=2)}
        
        REPUTATION SCORES:
        {json.dumps(reputation, indent=2)}
        
        Provide your analysis in the following JSON format:
        {{
            "strengths": ["List 2-3 key strengths with specific metrics"],
            "weaknesses": ["List 2-3 key weaknesses with specific metrics"],
            "actionable_recommendations": ["List 3-4 specific, actionable recommendations"],
            "risk_assessment": "A brief risk assessment",
            "copytrade_worthiness": "Your assessment of whether this trader would be worth copying",
            "trader_personality": "Brief characterization of trader personality/style"
        }}
        
        Return ONLY valid JSON, no other text.
        """
        
        response = self.llm.generate_response(prompt)
        return self.llm.parse_json_response(response)

    def _create_visualizations(self, trades_df: pd.DataFrame) -> Dict[str, str]:
        """Create data visualizations"""
        visualizations = {}
        
        if trades_df.empty:
            return visualizations
            
        # Time distribution visualization
        if 'timestamp' in trades_df.columns:
            try:
                plt.figure(figsize=(10, 6))
                trades_df['hour'] = trades_df['timestamp'].dt.hour
                hourly_counts = trades_df.groupby('hour').size()
                hourly_counts.plot(kind='bar', color='skyblue')
                plt.title('Trading Activity by Hour of Day')
                plt.xlabel('Hour')
                plt.ylabel('Number of Trades')
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
        if 'coin' in trades_df.columns:
            try:
                plt.figure(figsize=(10, 6))
                coin_counts = trades_df['coin'].value_counts()
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
        
        # Performance over time
        if 'position_value' in trades_df.columns and 'timestamp' in trades_df.columns:
            try:
                plt.figure(figsize=(12, 6))
                trades_df = trades_df.sort_values('timestamp')
                trades_df['cumulative_pnl'] = trades_df['position_value'].cumsum()
                trades_df.plot(x='timestamp', y='cumulative_pnl', kind='line', figsize=(12, 6))
                plt.title('Cumulative Profit/Loss Over Time')
                plt.xlabel('Date')
                plt.ylabel('Cumulative P&L')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                visualizations['performance_chart'] = img_str
                plt.close()
            except Exception as e:
                logger.error(f"Error creating performance visualization: {str(e)}")
                
        return visualizations 