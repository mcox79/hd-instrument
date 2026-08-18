"""RE-SCORE EVERY LANDED CELL AGAINST THE STRONGEST FLOOR IT ALREADY HAS ON DISK.

!!! UNRELIABLE -- DO NOT ACT ON ITS FLAGS WITHOUT READING THE CELL. SPOT-CHECKED AND FAILED. !!!

    2026-08-18 spot-check, one flagged cell, verified against its own metrics:
    `exp_causal_link_comprehension_pilot_v1` was flagged "floor 1.0000 >= arm 0.1000". Its REAL
    numbers are `organ_accuracy_integration = 0.95` vs `most_recent_accuracy_integration = 0.10`
    -- the organ WINS by 0.85. The sweep had picked the BASELINE measured on easy items as the
    "floor" and the SAME BASELINE measured on hard items as the "arm", and compared a baseline
    to itself. An earlier version was worse still, comparing a law coefficient against an error
    term across incommensurable scorers.

    THE LESSON, WHICH IS THE USEFUL OUTPUT OF THIS FILE: deciding WHICH NUMBER IS THE ARM AND
    WHICH IS THE FLOOR IS A SEMANTIC JUDGEMENT THAT KEY NAMES DO NOT ENCODE. Across 7,788
    heterogeneous schemas there is no naming convention to lean on, so a mechanical re-flooring
    sweep cannot be trusted. The Director proposed this as "the cheapest fix in the backlog"; the
    spot-check the owner asked for is what caught it. Vetting by reading the cell -- which found
    a refutation, two suspensions and three qualifications in six cells -- remains the method
    that works.

    KEPT, not deleted, for two narrow uses: `--cell NAME` dumps one cell's harvested numbers,
    which is a genuinely useful reading aid; and `--stub` finds floors sitting at exactly 0.0 or
    1.0, which are usually by-construction placeholders rather than measurements.

WHY (2026-08-18 vet, `a2e65896`). Vetting six claimed HARD_PASS cells found the same defect twice,
and it needs NO new experiment to detect:

  `exp_base_reader_grounded_relations_coref_v1` COMPUTED a proper frequency floor, stored it as
  `acc_CO = 0.714`, and then defined its primary discriminator as FULL minus NOCOREF instead. Scored
  against the floor it already had, the headline dies (full vs floor: 2/1 discordant, p = 1.0000).

  `exp_read_grow_foundation_realprose_glassbox_ie_v1` gated on a HARDCODED literal 1.0 imported from
  a different cell on a different corpus, having run no floor on its own 34 sentences.

So: a cell can carry the evidence that kills its own headline and never be compared against it. This
sweep finds those cells mechanically, across the whole archive, without running any science.

WHAT IT DOES. For each `data/exp_*/metrics.json`: harvest every FLOOR-LIKE number and every ARM-LIKE
number by key name, then flag the cell when the strongest floor on disk is at or above the best arm
on disk. That is the signature of "the comparison it made was not the comparison it should have
made".

WHAT THIS IS NOT, AND THE LIMIT IS LOAD-BEARING. **This is a CANDIDATE DETECTOR, not a verdict.**
Metrics schemas vary wildly across 7,794 cells, so key-name matching WILL produce false positives:
a "floor" key may be an arm's own diagnostic, an "arm" key may be a control, and two numbers may live
on different scorers or populations entirely -- and NO NUMBER CROSSES SCORERS in this project. Every
flag must be confirmed by reading the cell before it is quoted as a defect. The sweep's job is to
turn 199 unbounded re-reads into a short, ranked list worth reading.

It also cannot see the defect that suspended 21 arms on 08-18 -- a floor IMPORTED from another
representation looks like a perfectly good floor from inside the file. `--stub` flags the narrower,
detectable version of that: floors sitting at exactly 0.0 or 1.0, which are usually
by-construction placeholders rather than measurements.

USAGE
  python tools/refloor_sweep.py                 # sweep, print the ranked flags
  python tools/refloor_sweep.py --stub          # also list suspicious 0.0/1.0 floors
  python tools/refloor_sweep.py --cell NAME     # dump one cell's harvested numbers, for spot-checks
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

FLOOR_KEY = re.compile(
    r"floor|scramble|shuffl|permut|constant_prototype|prototype_magnitude|orthographic|"
    r"^f_|_f_|baseline|chance|null|random_|control|untrained", re.I)
ARM_KEY = re.compile(r"auc|acc|accuracy|correct_rate|f1|precision|recall|hit|mrr|rho|score", re.I)
SKIP_KEY = re.compile(r"half_width|hw$|ci95|_ci$|p_value|pval|n_boot|seed|count|_n$|n_|"
                      r"threshold|delta|margin|lift|gap", re.I)


def _numbers(obj, prefix=""):
    """Flatten to (dotted_key, float) for every finite number in [0,1] -- the range every scorer
    in this project reports in. Values outside it are token counts, seeds and sizes, not scores."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(_numbers(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:40]):
            out.extend(_numbers(v, f"{prefix}[{i}]"))
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, (int, float)):
        try:
            f = float(obj)
        except Exception:
            return out
        if 0.0 <= f <= 1.0:
            out.append((prefix, f))
    return out


def harvest(mp: Path):
    try:
        d = json.loads(mp.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None
    nums = _numbers(d)
    floors, arms = [], []
    for k, v in nums:
        leaf = k.split(".")[-1]
        if SKIP_KEY.search(leaf):
            continue
        if FLOOR_KEY.search(k):
            floors.append((k, v))
        elif ARM_KEY.search(leaf):
            arms.append((k, v))
    return floors, arms


def sweep(show_stub=False, limit=45) -> int:
    rows, n_seen, n_parsed = [], 0, 0
    stubs = []
    for d in sorted(os.listdir(DATA)):
        if not d.startswith("exp_"):
            continue
        mp = DATA / d / "metrics.json"
        if not mp.exists():
            continue
        n_seen += 1
        h = harvest(mp)
        if not h:
            continue
        floors, arms = h
        n_parsed += 1
        if show_stub:
            for k, v in floors:
                if v in (0.0, 1.0):
                    stubs.append((d, k, v))
        if not floors or not arms:
            continue
        # COMPARE LIKE WITH LIKE. The first version of this sweep took max(floor) vs max(arm)
        # across ALL harvested numbers, and its top flags were nonsense: a law coefficient
        # (kappa_accumulation 0.0050) against an error term (abs_T_real 0.9941), an accuracy on
        # unseen items against a COVERAGE fraction. That is precisely the "no number crosses
        # scorers" rule being broken by the tool built to enforce it. A floor and an arm are only
        # comparable when they are THE SAME MEASURE -- so they are bucketed by metric name and
        # compared only within a bucket.
        def metric_of(key):
            leaf = key.split(".")[-1].lower()
            for m in ("auc", "correct_rate", "accuracy", "acc", "f1", "precision", "recall",
                      "mrr", "rho", "hit"):
                if m in leaf:
                    return m
            return None
        fb, ab = {}, {}
        for k, v in floors:
            m = metric_of(k)
            if m and v > fb.get(m, (None, -1))[1]:
                fb[m] = (k, v)
        for k, v in arms:
            m = metric_of(k)
            if m and v > ab.get(m, (None, -1))[1]:
                ab[m] = (k, v)
        for m in set(fb) & set(ab):
            fk, fv = fb[m]
            ak, av = ab[m]
            if fv >= av:      # strongest floor >= best arm, ON THE SAME MEASURE
                rows.append((fv - av, d, ak, av, fk, fv, m))
    rows.sort(reverse=True)
    # Counts FIRST and ALWAYS -- an empty result must be distinguishable from a broken sweep.
    print(f"[refloor] scanned {n_seen:,} landed cells, parsed {n_parsed:,}, "
          f"FLAGGED {len(rows):,} (cell, metric) pairs where the strongest floor >= the best arm ON THE SAME MEASURE")
    print("[refloor] THESE ARE CANDIDATES, NOT VERDICTS -- key-name matching cannot tell an arm's "
          "diagnostic from a control, and no number crosses scorers. Read the cell before quoting.\n")
    for gap, cell, ak, av, fk, fv, m in rows[:limit]:
        print(f"  +{gap:.4f}  [{m}]  {cell[:52]}")
        print(f"            best arm   {av:.4f}  {ak[:64]}")
        print(f"            top floor  {fv:.4f}  {fk[:64]}")
    if len(rows) > limit:
        print(f"\n  ... {len(rows)-limit} more")
    if show_stub:
        print(f"\n[refloor] floors sitting at exactly 0.0 or 1.0 (usually by-construction "
              f"placeholders, not measurements): {len(stubs):,}")
        for cell, k, v in stubs[:25]:
            print(f"    {v:.1f}  {cell[:52]}  {k[:56]}")
    return 0


def dump(cell: str) -> int:
    mp = DATA / cell / "metrics.json"
    if not mp.exists():
        print(f"no metrics.json for {cell}", file=sys.stderr)
        return 1
    h = harvest(mp)
    if not h:
        print("unparseable", file=sys.stderr)
        return 1
    floors, arms = h
    print(f"=== {cell}\n--- FLOOR-LIKE ({len(floors)}) ---")
    for k, v in sorted(floors, key=lambda x: -x[1]):
        print(f"  {v:.4f}  {k}")
    print(f"--- ARM-LIKE ({len(arms)}) ---")
    for k, v in sorted(arms, key=lambda x: -x[1]):
        print(f"  {v:.4f}  {k}")
    return 0


def main() -> int:
    if "--cell" in sys.argv:
        return dump(sys.argv[sys.argv.index("--cell") + 1])
    return sweep(show_stub="--stub" in sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
