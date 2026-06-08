"""
exp_iterative_regime_crossover_cpu_v1 -- empirical proof of the iterative-multihop UNIVERSAL PRINCIPLE -- CPU.

ROUTING: iterative_pattern_universal_principle_strategic. The 5x deep-dive (32 citations) established: iterative multi-hop
  works IFF each step is grounded in DISCRETE symbols; it loses in the fuzzy-embedding regime (the 5 HFs were the fuzzy regime,
  not substrate failures). This cell demonstrates that crossover directly on the substrate: the SAME 2-hop K-hop task, run with
  entities whose inter-similarity (fuzziness) rho is dialed from 0 (discrete/orthogonal symbols) to high (fuzzy/overlapping
  like text embeddings). Measures recall@2 (bridge + answer) vs rho. Confirms discrete-regime success and fuzzy-regime failure
  within ONE controlled experiment. Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS discrete regime (rho=0) recall@2 >= 0.80 AND fuzzy regime (rho=0.9) recall@2 <= 0.50 (the crossover
  is real -- substrate iterative multi-hop works on discrete symbols, fails on fuzzy). MIDDLE crossover present but weaker
  (discrete >= 0.65 and fuzzy <= 0.65). HARD-FAIL no crossover.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind inverse. 2. cleanup self. 3. correlation increases similarity.
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

ANCHOR_NAME = "iterative_regime_crossover_cpu_v1"; N = 2048
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
TRIALS = 30 if SMOKE else 120; CHAINS = 15


def corr_phasors(m, d, rho, g):
    # entities with controllable inter-similarity: shared phase component weight rho, individual weight sqrt(1-rho^2)
    common = (g.random((1, d)) * 2 - 1) * math.pi
    indiv = (g.random((m, d)) * 2 - 1) * math.pi
    phase = math.sqrt(1 - rho * rho) * indiv + rho * common
    return np.exp(1j * phase).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); a = corr_phasors(1, 32, 0.0, g)[0]; b = corr_phasors(1, 32, 0.0, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind/unbind inverse"
    bk = corr_phasors(5, 32, 0.0, g); assert cidx(bk[2], bk) == 2, "cleanup self"
    lo = corr_phasors(40, 64, 0.0, g); hi = corr_phasors(40, 64, 0.9, g)
    sim_lo = np.abs(lo @ np.conj(lo[0]))[1:].mean(); sim_hi = np.abs(hi @ np.conj(hi[0]))[1:].mean()
    assert sim_hi > sim_lo, "correlation increases similarity"
    print("[selftest] PASS: iterative-regime-crossover", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def khop_recall(rho, g):
    succ_both = 0
    for _ in range(TRIALS):
        E = corr_phasors(50, N, rho, g); R = corr_phasors(8, N, 0.0, g)   # relations stay distinct; entities carry the fuzziness
        M = np.zeros(N, dtype=np.complex64); chains = []
        for _c in range(CHAINS):
            trip = g.choice(50, 3, replace=False); e1, b, a = int(trip[0]), int(trip[1]), int(trip[2])
            r1, r2 = int(g.integers(0, 8)), int(g.integers(0, 8))
            M = M + E[e1] * R[r1] * E[b] + E[b] * R[r2] * E[a]; chains.append((e1, r1, b, r2, a))
        e1, r1, b, r2, a = chains[int(g.integers(0, CHAINS))]
        bh = cidx(M * np.conj(E[e1] * R[r1]), E)                          # hop1: bridge
        ah = cidx(M * np.conj(E[bh] * R[r2]), E)                          # hop2: answer (grounded on recovered bridge)
        succ_both += int(bh == b and ah == a)
    return succ_both / TRIALS


def run() -> Dict:
    g = np.random.default_rng(7); rhos = [0.0, 0.5, 0.9] if SMOKE else [0.0, 0.3, 0.6, 0.9]; by = {}
    for rho in rhos:
        by["rho%.1f" % rho] = khop_recall(rho, g); print("  rho=%.1f (fuzziness) recall@2=%.3f" % (rho, by["rho%.1f" % rho]), flush=True)
    return {"by": by, "discrete": by["rho0.0"], "fuzzy": by["rho0.9"]}


def verdict(r) -> Tuple[str, str]:
    d = r["discrete"]; f = r["fuzzy"]; s = "discrete(rho=0)=%.3f fuzzy(rho=0.9)=%.3f | curve=%s" % (d, f, {k: round(v, 3) for k, v in r["by"].items()})
    if d >= 0.80 and f <= 0.50:
        return ("HARD_PASS", "HARD_PASS: substrate iterative multi-hop succeeds on DISCRETE symbols (>=0.80) and fails on FUZZY entities (<=0.50) -- the 32-citation universal principle reproduced on the substrate; the 5 iterative HFs were the fuzzy regime, not substrate limits. " + s)
    if d >= 0.65 and f <= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: crossover present but weaker. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no clear discrete-vs-fuzzy crossover. " + s)


print("[config] anchor=%s mode=%s N=%d trials=%d chains=%d" % (ANCHOR_NAME, RUN_MODE, N, TRIALS, CHAINS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
