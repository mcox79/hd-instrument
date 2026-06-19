import urllib.request, json
from pathlib import Path
key = Path(r"D:\AI\hd-instrument\.together_token").read_text(encoding="utf-8").strip().split("\n")[0].strip()
req = urllib.request.Request(
    "https://api.together.xyz/v1/models",
    headers={"Authorization": f"Bearer {key}"},
)
with urllib.request.urlopen(req, timeout=15) as r:
    models = json.loads(r.read())
print("=== ALL Llama 405B variants ===")
for m in models:
    mid = m.get("id", "")
    if "405" in mid:
        ctx = m.get("context_length", "?")
        mtype = m.get("type", "?")
        display = m.get("display_name", "")
        pricing = m.get("pricing", {})
        print(f"  id={mid}")
        print(f"    type={mtype} ctx={ctx} display={display}")
        print(f"    pricing={pricing}")
