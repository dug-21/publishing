// Runs axe-core against one or more local HTML files and fails on any
// violation of the WCAG 2.0, 2.1 and 2.2 level A and AA rules.
// Usage: node tools/a11y.mjs FILE.html [FILE.html ...]
import { createRequire } from 'node:module';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(process.env.NODE_PATH ? process.env.NODE_PATH + '/' : import.meta.url);
const { chromium } = require('playwright');
const { AxeBuilder } = require('@axe-core/playwright');

const TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];
const files = process.argv.slice(2);
if (files.length === 0) {
  console.error('usage: a11y.mjs FILE.html [FILE.html ...]');
  process.exit(2);
}

const browser = await chromium.launch({ args: ['--no-sandbox'] });
let failures = 0;
for (const file of files) {
  const page = await (await browser.newContext()).newPage();
  await page.goto(pathToFileURL(path.resolve(file)).href);
  const results = await new AxeBuilder({ page }).options({ rules: { 'target-size': { enabled: true } } }).withTags(TAGS).analyze();
  for (const violation of results.violations) {
    for (const node of violation.nodes) {
      failures += 1;
      console.log(`${file}: [${violation.id}] ${violation.help} (${violation.impact})`);
      console.log(`    element: ${node.target.join(' ')}`);
      console.log(`    fix: ${violation.helpUrl}`);
    }
  }
  console.log(`${file}: ${results.violations.length} violated rule(s), ${results.passes.length} passed`);
}
await browser.close();
if (failures > 0) {
  console.error(`${failures} accessibility violation(s)`);
  process.exit(1);
}
