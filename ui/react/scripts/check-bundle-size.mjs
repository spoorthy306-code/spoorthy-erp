import { createGzip } from 'node:zlib';
import { createReadStream, readdirSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { pipeline } from 'node:stream/promises';
import { Writable } from 'node:stream';
import budgetConfig from '../bundle-budget.config.js';

const distAssetsDir = path.resolve('dist', 'assets');
const reportPath = path.resolve('bundle-report.txt');

function formatKiB(bytes) {
  return Number((bytes / 1024).toFixed(2));
}

async function gzipSize(filePath) {
  let total = 0;
  const counter = new Writable({
    write(chunk, _encoding, callback) {
      total += chunk.length;
      callback();
    },
  });

  await pipeline(createReadStream(filePath), createGzip(), counter);
  return total;
}

function findChunkSize(chunkSizes, name) {
  const match = Object.entries(chunkSizes).find(([fileName]) => fileName.startsWith(`${name}-`));
  return match?.[1] ?? 0;
}

async function main() {
  const files = readdirSync(distAssetsDir)
    .filter((file) => file.endsWith('.js') || file.endsWith('.css'))
    .sort();

  const chunkSizes = {};
  let totalGzip = 0;

  for (const fileName of files) {
    const filePath = path.join(distAssetsDir, fileName);
    statSync(filePath);
    const gzippedBytes = await gzipSize(filePath);
    const gzippedKb = formatKiB(gzippedBytes);
    chunkSizes[fileName] = gzippedKb;
    totalGzip += gzippedKb;
  }

  const lines = [];
  lines.push('Bundle Size Analysis');
  lines.push('====================');
  lines.push('');

  for (const [fileName, sizeKb] of Object.entries(chunkSizes)) {
    lines.push(`${fileName}: ${sizeKb.toFixed(2)} kB gzip`);
  }

  lines.push('');
  lines.push(`Total gzip size: ${totalGzip.toFixed(2)} kB`);
  lines.push(`Budget: ${budgetConfig.totalBudgetSizeKb.toFixed(2)} kB`);
  lines.push('');

  let hasError = false;
  for (const budget of budgetConfig.budgets) {
    const actualSize = findChunkSize(chunkSizes, budget.name);
    const status = actualSize <= budget.maxSizeKb ? 'OK' : 'FAIL';
    lines.push(`${status} ${budget.name}: ${actualSize.toFixed(2)} / ${budget.maxSizeKb.toFixed(2)} kB`);
    if (actualSize > budget.maxSizeKb) {
      hasError = true;
    }
  }

  lines.push('');
  if (totalGzip > budgetConfig.totalBudgetSizeKb) {
    lines.push(`FAIL total: exceeded by ${(totalGzip - budgetConfig.totalBudgetSizeKb).toFixed(2)} kB`);
    hasError = true;
  } else {
    lines.push(`OK total: headroom ${(budgetConfig.totalBudgetSizeKb - totalGzip).toFixed(2)} kB`);
  }

  const report = lines.join('\n');
  console.log(report);
  writeFileSync(reportPath, `${report}\n`, 'utf8');

  if (hasError && budgetConfig.onBudgetExceeded === 'error') {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
