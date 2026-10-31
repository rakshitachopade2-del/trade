import { spawn, type ChildProcess } from 'node:child_process';
import { once } from 'node:events';
import { fileURLToPath } from 'node:url';
import { test, expect, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const root = fileURLToPath(new URL('../../', import.meta.url));
let backend: ChildProcess | undefined;

async function startBackend() {
  // Refuse occupied ports so the outage check never stops another user's server.
  const { createServer } = await import('node:net');
  const probe = createServer();
  await new Promise<void>((resolve, reject) => {
    probe.once('error', reject);
    probe.listen(8000, '127.0.0.1', () => probe.close(() => resolve()));
  });
  backend = spawn(`${root}.venv/bin/python`, ['-m', 'uvicorn', 'backend.app.main:app', '--host', '127.0.0.1', '--port', '8000'], { cwd: root, stdio: 'pipe' });
  let output = '';
  backend.stdout?.on('data', data => { output += data; });
  backend.stderr?.on('data', data => { output += data; });
  backend.on('error', error => { output += error.message; });
  await expect.poll(async () => {
    if (backend?.exitCode !== null) throw new Error(output);
    try { return (await fetch('http://127.0.0.1:8000/api/health')).status; }
    catch { return 0; }
  }, { timeout: 15_000 }).toBe(200);
}

async function stopBackend() {
  if (backend && backend.exitCode === null && backend.signalCode === null) {
    const exited = once(backend, 'exit');
    backend.kill('SIGTERM');
    await exited;
  }
  backend = undefined;
}

async function selectTime(page: Page, minute: string) {
  await page.getByRole('combobox', { name: 'Replay as of' }).selectOption(`2026-10-30T09:${minute}:00+05:30`);
  await expect(page.getByRole('status')).toContainText(`loaded for 09:${minute} IST`);
}

async function checkLayout(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(results.violations).toEqual([]);
}

test.beforeAll(startBackend);
test.afterAll(stopBackend);

test('replay, evidence, exclusions, keyboard access and responsive layout', async ({ page }, testInfo) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.getByRole('button', { name: /ALPHA/ })).toBeVisible();
  await expect(page.getByText('Synthetic demo', { exact: true })).toBeVisible();
  await expect(page.getByText('Contract not evaluated', { exact: true })).toBeVisible();
  await checkLayout(page);
  await page.screenshot({ path: testInfo.outputPath('09-35-alpha.png'), fullPage: true });

  await selectTime(page, '30');
  await expect(page.locator('[aria-label="Replay summary"] section').filter({ hasText: 'Screen qualified' })).toContainText('00');
  await expect(page.getByText('The opening range is complete; wait for a subsequent completed bar.')).toBeVisible();
  await selectTime(page, '35');
  await expect(page.locator('[aria-label="Replay summary"] section').filter({ hasText: 'Screen qualified' })).toContainText('01');

  await page.getByRole('button', { name: /BETA/ }).click();
  await expect(page.getByText('Financials: unknown', { exact: true })).toBeVisible();
  await expect(page.getByText('Synthetic result released during replay', { exact: true })).toHaveCount(0);
  await checkLayout(page);
  await selectTime(page, '40');
  await expect(page.getByText('Synthetic result released during replay', { exact: true })).toBeVisible();
  await expect(page.getByText('Financials: available', { exact: true })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('09-40-beta.png'), fullPage: true });
  await selectTime(page, '35');
  await expect(page.getByText('Synthetic result released during replay', { exact: true })).toHaveCount(0);

  for (const [symbol, reason] of [
    ['DELTA', 'Listed-options eligibility is unknown at this time.'],
    ['EPSILON', 'The latest available completed bar is more than 300 seconds old.'],
    ['GAMMA', 'Listed-options eligibility is ineligible at this time.'],
  ]) {
    await page.getByRole('button', { name: new RegExp(symbol) }).click();
    await expect(page.getByText(reason, { exact: true })).toBeVisible();
    await expect(page.getByText('Contract not evaluated', { exact: true })).toBeVisible();
  }

  await page.reload();
  await expect(page.getByRole('button', { name: /ALPHA/ })).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to research' })).toBeFocused();
  await page.keyboard.press('Enter');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('combobox', { name: 'Replay as of' })).toBeFocused();
  await page.getByRole('button', { name: /BETA/ }).focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('button', { name: /BETA/ })).toHaveAttribute('aria-pressed', 'true');
  expect(errors).toEqual([]);
});

test('real backend outage clears results and retry recovers', async ({ page }, testInfo) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: /ALPHA/ })).toBeVisible();
  await stopBackend();
  await page.getByRole('button', { name: 'Refresh replay' }).click();
  await expect(page.getByRole('alert')).toContainText('Unable to load research');
  await expect(page.getByRole('button', { name: /ALPHA/ })).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole('alert')).toContainText('No cached or generated market results are shown.');
  await expect(page.getByRole('button', { name: /ALPHA/ })).toHaveCount(0);
  await checkLayout(page);
  await page.screenshot({ path: testInfo.outputPath('backend-offline.png'), fullPage: true });
  await startBackend();
  await page.getByRole('button', { name: 'Retry connection' }).click();
  await expect(page.getByRole('button', { name: /ALPHA/ })).toBeVisible();
  await expect(page.getByRole('alert')).toHaveCount(0);
});
