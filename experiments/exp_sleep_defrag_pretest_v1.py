"""
exp_sleep_defrag_pretest_v1 -- C5: sleep-defrag implicit-generalization closure pre-test (synthetic) -- CPU.

ROUTING: 2hour battery C5. Tests the "50-60% domain-specific implicit-generalization closure" claim. 100 synthetic
  fever-class Pattern B facts share a latent regularity (e.g. role FEVER co-occurs with filler INFECTION across many cases
  with surface variation). A co-occurrence aggregator ("sleep defrag") bundles the cases into a consolidated regularity
  vector; we test whether that consolidated vector RECOVERS the latent regularity (the implicit generalization) that no
  single stored case states explicitly. FHRR phasors; aggregator = normalized bundle of unbound role->filler evidence.
PRE-REGISTERED (per drill recipe): HARD-PASS aggregated-regularity cosine to the true latent filler >= 0.65 AND the true
  filler ranks #1 in the codebook cleanup. MIDDLE one of the two. HARD-FAIL neither (no implicit generalization).
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind inverse. 2. cleanup self. 3. aggregator points to majority.
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

ANCHOR_NAME = "sleep_defrag_pretest_v1"; D = 2048
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_CASES = 30 if RUN_MODE == "smoke" else 100; N_FILLERS = 20; NOISE = 0.6; MAJ = 0.55


def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)


def unit(v):
    return v / (np.abs(v) + 1e-8)


def bind(a, b):
    return a * b


def unbind(c, b):
    return c * np.conj(b)


def cleanup_idx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def cos(a, b):
    return float((np.vdot(a, b)).real / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


def _selftest():
    g = np.random.default_rng(0); a = phasor(1, 32, g)[0]; b = phasor(1, 32, g)[0]
    assert np.allclose(unbind(bind(a, b), b), a, atol=1e-4), "bind/unbind inverse"
    book = phasor(5, 32, g); assert cleanup_idx(book[3], book) == 3, "cleanup self"
    agg = book[1] + book[1] + book[2]; assert cleanup_idx(agg, book) == 1, "aggregator points to majority"
    print("[selftest] PASS: sleep-defrag-pretest", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(13)
    book = phasor(N_FILLERS, D, g)             # filler codebook (e.g. diagnoses)
    role = phasor(1, D, g)[0]                   # the shared role (e.g. "fever ->")
    true_filler = 0                             # latent regularity: FEVER co-occurs with filler #0 in the majority
    cases = []
    for _ in range(N_CASES):
        # majority of cases bind role->true_filler (with surface noise); minority bind to a random other filler
        if g.random() < MAJ:
            f = true_filler
        else:
            f = int(g.integers(1, N_FILLERS))
        surface = unit(book[f] + NOISE * phasor(1, D, g)[0])     # surface variation per case
        cases.append(bind(role, surface))
    # sleep-defrag aggregator: unbind the shared role from each case, bundle the evidence, normalize
    evidence = [unbind(c, role) for c in cases]
    agg = np.sum(evidence, axis=0)
    rank1 = cleanup_idx(agg, book)
    c_true = cos(agg, book[true_filler])
    c_other = max(cos(agg, book[j]) for j in range(N_FILLERS) if j != true_filler)
    print("  aggregated-regularity: cosine_to_true=%.3f best_other=%.3f rank1_filler=%d (true=%d) maj=%.2f noise=%.2f n=%d" % (c_true, c_other, rank1, true_filler, MAJ, NOISE, N_CASES), flush=True)
    return {"cos_true": c_true, "cos_other": c_other, "rank1": rank1, "true": true_filler, "n": N_CASES}


def verdict(r) -> Tuple[str, str]:
    ranks1 = (r["rank1"] == r["true"]); cos_ok = (r["cos_true"] >= 0.65)
    summary = "cosine_to_true_regularity=%.3f (best_other=%.3f) rank1_correct=%s n=%d" % (r["cos_true"], r["cos_other"], ranks1, r["n"])
    if cos_ok and ranks1:
        return ("HARD_PASS", "HARD_PASS: sleep-defrag aggregator RECOVERS the latent regularity no single case states (cosine>=0.65 AND correct filler ranks #1) -- implicit generalization / continual-learning closure supported. " + summary)
    if cos_ok or ranks1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial implicit generalization (one of cosine>=0.65 / rank1 holds). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: aggregator does not recover the latent regularity (no implicit generalization at this noise/majority). " + summary)


print("[config] anchor=%s mode=%s D=%d cases=%d fillers=%d noise=%.2f" % (ANCHOR_NAME, RUN_MODE, D, N_CASES, N_FILLERS, NOISE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
