import { useEffect, useState } from 'react';
import { getCoverage, gapMessages, type CoverageResponse } from '../coverage';
import { time } from '../format';
import styles from './DataCoverage.module.css';

const words = (value: string) => value.replaceAll('_', ' ');

export default function DataCoverage() {
  const [attempt, setAttempt] = useState(0);
  const [result, setResult] = useState<CoverageResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setLoading(true); setResult(null); setError(null);
    getCoverage(controller.signal).then(value => { if (active) setResult(value); })
      .catch((cause: unknown) => { if (active) setError(cause instanceof Error ? cause.message : 'Unable to reach the coverage API.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; controller.abort(); };
  }, [attempt]);
  const report = result?.state === 'report' ? result.report : null;
  const status = loading ? 'Loading coverage' : error ? 'Backend / response error' : result?.state === 'not_imported' ? 'Not imported'
    : result?.state === 'invalid_report' ? 'Invalid report' : report?.status === 'coverage_complete' ? 'Coverage complete' : report?.status === 'invalid' ? 'Invalid inputs' : 'Partial';
  return <section id="data-coverage" className={styles.panel} aria-labelledby="coverage-title">
    <header className={styles.header}><div><p className="eyebrow">OFFLINE SAMPLE INTAKE</p><h2 id="coverage-title">Data coverage</h2></div><span className={styles.badge} aria-live="polite">{status}</span></header>
    <p className={styles.separate}>Separate from research calculations. Imported data does not drive the synthetic rankings above.</p>
    {report && <p className={styles.nature}>{report.dataset_nature === 'synthetic_test' ? 'Synthetic test — not a real-data trial' : report.dataset_nature === 'user_import' ? 'User import — source claims require manual review' : 'Dataset nature unknown'}</p>}
    <details>
      <summary>View coverage details</summary>
      <button type="button" className={styles.refresh} disabled={loading} onClick={() => { setResult(null); setError(null); setLoading(true); setAttempt(a => a + 1); }}>Refresh coverage</button>
      {error && <p role="alert" className={styles.error}>{error}</p>}
      {result?.state === 'not_imported' && <p>No local import report is configured. Run the offline intake command documented in Milestone 2A, then configure its report on the backend.</p>}
      {result?.state === 'invalid_report' && <p className={styles.error}>The configured report is missing, unreadable or incompatible. Correct the backend report configuration or generate a new report; no coverage success is inferred.</p>}
      {report && <>
        <dl className={styles.metadata}>
          <div><dt>Dataset / session</dt><dd>{report.dataset_id ?? 'Unknown'} · {report.session_date ?? 'Unknown'}</dd></div>
          <div><dt>Selected sample</dt><dd>{report.stock_count} equities · benchmark {report.benchmark ?? 'Unknown'} (context only)</dd></div>
          <div><dt>Source / imported</dt><dd>{report.source_label ?? 'Unknown'} · {time(report.imported_at, true)} IST</dd></div>
          <div><dt>Schema / source review</dt><dd>{report.schema_valid ? 'Structurally readable' : 'Invalid'} · {words(report.source_review)} (manual, not independent verification)</dd></div>
          <div><dt>Session / adjustment</dt><dd>{words(report.session_review)} · {report.price_adjustment}</dd></div>
          <div><dt>Local retention / source date</dt><dd>{report.retention} · {report.source_dates_known ? 'Supplied' : 'Unknown'}</dd></div>
        </dl>
        {report.series.length > 0 && <div className={styles.tableWrap}><table><caption>Five-minute sample coverage · 09:15–10:00 IST</caption><thead><tr><th scope="col">Instrument</th><th scope="col">Present / expected</th><th scope="col">Missing interval starts</th></tr></thead><tbody>{report.series.map(s => <tr key={s.symbol}><th scope="row">{s.symbol}<small>{words(s.instrument_type)}</small></th><td>{s.present} / {s.expected}</td><td>{s.missing.join(', ') || 'None'}{s.missing_volume > 0 && <small>Missing equity volume: {s.missing_volume}</small>}</td></tr>)}</tbody></table></div>}
        <p>Duplicate candles: {report.duplicate_rows} · Invalid rows: {report.invalid_rows} · Outside sample: {report.outside_window}. Outside rows do not count toward coverage.</p>
        <h3>Options membership evidence</h3>
        <p>Universe list: {report.universe_count} symbols · {report.list_duplicates} duplicates removed · {report.unmapped_symbols} mappings to review.</p>
        <ul>{report.membership.map(m => <li key={m.symbol}>{m.symbol}: {words(m.level)} · dated review {m.dated_review ? 'manually confirmed' : 'pending'}</li>)}</ul>
        <p>A user list is an assertion, not verified historical eligibility. Absence is not ineligibility. Listing, F&amp;O ban status and contract liquidity are separate.</p>
        <h3>Quarterly filing</h3>
        <p>{report.filing.status === 'not_imported' ? 'Not imported. Financials remain unknown.' : `${report.filing.symbol}: publication ${words(report.filing.publication_precision)} · transcription ${report.filing.reconciliation} · ${report.filing.figures_present} figures supplied. Other companies’ financials remain unknown.`}</p>
        {report.filing.status === 'imported' && report.filing.figures_present === 0 && <p>No optional financial figures supplied; financial values remain unknown.</p>}
        <p>Manual transcription is not independently verified. Date-only publication cannot pass exact timestamp coverage.</p>
        {report.gaps.length > 0 ? <><h3>Remaining gaps</h3><ul>{report.gaps.map(g => <li key={g}>{gapMessages[g]}</li>)}</ul></> : <p>Declared sample coverage and required manual reviews are complete. This does not establish historical feed availability, market accuracy or profitable trading.</p>}
      </>}
    </details>
  </section>;
}
