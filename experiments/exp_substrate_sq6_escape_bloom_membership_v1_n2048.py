"""
substrate_sq6_escape_bloom_membership_v1_n2048 -- SQ6 Escape: Bloom-substrate edge membership -- remote CPU.

ROUTING: exp_dev_handoff_research_substrate_negative_results_structural_analysis_2x (Escape #4, SQ6). SQ6 + SQ6-v2
  both HF: bundle G=sum(node_u*node_v) has a 1/sqrt(E) SNR wall for membership at E=O(N). Escape: BLOOM-SUBSTRATE
  -- hash each edge into K sparse indicator bits in {0,1}^N; membership = all K bits set in the accumulated Bloom
  vector. Algebraically distinct from bundling (no SNR wall; only Bloom false-positive rate). CPU numpy, $0. remote_cpu_queue.

MODEL: V nodes. Edge (u,v): K hash functions h_i(u,v) -> K bit positions; OR them into Bloom vector B in {0,1}^N.
  Membership(a,b): all K hashed bits set in B -> "present" (Bloom: zero false-negatives; FP grows with E).
  balanced accuracy over E true edges + E non-edges. Sweep E.

CELLS (3 seeds): balanced acc at E in {0.5,1,2,4}*N; V=128; K_hash=ceil((N/E)ln2) per E (optimal).
PRE-REGISTERED bands (E_max = max E with balanced acc>=0.95): HARD-PASS E_max>=N (Bloom holds >=N edges; rescues
  SQ6's <0.25N membership wall). MIDDLE: E_max in [0.25N, N). HARD-FAIL: E_max<0.25N (no improvement over SQ6 bundle).

FORMULA SELF-TESTS (PROT-022): 1. Bloom zero false-negatives (every inserted edge passes). 2. distinct edges hash differently. 3. N=2048.
ASCII-only. write_metrics. PROT-018 _n2048 -> N=2048.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sq6_escape_bloom_membership_v1_n2048"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

V_NODES = 256
E_FRACS = [0.5, 1.0, 2.0, 4.0]
_P = [2654435761, 40503, 2246822519, 3266489917, 668265263, 374761393]
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def hashes(u, v, k, n):
    a, b = (u, v) if u < v else (v, u)
    return [((a + 1) * _P[i % len(_P)] ^ ((b + 1) * _P[(i + 3) % len(_P)])) % n for i in range(k)]


def _edge_set(V, E, g):
    E = min(E, V * (V - 1) // 2)   # cap at max distinct edges (no infinite loop)
    seen = set()
    while len(seen) < E:
        u, v = int(g.integers(0, V)), int(g.integers(0, V))
        if u != v:
            seen.add((min(u, v), max(u, v)))
    return list(seen), seen


def acc_at_E(n, E, g):
    k = max(2, int(round((n / max(E, 1)) * math.log(2))))
    edges, seen = _edge_set(V_NODES, E, g)
    B = np.zeros(n, dtype=np.uint8)
    for (u, v) in edges:
        for h in hashes(u, v, k, n):
            B[h] = 1
    pos = np.mean([1.0 if all(B[h] for h in hashes(u, v, k, n)) else 0.0 for (u, v) in edges])
    neg = []
    while len(neg) < E:
        u, v = int(g.integers(0, V_NODES)), int(g.integers(0, V_NODES))
        if u == v or (min(u, v), max(u, v)) in seen:
            continue
        neg.append(0.0 if all(B[h] for h in hashes(u, v, k, n)) else 1.0)
    return float(0.5 * (pos + np.mean(neg))), k


def _selftest():
    g = np.random.default_rng(0); n = 512; k = 4; edges, seen = _edge_set(20, 10, g)
    B = np.zeros(n, dtype=np.uint8)
    for (u, v) in edges:
        for h in hashes(u, v, k, n):
            B[h] = 1
    assert all(all(B[h] for h in hashes(u, v, k, n)) for (u, v) in edges), "Bloom false-negative!"
    assert hashes(0, 1, 4, n) != hashes(2, 3, 4, n), "distinct edges hash same"
    assert N == 2048
    print("[selftest] PASS: bloom_no_false_negatives distinct_hashes", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    out = {"seed": seed, "N": N_DIM}
    for ef in E_FRACS:
        E = max(2, int(round(ef * N_DIM)))
        a, k = acc_at_E(N_DIM, E, np.random.default_rng(seed * 100 + int(ef * 10)))
        out["E%.1f_acc" % ef] = a; out["E%.1f_k" % ef] = k
    return out


def verdict(ps) -> Tuple[str, str]:
    acc = {ef: float(np.mean([p["E%.1f_acc" % ef] for p in ps])) for ef in E_FRACS}
    emax = max([ef for ef in E_FRACS if acc[ef] >= 0.95], default=0.0)
    summary = "acc " + " ".join("E%.1fN:%.2f" % (ef, acc[ef]) for ef in E_FRACS) + " | E_max=%.1fN (SQ6 bundle was <0.25N)" % emax
    if emax >= 1.0:
        return ("HARD_PASS", "HARD_PASS: Bloom-substrate holds >=%.0fN edges (rescues SQ6 membership). %s" % (emax, summary))
    if emax >= 0.25:
        return ("MIDDLE_BAND", "MIDDLE_BAND: Bloom E_max=%.1fN (> SQ6 bundle). %s" % (emax, summary))
    return ("HARD_FAIL", "HARD_FAIL: Bloom no better than bundle. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_NODES), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] " % seed + " ".join("E%.1fN:%.2f" % (ef, r["E%.1f_acc" % ef]) for ef in E_FRACS), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
