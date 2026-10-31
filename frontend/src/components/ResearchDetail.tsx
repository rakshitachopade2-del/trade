import type { Candidate } from '../types';
import { number, signed, time } from '../format';
import StatusBadge from './StatusBadge';
import PricePlot from './PricePlot';
import styles from './ResearchDetail.module.css';

export default function ResearchDetail({ candidate }: { candidate: Candidate }) {
  return <section className={styles.panel} aria-labelledby="detail-title">
    <header className={styles.header}><div><p className="eyebrow">SELECTED UNDERLYING</p><h2 id="detail-title">{candidate.symbol.replace('DEMO_', '')}<span>{candidate.sector}</span></h2><p className={styles.fullName}>{candidate.name}</p></div><StatusBadge state={candidate.state} /></header>
    <div className={styles.metrics}>
      <div><span>Last completed close</span><strong>{number(candidate.last_price)}</strong><small>{time(candidate.last_bar_end)} IST</small></div>
      <div><span>Stock return</span><strong>{signed(candidate.return_pct)}</strong><small>Benchmark {signed(candidate.benchmark_return_pct)}</small></div>
      <div><span>Opening range</span><strong className={styles.range}>{number(candidate.opening_range_low)} <span>–</span> {number(candidate.opening_range_high)}</strong><small>First 15 minutes</small></div>
    </div>
    <PricePlot candidate={candidate} />
    <div className={styles.reasonArea}>
      <div className={styles.sectionTitle}><h3>Why this screen</h3><span>Screening rules</span></div>
      <ul className={styles.reasons}>{candidate.reasons.map((reason, index) => <li key={`${candidate.reason_codes[index] ?? 'reason'}-${index}`}><span className={styles.bullet} aria-hidden="true" /><div>{reason}</div></li>)}</ul>
      <div className={styles.eligibility}><span>Listed-options eligibility</span><strong>{candidate.eligibility}</strong></div>
    </div>
    <div className={styles.contract}><span className={styles.lock} aria-hidden="true"><svg viewBox="0 0 20 20"><rect x="5" y="8" width="10" height="8" rx="2" /><path d="M7 8V6a3 3 0 0 1 6 0v2" /></svg></span><div><strong>Contract not evaluated</strong><p>A qualified underlying screen is not an actionable trade. Option liquidity, spreads, expiry and risk have not been checked.</p></div></div>
  </section>;
}
