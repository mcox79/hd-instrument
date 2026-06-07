import json, subprocess, re
with open("/root/.lambda_cloud/lambda_keys") as f:
    content = f.read().strip()
api_key = re.search(r"api_key\s*=\s*(\S+)", content).group(1)
# Query actually-running instances
r = subprocess.run(["curl", "-s", "-u", f"{api_key}:", "https://cloud.lambdalabs.com/api/v1/instances"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
instances = d.get("data", [])
print(f"Lambda API reports {len(instances)} running instance(s)")
for ii in instances:
    print(f"  id={ii.get('id')} status={ii.get('status')} region={ii.get('region',{}).get('name')} type={ii.get('instance_type',{}).get('name')} ip={ii.get('ip')}")
print()
# Also re-probe capacity for GH200 + H100 + A100 right now
r2 = subprocess.run(["curl", "-s", "-u", f"{api_key}:", "https://cloud.lambdalabs.com/api/v1/instance-types"],
                    capture_output=True, text=True)
d2 = json.loads(r2.stdout)
data = d2.get("data", {})
print("Current capacity for our priority SKUs:")
for sku in ["gpu_1x_gh200", "gpu_1x_a100_sxm4", "gpu_1x_h100_pcie", "gpu_1x_h100_sxm5"]:
    regs = [r["name"] for r in data.get(sku, {}).get("regions_with_capacity_available", [])]
    print(f"  {sku}: {regs}")
