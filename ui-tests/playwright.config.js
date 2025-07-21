// @ts-check
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
	use: {
		baseURL: "http://localhost:8000",
		headless: true,
	},
	testDir: "tests",
});
