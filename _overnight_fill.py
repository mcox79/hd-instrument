"""Overnight queue filler: fork ACF K-dependent with extended K + add CPU queue items + extend GPU queue."""
import json
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")

# 1) Fork ACF K-dependent with extended K values
acf_base = (REPO / "experiments" / "exp_wave14b_acf_K_dependent.py").read_text()
acf_ext = acf_base.replace(
    "K_SWEEP = [2048, 2304, 2560, 3072, 4096, 6144]",
    "K_SWEEP = [1536, 1792, 2048, 2176, 2304, 2432, 2560, 2688, 2816, 2944, 3072, 3328, 3584, 4096, 5120, 6144]"
).replace("exp_wave14b_acf_K_dependent", "exp_wave14b_acf_K_dependent_extended")
(REPO / "experiments" / "exp_wave14b_acf_K_dependent_extended.py").write_text(acf_ext)
print("wrote exp_wave14b_acf_K_dependent_extended.py")

# 2) Fork decompose K-cliff to denser sweep near cliff
dec_base = (REPO / "experiments" / "exp_wave14b_decompose_K_cliff.py").read_text()
dec_ext = dec_base.replace(
    "K_SWEEP = [2304, 2560, 2816, 3072, 3328, 3584, 3840]",
    "K_SWEEP = [2240, 2304, 2368, 2432, 2496, 2560, 2624, 2688, 2752, 2816, 2880, 2944, 3008, 3072, 3200, 3328]"
).replace("exp_wave14b_decompose_K_cliff", "exp_wave14b_decompose_K_cliff_dense")
(REPO / "experiments" / "exp_wave14b_decompose_K_cliff_dense.py").write_text(dec_ext)
print("wrote exp_wave14b_decompose_K_cliff_dense.py")

# 3) Append to CPU queue
cpu_q_path = REPO / "data" / "remote_cpu_queue" / "queue.json"
cpu_q = json.loads(cpu_q_path.read_text())
cpu_items = [
    {"name": "acf_K_dependent_extended", "script": "experiments/exp_wave14b_acf_K_dependent_extended.py",
     "status": "pending",
     "purpose": "ACF K-dependent with 16 K levels for fine cliff mapping. Extends prior 6-level sweep with intermediate K values around the 0.5-0.6 K/N transition.",
     "timeout_s": 7200},
    {"name": "decompose_K_cliff_dense", "script": "experiments/exp_wave14b_decompose_K_cliff_dense.py",
     "status": "pending",
     "purpose": "Decompose K-cliff with 16 K levels in 2240-3328 range for sub-step cliff localization. Tests if cliff is single-step or has substructure.",
     "timeout_s": 7200},
    {"name": "acf_sparsity_sweep_redo", "script": "experiments/exp_wave14b_acf_sparsity_sweep.py",
     "status": "pending",
     "purpose": "Re-run ACF sparsity sweep r in {0.005,0.01,0.05,0.1} at cliff K values. Cross-validates the asymmetric ACF behavior.",
     "timeout_s": 5400},
    {"name": "cpu_platform_timing_redo", "script": "experiments/exp_wave14b_cpu_platform_timing_v2.py",
     "status": "pending",
     "purpose": "CPU platform timing at K=4 corpus. Throughput / latency reference for production-readiness narrative.",
     "timeout_s": 3600},
    {"name": "acf_resonator_redo", "script": "experiments/exp_wave14b_acf_resonator.py",
     "status": "pending",
     "purpose": "ACF resonator re-run for cross-validation of fixed-r=0.01 behavior at K=2048-6144.",
     "timeout_s": 5400},
]
cpu_q["experiments"].extend(cpu_items)
cpu_q_path.write_text(json.dumps(cpu_q, indent=2))
print("\nCPU queue now:")
for e in cpu_q["experiments"]:
    print(f"  - {e['name']:40s} {e['status']}")

# 4) Append more items to GPU queue too (insurance for 6h window)
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())

# Fork R3-disjoint to K=32 too
r3d_base = (REPO / "experiments" / "exp_wave14b_r3_disjoint_concepts.py").read_text()
r3d_32 = r3d_base.replace("K = 4", "K = 32").replace("r3_disjoint_concepts", "r3_disjoint_K32")
(REPO / "experiments" / "exp_wave14b_r3_disjoint_K32.py").write_text(r3d_32)
print("\nwrote exp_wave14b_r3_disjoint_K32.py")

# Fork R10 best-config to N=8192 at K=128
r10_base = (REPO / "experiments" / "exp_wave14b_r10_best_config_multiseed.py").read_text()
r10_n8 = r10_base.replace("N = 4096", "N = 8192").replace(
    "K_LEVELS = [128, 256]", "K_LEVELS = [128]"
).replace("r10_best_config_multiseed", "r10_best_config_N8192_K128")
(REPO / "experiments" / "exp_wave14b_r10_best_config_N8192_K128.py").write_text(r10_n8)
print("wrote exp_wave14b_r10_best_config_N8192_K128.py")

gpu_extras = [
    {"name": "r3_disjoint_K32", "script": "experiments/exp_wave14b_r3_disjoint_K32.py",
     "status": "pending",
     "purpose": "R3 disjoint concepts at K=32. Does the disjoint-compound effect (+0.025 at K=4) scale up with K like R10?",
     "timeout_s": 5400},
    {"name": "r10_best_config_N8192_K128", "script": "experiments/exp_wave14b_r10_best_config_N8192_K128.py",
     "status": "pending",
     "purpose": "R10 best-config at N=8192, K=128. Tests if N doubling shrinks the +0.412 best-config gap (M1 bundle-SNR mechanism check).",
     "timeout_s": 10800},
]
gpu_q["experiments"].extend(gpu_extras)
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))
print("\nGPU queue now:")
for e in gpu_q["experiments"]:
    print(f"  - {e['name']:40s} {e['status']}")
