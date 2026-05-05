const fs = require('fs');
const path = require('path');

class ElyonReporter {
    constructor() {
        this.pendingRequests = [];
    }

    onTestEnd(test, result) {
        console.log('ELYON REPORTER TRIGGERED');

        if (result.status === 'passed') return;

        const promise = this.sendFailureToElyon(test, result);
        this.pendingRequests.push(promise);
    }

    async onEnd() {
        await Promise.all(this.pendingRequests);
    }

    async sendFailureToElyon(test, result) {

        const screenshot = result.attachments.find(a => a.name === 'screenshot');

        let testCode = '';

        try {
            testCode = fs.readFileSync(test.location.file, 'utf-8');
        } catch (err) {
            testCode = '';
        }

        function extractFailureLocation(stack) {
            if (!stack) return null;

            const match = stack.match(/(.*\.spec\.(ts|js)):(\d+):(\d+)/);

            if (!match) return null;

            return {
                file: match[1],
                line: Number(match[3]),
                column: Number(match[4])
            };
        }

        const failureLocation = extractFailureLocation(result.error?.stack || '');

        const payload = {
            testTitle: test.title,
            file: test.location.file,
            line: test.location.line,
            status: result.status,
            errorMessage: result.error?.message || '',
            errorStack: result.error?.stack || '',
            screenshotPath: screenshot?.path || null,
            testCode: testCode,
            failureLocation: failureLocation
        };

        const outDir = path.join(process.cwd(), '..', 'elyon-failures');
        fs.mkdirSync(outDir, { recursive: true });

        const fileName = `${Date.now()}-${test.title.replace(/[^a-z0-9]/gi, '_')}.json`;

        fs.writeFileSync(
            path.join(outDir, fileName),
            JSON.stringify(payload, null, 2)
        );

        try {
            console.log('Sending failure to Elyon backend...');

            const response = await fetch('http://127.0.0.1:8000/analyze-playwright-failure', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            console.log('\n================ ELYON AI ANALYSIS ================');
            console.log(`Model: ${data.model_used.toUpperCase()} (Vision Enabled)\n`);
            console.log(data.analysis);
            console.log('================================================\n');
        } catch (err) {
            console.log('\nElyon analyzer request failed.');
            console.log(err.message);
        }
    }
}

module.exports = ElyonReporter;