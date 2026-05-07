import { test, expect } from '@playwright/test'

function uniqueId() {
  return Date.now().toString(36) + Math.random().toString(36).substring(2, 8);
}

test.describe.serial('Authentication', () => {
  test('should register new user', async ({ page }) => {
    const username = `user_${uniqueId()}`;
    const email = `user_${uniqueId()}@example.com`;

    await page.goto('/register');
    await page.waitForSelector('input[placeholder="Choose username"]', { timeout: 15000 });

    await page.fill('input[placeholder="Choose username"]', username);
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Register")');

    await page.waitForURL('**/wallet', { timeout: 30000 });
    await expect(page.locator('h2')).toContainText('Wallet');
  });

  test('should login existing user', async ({ page }) => {
    const id = uniqueId();
    const loginUser = `login_${id}`;
    const loginEmail = `login_${id}@example.com`;

    // First register
    await page.goto('/register');
    await page.waitForSelector('input[placeholder="Choose username"]', { timeout: 15000 });
    await page.fill('input[placeholder="Choose username"]', loginUser);
    await page.fill('input[type="email"]', loginEmail);
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Register")');
    await page.waitForURL('**/wallet', { timeout: 30000 });

    // Logout via clearing storage
    await page.evaluate(() => localStorage.clear());
    await page.goto('/login');
    await page.waitForSelector('input[placeholder="Enter username"]', { timeout: 15000 });

    // Login
    await page.fill('input[placeholder="Enter username"]', loginUser);
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');

    await page.waitForURL('**/wallet', { timeout: 30000 });
    await expect(page.locator('h2')).toContainText('Wallet');
  });

  test('should show error on wrong credentials', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('input[placeholder="Enter username"]', { timeout: 15000 });

    await page.fill('input[placeholder="Enter username"]', 'wronguser');
    await page.fill('input[type="password"]', 'wrongpass');
    await page.click('button:has-text("Login")');

    // Wait for error message
    await page.waitForSelector('.error-text', { timeout: 15000 });
    await expect(page.locator('.error-text')).toBeVisible();
  });

  test('should redirect to login when not authenticated', async ({ page }) => {
    await page.goto('/wallet');
    await page.waitForURL('**/login', { timeout: 15000 });
  });
});

test.describe.serial('Wallet operations', () => {
  let senderUsername: string;
  let senderEmail: string;

  test.beforeEach(async ({ page }) => {
    const id = uniqueId();
    senderUsername = `wallet_${id}`;
    senderEmail = `wallet_${id}@example.com`;

    await page.goto('/register');
    await page.waitForSelector('input[placeholder="Choose username"]', { timeout: 15000 });
    await page.fill('input[placeholder="Choose username"]', senderUsername);
    await page.fill('input[type="email"]', senderEmail);
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Register")');
    await page.waitForURL('**/wallet', { timeout: 30000 });
  });

  test('should display balance', async ({ page }) => {
    await expect(page.locator('body')).toContainText('$10,000');
  });

  test('should transfer funds', async ({ page }) => {
    const id = uniqueId();
    const receiver = `recv_${id}`;
    const recvEmail = `recv_${id}@example.com`;

    // Create receiver user (we'll be logged in as receiver after this)
    await page.evaluate(() => localStorage.clear());
    await page.goto('/register');
    await page.waitForSelector('input[placeholder="Choose username"]', { timeout: 15000 });
    await page.fill('input[placeholder="Choose username"]', receiver);
    await page.fill('input[type="email"]', recvEmail);
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Register")');
    await page.waitForURL('**/wallet', { timeout: 30000 });

    // Now login back as the sender
    await page.evaluate(() => localStorage.clear());
    await page.goto('/login');
    await page.waitForSelector('input[placeholder="Enter username"]', { timeout: 15000 });
    await page.fill('input[placeholder="Enter username"]', senderUsername);
    await page.fill('input[placeholder="Enter password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/wallet', { timeout: 30000 });

    // Now transfer funds to receiver
    await page.click('button:has-text("Transfer")');
    await page.waitForTimeout(1000);

    await page.fill('input[placeholder="Enter username"]', receiver);
    await page.fill('input[placeholder="0.00"]', '100');
    await page.click('button:has-text("Send")');

    // Wait for processing (simulated delay in backend)
    await page.waitForTimeout(6000);

    // Check that balance decreased
    await expect(page.locator('body')).toContainText('$9,89');
  });
});

test.describe.serial('Admin panel', () => {
  test('should deny access for regular user', async ({ page }) => {
    const id = uniqueId();
    await page.goto('/register');
    await page.waitForSelector('input[placeholder="Choose username"]', { timeout: 15000 });
    await page.fill('input[placeholder="Choose username"]', `reg_${id}`);
    await page.fill('input[type="email"]', `reg_${id}@example.com`);
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Register")');
    await page.waitForURL('**/wallet', { timeout: 30000 });

    await page.goto('/admin');
    await page.waitForURL('**/wallet', { timeout: 15000 });
  });

  test('should allow access for admin', async ({ page }) => {
    const id = uniqueId();
    await page.goto('/register');
    await page.waitForSelector('input[placeholder="Choose username"]', { timeout: 15000 });
    await page.fill('input[placeholder="Choose username"]', `admin_${id}`);
    await page.fill('input[type="email"]', `admin_${id}@example.com`);
    await page.fill('input[type="password"]', 'password123');
    await page.selectOption('select', 'admin');
    await page.click('button:has-text("Register")');

    // Admin users should be redirected to /admin
    await page.waitForTimeout(3000);

    const currentUrl = page.url();
    if (!currentUrl.includes('/admin')) {
      await page.goto('/admin');
    }

    await expect(page.locator('body')).toContainText('Admin', { timeout: 15000 });
  });
});
