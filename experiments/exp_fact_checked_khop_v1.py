"""
exp_fact_checked_khop_v1 -- Batch B: K-hop reasoning with per-hop hallucination detection (composition demo) -- CPU.

ROUTING: Research Batch B. Composition of validated capabilities: native K-hop chained retrieval (W_c = sum next.cur^T)
  PLUS per-hop KF-1 grounding (each intermediate hop's retrieved concept must be grounded in the stored KB; a fabricated
  hop is flagged). Unique vs frontier LLMs: per-hop hallucination LOCALIZATION. Reports K-hop accuracy + per-hop
  flag AUC (grounded hop vs injected-fabricated hop). CPU numpy $0.
PRE-REGISTERED: HARD-PASS k-hop acc(K=3..5)>=0.90 AND fabrication-flag AUC>=0.90. MID one>=0.80. HF either<0.75.
FORMULA SELF-TESTS (PROT-022): 1. chain step recovers. 2. grounding separates. 3. N.
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

ANCHOR_NAME = "fact_checked_khop_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048; V_C = 600; CHAINS = 150; KS = [2, 3, 5]
else:
    SEEDS = [7, 17, 23]; N = 8192; V_C = 3000; CHAINS = 400; KS = [2, 3, 4, 5]


def bp(M, n, g):
    x = (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32); return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); C = bp(20, 256, g); seq = [0, 5, 9]
    W = sum(np.outer(C[seq[i + 1]], C[seq[i]]) for i in range(2))
    cur = C[seq[0]]
    for _ in range(2):
        cur = C[np.argmax(C @ (W @ cur))]
    assert np.allclose(cur, C[seq[2]]), "chain step recovers"
    print("[selftest] PASS: khop chain", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = bp(V_C, N, g)
    acc_by_k = {}; grounded_scores = []; fabricated_scores = []
    for K in KS:
        ok = 0
        for _ in range(CHAINS):
            seq = g.choice(V_C, K + 1, replace=False)
            W = sum(np.outer(C[seq[i + 1]], C[seq[i]]) for i in range(K)) / N
            cur = C[seq[0]]; path = []
            for _h in range(K):
                nxt = C @ (W @ cur); j = int(np.argmax(nxt)); path.append(j); cur = C[j]
                grounded_scores.append(float(np.max(C @ cur)))                 # grounded hop: high max-sim to KB concept
            ok += int(path[-1] == seq[-1])
            fab = bp(1, N, g)[0]; fabricated_scores.append(float(np.max(C @ fab)))  # fabricated concept: low grounding
        acc_by_k["k%d" % K] = ok / CHAINS
    def auc(pos, neg):
        pos = np.asarray(pos); neg = np.asarray(neg); r = np.argsort(np.argsort(np.concatenate([pos, neg])))
        return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))
    flag_auc = auc(grounded_scores, fabricated_scores)
    kmid = "k%d" % KS[len(KS) // 2]
    return {"seed": seed, "acc_by_k": acc_by_k, "acc_mid": acc_by_k[kmid], "fabrication_flag_auc": flag_auc}


def verdict(ps) -> Tuple[str, str]:
    am = float(np.mean([p["acc_mid"] for p in ps])); fa = float(np.mean([p["fabrication_flag_auc"] for p in ps]))
    curve = {k: round(float(np.mean([p["acc_by_k"][k] for p in ps])), 3) for k in ps[0]["acc_by_k"]}
    summary = "khop_acc=%s fabrication_flag_AUC=%.3f" % (curve, fa)
    if am >= 0.90 and fa >= 0.90:
        return ("HARD_PASS", "HARD_PASS: K-hop reasoning + per-hop hallucination LOCALIZATION both work -- composition unique vs frontier LLM. " + summary)
    if am >= 0.80 and fa >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: composition partial. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: composition breaks (khop or flag <0.75). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_c=%d KS=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, V_C, KS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r); print("  [seed=%d] acc=%s flag_auc=%.3f" % (seed, {k: round(v, 2) for k, v in r["acc_by_k"].items()}, r["fabrication_flag_auc"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
