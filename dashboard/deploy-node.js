#!/usr/bin/env node
/**
 * Vercel Deployment Script using Node.js
 * Deploys the SolShield dashboard to Vercel production
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const VERCEL_TOKEN = '1rzNjBUZLOAKORAXpSsZqEUI';
const PROJECT_NAME = 'solshield-dashboard';

// Directories to skip
const SKIP_DIRS = new Set([
  'node_modules', '.next', '.git', '__pycache__', 
  '.vercel', 'dist', 'build', '.cache', '.vscode',
  '.idea', 'coverage', '.DS_Store', 'deploy_vercel.py',
  'deploy-node.js'
]);

function shouldSkip(filePath) {
  const parts = filePath.split(path.sep);
  // Skip if any parent directory is in SKIP_DIRS
  if (parts.some(part => SKIP_DIRS.has(part))) {
    return true;
  }
  // Skip hidden files except specific ones
  if (parts.some(part => part.startsWith('.') && !part.match(/^\.(env\.example|gitignore)$/))) {
    return true;
  }
  return false;
}

function collectFiles(directory) {
  const files = [];
  
  console.log(`📂 Scanning directory: ${directory}`);
  
  function walk(dir, baseDir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.relative(baseDir, fullPath);
      
      if (shouldSkip(relativePath)) {
        continue;
      }
      
      if (entry.isDirectory()) {
        walk(fullPath, baseDir);
      } else if (entry.isFile()) {
        try {
          const content = fs.readFileSync(fullPath);
          const encoded = content.toString('base64');
          
          files.push({
            file: relativePath.replace(/\\/g, '/'),
            data: encoded,
            encoding: 'base64'
          });
          
          console.log(`  ✓ ${relativePath} (${content.length} bytes)`);
        } catch (err) {
          console.log(`  ✗ Error reading ${relativePath}: ${err.message}`);
        }
      }
    }
  }
  
  walk(directory, directory);
  return files;
}

function deployToVercel(files) {
  return new Promise((resolve, reject) => {
    console.log(`\n🚀 Deploying ${files.length} files to Vercel...`);
    
    const payload = JSON.stringify({
      name: PROJECT_NAME,
      files: files,
      projectSettings: {
        framework: 'nextjs',
        buildCommand: 'npm run build',
        installCommand: 'npm install',
        outputDirectory: '.next'
      },
      target: 'production'
    });
    
    const options = {
      hostname: 'api.vercel.com',
      port: 443,
      path: '/v13/deployments',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${VERCEL_TOKEN}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    };
    
    console.log('📡 Sending deployment request to Vercel API...');
    
    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          
          if (res.statusCode === 200 || res.statusCode === 201) {
            const deploymentUrl = result.url;
            if (deploymentUrl) {
              const fullUrl = `https://${deploymentUrl}`;
              console.log(`\n✅ DEPLOYMENT SUCCESSFUL!`);
              console.log(`🌐 Live URL: ${fullUrl}`);
              console.log(`📊 Deployment ID: ${result.id}`);
              console.log(`🔗 Inspector: https://vercel.com/deployments/${result.id}`);
              resolve(fullUrl);
            } else {
              console.log(`\n⚠️  Deployment created but no URL returned`);
              console.log(`Response: ${JSON.stringify(result, null, 2)}`);
              resolve(null);
            }
          } else {
            console.log(`\n❌ HTTP Error ${res.statusCode}`);
            console.log(`Response: ${data}`);
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          }
        } catch (err) {
          console.log(`\n❌ Error parsing response: ${err.message}`);
          console.log(`Raw response: ${data}`);
          reject(err);
        }
      });
    });
    
    req.on('error', (err) => {
      console.log(`\n❌ Request error: ${err.message}`);
      reject(err);
    });
    
    req.write(payload);
    req.end();
  });
}

async function main() {
  console.log('='.repeat(60));
  console.log('🛡️  SolShield Dashboard - Vercel Deployment');
  console.log('='.repeat(60));
  
  const dashboardDir = __dirname;
  console.log(`\n📍 Dashboard directory: ${dashboardDir}`);
  
  // Collect files
  const files = collectFiles(dashboardDir);
  
  if (files.length === 0) {
    console.log('\n❌ No files found to deploy!');
    process.exit(1);
  }
  
  console.log(`\n📦 Total files to deploy: ${files.length}`);
  
  // Deploy to Vercel
  try {
    const url = await deployToVercel(files);
    
    if (url) {
      console.log('\n' + '='.repeat(60));
      console.log('🎉 SUCCESS! Dashboard is live at:');
      console.log(`   ${url}`);
      console.log('='.repeat(60));
      process.exit(0);
    } else {
      console.log('\n❌ Deployment failed. Check errors above.');
      process.exit(1);
    }
  } catch (err) {
    console.log(`\n❌ Deployment failed: ${err.message}`);
    process.exit(1);
  }
}

main();
