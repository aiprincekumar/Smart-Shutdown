/**
 * Project Rules Health Sentinel
 * Validates canonical rules binary parity, UTF-8 BOM, size headroom, and code fences.
 * Adheres strictly to Universal Rule 28 (< 280 lines, fn <= 50 lines, nesting <= 3).
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

const GLOBAL_RULES_DIR = path.resolve('C:/Users/Atul Verma/.gemini/config/rules');
const LOCAL_RULES_DIR = path.resolve(projectRoot, '.agents/rules');
const RECOM_LIMIT = 20 * 1024; // 20 KB
const HARD_LIMIT = 24 * 1024;  // 24 KB
const isFixMode = process.argv.includes('--fix');

function computeMD5(filePath) {
  const buf = fs.readFileSync(filePath);
  return crypto.createHash('md5').update(buf).digest('hex');
}

function verifyBOM(filePath, isFix) {
  const buf = fs.readFileSync(filePath);
  const hasBOM = buf.length >= 3 && buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf;
  if (!hasBOM && isFix) {
    const bom = Buffer.from([0xef, 0xbb, 0xbf]);
    fs.writeFileSync(filePath, Buffer.concat([bom, buf]));
    return true;
  }
  return hasBOM;
}

function getRuleFileList() {
  const canonical = [
    'foundation_core.md',
    'special_operations_guide.md',
    'architecture_recommendation.md',
    'dynamic_departments_matrix.md',
    'dept_index.md',
    'master_rules_navigator.md',
    'PHASE_WISE_PROMPT_GENERATION_ARCHITECTURE.md',
    'CODE_MODULARITY_AND_SCALABLE_ARCHITECTURE.md'
  ];

  const archiveDir = path.join(LOCAL_RULES_DIR, 'departments_archive');
  const archiveFiles = fs.existsSync(archiveDir)
    ? fs.readdirSync(archiveDir).filter(f => f.endsWith('.md')).map(f => path.join('departments_archive', f))
    : [];

  return [...canonical, ...archiveFiles];
}

function checkFenceBalance(content) {
  const fences = content.match(/^```/gm);
  return !fences || fences.length % 2 === 0;
}

function runHealthChecks() {
  console.log('='.repeat(80));
  console.log('🛡️  SMART SHUTDOWN — RULES HEALTH & INTEGRITY SENTINEL');
  console.log('='.repeat(80));
  console.log(`Global Path : ${GLOBAL_RULES_DIR}`);
  console.log(`Local Path  : ${LOCAL_RULES_DIR}\n`);

  if (!fs.existsSync(LOCAL_RULES_DIR)) {
    console.error(`❌ Local rules directory missing: ${LOCAL_RULES_DIR}`);
    process.exit(1);
  }

  const files = getRuleFileList();
  let failures = 0;

  for (const relFile of files) {
    const localPath = path.join(LOCAL_RULES_DIR, relFile);
    const globalPath = path.join(GLOBAL_RULES_DIR, relFile);

    if (!fs.existsSync(localPath) || !fs.existsSync(globalPath)) {
      console.error(`❌ Missing rule file: ${relFile}`);
      failures++;
      continue;
    }

    let lHash = computeMD5(localPath);
    let gHash = computeMD5(globalPath);
    if (lHash !== gHash && isFixMode) {
      fs.copyFileSync(globalPath, localPath);
      lHash = computeMD5(localPath);
      console.log(`🔧 Repaired parity for: ${relFile}`);
    }

    if (lHash !== gHash) {
      console.error(`❌ Parity failure: ${relFile} (local=${lHash}, global=${gHash})`);
      failures++;
    }

    if (!verifyBOM(localPath, isFixMode)) {
      console.error(`❌ Missing UTF-8 BOM: ${relFile}`);
      failures++;
    }

    const stat = fs.statSync(localPath);
    if (stat.size > HARD_LIMIT) {
      console.error(`❌ Exceeds 24 KB ceiling: ${relFile} (${stat.size} bytes)`);
      failures++;
    }

    const content = fs.readFileSync(localPath, 'utf8');
    if (!checkFenceBalance(content)) {
      console.error(`❌ Unbalanced code fences: ${relFile}`);
      failures++;
    }
  }

  return { total: files.length, failures };
}

function main() {
  const { total, failures } = runHealthChecks();
  console.log('\n' + '-'.repeat(80));
  if (failures === 0) {
    console.log(`✅ All ${total} rules passed health checks (100% parity, BOM valid, within headroom)`);
    console.log('='.repeat(80));
    process.exit(0);
  } else {
    console.error(`💥 ${failures} rule health check failure(s) detected!`);
    console.log('='.repeat(80));
    process.exit(1);
  }
}

main();
