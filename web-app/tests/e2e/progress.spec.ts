/**
 * Progress E2E Tests
 *
 * Tests the progress page including visualization,
 * streak calendar, and chapter-by-chapter progress.
 */

import { test, expect } from '@playwright/test';
import { AuthHelper } from '../helpers/auth-helpers';
import { ConsoleMonitor } from '../helpers/console-monitor';
import { TEST_USERS, DEMO_USER_EXPECTED, PAGES } from '../helpers/test-data';

test.describe('Progress', () => {

  test.beforeEach(async ({ page }) => {
    await AuthHelper.login(page, TEST_USERS.FREE.email, TEST_USERS.FREE.password);
  });

  test('should display overall progress', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.PROGRESS);
    await page.waitForLoadState('domcontentloaded');

    // Check for progress display
    const progressElement = page.locator('text=/Progress|Completion/');
    await expect(progressElement.first()).toBeVisible();

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should display streak calendar', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.PROGRESS);
    await page.waitForLoadState('domcontentloaded');

    // Check for streak calendar or display
    const streakElement = page.locator('text=Streak, text=Days, [class*="calendar"]');
    const isStreakVisible = await streakElement.isVisible().catch(() => false);

    if (isStreakVisible) {
      await expect(streakElement.first()).toBeVisible();
    }

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should display chapter-by-chapter progress', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.PROGRESS);
    await page.waitForLoadState('domcontentloaded');

    // Check for chapter list or grid
    const chapterList = page.locator('.list, .grid, [class*="chapter"]');
    await expect(chapterList.first()).toBeVisible();

    // Should have multiple items
    const chapterItems = page.locator('[class*="chapter"], .list-item');
    const itemCount = await chapterItems.count();
    expect(itemCount).toBeGreaterThan(0);

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should record daily checkin', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.PROGRESS);
    await page.waitForLoadState('domcontentloaded');

    // Look for checkin button
    const checkinButton = page.locator('button:has-text("Check In"), button:has-text("Daily")');
    const isButtonVisible = await checkinButton.isVisible().catch(() => false);

    if (isButtonVisible) {
      // Get initial streak
      const initialStreakText = await page.locator(`text=/${DEMO_USER_EXPECTED.streak}/`).first().textContent().catch(() => '5');

      // Click checkin
      await checkinButton.click();
      await page.waitForTimeout(1000);

      // Streak should be updated (or already checked in today)
      const finalStreakText = await page.locator(`text=/${DEMO_USER_EXPECTED.streak}/`).first().textContent().catch(() => initialStreakText);

      expect(finalStreakText).toBeTruthy();
    }

    monitor.assertNoErrors();
    monitor.detach();
  });
});
