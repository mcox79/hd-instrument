"""exp_c5_multigoal_content_coherence_tiebreak_v1 -- THE 3c goal-content<->outcome-content
COHERENCE tie-break that resolves multi-goal cue-conflict, fixing the 1 remaining miss (t24) in the
47/48 goal-owner organ WITHOUT regressing the 47.

DIAGNOSIS (disk-verified, notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md "3c gap" +
data/exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1/metrics.json, commit b1b1ce460):
the promoted goal-coherence candidate-gen organ scores 47/48 on the fair instrument but misses
t24_tom_boat_foil_sid because directed_goal_outcome_score is CONTENT-BLIND -- it checks goal-PRESENCE
(has_goal), so when BOTH entities hold a goal it TIES. Instrumented on disk (seed0):
t24 scored {tom:1.0, sid:1.0} -> tie -> sorted-order winners[0] picks sid (WRONG; gold=tom).
Full-instrument tie scope (grep-verified this session): exactly 2 genuine ties across all 48 items --
t23_laurie_hay_foil_tom (resolved right by sorted-order) and t24_tom_boat_foil_sid (resolved WRONG).
No other item in the 48 (primacy_ep 0 ties, primacy_ai 0, recency_ep 0, recency_ai 2) is a tie.

THE MECHANISM (Trabasso content/causal coherence, brain-faithful; structural, reuse-based -- NOT a
learned content vector): among TIED goal-holders, prefer the entity whose GOAL event's THEME/object
overlaps the OUTCOME event's THEME/object. THIS IS A PURE ADD-ON TIE-BREAK:
  - candidate scoring is BYTE-IDENTICAL to the promoted organ (PARENT.build_candidate_role_seq +
    hdlab.goal_owner_select.directed_goal_outcome_score, unmodified); winners = argmax as before.
  - if there is exactly ONE winner (len(winners)==1) the tie-break NEVER runs -> the 46 non-tie
    items are BIT-IDENTICAL to the parent organ (no regression possible by construction).
  - only when tied AND exactly ONE tied candidate's goal-theme overlaps the outcome-theme does the
    tie-break override the sorted-order pick; otherwise it FALLS BACK to the sorted-order winner.
    So t23 (both tied candidates' goal-themes are DISJOINT from the outcome-theme -> no unique
    overlapper) falls back to sorted-order (laurie, correct, UNCHANGED); t24 (tom's goal-theme
    {oars,boat,tide} overlaps outcome-theme {tools,boat}={boat}, sid's {rope} does not) uniquely
    selects tom -> FIXED. Net effect on the 48: t24 flips sid->tom (wrong->right); all 47 others
    unchanged -> 48/48.

THEME EXTRACTION (glass-box, deterministic, no POS tagger, no external model): clause_theme(sentence)
= the set of head nouns of determiner-led noun phrases (det in {the,a,an,his,her,its,their}; skip a
short closed ADJ_STOP set of adjectives that appear pre-head in this bank; head = first following
non-adjective token), minus roster names. This is the "shared head-noun / object-noun overlap"
the task brief authorizes. clause_theme runs ONLY on tie items (t23, t24) + the authored multi-goal
items -- never on the 46 non-tie items -- so its lexicon only needs to be correct on those clauses
(self-test asserts the exact theme sets + the unique overlapper for every one).

AUTHORED DATA (mandatory -- the fair instrument has only 2 multi-goal items, too few to validate):
experiments/data/goal_owner_multigoal_coherence_v1.jsonl = 6 gender-matched cue-conflict FAMILIES x
2 variants (base + FLIP) = 12 items. Each has 2 gender-matched entities BOTH holding a goal (via a
purpose-infinitival "to VP" clause) with DISTINCT object-themes, and an outcome whose theme matches
EXACTLY ONE entity's goal-theme; gold_outcome_owner = that entity. The FLIP variant is the same
family with the outcome-theme swapped to the FOIL's object -> the gold answer FLIPS. This is the
decisive control: a tie-break that used POSITION/IDENTITY (not theme) cannot flip; only a
theme-driven tie-break gets both base and flip right. Self-VET (self_test below): both goals fire,
themes are distinct + decisive, sorted-order (positional) tie-break lands at exactly 6/12 (chance)
while content-coherence lands at 12/12, and no gold-answer leakage into the mechanism.

FAIRNESS / CONTROLS (pre-registered, all measured):
  (A) POSITIONAL tie-break baseline = the SAME pipeline with the theme tie-break OFF (falls back to
      sorted-order winners[0]) -- the most adversarial baseline (shares everything except the tie-
      break); content must strictly beat it. (B) FLIP-control: within every family content(base)
      picks the base owner and content(flip) picks the flipped owner (base_pick != flip_pick). (C)
      GOAL-SCRAMBLE (reused from the parent organ, scramble_goal_to_foil): corrupts the goal binding
      so only the foil carries a goal -> pick collapses to the foil -> wrong; non-vacuous collapse.
      (D) 4 positional baselines (recency, first_mention, nearest_subject, majority) reported.

PRE-REGISTERED BANDS (registered before running):
  HARD-PASS (ALL must hold):
    multi-goal: content_acc >= 11/12 (0.9167) AND content_acc > positional_tiebreak_acc AND
      flip_control_all_families_flip==True AND goal_scramble collapses non-vacuously; AND
    full instrument: content_total == 48/48 AND t24 content-correct AND t23 content-correct AND
      no_regression (content-correct set is a SUPERSET of positional-correct set) AND
      positional_total == 47/48 (proves the tie-break is exactly what closes the gap).
  HARD-FAIL: content_acc <= positional_tiebreak_acc (theme doesn't discriminate the multi-goal set)
    OR NOT flip_control_all_families_flip OR content_total < 48 OR NOT no_regression OR
    goal_scramble vacuous.
  MIDDLE_BAND: anything else (e.g. multi-goal content in [6/12, 11/12) but full instrument 48/48).

Prior-work check (SUBSTRATE-KB, run before authoring): tools/substrate_query.sh "goal content
outcome content coherence theme overlap tie break multi-goal cue conflict" -- top hit cosine=0.34
(the b1b1ce460 candidate-gen organ this cell extends; same arc, adjacent mechanism). No atom at
cosine>0.30 is about a THEME/object-overlap coherence tie-break among tied goal-holders. This is a
genuinely novel add-on to the existing organ, not a rediscovery.

GUARDS: glass-box; deterministic given seed (3 seeds; the has_goal/theme signals are seed-invariant,
seeds kept for organ-parity + resumable discipline); ASCII-only; atomic metrics write
(tmp+os.replace); resumable per-seed (tools/exp_checkpoint.py); LOCAL-ONLY, in-process foreground,
NOT queue-dispatched, no push; production hdlab/ UNTOUCHED (goal_typing.py / goal_owner_select.py /
etc. imported + consumed unmodified); parent organ cell + all reused experiment cells imported
bit-identical, never edited; no hash()-seeded RNG, sorted(set) ordering only.

Cites: notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md ("3c gap");
data/exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1/metrics.json (commit b1b1ce460,
the 47/48 organ this extends); experiments/exp_c5_primacy_trap_endtoend_goal_coherence_candidate_
gen_v1.py (PARENT: build_candidate_role_seq/_outcome_pos/load_primacy/PREVMOD/baselines, reused
bit-identical); hdlab/goal_typing.py (type_goal_events/R_GOAL, PROMOTED, consumed directly);
hdlab/goal_owner_select.py (directed_goal_outcome_score, PROMOTED, consumed directly);
experiments/exp_component5_gold_role_isolated_v1.py (GeneralRecencyEntityResolver, reused);
experiments/data/goal_owner_fair_v1.jsonl (t23/t24 multi-goal ties);
experiments/data/goal_owner_multigoal_coherence_v1.jsonl (authored this cell).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "c5_multigoal_content_coherence_tiebreak_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
MULTIGOAL_BANK_PATH = os.path.join(
    REPO_ROOT, "experiments", "data", "goal_owner_multigoal_coherence_v1.jsonl")

# ---- PROMOTED PRODUCTION ORGANS (WIRE-DON'T-ISLAND: consume hdlab/, unmodified) ----------------
from hdlab.goal_typing import type_goal_events, R_GOAL  # noqa: E402
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
# ---- REUSED BIT-IDENTICAL ------------------------------------------------------------------------
from exp_component5_gold_role_isolated_v1 import GeneralRecencyEntityResolver  # noqa: E402
from exp_situation_model_goal_outcome_dimension_v1 import _sentences  # noqa: E402
# ---- PARENT ORGAN (the 47/48 candidate-gen cell) reused bit-identical; only its TIE-BREAK changes -
import exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1 as PARENT  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)

# ============================================================================ THEME EXTRACTION
# Determiner-led NP head-noun extractor (glass-box). DET starts an NP; a short closed ADJ_STOP of
# pre-head adjectives is skipped; the head is the first following non-adjective token. Runs ONLY on
# tie items (t23/t24) + the authored multi-goal items (see enumerate_and_select_coherence), so its
# lexicon only needs coverage on those clauses -- self_test asserts every theme set + overlapper.
_DET = {"the", "a", "an", "his", "her", "its", "their"}
# Adjectives that appear directly pre-head in the tie clauses (t23/t24) + multi-goal bank.
_ADJ_STOP = {
    "old", "whole", "broken", "tall", "leaking", "torn", "heavy", "brass",
    "woven", "copper", "cracked", "wooden", "new",
}


def _theme_tokens(sentence: str):
    return [t for t in re.findall(r"[a-z']+", sentence.lower()) if t]


def clause_theme(sentence: str, roster: dict) -> set:
    """Head nouns of determiner-led NPs in `sentence`, minus roster entity names. Glass-box."""
    toks = _theme_tokens(sentence)
    heads = set()
    i = 0
    n = len(toks)
    while i < n:
        if toks[i] in _DET:
            j = i + 1
            while j < n and toks[j] in _ADJ_STOP:
                j += 1
            if j < n and toks[j] not in _DET:
                head = toks[j]
                if head not in roster:
                    heads.add(head)
            i = j + 1
        else:
            i += 1
    return heads


def entity_goal_themes(item: dict) -> dict:
    """{entity: set of goal-theme head nouns} from each non-outcome sentence whose STRUCTURAL subject
    (GeneralRecencyEntityResolver -- gold-free, identical walk to PARENT.build_candidate_role_seq)
    fires a GOAL. Independent of any proposed candidate; never consults item['owner']/gold."""
    sents = _sentences(item["text"])
    roster = item["roster"]
    resolver = GeneralRecencyEntityResolver(roster)
    themes: dict = {}
    for s in sents[:-1]:
        subj = resolver.subject_entity(s)
        if subj is None:
            continue
        fires_goal = any(r == R_GOAL and e == subj for (e, r) in type_goal_events(s, subj))
        if fires_goal:
            themes.setdefault(subj, set()).update(clause_theme(s, roster))
    return themes


# ============================================================================ SCORING (byte-identical to PARENT)
def score_candidates(item: dict, seed: int, scramble_goal_to_foil=None) -> dict:
    """Per-candidate directed_goal_outcome_score, IDENTICAL to PARENT.enumerate_and_select's scoring
    (same build_candidate_role_seq, same directed organ, same candidate set = sorted roster keys)."""
    candidates = sorted(item["roster"].keys())
    scored = {}
    for c in candidates:
        rs, cid = PARENT.build_candidate_role_seq(item, c, scramble_goal_to_foil=scramble_goal_to_foil)
        pos = PARENT._outcome_pos(rs)
        assert pos is not None, f"{item['id']}: outcome never typed for candidate {c!r}"
        scored[c] = directed_goal_outcome_score(rs, cid, seed, pos)
    return scored


def enumerate_and_select_coherence(item: dict, seed: int, scramble_goal_to_foil=None,
                                   theme_off: bool = False):
    """PARENT scoring + argmax, THEN the content-coherence tie-break. Returns
    (final_owner, scored, tie, tiebreak_fired).
      - len(winners)==1 -> return winners[0] (non-tie items BIT-IDENTICAL to PARENT).
      - tie AND not theme_off AND exactly one tied candidate's goal-theme overlaps the outcome-theme
        -> that candidate. Otherwise -> sorted-order winners[0] (fallback; PARENT behavior)."""
    scored = score_candidates(item, seed, scramble_goal_to_foil=scramble_goal_to_foil)
    candidates = sorted(item["roster"].keys())
    max_score = max(scored.values())
    winners = [c for c in candidates if scored[c] == max_score]
    tie = len(winners) > 1
    if tie and not theme_off:
        goal_themes = entity_goal_themes(item)
        out_theme = clause_theme(_sentences(item["text"])[-1], item["roster"])
        overlappers = [c for c in winners if goal_themes.get(c, set()) & out_theme]
        if len(overlappers) == 1:
            return overlappers[0], scored, tie, True
    return winners[0], scored, tie, False


# ============================================================================ MULTI-GOAL bank
def load_multigoal():
    rows = []
    with open(MULTIGOAL_BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run_item_multigoal(item: dict, seed: int):
    gold = item["gold_outcome_owner"]
    foil = item["foil"]
    c_owner, scored, tie, fired = enumerate_and_select_coherence(item, seed, theme_off=False)
    p_owner, _s2, _t2, _f2 = enumerate_and_select_coherence(item, seed, theme_off=True)
    s_owner, scored_s, _t3, _f3 = enumerate_and_select_coherence(
        item, seed, scramble_goal_to_foil=foil, theme_off=False)
    rec = PARENT.PREVMOD.resolve_outcome_recency_positional(item)
    fm = PARENT.baseline_first_mention(item)
    ns = PARENT.baseline_nearest_subject(item)
    mj = PARENT.baseline_majority(item)
    return dict(
        id=item["id"], family=item["family"], variant=item["variant"], gold=gold, foil=foil,
        both_goals_tie=tie, tiebreak_fired=fired, scored=scored, scored_scrambled=scored_s,
        content_owner=c_owner, content_matches=(c_owner == gold),
        positional_owner=p_owner, positional_matches=(p_owner == gold),
        scrambled_owner=s_owner, scrambled_matches=(s_owner == gold),
        recency_owner=rec, recency_matches=(rec == gold),
        first_mention_owner=fm, first_mention_matches=(fm == gold),
        nearest_subject_owner=ns, nearest_subject_matches=(ns == gold),
        majority_owner=mj, majority_matches=(mj == gold),
    )


# ============================================================================ FULL instrument re-run
def load_full_instrument():
    """The 48-item fair instrument, exactly as PARENT gates it: primacy ep(12)+ai(8) [all items],
    recency ep+ai [DIVERGENT subset only, i.e. recency baseline is wrong]. Returns list of
    (subset, verb_type, item) with a per-subset expected-N tag."""
    units = []
    for vt in ("explicit_psych", "action_implied"):
        for it in PARENT.load_primacy(vt):
            units.append(("primacy", vt, it))
    for vt in ("explicit_psych", "action_implied"):
        core, _twins = PARENT.PREVMOD.load_bank(vt)
        for it in core:
            rec = PARENT.PREVMOD.resolve_outcome_recency_positional(it)
            if rec != it["gold_outcome_owner"]:  # divergent subset only (PARENT contract)
                units.append(("recency", vt, it))
    return units


def run_full_instrument(seed: int):
    rows = []
    for subset, vt, it in load_full_instrument():
        gold = it["gold_outcome_owner"]
        c_owner, scored, tie, fired = enumerate_and_select_coherence(it, seed, theme_off=False)
        p_owner, _s, _t, _f = enumerate_and_select_coherence(it, seed, theme_off=True)
        rows.append(dict(id=it["id"], subset=subset, verb_type=vt, gold=gold, tie=tie,
                         tiebreak_fired=fired,
                         content_owner=c_owner, content_matches=(c_owner == gold),
                         positional_owner=p_owner, positional_matches=(p_owner == gold),
                         scored=scored))
    return rows


# ============================================================================ per-seed unit
def run_seed(seed: int):
    mg_rows = [run_item_multigoal(it, seed) for it in load_multigoal()]
    full_rows = run_full_instrument(seed)
    return dict(seed=seed, multigoal_rows=mg_rows, full_rows=full_rows)


# ============================================================================ aggregate + verdict
def _acc(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(sum(bool(v) for v in vals) / len(vals), 4) if vals else None


def _flip_control(mg_rows):
    """Within each family: content(base) picks base gold, content(flip) picks flip gold, and the two
    picks DIFFER (the answer actually flipped). Positional picks are also returned for contrast."""
    fams = {}
    for r in mg_rows:
        fams.setdefault(r["family"], {})[r["variant"]] = r
    details = {}
    all_flip = True
    for fam, vv in sorted(fams.items()):
        b, f = vv.get("base"), vv.get("flip")
        if b is None or f is None:
            all_flip = False
            details[fam] = {"error": "missing base/flip"}
            continue
        content_flips = (b["content_matches"] and f["content_matches"]
                         and b["content_owner"] != f["content_owner"])
        positional_flips = (b["positional_matches"] and f["positional_matches"]
                            and b["positional_owner"] != f["positional_owner"])
        details[fam] = dict(
            base_gold=b["gold"], flip_gold=f["gold"],
            content_base=b["content_owner"], content_flip=f["content_owner"],
            content_flips=content_flips,
            positional_base=b["positional_owner"], positional_flip=f["positional_owner"],
            positional_flips=positional_flips)
        all_flip = all_flip and content_flips
    return all_flip, details


def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())
    seed0 = per_seed[seeds[0]]
    mg = seed0["multigoal_rows"]
    full = seed0["full_rows"]

    # seed-invariance guard: boolean has_goal + theme signals must not vary across seeds.
    def _sig(ps):
        return tuple((r["id"], r["content_owner"], r["positional_owner"], r["scrambled_owner"])
                     for r in ps["multigoal_rows"]) + \
               tuple((r["id"], r["content_owner"], r["positional_owner"]) for r in ps["full_rows"])
    seed_invariant = all(_sig(per_seed[s]) == _sig(seed0) for s in seeds)

    # ---- multi-goal metrics ----
    content_acc = _acc(mg, "content_matches")
    positional_acc = _acc(mg, "positional_matches")
    scrambled_acc = _acc(mg, "scrambled_matches")
    base_accs = {
        "recency": _acc(mg, "recency_matches"),
        "first_mention": _acc(mg, "first_mention_matches"),
        "nearest_subject": _acc(mg, "nearest_subject_matches"),
        "majority": _acc(mg, "majority_matches"),
    }
    n_mg = len(mg)
    all_tie = all(r["both_goals_tie"] for r in mg)  # every multi-goal item MUST be a genuine tie
    # goal-scramble non-vacuous collapse: content beats the best baseline, scramble does not.
    best_base = max([v for v in list(base_accs.values()) + [positional_acc] if v is not None])
    gain_unscr = (content_acc - best_base) if content_acc is not None else None
    gain_scr = (scrambled_acc - best_base) if scrambled_acc is not None else None
    if gain_unscr is not None and gain_unscr > 1e-9:
        scramble_collapses = gain_scr is not None and gain_scr <= 0.5 * gain_unscr + 1e-9
        scramble_vacuous = False
    else:
        scramble_collapses = gain_scr is not None and gain_scr <= 1e-9
        scramble_vacuous = True
    content_beats_positional = (content_acc is not None and positional_acc is not None
                                and content_acc > positional_acc + 1e-9)
    flip_all, flip_details = _flip_control(mg)

    # ---- full-instrument metrics ----
    n_full = len(full)
    content_correct = {r["id"] for r in full if r["content_matches"]}
    positional_correct = {r["id"] for r in full if r["positional_matches"]}
    content_total = len(content_correct)
    positional_total = len(positional_correct)
    no_regression = positional_correct.issubset(content_correct)
    newly_fixed = sorted(content_correct - positional_correct)
    t24 = next((r for r in full if r["id"] == "t24_tom_boat_foil_sid"), None)
    t23 = next((r for r in full if r["id"] == "t23_laurie_hay_foil_tom"), None)
    t24_content_correct = bool(t24 and t24["content_matches"])
    t23_content_correct = bool(t23 and t23["content_matches"])
    n_ties_full = sum(1 for r in full if r["tie"])
    n_tiebreak_fired_full = sum(1 for r in full if r["tiebreak_fired"])

    # ---- HARD-PASS / HARD-FAIL ----
    hard_pass = bool(
        content_acc is not None and content_acc >= 11 / 12 - 1e-9
        and content_beats_positional and flip_all
        and scramble_collapses and not scramble_vacuous and all_tie
        and content_total == 48 and t24_content_correct and t23_content_correct
        and no_regression and positional_total == 47
    )
    hard_fail = bool(
        (content_acc is not None and positional_acc is not None and content_acc <= positional_acc + 1e-9)
        or not flip_all or content_total < 48 or not no_regression or scramble_vacuous or not all_tie
    )
    verdict = "HARD_FAIL" if hard_fail else ("HARD_PASS" if hard_pass else "MIDDLE_BAND")

    msg = (
        f"MULTI-GOAL (N={n_mg}, all_genuine_ties={all_tie}): content={content_acc} vs "
        f"positional_tiebreak={positional_acc} (beats={content_beats_positional}); "
        f"baselines={base_accs}; scramble={scrambled_acc} collapses={scramble_collapses} "
        f"vacuous={scramble_vacuous}; flip_control_all_families_flip={flip_all}. "
        f"FULL INSTRUMENT (N={n_full}): content_total={content_total}/48 "
        f"positional_total={positional_total}/48; t24_fixed={t24_content_correct} "
        f"(owner={t24['content_owner'] if t24 else None}); t23_correct={t23_content_correct}; "
        f"no_regression={no_regression}; newly_fixed={newly_fixed}; ties={n_ties_full} "
        f"tiebreak_fired={n_tiebreak_fired_full}; seed_invariant={seed_invariant}. VERDICT={verdict}.")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {msg}", summary=msg, n_seeds=len(seeds),
        multigoal=dict(n=n_mg, all_genuine_ties=all_tie, content_accuracy=content_acc,
                       positional_tiebreak_accuracy=positional_acc,
                       content_beats_positional=content_beats_positional,
                       scrambled_accuracy=scrambled_acc, scramble_collapses=scramble_collapses,
                       scramble_vacuous=scramble_vacuous, baselines=base_accs,
                       flip_control_all_flip=flip_all, flip_control_details=flip_details),
        full_instrument=dict(n=n_full, content_total=content_total, positional_total=positional_total,
                             no_regression=no_regression, newly_fixed=newly_fixed,
                             t24_content_correct=t24_content_correct, t24_owner=(t24 or {}).get("content_owner"),
                             t23_content_correct=t23_content_correct, n_ties=n_ties_full,
                             n_tiebreak_fired=n_tiebreak_fired_full,
                             content_correct=sorted(content_correct),
                             content_misses=sorted({r["id"] for r in full} - content_correct)),
        seed_invariant=seed_invariant, per_seed=per_seed,
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
        mg_c = _acc(res["multigoal_rows"], "content_matches")
        mg_p = _acc(res["multigoal_rows"], "positional_matches")
        ct = sum(1 for r in res["full_rows"] if r["content_matches"])
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"multigoal_content={mg_c} multigoal_positional={mg_p} full_content_total={ct}/48",
              flush=True)

    raw = load_units(OUTPUT_DIR)
    per_seed = {int(v["seed"]): v for v in raw.values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")

    agg = aggregate(per_seed)
    agg["arms_differ_verified"] = False
    agg["arms_differ_exempted"] = [("content_coherence_tiebreak_ON", "positional_tiebreak_OFF")]
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(
        seeds=SEEDS, multigoal_bank=MULTIGOAL_BANK_PATH,
        cardinality_ok=(len(per_seed) == EXPECTED_N_SEEDS),
        parent_organ="exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1 (commit b1b1ce460)",
        typer="hdlab.goal_typing.type_goal_events (PROMOTED, wire-dont-island)",
        scorer="hdlab.goal_owner_select.directed_goal_outcome_score (PROMOTED, unmodified)",
        tiebreak="content-coherence: goal-theme vs outcome-theme head-noun overlap among tied "
                 "goal-holders; fires only on unique overlapper, else sorted-order fallback")
    agg["final_metrics_atomicity"] = "tmp_replace"
    agg["crlb_n/a"] = "boolean owner-selection accuracy (theme-overlap tie-break), not an SNR regime"
    agg["deterministic_seeding"] = True
    agg["prereg"] = "inline (docstring, LOCAL-ONLY task brief; no separate preregs/ file)"
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    mg = load_multigoal()
    assert len(mg) == 12, f"expected 12 multi-goal items, got {len(mg)}"
    fams = sorted(set(r["family"] for r in mg))
    assert len(fams) == 6, f"expected 6 families, got {fams}"
    for fam in fams:
        variants = sorted(r["variant"] for r in mg if r["family"] == fam)
        assert variants == ["base", "flip"], f"family {fam} variants {variants}"
    print(f"[SELFTEST 1/8] multi-goal bank: 12 items, 6 families x (base,flip)", flush=True)

    # (2) THEME extraction is exact on the decisive clauses (t24 + one multi-goal family).
    t24 = None
    core_ai, _tw = PARENT.PREVMOD.load_bank("action_implied")
    t24 = next(it for it in core_ai if it["id"] == "t24_tom_boat_foil_sid")
    gt24 = entity_goal_themes(t24)
    out24 = clause_theme(_sentences(t24["text"])[-1], t24["roster"])
    assert gt24.get("tom") == {"oars", "boat", "tide"}, f"t24 tom goal-theme wrong: {gt24.get('tom')}"
    assert gt24.get("sid") == {"rope"}, f"t24 sid goal-theme wrong: {gt24.get('sid')}"
    assert out24 == {"tools", "boat"}, f"t24 outcome-theme wrong: {out24}"
    assert (gt24["tom"] & out24) == {"boat"} and not (gt24["sid"] & out24), "t24 overlap not decisive"
    print(f"[SELFTEST 2/8] t24 themes: tom={sorted(gt24['tom'])} sid={sorted(gt24['sid'])} "
          f"outcome={sorted(out24)} -> unique overlapper=tom", flush=True)

    # (3) t24 is a genuine directed-score TIE, and the content tie-break FIXES it to tom.
    scored24 = score_candidates(t24, seed=0)
    assert scored24 == {"sid": 1.0, "tom": 1.0}, f"t24 must tie both 1.0: {scored24}"
    owner24, _s, tie24, fired24 = enumerate_and_select_coherence(t24, seed=0, theme_off=False)
    assert tie24 and fired24 and owner24 == "tom", f"t24 tie-break must select tom: {owner24} tie={tie24} fired={fired24}"
    pos24, _s2, _t2, _f2 = enumerate_and_select_coherence(t24, seed=0, theme_off=True)
    assert pos24 == "sid", f"t24 positional (sorted-order) must be the OLD wrong pick sid: {pos24}"
    print(f"[SELFTEST 3/8] t24 scored={scored24} -> content=tom (FIXED), positional=sid (old miss)",
          flush=True)

    # (4) t23 (the other genuine tie) stays right via FALLBACK (neither goal-theme overlaps outcome).
    core_ai2, _tw2 = PARENT.PREVMOD.load_bank("action_implied")
    t23 = next(it for it in core_ai2 if it["id"] == "t23_laurie_hay_foil_tom")
    gt23 = entity_goal_themes(t23)
    out23 = clause_theme(_sentences(t23["text"])[-1], t23["roster"])
    assert not (gt23.get("laurie", set()) & out23) and not (gt23.get("tom", set()) & out23), \
        f"t23 must be non-discriminating for theme: laurie={gt23.get('laurie')} tom={gt23.get('tom')} out={out23}"
    owner23, _s3, tie23, fired23 = enumerate_and_select_coherence(t23, seed=0, theme_off=False)
    assert tie23 and not fired23 and owner23 == t23["gold_outcome_owner"], \
        f"t23 must fall back to sorted-order (laurie), tie-break NOT fired: {owner23} fired={fired23}"
    print(f"[SELFTEST 4/8] t23 themes non-decisive -> fallback sorted-order=laurie (unchanged, "
          f"tiebreak_fired={fired23})", flush=True)

    # (5) every multi-goal item is a genuine tie AND content picks the gold owner (12/12).
    n_tie = n_content = n_pos = 0
    for it in mg:
        sc = score_candidates(it, seed=0)
        c_owner, _sc, tie, fired = enumerate_and_select_coherence(it, seed=0, theme_off=False)
        p_owner, _sc2, _t, _f = enumerate_and_select_coherence(it, seed=0, theme_off=True)
        assert len(set(sc.values())) == 1 and list(sc.values())[0] == 1.0, \
            f"{it['id']}: both entities must hold a goal (tie at 1.0): {sc}"
        n_tie += int(tie)
        n_content += int(c_owner == it["gold_outcome_owner"])
        n_pos += int(p_owner == it["gold_outcome_owner"])
    assert n_tie == 12, f"all 12 multi-goal items must be genuine ties, got {n_tie}"
    assert n_content == 12, f"content-coherence must be 12/12 on multi-goal, got {n_content}"
    print(f"[SELFTEST 5/8] multi-goal: ties={n_tie}/12, content={n_content}/12, "
          f"positional={n_pos}/12 (positional expected 6/12 == chance)", flush=True)

    # (6) FLIP-control: within each family the content pick FLIPS base<->flip; positional cannot flip.
    flip_all, details = _flip_control([run_item_multigoal(it, 0) for it in mg])
    assert flip_all, f"flip-control failed: {json.dumps(details, indent=2, default=str)}"
    print(f"[SELFTEST 6/8] flip-control: all 6 families flip under content-coherence "
          f"(positional flips only by luck)", flush=True)

    # (7) GOAL-SCRAMBLE collapses on a multi-goal item (pick -> foil, wrong).
    it0 = mg[0]
    s_owner, _ss, _st, _sf = enumerate_and_select_coherence(
        it0, seed=0, scramble_goal_to_foil=it0["foil"], theme_off=False)
    assert s_owner == it0["foil"] and s_owner != it0["gold_outcome_owner"], \
        f"goal-scramble must collapse the pick to the foil: {s_owner}"
    print(f"[SELFTEST 7/8] goal-scramble on {it0['id']}: pick->foil={s_owner} (non-vacuous collapse)",
          flush=True)

    # (8) FULL instrument = 48 items; content 48/48; positional 47/48; no regression.
    full = run_full_instrument(0)
    assert len(full) == 48, f"full instrument must be 48 items, got {len(full)}"
    cc = {r["id"] for r in full if r["content_matches"]}
    pc = {r["id"] for r in full if r["positional_matches"]}
    assert len(cc) == 48, f"content must be 48/48, got {len(cc)}; misses={sorted({r['id'] for r in full}-cc)}"
    assert len(pc) == 47 and pc.issubset(cc), f"positional must be 47/48 subset of content: {len(pc)}"
    assert (cc - pc) == {"t24_tom_boat_foil_sid"}, f"only t24 must be newly-fixed: {sorted(cc-pc)}"
    print(f"[SELFTEST 8/8] full instrument: content={len(cc)}/48 positional={len(pc)}/48 "
          f"newly_fixed={sorted(cc-pc)} no_regression=True", flush=True)
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
