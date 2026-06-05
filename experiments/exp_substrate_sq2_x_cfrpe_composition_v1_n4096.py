"""
substrate_sq2_x_cfrpe_composition_v1_n4096 -- P1: multi-hop reasoning x cf-RPE task-gating -- remote CPU.

ROUTING: research_to_exp_dev_priority_1_compositions_routing (Cell P1). Does cf-RPE (task-supervised rank-1
  substitution write) PRESERVE SQ2's 12-hop iterated-retrieval reasoning, or does its filtering break the chain?
  CPU numpy, $0. remote_cpu_queue. Reuses SQ2 chains + Bundle A cf-RPE.

MODEL: G chains s_g0->...->s_gL (random bipolar, N=4096). Store transitions two ways:
  hebbian: W += outer(s_{t+1}, s_t).   cfrpe (delta rule): W += outer(s_{t+1} - W@s_t, s_t).
  Retrieve: from s_g0 iterate q=sign(W q) K times; hop-K correct iff overlap(q, s_gK)>0.9. depth=max K acc>=0.8.

CELLS (3 seeds): hop depth for {hebbian, cfrpe}; L=12; load 0.5*alpha_c (SQ2 baseline regime).
PRE-REGISTERED bands: HARD-PASS cfrpe depth >= 12 (preserves reasoning) AND cfrpe depth >= hebbian depth.
  MIDDLE: cfrpe depth in [8,12). HARD-FAIL: cfrpe depth < 8 (cf-RPE filtering breaks iterated retrieval).

FORMULA SELF-TESTS (PROT-022): 1. hebbian 1-hop+2-hop recall. 2. cf-RPE shrinks transition error. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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

ANCHOR_NAME = "substrate_sq2_x_cfrpe_composition_v1_n4096"
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
L = 12
K_GRID = [1, 2, 4, 8, 12]
LOAD_FRAC = 0.5
LR = 0.5
ARMS = ["hebbian", "cfrpe"]
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def build(n, arm, g):
    n_trans = max(L, int(round(LOAD_FRAC * ALPHA_C * n)))
    G = max(1, n_trans // L)
    chains = [bipolar((L + 1, n), g) for _ in range(G)]
    W = np.zeros((n, n), dtype=np.float32)
    for ch in chains:
        for i in range(L):
            cur, nxt = ch[i], ch[i + 1]
            if arm == "hebbian":
                W += np.outer(nxt, cur)
            else:
                W += (LR / n) * np.outer(nxt - W @ cur, cur)   # cf-RPE delta rule (normalized by ||cur||^2=n)
    return W, chains, G


def hop_acc(W, chains, n, K):
    hits = 0
    for ch in chains:
        q = ch[0].copy()
        for _ in range(K):
            q = np.sign(W @ q); q[q == 0] = 1.0
        hits += (float((q * ch[K]).sum() / n) > 0.90)
    return hits / len(chains)


def _selftest():
    g = np.random.default_rng(0); n = 256; ch = bipolar((5, n), g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(4):
        W += np.outer(ch[i + 1], ch[i])
    q = np.sign(W @ ch[0]); assert float((q * ch[1]).sum() / n) > 0.9, "1-hop"
    assert float((np.sign(W @ q) * ch[2]).sum() / n) > 0.9, "2-hop"
    W2 = np.zeros((n, n), dtype=np.float32); v = W2 @ ch[0]; eb = float(np.linalg.norm(ch[1] - v))
    W2 += (LR / n) * np.outer(ch[1] - v, ch[0]); assert float(np.linalg.norm(ch[1] - W2 @ ch[0])) < eb, "cf-RPE shrinks"
    assert N == 4096
    print("[selftest] PASS: hebbian_hops cfrpe_shrinks", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    out = {"seed": seed, "N": N_DIM}
    for arm in ARMS:
        g = np.random.default_rng(seed * 10 + (0 if arm == "hebbian" else 1)); W, chains, G = build(N_DIM, arm, g)
        accs = {k: float(hop_acc(W, chains, N_DIM, k)) for k in K_GRID}
        out[arm + "_depth"] = max([k for k in K_GRID if accs[k] >= 0.80], default=0)
        out[arm + "_acc12"] = accs[12]
        out["G_chains"] = G
    return out


def verdict(ps) -> Tuple[str, str]:
    hd = float(np.mean([p["hebbian_depth"] for p in ps])); cd = float(np.mean([p["cfrpe_depth"] for p in ps]))
    ca12 = float(np.mean([p["cfrpe_acc12"] for p in ps]))
    summary = "hebbian_depth=%.1f cfrpe_depth=%.1f cfrpe_acc@12=%.2f" % (hd, cd, ca12)
    if cd >= 12 and cd >= hd:
        return ("HARD_PASS", "HARD_PASS: cf-RPE PRESERVES 12-hop reasoning (>=hebbian). " + summary)
    if cd >= 8:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cf-RPE depth 8-12 (slight degradation). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: cf-RPE breaks iterated retrieval (depth<8). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d L=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, L), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] hebbian_depth=%d cfrpe_depth=%d cfrpe_acc12=%.2f" % (seed, r["hebbian_depth"], r["cfrpe_depth"], r["cfrpe_acc12"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
