export const spotTradeTemplate = `Look at your LAST RESPONSE in the conversation where you confirmed a trade request.
Based on ONLY that last message, extract the trading details:

For Hyperliquid spot trading:
- Market orders (executes immediately at best available price):
  "buy 1 HYPE" -> { "coin": "HYPE", "is_buy": true, "sz": 1 }
  "sell 2 HYPE" -> { "coin": "HYPE", "is_buy": false, "sz": 2 }
  "market buy 1 HYPE" -> { "coin": "HYPE", "is_buy": true, "sz": 1 }
  "market sell 2 HYPE" -> { "coin": "HYPE", "is_buy": false, "sz": 2 }

- Limit orders (waits for specified price):
  "buy 1 HYPE at 20 USDC" -> { "coin": "HYPE", "is_buy": true, "sz": 1, "limit_px": 20 }
  "sell 0.5 HYPE at 21 USDC" -> { "coin": "HYPE", "is_buy": false, "sz": 0.5, "limit_px": 21 }
  "limit buy 1 HYPE at 20 USDC" -> { "coin": "HYPE", "is_buy": true, "sz": 1, "limit_px": 20 }
  "limit sell 0.5 HYPE at 21 USDC" -> { "coin": "HYPE", "is_buy": false, "sz": 0.5, "limit_px": 21 }

\`\`\`json
{
    "coin": "<coin symbol>",
    "is_buy": "<true for buy, false for sell>",
    "sz": "<quantity to trade>",
    "limit_px": "<price in USDC if limit order, null if market order>"
}
\`\`\`

Note:
- Just use the coin symbol (HYPE, ETH, etc.)
- sz is the size/quantity to trade (exactly as specified in the message)
- limit_px is optional:
  - If specified (with "at X USDC"), order will be placed at that exact price
  - If not specified, order will be placed at current market price
- Words like "market" or "limit" at the start are optional but help clarify intent

Recent conversation:
{{recentMessages}}`;

export const priceCheckTemplate = `Look at your LAST RESPONSE in the conversation where you confirmed which token price to check.
Based on ONLY that last message, extract the token symbol.

For example:
- "I'll check PIP price for you" -> { "symbol": "PIP" }
- "Let me check the price of HYPE" -> { "symbol": "HYPE" }
- "I'll get the current ETH price" -> { "symbol": "ETH" }

\`\`\`json
{
    "symbol": "<token symbol from your last message>"
}
\`\`\`

Note:
- Just return the token symbol (PIP, HYPE, ETH, etc.)
- Remove any suffixes like "-SPOT" or "USDC"
- If multiple tokens are mentioned, use the last one

Recent conversation:
{{recentMessages}}`;

export const analyseTradersTemplate = `You will request another agent to give you some analysis on some trader data. These are trader data from the Hyperliquid database, that has been analyse and summerised in a JSON format.

Analyze the following trader data and provide a nice summary of the data in a presentable format.

TRADER DATA:
{{trader_data}}

Be specific to what the user has asked in the conversation.

Recent conversation:
{{recentMessages}}`;


export const sentimentAnalysisTemplate = `Look at your LAST RESPONSE in the conversation where you confirmed which token sentiment to check.
Based on ONLY that last message, extract the token symbol.

For example:
- "I'll check the sentiment for HYPE" -> { "symbol": "HYPE" }
- "Let me check the sentiment of ETH" -> { "symbol": "ETH" }
- "I'll get the sentiment of HYPE" -> { "symbol": "HYPE" }

\`\`\`json
{
    "symbol": "<token symbol from your last message>"
}
\`\`\`

Note:
- Just return the token symbol (PIP, HYPE, ETH, etc.)
- Remove any suffixes like "-SPOT" or "USDC"
- If multiple tokens are mentioned, use the last one

Recent conversation:
{{recentMessages}}`;


export const analyseVaultsTemplate = `Some data has been provided to you in a JSON format. This data is the vault data from the top Hyperliquid vaults that has been analysed and summarised.

Analyze the following vault data and provide a nice summary of the data in a presentable format specific to what the user has asked in the conversation.

i.e if the user asks for the best performing vaults, you should analyse the vault data and provide a summary of the best performing vaults.

VAULT DATA:
{{vault_data}}

Recent conversation:
{{recentMessages}}`;


export const getAddressTemplate = `Look at your LAST RESPONSE in the conversation where you confirmed which trader to analyse.
Based on ONLY that last message, extract the trader's address.

For example:
- "I'll analyse the trader with address 0x1234567890123456789012345678901234567890" -> { "address": "0x1234567890123456789012345678901234567890" }
- "Let me analyse the trader with address 0x1234567890123456789012345678901234563456" -> { "address": "0x1234567890123456789012345678901234563456" }

\`\`\`json
{
    "address": "<trader's address from your last message>"
}
\`\`\`

Recent conversation:
{{recentMessages}}`;

export const getPositionsTemplate = `Some data has been provided to you in a JSON format. These are trader's current positions from the Hyperliquid database (in the positions key), and also the analysis of the trader's positions against the market data (in the analysis key).

Analyze the following trader data and provide a nice summary of the data in a presentable format specific to what the user has asked in the conversation.

For example:
- If the user asks for the trader's positions, you should analyse the trader's positions and provide a summary of the positions in a presentable format.
- If the user asks if the trader is holding a specific token, you should analyse the trader's position and extract the positions of the specific token, if any

TRADER DATA:
{{trader_data}}

Recent conversation:
{{recentMessages}}`;

