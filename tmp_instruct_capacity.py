import json, subprocess, re
with open("/root/.lambda_cloud/lambda_keys") as f:
    api_key = re.search(r"api_key\s*=\s*(\S+)", f.read().strip()).group(1)
r = subprocess.run(["curl", "-s", "-u", f"{api_key}:", "https://cloud.lambdalabs.com/api/v1/instance-types"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
data = d.get("data", {})
SK = {'us-east-1','us-east-2','us-east-3','us-west-1','us-west-2','us-west-3',
      'us-south-1','us-south-2','us-south-3','us-midwest-1','us-southeast-1',
      'asia-northeast-1','asia-northeast-2','asia-south-1','australia-east-1',
      'europe-central-1','europe-south-1','me-west-1'}
print("=== priority SKUs availability (filtered to SkyPilot-known regions) ===")
for sku in ['gpu_1x_gh200', 'gpu_1x_h100_sxm5', 'gpu_1x_h100_pcie']:
    regs_all = [r['name'] for r in data.get(sku, {}).get('regions_with_capacity_available', [])]
    sk_regs = [r for r in regs_all if r in SK]
    unknown = [r for r in regs_all if r not in SK]
    print(f"  {sku}: SkyPilot-known={sk_regs} unknown-to-sky={unknown}")
