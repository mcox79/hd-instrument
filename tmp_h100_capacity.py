import json, subprocess, re
with open("/root/.lambda_cloud/lambda_keys") as f:
    content = f.read().strip()
api_key = re.search(r"api_key\s*=\s*(\S+)", content).group(1)
r = subprocess.run(["curl", "-s", "-u", f"{api_key}:", "https://cloud.lambdalabs.com/api/v1/instance-types"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
data = d.get("data", {})
print("=== H100 multi-GPU capacity right now ===")
for sku in ["gpu_1x_h100_pcie", "gpu_1x_h100_sxm5", "gpu_2x_h100_sxm5", "gpu_4x_h100_sxm5", "gpu_8x_h100_sxm5"]:
    info = data.get(sku, {})
    price_c = info.get("instance_type", {}).get("price_cents_per_hour", "?")
    regs = [r["name"] for r in info.get("regions_with_capacity_available", [])]
    pstr = f"${price_c/100:.2f}/h" if isinstance(price_c, int) else "?"
    print(f"  {sku:<22}  {pstr:>10}  regions={regs}")
