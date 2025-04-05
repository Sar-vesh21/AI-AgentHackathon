from agent.AnalysisAgent import AnalysisAgent
from db.database import TraderDatabase
import json
from typing import Any
from datetime import datetime, timedelta

def print_section(title: str, content: Any, indent: int = 0):
    """Helper function to print formatted sections"""
    print("\n" + "=" * (80 - indent))
    print(" " * indent + title)
    print("=" * (80 - indent))
    
    if isinstance(content, dict):
        for key, value in content.items():
            if isinstance(value, (list, dict)):
                print(f"\n{key}:")
                print_section("", value, indent + 2)
            else:
                print(f"\n{key}: {value}")
    elif isinstance(content, list):
        for item in content:
            print(f"- {item}")
    else:
        print(content)

def prepare_trader_data(analyses: list) -> list:
    """Prepare trader data from database analyses for LLM processing
    
    Args:
        analyses (list): List of analysis records from the database, each containing:
            - user_address: Trader's address
            - trading_style: Analysis of trading style
            - risk_profile: Risk analysis
            - performance_metrics: Performance statistics
            - market_behavior: Market behavior analysis
            - recommendations: Trading recommendations
            - raw_analysis: Complete analysis data
    """
    trader_data = []
    
    for analysis in analyses:
        trader = {
            'address': analysis['user_address'],
            'trading_style': analysis['trading_style'],
            'risk_profile': analysis['risk_profile'],
            'performance_metrics': analysis['performance_metrics'],
            'market_behavior': analysis['market_behavior'],
            'recommendations': analysis['recommendations'],
            'raw_analysis': analysis['raw_analysis']
        }
        trader_data.append(trader)
    
    return trader_data

def main():
    # Initialize database and LLM agent
    db = TraderDatabase()
    agent = AnalysisAgent()
    
    # Get first 100 trader analyses by ID
    print("Fetching trader analyses from database...")
    analyses = db.get_all_trader_analyses(limit=45)
    print(f"Fetched {len(analyses)} trader analyses")
    
    # Prepare data for LLM analysis
    trader_data = prepare_trader_data(analyses)
    
    # Analyze with LLM
    print("Analyzing trading patterns across traders...")
    results = agent.analyze_all_traders(trader_data=trader_data)
    
    # Print results
    print(f"\nAnalyzed {len(analyses)} traders")
    
    insights = results['insights']
    print(insights)
    
    # Print each major section
    print_section("Trading Styles Analysis", insights['trading_styles'])
    print_section("Market Behavior Analysis", insights['market_behavior'])
    print_section("Risk Analysis", insights['risk_analysis'])
    print_section("Successful Strategies", insights['strategies'])
    print_section("Market Psychology", insights['psychology'])
    print_section("Recommendations", insights['recommendations'])
    print_section("Evolution Analysis", insights['evolution'])

if __name__ == "__main__":
    main() 