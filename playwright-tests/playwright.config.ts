import { defineConfig } from '@playwright/test';

export default defineConfig({
    testDir: './tests',

    reporter: [
        ['list'],
        ['./elyon-reporter.js']
    ],

    use: {
        screenshot: 'only-on-failure',
        trace: 'retain-on-failure',
        video: 'retain-on-failure',
    },
});