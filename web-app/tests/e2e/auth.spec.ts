/**
 * Authentication E2E Tests
 *
 * Tests user authentication flows including login, registration,
 * password validation, and route protection.
 */

import { test, expect } from '@playwright/test';
import { AuthHelper } from '../helpers/auth-helpers';
import { ConsoleMonitor } from '../helpers/console-monitor';
import { TEST_USERS, INVALID_CREDENTIALS, NEW_USER, PAGES } from '../helpers/test-data';

test.describe('Authentication Flow', () => {

  test('should login with valid credentials', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await AuthHelper.login(page, TEST_USERS.FREE.email, TEST_USERS.FREE.password);
    await AuthHelper.assertOnDashboard(page);

    // Verify auth was stored
    const token = await AuthHelper.getAuthToken(page);
    const userId = await AuthHelper.getUserId(page);
    expect(token).toBeTruthy();
    expect(userId).toBe(TEST_USERS.FREE.userId);

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.LOGIN);
    await page.waitForLoadState('domcontentloaded');

    await page.fill('input[type="email"]', INVALID_CREDENTIALS.email);
    await page.fill('input[type="password"]', INVALID_CREDENTIALS.password);
    await page.click('button[type="submit"]');

    // Should stay on login page and show error
    await page.waitForURL(/\/login/, { timeout: 5000 });
    const errorElement = page.locator('text=Invalid email or password');
    await expect(errorElement).toBeVisible({ timeout: 3000 }).catch(() => {
      // If error message is different, check for any error
      return expect(page.locator('.error, [role="alert"]').first()).toBeVisible();
    });

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should register new user', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.REGISTER);
    await page.waitForLoadState('domcontentloaded');

    await page.fill('input[type="email"]', NEW_USER.email);
    await page.fill('input[name="password"]', NEW_USER.password);
    await page.fill('input[name="confirmPassword"]', NEW_USER.confirmPassword);

    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL(/\/dashboard/, { timeout: 10000 });

    // Verify user is logged in
    const token = await AuthHelper.getAuthToken(page);
    const userId = await AuthHelper.getUserId(page);
    expect(token).toBeTruthy();
    expect(userId).toBeTruthy();

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should validate password match', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    await page.goto(PAGES.REGISTER);
    await page.waitForLoadState('domcontentloaded');

    await page.fill('input[type="email"]', NEW_USER.email);
    await page.fill('input[name="password"]', 'Password123');
    await page.fill('input[name="confirmPassword"]', 'DifferentPassword123');

    await page.click('button[type="submit"]');

    // Should show validation error
    const errorElement = page.locator('text=Passwords do not match');
    await expect(errorElement).toBeVisible({ timeout: 3000 }).catch(() => {
      return expect(page.locator('.error, [role="alert"]').first()).toBeVisible();
    });

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    // Clear any existing auth
    await AuthHelper.logout(page);

    // Try to access dashboard without auth
    await page.goto(PAGES.DASHBOARD);

    // Should be redirected to login
    await page.waitForURL(/\/login/, { timeout: 5000 });
    expect(page.url()).toContain('/login');

    // Check for returnTo parameter
    const url = new URL(page.url());
    const returnTo = url.searchParams.get('returnTo');
    expect(returnTo).toBe('/dashboard');

    monitor.assertNoErrors();
    monitor.detach();
  });

  test('should persist auth across page refresh', async ({ page }) => {
    const monitor = new ConsoleMonitor();
    monitor.attach(page);

    // Login
    await AuthHelper.login(page, TEST_USERS.FREE.email, TEST_USERS.FREE.password);

    // Refresh page
    await page.reload();

    // Should still be on dashboard
    await page.waitForURL(/\/dashboard/, { timeout: 5000 });
    await expect(page.locator('h1')).toContainText('Dashboard');

    // Auth should still be present
    const token = await AuthHelper.getAuthToken(page);
    expect(token).toBeTruthy();

    monitor.assertNoErrors();
    monitor.detach();
  });
});
