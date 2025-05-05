from agent.AnalysisAgent import AnalysisAgent
from datetime import datetime
import time
import json
import os

def run_analysis_job():
    """Run the trader analysis job in batches"""
    print(f"Starting analysis job at {datetime.now()}")
    
    # Initialize agent
    agent = AnalysisAgent()
    
    try:
        # Process traders in batches
        results = agent.process_traders_in_batches(batch_size=30)
        
        # Store final results
        os.makedirs('analysis_cache', exist_ok=True)
        with open('analysis_cache/final_analysis.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results
            }, f)
        
        print(f"Analysis job completed at {datetime.now()}")
        print(f"Processed {results['trader_count']} traders")
        print(f"Results saved to analysis_cache/final_analysis.json")
        
    except Exception as e:
        print(f"Error in analysis job: {e}")

if __name__ == "__main__":
    # Run the job
    run_analysis_job() 