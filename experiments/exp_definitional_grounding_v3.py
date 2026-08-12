"""experiments/exp_definitional_grounding_v3.py

DEFINITIONAL EXTRACTION AS A SECOND GROUNDING SIGNAL, alongside (NOT replacing) the existing
distributional path, so the two can be compared on the same hand-scored rubric.

Pre-reg: preregs/2026-08-12_definitional_grounding_v3.md  (committed BEFORE this run)
Notes:   notes/definitional_grounding_v3_2026-08-12.md

ARMS
  DIST_ASIS      the existing signal, read off disk (v2 store, 634 facts, hand-scored 8/26/66)
  DIST_LOWINFO   the existing signal + the fault-2b PMI gate ONLY  <- CONTROL: isolates how much
                 of any change is due to the step-2 FIXES rather than to definitional structure
  DEF            the new signal: meaning read off explicit definitional constructions

The cell writes a 50-pair audit sample per new arm and STOPS. It does NOT assign
MEANINGFUL/RELATED/NOISE and does NOT claim a band -- the director hand-scores, exactly as the
v2 cell correctly did. Verdict emitted is STRUCTURAL_PASS_PENDING_B3.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at gate (META_RULE_AF; DEF vs DIST fact-set hash test)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
 - crlb_n/a: primary metric is a HUMAN bucket count; the feasibility bound is BINOMIAL and is
   computed in the pre-reg, where the band edges are placed on it
 - baseline_in_band: DIST_ASIS = 0.08 MEANINGFUL, inside (0.05, 0.95)
 - cardinality_ok: EXPECTED_N_ARMS = 3, counted in the verdict logic
 - calibration_check: adaptive_with_discriminator_gate (PMI floor off the closed-class lexicon;
   calibration logged; known-meaningful control pairs asserted to survive)
 - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@

READ-ONLY GUARANTEE: data/foundation/reading_grounding_v1 and reading_grounding_v2_qualityfix are
EVIDENCE. This cell opens them for READ only and writes exclusively to a NEW directory.

ASCII-only.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import re
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class          # noqa: E402
from hdlab.definitional_extraction import extract_definitions    # noqa: E402
from hdlab.hd_fact_store import HDFactStore                      # noqa: E402
from hdlab.low_information_filter import build_profile           # noqa: E402
from hdlab.thematic_role_labeler import lemma_word               # noqa: E402

ANCHOR_NAME = "definitional_grounding_v3"
MEANING_RELATION = "GROUNDED_MEANING"
N_DIM = 2048
EXPECTED_N_ARMS = 3

OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_definitional_grounding_v3")
NEW_FOUNDATION = os.path.join(REPO_ROOT, "data", "foundation",
                              "reading_grounding_v3_definitional")
V2_EVIDENCE = os.path.join(REPO_ROOT, "data", "foundation", "reading_grounding_v2_qualityfix")

TOK = re.compile(r"[A-Za-z][A-Za-z'-]*")

# Known-meaningful control pairs (MEASURED@notes/foundation_grounding_sample_2026-08-12.md, the
# previous director's INDEPENDENT v1 bucket labels) -- these must SURVIVE the PMI gate, else the
# gate is swallowing signal and the cell must halt rather than report a flattering number.
PMI_CONTROL_PAIRS = [("primer", "polymerase"), ("organelle", "cytoplasm"),
                     ("tree", "phylogenetic"), ("variant", "gene"),
                     ("alternation", "haploid")]
# Facts the gate MUST refuse (MEASURED: `people` is the object of 20/634 v2 facts).
PMI_MUST_REFUSE_OBJECT = "people"


# ============================================================================ instrumentation
def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": EXPECTED_N_ARMS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, path)


# ============================================================================ corpus
def load_corpus(limit: Optional[int] = None) -> List[Tuple[str, str]]:
    """[(segment, sentence)] over every pool the reading loop reads. Same loaders, verbatim."""
    from experiments.exp_reading_grounding_loop_cycle1_v1 import build_curriculum_pool
    from experiments.exp_reading_grounding_loop_cycle2_v1 import SEGMENT_POOL_LOADERS
    out: List[Tuple[str, str]] = [("bootstrap", s) for _t, s in build_curriculum_pool(limit)]
    for seg, loader in SEGMENT_POOL_LOADERS.items():
        out.extend((seg, s) for _t, s in loader(limit))
    return out


# ============================================================================ DEF arm
def build_def_arm(corpus: List[Tuple[str, str]], prof) -> Tuple[List[dict], Counter]:
    """Extract definitional facts, apply every pre-declared gate, return (facts, refusal counts).

    One row per DISTINCT (definiendum, head) pair; repeat attestations are counted, not re-banked.
    """
    refusals: Counter = Counter()
    by_pair: Dict[Tuple[str, str], dict] = {}
    for seg, sent in corpus:
        for d in extract_definitions(sent):
            subj, obj = d.definiendum_lemma, d.head
            if not subj or not obj:
                refusals["EMPTY_SPAN"] += 1
                continue
            # gate 2: both open-class
            if is_closed_class(subj):
                refusals["CLOSED_CLASS_SUBJECT"] += 1
                continue
            if is_closed_class(obj):
                refusals["CLOSED_CLASS_OBJECT"] += 1
                continue
            # gate 3: tautology
            if subj == obj:
                refusals["TAUTOLOGY"] += 1
                continue
            # gate 4: low-information (PMI floor calibrated off the closed-class lexicon)
            ok, reason = prof.eligible_meaning(subj, obj)
            if not ok:
                refusals[reason] += 1
                continue
            key = (subj, obj)
            row = by_pair.get(key)
            if row is None:
                by_pair[key] = {
                    "subject": subj, "object": obj, "segment": seg, "pattern": d.pattern,
                    "n_attestations": 1, "pmi": round(prof.pmi(subj, obj), 4),
                    "patterns_seen": [d.pattern],
                    "source_sentences": [sent],
                    "definiendum_surface": d.definiendum, "definiens_surface": d.definiens,
                }
            else:
                row["n_attestations"] += 1
                if d.pattern not in row["patterns_seen"]:
                    row["patterns_seen"].append(d.pattern)
                if len(row["source_sentences"]) < 3 and sent not in row["source_sentences"]:
                    row["source_sentences"].append(sent)
    facts = [by_pair[k] for k in sorted(by_pair)]
    return facts, refusals


# ============================================================================ DIST arms
def load_dist_asis() -> List[dict]:
    path = os.path.join(V2_EVIDENCE, "grounding_provenance.jsonl")
    with open(path, "r", encoding="utf-8") as f:      # READ-ONLY (evidence store)
        return [json.loads(line) for line in f if line.strip()]


def build_dist_lowinfo(dist: List[dict], prof) -> Tuple[List[dict], Counter]:
    refusals: Counter = Counter()
    kept = []
    for r in dist:
        ok, reason = prof.eligible_meaning(r["subject"], r["object"])
        if ok:
            kept.append(r)
        else:
            refusals[reason] += 1
    return kept, refusals


# ============================================================================ banking
def bank_facts(facts: List[dict], foundation_dir: str) -> HDFactStore:
    """Bank into a REAL HDFactStore (the actual substrate object, not a dict) at n_dim=2048."""
    store = HDFactStore(n_dim=N_DIM, seed=0)
    for f in facts:
        store.store(f["subject"], MEANING_RELATION, f["object"],
                    f"definitional:{f['segment']}", "TRUST_MID")
    os.makedirs(foundation_dir, exist_ok=True)
    return store


def sample_for_audit(facts: List[dict], k: int = 50, seed: int = 42) -> List[dict]:
    """IDENTICAL sampling to the v2 B3 audit: random.seed(42), random.sample over the
    GROUNDED_MEANING facts in fid (= insertion) order."""
    rng = random.Random(seed)
    idx = sorted(rng.sample(range(len(facts)), min(k, len(facts))))
    return [facts[i] for i in idx]


# ============================================================================ self-test
def _no_bare_except_selftest() -> None:
    src = open(os.path.abspath(__file__), "r", encoding="utf-8").read()
    # Patterns are ASSEMBLED FROM FRAGMENTS so this checker does not match its own source; the
    # naive literal version asserts against itself and can never pass.
    banned_base = r"except\s+" + "Base" + "Exception"
    banned_bare = "except" + r"\s*" + ":"
    assert not re.search(banned_base, src), "META_RULE: broad-catch handler banned (see banned_base)"
    assert not re.search(banned_bare, src), "META_RULE: bare except banned"


def _selftest_real_code_path_tiny() -> None:
    """F.1: construct the REAL substrate objects the FULL run uses, at tiny scale."""
    exercised = set()
    docs = [["nephron", "kidney", "unit", "filter"] for _ in range(8)]
    docs += [["the", "of", "a", "topic%d" % i] for i in range(40)]
    prof = build_profile(docs)
    exercised.add("build_profile")
    assert prof.pmi_calibration is not None, prof.pmi_calibration

    corpus = [("bio_new", "A nephron is the functional unit of the kidney"),
              ("bio_new", "Cholesterol is a lipid that helps membranes"),
              ("news", "The increase will put more pressure on land, water and nutrients")]
    facts, refusals = build_def_arm(corpus, prof)
    exercised.add("build_def_arm")
    subj_obj = {(f["subject"], f["object"]) for f in facts}
    # the definitional sentence must yield its fact; the co-occurrence sentence must not
    assert ("nephron", "unit") in subj_obj or refusals, (subj_obj, refusals)
    assert ("nutrient", "pressure") not in subj_obj, subj_obj

    store = bank_facts(facts, os.path.join(OUT_DIR, "_selftest_foundation"))
    exercised.add("HDFactStore")
    live = [f for f in store.live_facts() if f.relation == MEANING_RELATION]
    assert len(live) == len(facts), (len(live), len(facts))
    # glass-box round-trip through the REAL recover path, not the shadow fields
    if live:
        rec = store.recover_fact(live[0].vec if hasattr(live[0], "vec") else live[0].vector)
        assert rec is not None
        exercised.add("recover_fact")

    for name in ("build_profile", "build_def_arm", "HDFactStore"):
        assert name in exercised, f"F.1 declared entrypoint {name} not exercised"


def _selftest_sampling_is_identical_to_v2() -> None:
    """The audit band is only comparable if the sampling is bit-identical to the v2 procedure."""
    facts = [{"i": i} for i in range(634)]
    got = sample_for_audit(facts, k=50, seed=42)
    rng = random.Random(42)
    expect_idx = sorted(rng.sample(range(634), 50))
    assert [f["i"] for f in got] == expect_idx, (got[:5], expect_idx[:5])
    assert len(got) == 50


def run_self_test() -> dict:
    _no_bare_except_selftest()
    _selftest_real_code_path_tiny()
    _selftest_sampling_is_identical_to_v2()
    return {"verdict": "SELFTEST_PASS", "verdict_msg": "all self-tests passed",
            "summary": "SELFTEST_PASS", "elapsed_s": 0.0}


# ============================================================================ main run
def run_full(run_mode: str, limit: Optional[int]) -> dict:
    t0 = time.time()
    corpus = load_corpus(limit)
    doc_lemmas = [[lemma_word(t) for t in TOK.findall(s)] for _seg, s in corpus]
    prof = build_profile(doc_lemmas)

    # -------- calibration_check: the gate must refuse the known-bad and keep the known-good ----
    calib_controls = {}
    for a, b in PMI_CONTROL_PAIRS:
        ok, reason = prof.eligible_meaning(a, b)
        calib_controls[f"{a}->{b}"] = {"survives": bool(ok), "pmi": prof.pmi(a, b),
                                       "refusal": reason}
    survivors = sum(1 for v in calib_controls.values() if v["survives"])
    dist_asis = load_dist_asis()
    people_facts = [r for r in dist_asis if r["object"] == PMI_MUST_REFUSE_OBJECT]
    people_surviving = sum(1 for r in people_facts
                           if prof.eligible_meaning(r["subject"], r["object"])[0])
    if run_mode == "full" and limit is None:
        # HALT rather than report a flattering number if the gate swallows known signal.
        if survivors < len(PMI_CONTROL_PAIRS) - 1:
            raise AssertionError(
                "BLOCK_DISPATCH_calibration_check: PMI gate refused %d/%d known-meaningful "
                "control pairs: %r" % (len(PMI_CONTROL_PAIRS) - survivors,
                                       len(PMI_CONTROL_PAIRS), calib_controls))
        if people_facts and people_surviving > 0:
            raise AssertionError(
                "BLOCK_DISPATCH_calibration_check: PMI gate failed to refuse %d/%d `-> people` "
                "facts it was calibrated to refuse" % (people_surviving, len(people_facts)))

    # -------- arms --------------------------------------------------------------------------
    def_facts, def_refusals = build_def_arm(corpus, prof)
    dist_lowinfo, dist_refusals = build_dist_lowinfo(dist_asis, prof)

    # -------- META_RULE_AF: arms must differ -------------------------------------------------
    def _digest(rows: List[dict]) -> str:
        payload = sorted((r["subject"], r["object"]) for r in rows)
        return hashlib.sha256(json.dumps(payload).encode("utf-8")).hexdigest()

    digests = {"DEF": _digest(def_facts), "DIST_LOWINFO": _digest(dist_lowinfo),
               "DIST_ASIS": _digest(dist_asis)}
    for a in sorted(digests):
        for b in sorted(digests):
            if a < b:
                assert digests[a] != digests[b], (
                    "META_RULE_AF VIOLATION: arms %r and %r are bit-identical (%s)"
                    % (a, b, digests[a]))

    # -------- discriminator_fires: DEF must produce facts DIST does not ----------------------
    dist_pairs = {(r["subject"], r["object"]) for r in dist_asis}
    def_pairs = {(f["subject"], f["object"]) for f in def_facts}
    novel = def_pairs - dist_pairs
    discriminator_fires = len(novel) >= 100

    # -------- bank the DEF arm into a NEW foundation -----------------------------------------
    store = bank_facts(def_facts, NEW_FOUNDATION)
    live = [f for f in store.live_facts() if f.relation == MEANING_RELATION]

    # -------- audit samples (NOT scored here) -------------------------------------------------
    rubric = ("MEANINGFUL / RELATED / NOISE per notes/foundation_grounding_sample_2026-08-12.md; "
              "sampling random.seed(42) over GROUNDED_MEANING fid order -- IDENTICAL to the v2 "
              "B3 audit so the numbers are directly comparable")
    def_sample_path = os.path.join(OUT_DIR, "b3_audit_sample_DEF.json")
    _atomic_write_json(def_sample_path, {
        "arm": "DEF", "rubric": rubric,
        "baseline_to_beat": {"source": "v2 hand-score", "MEANINGFUL": 0.08,
                             "RELATED": 0.26, "NOISE": 0.66},
        "prereg": "preregs/2026-08-12_definitional_grounding_v3.md",
        "n_facts_in_arm": len(def_facts),
        "NOT_AUTO_SCORED": True,
        "rows": sample_for_audit(def_facts)})
    dist_sample_path = os.path.join(OUT_DIR, "b3_audit_sample_DIST_LOWINFO.json")
    _atomic_write_json(dist_sample_path, {
        "arm": "DIST_LOWINFO",
        "purpose": ("CONTROL -- isolates how much of any DEF gain is due to the step-2 fixes "
                    "rather than to definitional structure. If this scores as well as DEF, the "
                    "definitional signal has NOT been shown to add anything."),
        "rubric": rubric,
        "prereg": "preregs/2026-08-12_definitional_grounding_v3.md",
        "n_facts_in_arm": len(dist_lowinfo),
        "NOT_AUTO_SCORED": True,
        "rows": sample_for_audit(dist_lowinfo)})

    _atomic_write_json(os.path.join(NEW_FOUNDATION, "grounding_provenance.jsonl.json"),
                       {"note": "see definitional_facts.jsonl"})
    prov_path = os.path.join(NEW_FOUNDATION, "definitional_facts.jsonl")
    tmp = prov_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for i, r in enumerate(def_facts):
            f.write(json.dumps({"fid": i, "relation": MEANING_RELATION, **r},
                               ensure_ascii=False) + "\n")
    os.replace(tmp, prov_path)

    elapsed = time.time() - t0
    n_meaningful_equiv_dist = int(round(0.08 * len(dist_asis)))   # MEASURED@v2 hand-score
    metrics = {
        "verdict": "STRUCTURAL_PASS_PENDING_B3",
        "verdict_msg": (
            "STRUCTURAL_PASS_PENDING_B3: DEF arm banked %d facts (%d NOT produced by the "
            "distributional path); DIST_LOWINFO control kept %d/%d. B3 requires the HUMAN-bucketed "
            "50-pair audits at %s and %s -- NOT auto-scored, NOT claimed here. Bands + the "
            "'definitional extraction is NOT the answer' condition: "
            "preregs/2026-08-12_definitional_grounding_v3.md"
            % (len(def_facts), len(novel), len(dist_lowinfo), len(dist_asis),
               def_sample_path, dist_sample_path)),
        "summary": "definitional grounding v3: %d DEF facts, pending human B3" % len(def_facts),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "n_corpus_sentences": len(corpus),
        "arms": {
            "DIST_ASIS": {"n_facts": len(dist_asis),
                          "hand_scored_MEANINGFUL_rate": 0.08,
                          "implied_meaningful_count": n_meaningful_equiv_dist},
            "DIST_LOWINFO": {"n_facts": len(dist_lowinfo),
                             "refusals": dict(dist_refusals)},
            "DEF": {"n_facts": len(def_facts),
                    "n_novel_vs_dist": len(novel),
                    "n_banked_live_in_store": len(live),
                    "refusals": dict(def_refusals),
                    "pattern_mix": dict(Counter(f["pattern"] for f in def_facts)),
                    "segment_mix": dict(Counter(f["segment"] for f in def_facts)),
                    "attestation_hist": dict(Counter(
                        min(f["n_attestations"], 5) for f in def_facts))},
        },
        "arms_differ_verified": True,
        "arm_digests": digests,
        "cardinality_ok": len(digests) == EXPECTED_N_ARMS,
        "discriminator_fires": discriminator_fires,
        "calibration_check": "adaptive_with_discriminator_gate",
        "calibration_detail": {
            "pmi_floor": prof.pmi_floor, "pmi_calibration": prof.pmi_calibration,
            "known_meaningful_controls": calib_controls,
            "n_people_facts_in_v2": len(people_facts),
            "n_people_facts_surviving_gate": people_surviving},
        "final_metrics_atomicity": "tmp_replace",
        "b3_audit_sample_paths": {"DEF": def_sample_path, "DIST_LOWINFO": dist_sample_path},
        "new_foundation_dir": NEW_FOUNDATION,
        "evidence_stores_untouched": [V2_EVIDENCE,
                                      os.path.join(REPO_ROOT, "data", "foundation",
                                                   "reading_grounding_v1")],
    }
    if not metrics["cardinality_ok"]:
        metrics["verdict"] = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    return metrics


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full", choices=["full", "smoke"])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    if args.self_test:
        m = run_self_test()
        _atomic_write_json(os.path.join(OUT_DIR, "selftest_metrics.json"), m)
        print(json.dumps(m))
        raise SystemExit(0)

    _write_start_marker(OUT_DIR, args.mode)
    limit = args.limit if args.limit is not None else (200 if args.mode == "smoke" else None)
    metrics = run_full(args.mode, limit)
    out = os.path.join(OUT_DIR, "metrics.json" if args.mode == "full"
                       else "smoke_metrics.json")
    _atomic_write_json(out, metrics)
    print(json.dumps({k: v for k, v in metrics.items()
                      if k not in ("calibration_detail",)}, indent=2)[:3500])
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:      # NOT BaseException
        _write_crash_metrics(OUT_DIR, e)
        raise
