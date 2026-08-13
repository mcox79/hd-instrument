"""exp_structured_comparator_v1 -- matched ablation, ONE variable: THE COMPARATOR.

PRE-REG: preregs/2026-08-13_structured_comparator_ablation.md (filed BEFORE any arm ran).

THE FINDING UNDER TEST (notes/brain_fidelity_audit_readout_2026-08-13.md): the meaning read-out's
decision variable is cosine between two BAGS OF NEARBY CONTENT WORDS. Propose, the informativeness
gate and verify all route through the same canonicalize_fast, so a systematic co-occurrence bias
is invisible to verification. Blind hand-score: 3 MEANINGFUL / 19 RELATED / 78 NOISE, failures
being topical neighbours (whisky->wedding, banana->people, checklist->joe).

ARMS -- everything identical except the function that builds the compared vector:
  CONTROL     context_vector_masked  -- bag of content-word lemmas   (the shipped default)
  STRUCTURED  structural_vector_masked -- sign(sum(bind(rel_vec, filler_vec))) over the target's
              1-hop dependency neighbourhood + co-arguments of its head

F1/F3 are OFF in BOTH arms (proven irrelevant by the 2026-08-13 hand-score; not varied here).

THIS CELL MAKES NO QUALITY CLAIM. It writes 100 blind rows for the Director's hand-score and one
MECHANISTIC, hand-score-independent number: per-arm agreement with a plain co-occurrence baseline.

GROWTH IS PAUSED: everything is written under data/exp_structured_comparator_v1/ only.
ASCII-only. Deterministic: sorted(set(...)), hashlib-seeded vectors, fixed integer seeds.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import platform
import random
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class, is_eligible_meaning
from hdlab.grounding_acquisition_loop import content_words
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    PBV_COMMIT_STRENGTH,
    ReadingLoopState,
    StructuralEncoder,
    checkpoint,
    make_pbv_fns,
    normalize_lemma,
    pbv_trajectory_stats,
    process_sentence,
    seed_known_words,
)
from tools import exp_checkpoint

from experiments.exp_reading_grounding_loop_cycle1_v1 import (
    N_DIM, SCHEMA_THRESH_FULL, load_base_vocab_seed, repo_path,
)
from experiments.exp_reading_grounding_loop_cycle2_v1 import (
    CHUNK_SIZE, grounded_lemmas_in_store,
)
from experiments.exp_definitional_grounding_v5 import load_corpus_v5

ANCHOR_NAME = "structured_comparator_v1"
PREREG = "preregs/2026-08-13_structured_comparator_ablation.md"

ARMS = ["CONTROL", "STRUCTURED"]
SEGMENTS = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new"]
EXPECTED_N_UNITS = len(ARMS) * len(SEGMENTS)

# ONE VARIABLE: both arms get the IDENTICAL store seed, so the hypervector codebook is not a
# second variable. Same value the reference run used, which is what lets CONTROL reproduce it.
ARM_SEED = 4201

SAMPLE_SEED = 42
SAMPLE_N = 50
BLIND_SHUFFLE_SEED = 42

SMOKE_LIMIT_PER_SEGMENT = 400

# ---- CONTROL regression reference (prereg sec 6, S4) -------------------------------------------
REF_RUN = "data/exp_grounding_quality_readout_v1/metrics.json"
REF_N_FACTS = 384
REF_DIGEST16 = "836571fa99d5765d"

# ---- pre-registered bands, RECORDED not evaluated (the Director scores blind) -------------------
QUALITY_BANDS_RECORDED = {
    "discriminator": "MEANINGFUL(STRUCTURED) - MEANINGFUL(CONTROL), two blind 50-row hand-scores",
    "STRUCTURAL_FIX_WORKS": "MEANINGFUL(STRUCTURED) >= 0.15 AND delta >= +0.10",
    "PARTIAL": "delta in [+0.05, +0.10) -- BELOW the 2-SE resolution at n=50; licenses a re-score "
               "at larger n and nothing else",
    "NULL": "abs(delta) < 0.05 -- pre-declared acceptable and genuinely possible",
    "HURTS": "delta <= -0.05",
    "power": "at p1=0.03, p2=0.15, n=50/arm: SE(delta)=0.056, delta=0.12=2.14 SE, two-sided "
             "power ~0.57. MINIMUM DETECTABLE DELTA AT 2 SE = +0.11. Resolving delta=+0.075 "
             "needs n~88/arm at 2 SE, or n~172/arm for 80% power.",
    "why_a_positive_is_reachable_here": "the 2026-08-12 read-out cell was FLOOR-LIMITED (both "
                                        "arms pinned at 2-4%, max attainable delta 0.06, inside "
                                        "its own NULL band -- it could not have returned a "
                                        "non-NULL verdict). Here only CONTROL is pinned; "
                                        "STRUCTURED is unconstrained upward, so 8/50 against "
                                        "1-2/50 clears the band.",
    "secondary_mechanistic": "cooc_agreement_top5(STRUCTURED) >= cooc_agreement_top5(CONTROL) "
                             "- 0.05  =>  THE COMPARATOR DID NOT BIND; that is the headline "
                             "REGARDLESS of the hand-score.",
}


# =========================================================================== io helpers
def _output_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _write_start_marker(output_dir: str, run_mode: str, arm: Optional[str]) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "arm": arm,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node(),
              "prereg": PREREG}
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"), marker)


def _heartbeat(output_dir: str, payload: dict) -> None:
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(payload, ts_iso=datetime.now(timezone.utc).isoformat())) + "\n")


def _digest_pairs(pairs) -> str:
    h = hashlib.sha256()
    for s, o in sorted(set(pairs)):
        h.update(("%s\x1f%s\x1e" % (s, o)).encode("utf-8"))
    return h.hexdigest()


# =========================================================================== corpus
def build_stream(run_mode: str) -> List[Tuple[str, str]]:
    """IDENTICAL corpus + order to the reference run: load_corpus_v5(None, lineaware=True),
    34169 sentences. Holding it fixed is what makes CONTROL reproducible against 384 /
    836571fa99d5765d."""
    limit = SMOKE_LIMIT_PER_SEGMENT if run_mode == "smoke" else None
    return load_corpus_v5(limit, lineaware=True)


# =========================================================================== one arm
def run_arm(arm: str, run_mode: str, output_dir: str) -> dict:
    already = exp_checkpoint.completed_units(output_dir)
    done_key = exp_checkpoint.unit_key("arm_done", arm)
    if done_key in already:
        return dict(exp_checkpoint.load_units(output_dir)[done_key], skipped=True)

    stream = build_stream(run_mode)
    store = HDFactStore(n_dim=N_DIM, seed=ARM_SEED,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, load_base_vocab_seed(), source="seed_base_vocabulary")
    known_seed_snapshot = set(state.known_seed)

    # ---------------- THE ONE VARIABLE ----------------
    encoder = StructuralEncoder(REPO_ROOT) if arm == "STRUCTURED" else None
    # F1/F3 OFF in BOTH arms: readout=None, freeze_episode=False.
    propose_fn, verify_fn = make_pbv_fns(state)
    pbv_fns = (propose_fn, verify_fn)

    n_chunks = math.ceil(len(stream) / CHUNK_SIZE) if stream else 0
    seg_seen: Dict[str, int] = {}
    seg_units_written: Dict[str, bool] = {}
    t0 = time.time()
    last_hb = t0

    for chunk_idx in range(n_chunks):
        chunk = stream[chunk_idx * CHUNK_SIZE:(chunk_idx + 1) * CHUNK_SIZE]
        for i, (seg, sent) in enumerate(chunk):
            seg_seen[seg] = seg_seen.get(seg, 0) + 1
            process_sentence(state, sent, f"{arm}_{chunk_idx}_{i}", pass_idx=chunk_idx,
                             pbv_fns=pbv_fns, revive_terminal=True, encoder=encoder)
        seg_tag = chunk[-1][0] if chunk else "unknown"
        row = checkpoint(state, pass_idx=chunk_idx, source_tag=seg_tag,
                         schema_thresh=SCHEMA_THRESH_FULL, pbv=True,
                         commit_strength=PBV_COMMIT_STRENGTH)

        if seg_tag in SEGMENTS and not seg_units_written.get(seg_tag):
            seg_units_written[seg_tag] = True
            key = exp_checkpoint.unit_key(arm, seg_tag)
            if key not in already:
                exp_checkpoint.record_unit(output_dir, key, {
                    "arm": arm, "segment": seg_tag, "first_chunk_idx": chunk_idx,
                    "n_grounded_at_segment_open": len(grounded_lemmas_in_store(state.store))})
        if chunk_idx % 10 == 0 or chunk_idx == n_chunks - 1:
            print(f"[progress] {arm} chunk={chunk_idx + 1}/{n_chunks} seg={seg_tag} "
                  f"grounded={len(grounded_lemmas_in_store(state.store))} "
                  f"refused={row['n_refused_cumulative']} "
                  f"elapsed={time.time() - t0:.1f}s", flush=True)
        if time.time() - last_hb >= 30.0:
            last_hb = time.time()
            _heartbeat(output_dir, {"arm": arm, "chunk": chunk_idx, "n_chunks": n_chunks,
                                    "elapsed_s": round(time.time() - t0, 1)})

    traj = pbv_trajectory_stats(state.library)
    gm = [f for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    grounded = grounded_lemmas_in_store(state.store)
    n_conf, n_disc = int(traj["n_confirm"]), int(traj["n_disconfirm"])
    verdict_bearing = n_conf + n_disc

    summary = {
        "arm": arm,
        "encoder": "structural_vector_masked" if encoder is not None else "context_vector_masked",
        "readout": None, "freeze_episode": False,
        "n_sentences": len(stream), "n_chunks": n_chunks,
        "segments_seen": {s: seg_seen.get(s, 0) for s in SEGMENTS},
        "n_grounded": len(grounded),
        "n_meaning_facts": len(gm),
        "n_tautology_facts": sum(1 for f in gm if f.subject == f.obj),
        "n_closed_class_object_facts": sum(1 for f in gm if is_closed_class(f.obj)),
        "no_leak_violations": sorted(set(l for l in grounded if l in known_seed_snapshot)),
        "n_refusals": len(state.refusals),
        "refusal_reasons": _count_reasons(state.refusals),
        "trajectory": {k: v for k, v in traj.items() if k != "revisions"},
        "confirm_rate": round(n_conf / verdict_bearing, 6) if verdict_bearing else None,
        "n_verdict_bearing": verdict_bearing,
        "admission_rate": traj.get("informative_encounter_rate"),
        "encoder_stats": encoder.stats() if encoder is not None else None,
        "pairs_digest": _digest_pairs((f.subject, f.obj) for f in gm),
        "grounded_objects": {f.subject: f.obj for f in gm},
        "elapsed_s": round(time.time() - t0, 2),
    }
    _atomic_json(os.path.join(output_dir, f"arm_{arm}_provenance.json"),
                 [_prov_row(p) for p in state.provenance if p["relation"] == MEANING_RELATION])
    exp_checkpoint.record_unit(output_dir, done_key, summary)
    return summary


def _prov_row(p: dict) -> dict:
    return {k: p.get(k) for k in ("fid", "subject", "relation", "object", "segment", "pass_idx",
                                  "best_cos", "n_exposures", "schema_score", "evidence",
                                  "hypothesis")}


def _count_reasons(refusals: List[dict]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in refusals:
        out[r["reason"]] = out.get(r["reason"], 0) + 1
    return dict(sorted(out.items()))


# ================================================== SECONDARY: co-occurrence baseline
def cooccurrence_top(run_mode: str, k: int = 5) -> Dict[str, List[str]]:
    """PLAIN sentence-level co-occurrence over the FULL corpus: subject -> its k highest-count
    co-occurring content lemmas, restricted to is_eligible_meaning, ties broken by sorted lemma.

    This is deliberately the DUMBEST possible "what word hangs around this word" baseline. It is
    the yardstick the two arms are measured against: CONTROL is predicted to track it closely,
    STRUCTURED to diverge. No hand-scoring is involved anywhere in this number."""
    counts: Dict[str, Counter] = defaultdict(Counter)
    for _seg, sent in build_stream(run_mode):
        lem = sorted(set(normalize_lemma(w) for w in content_words(sent)))
        for a in lem:
            for b in lem:
                if a != b:
                    counts[a][b] += 1
    out: Dict[str, List[str]] = {}
    for a, c in counts.items():
        ranked = sorted(((-n, b) for b, n in c.items() if is_eligible_meaning(b)))
        out[a] = [b for _n, b in ranked[:k]]
    return out


def cooc_agreement(pairs: Dict[str, str], top: Dict[str, List[str]]) -> dict:
    n = t1 = t5 = miss = 0
    for s, o in sorted(pairs.items()):
        tops = top.get(s)
        if not tops:
            miss += 1
            continue
        n += 1
        t1 += int(o == tops[0])
        t5 += int(o in tops)
    return {"n_scored": n, "n_subject_absent_from_baseline": miss,
            "cooc_agreement_top1": round(t1 / n, 6) if n else None,
            "cooc_agreement_top5": round(t5 / n, 6) if n else None}


# =========================================================================== audit sample
def _sample_rows(prov: List[dict]) -> List[dict]:
    """50 rows, random.Random(42).sample over fid order -- the SAME sampling convention as
    data/exp_grounding_quality_readout_v1."""
    by_fid = sorted(prov, key=lambda r: (int(r["fid"]), str(r["subject"])))
    n = min(SAMPLE_N, len(by_fid))
    picked = random.Random(SAMPLE_SEED).sample(by_fid, n)
    rows = []
    for r in picked:
        sents = sorted(set(e.get("sentence") for e in (r.get("evidence") or [])
                           if e.get("sentence")))
        hyp = r.get("hypothesis") or {}
        rows.append({
            "subject": r["subject"], "object": r["object"],
            "subject_type": "COMMON", "subject_head_lemma": r["subject"],
            "segment": r.get("segment"), "pattern": None,
            "n_attestations": r.get("n_exposures"), "pmi": None, "patterns_seen": [],
            "source_sentences": sents[:5],
            "definiendum_surface": None, "definiens_surface": None,
            "fid": r["fid"], "relation": r["relation"],
            "best_cos": r.get("best_cos"), "schema_score": r.get("schema_score"),
            "n_confirm": hyp.get("n_confirm"), "n_disconfirm": hyp.get("n_disconfirm"),
            "n_abandoned": hyp.get("n_abandoned"),
        })
    return rows


_ASCII_FOLD = {0x2018: "'", 0x2019: "'", 0x201a: "'", 0x201b: "'", 0x201c: '"', 0x201d: '"',
               0x201e: '"', 0x2013: "-", 0x2014: "-", 0x2212: "-", 0x2026: "...", 0x00a0: " "}


def _ascii(s: str) -> str:
    return "".join(c if ord(c) < 128 else "?" for c in s.translate(_ASCII_FOLD))


def write_scoring_sheet(path: str, blind_rows: List[dict]) -> None:
    """EXACT format of data/exp_grounding_quality_readout_v1/SCORING_SHEET.txt (verified against
    that file: 100-char rule, `[%03d] subj  ->  obj`, 6-space indent, sentence truncated to
    s[:157] + '...').

    NO-LEAK: best_cos, schema_score, every attestation counter, fid and segment are NOT printed,
    and EXACTLY ONE context sentence is printed per row so block shape carries no arm signal.
    arm_key.json is never read here."""
    lines = [
        "GROUNDED_MEANING BLIND SCORING SHEET  (exp_%s)" % ANCHOR_NAME,
        "%d rows, file order preserved. Rubric: MEANINGFUL / RELATED / NOISE." % len(blind_rows),
        "Line 1: [idx] subject -> assigned grounded meaning.  Line 2: one context sentence "
        "(<=160 chars).",
        "Write your verdict at the end of line 1 for each row.",
        "=" * 100,
        "",
    ]
    for i, r in enumerate(blind_rows, start=1):
        lines.append("[%03d] %s  ->  %s" % (i, _ascii(r["subject"]), _ascii(r["object"])))
        srcs = r.get("source_sentences") or [""]
        s = _ascii(srcs[0])
        if len(s) > 160:
            s = s[:157] + "..."
        lines.append('      "%s"' % s)
        lines.append("")
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    os.replace(path + ".tmp", path)


def write_audit_samples(output_dir: str, arms: Dict[str, dict]) -> dict:
    combined = []
    out_paths = {}
    for arm in ARMS:
        with open(os.path.join(output_dir, f"arm_{arm}_provenance.json"), encoding="utf-8") as f:
            prov = json.load(f)
        rows = _sample_rows(prov)
        env = {
            "arm": arm, "n_facts_in_arm": arms[arm]["n_meaning_facts"],
            "sample_seed": SAMPLE_SEED,
            "sampling": "random.Random(42).sample over fid order",
            "rubric": "MEANINGFUL / RELATED / NOISE per "
                      "notes/foundation_grounding_sample_2026-08-12.md",
            "scored": False,
            "note": "UNSCORED. The cell assigns no buckets and claims no quality band. Bands: "
                    + PREREG + " sec 4.",
            "rows": rows,
        }
        name = f"b3_audit_sample_{arm}.json"
        _atomic_json(os.path.join(output_dir, name), env)
        out_paths[arm] = name
        combined.extend((arm, r) for r in rows)

    rng = random.Random(BLIND_SHUFFLE_SEED)
    rng.shuffle(combined)
    blind_rows, key_rows = [], []
    for i, (arm, r) in enumerate(combined):
        blind_rows.append(dict(r, blind_id=i))
        key_rows.append({"blind_id": i, "arm": arm, "subject": r["subject"],
                         "object": r["object"], "fid": r["fid"]})
    _atomic_json(os.path.join(output_dir, "blind_sample.json"), {
        "n_rows": len(blind_rows), "shuffle_seed": BLIND_SHUFFLE_SEED,
        "sample_seed": SAMPLE_SEED,
        "arms_present": "TWO, LABELS STRIPPED -- the key is in arm_key.json, do not open it "
                        "until every row is scored",
        "rubric": "MEANINGFUL / RELATED / NOISE per "
                  "notes/foundation_grounding_sample_2026-08-12.md",
        "instruction": "Score each row's (subject -> object) read-out as MEANINGFUL / RELATED / "
                       "NOISE using source_sentences as context. Score all rows in ONE sitting.",
        "scored": False, "bands": QUALITY_BANDS_RECORDED, "rows": blind_rows,
    })
    _atomic_json(os.path.join(output_dir, "arm_key.json"), {
        "warning": "DO NOT OPEN UNTIL blind_sample.json IS FULLY SCORED",
        "shuffle_seed": BLIND_SHUFFLE_SEED, "rows": key_rows})
    write_scoring_sheet(os.path.join(output_dir, "SCORING_SHEET.txt"), blind_rows)
    return {"per_arm_files": out_paths, "blind_file": "blind_sample.json",
            "key_file": "arm_key.json", "sheet": "SCORING_SHEET.txt",
            "n_blind_rows": len(blind_rows)}


# =========================================================================== finalize
def finalize(run_mode: str, output_dir: str) -> dict:
    units = exp_checkpoint.load_units(output_dir)
    arms = {a: units[exp_checkpoint.unit_key("arm_done", a)] for a in ARMS
            if exp_checkpoint.unit_key("arm_done", a) in units}
    missing_arms = [a for a in ARMS if a not in arms]

    present = sorted(set(units))
    expected = sorted(set(exp_checkpoint.unit_key(a, s) for a in ARMS for s in SEGMENTS))
    missing_units = [k for k in expected if k not in present]
    s1 = not missing_arms and not missing_units

    s2 = {a: {"n_tautology_facts": arms[a]["n_tautology_facts"],
              "n_closed_class_object_facts": arms[a]["n_closed_class_object_facts"],
              "no_leak_violations": arms[a]["no_leak_violations"]} for a in arms}
    s2_ok = all(v["n_tautology_facts"] == 0 and v["n_closed_class_object_facts"] == 0
                and not v["no_leak_violations"] for v in s2.values())

    digests = {a: arms[a]["pairs_digest"] for a in arms}
    s3 = len(arms) == len(ARMS) and len(sorted(set(digests.values()))) == len(ARMS)

    # ---- S4 CONTROL REGRESSION vs the reference run
    s4 = {"reference": REF_RUN, "expected_n_facts": REF_N_FACTS,
          "expected_digest16": REF_DIGEST16}
    if "CONTROL" in arms:
        got_n = arms["CONTROL"]["n_meaning_facts"]
        got_d = arms["CONTROL"]["pairs_digest"][:16]
        s4.update({"observed_n_facts": got_n, "observed_digest16": got_d,
                   "control_reproduces_reference": bool(got_n == REF_N_FACTS
                                                        and got_d == REF_DIGEST16)})
    else:
        s4["control_reproduces_reference"] = None

    s5 = {a: {"n_meaning_facts": arms[a]["n_meaning_facts"],
              "meets_yield_floor_50": arms[a]["n_meaning_facts"] >= 50} for a in arms}

    # ---- SECONDARY: co-occurrence agreement, per arm
    top = cooccurrence_top(run_mode, k=5)
    cooc = {a: cooc_agreement(arms[a]["grounded_objects"], top) for a in arms}
    cooc_note = None
    if len(cooc) == 2:
        cs = cooc["STRUCTURED"]["cooc_agreement_top5"]
        cc = cooc["CONTROL"]["cooc_agreement_top5"]
        if cs is not None and cc is not None:
            cooc_note = ("DID_NOT_BIND" if cs >= cc - 0.05 else "DIVERGED")

    sample_info = {}
    if len(arms) == len(ARMS):
        sample_info = write_audit_samples(output_dir, arms)

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "prereg": PREREG,
        "wire_status": "VET_PENDING -- structured comparator is DEFAULT-OFF; nothing wired ON",
        "verdict": "STRUCTURAL_PASS_PENDING_HANDSCORE" if (s1 and s2_ok and s3)
                   else "STRUCTURAL_INCOMPLETE",
        "QUALITY_CLAIM": "NONE -- this cell emits no quality tier. The primary discriminator is a "
                         "BLIND HUMAN HAND-SCORE the Director performs on blind_sample.json.",
        "noncircularity_witness": NONCIRCULARITY_WITNESS,
        "quality_bands_recorded_not_evaluated": QUALITY_BANDS_RECORDED,
        "structural_gates": {
            "S1_cardinality": {"ok": s1, "expected_n_units": EXPECTED_N_UNITS,
                               "n_present": len(present), "missing_units": missing_units,
                               "missing_arms": missing_arms},
            "S2_integrity": {"ok": s2_ok, "per_arm": s2},
            "S3_arms_differ": {"ok": s3, "digests": digests},
            "S4_control_regression": s4,
            "S5_yield_floor": s5,
        },
        "secondary_cooccurrence_agreement": {
            "what": "agreement between each arm's banked (subject -> object) facts and a PLAIN "
                    "sentence-level co-occurrence baseline over the same 34169-sentence corpus. "
                    "Hand-score independent.",
            "per_arm": cooc,
            "binding_check": cooc_note,
            "binding_rule": QUALITY_BANDS_RECORDED["secondary_mechanistic"],
        },
        "objective_metrics": {a: {k: v for k, v in arms[a].items()
                                  if k not in ("grounded_objects",)} for a in arms},
        "deliverable": sample_info,
        "limitations": [
            "STRUCTURED sees ~4x fewer features per encounter than CONTROL (2.86 vs 11.33, "
            "prereg sec 3.1). Filtering IS the mechanism, so this is not corrected for; it is "
            "the leading alternative explanation for a NULL ('structure was starved').",
            "The UD front-end is trained on UD EWT (web text) and used out-of-domain on news + "
            "OpenStax biology; parse noise degrades STRUCTURED only, so it biases AGAINST H1.",
            "Single judge, one sitting, n=50/arm. The PARTIAL band is below the 2-SE resolution.",
            "No cross-comparison to the 64% v5 definitional-extraction number: different "
            "pipeline (a parser SUPPLYING facts vs a read-out ACQUIRING one).",
        ],
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
    return metrics


NONCIRCULARITY_WITNESS = {
    "question": "Can the STRUCTURED comparator DISAGREE with the CONTROL _cos() argmax, or does "
                "it secretly reduce to it?",
    "witness_1_argmax_disagreement": {
        "probe": "data/exp_structured_comparator_v1/_probe_disagree.json",
        "method": "both encoders run over the same 3992-sentence corpus slice, two ConceptSpaces "
                  "built, argmax taken for every lemma present in both",
        "n_common_lemmas": 6283, "n_disagree": 6145, "disagreement_rate": 0.978036,
    },
    "witness_2_worked_example": {
        "probe": "data/exp_structured_comparator_v1/_probe_witness.json",
        "target": "whisky",
        "documented_control_failure": "whisky -> wedding (hand-score row 016)",
        "finding": "'wedding' is in the CONTROL bag in ALL THREE corpus sentences where it "
                   "co-occurs with 'whisky', and in the STRUCTURED feature set in NONE of them. "
                   "STRUCTURED cannot produce whisky->wedding from this corpus; CONTROL "
                   "demonstrably did.",
        "rows": [
            {"sentence": "One buyer ordered nine cases of Japanese whisky costing over $750 a "
                         "bottle for a wedding reception",
             "control_bag": ["bottle", "buyer", "case", "costing", "japanese", "nine", "order",
                             "reception", "wedding"],
             "structured_features": [["^mark", "costing"], ["~mark:obl", "bottle"],
                                     ["~mark:obl", "reception"]]},
            {"sentence": "One super-rich person bought nine boxes of Japanese whisky that cost "
                         "more than over $750 a bottle for a wedding party",
             "control_bag": ["bottle", "box", "buy", "cost", "japanese", "more", "nine", "party",
                             "person", "rich", "super", "wedding"],
             "structured_features": [["^nmod", "box"], ["acl", "cost"], ["amod", "japanese"],
                                     ["~nmod:nummod", "nine"]]},
            {"sentence": "The attraction of the imported whisky was that no one who came to the "
                         "wedding would be able to find the same drink in India",
             "control_bag": ["able", "attraction", "come", "drink", "find", "india", "same",
                             "wedding"],
             "structured_features": [["^obj", "import"], ["~obj:conj", "come"]]},
        ],
        "corroborating": {
            "checklist": "documented failure checklist->joe; 'joe' and 'kittinger' are in the bag "
                         "and excluded by structure in both corpus sentences",
            "banana": "structure isolates ('^nsubj','fruit') -- the correct hypernym -- from a "
                      "12-word bag also containing adult, apple, ate, week, orange",
        },
    },
    "still_a_dot_product": "Yes, and the audit explicitly permitted this: 'the point is WHAT is "
                           "being compared, not whether a dot product is involved'. What changed "
                           "is the feature alphabet (role-bound dependency pairs, 1-hop only) and "
                           "it is asserted byte-identical in symbol codebook to CONTROL by "
                           "hdlab.reading_grounding_loop._selftest_structural_unbound_matches_"
                           "context_vector.",
}


# =========================================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("full", "smoke", "self-test"), default="full")
    ap.add_argument("--arm", choices=ARMS + ["finalize", "all"], default=None)
    args = ap.parse_args()

    if args.mode == "self-test":
        from hdlab.reading_grounding_loop import _run_all_selftests
        r = _run_all_selftests()
        print(json.dumps({"selftests": len(r), "ok": True}, indent=2))
        return

    output_dir = _output_dir(args.mode)
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, args.mode, args.arm)
    with open(os.path.join(output_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    todo = ARMS + ["finalize"] if args.arm in (None, "all") else [args.arm]
    for step in todo:
        try:
            if step == "finalize":
                m = finalize(args.mode, output_dir)
                print(json.dumps({"verdict": m["verdict"],
                                  "S4": m["structural_gates"]["S4_control_regression"],
                                  "cooc": m["secondary_cooccurrence_agreement"]["per_arm"],
                                  "binding": m["secondary_cooccurrence_agreement"]["binding_check"]},
                                 indent=2), flush=True)
            else:
                s = run_arm(step, args.mode, output_dir)
                print(json.dumps({k: s[k] for k in ("arm", "encoder", "n_meaning_facts",
                                                    "n_grounded", "elapsed_s")}, indent=2),
                      flush=True)
        except Exception:
            traceback.print_exc()
            raise


if __name__ == "__main__":
    main()
