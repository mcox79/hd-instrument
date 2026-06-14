"""
exp_substrate_m1c_confidence_coverage_separability_fullset_cpu_v1.py -- strengthen the M1b inverted-confidence finding from n=13 to n~65: does bge confidence separate IN-COVERAGE from COVERAGE-GAP across the FULL tuned+held-out question set? -- runs on BGE machine.

ROUTING: follow-up to M1b (held-out n=7/6 found ALL 8 confidence features AUC<0.5 -- inverted; small-n caveat). This re-measures the SAME
  confidence-vs-coverage separability across tuned (v3_60q q01-q60) + held-out (q54-q65), dedup by qid, EACH question bucketed by whether its
  gold atoms are in the index. Two decisive outcomes:
   (1) inversion HOLDS at n~65 (AUC<0.5) -> bge confidence is anti-correlated with correctness substrate-wide -> M1/M2 confidence-gating dead
       generally, M4 paraphrase-invariance necessity FIRM (not a small-n artifact).
   (2) tuned subset shows CORRECT correlation (in-coverage HIGHER conf; AUC>0.5) while held-out is inverted -> the inversion is LOCALIZED to
       held-out PHRASING -> precisely validates M4 (paraphrase-invariant retrieval) as the targeted fix (raises held-out in-coverage conf to match tuned).
  Reports overall AUC + tuned-only AUC + heldout-only AUC per feature, so the localization question is answered directly. Substrate-internal (bge; no LLM).
  ASCII; --self-test + metrics.json. Reuses M1b feature/auc helpers.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_m1c_confidence_coverage_separability_fullset_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA_ROOT = REPO / "data" / "substrate_index"
TUNED = DATA_ROOT / "benchmark_corpus_v3_60q.jsonl"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
FEAT_NAMES = ["top1", "margin", "mean5", "mean20", "peak", "flatness", "mass070", "mass080"]


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def shape_feats(scores: List[float]) -> Dict[str, float]:
    s = sorted([float(x) for x in scores], reverse=True)
    if not s:
        return {k: 0.0 for k in FEAT_NAMES}
    top1 = s[0]; top2 = s[1] if len(s) > 1 else 0.0
    m5 = sum(s[:5]) / min(5, len(s)); m20 = sum(s[:20]) / min(20, len(s))
    return {"top1": top1, "margin": top1 - top2, "mean5": m5, "mean20": m20, "peak": top1 - m20,
            "flatness": float(np.std(s[:20])), "mass070": float(sum(1 for v in s if v >= 0.70)), "mass080": float(sum(1 for v in s if v >= 0.80))}


def auc(pos: List[float], neg: List[float]) -> float:
    if not pos or not neg:
        return 0.5
    w = sum((1.0 if p > n else (0.5 if p == n else 0.0)) for p in pos for n in neg)
    return w / (len(pos) * len(neg))


def _selftest():
    f = shape_feats([0.9, 0.5, 0.4]); assert abs(f["margin"] - 0.4) < 1e-9
    assert auc([1, 1], [0, 0]) == 1.0 and auc([0], [1]) == 0.0
    print("[selftest] PASS: substrate_m1c_confidence_coverage_separability_fullset_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def _load_dedup() -> List[dict]:
    seen = {}; order = []
    for f in [TUNED, HELDOUT]:
        if not f.exists():
            continue
        src = "heldout" if "HELD_OUT" in f.name else "tuned"
        for l in open(f, encoding="utf-8"):
            if not l.strip():
                continue
            q = json.loads(l); qid = q.get("qid") or q.get("id")
            if not qid or not q.get("question"):
                continue
            # held-out wins on overlap (q54-q60 appear in both; held-out is the integrity set)
            if qid in seen and src != "heldout":
                continue
            if qid not in seen:
                order.append(qid)
            q["_src"] = src; q["_qid"] = qid; seen[qid] = q
    return [seen[q] for q in order]


def run() -> Dict:
    try:
        from backend.substrate_index.partition import PartitionedStore
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
    except Exception as e:
        return {"error": "import_failed:" + str(e)[:100]}
    pstore = PartitionedStore(DATA_ROOT)
    try:
        enc = AtomEncoder()
    except Exception as e:
        return {"error": "bge_unavailable:" + str(e)[:80]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    sset = {_short(a.id) for a in pstore.all_atoms()}
    qs = _load_dedup()
    if not qs:
        return {"error": "no_questions"}
    perq = []
    for q in qs:
        gold = q.get("ground_truth_atoms") or q.get("gold") or []
        if isinstance(gold, str):
            gold = [gold]
        in_cov = any(_short(g) in sset for g in gold) if gold else None  # None = no-gold (neg/boolean) -> skip from coverage AUC
        try:
            cands = r.semantic(q["question"], top_k=20)
            scores = [float(getattr(c, "score", 0.0)) for c in cands]
        except Exception:
            scores = []
        perq.append({"qid": q["_qid"], "src": q["_src"], "in_cov": in_cov, "feats": shape_feats(scores)})

    def auc_block(items):
        inc = [x for x in items if x["in_cov"] is True]; gap = [x for x in items if x["in_cov"] is False]
        out = []
        for fn in FEAT_NAMES:
            out.append({"feature": fn, "auc": round(auc([x["feats"][fn] for x in inc], [x["feats"][fn] for x in gap]), 3),
                        "n_in": len(inc), "n_gap": len(gap)})
        return sorted(out, key=lambda d: d["auc"], reverse=True), len(inc), len(gap)
    overall, n_in, n_gap = auc_block(perq)
    tuned_rows, t_in, t_gap = auc_block([x for x in perq if x["src"] == "tuned"])
    held_rows, h_in, h_gap = auc_block([x for x in perq if x["src"] == "heldout"])
    print("  total q=%d | coverage-labeled: in=%d gap=%d (no-gold skipped)" % (len(perq), n_in, n_gap), flush=True)
    print("  [OVERALL n_in=%d n_gap=%d] feature AUC (in-coverage vs gap; >0.5 = correct, <0.5 = inverted):" % (n_in, n_gap), flush=True)
    for d in overall:
        print("    %-9s AUC=%.3f" % (d["feature"], d["auc"]), flush=True)
    print("  [TUNED n_in=%d n_gap=%d] top1 AUC=%.3f mean5 AUC=%.3f" % (t_in, t_gap,
          next(d["auc"] for d in tuned_rows if d["feature"] == "top1"), next(d["auc"] for d in tuned_rows if d["feature"] == "mean5")), flush=True)
    print("  [HELDOUT n_in=%d n_gap=%d] top1 AUC=%.3f mean5 AUC=%.3f" % (h_in, h_gap,
          next(d["auc"] for d in held_rows if d["feature"] == "top1"), next(d["auc"] for d in held_rows if d["feature"] == "mean5")), flush=True)
    return {"n_total": len(perq), "n_in": n_in, "n_gap": n_gap, "overall": overall, "tuned": tuned_rows, "heldout": held_rows,
            "tuned_in": t_in, "tuned_gap": t_gap, "held_in": h_in, "held_gap": h_gap}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    best = r["overall"][0]; best_auc = best["auc"]
    t_top1 = next(d["auc"] for d in r["tuned"] if d["feature"] == "top1")
    h_top1 = next(d["auc"] for d in r["heldout"] if d["feature"] == "top1")
    base = ("M1c full-set confidence-coverage separability (n=%d coverage-labeled: in=%d gap=%d). Best overall feature %s AUC=%.3f. "
            "TUNED top1 AUC=%.3f (n_in=%d/gap=%d); HELDOUT top1 AUC=%.3f (n_in=%d/gap=%d)." % (
                r["n_in"] + r["n_gap"], r["n_in"], r["n_gap"], best["feature"], best_auc,
                t_top1, r["tuned_in"], r["tuned_gap"], h_top1, r["held_in"], r["held_gap"]))
    # localization read
    if t_top1 >= 0.65 and h_top1 <= 0.45:
        return ("HARD_PASS", "HARD_PASS (M4 TARGET VALIDATED -- inversion is LOCALIZED to held-out phrasing): TUNED confidence CORRECTLY tracks "
                "coverage (top1 AUC=%.3f>0.5) but HELDOUT is INVERTED (top1 AUC=%.3f<0.5). The substrate's confidence signal works on phrasing it "
                "was tuned on and breaks on held-out paraphrases -- EXACTLY the gap M4 paraphrase-invariant retrieval targets. M4 necessity firm + "
                "precisely scoped. " % (t_top1, h_top1) + base)
    if best_auc < 0.5 and h_top1 < 0.5:
        return ("HARD_FAIL", "HARD_FAIL (inversion is SUBSTRATE-WIDE, not small-n artifact): even at n=%d the best confidence feature AUC=%.3f<0.5. "
                "bge confidence is anti-correlated with correctness broadly. Confidence-gating (M1/M2 on bge cosine) is dead generally; M4 "
                "paraphrase-invariance necessity FIRM (the M1b finding was not a small-n fluke). " % (r["n_in"] + r["n_gap"], best_auc) + base)
    return ("PARTIAL", "PARTIAL: mixed separability. " + base)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
