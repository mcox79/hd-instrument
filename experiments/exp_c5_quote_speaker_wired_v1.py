"""exp_c5_quote_speaker_wired_v1 -- WIRE THE OWNED QUOTATIVE ORGAN into C-F outcome-subject
resolution: does routing the naive-splitter's subject=None fallback (on quote-fractured dialogue
fragments) through hdlab.coreference_resolver's quotative-attribution mechanism (_detect_speaker /
_SPEECH_VERBS, the core of run_principle_b_deixis's enrich_dialogue, promoted 2026-08-02) shrink the
TYPING_MISS bucket on the 38-item C3-mined bank (baseline commit dfabbde26 / re-verified this cell:
failure_decomposition={OWNER_ID_ERROR:7, TYPING_MISS:14, BINDING_ERROR:5, CORRECT:12}, e2e=12/38=0.3158)?

WHY (per notes/director_POST_COMPACTION_BACKUP_2026-08-04.md "C-F goal-owner PAYOFF = HONEST
NEGATIVE" + commit 9317c0c06): spot-checking the 14 TYPING_MISS items found the dominant cause is
NOT OOV verbs or a missing outcome-valence axis (both wired + measured, unchanged 14->14) -- it is
that _sentences() (re.split on [.!?]) FRACTURES quoted dialogue ('"...glad...!" she cried.' splits
into '"...glad' and '" she cried') so the outcome-cue-bearing fragment's subject_entity() call finds
no roster name/pronoun in its own truncated text and returns None, dropping the OUTCOME event even
though the goal_verb itself typed fine. Standing rule (WIRE-DON'T-ISLAND): we OWN a quotative
speaker-attribution organ (hdlab/coreference_resolver.py _detect_speaker + _SPEECH_VERBS, the
regex-based "said NAME" / "NAME said" quotative-tag detector that enrich_dialogue/run_principle_b_
deixis's clause_speaker field is built from) -- route outcome-subject resolution through it instead
of building a new segmenter.

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `tools/substrate_query.sh "quotative
speaker attribution outcome subject resolution quoted dialogue goal owner"` -- top hits (cosine
0.32-0.38) are exp_quotative_speaker_attribution_stack_break050_v1 (the SAME arc's own owned
quotative organ this cell reuses, already cited by the backup doc, not a rediscovery) and the
generic WordNet "quotation" atom. No prior cell performs THIS specific wiring (outcome-subject
resolution on the C3-mined goal-owner bank) -- genuinely novel within the arc, reuses cited prior
art with credit, not a rediscovery.

STEP 1 -- CATEGORIZE ALL 14 TYPING_MISS ITEMS BY CAUSE (honest ceiling before claiming a fix, per
task contract #1): a diagnostic-only pass (does not mutate the measured pipeline) walks each item's
_sentences() fragments with the OLD (unmodified) resolver+typing, and classifies:
  (a) OUTCOME-cue-in-QUOTED-dialogue-fractured: >=1 fragment fires an OUTCOME cue (has_unmet/
      has_met) with subject=None AND that fragment touches a quote character ('"'/U+201C/U+201D) --
      speaker-attributable in principle, the wire's intended target.
  (b) outcome cue present, subject None, but NO quote character on the firing fragment -- a
      different segmentation/subject-resolution gap (e.g. generic-noun subject "the stranger", or a
      non-quote-marked reported-speech construction like "A voice cried ... : --All in") -- the
      quotative-quote-gate cannot fire here by design (no quote punctuation to gate on).
  (c) NO outcome cue anywhere in the item (has_outcome_any=False) -- a lexicon/axis gap, orthogonal
      to subject resolution entirely.
  (d) GOAL-side miss (has_goal_any=False) -- would take priority over (a)/(b)/(c) if it occurred;
      MEASURED to be 0/14 on this bank (every item's mined goal_verb already fires PSYCH_VERBS by
      construction of the C3 miner's own selection filter, see exp_c5_realtext_c3mined_v1.py).

STEP 2 -- THE WIRE (build_positions_c3_quotewired / _quote_speaker_fallback below): when
resolver.subject_entity(sent) returns None for a sentence fragment that touches a quote character,
search neighboring fragments (forward first -- attribution conventionally trails the quote, e.g.
'"..." she cried.' -- then backward, window=3) for one carrying a QUOTATIVE speech-verb (reusing
hdlab.coreference_resolver._SPEECH_VERBS, the exact lexicon _detect_speaker itself scans -- not a
new lexicon). On a hit, resolve the speaker's IDENTITY via two tiers, BOTH already-owned mechanisms:
  tier 1 -- hdlab.coreference_resolver._detect_speaker's own NAME-adjacency regex ("said NAME" /
    "NAME said"), checked against the item roster.
  tier 2 -- the SAME resolver.subject_entity already used everywhere in this pipeline, applied to
    the quotative-tagged neighbor fragment instead of the cue-bearing fragment -- resolves a PRONOUN
    speaker tag ("she cried") via the resolver's own backward-search antecedent tracking (no new
    pronoun-resolution code).
GOAL typing is left untouched (type_sentence_events_c3 imported bit-identical from
exp_c5_realtext_c3mined_v1.py, unmodified) -- the ONE variable is which subject value gets passed
into it when the naive split would otherwise pass None on a quote-touching fragment.

CONTRACT / PRE-REGISTERED BANDS (per task brief #4):
  HARD-PASS: TYPING_MISS shrinks by ~the count of category-(a) items AND e2e > 0.3158, with the
    ablation (OLD arm, unmodified build_positions_c3) reproducing the exact {7,14,5,12} baseline.
  PARTIAL: category-(a) items get typed (subject resolves) but the resolved subject does not match
    gold_outcome_owner (moves TYPING_MISS -> BINDING_ERROR, not CORRECT) -- routes to the BINDING
    bucket (a different, already-known component) rather than the TYPING bucket.
  HARD-FAIL: category-(a) items are NOT fixed (subject stays None) -- drilled per-item below: is the
    quotative organ firing on these quote spans (gate fires)? is the extracted speaker resolvable to
    a roster entity (identity tier succeeds)?

GUARDS: glass-box; deterministic; ASCII-only; atomic metrics write (os.replace); LOCAL-ONLY,
in-process foreground, no push, no queue dispatch; no silent except (outer try/except re-raises
after writing CELL_CRASHED diagnostic); no modification to hdlab/coreference_resolver.py,
exp_c5_realtext_c3mined_v1.py, exp_c5_realtext_c3mined_v2_38item_v1.py, or hdlab/goal_owner_select.py
(reused bit-identical via import only).
"""
from __future__ import annotations

import json
import os
import re
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ANCHOR_NAME = "c5_quote_speaker_wired_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "metrics.json")

# ---- REUSED BIT-IDENTICAL: OLD typing/resolution pipeline (the baseline-to-beat) ------------------
from exp_c5_realtext_c3mined_v1 import (  # noqa: E402
    MINED_PATH, _load_mined, type_sentence_events_c3, build_positions_c3 as build_positions_c3_OLD,
    run_item as run_item_OLD, _build_c5_item, GeneralRecencyEntityResolver, ContentMatchResolver,
    R_GOAL, R_UNMET, R_MET,
)
import exp_c5_realtext_c3mined_v1 as _v1  # noqa: E402 (module-level GENDER_PATCH override target)
# ---- REUSED BIT-IDENTICAL: owner-correctness + extended gender patch (v2's agent-verified work) ---
from exp_c5_realtext_c3mined_v2_38item_v1 import OWNER_WRONG_IDS, GENDER_PATCH  # noqa: E402
_v1.GENDER_PATCH = GENDER_PATCH  # _build_c5_item (imported above) reads this at call time
# ---- REUSED BIT-IDENTICAL: promoted Component-5 organ + adoption gate ------------------------------
from hdlab.goal_owner_select import directed_goal_outcome_score  # noqa: E402
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402
# ---- REUSED BIT-IDENTICAL: sentence/token plumbing ------------------------------------------------
from exp_situation_model_goal_outcome_dimension_v1 import _sentences, _ordered_tokens  # noqa: E402
# ---- THE OWNED QUOTATIVE ORGAN (hdlab/coreference_resolver.py, promoted 2026-08-02) ---------------
from hdlab.coreference_resolver import _detect_speaker, _SPEECH_VERBS  # noqa: E402

_QUOTE_CHARS = ('"', "“", "”")
_SPEECH_VERB_RE = re.compile(r"\b(?:" + _SPEECH_VERBS + r")\b")


def _has_quote_char(fragment: str) -> bool:
    return any(c in fragment for c in _QUOTE_CHARS)


# ============================================================================ THE WIRE
def _quote_speaker_fallback(resolver, frags: list, idx: int, window: int = 3):
    """Reuse of the OWNED quotative-attribution organ to resolve the subject of a sentence-fragment
    the naive _sentences() splitter left subject-less, when that fragment touches a quote character
    (a fractured-dialogue signature). See module docstring STEP 2 for the two-tier identity
    resolution. Returns (subject_or_None, gate_fired: bool) -- gate_fired distinguishes "quote-gate
    fired but no speaker resolvable" from "quote-gate never fired" for honest per-item reporting."""
    frag = frags[idx]
    if not _has_quote_char(frag):
        return None, False
    roster = getattr(resolver, "_roster", {})
    order = (list(range(idx + 1, min(len(frags), idx + 1 + window))) +
             list(range(idx - 1, max(-1, idx - 1 - window), -1)))
    for j in order:
        nb = frags[j]
        if not _SPEECH_VERB_RE.search(nb.lower()):
            continue  # not a quotative-tagged neighbor -- skip (reuses _SPEECH_VERBS as the gate)
        name = _detect_speaker(nb)  # tier 1: owned NAME-adjacency regex
        if name and name.lower() in roster:
            return name.lower(), True
        subj2 = resolver.subject_entity(nb)  # tier 2: resolver's own pronoun backward-search
        if subj2 is not None:
            return subj2, True
    return None, True


def build_positions_c3_quotewired(item: dict, resolver, scramble_owner_to_foil: str | None = None):
    """Mirrors exp_c5_realtext_c3mined_v1.build_positions_c3 exactly (same resolver-driven subject
    walk, same role-scramble semantics), BUT scopes the quote-speaker wire to OUTCOME events ONLY
    (R_UNMET/R_MET), per task contract "one variable = outcome-subject resolution on quotes" --
    GOAL typing must stay bit-identical to OLD. This matters in practice: an early version of this
    cell applied the wire's fallback subject uniformly (same subject value fed into
    type_sentence_events_c3 for GOAL and OUTCOME alike), which caused a measured REGRESSION on
    c3_113_the_secret_garden__s32 (12/38 -> 11/38): the wire correctly resolved a quote-fractured
    "she cried" fragment's speaker (Sahib), but that fragment ALSO carried a psych-verb ("I know I
    ought") that would previously have been silently dropped (subject=None), and newly typing it as
    a SECOND GOAL event (Sahib, competing with Mary's real goal) changed the C5 selection organ's
    adoption decision and flipped a previously-CORRECT item to BINDING_ERROR. Fixed here by typing
    GOAL only against the ORIGINAL (un-wired) subject and OUTCOME only against the wire-resolved
    subject, so a fragment's GOAL-eligibility can never change due to the wire."""
    owner = item.get("owner")
    role_seq, cluster_ids = [], []
    diag_rows = []
    frags = _sentences(item["text"])
    for idx, sent in enumerate(frags):
        orig_subj = resolver.subject_entity(sent)
        outcome_subj = orig_subj
        quote_gate_fired = quote_wire_used = False
        if orig_subj is None:
            fixed, gate_fired = _quote_speaker_fallback(resolver, frags, idx)
            quote_gate_fired = gate_fired
            if fixed is not None:
                outcome_subj = fixed
                quote_wire_used = True
        # cue detection (has_desire/has_unmet/has_met) is subject-independent inside
        # type_sentence_events_c3 -- call once (subject=None) purely to read the flags, bit-
        # identical cue lexicon/logic to OLD, then build events with the PER-ROLE subject below.
        _, info = type_sentence_events_c3(sent, None)
        info["quote_gate_fired"] = quote_gate_fired
        info["quote_wire_used"] = quote_wire_used
        info["subject"] = outcome_subj
        diag_rows.append(info)
        ev = []
        if info["has_desire"] and orig_subj is not None:
            ev.append((orig_subj, R_GOAL))
        if info["has_unmet"] and outcome_subj is not None:
            ev.append((outcome_subj, R_UNMET))
        if info["has_met"] and outcome_subj is not None:
            ev.append((outcome_subj, R_MET))
        for (entity, role) in ev:
            eff_entity = entity
            if scramble_owner_to_foil is not None and role == R_GOAL and entity == owner:
                eff_entity = scramble_owner_to_foil
            role_seq.append(role)
            cluster_ids.append(eff_entity)
            if hasattr(resolver, "mark_role"):
                resolver.mark_role(eff_entity, role)
    event_slots = list(range(len(role_seq)))
    return role_seq, cluster_ids, event_slots, diag_rows


def run_item_quotewired(item, scrambled: bool = False):
    """Mirrors exp_c5_realtext_c3mined_v1.run_item exactly, using build_positions_c3_quotewired for
    both resolver candidates (GeneralRecencyEntityResolver / ContentMatchResolver) -- same contract,
    C5 selection organ (directed_goal_outcome_score / decide_keep_or_revert) reused bit-identical."""
    roster = item["roster"]
    rs_b, cid_b, es_b, diag_b = build_positions_c3_quotewired(item, GeneralRecencyEntityResolver(roster))
    foil = item.get("foil")
    scramble_target = foil if (scrambled and foil) else None
    rs_c, cid_c, es_c, diag_c = build_positions_c3_quotewired(
        item, ContentMatchResolver(roster), scramble_owner_to_foil=scramble_target)
    quote_wire_used_any = any(d.get("quote_wire_used") for d in diag_b)
    if rs_b != rs_c or es_b != es_c:
        return dict(id=item["id"], scrambled=scrambled, typed=False,
                    reason="role_seq_diverged_between_resolvers", quote_wire_used_any=quote_wire_used_any)
    outcome_positions = [i for i, r in enumerate(rs_b) if r in (R_UNMET, R_MET)]
    goal_positions = [i for i, r in enumerate(rs_b) if r == R_GOAL]
    if not outcome_positions or not goal_positions:
        return dict(id=item["id"], scrambled=scrambled, typed=False,
                    reason="no_goal_or_outcome_event_typed",
                    n_goal=len(goal_positions), n_outcome=len(outcome_positions), role_seq=rs_b,
                    quote_wire_used_any=quote_wire_used_any)
    outcome_pos = outcome_positions[-1]
    score_b = directed_goal_outcome_score(rs_b, cid_b, 0, outcome_pos)
    score_c = directed_goal_outcome_score(rs_c, cid_c, 0, outcome_pos)
    delta = score_c - score_b
    adopt = decide_keep_or_revert({"content_match": delta}, ABSTAIN_BAND_DEFAULT)
    adopted = cid_c if adopt == "content_match" else cid_b
    final_owner = adopted[outcome_pos]
    baseline_owner = cid_b[outcome_pos]
    gold = item["gold_outcome_owner"]
    return dict(id=item["id"], scrambled=scrambled, typed=True, matches_gold=(final_owner == gold),
                recency_alone_matches_gold=(baseline_owner == gold), final_owner=final_owner,
                baseline_owner=baseline_owner, content_owner=cid_c[outcome_pos], gold=gold, foil=foil,
                adopt=adopt, score_b=score_b, score_c=score_c, delta=delta, role_seq=rs_b,
                quote_wire_used_any=quote_wire_used_any)


# ============================================================================ failure decomposition
def _decompose(all_ids: list, results: dict) -> dict:
    decomp = dict(OWNER_ID_ERROR=0, TYPING_MISS=0, BINDING_ERROR=0, CORRECT=0)
    for mid in all_ids:
        r = results[mid]
        owner_correct = mid not in OWNER_WRONG_IDS
        if not owner_correct:
            decomp["OWNER_ID_ERROR"] += 1
        elif not r["typed"]:
            decomp["TYPING_MISS"] += 1
        elif not r["matches_gold"]:
            decomp["BINDING_ERROR"] += 1
        else:
            decomp["CORRECT"] += 1
    assert sum(decomp.values()) == len(all_ids), f"decomposition does not sum to {len(all_ids)}: {decomp}"
    return decomp


# ============================================================================ STEP 1 categorization
def _categorize_typing_miss(mined: dict, mid: str) -> dict:
    """Diagnostic-only (does not feed the measured pipeline): walks the item's _sentences() fragments
    with the OLD resolver+typing to classify the TYPING_MISS cause per module docstring STEP 1
    (a/b/c/d). Uses a FRESH GeneralRecencyEntityResolver mirroring build_positions_c3's own walk
    exactly (same subject-resolution order) so the diagnosis matches what the measured OLD arm
    actually saw."""
    item = _build_c5_item(mined[mid])
    roster = item["roster"]
    resolver = GeneralRecencyEntityResolver(roster)
    frags = _sentences(item["text"])
    has_goal_any = False
    has_outcome_any = False
    outcome_none_subj_quote = False   # >=1 outcome-cue fragment: subject None AND touches a quote char
    outcome_none_subj_noquote = False  # >=1 outcome-cue fragment: subject None, no quote char
    for sent in frags:
        subj = resolver.subject_entity(sent)
        ev, info = type_sentence_events_c3(sent, subj)
        if info["has_desire"]:
            has_goal_any = True
        if info["has_unmet"] or info["has_met"]:
            has_outcome_any = True
            if subj is None:
                if _has_quote_char(sent):
                    outcome_none_subj_quote = True
                else:
                    outcome_none_subj_noquote = True
        if hasattr(resolver, "mark_role"):
            for (entity, role) in ev:
                resolver.mark_role(entity, role)
    if not has_goal_any:
        cause = "d_goal_side_miss"
    elif not has_outcome_any:
        cause = "c_no_outcome_cue_in_item"
    elif outcome_none_subj_quote:
        cause = "a_outcome_cue_in_quoted_dialogue_fractured"
    elif outcome_none_subj_noquote:
        cause = "b_outcome_cue_present_not_in_quote_other_segmentation"
    else:
        cause = "OTHER_unclassified"  # honest fallback; should not occur given the branches above
    return dict(cause=cause, has_goal_any=has_goal_any, has_outcome_any=has_outcome_any,
                outcome_none_subj_quote=outcome_none_subj_quote,
                outcome_none_subj_noquote=outcome_none_subj_noquote)


def self_test():
    """Pre-flight smoke: (1) mined file + OWNER_WRONG_IDS cross-check; (2) OLD-arm ablation
    reproduces the exact baseline {OWNER_ID_ERROR:7, TYPING_MISS:14, BINDING_ERROR:5, CORRECT:12}
    (mandatory make-or-break gate before trusting the quote-wired delta); (3) the quote-wire fires
    (gate_fired=True, subject resolves) on a synthetic fractured-quote sentence with a NAME-tagged
    speaker (arms-must-differ, non-vacuous); (4) the wire correctly ABSTAINS (gate never fires) on a
    non-quoted sentence, proving it is gated on quote-touching fragments only, not a blanket
    subject-recovery hack."""
    mined_list = _load_mined()
    mined = {it["id"]: it for it in mined_list}
    assert len(mined) == 38, f"expected 38 mined items, got {len(mined)}"
    n_correct = len(mined) - len(OWNER_WRONG_IDS)
    assert n_correct == 31, f"expected 31 owner-correct (reused from v2), got {n_correct}"

    all_ids = list(mined.keys())
    results_old = {}
    for mid in all_ids:
        item = _build_c5_item(mined[mid])
        results_old[mid] = run_item_OLD(item, scrambled=False)
    decomp_old = _decompose(all_ids, results_old)
    EXPECTED_OLD = dict(OWNER_ID_ERROR=7, TYPING_MISS=14, BINDING_ERROR=5, CORRECT=12)
    assert decomp_old == EXPECTED_OLD, (
        f"OLD-arm ablation must reproduce the exact baseline before the quote-wire delta is "
        f"trustworthy: got {decomp_old}, expected {EXPECTED_OLD}")

    # (3) synthetic fractured-quote smoke: NAME-tagged speaker resolves via tier 1.
    roster = {"mary": "f", "john": "m"}
    resolver = GeneralRecencyEntityResolver(roster)
    frags = _sentences('John walked in. "I am so glad!" said Mary. She smiled.')
    # frags[0]="John walked in", frags[1]='"I am so glad', frags[2]='" said Mary', frags[3]="She smiled"
    subj0 = resolver.subject_entity(frags[0])
    assert subj0 == "john"
    resolver.subject_entity(frags[1])  # advances resolver state exactly as build_positions_c3 would
    fixed, gate_fired = _quote_speaker_fallback(resolver, frags, 1)
    assert gate_fired is True, "quote gate must fire on a fragment touching a quote char"
    assert fixed == "mary", f"tier-1 NAME-adjacency must resolve 'said Mary' -> mary, got {fixed!r}"

    # (4) non-quoted fragment: gate must NOT fire (honest scope, not a blanket None->guess hack).
    fixed2, gate2 = _quote_speaker_fallback(resolver, frags, 0)
    assert gate2 is False, "quote gate must abstain on a fragment with no quote character"
    assert fixed2 is None

    ok_id = "c3_1342_pride_and_prejudice__s30"
    item_ok = _build_c5_item(mined[ok_id])
    res_ok = run_item_quotewired(item_ok, scrambled=False)
    assert "typed" in res_ok, f"run_item_quotewired did not return a typed field: {res_ok}"

    print(f"[SELFTEST PASS] OLD-arm ablation reproduces exact baseline {decomp_old}; quote-wire "
          f"gate fires on quote-touching fragments (tier-1 NAME resolves 'said Mary'->mary) and "
          f"abstains on non-quoted fragments; quote-wired pipeline runs end-to-end on {ok_id} "
          f"(typed={res_ok['typed']})", flush=True)
    return True


def main():
    mined_list = _load_mined()
    mined = {it["id"]: it for it in mined_list}
    assert len(mined) == 38, f"expected 38 mined items on disk, got {len(mined)}"
    all_ids = list(mined.keys())

    results_old, results_quotewired = {}, {}
    for mid in all_ids:
        mined_item = mined[mid]
        item = _build_c5_item(mined_item)
        r_old = run_item_OLD(item, scrambled=False)
        r_old["structure_type"] = mined_item.get("structure_type")
        results_old[mid] = r_old
        r_qw = run_item_quotewired(item, scrambled=False)
        r_qw["structure_type"] = mined_item.get("structure_type")
        results_quotewired[mid] = r_qw
        print(f"[quote-wire] {mid}: old_typed={r_old['typed']} old_match={r_old.get('matches_gold')} "
              f"| qw_typed={r_qw['typed']} qw_match={r_qw.get('matches_gold')} "
              f"quote_wire_used={r_qw.get('quote_wire_used_any')}", flush=True)

    decomp_old = _decompose(all_ids, results_old)
    decomp_qw = _decompose(all_ids, results_quotewired)
    assert decomp_old == dict(OWNER_ID_ERROR=7, TYPING_MISS=14, BINDING_ERROR=5, CORRECT=12), (
        f"OLD-arm ablation drifted from the cited baseline: {decomp_old}")

    acc_old = round(decomp_old["CORRECT"] / 38, 4)
    acc_qw = round(decomp_qw["CORRECT"] / 38, 4)
    typing_miss_delta = decomp_old["TYPING_MISS"] - decomp_qw["TYPING_MISS"]

    old_typing_miss_ids = [mid for mid in all_ids
                           if mid not in OWNER_WRONG_IDS and not results_old[mid]["typed"]]
    assert len(old_typing_miss_ids) == 14

    # STEP 1: categorize all 14 by cause (independent of the wire's own run, diagnostic pass).
    categorization = {mid: _categorize_typing_miss(mined, mid) for mid in old_typing_miss_ids}
    cause_counts = dict(Counter(c["cause"] for c in categorization.values()))
    category_a_ids = [mid for mid, c in categorization.items()
                       if c["cause"] == "a_outcome_cue_in_quoted_dialogue_fractured"]

    # per-category-(a)-item outcome under the wire: did it get typed? bound correctly? why not?
    category_a_outcomes = {}
    for mid in category_a_ids:
        r_qw = results_quotewired[mid]
        r_old = results_old[mid]
        if r_qw["typed"] and r_qw.get("matches_gold"):
            status = "FIXED_TYPED_AND_CORRECT"
        elif r_qw["typed"] and not r_qw.get("matches_gold"):
            status = "TYPED_BUT_WRONG_SPEAKER_BINDING_ERROR"
        elif r_qw.get("quote_wire_used_any"):
            status = "GATE_FIRED_BUT_STILL_UNTYPED_other_position_missing"
        else:
            status = "GATE_NEVER_FIRED_OR_SPEAKER_UNRESOLVABLE"
        category_a_outcomes[mid] = dict(
            status=status, old_typed=r_old["typed"], qw_typed=r_qw["typed"],
            qw_matches_gold=r_qw.get("matches_gold"), quote_wire_used_any=r_qw.get("quote_wire_used_any"),
            gold=mined[mid].get("goal_owner"),
        )

    n_category_a_fixed_typed = sum(1 for v in category_a_outcomes.values() if v["qw_typed"])
    n_category_a_fixed_correct = sum(
        1 for v in category_a_outcomes.values() if v["status"] == "FIXED_TYPED_AND_CORRECT")

    # PRE-REGISTERED VERDICT
    n_cat_a = len(category_a_ids)
    typing_miss_shrinks_by_cat_a = (typing_miss_delta >= max(1, n_cat_a - 1)) if n_cat_a else False
    beats_old_e2e = acc_qw > acc_old
    if n_cat_a == 0:
        verdict = "NO_CATEGORY_A_ITEMS_WIRE_UNTESTABLE_ON_THIS_BANK"
    elif n_category_a_fixed_correct > 0 and typing_miss_shrinks_by_cat_a and beats_old_e2e:
        verdict = "HARD_PASS_CATEGORY_A_FIXED_E2E_IMPROVES"
    elif n_category_a_fixed_typed > 0:
        verdict = "PARTIAL_CATEGORY_A_TYPES_BUT_GATED_BY_ANOTHER_BUCKET"
    else:
        verdict = "HARD_FAIL_CATEGORY_A_NOT_FIXED"

    verdict_msg = (
        f"MEASURED quote-speaker wire (38 items): OLD e2e={acc_old} ({decomp_old['CORRECT']}/38) "
        f"decomp={decomp_old} | QUOTEWIRED e2e={acc_qw} ({decomp_qw['CORRECT']}/38) decomp={decomp_qw} "
        f"| TYPING_MISS delta={typing_miss_delta} (14 -> {decomp_qw['TYPING_MISS']}) | "
        f"14-item cause_counts={cause_counts} | category(a) n={n_cat_a} ids={category_a_ids} | "
        f"category(a) fixed_typed={n_category_a_fixed_typed} fixed_correct={n_category_a_fixed_correct} "
        f"| verdict={verdict}")

    metrics = dict(
        anchor_name=ANCHOR_NAME, n_items=38, n_owner_correct=31, n_owner_wrong=7,
        old_baseline=dict(failure_decomposition=decomp_old, end_to_end_accuracy=acc_old,
                          cites="data/exp_c5_realtext_c3mined_v2_38item_v1/metrics.json commit dfabbde26"),
        quotewired_run=dict(failure_decomposition=decomp_qw, end_to_end_accuracy=acc_qw),
        typing_miss_delta=typing_miss_delta,
        old_typing_miss_ids=old_typing_miss_ids,
        typing_miss_cause_categorization=categorization,
        typing_miss_cause_counts=cause_counts,
        category_a_ids=category_a_ids,
        category_a_outcomes=category_a_outcomes,
        n_category_a_fixed_typed=n_category_a_fixed_typed,
        n_category_a_fixed_correct=n_category_a_fixed_correct,
        typing_miss_shrinks_by_cat_a_band=typing_miss_shrinks_by_cat_a,
        beats_old_end_to_end=beats_old_e2e,
        verdict=verdict, verdict_msg=verdict_msg,
        per_item_old={mid: results_old[mid] for mid in all_ids},
        per_item_quotewired={mid: results_quotewired[mid] for mid in all_ids},
        n=38, small_n=True, elapsed_s=0.0,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        prereg_note=(
            "MEASUREMENT/wiring cell; bands: HARD-PASS=category-(a) items fixed (typed+correct) AND "
            "TYPING_MISS shrinks by ~count(category-a) AND e2e>0.3158; PARTIAL=category-(a) types but "
            "another bucket (BINDING) gates; HARD-FAIL=category-(a) not fixed. Categorization (STEP 1) "
            "is a diagnostic-only pass over the OLD (unmodified) pipeline's per-fragment info, disk-"
            "verifiable independent of the wire's own run."
        ),
        source_mined_path=MINED_PATH,
    )
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = OUTPUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, OUTPUT_PATH)
    print(f"[VERDICT] {verdict_msg}", flush=True)
    return metrics


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            raise SystemExit(0 if self_test() else 1)
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        tmp = OUTPUT_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            json.dump(dict(
                verdict="CELL_CRASHED", verdict_msg=f"{type(e).__name__}: {str(e)[:500]}",
                summary=f"CELL_CRASHED: {type(e).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(),
                anchor_name=ANCHOR_NAME,
            ), f, indent=2)
        os.replace(tmp, OUTPUT_PATH)
        raise
