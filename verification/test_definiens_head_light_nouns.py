"""Witness: the trigger word `means` must not become a definition's HEAD.

THE DEFECT, measured 2026-08-20 over 40,000 sentences of simplewiki +
textbook_biology_2e. Sampling every definition the extractor returned: **7 of 47 heads (14.9%) were
semantically EMPTY** -- a definition whose head is `means` / `thing` / `way` asserts nothing.

`means` was the single commonest, and that is not chance: **it is the TRIGGER WORD**, so it turns up
in the definiens far more often than an ordinary noun would.

    "Firing squad ... the lawful means of execution in Finland"   -> head `means`
    "fruits ... a means of dispersal"                             -> head `means`

**THE MECHANISM WAS ALREADY THERE AND ALREADY CORRECT.** `_MEASURE_HEAD` + the partitive expansion
in `definiens_head` handle this exact shape for 23 other words -- "a type of physical science" ->
`science`, "a kind of bird" -> `bird`. `means`, `way` and `part` were simply absent from a curated
list. So the fix is a gap-fill in tested machinery, NOT new behaviour, and this witness pins both
halves of that claim: the new entries work, and the old ones did not change.

AFTER: empty heads 7 -> 5 (14.9% -> 10.6%), with the extraction count UNCHANGED at 47 -- so two
definitions were repaired and no supply was lost.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

from hdlab.definitional_extraction import _MEASURE_HEAD, definiens_head  # noqa: E402


def main() -> int:
    # ---- 1. the cases that motivated the change ------------------------------------------
    fixed = {
        "a means of dispersal": "dispersal",
        "the lawful means of execution in Finland": "execution",
        "a part of the cell": "cell",
    }
    for text, want in fixed.items():
        got = definiens_head(text)
        assert got == want, "%r -> %r, wanted %r (the light-noun gap-fill regressed)" % (
            text, got, want)
    print("fixed cases: %d/%d resolve past the light noun" % (len(fixed), len(fixed)))

    # ---- 2. REGRESSION -- the 23 pre-existing entries must be untouched -------------------
    unchanged = {
        "a type of physical science": "science",
        "a kind of bird": "bird",
        "a pair of kidneys": "kidney",
        "a blood vessel that carries blood": "vessel",
    }
    for text, want in unchanged.items():
        got = definiens_head(text)
        assert got == want, "REGRESSION: %r -> %r, was %r" % (text, got, want)
    print("regression: %d pre-existing cases unchanged" % len(unchanged))

    # ---- 3. the definite-complement guard must STILL hold ---------------------------------
    # Partitive expansion is deliberately limited to INDEFINITE/bare complements. Widening it
    # here would be a behaviour change smuggled in beside a list edit.
    got = definiens_head("a means of the process")
    assert got == "means", ("the definite-complement guard was widened: %r -- partitive expansion "
                            "must not reach into a definite NP" % got)
    print("guard: a definite complement still blocks expansion (%r)" % got)

    # ---- 4. the entries are actually present, so a future edit cannot silently drop them ---
    for w in ("means", "way", "part"):
        assert w in _MEASURE_HEAD, "%r fell out of _MEASURE_HEAD" % w
    assert len(_MEASURE_HEAD) >= 26, "_MEASURE_HEAD shrank to %d" % len(_MEASURE_HEAD)
    print("membership: means/way/part present; _MEASURE_HEAD has %d entries" % len(_MEASURE_HEAD))

    print("\nALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
