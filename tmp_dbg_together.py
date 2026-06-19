from pathlib import Path
raw = Path(r"D:\AI\hd-instrument\.together_token").read_text(encoding="utf-8")
print(f"raw length: {len(raw)}")
print(f"first line: [{raw.split(chr(10))[0]}]")
print(f"after strip+split: [{raw.strip().split(chr(10))[0].strip()}]")
key = raw.strip().split(chr(10))[0].strip()
print(f"final key len={len(key)} prefix={key[:10]}")
import urllib.request, json
req = urllib.request.Request("https://api.together.xyz/v1/models",
    headers={"Authorization": f"Bearer {key}", "User-Agent": "hd-instrument/cell5"})
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        models = json.loads(r.read())
    print(f"OK: {len(models)} models")
    for m in models:
        mid = m.get("id", "")
        if "405" in mid:
            pr = m.get("pricing", {})
            print(f"  {mid}  pricing={pr}")
except urllib.error.HTTPError as e:
    print(f"FAIL: HTTP {e.code} {e.read().decode()[:300]}")
