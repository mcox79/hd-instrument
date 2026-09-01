# RESEARCH DRILL -- pushing word-sense SELECTION accuracy toward the ceiling

Lead-with-biology literature scan for the SOLVER on
`grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice`.
Generic-terms-only scan. Lit-scan calibration penalty applied (expected lifts
deflated 0.15-0.25; novel-synthesis confidence capped at P<=0.50). Date: 2026-09-01.

**Companion to `RESEARCH_sense_selection_mechanism.md` (do NOT duplicate it).** That
drill pinned the COMBINATION RULE (reliability-weighted == product-of-experts fusion,
argmax = settled basin) and the ACCUMULATION mechanism (running grounded prototype).
This drill attacks a different axis: **why the grounded cue itself tops out, and how
the brain makes a word's grounded representation CONTEXT-SPECIFIC rather than a static
per-lemma average.** The two are complementary -- the prior drill improves how two
cues are fused; this drill improves what the grounded cue *is*.

---

## THE DECISIVE FRAME (from the on-disk evidence, before any biology)

The established-on-disk facts already tell us WHERE the ceiling lives, and it is not
where a naive reading would put it:

1. **The correct anchor is in the distributional top-K shortlist ~85% of the time**,
   but cosine cannot SELECT it. A grounded re-rank roughly DOUBLES selection
   (~0.20-0.28 -> ~0.45-0.48).
2. **An unsupervised cascade already MATCHES a supervised-over-grounded-features
   ceiling (~0.41).** This is the load-bearing fact. It means a *supervised
   classifier given the same features cannot beat the unsupervised selection.* So
   the SELECTION ALGORITHM is not the bottleneck -- **more selection cleverness
   (better fusion, recurrent settling, a learned readout) has no headroom over the
   CURRENT features.** The headroom is in the FEATURES.
3. The grounded cue is PER-WORD (one static norm vector per lemma). For a polysemous
   word that vector is a **sense-blend** -- an average over senses that matches none
   of them well.

Chaining these: the only lever that can move the ceiling is **changing the grounded
features to be occurrence-specific (context-conditioned), not the mechanism that
selects over them.** Everything below is scored against that conclusion, and it is
what makes the recommendation decisive rather than a menu.

---

## TOPIC 1 -- CONTEXTUALIZED / SITUATED GROUNDED MEANING (the prime suspect)

### What the biology PINS

- **Concepts are NOT static summaries; they are situated simulations built per
  occurrence.** Barsalou's situated-conceptualization account (Barsalou 2003, 2009
  *Phil Trans R Soc B* "Simulation, situated conceptualization, and prediction"):
  a concept is implemented by a *simulator*, but any given act of thinking runs a
  *situated conceptualization* -- an ad-hoc, context-bound multimodal simulation in
  which pre-existing feature repertoires and the current contextual elements are
  intertwined. **The representation of a word occurrence is dynamical, varying with
  situation and goal.** This is the exact biological refutation of a static per-lemma
  grounded vector: the brain does not store one experiential vector per word and reuse
  it -- it CONSTRUCTS a context-specific one each time.

- **The mechanism that makes it context-specific is top-down predictive constraint.**
  Predictive-coding models of comprehension (Kuperberg & Jaeger 2016; Rabovsky et al.;
  Wang, Nour Eddine & Kuperberg 2025 implemented predictive-coding lexico-semantic
  model) show higher levels generate top-down predictions that PRE-ACTIVATE
  lower-level semantic features, and the N400 indexes the residual prediction error.
  The functional consequence: **prior context pre-activates the sense-appropriate
  experiential features before/at the moment the word is read.** The right sense's
  grounded features are selectively boosted by context; the wrong sense's are
  suppressed. Reliability-weighting (from the prior drill) is the same story on the
  cue-combination side: listeners lean HARDER on top-down context exactly when the
  bottom-up signal is ambiguous (noisy-channel comprehension) -- and a polysemous word
  read cold IS the maximally-ambiguous bottom-up signal.

- **The hub gets this context via its spokes and semantic control.** Hub-and-spoke
  (Patterson, Nestor & Rogers 2007; Lambon Ralph, Jefferies, Patterson & Rogers 2017):
  the ATL transmodal hub augments its coupling to context-sensitive spoke systems when
  elements form a coherent ensemble, and ventrolateral PFC/IFG semantic control
  selectively strengthens the task/context-relevant spoke. So "activate the right
  sense's grounded features for this occurrence" is a pinned, named brain operation
  (controlled semantic cognition), not our invention.

- **In machine terms this is exactly why contextualized > static for WSD.** Static
  embeddings give one vector per word type regardless of context; contextualized
  representations give a context-dependent vector and thereby *implicitly disambiguate*
  -- a nearest-neighbour classifier over contextual embeddings reaches ~human-like
  accuracy on coarse noun WSD (>94%), well above anything a static per-word vector can
  do (Wiedemann et al. 2019 "Does BERT Make Any Sense?"; Loureiro et al. 2021 analysis
  of LMs for WSD). The lesson transfers to our grounded space directly: **a
  context-conditioned grounded vector should disambiguate where a static per-lemma one
  cannot.**

### The computational form we can COPY (glass-box, our assets, no external LLM)

The pinned operation is: *context sets the target experiential profile; the word's
candidate senses are scored against that context-demanded profile.* Concretely, replace
the ambiguous target's static grounded vector with a **context-predicted grounded
vector**:

```
binder_ctx = g(phi_context)          # predicted Binder-65 from the OCCURRENCE context,
                                     #   not from the (sense-blended) lemma
score(sense_k) = sim(grounded_proto(sense_k), binder_ctx)
select = argmax_k score(sense_k)     # over the distributional top-K shortlist
```

- `phi_context` = our existing distributional context vector for the occurrence
  (sentence/window embedding). This is the "top-down context".
- `g` = our existing predicted-Binder-65 map, but **applied to the context vector**
  instead of the lemma. This is the situated-simulation step: context -> experiential
  profile. Glass-box (a small learned linear/MLP map, already in our toolkit).
- `grounded_proto(sense_k)` = each shortlist candidate's static grounded vector
  (its per-lemma norms, or gloss-derived Binder). The candidates stay static; the
  TARGET becomes context-specific. That asymmetry is the whole fix -- we are no longer
  matching candidate-grounding to a blurry per-word average, we are matching it to what
  the context demands the experiential features should be.

This is the literal implementation of "context-conditioned grounded vector =
f(word_norms, sentence_context)" the drill asked for, and it changes the FEATURES (the
established bottleneck), not the selector.

---

## TOPIC 2 -- RECURRENT / ITERATIVE CONSTRAINT SATISFACTION (vs one-shot argmax)

### What the biology PINS

- **Senses are attractor basins reached by recurrent settling** (Rodd, Gaskell &
  Marslen-Wilson 2004 *Cognitive Science*). Recurrent connections within the semantic
  units "clean up" a partial activation pattern into a stable sense-state; related
  senses share one broad basin (facilitation), unrelated meanings compete (interference).
- **Interactive activation == mutual constraint satisfaction, and an appropriately
  parameterised IAC network implements optimal Bayesian inference** (McClelland, Mirman,
  Bolger & Khaitan 2014 *Cognitive Science*). Recurrent settling is provably a superior
  cue-integration mechanism to feedforward *when multiple sources must be mutually
  reconciled*.

### The honest verdict for OUR case (this is where the on-disk fact bites)

Recurrent settling is a better cue-INTEGRATION and better OUTPUT-cleanup mechanism --
**it is not a source of new features.** Given the on-disk result that a supervised
readout over the current features already matches the unsupervised cascade, iterating
the *same* features through a settling loop cannot manufacture headroom that a
supervised classifier over those features could not find. Rodd's own result is
instructive: settling changes *latency* (ambiguous words settle FASTER) and models the
ambiguity advantage/disadvantage -- it is not primarily an accuracy lever on a
single item's sense choice.

**Where settling WOULD earn its keep is strictly downstream of Topic 1.** Once the
grounded cue is context-specific, you have (at least) three mutually-constraining
signals -- distributional-context, context-predicted grounding, and per-sense grounded
prototypes -- and reconciling them iteratively (context sharpens grounding -> grounding
re-weights which context features matter -> re-read) is exactly the mutual-constraint
regime where settling helps. So settling is **second-order: valuable only after
context-gating supplies features worth settling among.** Deferring it is the correct
sequencing, not a dismissal.

---

## TOPIC 3 -- PER-SENSE GROUNDED PROTOTYPES

### What the biology + NLP PIN

- **The brain represents multiple senses of one form as distinct sub-states of the
  hub, separated by learning, not as one averaged vector** (Rodd 2004 basins; the PDP
  hub view). Distinct senses = distinct attractors reached from the same orthographic
  input under different context.
- **In NLP the winning cheap operationalisation is a per-sense prototype + 1-nearest-
  neighbour.** LMMS (Loureiro & Jorge 2019; LMMS Reloaded 2022) builds one prototype
  embedding per WordNet sense (pooled from contextual encoders + propagated through the
  WordNet graph + gloss text) and does 1-NN against the occurrence's contextual vector
  -- and this *beat the prior state of the art* with no per-token supervised classifier.
  Gloss-informed biencoders (Blevins & Zettlemoyer 2020) push the same idea down the
  long tail using sense definitions. **Per-sense prototype + 1-NN is a proven, glass-box,
  training-light selection rule.**

### The cost/benefit -- and why this is the FALLBACK, not the lead

The decisive question the drill poses: *do we even need explicit sense-splitting if
context-gating is enough?* Barsalou's account says situated conceptualization is
CONTINUOUS and ad-hoc -- the brain does not necessarily commit to a discrete enumerated
sense; it builds the occurrence's meaning from context. Topic 1's context-predicted
grounded vector already delivers occurrence-specificity WITHOUT needing to (a) cluster
each lemma's occurrences into senses, (b) decide K per lemma, or (c) align clusters to
WordNet synsets -- three hard, brittle steps that also need many occurrences per lemma
to be stable.

**So the ordering is: context-gating first (Topic 1); per-sense prototypes as the
fallback if context-gating alone plateaus below the ceiling.** If we DO go there, do it
the LMMS way with our assets: cluster a lemma's occurrences by `phi_context`, ground
each cluster by the mean context-predicted Binder of its members (or by attaching the
shortlist's WordNet senses to clusters), keep 1-NN as the selector. This is also
naturally the accumulation mechanism the problem-name asks for -- each new exposure
sharpens its cluster's grounded prototype (a running centroid), which is the same
"running prototype" the companion drill recommends, but split per-sense instead of
per-word. **Per-sense splitting is the correct home for the accumulation fix IF a
per-word running prototype proves to be a sense-blend that stops accumulating.**

---

## TOPIC 4 -- THE CEILING (calibrate "as close to 1.0 as possible")

**1.0 is not achievable, and the binding constraint is not the selector -- it is a
stack of three ceilings, the lowest of which is our own shortlist:**

| ceiling | value | source / reason |
|---|---|---|
| **Shortlist recall (HARD structural cap)** | **~0.85** | the correct anchor is in the top-K only ~85% of the time; PERFECT selection cannot exceed this. You cannot select what is not there. |
| Fine-grained WordNet human inter-annotator agreement | ~0.70-0.80 | WordNet's fine granularity is itself the main cause of low IAA (Navigli survey; SemEval); even humans disagree on ~20-30% of fine-grained decisions |
| Best supervised all-words WSD systems (fine-grained) | ~0.80-0.83 F1 | unified SemEval benchmark; transformer bi-encoders / LMMS / EWISER -- and this plateaus around 81% against WordNet as inventory, WITH full context + supervision |
| Most-frequent-sense baseline (fine-grained all-words) | ~0.65 F1 | the standard MFS heuristic; our ~0.45 on the HARD polysemous/low-coherence slice is below this because that slice deliberately excludes the easy dominant-sense wins |
| Coarse-grained WSD ceiling | ~0.90+ | when sense granularity is coarsened, both IAA and system accuracy jump toward 90% |

**The relatedness relaxation helps us and RAISES the effective ceiling.** Our scoring
counts a hit on WordNet subsumption OR `wup>=0.5` -- i.e. it forgives fine-grained
near-misses and behaves like COARSE-grained scoring. That moves our human-agreement/
inventory ceiling from the fine-grained ~0.75 up toward the coarse-grained ~0.90. It
does NOT relax the shortlist-recall cap.

**Net realistic ceiling for the selection mechanism = min(shortlist_recall ~0.85,
coarse_scoring_ceiling ~0.90) ~= 0.85** on the answerable subset. The irreducible floor
below 1.0 is: ~15% shortlist misses (an anchor that was never retrieved cannot be
selected) + a few percent of genuinely-context-underdetermined occurrences even a human
would split on.

**Calibrated target:** from ~0.45, aim for **~0.60-0.70 near-term with context-gating**
(deflated per the lit-scan penalty from the ~2x the grounded re-rank already showed on
the features it had), with **~0.85 as the asymptote for this scoring regime.** Closing
the last 0.85->1.0 requires WIDENING/improving the SHORTLIST (a different problem than
selection), not a better selector. Name that explicitly whenever "toward 1.0" is quoted.

---

## PINNED vs OUR-INVENTION -- one-glance table

| Design element | Status | Anchor |
|---|---|---|
| Word meaning is a context-specific situated simulation, not a static average | PINNED | Barsalou 2003/2009 situated conceptualization |
| Top-down context pre-activates sense-appropriate experiential features | PINNED | Kuperberg predictive-coding N400; Wang/Nour Eddine/Kuperberg 2025 |
| ATL hub + context-sensitive spokes + PFC/IFG semantic control select the right sense in context | PINNED | Patterson 2007; Lambon Ralph 2017; controlled semantic cognition |
| Contextualized > static for disambiguation | PINNED (computational) | Wiedemann 2019; Loureiro 2021 |
| Context-conditioned grounded vector `g(phi_context)` re-rank | OUR-INVENTION, tightly constrained by the above | -- |
| Senses = attractor basins reached by recurrent settling | PINNED | Rodd 2004 |
| Recurrent settling == mutual constraint satisfaction == optimal Bayesian integration | PINNED | McClelland, Mirman, Bolger & Khaitan 2014 |
| Settling raises single-item disambiguation ACCURACY over the current features | NOT SUPPORTED for our case (on-disk: supervised==unsupervised over current features) | -- |
| Per-sense prototype + 1-NN selection | PINNED (computational, proven) | LMMS Loureiro & Jorge 2019; Blevins & Zettlemoyer 2020 |
| Multiple senses = distinct hub sub-states/attractors, not one average | PINNED | Rodd 2004; PDP hub |
| Shortlist recall ~0.85 caps perfect selection | PINNED (our own measurement) | on-disk |
| Fine-grained IAA ~0.70-0.80; coarse ~0.90; SOTA ~0.80-0.83 F1; MFS ~0.65 | PINNED | Navigli survey; SemEval unified benchmark |

---

## DECISIVE RECOMMENDATION

**Prototype ONE thing next: context-gated grounding -- a context-conditioned grounded
re-rank. It is the single lever that changes the FEATURES, which is the only thing the
on-disk evidence leaves headroom in.**

Concrete form, glass-box, our assets, no external LLM at inference:

1. For each occurrence, compute the context-predicted experiential profile
   `binder_ctx = g(phi_context)` -- reuse the predicted-Binder-65 map but drive it from
   the OCCURRENCE'S distributional context vector, not the lemma.
2. Score each distributional top-K shortlist candidate by
   `sim(grounded_proto(candidate), binder_ctx)`; argmax = selection.
3. Combine with the existing distributional score via the reliability-weighted fusion
   the companion drill recommends (so a context-underdetermined occurrence, where
   `binder_ctx` is low-confidence, safely falls back to distributional).

**Why this over the alternatives, decisively:**
- **over recurrent settling:** settling is a better SELECTOR; the on-disk result says
  the selector is already saturated over the current features -- settling has no
  features to work with until context-gating supplies them. Defer it to second-order.
- **over per-sense prototypes:** context-gating gets occurrence-specificity WITHOUT the
  three brittle sense-splitting steps (K per lemma, cluster stability, cluster->WordNet
  alignment), and Barsalou's situated conceptualization says the brain's representation
  is continuous/ad-hoc rather than discretely enumerated anyway. Keep per-sense
  prototypes as the FALLBACK if context-gating plateaus, and as the natural home for the
  accumulation fix if a per-word running prototype proves to be a stuck sense-blend.

**Mandatory controls before believing any lift** (per standing discipline): info-free
shuffle of `phi_context` must drop to chance (proves the context, not the pipeline, is
doing the work); re-fusing the STATIC per-lemma grounded vector must NOT recover the
lift (proves it is the context-conditioning, not just more grounding); measure on the
HARD polysemous/low-coherence slice specifically; report CI half-width + null p95 beside
the margin; verify `binder_ctx` actually turns per-occurrence (the same word in two
different sentences must produce materially different profiles, or the "context-gating"
never reached the representation -- this is the reachability check that the exactly-zero
CI incident teaches).

**Realistic ceiling to aim for:** ~0.60-0.70 near-term, ~0.85 asymptote for this scoring
regime; 1.0 is barred by ~15% shortlist misses (a selection fix cannot recover an anchor
that was never retrieved -- that is a shortlist problem, not a selection problem).

---

## TLDR (plain English)
The machine currently stores ONE "what it feels/looks/does like" description per word,
averaged over all the word's meanings -- so for a word with several meanings that
description is a blur that fits none of them. The brain does not do this: it builds a
FRESH sense-of-the-word every time it reads it, letting the surrounding sentence switch
on the features of the meaning that fits HERE. We already measured that being cleverer
about *picking* the meaning has run out of room -- the ceiling now sits in the blurry
description itself. So the highest-value next build is to compute the description FROM
the sentence context (which meaning does this context call for?) instead of from the
word alone, then pick the candidate meaning whose stored description best matches what
the context is asking for. Do that first; the "settle back and forth" and "keep a
separate description per meaning" ideas only pay off afterwards. And "as close to 1 as
possible" really means "as close to about 85% as possible," because the right meaning is
only in our shortlist about 85% of the time -- the last 15% is a different problem
(making a better shortlist), not a picking problem.

## QUESTIONS
None blocking. One judgement call for the solver: whether to reuse the existing
predicted-Binder-65 map driven by the context vector (leanest, recommended) or train a
small dedicated context->experiential map. Resolve empirically -- start with the reuse,
only train a dedicated map if the reused one does not turn materially per-occurrence.

## NEXT STEPS (for the solver)
1. Build the context-conditioned grounded re-rank: `binder_ctx = g(phi_context)` per
   occurrence, score shortlist candidates against it, fuse reliability-weighted with the
   distributional score, argmax.
2. Run the reachability check FIRST (same word in two sentences -> materially different
   `binder_ctx`); if it does not turn, the feature never reached the scorer and any null
   is a reachability failure, not a ceiling.
3. Run the control battery: info-free shuffle of context -> chance; static per-lemma
   grounding re-fusion must NOT recover the lift; measure on the hard polysemous slice;
   CI + null p95.
4. Only if context-gating plateaus below ~0.85: add per-sense prototypes (cluster
   occurrences by context, ground each cluster, 1-NN) -- and move the accumulation fix
   there (per-sense running centroid).
5. Defer recurrent settling until step 1 supplies context-specific features to reconcile.
6. Quote the ceiling honestly: ~0.85 asymptote for this scoring regime; the 0.85->1.0
   gap is a SHORTLIST-recall problem, not a selection problem.
