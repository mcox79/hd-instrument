import json, subprocess, re
with open("/root/.lambda_cloud/lambda_keys") as f:
    content = f.read().strip()
# Extract the value after "api_key ="
m = re.search(r"api_key\s*=\s*(\S+)", content)
api_key = m.group(1) if m else content
print(f"Parsed key prefix: {api_key[:15]}... length={len(api_key)}")

r = subprocess.run(["curl", "-s", "-u", f"{api_key}:", "https://cloud.lambdalabs.com/api/v1/instance-types"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
data = d.get("data", {})
print(f"Total SKUs: {len(data)}")

h100_skus = [k for k in data.keys() if "h100" in k.lower()]
print(f"H100 SKUs: {h100_skus}")
for sku in h100_skus:
    regs = [r["name"] for r in data[sku].get("regions_with_capacity_available", [])]
    price = data[sku].get("instance_type", {}).get("price_cents_per_hour", "?")
    print(f"  {sku} price={price}c/h regions_w_capacity={regs}")

# All regions Lambda has H100 in (regardless of current capacity); need to look at the instance descriptions
all_regs = set()
for k in data.keys():
    for r in data[k].get("regions_with_capacity_available", []):
        all_regs.add(r["name"])
print(f"All Lambda regions with ANY capacity right now: {sorted(all_regs)}")
