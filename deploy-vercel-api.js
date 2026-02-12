#!/usr/bin/env node

const VERCEL_TOKEN = process.env.VERCEL_TOKEN || '1rzNjBUZLOAKORAXpSsZqEUI';
const PROJECT_NAME = 'solshield-dashboard';

async function createDeployment() {
  console.log('🚀 Creating Vercel deployment from GitHub...\n');
  
  const deploymentPayload = {
    name: PROJECT_NAME,
    gitSource: {
      type: 'github',
      repo: 'mgnlia/colosseum-agent-hackathon',
      ref: 'main',
    },
    projectSettings: {
      framework: 'nextjs',
      buildCommand: 'npm run build',
      outputDirectory: '.next',
      installCommand: 'npm install',
      rootDirectory: 'dashboard',
    },
    target: 'production',
  };

  try {
    const response = await fetch('https://api.vercel.com/v13/deployments', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${VERCEL_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(deploymentPayload),
    });

    const data = await response.json();
    
    if (!response.ok) {
      console.error('❌ Deployment failed:', data);
      process.exit(1);
    }

    console.log('✅ Deployment created successfully!');
    console.log('   ID:', data.id);
    console.log('   URL:', `https://${data.url}`);
    console.log('   Status:', data.readyState);
    console.log('\n🌐 Production URL: https://solshield-dashboard.vercel.app');
    console.log('\n⏳ Building... This may take a few minutes.');
    
    // Poll for completion
    await pollDeployment(data.id);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

async function pollDeployment(deploymentId) {
  const maxAttempts = 30;
  let attempts = 0;
  
  while (attempts < maxAttempts) {
    attempts++;
    await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
    
    try {
      const response = await fetch(`https://api.vercel.com/v13/deployments/${deploymentId}`, {
        headers: {
          'Authorization': `Bearer ${VERCEL_TOKEN}`,
        },
      });
      
      const data = await response.json();
      console.log(`\n📊 Check ${attempts}/${maxAttempts}: ${data.readyState}`);
      
      if (data.readyState === 'READY') {
        console.log('\n✅ Deployment is READY!');
        console.log('🌐 Live URL:', `https://${data.url}`);
        console.log('🌐 Production URL: https://solshield-dashboard.vercel.app');
        return;
      } else if (data.readyState === 'ERROR') {
        console.log('\n❌ Deployment failed!');
        console.log('Error:', data.error);
        process.exit(1);
      }
    } catch (error) {
      console.error('Error polling:', error.message);
    }
  }
  
  console.log('\n⏰ Timeout waiting for deployment. Check Vercel dashboard for status.');
}

createDeployment();
