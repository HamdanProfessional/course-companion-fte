/**
 * Console error monitoring for E2E tests
 */

import { Page, ConsoleMessage } from '@playwright/test';

export class ConsoleMonitor {
  private errors: string[] = [];
  private warnings: string[] = [];
  private page: Page | null = null;

  /**
   * Attach console listeners to page
   */
  attach(page: Page): void {
    this.page = page;
    this.errors = [];
    this.warnings = [];

    page.on('console', (msg: ConsoleMessage) => {
      const type = msg.type();
      const text = msg.text();

      if (type === 'error') {
        this.errors.push(text);
      } else if (type === 'warning') {
        this.warnings.push(text);
      }
    });

    page.on('pageerror', (error: Error) => {
      this.errors.push(error.toString());
    });
  }

  /**
   * Get all console errors
   */
  getErrors(): string[] {
    return [...this.errors];
  }

  /**
   * Get all console warnings
   */
  getWarnings(): string[] {
    return [...this.warnings];
  }

  /**
   * Check if there are any errors
   */
  hasErrors(): boolean {
    return this.errors.length > 0;
  }

  /**
   * Check if there are any warnings
   */
  hasWarnings(): boolean {
    return this.warnings.length > 0;
  }

  /**
   * Assert no console errors occurred
   */
  assertNoErrors(): void {
    if (this.hasErrors()) {
      const errorList = this.errors.join('\n  - ');
      throw new Error(
        `Console errors detected:\n  - ${errorList}\nTotal: ${this.errors.length} errors`
      );
    }
  }

  /**
   * Assert no console warnings occurred
   */
  assertNoWarnings(): void {
    if (this.hasWarnings()) {
      const warningList = this.warnings.join('\n  - ');
      throw new Error(
        `Console warnings detected:\n  - ${warningList}\nTotal: ${this.warnings.length} warnings`
      );
    }
  }

  /**
   * Print errors to console
   */
  printErrors(): void {
    if (this.hasErrors()) {
      console.error(`\n❌ Console Errors (${this.errors.length}):`);
      this.errors.forEach((error, i) => {
        console.error(`  ${i + 1}. ${error}`);
      });
    } else {
      console.log('\n✅ No console errors');
    }
  }

  /**
   * Print warnings to console
   */
  printWarnings(): void {
    if (this.hasWarnings()) {
      console.warn(`\n⚠️ Console Warnings (${this.warnings.length}):`);
      this.warnings.forEach((warning, i) => {
        console.warn(`  ${i + 1}. ${warning}`);
      });
    } else {
      console.log('\n✅ No console warnings');
    }
  }

  /**
   * Print both errors and warnings
   */
  printAll(): void {
    this.printErrors();
    this.printWarnings();
  }

  /**
   * Reset error tracking
   */
  reset(): void {
    this.errors = [];
    this.warnings = [];
  }

  /**
   * Detach from page and cleanup
   */
  detach(): void {
    this.reset();
    this.page = null;
  }
}

/**
 * Create a console monitor and attach to page
 */
export async function createConsoleMonitor(page: Page): Promise<ConsoleMonitor> {
  const monitor = new ConsoleMonitor();
  monitor.attach(page);
  return monitor;
}
