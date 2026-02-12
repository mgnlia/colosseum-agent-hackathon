#!/usr/bin/env node
/**
 * Deploy to Vercel using the REST API directly (no CLI needed).
 * Uses Node.js built-in fetch (Node 18+).
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, relative } from 'path';
import { execSync } from 'child_process';

const VERCEL_TOKEN = process.env.VERCEL_TOKEN || '1rzNjBUZLOAKORAXpSsZqEUI';
const API_BASE = 'https://api.vercel.com';

const headers = {
  'Authorization': `Bearer ${VERCEL_TOKEN}`,
  'Content-Type': 'application/json',
};

// Collect all files recursively, skipping node_modules, .next, .git
function collectFiles(dir, base = dir) {
  const files = [];
  for (const entry of readdirSync(dir)) {
    if (['node_modules', '.next', '.git', '.vercel', '__pycache__'].includes(entry)) continue;
    const fullPath = join(dir, entry);
    const stat = statSync(fullPath);
    if (stat.isDirectory()) {
      files.push(...collectFiles(fullPath, base));
    } else if (stat.size < 5 * 1024 * 1024) { // Skip files > 5MB
      const relativePath = relative(base, fullPath);
      const content = readFileSync(fullPath);
      files.push({
        file: relativePath,
        data: content.toString('base64'),
        encoding: 'base64',
      });
    }
  }
  return files;
}

async function deploy() {
  console.log('📦 Collecting dashboard files...');
  const projectDir = process.cwd();
  const files = collectFiles(projectDir);
  console.log(`Found ${files.length} files to deploy`);

  // Step 1: Create deployment
  console.log('🚀 Creating Vercel deployment...');
  const deployPayload = {
    name: 'solshield-dashboard',
    files: files,
    projectSettings: {
      framework: 'nextjs',
      buildCommand: 'npm run build',
      outputDirectory: '.next',
      installCommand: 'npm install',
    },
    target: 'production',
  };

  const response = await fetch(`${API_BASE}/v13/deployments`, {
    method: 'POST',
    headers,
    body: JSON.stringify(deployPayload),
  });

  const result = await response.json();

  if (!response.ok) {
    console.error('❌ Deployment failed:', JSON.stringify(result, null, 2));
    process.exit(1);
  }

  console.log('✅ Deployment created!');
  console.log(`📋 Deployment ID: ${result.id}`);
  console.log(`🌐 URL: https://${result.url}`);
  console.log(`🔗 Dashboard: https://vercel.com/dashboard`);
  
  // Poll for ready status
  console.log('\n⏳ Waiting for build to complete...');
  let status = result.readyState || result.status;
  let deployUrl = result.url;
  
  while (status === 'BUILDING' || status === 'INITIALIZING' || status === 'QUEUED') {
    await new Promise(r => setTimeout(r, 5000));
    const checkRes = await fetch(`${API_BASE}/v13/deployments/${result.id}`, { headers });
    const checkData = await checkRes.json();
    status = checkData.readyState || checkData.status;
    deployUrl = checkData.url || deployUrl;
    console.log(`  Status: ${status}...`);
  }

  if (status === 'READY') {
    console.log(`\n🎉 DEPLOYMENT LIVE!`);
    console.log(`🌐 Production URL: https://${deployUrl}`);
  } else {
    console.log(`\n⚠️ Final status: ${status}`);
    console.log(`🌐 URL: https://${deployUrl}`);
  }
}

deploy().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
