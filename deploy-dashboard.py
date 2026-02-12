#!/usr/bin/env python3
"""Deploy SolShield dashboard to Vercel without curl dependency."""

import os
import sys
import tarfile
import tempfile
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def create_tarball(source_dir, output_path):
    """Create a gzipped tarball excluding unnecessary files."""
    print("📦 Creating tarball...")
    
    exclude_patterns = {
        'node_modules', '.git', '.next', '.vercel', 
        '.env.local', 'dist', 'build', '__pycache__',
        '.DS_Store', '*.pyc', '.pytest_cache'
    }
    
    def filter_func(tarinfo):
        # Exclude based on patterns
        for pattern in exclude_patterns:
            if pattern in tarinfo.name:
                return None
        return tarinfo
    
    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(source_dir, arcname=".", filter=filter_func)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ Tarball created: {output_path} ({file_size:.2f} MB)")
    return output_path

def upload_to_vercel(tarball_path):
    """Upload tarball to Vercel deployment service."""
    print("📤 Uploading to Vercel deployment service...")
    
    url = "https://skill-deploy.vercel.app/api/deploy"
    
    # Read tarball
    with open(tarball_path, 'rb') as f:
        tarball_data = f.read()
    
    print(f"   Tarball size: {len(tarball_data) / (1024 * 1024):.2f} MB")
    
    # Create multipart form data manually
    boundary = '----WebKitFormBoundary' + os.urandom(16).hex()
    
    body = []
    body.append(f'--{boundary}'.encode())
    body.append(b'Content-Disposition: form-data; name="framework"')
    body.append(b'')
    body.append(b'nextjs')
    
    body.append(f'--{boundary}'.encode())
    body.append(b'Content-Disposition: form-data; name="file"; filename="project.tar.gz"')
    body.append(b'Content-Type: application/gzip')
    body.append(b'')
    body.append(tarball_data)
    body.append(f'--{boundary}--'.encode())
    body.append(b'')
    
    body_bytes = b'\r\n'.join(body)
    
    # Create request
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body_bytes))
    }
    
    req = Request(url, data=body_bytes, headers=headers, method='POST')
    
    print("   Sending request...")
    try:
        with urlopen(req, timeout=300) as response:
            response_data = response.read().decode('utf-8')
            print(f"   Response status: {response.status}")
            result = json.loads(response_data)
            return result
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP {e.code}: {error_body}")
    except URLError as e:
        raise Exception(f"URL Error: {e.reason}")

def main():
    print("🚀 Starting SolShield Dashboard deployment to Vercel...")
    print()
    
    # Determine project path - we're already in colosseum-agent-hackathon
    project_path = Path("dashboard")
    
    if not project_path.exists():
        # Try from workspace root
        project_path = Path.cwd() / "colosseum-agent-hackathon" / "dashboard"
    
    if not project_path.exists():
        print(f"❌ Project not found at: {project_path}")
        print(f"   Current directory: {Path.cwd()}")
        sys.exit(1)
    
    print(f"📂 Project path: {project_path.absolute()}")
    
    # Create temporary tarball
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
        tarball_path = tmp.name
    
    try:
        # Create tarball
        create_tarball(str(project_path), tarball_path)
        
        # Upload to Vercel
        result = upload_to_vercel(tarball_path)
        
        # Display results
        print()
        print("=" * 60)
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)
        
        # Try to extract URL from various possible response formats
        url = (result.get('url') or 
               result.get('deploymentUrl') or 
               result.get('previewUrl') or
               result.get('preview_url') or
               result.get('deployment_url'))
        
        if url:
            # Ensure URL has protocol
            if not url.startswith('http'):
                url = f"https://{url}"
            print()
            print(f"🌐 LIVE URL: {url}")
            print()
        else:
            print()
            print("⚠️  URL not found in standard fields")
            print()
        
        print("Full response:")
        print(json.dumps(result, indent=2))
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ DEPLOYMENT FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        if os.path.exists(tarball_path):
            os.unlink(tarball_path)
            print(f"\n🧹 Cleaned up temporary tarball")

if __name__ == "__main__":
    sys.exit(main())
