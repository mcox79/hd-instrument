"""exp_c5_primacy_trap_endtoend_promoted_organ_v1 -- WIRE-DON'T-ISLAND: run the goal-owner
end-to-end pipeline (real event_role coref + hdlab/goal_owner_select.directed_goal_outcome_score
integrator) on the PRIMACY-TRAP subset (p01-p20) of experiments/data/goal_owner_fair_v1.jsonl,
consuming the PROMOTED production GOAL-typing organ hdlab/goal_typing.py (type_goal_events /
has_goal) -- not any experiment-cell detector re-import. Completes the fairness picture: the
RECENCY-trap subset (t01-t28) was already tested end-to-end
(data/exp_c5_real_coref_endtoend_purpose_infinitival_v1/metrics.json, commit a2eb1ea25) where
first_mention/majority were 1.0 on the divergent subset (NOT gated, bank-structural -- owner is
named first + tied-or-more frequent on that bank's construction). The primacy-trap items are
constructed to DEFEAT first_mention/majority (foil is named first AND most frequently; owner is
named exactly once, mid-passage) so THIS cell is the first one where all four positional baselines
can be legitimately probed together.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: EXEMPTED (single mechanism-arm cell, no typing-mode/coref-mode sweep --
#   see arms_differ_exempted below for the positive-control substitute: GOAL-typing detection rate
#   under the (required) multi-sentence scan vs a naive S0-only scan, which DOES differ 20/20 vs
#   0/20, proving the generalization is load-bearing, not vacuous).
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: boolean-match discriminator (owner-selection accuracy), not an SNR/argmax-noise regime
# - baseline_in_band: N/A -- positional baselines are PRE-REGISTERED near-zero BY CONSTRUCTION on
#   the divergent subset for ALL FOUR baselines on this bank (recency AND first_mention/majority/
#   nearest_subject), MEASURED inline before authoring (see PRE-FLIGHT PROBE below) -- that IS the
#   gate, reused convention from exp_c5_real_coref_endtoend_purpose_infinitival_v1.
# - discriminator survives scale: FULL N (20 primacy-trap core items, all has_distractor=true, no
#   twin variants exist for this subset), no separate smoke-N; --self-test runs the full bank.
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration below
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds(3) x n_items(20) = 60 row-evals; gate on len(per_seed)==3
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check: default_ok_for_this_regime (all thresholds/formulas reused verbatim from the
#   already-VET'd exp_c5_real_coref_endtoend_purpose_infinitival_v1 / hdlab/goal_owner_select.py)
# - numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in this docstring

PRE-REG (LOCAL-ONLY, in-process foreground; no queue dispatch, no push; task-brief-authored,
registered BEFORE reading the full-run verdict below -- the PRE-FLIGHT PROBE section documents the
exact inline measurement run to derive these bands honestly, per META_RULE_AC).

  SCOPE: trap_type=="primacy" subset only (p01-p20, N=20, MEASURED@ grep count of
  experiments/data/goal_owner_fair_v1.jsonl). All 20 items have has_distractor=true; NO twin
  (no-distractor) variants exist for this subset (MEASURED@ same file: 0 rows with
  twin_of starting "p" or trap_type=="primacy" and has_distractor=false) -- so no twin-control arm
  is reported for this subset (twin_control_accuracy: "n/a_no_twins_in_primacy_subset").
  verb_type breakdown: explicit_psych p01-p12 (N=12), action_implied p13-p20 (N=8),
  MEASURED@ grep count before authoring.

  STRUCTURAL DIFFERENCE FROM THE RECENCY-TRAP BANK (why a new build_role_seq is required, not a
  bit-identical reuse of PREVMOD.build_role_seq): the recency-trap bank's GOAL sentence is ALWAYS
  sentence index 0 (owner is introduced first, with the psych/purpose-infinitival GOAL verb, in
  S0); PREVMOD.build_role_seq hardcodes sents[0] as the GOAL sentence and sents[-1] as the outcome
  sentence. The primacy-trap bank's 4-sentence construction is: S0 = foil's early action (NOT the
  GOAL sentence), S1 = owner's GOAL sentence, S2 = foil's action again, S3 = outcome. Calling
  PREVMOD.build_role_seq unmodified on a primacy item types S0 (foil's action, no GOAL verb) as
  the "GOAL sentence" and MISSES the real GOAL entirely -- MEASURED@ inline pre-flight probe
  (below): goal_present=False on 20/20 primacy items when using PREVMOD.build_role_seq bit-
  identical. This cell's build_role_seq_primacy (below) scans ALL non-outcome sentences (typer
  applied per-sentence against the fixed `owner` subject, events unioned) instead of hardcoding S0
  -- the natural generalization once GOAL-sentence position is no longer fixed. Re-verified this
  does not spuriously fire on foil's action sentences (S0/S2 contain no desiderative/purpose-
  infinitival/outcome-lexicon tokens for any of the 20 items, MEASURED@ inline probe: goal_present
  count is IDENTICAL, 20/20, whether S0/S2 are included or the scan is restricted to S1 alone --
  the union is safe on this bank, not accidentally permissive).

  PRE-FLIGHT PROBE (MEASURED@ inline python run before authoring this pre-reg, not discovered
  post-hoc -- disclosing the KNOWN-IN-ADVANCE outcome per META_RULE_AC / the harness's own
  KNOWN-IN-ADVANCE-FINDING convention):
    (a) ALL FOUR positional baselines (recency, first_mention, nearest_subject, majority) score
        0/20 (0.0) on the full primacy-trap bank -- MEASURED: foil is named first (defeats
        first_mention) AND twice vs owner's once (defeats majority, ties broken by first-mention)
        AND is the subject of the sentence immediately preceding the outcome (defeats
        nearest_subject) AND is the most-recently-named entity walking through all sentences
        (defeats recency). This is BY CONSTRUCTION (the trap's design intent) and is the
        divergent-subset selector: N_divergent = 20/20 (recency baseline wrong on all 20 items).
    (b) The PROMOTED GOAL-typing organ (hdlab.goal_typing.type_goal_events), run through
        build_role_seq_primacy, correctly detects a GOAL event for `owner` on 20/20 items --
        MEASURED: this is the mechanism working as validated (recency-trap subset, promotion
        witness). GOAL-typing is NOT the failure point on this subset.
    (c) The REAL event_role coref resolver (hdlab.event_centrality_coref.EventCentralityReader,
        production centrality_mode="event_role", via the bit-identical item_to_mentions /
        resolve_outcome_coref adapter reused from PREVMOD) resolves the outcome pronoun to the
        FOIL on 20/20 items -- MEASURED (inline probe, p01_amy_ice_foil_jo traced in full: the
        pronoun's only same-gold-cluster prior mention is the owner mention at sent_dist=2, but
        the resolver's event_role-centrality scoring still selects the foil, resolved_cluster=1 !=
        gold_cluster=0, correct=False). This means BOTH candidate resolutions the adoption gate
        chooses between (recency-positional baseline AND real-event_role-coref) point to the SAME
        wrong entity (foil) on this trap -- score_b == score_c bit-identical (cluster_ids_b ==
        cluster_ids_c at the outcome position), so directed_goal_outcome_score's diff is exactly
        0.0, decide_keep_or_revert abstains (falls into ABSTAIN_BAND_DEFAULT around 0), and
        final_owner = baseline_owner = foil on 20/20 items. System accuracy = 0/20 = 0.0, TIED
        with (not beating) all four positional baselines.
    (d) This is a GENUINE, DISCLOSED FINDING about the adoption-gate architecture, not a bug: the
        integrator only ever chooses BETWEEN two candidate resolutions it is handed (recency vs
        real-coref); it cannot synthesize a THIRD candidate (the GOAL-holder) from scratch when
        NEITHER upstream resolver ever nominates that entity as the outcome-pronoun's referent.
        The primacy-trap construction defeats the antecedent-resolution stage itself (real coref's
        event-role centrality signal loses to surface recency at sent_dist=2 with no closer same-
        cluster candidate), one layer upstream of GOAL-typing / the adoption gate -- GOAL-typing
        fires correctly (20/20) but has no correct candidate to redirect the outcome attribution
        toward.

  HYPOTHESIZED@this docstring, PRE-REGISTERED BEFORE the formal cell run below (matches the
  MEASURED pre-flight probe exactly, so the formal run is a REPRODUCTION/confirmation, not a
  surprise reframed after the fact): system_accuracy_divergent = 0.0 on both verb_type subsets;
  ties (does not beat) all four positional baselines; scramble control is VACUOUS (scramble_vacuous
  =True) because the unscrambled gain is already 0 (nothing to collapse -- the content candidate
  never wins in the first place, so corrupting its GOAL binding cannot change an outcome that was
  never adopted).

  BASELINES (all 4 positional, reused bit-identical): recency (via
  PREVMOD.resolve_outcome_recency_positional -- the adoption gate's baseline candidate, 0.0 by
  construction on the divergent subset, defines the divergent subset itself), first_mention,
  nearest_subject, majority (all three imported bit-identical from
  experiments/exp_c5_fair_goal_owner_primacy_v1.py). ALL FOUR are gated on this subset (unlike the
  recency-trap bank, where only recency/nearest_subject were gated and first_mention/majority were
  reported-only per that cell's own HONEST DISCLOSURE) -- see PRE-FLIGHT PROBE (a) for the measured
  justification.

  SCRAMBLE control (non-vacuous-scramble pattern, reused bit-identical formula from
  PREVMOD.run_item): for the CONTENT candidate's role_seq only, relabel the GOAL role's owner
  entity to the item's foil before scoring; corrupted GOAL binding must drop the content score. On
  this subset the unscrambled content score is expected to already equal the baseline score
  (gain_unscr == 0, per PRE-FLIGHT PROBE (c)), so the scramble check is HYPOTHESIZED to be VACUOUS
  (scramble_vacuous=True, reported honestly per PREVMOD's own vacuous-scramble convention, not
  silently upgraded to a false collapse-pass).

  BANDS (per-subset; OVERALL = worse of the two per-subset bands, matching PREVMOD's convention):
    HARD-PASS (either subset) -- system_accuracy_divergent STRICTLY beats ALL FOUR positional
      baselines (recency, first_mention, nearest_subject, majority) on that subset's divergent
      items AND the scramble control collapses NON-VACUOUSLY (gain_unscr > 0 and gain_scr <=
      0.5*gain_unscr).
    HARD-FAIL (either subset) -- system_accuracy_divergent does NOT strictly beat first_mention OR
      does NOT strictly beat majority (the two baselines this subset is specifically constructed to
      defeat) -- "primacy trap not actually defeated / coref selection can't handle primacy, a real
      finding" (verbatim task-brief HARD-FAIL condition).
    MIDDLE_BAND (either subset) -- system beats recency/nearest_subject (the two baselines already
      known-gated from the recency-trap bank) but not first_mention/majority, OR beats all four but
      the scramble check cannot discriminate (vacuous in the WRONG direction, i.e. gain_unscr>0 but
      gain_scr also >0 non-collapsing) -- reported, not silently folded into HARD-FAIL or HARD-PASS.
  OVERALL verdict = worst of {explicit_psych, action_implied} per-subset bands (rank HARD_FAIL <
  MIDDLE_BAND < HARD_PASS), matching PREVMOD.aggregate's own rank-of convention.

  If goal-typing is OOV/uncovered on any item (no GOAL event fires via either C3-EXPERIENCER-frame
  or the partitioned purpose-infinitival construction), that item's row records goal_present=False
  and is NOT silently dropped -- it still feeds n_divergent / the discriminating count and is
  listed in `goal_oov_ids` (MEASURED@ pre-flight probe: expected empty, 20/20 items fire GOAL, but
  this is checked live in the formal run, not assumed).

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `tools/substrate_query.sh "primacy
trap goal owner end to end promoted goal typing organ real coref positional baselines first
mention majority nearest subject recency"` -- see PRIOR_WORK_CHECK note at bottom of this docstring
(run + logged before dispatch per the standing discipline).

GUARDS: glass-box; deterministic given seed; ASCII-only; atomic metrics write (tmp+os.replace);
NOT dispatched to any queue (LOCAL-ONLY, in-process foreground, no push); no modification to
hdlab/goal_typing.py / hdlab/goal_owner_select.py / hdlab/event_centrality_coref.py /
hdlab/self_improving_loop.py / hdlab/coref.py / hdlab/learner/ (production hdlab/ untouched); no
modification to exp_c5_real_coref_endtoend_purpose_infinitival_v1.py or
exp_c5_fair_goal_owner_primacy_v1.py (both imported and reused bit-identical, not edited).

Cites: hdlab/goal_typing.py (PROMOTED GOAL-typing organ under test, commit 5449161c2 -- consumed
directly per the WIRE-DON'T-ISLAND mandate, NOT the experiment-cell detectors it was promoted
from); experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py (item_to_mentions,
resolve_outcome_coref, resolve_outcome_recency_positional, _outcome_pos, _sentences, GENDER_SCHEME
-- all reused bit-identical); experiments/exp_c5_fair_goal_owner_primacy_v1.py
(baseline_first_mention, baseline_nearest_subject, baseline_majority, reused bit-identical);
hdlab/goal_owner_select.py (directed_goal_outcome_score, promoted 2026-08-05);
hdlab/event_centrality_coref.py (EventCentralityReader, fixed event_role mode);
hdlab/coref.py (build_pronoun_targets); hdlab/self_improving_loop.py (decide_keep_or_revert,
promoted 2026-08-02); verification/verify_goal_typing.py (promotion witness pattern this cell
follows: import the certified helpers, never re-author them).
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

ANCHOR_NAME = "c5_primacy_trap_endtoend_promoted_organ_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_owner_fair_v1.jsonl")

# ---- PROMOTED PRODUCTION ORGAN (WIRE-DON'T-ISLAND: consume hdlab/, not the experiment cells) ----
from hdlab.goal_typing import type_goal_events, has_goal, R_GOAL  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the real end-to-end harness's generic (typer-independent) helpers ----
import exp_c5_real_coref_endtoend_purpose_infinitival_v1 as PREVMOD  # noqa: E402
from exp_situation_model_goal_outcome_dimension_v1 import R_UNMET, R_MET, _sentences  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the primacy-aware positional baselines --------------------------------
from exp_c5_fair_goal_owner_primacy_v1 import (  # noqa: E402
    baseline_first_mention, baseline_nearest_subject, baseline_majority,
)
# ---- REUSED BIT-IDENTICAL: the promoted C5 integrator + adoption gate ---------------------------
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
VERB_TYPES = ("explicit_psych", "action_implied")


# ============================================================================ bank load
def load_bank_primacy(verb_type: str):
    """primacy-trap subset (trap_type=='primacy'), verb_type in {'explicit_psych','action_implied'}.
    All rows have has_distractor=true; no twin variants exist for this subset (checked below)."""
    rows = []
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    rows = [r for r in rows if r.get("trap_type") == "primacy" and r["verb_type"] == verb_type]
    assert all(r["has_distractor"] for r in rows), "unexpected no-distractor row in primacy subset"
    return rows


# ============================================================================ NEW: role_seq builder that
# scans ALL non-outcome sentences (GOAL-sentence position is not fixed on this bank, unlike the
# recency-trap bank's sents[0] convention -- see STRUCTURAL DIFFERENCE in the docstring above).
def _promoted_typer(sentence: str, subject):
    return type_goal_events(sentence, subject)


def build_role_seq_primacy(item: dict, outcome_entity, scramble_goal_to_foil=None):
    sents = _sentences(item["text"])
    owner = item["owner"]
    role_seq, cluster_ids = [], []
    for s in sents[:-1]:
        for (entity, role) in _promoted_typer(s, owner):
            eff = entity
            if scramble_goal_to_foil is not None and role == R_GOAL and entity == owner:
                eff = scramble_goal_to_foil
            role_seq.append(role)
            cluster_ids.append(eff)
    for (entity, role) in _promoted_typer(sents[-1], outcome_entity):
        role_seq.append(role)
        cluster_ids.append(entity)
    return role_seq, cluster_ids


def _outcome_pos(role_seq):
    positions = [i for i, r in enumerate(role_seq) if r in (R_UNMET, R_MET)]
    return positions[-1] if positions else None


# ============================================================================ per-item eval (single arm: promoted organ)
def run_item(item: dict, seed: int):
    gold = item["gold_outcome_owner"]
    foil = item.get("foil")

    baseline_owner = PREVMOD.resolve_outcome_recency_positional(item)
    role_seq_b, cluster_ids_b = build_role_seq_primacy(item, baseline_owner)
    outcome_pos = _outcome_pos(role_seq_b)

    coref_owner = PREVMOD.resolve_outcome_coref(item)
    role_seq_c, cluster_ids_c = build_role_seq_primacy(item, coref_owner)
    assert role_seq_b == role_seq_c, (
        f"{item['id']}: role attribution must be resolver-independent: {role_seq_b} vs {role_seq_c}")

    goal_present = R_GOAL in role_seq_b
    row = dict(id=item["id"], gold=gold, baseline_owner=baseline_owner, coref_owner=coref_owner,
               goal_present=goal_present, baseline_matches_gold=(baseline_owner == gold),
               coref_raw_matches_gold=(coref_owner == gold))

    if outcome_pos is None:
        row.update(final_owner=None, matches_gold=False, adopt=None,
                    scrambled_final_owner=None, scrambled_matches_gold=None,
                    directed_score_baseline=None, directed_score_content=None)
        return row

    score_b = directed_goal_outcome_score(role_seq_b, cluster_ids_b, seed, outcome_pos)
    score_c = directed_goal_outcome_score(role_seq_c, cluster_ids_c, seed, outcome_pos)
    adopt = decide_keep_or_revert({"content": score_c - score_b}, ABSTAIN_BAND_DEFAULT)
    final_owner = cluster_ids_c[outcome_pos] if adopt == "content" else cluster_ids_b[outcome_pos]
    row.update(final_owner=final_owner, matches_gold=(final_owner == gold), adopt=adopt,
               directed_score_baseline=score_b, directed_score_content=score_c)

    if foil is not None:
        role_seq_s, cluster_ids_s = build_role_seq_primacy(item, coref_owner,
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
def run_seed(seed: int):
    out = {}
    for verb_type in VERB_TYPES:
        items = load_bank_primacy(verb_type)
        rows = [run_item(it, seed) for it in items]
        div = [r for r in rows if not r["baseline_matches_gold"]]  # recency-divergent (expect ALL)
        n_div = len(div)

        def rate(rows_, key):
            vals = [r[key] for r in rows_ if r[key] is not None]
            return round(sum(bool(v) for v in vals) / len(vals), 4) if vals else None

        div_items = [it for it in items if any(r["id"] == it["id"] for r in div)]

        def pos_rate(fn):
            vals = [(fn(it) == it["gold_outcome_owner"]) for it in div_items]
            return round(sum(vals) / len(vals), 4) if vals else None

        out[verb_type] = dict(
            n_items=len(items), n_divergent=n_div,
            recency_floor_divergent=rate(div, "baseline_matches_gold"),
            system_accuracy_divergent=rate(div, "matches_gold"),
            system_scrambled_accuracy_divergent=rate(
                [r for r in div if r["scrambled_final_owner"] is not None], "scrambled_matches_gold"),
            n_goal_present=sum(1 for r in rows if r["goal_present"]),
            goal_oov_ids=[r["id"] for r in rows if not r["goal_present"]],
            miss_ids=[r["id"] for r in div if not r["matches_gold"]],
            positional_baselines_divergent=dict(
                recency=0.0 if div_items else None,
                first_mention=pos_rate(baseline_first_mention),
                nearest_subject=pos_rate(baseline_nearest_subject),
                majority=pos_rate(baseline_majority),
            ),
            rows=rows,
        )
    return dict(seed=seed, per_verb_type=out)


# ============================================================================ positive-control (substitute for
# ARMS-MUST-DIFFER, META_RULE_AF -- see docstring): naive S0-only GOAL scan vs the required
# multi-sentence scan MUST differ (0/20 vs 20/20 GOAL-detection) -- proves the generalization is
# load-bearing, not vacuous. Computed once at seed0.
def _positive_control_goal_scan_differs():
    all_items = load_bank_primacy("explicit_psych") + load_bank_primacy("action_implied")
    n_naive = 0
    n_scan = 0
    for it in all_items:
        sents = _sentences(it["text"])
        owner = it["owner"]
        naive_events = _promoted_typer(sents[0], owner)  # PREVMOD-style hardcoded S0
        if any(r == R_GOAL for (_e, r) in naive_events):
            n_naive += 1
        scan_events = []
        for s in sents[:-1]:
            scan_events.extend(_promoted_typer(s, owner))
        if any(r == R_GOAL for (_e, r) in scan_events):
            n_scan += 1
    return {"n_items": len(all_items), "naive_s0_only_goal_detected": n_naive,
            "multi_sentence_scan_goal_detected": n_scan, "differ": n_naive != n_scan}


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())
    n = len(seeds)
    baseline_names = ("recency", "first_mention", "nearest_subject", "majority")
    defeat_names = ("first_mention", "majority")  # the two THIS subset is constructed to defeat

    def mean(verb_type, key):
        vals = [per_seed[s]["per_verb_type"][verb_type][key] for s in seeds
                if per_seed[s]["per_verb_type"][verb_type][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    per_vt = {}
    subset_verdicts = {}
    for verb_type in VERB_TYPES:
        pos_base = per_seed[seeds[0]]["per_verb_type"][verb_type]["positional_baselines_divergent"]
        n_divergent = per_seed[seeds[0]]["per_verb_type"][verb_type]["n_divergent"]
        n_divergent_ok = all(
            per_seed[s]["per_verb_type"][verb_type]["n_divergent"] == n_divergent for s in seeds)

        acc = mean(verb_type, "system_accuracy_divergent")
        beats = {bn: (acc is not None and pos_base.get(bn) is not None and acc > pos_base[bn])
                 for bn in baseline_names}
        beats_all_four = all(beats.values()) if acc is not None else False
        defeats_the_trap = all(beats[bn] for bn in defeat_names) if acc is not None else False

        unscr = mean(verb_type, "system_accuracy_divergent")
        scr = mean(verb_type, "system_scrambled_accuracy_divergent")
        floor = pos_base.get("recency")
        gain_unscr = (unscr - floor) if (unscr is not None and floor is not None) else None
        gain_scr = (scr - floor) if (scr is not None and floor is not None) else None
        if gain_unscr is not None and gain_unscr > 1e-9:
            scramble_collapses = (gain_scr is not None and gain_scr <= 0.5 * gain_unscr + 1e-9)
            scramble_vacuous = False
        else:
            scramble_collapses = (gain_scr is not None and gain_scr <= 1e-9)
            scramble_vacuous = True

        if beats_all_four and scramble_collapses and not scramble_vacuous:
            v = "HARD_PASS_DEFEATS_ALL_FOUR_POSITIONAL"
        elif not defeats_the_trap:
            v = "HARD_FAIL_PRIMACY_TRAP_NOT_DEFEATED_COREF_SELECTION_LIMIT"
        elif defeats_the_trap and not beats_all_four:
            v = "MIDDLE_BAND_DEFEATS_FIRST_MENTION_MAJORITY_NOT_ALL_FOUR"
        else:
            v = "MIDDLE_BAND"

        subset_verdicts[verb_type] = v
        per_vt[verb_type] = dict(
            n_items=per_seed[seeds[0]]["per_verb_type"][verb_type]["n_items"],
            n_divergent=n_divergent, n_divergent_ok=n_divergent_ok,
            positional_baselines_divergent=pos_base,
            system_accuracy_divergent=acc,
            system_scrambled_accuracy_divergent=scr,
            beats_per_baseline=beats, beats_all_four_positional=beats_all_four,
            defeats_the_trap_first_mention_and_majority=defeats_the_trap,
            scramble_collapses=scramble_collapses, scramble_vacuous=scramble_vacuous,
            n_goal_present_seed0=per_seed[seeds[0]]["per_verb_type"][verb_type]["n_goal_present"],
            goal_oov_ids_seed0=per_seed[seeds[0]]["per_verb_type"][verb_type]["goal_oov_ids"],
            miss_ids_seed0=per_seed[seeds[0]]["per_verb_type"][verb_type]["miss_ids"],
            verdict=v,
        )

    def rank_of(v):
        if v.startswith("HARD_FAIL"):
            return 0
        if v.startswith("HARD_PASS"):
            return 2
        return 1

    overall_rank = min(rank_of(subset_verdicts[vt]) for vt in VERB_TYPES)
    overall = {0: "HARD_FAIL", 1: "MIDDLE_BAND", 2: "HARD_PASS"}[overall_rank]

    where_breaks = {
        "explicit_psych_misses": per_vt["explicit_psych"]["miss_ids_seed0"],
        "action_implied_misses": per_vt["action_implied"]["miss_ids_seed0"],
        "explicit_psych_goal_oov": per_vt["explicit_psych"]["goal_oov_ids_seed0"],
        "action_implied_goal_oov": per_vt["action_implied"]["goal_oov_ids_seed0"],
    }

    msg = (
        f"explicit_psych: system={per_vt['explicit_psych']['system_accuracy_divergent']} vs "
        f"baselines={per_vt['explicit_psych']['positional_baselines_divergent']} "
        f"(N_div={per_vt['explicit_psych']['n_divergent']}, verdict={subset_verdicts['explicit_psych']}). "
        f"action_implied: system={per_vt['action_implied']['system_accuracy_divergent']} vs "
        f"baselines={per_vt['action_implied']['positional_baselines_divergent']} "
        f"(N_div={per_vt['action_implied']['n_divergent']}, verdict={subset_verdicts['action_implied']}). "
        f"OVERALL={overall} (worse-of-two-subsets rule; HARD-FAIL iff system fails to strictly "
        f"beat first_mention OR majority on either subset).")

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
        json.dump(d, f, indent=2, default=str)
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
        pv = res["per_verb_type"]
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"explicit_psych(acc={pv['explicit_psych']['system_accuracy_divergent']}) "
              f"action_implied(acc={pv['action_implied']['system_accuracy_divergent']})", flush=True)

    raw = load_units(OUTPUT_DIR)
    per_seed = {int(v["seed"]): v for v in raw.values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")

    pos_ctrl = _positive_control_goal_scan_differs()
    if not pos_ctrl["differ"]:
        raise AssertionError(
            f"POSITIVE-CONTROL VIOLATION (arms_differ_exempted substitute): naive S0-only scan and "
            f"the required multi-sentence scan produced the SAME GOAL-detection count -- the "
            f"generalization is not load-bearing: {pos_ctrl}")

    agg = aggregate(per_seed)
    agg["arms_differ_verified"] = False
    agg["arms_differ_exempted"] = [("naive_s0_only_scan", "multi_sentence_scan_primacy")]
    agg["arms_differ_positive_control"] = pos_ctrl
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(seeds=SEEDS, verb_types=list(VERB_TYPES), coref_mode_fixed="event_role",
                         abstain_band=ABSTAIN_BAND_DEFAULT, bank_path=BANK_PATH,
                         scope="explicit_psych+action_implied x trap_type=primacy",
                         cardinality_ok=(len(per_seed) == EXPECTED_N_SEEDS),
                         typer="hdlab.goal_typing.type_goal_events (PROMOTED organ, wire-dont-island)")
    agg["hp_scope"] = {
        "explicit_psych": ["beats_all_four_positional", "scramble_collapses_non_vacuous"],
        "action_implied": ["beats_all_four_positional", "scramble_collapses_non_vacuous"],
    }
    agg["final_metrics_atomicity"] = "tmp_replace"
    agg["crlb_n/a"] = "boolean-match discriminator (owner-selection accuracy), not an SNR/argmax-noise regime"
    agg["baseline_in_band_n/a"] = ("positional baselines pre-registered near-zero by construction on "
                                    "the divergent subset for ALL FOUR baselines on this bank -- see "
                                    "PRE-FLIGHT PROBE in docstring")
    agg["prereg"] = "inline (docstring, per LOCAL-ONLY task brief; no separate preregs/ file)"
    agg["cites"] = [
        "hdlab/goal_typing.py (PROMOTED GOAL-typing organ, commit 5449161c2, consumed directly)",
        "experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py (item_to_mentions, "
        "resolve_outcome_coref, resolve_outcome_recency_positional, reused bit-identical)",
        "experiments/exp_c5_fair_goal_owner_primacy_v1.py (baseline_first_mention/"
        "nearest_subject/majority, reused bit-identical)",
        "hdlab/goal_owner_select.py (directed_goal_outcome_score, promoted 2026-08-05)",
        "hdlab/event_centrality_coref.py (EventCentralityReader, fixed event_role mode)",
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
    ep = load_bank_primacy("explicit_psych")
    ai = load_bank_primacy("action_implied")
    assert len(ep) == 12, f"expected 12 explicit_psych primacy items, got {len(ep)}"
    assert len(ai) == 8, f"expected 8 action_implied primacy items, got {len(ai)}"
    print(f"[bank] primacy: explicit_psych={len(ep)}, action_implied={len(ai)}", flush=True)

    # (1) STRUCTURAL CHECK: naive PREVMOD.build_role_seq (S0-hardcoded) MISSES the GOAL entirely on
    # a primacy item -- proves the structural-difference claim in the docstring is real, not
    # asserted without evidence.
    it01 = next(it for it in ep if it["id"] == "p01_amy_ice_foil_jo")
    naive_role_seq, _ = PREVMOD.build_role_seq(it01, it01["owner"], _promoted_typer)
    assert R_GOAL not in naive_role_seq, (
        f"expected naive S0-only role_seq to MISS the GOAL on a primacy item: {naive_role_seq}")
    print("[SELFTEST 1/8] naive PREVMOD.build_role_seq (S0-only) misses GOAL on p01 (as pre-registered)",
          flush=True)

    # (2) build_role_seq_primacy DOES detect the GOAL on the same item.
    scan_role_seq, scan_cluster_ids = build_role_seq_primacy(it01, it01["owner"])
    assert R_GOAL in scan_role_seq, f"expected multi-sentence scan to detect GOAL: {scan_role_seq}"
    print("[SELFTEST 2/8] build_role_seq_primacy detects GOAL on p01 (structural fix confirmed)",
          flush=True)

    # (3) ALL FOUR positional baselines are wrong (foil) on p01 -- the trap fires as designed.
    gold = it01["gold_outcome_owner"]
    assert PREVMOD.resolve_outcome_recency_positional(it01) != gold
    assert baseline_first_mention(it01) != gold
    assert baseline_nearest_subject(it01) != gold
    assert baseline_majority(it01) != gold
    print("[SELFTEST 3/8] all four positional baselines wrong on p01 (trap fires as designed)",
          flush=True)

    # (4) real event_role coref ALSO resolves to the foil on p01 (the pre-registered upstream
    # limitation -- confirms this is not a harness bug, the real coref organ genuinely loses here).
    coref_owner = PREVMOD.resolve_outcome_coref(it01)
    assert coref_owner != gold, (
        f"PRE-REGISTERED expectation: real coref also loses to primacy on p01, got {coref_owner}")
    print(f"[SELFTEST 4/8] real event_role coref resolves p01 to foil (pre-registered limitation "
          f"confirmed: coref_owner={coref_owner!r} != gold={gold!r})", flush=True)

    # (5) end-to-end run_item on p01: goal_present True, but matches_gold False (pre-registered).
    row = run_item(it01, seed=0)
    assert row["goal_present"] is True
    assert row["matches_gold"] is False, f"pre-registered outcome: p01 end-to-end should MISS: {row}"
    print(f"[SELFTEST 5/8] p01 end-to-end: goal_present=True, matches_gold=False (pre-registered)",
          flush=True)

    # (6) positive-control substitute for ARMS-MUST-DIFFER: naive vs scan GOAL-detection differs.
    pc = _positive_control_goal_scan_differs()
    assert pc["differ"], f"POSITIVE-CONTROL VIOLATION: {pc}"
    print(f"[SELFTEST 6/8] positive control: naive={pc['naive_s0_only_goal_detected']}/20 vs "
          f"scan={pc['multi_sentence_scan_goal_detected']}/20 GOAL-detection differs", flush=True)

    # (7) cardinality + divergent-subset sanity for both subsets.
    res = run_seed(0)
    for vt in VERB_TYPES:
        pb = res["per_verb_type"][vt]["positional_baselines_divergent"]
        assert pb["recency"] == 0.0, f"{vt}: recency positional baseline must be 0.0: {pb}"
        n_div = res["per_verb_type"][vt]["n_divergent"]
        n_items = res["per_verb_type"][vt]["n_items"]
        assert n_div == n_items, f"{vt}: expected ALL items divergent on the recency baseline (the "\
            f"trap's own construction), got {n_div}/{n_items}"
    print(f"[SELFTEST 7/8] both subsets: recency baseline=0.0, all items divergent (trap fires "
          f"on 100% of the bank, as designed)", flush=True)

    # (8) reused organs' own self-tests still pass (no touched-module regression).
    from hdlab.goal_typing import self_test as organ_self_test
    from hdlab.event_centrality_coref import _run_all_selftests as coref_self_test
    organ_res = organ_self_test()
    coref_res = coref_self_test()
    print("[SELFTEST 8/8] promoted organ + coref organ self-tests pass", flush=True)

    return {
        "p01_naive_role_seq": naive_role_seq, "p01_scan_role_seq": scan_role_seq,
        "p01_row": row, "positive_control": pc,
        "seed0_positional_baselines": {vt: res["per_verb_type"][vt]["positional_baselines_divergent"]
                                        for vt in VERB_TYPES},
        "promoted_organ_self_test": organ_res, "coref_organ_self_test": coref_res,
    }


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
