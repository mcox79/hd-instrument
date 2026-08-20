"""THE PLAN'S TOP ITEM: of the landed replay/consolidation cells, did ANY change the KIND of code?

WHY THIS AND NOT ANOTHER EXPERIMENT. Eleven write-side interventions have closed. The only two
things that ever moved the representation -- coverage, and a post-hoc centring transform -- are
NOT rules about writing. That points at consolidation as a TRANSFORMATION rather than a summation.
But `replay` returns 211 cells / 176 landed and `consolidation` 114 / 100, so "nobody tried it" is
not a claim anyone may make here without an ENUMERATION. This is that enumeration.

THE DISCRIMINATING QUESTION, and it is arithmetic rather than a matter of taste:
  Does the cell's stored representation remain a (re)WEIGHTED SUM of the input traces, or is it a
  NON-LINEAR function of them?
Selection, gating, reweighting, prioritised replay and scalar normalisation ALL leave the code a
weighted sum -- they only change the weights, and a weight of zero is still a weight. What leaves
that family is an element-wise or set-wise NON-LINEARITY: sparsification/k-WTA, quantisation,
clustering to a prototype, binding, rank truncation, or an error-driven learned transform.

*** THE TRAP THIS SCRIPT IS BUILT AROUND. *** A keyword filter shares its blind spots with the
thing it filters, which is this project's most-repeated fault (five recorded instances, most
recently a mojibake detector that verified its own fix with the regex that caused it). So:
  1. Keywords only SURFACE candidates; they never decide. Every surfaced cell is printed in full
     for a human read.
  2. A POSITIVE CONTROL runs first: cells we already KNOW are non-linear (k-WTA, sparsify, sign,
     codebook) MUST be surfaced. If the filter cannot find those, the filter is broken and the
     run REFUSES rather than reporting a comfortable "nothing found".
  3. The NEGATIVE side is reported too -- how many landed cells matched NOTHING -- because a
     filter that matches 3 of 176 is not evidence about the other 173.
"""
import json
import os
import re
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INDEX = os.path.join(_REPO, "data", "experiment_index.jsonl")

# The population: anything about replay or consolidation.
POP = ("replay", "consolidat")

# NON-LINEAR operations -- these leave the weighted-sum family.
NONLINEAR = {
    "sparsify":   r"\bk-?wta\b|\btop-?k\b|sparsif|sparse cod|winner.take.all",
    "quantise":   r"\bnp\.sign\b|binaris|binariz|quantis|quantiz|\bternary\b|\bbipolar sign\b",
    "prototype":  r"prototyp|codebook|cluster|vector quantis|vector quantiz|centroid",
    "bind":       r"\bbind(ing)?\b|circular convolution|\bhrr\b|\bfhrr\b|permut",
    "truncate":   r"\bsvd\b|\bpca\b|rank.?truncat|low.?rank|eigen",
    "learned":    r"learned (transform|projection|encoder)|backprop|gradient descent|delta rule|error.driven",
    "attractor":  r"attractor|hopfield|pattern complet|\bca3\b|iterative clean",
}
# LINEAR operations -- these only change the WEIGHTS, so the code stays a weighted sum.
LINEAR = {
    "select":     r"\bgate\b|\bgating\b|select|prioritis|prioritiz|schedul|which traces|skip",
    "reweight":   r"reweight|re-weight|weight(ing|ed) by|precision|surpris|novelt|salien",
    "normalise":  r"normalis|normaliz|\bscal(e|ing)\b|divisive",
}


def load():
    rows = []
    with open(INDEX, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def text_of(r):
    return " ".join(str(r.get(k) or "") for k in ("cell", "headline", "verdict")).lower()


def hits(txt, table):
    return sorted(k for k, pat in table.items() if re.search(pat, txt))


def main():
    rows = load()
    print("index rows: %d" % len(rows))

    # ---- POSITIVE CONTROL: the filter must find things we KNOW are non-linear ----------------
    # These are searched across the WHOLE index, not the replay subset -- the control is about the
    # FILTER's sensitivity, not about the population.
    ctrl = [r for r in rows if hits(text_of(r), NONLINEAR)]
    print("positive control: %d of %d cells anywhere in the index match a NON-LINEAR operation"
          % (len(ctrl), len(rows)))
    if len(ctrl) < 20:
        print("\nREFUSING TO REPORT. The non-linear filter matched almost nothing across the whole\n"
              "archive, which means it is broken rather than that the archive is linear. A filter\n"
              "that cannot find k-WTA or binding in 8,836 cells cannot be trusted to report their\n"
              "absence in a subset.")
        return 2
    by_op = {}
    for r in ctrl:
        for k in hits(text_of(r), NONLINEAR):
            by_op[k] = by_op.get(k, 0) + 1
    print("   by operation: %s" % json.dumps(by_op, sort_keys=True))

    # ---- THE POPULATION ----------------------------------------------------------------------
    pop = [r for r in rows if any(p in text_of(r) for p in POP)]
    landed = [r for r in pop if r.get("landed")]
    print("\npopulation: %d replay/consolidation cells, %d LANDED" % (len(pop), len(landed)))

    nl, lin, neither = [], [], []
    for r in landed:
        t = text_of(r)
        h_nl, h_li = hits(t, NONLINEAR), hits(t, LINEAR)
        if h_nl:
            nl.append((r, h_nl, h_li))
        elif h_li:
            lin.append((r, h_li))
        else:
            neither.append(r)

    print("   NON-LINEAR candidates : %3d" % len(nl))
    print("   linear-only (weights) : %3d" % len(lin))
    print("   matched NOTHING       : %3d   <-- the filter says nothing about these" % len(neither))

    # ---- THE CANDIDATES, IN FULL, FOR A HUMAN READ -------------------------------------------
    print("\n" + "=" * 100)
    print("NON-LINEAR CANDIDATES -- these are the only cells that could have changed the KIND of")
    print("code. Keywords SURFACED them; a human decides. Verdict shown because a HARD_FAIL that")
    print("changed the kind of code is still an answer to 'has this been tried'.")
    print("=" * 100)
    nl.sort(key=lambda x: (str(x[0].get("verdict")), x[0]["cell"]))
    for r, h_nl, h_li in nl:
        print("\n--- %s" % r["cell"])
        print("    landed %s | verdict: %s" % (r.get("landed_date"), str(r.get("verdict"))[:110]))
        print("    ops: NONLINEAR=%s  linear=%s" % (",".join(h_nl), ",".join(h_li) or "-"))
        print("    %s" % (str(r.get("headline") or "")[:400].replace("\n", " ")))

    print("\n" + "=" * 100)
    print("MATCHED NOTHING (%d) -- listed so the residue is visible rather than assumed empty."
          % len(neither))
    print("=" * 100)
    for r in neither:
        print("  %-70s %s" % (r["cell"][:70], str(r.get("verdict"))[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
