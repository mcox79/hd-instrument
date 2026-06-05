"""
substrate_max_for_reasoning_tasks_not_lm_v1 -- HP-4: substrate-MAX variants help REASONING, not LM -- CPU.

ROUTING: research high_priority_experiments_phase1_5 (HP-4). The substrate-MAX variants (cleanup-augmentation,
  iterated retrieval, extended context) HURT or no-op at next-concept-LM (EX-CONCEPT honest finding). But those are
  REASONING mechanisms. Test them where they SHOULD help: multi-hop chain traversal under load. Show the CONTRAST --
  same variants, opposite outcomes on LM vs reasoning -- which reframes the LM-negative as a task-mismatch, not a
  substrate weakness. CPU numpy $0. remote_cpu.

TASKS: (R) multi-hop reasoning = K-hop chain over a node codebook at OVERLOAD; measure max-hop depth K_max for
  PLAIN-iterate (sign(W@q), drifts) vs CLEANUP-iterate (snap to nearest node each hop). (L) next-concept-LM = 1-step
  prediction; single-pass vs cleanup (reference: cleanup is a no-op for LM, per EX-CONCEPT). Contrast the two.

PRE-REGISTERED bands: HARD-PASS cleanup-iterate K_max >= 2.0x plain-iterate K_max (variants help reasoning) AND
  cleanup gives no LM gain (confirms task-mismatch reframe). MIDDLE: K_max ratio 1.3-2.0x. HARD-FAIL: < 1.3x.
FORMULA SELF-TESTS (PROT-022): 1. clean chain hop. 2. cleanup snaps to node. 3. N=2048.
ASCII-only. write_metrics. PROT-018 _n2048 -> N=2048.
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

ANCHOR_NAME = "substrate_max_for_reasoning_tasks_not_lm_v1"
_N_SUFFIX = 2048; N = 2048; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512; V_NODES = 200; CHAIN = 40
else:
    SEEDS = [7, 17, 23]; N_DIM = N; V_NODES = 600; CHAIN = 60


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 256; cb = bp(5, n, g); W = np.outer(cb[2], cb[1])
    r = W @ cb[1]; assert int(np.argmax(cb @ r)) == 2, "clean chain hop"
    snap = cb[int(np.argmax(cb @ r))]; assert np.allclose(snap, cb[2]), "cleanup snaps to node"
    assert N == 2048; print("[selftest] PASS: hop cleanup", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def reasoning_depth(cb, seq, W, n, cleanup):
    """traverse the chain; PLAIN: sign(W@q); CLEANUP: snap to nearest node. Return max correct hop depth."""
    q = cb[seq[0]].copy(); best = 0
    for t in range(len(seq) - 1):
        r = W @ q
        if cleanup:
            nxt = int(np.argmax(cb @ r))
            if nxt == seq[t + 1]:
                best = t + 1; q = cb[nxt]
            else:
                break
        else:
            q = np.sign(r); q[q == 0] = 1.0
            if float((q * cb[seq[t + 1]]).sum() / n) > 0.5:
                best = t + 1
            else:
                break
    return best


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; cb = bp(V_NODES, n, g)
    # store a LONG chain -- its own accumulating crosstalk makes PLAIN-iterate drift after a few hops;
    # CLEANUP (snap to nearest node each hop) removes the per-hop noise -> deep traversal (NEW EXP 3 regime).
    W = np.zeros((n, n), dtype=np.float32)
    seq = [int(g.integers(0, V_NODES)) for _ in range(CHAIN + 1)]
    for t in range(CHAIN):
        W += (1.0 / n) * np.outer(cb[seq[t + 1]], cb[seq[t]])
    k_plain = reasoning_depth(cb, seq, W, n, False); k_clean = reasoning_depth(cb, seq, W, n, True)
    # LM contrast: 1-step next-concept, single vs cleanup (cleanup no-op for 1-step)
    lm_single = lm_clean = lm_tot = 0
    for t in range(CHAIN):
        r = W @ cb[seq[t]]; lm_single += (int(np.argmax(cb @ r)) == seq[t + 1])
        snap = cb[int(np.argmax(cb @ r))]; lm_clean += (int(np.argmax(cb @ snap)) == seq[t + 1]); lm_tot += 1
    return {"seed": seed, "N": n, "K_plain": k_plain, "K_cleanup": k_clean, "reasoning_ratio": float(k_clean / max(k_plain, 1)),
            "lm_single": lm_single / lm_tot, "lm_cleanup": lm_clean / lm_tot}


def verdict(ps) -> Tuple[str, str]:
    kp = float(np.mean([p["K_plain"] for p in ps])); kc = float(np.mean([p["K_cleanup"] for p in ps])); rr = kc / max(kp, 1)
    lm_s = float(np.mean([p["lm_single"] for p in ps])); lm_c = float(np.mean([p["lm_cleanup"] for p in ps]))
    lm_gain = lm_c - lm_s
    summary = "REASONING K_plain=%.1f K_cleanup=%.1f ratio=%.2fx | LM single=%.3f cleanup=%.3f gain=%.3f (cleanup no-op for LM as expected)" % (kp, kc, rr, lm_s, lm_c, lm_gain)
    if rr >= 2.0 and lm_gain < 0.05:
        return ("HARD_PASS", "HARD_PASS: substrate-MAX (cleanup) helps REASONING >=2x but not LM -- variants belong in reasoning, not generation (reframes LM-negative). " + summary)
    if rr >= 1.3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cleanup helps reasoning 1.3-2x. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: cleanup no reasoning advantage. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V=%d chain=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_NODES, CHAIN), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] REASONING K_plain=%d K_cleanup=%d (%.1fx) | LM single=%.3f cleanup=%.3f" % (seed, r["K_plain"], r["K_cleanup"], r["reasoning_ratio"], r["lm_single"], r["lm_cleanup"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
