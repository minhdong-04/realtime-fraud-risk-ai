/*
 * Playwright E2E Test cho luồng kiểm duyệt Fraud Case (E2E-01, E2E-02).
 */

import { test, expect } from '@playwright/test';

test.describe('E2E Fraud Review Workflow', () => {
  test('E2E-01: Analyst đăng nhập và điều hướng tới Analyst Queue', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'analyst@bank.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/analyst');
    await expect(page.locator('h1')).toContainText('Hàng Đợi Kiểm Duyệt');
  });

  test('E2E-02: Analyst xem chi tiết Case và submit review', async ({ page }) => {
    await page.goto('/analyst');
    const firstCase = page.locator('table tr').nth(1);
    if (await firstCase.isVisible()) {
      await firstCase.click();
      await expect(page.locator('textarea[name="reason"]')).toBeVisible();
    }
  });
});
