interface Leverage {
  type: 'cross';
  value: number;
}

interface CumulativeFunding {
  allTime: string;
  sinceOpen: string;
  sinceChange: string;
}

interface PositionDetails {
  coin: string;
  szi: string;
  leverage: Leverage;
  entryPx: string;
  positionValue: string;
  unrealizedPnl: string;
  returnOnEquity: string;
  liquidationPx: string | null;
  marginUsed: string;
  maxLeverage: number;
  cumFunding: CumulativeFunding;
}

interface Position {
  type: 'oneWay';
  position: PositionDetails;
}

interface MarginSummary {
  accountValue: string;
  totalNtlPos: string;
  totalRawUsd: string;
  totalMarginUsed: string;
}

interface PositionsResponse {
  marginSummary: MarginSummary;
  crossMarginSummary: MarginSummary;
  crossMaintenanceMarginUsed: string;
  withdrawable: string;
  assetPositions: Position[];
  time: number;
}

export interface TransformedPosition {
  asset: string;
  leverage: string;
  type: 'LONG' | 'SHORT';
  positionValue: number;
  size: number;
  unrealizedPnl: number;
  unrealizedPnlPercentage: number;
  entryPrice: number;
  currentPrice: number;
  returnOnEquity: number;
  liquidationPrice: number | null;
  marginUsed: number;
  maxLeverage: number;
  funding: {
    allTime: number;
    sinceOpen: number;
    sinceChange: number;
  };
}

export interface PositionsSummary {
  accountValue: number;
  totalNotional: number;
  totalRawUsd: number;
  totalMarginUsed: number;
  maintenanceMargin: number;
  withdrawable: number;
  positions: TransformedPosition[];
  lastUpdated: number;
}

export async function fetchPositions(address: string): Promise<PositionsSummary> {
  try {
    const response = await fetch('https://api.hyperliquid.xyz/info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        type: "clearinghouseState",
        user: address
      })
    });

    const data: PositionsResponse = await response.json();
    
    return {
      accountValue: parseFloat(data.marginSummary.accountValue),
      totalNotional: parseFloat(data.marginSummary.totalNtlPos),
      totalRawUsd: parseFloat(data.marginSummary.totalRawUsd),
      totalMarginUsed: parseFloat(data.marginSummary.totalMarginUsed),
      maintenanceMargin: parseFloat(data.crossMaintenanceMarginUsed),
      withdrawable: parseFloat(data.withdrawable),
      lastUpdated: data.time,
      positions: data.assetPositions.map(pos => ({
        asset: pos.position.coin,
        leverage: pos.position.leverage.value + 'x',
        type: parseFloat(pos.position.szi) > 0 ? 'LONG' : 'SHORT',
        positionValue: parseFloat(pos.position.positionValue),
        size: Math.abs(parseFloat(pos.position.szi)),
        unrealizedPnl: parseFloat(pos.position.unrealizedPnl),
        unrealizedPnlPercentage: parseFloat(pos.position.returnOnEquity),
        entryPrice: parseFloat(pos.position.entryPx),
        currentPrice: parseFloat(pos.position.positionValue) / Math.abs(parseFloat(pos.position.szi)),
        returnOnEquity: parseFloat(pos.position.returnOnEquity),
        liquidationPrice: pos.position.liquidationPx ? parseFloat(pos.position.liquidationPx) : null,
        marginUsed: parseFloat(pos.position.marginUsed),
        maxLeverage: pos.position.maxLeverage,
        funding: {
          allTime: parseFloat(pos.position.cumFunding.allTime),
          sinceOpen: parseFloat(pos.position.cumFunding.sinceOpen),
          sinceChange: parseFloat(pos.position.cumFunding.sinceChange)
        }
      }))
    };
  } catch (error) {
    console.error('Error fetching positions:', error);
    throw error;
  }
} 