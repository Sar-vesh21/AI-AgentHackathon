# Hyperliquid Analytics Plugin

## Overview

The Hyperliquid Analytics plugin provides comprehensive analytics and trading functionality for the Hyperliquid protocol within Eliza OS. It enables users to analyze traders, market sentiment, and vault performance through a set of specialized actions.

## How It Works

The Hyperliquid Analytics plugin works by providing a set of specialized actions that users can interact with through natural language. Each action follows a specific pattern:

1. User asks a question or makes a request
2. The plugin identifies the relevant action
3. The action uses a prompt template to extract necessary information
4. The extracted information is used to fetch data from the backend
5. The response is formatted and presented back to the user

## Features

### Trader Analysis
- Individual trader performance analysis
- Trading pattern and strategy insights
- Position and performance metrics tracking

### Market Analysis
- Real-time token price checking
- Market sentiment analysis
- Comprehensive market insights

### Vault Analytics
- Vault performance analysis
- Strategy and return insights
- Performance metrics comparison

## Actions

### `analyseTraders`
Analyzes trader data from the Hyperliquid database.

**User Interaction:**
- "Show me the top traders"
- "Analyze recent trading activity"
- "What are the best performing traders?"

**Prompt Template:**
The template helps extract the specific type of analysis the user wants, focusing on:
- Time period
- Performance metrics
- Specific trading patterns

### `priceCheck`
Checks the current price of specified tokens.

**User Interaction:**
- "What's the price of ETH?"
- "Check HYPE price"
- "Get current BTC price"

**Prompt Template:**
The template extracts:
- Token symbol
- Time period (if specified)
- Additional metrics (if requested)

### `analyseSentiment`
Analyzes market sentiment for specific tokens.

**User Interaction:**
- "What's the sentiment for ETH?"
- "How is the market feeling about BTC?"
- "Show me sentiment analysis for HYPE"

**Prompt Template:**
The template focuses on:
- Token identification
- Time period
- Sentiment aspects (price, volume, social)

### `analyseVaults`
Analyzes vault data from top Hyperliquid vaults.

**User Interaction:**
- "Show me the best vaults"
- "Analyze vault performance"
- "What are the top performing vaults?"

**Prompt Template:**
The template helps identify:
- Performance metrics of interest
- Time period
- Specific vault characteristics

### `analyseTrader`
Analyzes a specific trader's performance and positions.

**User Interaction:**
- "Analyze trader 0x123..."
- "Show me positions for 0x123..."
- "What's this trader's performance?"

**Prompt Template:**
The template extracts:
- Trader address
- Specific metrics of interest
- Time period for analysis

## Prompt-Based Information Extraction

Each action uses specialized prompt templates to:
1. Understand the user's intent
2. Extract relevant parameters
3. Structure the request to the backend
4. Format the response in a user-friendly way

The prompts are designed to:
- Handle natural language variations
- Extract specific data points
- Maintain conversation context
- Provide structured output

## Example Conversations

### Price Check
```
User: "What's the current price of ETH?"
Plugin: "I'll check the current ETH price for you"
[Fetches price data]
Plugin: "ETH is currently trading at $3,200 with a 24h change of +2.5%"
```

### Trader Analysis
```
User: "Show me the positions for trader 0x123..."
Plugin: "I'll analyze the positions for trader 0x123..."
[Fetches trader data]
Plugin: "This trader currently holds: 1.5 ETH, 5000 HYPE, with a total portfolio value of $15,000"
```

### Vault Analysis
```
User: "What are the best performing vaults?"
Plugin: "I'll analyze the vault performance metrics..."
[Fetches vault data]
Plugin: "The top 3 performing vaults are: Vault A (APY: 25%), Vault B (APY: 22%), Vault C (APY: 20%)"
```

## Natural Language Understanding

The plugin is designed to understand various ways users might phrase their requests:
- Direct questions ("What's the price of ETH?")
- Commands ("Show me the best vaults")
- Contextual requests ("How is this trader performing?")
- Comparative analysis ("Compare these vaults")

Each action's prompt template is optimized to handle these variations while maintaining accuracy in data extraction.

## Configuration

### Required Configuration
```typescript
interface HyperliquidConfig {
    privateKey: string;      // Private key for authentication
    testnet?: boolean;       // Whether to use testnet (default: false)
    walletAddress?: string;  // Optional wallet address
}
```

### Environment Variables
```env
HYPERLIQUID_PRIVATE_KEY=your_private_key
HYPERLIQUID_TESTNET=true_or_false
```

## Data Types

### Spot Order
```typescript
interface SpotOrder {
    coin: string;
    is_buy: boolean;
    sz: number;
    limit_px: number | null;
    reduce_only?: boolean;
    order_type?: {
        limit: {
            tif: "Ioc" | "Gtc";
        };
    };
}
```

### Response Types
```typescript
interface OrderResponse {
    coin: string;
    orderId: string;
    status: "open" | "filled" | "cancelled" | "rejected";
    size: number;
    price: number;
    is_buy: boolean;
}

interface BalanceResponse {
    coin: string;
    free: number;
    locked: number;
}
```

## Error Handling

The plugin uses a custom error class for handling Hyperliquid-specific errors:

```typescript
class HyperliquidError extends Error {
    constructor(
        message: string,
        public code?: number,
        public details?: unknown
    );
}
```

## Constants

### Order Status
```typescript
const ORDER_STATUS = {
    OPEN: "open",
    FILLED: "filled",
    CANCELLED: "cancelled",
    REJECTED: "rejected",
};
```

### Price Validation
```typescript
const PRICE_VALIDATION = {
    MARKET_ORDER: {
        MIN_RATIO: 0.5,  // -50% from mid price
        MAX_RATIO: 1.5,  // +50% from mid price
    },
    LIMIT_ORDER: {
        WARNING_MIN_RATIO: 0.2,  // -80% from mid price
        WARNING_MAX_RATIO: 5,    // +500% from mid price
    },
    SLIPPAGE: 0.01,  // 1% slippage for market orders
};
```

## Implementation Notes

- Uses Zod for schema validation
- Price validations are relative to the mid price
- Market orders have tighter price validation than limit orders
- Includes built-in slippage protection for market orders
- Supports both mainnet and testnet environments

## Security Considerations

- Private keys should be stored securely using environment variables
- Test with small amounts first
- Use testnet for initial testing
- Monitor orders regularly
- Double-check prices before confirming trades

## License

MIT
