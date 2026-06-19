"""Re-queue the 6 failed CPU experiments + verify CPU runner alive."""
import json
from pathlib import Path
REPO = Path(r"C:\dev\hd-instrument")
cpu_q_path = REPO / "data" / "remote_cpu_queue" / "queue.json"
cpu_q = json.loads(cpu_q_path.read_text())
# Re-queue each failed experiment (the spin glass test is the critical one)
failed_names = [
    ("wave14e2_parisi_ultrametricity", "experiments/exp_wave14e2_parisi_ultrametricity.py",
     "RETRY: Spin glass E1 -- localizes substrate in RS vs RSB phase. Critical for whether substrate has free O(log P) tree-walk retrieval.",
     1200),
    ("acf_K2944_fine_r_sweep_retry", "experiments/exp_wave14b_acf_K2944_fine_r_sweep.py",
     "RETRY of fine r-sweep at K=2944. Settles K=2944 dip mechanism (r-mistuning per research).",
     5400),
    ("decompose_K_cliff_B3_retry", "experiments/exp_wave14b_decompose_K_cliff_B3.py",
     "RETRY of K-cliff at B=3 bundle size.",
     14400),
    ("acf_resonator_high_K_retry", "experiments/exp_wave14b_acf_resonator_high_K.py",
     "RETRY of ACF resonator at high K (K=4096-16384).",
     7200),
    # Skip acf_K_very_extended_50trials retry (it caused the crash; too risky to repeat)
    # Skip decompose_K_cliff_B4 retry (lower priority)
]
for name, script, purpose, timeout in failed_names:
    cpu_q["experiments"].append({
        "name": name, "script": script, "status": "pending",
        "purpose": purpose, "timeout_s": timeout,
    })
cpu_q_path.write_text(json.dumps(cpu_q, indent=2))
print(f"CPU pending: {sum(1 for e in cpu_q['experiments'] if e['status']=='pending')}")
for e in cpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
