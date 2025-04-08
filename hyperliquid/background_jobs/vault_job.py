from agent.AnalysisAgent import AnalysisAgent
from data.VaultDataService import VaultDataService
from datetime import datetime
import time
import json
import os

def run_vault_analysis_job():
    """Run the vault analysis job"""
    print(f"Starting vault analysis job at {datetime.now()}")
    
    # Initialize services
    data_service = VaultDataService()
    agent = AnalysisAgent()
    
    try:
        # Fetch and process vault data
        print("Fetching vault data...")
        vaults = data_service.get_vaults()
        processed_vaults = data_service.process_vault_metrics(vaults)
        
        print("Analyzing vault data...")
        results = agent.analyze_vault_performance(processed_vaults)
        
        # Store results
        os.makedirs('analysis_cache', exist_ok=True)
        with open('analysis_cache/vault_analysis.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'vault_data': processed_vaults,
                'analysis': results
            }, f)
        
        print(f"Vault analysis job completed at {datetime.now()}")
        print(f"Results saved to analysis_cache/vault_analysis.json")
        
    except Exception as e:
        print(f"Error in vault analysis job: {e}")

if __name__ == "__main__":
    # Run the job
    run_vault_analysis_job()
