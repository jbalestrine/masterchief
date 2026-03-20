#!/usr/bin/env python3
"""
Demo script showing how to use the data upload API.

This script demonstrates:
1. Creating sample files
2. Uploading them via the API
3. Listing uploaded files
4. Getting statistics
5. Downloading and deleting files
"""

import requests
import json
import os
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8080/api/v1/data"
DEMO_DIR = Path("/tmp/upload_demo")


def setup_demo():
    """Create demo directory and sample files."""
    print("Setting up demo...")
    DEMO_DIR.mkdir(exist_ok=True)
    
    # Create sample training data
    training_data = {
        "commands": [
            {
                "name": "hello",
                "response": "Hello! I'm Echo, your DevOps assistant.",
                "examples": ["hello", "hi", "hey"]
            },
            {
                "name": "status",
                "response": "All systems operational.",
                "examples": ["status", "how are you", "system status"]
            }
        ]
    }
    
    with open(DEMO_DIR / "training_commands.json", "w") as f:
        json.dump(training_data, f, indent=2)
    
    # Create sample log file
    with open(DEMO_DIR / "sample.log", "w") as f:
        f.write("2026-01-12 23:00:00 INFO Application started\n")
        f.write("2026-01-12 23:01:00 INFO Processing request\n")
        f.write("2026-01-12 23:02:00 ERROR Connection timeout\n")
    
    # Create sample CSV
    with open(DEMO_DIR / "metrics.csv", "w") as f:
        f.write("timestamp,cpu_usage,memory_usage\n")
        f.write("2026-01-12 23:00:00,45.2,62.1\n")
        f.write("2026-01-12 23:01:00,48.5,63.8\n")
        f.write("2026-01-12 23:02:00,52.1,65.4\n")
    
    print(f"  Created {len(list(DEMO_DIR.glob('*')))} demo files in {DEMO_DIR}")


def upload_file(filepath, purpose="training", description=""):
    """Upload a file to the API."""
    url = f"{API_BASE}/upload"
    
    try:
        with open(filepath, "rb") as f:
            files = {"file": f}
            data = {
                "purpose": purpose,
                "description": description
            }
            
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 201:
                result = response.json()
                print(f"  ✓ Uploaded: {filepath.name}")
                print(f"    Category: {result['file']['category']}")
                print(f"    Hash: {result['file']['hash'][:16]}...")
                return result
            else:
                print(f"  ✗ Failed: {filepath.name}")
                print(f"    Error: {response.json().get('error', 'Unknown')}")
                return None
                
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Cannot connect to {API_BASE}")
        print(f"    Make sure the platform is running: python platform/app.py")
        return None
    except Exception as e:
        print(f"  ✗ Error uploading {filepath.name}: {e}")
        return None


def list_files(purpose=None):
    """List uploaded files."""
    url = f"{API_BASE}/files"
    if purpose:
        url += f"?purpose={purpose}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print(f"  Found {result['total']} files")
            for file in result["files"][:5]:  # Show first 5
                print(f"    - {file['filename']} ({file['category']}, {file['size']} bytes)")
            if result['total'] > 5:
                print(f"    ... and {result['total'] - 5} more")
            return result
        else:
            print(f"  ✗ Failed to list files")
            return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def get_stats():
    """Get upload statistics."""
    url = f"{API_BASE}/stats"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            stats = result["stats"]
            print(f"  Total Files: {stats['total_files']}")
            print(f"  Total Size: {stats['total_size']:,} bytes")
            print(f"  Training: {stats['by_purpose'].get('training', {}).get('count', 0)} files")
            print(f"  Ingestion: {stats['by_purpose'].get('ingestion', {}).get('count', 0)} files")
            return result
        else:
            print(f"  ✗ Failed to get stats")
            return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def main():
    """Run the demo."""
    print("=" * 60)
    print("DATA UPLOAD API DEMONSTRATION")
    print("=" * 60)
    
    # Check if API is available
    try:
        response = requests.get(f"{API_BASE}/../health", timeout=2)
        print(f"\n✓ API is available at {API_BASE}")
    except:
        print(f"\n✗ API is not running at {API_BASE}")
        print("\nTo start the platform:")
        print("  cd /home/runner/work/masterchief/masterchief")
        print("  python platform/app.py")
        print("\nThen run this demo again.")
        return
    
    # Setup demo files
    print("\n" + "=" * 60)
    print("STEP 1: Creating Demo Files")
    print("=" * 60)
    setup_demo()
    
    # Upload files
    print("\n" + "=" * 60)
    print("STEP 2: Uploading Files")
    print("=" * 60)
    
    files_to_upload = [
        (DEMO_DIR / "training_commands.json", "training", "Bot command definitions"),
        (DEMO_DIR / "sample.log", "ingestion", "Application logs"),
        (DEMO_DIR / "metrics.csv", "ingestion", "System metrics"),
    ]
    
    uploaded = []
    for filepath, purpose, desc in files_to_upload:
        result = upload_file(filepath, purpose, desc)
        if result:
            uploaded.append(result)
    
    if not uploaded:
        print("\n✗ No files uploaded. Exiting.")
        return
    
    # List files
    print("\n" + "=" * 60)
    print("STEP 3: Listing Uploaded Files")
    print("=" * 60)
    print("\nAll files:")
    list_files()
    
    print("\nTraining files only:")
    list_files(purpose="training")
    
    # Get statistics
    print("\n" + "=" * 60)
    print("STEP 4: Upload Statistics")
    print("=" * 60)
    get_stats()
    
    # Success
    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Open docs/examples/data-upload-ui.html for a web interface")
    print("  2. Check docs/UPLOAD_QUICKSTART.md for more examples")
    print("  3. See docs/DATA_UPLOAD_API.md for full API reference")
    print("\n🌙 Echo can now learn from your uploaded data!")


if __name__ == "__main__":
    main()
