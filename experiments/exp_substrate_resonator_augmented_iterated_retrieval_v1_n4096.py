"""
substrate_resonator_augmented_iterated_retrieval_v1_n4096 -- NEW EXP 3: cleanup-augmented reasoning depth -- remote CPU.

ROUTING: research_to_exp_dev_3_drill_synthesis_priority_experiments (NEW EXP 3, highest-leverage per drill 3:
  resonator/cleanup augmentation = depth boost). Plain iterated retrieval q=sign(W@q) accumulates per-hop noise ->
  depth ceiling (~12 at 0.5 alpha_c). CLEANUP-AUGMENTED: snap each hop to the nearest stored node (codebook
  cleanup, resonator-style denoise) -> less per-hop noise -> deeper reasoning. CPU numpy, $0. remote_cpu_queue.

MODEL: G chains over a node codebook (all distinct nodes); W += outer(node_{t+1}, node_t). PLAIN: q=sign(W@q).
  CLEANUP: q = codebook[argmax(codebook @ (W@q))] each hop (snap to nearest node). depth = max K with chain-K acc>=0.8.

PRE-REGISTERED bands: HARD-PASS cleanup_depth >= 1.5x plain_depth (resonator augmentation extends depth). MIDDLE 1.1-1.5x. HARD-FAIL <1.1x.
FORMULA SELF-TESTS (PROT-022): 1. chain 2-hop. 2. cleanup snaps noisy vec to nearest node. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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

ANCHOR_NAME = "substrate_resonator_augmented_iterated_retrieval_v1_n4096"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138; LOAD_FRAC = 2.0; K_CAP = 40
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 1024; K_CAP = 24
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def build(n, g):
    n_trans = max(K_CAP, int(round(LOAD_FRAC * ALPHA_C * n))); G = max(1, n_trans // K_CAP)
    chains = [bipolar((K_CAP + 1, n), g) for _ in range(G)]
    cb = np.concatenate(chains, 0)                                  # node codebook (all chain nodes)
    W = np.zeros((n, n), dtype=np.float32)
    for ch in chains:
        for i in range(K_CAP):
            W += np.outer(ch[i + 1], ch[i])
    return W, chains, cb


def depth(W, chains, cb, n, mode):
    best = 0
    for K in range(1, K_CAP + 1):
        hits = 0
        for ch in chains:
            q = ch[0].copy()
            for _ in range(K):
                v = W @ q
                if mode == "cleanup":
                    q = cb[int(np.argmax(cb @ v))]                 # snap to nearest node (resonator cleanup)
                else:
                    q = np.sign(v); q[q == 0] = 1.0
            hits += (float((q * ch[K]).sum() / n) > 0.90)
        if hits / len(chains) >= 0.80:
            best = K
        else:
            break
    return best


def _selftest():
    g = np.random.default_rng(0); n = 256; ch = bipolar((5, n), g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(4):
        W += np.outer(ch[i + 1], ch[i])
    assert float((np.sign(W @ np.sign(W @ ch[0])) * ch[2]).sum() / n) > 0.9, "2-hop"
    cb = ch; noisy = ch[2] + 0.3 * g.standard_normal(n).astype(np.float32)
    assert int(np.argmax(cb @ noisy)) == 2, "cleanup snaps to nearest node"
    assert N == 4096; print("[selftest] PASS: 2hop cleanup_snap", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); W, chains, cb = build(N_DIM, g)
    dp = depth(W, chains, cb, N_DIM, "plain"); dc = depth(W, chains, cb, N_DIM, "cleanup")
    return {"seed": seed, "N": N_DIM, "G_chains": len(chains), "plain_depth": dp, "cleanup_depth": dc, "ratio": float(dc / max(dp, 1))}


def verdict(ps) -> Tuple[str, str]:
    dp = float(np.mean([p["plain_depth"] for p in ps])); dc = float(np.mean([p["cleanup_depth"] for p in ps])); r = dc / max(dp, 1)
    note = "" if dc < K_CAP else " (cleanup hit K_CAP; ratio LOWER BOUND)"
    summary = "plain_depth=%.1f cleanup_depth=%.1f ratio=%.1fx%s (load=%.1f alpha_c)" % (dp, dc, r, note, LOAD_FRAC)
    if r >= 1.5:
        return ("HARD_PASS", "HARD_PASS: cleanup/resonator augmentation extends reasoning depth >=1.5x. " + summary)
    if r >= 1.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cleanup gives 1.1-1.5x depth. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: cleanup no depth gain. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d load=%.1f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, LOAD_FRAC), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] plain_depth=%d cleanup_depth=%d ratio=%.1fx" % (seed, r["plain_depth"], r["cleanup_depth"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
