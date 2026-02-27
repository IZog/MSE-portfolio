import { Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  return (
    <div className="min-h-screen bg-[#f8fafc]">
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/:ticker" element={<DashboardPage />} />
      </Routes>
    </div>
  );
}
