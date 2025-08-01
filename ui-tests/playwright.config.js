// @ts-check
const { defineConfig } = require("@playwright/test");

const BASE_URL = process.env.BASE_URL || "http://localhost:8000"; // Use environment variable for flexibility

module.exports = defineConfig({
	use: {
		baseURL: BASE_URL, // Use environment variable for base URL
		headless: true, // Run tests in headless mode for CI/CD
	},
	testDir: "./tests", // Ensure the path is relative and correct
});
