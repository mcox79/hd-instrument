"""Queue ICL v2 + Generation v2 (research-informed redesigns)."""
import json
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
new_items = [
    {"name": "wave14d_icl_via_pool_v2", "script": "experiments/exp_wave14d_icl_via_pool_v2.py",
     "status": "pending",
     "purpose": "ICL v2 with research fixes: JSON corpus B (true distribution shift), N to 2048, ALPHA sweep including pool_only, POOL_SIZE=4096, 5 seeds + t-test at threshold 0.015. The decisive test.",
     "timeout_s": 5400},
    {"name": "wave14d_generation_v2_K16", "script": "experiments/exp_wave14d_generation_v2_K16.py",
     "status": "pending",
     "purpose": "Generation v2 with research fixes: K=16 (K=4 was diagnosis-only), B3 baseline (raw K-gram Markov chain), substrate-with-pool vs substrate-without-pool A/B, K-gram-validity metric. The decisive test.",
     "timeout_s": 7200},
]
gpu_q["experiments"].extend(new_items)
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))
print(f"Queue now has {sum(1 for e in gpu_q['experiments'] if e['status']=='pending')} pending GPU items.")
for e in gpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
