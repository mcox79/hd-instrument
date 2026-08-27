"""Role-BALANCED who-did-what comprehension gold (the consolidation-phase measurement instrument).

WHY: the McGuffey entity-role gold is AGENT-SATURATED (majority-role floor ~0.78) and ~200 years old, so a reader
that just guesses "the post-verbal nominal is the patient" already looks great and a real role-assignment win is
INVISIBLE. This builds a MODERN, ROLE-BALANCED who-did-what test from QA-SRL where the naive POSITIONAL baseline scores
~0.5, so the composed reader (incremental_parser -> role assigner + relcl_resolver; graded_competition) has to actually
resolve WHO-did-WHAT to beat the floor.

CONSTRUCTION: QA-SRL labels, per predicate, the AGENT and PATIENT spans + voice. The patient's POSITION relative to
the verb is the balancer:
  * POST-verbal patient  = canonical active SVO ("the lawyer chased the DOCTOR")   -> the easy majority case.
  * PRE-verbal  patient  = passive ("the DOCTOR was chased") or object-relative ("the DOCTOR that ... chased") -> the
                           reversible/non-canonical case where a positional-only reader FAILS.
We sample EQUAL counts of pre- and post-verbal patients, so the positional-only floor ("patient = a post-verbal
nominal") is ~0.5 BY CONSTRUCTION. The pre-verbal slice is the can-fail DISCRIMINATOR (word order is misleading there).

CAN-FAIL SELF-CHECK: if the sampled set's positional-only floor is NOT ~0.5, the balancing FAILED (still saturated).

Run:  .venv/Scripts/python.exe experiments/exp_role_balanced_comprehension_gold_v1.py [--smoke]
Saves: data/role_balanced_comprehension_gold_v1/gold.jsonl  (+ meta.json)  for the OFF-vs-ON measurement step.
"""
from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

from exp_reader_vs_twoline_qasrl_power_v1 import load_patient_items  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "data", "role_balanced_comprehension_gold_v1")
SEED = 20260827


def _patient_position(item) -> str:
    """pre / post / mixed -- the patient span's position relative to the verb (0-based verb_idx)."""
    v = item["verb_idx"]
    span = item["patient"]
    if not span:
        return "mixed"
    if max(span) < v:
        return "pre"
    if min(span) > v:
        return "post"
    return "mixed"


def build(limit_per_split=None, seed=SEED):
    # deterministic order (no RNG needed -- we take a fixed prefix of each pool for reproducibility)
    raw = []
    for split in ("dev.jsonl.gz", "test.jsonl.gz"):
        raw.extend(load_patient_items(split, limit=limit_per_split))
    pre, post = [], []
    for it in raw:
        posn = _patient_position(it)
        rec = {
            "toks": it["toks"], "verb_idx": it["verb_idx"],
            "patient": it["patient"], "agent": it.get("agent"),
            "voice": it["voice"], "category": it["category"], "patient_position": posn,
        }
        if posn == "pre":
            pre.append(rec)
        elif posn == "post":
            post.append(rec)
    k = min(len(pre), len(post))
    balanced = pre[:k] + post[:k]

    n = len(balanced)
    n_post = sum(1 for r in balanced if r["patient_position"] == "post")
    # POSITIONAL-ONLY floor: "the patient is a POST-verbal nominal" -> correct exactly on the post-verbal items
    positional_floor = n_post / n if n else 0.0
    # MAJORITY-role floor: always guess the more common position
    majority_floor = max(n_post, n - n_post) / n if n else 0.0
    n_passive = sum(1 for r in balanced if r["category"] == "passive")
    n_relcl_reversible = sum(1 for r in balanced
                             if r["patient_position"] == "pre" and r["category"] != "passive")
    meta = {
        "anchor": "role_balanced_comprehension_gold_v1",
        "n_items": n, "n_pre_verbal_patient": n - n_post, "n_post_verbal_patient": n_post,
        "positional_only_floor": round(positional_floor, 4),
        "majority_role_floor": round(majority_floor, 4),
        "n_passive": n_passive, "n_relcl_or_other_reversible": n_relcl_reversible,
        "pool_pre": len(pre), "pool_post": len(post), "balanced_to": k,
        "note": "patient position balanced pre/post so a positional-only reader scores ~0.5; pre-verbal = the "
                "reversible/non-canonical discriminator (passive + object-relative).",
    }
    return balanced, meta


def main():
    smoke = "--smoke" in sys.argv
    balanced, meta = build(limit_per_split=4000 if smoke else None)
    print("=== ROLE-BALANCED COMPREHENSION GOLD ===")
    for kk in ("n_items", "n_pre_verbal_patient", "n_post_verbal_patient", "positional_only_floor",
               "majority_role_floor", "n_passive", "n_relcl_or_other_reversible", "pool_pre", "pool_post"):
        print(f"  {kk}: {meta[kk]}")

    # CAN-FAIL: the whole point is a defeated positional floor. If it is not ~0.5, the balancing failed.
    assert meta["n_items"] >= 200, f"gold too small to be a measurement instrument: {meta['n_items']}"
    assert 0.45 <= meta["positional_only_floor"] <= 0.55, \
        f"[can-fail] positional-only floor {meta['positional_only_floor']} is NOT ~0.5 -> balance FAILED"
    assert 0.45 <= meta["majority_role_floor"] <= 0.60, \
        f"[can-fail] majority floor {meta['majority_role_floor']} not balanced"
    assert meta["n_pre_verbal_patient"] > 0 and meta["n_post_verbal_patient"] > 0, "one position pool is empty"

    if not smoke:
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "gold.jsonl"), "w", encoding="utf-8", newline="") as fh:
            for r in balanced:
                fh.write(json.dumps(r) + "\n")
        with open(os.path.join(OUT_DIR, "meta.json"), "w", encoding="utf-8", newline="") as fh:
            json.dump(meta, fh, indent=2)
        print(f"\nSAVED {meta['n_items']} items -> {OUT_DIR}")
    print("\nCAN-FAIL CHECK PASSED: the positional-only floor is ~0.5 -> a naive word-order reader CANNOT win; "
          "the pre-verbal (reversible) slice is the discriminator the composed reader must beat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
