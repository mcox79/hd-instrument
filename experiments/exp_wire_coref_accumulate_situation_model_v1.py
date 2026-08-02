"""exp_wire_coref_accumulate_situation_model_v1 (2026-08-02)

MILESTONE cell: wire EARNED coreference (match-or-allocate, our own mechanism, fair-test
HARD_PASS commit 27e10d3a8, possessive-gender fix a0aac7eeb) into the accumulate organ
(hdlab.situation_model_accumulate.AccumulateRegister, atom 29609 accumulate=1.0 on ORACLE
entity ids) = the REAL end-to-end situation model on real McGuffey, with NO oracle scaffolding
for entity identity.

Design: notes/wire_earned_coref_into_accumulate_organ_real_situation_model_design_2026-08-02.md

THE QUESTION: the accumulate organ was validated on ORACLE entity ids. Fed EARNED (imperfect)
coref cluster-ids instead, does it still carry the situation model?

MECHANISM REUSE (verbatim, no reimplementation):
  - hdlab.situation_model_accumulate.AccumulateRegister (add_event/decode, promoted organ)
  - experiments.exp_earn_coref_match_or_allocate_v1.run_learnable / run_recency_floor
    (imported functions, NOT reimplemented -- only consumed)
  - build_mention_stream is locally re-copied (build_mention_stream_with_role below) ONLY to
    retain the gold 'role' field the upstream version drops; the mention-construction /
    sort-key logic is byte-identical to the imported version, so coref behavior is unchanged.

ARMS (fair test, one clean comparison, same stream/event-slots across arms):
  - oracle:         cluster key = gold_entity string (the CEILING; should reproduce atom 29609
                     near-perfectly on this eval -- a low oracle ceiling here means a WIRING BUG
                     in this cell, not a real finding; VET this arm first).
  - earned:         cluster key = run_learnable(stream) cluster id (the REAL system).
  - recency_floor:  cluster key = run_recency_floor(stream) cluster id (chain-everything floor).
  - singleton_floor: cluster key = one-per-mention (no identity tracking at all).

HEADLINE METRIC = CROSS-MENTION QUERY ACCURACY (name-anchored), using p["target_queries"]
(each = {entity, query_clause, gold_role}). To answer a query for entity E at clause qc:
  (1) anchor = PREDICTED cluster id of E's first non-pronoun (name) mention (see name_anchor_map;
      gold_entity is used ONLY to locate the canonical mention, the cluster returned is the arm's
      prediction); (2) map qc to the same compacted event slot; (3) decode(anchor, slot) ->
      predicted role; (4) compare to gold_role. This is the FAIR situation-model test: when the
  event at qc was contributed by a PRONOUN ("he did X"), only CORRECT coref links that pronoun
  into E's name cluster so the event is retrievable -- singleton coref (pronoun in its own
  cluster) MUST miss; chain-everything (name cluster absorbs other entities) MUST corrupt on
  slot collisions. WHY the per-mention decode metric was NOT used as headline: singleton scores
  ~1.0 on it (1 event/register, zero crosstalk) so it rewards NOT-merging -- the opposite of what
  a situation model is for -- and cannot show coref adds value. Per-mention decode is kept as a
  SECONDARY diagnostic (validly shows organ wiring correct via oracle + earned/oracle crosstalk).

CAN-FAIL BANDS (pre-registered BEFORE running; all on the HEADLINE query metric):
  - MILESTONE_MET:        earned_q within MILESTONE_MARGIN (0.05) of oracle_q AND earned_q beats
                           BOTH singleton_q and recency_q by >= FLOOR_GAP_MARGIN (0.05).
  - BOTTLENECK_QUANTIFIED: earned_q beats both floors by >= FLOOR_GAP_MARGIN but stays below the
                           milestone band vs oracle -- coref adds value but is the quantified
                           bottleneck; states remaining coref headroom.
  - INVESTIGATE_NULL:      earned_q fails to clear EITHER floor by >= FLOOR_GAP_MARGIN -- earned
                           coref adds little at the situation-model level; check vs the coref
                           fair-test HARD_PASS (27e10d3a8) -- flag, do not spin a positive story.
  - QUERY_METRIC_NOT_DISCRIMINATING: singleton_q did NOT collapse vs oracle_q (gap < FLOOR_GAP) --
                           the query metric is not discriminating on this gold; report, do not spin.
  - WIRING_BUG_SUSPECTED:  oracle per-mention decode < ORACLE_CEILING_FLOOR (0.90) -- the organ or
                           the slot-remap has a bug in THIS cell; investigate before trusting arms.

Event-slot mapping: per passage, distinct clause indices are compacted to slots 0..k-1
(dense-ranked, sorted). Collision policy (documented, not hidden): if the same (cluster_id,
event_slot) pair recurs for a later mention (either two gold mentions truly share a clause+
cluster, or -- the interesting case -- a coref MERGE puts two different gold entities' events
into the same cluster at the same slot), only the FIRST such mention's add_event call binds the
register; later same-key mentions are still scored against that already-bound slot (this is the
real end-to-end penalty a merge inflicts) and counted in n_collisions.

Roles are SUPPLIED gold here (the extraction organ is a separate, already-~0.60 layer); this
cell isolates the identity(coref)+accumulate integration only.

Self-test: python exp_wire_coref_accumulate_situation_model_v1.py --self-test
Full:      python exp_wire_coref_accumulate_situation_model_v1.py --timeout 120
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import torch  # noqa: E402

from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
from exp_earn_coref_match_or_allocate_v1 import (  # noqa: E402
    is_pronoun_mention,
    gender_number_for,
    run_learnable,
    run_recency_floor,
)
import exp_checkpoint as ckpt  # noqa: E402 (per-unit checkpoint/resume, MANDATORY per CLAUDE.md)

ANCHOR_NAME = "wire_coref_accumulate_situation_model_v1"
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multientity_dense_v1.jsonl"
)

# Role vocab = union across dense gold, per the design doc (7 of the 9 actually occur in this
# eval; the extra 2 are declared for forward-compat with other gold files sharing this vocab).
ROLE_VOCAB = [
    "agent", "experiencer", "theme", "patient", "recipient",
    "possessor", "addressee", "goal", "instrument",
]
D = 1024  # project default N per CLAUDE.md
MAX_EVENT_SLOTS = 16  # headroom; dense gold max distinct clauses/passage observed = 8
SEED = 20260802

ARM_ORDER = ["oracle", "earned", "recency_floor", "singleton_floor"]

MILESTONE_MARGIN = 0.05
FLOOR_GAP_MARGIN = 0.05
ORACLE_CEILING_FLOOR = 0.90


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return passages


def build_mention_stream_with_role(passage: dict) -> List[dict]:
    """Byte-identical mention-construction + sort-key logic to
    exp_earn_coref_match_or_allocate_v1.build_mention_stream (and its dense re-export) -- the
    ONLY difference is retaining the gold 'role' field, which the upstream version drops. This
    does not change coref behavior: run_learnable/run_recency_floor only read gender/number/
    is_pronoun/mention_text/has_determiner, so the extra 'role' key is inert to them."""
    clauses = passage["clauses"]
    raw = []
    for ent_name, mentions in passage["entities"].items():
        for m in mentions:
            mtxt = m["mention"]
            if mtxt.strip().startswith("("):
                continue
            clause_idx = m["clause"]
            clause_text = clauses[clause_idx].lower()
            first_tok = mtxt.split()[0].lower().strip(".,'\"!?;:()/")
            pos = clause_text.find(first_tok)
            if pos < 0:
                pos = 0
            is_pron = is_pronoun_mention(mtxt)
            gender, number = gender_number_for(mtxt, is_pron)
            first_word = mtxt.strip().split()[0].lower().strip(".,'\"") if mtxt.strip() else ""
            has_determiner = first_word in {"the", "a", "an"}
            raw.append(
                {
                    "gold_entity": ent_name,
                    "clause": clause_idx,
                    "mention_text": mtxt,
                    "is_pronoun": is_pron,
                    "gender": gender,
                    "number": number,
                    "text_pos": pos,
                    "has_determiner": has_determiner,
                    "role": m["role"],
                }
            )
    raw.sort(key=lambda r: (r["clause"], r["text_pos"]))
    return raw


def event_slots_for(stream: List[dict]) -> Tuple[List[int], int, Dict[int, int]]:
    """Compact distinct clause indices in this stream to dense slots 0..k-1 (sorted).
    Returns (per-mention slot list, n_slots, clause_index -> slot map)."""
    distinct_clauses = sorted({r["clause"] for r in stream})
    clause_to_slot = {c: i for i, c in enumerate(distinct_clauses)}
    return [clause_to_slot[r["clause"]] for r in stream], len(distinct_clauses), clause_to_slot


def name_anchor_map(stream: List[dict], cluster_ids: List[str]) -> Dict[str, str]:
    """For each gold entity in the stream, the PREDICTED cluster id of its canonical NAME anchor.

    Anchor rule (documented): the anchor for entity E is the FIRST non-pronoun (name/definite)
    mention of E in stream order; if E has only pronoun mentions, its first mention. gold_entity
    is used ONLY to LOCATE E's canonical mention -- the cluster id returned is the arm's PREDICTED
    cluster, not a gold label -- so the query metric fairly rewards coref that links E's pronoun-
    contributed events into E's name cluster and penalizes both mis-splits (pronoun in a separate
    cluster -> event unreachable) and mis-merges (name cluster absorbs another entity -> wrong role)."""
    anchor: Dict[str, str] = {}
    for rec, cid in zip(stream, cluster_ids):
        e = rec["gold_entity"]
        if e in anchor:
            if not rec["is_pronoun"] and anchor[e][1]:  # upgrade pronoun-anchor to a name-anchor
                anchor[e] = (cid, False)
            continue
        anchor[e] = (cid, rec["is_pronoun"])
    return {e: cid for e, (cid, _was_pron) in anchor.items()}


def pronoun_contributed_queries(passage: dict, stream: List[dict]) -> Dict[int, bool]:
    """For each query index, True iff the event at its query_clause was contributed by a PRONOUN
    mention of the queried entity (the discriminating subset: only correct coref links that
    pronoun into the entity's name cluster so the event is retrievable). Arm-independent."""
    out: Dict[int, bool] = {}
    for qi, q in enumerate(passage.get("target_queries", [])):
        E, qc = q["entity"], q["query_clause"]
        e_at_qc = [r for r in stream if r["gold_entity"] == E and r["clause"] == qc]
        out[qi] = bool(e_at_qc) and e_at_qc[0]["is_pronoun"]
    return out


def run_singleton_floor(stream: List[dict]) -> List[int]:
    """No identity tracking at all: every mention is its own entity."""
    return list(range(len(stream)))


def cluster_ids_for_arm(arm: str, stream: List[dict]) -> List[str]:
    if arm == "oracle":
        return [r["gold_entity"] for r in stream]
    if arm == "earned":
        return [str(c) for c in run_learnable(stream)]
    if arm == "recency_floor":
        return [str(c) for c in run_recency_floor(stream)]
    if arm == "singleton_floor":
        return [str(c) for c in run_singleton_floor(stream)]
    raise ValueError(f"unknown arm {arm!r}")


def run_arm_on_passage(
    passage: dict,
    stream: List[dict],
    cluster_ids: List[str],
    event_slots: List[int],
    clause_to_slot: Dict[int, int],
    role_vocab: List[str],
    d: int,
    generator: torch.Generator,
    max_event_slots: int,
) -> dict:
    """Build one AccumulateRegister for this (passage, arm), add_event per mention (first
    occurrence of a (cluster_id, event_slot) key only -- collision policy above). Score BOTH:
      (headline) the cross-mention QUERY metric via name-anchored cluster decode (target_queries);
      (secondary) the per-mention decode of every mention-event (organ-wiring + crosstalk diag)."""
    reg = AccumulateRegister(role_vocab, d, generator, max_event_slots=max_event_slots)
    added_keys = set()
    n_collisions = 0
    for rec, cid, slot in zip(stream, cluster_ids, event_slots):
        key = (cid, slot)
        if key in added_keys:
            n_collisions += 1
            continue
        added_keys.add(key)
        reg.add_event(cid, rec["role"], slot)

    # ---- HEADLINE: cross-mention query metric (name-anchored) ----
    anchor = name_anchor_map(stream, cluster_ids)
    pron_map = pronoun_contributed_queries(passage, stream)
    q_correct = q_total = 0
    q_correct_pron = q_total_pron = 0
    q_skipped = 0
    for qi, q in enumerate(passage.get("target_queries", [])):
        E, qc, gold_role = q["entity"], q["query_clause"], q["gold_role"]
        if E not in anchor or qc not in clause_to_slot:
            q_skipped += 1  # entity absent from stream or clause had no mentions -> unanswerable
            continue
        cid = anchor[E]
        slot = clause_to_slot[qc]
        pred_role, _ = reg.decode(cid, slot)
        ok = int(pred_role == gold_role)
        q_correct += ok
        q_total += 1
        if pron_map.get(qi, False):
            q_correct_pron += ok
            q_total_pron += 1

    # ---- SECONDARY: per-mention decode ----
    n_correct = 0
    n_total = 0
    for rec, cid, slot in zip(stream, cluster_ids, event_slots):
        pred_role, _scores = reg.decode(cid, slot)
        n_correct += int(pred_role == rec["role"])
        n_total += 1

    return {
        "q_correct": q_correct,
        "q_total": q_total,
        "q_correct_pron": q_correct_pron,
        "q_total_pron": q_total_pron,
        "q_skipped": q_skipped,
        "n_correct": n_correct,
        "n_total": n_total,
        "accuracy": (n_correct / n_total) if n_total else None,
        "n_collisions": n_collisions,
        "n_clusters": len(set(cluster_ids)),
    }


# ---------------------------------------------------------------------------
# Self-test: exercises the real path (AccumulateRegister, event-slot remap, collision policy)
# on a tiny fixture with a KNOWN answer, plus corrupts identity on purpose to prove the metric
# is sensitive to merge-induced crosstalk (the whole point of this cell).
# ---------------------------------------------------------------------------
def _mk(gold_entity, clause, role, mention_text, is_pronoun):
    return {"gold_entity": gold_entity, "clause": clause, "role": role,
            "mention_text": mention_text, "is_pronoun": is_pronoun}


def self_test() -> None:
    role_vocab = ["agent", "theme", "patient", "recipient"]
    d = 256

    # Fixture with a PRONOUN-contributed cross-mention query -- the discriminating case:
    #   Alice: name "Alice"@c0 (agent), pronoun "she"@c1 (theme)   <- her c1 event is via a pronoun
    #   Bob:   name "Bob"@c1 (patient)
    # Query {Alice, clause 1, theme}: retrievable ONLY if coref links "she" into Alice's name
    # cluster. Oracle does; singleton does NOT (she is a separate cluster from "Alice").
    stream = [
        _mk("Alice", 0, "agent", "Alice", False),
        _mk("Alice", 1, "theme", "she", True),
        _mk("Bob", 1, "patient", "Bob", False),
    ]
    passage = {"target_queries": [{"entity": "Alice", "query_clause": 1, "gold_role": "theme"}]}
    event_slots, n_slots, clause_to_slot = event_slots_for(stream)
    assert n_slots == 2 and event_slots == [0, 1, 1] and clause_to_slot == {0: 0, 1: 1}

    pron_map = pronoun_contributed_queries(passage, stream)
    assert pron_map == {0: True}, f"query 0 must be classified pronoun-contributed: {pron_map}"

    def run(ids, seed=1, mes=4):
        gen = torch.Generator().manual_seed(seed)
        return run_arm_on_passage(passage, stream, ids, event_slots, clause_to_slot,
                                  role_vocab, d, gen, mes)

    # ORACLE: gold_entity keys -> "she" bound into Alice cluster -> query hits.
    oracle_ids = [r["gold_entity"] for r in stream]
    res_oracle = run(oracle_ids)
    assert res_oracle["q_total"] == 1 and res_oracle["q_correct"] == 1, (
        f"oracle must answer the pronoun-contributed query correctly: {res_oracle}")
    assert res_oracle["q_total_pron"] == 1 and res_oracle["q_correct_pron"] == 1
    assert res_oracle["accuracy"] == 1.0, f"oracle per-mention decode must be perfect: {res_oracle}"

    # SINGLETON: every mention its own cluster -> "she" is NOT in Alice's name cluster -> the
    # query decodes a slot that Alice's name cluster never bound -> MISS. This is the tell the
    # per-mention metric hid: singleton must COLLAPSE on the query metric.
    singleton_ids = [str(i) for i in range(len(stream))]
    res_single = run(singleton_ids)
    assert res_single["q_correct_pron"] == 0, (
        f"singleton MUST miss the pronoun-contributed query (no identity link): {res_single}")
    assert res_single["accuracy"] == 1.0, (
        f"singleton per-mention decode is still 1.0 (1 event/register) -- exactly why the query "
        f"metric is needed as the headline: {res_single}")
    assert res_single["q_correct"] < res_oracle["q_correct"], (
        f"singleton query score must fall below oracle: single={res_single} oracle={res_oracle}")

    # MERGED: force everything into one cluster -> per-mention decode corrupts via slot collision.
    merged_ids = ["M", "M", "M"]
    res_merged = run(merged_ids)
    assert res_merged["n_collisions"] == 1, f"Bob@c1 collides with she@c1 in one cluster: {res_merged}"
    assert res_merged["accuracy"] < 1.0, f"merge must corrupt per-mention decode: {res_merged}"

    # real gold path + real coref mechanism, sanity only (not scored).
    assert os.path.exists(GOLD_PATH), f"dense gold file missing: {GOLD_PATH}"
    passages = load_passages(GOLD_PATH)
    assert len(passages) == 18, f"expected 18 dense passages, got {len(passages)}"
    real_stream = build_mention_stream_with_role(passages[0])
    assert len(real_stream) > 0
    assert all("role" in r for r in real_stream), "role field must survive the local stream builder"
    _rs, real_n_slots, _c2s = event_slots_for(real_stream)
    assert real_n_slots <= MAX_EVENT_SLOTS
    _ = run_learnable(real_stream)

    print("[SELF-TEST] PASS: query metric discriminates (singleton MISSES pronoun-contributed "
          "query while its per-mention decode stays 1.0; oracle hits), collision policy, "
          "merge-corrupts-decode, and real gold/coref path all verified")


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


def main(timeout_s: float) -> None:
    t0 = time.perf_counter()
    output_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
    os.makedirs(output_dir, exist_ok=True)

    passages = sorted(load_passages(GOLD_PATH), key=lambda p: p["passage_id"])
    streams = {p["passage_id"]: build_mention_stream_with_role(p) for p in passages}

    done = ckpt.completed_units(output_dir)
    total_units = len(passages) * len(ARM_ORDER)
    n_run = 0
    for p_idx, p in enumerate(passages):
        pid = p["passage_id"]
        stream = streams[pid]
        event_slots, n_slots, clause_to_slot = event_slots_for(stream)
        assert n_slots <= MAX_EVENT_SLOTS, (
            f"passage {pid} has {n_slots} distinct clause slots > MAX_EVENT_SLOTS={MAX_EVENT_SLOTS}"
        )
        for a_idx, arm in enumerate(ARM_ORDER):
            key = ckpt.unit_key(pid, arm)
            if key in done:
                continue
            if time.perf_counter() - t0 > timeout_s:
                raise TimeoutError(
                    f"exceeded --timeout {timeout_s}s after {n_run}/{total_units} units; "
                    f"resume by re-running (checkpointed)."
                )
            cluster_ids = cluster_ids_for_arm(arm, stream)
            gen = torch.Generator().manual_seed(SEED + p_idx * 100 + a_idx)
            res = run_arm_on_passage(p, stream, cluster_ids, event_slots, clause_to_slot,
                                     ROLE_VOCAB, D, gen, MAX_EVENT_SLOTS)
            res["passage_id"] = pid
            res["arm"] = arm
            res["n_distinct_clause_slots"] = n_slots
            ckpt.record_unit(output_dir, key, res)
            n_run += 1

    units = ckpt.load_units(output_dir)
    assert len(units) == total_units, f"expected {total_units} units, have {len(units)}"

    per_arm: Dict[str, dict] = {}
    for arm in ARM_ORDER:
        recs = [u for k, u in units.items() if u["arm"] == arm]
        # HEADLINE query metric (cross-mention, name-anchored)
        q_correct = sum(r["q_correct"] for r in recs)
        q_total = sum(r["q_total"] for r in recs)
        q_correct_pron = sum(r["q_correct_pron"] for r in recs)
        q_total_pron = sum(r["q_total_pron"] for r in recs)
        q_skipped = sum(r["q_skipped"] for r in recs)
        # SECONDARY per-mention decode metric
        n_correct = sum(r["n_correct"] for r in recs)
        n_total = sum(r["n_total"] for r in recs)
        n_collisions = sum(r["n_collisions"] for r in recs)
        per_arm[arm] = {
            "query_accuracy": (q_correct / q_total) if q_total else None,
            "q_correct": q_correct,
            "q_total": q_total,
            "query_accuracy_pronoun_contributed": (q_correct_pron / q_total_pron) if q_total_pron else None,
            "q_correct_pron": q_correct_pron,
            "q_total_pron": q_total_pron,
            "q_skipped": q_skipped,
            "per_mention_accuracy": (n_correct / n_total) if n_total else None,
            "n_correct": n_correct,
            "n_total": n_total,
            "n_collisions": n_collisions,
            "n_passages": len(recs),
        }

    # HEADLINE metric = cross-mention query accuracy
    oracle_q = per_arm["oracle"]["query_accuracy"]
    earned_q = per_arm["earned"]["query_accuracy"]
    recency_q = per_arm["recency_floor"]["query_accuracy"]
    singleton_q = per_arm["singleton_floor"]["query_accuracy"]
    value_ceiling = (earned_q / oracle_q) if oracle_q else None
    # SECONDARY (per-mention) kept for organ-wiring + crosstalk diagnostics
    oracle_pm = per_arm["oracle"]["per_mention_accuracy"]
    earned_pm = per_arm["earned"]["per_mention_accuracy"]

    beats_singleton = (earned_q is not None and singleton_q is not None
                       and (earned_q - singleton_q) >= FLOOR_GAP_MARGIN)
    beats_recency = (earned_q is not None and recency_q is not None
                     and (earned_q - recency_q) >= FLOOR_GAP_MARGIN)
    within_ceiling = (earned_q is not None and oracle_q is not None
                      and earned_q >= oracle_q - MILESTONE_MARGIN)
    # discriminating precondition: singleton must COLLAPSE vs oracle on the query metric, else
    # the query metric is not discriminating and no milestone can be claimed on it.
    query_discriminates = (oracle_q is not None and singleton_q is not None
                           and (oracle_q - singleton_q) >= FLOOR_GAP_MARGIN)

    # ---- can-fail bands (pre-registered, see docstring; HEADLINE = query metric) ----
    if oracle_q is None or oracle_pm is None or oracle_pm < ORACLE_CEILING_FLOOR:
        verdict = "WIRING_BUG_SUSPECTED"
        verdict_msg = (
            f"oracle per-mention decode={oracle_pm} below ORACLE_CEILING_FLOOR={ORACLE_CEILING_FLOOR} "
            f"(or query metric empty) -- the accumulate organ or the event-slot remap has a bug in "
            f"THIS cell; investigate before trusting earned/floor arms."
        )
    elif not query_discriminates:
        verdict = "QUERY_METRIC_NOT_DISCRIMINATING"
        verdict_msg = (
            f"singleton query_acc={singleton_q:.4f} did NOT collapse vs oracle={oracle_q:.4f} "
            f"(gap < {FLOOR_GAP_MARGIN}) -- the query metric is not discriminating on this gold; "
            f"no milestone can be claimed. Report, do not spin."
        )
    elif within_ceiling and beats_singleton and beats_recency:
        verdict = "MILESTONE_MET"
        verdict_msg = (
            f"MILESTONE_MET (query metric): earned={earned_q:.4f} within {MILESTONE_MARGIN} of "
            f"oracle ceiling={oracle_q:.4f} (value_ceiling={value_ceiling:.4f}) AND beats both "
            f"floors -- singleton={singleton_q:.4f}, recency={recency_q:.4f} (both by >= "
            f"{FLOOR_GAP_MARGIN}). Earned coref carries cross-mention role retrieval end-to-end on "
            f"real McGuffey, no oracle scaffolding."
        )
    elif beats_singleton and beats_recency:
        verdict = "BOTTLENECK_QUANTIFIED"
        verdict_msg = (
            f"BOTTLENECK_QUANTIFIED (query metric): earned={earned_q:.4f} beats singleton="
            f"{singleton_q:.4f} and recency={recency_q:.4f} (both by >= {FLOOR_GAP_MARGIN}) but "
            f"stays below the milestone band vs oracle={oracle_q:.4f} (value_ceiling="
            f"{value_ceiling:.4f}). Coref adds value but is the quantified bottleneck; remaining "
            f"headroom oracle-earned={(oracle_q - earned_q):.4f}."
        )
    elif (not beats_singleton) or (not beats_recency):
        verdict = "INVESTIGATE_NULL"
        verdict_msg = (
            f"INVESTIGATE_NULL (query metric): earned={earned_q:.4f} does NOT clear both floors by "
            f">= {FLOOR_GAP_MARGIN} (singleton={singleton_q:.4f}, recency={recency_q:.4f}). Earned "
            f"coref adds little at the situation-model level; check against the coref fair-test "
            f"HARD_PASS (commit 27e10d3a8) -- investigate, do not spin."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND (query metric): earned={earned_q:.4f}, oracle={oracle_q:.4f}, "
            f"singleton={singleton_q:.4f}, recency={recency_q:.4f} -- no clean band."
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
        "seed": SEED,
        "d": D,
        "max_event_slots": MAX_EVENT_SLOTS,
        "role_vocab": ROLE_VOCAB,
        "gold_path": GOLD_PATH,
        "n_passages": len(passages),
        "arm_order": ARM_ORDER,
        "per_arm": per_arm,
        "headline_metric": "cross_mention_query_accuracy_name_anchored",
        "query_accuracy": {
            "oracle": oracle_q, "earned": earned_q,
            "recency_floor": recency_q, "singleton_floor": singleton_q,
        },
        "query_accuracy_pronoun_contributed": {
            arm: per_arm[arm]["query_accuracy_pronoun_contributed"] for arm in ARM_ORDER
        },
        "n_queries_total": per_arm["oracle"]["q_total"],
        "n_queries_pronoun_contributed": per_arm["oracle"]["q_total_pron"],
        "n_queries_skipped": per_arm["oracle"]["q_skipped"],
        "value_ceiling_earned_over_oracle_query": value_ceiling,
        "query_discriminates": query_discriminates,
        "earned_beats_singleton": beats_singleton,
        "earned_beats_recency": beats_recency,
        "earned_within_ceiling": within_ceiling,
        "secondary_per_mention_accuracy": {
            arm: per_arm[arm]["per_mention_accuracy"] for arm in ARM_ORDER
        },
        "secondary_note": (
            "per_mention decode is a SECONDARY diagnostic only: it validly confirms organ wiring "
            "(oracle high) + earned-vs-oracle crosstalk, but singleton scores ~1.0 on it (1 event/"
            "register, no crosstalk) so it CANNOT show coref adds value -- the query metric is the "
            "headline."
        ),
        "bands": {
            "milestone_margin": MILESTONE_MARGIN,
            "floor_gap_margin": FLOOR_GAP_MARGIN,
            "oracle_ceiling_floor": ORACLE_CEILING_FLOOR,
        },
        "timeout_s": timeout_s,
        "final_metrics_atomicity": "tmp_replace",
        "checkpointed": True,
        "n_units_total": total_units,
        "n_units_ran_this_invocation": n_run,
        "prior_commits": {
            "coref_fair_test_hard_pass": "27e10d3a8",
            "possessive_gender_fix": "a0aac7eeb",
            "accumulate_organ_atom": "29609",
        },
    }
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    print(f"[{ANCHOR_NAME}] {verdict}")
    print(verdict_msg)
    print(f"metrics written to {final}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--timeout", type=float, default=120.0,
        help=(
            "formula: 18 passages x 4 arms = 72 units, each unit is O(n_mentions^0) FHRR bind/"
            "unbind on d=1024 vectors (<50ms/unit measured on comparable cells); 120s gives "
            "~1.6s/unit headroom, generous for a CPU-only run with import overhead."
        ),
    )
    args = parser.parse_args()
    _output_dir_for_crash = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        if args.self_test:
            self_test()
        else:
            main(args.timeout)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
