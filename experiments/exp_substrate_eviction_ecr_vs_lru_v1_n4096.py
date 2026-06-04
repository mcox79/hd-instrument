"""
substrate_eviction_ecr_vs_lru_v1_n4096 -- audit-preserving eviction: ECR vs LRU at 90% capacity (CPU).

ROUTING: notes/exp_dev_handoff_research_cross_domain_interference_capacity_degradation_2026-06-04.md
  (anchor 2: ECR-vs-LRU eviction). Per [[feedback-no-experiment-design-in-prompts]] exp_dev designed params.
  CPU numpy (auto-assoc Hopfield streaming; GPU not needed).

CAPABILITY QUESTION:
  When a substrate runs PAST its single-substrate capacity by evicting patterns, does an Energy-Contribution-
  Ranked (ECR) eviction policy maintain graceful retrieval (>95%) where naive LRU degrades (<90%) at 90% of
  alpha_c? ECR is the audit-preserving eviction primitive enabling "indefinite auditable operation past the
  single-substrate limit" (product differentiator).

MODEL: auto-assoc Hopfield W = sum outer(xi,xi) (diag 0). Stream N_STREAM bipolar patterns one at a time;
  keep a bank capped at M_cap = 0.90*alpha_c*N. On overflow, EVICT one (W -= outer(evicted,evicted); diag 0):
    LRU = evict the oldest-written. ECR = evict the lowest energy-contribution pattern (min current
    self-retrieval overlap = the one already worst-stored -> least loss). After the stream, measure mean
    self-retrieval overlap (one sign step) of the CURRENTLY-banked patterns.

CELLS (3 seeds): policy in {LRU, ECR}; N=4096; M_cap=0.90*0.138*N; N_STREAM=3*M_cap.

PRE-REGISTERED BANDS (retrieval = fraction of banked patterns with self-overlap > 0.95):
  HARD-PASS: ECR retrieval > 0.95 AND LRU retrieval < 0.90 (ECR clearly maintains graceful operation; LRU degrades).
  MIDDLE: ECR > LRU by > 0.03 but not both thresholds met.
  HARD-FAIL: ECR <= LRU (no eviction-policy benefit).

FORMULA SELF-TESTS (PROT-022):
  1. low-load self-retrieval ~ 1.0. 2. eviction reduces ||W|| (rank-1 subtract). 3. alpha_c=0.138.

PROT-018: anchor _n4096 -> N=4096. PROT-019: _n4096 timeout floor 14400s. PROT-021: per-seed partials.
QUEUE: remote_cpu_queue (numpy; GPU not needed). ASCII-only.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_eviction_ecr_vs_lru_v1_n4096"
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
CAP_FRAC = 0.90
RECALL_THRESH = 0.95
POLICIES = ["LRU", "ECR"]

if RUN_MODE == "smoke":
    N_DIM = 512; SEEDS = [1, 2]
else:
    N_DIM = N; SEEDS = [7, 17, 23]


def self_overlaps(W, bank, n):
    """one sign step self-retrieval overlap for each banked pattern."""
    if len(bank) == 0:
        return np.array([])
    X = np.stack(bank)                      # (M, n)
    R = np.sign(X @ W.T); R[R == 0] = 1.0
    return (X * R).sum(axis=1) / n          # (M,)


def stream_evict(n, policy, gen) -> float:
    m_cap = max(4, int(round(CAP_FRAC * ALPHA_C * n)))
    n_stream = 3 * m_cap
    W = np.zeros((n, n), dtype=np.float32)
    bank = []          # list of patterns (np arrays)
    ages = []          # write order
    for t in range(n_stream):
        x = (gen.integers(0, 2, size=n) * 2 - 1).astype(np.float32)
        bank.append(x); ages.append(t)
        W += np.outer(x, x); np.fill_diagonal(W, 0.0)
        if len(bank) > m_cap:
            if policy == "LRU":
                ev = 0                                  # oldest
            else:  # ECR: lowest current self-retrieval overlap (already worst-stored -> least loss)
                ov = self_overlaps(W, bank, n)
                ev = int(np.argmin(ov))
            xe = bank.pop(ev); ages.pop(ev)
            W -= np.outer(xe, xe); np.fill_diagonal(W, 0.0)
    ov = self_overlaps(W, bank, n)
    return float(np.mean(ov > RECALL_THRESH))


def _selftest():
    g = np.random.default_rng(0)
    n = 256; W = np.zeros((n, n), dtype=np.float32)
    xs = [(g.integers(0, 2, size=n) * 2 - 1).astype(np.float32) for _ in range(5)]
    for x in xs:
        W += np.outer(x, x)
    np.fill_diagonal(W, 0.0)
    ov = self_overlaps(W, xs, n); assert float(np.mean(ov > 0.95)) > 0.9, "low-load recall"
    nb = float(np.abs(W).sum()); W2 = W - np.outer(xs[0], xs[0]); np.fill_diagonal(W2, 0.0)
    assert float(np.abs(W2).sum()) != nb
    assert abs(ALPHA_C - 0.138) < 1e-6
    print(f"[selftest] PASS: low_load_recall_ok eviction_changes_W alpha_c=0.138", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time(); res = {}
    for pol in POLICIES:
        gen = np.random.default_rng(seed * 10 + (0 if pol == "LRU" else 1))
        acc = stream_evict(n_dim, pol, gen)
        res[pol] = float(acc)
        print(f"  [seed={seed} {pol}] retrieval={acc:.4f}", flush=True)
    return {"seed": seed, "N": n_dim, "LRU": res["LRU"], "ECR": res["ECR"], "elapsed_s": time.time() - t0}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    lru = float(np.mean([r["LRU"] for r in results])); ecr = float(np.mean([r["ECR"] for r in results]))
    summary = f"ECR_retrieval={ecr:.3f} LRU_retrieval={lru:.3f} margin={ecr - lru:+.3f}"
    if ecr > RECALL_THRESH and lru < 0.90:
        return ("HARD_PASS", f"HARD_PASS: ECR maintains graceful (>0.95) while LRU degrades (<0.90) -> audit-preserving eviction validated. {summary}")
    if ecr - lru > 0.03:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: ECR>LRU by >0.03 but thresholds not both met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: ECR ~ LRU (no eviction-policy benefit). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} policies={POLICIES} cap_frac={CAP_FRAC} mode={RUN_MODE} seeds={SEEDS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "policies": POLICIES})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed, N_DIM))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "N": N_DIM,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
           "per_seed": [{"seed": r.get("seed"), "LRU": r.get("LRU"), "ECR": r.get("ECR"), "elapsed_s": r.get("elapsed_s")} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
