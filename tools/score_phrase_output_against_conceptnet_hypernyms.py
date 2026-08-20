"""AN ADMISSIBLE, MACHINE-COMPUTED FLOOR FOR *PHRASE* OUTPUT -- FEASIBILITY.

THE PROBLEM. Every floor this project owns (COOC, COOC2, FREQ, TOP_COOCCURRENT, SCRAMBLE) is
WORD-TO-WORD, and the independent gold is word-to-word edges. **So the good half of the substrate's
output has no admissible floor and cannot be scored by machine at all** -- which is why the only
evidence for it is n=25 hand-scored by an interested party (me).

THE WAY THROUGH. ConceptNet cannot match a phrase EXACTLY, but it holds **154,974 `/r/IsA`** and
**2,173 `/r/DefinedAs`** edges. So score a HIT when our phrase for term T **CONTAINS a word W with
an attested (T IsA W)**. Machine-computable, independent gold, works on phrases.

*** AND THE METRIC HAS AN OBVIOUS WAY TO FAKE A WIN, WHICH IS WHY THE FLOORS BELOW ARE
*** LENGTH-MATCHED. A LONGER PHRASE MECHANICALLY GETS MORE CHANCES TO CONTAIN A HYPERNYM.
Our definitional phrases are long by construction; a single-word arm gets ONE chance. Scoring those
against each other measures LENGTH, not meaning -- **the same defect as this week's sparse-DG
artifact, wearing different clothes.** The project's own rule applies verbatim: *build the
information-free version of your winning arm and check that it LOSES.*

ARMS (every floor emits a phrase of THE SAME LENGTH as ours for that term):
  OURS            the definitional phrase the substrate banked
  SHUFFLE         another term's phrase -- destroys the pairing, keeps length + phrasing
  RANDOM_NOUNS    K random corpus content words, K = our length  <- THE INFORMATION-FREE VERSION
  CO_SENTENCE     K random content words drawn FROM A SENTENCE CONTAINING T  <- STRONGEST FLOOR:
                  controls for length AND topical co-occurrence, so beating it isolates the
                  DEFINITIONAL pattern rather than mere proximity
  CONSTANT        the most common phrase in the output, applied to EVERY term (prototype floor;
                  long generic phrases contain 'type', 'person', 'part' and can score by accident)

PRE-COMMITTED READINGS:
  OURS clears CO_SENTENCE's upper bound -> a real, machine-checkable floor for phrase output exists
      and the phrase result can be hardened without a hand-score. That is the top item unblocked.
  RANDOM_NOUNS or CONSTANT scores near OURS -> **the metric measures LENGTH, is inadmissible, and
      I say so and do not use it.** A floor that cannot separate noise from signal is not a floor.
  every arm near zero -> the gold does not cover this vocabulary; report coverage, not a verdict.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402
from hdlab.substrate import Substrate  # noqa: E402

N_READ = int(os.environ.get("DIAG_N_READ", "12000"))
GOLD = os.path.join(_REPO, "data", "conceptnet_gold_v1", "edges.jsonl")

isa = collections.defaultdict(set)
for line in open(GOLD, encoding="utf-8"):
    e = json.loads(line)
    if e.get("rel") in ("/r/IsA", "/r/DefinedAs"):
        isa[str(e["subj"]).lower()].add(str(e["obj"]).lower())
print("gold: %d subjects carry an IsA/DefinedAs edge" % len(isa))

SEED = int(os.environ.get("DIAG_SEED", "7"))
sub = Substrate(seed=SEED)
total = 0
while total < N_READ:
    r = sub.read(corpus="simplewiki", n_sentences=min(800, N_READ - total), batch=50,
                 max_patches=1, consolidate_every=200)
    if r.n_sentences == 0:
        break
    total += r.n_sentences
print("SEED %d" % SEED)

prov = [p for p in sub.state.provenance
        if p.get("meaning_source") and "DEFINITION" in str(p["meaning_source"]).upper()]
pool = sorted({w for s in sub.state.sentence_pool for w in content_lemmas(s)})
print("read %d | definitional facts %d | corpus content-word pool %d" % (total, len(prov), len(pool)))

items = []
for p in prov:
    t = str(p["subject"]).strip().lower()
    words = [w for w in str(p.get("object") or "").lower().split() if w.isalpha()]
    if not words:
        continue
    sents = [e.get("sentence") or "" for e in (p.get("evidence") or [])]
    items.append({"term": t, "words": words, "sents": [s for s in sents if s]})

covered = [it for it in items if it["term"] in isa]
print("items with a phrase: %d | of those, in the gold: %d (%.0f%% COVERAGE -- everything below is"
      % (len(items), len(covered), 100.0 * len(covered) / max(1, len(items))))
print("   computed on the COVERED subset only; an uncovered term cannot hit and would dilute every"
      "\n   arm equally, but reporting it as a score would understate all of them.)")

if not covered:
    print("\nNO COVERAGE -- the gold does not reach this vocabulary. No verdict.")
    raise SystemExit(0)

rng = random.Random(20260820)
all_phrases = [it["words"] for it in covered]
constant = collections.Counter(" ".join(it["words"]) for it in covered).most_common(1)[0][0].split()


def hit(term, words):
    gold = isa.get(term, set())
    return any(w in gold for w in words)


def arm_words(it, arm, idx):
    k = len(it["words"])
    if arm == "OURS":
        return it["words"]
    if arm == "SHUFFLE":
        return all_phrases[(idx + 1 + rng.randrange(len(all_phrases) - 1)) % len(all_phrases)]
    if arm == "RANDOM_NOUNS":
        return rng.sample(pool, min(k, len(pool)))
    if arm == "CONSTANT":
        return constant
    if arm == "CO_SENTENCE":
        bag = [w for s in it["sents"] for w in content_lemmas(s) if w != it["term"]]
        if not bag:
            return []
        return [rng.choice(bag) for _ in range(k)]
    if arm == "ORACLE":
        # a genuine attested hypernym, padded to OUR length so it is not advantaged by being short
        gold = sorted(isa.get(it["term"], set()))
        if not gold:
            return []
        return [rng.choice(gold)] + rng.sample(pool, max(0, k - 1))
    raise ValueError(arm)


# *** POSITIVE CONTROL. A SCORER THAT HAS NEVER BEEN SHOWN TO RETURN A HIT CANNOT SUPPORT A LOW
# *** FLOOR NUMBER: SHUFFLE = 0.0% and RANDOM_NOUNS = 0.6% are only meaningful if the matcher
# demonstrably CAN fire. ORACLE emits a genuine attested hypernym of the term, padded to the same
# length with random words, and MUST score ~100%. If it does not, every other number here is void.
# (Standing rule: verify with a positive control, never only an absence check -- the mojibake
# repair, the proper-noun detector and `experiment_index.py` all failed exactly this way.)
ARMS = ("OURS", "CO_SENTENCE", "SHUFFLE", "RANDOM_NOUNS", "CONSTANT", "ORACLE")
res = {}
for arm in ARMS:
    hits, lens, scored = 0, [], 0
    for i, it in enumerate(covered):
        w = arm_words(it, arm, i)
        if not w:
            continue
        scored += 1
        lens.append(len(w))
        hits += hit(it["term"], w)
    res[arm] = (hits, scored, sum(lens) / max(1, len(lens)))


def wilson(k, n):
    z = 1.959964
    if n == 0:
        return (0.0, 0.0)
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


print("\n" + "=" * 88)
print("HIT = the emitted phrase CONTAINS a ConceptNet-attested hypernym of the term")
print("=" * 88)
print("%-14s %6s %7s %9s   %-22s %s" % ("arm", "hits", "n", "rate", "95% CI", "mean words"))
for arm in ARMS:
    h, n, ml = res[arm]
    lo, hi = wilson(h, n)
    print("%-14s %6d %7d %8.1f%%   [%5.1f%%, %5.1f%%]        %.1f"
          % (arm, h, n, 100.0 * h / max(1, n), 100 * lo, 100 * hi, ml))

ours_lo = wilson(*res["OURS"][:2])[0]
print("\nGATE: OURS's LOWER bound vs each floor's UPPER bound (gate on the floor's upper bound,")
print("      never its point value -- standing measurement rule).")
verdict = True
FLOORS = [a for a in ARMS if a not in ("OURS", "ORACLE")]  # ORACLE is a CEILING, not a floor
for arm in FLOORS:
    f_hi = wilson(*res[arm][:2])[1]
    ok = ours_lo > f_hi
    verdict &= ok
    print("   OURS lo %.1f%%  vs  %-13s hi %.1f%%   -> %s"
          % (100 * ours_lo, arm, 100 * f_hi, "CLEARS" if ok else "**DOES NOT CLEAR**"))

o_h, o_n, _ = res["ORACLE"]
o_rate = 100.0 * o_h / max(1, o_n)
print("\nPOSITIVE CONTROL: ORACLE (a genuine attested hypernym, padded to our length) = %.1f%%"
      % o_rate)
if o_rate < 95.0:
    print("   *** THE MATCHER IS BROKEN. It cannot reliably find a hypernym that IS present, so")
    print("   *** every floor number above is void -- a 0.0%% floor may just be a scorer that")
    print("   *** never fires. DO NOT USE THIS METRIC UNTIL THIS READS ~100%.")
    verdict = False
else:
    print("   -> the matcher demonstrably FIRES, so SHUFFLE=0.0%% and RANDOM_NOUNS=0.6%% are real")
    print("      floors and not a scorer that is simply silent.")

print("\nLENGTH CHECK (the way this metric fakes a win):")
print("   OURS mean words %.1f | RANDOM_NOUNS %.1f | CO_SENTENCE %.1f -- matched by construction."
      % (res["OURS"][2], res["RANDOM_NOUNS"][2], res["CO_SENTENCE"][2]))
print("   If RANDOM_NOUNS is near OURS, the metric is counting WORDS, not meaning.")
print("\nVERDICT: %s" % ("AN ADMISSIBLE PHRASE FLOOR EXISTS -- the top item is unblocked."
                         if verdict else
                         "NOT ADMISSIBLE as it stands -- at least one floor is not cleared. "
                         "Report it, do not use the metric."))
