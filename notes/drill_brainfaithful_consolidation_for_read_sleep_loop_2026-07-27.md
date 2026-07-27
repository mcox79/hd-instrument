# Drill: brain-faithful consolidation to replace plain mention-averaging in the read/sleep loop

Filed by: research (Opus synthesis over in-house prior-art review + 2 parallel Sonnet lit-scan
sub-agents on anisotropy/representation-degeneration and precision-weighted plasticity; one
sub-agent's transcript had not returned at write time — this note stands on the in-house synthesis
+ the completed/partial lit-scan plus already-verified public literature, flagged where a claim
rests on general knowledge rather than a fresh fetch).

Trigger: the read/sleep loop's current concept-consolidation step is a PLAIN RUNNING MEAN of the
encoder's rep at every mention site for a concept. Symptom: representations REGRESS toward a
centroid (dilute) rather than sharpening with more evidence. Task: find the brain-faithful fix.

Per [[feedback-lit-scan-calibration-penalty]]: P estimates below are deflated 0.15-0.25 from raw
sub-agent/self read; novel-synthesis capped at 0.50.

**KB-check note:** this drill sits on top of a LOT of existing on-disk work that already solved
adjacent pieces of this exact problem. Read in full before drafting: `research_hippocampal_biology_
consolidation_loop_brain_first_2026-07-08.md` (CLS/SWR/CA3/CA1/SHY physiology + Rank1-5 buildable
list), `consolidation_to_structure_implementable_algorithm_2026-07-14.md` (P1-P5: interleaved slow
update, structure/content bottleneck, **Oja/Sanger streaming PCA as the glass-box consolidation
primitive**, anti-smear/pattern-separation, prioritized replay), `research_consolidation_confidence_
permanence_relational_inference_2026-07-14.md` (precision-weighted per-relation confidence/
permanence scalar, Kalman-gain framing, reconsolidation/revisability), `research_consolidation_gate_
signal_mechanism_and_integration_2026-07-16.md` (surprise must be measured LOCALLY not against a
global/flat statistic, or it's worse than useless), `research_brain_confidence_weighted_learning_
consolidation_2026-07-20.md` (self-generated confidence gates update strength), `research_brain_
ingestion_valve_what_to_consolidate_2026-07-20.md` (branching/routing gate, not flat sum). **This
drill does NOT re-derive any of that — it answers the one question those notes left unanswered:
given an item IS selected for consolidation, what should the VECTOR-LEVEL UPDATE RULE be, so that
repeated mentions sharpen instead of diluting the concept representation.** That is a narrower,
more mechanical question than "what to consolidate" (already answered) or "how confident is this
relation" (already answered) — it is specifically about the arithmetic of combining N noisy
mention-site vectors into one concept representation.

---

## HEADLINE

**Plain running-mean averaging fails for two SEPARATE, independently-fixable reasons, and the
brain (and the parallel ML embedding literature) gives a distinct fix for each — conflating them
is why "just weight by confidence" alone will not fully solve this:**

1. **Uniform-weight dilution** (every mention counts 1/n regardless of reliability) — fixed by
   **precision-weighted (Kalman-gain) integration**: the update step shrinks as the concept's own
   confidence grows, and unreliable/noisy mentions are down-weighted rather than counted equally.
   This is the textbook Bayesian-brain fix (Yu & Dayan 2005; Behrens et al. 2007; Mathys et al.
   2011/2014) and it is ALREADY the mechanism the substrate's own `research_consolidation_
   confidence_permanence_relational_inference_2026-07-14.md` proposed for per-relation confidence
   — this drill's contribution is confirming the SAME rule is the right one for the raw
   mention-VECTOR update, not just the scalar confidence/permanence tag.

2. **Regression toward a SHARED, cross-concept centroid** (not just noise-dilution around the
   concept's OWN true value, but a systematic pull toward a corpus-wide common direction that
   makes distinct concepts look more alike as more mentions accumulate) — this is a DIFFERENT
   failure mode than (1), and precision-weighting ALONE does not fix it, because a shared,
   correlated common-mode component is not simply "high-variance noise" that averaging washes
   out — it is a coherent signal, present in every mention, that a plain mean (weighted or not)
   accumulates right alongside the genuine concept-specific signal. **This is the well-documented
   "anisotropy" / "representation degeneration" problem in embedding literatures** (Ethayarajh
   2019; Gao et al. 2019; Mu & Viswanath 2018) — averaged contextual/general-purpose embeddings
   cluster in a narrow cone dominated by a few high-variance shared directions (frequency effects,
   generic-context effects), which is EXACTLY "regression to a centroid, not sharpening" stated in
   ML terms. The fix there is explicit: **subtract/whiten the shared common-mode direction(s)**
   before or during accumulation (all-but-the-top postprocessing, BERT-flow, BERT-whitening,
   contrastive spreading). **The brain's mechanistic analog of this same fix is pattern SEPARATION
   (dentate gyrus) applied BEFORE pattern completion/integration (CA3)** — decorrelate/orthogonalize
   the incoming signal against what's already shared/common, THEN accumulate. The substrate's own
   `consolidation_to_structure_implementable_algorithm_2026-07-14.md` P3/P4 already named both
   halves of this (Oja/Sanger streaming PCA to extract shared structure; DG-style anti-smear
   pattern separation to keep distinct items from being smeared together) but for a DIFFERENT use
   (extracting cross-concept RELATIONAL structure) — this drill's new point is that the SAME
   machinery, pointed the OPPOSITE direction (subtract the dominant shared component from each
   concept's OWN representation, rather than accumulate it as signal), is the fix for dilution.

**The single highest-leverage fix, ranked above alternatives:** a **precision-weighted running
update with an explicit common-mode-subtraction step**, not either one alone. Precision-weighting
without common-mode removal will still slowly converge every concept toward the same generic
"typical mention" direction (just more slowly/more honestly weighted). Common-mode removal without
precision-weighting will still let one noisy/unreliable mention swing the estimate at n=1 the same
as a reliable one. Both together map cleanly onto distinct, well-evidenced brain mechanisms
(precision-weighted plasticity gain; DG-style separation-before-CA3-completion) and onto distinct,
well-evidenced ML fixes (Kalman/variable learning rate; whitening/anisotropy correction) — this
is a compound claim, held at **P_deflated = 0.45** (capped near the novel-synthesis ceiling; each
HALF is independently well-evidenced in its own literature at 0.65-0.75, but their COMBINATION as a
concept-consolidation update rule has no direct precedent found in either literature, hence capped).

---

## 1. BIOLOGY FIRST

**Why doesn't the brain just average all experiences into one concept representation?**

The brain does NOT compute a running arithmetic mean over raw mention-site activations. Every
mechanism below is a way of making sure integration is (a) SELECTIVE (not everything gets in),
(b) WEIGHTED by reliability/precision (not uniform), and (c) STRUCTURE-PRESERVING (distinct
sub-patterns are kept separable, not smeared into one point estimate) — three properties a plain
running mean has none of.

### 1.1 Hippocampal replay is PRIORITIZED, not uniform
Sharp-wave-ripple (SWR) content during offline replay is biased toward novel, rewarded, and
surprising experience (Foster & Wilson 2006, *Nature*, reverse replay scales with reward magnitude;
Ambrose, Pfeiffer & Foster 2016, *Neuron*, forward replay scales with novelty/uncertainty). The
finite nightly SWR budget (~10k-30k events/night) means only a SUBSET of experience is replayed
and consolidated per cycle — this is a SELECTION step upstream of any averaging, already the
subject of the substrate's own ingestion-valve/consolidation-gate notes (07-16, 07-20). Relevant
to THIS drill only insofar as it confirms: consolidation input is already a curated, reliability-
weighted subset by the time any vector-level integration happens — plain mention-averaging
currently throws that away by treating every raw mention-site rep as equally informative.

### 1.2 Precision-weighted plasticity: the brain's actual "averaging" rule is Bayesian, not arithmetic
- **Yu & Dayan 2005** (*Neuron*, canonical): acetylcholine signals expected uncertainty,
  norepinephrine signals unexpected uncertainty; together they set a Kalman-filter-like GAIN on
  prediction-error-driven updates. This is not "add every new sample with weight 1/n" — it is
  "weight each new sample by how much it should be trusted given current confidence AND the
  sample's own reliability."
- **Behrens et al. 2007** (*Nat Neurosci*, canonical): direct behavioral+fMRI evidence humans
  adapt learning rate to environmental volatility (localized to ACC) — the effective "n" the brain
  divides by is NOT the raw count of exposures, it adapts to how stable the underlying thing being
  estimated appears to be.
- **Mathys et al. 2011/2014** (Hierarchical Gaussian Filter, *Front Hum Neurosci*, influential):
  formalizes learning rate as a LIVE precision ratio (belief precision / total precision) at every
  level of a hierarchy — the canonical formal statement of "the update step shrinks as your own
  confidence grows, and grows when the environment looks volatile."
- **Metaplasticity / BCM** (Bienenstock-Cooper-Munro 1982, canonical): a synapse's own history of
  activity changes its future susceptibility to further change — a sliding, history-dependent
  threshold, giving a concrete biological mechanism for "harder to move once moved," i.e. the
  learning rate ITSELF is not fixed, it decays with accumulated confirming evidence. This is a
  DIFFERENT mechanism from Kalman-gain (local synaptic history vs. an inferred global uncertainty
  state) but produces the same qualitative shape (shrinking effective learning rate), so both are
  cited as convergent, non-redundant support for the same design principle.
- **Synaptic tagging and capture** (Frey & Morris 1997, *Nature*, canonical): a single potentiation
  event sets only a short-lived, protein-synthesis-independent "tag"; DURABLE change requires a
  SECOND, independent step (capture of separately-synthesized plasticity proteins, suppliable by
  repetition or by a strong salience signal). This is the direct biological argument for why a
  SINGLE mention should NOT durably move a concept representation the way a naive online-mean
  initialization does (where mention 1 sets 100% of the initial estimate) — the first exposure
  should set a labile, easily-overwritten tag, not a committed update.

### 1.3 Schema-consistency gates HOW FAST and HOW MUCH a new mention integrates
- **Tse et al. 2007/2011** (*Science*, canonical): schema-CONGRUENT new learning consolidates in
  ~24-48h (vs. the normal weeks-long timescale) via a fast mPFC route. Schema-INCONGRUENT material
  triggers a slower, MTL/hippocampal-mediated route producing a richer but more isolated trace.
- **van Kesteren et al. 2012** (SLIMM model, *Trends Neurosci.*, canonical integrative account):
  the relationship is U-SHAPED — highly congruent integrates fast/cheap; highly incongruent gets
  a rich isolated encoding; MODERATELY novel/ambiguous material is the worst-remembered of the
  three regimes. A flat, schema-blind averaging rule cannot express any of this branching.
- **Substrate-relevant point already independently confirmed in-house** (`research_consolidation_
  gate_signal_mechanism_and_integration_2026-07-16.md`): a schema-fit / surprise signal MUST be
  computed LOCALLY (against the concept's own existing structure/neighborhood), never against a
  flat GLOBAL statistic — the landed empirical race cell on this substrate found that multiplying
  a global, schema-blind surprise proxy into schema-fit made things WORSE than schema-fit alone
  (chance-level contribution). The same lesson applies directly here: the "prior" a new mention's
  informativeness is judged against must be the CONCEPT'S OWN current local representation, not a
  corpus-wide statistic — otherwise the "confidence" weight one might compute is itself
  schema-blind and adds noise rather than signal.

### 1.4 Pattern separation (DG) BEFORE pattern completion (CA3) — the anti-smear mechanism
- Dentate gyrus performs ~10x expansion + strong sparsification, orthogonalizing overlapping
  inputs so similar-but-distinct experiences get DISSIMILAR codes, before anything is allowed to
  integrate into an autoassociative CA3 attractor. This is the brain's answer to "how do you keep
  averaging from smearing together things that are similar but should stay distinct" — it does NOT
  rely on the integration step itself to preserve distinctions; it decorrelates FIRST, so that what
  gets integrated afterward is already maximally separated from confounding shared structure.
- **Duszkiewicz, McNamara, Takeuchi & Genzel 2019** (*Trends Neurosci.*, canonical-recent synthesis):
  bifurcates "common novelty" (schema-related, assimilates smoothly) from "distinct novelty"
  (schema-unrelated, produces vivid-but-ENCAPSULATED traces, i.e. explicitly NOT blended into the
  existing schema average) — direct precedent for "some mentions should NOT be smoothly averaged
  in at all, they should be kept as a separate, flagged sub-representation."
- **Schapiro, Turk-Browne, Botvinick & Norman 2017** (*Phil Trans R Soc B*): repeated exposure
  across MANY instances drives reorganization toward abstracted structural regularities — but this
  is a MANY-EXPOSURE, slow process (matching the Saxe/McClelland-Ganguli 2019 PNAS result already
  in-house: gradient descent over interleaved replay learns SHARED/high-singular-value structure
  first, on a timescale that scales inversely with the singular value — meaning dominant SHARED
  directions across many concepts get extracted FAST, and this is exactly the anisotropic
  common-mode component that must be identified and separated OUT of any single concept's own
  representation, not folded into it).

### 1.5 Synaptic homeostasis (SHY) — SELECTIVE downscaling, not a uniform rescale
Tononi & Cirelli: slow-wave sleep drives net AMPA-receptor internalization, but this is Hebbian-
SELECTIVE — synapses that were causally responsible for real output are PROTECTED, synapses that
only ever contributed noise are weakened. This is the biological precedent for "redundant/
uninformative mentions should be down-weighted over time, not simply accumulated at equal weight
forever" — directly supporting a saturating/diminishing-marginal-weight-per-repeated-mention shape
rather than the flat, unbounded 1/n contribution of a running mean.

### 1.6 Complementary Learning Systems (CLS) — WHY two systems, and why one flat average can't do both jobs
McClelland, McNaughton & O'Reilly 1995 (*Psychological Review*, canonical): a single dense network
updated fast on individual items produces catastrophic interference; hippocampus (fast/sparse/
pattern-separated) and neocortex (slow/dense/overlapping) exist because ONE system cannot do both
"acquire a new instance immediately" and "extract shared statistical structure across many
instances" well. **This is the deepest reason plain mention-averaging is the wrong shape at all**:
it is trying to do BOTH jobs (fast acquisition of a new mention's content, AND slow extraction of
the concept's stable "gist") with the SAME single running-mean update, at the SAME timescale, with
NO separation between "this specific mention" and "the concept's accumulated structure." The brain
never does this in one step — there is always a fast/labile stage (tag, hippocampal episode) and a
separate, slower, structure-extracting stage (capture, cortical interleaved replay).

---

## 2. THE MECHANISM MAP — concrete replacement for plain mention-averaging

| Brain principle | Concrete update-rule replacement | Priority |
|---|---|---|
| Precision-weighted plasticity (Yu & Dayan; Behrens; Mathys; Kalman gain) | **Kalman-style update**: `concept_rep_new = concept_rep_old + K_t * (mention_vec_t - concept_rep_old)`, where `K_t = precision_concept / (precision_concept + precision_mention_t)`. `precision_concept` GROWS (K shrinks) as more reliable mentions accumulate — this alone already breaks the flat-1/n shape of a running mean, since K is not fixed at `1/(n+1)`, it depends on the RELATIVE reliability of what's already been integrated vs. the new observation. | **HIGHEST — cheapest, reuses existing signals** |
| Common-mode / anisotropy removal (DG pattern separation; ML whitening/anisotropy-correction) | Before computing `mention_vec_t`'s contribution, **subtract its projection onto the dominant shared direction(s)** across ALL concepts' mention-site reps: maintain a small set of top-PC "common-mode" directions `U` (via streaming Oja's rule / Hebbian GHA, already proposed in-house for a different purpose in P3 of `consolidation_to_structure_implementable_algorithm`), and use `mention_vec_t_decorrelated = mention_vec_t - U U^T mention_vec_t` in the Kalman update above. This is the specific fix for REGRESSION-TOWARD-A-SHARED-CENTROID (distinct from noise dilution) — without it, precision-weighting alone still slowly accumulates the shared/generic component into every concept. | **HIGHEST — this is the one plain-averaging is missing entirely, and it's the one that produces the "regress toward centroid" symptom specifically, not just noisy dilution** |
| Precision itself = informativeness/surprise/coherence/reliability, computed LOCALLY | `precision_mention_t` should be derived from signals the substrate ALREADY computes (schema-fit-to-this-concept's-own-neighborhood, coherence/settling residual, source-reliability) — NOT a corpus-global frequency statistic (the substrate's own landed race-cell result shows global/schema-blind surprise proxies add noise, not signal). Reuse, don't re-derive, per `research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`. | High — feeds the Kalman gain above; don't build a new signal, wire an existing one |
| Synaptic tagging and capture (first exposure = labile tag, not committed update) | New concept mentions (or any mention with low reliability/precision) should update into a SEPARATE fast/labile buffer first (a "tag"), and only get folded into the slow/stable concept representation after a SECOND corroborating signal (repetition, or a strong independent reliability signal) — mirrors the CLS fast/slow split already partially designed in Rank-1/Rank-2 of `research_hippocampal_biology_consolidation_loop_brain_first_2026-07-08.md`. Concretely: `concept_rep` (slow/stable) is updated only during a discrete CONSOLIDATE phase from the ALREADY-TAGGED buffer, never directly from a single raw mention at ingest time. | Medium — architecturally larger change, but directly fixes "one noisy mention shouldn't move an established concept" |
| Schema-consistency U-shaped gating (Tse/Morris; van Kesteren SLIMM) | Route a mention by its LOCAL schema-fit to the concept's existing representation: high-congruence -> fast/cheap fold-in (small Kalman step, high confidence prior); genuinely novel-but-coherent (settles cleanly, doesn't fit current rep) -> flag as a possible new SENSE/exemplar rather than blending (see next row); incongruent-and-incoherent -> reject (noise, don't integrate at all). This is a BRANCH, not a smooth blend — matches the landed empirical finding elsewhere on this substrate that gating/routing beats scalar blending. | Medium — the branch structure is the right SHAPE but is a bigger design commitment than rows 1-3 |
| Pattern separation before completion; prototype dilution documented in-house | For polysemous/multi-sense concepts, do NOT collapse all mentions into ONE mean vector at all — keep a small number of separated exemplar/mixture components (Rosch 1975 prototype theory vs. Medin & Schaffer 1978 / Nosofsky 1986 exemplar theory / GCM: pure single-prototype averaging is the theory shown to lose category-structure information that exemplar/mixture models preserve) and only average WITHIN an assigned component. **In-house confirmation this failure mode is real and severe on this substrate already**: `hdlab/schema_exemplar_bayes.py` documents that 100x hardmax CENTROID pooling of facts loses 96% of recall relative to keeping exemplars — direct, already-measured evidence that collapsing-to-one-centroid is catastrophic here, not merely a suspected risk. | Medium-high leverage for concepts with genuine multi-sense structure; lower priority than rows 1-2 for the base single-sense case |
| SHY-selective homeostatic down-weighting | Redundant, already-well-represented mentions (high recurrence, low marginal information given current `concept_rep`) should contribute a SATURATING (diminishing-return) amount, not a flat constant share — implementable as `precision_mention_t` scaling down with redundancy (cosine similarity of `mention_vec_t` to `concept_rep` already high -> low marginal precision, since it adds confirmatory but non-novel evidence) — this naturally falls out of the Kalman formulation above if precision is defined to include a novelty/marginal-information term, so it is a refinement of row 1, not a new mechanism. | Low-medium — folds into row 1's precision definition, not a separate build |

---

## 3. ANTI-DILUTION SPECIFIC

**Why averaging dilutes, precisely:** with a plain running mean, `concept_rep_new = ((n)*concept_rep_old + mention_vec_t) / (n+1)`, i.e. the update weight on the new sample is EXACTLY `1/(n+1)` regardless of (a) how reliable/informative that mention is, and (b) how much the new mention's DIRECTION agrees with vs. deviates from a corpus-wide shared component. Two independent things go wrong:

1. **Noise-dilution**: if mentions are noisy but zero-mean around the concept's TRUE representation, plain averaging is actually FINE asymptotically (`1/n` variance reduction is the textbook LLN result) — this is NOT the dilution problem by itself. The brain's precision-weighting fix here mostly matters for FINITE-SAMPLE / non-stationary behavior (a volatile or still-forming concept should have a LARGER effective step than 1/(n+1) suggests, and a single wildly unreliable mention should get a SMALLER step) — it sharpens convergence SPEED and robustness, but doesn't by itself explain regression to a *different, shared* point.

2. **Common-mode/centroid-regression** (the actually-reported symptom): if every mention-site rep, regardless of which concept it's a mention of, carries a shared, systematic component (e.g. a dominant "generic sentence/context" direction from a general-purpose encoder — exactly the anisotropy documented in Ethayarajh 2019 and Gao et al. 2019 for contextual embeddings), then averaging N such vectors does NOT wash that shared component out — it accumulates it identically into EVERY concept's representation, at a rate proportional to how much of each mention's variance the shared direction explains. As N grows, every concept's representation converges toward `concept_specific_signal + shared_common_mode`, and since `shared_common_mode` is the SAME across concepts, concepts become MORE similar to each other (i.e., they regress toward a shared centroid) even though each individual concept's own noise is shrinking. **This is a bias problem, not a variance problem — precision-weighting (which only reweights how fast you trust a sample, not what direction that sample points) cannot fix a systematic, coherent bias.** The only fix is to explicitly identify and REMOVE the shared direction before or during accumulation — whitening, all-but-the-top postprocessing (Mu & Viswanath 2018), BERT-flow (Li et al. 2020), BERT-whitening (Su et al. 2021), contrastive spreading (SimCSE-style), or, in brain terms, dentate-gyrus-style pattern separation applied to the mention representation before it's allowed into the (CA3-analog) integration step.

**The brain-faithful counter, stated as one sentence:** weight each mention's contribution by its own local informativeness/reliability (precision-weighted Kalman update, fixes noise-dilution and finite-sample instability) AND strip out the shared/common-mode direction before integrating it (DG-style pattern separation / whitening, fixes centroid-regression) — doing only the first still leaves every concept slowly converging toward the same generic direction, just more efficiently.

---

## 4. PITFALLS

- **Precision-weighting without a genuinely LOCAL precision signal is worse than useless.** The
  substrate's own landed empirical result (`research_consolidation_gate_signal_mechanism_and_
  integration_2026-07-16.md`) shows a GLOBAL/schema-blind surprise/precision proxy actively hurts
  (chance-level, worse when multiplied into a good signal). Any precision term wired into the
  Kalman update here MUST be computed relative to the concept's OWN existing local representation/
  neighborhood, not a corpus-wide statistic — reuse the already-fixed local formulation, don't
  reintroduce the global-statistic bug in a new location.
- **Over-aggressive common-mode removal can strip genuine shared SEMANTIC structure, not just
  noise/anisotropy artifact.** Some cross-concept correlation is real signal (e.g. shared syntactic
  role, shared domain) that later reasoning steps may want. The number of top-PC directions removed
  (`U`'s rank) needs a design-gate precondition check (monotone dose-response, similar discipline
  already used elsewhere on this substrate: sweep rank-removed and confirm a ceiling/ inverted-U,
  not unbounded monotonic improvement — unbounded improvement with more components removed would
  itself be a red flag that something is being gamed, e.g. trivial variance collapse).
- **Schema-congruent generalization and schema-congruent CONFABULATION are the same mechanism, not
  separable ones** (already flagged in-house, `research_consolidation_confidence_permanence_
  relational_inference_2026-07-14.md`, Q6/Alba & Hasher 1983, Payne et al. 2009 DRM false-recall):
  any mechanism that lets schema-fit accelerate integration will ALSO sometimes fold in
  plausible-but-wrong mentions faster. Pre-register this as an expected cost, not a bug to eliminate
  to zero.
- **Tag/capture separation (first mention = labile) adds real state/complexity** — a labile buffer
  distinct from the committed concept representation is an architectural change, not a drop-in
  formula swap like the Kalman/whitening rows. Sequence it AFTER the cheap Kalman+whitening fix is
  validated, not simultaneously (isolate variables).
- **Exemplar/multi-component representations (row 6) can silently reproduce the SAME dilution bug
  ONE LEVEL DOWN** if the within-component averaging is still a plain running mean — the fix is not
  "add exemplars" alone, it's "add exemplars AND apply the same precision+whitening rule within
  each exemplar's own accumulation."
- **Construction-determinism guard, mandatory before any full run:** a fair test needs a REAL
  ungated/unwhitened baseline (current plain-averaging behavior) run on the SAME corpus/order, with
  the Kalman-gain and common-mode-removal steps as the ONLY variables changed, per the substrate's
  standing design-gate discipline.

---

## Cheap decisive test

Reuse whatever harness currently builds concept representations via mention-averaging in the read/
sleep loop (grep for the per-concept accumulation step feeding the codebook/concept store — this
note did not locate the exact call site with certainty before the connection interruption; the
likely candidates based on file/module names encountered this session are the codebook-build /
concept-encoder pipeline and the `hippocampal_encoder.py` consolidation functions — confirm the
exact site before building). Add THREE arms on the same real corpus, same mention stream, same
concept set:
1. **Baseline (current)**: plain running mean, as-is.
2. **Precision-only**: Kalman-gain update with `precision_mention_t` from existing local
   schema-fit/coherence/reliability signals, NO common-mode removal.
3. **Precision + common-mode removal**: as (2), plus subtracting the top-k streaming-PCA shared
   direction(s) from each mention vector before the Kalman step.

**Held-out metric**: pairwise concept-distinctiveness (do genuinely different concepts' final
representations stay separated — e.g. average cosine similarity between UNRELATED concept pairs,
which should be LOW and should NOT rise with more mentions/ingest volume under a correct fix, but
WILL rise under the current plain-averaging baseline if the centroid-regression diagnosis is
correct) plus standard within-concept retrieval/generalization fidelity (must not regress).

## Falsifiable predictions

**HARD-PASS** (pre-registered, >=3 seeds):
- Baseline arm shows pairwise cross-concept similarity RISING measurably as ingest volume grows
  (directly confirms the diagnosed centroid-regression symptom, not just an assumption).
- Precision-only arm slows but does NOT reverse that rise (confirms precision-weighting fixes
  noise-dilution/instability but not the systematic bias, exactly as the ML anisotropy literature
  and this drill's Part 3 argument predict).
- Precision+common-mode-removal arm shows FLAT or DECREASING cross-concept similarity as ingest
  volume grows, while within-concept retrieval fidelity is >= baseline (the compound fix works,
  and doesn't cost accuracy to get it).

**HARD-FAIL** (any one kills/downgrades the candidate):
- Baseline does NOT show rising cross-concept similarity with volume — the "regress to centroid"
  symptom as originally reported may be a different mechanism than anisotropy/common-mode
  contamination (e.g. simple insufficient-data variance, or a labeling/pipeline bug elsewhere),
  and this entire diagnosis needs to be revisited before building the fix.
- Precision+common-mode-removal arm matches precision-only (common-mode removal adds nothing) —
  would mean the shared-direction hypothesis is wrong for this substrate's specific encoder, and
  the residual dilution has a different cause.
- Common-mode removal at any tested rank materially HURTS within-concept retrieval fidelity (the
  removed components were carrying real signal, not just shared-artifact) — would mean the fix
  needs a smarter component-selection criterion (e.g. only remove directions common across
  UNRELATED concepts specifically, not all top-variance directions) rather than blind top-k removal.

---

## Cross-thread synthesis

This drill sits directly on five same-project prior notes and does not duplicate any of them:
`research_hippocampal_biology_consolidation_loop_brain_first_2026-07-08` supplied the CLS/SWR/
SHY physiology and the fast/slow architectural split this drill's tag/capture row reuses;
`consolidation_to_structure_implementable_algorithm_2026-07-14` supplied the Oja/Sanger
streaming-PCA primitive this drill repurposes (same tool, opposite use — extracting the shared
component to REMOVE it here, vs. extracting it as target signal there — genuinely complementary,
not redundant, since both cases benefit from having the shared-direction detector as a general
substrate primitive); `research_consolidation_confidence_permanence_relational_inference_2026-07-14`
supplied the Kalman-gain/precision-weighted per-relation confidence framing this drill applies at
the raw-vector level instead of the scalar-confidence level; `research_consolidation_gate_signal_
mechanism_and_integration_2026-07-16` supplied the hard empirical lesson (local, not global,
statistics) that gates how the precision term here must be computed; `research_brain_confidence_
weighted_learning_consolidation_2026-07-20` and `research_brain_ingestion_valve_what_to_
consolidate_2026-07-20` supplied the broader selective-gating context this drill assumes as already
having selected WHAT to consolidate, focusing narrowly on HOW the vector update itself should work.
The genuinely NEW contribution of this drill is the anisotropy/representation-degeneration framing
(Ethayarajh 2019; Gao et al. 2019; Mu & Viswanath 2018) as the precise ML-literature parallel that
explains WHY precision-weighting alone is insufficient for the specific "regress to centroid"
symptom (as opposed to generic noise-dilution), and the resulting two-part compound fix.

## Substrate-product implications

If validated: the product gets a concept-representation-formation mechanism that genuinely
SHARPENS with more reading rather than degrading — directly load-bearing for the entire read/sleep
loop's core promise ("reads better over time," per the loop's own stated success criteria in
`ingestion_learn_sleep_loop_2026-07-24.md`). It is also cheap: rows 1-2 of the mechanism map are
formula-level changes to an existing accumulation step plus one new lightweight streaming-PCA
tracker, not a new architecture. If it HARD-FAILs on the "baseline doesn't actually show rising
cross-concept similarity" ground, that is still valuable — it would redirect the diagnosis away
from anisotropy/common-mode contamination toward a simpler variance/data-volume explanation, saving
effort that would otherwise go into building whitening machinery for a problem that doesn't have
that specific cause.

## Citations (verified/high-confidence count: 24 distinct sources; some cited from the completed
in-house prior-art notes' own already-cross-checked citation lists rather than a fresh fetch this
session, flagged as such; anisotropy/whitening citations are standard, well-known ML literature)

**Precision-weighting / Bayesian brain:** Yu, A.J. & Dayan, P. (2005). *Neuron* (ACh/NE precision).
Behrens, T.E.J. et al. (2007). *Nat Neurosci* (volatility-adapted learning rate). Mathys, C. et al.
(2011, 2014). Hierarchical Gaussian Filter, *Front Hum Neurosci*. Kalman, R.E. (1960), original
filter (engineering canon, cited for the formal update-rule form).

**Metaplasticity / tagging:** Bienenstock, Cooper & Munro (1982), BCM theory (canonical). Frey,
J.-U. & Morris, R.G.M. (1997). Synaptic tagging and capture, *Nature* 385:533. Redondo, R.L. &
Morris, R.G.M. (2011). *Nat Rev Neurosci* 12:17 (secondary review).

**Schema-consistency:** Tse, D. et al. (2007, 2011). *Science* 316:76; 333:891. van Kesteren,
M.T.R. et al. (2012). SLIMM, *Trends Neurosci.* 35:211.

**Pattern separation / novelty routing:** Duszkiewicz, A.J., McNamara, C.G., Takeuchi, T. & Genzel,
L. (2019). *Trends Neurosci.* (common vs. distinct novelty). Schapiro, A.C., Turk-Browne, N.B.,
Botvinick, M.M. & Norman, K.A. (2017). *Phil Trans R Soc B* (structural-regularity extraction over
repeated exposure). Saxe, A., McClelland, J. & Ganguli, S. (2019). *PNAS* (deep linear nets learn
shared/high-singular-value structure first — already in-house, re-cited for the common-mode-extracts-
fast argument).

**CLS foundation:** McClelland, J.L., McNaughton, B.L. & O'Reilly, R.C. (1995). *Psychological
Review* 102:419 (canonical).

**Synaptic homeostasis:** Tononi, G. & Cirelli, C., SHY (canonical, Hebbian-selective downscaling).

**Anisotropy / representation degeneration (ML, the new angle this drill adds):** Ethayarajh, K.
(2019). "How Contextual are Contextualized Word Representations?" *EMNLP* (anisotropy in BERT/
GPT-2/ELMo layers, well-established). Gao, J. et al. (2019). "Representation Degeneration Problem
in Training Natural Language Generation Models." *ICLR* (word embeddings cluster in a narrow cone).
Mu, J. & Viswanath, P. (2018). "All-but-the-Top: Simple and Effective Postprocessing for Word
Representations." (top-PC removal fixes isotropy, well-cited standard technique). Li, B. et al.
(2020). "On the Sentence Embeddings from Pre-trained Language Models" (BERT-flow). Su, J. et al.
(2021). "Whitening Sentence Representations for Better Semantics and Faster Retrieval" (BERT-
whitening) — all four of these are standard, frequently-cited NLP results; flagged as
general-knowledge-confirmed rather than freshly re-verified this session due to a mid-session
connection interruption, so treat the exact citation details (venue/year) as high-confidence but
not re-fetched today.

**Prototype vs. exemplar theory:** Rosch, E. (1975), prototype theory (canonical). Medin, D.L. &
Schaffer, M.M. (1978), exemplar theory (canonical). Nosofsky, R.M. (1986), Generalized Context
Model (canonical) — standard cognitive-psychology citations, general-knowledge-confirmed.

**In-house empirical confirmation (not external lit, cited for cross-thread accuracy):**
`hdlab/schema_exemplar_bayes.py` (100x hardmax centroid pooling loses 96% recall vs. exemplar-based
routing — direct, already-measured, on-substrate evidence that centroid-collapse is a real and
severe failure mode here, independent of today's new mention-averaging report).

**Note on this drill's evidentiary status:** two Sonnet lit-scan sub-agents were dispatched
(anisotropy/dilution mechanisms; precision-weighted plasticity formulas) but a connection
interruption occurred before their full transcripts could be integrated into this note. The
citations above for the anisotropy/ML section and some of the neuroscience formalism rest on
strong general knowledge rather than a freshly re-verified fetch this session. Per calibration
discipline this is an ADDITIONAL reason to hold P_deflated at 0.45 rather than higher — treat the
specific paper-level citations (venue/year) as likely-correct-but-not-re-verified-today, while the
underlying mechanisms (precision-weighting is real and canonical; anisotropy in averaged embeddings
is real and canonical; DG pattern separation is real and canonical) are high-confidence regardless
of citation-detail re-verification.
