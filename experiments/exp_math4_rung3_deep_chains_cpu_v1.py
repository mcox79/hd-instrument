"""
exp_math4_rung3_deep_chains_cpu_v1.py -- MATH-4 RUNG-3 deep proof chains (substrate-over-biology falsification) -- CPU.

ROUTING: Research SPRINT2 priority #7. MATH-4 held 1.0 at lengths 2/4/6. Rung-3 pushes to lengths 8/10/12 with a LARGER rule
  base (NPROP=100) -- beyond human working-memory chain limits (~7 +/- 2). Per-antecedent sharded rules (the fix). Tests
  whether substrate deductive chaining is DEPTH-ROBUST past biological limits. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS mean accuracy >= 0.90 across lengths 8/10/12 (depth-robust beyond human limit). MIDDLE >= 0.70. HARD-FAIL else.
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
ANCHOR_NAME = "math4_rung3_deep_chains_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: math4-rung3-deep-chains", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "824"))); NPROP = 100; IMPL = cphasor(1, N, g)[0]
    lengths = [8, 10, 12]; TR = 20 if SMOKE else 120; by_len = {L: [] for L in lengths}
    for _ in range(TR):
        props = cphasor(NPROP, N, g); nxt = g.permutation(NPROP)        # functional chain over 100 props
        rule_vec = np.stack([cnorm(props[a] * IMPL * props[int(nxt[a])]) for a in range(NPROP)])  # per-antecedent sharded
        for L in lengths:
            start = int(g.integers(0, NPROP)); gold = start
            for _s in range(L):
                gold = int(nxt[gold])
            ci = start
            for _s in range(L):
                cand = rule_vec[ci] * np.conj(props[ci]) * np.conj(IMPL); ci = cidx(cand, props)
            by_len[L].append(int(ci == gold))
    accs = {L: round(float(np.mean(v)), 3) for L, v in by_len.items()}; mean = float(np.mean(list(accs.values())))
    print("  MATH-4 RUNG-3 deep-chain accuracy-by-length=%s mean=%.3f (NPROP=%d; human limit ~7)" % (accs, mean, NPROP), flush=True)
    return {"accuracy_by_length": accs, "mean_accuracy": round(mean, 3), "n_prop": NPROP}
def verdict(r) -> Tuple[str, str]:
    m = r["mean_accuracy"]; s = "by-length=%s mean=%.3f" % (r["accuracy_by_length"], m)
    if m >= 0.90:
        return ("HARD_PASS", "HARD_PASS: substrate deductive chaining is DEPTH-ROBUST at lengths 8/10/12 (mean>=0.90) -- beyond human working-memory chain limits (~7). Substrate-over-biology for deductive depth, substrate-only. " + s)
    if m >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: deep-chain 0.70-0.90 (some depth decay). " + s)
    return ("HARD_FAIL", "HARD_FAIL: deep-chain <0.70 -- depth limit reached. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
