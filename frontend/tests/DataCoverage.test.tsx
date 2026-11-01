import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import DataCoverage from '../src/components/DataCoverage';
import App from '../src/App';
import { getCoverage } from '../src/coverage';
import fixture from './coverageFixture.json';
import { demo, jsonResponse, replayAt } from './fixtures';

const empty = { api_version: 'coverage-api-v1', state: 'not_imported', report: null };
const copy = () => structuredClone(fixture);
async function expand() { await userEvent.click(screen.getByText('View coverage details')); }

function serve(body: unknown) { vi.stubGlobal('fetch', vi.fn(async () => jsonResponse(body))); }

describe('separate data coverage', () => {
  it('distinguishes no import and a configured invalid report', async () => {
    let body = empty;
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse(body)));
    render(<DataCoverage />);
    expect(await screen.findByText('Not imported')).toBeInTheDocument();
    await expand();
    expect(screen.getByText(/No local import report is configured/)).toBeVisible();
    body = { ...empty, state: 'invalid_report' };
    await userEvent.click(screen.getByRole('button', { name: 'Refresh coverage' }));
    expect(await screen.findByText('Invalid report')).toBeInTheDocument();
    expect(screen.getByText(/configured report is missing, unreadable or incompatible/)).toBeVisible();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('shows complete synthetic coverage without claiming a real trial or changing the research desk', async () => {
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input), 'http://localhost');
      return jsonResponse(url.pathname === '/api/data-coverage' ? fixture : url.pathname === '/api/demo' ? demo : replayAt(url.searchParams.get('as_of')!));
    }));
    render(<App />);
    expect(await screen.findByText('Coverage complete')).toBeInTheDocument();
    await expand();
    expect(screen.getByText('Synthetic test — not a real-data trial')).toBeVisible();
    expect(screen.getAllByText('9 / 9')).toHaveLength(4);
    expect(screen.getByText('Synthetic demo', { exact: true })).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /ALPHA/ })).toBeInTheDocument();
    expect(screen.getByText('Contract not evaluated')).toBeInTheDocument();
    expect(screen.getByText(/Imported data does not drive the synthetic rankings/)).toBeInTheDocument();
  });

  it('shows partial user import, unknown membership, date-only filing and separate gaps', async () => {
    const body = copy();
    Object.assign(body.report, { status: 'partial', dataset_nature: 'user_import', gaps: ['missing_bars', 'eligibility_review_pending', 'filing_publication_partial'] });
    Object.assign(body.report.series[0], { present: 8, missing: ['09:20'] });
    Object.assign(body.report.membership[0], { level: 'user_assertion', dated_review: false });
    body.report.filing.publication_precision = 'date_only';
    serve(body); render(<DataCoverage />);
    expect(await screen.findByText('Partial')).toBeInTheDocument(); await expand();
    expect(screen.getByText('8 / 9')).toBeVisible();
    expect(screen.getByText('09:20')).toBeVisible();
    expect(screen.getByText(/DEMO_ALPHA: user assertion · dated review pending/)).toBeVisible();
    expect(screen.getByText(/DEMO_ALPHA: publication date only/)).toBeVisible();
    expect(screen.queryByText('Coverage complete')).not.toBeInTheDocument();
  });

  it('accepts complete coverage with zero optional figures and keeps values unknown', async () => {
    const body = copy();
    body.report.filing.figures_present = 0;
    serve(body); render(<DataCoverage />);
    expect(await screen.findByText('Coverage complete')).toBeInTheDocument();
    await expand();
    expect(screen.getByText('No optional financial figures supplied; financial values remain unknown.')).toBeVisible();
    expect(screen.getByText(/0 figures supplied/)).toBeVisible();
    expect(screen.getByText('Synthetic test — not a real-data trial')).toBeVisible();
    expect(screen.queryByText('Remaining gaps')).not.toBeInTheDocument();
  });

  it('does not reconcile a zero-figure filing automatically', async () => {
    const body = copy();
    Object.assign(body.report, { status: 'partial', gaps: ['filing_reconciliation_pending'] });
    Object.assign(body.report.filing, { figures_present: 0, reconciliation: 'transcribed' });
    serve(body); render(<DataCoverage />);
    expect(await screen.findByText('Partial')).toBeInTheDocument(); await expand();
    expect(screen.getByText(/transcription transcribed/)).toBeVisible();
    expect(screen.getByText(/No optional financial figures supplied/)).toBeVisible();
    expect(screen.getByText(/Manually reconcile the filing transcription/)).toBeVisible();
  });

  it('keeps legacy figure-gap reports partial and explains how to regenerate them', async () => {
    const body = copy();
    Object.assign(body.report, { status: 'partial', gaps: ['filing_figures_missing'] });
    body.report.filing.figures_present = 0;
    serve(body); render(<DataCoverage />);
    expect(await screen.findByText('Partial')).toBeInTheDocument(); await expand();
    expect(screen.getByText(/Legacy report: optional figures no longer block completion/)).toBeVisible();
    expect(screen.getByText(/Rerun the original inputs to generate a new report; preserve this report/)).toBeVisible();
    expect(screen.queryByText('Coverage complete')).not.toBeInTheDocument();
  });

  it('rejects invalid figure counts even when a complete report may have zero', async () => {
    for (const count of [-1, 4, 0.5, true, null, '0', NaN, Infinity]) {
      const body = copy();
      Object.assign(body.report.filing, { figures_present: count });
      serve(body);
      await expect(getCoverage(new AbortController().signal)).rejects.toThrow(/malformed report/);
    }
  });

  it('still rejects complete zero-figure reports without the other required coverage', async () => {
    const original = copy();
    original.report.filing.figures_present = 0;
    const reports = [
      { ...original.report, filing: { ...original.report.filing, status: 'not_imported', symbol: null, publication_precision: 'unknown', reconciliation: 'unreviewed', source_known: false } },
      { ...original.report, filing: { ...original.report.filing, publication_precision: 'date_only' } },
      { ...original.report, filing: { ...original.report.filing, reconciliation: 'transcribed' } },
      { ...original.report, filing: { ...original.report.filing, source_known: false } },
      { ...original.report, source_review: 'pending' },
      { ...original.report, session_review: 'pending' },
      { ...original.report, retention: 'unresolved' },
      { ...original.report, membership: original.report.membership.map(m => ({ ...m, dated_review: false })) },
      { ...original.report, series: original.report.series.map(s => ({ ...s, present: 8, missing: ['09:20'] })) },
      { ...original.report, gaps: ['filing_publication_partial'] },
    ];
    for (const report of reports) {
      serve({ ...original, report });
      await expect(getCoverage(new AbortController().signal)).rejects.toThrow(/malformed report/);
    }
  });

  it('keeps invalid inputs distinct from absent inputs and backend errors', async () => {
    const body = copy();
    Object.assign(body.report, { status: 'invalid', schema_valid: false, invalid_rows: 1, gaps: ['invalid_rows'] });
    serve(body); render(<DataCoverage />);
    expect(await screen.findByText('Invalid inputs')).toBeInTheDocument(); await expand();
    expect(screen.getByText(/Correct malformed or contradictory inputs/)).toBeVisible();
  });

  it('clears coverage on failure and recovers using its own refresh control', async () => {
    let fail = false;
    vi.stubGlobal('fetch', vi.fn(async () => fail ? jsonResponse({}, 503) : jsonResponse(fixture)));
    render(<DataCoverage />); await screen.findByText('Coverage complete'); await expand();
    fail = true;
    await userEvent.click(screen.getByRole('button', { name: 'Refresh coverage' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('HTTP 503');
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
    expect(screen.queryByText('Coverage complete')).not.toBeInTheDocument();
    fail = false;
    await userEvent.click(screen.getByRole('button', { name: 'Refresh coverage' }));
    expect(await screen.findByRole('table')).toBeVisible();
  });

  it('rejects incompatible, nonfinite, inconsistent and malformed payloads', async () => {
    const invalids: unknown[] = [
      { ...empty, api_version: 'future' },
      { ...fixture, report: { ...fixture.report, schema_version: 'future' } },
      { ...fixture, report: { ...fixture.report, imported_at: 'yesterday' } },
      { ...fixture, report: { ...fixture.report, series: [{ ...fixture.report.series[0], present: null }] } },
      { ...fixture, report: { ...fixture.report, source_label: '/private/path' } },
      { ...fixture, report: { ...fixture.report, membership: [] } },
      { ...fixture, report: { ...fixture.report, price_adjustment: 'unknown' } },
      { ...fixture, report: { ...fixture.report, filing: null } },
      { ...fixture, report: { ...fixture.report, invalid_rows: Infinity } },
    ];
    for (const body of invalids) {
      serve(body);
      await expect(getCoverage(new AbortController().signal)).rejects.toThrow(/malformed report/);
    }
  });
});
