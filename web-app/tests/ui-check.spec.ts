import { test, expect } from '@playwright/test';

const BASE_URL = 'https://web-app-ebon-mu.vercel.app';

test.describe('UI Bug Detection Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Set viewport to desktop size
    page.setViewportSize({ width: 1280, height: 720 });
  });

  test('Dashboard page - check for visual issues', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);

    // Wait for DOM content instead of networkidle (SearchBar causes continuous requests)
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // Check for console errors
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Check if AI feature cards are visible
    const adaptiveLearning = page.locator('a[href="/adaptive-learning"]');
    await expect(adaptiveLearning).toBeVisible();

    const aiMentor = page.locator('a[href="/ai-mentor"]');
    await expect(aiMentor).toBeVisible();

    // Check accent-secondary color is applied (purple for AI features)
    const accentElements = page.locator('.bg-accent-secondary\\/10, .text-accent-secondary');
    const count = await accentElements.count();
    console.log(`Found ${count} elements with accent-secondary styling`);

    // Check stats cards
    const statsCards = page.locator('.card').filter({ hasText: /Course Progress|Current Streak|Completed|Remaining/ });
    await expect(statsCards).toHaveCount(4);

    // Check for broken images or missing content
    const images = page.locator('img');
    const imgCount = await images.count();
    console.log(`Found ${imgCount} images on dashboard`);

    // Check course outline section
    const courseOutline = page.locator('text=Course Outline');
    await expect(courseOutline).toBeVisible();

    console.log('Dashboard errors:', errors);
  });

  test('Chapters page - check grid layout and cards', async ({ page }) => {
    await page.goto(`${BASE_URL}/chapters`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Check page title
    await expect(page.locator('h1')).toContainText('Course Chapters');

    // Check for progress card
    const progressCard = page.locator('.card').filter({ hasText: 'Your Progress' });
    await expect(progressCard).toBeVisible();

    // Check filter tabs
    const tabs = page.locator('[role="tab"]');
    const tabCount = await tabs.count();
    console.log(`Found ${tabCount} filter tabs on chapters page`);
    expect(tabCount).toBeGreaterThan(0);

    // Check if chapters grid exists
    const grid = page.locator('.grid');
    await expect(grid.first()).toBeVisible();
  });

  test('Quizzes page - check quiz cards and layout', async ({ page }) => {
    await page.goto(`${BASE_URL}/quizzes`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Check page title
    await expect(page.locator('h1')).toContainText('Quizzes');

    // Check stats cards
    const statsCards = page.locator('.card .text-3xl');
    await expect(statsCards).toHaveCount(5);

    // Check tabs
    const tabs = page.locator('[role="tab"]');
    const tabCount = await tabs.count();
    console.log(`Found ${tabCount} tabs on quizzes page`);
    expect(tabCount).toBeGreaterThan(0);
  });

  test('Progress page - check visualization', async ({ page }) => {
    await page.goto(`${BASE_URL}/progress`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Check page title
    await expect(page.locator('h1')).toContainText('Progress');

    // Check for progress bars or circular progress
    const progressBars = page.locator('.progress, .circular');
    const count = await progressBars.count();
    console.log(`Found ${count} progress indicators`);
  });

  test('Navigation - check all menu items', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Check main navigation
    const navLinks = page.locator('nav a[href*="/"], nav button');
    const navCount = await navLinks.count();
    console.log(`Found ${navCount} navigation items`);

    // Check AI feature links
    const aiFeatures = page.locator('a:has-text("AI")');
    const aiCount = await aiFeatures.count();
    console.log(`Found ${aiCount} AI feature links`);

    // Check if accent-secondary hover states are applied
    const aiLink = page.locator('a[href="/adaptive-learning"]');
    if (await aiLink.isVisible()) {
      const hasHoverClass = await aiLink.getAttribute('class');
      const hasAccentSecondary = hasHoverClass?.includes('accent-secondary');
      console.log(`AI feature link has accent-secondary: ${hasAccentSecondary}`);
    }
  });

  test('Search functionality - check SearchBar', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Check if SearchBar exists
    const searchInput = page.locator('input[type="text"]').first();
    const isVisible = await searchInput.isVisible();

    if (isVisible) {
      // Type in search
      await searchInput.fill('test');
      await page.waitForTimeout(500);

      // Check if dropdown appears
      const dropdown = page.locator('.z-50 .card');
      const hasDropdown = await dropdown.count() > 0;
      console.log(`Search dropdown visible: ${hasDropdown}`);
    } else {
      console.log('SearchBar not visible on dashboard');
    }
  });

  test('Mobile responsive check', async ({ page }) => {
    // Set mobile viewport
    page.setViewportSize({ width: 375, height: 667 });

    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Check if mobile menu exists
    const mobileMenu = page.locator('button[aria-label*="menu"], button[aria-label*="Menu"]');
    const hasMobileMenu = await mobileMenu.count() > 0;
    console.log(`Mobile menu button exists: ${hasMobileMenu}`);

    // Check if main navigation is hidden on mobile
    const desktopNav = page.locator('.hidden.md\\:flex').first();
    const isHidden = await desktopNav.isHidden();
    console.log(`Desktop navigation hidden on mobile: ${isHidden}`);
  });

  test('Color contrast and accessibility', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Check for skip link (accessibility)
    const skipLink = page.locator('.skip-link');
    const hasSkipLink = await skipLink.count() > 0;
    console.log(`Skip link exists: ${hasSkipLink}`);

    // Check for ARIA labels
    const nav = page.locator('nav[aria-label="Global"]');
    await expect(nav).toBeVisible();

    // Check main content landmark
    const main = page.locator('main#main-content');
    await expect(main).toBeVisible();
  });

  test('Badge and card styling check', async ({ page }) => {
    await page.goto(`${BASE_URL}/chapters`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Check if badges are visible
    const badges = page.locator('.badge, [class*="badge"]');
    const badgeCount = await badges.count();
    console.log(`Found ${badgeCount} badges on chapters page`);

    // Check card styles
    const cards = page.locator('.card');
    const cardCount = await cards.count();
    console.log(`Found ${cardCount} cards`);

    // Check if cards have hover effects
    const firstCard = cards.first();
    const cardClass = await firstCard.getAttribute('class');
    const hasTransition = cardClass?.includes('transition');
    console.log(`Cards have transition classes: ${hasTransition}`);
  });

  test('Footer check', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Check footer exists
    const footer = page.locator('footer');
    await expect(footer).toBeVisible();

    // Check footer has correct styling
    const footerText = await footer.locator('p').textContent();
    console.log(`Footer text: ${footerText?.trim()}`);
  });
});
