export interface CompanyProfile {
  ticker: string;
  name: string | null;
  description: string | null;
  address: string | null;
  sector: string | null;
}

export interface PriceData {
  current_price: number | null;
  price_change_pct: number | null;
  high_52w: number | null;
  low_52w: number | null;
  total_shares: number | null;
  market_cap: number | null;
}

export interface PricePoint {
  date: string;
  last_trade_price: number | null;
  max_price: number | null;
  min_price: number | null;
  avg_price: number | null;
  pct_change: number | null;
  volume: number | null;
  turnover_best: number | null;
  total_turnover: number | null;
}

export interface FinancialData {
  year: number;
  revenue: number | null;
  operating_profit: number | null;
  net_profit: number | null;
  equity: number | null;
  total_assets: number | null;
  total_liabilities: number | null;
}

export interface FinancialRatios {
  pe_ratio: number | null;
  eps: number | null;
  roa: number | null;
  roe: number | null;
  book_value_per_share: number | null;
  dividend_per_share: number | null;
  dividend_yield: number | null;
  market_cap: number | null;
}

export interface ValuationMetrics {
  pe_ratio: number | null;
  pe_assessment: string | null;
  pb_ratio: number | null;
  pb_assessment: string | null;
  dividend_yield: number | null;
  dividend_assessment: string | null;
  earnings_yield: number | null;
  overall_assessment: string | null;
  score: number;
}

export interface TechnicalAnalysis {
  trend: string | null;
  sma_short: number | null;
  sma_long: number | null;
  support: number | null;
  resistance: number | null;
  momentum: string | null;
  momentum_pct: number | null;
  volume_trend: string | null;
  avg_volume_10d: number | null;
  avg_volume_30d: number | null;
  week52_position: number | null;
  score: number;
}

export interface MacroContext {
  mbi10_value: number | null;
  mbi10_change_pct: number | null;
  gdp_growth: number | null;
  inflation: number | null;
  policy_rate: number | null;
  last_updated: string | null;
}

export interface RiskAssessment {
  liquidity_risk: string | null;
  volatility_risk: string | null;
  financial_risk: string | null;
  market_risk: string;
  overall_risk: string | null;
  factors: string[];
  score: number;
}

export interface Verdict {
  rating: string;
  total_score: number;
  valuation_score: number;
  growth_score: number;
  technical_score: number;
  risk_score: number;
  summary: string;
  key_positives: string[];
  key_negatives: string[];
}

export interface ResearchReport {
  ticker: string;
  company: CompanyProfile;
  price: PriceData;
  price_history: PricePoint[];
  financials: FinancialData[];
  ratios: FinancialRatios;
  valuation: ValuationMetrics;
  technical: TechnicalAnalysis;
  macro: MacroContext;
  risk: RiskAssessment;
  verdict: Verdict;
  generated_at: string;
}

export interface TickerInfo {
  symbol: string;
  name: string | null;
  isin: string | null;
  market_segment: string | null;
}
