"""exp_definitional_grounding_v4 -- PARSE-FAULT REPAIR of the v3 definitional fact set.

Pre-reg: preregs/2026-08-12_definitional_parse_faults_v4.md (committed BEFORE this run).
Fault frequencies: notes/definitional_parse_faults_v4_2026-08-12.md (measured over ALL 1751).

WHAT CHANGES vs v3: NOTHING except the parser. Same corpus, same loaders, same closed-class
gate, same PMI floor, same n_dim, same seed-42 sampling. The six fixes live in
hdlab/definitional_extraction.py (commits 00e240710 / a280d9cf4 / 3985e573b) and each has a
named regression test on a REAL v3 row.

The one schema change is load-bearing and is declared in the pre-reg: the subject is now the
FULL TERM (`transcription bubble`), with the old single-lemma key kept alongside as
`subject_head_lemma`, and `subject_type` in {COMMON, PROPER}. PROPER keys keep their case, so a
surname can never fold onto a common noun.

NOT SCORED HERE. The cell writes an UNSCORED 50-row sample and claims no quality band.
Yield counts ARE auto-reported: they are counts, not judgements.

CELL-TEMPLATE MANDATORY:
 - final_metrics_atomicity: tmp_replace
 - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
 - start marker + crash metrics; heartbeat n/a (single ~40s pass)
 - crlb_n/a: deterministic symbolic extraction, no estimator noise floor
 - arms_differ_verified: v3 and v4 fact sets are sha256-compared; identical => BLOCK
 - cardinality n/a: no seed/sweep axis
ASCII-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class            # noqa: E402
from hdlab.definitional_extraction import extract_definitions      # noqa: E402
from hdlab.hd_fact_store import HDFactStore                        # noqa: E402
from hdlab.low_information_filter import build_profile             # noqa: E402
from hdlab.thematic_role_labeler import lemma_word                 # noqa: E402
from experiments.exp_definitional_grounding_v3 import (             # noqa: E402
    load_corpus, sample_for_audit, PMI_CONTROL_PAIRS, TOK)


def build_profile_for(corpus):
    """IDENTICAL profile construction to v3 (doc_lemmas, one document per sentence) so the PMI
    floor calibration is unchanged and the only moving part is the parser."""
    return build_profile([[lemma_word(t) for t in TOK.findall(s)] for _seg, s in corpus])

ANCHOR_NAME = "definitional_grounding_v4"
MEANING_RELATION = "GROUNDED_MEANING"
N_DIM = 2048
MAX_SOURCE_SENTENCES = 10          # v3 capped at 3; pure evidence retention (see pre-reg)

OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_definitional_grounding_v4")
NEW_FOUNDATION = os.path.join(REPO_ROOT, "data", "foundation",
                              "reading_grounding_v4_parsefix")
V3_FACTS = os.path.join(REPO_ROOT, "data", "foundation", "reading_grounding_v3_definitional",
                        "definitional_facts.jsonl")

# Rows that MUST survive the repair. A precision fix that also kills known-good facts is not a
# win (pre-reg failure condition HARD_FAIL_CONTROL_ROWS). (subject, object) at v4 keys.
CONTROL_ROWS_MUST_SURVIVE = [
    ("aorta", "artery"), ("cholesterol", "lipid"), ("arthropoda", "phylum"),
    ("Piraeus", "port"), ("Drosophila", "fly"), ("arteriole", "vessel"),
]
# Rows the repair MUST remove (each was hand-scored NOISE / RELATED by the director).
FAULT_ROWS_MUST_DIE = [
    ("fan", "expert"), ("technology", "seller"), ("kidney", "ureter"),
    ("system", "locomotion"), ("structure", "function"), ("dialysis", "medical"),
    ("kidney", "pair"), ("bubble", "region"), ("effect", "magnification"),
]


def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_write_json(os.path.join(output_dir, "metrics.json"), {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
        "summary": "CELL_CRASHED", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME})


# ============================================================================ DEF v4 arm
def build_def_v4(corpus: List[Tuple[str, str]], prof) -> Tuple[List[dict], Counter]:
    """One row per DISTINCT (term, head). Gates are v3's, applied at the HEAD LEMMA so the PMI
    calibration is unchanged; the TERM is what gets stored."""
    refusals: Counter = Counter()
    by_pair: Dict[Tuple[str, str], dict] = {}
    for seg, sent in corpus:
        for d in extract_definitions(sent):
            term, obj, head_lemma = d.term, d.head, d.definiendum_lemma
            if not term or not obj or not head_lemma:
                refusals["EMPTY_SPAN"] += 1
                continue
            if is_closed_class(head_lemma):
                refusals["CLOSED_CLASS_SUBJECT"] += 1
                continue
            if is_closed_class(obj):
                refusals["CLOSED_CLASS_OBJECT"] += 1
                continue
            if head_lemma == obj or term.lower() == obj:
                refusals["TAUTOLOGY"] += 1
                continue
            ok, reason = prof.eligible_meaning(head_lemma, obj)
            if not ok:
                refusals[reason] += 1
                continue
            key = (term, obj)
            row = by_pair.get(key)
            if row is None:
                by_pair[key] = {
                    "subject": term, "object": obj, "subject_type": d.term_type,
                    "subject_head_lemma": head_lemma,
                    "segment": seg, "pattern": d.pattern, "n_attestations": 1,
                    "pmi": round(prof.pmi(head_lemma, obj), 4),
                    "patterns_seen": [d.pattern], "source_sentences": [sent],
                    "definiendum_surface": d.definiendum, "definiens_surface": d.definiens,
                }
            else:
                row["n_attestations"] += 1
                if d.pattern not in row["patterns_seen"]:
                    row["patterns_seen"].append(d.pattern)
                if (len(row["source_sentences"]) < MAX_SOURCE_SENTENCES
                        and sent not in row["source_sentences"]):
                    row["source_sentences"].append(sent)
    facts = [by_pair[k] for k in sorted(by_pair)]
    for i, f in enumerate(facts):
        f["fid"] = i
        f["relation"] = MEANING_RELATION
    return facts, refusals


def multisense_yield(rows: List[dict]) -> dict:
    by_subj = defaultdict(set)
    for r in rows:
        by_subj[r["subject"]].add(r["object"])
    multi = {s for s, o in by_subj.items() if len(o) > 1}
    in_multi = [r for r in rows if r["subject"] in multi]
    per_word = defaultdict(list)
    for r in in_multi:
        per_word[r["subject"]].append(len(r.get("source_sentences") or []))
    return {
        "n_facts": len(rows),
        "n_distinct_subjects": len(by_subj),
        "n_multi_sense_words": len(multi),
        "n_facts_in_multi_sense_words": len(in_multi),
        "n_senses_with_gt1_source_sentence": sum(
            1 for r in in_multi if len(r.get("source_sentences") or []) > 1),
        "n_multi_sense_words_with_ANY_sense_gt1_sentence": sum(
            1 for v in per_word.values() if any(x > 1 for x in v)),
        "n_multi_sense_words_with_ALL_senses_gt1_sentence": sum(
            1 for v in per_word.values() if all(x > 1 for x in v)),
        "sentence_count_dist_in_multi_sense": dict(sorted(Counter(
            len(r.get("source_sentences") or []) for r in in_multi).items())),
    }


def _digest(rows: List[dict]) -> str:
    h = hashlib.sha256()
    for r in rows:
        h.update(("%s|%s\n" % (r["subject"], r["object"])).encode("utf-8"))
    return h.hexdigest()


# ============================================================================ self-test
def _selftest_sampling_is_identical_to_v3() -> None:
    """Seed-42 sampling must be BIT-IDENTICAL to the v2/v3 B3 procedure, else the director's
    38% baseline is not comparable (pre-reg HARD_FAIL_SAMPLING_DRIFT)."""
    facts = [{"subject": "s%d" % i, "object": "o%d" % i} for i in range(634)]
    got = sample_for_audit(facts, k=50, seed=42)
    rng = random.Random(42)
    expect = sorted(rng.sample(range(634), 50))
    assert [f["subject"] for f in got] == ["s%d" % i for i in expect], "SAMPLING DRIFT"


def _selftest_real_code_path_tiny() -> dict:
    """Exercise the REAL objects the FULL run uses (extractor, profile, HDFactStore) at N~6."""
    corpus = [("bio_new", "A nephron is the functional unit of the kidney"),
              ("bio_new", "The region of unwinding is called a transcription bubble"),
              ("bio_new", "The kidneys are a pair of bean-shaped structures in the body"),
              ("bio_new", "These unused structures without function are called vestigial "
                          "structures"),
              ("bootstrap", "I would dock in Piraeus, the port in Athens, take my pay"),
              ("bootstrap", "Dialysis is a medical process of removing wastes from the blood")]
    prof = build_profile_for(corpus * 6)
    facts, refusals = build_def_v4(corpus, prof)
    pairs = {(f["subject"], f["object"]) for f in facts}
    assert ("transcription bubble", "region") in pairs, pairs
    assert ("Piraeus", "port") in pairs, pairs
    assert not any(s == "bubble" for s, _o in pairs), pairs
    assert ("structure", "function") not in pairs, pairs
    assert ("kidney", "pair") not in pairs, pairs
    assert all(f["subject_type"] in ("COMMON", "PROPER") for f in facts)
    store = HDFactStore(n_dim=N_DIM, seed=0)
    for f in facts:
        store.store(f["subject"], MEANING_RELATION, f["object"], "definitional:selftest",
                    "TRUST_MID")
    assert len(store.live_facts()) == len(facts), (len(store.live_facts()), len(facts))
    return {"n_selftest_facts": len(facts), "pairs": sorted("%s|%s" % p for p in pairs),
            "refusals": dict(refusals)}


def run_self_test() -> dict:
    t0 = time.perf_counter()
    _selftest_sampling_is_identical_to_v3()
    tiny = _selftest_real_code_path_tiny()
    return {"verdict": "SELFTEST_PASS", "verdict_msg": "sampling identical + real code path",
            "summary": "selftest", "elapsed_s": round(time.perf_counter() - t0, 2),
            "tiny": tiny}


# ============================================================================ full
def run_full(limit: Optional[int]) -> dict:
    t0 = time.perf_counter()
    corpus = load_corpus(limit)
    prof = build_profile_for(corpus)

    # calibration_check carried over from v3 UNCHANGED: halt rather than report a flattering
    # number if the PMI gate has started swallowing known-meaningful pairs.
    calib = {}
    for a, b in PMI_CONTROL_PAIRS:
        ok, reason = prof.eligible_meaning(a, b)
        calib["%s->%s" % (a, b)] = {"survives": bool(ok), "pmi": prof.pmi(a, b),
                                    "refusal": reason}
    survivors = sum(1 for v in calib.values() if v["survives"])
    if limit is None and survivors < len(PMI_CONTROL_PAIRS) - 1:
        raise AssertionError("BLOCK_DISPATCH_calibration_check: %r" % calib)

    facts, refusals = build_def_v4(corpus, prof)

    v3 = [json.loads(l) for l in open(V3_FACTS, encoding="utf-8") if l.strip()]
    v3_pairs = {(r["subject"], r["object"]) for r in v3}
    v4_pairs = {(r["subject"], r["object"]) for r in facts}

    checks = {}
    checks["arms_differ_verified"] = _digest(v3) != _digest(facts)
    survived = {"%s|%s" % p: (p in v4_pairs) for p in CONTROL_ROWS_MUST_SURVIVE}
    died = {"%s|%s" % p: (p not in v4_pairs) for p in FAULT_ROWS_MUST_DIE}
    checks["control_rows_survived"] = survived
    checks["fault_rows_removed"] = died

    y_before = multisense_yield(v3)
    y_after = multisense_yield(facts)

    verdict, msgs = "STRUCTURAL_PASS_PENDING_B3", []
    if len(facts) < 500:
        verdict = "HARD_FAIL_YIELD_COLLAPSE"
        msgs.append("v4 facts %d < 500" % len(facts))
    if not checks["arms_differ_verified"]:
        verdict = "BLOCK_DISPATCH_META_RULE_AF"
        msgs.append("v3 and v4 fact sets identical")
    if not all(survived.values()):
        verdict = "HARD_FAIL_CONTROL_ROWS"
        msgs.append("lost: %s" % [k for k, v in survived.items() if not v])
    if not all(died.values()):
        verdict = "HARD_FAIL_REGRESSION"
        msgs.append("still present: %s" % [k for k, v in died.items() if not v])

    yield_band = ("YIELD_IMPROVED"
                  if (y_after["n_senses_with_gt1_source_sentence"] >= 150
                      and y_after["n_multi_sense_words_with_ALL_senses_gt1_sentence"] >= 12)
                  else "YIELD_HELD"
                  if y_after["n_senses_with_gt1_source_sentence"] >= 102
                  else "YIELD_REGRESSED")

    os.makedirs(NEW_FOUNDATION, exist_ok=True)
    fpath = os.path.join(NEW_FOUNDATION, "definitional_facts_v4.jsonl")
    tmp = fpath + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for r in facts:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, fpath)

    sample_path = os.path.join(OUT_DIR, "b3_audit_sample_DEF_V4.json")
    _atomic_write_json(sample_path, {
        "arm": "DEF_V4_PARSEFIX",
        "n_facts_in_arm": len(facts),
        "sample_seed": 42,
        "sampling": "random.Random(42).sample over fid order -- BIT-IDENTICAL to v2/v3 B3, "
                    "asserted in run_self_test",
        "rubric": "MEANINGFUL / RELATED / NOISE per notes/foundation_grounding_sample_2026-08-12.md",
        "scored": False,
        "note": "UNSCORED. The cell assigns no buckets and claims no quality band. Baseline to "
                "compare against is the v3 DEF hand-score 19/9/22 = 38% MEANINGFUL "
                "(notes/director_handscore_b3_def_vs_control_2026-08-12.md). Bands: "
                "preregs/2026-08-12_definitional_parse_faults_v4.md",
        "rows": sample_for_audit(facts)})

    return {
        "verdict": verdict,
        "verdict_msg": ("v4 parse-fix: %d facts (v3 1751, %+d); yield band %s; %s"
                        % (len(facts), len(facts) - len(v3), yield_band,
                           "; ".join(msgs) if msgs else "all machine checks pass")),
        "summary": "definitional parse-fault repair v4",
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "n_facts_v3": len(v3), "n_facts_v4": len(facts),
        "n_pairs_kept_from_v3": len(v3_pairs & v4_pairs),
        "n_pairs_new_in_v4": len(v4_pairs - v3_pairs),
        "n_pairs_dropped_from_v3": len(v3_pairs - v4_pairs),
        "subject_type_mix": dict(Counter(f["subject_type"] for f in facts)),
        "multiword_subject_count": sum(1 for f in facts if " " in f["subject"]),
        "pattern_mix": dict(Counter(f["pattern"] for f in facts)),
        "segment_mix": dict(Counter(f["segment"] for f in facts)),
        "refusals": dict(refusals),
        "checks": checks,
        "pmi_calibration_controls": calib,
        "yield_band": yield_band,
        "multisense_yield_BEFORE_v3": y_before,
        "multisense_yield_AFTER_v4": y_after,
        "b3_audit_sample_path": sample_path,
        "facts_path": fpath,
        "prereg": "preregs/2026-08-12_definitional_parse_faults_v4.md",
        "quality_scored_here": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("full", "smoke", "self-test"), default="full")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if args.mode == "self-test":
        m = run_self_test()
        _atomic_write_json(os.path.join(OUT_DIR, "selftest_metrics.json"), m)
        print(json.dumps(m, indent=2)[:2000])
        return
    _write_start_marker(OUT_DIR, args.mode)
    limit = args.limit if args.limit is not None else (400 if args.mode == "smoke" else None)
    m = run_full(limit)
    out = os.path.join(OUT_DIR, "metrics.json" if args.mode == "full" else "smoke_metrics.json")
    _atomic_write_json(out, m)
    print(json.dumps({k: v for k, v in m.items() if k != "multisense_yield_BEFORE_v3"},
                     indent=2)[:4000])


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUT_DIR, e)
        raise
