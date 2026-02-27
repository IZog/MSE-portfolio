import type { TickerInfo, ResearchReport } from '../types';

const BASE = '';

export async function fetchTickers(): Promise<TickerInfo[]> {
  const res = await fetch(`${BASE}/api/tickers`);
  if (!res.ok) throw new Error(`Failed to fetch tickers: ${res.status}`);
  return res.json();
}

export async function fetchResearch(ticker: string): Promise<ResearchReport> {
  const res = await fetch(`${BASE}/api/research/${ticker}`);
  if (!res.ok) throw new Error(`Failed to fetch research for ${ticker}: ${res.status}`);
  return res.json();
}
