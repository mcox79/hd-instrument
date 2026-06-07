import os
from pathlib import Path
TOK = Path(r"C:\dev\hd-instrument\.hf_token").read_text(encoding="utf-8").strip()
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_TOKEN"] = TOK
print(f"Using token prefix: {TOK[:5]}...")
print()
# Check current cache state
import subprocess
cache = Path(os.path.expanduser("~")) / ".cache/huggingface/hub/models--meta-llama--Llama-3.2-1B"
print(f"Cache dir: {cache}")
print(f"Exists: {cache.exists()}")
if cache.exists():
    # Print directory contents
    for snap in (cache / "snapshots").iterdir() if (cache / "snapshots").exists() else []:
        print(f"  snapshot: {snap.name}")
        for f in snap.iterdir():
            print(f"    {f.name} ({'symlink' if f.is_symlink() else 'file'})")
print()
print("=== triggering download (snapshot_download with HF_TOKEN) ===")
from huggingface_hub import snapshot_download
try:
    path = snapshot_download(
        repo_id="meta-llama/Llama-3.2-1B",
        token=TOK,
        allow_patterns=["*.safetensors", "*.bin", "*.json", "tokenizer*", "*.model", "*.txt"],
    )
    print(f"OK: downloaded to {path}")
    print()
    print("=== verify safetensors present ===")
    for f in Path(path).iterdir():
        size_mb = f.stat().st_size / 1e6 if f.is_file() else 0
        print(f"  {f.name} ({size_mb:.1f} MB)")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
