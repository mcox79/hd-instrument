"""exp_c5_desiderative_aspectual_partition_goal_typing_v1 -- CLOSE the explicit_psych 2-item gap
(t03_beth "Beth hoped to win...", t12_jo "Jo hoped to finish...") left open by
exp_c5_real_coref_endtoend_purpose_infinitival_v1 (commit 78294a2c6), by PARTITIONING
`CONTROL_VERB_STOP` into DESIDERATIVE (goal-signaling) vs ASPECTUAL/IMPLICATIVE (not).

PRE-REG: preregs/2026-08-05_c5_desiderative_aspectual_partition_goal_typing_v1.md

WHY (disk-verified, task brief): the predecessor cell pre-registered and MEASURED that
explicit_psych stays at 16/18 under `c3_plus_purpose` because `action_frame_feats`'
`CONTROL_VERB_STOP` deliberately excludes ALL control verbs -- including desiderative ones
(hope/want/wish) -- from the purpose-infinitival construction feature, assuming C3's EXPERIENCER
lexicon covers them. C3 is OOV on "hoped" (MEASURED@notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md
"LANDED-2"): `action_frame_feats("Beth hoped to win a place at the summer fair.") == []` AND
`c3_has_desire(...) == False`, both independently verified inline before the predecessor cell's own
authoring (MEASURED@data/exp_c5_real_coref_endtoend_purpose_infinitival_v1/metrics.json).

THE FIX (principled, per task brief): "X hoped/wanted to VP" IS a goal reading -- a
DESIDERATIVE/intention verb governing the infinitival-purpose construction, verb-class-conditioned.
Partition the control-verb stop list:
  - DESIDERATIVE (hope/hoped, want/wanted, wish/wished, mean/meant, plan/planned, intend/intended,
    aim/aimed, long/longed, yearn/yearned, desire/desired) -> REMOVED from the stop set: the
    infinitival now fires `purpose_to_no_det` even when C3 is OOV on the governing verb.
  - ASPECTUAL/IMPLICATIVE (begin/began, start/started, try/tried, fail/failed, manage/managed,
    happen/happened, cease/ceased, stop/stopped, continue/continued) -> STAYS in the stop set:
    "X began/tried/failed to VP" is NOT a goal-ownership signal.
Desiderative verbs are fired via the CONSTRUCTION path (the same `purpose_to_no_det` feature +
MDL-induced rule the predecessor cell already validated), NOT added to C3's EXPERIENCER frame
lexicon (a desirer is not an emotion-undergoer -- mislabeling would conflate two different frames).

Prior-work check (SUBSTRATE-KB, mandatory before authoring):
`tools/substrate_query.sh "desiderative aspectual verb partition goal typing purpose infinitival
control verb stop hope want wish begin try fail"` returned top cosine=0.2881 (a WordNet
'infinitival' entity) -- ALL hits below the 0.30 rediscovery threshold. No prior cell implements
this partition; genuinely novel extension of the exp_c5_generative_goal_typing_action_frame_v1 /
exp_c5_real_coref_endtoend_purpose_infinitival_v1 family, not a rediscovery.

WIRE-DON'T-ISLAND / REUSE (zero modification to any reused module -- all four imported bit-identical):
  - `exp_c5_real_coref_endtoend_purpose_infinitival_v1` (aliased PREVMOD below): `load_bank`,
    `item_to_mentions`, `resolve_outcome_coref`, `resolve_outcome_recency_positional`,
    `build_role_seq`, `_outcome_pos`, `type_sentence_events_c3`, `baseline_first_mention`,
    `baseline_nearest_subject`, `baseline_majority` -- all GENERIC w.r.t. typing mode, reused as-is.
  - `exp_c5_generative_goal_typing_action_frame_v1`: `induce_hypothesis`, `DET_STOP`,
    `DIRECTIONAL_PP` (constants reused; the MDL hypothesis is reused VERBATIM because the feature
    NAME `purpose_to_no_det` is unchanged here -- only which sentences make it fire changes).
  - `hdlab.learner.apply`, `hdlab.goal_owner_select.directed_goal_outcome_score`,
    `hdlab.self_improving_loop.decide_keep_or_revert` -- the promoted C5 integrator, untouched.
  - `hdlab/`, `exp_component5_wired_endtoend_v1.py`,
    `exp_c5_generative_goal_typing_action_frame_v1.py`,
    `exp_c5_real_coref_endtoend_purpose_infinitival_v1.py` are all imported-only, NOT edited.
The ONLY new code: `ASPECTUAL_STOP`/`DESIDERATIVE_PASS`/`OTHER_STOP_UNCHANGED` sets,
`action_frame_feats_partitioned()`, `type_sentence_events_partitioned()` typer wrapper,
`run_item_typer()` (a typer-parametrized generalization of PREVMOD.run_item, same logic verified
against PREVMOD's own source), the aspectual precision probe bank (7 hand-authored items), and the
aggregate/verdict/self-test/checkpoint harness.

Cites: notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md (task brief diagnosis);
experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py (harness under extension);
experiments/exp_c5_generative_goal_typing_action_frame_v1.py (purpose-infinitival detector,
CONTROL_VERB_STOP under partition); experiments/exp_component5_wired_endtoend_v1.py
(type_sentence_events_c3/c3_has_desire, reused); hdlab/goal_owner_select.py;
hdlab/self_improving_loop.py; hdlab/learner/ (ruleind plugin).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "c5_desiderative_aspectual_partition_goal_typing_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- REUSED BIT-IDENTICAL: the real-coref end-to-end harness (generic helpers) ------------------
import exp_c5_real_coref_endtoend_purpose_infinitival_v1 as PREVMOD  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the purpose-infinitival detector's constants + MDL induction ---------
from exp_c5_generative_goal_typing_action_frame_v1 import (  # noqa: E402
    DET_STOP, DIRECTIONAL_PP, induce_hypothesis,
)
from exp_situation_model_goal_outcome_dimension_v1 import (  # noqa: E402
    R_GOAL, _ordered_tokens, _sentences,
)
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402
from hdlab.learner import apply as learner_apply  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
TYPING_MODES = ("c3_only", "c3_plus_purpose_original", "c3_plus_purpose_partitioned")
VERB_TYPES = ("explicit_psych", "action_implied")

# ============================================================================ THE PARTITION (new)
# DESIDERATIVE/intention verbs -- goal-signaling; REMOVED from the stop set so "X <verb> to VP"
# fires purpose_to_no_det via the CONSTRUCTION path even when C3's EXPERIENCER lexicon is OOV.
DESIDERATIVE_PASS = {
    "hope", "hopes", "hoped", "want", "wants", "wanted", "wish", "wishes", "wished",
    "mean", "means", "meant", "plan", "plans", "planned", "intend", "intends", "intended",
    "aim", "aims", "aimed", "long", "longs", "longed", "yearn", "yearns", "yearned",
    "desire", "desires", "desired",
}
# ASPECTUAL/IMPLICATIVE verbs -- NOT goal-signaling ("X began/tried/failed to VP" is not a goal
# ownership signal); STAYS in the stop set.
ASPECTUAL_STOP = {
    "begin", "begins", "began", "start", "starts", "started",
    "try", "tries", "tried", "fail", "fails", "failed",
    "manage", "manages", "managed", "happen", "happens", "happened",
    "cease", "ceases", "ceased", "stop", "stops", "stopped",
    "continue", "continues", "continued",
}
# Unclassified by the task brief (not desiderative, not named aspectual) -- conservatively LEFT in
# the stop set: no behavior change, precision-safe default.
OTHER_STOP_UNCHANGED = {
    "decide", "decides", "decided", "need", "needs", "needed", "seem", "seems", "seemed",
    "get", "gets", "got", "choose", "chooses", "chose",
}
PARTITIONED_STOP = ASPECTUAL_STOP | OTHER_STOP_UNCHANGED
assert DESIDERATIVE_PASS.isdisjoint(PARTITIONED_STOP), "partition must be disjoint by construction"


def action_frame_feats_partitioned(sentence: str):
    """Same structural detector as exp_c5_generative_goal_typing_action_frame_v1.action_frame_feats
    (verb-lemma-independent 'to VP' vs 'to NP' distinction), but the control-verb exclusion is the
    PARTITIONED stop set: aspectual/unclassified verbs still block the feature; desiderative verbs
    no longer do. Feature NAME (`purpose_to_no_det`) is unchanged so the predecessor cell's
    MDL-induced hypothesis applies verbatim."""
    toks = _ordered_tokens(sentence)
    feats = []
    has_purpose_inf = False
    for i in range(len(toks) - 1):
        if toks[i] != "to" or toks[i + 1] in DET_STOP:
            continue
        preceding = toks[i - 1] if i > 0 else None
        if preceding in PARTITIONED_STOP:
            continue
        has_purpose_inf = True
        break
    if has_purpose_inf:
        feats.append("purpose_to_no_det")
    if any(w in toks for w in DIRECTIONAL_PP):
        feats.append("has_directional_pp")
    return feats


def type_sentence_events_partitioned(sentence, subject, plugin_name, hypothesis):
    """c3_only events UNIONED with a GOAL event iff the PARTITIONED purpose-infinitival detector
    fires and the subject doesn't already have a GOAL. Same union pattern as PREVMOD's own
    type_sentence_events_union, only the feature extractor differs."""
    events = PREVMOD.type_sentence_events_c3(sentence, subject)
    feats = action_frame_feats_partitioned(sentence)
    pred = learner_apply(plugin_name, hypothesis, feats, key=None, default_class="NOT_GOAL")
    already_goal = any(r == R_GOAL and e == subject for (e, r) in events)
    if pred == "GOAL" and subject is not None and not already_goal:
        events = list(events) + [(subject, R_GOAL)]
    return events


def typer_for_mode(mode: str, plugin_name, hypothesis):
    if mode == "c3_only":
        return lambda sentence, subject: PREVMOD.type_sentence_events_c3(sentence, subject)
    if mode == "c3_plus_purpose_original":
        return lambda sentence, subject: PREVMOD.type_sentence_events_union(
            sentence, subject, plugin_name, hypothesis)
    if mode == "c3_plus_purpose_partitioned":
        return lambda sentence, subject: type_sentence_events_partitioned(
            sentence, subject, plugin_name, hypothesis)
    raise ValueError(f"unknown typing_mode {mode!r}")


# ============================================================================ typer-parametrized run_item
# Generalization of PREVMOD.run_item that takes a typer CALLABLE directly instead of a mode string
# (PREVMOD.typer_for_mode only knows its own two modes). Logic verified identical to PREVMOD.run_item
# line-for-line; reuses PREVMOD's generic (typer-independent) helper functions throughout.
def run_item_typer(item: dict, typer, seed: int):
    gold = item["gold_outcome_owner"]
    foil = item.get("foil")

    baseline_owner = PREVMOD.resolve_outcome_recency_positional(item)
    role_seq_b, cluster_ids_b = PREVMOD.build_role_seq(item, baseline_owner, typer)
    outcome_pos = PREVMOD._outcome_pos(role_seq_b)

    coref_owner = PREVMOD.resolve_outcome_coref(item)
    role_seq_c, cluster_ids_c = PREVMOD.build_role_seq(item, coref_owner, typer)
    assert role_seq_b == role_seq_c, (
        f"{item['id']}: role attribution must be resolver-independent: {role_seq_b} vs {role_seq_c}")

    goal_present = R_GOAL in role_seq_b
    row = dict(id=item["id"], gold=gold, baseline_owner=baseline_owner, coref_owner=coref_owner,
               goal_present=goal_present, baseline_matches_gold=(baseline_owner == gold))

    if outcome_pos is None:
        row.update(final_owner=None, matches_gold=False, adopt=None,
                    scrambled_final_owner=None, scrambled_matches_gold=None)
        return row

    score_b = directed_goal_outcome_score(role_seq_b, cluster_ids_b, seed, outcome_pos)
    score_c = directed_goal_outcome_score(role_seq_c, cluster_ids_c, seed, outcome_pos)
    adopt = decide_keep_or_revert({"content": score_c - score_b}, ABSTAIN_BAND_DEFAULT)
    final_owner = cluster_ids_c[outcome_pos] if adopt == "content" else cluster_ids_b[outcome_pos]
    row.update(final_owner=final_owner, matches_gold=(final_owner == gold), adopt=adopt,
               directed_score_baseline=score_b, directed_score_content=score_c)

    if foil is not None:
        role_seq_s, cluster_ids_s = PREVMOD.build_role_seq(item, coref_owner, typer,
                                                             scramble_goal_to_foil=foil)
        score_s = directed_goal_outcome_score(role_seq_s, cluster_ids_s, seed, outcome_pos)
        adopt_s = decide_keep_or_revert({"content": score_s - score_b}, ABSTAIN_BAND_DEFAULT)
        scrambled_owner = cluster_ids_s[outcome_pos] if adopt_s == "content" else cluster_ids_b[outcome_pos]
        row.update(scrambled_final_owner=scrambled_owner,
                    scrambled_matches_gold=(scrambled_owner == gold))
    else:
        row.update(scrambled_final_owner=None, scrambled_matches_gold=None)
    return row


# ============================================================================ per-seed unit (bank subsets)
def run_seed(seed: int, plugin_name, hypothesis):
    out = {}
    for verb_type in VERB_TYPES:
        core, twins = PREVMOD.load_bank(verb_type)
        out[verb_type] = {}
        for mode in TYPING_MODES:
            typer = typer_for_mode(mode, plugin_name, hypothesis)
            core_rows = [run_item_typer(it, typer, seed) for it in core]
            twin_rows = [run_item_typer(it, typer, seed) for it in twins]
            div = [r for r in core_rows if not r["baseline_matches_gold"]]
            n_div = len(div)

            def rate(rows_, key):
                vals = [r[key] for r in rows_ if r[key] is not None]
                return round(sum(bool(v) for v in vals) / len(vals), 4) if vals else None

            out[verb_type][mode] = dict(
                n_core=len(core_rows), n_twin=len(twin_rows), n_divergent=n_div,
                recency_floor_divergent=rate(div, "baseline_matches_gold"),
                system_accuracy_divergent=rate(div, "matches_gold"),
                system_scrambled_accuracy_divergent=rate(
                    [r for r in div if r["scrambled_final_owner"] is not None], "scrambled_matches_gold"),
                twin_control_accuracy=rate(twin_rows, "matches_gold"),
                n_goal_present_core=sum(1 for r in core_rows if r["goal_present"]),
                miss_ids=[r["id"] for r in div if not r["matches_gold"]],
                core_rows=core_rows, twin_rows=twin_rows,
            )
        div_ids = {r["id"] for r in out[verb_type]["c3_only"]["core_rows"] if not r["baseline_matches_gold"]}
        div_items = [it for it in core if it["id"] in div_ids]

        def pos_rate(fn):
            vals = [(fn(it) == it["gold_outcome_owner"]) for it in div_items]
            return round(sum(vals) / len(vals), 4) if vals else None

        out[verb_type]["positional_baselines_divergent"] = dict(
            recency=0.0 if div_items else None,
            first_mention=pos_rate(PREVMOD.baseline_first_mention),
            nearest_subject=pos_rate(PREVMOD.baseline_nearest_subject),
            majority=pos_rate(PREVMOD.baseline_majority),
        )
        out[verb_type]["n_divergent"] = len(div_items)

    # ---- ASPECTUAL PRECISION PROBE (new bank, hand-authored, NOT in goal_owner_fair_v1.jsonl) ----
    probe_rows = {}
    for mode in TYPING_MODES:
        typer = typer_for_mode(mode, plugin_name, hypothesis)
        probe_rows[mode] = [run_item_typer(it, typer, seed) for it in ASPECTUAL_PRECISION_PROBE]
    out["aspectual_precision_probe"] = dict(
        n=len(ASPECTUAL_PRECISION_PROBE),
        false_goal_count=sum(1 for r in probe_rows["c3_plus_purpose_partitioned"] if r["goal_present"]),
        goal_present_ids=[r["id"] for r in probe_rows["c3_plus_purpose_partitioned"] if r["goal_present"]],
        matches_c3_only=all(
            probe_rows["c3_plus_purpose_partitioned"][i]["matches_gold"] ==
            probe_rows["c3_only"][i]["matches_gold"]
            for i in range(len(ASPECTUAL_PRECISION_PROBE))),
        rows=probe_rows,
    )
    return dict(seed=seed, per_verb_type=out)


# ============================================================================ aspectual precision probe bank
# 7 hand-authored items, one per ASPECTUAL verb (stopped/happened excluded from the PROBE SENTENCES
# themselves -- both are genuinely construction-ambiguous in English ("stopped to VP"/"happened to
# VP" can read as purpose-adjunct or evidential, not cleanly implicative-complement -- a false-fire
# there would be inconclusive by construction); both verbs remain in ASPECTUAL_STOP regardless.
# Structurally identical to real bank items (owner + foil + recency-trap pronoun outcome); S2/S3
# templates reused VERBATIM from real goal_owner_fair_v1.jsonl items (known to trigger R_UNMET).
def _mk_probe(pid, owner, verb, clause, foil, s2, s3):
    return dict(id=pid, owner=owner, foil=foil, roster={owner: "f", foil: "f"},
                verb_type="aspectual_probe", outcome_polarity="unmet", has_distractor=True,
                twin_of=None, gold_outcome_owner=owner,
                text=f"{owner.capitalize()} {verb} to {clause}. {s2} {s3}")


ASPECTUAL_PRECISION_PROBE = [
    _mk_probe("p01_dawn_gate_foil_eve", "dawn", "began", "open the gate", "eve",
              "Eve hurried off toward the house.", "Left unwarned, she went down through the ice."),
    _mk_probe("p02_fay_shop_foil_gwen", "fay", "started", "close the shop", "gwen",
              "Gwen hurried up the path first.", "Held back at the door, she never rang it and was sorry."),
    _mk_probe("p03_ivy_crate_foil_kay", "ivy", "tried", "lift the crate", "kay",
              "Kay walked briskly on ahead.", "Kept from the gate, she missed her turn and was sorry."),
    _mk_probe("p04_liv_fence_foil_mae", "liv", "failed", "mend the fence", "mae",
              "Mae went off early toward the barn.", "Too late at the gate, she missed it and was sorry."),
    _mk_probe("p05_nia_cart_foil_opal", "nia", "managed", "fix the cart", "opal",
              "Opal walked swiftly on toward the village.", "Alone on the bank, she never crossed and was sorry."),
    _mk_probe("p06_posy_plan_foil_reya", "posy", "ceased", "protest the plan", "reya",
              "Reya went off early to the barn.", "Caught in the field, she failed and was sorry."),
    _mk_probe("p07_sana_flock_foil_tess", "sana", "continued", "guard the flock", "tess",
              "Tess strode on quickly ahead.", "Far behind, he fell through and was sorry."),
]


# ============================================================================ arms-must-differ (META_RULE_AF)
def _arms_must_differ(per_seed0):
    digests = {}
    for verb_type in VERB_TYPES:
        for mode in TYPING_MODES:
            core_rows = per_seed0["per_verb_type"][verb_type][mode]["core_rows"]
            blob = json.dumps([(r["id"], r["final_owner"], r["goal_present"]) for r in core_rows],
                               sort_keys=True).encode("utf-8")
            digests[f"{verb_type}/{mode}"] = hashlib.sha256(blob).hexdigest()
    a = "explicit_psych/c3_only"
    b = "explicit_psych/c3_plus_purpose_partitioned"
    differ = digests[a] != digests[b]
    return digests, differ


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())
    n = len(seeds)
    gated_baseline_names = ("recency", "nearest_subject")

    def mean(verb_type, mode, key):
        vals = [per_seed[s]["per_verb_type"][verb_type][mode][key] for s in seeds
                if per_seed[s]["per_verb_type"][verb_type][mode][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    per_vt = {}
    subset_verdicts = {}
    for verb_type in VERB_TYPES:
        pos_base = per_seed[seeds[0]]["per_verb_type"][verb_type]["positional_baselines_divergent"]
        n_divergent = per_seed[seeds[0]]["per_verb_type"][verb_type]["n_divergent"]
        modes = {}
        for mode in TYPING_MODES:
            modes[mode] = dict(
                n_core=per_seed[seeds[0]]["per_verb_type"][verb_type][mode]["n_core"],
                n_divergent=per_seed[seeds[0]]["per_verb_type"][verb_type][mode]["n_divergent"],
                recency_floor_divergent=mean(verb_type, mode, "recency_floor_divergent"),
                system_accuracy_divergent=mean(verb_type, mode, "system_accuracy_divergent"),
                system_scrambled_accuracy_divergent=mean(
                    verb_type, mode, "system_scrambled_accuracy_divergent"),
                miss_ids_seed0=per_seed[seeds[0]]["per_verb_type"][verb_type][mode]["miss_ids"],
            )

        acc_c3_only = modes["c3_only"]["system_accuracy_divergent"]
        acc_orig = modes["c3_plus_purpose_original"]["system_accuracy_divergent"]
        acc_part = modes["c3_plus_purpose_partitioned"]["system_accuracy_divergent"]

        gated_vals = [pos_base[k] for k in gated_baseline_names if pos_base.get(k) is not None]
        beats_gated_positional = (
            acc_part is not None and gated_vals and all(acc_part > v for v in gated_vals))

        unscr = modes["c3_plus_purpose_partitioned"]["system_accuracy_divergent"]
        scr = modes["c3_plus_purpose_partitioned"]["system_scrambled_accuracy_divergent"]
        floor = modes["c3_plus_purpose_partitioned"]["recency_floor_divergent"]
        gain_unscr = (unscr - floor) if (unscr is not None and floor is not None) else None
        gain_scr = (scr - floor) if (scr is not None and floor is not None) else None
        if gain_unscr is not None and gain_unscr > 1e-9:
            scramble_collapses = (gain_scr is not None and gain_scr <= 0.5 * gain_unscr + 1e-9)
            scramble_vacuous = False
        else:
            scramble_collapses = (gain_scr is not None and gain_scr <= 1e-9)
            scramble_vacuous = True

        n_div = modes["c3_plus_purpose_partitioned"]["n_divergent"]
        no_regression_vs_orig = (acc_part is not None and acc_orig is not None and acc_part >= acc_orig)

        if verb_type == "explicit_psych":
            hard_pass_thresh = 17.0 / 18.0 if n_div == 18 else (1.0 - 1.0 / max(n_div, 1))
            if (acc_part is not None and acc_part >= hard_pass_thresh - 1e-9
                    and no_regression_vs_orig and beats_gated_positional and scramble_collapses
                    and not scramble_vacuous):
                v = "HARD_PASS_RECOVERED_DESIDERATIVE_PARTITION"
            elif acc_part is not None and acc_orig is not None and acc_part < acc_orig:
                v = "HARD_FAIL_REGRESSION_FROM_PARTITION"
            elif acc_part is not None and acc_orig is not None and acc_part == acc_orig:
                v = "MIDDLE_BAND_NO_CHANGE_FROM_ORIGINAL"
            else:
                v = "MIDDLE_BAND"
        else:  # action_implied
            holds_at_landed_1p0 = (acc_part is not None and acc_part >= 1.0 - 1e-9)
            if (holds_at_landed_1p0 and no_regression_vs_orig and beats_gated_positional
                    and scramble_collapses and not scramble_vacuous):
                v = "MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS" if n_div < 30 else "HARD_PASS"
            elif not holds_at_landed_1p0 or not no_regression_vs_orig:
                v = "HARD_FAIL_ACTION_IMPLIED_REGRESSION"
            else:
                v = "MIDDLE_BAND"

        subset_verdicts[verb_type] = v
        per_vt[verb_type] = dict(
            n_divergent=n_divergent, positional_baselines_divergent=pos_base,
            gated_baseline_names=list(gated_baseline_names), modes=modes,
            beats_gated_positional=beats_gated_positional, scramble_collapses=scramble_collapses,
            scramble_vacuous=scramble_vacuous, no_regression_vs_original=no_regression_vs_orig,
            verdict=v,
        )

    # ---- aspectual precision probe (make-or-break gate, per task brief) ----
    probe0 = per_seed[seeds[0]]["per_verb_type"]["aspectual_precision_probe"]
    false_goal_counts = [per_seed[s]["per_verb_type"]["aspectual_precision_probe"]["false_goal_count"]
                          for s in seeds]
    matches_c3_only_all = all(
        per_seed[s]["per_verb_type"]["aspectual_precision_probe"]["matches_c3_only"] for s in seeds)
    precision_clean = (max(false_goal_counts) == 0) and matches_c3_only_all

    def rank_of(v):
        if v.startswith("HARD_FAIL"):
            return 0
        if v.startswith("HARD_PASS"):
            return 2
        return 1

    overall_rank = min(rank_of(subset_verdicts[vt]) for vt in VERB_TYPES)
    if not precision_clean:
        overall = "HARD_FAIL"
        overall_reason = "ASPECTUAL_PRECISION_PROBE_OVERFIRE"
    else:
        overall = {0: "HARD_FAIL", 1: "MIDDLE_BAND", 2: "HARD_PASS"}[overall_rank]
        overall_reason = "worse_of_two_subsets_precision_clean"

    msg = (
        f"explicit_psych: c3_only={per_vt['explicit_psych']['modes']['c3_only']['system_accuracy_divergent']} "
        f"orig={per_vt['explicit_psych']['modes']['c3_plus_purpose_original']['system_accuracy_divergent']} "
        f"partitioned={per_vt['explicit_psych']['modes']['c3_plus_purpose_partitioned']['system_accuracy_divergent']} "
        f"(N_div={per_vt['explicit_psych']['n_divergent']}, verdict={subset_verdicts['explicit_psych']}). "
        f"action_implied: c3_only={per_vt['action_implied']['modes']['c3_only']['system_accuracy_divergent']} "
        f"orig={per_vt['action_implied']['modes']['c3_plus_purpose_original']['system_accuracy_divergent']} "
        f"partitioned={per_vt['action_implied']['modes']['c3_plus_purpose_partitioned']['system_accuracy_divergent']} "
        f"(N_div={per_vt['action_implied']['n_divergent']}, verdict={subset_verdicts['action_implied']}). "
        f"aspectual_precision_probe: N={probe0['n']} false_goal_count(max over seeds)={max(false_goal_counts)} "
        f"matches_c3_only_all_seeds={matches_c3_only_all} clean={precision_clean}. "
        f"OVERALL={overall} ({overall_reason}).")

    return dict(
        verdict=overall, verdict_msg=f"{overall}: {msg}", summary=msg, n_seeds=n,
        subset_verdicts=subset_verdicts, per_verb_type=per_vt,
        aspectual_precision_probe=dict(
            n=probe0["n"], false_goal_count_per_seed=false_goal_counts,
            false_goal_count_max=max(false_goal_counts),
            goal_present_ids_seed0=probe0["goal_present_ids"],
            matches_c3_only_all_seeds=matches_c3_only_all, clean=precision_clean,
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


def run(run_mode: str):
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_json(os.path.join(OUTPUT_DIR, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
                 "expected_n_units": EXPECTED_N_SEEDS})

    plugin_name, chosen, _all_results = induce_hypothesis()
    if chosen is None:
        raise RuntimeError("MDL model-selection returned KEEP_EPISODIC -- no rule induced")
    hypothesis = chosen.hypothesis
    print(f"[induce] plugin={plugin_name} n_rules={chosen.metrics.get('n_rules')} "
          f"compression_ratio={chosen.compression_ratio:.3f}", flush=True)

    done = completed_units(OUTPUT_DIR)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, plugin_name, hypothesis)
        record_unit(OUTPUT_DIR, k, res)
        pv = res["per_verb_type"]
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"explicit_psych(c3_only={pv['explicit_psych']['c3_only']['system_accuracy_divergent']}, "
              f"partitioned={pv['explicit_psych']['c3_plus_purpose_partitioned']['system_accuracy_divergent']}) "
              f"action_implied(c3_only={pv['action_implied']['c3_only']['system_accuracy_divergent']}, "
              f"partitioned={pv['action_implied']['c3_plus_purpose_partitioned']['system_accuracy_divergent']}) "
              f"probe_false_goal_count={pv['aspectual_precision_probe']['false_goal_count']}",
              flush=True)

    raw = load_units(OUTPUT_DIR)
    per_seed = {int(v["seed"]): v for v in raw.values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")

    digests, differ = _arms_must_differ(per_seed[SEEDS[0]])
    if not differ:
        raise AssertionError(f"META_RULE_AF VIOLATION: typing modes bit-identical on explicit_psych: {digests}")

    agg = aggregate(per_seed)
    agg["arms_differ_verified"] = True
    agg["arms_digests"] = digests
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(seeds=SEEDS, typing_modes=list(TYPING_MODES), verb_types=list(VERB_TYPES),
                         abstain_band=ABSTAIN_BAND_DEFAULT, bank_path=PREVMOD.BANK_PATH,
                         scope="explicit_psych+action_implied x trap_type=recency + aspectual_precision_probe(N=7)",
                         cardinality_ok=(len(per_seed) == EXPECTED_N_SEEDS), induced_plugin=plugin_name,
                         desiderative_pass=sorted(DESIDERATIVE_PASS), aspectual_stop=sorted(ASPECTUAL_STOP),
                         other_stop_unchanged=sorted(OTHER_STOP_UNCHANGED))
    agg["hp_scope"] = {
        "explicit_psych/c3_plus_purpose_partitioned": ["hard_pass_thresh_17_of_18",
            "no_regression_vs_original", "beats_gated_positional", "scramble_collapses"],
        "action_implied/c3_plus_purpose_partitioned": ["holds_at_landed_1p0", "no_regression_vs_original",
            "beats_gated_positional", "scramble_collapses"],
        "aspectual_precision_probe": ["false_goal_count_eq_0_all_seeds", "matches_c3_only_all_seeds"],
        "c3_only": ["reported_only_not_hard_pass_gated"],
        "c3_plus_purpose_original": ["reported_only_positive_control_reproduction"],
    }
    agg["final_metrics_atomicity"] = "tmp_replace"
    agg["crlb_n/a"] = "boolean-match discriminator (owner-selection accuracy), not an SNR/argmax-noise regime"
    agg["prereg"] = "preregs/2026-08-05_c5_desiderative_aspectual_partition_goal_typing_v1.md"
    agg["cites"] = [
        "notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md (task brief diagnosis)",
        "experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py (harness under extension, reused)",
        "experiments/exp_c5_generative_goal_typing_action_frame_v1.py (DET_STOP/DIRECTIONAL_PP/induce_hypothesis, reused)",
        "experiments/exp_component5_wired_endtoend_v1.py (type_sentence_events_c3/c3_has_desire, reused via PREVMOD)",
        "hdlab/goal_owner_select.py (directed_goal_outcome_score, reused)",
        "hdlab/self_improving_loop.py (decide_keep_or_revert, reused)",
        "hdlab/learner/ (ruleind plugin, config-only MDL registry, reused)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (1) partition is disjoint by construction
    assert DESIDERATIVE_PASS.isdisjoint(ASPECTUAL_STOP) and DESIDERATIVE_PASS.isdisjoint(OTHER_STOP_UNCHANGED)
    print(f"[SELFTEST 1/8] DESIDERATIVE_PASS ({len(DESIDERATIVE_PASS)}) disjoint from "
          f"ASPECTUAL_STOP+OTHER ({len(PARTITIONED_STOP)})", flush=True)

    # (2) feature-level: desiderative-governed infinitival NOW fires; aspectual-governed does NOT
    assert "purpose_to_no_det" in action_frame_feats_partitioned(
        "Beth hoped to win a place at the summer fair.")
    assert "purpose_to_no_det" in action_frame_feats_partitioned(
        "Jo hoped to finish planting the garden before noon.")
    assert "purpose_to_no_det" not in action_frame_feats_partitioned("Dawn began to open the gate.")
    assert "purpose_to_no_det" not in action_frame_feats_partitioned("Fay started to close the shop.")
    print("[SELFTEST 2/8] partitioned feature fires on 'hoped to VP', NOT on 'began/started to VP'",
          flush=True)

    # (3) MDL induction (reused, feature name unchanged) still produces a rule using the feature
    plugin_name, chosen, _ = induce_hypothesis()
    assert chosen is not None, "MDL model-selection returned KEEP_EPISODIC"
    hyp = chosen.hypothesis
    uses_feat = any("purpose_to_no_det" in r.get("conjunct", []) for r in hyp.get("rules", []))
    assert uses_feat, f"induced hypothesis does not use purpose_to_no_det: {hyp}"
    print(f"[SELFTEST 3/8] induced hypothesis (plugin={plugin_name}) uses purpose_to_no_det", flush=True)

    # (4) t03/t12 RECOVER end-to-end under c3_plus_purpose_partitioned
    ep_core, _ep_twins = PREVMOD.load_bank("explicit_psych")
    it_beth = next(it for it in ep_core if it["id"] == "t03_beth_fair_foil_ruth")
    it_jo = next(it for it in ep_core if it["id"] == "t12_jo_garden_foil_ruth")
    typer_part = typer_for_mode("c3_plus_purpose_partitioned", plugin_name, hyp)
    row_beth = run_item_typer(it_beth, typer_part, seed=0)
    row_jo = run_item_typer(it_jo, typer_part, seed=0)
    assert row_beth["goal_present"] is True, f"expected GOAL to fire for t03_beth: {row_beth}"
    assert row_jo["goal_present"] is True, f"expected GOAL to fire for t12_jo: {row_jo}"
    assert row_beth["matches_gold"] is True, f"expected t03_beth to recover end-to-end: {row_beth}"
    assert row_jo["matches_gold"] is True, f"expected t12_jo to recover end-to-end: {row_jo}"
    print(f"[SELFTEST 4/8] t03_beth and t12_jo RECOVER under c3_plus_purpose_partitioned "
          f"(goal_present=True, matches_gold=True both)", flush=True)

    # (5) c3_only still misses both (sanity: the gap is real, not stale)
    typer_c3 = typer_for_mode("c3_only", plugin_name, hyp)
    row_beth_c3 = run_item_typer(it_beth, typer_c3, seed=0)
    row_jo_c3 = run_item_typer(it_jo, typer_c3, seed=0)
    assert row_beth_c3["goal_present"] is False and row_jo_c3["goal_present"] is False, (
        f"expected c3_only to still miss both: {row_beth_c3}, {row_jo_c3}")
    print("[SELFTEST 5/8] c3_only still misses GOAL on t03_beth/t12_jo (confirms targeted gap real)",
          flush=True)

    # (6) ASPECTUAL PRECISION PROBE: 0 false GOALs, no side-effect on owner selection (make-or-break)
    typer_orig = typer_for_mode("c3_plus_purpose_original", plugin_name, hyp)
    n_false_goal = 0
    for it in ASPECTUAL_PRECISION_PROBE:
        r_part = run_item_typer(it, typer_part, seed=0)
        r_c3 = run_item_typer(it, typer_c3, seed=0)
        if r_part["goal_present"]:
            n_false_goal += 1
        assert r_part["matches_gold"] == r_c3["matches_gold"], (
            f"{it['id']}: partitioned typer changed owner-selection outcome vs c3_only: "
            f"{r_part} vs {r_c3}")
    assert n_false_goal == 0, (
        f"META_RULE PRECISION VIOLATION: partitioned typer fired GOAL on {n_false_goal}/"
        f"{len(ASPECTUAL_PRECISION_PROBE)} aspectual-verb probe items")
    print(f"[SELFTEST 6/8] aspectual precision probe: 0/{len(ASPECTUAL_PRECISION_PROBE)} false GOALs, "
          f"owner-selection identical to c3_only on all items", flush=True)

    # (7) action_implied holds at 10/10 under partitioned (no regression vs original union)
    ai_core, _ai_twins = PREVMOD.load_bank("action_implied")
    ai_rows_orig = [run_item_typer(it, typer_orig, seed=0) for it in ai_core]
    ai_rows_part = [run_item_typer(it, typer_part, seed=0) for it in ai_core]
    div_orig = [r for r in ai_rows_orig if not r["baseline_matches_gold"]]
    div_part = [r for r in ai_rows_part if not r["baseline_matches_gold"]]
    assert len(div_orig) == len(div_part) and len(div_orig) > 0
    acc_orig = sum(r["matches_gold"] for r in div_orig) / len(div_orig)
    acc_part = sum(r["matches_gold"] for r in div_part) / len(div_part)
    assert acc_part >= acc_orig - 1e-9, (
        f"action_implied regression: original={acc_orig} partitioned={acc_part}")
    print(f"[SELFTEST 7/8] action_implied divergent accuracy: original={acc_orig} "
          f"partitioned={acc_part} (no regression, N_div={len(div_part)})", flush=True)

    # (8) ARMS-MUST-DIFFER at aggregate level
    res = run_seed(0, plugin_name, hyp)
    digests, differ = _arms_must_differ(res)
    assert differ, f"META_RULE_AF: typing modes bit-identical on explicit_psych: {digests}"
    print("[SELFTEST 8/8] typing modes diverge on explicit_psych full item set", flush=True)

    return {"induced_plugin": plugin_name, "t03_beth_row": row_beth, "t12_jo_row": row_jo,
            "aspectual_probe_false_goal_count": n_false_goal,
            "action_implied_orig_vs_partitioned": {"orig": acc_orig, "partitioned": acc_part}}


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        res = self_test()
        print(json.dumps(res, indent=2, default=str))
        print("[SELFTEST PASS]")
        raise SystemExit(0)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
