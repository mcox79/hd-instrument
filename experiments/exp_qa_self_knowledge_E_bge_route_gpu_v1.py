"""
exp_qa_self_knowledge_E_bge_route_gpu_v1.py -- can a bge E-route beat the keyword-only E-route? (E gold at bge rank ~0.0) (GPU/bge) -- GPU.

ROUTING: the A-cue-alignment diagnosis showed the bge cue is excellent (A-gold median rank 0.5/1743, cos ~0.77, recall@10=1.0)
  but A-gold sets are SMALL (2-3 atoms), so the production fixed keyword-UNION-bge-top-3 caps recall of the full gold set. This
  cell tests the lever the measurement implies: an ADAPTIVE-SIZE selection via a bge cosine THRESHOLD (return all atoms with
  cos >= tau), which can capture a 3-atom gold set when all 3 are above threshold WITHOUT the precision crash of a large fixed
  k. Sweep policies on the 12 A-axis answerable-with-gold Qs and compute FULL-gold-set E-F1: production (keyword UNION top-3),
  bge-top-k (k=3,5,8), cosine-threshold (tau=0.60..0.75), keyword UNION threshold. Decisive: either a threshold beats the tuned
  baseline (NEW E-axis lever toward path-to-0.70) or confirms the tuned-UNION ceiling now with the cue mechanism understood.
  bge = embedding model (NO generative LLM); substrate-physics of the A-route.

PRE-REGISTERED: HARD-PASS best policy E-F1 >= production_A_F1 + 0.05 (a real A-axis lift). MIDDLE +0.02..+0.05. HARD-FAIL best
  policy <= production + 0.02 (tuned UNION confirmed near-ceiling; threshold does not help). UNKNOWN if bge/benchmark unavailable.
ASCII-only. write_metrics. PROT-020 (import torch). GPU. Route via overnight_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json, re
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "qa_self_knowledge_E_bge_route_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
STOP = {"the", "a", "an", "of", "to", "and", "in", "is", "it", "for", "on", "about", "do", "i", "have", "what", "which", "family"}


def _norm(qid):
    return str(qid).split("::")[-1].strip()


def _f1(retrieved, gold):
    if not gold:
        return 1.0 if not retrieved else 0.0
    tp = len(retrieved & gold); fp = len(retrieved - gold); fn = len(gold - retrieved)
    p = tp / (tp + fp + 1e-9); r = tp / (tp + fn + 1e-9)
    return 2 * p * r / (p + r + 1e-9)


def _selftest():
    assert abs(_f1({"a", "b"}, {"a", "b"}) - 1.0) < 1e-6
    assert _f1({"a", "x"}, {"a", "b"}) < 1.0 and _norm("c::T1/x") == "T1/x"
    print("[selftest] PASS: qa_self_knowledge_E_bge_route_gpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch  # PROT-020
    _ = torch.cuda.is_available()
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)


def route_E_keyword(atoms, topic):
    """production E-route: >=2 scenario-keyword hits, restricted to meta/methodology corpus."""
    kws = [w for w in topic.lower().split() if w not in STOP and len(w) > 2]
    out = set()
    for a in atoms:
        if str(getattr(a.corpus, "value", a.corpus)).lower() not in ("meta", "methodology"):
            continue
        hay = (a.name + " " + (a.id or "") + " " + " ".join(getattr(a, "aliases", []) or []) + " " + (getattr(a, "description", "") or "")).lower()
        if sum(1 for k in kws if k in hay) >= 2:
            out.add(_norm(a.id))
    return out


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    bench_fp = REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl"
    if not bench_fp.exists():
        return {"error": "benchmark_missing"}
    raw = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    aqs = []
    for r in raw:
        if r.get("type", "A").split("_")[0].upper() != "E":
            continue
        gold = list(r.get("ground_truth_atoms") or r.get("gold") or [])
        if not gold:
            continue
        args = r.get("args") or {}
        aqs.append({"id": r.get("qid") or r.get("id"), "topic": args.get("scenario") or args.get("topic") or r.get("question", ""),
                    "gold": set(_norm(g) for g in gold)})
    if SMOKE: aqs = aqs[:5]
    idx_dir = REPO / "data" / "substrate_index"
    if not idx_dir.exists():
        return {"error": "no_substrate_index"}
    pstore = PartitionedStore(idx_dir); atoms = pstore.all_atoms()
    all_ids = set(_norm(a.id) for a in atoms)
    try:
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        enc = AtomEncoder(); retr = Retriever(getattr(pstore, "store", pstore), enc); retr.rebuild_index()
    except Exception as e:
        return {"error": "bge_unavailable", "note": str(e)[:160]}
    id_order = retr._id_order; sem = retr._semantic_matrix
    norm_ids = [_norm(i) for i in id_order]
    # restrict bge candidate pool to meta/methodology corpus (matches E-route domain; avoids non-methodology distractors)
    corpus_of = {_norm(a.id): str(getattr(a.corpus, "value", a.corpus)).lower() for a in atoms}
    meth_mask = np.array([corpus_of.get(nid, "") in ("meta", "methodology") for nid in norm_ids])
    # restrict gold to present
    for q in aqs:
        q["gold"] = set(g for g in q["gold"] if g in all_ids)
    policies = {"prod_E_keyword": None, "bge_top3": None, "bge_top5": None, "bge_top8": None,
                "thr_0.60": 0.60, "thr_0.65": 0.65, "thr_0.70": 0.70, "thr_0.75": 0.75,
                "kw_U_thr_0.65": ("kw", 0.65), "kw_U_thr_0.70": ("kw", 0.70)}
    agg = {p: [] for p in policies}
    for q in aqs:
        qv = enc.bge.encode([q["topic"]])[0].astype(np.float32); qv /= (np.linalg.norm(qv) + 1e-9)
        sims = sem @ qv
        order = np.argsort(-sims)
        # restrict ranking to methodology corpus for bge policies
        msims = np.where(meth_mask, sims, -1e9)
        morder = np.argsort(-msims)
        topset = lambda k: set(norm_ids[morder[i]] for i in range(k))
        thrset = lambda t: set(norm_ids[i] for i in range(len(norm_ids)) if meth_mask[i] and sims[i] >= t)
        kw = route_E_keyword(atoms, q["topic"])
        for p, cfg in policies.items():
            if p == "prod_E_keyword":
                ret = kw                                      # PRODUCTION E-route: keyword only (no bge)
            elif p.startswith("bge_top"):
                ret = topset(int(p[len("bge_top"):]))
            elif p.startswith("thr_"):
                ret = thrset(cfg)
            elif p.startswith("kw_U_thr_"):
                ret = kw | thrset(cfg[1])
            else:
                ret = set()
            agg[p].append(_f1(ret, q["gold"]))
    macro = {p: round(float(np.mean(v)), 4) for p, v in agg.items()}
    prod = macro["prod_E_keyword"]
    best_p = max((p for p in macro if p != "prod_E_keyword"), key=lambda p: macro[p])
    best = macro[best_p]
    print("  E-F1 by policy (n=%d):" % len(aqs), flush=True)
    for p in policies:
        print("    %-16s %.4f%s" % (p, macro[p], "  <-- production" if p == "prod_E_keyword" else ""), flush=True)
    print("  best non-prod = %s (%.4f); production = %.4f; delta = %+.4f" % (best_p, best, prod, best - prod), flush=True)
    return {"n": len(aqs), "macro_by_policy": macro, "prod_A_f1": prod, "best_policy": best_p, "best_A_f1": best,
            "delta": round(best - prod, 4)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("note", "")))
    d = r["delta"]; s = "best=%s E-F1=%.4f vs production %.4f (delta %+.4f); all=%s; n=%d" % (
        r["best_policy"], r["best_A_f1"], r["prod_A_f1"], d, r["macro_by_policy"], r["n"])
    if d >= 0.05:
        return ("HARD_PASS", "HARD_PASS: a bge cosine-threshold / k policy BEATS the production keyword-only E-route by >=0.05 E-F1 -- a real E-axis lever toward path-to-0.70 (adaptive-size selection captures small multi-atom gold sets the fixed top-3 misses). " + s)
    if d >= 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: a threshold/k policy gives a small E-F1 lift (+0.02..0.05) -- marginal; worth Testbed considering an adaptive-k. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no policy beats the production keyword-only E-route by >0.02 -- the tuned UNION is near the A-axis ceiling (precision-recall on SMALL gold sets), confirming the prior tuned-UNION-bound finding now with the cue mechanism understood (cue is excellent; small-gold precision-recall is the wall). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
