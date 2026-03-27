import { useNavigate } from 'react-router-dom';
import { getCachedVerdict } from '../../hooks/useResearch';

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

function verdictBorderColor(rating: string | null): string {
  if (!rating) return 'border-gray-200';
  const r = rating.toLowerCase();
  if (r.includes('strong buy') || r.includes('buy')) return 'border-l-green-500 border-l-4 border-gray-200';
  if (r.includes('hold')) return 'border-l-amber-500 border-l-4 border-gray-200';
  if (r.includes('avoid') || r.includes('sell')) return 'border-l-red-500 border-l-4 border-gray-200';
  return 'border-gray-200';
}

function verdictLabel(rating: string | null): { text: string; color: string } | null {
  if (!rating) return null;
  const r = rating.toLowerCase();
  if (r.includes('strong buy')) return { text: 'Strong Buy', color: 'text-green-700 bg-green-50' };
  if (r.includes('buy')) return { text: 'Buy', color: 'text-green-600 bg-green-50' };
  if (r.includes('hold')) return { text: 'Hold', color: 'text-amber-600 bg-amber-50' };
  if (r.includes('avoid')) return { text: 'Avoid', color: 'text-red-600 bg-red-50' };
  return null;
}

export default function TickerList() {
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
      {POPULAR_TICKERS.map((t) => {
        const rating = getCachedVerdict(t.symbol);
        const borderClass = verdictBorderColor(rating);
        const label = verdictLabel(rating);

        return (
          <button
            key={t.symbol}
            onClick={() => navigate(`/${t.symbol}`)}
            className={`bg-white border ${borderClass} rounded-lg p-4 text-left hover:border-blue-400 hover:shadow-md transition-all cursor-pointer group`}
          >
            <div className="flex items-center justify-between">
              <div className="text-base font-bold text-[#0f172a] group-hover:text-blue-600 transition-colors">
                {t.symbol}
              </div>
              {label && (
                <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${label.color}`}>
                  {label.text}
                </span>
              )}
            </div>
            <div className="text-xs text-gray-500 mt-1 truncate">{t.name}</div>
          </button>
        );
      })}
    </div>
  );
}
