"""exp_real_text_goal_owner_generalization_diagnostic_v1 -- REAL-TEXT GENERALIZATION DIAGNOSTIC for
the composed goal-owner-selection + outcome-valence organs.

WHY (task brief): every prior VET of hdlab.goal_owner_select.select_outcome_owner and
hdlab.goal_typing.congruence_with_lexicon_fallback ran on HAND-AUTHORED, controlled-construction
instruments (goal_owner_fair_v1.jsonl and its primacy-trap extension). Those instruments were
carefully written so goal/outcome vocabulary matched the mechanism's hand-typed lexicons by
construction. The open question this cell answers is diagnostic, not a capability gate: do the
WIRED, already-validated organs generalize to REAL narrative prose nobody wrote for this test, and
if they miss, WHICH pipeline stage breaks first?

PRE-REGISTERED HONESTY CONDITIONS (per task brief, satisfied before this cell ran the organ):
1. Passages were selected from experiments/data/real_text_goal_owner_diagnostic_v1.jsonl on PURELY
   STRUCTURAL narrative criteria -- single/dual protagonist, an identifiable goal, and a resolved
   (met/unmet) outcome within the excerpted span -- never by pre-running the organ and keeping only
   the wins. Sourced from data/corpora/graded_readers_grade1 (grade 1, closest register to the
   hand-authored instrument) and data/corpora/mcguffey_graded (grade 2/3, richer real prose),
   McGuffey's Eclectic Readers, public domain. See that file's `notes` field per item for the
   specific judgment call / expected stress point of each passage, written BEFORE this cell was run.
2. Gold (`gold_outcome_owner`, `gold_outcome_polarity`, `roster`) was hand-authored by a single
   annotator into that JSONL file before this cell existed in runnable form.
3. This cell does NOT declare a HARD_PASS/HARD_FAIL band. `verdict` is always DIAGNOSTIC_COMPLETE
   (or CELL_CRASHED on a genuine bug). The deliverable is the measured accuracy numbers AS MEASURED
   (a low score is an honest finding, not a cell failure) plus a per-miss FAILURE-STAGE diagnosis
   that tallies which pipeline stage broke, surfacing the real bottleneck on real text.

MECHANISM UNDER TEST (glass-box, reused verbatim, ZERO new hdlab code):
- hdlab.goal_owner_select.select_outcome_owner(text, roster, seed) -- the full composed
  candidate-enumeration + directed-score argmax + content-coherence-tiebreak organ (promoted
  2026-08-05, wired production entry point).
- hdlab.goal_typing.congruence_with_lexicon_fallback(text) -- goal-congruence-PRIMARY /
  V2_OUTCOME_UNMET/_MET-lexicon-FALLBACK outcome-polarity organ (promoted 2026-08-06).
This cell's own code is HARNESS-ONLY: 3 positional baselines (recency / first-mention / majority,
same formulas as exp_c5_fair_goal_owner_primacy_v1.py's baseline_recency/_first_mention/_majority)
+ a failure-stage DIAGNOSIS layer that re-walks the SAME production primitives
(GeneralRecencyEntityResolver.subject_entity, hdlab.goal_typing.type_goal_events,
hdlab.goal_typing.congruence_outcome_valence, hdlab.goal_typing.lexicon_predict) to introspect
WHERE a miss originated -- no new typing/scoring mechanism is introduced anywhere in this file.

FAILURE-STAGE TAXONOMY (owner-selection side; assigned only when system_owner != gold_owner):
- OUTCOME_NEVER_TYPED (event extraction): the outcome (final) sentence never trips an
  OUTCOME_UNMET/OUTCOME_MET event for ANY candidate -- select_outcome_owner cannot even run
  (enumerate_and_score's precondition fails); the outcome-valence lexicon gate is the blocker.
- EVENT_EXTRACTION_MISS_no_goal_typed_for_anyone: outcome WAS typeable, but no GOAL event fired for
  ANY roster entity in the non-outcome sentences -- type_goal_events never recognized the passage's
  goal construction at all.
- COREF_SUBJECT_RESOLUTION_MISS: a GOAL event DID fire, but for the wrong entity -- the structural
  subject resolver attributed the goal-bearing clause to the foil, not the gold owner.
- CANDIDATE_SCORING_MISS: the GOAL correctly bound to the gold owner structurally, but
  directed_goal_outcome_score's argmax favored a different candidate anyway.
- TIEBREAK_MISS: the directed score tied across candidates and the content-coherence tie-break (or
  its sorted-order fallback) picked the wrong one.
FAILURE-STAGE TAXONOMY (polarity side; assigned only when system_polarity != gold_polarity):
- LEXICON_COVERAGE_MISS_<reason>: congruence_outcome_valence abstained (NA) -- the outcome verb (or
  the goal's embedded purpose-infinitival verb) is out-of-vocabulary for the class-registry, and the
  V2_OUTCOME_UNMET/_MET fallback lexicon (~17+6 words) also missed or mis-typed it.
- GOAL_CONGRUENCE_MISPREDICT_<reason>: the goal-congruence engine DID fire (non-NA) but produced the
  wrong polarity (a genuine mechanism error, not a coverage gap).

GUARDS: glass-box; deterministic given seed (SEEDS=[0,1,2], fixed integers, no hash()-derived
seeding -- PROT-023/F.5 compliant by construction); resumable per-seed via tools/exp_checkpoint.py;
ASCII-only; atomic metrics write (tmp + os.replace); LOCAL-ONLY, in-process foreground, NOT
queue-dispatched, no push (per task brief). No HARD_PASS threshold is declared -> crlb_n/a and
HP_SCOPE are both explicitly n/a (diagnostic cell, not a capacity-feasibility or capability gate).

Cites: hdlab/goal_owner_select.py; hdlab/goal_typing.py; experiments/exp_c5_fair_goal_owner_primacy_v1.py
(baseline formulas reused); experiments/data/real_text_goal_owner_diagnostic_v1.jsonl (this cell's gold).
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

ANCHOR_NAME = "real_text_goal_owner_generalization_diagnostic_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "real_text_goal_owner_diagnostic_v1.jsonl")

# ---- REUSED BIT-IDENTICAL: the promoted, wired production organs (no new hdlab code) -------------
from hdlab.goal_owner_select import (  # noqa: E402
    select_outcome_owner, enumerate_and_score, build_candidate_role_seq, _outcome_pos,
    GeneralRecencyEntityResolver, _sentences, _ordered_tokens, R_GOAL,
)
from hdlab.goal_typing import (  # noqa: E402
    congruence_with_lexicon_fallback, congruence_outcome_valence, lexicon_predict, type_goal_events,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
EXPECTED_N_ITEMS = 10
EXPECTED_N_MET = 7
EXPECTED_N_UNMET = 3


# ============================================================================ bank load
def load_bank():
    rows = []
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


# ============================================================================ positional baselines
# (harness-only reads; SAME formulas as exp_c5_fair_goal_owner_primacy_v1.py's
# baseline_recency/_first_mention/_majority -- reused, not reinvented)
def baseline_recency(item):
    """Whole-passage structural subject resolution (GeneralRecencyEntityResolver), taking the LAST
    sentence whose subject resolves to a roster entity as the recency answer."""
    roster = item["roster"]
    sents = _sentences(item["text"])
    resolver = GeneralRecencyEntityResolver(roster)
    last_resolved = None
    for s in sents:
        r = resolver.subject_entity(s)
        if r is not None:
            last_resolved = r
    return last_resolved


def baseline_first_mention(item):
    roster = item["roster"]
    toks = _ordered_tokens(item["text"])
    for t in toks:
        if t in roster:
            return t
    return None


def baseline_majority(item):
    roster = item["roster"]
    toks = _ordered_tokens(item["text"])
    counts = Counter(t for t in toks if t in roster)
    if not counts:
        return None
    first_idx = {e: toks.index(e) for e in counts}
    return min(counts.keys(), key=lambda e: (-counts[e], first_idx[e]))


# ============================================================================ failure-stage diagnosis
def outcome_typeable(text, roster):
    """True iff AT LEAST ONE roster candidate's role_seq (hypothesized as the outcome-slot filler)
    contains an OUTCOME_UNMET/OUTCOME_MET event for the outcome (final) sentence -- the hard
    precondition enumerate_and_score/select_outcome_owner require (raises only when NO candidate
    types, per hdlab.goal_owner_select.enumerate_and_score's 2026-08-06 Tier-3-bridging update).
    UPDATED 2026-08-06 (task brief Part 3, harness-only change, no new mechanism): the prior version
    checked only sorted(roster.keys())[0], which was a safe proxy while outcome-typing was subject-
    INVARIANT (lexical typing fires identically for whichever candidate is hypothesized, so all
    candidates were always typeable together or not at all). The Tier-3 evaluative bridge (wired into
    hdlab.goal_owner_select.build_candidate_role_seq) is candidate-DIRECTED -- it fires only for the
    evaluative construction's addressee, who must already hold an open GOAL -- so typeability can now
    differ per candidate; checking only the alphabetically-first roster key could under-report
    OUTCOME_NEVER_TYPED for a passage where the bridge fires for a later-sorted candidate. This
    harness-only introspection now mirrors production's own precondition exactly (re-walks the SAME
    production primitive, build_candidate_role_seq/_outcome_pos, for every candidate -- no new typing
    or scoring mechanism introduced)."""
    for cand in sorted(roster.keys()):
        role_seq, _cid = build_candidate_role_seq(text, roster, cand)
        if _outcome_pos(role_seq) is not None:
            return True
    return False


def structural_goal_trace(text, roster):
    """Re-walk STRUCTURAL (resolver-based) subject + type_goal_events for every non-final sentence.
    Diagnostic introspection only -- calls the SAME production functions the organ itself calls, no
    new typing mechanism."""
    sents = _sentences(text)
    resolver = GeneralRecencyEntityResolver(roster)
    trace = []
    for s in sents[:-1]:
        subj = resolver.subject_entity(s)
        events = type_goal_events(s, subj)
        trace.append({"sentence": s, "resolved_subject": subj, "events": events})
    return trace


def diagnose_owner_miss(text, roster, gold_owner, system_owner, outcome_ok, scored, winners):
    if not outcome_ok:
        return "OUTCOME_NEVER_TYPED_event_extraction_blocks_owner_selection_entirely"
    trace = structural_goal_trace(text, roster)
    any_goal = any(r == R_GOAL for t in trace for (_e, r) in t["events"])
    goal_for_gold = any(r == R_GOAL and e == gold_owner for t in trace for (e, r) in t["events"])
    if not any_goal:
        return "EVENT_EXTRACTION_MISS_no_goal_typed_for_anyone"
    if not goal_for_gold:
        return "COREF_SUBJECT_RESOLUTION_MISS_goal_bound_to_wrong_entity"
    max_score = max(scored.values())
    if scored.get(gold_owner, 0.0) < max_score:
        return "CANDIDATE_SCORING_MISS_directed_score_favored_other_entity"
    if winners is not None and len(winners) > 1 and system_owner != gold_owner:
        return "TIEBREAK_MISS_content_coherence_picked_wrong_entity"
    return "UNKNOWN_MISS_investigate"


def diagnose_polarity_miss(text):
    verdict_c, detail_c = congruence_outcome_valence(text)
    if verdict_c == "NA":
        return f"LEXICON_COVERAGE_MISS_{detail_c.get('reason', 'unknown')}"
    return f"GOAL_CONGRUENCE_MISPREDICT_{detail_c.get('reason', 'unknown')}"


# ============================================================================ per-item eval
def run_item(item: dict, seed: int):
    text, roster = item["text"], item["roster"]
    gold_owner, gold_pol = item["gold_outcome_owner"], item["gold_outcome_polarity"]

    outcome_ok = outcome_typeable(text, roster)
    if outcome_ok:
        scored, winners = enumerate_and_score(text, roster, seed)
        system_owner = select_outcome_owner(text, roster, seed)
    else:
        scored, winners, system_owner = None, None, None

    recency_owner = baseline_recency(item)
    first_mention_owner = baseline_first_mention(item)
    majority_owner = baseline_majority(item)

    owner_hit = bool(outcome_ok and system_owner == gold_owner)
    owner_failure_class = None if owner_hit else diagnose_owner_miss(
        text, roster, gold_owner, system_owner, outcome_ok, scored, winners)

    system_pol, pol_detail = congruence_with_lexicon_fallback(text)
    sents = _sentences(text)
    baseline_pol = lexicon_predict(sents[-1]) if sents else "NONE"
    pol_hit = system_pol.lower() == gold_pol
    baseline_pol_hit = baseline_pol.lower() == gold_pol
    pol_failure_class = None if pol_hit else diagnose_polarity_miss(text)

    return dict(
        id=item["id"], corpus=item["corpus"], gold_owner=gold_owner, gold_polarity=gold_pol,
        outcome_typeable=outcome_ok,
        system_owner=system_owner, owner_hit=owner_hit,
        recency_owner=recency_owner, recency_hit=(recency_owner == gold_owner),
        first_mention_owner=first_mention_owner,
        first_mention_hit=(first_mention_owner == gold_owner),
        majority_owner=majority_owner, majority_hit=(majority_owner == gold_owner),
        owner_failure_class=owner_failure_class,
        system_polarity=system_pol, system_polarity_reason=pol_detail.get("reason"),
        polarity_hit=pol_hit,
        baseline_polarity=baseline_pol, baseline_polarity_hit=baseline_pol_hit,
        polarity_failure_class=pol_failure_class,
        scored=scored, winners=winners,
    )


# ============================================================================ per-seed unit
def run_seed(seed: int):
    bank = load_bank()
    rows = [run_item(it, seed) for it in bank]

    def rate(key):
        return round(sum(bool(r[key]) for r in rows) / len(rows), 4) if rows else None

    owner_failure_tally = Counter(r["owner_failure_class"] for r in rows if r["owner_failure_class"])
    polarity_failure_tally = Counter(
        r["polarity_failure_class"] for r in rows if r["polarity_failure_class"])

    return dict(
        seed=seed, n_items=len(rows),
        n_outcome_typeable=sum(bool(r["outcome_typeable"]) for r in rows),
        organ_owner_accuracy=rate("owner_hit"),
        recency_accuracy=rate("recency_hit"),
        first_mention_accuracy=rate("first_mention_hit"),
        majority_accuracy=rate("majority_hit"),
        organ_polarity_accuracy=rate("polarity_hit"),
        lexicon_baseline_polarity_accuracy=rate("baseline_polarity_hit"),
        owner_failure_tally=dict(owner_failure_tally),
        polarity_failure_tally=dict(polarity_failure_tally),
        rows=rows,
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    n_items = per_seed[seeds[0]]["n_items"]
    cardinality_ok = all(per_seed[s]["n_items"] == EXPECTED_N_ITEMS for s in seeds)

    # determinism check (informational, not a hard gate): the SAME hit-pattern across seeds
    hit_patterns = {
        s: tuple((r["owner_hit"], r["polarity_hit"]) for r in per_seed[s]["rows"]) for s in seeds
    }
    deterministic_across_seeds = len(set(hit_patterns.values())) == 1

    combined_owner_tally = Counter()
    combined_polarity_tally = Counter()
    for s in seeds:
        combined_owner_tally.update(per_seed[s]["owner_failure_tally"])
        combined_polarity_tally.update(per_seed[s]["polarity_failure_tally"])
    # representative (seed-0) tally for the headline report -- deterministic_across_seeds means this
    # equals every other seed's tally; report both the representative and the seed-summed version.
    rep_owner_tally = dict(per_seed[seeds[0]]["owner_failure_tally"])
    rep_polarity_tally = dict(per_seed[seeds[0]]["polarity_failure_tally"])

    dominant_owner_bottleneck = (max(rep_owner_tally, key=rep_owner_tally.get)
                                  if rep_owner_tally else None)
    dominant_polarity_bottleneck = (max(rep_polarity_tally, key=rep_polarity_tally.get)
                                     if rep_polarity_tally else None)

    organ_owner_accuracy = mean("organ_owner_accuracy")
    recency_accuracy = mean("recency_accuracy")
    first_mention_accuracy = mean("first_mention_accuracy")
    majority_accuracy = mean("majority_accuracy")
    max_baseline = max(v for v in (recency_accuracy, first_mention_accuracy, majority_accuracy)
                       if v is not None)
    organ_beats_baselines = (organ_owner_accuracy is not None
                             and organ_owner_accuracy > max_baseline)

    organ_polarity_accuracy = mean("organ_polarity_accuracy")
    lexicon_polarity_accuracy = mean("lexicon_baseline_polarity_accuracy")
    organ_beats_lexicon_polarity = (
        organ_polarity_accuracy is not None and lexicon_polarity_accuracy is not None
        and organ_polarity_accuracy > lexicon_polarity_accuracy)

    verdict = "DIAGNOSTIC_COMPLETE" if cardinality_ok else "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"

    summary = (
        f"N_items={n_items} (7 met + 3 unmet gold). "
        f"OWNER: organ={organ_owner_accuracy} vs recency={recency_accuracy} "
        f"first_mention={first_mention_accuracy} majority={majority_accuracy} "
        f"(max_baseline={round(max_baseline, 4)}, organ_beats_baselines={organ_beats_baselines}). "
        f"POLARITY: organ={organ_polarity_accuracy} vs lexicon_baseline={lexicon_polarity_accuracy} "
        f"(organ_beats_lexicon={organ_beats_lexicon_polarity}). "
        f"deterministic_across_seeds={deterministic_across_seeds}. "
        f"OWNER_FAILURE_TALLY(seed0)={rep_owner_tally} -> dominant={dominant_owner_bottleneck}. "
        f"POLARITY_FAILURE_TALLY(seed0)={rep_polarity_tally} -> dominant={dominant_polarity_bottleneck}. "
        f"This is a DIAGNOSTIC probe (no HARD_PASS/HARD_FAIL capability gate) -- numbers are reported "
        f"AS MEASURED; a low score is a finding about real-text generalization, not a cell failure."
    )

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary,
        n_seeds=len(seeds), n_items=n_items, cardinality_ok=cardinality_ok,
        deterministic_across_seeds=deterministic_across_seeds,
        organ_owner_accuracy=organ_owner_accuracy, recency_accuracy=recency_accuracy,
        first_mention_accuracy=first_mention_accuracy, majority_accuracy=majority_accuracy,
        max_baseline_owner_accuracy=round(max_baseline, 4),
        organ_beats_baselines=organ_beats_baselines,
        organ_polarity_accuracy=organ_polarity_accuracy,
        lexicon_baseline_polarity_accuracy=lexicon_polarity_accuracy,
        organ_beats_lexicon_polarity=organ_beats_lexicon_polarity,
        owner_failure_tally_seed0=rep_owner_tally,
        polarity_failure_tally_seed0=rep_polarity_tally,
        owner_failure_tally_combined_all_seeds=dict(combined_owner_tally),
        polarity_failure_tally_combined_all_seeds=dict(combined_polarity_tally),
        dominant_owner_bottleneck=dominant_owner_bottleneck,
        dominant_polarity_bottleneck=dominant_polarity_bottleneck,
        per_seed=per_seed,
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def _arms_must_differ_check(per_seed0_rows):
    """META_RULE_AF-style hash check: the organ's owner-answer VECTOR must not be bit-identical to
    ALL THREE positional baselines simultaneously (else this instrument tests nothing new)."""
    def digest(key):
        blob = "|".join(str(r[key]) for r in per_seed0_rows)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()
    d_sys = digest("system_owner")
    d_rec, d_fm, d_maj = digest("recency_owner"), digest("first_mention_owner"), digest("majority_owner")
    all_identical = d_sys == d_rec == d_fm == d_maj
    return {"system": d_sys, "recency": d_rec, "first_mention": d_fm, "majority": d_maj,
            "all_identical_to_every_baseline": all_identical}


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
              f"organ_owner={res['organ_owner_accuracy']} recency={res['recency_accuracy']} "
              f"first_mention={res['first_mention_accuracy']} majority={res['majority_accuracy']} "
              f"organ_polarity={res['organ_polarity_accuracy']} "
              f"lexicon_polarity={res['lexicon_baseline_polarity_accuracy']}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(OUTPUT_DIR).values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")
    agg = aggregate(per_seed)
    agg["arms_must_differ"] = _arms_must_differ_check(per_seed[SEEDS[0]]["rows"])
    agg["arms_differ_verified"] = not agg["arms_must_differ"]["all_identical_to_every_baseline"]
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(
        seeds=SEEDS, bank_path=BANK_PATH, expected_n_items=EXPECTED_N_ITEMS,
        expected_n_met=EXPECTED_N_MET, expected_n_unmet=EXPECTED_N_UNMET,
        final_metrics_atomicity="tmp_replace",
        crlb_n_a="diagnostic cell: measures accuracy AS MEASURED, no capacity-feasibility "
                 "quantitative discriminator threshold is declared",
        hp_scope_n_a="no HARD_PASS/HARD_FAIL gate declared per task brief (diagnostic probe)",
        deterministic_seeding=True,
    )
    agg["prereg"] = ("pre-registered honesty conditions in this cell's own module docstring "
                     "(passages selected before running the organ; gold authored before this cell "
                     "was runnable; no HARD_PASS/HARD_FAIL band declared)")
    agg["cites"] = [
        "hdlab/goal_owner_select.py (select_outcome_owner, promoted 2026-08-05)",
        "hdlab/goal_typing.py (congruence_with_lexicon_fallback, promoted 2026-08-06)",
        "experiments/exp_c5_fair_goal_owner_primacy_v1.py (baseline formulas reused)",
        "experiments/data/real_text_goal_owner_diagnostic_v1.jsonl (this cell's gold, 10 items)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    bank = load_bank()
    assert len(bank) == EXPECTED_N_ITEMS, f"expected {EXPECTED_N_ITEMS} items, got {len(bank)}"
    n_met = sum(1 for it in bank if it["gold_outcome_polarity"] == "met")
    n_unmet = sum(1 for it in bank if it["gold_outcome_polarity"] == "unmet")
    assert n_met == EXPECTED_N_MET and n_unmet == EXPECTED_N_UNMET, (n_met, n_unmet)
    for it in bank:
        assert it["gold_outcome_owner"] in it["roster"], it["id"]
        assert len(it["roster"]) >= 2, f"{it['id']}: need 2+ roster entities for non-trivial owner"
        assert len(_sentences(it["text"])) >= 2, f"{it['id']}: need 2+ sentences"
    print(f"[SELFTEST 1/4] bank cardinality + gold-validity OK: {len(bank)} items "
          f"({n_met} met, {n_unmet} unmet)", flush=True)

    # (2) REAL production organs are actually being called (real_code_path, not a synthetic-only
    # branch) -- exercise select_outcome_owner + congruence_with_lexicon_fallback on the FIRST bank
    # item at seed 0 and assert they return well-typed results (string owner or None; a valid
    # polarity token), proving the import + call signature is live before the full run.
    it0 = bank[0]
    ok0 = outcome_typeable(it0["text"], it0["roster"])
    if ok0:
        owner0 = select_outcome_owner(it0["text"], it0["roster"], seed=0)
        assert owner0 in it0["roster"], f"select_outcome_owner returned non-roster value {owner0!r}"
    pol0, detail0 = congruence_with_lexicon_fallback(it0["text"])
    assert pol0 in ("MET", "UNMET", "AMBIGUOUS", "NONE"), f"unexpected polarity token {pol0!r}"
    print(f"[SELFTEST 2/4] real production organs callable: outcome_typeable={ok0} "
          f"polarity_organ({it0['id']!r})={pol0!r} reason={detail0.get('reason')}", flush=True)

    # (3) one full seed sanity + failure-tally shape
    res = run_seed(0)
    assert res["n_items"] == EXPECTED_N_ITEMS
    assert 0.0 <= res["organ_owner_accuracy"] <= 1.0
    assert 0.0 <= res["organ_polarity_accuracy"] <= 1.0
    print(f"[SELFTEST 3/4] seed0: organ_owner={res['organ_owner_accuracy']} "
          f"recency={res['recency_accuracy']} first_mention={res['first_mention_accuracy']} "
          f"majority={res['majority_accuracy']} organ_polarity={res['organ_polarity_accuracy']} "
          f"lexicon_polarity={res['lexicon_baseline_polarity_accuracy']} "
          f"owner_failures={res['owner_failure_tally']} "
          f"polarity_failures={res['polarity_failure_tally']}", flush=True)

    # (4) determinism: repeating seed 0 must reproduce byte-identical hit-pattern (no hash()-seeded
    # nondeterminism anywhere in this harness -- PROT-023/F.5 self-check)
    res_repeat = run_seed(0)
    pat1 = tuple((r["owner_hit"], r["polarity_hit"]) for r in res["rows"])
    pat2 = tuple((r["owner_hit"], r["polarity_hit"]) for r in res_repeat["rows"])
    assert pat1 == pat2, "non-deterministic hit-pattern across repeated seed-0 runs"
    print("[SELFTEST 4/4] seed0 repeat is deterministic (bit-identical hit pattern)", flush=True)
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
                     "summary": f"CELL_CRASHED: {type(e).__name__}",
                     "elapsed_s": 0.0,
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
