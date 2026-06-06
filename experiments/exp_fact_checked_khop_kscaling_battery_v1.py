"""
exp_fact_checked_khop_kscaling_battery_v1 -- BUNDLED Batch D K-scaling production battery -- CPU (long).

ROUTING: Batch D bundled + CPU-load (one long job vs many fast cells). Maps the full K-scaling curve K=[3,5,8,10,15,20] for
  fact_checked_khop production-readiness. Per K, high chain count, measures: joint detection AUC (binary flag), confidence
  detection AUC (C_min/C_chain), and middle-hop localization. Directly tests the drill's structural-ceiling prediction
  joint_AUC >= 1 - K*(1-AUC_hop): does detection/localization survive to K=20? Bundles Rank1 (confidence) + Rank2
  (localization) analysis across the full K range. CPU numpy $0.
PRE-REGISTERED: HARD-PASS at K=20 both detection AUC >= 0.90 AND middle-hop localization >= 0.85 (production-ready to K=20).
  MID one >= threshold. HARD-FAIL both below (structural ceiling bites; needs architecture changes).
FORMULA SELF-TESTS (PROT-022): 1. clean grounded. 2. fabricated low. 3. AUC bounds.
ASCII-only. write_metrics. PROT-018 no _nN (K-sweep).
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

ANCHOR_NAME = "fact_checked_khop_kscaling_battery_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; V_C = 600; CHAINS = 150; KS = [3, 10]
else:
    SEEDS = [7, 17, 23, 29, 37]; N = 8192; V_C = 4000; CHAINS = 1500; KS = [3, 5, 8, 10, 15, 20]


def bp(M, n, g):
    x = (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32); return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-8)


def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg])))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def _selftest():
    g = np.random.default_rng(0); C = bp(50, 256, g); assert np.max(C @ C[3]) > 0.99, "clean grounded"
    assert np.max(C @ bp(1, 256, g)[0]) < 0.5, "fabricated low"
    assert auc([1, 1], [0, 0]) == 1.0, "AUC bounds"
    print("[selftest] PASS: kscaling", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = bp(V_C, N, g); by_K = {}
    for K in KS:
        bf_p, bf_n, cm_p, cm_n = [], [], [], []; loc_ok = 0; loc_tot = 0
        for _ in range(CHAINS):
            # clean chain
            seq = list(g.choice(V_C, K, replace=False)); conf = np.array([float(np.max(C @ C[seq[i]])) for i in range(K)])
            bf_n.append(int(np.any(conf < 0.5))); cm_n.append(-float(conf.min()))
            # fabricated chain (inject at random position, localize)
            seq = list(g.choice(V_C, K, replace=False)); hops = [C[j] for j in seq]; hinj = int(g.integers(0, K)); hops[hinj] = bp(1, N, g)[0]
            conf = np.array([float(np.max(C @ hops[i])) for i in range(K)])
            bf_p.append(int(np.any(conf < 0.5))); cm_p.append(-float(conf.min()))
            loc_ok += int(np.argmin(conf) == hinj); loc_tot += 1
        by_K["k%d" % K] = {"binary_auc": auc(bf_p, bf_n), "conf_auc": auc(cm_p, cm_n), "localization": loc_ok / loc_tot}
        print("  [seed=%d K=%d] binary_auc=%.3f conf_auc=%.3f loc=%.3f" % (seed, K, by_K["k%d" % K]["binary_auc"], by_K["k%d" % K]["conf_auc"], by_K["k%d" % K]["localization"]), flush=True)
    return {"seed": seed, "by_K": by_K}


def verdict(ps) -> Tuple[str, str]:
    kmax = "k%d" % KS[-1]
    det = float(np.mean([max(p["by_K"][kmax]["binary_auc"], p["by_K"][kmax]["conf_auc"]) for p in ps]))
    loc = float(np.mean([p["by_K"][kmax]["localization"] for p in ps]))
    curve = {k: round(float(np.mean([p["by_K"][k]["conf_auc"] for p in ps])), 3) for k in ps[0]["by_K"]}
    summary = "conf_auc by K: %s | at K=%d det=%.3f loc=%.3f" % (curve, KS[-1], det, loc)
    if det >= 0.90 and loc >= 0.85:
        return ("HARD_PASS", "HARD_PASS: detection AND localization survive to K=%d -- killer demo production-ready at production depth. " % KS[-1] + summary)
    if det >= 0.90 or loc >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one of detection/localization holds at K=%d. " % KS[-1] + summary)
    return ("HARD_FAIL", "HARD_FAIL: structural ceiling bites at K=%d (both below threshold). " % KS[-1] + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_c=%d KS=%s chains=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, V_C, KS, CHAINS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
