"""Queue all wave14e math-gap probes."""
import json
from pathlib import Path
REPO = Path(r"C:\dev\hd-instrument")
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
new = [
    {"name": "wave14e_lsh_for_bsc", "script": "experiments/exp_wave14e_lsh_for_bsc.py",
     "status": "pending",
     "purpose": "LSH for BSC bipolar pool. Pass if recall@10 >=0.9 at >=10x speedup. Unlocks 10M+ pool size (effectively unbounded context).",
     "timeout_s": 1800},
    {"name": "wave14e_substrate_uncertainty", "script": "experiments/exp_wave14e_substrate_uncertainty.py",
     "status": "pending",
     "purpose": "Substrate-native uncertainty. Pass if any internal signal has abstention AUROC >0.7. Enables trust-layer.",
     "timeout_s": 1800},
    {"name": "wave14e_polarity_binding", "script": "experiments/exp_wave14e_polarity_binding.py",
     "status": "pending",
     "purpose": "Polarity (truth-conditional) binding. Pass if substrate distinguishes positive/negative facts at >=90%. Enables negation.",
     "timeout_s": 600},
    {"name": "wave14e_continuous_edits", "script": "experiments/exp_wave14e_continuous_edits.py",
     "status": "pending",
     "purpose": "Continuous alpha-interpolated edits via soft bipolar (tanh). Pass if P(byte) moves monotonically with alpha at >=80%.",
     "timeout_s": 600},
    {"name": "wave14e_temporal_binding", "script": "experiments/exp_wave14e_temporal_binding.py",
     "status": "pending",
     "purpose": "Sinusoidal time atom as a third binding factor. Pass if substrate distinguishes 10 time bins at >=80%.",
     "timeout_s": 600},
    {"name": "wave14e_multi_hop_reasoning", "script": "experiments/exp_wave14e_multi_hop_reasoning.py",
     "status": "pending",
     "purpose": "2-hop and 3-hop chained reasoning via decompose-rebind. v1 minimal probe. v2 after research.",
     "timeout_s": 600},
    {"name": "wave14e_hierarchical_composition", "script": "experiments/exp_wave14e_hierarchical_composition.py",
     "status": "pending",
     "purpose": "2-level hierarchical bundle composition (byte-words into phrase-bundles). v1 minimal probe.",
     "timeout_s": 600},
]
gpu_q["experiments"].extend(new)
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))
print(f"GPU pending: {sum(1 for e in gpu_q['experiments'] if e['status']=='pending')}")
for e in gpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
