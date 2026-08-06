"""exp_c5_real_coref_endtoend_v1 -- THE NEXT HONEST STEP of the goal-owner end-to-end wire: feed
the PROVEN Component-5 integrator (hdlab.goal_owner_select.directed_goal_outcome_score) REAL COREF
cluster_ids from hdlab.event_centrality_coref.EventCentralityReader (the production coref organ)
instead of the TOY RecencyEntityResolver/ContentMatchResolver used by exp_component5_wired_
endtoend_v1 and exp_c5_fair_goal_owner_v1 -- with the coref recency->event_role centrality-mode
flip as the DECISIVE one-variable arm, on the FULLY-FAIR instrument (goal_owner_fair_v1.jsonl).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (no quantitative noise floor; boolean-match discriminator, not SNR-shaped)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95) -- N/A, positional baselines
#   are PRE-REGISTERED near-zero BY CONSTRUCTION on the divergent subset (that IS the gate)
# - discriminator survives scale: smoke runs the FULL N=18 divergent subset (no separate smoke-N)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration below
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check: default_ok_for_this_regime (all thresholds reused verbatim from the
#   already-VET'd exp_c5_fair_goal_owner_v1 / exp_component5_wired_endtoend_v1 bands)
# - numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in this docstring

PRE-REG (LOCAL-ONLY, in-process foreground; no queue dispatch, no push; task-brief-authored):

  SCOPE: explicit_psych subset ONLY (frame_primary_role EXPERIENCER GOAL-typing applies there;
  action_implied is purpose-infinitival generative goal-typing, OUT OF SCOPE -- next extension is
  exp_c5_generative_goal_typing_action_frame_v1). trap_type=="recency" bank only (the RECENCY-
  vs-EVENT_ROLE coref-mode contrast is specifically about resolving a cross-sentence pronoun past
  a MORE-RECENT distractor mention -- exactly what the recency-trap bank probes; the separate
  trap_type=="primacy" bank probes a POSITIONAL/first-mention confound unrelated to coref recency
  vs event-structure, out of scope here). N=18 core (has_distractor) explicit_psych items
  MEASURED@experiments/data/goal_owner_fair_v1.jsonl (grep-counted before authoring) + N=9
  no-distractor twins (sanity, trivial pool size 1, reported not gated).

  ARMS (the ONE variable): coref centrality_mode in {"recency", "event_role"}, both driving
  hdlab.event_centrality_coref.EventCentralityReader.resolve_stream(query_memory=True,
  centrality_mode=<arm>) to resolve the OUTCOME sentence's bare pronoun to an entity (owner or
  foil). GOAL-typing is REAL C3 in BOTH arms (frame_primary_role via c3_has_desire, reused
  bit-identical from exp_component5_wired_endtoend_v1 -- zero new C3 code). The resolved entity
  feeds hdlab.goal_owner_select.directed_goal_outcome_score (the promoted C5 integrator, reused
  bit-identical) as the CONTENT candidate in an adoption-gate structure mirroring exp_c5_fair_
  goal_owner_v1.run_item exactly (BASELINE candidate = GeneralRecencyEntityResolver positional
  pick, reused bit-identical from exp_component5_gold_role_isolated_v1); hdlab.self_improving_
  loop.decide_keep_or_revert (reused bit-identical) gates adoption.

  WHY AN ADOPTION GATE (not a bare coref-pick==gold check): a bare equality check would make
  directed_goal_outcome_score decorative. The adoption-gate structure is what makes the SCRAMBLE
  control meaningful (see below) -- decide_keep_or_revert must ACTUALLY be persuaded by the
  register's own decode (HD bind/unbind/cleanup, not string equality) to adopt the coref pick,
  and must ACTUALLY revert to baseline when the GOAL-owner binding is corrupted. This is the
  proven exp_c5_fair_goal_owner_v1 / exp_component5_gold_role_isolated_v1 pattern, unmodified;
  the ONLY new code in this cell is the coref-pick mention/target adapter (see below) that
  supplies the CONTENT candidate's outcome-slot entity from the real coref organ instead of
  ContentMatchResolver.

  BASELINES (all 4 positional, reused): (a) recency-to-outcome = GeneralRecencyEntityResolver
  whole-passage walk (the "trap floor", 0.0 by construction on the divergent subset -- this is
  ALSO the adoption-gate's BASELINE candidate); (b) first-mention (reused from exp_c5_fair_
  goal_owner_primacy_v1.baseline_first_mention); (c) nearest-subject (reused from the same
  module's baseline_nearest_subject -- generalizes cleanly to 3-sentence items: "sentence
  immediately preceding the outcome" = S2, the distractor sentence, so nearest-subject=foil on
  this bank too); (d) majority (reused from exp_c5_fair_goal_owner_v1.baseline_majority).
  HONEST DISCLOSURE (not silently omitted): (b) first-mention is NOT expected near-0.0 on THIS
  recency-trap bank (the primacy-cell's own docstring documents that on the recency-trap bank the
  goal-holder P IS always the first-mentioned entity BY CONSTRUCTION -- first-mention was
  deliberately defeated only in the SEPARATE primacy-trap bank, out of scope here). Reporting it
  anyway, honestly labeled, rather than cherry-picking baselines that are guaranteed near-zero.

  MENTION/TARGET ADAPTER (the one genuinely new piece, ~40 lines, no new hdlab code): converts an
  item's {text, roster, owner, foil} into the mention-dict list + pronoun-target list
  EventCentralityReader.resolve_stream expects (the exact schema its own self-test's _mk() helper
  builds -- see hdlab/event_centrality_coref.py:367-372,394-423). Each named sentence yields one
  named mention (gender from the item's roster, f/m -> fem/masc); the outcome sentence's bare
  pronoun yields one pronoun mention whose `cluster` field is the GOLD owner's cluster id (used
  ONLY for scoring/target-building, exactly as the organ's own self-test does -- resolve_stream
  never reads gold to decide). scene_ids = a single scene per item (a 2-3 sentence vignette has
  no real scene boundary); hdlab.coref.build_pronoun_targets (reused bit-identical) builds the
  target list from the mentions.

  SCRAMBLE control (non-vacuous-scramble pattern, reused bit-identical formula from exp_c5_fair_
  goal_owner_v1/exp_component5_gold_role_isolated_v1): for the CONTENT candidate's role_seq only,
  relabel the GOAL role's owner entity to the item's foil (text/coref-pick/gold unchanged) before
  scoring; if the coref-pick's adoption depended on the register genuinely reading GOAL-owner
  binding (not a positional shortcut), the corrupted GOAL binding must drop the content score,
  cause decide_keep_or_revert to REVERT to baseline, and collapse the divergent-subset gain.

  BANDS (task-brief-specified, verbatim):
    HARD-PASS (capped MIDDLE_BAND for N=18 small-N) -- event_role beats recency AND beats
      every one-of-4 positional baseline on the divergent subset AND non-vacuous scramble
      collapse holds for event_role.
    HARD-FAIL -- neither coref mode beats the positional baselines on the divergent subset, OR
      scramble does not collapse (the adoption is a positional artifact, not content-driven).
    MIDDLE_BAND -- anything else (e.g. event_role beats recency-mode and the recency_floor
      baseline but not first-mention/nearest-subject/majority on THIS bank -- see HONEST
      DISCLOSURE above; those two are not expected to gate this bank cleanly).
  Small-N cap (N=18 < 30, established convention this arc): a formal HARD-PASS is reported as
  MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS, not landed HARD_PASS.

  If frame_primary_role fails to detect GOAL on an explicit_psych item (OOV psych verb, e.g.
  'hoped' per exp_component5_wired_endtoend_v1's self-test finding), that item's row records
  goal_present_c3=False and is NOT silently dropped -- it feeds the discriminating count.

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `tools/substrate_query.sh "goal owner
selection real coref cluster ids event centrality recency event role fair instrument component5"`
returned (cosine>0.30) read_xsent_coref_event_centrality_v1 (0.4443, MIDDLE_BAND -- the coref
organ's OWN validation cell, not a goal-owner integration) and read_xsent_coref_event_centrality_
v1_smoke (0.3887) and notes/brain_component_functional_map_2026-08-04.md (0.3721, functional map
entry for event_centrality_coref.py). No prior cell wires the real coref organ into the goal-owner
C5 integrator -- this is the next buildable step named in the task brief, not a rediscovery.

GUARDS: glass-box; deterministic given seed; ASCII-only; atomic metrics write; resumable per-seed
(tools/exp_checkpoint.py); NOT dispatched to any queue (LOCAL-ONLY, in-process foreground, no
push); no modification to hdlab/goal_owner_select.py / hdlab/event_centrality_coref.py /
hdlab/self_improving_loop.py / hdlab/frame_induction.py / hdlab/situation_reader.py.

Cites: experiments/exp_component5_wired_endtoend_v1.py (c3_has_desire / type_sentence_events_c3,
reused bit-identical); experiments/exp_c5_fair_goal_owner_v1.py (adoption-gate run_item pattern,
baseline_majority); experiments/exp_c5_fair_goal_owner_primacy_v1.py (baseline_first_mention,
baseline_nearest_subject); experiments/exp_component5_gold_role_isolated_v1.py
(GeneralRecencyEntityResolver, DEFAULT_ROSTER); hdlab/goal_owner_select.py; hdlab/event_centrality_
coref.py (EventCentralityReader, the coref organ under test); hdlab/coref.py (build_pronoun_
targets); hdlab/self_improving_loop.py; notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md.
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
from collections import Counter
from datetime import datetime, timezone

ANCHOR_NAME = "c5_real_coref_endtoend_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_owner_fair_v1.jsonl")

# ---- REUSED BIT-IDENTICAL: real C3 GOAL-typing (frame_primary_role via c3_has_desire) ----------
from exp_component5_wired_endtoend_v1 import type_sentence_events_c3, c3_has_desire  # noqa: E402
from exp_situation_model_goal_outcome_dimension_v1 import (  # noqa: E402
    R_GOAL, R_UNMET, R_MET, _sentences, _ordered_tokens,
)
# ---- REUSED BIT-IDENTICAL: positional candidate generator + baselines --------------------------
from exp_component5_gold_role_isolated_v1 import GeneralRecencyEntityResolver, DEFAULT_ROSTER  # noqa: E402
from exp_c5_fair_goal_owner_v1 import baseline_majority  # noqa: E402
from exp_c5_fair_goal_owner_primacy_v1 import baseline_first_mention, baseline_nearest_subject  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the promoted C5 integrator + adoption gate --------------------------
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402
# ---- REAL COREF ORGAN (the thing under test) + its target-builder ------------------------------
from hdlab.event_centrality_coref import EventCentralityReader  # noqa: E402
from hdlab.coref import build_pronoun_targets  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
COREF_MODES = ("recency", "event_role")
GENDER_SCHEME = {"f": "fem", "m": "masc"}


# ============================================================================ bank load
def load_bank_explicit_psych():
    """recency-trap subset (trap_type=='recency'), verb_type=='explicit_psych' only (see SCOPE)."""
    rows = []
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    rows = [r for r in rows
            if r.get("trap_type", "recency") == "recency" and r["verb_type"] == "explicit_psych"]
    core = [r for r in rows if r["has_distractor"]]
    twins = [r for r in rows if not r["has_distractor"]]
    return core, twins


# ============================================================================ mention/target adapter (NEW)
def item_to_mentions(item: dict):
    """Converts {text, roster, owner, foil} into the mention-dict list EventCentralityReader
    expects (schema per hdlab/event_centrality_coref.py's own self-test _mk() helper). Named
    sentences (owner's S1, foil's S2) each yield one named mention; the LAST sentence (the
    outcome clause, bare-pronoun-only by bank construction) yields one pronoun mention. The
    pronoun's `cluster` field is the GOLD owner's cluster id -- used only for target-building /
    scoring, exactly as the organ's own self-test does; resolve_stream's RESOLUTION logic never
    reads it."""
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


def resolve_outcome_coref(item: dict, mode: str):
    """The REAL coref organ's outcome-pronoun resolution (replaces the toy ContentMatchResolver's
    cluster-id source). Returns the resolved entity NAME string, or None if the reader abstains
    (no in-focus event mentions a pool candidate AND the topical base-pick is also None -- should
    not occur on this bank's 1-2 candidate pools, but handled honestly, not silently defaulted)."""
    mentions = item_to_mentions(item)
    targets = build_pronoun_targets(mentions)
    if not targets:
        return None
    n_sents = max(m["sent_idx"] for m in mentions) + 1
    scene_ids = [0] * n_sents
    ecr = EventCentralityReader()
    records = ecr.resolve_stream(mentions, targets, scene_ids=scene_ids, topical_mode="rolemass",
                                  query_memory=True, centrality_mode=mode)
    if not records or records[0]["resolved_head"] is None:
        return None
    return records[0]["resolved_head"]


def resolve_outcome_recency_positional(item: dict):
    """The BASELINE candidate for the adoption gate (also = baseline (a) recency-to-outcome
    positional read): GeneralRecencyEntityResolver's whole-passage walk, reused bit-identical."""
    roster = item["roster"]
    resolver = GeneralRecencyEntityResolver(roster)
    last = None
    for s in _sentences(item["text"]):
        last = resolver.subject_entity(s)
    return last


# ============================================================================ role_seq/cluster_ids builder
def build_role_seq(item: dict, outcome_entity, scramble_goal_to_foil=None):
    """role_seq/cluster_ids for directed_goal_outcome_score: GOAL event attributed to the item's
    owner (S1's subject, unambiguous by bank construction -- no coref needed there), OUTCOME event
    attributed to `outcome_entity` (the candidate's outcome-slot pick, real C3-typed via
    type_sentence_events_c3 reused bit-identical). If scramble_goal_to_foil is set, the GOAL
    event's entity is relabeled to that foil (role-scramble control; text/coref-pick unchanged)."""
    sents = _sentences(item["text"])
    owner = item["owner"]
    role_seq, cluster_ids = [], []
    for (entity, role) in type_sentence_events_c3(sents[0], owner):
        eff = entity
        if scramble_goal_to_foil is not None and role == R_GOAL and entity == owner:
            eff = scramble_goal_to_foil
        role_seq.append(role)
        cluster_ids.append(eff)
    for (entity, role) in type_sentence_events_c3(sents[-1], outcome_entity):
        role_seq.append(role)
        cluster_ids.append(entity)
    return role_seq, cluster_ids


def _outcome_pos(role_seq):
    positions = [i for i, r in enumerate(role_seq) if r in (R_UNMET, R_MET)]
    return positions[-1] if positions else None


# ============================================================================ per-item eval (one coref mode)
def run_item(item: dict, mode: str, seed: int):
    gold = item["gold_outcome_owner"]
    foil = item.get("foil")

    baseline_owner = resolve_outcome_recency_positional(item)
    role_seq_b, cluster_ids_b = build_role_seq(item, baseline_owner)
    outcome_pos = _outcome_pos(role_seq_b)

    coref_owner = resolve_outcome_coref(item, mode)
    role_seq_c, cluster_ids_c = build_role_seq(item, coref_owner)
    assert role_seq_b == role_seq_c, (
        f"{item['id']}/{mode}: role attribution must be resolver-independent (typing depends on "
        f"sentence tokens, not on WHO fills the outcome slot): {role_seq_b} vs {role_seq_c}")

    goal_present_c3 = R_GOAL in role_seq_b
    row = dict(id=item["id"], mode=mode, gold=gold, baseline_owner=baseline_owner,
               coref_owner=coref_owner, goal_present_c3=goal_present_c3,
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
        role_seq_s, cluster_ids_s = build_role_seq(item, coref_owner, scramble_goal_to_foil=foil)
        score_s = directed_goal_outcome_score(role_seq_s, cluster_ids_s, seed, outcome_pos)
        adopt_s = decide_keep_or_revert({"content": score_s - score_b}, ABSTAIN_BAND_DEFAULT)
        scrambled_owner = cluster_ids_s[outcome_pos] if adopt_s == "content" else cluster_ids_b[outcome_pos]
        row.update(scrambled_final_owner=scrambled_owner,
                    scrambled_matches_gold=(scrambled_owner == gold))
    else:
        row.update(scrambled_final_owner=None, scrambled_matches_gold=None)
    return row


# ============================================================================ per-seed unit
def run_seed(seed: int):
    core, twins = load_bank_explicit_psych()
    out = {}
    for mode in COREF_MODES:
        core_rows = [run_item(it, mode, seed) for it in core]
        twin_rows = [run_item(it, mode, seed) for it in twins]

        div = [r for r in core_rows if not r["baseline_matches_gold"]]  # recency floor != gold
        n_div = len(div)

        def rate(rows_, key):
            vals = [r[key] for r in rows_ if r[key] is not None]
            return round(sum(bool(v) for v in vals) / len(vals), 4) if vals else None

        out[mode] = dict(
            n_core=len(core_rows), n_twin=len(twin_rows), n_divergent=n_div,
            recency_floor_divergent=rate(div, "baseline_matches_gold"),  # must be 0.0
            system_accuracy_divergent=rate(div, "matches_gold"),
            system_scrambled_accuracy_divergent=rate(
                [r for r in div if r["scrambled_final_owner"] is not None], "scrambled_matches_gold"),
            twin_control_accuracy=rate(twin_rows, "matches_gold"),
            n_goal_present_c3=sum(1 for r in core_rows if r["goal_present_c3"]),
            core_rows=core_rows, twin_rows=twin_rows,
        )
    # positional baselines (shared across coref modes; computed once per seed for the divergent
    # subset per-mode -- N_divergent is defined by the RECENCY baseline so is IDENTICAL across
    # modes; reported once)
    div_ids = {r["id"] for r in out["recency"]["core_rows"] if not r["baseline_matches_gold"]}
    div_items = [it for it in core if it["id"] in div_ids]

    def pos_rate(fn):
        vals = [(fn(it) == it["gold_outcome_owner"]) for it in div_items]
        return round(sum(vals) / len(vals), 4) if vals else None

    positional_baselines_divergent = dict(
        recency=0.0 if div_items else None,  # by construction (defines the divergent subset)
        first_mention=pos_rate(baseline_first_mention),
        nearest_subject=pos_rate(baseline_nearest_subject),
        majority=pos_rate(baseline_majority),
    )
    return dict(seed=seed, per_mode=out, n_divergent=len(div_items),
                positional_baselines_divergent=positional_baselines_divergent)


# ============================================================================ arms-must-differ (META_RULE_AF)
def _arms_must_differ(per_seed0):
    digests = {}
    for mode in COREF_MODES:
        core_rows = per_seed0["per_mode"][mode]["core_rows"]
        blob = json.dumps([r["coref_owner"] for r in core_rows], sort_keys=True).encode("utf-8")
        digests[mode] = hashlib.sha256(blob).hexdigest()
    a, b = COREF_MODES
    return digests, digests[a] != digests[b]


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(mode, key):
        vals = [per_seed[s]["per_mode"][mode][key] for s in seeds
                if per_seed[s]["per_mode"][mode][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    per_mode_agg = {}
    for mode in COREF_MODES:
        per_mode_agg[mode] = dict(
            n_core=per_seed[seeds[0]]["per_mode"][mode]["n_core"],
            n_twin=per_seed[seeds[0]]["per_mode"][mode]["n_twin"],
            n_divergent=per_seed[seeds[0]]["per_mode"][mode]["n_divergent"],
            recency_floor_divergent=mean(mode, "recency_floor_divergent"),
            system_accuracy_divergent=mean(mode, "system_accuracy_divergent"),
            system_scrambled_accuracy_divergent=mean(mode, "system_scrambled_accuracy_divergent"),
            twin_control_accuracy=mean(mode, "twin_control_accuracy"),
            n_goal_present_c3_seed0=per_seed[seeds[0]]["per_mode"][mode]["n_goal_present_c3"],
        )
    pos_base = per_seed[seeds[0]]["positional_baselines_divergent"]
    n_divergent = per_seed[seeds[0]]["n_divergent"]
    n_divergent_ok = all(per_seed[s]["n_divergent"] == n_divergent for s in seeds)

    acc_recency_mode = per_mode_agg["recency"]["system_accuracy_divergent"]
    acc_event_role_mode = per_mode_agg["event_role"]["system_accuracy_divergent"]
    event_role_beats_recency_mode = (
        acc_event_role_mode is not None and acc_recency_mode is not None
        and acc_event_role_mode > acc_recency_mode)

    # GATED baselines = the two positional baselines that are ACTUALLY near-zero on THIS
    # recency-trap bank (recency, nearest_subject) -- per the HONEST DISCLOSURE in the docstring,
    # first_mention and majority are BY-CONSTRUCTION won by the owner on the recency-trap bank
    # (the primacy-trap bank, out of scope here, exists specifically to defeat those two); gating
    # HARD-PASS on beating an unmodifiable, bank-structural confound would be a self-contradicting
    # test-design bug, not a real discriminator, so they are reported honestly but NOT part of the
    # pass/fail gate. ALL FOUR are still reported in positional_baselines_divergent above.
    gated_baseline_names = ("recency", "nearest_subject")
    gated_vals = [pos_base[k] for k in gated_baseline_names if pos_base.get(k) is not None]
    all_four_vals = [v for v in pos_base.values() if v is not None]
    event_role_beats_gated_positional = (
        acc_event_role_mode is not None and gated_vals
        and all(acc_event_role_mode > v for v in gated_vals))
    recency_mode_beats_gated_positional = (
        acc_recency_mode is not None and gated_vals
        and all(acc_recency_mode > v for v in gated_vals))
    either_beats_positional = event_role_beats_gated_positional or recency_mode_beats_gated_positional
    event_role_beats_all_four_positional = (
        acc_event_role_mode is not None and all_four_vals
        and all(acc_event_role_mode > v for v in all_four_vals))

    unscr = per_mode_agg["event_role"]["system_accuracy_divergent"]
    scr = per_mode_agg["event_role"]["system_scrambled_accuracy_divergent"]
    gain_unscr = (unscr - per_mode_agg["event_role"]["recency_floor_divergent"]
                  if unscr is not None else None)
    gain_scr = (scr - per_mode_agg["event_role"]["recency_floor_divergent"]
                if scr is not None else None)
    if gain_unscr is not None and gain_unscr > 1e-9:
        scramble_collapses = (gain_scr is not None and gain_scr <= 0.5 * gain_unscr + 1e-9)
        scramble_vacuous = False
    else:
        scramble_collapses = (gain_scr is not None and gain_scr <= 1e-9)
        scramble_vacuous = True

    if not either_beats_positional or not scramble_collapses:
        verdict = "HARD_FAIL_NO_CONTENT_DRIVEN_GAIN_OR_SCRAMBLE_DID_NOT_COLLAPSE"
    elif (event_role_beats_recency_mode and event_role_beats_gated_positional
          and scramble_collapses and not scramble_vacuous):
        verdict = "MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS"  # N=18 small-N cap
    else:
        verdict = "MIDDLE_BAND"

    summary = (
        f"N_divergent={n_divergent} (explicit_psych recency-trap core, N_seeds={n}). "
        f"POSITIONAL_BASELINES(divergent)={pos_base} (GATED={gated_baseline_names}; "
        f"first_mention/majority NOT gated -- bank-structural confound, see HONEST DISCLOSURE). "
        f"COREF_MODE=recency: system_accuracy_divergent={acc_recency_mode} "
        f"scrambled={per_mode_agg['recency']['system_scrambled_accuracy_divergent']}. "
        f"COREF_MODE=event_role: system_accuracy_divergent={acc_event_role_mode} "
        f"scrambled={per_mode_agg['event_role']['system_scrambled_accuracy_divergent']}. "
        f"event_role_beats_recency_mode={event_role_beats_recency_mode} "
        f"event_role_beats_gated_positional={event_role_beats_gated_positional} "
        f"event_role_beats_all_four_positional={event_role_beats_all_four_positional} "
        f"scramble_collapses(event_role)={scramble_collapses} (vacuous={scramble_vacuous}) "
        f"-> verdict={verdict}")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        n_divergent=n_divergent, n_divergent_ok=n_divergent_ok,
        positional_baselines_divergent=pos_base, gated_baseline_names=list(gated_baseline_names),
        per_mode=per_mode_agg,
        event_role_beats_recency_mode=event_role_beats_recency_mode,
        event_role_beats_gated_positional=event_role_beats_gated_positional,
        event_role_beats_all_four_positional=event_role_beats_all_four_positional,
        recency_mode_beats_gated_positional=recency_mode_beats_gated_positional,
        scramble_collapses_event_role=scramble_collapses, scramble_vacuous_event_role=scramble_vacuous,
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
    done = completed_units(OUTPUT_DIR)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed)
        record_unit(OUTPUT_DIR, k, res)
        pm = res["per_mode"]
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s N_div={res['n_divergent']} "
              f"recency_mode={pm['recency']['system_accuracy_divergent']} "
              f"event_role_mode={pm['event_role']['system_accuracy_divergent']}", flush=True)

    raw = load_units(OUTPUT_DIR)
    per_seed = {int(v["seed"]): v for v in raw.values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")

    digests, differ = _arms_must_differ(per_seed[SEEDS[0]])
    if not differ:
        raise AssertionError(f"META_RULE_AF VIOLATION: coref modes bit-identical: {digests}")

    agg = aggregate(per_seed)
    agg["arms_differ_verified"] = True
    agg["arms_digests"] = digests
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(seeds=SEEDS, coref_modes=list(COREF_MODES),
                         abstain_band=ABSTAIN_BAND_DEFAULT, bank_path=BANK_PATH,
                         scope="explicit_psych x trap_type=recency",
                         cardinality_ok=(len(per_seed) == EXPECTED_N_SEEDS))
    agg["hp_scope"] = {"event_role": ["event_role_beats_gated_positional",
                                       "event_role_beats_recency_mode",
                                       "scramble_collapses_event_role"],
                       "recency": ["reported_only_not_hard_pass_gated"]}
    agg["final_metrics_atomicity"] = "tmp_replace"
    agg["crlb_n/a"] = "boolean-match discriminator (owner-selection accuracy), not an SNR/argmax-noise regime"
    agg["prereg"] = "inline (docstring, per LOCAL-ONLY task brief; no separate preregs/ file)"
    agg["cites"] = [
        "experiments/exp_component5_wired_endtoend_v1.py (type_sentence_events_c3/c3_has_desire, reused)",
        "experiments/exp_c5_fair_goal_owner_v1.py (adoption-gate run_item pattern, baseline_majority)",
        "experiments/exp_c5_fair_goal_owner_primacy_v1.py (baseline_first_mention/nearest_subject)",
        "experiments/exp_component5_gold_role_isolated_v1.py (GeneralRecencyEntityResolver)",
        "hdlab/goal_owner_select.py (directed_goal_outcome_score, promoted 2026-08-05)",
        "hdlab/event_centrality_coref.py (EventCentralityReader, the coref organ under test)",
        "hdlab/coref.py (build_pronoun_targets)",
        "hdlab/self_improving_loop.py (decide_keep_or_revert, promoted 2026-08-02)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    core, twins = load_bank_explicit_psych()
    assert len(core) >= 15, f"expected N>=15 explicit_psych recency-trap core items, got {len(core)}"
    assert len(twins) >= 5, f"expected a real twin subset, got {len(twins)}"
    print(f"[bank] {len(core)} core + {len(twins)} twin explicit_psych recency-trap items", flush=True)

    # (1) mention adapter produces a well-formed mention list + at least one target
    it0 = next(it for it in core if it["id"] == "t01_amy_ice_foil_jo")
    mentions = item_to_mentions(it0)
    assert len(mentions) == 3, f"expected 3 mentions (owner, foil, pronoun): {mentions}"
    assert mentions[0]["head"] == "amy" and mentions[1]["head"] == "jo" and mentions[2]["is_pronoun"]
    targets = build_pronoun_targets(mentions)
    assert len(targets) == 1, f"expected exactly 1 pronoun target: {targets}"
    print("[SELFTEST 1/7] mention/target adapter well-formed on a known item", flush=True)

    # (2) recency-mode coref reproduces the KNOWN recency-trap failure (picks the foil, matching
    # the toy positional baseline this bank was gold-VET'd against).
    coref_recency = resolve_outcome_coref(it0, "recency")
    assert coref_recency == "jo", f"recency coref-mode expected to fall for the trap (jo), got {coref_recency}"
    print(f"[SELFTEST 2/7] recency coref-mode falls for the trap on {it0['id']!r} "
          f"(picked {coref_recency!r}, matching the known-falsified recency failure mode)", flush=True)

    # (3) event_role-mode coref must differ from recency-mode on this same item (ARMS-MUST-DIFFER
    # exercised at the single-item level, not just the aggregate hash-check in run()).
    coref_event_role = resolve_outcome_coref(it0, "event_role")
    assert coref_event_role != coref_recency, (
        f"event_role and recency coref modes must diverge on a genuine trap: "
        f"{coref_event_role!r} vs {coref_recency!r}")
    print(f"[SELFTEST 3/7] event_role coref-mode diverges from recency-mode on {it0['id']!r} "
          f"(picked {coref_event_role!r})", flush=True)

    # (4) end-to-end: event_role-mode's FINAL adopted owner on this trap must be gold (amy) -- the
    # adoption gate must trust the correct coref pick, decoded via the register (not string eq).
    row = run_item(it0, "event_role", seed=0)
    assert row["matches_gold"] is True, f"event_role end-to-end must match gold on this trap: {row}"
    assert row["adopt"] == "content", row
    print(f"[SELFTEST 4/7] event_role end-to-end adopts the correct owner on {it0['id']!r}: {row}",
          flush=True)

    # (5) scramble collapses this item's event_role win (non-vacuous-scramble check).
    assert row["scrambled_matches_gold"] is False, (
        f"role-scramble must collapse the correct adoption: {row}")
    print("[SELFTEST 5/7] role-scramble collapses the event_role win on this item", flush=True)

    # (6) recency-mode's end-to-end on the SAME item must NOT beat gold (the adoption gate should
    # revert to baseline or adopt the wrong coref pick -- either way, not correct).
    row_rec = run_item(it0, "recency", seed=0)
    assert row_rec["matches_gold"] is False, (
        f"recency-mode end-to-end expected to fail on this genuine trap: {row_rec}")
    print("[SELFTEST 6/7] recency-mode end-to-end fails on the same trap (as expected)", flush=True)

    # (7) one full seed sanity: cardinality + arms differ + positional baselines computed.
    res = run_seed(0)
    assert res["n_divergent"] >= 10, f"too few divergent items for a powered test: {res['n_divergent']}"
    digests, differ = _arms_must_differ(res)
    assert differ, f"META_RULE_AF: coref modes bit-identical across the full item set: {digests}"
    pb = res["positional_baselines_divergent"]
    assert pb["recency"] == 0.0, f"recency positional baseline must be 0.0 by construction: {pb}"
    print(f"[SELFTEST 7/7] seed0 full run: N_divergent={res['n_divergent']} "
          f"recency_mode_acc={res['per_mode']['recency']['system_accuracy_divergent']} "
          f"event_role_mode_acc={res['per_mode']['event_role']['system_accuracy_divergent']} "
          f"positional_baselines={pb}", flush=True)

    # promoted-organ + coref-organ self-tests (proves the reused mechanisms themselves, not just
    # this cell's use of them).
    from hdlab.goal_owner_select import self_test as organ_self_test
    from hdlab.event_centrality_coref import _run_all_selftests as coref_self_test
    organ_res = organ_self_test()
    coref_res = coref_self_test()
    return {
        "mention_adapter": "passed", "recency_trap_pick": coref_recency,
        "event_role_trap_pick": coref_event_role, "endtoend_row_event_role": row,
        "endtoend_row_recency": row_rec, "seed0_positional_baselines": pb,
        "promoted_organ_self_test": organ_res, "coref_organ_self_test": coref_res,
    }


def _run_no_regression_checks() -> dict:
    """Confirms no touched-module regression: reruns the C3-typing cell's own self-test and the
    coref organ's own self-test (both untouched by this cell)."""
    out = {}
    try:
        from exp_component5_wired_endtoend_v1 import self_test as wired_self_test
        wr = wired_self_test()
        out["wired_endtoend_selftest"] = {"passed": True, "keys": list(wr.keys())}
    except Exception as e:  # noqa: BLE001
        out["wired_endtoend_selftest"] = {"passed": False, "error": f"{type(e).__name__}: {e}"}
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
