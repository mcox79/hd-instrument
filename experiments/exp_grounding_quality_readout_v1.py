"""experiments/exp_grounding_quality_readout_v1.py

DOES A STABLER READ-OUT PRODUCE BETTER MEANINGS?

Everything measured in exp_readout_fix_v1 is argmax STABILITY (flip rate, admission, confirm
rate). The landed-VET (notes/landed_vet_readout_fix_v1_2026-08-12.md) states the scope limit
explicitly: "NOT licensed: any statement about grounding quality/correctness." A read-out that
agrees with itself is not a read-out that is RIGHT.

THIS CELL CLAIMS NO QUALITY BAND. It produces the material for the only instrument that can
answer the quality question -- a BLIND HUMAN HAND-SCORE -- and emits only STRUCTURAL gates.
Its best possible verdict is STRUCTURAL_PASS_PENDING_B3.

Pre-reg: preregs/2026-08-12_grounding_quality_readout_v1.md
  sec 3   PRIMARY quality bands (scored LATER by the director, NOT here):
          HARD_PASS   delta >= +0.20 AND F1F3 MEANINGFUL >= 0.25
          MIDDLE_BAND delta in [+0.08, +0.20)
          NULL        |delta| < 0.08   -- stability and quality are DECOUPLED (live + expected)
          HARD_FAIL   delta <= -0.08
  sec 3.2 SELECTIVITY CAP: n_facts(F1F3)/n_facts(BASE) outside [0.5, 2.0] -> verdict capped at
          MIDDLE_BAND regardless of delta size
  sec 4   STRUCTURAL gates S1..S8 (this cell's own, machine-checked)
  sec 5   SECONDARY: confirm rate vs PBV's MEASURED 0.100561 gate, positive-controlled on BASE

ARMS -- two, ONE variable (the read-out), same corpus, same order, same seed:
  PBV_BASE   readout=None,               freeze_episode=False   (current default; also the
                                                                 positive control for sec 5)
  PBV_F1F3   readout=operating_readout(), freeze_episode=True,   (mechanism)
             freeze_epoch_fn=<chunk index>

F1 = the field-relative z_top gate (margin_z_min = 3.542496,
MEASURED@data/exp_readout_fix_v1/metrics.json:fix1.thresholds['grow_epi|f2=0|z_top'].g_match).
F2 (anchor_background) is SHELLVED-OFF and a self-test asserts it stays off.
F3 = the anchor-field freeze; epoch-interned per 150-sentence chunk (prereg sec 6 DECLARED
COARSENING -- coarser than true per-episode freeze, strictly FINER than the 5-snapshot
granularity at which F3's -0.168 was actually measured).

# CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - start_marker_written / crash_diagnostic_present / per-chunk progress flush / heartbeat
# - cardinality_ok: EXPECTED_N_UNITS = 10 (2 arms x 5 segments); finalize refuses on any missing
# - crlb n/a: the discriminator is a human-bucketed proportion, not an estimator against a noise
#   floor; the binding limit is BINOMIAL (SE 0.10 at n=50) and is enforced by the 0.20 band
# - arms-must-differ: S3, sha256 over each arm's sorted (subject, object) set
# - all numbers in comments are tagged MEASURED@ / HYPOTHESIZED@ / CITED@
# - real_code_path: drives the REAL ReadingLoopState / process_sentence / checkpoint /
#   Library.flag / HDFactStore / make_pbv_fns / operating_readout objects; no synthetic-only branch

ASCII-only. Deterministic (fixed seeds; sorted(set(...)) throughout; no built-in hash()).
"""
from __future__ import annotations

import os

# MUST precede numpy import (PROT: split-nondeterminism / BLAS thread nondeterminism)
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    OPERATING_MARGIN_STAT,
    OPERATING_MARGIN_Z_MIN,
    OPERATING_MARGIN_Z_MIN_MATCHED_RETENTION,
    OPERATING_MARGIN_Z_MIN_SOURCE,
    OPERATING_READOUT_NAME,
    PBV_COMMIT_STRENGTH,
    PBV_INFORMATIVE_MIN,
    ReadingLoopState,
    checkpoint,
    make_pbv_fns,
    operating_readout,
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

ANCHOR_NAME = "grounding_quality_readout_v1"
PREREG = "preregs/2026-08-12_grounding_quality_readout_v1.md"

ARMS = ["PBV_BASE", "PBV_F1F3"]
SEGMENTS = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new"]
EXPECTED_N_UNITS = len(ARMS) * len(SEGMENTS)          # S1 = 10

# ONE VARIABLE: both arms get the IDENTICAL store seed. The only difference between the arms is
# the read-out (readout= / freeze_episode= / freeze_epoch_fn=). Differing per-arm seeds would put
# a second variable (the hypervector codebook) into a two-arm comparison.
ARM_SEED = 4201

SAMPLE_SEED = 42                 # sampling convention, BIT-IDENTICAL to
SAMPLE_N = 50                    # data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json
BLIND_SHUFFLE_SEED = 42

SMOKE_LIMIT_PER_SEGMENT = 400    # smoke only; the FULL run passes limit=None (34169 sentences)

# ---- pre-registered STRUCTURAL bands (prereg sec 4; frozen before any run of this cell) --------
S5_PBV_CONFIRM_RATE_CITED = 0.100561   # MEASURED@data/exp_pbv_hypothesis_v1_smoke/metrics.json:
                                       # arms.B_PBV.trajectory -> 788 / (788 + 7048)
S5_TOLERANCE = 0.05
S6_YIELD_FLOOR = 50                    # each arm must bank >= 50 GROUNDED_MEANING facts
S7_PEAK_SNAPSHOT_BYTES_CAP = 4 * 1024 ** 3
S8_MATCHED_RETENTION = OPERATING_MARGIN_Z_MIN_MATCHED_RETENTION   # 0.403405
S8_DRIFT_VOIDS_MATCH = 0.10
SELECTIVITY_BAND = (0.5, 2.0)          # prereg sec 3.2 CAP

# quality bands -- RECORDED ONLY, so the director's later hand-score is judged against the
# pre-registration and not against anything invented after seeing the sample. THIS CELL DOES NOT
# EVALUATE THEM (it has no scores to evaluate them with).
QUALITY_BANDS_RECORDED = {
    "discriminator": "MEANINGFUL(PBV_F1F3) - MEANINGFUL(PBV_BASE), two blind 50-row hand-scores",
    "HARD_PASS": "delta >= +0.20 AND F1F3 MEANINGFUL >= 0.25",
    "MIDDLE_BAND": "delta in [+0.08, +0.20) -- under-powered at n=50; licenses a re-score only",
    "NULL": "|delta| < 0.08 -- a stabler read-out does NOT produce better meanings (LIVE outcome)",
    "HARD_FAIL_HURTS": "delta <= -0.08 -- F1+F3 makes meanings WORSE",
    "selectivity_cap": "n_facts(F1F3)/n_facts(BASE) outside [0.5, 2.0] -> capped at MIDDLE_BAND",
    "power": "SE(delta) ~ sqrt(2*0.25/50) = 0.10; deltas below ~0.20 are UNRESOLVABLE at 2 SE",
    "reference_points": {"v2_DIST_readout_handscore": 0.08, "v5_DEF_parser_handscore": 0.64,
                         "note": "0.64 is a CEILING REFERENCE from a DIFFERENT MECHANISM (a "
                                 "hand-written appositive/copula parser), NOT the comparator. The "
                                 "read-out's own prior quality number is the 0.08."},
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
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"), marker)


def _heartbeat(output_dir: str, payload: dict) -> None:
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(payload, ts_iso=datetime.now(timezone.utc).isoformat())) + "\n")


def _digest_pairs(pairs) -> str:
    """sha256 over a arm's sorted (subject, object) set -- S3 arms-must-differ."""
    h = hashlib.sha256()
    for s, o in sorted(set(pairs)):
        h.update(("%s\x1f%s\x1e" % (s, o)).encode("utf-8"))
    return h.hexdigest()


# =========================================================================== corpus
def build_stream(run_mode: str) -> List[Tuple[str, str]]:
    """(segment_tag, sentence) over the v5 line-aware corpus, in curriculum order.

    CORPUS CHOICE, prereg sec 2: `load_corpus_v5(limit, lineaware=True)` -- the SAME corpus the
    64% hand-scored v5 baseline and the 8% v2 DIST read-out baseline were built on. It is REAL
    MODERN text: OneStopEnglish news at three reading levels (ele_cont / int_cont / adv_new) plus
    the line-aware OpenStax Biology 2e glossary/body text (bio_new, the largest segment at 12546
    sentences) plus the bootstrap curriculum pool. It is NOT the McGuffey 200-year-old prose.
    Holding the corpus fixed is what makes the later hand-score comparable to the 0.08 reference
    at all; changing it would put a second variable into the comparison.
    """
    limit = SMOKE_LIMIT_PER_SEGMENT if run_mode == "smoke" else None
    return load_corpus_v5(limit, lineaware=True)


# =========================================================================== one arm
def _make_fns(arm: str, state: ReadingLoopState, epoch_holder: dict):
    """The ONE variable. Everything else about the two arms is byte-identical."""
    if arm == "PBV_BASE":
        return make_pbv_fns(state)                       # readout=None, freeze_episode=False
    return make_pbv_fns(state, readout=operating_readout(), freeze_episode=True,
                        freeze_epoch_fn=lambda: epoch_holder["chunk"])


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

    epoch_holder = {"chunk": 0}
    propose_fn, verify_fn = _make_fns(arm, state, epoch_holder)
    pbv_fns = (propose_fn, verify_fn)

    n_chunks = math.ceil(len(stream) / CHUNK_SIZE) if stream else 0
    seg_seen: Dict[str, int] = {}
    seg_units_written: Dict[str, bool] = {}
    released: set = set()
    peak_rss_note: Dict[str, int] = {}
    t0 = time.time()
    last_hb = t0

    for chunk_idx in range(n_chunks):
        epoch_holder["chunk"] = chunk_idx            # F3 epoch id (one snapshot per 150 sentences)
        chunk = stream[chunk_idx * CHUNK_SIZE:(chunk_idx + 1) * CHUNK_SIZE]
        for i, (seg, sent) in enumerate(chunk):
            seg_seen[seg] = seg_seen.get(seg, 0) + 1
            process_sentence(state, sent, f"{arm}_{chunk_idx}_{i}", pass_idx=chunk_idx,
                             pbv_fns=pbv_fns, revive_terminal=True)
        seg_tag = chunk[-1][0] if chunk else "unknown"
        row = checkpoint(state, pass_idx=chunk_idx, source_tag=seg_tag,
                         schema_thresh=SCHEMA_THRESH_FULL, pbv=True,
                         commit_strength=PBV_COMMIT_STRENGTH)
        # F3 memory bound: a lemma that has gone TERMINAL never proposes again, so its epoch
        # snapshot would be pinned for the rest of the pass (see release_episodes' docstring).
        terminal = sorted(set(l for l, it in state.library.items.items()
                              if it.status != "PENDING" and l not in released))
        if terminal:
            propose_fn.release_episodes(terminal)
            released.update(terminal)
        fs = propose_fn.freeze_stats()
        peak_rss_note["peak_live_snapshot_bytes"] = max(
            peak_rss_note.get("peak_live_snapshot_bytes", 0), int(fs["peak_live_snapshot_bytes"]))

        # per-(arm, segment) unit: written the first time a chunk CLOSES inside that segment, so
        # a killed run resumes with the segment-level cardinality ledger intact (S1).
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
                  f"snap_live={fs['live_snapshots_now']} "
                  f"snap_peak_b={fs['peak_live_snapshot_bytes']} "
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
        "readout": None if arm == "PBV_BASE" else OPERATING_READOUT_NAME,
        "freeze_episode": arm != "PBV_BASE",
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
        "freeze_stats": propose_fn.freeze_stats(),
        "pairs_digest": _digest_pairs((f.subject, f.obj) for f in gm),
        "grounded_objects": {f.subject: f.obj for f in gm},
        "elapsed_s": round(time.time() - t0, 2),
    }
    # provenance rows are what the audit sample is drawn from; keep them out of metrics.json but
    # persist them per-arm so the sample is reproducible without a re-run.
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


# =========================================================================== audit sample
def _sample_rows(prov: List[dict], arm: str) -> List[dict]:
    """50 rows, `random.Random(42).sample` over fid order -- the SAME sampling convention as
    data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json.

    Row field-set is IDENTICAL to that file. Fields with no analogue in a distributional read-out
    (`pmi`, `definiendum_surface`, `definiens_surface`, `pattern`, `patterns_seen`) are PRESENT
    and null / empty -- never fabricated."""
    by_fid = sorted(prov, key=lambda r: (int(r["fid"]), str(r["subject"])))
    n = min(SAMPLE_N, len(by_fid))
    picked = random.Random(SAMPLE_SEED).sample(by_fid, n)
    rows = []
    for r in picked:
        sents = sorted(set(e.get("sentence") for e in (r.get("evidence") or [])
                           if e.get("sentence")))
        hyp = r.get("hypothesis") or {}
        rows.append({
            "subject": r["subject"],
            "object": r["object"],
            "subject_type": "COMMON",
            "subject_head_lemma": r["subject"],
            "segment": r.get("segment"),
            "pattern": None,                 # no analogue: this is a read-out, not a parser
            "n_attestations": r.get("n_exposures"),
            "pmi": None,                     # no analogue
            "patterns_seen": [],             # no analogue
            "source_sentences": sents[:5],
            "definiendum_surface": None,     # no analogue
            "definiens_surface": None,       # no analogue
            "fid": r["fid"],
            "relation": r["relation"],
            "best_cos": r.get("best_cos"),
            "schema_score": r.get("schema_score"),
            "n_confirm": hyp.get("n_confirm"),
            "n_disconfirm": hyp.get("n_disconfirm"),
            "n_abandoned": hyp.get("n_abandoned"),
        })
    return rows


def write_audit_samples(output_dir: str, arms: Dict[str, dict]) -> dict:
    """Per-arm UNSCORED samples + ONE blind-shuffled combined file and its key.

    THE CELL ASSIGNS NO BUCKETS AND CLAIMS NO QUALITY BAND. `blind_sample.json` carries NO arm
    label; `arm_key.json` is the separate key the director opens only AFTER scoring."""
    combined = []
    out_paths = {}
    for arm in ARMS:
        path = os.path.join(output_dir, f"arm_{arm}_provenance.json")
        with open(path, encoding="utf-8") as f:
            prov = json.load(f)
        rows = _sample_rows(prov, arm)
        env = {
            "arm": arm,
            "n_facts_in_arm": arms[arm]["n_meaning_facts"],
            "sample_seed": SAMPLE_SEED,
            "sampling": "random.Random(42).sample over fid order -- same convention as "
                        "data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json",
            "rubric": "MEANINGFUL / RELATED / NOISE per "
                      "notes/foundation_grounding_sample_2026-08-12.md",
            "scored": False,
            "note": "UNSCORED. The cell assigns no buckets and claims no quality band. The "
                    "read-out's own prior hand-score is 8% (v2 DIST). The 64% v5 DEF number is a "
                    "DIFFERENT MECHANISM (a parser) and is a ceiling reference, NOT the "
                    "comparator. Bands: " + PREREG + " sec 3.",
            "rows": rows,
        }
        name = f"b3_audit_sample_READOUT_{'BASE' if arm == 'PBV_BASE' else 'F1F3'}.json"
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
        "n_rows": len(blind_rows),
        "shuffle_seed": BLIND_SHUFFLE_SEED,
        "sample_seed": SAMPLE_SEED,
        "arms_present": "TWO, LABELS STRIPPED -- the key is in arm_key.json, do not open it "
                        "until every row is scored",
        "rubric": "MEANINGFUL / RELATED / NOISE per "
                  "notes/foundation_grounding_sample_2026-08-12.md",
        "instruction": "Score each row's (subject -> object) read-out as MEANINGFUL / RELATED / "
                       "NOISE using source_sentences as context. Score all rows in ONE sitting.",
        "scored": False,
        "bands": QUALITY_BANDS_RECORDED,
        "rows": blind_rows,
    })
    _atomic_json(os.path.join(output_dir, "arm_key.json"), {
        "warning": "DO NOT OPEN UNTIL blind_sample.json IS FULLY SCORED",
        "shuffle_seed": BLIND_SHUFFLE_SEED, "rows": key_rows})
    return {"per_arm_files": out_paths, "blind_file": "blind_sample.json",
            "key_file": "arm_key.json", "n_blind_rows": len(blind_rows)}


# =========================================================================== finalize
def finalize(run_mode: str, output_dir: str) -> dict:
    units = exp_checkpoint.load_units(output_dir)
    arms = {a: units[exp_checkpoint.unit_key("arm_done", a)] for a in ARMS
            if exp_checkpoint.unit_key("arm_done", a) in units}
    missing_arms = [a for a in ARMS if a not in arms]

    # ---- S1 cardinality: 2 arms x 5 segments = 10 units
    present_units = sorted(set(k for k in units
                               if any(k == exp_checkpoint.unit_key(a, s)
                                      for a in ARMS for s in SEGMENTS)))
    missing_units = sorted(set(exp_checkpoint.unit_key(a, s) for a in ARMS for s in SEGMENTS)
                           - set(present_units))
    s1 = (not missing_arms) and (not missing_units) and len(present_units) == EXPECTED_N_UNITS

    # ---- S2 integrity per arm
    s2 = bool(arms) and all(
        arms[a]["n_tautology_facts"] == 0 and arms[a]["n_closed_class_object_facts"] == 0
        and not arms[a]["no_leak_violations"] for a in arms)

    # ---- S3 ARMS-MUST-DIFFER (META_RULE_AF)
    digests = {a: arms[a]["pairs_digest"] for a in arms}
    s3 = len(arms) == len(ARMS) and len(sorted(set(digests.values()))) == len(ARMS)

    # ---- S4 backward-compat (foundations load unchanged; readout=None path untouched)
    s4_detail = _s4_backward_compat()
    s4 = bool(s4_detail["ok"])

    # ---- S5 confirm-rate calibration, positive-controlled on BASE
    base_cr = arms.get("PBV_BASE", {}).get("confirm_rate")
    f13_cr = arms.get("PBV_F1F3", {}).get("confirm_rate")
    s5 = base_cr is not None and abs(base_cr - S5_PBV_CONFIRM_RATE_CITED) <= S5_TOLERANCE
    confirm_rate_calibrated = bool(s5)

    # ---- S6 yield floor
    s6 = bool(arms) and all(arms[a]["n_meaning_facts"] >= S6_YIELD_FLOOR for a in arms)

    # ---- S7 F3 memory cap
    peak_bytes = int(arms.get("PBV_F1F3", {}).get("freeze_stats", {})
                     .get("peak_live_snapshot_bytes", 0))
    s7 = peak_bytes <= S7_PEAK_SNAPSHOT_BYTES_CAP

    # ---- S8 F1 admission drift vs the 0.403405 the threshold was retention-matched at
    adm = arms.get("PBV_F1F3", {}).get("admission_rate")
    adm_base = arms.get("PBV_BASE", {}).get("admission_rate")
    drift = round(adm - S8_MATCHED_RETENTION, 6) if adm is not None else None
    retention_ratio_here = (round(adm / adm_base, 6)
                            if (adm is not None and adm_base) else None)
    retention_match_holds = drift is not None and abs(drift) <= S8_DRIFT_VOIDS_MATCH

    # ---- prereg sec 3.2 SELECTIVITY CAP (machine-checkable, computed BEFORE any quality score)
    nb = arms.get("PBV_BASE", {}).get("n_meaning_facts")
    nf = arms.get("PBV_F1F3", {}).get("n_meaning_facts")
    sel_ratio = round(nf / nb, 6) if (nb and nf is not None) else None
    sel_ok = sel_ratio is not None and SELECTIVITY_BAND[0] <= sel_ratio <= SELECTIVITY_BAND[1]

    gb = arms.get("PBV_BASE", {}).get("grounded_objects", {})
    gf = arms.get("PBV_F1F3", {}).get("grounded_objects", {})
    both = sorted(set(gb) & set(gf))
    agree = sum(1 for l in both if gb[l] == gf[l])

    samples = None
    if len(arms) == len(ARMS):
        samples = write_audit_samples(output_dir, arms)

    gates = {"S1_cardinality": s1, "S2_integrity": s2, "S3_arms_differ": s3,
             "S4_backward_compat": s4, "S6_yield_floor": s6, "S7_f3_memory": s7}
    hard_fail = [k for k, v in gates.items() if not v]
    if hard_fail:
        verdict = "HARD_FAIL"
        verdict_msg = ("STRUCTURAL gate(s) failed: " + ", ".join(hard_fail) +
                       " -- the blind sample is NOT fit to hand-score. No quality claim.")
    else:
        verdict = "STRUCTURAL_PASS_PENDING_B3"
        verdict_msg = (
            f"structural gates pass; {samples['n_blind_rows'] if samples else 0} blind rows "
            f"written for the director's hand-score. THIS CELL MAKES NO QUALITY CLAIM. "
            f"S5_confirm_calibrated={confirm_rate_calibrated} (BASE {base_cr} vs cited "
            f"{S5_PBV_CONFIRM_RATE_CITED}); selectivity n_F1F3/n_BASE={sel_ratio} "
            f"(cap band {SELECTIVITY_BAND}, ok={sel_ok}); S8 admission {adm} drift {drift} "
            f"(retention-match holds={retention_match_holds}).")

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "prereg": PREREG,
        "wire_status": "VET_PENDING",
        "verdict": verdict, "verdict_msg": verdict_msg,
        "QUALITY_CLAIM": "NONE -- this cell emits no quality tier. The primary discriminator is a "
                         "BLIND HUMAN HAND-SCORE the director performs on blind_sample.json. "
                         "Read-out stability and meaning quality may be fully decoupled; the NULL "
                         "outcome is pre-registered as LIVE and ACCEPTABLE (prereg sec 3.1).",
        "quality_bands_recorded_not_evaluated": QUALITY_BANDS_RECORDED,
        "structural_gates": {
            "S1_cardinality": {"ok": s1, "expected_n_units": EXPECTED_N_UNITS,
                               "n_present": len(present_units), "missing_units": missing_units,
                               "missing_arms": missing_arms},
            "S2_integrity": {"ok": s2, "per_arm": {
                a: {"n_tautology_facts": arms[a]["n_tautology_facts"],
                    "n_closed_class_object_facts": arms[a]["n_closed_class_object_facts"],
                    "no_leak_violations": arms[a]["no_leak_violations"]} for a in arms}},
            "S3_arms_differ": {"ok": s3, "digests": digests},
            "S4_backward_compat": dict(s4_detail, ok=s4),
            "S5_confirm_rate_calibration": {
                "ok": s5, "confirm_rate_calibrated": confirm_rate_calibrated,
                "cited_pbv_confirm_rate": S5_PBV_CONFIRM_RATE_CITED,
                "cited_source": "data/exp_pbv_hypothesis_v1_smoke/metrics.json:"
                                "arms.B_PBV.trajectory (788 / (788+7048))",
                "tolerance": S5_TOLERANCE,
                "PBV_BASE_confirm_rate": base_cr, "PBV_F1F3_confirm_rate": f13_cr,
                "note": "If not calibrated, every confirm-rate number here is "
                        "WITHIN_CELL_RELATIVE_ONLY and NO claim is made against the 0.101 gate. "
                        "A confirm-rate RISE under F1F3 is expected on STABILITY grounds alone "
                        "and is NOT evidence of better meanings (prereg sec 5)."},
            "S6_yield_floor": {"ok": s6, "floor": S6_YIELD_FLOOR,
                               "per_arm": {a: arms[a]["n_meaning_facts"] for a in arms}},
            "S7_f3_memory": {"ok": s7, "peak_live_snapshot_bytes": peak_bytes,
                             "cap_bytes": S7_PEAK_SNAPSHOT_BYTES_CAP,
                             "freeze_stats": arms.get("PBV_F1F3", {}).get("freeze_stats")},
            "S8_f1_admission_drift": {
                "reported_only": True,
                "matched_retention_cited": S8_MATCHED_RETENTION,
                "PBV_F1F3_admission_rate": adm, "PBV_BASE_admission_rate": adm_base,
                "drift": drift, "retention_ratio_F1F3_over_BASE": retention_ratio_here,
                "retention_match_holds": retention_match_holds,
                "note": "drift > 0.10 voids the 'retention-matched' claim; the sec 3.2 cap then "
                        "applies to any later quality delta."},
        },
        "selectivity_cap": {
            "n_facts_PBV_BASE": nb, "n_facts_PBV_F1F3": nf, "ratio_F1F3_over_BASE": sel_ratio,
            "band": list(SELECTIVITY_BAND), "within_band": sel_ok,
            "n_lemmas_grounded_by_both": len(both), "n_agree_on_object": agree,
            "object_agreement_rate": round(agree / len(both), 6) if both else None,
            "note": "OUTSIDE the band, any later quality delta is CONFOUNDED WITH SELECTIVITY and "
                    "the verdict is CAPPED AT MIDDLE_BAND regardless of its size (prereg 3.2)."},
        "objective_metrics": {
            a: {k: arms[a][k] for k in ("n_sentences", "n_chunks", "n_grounded",
                                        "n_meaning_facts", "n_refusals", "refusal_reasons",
                                        "confirm_rate", "n_verdict_bearing", "admission_rate",
                                        "trajectory", "freeze_stats", "pairs_digest",
                                        "segments_seen", "elapsed_s")} for a in arms},
        "config": {"N_DIM": N_DIM, "CHUNK_SIZE": CHUNK_SIZE, "ARM_SEED": ARM_SEED,
                   "SCHEMA_THRESH_FULL": SCHEMA_THRESH_FULL,
                   "PBV_INFORMATIVE_MIN": PBV_INFORMATIVE_MIN,
                   "PBV_COMMIT_STRENGTH": PBV_COMMIT_STRENGTH,
                   "F1_margin_z_min": OPERATING_MARGIN_Z_MIN,
                   "F1_margin_stat": OPERATING_MARGIN_STAT,
                   "F1_source": OPERATING_MARGIN_Z_MIN_SOURCE,
                   "F2_anchor_background": "SHELVED_OFF",
                   "F3_epoch_granularity": f"one snapshot per {CHUNK_SIZE}-sentence chunk",
                   "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
                   "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
                   "corpus": "experiments.exp_definitional_grounding_v5.load_corpus_v5("
                             f"{'None' if run_mode == 'full' else SMOKE_LIMIT_PER_SEGMENT}, "
                             "lineaware=True)"},
        "deliverable": samples,
        "limitations": [
            "THIS CELL MEASURES NO QUALITY. Everything it emits is structural or a stability/"
            "selectivity control. The quality question is answered ONLY by the blind hand-score.",
            "F3 is run at EPOCH (per-150-sentence-chunk) granularity, a DECLARED COARSENING "
            "(prereg sec 6): true per-episode freeze extrapolates past 50 GB on this corpus and "
            "is not runnable. It is coarser than per-episode and strictly FINER than the "
            "5-snapshot granularity at which F3's confirmed -0.168 was measured.",
            "F1 is a stability selector only. The landed-VET refuted it as an informativeness / "
            "lemma-specificity gate (AUC 0.5067, real-vs-scramble enrichment 1.0000x). Nothing "
            "in F1 or F3 supplies REFERENCE.",
            "the proposer's metric is still distributional relatedness, not reference -- if the "
            "hand-score comes back NULL, the pre-registered reading is that the read-out was "
            "never the binding constraint (prereg sec 3.1).",
            "n=50 per arm: SE(delta) ~ 0.10. Deltas below ~0.20 are pre-declared unresolvable.",
        ],
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
    return metrics


def _s4_backward_compat() -> dict:
    """S4: the two pre-existing foundations load unchanged, and the readout=None path is
    untouched (asserted structurally in self_test; here we only exercise the loads)."""
    from hdlab.foundation_persistence import load_foundation
    out = {"checked": [], "errors": []}
    for name in ("reading_grounding_v1", "reading_grounding_v2_qualityfix"):
        p = repo_path(os.path.join("data", "foundation", name))
        if not os.path.isdir(p):
            out["errors"].append(f"{name}: missing on disk")
            continue
        try:
            st = load_foundation(p)
            out["checked"].append({"name": name, "n_live_facts": len(st.store.live_facts()),
                                   "n_anchors": len(st.space.anchors())})
        except SystemExit:
            raise
        except Exception as exc:                      # noqa: BLE001 -- recorded, not swallowed
            out["errors"].append(f"{name}: {type(exc).__name__}: {exc}")
    out["ok"] = not out["errors"] and len(out["checked"]) == 2
    return out


# =========================================================================== self-test
def self_test() -> dict:
    """Fast off-disk gate on the REAL code path at tiny N (no corpus read)."""
    from hdlab.reading_grounding_loop import _pbv_fixture, ReadoutConfig

    # (1) F2 MUST stay shelved-off in the operating config.
    cfg = operating_readout()
    assert isinstance(cfg, ReadoutConfig) and cfg.anchor_background is None, cfg
    assert cfg.margin_z_min == OPERATING_MARGIN_Z_MIN and cfg.margin_stat == OPERATING_MARGIN_STAT

    # (2) the two arms must actually take DIFFERENT code paths on the same fixture.
    def _run(arm: str) -> Tuple[str, dict]:
        state, sents, _ = _pbv_fixture(seed=5150)
        holder = {"chunk": 0}
        p, v = _make_fns(arm, state, holder)
        for i, s in enumerate(sents):
            process_sentence(state, s, f"{arm}_s{i}", pass_idx=0, pbv_fns=(p, v))
        return _digest_pairs((l, it.hypothesis.obj) for l, it in state.library.items.items()
                             if it.hypothesis is not None), p.freeze_stats()

    d_base, fs_base = _run("PBV_BASE")
    d_f13, fs_f13 = _run("PBV_F1F3")
    assert fs_base["freeze_episode"] is False and fs_base["readout_active"] is False, fs_base
    assert fs_f13["freeze_episode"] is True and fs_f13["readout_active"] is True, fs_f13
    assert fs_f13["epoch_interned"] is True and fs_f13["n_snapshots_created"] >= 1, fs_f13
    assert fs_f13["readout_f2_anchor_background_on"] is False, fs_f13

    # (3) sampling convention is reproducible and label-free.
    prov = [{"fid": i, "subject": f"w{i}", "relation": MEANING_RELATION, "object": f"o{i}",
             "segment": "bootstrap", "n_exposures": 2, "best_cos": 0.5, "schema_score": 0.3,
             "evidence": [{"sentence": f"sent {i}"}], "hypothesis": {}} for i in range(120)]
    r1 = _sample_rows(prov, "PBV_BASE")
    r2 = _sample_rows(prov, "PBV_BASE")
    assert len(r1) == SAMPLE_N and [r["fid"] for r in r1] == [r["fid"] for r in r2]
    assert all("arm" not in r for r in r1), "blind rows must carry NO arm label"
    assert sorted(r1[0].keys()) == sorted(r2[0].keys())

    return {"f2_shelved_off_ok": True, "arms_take_different_paths_ok": True,
            "fixture_digests_differ": d_base != d_f13,
            "fixture_digest_base": d_base[:16], "fixture_digest_f1f3": d_f13[:16],
            "sampling_deterministic_ok": True, "rows_carry_no_arm_label_ok": True,
            "note": "fixture_digests_differ is INFORMATIONAL at fixture scale (a 3-sentence "
                    "fixture may not exercise the gate); the binding check is S3 on the real run."}


# =========================================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--arm", choices=ARMS + ["finalize", "all"], default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2))
        print("ALL SELF-TESTS PASSED")
        return

    output_dir = _output_dir(args.mode)
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, args.mode, args.arm)
    try:
        todo = ARMS + ["finalize"] if args.arm in (None, "all") else [args.arm]
        for a in todo:
            if a == "finalize":
                m = finalize(args.mode, output_dir)
                print(json.dumps({k: m[k] for k in ("verdict", "verdict_msg", "structural_gates",
                                                    "selectivity_cap", "deliverable")},
                                 indent=2), flush=True)
                continue
            res = run_arm(a, args.mode, output_dir)
            print(f"[arm-done] {a} grounded={res['n_grounded']} "
                  f"facts={res['n_meaning_facts']} confirm_rate={res['confirm_rate']} "
                  f"elapsed={res['elapsed_s']}s", flush=True)
    except SystemExit:
        raise
    except Exception as exc:
        diag = {"anchor_name": ANCHOR_NAME, "run_mode": args.mode, "arm": args.arm,
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
                "ts_iso": datetime.now(timezone.utc).isoformat()}
        _atomic_json(os.path.join(output_dir, "_crash_diagnostic.json"), diag)
        raise


if __name__ == "__main__":
    main()
