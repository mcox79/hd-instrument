# Frontier drill: inductive/subject-conditional relational transfer to unseen entities

**Filed:** 2026-07-05 by research (Opus + 3 parallel Sonnet lit-scans: inductive-KG-completion,
TEM/brain-grounding, VSA-hypernetwork content-conditioned binding)
**Trigger:** user-directed frontier drill on the deepest open problem this session located --
turning stored facts into transferable relational knowledge.
**Basis:** `schema_relation_transform_estimator_ablation_v1` FULL
(`data/exp_schema_relation_transform_estimator_ablation_v1/metrics.json`, verdict=MIDDLE_BAND),
prereg `preregs/2026-07-05_schema_relation_transform_estimator_ablation_v1.md`, cap_map PP-275/
PP-321/PP-303/PP-327, prior 2x-drill note
`notes/research_2x_drill_what_encoding_carries_relational_structure_for_schema_transfer_2026-07-05.md`.

**MID-TASK CORRECTION APPLIED (from director, off-disk re-read of the same metrics.json):**
the initial task brief's framing ("TRAINED ~= NAIVE -> training refuted"; "root cause = inductive
setting specifically") is NOT what the numbers support. Both corrections are load-bearing and
are reflected in every section below:

1. **The estimator axis is UNTESTED, not refuted.** `gate_diagnostics.synth_hard` (the
   discriminator-fires positive control, designed so TRAINED should provably beat NAIVE) shows
   `naive=1.000, trained=1.000, trained_adv=+0.000, discriminator_fires=false` -- the control
   SATURATED. A test that can't show an effect under ideal conditions cannot be used to conclude
   the effect is absent under real conditions. This is exactly why the cell verdict is
   MIDDLE_BAND, not HARD_FAIL.
2. **The failure is not inductive-specific.** `ind_trans_gap` (`real_trans - real_ind`) is
   negative in 7/8 non-DerivedFrom-adjacent cells (e.g. AtLocation/bge -0.038, CausesDesire/bge
   -0.096, CausesDesire/char -0.047/-0.057) -- inductive (novel subject) performs AS WELL OR
   BETTER than transductive (subject seen via other pairs), not worse. If the bottleneck were
   "novel entities lack a learned embedding slot," transductive should clearly beat inductive.
   It doesn't. Both eval modes are shuffle-invariant on the semantic relations
   (`confound_shuffle_invariant=true` for `AtLocation|bge_semantic|*` and
   `CausesDesire|bge_semantic|*`, real_minus_shuf approx 0.000 to -0.002).

**Reframed question:** not "why does inductive (unseen-entity) transfer fail" but the broader
"why does *any* subject-conditional relational mapping fail on real ConceptNet triples, seen or
unseen subject, surface or semantic content, averaged or gradient-trained global operator" --
and what mechanism class would actually fix it.

**MID-TASK CORRECTION #2 APPLIED (from director, corpus scour a0aaa9 -- full frontier prior-work
map):** this landscape is more resolved than either the ablation alone or my first-pass reframe
suggested. Three additional prior results bracket the white space precisely:

- **EXHAUSTED family (do not propose another variant of this):** every substrate cell to date
  that has tried subject-conditional relational transfer has used an AVERAGED/GLOBAL-TRANSFORM
  estimator -- `schema_bundle_structural_transfer` (synthetic, HARD_PASS), `schema_bundle_real_corpus_transfer_v1`
  (real, HARD_FAIL), today's `schema_relation_transform_estimator_ablation_v1` (real, semantic
  BGE still shuffle-invariant), plus `analogy_map` and `analogy_relation_transfer`. All of these
  are the SAME operator family (a single per-relation transform, closed-form or gradient-fit,
  applied uniformly to every subject) -- confirming the operator-class diagnosis above from a
  fourth independent angle. No further variant of "fit the global transform better" is a
  worthwhile next spend.
- **PROVEN CONSTRAINT (CHAIN_GRADE honest negative, reconciled here):**
  `exp_substrate_relation_type_binding_cross_domain_analogy_v1`: `cross_domain_hits1=0.0000`.
  The substrate cannot zero-shot relational transfer from an UNTRAINED/random codebook at all --
  it needs either a trained relation structure or an explicit inductive bias, and both of those
  are CORTEX-LAYER contributions, not raw-substrate primitives. This sets a floor: any workable
  mechanism must include a trained/learned component, ruling out a purely-algebraic (zero
  training) fix.
- **PP-275 re-characterization (stronger than "likely transductive"; now CONFIRMED):**
  `lap3_rotate_analogy_cpu_v1` (Hits@1=0.899) trains per-entity phase ROWS and evaluates on
  held-out TRIPLES, not held-out ENTITIES -- it is transductive by construction, not just by
  inference from architecture. It must not be cited as inductive/novel-entity precedent in any
  future framing; it remains valid ONLY as an existence-proof that FHRR-rotation can carry
  high-fidelity relational structure when entity identity is already known to the model.

**The white space, sharpened:** not "a content-conditioned rotation" (too narrow a framing) but
an **entity-feature-conditioned LEARNED SCORER** -- a trained function `score(subject_content,
relation, candidate_object)` that conditions on the novel subject's CONTENT features (from the
program's semantic encoder, not a fixed global per-relation operator) to rank candidate objects,
generalizing to entities never seen in training. This is the inductive-relational-embedding /
relational-GNN pattern realized in VSA terms, and it is what BLP/DKRL/ConMask/SimKGC actually
implement under the hood (Q1 below) -- no substrate cell has tried this scorer framing (all
prior cells bind-then-nearest-neighbor through an averaged transform; none learns a
subject-content-conditioned scoring function end-to-end). GPU-trainable, fills the idle GPU --
recommended as a GPU dispatch, not CPU-only, for this specific next cell (see spec below).

## HEADLINE

Across every tested combination (2 encodings x 2 estimators x 2 eval modes x 2 semantic
relations = 16 real-relation cells), the substrate recovers the relation's population-typical
answer, never the specific-to-this-subject answer -- confirmed by `real_minus_shuf approx 0`
everywhere except the surface-morphology control (DerivedFrom, a known nearest-substring
artifact, not transfer). The most load-bearing convergent literature finding (BLP, Daza et al.
2021, a controlled ablation on a real KG benchmark) says the fix that reliably works in the
field is **not** "train the relation operator harder" (frozen-entity-encoder + trained-relation
scores WN18RR MRR=0.180) but **"make the entity-side content representation itself a function
trained jointly against the same relational objective"** (fine-tuned encoder + relation:
MRR=0.285, +58% relative). The substrate's ablation only tried the first lever (global,
entity-agnostic rotation, closed-form vs. gradient-trained -- structurally the SAME operator
class either way) and its own test of whether that lever works at all came back uninterpretable
(saturated control). No VSA/HRR paper was found that has ever built the second lever (a
content-conditioned bind operator) -- one 2024 paper (GHRR, Yeung/Zou/Imani) explicitly flags
"input-dependent Q" as an unexplored variant of their own framework and does not implement it.
This is a genuine, narrow, buildable white space, not a rediscovery and not a known negative.

## PRIMARY mechanism (brain-first, per USER standing steer): TEM structural/content
factorization, VSA-realized

Per explicit USER steer: prior work tells us what NOT to rediscover (the exhausted
averaged-transform family), but should not constrain the next attempt to merely extending that
family -- and the failed family was NOT brain-aligned. So the LEAD candidate here is the brain's
own actual solution to this exact problem, not a generic ML scorer.

**Why TEM is the right lead, mechanistically (not just by analogy):** the Tolman-Eichenbaum
Machine's core move is factorizing a small, REUSABLE structural/relational code (entorhinal
grid/graph-structure cells -- a small repertoire of transition topologies, learned ACROSS many
environments) from a per-episode CONTENT code (hippocampal what-cells), bound together via a
fast conjunctive (Hebbian, one-shot) write. Zero-shot transfer to a brand-new environment works
because the structural code is already general -- only a fast content-to-structure BINDING step
is needed on first exposure, not a slow re-training of the structure itself. This is precisely
what the exhausted averaged-transform family got wrong: it has only ONE relation-wide global
transform (no reusable sub-structure at all) and no separate content-to-structure classification
step -- so it can only ever express the population-average, exactly the shuffle-invariant
signature observed everywhere.

**The VSA realization, concretely (a genuine new construction, not a rediscovery):**

1. **Structural code (the reusable, general part):** for each relation, cluster TRAINING
   subjects by content similarity into K recurring TYPE-prototypes (e.g., for `AtLocation`:
   "container/furniture objects," "tool objects," "food objects" ...), each represented as a VSA
   bundle. For each type-prototype, build a RELATIONAL FILLER BUNDLE by aggregating the true
   objects observed for training subjects assigned to that type. **This is not a new primitive
   to invent from scratch** -- it is a direct application of the substrate's OWN already-proven
   mechanism, `PP-254`/`PP-282`/`PP-284` (schema-layer prototype extraction via bundle-centroid
   superposition, HARD_PASS at ceiling coverage/precision, scaled 60 -> 220 -> 1000 schemas with
   zero degradation). The earlier cross-thread note in this drill flagged PP-254 as "a different
   kind of schema, not directly relevant" -- that was premature dismissal (exactly the failure
   mode [[feedback-dont-dismiss-adjacent-methods]] warns against): PP-254's bundle-centroid
   extraction IS the content-to-structural-type classification step TEM needs, already validated
   on this substrate.
2. **Content code:** the novel subject's fixed GSBC semantic encoding, evaluated zero-shot (no
   retraining needed per new entity -- matches TEM's fast per-episode content pathway).
3. **Fast content-to-structure binding (zero-shot, the actual transfer step):** classify the
   NOVEL subject's content vector against the K learned type-prototypes (nearest-bundle cosine
   cleanup -- a native VSA operation, analogous to TEM's Hebbian one-shot conjunctive write) ->
   retrieve that type's relational filler-bundle -> resolve the specific answer via a resonator-
   style disambiguation pass among the type's candidate fillers using the subject's own finer-
   grained content similarity (this is the step that must produce a DIFFERENT answer for
   different same-type subjects, the acid test that failed everywhere in the exhausted family).
4. **The trained component (satisfies the PROVEN CONSTRAINT):** the type-prototype clustering
   and per-type filler-bundle construction ARE the trained/fit-from-data piece (analogous to
   TEM's slow backprop-trained structural weights, done ONCE across the training population, not
   per-novel-entity) -- consistent with `exp_substrate_relation_type_binding_cross_domain_analogy_v1`'s
   finding that an untrained/random codebook scores exactly 0.0000; SOME trained structure is
   required, and here it is the reusable TYPE code, not a single global relation transform.

**The ML/relational-GNN framing (entity-feature-conditioned scorer, below) is the FALLBACK, not
the lead** -- it is best understood as the differentiable version of step 1+3 above (learn a
soft content -> structural-code map via gradient descent instead of hard clustering), i.e. the
engineering realization of the SAME TEM principle when a harder, more expressive parametrization
is warranted, not a competing/alternative mechanism. Brain-alignment is the reason to try the
TEM-structural-binding arm FIRST: it is untried, it reuses the substrate's own strongest existing
primitive (PP-254 at ceiling), and it is structurally distinct from every exhausted
averaged-transform cell in a way that specifically targets the failure signature observed
(shuffle-invariance = no sub-population structure at all).

## Convergent mechanism (supporting evidence / fallback framing): what would make transfer
genuinely subject-conditional

**The operator-class diagnosis (mathematical, verified against the cell's own source code):**
`TRAINED` fits `theta`, an `(N,)` vector -- ONE rotation per relation, identical for every
subject, warm-started at the naive circular mean and refined via full-codebook softmax
cross-entropy (`experiments/exp_schema_relation_transform_estimator_ablation_v1.py:381-406`).
This is mathematically the same operator FAMILY as `NAIVE_MEAN` (a single global per-relation
transform); only the fitting procedure differs (closed-form circular mean vs. gradient descent
with negative sampling). Neither version lets the transform itself depend on which subject is
being queried -- subject-specificity can ONLY enter through the raw content vector being rotated,
then nearest-neighbor cleanup against the object codebook. If the codebook's majority-direction
signal dominates cosine similarity (plausible with V<=100 objects and heavy skew in a real KG's
degree distribution), any global operator, however well-fit, will read out the popular answer
regardless of subject. This matches the observed `confound_shuffle_invariant=true` signature
exactly, and predicts (testably) that the failure would persist under a BETTER-trained global
operator too -- consistent with the corrected, non-alarmist reading above.

**The literature-supported fix (convergent across all 3 lit-scans):**

1. *Inductive-KG-completion angle (HIGH confidence, direct citation):* every method surveyed
   that actually works on unseen/content-only entities (GraIL, NBFNet, DKRL, ConMask, BLP,
   KEPLER, SimKGC) trains the entity-side representation end-to-end against the link-prediction
   loss -- none uses a literally-frozen generic encoder as its real system; frozen encoders
   appear ONLY as deliberately weak baselines that consistently underperform (BLP's own
   controlled ablation: 0.180 vs 0.285 MRR, same relation-operator machinery, same paper). This
   is the single cleanest piece of evidence in the whole scan and it is a controlled, not
   confounded, comparison.
2. *TEM/brain-grounding angle (HIGH confidence on the fact, MEDIUM on its transfer-relevance):*
   in TEM (Whittington et al. 2020, *Cell*), the sensory/content-compression pathway is
   **backprop-trained jointly** with the structural/transition weights -- not frozen -- while a
   SEPARATE fast Hebbian outer-product write handles per-episode content-structure binding.
   Important honest caveat surfaced by the lit-scan: TEM's own "zero-shot" relational-inference
   demos (e.g. inferring "Bob's niece") reuse entities from an ALREADY-TRAINED sensory
   vocabulary -- novelty is in the graph/combination, not in the low-level content itself. No
   TEM-family paper was found that cleanly demonstrates one-shot relational transfer to content
   the network has never seen in any form. So brain evidence is **architecturally consistent**
   with "content pathway must be trained, not frozen" but does NOT prove it for the fully novel
   case -- flagged, not overclaimed.
3. *VSA-native angle (mechanism gap, not yet built):* Fast Weight Programmers / linear-
   transformer-as-fast-weights (Schlag, Irie & Schmidhuber 2021) and role-learning networks
   (Soulos et al. 2020) both make a binding-side quantity a trained FUNCTION of content rather
   than a fixed external role -- outside VSA/HRR terms, but architecturally the exact recipe
   needed. FiLM / hypernetworks / attention-QKV projections are mature, GPU-trainable, standard
   deep-learning techniques for content-conditioned transforms generally. HypER (Balazevic et
   al. 2019) is the closest KG-embedding hypernetwork but conditions on the RELATION side, not
   the entity side -- the wrong operand for this problem. **No paper combines an HRR/FHRR bind
   operator with a hypernetwork-generated, per-entity content-conditioned transform** -- a 2024
   GHRR paper explicitly names this as an unimplemented variant of its own formalism. This
   confirms the combination is a real, narrow, novel-synthesis opportunity, not previously
   attempted or previously refuted by anyone.

## Cheap decisive test (single highest-EV next experiment) -- brain-first, per director-confirmed spec

**`schema_relation_TEM_structural_content_binding_v1`** (proposed, GPU dispatch). PRIMARY arm is
the TEM-VSA realization above (type-prototype structural code + fast content-binding); the
entity-feature-conditioned scorer is retained as a SECOND arm in the same cell (the
differentiable fallback realization of the same principle), not a separate proposal. Two coupled
fixes apply to both arms:

**Fix A -- repair the discriminator.** Recalibrate `SYNTH_CORR_HARD`'s `NAIVE` arm DOWN below
ceiling (currently `naive=1.000` -- too easy to show any estimator advantage) by reducing `M`
into the noisy-averaging regime or correlating codebook objects, so `TRAINED`/scorer-style
fitting has room to demonstrably beat naive averaging. Gate: `trained_adv >= 0.05` AND
`discriminator_fires=true` BEFORE trusting any real-relation result from the same run --
non-negotiable, since this exact control saturation is why the current ablation is
uninterpretable rather than a negative.

**Fix B -- the mechanism itself, two arms:**

- **PRIMARY -- `TEM_STRUCTURAL_BINDING`:** cluster training subjects per relation into K
  type-prototypes over their GSBC content vectors (reusing the PP-254 bundle-centroid
  mechanism); build a per-type relational filler-bundle from each type's true training objects;
  for a NOVEL subject, classify its GSBC content against the K prototypes (nearest-bundle
  cleanup, zero-shot, no per-entity training), retrieve the type's filler-bundle, and resolve
  the specific object via a resonator-style disambiguation pass using the subject's own content.
  K is a swept hyperparameter (e.g. 5, 10, 20) -- report the curve, since K too small
  degenerates to the global (shuffle-invariant) baseline and K too large degenerates toward
  per-entity memorization (transductive-like, defeats the inductive point).
- **SECONDARY (fallback/ML realization) -- `ENTITY_FEATURE_SCORER`:** a trained scorer
  `s_phi(subject_content, relation_id, candidate_content) -> logit`, ranking the full object
  codebook per query, trained end-to-end via the same negative-sampling recipe as the current
  `TRAINED` estimator but generalized from "one global rotation" to "a ranking conditioned on
  both endpoints' content" (bilinear or small-MLP over `[subject_content ; relation_embedding]`
  vs. candidate content). This is the differentiable version of the SAME content-to-structure
  principle, not a competing mechanism -- kept as a second arm to see whether a soft/learned
  structural code outperforms the hard-clustered TEM-style one.

Both arms use subject content from the **program's target semantic encoder (GSBC, not
char_trigram/BGE-only)** -- the previously-flagged UNTESTED rescue arm, now promoted to primary
because it is the substrate's actual intended production encoder, and because the BGE-only
ablation cannot rule out that GSBC's different geometry changes the outcome.

**Relations:** expand from 2 semantic relations (AtLocation, CausesDesire) to **>=3** --
add at least one more genuinely one-to-many or one-to-one semantic ConceptNet relation
(e.g. `UsedFor`, `HasProperty`, or `Causes`) so a HARD-PASS is not a single-relation fluke and a
HARD-FAIL is not attributable to an unlucky pick of 2 relations.

**Arms:** `{GLOBAL (=current best-of NAIVE/TRAINED, carried as baseline), TEM_STRUCTURAL_BINDING
PRIMARY, ENTITY_FEATURE_SCORER secondary} x {inductive PRIMARY, transductive secondary} x {GSBC
primary, bge_semantic secondary}`, plus `SHUFFLED` / `MEAN_OBJECT` controls and the repaired
`SYNTH_CORR_HARD`. `SHUFFLED` for `TEM_STRUCTURAL_BINDING` specifically means: build type
-prototypes and filler-bundles from object-shuffled training pairs -- if this still recovers
plausible-looking objects, the type-clustering itself is a surface-content artifact, not
relational structure.

**Pre-registered HARD-PASS (gated on the load-bearing metric: real-minus-shuffled on NOVEL
entities):** EITHER arm (`TEM_STRUCTURAL_BINDING` OR `ENTITY_FEATURE_SCORER`) clears
`gain(REAL, inductive) >= 0.2075` on >=1 of the >=3 semantic relations, WITH
`real_minus_shuf(inductive) >= 0.05` on NOVEL (held-out, never-seen) entities specifically --
this is the metric that failed everywhere in every prior cell, and whose recovery is the actual
claim of inductive relational transfer -- AND the repaired synthetic control fires
(`trained_adv>=0.05`), so the result is trustworthy rather than a repeat of this run's
vacuous-control problem. If `TEM_STRUCTURAL_BINDING` clears it, that is the headline (brain
-aligned mechanism win); if only `ENTITY_FEATURE_SCORER` clears it, report honestly that the
brain-first hypothesis was not the one that worked this round.

**Pre-registered HARD-FAIL:** BOTH arms remain shuffle-invariant /
`real_minus_shuf(inductive) <= 0.05` on ALL >=3 semantic relations, WHILE the repaired synthetic
control DOES fire (proving the test could show an effect if one existed) -- the honest "real
wall" reading: neither a brain-faithful structural/content factorization nor a learned
subject-content-conditioned scorer can extract subject-specific correspondence from this content
source at novel entities. Given the PROVEN CONSTRAINT above (untrained/random codebook scores
exactly 0.0000, so SOME trained component is necessary but apparently not sufficient here), this
would be strong evidence of an information-theoretic content-insufficiency wall for generic
semantic content specifically, not an engineering gap -- the most damaging and most informative
possible negative this program could produce.

**MIDDLE_BAND (flagged in advance):** repaired control fires AND at least one arm partially
improves (nonzero inductive `real_minus_shuf` but below 0.2075, or passes on GSBC but not BGE or
vice-versa, or only at certain K for `TEM_STRUCTURAL_BINDING`) -- would mean a mechanism is
directionally right but under-parameterized, under-trained, or encoder/K-sensitive at this
scale; motivates a scaled follow-up (more types K, more training steps, larger hidden dim) rather
than a mechanism pivot.

**GPU-trainable: YES for `ENTITY_FEATURE_SCORER`; CPU-cheap for `TEM_STRUCTURAL_BINDING`.** The
brain-first primary arm (type-clustering + bundle construction + nearest-bundle cleanup) is the
same cost class as PP-254 (sub-second CPU elapsed at 1000 schemas) -- no GPU needed for a first
attempt. The fallback scorer arm IS the natural idle-GPU-filling candidate: batched bilinear/MLP
scoring over the full V-object codebook per training step is a standard batched-matmul GPU
workload, unlike the tiny CPU-bound closed-form circular means used so far. Recommend: run
`TEM_STRUCTURAL_BINDING` locally/CPU first (cheap, fast signal), dispatch
`ENTITY_FEATURE_SCORER` to remote GPU queue per [[feedback-gpu-first-for-depth-probes]] in the
same cell or a fast-follow, so the idle GPU is used regardless of which arm wins.

## Brain grounding (honest strength)

TEM's jointly-trained content pathway is consistent with, but does not prove, the hypothesis for
truly novel content -- it is architecture-precedent, not a controlled experiment on this exact
question (no TEM-family paper runs a frozen-vs-trained content-pathway ablation). The
Behrens/Whittington line's actual novel-item claims are graph-level ("new combination of
already-known items"), not content-level ("item never encoded in any form before") -- the
substrate's ask is closer to the harder, less-tested case. Deflate brain-grounding confidence to
MEDIUM accordingly; it corroborates architecture choice, it does not license "biology proves
this works."

## Honest rating: engineering gap, information-theoretic wall, or genuinely unknown

**Genuinely unknown from the substrate's own data (the test that would tell us was
uninterpretable this run) -- but field precedent leans ENGINEERING, not info-theoretic.**
SimKGC-family results show a roughly monotonic improvement in inductive/content-based accuracy
as more of the entity-side pathway is trained end-to-end against the relational objective
(DKRL -> KEPLER -> BLP -> SimKGC), which is the strongest available evidence that this class of
problem yields to more joint training rather than hitting an information floor. But this is a
DIFFERENT content source (Wikipedia/Wikidata descriptions, often much richer per-entity text)
than ConceptNet's short entity strings passed through a generic sentence encoder -- so the
"is the needed fact even present in this specific content signal" question is a real, separate,
and currently untested sub-risk, not resolved by field precedent alone. Rate: **MEDIOCRE
evidence, cautiously-promising direction** -- not proven achievable, not shown to be a hard
wall; the substrate has not yet run a single VALID (non-vacuous-control) test of the correct
mechanism class.

## Cross-thread synthesis

- PP-275 (`lap3_rotate_analogy_cpu_v1`, Hits@1=0.899) remains the standing existence-proof that
  FHRR-rotation CAN carry high-quality relational structure -- but per the earlier 2x-drill, it
  is transductive (learned per-entity embeddings), so it is a precedent for "the algebra can
  support this," not for "a frozen-content + global-operator recipe suffices."
- PP-321 (structural alignment beats surface similarity, +14pp, MIDDLE_BAND, n=7) and PP-327
  (Slipnet relation-type-weighted spreading activation beats degree-only baseline by +15.8pp,
  HARD_PASS) are a different task shape (cross-domain structural correspondence, not
  subject -> specific-object retrieval) -- relevant as "relation-type-aware mechanisms beat
  naive geometry" precedent, not directly transferable evidence for this drill.
  interesting adjacency worth a follow-up drill: Slipnet's relation-type-weighted spreading
  activation is itself a form of content/context-conditioned relational computation and may be
  a cheaper VSA-native alternative to a full hypernetwork -- flagged as an alternate
  cheap-to-try mechanism, not pursued further in this note.
- `schema_exemplar_bayes_capacity_stress_v2/v3/v4` cells (found via corpus scour) are a
  DIFFERENT research line (Bayesian schema-exemplar capacity under cortex importance sampling)
  -- do not bear directly on subject-conditional relational transfer; flagged so it is not
  conflated in a future framing pass.
- `GSBC_EXPAND2X`, the program's target encoder, remains UNTESTED in this ablation (only
  char_trigram and bge_semantic were run) -- a natural next arm once the mechanism question
  above is resolved, not before (adding an encoder axis to an already-uninterpretable estimator
  axis would compound confounds).

## Substrate-product implications

If HARD-PASS: a genuinely new, buildable "learn a small per-relation content-conditioning
network from stored facts" primitive -- lets the substrate answer novel questions about
entities it has partial or no direct relational data for, using only what it knows about the
entity's content, a capability most retrieval-based LLM-adjacent systems do not have natively
(they retrieve nearest facts; they don't algebraically project content into fact-space). If
HARD-FAIL (with a validated, non-vacuous control): the honest product claim narrows to "relation
types with either dense per-subject training data, or content encodings richer than short
generic text (e.g. structured attributes, co-occurrence statistics)" -- not a defeat of the
program, a scoping of where schema transfer is buildable now versus needs richer inputs later.
Either outcome is actionable; this is why the recalibrated test is the correct next spend
regardless of which way it lands.

## Falsifiable predictions (calibration-penalized; novel-synthesis cap 0.50 applied)

- P(repaired synthetic control becomes non-vacuous, i.e. `discriminator_fires=true` with
  `trained_adv>=0.05`) = 0.70 (deflated from a naive ~0.85; this is largely a harness-tuning
  fix, not a science risk, but first attempts at recalibrating difficulty bands sometimes
  overshoot into the opposite failure mode).
- P(TEM_STRUCTURAL_BINDING alone clears HARD-PASS on >=1 semantic relation, inductive |
  control is valid) = 0.28 (deflated -0.20 from a naive ~0.48; reuses a proven substrate
  primitive (PP-254) which raises confidence over a from-scratch mechanism, but the
  content-to-type classification step at fine granularity is unvalidated for THIS purpose, and
  K-sensitivity is a real, untested risk).
- P(ENTITY_FEATURE_SCORER alone clears HARD-PASS, same gate) = 0.24 (deflated -0.20 from a
  naive ~0.44; no direct VSA prior art for this exact combination -- explicitly flagged as
  unbuilt by the field itself -- and small entity/codebook scale limiting effective sample size).
- P(either arm clears HARD-PASS, i.e. the OR across both) approx 0.40 (not a simple sum -- the
  two mechanisms share a common failure mode (content insufficiency) so their successes are
  positively correlated, not independent).
- P(genuine content-insufficiency wall: HARD-FAIL on BOTH arms under a validated control) = 0.25
  -- a real, non-dismissible possibility; would be a valuable, well-instrumented negative
  narrowing the product claim rather than wasted work.
- P(MIDDLE_BAND -- partial signal on either arm, under-parameterized or K/encoder-sensitive,
  scale-up warranted) = 0.35.
- P("it's an information-theoretic wall for THIS specific content source, engineering-fixable
  with richer content" -- the nuanced middle reading) = 0.35, the single most likely honest
  outcome given the SimKGC-family field trend plus ConceptNet's thin per-entity text.

P_deflated (headline claim: "a brain-faithful structural/content factorization -- or, failing
that, its differentiable ML fallback -- is the correct next mechanism to test, and the prior
ablation's null result does not refute either") = **0.40** (capped at the 0.50 novel-synthesis
ceiling per calibration discipline; further deflated for the acknowledged absence of direct VSA
prior art for the scorer arm and the K-sensitivity/small-scale power concern for the TEM arm).

## Citations (verified count: 15, distinct)

Inductive KG completion (6): Teru, Denis & Hamilton, ICML 2020 (GraIL, arXiv:1911.06962); Zhu
et al., NeurIPS 2021 (NBFNet, arXiv:2106.06935); Xie et al., AAAI 2016 (DKRL); Shi & Weninger,
AAAI 2018 (ConMask, arXiv:1711.03438); Daza, Cochez & Groth, WWW 2021 (BLP, arXiv:2010.03496);
Wang et al., arXiv:2203.02167 (SimKGC) / Wang et al., TACL 2021 (KEPLER, arXiv:1911.06136)
counted together as the same trend-line citation.

Brain grounding (2, new beyond the 2x-drill's 5): Luettgau et al. 2025, *eLife* (reviewed
preprint, structural building-block reuse); Whittington, Warren & Behrens, ICLR 2022 (TEM-t).
(Whittington et al. 2020 *Cell*, Constantinescu/O'Reilly/Behrens 2016 *Science*, Behrens et al.
2018 *Neuron*, Samborska et al. 2022 *Nat. Neurosci.* carried over from the prior 2x-drill note,
not re-counted.)

VSA / hypernetwork (7): Smolensky 1990 (TPR); Soulos, McCoy, Linzen & Smolensky, arXiv:1910.09113
(role-learning networks); Schlag & Schmidhuber, NeurIPS 2018 (arXiv:1811.12143); Schlag, Irie &
Schmidhuber, ICML 2021 (Fast Weight Programmers, arXiv:2102.11174); Frady/Kleyko/Sommer
resonator networks (2020-2022, general citation); Balazevic, Allen & Hospedales, EMNLP 2019
(HypER, arXiv:1808.07018); Yeung, Zou & Imani, arXiv:2405.09689 (GHRR, "input-dependent Q").

One 2026 arXiv preprint (Zhang, Lyu, Liu, Wu, HPC-MEC world model) was surfaced but explicitly
excluded from the verified count -- unreviewed, narrow same-category test, flagged not relied on.
