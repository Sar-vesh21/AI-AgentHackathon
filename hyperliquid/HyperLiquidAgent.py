import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import time
from typing import Dict, List, Any, Optional, Union
from openai import OpenAI
import logging
import matplotlib.pyplot as plt
import io
import base64

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HyperliquidAgent:
    """
    An AI agent for analyzing Hyperliquid trading data that incorporates LLM capabilities
    for generating insights and recommendations.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the Hyperliquid AI agent.
        
        Args:
            openai_api_key: API key for OpenAI. If not provided, will try to get from environment.
        """
        self.api_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"Content-Type": "application/json"}
        
        # Initialize LLM client
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("No OpenAI API key provided. LLM functionality will be disabled.")
            self.llm_enabled = False
        else:
            self.llm_client = OpenAI(api_key=self.openai_api_key)
            self.llm_enabled = True
            
        # Cache for API responses to avoid repeated calls
        self.cache = {}
        
        # Memory of past analyses and user interactions
        self.memory = []
    
    def get_historical_orders(self, user_address: str) -> List[Dict[str, Any]]:
        """
        Retrieve historical orders for a specific user from Hyperliquid API.
        Implements caching to avoid redundant API calls.
        
        Args:
            user_address: User's wallet address in 42-character hexadecimal format
            
        Returns:
            List of order dictionaries
        """
        cache_key = f"orders_{user_address}"
        if cache_key in self.cache:
            logger.info(f"Using cached orders for {user_address}")
            return self.cache[cache_key]
            
        logger.info(f"Fetching historical orders for {user_address}")
        payload = {
            "type": "historicalOrders",
            "user": user_address
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            orders = response.json()
            
            # Cache the results
            self.cache[cache_key] = orders
            return orders
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return []
    
    def get_user_trades(self, user_address: str) -> List[Dict[str, Any]]:
        """
        Retrieve executed trades for a specific user.
        
        Args:
            user_address: User's wallet address
            
        Returns:
            List of trade dictionaries
        """
        cache_key = f"trades_{user_address}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        logger.info(f"Fetching trades for {user_address}")
        payload = {
            "type": "userFills",
            "user": user_address
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            trades = response.json()
            
            # Cache the results
            self.cache[cache_key] = trades
            return trades
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return []
    
    def get_market_data(self) -> Dict[str, Any]:
        """
        Retrieve current market data for all available coins.
        
        Returns:
            Dictionary of market data
        """
        cache_key = "market_data"
        # Only use cache if less than 5 minutes old
        if cache_key in self.cache and time.time() - self.cache.get(f"{cache_key}_time", 0) < 300:
            return self.cache[cache_key]
            
        logger.info("Fetching market data")
        payload = {
            "type": "allMids"
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            market_data = response.json()
            
            # Cache the results with timestamp
            self.cache[cache_key] = market_data
            self.cache[f"{cache_key}_time"] = time.time()
            return market_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {}
    
    def process_orders_to_dataframe(self, orders: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert raw orders data to pandas DataFrame with proper types.
        
        Args:
            orders: List of order dictionaries from the API
            
        Returns:
            Processed DataFrame
        """
        if not orders:
            return pd.DataFrame()
            
        # Create DataFrame
        df = pd.DataFrame(orders)
        
        # Convert timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Handle nested JSON structures if present
        # (Exact structure depends on the API response format)
        
        return df
    
    def process_trades_to_dataframe(self, trades: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert raw trades data to pandas DataFrame with proper types.
        
        Args:
            trades: List of trade dictionaries from the API
            
        Returns:
            Processed DataFrame
        """
        if not trades:
            return pd.DataFrame()
            
        # Create DataFrame
        df = pd.DataFrame(trades)
        
        # Convert timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Calculate profit/loss if needed fields are available
        if all(col in df.columns for col in ['price', 'size', 'side']):
            # Apply multiplier based on side (buy/sell)
            df['side_multiplier'] = df['side'].apply(lambda x: 1 if x.lower() == 'buy' else -1)
            df['position_value'] = df['price'] * df['size'] * df['side_multiplier']
        
        return df
    
    def calculate_trader_metrics(self, orders_df: pd.DataFrame, trades_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate comprehensive trader performance metrics.
        
        Args:
            orders_df: DataFrame of orders
            trades_df: DataFrame of executed trades
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        if orders_df.empty and trades_df.empty:
            return metrics
        
        # Use trades dataframe for performance metrics if available
        df_to_use = trades_df if not trades_df.empty else orders_df
        
        # Basic activity metrics
        first_date = df_to_use['timestamp'].min()
        last_date = df_to_use['timestamp'].max()
        total_days = (last_date - first_date).days + 1
        
        metrics['first_activity'] = first_date.isoformat()
        metrics['last_activity'] = last_date.isoformat()
        metrics['active_days'] = total_days
        metrics['total_orders'] = len(orders_df) if not orders_df.empty else 0
        metrics['total_trades'] = len(trades_df) if not trades_df.empty else 0
        metrics['activity_frequency'] = metrics['total_trades'] / total_days if total_days > 0 else 0
        
        # Trading patterns
        if not df_to_use.empty:
            df_to_use['hour'] = df_to_use['timestamp'].dt.hour
            df_to_use['day_of_week'] = df_to_use['timestamp'].dt.day_name()
            
            metrics['hourly_distribution'] = df_to_use.groupby('hour').size().to_dict()
            metrics['daily_distribution'] = df_to_use.groupby('day_of_week').size().to_dict()
            
            # Find peak activity hours
            peak_hour = max(metrics['hourly_distribution'].items(), key=lambda x: x[1])[0]
            metrics['peak_activity_hour'] = peak_hour
            
        # Asset diversity and preferences
        if 'coin' in df_to_use.columns:
            coin_counts = df_to_use['coin'].value_counts()
            metrics['asset_distribution'] = coin_counts.to_dict()
            metrics['most_traded_asset'] = coin_counts.index[0] if not coin_counts.empty else None
            metrics['asset_count'] = len(coin_counts)
            
            # Calculate concentration (Herfindahl-Hirschman Index)
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
        
        # Performance metrics (if trade data available)
        if not trades_df.empty and 'position_value' in trades_df.columns:
            # Calculate profit/loss metrics
            metrics['total_pnl'] = trades_df['position_value'].sum()
            metrics['win_rate'] = (trades_df['position_value'] > 0).mean()
            metrics['avg_win'] = trades_df.loc[trades_df['position_value'] > 0, 'position_value'].mean()
            metrics['avg_loss'] = abs(trades_df.loc[trades_df['position_value'] < 0, 'position_value'].mean())
            
            if metrics.get('avg_loss', 0) > 0:
                metrics['risk_reward_ratio'] = metrics.get('avg_win', 0) / metrics.get('avg_loss', 1)
            else:
                metrics['risk_reward_ratio'] = float('inf')
                
            # Calculate drawdown
            # This is simplified - a real implementation would be more comprehensive
            cumulative = trades_df['position_value'].cumsum()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            metrics['max_drawdown'] = abs(drawdown.min()) if not drawdown.empty else 0
        
        return metrics
    
    def analyze_trading_style(self, orders_df: pd.DataFrame, trades_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the trading style and patterns.
        
        Args:
            orders_df: DataFrame of orders
            trades_df: DataFrame of executed trades
            
        Returns:
            Dictionary of trading style characteristics
        """
        style = {}
        
        if orders_df.empty and trades_df.empty:
            return style
            
        # Use trades dataframe for style analysis if available
        df_to_use = trades_df if not trades_df.empty else orders_df
        
        # Calculate average holding time (if we can pair entries and exits)
        if 'coin' in df_to_use.columns and 'timestamp' in df_to_use.columns and 'side' in df_to_use.columns:
            holding_times = []
            
            for coin in df_to_use['coin'].unique():
                coin_trades = df_to_use[df_to_use['coin'] == coin].sort_values('timestamp')
                
                if len(coin_trades) > 1:
                    # Pair buys and sells (simplified approach)
                    buys = coin_trades[coin_trades['side'].str.lower() == 'buy'].reset_index()
                    sells = coin_trades[coin_trades['side'].str.lower() == 'sell'].reset_index()
                    
                    # Match trades by their sequence
                    for i in range(min(len(buys), len(sells))):
                        if sells.loc[i, 'timestamp'] > buys.loc[i, 'timestamp']:
                            holding_period = (sells.loc[i, 'timestamp'] - buys.loc[i, 'timestamp']).total_seconds() / 3600
                            holding_times.append(holding_period)
            
            if holding_times:
                avg_holding = np.mean(holding_times)
                style['avg_holding_period_hours'] = avg_holding
                
                # Classify trading style based on holding period
                if avg_holding < 1:
                    style['primary_style'] = 'Scalper'
                elif avg_holding < 24:
                    style['primary_style'] = 'Day Trader'
                elif avg_holding < 168:  # 7 days
                    style['primary_style'] = 'Swing Trader'
                else:
                    style['primary_style'] = 'Position Trader'
        
        # Determine if the trader follows trends or is contrarian
        # (Would require market data correlation analysis)
        
        # Check consistency in position sizing
        if 'size' in df_to_use.columns:
            sizes = df_to_use['size'].dropna()
            if not sizes.empty:
                size_std = sizes.std() / sizes.mean() if sizes.mean() > 0 else 0
                style['position_size_consistency'] = size_std
                
                if size_std < 0.3:
                    style['sizing_approach'] = 'Very Consistent'
                elif size_std < 0.7:
                    style['sizing_approach'] = 'Moderately Consistent'
                else:
                    style['sizing_approach'] = 'Variable'
        
        # Risk profile based on leverage (if available)
        if 'leverage' in df_to_use.columns:
            leverage = df_to_use['leverage'].dropna()
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
    
    def calculate_reputation_score(self, metrics: Dict[str, Any], style: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate a comprehensive reputation score based on trading metrics and style.
        
        Args:
            metrics: Dictionary of trader metrics
            style: Dictionary of trading style characteristics
            
        Returns:
            Dictionary with overall and category scores
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
            
        # Adjust consistency based on trading frequency
        activity_frequency = metrics.get('activity_frequency', 0)
        if activity_frequency > 3:
            scores['consistency'] = min(100, scores['consistency'] + 10)
        elif activity_frequency < 0.5 and active_days > 30:
            scores['consistency'] = max(0, scores['consistency'] - 10)
            
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
            
        # Adjust risk score based on drawdown
        max_drawdown = metrics.get('max_drawdown', 1)
        if max_drawdown < 0.1:
            scores['risk_management'] = min(100, scores['risk_management'] + 15)
        elif max_drawdown > 0.3:
            scores['risk_management'] = max(0, scores['risk_management'] - 20)
            
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
            
        # Adjust performance based on risk/reward ratio
        risk_reward = metrics.get('risk_reward_ratio', 0)
        if risk_reward > 2:
            scores['performance'] = min(100, scores['performance'] + 20)
        elif risk_reward > 1:
            scores['performance'] = min(100, scores['performance'] + 10)
        elif risk_reward < 0.8:
            scores['performance'] = max(0, scores['performance'] - 15)
            
        # Calculate overall score (weighted average)
        scores['overall'] = int(0.25 * scores['experience'] + 
                              0.20 * scores['consistency'] + 
                              0.25 * scores['risk_management'] + 
                              0.30 * scores['performance'])
                              
        return scores
        
    def generate_llm_insights(self, metrics: Dict[str, Any], style: Dict[str, Any], 
                            reputation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to generate advanced insights based on the trader analysis.
        
        Args:
            metrics: Dictionary of trader metrics
            style: Dictionary of trading style characteristics
            reputation: Dictionary with reputation scores
            
        Returns:
            Dictionary of insights and recommendations
        """
        if not self.llm_enabled:
            logger.warning("LLM functionality is disabled. Cannot generate insights.")
            return {
                "warning": "LLM insights unavailable - API key not configured",
                "basic_insights": [
                    f"Trader follows a {style.get('primary_style', 'unknown')} approach",
                    f"Overall reputation score: {reputation.get('overall', 'N/A')}/100"
                ]
            }
            
        # Prepare the input for the LLM
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
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1000
            )
            
            # Extract the text from the response
            insight_text = response.choices[0].message.content.strip()
            
            # Parse the JSON response
            try:
                insights = json.loads(insight_text)
                return insights
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return {"error": "Failed to generate structured insights", "raw_text": insight_text}
                
        except Exception as e:
            logger.error(f"Error generating LLM insights: {str(e)}")
            return {"error": f"Failed to generate insights: {str(e)}"}
    
    def create_visualizations(self, orders_df: pd.DataFrame, trades_df: pd.DataFrame) -> Dict[str, str]:
        """
        Create data visualizations to help understand trader behavior.
        
        Args:
            orders_df: DataFrame of orders
            trades_df: DataFrame of executed trades
            
        Returns:
            Dictionary of base64-encoded visualizations
        """
        visualizations = {}
        
        if orders_df.empty and trades_df.empty:
            return visualizations
            
        # Use trades dataframe for visualizations if available
        df_to_use = trades_df if not trades_df.empty else orders_df
        
        # Time distribution visualization
        if 'timestamp' in df_to_use.columns:
            try:
                plt.figure(figsize=(10, 6))
                df_to_use['hour'] = df_to_use['timestamp'].dt.hour
                hourly_counts = df_to_use.groupby('hour').size()
                hourly_counts.plot(kind='bar', color='skyblue')
                plt.title('Trading Activity by Hour of Day')
                plt.xlabel('Hour')
                plt.ylabel('Number of Trades')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Convert plot to base64 string
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                visualizations['hourly_activity'] = img_str
                plt.close()
            except Exception as e:
                logger.error(f"Error creating time distribution visualization: {str(e)}")
        
        # Asset distribution visualization
        if 'coin' in df_to_use.columns:
            try:
                plt.figure(figsize=(10, 6))
                coin_counts = df_to_use['coin'].value_counts()
                # Limit to top 10 assets if there are many
                if len(coin_counts) > 10:
                    coin_counts = coin_counts.head(10)
                coin_counts.plot(kind='pie', autopct='%1.1f%%')
                plt.title('Distribution of Trading Activity by Asset')
                plt.ylabel('')
                plt.tight_layout()
                
                # Convert plot to base64 string
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                visualizations['asset_distribution'] = img_str
                plt.close()
            except Exception as e:
                logger.error(f"Error creating asset distribution visualization: {str(e)}")
        
        # Performance over time (if PnL data available)
        if not trades_df.empty and 'position_value' in trades_df.columns and 'timestamp' in trades_df.columns:
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
                
                # Convert plot to base64 string
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                visualizations['performance_chart'] = img_str
                plt.close()
            except Exception as e:
                logger.error(f"Error creating performance visualization: {str(e)}")
                
        return visualizations
    
    def analyze_trader(self, user_address: str) -> Dict[str, Any]:
        """
        Main function to analyze a trader and generate comprehensive insights.
        
        Args:
            user_address: User's wallet address
            
        Returns:
            Dictionary with complete analysis results
        """
        logger.info(f"Starting comprehensive analysis for trader {user_address}")
        
        # Get data
        orders = self.get_historical_orders(user_address)
        trades = self.get_user_trades(user_address)
        
        # Process data
        orders_df = self.process_orders_to_dataframe(orders)
        trades_df = self.process_trades_to_dataframe(trades)
        
        # Generate analysis
        metrics = self.calculate_trader_metrics(orders_df, trades_df)
        style = self.analyze_trading_style(orders_df, trades_df)
        reputation = self.calculate_reputation_score(metrics, style)
        
        # Generate LLM insights
        insights = self.generate_llm_insights(metrics, style, reputation)
        
        # Create visualizations
        visualizations = self.create_visualizations(orders_df, trades_df)
        
        # Record this analysis in memory
        self.memory.append({
            "timestamp": datetime.now().isoformat(),
            "user_address": user_address,
            "reputation_score": reputation.get('overall'),
            "trader_style": style.get('primary_style', 'Unknown')
        })
        
        # Return complete results
        return {
            "user_address": user_address,
            "analysis_timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "trading_style": style,
            "reputation_scores": reputation,
            "insights": insights,
            "visualizations": visualizations
        }
    
    def ask_question(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        Allow users to ask questions about analysis results using natural language.
        
        Args:
            question: Natural language question from the user
            context: Optional context from previous analysis
            
        Returns:
            Natural language response to the question
        """
        if not self.llm_enabled:
            return "Sorry, LLM functionality is disabled. Please provide an OpenAI API key to enable this feature."
            
        # Prepare context for the LLM
        context_str = ""
        if context:
            context_str = json.dumps(context, indent=2)
        else:
            # If no specific context, provide general information from memory
            if self.memory:
                context_str = "Previous analyses: " + json.dumps(self.memory, indent=2)
            else:
                context_str = "No previous analyses available."
        
        # Prepare the prompt
        prompt = f"""
        You are an expert cryptocurrency trading analyst assistant specializing in the Hyperliquid exchange.
        
        USER QUESTION: {question}
        
        CONTEXT INFORMATION:
        {context_str}
        
        Please answer the question based on the provided context. If the question cannot be answered with the 
        available information, explain what additional data would be needed and how it could be obtained.
        Be concise, accurate, and helpful. Provide specific data points when available.
        """
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            # Extract the response text
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            logger.error(f"Error processing question with LLM: {str(e)}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"
    
    def recommend_traders(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Recommend traders to follow based on specified criteria and past analyses.
        
        Args:
            criteria: Optional dictionary of criteria for recommendations
            
        Returns:
            List of recommended traders with rationale
        """
        if not self.memory or len(self.memory) < 2:
            return [{"error": "Not enough trader data to make recommendations"}]
            
        # Default criteria if none provided
        if criteria is None:
            criteria = {
                "min_reputation_score": 70,
                "preferred_styles": ["Any"],
                "min_trades": 50
            }
            
        # Filter based on criteria
        candidates = []
        for trader in self.memory:
            # Skip traders with no reputation score
            if trader.get("reputation_score") is None:
                continue
                
            # Check minimum reputation score
            if trader["reputation_score"] < criteria.get("min_reputation_score", 0):
                continue
                
            # Check trading style
            if ("Any" not in criteria.get("preferred_styles", ["Any"]) and 
                trader.get("trader_style") not in criteria.get("preferred_styles", ["Any"])):
                continue
                
            # Add to candidates
            candidates.append(trader)
        
        # Sort by reputation score (descending)
        candidates.sort(key=lambda x: x.get("reputation_score", 0), reverse=True)
        
        # Get top 3 recommendations
        recommendations = []
        for candidate in candidates[:3]:
            # Get more details about this trader
            details = self.generate_recommendation_rationale(candidate)
            recommendations.append({
                "user_address": candidate["user_address"],
                "reputation_score": candidate["reputation_score"],
                "trader_style": candidate.get("trader_style", "Unknown"),
                "rationale": details
            })
            
        return recommendations
        
    def generate_recommendation_rationale(self, trader_info: Dict[str, Any]) -> str:
        """
        Generate a rationale for why a trader is recommended (using LLM).
        
        Args:
            trader_info: Basic trader information
            
        Returns:
            String with recommendation rationale
        """
        if not self.llm_enabled:
            return f"Trader has a reputation score of {trader_info.get('reputation_score', 'N/A')}"
            
        try:
            # Get additional data if available in cache
            user_address = trader_info["user_address"]
            additional_data = {}
            
            cache_keys = [
                f"trades_{user_address}", 
                f"orders_{user_address}"
            ]
            
            for key in cache_keys:
                if key in self.cache:
                    additional_data[key.split('_')[0]] = "Data available"
            
            # Create prompt
            prompt = f"""
            You are a cryptocurrency trading expert. Create a brief rationale for why someone might want to 
            follow this Hyperliquid trader:
            
            Trader address: {user_address}
            Reputation score: {trader_info.get('reputation_score', 'Unknown')}/100
            Trading style: {trader_info.get('trader_style', 'Unknown')}
            
            Additional context: {json.dumps(additional_data)}
            
            Write 2-3 sentences explaining why this trader might be worth following. Be specific and focus on 
            the reputation score and trading style. Do not invent specific statistics that aren't mentioned.
            """
            
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using a smaller model for this task
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating recommendation rationale: {str(e)}")
            return f"High-reputation {trader_info.get('trader_style', 'trader')}"
    
    def monitor_social_sentiment(self, asset: str) -> Dict[str, Any]:
        """
        Monitor social media sentiment for a specific asset on Hyperliquid.
        
        Args:
            asset: Asset symbol to monitor
            
        Returns:
            Dictionary with sentiment analysis
        """
        # Placeholder for actual social media API integration
        logger.info(f"Social sentiment monitoring requested for {asset}")
        
        if not self.llm_enabled:
            return {"error": "LLM functionality required for sentiment analysis"}
            
        # For demonstration, we'll generate simulated sentiment
        try:
            # Use the LLM to create realistic simulated sentiment analysis
            prompt = f"""
            You are a cryptocurrency social media sentiment analyzer. Create a realistic but fictional 
            social sentiment analysis for {asset} on the Hyperliquid exchange.
            
            Return a JSON object with the following structure:
            {{
                "sentiment_score": [number between -100 and 100],
                "volume": [number of mentions, realistic for crypto],
                "trending_topics": [list of 3-5 related trending topics],
                "key_influencers": [list of 2-3 fictional influencer handles],
                "common_phrases": [list of 3-5 common phrases being used]
            }}
            
            Return ONLY valid JSON, no other text.
            """
            
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300
            )
            
            sentiment_text = response.choices[0].message.content.strip()
            
            try:
                sentiment = json.loads(sentiment_text)
                sentiment["asset"] = asset
                sentiment["timestamp"] = datetime.now().isoformat()
                sentiment["source"] = "simulated"
                return sentiment
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return {"error": "Failed to generate sentiment analysis", "raw_text": sentiment_text}
                
        except Exception as e:
            logger.error(f"Error monitoring social sentiment: {str(e)}")
            return {"error": f"Failed to analyze sentiment: {str(e)}"}
    
    def generate_trading_signals(self, user_address: str) -> Dict[str, Any]:
        """
        Generate trading signals based on a user's historical performance.
        
        Args:
            user_address: User's wallet address
            
        Returns:
            Dictionary with trading signals
        """
        logger.info(f"Generating trading signals based on user {user_address}")
        
        # Get historical data
        trades = self.get_user_trades(user_address)
        trades_df = self.process_trades_to_dataframe(trades)
        
        if trades_df.empty:
            return {"error": "Insufficient trading data to generate signals"}
            
        # Get current market data
        market_data = self.get_market_data()
        
        # Generate signals using LLM
        if self.llm_enabled:
            # Prepare simplified trade data for the prompt
            recent_trades = trades_df.sort_values('timestamp', ascending=False).head(10)
            trade_data = []
            for _, row in recent_trades.iterrows():
                trade_data.append({
                    "coin": row.get('coin', 'unknown'),
                    "side": row.get('side', 'unknown'),
                    "timestamp": row.get('timestamp', 'unknown'),
                    "price": row.get('price', 0)
                })
                
            # Current market prices
            current_prices = {}
            for coin, data in market_data.items():
                if isinstance(data, dict) and 'mid' in data:
                    current_prices[coin] = data['mid']
                    
            prompt = f"""
            You are an expert cryptocurrency trading signal generator. Based on the trader's recent activity
            and current market conditions, generate potential trading signals.
            
            RECENT TRADES:
            {json.dumps(trade_data, indent=2, default=str)}
            
            CURRENT MARKET PRICES:
            {json.dumps(current_prices, indent=2)}
            
            Generate 3-5 potential trading signals in the following JSON format:
            {{
                "signals": [
                    {{
                        "asset": "[asset symbol]",
                        "direction": "[long/short]",
                        "confidence": [number between 1-10],
                        "rationale": "[brief explanation]",
                        "time_frame": "[short-term/medium-term/long-term]"
                    }}
                ]
            }}
            
            Return ONLY valid JSON, no other text.
            """
            
            try:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=800
                )
                
                signals_text = response.choices[0].message.content.strip()
                
                try:
                    signals = json.loads(signals_text)
                    signals["generated_at"] = datetime.now().isoformat()
                    signals["based_on_user"] = user_address
                    signals["disclaimer"] = "These signals are generated based on historical patterns and should not be considered financial advice."
                    return signals
                except json.JSONDecodeError:
                    logger.error("Failed to parse LLM response as JSON")
                    return {"error": "Failed to generate signals", "raw_text": signals_text}
                    
            except Exception as e:
                logger.error(f"Error generating trading signals: {str(e)}")
                return {"error": f"Failed to generate signals: {str(e)}"}
        else:
            return {"error": "LLM functionality required for signal generation"}

# Example usage
if __name__ == "__main__":
    # Example user address (replace with actual address)
    user_address = "0x000000000000000000000000000000000000000"
    
    # Initialize the agent
    agent = HyperliquidAgent()
    
    # Analyze a trader
    analysis = agent.analyze_trader(user_address)
    print(json.dumps(analysis, indent=2, default=str))
    
    # Ask a follow-up question
    answer = agent.ask_question("What is this trader's risk profile?", context=analysis)
    print("\nQuestion: What is this trader's risk profile?")
    print(f"Answer: {answer}")
    
    # Generate trading signals
    signals = agent.generate_trading_signals(user_address)
    print("\nTrading Signals:")
    print(json.dumps(signals, indent=2, default=str))