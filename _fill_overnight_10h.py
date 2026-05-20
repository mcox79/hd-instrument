"""Fill GPU + CPU queues for ~10h overnight run."""
import json
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")

# Fork helpers
icl_base = (REPO / "experiments" / "exp_wave14d_in_context_learning_via_pool.py").read_text()
gen_base = (REPO / "experiments" / "exp_wave14d_generation_via_sample_feedback.py").read_text()

# ICL variants at K=8 and K=16
for k in [8, 16]:
    v = icl_base.replace("K = 4\n", f"K = {k}\n")
    v = v.replace("in_context_learning_via_pool", f"icl_via_pool_K{k}")
    (REPO / "experiments" / f"exp_wave14d_icl_via_pool_K{k}.py").write_text(v)
    print(f"wrote exp_wave14d_icl_via_pool_K{k}.py")

# Generation variants at K=8 and K=16
for k in [8, 16]:
    v = gen_base.replace("K = 4\n", f"K = {k}\n")
    v = v.replace("generation_via_sample_feedback", f"generation_K{k}")
    (REPO / "experiments" / f"exp_wave14d_generation_K{k}.py").write_text(v)
    print(f"wrote exp_wave14d_generation_K{k}.py")

# R10 K=2048 extension (further extend the headline)
r10_base = (REPO / "experiments" / "exp_wave14b_r10_best_config_multiseed.py").read_text()
v = r10_base.replace("K_LEVELS = [128, 256]", "K_LEVELS = [2048]")
v = v.replace("r10_best_config_multiseed", "r10_best_config_K2048")
(REPO / "experiments" / "exp_wave14b_r10_best_config_K2048.py").write_text(v)
print("wrote exp_wave14b_r10_best_config_K2048.py")

# CPU: fork ACF very extended K (more levels at the cliff)
acf_base = (REPO / "experiments" / "exp_wave14b_acf_K_dependent.py").read_text()
v = acf_base.replace(
    "K_SWEEP = [2048, 2304, 2560, 3072, 4096, 6144]",
    "K_SWEEP = [1280, 1536, 1792, 2048, 2176, 2304, 2432, 2560, 2688, 2816, 2944, 3072, 3200, 3328, 3456, 3584, 3712, 3840, 4096, 4608, 5120, 5632, 6144, 7168, 8192]"
).replace("NUM_TRIALS = 30", "NUM_TRIALS = 50").replace(
    "exp_wave14b_acf_K_dependent", "exp_wave14b_acf_K_very_extended_50trials"
)
(REPO / "experiments" / "exp_wave14b_acf_K_very_extended_50trials.py").write_text(v)
print("wrote exp_wave14b_acf_K_very_extended_50trials.py")

# CPU: fork decompose K-cliff with B variations (B=3 instead of B=2)
dec_base = (REPO / "experiments" / "exp_wave14b_decompose_K_cliff.py").read_text()
v = dec_base.replace("B = 2", "B = 3")
v = v.replace("K_SWEEP = [2304, 2560, 2816, 3072, 3328, 3584, 3840]",
              "K_SWEEP = [1024, 1280, 1536, 1792, 2048, 2304, 2560, 2816]")
v = v.replace("exp_wave14b_decompose_K_cliff", "exp_wave14b_decompose_K_cliff_B3")
(REPO / "experiments" / "exp_wave14b_decompose_K_cliff_B3.py").write_text(v)
print("wrote exp_wave14b_decompose_K_cliff_B3.py")

# === Queue items ===
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
gpu_new = [
    {"name": "wave14d_icl_via_pool_K4", "script": "experiments/exp_wave14d_in_context_learning_via_pool.py",
     "status": "pending",
     "purpose": "Does pool retrieval do in-context learning? Tests if adding novel-domain examples to pool at query time improves predictions. If yes, instant product moat.",
     "timeout_s": 3600},
    {"name": "wave14d_generation_K4", "script": "experiments/exp_wave14d_generation_via_sample_feedback.py",
     "status": "pending",
     "purpose": "Can substrate autoregressively generate via sample-feedback? Opens/closes Tier-1 GPT-quality+audit killer.",
     "timeout_s": 3600},
    {"name": "wave14d_icl_via_pool_K8", "script": "experiments/exp_wave14d_icl_via_pool_K8.py",
     "status": "pending",
     "purpose": "ICL via pool at K=8. Does pool-based ICL scale with K?",
     "timeout_s": 5400},
    {"name": "wave14d_icl_via_pool_K16", "script": "experiments/exp_wave14d_icl_via_pool_K16.py",
     "status": "pending",
     "purpose": "ICL via pool at K=16.",
     "timeout_s": 7200},
    {"name": "wave14d_generation_K8", "script": "experiments/exp_wave14d_generation_K8.py",
     "status": "pending",
     "purpose": "Autoregressive generation at K=8. Does longer context maintain coherence further?",
     "timeout_s": 3600},
    {"name": "wave14d_generation_K16", "script": "experiments/exp_wave14d_generation_K16.py",
     "status": "pending",
     "purpose": "Autoregressive generation at K=16.",
     "timeout_s": 5400},
    {"name": "r10_best_config_K2048", "script": "experiments/exp_wave14b_r10_best_config_K2048.py",
     "status": "pending",
     "purpose": "R10 best-config K=2048. Extends curve from +0.628 (K=512). If still monotone, headline pushes toward +0.8.",
     "timeout_s": 18000},
]
gpu_q["experiments"].extend(gpu_new)
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))

cpu_q_path = REPO / "data" / "remote_cpu_queue" / "queue.json"
cpu_q = json.loads(cpu_q_path.read_text())
cpu_new = [
    {"name": "acf_K_very_extended_50trials", "script": "experiments/exp_wave14b_acf_K_very_extended_50trials.py",
     "status": "pending",
     "purpose": "ACF K-sweep: 25 K levels x 50 trials. Resolves K=2944 dip via density; maps the whole cliff at higher trial count.",
     "timeout_s": 21600},
    {"name": "decompose_K_cliff_B3", "script": "experiments/exp_wave14b_decompose_K_cliff_B3.py",
     "status": "pending",
     "purpose": "K-cliff at B=3 (vs canonical B=2). Tests whether cliff scales with bundle size or is bundle-size-independent.",
     "timeout_s": 14400},
]
cpu_q["experiments"].extend(cpu_new)
cpu_q_path.write_text(json.dumps(cpu_q, indent=2))

print(f"\nGPU pending after fill ({sum(1 for e in gpu_q['experiments'] if e['status']=='pending')} pending):")
for e in gpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
print(f"\nCPU pending after fill ({sum(1 for e in cpu_q['experiments'] if e['status']=='pending')} pending):")
for e in cpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
