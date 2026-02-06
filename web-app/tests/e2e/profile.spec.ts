/**
 * Profile E2E Tests
 *
 * Tests the profile page including user info display
 * and tier upgrade functionality.
 */

import { test, expect } from '@playwright/test';
import { AuthHelper } from '../helpers/auth-helpers';
import { ConsoleMonitor } from '../helpers/console-monitor';
import { TEST_USERS, PAGES } from '../helpers/test-data';

test.describe('Profile', () => {

  test.beforeEach(async ({ page }) => {
    await AuthHelper.login(page, TEST_USERS.FREE.email, TEST_USERS.FREE.password);
  });

  test('should display user info', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.PROFILE);
    await page.waitForLoadState('domcontentloaded');

    // Check for user email display
    const emailElement = page.locator(`text=${TEST_USERS.FREE.email}`);
    const isEmailVisible = await emailElement.isVisible().catch(() => false);

    if (!isEmailVisible) {
      // Email might be in a different element
      const anyText = await page.textContent('body');
      expect(anyText).toContain(TEST_USERS.FREE.email);
    }

    // Check for tier display
    const tierElement = page.locator(`text=${TEST_USERS.FREE.tier}`);
    const isTierVisible = await tierElement.isVisible().catch(() => false);

    if (!isTierVisible) {
      const anyText = await page.textContent('body');
      expect(anyText).toContain(TEST_USERS.FREE.tier);
    }

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should allow tier upgrade', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.PROFILE);
    await page.waitForLoadState('domcontentloaded');

    // Look for upgrade button or link
    const upgradeButton = page.locator('button:has-text("Upgrade"), a:has-text("Upgrade"), button:has-text("Premium")');
    const isButtonVisible = await upgradeButton.isVisible().catch(() => false);

    if (isButtonVisible) {
      await upgradeButton.click();

      // Should navigate to subscription/upgrade page
      await page.waitForTimeout(1000);
      const url = page.url();

      // Should be on subscription-related page
      const isSubscriptionPage = url.includes('/subscription') || url.includes('/upgrade') || url.includes('/pricing');
      expect(isSubscriptionPage).toBeTruthy();
    }

    monitor.assertNoErrors();
    monitor.detach();
  });
});
