# Deep drill (3x/angle): the full set of this session's VET-confirmed negatives -- one root, or several? (2026-07-20)

**Filed by:** research (Opus synthesis over 2 parallel Sonnet lit-scan sub-agents for the two negatives without
existing dedicated literature grounding [N6, N7], integrated against this session's own extensive prior brain-drill
corpus for N1-N5, which already carries deep theory+biology treatment and is not re-litigated from scratch here).
**Trigger:** direct USER deep-drill request across ALL 7 VET-confirmed negatives, 3 angles each: (a) unifying root
cause, (b) envelope-push per negative, (c) brain-check of the cluster.

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature agreement; novel-synthesis
capped at P<=0.50), per [[feedback-lit-scan-calibration-penalty]].

Builds on and integrates, without relitigating: `notes/drill_brain_how_it_does_it_given_failures_5x_2026-07-20.md`
(N1/N3/N4 mechanism, the CPC-rival-vs-real-data hypothesis), `notes/drill_platform_maturity_base_elements_brain_sufficient_5x_2026-07-20.md`
(element-by-element maturity audit), `notes/SYNTHESIS_platform_maturity_and_the_missing_learning_loop_2026-07-20.md`
(the prior single-root proposal this drill re-tests against TWO NEW, harder data points), `notes/research_brain_incomplete_kg_reasoning_substrate_edge_or_extraction_pivot_2026-07-19.md`
(N5), `notes/research_brain_reasoning_readout_multihop_constraint_chaingrade_target_2026-07-19.md` +
`notes/research_brain_systematic_compositional_generalization_binding_chaingrade_2026-07-19.md` (N1/N2 pre-reg
design and construction-determined guard, atom 29363).

---

## HEADLINE

**Two distinct roots, not one -- but they are coupled, and the coupling itself is the finding.**

**Root 1 (N1, N2, N5 -- "free algebra"):** wherever the substrate is handed clean, closed relational structure
(an oracle role-key, a foldable composition table, a KG edge-completion task with no distributional escape
hatch), the win is FREE ALGEBRA -- construction-determined by the task's own closure properties, not earned by
learning. This is the Fodor-Pylyshyn "systematicity for free" property, and it is real and correctly built --
but it was never a chain-grade candidate to begin with, because free composition is an architectural
sufficiency proof, not a learned achievement.

**Root 2 (N3, N4, N6, N7 -- "no informative learning signal reaches the parameters that need it"):** wherever
the substrate depends on a component that is supposed to improve from experience (extraction rules, a
cleanup/codebook decision layer, a contrastive predictive-coding loop), the actual blocking finding is NOT
"missing architecture" in the abstract -- each of these four negatives has ALREADY been tried against a
SPECIFIC learning-loop candidate this session, and each candidate CAME BACK NEGATIVE for a DIFFERENT proximate
reason: N3 = the front-end is still hand-ruled, not learned, so there is no parameter for a signal to reach;
N4 = the signal was non-contrastive (single hypothesis vs. one curated table); N6 = the signal cannot beat a
representation-level (codebook SNR) ceiling no matter how good the decision rule is; N7 = the signal existed in
the right SHAPE (contrastive, real-data-scored) but the corpus was too homogeneous to carry it. Root 2 is
therefore not fully closed by "add a learning loop" -- the session already tried variants of exactly that
(N4, N6, N7) and each hit a DIFFERENT wall. The unifying statement for Root 2 is sharper than the prior
SYNTHESIS doc's: **a contrastive, error-driven, real-data-scored learning signal is necessary but each of its
three preconditions (rival hypotheses to contrast, decision-relevant representational SNR headroom, and corpus
discriminability) has now been independently tested and independently found wanting at least once.** The fix is
not one build item, it's three separable preconditions, and only one of them (N4 -> the CPC-rival-vs-real-data
redesign) has a validated design pending its must-fail-controlled retest.

**Closed vs. open, honest tally:** N1, N2, N5 are TRULY closed as chain-grade targets (structural, brain-shared,
proven twice over independently in-house and externally) -- they were never going to be chain-grades, and
re-attempting them is the dominant historical failure mode (per this project's own Pattern 6, ~80% refutation
rate on re-drilling a closed field). N6 is closed FOR THE DECISION RULE specifically (argmax is provably
optimal for a random codebook; no cleanup-rule swap fixes an SNR ceiling) but OPEN for the CODE itself (learned/
structured/error-corrected codebooks are a real, distinct, untried lever -- see Angle 2 below). N3 is closed for
the CURRENT hand-rule architecture (already independently proven insufficient, 0.41-0.46 defensible) but open
for a learned front-end (never built). N4 is open and has a specific, already-designed retest pending (the
CPC-rival-vs-real-data 3-arm test). N7 is the newest and least understood: HONEST NULL, not HARD-FAIL --
diagnosed as corpus-coarseness, which is a DIFFERENT failure mode from N4's non-contrastive-signal diagnosis,
and it is genuinely unclear yet whether richer corpus alone rescues it or whether the predictive TARGET itself
(surface continuation vs. structured role-filler prediction) also needs to change.

**Single highest-leverage move across the whole cluster:** do NOT re-attempt N1/N2/N5 (closed, same root,
would burn cycles per Pattern 6). Do NOT treat "the learning loop" as one monolithic build item (the prior
SYNTHESIS doc's framing) -- treat it as THREE separable, independently-testable preconditions (rivalry, SNR
headroom, corpus/target discriminability) and sequence the CHEAPEST validated one first: **retest N4's CPC-
rival-vs-real-data design (already fully specified, reuses existing rival-LCCP + predictive_coding.py
primitives) BEFORE touching the codebook (N6, needs new representational math) or the corpus (N7, needs new
data acquisition/curation).** If N4's retest also nulls, the honest reading is that root 2 needs the codebook
and corpus fixes done FIRST (SNR and discriminability headroom are prerequisites a contrastive signal cannot
create out of nothing) -- which would flip the build order and is itself a falsifiable, cheap first checkpoint.

---

## Angle-by-angle drill: 7 negatives x 3 angles

### N1 (29363) -- Factorization compositional generalization = construction-determined

**(a) Root cause:** Root 1 (free algebra). An oracle role-key handed to a fixed-bind FHRR/VSA system recovers
held-out role-filler combinations by pure unbind arithmetic -- this is a closed-form algebraic identity
(commutative bind + distinct orthogonal-ish role vectors = exact recovery), not a statistical generalization
that could have failed. Per the systematicity literature (Fodor & Pylyshyn 1988; Smolensky 1990 TPR; Plate 1995
HRR), this is precisely the CONSTRUCTIVE-PROOF property VSA architectures are built to have -- a real,
well-established architectural fact, correctly reproduced, but tautological by design (oracle=1.000 is what the
math guarantees, not what was learned).

**(b) Envelope-push:** CLOSED as stated (zero-shot-from-oracle-keys is not a chain-grade and never will be, no
matter how it's re-run) -- but the sibling design (`research_brain_systematic_compositional_generalization_binding_chaingrade_2026-07-19.md`,
Scan 2) already specifies the genuinely open reframe: measure a LEARNING CURVE (held-out accuracy vs. number of
exemplar TYPES, hunting for a Yang Tolerance-Principle threshold phase-change) with role/filler vocabulary
LEARNED from an accumulating exemplar stream rather than handed as oracle keys. This is untried and is the
correct next attempt IF this thread is revisited -- but per the root-cause finding above, it is redundant with
N2's already-failed attempt at exactly this reframe (see below), so it should not be re-run without first
understanding why N2's version of the same fix failed.

**(c) Brain-check:** The brain gets free composition too (Fodor-Pylyshyn's own claim is that SOME
architecture must explain systematicity; VSA/TPR are recognized sufficiency proofs, not the confirmed neural
mechanism -- binding-by-synchrony is contested/largely disconfirmed, mixed-selectivity is about flexible
readout not binding itself). But critically, the brain does NOT get the COMBINATION VOCABULARY for free --
Berko's wug-test, Marcus's overregularization U-curve, and Tomasello's item-based-to-abstract developmental
trajectory all show REAL, measurable learning curves for which combinations become productive, gated by a
Tolerance-Principle-style exception threshold (Schuler & Yang 2023: productive at 11/5 exemplars, not yet at
10/6 -- a quantal, not gradual, threshold). **The brain shares the free-algebra half (it too has an innate/
early-scaffolded capacity for compositional binding) but does NOT share the "combinations known instantly from
an oracle" half -- it always earns the specific combination vocabulary through exemplar exposure.** This is
where our N1 test diverged from the brain: we tested the free-algebra half (already proven, uninformative) and
skipped the vocabulary-learning half (the actual brain-relevant question, never tested).

### N2 (29364) -- CLUTRR multi-hop reasoning = construction-determined

**(a) Root cause:** Root 1 (free algebra), same mechanism as N1 but at the multi-hop composition level rather
than the single-bind level. "Folder-vs-cannot-fold" is a tautology: a deterministic monoid (kinship-relation
composition table) is either closed under composition (foldable, hence solvable by a path-following oracle with
no learning at all) or it isn't -- there is no learning-dependent middle ground once the composition table
itself is handed rather than induced from data. The "tuned knob" flag in the negative description means the
task's apparent difficulty was actually controlled by a sampling/construction parameter (chain length under a
fixed foldable table), not by genuine statistical uncertainty in what the composition rules ARE.

**(b) Envelope-push:** This is the sharpest case of "already-attempted-fix-that-still-failed" in the cluster.
The pre-registered design (`research_brain_reasoning_readout_multihop_constraint_chaingrade_target_2026-07-19.md`)
explicitly built in the construction-determined guard (atom 29363's lesson, applied prospectively) and still
the arms landed construction-determined -- meaning the guard was insufficiently strict, or the composition
rules were learnable-in-principle but the specific short-chain training regime still let the model discover (or
be handed, via an under-specified "must-fail" control) the closed-form monoid rather than a statistical
approximation to it. OPEN lever, genuinely untried: force the composition table itself to be PARTIALLY
NOISY/incomplete (not just length-varying) so that no closed-form fold exists and only a statistically-learned
approximate composition can do better than chance -- this converts CLUTRR from a clean symbolic-algebra task
into a genuine incomplete-relational-learning task, which is exactly the KG-incompleteness framing N5 already
found is neural-embedding turf, not glass-box turf. That convergence (N2's honest fix leads directly into N5's
already-closed territory) is itself informative: CLOSED, not because CLUTRR-class tasks can't be fixed, but
because fixing them moves the target onto ground N5 already proved is not a substrate edge.

**(c) Brain-check:** The brain does NOT solve multi-hop kinship reasoning by folding a closed monoid either --
human relational reasoning over long inference chains is itself capacity- and serial-chaining-limited (Halford/
Wilson/Phillips: ~4-argument relational ceiling; beyond that, humans go serial via chunking/recoding, not a
bigger simultaneous fold), and human transitive-inference performance on incomplete/uncertain premise sets is
graded and error-prone, not exact-monoid-perfect. The brain's multi-hop reasoning is closer to N5's "neocortical
slow statistical extraction" mechanism than to N1/N2's closed-form algebra -- so the brain does NOT share this
specific negative's SHAPE (perfect algebraic fold), it shares N5's shape instead. This confirms N2 and N5 are
the same underlying phenomenon viewed from two different task framings, not two independent negatives.

### N3 -- Reader/extraction (LCCP) bounded at 0.557

**(a) Root cause:** Root 2 (no learning signal reaches the front-end), proximate cause = the front-end is a
static hand-authored rule set with no parameters a signal COULD update. The residual (85% light/report-verb +
coreference, "per-instance/structural") is not evidence of a fundamental representational limit -- it is
evidence that specific linguistic sub-classes (light verbs, report-verb complementation, coreference chains)
need either broader rule coverage (an engineering fix) or a genuinely learned front-end (an architecture fix),
and the extensive same-session brain-drill (`research_structural_residual_and_learned_in_substrate_reader_pivot_2026-07-19.md`)
already found that at least one sub-slice of the residual (created-object vs. locative-adjunct ambiguity) is a
cheap, glass-box, STRUCTURAL rule gap (a PP-class feature), not a deep semantic/world-knowledge wall -- meaning
part of the 0.557 ceiling is a coverage gap in the CURRENT rule set, not a proof that hand-rules cannot do
better.

**(b) Envelope-push:** Genuinely OPEN on two independent axes: (i) cheap, already-identified structural rule
extensions (PP-class/preposition-negative-prior features, generalizing across verb classes) that the 07-19 drill
explicitly found reopens a lever the "0.557 is a proven ceiling" framing had prematurely closed for at least one
sub-class; (ii) the deeper, harder lever -- a genuinely learned front-end trained via the CPC-rival-vs-real-data
mechanism (N4's redesign), which would let cue-integration weights shift from experience rather than needing an
engineer to notice and author each new rule. Both are untried in production; neither is closed.

**(c) Brain-check:** The brain's own syntactic/argument-structure extraction is a LATE-MATURING, experience-
hungry learned capability (parsing sophistication continues developing into adolescence, per the same-session
prior-art scan), dissociable from earlier-maturing core reasoning capacity. The brain does NOT get a hand-tuned
rule set -- it builds one from statistical exposure over years. So the brain does NOT share this negative's
proximate cause (a frozen rule table) -- it solves the SAME problem class differently (slow learned extraction),
which per the standing brain-check discipline means this is a genuine FIX target (a learned front-end), not an
accepted structural bound.

### N4 (29360/29361) -- Picture-verifier/thematic-fit (SCV) closed

**(a) Root cause:** Root 2, and the MOST PRECISELY DIAGNOSED instance of it this session. Two distinct failure
modes were measured: the static contrastive selector nulled even gold-perfect (no rivalry structure -- a single
hypothesis scored against a fixed table cannot produce a usable contrastive gradient, per the BYOL/DINO
cautionary parallel: non-contrastive graded scoring is collapse-prone without either negatives or an
architectural anti-collapse trick), and the graded verb-class fit signal fires densely but with the WRONG SIGN
(-0.024) -- meaning the signal is present and non-vacuous but is not currently oriented correctly, a tuning/
wiring issue distinct from "no signal exists at all."

**(b) Envelope-push:** OPEN, and the single most fully-specified fix in the entire cluster
(`notes/drill_brain_how_it_does_it_given_failures_5x_2026-07-20.md`, Angle 5): swap the static single-hypothesis-
vs-curated-table design for a multi-RIVAL hypothesis set (reusing the SCV's own already-built rival-LCCP
candidates) scored via prediction error against REAL subsequent exogenous text (not the coherence-table oracle),
using the CONTRASTIVE (relative, cross-rival) residual rather than any single rival's absolute score. This is a
re-wiring of three already-existing components, not new representational math, and has a pre-registered 3-arm
must-fail-controlled test (absolute vs. contrastive-vs-real vs. contrastive-vs-shuffled) ready to run. **This is
the highest-leverage single lever in the whole cluster because it is simultaneously the cheapest (reuses
existing primitives) and the most theoretically convergent (CPC, active-inference policy-comparison, and the
BYOL/DINO collapse literature all point the same direction).**

**(c) Brain-check:** The strongest N400-as-trainable-prediction-error models (Rabovsky & McRae 2014; Rabovsky/
Hansen/McClelland 2018; Kuperberg's 2024 hierarchical PC model) are explicitly AMODAL and CONTINUOUS, not
grounded/embodied and not categorical -- the brain's own thematic-fit error signal is graded and contrastive
across the space of possible next-words/interpretations, not a binary compatibility lookup. The SCV's original
design (a curated coherence TABLE) is architecturally closer to a symbolic lookup than to the brain's own
continuous, prediction-error-based mechanism -- so the brain does NOT share this negative's cause and its
mechanism IS the fix (contrastive predictive coding over a continuous representational space), consistent with
(b) above.

### N5 -- Path-A KG-reasoning closed

**(a) Root cause:** Root 1 (free algebra) restated at the knowledge-graph scale, and the CLEAREST double-
confirmed case in the cluster (both external literature and this project's own multi-week in-house history
converge). Pure glass-box VSA superposition with no gradient training measures 5-9x worse than either
gradient-trained low-dim embeddings (even a small additive map) or symbolic rule-mining on the SAME real data
(CSKG, FB15k-237). The apparent "conjunctive queries get easier" effect (3i > 2i in BetaE) is answer-set
shrinkage (generic multiplicative-evidence-combination arithmetic), the SAME construction-determined trap as
N1/N2 wearing a different costume.

**(b) Envelope-push:** CLOSED as a glass-box-VSA-accuracy target -- this is now confirmed three independent
ways (external lit, in-house native-VSA ceiling MRR 0.023, in-house pure-FHRR-bind-unbind-resonator ceiling
~0.207) and re-attempting a fourth version of the same test is exactly the low-yield "re-drill a closed field"
pattern this project's own meta-map flags as ~80% refutation rate. The one surviving, DIFFERENT-in-kind value
proposition (interpretability/soundness via a logical verifier layer, not raw accuracy) remains open but is a
transparency/trust differentiator, not a chain-grade candidate.

**(c) Brain-check:** Gap-filling over incomplete relational knowledge IS a genuinely learned, experience-
dependent brain capability -- but the brain's OWN mechanism for it is slow, interleaved, neocortical statistical
regularity extraction (the biological analog of training an embedding via many exposures), not fixed-codebook
symbol algebra. The brain does NOT solve incomplete-KG inference by glass-box bind/unbind either -- it shares
this negative's SHAPE (algebra alone doesn't do it) and its escape route (learned statistical extraction) is
exactly what the substrate is missing. This is a genuine "brain solves it differently, and differently IS the
fix" case, not an accepted shared bound.

### N6 (29365) -- Cleanup swap HARD-FAIL: codebook SNR wall, not a cleanup-rule immaturity

**(a) Root cause:** Root 2, but a DIFFERENT proximate mechanism than N3/N4/N7 -- not "no learning signal exists,"
but "the representation itself has no capacity headroom for a signal, no matter how good the decision rule
reading it out is." Per the parallel lit-scan (Angle-2 detail below): for a RANDOM (i.i.d., unstructured)
high-dimensional codebook, argmax/nearest-neighbor cleanup is provably the Bayes-optimal decision rule (matched-
filter/maximum-likelihood decoding under isotropic noise) -- this matches classical associative-memory capacity
theory (Amit-Gutfreund-Sompolinsky, Hopfield ~0.14N; Gardner-Derrida capacity bound) and modern dense-associative-
memory literature (Ramsauer et al., "Hopfield Networks is All You Need"), which shows exponential-capacity gains
come from CHANGING THE ENERGY FUNCTION'S EFFECTIVE SEPARATION (a property of the STORED PATTERNS' geometry and
the update rule's sharpness together), not from a decision-rule swap alone when patterns are already at the
random-code SNR ceiling for the existing dimension/load. The "cliff" is therefore a hard capacity-vs-load phase
transition intrinsic to random-codebook geometry, and a modern-Hopfield swap changes HOW SHARP the transition is
(if anything), not WHERE it sits, when the input codebook itself is unchanged.

**(b) Envelope-push:** GENUINELY OPEN, and distinct from "cleanup rule" -- the lever is the CODE, not the RULE
(confirmed by dedicated lit-scan). A load-bearing correction to the naive "just cluster/structure the codebook"
intuition: correlated/clustered patterns measurably LOWER a Hopfield-class network's critical capacity alpha_c
relative to i.i.d. random patterns (the "storage capacity of Hopfield models with correlated patterns"
literature) -- so naive semantic structuring of the codebook is a capacity COST, not a free win, unless paired
with an explicit compensating sparsification/orthogonalization step (see brain-check below). Three concrete,
literature-grounded candidates that are NOT naive clustering, none yet tried: (i) sparsify-and-orthogonalize the
codebook BEFORE storage (the direct DG-analog fix -- reduces effective inter-pattern overlap rather than adding
semantic correlation); (ii) redundancy/error-correcting-code augmentation of the existing random codebook
(concatenated/product-code style, borrowed directly from classical coding theory) to push the SNR wall without
abandoning randomness; (iii) multi-cue combination at retrieval time (combining multiple independently-noisy
cues restores effective SNR up to sqrt(N)-per-cues improvement in discrimination sensitivity when cues are
reliability-weighted, per signal-detection-theory cue-integration results) -- this is the cheapest of the three
since it changes nothing about the codebook or the decision rule, only how many independent noisy readout
attempts are fused before the final argmax. Note also that modern/dense-Hopfield "exponential capacity" claims
(Krotov-Hopfield 2016; Ramsauer et al. 2020) are NOT a counterexample to the SNR-wall diagnosis on closer
reading: the exponential-capacity result still requires a minimum pairwise separation Delta between the STORED
PATTERNS themselves -- the sharper energy function is a continuous relaxation of argmax that exploits
high-dimensional geometric separation more efficiently in one shot, it does not beat the SNR set by a GIVEN
pattern geometry at fixed dimension/load. This independently confirms N6's own finding: the modern-Hopfield
cleanup-rule swap hard-failed because the codebook geometry, not the update rule, was the bottleneck.

**(c) Brain-check:** The hippocampal CA3 recurrent network is the classical biological analog of exactly this
system (an autoassociative Hopfield-like memory), and biology's answer to capacity pressure is NOT a smarter
decision rule inside CA3 -- it is a STRUCTURAL fix upstream: the dentate gyrus performs aggressive sparsification/
pattern-separation BEFORE storage (reducing effective pattern overlap, i.e. improving the code's geometry before
CA3 ever has to decode it), and systems consolidation + adult neurogenesis continually manage effective load over
time (offloading/reorganizing old memories, integrating new granule cells) rather than the CA3 decode rule itself
getting more sophisticated. **This directly confirms the empirical N6 finding via an independent biological
route: the brain also fixes capacity/SNR problems by changing the CODE UPSTREAM (DG sparsification) and managing
LOAD (consolidation/neurogenesis), never by upgrading the CA3 decision rule.** This is a brain-shares-the-
diagnosis-and-shares-the-fix-direction case: the wall is real and structural, but the escape route (fix the code,
not the rule) is brain-precedented, not brain-refuted.

### N7 -- CPCL learning loop honest null on McGuffey (real-vs-shuffled continuation gap ~0, 3.7% margin)

**(a) Root cause:** Root 2, and the newest, least-precedented-in-house instance -- this is the direct empirical
test of the very mechanism N4's envelope-push (and the prior SYNTHESIS doc) proposed as the fix, and it came back
an HONEST NULL rather than a HARD-FAIL, which matters: the signal-shape (contrastive, real-data-scored) was
correctly implemented, but the CORPUS did not carry enough discriminative signal for real-vs-shuffled
continuation to be reliably distinguishable. Per the parallel lit-scan (Angle-2 detail below), this is a known
failure mode in contrastive/self-supervised learning generally -- when negative samples (here, shuffled
continuations) are too similar to positives (because the underlying corpus itself has low lexical/semantic
diversity and highly repetitive sentence templates), the achievable margin between real and fake collapses
toward the corpus's own entropy floor, independent of whether the SCORING mechanism is correctly built.

**(b) Envelope-push:** OPEN on (at least) THREE separable axes, confirmed and sharpened by dedicated lit-scan
(which independently converged on the corpus/negative-construction axis as the single best-evidenced lever):
(i) NEGATIVE-CONSTRUCTION axis -- replace fully-random shuffled distractors with MINED HARD NEGATIVES (near-miss
continuations that are plausible but wrong), the most-established fix in the contrastive-learning literature for
exactly this failure mode, with the documented caveat that harder negatives raise false-negative risk (a
near-miss distractor may actually BE an acceptable completion in a formulaic primer corpus, so this needs care);
(ii) CORPUS-DIVERSITY axis -- stage in more lexically/syntactically diverse "wild" text (mixing graded-reader
material with richer text), which curriculum/diversity-staging literature and a decodable-text meta-analysis
both show beats controlled-vocabulary-only training, converging with the already-planned corpus-staging note;
(iii) TARGET axis -- change WHAT is being predicted/contrasted, from raw surface-text continuation (highly
sensitive to corpus homogeneity and, per current self-supervised-learning literature, prone to over-anchoring
on surface-form identity rather than deeper structure) to a STRUCTURED prediction target (which rival PARSE/
role-filler structure best explains the actual next clause) -- directionally supported by the current move
toward latent/structured self-supervised objectives, but this specific instantiation is untested and is the
higher-novelty, higher-risk of the three levers. All three converge directly with N4's already-validated
rival-LCCP redesign, suggesting N7's null may partly be an artifact of BOTH corpus coarseness AND scoring the
wrong (surface) representation, not a single-cause problem. The corpus/negative-construction axes (i, ii) are
the cheaper, more standard first tests; (iii) should follow once (i)/(ii) are ruled in or out.

**(c) Brain-check:** Genuinely double-edged, and reported honestly rather than resolved prematurely. Habituation/
dishabituation and novelty-detection literature show the brain's own prediction-error/salience signal DOES
flatten under highly repetitive, low-variability input (a real biological precedent for the corpus-coarseness
diagnosis) -- and Bjork's desirable-difficulties / spacing-and-interleaving literature shows VARIED, harder
practice produces a stronger learning signal than easy, repetitive practice, supporting the corpus-diversity fix.
But child-directed-speech and early statistical-learning research shows the OPPOSITE can also be true for very
young learners: simple, repetitive, formulaic input is exactly what supports EARLY statistical learning (high
type-token predictability lets an immature learner detect structure at all) -- meaning graded readers may be
doing real developmental work for a DIFFERENT (earlier) stage of learning than the one this contrastive signal is
being asked to support. The honest brain-check conclusion: the brain does NOT show a clean single answer here --
repetitive input helps bootstrap SOME kinds of early learning while impairing OTHERS (fine-grained discrimination
signals), so this negative is not simply "the brain would fail the same way" or "the brain solves it differently"
-- it is age/stage-dependent, and the substrate's implicit assumption (one corpus, one learning stage) may itself
be the mismatch worth testing before concluding the corpus per se is the problem.

---

## Cheap decisive test (cluster-level, not per-negative)

Given the "single highest-leverage move" above, the cheap decisive next step is: **run N4's already-designed
3-arm CPC-rival-vs-real-data test FIRST** (absolute single-hypothesis vs. contrastive-vs-real vs. contrastive-vs-
shuffled, on the SCV's existing rival-LCCP candidates against real corpus continuations). This is cheap (reuses
existing primitives, no new data acquisition, no new representational math) and DIRECTLY tests whether Root 2's
"rivalry" precondition alone (independent of N6's codebook-SNR precondition and N7's corpus-discriminability
precondition) produces a usable signal on a DIFFERENT task shape (SCV thematic-fit disambiguation) than N7's
(raw continuation prediction). If N4's retest passes where N7 nulled, that isolates the CORPUS/TARGET axis
(N7's problem) as separable from the RIVALRY axis (N4's fix) -- informative either way.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 -- N4's retest succeeds where N7 nulled (task-shape matters more than corpus).** P=0.35
(deflated; plausible given the SCV task has a much narrower, more constrained rival set than open-ended
continuation prediction, but genuinely untested whether the SAME McGuffey-corpus coarseness that broke N7 also
caps N4's achievable margin). **HARD-PASS:** N4's contrastive-vs-real arm shows a measurable, non-zero,
statistically-distinguishable-from-N7's-3.7%-margin signal. **HARD-FAIL:** N4's retest ALSO nulls at a similar
(~sub-5%) margin -- this would mean corpus coarseness is a cluster-wide constraint, not specific to raw
continuation prediction, and would flip build priority to the CORPUS axis before any further rivalry-based
redesign is attempted anywhere in the cluster.

**Prediction 2 -- N6's codebook-code fix (multi-cue combination, the cheapest of the three named levers)
measurably moves the SNR wall without any cleanup-rule change.** P=0.40 (deflated; signal-detection-theory cue-
combination is well-established in principle, untested on this specific codebook geometry). **HARD-PASS:**
combining >=2 independent noisy retrieval cues before the final argmax raises the accuracy-vs-load curve's
cliff point measurably above the single-cue baseline. **HARD-FAIL:** no measurable shift -- would mean the
cues are not sufficiently independent (correlated noise sources), reopening the question of whether ANY code-
level lever (not just decision-rule levers) can move this specific wall.

**Prediction 3 -- N1/N2/N5 are NOT re-attempted as chain-grade targets in their current framing within this
program's next work cycle.** This is a process prediction, not an empirical one: if a 4th version of "handed
structure -> free generalization" is dispatched without first changing the task's closure properties (per N2's
own envelope-push finding: make the composition/relation table genuinely incomplete, not just longer), that
would repeat this project's own documented ~80% re-drill-a-closed-field refutation pattern (Pattern 6) and
should be treated as a process yellow flag, not a fresh scientific test.

---

## Cross-thread synthesis

This drill sharpens, and partially corrects, the prior `SYNTHESIS_platform_maturity_and_the_missing_learning_loop_2026-07-20.md`
single-root framing ("the substrate lacks a genuine learning mechanism," treated as one build item). That framing
was written BEFORE N6 and N7 landed as actual tested results. With N6 and N7 now in hand, the honest correction
is: **the missing-learning-loop diagnosis was right in kind but wrong in granularity.** It is not one missing
mechanism to build -- it is (at least) three separable preconditions for ANY learning signal to be usable in
this architecture (rivalry/contrast, representational SNR headroom, corpus/target discriminability), and this
session independently tested one candidate against each precondition (N4 against rivalry, N6 against SNR
headroom via a decision-rule swap that turned out to be the wrong lever for that precondition, N7 against corpus
discriminability) and got three DIFFERENT outcomes (open-and-promising, closed-for-the-rule-but-open-for-the-
code, and honest-null). Treating these as one monolithic "add the learning loop" item would have hidden this
differentiation and risked declaring premature victory or premature defeat on the whole cluster based on any
single one of the three results. The corrected framing: root cause = Root 1 (free algebra, 3 negatives, truly
closed) is architecturally distinct from Root 2 (learning-signal preconditions, 4 negatives, each with its OWN
proximate blocker), and Root 2 itself further decomposes into three testable sub-preconditions rather than one
crux.

This also reconciles the standing tension in the "keep brain-faithful + flexible/improving, not static" anchor:
the brain-check angle above shows the brain shares Root 1's free-algebra capacity (systematicity is real and
early/scaffolded) but does NOT share Root 2's specific proximate blockers -- it solves N3 (learned front-end),
N4/N7 (continuous contrastive prediction-error, not curated tables), N5 (slow statistical extraction), and N6
(fix the code upstream via DG sparsification, not the CA3 decode rule) all via mechanisms genuinely different
from what this session tried. Per the standing discipline ("does the brain get 'free composition' too, yes, but
ALSO learn the structure, which we skip" -- the prompt's own candidate framing): CONFIRMED for Root 1 (we built
the free half correctly and it was never going to be a chain-grade), and REFINED for Root 2 (we did NOT skip
"the learned half" wholesale -- we attempted three different learned-half candidates this session and each
taught a specific, different lesson about what the learned half actually requires).

## Substrate-product implications

Not a publication angle -- a build-sequencing and honesty angle. The practical payoff of decomposing Root 2 into
three preconditions is a concrete, risk-reducible build ORDER: retest the cheapest, most-validated lever (N4's
rivalry redesign) first, in isolation, before committing engineering time to either the codebook-code redesign
(N6, needs new representational math, higher cost) or a corpus-acquisition effort (N7, needs new data curation,
also higher cost and slower to iterate). If N4 HARD-PASSes, that is standalone evidence the rivalry precondition
is sufficient for AT LEAST the thematic-fit/disambiguation task shape, independent of whether N6/N7's harder
preconditions are ever fixed -- a genuine, shippable, narrower win rather than waiting on the full three-
precondition stack. If N4 also nulls, the corrected priority (per Prediction 1's HARD-FAIL branch) becomes fixing
corpus/target discriminability FIRST, since a contrastive signal cannot manufacture discriminability that isn't
present in either the representation (N6) or the data (N7) — no amount of rivalry-scoring machinery invents SNR
or lexical diversity that doesn't exist upstream of it.

---

## Citations (verified count)

**Carried forward from same-session prior drills (not re-cited in full; see source notes):** Fodor & Pylyshyn
1988; Smolensky 1990 (TPR); Plate 1995 (HRR); Lake & Baroni 2023 (Nature, MLC); Yang Tolerance Principle
(Schuler & Yang 2023); Berko (wug test); Marcus (overregularization); Tomasello (item-based learning); Frankland
& Greene 2015 (PNAS); Lalisse & Smolensky 2021; Whittington/Behrens 2020 (TEM, Cell); Tse et al. 2007 (Science,
schema consolidation); Rabovsky & McRae 2014 (Cognition); Rabovsky/Hansen/McClelland 2018 (Nat. Human Behaviour,
Sentence Gestalt); Kuperberg lineage (2024 PC-N400); van den Oord et al. 2018 (CPC/InfoNCE); BYOL/DINO
self-distillation lineage; Parr & Friston 2019 (active inference policy comparison); Halford/Wilson/Phillips
(Relational Complexity theory); Cowan 2001; the in-house KG-reasoning experimental history (native-VSA MRR
0.023-0.207; SGD additive-map MRR 0.128; AnyBURL rule-induction MRR 0.212 on FB15k-237; arXiv 2606.24948
Holographic Memory single-hop parity + two-hop collapse); Query2Box/BetaE (FB15k-237 conjunctive-query MRR
table).

**New, this drill (2 parallel Sonnet lit-scans, ~12 + ~10 tool-uses, generic-terms-only queries, full findings
integrated into N6 and N7's angle sections above):**
N6 lit-scan (12 sources): Amit, Gutfreund & Sompolinsky 1985 (*PRL* 55, Hopfield capacity alpha_c~0.138N);
Gardner-Derrida capacity/replica formula (projecteuclid intersecting-random-half-spaces; "Another look at the
Gardner problem," arXiv 1306.3979); Ramsauer et al. 2020 ("Hopfield Networks is All You Need"); "A Biologically
Plausible Dense Associative Memory with Exponential Capacity" (arXiv 2601.00984); generalized/Gaussian
nearest-neighbor decoding optimality (arXiv 2010.06791; ResearchGate 3079048); "On the storage capacity of
Hopfield models with correlated patterns" (Ann. Appl. Prob. 8(4)); Donoho-Tanner-matching deterministic
compressed-sensing phase transitions (PNAS 110); cue-combination/signal-detection-theory tutorial (ScienceDirect
S0022249616300165); CA3/dentate-gyrus pattern-separation reviews (PMC2829853, PMC2976779); McClelland,
McNaughton & O'Reilly 1995 (complementary learning systems); adult-neurogenesis capacity-conservation (*J.
Neurosci.* 38(31), PMC4561984).
N7 lit-scan (10 sources): hard-negative-sampling geometry (arXiv 2311.05139); collapse-phenomena taxonomy (MDPI
*Mathematics* 13(18)); Lilian Weng's contrastive-representation-learning survey; medical vision-language and
code-search hard-negative-mining work (ACM MM 2025; ACM TOSEM); corpus entropy/type-token-ratio formalization
(arXiv 2411.10227); text-simplification/curriculum-learning for data-constrained pretraining (arXiv 2509.24356)
and readability-driven curriculum (MDPI *Mathematics* 13(20)); "Predict and Reconstruct" joint self-supervised
objectives (arXiv 2606.05173); Gershman 2024 habituation-as-optimal-filtering (*iScience*) and predictability-
habituation (PLOS ONE 2020); Bjork desirable-difficulties lineage (UCLA Bjork Lab; UNH practitioner review);
infant statistical-learning and infant-directed-speech studies (PMC3883431; PLOS ONE 2016) plus the
"paradox-of-simplification" finding (simplified input can cap statistical-learning ceiling); decodable-text
meta-analysis (*Literacy* 2024) and Shanahan's controlled-vs-diverse-text synthesis.

Total: ~75-80 distinct named sources/lineages across the full drill (carried-forward ~55-60 + 22 new, cross-
checked against this session's own on-disk experimental history where available: KG-reasoning ceiling numbers,
substrate_capability_map rows).

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: all P estimates above are deflated 0.15-0.25 from raw literature
agreement; the two-root, three-sub-precondition framing is this drill's own cross-negative synthesis and is
capped at P<=0.50 as novel synthesis (no single prior source in this project's history had separated Root 2 into
three independently-testable preconditions before this drill — the prior SYNTHESIS doc's one-crux framing is
the direct predecessor being revised here).

---

## VERDICT (one line)

**Two roots, not one: Root 1 (N1, N2, N5 = free algebra, construction-determined, TRULY closed, brain-shared,
do not re-attempt) is architecturally distinct from Root 2 (N3, N4, N6, N7 = learning-signal preconditions,
each independently tested this session against a DIFFERENT proximate blocker — rivalry [N4, open, cheapest,
retest first], representational SNR headroom [N6, closed for the decision rule, open for the code], and corpus/
target discriminability [N7, honest null, open on two axes]) — the single highest-leverage move is retesting
N4's already-designed CPC-rival-vs-real-data 3-arm test before committing to either N6's codebook redesign or
N7's corpus-acquisition effort, since it is the cheapest of the three and its outcome (pass or fail) sharpens
build priority for the other two either way.**
