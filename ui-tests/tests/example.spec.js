const { test, expect } = require("@playwright/test");

// Environment variable for the base URL
const BASE_URL = process.env.BASE_URL || "https://example.com";

test("homepage has correct title", async ({ page }) => {
    await page.goto(BASE_URL); // Use HTTPS instead of HTTP
    await expect(page).toHaveTitle(/Example Domain/);
    // Additional test for page content
    await expect(page.locator('h1')).toHaveText('Example Domain');
});
