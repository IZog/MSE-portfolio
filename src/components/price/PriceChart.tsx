import { useEffect, useRef } from 'react';
import {
  createChart,
  type IChartApi,
  ColorType,
  type CandlestickData,
  type LineData,
  type HistogramData,
  type Time,
  CandlestickSeries,
  LineSeries,
  HistogramSeries,
} from 'lightweight-charts';
import type { PricePoint, TechnicalAnalysis } from '../../types';
import Card from '../common/Card';

interface Props {
  history: PricePoint[];
  technical?: TechnicalAnalysis;
}

/** Normalise any date string to YYYY-MM-DD for lightweight-charts. */
function toTime(dateStr: string): Time {
  const d = new Date(dateStr);
  if (!isNaN(d.getTime())) {
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}` as Time;
  }
  return dateStr as Time;
}

function computeSMA(prices: number[], period: number): (number | null)[] {
  const result: (number | null)[] = [];
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      let sum = 0;
      for (let j = i - period + 1; j <= i; j++) sum += prices[j];
      result.push(sum / period);
    }
  }
  return result;
}

export default function PriceChart({ history, technical }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current || history.length === 0) return;

    // Clean up previous chart instance.
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#64748b',
        fontSize: 11,
      },
      grid: {
        vertLines: { color: '#f1f5f9' },
        horzLines: { color: '#f1f5f9' },
      },
      crosshair: { mode: 0 },
      rightPriceScale: { borderColor: '#e2e8f0' },
      timeScale: {
        borderColor: '#e2e8f0',
        timeVisible: false,
      },
      height: 350,
    });
    chartRef.current = chart;

    // --- Candlestick series ---
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderDownColor: '#ef4444',
      borderUpColor: '#22c55e',
      wickDownColor: '#ef4444',
      wickUpColor: '#22c55e',
    });

    // Build OHLC data. Use previous close as open when avg_price is unavailable.
    const candleData: CandlestickData[] = [];
    let prevClose: number | null = null;

    for (const p of history) {
      const close = p.last_trade_price;
      if (close == null) continue;

      const open = p.avg_price ?? prevClose ?? close;
      const high = p.max_price ?? Math.max(open, close);
      const low = p.min_price ?? Math.min(open, close);

      candleData.push({
        time: toTime(p.date),
        open,
        high,
        low,
        close,
      });
      prevClose = close;
    }

    candleSeries.setData(candleData);

    // --- SMA overlays ---
    const closePrices = candleData.map((c) => c.close);
    const times = candleData.map((c) => c.time);

    const sma20Values = computeSMA(closePrices, 20);
    const sma50Values = computeSMA(closePrices, 50);

    const sma20Data: LineData[] = [];
    const sma50Data: LineData[] = [];

    for (let i = 0; i < times.length; i++) {
      if (sma20Values[i] != null) {
        sma20Data.push({ time: times[i], value: sma20Values[i]! });
      }
      if (sma50Values[i] != null) {
        sma50Data.push({ time: times[i], value: sma50Values[i]! });
      }
    }

    if (sma20Data.length > 0) {
      const sma20Series = chart.addSeries(LineSeries, {
        color: '#f59e0b',
        lineWidth: 1,
        priceLineVisible: false,
        lastValueVisible: false,
        crosshairMarkerVisible: false,
        title: 'SMA 20',
      });
      sma20Series.setData(sma20Data);
    }

    if (sma50Data.length > 0) {
      const sma50Series = chart.addSeries(LineSeries, {
        color: '#8b5cf6',
        lineWidth: 1,
        priceLineVisible: false,
        lastValueVisible: false,
        crosshairMarkerVisible: false,
        title: 'SMA 50',
      });
      sma50Series.setData(sma50Data);
    }

    // --- Support / Resistance price lines ---
    if (technical?.support != null) {
      candleSeries.createPriceLine({
        price: technical.support,
        color: '#22c55e',
        lineWidth: 1,
        lineStyle: 2, // dashed
        axisLabelVisible: true,
        title: 'Support',
      });
    }
    if (technical?.resistance != null) {
      candleSeries.createPriceLine({
        price: technical.resistance,
        color: '#ef4444',
        lineWidth: 1,
        lineStyle: 2,
        axisLabelVisible: true,
        title: 'Resistance',
      });
    }

    // --- Volume histogram ---
    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    });

    chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    const volumeData: HistogramData[] = [];
    for (let i = 0; i < history.length; i++) {
      const p = history[i];
      if (p.volume == null || p.last_trade_price == null) continue;
      const prevPrice = i > 0 ? history[i - 1].last_trade_price : null;
      const isUp = prevPrice != null ? p.last_trade_price >= prevPrice : true;

      volumeData.push({
        time: toTime(p.date),
        value: p.volume,
        color: isUp ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)',
      });
    }
    volumeSeries.setData(volumeData);

    // Fit content.
    chart.timeScale().fitContent();

    // --- Resize observer ---
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width } = entry.contentRect;
        chart.applyOptions({ width });
      }
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [history, technical]);

  return (
    <Card title="Price Chart">
      <div className="flex items-center gap-4 mb-2 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-0.5 bg-amber-500 rounded" /> SMA 20
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-0.5 bg-violet-500 rounded" /> SMA 50
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-0.5 bg-green-500 rounded" /> Support
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-0.5 bg-red-500 rounded" /> Resistance
        </span>
      </div>
      <div ref={containerRef} />
    </Card>
  );
}
