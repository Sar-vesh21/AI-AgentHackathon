interface VaultSummary {
  name: string;
  vaultAddress: string;
  leader: string;
  tvl: string;
  isClosed: boolean;
  relationship: {
    type: string;
  };
  createTimeMillis: number;
}

// interface VaultPnlData {
//   timeframe: 'day' | 'week' | 'month' | 'allTime';
//   values: string[];
// }

export interface VaultData {
  apr: number;
  pnls: [string, string[]][];
  summary: VaultSummary;
}

export interface TransformedVaultData {
  name: string;
  address: string;
  tvl: number;
  aprChange: number;
  chart: {
    labels: string[];
    values: number[];
  };
  allTimePnl: number;
  isActive: boolean;
}

export async function fetchVaults(): Promise<TransformedVaultData[]> {
  try {
    const response = await fetch('https://stats-data.hyperliquid.xyz/Mainnet/vaults');
    const data: VaultData[] = await response.json();
    console.log(data);
    
    // Sort by TVL (highest first) and limit to 50 vaults before transforming
    return data
      .sort((a, b) => parseFloat(b.summary.tvl) - parseFloat(a.summary.tvl))
      .slice(0, 50)
      .map((vault) => {
        // Find the allTime PNL data
        const allTimePnls = vault.pnls.find(([timeframe]) => timeframe === 'allTime')?.[1] || [];
        
        // Get the latest non-zero PNL value
        const latestPnl = allTimePnls.reverse().find(val => val !== "0.0") || "0.0";
        
        // Calculate APR change - if APR is 0, use the difference between latest and previous PNL
        const aprChange = vault.apr || (parseFloat(latestPnl) - parseFloat(allTimePnls[1] || "0.0"));

        return {
          name: vault.summary.name,
          address: vault.summary.vaultAddress,
          tvl: parseFloat(vault.summary.tvl),
          aprChange,
          chart: {
            // Use timestamps for labels
            labels: allTimePnls.map((_, i) => 
              new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString()
            ),
            // Convert PNL strings to numbers and reverse to show oldest to newest
            values: allTimePnls.map(val => parseFloat(val)).reverse()
          },
          allTimePnl: parseFloat(latestPnl),
          isActive: !vault.summary.isClosed
        };
      });
  } catch (error) {
    console.error('Error fetching vaults:', error);
    return [];
  }
} 