#!/usr/bin/env python3
"""
Vercel Deployment Script using REST API
Deploys the SolShield dashboard to Vercel production
"""

import os
import json
import base64
import urllib.request
import urllib.error
from pathlib import Path

# Configuration
VERCEL_TOKEN = "1rzNjBUZLOAKORAXpSsZqEUI"
VERCEL_API_URL = "https://api.vercel.com/v13/deployments"
PROJECT_NAME = "solshield-dashboard"

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.next', '.git', '__pycache__', 
    '.vercel', 'dist', 'build', '.cache', '.vscode',
    '.idea', 'coverage', '.DS_Store'
}

# File extensions to skip
SKIP_FILES = {'.pyc', '.pyo', '.so', '.dylib', '.dll'}

def should_skip(path):
    """Check if path should be skipped"""
    parts = Path(path).parts
    # Skip if any parent directory is in SKIP_DIRS
    if any(part in SKIP_DIRS for part in parts):
        return True
    # Skip if file extension is in SKIP_FILES
    if Path(path).suffix in SKIP_FILES:
        return True
    # Skip hidden files except .env.example
    if any(part.startswith('.') and part not in ['.env.example', '.gitignore'] for part in parts):
        return True
    return False

def collect_files(directory):
    """Collect all files from directory recursively"""
    files = []
    base_path = Path(directory).resolve()
    
    print(f"📂 Scanning directory: {base_path}")
    
    for root, dirs, filenames in os.walk(base_path):
        # Remove skip directories from dirs list to prevent walking into them
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for filename in filenames:
            file_path = Path(root) / filename
            
            # Get relative path from base
            try:
                rel_path = file_path.relative_to(base_path)
            except ValueError:
                continue
            
            # Skip if should be skipped
            if should_skip(str(rel_path)):
                continue
            
            # Read and encode file
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    encoded = base64.b64encode(content).decode('utf-8')
                    
                files.append({
                    "file": str(rel_path).replace('\\', '/'),  # Use forward slashes
                    "data": encoded,
                    "encoding": "base64"
                })
                print(f"  ✓ {rel_path} ({len(content)} bytes)")
            except Exception as e:
                print(f"  ✗ Error reading {rel_path}: {e}")
    
    return files

def deploy_to_vercel(files):
    """Deploy files to Vercel using REST API"""
    
    print(f"\n🚀 Deploying {len(files)} files to Vercel...")
    
    # Prepare payload
    payload = {
        "name": PROJECT_NAME,
        "files": files,
        "projectSettings": {
            "framework": "nextjs",
            "buildCommand": "npm run build",
            "installCommand": "npm install",
            "outputDirectory": ".next"
        },
        "target": "production"
    }
    
    # Prepare request
    data = json.dumps(payload).encode('utf-8')
    
    headers = {
        'Authorization': f'Bearer {VERCEL_TOKEN}',
        'Content-Type': 'application/json',
    }
    
    req = urllib.request.Request(
        VERCEL_API_URL,
        data=data,
        headers=headers,
        method='POST'
    )
    
    try:
        print("📡 Sending deployment request to Vercel API...")
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            # Extract deployment URL
            deployment_url = result.get('url')
            if deployment_url:
                full_url = f"https://{deployment_url}"
                print(f"\n✅ DEPLOYMENT SUCCESSFUL!")
                print(f"🌐 Live URL: {full_url}")
                print(f"📊 Deployment ID: {result.get('id')}")
                print(f"🔗 Inspector: https://vercel.com/deployments/{result.get('id')}")
                return full_url
            else:
                print(f"\n⚠️  Deployment created but no URL returned")
                print(f"Response: {json.dumps(result, indent=2)}")
                return None
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"\n❌ HTTP Error {e.code}: {e.reason}")
        print(f"Response: {error_body}")
        try:
            error_json = json.loads(error_body)
            if 'error' in error_json:
                print(f"Error details: {error_json['error']}")
        except:
            pass
        return None
    except urllib.error.URLError as e:
        print(f"\n❌ URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main deployment function"""
    print("=" * 60)
    print("🛡️  SolShield Dashboard - Vercel Deployment")
    print("=" * 60)
    
    # Get the dashboard directory
    script_dir = Path(__file__).parent.resolve()
    dashboard_dir = script_dir
    
    print(f"\n📍 Dashboard directory: {dashboard_dir}")
    
    if not dashboard_dir.exists():
        print(f"❌ Error: Directory not found: {dashboard_dir}")
        return 1
    
    # Collect files
    files = collect_files(dashboard_dir)
    
    if not files:
        print("\n❌ No files found to deploy!")
        return 1
    
    print(f"\n📦 Total files to deploy: {len(files)}")
    
    # Deploy to Vercel
    url = deploy_to_vercel(files)
    
    if url:
        print("\n" + "=" * 60)
        print(f"🎉 SUCCESS! Dashboard is live at:")
        print(f"   {url}")
        print("=" * 60)
        return 0
    else:
        print("\n❌ Deployment failed. Check errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
