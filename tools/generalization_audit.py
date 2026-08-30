#!/usr/bin/env python
"""generalization_audit.py -- DERIVED scan: which integrated organs' wins may NOT generalize?

Owner concern (2026-08-30): "many of our results don't generalize." The strongest free predictor
(project audit 2026-08-18) is: did the TEST ITEMS EXIST BEFORE THE MECHANISM? A win on a CONSTRUCTED
gold (minimal pairs / hand-authored vignettes made FOR the mechanism) is generalization-risk; a win on
a PRE-EXISTING corpus/benchmark, a HELD-OUT split, or OUT-OF-VOCAB items is generalization-evidence.

Scans each integrated notes/problems/*/SOLVED.md for those signals and classifies:
  GENERALIZES  -- has held-out / OOV / real-text (pre-existing) evidence
  AT-RISK      -- a constructed/synthetic win with NO held-out/OOV/real-text evidence
  NEGATIVE     -- a rigorous negative (no capability claim to generalize)
  UNCLEAR      -- signals ambiguous

Derives from disk on every run (like tools/wiring_debt.py). Registry is not consulted -- the SOLVED
argument is the source of truth for how a result was validated.

Usage:  python tools/generalization_audit.py            # summary + the AT-RISK list
        python tools/generalization_audit.py --risk     # AT-RISK only, with the signal hits
"""
import os, re, glob, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROB = os.path.join(ROOT, "notes", "problems")

# pre-existing test sources = generalization evidence (items existed before the mechanism)
PREEXISTING = r"(litbank|ud[-_ ]?ewt|ontonotes|simlex|simverb|wordsim|mcscript|\brace\b|onestop|conll|" \
              r"wordnet|framenet|verbnet|cskg|brysbaert|lancaster|mcrae|glove|external benchmark|" \
              r"real[- ]?text|real narrative|real prose|natural text|modern (annotated|text|corpus))"
HELDOUT = r"(held[- ]?out|heldout|out[- ]?of[- ]?vocab|\boov\b|\bunseen\b|generali[sz]|" \
          r"novel (affector|ground|item|word|patient)|cross[- ]?val|transfer)"
CONSTRUCTED = r"(constructed (gold|pair|population|minimal)|minimal pair|synthetic|microworld|" \
              r"hand[- ]?authored|hand[- ]?built|construction (proof|artifact)|authored gold|toy )"
NEGATIVE = r"(rigorous negative|a full pass|net-zero|route closed|does not beat|no hdlab landing|refuted)"
SMALLN = r"\bn ?= ?([1-9]|1[0-9]|2[0-9])\b"   # n <= 29
# FRAGILITY = the win is constructed-headlined and the real-text/generalization tail is THIN.
FRAGILE = r"(construction (proof|artifact)|constructed 1\.000|mechanism demonstration|" \
          r"not a (capability|real-text)|not corpus-generalit|point[- ]?estimate|" \
          r"no labeled real[- ]?text|solver[- ]?adjudicated|a mechanism demonstration|" \
          r"authored (real-english |)gold|synthetic|microworld|does not beat|hand[- ]?adjudicated)"


def classify(text):
    low = text.lower()
    hits = {}
    hits["preexisting"] = len(re.findall(PREEXISTING, low))
    hits["heldout"] = len(re.findall(HELDOUT, low))
    hits["constructed"] = len(re.findall(CONSTRUCTED, low))
    hits["negative"] = len(re.findall(NEGATIVE, low))
    hits["smalln"] = len(re.findall(SMALLN, low))
    hits["fragile"] = len(re.findall(FRAGILE, low))
    generalizes = hits["preexisting"] > 0 or hits["heldout"] > 0
    if hits["negative"] >= 2 and not generalizes:
        cls = "NEGATIVE"
    elif hits["constructed"] > 0 and not generalizes:
        cls = "AT-RISK"          # constructed win, NO generalization evidence at all
    elif hits["fragile"] >= 2 and hits["constructed"] > 0:
        cls = "FRAGILE"          # constructed-headlined, generalization evidence is THIN
    elif generalizes:
        cls = "GENERALIZES"
    else:
        cls = "UNCLEAR"
    return cls, hits


def main():
    risk_only = "--risk" in sys.argv
    rows = []
    for d in sorted(glob.glob(os.path.join(PROB, "*"))):
        sol = os.path.join(d, "SOLVED.md")
        if not os.path.isfile(sol):
            continue
        text = open(sol, encoding="utf-8", errors="ignore").read()
        if "INTEGRATED_BY_STRATEGY" not in text:
            continue
        cls, hits = classify(text)
        rows.append((os.path.basename(d), cls, hits))

    tally = collections.Counter(c for _, c, _ in rows)
    print("=" * 82)
    print("GENERALIZATION AUDIT -- %d integrated organs (derived from SOLVED arguments)" % len(rows))
    print("=" * 82)
    for k in ("GENERALIZES", "FRAGILE", "AT-RISK", "NEGATIVE", "UNCLEAR"):
        print("  %-12s %d" % (k, tally.get(k, 0)))
    print()
    print("AT-RISK (constructed win, NO held-out/OOV/pre-existing-corpus evidence at all):")
    print("-" * 82)
    for slug, cls, hits in rows:
        if cls == "AT-RISK":
            print("  * %-62s %s" % (slug, "small-n" if hits["smalln"] else ""))
    print()
    print("FRAGILE (constructed-HEADLINED; generalization tail is THIN -- point-estimate / small-n / "
          "'mechanism demo' / adjudicated): the stress-test targets.")
    print("-" * 82)
    for slug, cls, hits in rows:
        if cls == "FRAGILE":
            flags = ",".join(k for k in ("smalln",) if hits[k]) or "-"
            print("  ~ %-58s fragile=%d small-n=%d" % (slug, hits["fragile"], hits["smalln"]))
    if not risk_only:
        print()
        print("UNCLEAR (ambiguous signals -- eyeball before trusting):")
        for slug, cls, hits in rows:
            if cls == "UNCLEAR":
                print("  ? " + slug)
    print()
    print("NOTE: this is a TRIAGE, NOT a verdict, and it OVER-FLAGS. Spot-checked 2026-08-30: two FRAGILE "
          "hits (the_reading_extractor, the_entity_store) were actually validated on 17k / 28k HELD-OUT items "
          "-- FALSE POSITIVES. The keyword signal cannot separate 'constructed win + STRONG held-out' from "
          "'constructed win + THIN held-out'. To confirm an organ is genuinely fragile, READ its SOLVED for the "
          "ACTUAL held-out n and real-text number. The only real test is a held-out/OOV/modern RERUN (a rigorous "
          "negative is a PASS) -- that is a PROBLEM, not a scan.")


if __name__ == "__main__":
    main()
