"""Queue the final two wave14f experiments."""
import json
from pathlib import Path
REPO = Path(r"C:\dev\hd-instrument")
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
gpu_q["experiments"].extend([
    {"name": "wave14f_icl_rsb_synergy", "script": "experiments/exp_wave14f_icl_rsb_synergy.py",
     "status": "pending",
     "purpose": "ICL x RSB synergy: does ICL gain depend on tree-cluster membership of added examples? 3-cell (close/sibling/distant) lean test at K=4, N_aug=64, 3 seeds. Resolves tree-close vs tree-distant ambiguity per research.",
     "timeout_s": 3600},
    {"name": "wave14f_icl_scaling_pool", "script": "experiments/exp_wave14f_icl_scaling_pool.py",
     "status": "pending",
     "purpose": "ICL gain scaling with POOL_SIZE in {512, 1024, 2048, 4096} + shuffled-pool diagnostic to separate retrieval-side from encoder-side gain. Decisive on whether ICL is real retrieval or encoder artifact.",
     "timeout_s": 7200},
])
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))
print(f"GPU pending: {sum(1 for e in gpu_q['experiments'] if e['status']=='pending')}")
for e in gpu_q["experiments"][-3:]:
    print(f"  + {e['name']}")
