/**
 * Authentication helper utilities for E2E tests
 */

import { Page, expect } from '@playwright/test';

export class AuthHelper {
  /**
   * Login with email and password
   */
  static async login(page: Page, email: string, password: string): Promise<void> {
    await page.goto('/login');
    await page.waitForLoadState('domcontentloaded');

    // Fill login form
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard', { timeout: 5000 });
  }

  /**
   * Logout by clearing localStorage
   */
  static async logout(page: Page): Promise<void> {
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.goto('/login');
  }

  /**
   * Get authentication token from localStorage
   */
  static async getAuthToken(page: Page): Promise<string | null> {
    return await page.evaluate(() => localStorage.getItem('token'));
  }

  /**
   * Get user ID from localStorage
   */
  static async getUserId(page: Page): Promise<string | null> {
    return await page.evaluate(() => localStorage.getItem('user_id'));
  }

  /**
   * Check if user is authenticated
   */
  static async isAuthenticated(page: Page): Promise<boolean> {
    const token = await this.getAuthToken(page);
    const userId = await this.getUserId(page);
    return !!(token && userId);
  }

  /**
   * Register a new user
   */
  static async register(
    page: Page,
    email: string,
    password: string,
    confirmPassword: string
  ): Promise<void> {
    await page.goto('/register');
    await page.waitForLoadState('domcontentloaded');

    // Fill registration form
    await page.fill('input[type="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.fill('input[name="confirmPassword"]', confirmPassword);

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard', { timeout: 5000 });
  }

  /**
   * Wait for authentication to complete
   */
  static async waitForAuth(page: Page): Promise<void> {
    await page.waitForURL(/\/dashboard|\/login/, { timeout: 5000 });
  }

  /**
   * Assert user is on dashboard
   */
  static async assertOnDashboard(page: Page): Promise<void> {
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.locator('h1')).toContainText('Dashboard');
  }
}
