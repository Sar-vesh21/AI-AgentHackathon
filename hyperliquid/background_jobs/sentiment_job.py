from data.SentimentDataService import SentimentDataService
import json
import time
from datetime import datetime

def run_sentiment_job():
    """Run the sentiment analysis job"""
    print(f"Starting sentiment analysis job at {datetime.now()}")
    
    sentiment_data_service = SentimentDataService()
    
    try:
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

        print("\nSentiment analysis complete. Waiting 1 hour before next update...")
        time.sleep(3600)  # Wait 1 hour before next update

    except Exception as e:
        print(f"Error in sentiment analysis job: {e}")
        time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    while True:
        run_sentiment_job() 