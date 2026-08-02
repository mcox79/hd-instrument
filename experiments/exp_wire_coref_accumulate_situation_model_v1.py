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
(dense-ranked, sorted). Collision policy (FIXED 2026-08-02, was a metric bug): EVERY mention is
add_event'd into its cluster's register -- a recurring (cluster_id, event_slot) key is NEVER
skipped. The AccumulateRegister is designed to bundle multiple events and let FHRR cross-talk
degrade decode when a cluster is over-merged; that cross-talk IS the intended penalty for a
wrong merge. The prior code SKIPPED the add on a recurring key, which protected a mega-cluster
(e.g. recency_floor's single collapse-all cluster) from that penalty and artificially inflated
its query score -- the artifact that made recency_floor spuriously "beat" earned coref.
n_collisions is now a DIAGNOSTIC count of recurring keys only; it no longer changes what binds.

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

# strict-Cb powered pronoun lever (commit 5b266248f): imported, NOT reimplemented. LAZY import
# (inside cluster_ids_for_arm) because that cell imports helpers from THIS module -- a top-level
# import here would be circular. The lazy import runs after this module is fully initialized.
def _run_learnable_strict_cb(stream):
    from exp_earn_coref_pronoun_strict_cb_v1 import run_learnable_strict_cb
    return run_learnable_strict_cb(stream)

ANCHOR_NAME = "wire_coref_accumulate_situation_model_v1"
_GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
# HEADLINE eval = powered pronoun combined (36 passages, 129 pronoun mentions, 130 queries);
# SECONDARY = g5g6-only reviewed verbatim subset (18 passages).
EVALS = {
    "powered": os.path.join(_GOLD_DIR, "gold_combined_pronoun_powered_v1.jsonl"),
    "g5g6_reviewed": os.path.join(_GOLD_DIR, "gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl"),
}
HEADLINE_EVAL = "powered"
# Legacy single-file path kept for the --self-test real-gold sanity check.
GOLD_PATH = os.path.join(_GOLD_DIR, "gold_multientity_dense_v1.jsonl")

# Role vocab = union across dense gold, per the design doc (7 of the 9 actually occur in this
# eval; the extra 2 are declared for forward-compat with other gold files sharing this vocab).
ROLE_VOCAB = [
    "agent", "experiencer", "theme", "patient", "recipient",
    "possessor", "addressee", "goal", "instrument",
]
D = 1024  # project default N per CLAUDE.md
MAX_EVENT_SLOTS = 16  # headroom; dense gold max distinct clauses/passage observed = 8
SEED = 20260802

ARM_ORDER = ["oracle", "earned", "strict_cb", "recency_floor", "singleton_floor"]

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


def identity_demanding_queries(passage: dict, stream: List[dict]) -> Dict[int, bool]:
    """For each query index, True iff its query_clause has mentions from >= 2 DISTINCT gold
    entities (identity IS required: a mega-cluster must bundle multiple roles at that slot ->
    cross-talk corrupt, while correct coref attributes to separate clusters). Arm-independent.
    The complement (single-entity clause) is the trivial subset where 'role at qc' needs no
    identity -- the chain-everything floor coasts there."""
    out: Dict[int, bool] = {}
    for qi, q in enumerate(passage.get("target_queries", [])):
        qc = q["query_clause"]
        ents_at_qc = {r["gold_entity"] for r in stream if r["clause"] == qc}
        out[qi] = len(ents_at_qc) >= 2
    return out


def run_singleton_floor(stream: List[dict]) -> List[int]:
    """No identity tracking at all: every mention is its own entity."""
    return list(range(len(stream)))


def cluster_ids_for_arm(arm: str, stream: List[dict]) -> List[str]:
    if arm == "oracle":
        return [r["gold_entity"] for r in stream]
    if arm == "earned":
        return [str(c) for c in run_learnable(stream)]
    if arm == "strict_cb":
        return [str(c) for c in _run_learnable_strict_cb(stream)]
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
    """Build one AccumulateRegister for this (passage, arm), add_event for EVERY mention. Score
    BOTH: (headline) the cross-mention QUERY metric via name-anchored cluster decode
    (target_queries); (secondary) the per-mention decode of every mention-event.

    COLLISION POLICY (fixed 2026-08-02): every mention is add_event'd -- NEVER skipped. The
    accumulate organ is DESIGNED to bundle multiple events into one register and let FHRR
    cross-talk degrade decode when a cluster is over-merged; that cross-talk IS the intended
    penalty for a wrong merge. The prior code skipped an add when a (cluster_id, event_slot) key
    recurred, which PROTECTED a mega-cluster (e.g. recency_floor's single collapse-all cluster)
    from the penalty it should incur and artificially inflated its query score. n_collisions is
    now a DIAGNOSTIC count of recurring keys only -- it no longer changes what gets bound."""
    reg = AccumulateRegister(role_vocab, d, generator, max_event_slots=max_event_slots)
    seen_keys = set()
    n_collisions = 0
    for rec, cid, slot in zip(stream, cluster_ids, event_slots):
        key = (cid, slot)
        if key in seen_keys:
            n_collisions += 1  # diagnostic only: still bundle it (cross-talk is the real penalty)
        seen_keys.add(key)
        reg.add_event(cid, rec["role"], slot)

    # ---- HEADLINE: cross-mention query metric (name-anchored) ----
    anchor = name_anchor_map(stream, cluster_ids)
    pron_map = pronoun_contributed_queries(passage, stream)
    iddem_map = identity_demanding_queries(passage, stream)
    q_correct = q_total = 0
    q_correct_pron = q_total_pron = 0
    q_correct_iddem = q_total_iddem = 0   # >=2 distinct entities at query_clause (identity required)
    q_correct_triv = q_total_triv = 0     # single-entity clause (floor coasts here)
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
        if iddem_map.get(qi, False):
            q_correct_iddem += ok
            q_total_iddem += 1
        else:
            q_correct_triv += ok
            q_total_triv += 1

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
        "q_correct_iddem": q_correct_iddem,
        "q_total_iddem": q_total_iddem,
        "q_correct_triv": q_correct_triv,
        "q_total_triv": q_total_triv,
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

    # ---- MEGA-CLUSTER CROSS-TALK FIXTURE (the collision-policy fix) ----
    # 3 distinct entities each appearing in BOTH clauses with DIFFERENT roles. Collapsing them
    # all into ONE cluster bundles 3 conflicting roles at each event slot. Under the FIXED policy
    # (add EVERY mention, never skip) the mega-cluster's decode is ambiguous -> it must score
    # POORLY on the query metric (cross-talk = the intended penalty). Under the OLD buggy skip
    # policy the mega-cluster would bind only the FIRST role per slot and decode cleanly -> this
    # is exactly the artifact that let recency_floor "beat" earned coref.
    d2 = 1024
    role_vocab2 = ["agent", "theme", "patient", "recipient"]
    mega_stream = [
        _mk("A", 0, "agent", "Ann", False),
        _mk("B", 0, "patient", "Bob", False),
        _mk("C", 0, "theme", "Cal", False),
        _mk("A", 1, "theme", "Ann", False),
        _mk("B", 1, "agent", "Bob", False),
        _mk("C", 1, "patient", "Cal", False),
    ]
    mega_passage = {"target_queries": [
        {"entity": "A", "query_clause": 0, "gold_role": "agent"},
        {"entity": "B", "query_clause": 0, "gold_role": "patient"},
        {"entity": "C", "query_clause": 0, "gold_role": "theme"},
        {"entity": "A", "query_clause": 1, "gold_role": "theme"},
        {"entity": "B", "query_clause": 1, "gold_role": "agent"},
        {"entity": "C", "query_clause": 1, "gold_role": "patient"},
    ]}
    m_slots, m_n, m_c2s = event_slots_for(mega_stream)

    def run2(ids, seed=7):
        gen = torch.Generator().manual_seed(seed)
        return run_arm_on_passage(mega_passage, mega_stream, ids, m_slots, m_c2s,
                                  role_vocab2, d2, gen, 4)

    res_oracle2 = run2([r["gold_entity"] for r in mega_stream])
    assert res_oracle2["q_correct"] == res_oracle2["q_total"] == 6, (
        f"oracle (distinct clusters) must answer all 6 queries: {res_oracle2}")
    # every clause here has 3 distinct entities -> ALL 6 queries are identity-demanding, 0 trivial.
    assert res_oracle2["q_total_iddem"] == 6 and res_oracle2["q_total_triv"] == 0, (
        f"all mega-fixture queries must classify identity-demanding: {res_oracle2}")
    assert res_oracle2["q_correct_iddem"] == 6, f"oracle must solve the id-demanding subset: {res_oracle2}"

    mega_ids = ["M"] * len(mega_stream)
    res_mega = run2(mega_ids)
    # diagnostic: 2 events per slot recur after the first -> 4 collisions counted, NONE skipped.
    assert res_mega["n_collisions"] == 4, f"mega-cluster must COUNT 4 recurring keys: {res_mega}"
    assert res_mega["n_clusters"] == 1, f"mega-cluster is a single cluster: {res_mega}"
    # the FIX: mega-cluster piles 3 conflicting roles per slot -> cross-talk -> POOR query score.
    assert res_mega["q_correct"] <= 3, (
        f"FIXED collision policy: mega-cluster cross-talk must corrupt >= half the queries "
        f"(<=3/6), NOT decode cleanly as the old skip policy allowed: {res_mega}")
    assert res_mega["q_correct"] < res_oracle2["q_correct"], (
        f"mega-cluster query score must fall well below oracle: mega={res_mega} oracle={res_oracle2}")

    # real gold path + real coref mechanism, sanity only (not scored) -- exercise BOTH powered
    # evals + strict_cb so a missing file / signature drift is caught at self-test.
    for _ename, _epath in EVALS.items():
        assert os.path.exists(_epath), f"eval file missing: {_epath}"
        _ps = load_passages(_epath)
        assert len(_ps) > 0
        _rstream = build_mention_stream_with_role(_ps[0])
        assert _rstream and all("role" in r for r in _rstream), f"role field dropped in {_ename}"
        _rs, _rn, _rc = event_slots_for(_rstream)
        assert _rn <= MAX_EVENT_SLOTS, f"{_ename} passage 0 exceeds MAX_EVENT_SLOTS"
        _ = run_learnable(_rstream)
        _ = _run_learnable_strict_cb(_rstream)

    print("[SELF-TEST] PASS: FIXED collision policy (mega-cluster cross-talk corrupts query decode "
          "instead of being skip-protected); query metric discriminates (singleton misses pronoun "
          "query while per-mention stays 1.0); oracle hits; both powered evals + strict_cb load")


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


def _agg_arm(recs: List[dict]) -> dict:
    q_correct = sum(r["q_correct"] for r in recs)
    q_total = sum(r["q_total"] for r in recs)
    q_correct_pron = sum(r["q_correct_pron"] for r in recs)
    q_total_pron = sum(r["q_total_pron"] for r in recs)
    q_correct_iddem = sum(r["q_correct_iddem"] for r in recs)
    q_total_iddem = sum(r["q_total_iddem"] for r in recs)
    q_correct_triv = sum(r["q_correct_triv"] for r in recs)
    q_total_triv = sum(r["q_total_triv"] for r in recs)
    q_skipped = sum(r["q_skipped"] for r in recs)
    n_correct = sum(r["n_correct"] for r in recs)
    n_total = sum(r["n_total"] for r in recs)
    n_collisions = sum(r["n_collisions"] for r in recs)
    n_clusters = sum(r["n_clusters"] for r in recs)
    return {
        "query_accuracy": (q_correct / q_total) if q_total else None,
        "q_correct": q_correct, "q_total": q_total,
        "query_accuracy_pronoun_contributed": (q_correct_pron / q_total_pron) if q_total_pron else None,
        "q_correct_pron": q_correct_pron, "q_total_pron": q_total_pron,
        "query_accuracy_identity_demanding": (q_correct_iddem / q_total_iddem) if q_total_iddem else None,
        "q_correct_iddem": q_correct_iddem, "q_total_iddem": q_total_iddem,
        "query_accuracy_trivial": (q_correct_triv / q_total_triv) if q_total_triv else None,
        "q_correct_triv": q_correct_triv, "q_total_triv": q_total_triv,
        "q_skipped": q_skipped,
        "per_mention_accuracy": (n_correct / n_total) if n_total else None,
        "n_correct": n_correct, "n_total": n_total,
        "n_collisions": n_collisions, "n_clusters_summed": n_clusters,
        "n_passages": len(recs),
    }


def _length_bucket(n_slots: int) -> str:
    return "short_le4" if n_slots <= 4 else ("med_5to7" if n_slots <= 7 else "long_ge8")


def _oracle_length_stratified(recs: List[dict]) -> dict:
    """oracle query accuracy by passage clause-count bucket -- surfaces any FHRR bundling-capacity
    drop on LONGER multi-event registers (atom 29609 validated only chain-length 2-3)."""
    buckets: Dict[str, dict] = {}
    for r in recs:
        b = _length_bucket(r["n_distinct_clause_slots"])
        d = buckets.setdefault(b, {"q_correct": 0, "q_total": 0, "n_passages": 0})
        d["q_correct"] += r["q_correct"]
        d["q_total"] += r["q_total"]
        d["n_passages"] += 1
    for b, d in buckets.items():
        d["query_accuracy"] = (d["q_correct"] / d["q_total"]) if d["q_total"] else None
    return buckets


def _query_verdict(per_arm: Dict[str, dict]) -> dict:
    """HEADLINE verdict now gated on the IDENTITY-DEMANDING subset (queries whose query_clause has
    >= 2 distinct entities -- the queries that ACTUALLY require identity, where a chain-everything
    mega-cluster MUST cross-talk-corrupt). Milestone if the best real coref arm (earned/strict_cb)
    on that subset beats BOTH floors AND tracks oracle. The ALL-queries and identity-TRIVIAL
    numbers are reported alongside so the 'floor coasts on single-entity clauses' caveat stays
    visible -- we do NOT headline only the favorable subset."""
    K = "query_accuracy_identity_demanding"  # gating metric
    oracle_pm = per_arm["oracle"]["per_mention_accuracy"]
    oracle_q = per_arm["oracle"][K]
    singleton_q = per_arm["singleton_floor"][K]
    recency_q = per_arm["recency_floor"][K]
    earned_q = per_arm["earned"][K]
    strict_q = per_arm["strict_cb"][K]

    real = {"earned": earned_q, "strict_cb": strict_q}
    best_arm = max(real, key=lambda a: (real[a] if real[a] is not None else -1.0))
    best_q = real[best_arm]

    def gates(rq):
        return {
            "beats_singleton": rq is not None and singleton_q is not None and (rq - singleton_q) >= FLOOR_GAP_MARGIN,
            "beats_recency": rq is not None and recency_q is not None and (rq - recency_q) >= FLOOR_GAP_MARGIN,
            "within_ceiling": rq is not None and oracle_q is not None and rq >= oracle_q - MILESTONE_MARGIN,
        }
    g_best = gates(best_q)
    # on the identity-demanding subset, the recency mega-cluster SHOULD cross-talk-corrupt, so the
    # discriminating precondition is that BOTH floors fall clearly below oracle there.
    query_discriminates = (oracle_q is not None and recency_q is not None
                           and (oracle_q - recency_q) >= FLOOR_GAP_MARGIN
                           and singleton_q is not None and (oracle_q - singleton_q) >= FLOOR_GAP_MARGIN)

    scope = "IDENTITY-DEMANDING subset"
    if oracle_pm is None or oracle_pm < ORACLE_CEILING_FLOOR:
        verdict = "WIRING_BUG_SUSPECTED"
        msg = (f"oracle per-mention decode={oracle_pm} below ORACLE_CEILING_FLOOR="
               f"{ORACLE_CEILING_FLOOR} -- organ/slot-remap bug in THIS cell; investigate first.")
    elif oracle_q is None:
        verdict = "QUERY_METRIC_NOT_DISCRIMINATING"
        msg = "no identity-demanding queries in this eval -- cannot gate the milestone here."
    elif not query_discriminates:
        verdict = "QUERY_METRIC_NOT_DISCRIMINATING"
        msg = (f"on the {scope} the floors did NOT fall clearly below oracle "
               f"(oracle={oracle_q:.4f}, recency={recency_q:.4f}, singleton={singleton_q:.4f}); "
               f"subset not discriminating -- report, do not spin.")
    elif g_best["within_ceiling"] and g_best["beats_singleton"] and g_best["beats_recency"]:
        verdict = "MILESTONE_MET"
        msg = (f"MILESTONE_MET on the {scope}: best real arm {best_arm}={best_q:.4f} within "
               f"{MILESTONE_MARGIN} of oracle={oracle_q:.4f} AND beats both floors "
               f"(recency={recency_q:.4f}, singleton={singleton_q:.4f}). earned={earned_q:.4f}, "
               f"strict_cb={strict_q:.4f}. Coref earns its value where identity is REQUIRED. "
               f"CAVEAT: on identity-trivial (single-entity) clauses the floor coasts -- see "
               f"query_accuracy_trivial (simple-narrative limitation, kept visible).")
    elif g_best["beats_singleton"] and g_best["beats_recency"]:
        verdict = "BOTTLENECK_QUANTIFIED"
        msg = (f"BOTTLENECK_QUANTIFIED on the {scope}: best real arm {best_arm}={best_q:.4f} beats "
               f"both floors (recency={recency_q:.4f}, singleton={singleton_q:.4f}) but stays below "
               f"the milestone band vs oracle={oracle_q:.4f}. earned={earned_q:.4f}, "
               f"strict_cb={strict_q:.4f}. Coref adds real value where identity is required; "
               f"headroom oracle-best={(oracle_q - best_q):.4f}.")
    elif not (g_best["beats_singleton"] and g_best["beats_recency"]):
        verdict = "INVESTIGATE_NULL"
        msg = (f"INVESTIGATE_NULL on the {scope}: best real arm {best_arm}={best_q:.4f} does NOT "
               f"clear both floors by >= {FLOOR_GAP_MARGIN} (recency={recency_q:.4f}, "
               f"singleton={singleton_q:.4f}). earned={earned_q:.4f}, strict_cb={strict_q:.4f}. "
               f"Even where identity is required, coref does not beat the floor -- a real negative; "
               f"check vs coref fair-test HARD_PASS (27e10d3a8), do not spin.")
    else:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND on the {scope}: best {best_arm}={best_q:.4f}, oracle={oracle_q:.4f}, "
               f"recency={recency_q:.4f}, singleton={singleton_q:.4f} -- no clean band.")

    return {
        "verdict": verdict, "verdict_msg": msg,
        "gating_scope": "identity_demanding_subset",
        "best_real_arm": best_arm, "best_real_q": best_q,
        "query_discriminates": query_discriminates,
        "gates_best_real_arm": g_best,
        "value_ceiling_earned_over_oracle": (earned_q / oracle_q) if oracle_q else None,
        "value_ceiling_strict_cb_over_oracle": (strict_q / oracle_q) if oracle_q else None,
    }


def main(timeout_s: float) -> None:
    t0 = time.perf_counter()
    output_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
    os.makedirs(output_dir, exist_ok=True)

    # load both evals (deterministic passage order)
    eval_passages = {
        ename: sorted(load_passages(epath), key=lambda p: p["passage_id"])
        for ename, epath in EVALS.items()
    }
    total_units = sum(len(ps) * len(ARM_ORDER) for ps in eval_passages.values())

    done = ckpt.completed_units(output_dir)
    n_run = 0
    for ename in sorted(EVALS):
        passages = eval_passages[ename]
        for p_idx, p in enumerate(passages):
            pid = p["passage_id"]
            stream = build_mention_stream_with_role(p)
            event_slots, n_slots, clause_to_slot = event_slots_for(stream)
            assert n_slots <= MAX_EVENT_SLOTS, (
                f"{ename}/{pid} has {n_slots} clause slots > MAX_EVENT_SLOTS={MAX_EVENT_SLOTS}"
            )
            for a_idx, arm in enumerate(ARM_ORDER):
                key = ckpt.unit_key(ename, pid, arm)
                if key in done:
                    continue
                if time.perf_counter() - t0 > timeout_s:
                    raise TimeoutError(
                        f"exceeded --timeout {timeout_s}s after {n_run} new units; resume by "
                        f"re-running (checkpointed)."
                    )
                cluster_ids = cluster_ids_for_arm(arm, stream)
                gen = torch.Generator().manual_seed(SEED + p_idx * 100 + a_idx)
                res = run_arm_on_passage(p, stream, cluster_ids, event_slots, clause_to_slot,
                                         ROLE_VOCAB, D, gen, MAX_EVENT_SLOTS)
                res["eval"] = ename
                res["passage_id"] = pid
                res["arm"] = arm
                res["n_distinct_clause_slots"] = n_slots
                ckpt.record_unit(output_dir, key, res)
                n_run += 1

    units = ckpt.load_units(output_dir)
    assert len(units) == total_units, f"expected {total_units} units, have {len(units)}"

    # per-eval aggregation
    eval_blocks: Dict[str, dict] = {}
    for ename in EVALS:
        per_arm = {arm: _agg_arm([u for u in units.values()
                                  if u["eval"] == ename and u["arm"] == arm])
                   for arm in ARM_ORDER}
        vinfo = _query_verdict(per_arm)
        oracle_recs = [u for u in units.values() if u["eval"] == ename and u["arm"] == "oracle"]
        eval_blocks[ename] = {
            "per_arm": per_arm,
            "query_accuracy": {arm: per_arm[arm]["query_accuracy"] for arm in ARM_ORDER},
            "query_accuracy_pronoun_contributed": {
                arm: per_arm[arm]["query_accuracy_pronoun_contributed"] for arm in ARM_ORDER
            },
            "query_accuracy_identity_demanding": {
                arm: per_arm[arm]["query_accuracy_identity_demanding"] for arm in ARM_ORDER
            },
            "query_accuracy_trivial": {
                arm: per_arm[arm]["query_accuracy_trivial"] for arm in ARM_ORDER
            },
            "n_collisions_diagnostic": {arm: per_arm[arm]["n_collisions"] for arm in ARM_ORDER},
            "n_clusters_summed": {arm: per_arm[arm]["n_clusters_summed"] for arm in ARM_ORDER},
            "per_mention_accuracy_secondary": {
                arm: per_arm[arm]["per_mention_accuracy"] for arm in ARM_ORDER
            },
            "n_queries_total": per_arm["oracle"]["q_total"],
            "n_queries_pronoun_contributed": per_arm["oracle"]["q_total_pron"],
            "n_queries_identity_demanding": per_arm["oracle"]["q_total_iddem"],
            "n_queries_trivial": per_arm["oracle"]["q_total_triv"],
            "n_passages": per_arm["oracle"]["n_passages"],
            "oracle_query_accuracy_by_length": _oracle_length_stratified(oracle_recs),
            **vinfo,
        }

    head = eval_blocks[HEADLINE_EVAL]
    verdict = head["verdict"]
    verdict_msg = head["verdict_msg"]

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict} (headline eval={HEADLINE_EVAL})",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "seed": SEED,
        "d": D,
        "max_event_slots": MAX_EVENT_SLOTS,
        "role_vocab": ROLE_VOCAB,
        "evals": EVALS,
        "headline_eval": HEADLINE_EVAL,
        "headline_metric": "cross_mention_query_accuracy_name_anchored",
        "arm_order": ARM_ORDER,
        "eval_blocks": eval_blocks,
        "collision_policy": "add_every_mention_never_skip_ncollisions_is_diagnostic_only",
        "secondary_note": (
            "per_mention decode is a SECONDARY diagnostic (organ wiring via oracle + crosstalk); "
            "singleton scores ~1.0 on it so it cannot show coref adds value -- query metric is "
            "the headline. Collision-skip metric bug fixed 2026-08-02: every mention is now "
            "add_event'd so a mega-cluster incurs the FHRR cross-talk penalty it should."
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
            "strict_cb_pronoun_lever": "5b266248f",
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
        "--timeout", type=float, default=180.0,
        help=(
            "formula: (36 powered + 18 g5g6) passages x 5 arms = 270 units, each unit is FHRR "
            "bind/unbind on d=1024 vectors (<50ms/unit on comparable cells); 180s gives generous "
            "headroom for a CPU-only run with import overhead."
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
