import urllib.request, json, sys
from pathlib import Path
token_path = Path(r"D:\AI\hd-instrument\.together_token")
key = token_path.read_text(encoding="utf-8").strip().split("\n")[0].strip()
print(f"Together API key prefix: {key[:10]}... (length {len(key)})")
print()
req = urllib.request.Request(
    "https://api.together.xyz/v1/models",
    headers={"Authorization": f"Bearer {key}", "User-Agent": "hd-instrument/0.1"},
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        models = json.loads(r.read())
    print(f"OK: API key works. Server returned {len(models)} models.")
    print()
    print("=== Llama 405B variants available ===")
    for m in models:
        mid = m.get("id", "")
        if "405" in mid and "llama" in mid.lower():
            print(f"  {mid}")
    print()
    print("=== Sample Llama-3 models (top 10) ===")
    count = 0
    for m in models:
        mid = m.get("id", "")
        if "llama-3" in mid.lower():
            print(f"  {mid}")
            count += 1
            if count >= 10:
                break
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")[:300]
    print(f"FAIL: HTTP {e.code} {e.reason}")
    print(f"Response body: {body}")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
