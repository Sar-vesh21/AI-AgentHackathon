import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { forwardRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { fetchTokens, fetchChartData, fetchHypeSentiment, fetchTraderSummarys } from '@/lib/statsApi';
import { clsx } from 'clsx';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Dashboard = forwardRef<HTMLDivElement>((_, ref) => {
  const [timeframe, setTimeframe] = useState<number>(30); // Default to 30 days
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 50;

  const { data: tokens } = useQuery({
    queryKey: ['tokens'],
    queryFn: fetchTokens,
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  const { data: chartData, isLoading: chartLoading } = useQuery({
    queryKey: ['chart', timeframe],
    queryFn: () => fetchChartData(timeframe),
    refetchInterval: 300000, // Refresh every 5 minutes
  });

  const { data: sentimentData } = useQuery({
    queryKey: ['sentiment'],
    queryFn: fetchHypeSentiment,
  });

  const { data: tradersData, isLoading: tradersLoading } = useQuery({
    queryKey: ['traders', currentPage],
    queryFn: () => fetchTraderSummarys(currentPage, pageSize),
    refetchInterval: 1000 // Refresh every 30 seconds
  });

  // Add console logs to inspect data
  console.log('Sentiment Data:', sentimentData);
  console.log('Traders Data:', tradersData);
  console.log('Traders Loading:', tradersLoading);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        grid: {
          // color: 'rgba(255, 255, 255, 0.1)',
          display: false,
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
    },
  };

  return (
    <div ref={ref} className="p-6 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">Total Volume</h3>
          <p className="text-2xl font-bold">$45.2M</p>
          <span className="text-primary-500 text-sm">+20.1% from last month</span>
        </div>
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">HYPE Sentiment</h3>
          <p className="text-2xl font-bold flex items-center gap-2">
            {sentimentData?.data.trend === 'up'}
            {sentimentData?.data.trend === 'down'}
            {sentimentData?.data.trend === 'stable'}
            {sentimentData?.data.sentiment_percentages.tweet.positive.toFixed(1)}%
          </p>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-primary">
              {sentimentData?.data.total_interactions.toLocaleString()} interactions
            </span>
            <span className="text-gray-400">•</span>
            <span className="text-gray-400">
              {sentimentData?.data.num_contributors.toLocaleString()} contributors
            </span>
          </div>
        </div>
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">Open Interest</h3>
          <p className="text-2xl font-bold">$12.8M</p>
          <span className="text-primary-500 text-sm">+12% from last week</span>
        </div>
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">Liquidations (24h)</h3>
          <p className="text-2xl font-bold">$1.2M</p>
          <span className="text-red-500 text-sm">-4% from yesterday</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-surface-DEFAULT p-6 rounded-lg border border-surface-light">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold">Price Chart</h2>
            <div className="flex space-x-2">
              <button 
                className={`px-3 py-1 text-sm rounded-md ${timeframe === 1 ? 'bg-primary-500 text-white' : 'hover:bg-surface-light'}`}
                onClick={() => setTimeframe(1)}
              >
                24H
              </button>
              <button 
                className={`px-3 py-1 text-sm rounded-md ${timeframe === 7 ? 'bg-primary-500 text-white' : 'hover:bg-surface-light'}`}
                onClick={() => setTimeframe(7)}
              >
                7D
              </button>
              <button 
                className={`px-3 py-1 text-sm rounded-md ${timeframe === 30 ? 'bg-primary-500 text-white' : 'hover:bg-surface-light'}`}
                onClick={() => setTimeframe(30)}
              >
                1M
              </button>
            </div>
          </div>
          <div className="h-[400px]">
            {chartLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
              </div>
            ) : chartData ? (
              <Line data={chartData} options={chartOptions} />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                No data available
              </div>
            )}
          </div>
        </div>

        <div className="bg-surface-DEFAULT p-6 rounded-lg border border-surface-light">
          <h2 className="text-xl font-bold mb-6">Top Tokens</h2>
          <div className="space-y-4">
            {tokens?.map((token: any) => (
              <div key={token.symbol} className="flex items-center justify-between p-3 hover:bg-surface-light rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-full bg-surface-light flex items-center justify-center text-sm font-bold">
                    {token.symbol.slice(0, 2)}
                  </div>
                  <div>
                    <div className="font-medium">{token.name}</div>
                    <div className="text-sm text-gray-400">{token.symbol}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium">{token.price}</div>
                  <div className={token.change.startsWith('+') ? 'text-primary-500' : 'text-red-500'}>
                    {token.change}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-surface-DEFAULT rounded-lg border border-surface-light overflow-hidden">
        <div className="p-4 border-b border-surface-light">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold">Traders</h2>
            {tradersLoading ? (
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-emerald-400"></div>
                <span className="text-sm text-gray-400">Loading...</span>
              </div>
            ) : (
              <div className="text-sm text-gray-400">
                Showing {((tradersData?.pagination?.current_page ?? 1) - 1) * pageSize + 1}-{Math.min((tradersData?.pagination?.current_page ?? 1) * pageSize, tradersData?.pagination?.total_items ?? 0)} of {tradersData?.pagination?.total_items ?? 0}
              </div>
            )}
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-surface-light">
              <tr>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Trader</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Account Value</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Position Bias</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Daily PnL</th>
                <th className="p-4 text-left text-sm font-medium text-gray-400">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-light">
              {tradersLoading ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center">
                    <div className="flex flex-col items-center gap-2">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-400"></div>
                      <span className="text-sm text-gray-400">Loading traders...</span>
                    </div>
                  </td>
                </tr>
              ) : tradersData?.data?.map((trader: any) => (
                <tr key={trader.address} className="hover:bg-surface-light/50 cursor-pointer">
                  <Link to={`/positions/${trader.address}`} className="contents">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-surface-light flex items-center justify-center">
                          <span className="text-xs">🤖</span>
                        </div>
                        <div>
                          <div className="font-medium">{trader.display_name === "Unknown" ? 
                            `${trader.address.slice(0, 6)}...${trader.address.slice(-4)}` : 
                            trader.display_name}
                          </div>
                          <div className="text-xs text-gray-400">
                            {trader.analysis.metrics.most_traded_asset}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4 font-medium">${(trader.account_value / 1_000_000).toFixed(2)}M</td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className={clsx(
                          'px-2 py-1 rounded text-xs font-medium',
                          trader.analysis.metrics.position_bias === 'Long' ? 'bg-emerald-400/20 text-emerald-400' : 
                          trader.analysis.metrics.position_bias === 'Short' ? 'bg-red-500/20 text-red-500' :
                          'bg-gray-500/20 text-gray-500'
                        )}>
                          {trader.analysis.metrics.position_bias}
                        </span>
                        <span className="text-xs text-gray-400">
                          {trader.analysis.metrics.buy_percentage.toFixed(1)}% buy
                        </span>
                      </div>
                    </td>
                    <td className={clsx('p-4', trader.daily_pnl >= 0 ? 'text-emerald-400' : 'text-red-500')}>
                      ${(trader.daily_pnl / 1_000).toFixed(1)}K
                      <div className="text-xs text-gray-400">
                        {(trader.daily_roi * 100).toFixed(2)}%
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-1">
                        <div className={clsx(
                          'w-2 h-2 rounded-full',
                          trader.analysis.reputation_scores.overall >= 70 ? 'bg-primary-500' :
                          trader.analysis.reputation_scores.overall >= 40 ? 'bg-yellow-500' :
                          'bg-red-500'
                        )}></div>
                        <span className="font-medium">{trader.analysis.reputation_scores.overall}</span>
                      </div>
                    </td>
                  </Link>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {!tradersLoading && (
          <div className="flex items-center justify-between p-4 border-t border-surface-light">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={!tradersData?.pagination?.has_previous}
              className={clsx(
                'px-4 py-2 rounded-md text-sm',
                !tradersData?.pagination?.has_previous ? 'text-gray-500 cursor-not-allowed' : 'text-emerald-400 hover:bg-surface-light'
              )}
            >
              Previous
            </button>
            
            <div className="flex items-center gap-2">
              {Array.from({ length: Math.min(5, tradersData?.pagination?.total_pages ?? 0) }, (_, i) => {
                const page = i + 1;
                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={clsx(
                      'w-8 h-8 rounded-md text-sm',
                      tradersData?.pagination?.current_page === page ? 'bg-emerald-400 text-white' : 'text-gray-400 hover:bg-surface-light'
                    )}
                  >
                    {page}
                  </button>
                );
              })}
              {tradersData?.pagination?.total_pages && tradersData.pagination.total_pages > 5 && (
                <span className="text-gray-400">...</span>
              )}
            </div>

            <button
              onClick={() => setCurrentPage(prev => Math.min(tradersData?.pagination?.total_pages ?? 1, prev + 1))}
              disabled={!tradersData?.pagination?.has_next}
              className={clsx(
                'px-4 py-2 rounded-md text-sm',
                !tradersData?.pagination?.has_next ? 'text-gray-500 cursor-not-allowed' : 'text-emerald-400 hover:bg-surface-light'
              )}
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
});

Dashboard.displayName = 'Dashboard';

export default Dashboard; 