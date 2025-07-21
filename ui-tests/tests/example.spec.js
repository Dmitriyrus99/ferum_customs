const { test, expect } = require("@playwright/test");

test("homepage has correct title", async ({ page }) => {
	await page.goto("http://example.com");
	await expect(page).toHaveTitle(/Example Domain/);
});
