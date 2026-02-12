#!/usr/bin/env node
/**
 * Deploy to Vercel using the REST API with Node.js native fetch
 * No curl needed - uses built-in fetch (Node 18+)
 */
import { readFileSync, readdirSync, statSync, existsSync } from 'fs';
import { join, relative, extname } from 'path';

const VERCEL_TOKEN = process.env.VERCEL_TOKEN || '1rzNjBUZLOAKORAXpSsZqEUI';
const PROJECT_DIR = join(process.cwd(), 'dashboard');

// Recursively collect all files
function collectFiles(dir, base = dir) {
  const files = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const rel = relative(base, full);
    
    // Skip these directories
    if (['node_modules', '.git', '.next', '.vercel', '__pycache__'].includes(entry)) continue;
    
    const stat = statSync(full);
    if (stat.isDirectory()) {
      files.push(...collectFiles(full, base));
    } else if (stat.size < 5 * 1024 * 1024) { // Skip files > 5MB
      files.push({
        file: rel,
        data: readFileSync(full).toString('base64'),
        encoding: 'base64'
      });
    }
  }
  return files;
}

async function deploy() {
  console.log('📦 Collecting files from', PROJECT_DIR);
  
  if (!existsSync(PROJECT_DIR)) {
    console.error('❌ Dashboard directory not found at', PROJECT_DIR);
    process.exit(1);
  }
  
  const files = collectFiles(PROJECT_DIR);
  console.log(`📁 Found ${files.length} files`);
  
  // Read package.json to detect framework
  const pkgPath = join(PROJECT_DIR, 'package.json');
  let framework = 'nextjs';
  if (existsSync(pkgPath)) {
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    console.log(`📋 Project: ${pkg.name || 'unknown'}`);
  }
  
  const payload = {
    name: 'solshield-dashboard',
    files: files,
    projectSettings: {
      framework: framework,
      buildCommand: 'npm run build',
      outputDirectory: '.next',
      installCommand: 'npm install'
    },
    target: 'production'
  };
  
  console.log('🚀 Deploying to Vercel...');
  console.log(`   Payload size: ~${Math.round(JSON.stringify(payload).length / 1024)}KB`);
  
  try {
    const response = await fetch('https://api.vercel.com/v13/deployments', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${VERCEL_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      console.error('❌ Deployment failed:', response.status);
      console.error(JSON.stringify(data, null, 2));
      process.exit(1);
    }
    
    console.log('\n✅ DEPLOYMENT SUCCESSFUL!');
    console.log(`🌐 Preview URL: https://${data.url}`);
    if (data.alias && data.alias.length > 0) {
      console.log(`🌐 Production URL: https://${data.alias[0]}`);
    }
    console.log(`📊 Deployment ID: ${data.id}`);
    console.log(`📊 Project ID: ${data.projectId}`);
    console.log(`📊 Status: ${data.readyState || data.status}`);
    
  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

deploy();
