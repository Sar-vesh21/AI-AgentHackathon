// // Types
// interface Vault {
//     id: string;
//     name: string;
//     tvl: number;
//     apy: number;
//     strategy: string;
//     performance: {
//         daily: number;
//         weekly: number;
//         monthly: number;
//         allTime: number;
//     };
// }

// interface Trader {
//     id: string;
//     address: string;
//     name: string;
//     pnl: {
//         daily: number;
//         weekly: number;
//         monthly: number;
//         allTime: number;
//     };
//     volume: {
//         daily: number;
//         weekly: number;
//         monthly: number;
//         allTime: number;
//     };
//     roi: number;
// }

// interface Stats {
//     totalTvl: number;
//     totalVolume24h: number;
//     totalTraders: number;
//     totalVaults: number;
//     topPerformingVault: {
//         id: string;
//         name: string;
//         performance: number;
//     };
//     topPerformingTrader: {
//         id: string;
//         name: string;
//         performance: number;
//     };
// }

// interface Token {
//     symbol: string;
//     name: string;
//     price: string;
//     change: string;
// }

// interface CoinGeckoResponse {
//     [key: string]: {
//         usd: number;
//         usd_24h_change: number;
//         usd_24h_vol?: number;
//     };
// }

// interface ChartData {
//     labels: string[];
//     datasets: {
//         label: string;
//         data: number[];
//         fill: boolean;
//         borderColor: string;
//         backgroundColor: string;
//         tension: number;
//     }[];
// }

// interface CoinGeckoChartResponse {
//     prices: [number, number][]; // [timestamp, price]
// }

// interface SentimentData {
//     sentiment_percentages: {
//         positive: number;
//         neutral: number;
//         negative: number;
//     };
//     total_interactions: number;
//     num_contributors: number;
//     trend: 'up' | 'down' | 'stable';
// }

// interface TraderData {
//     address: string;
//     account_value: number;
//     display_name: string;
//     daily_pnl: number;
//     daily_roi: number;
//     weekly_pnl: number;
//     monthly_pnl: number;
//     all_time_pnl: number;
//     analysis: {
//         metrics: {
//             position_bias: string;
//             buy_percentage: number;
//             total_buy_volume: number;
//             total_sell_volume: number;
//             most_traded_asset: string;
//         };
//         reputation_scores: {
//             overall: number;
//             experience: number;
//             consistency: number;
//             risk_management: number;
//             performance: number;
//         };
//         trading_style: {
//             position_size_consistency: number;
//             sizing_approach: string;
//         };
//     };
// }

// interface TraderSummaryResponse {
//     data: TraderData[];
//     pagination: {
//         current_page: number;
//         has_next: boolean;
//         has_previous: boolean;
//         page_size: number;
//         total_items: number;
//         total_pages: number;
//     };
// }

// Base URL for API endpoints
const BASE_URL = "";
const HYPERLIQUID_BASE_URL = "https://api.hyperliquid.xyz/info";

const COINGECKO_API_KEY = 'CG-DssZCqvgtcftTwkEgsyqackM';

// Map of our token symbols to CoinGecko IDs
const TOKEN_ID_MAP: { [key: string]: string } = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SOL': 'solana',
    'BNB': 'binancecoin',
    'HYPE': 'hyperliquid'
};

// Helper function for making API requests
const fetcher = async <T>(url: string, options?: RequestInit, baseUrl: string = BASE_URL): Promise<T> => {
    const response = await fetch(`${baseUrl}${url}`, {
        headers: {
            "Content-Type": "application/json",
        },
        ...options,
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
    }

    const data = await response.json();
    console.log('API Response:', data);
    
    return data;
};

// Vault related functions
export const fetchVaults = async (): Promise<any> => {

    return fetcher<any>(`/vaults`, undefined, HYPERLIQUID_BASE_URL);
};

export const fetchVaultById = async (vaultId: string): Promise<any> => {
    return fetcher<any>(`/vaults/${vaultId}`, undefined, HYPERLIQUID_BASE_URL);
};

// Trader related functions
export const fetchTraders = async (limit: number = 50): Promise<any> => {
    return fetcher<any>(`/analysis/traders?limit=${limit}`);
};

export const fetchTraderSummarys = async (page: number = 1, page_size: number = 50): Promise<any> => {
    return fetcher<any>(`/analysis/traderSummary?page=${page}&page_size=${page_size}`);
};

export const fetchTraderById = async (traderId: string): Promise<any> => {
    return fetcher<any>(`/traders/${traderId}`, undefined, HYPERLIQUID_BASE_URL);
};

// Stats related functions
export const fetchStats = async (): Promise<any> => {
    return fetcher<any>("/stats", undefined, HYPERLIQUID_BASE_URL);
};

// Token related functions
export const fetchTokens = async (): Promise<any> => {
    const ids = Object.values(TOKEN_ID_MAP).join(',');
    const url = `https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true`;
    
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'accept': 'application/json',
            'x-cg-demo-api-key': COINGECKO_API_KEY
        }
    });

    if (!response.ok) {
        throw new Error('Failed to fetch token data');
    }

    const data: any = await response.json();

    // Convert CoinGecko data to our Token format
    return Object.entries(TOKEN_ID_MAP).map(([symbol, geckoId]) => {
        const tokenData = data[geckoId];
        return {
            symbol,
            name: getTokenName(symbol),
            price: formatPrice(tokenData.usd),
            change: formatChange(tokenData.usd_24h_change)
        };
    });
};

// Chart related functions
export const fetchChartData = async (days: number = 30): Promise<any> => {
    const url = `https://api.coingecko.com/api/v3/coins/hyperliquid/market_chart?vs_currency=usd&days=${days}&interval=daily`;
    
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'accept': 'application/json',
            'x-cg-demo-api-key': COINGECKO_API_KEY
        }
    });

    if (!response.ok) {
        throw new Error('Failed to fetch chart data');
    }

    const data: any = await response.json();

    // Format dates and prices
    const formattedData = data.prices.map(([timestamp, price]: [any, any]) => {
        const date = new Date(timestamp);
        return {
            date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            price
        };
    });

    return {
        labels: formattedData.map((d: any) => d.date),
        datasets: [
            {
                label: 'Price',
                data: formattedData.map((d: any) => d.price),
                fill: true,
                borderColor: '#10B981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
            },
        ],
    };
};

// Sentiment related functions
export const fetchHypeSentiment = async (): Promise<any> => {
    return fetcher<any>('/analysis/sentiment/hyperliquid');
};

// Meta and Asset Context functions
interface AssetContext {
    funding: string;
    openInterest: string;
    prevDayPx: string;
    dayNtlVlm: string;
    premium: string | null;
    oraclePx: string;
    markPx: string;
    midPx: string | null;
    impactPxs: string[] | null;
    dayBaseVlm: string;
}

interface AssetInfo {
    szDecimals: number;
    name: string;
    maxLeverage: number;
    marginTableId: number;
    isDelisted?: boolean;
    onlyIsolated?: boolean;
}

interface MarginTier {
    lowerBound: string;
    maxLeverage: number;
}

interface MarginTable {
    description: string;
    marginTiers: MarginTier[];
}

interface MetaAndAssetContextsResponse {
    universe: AssetInfo[];
    marginTables: [number, MarginTable][];
    assetContexts: AssetContext[];
}

export const fetchMetaAndAssetContexts = async (): Promise<MetaAndAssetContextsResponse> => {
    const url = 'https://api.hyperliquid.xyz/info';
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: "metaAndAssetCtxs"
        })
    });

    if (!response.ok) {
        throw new Error('Failed to fetch meta and asset contexts');
    }

    const data = await response.json();
    return {
        universe: data[0].universe,
        marginTables: data[0].marginTables,
        assetContexts: data[1]
    };
};

// Helper functions
const getTokenName = (symbol: string): string => {
    const names: { [key: string]: string } = {
        'BTC': 'Bitcoin',
        'ETH': 'Ethereum',
        'SOL': 'Solana',
        'BNB': 'Binance Coin',
        'HYPE': 'Hyperliquid'
    };
    return names[symbol] || symbol;
};

const formatPrice = (price: number): string => {
    return `$${price.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
};

const formatChange = (change: number): string => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(1)}%`;
};
