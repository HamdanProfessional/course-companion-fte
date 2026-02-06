/**
 * Mobile E2E Tests
 *
 * Tests mobile-specific functionality including
 * responsive design and mobile menu.
 */

import { test, expect } from '@playwright/test';
import { AuthHelper } from '../helpers/auth-helpers';
import { ConsoleMonitor } from '../helpers/console-monitor';
import { TEST_USERS, PAGES } from '../helpers/test-data';

test.describe('Mobile', () => {

  test('should show mobile menu', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await AuthHelper.login(page, TEST_USERS.FREE.email, TEST_USERS.FREE.password);
    await page.waitForLoadState('domcontentloaded');

    // Look for mobile menu button
    const menuButton = page.locator('button[aria-label*="menu"], button[aria-label*="Menu"], button[class*="menu"]');
    const isMenuVisible = await menuButton.isVisible().catch(() => false);

    if (isMenuVisible) {
      await menuButton.click();
      await page.waitForTimeout(500);

      // Mobile menu should be visible
      const mobileMenu = page.locator('[class*="mobile"], [role="navigation"]');
      await expect(mobileMenu.first()).toBeVisible();
    }

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should work on mobile chapters page', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await AuthHelper.login(page, TEST_USERS.FREE.email, TEST_USERS.FREE.password);
    await page.goto(PAGES.CHAPTERS);
    await page.waitForLoadState('domcontentloaded');

    // Chapter cards should be visible on mobile
    const chapterCards = page.locator('.card');
    const cardCount = await chapterCards.count();

    expect(cardCount).toBeGreaterThan(0);

    // First card should be visible
    await expect(chapterCards.first()).toBeVisible();

    monitor.assertNoErrors();
    monitor.detach();
  });
});
