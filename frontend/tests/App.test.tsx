import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import App from '../src/App';
import { demo, jsonResponse, replayAt, times } from './fixtures';

function path(input: RequestInfo | URL): URL {
  return new URL(String(input), 'http://localhost');
}

function successfulApi(config = demo) {
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
    const url = path(input);
    return jsonResponse(url.pathname === '/api/demo' ? config : replayAt(url.searchParams.get('as_of')!));
  }));
}

describe('research replay', () => {
  it('shows all five synthetic screens while keeping contract analysis explicitly unavailable', async () => {
    successfulApi();
    render(<App />);
    expect(screen.getByText('Synthetic demo')).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /ALPHA/ })).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /Industries/ })).toHaveLength(5);
    expect(screen.getByText('Contract not evaluated')).toBeInTheDocument();
    expect(screen.getByText(/A qualified underlying screen is not an actionable trade/)).toBeInTheDocument();
    expect(screen.getByText('Financials: unknown')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /buy|sell|place order/i })).not.toBeInTheDocument();
  });

  it('updates the chosen replay and exposes late evidence only when it becomes available', async () => {
    successfulApi({ ...demo, default_as_of: times[0] });
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole('button', { name: /BETA/ }));
    expect(screen.queryByText('Beta result available at 09:40')).not.toBeInTheDocument();
    expect(screen.getByText('Financials: unknown')).toBeInTheDocument();
    await user.selectOptions(screen.getByRole('combobox', { name: 'Replay as of' }), times[1]);
    await screen.findByRole('button', { name: /ALPHA/ });
    expect(screen.queryByText('Beta result available at 09:40')).not.toBeInTheDocument();
    await user.selectOptions(screen.getByRole('combobox', { name: 'Replay as of' }), times[2]);
    expect(await screen.findByText('Beta result available at 09:40')).toBeInTheDocument();
    expect(screen.getByText('Financials: available')).toBeInTheDocument();
    expect(screen.getByText(/Available to the system by 30 Oct 2026, 09:40 IST/)).toBeInTheDocument();
  });

  it('clears results on an HTTP failure and can retry without substituting demo data', async () => {
    let failReplay = false;
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = path(input);
      if (url.pathname === '/api/demo') return jsonResponse(demo);
      return failReplay ? jsonResponse({ detail: 'Unavailable' }, 503) : jsonResponse(replayAt(url.searchParams.get('as_of')!));
    });
    vi.stubGlobal('fetch', fetchMock);
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole('button', { name: /ALPHA/ });
    failReplay = true;
    await user.click(screen.getByRole('button', { name: 'Refresh replay' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('HTTP 503');
    expect(screen.queryByRole('button', { name: /ALPHA/ })).not.toBeInTheDocument();
    expect(screen.getByText('Synthetic demo')).toBeInTheDocument();
    failReplay = false;
    await user.click(screen.getByRole('button', { name: 'Retry connection' }));
    expect(await screen.findByRole('button', { name: /ALPHA/ })).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('shows a recoverable error for malformed nested data rather than crashing or rendering it', async () => {
    const malformed = replayAt(times[1]);
    const wrongPayload = { ...malformed, candidates: [{ ...malformed.candidates[0], bars: [{ close: 'not a price', bar_end: times[1] }] }, ...malformed.candidates.slice(1)] };
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => jsonResponse(path(input).pathname === '/api/demo' ? demo : wrongPayload)));
    render(<App />);
    expect(await screen.findByRole('alert')).toHaveTextContent('incomplete or invalid research data');
    expect(screen.getByRole('button', { name: 'Retry connection' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /ALPHA/ })).not.toBeInTheDocument();
    expect(screen.getByText('Synthetic demo')).toBeInTheDocument();
  });

  it('clears in-flight results and rejects an older response even if the transport ignores cancellation', async () => {
    const pending = new Map<string, (response: Response) => void>();
    vi.stubGlobal('fetch', vi.fn((input: RequestInfo | URL) => {
      const url = path(input);
      if (url.pathname === '/api/demo') return Promise.resolve(jsonResponse(demo));
      return new Promise<Response>((resolve) => pending.set(url.searchParams.get('as_of')!, resolve));
    }));
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => expect(pending.has(times[1])).toBe(true));
    await act(async () => pending.get(times[1])!(jsonResponse(replayAt(times[1]))));
    await screen.findByRole('button', { name: /ALPHA/ });
    await user.selectOptions(screen.getByRole('combobox', { name: 'Replay as of' }), times[0]);
    expect(screen.queryByRole('button', { name: /ALPHA/ })).not.toBeInTheDocument();
    await waitFor(() => expect(pending.has(times[0])).toBe(true));
    await user.selectOptions(screen.getByRole('combobox', { name: 'Replay as of' }), times[2]);
    await waitFor(() => expect(pending.has(times[2])).toBe(true));
    await act(async () => pending.get(times[2])!(jsonResponse(replayAt(times[2]))));
    await user.click(await screen.findByRole('button', { name: /BETA/ }));
    expect(screen.getByText('Beta result available at 09:40')).toBeInTheDocument();
    await act(async () => pending.get(times[0])!(jsonResponse(replayAt(times[0]))));
    expect(screen.getByRole('combobox', { name: 'Replay as of' })).toHaveValue(times[2]);
    expect(screen.getByText('Beta result available at 09:40')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('09:40 IST');
  });

  it('keeps event evidence visible when financial evidence is still unknown', async () => {
    const result = replayAt(times[1]);
    result.candidates[0].evidence = [{
      id: 'alpha-event', kind: 'company_event', title: 'Synthetic board update',
      summary: 'Fictional corporate event, not a financial statement.', period: 'DEMO event',
      source: 'Synthetic fixture', source_url: null,
      published_at: times[0], available_at: times[0],
    }];
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => jsonResponse(path(input).pathname === '/api/demo' ? demo : result)));
    render(<App />);
    expect(await screen.findByText('Synthetic board update')).toBeInTheDocument();
    expect(screen.getByText('Financials: unknown')).toBeInTheDocument();
    expect(screen.getByText(/The available event evidence is shown below/)).toBeInTheDocument();
  });
});
