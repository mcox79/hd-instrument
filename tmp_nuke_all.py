import json, subprocess, re
with open("/root/.lambda_cloud/lambda_keys") as f:
    api_key = re.search(r"api_key\s*=\s*(\S+)", f.read().strip()).group(1)
r = subprocess.run(["curl", "-s", "-u", f"{api_key}:", "https://cloud.lambdalabs.com/api/v1/instances"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
ids = [ii["id"] for ii in d.get("data", [])]
print(f"Found {len(ids)} instance(s): {ids}")
if ids:
    payload = json.dumps({"instance_ids": ids})
    rt = subprocess.run(
        ["curl", "-s", "-u", f"{api_key}:", "-H", "Content-Type: application/json",
         "-X", "POST", "-d", payload,
         "https://cloud.lambdalabs.com/api/v1/instance-operations/terminate"],
        capture_output=True, text=True)
    print(f"terminate response: {rt.stdout[:300]}")
