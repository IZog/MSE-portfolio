import { useNavigate } from 'react-router-dom';

const POPULAR_TICKERS = [
  // Blue chips / most traded
  { symbol: 'ALK', name: 'Alkaloid AD Skopje' },
  { symbol: 'KMB', name: 'Komercijalna banka AD Skopje' },
  { symbol: 'STB', name: 'Stopanska banka AD Skopje' },
  { symbol: 'TEL', name: 'Makedonski Telekom AD Skopje' },
  { symbol: 'GRNT', name: 'Granit AD Skopje' },
  { symbol: 'MPT', name: 'Makpetrol AD Skopje' },
  { symbol: 'REPL', name: 'Replek AD Skopje' },
  { symbol: 'USJE', name: 'TITAN USJE AD Skopje' },
  // Banks
  { symbol: 'TNB', name: 'NLB Banka AD Skopje' },
  { symbol: 'TTK', name: 'TTK Banka AD Skopje' },
  { symbol: 'CKB', name: 'Centralna kooperativna banka AD Skopje' },
  { symbol: 'UNI', name: 'UNI Banka AD Skopje' },
  // Industry & other
  { symbol: 'OKTA', name: 'OKTA AD Skopje' },
  { symbol: 'VITA', name: 'Vitaminka AD Prilep' },
  { symbol: 'MTUR', name: 'Makedonijaturist AD Skopje' },
  { symbol: 'MAKP', name: 'Makpromet AD Stip' },
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
