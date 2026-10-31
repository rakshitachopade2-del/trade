import type { Candidate } from '../types';
import { safeSourceUrl, time } from '../format';
import styles from './EvidencePanel.module.css';

export default function EvidencePanel({ candidate, asOf }: { candidate: Candidate; asOf: string }) {
  return <section id="evidence" className={styles.panel} aria-labelledby="evidence-title">
    <header className={styles.header}><div><p className="eyebrow">POINT-IN-TIME CONTEXT</p><h2 id="evidence-title">Fundamental & event evidence</h2></div><span className={`${styles.status} ${candidate.fundamentals_status === 'unknown' ? styles.unknown : ''}`}>Financials: {candidate.fundamentals_status === 'available' ? 'available' : 'unknown'}</span></header>
    <p className={styles.cutoff}>Available to the system by {time(asOf, true)} IST.</p>
    {candidate.fundamentals_status === 'unknown' && candidate.evidence.length > 0 && <p className={styles.unknownNote}>Financial information remains unknown at this time. The available event evidence is shown below.</p>}
    {!candidate.evidence.length
      ? <div className={styles.empty}><span aria-hidden="true">—</span><div><strong>No evidence available at this time</strong><p>Missing financial information stays unknown. It does not become a positive or negative signal.</p></div></div>
      : <div className={styles.items}>{candidate.evidence.map((item) => {
        const sourceUrl = safeSourceUrl(item.source_url);
        return <article key={item.id} className={styles.item}>
          <div className={styles.itemTop}><span>{item.kind.replaceAll('_', ' ')}</span><span>{item.period}</span></div>
          <h3>{item.title}</h3><p className={styles.summary}>{item.summary}</p>
          <dl className={styles.metadata}><div><dt>Source</dt><dd>{sourceUrl ? <a href={sourceUrl} target="_blank" rel="noreferrer">{item.source} ↗</a> : item.source}</dd></div><div><dt>Published</dt><dd>{time(item.published_at, true)} IST</dd></div><div><dt>Available</dt><dd>{time(item.available_at, true)} IST</dd></div></dl>
        </article>;
      })}</div>}
    <footer>Evidence is shown separately and does not affect this price-screen ranking. Good business results do not establish downside protection for a call option.</footer>
  </section>;
}
