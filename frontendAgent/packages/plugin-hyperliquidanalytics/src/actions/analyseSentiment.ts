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
import { analyseTradersTemplate, sentimentAnalysisTemplate } from "../templates.js";
import axios from 'axios';

export const analyseSentiment: Action = {
    name: "ANALYSE_SENTIMENT",
    similes: ["ANALYSE_SENTIMENT", "ANALYSE_SENTIMENT_PERFORMANCE", "GET_SENTIMENT_ANALYSIS"],
    description: "Analyse sentiment on Hyperliquid",
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
                template: sentimentAnalysisTemplate,
            });

            const content = await generateObjectDeprecated({
                runtime,
                context,
                modelClass: ModelClass.SMALL,
            });

            if (!content?.symbol) {
                elizaLogger.error("Error checking sentiment:",);
                if (callback) {
                    callback({
                        text: `Error checking sentiment: Could not determine which token sentiment to check`,
                        content: { error: "Could not determine which token sentiment to check" },
                    });
                }
            }

            // Make the API request to our analysis API
            const response = await axios.get(`http://localhost:8000/analysis/sentiment/${content.symbol}`);

            elizaLogger.info(`[INFO] [ANALYSE_SENTIMENT] ${JSON.stringify(response.data, null, 2)}`);

            if (response.data.status !== 'success') {
                elizaLogger.error("Error checking sentiment:",);
                if (callback) {
                    callback({
                        text: `Error checking sentiment: Failed to get sentiment analysis`,
                        content: { error: "Failed to get sentiment analysis" },
                    });
                }
            }

            const analyseDataContext = `You have just received a response from the sentiment analysis API.
            The response is as follows:
            ${JSON.stringify(response.data, null, 2)}

            Analyse the response and provide a summary of the sentiment analysis.
            `
            const newContext = composeContext({
                state: currentState,
                template: analyseDataContext,
            });



            const llmResponse = await generateText({
                runtime,
                context: newContext,
                modelClass: ModelClass.SMALL,
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
                    text: "What's the sentiment around HYPE token?",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll check the sentiment analysis for HYPE token.",
                    action: "ANALYSE_SENTIMENT",
                },
            },
        ],
        [
            {
                user: "{{user1}}",
                content: {
                    text: "How are people feeling about ETH right now?", 
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "Let me analyze the current sentiment for ETH.",
                    action: "ANALYSE_SENTIMENT",
                },
            },
        ],
        [
            {
                user: "{{user1}}",
                content: {
                    text: "Check the market sentiment for BTC please",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll check what the overall sentiment is for BTC.",
                    action: "ANALYSE_SENTIMENT", 
                },
            },
        ],
    ] as ActionExample[][],
};
