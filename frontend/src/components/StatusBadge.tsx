import type { ScreenState } from '../types';
import styles from './StatusBadge.module.css';

export default function StatusBadge({ state }: { state: ScreenState }) {
  const labels = { qualified: 'Qualified', watching: 'Watching', blocked: 'Blocked' };
  return <span className={`${styles.badge} ${styles[state]}`}><span className={styles.dot} aria-hidden="true" />{labels[state]}</span>;
}
