---
problem: context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark
status: SOLVED
bar: "On SUBORDINATE-congruent items (the true sense is NOT the most frequent), grounded-covered, held-out, floors recomputed on that population: a context-likelihood mechanism (constraint-satisfaction / settling over a pre-stored sense inventory) must recover the context-appropriate sense CI-separated over the UPPER bound of the strongest FREQUENCY floor (MFS), with the info-free twin (SHUFFLED / scrambled context sentence) LOSING CI-separated. Report CI half-width and null p95 beside every margin. AND show the SETTLING read beats (or CI-ties, honestly reported) the single-cosine read (does context's brain-faithful machinery earn its keep?)."
result: "CONTEXT overrides the frequency prior on modern data. On 44,818 held-out SUBORDINATE-congruent SemCor items (gold WordNet sense STRICTLY less frequent than the top sense; MFS=0 by construction), scored by exact match to the human-tagged SemCor sense, a STRUCTURED context-likelihood read (held-out sense prototypes over BAG + local positional collocations) recovers the rarer sense at 0.3902 vs MFS 0.0000 -- delta +0.3899 CI[+0.3725,+0.4072]; it also beats uniform chance 0.1716 (+0.2184) and both info-free twins (SHUFFLE 0.1653 +0.2244; SCRAMBLE 0.1539), null p95 0.1654; survives leave-one-DOCUMENT-out (0.3288 vs MFS CI-separated). SEPARATELY, the MISSING ORGAN was identified and built: a GOLD-BLIND two-sided conflict trigger (coherence of the best non-dominant sense minus the dominant) predicts 'the prior is wrong' at AUC 0.7916 (shuffled-context twin 0.5928) on the full 126,686-item population; conflict-gated GRADED suppression of the dominant sense (LIFG/pMTG semantic control) is NET-POSITIVE CI-separated (full accuracy +0.0014 CI[+0.0010,+0.0018]) and lifts the frequency-OVERRIDE cases CI-separated (subordinate +0.0070 CI[+0.0061,+0.0078], up to +0.033 at stronger suppression), the gain attributable to the real trigger (info-free shuffled-trigger twin LOSES)."
floor: "Strongest FREQUENCY floor = MFS = 0.0000 on subordinate items by construction (gold strictly less frequent); gate on its upper bound (rule-of-three ~3/n). Additional floors recomputed on the population: uniform 1/k = 0.1716; info-free SHUFFLE twin 0.1653 (null p95 0.1654 over 12 shuffles); SCRAMBLE 0.1539; leave-one-DOCUMENT-out MFS still 0. For the semantic-control organ the floor is REORDERED access (no control) and the shuffled-context TRIGGER twin (AUC 0.5928)."
controls: "info-free twins SHUFFLE (context from a different item) and SCRAMBLE (random words) both LOSE CI-separated; UNIFORM beaten CI-separated; leave-one-DOCUMENT-out (excludes the test item's WHOLE file) still beats MFS CI-separated -> NOT topic memorization; STRUCTURED-context ablation (probe: bag 0.34, positional 0.34, bag+positional 0.41) shows local collocation is the lever; selectional-fit dependency features add negligibly (+0.007) -> deeper structure not needed on fine senses; SETTLING is FORMALLY IDENTICAL to the argmax read (McClelland 2013) so its CI-tie is a tautology, not a finding; DIAGNOSTICITY is null even competition-gated; for SEMANTIC CONTROL: the trigger's shuffled-context twin loses (AUC 0.59 vs 0.79), the suppression's info-free shuffled-TRIGGER twin loses CI-separated, and the dominant see-saw is reported across the sweep (never crashed at the headline point, -0.0018)."
files_changed: "experiments/exp_context_override_frequency_wsd_v1.py, verification/test_context_override_frequency.py, notes/problems/context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark/DESIGN_brain_analysis.md, data/exp_context_override_frequency_wsd_v1/metrics.json"
reverify: ".venv/Scripts/python.exe verification/test_context_override_frequency.py"
---

# Context overrides the frequency prior on modern data -- and the missing organ is SEMANTIC CONTROL (conflict-gated suppression of the dominant sense), not grounding, settling, or a richer context

**Status SOLVED, and the investigation went well past the original bar.** The bar (context recovers the
rarer sense CI-separated over frequency, twin losing) is MET and strengthened. But the owner pushed the
real question -- "are we actually brain-faithful? if we were, wouldn't this work?" -- and four research
drills + a chain of can-fail probes converged on the answer: my distributional model was faithful for
what it modelled (the brain's associative access + reordered-access scoring) but was **behaviourally a
semantic-APHASIA brain -- it lacked the LIFG/pMTG semantic-control network**. Building that organ (a
gold-blind conflict-gated suppression of the dominant sense) is the brain-foundational advance, and it
works: the gold-blind trigger this project had repeatedly failed to build (prior attempts at chance AUC
0.40-0.54) reaches **AUC 0.79** via a two-sided conflict signal, and gated suppression is net-positive
CI-separated.

## What I built and measured

`experiments/exp_context_override_frequency_wsd_v1.py` (+ scaffold-free witness; deep brain-design doc
`DESIGN_brain_analysis.md`). SemCor via the vetted nltk parse; population = subordinate-congruent items
(gold count STRICTLY below the top -> MFS=0 by construction), held-out per instance and per DOCUMENT.

**1. The override (the bar) -- WIN, strengthened by a structured context.** The context-likelihood read
beats MFS 0, uniform, and both info-free twins CI-separated (0.3902 vs 0 at 44,818 items; survives
document-holdout at 0.3288). The headline improved from 0.31 to **0.39 (+28%)** when I replaced the
bag-of-words context with a STRUCTURED context (bag + local positional collocations L1/L2/R1/R2) -- the
ceiling was partly a representation fidelity gap ("one sense per collocation", Yarowsky 1993). Going
deeper to syntactic SELECTIONAL-FIT (dependency head+child, real spaCy parse) added negligibly (+0.007) --
a clean negative matching the fine-sense WSD literature (Martinez & Agirre): local collocation is the lever.

**2. The missing organ -- SEMANTIC CONTROL.** On the full 126,686-item population (dominant +
subordinate), a GOLD-BLIND two-sided conflict trigger
`conflict = max_{s != dominant} coh(context, s) - coh(context, dominant)` predicts "the frequency prior
is wrong" at **AUC 0.7916** (shuffled-context twin 0.5928). Wired as conflict-gated GRADED suppression of
the dominant sense (`score[dom] -= gamma*relu(conflict - theta)`), it is NET-POSITIVE at every operating
point (full accuracy +0.0014 CI[+0.0010,+0.0018] at the fixed theta=80th-pct / gamma=1.0 point; up to
+0.0043 at stronger settings), lifts the frequency-OVERRIDE (subordinate) cases CI-separated (+0.0070 up
to +0.033, a +24% relative gain there), at a small dominant cost (the Gernsbacher suppression see-saw),
and the gain is attributable to the REAL trigger (the info-free shuffled-TRIGGER twin loses CI-separated).
This is the first working gold-blind control trigger on this substrate.

## The four negatives, adjudicated (owner: "these should work if we're brain-foundational")

Each was tested as a genuine-brain-fact vs my-fidelity-gap, not assumed:
- **~39% override ceiling -- PARTLY my gap (fixed), mostly a genuine floor.** Structured local context
  lifted it 0.31->0.39; but 2020 transformer SOTA gets only 52.6% on the analogous least-frequent-sense
  subtask (Blevins & Zettlemoyer 2020), so my 0.39 with no pretrained backbone is within ~13 points --
  the residual is honest task difficulty plus the (now-addressed) control gap.
- **Settling doesn't beat the feed-forward read -- WITHDRAWN as a finding; it is a TAUTOLOGY.**
  McClelland (2013) proves recurrent settling and `argmax[log P(sense) + coherence]` are the SAME
  computation, so my feed-forward read IS the settling fixed point; the CI-tie was mathematically
  guaranteed. (Also, genuine competitive settling needs well-separated basins, which the substrate's
  95.65%-frequency-correlated errors show it lacks -- Mirman 2010.) The real lever was never the settling
  dynamics; it was control.
- **Diagnosticity is null -- genuine null for the tested forms.** Uniform variance-weighting hurts
  (-0.03), and it stays negative even competition-GATED on the high-competition subset (probe): the hard
  items are hard because the CONTEXT is weak, not because good words are diluted.
- **Grounding does NOT fix selection -- REFUTED on this project's own disk.** `reader_meaning_channel`
  tested the richest grounded hub (sensory+motor+affect) on a real selection task and it did not beat the
  frequency prior. The ceiling is not a grounding gap; the two-meaning-systems audit holds (grounding ->
  similarity, not selection).

## KEY REALIZATIONS (the enabling moves)

- **The owner's "wouldn't this work if it were brain-faithful?" was the key reframe.** It forced me to
  ask what my model IS -- an associative/reordered-access reader with NO semantic-control network -- i.e.
  a lesioned (semantic-aphasia) brain. The gap wasn't the representation; it was a missing organ.
- **A TWO-SIDED conflict signal is what makes the gold-blind trigger work.** The project's prior triggers
  (peakedness/entropy of the channel) were frequency-confounded and scored at chance. `coh(best
  non-dominant) - coh(dominant)` directly asks "does another sense fit the context better than the
  habitual one?" -- AUC 0.79, twin 0.59. Same data, right question.
- **Move to the population where frequency is GUARANTEED wrong.** Defining subordinate as gold count
  strictly below the top makes MFS=0 by construction, so any context signal is unambiguously an override
  and the info-free twin (not MFS) becomes the real bar.
- **Structured beats dense.** A bag-of-words discards local collocation the brain uses; adding positional
  collocation (not more density -- dense PPMI+SVD LOWERED accuracy) is the faithful fix.
- **Read the disk before theorising.** Three on-disk REFUTED cells (`reader_meaning_channel`,
  `the_prior_swamps_the_channel`, `store_survives_a_partial_cue`) already contained the answer -- grounding
  refuted, suppression oracle-verified, trigger unsolved -- and were found only by the deep drill reading
  the substrate.

## AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

1. **The meaning-in-context OVERRIDE is DEMONSTRATED on modern data** (was a data-limited open cell):
   context recovers the rarer sense CI-separated over frequency (0.39 vs 0), twins losing, surviving
   document holdout. Mechanism = reordered access (Bayesian log-prior + STRUCTURED context log-likelihood
   over held-out prototypes). Local collocation, not grounding or dense embeddings, is the context lever.
2. **NEW ORGAN identified + prototyped: LIFG/pMTG SEMANTIC CONTROL (conflict-gated suppression of the
   dominant sense; Noonan 2010).** The substrate lacked it entirely -- behaviourally a semantic-aphasia
   reader. A GOLD-BLIND two-sided conflict trigger works (AUC 0.79 vs twin 0.59), and gated suppression is
   net-positive CI-separated. This is the first working gold-blind control trigger on this substrate; the
   `the_prior_swamps_the_channel` "no unsupervised trigger" negative is now PARTIALLY overturned (its
   proxies were frequency-confounded; a two-sided signal works). The net gain is trigger-quality-limited;
   improving the trigger beyond 0.79 is the forward lever.
3. **The "settling vs argmax" question is CLOSED as a tautology (McClelland 2013):** they are the same
   computation; do not spend build budget testing settling dynamics against the algebraic read on this
   substrate. Genuine settling would need well-separated basins the store lacks.
4. **Grounding for selection is RE-CONFIRMED negative** (reconciles `reader_meaning_channel`): but the
   missing piece is NOT (only) control -- see #5. The subordinate-bias residual is a LATENCY/margin cost
   (Binder & Rayner 1998), not an accuracy penalty; the prior helps DOMINANT selection (0.98).
5. **DEEPEST FINDING (owner-driven, corrects my premature "converged"): the reader's MEANING
   representation is not brain-faithful -- it is purely ASSOCIATIVE (co-occurrence), and the missing brain
   system is the ATL CONCEPTUAL/DEFINITIONAL meaning hub.** On the HUMAN-graded meaning-identity task (WiC)
   the co-occurrence reader is at CHANCE (0.51); swapping the SENSE representation to a DEFINITIONAL one
   (WordNet gloss + hypernym closure -- a glass-box static asset), same algorithm, lifts WiC to balanced
   accuracy 0.78 CI[0.75,0.82] with a proper info-free twin (random-unrelated glosses) at CHANCE 0.51 ->
   GENUINE MEANING (not artifact; a first, naive same-permutation twin was a non-control and was caught).
   The two systems are COMPLEMENTARY: co-occurrence (LIFG associative) wins fine SemCor synset selection
   (0.41 vs gloss 0.22); definitional (ATL conceptual) wins meaning-identity (WiC). This is the project's
   two-meaning-systems architecture; the reader had only the associative half. The frequency-override
   result stands, but the WiC-at-chance was a genuine FIDELITY GAP (missing the ATL conceptual-meaning
   system), NOT a ceiling.

## PROPOSED hdlab CHANGE (strategy lands it, board Q111 -- I did NOT write hdlab/)

1. **Wire a per-sense REORDERED-ACCESS read with a STRUCTURED context** (frequency prior + additive
   log-likelihood = cosine of a BAG+POSITIONAL-COLLOCATION context to a held-out sense prototype),
   default-off; sweep lambda:beta.
2. **Wire the SEMANTIC-CONTROL organ:** a gold-blind two-sided conflict detector (`coh(best non-dominant)
   - coh(dominant)`) gating GRADED suppression of the dominant sense. Fixed, conservative theta/gamma
   (suppress the top-conflict items); it is net-positive CI-separated and its info-free twin loses. This
   is the substrate's missing semantic-control network.
3. **Do NOT wire settling** (formally identical to the read), **grounded read-out for selection**
   (refuted), or **diagnosticity word-weighting** (null).
4. **The forward lever is a BETTER TRIGGER** (beyond AUC 0.79) -- likely needs a small learned/calibrated
   gate on a dev split (the `the_prior_swamps_the_channel` note that control may need learning, not an
   unfitted heuristic, is consistent -- but the two-sided signal already gets most of the way gold-blind).
5. **Measure on the LIVE reading/coref task before any capability claim** (the SemCor ceiling is a
   naturalistic-context number).

## WHAT I DID NOT ESTABLISH (withdraw first if wrong)

- **All numbers are on the SemCor instrument** (human-tagged senses; exact synset match, NOT WordNet
  taxonomic distance). No number crosses to live reading. The 0.39 ceiling is a naturalistic-context number.
- **The semantic-control net gain is modest** (full +0.0014 to +0.0043) because 63% of the population is
  dominant (where the override is irrelevant) and it is trigger-quality-limited at AUC 0.79. The strong
  effect is on the frequency-override cases (+0.007 to +0.033, +24% relative). Do NOT quote the net gain as
  a large WSD improvement; quote the TRIGGER (AUC 0.79 gold-blind) and the override-case gain.
- **WiC near-majority with the CO-OCCURRENCE reader was a FIDELITY GAP, not a ceiling** (corrected): the
  co-occurrence representation is at chance on meaning-identity; a DEFINITIONAL/conceptual representation
  reaches balanced accuracy 0.78 (info-free twin at chance). CAVEAT: WiC was partly built from WordNet, so
  the definitional gloss method has some inside-track on WiC's sense boundaries -- the absolute 0.78 is
  inflated by that provenance; the controlled claim is chance->0.78 with the info-free twin at chance, i.e.
  the conceptual representation captures genuine meaning the co-occurrence one cannot. Do NOT quote 0.78 as
  a domain-general WiC number.
- **The suppression theta/gamma are swept hyperparameters** (reported as a transparent sweep; the headline
  point is fixed, not tuned to gold). A fully clean version tunes them on a dev split.

## TLDR

Words have a common meaning and rarer ones; the brain leans on the common one but lets the sentence
override it to pick the rarer meaning ("the bank was muddy after the flood"). On modern sense-labelled
text -- with the frequency habit guaranteed to point the WRONG way -- the sentence context picks the
correct rarer meaning ~39% of the time vs 0% for the habit and ~16% for scrambled context, and it survives
hiding the whole source document (real sentence understanding, not topic memorising). The owner then asked
the deep question: if we were truly copying the brain, wouldn't it work better? It turns out my reader was
like a brain with a specific injury -- it had the "look up meanings" part but not the CONTROL part that
actively SUPPRESSES the habitual meaning when the sentence disagrees. I built that missing part: a
detector that, without ever seeing the answer, spots when "some other meaning fits this sentence better
than the usual one" -- and it works (it's right about 79% of the time, vs a scrambled-sentence version at
59%). Using it to push down the habitual meaning improves the hard "rarer-meaning" cases (by up to ~a
quarter) at a tiny cost on the easy cases -- the same trade-off the brain makes. Along the way I retired
two wrong turns: adding "grounded sensory meaning" does NOT help here (the brain uses control, not more
meaning), and the fancy "let meanings settle by competing" machinery is mathematically the SAME as the
simple calculation we already do, so it was never going to add anything. The one real missing piece was
CONTROL, and now it's built.

## QUESTIONS

None blocking. Two judgement calls: (1) I filed SOLVED -- the bar (override beats frequency, twin losing)
is met and strengthened; the semantic-control organ is an additional, deeper brain-foundational advance
answering the owner's fidelity challenge. (2) The semantic-control net-gain magnitude is modest and
trigger-quality-limited; if you want a larger effect before wiring, the forward step is a better (possibly
lightly-learned) conflict trigger -- say if you'd like that built before integration.

## NEXT STEPS

0. **DEEPEST, HIGHEST-PRIORITY (owner-driven): give the reader a brain-faithful MEANING representation.**
   It currently has only the ASSOCIATIVE (co-occurrence) system and is at CHANCE on human-graded
   meaning-identity (WiC). Add the ATL CONCEPTUAL/DEFINITIONAL meaning hub (a glass-box static asset --
   WordNet/dictionary gloss + hypernym/relational closure, via the project's `definitional_extraction`) as
   a SECOND, DEMAND-ROUTED channel (conceptual for meaning-identity, associative for fine online selection).
   DO NOT FUSE the two into one score: Stage-1 fusion was RUN and HARD-FAILED (gated combination == random
   gate, no gain over the associative specialist -- DESIGN sec 13); the CSC-faithful model is task/demand
   ROUTING. And the COMPOSITIONAL, ROLE-BOUND relational-consistency read (the last computational-KIND lever)
   was BUILT RIGHT (real parse + a genuine role-conditioned selectional-preference profile, NOT bag features)
   and ALSO HARD-FAILED its can-fail test (probe 18: role-fit does not beat the bag CI-sep, and the
   role-permutation info-free twin does not lose -> role structure carries no separable sense signal on this
   population; sense is resolved by topical/collocational context, which the bag captures). So the
   SENSE-SELECTION story is CONVERGED: the associative organ + the demand-routed ATL conceptual channel are
   the wins; neither fusion nor compositional role-binding earns its keep as a WSD lever. (Full
   comprehension / situation-model is a separate Phase-1 program with its own justification, not a
   sense-selection fix.)
1. Wire the per-sense reordered-access read (structured context) + the semantic-control conflict-gated
   suppression organ (both default-off). Do NOT wire settling / grounding-for-selection / diagnosticity.
2. Improve the TRIGGER beyond AUC 0.79 -- but NOT by a fitted combiner of the current signals (drill 5 +
   probe 8: the symmetric ACC entropy/energy and prediction-error KL are worse AND not context-specific;
   unfitted/fitted combining hurts). The lever is a genuinely NEW orthogonal DIRECTIONAL signal (e.g.
   runner-up-identity stability across context bootstrap resamples). NOTE: bounded/normalization
   suppression (probe 9) and generative/predictive coherence (probe 10) were tested and are NEGATIVE
   (see-saw is trigger-limited not shape-limited; cosine ~= generative here) -- the mechanism is at its
   sensible ceiling; the residual is task difficulty (SOTA 52.6% on this subtask) + trigger quality.
3. Measure on the LIVE reading/coref task (is real local context diagnostic enough to override frequency?).
4. Optional: graded meaning-similarity rescoring (WordNet path / gloss-embedding) instead of exact-synset
   match -- changes what "39%" means and gives a more sensitive readout (drill-4 Q4).

---

INTEGRATED_BY_STRATEGY: 2026-08-27 -- EXCELLENT / SOLVED (owner-DONE). Full SOLVED re-read FRESH (standing rule).
Re-verified scaffold-free FIRST-HAND (test_context_override_frequency.py PASS: CONTEXT 0.46 vs MFS 0 and UNIFORM 0.25
CI-sep; SHUFFLE/SCRAMBLE twins lose; leave-one-doc-out survives; settling==argmax tie 0.0012 (tautology); trigger AUC
0.81 vs twin 0.58; SUPPRESS subordinate +0.0093 CI-sep, info-free trigger twin loses). VINDICATES the SemCor acquisition:
CONTEXT overrides the frequency prior on MODERN data (the McGuffey data-limit the meaning_win result hypothesized) --
recovers the rarer sense at 0.39-0.46 vs MFS 0, chance 0.17-0.25, twins losing, not topic memorization. THE MISSING ORGAN
BUILT = SEMANTIC CONTROL (LIFG/pMTG): a gold-blind two-sided conflict trigger (AUC 0.79) gating GRADED suppression of the
dominant sense, net-positive CI-sep, lifting override cases +0.007-0.033 -- 'the reader had look-up but no CONTROL'.
RETIRED 4 wrong turns w/ strong controls (grounded-for-selection refuted; settling = argmax tautology; diagnosticity
null; fusion HARD-FAILED -> demand ROUTING not fusion; role-binding HARD-FAILED -> sense is topical/collocational).
HONEST: SemCor-instrument numbers; net semantic-control gain modest/trigger-limited (quote the trigger AUC + override
gain). hdlab landing EARNED -> QUEUED proven-ready (default-off reordered-access read + the semantic-control
conflict-trigger+suppression organ; NO settling/grounding/diagnosticity). AUDIT UPDATE folded (§2b + meaning re-frame).
SUCCESSOR packaged = the #0 next step: the ATL CONCEPTUAL/DEFINITIONAL meaning channel (reader is at CHANCE on human
meaning-identity -- only has the associative system; demand-ROUTED, NOT fused). Review EXCELLENT + SOLVER REVIEW in
PROBLEM.md; priority cleared. Committed. *(batch 3 of 3 -- the final; next-steps recommendation follows.)*
