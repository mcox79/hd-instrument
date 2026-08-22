"""DRAW A *REPRESENTATIVE* BLIND SAMPLE OF LEARNED FACTS, READY FOR A HUMAN TO SCORE.

WHY THIS EXISTS. Six separate questions this week ended at the same wall: we have no representative
hand-scored sample of what the substrate learned. The one that exists (100 rows,
`exp_grounding_quality_readout_v1`) was drawn 50/50 ACROSS TWO ARMS and weighted to the hardest
segment, because its job was to measure an arm DELTA. That is the right design for a difference and
the wrong design for a LEVEL -- and measured, it passes the validated quality proxy at 0.3200 where
the full foundations pass at 0.5683 and 0.5016, CIs not overlapping. It is materially harder than the
bulk, so its 3 MEANINGFUL / 19 RELATED / 78 NOISE cannot be quoted as the foundation's quality.

WHAT THIS DOES. Draws N facts UNIFORMLY AT RANDOM from a foundation snapshot, shuffles them, strips
every hint of provenance, and writes:
    <out>/blind_sheet.txt   -- numbered `subject -> object` lines for a human, nothing else
    <out>/blind_key.json    -- index -> (subject, obj), for joining AFTER scoring
No arm, no segment, no score, no proxy verdict is visible on the sheet. The scorer sees facts.

THE REPRESENTATIVENESS CHECK IS THE POINT, AND IT IS ENFORCED. `--check` refuses to write a sample
whose validated-proxy pass rate differs materially from the population it was drawn from. A uniform
draw should match its population; if it does not, the draw is broken. THIS IS EXACTLY THE PROPERTY
THE EXISTING SAMPLE LACKS, and nothing checked it at the time.

SCORING INSTRUCTION FOR THE HUMAN, kept identical to the existing scale so the two are comparable:
    MEANINGFUL -- the object genuinely gives the subject's meaning
    RELATED    -- topically connected but not a meaning (whisky -> wedding)
    NOISE      -- neither
Write one word per line into a file of your own; `blind_key.json` joins it afterwards.

THIS TOOL DOES NOT SCORE. It cannot: the point of a blind sample is that whoever built it does not
label it, and I have already read this material.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import json
import math
import random
import sys
from typing import List, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

DEFAULT_SNAPSHOT = "data/foundation_snapshots/reading_grounding_v2q_full_20260815T182838Z"
DEFAULT_N = 150          # power 0.82 for the declared trend test; see tools/graded_cooccurrence_quality
MAX_PASS_RATE_DRIFT = 0.12


def _wilson(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), c + h


def load_facts(snapshot: str) -> List[Tuple[str, str]]:
    """All distinct grounded-meaning (subject, object) pairs in a snapshot. READ-ONLY."""
    from hdlab.foundation_persistence import load_store
    import exp_foundation_validation_harness_v1 as V1
    store = load_store(os.path.join(snapshot, "store"))
    facts = [f for f in store._facts
             if f.relation == V1.GM_REL and f.status in ("ACTIVE", "COMBINED")]
    return sorted({(f.subject, f.obj) for f in facts if f.subject != f.obj})


def draw(snapshot: str, n: int, seed: int, out_dir: str, check: bool = True) -> dict:
    from hdlab import quality_proxy as QP
    from exp_foundation_validation_harness_v1 import load_corpus_sentences, CORPUS_SOURCES_FULL

    pop = load_facts(snapshot)
    if len(pop) < n:
        raise ValueError(f"population has {len(pop)} facts, cannot draw {n}")
    rng = random.Random(seed)
    sample = rng.sample(pop, n)            # UNIFORM, no stratification, no arm balancing

    toks = QP.tokenize_corpus(load_corpus_sentences(CORPUS_SOURCES_FULL))
    pop_hit = sum(1 for s, o in pop if QP.is_meaningful_fact(s, o, toks))
    smp_hit = sum(1 for s, o in sample if QP.is_meaningful_fact(s, o, toks))
    pop_rate, smp_rate = pop_hit / len(pop), smp_hit / n
    drift = abs(smp_rate - pop_rate)
    lo, hi = _wilson(smp_hit, n)

    report = {
        "snapshot": snapshot, "population": len(pop), "n": n, "seed": seed,
        "population_proxy_pass_rate": round(pop_rate, 4),
        "sample_proxy_pass_rate": round(smp_rate, 4),
        "sample_pass_ci": [round(lo, 4), round(hi, 4)],
        "drift": round(drift, 4), "max_allowed_drift": MAX_PASS_RATE_DRIFT,
        "representative": bool(drift <= MAX_PASS_RATE_DRIFT),
    }
    if check and not report["representative"]:
        raise AssertionError(
            f"REFUSING to write: sample pass rate {smp_rate:.4f} differs from population "
            f"{pop_rate:.4f} by {drift:.4f} > {MAX_PASS_RATE_DRIFT}. A uniform draw should match its "
            f"population; this one does not, so the draw is broken.")

    os.makedirs(out_dir, exist_ok=True)
    shuffled = list(sample)
    rng.shuffle(shuffled)
    with open(os.path.join(out_dir, "blind_sheet.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("BLIND SCORING SHEET -- write MEANINGFUL / RELATED / NOISE for each line.\n")
        fh.write("MEANINGFUL = the object genuinely gives the subject's meaning.\n")
        fh.write("RELATED    = topically connected but not a meaning (whisky -> wedding).\n")
        fh.write("NOISE      = neither.\n")
        fh.write("No arm, segment or automatic score is shown. That is deliberate.\n\n")
        for i, (s, o) in enumerate(shuffled, 1):
            fh.write(f"{i:4d}.  {s}  ->  {o}\n")
    with open(os.path.join(out_dir, "blind_key.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"report": report,
                   "key": [{"idx": i, "subj": s, "obj": o}
                           for i, (s, o) in enumerate(shuffled, 1)]}, fh, indent=1)
    return report


def _self_test() -> int:
    """Controls. The representativeness gate must fire on a KNOWN-biased draw, or it is decoration."""
    ok = True
    from hdlab import quality_proxy as QP
    from exp_foundation_validation_harness_v1 import load_corpus_sentences, CORPUS_SOURCES_FULL

    pop = load_facts(os.path.join(REPO, DEFAULT_SNAPSHOT))
    toks = QP.tokenize_corpus(load_corpus_sentences(CORPUS_SOURCES_FULL))
    flags = [(s, o, QP.is_meaningful_fact(s, o, toks)) for s, o in pop]
    pop_rate = sum(1 for _s, _o, h in flags if h) / len(flags)

    # POSITIVE: a uniform draw must land within tolerance of the population.
    rng = random.Random(4)
    smp = rng.sample(flags, 150)
    drift = abs(sum(1 for _s, _o, h in smp if h) / 150 - pop_rate)
    if drift > MAX_PASS_RATE_DRIFT:
        print(f"  FAIL uniform draw drifted {drift:.4f}")
        ok = False
    else:
        print(f"  PASS uniform draw is representative (drift {drift:.4f} <= {MAX_PASS_RATE_DRIFT})")

    # NEGATIVE: a deliberately biased draw (all proxy-failing facts, like the arm-balanced sample
    # turned out to be) MUST be caught. A gate nobody has seen fire is a gate nobody has tested.
    fails = [t for t in flags if not t[2]]
    if len(fails) >= 150:
        biased = fails[:150]
        d2 = abs(sum(1 for _s, _o, h in biased if h) / 150 - pop_rate)
        if d2 <= MAX_PASS_RATE_DRIFT:
            print(f"  FAIL biased draw NOT caught (drift {d2:.4f})")
            ok = False
        else:
            print(f"  PASS biased draw caught (drift {d2:.4f} > {MAX_PASS_RATE_DRIFT})")
    else:
        print(f"  SKIP biased-draw control: only {len(fails)} failing facts available")

    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: List[str]) -> int:
    if "--self-test" in argv:
        return _self_test()
    snap = os.path.join(REPO, DEFAULT_SNAPSHOT)
    n = DEFAULT_N
    for i, a in enumerate(argv):
        if a == "--n" and i + 1 < len(argv):
            n = int(argv[i + 1])
        elif a == "--snapshot" and i + 1 < len(argv):
            snap = argv[i + 1]
    out = os.path.join(REPO, "data", "blind_samples",
                       f"representative_{os.path.basename(snap)[:28]}_n{n}")
    rep = draw(snap, n, seed=20260822, out_dir=out, check=True)
    print(json.dumps(rep, indent=1))
    print(f"\nwrote {out}/blind_sheet.txt  and  blind_key.json")
    print("THIS TOOL DOES NOT SCORE. A human writes the labels; the key joins them afterwards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
