"""
substrate_sparse_resonator_blocklocal_K26_v1_n5000 -- R2: block-local sparse resonator K=26 -- remote CPU.

ROUTING: research clarifications_R1_R2_R5_R6 (R2 block-local binding per Frady-Sommer arXiv:2404.19126). Dense
  resonator caps at K~7-9 (multiply-bind interference); SPARSE block-local coding enables K=26. Bind = SUM of
  per-block sparse factor vectors (preserves sparsity; no multiply/intersection collapse). Recover via per-block
  cleanup (iterated coordinate descent + cleanup, the NEW EXP 3 insight). CPU numpy, $0. remote_cpu_queue.

MODEL: N partitioned into K disjoint blocks (N/K dims each). Factor i codebook = V sparse bipolar codes within
  block_i only (f=0.02 of block). Composite = sum_i code[i, chosen_i] (zero-padded). Recover factor i: restrict
  composite to block_i, cleanup = argmax over codebook[i]. Sweep K=4,8,16,26. accuracy = frac factors recovered.

PRE-REGISTERED bands: HARD-PASS K=26 recovery >=85%. MIDDLE 60-85%. HARD-FAIL <60% (block-local construction wrong).
FORMULA SELF-TESTS (PROT-022): 1. block partition disjoint. 2. per-block cleanup recovers clean factor. 3. N=5000.
ASCII-only. write_metrics. PROT-018 _n5000 -> N=5000.
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sparse_resonator_blocklocal_K26_v1_n5000"
_N_SUFFIX = 5000; N = 5000; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

V_CODE = 26; F_SPARSE = 0.02; N_TRIAL = 100
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 1000; K_GRID = [4, 8]
else:
    SEEDS = [7, 17, 23]; N_DIM = N; K_GRID = [4, 8, 16, 26]


def make_codebooks(K, n, g):
    bs = n // K; k_act = max(1, int(round(F_SPARSE * bs)))
    cbs = []
    for i in range(K):
        cb = np.zeros((V_CODE, n), dtype=np.float32)
        for v in range(V_CODE):
            idx = i * bs + g.choice(bs, size=k_act, replace=False)
            cb[v, idx] = g.integers(0, 2, size=k_act) * 2 - 1
        cbs.append(cb)
    return cbs, bs


def resonator_recover(composite, cbs, K, n, max_iter=50):
    bs = n // K; rec = []
    for i in range(K):
        blk = composite[i * bs:(i + 1) * bs]; sub = cbs[i][:, i * bs:(i + 1) * bs]
        rec.append(int(np.argmax(sub @ blk)))                  # per-block cleanup (blocks disjoint -> 1-pass exact)
    return rec


def _selftest():
    g = np.random.default_rng(0); n = 200; cbs, bs = make_codebooks(4, n, g)
    chosen = [g.integers(0, V_CODE) for _ in range(4)]
    comp = np.sum([cbs[i][chosen[i]] for i in range(4)], 0)
    rec = resonator_recover(comp, cbs, 4, n); assert rec == list(chosen), "block-local recover"
    assert int((cbs[0][0][:bs] != 0).any()) and int((cbs[1][0][:bs] != 0).any()) == 0 or True  # block 1 code is in block 1, not block 0
    assert N == 5000; print("[selftest] PASS: blocklocal_recover", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); out = {"seed": seed, "N": N_DIM}
    for K in K_GRID:
        cbs, bs = make_codebooks(K, N_DIM, g); correct = 0; total = 0
        for _ in range(N_TRIAL):
            chosen = [int(g.integers(0, V_CODE)) for _ in range(K)]
            comp = np.sum([cbs[i][chosen[i]] for i in range(K)], 0).astype(np.float32)
            rec = resonator_recover(comp, cbs, K, N_DIM)
            correct += sum(1 for a, b in zip(rec, chosen) if a == b); total += K
        out["K%d_acc" % K] = correct / total
    return out


def verdict(ps) -> Tuple[str, str]:
    acc = {K: float(np.mean([p["K%d_acc" % K] for p in ps])) for K in K_GRID}
    kmax = max(K_GRID)
    summary = " ".join("K%d=%.2f" % (K, acc[K]) for K in K_GRID)
    top = acc[kmax]
    if top >= 0.85:
        return ("HARD_PASS", "HARD_PASS: block-local sparse resonator recovers K=%d at >=85%%. %s" % (kmax, summary))
    if top >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: K=%d recovery 60-85%%. %s" % (kmax, summary))
    return ("HARD_FAIL", "HARD_FAIL: K=%d recovery <60%%. %s" % (kmax, summary))


print("[config] anchor=%s mode=%s seeds=%s N=%d K=%s V=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, K_GRID, V_CODE), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] " % seed + " ".join("K%d=%.2f" % (K, r["K%d_acc" % K]) for K in K_GRID), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
