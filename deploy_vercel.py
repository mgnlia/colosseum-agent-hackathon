#!/usr/bin/env python3
"""Deploy SolShield Dashboard to Vercel using REST API. No external deps needed."""

import json
import os
import sys
import base64
import urllib.request
import urllib.error
import tarfile
import io
import time
from pathlib import Path

VERCEL_TOKEN = os.environ.get("VERCEL_TOKEN", "1rzNjBUZLOAKORAXpSsZqEUI")
API = "https://api.vercel.com"
DASHBOARD_DIR = Path(__file__).parent / "dashboard"

SKIP_DIRS = {"node_modules", ".next", ".git", ".vercel", "__pycache__", ".turbo"}
SKIP_EXTS = {".pyc", ".pyo", ".so", ".dylib"}

def collect_files(root: Path):
    """Collect all deployable files."""
    files = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        # Skip unwanted directories
        parts = path.relative_to(root).parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        # Skip binary/large files
        if path.suffix in SKIP_EXTS:
            continue
        if path.stat().st_size > 4 * 1024 * 1024:
            continue
        
        rel = str(path.relative_to(root))
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        files.append({"file": rel, "data": data, "encoding": "base64"})
    return files

def api_call(method, endpoint, data=None):
    """Make authenticated Vercel API call."""
    url = f"{API}{endpoint}"
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"API Error {e.code}: {err_body}", file=sys.stderr)
        raise

def deploy():
    print(f"📦 Collecting files from {DASHBOARD_DIR}...")
    if not DASHBOARD_DIR.exists():
        print(f"❌ Dashboard directory not found: {DASHBOARD_DIR}")
        sys.exit(1)
    
    files = collect_files(DASHBOARD_DIR)
    print(f"   Found {len(files)} files")
    
    # Calculate total payload size
    payload_size = sum(len(f["data"]) for f in files)
    print(f"   Payload size: {payload_size / 1024 / 1024:.1f} MB")
    
    if payload_size > 90 * 1024 * 1024:
        print("⚠️  Payload too large, filtering to essential files only...")
        essential_exts = {".ts", ".tsx", ".js", ".jsx", ".json", ".css", ".html", ".md", ".svg", ".png", ".ico", ".mjs"}
        files = [f for f in files if Path(f["file"]).suffix in essential_exts or f["file"] in ["next.config.js", "next.config.mjs", "tsconfig.json", "package.json", "tailwind.config.ts", "tailwind.config.js", "postcss.config.js", "postcss.config.mjs"]]
        payload_size = sum(len(f["data"]) for f in files)
        print(f"   Filtered to {len(files)} files ({payload_size / 1024 / 1024:.1f} MB)")

    print("🚀 Creating Vercel deployment...")
    deploy_data = {
        "name": "solshield-dashboard",
        "files": files,
        "projectSettings": {
            "framework": "nextjs",
            "buildCommand": "npm run build",
            "outputDirectory": ".next",
            "installCommand": "npm install",
        },
        "target": "production",
    }
    
    result = api_call("POST", "/v13/deployments", deploy_data)
    
    deploy_id = result.get("id", "unknown")
    deploy_url = result.get("url", "unknown")
    print(f"✅ Deployment created!")
    print(f"   ID: {deploy_id}")
    print(f"   URL: https://{deploy_url}")
    
    # Poll for completion
    print("\n⏳ Waiting for build...")
    for i in range(60):
        time.sleep(5)
        status_data = api_call("GET", f"/v13/deployments/{deploy_id}")
        state = status_data.get("readyState", status_data.get("status", "UNKNOWN"))
        print(f"   [{i*5}s] Status: {state}")
        
        if state == "READY":
            final_url = status_data.get("url", deploy_url)
            alias = status_data.get("alias", [])
            print(f"\n🎉 DEPLOYMENT LIVE!")
            print(f"   🌐 URL: https://{final_url}")
            if alias:
                print(f"   🔗 Aliases: {', '.join(f'https://{a}' for a in alias)}")
            return final_url
        elif state in ("ERROR", "CANCELED"):
            print(f"\n❌ Deployment failed: {state}")
            errors = status_data.get("errorMessage", "No error details")
            print(f"   Error: {errors}")
            sys.exit(1)
    
    print(f"\n⚠️ Timed out. Check: https://vercel.com/dashboard")
    return deploy_url

if __name__ == "__main__":
    url = deploy()
    print(f"\n{'='*50}")
    print(f"SOLSHIELD DASHBOARD: https://{url}")
    print(f"{'='*50}")
