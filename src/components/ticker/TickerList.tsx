import { useNavigate } from 'react-router-dom';

const POPULAR_TICKERS = [
  { symbol: 'ALK', name: 'Alkaloid AD Skopje' },
  { symbol: 'KMB', name: 'Komercijalna Banka AD Skopje' },
  { symbol: 'STB', name: 'Stopanska Banka AD Skopje' },
  { symbol: 'GRNT', name: 'Granit AD Skopje' },
  { symbol: 'MPT', name: 'Makpetrol AD Skopje' },
  { symbol: 'TNB', name: 'Tutunski Kombinat AD Prilep' },
  { symbol: 'TTK', name: 'Teteks AD Tetovo' },
  { symbol: 'REPL', name: 'Replek AD Skopje' },
];

export default function TickerList() {
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
      {POPULAR_TICKERS.map((t) => (
        <button
          key={t.symbol}
          onClick={() => navigate(`/${t.symbol}`)}
          className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-blue-400 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="text-base font-bold text-[#0f172a] group-hover:text-blue-600 transition-colors">
            {t.symbol}
          </div>
          <div className="text-xs text-gray-500 mt-1 truncate">{t.name}</div>
        </button>
      ))}
    </div>
  );
}
