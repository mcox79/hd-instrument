"""EARN-COREFERENCE PROBE: learnable MATCH-OR-ALLOCATE identity-tracking vs recency-floor vs
random, on the LONG-form cross-clause gold (data/eval_gold_mention_role_mcguffey_v1/
gold_multiclause_LONG_v1.jsonl, 24 passages).

WHAT: coref (which surface mentions -- names, definite descriptions, pronouns -- refer to the
same entity across clauses) is currently SUPPLIED by the gold's "entities" grouping. This probe
tests whether a substrate-native, OWN-mechanism (glass-box, no external coref tool, no borrowed
embeddings) identity tracker can RECOVER that grouping from the bare mention stream.

MECHANISM (match-or-allocate, Centering/discourse-salience, brain-foundational):
  - Reuses hdlab.state_of_mind's validated CONSTANTS (PRONOUN_SCOPE gender/number table,
    MASC_CUES/FEM_CUES common-noun gender cues via infer_nominal_gender, OVERLAY_BETA /
    OVERLAY_TIEBREAK_LAMBDA salience formula) -- the same identity-feature vocabulary as the
    validated WorkingOverlay coref primitive (VET a7ca3db1) and the accumulate-register's
    match-vs-allocate addressing idea (hdlab/situation_model_accumulate.py). NOT a bolt-on
    external coref library; NOT a borrowed embedding.
  - PRONOUN mention: MATCH ONLY (a pronoun is a reference, never an introduction) to the
    gender/number-compatible entity with highest Centering salience = count + beta*exp(-lam*dist).
  - NAME/NOMINAL mention (proper name OR definite description): compute normalized-token
    Jaccard overlap against every known entity's accumulated surface-token set.
      * overlap > 0        -> MATCH the best-overlap entity (name-equality/overlap identity
                               feature).
      * overlap == 0 AND the mention is a DETERMINER-LED definite description ("the girl")
        AND exactly one gender/number-compatible entity is currently active
                          -> MATCH that entity (Centering "unique compatible antecedent"
                               bridging default -- covers definite-description ("the girl")
                               -> proper-name ("Ernestine") chains with no lexical overlap).
                               Restricted to determiner-led mentions so a bare NEW proper name
                               ("Bob") is never bridged into an unrelated active entity.
      * else               -> ALLOCATE a new entity.

CAN-FAIL (both required, per contract):
  (a) RANDOM assignment (seeded) must score far worse than LEARNABLE.
  (b) RECENCY-ONLY floor (chain every mention to whatever entity absorbed the immediately
      preceding mention -- zero identity features) must be beaten by LEARNABLE.

METRIC: B-cubed precision/recall/F1 over mention pairs, computed per-passage then averaged
per-mention across the whole eval set. Reported overall, and broken out for NAME-mentions vs
PRONOUN-mentions (the harder subset).

HONEST SCOPE: this is a PROBE (single clean local run) to aim the coref build, not a claim
that this is the final mechanism. "Implicit" mentions (non-surface, e.g. "(implicit
addressee)") are excluded from the mention stream (nothing to identity-track). Within-clause
mention order across different gold entities is inferred from raw text substring position
(best-effort; clause text is short prose so this is reliable in practice).

Self-test: python exp_earn_coref_match_or_allocate_v1.py --self-test
Full:      python exp_earn_coref_match_or_allocate_v1.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.state_of_mind import (  # noqa: E402
    FEM_CUES,
    MASC_CUES,
    OVERLAY_BETA,
    OVERLAY_TIEBREAK_LAMBDA,
    PRONOUN_SCOPE,
    infer_nominal_gender,
)

ANCHOR_NAME = "earn_coref_match_or_allocate_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multiclause_LONG_v1.jsonl"
)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

STOPWORDS = {"the", "a", "an", "his", "her", "its", "their", "this", "that"}
RANDOM_SEED = 1234
RANDOM_P_NEW = 0.3  # probability random arm allocates a fresh entity id

# PASS/FAIL bands (pre-declared; probe-grade, not a schema-vet full dispatch cell).
HARD_PASS_MARGIN = 0.05  # learnable must clear both floors by >= 5% absolute F1
BASELINE_IN_BAND_LO, BASELINE_IN_BAND_HI = 0.02, 0.98  # floors must not be degenerate 0/1


# ---------------------------------------------------------------------------
# Gold loading: flatten each passage's grouped "entities" into a clause/text-position-ordered
# mention stream, tagging (gold_entity, mention_text, is_pronoun).
# ---------------------------------------------------------------------------
def normalize_tokens(text: str) -> Set[str]:
    toks = text.lower().strip(".,'\"!?;:()").split()
    toks = [t.strip(".,'\"!?;:()") for t in toks]
    toks = [t for t in toks if t and t not in STOPWORDS]
    return set(toks)


def is_pronoun_mention(text: str) -> bool:
    t = text.lower().strip(".,'\"!?;:()")
    # handle multi-token surfaces like "you / my young lady" (pick the pronoun-bearing half if any)
    parts = [p.strip() for p in t.replace("/", " ").split()]
    return any(p in PRONOUN_SCOPE for p in parts) and len(normalize_tokens(text)) <= 2


def gender_number_for(text: str, is_pron: bool) -> Tuple[Optional[str], Optional[str]]:
    if is_pron:
        t = text.lower().strip(".,'\"!?;:()")
        parts = [p.strip() for p in t.replace("/", " ").split()]
        for p in parts:
            if p in PRONOUN_SCOPE:
                sc = PRONOUN_SCOPE[p]
                return sc["gender"], sc["number"]
        return None, None
    toks = text.replace("/", " ").split()
    g = infer_nominal_gender(toks)
    return g, "singular"


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return passages


def build_mention_stream(passage: dict) -> List[dict]:
    """Flatten passage['entities'] into a clause + textual-position ordered mention list.
    Each record: {gold_entity, clause, mention_text, is_pronoun, gender, number, text_pos}.
    Excludes non-surface "(implicit ...)" placeholder mentions."""
    clauses = passage["clauses"]
    raw = []
    for ent_name, mentions in passage["entities"].items():
        for m in mentions:
            mtxt = m["mention"]
            if mtxt.strip().startswith("("):
                continue  # non-surface placeholder, nothing to identity-track
            clause_idx = m["clause"]
            clause_text = clauses[clause_idx].lower()
            # position of first token of the mention text within the clause (best-effort ordering)
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
                }
            )
    raw.sort(key=lambda r: (r["clause"], r["text_pos"]))
    return raw


# ---------------------------------------------------------------------------
# Identity feature compatibility (gender/number agreement filter, same semantics as
# hdlab.state_of_mind.compatible -- reimplemented here since we track entities via a local
# lightweight registry, not hdlab.state_of_mind.EntityState objects).
# ---------------------------------------------------------------------------
def gn_compatible(t_gender: Optional[str], t_number: Optional[str],
                   e_gender: Optional[str], e_number: Optional[str]) -> bool:
    if t_number is not None and e_number is not None and t_number != e_number:
        return False
    if t_gender is not None and t_gender != "any" and e_gender is not None and e_gender != "any" \
            and t_gender != e_gender:
        return False
    return True


class _Entity:
    __slots__ = ("eid", "tokens", "gender", "number", "count", "last_pos")

    def __init__(self, eid: int) -> None:
        self.eid = eid
        self.tokens: Set[str] = set()
        self.gender: Optional[str] = None
        self.number: Optional[str] = None
        self.count = 0
        self.last_pos = -1

    def salience(self, now: int) -> float:
        import math
        return self.count + OVERLAY_BETA * math.exp(-OVERLAY_TIEBREAK_LAMBDA * (now - self.last_pos))


def run_learnable(stream: List[dict]) -> List[int]:
    """MATCH-OR-ALLOCATE arm. Returns predicted entity-id per mention in stream order."""
    entities: List[_Entity] = []
    next_id = 0
    assigned: List[int] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                best = max(compat, key=lambda e: e.salience(pos))
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)  # best-effort fallback
            else:
                best = _Entity(next_id)
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
        if best is None and len(compat) == 1 and rec["has_determiner"]:
            # unique-compatible-antecedent bridging default: ONLY for determiner-led definite
            # descriptions ("the girl"), never for bare proper names ("Bob") -- a bare name is
            # an unambiguous NEW-identity introduction, not a bridging reference.
            best = compat[0]
        if best is None:
            best = _Entity(next_id)
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


def run_recency_floor(stream: List[dict]) -> List[int]:
    """Chain every mention to whatever entity absorbed the immediately preceding mention.
    Zero identity features -- the naive floor the learnable mechanism must beat."""
    if not stream:
        return []
    assigned = [0]
    for _ in stream[1:]:
        assigned.append(assigned[-1])
    return assigned


def run_random(stream: List[dict], rng) -> List[int]:
    """Seeded random assignment: p_new chance of a fresh entity, else uniform over existing ids."""
    assigned: List[int] = []
    next_id = 0
    seen_ids: List[int] = []
    for _ in stream:
        if not seen_ids or rng.random() < RANDOM_P_NEW:
            eid = next_id
            next_id += 1
            seen_ids.append(eid)
        else:
            eid = seen_ids[rng.randrange(len(seen_ids))]
        assigned.append(eid)
    return assigned


# ---------------------------------------------------------------------------
# B-cubed precision/recall/F1, computed per-passage then pooled by mention across the eval set.
# ---------------------------------------------------------------------------
def bcubed(streams_and_preds: List[Tuple[List[dict], List[int]]],
           subset: Optional[str] = None) -> Dict[str, float]:
    """subset in {None, 'name', 'pronoun'} restricts which mentions are AVERAGED over (the
    cluster-membership computation itself always uses the full passage's mention set)."""
    prec_sum = 0.0
    rec_sum = 0.0
    n = 0
    for stream, preds in streams_and_preds:
        m = len(stream)
        for i in range(m):
            if subset == "name" and stream[i]["is_pronoun"]:
                continue
            if subset == "pronoun" and not stream[i]["is_pronoun"]:
                continue
            gold_i = stream[i]["gold_entity"]
            pred_i = preds[i]
            p_cluster = [j for j in range(m) if preds[j] == pred_i]
            g_cluster = [j for j in range(m) if stream[j]["gold_entity"] == gold_i]
            inter = len(set(p_cluster) & set(g_cluster))
            prec_sum += inter / len(p_cluster)
            rec_sum += inter / len(g_cluster)
            n += 1
    if n == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "n_mentions": 0}
    precision = prec_sum / n
    recall = rec_sum / n
    f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1, "n_mentions": n}


# ---------------------------------------------------------------------------
# Self-test: exercises the REAL code path (load_passages, build_mention_stream, all 3 arms,
# bcubed) on a tiny synthetic 2-passage fixture with a known correct answer.
# ---------------------------------------------------------------------------
def self_test() -> None:
    fixture = [
        {
            "passage_id": "t1",
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
    ]
    stream = build_mention_stream(fixture[0])
    assert len(stream) == 4, f"expected 4 surface mentions, got {len(stream)}"
    assert stream[0]["mention_text"] == "Alice" and not stream[0]["is_pronoun"]
    assert stream[1]["mention_text"] == "She" and stream[1]["is_pronoun"]
    assert stream[1]["gender"] == "fem"
    learn_pred = run_learnable(stream)
    # Alice(0), She(1), Bob(2 or 3 depending on text-pos order), her(the other) must all resolve:
    # Alice and She and her must share one id; Bob must be a distinct id.
    alice_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Alice"]
    bob_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Bob"]
    alice_ids = {learn_pred[i] for i in alice_idxs}
    bob_ids = {learn_pred[i] for i in bob_idxs}
    assert len(alice_ids) == 1, f"learnable failed to chain Alice/She/her: {alice_ids}"
    assert alice_ids.isdisjoint(bob_ids), "learnable incorrectly merged Alice and Bob"

    rec_pred = run_recency_floor(stream)
    assert rec_pred == [0, 0, 0, 0], f"recency floor must chain everything to id 0: {rec_pred}"

    import random
    rng = random.Random(RANDOM_SEED)
    rand_pred = run_random(stream, rng)
    assert len(rand_pred) == 4

    b = bcubed([(stream, learn_pred)])
    assert b["f1"] == 1.0, f"learnable must score perfect B3 on this clean fixture: {b}"
    b_rec = bcubed([(stream, rec_pred)])
    assert b_rec["f1"] < b["f1"], "recency-floor must NOT beat learnable on the self-test fixture"

    # real code path: load the actual gold file too (tiny slice) to catch schema drift early.
    assert os.path.exists(GOLD_PATH), f"gold file missing: {GOLD_PATH}"
    real_passages = load_passages(GOLD_PATH)
    assert len(real_passages) >= 1
    real_stream = build_mention_stream(real_passages[0])
    assert len(real_stream) > 0
    _ = run_learnable(real_stream)

    print("[SELF-TEST] PASS: real code path exercised, chaining + disjointness + bcubed verified")


# ---------------------------------------------------------------------------
# Main.
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

    streams = [build_mention_stream(p) for p in passages]
    n_mentions_total = sum(len(s) for s in streams)
    n_pronoun = sum(1 for s in streams for r in s if r["is_pronoun"])
    n_name = n_mentions_total - n_pronoun

    import random
    rng = random.Random(RANDOM_SEED)

    learn_preds = [run_learnable(s) for s in streams]
    rec_preds = [run_recency_floor(s) for s in streams]
    rand_preds = [run_random(s, rng) for s in streams]

    arms = {
        "learnable": list(zip(streams, learn_preds)),
        "recency_floor": list(zip(streams, rec_preds)),
        "random": list(zip(streams, rand_preds)),
    }
    results = {}
    for arm_name, pairs in arms.items():
        results[arm_name] = {
            "overall": bcubed(pairs),
            "name_only": bcubed(pairs, subset="name"),
            "pronoun_only": bcubed(pairs, subset="pronoun"),
        }

    learn_f1 = results["learnable"]["overall"]["f1"]
    rec_f1 = results["recency_floor"]["overall"]["f1"]
    rand_f1 = results["random"]["overall"]["f1"]

    beats_recency = (learn_f1 - rec_f1) >= HARD_PASS_MARGIN
    beats_random = (learn_f1 - rand_f1) >= HARD_PASS_MARGIN
    floors_in_band = (BASELINE_IN_BAND_LO < rec_f1 < BASELINE_IN_BAND_HI) and \
                      (BASELINE_IN_BAND_LO < rand_f1 < BASELINE_IN_BAND_HI)

    if beats_recency and beats_random and floors_in_band:
        verdict = "HARD_PASS_LEARNABLE_BEATS_BOTH_FLOORS"
    elif beats_recency and beats_random:
        verdict = "MIDDLE_BAND_FLOORS_DEGENERATE"
    else:
        verdict = "HARD_FAIL_LEARNABLE_DOES_NOT_BEAT_FLOOR"

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": (
            f"learnable_f1={learn_f1:.4f} recency_floor_f1={rec_f1:.4f} random_f1={rand_f1:.4f} "
            f"beats_recency={beats_recency} beats_random={beats_random} "
            f"n_passages={len(passages)} n_mentions={n_mentions_total} "
            f"n_name={n_name} n_pronoun={n_pronoun}"
        ),
        "summary": verdict,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "n_passages": len(passages),
        "n_mentions_total": n_mentions_total,
        "n_name_mentions": n_name,
        "n_pronoun_mentions": n_pronoun,
        "arms": results,
        "cardinality_ok": len(streams) == len(passages),
        "bands": {
            "hard_pass_margin": HARD_PASS_MARGIN,
            "baseline_in_band": [BASELINE_IN_BAND_LO, BASELINE_IN_BAND_HI],
        },
        "gold_path": GOLD_PATH,
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    print(f"[{ANCHOR_NAME}] {verdict}")
    print(metrics["verdict_msg"])
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
