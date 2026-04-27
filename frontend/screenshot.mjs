import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 800 });
  
  // Go to Deepfake media page
  await page.goto('http://localhost:3000/analyze/email');
  await page.waitForTimeout(1000);
  
  // Take screenshot of empty page
  await page.screenshot({ path: 'frontend_initial.png' });
  
  // Type a suspicious keyword so it catches it
  await page.fill('textarea', 'this is an urgent message asking for your password');
  
  // Click scan
  await page.click('button:has-text("INITIATE NEURAL SCAN")');
  
  // Wait for the 3.5s simulation to complete and the dossier to render
  await page.waitForTimeout(4500);
  
  // Scroll down slightly so the dossier is centered
  await page.evaluate(() => window.scrollBy(0, 300));
  
  // Take screenshot of completed report
  await page.screenshot({ path: 'frontend_dossier.png' });
  
  await browser.close();
  console.log("Screenshots captured successfully");
})();
