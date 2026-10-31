import type { Candidate } from '../types';
import { signed, number, time } from '../format';
import StatusBadge from './StatusBadge';
import styles from './CandidateList.module.css';

interface Props { candidates: Candidate[]; selected: string | null; onSelect: (symbol: string) => void; }

export default function CandidateList({ candidates, selected, onSelect }: Props) {
  return <section id="candidates" className={styles.panel} aria-labelledby="candidates-title">
    <header className={styles.header}><div><p className="eyebrow">THE UNIVERSE</p><h2 id="candidates-title">Underlying screens</h2></div><span className={styles.count}>{candidates.length} stocks</span></header>
    <p className={styles.intro}>Qualified screens rank by observed relative return, not expected profit. Every exclusion remains inspectable.</p>
    <div className={styles.columns} aria-hidden="true"><span>Stock / screen</span><span>Relative return</span></div>
    <div className={styles.list}>
      {candidates.map((candidate) => <button
        type="button" key={candidate.symbol}
        onClick={() => onSelect(candidate.symbol)}
        aria-pressed={selected === candidate.symbol}
        className={`${styles.row} ${selected === candidate.symbol ? styles.selected : ''}`}
      >
        <span className={styles.rank} aria-label={candidate.rank ? `Rank ${candidate.rank}` : 'Unranked'}>{candidate.rank ? candidate.rank.toString().padStart(2, '0') : '—'}</span>
        <span className={styles.identity}>
          <strong>{candidate.symbol.replace('DEMO_', '')}<span className={styles.symbolPrefix}>DEMO</span></strong>
          <span className={styles.name}>{candidate.name.replace(' (fictional)', '')}</span>
          <span className={styles.meta}><StatusBadge state={candidate.state} /><span>{candidate.sector}</span></span>
        </span>
        <span className={styles.performance}>
          <strong className={candidate.relative_return_pct !== null && candidate.relative_return_pct > 0 ? styles.positive : ''}>{signed(candidate.relative_return_pct, ' pp')}</strong>
          <span>Close {number(candidate.last_price)}</span>
          <span className={styles.time}>{time(candidate.last_bar_end)} IST</span>
        </span>
      </button>)}
    </div>
    <footer className={styles.footer}><span aria-hidden="true">ⓘ</span><span>Relative return = stock return minus benchmark return. It is not a predicted return.</span></footer>
  </section>;
}
