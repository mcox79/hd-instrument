"""Queue wave14e2 (iteration-2 materials-science) experiments."""
import json
from pathlib import Path
REPO = Path(r"C:\dev\hd-instrument")
cpu_q_path = REPO / "data" / "remote_cpu_queue" / "queue.json"
cpu_q = json.loads(cpu_q_path.read_text())
cpu_q["experiments"].append({
    "name": "wave14e2_parisi_ultrametricity",
    "script": "experiments/exp_wave14e2_parisi_ultrametricity.py",
    "status": "pending",
    "purpose": "Spin glass E1: Parisi P(q) + ultrametricity on substrate pool. RS phase = ~350K bundle headroom (Frady-Sommer). RSB = emergent O(log P) tree-walk index. Decisive 10-min CPU test.",
    "timeout_s": 1200,
})
cpu_q_path.write_text(json.dumps(cpu_q, indent=2))

gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
gpu_q["experiments"].append({
    "name": "wave14e2_ssh_bsc_topological",
    "script": "experiments/exp_wave14e2_ssh_bsc_topological.py",
    "status": "pending",
    "purpose": "SSH-BSC chiral topological substrate. Categorical (not statistical) noise immunity via integer winding number (chiral class AIII). Predicted SHARP KINK in noise tolerance vs random-baseline smooth decay. The big bet.",
    "timeout_s": 1800,
})
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))
print(f"GPU pending: {sum(1 for e in gpu_q['experiments'] if e['status']=='pending')}")
print(f"CPU pending: {sum(1 for e in cpu_q['experiments'] if e['status']=='pending')}")
