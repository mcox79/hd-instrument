"""One-shot helper: mark partial + add 5 new pending items to GPU queue."""
import json
from pathlib import Path

p = Path(r"C:\dev\hd-instrument\data\overnight_queue\queue.json")
q = json.loads(p.read_text())

for e in q["experiments"]:
    if e["name"] == "r10_best_config_K16_K32_K64" and e["status"] == "running":
        e["status"] = "partial"
        e["note"] = ("completed K=16 and K=32 (3 seeds each), K=64 seed=17 done (+0.318 best post_gap), "
                     "crashed mid K=64 seed=23. Verify K=64 with r10_best_config_K64_verify.")

new_items = [
    {"name": "r10_best_config_K64_verify",
     "script": "experiments/exp_wave14b_r10_best_config_K64_verify.py",
     "status": "pending",
     "purpose": "Verify K=64 best-config (3 seeds, +0.318 expected) -- prior K16_K32_K64 run crashed before completing K=64.",
     "timeout_s": 3600},
    {"name": "r3_unigram_diagnostic",
     "script": "experiments/exp_wave14b_r3_unigram_diagnostic.py",
     "status": "pending",
     "purpose": "wave14c hypothesis test: R3 +0.032 is class-prior re-injection. Predicted unigram gain ~0.022; if residual<0.01 retract R3.",
     "timeout_s": 1800},
    {"name": "r10_best_config_K2_K4_K8",
     "script": "experiments/exp_wave14b_r10_best_config_K2_K4_K8.py",
     "status": "pending",
     "purpose": "R10 best-config below K=16. Does the +180-200% improvement hold at low K or is it K-scaling specific?",
     "timeout_s": 3600},
    {"name": "r3_disjoint_K16",
     "script": "experiments/exp_wave14b_r3_disjoint_K16.py",
     "status": "pending",
     "purpose": "R3 disjoint concepts at K=16. Does the +0.025 disjoint-compound gain scale up with K like R10 does?",
     "timeout_s": 3600},
    {"name": "r10_best_config_K512",
     "script": "experiments/exp_wave14b_r10_best_config_K512.py",
     "status": "pending",
     "purpose": "R10 best-config K=512. If +0.543 at K=256 extends, K=512 could push toward +0.7-0.8 bpc post-shift gap.",
     "timeout_s": 10800},
]
q["experiments"].extend(new_items)
p.write_text(json.dumps(q, indent=2))
print("Queue now:")
for e in q["experiments"]:
    print(f"  - {e['name']:40s} {e['status']}")
