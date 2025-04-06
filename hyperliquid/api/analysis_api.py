from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from agent.AnalysisAgent import AnalysisAgent
from db.database import TraderDatabase
from datetime import datetime, timedelta
from data.SentimentDataService import SentimentDataService
import json
import os

app = FastAPI(title="Hyperliquid Analysis API")

# Initialize sentiment service
sentiment_service = SentimentDataService()

@app.get("/analysis/recent", response_model=Dict[str, Any])
async def get_recent_analysis(limit: int = 50):
    """Get analysis of recent traders
    
    Args:
        limit (int): Number of traders to analyze. Defaults to 50.
    """
    try:
        # Initialize components
        db = TraderDatabase()
        agent = AnalysisAgent()
        
        # Get recent analyses
        analyses = db.get_all_trader_analyses(limit=limit)
        
        # Analyze with LLM
        results = agent.analyze_all_traders(trader_data=analyses)
        
        return {
            "status": "success",
            "data": results['insights'],
            "metadata": {
                "trader_count": results['trader_count'],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


## TODO: Review this endpoint
@app.get("/analysis/sentiment/{topic}", response_model=Dict[str, Any])
async def get_topic_sentiment(topic: str = "bitcoin"):
    """Get sentiment analysis for a specific topic
    
    Args:
        topic (str): Topic to analyze. Defaults to "bitcoin"
    """
    try:
        # Get fresh sentiment data
        topic_data = sentiment_service.get_topic_sentiment(topic)
        sentiment_percentages = sentiment_service.calculate_sentiment_percentages(topic_data)
        
        return {
            "status": "success",
            "data": {
                "sentiment_percentages": sentiment_percentages,
                "topic": topic,
                "total_interactions": topic_data['data']['interactions_24h'],
                "num_contributors": topic_data['data']['num_contributors'],
                "trend": topic_data['data']['trend']
            },
            "metadata": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


## TODO: Review this endpoint
@app.get("/analysis/coins", response_model=Dict[str, Any])
async def get_coin_metrics(limit: int = 50, min_galaxy_score: float = None):
    """Get metrics for all coins with optional filtering
    
    Args:
        limit (int): Number of coins to return. Defaults to 50.
        min_galaxy_score (float): Minimum galaxy score filter. Optional.
    """
    try:
        # Read from stored JSON
        try:
            with open('coin_metrics.json', 'r') as f:
                coin_metrics = json.load(f)
        except FileNotFoundError:
            # If file doesn't exist, fetch fresh data
            coins_data = sentiment_service.get_coins_list()
            coin_metrics = sentiment_service.extract_coin_metrics(coins_data)
        
        # Apply filters
        if min_galaxy_score is not None:
            coin_metrics = [
                coin for coin in coin_metrics 
                if coin.get('galaxy_score', 0) >= min_galaxy_score
            ]
        
        return {
            "status": "success",
            "data": {
                "coins": coin_metrics[:limit],
                "total_coins": len(coin_metrics)
            },
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "filters_applied": {
                    "limit": limit,
                    "min_galaxy_score": min_galaxy_score
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/trader/{address}", response_model=Dict[str, Any])
async def get_trader_analysis(address: str):
    """Get analysis for a specific trader
    
    Args:
        address (str): Trader's address
    """
    try:
        # Initialize components
        db = TraderDatabase()
        agent = AnalysisAgent()
        
        # Get trader's analysis
        analysis = db.get_trader_analysis(address)
        if not analysis:
            raise HTTPException(status_code=404, detail="Trader analysis not found")
        
        # Analyze with LLM
        results = agent.analyze_all_traders(trader_data=[analysis[0]])
        
        return {
            "status": "success",
            "data": results['insights'],
            "metadata": {
                "address": address,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/styles", response_model=Dict[str, Any])
async def get_trading_styles(limit: int = 50):
    """Get analysis of different trading styles
    
    Args:
        limit (int): Number of traders to analyze. Defaults to 50.
    """
    try:
        # Initialize components
        db = TraderDatabase()
        agent = AnalysisAgent()
        
        # Get analyses
        analyses = db.get_all_trader_analyses(limit=limit)
        
        # Analyze with LLM
        results = agent.analyze_all_traders(trader_data=analyses)
        
        return {
            "status": "success",
            "data": {
                "trading_styles": results['insights']['trading_styles'],
                "style_distribution": results['insights'].get('style_distribution', {})
            },
            "metadata": {
                "trader_count": results['trader_count'],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 