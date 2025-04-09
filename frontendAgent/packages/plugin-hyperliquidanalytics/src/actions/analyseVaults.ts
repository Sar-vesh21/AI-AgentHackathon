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
import { analyseVaultsTemplate } from "../templates.js";
import axios from 'axios';

export const analyseVaults: Action = {
    name: "ANALYSE_VAULTS",
    similes: ["ANALYSE_VAULT", "ANALYSE_VAULT_PERFORMANCE", "GET_VAULT_ANALYSIS"],
    description: "Analyse vaults on Hyperliquid",
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
            const response = await axios.get('http://localhost:8000/analysis/vaults');

            if (response.data.status !== 'success') {
                throw new Error('Failed to get vault analysis');
            }

            elizaLogger.info(`[ANALYSE_VAULTS] ${JSON.stringify(response.data, null, 2)}`);

            // Add trader data to the state
            const updatedState = {
                ...currentState,
                vault_data: JSON.stringify(response.data.data, null, 2)
            };

            // Prepare context for LLM analysis
            const context = composeContext({
                state: updatedState,
                template: analyseVaultsTemplate,
            });

            // Generate analysis using LLM
            // const analysis = await runtime.generateResponse(context);

            elizaLogger.info(`[INFO] [ANALYSE_VAULTS] ${JSON.stringify(context, null, 2)}`);

            const llmResponse = await generateText({
                runtime,
                context,
                modelClass: ModelClass.SMALL,
            });

            elizaLogger.info(`[INFO] [ANALYSE_VAULTS] ${llmResponse}`);
    

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
                    text: "Analyze the vaults on Hyperliquid",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "This may take a moment, bare with me. Here's the analysis of the vaults...",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll analyze the vaults and provide insights about their performance.",
                    action: "ANALYSE_VAULTS",
                },
            },
        ],
        [
            {
                user: "{{user1}}",
                content: {
                    text: "What are the best performing vaults?",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "Let me analyze the vaults and find the top performers...",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll analyze the vault performance metrics and highlight the best ones.",
                    action: "ANALYSE_VAULTS", 
                },
            },
            {
                user: "{{user1}}",
                content: {
                    text: "What are the vaults looking on Hyperliquid?",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "Let me analyze the vaults and find the top performers...",
                },
            },
            {
                user: "{{agent}}",
                content: {
                    text: "I'll analyze the vaults and provide insights about their performance.",
                    action: "ANALYSE_VAULTS",
                },
            },
        ],
    ] as ActionExample[][],
};
