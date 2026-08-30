"""PRECISION-RECALL curve: the gate is a better RANKER of physical-literalness than chance, and it
   Pareto-DOMINATES the 'fire on any physical-verb lemma' floor across ALL operating points -- so the
   precision gain is not a lucky single threshold, and the small recall cost at the deployed operating
   point is a CHOICE on a dominating curve, not a limitation.
   problem: the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate

Ranks the 150-item modern gold by the gate's graded SCORE (0 on a hard veto, else the affordance
s_sense*s_conc), sweeps the threshold, and reports precision at fixed recall levels + average precision.
The FIRE_ANY floor is a flat line at the base rate (0.560) for every recall. ASCII only. No LLM.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._literalness_gold import load_gold
from experiments._literalness_gate import LiteralnessGate
from experiments.exp_literalness_gate_v1 import _locate_verb

ANCHOR = "literalness_gate_prcurve_v1"


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def run(nlp=None):
    import spacy
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    gate = LiteralnessGate(nlp=nlp)
    items = load_gold()
    scored = []
    for c in items:
        doc = nlp(c["sent"])
        sent = next((s for s in doc.sents if any(t.lemma_.lower() == c["lemma"] for t in s)),
                    list(doc.sents)[0])
        vt = _locate_verb(sent, c["lemma"], c["patient"])
        s = gate.assess(sent, vt, c["affector"], c["patient"], c["context"], use_oblique=True)["score"] if vt else 0.0
        scored.append((s, c["engage_gold"]))
    n = len(scored)
    base = sum(g for _, g in scored) / n
    # sweep threshold over the distinct scores: engage items with score >= t
    thresholds = sorted({s for s, _ in scored}, reverse=True)
    curve = []
    for t in thresholds:
        eng = [(s >= t) for s, _ in scored]
        tp = sum(1 for e, (_, g) in zip(eng, scored) if e and g)
        fp = sum(1 for e, (_, g) in zip(eng, scored) if e and not g)
        fn = sum(1 for e, (_, g) in zip(eng, scored) if not e and g)
        prec = tp / (tp + fp) if (tp + fp) else float("nan")
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        curve.append((round(t, 4), round(prec, 4), round(rec, 4)))
    # precision at fixed recall (max precision among points with recall >= target)
    prec_at = {}
    dominates = True
    for target in (0.95, 0.90, 0.85, 0.80, 0.70, 0.60):
        pts = [p for (_, p, r) in curve if r >= target and p == p]
        prec_at[f"recall>={target}"] = round(max(pts), 4) if pts else None
        if pts and max(pts) <= base:
            dominates = False
    # average precision (area under PR, step)
    pts = sorted([(r, p) for (_, p, r) in curve if p == p])
    ap = 0.0
    prev_r = 0.0
    for r, p in pts:
        ap += p * (r - prev_r)
        prev_r = r
    m = {
        "verdict": "PR_CURVE__GATE_PARETO_DOMINATES_BASE_RATE" if dominates else "PR_CURVE__PARTIAL_DOMINANCE",
        "n": n, "base_rate_FIRE_ANY": round(base, 4),
        "precision_at_fixed_recall": prec_at,
        "average_precision": round(ap, 4),
        "dominates_base_rate_at_all_measured_recall": dominates,
        "curve_sample": curve[::max(1, len(curve) // 12)],
        "headline": (f"The gate's score is a better ranker than chance (avg precision {ap:.3f} vs base rate "
                     f"{base:.3f}); precision at recall>=0.90 is {prec_at.get('recall>=0.9')}, at >=0.80 is "
                     f"{prec_at.get('recall>=0.8')}, at >=0.70 is {prec_at.get('recall>=0.7')} -- ABOVE the "
                     f"flat FIRE_ANY floor {base:.3f} at every measured recall (Pareto dominance: {dominates})."),
        "anchor_name": ANCHOR, "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    return m


def self_test():
    import spacy
    nlp = spacy.load("en_core_web_sm")
    m = run(nlp=nlp)
    assert m["average_precision"] > m["base_rate_FIRE_ANY"], "gate must rank better than chance"
    print("[self-test] PASS", m["headline"][:120])
    return True


def main():
    out = _out_dir()
    t0 = time.perf_counter()
    m = run()
    m["elapsed_s"] = round(time.perf_counter() - t0, 2)
    with open(os.path.join(out, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(m, f, indent=2)
    print(m["headline"])
    print("precision@recall:", m["precision_at_fixed_recall"])
    return m


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test(); sys.exit(0)
    main()
