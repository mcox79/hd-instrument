"""Refill helper after cycle 1: queue follow-ups, mark partials, fork variants."""
import json
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")

# --- Fork GPU follow-ups ---
r10_base = (REPO / "experiments" / "exp_wave14b_r10_best_config_multiseed.py").read_text()

# R10 K=1024 (extend headline)
v = r10_base.replace("K_LEVELS = [128, 256]", "K_LEVELS = [1024]")
v = v.replace("r10_best_config_multiseed", "r10_best_config_K1024")
(REPO / "experiments" / "exp_wave14b_r10_best_config_K1024.py").write_text(v)

# R10 K=8 multi-seed (verify the K=8 boundary)
v = r10_base.replace("K_LEVELS = [128, 256]", "K_LEVELS = [8]")
v = v.replace("r10_best_config_multiseed", "r10_best_config_K8_verify")
(REPO / "experiments" / "exp_wave14b_r10_best_config_K8_verify.py").write_text(v)

# R10 N=8192 at K=256 (M1 mechanism at higher K)
v = r10_base.replace("N = 4096", "N = 8192")
v = v.replace("K_LEVELS = [128, 256]", "K_LEVELS = [256]")
v = v.replace("r10_best_config_multiseed", "r10_best_config_N8192_K256")
(REPO / "experiments" / "exp_wave14b_r10_best_config_N8192_K256.py").write_text(v)

# Fork R3-disjoint K=64 (does K-flatness hold further?)
r3d_base = (REPO / "experiments" / "exp_wave14b_r3_disjoint_concepts.py").read_text()
v = r3d_base.replace("K = 4", "K = 64")
v = v.replace("r3_disjoint_concepts", "r3_disjoint_K64")
(REPO / "experiments" / "exp_wave14b_r3_disjoint_K64.py").write_text(v)

print("Wrote GPU follow-up scripts.")

# --- Fork CPU follow-ups: smaller subsets to avoid timeout ---
# Decompose K-cliff dense SMALLER subset (8 levels, not 16, fits in 2h)
dec_base = (REPO / "experiments" / "exp_wave14b_decompose_K_cliff.py").read_text()
v = dec_base.replace(
    "K_SWEEP = [2304, 2560, 2816, 3072, 3328, 3584, 3840]",
    "K_SWEEP = [2304, 2432, 2560, 2688, 2816, 2944, 3072, 3200]"
)
v = v.replace("exp_wave14b_decompose_K_cliff", "exp_wave14b_decompose_K_cliff_dense8")
(REPO / "experiments" / "exp_wave14b_decompose_K_cliff_dense8.py").write_text(v)

print("Wrote CPU follow-up script.")

# --- Update GPU queue ---
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
gpu_new = [
    {"name": "r10_best_config_K1024", "script": "experiments/exp_wave14b_r10_best_config_K1024.py",
     "status": "pending",
     "purpose": "R10 best-config K=1024. Curve K=8 to K=512 monotone; does K=1024 extend toward +0.7+ or saturate?",
     "timeout_s": 14400},
    {"name": "r10_best_config_K8_verify", "script": "experiments/exp_wave14b_r10_best_config_K8_verify.py",
     "status": "pending",
     "purpose": "Verify K=8 boundary: best=+0.142 from K2_K4_K8 single run. Multi-seed verify the inversion threshold.",
     "timeout_s": 3600},
    {"name": "r10_best_config_N8192_K256", "script": "experiments/exp_wave14b_r10_best_config_N8192_K256.py",
     "status": "pending",
     "purpose": "M1 mechanism check at K=256: does N=8192 shrink best-config +0.543 gap (like K=128 shrank 15%)?",
     "timeout_s": 14400},
    {"name": "r3_disjoint_K64", "script": "experiments/exp_wave14b_r3_disjoint_K64.py",
     "status": "pending",
     "purpose": "R3-disjoint K-scan extension. K=16/32 gave +0.008 (vs +0.025 at K=4). Does K=64 stay flat or rebound?",
     "timeout_s": 5400},
]
gpu_q["experiments"].extend(gpu_new)
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))

# --- Update CPU queue ---
cpu_q_path = REPO / "data" / "remote_cpu_queue" / "queue.json"
cpu_q = json.loads(cpu_q_path.read_text())
cpu_new = [
    {"name": "decompose_K_cliff_dense8", "script": "experiments/exp_wave14b_decompose_K_cliff_dense8.py",
     "status": "pending",
     "purpose": "Decompose K-cliff with 8 K levels in 2304-3200 (subset of dense16 which timed out). Fits in 2h.",
     "timeout_s": 7200},
    {"name": "acf_K_dependent_extended_redo", "script": "experiments/exp_wave14b_acf_K_dependent_extended.py",
     "status": "pending",
     "purpose": "Re-run ACF K-dep extended to cross-validate the K=2944 dip (single-run anomaly?).",
     "timeout_s": 14400},
]
cpu_q["experiments"].extend(cpu_new)
cpu_q_path.write_text(json.dumps(cpu_q, indent=2))

print("\nGPU queue now:")
for e in gpu_q["experiments"][-5:]:
    print(f"  - {e['name']:40s} {e['status']}")
print("\nCPU queue now:")
for e in cpu_q["experiments"][-3:]:
    print(f"  - {e['name']:40s} {e['status']}")
