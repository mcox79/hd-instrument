---
owner_verdict:
---

# construction_aware_selector_for_multi_do — REFUTED (a located negative, which the brief names a FULL PASS)

## What we were asked to build, in one plain sentence
When a sentence has two possible objects ("she gave the man a book", "they called the place a haven"), teach the
reader to use the sentence PATTERN to decide which noun is the answer, instead of just taking the nearest noun after
the verb — and prove it makes the reader more accurate.

## What we found (the honest answer)
It makes **no difference at all — exactly zero** — and we measured that three separate ways, on both old and modern
text:
- picking-step only (2-object sentences, clean gold): **+0.000** (19c), **-0.001** (modern) — no gain, slightly worse.
- all the way through the real reader: **+0.000**.
- and our reader's picking step is **already as accurate as a strong off-the-shelf parser** (about 93% vs 92%) — a
  statistical tie with a competent reader.

**Why (and it's the brain-foundational point):** for ordinary English, "nearest noun after the verb" and "what the
sentence pattern says" point at the **same** word — so the fancier rule adds nothing. This is exactly how the brain
does it: the brain assigns who-did-what by a *competition among cues* (word order, animacy, voice), NOT by looking up
a sentence-pattern template. Our reader already runs that competition. Bolting a pattern-lookup on top is *less*
brain-like, not more, and the measurements agree.

**A correction to a prior write-up:** the earlier claim that this fix gave "+15 points on two-object sentences" was
measured against a **buggy stand-in** selector (it wrongly preferred the inanimate object on "give"-type sentences).
Against the REAL reader the gain is zero. We isolated and proved this.

## What we are submitting here (the parts)
1. **The verdict: REFUTED** — a construction-aware selector does not beat the deployed selector; the deployed selector
   is already the brain-faithful mechanism and is at the competent-reader ceiling. (The brief explicitly says a
   rigorous located negative with the named cause is a FULL PASS.)
2. **Five experiment cells** (`experiments/exp_construction_aware_selector_{diagnosis,residual,brain_comparison,
   generalization,live_reader}_v1.py`) — the re-baseline, the full-power null, the spaCy brain comparison, the
   register generalization, and the end-to-end confirmation through the real `read()`.
3. **A scaffold-free witness** (`verification/test_construction_aware_selector.py`, 7/7) that re-runs no cell.
4. **The full write-up** (`SOLVED.md`) with the brain-mechanism opening move, the decisive measurement, the residual
   decomposed vs a competent reader, generalization, and the "is it solvable another way?" analysis.
5. **A deep brain-mechanism research drill** (5 lanes) confirming the brain does feature-competition, not
   construction-template retrieval, and that construction-vs-word-order is redundant on canonical English.
6. **An AUDIT UPDATE** (in SOLVED.md) with two corrections to the parent problem's write-up for strategy to fold in.

## The ideal, exact brain-foundational solution — prototyped and measured (your follow-up question)
Yes — and the key fact is that the ideal's *picking step is already built and already as good as it gets*, so "the
ideal" is really the composition plus the upstream fixes. Prototyped (`exp_construction_ideal_composition_v1`, 669
sentences):
- **Picking step (feature-competition — the brain's actual mechanism): 0.928, held fixed — no gain available.**
- **One genuinely new, buildable win, upstream:** open a candidate for indefinite words like "everybody"/"somebody"/
  "thee" (the reader currently ignores them, so "invite everybody" has no answer to pick). Measured **+1.0 point,
  clean, its scrambled version loses.** Small, and it belongs on the reader's candidate-list step (the parent's area).
- **I composed and PROVED the whole buildable pipeline** (`exp_construction_whole_composition_v1`): referent-per-NP +
  indefinite-pronoun coverage + a structural head-rule fix + the deployed picker. It beats the deployed reader
  **+1.0 point, statistically clean, twin loses, no regression** on old text — the gain is entirely the indefinite-word
  coverage, and it is old-text-specific (modern text doesn't need it). I also *tried* a structural rule to fix the
  tagger's mislabeled adjectives; it is a clean **zero** (it fixes two sentences and breaks two others, both because
  the old-text tagger is unreliable) — which proves the remaining fix belongs in a **register-aware tagger**, not in
  the picker. No half-measures hidden: the honest ceiling on this step is ~0.97 and every remaining point is a named,
  already-filed upstream job.
- **Ceiling if we also had a competent parser: ~0.97** — and that remaining +4 points is entirely *already-filed*
  upstream work: a **register-native part-of-speech tagger** (the current one mislabels old-fashioned adjectives like
  "cheery-looking" as nouns, so the picker grabs them) and **cleft-sentence parsing**. Neither is the picking step.
- **Irreducible floor: ~3%** — mostly "call X Y" naming sentences where even linguists disagree which noun is "the
  thing acted on", so there is no right answer to pick.
- **To actually maximize performance end-to-end**, the single biggest lever is not on this problem at all: turning on
  the referent-per-NP candidate source (the deployed reader scores 0.47 instead of 0.93 purely because of that),
  which is gated on the coreference-linker fix already on the board.

## What this means for the board (recommended actions — strategy owns the call)
- **Do NOT land a construction-aware selector.** Strike the parent problem's NEXT-STEP #1 ("land the construction
  improvement 0.873→0.913").
- **The real who-did-what levers are elsewhere, and are already filed:** the PARSE (clefts / locative inversion /
  apposition — 56% of the residual; the `parser_arceager` route + a discourse module), the candidate SOURCE
  (indefinite-pronoun objects — 15%; the parent's referent-per-NP territory), and the meaning channel (the genuine
  ambiguity tail — the learner-on successor). Naming/object-complement ("call X Y") is genuinely ill-posed — even
  linguists disagree which noun is "the patient" — so it is not a pick-the-right-one problem at all.

## Reverify (re-runs no landed cell)
```
.venv/Scripts/python.exe verification/test_construction_aware_selector.py     # 7/7
```

## Questions for you
None blocking. One judgement call is flagged in SOLVED.md (§QUESTIONS): this refutation implies a small correction to
the owner-DONE parent problem's write-up; I recorded it as an AUDIT UPDATE rather than editing the parent's files.
