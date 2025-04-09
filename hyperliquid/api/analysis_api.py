from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from agent.AnalysisAgent import AnalysisAgent
from db.database import TraderDatabase
from datetime import datetime, timedelta
from data.SentimentDataService import SentimentDataService
from data.VaultDataService import VaultDataService
from data.HyperliquidDataService import HyperliquidDataService
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="Hyperliquid Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app default port
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize services
sentiment_service = SentimentDataService()
vault_service = VaultDataService()
hyperliquid_service = HyperliquidDataService()
analysis_agent = AnalysisAgent()

@app.get("/analysis/recent", response_model=Dict[str, Any])
async def get_recent_analysis():
    """Get analysis of recent traders from cached results"""
    try:
        # Check if cached results exist
        cache_file = 'analysis_cache/final_analysis.json'
        if not os.path.exists(cache_file):
            raise HTTPException(
                status_code=404,
                detail="Analysis results not available. Please try again later."
            )
        
        # Load cached results
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        return {
            "status": "success",
            "data": cache_data['results']['insights'],
            "metadata": {
                "trader_count": cache_data['results']['trader_count'],
                "timestamp": cache_data['timestamp']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/analysis/traders", response_model=Dict[str, Any])
async def get_traders(limit: int = 50):
    """Get analysis of recent traders
    
    Args:
        limit (int): Number of traders to analyze. Defaults to 50.
    """
    try:
        # Initialize components
        db = TraderDatabase()
        agent = AnalysisAgent()
        
        # Get recent analyses
        traders = db.get_all_trader_analyses(limit=limit)
        
        return {
            "status": "success",
            "data": traders,
            "metadata": {
                "trader_count": len(traders),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/analysis/traderSummary", response_model=Dict[str, Any])
async def get_trader_summarys(page: int = 1, page_size: int = 50):
    """Get paginated trader summaries with analysis
    
    Args:
        page (int): Page number (1-based). Defaults to 1.
        page_size (int): Number of items per page. Defaults to 50.
    """
    try:
        # Initialize components
        db = TraderDatabase()
        
        # Get paginated data
        result = db.get_traders_with_analysis(page=page, page_size=page_size)
        
        return {
            "status": "success",
            "data": result['data'],
            "pagination": result['pagination'],
            "metadata": {
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
    
    
@app.get("/analysis/sentiment/{symbol}", response_model=Dict[str, Any])
async def get_sentiment(symbol: str):
    """Get sentiment analysis for a specific symbol
    
    Args:
        symbol (str): Symbol to analyze.
        
    Returns:
        Dict[str, Any]: Sentiment data for the symbol
    """
    try:
        # First get the coin name from coin_metrics.json
        with open('coin_metrics.json', 'r') as f:
            coin_metrics = json.load(f)
        
        # Find the symbol (case-insensitive)
        symbol_data = next(
            (coin for coin in coin_metrics if coin['symbol'].upper() == symbol.upper()),
            None
        )
        
        if not symbol_data:
            raise HTTPException(
                status_code=404,
                detail=f"Symbol {symbol} not found in metrics data"
            )
        
        # Get topic sentiment data
        topic_data = sentiment_service.get_topic_sentiment(symbol_data['name'].lower())
        sentiment_percentages = sentiment_service.calculate_sentiment_percentages(topic_data)
        
        return {
            "status": "success",
            "data": {
                "symbol": symbol_data['symbol'],
                "name": symbol_data['name'],
                "sentiment": symbol_data['sentiment'],
                "sentiment_score": symbol_data['galaxy_score'],
                "topic_sentiment": sentiment_percentages,
                "total_interactions": topic_data['data']['interactions_24h'],
                "num_contributors": topic_data['data']['num_contributors'],
                "trend": topic_data['data']['trend']
            },
            "metadata": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Coin metrics data not available"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/vaults", response_model=Dict[str, Any])
async def get_vaults(min_tvl: float = 0, min_apr: float = None, active_only: bool = True):
    """Get all vaults with optional filtering and cached analysis
    
    Args:
        min_tvl (float): Minimum TVL filter. Defaults to 0.
        min_apr (float): Minimum APR filter. Optional.
        active_only (bool): Only show active (non-closed) vaults. Defaults to True.
    """
    try:
        # Read cached analysis data
        cache_file = 'analysis_cache/vault_analysis.json'
        if not os.path.exists(cache_file):
            raise HTTPException(
                status_code=404,
                detail="Vault analysis data not available. Please try again later."
            )
            
        with open(cache_file, 'r') as f:
            cached_data = json.load(f)
            
        # Get vault data from cache
        processed_vaults = cached_data['vault_data']
        
        # Apply filters
        filtered_vaults = [
            vault for vault in processed_vaults
            if vault['tvl'] >= min_tvl and
            (not active_only or not vault['is_closed']) and
            (min_apr is None or vault['apr'] >= min_apr)
        ]
        
        # Sort by TVL descending
        filtered_vaults.sort(key=lambda x: x['tvl'], reverse=True)
        
        
        return {
            "status": "success",
            "data": {
                "analysis": cached_data['analysis'],
                "total_vaults": len(filtered_vaults),
            },
            "metadata": {
                "timestamp": cached_data['timestamp'],
                "filters_applied": {
                    "min_tvl": min_tvl,
                    "min_apr": min_apr,
                    "active_only": active_only
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/vaults/{address}", response_model=Dict[str, Any])
async def get_vault_details(address: str, include_positions: bool = True):
    """Get detailed information for a specific vault
    
    Args:
        address (str): Vault address
        include_positions (bool): Whether to include detailed position information. Defaults to True.
    """
    try:
        # Get vault data
        vaults_data = vault_service.get_vaults()
        processed_vaults = vault_service.process_vault_metrics(vaults_data)
        
        # Find specific vault
        vault = next((v for v in processed_vaults if v['address'].lower() == address.lower()), None)
        if not vault:
            raise HTTPException(status_code=404, detail="Vault not found")
        
        # Get additional details directly if not included in processed data
        if include_positions and (not vault.get('details')):
            try:
                vault['details'] = vault_service.get_vault_details(address)
            except Exception as e:
                vault['details'] = {"error": str(e)}
        
        return {
            "status": "success",
            "data": {
                "summary": {
                    "name": vault['name'],
                    "address": vault['address'],
                    "leader": vault['leader'],
                    "tvl": vault['tvl'],
                    "apr": vault['apr'],
                    "is_closed": vault['is_closed'],
                    "created_at": vault['created_at']
                },
                "performance": vault['performance'],
                "details": vault.get('details') if include_positions else None
            },
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "include_positions": include_positions
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/analysis/positions/{address}", response_model=Dict[str, Any])
async def get_user_positions(address: str):
    """Get current positions and analysis for a specific user
    
    Args:
        address (str): User's wallet address
        
    Returns:
        Dict[str, Any]: User's current positions and analysis
    """
    try:
        # Get user positions
        positions = hyperliquid_service.get_user_positions(address)
        
        # Analyze positions against market data
        analysis = analysis_agent.analyze_user_positions(positions)
        
        return {
            "status": "success",
            "data": {
                "positions": positions,
                "analysis": analysis
            },
            "metadata": {
                "address": address,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 