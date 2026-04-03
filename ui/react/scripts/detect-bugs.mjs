import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(process.cwd(), 'src');
const ALLOWED_EMAIL = 'spoorthy306@gmail.com';
const CODE_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx']);
const IGNORE_DIRS = new Set(['node_modules', 'dist', '.git', 'coverage', 'target']);

const EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
const PHONE_RE = /\b\d{10}\b|\b\d{3}[- ]?\d{3}[- ]?\d{4}\b/g;

const findings = [];

function isCodeFile(filePath) {
  return CODE_EXTENSIONS.has(path.extname(filePath));
}

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (IGNORE_DIRS.has(entry.name)) continue;
      walk(path.join(dir, entry.name));
      continue;
    }

    const absPath = path.join(dir, entry.name);
    if (!isCodeFile(absPath)) continue;

    const content = fs.readFileSync(absPath, 'utf8');
    const lines = content.split(/\r?\n/);

    lines.forEach((line, index) => {
      const emails = line.match(EMAIL_RE) ?? [];
      for (const email of emails) {
        if (email.toLowerCase() !== ALLOWED_EMAIL) {
          findings.push({
            type: 'HARDCODED_EMAIL',
            file: path.relative(process.cwd(), absPath),
            line: index + 1,
            value: email,
            fix: `Replace with ${ALLOWED_EMAIL}`,
          });
        }
      }

      const phones = line.match(PHONE_RE) ?? [];
      for (const phone of phones) {
        findings.push({
          type: 'HARDCODED_PHONE',
          file: path.relative(process.cwd(), absPath),
          line: index + 1,
          value: phone,
          fix: 'Remove or set to null',
        });
      }

      if (line.includes(': any') || line.includes('<any>')) {
        findings.push({
          type: 'ANY_TYPE',
          file: path.relative(process.cwd(), absPath),
          line: index + 1,
          value: line.trim(),
          fix: 'Replace with concrete type',
        });
      }

      if (line.includes('console.log') && !absPath.includes('.test.')) {
        findings.push({
          type: 'CONSOLE_LOG',
          file: path.relative(process.cwd(), absPath),
          line: index + 1,
          value: line.trim(),
          fix: 'Remove or gate behind debug logging',
        });
      }

      if (line.includes('TODO') || line.includes('FIXME')) {
        findings.push({
          type: 'TODO_COMMENT',
          file: path.relative(process.cwd(), absPath),
          line: index + 1,
          value: line.trim(),
          fix: 'Implement or remove marker',
        });
      }
    });
  }
}

if (!fs.existsSync(ROOT)) {
  console.error('Could not find src directory.');
  process.exit(1);
}

walk(ROOT);

const grouped = findings.reduce((acc, item) => {
  acc[item.type] = (acc[item.type] ?? 0) + 1;
  return acc;
}, {});

console.log('Bug scan finished.');
console.log(`Total findings: ${findings.length}`);
console.log('Summary by type:');
for (const [type, count] of Object.entries(grouped)) {
  console.log(`- ${type}: ${count}`);
}

if (findings.length > 0) {
  console.log('\nDetailed findings:');
  findings.forEach((item, idx) => {
    console.log(`${idx + 1}. ${item.type} ${item.file}:${item.line}`);
    console.log(`   value: ${item.value}`);
    console.log(`   fix: ${item.fix}`);
  });
}

const outputPath = path.resolve(process.cwd(), 'audit-findings.json');
fs.writeFileSync(outputPath, `${JSON.stringify({ generatedAt: new Date().toISOString(), findings }, null, 2)}\n`, 'utf8');
console.log(`\nWrote JSON findings: ${path.relative(process.cwd(), outputPath)}`);

if (findings.length > 0) {
  process.exitCode = 1;
}
