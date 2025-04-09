import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchPositions, type TransformedPosition } from '@/lib/positionsApi';
import { clsx } from 'clsx';
import { useState } from 'react';

const formatUSD = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

const formatPercent = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    signDisplay: 'exceptZero',
  }).format(value / 100);
};

const Positions = () => {
  const { address } = useParams<{ address: string }>();
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    if (address) {
      navigator.clipboard.writeText(address);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const { data: positionsData, isLoading } = useQuery({
    queryKey: ['positions', address],
    queryFn: () => fetchPositions(address!),
    refetchInterval: 5000, // Refresh every 5 seconds
    enabled: !!address, // Only fetch if we have an address
  });

  if (!address) {
    return (
      <div className="p-6 text-center text-gray-400">
        No wallet address provided
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      </div>
    );
  }

  if (!positionsData) {
    return (
      <div className="p-6 text-center text-gray-400">
        No positions found
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-2 p-4 bg-surface-DEFAULT rounded-lg border border-surface-light">
        <div className="flex-1">
          <h3 className="text-gray-400 text-sm mb-1">Wallet Address</h3>
          <p className="font-mono text-sm break-all">{address}</p>
        </div>
        <button
          onClick={copyToClipboard}
          className="px-3 py-2 text-sm font-medium text-primary-500 hover:text-primary-400 transition-colors"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">Account Value</h3>
          <p className="text-2xl font-bold">{formatUSD(positionsData.accountValue)}</p>
        </div>
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">Total Notional</h3>
          <p className="text-2xl font-bold">{formatUSD(positionsData.totalNotional)}</p>
        </div>
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">Maintenance Margin</h3>
          <p className="text-2xl font-bold">{formatUSD(positionsData.maintenanceMargin)}</p>
        </div>
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">Withdrawable</h3>
          <p className="text-2xl font-bold">{formatUSD(positionsData.withdrawable)}</p>
        </div>
      </div>

      <div className="bg-surface-DEFAULT rounded-lg border border-surface-light overflow-hidden">
        <div className="p-4 border-b border-surface-light">
          <h2 className="text-xl font-bold">Positions</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-surface-light">
              <tr>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Asset</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Type</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Size</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Leverage</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Entry Price</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Mark Price</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">PnL</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">ROE</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Liquidation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-light">
              {positionsData.positions.map((position: TransformedPosition) => (
                <tr key={position.asset} className="hover:bg-surface-light/50">
                  <td className="p-4 font-medium">{position.asset}</td>
                  <td className="p-4">
                    <span className={clsx(
                      'px-2 py-1 rounded text-xs font-medium',
                      position.type === 'LONG' ? 'bg-emerald-400/20 text-emerald-400' : 'bg-red-500/20 text-red-500'
                    )}>
                      {position.type}
                    </span>
                  </td>
                  <td className="p-4">{position.size.toLocaleString()}</td>
                  <td className="p-4">{position.leverage}</td>
                  <td className="p-4">${position.entryPrice.toFixed(2)}</td>
                  <td className="p-4">${position.currentPrice.toFixed(2)}</td>
                  <td className={clsx('p-4', position.unrealizedPnl >= 0 ? 'text-emerald-400' : 'text-red-500')}>
                    {formatUSD(position.unrealizedPnl)}
                    <div className="text-xs">
                      {formatPercent(position.unrealizedPnlPercentage)}
                    </div>
                  </td>
                  <td className={clsx('p-4', position.returnOnEquity >= 0 ? 'text-emerald-400' : 'text-red-500')}>
                    {formatPercent(position.returnOnEquity)}
                  </td>
                  <td className="p-4">
                    {position.liquidationPrice ? `$${position.liquidationPrice.toFixed(2)}` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Positions; 