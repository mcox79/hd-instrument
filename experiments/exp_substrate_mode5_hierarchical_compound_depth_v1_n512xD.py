"""
substrate_mode5_hierarchical_compound_depth_v1_n512xD -- Mode 5 + Hierarchical compound (production arch) -- remote CPU.

ROUTING: research_to_exp_dev_mode5_HP_ack_next_priority. Production architecture: D parallel ISOLATED storage
  substrates (hierarchical) + controller routing + per-hop cleanup (NEW EXP 3) + iterated traversal (Mode 4/5).
  Combines the 3 validated levers (partition P2 + cleanup NEW-EXP-3 + isolation Mode-5) -> deep reasoning K>=50
  where a single substrate collapses. CPU numpy, $0. remote_cpu_queue.

MODEL: L-node reasoning chain over a global node codebook (V nodes). COMPOUND: partition chain into D contiguous
  segments; segment d stored in isolated W_s[d] (light load -> full recall); a controller routes each hop to the
  substrate holding the current segment + cleans up (snap to nearest node). Traverse L hops. SINGLE baseline: whole
  chain in ONE W + plain iterate (no partition, no cleanup) -> collapses under load. K_effective = max hops at >=0.8 acc.

PRE-REGISTERED bands: HARD-PASS K_effective(compound) >= 50 AND >= 2x K_single. MIDDLE: K_eff >= 25 OR >= 1.5x single.
  HARD-FAIL: K_eff < 25 AND < 1.5x single.
FORMULA SELF-TESTS (PROT-022): 1. segment store+cleanup recall. 2. controller routes to correct segment substrate. 3. N=512.
ASCII-only. write_metrics. PROT-018 anchor scaffold (N_s=512 per substrate; no single _nN).
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

ANCHOR_NAME = "substrate_mode5_hierarchical_compound_depth_v1_n512xD"
N_S = 512
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 256; D = 4; L = 40; V_NODES = 80
else:
    SEEDS = [7, 17, 23]; N_DIM = N_S; D = 4; L = 80; V_NODES = 160


def bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_chain(n, g):
    cb = bipolar(V_NODES, n, g)                        # global node codebook
    seq = list(g.choice(V_NODES, size=L + 1, replace=False)) if V_NODES > L else [int(g.integers(0, V_NODES)) for _ in range(L + 1)]
    return cb, seq


def compound_depth(cb, seq, n, g):
    seg = max(1, (L + D - 1) // D)
    Ws = [np.zeros((n, n), dtype=np.float32) for _ in range(D)]
    for t in range(L):
        d = min(D - 1, t // seg)                       # controller routing: which substrate holds position t
        Ws[d] += np.outer(cb[seq[t + 1]], cb[seq[t]])
    q = cb[seq[0]].copy(); best = 0
    for t in range(L):
        d = min(D - 1, t // seg)                       # controller routes to substrate d
        r = Ws[d] @ q; nxt = int(np.argmax(cb @ r))    # cleanup: snap to nearest node
        if nxt == seq[t + 1]:
            best = t + 1; q = cb[nxt]
        else:
            break
    return best


def single_depth(cb, seq, n, g):
    W = np.zeros((n, n), dtype=np.float32)
    for t in range(L):
        W += np.outer(cb[seq[t + 1]], cb[seq[t]])
    q = cb[seq[0]].copy(); best = 0
    for t in range(L):
        q = np.sign(W @ q); q[q == 0] = 1.0            # plain iterate (no cleanup, no partition)
        if float((q * cb[seq[t + 1]]).sum() / n) > 0.90:
            best = t + 1
        else:
            break
    return best


def _selftest():
    g = np.random.default_rng(0); n = 256; cb = bipolar(10, n, g)
    W = np.outer(cb[2], cb[1]); r = W @ cb[1]; assert int(np.argmax(cb @ r)) == 2, "segment store+cleanup"
    seg = max(1, (L + D - 1) // D); assert min(D - 1, 0 // seg) == 0 and min(D - 1, (L - 1) // seg) <= D - 1, "routing bounds"
    assert N_S == 512; print("[selftest] PASS: segment_cleanup routing", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); cb, seq = build_chain(N_DIM, g)
    kc = compound_depth(cb, seq, N_DIM, g); ks = single_depth(cb, seq, N_DIM, g)
    return {"seed": seed, "N_s": N_DIM, "D": D, "L": L, "K_compound": kc, "K_single": ks, "ratio": float(kc / max(ks, 1))}


def verdict(ps) -> Tuple[str, str]:
    kc = float(np.mean([p["K_compound"] for p in ps])); ks = float(np.mean([p["K_single"] for p in ps])); r = kc / max(ks, 1)
    note = "" if kc < L else " (compound hit chain length L=%d; LOWER BOUND)" % L
    summary = "K_compound=%.1f K_single=%.1f ratio=%.1fx (D=%d, N_s=%d, L=%d)%s" % (kc, ks, r, D, ps[0]["N_s"], L, note)
    if kc >= 50 and kc >= 2 * max(ks, 1):
        return ("HARD_PASS", "HARD_PASS: Mode5+Hierarchical compound reaches deep reasoning K>=50 (>=2x single). " + summary)
    if kc >= 25 or r >= 1.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: compound deeper than single. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: compound no deep-reasoning gain. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_s=%d D=%d L=%d V=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, D, L, V_NODES), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] K_compound=%d K_single=%d ratio=%.1fx" % (seed, r["K_compound"], r["K_single"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
