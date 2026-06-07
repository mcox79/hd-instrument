"""
exp_qdef_watermark_canary_v1 -- quantum-defenses anchor 3 (zero-cost MIA detection) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_chain1_drill4_quantum_defenses (#3). Insert canary facts; run a paraphrase
  extraction attack; if a canary appears in the adversary's extracted set, the DEFENDER detects the extraction from the KF-1
  grounding flag (the canary is a known-planted fact whose retrieval signals an active extraction campaign). Validates a
  zero-cost membership-inference-detection feature. CPU $0.
PRE-REGISTERED (research bands): HARD-PASS 10/10 canaries detected when extracted by the adversary. MID 7-9/10. HARD-FAIL
  < 7/10 (canary detection unreliable).
FORMULA SELF-TESTS (PROT-022): 1. canary retrievable. 2. paraphrase preserves grounding. 3. cosine bound.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "qdef_watermark_canary_v1"
N = 2048; N_CANARY = 10; PARA_MIX = 0.30; GROUND_THR = 0.40
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_KB = 400 if RUN_MODE == "smoke" else 3000


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); kb = unit(g.standard_normal((10, 64))); q = kb[3]
    assert int(np.argmax(kb @ q)) == 3, "canary retrievable"
    p = unit(0.7 * kb[3] + 0.3 * unit(g.standard_normal(64))); assert (p @ kb[3]) > 0.5, "paraphrase preserves grounding"
    assert abs(float(unit(np.ones((1, 4)))[0] @ unit(np.ones((1, 4)))[0]) - 1.0) < 1e-5, "cosine bound"
    print("[selftest] PASS: watermark-canary", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); kb = unit(g.standard_normal((N_KB, N)).astype(np.float32))
    canaries = unit(g.standard_normal((N_CANARY, N)).astype(np.float32))
    full_kb = np.vstack([kb, canaries]); canary_ids = set(range(N_KB, N_KB + N_CANARY))
    # adversary issues paraphrase queries targeting each canary (simulating it tries to extract everything)
    detected = 0
    for ci in range(N_CANARY):
        para = unit((1 - PARA_MIX) * canaries[ci] + PARA_MIX * unit(g.standard_normal(N).astype(np.float32)))
        ground = full_kb @ para; top = int(np.argmax(ground))
        # defender flag: top hit is a planted canary AND grounding exceeds threshold (extraction signal)
        if top in canary_ids and ground[top] > GROUND_THR:
            detected += 1
    print("  canaries=%d detected=%d (thr=%.2f)" % (N_CANARY, detected, GROUND_THR), flush=True)
    return {"n_canary": N_CANARY, "detected": detected}


def verdict(r) -> Tuple[str, str]:
    d = r["detected"]; n = r["n_canary"]
    summary = "%d/%d canaries detected on extraction" % (d, n)
    if d >= n:
        return ("HARD_PASS", "HARD_PASS: 10/10 canaries detected when extracted -- zero-cost MIA-detection feature works. " + summary)
    if d >= 7:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 7-9/10 canaries detected (qualify). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: <7/10 detected -- canary detection unreliable. " + summary)


print("[config] anchor=%s mode=%s n_kb=%d n_canary=%d" % (ANCHOR_NAME, RUN_MODE, N_KB, N_CANARY), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
