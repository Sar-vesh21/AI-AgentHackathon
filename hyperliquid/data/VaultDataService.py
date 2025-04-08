from typing import List, Dict, Any
import requests
from datetime import datetime

class VaultDataService:
    def __init__(self):
        self.base_url = "https://stats-data.hyperliquid.xyz/Mainnet"
        self.api_url = "https://api-ui.hyperliquid.xyz/info"
        self.headers = {"Content-Type": "application/json"}
        
    def get_vaults(self) -> List[Dict[str, Any]]:
        """
        Fetch all vaults data from Hyperliquid and return top 10 by TVL
        
        Returns:
            List[Dict]: List of top 10 vault data including APR, PnLs and summary, sorted by TVL
        """
        try:
            response = requests.get(f"{self.base_url}/vaults")
            response.raise_for_status()
            vaults = response.json()
            
            # Sort by TVL (highest first) and limit to 10 vaults
            return sorted(vaults, key=lambda x: float(x['summary']['tvl']), reverse=True)[:6]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch vault data: {str(e)}")

    def get_vault_details(self, vault_address: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific vault from Hyperliquid API
        
        Args:
            vault_address (str): The vault address to fetch details for
            
        Returns:
            Dict: Detailed vault information including positions, performance, etc.
        """
        try:
            payload = {
                "type": "vaultDetails",
                "vaultAddress": vault_address
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch vault details: {str(e)}")
    
    def process_vault_metrics(self, vaults: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process vault data to extract key metrics
        
        Args:
            vaults (List[Dict]): Raw vault data from API
            
        Returns:
            List[Dict]: Processed vault metrics
        """
        processed_vaults = []
        
        for vault in vaults:
            # Convert PnLs to dict for easier access
            pnls = {period: values for period, values in vault['pnls']}
            
            processed_vault = {
                'name': vault['summary']['name'],
                'address': vault['summary']['vaultAddress'],
                'leader': vault['summary']['leader'],
                'tvl': float(vault['summary']['tvl']),
                'apr': float(vault['apr']),
                'is_closed': vault['summary']['isClosed'],
                'created_at': datetime.fromtimestamp(vault['summary']['createTimeMillis'] / 1000).isoformat(),
                'performance': {
                    'daily': {
                        'values': pnls.get('day', []),
                        'latest': float(pnls.get('day', [0])[-1]) if pnls.get('day') else 0
                    },
                    'weekly': {
                        'values': pnls.get('week', []),
                        'latest': float(pnls.get('week', [0])[-1]) if pnls.get('week') else 0
                    },
                    'monthly': {
                        'values': pnls.get('month', []),
                        'latest': float(pnls.get('month', [0])[-1]) if pnls.get('month') else 0
                    },
                    'all_time': {
                        'values': pnls.get('allTime', []),
                        'latest': float(pnls.get('allTime', [0])[-1]) if pnls.get('allTime') else 0
                    }
                }
            }
            
            # Try to fetch additional details
            try:
                details = self.get_vault_details(vault['summary']['vaultAddress'])
                processed_vault['details'] = details
            except Exception as e:
                processed_vault['details'] = None
                
            processed_vaults.append(processed_vault)
            
        return processed_vaults 
    
