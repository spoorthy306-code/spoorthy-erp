import { createGzip } from 'node:zlib';
import { createReadStream, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { pipeline } from 'node:stream/promises';
import { Writable } from 'node:stream';

const distAssetsDir = path.resolve('dist', 'assets');

function formatKiB(bytes) {
  return `${(bytes / 1024).toFixed(2)} kB`;
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

async function main() {
  const assetFiles = readdirSync(distAssetsDir)
    .filter((file) => file.endsWith('.js') || file.endsWith('.css'))
    .map((file) => path.join(distAssetsDir, file));

  let totalGzip = 0;

  console.log('Bundle asset sizes:');
  for (const assetPath of assetFiles.sort()) {
    const stat = statSync(assetPath);
    const gzipped = await gzipSize(assetPath);
    totalGzip += gzipped;
    console.log(`${path.basename(assetPath)}: ${formatKiB(stat.size)} raw | ${formatKiB(gzipped)} gzip`);
  }

  console.log(`Total gzip across JS/CSS assets: ${formatKiB(totalGzip)}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});