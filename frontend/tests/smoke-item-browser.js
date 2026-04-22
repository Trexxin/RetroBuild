// Smoke test: navigate to the Item Browser and verify items load.
// Captures console messages, network failures, and the final DOM state.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  const consoleMessages = [];
  const failedRequests = [];

  page.on('console', (msg) => {
    consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
  });

  page.on('requestfailed', (req) => {
    failedRequests.push(`${req.method()} ${req.url()} — ${req.failure()?.errorText}`);
  });

  page.on('response', (resp) => {
    if (resp.url().includes('/api/')) {
      consoleMessages.push(`[network] ${resp.status()} ${resp.url()}`);
    }
  });

  await page.goto('http://localhost:4300/items', { waitUntil: 'networkidle' });

  // Give Angular a moment to render after network settles.
  await page.waitForTimeout(500);

  const cardCount = await page.locator('app-item-card').count();
  const errorText = await page.locator('.error').textContent().catch(() => null);
  const bodyText = (await page.locator('.page').textContent()) || '';

  console.log('--- Summary ---');
  console.log('Item cards rendered:', cardCount);
  console.log('Error banner:', errorText);
  console.log('Page text snippet:', bodyText.slice(0, 200).replace(/\s+/g, ' '));
  console.log('\n--- Console/network ---');
  consoleMessages.forEach((m) => console.log(m));
  console.log('\n--- Failed requests ---');
  failedRequests.forEach((m) => console.log(m));

  await browser.close();
})();
