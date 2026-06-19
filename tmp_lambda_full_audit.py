import json, subprocess, re
with open("/root/.lambda_cloud/lambda_keys") as f:
    content = f.read().strip()
api_key = re.search(r"api_key\s*=\s*(\S+)", content).group(1)
r = subprocess.run(["curl", "-s", "-u", f"{api_key}:", "https://cloud.lambdalabs.com/api/v1/instance-types"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
data = d.get("data", {})

print("=== ALL Lambda Cloud GPU SKUs + current capacity ===")
print(f"{'SKU':<28s} {'price/hr':>10s} {'gpu_desc':<28s} {'vCPU':>5s} {'RAM_GB':>7s} {'storage':>9s} {'regions w/ capacity'}")
print("-" * 140)
rows = []
for sku, info in sorted(data.items()):
    it = info.get("instance_type", {})
    specs = it.get("specs", {})
    price_c = it.get("price_cents_per_hour", 0)
    gpu_desc = it.get("gpu_description", "")
    vcpus = specs.get("vcpus", "?")
    ram = specs.get("memory_gib", "?")
    storage = specs.get("storage_gib", "?")
    regs = [r["name"] for r in info.get("regions_with_capacity_available", [])]
    rows.append((price_c, sku, gpu_desc, vcpus, ram, storage, regs))

# Sort by price ascending
rows.sort()
for price_c, sku, gpu, vcpu, ram, st, regs in rows:
    pstr = f"${price_c/100:.2f}" if isinstance(price_c, int) else "?"
    rstr = "[" + ", ".join(regs) + "]" if regs else "[]"
    print(f"{sku:<28s} {pstr:>10s} {gpu:<28s} {str(vcpu):>5s} {str(ram):>7s} {str(st):>9s} {rstr}")

print()
print("=== Total VRAM per SKU (for 70B sizing) ===")
print(f"{'SKU':<28s} {'count':>5s} {'per_gpu_VRAM':>12s} {'total_VRAM':>10s} {'fits 70B fp16 (140GB)?':>22s} {'fits 70B 4bit (40GB)?':>22s}")
print("-" * 110)
def parse_count_vram(sku):
    m = re.match(r"gpu_(\d+)x_(\w+)", sku)
    if not m:
        return None, None
    count = int(m.group(1))
    model = m.group(2)
    # Approximate per-GPU VRAM mapping
    vram_map = {
        "a10": 24,
        "a100": 40,  # all Lambda A100 SXM4 are 40 GB
        "a100_pcie": 40,  # if present
        "a6000": 48,
        "h100_pcie": 80,
        "h100_sxm5": 80,
        "gh200": 96,
        "h200": 141,  # if available
        "v100_n": 16,
        "v100": 16,
        "rtx6000": 48,
    }
    vram = vram_map.get(model)
    return count, vram

for sku, info in sorted(data.items()):
    c, v = parse_count_vram(sku)
    if c and v:
        total_vram = c * v
        fp16_fit = "YES" if total_vram >= 140 else "no"
        nf4_fit = "YES" if total_vram >= 40 else "no"
        print(f"{sku:<28s} {c:>5d} {v:>12d}GB {total_vram:>9d}GB {fp16_fit:>22s} {nf4_fit:>22s}")
