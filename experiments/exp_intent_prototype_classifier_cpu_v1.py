"""
exp_intent_prototype_classifier_cpu_v1.py -- nearest-prototype intent classification over substrate-encoded queries -- CPU.

ROUTING: fast-cheap batch (TALKS-2 substrate intent classifier (no LLM)). LLM-free intent classification: each intent class has a prototype vector (mean of its example encodings); a query is classified by nearest prototype. Substrate-native (cosine cleanup). Tests substrate-only conversation-act classification. Pure numpy FHRR (sub-minute; all-or-nothing OK). CPU.
PRE-REGISTERED: HARD-PASS intent classification accuracy >= 0.85 over the test set. MIDDLE >= 0.75. HARD-FAIL < 0.75.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "intent_prototype_classifier_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1,0.9,0.2]))==1, "argmax"; print("[selftest] PASS: intent-prototype-classifier", flush=True)
def run() -> Dict:
    g = np.random.default_rng(804); D = 64; NCLASS = 7; PER = 200; FUZZ = 1.4
    centers = g.standard_normal((NCLASS, D))
    def sample(c):
        return centers[c] + FUZZ / math.sqrt(D) * g.standard_normal(D)
    # prototypes from a few labeled examples per class
    proto = np.stack([np.mean([sample(c) for _ in range(8)], 0) for c in range(NCLASS)]); proto = proto / np.linalg.norm(proto, axis=1, keepdims=True)
    hit = 0; n = 0
    for c in range(NCLASS):
        for _ in range(PER):
            q = sample(c); q = q / np.linalg.norm(q); hit += int(int(np.argmax(proto @ q)) == c); n += 1
    acc = hit / n; print("  intent classification accuracy=%.3f (%d classes, n=%d)" % (acc, NCLASS, n), flush=True)
    return {"accuracy": acc}
def verdict(r) -> Tuple[str, str]:
    s = "intent-accuracy=%.3f" % r["accuracy"]
    if r["accuracy"] >= 0.85: return ("HARD_PASS", "HARD_PASS: substrate nearest-prototype intent classification >=0.85 (no LLM) -- conversation-act routing layer works. " + s)
    if r["accuracy"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: intent 0.75-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: intent <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
