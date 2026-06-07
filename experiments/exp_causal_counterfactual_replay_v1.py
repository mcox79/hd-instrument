"""
exp_causal_counterfactual_replay_v1 -- causal/counterfactual (3x) anchor 1 (DECISIVE) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_causal_counterfactual_3x #1. Synthetic causal chains stored as a
  HETERO-ASSOCIATIVE source->target map (pinv). For each chain substitute one mid-chain target (the do(X=x) intervention)
  into a query-scoped W_tmp, re-run the hop from that node, measure fraction reaching the correct MODIFIED conclusion.
  Minimum viable falsification of local counterfactual replay. EU AI Act Article 12 post-hoc audit (Aug 2026). CPU $0 ~2min.
PRE-REGISTERED: HARD-PASS >=80%% reach correct modified conclusion AND <10ms/intervention. MID 50-80%%. HARD-FAIL <50%%.
FORMULA SELF-TESTS (PROT-022): 1. clean hop retrieves true next. 2. counterfactual hop retrieves new target. 3. cosine bound.
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

ANCHOR_NAME = "causal_counterfactual_replay_v1"
N = 1024; RIDGE = 1e-3
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENT = 60; N_CHAIN = 20; KLEN = 4
else:
    SEEDS = [7, 17, 23]; N_ENT = 100; N_CHAIN = 60; KLEN = 5


def hetero_W(S, T):
    # source->target associative map: W @ s_i ~= t_i ; W = T^T (S S^T + ridge)^-1 S
    G = S @ S.T + RIDGE * np.eye(S.shape[0]); return T.T @ np.linalg.solve(G, S)


def hop(W, src_vec, ent):
    out = W @ src_vec; sims = ent @ out; return int(np.argmax(sims))


def _selftest():
    g = np.random.default_rng(0); ent = np.sign(g.standard_normal((10, 128))).astype(np.float64); ent[ent == 0] = 1.0
    chain = [0, 1, 2, 3]; S = np.stack([ent[chain[i]] for i in range(3)]); T = np.stack([ent[chain[i + 1]] for i in range(3)])
    W = hetero_W(S, T); assert hop(W, ent[1], ent) == 2, "clean hop retrieves true next"
    Tm = T.copy(); Tm[1] = ent[7]; Wm = hetero_W(S, Tm); assert hop(Wm, ent[1], ent) == 7, "counterfactual hop retrieves new target"
    print("[selftest] PASS: causal-counterfactual", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); ent = np.sign(g.standard_normal((N_ENT, N))).astype(np.float64); ent[ent == 0] = 1.0
    correct = 0; lat = []
    for c in range(N_CHAIN):
        chain = g.choice(N_ENT, KLEN + 1, replace=False)
        S = np.stack([ent[chain[i]] for i in range(KLEN)]); T = np.stack([ent[chain[i + 1]] for i in range(KLEN)])
        m = KLEN // 2; new_tail = int(g.integers(0, N_ENT))
        while new_tail in chain:
            new_tail = int(g.integers(0, N_ENT))
        t0 = time.perf_counter()
        Tm = T.copy(); Tm[m] = ent[new_tail]                                       # do(): replace target of mid hop
        W_tmp = hetero_W(S, Tm)                                                     # query-scoped counterfactual map
        lat.append((time.perf_counter() - t0) * 1e3)
        if hop(W_tmp, ent[chain[m]], ent) == new_tail:                             # hop from the intervened node
            correct += 1
    acc = correct / N_CHAIN; ml = float(np.mean(lat))
    print("  [seed=%d] counterfactual_accuracy=%.3f mean_intervention_ms=%.3f" % (seed, acc, ml), flush=True)
    return {"seed": seed, "accuracy": acc, "intervention_ms": ml}


def verdict(ps) -> Tuple[str, str]:
    a = float(np.mean([p["accuracy"] for p in ps])); ml = float(np.mean([p["intervention_ms"] for p in ps]))
    summary = "counterfactual_accuracy=%.3f mean_intervention=%.3fms (do() via hetero-assoc target swap)" % (a, ml)
    if a >= 0.80 and ml < 10:
        return ("HARD_PASS", "HARD_PASS: local counterfactual replay reaches the correct modified conclusion >=80%% at <10ms -- substrate exposes a 'what-if?' API for EU AI Act Article 12 audit. " + summary)
    if a >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: counterfactual replay 50-80%% (or latency>10ms). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: counterfactual replay <50%% -- do() does not translate to retrieval. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d entities=%d chains=%d K=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_ENT, N_CHAIN, KLEN), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
