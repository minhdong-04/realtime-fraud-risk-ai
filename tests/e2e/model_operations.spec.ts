/*
 * Playwright E2E Test cho thao tác ML Engineer Promote / Rollback (E2E-03, E2E-04).
 */

import { test, expect } from '@playwright/test';

test.describe('E2E ML Engineer Model Operations', () => {
  test('E2E-03: ML Engineer truy cập Model Registry', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'ml_engineer@bank.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await page.goto('/ml-engineer');
    await expect(page.locator('h1')).toContainText('Model Registry');
  });
});
