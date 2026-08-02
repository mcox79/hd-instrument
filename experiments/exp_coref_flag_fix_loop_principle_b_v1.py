"""SELF-IMPROVING-READER LOOP, cycle 2: FLAG (earned) -> FIX = Binding Principle B (2026-08-02).

Cycle 1 (commit 82492af76, atom 29619) NULLed the topic-continuity fix but proved the FLAG is
earned + localizes. The probe (notes/probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_
2026-08-02.md, commit b839a3176) then REDIRECTED the fix: verb-semantics ceiling is only 5.9% of
flagged errors (not worth building), but a CHEAP, zero-new-knowledge, purely-syntactic fix covers
29.4% = BINDING PRINCIPLE B (disjoint reference). This cell implements + measures it -- the RIGHT
fix flavor (flag earned; probe found the lever).

THE FIX (Binding Principle B -- brain-faithful native grammatical competence, glass-box, NO
supplied knowledge, NO borrowed embeddings): a non-reflexive pronoun cannot corefer with a
co-argument in its own local clause ("John saw him" => him != John). For our resolver: when
resolving a pronoun whose OWN role is NON-agent (object/patient/theme/recipient/experiencer),
EXCLUDE from its candidate antecedents the entity that holds the AGENT role in that SAME clause.
The data is already computed: _EntityCb.clause_role tracks who is agent of each clause; the
mention stream carries per-mention clause + role. No new resource.

CONSERVATIVE APPLICATION (per the probe's participial caution -- case 7 "catching Dick..., jerked
him forward", and the multi-verb/relative-clause hazard -- case 15 "Joab said unto the man that
told him", where BOTH Joab and the man are agents in the same clause index and the gold IS one of
them). The exclusion fires ONLY when ALL of:
  (1) the pronoun's own role is a genuine NON-agent role (role known AND != agent); role unknown
      -> abstain (cannot confirm co-argument status);
  (2) EXACTLY ONE compatible candidate holds role==agent in the pronoun's OWN clause -- guards
      against multi-verb / relative-clause / conjoined-subject clauses (>=2 same-clause agents ->
      abstain) AND against participials whose subject is tagged at a PRIOR clause index (0
      same-clause agents -> abstain, by construction: case 7's "lad" is agent of clause 0, not the
      pronoun's clause 1, so it is never excluded);
  (3) excluding it still leaves at least one compatible candidate (never exclude the only option).
Otherwise the candidate pool is unchanged and strict_cb's pick stands. This is a candidate-pool
FILTER layered before strict_cb's selection -- one variable vs strict_cb.

OPT-IN / NEVER-MUTATE: strict_cb (exp_earn_coref_pronoun_strict_cb_v1.run_learnable_strict_cb,
commit 5b266248f, atom 29614), its helpers (_EntityCb/_pick_strict_cb/_resolve_name_branch), the
query machinery (exp_wire_coref_accumulate_situation_model_v1, commit e6a3a9ee8), and the clean
link label (exp_coref_self_confidence_calibration_v1.mention_link_wrong) are all imported VERBATIM.
run_loop_principle_b is a NEW opt-in function here. Prior committed cells are unaffected.

ARMS (one clean comparison, same streams/event-slots): strict_cb (BASELINE) vs principle_b
(strict_cb + Principle-B candidate filter, applied universally since it is a hard grammatical
constraint, not an ambiguity heuristic). oracle / recency_floor / singleton_floor for query-metric
context.

MEASURE (powered combined eval, 36 passages, 130 queries, 76 pronoun decisions; g5g6 secondary):
  1. pronoun-only B3-F1: does principle_b beat strict_cb (~0.703)? name/overall must not regress.
  2. identity-demanding situation-model query acc (reuse run_arm_on_passage, iddem split): does it
     move strict_cb (~0.719) toward oracle (~0.930)?
  3. DIRECT: among flagged (n_compatible>=2) pronoun decisions, corrected (strict_cb wrong ->
     principle_b right) vs broken (strict_cb right -> principle_b wrong), net; and the same over ALL
     pronoun decisions. Plus how many decisions the filter actually fired on (coverage) and how many
     it ABSTAINED on via each guard (multi-agent / participial / role-unknown).

CAN-FAIL (pre-registered): HARD_PASS = net-positive on pronoun-B3 (>= PRONOUN_B3_MARGIN) AND
identity-demanding query (>= IDDEM_QUERY_MARGIN), with no name/overall regression and net corrected
> 0 (participial/multi-agent guards prevent regressions). PARTIAL = fixes coref-level (B3 +
corrected) but does not move the query metric. NULL/NEGATIVE = no lift or net-negative -> report the
break cases honestly. REGRESSION = name/overall B3 regresses beyond tol.

Self-test: python exp_coref_flag_fix_loop_principle_b_v1.py --self-test
Full:      python exp_coref_flag_fix_loop_principle_b_v1.py
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
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import torch  # noqa: E402

from exp_earn_coref_match_or_allocate_v1 import (  # noqa: E402
    gn_compatible,
    normalize_tokens,
    run_recency_floor,
    bcubed,
)
from exp_earn_coref_pronoun_strict_cb_v1 import (  # noqa: E402
    run_learnable_strict_cb,
    _EntityCb,
    _pick_strict_cb,
    _resolve_name_branch,
    SUBJECT_LIKE_ROLES,
)
from exp_wire_coref_accumulate_situation_model_v1 import (  # noqa: E402
    build_mention_stream_with_role,
    event_slots_for,
    run_singleton_floor,
    run_arm_on_passage,
    ROLE_VOCAB,
    D,
    MAX_EVENT_SLOTS,
    SEED,
)
from exp_coref_self_confidence_calibration_v1 import mention_link_wrong  # noqa: E402

ANCHOR_NAME = "coref_flag_fix_loop_principle_b_v1"
_GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
GOLD_PATH_COMBINED = os.path.join(_GOLD_DIR, "gold_combined_pronoun_powered_v1.jsonl")
GOLD_PATH_G5G6 = os.path.join(_GOLD_DIR, "gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

FLAG_THRESHOLD = 2  # the calibration-earned flag (n_compatible >= 2); used only for the direct
                    # corrected/broken breakdown, NOT to gate the (universal) grammatical filter.

# Pre-registered bands.
PRONOUN_B3_MARGIN = 0.02
IDDEM_QUERY_MARGIN = 0.03
REGRESSION_TOL = 0.01


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return sorted(passages, key=lambda p: p["passage_id"])


# ---------------------------------------------------------------------------
# Binding Principle B candidate filter. Returns (filtered_compat, action) where action is one of:
# "fired" (excluded exactly one same-clause agent), "abstain_agent_pronoun",
# "abstain_role_unknown", "abstain_no_same_clause_agent" (incl. participial),
# "abstain_multi_same_clause_agent", "abstain_only_option".
# ---------------------------------------------------------------------------
def _principle_b_filter(compat: List[_EntityCb], cur_clause: int,
                        cur_role: Optional[str]) -> Tuple[List[_EntityCb], str]:
    if cur_role is None:
        return compat, "abstain_role_unknown"
    if cur_role in SUBJECT_LIKE_ROLES:  # agent/subject pronoun -> Principle B does not constrain it
        return compat, "abstain_agent_pronoun"
    same_clause_agents = [e for e in compat if e.clause_role.get(cur_clause) == "agent"]
    if len(same_clause_agents) == 0:
        return compat, "abstain_no_same_clause_agent"
    if len(same_clause_agents) >= 2:
        return compat, "abstain_multi_same_clause_agent"
    excluded = same_clause_agents[0]
    remaining = [e for e in compat if e is not excluded]
    if not remaining:
        return compat, "abstain_only_option"
    return remaining, "fired"


def run_loop_principle_b(stream: List[dict]) -> Tuple[List[int], Dict[str, int]]:
    """strict_cb + Binding Principle B candidate filter on the pronoun branch. Name/nominal branch
    byte-identical to strict_cb. Returns (assigned, action_counts)."""
    entities: List[_EntityCb] = []
    next_id = 0
    assigned: List[int] = []
    actions: Dict[str, int] = {}
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                filtered, action = _principle_b_filter(compat, cur_clause, cur_role)
                actions[action] = actions.get(action, 0) + 1
                best = _pick_strict_cb(filtered, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)  # tier-4 best-effort
                actions["abstain_no_compat"] = actions.get("abstain_no_compat", 0) + 1
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
                actions["allocate_new"] = actions.get("allocate_new", 0) + 1
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
    return assigned, actions


# ---------------------------------------------------------------------------
# n_compatible per pronoun (strict_cb replay) -- for the flagged-subset corrected/broken breakdown.
# ---------------------------------------------------------------------------
def _pronoun_ncomp(stream: List[dict]) -> List[Tuple[int, int]]:
    """Returns (stream_pos, n_compatible) for each pronoun decision (strict_cb candidate pool)."""
    entities: List[_EntityCb] = []
    next_id = 0
    out: List[Tuple[int, int]] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            out.append((pos, len(compat)))
            if compat:
                best = _pick_strict_cb(compat, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = _EntityCb(next_id); next_id += 1; entities.append(best)
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
    return out


def _corrected_broken(passages: List[dict]) -> dict:
    n_flagged = 0
    corr_all = broke_all = corr_flag = broke_flag = 0
    diff_all = 0
    samples = []
    for p in passages:
        s = build_mention_stream_with_role(p)
        cb = run_learnable_strict_cb(s)
        pb, _actions = run_loop_principle_b(s)
        ncomp = dict(_pronoun_ncomp(s))
        for pos, rec in enumerate(s):
            if not rec["is_pronoun"]:
                continue
            cbw = mention_link_wrong(pos, s, cb)
            pbw = mention_link_wrong(pos, s, pb)
            flagged = ncomp.get(pos, 0) >= FLAG_THRESHOLD
            if flagged:
                n_flagged += 1
            if cb[pos] != pb[pos]:
                diff_all += 1
                if cbw and not pbw:
                    corr_all += 1
                    if flagged:
                        corr_flag += 1
                    if len(samples) < 20:
                        samples.append({"passage_id": p["passage_id"], "pos": pos,
                                        "mention_text": rec["mention_text"], "clause": rec["clause"],
                                        "role": rec.get("role"), "gold_entity": rec["gold_entity"],
                                        "outcome": "corrected", "flagged": flagged})
                elif pbw and not cbw:
                    broke_all += 1
                    if flagged:
                        broke_flag += 1
                    if len(samples) < 20:
                        samples.append({"passage_id": p["passage_id"], "pos": pos,
                                        "mention_text": rec["mention_text"], "clause": rec["clause"],
                                        "role": rec.get("role"), "gold_entity": rec["gold_entity"],
                                        "outcome": "broken", "flagged": flagged})
    return {
        "n_flagged_pronoun_decisions": n_flagged,
        "n_decisions_changed_by_filter": diff_all,
        "corrected_all": corr_all, "broken_all": broke_all, "net_all": corr_all - broke_all,
        "corrected_flagged": corr_flag, "broken_flagged": broke_flag,
        "net_flagged": corr_flag - broke_flag,
        "sample_changed_decisions": samples,
    }


# ---------------------------------------------------------------------------
def _b3(streams: List[List[dict]], preds_by_arm: Dict[str, List[List[int]]]) -> dict:
    out = {}
    for arm, preds in preds_by_arm.items():
        pairs = list(zip(streams, preds))
        out[arm] = {
            "overall": bcubed(pairs),
            "name_only": bcubed(pairs, subset="name"),
            "pronoun_only": bcubed(pairs, subset="pronoun"),
        }
    return out


def _query_metrics(passages: List[dict], streams: List[List[dict]],
                    cluster_ids_by_arm: Dict[str, List[List[str]]]) -> dict:
    arm_seed_idx = {"oracle": 0, "strict_cb": 1, "principle_b": 2,
                    "recency_floor": 3, "singleton_floor": 4}
    results: Dict[str, dict] = {}
    for arm, cid_lists in cluster_ids_by_arm.items():
        qc = qt = qc_id = qt_id = qc_pr = qt_pr = 0
        for p_idx, (p, s, cids) in enumerate(zip(passages, streams, cid_lists)):
            event_slots, n_slots, clause_to_slot = event_slots_for(s)
            gen = torch.Generator().manual_seed(SEED + p_idx * 100 + arm_seed_idx[arm])
            res = run_arm_on_passage(p, s, cids, event_slots, clause_to_slot,
                                     ROLE_VOCAB, D, gen, MAX_EVENT_SLOTS)
            qc += res["q_correct"]; qt += res["q_total"]
            qc_id += res["q_correct_iddem"]; qt_id += res["q_total_iddem"]
            qc_pr += res["q_correct_pron"]; qt_pr += res["q_total_pron"]
        results[arm] = {
            "query_accuracy_all": (qc / qt) if qt else None, "q_total": qt,
            "query_accuracy_identity_demanding": (qc_id / qt_id) if qt_id else None,
            "q_total_iddem": qt_id,
            "query_accuracy_pronoun_contributed": (qc_pr / qt_pr) if qt_pr else None,
            "q_total_pron": qt_pr,
        }
    return results


def _eval_block(passages: List[dict]) -> dict:
    streams = [build_mention_stream_with_role(p) for p in passages]
    cb_preds = [run_learnable_strict_cb(s) for s in streams]
    pb_pairs = [run_loop_principle_b(s) for s in streams]
    pb_preds = [pp for pp, _ in pb_pairs]
    rec_preds = [run_recency_floor(s) for s in streams]

    action_totals: Dict[str, int] = {}
    for _, acts in pb_pairs:
        for k, v in acts.items():
            action_totals[k] = action_totals.get(k, 0) + v

    n_pron = sum(1 for s in streams for r in s if r["is_pronoun"])
    flips = sum(1 for a, b in zip(cb_preds, pb_preds) if a != b)

    b3 = _b3(streams, {"strict_cb": cb_preds, "principle_b": pb_preds, "recency_floor": rec_preds})
    cluster_ids_by_arm = {
        "oracle": [[r["gold_entity"] for r in s] for s in streams],
        "strict_cb": [[str(c) for c in p] for p in cb_preds],
        "principle_b": [[str(c) for c in p] for p in pb_preds],
        "recency_floor": [[str(c) for c in p] for p in rec_preds],
        "singleton_floor": [[str(c) for c in run_singleton_floor(s)] for s in streams],
    }
    query = _query_metrics(passages, streams, cluster_ids_by_arm)
    return {
        "n_passages": len(passages), "n_pronoun_mentions": n_pron,
        "principle_b_flip_passages": flips,
        "principle_b_action_counts": action_totals,
        "b3": b3, "query_metric": query,
    }


# ---------------------------------------------------------------------------
def self_test() -> None:
    # (A) POSITIVE: "John saw him" -> him != John, forces the correct other-entity antecedent.
    # strict_cb ranks by most-recent subject clause STRICTLY BEFORE the pronoun's clause (c<cur),
    # so the fixture gives John a prior-subject clause (1) more recent than Bob's (0); at the "him"
    # clause (2) strict_cb picks John (subj@1 > Bob's subj@0) = WRONG (co-argument in the same
    # clause). Principle B excludes the single same-clause agent (John@2) -> forces Bob (correct).
    pos_fixture = {
        "passage_id": "pb_pos",
        "clauses": ["Bob spoke first.", "John ran outside.", "John saw him."],
        "entities": {
            "Bob": [{"clause": 0, "mention": "Bob", "role": "agent"},
                    {"clause": 2, "mention": "him", "role": "patient"}],
            "John": [{"clause": 1, "mention": "John", "role": "agent"},
                     {"clause": 2, "mention": "John", "role": "agent"}],
        },
    }
    s = build_mention_stream_with_role(pos_fixture)
    him_idx = [i for i, r in enumerate(s) if r["mention_text"] == "him"][0]
    bob_idxs = [i for i, r in enumerate(s) if r["gold_entity"] == "Bob"]
    john_idxs = [i for i, r in enumerate(s) if r["gold_entity"] == "John"]
    cb = run_learnable_strict_cb(s)
    pb, acts = run_loop_principle_b(s)
    assert cb[him_idx] in {cb[i] for i in john_idxs}, (
        f"precondition: strict_cb must mispick John (same-clause agent) for 'him'; cb={cb}")
    assert pb[him_idx] in {pb[i] for i in bob_idxs} and pb[him_idx] not in {pb[i] for i in john_idxs}, (
        f"Principle B must exclude John and force Bob for 'him'; pb={pb}")
    assert acts.get("fired", 0) >= 1, f"filter must have fired on the positive case: {acts}"
    assert cb != pb, "arms must differ on the positive fixture"

    # (B) PARTICIPIAL / CONTINUED-SUBJECT GUARD: the correct antecedent is the continued subject
    # whose agent role is tagged at a PRIOR clause (participial adjunct), NOT the pronoun's clause.
    # Principle B must NOT fire (no same-clause agent). Mirror probe case 7: "A lad caught the pony.
    # Catching Dick, jerked him forward." lad agent@0; clause1 has Dick (patient) + him (patient),
    # NO agent tagged at clause1 -> abstain_no_same_clause_agent. principle_b must equal strict_cb.
    part_fixture = {
        "passage_id": "pb_participial",
        "clauses": ["A lad caught the pony.", "Catching Dick, jerked him forward."],
        "entities": {
            "lad": [{"clause": 0, "mention": "A lad", "role": "agent"}],
            "Dick": [{"clause": 1, "mention": "Dick", "role": "patient"},
                     {"clause": 1, "mention": "him", "role": "patient"}],
        },
    }
    sp = build_mention_stream_with_role(part_fixture)
    cbp = run_learnable_strict_cb(sp)
    pbp, actsp = run_loop_principle_b(sp)
    assert pbp == cbp, f"participial guard: Principle B must NOT change the pick; cb={cbp} pb={pbp}"
    assert actsp.get("fired", 0) == 0, f"filter must NOT fire on the participial case: {actsp}"
    assert actsp.get("abstain_no_same_clause_agent", 0) >= 1, actsp

    # (C) MULTI-AGENT / RELATIVE-CLAUSE GUARD (probe case 15): a clause with TWO agents at the same
    # clause index and a non-agent pronoun -> abstain (>=2 same-clause agents), never exclude the
    # gold. "Joab met Amasa. Joab asked Amasa who told him." clause1: Joab agent (asked) + Amasa
    # agent (told) both @1; 'him' recipient@1. Principle B must abstain_multi_same_clause_agent.
    # (Proper names avoid the determiner-bridging merge that a definite "the man" would trigger.)
    multi_fixture = {
        "passage_id": "pb_multi",
        "clauses": ["Joab met Amasa.", "Joab asked Amasa who told him."],
        "entities": {
            "Joab": [{"clause": 0, "mention": "Joab", "role": "agent"},
                     {"clause": 1, "mention": "Joab", "role": "agent"},
                     {"clause": 1, "mention": "him", "role": "recipient"}],
            "Amasa": [{"clause": 0, "mention": "Amasa", "role": "patient"},
                      {"clause": 1, "mention": "Amasa", "role": "agent"}],
        },
    }
    sm = build_mention_stream_with_role(multi_fixture)
    _pbm, actsm = run_loop_principle_b(sm)
    assert actsm.get("abstain_multi_same_clause_agent", 0) >= 1, (
        f"multi-agent guard must abstain (>=2 same-clause agents): {actsm}")
    assert actsm.get("fired", 0) == 0, f"filter must NOT fire on the multi-agent case: {actsm}"

    # real code path on the actual powered gold.
    assert os.path.exists(GOLD_PATH_COMBINED), f"combined gold missing: {GOLD_PATH_COMBINED}"
    assert os.path.exists(GOLD_PATH_G5G6), f"g5g6 gold missing: {GOLD_PATH_G5G6}"
    passages = load_passages(GOLD_PATH_COMBINED)
    assert len(passages) == 36, f"expected 36 combined passages, got {len(passages)}"
    p0 = passages[0]
    s0 = build_mention_stream_with_role(p0)
    pb0, _ = run_loop_principle_b(s0)
    ev, ns, c2s = event_slots_for(s0)
    gen = torch.Generator().manual_seed(SEED)
    res = run_arm_on_passage(p0, s0, [str(c) for c in pb0], ev, c2s, ROLE_VOCAB, D, gen, MAX_EVENT_SLOTS)
    assert "q_correct_iddem" in res

    print("[SELF-TEST] PASS: Principle B fires on the positive co-argument case (John saw him -> "
          "him=Bob); participial guard abstains (continued subject tagged at prior clause); "
          "multi-agent/relative-clause guard abstains (>=2 same-clause agents, gold preserved); "
          "real query-metric code path exercised on the powered gold")


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

    passages = load_passages(GOLD_PATH_COMBINED)
    g5g6 = load_passages(GOLD_PATH_G5G6)

    combined = _eval_block(passages)
    g5g6_block = _eval_block(g5g6)
    cb_report = _corrected_broken(passages)

    cb_pron = combined["b3"]["strict_cb"]["pronoun_only"]["f1"]
    pb_pron = combined["b3"]["principle_b"]["pronoun_only"]["f1"]
    cb_name = combined["b3"]["strict_cb"]["name_only"]["f1"]
    pb_name = combined["b3"]["principle_b"]["name_only"]["f1"]
    cb_overall = combined["b3"]["strict_cb"]["overall"]["f1"]
    pb_overall = combined["b3"]["principle_b"]["overall"]["f1"]

    cb_id = combined["query_metric"]["strict_cb"]["query_accuracy_identity_demanding"]
    pb_id = combined["query_metric"]["principle_b"]["query_accuracy_identity_demanding"]
    oracle_id = combined["query_metric"]["oracle"]["query_accuracy_identity_demanding"]

    pron_lift = pb_pron - cb_pron
    id_lift = (pb_id - cb_id) if (pb_id is not None and cb_id is not None) else None
    name_regr = cb_name - pb_name
    overall_regr = cb_overall - pb_overall

    lifts_pron = pron_lift >= PRONOUN_B3_MARGIN
    lifts_iddem = (id_lift is not None and id_lift >= IDDEM_QUERY_MARGIN)
    no_regression = (name_regr <= REGRESSION_TOL) and (overall_regr <= REGRESSION_TOL)
    net_pos = cb_report["net_all"] > 0

    if lifts_pron and lifts_iddem and no_regression and net_pos:
        verdict = "HARD_PASS"
    elif not no_regression:
        verdict = "REGRESSION"
    elif (lifts_pron or net_pos) and no_regression and not lifts_iddem:
        verdict = "PARTIAL_COREF_ONLY"
    elif lifts_pron and lifts_iddem and no_regression and not net_pos:
        verdict = "PARTIAL_METRIC_MOVES_NET_ZERO"
    else:
        verdict = "NULL"

    verdict_msg = (
        f"[{verdict}] Principle B vs strict_cb (powered combined): pronoun-B3 {cb_pron:.4f}->"
        f"{pb_pron:.4f} (lift={pron_lift:+.4f}); identity-demanding query {cb_id}->{pb_id} "
        f"(lift={id_lift}; oracle={oracle_id}); name {cb_name:.4f}->{pb_name:.4f} "
        f"(regr={name_regr:+.4f}), overall {cb_overall:.4f}->{pb_overall:.4f} (regr={overall_regr:+.4f}). "
        f"DIRECT corrected/broken: all corrected={cb_report['corrected_all']} broken="
        f"{cb_report['broken_all']} net={cb_report['net_all']} (changed "
        f"{cb_report['n_decisions_changed_by_filter']} decisions); flagged-subset corrected="
        f"{cb_report['corrected_flagged']} broken={cb_report['broken_flagged']} "
        f"net={cb_report['net_flagged']}. Filter actions: {combined['principle_b_action_counts']}."
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
        "fix": "binding_principle_b_same_clause_agent_exclusion",
        "flag_threshold_for_breakdown": FLAG_THRESHOLD,
        "bands": {
            "pronoun_b3_margin": PRONOUN_B3_MARGIN,
            "iddem_query_margin": IDDEM_QUERY_MARGIN,
            "regression_tol": REGRESSION_TOL,
        },
        "headline_combined": {
            "pronoun_b3_f1": {"strict_cb": cb_pron, "principle_b": pb_pron},
            "name_b3_f1": {"strict_cb": cb_name, "principle_b": pb_name},
            "overall_b3_f1": {"strict_cb": cb_overall, "principle_b": pb_overall},
            "identity_demanding_query_acc": {"oracle": oracle_id, "strict_cb": cb_id,
                                             "principle_b": pb_id},
            "pronoun_b3_lift": pron_lift, "iddem_query_lift": id_lift,
            "name_regression": name_regr, "overall_regression": overall_regr,
        },
        "corrected_broken_combined": cb_report,
        "combined_powered": combined,
        "g5g6_only": g5g6_block,
        "gold_path_combined": GOLD_PATH_COMBINED,
        "gold_path_g5g6": GOLD_PATH_G5G6,
        "participial_guard_note": (
            "Principle B abstains unless EXACTLY ONE compatible candidate holds role==agent in the "
            "pronoun's OWN clause. Participials/continued-subject (probe case 7): the subject's agent "
            "role is tagged at a PRIOR clause index, so 0 same-clause agents -> abstain_no_same_"
            "clause_agent. Multi-verb/relative clauses (probe case 15): >=2 same-clause agents -> "
            "abstain_multi_same_clause_agent (gold preserved). See principle_b_action_counts for the "
            "achieved coverage/abstention breakdown."
        ),
        "reproducibility_note": (
            "run_learnable_strict_cb (5b266248f) + helpers + query machinery (e6a3a9ee8) + clean "
            "label (calibration v1) imported verbatim, NEVER mutated. run_loop_principle_b / "
            "_principle_b_filter are NEW opt-in functions in this file. Prior committed cells "
            "unaffected."
        ),
        "prior_commits": {
            "strict_cb_mechanism": "5b266248f",
            "loop_cycle1_topic_continuity_null": "82492af76",
            "probe_fix_tier_redirect": "b839a3176",
            "query_machinery_iddem_split": "e6a3a9ee8",
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
