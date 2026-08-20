"""PAIRED: for the SAME term, what did the definitional route bank, and what would the
distributional read-out have chosen from the SAME accumulated traces?

*** WHY THIS EXISTS: MY OWN RESULT AN HOUR AGO IS CONFOUNDED AND THIS IS THE CONTROL FOR IT. ***
The interleaved hand-score read PHRASE 32% MEANINGFUL vs SINGLE-WORD 0% (Fisher p=0.002). But the
two arms were not the same TERMS. The phrase arm drew `drupe, economics, tectonics, archaeologist,
electrolysis`; the word arm drew `previous, other's, useful, populous, silly, new`. **Adjectives and
function-ish words have no good one-word meaning for ANY system, so that comparison may be measuring
TERM DIFFICULTY rather than PATHWAY QUALITY.** That is the two-populations trap, and this project's
own banner says never to judge one population by the other's base rate.

THE FIX IS PAIRING, AND IT IS AVAILABLE FOR FREE. `_make_definitional_gate` SHORT-CIRCUITS: when a
definition exists it never calls `inner`, so the ledger has no record of the distributional
alternative. But line 1479 computes `raw_sum` from the item's own traces, and `canonicalize` is a
pure function of it. **So the counterfactual is exactly recomputable: same term, same traces, same
space, two read-outs.** Term difficulty then cancels by construction -- it is the same term.

*** THE PRE-COMMITTED READING, WRITTEN BEFORE THE OUTPUT IS SEEN ***
  the phrase wins on the SAME terms  -> the earlier 32-vs-0 was measuring the pathway, and the
      unpaired confound, while real, did not produce the result.
  they are comparable on the same terms -> **THE EARLIER RESULT WAS TERM DIFFICULTY AND I WILL SAY
      SO.** The headline stays as it was: this system's read-out is not better than counting; it was
      simply being asked easier questions on one arm.

NOTE ON WHAT CHANGED SINCE 2026-08-12, because it explains why this pathway is unmeasured at all:
`substrate.py:538` stores `d.definiens` (the FULL phrase). `exp_definitional_grounding_v3`, whose
50-row B3 audit sample has sat unscored since 2026-08-12, banked `d.head` -- **0 of its 50 sampled
objects are multi-word.** The v3 audit therefore measures the definitional-HEAD route, NOT this one.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.reading_grounding_loop import SENSE_MATCH_THRESH, canonicalize  # noqa: E402
from hdlab.substrate import Substrate  # noqa: E402

N_READ = int(os.environ.get("DIAG_N_READ", "12000"))

sub = Substrate(seed=7)
total = 0
while total < N_READ:
    r = sub.read(corpus="simplewiki", n_sentences=min(800, N_READ - total), batch=50,
                 max_patches=1, consolidate_every=200)
    if r.n_sentences == 0:
        break
    total += r.n_sentences

prov = sub.state.provenance
src = {}
for p in prov:
    src[str(p.get("subject", "")).strip().lower()] = p
print("read %d | provenance rows %d" % (total, len(prov)))

by_source = {}
for p in prov:
    by_source.setdefault(p.get("meaning_source") or "(distributional)", []).append(p)
for k, v in sorted(by_source.items(), key=lambda kv: -len(kv[1])):
    n_mw = sum(1 for p in v if " " in str(p.get("object") or "").strip())
    print("   meaning_source=%-28s %4d facts   multi-word objects %d (%.0f%%)"
          % (k, len(v), n_mw, 100.0 * n_mw / max(1, len(v))))

defn = [p for p in prov if p.get("meaning_source") and "DEFINITION" in str(p["meaning_source"]).upper()]
if not defn:
    defn = [p for p in prov if " " in str(p.get("object") or "").strip()]
    print("\n!! no meaning_source label found; falling back to whitespace. %d rows" % len(defn))

pairs, unreachable = [], 0
for p in defn:
    lem = str(p["subject"]).strip().lower()
    it = sub.state.library.items.get(lem)
    if it is None or not getattr(it, "traces", None):
        unreachable += 1
        continue
    raw_sum = np.sum([t.context_vec for t in it.traces], axis=0)
    alt, cos = canonicalize(lem, raw_sum, sub.state.space, thresh=SENSE_MATCH_THRESH)
    pairs.append({"term": lem, "definitional": p.get("object"), "distributional": alt,
                  "best_cos": None if cos is None else round(float(cos), 4),
                  "n_traces": len(it.traces)})

print("\nPAIRABLE: %d definitional facts, %d recomputed, %d had no surviving traces"
      % (len(defn), len(pairs), unreachable))
if unreachable:
    print("   (a consolidated item is TERMINAL -- its traces may be released, so this is expected;")
    print("    what matters is that the recomputed set is not a biased subset. n reported above.)")

# *** THE SENTINEL IS `object == term`, NOT EMPTY -- AND MY FIRST VERSION OF THIS BLOCK TESTED FOR
# *** EMPTY AND PRINTED "distributional returned nothing: 0 (0%)" WHEN THE TRUE FIGURE WAS 76%.
# `canonicalize` (reading_grounding_loop.py:770-775) documents the self-return as its NO-MATCH
# signal: "no anchor in the concept space was close enough... It is NOT a meaning", and records that
# banking it is the tautology defect measured at 65.7% of the landed foundation. `_make_grounding_
# gate` REFUSES it. So `distributional == term` means the distributional route WOULD HAVE BANKED
# NOTHING FOR THIS TERM -- it is a refusal, not an answer, and it cannot enter a quality comparison.
no_match = [q for q in pairs if str(q["distributional"]).strip().lower() == q["term"]]
same = [q for q in pairs
        if str(q["definitional"]).strip().lower() == str(q["distributional"]).strip().lower()]
print("   distributional NO-MATCH (obj == term, would be REFUSED at the gate) : %d (%.0f%%)"
      % (len(no_match), 100.0 * len(no_match) / max(1, len(pairs))))
print("      -> for these the definitional route is the ONLY source of a meaning. That is a")
print("         COVERAGE fact, not a quality one, and coverage is already a known strength.")
print("   identical under both read-outs : %d (%.0f%%)  <- carry NO information about which is better"
      % (len(same), 100.0 * len(same) / max(1, len(pairs))))

informative = [q for q in pairs if q not in same and q not in no_match and q["distributional"]]
print("   INFORMATIVE (both routes produced a real, differing answer) : %d (%.0f%%)"
      % (len(informative), 100.0 * len(informative) / max(1, len(pairs))))
print("      -> ONLY these can answer 'which read-out is better on the same term'.")
rng = random.Random(20260820)
samp = rng.sample(informative, min(25, len(informative)))
out = os.path.join(_REPO, "scratch", "paired_sheet.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(samp, fh, indent=1)

print("\n" + "=" * 96)
print("SCORE BOTH SIDES OF EACH PAIR. Same term, same traces -- term difficulty CANCELS.")
print("Rubric: MEANINGFUL / RELATED / NOISE, identical wording to the 2026-08-12 sheet.")
print("=" * 96)
for i, q in enumerate(samp, 1):
    print("%2d. %-18s A: %-46s B: %s"
          % (i, q["term"][:18], str(q["definitional"])[:46], str(q["distributional"])[:26]))
print("\n(A = definitional route, B = distributional read-out. Written A/B in the printout so the")
print(" scoring below names sides rather than pathways; the mapping is fixed and stated here.)")
print("wrote %s" % out)
