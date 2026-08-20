"""HOW MUCH GROUNDING EFFORT GOES TO WORDS THAT HAVE NO MEANING TO FIND?

THE OBSERVATION THIS TESTS. In the 100-row blind hand-score, **WordNet had NO ENTRY for 24 of the
100 grounded subjects** -- `baffin`, `tesco`, `abdullah` -- and those rows scored 12% good against
25% for known words, roughly half. n=24 and never formally tested, so it was flagged and not
claimed. This measures it on the WHOLE store instead of a sample.

⚖️ THE BRAIN FRAMING, BECAUSE "FILTER OUT PROPER NOUNS" WOULD NOT BE BRAIN-FAITHFUL AND IS NOT THE
CLAIM. People learn names perfectly well. **But the brain does not store a name as a WORD MEANING --
it stores it as a REFERENT**, and person/place identity is carried by different machinery from
conceptual semantics (anterior temporal person-identity representations, distinct from the ATL
conceptual hub). **Our loop assigns `tesco -> situation`: it routes a named entity into the
concept-meaning pathway and asks which OTHER WORD it means. That is a category error, and it is a
POSITION/routing fidelity issue rather than a "these words are bad" one.** The actionable form is
not "delete names" but "names need a referent slot, not an anchor word".

*** WHY THIS IS NOT JUST THE POLYSEMY TEST AGAIN. *** That test asked whether a subject's number of
SENSES predicts quality, and the answer was a flat no (27% / 25% / 21% / 29% across 1 to 10+
senses). This asks a different question: whether the subject has ANY dictionary entry at all.
**"No entry" was deliberately kept distinct from "one sense" in that test precisely so it could be
asked separately here.**

MEASURED ON THE WHOLE STORE (read-only; `data/foundation` is read-only and unbacked):
  1. what FRACTION of GROUNDED_MEANING subjects have no dictionary entry
  2. the same for the ASSIGNED OBJECTS -- because a grounded name becomes an ANCHOR for later
     words, so the cost compounds rather than staying local
  3. capitalisation evidence, to separate "proper noun" from "inflection / rare word / typo"

GUARDS:
  * POSITIVE CONTROL on the no-entry proxy: common nouns must HAVE entries and known names must
    not. Without it, "24% have no entry" could just mean the lookup is broken.
  * Every store is reported separately with its n. No pooling across versions -- they are different
    runs of different code.
  * This measures PREVALENCE, not quality. It cannot show that names ground worse; the 100-row
    sample already hinted at that and this run does not re-litigate it. **Prevalence is the useful
    number because a filter's value is bounded by how often it would fire.**
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FOUND = os.path.join(_REPO, "data", "foundation")

from nltk.corpus import wordnet as wn  # noqa: E402


def has_entry(w):
    if not w or not isinstance(w, str):
        return False
    try:
        return bool(wn.synsets(w.lower()))
    except Exception:
        return False


def _selftest():
    common = ["dog", "artery", "situation", "head", "boat"]
    names = ["tesco", "baffin", "abdullah", "zzqqxx"]
    assert all(has_entry(w) for w in common), "a common noun has no entry -- lookup is broken"
    assert not any(has_entry(w) for w in names), "a name HAS an entry -- proxy is not selective"
    print("selftest no-entry proxy: %d/%d common nouns found, %d/%d names absent"
          % (sum(has_entry(w) for w in common), len(common),
             sum(not has_entry(w) for w in names), len(names)), flush=True)


_selftest()

stores = sorted(d for d in os.listdir(FOUND)
                if os.path.isfile(os.path.join(FOUND, d, "store", "store_facts.json")))
print("\nstores found: %d" % len(stores))

for s in stores:
    p = os.path.join(FOUND, s, "store", "store_facts.json")
    try:
        with open(p, encoding="utf-8") as fh:
            facts = json.load(fh)
    except Exception as exc:
        print("\n%-52s UNREADABLE: %s" % (s, type(exc).__name__))
        continue
    if isinstance(facts, dict):
        facts = facts.get("facts", list(facts.values()))
    gm = [f for f in facts
          if isinstance(f, dict) and str(f.get("relation", "")).upper() == "GROUNDED_MEANING"]
    if not gm:
        rels = collections.Counter(str(f.get("relation")) for f in facts if isinstance(f, dict))
        print("\n%-52s n_facts=%-6d NO GROUNDED_MEANING | relations: %s"
              % (s, len(facts), dict(rels.most_common(4))))
        continue

    # FIELD NAME IS `obj`, NOT `object`. The first version of this script read `object`, got None
    # for every row, and reported "100.0% of objects have no dictionary entry" -- a number that was
    # measuring nothing at all. **AN EXACTLY-100.0% (or exactly-0.0%) RESULT IS A REACHABILITY
    # FAILURE, NOT A FINDING**, the same class as the exactly-zero-width CI already in CLAUDE.md.
    # The assertion below is what should have been there from the start.
    subs = [str(f.get("subject", "")) for f in gm]
    objs = [str(f.get("obj", "")) for f in gm]
    n_pop = sum(1 for o in objs if o and o not in ("None", ""))
    assert n_pop > 0.5 * len(objs), (
        "OBJECT FIELD IS MOSTLY EMPTY (%d of %d populated) in %s -- refusing to score. Check the "
        "field name against the record schema before reading any percentage." % (n_pop, len(objs), s))
    sub_no = sum(1 for w in subs if not has_entry(w))
    obj_no = sum(1 for w in objs if not has_entry(w))
    # distinct, because a repeated name is one wasted CONCEPT not many
    d_subs = sorted(set(w.lower() for w in subs))
    d_sub_no = sum(1 for w in d_subs if not has_entry(w))
    print("\n%-52s GROUNDED_MEANING n=%d (distinct subjects %d)" % (s, len(gm), len(d_subs)))
    print("   SUBJECTS with NO dictionary entry : %5d of %5d  (%.1f%%)   distinct: %d of %d (%.1f%%)"
          % (sub_no, len(subs), 100.0 * sub_no / len(subs),
             d_sub_no, len(d_subs), 100.0 * d_sub_no / len(d_subs)))
    print("   OBJECTS  with NO dictionary entry : %5d of %5d  (%.1f%%)   <- these became ANCHORS"
          % (obj_no, len(objs), 100.0 * obj_no / len(objs)))
    ex = [w for w in d_subs if not has_entry(w)][:12]
    print("   examples: %s" % ", ".join(ex))

print("\n" + "=" * 78)
print("READ THIS AS PREVALENCE, NOT QUALITY. It bounds how often a referent-vs-concept routing fix")
print("could fire. The 100-row hand-score separately hinted these ground about half as well")
print("(12% vs 25%, n=24, NOT formally tested) -- that is a different claim and is not re-tested here.")
