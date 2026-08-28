# Brain-foundational design: can CONTEXT override the frequency prior and pick a word's RARER meaning?

**Slug:** `context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark` -- solver session, 2026-08-26.
This is the design/methodology doc: the brain frame, the mechanism, and the two research drills that
shaped every arm of `experiments/exp_context_override_frequency_wsd_v1.py`. It exists because the owner
asked to "stay brain foundational" and to run research drills to "make sure we're doing the right thing."
(Numbers marked [FULL] are filled from the full-corpus run; smoke-validated figures are marked [smoke].)

## 1. The opening move: how does the BRAIN resolve a word's meaning against the frequency habit?

The phenomenon is **reordered access** (Duffy, Morris & Rayner 1988): a word activates all its senses,
weighted by a **frequency PRIOR** (resting activation / dominance), which **CONTEXT can override** -- the
**subordinate-bias effect** (Pacht & Rayner 1993): a subordinate meaning wins when prior context supports
it, against frequency, but at a residual processing cost (the prior is never fully erased). The optimal
combination is **BAYESIAN and additive in log space** (Norris 2006, the Bayesian Reader):

    log P(sense | context) = log P(sense)  [PRIOR / dominance]  +  log P(context | sense)  [LIKELIHOOD]

The senses being combined are stored from a **LIFETIME of experience in the ATL semantic hub**
(Lambon Ralph, Jefferies, Patterson & Rogers 2017), NOT re-estimated from a tiny corpus per trial.

**PINNED (do not invent around it):** reordered access = frequency prior + context likelihood, additive;
the inventory is pre-stored. **OUR-INVENTION-UNDER-TEST (sweep, do not adopt):** how the context
likelihood is computed (single cosine vs multi-step settling); what the pre-stored inventory is (SemCor
experience prototypes, held out); the context representation and the prior:context weighting lambda:beta.

## 2. Why this is finally testable (the data block is removed)

The parent result `the_meaning_win...` (integrated PARTIAL) proved the frequency PRIOR works (beats
uniform CI-separated) and is the wire-able half, but could NOT test the OVERRIDE: on the ~200-year-old
McGuffey corpus each subordinate sense is attested ~once (prototype n=6). SemCor (WordNet-sense-tagged
running text, via nltk) removes that: subordinate senses are attested MANY times, so a held-out sense
prototype is formable. Probe (full corpus): **46,702 held-out subordinate-congruent items** (gold sense
strictly less frequent than the top sense; MFS = 0 by construction) across 3,535 lemmas; 44,281 also
formable under document-level holdout. The experiment CAN succeed.

## 3. The instrument

- **Population:** subordinate-congruent items = an attestation whose gold WordNet sense count is
  STRICTLY below the lemma's top sense count. On these the frequency floor MFS is wrong by construction
  (== 0). Ties-for-top are excluded (balanced words have no "less frequent" sense). Held-out
  leave-one-instance-out (and leave-one-DOCUMENT-out as a stronger leak control).
- **Inventory (the ATL store):** per WordNet synset, a held-out prototype = IDF-weighted bag of the
  content words of that sense's OTHER sentences (the "lifetime experience" of the sense). Cosine gives
  the context likelihood.
- **Grading:** discrete accuracy against the HUMAN-annotated SemCor sense (human judgement, NOT WordNet
  taxonomic distance). WiC (human same/different labels) is the second, human-graded instrument. SemCor
  synsets are the inventory + source of multiply-attested contexts, never the taxonomic scorer.
- **Floors, recomputed on the population:** MFS (frequency, = 0), uniform (1/k), and the info-free TWINS
  -- SHUFFLE (context vector from a DIFFERENT item; destroys the item<->context link) and SCRAMBLE
  (context words replaced by random vocab). Null p95 = the shuffle-twin accuracy distribution over seeds.
- **Statistics:** lemma-CLUSTERED bootstrap (items sharing a lemma+prototype are not independent).

## 4. The two questions, made decisive

**Q1 -- does context override frequency?** The Bayesian reordered read (log-prior + context log-likelihood)
must recover the subordinate sense CI-separated over the MFS upper bound, with the info-free twin LOSING.
[smoke: MFS 0.000, REORDERED 0.172 vs MFS delta +0.175 CI[0.14,0.21], SHUFFLE 0.024 loses CI-sep,
null_p95 0.023 -- override_win = True.] The clean demonstration lives in the context-likelihood term
(CONTEXT_ONLY ~0.42 [smoke] >> MFS 0, twin, uniform); adding the prior at equal weight imposes the
**subordinate-bias residual cost** (REORDERED < CONTEXT_ONLY) -- a brain-faithful signature, quantified
by the lambda sweep (prior helps DOMINANT items, costs SUBORDINATE items).

**Q2 -- does genuine multi-step SETTLING earn its keep over the single feed-forward read?**

## 5. Research drill 1 (the reframe): settling's fingerprint is RELATEDNESS, not accuracy

The first drill's load-bearing finding: for dominance x context, a **Bayesian race / threshold** model
explains the data as well as full recurrent settling; the cleanest evidence that genuine multi-step
settling is REQUIRED comes from **relatedness-dependent effects** -- the **polysemy advantage vs
homonymy disadvantage** (Rodd, Gaskell & Marslen-Wilson 2004; Armstrong & Plaut 2016): related senses
share a broad shallow basin (settle cheaply); unrelated meanings sit in separate deep basins that
compete (settle slowly). A feed-forward/race model CANNOT produce this, and it must VANISH at T=1.

So the drill REDIRECTED the test: "build a settling loop and show it beats cosine on accuracy" is the
WRONG (possibly decorative) test -- the RIGHT test is whether the settling produces the relatedness
signature that a feed-forward model can't fake. **A CI-tie on accuracy is the predicted, honest
outcome**, and the bar explicitly allows it ("beats OR CI-ties, honestly reported"). Consistent with
this, [smoke] SETTLE 0.1725 CI-ties REORDERED 0.1722 (delta +0.0003 CI[-0.002,+0.002]); homonym vs
polyseme show ~no accuracy gap and near-identical trivial settling cost.

## 6. Research drill 2 (the fairness check): am I testing a STRONG settling, and is the prior weighting faithful?

Before reporting "settling does not earn its keep," the standing discipline demands testing the STRONGER
brain version, not a strawman. Three open risks were drilled (and probed empirically in parallel). Drill 2
also delivered two corrections that reshaped the reporting:

- **The subordinate-bias residual is LATENCY, not accuracy (Binder & Rayner 1998, read directly).** The
  SBE is a 33-46 ms gaze cost that RESOLVES within one word downstream; human comprehension accuracy under
  strong context is ~97-98%, never below chance. So my model's "equal-weight prior drags subordinate
  ACCURACY below chance" must NOT be reported as "the faithful residual" -- that mis-maps a latency effect
  onto an accuracy statistic. FIX: the override is carried by the context LIKELIHOOD (which beats all
  floors); the prior's cost is reported as a MARGIN (subordinate reordered margin << dominant margin --
  the latency analog), and the prior is shown to HELP dominant-item accuracy (the reordered-access
  trade-off). CAVEAT folded in: the ~0.30-0.40 context ceiling reflects NATURALISTIC/diffuse SemCor
  context; human strong-context ceilings are near 100% on curated, maximally-diagnostic stimuli -- a
  ceiling depends on the diagnosticity handed in, not only on the mechanism.
- **CONTROLLED RETRIEVAL / diagnosticity is a real, currently-missing mechanism (Badre et al. 2005;
  Desimone & Duncan 1995).** Weight each context word by how much it DISCRIMINATES the candidate senses
  (`diag(c) = Var_lambda[cos(c, proto_lambda)]`), computed over the candidate SET only -- LEAK-FREE (never
  the gold). BUILT as the DIAG arm. Tested: it does NOT beat uniform IDF aggregation on average (a tested-
  neutral brain mechanism); the drill's specific prediction (it helps where a FEW words carry the signal)
  is checked via the diagnosticity-CONCENTRATION subgroup split.
- **Joint vs single-target settling.** The canonical Rodd/McClelland mechanism is JOINT constraint
  satisfaction (all the sentence's ambiguous words settle together). Drill 2's verdict: NOT worth building
  yet -- its own sequencing gate is "build joint only if single-target-in-DENSE shows the relatedness
  signal but STILL TIES on accuracy." My dense single-target settling HURTS (does not tie) and the basin
  gap is weak, so the gate is NOT met. Joint settling is flagged as a scoped future test (pre-registered
  to the subgroup of sentences with co-occurring subordinate-biased words), not built.
- **Representation richness. TESTED (probe 3).** IDF bag-of-words gives ~0.02 inter-sense cosine even for
  RELATED senses -> no basin structure. Rebuilt the inventory in a DENSE distributed space (PPMI +
  truncated SVD d=150, the ATL-hub analog): the basin structure now EXISTS (inter-sense cosine ~0.30) and
  has the Rodd-CORRECT direction (polyseme basins broader than homonym: 0.314 vs 0.282, small gap). The
  override still holds (CONTEXT_ONLY 0.357, REORDERED 0.209, MFS 0), though sparse IDF scores higher on
  the override (0.42) -- exact-lexical context is the stronger selection cue, so sparse stays the headline.
  **CRITICALLY: continuous-attractor settling STILL does not earn its keep even in the fair, real-basin
  dense space -- it HURTS (SETTLE 0.136 vs feed-forward 0.209; helped 44 items, hurt 1258)**: settling
  over-commits toward the dominant/central basin and destroys the fine context discrimination selection
  needs. So the settling negative is FAIR (a representation where basins are real) and ROBUST across
  representations (ties in sparse, hurts in dense) -- consistent with the literature's claim that the
  relatedness signature is an RT/depth effect, not a selection-accuracy benefit.
- **Controlled retrieval / diagnosticity.** Anterior-VLPFC controlled retrieval (Badre et al. 2005)
  top-down-biases weak/subordinate meanings. Should the override be an explicit control term that
  up-weights DIAGNOSTIC context features rather than a uniform likelihood? [pending drill 2; note the
  leak risk -- a diagnosticity weight from the candidate set can peek, demoted in a prior slug.]

## 7. Component-by-component fidelity ledger

| Component | Fidelity | Note |
|---|---|---|
| reordered access = additive log-prior + context log-likelihood | PINNED | Duffy-Rayner; Norris 2006 |
| pre-stored inventory = held-out SemCor experience prototypes | PINNED direction | ATL lifetime store; NOT per-trial re-fit |
| grade on human SemCor senses + WiC human labels | PINNED | not WordNet taxonomic distance |
| decision = argmax of the Bayesian score (feed-forward) | measured sufficient | settling CI-ties it on accuracy |
| settling = continuous attractor + lateral competition, T>1 | INVENTION-UNDER-TEST | tested for the relatedness signature |
| lambda, beta, T, gamma, dense-vs-sparse rep | INVENTION-UNDER-TEST | all swept; none adopted |

## 8. What a WIN and a NEGATIVE each mean (decisive either way)

- Context overrides frequency on subordinate items CI-separated (twin losing) -> the override capability
  is REAL on modern data (a first; the parent result could not test it). Propose the hdlab wiring
  (frequency prior as sense default + the context likelihood; strategy lands it).
- Settling does NOT beat the feed-forward Bayesian read (CI-tie/loss) AND the relatedness signature does
  not require recurrence -> the brain-faithful-enough mechanism for sense SELECTION is the Bayesian race,
  not full mutual-constraint settling -- a rigorous, valuable negative on the settling sub-question, only
  trustworthy BECAUSE the data can now test it and BECAUSE the stronger settling versions were built and
  tested (joint / dense / controlled), not assumed away.

## 9. Resolving the negatives (owner: "these should work if we're brain-foundational") -- drill 3 + probes

The owner's challenge is the standing discipline: a miss is a fidelity gap to build across unless it is a
genuine brain fact. I split the four negatives by testing each -- some resolve (they were MY gaps), some
do not (they are brain facts that would be UN-faithful to force):

- **NEGATIVE 2, the ~31% override CEILING -- RESOLVED, it was a REPRESENTATION fidelity gap.** My context
  likelihood was a BAG-OF-WORDS cosine, the weakest possible context rep; it discards local collocation
  and syntax, which the brain uses ("one sense per collocation", Yarowsky 1993; the immediate syntactic
  neighbours carry most WSD signal). Probe (200 files): bag 0.34, positional-collocations-only (L1/L2/R1/R2)
  0.34, **bag+positional 0.41** -- the local and broad-thematic cues are COMPLEMENTARY (either alone ~0.34,
  together 0.41), which is itself brain-faithful. FOLDED IN: the cell's headline context is now STRUCTURED
  (BAG + positional collocations); smoke override rose 0.39 -> 0.46. The deeper lever (selectional
  restrictions / thematic fit -- a predicate selects its arguments' senses; McRae/Hare/Elman) is the next
  step above raw positional collocation and is drill-3-pending.
- **NEGATIVE 1, SETTLING does not improve SELECTION accuracy -- persists under structured context (still a
  tie), consistent with a GENUINE BRAIN FACT.** Settling affects RT / time-course (Armstrong & Plaut), not
  the selected sense, in this full-sentence-at-once regime; a Bayesian race suffices for the decision.
  (The one regime that could change the OUTCOME -- incremental reading with late-arriving disambiguation +
  reanalysis, or joint co-ambiguity settling -- is drill-3-pending; my instrument scores the whole sentence
  at once, which may structurally hide any settling benefit.)
- **NEGATIVE 3, DIAGNOSTICITY neutral -- persists under structured context.** Likely my operationalization
  (uniform variance-weighting) is not the brain's controlled retrieval, which is COMPETITION-GATED (engaged
  only when the automatic read is uncertain) and may be SUPPRESSIVE (inhibit the dominant sense) rather
  than up-weighting -- drill-3-pending.
- **NEGATIVE 4, WiC near-majority -- persists under structured context** (smoke 0.55 vs majority 0.56),
  pointing to a genuine SemCor->WiC sense-granularity mismatch rather than a context-rep gap.

The honest split so far: the CEILING was my fidelity gap (fixed, structured context); SETTLING-for-accuracy
and WiC look like genuine facts/limits; DIAGNOSTICITY awaits the right (gated/suppressive) formulation.

## 10. The deep fidelity drill (owner: "are we ACTUALLY brain-faithful? if we were, wouldn't this work?") -- drill 4

This challenge overturned my own conclusions and found the real missing organ. Drill 4 also surfaced
ON-DISK evidence I had missed. The verdict:

- **My distributional model IS brain-faithful for what it models** -- the brain's fast associative access
  (Swinney 1979) + reordered-access scoring (Duffy-Rayner; McClelland 2013). "Distributional == ungrounded
  surface stats" is itself a caricature: co-occurrence provably recovers grounded structure (Gunther 2019;
  Louwerse 2011). It is NOT a mere surface proxy.
- **Grounding does NOT fix it -- REFUTED on this project's own disk, recently and at power.**
  `reader_meaning_channel` tested the richest grounded hub (sensory+motor+affect, Bayesian-combined,
  control-gated) on a real selection instrument and it did NOT beat the frequency prior CI-separated. So
  the ceiling is not a grounding gap; the two-meaning-systems audit (grounding -> similarity, not
  selection) holds.
- **The real fidelity gap is SEMANTIC CONTROL: conflict-gated SUPPRESSION of the frequency-dominant sense**
  (LIFG/pMTG; Noonan et al. 2010 -- a dissociable, damageable computation). My associative-only model is
  behaviourally like a semantic-APHASIA brain (lesioned control network). `the_prior_swamps_the_channel`
  had already shown the mechanism is oracle-verified worth ~+30 points on subordinate items, but every
  gold-blind TRIGGER it tried scored at chance (AUC 0.40-0.54), because the channel's errors are 95.65%
  frequency-correlated.
- **THE BUILD (this session's advance):** a GOLD-BLIND two-sided conflict trigger --
  `conflict = max_{s != dominant} coh(context, s) - coh(context, dominant)` -- predicts "the prior is
  wrong" at **AUC 0.80** (shuffled-context twin 0.58, CI-separated). This is the enabling move: a two-sided
  signal instead of the frequency-confounded peakedness/entropy proxies the project tried before. Wired as
  GRADED gated suppression of the dominant sense, it lifts the frequency-OVERRIDE (subordinate) cases
  CI-separated, with the gain attributable to the real trigger (info-free shuffled-trigger twin LOSES) and
  a brain-faithful see-saw (the small dominant cost is the Gernsbacher 1990 suppression trade-off).

### The settling negative was a TAUTOLOGY, not a finding (drill-4 correction)

McClelland (2013, Frontiers in Psychology 4:503) PROVES that recurrent attractor settling and
`argmax[log P(sense) + coherence]` are the SAME computation (log-priors as biases, log-likelihoods as
weights). So my feed-forward read IS the settling fixed point -- testing "does settling beat the
feed-forward read" was testing a tautology, and a null was mathematically guaranteed, not informative.
Additionally, genuine competitive settling only pays off with WELL-SEPARATED basins, and this substrate's
measured 95.65%-frequency-correlated errors show the sense-prototypes are NOT well separated -- exactly the
regime that kills settling (Mirman et al. 2010). REVISED: "settling doesn't earn its keep" is withdrawn as
a finding; the correct statement is that settling is FORMALLY IDENTICAL to the read we already use, and the
real lever is CONTROL (suppression), not the settling dynamics.

### Revised status of the negatives
- ~39% override ceiling: MOSTLY a genuine, calibrated task-difficulty floor (2020 transformer SOTA gets
  only 52.6% on the analogous least-frequent-sense subtask; Blevins & Zettlemoyer 2020) -- my structured
  0.39 with no pretrained backbone is within ~13 points -- PLUS the real, now-addressed suppression gap.
- settling inert: a mathematically-guaranteed tautology + wrong basin geometry (NOT a fair test).
- diagnosticity null: an implementation artifact of a frequency-confounded circular proxy; the correct
  control operation (gold-blind conflict trigger + suppression) DOES work (AUC 0.80).

## 11. Mechanism-fidelity drill (drill 5) -- is the TRIGGER and the SUPPRESSION brain-faithful? Three refinements tested, all negative -> genuine convergence

The owner asked whether every piece is brain-faithful and whether there are optimisations. Drill 5 +
probes 8-10 interrogated the two engineering-choice pieces (the conflict TRIGGER and the SUPPRESSION
operation) and the surrounding machinery. Verdict: the mechanism is at its sensible ceiling; three
brain-motivated refinements were each tested with a can-fail test and came back NEGATIVE, each with a
specific reason -- which is what CONVERGENCE (mechanism identified + built + faithful refinements tested,
or shown un-improvable with a reason) actually looks like.

- **The TRIGGER is brain-faithful FUNCTIONALLY (directional), and empirically the best.** ACC conflict
  monitoring (Botvinick 2001) is SYMMETRIC co-activation energy `= 1 - Sum a_i^2` (Gini-Simpson) --
  direction-BLIND. Probe 8 (gold-blind AUC to predict prior-is-wrong): my two-sided
  `coh(best-nondom)-coh(dom)` = 0.80 (context-specific, twin 0.60); the symmetric ACC entropy/energy = 0.67
  AND tie their shuffled-context twin (~0.68 -- NOT context-specific, exactly as the direction-blind algebra
  predicts); prediction-error KL(ctx||prior) = 0.53; margin anti-predictive; unfitted combos HURT. So the
  directional signal is load-bearing and my trigger has it; the literal ACC measures are worse. ("ACC-style
  conflict" was already a thin extrapolation to lexical selection -- the shared substrate is left IFG, not
  ACC; January, Trueswell & Thompson-Schill 2009.) A FITTED combiner is NOT worth building (no
  context-specific residual in the other features).
- **BOUNDED (biased-competition / divisive-normalization) suppression -- TESTED, FAILED its can-fail
  test.** The faithful saturating form `-= gamma*sigmoid/tanh(...)` (Reynolds-Heeger; Louie-Glimcher) was
  predicted to reduce the dominant see-saw by capping overcorrection on noisy high-conflict outliers.
  Budget-matched probe 9: bounded is -0.0058 CI-separated WORSE than the additive relu on the
  top-quartile-conflict DOMINANT items (the predicted-benefit subset), and the overall difference is
  negligible (+0.0005). REASON: the see-saw is NOT driven by extreme-conflict outliers (those are mostly
  TRUE subordinates, correctly suppressed); the false-positives are spread across the moderate-conflict
  range, so capping the extremes does not help. The see-saw is TRIGGER-quality-limited (AUC 0.79), not
  suppression-SHAPE-limited.
- **GENERATIVE / predictive coherence -- TESTED, CI-TIE.** Replacing the cosine associative overlap with a
  naive-Bayes generative likelihood P(context|sense) (the belief-update / N400 framing; Rabovsky, Hansen &
  McClelland 2018) does NOT beat cosine on the override (probe 10: 0.401 vs 0.410, d -0.009 straddles 0).
  Cosine overlap is an adequate likelihood here.

**Net:** the brain-foundational mechanism (reordered access + STRUCTURED context + a directional
conflict-gated suppression) is at its sensible ceiling for this feature set. The residual gap is
FUNDAMENTAL -- task difficulty (2020 SOTA 52.6% on the least-frequent-sense subtask; Blevins & Zettlemoyer)
plus trigger quality (AUC 0.79) -- not a fixable fidelity gap I have found. The forward lever, if pursued,
is a genuinely NEW orthogonal directional signal for the trigger (not re-weighting the existing set).

## 12. THE ROOT DRILL + the meaning-representation breakthrough (owner: "brain-foundational would not be negative if we were doing this right") -- CORRECTS my premature "converged"

I was wrong to call it converged in section 11. The owner's principle -- a truly brain-faithful system
would NOT plateau where the brain succeeds -- was correct, and a root-level drill + controlled probes found
the fundamental fidelity gap I had missed.

**The tell:** on the HUMAN-graded meaning-identity task (WiC: "do these two sentences use the word in the
same meaning?") my model is at CHANCE (balanced acc ~0.51), while humans are ~0.80. If we captured MEANING
the brain's way, the human-judged task would work. It did not.

**The root diagnosis (drill 6):** my whole computation is `cosine(bag(context), bag(sense co-occurrences))`
+ scalar terms -- a SYMMETRIC, ORDER-INVARIANT, ROLE-BLIND, single-locus similarity. Every "mechanism
refinement" (suppression, conflict trigger, generative coherence) added another SCALAR to the same flat
sum and left those structural properties fixed. A wall every variation hits while the structure is held
fixed is the signature that NONE of them was the brain's mechanism -- the wall is STRUCTURAL, not
parametric. The brain runs an ASYMMETRIC, COMPOSITIONAL, relational-consistency check over a learned
MEANING space (St. John & McClelland sentence gestalt; Kintsch CI; ATL conceptual hub).

**The controlled result (probes 12-15) -- and a did-it-right catch:** swapping only the SENSE
REPRESENTATION from raw co-occurrence bags to a DEFINITIONAL/conceptual one (WordNet gloss + examples +
hypernym/hyponym closure -- a static offline glass-box asset, the ATL lexical-semantic hub analog), with
the SAME argmax-cosine algorithm, lifts WiC from chance to **balanced accuracy 0.78 CI[0.75,0.82]**. THE
CONTROL MATTERED: my FIRST info-free twin (permute glosses with the SAME permutation for both sentences)
was a NON-control -- "do both sentences pick the same slot?" is invariant to a shared relabelling, so it
read 0.78 too and would have let me claim a false win. The PROPER twin (each sense gets a RANDOM UNRELATED
synset's gloss) collapses to **chance 0.51 CI[0.49,0.53]** -- so the WiC gain is GENUINE MEANING,
CI-separated from the info-free twin. (Caveat: WiC was partly built from WordNet, so gloss-Lesk has some
inside-track on its sense boundaries; the absolute 0.78 is inflated by that, but chance->0.78 with the
twin at chance is decisive on the qualitative point.)

**Reconciliation (the two-meaning-systems architecture the project already audited):**
- CO-OCCURRENCE context (the LIFG/pMTG ASSOCIATIVE system) wins the fine-grained SemCor synset selection
  (0.41) but is at CHANCE on meaning-identity (WiC) -- word-company is not meaning.
- DEFINITIONAL/conceptual meaning (the ATL hub) wins meaning-identity (WiC 0.78) but is worse on fine
  SemCor selection (0.22 -- glosses are short/sparse); combined with co-occurrence it adds only marginally
  on SemCor (+0.006 at low weight).
- So the two are COMPLEMENTARY and TASK-DEPENDENT -- the brain's two systems. I had built ONLY the
  associative half, which is exactly why the human-graded MEANING task was at chance. This also reconciles
  the on-disk grounding refutation: the missing piece is NOT sensorimotor grounding (refuted for
  selection) -- it is the lexical-CONCEPTUAL/relational meaning the ATL hub stores (definitional).

**Corrected status of the negatives:** the WiC-at-chance was a genuine FIDELITY GAP (a missing brain
system -- the ATL conceptual-meaning hub), not a ceiling. My section-11 "converged" was premature; the
faithful rebuild (conceptual meaning representation) DID break the plateau, exactly as the owner predicted.
The forward lever is the two-system model (associative context + conceptual/definitional meaning), and --
per the root drill -- a compositional, role-bound, relational-consistency computation over that meaning
space (using the project's existing bind/bundle operators + an offline static parse) rather than a flat
bag-cosine.

## 13. PATH FORWARD -- the two-system, control-gated, compositional architecture (design drill) + how it ties into what was built

The design drill maps the two-system finding onto CONTROLLED SEMANTIC COGNITION (Lambon Ralph et al.
2017): ATL = the conceptual STORE; LIFG/pMTG = controlled RETRIEVAL that gates which part of the ATL store
is active (it never stores meaning). So the combination is NOT a symmetric blend -- it is DEMAND-GATED
division of labor: "associative proposes, conceptual verifies." Crucially, this REUSES the organs already
built.

**Unified read (target):**
  score(s | c_1:t) = lambda*logP(s) [prior] + beta*coh_assoc(s, c) [structured-context likelihood]
                   - delta*suppress(dominant | conflict) [existing control]
                   + gamma(conflict)*sim_ATL(gloss(s), SitModel(c)) [NEW gated conceptual term]
  gamma(conflict) = gamma_max * sigmoid(k*(conflict - theta))     -- the EXISTING AUC-0.79 trigger is the gate
  SitModel(c_1:t) = running FHRR bundle of resolved-sense glosses  -- the incremental context
For a WiC-shaped identity judgment: associative resolves each occurrence's sense; identity is judged in
ATL space: same iff sim_ATL(gloss(s1*), gloss(s2*)) > tau ("associative proposes, conceptual verifies").

**Organ mapping (nothing thrown away):** reordered access = the fast default route (most words resolved
without control -- Rodd 2005); the semantic-control trigger = the GATE (generalized to gate both
suppression AND the conceptual term); FHRR bind/bundle = clause-level role-filler composition;
`definitional_extraction` = the ATL store + an offline thematic-fit table; the situation-model accumulator
= the evolving context both the likelihood and the conceptual conflict condition on; the two-meaning-
systems WHITENED metric = sim_ATL (do not build a third representation); grounded norms stay excluded.

**Why the role-bound read is an OPERATOR fix, not a feature fix:** the +0.007 selectional-fit null was
feeding compositional features into a SYMMETRIC bag operator (commutative -> role-blind). The fix is the
non-commutative FHRR binding (R_AGENT (x) V != R_PATIENT (x) V; Plate HRR; Eliasmith SPA), with clause
vectors scored by role-conditioned selectional consistency -- and a MANDATORY role-permutation info-free
twin at every stage (if permuting roles doesn't degrade the score, it silently collapsed back to a bag).
Neural support: Frankland & Greene (2015) decode compositional agent/patient role-filler codes in left
mid-superior temporal cortex.

**Staged, can-fail build plan (leverage-first):**
- STAGE 1 (same-day, NO new organs): the trigger-gated two-system combination above. **RAN (probe 17,
  full SemCor n=53,111): HARD-FAIL.** GATED - ASSOC(specialist) = -0.0016 (not better) and GATED -
  RANDOM-GATE twin = +0.0004, NOT CI-separated -- the conflict trigger does NO real work as a fusion gate
  (admitting the conceptual term gated-by-conflict is indistinguishable from admitting it at RANDOM). ->
  DECISIVE: do NOT FUSE the two systems into one score. They are DEMAND-SEPARABLE (associative for fine
  online selection, conceptual for meaning-identity), and the brain-faithful model is task/demand ROUTING,
  not summing -- exactly the CSC division-of-labor prediction, now empirically grounded. Per the drill's own
  gate, Stage 3 (role-bound read) is warranted only on its OWN can-fail test (coh_role alone vs coh_assoc
  alone on role-bearing items), not as a fusion.
- STAGE 2 (cheap): a conceptual-space conflict signal from the situation-model gestalt (NOT raw gloss --
  see optimization note). HARD-PASS: raises trigger AUC beyond 0.79 OR catches a disjoint error class.
- STAGE 3 (new offline asset): dependency->role transducer + thematic-fit centroids; test coh_role ALONE
  vs coh_assoc ALONE on role-bearing items (role-permutation twin alongside). **RAN (probe 18) DESPITE
  Stage-1's fail, because it is a distinct hypothesis -- built RIGHT (real spaCy parse; a genuine
  role-conditioned selectional-preference profile F[(head,rel)] from gold-sense glosses, held out per
  document; NOT bag features): HARD-FAIL.** On role-bearing subordinate items (n=3,416): ROLE-fit 0.265 vs
  ASSOC(bag) 0.243 = +0.022 CI includes 0 (no CI-separated win); the mandatory role-permutation info-free
  twin (wrong-role profile) 0.246 -- ROLE-fit - ROLE-PERM = +0.020 CI includes 0 (the RIGHT role does NOT
  beat a WRONG role -> role-conditioning is not doing distinguishable work); role ADDS nothing beyond the
  bag (+0.007, not sep -- the same null as the +0.007 feature version); and role-conditioning is WORSE than
  plain gloss (0.265 < 0.298), i.e. the (predicate,role) profile adds noise. SPECIFIC REASON: on this
  population sense is resolved by TOPICAL/COLLOCATIONAL context (which the bag captures), not by
  who-did-what-to-whom; the role-permutation twin not losing is the direct evidence. Caveat: modest power
  (+/-0.03-0.06 CIs) -- but point estimates + the twin + the plain-gloss comparison all agree. -> The last
  computational-KIND lever does NOT earn its keep as a sense-selection mechanism on this task. Do NOT build
  Variant B (Stage 4).
- STAGE 4: full role-bound integration + Hopfield-attractor readout; ablate the binding ALGEBRA (replace
  circular convolution with additive one-hot) as a twin, since VSA binding is unpinned in this project.

**Optimization findings on the EXISTING organs (owner's second question), TESTED:**
- Conflict trigger in CONCEPTUAL space (gloss-vs-sentence): NEGATIVE -- AUC 0.54 vs the co-occurrence
  trigger 0.80; z-combining HURTS (0.76). The co-occurrence trigger stays best. (The drill's proper
  situation-gestalt version is untested -- needs the situation model; Stage 2.)
- Context-informative lambda (shrink the prior weight as coh_assoc entropy falls -- Duffy-Rayner): a
  plausible, well-precedented, untested optimization to the reordered read (candidate, not yet run).
- The additive combination should become GATED (Stage 1), not unconditional -- an unconditional sum
  dilutes whichever system is decisive for the current judgment type.
Net: the associative organ is at its sensible ceiling; the real gains require the NEW conceptual/
compositional system (Stage 1+), which is the path forward, not a tweak.

**Tie to the project arc:** the definitional/ATL representation IS the Phase-1 meaning-supply artifact
(offline, static, glass-box); Stage 1 is the first place the two-meaning-systems audit becomes ONE running
pipeline rather than a comparison table; the situation model is the connective tissue that keeps
sense-selection a READ-OUT of the evolving comprehension state, not a standalone WSD module (St. John &
McClelland sentence gestalt; sense settling as a byproduct of situation-model update, with sense accuracy
kept only as the scoreable instrument).

## Anchor citations
Duffy, Morris & Rayner (1988), J. Memory & Language 27:429-446 (reordered access);
Norris (2006), Psychological Review 113:327-357 (Bayesian combination);
Noonan, Jefferies, Corbett & Lambon Ralph (2010), J. Cognitive Neuroscience 22:1597-1613 (semantic
control / suppression is a dissociable, damageable computation -- the missing organ);
McClelland (2013), Frontiers in Psychology 4:503 (settling == argmax[logP + coherence], i.e. the settling
test is a tautology); Gernsbacher (1990), Language Comprehension as Structure Building (suppression of the
context-inappropriate meaning); Blevins & Zettlemoyer (2020), ACL (calibration: SOTA 52.6% on the
least-frequent-sense subtask); Lambon Ralph et al. (2017), Nat Rev Neurosci 18:42-55 (ATL hub vs control
network); Rodd, Gaskell & Marslen-Wilson (2004), Cognitive Science 28:89-104 (attractor-basin settling).
