# Patch SkyPilot's Lambda CSV catalog: add us-southeast-1 rows for our target SKUs
CSV = "/root/.sky/catalogs/v8/lambda/vms.csv"

new_rows = [
    'gpu_1x_b200_sxm6,B200,1.0,26.0,360.0,6.99,us-southeast-1,"{\'Gpus\': [{\'Name\': \'B200\', \'Manufacturer\': \'NVIDIA\', \'Count\': 1.0, \'MemoryInfo\': {\'SizeInMiB\': 184320}}], \'TotalGpuMemoryInMiB\': 184320}",',
    'gpu_2x_h100_sxm5,H100,2.0,52.0,450.0,8.38,us-southeast-1,"{\'Gpus\': [{\'Name\': \'H100\', \'Manufacturer\': \'NVIDIA\', \'Count\': 2.0, \'MemoryInfo\': {\'SizeInMiB\': 81920}}], \'TotalGpuMemoryInMiB\': 81920}",',
]

with open(CSV, "r") as f:
    existing = f.read()

# Check if already patched
if "us-southeast-1" in existing:
    print("Already patched; skipping.")
else:
    with open(CSV, "a") as f:
        for row in new_rows:
            f.write(row + "\n")
    print(f"Added {len(new_rows)} rows for us-southeast-1.")

# Verify
import subprocess
r = subprocess.run(["grep", "-c", "us-southeast-1", CSV], capture_output=True, text=True)
print(f"us-southeast-1 row count: {r.stdout.strip()}")
print("B200 + H100:2 regions now:")
r = subprocess.run(["grep", "-E", "^gpu_(1x_b200_sxm6|2x_h100_sxm5)", CSV], capture_output=True, text=True)
import re
regions = set()
for line in r.stdout.splitlines():
    parts = line.split(",")
    if len(parts) > 6:
        regions.add(parts[6])
for reg in sorted(regions):
    print(f"  {reg}")
