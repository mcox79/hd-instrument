import urllib.request, json, sys
# Query PyPI for bitsandbytes wheels; check for aarch64 (ARM) wheels
print("=== bitsandbytes wheels available ===")
try:
    with urllib.request.urlopen("https://pypi.org/pypi/bitsandbytes/json", timeout=10) as r:
        d = json.loads(r.read())
    # Latest version files
    latest = d["info"]["version"]
    files = d["releases"].get(latest, [])
    print(f"Latest version: {latest}")
    has_aarch64 = False
    has_x86_64 = False
    for f in files:
        fn = f["filename"]
        if "aarch64" in fn or "arm64" in fn:
            has_aarch64 = True
            print(f"  ARM64 wheel: {fn}")
        elif "x86_64" in fn or "amd64" in fn:
            has_x86_64 = True
    if not has_aarch64:
        print(f"  NO aarch64 wheel for {latest}")
        # Check if any older version has aarch64
        for ver in list(d["releases"].keys())[-10:][::-1]:
            for f in d["releases"][ver]:
                if "aarch64" in f["filename"] or "arm64" in f["filename"]:
                    print(f"  (older) {ver}: {f['filename']}")
                    break
    print(f"  has_x86_64={has_x86_64}; has_aarch64={has_aarch64}")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")

# Check torch 2.4.1 cu121 aarch64 availability via PyTorch index
print("\n=== torch 2.4.1 ===")
try:
    with urllib.request.urlopen("https://pypi.org/pypi/torch/2.4.1/json", timeout=10) as r:
        d = json.loads(r.read())
    files = d.get("urls", [])
    aarch_files = [f["filename"] for f in files if "aarch64" in f["filename"]]
    x86_files = [f["filename"] for f in files if "x86_64" in f["filename"]]
    print(f"  aarch64 wheels: {aarch_files[:3]}")
    print(f"  x86_64 wheels:  {x86_files[:3]}")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
