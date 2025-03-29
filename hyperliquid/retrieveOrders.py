import requests
import json

def get_historical_orders(user_address):
    """
    Retrieve historical orders for a specific user from Hyperliquid API
    
    Args:
        user_address (str): User's wallet address in 42-character hexadecimal format
                           (e.g., 0x000000000000000000000000000000000000000)
    
    Returns:
        dict: JSON response containing the user's historical orders
    """
    # API endpoint
    url = "https://api.hyperliquid.xyz/info"
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "type": "historicalOrders",
        "user": user_address
    }
    
    # Make the API request
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    # Replace with the actual user address you want to query
    user_address = "0xfbdd44e73e24dc3ac26c2747d92b35363f155680"
    
    orders = get_historical_orders(user_address)
    
    if orders:
        # Pretty print the results
        print(json.dumps(orders, indent=2))
        
        # Print the number of orders retrieved
        if isinstance(orders, list):
            print(f"Retrieved {len(orders)} historical orders")