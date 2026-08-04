"""exp_coherence_role_conflict_crosstalk_v1 -- mechanism-capacity probe (NOT a capability claim).

Tests whether decode_coherence_margins / route_passage discriminates the TRUE goal-owner from a
foil ONCE the foil's error is embedded as a ROLE-CONFLICT: the foil already holds another
established role in the SAME passage register, so binding the outcome to it collides two
role-bindings on the SAME (cluster,event_slot) key in the foil's accumulated FHRR register
(hdlab.situation_model_accumulate.AccumulateRegister.register() bundles ALL of an entity's
(role,slot) bindings; decode() unbinds by slot then cleanup-argmaxes role -- two DIFFERENT roles
sharing one slot for one entity is a real superposition collision, not a proxy for one).

Pre-validated by a brain-foundational framing drill BEFORE this cell was authored:
notes/research_goal_owner_coherence_vs_mentalizing_framing_audit.md (commit aeceefe1d). That
drill ENDORSED running this probe WITH 3 mandatory scope corrections, followed exactly here
(see the drill's "Level 5" + "Falsifiable predictions" sections):

  1. SCOPE THE CLAIM: HARD-PASS criterion is "stated/single-world role-conflict-embedded
     goal-owner discrimination", explicitly NOT "goal-owner attribution" or "role-content
     coherence" generally. Carried in SCOPE_LABEL below, embedded in verdict_msg + metrics.
  2. HARD-FAIL SIGNATURE decisive even at N=1: margin-delta EXACTLY 0.0, OR sign-flips under a
     load-direction/identity-flip check (the artifact signature characterized in
     exp_coherence_aggregate_discriminates_goal_outcome_v1 commit 925897d74 and
     exp_coherence_fair_load_matched_retest_v1) -- HARD-FAIL, not "inconclusive N=1".
  3. LOAD DISCIPLINE: assert owner_load == foil_load PRE-conflict-embedding (asserted inline in
     _build_role_conflict_item; a violation crashes, not silently passes).

TWO items on the SAME real g5g6 passage (g5v_henry_wilkins_cherries, per
exp_coherence_fair_load_matched_retest_v1.py lines 271-300, reused: owner=Henry cluster '1',
foil=old_gentleman cluster '0', naturally load-matched 3 mentions each under strict_cb):

  ITEM "original": conflict embedded on the FOIL (old_gentleman). The wrong/recency baseline
  binds OUTCOME_UNMET to the foil at a REAL event_slot the foil already occupies with an
  established role elsewhere in the real passage (crosstalk); the coherent candidate binds
  OUTCOME_UNMET to the TRUE owner (Henry) at that same slot, which Henry does NOT already
  occupy (no collision). Prediction: agg_coherence_delta (candidate - baseline) > 0.

  ITEM "flipped" (the load-direction/identity-flip control mandated by correction 2): the SAME
  construction with conflicted/clean SWAPPED -- conflict embedded on Henry instead, coherent
  candidate = old_gentleman. If the mechanism's positive delta on "original" were really an
  identity bias (e.g. "owner=Henry always wins") rather than genuine crosstalk-sensitivity, this
  item's delta would flip sign or collapse. Prediction (if crosstalk generalizes): ALSO > 0 (the
  conflict-free candidate wins regardless of WHICH entity is conflict-free).

  SHUFFLED CONTROL: role_seq reversed on "original" (reuse _shuffle_role_seq verbatim from
  exp_coherence_fair_load_matched_retest_v1) -- entities/loads/event_slots/flagged_positions
  unchanged, only which semantic role binds to which position is scrambled. A real coherence
  signal must collapse (not still adopt the coherent candidate).

REUSED VERBATIM (no fork): hdlab.self_improving_loop.route_passage / decode_coherence_margins /
decide_keep_or_revert (via route_passage); exp_coherence_fair_load_matched_retest_v1.{
load_passages, _passage_bundle, GOLD_PATH_G5G6, ROLE_VOCAB, COREF_D as COREF_D,
MAX_EVENT_SLOTS, COREF_SEED, GO_ROLE_VOCAB_EXT, ABSTAIN_BAND}; exp_coherence_aggregate_
discriminates_goal_outcome_v1.{_coref_arm as the positive-control reproduction, _shuffle_role_seq,
_arms_must_differ_check, hash_stable}; exp_wire_coref_accumulate_situation_model_v1.name_anchor_map
(self-test owner/foil anchor verification only).

PRE-REGISTERED BANDS (this cell's own numeric instantiation; see also
notes/prereg_coherence_role_conflict_crosstalk_v1_2026-08-04.md):

  POSITIVE CONTROL (sanity gate, must fire before anything else is trusted): re-running
  exp_coherence_aggregate_discriminates_goal_outcome_v1._coref_arm(seed) unmodified MUST
  reproduce net_auto=1.0 (all seeds). If not, harness/imports are broken -- HARNESS_DEAD, stop.

  HARD_FAIL_ARTIFACT_SIGNATURE_CROSSTALK_DOES_NOT_GENERALIZE iff (any seed): orig_delta == 0.0
  EXACTLY, OR flip_delta <= 0 (sign flips / collapses under the identity-flip). Decisive at N=1
  per correction 2 -- this is the KNOWN artifact signature from prior cells, not new territory.

  HARD_FAIL_SIGNAL_IS_POSITIONAL_NOT_STRUCTURAL iff the shuffled control still adopts the
  coherent candidate (adopt_coherent==True) or shows a positive delta in ANY seed -- the effect
  would be positional, not structural/crosstalk-driven.

  HARD_PASS_CROSSTALK_GENERALIZATION_EXISTENCE_PROOF_SINGLE_ITEM iff (ALL seeds): orig_delta > 0
  AND flip_delta > 0 AND shuffled control collapses (adopt_coherent==False and delta <= 0 every
  seed). SCOPE-LABELED per correction 1: a single-item (N=1 real passage, 2-direction
  flip-tested) existence proof of crosstalk-generalization, NOT general goal-owner attribution
  or general role-content coherence.

  MIDDLE_BAND_N1_INCONCLUSIVE: none of the above decisive signatures fire (e.g. orig survives,
  flip does not fully clear >0 in every seed, but no exact-0.0 or sign-flip fired either --
  should not occur given the decisive-at-N=1 discipline in correction 2, but is the honest
  fallback if per-seed results genuinely split).

Not dispatched remote: LOCAL/CPU only (local_cpu_queue, or direct .venv invocation if paused),
<30s wall time expected -- exempt from Section 17 print-progress-flushing (timeout_s < 1800).
Self-test: python exp_coherence_role_conflict_crosstalk_v1.py --self-test
Smoke:     python exp_coherence_role_conflict_crosstalk_v1.py --smoke
Full:      python exp_coherence_role_conflict_crosstalk_v1.py --full
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "coherence_role_conflict_crosstalk_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import torch  # noqa: E402

# ---- REUSED BIT-IDENTICAL --------------------------------------------------------------------
from hdlab.self_improving_loop import route_passage  # noqa: E402
from exp_wire_coref_accumulate_situation_model_v1 import name_anchor_map  # noqa: E402
from exp_coherence_fair_load_matched_retest_v1 import (  # noqa: E402
    load_passages, _passage_bundle, GOLD_PATH_G5G6, ROLE_VOCAB, COREF_D, MAX_EVENT_SLOTS,
    COREF_SEED, GO_ROLE_VOCAB_EXT, ABSTAIN_BAND,
)
from exp_coherence_aggregate_discriminates_goal_outcome_v1 import (  # noqa: E402
    _coref_arm as _orig_coref_positive_control, _shuffle_role_seq, _arms_must_differ_check,
    hash_stable,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ============================================================================ config
SEEDS = list(range(5))
EXPECTED_N_SEEDS = len(SEEDS)
GO_SEED_BASE = 30260805  # fixed integer (distinct from the sibling cell's 30260804), no hash()

SCOPE_LABEL = (
    "stated/single-world role-conflict-embedded goal-owner discrimination -- NOT general "
    "goal-owner attribution, NOT general role-content coherence. A HARD-PASS is a single-item "
    "(N=1 real passage, 2-direction identity-flip-tested) existence proof that crosstalk-based "
    "coherence generalizes from identity-merge collisions (coref) to role-conflict collisions "
    "(foil independently busy elsewhere in the register); it is NOT a general "
    "role-content-coherence capability."
)


# ============================================================================ item construction
def _build_role_conflict_item(bundle: dict, conflicted: str, clean: str, item_id: str) -> dict:
    """DOWNSTREAM-EMBEDDED, ROLE-CONFLICT goal-owner item on the REAL passage
    g5v_henry_wilkins_cherries. `conflicted` is the entity the WRONG/recency baseline assigns
    the outcome to; its outcome-slot binding REUSES a REAL event_slot where `conflicted` already
    holds an established role in the real passage -- crosstalk: two role-bindings (the real
    established role + OUTCOME_UNMET) share one (cluster,slot) key in `conflicted`'s accumulated
    FHRR register. `clean` is the TRUE/coherent owner; its outcome-slot binding at that SAME
    reused slot is a fresh single binding for `clean` (asserted below: `clean` does not already
    occupy that slot) -- asymmetric crosstalk by construction, not by asserted metric.

    Symmetric supporting GOAL/ACTION_AGAINST events (2 each) keep register load matched between
    `conflicted` and `clean` through the extension; the LOAD-MATCH ASSERTION below is checked
    PRE-conflict-embedding (on the real passage alone, per contract correction 3) so a pass
    can never be re-explained as raw load asymmetry.
    """
    n_slots = bundle["n_slots"]
    real_role_seq = list(bundle["role_seq"])
    real_event_slots = list(bundle["event_slots"])
    real_base_ids = list(bundle["base_ids"])

    conflicted_load = sum(1 for c in real_base_ids if c == conflicted)
    clean_load = sum(1 for c in real_base_ids if c == clean)
    assert conflicted_load == clean_load, (
        f"{item_id}: PRE-CONFLICT-EMBEDDING LOAD MISMATCH conflicted={conflicted_load} "
        f"clean={clean_load} -- load-match assertion (contract correction 3) FAILED"
    )

    conflicted_positions = [p for p in range(len(real_base_ids)) if real_base_ids[p] == conflicted]
    clean_slots = {real_event_slots[p] for p in range(len(real_base_ids)) if real_base_ids[p] == clean}
    reuse_candidates = [p for p in conflicted_positions if real_event_slots[p] not in clean_slots]
    assert reuse_candidates, (
        f"{item_id}: no {conflicted}-only real slot available for role-conflict embedding "
        f"(every {conflicted} slot is shared with {clean} -- construction would be symmetric, "
        f"not a targeted role-conflict on {conflicted} alone)"
    )
    reuse_pos = reuse_candidates[0]
    reuse_slot = real_event_slots[reuse_pos]
    reuse_established_role = real_role_seq[reuse_pos]
    assert reuse_established_role != "OUTCOME_UNMET", (
        f"{item_id}: reused slot's established role is already OUTCOME_UNMET -- not a genuine "
        f"role-CONFLICT (same role twice is not a conflict, it is a repeat)"
    )

    ext_role_seq = ["GOAL", "ACTION_AGAINST", "GOAL", "ACTION_AGAINST", "OUTCOME_UNMET"]
    ext_event_slots = [n_slots, n_slots + 1, n_slots, n_slots + 1, reuse_slot]
    ext_baseline_ids = [clean, clean, conflicted, conflicted, conflicted]  # recency->conflicted (WRONG)
    ext_true_ids = [clean, clean, conflicted, conflicted, clean]          # coherent->clean (TRUE)

    role_seq = real_role_seq + ext_role_seq
    event_slots = real_event_slots + ext_event_slots
    baseline_cluster_ids = real_base_ids + ext_baseline_ids
    true_cluster_ids = real_base_ids + ext_true_ids
    flagged_positions = [len(real_role_seq) + 4]
    max_event_slots = n_slots + 4

    return dict(id=item_id, role_seq=role_seq, event_slots=event_slots,
                baseline_cluster_ids=baseline_cluster_ids, true_cluster_ids=true_cluster_ids,
                flagged_positions=flagged_positions, max_event_slots=max_event_slots,
                conflicted=conflicted, clean=clean, reuse_slot=reuse_slot,
                reuse_established_role=reuse_established_role, reuse_pos=reuse_pos)


def _go_route_one(it: dict, seed: int) -> dict:
    item_seed = GO_SEED_BASE + seed * 1000 + (hash_stable(it["id"]) % 1000)
    result = route_passage(
        it["role_seq"], it["event_slots"], it["baseline_cluster_ids"],
        {"coherent": it["true_cluster_ids"]}, it["flagged_positions"], GO_ROLE_VOCAB_EXT, COREF_D,
        lambda: torch.Generator().manual_seed(item_seed), it["max_event_slots"],
        abstain_band=ABSTAIN_BAND,
    )
    pc = result["per_candidate"]["coherent"]
    return dict(id=it["id"], adopt_coherent=(result["adopt"] == "coherent"),
                applicable=pc["applicable"], agg_coherence_delta=pc["agg_coherence_delta"])


# ============================================================================ per-seed unit
def run_seed(seed: int) -> dict:
    passages = load_passages(GOLD_PATH_G5G6)
    bundles = [_passage_bundle(p) for p in passages]
    bundle_by_id = {b["passage_id"]: b for b in bundles}
    bundle_henry = bundle_by_id["g5v_henry_wilkins_cherries"]

    positive_control = _orig_coref_positive_control(seed)

    item_orig = _build_role_conflict_item(bundle_henry, conflicted="0", clean="1",
                                           item_id="go_role_conflict_original")
    item_flip = _build_role_conflict_item(bundle_henry, conflicted="1", clean="0",
                                           item_id="go_role_conflict_flipped")
    _arms_must_differ_check([item_orig, item_flip])

    row_orig = _go_route_one(item_orig, seed)
    row_flip = _go_route_one(item_flip, seed)

    shuffled_orig = _shuffle_role_seq([item_orig])[0]
    assert shuffled_orig["role_seq"] != item_orig["role_seq"]
    row_shuffled = _go_route_one(shuffled_orig, seed)

    return dict(
        seed=seed,
        pc_net_auto=positive_control["net_auto"], pc_fires=positive_control["fires"],
        orig_delta=row_orig["agg_coherence_delta"], orig_adopt=row_orig["adopt_coherent"],
        orig_applicable=row_orig["applicable"],
        flip_delta=row_flip["agg_coherence_delta"], flip_adopt=row_flip["adopt_coherent"],
        flip_applicable=row_flip["applicable"],
        shuffled_delta=row_shuffled["agg_coherence_delta"], shuffled_adopt=row_shuffled["adopt_coherent"],
        shuffled_applicable=row_shuffled["applicable"],
        reuse_slot_orig=item_orig["reuse_slot"], reuse_role_orig=item_orig["reuse_established_role"],
        reuse_slot_flip=item_flip["reuse_slot"], reuse_role_flip=item_flip["reuse_established_role"],
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return round(sum(vals) / len(vals), 6) if vals else None

    def all_true(key):
        return all(per_seed[s][key] for s in seeds)

    pc_fires_all = all_true("pc_fires")
    pc_net_auto_mean = mean("pc_net_auto")
    positive_control_reproduces = bool(pc_fires_all and pc_net_auto_mean == 1.0)

    orig_delta_mean = mean("orig_delta")
    flip_delta_mean = mean("flip_delta")
    shuffled_delta_mean = mean("shuffled_delta")

    orig_delta_exact_zero_any = any(per_seed[s]["orig_delta"] == 0.0 for s in seeds)
    flip_sign_flips_any = any(
        (per_seed[s]["flip_delta"] is not None and per_seed[s]["flip_delta"] <= 0) for s in seeds
    )
    artifact_signature = bool(orig_delta_exact_zero_any or flip_sign_flips_any)

    shuffled_reproduces = bool(
        any(per_seed[s]["shuffled_adopt"] for s in seeds)
        or any((per_seed[s]["shuffled_delta"] is not None and per_seed[s]["shuffled_delta"] > 0)
               for s in seeds)
    )
    shuffled_collapses = not shuffled_reproduces

    orig_survives_all = all(
        (per_seed[s]["orig_delta"] is not None and per_seed[s]["orig_delta"] > 0) for s in seeds
    )
    flip_survives_all = all(
        (per_seed[s]["flip_delta"] is not None and per_seed[s]["flip_delta"] > 0) for s in seeds
    )

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH"
    elif not positive_control_reproduces:
        verdict = "HARNESS_DEAD_POSITIVE_CONTROL_FAILED"
    elif artifact_signature:
        verdict = "HARD_FAIL_ARTIFACT_SIGNATURE_CROSSTALK_DOES_NOT_GENERALIZE"
    elif shuffled_reproduces:
        verdict = "HARD_FAIL_SIGNAL_IS_POSITIONAL_NOT_STRUCTURAL"
    elif orig_survives_all and flip_survives_all and shuffled_collapses:
        verdict = "HARD_PASS_CROSSTALK_GENERALIZATION_EXISTENCE_PROOF_SINGLE_ITEM"
    else:
        verdict = "MIDDLE_BAND_N1_INCONCLUSIVE"

    summary = (
        f"SCOPE=[{SCOPE_LABEL}] || POSITIVE_CONTROL reproduces={positive_control_reproduces} "
        f"(fires_all_seeds={pc_fires_all} net_auto_mean={pc_net_auto_mean}) | "
        f"ORIG(conflict on foil old_gentleman, true owner Henry) delta_mean={orig_delta_mean} "
        f"survives_all_seeds={orig_survives_all} | "
        f"FLIP(identity/load-direction-flip: conflict on Henry, true owner old_gentleman) "
        f"delta_mean={flip_delta_mean} survives_all_seeds={flip_survives_all} | "
        f"SHUFFLED(role_seq reversed on ORIG) delta_mean={shuffled_delta_mean} "
        f"reproduces={shuffled_reproduces} collapses={shuffled_collapses} | "
        f"artifact_signature_fired={artifact_signature} "
        f"(orig_delta_exact_zero_any={orig_delta_exact_zero_any} "
        f"flip_sign_flips_any={flip_sign_flips_any})"
    )

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        scope_label=SCOPE_LABEL,
        means=dict(
            pc_net_auto=pc_net_auto_mean, orig_delta=orig_delta_mean, flip_delta=flip_delta_mean,
            shuffled_delta=shuffled_delta_mean,
        ),
        bands=dict(
            positive_control_reproduces=positive_control_reproduces,
            orig_survives_all_seeds=orig_survives_all, flip_survives_all_seeds=flip_survives_all,
            shuffled_collapses=shuffled_collapses, shuffled_reproduces=shuffled_reproduces,
            artifact_signature_fired=artifact_signature,
            orig_delta_exact_zero_any=orig_delta_exact_zero_any,
            flip_sign_flips_any=flip_sign_flips_any,
        ),
        load_match_assertion_held=True,  # asserted inline in _build_role_conflict_item (twice,
                                          # once per direction); would have raised AssertionError
                                          # (crash) otherwise -- never silently passed
        brain_fidelity_caveat=(
            "route_passage's aggregate is a single-pass integration over the whole passage/item -- "
            "a brain-COMPATIBLE approximation of Kintsch construction-integration / CA3 recurrent "
            "attractor settling, not full recurrent relaxation. A HARD_PASS here licenses the "
            "one-shot crosstalk-collision test as sufficient for THIS role-conflict-embedded item, "
            "not as fully brain-faithful settling, and NOT as a general role-content-coherence "
            "capability (see scope_label)."
        ),
        per_seed=per_seed,
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    _write_json(os.path.join(output_dir, "metrics.json"), diag)


def run(run_mode: str) -> dict:
    t0 = time.perf_counter()
    out_dir = OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"
    os.makedirs(out_dir, exist_ok=True)
    _write_json(os.path.join(out_dir, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
                 "expected_n_units": EXPECTED_N_SEEDS})

    seeds = SEEDS if run_mode == "full" else SEEDS[:2]
    done = completed_units(out_dir)
    for seed in seeds:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed)
        record_unit(out_dir, k, res)
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"pc_net_auto={res['pc_net_auto']} orig_delta={res['orig_delta']} "
              f"flip_delta={res['flip_delta']} shuffled_delta={res['shuffled_delta']}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(out_dir).values()}
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(coref_d=COREF_D, coref_role_vocab=ROLE_VOCAB, coref_max_event_slots=MAX_EVENT_SLOTS,
                          go_role_vocab_ext=GO_ROLE_VOCAB_EXT, abstain_band=ABSTAIN_BAND,
                          seeds=seeds, n_g5g6_passages=18, n_items_per_seed=3)
    agg["prereg"] = "notes/prereg_coherence_role_conflict_crosstalk_v1_2026-08-04.md"
    agg["endorsement_note"] = "notes/research_goal_owner_coherence_vs_mentalizing_framing_audit.md"
    agg["cites"] = [
        "hdlab/self_improving_loop.py (route_passage, reused verbatim)",
        "hdlab/situation_model_accumulate.py (AccumulateRegister.register/decode -- the "
        "crosstalk mechanism under test: register() bundles ALL (role,slot) bindings for an "
        "entity; decode() unbinds by slot then cleanup-argmaxes role)",
        "exp_coherence_fair_load_matched_retest_v1.py (load_passages, _passage_bundle, "
        "GOLD_PATH_G5G6, ROLE_VOCAB/COREF_D/MAX_EVENT_SLOTS/COREF_SEED/GO_ROLE_VOCAB_EXT/"
        "ABSTAIN_BAND, sourced verbatim; item-construction PATTERN reused, role-conflict slot "
        "reuse is this cell's own addition)",
        "exp_coherence_aggregate_discriminates_goal_outcome_v1.py (_coref_arm positive-control, "
        "_shuffle_role_seq, _arms_must_differ_check, hash_stable, reused verbatim)",
        "notes/research_goal_owner_coherence_vs_mentalizing_framing_audit.md (the endorsing "
        "framing drill, 3 mandatory scope corrections applied verbatim)",
    ]
    _write_json(os.path.join(out_dir, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (0) real code path: route_passage exercised directly
    res = route_passage(["agent"], [0], ["A"], {"cand": ["B"]}, [0], ["agent", "mentioned"], 64,
                         lambda: torch.Generator().manual_seed(0), 1, abstain_band=ABSTAIN_BAND)
    assert "adopt" in res and "per_candidate" in res, f"route_passage real-call bad: {res}"

    # (1) 18 g5g6 passages load + bundle construction (reused verbatim from sibling cell)
    passages = load_passages(GOLD_PATH_G5G6)
    assert len(passages) == 18, f"expected 18 g5g6 passages, got {len(passages)}"
    bundles = [_passage_bundle(p) for p in passages]
    bundle_by_id = {b["passage_id"]: b for b in bundles}
    b_henry = bundle_by_id["g5v_henry_wilkins_cherries"]

    # (2) owner/foil anchors are the entities claimed (Henry='1', old_gentleman='0')
    anchors = name_anchor_map(b_henry["stream"], b_henry["base_ids"])
    assert anchors.get("Henry") == "1", f"Henry anchor changed: {anchors}"
    assert anchors.get("old_gentleman") == "0", f"old_gentleman anchor changed: {anchors}"

    # (3) role-conflict item construction: load-match assertion holds (would crash if not),
    # a genuine foil-only reusable slot exists, established role differs from OUTCOME_UNMET
    item_orig = _build_role_conflict_item(b_henry, conflicted="0", clean="1",
                                           item_id="go_role_conflict_original")
    item_flip = _build_role_conflict_item(b_henry, conflicted="1", clean="0",
                                           item_id="go_role_conflict_flipped")
    for it, conflicted in ((item_orig, "0"), (item_flip, "1")):
        assert it["reuse_established_role"] in ROLE_VOCAB or it["reuse_established_role"] in (
            "AGENT", "PATIENT",
        ) or it["reuse_established_role"] not in ("GOAL", "ACTION_AGAINST", "OUTCOME_MET",
                                                    "OUTCOME_UNMET"), (
            f"{it['id']}: reused role {it['reuse_established_role']!r} looks synthetic, not a "
            f"real established coref role"
        )
        # the reused slot is genuinely occupied by `conflicted` in the REAL (pre-extension) base
        pos = it["reuse_pos"]
        assert b_henry["base_ids"][pos] == conflicted
        assert b_henry["event_slots"][pos] == it["reuse_slot"]

    # (4) arms-must-differ + shuffle actually differs (reused verbatim functions exercised for real)
    _arms_must_differ_check([item_orig, item_flip])
    shuffled = _shuffle_role_seq([item_orig])[0]
    assert shuffled["role_seq"] != item_orig["role_seq"], "shuffle no-op"
    assert shuffled["baseline_cluster_ids"] == item_orig["baseline_cluster_ids"]
    assert shuffled["event_slots"] == item_orig["event_slots"]

    # (5) positive control reproduces net_auto=1.0 (the harness sanity gate)
    pc = _orig_coref_positive_control(0)
    assert pc["net_auto"] == 1.0, f"POSITIVE CONTROL FAILED: harness broken, net_auto={pc['net_auto']}"

    # (6) one full seed sanity (all pieces run to completion)
    res = run_seed(0)
    for k in ("pc_net_auto", "orig_delta", "flip_delta", "shuffled_delta"):
        assert res[k] is not None, f"{k} missing"

    print(f"[SELFTEST PASS] positive_control net_auto={pc['net_auto']} "
          f"orig reuse_slot={item_orig['reuse_slot']} role={item_orig['reuse_established_role']!r} "
          f"flip reuse_slot={item_flip['reuse_slot']} role={item_flip['reuse_established_role']!r} "
          f"seed0 orig_delta={res['orig_delta']} flip_delta={res['flip_delta']} "
          f"shuffled_delta={res['shuffled_delta']}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            raise SystemExit(0 if self_test() else 1)
        if args.smoke:
            run("smoke")
            raise SystemExit(0)
        run("full")
        raise SystemExit(0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise


if __name__ == "__main__":
    main()
