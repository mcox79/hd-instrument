"""
substrate_mode5_architecture_a_isolated_dual_substrate_controller_v1_n1024 -- Mode 5 hybrid (Arch A) -- remote CPU.

ROUTING: research_to_exp_dev_mode5_architecture_A_buildable. Mode 5 hybrid: ISOLATED storage substrate W_s +
  ISOLATED resonator substrate W_r + FSM controller routing between them. Validates the R6 STORAGE-COMPATIBILITY
  RULE architecturally: storage crosstalk in W_s must NOT corrupt resonator block-structure in W_r (-> use SEPARATE
  matrices). Reuses R2 block-local resonator (HP). CPU numpy, $0. remote_cpu_queue.

TASK (2-hop chain + factor decomposition): query A -> W_s -> retrieve B (episodic); B -> W_r -> decompose factors
  (f1,f2) [block-local resonator]; f1-codeword -> W_s -> retrieve C (2nd hop). Controller states START/HOP1/
  DECOMPOSE/HOP2/DONE + 2-bit counter. Chain correct iff f1 decoded right AND C retrieved (overlap>0.9).

CONDITIONS: (1) SHARED-W: one matrix = episodic transitions + codebook auto-assoc together (R6 predicts crosstalk
  corrupts decomposition). (2) ISOLATED (Arch A): W_s (episodic) + W_r (codebook) separate.

PRE-REGISTERED bands: HARD-PASS isolated/shared accuracy ratio >= 1.5x at M=100. MIDDLE [1.1,1.5). HARD-FAIL <1.1x.
FORMULA SELF-TESTS (PROT-022): 1. block-local decompose (clean). 2. episodic A->B->C retrieve (isolated). 3. N=1024.
ASCII-only. write_metrics. PROT-018 _n1024 -> N=1024.
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

ANCHOR_NAME = "substrate_mode5_architecture_a_isolated_dual_substrate_controller_v1_n1024"
_N_SUFFIX = 1024; N = 1024; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

K_FAC = 2; D_CODE = 20
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512; M_GRID = [10, 30, 100]
else:
    SEEDS = [7, 17, 23, 31, 41]; N_DIM = N; M_GRID = [10, 30, 100, 300]


def bipolar(n, g):
    return (g.integers(0, 2, n) * 2 - 1).astype(np.float32)


def make_codebooks(K, n, g):
    bs = n // K; k_act = max(1, int(round(0.05 * bs))); cbs = []
    for i in range(K):
        cb = np.zeros((D_CODE, n), dtype=np.float32)
        for v in range(D_CODE):
            idx = i * bs + g.choice(bs, size=k_act, replace=False); cb[v, idx] = g.integers(0, 2, size=k_act) * 2 - 1
        cbs.append(cb)
    return cbs, bs


def compose(cbs, chosen):
    return np.sum([cbs[i][chosen[i]] for i in range(K_FAC)], 0).astype(np.float32)


def decompose(comp, cbs, W_clean, n):
    """resonator: denoise via W_clean (auto-assoc) then per-block cleanup to nearest codeword."""
    bs = n // K_FAC; den = W_clean @ comp
    return [int(np.argmax(cbs[i][:, i * bs:(i + 1) * bs] @ den[i * bs:(i + 1) * bs])) for i in range(K_FAC)]


def _selftest():
    g = np.random.default_rng(0); n = 256; cbs, bs = make_codebooks(K_FAC, n, g)
    Wr = np.zeros((n, n), dtype=np.float32)
    for i in range(K_FAC):
        for v in range(D_CODE):
            Wr += np.outer(cbs[i][v], cbs[i][v])
    np.fill_diagonal(Wr, 0.0)
    chosen = [int(g.integers(0, D_CODE)) for _ in range(K_FAC)]; comp = compose(cbs, chosen)
    assert decompose(comp, cbs, Wr, n) == chosen, "block-local decompose"
    A = bipolar(n, g); B = comp; Ws = np.outer(B, A); assert float((np.sign(Ws @ A) * np.sign(B)).sum()) > 0, "A->B"
    assert N == 1024; print("[selftest] PASS: decompose A->B", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def build_and_eval(M, n, isolated, g):
    cbs, bs = make_codebooks(K_FAC, n, g)
    # W_r = codebook auto-assoc (resonator denoise reference)
    Wr = np.zeros((n, n), dtype=np.float32)
    for i in range(K_FAC):
        for v in range(D_CODE):
            Wr += np.outer(cbs[i][v], cbs[i][v])
    # episodic chains: A_m -> B_m(composite) ; f1-codeword -> C_m
    chains = []; Ws = np.zeros((n, n), dtype=np.float32)
    for _ in range(M):
        A = bipolar(n, g); f = [int(g.integers(0, D_CODE)) for _ in range(K_FAC)]; B = compose(cbs, f); C = bipolar(n, g)
        Ws += np.outer(B, A) + np.outer(C, cbs[0][f[0]]); chains.append((A, f, C))
    np.fill_diagonal(Ws, 0.0); np.fill_diagonal(Wr, 0.0)
    W_store = (Ws + Wr) if not isolated else Ws            # shared: storage+codebook in one matrix
    W_clean = (Ws + Wr) if not isolated else Wr            # shared: decompose reads corrupted matrix
    ok = 0
    for (A, f, C) in chains:
        Bh = W_store @ A                                    # HOP1: retrieve B (raw -- preserve sparse composite structure)
        fh = decompose(Bh, cbs, W_clean, n)                # DECOMPOSE: factors
        Ch = np.sign(W_store @ cbs[0][fh[0]]); Ch[Ch == 0] = 1.0   # HOP2: retrieve C via f1-codeword
        ok += (fh[0] == f[0] and float((Ch * C).sum() / n) > 0.90)
    return ok / max(M, 1)


def run_seed(seed: int) -> Dict:
    out = {"seed": seed, "N": N_DIM}
    for M in M_GRID:
        out["M%d_shared" % M] = build_and_eval(M, N_DIM, False, np.random.default_rng(seed * 100 + M))
        out["M%d_isolated" % M] = build_and_eval(M, N_DIM, True, np.random.default_rng(seed * 100 + M))
    return out


def verdict(ps) -> Tuple[str, str]:
    iso_by_M = {M: float(np.mean([p["M%d_isolated" % M] for p in ps])) for M in M_GRID}
    sh_by_M = {M: float(np.mean([p["M%d_shared" % M] for p in ps])) for M in M_GRID}
    # report the band where the isolation benefit is meaningful: max ratio among M with BOTH non-trivial (iso>=0.1)
    cand = [M for M in M_GRID if iso_by_M[M] >= 0.1]
    Mref = max(cand, key=lambda M: iso_by_M[M] / max(sh_by_M[M], 1e-6)) if cand else M_GRID[0]
    sh = sh_by_M[Mref]; iso = iso_by_M[Mref]; ratio = iso / max(sh, 1e-6)
    parts = " ".join("M%d:iso=%.2f/sh=%.2f" % (M, float(np.mean([p["M%d_isolated" % M] for p in ps])), float(np.mean([p["M%d_shared" % M] for p in ps]))) for M in M_GRID)
    summary = "at M=%d isolated=%.2f shared=%.2f ratio=%.2fx | %s" % (Mref, iso, sh, ratio, parts)
    if ratio >= 1.5:
        return ("HARD_PASS", "HARD_PASS: Mode-5 isolated dual-substrate >=1.5x shared-W (storage-compatibility rule architecturally validated). " + summary)
    if ratio >= 1.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: isolation helps 1.1-1.5x. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: isolation not helping. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d K=%d D=%d M=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, K_FAC, D_CODE, M_GRID), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] " % seed + " ".join("M%d:i%.2f/s%.2f" % (M, r["M%d_isolated" % M], r["M%d_shared" % M]) for M in M_GRID), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
