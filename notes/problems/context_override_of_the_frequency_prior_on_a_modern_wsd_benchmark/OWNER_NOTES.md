---
owner_verdict: DONE
---

SUBMISSION -- SOLVER RESULT: context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark
STATUS: SOLVED (bar met, and the deeper fidelity question answered) | ledger malformed/incomplete: 0
REVERIFY:
  .venv/Scripts/python.exe verification/test_context_override_frequency.py            (override + semantic-control organ; PASS)
  .venv/Scripts/python.exe verification/test_definitional_meaning_representation.py    (the ATL conceptual-meaning finding; PASS)
NO hdlab/ MODIFIED (proposed diffs below; strategy lands, board Q111). Integrate ONLY on owner_verdict: DONE.

THE ANSWER IN ONE LINE
Context DOES override the frequency habit and recover a word's RARER, context-appropriate meaning on modern
data (SemCor). Along the way, owner-driven fidelity drills found the deeper truth: the reader had only the
brain's ASSOCIATIVE meaning system (co-occurrence) and was MISSING the semantic-control network AND the ATL
conceptual-meaning hub -- and building those is the real advance. Every remaining sense-selection lever was
tested with a can-fail control and closed; the story is genuinely CONVERGED.

THE BAR (PROBLEM.md sec 7, verbatim): on SUBORDINATE-congruent items (true sense NOT the most frequent),
held-out, floors recomputed on that population: a context-likelihood mechanism must recover the
context-appropriate sense CI-separated over the MFS upper bound, with the info-free twin LOSING; report CI
half-width + null p95; AND show settling beats (or CI-ties, honestly) the single read.

RESULT 1 -- THE OVERRIDE (the bar): WIN, strengthened by a brain-faithful STRUCTURED context.
  44,818 held-out subordinate-congruent SemCor items (gold sense strictly less frequent -> MFS = 0 by
  construction), graded by exact match to the human-tagged SemCor sense:
    MFS (frequency floor)               0.0000
    UNIFORM (1/k chance)                0.1716
    SHUFFLE twin / SCRAMBLE twin        0.1653 / 0.1539   (null p95 0.1654)
    CONTEXT-likelihood (STRUCTURED)     0.3902   vs MFS +0.3899 CI[+0.3725,+0.4072]; vs UNIFORM +0.2184;
                                                 vs SHUFFLE +0.2244 -- all CI-separated
    leave-one-DOCUMENT-out              0.3288   vs MFS CI-separated -> genuine context, NOT topic memorization
  Structured local context (bag + positional collocations L1/L2/R1/R2) lifted this 0.31 -> 0.39 (+28%); the
  bag-of-words was a fidelity gap (Yarowsky "one sense per collocation"). Deeper syntactic selectional-fit
  features added ~0. Settling CI-TIES the feed-forward read -- and per McClelland 2013 settling == the
  argmax read, so that "test" is a tautology (withdrawn as a finding). The subordinate-bias residual is a
  LATENCY/margin cost (Binder & Rayner 1998), not an accuracy penalty; the prior HELPS dominant items (0.98).

RESULT 2 -- THE MISSING ORGAN #1: SEMANTIC CONTROL (LIFG/pMTG; Noonan 2010).
  The reader was behaviourally a semantic-aphasia brain -- no control network. Built it: a GOLD-BLIND
  two-sided conflict trigger [coh(best non-dominant sense) - coh(dominant)] predicts "the prior is wrong" at
  AUC 0.7916 (shuffled-context twin 0.5928) on the full 126,686-item population -- the FIRST working
  gold-blind trigger on this substrate (prior attempts were at chance 0.40-0.54; the enabling move is a
  TWO-SIDED / directional signal, not the frequency-confounded peakedness/entropy). Conflict-gated GRADED
  suppression of the dominant sense is net-positive CI-separated and lifts the override cases (subordinate
  +0.007 up to +0.033), gain attributable to the real trigger (info-free shuffled-trigger twin loses),
  small dominant see-saw cost (Gernsbacher trade-off). Net gain is trigger-quality-limited.

RESULT 3 -- THE MISSING ORGAN #2 (owner-driven, corrects a premature "converged"): the reader's MEANING
representation is not brain-faithful. It is purely ASSOCIATIVE (co-occurrence = LIFG system) and is at
CHANCE (0.51) on the HUMAN-graded meaning-identity task (WiC). Swapping the SENSE representation to a
DEFINITIONAL/CONCEPTUAL one (WordNet gloss + hypernym closure = the ATL hub analog, a glass-box static
asset), SAME argmax-cosine algorithm, reaches WiC balanced accuracy 0.78 CI[0.75,0.82], with a PROPER
info-free twin (random UNRELATED glosses) at CHANCE 0.51 -> GENUINE MEANING, CI-separated.
  DID-IT-RIGHT CATCH (report this -- it is the point): my FIRST info-free twin (permute glosses with the
  SAME permutation for both sentences) was a NON-control -- same-slot agreement is invariant to a shared
  relabel, so it read 0.78 too and would have let me claim a false win. The PROPER random-gloss twin (at
  chance) is what makes the claim trustworthy. CAVEAT: WiC was partly built from WordNet, so the absolute
  0.78 is inflated by shared sense provenance -- the controlled claim is chance -> 0.78 with the twin at
  chance; DO NOT quote 0.78 as a domain-general WiC number.
  The two systems are COMPLEMENTARY + task-dependent: co-occurrence (LIFG associative) wins fine SemCor
  synset selection (0.41 vs gloss 0.22); definitional (ATL conceptual) wins meaning-identity (WiC). This IS
  the project's two-meaning-systems architecture; the reader had only the associative half.

CONVERGENCE -- every remaining sense-selection lever BUILT + tested with a can-fail control + info-free twin,
ALL closed (do NOT re-run these):
  - settling: McClelland 2013 tautology (== the argmax read) -> not a finding.
  - grounding-for-selection: refuted on this project's own disk (reader_meaning_channel).
  - diagnosticity / controlled-retrieval word-weighting: null even competition-gated.
  - bounded/normalization suppression: HARD-FAIL its can-fail test (see-saw is trigger-limited, not shape-limited).
  - generative/predictive coherence (N400 belief-update): CI-tie (cosine adequate).
  - conflict trigger in conceptual space: negative (0.54 vs 0.80; combining hurts).
  - FUSING the two systems (Stage 1): HARD-FAIL -- gated combination == a RANDOM gate; no gain over the
    associative specialist -> do NOT fuse; the CSC-faithful model is task/demand ROUTING.
  - COMPOSITIONAL role-bound relational-consistency read (Stage 3, the last computational-KIND lever), BUILT
    RIGHT (real spaCy parse + a genuine role-conditioned selectional-preference profile, NOT bag features,
    held out per document): HARD-FAIL -- role-fit does not beat the bag CI-sep, and the mandatory
    role-permutation info-free twin does NOT lose (a WRONG role scores as well as the RIGHT one). Specific
    reason: on this population sense is resolved by TOPICAL/COLLOCATIONAL context (the bag captures it), not
    by who-did-what-to-whom.

AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md):
  1. The meaning-in-context OVERRIDE is DEMONSTRATED on modern data (was a data-limited open cell): mechanism
     = reordered access (Bayesian log-prior + STRUCTURED context log-likelihood over held-out prototypes);
     local collocation, not grounding or dense embeddings, is the context lever.
  2. NEW ORGAN prototyped: LIFG/pMTG SEMANTIC CONTROL (conflict-gated suppression; Noonan 2010). First working
     gold-blind trigger (AUC 0.79) via a two-sided/directional conflict signal; the prior "no unsupervised
     trigger" negative (the_prior_swamps_the_channel) is PARTIALLY overturned (its proxies were
     frequency-confounded). Net gain is trigger-quality-limited.
  3. NEW ORGAN identified: the reader lacks the ATL CONCEPTUAL/DEFINITIONAL meaning system -- it is at CHANCE
     on human-graded meaning-identity; a definitional representation captures it (controlled). This is the
     two-meaning-systems architecture; the missing piece is CONCEPTUAL meaning, NOT sensorimotor grounding
     (reconciles the grounding refutation).
  4. "settling vs argmax" is CLOSED as a tautology (McClelland 2013). Fusion of the two systems and
     compositional role-binding are TESTED-NEGATIVE as WSD levers (do not re-run).
  5. The subordinate-bias residual is a LATENCY/margin cost, not an accuracy penalty.

PROPOSED hdlab CHANGE (strategy lands it; I did NOT write hdlab/):
  1. Wire the per-sense REORDERED-ACCESS read (frequency prior + additive STRUCTURED-context log-likelihood =
     cosine of a bag+positional-collocation context to a held-out sense prototype), default-off; sweep lambda:beta.
  2. Wire the SEMANTIC-CONTROL organ: gold-blind two-sided conflict trigger gating GRADED suppression of the
     dominant sense. Fixed conservative theta/gamma; net-positive; info-free twin loses.
  3. Wire the ATL CONCEPTUAL/DEFINITIONAL meaning representation (WordNet/dictionary gloss + hypernym closure,
     via definitional_extraction) as a SECOND, DEMAND-ROUTED channel (conceptual for meaning-identity,
     associative for fine online selection). Do NOT FUSE into one score (Stage-1 fusion HARD-FAILED) -- route.
  4. Do NOT wire: settling, grounded read-out for selection, diagnosticity, bounded suppression, generative
     coherence, or the compositional role-bound read (all tested-negative).
  5. MEASURE on the LIVE reading/coref task before any capability claim (SemCor ceiling is a naturalistic-context number).

KEY REALIZATIONS (the enabling moves):
  - Move to the population where frequency is GUARANTEED wrong (gold strictly < top) -> MFS = 0 by construction,
    so the info-free twin (not MFS) becomes the real bar.
  - Structured LOCAL collocation beats a bag (and beats dense) -- and beats deeper syntactic features.
  - The gold-blind control trigger works because it is DIRECTIONAL (does the evidence favor a specific
    alternative to the habitual response) -- symmetric ACC-style conflict is direction-blind and ties its twin.
  - The reader was a "lesioned" brain: associative-only, no control network, no conceptual-meaning hub. Adding
    those is the advance; more scalar tweaks on the flat frame all hit the same (structural) wall.
  - The info-free twin discipline caught a FALSE breakthrough (the same-permutation gloss twin) before it was
    claimed -- the proper random-gloss twin at chance is what made the meaning finding real.

WHAT I DID NOT ESTABLISH / DO NOT QUOTE:
  - All numbers on the SemCor instrument (human-tagged senses; exact synset match, NOT WordNet taxonomic
    distance); no number crosses to live reading. The 0.39 override ceiling is a NATURALISTIC-context number.
  - Do NOT quote WiC 0.78 as a domain-general number (WordNet-provenance inflation); the controlled claim is
    chance -> 0.78 with the info-free twin at chance.
  - The semantic-control NET gain is modest (full +0.001 to +0.004) and trigger-quality-limited; the strong
    effect is on the override cases. Quote the TRIGGER (AUC 0.79) and the override-case gain, not the net.
  - Fusion and compositional role-binding are tested-NEGATIVE; do not present them as open opportunities.

FILES: experiments/exp_context_override_frequency_wsd_v1.py; verification/test_context_override_frequency.py;
verification/test_definitional_meaning_representation.py;
notes/problems/context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark/{SOLVED.md, DESIGN_brain_analysis.md};
data/exp_context_override_frequency_wsd_v1/metrics.json. NO hdlab/.

TLDR (plain language): Words have a common meaning and rarer ones; the brain leans on the common one but lets
the sentence override it to pick the rarer meaning. On modern sense-labelled text, with the frequency habit
guaranteed to point the WRONG way, the sentence context picks the correct rarer meaning ~39% of the time vs
0% for the habit and ~16% for scrambled context, and it survives hiding the whole source document (real
understanding, not topic memorising). Pushed to ask "if this were truly brain-faithful, wouldn't it work
better?", I found the reader was like a brain with two parts missing: (1) the CONTROL part that actively
suppresses the habitual meaning when the sentence disagrees -- I built it (a detector that, without seeing the
answer, spots when another meaning fits better, right ~79% of the time), and (2) the part that stores what
words actually MEAN (definitions/concepts), not just what words they appear near -- without it, the reader was
at chance on "do these two sentences mean the same thing?", and adding it takes that to ~0.78. I also
carefully ruled out the tempting fixes that DON'T work (fancy settling, grounding, fusing the two systems, a
who-did-what-to-whom parser) -- each tested with a control, each closed. So: the override is real and built;
the two missing brain systems are identified and prototyped; wire them as separate demand-routed channels;
and the only bigger thing left (full sentence comprehension) is a separate long-term goal, not a fix to this.

QUESTIONS: none blocking. One judgement call: filed SOLVED -- the bar (override beats frequency, twin losing)
is met and strengthened; the two missing-organ findings are additional, deeper advances that answer the
fidelity challenge. If you want the ATL conceptual-meaning channel wired-and-measured before accepting, mark
that sub-item as the follow-on; the override + control results stand on their own.

NEXT STEPS: (1) wire the override organ + semantic-control organ (default-off). (2) wire the ATL
conceptual/definitional meaning as a demand-routed second channel (route, do NOT fuse). (3) measure on the
live reading/coref task. (4) Do NOT pursue settling / grounding-for-selection / diagnosticity / fusion /
compositional role-binding (tested-negative). (5) Full comprehension / situation-model is a separate Phase-1
program (sense selection becomes a read-out, not a module) -- justified on its own terms, not as a fix to this number.
