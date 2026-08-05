"""exp_c5_fair_goal_owner_primacy_v1 -- FULLY-FAIR goal-owner test: PRIMACY-TRAP extension of
exp_c5_fair_goal_owner_v1, closing the confound flagged by independent Skunkworks gold-VET
(notes/skunkworks_goldvet_fair_goal_owner.md, commit 095d3a876): on the original 28-item
recency-trap bank, the goal-holder P is ALWAYS simultaneously the S1 grammatical subject AND the
first-mentioned entity AND the goal-holder -- so a trivial primacy/first-mention/subject picker
scores 28/28 (1.0), and the system's 0.6429 is BELOW that trivial ceiling. The audit's own fix
recommendation: "add items where the goal-holder is NOT the first-mentioned / not the S1 subject
... so that primacy and subject baselines FAIL and only goal-binding wins." This cell IS that fix.

PRE-REG: preregs/2026-08-05_c5_fair_goal_owner_primacy_v1.md
GOLD-VET: notes/goldvet_fair_goal_owner_primacy_v1.md

WHY (task brief): notes/skunkworks_goldvet_fair_goal_owner.md's "LOAD-BEARING DEFLATIONARY CAVEAT"
+ "RECOMMENDATION" sections -- the FAIR (recency-defeating) instrument still lets a
primacy/first-mention/subject heuristic win 28/28; 0.6429 must not be read as a capability number
until an instrument exists where those position heuristics ALSO fail.

BANK EXTENSION (experiments/data/goal_owner_fair_v1.jsonl, +20 rows, trap_type=="primacy",
additive -- the original 42 rows are UNCHANGED and un-touched by this cell): each item is a
4-sentence vignette, restructured from the recency-trap's 3-sentence shape specifically to defeat
POSITION heuristics: S1 introduces the DISTRACTOR D FIRST (D is named, unrelated filler action --
D is thus the first-mentioned entity AND S1's subject). S2 introduces the protagonist P WITH the
goal (12 explicit-psych-verb / 8 action-implied, same generative-inference split as the core bank,
reusing the CORE bank's exact vetted goal sentences verbatim -- zero new lexicon risk). S3 names D
AGAIN doing a second unrelated filler action (D's second mention -- this is what also defeats
nearest-subject AND majority-count: D now has 2 mentions vs P's 1, and D is the subject of the
sentence immediately preceding the outcome). S4 is the outcome clause (reusing the CORE bank's
exact vetted outcome sentence verbatim, pronoun-only, one polarity trigger), causally tied to P's
goal. By construction: first-mention=D, S1-subject=D, nearest-subject(S3)=D, majority-count=D
(2 mentions) -- ALL FOUR position heuristics point at the WRONG entity; only P holds a GOAL event
that binds the outcome, so goal-CONTENT binding is the only path to the gold answer.

GOLD-VET (rule c, triple-checked; see notes/goldvet_fair_goal_owner_primacy_v1.md):
(1) MECHANICAL pass (scratch verification script, reused lexicons V2_DESIRE / V2_OUTCOME_UNMET /
V2_OUTCOME_MET bit-identical): every item's S1/S3 (D filler) sentences carry ZERO desire/outcome
triggers (no cross-contamination); S2 carries EXACTLY the declared verb_type's trigger pattern
(explicit_psych has >=1 V2_DESIRE hit, action_implied has none); S4 carries EXACTLY the declared
polarity's outcome trigger and no desire trigger; S1/S3 name the foil (not the owner); S2 names the
owner (not the foil); S4 names NEITHER (pronoun-only); mention-count is EXACTLY foil=2, owner=1
(the structural cause of majority-baseline failure). 0/20 problems (script re-run, disk-verified).
(2) STRUCTURAL pass (this cell's self-test): re-derives, from the SAME resolvers the harness scores
with, that all FOUR position baselines (recency / first-mention / nearest-subject / majority) land
on the FOIL on every one of the 20 items -- a genuine four-way trap by construction, not by label.
(3) Manual read (all 20 items, this session): confirmed the outcome clause is causally P's own
consequence (reusing the CORE bank's already-manually-verified goal/outcome sentence pairs
verbatim), D's two actions are genuinely unrelated filler (no shared vocabulary with the goal/
outcome), and gender pairing is correct throughout (reusing the CORE bank's already-verified
owner/foil pairs).

MECHANISM UNDER TEST (glass-box, reused verbatim, zero new hdlab code): identical organs to
exp_c5_fair_goal_owner_v1 -- GeneralRecencyEntityResolver / ContentMatchResolver / build_positions /
type_sentence_events (experiments/exp_component5_gold_role_isolated_v1.py), hdlab.goal_owner_select.
directed_goal_outcome_score (wired promotion), hdlab.self_improving_loop.decide_keep_or_revert
(wired promotion). NEW in this cell (harness-only, no new hdlab code): three additional position
baselines beyond v1's recency + majority -- first-mention (earliest-named roster entity in the
whole passage) and nearest-subject (the resolved subject of the sentence immediately preceding the
outcome sentence) -- both simple structural reads over the same _ordered_tokens /
GeneralRecencyEntityResolver.subject_entity primitives v1 already uses, not new mechanism.

FOUR BASELINES (all reported, all must be LOW on this subset for the instrument to be valid):
(a) recency-to-outcome: GeneralRecencyEntityResolver's whole-passage resolution at the outcome slot
    (same as v1's "trap floor" baseline).
(b) first-mention/primacy: the roster entity named earliest in the FULL passage text.
(c) nearest-subject: the resolved subject of the sentence immediately preceding the outcome
    sentence (S3 by construction).
(d) majority-class: the roster entity with the most explicit-name mentions (same structural
    baseline as v1, reused).
Note: v1's "goal-subject-ceiling" baseline (S1-alone) is NOT reported here as a construction
sanity check -- on primacy items S1 is deliberately the DISTRACTOR's sentence, so that baseline
would trivially read ~0.0 for P (by design, not a defect); it is subsumed by the first-mention
baseline (S1's only entity IS the first mention here).

METRIC: system accuracy on the full 20-item primacy-trap subset (N reported explicitly). A SCRAMBLE
control (role-scramble: the GOAL role's owner relabeled to the foil for the content candidate only,
text/gold unchanged -- identical non-vacuous-scramble pattern reused from v1 /
exp_component5_gold_role_isolated_v1) must collapse the system's gain over the baselines, or the
instrument does not discriminate.

PRE-REGISTERED CAN-FAIL (the instrument is VALID iff ALL FOUR):
1. ALL FOUR position baselines (recency, first-mention, nearest-subject, majority) score < 0.5 on
   the primacy-trap subset (ideally 0.0 by construction -- reported, not hardcoded).
2. n_primacy == 20 (cardinality; all 20 items are genuine four-way traps, verified in self-test).
3. Scramble collapses the system's gain over the (max of the four) baselines by >=50% relative
   (or both scrambled/unscrambled are non-vacuously zero, flagged `scramble_vacuous`).
4. Deterministic across 3 seeds.

If instrument_valid: report `system_accuracy_primacy` honestly -- THIS is the real goal-binding
capability number (a low score is an honest finding, not a cell failure; the PRIMARY deliverable is
the valid instrument). Keep the explicit_psych vs action_implied decomposition on this subset
(expect explicit>0, action_implied~0 = the same generative-inference gap should persist here too,
per the task brief's own prediction).

GUARDS: glass-box; all organs reused bit-identical (no new hdlab code, only 2 new harness-local
baseline READS over existing primitives); deterministic given seed (3 seeds); resumable per-seed via
tools/exp_checkpoint.py; ASCII-only; atomic metrics write; LOCAL-ONLY, in-process foreground, NOT
queue-dispatched, no push (per task brief).

Cites: notes/skunkworks_goldvet_fair_goal_owner.md (095d3a876); notes/testfairness_audit_goal_owner.md;
notes/DRILL_SYNTHESIS_goal_owner_brain_and_fairness.md; experiments/exp_c5_fair_goal_owner_v1.py
(the instrument this extends); hdlab/goal_owner_select.py; experiments/exp_component5_gold_role_
isolated_v1.py; hdlab/self_improving_loop.py.
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

ANCHOR_NAME = "c5_fair_goal_owner_primacy_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_owner_fair_v1.jsonl")

# ---- REUSED BIT-IDENTICAL: candidate generators + typing + positions ---------------------------
from exp_component5_gold_role_isolated_v1 import (  # noqa: E402
    GeneralRecencyEntityResolver, ContentMatchResolver, build_positions,
)
from exp_situation_model_goal_outcome_dimension_v1 import (  # noqa: E402
    R_UNMET, R_MET, _sentences, _ordered_tokens,
)
# ---- REUSED BIT-IDENTICAL: the promoted Component-5 selection organ (2026-08-05 wire-point) -----
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the promoted adoption gate (2026-08-02) ------------------------------
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
EXPECTED_N_PRIMACY = 20


# ============================================================================ bank load
def load_primacy_bank():
    rows = []
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    primacy = [r for r in rows if r.get("trap_type") == "primacy"]
    return primacy


# ============================================================================ baselines (NEW, harness-only reads)
def baseline_first_mention(item: dict):
    """(b) first-mention/primacy: the roster entity named EARLIEST in the full passage text."""
    roster = item["roster"]
    toks = _ordered_tokens(item["text"])
    for t in toks:
        if t in roster:
            return t
    return None


def baseline_nearest_subject(item: dict):
    """(c) nearest-subject: the resolved subject of the sentence immediately PRECEDING the outcome
    sentence (S3 by construction for these 4-sentence items). Uses a FRESH GeneralRecencyEntityResolver
    walked through all preceding sentences so subject resolution has correct recency state -- for
    these items every pre-outcome sentence names its subject explicitly, so this is deterministic."""
    roster = item["roster"]
    sents = _sentences(item["text"])
    resolver = GeneralRecencyEntityResolver(roster)
    subjects = [resolver.subject_entity(s) for s in sents]
    if len(subjects) < 2:
        return None
    return subjects[-2]  # subject of the sentence immediately before the (last) outcome sentence


def baseline_majority(item: dict):
    """(d) majority-class: the roster entity with the most explicit-name mentions; ties broken by
    earliest first mention. Computed structurally, never hand-set. Bit-identical formula to v1's
    baseline_majority (re-implemented locally to keep this cell import-self-contained)."""
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

    outcome_positions = [i for i, r in enumerate(role_seq_b) if r in (R_UNMET, R_MET)]
    assert outcome_positions, f"{item['id']}: outcome never typed"
    outcome_pos = outcome_positions[-1]

    recency_owner = cluster_ids_b[outcome_pos]
    first_mention_owner = baseline_first_mention(item)
    nearest_subject_owner = baseline_nearest_subject(item)
    majority_owner = baseline_majority(item)

    score_b = directed_goal_outcome_score(role_seq_b, cluster_ids_b, seed, outcome_pos)
    score_c = directed_goal_outcome_score(role_seq_c, cluster_ids_c, seed, outcome_pos)
    adopt = decide_keep_or_revert({"content": score_c - score_b}, ABSTAIN_BAND_DEFAULT)
    final_owner = cluster_ids_c[outcome_pos] if adopt == "content" else cluster_ids_b[outcome_pos]

    row = dict(
        id=item["id"], verb_type=item["verb_type"], outcome_polarity=item["outcome_polarity"],
        gold=gold,
        recency_owner=recency_owner, recency_matches_gold=(recency_owner == gold),
        first_mention_owner=first_mention_owner,
        first_mention_matches_gold=(first_mention_owner == gold),
        nearest_subject_owner=nearest_subject_owner,
        nearest_subject_matches_gold=(nearest_subject_owner == gold),
        majority_owner=majority_owner, majority_matches_gold=(majority_owner == gold),
        final_owner=final_owner, matches_gold=(final_owner == gold), adopt=adopt,
        directed_score_baseline=score_b, directed_score_content=score_c,
        # structural check: all four position baselines must agree with each other AND with the
        # foil (the four-way-trap-by-construction property this cell exists to verify)
        all_baselines_point_at_foil=(
            recency_owner == item["foil"] and first_mention_owner == item["foil"]
            and nearest_subject_owner == item["foil"] and majority_owner == item["foil"]),
    )

    # SCRAMBLE control: relabel the GOAL role's owner to the foil for the CONTENT candidate only --
    # text/gold unchanged. Identical non-vacuous-scramble pattern reused from v1.
    foil = item.get("foil")
    role_seq_s, cluster_ids_s, _es_s = build_positions(
        item, ContentMatchResolver(roster), scramble_owner_to_foil=foil)
    score_s = directed_goal_outcome_score(role_seq_s, cluster_ids_s, seed, outcome_pos)
    adopt_s = decide_keep_or_revert({"content": score_s - score_b}, ABSTAIN_BAND_DEFAULT)
    scrambled_owner = cluster_ids_s[outcome_pos] if adopt_s == "content" else cluster_ids_b[outcome_pos]
    row.update(scrambled_final_owner=scrambled_owner,
                scrambled_matches_gold=(scrambled_owner == gold))
    return row


# ============================================================================ per-seed unit
def run_seed(seed: int):
    primacy = load_primacy_bank()
    rows = [run_item(it, seed) for it in primacy]

    def rate(key):
        return round(sum(bool(r[key]) for r in rows) / len(rows), 4) if rows else None

    n_explicit = sum(1 for r in rows if r["verb_type"] == "explicit_psych")
    n_implied = sum(1 for r in rows if r["verb_type"] == "action_implied")
    explicit_rows = [r for r in rows if r["verb_type"] == "explicit_psych"]
    implied_rows = [r for r in rows if r["verb_type"] == "action_implied"]

    def rate_of(rows_):
        return round(sum(bool(r["matches_gold"]) for r in rows_) / len(rows_), 4) if rows_ else None

    return dict(
        seed=seed, n_primacy=len(rows),
        recency_accuracy=rate("recency_matches_gold"),
        first_mention_accuracy=rate("first_mention_matches_gold"),
        nearest_subject_accuracy=rate("nearest_subject_matches_gold"),
        majority_accuracy=rate("majority_matches_gold"),
        system_accuracy_primacy=rate("matches_gold"),
        system_scrambled_accuracy_primacy=rate("scrambled_matches_gold"),
        n_explicit=n_explicit, n_action_implied=n_implied,
        system_accuracy_explicit=rate_of(explicit_rows),
        system_accuracy_action_implied=rate_of(implied_rows),
        all_four_way_trap=all(r["all_baselines_point_at_foil"] for r in rows),
        rows=rows,
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    recency_accuracy = mean("recency_accuracy")
    first_mention_accuracy = mean("first_mention_accuracy")
    nearest_subject_accuracy = mean("nearest_subject_accuracy")
    majority_accuracy = mean("majority_accuracy")
    system_accuracy_primacy = mean("system_accuracy_primacy")
    system_scrambled_accuracy_primacy = mean("system_scrambled_accuracy_primacy")
    system_accuracy_explicit = mean("system_accuracy_explicit")
    system_accuracy_action_implied = mean("system_accuracy_action_implied")

    n_primacy = per_seed[seeds[0]]["n_primacy"]
    n_primacy_ok = all(per_seed[s]["n_primacy"] == n_primacy for s in seeds)
    all_four_way_trap = all(per_seed[s]["all_four_way_trap"] for s in seeds)

    # PRE-REGISTERED VALIDITY GATES (the instrument, not the pipeline, is being judged here)
    baseline_accs = dict(recency=recency_accuracy, first_mention=first_mention_accuracy,
                         nearest_subject=nearest_subject_accuracy, majority=majority_accuracy)
    gate_all_baselines_low = all(v is not None and v < 0.5 for v in baseline_accs.values())
    max_baseline = max(v for v in baseline_accs.values() if v is not None)

    gain_unscrambled = (system_accuracy_primacy - max_baseline
                        if system_accuracy_primacy is not None else None)
    gain_scrambled = (system_scrambled_accuracy_primacy - max_baseline
                      if system_scrambled_accuracy_primacy is not None else None)
    if gain_unscrambled is not None and gain_unscrambled > 1e-9:
        gate_scramble_collapses = (gain_scrambled is not None
                                   and gain_scrambled <= 0.5 * gain_unscrambled + 1e-9)
        scramble_vacuous = False
    else:
        gate_scramble_collapses = (gain_scrambled is not None and gain_scrambled <= 1e-9)
        scramble_vacuous = True

    cardinality_ok = (n_primacy_ok and n_primacy == EXPECTED_N_PRIMACY)
    instrument_valid = bool(gate_all_baselines_low and cardinality_ok and all_four_way_trap
                            and gate_scramble_collapses)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not all_four_way_trap:
        verdict = "HARD_FAIL_NOT_A_GENUINE_FOUR_WAY_TRAP"
    elif not gate_all_baselines_low:
        verdict = "INSTRUMENT_INVALID_A_POSITION_BASELINE_STILL_WINS"
    elif not gate_scramble_collapses:
        verdict = "INSTRUMENT_INVALID_SCRAMBLE_DID_NOT_COLLAPSE"
    else:
        verdict = "INSTRUMENT_VALID_FULLY_FAIR_PRIMACY_TRAP"

    summary = (
        f"N_primacy={n_primacy} (12 explicit + 8 action_implied). "
        f"BASELINES(all should be <0.5): recency={recency_accuracy} first_mention={first_mention_accuracy} "
        f"nearest_subject={nearest_subject_accuracy} majority={majority_accuracy} -> "
        f"all_baselines_low={gate_all_baselines_low} (max={round(max_baseline, 4)}). "
        f"all_four_way_trap={all_four_way_trap}. "
        f"SYSTEM(primacy)={system_accuracy_primacy} SYSTEM_SCRAMBLED={system_scrambled_accuracy_primacy} "
        f"scramble_collapses={gate_scramble_collapses} (vacuous={scramble_vacuous}). "
        f"explicit={system_accuracy_explicit} action_implied={system_accuracy_action_implied}. "
        f"instrument_valid={instrument_valid}. THIS IS THE REAL GOAL-BINDING CAPABILITY NUMBER "
        f"(beats every position heuristic iff instrument_valid and system_accuracy_primacy>max_baseline).")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        n_primacy=n_primacy, cardinality_ok=cardinality_ok, all_four_way_trap=all_four_way_trap,
        recency_accuracy=recency_accuracy, first_mention_accuracy=first_mention_accuracy,
        nearest_subject_accuracy=nearest_subject_accuracy, majority_accuracy=majority_accuracy,
        max_baseline_accuracy=round(max_baseline, 4),
        system_accuracy_primacy=system_accuracy_primacy,
        system_scrambled_accuracy_primacy=system_scrambled_accuracy_primacy,
        system_accuracy_explicit=system_accuracy_explicit,
        system_accuracy_action_implied=system_accuracy_action_implied,
        gate_all_baselines_low=gate_all_baselines_low,
        gate_scramble_collapses=gate_scramble_collapses, scramble_vacuous=scramble_vacuous,
        instrument_valid=instrument_valid,
        beats_every_position_heuristic=bool(
            instrument_valid and system_accuracy_primacy is not None
            and system_accuracy_primacy > max_baseline),
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
              f"N={res['n_primacy']} recency={res['recency_accuracy']} "
              f"first_mention={res['first_mention_accuracy']} "
              f"nearest_subject={res['nearest_subject_accuracy']} "
              f"majority={res['majority_accuracy']} system={res['system_accuracy_primacy']} "
              f"system_scrambled={res['system_scrambled_accuracy_primacy']}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(OUTPUT_DIR).values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(seeds=SEEDS, abstain_band=ABSTAIN_BAND_DEFAULT, bank_path=BANK_PATH,
                         expected_n_primacy=EXPECTED_N_PRIMACY,
                         cardinality_ok=(len(per_seed) == EXPECTED_N_SEEDS))
    agg["prereg"] = "preregs/2026-08-05_c5_fair_goal_owner_primacy_v1.md"
    agg["cites"] = [
        "notes/skunkworks_goldvet_fair_goal_owner.md (095d3a876)",
        "experiments/exp_c5_fair_goal_owner_v1.py (the instrument this extends)",
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
    primacy = load_primacy_bank()
    assert len(primacy) == EXPECTED_N_PRIMACY, (
        f"expected exactly {EXPECTED_N_PRIMACY} primacy-trap items, got {len(primacy)}")
    n_explicit = sum(1 for r in primacy if r["verb_type"] == "explicit_psych")
    n_implied = sum(1 for r in primacy if r["verb_type"] == "action_implied")
    print(f"[bank] {len(primacy)} primacy-trap items: {n_explicit} explicit + {n_implied} "
          f"action_implied", flush=True)

    # (1) STRUCTURAL GOLD-VET: every item is a genuine FOUR-WAY trap -- recency, first-mention,
    # nearest-subject, AND majority must all land on the FOIL, never the owner.
    bad = []
    for it in primacy:
        role_seq_b, cluster_ids_b, _ = build_positions(it, GeneralRecencyEntityResolver(it["roster"]))
        outcome_positions = [i for i, r in enumerate(role_seq_b) if r in (R_UNMET, R_MET)]
        assert outcome_positions, f"{it['id']}: outcome never typed"
        recency_owner = cluster_ids_b[outcome_positions[-1]]
        fm = baseline_first_mention(it)
        ns = baseline_nearest_subject(it)
        mj = baseline_majority(it)
        foil = it["foil"]
        if not (recency_owner == foil and fm == foil and ns == foil and mj == foil):
            bad.append((it["id"], dict(recency=recency_owner, first_mention=fm,
                                       nearest_subject=ns, majority=mj, expected_foil=foil)))
    assert not bad, f"non-genuine four-way traps: {bad}"
    print(f"[SELFTEST 1/5] all {len(primacy)} items are genuine FOUR-WAY traps (recency, "
          f"first-mention, nearest-subject, majority all land on the foil)", flush=True)

    # (2) leakage guard + mention-count-by-construction: foil named exactly twice, owner exactly once
    for it in primacy:
        toks = _ordered_tokens(it["text"])
        n_owner, n_foil = toks.count(it["owner"]), toks.count(it["foil"])
        assert n_foil == 2 and n_owner == 1, (
            f"{it['id']}: expected foil=2 owner=1 mentions, got foil={n_foil} owner={n_owner}")
    print("[SELFTEST 2/5] mention-count-by-construction holds on all items (foil=2, owner=1 -- "
          "the structural cause of the majority-baseline trap)", flush=True)

    # (3) ARMS-MUST-DIFFER-style check: baseline and content-match candidates must actually
    # disagree at the outcome slot on at least one explicit item (mechanism exercisable)
    it0 = next(x for x in primacy if x["verb_type"] == "explicit_psych")
    role_seq_b, cluster_ids_b, _ = build_positions(it0, GeneralRecencyEntityResolver(it0["roster"]))
    role_seq_c, cluster_ids_c, _ = build_positions(it0, ContentMatchResolver(it0["roster"]))
    outcome_pos0 = [i for i, r in enumerate(role_seq_b) if r in (R_UNMET, R_MET)][-1]
    assert cluster_ids_b[outcome_pos0] != cluster_ids_c[outcome_pos0], (
        f"{it0['id']}: recency and content-match candidates must differ")
    print(f"[SELFTEST 3/5] baseline vs content-match candidates differ on {it0['id']!r} "
          f"(mechanism is exercisable)", flush=True)

    # (4) action-implied items honestly miss GOAL typing (same named gap as v1, expected here too)
    from exp_situation_model_goal_outcome_dimension_v1 import R_GOAL
    implied = [x for x in primacy if x["verb_type"] == "action_implied"]
    assert len(implied) == 8
    n_miss = 0
    for it in implied:
        role_seq_b, _cid, _ = build_positions(it, GeneralRecencyEntityResolver(it["roster"]))
        if R_GOAL not in role_seq_b:
            n_miss += 1
    assert n_miss == len(implied), (
        f"expected all {len(implied)} action_implied items to miss GOAL typing; got {n_miss}")
    print(f"[SELFTEST 4/5] all {len(implied)} action_implied items honestly miss GOAL typing "
          f"(same generative-inference gap as the core bank, confirmed here too)", flush=True)

    # (5) one full seed sanity + validity gates fire as expected
    res = run_seed(0)
    assert res["n_primacy"] == EXPECTED_N_PRIMACY
    assert res["all_four_way_trap"] is True
    assert res["recency_accuracy"] == 0.0, f"recency must be exactly 0.0: {res['recency_accuracy']}"
    assert res["first_mention_accuracy"] == 0.0, f"first_mention must be 0.0: {res['first_mention_accuracy']}"
    assert res["nearest_subject_accuracy"] == 0.0, f"nearest_subject must be 0.0: {res['nearest_subject_accuracy']}"
    assert res["majority_accuracy"] == 0.0, f"majority must be 0.0: {res['majority_accuracy']}"
    print(f"[SELFTEST 5/5] seed0: N={res['n_primacy']} recency={res['recency_accuracy']} "
          f"first_mention={res['first_mention_accuracy']} nearest_subject={res['nearest_subject_accuracy']} "
          f"majority={res['majority_accuracy']} system={res['system_accuracy_primacy']} "
          f"system_scrambled={res['system_scrambled_accuracy_primacy']} "
          f"explicit={res['system_accuracy_explicit']} action_implied={res['system_accuracy_action_implied']}",
          flush=True)
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
