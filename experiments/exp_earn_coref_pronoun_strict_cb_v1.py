"""STEP 2 RE-ATTEMPT (strict Cb / literal Centering pronoun coref), 2026-08-02.

Design pointer: notes/step2_pronoun_coref_centering_role_prominence_design_2026-08-02.md
Prior attempt (NULL): exp_earn_coref_pronoun_centering_v1.py (commit 5639fe312) -- a BLENDED
role-prominence term (+0.3*prominence(last_role), same weight for every "agent") added to the
existing frequency+recency salience. Diagnosis: n_role_flips=1/18 passages; on the hard cases ALL
candidate antecedents were role=agent (turn-taking narration -- "Robert said X. Willie said Y. He
said Z.") so the blended prominence term is TIED across candidates and never discriminates. A
weight sweep only made things worse (the additive blend can't express "immediate-clause identity
beats everything else", only "shift the tie-break a little").

THE FIX (this cell): literal Centering (Grosz/Joshi/Weinstein) is NOT a blended salience term --
Cb (the backward-looking center) is a HARD PREFERENCE for the most grammatically prominent entity
of the immediately preceding clause, with explicit fallback tiers, not an additive score. This
cell replaces the blend with a strict tiered rule on the PRONOUN branch only (name/nominal branch
byte-identical to run_learnable, per the opt-in/never-mutate-baseline contract):

  Tier 1/2 (merged -- see below): among gender/number-compatible candidate entities, pick the one
    whose MOST RECENT clause with role=="agent" (strictly before the pronoun's own clause) is
    closest to the pronoun's clause. If that closest agent-clause IS the immediately preceding
    clause (cur_clause-1), that's the textbook Cb case; if not, this is the documented fallback
    "most-recent compatible SUBJECT-like role" tier -- both are the same computation (argmax over
    agent-clause recency), so they are implemented as one rule, not two branches.
  Tier 3 (fallback): no compatible candidate ever held role=="agent" -- fall back to pure recency
    among compatible candidates (argmax last_pos, NO frequency term).
  Tier 4 (fallback): no compatible candidates at all -- existing best-effort (most recent overall
    entity, or allocate new) -- unchanged from run_learnable.

This directly targets AGENT-vs-AGENT turn-taking (the case the blend couldn't touch): the
immediate-preceding-clause agent is a HARD selector, not a small additive nudge that frequency can
swamp.

OPTIONAL SECONDARY ARM (recency_boost): per task contract, if strict-Cb still nulls, test whether
a stronger PURE-RECENCY prior (not role-aware at all) is the real lever the situation-model query
metric rewards (recall: the recency FLOOR beat earned coref on the milestone query metric,
0.750 vs 0.375). Pronoun branch uses last_pos only (RECENCY_BOOST_FACTOR * recency term dominates
count) -- still glass-box, still a small explicit rule, no learned/opaque component.

REPRODUCIBILITY / OPT-IN CONSTRAINT: run_learnable (exp_earn_coref_match_or_allocate_v1.py) is
imported VERBATIM and NEVER mutated. This file adds NEW opt-in functions
(run_learnable_strict_cb, run_learnable_recency_boost); the "baseline" arm below IS run_learnable,
unchanged. Prior committed cells (27e10d3a8, a0aac7eeb, 54a0af00d, 5639fe312) stay reproducible.

CONTENT (now POWERED, the prior blocker): data/eval_gold_mention_role_mcguffey_v1/
gold_combined_pronoun_powered_v1.jsonl -- 36 passages, 130 target_queries, N=81 pronoun mentions
(combines the g1-g2 dense gold + director-verified g5-g6 verbatim pronoun gold). Primary eval.
Also reports the g5g6-only subset (gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl, 18
passages, pronoun-dense half) as a secondary breakout.

MEASURE:
  1. pronoun-only / name-only / overall B3-F1: baseline vs strict_cb (vs recency_boost), on BOTH
     the combined powered eval (primary) and the g5g6-only subset (secondary). Reuses bcubed()
     from exp_earn_coref_match_or_allocate_v1.py verbatim.
  2. Situation-model QUERY metric (name-anchored), pronoun-contributed subset + overall, arms
     oracle / baseline / strict_cb / recency_boost / recency_floor / singleton_floor, computed on
     the combined powered eval (has target_queries). Reuses run_arm_query_metrics,
     derive_pronoun_queries, score_queries from exp_earn_coref_pronoun_centering_v1.py verbatim
     (that file's own centering/prominence arm is NOT used here -- only its query-metric
     plumbing).

CAN-FAIL bands (pre-registered before running):
  HARD_PASS: strict_cb pronoun-only B3-F1 beats baseline by >= PRONOUN_LIFT_MARGIN (0.03) AND
    does not regress name/overall B3-F1 by more than REGRESSION_TOL (0.01) AND strict_cb clears
    the recency_floor on the pronoun-contributed query subset (authored target_queries) by >=
    QUERY_FLOOR_GAP_MARGIN (0.05).
  PARTIAL_LIFT: strict_cb lifts pronoun-only B3-F1 (>= margin, no regression) but does NOT clear
    the recency floor on the query subset -- the coref-level lever works but doesn't propagate to
    the situation-model query metric; report both facts, do not spin as HARD_PASS.
  REGRESSION_DETECTED: strict_cb lifts pronoun B3 but regresses name/overall beyond tolerance.
  NULL_INVESTIGATE: strict_cb does not lift pronoun-only B3-F1 by margin. A powered null here is
    now trustworthy (content is no longer the excuse) -- dump per-mention decision traces (which
    clause's Cb was chosen vs gold) to diagnose whether strict-Cb is picking the WRONG antecedent
    (mechanism bug) or picking the RIGHT antecedent and the metric still doesn't move (residual
    errors are not Cb-shaped at all -- e.g. genuinely need discourse-topic tracking beyond one
    clause, or verb-semantics cues this lever can't see).

Self-test: python exp_earn_coref_pronoun_strict_cb_v1.py --self-test
Full:      python exp_earn_coref_pronoun_strict_cb_v1.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch  # noqa: E402

# Reused VERBATIM, never mutated (reproducibility constraint -- see docstring).
from exp_earn_coref_match_or_allocate_v1 import (  # noqa: E402
    gn_compatible,
    normalize_tokens,
    run_learnable,       # baseline arm, unchanged
    run_recency_floor,
    bcubed,
)
from exp_wire_coref_accumulate_situation_model_v1 import (  # noqa: E402
    build_mention_stream_with_role,
    event_slots_for,
    name_anchor_map,
    pronoun_contributed_queries,
    run_singleton_floor,
    ROLE_VOCAB,
    D,
    MAX_EVENT_SLOTS,
    SEED,
)
# Query-metric plumbing reused verbatim from the prior (blended-prominence) step-2 cell -- only
# its query-scoring machinery, NOT its centering/prominence arm (which is not used by this cell).
from exp_earn_coref_pronoun_centering_v1 import (  # noqa: E402
    run_arm_query_metrics,
    derive_pronoun_queries,
)

ANCHOR_NAME = "earn_coref_pronoun_strict_cb_v1"
REPO_ROOT_ = REPO_ROOT
GOLD_PATH_COMBINED = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_combined_pronoun_powered_v1.jsonl"
)
GOLD_PATH_G5G6 = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
    "gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl",
)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# Strict-Cb: which role(s) count as the grammatically-prominent "subject-like" tier. Kept as an
# explicit, tiny, glass-box set (no learned/opaque component) -- per the design doc, agent-role is
# the Centering subject-analog in this gold's role vocabulary.
SUBJECT_LIKE_ROLES = frozenset({"agent"})

# Optional secondary arm: pronoun branch salience = count + RECENCY_BOOST_FACTOR * OVERLAY_BETA *
# exp(-lambda*dist) instead of count + 1x that term -- tests whether a stronger PURE recency prior
# (no role-awareness) is what the situation-model query metric rewards.
RECENCY_BOOST_FACTOR = 5.0

# PASS/FAIL bands (pre-declared; probe-grade, single local run per exp_dev task contract).
PRONOUN_LIFT_MARGIN = 0.03     # strict_cb must lift pronoun-only B3-F1 over baseline by this much
REGRESSION_TOL = 0.01          # name/overall B3-F1 must not regress by more than this
QUERY_FLOOR_GAP_MARGIN = 0.05  # strict_cb vs recency_floor on pronoun-contributed query subset


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return sorted(passages, key=lambda p: p["passage_id"])


# ---------------------------------------------------------------------------
# STRICT-CB arm: opt-in variant of run_learnable -- ONLY the pronoun branch changes (hard tiered
# antecedent selection instead of a frequency+recency blend); the name/nominal branch (token-
# overlap + determiner-bridging) is byte-identical to run_learnable.
# ---------------------------------------------------------------------------
class _EntityCb:
    __slots__ = ("eid", "tokens", "gender", "number", "count", "last_pos", "clause_role")

    def __init__(self, eid: int) -> None:
        self.eid = eid
        self.tokens: set = set()
        self.gender: Optional[str] = None
        self.number: Optional[str] = None
        self.count = 0
        self.last_pos = -1
        self.clause_role: Dict[int, str] = {}   # clause_idx -> role held by this entity there

    def most_recent_subject_clause(self, cur_clause: int) -> Optional[int]:
        cands = [c for c, r in self.clause_role.items()
                 if r in SUBJECT_LIKE_ROLES and c < cur_clause]
        return max(cands) if cands else None


def _pick_strict_cb(compat: List[_EntityCb], cur_clause: int) -> _EntityCb:
    """Tiers 1+2 merged: argmax over (most-recent subject-like clause < cur_clause); ties broken
    by last stream position. Tier 3: no compatible entity ever held a subject-like role -> pure
    recency (argmax last_pos) among compat. compat is guaranteed non-empty by the caller."""
    scored = [(e, e.most_recent_subject_clause(cur_clause)) for e in compat]
    with_subject = [(e, c) for e, c in scored if c is not None]
    if with_subject:
        best_c = max(c for _, c in with_subject)
        tied = [e for e, c in with_subject if c == best_c]
        return max(tied, key=lambda e: e.last_pos)
    return max(compat, key=lambda e: e.last_pos)


def _resolve_name_branch(entities: List[_EntityCb], next_id: int, gender, number,
                          toks: set, has_determiner: bool) -> Tuple[_EntityCb, int]:
    """Byte-identical logic to run_learnable's name/nominal branch (token-overlap + determiner-
    bridging default), reimplemented over _EntityCb so both branches share one entity registry."""
    compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
    best = None
    best_overlap = 0.0
    for e in compat:
        if not toks and not e.tokens:
            continue
        union = toks | e.tokens
        if not union:
            continue
        ov = len(toks & e.tokens) / len(union)
        if ov > best_overlap:
            best_overlap = ov
            best = e
    if best is None and len(compat) == 1 and has_determiner:
        best = compat[0]
    if best is None:
        best = _EntityCb(next_id)
        next_id += 1
        entities.append(best)
    return best, next_id


def run_learnable_strict_cb(stream: List[dict]) -> List[int]:
    """MATCH-OR-ALLOCATE with literal-Centering strict-Cb on the PRONOUN branch (tiered hard
    selection, not an additive blend). Name/nominal branch unchanged from run_learnable. Requires
    stream records to carry 'role' (build_mention_stream_with_role); records without 'role'
    degrade gracefully to tier-3 pure recency for that mention (no subject-like signal to see)."""
    entities: List[_EntityCb] = []
    next_id = 0
    assigned: List[int] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                best = _pick_strict_cb(compat, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)  # best-effort fallback (tier 4)
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
            best.count += 1
            best.last_pos = pos
            if cur_role is not None:
                best.clause_role[cur_clause] = cur_role
            assigned.append(best.eid)
            continue
        toks = normalize_tokens(rec["mention_text"])
        first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
            if rec["mention_text"].strip() else ""
        has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        best.count += 1
        best.last_pos = pos
        if cur_role is not None:
            best.clause_role[cur_clause] = cur_role
        assigned.append(best.eid)
    return assigned


# ---------------------------------------------------------------------------
# OPTIONAL SECONDARY ARM: pure-recency-boosted salience on the pronoun branch (no role-awareness
# at all) -- tests whether the query-metric's known recency-floor advantage comes from RECENCY
# specifically (as opposed to grammatical role).
# ---------------------------------------------------------------------------
class _EntityRB:
    __slots__ = ("eid", "tokens", "gender", "number", "count", "last_pos")

    def __init__(self, eid: int) -> None:
        self.eid = eid
        self.tokens: set = set()
        self.gender: Optional[str] = None
        self.number: Optional[str] = None
        self.count = 0
        self.last_pos = -1

    def recency_boosted_salience(self, now: int) -> float:
        import math
        from hdlab.state_of_mind import OVERLAY_BETA, OVERLAY_TIEBREAK_LAMBDA
        return self.count + RECENCY_BOOST_FACTOR * OVERLAY_BETA * \
            math.exp(-OVERLAY_TIEBREAK_LAMBDA * (now - self.last_pos))


def run_learnable_recency_boost(stream: List[dict]) -> List[int]:
    """MATCH-OR-ALLOCATE with a boosted pure-recency term on the PRONOUN branch only (no role
    signal). Name/nominal branch unchanged from run_learnable."""
    entities: List[_EntityRB] = []
    next_id = 0
    assigned: List[int] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                best = max(compat, key=lambda e: e.recency_boosted_salience(pos))
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = _EntityRB(next_id)
                next_id += 1
                entities.append(best)
            best.count += 1
            best.last_pos = pos
            assigned.append(best.eid)
            continue
        toks = normalize_tokens(rec["mention_text"])
        compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
        best = None
        best_overlap = 0.0
        for e in compat:
            if not toks and not e.tokens:
                continue
            union = toks | e.tokens
            if not union:
                continue
            ov = len(toks & e.tokens) / len(union)
            if ov > best_overlap:
                best_overlap = ov
                best = e
        first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
            if rec["mention_text"].strip() else ""
        has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
        if best is None and len(compat) == 1 and has_determiner:
            best = compat[0]
        if best is None:
            best = _EntityRB(next_id)
            next_id += 1
            entities.append(best)
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        best.count += 1
        best.last_pos = pos
        assigned.append(best.eid)
    return assigned


# ---------------------------------------------------------------------------
# Decision trace (for the NULL_INVESTIGATE path): per pronoun mention, which entity did strict_cb
# pick vs baseline vs gold, and whether the pick was via an immediate-clause Cb, a farther
# subject-like fallback, or pure recency.
# ---------------------------------------------------------------------------
def trace_strict_cb_decisions(stream: List[dict]) -> List[dict]:
    entities: List[_EntityCb] = []
    next_id = 0
    trace: List[dict] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            tier = "tier4_no_compat"
            picked_gold_hint = None
            if compat:
                best = _pick_strict_cb(compat, cur_clause)
                c = best.most_recent_subject_clause(cur_clause)
                if c == cur_clause - 1:
                    tier = "tier1_immediate_cb"
                elif c is not None:
                    tier = "tier2_farther_subject"
                else:
                    tier = "tier3_pure_recency"
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
            trace.append({
                "pos": pos, "mention_text": rec["mention_text"], "clause": cur_clause,
                "gold_entity": rec["gold_entity"], "picked_eid": best.eid, "tier": tier,
                "n_compat": len(compat),
            })
            best.count += 1
            best.last_pos = pos
            if cur_role is not None:
                best.clause_role[cur_clause] = cur_role
            continue
        toks = normalize_tokens(rec["mention_text"])
        first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
            if rec["mention_text"].strip() else ""
        has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        best.count += 1
        best.last_pos = pos
        if cur_role is not None:
            best.clause_role[cur_clause] = cur_role
    return trace


# ---------------------------------------------------------------------------
# Self-test: (1) real code path (combined + g5g6 gold, real streams, real AccumulateRegister);
# (2) the agent-vs-agent turn-taking FIXTURE where strict-Cb gets it right and the frequency-
# salience baseline gets it wrong (baseline picks the higher-FREQUENCY, non-immediate antecedent;
# strict-Cb picks the immediately-preceding-clause agent); (3) non-regression on a clean chain
# fixture; (4) arms-must-differ (baseline vs strict_cb predictions differ on the flip fixture).
# ---------------------------------------------------------------------------
def self_test() -> None:
    # --- (2) agent-vs-agent turn-taking flip fixture ---
    # "Robert ran. Robert jumped again. Willie appeared. He laughed." Robert is mentioned TWICE
    # (count=2, frequency-heavy) but is NOT the agent of the immediately preceding clause; Willie
    # is mentioned once (count=1) but IS the agent of clause 2, immediately preceding "He"@clause3.
    # Baseline (count + small recency tie-break, beta=0.5) lets Robert's extra count win despite
    # being farther away and NOT the Cb -> mispicks Robert. Strict-Cb ignores frequency and picks
    # the immediate-clause agent (Willie) directly -> correct.
    fixture = {
        "passage_id": "flip_cb1",
        "clauses": ["Robert ran.", "Robert jumped again.", "Willie appeared.", "He laughed."],
        "entities": {
            "Robert": [
                {"clause": 0, "mention": "Robert", "role": "agent"},
                {"clause": 1, "mention": "Robert", "role": "agent"},
            ],
            "Willie": [
                {"clause": 2, "mention": "Willie", "role": "agent"},
                {"clause": 3, "mention": "He", "role": "agent"},
            ],
        },
    }
    stream = build_mention_stream_with_role(fixture)
    assert len(stream) == 4
    he_idx = [i for i, r in enumerate(stream) if r["mention_text"] == "He"][0]
    robert_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Robert"]
    willie_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Willie"]

    base_pred = run_learnable(stream)
    cb_pred = run_learnable_strict_cb(stream)

    base_he_matches_robert = base_pred[he_idx] in {base_pred[i] for i in robert_idxs}
    assert base_he_matches_robert, (
        f"precondition failed: baseline (frequency+recency blend) was expected to MISPICK "
        f"Robert (higher count, farther clause) over Willie (immediate-clause agent) for 'He'; "
        f"base_pred={base_pred}"
    )
    cb_he_matches_willie = cb_pred[he_idx] in {cb_pred[i] for i in willie_idxs}
    cb_he_matches_robert = cb_pred[he_idx] in {cb_pred[i] for i in robert_idxs}
    assert cb_he_matches_willie and not cb_he_matches_robert, (
        f"strict-Cb must pick Willie (immediate-preceding-clause agent), not Robert: "
        f"cb_pred={cb_pred}"
    )

    # (4) arms-must-differ on this fixture
    assert base_pred != cb_pred, "baseline and strict_cb must differ on the flip fixture"

    b_base = bcubed([(stream, base_pred)])
    b_cb = bcubed([(stream, cb_pred)])
    assert b_cb["f1"] > b_base["f1"], (
        f"strict_cb must score strictly higher B3-F1 than baseline on the flip fixture: "
        f"base={b_base} cb={b_cb}"
    )

    # trace sanity: the pronoun decision must be logged as tier1_immediate_cb
    tr = trace_strict_cb_decisions(stream)
    he_trace = [t for t in tr if t["mention_text"] == "He"][0]
    assert he_trace["tier"] == "tier1_immediate_cb", he_trace
    assert he_trace["gold_entity"] == "Willie"

    # --- (3) non-regression fixture (clean chain, no ambiguity) ---
    clean_fixture = {
        "passage_id": "clean_cb1",
        "clauses": ["Alice went to the store.", "She bought bread.", "Bob saw her there."],
        "entities": {
            "Alice": [
                {"clause": 0, "mention": "Alice", "role": "agent"},
                {"clause": 1, "mention": "She", "role": "agent"},
                {"clause": 2, "mention": "her", "role": "patient"},
            ],
            "Bob": [{"clause": 2, "mention": "Bob", "role": "agent"}],
        },
    }
    clean_stream = build_mention_stream_with_role(clean_fixture)
    clean_cb = run_learnable_strict_cb(clean_stream)
    alice_idxs = [i for i, r in enumerate(clean_stream) if r["gold_entity"] == "Alice"]
    bob_idxs = [i for i, r in enumerate(clean_stream) if r["gold_entity"] == "Bob"]
    alice_ids = {clean_cb[i] for i in alice_idxs}
    bob_ids = {clean_cb[i] for i in bob_idxs}
    assert len(alice_ids) == 1, f"strict_cb must still chain Alice/She/her: {alice_ids}"
    assert alice_ids.isdisjoint(bob_ids), "strict_cb must not merge Alice and Bob"

    # --- optional recency_boost arm: sanity (must run, must differ from baseline on the flip
    # fixture since Willie is also the more RECENT mention there -- both cues agree here) ---
    rb_pred = run_learnable_recency_boost(stream)
    assert len(rb_pred) == 4
    rb_he_matches_willie = rb_pred[he_idx] in {rb_pred[i] for i in willie_idxs}
    assert rb_he_matches_willie, f"recency_boost should also favor the more-recent Willie: {rb_pred}"

    # --- derive_pronoun_queries sanity (imported function, real path) ---
    dq = derive_pronoun_queries(stream)
    assert dq == [{"entity": "Willie", "query_clause": 3, "gold_role": "agent"}], dq

    # --- (1) real code path: combined powered gold + g5g6 subset, real streams, real
    # AccumulateRegister decode via the imported run_arm_query_metrics ---
    assert os.path.exists(GOLD_PATH_COMBINED), f"combined gold missing: {GOLD_PATH_COMBINED}"
    assert os.path.exists(GOLD_PATH_G5G6), f"g5g6 gold missing: {GOLD_PATH_G5G6}"
    real_passages = load_passages(GOLD_PATH_COMBINED)
    assert len(real_passages) == 36, f"expected 36 combined passages, got {len(real_passages)}"
    g5g6_passages = load_passages(GOLD_PATH_G5G6)
    assert len(g5g6_passages) == 18, f"expected 18 g5g6 passages, got {len(g5g6_passages)}"
    n_tq = sum(len(p.get("target_queries", [])) for p in real_passages)
    assert n_tq == 130, f"expected 130 target_queries in combined gold, got {n_tq}"

    p0 = real_passages[0]
    real_stream = build_mention_stream_with_role(p0)
    assert len(real_stream) > 0
    real_base = run_learnable(real_stream)
    real_cb = run_learnable_strict_cb(real_stream)
    real_rb = run_learnable_recency_boost(real_stream)
    assert len(real_base) == len(real_cb) == len(real_rb) == len(real_stream)
    event_slots, n_slots, clause_to_slot = event_slots_for(real_stream)
    gen = torch.Generator().manual_seed(SEED)
    res = run_arm_query_metrics(p0, real_stream, [str(c) for c in real_cb], event_slots,
                                 clause_to_slot, gen)
    assert "authored" in res and "derived" in res

    print("[SELF-TEST] PASS: real code path exercised (36 combined + 18 g5g6 passages, 130 "
          "target_queries); agent-vs-agent turn-taking flip fixture confirms strict-Cb corrects "
          "a baseline frequency mispick via tier1_immediate_cb (arms differ, B3-F1 strictly "
          "higher); non-regression on clean chain fixture; recency_boost + derive_pronoun_queries "
          "+ decision-trace verified")


# ---------------------------------------------------------------------------
def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _b3_for_gold(streams: List[List[dict]], arm_preds: Dict[str, List[List[int]]]) -> dict:
    b3 = {}
    for arm_name, preds in arm_preds.items():
        pairs = list(zip(streams, preds))
        b3[arm_name] = {
            "overall": bcubed(pairs),
            "name_only": bcubed(pairs, subset="name"),
            "pronoun_only": bcubed(pairs, subset="pronoun"),
        }
    return b3


def main() -> None:
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ---- combined powered gold (primary) ----
    passages = load_passages(GOLD_PATH_COMBINED)
    streams = [build_mention_stream_with_role(p) for p in passages]
    n_mentions_total = sum(len(s) for s in streams)
    n_pronoun = sum(1 for s in streams for r in s if r["is_pronoun"])

    base_preds = [run_learnable(s) for s in streams]
    cb_preds = [run_learnable_strict_cb(s) for s in streams]
    rb_preds = [run_learnable_recency_boost(s) for s in streams]
    rec_preds = [run_recency_floor(s) for s in streams]

    n_role_flips = sum(1 for bp, cp in zip(base_preds, cb_preds) if bp != cp)

    b3 = _b3_for_gold(streams, {
        "baseline": base_preds, "strict_cb": cb_preds,
        "recency_boost": rb_preds, "recency_floor": rec_preds,
    })

    # ---- g5g6-only subset (secondary, pronoun-dense half) ----
    g5g6_passages = load_passages(GOLD_PATH_G5G6)
    g5g6_streams = [build_mention_stream_with_role(p) for p in g5g6_passages]
    g5g6_base_preds = [run_learnable(s) for s in g5g6_streams]
    g5g6_cb_preds = [run_learnable_strict_cb(s) for s in g5g6_streams]
    g5g6_rb_preds = [run_learnable_recency_boost(s) for s in g5g6_streams]
    b3_g5g6 = _b3_for_gold(g5g6_streams, {
        "baseline": g5g6_base_preds, "strict_cb": g5g6_cb_preds, "recency_boost": g5g6_rb_preds,
    })

    base_pron_f1 = b3["baseline"]["pronoun_only"]["f1"]
    cb_pron_f1 = b3["strict_cb"]["pronoun_only"]["f1"]
    base_name_f1 = b3["baseline"]["name_only"]["f1"]
    cb_name_f1 = b3["strict_cb"]["name_only"]["f1"]
    base_overall_f1 = b3["baseline"]["overall"]["f1"]
    cb_overall_f1 = b3["strict_cb"]["overall"]["f1"]

    pronoun_lift = cb_pron_f1 - base_pron_f1
    name_regression = base_name_f1 - cb_name_f1
    overall_regression = base_overall_f1 - cb_overall_f1
    lifts_pronoun_b3 = pronoun_lift >= PRONOUN_LIFT_MARGIN
    no_regression = (name_regression <= REGRESSION_TOL) and (overall_regression <= REGRESSION_TOL)

    # ---- situation-model QUERY metric (combined gold, name-anchored) ----
    ARM_SEED_IDX = {"oracle": 0, "baseline": 1, "recency_floor": 2, "singleton_floor": 3,
                     "strict_cb": 4, "recency_boost": 5}
    query_arms = {
        "oracle": [[r["gold_entity"] for r in s] for s in streams],
        "baseline": [[str(c) for c in p] for p in base_preds],
        "strict_cb": [[str(c) for c in p] for p in cb_preds],
        "recency_boost": [[str(c) for c in p] for p in rb_preds],
        "recency_floor": [[str(c) for c in p] for p in rec_preds],
        "singleton_floor": [[str(c) for c in run_singleton_floor(s)] for s in streams],
    }
    query_results: Dict[str, dict] = {}
    for arm_name, cluster_id_lists in query_arms.items():
        a_correct = a_total = a_correct_pron = a_total_pron = a_skip = 0
        d_correct = d_total = d_correct_pron = d_total_pron = d_skip = 0
        n_collisions_total = 0
        for p_idx, (p, s, cids) in enumerate(zip(passages, streams, cluster_id_lists)):
            event_slots, n_slots, clause_to_slot = event_slots_for(s)
            gen = torch.Generator().manual_seed(SEED + p_idx * 100 + ARM_SEED_IDX[arm_name])
            res = run_arm_query_metrics(p, s, cids, event_slots, clause_to_slot, gen)
            a_correct += res["authored"]["correct"]; a_total += res["authored"]["total"]
            a_correct_pron += res["authored"]["correct_pron"]; a_total_pron += res["authored"]["total_pron"]
            a_skip += res["authored"]["skipped"]
            d_correct += res["derived"]["correct"]; d_total += res["derived"]["total"]
            d_correct_pron += res["derived"]["correct_pron"]; d_total_pron += res["derived"]["total_pron"]
            d_skip += res["derived"]["skipped"]
            n_collisions_total += res["n_collisions"]
        query_results[arm_name] = {
            "authored_query_accuracy": (a_correct / a_total) if a_total else None,
            "authored_query_accuracy_pronoun_subset": (a_correct_pron / a_total_pron) if a_total_pron else None,
            "authored_n_total": a_total, "authored_n_total_pron": a_total_pron, "authored_n_skipped": a_skip,
            "derived_query_accuracy": (d_correct / d_total) if d_total else None,
            "derived_n_total": d_total, "derived_n_skipped": d_skip,
            "n_collisions": n_collisions_total,
        }

    oracle_pron_q = query_results["oracle"]["authored_query_accuracy_pronoun_subset"]
    base_pron_q = query_results["baseline"]["authored_query_accuracy_pronoun_subset"]
    cb_pron_q = query_results["strict_cb"]["authored_query_accuracy_pronoun_subset"]
    rb_pron_q = query_results["recency_boost"]["authored_query_accuracy_pronoun_subset"]
    recency_pron_q = query_results["recency_floor"]["authored_query_accuracy_pronoun_subset"]

    cb_clears_recency_authored = (
        cb_pron_q is not None and recency_pron_q is not None
        and (cb_pron_q - recency_pron_q) >= QUERY_FLOOR_GAP_MARGIN
    )
    cb_beats_base_authored = (
        cb_pron_q is not None and base_pron_q is not None
        and (cb_pron_q - base_pron_q) >= QUERY_FLOOR_GAP_MARGIN
    )
    rb_clears_recency_authored = (
        rb_pron_q is not None and recency_pron_q is not None
        and (rb_pron_q - recency_pron_q) >= QUERY_FLOOR_GAP_MARGIN
    )

    oracle_derived_q = query_results["oracle"]["derived_query_accuracy"]
    base_derived_q = query_results["baseline"]["derived_query_accuracy"]
    cb_derived_q = query_results["strict_cb"]["derived_query_accuracy"]
    recency_derived_q = query_results["recency_floor"]["derived_query_accuracy"]
    cb_clears_recency_derived = (
        cb_derived_q is not None and recency_derived_q is not None
        and (cb_derived_q - recency_derived_q) >= QUERY_FLOOR_GAP_MARGIN
    )
    cb_beats_base_derived = (
        cb_derived_q is not None and base_derived_q is not None
        and (cb_derived_q - base_derived_q) >= QUERY_FLOOR_GAP_MARGIN
    )

    # ---- decision-trace dump (always computed -- cheap, and load-bearing for the NULL path) ----
    trace_summary = {"tier1_immediate_cb": 0, "tier2_farther_subject": 0,
                      "tier3_pure_recency": 0, "tier4_no_compat": 0}
    sample_traces = []
    for p_idx, (p, s) in enumerate(zip(passages, streams)):
        tr = trace_strict_cb_decisions(s)
        for t in tr:
            trace_summary[t["tier"]] = trace_summary.get(t["tier"], 0) + 1
        if len(sample_traces) < 20:
            for t in tr:
                if len(sample_traces) >= 20:
                    break
                t2 = dict(t)
                t2["passage_id"] = p["passage_id"]
                sample_traces.append(t2)

    # ---- verdict (primary = powered B3 pronoun-only signal on combined gold, per task contract) ----
    if lifts_pronoun_b3 and no_regression and cb_clears_recency_authored:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"strict_cb pronoun-only B3-F1: baseline={base_pron_f1:.4f} -> strict_cb={cb_pron_f1:.4f} "
            f"(lift={pronoun_lift:.4f} >= {PRONOUN_LIFT_MARGIN}); no regression on name "
            f"({name_regression:.4f}<={REGRESSION_TOL}) or overall ({overall_regression:.4f}<="
            f"{REGRESSION_TOL}); clears recency floor on pronoun-contributed query subset "
            f"(strict_cb={cb_pron_q} vs recency={recency_pron_q}, gap>={QUERY_FLOOR_GAP_MARGIN}). "
            f"n_role_flips={n_role_flips}/{len(streams)} passages. tiers={trace_summary}."
        )
    elif not no_regression:
        verdict = "REGRESSION_DETECTED"
        verdict_msg = (
            f"strict_cb LIFTED pronoun-only B3-F1 ({pronoun_lift:.4f}) but REGRESSED "
            f"name ({name_regression:.4f}) or overall ({overall_regression:.4f}) beyond "
            f"tolerance {REGRESSION_TOL} -- strict-Cb tier is bleeding into or otherwise "
            f"corrupting non-pronoun/overall behavior; investigate before adopting."
        )
    elif lifts_pronoun_b3 and no_regression and not cb_clears_recency_authored:
        verdict = "PARTIAL_LIFT"
        verdict_msg = (
            f"strict_cb pronoun-only B3-F1 lift confirmed ({base_pron_f1:.4f} -> {cb_pron_f1:.4f}, "
            f"lift={pronoun_lift:.4f}>={PRONOUN_LIFT_MARGIN}, no regression) but the coref-level "
            f"gain does NOT propagate to the situation-model query metric: strict_cb={cb_pron_q} "
            f"vs recency_floor={recency_pron_q} (gap={(cb_pron_q - recency_pron_q) if (cb_pron_q is not None and recency_pron_q is not None) else None} "
            f"< {QUERY_FLOOR_GAP_MARGIN}). Coref-level fix real, query-metric propagation "
            f"unresolved -- report both, do not spin as HARD_PASS. tiers={trace_summary}."
        )
    else:
        verdict = "NULL_INVESTIGATE"
        verdict_msg = (
            f"strict_cb pronoun-only B3-F1: baseline={base_pron_f1:.4f} -> strict_cb={cb_pron_f1:.4f} "
            f"(lift={pronoun_lift:.4f} < {PRONOUN_LIFT_MARGIN}); powered eval (N={n_pronoun} pronoun "
            f"mentions, no longer a content excuse). n_role_flips={n_role_flips}/{len(streams)} "
            f"passages. tier distribution={trace_summary} -- tier1_immediate_cb count tells whether "
            f"the immediate-clause Cb rule ever actually fires; if it's near-zero, the gold's "
            f"pronoun antecedents mostly aren't the immediately-preceding-clause's agent (Centering "
            f"needs a WIDER window / different unit than 'clause', not this lever as specified). "
            f"recency_boost secondary arm: pron_q={rb_pron_q} clears_recency={rb_clears_recency_authored} "
            f"-- if recency_boost clears the floor but strict_cb doesn't, RECENCY (not grammatical "
            f"role) is the real lever the query metric rewards."
        )

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "gold_path_combined": GOLD_PATH_COMBINED,
        "gold_path_g5g6": GOLD_PATH_G5G6,
        "n_passages_combined": len(passages),
        "n_passages_g5g6": len(g5g6_passages),
        "n_mentions_total": n_mentions_total,
        "n_pronoun_mentions": n_pronoun,
        "n_role_flips_baseline_vs_strict_cb": n_role_flips,
        "subject_like_roles": sorted(SUBJECT_LIKE_ROLES),
        "recency_boost_factor": RECENCY_BOOST_FACTOR,
        "b3_combined": b3,
        "b3_g5g6_only": b3_g5g6,
        "pronoun_lift": pronoun_lift,
        "name_regression": name_regression,
        "overall_regression": overall_regression,
        "lifts_pronoun_b3": lifts_pronoun_b3,
        "no_regression": no_regression,
        "query_metric": query_results,
        "query_metric_note": (
            "authored_* uses each gold passage's committed target_queries (pronoun-contributed "
            "subset via pronoun_contributed_queries); derived_* is EVERY entity's pronoun mention "
            "at a clause turned into a query -- a better-powered directional read of the same "
            "lever, all-pronoun by construction. Both computed on the COMBINED powered gold."
        ),
        "cb_clears_recency_authored": cb_clears_recency_authored,
        "cb_beats_baseline_authored": cb_beats_base_authored,
        "cb_clears_recency_derived": cb_clears_recency_derived,
        "cb_beats_baseline_derived": cb_beats_base_derived,
        "recency_boost_clears_recency_authored": rb_clears_recency_authored,
        "decision_trace_tier_summary": trace_summary,
        "decision_trace_sample": sample_traces,
        "bands": {
            "pronoun_lift_margin": PRONOUN_LIFT_MARGIN,
            "regression_tol": REGRESSION_TOL,
            "query_floor_gap_margin": QUERY_FLOOR_GAP_MARGIN,
        },
        "reproducibility_note": (
            "run_learnable (exp_earn_coref_match_or_allocate_v1.py) is imported and NEVER "
            "mutated; run_learnable_strict_cb and run_learnable_recency_boost are NEW opt-in "
            "functions in this file. Prior committed cells (27e10d3a8, a0aac7eeb, 54a0af00d, "
            "5639fe312) are unaffected."
        ),
        "prior_commits": {
            "coref_fair_test_hard_pass": "27e10d3a8",
            "possessive_gender_fix": "a0aac7eeb",
            "milestone_wire_accumulate": "54a0af00d",
            "step2_blended_prominence_null": "5639fe312",
        },
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    print(f"[{ANCHOR_NAME}] {verdict}")
    print(verdict_msg)
    print(f"metrics written to {final}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
