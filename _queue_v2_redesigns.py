"""Queue the 4 v2 redesigns based on research findings."""
import json
from pathlib import Path
REPO = Path(r"C:\dev\hd-instrument")
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
gpu_q["experiments"].extend([
    {"name": "wave14e_hierarchical_v2", "script": "experiments/exp_wave14e_hierarchical_v2.py",
     "status": "pending",
     "purpose": "Hierarchical composition v2: 3-level hierarchy with Hopfield cleanup BETWEEN levels (Plate 1995 chunking). v1 lacked cleanup; v2 enables depth 5-6.",
     "timeout_s": 1800},
    {"name": "wave14e_multi_hop_v2", "script": "experiments/exp_wave14e_multi_hop_v2.py",
     "status": "pending",
     "purpose": "Multi-hop reasoning v2: bound triples e=subj*rel*obj with per-hop Hopfield cleanup. Per research, BSC self-inverse algebra makes chains clean. Predicted 50+ hops viable.",
     "timeout_s": 1200},
    {"name": "wave14e_continuous_edits_v2", "script": "experiments/exp_wave14e_continuous_edits_v2.py",
     "status": "pending",
     "purpose": "Continuous edits v2: per-coordinate Bernoulli mixing (NOT deterministic blend which fails at alpha=0.5). 200 samples per alpha for population average.",
     "timeout_s": 1800},
    {"name": "wave14e_lsh_v2_binaryivf", "script": "experiments/exp_wave14e_lsh_v2_binaryivf.py",
     "status": "pending",
     "purpose": "LSH v2: BinaryIVF (k-means centroids + Voronoi partition). Per research, SimHash gives ro=0.87 (marginal); BinaryIVF exploits actual pool clustering at our high-radius regime.",
     "timeout_s": 1800},
])
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))
print(f"GPU pending after v2: {sum(1 for e in gpu_q['experiments'] if e['status']=='pending')}")
for e in gpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
