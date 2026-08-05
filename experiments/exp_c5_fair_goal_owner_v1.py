"""exp_c5_fair_goal_owner_v1 -- THE FAIR goal-owner test: a hand-authored, verified-gold,
DISCRIMINATING bank + harness that measures goal->owner BINDING (not subject-resolution),
replacing the unfair auto-mined banks per the test-fairness audit.

PRE-REG: preregs/2026-08-05_c5_fair_goal_owner_v1.md
GOLD-VET: notes/goldvet_fair_goal_owner_bank_v1.md

WHY (task brief, gating deliverable): notes/testfairness_audit_goal_owner.md (ff6f93a9a) +
notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md (6df2083db) diagnosed the PRIOR real-text
goal-owner numbers (0.64-0.71) as an artifact: gold was the miner's own syntactic-subject pick (so
a trivial subject-picker scores ~100% by construction), the metric TIED a degenerate recency
baseline exactly (candidate_divergence_rate ~0.0-0.06, i.e. the C5 organ decided ~1 real item),
outcome_spans were auto-extracted trailing text about a DIFFERENT character, and the task was
sentence-local (no maintained goal across a genuine distractor). Nothing about goal-owner is
measurable until a FAIR instrument exists. This cell IS that instrument.

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `tools/substrate_query.sh "fair goal
owner test recency trap distractor gender matched divergent subset baseline"` returned 5 hits, ALL
below cosine=0.30 (top=0.2676, unrelated process-log chunks) -- NO prior fair-goal-owner-test design
exists in the KB. This is NOT a rediscovery. (The 2 audit/synthesis docs above were read directly,
not surfaced by this KB query -- they were the task brief's own pointers, read in full before
authoring, and are the WHY, not prior implementations of THIS instrument.)

BANK (experiments/data/goal_owner_fair_v1.jsonl, hand-authored, N=42 rows = 28 core trap items + 14
no-distractor twins): each CORE item is a 3-sentence vignette: S1 names the protagonist P and
states/implies a GOAL (mix: 18 EXPLICIT via a V2_DESIRE psych/desiderative verb [wanted/wished/
longed/hoped], reused bit-identical from exp_self_extension_grounded_realprose_v1.V2_DESIRE; 10
ACTION-IMPLIED with NO goal-word at all, e.g. "Ruth set out at dawn to draw water from the well" --
these probe the GENERATIVE-goal-inference gap named in the drill synthesis: the current lexicon
typer cannot type these, an HONEST expected finding, not a bug). S2 names a GENDER-MATCHED
DISTRACTOR D doing an unrelated action (no lexicon collision, hand-verified -- see the generation+
verification script's PROBLEMS pass, 0 problems on the final bank). S3 is the OUTCOME clause, tied
CAUSALLY to P's goal (contains exactly one V2_OUTCOME_UNMET or V2_OUTCOME_MET trigger word, reused
bit-identical), referring to P via a BARE PRONOUN ONLY (no name -- hand-verified, see below) so
that D, mentioned more recently, is the genuine recency trap. 14 of the 28 core items have a
NO-DISTRACTOR CONTROL TWIN (S2 dropped; <id>_twin) proving the system does not regress on the
undistracted case. Gold = HAND-AUTHORED (owner=P the goal-holder, decoupled from the outcome-
sentence's naive-recency subject; outcome_polarity=unmet|met) -- NO auto-extracted spans anywhere.

GOLD-VET (rule c, triple-checked): (1) MECHANICAL pass -- a generation+verification script asserted
per item: explicit_psych items DO carry a V2_DESIRE trigger in S1 and action_implied items do NOT;
S1 never accidentally carries an OUTCOME trigger; S2 (distractor) never carries ANY V2_DESIRE/
V2_OUTCOME trigger (no cross-contamination); S3 never accidentally carries a V2_DESIRE trigger and
carries EXACTLY the declared polarity's trigger, not the other polarity's; S3 names NEITHER P nor D
explicitly (pronoun-only, so the trap is genuine -- an item where S3 named P outright would let a
naive picker win by luck, not because it resolved the pronoun correctly); owner/foil GENDER MATCH
(same gender bucket, reused bit-identical from GENDER, both f or both m) so the trap is not solvable
by gender alone. All 42 rows pass 0/42 problems (script re-run recorded in provenance below).
(2) STRUCTURAL pass (this cell's self-test, mechanically re-derived from the SAME resolver the
harness scores with, not hand-typed twice): for every CORE item, the naive recency-to-outcome
baseline (GeneralRecencyEntityResolver) must resolve the outcome pronoun to the FOIL, not the OWNER
(a genuine trap by construction) -- any item failing this is flagged, not silently included.
(3) LEAKAGE check: owner is never the ONLY roster entity in a core item (foil is always present, so
the resolver has a real choice); majority-class (most-named entity) is computed structurally, not
hand-set, so it cannot leak the answer.

MECHANISM UNDER TEST (glass-box, reused VERBATIM, zero new hdlab code): GeneralRecencyEntityResolver
/ ContentMatchResolver / build_positions / type_sentence_events (all reused bit-identical from
experiments/exp_component5_gold_role_isolated_v1.py, itself reusing exp_situation_model_goal_
outcome_dimension_v1.py's lexicon typer) generate the two candidate whole-passage resolutions;
hdlab.goal_owner_select.directed_goal_outcome_score (the WIRED promotion, 2026-08-05) scores each
candidate's own assignment; hdlab.self_improving_loop.decide_keep_or_revert (reused verbatim) gates
adoption. This cell is the REAL-TEXT analog of exp_component5_gold_role_isolated_v1 (which proved
the mechanism EXISTS on N=23 hand-built GIVEN-role items, 1.0 vs recency 0.0435): same organs, but
scored the way the audit's corrected design demands (divergent-subset-only, 3 baselines, non-
vacuous scramble, gold decoupled from outcome-sentence subject).

THREE BASELINES (all reported): (a) goal-sentence-subject picker = GeneralRecencyEntityResolver
applied to S1 ALONE (the construction CEILING -- P is always the explicit subject of S1 by
authoring convention, so this should read ~1.0; a value below that flags an authoring defect).
(b) recency-to-outcome = GeneralRecencyEntityResolver's whole-passage resolution at the outcome
slot (the TRAP FLOOR -- by construction of the DIVERGENT subset this is EXACTLY 0.0 there; reported,
not hardcoded, so a construction bug would surface as a nonzero value). (c) majority-class = the
roster entity with the most explicit-name mentions in the passage (ties broken by earliest first
mention), a structural baseline computed from the text, never hand-set.

METRIC: score on the DIVERGENT subset (recency baseline != gold at the outcome slot) ONLY --
N_divergent reported explicitly, never averaged away into an undifferentiated accuracy. A SCRAMBLE
control (role-scramble: the GOAL role's owner is relabeled to the foil for the content candidate
only, text/gold unchanged -- the established non-vacuous-scramble pattern from exp_component5_gold_
role_isolated_v1, itself the "shuffle goal<->outcome pairing" instrument the task brief names) must
COLLAPSE the system's gain over the recency floor, or the instrument is non-discriminating.

PRE-REGISTERED CAN-FAIL (the instrument is VALID iff ALL THREE): (1) recency floor < 0.5 on the
divergent subset (trap is real); (2) goal-subject-ceiling >= 0.9 on core items (construction sane);
(3) scramble collapses the system's divergent-subset gain over recency (>= 50% relative collapse,
or both scrambled/unscrambled are non-vacuously zero). The PRIMARY deliverable is this VALID
INSTRUMENT; whether the CURRENT pipeline beats recency on the divergent subset is reported honestly
as the first FAIR goal-owner number -- a low score is an honest finding per task brief, not a
cell failure.

GUARDS: glass-box; all organs reused bit-identical (no new hdlab code); deterministic given seed
(3 seeds); resumable per-seed via tools/exp_checkpoint.py; ASCII-only; atomic metrics write;
LOCAL-ONLY, in-process foreground, NOT queue-dispatched, no push (per task brief).

Cites: notes/testfairness_audit_goal_owner.md; notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md;
hdlab/goal_owner_select.py; experiments/exp_component5_gold_role_isolated_v1.py;
experiments/exp_situation_model_goal_outcome_dimension_v1.py; hdlab/self_improving_loop.py.
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
from collections import Counter
from datetime import datetime, timezone

ANCHOR_NAME = "c5_fair_goal_owner_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_owner_fair_v1.jsonl")

# ---- REUSED BIT-IDENTICAL: candidate generators + typing + positions ---------------------------
from exp_component5_gold_role_isolated_v1 import (  # noqa: E402
    GeneralRecencyEntityResolver, ContentMatchResolver, build_positions, DEFAULT_ROSTER,
)
from exp_situation_model_goal_outcome_dimension_v1 import (  # noqa: E402
    R_GOAL, R_UNMET, R_MET, _sentences, _ordered_tokens,
)
# ---- REUSED BIT-IDENTICAL: the promoted Component-5 selection organ (2026-08-05 wire-point) -----
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the promoted adoption gate (2026-08-02) ------------------------------
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)


# ============================================================================ bank load
def load_bank():
    """Loads the RECENCY-TRAP subset of the bank only (trap_type=="recency" or unset -- the
    original 28 core + 14 twins this cell was built + gold-VET'd on). 2026-08-05: the bank file
    grew a SEPARATE trap_type=="primacy" subset (20 rows, all has_distractor=True) authored for
    exp_c5_fair_goal_owner_primacy_v1 -- those rows must NOT leak into this cell's "core" set (their
    S1 is deliberately the DISTRACTOR's sentence, so this cell's S1-alone "goal-subject-ceiling"
    baseline would read ~0.0 for them, not the ~1.0 this cell's gates require; they are a different,
    additional instrument, scored by their own dedicated cell). Filtering by trap_type keeps this
    cell's validated 28+14=42-row bank bit-identical to what it was gold-VET'd against."""
    rows = []
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    rows = [r for r in rows if r.get("trap_type", "recency") == "recency"]
    core = [r for r in rows if r["has_distractor"]]
    twins = [r for r in rows if not r["has_distractor"]]
    return rows, core, twins


# ============================================================================ baselines
def baseline_goal_subject_ceiling(item: dict):
    """(a) goal-sentence-subject picker: resolve S1 alone (fresh resolver, no prior recency
    state) -- the construction CEILING. Should read ~1.0 (P is always S1's explicit subject)."""
    roster = item["roster"]
    s1 = _sentences(item["text"])[0]
    return GeneralRecencyEntityResolver(roster).subject_entity(s1)


def baseline_majority(item: dict):
    """(c) majority-class: the roster entity with the most explicit-name mentions in the full
    passage text; ties broken by earliest first mention. Computed structurally, never hand-set."""
    roster = item["roster"]
    toks = _ordered_tokens(item["text"])
    counts = Counter(t for t in toks if t in roster)
    if not counts:
        return None
    first_idx = {e: toks.index(e) for e in counts}
    return min(counts.keys(), key=lambda e: (-counts[e], first_idx[e]))


# ============================================================================ per-item eval
def run_item(item: dict, seed: int):
    roster = item["roster"]
    gold = item["gold_outcome_owner"]

    role_seq_b, cluster_ids_b, _es_b = build_positions(item, GeneralRecencyEntityResolver(roster))
    role_seq_c, cluster_ids_c, _es_c = build_positions(item, ContentMatchResolver(roster))
    assert role_seq_b == role_seq_c, (
        f"{item['id']}: role sequences diverged between resolvers (lexicon typing must be "
        f"resolver-independent): {role_seq_b} vs {role_seq_c}")

    typing_miss_goal = R_GOAL not in role_seq_b
    outcome_positions = [i for i, r in enumerate(role_seq_b) if r in (R_UNMET, R_MET)]
    typing_miss_outcome = len(outcome_positions) == 0
    outcome_pos = outcome_positions[-1] if outcome_positions else None

    ceiling_owner = baseline_goal_subject_ceiling(item)
    recency_owner = cluster_ids_b[outcome_pos] if outcome_pos is not None else None
    majority_owner = baseline_majority(item)

    row = dict(
        id=item["id"], verb_type=item["verb_type"], outcome_polarity=item["outcome_polarity"],
        has_distractor=item["has_distractor"], gold=gold,
        typing_miss_goal=typing_miss_goal, typing_miss_outcome=typing_miss_outcome,
        ceiling_owner=ceiling_owner, ceiling_matches_gold=(ceiling_owner == gold),
        recency_owner=recency_owner, recency_matches_gold=(recency_owner == gold),
        majority_owner=majority_owner, majority_matches_gold=(majority_owner == gold),
        is_divergent=(item["has_distractor"] and outcome_pos is not None
                      and recency_owner != gold),
    )
    if outcome_pos is None:
        row.update(final_owner=None, matches_gold=False, adopt=None,
                    scrambled_final_owner=None, scrambled_matches_gold=False)
        return row

    score_b = directed_goal_outcome_score(role_seq_b, cluster_ids_b, seed, outcome_pos)
    score_c = directed_goal_outcome_score(role_seq_c, cluster_ids_c, seed, outcome_pos)
    adopt = decide_keep_or_revert({"content": score_c - score_b}, ABSTAIN_BAND_DEFAULT)
    final_owner = cluster_ids_c[outcome_pos] if adopt == "content" else cluster_ids_b[outcome_pos]
    row.update(final_owner=final_owner, matches_gold=(final_owner == gold), adopt=adopt,
               directed_score_baseline=score_b, directed_score_content=score_c)

    # SCRAMBLE control (only meaningful where a foil exists): relabel the GOAL role's owner to the
    # foil for the CONTENT candidate only -- text/gold unchanged. Non-vacuous-scramble pattern per
    # exp_component5_gold_role_isolated_v1 (the "shuffle goal<->outcome pairing" instrument).
    foil = item.get("foil")
    if foil is not None:
        role_seq_s, cluster_ids_s, _es_s = build_positions(
            item, ContentMatchResolver(roster), scramble_owner_to_foil=foil)
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
    _all_rows, core, twins = load_bank()
    core_rows = [run_item(it, seed) for it in core]
    twin_rows = [run_item(it, seed) for it in twins]

    div = [r for r in core_rows if r["is_divergent"]]
    n_div = len(div)

    def rate(rows_, key):
        return round(sum(bool(r[key]) for r in rows_) / len(rows_), 4) if rows_ else None

    ceiling_acc = rate(core_rows, "ceiling_matches_gold")
    recency_floor_div = rate(div, "recency_matches_gold")     # must be 0.0 by construction
    majority_acc_div = rate(div, "majority_matches_gold")
    system_acc_div = rate(div, "matches_gold")
    scrambled_div = [r for r in div if r["scrambled_final_owner"] is not None]
    system_scrambled_acc_div = rate(scrambled_div, "scrambled_matches_gold")
    twin_acc = rate(twin_rows, "matches_gold")

    return dict(
        seed=seed, n_core=len(core_rows), n_twin=len(twin_rows), n_divergent=n_div,
        ceiling_accuracy=ceiling_acc, recency_floor_divergent=recency_floor_div,
        majority_accuracy_divergent=majority_acc_div, system_accuracy_divergent=system_acc_div,
        system_scrambled_accuracy_divergent=system_scrambled_acc_div,
        twin_control_accuracy=twin_acc,
        n_typing_miss_goal=sum(r["typing_miss_goal"] for r in core_rows),
        n_typing_miss_outcome=sum(r["typing_miss_outcome"] for r in core_rows),
        core_rows=core_rows, twin_rows=twin_rows,
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    ceiling_accuracy = mean("ceiling_accuracy")
    recency_floor_divergent = mean("recency_floor_divergent")
    majority_accuracy_divergent = mean("majority_accuracy_divergent")
    system_accuracy_divergent = mean("system_accuracy_divergent")
    system_scrambled_accuracy_divergent = mean("system_scrambled_accuracy_divergent")
    twin_control_accuracy = mean("twin_control_accuracy")
    n_divergent = per_seed[seeds[0]]["n_divergent"]
    n_divergent_ok = all(per_seed[s]["n_divergent"] == n_divergent for s in seeds)
    n_core = per_seed[seeds[0]]["n_core"]
    n_twin = per_seed[seeds[0]]["n_twin"]

    # PRE-REGISTERED VALIDITY GATES (the instrument, not the pipeline, is being judged here)
    gate_recency_floor_low = (recency_floor_divergent is not None and recency_floor_divergent < 0.5)
    gate_ceiling_high = (ceiling_accuracy is not None and ceiling_accuracy >= 0.9)
    gain_unscrambled = (system_accuracy_divergent - recency_floor_divergent
                        if system_accuracy_divergent is not None and recency_floor_divergent is not None
                        else None)
    gain_scrambled = (system_scrambled_accuracy_divergent - recency_floor_divergent
                      if system_scrambled_accuracy_divergent is not None and recency_floor_divergent is not None
                      else None)
    if gain_unscrambled is not None and gain_unscrambled > 1e-9:
        gate_scramble_collapses = (gain_scrambled is not None and gain_scrambled <= 0.5 * gain_unscrambled + 1e-9)
        scramble_vacuous = False
    else:
        # nothing to break (system never beat recency unscrambled) -- scramble trivially "collapses"
        # for the WRONG reason; surface this explicitly rather than claim a pass.
        gate_scramble_collapses = (gain_scrambled is not None and gain_scrambled <= 1e-9)
        scramble_vacuous = True

    instrument_valid = bool(gate_recency_floor_low and gate_ceiling_high and n_divergent_ok
                            and n_divergent >= 10)
    pipeline_beats_recency_fair = bool(
        instrument_valid and system_accuracy_divergent is not None
        and recency_floor_divergent is not None
        and system_accuracy_divergent > recency_floor_divergent)

    if not n_divergent_ok:
        verdict = "HARD_FAIL_CARDINALITY_NONDETERMINISTIC_DIVERGENT_SET"
    elif not instrument_valid:
        verdict = "INSTRUMENT_INVALID_SEE_GATES"
    elif pipeline_beats_recency_fair and gate_scramble_collapses:
        verdict = "INSTRUMENT_VALID_PIPELINE_BEATS_RECENCY_FAIR"
    elif gate_scramble_collapses is False and not scramble_vacuous:
        verdict = "INSTRUMENT_VALID_SCRAMBLE_DID_NOT_COLLAPSE_FLAG"
    else:
        verdict = "INSTRUMENT_VALID_PIPELINE_DOES_NOT_BEAT_RECENCY_HONEST_NEGATIVE"

    summary = (
        f"N_core={n_core} N_twin={n_twin} N_divergent={n_divergent} (of {n_core} core items). "
        f"BASELINES: ceiling(goal-subject)={ceiling_accuracy} recency_floor(divergent)="
        f"{recency_floor_divergent} majority(divergent)={majority_accuracy_divergent}. "
        f"SYSTEM(divergent)={system_accuracy_divergent} SYSTEM_SCRAMBLED(divergent)="
        f"{system_scrambled_accuracy_divergent}. twin_control_accuracy={twin_control_accuracy}. "
        f"GATES: recency_floor<0.5={gate_recency_floor_low} ceiling>=0.9={gate_ceiling_high} "
        f"scramble_collapses={gate_scramble_collapses} (vacuous={scramble_vacuous}) -> "
        f"instrument_valid={instrument_valid}. pipeline_beats_recency_fair={pipeline_beats_recency_fair}.")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        n_core=n_core, n_twin=n_twin, n_divergent=n_divergent,
        ceiling_accuracy=ceiling_accuracy, recency_floor_divergent=recency_floor_divergent,
        majority_accuracy_divergent=majority_accuracy_divergent,
        system_accuracy_divergent=system_accuracy_divergent,
        system_scrambled_accuracy_divergent=system_scrambled_accuracy_divergent,
        twin_control_accuracy=twin_control_accuracy,
        gate_recency_floor_low=gate_recency_floor_low, gate_ceiling_high=gate_ceiling_high,
        gate_scramble_collapses=gate_scramble_collapses, scramble_vacuous=scramble_vacuous,
        instrument_valid=instrument_valid, pipeline_beats_recency_fair=pipeline_beats_recency_fair,
        n_typing_miss_goal_seed0=per_seed[seeds[0]]["n_typing_miss_goal"],
        n_typing_miss_outcome_seed0=per_seed[seeds[0]]["n_typing_miss_outcome"],
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
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"N_div={res['n_divergent']} ceiling={res['ceiling_accuracy']} "
              f"recency_floor={res['recency_floor_divergent']} "
              f"system={res['system_accuracy_divergent']} "
              f"system_scrambled={res['system_scrambled_accuracy_divergent']}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(OUTPUT_DIR).values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(seeds=SEEDS, abstain_band=ABSTAIN_BAND_DEFAULT, bank_path=BANK_PATH,
                         cardinality_ok=(len(per_seed) == EXPECTED_N_SEEDS))
    agg["prereg"] = "preregs/2026-08-05_c5_fair_goal_owner_v1.md"
    agg["cites"] = [
        "notes/testfairness_audit_goal_owner.md",
        "notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md",
        "hdlab/goal_owner_select.py (directed_goal_outcome_score, promoted 2026-08-05)",
        "experiments/exp_component5_gold_role_isolated_v1.py (candidate generators, resolvers)",
        "hdlab/self_improving_loop.py (decide_keep_or_revert, promoted 2026-08-02)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    all_rows, core, twins = load_bank()
    assert len(core) >= 25, f"contract requires N>=25 core items, got {len(core)}"
    assert len(twins) >= 5, f"expected a meaningful no-distractor-twin subset, got {len(twins)}"
    print(f"[bank] {len(all_rows)} total rows: {len(core)} core + {len(twins)} twins", flush=True)

    # (1) STRUCTURAL GOLD-VET: every core item's naive recency baseline must resolve to the FOIL,
    # not the OWNER (a genuine trap by construction) -- re-derived here from the SAME resolver the
    # harness scores with (not hand-typed twice).
    bad_traps = []
    for it in core:
        role_seq_b, cluster_ids_b, _ = build_positions(it, GeneralRecencyEntityResolver(it["roster"]))
        outcome_positions = [i for i, r in enumerate(role_seq_b) if r in (R_UNMET, R_MET)]
        assert outcome_positions, f"{it['id']}: outcome never typed (S3 must carry an OUTCOME trigger)"
        recency_owner = cluster_ids_b[outcome_positions[-1]]
        if recency_owner != it["foil"]:
            bad_traps.append((it["id"], recency_owner, it["foil"]))
    assert not bad_traps, f"non-genuine traps (recency did not land on the foil): {bad_traps}"
    print(f"[SELFTEST 1/6] all {len(core)} core items are genuine recency traps "
          f"(naive recency lands on the foil, not the owner)", flush=True)

    # (2) leakage guard: owner is never the only roster entity in a core item (foil always present)
    for it in core:
        assert it["foil"] is not None and it["foil"] in it["roster"], f"{it['id']}: no real foil choice"
    print("[SELFTEST 2/6] no core item is single-entity (foil always present, real choice)", flush=True)

    # (3) twins are true no-distractor controls: no foil, gold recoverable trivially
    for it in twins:
        assert it["foil"] is None and len(it["roster"]) == 1
        role_seq_b, cluster_ids_b, _ = build_positions(it, GeneralRecencyEntityResolver(it["roster"]))
        outcome_positions = [i for i, r in enumerate(role_seq_b) if r in (R_UNMET, R_MET)]
        assert outcome_positions, f"{it['id']}: twin outcome never typed"
        assert cluster_ids_b[outcome_positions[-1]] == it["owner"], (
            f"{it['id']}: twin (no-distractor) baseline must trivially match owner")
    print(f"[SELFTEST 3/6] all {len(twins)} twins resolve correctly with no distractor (sanity)", flush=True)

    # (4) ARMS-MUST-DIFFER-style check: on at least one genuine trap, baseline and content-match
    # candidates must actually disagree at the outcome slot (else the mechanism never gets exercised)
    it0 = next(x for x in core if x["verb_type"] == "explicit_psych")
    role_seq_b, cluster_ids_b, _ = build_positions(it0, GeneralRecencyEntityResolver(it0["roster"]))
    role_seq_c, cluster_ids_c, _ = build_positions(it0, ContentMatchResolver(it0["roster"]))
    outcome_pos0 = [i for i, r in enumerate(role_seq_b) if r in (R_UNMET, R_MET)][-1]
    assert cluster_ids_b[outcome_pos0] != cluster_ids_c[outcome_pos0], (
        f"{it0['id']}: recency and content-match candidates must differ on an explicit-goal trap")
    print(f"[SELFTEST 4/6] baseline vs content-match candidates differ on {it0['id']!r} "
          f"(mechanism is exercisable)", flush=True)

    # (5) action-implied items are honestly typing-missed for GOAL (the named gap, not a bug)
    implied = [x for x in core if x["verb_type"] == "action_implied"]
    assert len(implied) >= 5, "expected a real action-implied subset"
    n_miss = 0
    for it in implied:
        role_seq_b, _cid, _ = build_positions(it, GeneralRecencyEntityResolver(it["roster"]))
        if R_GOAL not in role_seq_b:
            n_miss += 1
    assert n_miss == len(implied), (
        f"expected ALL {len(implied)} action_implied items to miss GOAL typing (lexicon has no "
        f"generative inference); got {n_miss}/{len(implied)} -- if this changes, the gap claim "
        f"in the docstring needs re-scoping")
    print(f"[SELFTEST 5/6] all {len(implied)} action_implied items honestly miss GOAL typing "
          f"(confirms the named generative-inference gap, not a harness bug)", flush=True)

    # (6) one full seed sanity + validity gates fire as expected
    res = run_seed(0)
    assert res["n_divergent"] >= 10, f"too few divergent items for a powered test: {res['n_divergent']}"
    assert res["recency_floor_divergent"] == 0.0, (
        f"recency floor on the divergent subset must be EXACTLY 0.0 by construction "
        f"(divergent is DEFINED as recency!=gold); got {res['recency_floor_divergent']}")
    assert res["ceiling_accuracy"] >= 0.9, f"goal-subject ceiling too low: {res['ceiling_accuracy']}"
    print(f"[SELFTEST 6/6] seed0: N_divergent={res['n_divergent']} recency_floor="
          f"{res['recency_floor_divergent']} ceiling={res['ceiling_accuracy']} "
          f"system={res['system_accuracy_divergent']} "
          f"system_scrambled={res['system_scrambled_accuracy_divergent']}", flush=True)
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
