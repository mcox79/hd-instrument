import urllib.request, json
from pathlib import Path
key = Path(r"D:\AI\hd-instrument\.together_token").read_text(encoding="utf-8").strip().split("\n")[0].strip()
req = urllib.request.Request("https://api.together.xyz/v1/models",
    headers={"Authorization": f"Bearer {key}", "User-Agent": "hd-instrument/cell5"})
with urllib.request.urlopen(req, timeout=15) as r:
    models = json.loads(r.read())
print("=== ALL models with non-zero pricing AND chat-capable AND llama family ===")
for m in models:
    mid = m.get("id", "")
    if "llama" not in mid.lower():
        continue
    pr = m.get("pricing", {})
    inp = pr.get("input", 0)
    out = pr.get("output", 0)
    if inp == 0 and out == 0:
        continue
    mtype = m.get("type", "?")
    if mtype != "chat":
        continue
    print(f"  {mid} | type={mtype} | input=${inp}/M output=${out}/M")
print()
print("=== Search all entries with 405 in description ===")
for m in models:
    text = json.dumps(m).lower()
    if "405" in text:
        print(f"  {m.get('id', '?')}  display={m.get('display_name', '?')}  type={m.get('type', '?')}  pricing={m.get('pricing', {})}")
