// @ts-check
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
	use: {
		baseURL: "http://localhost:8000", // Consider using HTTPS in production
		headless: true,
	},
	testDir: "./tests", // Ensure the path is relative and correct
});
