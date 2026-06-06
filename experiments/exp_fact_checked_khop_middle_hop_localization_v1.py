"""
exp_fact_checked_khop_middle_hop_localization_v1 -- Batch D1 Rank 2 (PRODUCTION GATE): localize WHICH hop is fabricated -- CPU.

ROUTING: Research Batch D. fact_checked_khop flags THAT a chain has a fabrication; this tests whether it localizes WHICH
  hop. Inject one fabricated hop at position h in {0, K//2, K-1} for K in {3,5}; per-hop grounding score = max cosine to KB
  concept; predicted fabricated hop = argmin grounding. Localization accuracy per injected position. PRODUCTION GATE: if
  middle-hop (h=K//2) localization <0.85, backward chaining (Rank 5) becomes mandatory before K>=5 deploy.
PRE-REGISTERED: HARD-PASS middle-hop localization >= 0.85. MID 0.65-0.85. HARD-FAIL <0.65 (needs backward chaining).
FORMULA SELF-TESTS (PROT-022): 1. clean hop grounded. 2. fabricated hop low grounding. 3. N.
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

ANCHOR_NAME = "fact_checked_khop_middle_hop_localization_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; V_C = 600; CHAINS = 200; KS = [3, 5]
else:
    SEEDS = [7, 17, 23]; N = 8192; V_C = 3000; CHAINS = 500; KS = [3, 5]


def bp(M, n, g):
    x = (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32); return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); C = bp(50, 256, g)
    assert np.max(C @ C[3]) > 0.99, "clean hop grounded"
    fab = bp(1, 256, g)[0]; assert np.max(C @ fab) < 0.5, "fabricated hop low grounding"
    print("[selftest] PASS: localization", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = bp(V_C, N, g); loc_by_pos = {}
    for K in KS:
        positions = [0, K // 2, K - 1]
        for h_inj in positions:
            correct = 0
            for _ in range(CHAINS):
                seq = list(g.choice(V_C, K, replace=False))                 # K hop concepts (grounded)
                hops = [C[j] for j in seq]
                hops[h_inj] = bp(1, N, g)[0]                                  # inject fabrication at h_inj
                ground = [float(np.max(C @ hops[i])) for i in range(K)]       # per-hop grounding (max sim to KB)
                pred = int(np.argmin(ground))                                 # localize = least-grounded hop
                correct += int(pred == h_inj)
            loc_by_pos["K%d_h%d" % (K, h_inj)] = correct / CHAINS
    mids = [loc_by_pos["K%d_h%d" % (K, K // 2)] for K in KS]
    return {"seed": seed, "loc_by_pos": loc_by_pos, "middle_hop_loc": float(np.mean(mids))}


def verdict(ps) -> Tuple[str, str]:
    mid = float(np.mean([p["middle_hop_loc"] for p in ps]))
    agg = {k: round(float(np.mean([p["loc_by_pos"][k] for p in ps])), 3) for k in ps[0]["loc_by_pos"]}
    summary = "localization by (K,pos): %s | middle-hop=%.3f" % (agg, mid)
    if mid >= 0.85:
        return ("HARD_PASS", "HARD_PASS: middle-hop fabrication localization >=0.85 -- production gate clears, forward-only K-hop deployable. " + summary)
    if mid >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: middle-hop localization 0.65-0.85 (usable; backward chaining optional). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: middle-hop localization <0.65 -- backward chaining (Rank 5) MANDATORY before K>=5. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_c=%d KS=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, V_C, KS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r); print("  [seed=%d] middle_hop_loc=%.3f" % (seed, r["middle_hop_loc"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
