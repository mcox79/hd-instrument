"""STEP 2 (pronoun coref via Centering / grammatical-role prominence), 2026-08-02.

Design: notes/step2_pronoun_coref_centering_role_prominence_design_2026-08-02.md

THE GAP (milestone cell exp_wire_coref_accumulate_situation_model_v1.py, commit 54a0af00d):
earned coref UNDERPERFORMS the recency floor on the pronoun-contributed subset of the
situation-model query metric (earned=0.375 vs recency=0.750 vs oracle=0.875) specifically
because run_learnable's pronoun path (exp_earn_coref_match_or_allocate_v1.py L206-219) picks
the argmax-salience gender-compatible entity using ONLY frequency+recency -- no grammatical-role
signal. Pronoun-only B3-F1 on the dense eval = 0.547 (vs name-only 0.891).

THE FIX (Centering Theory -- Grosz/Joshi/Weinstein; Gordon-Grosz-Gilliom): a pronoun prefers the
backward-looking center Cb = the most grammatically PROMINENT entity of recent discourse
(subject/agent > experiencer > object/other). This cell adds a role-prominence term (+ a small
role-parallelism bonus) to the pronoun antecedent-salience formula. Role is SUPPLIED gold here
(the extraction organ is a separate, already-~0.60 layer); this cell isolates the coref
antecedent-selection lever only.

REPRODUCIBILITY / OPT-IN CONSTRAINT: exp_earn_coref_match_or_allocate_v1.run_learnable is
imported VERBATIM and NEVER mutated -- committed cells (dense-eval 27e10d3a8/a0aac7eeb, milestone
54a0af00d) import it and their results must stay reproducible. This file adds a NEW function
run_learnable_centering (below) that is opt-in: call it explicitly to get the Centering variant.
The comparison arms are: "baseline" = run_learnable (unchanged) vs "centering" =
run_learnable_centering (the one-variable role-prominence addition).

MEASURE (two readouts):
  1. POWERED: pronoun-only / name-only / overall B3-F1 on the dense eval (data/
     eval_gold_mention_role_mcguffey_v1/gold_multientity_dense_v1.jsonl, 18 passages), baseline
     vs centering. Primary significance signal (N=28 pronoun mentions).
  2. SITUATION-MODEL (directional, N smaller): the pronoun-contributed cross-mention QUERY
     accuracy from the milestone metric's headline (name-anchored query, AccumulateRegister),
     baseline vs centering, for BOTH the AUTHORED target_queries subset (~8 pronoun-contributed)
     AND the FULL DERIVED set (every pronoun mention -> a query {entity, clause, gold_role},
     ~17 in the dense gold). Reused verbatim from exp_wire_coref_accumulate_situation_model_v1.py
     (commit 54a0af00d): build_mention_stream_with_role, event_slots_for, name_anchor_map,
     pronoun_contributed_queries -- imported, not reimplemented; that file is untouched.

CAN-FAIL: if centering does not lift pronoun-only B3-F1 over baseline (>= PRONOUN_LIFT_MARGIN),
verdict = NULL_INVESTIGATE -- diagnose whether the role signal actually fired (n_role_flips) and
whether the residual same-gender cases are decidable from role at all.

Self-test: python exp_earn_coref_pronoun_centering_v1.py --self-test
Full:      python exp_earn_coref_pronoun_centering_v1.py
"""
from __future__ import annotations

import argparse
import json
import math
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

from hdlab.state_of_mind import OVERLAY_BETA, OVERLAY_TIEBREAK_LAMBDA  # noqa: E402
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402

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

ANCHOR_NAME = "earn_coref_pronoun_centering_v1"
REPO_ROOT_ = REPO_ROOT
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multientity_dense_v1.jsonl"
)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---------------------------------------------------------------------------
# Centering role-prominence table (glass-box, small explicit weight set; no learned/opaque
# component). Subject/agent-like roles are the most PROMINENT backward-looking-center candidate;
# everything else is lower. None (role unknown/absent) contributes zero.
# ---------------------------------------------------------------------------
ROLE_PROMINENCE: Dict[Optional[str], float] = {
    "agent": 1.0,
    "experiencer": 0.7,
    "theme": 0.3,
    "patient": 0.3,
    "recipient": 0.3,
    "possessor": 0.2,
    "addressee": 0.3,
    "goal": 0.2,
    "instrument": 0.2,
    None: 0.0,
}
ROLE_PROMINENCE_WEIGHT = 0.3   # additive weight on prominence(entity.last_role)
PARALLELISM_BONUS = 0.15       # extra when the pronoun's OWN role matches the antecedent's last_role

# PASS/FAIL bands (pre-declared; probe-grade, single local run per exp_dev task contract).
PRONOUN_LIFT_MARGIN = 0.03     # centering must lift pronoun-only B3-F1 over baseline by this much
REGRESSION_TOL = 0.01          # name/overall B3-F1 must not regress by more than this
QUERY_FLOOR_GAP_MARGIN = 0.05  # directional: centering vs recency floor on pronoun-contributed queries


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return sorted(passages, key=lambda p: p["passage_id"])


# ---------------------------------------------------------------------------
# CENTERING arm: opt-in variant of run_learnable (exp_earn_coref_match_or_allocate_v1.py
# L206-219) -- ONLY the pronoun branch changes (adds role-prominence + parallelism to salience);
# the name/nominal branch (token-overlap + determiner-bridging) is untouched, since Centering
# targets pronoun antecedent selection specifically (see design doc).
# ---------------------------------------------------------------------------
class _EntityC:
    __slots__ = ("eid", "tokens", "gender", "number", "count", "last_pos", "last_role")

    def __init__(self, eid: int) -> None:
        self.eid = eid
        self.tokens: set = set()
        self.gender: Optional[str] = None
        self.number: Optional[str] = None
        self.count = 0
        self.last_pos = -1
        self.last_role: Optional[str] = None

    def base_salience(self, now: int) -> float:
        return self.count + OVERLAY_BETA * math.exp(-OVERLAY_TIEBREAK_LAMBDA * (now - self.last_pos))

    def centering_salience(self, now: int, cur_role: Optional[str]) -> float:
        s = self.base_salience(now)
        s += ROLE_PROMINENCE_WEIGHT * ROLE_PROMINENCE.get(self.last_role, 0.0)
        if cur_role is not None and self.last_role is not None and cur_role == self.last_role:
            s += PARALLELISM_BONUS
        return s


def run_learnable_centering(stream: List[dict]) -> List[int]:
    """MATCH-OR-ALLOCATE + Centering role-prominence on the PRONOUN branch. Byte-identical to
    run_learnable on the name/nominal branch. Requires stream records to carry 'role' (use
    build_mention_stream_with_role); records without 'role' degrade gracefully (prominence=0,
    i.e. behaves like the base salience alone for that antecedent)."""
    entities: List[_EntityC] = []
    next_id = 0
    assigned: List[int] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                best = max(compat, key=lambda e: e.centering_salience(pos, cur_role))
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)  # best-effort fallback
            else:
                best = _EntityC(next_id)
                next_id += 1
                entities.append(best)
            best.count += 1
            best.last_pos = pos
            best.last_role = cur_role
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
            best = _EntityC(next_id)
            next_id += 1
            entities.append(best)
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        best.count += 1
        best.last_pos = pos
        best.last_role = cur_role
        assigned.append(best.eid)
    return assigned


# ---------------------------------------------------------------------------
# Derived pronoun-contributed query set: EVERY entity's pronoun mention at a clause -> a query
# {entity, query_clause, gold_role}. Arm-independent (built from gold stream, not predictions).
# Dedupe by (entity, clause) -- first mention's role wins (same event, should be consistent).
# ---------------------------------------------------------------------------
def derive_pronoun_queries(stream: List[dict]) -> List[dict]:
    seen: Dict[Tuple[str, int], str] = {}
    out: List[dict] = []
    for r in stream:
        if not r["is_pronoun"] or r.get("role") is None:
            continue
        key = (r["gold_entity"], r["clause"])
        if key in seen:
            continue
        seen[key] = r["role"]
        out.append({"entity": r["gold_entity"], "query_clause": r["clause"], "gold_role": r["role"]})
    return out


# ---------------------------------------------------------------------------
# Per-passage-per-arm: build the AccumulateRegister once, answer BOTH the authored (milestone
# target_queries, pronoun-contributed subset via pronoun_contributed_queries) and the derived
# (derive_pronoun_queries, all pronoun-contributed by construction) query sets against it.
# ---------------------------------------------------------------------------
def score_queries(reg: AccumulateRegister, anchor: Dict[str, str], clause_to_slot: Dict[int, int],
                   queries: List[dict], pron_flags: Optional[List[bool]]) -> Tuple[int, int, int, int, int]:
    correct = total = correct_pron = total_pron = skipped = 0
    for qi, q in enumerate(queries):
        E, qc, gold_role = q["entity"], q["query_clause"], q["gold_role"]
        if E not in anchor or qc not in clause_to_slot:
            skipped += 1
            continue
        cid = anchor[E]
        slot = clause_to_slot[qc]
        pred_role, _ = reg.decode(cid, slot)
        ok = int(pred_role == gold_role)
        correct += ok
        total += 1
        is_pron = pron_flags[qi] if pron_flags is not None else True
        if is_pron:
            correct_pron += ok
            total_pron += 1
    return correct, total, correct_pron, total_pron, skipped


def run_arm_query_metrics(passage: dict, stream: List[dict], cluster_ids: List[str],
                           event_slots: List[int], clause_to_slot: Dict[int, int],
                           generator: torch.Generator) -> dict:
    reg = AccumulateRegister(ROLE_VOCAB, D, generator, max_event_slots=MAX_EVENT_SLOTS)
    added_keys = set()
    n_collisions = 0
    for rec, cid, slot in zip(stream, cluster_ids, event_slots):
        key = (cid, slot)
        if key in added_keys:
            n_collisions += 1
            continue
        added_keys.add(key)
        reg.add_event(cid, rec["role"], slot)

    anchor = name_anchor_map(stream, cluster_ids)
    authored_queries = passage.get("target_queries", [])
    authored_pron_map = pronoun_contributed_queries(passage, stream)
    authored_pron_flags = [authored_pron_map.get(qi, False) for qi in range(len(authored_queries))]
    a_correct, a_total, a_correct_pron, a_total_pron, a_skip = score_queries(
        reg, anchor, clause_to_slot, authored_queries, authored_pron_flags)

    derived_queries = derive_pronoun_queries(stream)
    d_correct, d_total, d_correct_pron, d_total_pron, d_skip = score_queries(
        reg, anchor, clause_to_slot, derived_queries, None)

    return {
        "authored": {"correct": a_correct, "total": a_total, "correct_pron": a_correct_pron,
                     "total_pron": a_total_pron, "skipped": a_skip},
        "derived": {"correct": d_correct, "total": d_total, "correct_pron": d_correct_pron,
                    "total_pron": d_total_pron, "skipped": d_skip},
        "n_collisions": n_collisions,
    }


# ---------------------------------------------------------------------------
# Self-test: (1) real code path (dense gold, real stream, real AccumulateRegister); (2) the
# role-prominence FIXTURE where Centering must flip the answer vs baseline -- 2 same-gender
# entities, one was the prior AGENT; baseline salience (frequency+recency only) picks the WRONG
# (more recent, non-agent) entity, Centering correctly prefers the AGENT; (3) non-regression on
# the existing clean Alice/Bob/Sam-style fixture; (4) arms-must-differ (baseline vs centering
# predictions differ on the role-flip fixture, per META_RULE_AF spirit).
# ---------------------------------------------------------------------------
def self_test() -> None:
    # --- (2) role-prominence flip fixture ---
    # Robert (AGENT@c0), Willie (non-agent THEME@c1, more RECENT than Robert), "He"@c2 refers to
    # Robert (the discourse topic continuing as agent) -- but Willie is closer in position, so
    # frequency+recency-only salience favors Willie. Centering's role-prominence term must flip
    # the pick back to Robert.
    fixture = {
        "passage_id": "flip1",
        "clauses": ["Robert spoke first.", "Willie listened quietly.", "He left the room."],
        "entities": {
            "Robert": [
                {"clause": 0, "mention": "Robert", "role": "agent"},
                {"clause": 2, "mention": "He", "role": "agent"},
            ],
            "Willie": [{"clause": 1, "mention": "Willie", "role": "theme"}],
        },
    }
    stream = build_mention_stream_with_role(fixture)
    assert len(stream) == 3
    he_idx = [i for i, r in enumerate(stream) if r["mention_text"] == "He"][0]
    robert_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Robert"]
    willie_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Willie"]

    base_pred = run_learnable(stream)
    cent_pred = run_learnable_centering(stream)

    base_he_matches_willie = base_pred[he_idx] in {base_pred[i] for i in willie_idxs}
    assert base_he_matches_willie, (
        f"precondition failed: baseline salience (freq+recency only) was expected to MISPICK "
        f"Willie (more recent, non-agent) over Robert (agent) for 'He'; base_pred={base_pred}"
    )
    cent_he_matches_robert = cent_pred[he_idx] in {cent_pred[i] for i in robert_idxs}
    cent_he_matches_willie = cent_pred[he_idx] in {cent_pred[i] for i in willie_idxs}
    assert cent_he_matches_robert and not cent_he_matches_willie, (
        f"Centering must flip 'He' onto Robert (the prior AGENT), not Willie: cent_pred={cent_pred}"
    )

    # (4) arms-must-differ on this fixture (baseline and centering must produce different clusters)
    assert base_pred != cent_pred, "baseline and centering must differ on the role-flip fixture"

    b_base = bcubed([(stream, base_pred)])
    b_cent = bcubed([(stream, cent_pred)])
    assert b_cent["f1"] > b_base["f1"], (
        f"centering must score strictly higher B3-F1 than baseline on the role-flip fixture: "
        f"base={b_base} cent={b_cent}"
    )

    # --- (3) non-regression fixture (clean chain, no role-flip needed; both arms must still
    # resolve correctly -- Centering must not break the easy case) ---
    clean_fixture = {
        "passage_id": "clean1",
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
    clean_cent = run_learnable_centering(clean_stream)
    alice_idxs = [i for i, r in enumerate(clean_stream) if r["gold_entity"] == "Alice"]
    bob_idxs = [i for i, r in enumerate(clean_stream) if r["gold_entity"] == "Bob"]
    alice_ids = {clean_cent[i] for i in alice_idxs}
    bob_ids = {clean_cent[i] for i in bob_idxs}
    assert len(alice_ids) == 1, f"centering must still chain Alice/She/her: {alice_ids}"
    assert alice_ids.isdisjoint(bob_ids), "centering must not merge Alice and Bob"

    # --- derive_pronoun_queries sanity ---
    dq = derive_pronoun_queries(stream)
    assert dq == [{"entity": "Robert", "query_clause": 2, "gold_role": "agent"}], dq

    # --- (1) real code path: real dense gold, real stream, real AccumulateRegister decode ---
    assert os.path.exists(GOLD_PATH), f"dense gold file missing: {GOLD_PATH}"
    real_passages = load_passages(GOLD_PATH)
    assert len(real_passages) == 18, f"expected 18 dense passages, got {len(real_passages)}"
    p0 = real_passages[0]
    real_stream = build_mention_stream_with_role(p0)
    assert len(real_stream) > 0
    real_base = run_learnable(real_stream)
    real_cent = run_learnable_centering(real_stream)
    assert len(real_base) == len(real_cent) == len(real_stream)
    event_slots, n_slots, clause_to_slot = event_slots_for(real_stream)
    gen = torch.Generator().manual_seed(SEED)
    res = run_arm_query_metrics(p0, real_stream, [str(c) for c in real_cent], event_slots,
                                 clause_to_slot, gen)
    assert "authored" in res and "derived" in res

    print("[SELF-TEST] PASS: real code path exercised; role-flip fixture confirms Centering "
          "corrects a baseline mispick (arms differ, B3-F1 strictly higher); non-regression on "
          "clean chain fixture; derive_pronoun_queries verified")


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


def main() -> None:
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    passages = load_passages(GOLD_PATH)
    streams = [build_mention_stream_with_role(p) for p in passages]

    n_mentions_total = sum(len(s) for s in streams)
    n_pronoun = sum(1 for s in streams for r in s if r["is_pronoun"])

    base_preds = [run_learnable(s) for s in streams]
    cent_preds = [run_learnable_centering(s) for s in streams]
    rec_preds = [run_recency_floor(s) for s in streams]

    n_role_flips = sum(
        1 for bp, cp in zip(base_preds, cent_preds) if bp != cp
    )

    # ---- (1) POWERED: B3 overall/name/pronoun, baseline vs centering ----
    b3 = {}
    for arm_name, preds in (("baseline", base_preds), ("centering", cent_preds),
                             ("recency_floor", rec_preds)):
        pairs = list(zip(streams, preds))
        b3[arm_name] = {
            "overall": bcubed(pairs),
            "name_only": bcubed(pairs, subset="name"),
            "pronoun_only": bcubed(pairs, subset="pronoun"),
        }

    base_pron_f1 = b3["baseline"]["pronoun_only"]["f1"]
    cent_pron_f1 = b3["centering"]["pronoun_only"]["f1"]
    base_name_f1 = b3["baseline"]["name_only"]["f1"]
    cent_name_f1 = b3["centering"]["name_only"]["f1"]
    base_overall_f1 = b3["baseline"]["overall"]["f1"]
    cent_overall_f1 = b3["centering"]["overall"]["f1"]

    pronoun_lift = cent_pron_f1 - base_pron_f1
    name_regression = base_name_f1 - cent_name_f1
    overall_regression = base_overall_f1 - cent_overall_f1
    lifts_pronoun_b3 = pronoun_lift >= PRONOUN_LIFT_MARGIN
    no_regression = (name_regression <= REGRESSION_TOL) and (overall_regression <= REGRESSION_TOL)

    # ---- (2) DIRECTIONAL: situation-model query metric, baseline vs centering vs oracle vs floors ----
    # a_idx MATCHES exp_wire_coref_accumulate_situation_model_v1.ARM_ORDER's index convention
    # (oracle=0, earned=1, recency_floor=2, singleton_floor=3) so the "baseline" arm here
    # reproduces the milestone cell's committed "earned" numbers bit-for-bit (same seed formula
    # SEED + p_idx*100 + a_idx) -- this is a deliberate cross-check, not an arbitrary choice.
    # "centering" gets a_idx=4 (a genuinely new arm, no prior value to reproduce).
    ARM_SEED_IDX = {"oracle": 0, "baseline": 1, "recency_floor": 2, "singleton_floor": 3, "centering": 4}
    query_arms = {
        "oracle": [[r["gold_entity"] for r in s] for s in streams],
        "baseline": [[str(c) for c in p] for p in base_preds],
        "centering": [[str(c) for c in p] for p in cent_preds],
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
    cent_pron_q = query_results["centering"]["authored_query_accuracy_pronoun_subset"]
    recency_pron_q = query_results["recency_floor"]["authored_query_accuracy_pronoun_subset"]

    cent_clears_recency_authored = (
        cent_pron_q is not None and recency_pron_q is not None
        and (cent_pron_q - recency_pron_q) >= QUERY_FLOOR_GAP_MARGIN
    )
    cent_beats_base_authored = (
        cent_pron_q is not None and base_pron_q is not None
        and (cent_pron_q - base_pron_q) >= QUERY_FLOOR_GAP_MARGIN
    )

    oracle_derived_q = query_results["oracle"]["derived_query_accuracy"]
    base_derived_q = query_results["baseline"]["derived_query_accuracy"]
    cent_derived_q = query_results["centering"]["derived_query_accuracy"]
    recency_derived_q = query_results["recency_floor"]["derived_query_accuracy"]
    cent_clears_recency_derived = (
        cent_derived_q is not None and recency_derived_q is not None
        and (cent_derived_q - recency_derived_q) >= QUERY_FLOOR_GAP_MARGIN
    )
    cent_beats_base_derived = (
        cent_derived_q is not None and base_derived_q is not None
        and (cent_derived_q - base_derived_q) >= QUERY_FLOOR_GAP_MARGIN
    )

    # ---- verdict (primary = powered B3 pronoun-only signal, per task contract) ----
    if lifts_pronoun_b3 and no_regression:
        verdict = "CENTERING_LIFT_CONFIRMED"
        verdict_msg = (
            f"pronoun-only B3-F1: baseline={base_pron_f1:.4f} -> centering={cent_pron_f1:.4f} "
            f"(lift={pronoun_lift:.4f} >= {PRONOUN_LIFT_MARGIN}); no regression on name "
            f"({name_regression:.4f}<={REGRESSION_TOL}) or overall ({overall_regression:.4f}<="
            f"{REGRESSION_TOL}). n_role_flips={n_role_flips}/{len(streams)} passages. "
            f"Query-metric (directional): authored pronoun-subset base={base_pron_q} "
            f"cent={cent_pron_q} recency={recency_pron_q} oracle={oracle_pron_q}; "
            f"clears_recency={cent_clears_recency_authored} beats_baseline={cent_beats_base_authored}. "
            f"Derived-17-style set: base={base_derived_q} cent={cent_derived_q} "
            f"recency={recency_derived_q} oracle={oracle_derived_q}; "
            f"clears_recency={cent_clears_recency_derived} beats_baseline={cent_beats_base_derived}."
        )
    elif not no_regression:
        verdict = "REGRESSION_DETECTED"
        verdict_msg = (
            f"centering LIFTED pronoun-only B3-F1 ({pronoun_lift:.4f}) but REGRESSED "
            f"name ({name_regression:.4f}) or overall ({overall_regression:.4f}) beyond "
            f"tolerance {REGRESSION_TOL} -- role-prominence term is bleeding into or otherwise "
            f"corrupting non-pronoun/overall behavior; investigate before adopting."
        )
    else:
        verdict = "NULL_INVESTIGATE"
        verdict_msg = (
            f"pronoun-only B3-F1: baseline={base_pron_f1:.4f} -> centering={cent_pron_f1:.4f} "
            f"(lift={pronoun_lift:.4f} < {PRONOUN_LIFT_MARGIN}); NOT a ceiling by default -- "
            f"n_role_flips={n_role_flips}/{len(streams)} passages (did the role signal actually "
            f"fire?). If n_role_flips==0, the role-prominence term never changed an argmax pick "
            f"(same-gender residual cases may be decided by other salience terms already, or need "
            f"a wider window / different prominence weights / verb-based cues, not this lever as-is)."
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
        "gold_path": GOLD_PATH,
        "n_passages": len(passages),
        "n_mentions_total": n_mentions_total,
        "n_pronoun_mentions": n_pronoun,
        "n_role_flips_baseline_vs_centering": n_role_flips,
        "role_prominence_table": ROLE_PROMINENCE,
        "role_prominence_weight": ROLE_PROMINENCE_WEIGHT,
        "parallelism_bonus": PARALLELISM_BONUS,
        "b3": b3,
        "pronoun_lift": pronoun_lift,
        "name_regression": name_regression,
        "overall_regression": overall_regression,
        "lifts_pronoun_b3": lifts_pronoun_b3,
        "no_regression": no_regression,
        "query_metric": query_results,
        "query_metric_note": (
            "authored_* uses the milestone cell's committed target_queries (pronoun-contributed "
            "subset via pronoun_contributed_queries, ~8); derived_* is EVERY entity's pronoun "
            "mention at a clause turned into a query (~17 in this dense gold) -- a better-powered "
            "directional read of the same lever, all-pronoun by construction."
        ),
        "cent_clears_recency_authored": cent_clears_recency_authored,
        "cent_beats_baseline_authored": cent_beats_base_authored,
        "cent_clears_recency_derived": cent_clears_recency_derived,
        "cent_beats_baseline_derived": cent_beats_base_derived,
        "bands": {
            "pronoun_lift_margin": PRONOUN_LIFT_MARGIN,
            "regression_tol": REGRESSION_TOL,
            "query_floor_gap_margin": QUERY_FLOOR_GAP_MARGIN,
        },
        "reproducibility_note": (
            "run_learnable (exp_earn_coref_match_or_allocate_v1.py) is imported and NEVER "
            "mutated; run_learnable_centering is a NEW opt-in function in this file. Prior "
            "committed cells (27e10d3a8, a0aac7eeb, 54a0af00d) are unaffected."
        ),
        "prior_commits": {
            "coref_fair_test_hard_pass": "27e10d3a8",
            "possessive_gender_fix": "a0aac7eeb",
            "milestone_wire_accumulate": "54a0af00d",
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
