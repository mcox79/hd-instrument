# Brain-fidelity element audit: why our predictive encoder collapsed, and the minimal collapse-proof config (2026-08-01)

Director synthesis of a 3-way Sonnet lit-scan drill (structural anti-collapse; homeostatic
plasticity; target-externality + PC architecture). Question (USER, load-bearing): the cortex learns
predictively for a lifetime with NO representational collapse, so a truly brain-foundational
predictive learner cannot collapse. OUR causal predictive-coding encoder DID collapse
(rep_std 0.0078, WORSE than the old EMA+VICReg). Therefore our objective is NOT truly brain-faithful
yet. Score EACH element of our objective vs EXACTLY how cortex avoids collapse; name the divergences;
specify the minimal brain-faithful config that STRUCTURALLY cannot collapse.

Builds on `notes/research_brain_faithful_collapse_free_predictive_encoder_objective_2026-08-01.md`
(prior drill) and `notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`.
KB-check: `substrate_query.sh "predictive coding collapse sparse coding homeostatic plasticity firing
rate"` top cosine 0.417 (no prior note on this exact collapse-mechanism audit) -- genuinely new drill.

Calibration: P deflated 0.15-0.25 per lit-scan discipline; CITED@ vs REASONED@ tagged;
ESTABLISHED/CONTESTED per claim. Citations are search-snippet-confirmed, not full-PDF-verified.

---

## HEADLINE

The collapse is NOT a scale problem and NOT a "needs more regularization" problem -- it is TWO
brain-fidelity divergences, both now consistent with the MEASURED 0.0078 collapse:

1. **OUR TARGET IS NOT EXTERNAL.** We regress to the next token's OWN LEARNED INPUT EMBEDDING. That
   embedding is a trained parameter that co-adapts with the encoder under the SAME regression
   gradient -- the textbook shared-gradient collapse condition (CITED@ SimSiam/BYOL/Tian 2021).
   The prior drill's Rank-1 ("predict a REAL target = the next-token embedding") was ADOPTED and
   STILL COLLAPSED -- which does not refute "predict a real target," it shows the next-token INPUT
   EMBEDDING is NOT a real/external target. It is an ungrounded self-referential loop with no
   external anchor anywhere. Cortex NEVER does this: its predictive cascade is grounded at the base
   by REAL EXTERNAL SENSORY INPUT (fixed, high-entropy, cannot degenerate). The truly-faithful
   target is token **IDENTITY** (fixed one-hot over a fixed vocabulary) via sampled/adaptive softmax
   -- external, OOM-safe, and a constant output CANNOT minimize cross-entropy against varying token
   identities (this is why LLM pretraining is never observed to collapse in the BYOL sense).

2. **OUR ANTI-COLLAPSE IS SOFT AND HAS A KNOWN LOOPHOLE.** We used Barlow-Twins decorrelation ALONE.
   Decorrelation is a batch-level soft penalty with a DOCUMENTED variance-collapse loophole -- a
   near-zero-variance/constant output trivially satisfies "decorrelated" (this is the exact reason
   VICReg had to ADD an explicit variance-floor term). The prior drill's Rank-3 recommended
   REPLACING the VICReg variance hinge WITH Barlow -- which removed the one term that closes the
   loophole. The brain's anti-collapse is instead HARD, always-on, per-sample SPARSE CODING via
   lateral inhibition / k-WTA (Olshausen & Field 1996): a per-sample fixed-cardinality active set
   that a degenerate constant vector cannot occupy.

We are missing divergence #1 (dominant cause) and divergence #2 (structural guard). Homeostasis
(USER's Q3) is real and brain-faithful but is SOFT and SLOW -- biology itself (Zenke temporal
paradox) shows it is insufficient ALONE; it is not the structural fix. The PC error-population
architecture (Q4) is the weakest, most speculative gap.

---

## THE AUDIT -- each element scored vs cortex (SHAPE + MECHANISM)

### ELEMENT 1 -- THE TARGET (USER Q1). Divergence: SEVERE. Rank: #1 cause.

- **Cortex:** predicts the activity of the level BELOW, grounding out at the base in REAL EXTERNAL
  SENSORY INPUT. CITED@ Rao & Ballard 1999 (Nat Neurosci); Huang & Rao 2011; Friston 2005.
  ESTABLISHED. **Nuance (scan-3 correction to the prior drill's flat claim):** higher cortical
  levels DO regress to the internal representation-units of the level below -- cortex is a *cascade
  of internal-target regressions grounded by ONE external anchor at the base*, not "external at
  every level." The load-bearing invariant is not "never internal" but "never UNGROUNDED": every
  internal target is anchored to real external input within a few synapses.
- **Us:** a SINGLE level regressing to its own next-token INPUT EMBEDDING -- a learned parameter,
  with NO external anchor anywhere in the loop. This is precisely the ungrounded self-copy cortex
  never builds. Both the encoder output and the embedding table receive gradient from the same
  regression loss -> they co-adapt toward a shared constant -> loss -> 0 at the degenerate point.
- **ML establishment (scan-3, IMPORTANT refinement):** the precise ML-established cause is NOT
  "internal vs external" per se -- it is SHARED/SYNCHRONIZED optimization pressure between predictor
  output and target (stop-grad + predictor asymmetry are what prevent it in SimSiam/BYOL). A learned
  target CAN avoid collapse if gradient-decoupled; a FIXED external target trivially satisfies the
  no-shared-gradient condition. Our learned-embedding regression is the DANGEROUS case (shared
  gradient, no decoupling). CITED@ SimSiam (Chen&He 2021), Tian et al. 2021, CMU ECCV22, BYOL 2020.
  ESTABLISHED. The MAE-vs-latent-MIM contrast (He 2022 vs 2407.15837) is the cleanest direct
  evidence: fixed high-entropy target (pixels / token identity) => no collapse; co-adapting learned
  target without stop-grad => collapse.
- **Answer to USER's explicit sub-question** ("does cortex ever regress to its own learned internal
  target -- it does not, confirm"): CONFIRMED with precision -- cortex regresses to internal
  representation-units, but NEVER to an UNGROUNDED self-copy; every internal target is externally
  anchored at the base. Our objective violates the anchoring, not merely the internality.
- **CITED@, ESTABLISHED. P(target-non-externality is the dominant cause) deflated ~0.50** (scan-3
  raw 0.45 for target-externality as *a* sufficient cause, raised slightly because in OUR case the
  target is BOTH internal AND shared-gradient AND ungrounded = the worst quadrant, and the collapse
  is MEASURED, not hypothetical).

### ELEMENT 2 -- STRUCTURAL vs SOFT ANTI-COLLAPSE (USER Q2). Divergence: SEVERE. Rank: #2.

- **Cortex:** anti-collapse is HARD, always-on, per-sample. Ranked by strength of the STRUCTURAL
  guarantee (scan-1):
  1. **k-WTA / sparse coding (STRONGEST, brain-faithful).** Lateral inhibition -> only the top-k
     units survive per stimulus (Olshausen & Field 1996; k-WTA circuits ESTABLISHED in V1/cerebellum).
     A genuine per-sample combinatorial HARD constraint: a latent with exactly k nonzero
     magnitude-selected coordinates CANNOT be the all-equal constant vector (ties are measure-zero).
     Residual failure mode: the SAME fixed subset winning for all inputs ("dead units") -- real but
     narrower than full collapse, and closed by an auxiliary revival/dead-unit loss (BatchTopK SAE
     pattern). P(makes collapse structurally impossible) scan-1 raw 0.45.
  2. **Divisive normalization = LayerNorm/RMSNorm.** Always-on per-sample, but ANTI-EXPLOSION not
     anti-collapse: dividing a constant by a constant pool is well-defined. EMPIRICAL PROOF:
     transformers with LayerNorm STILL exhibit rank/representation collapse. So our LayerNorm buys
     nothing here. scan-1 raw P 0.10. Carandini & Heeger 2012 ESTABLISHED (as normalization, not as
     anti-collapse).
  3. **Lateral-inhibition/decorrelation (Barlow) = what we used.** Batch-level, SOFT, with the
     documented VARIANCE-COLLAPSE LOOPHOLE (a near-zero-variance output is trivially "decorrelated"
     -- exactly why VICReg added a variance term). scan-1 raw P 0.15. This IS our 0.0078 failure
     mode: decorrelation with the variance floor removed.
- **Us:** Barlow decorrelation ALONE (the weakest, loophole-bearing option), no hard sparsity, no
  variance floor. We picked the mechanism the literature specifically flags as insufficient alone.
- **CITED@, ESTABLISHED. The missing structural element = HARD SPARSITY (k-WTA/top-k on the latent).
  Minimal soft interim = restore an explicit variance floor (VICReg std hinge) alongside Barlow.**

### ELEMENT 3 -- HOMEOSTASIS (USER Q3). Divergence: real but SECONDARY. Rank: #3.

- **Cortex:** per-neuron firing-rate SET-POINT defended by synaptic scaling + intrinsic-excitability
  plasticity (Turrigiano; ESTABLISHED, decades-replicated). BUT: it is SLOW (hours-days) and SOFT by
  construction -- a negative-feedback plasticity RULE, not a hard gate. **Zenke/Gerstner "temporal
  paradox" (2017): homeostatic plasticity at its biologically-observed slow timescale is
  MATHEMATICALLY INSUFFICIENT to prevent Hebbian runaway/collapse -- the fast structural stabilizing
  work is done by inhibition/sparse coding, NOT homeostasis.** CONTESTED that it is a *sufficient*
  anti-collapse mechanism; ESTABLISHED that it exists and contributes.
- **Answer to USER's Q3** ("is a homeostatic/target-rate regularizer the brain-faithful always-on
  anti-collapse we are missing?"): PARTLY. It is brain-faithful and worth adding as a cheap always-on
  soft term (ML analog = per-unit KL-to-target-activation penalty, Ng sparse-AE; closest bio-fidelity
  of the candidates), and it directly addresses the k-WTA "dead-unit/fixed-subset" residual (revives
  under-used units). But it is NOT the STRUCTURAL fix -- biology itself does not rely on it for fast
  anti-collapse. Do NOT reach for homeostasis as the primary lever; it is the RESIDUAL-closer that
  rides on top of the hard sparsity constraint.
- **CITED@. ESTABLISHED-mechanism / CONTESTED-sufficiency. P(homeostasis alone prevents our collapse)
  deflated ~0.25** (scan-2 raw 0.40-0.45 for "prevents collapse durably", deflated harder because the
  bio literature itself flags insufficiency-alone).

### ELEMENT 4 -- PREDICTION ARCHITECTURE (USER Q4). Divergence: uncertain. Rank: #4 (weakest).

- **Cortex:** separate error-unit population (superficial pyramidal) + representation units +
  precision-weighting/gain (Bastos et al. 2012; Friston precision). ESTABLISHED as the microcircuit.
- **Us:** plain "predict next latent from left context" -- no separate error population, no precision.
- **Does the missing error-architecture CAUSE collapse?** scan-3 found NO source linking PC
  error/precision architecture to collapse-prevention in the ML sense -- it is a REASONED bridging
  analogy only (error-population loosely ~ predictor-asymmetry+stop-grad; precision ~ variance
  regularization). Our collapse is far better explained by Elements 1-2. **P(missing error-population
  is a cause) deflated ~0.15** (scan-3 raw 0.20). De-prioritize; do not chase this before Elements 1-2.

---

## RANKED GAPS (most -> least likely responsible for the collapse)

| Rank | Gap | Cited/Reasoned | Est/Contested | P_deflated (is-the-cause) |
|---|---|---|---|---|
| 1 | Target NON-externality (learned, co-adapting, ungrounded embedding vs external token IDENTITY) | CITED@ | ESTABLISHED | ~0.50 |
| 2 | Missing HARD structural sparsity / variance floor (Barlow-alone loophole vs k-WTA) | CITED@ | ESTABLISHED | ~0.45 |
| 3 | Missing homeostasis (soft target-rate) | CITED@ | ESTABLISHED-mech / CONTESTED-sufficiency | ~0.25 (residual-closer, not primary) |
| 4 | Missing PC error-population / precision architecture | REASONED@ | CONTESTED | ~0.15 |

Gaps 1 and 2 are COMPLEMENTARY and most likely BOTH active: Gap 1 removes the collapse CAUSE
(ungrounded co-adapting target), Gap 2 removes the structural GUARD (we used the loophole-bearing
soft option). The measured 0.0078 -- WORSE than the old EMA+VICReg -- is over-determined by having
BOTH: an ungrounded target AND stripping the variance floor.

---

## WHAT MAKES CORTEX COLLAPSE-PROOF, AND WHICH WE ARE MISSING (direct answer to USER)

Cortex is collapse-proof via THREE stacked mechanisms, each doing a distinct job:
1. **External sensory grounding** (base of the predictive cascade) -- a fixed, high-entropy target a
   constant cannot match. **WE ARE MISSING THIS (dominant).** We regress to a learned self-referential
   embedding with no external anchor.
2. **Hard per-sample sparse coding / lateral inhibition (k-WTA)** -- a combinatorial constraint a
   collapsed rep cannot satisfy. **WE ARE MISSING THIS (structural guard).** We used soft batch
   decorrelation with a known variance-collapse loophole.
3. **Homeostatic firing-rate regulation** -- a slow soft corrective that revives under-used units.
   **WE ARE ALSO MISSING THIS, but it is NOT the structural fix** -- biology itself shows it is
   insufficient alone (Zenke). It is the residual-closer on top of (2).

We are missing #1 (dominant cause) and #2 (structural guard); #3 is a cheap add-on that closes the
k-WTA dead-unit residual. That stack is the answer.

---

## MINIMAL BRAIN-FAITHFUL CONFIG THAT STRUCTURALLY CANNOT COLLAPSE (one-axis-at-a-time)

**AXIS 1 (PRIMARY -- do first, alone, for clean attribution): external token-IDENTITY target.**
- Change: replace the next-token-input-EMBEDDING regression target with token IDENTITY via
  cross-entropy over a SAMPLED / adaptive softmax (CITED@ 2203.16868; standard, memory-cheap, avoids
  the [B,L,vocab] OOM class -- project d_model to a sampled vocab subset, not the full vocab). Keep
  the causal mask, keep everything else.
- Why brain-faithful: this IS the base of the cortical predictive cascade -- predict the real
  external signal (token identity = our "sensory input"), grounded and fixed-entropy.
- Why collapse-resistant: a constant output yields a constant logit distribution whose cross-entropy
  is bounded away from the minimum by the token marginal entropy; gradient pushes AWAY from constant.
  (Optimization-pressure guarantee -- strong; this is why LLMs do not BYOL-collapse.)
- CAN-FAIL TEST: re-run the causal arm with AXIS 1 at the SAME small proxy budget that collapsed to
  0.0078. **HARD-PASS:** rep_std clears the 0.020 floor. **HARD-FAIL:** rep_std still < 0.020 with an
  external token-identity target => target-externality is NOT the cause; escalate to Element 2/scale.

**AXIS 2 (STRUCTURAL GUARD -- add second, complementary): k-WTA / top-k on the d_model latent.**
- Change: apply a top-k (retain top-k coordinates by magnitude, zero the rest) activation on the
  latent BEFORE the prediction head; add a small auxiliary dead-unit revival term (= the homeostatic
  target-rate KL, Element 3) to close the fixed-subset residual.
- Why brain-faithful: sparse coding via lateral inhibition (Olshausen & Field); the ONLY candidate
  with a genuine per-sample HARD cardinality constraint.
- Why collapse-proof (REPRESENTATIONAL, not just optimization): a top-k latent has exactly k nonzero
  magnitude-selected coordinates per sample -- it CANNOT be the degenerate all-equal constant vector
  (ties measure-zero). This is the strongest structural guarantee of the four mechanisms.
- CAN-FAIL TEST: with top-k active, measure rep_std across a batch. **HARD-PASS:** rep_std cannot fall
  below the floor by construction AND downstream separability improves vs AXIS-1-alone.
  **HARD-FAIL:** top-k active but downstream role-separability no better than the collapsed baseline
  => hard sparsity fixes the STATISTIC without fixing the CAPABILITY (sparsity is anti-collapse but
  not sufficient for the target representation).

**CHEAPEST INTERIM (if you want ONE line before the AXIS-1 rebuild): restore the variance floor.**
- Add back an explicit VICReg-style std hinge (variance floor) ALONGSIDE Barlow. This closes the
  decorrelation loophole the prior drill's Rank-3 opened by removing it. Near-zero cost; directly
  attacks the measured 0.0078. Use as a control to attribute "was it the missing variance floor?"
  before committing to the AXIS-1 target rebuild. CAN-FAIL: if Barlow+variance-floor still collapses
  at the same budget, the loophole was not the (whole) cause -> AXIS 1 is required.

**The full minimal collapse-PROOF config = AXIS 1 (external token-identity target: removes the
cause) + AXIS 2 top-k (hard structural floor: cannot represent the collapsed vector) + tiny
homeostatic revival term (closes top-k's dead-unit residual).** Two INDEPENDENT guarantees
(optimization-pressure away from constant + representational hard-cardinality) plus a residual
closer = the brain's own three-mechanism stack. Test AXIS 1 alone FIRST (attribution), then add
AXIS 2, then the revival term only if dead-units appear.

---

## CHEAP DECISIVE TEST (single, pre-registered)

Re-run the causal arm at the SAME small proxy budget that collapsed to rep_std 0.0078, in THREE
one-axis arms (attribution-clean):
- ARM_A: AXIS-1 only (external token-identity sampled-softmax target; drop the learned-embedding
  regression; keep Barlow).
- ARM_B: current-target + restored variance floor (interim control -- isolates "was it the loophole").
- ARM_C: AXIS-1 + AXIS-2 top-k (full structural config).

## FALSIFIABLE PREDICTIONS

- **HARD-PASS:** ARM_A rep_std >= 0.020 (clears the floor with an external target, everything else
  fixed) => target-externality was the dominant cause, as diagnosed.
- **HARD-PASS (strong):** ARM_C rep_std >= 0.020 AND stable across seeds by CONSTRUCTION (top-k
  cannot collapse) => structural config confirmed collapse-proof.
- **HARD-FAIL (diagnosis wrong):** ARM_A AND ARM_B both still < 0.020 => neither target-externality
  nor the variance loophole is the cause; the collapse is scale/data/architecture -- escalate to
  the fuller build budget and re-open Element 4.
- **MIDDLE (informative):** ARM_A passes rep_std but downstream voice-role probe stays inverted =>
  collapse fixed, capability NOT (consistent with the prior drill's PROXY-LIMIT finding -- see below).

---

## CROSS-THREAD SYNTHESIS

- **SHARPENS + partly CORRECTS the prior drill** (`research_brain_faithful_collapse_free_predictive_
  encoder_objective_2026-08-01.md`): its Rank-1 ("predict the real next-token EMBEDDING") was adopted
  and STILL collapsed because the next-token INPUT EMBEDDING is NOT external -- it is a learned,
  co-adapting, ungrounded target. The genuinely-external target is token IDENTITY (the prior drill's
  own "fully-external fallback," now PROMOTED to primary). Its Rank-3 (replace VICReg variance hinge
  WITH Barlow) OPENED the variance-collapse loophole -- Barlow needs the variance floor, not instead
  of it. This drill reclassifies both.
- **PROXY-LIMIT caveat carried forward (MEASURED, prior drill):** at the lite proxy budget the
  voice-invariant role capability does NOT emerge for ANY arm (bidir/random both 0.000). So a rep_std
  HARD-PASS proves collapse-FIX but CANNOT prove downstream de-inversion at this budget -- that needs
  the fuller build. Report a rep_std pass as "collapse fixed," not "capability earned."
- **Consistent with USER's foundational locks:** brain = existence proof (a brain-faithful predictive
  learner does NOT collapse => our collapse is a fidelity BUG, not a ceiling); flat/collapsed learning
  result = broken experiment, not a wall; do the HARD blocking thing (external target + hard sparsity)
  not the easy soft-regularizer patch.

## SUBSTRATE-PRODUCT IMPLICATIONS

The encoder is the CENTRAL concept representation. A collapse-proof, brain-faithful objective is the
precondition for every downstream comprehension competency (entity-identity, voice-invariant role,
coref) -- a collapsed encoder makes all of them unlearnable. The fix is fully glass-box and
no-borrowed-embedding: an external token-IDENTITY target (own tokenizer, own vocab), hard k-WTA
sparsity, and a homeostatic revival term are all NATIVE architecture/objective decisions -- no
pretrained vector, no bolt-on reader. This directly serves the from-scratch encoder build the
07-30 spec depends on: the causal encoder should predict token IDENTITY (sampled softmax) under a
top-k sparse latent, NOT regress to a self-referential embedding.

## CITATIONS (verified count)

CITED@ this cycle (3 parallel Sonnet lit-scans, generic-term WebSearch, query-privacy compliant):
Olshausen & Field 1996; Barlow 1952 (redundancy reduction); k-WTA spiking-network (1904.12591);
KATE/k-competitive AE (1705.02033); Top-K/BatchTopK SAE (2023-26); Carandini & Heeger 2012 /
Heeger 1992 (divisive normalization); Turrigiano (firing-rate set-point / synaptic scaling);
Desai/Marder (homeostasis); Zenke & Gerstner 2017 (temporal paradox -- homeostasis insufficient
alone); Ng CS294A (KL sparse-AE penalty); MoE load-balancing (2408.15664); BatchNorm-as-homeostat
correspondence (bioRxiv 2020.07.17.197640); Rao & Ballard 1999; Huang & Rao 2011; Friston 2005
(free-energy predictive coding); Bastos et al. 2012 (canonical microcircuits / error units);
precision-weighting (dopamine biorxiv 288936; acetylcholine eLife 91475); SimSiam (Chen & He 2021);
BYOL (Grill et al. 2020); Tian et al. 2021 (SSL dynamics without contrastive pairs); CMU ECCV22
(non-contrastive collapse); MAE (He et al. 2022); latent-MIM (2407.15837); "Neural Collapse Is
Forbidden" (2607.09487); Implicit Geometry of Next-Token Prediction (2408.15417); VICReg dimensional
collapse (OpenReview YevsQ05DEN7); SIGReg. Continuous-output/sampled-softmax external target
carried from prior drill: 1902.11269, 2203.16868. **Verified new-anchor count this cycle: ~30
distinct works across 3 scans.** ESTABLISHED/CONTESTED flags applied per-claim throughout.

## WEAKEST LINK

Two: (1) the k-WTA "fixed-subset-always-wins" dead-unit residual means top-k is not a COMPLETE
standalone guarantee -- it needs the auxiliary revival/homeostatic term, so "structurally cannot
collapse" is precise for full-constant collapse but needs the add-on for the narrower dead-subset
mode. (2) The prior "predict a real target" recommendation ALREADY partly failed (the learned-
embedding version collapsed), which is a cautionary signal that reasoning about "real/external
target" was imprecise before -- this drill sharpens it (learned embedding is NOT external), but the
core claim that token-IDENTITY + top-k clears the floor at OUR specific small causal-transformer
budget is a synthesis extrapolation, MEASURED-consistent but not yet directly tested. That is
exactly what the 3-arm can-fail test settles cheaply.

**P_deflated (external token-identity target + top-k structurally clears the 0.020 collapse floor at
the same proxy budget): 0.42.** Base REASONED@ ~0.60 (two independent, well-established guarantees +
LLMs empirically don't collapse + top-k is a hard representational gate) minus 0.18 lit-scan
calibration penalty (uncharted transfer to our specific small causal-transformer scale; one prior
"real target" recommendation already partly missed) = 0.42, under the 0.50 novel-synthesis cap.
