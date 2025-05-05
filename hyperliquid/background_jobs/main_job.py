from llm_agent import LLMAgent
from data.HyperliquidAnalytics import HyperliquidAnalytics
from data.HyperliquidDataService import HyperliquidDataService
from db.database import TraderDatabase
from background_jobs.analysis_job import run_analysis_job
import time
from datetime import datetime, timedelta

def run_main_job():
    """Run the main trader analysis job"""
    print(f"Starting main job at {datetime.now()}")
    
    # Initialize components
    llm = LLMAgent()
    analytics = HyperliquidAnalytics()
    data_service = HyperliquidDataService()
    db = TraderDatabase()

    try:
        # Fetch and store trader data
        print(f"Fetching trader data at {datetime.now()}")
        top_traders = data_service.get_top_traders(limit=10000)
        db.store_traders(top_traders)
        print(f"Stored {len(top_traders)} traders in database")

        # Analyze each trader and store results
        print("\nAnalyzing traders...")
        for i, trader in enumerate(top_traders):
            try:
                print(f"\nAnalyzing trader {i+1}/{len(top_traders)}: {trader['address']}")
                analysis = analytics.analyze_trader(trader['address'])
                if not analysis['metrics']:
                    print(f"No metrics for {trader['address']}")
                    continue
                print(analysis['metrics'])
                db.store_trader_analysis(trader['address'], analysis)
                print(f"Stored analysis for {trader['address']}")
                
                # Run analysis job after every 1000 traders
                # if (i + 1) % 1000 == 0:
                #     print(f"\nReached {i+1} traders, running analysis job...")
                #     run_analysis_job()
                #     print("Analysis job completed, continuing with main job...")
                
            except Exception as e:
                print(f"Error analyzing trader {trader['address']}: {e}")
                continue

        print("\nAnalysis complete. Waiting 5 minutes before next update...")
        time.sleep(300)

    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    while True:
        run_main_job() 