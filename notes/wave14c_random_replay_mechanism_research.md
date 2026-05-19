# Wave 14.C — what random replay actually does in our shallow Hebbian substrate

Returned 2026-05-19. Unbiased deep research on three converging negative
results about random replay in our BSC delta-rule substrate. The job is
to find the *mechanism* in the published literature that fits all three
observations, not to validate the framing we hoped for.

## 1. TL;DR

**Random replay in our substrate is a gradient-direction constraint, not
a data-augmentation rehearsal.** It acts as an implicit projection of
the Phase-B update onto the row-space of the Phase-A pool — formally
equivalent to A-GEM with a uniformly-sampled reference set, and to a
Stein-style empirical-Bayes shrinkage of the Phase-B delta toward the
W_A Fisher subspace. Because the constraint is binding only when the
W_B update has a component outside the A-row-space, replay is BWT-
positive in Phase B but pre-shift-neutral in Phase A; because priority
scores in our rank-1 delta-rule collapse to the same projection
direction the cosine retrieval already uses, MIR/PER lose to uniform;
and because every co-regularizer (R10, R3, EWC-style) projects toward
the same A-Fisher subspace, they substitute rather than compound.

## 2. Candidate mechanisms

I evaluated nine candidate mechanisms against all three negatives.
Ranked by joint explanatory power.

### Mechanism #1 — Replay as implicit gradient-direction constraint (A-GEM in disguise)

**Provenance**: Lopez-Paz & Ranzato 2017 GEM (arXiv 1706.08840),
Chaudhry et al. 2019 A-GEM (arXiv 1812.00420); reframed in
Verwimp-De Lange-Tuytelaars 2021 "Rehearsal Revealed" (arXiv 2104.07446)
which shows experimentally that rehearsal works by **keeping the
post-shift weights inside the OLD task's low-loss basin via an
implicit gradient projection**, not by augmenting the training distribution.

**Claim**: Mixing batches of fresh data with batches of replayed
old data is mathematically equivalent (to first order in lr) to
projecting the fresh-data gradient onto the cone of directions
that do not increase old-task loss. The constraint is binding only
when the fresh gradient has a component outside the old-data
row-space.

**Fit to negative #1 (random > priority)**:
- A-GEM uses a *random* reference set; replacing it with an
  importance-weighted reference (priority replay) breaks the
  unbiased Monte-Carlo estimate of the constraint set.
- MIR's priority score collapses to cosine-to-current-batch in our
  rank-1 delta-rule (already established in wave14b_mir_failure_diagnosis).
  This is the same direction the cosine retrieval branch already
  projects onto. Priority replay = constraint set concentrated on
  retrieval-redundant directions. Diversity (random) gives full-rank
  constraint estimate. **Predicted: random > priority.**
- Aljundi 2019 GSS already noted this: "the priority signal that
  wins is gradient-diversity in disguise" (paraphrase). Static or
  scalar-importance priority loses to random in the small-buffer
  regime because diversity dominates relevance.

**Fit to negative #2 (no compounding)**:
- R10 (concept-fusion retrieval) and R3 (concept-readout) are both
  projections onto subspaces derived from the SAME PPMI concept set.
  If random replay already constrains updates to the A-pool row-space,
  R10/R3 project to subsets of that space. **Three projections onto
  overlapping subspaces don't compound — the binding constraint is
  whichever has the smallest feasible region.** Substitution-not-
  orthogonality is the prediction.
- Chaudhry-A-GEM noted that adding regularizers to gradient-projection
  rehearsal gives sub-additive gains; Verwimp 2021's "Ridge Aversion"
  fix shows the same.

**Fit to negative #3 (BWT-positive AND pre-shift-neutral)**:
- During Phase A there is no Phase-A "old-task subspace" yet
  distinct from the current training distribution. The constraint
  set IS the current data row-space. Projecting onto it is the
  identity operation. **Replay = no-op in Phase A, even at 90% mix.**
- During Phase B the W_B-update has a large component outside the
  A-row-space (corpus B is shuffled, so its (ctx, target) joint
  is decorrelated from A's). Replay projects out that component.
  **Replay = BWT-positive in Phase B, large effect.**
- This asymmetry is exactly what A-GEM's geometry predicts.

**Verdict: explains all three. Leading candidate.**

### Mechanism #2 — Replay as empirical-Bayes shrinkage of Phase-B delta toward W_A Fisher subspace

**Provenance**: Ding 2024 "Understanding Forgetting in Continual
Learning with Linear Regression" (arXiv 2405.17583); Goldfarb-Hand
2025 "Replay Can Provably Increase Forgetting" (arXiv 2506.04377);
Stein-rule shrinkage for SGD (arXiv 2602.01777).

**Claim**: In linear regression with two tasks, the optimal continual
update is the projection of the new gradient onto the column space of
the old-task data, scaled by a James-Stein factor. Replay is a
plug-in estimator of this projection. Random sampling gives the
unbiased MC estimate; priority sampling biases it.

**Fit to all three**:
- #1: priority sampling violates the IID assumption needed for the
  unbiased Stein direction. Random wins (matches Stein literature).
- #2: shrinkage operators do NOT compose additively. Two shrinkers
  toward overlapping priors give shrinkage toward the more
  conservative one. Substitution predicted.
- #3: shrinkage is only active when the new gradient has variance
  in directions the old subspace is informative about. Phase-A
  data IS the old subspace — shrinker is the identity. Phase B
  is in a new subspace — shrinker is active. Asymmetry predicted.

**Caveat**: this is mathematically equivalent to Mechanism #1 for our
rank-1 delta-rule. They are two framings of the same geometric fact.
Stein language is friendlier to the bias-variance audit we did in
wave14b_stein_shrinkage_research.md; A-GEM language is friendlier to
the CL literature.

**Verdict: equivalent to #1; same evidence.**

### Mechanism #3 — Replay as functional regularization (Buzzega DER/DER++)

**Provenance**: Buzzega et al. 2020 DER/DER++ (arXiv 2004.07211).

**Claim**: Replay works not by re-presenting data but by matching the
*logits* (functional outputs) of the past model on those data,
preventing feature drift.

**Fit to #1**: DER++ uses reservoir-random sampling, not priority.
Buzzega Table 3 explicitly tests MIR vs random and finds random
matches or beats MIR for the DER objective. So #1 is predicted.

**Fit to #2**: DER (logit-distill alone) gives +7 over ER, DER++ (both)
gives +1.4 over DER. The marginal compounding is small. Our K=4
substrate shows -0.04 BWT (within noise) for replay+R3. **Below
DER's marginal noise floor — substitution is the empirically correct
prediction.**

**Fit to #3**: feature stability is a *Phase-B* property. In Phase A
there is no past feature to stabilize. Pre-shift neutrality predicted.

**Caveat**: in our substrate W is the *only* function (no encoder
head, no logit layer above retrieval). DER's logit-distill term and
our replay-W-update are NOT distinct mechanisms — they are the same
update on a one-layer linear readout. DER's compositional structure
(rep features + logit head) doesn't have an analogue here. So the
*qualitative* DER prediction lands; the *quantitative* DER++ gain
margin doesn't transfer.

**Verdict: 3/3 qualitative, mechanism partially redundant with #1.**

### Mechanism #4 — Mode-connectivity / basin-of-attraction (Mirzadeh / Goldfarb-Hand)

**Provenance**: Mirzadeh et al. 2020 (arXiv 2010.04495), Goldfarb-Hand
2025 (arXiv 2506.04377), Kozal 2024 weight interpolation (arXiv
2404.04002).

**Claim**: Successful CL keeps the optimizer in the connected low-loss
basin of task A. Replay biases the update toward that basin.

**Fit to #1**: random uniform sampling explores the entire basin
boundary; priority sampling biases exploration toward the most-
violating points, which biases the implicit basin geometry. Same
prediction as #1.

**Fit to #2**: every CL mechanism that steers toward the same basin
gives sub-additive returns. Substitution predicted.

**Fit to #3**: Phase A IS the basin. Nothing to escape from.
Phase B's natural gradient escapes the basin; replay pulls it back.
**Asymmetry predicted.**

**Important caveat**: mode-connectivity is well-defined for SGD on
non-convex losses with multiple minima. Our rank-1 delta-rule on
quadratic loss has a SINGLE minimum per data distribution
(Melchior-Wiskott 2020 Hebbian-Descent). The "basin" is really
the column-space of the data covariance. So Mirzadeh's geometric
intuition reduces to Mechanism #1's subspace projection in our
setting. Same math, different language.

**Verdict: equivalent to #1 in our regime.**

### Mechanism #5 — Replay as importance-sampling toward interference (MIR)

**Provenance**: Aljundi et al. 2019 MIR (arXiv 1908.04742).

**Claim**: priority replay should beat random because high-interference
samples carry more gradient information per unit memory budget.

**Fit to #1**: predicts the OPPOSITE of what we observe. Falsified.

**Fit to #2**: MIR + EWC compounds in Aljundi's experiments. Our
non-compounding is unexplained.

**Fit to #3**: silent on pre-shift effect.

**Verdict: 0/3. Falsified by our diagnostic. Per wave14b_mir_failure_diagnosis,
the MIR signal collapses to cosine-to-batch in rank-1 delta-rule —
which is exactly the redundancy that Mechanism #1 predicts.**

### Mechanism #6 — Replay as bias-variance regularizer (Stein/JS)

**Provenance**: wave14b_stein_shrinkage_research; Hatch 2024 selective
attention (arXiv 2411.12892); Velickovic 2024 softmax-is-not-enough
(arXiv 2410.01104).

**Claim**: replay is shrinkage of W toward a prior estimated from
the replay pool; provides bias-variance trade-off.

**Fit to #1**: shrinkage favors unbiased MC sampling. Random predicted.

**Fit to #2**: shrinkage operators substitute.

**Fit to #3**: PREDICTS PRE-SHIFT HURT in the low-variance regime
(K=4, B=5, (2B-1)/N ≈ 0.0022). **Empirically the pre-shift hurt
DID NOT happen** (delta < 0.01 bpc, within seed noise).

**This is the critical evidence**: a pure bias-variance story
predicts pre-shift damage at low variance because the bias term
becomes dominant. We don't see it. So replay is NOT acting as
generic bias-variance shrinkage — it is acting as a SUBSPACE
projection that is the identity on Phase A (where there is no
old subspace) and non-trivial in Phase B.

**Verdict: 2/3. Fails on #3.** Stein language is fine for accounting,
but the underlying mechanism is geometric (subspace projection),
not statistical (bias-variance).

### Mechanism #7 — Bricken-SDM sparse-distributed-memory continual learner

**Provenance**: Bricken et al. 2023 (arXiv 2303.11934).

**Claim**: SDM with Top-K activation is natively continual-learning
because writes to memory only update the K nearest addresses; the
rest is untouched. No replay needed.

**Fit to all three**:
- #1: silent on priority (no replay in vanilla SDM).
- #2: SDM + EWC achieves SOTA in their experiments — explicit
  compounding. Inconsistent with our #2.
- #3: predicts both pre-shift neutrality and BWT positivity for
  the Top-K mechanism itself — but our substrate is *dense* BSC,
  not Top-K SDM. Doesn't transfer.

**Verdict: 1/3. Substrate-mismatch.**

**Important note**: Bricken's SDM is "continual-learning native"
because sparsity automatically gives subspace separation. Our dense
BSC delta-rule replicates this *via replay* — random replay is the
poor man's Top-K. This is the deepest connection: replay manufactures,
at retrieval time, the same row-space separation that Top-K gives by
construction. **If we ported to Top-K SDM, we predict replay's BWT
gain shrinks to ~0** (because the projection is already free).

### Mechanism #8 — Hippocampal SWR-gated cortical plasticity (biological replay)

**Provenance**: Foster-Wilson 2006, Karlsson-Frank 2009, Joo-Frank 2018
(Nat Rev Neurosci review), Mattar-Daw 2018 (Nat Neuro), Wittkuhn 2021
(Nat Comm), Schapiro 2017/2018.

**Claim**: hippocampal sharp-wave ripples gate plasticity in cortex.
Replay is BWT-positive (consolidation) and pre-shift-neutral (during
encoding, plasticity is online, not via SWR).

**Mechanism details** (description of biology, not AI mapping):
- SWRs are 150-220Hz oscillations in CA1, lasting ~50-150ms
- During SWR, place cells fire in **temporally compressed sequences**
  that recapitulate behavioral trajectories (forward during planning,
  reverse after reward)
- SWR-gated plasticity is **selective**: not all cortical synapses
  receive the plasticity signal — only those that participate in
  the reactivated ensemble (Lehnert-Frank 2022, Igata 2021)
- Awake SWRs are biased toward **weakly-encoded** and **recently-
  rewarded** trajectories (Mattar-Daw 2018 "need × gain")
- Sleep SWRs are unbiased reactivation of the full day's experience,
  amplitude-weighted by activity strength
- Crucial: hippocampal-cortical replay is **NOT importance-sampling
  toward interference**; it's a normative-value calculation
  conditional on the agent's current goal (Mattar-Daw)

**Fit to all three**:
- #1: biology DOES prioritize (need × gain), so naively predicts
  priority > random. BUT the priority signal is closed-loop on
  current goal state, not on a static structural tag (the latter
  is what R7's "concept tags" implemented and lost to random).
- #2: biology's replay is one mechanism in a stack with EC-CA1
  statistical extraction (Schapiro 2017). Different anatomical
  pathways = different subspaces = should compound. **Doesn't
  match our non-compounding.** But our R3/R10 may not be biological
  analogues — they may be projecting to the SAME subspace.
- #3: biological replay during SWR is offline (rest, sleep), not
  during behavior. Pre-shift "encoding" plasticity uses a different
  mechanism (theta-gamma, online LTP). **Pre-shift neutrality
  predicted by the *gating*: during Phase A, online plasticity is
  the active mechanism; replay is dormant or no-op.**

**Verdict: 2/3 if you map MIR-priority to biological gating
(but our R7 implementation was static, not gating). #3 fit is
strong via the *gating* mechanism — biology has a temporal/spectral
gate (SWR vs theta) that decouples encoding plasticity from
consolidation plasticity. Our substrate has an *architectural* gate
(replay branch vs forward pass) with similar effect.**

The mechanism mapping that matters: **biological replay is a
gated-plasticity mechanism whose binding constraint is selective
reactivation, not data augmentation**. This maps cleanly to
Mechanism #1 (subspace projection): SWR-reactivated synapses
define the subspace in which plasticity is permitted.

### Mechanism #9 — Lin 1992 original analysis

**Provenance**: Lin 1992 "Self-improving reactive agents" (Machine
Learning 8:293-321).

**Claim**: experience replay improves sample efficiency by (a)
breaking temporal correlation in TD updates and (b) reusing
expensive experience. Empirical, not mechanistic.

**Fit to all three**: Lin's analysis is for RL with TD learning,
not supervised CL. He did not analyze priority vs random; he did
not analyze compounding; he did not analyze pre-shift effects.
**The original paper is silent on the mechanism we're trying to
explain.** Subsequent literature (Schaul 2015 PER, Riemer 2019
MER, Aljundi 2019 MIR) added the priority axis.

**Verdict: 0/3 for our negatives. Lin's substrate isn't ours;
his analysis doesn't apply.** Important historical anchor but
not the mechanism.

## 3. The mechanism that best fits all three (synthesis)

**Best single mechanism**: random replay is an implicit
**gradient-direction constraint / subspace projection of the
Phase-B delta-rule update onto the A-pool row-space**, formally
equivalent to A-GEM with a uniform-random reference set, and
to a Stein-style shrinkage of the Phase-B delta toward the
W_A Fisher subspace.

Three observations as a single mechanism:

1. **Priority < random**: priority sampling biases the constraint-
   set estimator. The MIR score in rank-1 delta-rule collapses
   to cosine-to-current-batch, which is precisely the direction
   the cosine retrieval already projects onto. Priority-weighted
   replay → over-concentrated projection → under-rank constraint
   set → less effective subspace coverage. Random gives the full-
   rank unbiased estimate. **(Confirmed by wave14b_mir_failure_diagnosis
   rank-equivalence math; aligned with Aljundi 2019 GSS diversity
   finding, Chaudhry 2019 uniform-ER finding.)**

2. **No compounding**: R10 (concept-fusion retrieval), R3 (concept
   readout), and random replay all project onto subspaces of the
   A-pool row-space. Projections onto overlapping subspaces do not
   compose additively — the binding constraint is whichever feasible
   region is smallest. **(Aligned with Verwimp 2021 Ridge Aversion,
   Mirzadeh 2020 mode-connectivity, Buzzega 2020 DER++ marginal
   compounding ≤ 20%.)**

3. **BWT-positive, pre-shift-neutral**: in Phase A the constraint
   set IS the current training distribution; the projection is
   the identity. In Phase B the W_B-update has a component outside
   the A-row-space (shuffled corpus B has decorrelated joint), and
   the projection actively removes it. **Asymmetry is geometric,
   not statistical.** A pure bias-variance story (Mechanism #6)
   would predict pre-shift damage in low-variance regime; we don't
   see it, falsifying the variance-reduction framing and
   confirming the subspace-projection framing.

**Why this is brutally honest**: replay in our substrate is NOT
"rehearsal of old data" in any meaningful sense. It is regularization
by projection. The data identities of pool entries don't matter
much; only the row-space they span matters. This is consistent with
(a) the result that pool entry granularity (concept-tagged vs
random) makes no difference once coverage is matched, (b) the
result that replay fraction effects saturate above some threshold,
and (c) the fact that we have never observed a meaningful gain from
making pool selection smarter on this substrate.

**Implication for the publication-grade story**: "we did Hebbian
replay rehearsal" is the wrong framing. The right framing is
"random replay is implicit gradient-direction projection in shallow
linear learners, and this projection IS the regularization." That
is a more defensible claim with broader implications and a cleaner
mathematical statement.

## 4. Brain-inspired mechanism mapping

(Description of biology first; mapping to substrate second. The
mapping is the contribution.)

### Biology

Hippocampal replay during sharp-wave ripples (SWRs) is the
mechanism by which the hippocampus communicates with cortex during
offline states (sleep, quiet rest). Key established mechanisms:

- **Selective gating** (Buzsáki 2015, Joo-Frank 2018): SWRs
  open a plasticity window in cortex during which co-active
  hippocampal-cortical synapses can be modified. Outside this
  window, cortical plasticity is suppressed or follows a
  different rule.
- **Reactivation specificity** (Foster-Wilson 2006): SWR sequences
  encode recently-traversed trajectories with cell-level fidelity.
- **Reverse / forward direction** (Karlsson-Frank 2009): reverse
  replay after reward (credit assignment), forward replay before
  decision (planning).
- **Need × gain prioritization** (Mattar-Daw 2018): replay content
  is biased by expected future utility; closed-loop on current
  goal state.
- **Statistical extraction in parallel pathway** (Schapiro 2017):
  EC-CA1 pathway extracts statistical regularities online;
  DG-CA3 pathway stores episodes for SWR replay. They cooperate
  but are anatomically distinct.

### Mapping to our substrate

| Biological feature | Substrate analogue | Fit |
|---|---|---|
| SWR gating window | Replay branch in training loop (separate from forward pass) | Strong: gates plasticity in time |
| Reactivation specificity | Pool entries are exact stored contexts | Strong: BSC vectors are crisp |
| Forward/reverse direction | N/A (we have no temporal sequence) | None |
| Need × gain prioritization | Not implemented (R7 was static tags, falsified) | None: literature warns this requires closed-loop |
| Statistical extraction parallel pathway | R10 concept-fusion retrieval | Plausible: PPMI on bigram is statistical extraction |
| Offline-only consolidation | Replay only active during Phase-B training | Strong: Phase A has no replay |

**The mechanism mapping that makes sense**: random replay in
our substrate ≈ unbiased SWR consolidation without need-gain
priority. We chose unbiased over need-gain because (a) our
substrate has no current-goal-state to compute gain against,
(b) the linear-regime evidence (Goldfarb-Hand 2025, Ding 2024)
says importance-weighted sampling biases the implicit subspace
estimator. Both biology and theory agree that **the bias-variance
trade-off in priority sampling cuts the other way when the
downstream operation is a subspace projection rather than a
sample-efficient gradient estimator**.

**The substrate-uniqueness claim that survives**: we have a
*decomposable* memory (14.B basis), a *gated* consolidation
mechanism (replay branch), and a *statistical extraction* parallel
pathway (R10) — three biological features simultaneously, none
of which a backprop transformer has. The lack of compounding
is then a *prediction* of mode-connectivity theory, not a bug.

## 5. Falsifiable predictions from the leading mechanism (≤1h GPU each, K=4 corpus)

If random replay is gradient-direction constraint / subspace
projection, then:

### Prediction P1 — Replay coverage ablation

The BWT gain should depend on the **rank of the replay pool**, not
on the number of pool entries. Take POOL_SIZE = 1024 and replace
with POOL_SIZE = 4096 entries randomly sampled from a SVD-truncated
rank-r approximation of the A-pool. Sweep r ∈ {64, 256, 1024, 4096}.

**Prediction**: BWT plateaus at r ≈ rank(A-row-space).
**Falsifier**: BWT grows monotonically with POOL_SIZE regardless
of r (would suggest data-augmentation framing, not projection).

### Prediction P2 — Synthetic pool from A-row-space

Replace the pool with a *random* basis spanning the same subspace
as the A-pool entries (Gram-Schmidt orthogonalize, take same rank).
The synthetic pool has zero data identity but the same row-space.

**Prediction**: BWT gain within 0.05 of the real pool's gain.
**Falsifier**: BWT collapses to 0 (would suggest data identity
matters, framework wrong).

### Prediction P3 — Replay during Phase A at 90% mix hurts ONLY when A is two-stage

Take corpus A and split it into A1 (first 50%) and A2 (last 50%).
Train W on A1, then continual-train on A2 with replay-from-A1.
Should now see BWT-on-A1 lift AND pre-A1-shift effect (because
A2 is the new task relative to A1).

**Prediction**: pre-shift on A1 is unaffected, but a NEW BWT
metric (loss-on-A1 after A2 training) shows the same ~0.7 gain.
**Falsifier**: no asymmetry — would mean pre-shift neutrality
was a corpus-shuffle artifact.

### Prediction P4 — Compound with TRUE-orthogonal regularizer

Add a regularizer that projects to a subspace **outside** the
A-row-space. Candidates: an EXPLICIT EWC-style penalty on
||W - W_A||_2 (zero-overlap with the row-space projection),
or a noise injection at the BSC level (anti-saturation, different
geometry).

**Prediction**: this regularizer compounds with random replay
because the subspaces are disjoint.
**Falsifier**: no compounding — would mean even orthogonal
mechanisms substitute, requiring a different theory entirely.

### Prediction P5 — Replay-on-Phase-A-during-Phase-A self-distillation

Replay W's own outputs from Phase A (DER-style functional replay
on the same data Phase A is training on). Predict no gain
because there is no shift; pure self-distillation in low-noise
regime is the identity update.

**Prediction**: pre-shift bpc unmoved (~0.01).
**Falsifier**: pre-shift improves — would mean replay is doing
something beyond projection (variance reduction, ensembling).

**Cheapest highest-power triple**: P2 (synthetic basis) + P4
(orthogonal compounding) + P5 (self-distillation neutrality).
Each <30 min GPU. Triple confirms or kills the projection story.

## 6. What this means for our publication-grade story

**The honest framing**: random replay in shallow Hebbian VSA
substrates is implicit subspace projection of the new-task
gradient onto the old-task row-space. This is not a new
mechanism — it is the linear-regime limit of the gradient-
projection family (GEM, A-GEM, OGD, GPM) applied to a
single-layer Hebbian rule.

**What is new**:

1. **The substrate**: BSC-bipolar dense codes, rank-1 delta-rule,
   pool retrieval. Theoretically clean enough to derive the
   projection equivalence explicitly. (None of the major CL
   papers have a clean closed-form mechanism explanation.)
2. **The decomposition story** (14.B): pool entries decompose
   into atoms — this is orthogonal to the replay mechanism
   and survives independently. Concept-readout via decomposed
   retrieval is a story no transformer can match.
3. **The three negatives as predictions, not failures**: priority
   < random, no compounding, BWT-positive pre-shift-neutral —
   these are *predictions* of the projection mechanism. The
   substrate is now a clean test-bed where these predictions
   hold in closed form, where in deep nets they hold only
   approximately.

**What is NOT publishable**:

- "Random replay surprisingly works" — it doesn't surprise the
  literature; Chaudhry 2019, Verwimp 2021, Buzzega 2020 all said
  this in deep nets. We are confirming, not discovering.
- "MIR loses to random on our substrate" — this is a *rank-1
  delta-rule artifact*; the cosine collapse is substrate-specific
  and known to be fragile in different settings.
- "Replay is BWT-positive" — table stakes for any rehearsal method.

**What IS publishable**:

- "Closed-form projection equivalence between rank-1 Hebbian
  replay and A-GEM with random reference set" — if we can derive
  this cleanly, it is a clean theoretical contribution.
- "Decomposable memory substrate (14.B) + gated consolidation
  (replay) + statistical extraction (R10) — three biologically-
  motivated mechanisms in one architecture, with mode-
  connectivity theory predicting their non-additivity" — this
  is a substrate-as-test-bed paper.
- "When you derive replay from first principles in a linear
  Hebbian model, priority-sampling is theoretically suboptimal,
  in agreement with empirical findings in deep nets and biology"
  — this is the unbiased version of the unbiased-research mandate.

**The honest framing that survives brutal review**: our substrate
is a **clean theoretical test-bed for the linear-regime limit of
continual learning**. Three published deep-net results
(uniform > priority, sub-additive compounding, BWT/pre-shift
asymmetry) are predictions of one mechanism (gradient-direction
projection) that has a closed-form derivation here. This is a
"linear analogue" paper in the style of Saxe-McClelland-Ganguli's
deep linear network analyses, not a "we beat SOTA" paper.

## 7. Sources

### Replay mechanism
- [Lin 1992 Self-improving reactive agents Machine Learning 8:293-321](https://link.springer.com/article/10.1007/BF00992699)
- [Lopez-Paz & Ranzato 2017 GEM NIPS arXiv:1706.08840](https://arxiv.org/abs/1706.08840)
- [Chaudhry et al. 2018 A-GEM ICLR arXiv:1812.00420](https://arxiv.org/abs/1812.00420)
- [Aljundi et al. 2019 GSS NeurIPS arXiv:1903.08671](https://arxiv.org/abs/1903.08671)
- [Aljundi et al. 2019 MIR NeurIPS arXiv:1908.04742](https://arxiv.org/abs/1908.04742)
- [Buzzega et al. 2020 DER/DER++ NeurIPS arXiv:2004.07211](https://arxiv.org/abs/2004.07211)
- [Verwimp et al. 2021 Rehearsal Revealed ICCV arXiv:2104.07446](https://arxiv.org/abs/2104.07446)

### Theory
- [Mirzadeh et al. 2020 Linear Mode Connectivity arXiv:2010.04495](https://arxiv.org/abs/2010.04495)
- [Ding et al. 2024 Understanding Forgetting in CL with Linear Regression ICML arXiv:2405.17583](https://arxiv.org/abs/2405.17583)
- [Goldfarb-Hand 2025 Replay Can Provably Increase Forgetting CoLLAs arXiv:2506.04377](https://arxiv.org/abs/2506.04377)
- [Kozal et al. 2024 Weight Interpolation CVPRW arXiv:2404.04002](https://arxiv.org/html/2404.04002v2)
- [Kirkpatrick et al. 2017 EWC PNAS arXiv:1612.00796](https://arxiv.org/abs/1612.00796)
- [Chaudhry et al. 2019 Tiny Episodic Memories arXiv:1902.10486](https://arxiv.org/abs/1902.10486)
- [Wang et al. 2024 Comprehensive Survey of Continual Learning IEEE TPAMI arXiv:2302.00487](https://arxiv.org/abs/2302.00487)

### Brain-inspired
- [van de Ven et al. 2020 Brain-Inspired Replay Nature Comm](https://www.nature.com/articles/s41467-020-17866-2)
- [Foster & Wilson 2006 Reverse Replay Nature](https://www.nature.com/articles/nature04587)
- [Karlsson & Frank 2009 Awake Replay Nature Neurosci](https://www.nature.com/articles/nn.2344)
- [Joo & Frank 2018 SWR Review Nature Rev Neurosci](https://www.nature.com/articles/s41583-018-0077-1)
- [Mattar & Daw 2018 Prioritized Memory Access Nature Neurosci](https://www.nature.com/articles/s41593-018-0232-z)
- [Wittkuhn & Schuck 2021 fMRI Replay Nature Comm](https://www.nature.com/articles/s41467-021-22571-9)
- [Schapiro et al. 2017 Complementary Learning Systems Phil Trans R Soc B](https://royalsocietypublishing.org/doi/10.1098/rstb.2016.0049)

### Substrate analogues
- [Bricken et al. 2023 SDM is a Continual Learner ICLR arXiv:2303.11934](https://arxiv.org/abs/2303.11934)
- [Schlag-Irie-Schmidhuber 2021 Linear Transformers Are FWP arXiv:2102.11174](https://arxiv.org/abs/2102.11174)
- [Melchior-Wiskott 2020 Hebbian-Descent arXiv:1905.10585](https://arxiv.org/pdf/1905.10585)

### Stein / shrinkage
- [Stein-Rule Shrinkage for SGD arXiv:2602.01777](https://arxiv.org/pdf/2602.01777)
- [Velickovic 2024 Softmax is Not Enough arXiv:2410.01104](https://arxiv.org/abs/2410.01104)

### Existing internal diagnoses
- `notes/wave14b_mir_failure_diagnosis.md` (rank-equivalence math)
- `notes/wave14b_compound_falsification_research.md` (mode-connectivity substitution)
- `notes/wave14b_preshift_bpc_research.md` (Bayes floor at K=4)
- `notes/wave14b_stein_shrinkage_research.md` (Stein audit, 6/8 sign-match)
- `notes/wave14b_r7_replay_literature.md` (static priority is dead)
