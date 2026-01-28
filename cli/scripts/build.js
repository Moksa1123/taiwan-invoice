#!/usr/bin/env node

/**
 * Build script for taiwan-invoice-skill CLI
 * Ensures dist/ and assets/ are ready for publishing
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const DIST = path.join(ROOT, 'dist');
const ASSETS = path.join(ROOT, 'assets');

console.log('Building taiwan-invoice-skill...');

// Ensure dist exists
if (!fs.existsSync(DIST)) {
  console.error('Error: dist/ directory not found');
  process.exit(1);
}

// Ensure assets exist
if (!fs.existsSync(ASSETS)) {
  console.error('Error: assets/ directory not found');
  process.exit(1);
}

// Verify main entry point
const entryPoint = path.join(DIST, 'index.js');
if (!fs.existsSync(entryPoint)) {
  console.error('Error: dist/index.js not found');
  process.exit(1);
}

// Verify skill assets
const skillAssets = path.join(ASSETS, 'taiwan-invoice', 'SKILL.md');
if (!fs.existsSync(skillAssets)) {
  console.error('Error: assets/taiwan-invoice/SKILL.md not found');
  process.exit(1);
}

console.log('Build complete!');
console.log('  - dist/index.js');
console.log('  - assets/taiwan-invoice/');
