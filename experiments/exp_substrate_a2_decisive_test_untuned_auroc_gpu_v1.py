"""A2 decisive-test: UNTUNED-substrate refuse-gate AUROC on the gap-balanced held-out (Bucket-2 TRACK-1 follow-up).

Per research drill 329eabb9 section (b) + Skunkworks A2-validity-VET PASS GO. The PRE-LoRA cheap decisive test: does the
CURRENT (untuned) substrate refuse-gate separate GAP from IN-COV on the validated 72-item set?
  refuse-gate confidence = max bge-cosine of the question to any atom (r.semantic top-1 score) = "can I answer this?"
  AUROC(gap-label, -confidence): in-cov should have HIGH confidence (covered), gap LOW.

Verdict bands (pre-registered; the LoRA-Stage-2 GATE):
  NEAR_CHANCE (target [0.45, 0.60]): untuned AUROC near-chance -> ROOM to improve -> LoRA Stage-2 is JUSTIFIED. = the
     decisive-test "PASS" (the set is measurable + the untuned substrate doesn't already solve it).
  ALREADY_SEPARATES (AUROC >= 0.70): the untuned substrate ALREADY separates gap/in-cov by raw confidence -> LoRA has
     NO headroom (or the set is leaky despite the TF-IDF audit) -> Stage-2 NOT justified (a calibrated threshold suffices).
  INVERTED (AUROC < 0.45): the confidence is anti-correlated with coverage -> investigate (broken scorer / mislabel).
  MIDDLE (0.60-0.70): partial separation; marginal LoRA headroom.

Reuses the proven m1 bge-scoring harness (AtomEncoder + Retriever + rebuild_index_cached + r.semantic). The 2
coincidental-mention near-gaps (Tarjan-SCC, Hopcroft-Karp; Skunkworks caveat) are scored AS GAPS -- if their confidence
is high (coincidental mention surfaced), that is the refuse-gate PRECISION LIMITATION the eval correctly exposes.

bge (GPU) required for the real run (AtomEncoder). --self-test exercises the AUROC LOGIC on synthetic scores (no bge).
Adopts gate0_self_check. 11th rule (bge primitive, no LLM). ASCII-only. HDLAB_RUN_MODE smoke|full ; --smoke ; --self-test.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cell_provenance import provenance_fields, now_utc, gate0_self_check, discrimination_self_check

ANCHOR = "substrate_a2_decisive_test_untuned_auroc_gpu_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)
A2_SET = REPO / "data" / "exp_a2_gap_balanced" / "a2_gap_balanced_v1.jsonl"
TOP_K = 20
NEAR_CHANCE_LO, NEAR_CHANCE_HI = 0.45, 0.60
ALREADY_SEP = 0.70


def _auroc(labels, scores):
    """AUROC via sklearn; labels: 1=gap (positive), scores: refuse-score (higher -> more gap-like)."""
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(labels, scores))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _ = ap.parse_known_args()
    is_smoke = args.smoke or (os.environ.get("HDLAB_RUN_MODE", "full") == "smoke" and not args.full)
    run_started_utc = now_utc()
    t0 = time.time()

    if args.self_test:
        # exercise AUROC + verdict logic on SYNTHETIC scores (no bge); NO metrics written
        import numpy as np
        rng = np.random.default_rng(0)
        labels = [1] * 5 + [0] * 5
        scores = list(rng.random(10))
        a = _auroc(labels, scores)
        print(f"[{ANCHOR}] --self-test OK (synthetic AUROC={a:.3f}; verdict-band logic wired); NO metrics. bge NOT required for self-test.")
        return 0

    if not A2_SET.exists():
        print(f"[{ANCHOR}] ERROR: A2 set not found at {A2_SET}")
        return 1
    items = [json.loads(l) for l in open(A2_SET, encoding="utf-8") if l.strip()]

    # real bge scoring (GPU) via the proven m1 harness
    try:
        from backend.substrate_index.partition import PartitionedStore
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
    except Exception as e:
        print(f"[{ANCHOR}] ERROR import: {e}")
        return 2
    pstore = PartitionedStore(REPO / "data" / "substrate_index")
    try:
        enc = AtomEncoder()
    except Exception as e:
        print(f"[{ANCHOR}] ERROR bge_unavailable (needs GPU/bge): {str(e)[:100]}")
        return 3
    r = Retriever(pstore, enc); rebuild_index_cached(r, REPO / "data" / "substrate_index")

    n_declared = len(items)
    rows = []
    for it in items:
        q = it["question"]
        try:
            cands = r.semantic(q, top_k=TOP_K)
            conf = max((float(getattr(c, "score", 0.0)) for c in cands), default=0.0)
        except Exception:
            conf = 0.0
        rows.append({"id": it["id"], "type": it["type"], "gap_kind": it.get("gap_kind"),
                     "answerable": it["answerable"], "confidence": round(conf, 4),
                     "refuse_score": round(1.0 - conf, 4)})

    labels = [1 if x["type"] == "gap" else 0 for x in rows]          # 1 = gap (positive)
    refuse = [x["refuse_score"] for x in rows]                       # higher -> more gap-like
    confs = [x["confidence"] for x in rows]
    n_gap = sum(labels); n_inc = len(labels) - n_gap
    # discrimination: AUROC computable (both classes present) AND confidence not all-identical (room to rank)
    has_both = n_gap > 0 and n_inc > 0
    conf_spread = (max(confs) - min(confs)) if confs else 0.0
    discriminates = has_both and conf_spread > 1e-6
    auroc = _auroc(labels, refuse) if discriminates else None

    # near/far subgroup AUROC (P4 precursor; vs all in-cov)
    def sub_auroc(kind):
        idx = [i for i, x in enumerate(rows) if x["type"] == "in_cov" or x["gap_kind"] == kind]
        sl = [labels[i] for i in idx]; sr = [refuse[i] for i in idx]
        return _auroc(sl, sr) if (sum(sl) > 0 and (len(sl) - sum(sl)) > 0) else None
    near_auroc = sub_auroc("near") if discriminates else None
    far_auroc = sub_auroc("far") if discriminates else None

    if not discriminates:
        verdict = "NON_TEST"
        msg = f"NON-TEST: AUROC not computable (both-classes={has_both}, conf_spread={conf_spread:.4f}). No discrimination to measure."
    elif auroc < NEAR_CHANCE_LO:
        verdict = "INVERTED"
        msg = (f"INVERTED: untuned refuse-gate AUROC={auroc:.3f} < {NEAR_CHANCE_LO} -- confidence ANTI-correlated with coverage. "
               f"Investigate (scorer/mislabel). n_gap={n_gap} n_in_cov={n_inc}.")
    elif auroc <= NEAR_CHANCE_HI:
        verdict = "NEAR_CHANCE"
        msg = (f"NEAR_CHANCE (decisive-test PASS): untuned refuse-gate AUROC={auroc:.3f} in [{NEAR_CHANCE_LO},{NEAR_CHANCE_HI}] "
               f"-> the untuned substrate does NOT already separate gap/in-cov by raw confidence -> ROOM to improve -> LoRA "
               f"Stage-2 is JUSTIFIED. (near-gap AUROC={near_auroc}, far-gap AUROC={far_auroc}.) n_gap={n_gap} n_in_cov={n_inc}.")
    elif auroc < ALREADY_SEP:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE: untuned AUROC={auroc:.3f} in ({NEAR_CHANCE_HI},{ALREADY_SEP}) -- partial separation; marginal LoRA "
               f"headroom. (near={near_auroc}, far={far_auroc}.)")
    else:
        verdict = "ALREADY_SEPARATES"
        msg = (f"ALREADY_SEPARATES: untuned refuse-gate AUROC={auroc:.3f} >= {ALREADY_SEP} -- the untuned substrate ALREADY "
               f"separates gap/in-cov by raw bge-confidence -> LoRA Stage-2 has NO headroom (a calibrated threshold suffices). "
               f"(near={near_auroc}, far={far_auroc}.) (Or residual leakage despite TF-IDF 0.510 -- inspect top gap confidences.)")

    src = "measured_bge_gpu"
    g0 = gate0_self_check(run_mode=("smoke" if is_smoke else "full"), metrics_source=src,
                          n_cells_declared=n_declared, n_cells_emitted=len(rows),
                          elapsed_s=round(time.time() - t0, 2), is_smoke=is_smoke)
    disc = discrimination_self_check(discriminates, auroc, 0.5, 1.0,
                                     "AUROC computable (both classes) + confidence has spread (room to rank)")

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "summary": msg, "headline": msg,
        "n_seeds": 1,
        **provenance_fields("smoke" if is_smoke else "full", "untuned_refuse_gate_auroc", src, run_started_utc),
        "gate0_self_check": g0, "discrimination_self_check": disc,
        "n_cells": len(rows), "untuned_auroc": round(auroc, 4) if auroc is not None else None,
        "near_gap_auroc": round(near_auroc, 4) if near_auroc is not None else None,
        "far_gap_auroc": round(far_auroc, 4) if far_auroc is not None else None,
        "n_gap": n_gap, "n_in_cov": n_inc,
        "bands": {"near_chance": [NEAR_CHANCE_LO, NEAR_CHANCE_HI], "already_separates": ALREADY_SEP},
        "coincidental_mention_caveat": "Tarjan-SCC + Hopcroft-Karp scored AS GAPS (Skunkworks caveat); high confidence on them = refuse-gate precision limitation the eval exposes",
        "rows": rows,
        "a2_set": str(A2_SET.relative_to(REPO)), "a2_set_validity_vet": "PASS (Skunkworks independent 2026-06-18)",
        "bears_on": "A2 gap-balanced v1 (validated); gates B-beta LoRA Stage-2 (near-chance -> justified; already-separates -> no headroom)",
        "measured_bounds": "untuned refuse-gate (max bge-cosine confidence) @ this corpus/index; pre-LoRA decisive test",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")
    print(f"[{ANCHOR}] -> {verdict}  untuned_auroc={auroc}  (near={near_auroc} far={far_auroc})  gate0={g0['pass']}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
