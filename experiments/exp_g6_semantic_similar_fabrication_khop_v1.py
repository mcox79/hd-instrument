"""
exp_g6_semantic_similar_fabrication_khop_v1 -- Batch G6 (AT-2 adaptive khop attack) -- CPU.

ROUTING: Batch G Tier-2 (adversarial drill #2). fact_checked_khop localization scored 1.000 -- but only vs RANDOM
  fabrications (which ground low, trivially caught). The adaptive attack injects a SEMANTICALLY SIMILAR fabrication
  (cosine > 0.85 to the true fact, different entity) at the middle hop K/2. A near-neighbor fab grounds HIGH (close to a
  real KB concept) -> may evade the argmin-grounding localizer. Tests whether per-hop localization survives high-cosine
  fabrications, or needs hash-exact (not similarity-threshold) verification. CPU $0.
PRE-REGISTERED: HARD-PASS middle-hop localization >= 0.85 even at cosine>0.85 fabs. MID 0.65-0.85. HARD-FAIL <0.65
  (similarity-threshold localization insufficient; needs hash-exact per-hop verification).
FORMULA SELF-TESTS (PROT-022): 1. near-neighbor cosine>0.85. 2. random fab low grounding. 3. clean hop grounded.
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

ANCHOR_NAME = "g6_semantic_similar_fabrication_khop_v1"
COS_TARGET = 0.87
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; V_C = 600; CHAINS = 200; KS = [3, 5]
else:
    SEEDS = [7, 17, 23]; N = 8192; V_C = 3000; CHAINS = 500; KS = [3, 5]


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def bp(M, n, g):
    return unit((g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32))


def near_neighbor(vec, g, cos=COS_TARGET):
    noise = g.standard_normal(vec.shape).astype(np.float32); noise = unit(noise - (noise @ vec) * vec)
    return unit(cos * vec + np.sqrt(max(1e-6, 1 - cos * cos)) * noise)


def _selftest():
    g = np.random.default_rng(0); C = bp(50, 256, g); nn = near_neighbor(C[3], g)
    assert abs(float(nn @ C[3]) - COS_TARGET) < 0.06, "near-neighbor cosine ~ target"
    assert float(np.max(C @ bp(1, 256, g)[0])) < 0.5, "random fab low grounding"
    assert float(np.max(C @ C[3])) > 0.99, "clean hop grounded"
    print("[selftest] PASS: g6-semfab", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = bp(V_C, N, g); loc_by_k = {}
    for K in KS:
        h_inj = K // 2; correct = 0
        for _ in range(CHAINS):
            seq = list(g.choice(V_C, K, replace=False)); hops = [C[j] for j in seq]
            true_concept = hops[h_inj]; hops[h_inj] = near_neighbor(true_concept, g)   # high-cosine fab at middle hop
            ground = [float(np.max(C @ hops[i])) for i in range(K)]
            correct += int(int(np.argmin(ground)) == h_inj)
        loc_by_k["K%d" % K] = correct / CHAINS
    mid = float(np.mean(list(loc_by_k.values())))
    return {"seed": seed, "loc_by_k": loc_by_k, "middle_hop_loc": mid}


def verdict(ps) -> Tuple[str, str]:
    loc = float(np.mean([p["middle_hop_loc"] for p in ps]))
    curve = {k: round(float(np.mean([p["loc_by_k"][k] for p in ps])), 3) for k in ps[0]["loc_by_k"]}
    summary = "middle-hop localization at cosine>%.2f fabs: %s | mean=%.3f" % (COS_TARGET, curve, loc)
    if loc >= 0.85:
        return ("HARD_PASS", "HARD_PASS: per-hop localization survives high-cosine fabrications (>=0.85) -- robust to adaptive semantic attack. " + summary)
    if loc >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: localization degraded under semantic fabs (0.65-0.85). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: localization fails on high-cosine fabs (<0.65) -- needs hash-exact (not similarity) per-hop verification. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_c=%d KS=%s cos=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, V_C, KS, COS_TARGET), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
