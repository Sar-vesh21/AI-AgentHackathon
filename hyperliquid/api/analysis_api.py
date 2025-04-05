from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from agent.AnalysisAgent import AnalysisAgent
from db.database import TraderDatabase
from datetime import datetime, timedelta

app = FastAPI(title="Hyperliquid Analysis API")

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
        # results = {
        #     "insights": "This is dummy data to test the API",
        #     "trader_count": 100
        # }
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