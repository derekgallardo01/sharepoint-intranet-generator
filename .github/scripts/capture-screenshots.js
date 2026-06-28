// Captures PNG screenshots of the live Pages demo and writes them under
// docs/screenshots/. Run by .github/workflows/screenshots.yml.
//
// DEMO_BASE env var is the root URL of the Pages site (no trailing slash).

const { chromium } = require("playwright");
const fs = require("fs");

const BASE = process.env.DEMO_BASE;
if (!BASE) {
  console.error("DEMO_BASE env var is required.");
  process.exit(1);
}

const OUT = "docs/screenshots";

// Pages to capture for this repo: { path: relative URL, name: file slug }
const CAPTURES = [
  { path: "/",                       name: "01-landing" },
  { path: "/meridian/index.html",    name: "02-meridian-home" },
  { path: "/meridian/hr.html",       name: "03-meridian-hr-section" },
  { path: "/meridian/faq.html",      name: "04-meridian-faq" },
  { path: "/meridian/people.html",   name: "05-meridian-people" },
  { path: "/acme/index.html",        name: "06-acme-home" },
  { path: "/acme/quality.html",      name: "07-acme-quality-section" },
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    deviceScaleFactor: 2,  // crisp on retina/zoomed views
  });
  const page = await ctx.newPage();

  for (const c of CAPTURES) {
    const url = BASE + c.path;
    const file = `${OUT}/${c.name}.png`;
    console.log(`-> ${url}`);
    await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    await page.screenshot({ path: file, fullPage: true });
    const size = fs.statSync(file).size;
    console.log(`   wrote ${file} (${(size/1024).toFixed(1)} KB)`);
  }

  await browser.close();
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
