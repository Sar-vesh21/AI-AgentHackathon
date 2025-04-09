import {
    type Action,
    type ActionExample,
    type IAgentRuntime,
    type Memory,
    type State,
    type HandlerCallback,
    composeContext,
    elizaLogger,
    generateMessageResponse,
    ModelClass,
    generateText,
    generateObjectDeprecated,
} from "@elizaos/core";
import { analyseTradersTemplate, sentimentAnalysisTemplate, getAddressTemplate, getPositionsTemplate } from "../templates.js";
import axios from 'axios';

export const analyseTrader: Action = {
    name: "ANALYSE_TRADER",
    similes: ["ANALYSE_TRADER", "ANALYSE_TRADER_PERFORMANCE", "GET_TRADER_ANALYSIS"],
    description: "Analyse trader on Hyperliquid",
    validate: async () => true,
    handler: async (
        runtime: IAgentRuntime,
        message: Memory,
        state: State,
        _options: Record<string, unknown>,
        callback?: HandlerCallback
    ) => {
        try {
            // Initialize or update state
            const currentState = !state
                ? await runtime.composeState(message)
                : await runtime.updateRecentMessageState(state);

            const context = composeContext({
                state: currentState,
                template: getAddressTemplate,
            });

            const content = await generateObjectDeprecated({
                runtime,
                context,
                modelClass: ModelClass.SMALL,
            });

            if (!content?.address) {
                elizaLogger.error("Error getting address:",);
                if (callback) {
                    callback({
                        text: `Error getting address: Could not determine which trader to analyse`,
                        content: { error: "Could not determine which trader to analyse" },
                    });
                }
            }

            // Make the API request to our analysis API
            const response = await axios.get(`http://localhost:8000/analysis/positions/${content.address}`);

            elizaLogger.info(`[INFO] [ANALYSE_TRADER] ${JSON.stringify(response.data, null, 2)}`);

            if (response.data.status !== 'success') {
                elizaLogger.error("Error getting positions:",);
                if (callback) {
                    callback({
                        text: `Error getting positions: Failed to get positions`,
                        content: { error: "Failed to get positions" },
                    });
                }
            }

            const updatedState = {
                ...currentState,
                trader_data: JSON.stringify(response.data.data, null, 2)
            };
        
            const newContext = composeContext({
                state: updatedState,
                template: getPositionsTemplate,
            });


            const llmResponse = await generateText({
                runtime,
                context: newContext,
                modelClass: ModelClass.LARGE,
            });


            // Send the analysis back to the user
            if (callback) {
                callback({
                    text: llmResponse,
                });
            }

            return true;
        } catch (error) {
            elizaLogger.error("Error analyzing traders:", error);
            if (callback) {
                callback({
                    text: `Error analyzing traders: ${error.message}`,
                    content: { error: error.message }
                });
            }
            return false;
        }
    },
    examples: [
        [
            {
                user: "{{user1}}",
                content: {
                    text: "Can you check the positions for trader 0x1234567890123456789012345678901234567890?",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll analyse the trader with address 0x1234567890123456789012345678901234567890",
                    action: "ANALYSE_TRADER",
                },
            },
        ],
        [
            {
                user: "{{user1}}",
                content: {
                    text: "What positions does 0x1234567890123456789012345678901234563456 have?",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "Let me analyse the trader with address 0x1234567890123456789012345678901234563456",
                    action: "ANALYSE_TRADER",
                },
            },
        ],
        [
            {
                user: "{{user1}}",
                content: {
                    text: "Show me the trading history for 0x1234567890123456789012345678901234567123",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll check the positions and history for trader 0x1234567890123456789012345678901234567123",
                    action: "ANALYSE_TRADER",
                },
            },
        ],
        [
            {
                user: "{{user1}}",
                content: {
                    text: "How does trader 0x1234567890123456789012345678901234567890 compare to market trends?",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll analyze how trader 0x1234567890123456789012345678901234567890's positions and performance compare to overall market movements",
                    action: "ANALYSE_TRADER",
                },
            },
        ],
    ] as ActionExample[][],
};
