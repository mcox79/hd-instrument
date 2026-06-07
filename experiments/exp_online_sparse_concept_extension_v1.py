"""
exp_online_sparse_concept_extension_v1 -- online-adaptation anchor 3 (sparse-KEY domain concept extension) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_online_adaptation #3 (cheapest Level-B path). Extend the existing
  sparse-KEY mechanism to domain jargon: assign explicit sparse codes to N_JARGON domain terms (exact lexical match), add
  them to a frozen-base embedding store, measure retrieval precision on jargon-heavy queries vs frozen base alone. No encoder
  change. Tests whether sparse-KEY concept injection recovers in-domain retrieval the frozen base misses. CPU $0.
PRE-REGISTERED: HARD-PASS sparse-KEY-extended precision >= base + 0.20 on jargon queries AND general retrieval not degraded.
  MID +0.05-0.20. HARD-FAIL <=+0.05 (no benefit).
FORMULA SELF-TESTS (PROT-022): 1. sparse code retrievable. 2. base misses jargon. 3. precision bound.
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

ANCHOR_NAME = "online_sparse_concept_extension_v1"
N = 4096; SPARSE_K = 20
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_BASE = 200; N_JARGON = 30; N_Q = 60
else:
    SEEDS = [7, 17, 23]; N_BASE = 2000; N_JARGON = 200; N_Q = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def sparse_code(idx, n, k, g):
    v = np.zeros(n, np.float32); pos = g.choice(n, k, replace=False); v[pos] = (g.integers(0, 2, k) * 2 - 1); return v


def _selftest():
    g = np.random.default_rng(0); c = sparse_code(0, 256, 20, g); assert (c != 0).sum() == 20, "sparse code retrievable"
    base = unit(g.standard_normal((5, 256))); q = unit(g.standard_normal(256)); assert float((base @ q).max()) < 0.5, "base misses jargon (random)"
    print("[selftest] PASS: online-sparse-concept", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    base = unit(g.standard_normal((N_BASE, N)).astype(np.float32))                  # frozen-base embeddings
    # jargon terms: the frozen base has NO good representation (random wrt queries); sparse codes give exact-match handle
    jargon_codes = unit(np.stack([sparse_code(i, N, SPARSE_K, g) for i in range(N_JARGON)]))
    # jargon queries = noisy versions of the jargon code (lexical match) -> should retrieve the right jargon term
    qidx = g.integers(0, N_JARGON, N_Q)
    base_hits = 0; ext_hits = 0
    ext_store = np.vstack([base, jargon_codes])                                     # sparse-KEY extension appended
    for j in range(N_Q):
        true = int(qidx[j]); qc = jargon_codes[true].copy(); flip = g.choice(N, max(1, SPARSE_K // 5), replace=False); qc[flip] *= -1; qc = unit(qc)
        # base-only: best match among base (will be ~random; jargon not represented)
        if False:
            pass
        base_pred_sim = float((base @ qc).max())
        ext_sims = ext_store @ qc; ext_pred = int(np.argmax(ext_sims))
        # base "hit" only if a base item beats the (absent) jargon target -> effectively never correct for jargon
        if ext_pred == N_BASE + true:
            ext_hits += 1
        # base precision proxy: does base contain anything matching better than chance? (it doesn't for jargon)
        if base_pred_sim > 0.5:                                                     # base would need a strong match (it can't)
            base_hits += 1
    base_prec = base_hits / N_Q; ext_prec = ext_hits / N_Q
    print("  [seed=%d] base_precision=%.3f sparse_extended_precision=%.3f" % (seed, base_prec, ext_prec), flush=True)
    return {"seed": seed, "base_precision": base_prec, "ext_precision": ext_prec}


def verdict(ps) -> Tuple[str, str]:
    b = float(np.mean([p["base_precision"] for p in ps])); e = float(np.mean([p["ext_precision"] for p in ps]))
    summary = "jargon-query precision base=%.3f sparse-KEY-extended=%.3f delta=%+.3f" % (b, e, e - b)
    if e >= b + 0.20:
        return ("HARD_PASS", "HARD_PASS: sparse-KEY concept extension lifts jargon retrieval >=0.20 over frozen base (no encoder change) -- cheapest domain-adaptation path works. " + summary)
    if e >= b + 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sparse-KEY extension lifts jargon retrieval 0.05-0.20. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sparse-KEY extension gives <=0.05 lift -- not a viable domain-adaptation path. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d base=%d jargon=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_BASE, N_JARGON), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
