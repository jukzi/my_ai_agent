const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    let cdn = 0, parts = 0;
    await page.route('**/agent.html', async route => {
      const response = await route.fetch();
      const html = await response.text();
      const marker = '    async function runPython(code, packages = []) {';
      assert.ok(html.includes(marker));
      await route.fulfill({ response, body: html.replace(marker, '    window.testRunPython = runPython;\n' + marker) });
    });
    await page.route('https://cdn.jsdelivr.net/**/scipy-*.whl', route => { cdn++; return route.abort('failed'); });
    await page.route('**/mirrors/**', route => { parts++; return route.continue(); });
    const run = () => page.evaluate(() => window.testRunPython('import scipy\nfrom scipy import sparse\nassert scipy.__version__ == "1.12.0"\nassert sparse.eye(3).nnz == 3', ['scipy']));
    await page.goto('http://localhost:8000/agent.html');
    await run();
    assert.ok(cdn > 0 && parts > 1);
    const first = [cdn, parts];
    await page.reload();
    await run();
    assert.deepEqual([cdn, parts], first);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
