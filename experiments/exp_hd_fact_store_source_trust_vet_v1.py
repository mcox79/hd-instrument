"""DEMONSTRATION: HD fact store + source-trust ingest vetting (glass-box, can-fail).

Builds a controlled fact set with DELIBERATELY INJECTED conflicts across trust levels
plus clean (non-conflicting) facts + hard negative distractors, then measures whether the
substrate-native ingest-vet does the RIGHT thing:

  1. CONFLICT-DETECTION      : recall/precision on same-(s,r)-different-o injected conflicts.
  2. TRUST-RESOLUTION correct : REPLACE / COMBINE / FLAG / DROP accuracy on injected cases.
  3. CLEAN FALSE-FLAG rate    : on clean facts + distractors, must be ~0 (the failed
                                condenser-auditor was 0.53 -- this must BEAT it).
  4. GLASS-BOX                : 3-4 worked resolutions with provenance recovered by unbind.

Honest frame: SOURCE-TRUST vetting trusts curation; it does NOT check factual truth.

CELL-TEMPLATE: start-marker + atomic metrics write (tmp+os.replace) +
`except SystemExit: raise` before `except Exception` + determinism guard. This is an
INLINE-LOCAL foreground demonstration (no queue, no seeds-sweep); it runs to completion in
well under a second. ASCII-only.
"""
from __future__ import annotations

import json
import os
import platform
import time
import traceback
from datetime import datetime, timezone

import torch

from hdlab.hd_fact_store import HDFactStore, TRUST_LEVEL, _run_all_selftests

ANCHOR_NAME = "hd_fact_store_source_trust_vet_v1"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "data", f"exp_{ANCHOR_NAME}")
AUDITOR_FALSE_FLAG = 0.53  # CITED@ condenser-auditor HARD_FAIL (false-flag on correct entries)

RELATION_CARDINALITY = {
    "capital_of": "FUNCTIONAL",     # one capital -> two different = contradiction
    "born_in": "FUNCTIONAL",        # one birthplace
    "atomic_number": "FUNCTIONAL",  # one value
    "speaks": "MULTIVALUED",        # many languages, additive
    "member_of": "MULTIVALUED",     # many groups, additive
}


def _write_start_marker() -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": "inline_local", "host": platform.node()}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "_start_marker.json"))


def _atomic_write_metrics(metrics: dict) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))


def _write_crash_metrics(exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _atomic_write_metrics(diag)


# ---- controlled injected fact set --------------------------------------------------
def _build_scenario():
    """Return (prestore, trials). Each trial is a dict with the store() args, the
    ground-truth conflict flag, and the expected resolution. `prestore` are the first
    facts written to set up conflicts; trials include those too (with expectations)."""
    trials = []

    def add(subj, rel, obj, src, trust, gt_conflict, expected):
        trials.append(dict(subject=subj, relation=rel, obj=obj, source=src, trust=trust,
                           gt_conflict=gt_conflict, expected=expected))

    # --- CLEAN facts: unique (s,r), never conflict (expected CLEAN_STORE) ---
    for i in range(40):
        rel = "capital_of" if i % 2 == 0 else "born_in"
        add(f"city{i}", rel, f"country{i}", "book_geo", "TRUST_MID", False, "CLEAN_STORE")

    # --- Hard negative distractors: SAME relation, DIFFERENT subject (NOT a conflict) ---
    for i in range(20):
        add(f"person{i}", "born_in", "shared_town", "book_bio", "TRUST_MID", False, "CLEAN_STORE")

    # --- Hard negative distractors: SAME subject, DIFFERENT relation (NOT a conflict) ---
    for i in range(20):
        # person{i} already has born_in; add a different relation for same subject
        add(f"person{i}", "member_of", f"club{i}", "book_bio", "TRUST_MID", False, "CLEAN_STORE")

    # --- REPLACE cases: mid stored, then HIGH new, same (s,r), diff obj ---
    for i in range(10):
        add(f"elem{i}", "atomic_number", f"wrong{i}", "old_article", "TRUST_MID", False, "CLEAN_STORE")
        add(f"elem{i}", "atomic_number", f"right{i}", "chem_textbook", "TRUST_HIGH", True, "REPLACE")

    # --- DROP cases: HIGH stored, then LOW new ---
    for i in range(10):
        add(f"star{i}", "born_in", f"real{i}", "astro_textbook", "TRUST_HIGH", False, "CLEAN_STORE")
        add(f"star{i}", "born_in", f"rumor{i}", "random_blog", "TRUST_LOW", True, "DROP")

    # --- FLAG cases: equal-trust, FUNCTIONAL relation, contradictory objects ---
    for i in range(10):
        add(f"town{i}", "capital_of", f"claimA{i}", "article_A", "TRUST_MID", False, "CLEAN_STORE")
        add(f"town{i}", "capital_of", f"claimB{i}", "article_B", "TRUST_MID", True, "FLAG")

    # --- COMBINE cases: equal-trust, MULTIVALUED relation, additive objects ---
    for i in range(10):
        add(f"poly{i}", "speaks", f"langA{i}", "survey_A", "TRUST_MID", False, "CLEAN_STORE")
        add(f"poly{i}", "speaks", f"langB{i}", "survey_B", "TRUST_MID", True, "COMBINE")

    return trials


def _run_measurement(seed: int) -> dict:
    st = HDFactStore(n_dim=8192, seed=seed, relation_cardinality=RELATION_CARDINALITY,
                     sr_threshold=0.75)
    trials = _build_scenario()

    # confusion for detection (over ALL store ops), resolution correctness, false-flag
    tp = fp = tn = fn = 0
    res_correct = 0
    res_total = 0
    clean_total = 0
    clean_flagged = 0
    roundtrip_ok = 0
    roundtrip_total = 0
    worked = []  # glass-box worked examples

    for t in trials:
        r = st.store(t["subject"], t["relation"], t["obj"], t["source"], t["trust"])
        gt = t["gt_conflict"]
        det = r.detected_conflict
        if gt and det:
            tp += 1
        elif gt and not det:
            fn += 1
        elif (not gt) and det:
            fp += 1
        else:
            tn += 1
        if not gt:
            clean_total += 1
            if det:
                clean_flagged += 1
        if gt:
            res_total += 1
            if r.resolution == t["expected"]:
                res_correct += 1

        # glass-box round-trip: recover the just-stored fact from HD, compare
        rec = st.recover_fact(st._facts[r.fid].vec)
        roundtrip_total += 1
        if (rec["subject"] == t["subject"] and rec["relation"] == t["relation"]
                and rec["object"] == t["obj"] and rec["source"] == t["source"]
                and rec["trust"] == t["trust"]):
            roundtrip_ok += 1

        # capture one worked example per resolution type
        if r.detected_conflict and r.resolution in ("REPLACE", "FLAG", "COMBINE", "DROP") \
                and not any(w["resolution"] == r.resolution for w in worked):
            worked.append({
                "resolution": r.resolution,
                "new_fact": f"({t['subject']}, {t['relation']}, {t['obj']})",
                "new_source": t["source"], "new_trust": t["trust"],
                "new_trust_level": r.new_trust, "stored_trust_level": r.stored_trust,
                "conflict_recovered_objs": r.conflict_objs,  # recovered by unbind (glass-box)
                "recovered_provenance": {"source": rec["source"], "trust": rec["trust"]},
                "note": r.note,
            })

    detection_precision = tp / (tp + fp) if (tp + fp) else 1.0
    detection_recall = tp / (tp + fn) if (tp + fn) else 1.0
    clean_false_flag_rate = clean_flagged / clean_total if clean_total else 0.0
    resolution_accuracy = res_correct / res_total if res_total else 0.0
    roundtrip_acc = roundtrip_ok / roundtrip_total if roundtrip_total else 0.0

    return {
        "n_trials": len(trials),
        "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "detection_precision": detection_precision,
        "detection_recall": detection_recall,
        "resolution_accuracy": resolution_accuracy,
        "resolution_correct": res_correct, "resolution_total": res_total,
        "clean_total": clean_total, "clean_flagged": clean_flagged,
        "clean_false_flag_rate": clean_false_flag_rate,
        "glassbox_roundtrip_acc": roundtrip_acc,
        "worked_examples": worked,
        "n_live_facts": len(st.live_facts()),
    }


def main() -> None:
    t0 = time.perf_counter()
    _write_start_marker()

    # formula self-test (module) first
    selftest = _run_all_selftests()

    # determinism guard: two independent runs must be bit-identical on all scalar metrics
    m1 = _run_measurement(seed=7)
    m2 = _run_measurement(seed=7)
    det_keys = ["detection_precision", "detection_recall", "resolution_accuracy",
                "clean_false_flag_rate", "glassbox_roundtrip_acc"]
    deterministic = all(abs(m1[k] - m2[k]) < 1e-12 for k in det_keys) and \
        m1["confusion"] == m2["confusion"]

    # PASS bands (pre-registered here inline):
    #   detection_recall    >= 0.98   (find the injected conflicts)
    #   detection_precision >= 0.98   (do not over-detect)
    #   resolution_accuracy >= 0.98   (right REPLACE/COMBINE/FLAG/DROP action)
    #   clean_false_flag_rate <= 0.02 (must BEAT the auditor's 0.53)
    #   glassbox_roundtrip_acc>= 0.99 (facts recover from HD by unbind)
    # FAIL band = any metric on the wrong side.
    passes = (m1["detection_recall"] >= 0.98 and m1["detection_precision"] >= 0.98 and
              m1["resolution_accuracy"] >= 0.98 and m1["clean_false_flag_rate"] <= 0.02 and
              m1["glassbox_roundtrip_acc"] >= 0.99 and deterministic)
    verdict = "PASS" if passes else "FAIL"

    beats_auditor = m1["clean_false_flag_rate"] < AUDITOR_FALSE_FLAG

    metrics = {
        "verdict": verdict,
        "verdict_msg": (f"detect P/R={m1['detection_precision']:.3f}/{m1['detection_recall']:.3f} "
                        f"res_acc={m1['resolution_accuracy']:.3f} "
                        f"clean_false_flag={m1['clean_false_flag_rate']:.3f} "
                        f"(auditor={AUDITOR_FALSE_FLAG}) roundtrip={m1['glassbox_roundtrip_acc']:.3f} "
                        f"determ={deterministic}"),
        "summary": f"HD fact store source-trust vet: {verdict}",
        "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "n_dim": 8192,
        "deterministic": deterministic,
        "beats_condenser_auditor": beats_auditor,
        "auditor_false_flag_reference": AUDITOR_FALSE_FLAG,
        "selftest": selftest,
        "metrics": m1,
        "trust_ladder": TRUST_LEVEL,
        "relation_cardinality": RELATION_CARDINALITY,
        "honest_frame": ("SOURCE-TRUST vetting: trusts curated sources + resolves conflicts "
                         "by trust rank; does NOT verify factual truth (student-model trade)."),
    }
    _atomic_write_metrics(metrics)
    print(f"[{ANCHOR_NAME}] {verdict} :: {metrics['verdict_msg']}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(e)
        raise
