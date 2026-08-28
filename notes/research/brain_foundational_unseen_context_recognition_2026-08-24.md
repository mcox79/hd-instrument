# Brain-foundational research drill: unseen-context concept recognition

Filed by: research sub-agent (Opus synthesis over 2 web-verified Sonnet lit-scans)
Date: 2026-08-24
Scope: research-only. No edits to hdlab/, preregs/, plan.json, STATUS.md, or any SOLVED.md.
Triggered by: owner-authorized brain-foundational drill on "recognize a KNOWN concept from a
linguistic context it has NEVER directly co-occurred with" (unseen-context / paradigmatic recognition).

Discipline note: lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis capped
at 0.50; hard-fail thresholds pre-registered below). Every claim is marked PINNED-BY-EVIDENCE
(a real neural/behavioural finding) or SPECULATIVE/OUR-INVENTION. "What the brain does" is kept
separate from "what is computationally convenient."

---

## (1) PLAIN-LANGUAGE ANSWER (for the owner) -- the optimal brain-foundational way to give the reader this capability

The best brain-like way to let the reader recognise a familiar word inside a sentence unlike any it
saw that word in before is to give it TWO word-meaning maps and, above all, a smart rule for deciding
which map to trust for each individual word.

- **Map one** is a big, ready-made "words that keep similar company are similar" map, built once,
  offline, from a large body of ordinary text. This is the computer's stand-in for the lifetime of
  language a real brain soaks up before it ever has to answer a hard question. We already measured
  that this map answers the hard questions well.
- **Map two** is the small map the reader builds from its own reading. We already measured that on
  words it has actually read about, this small map is *just as good as the big one* -- and near
  useless on words it has not read about yet.

The mistake we keep making is **blending the two maps at a fixed strength**. The brain never does
that. The brain leans on whichever source has real evidence about the specific thing in front of it,
and when two sources flatly disagree it **picks one** rather than averaging them into mush. So the
reader should use its own map for the words it has genuinely read about, fall back to the big
ready-made map for everything else, and weight each source by *how much it actually knows about that
particular word*.

Concretely: build the big map offline (this is allowed -- it is a plain inspectable lookup table, not
a live AI), keep growing the small map from reading, and put a **confidence-based "which one do I
trust here" switch** between them. That switch -- not more reading, and not a cleverer single map --
is the missing piece. It is also, on the neuroscience, the single genuinely open and hard part; the
two maps themselves are settled.

---

## (2) THE BIOLOGY, PER QUESTION, WITH CITATIONS AND PINNED/SPECULATIVE LABELS

### Question A -- the arbitration / combination rule (highest priority, the genuinely open part)

**The measured problem restated.** Fixed-weight blending of a distributional/semantic signal with a
grounded or frequency-prior signal has a *landed track record of hurting* on our tasks: the flagship
`reader_meaning_channel` result shows a strong frequency prior SWAMPS a weaker-but-correct grounded
channel (channel alone 0.4811 above chance on subordinate senses; channel + prior 0.1415, below
chance); the c3 fusion result shows fusion *works when the two channels are comparable* and *fails
when one dominates*. So the real question is not "what weights?" but "what does the brain do INSTEAD
of fixed weights?"

The neuroscience gives a coherent, four-part answer, and the core of it is PINNED:

- **Reliability-weighted (inverse-variance) cue combination.** [PINNED] Ernst & Banks 2002 (Nature)
  and Alais & Burr 2004 (Curr Biol): when the brain combines two estimates of the same thing, it
  weights each by its reliability, weight_i proportional to 1/variance_i, and the combined estimate
  has lower variance than either cue alone. Humans match this near-exactly, and the weighting shifts
  continuously as one cue is degraded. **The weight is a property of the cue's current reliability,
  not a fixed constant** -- which is precisely the property our fixed-weight rule lacks.

- **Reliability IS gain; addition IS inference.** [PINNED-mechanistic] Ma, Beck, Latham & Pouget 2006
  (Nat Neurosci): with Poisson-like population codes, a cue's reliability (Fisher information, inverse
  variance) is carried by the *amplitude/gain* of its population response. Therefore simply *adding*
  two population responses, r_comb = r_1 + r_2, automatically produces the inverse-variance-weighted
  optimal combination -- no explicit weight computation, no division. **This is the crucial
  build-relevant fact: you do not compute weights and multiply; you scale each source's contribution
  by its own evidence/confidence and add.** A source with little evidence about a term contributes a
  small-amplitude vote and is automatically down-weighted.

- **When to fuse vs when to SEGREGATE (defer to one).** [PINNED-descriptive] Kording, Beierholm, Ma,
  Quartz, Tenenbaum & Shams 2007 (PLoS ONE): the brain runs causal inference over whether two cues
  share a common cause. Final estimate = p(common)*fused + p(separate)*segregated. When the cues
  disagree strongly, p(common) collapses and the brain STOPS fusing -- it reports the cues
  separately, effectively deferring to the more reliable single source. **This is the direct
  biological account of why fixed-weight blending fails: blending is only correct when the sources
  agree; when they conflict the brain switches to picking one, not averaging.**

- **A concrete "which system to trust" circuit.** [PINNED] Lee, Shimojo & O'Doherty 2014 (Neuron):
  reliability-based arbitration between model-based and model-free learning. Each system carries a
  reliability signal tracked from the recent magnitude of its own prediction errors; a comparison of
  the two reliabilities, computed in inferior lateral prefrontal / frontopolar cortex, sets how much
  each system drives behaviour. Notably the arbitration is ASYMMETRIC -- it modulates the less
  reliable (habitual) system DOWN rather than symmetrically boosting the other. This is the closest
  published analog of the switch we need, at circuit level.

- **The system-level division of labour that makes the switch pay off.** [PINNED] Complementary
  Learning Systems: McClelland, McNaughton & O'Reilly 1995 (Psych Rev) and Kumaran, Hassabis &
  McClelland 2016 (Trends Cog Sci). A fast hippocampal system stores specific episodes with sparse,
  pattern-separated codes; a slow neocortical system extracts generalised statistical/semantic
  structure by interleaved learning. The 2016 update adds goal-dependent replay, fast neocortical
  learning of schema-congruent material, and hippocampal recombination for generalisation. **This
  maps one-to-one onto our measured SEEN/UNSEEN split**: the learned tier (fast/specific) owns
  material we have read; the consolidated foundation (slow/generalised) owns the novel/unread.

- **The representation the switch operates over.** [PINNED-at-core, CONTESTED-at-edges] ATL
  hub-and-spoke: Patterson, Nestor & Rogers 2007 and Lambon Ralph, Jefferies, Patterson & Rogers 2017
  (both Nat Rev Neurosci). The anterior temporal lobe is a transmodal hub that binds
  modality-specific spokes (vision, sound, action, *language/distributional statistics*) into
  coherent concepts; evidence from semantic dementia (correlated cross-modal, item-specific deficits).
  The "graded hub" refinement holds the hub computes convergent NON-LINEAR multimodal structure, not a
  weighted sum -- which is why it can generalise beyond any single spoke. That distributional/verbal
  experience is *one spoke among several* is PINNED-by-secondary-source (I could not confirm exact
  primary wording; flagged).

- **Precision-weighting as the same idea in predictive coding.** [SPECULATIVE/interpretive] Feldman &
  Friston 2010: prediction errors are weighted by their precision (inverse variance) before
  propagating up, with precision proposed as synaptic gain under neuromodulatory control. Coherent and
  influential, but direct causal evidence for "precision = synaptic gain" is thinner than the
  population-code cue-integration work, and the framework is explicitly contested. Use as
  corroboration, not as a load-bearing pin.

**Synthesis of A (this is the answer to "what decides which source to trust for a given
word/context").** The brain trusts each source *in proportion to that source's own evidence for the
specific item*, implemented as gain (Ma 2006) and validated behaviourally as inverse-variance
weighting (Ernst & Banks 2002); and when sources conflict beyond a threshold it *segregates* and
defers to one rather than averaging (Kording 2007), via an explicit reliability-comparison circuit
(Lee 2014). Fixed weights are wrong because they are blind to per-item evidence. The mechanism we are
missing is not a better single map -- it is a **per-item, evidence-scaled fuse-or-defer switch**.
[This synthesis is OUR-INVENTION-UNDER-TEST as applied to our task; its component neural findings are
PINNED.]

### Question B -- learning objective for the distributional tier (predictive vs count)

- **Skip-gram IS implicit count factorisation.** [Canonical; cited-from-knowledge, not re-verified
  this session] Levy & Goldberg 2014 (NeurIPS, "Neural word embedding as implicit matrix
  factorization"): skip-gram-with-negative-sampling implicitly factorises a shifted PMI matrix. So the
  "predictive" objective (skip-gram) and the "count" objective (PPMI+SVD) are *not two different kinds
  of knowledge* -- they optimise closely related targets.
- **Count vs predict is mostly hyperparameters.** [Canonical] Levy, Goldberg & Dagan 2015 (TACL) and
  Baroni, Dinu & Kruszewski 2014 (ACL, "Don't count, predict!"): predict-based methods look better out
  of the box, but with matched hyperparameters count-based PPMI/SVD performs comparably. **This
  corroborates our own measured result** that self-built PPMI+SVD EQUALS the supplied embedding on
  material actually read (SEEN 0.338 vs 0.336). Our objective is not the handicap.
- **Is cortex predictive or Hebbian?** [PINNED-framework] Predictive coding (Rao & Ballard 1999, Nat
  Neurosci) argues cortex is fundamentally predictive -- it learns to predict its inputs and
  propagates errors; this favours a predictive/next-item objective as more brain-faithful. But
  spike-timing-dependent plasticity is Hebbian and co-occurrence-like, so a count/PPMI objective is
  ALSO biologically grounded. Given Levy-Goldberg equivalence, the two are near-interchangeable in
  what they extract.
- **Sample efficiency at limited data.** The equivalence is asymptotic; at small data the weighting
  and smoothing matter. The measured fact that our count-based tier already matches supplied on read
  material means the count objective is *sample-efficient enough for the read regime*. The UNSEEN gap
  is coverage of unread terms, not objective choice.

**Synthesis of B.** The learning objective is NOT the bottleneck. Count (PPMI+SVD) and predictive
(skip-gram) are mathematically near-equivalent (Levy-Goldberg) and our count tier already matches the
supplied map where it has data. A predictive objective would be marginally more brain-faithful
(predictive coding) but the measured evidence says it will not close the UNSEEN gap, which is a
data/coverage problem, not an objective problem. **Do not spend the primary effort here.**

### Question C -- data / developmental bootstrapping (how a child does it with far less text)

- **Children hear far less than 6B tokens.** [Canonical] Order-of-magnitude estimates (Hart & Risley
  1995 and later corpora) put child-directed speech at a few million to low-tens-of-millions of words
  per year; by age ~6, tens of millions of words -- roughly 100-600x LESS than GloVe's 6B, but also
  roughly 100x MORE than our ~0.3-0.5M-token read corpus.
- **Child-scale LMs are a measured bound.** [Canonical] The BabyLM Challenge (Warstadt et al. 2023,
  CoNLL) asks how competent an LM can be trained on ~10M-100M words (child-scale). Answer: with the
  right inductive biases/curriculum, surprisingly competent -- but still below large-corpus models on
  many tasks. This BOUNDS the self-build question: child-scale is ~10-100M words; we are ~100x below
  even that.
- **Sample-efficiency multipliers the brain/child uses, and whether each is admissible for us:**
  1. **Morphology / subword composition** [Canonical: Bojanowski et al. 2017, fastText] -- an unseen
     inflected/derived form inherits from its morphemes; children generalise morphologically. This
     multiplies effective coverage with NO extra text. NOTE the double edge: STATUS Q117 shows our
     spelling floor was ~78% morphological leakage, so morphology is real signal that must be handled
     deliberately (as a coverage mechanism, not smuggled into a floor).
  2. **Replay / consolidation** [PINNED framework: McClelland 1995; Kumaran 2016; Tononi & Cirelli
     synaptic-homeostasis] -- replaying stored episodes lets neocortex extract structure from FEWER
     real exposures. Computationally this is multi-epoch / interleaved training over the read corpus,
     which embedding training already does. Schema-congruent material consolidates fast (Tse et al.
     2007). A genuine sample-efficiency lever.
  3. **Cross-situational learning** [Canonical: Yu & Smith 2007] -- meaning inferred from
     co-occurrence across situations. Relevant to grounding, less to distributional retrieval.
  4. **Structured-knowledge retrofitting** [Canonical: Faruqui et al. 2015, NAACL] -- sharpen a
     small-corpus embedding toward an owned lexical graph, substituting structure for corpus volume.
     CRITICAL measured caveat: retrofitting/teaching toward the GROUNDED (perceptual) graph HURTS
     retrieval (our `teach_the_self_built_space` REFUTED result, 3 mechanisms, monotone worse).
     Retrofitting toward a DISTRIBUTIONAL / free-association graph is a DIFFERENT and UNTESTED lever;
     the relational-KB path is separately measured unpromising (KB_BELOW_FLOOR; WordNet oracle 0.0365
     under a partial cue).

**Synthesis of C.** The realistic minimal-experience story is NOT "read 6B tokens." It is: small
corpus + morphological/subword composition (coverage) + replay/multi-epoch consolidation (efficiency)
+ possibly retrofitting toward a distributional graph (volume substitute). BUT the measured priors are
cautionary -- self-built at 20k is far below the UNSEEN floor, and grounded-graph retrofit hurt. The
honest bound is that a *pure*-UNSEEN self-built map on our ~0.3-0.5M-token corpora almost certainly
cannot reach the floor; child-scale (10-100M words) is the target, and we are ~100x short. Treat the
sample-efficient self-build as a SECONDARY, longer-horizon track.

### Question D -- is supplying a large distributional foundation the right call, or is a genuinely different mechanism missing?

- **The measured evidence supports SUPPLY as the working answer for the UNSEEN regime.** A supplied
  large distributional embedding (GloVe-class, glass-box, non-LLM) clears the floor CI-separated 3/3;
  nothing self-built does. Importing a static offline co-occurrence embedding is explicitly admissible
  under the project's FOUNDATION rule, and it is the honest computational analog of the *consolidated
  cortical semantic prior* a brain acquires over a lifetime of language exposure (CLS slow neocortical
  tier; ATL distributional spoke). [PINNED that language is a spoke and that a lifetime prior exists;
  SPECULATIVE that a STATIC LOOKUP TABLE is the faithful FORM -- the brain computes the hub
  dynamically, it does not store frozen vectors.]
- **Is it the optimum?** Two honest caveats.
  1. The brain's value is not the static table; it is the *dynamic hub* that reweights spokes per
     item (Question A). So the foundation is the right SPOKE but the missing organ is the HUB. A
     foundation wired in WITHOUT a reliability-weighted hub would repeat the fixed-weight failure.
  2. Genuinely different candidate mechanism: **episodic recombination / hippocampal pattern
     completion** (Kumaran 2016) -- recognise a concept in a novel context by pattern-completing from a
     similar remembered episode. [CONTESTED as a general mechanism.] But by construction it needs a
     stored episode of the concept, which the *pure*-UNSEEN items lack; so it helps the SEEN regime,
     not the pure-UNSEEN one. The other candidate, relational/graph-structured semantic memory, is
     already measured unpromising here (KB_BELOW_FLOOR).

**Synthesis of D.** Supplying a large static distributional foundation IS the right brain-foundational
call for the UNSEEN regime -- necessary, admissible, and measured to work. But the OPTIMUM is not
foundation-alone; it is foundation-as-a-spoke inside a reliability-weighted hub (Question A) that lets
the learned tier own SEEN and the foundation own UNSEEN. There is no evidence for a single different
mechanism that beats "large distributional foundation + reliability-weighted hub." The sample-efficient
self-build (C) is a real but low-probability volume-substitute, and episodic recombination addresses a
different sub-regime (SEEN), not the pure-UNSEEN gap.

---

## (3) RANKED, IMPLEMENTABLE RECOMMENDATIONS (glass-box; each with mechanism / neuroscience / build / test)

Ranking is by `P(brain-faithful AND addresses the named-open bottleneck) x P(measurably moves the
task)`. Calibration penalty applied.

### RANK 1 -- Reliability-weighted (gain-scaled) fuse-or-defer hub between the supplied foundation and the learned tier. [P_deflated ~= 0.40]

- **The mechanism (glass-box, explicit).** For a cue context and a candidate term, score by
  `score(cand) = SUM_over_sources r_s(term) * cos_s(cand, cue)` where each source s in
  {learned PPMI+SVD tier, supplied distributional foundation} contributes scaled by its own per-item
  reliability r_s(term):
  - `r_learned(term)` = a saturating function of how many contexts the substrate has actually read
    for `term` (e.g. `n/(n+k)`), so it is ~1 for well-read terms and ~0 for unread ones.
  - `r_supplied(term)` = coverage indicator (in-vocab), optionally scaled by corpus frequency.
  - PLUS a **segregation gate** (Kording 2007): if the two sources' top-k candidate rankings disagree
    beyond a threshold (a cheap rank-overlap statistic standing in for low common-cause posterior),
    DEFER to the higher-reliability source instead of summing.
  The reliability weights are inspectable scalars; the whole thing is arithmetic over two lookup
  tables. No LLM at inference.
- **The neuroscience it copies.** Ma et al. 2006 (reliability = gain, addition = inference) PINNED;
  Ernst & Banks 2002 (inverse-variance weighting) PINNED; Kording et al. 2007 (fuse-vs-segregate)
  PINNED; Lee/Shimojo/O'Doherty 2014 (reliability-comparison arbitration circuit) PINNED; CLS
  division of labour (McClelland 1995, Kumaran 2016) PINNED. The specific application to our retrieval
  task is OUR-INVENTION-UNDER-TEST.
- **How to test it (reuses the existing solverB harness + the `_glove_subset.npz` already on disk).**
  Score on a **MIXED population containing BOTH SEEN and UNSEEN items** (the division of labour only
  pays off on a mixture; on pure-UNSEEN the learned tier correctly has ~0 signal and the best you can
  do is match supplied-alone). Arms: reliability-weighted-fuse-or-defer; best FIXED-WEIGHT blend
  (tuned); supplied-alone; learned-alone; a per-item HARD COVERAGE SWITCH (learned-if-read-else-supplied)
  as the degenerate limit.
  - **Floor:** strongest floor actually run on this population = concreteness prior CONC (STATUS/SOLVED
    show CONC hit@10 ~0.115-0.172 depending on population); plus supplied-alone and best-fixed-blend as
    competitive baselines.
  - **Info-free control (the decisive one):** PERMUTE `r_learned` across terms (destroy the per-item
    evidence signal while keeping its marginal distribution). If the permuted-reliability twin matches
    the real one, the "reliability" carried no per-item information and the win is an artifact.
- **HARD-PASS:** reliability-weighted-fuse-or-defer beats BOTH `max(supplied-alone, learned-alone)` AND
  the best fixed-weight blend, CI-separated (pessimistic tie convention, 3 seeds, >=200 items),
  on the mixed population; AND the permuted-reliability twin does NOT match it.
- **HARD-FAIL:** reliability-weighting ties or loses to the best fixed-weight blend on the mixed
  population, OR the permuted-reliability twin reproduces it. Either kills the "arbitration is the
  missing organ" thesis for this task and says: just use a hard coverage switch (or supplied-alone).
- **Consistent with (does NOT overturn):** the fixed-weight-hurts findings (P1 prior-swamps-channel;
  c3 fusion-fails-when-one-dominates); the CLS SEEN/UNSEEN split (self-built = supplied on SEEN); the
  "teaching hurts" result (this is evidence-weighting, NOT teaching -- the spaces are never reshaped by
  each other). On pure-UNSEEN it degrades gracefully to supplied-alone, consistent with the ~1000x
  self-build shortfall.
- **Would overturn:** nothing measured. It is the untested combination rule that BOTH cited SOLVED.md
  files and STATUS explicitly name as the open problem ("combination is the bottleneck"; "a control
  that weights a source by how much it should be trusted HERE"). A HARD-FAIL would newly establish that
  even evidence-weighted arbitration cannot beat a hard coverage switch on this task.

### RANK 2 -- Wire the supplied distributional foundation as a spoke (B3' / cortical_recall `space="foundation"`). [P_deflated ~= 0.55; it is a WIRING of a measured win, not a discovery]

- **Mechanism.** In the cortical read, represent each consolidated term by its supplied distributional
  vector; leave the CLS consolidation GATE unchanged (membership stays sparsity-gated, the foundation
  supplies geometry only). This is Rank 1's necessary substrate.
- **Neuroscience.** Consolidated cortical semantic prior = CLS slow neocortical tier (PINNED);
  distributional/verbal spoke into the ATL hub (PINNED that language is a spoke; SPECULATIVE that a
  static table is the faithful form).
- **Build (glass-box).** Static offline non-LLM co-occurrence embedding as a lookup table; admissible
  under the FOUNDATION rule. GloVe-class or a large-corpus self-built PPMI+SVD built OFFLINE.
- **Test.** Reproduce GloVe-clears-floor-3/3 as the *wired* path (positive control already exists in
  solverB). Floor CONC; info-free twins SCRAMBLE/RANDOM (already in harness).
- **Consistent with:** `cortical_read_never_tested` SOLVED (GloVe clears 3/3). Overturns nothing.

### RANK 3 -- Grow the learned tier sample-efficiently: subword/morphology composition + multi-epoch replay + retrofit toward a DISTRIBUTIONAL graph. [P_deflated ~= 0.20; measured priors are cautionary]

- **Mechanism.** (a) fastText-style subword composition so unseen inflected/derived forms inherit
  vectors; (b) multi-epoch / interleaved replay of the read corpus (CLS consolidation) to extract more
  structure per exposure; (c) retrofit the small-corpus embedding toward an owned lexical graph -- but
  a DISTRIBUTIONAL / free-association graph, explicitly NOT the grounded/perceptual graph (refuted).
- **Neuroscience.** Morphological generalisation (developmental); systems consolidation via replay
  (McClelland 1995, Kumaran 2016, Tononi-Cirelli SHY) PINNED; retrofitting (Faruqui 2015) as an
  engineering analog of schema-based sharpening.
- **Build (glass-box).** All count-based / graph-based, fully inspectable; no LLM.
- **Test.** Does the self-built map's *pure*-UNSEEN hit@10 rise toward CONC floor as each is added?
  Floor CONC; info-free twins = random-graph retrofit (already used in the teaching cell), scrambled
  morphology.
- **HARD-PASS:** self-built UNSEEN clears CONC floor CI-separated, 3 seeds. **HARD-FAIL (the likely
  outcome per the ~1000x bound):** stays below floor -- a clean negative that confirms supply is
  necessary and closes the self-build route properly.
- **Consistent with:** SEEN-equals-supplied. **Would (only if it PASSED) overturn** the "~1000x short,
  cannot self-build" bound -- low probability given grounded-retrofit-hurt and 20k-far-below-floor.
  Note: grounded-graph retrofit is REFUTED; distributional-graph retrofit is UNTESTED and distinct.

### RANK 4 -- Episodic recombination (hippocampal pattern completion) for the SEEN sub-regime. [P_deflated ~= 0.20; addresses a different sub-regime]

- **Mechanism.** For a novel-context query about a term the substrate HAS read in some context,
  retrieve that term's stored episodic traces and use them to disambiguate the candidate. Cannot help
  *pure*-UNSEEN (no episode exists).
- **Neuroscience.** Hippocampal recombination / memory-based generalisation (Kumaran 2016) -- CONTESTED
  as a general reasoning mechanism.
- **Test.** SEEN population only; floor = counting and supplied-on-SEEN; info-free = scrambled episodes.
- **Consistent with:** SEEN-equals-supplied. Lowest priority because SEEN is already solved by the
  learned tier; included for completeness as the one genuinely-different brain mechanism, with its
  scope limit (SEEN not UNSEEN) stated honestly.

---

## HEADLINE

The unseen-context recognition gap is a HUB problem, not a MAP problem: the two maps (a supplied
large distributional foundation for the novel regime, a self-built tier that already equals it on
read material) are settled, and the one missing, brain-pinned, genuinely-open organ is a **per-item,
evidence-scaled fuse-or-defer arbitration rule** -- reliability = gain, add-when-agree, defer-when-
conflict (Ma 2006 / Ernst-Banks 2002 / Kording 2007 / Lee 2014) -- that fixed-weight blending
structurally cannot express, which is exactly why fixed-weight blending has repeatedly HURT.

## Cheap decisive test

On the EXISTING solverB harness and its already-built GloVe subset, add a MIXED (SEEN+UNSEEN)
population and run one contrast: a per-item HARD COVERAGE SWITCH (use learned tier if the term's
read-count exceeds a threshold, else supplied foundation) vs (a) the best fixed-weight blend, (b)
supplied-alone, (c) learned-alone. The hard switch is the degenerate, few-lines limit of Rank 1.
If even the hard switch beats both the fixed-weight blend AND supplied-alone CI-separated on the
mixture, arbitration matters and Rank 1 (graded reliability weighting) is worth building. If the hard
switch merely equals supplied-alone, the learned tier adds nothing for retrieval beyond what supply
already covers, and the whole arbitration thesis is refuted cheaply.

## Falsifiable predictions

- **HARD-PASS (arbitration is the missing organ):** the per-item evidence-scaled fuse-or-defer rule
  beats BOTH `max(supplied-alone, learned-alone)` AND the best tuned fixed-weight blend, CI-separated
  (pessimistic tie convention, 3 seeds, >=200 mixed items), AND the permuted-reliability info-free twin
  fails to reproduce it.
- **HARD-FAIL (arbitration is NOT the lever here):** the fuse-or-defer rule ties/loses to the best
  fixed-weight blend on the mixed population, OR the permuted-reliability twin matches it, OR the hard
  coverage switch equals supplied-alone (learned tier redundant for retrieval). Any one of these
  closes the arbitration route and says: ship supplied-alone with a coverage gate and stop.
- **Secondary HARD-FAIL (self-build, Rank 3):** subword + replay + distributional-graph retrofit does
  NOT lift the self-built map's pure-UNSEEN hit@10 to the CONC floor on 3 seeds -- confirming supply is
  necessary (the expected outcome).

## Cross-thread synthesis (with prior measured results)

- `cortical_read_never_tested_where_it_matters` (PARTIAL): supplied distributional map clears the
  UNSEEN floor 3/3; self-built does not (data-starved ~1000x); self-built EQUALS supplied on SEEN.
  -> Rank 2 wires the win; Rank 1 exploits the SEEN/UNSEEN division of labour it demonstrated.
- `teach_the_self_built_space_instead_of_concatenating_it` (REFUTED): grounded->distributional
  TEACHING hurts retrieval; more teaching = monotonically worse; perceptual similarity is the wrong
  axis for slot-fill. -> Rank 1 is explicitly NOT teaching (no space reshapes another); Rank 3
  explicitly excludes the grounded graph and proposes a distributional graph instead.
- `reader_meaning_channel` (flagship): fixed-weight prior SWAMPS a weaker-but-correct channel;
  "combination is the bottleneck"; segregated slots beat superposition. -> Rank 1 is the named
  combination rule the flagship owns; the segregation gate echoes its measured segregation win.
- `exp_readout_second_order_v1` (landed NO): a second-order READOUT cue over our first-order profiles
  does not clear the floor. -> This is why the fix is a genuine matrix-factorisation distributional
  space (GloVe/PPMI+SVD are already second-order), not a readout tweak. The lever stays closed.
- The c3 grounded-fusion win (fusion beats both components when channels are COMPARABLE; fails when
  one DOMINATES) is the same organ Rank 1 generalises: replace "comparable vs dominating" with a
  per-item reliability that makes the fuse-or-defer decision automatically.
- Substrate-physics field advisor (spin-glass / free-probability program) is orthogonal to this
  neuroscience drill; no adjacency edge into the unseen-retrieval question. Noted, not drilled.

## Substrate-product implications

The reader ships as a two-tier semantic memory with a confidence switch, mirroring how a human reader
handles a familiar word in an unfamiliar sentence: use what you have genuinely learned when you have
learned it, fall back to a broad prior otherwise, and never average two sources that disagree. This is
directly demonstrable to a user ("watch it recognise a word in a sentence it has never seen that word
in") and the switch is fully glass-box -- the per-word confidence and the fuse/defer decision are
inspectable scalars, not a black-box blend. The foundation is a static offline asset (no live LLM),
preserving the project invariant. Product framing only; not a publication.

## Citations (verified count)

**WEB-VERIFIED THIS SESSION (12), via two Sonnet lit-scans:**
1. Ernst & Banks 2002, Nature 415:429-433 -- optimal MLE cue integration (weight ~ 1/variance). [PINNED]
2. Alais & Burr 2004, Curr Biol 14:257-262 -- audiovisual reliability-weighting (ventriloquist). [PINNED]
3. Kording, Beierholm, Ma, Quartz, Tenenbaum & Shams 2007, PLoS ONE 2(9):e943 -- causal-inference
   fuse-vs-segregate. [PINNED-descriptive]
4. Ma, Beck, Latham & Pouget 2006, Nat Neurosci 9:1432-1438 -- probabilistic population codes;
   reliability=gain, addition=inference. [PINNED-mechanistic]
5. Feldman & Friston 2010, Front Hum Neurosci 4:215 -- precision-weighting of prediction error.
   [SPECULATIVE/interpretive]
6. Henaff et al. 2020, Nat Commun 11:2513 -- neural gain variability as uncertainty representation.
   [CONTESTED/active]
7. Bays 2016, J Vision (PMC5024667) -- optimal decoding of gain-variable population codes. [supporting]
8. McClelland, McNaughton & O'Reilly 1995, Psych Rev 102(3):419-457 -- CLS foundational. [PINNED]
9. Kumaran, Hassabis & McClelland 2016, Trends Cog Sci 20(7):512-534 -- CLS updated. [PINNED]
10. Lee, Shimojo & O'Doherty 2014, Neuron 81(3):687-699 -- reliability-based arbitration circuit. [PINNED]
11. Patterson, Nestor & Rogers 2007, Nat Rev Neurosci 8:976-987 -- ATL hub-and-spoke. [PINNED-core]
12. Lambon Ralph, Jefferies, Patterson & Rogers 2017, Nat Rev Neurosci 18:42-55 -- semantic cognition. [PINNED-core]

**CANONICAL, CITED-FROM-KNOWLEDGE (NOT re-verified by web search this session; standard references):**
13. Levy & Goldberg 2014, NeurIPS -- skip-gram = implicit shifted-PMI factorisation.
14. Levy, Goldberg & Dagan 2015, TACL -- count-vs-predict is mostly hyperparameters.
15. Baroni, Dinu & Kruszewski 2014, ACL -- "Don't count, predict!"
16. Rao & Ballard 1999, Nat Neurosci -- predictive coding in visual cortex.
17. Bojanowski, Grave, Joulin & Mikolov 2017, TACL -- fastText subword composition.
18. Faruqui, Dodge, Jauhar, Dyer, Hovy & Smith 2015, NAACL -- retrofitting to lexicons.
19. Yu & Smith 2007, Psych Sci -- cross-situational word learning.
20. Warstadt et al. 2023, CoNLL -- BabyLM Challenge (child-scale LM).
21. Hart & Risley 1995 -- child language input volume.
22. Tse et al. 2007, Science -- schemas accelerate consolidation. (Tononi & Cirelli SHY as framework.)

Verified-this-session count: **12**. Cited-from-knowledge (canonical): 10.

---

## TLDR

We already have the two ingredients to recognise a familiar word in a brand-new kind of sentence: a
big ready-made word-meaning map (works on new words, allowed to build offline, not a live AI) and a
small map the reader builds from its own reading (already just as good on words it has actually read
about, useless on the rest). The thing we are missing, and the only genuinely hard part, is the
*rule for which map to trust for each word*. The brain does not blend two sources at a fixed strength
-- it trusts whichever one has real evidence about the specific word, and when they disagree it picks
one instead of averaging. Every time we have blended at a fixed strength, it has hurt. So the build is:
supply the big map, keep growing the small map, and put a confidence-based "trust the one that
actually knows this word" switch between them. The cheapest way to find out if this is right is a
tiny experiment on tools we already have: does a simple "use my own map if I've read about this word,
else use the big map" switch beat the fixed blend? If yes, build the graded version; if it just ties
the big map alone, the small map adds nothing for this task and we ship the big map with a coverage
gate.

## QUESTIONS

1. One owner-level decision (inherited from the SOLVED.md files, restated here): may the cortical read
   use an IMPORTED distributional map (static, inspectable, offline, non-LLM), or must it LEARN its map
   from the substrate's own reading? The first clears the bar today; the second needs ~100x more
   reading than child-scale and ~1000x more than we own. Rank 1/2 assume "imported is admissible" (per
   the standing FOUNDATION rulings); if that is overruled, only Rank 3 remains and it is expected to
   fail.

## NEXT STEPS

1. (Director) Dispatch the cheap decisive test to a cell-author: MIXED (SEEN+UNSEEN) population on the
   existing solverB harness; arms = hard coverage switch, best fixed-weight blend, supplied-alone,
   learned-alone; floor CONC; info-free twin = permuted reliabilities. This is a few lines on an
   existing harness and settles whether Rank 1 is worth building.
2. If the cheap test passes, build Rank 1 (graded reliability weighting = gain-scaled add + Kording
   segregation gate) and Rank 2 (wire the foundation spoke) together -- they share the substrate.
3. Rank 3 (sample-efficient self-build) is a secondary, longer-horizon track; run it as the clean
   negative that closes the self-build route only if capacity is free.
4. Keep the grounded spoke labelled as the SIMILARITY teacher it is proven to be, never a retrieval
   teacher (teaching wins on similarity, loses on prediction -- that split is a measured result).
