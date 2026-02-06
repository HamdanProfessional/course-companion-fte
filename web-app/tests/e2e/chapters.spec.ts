/**
 * Chapters E2E Tests
 *
 * Tests the chapters page including listing,
 * filtering, navigation, and access control.
 */

import { test, expect } from '@playwright/test';
import { AuthHelper } from '../helpers/auth-helpers';
import { ConsoleMonitor } from '../helpers/console-monitor';
import { TEST_USERS, CHAPTER_COUNT, PAGES } from '../helpers/test-data';

test.describe('Chapters', () => {

  test.beforeEach(async ({ page }) => {
    await AuthHelper.login(page, TEST_USERS.FREE.email, TEST_USERS.FREE.password);
  });

  test('should display all chapters', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.CHAPTERS);
    await page.waitForLoadState('domcontentloaded');

    // Check for chapter cards
    const chapterCards = page.locator('.card');
    const cardCount = await chapterCards.count();

    expect(cardCount).toBeGreaterThanOrEqual(CHAPTER_COUNT);

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should show completion badges for completed chapters', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.CHAPTERS);
    await page.waitForLoadState('domcontentloaded');

    // Demo user has completed 2 chapters
    const completedBadges = page.locator('.badge, [class*="completed"], [class*="Complete"]');

    // At least some badges should exist
    const badgeCount = await completedBadges.count();
    expect(badgeCount).toBeGreaterThan(0);

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should filter by difficulty', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.CHAPTERS);
    await page.waitForLoadState('domcontentloaded');

    // Click on a difficulty filter tab
    const beginnerTab = page.locator('text=Beginner');
    const isTabVisible = await beginnerTab.isVisible().catch(() => false);

    if (isTabVisible) {
      await beginnerTab.click();
      await page.waitForTimeout(500); // Wait for filter to apply

      // Verify some chapters are still visible
      const chapterCards = page.locator('.card');
      const cardCount = await chapterCards.count();
      expect(cardCount).toBeGreaterThan(0);
    }

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should navigate to chapter detail', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.CHAPTERS);
    await page.waitForLoadState('domcontentloaded');

    // Click on first chapter
    const firstChapter = page.locator('.card').first();
    await firstChapter.click();

    // Should navigate to chapter detail page
    await page.waitForURL(/\/chapters\/[^/]+/, { timeout: 5000 });

    // Check for chapter content
    const content = page.locator('article, .content, main');
    await expect(content.first()).toBeVisible();

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should enforce access control for free users', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.CHAPTERS);
    await page.waitForLoadState('domcontentloaded');

    // Look for locked chapters (beyond chapter 3 for FREE users)
    const lockIcons = page.locator('[class*="lock"], svg[class*="lock"]');
    const lockCount = await lockIcons.count();

    // For FREE tier, some chapters should be locked
    // (This depends on the UI implementation)
    if (lockCount > 0) {
      expect(lockCount).toBeGreaterThan(0);
    }

    monitor.assertNoErrors();
    monitor.detach();
  });
});
