import type { Replay } from '../types';
import styles from './SummaryCards.module.css';

export default function SummaryCards({ summary }: { summary: Replay['summary'] }) {
  const cards = [
    { label: 'Research universe', value: summary.total, detail: 'Fictional underlyings', tone: 'neutral' },
    { label: 'Screen qualified', value: summary.qualified, detail: 'Underlying conditions met', tone: 'green' },
    { label: 'Still watching', value: summary.watching, detail: 'Waiting for confirmation', tone: 'amber' },
    { label: 'Screen blocked', value: summary.blocked, detail: 'Exclusions stay visible', tone: 'neutral' },
  ];
  return <div className={styles.grid} aria-label="Replay summary">
    {cards.map((card) => <section key={card.label} className={styles.card}>
      <div className={styles.label}><span className={`${styles.dot} ${styles[card.tone]}`} />{card.label}</div>
      <div className={styles.value}>{card.value.toString().padStart(2, '0')}</div>
      <p>{card.detail}</p>
    </section>)}
  </div>;
}
