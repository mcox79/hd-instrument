"""Queue 5 new experiments: 4 quick forks + K-adaptive R10."""
import json
from pathlib import Path
REPO = Path(r"C:\dev\hd-instrument")
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
new = [
    {"name": "wave14f_r10_K_adaptive", "script": "experiments/exp_wave14f_r10_K_adaptive.py",
     "status": "pending",
     "purpose": "K-adaptive R10 schedule: lam(K)/beta(K)/nc(K) sigmoid per wave14c2 research. Tests if adaptive matches default at K<8 and best at K>=32 -- unifying the K-curve.",
     "timeout_s": 18000},
    {"name": "r10_best_config_K1024_retry2", "script": "experiments/exp_wave14b_r10_best_config_K1024_retry2.py",
     "status": "pending",
     "purpose": "R10 best-config K=1024 clean retry (prior was zombie). Extends K-curve to K=1024 -- predicts toward +0.7 if monotone trend continues.",
     "timeout_s": 14400},
    {"name": "r10_best_config_K2048_retry", "script": "experiments/exp_wave14b_r10_best_config_K2048_retry.py",
     "status": "pending",
     "purpose": "R10 best-config K=2048. Top of K-curve. If still monotone, headline +0.8 region.",
     "timeout_s": 21600},
    {"name": "wave14d_generation_v2_K32", "script": "experiments/exp_wave14d_generation_v2_K32.py",
     "status": "pending",
     "purpose": "Generation v2 at K=32. Per research, K=4-16 capture byte-match but not word-coherence (English words exceed K=4). K=32 should transition to word-level coherence.",
     "timeout_s": 5400},
    {"name": "wave14d_generation_v2_K64", "script": "experiments/exp_wave14d_generation_v2_K64.py",
     "status": "pending",
     "purpose": "Generation v2 at K=64. Tests upper limit of K=4-byte word coherence regime.",
     "timeout_s": 7200},
]
gpu_q["experiments"].extend(new)
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))
print(f"GPU pending after wave14f add: {sum(1 for e in gpu_q['experiments'] if e['status']=='pending')}")
for e in gpu_q["experiments"][-5:]:
    print(f"  + {e['name']}")
