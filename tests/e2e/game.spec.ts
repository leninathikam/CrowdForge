import { test, expect } from '@playwright/test';

test('runner, audience, mutation, replay, overlay and reconnect form one working loop', async ({ page, context }) => {
  const consoleErrors: string[] = [];
  page.on('pageerror', error => consoleErrors.push(error.message));
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Your run. Their rules.' })).toBeVisible();
  await expect(page.getByText('SIMULATION MODE', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Enter the arena', exact: true }).click();
  await page.keyboard.press('ArrowRight');
  await expect(page.getByTestId('arena')).toHaveAttribute('aria-label', /Player at 3, 13/);
  await page.getByRole('button', { name: 'Pause', exact: true }).click();
  const paused = await page.getByTestId('round-timer').innerText();
  await page.waitForTimeout(500); // Explicitly verify the timer stays stopped during pause.
  await expect(page.getByTestId('round-timer')).toHaveText(paused);
  await page.getByRole('button', { name: 'Audience impact timeline', exact: true }).click();
  await page.getByRole('button', { name: 'Back to arena', exact: true }).click();
  await page.getByRole('button', { name: 'Resume round', exact: true }).click();
  await page.getByRole('button', { name: 'Simulate lava vote', exact: true }).click();
  await expect(page.locator('.lava .option-bottom b')).toContainText('1');
  await expect(page.getByText('LAVA FORGED', { exact: true })).toBeVisible({ timeout: 18000 });
  await page.getByRole('button', { name: 'Freeze votes', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Simulate wall vote' })).toBeDisabled();
  await page.getByRole('button', { name: 'Unfreeze votes', exact: true }).click();
  await page.getByRole('button', { name: 'OBS overlay setup' }).click();
  const overlayUrl = await page.getByLabel('Read-only overlay URL').inputValue();
  const observer = await context.newPage();
  await observer.goto(overlayUrl);
  await expect(observer.getByTestId('arena')).toHaveAttribute('aria-label', /Player at 3, 13/);
  await expect(observer.getByRole('button', { name: 'Pause', exact: true })).toHaveCount(0);
  await observer.screenshot({ path: 'artifacts/screenshots/overlay.png', fullPage: true });
  await observer.close();
  await page.getByRole('button', { name: 'Close dialog' }).click();
  await page.reload();
  await expect(page.getByText('World synchronized', { exact: false })).toBeVisible();
  await expect(page.getByTestId('arena')).toHaveAttribute('aria-label', /Player at 3, 13/);
  const id = new URL(page.url()).searchParams.get('session');
  const response = await page.request.get('/api/sessions/' + id);
  const state = await response.json();
  const queue: number[][] = [state.player], previous = new Map<string, number[] | null>([[state.player.join(','), null]]);
  for (let i = 0; i < queue.length; i++) {
    const [x, y] = queue[i];
    if (x === state.exit[0] && y === state.exit[1]) break;
    for (const [dx, dy] of [[1, 0], [0, -1], [-1, 0], [0, 1]]) {
      const next = [x + dx, y + dy], key = next.join(',');
      if (state.grid[next[1]]?.[next[0]] !== undefined && [0, 3].includes(state.grid[next[1]][next[0]]) && !previous.has(key)) { previous.set(key, [x, y]); queue.push(next); }
    }
  }
  const path: number[][] = []; let point = state.exit;
  while (point) { path.unshift(point); point = previous.get(point.join(',')); }
  expect(path[0]).toEqual(state.player);
  await page.getByTestId('arena').click();
  for (let i = 1; i < path.length; i++) {
    const dx = path[i][0] - path[i - 1][0], dy = path[i][1] - path[i - 1][1];
    await page.waitForTimeout(215); // Server movement cooldown is 125 ms, with 100 ms ticks.
    await page.keyboard.press(dx === 1 ? 'ArrowRight' : dx === -1 ? 'ArrowLeft' : dy === 1 ? 'ArrowDown' : 'ArrowUp');
    await expect(page.getByTestId('arena')).toHaveAttribute('aria-label', new RegExp(`Player at ${path[i][0]}, ${path[i][1]}\\.`));
  }
  await expect(page.getByRole('heading', { name: 'You beat the world.' })).toBeVisible();
  await page.screenshot({ path: 'artifacts/screenshots/round-result.png', fullPage: true });
  await page.getByRole('button', { name: 'See the impact timeline' }).click();
  await expect(page.getByText('AUDIENCE IMPACT REPLAY', { exact: true })).toBeVisible();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export deterministic replay' }).click();
  await (await download).saveAs('artifacts/e2e-replay.json');
  await page.getByRole('button', { name: 'Back to arena' }).click();
  await page.getByRole('button', { name: 'Forge another run' }).click();
  await expect(page.getByRole('button', { name: 'Enter the arena' })).toBeVisible();
  await page.screenshot({ path: 'artifacts/screenshots/desktop.png', fullPage: true });
  expect(consoleErrors).toEqual([]);
});

test('narrow layout, help, settings and connection setup remain usable', async ({ page }) => {
  await page.setViewportSize({ width: 1000, height: 850 });
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Enter the arena' })).toBeVisible();
  await page.getByRole('button', { name: 'Settings', exact: true }).click();
  await page.getByLabel('World seed', { exact: true }).fill('927');
  await page.getByRole('button', { name: 'Create new arena' }).click();
  await expect(page.getByText('#927', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'How to play', exact: true }).first().click();
  await expect(page.getByRole('heading', { name: 'Welcome to the forge.' })).toBeVisible();
  await page.getByRole('button', { name: 'Close dialog' }).click();
  await page.getByRole('button', { name: 'Connect Twitch' }).click();
  await expect(page.getByRole('heading', { name: 'Connect your Twitch.' })).toBeVisible();
  await page.getByRole('button', { name: 'Close dialog' }).click();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: 'artifacts/screenshots/mobile.png', fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
});
