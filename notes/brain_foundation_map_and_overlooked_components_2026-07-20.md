# Brain-foundation map: correspondence + exhaustive overlooked-components sweep (2026-07-20)

**Filed by:** research (Opus synthesis over 4 parallel Sonnet lit-scan sub-agents, generic-terms-only per
[[feedback-query-privacy-decomposition]]). **Trigger:** direct USER request for the BRAIN half of a
substrate-vs-brain foundational accounting — a correspondence map (Job 1) plus an exhaustive sweep for
brain processes the substrate effort may have overlooked entirely (Job 2, explicitly "do not skimp").

**Builds on, does not relitigate:** `notes/drill_brain_how_it_does_it_given_failures_5x_2026-07-20.md`
(binding/structure-learning hybrid, grounding demoted, contrastive-rival-scoring diagnosis for the missing
learning loop) and `notes/drill_platform_maturity_base_elements_brain_sufficient_5x_2026-07-20.md`
(capacity MATURE, WM/discourse SETTLED, cleanup IMMATURE+cheap-fix, encoding PARTIALLY mature, error-driven
loop MOST LOAD-BEARING MISSING element). Those two notes already cover capacity, cleanup, encoding,
comprehension-as-prediction, and the missing correction loop in depth — this drill CONFIRMS those briefly
and spends its budget on what those notes did NOT cover: binding-by-synchrony/conjunctive-coding specifics,
oscillations/phase coding, attention, hierarchical multi-timescale processing, curriculum/developmental
staging, neuromodulation as multiple distinct gating axes, active inference, systems-consolidation/sleep
detail, inhibition/sparsity/competition, metacognition, and dendritic/glial/neurogenesis/homeostatic detail.

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature agreement;
novel-synthesis capped at P<=0.50), per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

**Top-3 correspondence discrepancies (Job 1):**
1. **Learning signal (item 9):** the substrate's just-built predictive-coding/CPC loop is non-contrastive
   (scores one hypothesis, not rivals) AND has ZERO neuromodulatory gating dimension, vs. the brain's
   contrastive rival-scoring (active-inference policy comparison) PLUS at least three formally distinct
   gating axes (dopamine=credit/value, acetylcholine=encode-vs-retrieve mode + expected-uncertainty,
   norepinephrine=unexpected-uncertainty/regime-change reset — Yu & Dayan 2005 show these are
   non-redundant). Already independently flagged as the single most load-bearing gap in the companion note;
   this drill adds that even a fixed contrastive loop would still be missing a second, independent control
   axis.
2. **Binding + structural code (items 1, 5):** the substrate's bind is a fixed, content-blind, unlearned
   algebraic operation, and its structural (FHRR) maps are hand-orthogonalized/stipulated. The brain's
   best-evidenced binding mechanism is NOT synchrony (seriously contested since Shadlen & Movshon 1999,
   further undercut by 2024 "feature binding is slow" psychophysics) but learned, task-shaped
   conjunctive/mixed-selectivity coding (Rigotti et al. 2013) with flexible linear readout — and its
   structural code (grid cells / Tolman-Eichenbaum Machine) is spectrally DERIVED from a predictive
   objective over experienced transition statistics, even where partially scaffolded pre-experience. Nothing
   in the substrate derives structure from data; it is stipulated once and reused.
3. **Comprehension (item 7) — a double gap, not one:** the substrate's reader is (a) rule-based rather
   than predictive/generative (already flagged, P=0.45 in the companion note) AND (b) flat/single-timescale,
   with no equivalent of the Hasson-lineage hierarchy of temporal receptive windows (auditory ~100ms ->
   sentence-level -> paragraph/narrative-level, empirically staged across the cortical hierarchy). Even a
   successfully-fixed predictive reader at one flat level would still lack the architecture for long-range
   discourse/narrative coherence integration — this second gap was NOT previously identified.

**Top-3 overlooked LOAD-BEARING + TOTAL-GAP components (Job 2):**
1. **Metacognition / confidence representation.** Total gap — the substrate has no way to represent its
   own uncertainty, distinguish confident-right from confident-wrong from "don't know," or abstain. This
   directly undercuts the standing product differentiator ("auditable, no hallucination by construction") —
   transparency about a wrong answer after the fact is not the same as knowing in advance you're likely
   wrong.
2. **Attention / selective gating.** Total gap — the substrate processes all input uniformly with no
   salience/relevance prioritization. Brain evidence (inattentional amnesia: unattended suprathreshold
   stimuli are processed but not encoded into usable memory) predicts this will bite specifically once real,
   noisy, large corpora are ingested rather than curated toy sets.
3. **Hierarchical / multi-timescale predictive processing.** Total gap — `predictive_coding.py` is a flat,
   single-level module. This is independent of, and additional to, the already-known "needs to become
   contrastive" fix (item 9 above): even a corrected contrastive loop running at one flat level cannot
   integrate discourse/narrative-scale coherence, which the brain achieves via a genuine hierarchy of
   increasing integration windows, not a single richer prediction rule.

(Runner-up total gaps, load-bearing but ranked 4th-5th: inhibition/normalization/sparsity/competition, and
homeostatic plasticity as a near-term safety requirement for any correlational learning rule — see Job 2
below.)

Deflate throughout; separate established biology (marked ESTABLISHED) from inference/synthesis (marked
CONTESTED/SPECULATIVE or NOVEL-SYNTHESIS, capped P<=0.50).

---

## JOB 1 — CORRESPONDENCE MAP

### 1. Variable binding (role-filler)

**Brain:** Two live hypotheses, not one settled account. (a) Temporal synchrony / phase-locking (Singer &
Gray 1995; Gray et al. 1989) — the classical proposal, but SERIOUSLY CONTESTED: Shadlen & Movshon's
"Synchrony Unbound" (*Neuron* 1999) argued the evidence was indirect, and 2024 psychophysics ("Feature
binding is slow," PMC11309034) argues apparent ultrafast binding reflects temporal integration and
eye-movement artifacts, not synchrony. Status as of 2024-2026: real correlate of attention/grouping, NOT
established as *the* binding mechanism. (b) Nonlinear mixed selectivity / conjunctive coding (Rigotti et
al. 2013, *Nature*) — well-replicated, PFC/association-cortex neurons whose firing is a nonlinear function
of a role x filler combination, supporting flexible linear readout of combinations; this is the
better-evidenced current leading account. (c) Tensor-product/HRR-style binding has essentially NO direct
neurophysiological evidence — it is a computational-modeling analogy (Smolensky, Plate), not a confirmed
brain mechanism; the one biologically-grounded bridge found (2024 hippocampal-entorhinal
compositionality-binding theory paper) is itself a modeling proposal, not single-unit confirmation.

**Discrepancy:** the substrate's bind is a fixed, content-blind, instantaneous algebraic operation (circular
convolution / elementwise multiply on random vectors) with no learned tuning, no task-context sensitivity,
and no time/phase dimension at all. The brain's best-evidenced mechanism (mixed selectivity) is LEARNED,
context-shaped, and adaptively read out — the opposite of "fixed algebra." There is also no direct evidence
the substrate's specific operation (VSA bind) corresponds to any confirmed brain mechanism; the correspondence
is an analogy of convenience, not a validated mapping. P_deflated=0.55 that conjunctive/mixed-selectivity
coding is the dominant real mechanism (synchrony demoted to a correlate, not a cause).

### 2. Superposition/bundling + capacity

**Brain:** Population coding; Cowan (2001) ~4-chunk attentional-focus limit; Halford/Wilson/Phillips
Relational Complexity theory converges on ~4-argument (quaternary) relations as the parallel-binding
ceiling; beyond this the brain goes further via SERIAL CHAINING (hierarchical chunking, Ericsson & Kintsch's
long-term-working-memory learned retrieval-cue structures, hippocampal-PFC generative replay chaining
role-bound objects sequentially), not a bigger simultaneous bind.

**Discrepancy:** already measured to be minimal — the substrate's content-blind structural code is robust
through m=24 simultaneous bindings (first crosstalk at m=32), sitting almost exactly on the brain's 4-24
relational-complexity band, and the substrate already goes beyond one bundle's capacity via discrete
serial/sharded chaining, the same strategy class the brain uses (see companion note, section 1). The one
residual discrepancy: the brain's serial-chaining beyond the parallel core is driven by LEARNED
retrieval-cue structures (Ericsson & Kintsch) that improve with expertise; the substrate's sharding scheme
is hand-built, not learned from experience. Mechanism-class match; learned-vs-hand-built implementation gap.

### 3. Cleanup/pattern-completion

**Brain:** CA3 autoassociative attractor dynamics (Marr 1971; McNaughton & Morris 1987; Rolls 2013) recover
a full pattern from a partial/degraded cue via convergence into basins SHAPED BY THE FULL STATISTICS OF
PRIOR EXPERIENCE — direct in-vivo evidence (Neunuebel & Knierim 2014) of graceful recovery across a
continuum of cue quality, load-bearing for relational inference specifically (hippocampal lesions impair
transitive inference, not just episodic recall — Konkel et al. 2008).

**Discrepancy:** already measured and diagnosed in the companion note — the substrate's cleanup is a hard
step-function (1.0 recovery through sigma=2.0, cliff to 0.029 at sigma=3.0), structurally distinct from a
CA3-style graded attractor, and its basins are fixed-noise-radius rather than experience-shaped (no learned
generalization to novel partial-cue combinations exists or was tested). A validated modern-Hopfield
attractor primitive already exists on disk as a cheap fix candidate, not yet wired in as the default cleanup
path. P_deflated=0.55-0.60 that this is load-bearing for reasoning over incomplete/noisy real knowledge
specifically (not just episodic recall).

### 4. Encoding/representation

**Brain:** cortex encodes concepts as a continuous, metrically-organized similarity space (Huth et al. 2012:
1,705 categories as smooth shared gradients), grid/place cells as literal metric codes repurposed for
abstract cognitive maps (Behrens et al. 2018; Whittington et al. 2020 TEM) — the mechanism behind
interpolation/extrapolation and "this new thing is like that known thing" generalization.

**Discrepancy:** VSA/HDC architectures are similarity-AGNOSTIC, not similarity-ANTI — they compose correctly
whatever content vectors they are handed, but atomic fillers are conventionally random/dissimilar by
convention. The substrate's structure-content factorization (FHRR maps) is already, independently, the
right hybrid architecture (Smolensky tensor-product / Eliasmith SPA-equivalent: content-agnostic structural
bind over a similarity-structured content dimension) and was validated with real GloVe content correlation
with no cost to factorization at low load. The actual gap is narrower than "no similarity structure": most
cells to date populate the content layer with random or ad-hoc vectors, not learned/grounded
distributionally-shaped embeddings as the production filler layer. Architecture-compatible, not yet
populated. P_deflated=0.45-0.50 that this specifically bottlenecks semantic generalization (vs. pure
symbol-substitution).

### 5. Structure/content factorization

**Brain:** entorhinal grid cells (structure) x hippocampal/lateral-EC content = the Tolman-Eichenbaum
Machine (Whittington et al. 2020, *Cell*) — a genuinely learned low-conjunctivity structural code, DERIVED
via a predictive (TD/successor-representation) objective over experienced transition statistics
(Stachenfeld, Botvinick & Gershman 2017). Important nuance: the geometry is a HYBRID, not fully learned —
2026 evidence shows the toroidal population-level attractor manifold is scaffolded before active exploration
(~P10 in rat), while metric alignment to specific environments is genuinely learned; a geometric-deprivation
study (Wernle et al.-lineage, PNAS 2023) shows grid cells still form under impoverished rearing but are
initially disorganized, normalizing within days once exploration begins — "a preconfigured,
experience-independent basis whose alignment is fine-tuned by experience," not built from scratch.

**Discrepancy:** the substrate's structural code (FHRR maps) is entirely hand-designed/stipulated (hand-
orthogonalized vectors), with NO derivation mechanism — no predictive objective over experienced data ever
produces or refines its eigenstructure. Even the SCAFFOLDED half of the brain's geometry is only partially
innate; the substrate has no analog to the LEARNED half at all (the metric-alignment/TD-learning
component). This is the "hand-denoised vectors are free-by-construction, not learned" finding, independently
converged on across notes. P_deflated=0.50 (novel-synthesis-adjacent framing of a well-evidenced literature).

### 6. Reasoning/inference

**Brain:** hippocampal relational inference is not simple pattern completion — INTEGRATIVE ENCODING actively
links elements across separate encoding episodes AT LEARNING TIME (Zeithamova & Preston 2010; Schlichting,
Zeithamova & Preston 2014/2015), formalized as recurrent "big-loop" recombination between hippocampus and
neocortex (Kumaran & McClelland 2012). PFC provides hierarchical GATING of which representations control
inference, organized rostro-caudally from concrete to abstract rule levels (Miller & Cohen 2001; Badre 2008)
— i.e., inference involves an active selection/abstraction-level layer, not just recombination.

**Discrepancy:** the additive_map reasoner is a flat, fixed composition function (real-data MRR 0.128) with
no gating/selection layer — it does not decide WHICH relations to chain or AT WHAT abstraction level; it
simply adds bound vectors. This converges with an already-closed independent finding
(`research_brain_incomplete_kg_reasoning_substrate_edge_or_extraction_pivot_2026-07-19.md`): pure glass-box
VSA reasoning loses 5.5x to gradient-trained embeddings on real incomplete-KG link prediction, and novel
relational inference in the brain is itself learned/experience-dependent (hippocampal-lesion transitive-
inference studies), resolved biologically via slow neocortical statistical-regularity extraction — the
biological analog of training an embedding, with no known local/Hebbian-class rule that closes this gap.
Verdict (carried forward, not re-litigated): this is the neural-embedding turf; the substrate's real
opportunity is upstream, in extraction/grounding, not in out-competing gradient-trained relational inference.

### 7. Comprehension/parsing

**Brain:** two separable claims, both real. (a) Predictive/generative processing: surprisal theory (Hale
2001; Levy 2008) robustly predicts reading-time effects across ~6 orders of magnitude; the Sentence Gestalt
model (McClelland/St. John/Taraban 1989; Rabovsky, Hansen & McClelland 2018) is a concrete
predict-compare-update-carry-forward template, independently convergent with the substrate's own
"compress-and-carry" framing. (b) HIERARCHICAL, multi-timescale processing: Rao & Ballard (1999) hierarchy;
Bastos et al. (2012) canonical microcircuits map predictions/errors onto specific cortical layers; Hasson et
al. (temporal-receptive-window hierarchy, extended to 2022/2023 narrative-construction work) show early
auditory cortex integrates over ~100ms, language areas over sentence spans, and default-mode/high-order
association areas over paragraphs/whole narratives, with response lags cascading in fixed order during real
narrative listening — this timescale hierarchy is empirically robust and largely uncontested even though a
2025 critique challenges canonical predictive-coding's specific error-SUPPRESSION mechanism (feedback can
enhance, not just suppress, activity for predicted stimuli — a live, unresolved debate about implementation,
not about the existence of hierarchy/timescale separation).

**Discrepancy — a double gap:** (a) the hand-rule LCCP reader (0.557 ceiling) is not predictive/generative at
all — already the leading hypothesis (P=0.45, companion note) for why the ceiling exists, though rule-
coverage gaps and "good-enough processing" (Ferreira et al.) remain live alternative explanations not yet
ruled out. (b) NEWLY IDENTIFIED here: the reader (and the newly-built predictive-coding module) is FLAT —
single-level, single-timescale — with no equivalent of the Hasson-lineage hierarchy. Even a successfully
fixed predictive/generative/contrastive reader operating at one flat level would structurally lack the
mechanism for building increasingly abstract representations or integrating discourse/narrative-scale
coherence; that capability is empirically tied to the EXISTENCE of higher areas with wider temporal
receptive windows, not obtainable from a single level running a richer local rule. P_deflated=0.40 for gap
(b) specifically (established literature, but the "this is what the substrate needs next" inference is
this drill's own extension, not directly tested).

### 8. Working memory/discourse

**Brain:** PFC maintenance with hierarchical gating (Miller & Cohen 2001) of what enters/exits based on
rule-relevance, plus a persistent, INDEXED situation-model structure (Zwaan & Radvansky 1998; van Dijk &
Kintsch) tracking entities/space/time/causation — a distinct representational FORMAT requirement, not
reducible to raw capacity.

**Discrepancy:** minimal on the core claim — this is the one area already independently settled: the
substrate's two-layer WM/discourse buffer (symbolic exact-store at working-memory scale, HD-bundle
superposition winning only at >=8x overload) was drilled 5x and VET'd as brain-consistent, arriving at the
literature's predicted answer (situation-model = distinct format, not just capacity) unprompted. One
residual, minor discrepancy: PFC's rostro-caudal GATING hierarchy varies WHAT is allowed to enter WM based on
abstraction-level/rule-relevance; the substrate's two-layer split is a capacity/scale split (symbolic vs.
bundled), not an abstraction-level gating split — a subtler dimension the current architecture does not yet
address, though it is not the load-bearing gap for this component.

### 9. Learning signal

**Brain:** predictive coding / free-energy (Rao & Ballard 1999; Friston) gives a scalar prediction error per
site — not intrinsically contrastive on its own. Active inference's POLICY-COMPARISON layer is where
contrast lives: expected free energy is compared ACROSS candidate policies/hypotheses (Parr & Friston 2019).
N400 (Rabovsky/McClelland lineage) is the best-evidenced trainable error signal, and — a corrective finding —
the strongest such models are AMODAL, not embodied; grounding is sufficient, not necessary, for a dense
continuous residual. Dopaminergic RPE (Schultz) is a special, GATED case of the same predict-compare-update
algorithm, itself heterogeneous (distributional-RL evidence, Dabney et al. 2019 — not one scalar signal), and
sits alongside at least two other formally distinct neuromodulatory gating axes: acetylcholine (Hasselmo —
biases toward encoding vs. retrieval, a genuine mode-switch tied to theta phase, not just an amplitude gate)
and norepinephrine (Aston-Jones & Cohen adaptive-gain theory; Yu & Dayan 2005 formally distinguish ACh's
EXPECTED uncertainty signal from NE's UNEXPECTED-uncertainty/regime-change signal — a real, non-redundant
pair in a Bayesian-filtering sense, not two labels for the same thing).

**Discrepancy:** (a) already diagnosed — the substrate's just-built predictive_coding.py + CPC loop is
non-contrastive (single hypothesis vs. a coherence table), tested null on a thin corpus; the brain-matched
fix is scoring MULTIPLE rival hypotheses' prediction error against real subsequent exogenous data using the
CONTRASTIVE residual (companion note, Angle 5). (b) NEWLY IDENTIFIED here: even with that fix, the substrate
would still apply ONE global learning-rate/precision parameter everywhere, whereas the brain has at least
three non-redundant gating axes (DA=credit/value; ACh=encode-vs-retrieve mode + expected-uncertainty
reliance; NE=unexpected-uncertainty/model-reset) acting on the SAME base predictive-error computation in
functionally distinct ways. A single-scalar learning rate conflates "this cue is known-noisy, discount it"
(ACh) with "my whole model of the situation just broke, reset" (NE) with "this outcome was valuable, credit
it strongly" (DA) — three genuinely different corrective actions collapsed into one knob. P_deflated=0.45
(Yu & Dayan's formal separation is solid; whether the substrate needs all three axes vs. a coarser 2-axis
approximation is this drill's own inference, not directly tested).

---

## JOB 2 — OVERLOOKED-COMPONENTS SWEEP (exhaustive)

For each: WHAT it is / its computational role / rating as (LOAD-BEARING for chain-grade / helpful /
biological-detail-skip) and (TOTAL GAP / partial analog exists in the substrate).

### A. Neuromodulation (dopamine, acetylcholine, norepinephrine, serotonin)

**What/role:** four chemically distinct, spatially broadcast signals that gate LEARNING itself, not just
activity. Dopamine = TD reward-prediction-error, causally gating synaptic potentiation/depression sign and
magnitude (Schultz 1997/1998; Montague/Dayan/Sejnowski) — though 2023-2024 evidence (Dabney et al. 2019
distributional RL; VTA heterogeneity reviews) shows this is NOT one scalar signal but a heterogeneous
population encoding a distribution over outcomes. Acetylcholine = Hasselmo's encode-vs-retrieve mode switch:
high ACh favors bottom-up/afferent input (new encoding) and suppresses recurrent/feedback retrieval, tied to
theta phase — a genuine change in WHICH PATHWAY dominates, not an amplitude gate. Norepinephrine (locus
coeruleus) = adaptive gain / exploration-exploitation signal (Aston-Jones & Cohen 2005); Yu & Dayan (2005)
formally distinguish ACh's EXPECTED uncertainty (known cue unreliability) from NE's UNEXPECTED uncertainty
(a model-violating regime change) — a real, non-redundant computational pair. Serotonin = patience/temporal-
discounting and possibly learning-rate modulation for delayed outcomes (Nat Commun 2018) — SPECULATIVE,
weaker evidence, mood-confounded.

**Rating:** LOAD-BEARING (DA/ACh/NE core; serotonin lower confidence) / TOTAL GAP. Not fatal on its own — a
recent computational review states these axes are needed precisely because they are different computational
dimensions (surprise-driven reset vs. reliability-weighting vs. credit-assignment strength), meaning a system
with only one global learning-rate scalar forfeits real degrees of freedom, but this collapses substantially
into item-9's already-identified error-driven-loop gap: there is nothing to gate until that loop exists.
Deprioritize building this until the base contrastive-predictive loop is built and working; then it becomes
a real, non-trivial second-order lever, not a redundant one.

### B. Consolidation / sleep replay / systems consolidation

**What/role:** Complementary Learning Systems (McClelland/McNaughton/O'Reilly 1995) — hippocampus does fast,
pattern-separated one-shot encoding; neocortex integrates slowly across many interleaved exposures to avoid
catastrophic interference while extracting shared statistical structure. Two mechanistically DISTINCT
sub-processes, not one: (i) schema-fast-integration — an established schema (Tse et al. 2007/2011) lets NEW
schema-consistent material be assimilated into neocortex within ~24h, far faster than the classic CLS
timeline, because pre-existing overlapping representations reduce interference (McClelland 2013) — a
schema-FIT-gated speed-up, not more rehearsal; (ii) sleep-specific gist/schema EXTRACTION — Lewis & Durrant's
overlapping-replay account: sleep replay across MULTIPLE overlapping traces (not verbatim single-episode
replay) selectively reinforces shared/gist components, requires multiple nights (vs. single-night simple
strengthening), and occurs in a distinct neurochemical state (ACh low during slow-wave sleep, permitting
retrieval-like reactivation suppressed during waking encoding — precise SO-spindle-ripple coupling, 2024-2025
reviews).

**Rating:** LOAD-BEARING for durable knowledge accumulation / continual learning specifically, NOT for a
single reasoning episode performed in one sitting (matches companion-note deprioritization). PARTIAL ANALOG:
the substrate already has a validated simple anti-forgetting replay mechanism (random-replay BWT recovery
+0.66 to +0.73 at K=4; pre-shift neutral-replay near-zero cost — both already on the capability map). TOTAL
GAP specifically on schema-extraction/gist-abstraction replay: anti-forgetting rehearsal preserves what was
learned but never distills cross-episode regularities into a faster-access, schema-consistent store, and
never gets the schema-fit speed-up for new material — a genuinely distinct mechanism from what already
exists, not a bigger version of it.

### C. Oscillations / theta-gamma phase coding

**What/role:** theta phase precession (O'Keefe & Recce 1993) — place-cell spikes advance to earlier theta
phase across a field traversal, so that within one ~125ms theta cycle, firing ORDER reproduces real-world
traversal order and inter-cell time lags encode spatial distance — a genuine, continuous SEQUENCE-ORDER code
with no static-vector analog. Lisman & Idiart (1995) theta-gamma multi-item WM: nested gamma sub-cycles
within a theta cycle act as discrete ordered "slots" for multiple items; theta-gamma coupling correlates with
WM capacity/accuracy in humans. Whether phase-coding is NECESSARY vs. one viable implementation among several
is unresolved (a 2026 review explicitly frames rhythms as still contested — causal/necessary vs. correlate
of underlying computation; trained RNNs show phase-locked dynamics can emerge given a reference oscillation,
suggesting oscillation may be a convenient scaffold, not a logical requirement).

**Rating:** for a system operating over discrete stored text/symbols rather than continuous real-time neural
dynamics, this is LESS load-bearing than it first appears — the substrate's serial-chaining via explicit
bound position/order markers is a legitimate functional substitute for what phase-coding buys the brain
(representing sequence order), achieving the same functional outcome via a discrete symbolic mechanism
instead of continuous timing. HELPFUL to understand, likely NOT load-bearing as a literal missing primitive.
TOTAL GAP as a literal mechanism, PARTIAL FUNCTIONAL ANALOG via existing position-binding. One genuine
residual gap worth flagging: phase coding gives a native, continuously GRADED representation of relative
temporal/sequential distance "for free" (via phase difference); the substrate has no continuous analog if a
future task needs graded (not just discrete ordinal) sequence-distance information.

### D. Attention (selective gating, salience, top-down bias)

**What/role:** biased competition (Desimone & Duncan 1995) — top-down signals bias mutual suppression among
simultaneously-active representations toward task-relevant content. Predictive-coding formalization (Feldman
& Friston 2010): attention = precision-weighting of prediction errors, a mechanistic (not metaphorical)
definition riding on the same message-passing as content inference — though a 2025 Trends in Cognitive
Sciences critique reports feedback sometimes ENHANCING (not suppressing) activity for predicted stimuli,
challenging the canonical PC-suppression mechanism specifically (not attention-as-gating generally).
Bottom-up salience (Itti & Koch) is architecturally separate, stimulus-driven, feeding the same competition.
Consequence of no gating: inattentional amnesia/blindness — unattended suprathreshold stimuli are perceptually
processed (intact sensory-cortex activity) but not encoded into explicit, reportable memory; some content
leaks into implicit/latent memory but usable/explicit memory requires attentional gating.

**Rating:** LOAD-BEARING and TOTAL GAP. The substrate processes/reads all input uniformly with no
salience/relevance prioritization at all — not even a placeholder. This directly predicts a specific failure
mode once real, noisy, large corpora (rather than curated toy sets) are ingested: without a mechanism to bias
limited downstream capacity toward task/goal-relevant content, useful signal risks being drowned in uniform
throughput, and — per the inattentional-amnesia evidence — most processed input may never convert into
usable/reportable structure at all.

### E. Hierarchical / deep predictive processing (multi-timescale)

**What/role:** Rao & Ballard (1999) hierarchy; Bastos et al. (2012) canonical microcircuits give a specific
laminar implementation (deep layers carry top-down predictions, superficial layers carry bottom-up errors).
Kiebel/Daunizeau/Friston (2008) formalize a hierarchy of increasing temporal-integration windows up the
cortical hierarchy; Hasson et al. (2008, extended 2022/2023 narrative-construction work) show this
empirically — early auditory cortex integrates ~100ms, language areas integrate sentence-level spans, and
high-order association/default-mode areas integrate over paragraphs/whole narratives, with response lags
cascading in fixed temporal order during real narrative listening. This is the empirical basis for why a flat
single-level system cannot build increasingly abstract/invariant representations layer-by-layer, and cannot
integrate discourse-level structure unfolding over many seconds-to-minutes. Largely uncontested even amid the
2025 critique of canonical PC's specific suppression mechanism (which challenges implementation detail, not
the existence of hierarchy/timescale separation).

**Rating:** LOAD-BEARING and TOTAL GAP. `predictive_coding.py` is a flat, single-level module. This is
independent of, and additional to, the already-diagnosed "needs to become contrastive" fix (item 9 of Job 1):
even a corrected, rival-scoring, contrastive loop running at ONE flat level structurally lacks the mechanism
for long-range narrative/discourse coherence integration — that capability requires the EXISTENCE of
multiple levels with different integration windows, not a richer local rule at one level. This is the most
clearly novel (previously unflagged, in either companion note) structural gap surfaced by this drill.

### F. Curriculum / developmental staging

**What/role:** Elman (1993) "starting small" — capacity-limited or complexity-staged training succeeds where
full-complexity-from-start training fails at learning embedded clause structure; Newport's "less-is-more"
hypothesis (1990) — limited early capacity is causally ADVANTAGEOUS for generalization, not merely a
constraint (supported by Johnson & Newport 1989 critical-period second-language data). Brown's (1973) stable
14-morpheme acquisition ORDER and classic overregularization U-shaped curves are real, replicated
developmental signatures. IMPORTANT COUNTER-EVIDENCE: Rohde & Plaut (1999) directly challenge the strong
claim — networks trained on complex material from the start eventually MATCH OR EXCEED starting-small
networks given sufficient training time; prior "necessary" claims may have stopped complex-first training too
early. Broader curriculum-learning literature converges: curriculum reliably speeds convergence and helps
under CAPACITY-or-DATA-SCARCITY, but is not a universally necessary condition for reaching good
representations for a sufficiently patient/capable learner.

**Rating:** HELPFUL, not strictly load-bearing for a well-resourced learner (per Rohde & Plaut) — BUT this
project's own already-established constraint (the corpus-precondition finding: buildable-now learning is
scoped to ~99k words, roughly 10x below the smallest literature precedent for learning new distributional
statistics) is exactly the CAPACITY-or-DATA-SCARCITY regime where the Newport/Elman "less-is-more" account,
not the well-resourced-learner exemption, applies. This tips the judgment call toward LOAD-BEARING given the
substrate's actual operating regime, not the general case. TOTAL GAP currently — no staged/curriculum design
exists anywhere in corpus ingestion order.

### G. Reward / value / motivation / active inference

**What/role:** Friston's active inference unifies perception and action by minimizing EXPECTED free energy
over candidate policies (combining epistemic/uncertainty-reducing value with instrumental/goal-reaching
value) — well-established as a mathematical theory, less so as directly-observed neural mechanism (much
support is normative/model-fitting). Schmidhuber's artificial-curiosity/compression-progress program and
empowerment are the ML-side parallel: curiosity rewards improving predictive/compressive model quality,
favoring transferable structure by construction — suggestive, not conclusive (mostly demonstrated in
simulated domains). Active-vs-passive learning evidence (yoked-control studies) is MIXED: active learners
sometimes build more accurate spatial/structural models than yoked passive observers given identical input,
but effects are inconsistent and moderated by exploration strategy — a real but modest, context-dependent
effect, not proof that action-selection produces qualitatively different representations.

**Rating:** HELPFUL, not clearly load-bearing for reasoning/comprehension per se (comprehension can proceed
passively; the mixed active-vs-passive evidence does not support a strong necessity claim). Potentially
relevant as a partial substitute for the scarce-data problem (item F): curiosity-driven active selection of
which text to read/ingest next, weighted by expected information gain, could partially compensate for the
absence of a hand-designed curriculum. TOTAL GAP — the substrate does static comprehension/inference only,
with no action-selection or self-directed exploration of what to ingest next.

### H. Inhibition / normalization / sparsity / competition

**What/role:** sparse coding (Olshausen & Field 1996) — maximizing sparsity when learning a natural-image
code reproduces V1 receptive fields, establishing sparsity as an efficient-coding principle, not an arbitrary
constraint; advantages include reduced interference/crosstalk, higher associative-memory capacity per active
unit (Willshaw/Buneman/Longuet-Higgins 1969), and energy efficiency. Divisive normalization (Carandini &
Heeger 2012) is argued to be a CANONICAL cortical computation — contrast gain control, decorrelation,
attention gating, and multisensory integration, replicated across modalities/species — genuinely
load-bearing, not mere activity-clamping. Winner-take-all via PV+ inhibitory interneurons is concretely
linked to dentate-gyrus pattern separation (2026 circuit-level evidence). Nuance: dense/distributed codes
offer graceful degradation and fault-tolerance that maximally sparse ("grandmother-cell") codes lack, and
2024-2026 work shows sparsity's forgetting-prevention benefit is not automatic (depends on representational
strength, not sparsity alone) — this is a genuine trade-off, not a one-sided brain-superiority case.

**Rating:** LOAD-BEARING and TOTAL GAP for the specific computational functions of INTERFERENCE-REDUCTION,
CAPACITY-PER-ACTIVE-UNIT, and NORMALIZATION (contrast/gain control, decorrelation) — the substrate uses dense
superposition throughout with no competition, lateral inhibition, or normalization step of any kind. But this
is NOT a blanket "must add sparsity everywhere" verdict: dense superposition is a legitimate,
brain-divergent design choice with its own real advantage (graceful degradation, no hard sparse-code
fragility), and normalization specifically (a cheaper, purely additive fix — divide/rescale activations) may
capture most of the missing computational benefit without abandoning the density choice that the current
architecture depends on elsewhere.

### I. Embodiment / sensorimotor grounding

**What/role:** Barsalou's Perceptual Symbol Systems (structure claim: grounded representations carry richer,
context-dependent relational structure than amodal category lists) vs. congenitally-blind cognition studies
and Dove's (2015) symbol-ungrounding critique showing structural language/logic/theory-of-mind reasoning
develops largely intact without sensorimotor/visual grounding.

**Rating:** already correctly demoted in the companion note (P_deflated~0.15 fatal, weakest necessity claim)
and independently corroborated by this project's own already-closed finding (vision is not a grounding fix;
the dictionary already grounds concrete vocabulary relationally). HELPFUL, not load-bearing. PARTIAL ANALOG
already exists (relational/amodal grounding via the existing WordNet/VerbNet scaffold). No new evidence this
drill surfaces changes that verdict.

### J. Metacognition / uncertainty / confidence estimation

**What/role:** Fleming & Lau (2014) formalized second-order (meta-d') measurement, dissociable from
first-order task performance; Fleming et al. (2014, *Brain*) found anterior-PFC lesion patients with a
domain-specific metacognitive deficit (impaired visual metacognition, spared memory metacognition) despite
INTACT first-order visual discrimination — a clean causal dissociation, not merely correlational. Kiani &
Shadlen (2009): LIP neurons encoding decision-forming evidence also encode certainty, suggesting LOCAL
confidence can be a natural byproduct of the same evidence-accumulation process — but this operates alongside
a genuinely additional PFC readout stage; recent work (2023-2025) shows metacognition-like signals CAN emerge
spontaneously in RNNs trained only on first-order tasks (supporting "cheap byproduct" at the population
level), while the human/primate lesion literature shows the ACCURATE, reportable, cross-domain version needs
dedicated circuitry. Opt-out paradigm studies (capuchin monkeys largely fail uncertainty-monitoring where
rhesus macaques succeed) show task-competence without abstention-competence is a real, observed biological
dissociation.

**Rating:** LOAD-BEARING and TOTAL GAP. The substrate has no graded evidence-accumulation process (so
confidence cannot even be "free"), and no second-order readout exists either. This is arguably the single
highest product-relevance overlooked item given the standing "auditable, no hallucination by construction"
differentiator: transparency about how an answer was derived (already a real strength) is a different claim
from knowing IN ADVANCE that an answer is likely wrong and abstaining — the biological evidence shows these
are dissociable capabilities, and the substrate currently has neither the accumulator dynamics nor the
readout stage.

### K. Other foundational mechanisms — rated individually

- **Dendritic computation** (Poirazi & Mel 2003; London & Häusser 2005): single pyramidal neurons compute
  nonlinear, NMDA-spike-driven subunit functions across dendritic branches, formally equivalent to a
  two-layer network within one cell — a genuine expansion of a point-neuron's function class (feature
  conjunctions/quasi-XOR at the sub-unit level). ESTABLISHED. Rating: LOAD-BEARING CANDIDATE in general
  neuroscience, but LOW PRIORITY / possibly not applicable here — the substrate's base "unit" (a full
  bind/bundle/unbind vector operation) already has far more expressive power per-unit than a biological
  point-neuron, so the point-neuron-vs-dendritic-neuron analogy does not map cleanly onto this substrate's
  actual representational unit. TOTAL GAP if forced into a literal analogy, but the practical relevance is
  genuinely unclear (flagging honestly rather than forcing a fit).
- **Glial/astrocyte computation** (Araque tripartite-synapse tradition): astrocytes modulate synaptic
  efficacy and network-level meta-plasticity via Ca2+-gated gliotransmission on slower timescales — PARTIALLY
  ESTABLISHED as genuine computation vs. mainly modulatory/homeostatic support (the field itself is not
  settled on this distinction). Rating: HELPFUL / second-tier, PARTIAL ANALOG possible via a slow global
  gain/modulation parameter if one is ever added — not urgent.
- **Adult neurogenesis** (hippocampal dentate-gyrus new-neuron integration): a "temporal
  stamping"/pattern-separation-enhancement theory is directionally established (Aimone et al.) but
  mechanistically contested (a 2015 finding shows neurogenesis can paradoxically DECREASE pattern separation
  in some models). Rating: BIOLOGICAL-DETAIL-SKIP — its function (continuous representational refresh) is
  plausibly approximable by other, more direct means; not obviously irreplaceable.
- **Homeostatic plasticity** (Turrigiano synaptic scaling): a well-established NEGATIVE-FEEDBACK mechanism
  necessary to prevent runaway potentiation/depression under any Hebbian/correlational learning rule — without
  it, Hebbian learning is provably unstable. ESTABLISHED. Rating: LOAD-BEARING and TOTAL GAP, with a specific
  near-term practical implication: if/when the just-built predictive-coding/CPC loop's null result is fixed
  and it starts producing real weight updates (any correlational/Hebbian-adjacent update rule), homeostatic
  scaling is the standard biological safety valve against runaway weight growth — worth designing in
  proactively rather than discovering the instability empirically after the fact.

---

## Cheap decisive test

Given this is a mapping/survey deliverable (not a single hypothesis), the cheapest NEXT test that
discriminates among the newly-surfaced overlooked components, reusing existing signals with no new
representational math: **build a minimal abstain/confidence readout (item J) on top of a signal the
substrate already computes** (e.g., the cleanup match-score / nearest-neighbor margin, or the
predictive-coding residual magnitude once that loop is running) and test whether thresholding it reduces the
confident-wrong-answer rate on the existing held-out reasoning test suite, without materially hurting
confident-right coverage. This is a pure readout-and-threshold operation — no new architecture — and directly
tests whether Kiani & Shadlen's "confidence free from accumulator dynamics" finding transfers to this
substrate's existing signals.

**HARD-PASS:** an abstain threshold on an existing residual/match-score signal cuts the confident-wrong rate
by a clear, pre-registered margin (e.g. >=30% relative reduction) at a coverage cost no worse than
proportional (i.e., not simply abstaining on everything).
**HARD-FAIL:** no threshold on any existing signal outperforms a random-abstain baseline — would mean the
substrate's current signals carry no usable confidence information, contradicting the "confidence is free
from a graded/probabilistic representation" literature for THIS substrate specifically, and would require
building genuine accumulator-style dynamics before confidence can exist at all.

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

**Prediction 1 (metacognition, item J).** As specified above in the cheap decisive test. P_deflated=0.40
(the "confidence is free" literature is reasonably strong, but no source has tested it on this substrate's
specific signal types).

**Prediction 2 (hierarchical predictive processing, item E).** If a second predictive-coding level is added
above the existing flat module (operating at a coarser, multi-sentence timescale, feeding on the lower
level's residual rather than raw input), it will show measurably better discourse-level coherence tracking
(e.g., detecting a topic break or contradiction spanning multiple sentences) than the flat single-level
module at matched parameter budget. P_deflated=0.35 (well-established brain phenomenon; the specific
prediction that adding a second level helps THIS substrate's discourse task is an inference, not directly
tested). **HARD-PASS:** two-level module beats flat module by a pre-registered margin on a discourse-break
detection task with no additional gold labels. **HARD-FAIL:** no measurable improvement — would suggest the
substrate's current bottleneck is upstream (extraction quality) rather than the predictive hierarchy's depth,
redirecting priority back to item 9/Job-1's contrastive-loop fix before hierarchy is worth adding.

**Prediction 3 (attention/salience, item D).** A cheap relevance-gating step (e.g., discard or down-weight
low-information-content tokens/clauses before extraction, using an existing surprisal or frequency-based
proxy for salience — no new learned module required) measurably improves extraction precision on noisy,
uncurated real text relative to uniform processing, while showing no effect (or a small cost) on already-
curated/clean text. P_deflated=0.35. **HARD-PASS:** precision gain on noisy text >= a pre-registered margin,
with curated-text performance not degraded beyond a small tolerance. **HARD-FAIL:** no gain on noisy text —
would suggest the extraction bottleneck is not signal-to-noise/salience-related and attention-gating is lower
priority than currently ranked.

## Cross-thread synthesis

This drill is explicitly complementary to, not a re-run of, the two same-day companion notes. Confirmed
without relitigating: capacity is brain-matched and mature; the two-layer WM/discourse buffer is settled and
brain-consistent; cleanup is immature with a cheap, already-available fix; encoding's structure side is
mature while its content side needs population with learned/grounded vectors; and the single most
load-bearing missing element remains the contrastive, rival-scoring, error-driven correction loop (item 9,
Job 1) — nothing in this drill challenges that ranking. What this drill adds, net-new: (1) a formal, dual-axis
account of WHY that loop alone is insufficient once built — it still needs a second, independent
neuromodulatory gating dimension (item A) to distinguish reliability-discounting from regime-reset from
credit-assignment; (2) an entirely separate, previously-unflagged structural gap — the reader/predictive
module is flat/single-timescale, and needs a genuine multi-level hierarchy (item E) to reach
discourse/narrative-scale coherence, independent of and additional to becoming contrastive; (3) a full
accounting of attention/salience (item D) and metacognition/confidence (item J) as TOTAL gaps that neither
companion note touched at all, both plausibly high-leverage given the project's stated goals (robustness to
real noisy corpora; the auditable-AI product differentiator); (4) a rebalanced, less one-sided treatment of
dense-superposition-vs-sparsity (item H) as a genuine architectural trade-off rather than a one-directional
brain-deficiency; (5) a re-weighting of curriculum/staging (item F) toward load-bearing given this project's
OWN already-established data-scarcity constraint (the 99k-word corpus-precondition finding), which is exactly
the regime where "less-is-more" evidence applies rather than the well-resourced-learner exemption.

## Substrate-product implications

Not a publication angle — a build-priority and honesty angle. Three practical, ranked next-build candidates
emerge from this drill beyond the already-standing correction-loop build: (1) the metacognition/abstain
readout (item J) is the cheapest to test (pure threshold on an existing signal, no new architecture) and has
the highest direct product relevance — it is the difference between "auditable after the fact" and
"trustworthy in advance," which matters concretely for the auditable-AI positioning; if it HARD-FAILs, that
is itself valuable information (the substrate's current signals carry no confidence information yet, and
genuine accumulator dynamics would need to be built first, likely alongside the correction loop rather than
after it). (2) Hierarchical/multi-timescale predictive processing (item E) is a real, separate architectural
investment — it should NOT be conflated with or deferred behind the contrastive-loop fix; they solve different
problems (getting a usable learning signal at all, vs. integrating that signal across a genuine hierarchy of
scope). (3) Attention/salience gating (item D) is lower cost to prototype (a frequency/surprisal-based
relevance filter needs no new learned component) and directly de-risks the transition from curated toy
corpora to real noisy text, which is the stated direction of travel for the reading program. Neuromodulation
(item A) and homeostatic plasticity (item K) remain correctly deprioritized until the base correction loop
exists and starts producing real weight updates — but homeostatic scaling specifically should be designed in
from the start of that build, not discovered as an instability bug afterward, since the literature is
unambiguous that any correlational/Hebbian-adjacent update rule is provably unstable without it.

## Citations (verified count)

**~91 distinct citations** reported inline across the 4 new parallel Sonnet lit-scans this drill dispatched
(binding/oscillations/hippocampal-inference: ~24; attention/hierarchy/curriculum: ~19; neuromodulation/active-
inference/consolidation: ~24; inhibition-sparsity/metacognition/misc: ~24 — some overlap in foundational
citations across scans, not deduplicated here), cross-referenced against and not double-counted with the
~74 citations already reported in the two same-day companion notes this drill builds on (`drill_brain_how_
it_does_it_given_failures_5x_2026-07-20.md`: ~40; `drill_platform_maturity_base_elements_brain_sufficient_
5x_2026-07-20.md`: 34). Standard lit-scan provenance (author/year/venue-traceable as reported by each
sub-agent, not independently re-fetched by this synthesizing pass), per [[feedback-lit-scan-calibration-
penalty]].

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: all P estimates above are deflated 0.15-0.25 from raw
literature-agreement reads; any claim that combines multiple literatures into a single account not directly
tested in that combination (e.g., the "single unifying gating gap," the "hierarchy is independently necessary
from contrast" claim) is capped at P<=0.50 as novel synthesis. Established biology (marked ESTABLISHED
inline) is reported at literature-typical confidence; this drill's OWN inferences about what the substrate
specifically needs are flagged separately and held to the lower, capped range throughout.

---

## VERDICT (one line)

**Correspondence-wise, the substrate's fixed/hand-built algebra (binding, structural code) diverges from the
brain's learned/derived-from-data equivalents most sharply at exactly the point already identified as
most load-bearing (the missing contrastive error-driven loop), with comprehension carrying a second,
independent flat-vs-hierarchical gap not previously flagged; overlooked-component-wise, the three clearest
total gaps this drill surfaces beyond the two companion notes are metacognition/confidence (highest direct
product relevance), attention/selective gating (highest risk once real noisy corpora are ingested), and
multi-timescale hierarchical predictive processing (a structurally separate requirement from, not a
substitute for, the already-standing contrastive-loop fix) — with neuromodulation, sparsity/inhibition, and
curriculum/staging as real but lower-urgency runners-up, each re-weighted here by this substrate's own actual
operating constraints (data scarcity, dense-superposition design choice) rather than a blanket brain-fidelity
argument.**
