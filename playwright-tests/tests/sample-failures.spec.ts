import { test, expect } from '@playwright/test';

test('realistic login failure', async ({ page }) => {
    // Go to a real site with a login button
    await page.goto('https://the-internet.herokuapp.com/login');

    // INTENTIONAL FAILURE: wrong selector
    await page.click('button:has-text("Sign In")');

    // This won't be reached
    await expect(page).toHaveURL(/secure/);
});