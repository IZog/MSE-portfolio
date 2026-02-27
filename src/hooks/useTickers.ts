import { useState, useEffect } from 'react';
import type { TickerInfo } from '../types';
import { fetchTickers } from '../api/client';

export function useTickers() {
  const [tickers, setTickers] = useState<TickerInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchTickers()
      .then((data) => {
        if (!cancelled) setTickers(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { tickers, loading, error };
}
