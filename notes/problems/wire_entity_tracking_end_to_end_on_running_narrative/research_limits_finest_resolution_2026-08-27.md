# Finest-resolution drill: do we understand the LIMITS and why they are what they are?

Solver problem: `wire_entity_tracking_end_to_end_on_running_narrative`. Owner asked for a last, finest-
resolution brain-foundational drill on the three measured limits. Dispatched via `research` (4 lit-scans).
Findings persisted verbatim-in-substance below (full sub-agent reports were long; load-bearing content kept).
Each verdict tagged GENUINE-LIMIT / MISSING-MECHANISM / PINNED / PLAUSIBLE-BUT-UNTESTED. ASCII only.

## LIMIT A -- PREDICTION NULL: GENUINE-LIMIT (naive entity-history recurrence was never the brain's mechanism)

- Narrative prediction is driven by (ii) EVENT SCHEMAS/SCRIPTS and (iii) VERB-DRIVEN THEMATIC FIT / selectional
  preference -- one "generalized event knowledge" system pooling regularities across a LIFETIME of experience,
  activated by verb+role+situation, and EXPLICITLY ENTITY-AGNOSTIC. Not (i) a single character's own accumulated
  object/action history (what we tested).
- Key citations (verified): Bower/Black/Turner 1979 (*Cog Psych*, scripts structure expectation); Baldassano/
  Hasson/Norman 2018 (*J Neurosci*, schema patterns in mPFC/PMC that GENERALIZE ACROSS character identity --
  direct quote: schematic event patterns "generalized across stories, subjects, and modalities"); Altmann &
  Kamide 1999 (*Cognition*, verb selectional restriction drives anticipatory saccades); McRae et al.; Metusalem
  et al. 2012 (*JML*, N400 to event-consistent words -- generalized event knowledge pre-activates, not
  entity-specific content); Cohn & Paczynski 2013 (*Cog Psych*, it is Agent-ROLE occupancy, not character
  identity, that carries predictive weight); Chambers & Jurafsky 2008 (narrative chains -- even this closest
  "entity-continuity" analog uses coreference only as a SAMPLING KEY over a huge corpus, not one instance's
  idiosyncratic history).
- Coreference/entity-tracking in this literature serves RETRIEVAL, CONSISTENCY-MONITORING, and referential
  continuity ("who is talked about next" -- Centering's Cb/Cp; Zwaan et al. 1998: protagonist-continuity is
  MONITORED, a reading-time cost, not an anticipation signal) -- NOT content-anticipation.
- Also a statistical-power reason: a single character's in-story history is single-digit instances vs the
  schema system's lifetime aggregate.
- VERDICT: GENUINE-LIMIT for the mechanism tested. Confidence ~0.55-0.65 that a SCHEMA-ROLE-conditioned
  mechanism (below) would help; ~0.25-0.30 that it is an unconditional limit; ~0.10-0.15 inconclusive.
- **MISSING MECHANISM (what we leave on the table): SCHEMA-ROLE-conditioned prediction, NOT entity-content.**
  The faithful entity contribution is the entity's CURRENT abstract schema-ROLE / slot-type, dynamically
  updated -- and oracle coreference does NOT supply the role (it tells you WHICH entity, not WHICH role).
  Chen/Lu/Beukers/Baldassano/Norman 2021 (*PeerJ*): role-filler binding generalizes to novel fillers ONLY
  when role and filler are kept SEPARATE -- folding a character's history into its identity is exactly the
  design that fails to generalize. This is a SEPARATE ORGAN (verb->role->typical-next-argument / event schema),
  not the coreference channel this problem composes; it needs role/schema tagging on literary text not more
  available than what we tested. Does NOT change the SOLVED verdict.

## LIMIT B -- ATTRIBUTION-vs-PREDICTION DISSOCIATION: NEURALLY SUPPORTED, with an active-harm caveat

- Item-specific episodic binding (hippocampal/MTL) vs generalized schema/verb-driven expectation (mPFC, cortex,
  cerebellar forward models) are treated as at least partly separable: Preston & Eichenbaum 2013 (*Curr Biol*);
  Gilboa & Marlatte 2017 (*TiCS*, schemas); van Kesteren et al. 2012 (SLIMM); Kumaran et al. 2009 (*Neuron*);
  Knowlton & Squire double dissociation (item recognition vs implicit grammar/generalization).
- DIRECT patient evidence matching our pattern: Brown-Schmidt/Duff-lab 2020 (*Neuropsychologia*) -- bilateral
  hippocampal amnesia SPARES online anticipatory/semantic-activation eye-movements despite profound episodic
  deficit. Cerebellar forward model for prediction: Lesage et al. 2012 (*Curr Biol*, rTMS delays anticipatory
  fixations) -- anatomically distinct from MTL.
- CAVEAT (honest): the split is NOT anatomically clean. Hippocampus itself carries forward-looking predictive
  content (Hindy/Turk-Browne 2016; Kok/Turk-Browne 2018), and Barron/Auksztulewicz/Friston 2020 (*Prog
  Neurobiol*) argue recall and prediction are two MODES of the SAME hippocampal machinery. So entity info
  SHOULD be able to help prediction when genuinely predictive; a result where correct entity info ACTIVELY
  HURTS is not the literature's default.
- The best-supported account of active harm is CUE-OVERLOAD / retrieval-interference (Van Dyke & McElree 2006):
  extra competing cues degrade the useful signal. Our measurement ADDS the entity cosine to the gist cosine, so
  a noisy cue can only dilute an already-at-chance signal -- consistent with cue-dilution, NOT a strong novelty
  claim. PLAUSIBLE-BUT-UNTESTED as the exact mechanism; flagged "diagnose before building downstream."
- The explicit claim that coreference literature separates "retrieval" from "anticipation" as named functions
  was NOT found as a direct citation -- SPECULATIVE-TO-PLAUSIBLE, inferred from Gernsbacher/Kintsch.

## LIMIT C -- FAN EFFECT: PINNED; faithful fix is SPARSIFICATION, not a pointer

- DG does sparse conjunctive expansion recoding (~1-5% active, k-WTA); CA3 does attractor pattern-completion
  (Marr 1971; O'Reilly & McClelland 1994; McClelland/McNaughton/O'Reilly 1995 CLS).
- Norman & O'Reilly 2003 (the most directly relevant) EXPLICITLY names "cue overload effects and fan effects"
  and states the hippocampal signal "can even decrease due to interference between all of the similar memory
  traces"; pattern separation reduces the SLOPE of degradation, does not zero it.
- Anderson 1974 / ACT-R fan effect is a process-level (spreading-activation, retrieval-time), representation-
  agnostic, NON-neural account -- our bundled-vector fan is architecturally closer to the hippocampal/dense-
  superposition family.
- SYNTHESIS: an index/POINTER alone fixes cross-entity lookup, NOT within-register superposition crosstalk -- a
  "dense bundle + pointer" would STILL fan. Faithful redesign = sparse conjunctive encoding at EACH event +
  attractor retrieval; after sparsification residual degradation tracks item-SIMILARITY, not item-COUNT.
- (Numeric flag: a "~40x EC->DG expansion" figure from one fetch was contradicted; correct ~5-6x.)

## LIMIT D -- GRADED activation-weighted competition: the BRAIN-CORRECT SHAPE (interior optimum)

- Divisive normalization (Carandini & Heeger 2012, *Nat Rev Neurosci*): resp_i = a_i^n / (sigma^n + sum_j a_j^n).
  The exponent n nests our three arms: n->0 UNIFORM, n~1 GRADED, n->inf HARD ARGMAX. Our result (GRADED beats
  BOTH uniform and argmax) = an INTERIOR-n optimum -- exactly what normalization theory predicts. PINNED for
  the SHAPE (competitive, activation-proportional, spanning the three regimes as one parameter).
- Luce's choice axiom (1959) is formally continuous with softmax (PINNED) and is the standard account of
  MEMORY-RETRIEVAL competition (SAM; Raaijmakers & Shiffrin). Cue-based parsing (Lewis & Vasishth 2005) pins
  PARALLEL multi-candidate activation (not serial, not instant commit). Nref (real, replicated; PMC9784143) =
  graded ambiguity-maintenance cost scaling with bias and working-memory capacity.
- NOT pinned: the exact functional form (softmax vs another monotonic competitive function) and the
  temperature/sharpness -- every source treats it as fitted per area/task; no biological constant to import.
  Our fitted temperature is the correct approach. Confidence ~0.65.
- EMPIRICAL CONFIRMATION (our temperature sweep, 100 docs): SOFT pron-recall traces a clean INVERTED-U --
  hard-argmax limit (temp->0) 0.1783 -> peak temp~2.0 0.2084 -> back through hard (temp 4.0) -> toward the
  uniform-flat limit (temp 20 = 0.1386 ~ UNIF 0.1322). Both extremes worse than intermediate graded; SOFT>UNIF
  at every temp. This IS the divisive-normalization interior-optimum, measured -- strong support for the SHAPE.
- Race/DDM models (Usher & McClelland 2001) are winner-take-all PER TRIAL (graded only in the across-trial
  distribution) -- a disanalogy with a single-step fractional allocation, which is closer to a probabilistic-
  population-code readout.

## LIMIT E -- ACT-R-vs-RECENCY null: likely a DILUTION ARTIFACT (Hobbs' easy-majority) -- and we TESTED it

- Most pronouns are trivially unambiguous: Hobbs 1978 -- >50% single-candidate; on the multi-candidate subset
  pure syntax still gets 82%; genuinely-hard residual ~10-20%. Modern hard-pronoun benchmarks (Winograd/KnowRef)
  crater SOTA from ~90% aggregate to ~53%. The ACT-R content/associative term earns its keep only where
  base-level (recency) activation leaves candidates close (Van Dyke & McElree cue-overload). A whole-document
  aggregate is dominated by easy cases where recency and ACT-R agree -> subgroup dilution (Simpson-adjacent).
- ACTIONABLE (the drill's single most decisive next step): stratify the pipeline output by an independent
  difficulty proxy (candidate count) -- if the ACT-R>recency gap reappears in the hardest bucket, the null was
  dilution; if not, recency genuinely suffices downstream. "A re-slicing of data you already have."
- WE RAN IT (arm-independent difficulty = # of gold gender/number-compatible prior entities at the pronoun,
  bucketed easy=1 / med=2 / hard=3+). RESULT = INCONCLUSIVE, for a nameable reason: the proxy SATURATED --
  easy_1 n=25, med_2 n=47, hard_3plus n=9006 (of 9078). Long literary docs accumulate many entities and gender
  is often unknown (compat True by default), so the candidate-count proxy cannot isolate an easy majority on
  narrative (the opposite of Hobbs' scripted-corpus easy-majority). Within the dominant 3+ bucket ACT-R edges
  recency +0.0133 [0.0031,0.0238] under an ITEM bootstrap, but that equals the overall +0.0129 and the
  "separation" is a bootstrap-unit artifact (item vs doc-clustered), not a difficulty effect. So dilution is
  NEITHER confirmed nor refuted; honest verdict stays "ACT-R ~ recency downstream (doc-clustered NOT
  separated)". Follow-up: referential-distance or gender-DISTINCT (known-gender) difficulty proxy.

## NET (owner's question: is it truly brain-foundational, and do we understand the limits?)

- ATTRIBUTION win: brain-faithful and neurally grounded (reactivation pinned; dissociation supported).
- PREDICTION null: UNDERSTOOD as a GENUINE limit -- coreference feeds retrieval, not anticipation; the brain
  predicts via entity-agnostic generalized event knowledge; the entity's real predictive contribution (if any)
  is its SCHEMA-ROLE, a separate organ we did not build. Not a bug.
- FAN effect: UNDERSTOOD (dense-superposition interference); faithful fix specified (sparsify, don't pointer).
- GRADED binding: brain-correct SHAPE (divisive-normalization interior optimum), a concrete win.
- ACT-R-vs-recency: tested for dilution (see SOLVED) rather than left as an open deflation.
