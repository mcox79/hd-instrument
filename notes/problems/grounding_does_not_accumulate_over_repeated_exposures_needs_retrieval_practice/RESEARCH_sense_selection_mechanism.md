# RESEARCH DRILL — the sense-SELECTION mechanism at the ATL hub

Lead-with-biology literature scan for the SOLVER on
`grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice`.
Generic-terms-only scan. Lit-scan calibration penalty applied (expected lifts
deflated; novel-synthesis confidence capped at P<=0.50). Date: 2026-09-01.

Framing question we already answered on disk (do NOT re-derive): the correct
meaning-anchor is RETRIEVABLE (distributional top-10 ~85%) but NOT SELECTABLE by
any distributional read-out (~0.21-0.24 rank-1 vs ceiling 1.0). A grounded-hub
re-rank (11 Lancaster sensorimotor + 3 Warriner affect) selects it (+0.08
unsupervised). This drill pins the biology of the SELECTION step so we build the
full lift brain-faithfully, not by convenience.

---

## Q1 — THE COMBINATION RULE (distributional cue x grounded cue at the hub)

### What the biology PINS

- **Hub-and-spoke architecture is pinned.** A transmodal ATL hub binds
  modality-specific "spokes" into coherent, generalisable concepts (Patterson,
  Nestor & Rogers 2007; Lambon Ralph, Jefferies, Patterson & Rogers 2017, *Nat
  Rev Neurosci*). This is the correct macro-structure for our
  "distributional-context spoke + grounded-sensorimotor spoke -> convergence"
  design.

- **The hub combination is NONLINEAR and LEARNED, not linear averaging.** The
  canonical implementation is a recurrent PDP attractor network (Rogers,
  Lambon Ralph, Garrard, Bozeat, McClelland, Hodges & Patterson 2004, *Psych
  Review*; McClelland & Rogers 2003, *Nat Rev Neurosci*). Concepts are stable
  states in a high-dimensional space reached by recurrent settling; the mapping
  from inputs to the converged state is nonlinear and acquired gradually from
  the statistics of experience.

- **Word-meaning access is attractor SETTLING; senses are basins** (Rodd,
  Gaskell & Marslen-Wilson 2004, *Cognitive Science*). Related senses form one
  broad basin (facilitation); unrelated meanings form competing basins
  (interference). WTA is the OUTPUT of settling, not the combination rule.

- **Reliability-weighted (inverse-variance / MLE) integration is the pinned
  cue-combination rule in the brain — and it extends up to language.**
  Ernst & Banks 2002 (*Nature*): humans combine cues weighted by their
  reliability (inverse variance), which is statistically optimal. This is not
  perception-only: noisy-channel language comprehension shows listeners weight
  top-down context vs bottom-up signal by reliability and lean HARDER on context
  exactly when the bottom-up signal is degraded (Levy 2008; Gibson et al.;
  "Shortlist B" Bayesian word recognition). Reliability weighting is itself
  modulated by top-down attention (Rohe & Noppeney line).

- **Semantic CONTROL dynamically re-weights spokes by task/context.** The
  controlled-semantic-cognition framework (Lambon Ralph 2017; Jackson,
  Lambon Ralph 2018 CSC) shows PFC/IFG selectively strengthens coupling to the
  relevant spoke per task — a biological adaptive-weighting knob, not fixed
  equal weights.

### What is UNPINNED (call it OUR-INVENTION honestly)

- **The exact algebra of hub convergence is explicitly underdetermined.**
  The CSC papers describe "fusion"/"coalition" of hub + spokes and show
  directional (DCM) influence, but they do NOT specify whether combination is a
  weighted sum, a product, or an argmax. Choosing z-fusion vs product vs
  reliability-weighted at the hub is OUR engineering choice, *constrained by* the
  biology above, not dictated by a pinned equation.

- **Whether the brain literally computes inverse-variance weights at the
  CONCEPTUAL (not perceptual) level is an extrapolation** — but a well-motivated
  one: the noisy-channel comprehension evidence is the closest pinned analogue
  and it behaves exactly like reliability weighting.

### The unification that resolves the (b)-vs-(c) choice

For Gaussian cues, **reliability-weighted combination IS a product-of-experts**:
the product of two Gaussian likelihoods is a Gaussian whose mean is the
precision-weighted (inverse-variance) average of the two means. So option (b)
reliability-weighted and option (c) product-of-experts are the *same operation* —
(c) is the multiplicative/intersective view, (b) is its closed form. WTA (d) is
what you get by taking the argmax of the combined posterior. Equal-weight
z-fusion (a) is the special case that THROWS AWAY the reliability information the
brain demonstrably uses — it is the least brain-faithful of the four.

### RECOMMENDATION (Q1)

**Implement reliability-weighted (precision-weighted) fusion of the two cues,
then argmax.** Concretely, for each candidate sense combine a distributional
score and a grounded-hub score as `w_d * s_d + w_g * s_g`, with weights set by
per-cue reliability (inverse variance), NOT fixed equal weights:

- distributional reliability `w_d` ~ peakiness/margin of the distributional
  posterior over the candidate set (a flat top-10 = low reliability -> down-weight);
- grounded reliability `w_g` ~ sensorimotor/affect coverage & strength of the
  word (abstract words with weak norms = low reliability -> down-weight the
  grounded spoke exactly where it is uninformative — this makes Q3 fall out
  for free).

This is brain-faithful on three counts: MLE cue combination (Ernst-Banks),
control-modulated spoke weighting (CSC), and attractor read-out (argmax = the
settled basin, Rodd 2004). It dominates equal-weight z (which the biology
actively argues against). Sweep nothing about the *form*; sweep the reliability
estimators. Prefer this over a bespoke WTA — WTA is the output, you get it free.

---

## Q2 — TYPICALITY / PROTOTYPE IN SELECTION

### What the biology PINS

- **Graded typicality is real and neurally instantiated.** Typical items are
  categorised faster/more accurately; the semantic network shows graded
  typicality responses (e.g., typicality responses in the semantic-memory
  network; Rosch's graded-membership account). Both prototype and exemplar
  models produce typicality via SIMILARITY (distance to a central prototype, or
  summed similarity to stored instances) — the two are notoriously hard to
  separate behaviourally.

- **In the PDP/hub view, typicality falls out of the learned attractor
  landscape** — no separate prototype store is required. Feature-sharing pulls
  representations into central/deep basins; typicality = basin centrality
  (Rogers 2004; Rodd 2004 basin depth/breadth from learning statistics).

- **Repeated exposure SHAPES the landscape.** Basin depth/breadth is set by the
  statistics of exposure (Rodd 2004). This is the mechanistic pin for our exact
  problem name: grounding *should* accumulate over exposures by sharpening the
  grounded centroid of each sense.

### RECOMMENDATION (Q2)

**Yes, add a typicality term — and make it the core of the accumulation fix, not
an add-on.** Implement it brain-faithfully and cheaply as a PRIOR inside the
reliability-weighted combination:

- maintain, per candidate sense, a running grounded PROTOTYPE = the
  reliability-weighted running mean of the grounded read across accumulated
  exposures (a centroid). Prototype (centroid) is the cheaper, defensible choice
  over full exemplar storage; both are consistent with the data.
- add a typicality score = similarity(context-grounded read, that prototype),
  entered as a third weighted cue.

This is literally "the sense whose grounded representation is most typical given
accumulated exposure," and the running-mean update IS the retrieval-practice /
accumulation mechanism the problem asks for. A flat non-accumulating result would
be a broken update, not a ceiling (diagnose before concluding).

**Honesty caveat — the dominance trap.** A typicality prior biases toward the
DOMINANT sense and can HURT subordinate-sense selection (the classic
frequency-dominance effect; the exact interference Rodd 2004 models). Keep it a
*weighted* cue combined with the context cue (reliability-weighted), never
allowed to dominate — this matches brain data where context overrides dominance.
Sweep the typicality weight; verify it does not degrade subordinate senses on a
held-out slice.

---

## Q3 — ABSTRACT-WORD GROUNDING (the ~22% sensorimotor norms miss)

### What the biology PINS

- **The under-coverage is expected, not a bug.** Sensorimotor norms structurally
  under-represent abstract words.

- **Affective grounding is real and disproportionately loads abstract words**
  (Vigliocco, Meteyard, Andrews & Kousta 2009, affective-embodiment /
  Embodied Theory of Semantic Representation; Warriner affect norms). BUT pure
  affective embodiment as the SOLE abstract-grounding is CONTESTED — recent
  cross-linguistic evidence argues against affect being the whole story
  (Villani/ Borghi-line critiques, *Phil Trans R Soc B* 2023). Affect helps,
  insufficient alone.

- **Distributional / linguistic bootstrapping is a genuine, pinned grounding
  route for abstract words.** Andrews, Vigliocco & Vinson 2009 (*Psych Review*):
  semantic representation is an *optimal statistical combination* of experiential
  AND distributional data — directly supports our reliability-weighted fusion and
  says the distributional cue should carry MORE of the load for abstract items.
  LASS (Barsalou et al. 2008): the linguistic/word-association system fires FAST
  and carries much of abstract meaning; situated simulation is slower. Words are
  also social/linguistic tools for abstract concepts (Borghi WAT).

- **Binder et al. 2016 experiential-attribute representation (~65 dims across
  Vision, Somatic, Audition, Motor, Spatial, Temporal, Affective, SOCIAL,
  COGNITION, EMOTION, Drive, Attention, ...) carries abstract-relevant axes the
  14-dim sensorimotor+affect hub misses.** Binder dims separate a-priori
  categories BETTER than distributional LSA, and are derived to map onto
  large-scale brain networks. Experiential and distributional embeddings play
  COMPLEMENTARY roles in decoding brain activity (Anderson et al. 2017/2019,
  "complementary roles ... in decoding brain activity") — the two are not
  redundant.

### RECOMMENDATION (Q3)

**Upgrade the grounded spoke from 14-dim to the Binder-65 experiential
representation as the richer spoke for abstract words — but adopt it on measured
lift, not by faith, and keep reliability-weighting as the safety net.**

Rationale: Binder's ADDED domains — SOCIAL, COGNITION, EMOTION, SPACE, TIME,
CAUSAL/EVENT, ATTENTION — are precisely the experiential axes on which abstract
senses differ and which 11 sensorimotor + 3 affect dims cannot represent. This is
the hub-and-spoke "add the missing spokes" move and it is brain-grounded (dims
tied to brain networks). Two guardrails:

1. **Coverage.** Binder norms cover fewer words than Lancaster; use the published
   computational EXTENSIONS of Binder ratings to a large vocabulary (imputed
   dims) rather than dropping uncovered words.
2. **The residue still needs distributional bootstrapping.** For the truly
   abstract tail where even Binder dims are weak/imputed, the reliability-weighted
   rule (Q1) automatically shifts weight onto the distributional cue — which is
   the pinned brain route for abstract meaning anyway (Andrews 2009 / LASS).

**Mandatory ablation before adopting Binder-65:** does it lift subordinate /
abstract-sense selection over the 14-dim hub with the fusion rule held fixed,
measured on the abstract slice? Adopt only if it beats 14-dim there. Adding 65
noisy/imputed dims risks re-creating the exact "retrievable-but-not-selectable"
failure; measure the incremental lift, do not assume it.

### Architectural bonus (pinned by LASS timing)

LASS fixes the ORDER: linguistic/word-association cue is FAST, situated
grounded simulation is SLOWER and selective. This validates our current two-stage
pipeline as brain-faithful — distributional produces the fast top-10 shortlist,
grounded simulation does the slow selective re-rank. Keep that ordering.

---

## PINNED vs OUR-INVENTION — one-glance table

| Design element | Status | Anchor |
|---|---|---|
| Hub-and-spoke (context spoke + grounded spoke -> hub) | PINNED | Patterson 2007; Lambon Ralph 2017 |
| Nonlinear/attractor convergence, learned from exposure | PINNED | Rogers 2004; McClelland & Rogers 2003 |
| Senses = attractor basins; WTA is the output | PINNED | Rodd 2004 |
| Reliability-weighted (inverse-variance) cue fusion | PINNED (perception+comprehension); EXTRAPOLATED to concept level | Ernst-Banks 2002; Levy 2008 noisy-channel |
| Product-of-experts == precision-weighted fusion (same op) | PINNED (math identity) | Gaussian PoE |
| Exact hub algebra (z vs product vs argmax) | UNPINNED -> OUR-INVENTION | Lambon Ralph 2017 (underdetermined) |
| Control-modulated per-task spoke weighting | PINNED | CSC / Jackson-Lambon Ralph |
| Graded typicality via basin centrality | PINNED | Rogers 2004; Rosch |
| Running grounded prototype = accumulation mechanism | PINNED (mechanism) / OUR-INVENTION (our update rule) | Rodd 2004 basin-from-statistics |
| Affective grounding of abstract words (helps, not sole) | PINNED but CONTESTED-as-sole | Vigliocco 2009; PhilTrans 2023 |
| Distributional bootstrapping for abstract meaning | PINNED | Andrews 2009; Barsalou LASS 2008 |
| Binder-65 as richer abstract spoke | PINNED resource; incremental lift UNTESTED here | Binder 2016; Anderson 2017 complementary roles |

---

## TLDR (plain English)
When the brain figures out which meaning a word has, it does NOT just average two
guesses equally. It trusts each source of evidence in proportion to how reliable
that source is right now, and it leans harder on the source that is clearer for
this particular word. So: combine the "what words tend to sit near it" clue and
the "what it feels/looks/does like" clue by trusting whichever is clearer, then
pick the winner. Also let the machine sharpen its idea of each meaning a little
every time it sees the word (that is the "practice makes it stick" part the
problem is missing). And for fuzzy words with no physical feel (like "justice"),
lean on a richer 65-part "human-experience" description that includes social,
emotional, and time/space feel — but only keep it if it actually helps on those
words when we test it.

## QUESTIONS
None blocking. One judgement call is flagged for the solver: how aggressively to
let the "usual meaning wins" prior weigh in without burying rarer-but-correct
meanings — resolve by sweeping its weight and checking the rare-meaning slice.

## NEXT STEPS (for the solver)
1. Replace equal-weight z-fusion with reliability-weighted (precision-weighted)
   fusion; reliability = distributional-margin for the context cue, norm-coverage
   for the grounded cue. Argmax = selection.
2. Add a running grounded-prototype (centroid) per sense, updated per exposure;
   enter typicality-to-prototype as a third reliability-weighted cue. This is the
   accumulation/retrieval-practice fix. Sweep its weight; guard the subordinate slice.
3. Ablate Binder-65 vs the 14-dim hub on the ABSTRACT slice with the fusion rule
   fixed; adopt only on measured lift; use a computational extension of Binder to
   cover vocabulary; keep reliability-weighting so distributional carries the
   abstract residue.
4. Keep the two-stage order (fast distributional shortlist -> slow grounded
   re-rank) — it is LASS-faithful.
