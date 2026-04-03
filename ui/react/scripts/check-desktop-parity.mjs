import { execSync } from 'node:child_process';

function run(label, command) {
  try {
    const output = execSync(command, { stdio: 'pipe', encoding: 'utf8' });
    console.log(`OK ${label}`);
    if (output.trim()) {
      console.log(output.trim());
    }
    return true;
  } catch (error) {
    console.error(`FAIL ${label}`);
    console.error(String(error.stdout || '').trim());
    console.error(String(error.stderr || '').trim());
    return false;
  }
}

console.log('Desktop vs Web parity quick check');

const checks = [
  run('web typecheck', 'npm run type-check'),
  run('web test suite', 'npm run test -- --run'),
  run('desktop environment', 'npm run tauri:info'),
  run('desktop rust check', 'cd src-tauri && cargo check'),
];

if (checks.every(Boolean)) {
  console.log('Parity baseline checks passed.');
  process.exit(0);
}

console.error('Parity baseline checks failed.');
process.exit(1);
