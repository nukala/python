import os
import requests
from pathlib import Path

# Create sample_files directory
sample_dir = Path("sample_files")
sample_dir.mkdir(exist_ok=True)

# Sample documents to download
sample_docs = {
    "attention.pdf": "https://arxiv.org/pdf/1706.03762.pdf",
    "bert.pdf": "https://arxiv.org/pdf/1810.04805.pdf",
}

# Download sample documents with error handling
for filename, url in sample_docs.items():
    filepath = sample_dir / filename
    if not filepath.exists():
        print(f"📥 Downloading {filename}...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Basic content validation
            if response.headers.get('content-type', '').startswith('application/pdf'):
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"   ✅ Downloaded {filename}")
            else:
                print(f"   ⚠️ Warning: {filename} may not be a valid PDF")
        except requests.RequestException as e:
            print(f"   ❌ Failed to download {filename}: {e}")
    else:
        print(f"📁 {filename} already exists")

print("\n✅ Sample files ready!")