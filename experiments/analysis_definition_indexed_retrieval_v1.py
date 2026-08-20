"""WOULD CONNECTING THE TWO DISCONNECTED HALVES ACTUALLY PAY? A measurement, not a build.

TODAY'S FINDING: the substrate now writes good definitions (32% MEANINGFUL vs 4% for its own
distributional read-out, and 19-21% vs a 7-8% floor on an independent gold) -- **and nothing reads
them.** Enumerated, not assumed: `Substrate` has four read routes (`query`, `recall`,
`recall_cortical`, `recall_sentence`); `recall`/`recall_sentence` rank by episodic active-unit
overlap; `recall_cortical`'s index is built from `context_profiles`, never from the meaning;
`query`'s ACCEPT/CLARIFY/REFUSE keys on whether a meaning fact EXISTS, not on what it says; and
every read of a `GROUNDED_MEANING` object's content in `hdlab/` is a SELF-TEST ASSERTION.

**SO THE OBVIOUS QUESTION IS WHETHER THE DISCONNECTION COSTS ANYTHING, AND THAT IS MEASURABLE
WITHOUT BUILDING ANYTHING.** Represent each consolidated term by the CONTEXT VECTOR OF ITS OWN
DEFINITION TEXT instead of by its accumulated context profile, and score the SAME retrieval task.
Same space, same cue, same candidates, same scorer -- one variable: what the index row is made of.

ARMS
  PROFILE     `profile()[term]` -- the accumulated context vector. THIS IS THE SHIPPED ROUTE.
  DEFINIENS   the context vector of the term's own definition text. THE PROPOSED ROUTE.
  BOTH        L2-normalised sum of the two, because today's one reproducible positive result in
              this project is that COMBINING CHANNELS beats either alone (owner's own hypothesis).
  SHUFFLE_DEF ANOTHER term's definition text  <- controls for "definition-shaped text just helps"
  COOC        corpus co-occurrence count with the cue words. THE STANDING FLOOR THAT KEEPS WINNING.

⚠️ LEAK CONTROL, AND IT IS THE WHOLE EXPERIMENT IF IT IS WRONG. The definition text was itself read
out of a corpus sentence. If a cue sentence is the SAME sentence the definition came from, the
DEFINIENS arm is scoring against its own source. **Every evidence sentence for a term is excluded
from that term's cue pool, and the excluded count is PRINTED** -- a control that excludes nothing is
not a control, and this session already had a 600-of-600 leak that produced a thirty-fold fake win.

⚠️ RANKS VIA `tools/rank_with_ties.py`, MANDATORY: three tie artifacts in one day came from
`1 + sum(scores > target)`. No bare ranks here.

PRE-COMMITTED READINGS:
  DEFINIENS or BOTH beats PROFILE  -> the disconnection COSTS something measurable, and "make a read
      route consume the meaning" becomes a named build target with a number attached.
  DEFINIENS ~= PROFILE             -> the definitions carry no retrieval signal the profile lacks.
      Connecting them would be tidy and would buy nothing. **Say so.**
  DEFINIENS beats PROFILE but both lose to COOC -> the honest headline stays "still below counting",
      and the internal comparison is a mechanism note, NOT a capability claim.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.join(_REPO, "tools"))

from rank_with_ties import format_arms, rank_with_ties  # noqa: E402

from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402
from hdlab.substrate import CONTEXT_DIM, Substrate, context_vector_masked  # noqa: E402

N_READ = int(os.environ.get("DIAG_N_READ", "12000"))
SEED = int(os.environ.get("DIAG_SEED", "7"))
MIN_ITEMS = 120

sub = Substrate(seed=SEED)
total = 0
while total < N_READ:
    r = sub.read(corpus="simplewiki", n_sentences=min(800, N_READ - total), batch=50,
                 max_patches=1, consolidate_every=200)
    if r.n_sentences == 0:
        break
    total += r.n_sentences

prov = [p for p in sub.state.provenance
        if p.get("meaning_source") and "DEFINITION" in str(p["meaning_source"]).upper()]
profiles = sub.profile()

terms, definiens, source_sents = [], {}, {}
for p in prov:
    t = str(p["subject"]).strip().lower()
    obj = str(p.get("object") or "").strip()
    if not obj or t not in profiles:
        continue
    terms.append(t)
    definiens[t] = obj
    source_sents[t] = {(e.get("sentence") or "").strip() for e in (p.get("evidence") or [])}
terms = sorted(set(terms))
print("read %d | definitional terms with a profile: %d" % (total, len(terms)))


def ctx(text, mask):
    v = context_vector_masked(text, mask or "\x00none\x00", d=CONTEXT_DIM)
    if v is None:
        return None
    v = np.asarray(v, dtype=np.float64).reshape(-1)
    n = np.linalg.norm(v)
    return None if n == 0 else v / n


def unit(v):
    v = np.asarray(v, dtype=np.float64).reshape(-1)
    n = np.linalg.norm(v)
    return None if n == 0 else v / n


rng = random.Random(20260820)
shuf = terms[1:] + terms[:1]                       # every term gets a DIFFERENT term's definition

idx = {}
for i, t in enumerate(terms):
    idx[t] = {"PROFILE": unit(profiles[t]),
              "DEFINIENS": ctx(definiens[t], t),
              "SHUFFLE_DEF": ctx(definiens[shuf[i]], t)}
    a, b = idx[t]["PROFILE"], idx[t]["DEFINIENS"]
    idx[t]["BOTH"] = unit(a + b) if (a is not None and b is not None) else None

usable = [t for t in terms if all(idx[t][k] is not None for k in
                                  ("PROFILE", "DEFINIENS", "BOTH", "SHUFFLE_DEF"))]
print("terms usable in EVERY arm (so all arms score the identical candidate set): %d" % len(usable))

# ---- cue pool: held-out sentences mentioning the term, EXCLUDING its own evidence sentences ----
pool = [s for s in sub.state.sentence_pool if s and s.strip()]
by_term = collections.defaultdict(list)
uset = set(usable)
for s in pool:
    for w in set(content_lemmas(s)):
        if w in uset:
            by_term[w].append(s)

items, n_excluded, n_no_cue = [], 0, 0
for t in usable:
    cand = by_term.get(t, [])
    keep = [s for s in cand if s.strip() not in source_sents[t]]
    n_excluded += len(cand) - len(keep)
    if not keep:
        n_no_cue += 1
        continue
    items.append((rng.choice(keep), t))

print("cue sentences EXCLUDED as the definition's own source: %d  <- a control that excludes"
      " nothing is not a control" % n_excluded)
print("terms dropped for having no non-source cue left: %d" % n_no_cue)
print("scorable items: %d (candidates: %d)" % (len(items), len(usable)))
if len(items) < MIN_ITEMS:
    print("\nUNDERPOWERED: %d items < %d required. NO VERDICT." % (len(items), MIN_ITEMS))
    raise SystemExit(0)

# ---- co-occurrence floor, built from the SAME corpus the substrate read ----
cooc = collections.defaultdict(collections.Counter)
for s in pool:
    ws = content_lemmas(s)
    us = set(ws) & uset
    for t in us:
        cooc[t].update(w for w in ws if w != t)

ARMS = ("PROFILE", "DEFINIENS", "BOTH", "SHUFFLE_DEF", "COOC")
mats = {a: np.vstack([idx[t][a] for t in usable]) for a in ARMS if a != "COOC"}
pos = {t: i for i, t in enumerate(usable)}
out = {a: [] for a in ARMS}

for sent, tgt in items:
    q = ctx(sent, tgt)
    if q is None:
        continue
    cue_words = [w for w in content_lemmas(sent) if w != tgt]
    for a in ARMS:
        if a == "COOC":
            scores = np.array([sum(cooc[t].get(w, 0) for w in cue_words) for t in usable],
                              dtype=np.float64)
        else:
            scores = mats[a] @ q
        out[a].append(rank_with_ties(scores, pos[tgt]))

print("\n" + "=" * 74)
print("RANK OF THE TARGET AMONG %d CONSOLIDATED CANDIDATES (lower is better)" % len(usable))
print("=" * 74)
print(format_arms(out))
for a in ARMS:
    n_susp = sum(1 for r in out[a] if r.suspicious)
    if n_susp:
        print("  !! %-12s %d of %d items have tie-dense scores -- read the PESSIMISTIC column"
              % (a, n_susp, len(out[a])))

med = {a: float(np.median([r.midpoint for r in out[a]])) for a in ARMS}
print("\nMIDPOINT medians: " + " | ".join("%s %.1f" % (a, med[a]) for a in ARMS))
print("\nREADING:")
print("  DEFINIENS vs PROFILE : %+.1f  (negative = reading the definition RETRIEVES BETTER)"
      % (med["DEFINIENS"] - med["PROFILE"]))
print("  BOTH      vs PROFILE : %+.1f" % (med["BOTH"] - med["PROFILE"]))
print("  SHUFFLE_DEF          : %.1f  <- if this is near DEFINIENS, the gain is definition-SHAPED"
      "\n                              text, not the RIGHT definition" % med["SHUFFLE_DEF"])
print("  COOC (standing floor): %.1f  <- the number that has beaten every arm this week" % med["COOC"])
