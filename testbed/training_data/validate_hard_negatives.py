"""Validation tool: sample hard-negative tuples + print for inspection + heuristic quality score.

Per LLM integration handoff Update 2:
> "Validation gate: after generation, manually inspect ~50 random tuples
>  to verify the hard-negatives are actually plausible-but-wrong (not
>  trivial random negatives). If <80% pass quality bar, re-prompt the
>  teacher with sharper instructions; iterate."

Heuristic quality checks per tuple (no LLM call):
  (a) JSON well-formed with required fields
  (b) gt_trace and hard_negative_trace same length
  (c) hard_negative_trace has at least one (key OR wrong_value) different
      from the corresponding gt_trace step
  (d) hard_negative_trace shares at least one key with gt_trace
      (else it's a "trivial random negative" -- unrelated graph traversal)
  (e) negative_kind is one of the known kinds
  (f) why_plausible field present on each hard-negative step

A tuple passes if all 6 hold. Heuristic-pass != semantic-pass; manual
inspection is still required at the 80% threshold gate. The heuristic
catches obvious failures cheaply.

Run:
  .venv\\Scripts\\python.exe -m testbed.training_data.validate_hard_negatives \\
    --in data/hard_neg_smoke.jsonl --sample 50
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[2]
_KNOWN_KINDS = {
    "same_predicate_wrong_entity",
    "off_by_one_hop",
    "right_entities_wrong_relation",
    "other",
}


def _key_components(key: str) -> set[str]:
    """Split a substrate key like 'p_00__role' or 'c_02__employs__p_05'
    into its underscore-double-separated components for structural overlap
    checks. Hard negatives often share an entity prefix or a predicate
    suffix without sharing the full key string."""
    if not isinstance(key, str) or not key:
        return set()
    return set(key.split("__"))


def _heuristic_check(t: dict) -> tuple[bool, list[str]]:
    fails: list[str] = []
    if not isinstance(t, dict):
        return False, ["not a dict"]
    for f in ("query", "gt_trace", "hard_negative_trace", "answer",
              "negative_kind"):
        if f not in t:
            fails.append(f"missing field: {f}")
    if fails:
        return False, fails
    gt = t["gt_trace"]
    hn = t["hard_negative_trace"]
    if not isinstance(gt, list) or not isinstance(hn, list):
        fails.append("gt_trace / hard_negative_trace not lists")
    if isinstance(gt, list) and isinstance(hn, list):
        if len(gt) != len(hn):
            fails.append(f"trace length mismatch: gt={len(gt)} hn={len(hn)}")
        else:
            differs = False
            structural_overlap = False
            gt_components: set[str] = set()
            for step in gt:
                if isinstance(step, dict):
                    gt_components |= _key_components(step.get("key", ""))
            for gtstep, hnstep in zip(gt, hn):
                if not isinstance(gtstep, dict) or not isinstance(hnstep, dict):
                    fails.append("trace step not dict")
                    continue
                gk = gtstep.get("key")
                hk = hnstep.get("key")
                # Structural overlap: HN key shares >=1 entity/predicate
                # component with any GT key. Catches "same entity wrong
                # relation" and "same predicate wrong entity" as valid HN.
                if _key_components(hk) & gt_components:
                    structural_overlap = True
                if gk != hk or gtstep.get("expected_value") != hnstep.get("wrong_value"):
                    differs = True
                if "why_plausible" not in hnstep:
                    fails.append("hard-negative step missing why_plausible")
            if not differs:
                fails.append("hard-negative trace identical to gt trace")
            if not structural_overlap:
                fails.append(
                    "hard-negative has no structural overlap with gt "
                    "(no shared entity/predicate component) -- trivial random"
                )
    if t.get("negative_kind") not in _KNOWN_KINDS:
        fails.append(f"unknown negative_kind: {t.get('negative_kind')!r}")
    return (not fails), fails


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate generated hard-negative tuples")
    parser.add_argument("--in", dest="in_path", required=True,
                        help="Path to JSONL file produced by hard_negative_tuple_gen")
    parser.add_argument("--sample", type=int, default=50,
                        help="How many tuples to sample for inspection display")
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--show-failures", action="store_true",
                        help="Also print sampled tuples that fail the heuristic")
    args = parser.parse_args()

    in_path = Path(args.in_path)
    if not in_path.is_absolute():
        in_path = _REPO_ROOT / in_path
    if not in_path.is_file():
        print(f"[ERROR] not found: {in_path}")
        return 1

    tuples: list[dict] = []
    for line in in_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            tuples.append(json.loads(line))
        except Exception:
            tuples.append({"_parse_error": True, "_raw": line[:200]})
    print(f"loaded {len(tuples)} tuples from {in_path}")
    if not tuples:
        return 1

    # Full-set heuristic pass rate
    n_pass = 0
    fail_reasons: dict[str, int] = {}
    for t in tuples:
        ok, fails = _heuristic_check(t)
        if ok:
            n_pass += 1
        else:
            for f in fails:
                fail_reasons[f] = fail_reasons.get(f, 0) + 1
    pass_rate = 100 * n_pass / len(tuples)
    print(f"heuristic pass rate: {n_pass}/{len(tuples)} ({pass_rate:.1f}%)")
    if pass_rate < 80:
        print(f"  WARN: <80% pass; re-prompt teacher per handoff Update 2.")
    else:
        print(f"  OK: >=80% pass on heuristic; manual inspection now warranted.")
    if fail_reasons:
        print(f"  Failure mode counts:")
        for reason, n in sorted(fail_reasons.items(), key=lambda kv: -kv[1]):
            print(f"    [{n:>4}] {reason}")
    print()

    # Sample for manual inspection
    rng = random.Random(args.seed)
    sample_n = min(args.sample, len(tuples))
    sample = rng.sample(tuples, sample_n)
    if not args.show_failures:
        sample = [t for t in sample if _heuristic_check(t)[0]]

    print(f"--- {len(sample)} sampled tuple(s) for manual inspection ---")
    for i, t in enumerate(sample):
        ok, fails = _heuristic_check(t)
        ok_str = "OK" if ok else f"FAIL: {', '.join(fails[:2])}"
        print(f"\n[{i+1}] tuple_id={t.get('tuple_id', '?')}  ({ok_str})")
        print(f"  query: {t.get('query', '')!r}")
        print(f"  answer: {t.get('answer', '')!r}")
        print(f"  negative_kind: {t.get('negative_kind', '?')}")
        gt = t.get("gt_trace", [])
        hn = t.get("hard_negative_trace", [])
        for s in gt:
            if isinstance(s, dict):
                print(f"    GT step {s.get('step', '?')}: "
                      f"{s.get('key', '?')} -> {s.get('expected_value', '?')!r}")
        for s in hn:
            if isinstance(s, dict):
                why = s.get("why_plausible", "")
                if len(why) > 60:
                    why = why[:57] + "..."
                print(f"    HN step {s.get('step', '?')}: "
                      f"{s.get('key', '?')} -> {s.get('wrong_value', '?')!r}  "
                      f"[{why}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
