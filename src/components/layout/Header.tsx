import { useNavigate } from 'react-router-dom';
import TickerSearch from '../ticker/TickerSearch';

export default function Header() {
  const navigate = useNavigate();

  return (
    <header className="bg-[#0f172a] text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
        <button
          onClick={() => navigate('/')}
          className="text-lg font-bold tracking-tight whitespace-nowrap cursor-pointer hover:opacity-80 transition-opacity"
        >
          MSE Research
        </button>
        <div className="w-full max-w-sm">
          <TickerSearch />
        </div>
      </div>
    </header>
  );
}
