import json, subprocess, re
with open("/root/.lambda_cloud/lambda_keys") as f:
    api_key = re.search(r"api_key\s*=\s*(\S+)", f.read().strip()).group(1)
# Find the H100 instance and terminate it
r = subprocess.run(["curl", "-s", "-u", f"{api_key}:", "https://cloud.lambdalabs.com/api/v1/instances"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
for ii in d.get("data", []):
    if ii.get("instance_type", {}).get("name") == "gpu_1x_h100_pcie":
        iid = ii["id"]
        print(f"Terminating zombie H100 PCIe: id={iid} region={ii.get('region',{}).get('name')}")
        payload = json.dumps({"instance_ids": [iid]})
        rterm = subprocess.run(
            ["curl", "-s", "-u", f"{api_key}:", "-H", "Content-Type: application/json",
             "-X", "POST", "-d", payload,
             "https://cloud.lambdalabs.com/api/v1/instance-operations/terminate"],
            capture_output=True, text=True)
        print(f"  response: {rterm.stdout[:200]}")
    else:
        print(f"Keeping: {ii.get('instance_type',{}).get('name')} id={ii['id']} status={ii.get('status')}")
