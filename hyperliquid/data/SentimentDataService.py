import requests
import json
from typing import List, Dict
import os

class SentimentDataService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("SENTIMENT_API_KEY")
        if not self.api_key:
            raise ValueError("No Sentiment API key provided in environment or constructor")
        self.base_url = "https://lunarcrush.com/api4/public"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

    def get_coins_list(self) -> Dict:
        """
        Fetch list of available coins from LunarCrush
        
        Returns:
            dict: Response containing list of coins and their details
        """
        url = f"{self.base_url}/coins/list/v1"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch coins data: {str(e)}")
    
    def extract_coin_metrics(self, coins_data: Dict) -> List[Dict]:
        """
        Extract relevant metrics from coins data
        """
        metrics = []
        for coin in coins_data.get('data', []):
            metrics.append({
                'name': coin.get('name'),
                'symbol': coin.get('symbol'),
                'sentiment': coin.get('sentiment'),
                'galaxy_score': coin.get('galaxy_score'),
                'price': coin.get('price'),
                'market_cap': coin.get('market_cap'),
                'volume_24h': coin.get('volume_24h')
            })
        return metrics

    def get_topic_sentiment(self, topic: str = "bitcoin") -> Dict:
        """
        Fetch sentiment data for a specific topic
        
        Args:
            topic (str): Topic to analyze (default: "bitcoin")
            
        Returns:
            dict: Sentiment data for the topic
        """
        url = f"{self.base_url}/topic/{topic}/v1"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch topic data: {str(e)}")

    def calculate_sentiment_percentages(self, sentiment_data: Dict) -> Dict:
        """
        Calculate percentages for positive, neutral, and negative sentiment
        """
        results = {}
        
        types_detail = sentiment_data['data']['types_sentiment_detail']
        
        for content_type, counts in types_detail.items():
            total = sum(counts.values())
            if total == 0:
                continue
                
            percentages = {
                'positive': round(counts['positive'] / total * 100, 2),
                'neutral': round(counts['neutral'] / total * 100, 2),
                'negative': round(counts['negative'] / total * 100, 2),
                'total_interactions': total,
                'raw_counts': counts
            }
            results[content_type] = percentages
            
        return results


if __name__ == "__main__":
    sentiment_data_service = SentimentDataService()
    
    # Get list of available coins and their metrics
    print("Fetching coin metrics...")
    coins_data = sentiment_data_service.get_coins_list()
    coin_metrics = sentiment_data_service.extract_coin_metrics(coins_data)
    
    # Save coin data to JSON files
    with open('coin_data_full.json', 'w') as f:
        json.dump(coins_data, f, indent=2)
    with open('coin_metrics.json', 'w') as f:
        json.dump(coin_metrics, f, indent=2)
    
    print(f"Saved coin data to coin_data_full.json and coin_metrics.json")
    
    # Print sample coin metrics
    print("\nSample metrics for first 5 coins:")
    for coin in coin_metrics[:5]:
        print(f"{coin['name']} ({coin['symbol']}):")
        print(f"  Sentiment: {coin['sentiment']}")
        print(f"  Galaxy Score: {coin['galaxy_score']}")
        print(f"  Price: ${coin['price']:.6f}")
        print("---")

    # Get and analyze topic sentiment
    print("\nFetching Bitcoin topic sentiment...")
    topic_data = sentiment_data_service.get_topic_sentiment("bitcoin")
    sentiment_percentages = sentiment_data_service.calculate_sentiment_percentages(topic_data)
    
    # Save topic sentiment data to JSON files
    with open('topic_sentiment_full.json', 'w') as f:
        json.dump(topic_data, f, indent=2)
    with open('sentiment_percentages.json', 'w') as f:
        json.dump(sentiment_percentages, f, indent=2)
    
    print("Saved topic sentiment data to topic_sentiment_full.json and sentiment_percentages.json")
    
    # Print sentiment analysis
    print("\nSentiment Analysis by Platform:")
    print("==============================")
    
    for platform, data in sentiment_percentages.items():
        print(f"\n{platform.upper()}:")
        print(f"Positive: {data['positive']}%")
        print(f"Neutral: {data['neutral']}%")
        print(f"Negative: {data['negative']}%")
        print(f"Total Interactions: {data['total_interactions']:,}")
        print("-" * 30)

    
