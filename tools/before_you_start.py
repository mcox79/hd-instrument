"""BEFORE YOU START: run the prior-work check on what you are ABOUT TO DO, in one command.

WHY THIS EXISTS. On 2026-08-21 I proposed SEVEN pieces of work that were already answered on disk:
build the foraging organ (built, PINNED, run at 10k sentences); improve coreference that way
(HARD_FAIL on that exact mechanism); turn on the graded switches (already default-ON, and already
floored); hand-score 100 facts (a BLIND 100-row score already existed, done and written up); gate
writes by prediction error (already dissociated -- a random gate at the same rate ties it); sweep the
write rate (already swept, four thresholds); wire the sensorimotor spoke (already scored, 3 seeds,
40k sentences each).

**EACH WAS ONE `experiment_index` QUERY AWAY, AND I RAN THAT TOOL FAITHFULLY -- ON THE THING I WAS
*BUILDING*, NEVER ON THE THING I WAS *DOING*.** The standing rule says "before building OR wiring
anything, query BOTH archives". Hand-scoring is neither building nor wiring, so the rule never fired.

**SO THIS TAKES A PLAIN-ENGLISH DESCRIPTION OF THE INTENDED WORK AND QUERIES THE VERBS AS WELL AS THE
NOUNS.** "I am going to hand-score the grounding output" queries `hand-score`, `score`, `grounding`,
`quality` -- not just the organ name.

**IT CANNOT RETURN SILENTLY.** Every run prints what it searched and how many rows it scanned, because
`substrate_query.sh` returning zero bytes and exiting 0 is the failure this whole archive line exists
to prevent, and `experiment_index` itself once shipped a variant of it.

USAGE
  python tools/before_you_start.py "hand-score the definitional grounding output"
  python tools/before_you_start.py --self-test
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = str(REPO / ".venv" / "Scripts" / "python.exe")
INDEX = REPO / "tools" / "experiment_index.py"
REGISTRY = REPO / "data" / "capability_registry.jsonl"

# ACTIVITY VERBS -- the half that was never queried. Each maps to the words the archive actually
# uses, because a cell is named for what it MEASURED, not for what its author was doing that day.
ACTIVITY = {
    "hand-score": ["handscore", "blind", "quality"],
    "handscore": ["handscore", "blind", "quality"],
    "score": ["quality", "handscore"],
    "grade": ["quality", "handscore"],
    "sweep": ["sweep", "gating rate"],
    "gate": ["ingest gate", "write gate", "quality gate"],
    "wire": ["wire", "wiring"],
    "audit": ["audit", "coverage"],
    "measure": ["instrument", "quality"],
    "evaluate": ["evaluation", "quality"],
    "build": ["build"],
    "read": ["reading", "read grow"],
    "extract": ["extraction", "extractor"],
    "encode": ["encoder", "encoding quality"],
    "select": ["selection"],
    "rank": ["ranking", "rank"],
    "place": ["cold placement", "placement"],
    "forage": ["information foraging", "gap driven"],
    "predict": ["predictive coding", "surprise"],
}
STOP = set("the a an of to for on in and or i we you it that this is are be will would should our my "
           "am going next then with from by at as it's its into out up".split())


def terms_from(text: str):
    words = [w for w in re.findall(r"[a-zA-Z][a-zA-Z\-']+", text.lower()) if w not in STOP]
    nouns, acts = [], []
    for w in words:
        base = w.rstrip("s") if len(w) > 4 else w
        for key in (w, base):
            if key in ACTIVITY:
                acts.extend(ACTIVITY[key])
                break
        else:
            if len(w) > 3:
                nouns.append(w)
    seen, out = set(), []
    for t in acts + nouns:                       # ACTIVITIES FIRST -- they are the ones that get missed
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:10]


def run_query(term: str):
    try:
        r = subprocess.run([PY, str(INDEX), "query", term], capture_output=True, text=True,
                           timeout=180, cwd=str(REPO))
    except Exception as e:
        return None, "ERROR %s" % type(e).__name__
    out = r.stdout or ""
    m = re.search(r"\[query\] (\d[\d,]*) matching cells \((\d[\d,]*) landed\)", out)
    if not m:
        return None, "no count line -- TOOL PROBLEM, not an absence"
    n = int(m.group(1).replace(",", ""))
    landed = int(m.group(2).replace(",", ""))
    corr = out.count("!! CORRECTION ON THIS CELL")
    verdicts = re.findall(r"verdict: (\S+)", out)
    return (n, landed, corr, verdicts[:4]), None


def main():
    if "--self-test" in sys.argv:
        return _self_test()
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[-3])
        return 2
    text = " ".join(a for a in sys.argv[1:] if not a.startswith("--"))
    terms = terms_from(text)
    print("=" * 78)
    print("BEFORE YOU START:  %s" % text)
    print("=" * 78)
    print("querying %d terms (ACTIVITIES FIRST -- those are the ones that get missed): %s\n"
          % (len(terms), ", ".join(terms)))
    total = 0
    for t in terms:
        res, err = run_query(t)
        if err:
            print("  %-26s !! %s" % (t, err))
            continue
        n, landed, corr, verdicts = res
        total += n
        flag = "   " if n == 0 else ">> "
        print("%s%-26s %3d cells (%d landed)%s" % (flag, t, n, landed,
              ("   [%d CELL(S) CARRY A CORRECTION]" % corr) if corr else ""))
        for v in verdicts:
            print("       %s" % v[:96])
    print()
    if total == 0:
        print("NO PRIOR WORK FOUND ON ANY TERM. That is a real absence ONLY because every query above")
        print("printed its scan count. If a term errored, treat it as UNKNOWN, not as absent.")
    else:
        print("!! %d total matches. READ EVERY ROW A QUERY RETURNED BEFORE QUOTING ANY OF THEM --" % total)
        print("   on 2026-08-21 a 4-row result was read at row 1, and row 4 reversed row 1.")
    print("\nSTILL TO DO BY HAND: `python tools/organ_map_cite.py <ORGAN_ID>` if an organ is involved,")
    print("and grep data/capability_registry.jsonl for the capability name.")
    return 0


def _self_test():
    """A prior-work tool that has never been shown to return NON-zero cannot establish absence."""
    t = terms_from("hand-score the definitional grounding output")
    assert "handscore" in t, "activity verb not extracted: %r" % t
    assert t.index("handscore") < t.index("definitional"), "activities must be queried FIRST: %r" % t
    t2 = terms_from("sweep the write rate")
    assert any(x in t2 for x in ("sweep", "gating rate")), t2
    # POSITIVE CONTROL against the live index -- a known-present term must return rows.
    res, err = run_query("quality")
    assert err is None, "query failed: %s" % err
    assert res[0] > 50, "known-present term 'quality' returned %r -- the index is broken" % (res,)
    # NEGATIVE CONTROL -- a nonsense term must return zero, proving non-zero means something.
    res2, err2 = run_query("zzqqxx_not_a_real_term")
    assert err2 is None and res2[0] == 0, "known-absent term returned %r" % (res2,)
    print("self-test PASS (verb extraction, activities-first ordering, "
          "known-present control %d cells, known-absent control 0)" % res[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
