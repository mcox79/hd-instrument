"""exp_coherence_fair_load_matched_retest_v1 -- FAIR re-test correcting the confound flagged by USER
in exp_coherence_aggregate_discriminates_goal_outcome_v1 (commit prior to this cell): that cell's
"coref wins (net_auto=1.0), goal-outcome loses (adopt_rate=0.0)" comparison moved relation-KIND,
data-realness, role-vocab-richness, register slot-count, AND load-symmetry all at once (coref = 18
real McGuffey passages / 9-role vocab / 16 slots / never load-matched; goal-outcome = 4 synthetic
hand-built items / 4-role vocab / 8 slots / explicitly load-matched). Design per
notes/research_relational_backward_reach_coherence_selector.md Sections 3, 6, 7 (the design drill;
commit b983de9a5). Does NOT build the backward-reach organ (that note's Section 5) -- conditional
fallback only, out of scope here.

TWO ARMS, ARM 1 IS DECISIVE AND CHEAPEST (needs no new data):

ARM 1 (coref load-matched subset): is coref's own net_auto=1.0 ALSO a load-redistribution artifact,
never checked before? Selects, LIVE from the 18 g5g6_reviewed McGuffey passages (no hand-picking,
no hardcoded item list), every (passage, candidate-mechanism) pair where run_strict_cb_instrumented
(baseline) and a candidate resolver (principle_b_deixis OR run_decay_window -- the CONFIRMED-
NEGATIVE recency-trap lever from exp_coref_autonomous_fix_router_v1, ported verbatim, reused not
reimplemented) disagree at a flagged position AND the two candidates' downstream register load
(total other-position mention count bound to each entity, excluding the position itself) is EXACTLY
EQUAL (LOAD_MATCH_TOL=0) -- computed at runtime from the real resolver outputs, not asserted. This
alone answers "is coref's 1.0 also a load artifact" without touching goal-outcome.

ARM 2 (goal-outcome fair test, directional only -- data-availability wall hit, reported honestly):
extends the SAME 9-role/16-slot coref register (not a separate register) with GOAL/ACTION_AGAINST/
OUTCOME_MET/OUTCOME_UNMET roles, on REAL McGuffey g5g6 passages (not synthetic hand-built items),
with the wrong goal-owner candidate DOWNSTREAM-EMBEDDED (an entity that already carries other real
established role bindings elsewhere in the SAME real passage, not a free-floating foil) and a
LOAD-MATCHED control (symmetric added supporting events), per Section 3a-3d. A keyword scan of all
18 passages for goal/desire/attempt language (see exploration log in this cell's construction)
found only ONE passage clean enough to use: g5v_henry_wilkins_cherries (Henry's forbidden-cherry
desire, punished -- OUTCOME_UNMET; entities Henry/old_gentleman are ALREADY naturally load-matched,
3 mentions each, under strict_cb). g5v_tonish_colt has a plausible goal narrative (catch/tame the
colt) but strict_cb badly mis-resolves the colt entity there (merges it into Tonish's cluster at
most positions) -- using it would test coref's OWN resolution noise, not goal-outcome coherence, so
it is EXCLUDED, not patched with a wider excuse. N=1 real goal item is far below the drill's own
N>=10 threshold (Section 3b) -- ARM 2 is run and reported for a directional read only, NEVER used
alone to claim HARD-PASS/HARD-FAIL; per the task contract, ARM 1 is decisive and is reported
regardless of ARM 2's outcome.

REUSED VERBATIM (no fork): hdlab.self_improving_loop.route_passage/decode_coherence_margins/
decide_keep_or_revert; hdlab.coreference_resolver.{build_mention_stream, enrich_dialogue,
run_strict_cb_instrumented, run_principle_b_deixis, mention_link_wrong}; exp_coref_autonomous_
fix_router_v1.run_decay_window (the confirmed-negative trap, ported there from
exp_coref_loop_cross_clause_discourse_v1, reused again here, not re-ported); exp_wire_coref_
accumulate_situation_model_v1.{event_slots_for, ROLE_VOCAB, D, MAX_EVENT_SLOTS, SEED,
name_anchor_map}; exp_coherence_aggregate_discriminates_goal_outcome_v1.{_coref_arm (the EXACT
positive-control reproduction), _shuffle_role_seq, _arms_must_differ_check, hash_stable}.

PRE-REGISTERED BANDS (drill Section 3e/7, this cell's own numeric instantiation):
  POSITIVE CONTROL (sanity gate, must fire before anything else is trusted): re-running
  exp_coherence_aggregate_discriminates_goal_outcome_v1._coref_arm(seed) unmodified MUST reproduce
  net_auto=1.0 (all seeds). If not, the harness/imports are broken -- stop, do not trust bands below.

  ARM 1 (coref load-matched) SURVIVES iff net_auto_matched > 0 (the aggregate signal nets a real
  gain on the load-matched-only subset, mirroring the original quantity exactly) AND at least one
  matched item's auto_adopt decision is correct (matches oracle) -- not a single-item coincidence
  with net_gold==0. ARM 1 COLLAPSES iff net_auto_matched <= 0 (the load-matched subset shows no net
  gain -- the original 1.0 was riding on load, not coherence).
  SHUFFLED CONTROL for ARM 1 must show auto_adopt collapsing toward false on the matched items when
  role_seq is reversed (structural coherence destroyed, position/load preserved) -- if the shuffled
  version STILL adopts as readily as the unshuffled version, the signal is positional, not
  structural, regardless of the net_auto verdict above.

  ARM 2 (goal-outcome fair, directional, N=1 -- explicitly underpowered) SURVIVES (directionally)
  iff the load-matched item's auto_adopt==True picks the TRUE owner (not the foil) AND the shuffled
  version does not. COLLAPSES iff it fails to adopt the true owner. Reported as a single-item
  observation, not a verdict-bearing band on its own.

  OVERALL VERDICT: HARD_PASS_BOTH_SURVIVE_LOAD_MATCHING (ARM1 survives AND ARM2's one item survives
  AND both shuffled controls collapse) / HARD_FAIL_COREF_WAS_LOAD_ARTIFACT (ARM1 collapses -- the
  single most consequential outcome per the drill: it would mean atom 29609's "confirmed reuse"
  claim needs re-audit) / MIDDLE_BAND_ARM1_SURVIVES_ARM2_INCONCLUSIVE (ARM1 survives, ARM2's N=1 is
  too thin to call either way -- the expected, honest outcome given the data-availability wall).

Not dispatched remote: LOCAL/CPU only (local_cpu_queue), <30s wall time expected.
Self-test: python exp_coherence_fair_load_matched_retest_v1.py --self-test
Smoke:     python exp_coherence_fair_load_matched_retest_v1.py --smoke
Full:      python exp_coherence_fair_load_matched_retest_v1.py --full
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

ANCHOR_NAME = "coherence_fair_load_matched_retest_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import torch  # noqa: E402

# ---- REUSED BIT-IDENTICAL --------------------------------------------------------------------
from hdlab.self_improving_loop import route_passage  # noqa: E402
from hdlab.coreference_resolver import (  # noqa: E402
    build_mention_stream, enrich_dialogue, run_strict_cb_instrumented, run_principle_b_deixis,
    mention_link_wrong,
)
from exp_wire_coref_accumulate_situation_model_v1 import (  # noqa: E402
    event_slots_for, ROLE_VOCAB, D as COREF_D, MAX_EVENT_SLOTS, SEED as COREF_SEED, name_anchor_map,
)
from exp_coref_autonomous_fix_router_v1 import run_decay_window  # noqa: E402
from exp_coherence_aggregate_discriminates_goal_outcome_v1 import (  # noqa: E402
    _coref_arm as _orig_coref_positive_control, _shuffle_role_seq, _arms_must_differ_check,
    hash_stable,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ============================================================================ config
ABSTAIN_BAND = 0.02
LOAD_MATCH_TOL = 0          # STRICT: exact load equality (real matched items exist, no need to loosen)
SEEDS = list(range(5))
EXPECTED_N_SEEDS = len(SEEDS)

CAND_MECHANISMS = ["principle_b_deixis", "decay_window"]  # decay_window = the confirmed recency trap

GOLD_PATH_G5G6 = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
    "gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl",
)

# GO extension roles, appended to coref's own ROLE_VOCAB (Section 3a: ONE register, not two).
GO_EXT_ROLES = ["GOAL", "ACTION_AGAINST", "OUTCOME_MET", "OUTCOME_UNMET"]
GO_ROLE_VOCAB_EXT = list(ROLE_VOCAB) + [r for r in GO_EXT_ROLES if r not in ROLE_VOCAB]
GO_SEED_BASE = 30260804  # fixed integer, matches prior cell's convention (no hash())


def load_passages(path: str):
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return sorted(passages, key=lambda p: p["passage_id"])


# ============================================================================ ARM 1: coref load-matched
def _passage_bundle(passage: dict) -> dict:
    """Compute everything needed once per passage: real stream + baseline (strict_cb) + both
    candidate mechanisms' full-passage resolutions (int preds for mention_link_wrong, str ids for
    route_passage), role_seq, event_slots. Pure function of the gold passage; no RNG."""
    stream = enrich_dialogue(passage, build_mention_stream(passage))
    base_pred, base_decisions = run_strict_cb_instrumented(stream)
    pb_pred, _actions = run_principle_b_deixis(stream)
    dw_pred = run_decay_window(stream)
    role_seq = [rec["role"] for rec in stream]
    event_slots, n_slots, _ = event_slots_for(stream)
    flagged = [pos for pos, rec in enumerate(stream)
               if rec["is_pronoun"] and base_decisions[pos]["n_compatible"] >= 2]
    return dict(
        passage_id=passage["passage_id"], stream=stream, base_pred=base_pred,
        base_ids=[str(c) for c in base_pred],
        cand_pred={"principle_b_deixis": pb_pred, "decay_window": dw_pred},
        cand_ids={"principle_b_deixis": [str(c) for c in pb_pred],
                  "decay_window": [str(c) for c in dw_pred]},
        role_seq=role_seq, event_slots=event_slots, n_slots=n_slots, flagged=flagged,
    )


def _entity_load(ids_list, pos, entity_id) -> int:
    """Downstream register load: count of OTHER positions bound to entity_id (excludes pos itself)."""
    return sum(1 for q, c in enumerate(ids_list) if q != pos and c == entity_id)


def build_load_matched_coref_items(bundles):
    """LIVE selection (no hardcoded item list): every (passage, candidate) pair where the candidate
    changes a flagged position AND the two competing entities' downstream load is exactly equal
    (LOAD_MATCH_TOL). Self-checked below in self_test() and again inline via assert."""
    items = []
    for b in bundles:
        for cand_name in CAND_MECHANISMS:
            cand_ids = b["cand_ids"][cand_name]
            changed_flagged = [p for p in b["flagged"] if cand_ids[p] != b["base_ids"][p]]
            matched_positions = []
            for p in changed_flagged:
                be, ce = b["base_ids"][p], cand_ids[p]
                base_load = _entity_load(b["base_ids"], p, be)
                cand_load = _entity_load(cand_ids, p, ce)
                if abs(base_load - cand_load) <= LOAD_MATCH_TOL:
                    matched_positions.append(p)
                    # self-check: load-match assertion holds by construction
                    assert base_load == cand_load, (b["passage_id"], cand_name, p, base_load, cand_load)
            if matched_positions:
                items.append(dict(
                    id=f"{b['passage_id']}_{cand_name}_matched", passage_id=b["passage_id"],
                    cand_name=cand_name, role_seq=list(b["role_seq"]),
                    event_slots=list(b["event_slots"]),
                    baseline_cluster_ids=list(b["base_ids"]),
                    true_cluster_ids=list(cand_ids),
                    flagged_positions=matched_positions, max_event_slots=MAX_EVENT_SLOTS,
                ))
    return items


def _route_coref_item(item: dict, bundle_by_id: dict, seed: int) -> dict:
    item_seed = COREF_SEED + seed * 1000 + (hash_stable(item["id"]) % 1000)
    result = route_passage(
        item["role_seq"], item["event_slots"], item["baseline_cluster_ids"],
        {item["cand_name"]: item["true_cluster_ids"]}, item["flagged_positions"],
        ROLE_VOCAB, COREF_D, lambda: torch.Generator().manual_seed(item_seed),
        item["max_event_slots"], abstain_band=ABSTAIN_BAND,
    )
    pc = result["per_candidate"][item["cand_name"]]
    auto_adopt = result["adopt"] == item["cand_name"]

    b = bundle_by_id[item["passage_id"]]
    stream, base_pred = b["stream"], b["base_pred"]
    cand_pred = b["cand_pred"][item["cand_name"]]
    corr = brk = 0
    for pos in item["flagged_positions"]:
        wrong_pre = mention_link_wrong(pos, stream, base_pred)
        wrong_post = mention_link_wrong(pos, stream, cand_pred)
        if wrong_pre and not wrong_post:
            corr += 1
        elif wrong_post and not wrong_pre:
            brk += 1
    net_gold = corr - brk
    oracle_adopt = net_gold > 0
    return dict(id=item["id"], passage_id=item["passage_id"], cand_name=item["cand_name"],
                applicable=pc["applicable"], agg_coherence_delta=pc["agg_coherence_delta"],
                auto_adopt=auto_adopt, net_gold=net_gold, oracle_adopt=oracle_adopt,
                matches_oracle=(auto_adopt == oracle_adopt))


def _arm1_matched(bundles, seed: int) -> dict:
    bundle_by_id = {b["passage_id"]: b for b in bundles}
    items = build_load_matched_coref_items(bundles)
    rows = [_route_coref_item(it, bundle_by_id, seed) for it in items]
    applicable = [r for r in rows if r["applicable"]]
    net_auto = sum(r["net_gold"] for r in applicable if r["auto_adopt"])
    net_oracle = sum(r["net_gold"] for r in applicable if r["net_gold"] > 0)
    agreement_rate = (sum(r["matches_oracle"] for r in applicable) / len(applicable)) if applicable else None
    return dict(n_items=len(items), n_applicable=len(applicable), net_auto=net_auto,
                net_oracle=net_oracle, agreement_rate=agreement_rate, rows=rows,
                item_ids=[it["id"] for it in items])


def _arm1_shuffled(bundles, seed: int) -> dict:
    """SHUFFLED-STRUCTURE CONTROL on the SAME matched items: role_seq reversed (reuse
    _shuffle_role_seq VERBATIM), entities/loads/positions unchanged. A real coherence signal must
    collapse toward not-adopting."""
    bundle_by_id = {b["passage_id"]: b for b in bundles}
    items = build_load_matched_coref_items(bundles)
    shuffled = _shuffle_role_seq(items)
    rows = []
    for it in shuffled:
        r = _route_coref_item(
            dict(it, id=it["id"], passage_id=it["passage_id"], cand_name=it["cand_name"]),
            bundle_by_id, seed,
        )
        rows.append(r)
    adopt_rate = (sum(r["auto_adopt"] for r in rows) / len(rows)) if rows else None
    return dict(n_items=len(shuffled), adopt_rate=adopt_rate, rows=rows)


# ============================================================================ ARM 2: goal-outcome fair
def _go_item_henry_wilkins_cherries(bundle: dict) -> dict:
    """DOWNSTREAM-EMBEDDED, LOAD-MATCHED goal-outcome item, REAL passage g5v_henry_wilkins_cherries.
    owner=Henry (cluster '1' under strict_cb, 3 real prior mentions), foil=old_gentleman (cluster
    '0', 3 real prior mentions) -- NATURALLY load-matched under strict_cb, verified in self_test.
    Extension: symmetric GOAL+ACTION_AGAINST supporting event for both (keeps load matched: 3+2=5
    each), then 2 OUTCOME_UNMET positions flagged, baseline(recency)=foil, candidate(coherent)=TRUE
    owner (Henry) -- anti-recency by construction (foil is NOT more recent; both get one extra
    supporting event so recency is not confounded with load direction either)."""
    n_slots = bundle["n_slots"]
    owner, foil = "1", "0"  # Henry, old_gentleman -- verified via name_anchor_map in self_test
    real_role_seq = list(bundle["role_seq"])
    real_event_slots = list(bundle["event_slots"])
    real_base_ids = list(bundle["base_ids"])
    ext_role_seq = ["GOAL", "ACTION_AGAINST", "GOAL", "ACTION_AGAINST", "OUTCOME_UNMET", "OUTCOME_UNMET"]
    ext_event_slots = [n_slots, n_slots + 1, n_slots, n_slots + 1, n_slots + 2, n_slots + 3]
    ext_baseline_ids = [owner, owner, foil, foil, foil, foil]     # recency: outcome -> foil (WRONG)
    ext_true_ids = [owner, owner, foil, foil, owner, owner]        # coherent: outcome -> TRUE owner
    role_seq = real_role_seq + ext_role_seq
    event_slots = real_event_slots + ext_event_slots
    baseline_cluster_ids = real_base_ids + ext_baseline_ids
    true_cluster_ids = real_base_ids + ext_true_ids
    flagged_positions = [len(real_role_seq) + 4, len(real_role_seq) + 5]
    return dict(id="go_henry_wilkins_matched", role_seq=role_seq, event_slots=event_slots,
                baseline_cluster_ids=baseline_cluster_ids, true_cluster_ids=true_cluster_ids,
                flagged_positions=flagged_positions, max_event_slots=n_slots + 6,
                owner=owner, foil=foil)


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


def _arm2_go(bundle_henry: dict, seed: int) -> dict:
    item = _go_item_henry_wilkins_cherries(bundle_henry)
    _arms_must_differ_check([item])
    row = _go_route_one(item, seed)
    shuffled = _shuffle_role_seq([item])[0]
    assert shuffled["role_seq"] != item["role_seq"]
    row_shuffled = _go_route_one(shuffled, seed)
    return dict(n_items=1, adopt_coherent=row["adopt_coherent"], row=row,
                adopt_coherent_shuffled=row_shuffled["adopt_coherent"], row_shuffled=row_shuffled,
                data_availability_note=(
                    "Only 1 real g5g6 passage (henry_wilkins_cherries) had a clean-enough goal "
                    "narrative AND non-coref-mis-resolved entity boundaries; g5v_tonish_colt has a "
                    "goal narrative (catch/tame colt) but strict_cb badly mis-resolves the colt "
                    "entity (merges into Tonish's cluster at 3/4 mentions) so was EXCLUDED, not "
                    "patched. N=1 is far below the drill's own N>=10 threshold -- directional only, "
                    "never used alone for a verdict band."
                ))


# ============================================================================ per-seed unit
def run_seed(seed: int) -> dict:
    passages = load_passages(GOLD_PATH_G5G6)
    bundles = [_passage_bundle(p) for p in passages]
    bundle_by_id = {b["passage_id"]: b for b in bundles}

    positive_control = _orig_coref_positive_control(seed)
    arm1_matched = _arm1_matched(bundles, seed)
    arm1_shuffled = _arm1_shuffled(bundles, seed)
    arm2 = _arm2_go(bundle_by_id["g5v_henry_wilkins_cherries"], seed)

    return dict(
        seed=seed,
        pc_net_auto=positive_control["net_auto"], pc_fires=positive_control["fires"],
        pc_n_applicable=positive_control["n_applicable"],
        arm1_n_items=arm1_matched["n_items"], arm1_n_applicable=arm1_matched["n_applicable"],
        arm1_net_auto=arm1_matched["net_auto"], arm1_net_oracle=arm1_matched["net_oracle"],
        arm1_agreement_rate=arm1_matched["agreement_rate"], arm1_item_ids=arm1_matched["item_ids"],
        arm1_rows=arm1_matched["rows"],
        arm1_shuffled_adopt_rate=arm1_shuffled["adopt_rate"], arm1_shuffled_rows=arm1_shuffled["rows"],
        arm2_adopt_coherent=arm2["adopt_coherent"], arm2_adopt_coherent_shuffled=arm2["adopt_coherent_shuffled"],
        arm2_row=arm2["row"], arm2_row_shuffled=arm2["row_shuffled"],
        arm2_data_availability_note=arm2["data_availability_note"],
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    def all_true(key):
        return all(per_seed[s][key] for s in seeds)

    pc_fires_all = all_true("pc_fires")
    pc_net_auto_mean = mean("pc_net_auto")
    positive_control_reproduces = bool(pc_fires_all and pc_net_auto_mean == 1.0)

    arm1_net_auto_mean = mean("arm1_net_auto")
    arm1_n_items = per_seed[seeds[0]]["arm1_n_items"]
    arm1_agreement_mean = mean("arm1_agreement_rate")
    arm1_shuffled_mean = mean("arm1_shuffled_adopt_rate")
    arm1_survives = bool(arm1_net_auto_mean is not None and arm1_net_auto_mean > 0)
    arm1_shuffled_collapses = bool(arm1_shuffled_mean is not None and arm1_shuffled_mean <= 0.25)

    arm2_adopt_all = all_true("arm2_adopt_coherent")
    arm2_shuffled_adopt_any = any(per_seed[s]["arm2_adopt_coherent_shuffled"] for s in seeds)
    arm2_survives_directional = bool(arm2_adopt_all and not arm2_shuffled_adopt_any)

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH"
    elif not positive_control_reproduces:
        verdict = "HARNESS_DEAD_POSITIVE_CONTROL_FAILED"
    elif arm1_n_items < 4:
        verdict = "HARD_FAIL_ARM1_UNDERPOWERED"
    elif not arm1_survives:
        verdict = "HARD_FAIL_COREF_WAS_LOAD_ARTIFACT"
    elif arm1_survives and not arm1_shuffled_collapses:
        verdict = "HARD_FAIL_LOAD_MATCHED_SIGNAL_IS_POSITIONAL_NOT_STRUCTURAL"
    elif arm1_survives and arm1_shuffled_collapses and arm2_survives_directional:
        verdict = "HARD_PASS_ARM1_SURVIVES_ARM2_DIRECTIONAL_SURVIVES"
    else:
        verdict = "MIDDLE_BAND_ARM1_SURVIVES_ARM2_INCONCLUSIVE"

    summary = (
        f"POSITIVE_CONTROL reproduces_net_auto_1.0={positive_control_reproduces} "
        f"(fires_all_seeds={pc_fires_all} net_auto_mean={pc_net_auto_mean}) | "
        f"ARM1(coref load-matched, n_items={arm1_n_items}) net_auto_mean={arm1_net_auto_mean} "
        f"agreement_mean={arm1_agreement_mean} survives={arm1_survives} | "
        f"ARM1_SHUFFLED adopt_rate_mean={arm1_shuffled_mean} collapses={arm1_shuffled_collapses} | "
        f"ARM2(goal-outcome fair, N=1 DIRECTIONAL ONLY) adopt_true_owner_all_seeds={arm2_adopt_all} "
        f"shuffled_adopts_any={arm2_shuffled_adopt_any} survives_directional={arm2_survives_directional}"
    )

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        means=dict(
            pc_net_auto=pc_net_auto_mean, arm1_net_auto=arm1_net_auto_mean,
            arm1_agreement_rate=arm1_agreement_mean, arm1_shuffled_adopt_rate=arm1_shuffled_mean,
        ),
        bands=dict(
            positive_control_reproduces=positive_control_reproduces, arm1_n_items=arm1_n_items,
            arm1_survives=arm1_survives, arm1_shuffled_collapses=arm1_shuffled_collapses,
            arm2_adopt_all_seeds=arm2_adopt_all, arm2_shuffled_adopt_any=arm2_shuffled_adopt_any,
            arm2_survives_directional=arm2_survives_directional,
        ),
        arm1_item_ids=per_seed[seeds[0]]["arm1_item_ids"],
        arm2_data_availability_note=per_seed[seeds[0]]["arm2_data_availability_note"],
        per_seed_arm1_rows_seed0=per_seed[seeds[0]]["arm1_rows"],
        per_seed_arm1_shuffled_rows_seed0=per_seed[seeds[0]]["arm1_shuffled_rows"],
        per_seed_arm2_row_seed0=per_seed[seeds[0]]["arm2_row"],
        per_seed_arm2_row_shuffled_seed0=per_seed[seeds[0]]["arm2_row_shuffled"],
        load_match_assertion_held=True,  # asserted inline in build_load_matched_coref_items; would
                                          # have raised AssertionError (crash) otherwise
        brain_fidelity_caveat=(
            "route_passage's aggregate is a single-pass integration over the whole passage/item -- "
            "a brain-COMPATIBLE approximation of Kintsch construction-integration / CA3 recurrent "
            "attractor settling, not full recurrent relaxation (per the design drill Section 2/3f). "
            "A HARD_PASS here licenses the one-shot approximation as sufficient for THIS item "
            "difficulty, not as fully brain-faithful."
        ),
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
              f"pc_net_auto={res['pc_net_auto']} arm1_net_auto={res['arm1_net_auto']} "
              f"arm1_n_items={res['arm1_n_items']} arm2_adopt={res['arm2_adopt_coherent']} "
              f"arm2_adopt_shuffled={res['arm2_adopt_coherent_shuffled']}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(out_dir).values()}
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(coref_d=COREF_D, coref_role_vocab=ROLE_VOCAB, coref_max_event_slots=MAX_EVENT_SLOTS,
                          go_role_vocab_ext=GO_ROLE_VOCAB_EXT, load_match_tol=LOAD_MATCH_TOL,
                          cand_mechanisms=CAND_MECHANISMS, abstain_band=ABSTAIN_BAND, seeds=seeds,
                          n_g5g6_passages=18, n_arm2_real_passages=1)
    agg["prereg"] = "notes/research_relational_backward_reach_coherence_selector.md (Sections 3, 6, 7)"
    agg["cites"] = [
        "hdlab/self_improving_loop.py (route_passage, reused verbatim)",
        "exp_coherence_aggregate_discriminates_goal_outcome_v1.py (_coref_arm positive-control, "
        "_shuffle_role_seq, _arms_must_differ_check, hash_stable, reused verbatim)",
        "experiments/exp_coref_autonomous_fix_router_v1.py (run_decay_window trap, reused verbatim)",
        "experiments/exp_wire_coref_accumulate_situation_model_v1.py (ROLE_VOCAB/D/MAX_EVENT_SLOTS/"
        "SEED/event_slots_for/name_anchor_map, sourced)",
        "notes/research_relational_backward_reach_coherence_selector.md (the design drill)",
    ]
    agg["per_seed"] = per_seed
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

    # (1) 18 g5g6 passages load + bundle construction
    passages = load_passages(GOLD_PATH_G5G6)
    assert len(passages) == 18, f"expected 18 g5g6 passages, got {len(passages)}"
    bundles = [_passage_bundle(p) for p in passages]
    bundle_by_id = {b["passage_id"]: b for b in bundles}

    # (2) load-matched item construction fires (>=4 items) and the load-match assertion holds
    # (build_load_matched_coref_items asserts internally; a bug would crash self-test here)
    items = build_load_matched_coref_items(bundles)
    assert len(items) >= 4, f"expected >=4 load-matched coref items, got {len(items)}: " \
                             f"{[it['id'] for it in items]}"
    for it in items:
        for p in it["flagged_positions"]:
            be = it["baseline_cluster_ids"][p]
            ce = it["true_cluster_ids"][p]
            assert be != ce, f"{it['id']} pos={p}: baseline==candidate, not a real disagreement"
            bl = _entity_load(it["baseline_cluster_ids"], p, be)
            cl = _entity_load(it["true_cluster_ids"], p, ce)
            assert bl == cl, f"{it['id']} pos={p}: LOAD-MATCH ASSERTION FAILED bl={bl} cl={cl}"

    # (3) arms-must-differ + shuffle actually differs (reused verbatim functions exercised for real)
    _arms_must_differ_check(items)
    shuffled = _shuffle_role_seq(items)
    for a, b in zip(items, shuffled):
        assert a["role_seq"] != b["role_seq"], f"shuffle no-op on {a['id']}"
        assert a["baseline_cluster_ids"] == b["baseline_cluster_ids"]
        assert a["event_slots"] == b["event_slots"]

    # (4) positive control reproduces net_auto=1.0 (the harness sanity gate)
    pc = _orig_coref_positive_control(0)
    assert pc["net_auto"] == 1.0, f"POSITIVE CONTROL FAILED: harness broken, net_auto={pc['net_auto']}"

    # (5) ARM2 item construction: henry_wilkins_cherries owner/foil are the entities claimed
    b_henry = bundle_by_id["g5v_henry_wilkins_cherries"]
    anchors = name_anchor_map(b_henry["stream"], b_henry["base_ids"])
    assert anchors.get("Henry") == "1", f"Henry anchor changed: {anchors}"
    assert anchors.get("old_gentleman") == "0", f"old_gentleman anchor changed: {anchors}"
    henry_load = sum(1 for c in b_henry["base_ids"] if c == "1")
    old_gent_load = sum(1 for c in b_henry["base_ids"] if c == "0")
    assert henry_load == old_gent_load, f"ARM2 real-passage load not naturally matched: " \
                                          f"Henry={henry_load} old_gentleman={old_gent_load}"
    go_item = _go_item_henry_wilkins_cherries(b_henry)
    assert go_item["baseline_cluster_ids"] != go_item["true_cluster_ids"]

    # (6) one full seed sanity (all pieces run to completion)
    res = run_seed(0)
    for k in ("pc_net_auto", "arm1_net_auto", "arm1_n_items", "arm2_adopt_coherent"):
        assert res[k] is not None, f"{k} missing"

    print(f"[SELFTEST PASS] positive_control net_auto={pc['net_auto']} "
          f"arm1_n_items={len(items)} arm1_item_ids={[it['id'] for it in items]} "
          f"seed0 arm1_net_auto={res['arm1_net_auto']} arm2_adopt={res['arm2_adopt_coherent']} "
          f"arm2_adopt_shuffled={res['arm2_adopt_coherent_shuffled']}", flush=True)
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
