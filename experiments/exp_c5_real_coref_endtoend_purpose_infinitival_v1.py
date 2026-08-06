"""exp_c5_real_coref_endtoend_purpose_infinitival_v1 -- WIRE-DON'T-ISLAND: splice the ALREADY-
PROVEN purpose-infinitival generative goal-typer (exp_c5_generative_goal_typing_action_frame_v1's
action_frame_feats + MDL-induced ruleind hypothesis, HARD_PASS 8/10 action_implied) into the
real-coref end-to-end's (exp_c5_real_coref_endtoend_v1) GOAL-detection path, and re-measure on
BOTH the explicit_psych and action_implied divergent subsets of the fair instrument. Production
event_role coref mode is KEPT UNCHANGED (commit a9e873ab0 default); the ONE variable is
goal_typing_mode in {"c3_only", "c3_plus_purpose"}.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test on typing_mode)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: boolean-match discriminator (owner-selection accuracy), not SNR-shaped
# - baseline_in_band: N/A -- positional baselines are PRE-REGISTERED near-zero BY CONSTRUCTION on
#   the divergent subset (recency, nearest_subject); that IS the gate (see HONEST DISCLOSURE below,
#   reused verbatim from exp_c5_real_coref_endtoend_v1)
# - discriminator survives scale: FULL N (18 explicit_psych + 10 action_implied recency-trap core
#   items), no separate smoke-N; self-test runs seed0 full before dispatch (LOCAL-ONLY, no dispatch)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration below
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check: default_ok_for_this_regime (all thresholds reused verbatim from the already-
#   VET'd exp_c5_real_coref_endtoend_v1 / exp_c5_generative_goal_typing_action_frame_v1 bands)
# - numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in this docstring

PRE-REG (LOCAL-ONLY, in-process foreground; no queue dispatch, no push; task-brief-authored):

  SCOPE: trap_type=="recency" bank only (same scope as exp_c5_real_coref_endtoend_v1 -- the
  recency-vs-event_role coref-mode contrast this bank probes is orthogonal to, but co-resident
  with, the typing-mode contrast here; coref mode is FIXED to "event_role", the production
  default). TWO verb_type subsets: explicit_psych (N=18 core has_distractor + N=9 twins,
  MEASURED@experiments/data/goal_owner_fair_v1.jsonl) and action_implied (N=10 core has_distractor
  + N=5 twins, MEASURED@ same file, grep-counted before authoring).

  ARMS (the ONE variable): goal_typing_mode in {"c3_only", "c3_plus_purpose"}.
    c3_only = type_sentence_events_c3 unmodified (bit-identical import from
      exp_component5_wired_endtoend_v1 -- GOAL fires iff frame_primary_role(subj)==EXPERIENCER).
    c3_plus_purpose = c3_only's events UNIONED with a GOAL event iff the ALREADY-INDUCED
      action_frame_feats/ruleind hypothesis from exp_c5_generative_goal_typing_action_frame_v1
      (imported + invoked bit-identical: action_frame_feats(), induce_hypothesis(),
      hdlab.learner.apply) predicts GOAL and the subject doesn't already have one. Zero new
      feature engineering; the ONLY new code is the union-typer wrapper (~15 lines) and the
      OR-combination call, mirroring make_generative_typer's own wrap-and-union pattern
      (exp_c5_generative_goal_typing_action_frame_v1.py:184-198) but composing with c3-typing
      instead of the module-global-monkeypatch splice (that cell targets a different harness's
      call site; this cell's call site is a direct function import, so the wire is a direct
      OR-call, not a monkeypatch -- same mechanism, different plumbing per each harness's own
      call convention).

  COREF (unchanged, fixed): centrality_mode="event_role" for all arms (production default per
  commit a9e873ab0; this cell does NOT re-sweep recency-vs-event_role -- that contrast is already
  landed in exp_c5_real_coref_endtoend_v1, MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS,
  MEASURED@data/exp_c5_real_coref_endtoend_v1/metrics.json).

  BASELINES (all 4 positional, reused bit-identical, same as exp_c5_real_coref_endtoend_v1):
  recency (the adoption-gate's baseline candidate, 0.0 by construction on the divergent subset),
  first_mention, nearest_subject, majority. GATED baselines (recency, nearest_subject) are the two
  structurally near-zero on the recency-trap bank; first_mention/majority reported but NOT gated
  (bank-structural confound per exp_c5_real_coref_endtoend_v1's own HONEST DISCLOSURE, reused
  verbatim -- unchanged by this cell's typing-mode variable).

  SCRAMBLE control (non-vacuous-scramble pattern, reused bit-identical formula): for the CONTENT
  candidate's role_seq only, relabel the GOAL role's owner entity to the item's foil before
  scoring; corrupted GOAL binding must drop the content score and collapse the divergent-subset
  gain under c3_plus_purpose.

  KNOWN-IN-ADVANCE FINDING (MEASURED@ inline python probe, disclosed BEFORE dispatch, not
  discovered post-hoc): action_frame_feats' CONTROL_VERB_STOP list includes "hope/hopes/hoped"
  (exp_c5_generative_goal_typing_action_frame_v1.py:104-110) -- BY DESIGN, "to VP" after a
  control/desiderative verb is excluded from purpose_to_no_det (treated as that verb's argument-
  complement, assumed already covered by the C3/lexicon path). Direct measurement:
  action_frame_feats("Beth hoped to win a place at the summer fair.") == [] and
  action_frame_feats("Jo hoped to finish planting the garden before noon.") == [] (both, and their
  learner_apply prediction, verified inline before authoring this pre-reg). Since c3_has_desire
  ALSO returns False on "hoped" (the documented OOV gap, exp_component5_wired_endtoend_v1's own
  finding), t03_beth_fair_foil_ruth and t12_jo_garden_foil_ruth are NOT expected to recover under
  c3_plus_purpose: this is a genuine COVERAGE GAP BETWEEN two mechanisms (each individually
  correct by its own design contract), not a bug in either. Pre-registering this HYPOTHESIZED
  outcome explicitly so the run below is a confirmation/refutation, not a surprise reframed after
  the fact. HYPOTHESIZED@this docstring: explicit_psych divergent accuracy under c3_plus_purpose
  stays at 16/18 (unchanged from c3_only), NOT 18/18.

  BANDS (per-subset, small-N formal-HARD_PASS capped to MIDDLE_BAND per this arc's N<30
  convention):
    explicit_psych HARD-PASS -- c3_plus_purpose >= 17/18 (0.9444) on the divergent subset AND
      beats gated positional baselines AND scramble collapses non-vacuously.
    explicit_psych HARD-FAIL -- c3_plus_purpose does not improve over c3_only (i.e. still misses
      t03/t12) OR introduces a false-positive GOAL that breaks scramble collapse.
    explicit_psych MIDDLE_BAND -- anything else (e.g. the pre-registered KNOWN-IN-ADVANCE outcome:
      unchanged 16/18, gated baselines still cleared, scramble still collapses -- a coverage-gap
      finding, not a broken mechanism).
    action_implied HARD-PASS -- c3_plus_purpose beats c3_only AND beats gated positional baselines
      AND scramble collapses non-vacuously AND no explicit_psych regression.
    action_implied HARD-FAIL -- c3_plus_purpose does not improve over c3_only's (expected-zero, C3
      has no lexicon entry for action verbs) baseline, OR scramble does not collapse, OR
      explicit_psych regresses.
    action_implied MIDDLE_BAND -- partial improvement not clearing gated positional baselines, or
      scramble collapse only partial (<50% gain retained is the collapse threshold, matching the
      generative-typing cell's own formula).
  OVERALL verdict = the WORSE of the two per-subset bands (a HARD-FAIL on either subset caps the
  overall verdict at HARD-FAIL; explicit_psych staying MIDDLE_BAND on the pre-registered coverage
  gap does not by itself sink action_implied's independent HARD-PASS potential -- both are
  reported, neither is silently dropped).

  If frame_primary_role/action_frame_feats both fail to detect GOAL on any item (OOV psych verb
  AND non-purpose-infinitival phrasing), that item's row records goal_present_c3=False and
  goal_present_purpose=False and is NOT silently dropped -- it feeds the discriminating count.

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `tools/substrate_query.sh "wire
purpose infinitival generative goal typing into real coref end to end goal owner GOAL detection
event role explicit psych action implied"` returned (cosine>0.30) exp_c5_real_coref_endtoend_v1's
own prior cell entries (this cell's direct predecessor, expected -- extending it, not
rediscovering it) and exp_c5_generative_goal_typing_action_frame_v1's own entries (the detector
being reused, also expected). No prior cell wires the two together -- this is the next buildable
step named in the task brief, not a rediscovery.

GUARDS: glass-box; deterministic given seed; ASCII-only; atomic metrics write; resumable per-unit
(tools/exp_checkpoint.py aka experiments/exp_checkpoint.py); NOT dispatched to any queue
(LOCAL-ONLY, in-process foreground, no push); no modification to hdlab/goal_owner_select.py /
hdlab/event_centrality_coref.py / hdlab/self_improving_loop.py / hdlab/frame_induction.py /
hdlab/situation_reader.py / hdlab/learner/ (production hdlab/ untouched); no modification to
exp_component5_wired_endtoend_v1.py or exp_c5_generative_goal_typing_action_frame_v1.py (both
imported and reused bit-identical, not edited).

Cites: experiments/exp_c5_real_coref_endtoend_v1.py (the end-to-end harness being extended --
mention/target adapter, build_role_seq pattern, run_item/run_seed structure, all reused with
typing_mode as the added dimension); experiments/exp_c5_generative_goal_typing_action_frame_v1.py
(action_frame_feats, induce_hypothesis, the purpose-infinitival detector under wire);
experiments/exp_component5_wired_endtoend_v1.py (type_sentence_events_c3/c3_has_desire, reused
bit-identical); experiments/exp_c5_fair_goal_owner_v1.py (baseline_majority);
experiments/exp_c5_fair_goal_owner_primacy_v1.py (baseline_first_mention, baseline_nearest_subject);
experiments/exp_component5_gold_role_isolated_v1.py (GeneralRecencyEntityResolver);
hdlab/goal_owner_select.py; hdlab/event_centrality_coref.py; hdlab/coref.py;
hdlab/self_improving_loop.py; hdlab/learner/ (ruleind plugin);
notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md (task brief diagnosis).
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

ANCHOR_NAME = "c5_real_coref_endtoend_purpose_infinitival_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_owner_fair_v1.jsonl")

# ---- REUSED BIT-IDENTICAL: real C3 GOAL-typing + R_* role constants + token/sentence helpers ----
from exp_component5_wired_endtoend_v1 import type_sentence_events_c3, c3_has_desire  # noqa: E402
from exp_situation_model_goal_outcome_dimension_v1 import (  # noqa: E402
    R_GOAL, R_UNMET, R_MET, _sentences, _ordered_tokens,
)
# ---- REUSED BIT-IDENTICAL: the purpose-infinitival generative typer under wire ------------------
from exp_c5_generative_goal_typing_action_frame_v1 import (  # noqa: E402
    action_frame_feats, induce_hypothesis,
)
from hdlab.learner import apply as learner_apply  # noqa: E402
# ---- REUSED BIT-IDENTICAL: positional candidate generator + baselines --------------------------
from exp_component5_gold_role_isolated_v1 import GeneralRecencyEntityResolver, DEFAULT_ROSTER  # noqa: E402
from exp_c5_fair_goal_owner_v1 import baseline_majority  # noqa: E402
from exp_c5_fair_goal_owner_primacy_v1 import baseline_first_mention, baseline_nearest_subject  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the promoted C5 integrator + adoption gate --------------------------
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402
# ---- REAL COREF ORGAN (fixed to event_role, production default) + target-builder ---------------
from hdlab.event_centrality_coref import EventCentralityReader  # noqa: E402
from hdlab.coref import build_pronoun_targets  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
TYPING_MODES = ("c3_only", "c3_plus_purpose")
VERB_TYPES = ("explicit_psych", "action_implied")
COREF_MODE_FIXED = "event_role"
GENDER_SCHEME = {"f": "fem", "m": "masc"}


# ============================================================================ bank load
def load_bank(verb_type: str):
    """recency-trap subset (trap_type=='recency' or absent, defaulting per bank convention),
    verb_type in {'explicit_psych', 'action_implied'} only (per SCOPE)."""
    rows = []
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    rows = [r for r in rows
            if r.get("trap_type", "recency") == "recency" and r["verb_type"] == verb_type]
    core = [r for r in rows if r["has_distractor"]]
    twins = [r for r in rows if not r["has_distractor"]]
    return core, twins


# ============================================================================ typing-mode union (NEW)
def type_sentence_events_union(sentence: str, subject, plugin_name, hypothesis):
    """c3_only events UNIONED with a GOAL event iff the purpose-infinitival detector fires and the
    subject doesn't already have a GOAL. Mirrors exp_c5_generative_goal_typing_action_frame_v1's
    own make_generative_typer union-logic (reused pattern, not reused code -- that cell's wire
    point is a module-global monkeypatch for a different harness's call site; this harness calls
    the typer via a direct function import, so the union is a direct OR-call here)."""
    events = type_sentence_events_c3(sentence, subject)
    feats = action_frame_feats(sentence)
    pred = learner_apply(plugin_name, hypothesis, feats, key=None, default_class="NOT_GOAL")
    already_goal = any(r == R_GOAL and e == subject for (e, r) in events)
    if pred == "GOAL" and subject is not None and not already_goal:
        events = list(events) + [(subject, R_GOAL)]
    return events


def typer_for_mode(mode: str, plugin_name, hypothesis):
    if mode == "c3_only":
        return lambda sentence, subject: type_sentence_events_c3(sentence, subject)
    if mode == "c3_plus_purpose":
        return lambda sentence, subject: type_sentence_events_union(
            sentence, subject, plugin_name, hypothesis)
    raise ValueError(f"unknown typing_mode {mode!r}")


# ============================================================================ mention/target adapter (reused bit-identical logic from exp_c5_real_coref_endtoend_v1)
def item_to_mentions(item: dict):
    roster = item["roster"]
    owner, foil = item["owner"], item.get("foil")
    cluster_of = {owner: 0}
    if foil is not None:
        cluster_of[foil] = 1
    sents = _sentences(item["text"])
    mentions = []
    mi = 0
    for si, sent in enumerate(sents):
        toks = _ordered_tokens(sent)
        named = next((t for t in toks if t in roster), None)
        if named is not None:
            g = GENDER_SCHEME[roster[named]]
            mentions.append({"head": named, "cluster": cluster_of[named], "is_pronoun": False,
                              "sent_idx": si, "midx": mi, "gender": g, "number": "singular",
                              "name_gender": g, "sent_role_rank": 0, "is_subject": True,
                              "span_toks": [named]})
            mi += 1
            continue
        pron = next((t for t in toks if t in ("she", "he", "her", "him", "his", "hers")), None)
        if pron is not None:
            g = GENDER_SCHEME[roster[owner]]
            mentions.append({"head": pron, "cluster": cluster_of[owner], "is_pronoun": True,
                              "sent_idx": si, "midx": mi, "gender": g, "number": "singular",
                              "name_gender": None, "sent_role_rank": 0, "is_subject": True,
                              "span_toks": [pron]})
            mi += 1
    return mentions


def resolve_outcome_coref(item: dict):
    """Real coref organ's outcome-pronoun resolution, FIXED to event_role centrality_mode
    (production default). Returns the resolved entity NAME string, or None on abstention."""
    mentions = item_to_mentions(item)
    targets = build_pronoun_targets(mentions)
    if not targets:
        return None
    n_sents = max(m["sent_idx"] for m in mentions) + 1
    scene_ids = [0] * n_sents
    ecr = EventCentralityReader()
    records = ecr.resolve_stream(mentions, targets, scene_ids=scene_ids, topical_mode="rolemass",
                                  query_memory=True, centrality_mode=COREF_MODE_FIXED)
    if not records or records[0]["resolved_head"] is None:
        return None
    return records[0]["resolved_head"]


def resolve_outcome_recency_positional(item: dict):
    """BASELINE candidate for the adoption gate = the recency-to-outcome positional baseline."""
    roster = item["roster"]
    resolver = GeneralRecencyEntityResolver(roster)
    last = None
    for s in _sentences(item["text"]):
        last = resolver.subject_entity(s)
    return last


# ============================================================================ role_seq/cluster_ids builder
def build_role_seq(item: dict, outcome_entity, typer, scramble_goal_to_foil=None):
    sents = _sentences(item["text"])
    owner = item["owner"]
    role_seq, cluster_ids = [], []
    for (entity, role) in typer(sents[0], owner):
        eff = entity
        if scramble_goal_to_foil is not None and role == R_GOAL and entity == owner:
            eff = scramble_goal_to_foil
        role_seq.append(role)
        cluster_ids.append(eff)
    for (entity, role) in typer(sents[-1], outcome_entity):
        role_seq.append(role)
        cluster_ids.append(entity)
    return role_seq, cluster_ids


def _outcome_pos(role_seq):
    positions = [i for i, r in enumerate(role_seq) if r in (R_UNMET, R_MET)]
    return positions[-1] if positions else None


# ============================================================================ per-item eval (one typing mode)
def run_item(item: dict, typing_mode: str, seed: int, plugin_name, hypothesis):
    gold = item["gold_outcome_owner"]
    foil = item.get("foil")
    typer = typer_for_mode(typing_mode, plugin_name, hypothesis)

    baseline_owner = resolve_outcome_recency_positional(item)
    role_seq_b, cluster_ids_b = build_role_seq(item, baseline_owner, typer)
    outcome_pos = _outcome_pos(role_seq_b)

    coref_owner = resolve_outcome_coref(item)
    role_seq_c, cluster_ids_c = build_role_seq(item, coref_owner, typer)
    assert role_seq_b == role_seq_c, (
        f"{item['id']}/{typing_mode}: role attribution must be resolver-independent: "
        f"{role_seq_b} vs {role_seq_c}")

    goal_present = R_GOAL in role_seq_b
    row = dict(id=item["id"], typing_mode=typing_mode, gold=gold, baseline_owner=baseline_owner,
               coref_owner=coref_owner, goal_present=goal_present,
               baseline_matches_gold=(baseline_owner == gold),
               coref_raw_matches_gold=(coref_owner == gold))

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
        role_seq_s, cluster_ids_s = build_role_seq(item, coref_owner, typer,
                                                     scramble_goal_to_foil=foil)
        score_s = directed_goal_outcome_score(role_seq_s, cluster_ids_s, seed, outcome_pos)
        adopt_s = decide_keep_or_revert({"content": score_s - score_b}, ABSTAIN_BAND_DEFAULT)
        scrambled_owner = cluster_ids_s[outcome_pos] if adopt_s == "content" else cluster_ids_b[outcome_pos]
        row.update(scrambled_final_owner=scrambled_owner,
                    scrambled_matches_gold=(scrambled_owner == gold))
    else:
        row.update(scrambled_final_owner=None, scrambled_matches_gold=None)
    return row


# ============================================================================ per-seed unit
def run_seed(seed: int, plugin_name, hypothesis):
    out = {}
    for verb_type in VERB_TYPES:
        core, twins = load_bank(verb_type)
        out[verb_type] = {}
        for mode in TYPING_MODES:
            core_rows = [run_item(it, mode, seed, plugin_name, hypothesis) for it in core]
            twin_rows = [run_item(it, mode, seed, plugin_name, hypothesis) for it in twins]
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
            first_mention=pos_rate(baseline_first_mention),
            nearest_subject=pos_rate(baseline_nearest_subject),
            majority=pos_rate(baseline_majority),
        )
        out[verb_type]["n_divergent"] = len(div_items)
    return dict(seed=seed, per_verb_type=out)


# ============================================================================ arms-must-differ (META_RULE_AF)
def _arms_must_differ(per_seed0):
    digests = {}
    for verb_type in VERB_TYPES:
        for mode in TYPING_MODES:
            core_rows = per_seed0["per_verb_type"][verb_type][mode]["core_rows"]
            blob = json.dumps([(r["id"], r["final_owner"], r["goal_present"]) for r in core_rows],
                               sort_keys=True).encode("utf-8")
            digests[f"{verb_type}/{mode}"] = hashlib.sha256(blob).hexdigest()
    a, b = f"action_implied/c3_only", f"action_implied/c3_plus_purpose"
    differ_action_implied = digests[a] != digests[b]
    return digests, differ_action_implied


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
        n_divergent_ok = all(
            per_seed[s]["per_verb_type"][verb_type]["n_divergent"] == n_divergent for s in seeds)
        modes = {}
        for mode in TYPING_MODES:
            modes[mode] = dict(
                n_core=per_seed[seeds[0]]["per_verb_type"][verb_type][mode]["n_core"],
                n_twin=per_seed[seeds[0]]["per_verb_type"][verb_type][mode]["n_twin"],
                n_divergent=per_seed[seeds[0]]["per_verb_type"][verb_type][mode]["n_divergent"],
                recency_floor_divergent=mean(verb_type, mode, "recency_floor_divergent"),
                system_accuracy_divergent=mean(verb_type, mode, "system_accuracy_divergent"),
                system_scrambled_accuracy_divergent=mean(
                    verb_type, mode, "system_scrambled_accuracy_divergent"),
                twin_control_accuracy=mean(verb_type, mode, "twin_control_accuracy"),
                n_goal_present_core_seed0=per_seed[seeds[0]]["per_verb_type"][verb_type][mode][
                    "n_goal_present_core"],
                miss_ids_seed0=per_seed[seeds[0]]["per_verb_type"][verb_type][mode]["miss_ids"],
            )

        acc_c3_only = modes["c3_only"]["system_accuracy_divergent"]
        acc_c3_plus = modes["c3_plus_purpose"]["system_accuracy_divergent"]
        improves = (acc_c3_plus is not None and acc_c3_only is not None and acc_c3_plus > acc_c3_only)
        no_change = (acc_c3_plus is not None and acc_c3_only is not None and acc_c3_plus == acc_c3_only)

        gated_vals = [pos_base[k] for k in gated_baseline_names if pos_base.get(k) is not None]
        beats_gated_positional = (
            acc_c3_plus is not None and gated_vals and all(acc_c3_plus > v for v in gated_vals))
        all_four_vals = [v for v in pos_base.values() if v is not None]
        beats_all_four_positional = (
            acc_c3_plus is not None and all_four_vals and all(acc_c3_plus > v for v in all_four_vals))

        unscr = modes["c3_plus_purpose"]["system_accuracy_divergent"]
        scr = modes["c3_plus_purpose"]["system_scrambled_accuracy_divergent"]
        floor = modes["c3_plus_purpose"]["recency_floor_divergent"]
        gain_unscr = (unscr - floor) if (unscr is not None and floor is not None) else None
        gain_scr = (scr - floor) if (scr is not None and floor is not None) else None
        if gain_unscr is not None and gain_unscr > 1e-9:
            scramble_collapses = (gain_scr is not None and gain_scr <= 0.5 * gain_unscr + 1e-9)
            scramble_vacuous = False
        else:
            scramble_collapses = (gain_scr is not None and gain_scr <= 1e-9)
            scramble_vacuous = True

        n_div = modes["c3_plus_purpose"]["n_divergent"]
        strict_floor = n_div  # HARD_PASS floor per-subset computed below (verb_type-specific)
        if verb_type == "explicit_psych":
            hard_pass_thresh = 17.0 / 18.0 if n_div == 18 else 0.9444
            if acc_c3_plus is not None and acc_c3_plus >= hard_pass_thresh - 1e-9 \
                    and beats_gated_positional and scramble_collapses and not scramble_vacuous:
                v = "HARD_PASS_RECOVERED_INFINITIVAL_TRAP"
            elif no_change or (acc_c3_plus is not None and acc_c3_only is not None
                                and acc_c3_plus < acc_c3_only) or not scramble_collapses:
                v = "HARD_FAIL_NO_RECOVERY" if no_change else "HARD_FAIL_REGRESSION_OR_SCRAMBLE_LEAK"
                if no_change and scramble_collapses:
                    v = "MIDDLE_BAND_COVERAGE_GAP_UNCHANGED_16_18_PREREGISTERED"
            else:
                v = "MIDDLE_BAND"
        else:  # action_implied
            if improves and beats_gated_positional and scramble_collapses and not scramble_vacuous:
                v = "MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS" if n_div < 30 else "HARD_PASS"
            elif not improves or not scramble_collapses:
                v = "HARD_FAIL_NO_RECOVERY_OR_SCRAMBLE_LEAK"
            else:
                v = "MIDDLE_BAND"

        subset_verdicts[verb_type] = v
        per_vt[verb_type] = dict(
            n_divergent=n_divergent, n_divergent_ok=n_divergent_ok,
            positional_baselines_divergent=pos_base, gated_baseline_names=list(gated_baseline_names),
            modes=modes, improves_over_c3_only=improves, no_change_from_c3_only=no_change,
            beats_gated_positional=beats_gated_positional,
            beats_all_four_positional=beats_all_four_positional,
            scramble_collapses=scramble_collapses, scramble_vacuous=scramble_vacuous,
            verdict=v,
        )

    # OVERALL = worst of the two per-subset bands
    rank = {"HARD_FAIL": 0, "MIDDLE_BAND": 1, "HARD_PASS": 2}

    def rank_of(v):
        if v.startswith("HARD_FAIL"):
            return 0
        if v.startswith("HARD_PASS"):
            return 2
        return 1  # any MIDDLE_BAND flavor incl small-N-capped

    overall_rank = min(rank_of(subset_verdicts[vt]) for vt in VERB_TYPES)
    overall = {0: "HARD_FAIL", 1: "MIDDLE_BAND", 2: "HARD_PASS"}[overall_rank]

    where_breaks = {
        "explicit_psych_c3_plus_purpose_misses": per_vt["explicit_psych"]["modes"]["c3_plus_purpose"][
            "miss_ids_seed0"],
        "action_implied_c3_plus_purpose_misses": per_vt["action_implied"]["modes"]["c3_plus_purpose"][
            "miss_ids_seed0"],
        "action_implied_c3_only_misses": per_vt["action_implied"]["modes"]["c3_only"]["miss_ids_seed0"],
    }

    msg = (
        f"explicit_psych: c3_only={per_vt['explicit_psych']['modes']['c3_only']['system_accuracy_divergent']} "
        f"-> c3_plus_purpose={per_vt['explicit_psych']['modes']['c3_plus_purpose']['system_accuracy_divergent']} "
        f"(N_div={per_vt['explicit_psych']['n_divergent']}, verdict={subset_verdicts['explicit_psych']}, "
        f"misses={where_breaks['explicit_psych_c3_plus_purpose_misses']}). "
        f"action_implied: c3_only={per_vt['action_implied']['modes']['c3_only']['system_accuracy_divergent']} "
        f"-> c3_plus_purpose={per_vt['action_implied']['modes']['c3_plus_purpose']['system_accuracy_divergent']} "
        f"(N_div={per_vt['action_implied']['n_divergent']}, verdict={subset_verdicts['action_implied']}). "
        f"OVERALL={overall} (worse-of-two-subsets rule).")

    return dict(
        verdict=overall, verdict_msg=f"{overall}: {msg}", summary=msg, n_seeds=n,
        subset_verdicts=subset_verdicts, per_verb_type=per_vt, where_breaks=where_breaks,
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
              f"c3_plus={pv['explicit_psych']['c3_plus_purpose']['system_accuracy_divergent']}) "
              f"action_implied(c3_only={pv['action_implied']['c3_only']['system_accuracy_divergent']}, "
              f"c3_plus={pv['action_implied']['c3_plus_purpose']['system_accuracy_divergent']})",
              flush=True)

    raw = load_units(OUTPUT_DIR)
    per_seed = {int(v["seed"]): v for v in raw.values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")

    digests, differ = _arms_must_differ(per_seed[SEEDS[0]])
    if not differ:
        raise AssertionError(f"META_RULE_AF VIOLATION: typing modes bit-identical on action_implied: {digests}")

    agg = aggregate(per_seed)
    agg["arms_differ_verified"] = True
    agg["arms_digests"] = digests
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(seeds=SEEDS, typing_modes=list(TYPING_MODES), verb_types=list(VERB_TYPES),
                         coref_mode_fixed=COREF_MODE_FIXED, abstain_band=ABSTAIN_BAND_DEFAULT,
                         bank_path=BANK_PATH, scope="explicit_psych+action_implied x trap_type=recency",
                         cardinality_ok=(len(per_seed) == EXPECTED_N_SEEDS),
                         induced_plugin=plugin_name)
    agg["hp_scope"] = {
        "explicit_psych/c3_plus_purpose": ["beats_gated_positional", "scramble_collapses",
                                            "hard_pass_thresh_17_of_18"],
        "action_implied/c3_plus_purpose": ["improves_over_c3_only", "beats_gated_positional",
                                            "scramble_collapses"],
        "c3_only": ["reported_only_not_hard_pass_gated"],
    }
    agg["final_metrics_atomicity"] = "tmp_replace"
    agg["crlb_n/a"] = "boolean-match discriminator (owner-selection accuracy), not an SNR/argmax-noise regime"
    agg["prereg"] = "inline (docstring, per LOCAL-ONLY task brief; no separate preregs/ file)"
    agg["cites"] = [
        "experiments/exp_c5_real_coref_endtoend_v1.py (harness under extension)",
        "experiments/exp_c5_generative_goal_typing_action_frame_v1.py (purpose-infinitival detector, reused)",
        "experiments/exp_component5_wired_endtoend_v1.py (type_sentence_events_c3/c3_has_desire, reused)",
        "experiments/exp_c5_fair_goal_owner_v1.py (baseline_majority)",
        "experiments/exp_c5_fair_goal_owner_primacy_v1.py (baseline_first_mention/nearest_subject)",
        "experiments/exp_component5_gold_role_isolated_v1.py (GeneralRecencyEntityResolver)",
        "hdlab/goal_owner_select.py (directed_goal_outcome_score, promoted 2026-08-05)",
        "hdlab/event_centrality_coref.py (EventCentralityReader, fixed event_role mode)",
        "hdlab/coref.py (build_pronoun_targets)",
        "hdlab/self_improving_loop.py (decide_keep_or_revert, promoted 2026-08-02)",
        "hdlab/learner/ (ruleind plugin, config-only MDL registry)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    ep_core, ep_twins = load_bank("explicit_psych")
    ai_core, ai_twins = load_bank("action_implied")
    assert len(ep_core) >= 15, f"expected N>=15 explicit_psych core, got {len(ep_core)}"
    assert len(ai_core) >= 8, f"expected N>=8 action_implied core, got {len(ai_core)}"
    print(f"[bank] explicit_psych: {len(ep_core)} core + {len(ep_twins)} twin; "
          f"action_implied: {len(ai_core)} core + {len(ai_twins)} twin", flush=True)

    plugin_name, chosen, _ = induce_hypothesis()
    assert chosen is not None, "MDL induction returned KEEP_EPISODIC"
    hypothesis = chosen.hypothesis
    print(f"[SELFTEST 1/9] induced hypothesis plugin={plugin_name} n_rules="
          f"{chosen.metrics.get('n_rules')}", flush=True)

    # (2) PRE-REGISTERED KNOWN-IN-ADVANCE finding: purpose feature does NOT fire on "hoped to VP"
    # (CONTROL_VERB_STOP excludes desiderative-governing verbs by design).
    it_beth = next(it for it in ep_core if it["id"] == "t03_beth_fair_foil_ruth")
    it_jo = next(it for it in ep_core if it["id"] == "t12_jo_garden_foil_ruth")
    s0_beth = _sentences(it_beth["text"])[0]
    s0_jo = _sentences(it_jo["text"])[0]
    assert action_frame_feats(s0_beth) == [], (
        f"expected purpose feature NOT to fire on control-verb-governed infinitival: {s0_beth!r}")
    assert action_frame_feats(s0_jo) == [], (
        f"expected purpose feature NOT to fire on control-verb-governed infinitival: {s0_jo!r}")
    assert not c3_has_desire(s0_beth) and not c3_has_desire(s0_jo), (
        "expected the documented C3 OOV gap on 'hoped' to still hold")
    print("[SELFTEST 2/9] pre-registered coverage-gap finding confirmed: neither c3_has_desire nor "
          "action_frame_feats fires on 'hoped to VP' (t03/t12 not expected to recover)", flush=True)

    # (3) purpose feature DOES fire on a genuine action_implied S1 (held-out verb, no control-verb).
    it19 = next(it for it in ai_core if it["id"] == "t19_ruth_well_foil_amy")
    s0_19 = _sentences(it19["text"])[0]
    assert "purpose_to_no_det" in action_frame_feats(s0_19), (
        f"expected purpose feature to fire on action_implied S1: {s0_19!r}")
    print(f"[SELFTEST 3/9] purpose_to_no_det fires on action_implied item {it19['id']!r} S1", flush=True)

    # (4) c3_only misses GOAL entirely on action_implied S1 (no lexicon/frame entry for action verbs).
    row_c3only = run_item(it19, "c3_only", seed=0, plugin_name=plugin_name, hypothesis=hypothesis)
    assert row_c3only["goal_present"] is False, (
        f"expected c3_only to miss GOAL on action_implied item: {row_c3only}")
    print(f"[SELFTEST 4/9] c3_only misses GOAL on {it19['id']!r} (goal_present=False)", flush=True)

    # (5) c3_plus_purpose DOES detect GOAL on the same item (ARMS-MUST-DIFFER at item level).
    row_c3plus = run_item(it19, "c3_plus_purpose", seed=0, plugin_name=plugin_name, hypothesis=hypothesis)
    assert row_c3plus["goal_present"] is True, (
        f"expected c3_plus_purpose to detect GOAL via purpose-infinitival: {row_c3plus}")
    print(f"[SELFTEST 5/9] c3_plus_purpose detects GOAL on {it19['id']!r} via purpose-infinitival "
          f"(goal_present=True)", flush=True)

    # (6) end-to-end: c3_plus_purpose's adoption should trust the correct coref pick on this trap.
    assert row_c3plus["matches_gold"] is True, f"c3_plus_purpose end-to-end must match gold: {row_c3plus}"
    print(f"[SELFTEST 6/9] c3_plus_purpose end-to-end adopts correct owner on {it19['id']!r}", flush=True)

    # (7) scramble collapses this item's win.
    assert row_c3plus["scrambled_matches_gold"] is False, (
        f"role-scramble must collapse the win: {row_c3plus}")
    print("[SELFTEST 7/9] role-scramble collapses the c3_plus_purpose win", flush=True)

    # (8) ARMS-MUST-DIFFER at aggregate level for action_implied.
    res = run_seed(0, plugin_name, hypothesis)
    digests, differ = _arms_must_differ(res)
    assert differ, f"META_RULE_AF: typing modes bit-identical on action_implied: {digests}"
    print(f"[SELFTEST 8/9] typing modes diverge on action_implied full item set", flush=True)

    # (9) cardinality + positional-baseline sanity for both subsets.
    for vt in VERB_TYPES:
        pb = res["per_verb_type"][vt]["positional_baselines_divergent"]
        assert pb["recency"] == 0.0, f"{vt}: recency positional baseline must be 0.0: {pb}"
        n_div = res["per_verb_type"][vt]["n_divergent"]
        assert n_div >= 8, f"{vt}: too few divergent items for a powered test: {n_div}"
    print(f"[SELFTEST 9/9] both subsets: recency baseline=0.0, N_divergent adequate", flush=True)

    from hdlab.goal_owner_select import self_test as organ_self_test
    from hdlab.event_centrality_coref import _run_all_selftests as coref_self_test
    organ_res = organ_self_test()
    coref_res = coref_self_test()
    return {
        "induced_plugin": plugin_name, "beth_hoped_feats": action_frame_feats(s0_beth),
        "action_implied_item19_c3only": row_c3only, "action_implied_item19_c3plus": row_c3plus,
        "seed0_positional_baselines": {vt: res["per_verb_type"][vt]["positional_baselines_divergent"]
                                        for vt in VERB_TYPES},
        "promoted_organ_self_test": organ_res, "coref_organ_self_test": coref_res,
    }


def _run_no_regression_checks() -> dict:
    """Confirms no touched-module regression: reruns the reused cells' own self-tests (both
    untouched by this cell)."""
    out = {}
    try:
        from exp_component5_wired_endtoend_v1 import self_test as wired_self_test
        wr = wired_self_test()
        out["wired_endtoend_selftest"] = {"passed": True, "keys": list(wr.keys())}
    except Exception as e:  # noqa: BLE001
        out["wired_endtoend_selftest"] = {"passed": False, "error": f"{type(e).__name__}: {e}"}
    try:
        from exp_c5_generative_goal_typing_action_frame_v1 import self_test as gen_self_test
        gr = gen_self_test()
        out["generative_typing_selftest"] = {"passed": bool(gr)}
    except Exception as e:  # noqa: BLE001
        out["generative_typing_selftest"] = {"passed": False, "error": f"{type(e).__name__}: {e}"}
    try:
        from hdlab.event_centrality_coref import _run_all_selftests as coref_self_test
        cr = coref_self_test()
        out["coref_organ_selftest"] = {"passed": True, "keys": list(cr.keys())}
    except Exception as e:  # noqa: BLE001
        out["coref_organ_selftest"] = {"passed": False, "error": f"{type(e).__name__}: {e}"}
    out["all_passed"] = all(v.get("passed") for v in out.values() if isinstance(v, dict))
    return out


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--no-regression", action="store_true")
    args = ap.parse_args()
    if args.no_regression:
        res = _run_no_regression_checks()
        print(json.dumps(res, indent=2))
        raise SystemExit(0 if res["all_passed"] else 1)
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
