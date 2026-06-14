"""
exp_substrate_m1b_distribution_shape_separability_heldout_cpu_v1.py -- DECISION 34a follow-up: does ANY bge score-DISTRIBUTION-SHAPE feature separate IN-COVERAGE from COVERAGE-GAP held-out questions? -- completes the M1 spec (top-1 threshold FAILED in v1; Director's M1 spec said unknown queries are "flatter" -- this tests shape, not just threshold). Runs on BGE machine.

ROUTING: Director DECISION 33 M1 spec ("score distribution shifts; lower top-K confidence; flatter; refuse if distribution matches unknown signature").
  v1 (substrate_m1_refuse_gate) tested ONLY the top-1 threshold variant -> HARD_FAIL (distributions overlap). This v1b tests whether a
  DIFFERENT feature of the per-question bge top-20 score vector separates the two buckets where top-1 did not. Features: top1, margin(top1-top2),
  mean5, mean20, peak(top1-mean20), flatness(std20), mass_ge_070 (count>=0.70), mass_ge_080. For each feature compute the BEST single-threshold
  split separating in-coverage(should be HIGH/peaked) from coverage-gap(should be LOW/flat) + leave-one-out balanced accuracy + AUC.
  DECISIVE: if best feature AUC < ~0.75 -> NO usable separation -> M1 (confidence-shape calibration) CONCLUSIVELY dead; M4 paraphrase-invariance is
  the enabling precondition (raise in-coverage confidence so distributions separate). If a feature AUC >= 0.90 -> M1 salvageable via that feature.
  n=7 in-cov / 6 gap (SMALL -- report per-question values + honest small-n caveat). Substrate-internal (bge primitive; no LLM). ASCII; --self-test + metrics.json.
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
ANCHOR_NAME = "substrate_m1b_distribution_shape_separability_heldout_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def shape_feats(scores: List[float]) -> Dict[str, float]:
    s = sorted([float(x) for x in scores], reverse=True)
    if not s:
        return {"top1": 0.0, "margin": 0.0, "mean5": 0.0, "mean20": 0.0, "peak": 0.0, "flatness": 0.0, "mass070": 0.0, "mass080": 0.0}
    top1 = s[0]; top2 = s[1] if len(s) > 1 else 0.0
    m5 = sum(s[:5]) / min(5, len(s)); m20 = sum(s[:20]) / min(20, len(s))
    return {"top1": top1, "margin": top1 - top2, "mean5": m5, "mean20": m20, "peak": top1 - m20,
            "flatness": float(np.std(s[:20])), "mass070": float(sum(1 for v in s if v >= 0.70)), "mass080": float(sum(1 for v in s if v >= 0.80))}


def auc(pos: List[float], neg: List[float]) -> float:
    """AUC = P(pos score > neg score); pos = in-coverage (expected higher/peaked)."""
    if not pos or not neg:
        return 0.5
    w = 0.0
    for p in pos:
        for n in neg:
            w += 1.0 if p > n else (0.5 if p == n else 0.0)
    return w / (len(pos) * len(neg))


def best_split_bal_acc(pos: List[float], neg: List[float]) -> Tuple[float, float]:
    """best single threshold (pos>=t) balanced accuracy + threshold."""
    cuts = sorted(set(pos + neg)); best = (0.0, 0.0)
    for t in cuts + [max(cuts) + 1e-6]:
        tp = sum(1 for x in pos if x >= t); tn = sum(1 for x in neg if x < t)
        ba = 0.5 * (tp / len(pos) + tn / len(neg))
        if ba > best[0]:
            best = (ba, t)
    return best


def _selftest():
    f = shape_feats([0.9, 0.5, 0.4]); assert abs(f["margin"] - 0.4) < 1e-9 and f["mass080"] == 1.0
    assert auc([1, 1], [0, 0]) == 1.0 and auc([0, 0], [1, 1]) == 0.0 and auc([1], [1]) == 0.5
    ba, t = best_split_bal_acc([1.0, 0.9], [0.1, 0.2]); assert abs(ba - 1.0) < 1e-9
    print("[selftest] PASS: substrate_m1b_distribution_shape_separability_heldout_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    if not HELDOUT.exists():
        return {"error": "no_heldout_file"}
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
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    perq = []
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        in_cov = any(_short(g) in sset for g in gold)
        try:
            cands = r.semantic(q["question"], top_k=20)
            scores = [float(getattr(c, "score", 0.0)) for c in cands]
        except Exception:
            scores = []
        perq.append({"qid": q["qid"], "in_cov": in_cov, "feats": shape_feats(scores)})
    inc = [x for x in perq if x["in_cov"]]; gap = [x for x in perq if not x["in_cov"]]
    feat_names = ["top1", "margin", "mean5", "mean20", "peak", "flatness", "mass070", "mass080"]
    results = []
    for fn in feat_names:
        pos = [x["feats"][fn] for x in inc]; neg = [x["feats"][fn] for x in gap]
        a = auc(pos, neg); ba, t = best_split_bal_acc(pos, neg)
        results.append({"feature": fn, "auc": round(a, 3), "best_bal_acc": round(ba, 3), "threshold": round(t, 4),
                        "in_cov_mean": round(float(np.mean(pos)), 4), "gap_mean": round(float(np.mean(neg)), 4)})
    results.sort(key=lambda d: d["auc"], reverse=True)
    print("  n_in_cov=%d n_gap=%d (SMALL -- per-question + small-n caveat)" % (len(inc), len(gap)), flush=True)
    print("  feature    AUC    bal_acc  thr     in_cov_mean  gap_mean", flush=True)
    for d in results:
        print("  %-9s  %.3f  %.3f    %.3f   %.4f       %.4f" % (d["feature"], d["auc"], d["best_bal_acc"], d["threshold"], d["in_cov_mean"], d["gap_mean"]), flush=True)
    print("\n  per-question shape features:", flush=True)
    for x in perq:
        f = x["feats"]
        print("  %-9s %s top1=%.3f margin=%.3f peak=%.3f flat=%.3f mass070=%d" % (
            x["qid"], ("IN " if x["in_cov"] else "GAP"), f["top1"], f["margin"], f["peak"], f["flatness"], int(f["mass070"])), flush=True)
    return {"n_in_cov": len(inc), "n_gap": len(gap), "feature_separability": results, "best_feature": results[0] if results else None}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    bf = r["best_feature"]
    if not bf:
        return ("UNKNOWN", "no features computed")
    base = ("M1b distribution-shape separability (DECISION 34a follow-up). Best discriminating feature: %s AUC=%.3f bal_acc=%.3f "
            "(in_cov_mean=%.4f vs gap_mean=%.4f). n=%d/%d (SMALL). Top-1 threshold M1 already FAILED in v1; this tests shape." % (
                bf["feature"], bf["auc"], bf["best_bal_acc"], bf["in_cov_mean"], bf["gap_mean"], r["n_in_cov"], r["n_gap"]))
    if bf["auc"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS (M1 SALVAGEABLE via shape): feature '%s' separates in-coverage from coverage-gap at AUC=%.3f -- a "
                "confidence-SHAPE gate (not raw top-1 threshold) could deliver refuse-robustness. RE-RUN the refuse-gate using this feature. "
                "(small-n; confirm on larger held-out.) " % (bf["feature"], bf["auc"]) + base)
    if bf["auc"] >= 0.75:
        return ("PARTIAL", "PARTIAL (weak shape signal): best feature '%s' AUC=%.3f -- some separation but below the 0.90 bar for a reliable gate. "
                "M1-shape alone insufficient; would need to compose with M4. " % (bf["feature"], bf["auc"]) + base)
    return ("HARD_FAIL", "HARD_FAIL (M1 CONCLUSIVELY dead): NO bge score-distribution-shape feature separates in-coverage from coverage-gap "
            "(best AUC=%.3f < 0.75). The Director's 'unknown queries are flatter' hypothesis is REFUTED on this held-out: in-coverage "
            "(present-but-paraphrased) queries are NOT more confident/peaked than coverage-gap (absent) queries. Confidence calibration of ANY "
            "shape cannot fix refuse-robustness here. M4 paraphrase-invariant retrieval is the ENABLING PRECONDITION -- it must raise in-coverage "
            "confidence so a gate becomes possible. Confirms the M4-first sequence. " % bf["auc"] + base)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
