// Smoke test the full plan CRUD flow:
// 1. Navigate to /plans
// 2. Click New Plan
// 3. Fill in name + add a target item
// 4. Submit
// 5. See it in the list
// 6. Delete it
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newContext().then((c) => c.newPage());

  const failures = [];
  page.on('pageerror', (err) => failures.push(`pageerror: ${err.message}`));
  page.on('requestfailed', (req) => {
    if (req.url().includes('/api/')) {
      failures.push(`requestfailed: ${req.method()} ${req.url()}`);
    }
  });

  // 1. Start at plans list
  await page.goto('http://localhost:4300/plans', { waitUntil: 'networkidle' });
  console.log('On plans list. H1:', await page.locator('h1').first().textContent());

  // 2. Click the New Plan link (routerLink)
  await page.click('a:has-text("New Plan")');
  await page.waitForURL('**/plans/new');
  console.log('On new plan page. H1:', await page.locator('h1').textContent());

  // 3. Fill in the form
  await page.fill('input[name="name"]', 'Playwright Test Plan');
  await page.fill('textarea[name="notes"]', 'Created by smoke test');

  // Search for a target item and add it
  await page.fill('input[name="search"]', 'Black Cleaver');
  await page.waitForSelector('.search-results button');
  await page.click('.search-results button:has-text("Black Cleaver")');

  // Confirm chip appeared
  const chipText = await page.locator('.target-chip').first().textContent();
  console.log('Added target chip:', chipText?.replace(/\s+/g, ' ').trim());

  // 4. Submit
  await Promise.all([
    page.waitForURL('**/plans'),
    page.click('button[type="submit"]'),
  ]);
  console.log('Returned to plans list after save.');

  // 5. Verify in list
  const planCards = await page.locator('.plan-card').count();
  const firstName = await page.locator('.plan-name').first().textContent();
  console.log(`Plans in list: ${planCards}; first plan name: "${firstName}"`);

  // 6. Delete it (confirm() dialog accept)
  page.once('dialog', (d) => d.accept());
  await page.locator('.btn-delete').first().click();
  await page.waitForTimeout(500);
  const remaining = await page.locator('.plan-card').count();
  console.log(`Plans after delete: ${remaining}`);

  if (failures.length) {
    console.log('\n--- Failures ---');
    failures.forEach((f) => console.log(f));
    process.exitCode = 1;
  } else {
    console.log('\nAll flows passed with no errors.');
  }

  await browser.close();
})();
