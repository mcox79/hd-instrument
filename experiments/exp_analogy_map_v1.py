"""
exp_analogy_map_v1 -- Batch A Rank 3: relational reasoning via bundle-space arithmetic (A:B::C:?) -- CPU.

ROUTING: Research Batch A (new capability class). Relation R binds A->B (B = A*R; bipolar bind = elementwise product,
  self-inverse). Infer R from a BUNDLE of example pairs, apply to held-out C -> predict D; success = nearest test-D atom.
  HARD-PASS -> relational queries without an LLM call.
PRE-REGISTERED: HARD-PASS analogy accuracy >= 0.70. MID 0.5-0.7. HF < 0.5.
FORMULA SELF-TESTS (PROT-022): 1. bind self-inverse. 2. single-pair R exact.
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

ANCHOR_NAME = "analogy_map_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; N_VOCAB = 400; N_PAIRS = 20; N_TEST = 100
else:
    SEEDS = [7, 17, 23]; N = 8192; N_VOCAB = 2000; N_PAIRS = 40; N_TEST = 300


def bp(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def _selftest():
    g = np.random.default_rng(0); a = bp(1, 256, g); r = bp(1, 256, g); b = a * r
    assert np.array_equal(b * r, a), "bind self-inverse"
    assert np.array_equal((a * b), r), "single-pair R = a*b exact"
    print("[selftest] PASS: bind", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); V = bp(N_VOCAB, N, g); R = bp(1, N, g)[0]
    idx = g.choice(N_VOCAB, 2 * (N_PAIRS + N_TEST), replace=False)
    A = V[idx[:N_PAIRS]]; B = A * R
    R_hat = np.sign((A * B).sum(0)); R_hat[R_hat == 0] = 1.0             # infer R from bundle of A*B
    C = V[idx[N_PAIRS:N_PAIRS + N_TEST]]; D_true = C * R; D_pred = C * R_hat
    sims = D_pred @ D_true.T / N
    acc = float(np.mean(np.argmax(sims, axis=1) == np.arange(N_TEST)))
    return {"seed": seed, "N": N, "analogy_accuracy": acc}


def verdict(ps) -> Tuple[str, str]:
    a = float(np.mean([p["analogy_accuracy"] for p in ps]))
    summary = "analogy_accuracy=%.3f (N=%d, %d-way)" % (a, ps[0]["N"], N_TEST)
    if a >= 0.70:
        return ("HARD_PASS", "HARD_PASS: native relational reasoning via bundle arithmetic (acc>=0.70) -- relational queries without LLM. " + summary)
    if a >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial relational reasoning (0.5-0.7). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no native relational reasoning (<0.5). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d vocab=%d pairs=%d test=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_VOCAB, N_PAIRS, N_TEST), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r); print("  [seed=%d] analogy_accuracy=%.3f" % (seed, r["analogy_accuracy"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
