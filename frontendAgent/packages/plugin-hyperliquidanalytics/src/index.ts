import type { Plugin } from "@elizaos/core";
import { analyseTraders } from "./actions/analyseTraders";
import { priceCheck } from "./actions/priceCheck";
import { analyseSentiment } from "./actions/analyseSentiment";
import { analyseVaults } from "./actions/analyseVaults";
import { analyseTrader } from "./actions/analyseTrader";
// import { cancelOrders } from "./actions/cancelOrders";

export const hyperliquidAnalyticsPlugin: Plugin = {
    name: "hyperliquidanalytics",
    description: "Hyperliquid Analytics plugin",
    actions: [analyseTraders, priceCheck, analyseSentiment, analyseVaults, analyseTrader],
    providers: [],
    evaluators: [],
    services: [],
    clients: [],
};

export default hyperliquidAnalyticsPlugin;
