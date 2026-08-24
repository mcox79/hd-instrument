"""Strip MORPHOLOGICAL LEAKAGE from a WordNet gold set, so a spelling control cannot win on form.

WHY THIS IS PROMOTED HERE (2026-08-24, owner ruling on board Q117: *"why not fix the bar, and re run
the past results. let's do this right."*).

Measured on 2026-08-23 (`data/exp_c3_surprise_weighted_vs_bundling_v1/metrics.json`, run_mode full,
n=4,000): the character-trigram spelling control that has been the strongest no-understanding floor
on the c3 task scores 0.0867 on the shipped WordNet gold and 0.0193 once stem-sharing neighbours are
removed -- and at [0.0153, 0.0238] that residue OVERLAPS its own info-free shuffled twin
[0.0135, 0.0213]. **About 78% of that floor was words being spelled alike, not meaning alike**
(nation/national, volcano/volcanic), because derivational relatives share both a stem AND a synset.

This function was written inside one experiment. It is promoted because the GATES now need it too,
and a rule enforced by a copy in one file is a rule that drifts.

⚠️ **THE BAR AND THE GOLD MUST MOVE TOGETHER, AND THE BAR MUST BE RECOMPUTED IN ITS OWN HARNESS.**
Do NOT import 0.0193 as a constant: that number belongs to one cell's item construction (n=3,988),
and this project's standing rule is that no number crosses populations. A harness that switches to
stripped gold must re-measure its own trigram floor and use THAT.

THE STRIP IS DELIBERATELY OVER-INCLUSIVE -- it removes more than strictly necessary. That is the
conservative direction here: over-removing shrinks the gold and can only make the remaining task
HARDER for every arm equally, whereas under-removing leaves leakage that flatters the spelling
control specifically.
"""
import os

try:                                                    # optional; the prefix/substring rules below
    from nltk.stem import PorterStemmer                 # carry the test on their own without it
    _STEMMER = PorterStemmer()
except Exception:                                       # noqa: BLE001
    _STEMMER = None

try:
    from hdlab.lemma_norm import normalize_lemma
except Exception:                                       # noqa: BLE001
    def normalize_lemma(w):                             # last-resort identity, never silently wrong
        return (w or "").strip().lower()


def shares_stem(a: str, b: str) -> bool:
    """Over-inclusive shared-stem / shared-form test.

    Fires on run/running, nation/national, volcano/volcanic; NOT on dog/cat.
    """
    a, b = (a or "").lower(), (b or "").lower()
    if a == b:
        return True
    if normalize_lemma(a) == normalize_lemma(b):
        return True
    if _STEMMER is not None and _STEMMER.stem(a) == _STEMMER.stem(b):
        return True
    p = os.path.commonprefix([a, b])
    if len(p) >= 4 and min(len(a), len(b)) >= 4:
        return True
    if len(a) >= 4 and a in b:
        return True
    if len(b) >= 4 and b in a:
        return True
    return False


def strip_gold(lemma: str, gold) -> frozenset:
    """`gold` with every stem/form-sharing neighbour of `lemma` removed."""
    return frozenset(g for g in gold if not shares_stem(g, lemma))


def self_test() -> int:
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[self-test] %-62s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    # POSITIVE: the cases the 78% is made of must fire.
    for a, b in (("nation", "national"), ("volcano", "volcanic"), ("run", "running"),
                 ("abandon", "abandoned"), ("govern", "government")):
        chk("morphological relative is caught: %s/%s" % (a, b), shares_stem(a, b))

    # NEGATIVE CONTROL: a checker that fires on everything removes the whole gold and would make
    # every arm score 0 -- which would look like a "clean" floor and mean nothing.
    for a, b in (("dog", "cat"), ("car", "automobile"), ("happy", "glad"), ("buy", "purchase")):
        chk("genuine synonym/associate is NOT caught: %s/%s" % (a, b), not shares_stem(a, b))

    gold = frozenset({"national", "country", "state", "nationality"})
    out = strip_gold("nation", gold)
    chk("strip_gold removes the form-sharing members only",
        out == frozenset({"country", "state"}), "kept %s" % sorted(out))
    chk("strip_gold leaves a NON-empty gold on a realistic set", len(out) > 0)
    chk("strip_gold on an empty gold returns empty, never raises",
        strip_gold("x", frozenset()) == frozenset())

    print("[self-test] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(self_test())
