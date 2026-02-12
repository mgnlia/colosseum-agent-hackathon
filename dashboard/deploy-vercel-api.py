#!/usr/bin/env python3
"""Deploy dashboard to Vercel using the REST API with urllib (no curl needed)."""

import json
import os
import sys
import urllib.request
import urllib.error
import base64
import tarfile
import io
import glob

VERCEL_TOKEN = "1rzNjBUZLOAKORAXpSsZqEUI"
VERCEL_API = "https://api.vercel.com"

def read_file_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def collect_files(root_dir):
    """Collect all files for deployment, excluding unnecessary dirs."""
    files = []
    exclude_dirs = {'.next', 'node_modules', '.git', '__pycache__', '.vercel'}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            relpath = os.path.relpath(filepath, root_dir)
            try:
                content = read_file_bytes(filepath)
                files.append({
                    "file": relpath,
                    "data": base64.b64encode(content).decode('utf-8'),
                    "encoding": "base64"
                })
            except Exception as e:
                print(f"  Skipping {relpath}: {e}")
    return files

def api_request(endpoint, method="GET", data=None):
    """Make a Vercel API request."""
    url = f"{VERCEL_API}{endpoint}"
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"API Error {e.code}: {body}")
        raise

def deploy():
    dashboard_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Deploying from: {dashboard_dir}")
    
    # Step 1: Collect files
    print("Collecting files...")
    files = collect_files(dashboard_dir)
    print(f"  Found {len(files)} files")
    
    if not files:
        print("ERROR: No files found!")
        sys.exit(1)
    
    # Step 2: Create deployment via Vercel API v13
    print("Creating Vercel deployment...")
    deploy_data = {
        "name": "solshield-dashboard",
        "files": files,
        "projectSettings": {
            "framework": "nextjs",
            "buildCommand": "npm run build",
            "outputDirectory": ".next",
            "installCommand": "npm install"
        },
        "target": "production"
    }
    
    result = api_request("/v13/deployments", method="POST", data=deploy_data)
    
    deploy_url = result.get("url", "unknown")
    deploy_id = result.get("id", "unknown")
    status = result.get("readyState", result.get("status", "unknown"))
    
    print(f"\n{'='*60}")
    print(f"🚀 DEPLOYMENT CREATED!")
    print(f"{'='*60}")
    print(f"  ID:     {deploy_id}")
    print(f"  URL:    https://{deploy_url}")
    print(f"  Status: {status}")
    print(f"{'='*60}")
    
    # Write URL to file for easy retrieval
    with open(os.path.join(dashboard_dir, ".vercel-url"), "w") as f:
        f.write(f"https://{deploy_url}")
    
    return deploy_url

if __name__ == "__main__":
    deploy()
