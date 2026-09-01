# RESEARCH DRILL — the ACCUMULATION half (cross-situational learning + semantic consolidation)

Lead-with-biology literature scan for the SOLVER on
`grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice`.
Generic-terms-only scan. Lit-scan calibration penalty applied (expected lifts
deflated 0.15–0.25; novel-synthesis confidence capped at P<=0.50). Date: 2026-09-01.

Companion to `RESEARCH_sense_selection_mechanism.md` (the SELECTION half). This
drill covers the OTHER half — how meaning ACCUMULATES over repeated exposures —
so the whole problem's brain basis is pinned, not just selection.

**Established on disk (do NOT re-derive; from SOLVED.md):** the correct
meaning-anchor is RETRIEVABLE (distributional top-10 ~85%) but NOT SELECTABLE by
any distributional read-out (~0.21–0.24 rank-1 vs ceiling ~0.87); a GROUNDED-hub
re-rank (11 Lancaster sensorimotor + 3 Warriner affect) SELECTS it (0.32/0.35 vs
0.24/0.27, +0.08/+0.07, 2 seeds, CI-separated), and re-fusing the distributional
cue HURTS. Two-stage LASS cascade (fast distributional shortlist → slow grounded
re-rank) is the wire. The `CONSOLIDATION_FAIL` population is ~92% polysemy (41–44%)
/ no-anchor (25–29%) / incoherent-context (18–24%) / proper-noun (6–11%); only
0.6–2% is coherent-single-sense-with-anchor. Mean within-word split-half context
coherence is **0.09–0.13**. Retrieval practice built to Mozer 2009 Eq.7 is at
CHANCE for selection (AUC 0.486/0.503). This drill asks whether ACCUMULATION adds
anything ON TOP of per-encounter grounded selection for THIS population.

---

## Q1 — CROSS-SITUATIONAL WORD LEARNING: associative accumulation vs propose-but-verify

### What the biology PINS

- **The learner aggregates meaning across individually-ambiguous exposures — and
  the mechanism is a CONTINUUM, not a dichotomy.** The two poles are (a) **gradual
  associative accumulation** of word↔referent co-occurrence statistics (Yu & Smith
  2007, *Psych Science*; Smith & Yu 2008) and (b) **propose-but-verify (PBV)** — a
  single hypothesized mapping carried across exposures, kept if the next exposure
  confirms it, discarded and re-proposed if not (Trueswell, Medina, Hafri &
  Gleitman 2013, *Cog Psych*; Medina, Snedeker, Trueswell & Gleitman 2011, *PNAS*).
  The current consensus (2018–2020) is that these are **not separable constructs
  but ends of one continuum**; real learning "falls somewhere in between,"
  modulated by context, memory load, and individual ability (Roembke & McMurray
  and the "beyond propose-but-verify and associative bean counting" line).

- **The two poles map onto a PINNED neural dissociation that is itself the CLS
  split.** The gradual-associative pole is supported by non-hippocampal / cortical
  statistical learning; the inferential single-hypothesis PBV pole is supported by
  the **hippocampal-relational** system (fMRI RSA during learning; and CSL survives
  — slowly, gradually — even with bilateral hippocampal damage, Frontiers 2019).
  So the brain runs BOTH: a fast episodic single-best-guess AND a slow cortical
  statistical aggregate. This is exactly the two-store shape we already need.

- **Memory is FINITE — the brain does NOT store the full co-occurrence matrix.**
  Even "associative" learners behave as if carrying one-or-few hypotheses under
  memory limits (finite-memory CSL models). Pure "associative bean counting"
  (track every word×referent count) is NOT the brain-faithful implementation; a
  small number of weighted hypotheses is.

### The nuance that is DECISIVE for our population (do not miss it)

- **PBV's single-hypothesis result is for MONOSEMOUS novel word→object mappings in
  a controlled lab.** Each novel word has exactly ONE correct referent. Our
  population is **92% polysemous / no-anchor / incoherent**. For a polysemous word
  the correct structure is NOT one carried hypothesis — the brain maintains
  **MULTIPLE competing senses** (sense-enumeration for unrelated meanings; a shared
  broad basin for related ones — Rodd 2004; Frontiers 2018 polysemy-across-word-
  classes: literal+metonymic senses share a representation, metaphor/homonymy are
  stored separately). **So the CSL single-hypothesis finding does NOT license a
  single-hypothesis (single per-word running-mean) design here.** A single per-word
  average IS the incumbent's refuted "single-averaging consolidation": it collapses
  distinct senses into one blurred centroid.

### RECOMMENDATION (Q1)

**Carry MULTIPLE competing sense-hypotheses (multi-prototype), not one; and split
the learner into the two CLS stores the biology pins.** Concretely:
- a FAST per-encounter single-best-guess (the grounded selector's argmax — this is
  the PBV / hippocampal role, already built and demonstrated); AND
- a SLOW multi-sense statistical aggregate (a per-SENSE grounded prototype — the
  neocortical role, the accumulation candidate for Q2).
Do NOT implement pure associative co-occurrence counting (not brain-faithful under
finite memory) and do NOT implement a single per-word hypothesis (the refuted
single-average). The continuum result is a *design licence* for the two-store
architecture, not for either pole alone.

---

## Q2 — SEMANTIC CONSOLIDATION: how a grounded meaning SHARPENS over exposures

### What the biology PINS

- **Complementary Learning Systems is the macro-mechanism.** Fast hippocampal
  encoding (sparse, pattern-separated) → slow neocortical semantic extraction
  (overlapping, distributed, captures cross-episode structure); sleep/replay embeds
  hippocampal traces cortically (McClelland, McNaughton & O'Reilly 1995, *Psych
  Review*; Kumaran, Hassabis & McClelland 2016, *TiCS*). This is the pinned form of
  "meaning sharpens over exposures" — the neocortex EXTRACTS the regularity across
  repeated episodes.

- **Word-specific CLS: meaning INTEGRATION emerges AFTER sleep.** Most lexical
  processing is available immediately after exposure (hippocampal), but a specific
  set of properties — lexical **competition/integration**, recall advantage, faster
  processing — emerge only LATER, after **sleep** (Davis & Gaskell 2009, *Phil
  Trans R Soc B* "A complementary systems account of word learning"; Dumay &
  Gaskell 2007; Tamminen et al.). So the *deepening* of a word's meaning is a
  distinct, slow, offline consolidation stage — not part of the online encounter.

- **Word-MEANING access is retuned by recent + long-term experience, at the level
  of attractor basins.** Rodd 2020 (*Perspectives on Psych Science*, "Settling Into
  Semantic Space") — meaning access is shaped by experience across timescales
  (minutes → years); recent experience either strengthens form→meaning connections
  OR **deepens the attractor basin** for the encountered sense. Betts, Gilbert, Cai,
  Okedara & Rodd 2018 ("Retuning of lexical-semantic representations: repetition and
  spacing effects in word-meaning priming") — repeated exposures produce **lasting**
  representational change. Gaskell et al. 2019 ("Contextual priming of word meanings
  is stabilized over sleep") — the retuning is **consolidated by sleep**. This is
  the exact mechanistic pin for "grounding accumulates/deepens per sense."

- **Accumulation is PER-SENSE, SPACING-sensitive, and BAYESIAN-SURPRISE-weighted —
  and it does NOT erase dominance.** Word-meaning priming with short narratives
  (Rodd, Gilbert, Cai et al. 2022, *PeerJ*): three **spaced** subordinate-meaning
  encounters boost availability more than one, but **massed encounters give no
  boost** (a genuine spacing effect); the boost is LARGER for subordinate meanings
  because a single subordinate encounter is highly informative (Bayesian surprise —
  the same reliability/inverse-variance logic as the selector). CRITICALLY, even
  after boosting, the **dominant meaning is still preferred overall** — the
  dominance floor is not removed. This pins both the accumulation update rule AND
  its guardrail.

### The computational form (running mean vs exemplar)

- Both a **prototype/centroid** (abstract a running mean per sense) and an
  **exemplar store** fit the polysemy data (Frontiers 2018; exemplar models of
  polysemy exist). Distributional PROTOTYPE-of-the-whole-WORD models provably
  CANNOT distinguish senses (they abstract every occurrence into one vector — this
  is our incumbent's exact failure). So the prototype must be **per-SENSE and
  GROUNDED**, never per-word-distributional.
- A **reliability-weighted running mean per sense** is the cheaper, defensible
  choice, and its main quantitative payoff is **variance reduction**: averaging the
  noisy per-encounter grounded read across coherent same-sense exposures lowers the
  variance of the grounded vector, which directly *improves the reliability weight*
  the selector uses (Q1 of the SELECTION drill). That is a real, non-trivial
  contribution of accumulation even where it does not change the argmax.

### RECOMMENDATION (Q2)

**If an accumulator is added, make it a PER-SENSE, reliability-weighted running-mean
grounded prototype, updated on spaced (not massed) coherent same-sense exposures,
with a subordinate-guard.** Update rule = precision-weighted running mean of the
grounded read into the matched sense-cluster's centroid; weight each exposure by
its grounded-read reliability (Bayesian-surprise-larger for subordinate, exactly as
priming shows). Guardrails: (1) NEVER let dominance bury a subordinate sense used
consistently within a text (pinned: dominant still wins overall, but subordinate is
boosted where locally consistent); (2) respect spacing (spaced > massed);
(3) operate only on sense-split clusters (per-word = the refuted single-average).
Sleep/offline replay is a pinned but OPTIONAL refinement (an offline consolidation
pass that re-averages/deepens clusters); flag as future, not required for a first
build.

---

## Q3 — SELECTION-only, or SELECTION + ACCUMULATION, for THIS population?

### The reasoning (this is the crux of the drill)

A grounded-prototype accumulator sharpens a sense's centroid across exposures. Its
**precondition is coherent within-SENSE repetition** (Nagy & Anderson: meaning
learning needs many *informative* exposures; word-meaning priming: needs *spaced,
consistent* same-sense encounters). On THIS population that precondition is largely
absent:
- within-word split-half coherence is **0.09–0.13** (only 5–8% clear a 0.25 gate);
- 41–44% are polysemous (contexts point at *different* senses across encounters);
- 25–29% have no anchor to sharpen toward; 18–24% are genuinely incoherent.

So a **per-word accumulator averages across senses = the incumbent's refuted
single-average.** Accumulation adds NOTHING as a standalone here. It becomes
meaningful only AFTER (i) sense-splitting partitions exposures into coherent
per-sense clusters and (ii) the grounded selector picks the right sense
per-encounter — and on disk the sense-splitting itself was seed-unstable (recovery
0.4–4%). Therefore the residual an accumulator can close is **small and contingent**:
it is confined to the ~2% coherent-single-sense slice plus whatever coherent
per-sense sub-clusters splitting recovers, and it does not move population precision.

### The one place accumulation genuinely helps regardless

**Variance reduction of the grounded read → a better reliability weight for the
selector.** Even without changing which sense is argmax, averaging the noisy
per-encounter grounded vector across same-sense exposures lowers its variance and
sharpens the selector's confidence — a second-order but real gain, and the only one
that does not require the coherence this population lacks at the word level (it
requires coherence only *within a recovered sense-cluster*).

### HONEST ANSWER (Q3)

**For THIS population, per-encounter grounded SELECTION is the near-complete
brain-faithful answer.** Accumulation is real biology, but its preconditions
(coherent, spaced, per-sense repetition) are exactly what a 92%-polysemy/incoherent
population fails. Its honest incremental value is (a) variance-reduction for the
reliability weight and (b) the small coherent-repeat slice — both second-order.
**Build the selector first; the accumulator is a guarded, per-sense, spacing-aware,
variance-reducing add-on layered on sense-split clusters, NOT a population-level
fix.** Deflated expectation (calibration penalty applied): a well-built per-sense
accumulator adds a small lift confined to the coherent slice; do not expect it to
move the ~0.33 selector number toward the ~0.87 ceiling on its own — that residual
is a REPRESENTATION/coverage problem (richer grounding + morphology + anchor-pool),
not an accumulation problem.

---

## Q4 — MISSED MECHANISMS about how the brain grounds word meaning from reading

- **MORPHOLOGY as a word-INTERNAL grounding cue (the highest-value missed
  mechanism).** Readers extract morphological information while learning unknown
  words *without* instruction; morphological **family size** facilitates novel-word
  learning; readers combine **word-internal (morphology)** and **word-external
  (context)** cues for lexical inference (Royal Soc Open Sci 2024 registered report,
  "The role of morphology in novel word learning"; "role of morphemic knowledge
  during novel word learning" 2023; Springer *Reading & Writing* 2021 on
  morphological + contextual cues). This is PINNED, CHEAP, and gives a partial
  meaning from a **single exposure** — and it is exactly the route for the
  **abstract/derived tail** where sensorimotor norms are absent (justice←just;
  -ness/-tion/-ity abstractors; un-/re- polarity). Our system uses ONLY
  distributional context; morphological decomposition of the target word is an
  additional grounded spoke feeding the selector. **Worth building** — it directly
  attacks the ~22% grounded-norm-uncovered slice that the selector cannot ground.

- **Incidental learning from context is SLOW and LOW-yield for MEANING (fast for
  FORM).** Nagy, Anderson & Herman 1987; Nagy & Anderson 1984: ~**15% acquisition
  probability per exposure** (Swanborn & de Glopper 2000); "small but reliable gains"
  per encounter; **meaning** learning needs MANY exposures, whereas **orthographic/
  form** learning can follow a **single** exposure (Nation & Castles; Share
  self-teaching). This is the fast-mapping (form) vs slow-statistical (meaning)
  split — the same CLS/LASS two-stage shape. IMPLICATION: our accumulation
  expectation must be calibrated to a LOW per-exposure meaning-yield that requires
  INFORMATIVE contexts — which the incoherent population lacks. It reframes "grounding
  doesn't accumulate" as partly **expected** for a thin (3000-sentence),
  low-coherence corpus, not solely a mechanism defect.

- **Fast-mapping vs slow statistical learning = the two CLS stores again.** A
  provisional single hypothesis is available fast (hippocampal / PBV); durable
  correct MEANING comes only from slow neocortical extraction across many exposures
  + sleep. Our two-stage cascade (fast distributional shortlist → slow grounded
  re-rank) is faithful to this; the accumulator is the "slow neocortical extraction"
  stage and should be treated as such (offline, per-sense, sleep-consolidatable).

- **What both drills have now covered vs not.** Covered: hub-and-spoke, attractor
  selection, reliability-weighted fusion, typicality/prototype, abstract grounding
  (affect + distributional + Binder-65), sense-splitting, CSL, semantic
  consolidation, word-meaning priming/spacing/dominance. NOT yet built and pinned:
  **morphology as an internal spoke** (above) and **entity/episodic grounding for
  proper nouns** (already flagged in SOLVED.md follow-on #4 — route them out of the
  distributional grounding target, into an episodic store).

---

## PINNED vs OUR-INVENTION — one-glance table (accumulation half)

| Design element | Status | Anchor |
|---|---|---|
| CSL two-store: fast hippocampal single-guess + slow neocortical statistical aggregate | PINNED | McClelland/McNaughton/O'Reilly 1995; Kumaran 2016 |
| Word-meaning integration/deepening emerges AFTER sleep (offline) | PINNED | Davis & Gaskell 2009; Dumay & Gaskell 2007 |
| Meaning access retuned by recent+long experience; basin deepening | PINNED | Rodd 2020; Betts et al. 2018 |
| Priming/accumulation is PER-SENSE, SPACED>massed, larger for subordinate | PINNED | Rodd/Gilbert/Cai 2022 (PeerJ) |
| Dominance floor NOT erased by accumulation (guard subordinate) | PINNED | word-meaning priming line |
| Assoc-accumulation vs PBV = a CONTINUUM, both operate | PINNED | Yu&Smith 2007; Trueswell 2013; Medina 2011 |
| Single-hypothesis is for MONOSEMOUS lab words; polysemy needs MULTI-sense | PINNED | Rodd 2004; Frontiers 2018 polysemy |
| Pure full-matrix associative counting | NOT brain-faithful (finite memory) | finite-memory CSL models |
| Per-sense running-MEAN prototype vs exemplar | UNPINNED → OUR-INVENTION (running mean defensible + cheap; both fit data) | polysemy prototype/exemplar/attractor models |
| Accumulation's value = variance-reduction of grounded read → reliability weight | OUR-INVENTION (well-motivated by inverse-variance fusion) | Ernst-Banks logic + running-mean statistics |
| Morphology as word-internal grounding spoke | PINNED (mechanism) / un-built here | RSOS 2024; morphemic-knowledge 2023 |
| Incidental meaning-learning ~15%/exposure, slow; form fast-maps | PINNED | Nagy & Anderson 1984/87; Nation & Castles |

---

## TLDR (plain English)

When a person meets the same word many times, they do NOT just blur all the
meetings into one average — that is exactly the broken step we already have. The
brain does two things instead. First, in the moment, it makes a best guess about
which meaning this time (that is the "picking" step the other drill already showed
is the main fix). Second, slowly and offline (helped by sleep), it sharpens each
SEPARATE meaning of the word a little each time it sees that meaning used the same
way — and it keeps rarer meanings alive rather than letting the common meaning bury
them. The catch for OUR word list: those slow-sharpening habits only work when the
same meaning shows up clearly and repeatedly, and our hard words almost never do
(most have several meanings, or no known meaning, or messy contexts). So for THIS
list, the "picking" step is very nearly the whole answer; a "sharpen-each-meaning"
step would only help a little, and only after we first sort the word's uses into its
separate meanings. The one clearly useful thing the sharpening buys us is a steadier
read of each meaning, which makes the picking step more confident. The genuinely NEW
idea worth building is to read the word's PARTS (its root and endings) — that gives a
meaning clue from a single sighting and is exactly what helps the fuzzy, abstract
words that have no physical feel.

## QUESTIONS

None blocking. One judgement call for the solver: whether to build the per-sense
accumulator at all in the first pass, or defer it until the grounded selector +
sense-splitting are wired — my recommendation is DEFER it as a standalone grounding
driver and instead fold its only population-general benefit (variance-reduction of
the grounded read) directly into the selector's reliability weight, which needs no
extra machinery.

## NEXT STEPS (for the solver)

1. **Selection-only is ~the complete brain-faithful answer for THIS population.**
   Ship the grounded selector; do NOT expect a standalone accumulator to move
   population precision (its preconditions — coherent, spaced, per-sense repetition —
   are what this 92%-polysemy/incoherent population lacks).
2. **Carry MULTIPLE competing sense-hypotheses, never one running mean per word.**
   The CSL single-hypothesis (propose-but-verify) result is for monosemous lab words
   and does not transfer to polysemy; a single per-word average is the refuted
   single-averaging consolidation.
3. **If/when you add an accumulator, make it PER-SENSE, reliability-weighted
   running-mean, spacing-aware (spaced>massed), with a subordinate-guard**, layered
   ONLY on sense-split clusters. Its honest job is variance-reduction of the grounded
   read (better selector reliability weight) + the small coherent-repeat slice — a
   second-order refinement, sequenced AFTER selector + sense-splitting.
4. **Build MORPHOLOGY as a word-internal grounding spoke** — pinned, single-exposure,
   cheap, and the best lever for the ~22% abstract/derived tail the sensorimotor norms
   miss. Decompose target words into morphemes; feed morpheme-family/root meaning as an
   additional spoke into the grounded selector. Highest-value missed mechanism.
5. **Calibrate expectations to biology:** incidental meaning-learning is ~15%/exposure
   and slow even in humans; "grounding doesn't accumulate" on a thin low-coherence
   corpus is partly expected, not solely a mechanism defect — do not over-attribute the
   flatness to a broken accumulator.
