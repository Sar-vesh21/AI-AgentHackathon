import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
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
import { clsx } from 'clsx';
import { fetchVaults, type TransformedVaultData } from '@/lib/vaultsApi';

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

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: false,
    },
  },
  scales: {
    x: {
      display: false,
    },
    y: {
      display: false,
    },
  },
  elements: {
    point: {
      radius: 0,
    },
    line: {
      tension: 0.4,
      borderWidth: 2,
    },
  },
};

const VaultCard = ({ vault }: { vault: TransformedVaultData }) => {
  const chartData = {
    labels: vault.chart.labels,
    datasets: [
      {
        data: vault.chart.values,
        borderColor: vault.aprChange >= 0 ? '#10B981' : '#EF4444',
        backgroundColor: vault.aprChange >= 0 
          ? 'rgba(16, 185, 129, 0.1)' 
          : 'rgba(239, 68, 68, 0.1)',
        fill: true,
      },
    ],
  };

  return (
    <div className="bg-surface-DEFAULT rounded-lg border border-surface-light p-4">
      <div className="mb-2">
        <h3 className="text-lg font-medium">{vault.name}</h3>
        <div className="text-sm text-gray-400">{vault.address}</div>
      </div>
      
      <div className="mb-4">
        <div className="text-sm text-gray-400">TVL</div>
        <div className="text-xl font-bold">
          ${(vault.tvl / 1_000_000).toFixed(2)}M
        </div>
        <div className={clsx(
          'text-sm',
          vault.aprChange >= 0 ? 'text-emerald-400' : 'text-red-500'
        )}>
          {vault.aprChange >= 0 ? '+' : ''}{vault.aprChange.toFixed(2)}%
        </div>
      </div>

      <div className="h-24 mb-2">
        <Line data={chartData} options={chartOptions} />
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-400">All-time PNL</span>
        <span className={clsx(
          'flex items-center gap-1',
          vault.allTimePnl >= 0 ? 'text-emerald-400' : 'text-red-500'
        )}>
          {vault.allTimePnl >= 0 ? '↗' : '↘'}
        </span>
      </div>
    </div>
  );
};

const Vaults = () => {
  const [sortBy, setSortBy] = useState<'tvl' | 'apr'>('tvl');
  const [showClosed, setShowClosed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: vaults = [], isLoading } = useQuery({
    queryKey: ['vaults'],
    queryFn: fetchVaults,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const filteredAndSortedVaults = useMemo(() => {
    return vaults
      .filter((vault: TransformedVaultData) => {
        if (!showClosed && !vault.isActive) return false;
        if (searchQuery) {
          const query = searchQuery.toLowerCase();
          return vault.name.toLowerCase().includes(query) ||
                 vault.address.toLowerCase().includes(query);
        }
        return true;
      })
      .sort((a: TransformedVaultData, b: TransformedVaultData) => {
        if (sortBy === 'tvl') {
          return b.tvl - a.tvl;
        } else {
          return b.aprChange - a.aprChange;
        }
      });
  }, [vaults, sortBy, showClosed, searchQuery]);

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Vaults</h1>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSortBy('tvl')}
              className={clsx(
                'px-3 py-1.5 text-sm rounded-md',
                sortBy === 'tvl' ? 'bg-primary-500 text-white' : 'text-gray-400 hover:bg-surface-light'
              )}
            >
              TVL ↓
            </button>
            <button
              onClick={() => setSortBy('apr')}
              className={clsx(
                'px-3 py-1.5 text-sm rounded-md',
                sortBy === 'apr' ? 'bg-primary-500 text-white' : 'text-gray-400 hover:bg-surface-light'
              )}
            >
              Sort by APR
            </button>
          </div>

          <button
            onClick={() => setShowClosed(!showClosed)}
            className={clsx(
              'px-3 py-1.5 text-sm rounded-md',
              showClosed ? 'bg-primary-500 text-white' : 'text-gray-400 hover:bg-surface-light'
            )}
          >
            Show Closed
          </button>

          <div className="relative">
            <input
              type="text"
              placeholder="Search vaults..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-64 px-4 py-1.5 text-sm rounded-md bg-surface-light border border-surface-light focus:outline-none focus:border-primary-500"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAndSortedVaults.map((vault: TransformedVaultData) => (
            <VaultCard key={vault.address} vault={vault} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Vaults; 