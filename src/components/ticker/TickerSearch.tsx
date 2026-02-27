import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTickers } from '../../hooks/useTickers';

export default function TickerSearch() {
  const { tickers } = useTickers();
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const wrapperRef = useRef<HTMLDivElement>(null);

  const filtered = query.length > 0
    ? tickers.filter(
        (t) =>
          t.symbol.toLowerCase().includes(query.toLowerCase()) ||
          (t.name?.toLowerCase().includes(query.toLowerCase()) ?? false)
      ).slice(0, 8)
    : [];

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function handleSelect(symbol: string) {
    setQuery('');
    setOpen(false);
    navigate(`/${symbol}`);
  }

  return (
    <div ref={wrapperRef} className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => query.length > 0 && setOpen(true)}
        placeholder="Search ticker or company..."
        className="w-full px-3 py-1.5 text-sm bg-white/10 border border-white/20 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      {open && filtered.length > 0 && (
        <ul className="absolute z-50 mt-1 w-full bg-white rounded-md shadow-lg border border-gray-200 max-h-64 overflow-y-auto">
          {filtered.map((t) => (
            <li key={t.symbol}>
              <button
                onClick={() => handleSelect(t.symbol)}
                className="w-full px-3 py-2 text-left text-sm hover:bg-blue-50 flex justify-between items-center cursor-pointer"
              >
                <span className="font-medium text-gray-900">{t.symbol}</span>
                <span className="text-gray-500 text-xs truncate ml-2">{t.name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
