// @ts-check
const { defineConfig } = require("@playwright/test");

/**
 * Playwright configuration for UI tests.
 * @type {import('@playwright/test').PlaywrightTestConfig}
 */
const config = {
	use: {
		baseURL: process.env.BASE_URL || "http://localhost:8000", // Use environment variable for flexibility
		headless: process.env.HEADLESS === 'true', // Configurable headless mode
	},
	testDir: "./tests", // Ensure the path is relative and correct
};

module.exports = defineConfig(config);
