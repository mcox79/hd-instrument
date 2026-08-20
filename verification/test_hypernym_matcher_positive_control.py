"""POSITIVE CONTROL FOR THE HYPERNYM MATCHER -- standalone, no corpus read, no substrate.

WHY SEPARATELY: the phrase-floor result leans on **SHUFFLE = 0.0%** and **RANDOM_NOUNS = 0.6%**.
**A floor of zero is only evidence if the scorer can be shown to return NON-zero.** Otherwise
"no hit" is indistinguishable from "the matcher never fires", which is the precise way the mojibake
detector, the proper-noun detector and `experiment_index.py` each produced a confident wrong answer
this month.

Running it here rather than inside the scorer costs SECONDS instead of a 12,000-sentence read, and
it isolates the thing under test: the gold index and `hit()`. **The scorer's in-run ORACLE arm is
still the right belt-and-braces check; this is the one that can be run before trusting anything.**

ALSO MEASURED: what fraction of gold objects are MULTI-WORD (`city_of_westminster`). Our phrase is
split on whitespace into single tokens, so a multi-word gold object can NEVER be matched. That caps
the metric's reach -- **equally for every arm, so it does not bias the comparison, but it does mean
every rate reported is an UNDER-count and must not be read as "the definition was wrong".**
"""
import collections
import json
import os
import random

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GOLD = os.path.join(_REPO, "data", "conceptnet_gold_v1", "edges.jsonl")

isa = collections.defaultdict(set)
for line in open(GOLD, encoding="utf-8"):
    e = json.loads(line)
    if e.get("rel") in ("/r/IsA", "/r/DefinedAs"):
        isa[str(e["subj"]).lower()].add(str(e["obj"]).lower())


def hit(term, words):
    gold = isa.get(term, set())
    return any(w in gold for w in words)


fails = []

# 1. THE MATCHER FIRES on a genuine attested hypernym, including when buried in filler.
terms = [t for t in isa if isa[t] and t.isalpha()]
rng = random.Random(20260820)
sample = rng.sample(terms, 400)
fired = sum(1 for t in sample
            if hit(t, [rng.choice(sorted(isa[t]))] + ["zzz", "qqq", "wwww", "vvv", "uuu"]))
print("1. FIRES on an attested hypernym padded with filler : %d/400 (%.1f%%)"
      % (fired, 100.0 * fired / 400))
if fired < 380:
    fails.append("matcher failed to fire on its own gold in %d of 400 cases" % (400 - fired))

# 2. IT DOES NOT FIRE on random words -- otherwise the floors are meaningless in the other direction.
vocab = sorted({o for s in list(isa)[:6000] for o in isa[s] if o.isalpha()})
false_fire = sum(1 for t in sample if hit(t, rng.sample(vocab, 7)))
print("2. does NOT fire on 7 random gold-vocabulary words  : %d/400 (%.1f%%) false hits"
      % (false_fire, 100.0 * false_fire / 400))
if false_fire > 40:
    fails.append("matcher fires on random words at %.1f%% -- floors would be inflated, not zero"
                 % (100.0 * false_fire / 400))

# 3. A KNOWN PAIR, named explicitly so the test is legible rather than only statistical.
known = [("drupe", "fruit"), ("dog", "animal"), ("piraeus", "port")]
for t, o in known:
    present = o in isa.get(t, set())
    print("3. gold contains (%s IsA %s): %s%s" % (t, o, present,
                                                 "" if present else "   <- not in this gold"))

# 4. MULTI-WORD GOLD OBJECTS -- unreachable by a whitespace-split phrase, for EVERY arm.
allobj = [o for s in isa for o in isa[s]]
mw = sum(1 for o in allobj if "_" in o)
print("4. gold objects that are MULTI-WORD (unmatchable)   : %d/%d (%.1f%%)"
      % (mw, len(allobj), 100.0 * mw / len(allobj)))
print("   -> every reported hit rate is an UNDER-count by up to this much. It applies to ALL arms")
print("      equally, so the COMPARISON stands; the absolute rate is a lower bound.")

print("\nRESULT: %s" % ("PASS -- the matcher fires on real hypernyms and stays silent on random "
                        "words, so a 0.0%% floor is a real floor."
                        if not fails else "FAIL -- " + "; ".join(fails)))
raise SystemExit(1 if fails else 0)
