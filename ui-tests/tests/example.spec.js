const { test, expect } = require("@playwright/test");

// Environment variable for the base URL
const BASE_URL = process.env.BASE_URL || "https://example.com";

test("homepage has correct title", async ({ page }) => {
    // Navigate to the base URL
    await page.goto(BASE_URL); // Use HTTPS instead of HTTP

    // Verify the page title
    await expect(page).toHaveTitle(/Example Domain/);

    // Verify the main heading text
    await expect(page.locator('h1')).toHaveText('Example Domain');
});
