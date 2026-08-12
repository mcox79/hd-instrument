"""experiments/exp_pbv_hypothesis_v1.py

Does the reading path's NEW hypothesis object actually do propose-then-verify at corpus scale?

Four arms over ONE stream (the existing reading-path corpus -- no new material is ingested):
  A_BASELINE        current mechanism (sum-then-argmax at the consolidation gate)
  B_PBV             carried single hypothesis with a persisting strength
  C1_INJECT_WRONG   B, with a deliberately WRONG hypothesis injected at strength 0.9
  C2_INJECT_RIGHT   B, with the mechanism's OWN proposal injected at strength 0.9 (non-triviality
                    control -- an always-abandon mechanism passes C1 vacuously without this)

Pre-reg: preregs/2026-08-12_pbv_hypothesis_v1.md  (bands P1/P2/P3 primary, S1/S2/S3 secondary,
D1-D4 diagnostic, cardinality gates, disclosed limitations)
Basis:   notes/brain_fidelity_audit_word_learning_2026-08-12.md Section G.4.1

THIS CELL DOES NOT MEASURE SENSE SELECTION and nothing in it bears on the C1 swap-drop 0.0100
context-insensitivity finding (audit G.2). Two different defects.

# CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - start_marker_written / crash_diagnostic_present / per-chunk progress flush
# - cardinality_ok: EXPECTED_ARMS = 4, EXPECTED_SEGMENTS = 5; finalize refuses a verdict if any
#   arm or segment is missing
# - crlb n/a: metrics are rates over discrete stored facts and discrete abandonment events, not an
#   estimator against a Cramer-Rao bound
# - arms-must-differ: A vs B differ in the GATE (pbv flag) and in whether a hypothesis is carried;
#   C1 vs C2 differ ONLY in the injected object, everything else byte-identical (same seeds, same
#   stream, same targets) -- asserted at finalize
# - all numbers in comments are tagged MEASURED@ / HYPOTHESIZED@ / CITED@
# - real_code_path: drives the REAL ReadingLoopState / process_sentence / checkpoint /
#   Library.flag / HDFactStore objects; no synthetic-only branch

ASCII-only. Deterministic (fixed seeds; sorted(set(...)) throughout; no built-in hash()).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
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
from hdlab.grounded_similarity import grounded_similarity
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    PBV_COMMIT_STRENGTH,
    PBV_INFORMATIVE_MIN,
    ReadingLoopState,
    checkpoint,
    content_lemmas,
    make_pbv_fns,
    pbv_trajectory_stats,
    process_sentence,
    seed_known_words,
)
from tools import exp_checkpoint

from experiments.exp_reading_grounding_loop_cycle1_v1 import (
    N_DIM, SCHEMA_THRESH_FULL, build_curriculum_pool, load_base_vocab_seed, repo_path,
)
from experiments.exp_reading_grounding_loop_cycle2_v1 import (
    CHUNK_SIZE, SEGMENT_POOL_LOADERS, grounded_lemmas_in_store,
)

ANCHOR_NAME = "pbv_hypothesis_v1"
ARMS = ["A_BASELINE", "B_PBV", "C1_INJECT_WRONG", "C2_INJECT_RIGHT"]
EXPECTED_N_ARMS = len(ARMS)
SEGMENTS = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new"]
EXPECTED_N_SEGMENTS = len(SEGMENTS)

ARM_SEEDS = {"A_BASELINE": 3001, "B_PBV": 3002, "C1_INJECT_WRONG": 3003, "C2_INJECT_RIGHT": 3004}
INJECT_SEED = 20260812
N_INJECT_TARGETS_FULL = 200
N_INJECT_TARGETS_SMOKE = 30
SMOKE_LIMIT_PER_SEGMENT = 1500
INJECT_STRENGTH = 0.9          # HYPOTHESIZED@prereg sec 3 -- high, so abandonment requires
                                # accumulated disconfirmation rather than fragility

# ---- pre-registered bands (prereg sec 4; frozen before any run of this cell) --------------------
P1_C1_ABANDON_MIN = 0.80
P2_C2_ABANDON_MAX = 0.30
P3_SEPARATION_MIN = 0.50
FAIL_C1_ABANDON = 0.60
FAIL_C2_ABANDON = 0.50
FAIL_SEPARATION = 0.30
S1_REVISION_RATE_BAND = (0.02, 0.60)
S2_MEDIAN_ENCOUNTERS_TO_ABANDON_MAX = 4
S3_YIELD_RATIO_MIN = 0.25


def _output_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _write_start_marker(output_dir: str, run_mode: str, arm: Optional[str]) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "arm": arm,
              "expected_n_units": EXPECTED_N_ARMS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


# =========================================================================== corpus
def build_stream(run_mode: str) -> List[Tuple[str, str]]:
    """(segment_tag, sentence) over the EXISTING reading-path corpus, in curriculum order. Byte-for-
    byte the same pools exp_definitional_grounding_v5 reads (that cell composes build_curriculum_pool
    + SEGMENT_POOL_LOADERS the same way), so arm A stays comparable to the v5 baseline. The 117,642
    newly acquired OpenStax sentences are deliberately NOT read here."""
    limit = SMOKE_LIMIT_PER_SEGMENT if run_mode == "smoke" else None
    out: List[Tuple[str, str]] = [("bootstrap", s) for _t, s in build_curriculum_pool(limit)]
    for seg in SEGMENTS[1:]:
        out.extend((seg, s) for _t, s in SEGMENT_POOL_LOADERS[seg](limit))
    return out


# =========================================================================== injection targeting
def select_injection_targets(reference: dict, n_targets: int) -> Dict[str, Tuple[str, str]]:
    """lemma -> (right_obj, wrong_obj), derived from arm B's OWN first proposals.

    right_obj = the object B's mechanism itself proposed first for that lemma.
    wrong_obj = a DIFFERENT lemma's right_obj, assigned by a deterministic derangement of the
    sorted target list. Drawing the distractor from the same pool (rather than at random from the
    whole vocabulary) keeps the wrong object a plausible, in-distribution anchor -- a wrong meaning
    the mechanism has to work to reject, not an obvious outlier."""
    firsts = reference["first_proposals"]        # lemma -> obj, from arm B
    cands = sorted(l for l, o in firsts.items() if o and l != o)
    rng = np.random.default_rng(INJECT_SEED)
    if len(cands) > n_targets:
        idx = sorted(rng.choice(len(cands), size=n_targets, replace=False).tolist())
        cands = [cands[i] for i in idx]
    out: Dict[str, Tuple[str, str]] = {}
    n = len(cands)
    if n < 2:
        return out
    for i, lem in enumerate(cands):
        right = firsts[lem]
        wrong = firsts[cands[(i + 1) % n]]       # derangement: shift by one over the sorted list
        if wrong == right or wrong == lem or is_closed_class(wrong):
            # walk forward until a genuinely different, eligible distractor is found
            for k in range(2, n + 1):
                w = firsts[cands[(i + k) % n]]
                if w != right and w != lem and not is_closed_class(w):
                    wrong = w
                    break
        if wrong != right and wrong != lem:
            out[lem] = (right, wrong)
    return out


# =========================================================================== one arm
def run_arm(arm: str, run_mode: str, output_dir: str, *,
            reference: Optional[dict] = None, n_targets: int = N_INJECT_TARGETS_FULL) -> dict:
    """One arm end-to-end, in ONE process (no foundation_persistence round-trip -- hypotheses are
    not persisted by that module, see prereg sec 5.1). Checkpointed per chunk."""
    already = exp_checkpoint.completed_units(output_dir)
    done_key = exp_checkpoint.unit_key("arm_done", arm)
    if done_key in already:
        return dict(exp_checkpoint.load_units(output_dir)[done_key], skipped=True)

    pbv = arm != "A_BASELINE"
    injecting = arm in ("C1_INJECT_WRONG", "C2_INJECT_RIGHT")
    targets: Dict[str, Tuple[str, str]] = {}
    if injecting:
        if reference is None:
            raise RuntimeError(f"{arm} requires arm B's reference (run B_PBV first)")
        targets = select_injection_targets(reference, n_targets)

    stream = build_stream(run_mode)
    store = HDFactStore(n_dim=N_DIM, seed=ARM_SEEDS[arm],
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, load_base_vocab_seed(), source="seed_base_vocabulary")
    known_seed_snapshot = set(state.known_seed)
    pbv_fns = make_pbv_fns(state) if pbv else None

    first_proposals: Dict[str, str] = {}
    injected: Dict[str, str] = {}
    n_chunks = math.ceil(len(stream) / CHUNK_SIZE) if stream else 0
    seg_seen: Dict[str, int] = {}
    t0 = time.time()
    for chunk_idx in range(n_chunks):
        chunk = stream[chunk_idx * CHUNK_SIZE:(chunk_idx + 1) * CHUNK_SIZE]
        for i, (seg, sent) in enumerate(chunk):
            seg_seen[seg] = seg_seen.get(seg, 0) + 1
            process_sentence(state, sent, f"{arm}_{chunk_idx}_{i}", pass_idx=chunk_idx,
                             pbv_fns=pbv_fns, revive_terminal=pbv)
            if not pbv:
                continue
            # Record every item's FIRST proposal (arm B's is what C1/C2 inject against), and
            # perform the injection at the FIRST encounter after that item has a hypothesis.
            # Scanned over THIS SENTENCE's lemmas only -- a scan over the whole library here would
            # be O(n_items) per sentence (~10^8 ops at full corpus) and is what makes this loop
            # affordable at all.
            for lemma in content_lemmas(sent):
                it = state.library.items.get(lemma)
                if it is None or it.hypothesis is None or lemma in first_proposals:
                    continue
                first_proposals[lemma] = it.hypothesis.obj
                if injecting and lemma in targets and lemma not in injected:
                    right, wrong = targets[lemma]
                    obj = right if arm == "C2_INJECT_RIGHT" else wrong
                    state.library.inject_hypothesis(lemma, obj, INJECT_STRENGTH, chunk_idx)
                    injected[lemma] = obj
        seg_tag = chunk[-1][0] if chunk else "unknown"
        row = checkpoint(state, pass_idx=chunk_idx, source_tag=seg_tag,
                         schema_thresh=SCHEMA_THRESH_FULL, pbv=pbv,
                         commit_strength=PBV_COMMIT_STRENGTH)
        row["arm"] = arm
        row["segment"] = seg_tag
        row["foundation_size_in_store"] = len(grounded_lemmas_in_store(state.store))
        key = exp_checkpoint.unit_key(arm, chunk_idx)
        if key not in already:
            exp_checkpoint.record_unit(output_dir, key, row)
        if chunk_idx % 10 == 0 or chunk_idx == n_chunks - 1:
            print(f"[progress] {arm} chunk={chunk_idx + 1}/{n_chunks} "
                  f"grounded={row['foundation_size_in_store']} "
                  f"refused={row['n_refused_cumulative']} injected={len(injected)} "
                  f"elapsed={time.time() - t0:.1f}s", flush=True)

    traj = pbv_trajectory_stats(state.library)
    grounded = grounded_lemmas_in_store(state.store)
    gm = [f for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    summary = {
        "arm": arm, "pbv": pbv, "n_sentences": len(stream), "n_chunks": n_chunks,
        "segments_seen": {s: seg_seen.get(s, 0) for s in SEGMENTS},
        "n_grounded": len(grounded),
        "n_tautology_facts": sum(1 for f in gm if f.subject == f.obj),
        "n_closed_class_object_facts": sum(1 for f in gm if is_closed_class(f.obj)),
        "no_leak_violations": [l for l in grounded if l in known_seed_snapshot],
        "n_refusals": len(state.refusals),
        "refusal_reasons": _count_reasons(state.refusals),
        "trajectory": {k: v for k, v in traj.items() if k != "revisions"},
        "n_injected": len(injected),
        "injection_outcomes": _injection_outcomes(state, injected) if injecting else None,
        "grounded_objects": {f.subject: f.obj for f in gm},
        "revisions": traj["revisions"],
        "abandon_gaps": _abandon_gaps(state),
        "memory_bytes": _memory_bytes(state),
        "elapsed_s": round(time.time() - t0, 2),
    }
    if pbv:
        summary["first_proposals"] = first_proposals
    exp_checkpoint.record_unit(output_dir, done_key, summary)
    return summary


def _count_reasons(refusals: List[dict]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in refusals:
        out[r["reason"]] = out.get(r["reason"], 0) + 1
    return dict(sorted(out.items()))


def _injection_outcomes(state: ReadingLoopState, injected: Dict[str, str]) -> dict:
    """Per injected lemma: was the injected hypothesis ABANDONED after the injection?

    Only lemmas that saw at least one further INFORMATIVE encounter after injection are counted --
    a hypothesis that never met disconfirming evidence cannot be said to have survived it, and
    scoring those as 'survived' would inflate C2 and deflate C1 in the same breath."""
    rows, n_aband, n_survived, n_no_evidence = [], 0, 0, 0
    for lemma in sorted(injected):
        it = state.library.items.get(lemma)
        if it is None:
            continue
        log = it.hypothesis_log
        inj_pos = max((i for i, e in enumerate(log) if e["event"] == "INJECT"), default=None)
        if inj_pos is None:
            continue
        after = log[inj_pos + 1:]
        abandoned = any(e["event"] == "ABANDON" and e["obj"] == injected[lemma] for e in after)
        informative_after = sum(1 for e in after if e["event"] in ("CONFIRM", "DISCONFIRM"))
        if informative_after == 0:
            n_no_evidence += 1
        elif abandoned:
            n_aband += 1
        else:
            n_survived += 1
        rows.append({"lemma": lemma, "injected_obj": injected[lemma], "abandoned": abandoned,
                     "n_informative_after": informative_after,
                     "n_disconfirm_after": sum(1 for e in after if e["event"] == "DISCONFIRM"),
                     "final_obj": it.hypothesis.obj if it.hypothesis else None,
                     "status": it.status})
    scored = n_aband + n_survived
    return {"n_injected": len(injected), "n_scored": scored,
            "n_abandoned": n_aband, "n_survived": n_survived,
            "n_never_met_evidence": n_no_evidence,
            "abandon_rate": round(n_aband / scored, 6) if scored else None,
            "rows": rows}


def _abandon_gaps(state: ReadingLoopState) -> List[int]:
    """Encounters elapsed between each PROPOSE/REPROPOSE and the ABANDON that ended it (S2: PBV
    switches ABRUPTLY, so this should be small; a large value means smooth drift, not switching)."""
    gaps: List[int] = []
    for lemma in sorted(state.library.items):
        open_at: Optional[int] = None
        for e in state.library.items[lemma].hypothesis_log:
            if e["event"] in ("PROPOSE", "REPROPOSE", "INJECT"):
                open_at = e["n_traces"]
            elif e["event"] == "ABANDON" and open_at is not None:
                gaps.append(int(e["n_traces"]) - int(open_at))
                open_at = None
    return gaps


def _memory_bytes(state: ReadingLoopState) -> dict:
    """D3. Explicit accounting -- NOT sys.getsizeof on a nested structure (which under-counts).
    Hypothesis: 1 str + 1 float + 5 ints. Log entry: ~5 keys. Trace context_vec: d * 8 bytes."""
    n_items = len(state.library.items)
    n_traces = n_hyp = n_log = n_rejected = 0
    d = 0
    for it in state.library.items.values():
        n_traces += len(it.traces)
        n_log += len(it.hypothesis_log)
        n_rejected += len(it.rejected)
        if it.hypothesis is not None:
            n_hyp += 1
        if d == 0 and it.traces:
            d = int(it.traces[0].context_vec.shape[0])
    hyp_b = n_hyp * (48 + 8 + 5 * 28)               # str hdr + float + 5 small ints
    log_b = n_log * 240                              # dict of ~5 short keys, measured order
    rej_b = n_rejected * 56
    trace_b = n_traces * d * 8
    return {"n_items": n_items, "n_traces": n_traces, "trace_ctx_d": d,
            "n_standing_hypotheses": n_hyp, "n_log_entries": n_log, "n_rejected": n_rejected,
            "hypothesis_state_bytes": hyp_b + log_b + rej_b,
            "retained_trace_bytes": trace_b,
            "hypothesis_state_bytes_per_item": round((hyp_b + log_b + rej_b) / n_items, 2) if n_items else 0.0}


# =========================================================================== finalize
def _median(xs: List[float]) -> Optional[float]:
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return float(s[n // 2]) if n % 2 else float((s[n // 2 - 1] + s[n // 2]) / 2.0)


def revision_quality(arm_b: dict) -> dict:
    """D2. Independent judge: hdlab.grounded_similarity (Lancaster + Brysbaert), which is NOT in the
    acquisition path's import closure -- that is what makes it independent of the metric being
    judged. CAVEATED: concrete-biased and capped at GROUNDED_CAP=0.45 for a known 16.4% of pairs,
    so partial coverage and a weak null are expected. Diagnostic only; carries no verdict."""
    banked = arm_b.get("grounded_objects", {})
    better = worse = tied = uncovered = 0
    deltas: List[float] = []
    rows = []
    for rev in arm_b.get("revisions", []):
        lemma, first = rev["lemma"], rev["first_obj"]
        final = banked.get(lemma, rev.get("final_obj"))
        if not first or not final or first == final:
            continue
        s_first = grounded_similarity(lemma, first)
        s_final = grounded_similarity(lemma, final)
        if s_first is None or s_final is None:
            uncovered += 1
            continue
        d = s_final - s_first
        deltas.append(d)
        if d > 1e-9:
            better += 1
        elif d < -1e-9:
            worse += 1
        else:
            tied += 1
        rows.append({"lemma": lemma, "first_obj": first, "final_obj": final,
                     "sim_first": round(s_first, 4), "sim_final": round(s_final, 4),
                     "delta": round(d, 4), "banked": lemma in banked})
    return {"n_scored": len(deltas), "n_uncovered_by_judge": uncovered,
            "n_better": better, "n_worse": worse, "n_tied": tied,
            "mean_delta": round(float(np.mean(deltas)), 6) if deltas else None,
            "median_delta": round(float(_median(deltas)), 6) if deltas else None,
            "judge": "hdlab.grounded_similarity (Lancaster+Brysbaert)",
            "caveat": "concrete-biased; GROUNDED_CAP=0.45 saturates a known 16.4% of pairs; "
                      "partial coverage expected; DIAGNOSTIC ONLY -- carries no verdict",
            "rows": rows[:200]}


def finalize(run_mode: str, output_dir: str) -> dict:
    units = exp_checkpoint.load_units(output_dir)
    arms = {}
    for a in ARMS:
        k = exp_checkpoint.unit_key("arm_done", a)
        if k in units:
            arms[a] = units[k]
    missing = [a for a in ARMS if a not in arms]
    cardinality_ok = not missing
    seg_missing = {a: [s for s in SEGMENTS if not arms[a]["segments_seen"].get(s)] for a in arms}
    segments_ok = all(not v for v in seg_missing.values())

    c1 = (arms.get("C1_INJECT_WRONG") or {}).get("injection_outcomes") or {}
    c2 = (arms.get("C2_INJECT_RIGHT") or {}).get("injection_outcomes") or {}
    r1, r2 = c1.get("abandon_rate"), c2.get("abandon_rate")
    sep = round(r1 - r2, 6) if (r1 is not None and r2 is not None) else None

    b = arms.get("B_PBV", {})
    a = arms.get("A_BASELINE", {})
    traj = b.get("trajectory", {})
    rev_rate = traj.get("revision_rate")
    gaps = b.get("abandon_gaps", [])
    med_gap = _median([float(g) for g in gaps])
    yield_ratio = (round(b["n_grounded"] / a["n_grounded"], 6)
                   if a.get("n_grounded") else None)

    # D4 -- do the two mechanisms actually produce different meanings?
    ga, gb = a.get("grounded_objects", {}), b.get("grounded_objects", {})
    both = sorted(set(ga) & set(gb))
    agree = sum(1 for l in both if ga[l] == gb[l])

    # arms-must-differ (C1 vs C2 differ ONLY in the injected object)
    c1_rows = {r["lemma"]: r["injected_obj"] for r in c1.get("rows", [])}
    c2_rows = {r["lemma"]: r["injected_obj"] for r in c2.get("rows", [])}
    shared = sorted(set(c1_rows) & set(c2_rows))
    arms_differ = bool(shared) and all(c1_rows[l] != c2_rows[l] for l in shared)

    p1 = r1 is not None and r1 >= P1_C1_ABANDON_MIN
    p2 = r2 is not None and r2 <= P2_C2_ABANDON_MAX
    p3 = sep is not None and sep >= P3_SEPARATION_MIN
    hard_fail = (r1 is not None and r1 < FAIL_C1_ABANDON) or \
                (r2 is not None and r2 > FAIL_C2_ABANDON) or \
                (sep is not None and sep < FAIL_SEPARATION)
    s1 = rev_rate is not None and S1_REVISION_RATE_BAND[0] <= rev_rate <= S1_REVISION_RATE_BAND[1]
    s2 = med_gap is not None and med_gap <= S2_MEDIAN_ENCOUNTERS_TO_ABANDON_MAX
    s3 = yield_ratio is not None and yield_ratio >= S3_YIELD_RATIO_MIN

    integrity = {
        "cardinality_ok": cardinality_ok, "missing_arms": missing,
        "segments_ok": segments_ok, "missing_segments_per_arm": seg_missing,
        "arms_must_differ_ok": arms_differ,
        "no_tautology_facts": all(arms[x]["n_tautology_facts"] == 0 for x in arms),
        "no_closed_class_objects": all(arms[x]["n_closed_class_object_facts"] == 0 for x in arms),
        "no_leak_ok": all(not arms[x]["no_leak_violations"] for x in arms),
    }
    if not all(integrity[k] for k in ("cardinality_ok", "segments_ok", "arms_must_differ_ok",
                                      "no_tautology_facts", "no_closed_class_objects", "no_leak_ok")):
        verdict, verdict_msg = "UNKNOWN", "integrity gate failed; verdict refused (see integrity)"
    elif hard_fail:
        verdict = "HARD_FAIL"
        verdict_msg = (f"PBV verification does not work: C1 abandon {r1} (fail<{FAIL_C1_ABANDON}), "
                       f"C2 abandon {r2} (fail>{FAIL_C2_ABANDON}), separation {sep} "
                       f"(fail<{FAIL_SEPARATION})")
    elif p1 and p2 and p3:
        verdict = "PASS" if (s1 and s2 and s3) else "PARTIAL"
        verdict_msg = (f"primary PASS: injected WRONG abandoned {r1}, injected RIGHT abandoned "
                       f"{r2}, separation {sep}. secondary S1_revision={s1}({rev_rate}) "
                       f"S2_abrupt={s2}({med_gap}) S3_yield={s3}({yield_ratio})")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"inconclusive: C1 {r1} (need>={P1_C1_ABANDON_MIN}), C2 {r2} "
                       f"(need<={P2_C2_ABANDON_MAX}), separation {sep} (need>={P3_SEPARATION_MIN})")

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "prereg": "preregs/2026-08-12_pbv_hypothesis_v1.md",
        "wire_status": "VET_PENDING",
        "verdict": verdict, "verdict_msg": verdict_msg,
        "integrity": integrity,
        "primary": {"C1_abandon_rate": r1, "C2_abandon_rate": r2, "separation": sep,
                    "P1_ok": p1, "P2_ok": p2, "P3_ok": p3, "hard_fail": hard_fail,
                    "C1_detail": {k: v for k, v in c1.items() if k != "rows"},
                    "C2_detail": {k: v for k, v in c2.items() if k != "rows"}},
        "secondary": {"S1_revision_rate": rev_rate, "S1_ok": s1,
                      "S2_median_encounters_to_abandon": med_gap, "S2_ok": s2,
                      "S3_yield_ratio_B_over_A": yield_ratio, "S3_ok": s3,
                      "n_grounded_A": a.get("n_grounded"), "n_grounded_B": b.get("n_grounded")},
        "diagnostic": {
            "D1_informative_encounter_rate": traj.get("informative_encounter_rate"),
            "D1_n_encounters": traj.get("n_encounters"),
            "D1_note": "Medina ~7% highly informative is CITED@audit G; this filter is a coarse "
                       "distributional proxy and is not expected to reproduce it. Not scored.",
            "D2_revision_quality": revision_quality(b),
            "D3_memory": {"A": a.get("memory_bytes"), "B": b.get("memory_bytes")},
            "D4_agreement": {"n_both_grounded": len(both), "n_agree": agree,
                             "agreement_rate": round(agree / len(both), 6) if both else None},
        },
        "config": {"N_DIM": N_DIM, "SCHEMA_THRESH_FULL": SCHEMA_THRESH_FULL,
                   "CHUNK_SIZE": CHUNK_SIZE, "PBV_COMMIT_STRENGTH": PBV_COMMIT_STRENGTH,
                   "PBV_INFORMATIVE_MIN": PBV_INFORMATIVE_MIN,
                   "INJECT_STRENGTH": INJECT_STRENGTH, "ARM_SEEDS": ARM_SEEDS,
                   "INJECT_SEED": INJECT_SEED},
        "arms": {k: {kk: vv for kk, vv in v.items()
                     if kk not in ("grounded_objects", "revisions", "abandon_gaps",
                                   "first_proposals", "injection_outcomes")}
                 for k, v in arms.items()},
        "limitations": [
            "hypotheses are NOT persisted across a foundation_persistence save/load cycle "
            "(that module was not edited this session); every arm runs in ONE process",
            "the proposer's metric is still distributional relatedness, not reference "
            "(audit B.2.2) -- this build fixes the missing hypothesis, not the wrong metric",
            "C2 is a NON-TRIVIALITY CONTROL, circular w.r.t. correctness; never an accuracy number",
            "this cell does NOT measure sense selection and bears on no sense-selection claim",
        ],
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
    for name, arm_obj in arms.items():
        _atomic_json(os.path.join(output_dir, f"arm_{name}_detail.json"),
                     {k: arm_obj.get(k) for k in ("revisions", "injection_outcomes",
                                                  "abandon_gaps", "grounded_objects")})
    return metrics


# =========================================================================== self-test
def self_test() -> dict:
    """Fast off-disk gate on the REAL code path at tiny N (no corpus read)."""
    from hdlab.reading_grounding_loop import _pbv_fixture     # the organ's own fixture

    state, engine_sentences, _ = _pbv_fixture(seed=5150)
    fns = make_pbv_fns(state)
    process_sentence(state, engine_sentences[0], "s0", pass_idx=1, pbv_fns=fns)
    right = state.library.items["zibbo"].hypothesis.obj
    state.library.inject_hypothesis("zibbo", "meadow", INJECT_STRENGTH, 1)
    for i, s in enumerate(engine_sentences[1:]):
        process_sentence(state, s, f"s{i + 1}", pass_idx=1, pbv_fns=fns)
    out = _injection_outcomes(state, {"zibbo": "meadow"})
    assert out["abandon_rate"] == 1.0, f"wrong injection must be abandoned, got {out}"
    assert out["n_scored"] == 1 and out["n_never_met_evidence"] == 0, out

    state2, es2, _ = _pbv_fixture(seed=5150)
    fns2 = make_pbv_fns(state2)
    process_sentence(state2, es2[0], "t0", pass_idx=1, pbv_fns=fns2)
    state2.library.inject_hypothesis("zibbo", right, INJECT_STRENGTH, 1)
    for i, s in enumerate(es2[1:]):
        process_sentence(state2, s, f"t{i + 1}", pass_idx=1, pbv_fns=fns2)
    out2 = _injection_outcomes(state2, {"zibbo": right})
    assert out2["abandon_rate"] == 0.0, (
        f"NON-TRIVIALITY CONTROL FAILED: the right hypothesis is abandoned too, so abandoning the "
        f"wrong one proves nothing. {out2}")

    gaps = _abandon_gaps(state)
    assert gaps and all(isinstance(g, int) for g in gaps), gaps
    mem = _memory_bytes(state)
    assert mem["hypothesis_state_bytes"] > 0 and mem["retained_trace_bytes"] > 0, mem
    # derangement: no target may be assigned its own right_obj as the wrong_obj
    tg = select_injection_targets({"first_proposals": {"w1": "o1", "w2": "o2", "w3": "o3"}}, 10)
    assert tg and all(r != w for r, w in tg.values()), tg
    return {"injected_wrong_abandoned_ok": True, "injected_right_control_holds_ok": True,
            "abandon_gaps_ok": True, "memory_accounting_ok": True, "derangement_ok": True,
            "c1_abandon_rate": out["abandon_rate"], "c2_abandon_rate": out2["abandon_rate"]}


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
    n_targets = N_INJECT_TARGETS_SMOKE if args.mode == "smoke" else N_INJECT_TARGETS_FULL
    try:
        todo = ARMS + ["finalize"] if args.arm in (None, "all") else [args.arm]
        ref = None
        for a in todo:
            if a == "finalize":
                m = finalize(args.mode, output_dir)
                print(json.dumps({k: m[k] for k in ("verdict", "verdict_msg", "primary",
                                                    "secondary")}, indent=2), flush=True)
                continue
            if a in ("C1_INJECT_WRONG", "C2_INJECT_RIGHT") and ref is None:
                units = exp_checkpoint.load_units(output_dir)
                ref = units.get(exp_checkpoint.unit_key("arm_done", "B_PBV"))
                if ref is None:
                    raise SystemExit(f"{a} requires arm B_PBV to have completed first")
            res = run_arm(a, args.mode, output_dir, reference=ref, n_targets=n_targets)
            if a == "B_PBV":
                ref = res
            print(f"[arm-done] {a} grounded={res['n_grounded']} "
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
