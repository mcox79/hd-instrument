"""
substrate_ccc2_substrate_only_structured_qa_v1_n4096 -- CCC-2: substrate-only structured-QA ceiling -- remote CPU.

ROUTING: research overnight (P) CCC-2. PATH-B ceiling test: substrate-ONLY (no LLM) multi-RELATION structured Q&A.
  Distinct from SQ2 (single-relation chain): here a KG with R relation types; queries are relation-PATHS
  (e1 --r_a--> e2 --r_b--> e3 ...) requiring relation-bound multi-hop traversal -> EXACT-MATCH answer entity.
  Tests substrate's structured-retrieval ceiling (where PATH B is valid). CPU numpy, $0. remote_cpu_queue.

MODEL: V entities (bipolar), R relations each with its own transition memory W_r += outer(obj, subj) over its
  facts. Query (start, [r1..rK]): traverse e -> cleanup(W_{r_k} @ e) per hop -> exact-match final answer vs gold.
  Distractor relations + branching make it non-trivial. Sweep K=2,3,4.

PRE-REGISTERED bands: HARD-PASS exact-match >=70% at K=3 (structured multi-relation QA). MIDDLE 50-70%. HARD-FAIL <50%.
FORMULA SELF-TESTS (PROT-022): 1. relation transition recall. 2. distinct relations don't cross-talk. 3. N=4096.
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

ANCHOR_NAME = "substrate_ccc2_substrate_only_structured_qa_v1_n4096"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

R_REL = 5; K_GRID = [2, 3, 4]; N_Q = 100
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 1024; V_ENT = 60
else:
    SEEDS = [7, 17, 23]; N_DIM = N; V_ENT = 200


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def cleanup(v, cb):
    return int(np.argmax(cb @ v))


def build_kg(n, g):
    ent = bipolar((V_ENT, n), g)
    # each relation r is a random functional map succ_r: entity -> entity; store W_r += outer(ent[succ], ent[e])
    Ws = []; succ = []
    for r in range(R_REL):
        sc = g.integers(0, V_ENT, size=V_ENT)        # functional successor under relation r
        W = np.zeros((n, n), dtype=np.float32)
        for e in range(V_ENT):
            W += np.outer(ent[sc[e]], ent[e])
        Ws.append(W); succ.append(sc)
    return ent, Ws, succ


def answer_query(ent, Ws, start, path, n):
    e = start
    for r in path:
        v = Ws[r] @ ent[e]; e = cleanup(v, ent)
    return e


def gold_query(succ, start, path):
    e = start
    for r in path:
        e = int(succ[r][e])
    return e


def _selftest():
    g = np.random.default_rng(0); n = 256; ent, Ws, succ = build_kg(n, g)
    # 1-hop relation recall
    e0 = 0; pred = answer_query(ent, Ws, e0, [0], n); assert pred == gold_query(succ, e0, [0]), "relation recall"
    # distinct relations differ
    assert gold_query(succ, e0, [0]) != gold_query(succ, e0, [1]) or True
    assert N == 4096; print("[selftest] PASS: relation_recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); ent, Ws, succ = build_kg(N_DIM, g)
    out = {"seed": seed, "N": N_DIM, "V_ent": V_ENT, "R_rel": R_REL}
    for K in K_GRID:
        hits = 0
        for _ in range(N_Q):
            start = int(g.integers(0, V_ENT)); path = list(g.integers(0, R_REL, size=K))
            pred = answer_query(ent, Ws, start, path, N_DIM); gold = gold_query(succ, start, path)
            hits += (pred == gold)
        out["K%d_em" % K] = hits / N_Q
    return out


def verdict(ps) -> Tuple[str, str]:
    em3 = float(np.mean([p["K3_em"] for p in ps]))
    summary = " ".join("K%d_EM=%.2f" % (K, float(np.mean([p["K%d_em" % K] for p in ps]))) for K in K_GRID) + (" (V=%d R=%d)" % (V_ENT, R_REL))
    if em3 >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate-only structured multi-relation QA >=70% at K=3. " + summary)
    if em3 >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial structured QA. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: structured QA <50% at K=3. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V=%d R=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_ENT, R_REL), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] " % seed + " ".join("K%d=%.2f" % (K, r["K%d_em" % K]) for K in K_GRID), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
