"""Queue the 5 MVP-gating experiments via parameter-variant forks of validated scripts.

Per MVP session output:
  R1/mvp1: ICL saturation cap > N=2048 → fork icl_via_pool_v2 with N up to 16384
  R2/mvp1: multi-task distribution-shift ICL → fork icl_via_pool_v2 with extreme-shift corpus B
  R1/mvp2: calibration quality → already queued as wave14e_substrate_uncertainty
  R1/mvp3: edit fidelity at K=64 → fork sequential_edit_stress at K=64
  R3/mvp3: erase-under-replay → new minimal experiment

Per protocol D: don't queue polarity/temporal at K>=512 (B=3 cliff).
"""
import json
import re
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")

# Fork 1: ICL saturation extended (mvp1 R1)
icl_base = (REPO / "experiments" / "exp_wave14d_icl_via_pool_v2.py").read_text()
v = re.sub(r"N_EXAMPLES\s*=\s*\[[^\]]+\]",
           "N_EXAMPLES = [0, 64, 256, 1024, 2048, 4096, 8192, 16384]", icl_base, count=1)
v = v.replace("icl_via_pool_v2", "icl_saturation_extended")
(REPO / "experiments" / "exp_wave14g_icl_saturation_extended.py").write_text(v)
print("wrote exp_wave14g_icl_saturation_extended.py")

# Fork 2: ICL with genuine distribution shift (mvp1 R2)
v = (REPO / "experiments" / "exp_wave14d_icl_via_pool_v2.py").read_text()
# Replace load_corpus_b function to produce hex-encoded binary (large KL shift from markdown)
new_corpus = '''def load_corpus_b_json():
    """Genuine-shift corpus B: hex-encoded random bytes. Maximum byte-distribution KL from markdown."""
    import random
    random.seed(20260520)
    raw = bytes(random.randint(0, 255) for _ in range(40000))
    return raw.hex().encode("ascii")  # 80000 bytes of pure hex-digit chars 0-9a-f
'''
# Find and replace the existing load_corpus_b_json
v = re.sub(r"def load_corpus_b_json\(\):.*?return combined\n", new_corpus, v, count=1, flags=re.DOTALL)
v = v.replace("icl_via_pool_v2", "icl_genuine_shift_hex")
(REPO / "experiments" / "exp_wave14g_icl_genuine_shift_hex.py").write_text(v)
print("wrote exp_wave14g_icl_genuine_shift_hex.py")

# Fork 3: Sequential edit fidelity at K=64 (mvp3 R1)
edit_base = (REPO / "experiments" / "exp_wave14d_sequential_edit_stress.py").read_text()
v = edit_base.replace("K = 8\n", "K = 64\n")
v = v.replace("sequential_edit_stress", "edit_fidelity_K64")
(REPO / "experiments" / "exp_wave14g_edit_fidelity_K64.py").write_text(v)
print("wrote exp_wave14g_edit_fidelity_K64.py")

# Queue them on GPU
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
gpu_q["experiments"].extend([
    {"name": "wave14g_icl_saturation_extended", "script": "experiments/exp_wave14g_icl_saturation_extended.py",
     "status": "pending",
     "purpose": "MVP1 R1 gate: does ICL gain saturate beyond N=2048? Per kNN-LM scaling research, log-linear no saturation predicted through 9+ decades. Tests N up to 16384.",
     "timeout_s": 10800},
    {"name": "wave14g_icl_genuine_shift_hex", "script": "experiments/exp_wave14g_icl_genuine_shift_hex.py",
     "status": "pending",
     "purpose": "MVP1 R2 gate: does ICL work under maximum-KL distribution shift (markdown -> random hex)? Per multi-task CL research, substrate has no architectural advantage under genuine shift; ICL-specific test is open.",
     "timeout_s": 7200},
    {"name": "wave14g_edit_fidelity_K64", "script": "experiments/exp_wave14g_edit_fidelity_K64.py",
     "status": "pending",
     "purpose": "MVP3 R1 gate: do sequential edits survive at K=64 (R10 best-config regime)? Sequential_edit_stress at K=8 in queue; K=64 is the production regime.",
     "timeout_s": 7200},
])
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))
print(f"\nGPU pending: {sum(1 for e in gpu_q['experiments'] if e['status']=='pending')}")
