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
