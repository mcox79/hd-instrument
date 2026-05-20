"""Stage 4 CPU experiments: multi-seed validation + capacity extension + analysis.

Rationale: K=2944 dip retraction (cycle 3) revealed that ACF/decompose work
defaulted to SEED=17 and the conclusions had hidden seed-correlation. Multi-seed
ALL future ACF/decompose work. Plus a couple of capacity probes.
"""
import json
import re
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")

# 1) acf_K2944_multi_seed: 5 seeds at K=2944, r in {0.005, 0.01, 0.05}
# Confirms the retraction. Different seed should NOT show the 50% dip.
acf_base = (REPO / "experiments" / "exp_wave14b_acf_sparsity_sweep.py").read_text()
v = re.sub(r"SEED\s*=\s*\d+", "# multi-seed", acf_base, count=1)
# Add SEEDS = [...] at top + iterate
seed_block = "SEEDS = [7, 13, 17, 23, 31]\n"
if "SEEDS =" not in v:
    # inject after first DEVICE definition
    v = v.replace("DEVICE = torch.device", seed_block + "DEVICE = torch.device", 1)
# Replace K_SWEEP if found
m = re.search(r"K_SWEEP\s*=\s*\[[^\]]+\]", v)
if m:
    v = v.replace(m.group(0), "K_SWEEP = [2944]")
m = re.search(r"R_VALUES\s*=\s*\[[^\]]+\]", v)
if m:
    v = v.replace(m.group(0), "R_VALUES = [0.005, 0.01, 0.05]")
v = v.replace("exp_wave14b_acf_sparsity_sweep", "exp_wave14g_acf_K2944_multi_seed")
(REPO / "experiments" / "exp_wave14g_acf_K2944_multi_seed.py").write_text(v)
print("wrote exp_wave14g_acf_K2944_multi_seed.py")

# 2) decompose_K_cliff_multi_seed: redo K-cliff at 5 seeds (the K=2944 lesson)
dec_base = (REPO / "experiments" / "exp_wave14b_decompose_K_cliff.py").read_text()
v = re.sub(r"SEED\s*=\s*\d+", "# multi-seed", dec_base, count=1)
if "SEEDS =" not in v:
    v = v.replace("DEVICE = torch.device", seed_block + "DEVICE = torch.device", 1)
v = v.replace("exp_wave14b_decompose_K_cliff", "exp_wave14g_decompose_K_cliff_multi_seed")
(REPO / "experiments" / "exp_wave14g_decompose_K_cliff_multi_seed.py").write_text(v)
print("wrote exp_wave14g_decompose_K_cliff_multi_seed.py")

# 3) decompose_K_cliff_N8192: does the cliff shift with N? Per Frady-Sommer, cliff is
# function of K/N so should hold at K/N ratios. Tests this directly.
v = (REPO / "experiments" / "exp_wave14b_decompose_K_cliff.py").read_text()
v = v.replace("N = 4096", "N = 8192")
v = v.replace("K_SWEEP = [2304, 2560, 2816, 3072, 3328, 3584, 3840]",
              "K_SWEEP = [4096, 4608, 5120, 5632, 6144, 6656, 7168, 7680]")
v = v.replace("exp_wave14b_decompose_K_cliff", "exp_wave14g_decompose_K_cliff_N8192")
(REPO / "experiments" / "exp_wave14g_decompose_K_cliff_N8192.py").write_text(v)
print("wrote exp_wave14g_decompose_K_cliff_N8192.py")

# 4) Queue all 3 on CPU + add a 4th simple bayes-floor analysis
cpu_q_path = REPO / "data" / "remote_cpu_queue" / "queue.json"
cpu_q = json.loads(cpu_q_path.read_text())
cpu_q["experiments"].extend([
    {"name": "wave14g_acf_K2944_multi_seed", "script": "experiments/exp_wave14g_acf_K2944_multi_seed.py",
     "status": "pending",
     "purpose": "Confirms K=2944 dip retraction (cycle 3): 5 seeds x 3 r values. Different seeds should NOT show the 50% dip that SEED=17 produced.",
     "timeout_s": 5400},
    {"name": "wave14g_decompose_K_cliff_multi_seed", "script": "experiments/exp_wave14g_decompose_K_cliff_multi_seed.py",
     "status": "pending",
     "purpose": "Methodology fix per K=2944 lesson: original K-cliff finding used SEED=17 only. 5-seed validation that the cliff at K/N=0.56 is robust across seeds.",
     "timeout_s": 7200},
    {"name": "wave14g_decompose_K_cliff_N8192", "script": "experiments/exp_wave14g_decompose_K_cliff_N8192.py",
     "status": "pending",
     "purpose": "Tests Frady-Sommer prediction that cliff is K/N-dependent (not absolute K). At N=8192, sweep K=4096-7680. Expected cliff at same K/N=0.56 = K=4587.",
     "timeout_s": 14400},
])
cpu_q_path.write_text(json.dumps(cpu_q, indent=2))
print(f"\nCPU pending: {sum(1 for e in cpu_q['experiments'] if e['status']=='pending')}")
for e in cpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
