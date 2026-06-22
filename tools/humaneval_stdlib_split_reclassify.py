"""humaneval_stdlib_split_reclassify.py -- post-hoc broader-heuristic Class A reclassifier.

The cell `exp_humaneval_stdlib_split_qwen_v1.py` classifies Class A (stdlib-class) using
`canonical_solution` text (presence of `import`, `math.`, `re.`, `itertools.`, etc.).
This gives n_A=13 on HumanEval-164 -- much narrower than the 40-60 estimated in the
pre-reg.

This tool re-classifies Class A using BOTH the canonical_solution heuristic AND
prompt-text heuristics (docstring mentions of stdlib concepts: sqrt, factorial, prime,
combinations, fibonacci, palindrome, roman, regex, etc.). On HumanEval-164 it gives
n_A_broad=35. The bare/sub pass results are unchanged; only the bucketing differs.

Usage:
    cd /d/AI/hd-instrument
    .venv/Scripts/python.exe tools/humaneval_stdlib_split_reclassify.py

Reads:
    data/exp_humaneval_stdlib_split_qwen_v1/metrics.json
Prints:
    Re-derived NARROW and BROAD Class A pass@1 (bare and substrate-aug) + gain_A_broad.
    Discriminating-regime check: Class B (broad complement) gain_B_broad must be < +5pts.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
METRICS_PATH = REPO / "data" / "exp_humaneval_stdlib_split_qwen_v1" / "metrics.json"


def is_class_A_narrow_canonical(canonical_solution: str) -> bool:
    """Replicates the cell's in-place heuristic (the one applied during the run)."""
    pats = ["import ", "math.", "re.", "itertools.", "collections.",
            "os.", "string.", "functools.", "operator.", "bisect.",
            "heapq.", "datetime", "json."]
    return any(p in canonical_solution for p in pats)


def is_class_A_broad(canonical_solution: str, prompt: str) -> bool:
    """Broader heuristic: canonical-text stdlib mention OR prompt-docstring stdlib-concept hint."""
    if is_class_A_narrow_canonical(canonical_solution):
        return True
    p = prompt.lower()
    prompt_hints = [
        "sqrt", "factorial", "prime", "regex", "pattern",
        "combinations", "permutations", "frequency", "most common",
        "roman numeral", "palindrome", "fibonacci", "count of",
        "median", "mean", "anagram",
    ]
    return any(kw in p for kw in prompt_hints)


def main():
    if not METRICS_PATH.exists():
        print("ERROR: metrics.json not found at %s -- run the cell first." % METRICS_PATH)
        return 1
    m = json.loads(METRICS_PATH.read_text())
    print("run_mode:", m.get("run_mode"))
    print("verdict (in-cell):", m.get("verdict"))
    r = m["per_seed"][0]
    pp = r["per_problem"]
    print("per_problem entries:", len(pp))

    # Load HumanEval for the broad reclassification (we need prompts; the metrics only has task_id + class)
    from datasets import load_dataset
    ds = load_dataset("openai_humaneval", split="test")
    task2item = {it["task_id"]: it for it in ds}

    n_narrow_A = n_narrow_B = 0
    n_broad_A = n_broad_B = 0
    narrow_A_bare = narrow_A_sub = 0
    narrow_B_bare = narrow_B_sub = 0
    broad_A_bare = broad_A_sub = 0
    broad_B_bare = broad_B_sub = 0
    for p in pp:
        tid = p["task_id"]
        it = task2item.get(tid)
        if it is None:
            continue
        narrow_A = is_class_A_narrow_canonical(it["canonical_solution"])
        broad_A = is_class_A_broad(it["canonical_solution"], it["prompt"])
        if narrow_A:
            n_narrow_A += 1
            narrow_A_bare += int(p["bare_pass"]); narrow_A_sub += int(p["sub_pass"])
        else:
            n_narrow_B += 1
            narrow_B_bare += int(p["bare_pass"]); narrow_B_sub += int(p["sub_pass"])
        if broad_A:
            n_broad_A += 1
            broad_A_bare += int(p["bare_pass"]); broad_A_sub += int(p["sub_pass"])
        else:
            n_broad_B += 1
            broad_B_bare += int(p["bare_pass"]); broad_B_sub += int(p["sub_pass"])

    def rate(n, d): return float(n) / d if d else 0.0
    print("\n=== NARROW (canonical-only; the cell's in-place heuristic) ===")
    print("n_A = %d, n_B = %d" % (n_narrow_A, n_narrow_B))
    print("Class A bare=%.3f sub=%.3f gain=%+.3f" % (
        rate(narrow_A_bare, n_narrow_A), rate(narrow_A_sub, n_narrow_A),
        rate(narrow_A_sub, n_narrow_A) - rate(narrow_A_bare, n_narrow_A)))
    print("Class B bare=%.3f sub=%.3f gain=%+.3f" % (
        rate(narrow_B_bare, n_narrow_B), rate(narrow_B_sub, n_narrow_B),
        rate(narrow_B_sub, n_narrow_B) - rate(narrow_B_bare, n_narrow_B)))

    print("\n=== BROAD (canonical OR prompt-hint) ===")
    print("n_A = %d, n_B = %d" % (n_broad_A, n_broad_B))
    pA_b = rate(broad_A_bare, n_broad_A); pA_s = rate(broad_A_sub, n_broad_A)
    pB_b = rate(broad_B_bare, n_broad_B); pB_s = rate(broad_B_sub, n_broad_B)
    print("Class A bare=%.3f sub=%.3f gain=%+.3f" % (pA_b, pA_s, pA_s - pA_b))
    print("Class B bare=%.3f sub=%.3f gain=%+.3f" % (pB_b, pB_s, pB_s - pB_b))

    print("\n=== HONEST DISPOSITION (broad heuristic; n_A=%d) ===" % n_broad_A)
    gA = pA_s - pA_b
    gB = pB_s - pB_b
    if gA < -0.05:
        print("HARD_FAIL (wrong-direction): gain_A_broad = %+.3f" % gA)
    elif gA >= 0.15:
        if gB >= 0.05:
            print("MIDDLE_BAND: gain_A_broad %+.3f >= +15 BUT Class B gain %+.3f >= +5 (lift not retrieval-specific)" % (gA, gB))
        else:
            print("HARD_PASS candidate: gain_A_broad %+.3f >= +15 AND Class B gain %+.3f < +5" % (gA, gB))
    elif gA >= 0.05:
        print("MIDDLE_BAND: gain_A_broad %+.3f in [+5, +15)" % gA)
    else:
        print("HARD_FAIL: gain_A_broad %+.3f < +5" % gA)

    print("\nNote: NARROW n_A=%d is too small (<15) for the +15pt bar to be statistically robust." % n_narrow_A)
    print("BROAD n_A=%d is the operative cert disposition; report BOTH to Skunkworks for landed-VET." % n_broad_A)
    return 0


if __name__ == "__main__":
    sys.exit(main())
