const { test, expect } = require("@playwright/test");

test("homepage has correct title", async ({ page }) => {
	await page.goto("https://example.com"); // Use HTTPS instead of HTTP
	await expect(page).toHaveTitle(/Example Domain/);
});
