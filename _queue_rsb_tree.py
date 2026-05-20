"""Queue the RSB tree-walk experiment (CPU - mostly numpy)."""
import json
from pathlib import Path
REPO = Path(r"C:\dev\hd-instrument")
cpu_q_path = REPO / "data" / "remote_cpu_queue" / "queue.json"
cpu_q = json.loads(cpu_q_path.read_text())
cpu_q["experiments"].append({
    "name": "wave14f_rsb_tree_walk",
    "script": "experiments/exp_wave14f_rsb_tree_walk.py",
    "status": "pending",
    "purpose": "EXPLOITS confirmed RSB phase. Builds single-linkage Parisi tree on pool, beam-searches via tree. Predicted recall@10: 0.36/0.51/0.76/0.95 at beam=1/2/4/8 at our ultrametricity 0.357. First test of O(log P) hierarchical retrieval primitive.",
    "timeout_s": 3600,
})
cpu_q_path.write_text(json.dumps(cpu_q, indent=2))
print(f"CPU pending: {sum(1 for e in cpu_q['experiments'] if e['status']=='pending')}")
for e in cpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
