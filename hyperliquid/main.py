from llm_agent import LLMAgent
from hyperliquid_data_service import HyperliquidDataService
from hyperliquid_analytics import HyperliquidAnalytics

# Initialize components
llm = LLMAgent()

## Lets test the LLM agent with a simple prompt
# prompt = "What is the capital of the moon?"
# response = llm.generate_response(prompt)
# print(response)

## Lets test the HyperliquidAnalytics class
analytics = HyperliquidAnalytics(llm)

dataService = HyperliquidDataService()

## Lets test the HyperliquidDataService class
# trades = dataService.get_user_trades("0x7fdafde5cfb5465924316eced2d3715494c517d1")

## Lets test the HyperliquidAnalytics class
analysis = analytics.analyze_trader("0x8cc94dc843e1ea7a19805e0cca43001123512b6a")


print(trades)


