from typing import Dict, Any, List
import pandas as pd
import numpy as np
from data.HyperliquidAnalytics import HyperliquidAnalytics
from data.HyperliquidDataService import HyperliquidDataService
from llm_agent import LLMAgent, LLMProvider
import json
from time import sleep
class AnalysisAgent:
    """AI agent for analyzing trading styles across all traders"""
    
    def __init__(self, 
                 analytics: HyperliquidAnalytics = None,
                 data_service: HyperliquidDataService = None,
                 llm_agent: LLMAgent = None):
        self.analytics = analytics or HyperliquidAnalytics()
        self.data_service = data_service or HyperliquidDataService()
        self.llm = llm_agent or LLMAgent(provider=LLMProvider.ANTHROPIC)
        
    def analyze_all_traders(self, trader_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trading patterns across traders
        
        Args:
            trader_data (List[Dict[str, Any]], optional): Pre-prepared trader data from database.
                If None, will fetch top N traders from data service.
            top_n (int, optional): Number of top traders to analyze if trader_data is None.
                Defaults to 100.
        """
        all_trader_data = trader_data
            
        # Generate insights using LLM
        insights = self._generate_insights(all_trader_data)
        
        return {
            'insights': insights,
            'trader_count': len(all_trader_data)
        }
    
    def _summarize_trader_data(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Summarize trader's order data to reduce context size"""
        if orders_df.empty:
            return {}
            
        # Basic statistics
        summary = {
            'total_orders': len(orders_df),
            'unique_coins': orders_df['coin'].nunique(),
            'order_types': orders_df['orderType'].value_counts().to_dict(),
            'side_distribution': orders_df['side'].value_counts().to_dict(),
            'time_distribution': {
                'hourly': orders_df.groupby(orders_df['timestamp'].dt.hour).size().to_dict(),
                'daily': orders_df.groupby(orders_df['timestamp'].dt.day_name()).size().to_dict()
            }
        }
        
        # Position analysis
        positions = {}
        for coin in orders_df['coin'].unique():
            coin_orders = orders_df[orders_df['coin'] == coin]
            positions[coin] = {
                'total_orders': len(coin_orders),
                'avg_size': coin_orders['sz'].mean(),
                'max_size': coin_orders['sz'].max(),
                'side_distribution': coin_orders['side'].value_counts().to_dict()
            }
        summary['positions'] = positions
        
        # Time-based patterns
        summary['trading_hours'] = {
            'most_active_hour': orders_df.groupby(orders_df['timestamp'].dt.hour).size().idxmax(),
            'most_active_day': orders_df.groupby(orders_df['timestamp'].dt.day_name()).size().idxmax()
        }
        
        return summary
    
    def _generate_insights(self, all_trader_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights using LLM by analyzing summarized trading data"""
        # First, analyze current market activity
        current_prompt = f"""
        You are an expert cryptocurrency trading analyst. Analyze the following trading data 
        and focus specifically on current market activity and trader behavior.

        TRADER DATA:
        {json.dumps(all_trader_data, indent=2)}

        Analyze this data and provide insights about current market activity in the following JSON format:
        {{
            "market_activity": {{
                "active_traders": "Number of active traders in the last 24 hours",
                "most_bought_assets": ["List of assets with highest buy volume in last 24h"],
                "most_sold_assets": ["List of assets with highest sell volume in last 24h"],
                "buying_pressure": {{
                    "assets": ["List of assets showing strong buying pressure"],
                    "evidence": ["Evidence supporting buying pressure for each asset"]
                }},
                "selling_pressure": {{
                    "assets": ["List of assets showing strong selling pressure"],
                    "evidence": ["Evidence supporting selling pressure for each asset"]
                }},
                "position_changes": {{
                    "increasing_positions": ["Assets where traders are increasing positions"],
                    "decreasing_positions": ["Assets where traders are decreasing positions"]
                }},
                "market_sentiment": "Overall market sentiment based on trader behavior",
                "notable_patterns": ["List of notable patterns in current trading activity"]
            }}
        }}

        Focus on identifying current market trends and trader behavior.
        Consider order sizes, frequency, and timing.
        Return ONLY valid JSON, no other text.
        """
        
        current_response = self.llm.generate_response(current_prompt)
        current_insights = self.llm.parse_json_response(current_response)
        
        print(current_insights)
        
        sleep(10)
        
        # Then analyze trading styles
        style_prompt = f"""
        You are an expert cryptocurrency trading analyst. Analyze the following summarized trading data 
        and focus specifically on trading styles and patterns.

        TRADER DATA:
        {json.dumps(all_trader_data, indent=2)}

        Analyze this data and provide insights about trading styles in the following JSON format:
        {{
            "trading_styles": {{
                "style_distribution": {{
                    "description": "Detailed breakdown of trading styles observed",
                    "styles": ["List of identified trading styles with descriptions"]
                }},
                "style_characteristics": {{
                    "description": "Key characteristics of each trading style",
                    "characteristics": ["List of characteristics for each style"]
                }},
                "style_performance": {{
                    "description": "Performance analysis of different trading styles",
                    "analysis": ["Performance metrics for each style"]
                }}
            }}
        }}

        Focus on identifying distinct trading styles and their characteristics.
        Return ONLY valid JSON, no other text.
        """
        
        style_response = self.llm.generate_response(style_prompt)
        style_insights = self.llm.parse_json_response(style_response)
        
        print(style_insights)
        
        sleep(10)
        
        # Then, analyze market behavior and risk
        market_prompt = f"""
        You are an expert cryptocurrency trading analyst. Analyze the following summarized trading data 
        and focus specifically on market behavior and risk patterns.

        TRADER DATA:
        {json.dumps(all_trader_data, indent=2)}

        Analyze this data and provide insights about market behavior and risk in the following JSON format:
        {{
            "market_behavior": {{
                "patterns": ["List of observed market behavior patterns"],
                "trends": ["List of identified market trends"],
                "volatility": "Analysis of market volatility patterns"
            }},
            "risk_analysis": {{
                "risk_patterns": ["List of observed risk patterns"],
                "risk_management": ["List of risk management strategies observed"],
                "risk_recommendations": ["List of risk management recommendations"]
            }}
        }}

        Focus on market behavior patterns and risk management strategies.
        Return ONLY valid JSON, no other text.
        """
        
        market_response = self.llm.generate_response(market_prompt)
        market_insights = self.llm.parse_json_response(market_response)
        
        print(market_insights)
        
        sleep(10)
        
        # Finally, analyze strategies and psychology
        strategy_prompt = f"""
        You are an expert cryptocurrency trading analyst. Analyze the following summarized trading data 
        and focus specifically on successful strategies and market psychology.

        TRADER DATA:
        {json.dumps(all_trader_data, indent=2)}

        Analyze this data and provide insights about strategies and psychology in the following JSON format:
        {{
            "strategies": {{
                "successful_strategies": ["List of successful trading strategies identified"],
                "strategy_characteristics": ["Key characteristics of successful strategies"],
                "strategy_implementation": ["Implementation details for each strategy"]
            }},
            "psychology": {{
                "behavioral_patterns": ["List of observed behavioral patterns"],
                "emotional_factors": ["List of emotional factors affecting trading"],
                "psychological_recommendations": ["Recommendations for psychological aspects"]
            }},
            "recommendations": {{
                "style_based": ["Recommendations based on trading style"],
                "risk_based": ["Risk-based recommendations"],
                "market_based": ["Market-based recommendations"],
                "psychological": ["Psychological recommendations"]
            }},
            "evolution": {{
                "style_evolution": "How trading styles have evolved",
                "market_evolution": "How market behavior has evolved",
                "future_trends": ["Predicted future trends"]
            }}
        }}

        Focus on successful strategies and psychological aspects of trading.
        Return ONLY valid JSON, no other text.
        """
        
        strategy_response = self.llm.generate_response(strategy_prompt)
        strategy_insights = self.llm.parse_json_response(strategy_response)
        
        print(strategy_insights)
        
        sleep(10)
        
        # Combine all insights into a structured format
        return {
            "market_activity": current_insights.get("data", {}).get("market_activity", {}),
            "trading_styles": style_insights.get("data", {}).get("trading_styles", {}),
            "market_behavior": market_insights.get("data", {}).get("market_behavior", {}),
            "risk_analysis": market_insights.get("data", {}).get("risk_analysis", {}),
            "strategies": strategy_insights.get("data", {}).get("strategies", {}),
            "psychology": strategy_insights.get("data", {}).get("psychology", {}),
            "recommendations": strategy_insights.get("data", {}).get("recommendations", {}),
            "evolution": strategy_insights.get("data", {}).get("evolution", {})
        } 