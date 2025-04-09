export default function TokenExplorer() {
  return (
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
} 