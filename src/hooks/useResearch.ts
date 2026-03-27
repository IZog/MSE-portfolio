import { useState, useCallback } from 'react';
import type { ResearchReport } from '../types';
import { fetchResearch } from '../api/client';

const CACHE_PREFIX = 'mse_research_';
const CACHE_TTL = 1000 * 60 * 30; // 30 minutes

function getCached(ticker: string): ResearchReport | null {
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + ticker);
    if (!raw) return null;
    const { data, timestamp } = JSON.parse(raw);
    if (Date.now() - timestamp > CACHE_TTL) {
      localStorage.removeItem(CACHE_PREFIX + ticker);
      return null;
    }
    return data as ResearchReport;
  } catch {
    return null;
  }
}

function setCache(ticker: string, data: ResearchReport) {
  try {
    localStorage.setItem(
      CACHE_PREFIX + ticker,
      JSON.stringify({ data, timestamp: Date.now() })
    );
  } catch {
    // localStorage full or unavailable
  }
}

/** Read the cached verdict rating for a ticker without fetching. */
export function getCachedVerdict(ticker: string): string | null {
  const report = getCached(ticker);
  return report?.verdict?.rating ?? null;
}

export function useResearch() {
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (ticker: string, forceRefresh = false) => {
    setError(null);

    if (!forceRefresh) {
      const cached = getCached(ticker);
      if (cached) {
        setReport(cached);
        return;
      }
    }

    setLoading(true);
    try {
      const data = await fetchResearch(ticker);
      setCache(ticker, data);
      setReport(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  return { report, loading, error, load };
}
