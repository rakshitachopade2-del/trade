export function number(value: number | null, decimals = 2): string {
  if (value === null || !Number.isFinite(value)) return '—';
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function signed(value: number | null, suffix = '%'): string {
  if (value === null || !Number.isFinite(value)) return 'Unknown';
  return `${value > 0 ? '+' : ''}${number(value)}${suffix}`;
}

export function time(value: string | null, includeDate = false): string {
  if (!value) return 'Unknown';
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return 'Unknown';
  return new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata',
    ...(includeDate ? { day: '2-digit', month: 'short', year: 'numeric' } as const : {}),
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).format(date);
}

export function dateLabel(value: string | null): string {
  if (!value) return 'Replay date';
  return new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata', day: 'numeric', month: 'long', year: 'numeric',
  }).format(new Date(value));
}

export function safeSourceUrl(value: string | null): string | null {
  if (!value) return null;
  try {
    const url = new URL(value);
    return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : null;
  } catch { return null; }
}
