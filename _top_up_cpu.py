"""Top up CPU queue with 3 more parameter-variant experiments."""
import json
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")

# 1) ACF resonator at higher K (extend K-sweep)
acf_res = (REPO / "experiments" / "exp_wave14b_acf_resonator.py").read_text()
v = acf_res.replace("exp_wave14b_acf_resonator", "exp_wave14b_acf_resonator_high_K")
# Heuristic: replace any K_SWEEP list to add higher K values
import re
m = re.search(r"K_SWEEP\s*=\s*\[([^\]]+)\]", v)
if m:
    v = v.replace(m.group(0), "K_SWEEP = [4096, 6144, 8192, 10240, 12288, 14336, 16384]")
(REPO / "experiments" / "exp_wave14b_acf_resonator_high_K.py").write_text(v)
print("wrote exp_wave14b_acf_resonator_high_K.py")

# 2) Decompose K-cliff with B=4
dec = (REPO / "experiments" / "exp_wave14b_decompose_K_cliff.py").read_text()
v = dec.replace("B = 2", "B = 4").replace(
    "K_SWEEP = [2304, 2560, 2816, 3072, 3328, 3584, 3840]",
    "K_SWEEP = [512, 768, 1024, 1280, 1536, 1792, 2048, 2304]"
).replace("exp_wave14b_decompose_K_cliff", "exp_wave14b_decompose_K_cliff_B4")
(REPO / "experiments" / "exp_wave14b_decompose_K_cliff_B4.py").write_text(v)
print("wrote exp_wave14b_decompose_K_cliff_B4.py")

# 3) ACF sparsity sweep finer r grid at K=2944 (extends K=2944 100-trial test)
acf_sp = (REPO / "experiments" / "exp_wave14b_acf_sparsity_sweep.py").read_text()
m = re.search(r"K_SWEEP\s*=\s*\[([^\]]+)\]", acf_sp)
if m:
    v = acf_sp.replace(m.group(0), "K_SWEEP = [2944]")
m = re.search(r"R_VALUES\s*=\s*\[([^\]]+)\]", v)
if m:
    v = v.replace(m.group(0), "R_VALUES = [0.001, 0.003, 0.005, 0.007, 0.010, 0.012, 0.015, 0.020, 0.030, 0.050]")
m = re.search(r"NUM_TRIALS\s*=\s*\d+", v)
if m:
    v = v.replace(m.group(0), "NUM_TRIALS = 50")
v = v.replace("exp_wave14b_acf_sparsity_sweep", "exp_wave14b_acf_K2944_fine_r_sweep")
(REPO / "experiments" / "exp_wave14b_acf_K2944_fine_r_sweep.py").write_text(v)
print("wrote exp_wave14b_acf_K2944_fine_r_sweep.py")

# Append to CPU queue
cpu_q_path = REPO / "data" / "remote_cpu_queue" / "queue.json"
cpu_q = json.loads(cpu_q_path.read_text())
new_items = [
    {"name": "acf_resonator_high_K", "script": "experiments/exp_wave14b_acf_resonator_high_K.py",
     "status": "pending",
     "purpose": "ACF resonator at K=4096 to K=16384. Extends capacity-saturation curve.",
     "timeout_s": 7200},
    {"name": "decompose_K_cliff_B4", "script": "experiments/exp_wave14b_decompose_K_cliff_B4.py",
     "status": "pending",
     "purpose": "K-cliff at B=4. Tests how cliff scales with bundle size (B=2 baseline, B=3 queued, B=4 here). Maps the 3D (K, N, B) capacity surface.",
     "timeout_s": 7200},
    {"name": "acf_K2944_fine_r_sweep", "script": "experiments/exp_wave14b_acf_K2944_fine_r_sweep.py",
     "status": "pending",
     "purpose": "10 r values x 50 trials at K=2944. If K=2944 100-trial confirms dip, this localizes optimal r.",
     "timeout_s": 5400},
]
cpu_q["experiments"].extend(new_items)
cpu_q_path.write_text(json.dumps(cpu_q, indent=2))
print(f"\nCPU pending: {sum(1 for e in cpu_q['experiments'] if e['status']=='pending')}")
for e in cpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
