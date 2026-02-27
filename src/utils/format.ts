export function formatNumber(n: number | null | undefined): string {
  if (n == null) return 'N/A';
  return n.toLocaleString('en-US');
}

export function formatMKD(n: number | null | undefined): string {
  if (n == null) return 'N/A';
  return `${n.toLocaleString('en-US')} MKD`;
}

export function formatMillionsMKD(n: number | null | undefined): string {
  if (n == null) return 'N/A';
  const millions = n / 1_000_000;
  if (Math.abs(millions) >= 1) {
    return `${millions.toLocaleString('en-US', { maximumFractionDigits: 1 })}M MKD`;
  }
  return formatMKD(n);
}

export function formatPercent(n: number | null | undefined): string {
  if (n == null) return 'N/A';
  return `${n.toFixed(2)}%`;
}

export function formatRatio(n: number | null | undefined): string {
  if (n == null) return 'N/A';
  return n.toFixed(2);
}
