import { useEffect, useRef, useState } from 'react';
import { getDemo, getReplay } from './api';
import type { DemoConfig, Replay } from './types';
import { dateLabel, time } from './format';
import SummaryCards from './components/SummaryCards';
import CandidateList from './components/CandidateList';
import ResearchDetail from './components/ResearchDetail';
import EvidencePanel from './components/EvidencePanel';
import styles from './App.module.css';

const errorMessage = (error: unknown) => error instanceof Error ? error.message : 'The research API could not be reached. Check the local server and retry.';

function Mark() {
  return <svg viewBox="0 0 32 32" aria-hidden="true"><path d="M5 9h22M16 9v18M6 20l6-5 7 4 8-10" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

export default function App() {
  const [demo, setDemo] = useState<DemoConfig | null>(null);
  const [asOf, setAsOf] = useState('');
  const [replay, setReplay] = useState<Replay | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [configError, setConfigError] = useState<string | null>(null);
  const [replayError, setReplayError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [configAttempt, setConfigAttempt] = useState(0);
  const [replayAttempt, setReplayAttempt] = useState(0);
  const replayRequestId = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setConfigError(null);
    setLoading(true);
    getDemo(controller.signal).then((result) => {
      if (!active) return;
      setDemo(result);
      setAsOf(result.default_as_of);
    }).catch((error: unknown) => {
      if (!active || controller.signal.aborted) return;
      setConfigError(errorMessage(error));
      setLoading(false);
    });
    return () => { active = false; controller.abort(); };
  }, [configAttempt]);

  useEffect(() => {
    if (!asOf) return;
    const requestId = ++replayRequestId.current;
    const controller = new AbortController();
    let active = true;
    setReplay(null);
    setReplayError(null);
    setLoading(true);
    getReplay(asOf, controller.signal).then((result) => {
      if (!active || requestId !== replayRequestId.current) return;
      setReplay(result);
      setSelected((current) => result.candidates.some((item) => item.symbol === current) ? current : result.candidates[0]?.symbol ?? null);
      setLoading(false);
    }).catch((error: unknown) => {
      if (!active || controller.signal.aborted || requestId !== replayRequestId.current) return;
      setReplayError(errorMessage(error));
      setLoading(false);
    });
    return () => { active = false; controller.abort(); };
  }, [asOf, replayAttempt]);

  function changeReplay(value: string) {
    if (value === asOf) return;
    replayRequestId.current += 1;
    setReplay(null);
    setReplayError(null);
    setLoading(true);
    setAsOf(value);
  }

  function refreshReplay() {
    replayRequestId.current += 1;
    setReplay(null);
    setReplayError(null);
    setLoading(true);
    setReplayAttempt((attempt) => attempt + 1);
  }

  const currentReplay = replay && Date.parse(replay.as_of) === Date.parse(asOf) ? replay : null;
  const candidate = currentReplay?.candidates.find((item) => item.symbol === selected) ?? null;
  const error = configError ?? replayError;

  return <div className={styles.layout}>
    <a href="#main" className={styles.skip}>Skip to research</a>
    <aside className={styles.sidebar}>
      <a href="#overview" className={styles.brand} aria-label="Trade research desk"><span className={styles.logo}><Mark /></span><span>trade<span className={styles.brandDot}>.</span><small>RESEARCH DESK</small></span></a>
      <div className={styles.workspace}><span className={styles.workspaceIcon}>R</span><div>Private workspace<small>Local research prototype</small></div><span className={styles.workspaceDot} aria-hidden="true" /></div>
      <p className={styles.navLabel}>WORKSPACE</p>
      <nav aria-label="Research sections" className={styles.nav}>
        <a href="#overview" className={styles.activeNav}><svg viewBox="0 0 20 20" aria-hidden="true"><rect x="3" y="3" width="5" height="5" rx="1" /><rect x="12" y="3" width="5" height="5" rx="1" /><rect x="3" y="12" width="5" height="5" rx="1" /><rect x="12" y="12" width="5" height="5" rx="1" /></svg>Research desk<span>01</span></a>
        <a href="#candidates"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h9" /></svg>Underlying screens</a>
        <a href="#evidence"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 2h7l4 4v12H5zM11 2v5h5M8 11h5M8 14h5" /></svg>Evidence trail</a>
      </nav>
      <div className={styles.sidebarBottom}><div className={styles.readonly}><span aria-hidden="true">◇</span>Observation, with context.</div><p>Research stays here.<br />Every trading decision stays with you.</p><span className={styles.local}><i />LOCAL · READ ONLY</span></div>
    </aside>
    <div className={styles.mainWrap}>
      <header className={styles.topbar}><span>Workspace <span className={styles.slash}>/</span> <strong>Research desk</strong></span><div className={styles.topbarRight}><span className={styles.demoBadge}><i />Synthetic demo</span><span className={styles.avatar} aria-label="Private workspace">R</span></div></header>
      <main id="main" className={styles.main}>
        <div id="overview" className={styles.pageHeading}><div><p className="eyebrow">OBSERVE. VERIFY. DECIDE.</p><h1>A clearer view of the setup.</h1><p className={styles.subtitle}>Inspect the underlying, understand the evidence, keep the decision yours.</p></div><div className={styles.date}>{dateLabel(asOf || null)}<span>Point-in-time replay · IST</span></div></div>
        <div className={styles.demoNotice}><span className={styles.noticeIcon} aria-hidden="true">i</span><p><strong>Synthetic data, real research discipline.</strong> All companies, prices and financial evidence in this demo are fictional. This is not current market data.</p><span className={styles.noticeTag}>DEMO ONLY</span></div>
        <section className={styles.toolbar} aria-label="Replay controls"><div className={styles.replayControl}><span className={styles.clock} aria-hidden="true"><svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="7" /><path d="M10 6v4l3 2" /></svg></span><label htmlFor="as-of">Replay as of</label><select id="as-of" value={asOf} onChange={(event) => changeReplay(event.target.value)} disabled={!demo}>{!demo && <option value="">Loading times…</option>}{demo?.replay_times.map((value) => <option key={value} value={value}>{time(value)} IST</option>)}</select><span className={styles.availableOnly}>Only evidence available at this time</span></div><button type="button" onClick={refreshReplay} disabled={!demo || loading} className={styles.refresh}><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M15 7a6 6 0 1 0 .5 5M15 3v4h-4" /></svg>{loading ? 'Loading replay' : 'Refresh replay'}</button></section>
        <div className={styles.liveStatus} role="status" aria-live="polite">{loading ? 'Loading the selected replay. Previous results have been cleared.' : replay ? `${replay.summary.total} underlying screens loaded for ${time(replay.as_of)} IST.` : ''}</div>
        {error && <section className={styles.error} role="alert"><span className={styles.errorIcon} aria-hidden="true">!</span><div><h2>Unable to load research</h2><p>{error}</p><p>No cached or generated market results are shown.</p><button type="button" className={styles.retry} onClick={() => configError ? setConfigAttempt((attempt) => attempt + 1) : refreshReplay()}>Retry connection</button></div></section>}
        {loading && !error && <div className={styles.loading} aria-hidden="true"><div className={styles.loadingDot} /><strong>Assembling the replay</strong><p>Checking the selected time and available evidence.</p></div>}
        {replay && currentReplay && !loading && !error && <>
          <SummaryCards summary={replay.summary} />
          <div className={styles.researchHeader}><span className={styles.sectionKicker}>REPLAY RESEARCH</span><span><i />As of {time(replay.as_of)} IST <b>·</b> {replay.rule_version}</span></div>
          <div className={styles.researchGrid}><CandidateList candidates={replay.candidates} selected={selected} onSelect={setSelected} />{candidate ? <ResearchDetail candidate={candidate} /> : <div className={styles.noSelection}>No underlying screens returned for this replay.</div>}</div>
          {candidate && <EvidencePanel candidate={candidate} asOf={replay.as_of} />}
          <footer className={styles.footer}><span>{replay.source}</span><span>No model calls <i>·</i> No order execution <i>·</i> Research v0.1</span></footer>
        </>}
      </main>
    </div>
  </div>;
}
