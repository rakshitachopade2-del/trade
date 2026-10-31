import { useId } from 'react';
import type { Candidate } from '../types';
import { number, time } from '../format';
import styles from './PricePlot.module.css';

export default function PricePlot({ candidate }: { candidate: Candidate }) {
  const gradientId = useId().replaceAll(':', '');
  const bars = candidate.bars.filter((bar) => Number.isFinite(bar.close));
  if (!bars.length) return <div className={styles.empty}>No completed price bars were available at this replay time.</div>;
  const values = bars.map((bar) => bar.close);
  if (candidate.opening_range_high !== null) values.push(candidate.opening_range_high);
  if (candidate.opening_range_low !== null) values.push(candidate.opening_range_low);
  const min = Math.min(...values), max = Math.max(...values);
  const pad = Math.max((max - min) * 0.3, Math.abs(max) * 0.005, 0.2);
  const low = min - pad, high = max + pad;
  const left = 4, right = 416, top = 15, bottom = 156;
  const startTime = Date.parse(bars[0].bar_end), endTime = Date.parse(bars[bars.length - 1].bar_end);
  const x = (index: number) => startTime === endTime ? (left + right) / 2 : left + (Date.parse(bars[index].bar_end) - startTime) * (right - left) / (endTime - startTime);
  const y = (value: number) => bottom - (value - low) / (high - low) * (bottom - top);
  const segments: number[][] = [];
  bars.forEach((bar, index) => {
    if (index === 0 || Date.parse(bar.bar_end) - Date.parse(bars[index - 1].bar_end) > 300_000) segments.push([]);
    segments[segments.length - 1].push(index);
  });
  const lines = segments.map((indices) => indices.map((index, segmentIndex) => `${segmentIndex ? 'L' : 'M'} ${x(index)} ${y(bars[index].close)}`).join(' '));
  const areas = segments.map((indices, segmentIndex) => `${lines[segmentIndex]} L ${x(indices[indices.length - 1])} ${bottom} L ${x(indices[0])} ${bottom} Z`);
  return <div className={styles.wrapper}>
    <div className={styles.heading}><span>Synthetic close price</span><span className={styles.legend}><i aria-hidden="true" />Opening range high</span></div>
    <svg className={styles.chart} viewBox="0 0 470 192" role="img" aria-label={`Completed synthetic close prices for ${candidate.symbol}. Latest close ${number(bars[bars.length - 1].close)} at ${time(bars[bars.length - 1].bar_end)} IST.`}>
      <defs><linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#7ed9b3" stopOpacity=".18" /><stop offset="100%" stopColor="#7ed9b3" stopOpacity="0" /></linearGradient></defs>
      {[0, 0.5, 1].map((fraction) => <g key={fraction}>
        <line x1={left} x2={right} y1={top + (bottom - top) * fraction} y2={top + (bottom - top) * fraction} stroke="#26303e" strokeDasharray="2 5" />
        <text x="465" y={top + (bottom - top) * fraction + 3} textAnchor="end" className={styles.axis}>{number(high - (high - low) * fraction)}</text>
      </g>)}
      {candidate.opening_range_high !== null && <line x1={left} x2={right} y1={y(candidate.opening_range_high)} y2={y(candidate.opening_range_high)} stroke="#778a93" strokeDasharray="5 4" />}
      {areas.map((area, index) => <path key={`area-${index}`} d={area} fill={`url(#${gradientId})`} />)}
      {lines.map((line, index) => <path key={`line-${index}`} d={line} fill="none" stroke="#8de0bd" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />)}
      {bars.map((bar, index) => <circle key={bar.bar_end} cx={x(index)} cy={y(bar.close)} r="3" fill="#8de0bd" stroke="#12212a" strokeWidth="2"><title>{time(bar.bar_end)} IST: {number(bar.close)}</title></circle>)}
      <text x={left} y="185" className={styles.axis}>{time(bars[0].bar_end)}</text>
      {bars.length > 1 && <text x={right} y="185" textAnchor="end" className={styles.axis}>{time(bars[bars.length - 1].bar_end)} IST</text>}
    </svg>
    <p>Completed bars only. No forecast or option-price estimate.</p>
  </div>;
}
