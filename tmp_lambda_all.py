import json, subprocess, re
with open("/root/.lambda_cloud/lambda_keys") as f:
    content = f.read().strip()
api_key = re.search(r"api_key\s*=\s*(\S+)", content).group(1)
r = subprocess.run(["curl", "-s", "-u", f"{api_key}:", "https://cloud.lambdalabs.com/api/v1/instance-types"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
data = d.get("data", {})

print("=== All Lambda SKUs with current capacity ===")
print(f"{'SKU':<30s} {'price':>8s} {'gpu_vram':>10s} {'regions w/ capacity'}")
print("-" * 90)
rows = []
for sku in sorted(data.keys()):
    info = data[sku].get("instance_type", {})
    specs = info.get("specs", {})
    vram_gb = specs.get("memory_gib", "?")
    price_c = info.get("price_cents_per_hour", "?")
    gpu_desc = info.get("gpu_description", "")
    regs = [r["name"] for r in data[sku].get("regions_with_capacity_available", [])]
    if regs:
        rows.append((price_c if isinstance(price_c, int) else 999999, sku, price_c, gpu_desc, regs))
rows.sort()  # by price
for _, sku, price, gpu, regs in rows:
    pstr = f"${price/100:.2f}/h" if isinstance(price, int) else str(price)
    print(f"{sku:<30s} {pstr:>8s}  {gpu:<22s}  {regs}")
