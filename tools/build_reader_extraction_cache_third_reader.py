"""Build a DETERMINISTIC cache of the reader's ACTUAL extracted role-filler tuples on the
McGuffey Third Reader, for the reader-coupled factorization cell. This runs the REAL reader
(exp_read_nested_clause_relative_third_reader_v1, nest ON) ONCE and dumps its noisy extractions
so the factorization cell is fast + reproducible. The NOISE is preserved (extractions NOT cleaned).

Output: data/_reader_extractions_third_reader_v1.json
  { "corpus": ..., "n_passages": int, "n_tuples": int, "tuple_kinds": {...},
    "svo": [[verb, subj, obj], ...], "goal": [...], "recipient": [...], "loc": [...], "poss": [...] }

ASCII-only. Deterministic (fixed clf fit + fixed reader seed; sorted output).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import sys
import json
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST  # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2    # noqa: E402

OUT_PATH = os.path.join(REPO, "data", "_reader_extractions_third_reader_v1.json")


def main():
    passages = NEST.load_lessons()
    clf = V2._fit_clf()
    res = NEST.read_corpus(clf, passages, nest=True)
    foundation = res["foundation"]

    svo, goal, recipient, loc, poss = [], [], [], [], []
    for r in sorted(foundation, key=lambda x: (x[0], tuple(str(y) for y in x[1:]))):
        k = r[0]
        if k == "svo" and len(r) == 4:
            # skip copular "kind" pseudo-verb (not a lexical relation-type)
            if r[1] == "kind":
                continue
            svo.append([r[1], r[2], r[3]])
        elif k == "goal" and len(r) == 4:
            goal.append([r[1], r[2], r[3]])
        elif k == "recipient" and len(r) == 4:
            recipient.append([r[1], r[2], r[3]])
        elif k == "loc" and len(r) == 3:
            loc.append([r[1], r[2]])
        elif k == "poss" and len(r) == 3:
            poss.append([r[1], r[2]])

    kinds = Counter(r[0] for r in foundation)
    out = {
        "corpus": "mcguffey_third_reader.clean.txt (PG#14766, PD)",
        "reader": "exp_read_nested_clause_relative_third_reader_v1 (nest ON) @ argstruct/deixis reader chain",
        "n_passages": len(passages),
        "n_tuples": len(foundation),
        "tuple_kinds": dict(kinds),
        "svo": svo, "goal": goal, "recipient": recipient, "loc": loc, "poss": poss,
        "note": ("Reader's ACTUAL noisy extractions (NOT cleaned). Corpus-wide extraction precision "
                 "~0.40-0.60 CITED@notes/research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md."),
    }
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    os.replace(tmp, OUT_PATH)
    print(f"[cache] wrote {OUT_PATH}", flush=True)
    print(f"[cache] passages={len(passages)} tuples={len(foundation)} kinds={dict(kinds)}", flush=True)
    print(f"[cache] svo={len(svo)} goal={len(goal)} recipient={len(recipient)} loc={len(loc)} poss={len(poss)}",
          flush=True)


if __name__ == "__main__":
    main()
