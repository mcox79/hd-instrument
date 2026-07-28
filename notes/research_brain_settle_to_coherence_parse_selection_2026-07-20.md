# RESEARCH DRILL (3x): how the brain SETTLES on a coherent sentence interpretation, whether settling itself yields a "which-reading-is-right" signal, and whether that signal sharpens with world-experience

**Date:** 2026-07-20. **Filed by:** research (3 parallel Sonnet lit-scans -- axis 1 Kintsch Construction-Integration;
axis 2 N400/P600/predictive-coding + expertise; axis 3 Hopfield/resonator-network settling-confidence
literature -- synthesized by director). Trigger: direct USER drill to ground a "settling parse-selector"
experiment: construct candidate parses as composed vectors, run a clean-up/settling dynamic against a
learned codebook, and use the STABILITY of the settled state as the rationality score for parse selection,
then sweep corpus richness.

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature agreement;
novel-synthesis capped P<=0.50). Sub-agent reports themselves flagged canonical vs. speculative claims;
that grading is preserved below rather than flattened.

---

## HEADLINE

**The brain mechanism is real and well-documented (Construction-Integration settling = literal
constraint-satisfaction relaxation on an activation vector against a connection matrix; N400/Rabovsky
sentence-gestalt work gives a DIRECT, citable precedent for "low residual-of-change at settling = coherent
reading"). But two of the three legs the experiment needs are NOT directly demonstrated in the literature
and must be treated as extensions, not established fact: (1) no paper equates CI settling with a
Hopfield/attractor energy function -- the isomorphism is a strong structural analogy, not a proven identity;
(2) no study manipulates world/domain experience and shows a SHARPENING of the settling-residual
discrimination itself (expertise/vocabulary studies are real but indirect analogs -- different measure,
different design). The construction-determinism traps the lit-scan surfaced independently (resonator-network
convergence-speed confounds, Hopfield beta-as-hyperparameter, codebook-size capacity cliffs) are the load-bearing
part of this note and map cleanly onto guards a substrate settling-parse-selector cell must pre-register.
A fair test is tractable but the richness-sharpens-signal claim specifically should be deflated hardest --
it is the one leg with the weakest direct precedent.**

---

## (1) CONSTRUCT-INTEGRATE-SETTLE (Kintsch Construction-Integration)

**Construction (canonical, Kintsch & van Dijk 1978; Kintsch 1988, *Psych Review* 95(2)):** the model
represents text meaning as a network of propositions (predicate-argument structures). Construction is
explicitly "dumb"/context-insensitive: it activates ALL plausible readings in parallel from bottom-up
associative/lexical memory -- including implausible, contradictory, or irrelevant ones ("They are flying
planes" activates both the verb-phrase and the noun-phrase reading simultaneously) -- with NO
discourse-context filtering at this stage. Over-generation is the point: nothing is pruned before
integration.

**Integration (canonical mechanism, formalized by Guha & Rossi 2001, *J. Math. Psych.* 45(2)):** this is a
literal linear-algebra relaxation -- an activation vector is repeatedly multiplied against a weighted
connection/association matrix and renormalized each cycle, iterating until it stops changing
appreciably. Guha & Rossi analyze this as a dynamical system and derive the possible equilibrium points
from the connectivity matrix. **Settling = the activation vector reaching (approximately) a fixed point** --
coherent/mutually-supporting propositions reinforce each other and rise in activation; contradictory or
unsupported ones receive no reinforcement and decay toward the floor. **Selection is not a separate decision
rule** -- the settled relative activation levels ARE the selection: the reading whose propositions end up
with highest activation IS the comprehended interpretation. No external arbiter needed.

**Convergence specifics (deflated -- gap flagged by the lit-scan):** convergence is described qualitatively
as rapid/typically-a-few-cycles in secondary sources, but the sub-agent could **not verify an exact canonical
cycle count** from primary text in this pass -- treat "few cycles" as approximate, not load-bearing precision.
Guha & Rossi (2001) also show the **equilibrium reached is sensitive to initial activation weights** -- i.e.
CI's own math literature already documents an initialization-dependence, which is directly relevant to the
construction-determinism guards below (whoever initializes the settling dynamic controls part of the outcome).

**Relation to Hopfield/attractor networks -- important calibration point:** the sub-agent found **no
paper that explicitly proves CI is formally isomorphic to a Hopfield energy-minimization process.** The
structural resemblance (activation-vector times connection matrix, iterated to a fixed point) is strong and
repeatedly gestured at (Sanjose/Vidal-Abarca/Padilla 2006 connectionist CI extension; McClelland et al. 2014
"Interactive Activation and Mutual Constraint Satisfaction" as the general family CI belongs to), but this
should be reported as **an inference we are making**, not a documented identity. This matters because it
means "CI settling = energy descent" is an ANALOGY we are importing into the design, not neuroscience fact.

## (2) THE COHERENCE/STABILITY SIGNAL, AND WHETHER IT SHARPENS WITH EXPERIENCE

**N400 as the integration/coherence signal (canonical, Kutas & Federmeier 2011 "Thirty Years and
Counting," *Ann. Rev. Psych.* 62):** N400 amplitude indexes how readily an incoming element integrates into
the evolving discourse/situation model; large N400 = poor fit/anomaly, small N400 = coherent/expected fit.
Federmeier's prediction-based reframing and later surprisal-based accounts (Michaelov, Coulson & Bergen 2022)
converge with this rather than compete with it.

**Direct precedent for "settling-residual = coherence" (the single most load-bearing citation for this
design, Rabovsky, Hansen & McClelland 2018, *Nature Human Behaviour* -- the Sentence Gestalt model):**
N400 is explicitly modeled as **the magnitude of change induced in a distributed hidden "sentence meaning"
representation by each incoming word** -- small change = word was already implicit in the model's running
prediction (coherent), large change = the model had to substantially revise its implicit meaning state
(anomalous/incoherent). This reproduces patterns across 16 ERP paradigms and is the direct computational
analog of "low residual at settling = plausibility signal." **This is the best available precedent and
should anchor the design's readout definition** (residual-of-change across settling iterations, not final
state alone).

**P600 as a complementary, discrete re-analysis signal:** distinct from N400, associated with structural
reanalysis/repair cost when the initial (fast) integration must be revised; contested whether it is
syntax-specific or domain-general conflict-monitoring, but functions as a second, later coherence-failure
signal in a two-stage pipeline (fast graded N400-style settling, then a slower discrete repair flag). Not
needed for a first cut of the design but worth keeping in reserve as a "hard disagreement" detector distinct
from graded settling-residual.

**Sharpening with experience -- WEAKEST LEG, deflate hardest:** the lit-scan found real but INDIRECT
support: domain-expertise studies (chess, ERAN/musical-training) show larger/sharper prediction-violation
signals in experts than novices; individual-differences/aging studies show REDUCED linguistic
resources/experience associate with SMALLER, less-discriminating N400 modulation (supporting the inverse
by extrapolation). But **no study was found that directly manipulates amount of world/domain experience
and shows a resulting increase in the SPECIFIC settling-residual discrimination** (Rabovsky-style) in a
matched population. This is a well-motivated extension of adjacent findings, not a demonstrated result.
**Treat "richer corpus -> stronger settling signal" as a hypothesis borrowed by analogy, not a validated
brain finding** -- the richness-sweep experiment is genuinely testing new ground here, which is exactly
why the fairness guards in (3) matter so much.

**Predictive-coding framing generally:** well-established as an active (not fringe) computational
framing in psycholinguistics -- multiple 2024 papers (arXiv:2409.06803; Neurobiology of Language PMC11025650)
and fMRI evidence of hierarchical prediction-error propagation in fronto-temporal cortex during the N400
window support "coherence = low residual after a settling/relaxation process" as a legitimate, current
framing, though still one of several competing computational accounts (surprisal-only, gestalt-change,
hybrid) rather than closed consensus.

## (3) COMPUTATIONAL SETTLING/CONFIDENCE LITERATURE + DESIGN + FAIRNESS GUARDS

**Hopfield energy and settling-confidence (canonical for classical case, Hopfield 1982; Krotov & Hopfield
2016; Ramsauer et al. 2020/2021 "Hopfield Networks is All You Need"):** classical Hopfield settling is
provable monotone energy descent to a fixed point under asynchronous updates; modern (dense/exponential)
Hopfield networks converge in as little as one update for well-separated patterns, with retrieval error
falling exponentially in a separation measure controlled by an inverse-temperature parameter beta. Ramsauer
et al. identify three fixed-point classes -- single-pattern, metastable mixture-of-a-subset, and
global-average -- and **beta (a hyperparameter, not something discovered from data) determines which class
is reached.** This is an explicit, citable construction-determinism trap: "confidence from convergence
class" is partly a knob choice, not purely emergent from the data.

**Resonator networks for VSA factorization (Frady, Kent, Olshausen & Sommer 2020, *Neural Computation*):**
the closest public precedent to our exact mechanism -- iterative unbind-and-clean-up-against-codebook search.
The authors explicitly state the resonator network is **not descending any energy function** (non-symmetric
weights, no Lyapunov guarantee) -- convergence is empirically reliable in a regime, not proven. Documented,
quantitative structure: stability tracks the ratio of (number of codebook items per factor)/(vector
dimension), with a transition around 0.056 and a collapse above ~0.138 as cross-factor noise percolates;
capacity scales quadratically in dimension; **unbalanced codebook sizes across factors measurably hurt
capacity.** A 2026 follow-up (single-study, treat as speculative) explicitly separates outcomes into
correct-convergence / spurious-convergence / non-convergence and shows a cleanup rule that converges FASTEST
also has the WORST reliability (fast convergence != correct convergence) -- **iteration count alone is a
documented trivial/confounded metric unless reported jointly with a correct/spurious breakdown.**

**Attractor-basin stability as a genuine confidence readout (real precedent, but neuroscience not VSA-engineering, both single-study):**
Wang, Falcone, Richmond & Averbeck 2023 (*Nature Neuroscience*) show macaque PFC attractor basin steepness
around a decision state is measurably steeper for consistent (confident) decisions and shallower for
inconsistent ones -- basin sharpness at settling directly indexes behavioral confidence, empirically, in a
biological system. Atiya, Huys, Dolan & Fleming 2021 (*PLOS Comp Bio*) build a related but distinct account
where confidence comes from a **separate integrator population**, not the primary settled state itself --
worth noting as an alternative design (a secondary "how-hard-did-it-work-to-settle" readout rather than
reading confidence off the settled vector directly). No resonator-network paper was found using
residual/energy/iteration-count as an explicit, standalone correctness-confidence score -- the VSA
engineering literature always decodes correctness independently (nearest-codeword match) and treats
convergence dynamics as a separate efficiency metric. **This is the genuine novel-synthesis step in this
design: nobody has published "settling stability as the confidence readout" specifically for VSA/resonator
parse-disambiguation.** Cap P accordingly (novel-synthesis cap 0.50, further deflated below).

### Design sketch: settling-parse-selector

For a genuinely syntax-underdetermined sentence (PP-attachment ambiguity, reversible-thematic-role
sentences, "flying planes"-class structural ambiguity -- NOT sentences grammar already resolves):

1. Enumerate the (small, closed) set of candidate role-assignments/parses.
2. For each candidate, CONSTRUCT its composed vector the identical way (same binding operator, same
   normalization) -- this is the "construction" phase, deliberately including the dispreferred/implausible
   candidate, mirroring CI's over-generation.
3. Run an iterative clean-up/settling dynamic against the codebook (resonator-style unbind-clean-up, or
   Hopfield-style relaxation) for a fixed, pre-registered max-iteration budget.
4. Score each candidate's settled state by **residual-of-change across the last k iterations** (Rabovsky-style
   readout: how much did the state still move at the end), NOT final-state similarity alone and NOT raw norm.
5. Select the candidate with lower residual (more cleanly settled) as the model's preferred reading; compare
   against human norming/gold-preference data for that ambiguity class.
6. Sweep corpus richness (see operationalization below), holding everything else fixed, and check whether
   selection accuracy AND the margin between candidates' residuals grows with richness.

### Fairness / construction-determinism guards (the load-bearing part of this note)

Each guard below is anchored to a specific literature-documented failure mode from axis (3), not invented
in the abstract:

- **G1 -- not a trivial norm artifact.** Normalize every candidate's composed vector and every settled state
  to unit norm before scoring; use a residual/cosine-change metric, never raw activation magnitude, per the
  documented risk that norm/magnitude differences are a cheap confound (flagged generically in the
  resonator/Hopfield literature's emphasis on normalized comparisons).
- **G2 -- not a repackaged one-shot similarity.** Run a ZERO-iteration control (single clean-up pass, no
  settling loop) using the identical codebook and scoring rule. If multi-cycle settling does not outperform
  the single-pass control, the "settling" step is adding nothing beyond the codebook's static similarity
  geometry -- this is a real risk given CI's own literature describes convergence as rapid (few cycles),
  so the signal could collapse to single-pass. This must be reported even if it is a null result.
- **G3 -- must beat a REAL baseline, not a strawman.** The baseline is a one-shot thematic-fit/typicality
  similarity score per candidate (no iteration, no clean-up) -- this is the existing, already-characterized
  mechanism in this program (cf. `research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`'s
  cosine-to-slot-centroid gate). The settling-based selector must beat this baseline by a pre-registered
  margin, not merely differ from chance.
- **G4 -- must-fail control (can HURT).** Two independent must-fail arms: (a) shuffle/randomize the codebook's
  relational structure while keeping its size fixed -- selection accuracy must collapse toward chance; (b)
  invert the scoring rule (select the HIGHER-residual/less-settled candidate) -- this must perform
  significantly WORSE than chance-or-the-normal-rule, not merely "also work" (a signal that "works" no matter
  which direction you read it is not a signal).
- **G5 -- test only genuinely underdetermined items.** Restrict the test set to ambiguity classes where
  syntax alone does not resolve the role assignment (PP-attachment, reversible-thematic sentences,
  coordination ambiguity) -- confirmed via existing psycholinguistic norming corpora with human
  preference/reaction-time data as gold labels. Sentences syntax already resolves are excluded; they would
  let the selector "succeed" by leaning on cues unrelated to the coherence-settling mechanism being tested.
- **G6 -- construction symmetry across candidates.** Each candidate parse must be built with matched
  binding depth, matched atom-frequency profile, and counterbalanced role order across the item set (so
  no candidate has a structural head-start from asymmetric construction) -- directly motivated by Guha &
  Rossi's finding that CI's own equilibrium is initialization-sensitive, and by the resonator literature's
  finding that initialization scheme materially biases which basin is reached.
- **G7 -- capacity-cliff confound isolation (Frady et al. 2020's D/N and 0.056/0.138 thresholds).** Hold
  codebook SIZE and vector dimension N fixed and identical across every richness level in the sweep, and
  report the D/N ratio as a covariate confirmed to stay well below the 0.056 stability transition and the
  0.138 collapse threshold throughout. This is essential: if richness were operationalized as "bigger
  vocabulary," any observed effect could just be the documented capacity-cliff artifact, not a genuine
  richness-sharpens-coherence effect.
- **G8 -- convergence-quality reporting, not iteration-count alone.** Per the 2026 cleanup-rule finding
  (fastest-converging rule = worst reliability), always report the correct/spurious/non-convergent
  breakdown alongside any iteration-count or residual number -- a richness level that "converges faster"
  but converges to the WRONG candidate more often must be flagged as a regression, not a win.
- **G9 -- beta/temperature is not free to tune per richness level.** If the settling dynamic exposes an
  inverse-temperature or step-size hyperparameter (per Ramsauer et al.'s finding that beta determines which
  fixed-point class is reached), FIX it globally across the entire sweep and pre-register the value before
  looking at results -- otherwise "richer codebook wins" could just be a re-tuned hyperparameter dressed up
  as a richness effect.

### Operationalizing "corpus richness" fairly

Given G7, richness must NOT be vocabulary count or dimensionality. The fair operationalization: **fix the
codebook's vocabulary set, size, and dimension N identically across all richness levels; vary only the
FRACTION OF CORPUS TEXT used to fit the relational/co-occurrence structure that gives codebook vectors their
similarity geometry** (e.g. thin = codebook fit from a small corpus-token fraction, producing near-orthogonal/
unstructured relational geometry; rich = codebook fit from the full corpus, producing well-formed thematic-fit
structure). Use >=4 richness levels (not just thin-vs-rich endpoints) so a genuine monotonic trend can be
distinguished from noise. Same test sentences, same mechanism, same seed policy, same max-iteration budget,
same beta/hyperparameters at every level -- richness (relational-structure quality) is the only thing that
moves.

## Cheap decisive test

~30-50 genuinely two-way-ambiguous sentences drawn from existing psycholinguistic norming sets (PP-attachment
preference corpora, reversible-thematic-role stimuli) with human gold-preference labels. Construct both
candidates per item per G6; run the settling dynamic at >=4 richness levels per G7-G9; score selection
accuracy vs. gold labels for: (a) the settling-residual selector, (b) the zero-iteration control (G2), (c) the
one-shot thematic-fit baseline (G3), (d) the shuffled-codebook must-fail control (G4a), (e) the inverted-score
must-fail control (G4b). Report accuracy and the correct/spurious/non-convergent breakdown (G8) at every
richness level.

## Falsifiable predictions

**HARD-PASS (all must hold, pre-registered):**
1. Settling-residual selector beats the one-shot thematic-fit baseline (G3) by >=10 percentage points
   selection accuracy on held-out ambiguous items, replicated across >=2 random seeds.
2. Settling-residual selector beats the zero-iteration control (G2) by a non-trivial margin -- confirming the
   settling loop itself adds information beyond static codebook lookup.
3. Both must-fail controls (G4a shuffled-codebook, G4b inverted-score) collapse to at-or-below-chance
   accuracy -- confirming the signal is not construction-artifactual.
4. Selection accuracy AND candidate-residual margin show a monotonic (or at minimum, Spearman rho >= 0.6,
   p<0.05) increasing trend across the >=4 richness levels, with D/N ratio confirmed flat/covariate-controlled
   (G7) -- this is the specific test of "richer corpus sharpens the settling/coherence signal."

**HARD-FAIL (any one is sufficient to refute):**
1. Settling-residual selector does not beat the zero-iteration control (G2) -- i.e. settling is just relabeled
   static similarity; the "settling" framing adds nothing mechanistically new.
2. Either must-fail control does NOT degrade to chance (G4) -- the readout is a construction artifact,
   not a genuine coherence signal.
3. Richness sweep shows no significant trend (|rho| < 0.3, or non-monotonic with no plausible capacity-cliff
   explanation after G7 covariate check) -- directly refutes "richer corpus -> stronger settling signal" for
   this mechanism, independent of the general corpus-richness question already flagged as refuted elsewhere
   in this arc for other mechanisms.
4. Fastest-converging richness level is also the least-accurate (mirrors the 2026 cleanup-rule gotcha) without
   the G8 breakdown resolving it -- signals the whole convergence-speed framing is unreliable here.

## Cross-thread synthesis

- Directly extends `research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`'s finding that the brain
  runs (at least) two coherence mechanisms -- a graded N400-style prediction-error signal and a discrete
  P600-style reanalysis flag -- and that the existing first-draft `schema_fit_gate()` implements only a
  crude, STATIC analog of the graded one (fixed per-slot centroid, flat global-percentile threshold). This
  settling-parse-selector is a candidate upgrade path: it replaces the static centroid-similarity score with
  a genuine iterative-settling residual, directly answering that drill's call for something closer to "the
  CURRENT, growing situation-model" rather than a fixed reference.
- Relevant to the `SYNTHESIS_platform_maturity_and_the_missing_learning_loop_2026-07-20.md` crux
  (contrastive predictive coding over rival hypotheses vs. real exogenous data, currently HARD_FAIL pending
  forensic audit per the backup doc). This settling-parse-selector is a DIFFERENT mechanism -- a decode-time
  disambiguation/confidence readout via attractor stability, not a train-time contrastive-learning signal --
  but it is diagnostically useful regardless of the forensic audit's outcome: if a settling-stability signal
  cannot even discriminate genuinely-ambiguous parses at decode time (G1-G9 satisfied), that is independent
  evidence that "coherence," as currently operationalized in this program, may be a weak readout at this
  maturity level generally -- relevant to distinguishing REAL null vs TEST-ARTIFACT for the pending forensic
  question. If it CAN discriminate, it is a candidate replacement/complement error signal for the stalled
  CPCL-v2 loop (a coherence-settling contrast instead of, or alongside, contrastive-prediction-against-real-text).
- The single most load-bearing external precedent for the whole design is Rabovsky, Hansen & McClelland
  (2018) -- it is the only place in the literature where "residual of change during settling" is explicitly,
  quantitatively operationalized as a coherence/plausibility readout and validated against real ERP data
  across many paradigms. Everything else (Hopfield confidence, resonator convergence, CI-as-attractor) is
  analogy-level support, not direct precedent, and should carry the full 0.15-0.25 deflation.

## Substrate-product implications

A validated settling-parse-selector would give the product a **transparent, inspectable disambiguation
step** for role-assignment ambiguity -- a user-facing "why did it read the sentence this way" trace showing
candidate parses and their settled-residual scores, which is exactly the auditable-glass-box value
proposition (never framed as publication-worthy; framed as a concrete comprehension-quality and
explainability feature). If the richness-sweep HARD-PASSes, it also gives a principled, testable answer to
"does feeding the substrate more text actually make its judgment sharper" for THIS mechanism specifically --
a narrower, falsifiable version of the broader "more corpus" question already refuted elsewhere in this arc
for other mechanisms; a positive result here would need to be reconciled with, not assumed to override, that
prior refutation.

## Citations (verified count: 27 distinct sources cited across the three lit-scans, cross-checked for
canonical-vs-speculative status by the synthesizing agent)

Construction-Integration: Kintsch & van Dijk (1978, *Psych Review* 85); Kintsch (1988, *Psych Review* 95(2));
Kintsch (1998, *Comprehension: A Paradigm for Cognition*, Cambridge UP); Wharton & Kintsch (1991, AAAI
Working Notes); Guha & Rossi (2001, *J. Math. Psych.* 45(2)); Sanjose, Vidal-Abarca & Padilla (2006,
*Discourse Processes* 42(1)); McClelland, Mirman, Bolger & Khaitan (2014, *Cognitive Science* 38(6));
Rumelhart & McClelland (1986, PDP).

N400/P600/predictive coding: Kutas & Federmeier (2011, *Ann. Rev. Psych.* 62); Federmeier (2007,
*Psychophysiology* 44(4)); Federmeier, Wlotko, De Ochoa-Dewald & Kutas (2010); Rabovsky, Hansen & McClelland
(2018, *Nature Human Behaviour* 2); Rabovsky (2019, CCN/escholarship); Michaelov, Coulson & Bergen (2022,
IEEE TCDS); Kaan (P600 review); PLOS ONE 2014 (PMC3948820); PMC8419728; PMC11655752; chess-ERP expertise
study (ResearchGate 248383059); musical-training ERAN study (PMC3542524/PubMed 23335905); Qi et al.
native-language N400/P600-predicts-learning (PMC5885768); comprehension-ability N400 subcomponents (2025,
CABN Springer); Munding et al. (2025, *Psychophysiology*); arXiv:2409.06803 (2024); PMC11025650 (2024);
PubMed 36130089 (predictive coding fMRI).

Attractor/Hopfield/resonator: Hopfield (1982, PNAS); Krotov & Hopfield (2016, NeurIPS 29); Demircigil et al.
(2017); Ramsauer et al. (2020/2021, arXiv:2008.02217, ICLR); Frady, Kent, Olshausen & Sommer (2020, *Neural
Computation* 32(12), arXiv:2007.03748 + arXiv:1906.11684); Frontiers 2026 cleanup-rule comparison
(single-study); Wang, Falcone, Richmond & Averbeck (2023, *Nature Neuroscience* 26); Atiya, Huys, Dolan &
Fleming (2021, *PLOS Comp Bio* 17(7)); Elidan, McGraw & Koller (2006, residual belief propagation).

P_deflated for the overall design (novel-synthesis cap applied): **0.35** -- mechanism/readout legs
well-grounded (CI settling, Rabovsky residual-as-coherence), richness-sharpens leg weakly grounded (analogy
only), VSA-specific settling-as-confidence combination is genuinely novel synthesis with real documented
construction-determinism traps (G1-G9) that a naive implementation would likely fall into.
