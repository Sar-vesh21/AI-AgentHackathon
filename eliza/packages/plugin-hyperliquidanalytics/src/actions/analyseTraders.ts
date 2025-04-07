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
} from "@elizaos/core";
import { analyseTradersTemplate } from "../templates.js";
import axios from 'axios';

export const analyseTraders: Action = {
    name: "ANALYSE_TRADERS",
    similes: ["ANALYSE_TRADER", "ANALYSE_TRADER_PERFORMANCE", "GET_TRADER_ANALYSIS"],
    description: "Analyse traders on Hyperliquid",
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

            // Make the API request to our analysis API
            const response = await axios.get('http://localhost:8000/analysis/recent', {
                params: {
                    limit: 50  // Default limit, can be adjusted based on conversation
                }
            });

            if (response.data.status !== 'success') {
                throw new Error('Failed to get trader analysis');
            }

            elizaLogger.info(`[ANALYSE_TRADERS] ${JSON.stringify(response.data, null, 2)}`);

            // Add trader data to the state
            const updatedState = {
                ...currentState,
                trader_data: JSON.stringify(response.data.data, null, 2)
            };

            // Prepare context for LLM analysis
            const context = composeContext({
                state: updatedState,
                template: analyseTradersTemplate,
            });

            // Generate analysis using LLM
            // const analysis = await runtime.generateResponse(context);

            elizaLogger.info(`[INFO] [ANALYSE_TRADERS] ${JSON.stringify(context, null, 2)}`);

            const llmResponse = await generateText({
                runtime,
                context,
                modelClass: ModelClass.SMALL,
            });

            elizaLogger.info(`[INFO] [ANALYSE_TRADERS] ${llmResponse}`);
    

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
                    text: "Analyze the recent traders",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "This may take a moment, bare with me. Here's the analysis of recent traders...",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll analyze the recent traders and provide insights about their trading patterns.",
                    action: "ANALYSE_TRADERS",
                },
            },
        ],
        [
            {
                user: "{{user1}}",
                content: {
                    text: "What are the trading styles of recent traders?",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "This may take a moment, bare with me. Here's the analysis of recent traders...",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll analyze the trading styles of recent traders.",
                    action: "ANALYSE_TRADERS",
                },
            },
        ],
    ] as ActionExample[][],
};
