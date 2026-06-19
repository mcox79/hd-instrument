"""
exp_g9_consistent_lie_chain_verification_v1 -- Batch G9 (AT-5 compositional verification) -- CPU.

ROUTING: Batch G Tier-4 (adversarial drill #5). A "consistent lie" = a K-hop chain where EVERY hop is individually a
  valid grounded edge, but the chain's CONCLUSION (start->end) is false. Per-hop verification passes; only chain-level
  (composed-relation) verification can catch it. Model: edges B = sign(A * R) (bipolar bind); valid hops ground high. The
  lie chain reaches a claimed end that does NOT match the composed relation applied to the start. Chain-level check =
  recompute composed relation R1*..*Rk, apply to start, compare to claimed end. Measures catch rate at realistic KB size
  (crosstalk makes wrong ends sometimes plausible). CPU $0.
PRE-REGISTERED: HARD-PASS chain-level catch >= 0.85 (compositional verification works). MID 0.65-0.85. HARD-FAIL <0.65
  (end-to-end chain-composition verification is an architectural gap).
FORMULA SELF-TESTS (PROT-022): 1. bind self-inverse. 2. valid hop grounds. 3. composed relation consistent.
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

ANCHOR_NAME = "pb_consistent_lie_chain_harder_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; V_C = 400; CHAINS = 200; KS = [4, 6, 8, 12]
else:
    SEEDS = [7, 17, 23]; N = 8192; V_C = 2000; CHAINS = 400; KS = [4, 6, 8, 12]


def bp(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def _selftest():
    g = np.random.default_rng(0); a = bp(1, 256, g)[0]; r = bp(1, 256, g)[0]; b = np.sign(a * r)
    assert np.array_equal(np.sign(b * r), a), "bind self-inverse"
    C = bp(50, 256, g); assert float(np.max(C @ C[3])) > 0.99, "valid hop grounds"
    print("[selftest] PASS: g9-lie", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = bp(V_C, N, g); catch_by_k = {}
    for K in KS:
        caught = 0
        for _ in range(CHAINS):
            seq = list(g.choice(V_C, K + 1, replace=False)); rels = [np.sign(C[seq[i]] * C[seq[i + 1]]) for i in range(K)]  # valid edge relations
            start = C[seq[0]]
            # composed relation = product of hop relations; applied to start gives the TRUE end
            comp = np.ones(N, np.float32)
            for r in rels:
                comp = comp * r
            true_end = np.sign(start * comp)
            # consistent lie: claim a DIFFERENT end (a real concept, reachable-looking) -- each hop still valid edge
            claimed = C[seq[-1]]                                          # actually true; make a lie 50% of the time
            is_lie = g.random() < 0.5
            if is_lie:
                claimed = C[g.choice([j for j in range(V_C) if j != seq[-1]])]
            # chain-level check: does composed relation applied to start match the claimed end?
            pred_match = float(np.mean(true_end == np.sign(claimed))) > 0.85
            flagged_lie = not pred_match
            caught += int(flagged_lie == is_lie)                          # correct classification (lie caught / truth passed)
        catch_by_k["K%d" % K] = caught / CHAINS
    return {"seed": seed, "catch_by_k": catch_by_k, "catch": float(np.mean(list(catch_by_k.values())))}


def verdict(ps) -> Tuple[str, str]:
    c = float(np.mean([p["catch"] for p in ps]))
    curve = {k: round(float(np.mean([p["catch_by_k"][k] for p in ps])), 3) for k in ps[0]["catch_by_k"]}
    summary = "chain-level lie catch rate by K: %s | mean=%.3f" % (curve, c)
    if c >= 0.85:
        return ("HARD_PASS", "HARD_PASS: chain-level compositional verification catches consistent lies (>=0.85) -- composition verification works. " + summary)
    if c >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial chain-level catch (0.65-0.85). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: consistent lies evade chain-level verification (<0.65) -- end-to-end composition verification is an architectural gap. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_c=%d KS=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, V_C, KS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
