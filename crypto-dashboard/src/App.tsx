import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useState } from 'react';
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

// Components
const Dashboard = () => {
  const chartData = {
    labels: ['Apr 1', 'Apr 6', 'Apr 11', 'Apr 16', 'Apr 21', 'Apr 26'],
    datasets: [
      {
        label: 'Price',
        data: [1.5, 1.8, 2.1, 1.9, 2.3, 2.4],
        fill: true,
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
      },
    ],
  };

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
          color: 'rgba(255, 255, 255, 0.1)',
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
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">Total Volume</h3>
          <p className="text-2xl font-bold">$45.2M</p>
          <span className="text-primary-500 text-sm">+20.1% from last month</span>
        </div>
        <div className="bg-surface-DEFAULT p-4 rounded-lg border border-surface-light">
          <h3 className="text-gray-400 text-sm">Active Traders</h3>
          <p className="text-2xl font-bold">2,350</p>
          <span className="text-primary-500 text-sm">+180 since yesterday</span>
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
              <button className="px-3 py-1 text-sm rounded-md bg-primary-500 text-white">24H</button>
              <button className="px-3 py-1 text-sm rounded-md hover:bg-surface-light">7D</button>
              <button className="px-3 py-1 text-sm rounded-md hover:bg-surface-light">1M</button>
            </div>
          </div>
          <div className="h-[400px]">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        <div className="bg-surface-DEFAULT p-6 rounded-lg border border-surface-light">
          <h2 className="text-xl font-bold mb-6">Top Tokens</h2>
          <div className="space-y-4">
            {[
              { symbol: 'BTC', name: 'Bitcoin', price: '$45,000', change: '+5.2%' },
              { symbol: 'ETH', name: 'Ethereum', price: '$2,800', change: '+3.1%' },
              { symbol: 'SOL', name: 'Solana', price: '$120', change: '-2.3%' },
              { symbol: 'ARB', name: 'Arbitrum', price: '$1.80', change: '+1.7%' },
              { symbol: 'AVAX', name: 'Avalanche', price: '$35', change: '-0.8%' },
            ].map((token, index) => (
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
    </div>
  );
};

const TokenExplorer = () => (
  <div className="p-6">
    <h2 className="text-2xl font-bold mb-4">Token Explorer</h2>
    <div className="bg-surface-DEFAULT rounded-lg p-4 border border-surface-light">
      <div className="grid grid-cols-5 gap-4 font-semibold text-gray-400 mb-4">
        <div>Token</div>
        <div>Price</div>
        <div>Volume</div>
        <div>Market Cap</div>
        <div>Change (24h)</div>
      </div>
      {/* Sample token data */}
      {['BTC', 'ETH', 'SOL', 'ARB', 'AVAX'].map((token) => (
        <div key={token} className="grid grid-cols-5 gap-4 py-3 border-t border-surface-light">
          <div className="font-medium">{token}</div>
          <div>$45,000</div>
          <div>$1.2B</div>
          <div>$800B</div>
          <div className="text-primary-500">+2.5%</div>
        </div>
      ))}
    </div>
  </div>
);

const AIAssistant = () => {
  const [messages, setMessages] = useState<{text: string, isUser: boolean}[]>([]);
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    setMessages([...messages, { text: input, isUser: true }]);
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        text: "I'm an AI assistant. How can I help you today?", 
        isUser: false 
      }]);
    }, 1000);
    setInput('');
  };

  return (
    <div className="p-6 h-[calc(100vh-4rem)]">
      <div className="bg-surface-DEFAULT rounded-lg h-full flex flex-col border border-surface-light">
        <div className="flex-1 p-4 overflow-auto">
          {messages.map((msg, idx) => (
            <div key={idx} className={`mb-4 ${msg.isUser ? 'text-right' : 'text-left'}`}>
              <div className={`inline-block p-3 rounded-lg ${
                msg.isUser ? 'bg-primary-600' : 'bg-surface-light'
              }`}>
                {msg.text}
              </div>
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="p-4 border-t border-surface-light">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-surface-light rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Type your message..."
            />
            <button
              type="submit"
              className="bg-primary-600 px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-b from-background-dark to-background-light">
        <nav className="bg-surface-dark border-b border-surface-light">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <div className="flex-shrink-0">
                <span className="text-xl font-bold text-primary-500">Hyperliquid Analytics</span>
              </div>
              <div className="flex items-center space-x-4">
                <Link to="/" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-surface-DEFAULT hover:text-primary-500 transition-colors">Dashboard</Link>
                <Link to="/token-explorer" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-surface-DEFAULT hover:text-primary-500 transition-colors">Token Explorer</Link>
                <Link to="/ai-assistant" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-surface-DEFAULT hover:text-primary-500 transition-colors">AI Assistant</Link>
              </div>
            </div>
          </div>
        </nav>

        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/token-explorer" element={<TokenExplorer />} />
            <Route path="/ai-assistant" element={<AIAssistant />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
