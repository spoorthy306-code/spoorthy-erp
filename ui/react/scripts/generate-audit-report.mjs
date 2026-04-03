import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

function run(command) {
  try {
    const out = execSync(command, { stdio: 'pipe', encoding: 'utf8' });
    return { success: true, output: out.trim() };
  } catch (error) {
    return {
      success: false,
      output: String(error.stdout || '').trim(),
      error: String(error.stderr || error.message || '').trim(),
    };
  }
}

const checks = {
  typeCheck: run('npm run type-check'),
  lint: run('npm run lint'),
  unitTests: run('npm run test -- --run'),
  build: run('npm run build'),
  componentInventory: run('node scripts/check-missing-components.mjs'),
  bugScan: run('node scripts/detect-bugs.mjs'),
};

const findingsPath = path.resolve(process.cwd(), 'audit-findings.json');
let findingsCount = 0;
if (fs.existsSync(findingsPath)) {
  try {
    const parsed = JSON.parse(fs.readFileSync(findingsPath, 'utf8'));
    findingsCount = Array.isArray(parsed.findings) ? parsed.findings.length : 0;
  } catch {
    findingsCount = -1;
  }
}

const report = {
  generatedAt: new Date().toISOString(),
  checks,
  summary: {
    allChecksPassed: Object.values(checks).every((item) => item.success),
    bugFindings: findingsCount,
  },
};

const reportPath = path.resolve(process.cwd(), 'audit-report.json');
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
console.log(`Audit report written to ${path.relative(process.cwd(), reportPath)}`);
if (!report.summary.allChecksPassed) {
  process.exitCode = 1;
}
