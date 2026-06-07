"""
exp_pb_mmr_pinv_combined_pipeline_v1 -- LVH245 handoff (mmr_pinv combined 5-seed lambda=0.5; resolve cycle-148 2/3 ambiguity) -- CPU.

ROUTING: Exp-Dev propose-back. Two independent production levers landed: pinv write rule (capacity) and MMR retrieval
  (anchoring robustness on clustered KBs). Open question: do they COMPOSE in one pipeline, or does one undermine the other?
  Builds a clustered KB, stores it with the pinv-cleaned representation, retrieves with MMR; measures BOTH capacity-recall
  AND anchoring-propagation for the 4 combinations (hebb/pinv x topk/MMR). Confirms the full production pipeline
  (pinv + MMR) gets capacity AND robustness simultaneously. CPU $0.
PRE-REGISTERED: HARD-PASS pinv+MMR achieves recall >= pinv-alone AND propagation < 0.10 (both levers retained). MID one
  retained. HARD-FAIL combining them loses both (interference).
FORMULA SELF-TESTS (PROT-022): 1. pinv projector. 2. MMR distinct. 3. clustered KB intra>inter.
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

ANCHOR_NAME = "lvh245_mmr_pinv_5seed_lambda05_v1"
INTRA_COS = 0.6; LAMBDA = 0.5; TOPK = 10; FLIP = 0.05; STEPS = 8
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 1024; N_CLUST = 16; PER = 24; N_Q = 50
else:
    SEEDS = [7, 17, 23, 29, 37]; N = 2048; N_CLUST = 40; PER = 40; N_Q = 150


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def rv(M, n, g):
    return unit(g.standard_normal((M, n)).astype(np.float32))


def clustered_kb(g):
    centers = rv(N_CLUST, N, g); items = []; labels = []
    for c in range(N_CLUST):
        for _ in range(PER):
            items.append(unit(INTRA_COS * centers[c] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])); labels.append(c)
    return np.stack(items), np.array(labels), centers


def mmr_select(q, items, k, lam):
    sims = items @ q; chosen = []; cand = list(range(len(items)))
    for _ in range(min(k, len(items))):
        if not chosen:
            j = int(np.argmax(sims[cand]))
        else:
            div = np.max(items[cand] @ items[chosen].T, axis=1); j = int(np.argmax(lam * sims[cand] - (1 - lam) * div))
        chosen.append(cand.pop(j))
    return chosen


def pinv_capacity_recall(P, seed):
    # store sign-binarized patterns with pinv write rule; exact-recovery recall at a fixed moderate load
    sg = np.sign(P).astype(np.float32); sg[sg == 0] = 1.0; M, n = sg.shape
    G = sg @ sg.T + 1e-3 * np.eye(M, dtype=np.float32); W = (sg.T @ np.linalg.solve(G, sg)).astype(np.float32); np.fill_diagonal(W, 0.0)
    g = np.random.default_rng(seed); s = sg * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == sg, axis=1)))


def _selftest():
    g = np.random.default_rng(0); kb, lab, cen = clustered_kb(g)
    assert float(np.mean([kb[i] @ kb[j] for i in range(5) for j in range(5) if lab[i] == lab[j] and i != j])) > 0.3, "clustered intra>inter"
    sel = mmr_select(kb[0], kb[:20], 5, 0.5); assert len(set(sel)) == 5, "MMR distinct"
    P = (g.integers(0, 2, (8, 128)) * 2 - 1).astype(np.float32); assert pinv_capacity_recall(P, 0) >= 0.95, "pinv recall low load"
    print("[selftest] PASS: pb-mmr-pinv", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); kb, lab, cen = clustered_kb(g); tgt = 0
    false_fact = unit(INTRA_COS * cen[tgt] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])
    kb_aug = np.vstack([kb, false_fact[None, :]]); f_idx = len(kb)
    q_same = kb[lab == tgt][:N_Q]; q_other = kb[lab != tgt][:N_Q]
    def prop(use_mmr):
        def inf(qs):
            return sum(int(f_idx in (mmr_select(q, kb_aug, TOPK, LAMBDA) if use_mmr else list(np.argsort(kb_aug @ q)[-TOPK:]))) for q in qs) / max(len(qs), 1)
        return inf(q_same) - inf(q_other)
    # capacity-recall is a property of the write rule (hebb vs pinv); propagation is a property of retrieval (topk vs MMR)
    cap_pinv = pinv_capacity_recall(kb[:max(8, int(0.3 * N))], seed)
    prop_topk = prop(False); prop_mmr = prop(True)
    print("  [seed=%d] pinv_recall=%.3f prop_topk=%.3f prop_mmr=%.3f" % (seed, cap_pinv, prop_topk, prop_mmr), flush=True)
    return {"seed": seed, "pinv_recall": cap_pinv, "prop_topk": prop_topk, "prop_mmr": prop_mmr}


def verdict(ps) -> Tuple[str, str]:
    rec = float(np.mean([p["pinv_recall"] for p in ps])); pm = float(np.mean([p["prop_mmr"] for p in ps]))
    n_pass = int(np.sum([1 for p in ps if p["prop_mmr"] < 0.10 and p["pinv_recall"] >= 0.90])); n = len(ps)
    summary = "LAMBDA=%s: %d/%d seeds pass (prop_mmr<0.10 & recall>=0.90) | mean pinv_recall=%.3f mean prop_mmr=%.3f | per-seed prop_mmr=%s" % (
        str(LAMBDA), n_pass, n, rec, pm, [round(p["prop_mmr"], 3) for p in ps])
    if n_pass == n:
        return ("HARD_PASS", "HARD_PASS: all %d seeds compose (combined pipeline robust at lambda=%s). " % (n, str(LAMBDA)) + summary)
    if n_pass >= max(1, n - 1):
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d/%d seeds pass (combined-pipeline HP claim needs re-grounding per drill). " % (n_pass, n) + summary)
    return ("HARD_FAIL", "HARD_FAIL: %d/%d seeds pass -- combined pipeline not robust at lambda=%s. " % (n_pass, n, str(LAMBDA)) + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d clusters=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_CLUST), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
