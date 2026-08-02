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
  - singleton_floor: cluster key = one-per-mention (no identity tracking at all; reported for
                     context only -- structurally near-perfect on single-event registers, so it
                     is NOT used as the gating floor, recency_floor is).

METRIC: fraction of mention-events whose role decodes correctly from its assigned cluster's
AccumulateRegister (decode-argmax over role_vocab), pooled over all (passage, mention) pairs,
per arm. A wrong MERGE piles two entities' bindings into one register -> cross-talk corrupts
decode. A wrong SPLIT fragments one entity's trajectory across clusters -> registers still
decode locally (each fragment self-consistent) but VALUE-CEILING (earned/oracle) still drops
because slot-collisions increase when multiple entities' events land on the same (cluster, slot)
key inside a merged cluster.

CAN-FAIL BANDS (pre-registered BEFORE running, per the design doc):
  - MILESTONE_MET:        earned_accuracy >= oracle_accuracy - MILESTONE_MARGIN (0.05 abs)
  - BOTTLENECK_QUANTIFIED: earned clears recency_floor by >= FLOOR_GAP_MARGIN (0.05 abs) but
                           remains below the milestone band -- coref is the quantified
                           bottleneck; states remaining coref headroom.
  - INVESTIGATE_NULL:      |earned_accuracy - recency_floor_accuracy| < FLOOR_GAP_MARGIN --
                           earned coref adds nothing at the situation-model level, which would
                           CONTRADICT the coref fair-test HARD_PASS (27e10d3a8) -- flag, do not
                           spin a positive story.
  - WIRING_BUG_SUSPECTED:  oracle_accuracy < ORACLE_CEILING_FLOOR (0.90) -- the organ or the
                           slot-remap has a bug in THIS cell; investigate before trusting any
                           other arm.

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


def event_slots_for(stream: List[dict]) -> Tuple[List[int], int]:
    """Compact distinct clause indices in this stream to dense slots 0..k-1 (sorted)."""
    distinct_clauses = sorted({r["clause"] for r in stream})
    clause_to_slot = {c: i for i, c in enumerate(distinct_clauses)}
    return [clause_to_slot[r["clause"]] for r in stream], len(distinct_clauses)


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
    stream: List[dict],
    cluster_ids: List[str],
    event_slots: List[int],
    role_vocab: List[str],
    d: int,
    generator: torch.Generator,
    max_event_slots: int,
) -> dict:
    """Build one AccumulateRegister for this (passage, arm), add_event per mention (first
    occurrence of a (cluster_id, event_slot) key only -- collision policy above), decode+score
    every mention-event (including collided ones, which are scored against whatever the first
    mention at that key bound)."""
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

    n_correct = 0
    n_total = 0
    for rec, cid, slot in zip(stream, cluster_ids, event_slots):
        pred_role, _scores = reg.decode(cid, slot)
        n_correct += int(pred_role == rec["role"])
        n_total += 1

    return {
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
def self_test() -> None:
    role_vocab = ["agent", "theme", "patient", "recipient"]
    d = 256
    stream = [
        {"gold_entity": "A", "clause": 0, "role": "agent"},
        {"gold_entity": "A", "clause": 1, "role": "theme"},
        {"gold_entity": "B", "clause": 0, "role": "patient"},
        {"gold_entity": "B", "clause": 1, "role": "recipient"},
    ]
    event_slots, n_slots = event_slots_for(stream)
    assert n_slots == 2, f"expected 2 distinct clause slots, got {n_slots}"
    assert event_slots == [0, 1, 0, 1]

    oracle_ids = [r["gold_entity"] for r in stream]
    gen_oracle = torch.Generator().manual_seed(1)
    res_oracle = run_arm_on_passage(stream, oracle_ids, event_slots, role_vocab, d, gen_oracle, 4)
    assert res_oracle["accuracy"] == 1.0, f"oracle (distinct entities/slots) must decode all correctly: {res_oracle}"
    assert res_oracle["n_collisions"] == 0, f"no true collisions expected in this fixture: {res_oracle}"

    # Deliberately-merged key: force A and B into ONE cluster -- both entities' events now
    # collide pairwise on (cluster, slot) (A-agent vs B-patient at slot 0; A-theme vs
    # B-recipient at slot 1). Only the first mention at each slot binds; the second is scored
    # against the wrong role -> accuracy must drop below the oracle's 1.0.
    merged_ids = ["MERGED", "MERGED", "MERGED", "MERGED"]
    gen_merged = torch.Generator().manual_seed(1)
    res_merged = run_arm_on_passage(stream, merged_ids, event_slots, role_vocab, d, gen_merged, 4)
    assert res_merged["n_collisions"] == 2, f"merging must produce exactly 2 slot collisions: {res_merged}"
    assert res_merged["accuracy"] < res_oracle["accuracy"], (
        f"merged-key identity corruption must reduce decode accuracy: merged={res_merged} oracle={res_oracle}"
    )
    assert res_merged["accuracy"] == 0.5, f"expected exactly 2/4 correct under full merge, got {res_merged}"

    # singleton floor: no identity tracking -> every mention its own entity -> every register
    # has exactly one event -> decode is the FHRR exact-inverse special case -> must be 1.0
    # (this is why singleton is reported for context only, not used as the gating floor).
    singleton_ids = [str(i) for i in range(len(stream))]
    gen_single = torch.Generator().manual_seed(1)
    res_single = run_arm_on_passage(stream, singleton_ids, event_slots, role_vocab, d, gen_single, 4)
    assert res_single["accuracy"] == 1.0, f"singleton (1 event/register) must decode exactly: {res_single}"

    # real gold path + real coref mechanism, sanity only (not scored).
    assert os.path.exists(GOLD_PATH), f"dense gold file missing: {GOLD_PATH}"
    passages = load_passages(GOLD_PATH)
    assert len(passages) == 18, f"expected 18 dense passages, got {len(passages)}"
    real_stream = build_mention_stream_with_role(passages[0])
    assert len(real_stream) > 0
    assert all("role" in r for r in real_stream), "role field must survive the local stream builder"
    real_slots, real_n_slots = event_slots_for(real_stream)
    assert real_n_slots <= MAX_EVENT_SLOTS
    _ = run_learnable(real_stream)

    print("[SELF-TEST] PASS: AccumulateRegister wiring, event-slot remap, collision policy, "
          "merge-corrupts-decode, singleton exact-inverse, and real gold/coref path all verified")


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
        event_slots, n_slots = event_slots_for(stream)
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
            res = run_arm_on_passage(stream, cluster_ids, event_slots, ROLE_VOCAB, D, gen, MAX_EVENT_SLOTS)
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
        n_correct = sum(r["n_correct"] for r in recs)
        n_total = sum(r["n_total"] for r in recs)
        n_collisions = sum(r["n_collisions"] for r in recs)
        per_arm[arm] = {
            "accuracy": (n_correct / n_total) if n_total else None,
            "n_correct": n_correct,
            "n_total": n_total,
            "n_collisions": n_collisions,
            "n_passages": len(recs),
        }

    oracle_acc = per_arm["oracle"]["accuracy"]
    earned_acc = per_arm["earned"]["accuracy"]
    recency_acc = per_arm["recency_floor"]["accuracy"]
    singleton_acc = per_arm["singleton_floor"]["accuracy"]
    value_ceiling = (earned_acc / oracle_acc) if oracle_acc else None

    # ---- can-fail bands (pre-registered, see docstring) ----
    if oracle_acc is None or oracle_acc < ORACLE_CEILING_FLOOR:
        verdict = "WIRING_BUG_SUSPECTED"
        verdict_msg = (
            f"oracle_accuracy={oracle_acc} below ORACLE_CEILING_FLOOR={ORACLE_CEILING_FLOOR} -- "
            f"the accumulate organ or the event-slot remap has a bug in THIS cell; investigate "
            f"before trusting earned/floor arms."
        )
    elif earned_acc >= oracle_acc - MILESTONE_MARGIN:
        verdict = "MILESTONE_MET"
        verdict_msg = (
            f"MILESTONE_MET: earned={earned_acc:.4f} within {MILESTONE_MARGIN} of oracle "
            f"ceiling={oracle_acc:.4f} (value_ceiling={value_ceiling:.4f}). Earned coref is good "
            f"enough to carry the situation model end-to-end on real McGuffey, no oracle scaffolding."
        )
    elif (earned_acc - recency_acc) >= FLOOR_GAP_MARGIN:
        verdict = "BOTTLENECK_QUANTIFIED"
        verdict_msg = (
            f"BOTTLENECK_QUANTIFIED: earned={earned_acc:.4f} clears recency_floor={recency_acc:.4f} "
            f"by {(earned_acc - recency_acc):.4f} (>= {FLOOR_GAP_MARGIN}) but remains below the "
            f"milestone band vs oracle={oracle_acc:.4f} (value_ceiling={value_ceiling:.4f}). "
            f"Coref is the quantified bottleneck; remaining headroom = oracle - earned = "
            f"{(oracle_acc - earned_acc):.4f}."
        )
    elif abs(earned_acc - recency_acc) < FLOOR_GAP_MARGIN:
        verdict = "INVESTIGATE_NULL"
        verdict_msg = (
            f"INVESTIGATE_NULL: earned={earned_acc:.4f} ~= recency_floor={recency_acc:.4f} "
            f"(diff={(earned_acc - recency_acc):.4f} < {FLOOR_GAP_MARGIN}). Earned coref adds "
            f"nothing at the situation-model level; this CONTRADICTS the coref fair-test "
            f"HARD_PASS (commit 27e10d3a8) and must be investigated, not spun as a finding."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: earned={earned_acc:.4f}, oracle={oracle_acc:.4f}, "
            f"recency_floor={recency_acc:.4f} -- does not cleanly fall in a pre-registered band."
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
        "oracle_accuracy": oracle_acc,
        "earned_accuracy": earned_acc,
        "recency_floor_accuracy": recency_acc,
        "singleton_floor_accuracy": singleton_acc,
        "value_ceiling_earned_over_oracle": value_ceiling,
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
