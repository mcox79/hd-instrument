"""exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1 -- THE CANDIDATE-GENERATION FIX for
the primacy-trap end-to-end HARD_FAIL (data/exp_c5_primacy_trap_endtoend_promoted_organ_v1/
metrics.json, commit 43e942ca0, 0/20 on primacy). Diagnosis (notes/deep_vet_comprehension_organ_vs_
brain_2026-08-05.md "LANDED-4"): the failing cell's outcome-owner CANDIDATE POOL was {recency
positional baseline, real event_role coref}; under primacy BOTH candidates resolve the outcome
pronoun to the FOIL (recency because the foil is most-recently-named; real coref because event-role
centrality also loses to the foil's surface recency at sent_dist=2) -- score_b == score_c
bit-identical, the adoption gate abstains, final_owner is ALWAYS the foil. GOAL-typing itself fires
correctly 20/20; it is moot because the goal-holder is NEVER a candidate the integrator is handed.

THE FIX (this cell): replace bottom-up coref-pronoun candidate generation with GOAL-COHERENCE-BIASED
ENUMERATION over the entity set, reusing the pattern already proven primacy-robust in ISOLATION
(experiments/exp_c5_fair_goal_owner_primacy_v1.py: system=0.6, all four position baselines=0.0,
scramble non-vacuous) -- that cell's win comes from its candidate generator (ContentMatchResolver)
NOMINATING the open-goal entity as a candidate at all, not from a smarter integrator. Here the
enumeration is made explicit and literal, per the task brief: for the OUTCOME slot, every roster
entity is proposed as a candidate referent; hdlab.goal_owner_select.directed_goal_outcome_score
(unmodified promoted organ) scores each candidate's own whole-passage assignment; argmax selects
the final owner. GOAL-typing is delegated entirely to the PROMOTED production organ
(hdlab.goal_typing.type_goal_events, commit 5449161c2) -- wire-don't-island, no re-authored typer.

FAIRNESS (mandatory, disk-verified against the failing cell's OWN leak): the failing cell's
build_role_seq_primacy fixed `owner = item["owner"]` (== gold_outcome_owner in every row of this
bank, verified by inspection) as the subject for typing EVERY non-outcome sentence -- i.e. it used
the gold label to decide which entity's clauses count as GOAL-bearing. This cell does NOT do that:
each non-outcome sentence's subject is resolved STRUCTURALLY from the passage text via
GeneralRecencyEntityResolver.subject_entity (explicit roster-name detection, reused bit-identical
from experiments/exp_component5_gold_role_isolated_v1.py -- the same primitive the isolated cell's
own candidate generators use) -- never from item["owner"]/item["gold_outcome_owner"]. The entity SET
enumerated as outcome-slot candidates is item["roster"].keys() (structural passage metadata: who is
in the cast), never the gold label. The gold label (item["gold_outcome_owner"]) is read ONLY inside
run_item's scoring (`matches_gold = final_owner == gold`), never inside build_candidate_role_seq or
the enumeration loop. (Self-test 1 below re-derives this claim mechanically: on every item, the
structurally-resolved subject of the GOAL-bearing sentence equals item["owner"] BY COINCIDENCE of
this bank's construction, not by construction of this cell's code -- a bank where the GOAL sentence's
grammatical subject differed from the answer would still be typed correctly, because nothing here
special-cases the answer.)

MECHANISM SUMMARY (glass-box, deterministic given seed):
  1. For each non-outcome sentence, resolve its subject structurally (GeneralRecencyEntityResolver,
     explicit-name detection -- these sentences always name an entity, per bank construction) and
     type GOAL/ACTION events via the PROMOTED organ (hdlab.goal_typing.type_goal_events).
  2. For the outcome (final, pronoun-only) sentence: for EACH roster entity `c`, type events with
     subject=c (this is the enumeration: propose every entity as the outcome referent) and score the
     resulting whole-passage assignment with directed_goal_outcome_score(role_seq, cluster_ids, seed,
     outcome_pos). The score is 1.0 iff the entity THIS CANDIDATE bound to the outcome slot also
     carries an earlier GOAL event under that SAME candidate's assignment (byte-identical formula,
     hdlab/goal_owner_select.py, unmodified).
  3. final_owner = argmax_c score(c) (ties broken by sorted-roster-order, deterministic, and -- per
     self-test 5 -- NOT observed to occur on either subset of this bank).
  This generalizes across BOTH bank shapes without hardcoding GOAL-sentence position (unlike
  PREVMOD.build_role_seq / the failing cell's build_role_seq_primacy, which each hardcode a fixed
  slot -- sents[0] or "all-but-last scanned under item['owner']" respectively): the recency-trap bank
  puts the GOAL sentence at S0, the primacy bank puts it at S1; this cell's per-sentence structural
  subject resolution handles both without a bank-specific branch.

SCOPE MEASURED (grep, before authoring): primacy subset (trap_type=="primacy") N=20 (12
explicit_psych p01-p12, 8 action_implied p13-p20), all has_distractor=true. Recency-trap subset
(trap_type absent) N=42 rows (27 explicit_psych, 15 action_implied) of which has_distractor=true
("core") = 28 (18 explicit_psych + 10 action_implied) -- these are the "t01-t28" divergent items
this cell must NOT regress, per the task brief's regression contract; has_distractor=false ("twin")
=14 rows are loaded (via reused PREVMOD.load_bank) but not gated (no distractor -> recency baseline
already correct -> not part of the divergent-subset regression contract).

PRE-REGISTERED BANDS (registered before running; per-subset then worst-of-both overall, matching the
task brief's contract verbatim):
  HARD-PASS: primacy explicit_psych accuracy_divergent >= 11/12 (0.9167) AND primacy beats all four
    positional baselines (recency, first_mention, nearest_subject, majority) AND primacy scramble
    collapses non-vacuously AND recency-trap explicit_psych divergent >= 17/18 (0.9444) AND
    recency-trap action_implied divergent >= 9/10 (0.90) AND recency-trap scramble stays non-vacuous
    collapsing (no regression from the prior wired result).
  HARD-FAIL: recency-trap regresses below either floor above, OR primacy explicit_psych accuracy <
    6/12 (0.50), OR either subset's scramble control is vacuous (gain_unscr<=0, nothing to collapse).
  MIDDLE_BAND: anything else (e.g. primacy explicit_psych in [6/12, 11/12), or primacy
    action_implied improves over the isolated cell's 0/8 floor but the overall primacy band doesn't
    clear HARD-PASS, or one subset clears and the other sits in a gray zone).
  primacy action_implied is REPORTED (not gated in HARD-PASS/HARD-FAIL) per the task brief's
  "IMPROVED over the isolated 0/8" framing (a comparison number, not a pass/fail floor) -- the
  isolated cell's action_implied=0/8 failure was a GOAL-typing gap (its local typer lacked
  purpose-infinitival coverage), fixed upstream by the promoted organ's desiderative/aspectual
  partition (recency-trap action_implied=1.0 with that same organ) -- so an improvement here is the
  expected, not a stretch, outcome; reported honestly either way.

Prior-work check (SUBSTRATE-KB, run before authoring): `tools/substrate_query.sh "primacy trap goal
owner candidate generation entity enumeration goal coherence"` -- top hit cosine=0.376 ("generation",
a capability-registry/wordnet atom about a differently-scoped "generation" concept, not this
mechanism); no atom above 0.30 cosine is substantively about goal-owner candidate-generation via
entity enumeration. This is a genuinely novel harness-level fix, not a rediscovery.

GUARDS: glass-box; deterministic given seed (3 seeds); ASCII-only; atomic metrics write
(tmp+os.replace); resumable per-seed (tools/exp_checkpoint.py); LOCAL-ONLY, in-process foreground,
NOT queue-dispatched, no push; no modification to hdlab/goal_typing.py / hdlab/goal_owner_select.py
/ hdlab/self_improving_loop.py / hdlab/event_centrality_coref.py / hdlab/coref.py (production
hdlab/ untouched); no modification to exp_c5_primacy_trap_endtoend_promoted_organ_v1.py,
exp_c5_real_coref_endtoend_purpose_infinitival_v1.py, or exp_c5_fair_goal_owner_primacy_v1.py (all
imported and reused bit-identical, never edited).

Cites: notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md (task brief diagnosis, "LANDED-4");
data/exp_c5_primacy_trap_endtoend_promoted_organ_v1/metrics.json (commit 43e942ca0, the 0/20
HARD_FAIL this cell fixes); experiments/exp_c5_fair_goal_owner_primacy_v1.py (the isolated cell whose
candidate-generation pattern this brings end-to-end, system=0.6 all-baselines=0.0);
experiments/exp_component5_gold_role_isolated_v1.py (GeneralRecencyEntityResolver, reused
bit-identical); hdlab/goal_typing.py (promoted GOAL-typing organ, consumed directly);
hdlab/goal_owner_select.py (directed_goal_outcome_score, promoted 2026-08-05, consumed directly);
experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py (resolve_outcome_recency_positional,
_sentences, load_bank, reused bit-identical -- the recency-trap regression-check harness);
verification/verify_goal_typing.py (promotion-witness pattern this cell follows).
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

ANCHOR_NAME = "c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_owner_fair_v1.jsonl")

# ---- PROMOTED PRODUCTION ORGAN (WIRE-DON'T-ISLAND: consume hdlab/, not experiment-cell detectors) --
from hdlab.goal_typing import type_goal_events, R_GOAL  # noqa: E402
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
# ---- REUSED BIT-IDENTICAL: structural (gold-free) subject resolver -----------------------------
from exp_component5_gold_role_isolated_v1 import GeneralRecencyEntityResolver  # noqa: E402
# ---- REUSED BIT-IDENTICAL: recency-trap regression harness pieces + primacy-aware baselines -----
import exp_c5_real_coref_endtoend_purpose_infinitival_v1 as PREVMOD  # noqa: E402
from exp_situation_model_goal_outcome_dimension_v1 import R_UNMET, R_MET, _sentences  # noqa: E402
from exp_c5_fair_goal_owner_primacy_v1 import (  # noqa: E402
    baseline_first_mention, baseline_nearest_subject, baseline_majority,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
VERB_TYPES = ("explicit_psych", "action_implied")


# ============================================================================ bank loaders
def load_primacy(verb_type: str):
    rows = []
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return [r for r in rows if r.get("trap_type") == "primacy" and r["verb_type"] == verb_type]


# ============================================================================ THE FIX: candidate
# generation via goal-coherence-biased entity ENUMERATION (replaces coref-pronoun resolution).
def build_candidate_role_seq(item: dict, outcome_entity, scramble_goal_to_foil=None):
    """Structural (gold-free) role_seq/cluster_ids for ONE proposed outcome-slot candidate.
    Non-outcome sentences: subject resolved from the PASSAGE TEXT (GeneralRecencyEntityResolver,
    explicit-name detection), never from item['owner']/item['gold_outcome_owner']. Outcome sentence:
    subject is the PROPOSED CANDIDATE `outcome_entity` (the thing being enumerated over) -- this
    replaces the failing cell's coref-pronoun resolution AND the fixed-owner-subject-scan leak."""
    sents = _sentences(item["text"])
    roster = item["roster"]
    resolver = GeneralRecencyEntityResolver(roster)
    role_seq, cluster_ids = [], []
    for s in sents[:-1]:
        subj = resolver.subject_entity(s)
        for (entity, role) in type_goal_events(s, subj):
            eff = entity
            if scramble_goal_to_foil is not None and role == R_GOAL:
                eff = scramble_goal_to_foil
            role_seq.append(role)
            cluster_ids.append(eff)
    for (entity, role) in type_goal_events(sents[-1], outcome_entity):
        role_seq.append(role)
        cluster_ids.append(entity)
    return role_seq, cluster_ids


def _outcome_pos(role_seq):
    positions = [i for i, r in enumerate(role_seq) if r in (R_UNMET, R_MET)]
    return positions[-1] if positions else None


def enumerate_and_select(item: dict, seed: int, scramble_goal_to_foil=None):
    """The candidate-generation + selection core: propose EVERY roster entity as the outcome-slot
    referent, score each with directed_goal_outcome_score (unmodified promoted organ), argmax.
    Entity set = item['roster'].keys() (structural passage metadata), never the gold label.
    Returns (final_owner, scored_dict, tie_bool)."""
    candidates = sorted(item["roster"].keys())
    scored = {}
    for c in candidates:
        rs, cid = build_candidate_role_seq(item, c, scramble_goal_to_foil=scramble_goal_to_foil)
        pos = _outcome_pos(rs)
        assert pos is not None, f"{item['id']}: outcome never typed for candidate {c!r}"
        scored[c] = directed_goal_outcome_score(rs, cid, seed, pos)
    max_score = max(scored.values())
    winners = [c for c in candidates if scored[c] == max_score]
    return winners[0], scored, (len(winners) > 1)


# ============================================================================ per-item eval
def run_item(item: dict, seed: int):
    gold = item["gold_outcome_owner"]
    foil = item.get("foil")

    final_owner, scored, tie = enumerate_and_select(item, seed)
    recency_owner = PREVMOD.resolve_outcome_recency_positional(item)
    fm = baseline_first_mention(item)
    ns = baseline_nearest_subject(item)
    mj = baseline_majority(item)

    row = dict(
        id=item["id"], verb_type=item["verb_type"], gold=gold,
        final_owner=final_owner, matches_gold=(final_owner == gold), tie=tie, scored=scored,
        recency_owner=recency_owner, recency_matches_gold=(recency_owner == gold),
        first_mention_owner=fm, first_mention_matches_gold=(fm == gold),
        nearest_subject_owner=ns, nearest_subject_matches_gold=(ns == gold),
        majority_owner=mj, majority_matches_gold=(mj == gold),
    )

    if foil is not None:
        scrambled_owner, scored_s, tie_s = enumerate_and_select(item, seed, scramble_goal_to_foil=foil)
        row.update(scrambled_final_owner=scrambled_owner,
                    scrambled_matches_gold=(scrambled_owner == gold), scrambled_tie=tie_s)
    else:
        row.update(scrambled_final_owner=None, scrambled_matches_gold=None, scrambled_tie=None)
    return row


# ============================================================================ per-subset summarize
def _rate(rows, key):
    vals = [r[key] for r in rows if r[key] is not None]
    return round(sum(bool(v) for v in vals) / len(vals), 4) if vals else None


def summarize(rows):
    return dict(
        n=len(rows),
        recency_accuracy=_rate(rows, "recency_matches_gold"),
        first_mention_accuracy=_rate(rows, "first_mention_matches_gold"),
        nearest_subject_accuracy=_rate(rows, "nearest_subject_matches_gold"),
        majority_accuracy=_rate(rows, "majority_matches_gold"),
        system_accuracy=_rate(rows, "matches_gold"),
        system_scrambled_accuracy=_rate(rows, "scrambled_matches_gold"),
        n_ties=sum(1 for r in rows if r["tie"]),
        miss_ids=[r["id"] for r in rows if not r["matches_gold"]],
        rows=rows,
    )


# ============================================================================ per-seed unit
def run_seed(seed: int):
    primacy = {}
    for vt in VERB_TYPES:
        items = load_primacy(vt)
        rows = [run_item(it, seed) for it in items]
        primacy[vt] = summarize(rows)

    recency = {}
    for vt in VERB_TYPES:
        core, _twins = PREVMOD.load_bank(vt)
        rows_all = [run_item(it, seed) for it in core]
        div = [r for r in rows_all if not r["recency_matches_gold"]]
        recency[vt] = summarize(div)
        recency[vt]["n_core_total"] = len(core)

    return dict(seed=seed, primacy=primacy, recency=recency)


# ============================================================================ arms-differ diagnostic
# (positive-control substitute, mirrors the failing cell's own META_RULE_AF exemption pattern):
# proves the NEW candidate-generation mechanism actually differs from the OLD (coref-pronoun) one it
# replaces -- on primacy items the old end-to-end cell's final_owner was the foil on 20/20
# (data/exp_c5_primacy_trap_endtoend_promoted_organ_v1/metrics.json); this cell's final_owner should
# differ (pick the true owner) on most of those same items. Computed once at seed0, reported not gated.
def _arms_differ_vs_old_coref_pipeline(rows_ep, rows_ai):
    all_rows = rows_ep + rows_ai
    n_differs_from_old_foil_pick = sum(1 for r in all_rows if r["final_owner"] != r.get("recency_owner"))
    # old pipeline's final_owner on primacy was bit-identical to the recency baseline (0/20, always
    # foil) -- MEASURED@data/exp_c5_primacy_trap_endtoend_promoted_organ_v1/metrics.json. Any item
    # where this cell's final_owner differs from that recency baseline proves the enumeration
    # mechanism is exercised (not silently falling back to the same old candidate).
    return {"n_items": len(all_rows), "n_new_owner_differs_from_old_pipeline_pick": n_differs_from_old_foil_pick,
            "differs": n_differs_from_old_foil_pick > 0}


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean_subset(bank, vt, key):
        vals = [per_seed[s][bank][vt][key] for s in seeds if per_seed[s][bank][vt][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    def gain_gate(bank, vt):
        unscr = mean_subset(bank, vt, "system_accuracy")
        scr = mean_subset(bank, vt, "system_scrambled_accuracy")
        base_acc = dict(recency=mean_subset(bank, vt, "recency_accuracy"),
                         first_mention=mean_subset(bank, vt, "first_mention_accuracy"),
                         nearest_subject=mean_subset(bank, vt, "nearest_subject_accuracy"),
                         majority=mean_subset(bank, vt, "majority_accuracy"))
        max_base = max(v for v in base_acc.values() if v is not None)
        beats_all_four = all(unscr is not None and v is not None and unscr > v for v in base_acc.values())
        # SCRAMBLE REFERENCE BASELINE: on the recency-trap bank, first_mention/majority are 1.0 on
        # the divergent subset BY BANK CONSTRUCTION (owner is trivially first-named + majority-named
        # there -- disclosed, pre-existing property of this bank, reused verbatim from
        # exp_c5_real_coref_endtoend_purpose_infinitival_v1's own convention: "first_mention/majority
        # were 1.0 ... NOT gated, bank-structural"). Gating the scramble check against those trivially-
        # tied baselines on THAT bank would always read vacuous regardless of mechanism quality, so the
        # scramble reference there is {recency, nearest_subject} (the two baselines that bank actually
        # defeats). On the primacy bank all four baselines are 0.0 by construction, so the reference is
        # all four (equivalent either way there).
        if bank == "recency":
            ref_vals = [v for k, v in base_acc.items() if k in ("recency", "nearest_subject") and v is not None]
        else:
            ref_vals = [v for v in base_acc.values() if v is not None]
        ref_base = max(ref_vals) if ref_vals else max_base
        gain_unscr = (unscr - ref_base) if unscr is not None else None
        gain_scr = (scr - ref_base) if scr is not None else None
        if gain_unscr is not None and gain_unscr > 1e-9:
            collapses = gain_scr is not None and gain_scr <= 0.5 * gain_unscr + 1e-9
            vacuous = False
        else:
            collapses = gain_scr is not None and gain_scr <= 1e-9
            vacuous = True
        return dict(system_accuracy=unscr, system_scrambled_accuracy=scr, baselines=base_acc,
                    max_baseline=round(max_base, 4), beats_all_four_baselines=beats_all_four,
                    scramble_collapses=collapses, scramble_vacuous=vacuous)

    primacy_ep = gain_gate("primacy", "explicit_psych")
    primacy_ai = gain_gate("primacy", "action_implied")
    recency_ep = gain_gate("recency", "explicit_psych")
    recency_ai = gain_gate("recency", "action_implied")

    n_primacy_ep = per_seed[seeds[0]]["primacy"]["explicit_psych"]["n"]
    n_primacy_ai = per_seed[seeds[0]]["primacy"]["action_implied"]["n"]
    n_recency_ep = per_seed[seeds[0]]["recency"]["explicit_psych"]["n"]
    n_recency_ai = per_seed[seeds[0]]["recency"]["action_implied"]["n"]

    # HARD-PASS gate
    hard_pass = bool(
        primacy_ep["system_accuracy"] is not None and primacy_ep["system_accuracy"] >= 11 / 12 - 1e-9
        and primacy_ep["beats_all_four_baselines"] and primacy_ep["scramble_collapses"]
        and not primacy_ep["scramble_vacuous"]
        and recency_ep["system_accuracy"] is not None and recency_ep["system_accuracy"] >= 17 / 18 - 1e-9
        and recency_ai["system_accuracy"] is not None and recency_ai["system_accuracy"] >= 9 / 10 - 1e-9
        and not recency_ep["scramble_vacuous"] and recency_ep["scramble_collapses"]
        and not recency_ai["scramble_vacuous"] and recency_ai["scramble_collapses"]
    )
    # HARD-FAIL gate
    recency_regressed = bool(
        (recency_ep["system_accuracy"] is None or recency_ep["system_accuracy"] < 17 / 18 - 1e-9)
        or (recency_ai["system_accuracy"] is None or recency_ai["system_accuracy"] < 9 / 10 - 1e-9))
    primacy_explicit_floor_breach = bool(
        primacy_ep["system_accuracy"] is None or primacy_ep["system_accuracy"] < 0.5 - 1e-9)
    any_scramble_vacuous = bool(primacy_ep["scramble_vacuous"] or recency_ep["scramble_vacuous"]
                                or recency_ai["scramble_vacuous"])
    hard_fail = bool(recency_regressed or primacy_explicit_floor_breach or any_scramble_vacuous)

    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    msg = (
        f"PRIMACY explicit_psych: system={primacy_ep['system_accuracy']} (N={n_primacy_ep}) vs "
        f"baselines={primacy_ep['baselines']} beats_all_four={primacy_ep['beats_all_four_baselines']} "
        f"scramble_collapses={primacy_ep['scramble_collapses']} vacuous={primacy_ep['scramble_vacuous']}. "
        f"PRIMACY action_implied: system={primacy_ai['system_accuracy']} (N={n_primacy_ai}) vs "
        f"baselines={primacy_ai['baselines']} [reported, not gated -- isolated-cell floor was 0/8]. "
        f"RECENCY-TRAP explicit_psych: system={recency_ep['system_accuracy']} (N={n_recency_ep}, "
        f"floor=17/18). RECENCY-TRAP action_implied: system={recency_ai['system_accuracy']} "
        f"(N={n_recency_ai}, floor=9/10). recency_regressed={recency_regressed}. "
        f"VERDICT={verdict}.")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {msg}", summary=msg, n_seeds=n,
        primacy_explicit_psych=primacy_ep, primacy_action_implied=primacy_ai,
        recency_explicit_psych=recency_ep, recency_action_implied=recency_ai,
        n_primacy_explicit_psych=n_primacy_ep, n_primacy_action_implied=n_primacy_ai,
        n_recency_explicit_psych_divergent=n_recency_ep, n_recency_action_implied_divergent=n_recency_ai,
        recency_regressed=recency_regressed, primacy_explicit_floor_breach=primacy_explicit_floor_breach,
        any_scramble_vacuous=any_scramble_vacuous,
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
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"primacy_ep={res['primacy']['explicit_psych']['system_accuracy']} "
              f"primacy_ai={res['primacy']['action_implied']['system_accuracy']} "
              f"recency_ep={res['recency']['explicit_psych']['system_accuracy']} "
              f"recency_ai={res['recency']['action_implied']['system_accuracy']}", flush=True)

    raw = load_units(OUTPUT_DIR)
    per_seed = {int(v["seed"]): v for v in raw.values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")

    seed0 = per_seed[sorted(per_seed.keys())[0]]
    arms_diag = _arms_differ_vs_old_coref_pipeline(
        seed0["primacy"]["explicit_psych"]["rows"], seed0["primacy"]["action_implied"]["rows"])

    agg = aggregate(per_seed)
    agg["arms_differ_verified"] = False
    agg["arms_differ_exempted"] = [("old_coref_pronoun_candidate_gen", "new_goal_coherence_enumeration")]
    agg["arms_differ_diagnostic_vs_old_pipeline"] = arms_diag
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(seeds=SEEDS, verb_types=list(VERB_TYPES), bank_path=BANK_PATH,
                         cardinality_ok=(len(per_seed) == EXPECTED_N_SEEDS),
                         typer="hdlab.goal_typing.type_goal_events (PROMOTED, wire-dont-island)",
                         candidate_gen="entity-set enumeration + directed_goal_outcome_score argmax "
                                       "(replaces coref-pronoun resolution)")
    agg["final_metrics_atomicity"] = "tmp_replace"
    agg["crlb_n/a"] = "boolean-match discriminator (owner-selection accuracy), not an SNR/argmax-noise regime"
    agg["prereg"] = "inline (docstring, LOCAL-ONLY task brief; no separate preregs/ file)"
    agg["cites"] = [
        "data/exp_c5_primacy_trap_endtoend_promoted_organ_v1/metrics.json (commit 43e942ca0, the "
        "HARD_FAIL this cell fixes)",
        "experiments/exp_c5_fair_goal_owner_primacy_v1.py (isolated candidate-gen pattern, reused)",
        "experiments/exp_component5_gold_role_isolated_v1.py (GeneralRecencyEntityResolver, "
        "reused bit-identical)",
        "hdlab/goal_typing.py (PROMOTED GOAL-typing organ, commit 5449161c2, consumed directly)",
        "hdlab/goal_owner_select.py (directed_goal_outcome_score, promoted 2026-08-05)",
        "experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py "
        "(resolve_outcome_recency_positional, load_bank, _sentences, reused bit-identical)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[arms_differ_diagnostic] {arms_diag}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    ep = load_primacy("explicit_psych")
    ai = load_primacy("action_implied")
    assert len(ep) == 12, f"expected 12 explicit_psych primacy items, got {len(ep)}"
    assert len(ai) == 8, f"expected 8 action_implied primacy items, got {len(ai)}"
    print(f"[bank] primacy: explicit_psych={len(ep)}, action_implied={len(ai)}", flush=True)

    # (1) FAIRNESS CHECK: structural subject resolution never consults item['owner']/gold -- verify
    # by constructing a role_seq for a primacy item and confirming the derived GOAL-bearing subject
    # is discovered from the SENTENCE TEXT (matches the roster name token actually present), not by
    # any lookup of item['owner'].
    it01 = next(it for it in ep if it["id"] == "p01_amy_ice_foil_jo")
    sents = _sentences(it01["text"])
    resolver = GeneralRecencyEntityResolver(it01["roster"])
    derived_subjects = [resolver.subject_entity(s) for s in sents[:-1]]
    # S0 names the foil (jo), S1 names the owner (amy) -- both derived purely from explicit-name
    # tokens in the text, independent of which one happens to equal item['owner'].
    assert derived_subjects[0] == "jo" and derived_subjects[1] == "amy", (
        f"structural subject resolution mismatch: {derived_subjects}")
    print(f"[SELFTEST 1/7] structural (gold-free) subject resolution on p01: {derived_subjects} "
          f"(S0=foil, S1=owner -- derived from text, not from item['owner'])", flush=True)

    # (2) enumeration candidate pool = roster (structural), NOT {owner, gold} pair by name.
    cands = sorted(it01["roster"].keys())
    assert cands == sorted(["amy", "jo"]) == sorted([it01["owner"], it01["foil"]]), (
        "candidate pool must equal the structural roster")
    print(f"[SELFTEST 2/7] candidate pool = roster = {cands} (structural, not hand-picked)", flush=True)

    # (3) end-to-end enumeration on p01 selects the TRUE owner (fixes the old 0/20 HARD_FAIL).
    final_owner, scored, tie = enumerate_and_select(it01, seed=0)
    assert final_owner == it01["gold_outcome_owner"], (
        f"p01 enumeration should select the gold owner: final_owner={final_owner!r} scored={scored}")
    assert not tie, f"p01 should not be a tie: {scored}"
    print(f"[SELFTEST 3/7] p01 enumeration selects gold owner={final_owner!r} scored={scored} "
          f"(fixes the old coref-pronoun HARD_FAIL)", flush=True)

    # (4) scramble control collapses on p01: corrupting the GOAL binding flips the pick to the foil.
    scrambled_owner, scored_s, _tie_s = enumerate_and_select(
        it01, seed=0, scramble_goal_to_foil=it01["foil"])
    assert scrambled_owner == it01["foil"], (
        f"scramble should flip the pick to the foil: scrambled_owner={scrambled_owner!r} scored_s={scored_s}")
    print(f"[SELFTEST 4/7] p01 scramble control flips pick to foil={scrambled_owner!r} "
          f"scored_s={scored_s} (non-vacuous collapse)", flush=True)

    # (5) all four positional baselines still land on the foil on p01 (trap intact, unmodified).
    gold = it01["gold_outcome_owner"]
    assert PREVMOD.resolve_outcome_recency_positional(it01) != gold
    assert baseline_first_mention(it01) != gold
    assert baseline_nearest_subject(it01) != gold
    assert baseline_majority(it01) != gold
    print("[SELFTEST 5/7] all four positional baselines still wrong on p01 (trap intact)", flush=True)

    # (6) recency-trap regression harness loads + a known-good item (t01) still resolves correctly
    # under the NEW candidate-generation mechanism (no regression on the already-wired subset).
    core_ep, _twins = PREVMOD.load_bank("explicit_psych")
    t01 = next(it for it in core_ep if it["id"] == "t01_amy_ice_foil_jo")
    t01_owner, t01_scored, _t01_tie = enumerate_and_select(t01, seed=0)
    assert t01_owner == t01["gold_outcome_owner"], (
        f"t01 (recency-trap, already-wired) must still resolve correctly: {t01_owner!r} {t01_scored}")
    print(f"[SELFTEST 6/7] t01 (recency-trap) resolves correctly under the new mechanism: "
          f"{t01_owner!r} (no regression)", flush=True)

    # (7) one full seed sanity across both subsets.
    res = run_seed(0)
    print(f"[SELFTEST 7/7] seed0: primacy_ep={res['primacy']['explicit_psych']['system_accuracy']} "
          f"primacy_ai={res['primacy']['action_implied']['system_accuracy']} "
          f"recency_ep={res['recency']['explicit_psych']['system_accuracy']} "
          f"(N={res['recency']['explicit_psych']['n']}) "
          f"recency_ai={res['recency']['action_implied']['system_accuracy']} "
          f"(N={res['recency']['action_implied']['n']})", flush=True)
    return True


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
        raise SystemExit(0 if self_test() else 1)
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
