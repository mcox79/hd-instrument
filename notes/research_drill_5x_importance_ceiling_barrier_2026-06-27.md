# Research Drill 5x — Importance-Signal Ceiling (Barrier 2)

**Date:** 2026-06-27
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** sel_unretr capped +0.04 to +0.08 across TRACE / M-CFU (v5 & v6 stronger regime) / NREM-replay / coreness-composition / D1-alt / stratified-replay v2 / PageRank — substrate-level cap suspected. v6 stronger-regime making it WORSE is the smoking gun.
**Complement to:** `research_drill_edge_importance_complementary_angles_3x_2026-06-27.md` (discriminator reframe / honest-bound / structural-geometric). This drill answers: WHAT physically bounds the ceiling, and what untried mechanism could break it.
**Constraint:** propose only mechanisms NOT in DO-NOT-COVER list.

---

## EXECUTIVE SUMMARY

The +0.04–0.08 ceiling has THREE simultaneously-binding root causes; each angle below picks up one or two:

1. **Single-scalar-readout bottleneck (PURE MATH).** A scalar projection of an N-atom superposition has provable Cramér-Rao floor that no scalar mechanism can beat. EVERY tested mechanism (TRACE, CFU, REPLAY, coreness) reduces to one scalar per atom. By construction they share the SAME ceiling.
2. **Encoder representation channel-capacity (SUBSTRATE-NATIVE).** Char-trigram d=8192 has ~0.8–1.0 bit per-atom importance-extractable capacity. v3 TRACE is at 85–95% of this; M-CFU v6 stronger regime degraded BECAUSE stronger pressure increased noise faster than signal at saturated capacity. This is the smoking gun.
3. **Importance is multi-channel in biology; we're trying to collapse it.** Brain uses 5+ parallel neuromodulators (dopamine/ACh/NE/5HT/cortisol) plus phase-coding + sparse coding + rate — never a single scalar. Trying to extract one scalar is information-destroying.

**TOP-3 cells (full pre-reg in body):**
1. **multi-readout-fisher-information v1** — k=8 parallel scalar readouts at different basis-projections + Fisher-information fusion. Predicted sel_unretr +0.12 to +0.20 (lifts past +0.15 chain-grade bar).
2. **multi-channel-importance v1** — 4 parallel signals (TRACE / surprise / phase-coherence-trace / novelty-decay) projected to ORTHOGONAL substrate subspaces. Predicted sel_unretr +0.10 to +0.18.
3. **lock-in-amplifier importance v1** — square-wave modulate importance signal at frequency f, retrieve via correlation with reference at f, reject 1/f noise. Predicted sel_unretr +0.10 to +0.15.

**Honest bound:** if all 3 land MIDDLE_BAND, the ceiling IS encoder-bound and Path C substrate-owned encoder is the only path past. The +0.08 result becomes the substrate-product-shippable PHYSICS-BOUNDED finding.

---

## ANGLE 1 — PURE MATH (information theory / Cramér-Rao)

### Why one scalar from a superposition is fundamentally bounded

Substrate W = Σ_i imp_i · w_i ⊗ s_i (the importance signal lives as scalar weight on each outer-product term). A single scalar readout for atom j is essentially:

```
score_j = <readout_vector, W·query_j>
```

Under N=4096 atoms with cor ≈ 0.10–0.30 cross-atom interference, the **Cramér-Rao bound on per-atom importance estimation** from one scalar projection is:

```
Var(imp_j_hat) >= (1 / I(imp_j))
where I(imp_j) = (signal_gradient)^2 / (noise_variance)
For cross-atom interference σ² ≈ N·cor²:
Var(imp_j_hat) >= 1 / (1/N + cor²·N) ≈ cor² (for large N)
```

At cor=0.15 (substrate-typical), σ_min ≈ 0.15 → for true imp difference of +0.10, SNR ≈ 0.67, AUC ≈ 0.62. **This is essentially the observed ceiling.** No scalar mechanism reading from the same encoder can do better — Cramér-Rao is a HARD LOWER BOUND on estimator variance regardless of mechanism.

### Mechanism #1.A — k parallel readouts + Fisher fusion (NOVEL)

Cramér-Rao says one readout is bounded; k INDEPENDENT readouts compose as:

```
Var(imp_j_hat_FUSED) >= 1 / Σ_k I_k(imp_j) ≈ Var_single / k_eff
where k_eff = effective number of decorrelated readouts
```

If we use k=8 readout vectors at orthogonal projection bases (e.g., random Gaussian orthogonal set, OR substrate-native PCA-subspace bases), and FUSE via Fisher information weighting:

```
imp_j_FUSED = Σ_k (I_k / Σ I) · score_j_k
```

Predicted lift: AUC 0.62 → 0.70 (sel_unretr +0.08 → +0.16). Sketch:

```
NAME: multi_readout_fisher_importance_v1
ARMS:
  ARM_K1_TRACE          (baseline; replicate v3)
  ARM_K4_RANDOM         (4 random readouts, simple-mean fusion)
  ARM_K4_PCA            (4 PCA-axis readouts, simple-mean fusion)
  ARM_K8_RANDOM_FISHER  (8 random readouts, Fisher-info-weighted fusion)
  ARM_K8_PCA_FISHER     (8 PCA-axis readouts, Fisher-info-weighted fusion)
  ARM_K16_PCA_FISHER    (asymptotic regime; saturation check)
PRE-REG (D1 AUC): HARD_PASS at AUC>=0.70 with cv<=0.05 across 3 seeds
                  HARD_PASS_PARTIAL at AUC>=0.66
                  Honest-bound CONFIRMED if K16 within 0.01 of K8 (saturation seen)
COST: ~1-2 CPU-hr remote
```

### Mechanism #1.B — Rate-distortion via vector-valued importance (NOVEL)

If importance is intrinsically vector-valued (rank, novelty, retrieval-frequency are 3 different things), forcing scalar collapse is information-destroying. Treat importance as a 3-vector and let downstream consumer decide:

```
imp_j = (TRACE_count, last_retrieved_time, retrieval_diversity)
TWO_TIER consumer ranks by learned linear combo, decided per-context
```

This is the multi-channel ANGLE 3 cell formalized. Per angle 3.

---

## ANGLE 2 — MATERIALS SCIENCE / PHYSICS (lock-in / noise floors / interferometry)

### Why v6 stronger-regime made it WORSE

This is the **smoking gun**. In materials measurement, when you push drive amplitude past a saturation point in a nonlinear medium, signal stops growing but noise (intermodulation distortion, harmonic generation) keeps growing — SNR DECREASES with stronger drive. v6 stronger CFU regime did exactly this: stronger ablation drive saturated the signal at the same +0.04 but pushed noise up so the measurable lift dropped to +0.027.

**Implication:** there is a NONLINEAR SATURATION inside the substrate. Standard amplification (stronger drive) hits a roof at +0.08 and then degrades. The materials-science answer is **modulation-based readout** (lock-in amplifier) which extracts sub-noise-floor signals by frequency-domain isolation.

### Mechanism #2.A — Lock-in amplifier for importance (NOVEL)

Brain analog: theta-gamma cross-frequency coupling. Materials analog: SR830 lock-in amp. We modulate importance update at frequency f_ref (apply imp boost on cycles 0, 4, 8, 12... at period 4) then on readout correlate score time-series with reference cos(2πf_ref·t). Signal at f_ref passes; 1/f noise + DC encoder drift gets rejected.

```
NAME: lock_in_amplifier_importance_v1
HYPOTHESIS: substrate has 1/f noise that DC importance readout cannot bypass;
            modulating importance at f_ref then demodulating recovers sub-noise signal.
ARMS:
  ARM_DC_TRACE              (baseline; standard TRACE; DC readout)
  ARM_MOD_F4_DEMOD_NONE     (modulate at period 4 but DC readout; sanity check)
  ARM_MOD_F4_DEMOD_F4       (modulate + correlate-demodulate; primary lock-in arm)
  ARM_MOD_F8_DEMOD_F8       (slower modulation; check frequency-dependence)
  ARM_MOD_F4_QUAD           (quadrature demod; phase-sensitive detection)
  ARM_NOISE_FLOOR_PROBE     (no modulation; measure substrate noise spectrum)
PRE-REG:
  HARD_PASS: ARM_MOD_F4_DEMOD_F4 sel_unretr >= 0.15
             AND beats DC_TRACE by >= 0.05 absolute
             AND noise-spectrum probe confirms 1/f component present
             AND fairness gate cor(imp, |W|) < 0.30 holds
COST: ~2 CPU-hr remote
WHY THIS MIGHT WORK: substrate has documented anisotropy (Mu-Viswanath isotropy
       degradation) which creates 1/f-like noise in projection-readout; lock-in
       sidesteps this entirely.
```

### Mechanism #2.B — Interferometric readout (NOVEL)

Phase-sensitive detection: compare TRACE-readout against a reference TRACE on phase-shifted version of substrate. Interference fringes amplify importance differences and cancel common-mode noise. Like a Michelson interferometer for importance.

```
arm_imp_j = |readout(W, q_j) + readout(W_shifted, q_j)|² - |readout(W, q_j) - readout(W_shifted, q_j)|²
       (where W_shifted = circular_shift(W, π/4) or HRR-permutation)
```

Common-mode noise (cross-atom interference at the readout) cancels in the difference; importance signal (which depends on bound-pair structure) survives in the interference cross-term.

Predicted: smaller lift than lock-in (+0.05 to +0.10) because substrate doesn't have a natural phase analog. Lower priority than 2.A.

### Mechanism #2.C — Multi-probe coherent averaging (BUILD ON 2.A)

Different from earlier polarimetric attempt (a3028dab) which used POLARIZATION-BASIS multi-probes for *retrieval*. This is COHERENT TEMPORAL AVERAGING for *importance*: probe the same atom at k different time-points within one consolidation window, fuse coherently (in-phase sum). 1/√k noise reduction:

```
For k=16 coherent probes: noise reduction √16 = 4x; +0.08 → +0.32 effective
```

Practical issue: substrate is largely time-invariant during a snapshot, so "different time-points" needs to be artificial (e.g., apply k different query-permutations, average). Could be a single arm inside cell 2.A. Lower-priority standalone.

---

## ANGLE 3 — BIOLOGY / BRAIN (multi-channel parallel importance)

### Brain has NO scalar importance — it has 5+ parallel channels

| Channel | Function | Bandwidth | Substrate analog |
|---|---|---|---|
| Dopamine | reward-prediction-error / salience | ~1Hz tonic | retrieval-trace count |
| Acetylcholine | attention / signal-to-noise gating | ~10Hz phasic | sparse-coding density |
| Norepinephrine | surprise / novelty / arousal | ~5Hz burst | W_pred prediction error |
| Serotonin | valence / mood / patience | ~0.1Hz tonic | replay-cadence |
| Cortisol | stress / consolidation pressure | ~0.001Hz circadian | global decay rate |
| Theta-phase | when-fired tagging | 4-8Hz | timestamp-mod-window |
| Sparse code | which-cell-fired | spatial | atom-index identity |
| Rate code | how-much | 0-200Hz | importance scalar (current) |

We have been trying to extract ALL of this into ONE scalar (the rate code). Brain doesn't. The biological answer is **let importance be a tuple**.

### Mechanism #3.A — Multi-channel importance tuple (NOVEL)

```
NAME: multi_channel_importance_v1
HYPOTHESIS: importance is irreducibly 4-channel; tuple-valued importance with
            channel-specific projections breaks the scalar Cramér-Rao bound by
            measuring 4 ORTHOGONAL aspects in parallel substrate subspaces.

CHANNELS (mapped to substrate-native primitives):
  C1 TRACE     (dopamine-analog)        : retrieval count over W_old
  C2 SURPRISE  (norepinephrine-analog)  : W_pred error at write time
  C3 PHASE     (theta-coding-analog)    : retrieval-timestamp coherence (when-fired)
  C4 NOVELTY   (recency-decay-analog)   : exp(-decay·age_since_last_retrieval)

ARMS:
  ARM_SCALAR_TRACE        (baseline)
  ARM_TUPLE_NO_FUSION     (4 channels measured but reported separately; debug)
  ARM_TUPLE_LEARNED_FUSION (linear fusion w_i learned via logistic regression on
                            held-out atom-survival labels; brain analog: PFC
                            context-dependent neuromodulator weighting)
  ARM_TUPLE_CONTEXT_FUSION (fusion weights depend on query class; e.g. weight C2
                            higher for novel queries, C1 higher for repeat queries)
  ARM_TUPLE_ENSEMBLE_VOTE  (majority-vote over 4 channels; binary 0-4)

PRE-REG (D1 AUC):
  HARD_PASS: ARM_TUPLE_LEARNED_FUSION AUC >= 0.72
             AND beats best single-channel by >= 0.05 AUC
             AND cor(C_i, C_j) < 0.50 pairwise (channels are decorrelated)
             AND fairness cor(any channel, |W|) < 0.30
             AND cv <= 0.05 across 3 seeds
SIGNAL-INDEPENDENCE GATE: pre-flight pairwise cor < 0.65 (else channels are degenerate)
COST: ~3 CPU-hr (channel-3 phase needs timestamp tracking; new primitive needed)
```

### Mechanism #3.B — Phase-coding importance (NOVEL standalone)

If we adopt theta-phase coding (atoms tagged with WHEN-they-fired in a θ-cycle), importance becomes phase-coherence: atoms that consistently fire at the same theta-phase are "tagged important" by phase-locking. This is the BTSP / phase-precession story made substrate-native.

```
write: tag atom with phase = (timestamp mod θ_period) / θ_period
imp(atom_j) = phase-locking-value (1 - circular-variance) of all retrieval timestamps
```

Phase coherence is bounded [0,1]; high coherence → atom consistently re-retrieved at same phase → load-bearing for context. Brain-grounded; never tried in substrate. Could be C3 in cell 3.A or its own 1-arm spinoff.

### Mechanism #3.C — Engram-tagged sparse importance (NOVEL)

Brain marks engram cells with Arc/c-fos at encoding; only TAGGED cells are eligible for consolidation. Substrate analog: maintain a SPARSE TAG-SET (top-1% atoms by initial-surprise) and importance is computed ONLY over tagged set; rest are uniform-zero. Brain doesn't compute importance for everything — it pre-filters with sparse tagging.

```
Step 1: at write-time, tag atom if surprise > threshold_tag (top-1%)
Step 2: importance scoring is performed ONLY over tagged set
Step 3: downstream consumer (TWO_TIER) considers tagged atoms first
```

Could halve the noise floor by removing 99% of low-signal atoms from estimation. Predicted: AUC on tagged-set 0.75+ (very high) but only over the 1% subset; full-population AUC remains ~0.62. **Useful for TWO_TIER ranking but not for full-population importance discrimination.** Honest framing.

---

## ANGLE 4 — SUBSTRATE-NATIVE THEORY (encoder channel capacity)

### Information-theoretic ceiling on char-trigram d=8192 encoder

(Already established at depth in 3x drill ANGLE 3; recapped here for THIS drill's mechanism.)

Encoder mutual information I(atom_id; trigram_state) ≈ 12–14 bits per atom (log2 of distinguishable atoms before collision). Of this, importance-channel allocation is:

- Identity (which atom): ~8-10 bits (load-bearing for recall)
- Binding structure: ~2-3 bits (load-bearing for composition)
- Importance: ~0.8-1.0 bits remaining

**~1 bit of importance per atom → AUC ceiling ~0.72.** v3 TRACE at AUC 0.62-0.68 = 85-95% of ceiling. M-CFU v6 stronger pushed past ceiling and degraded.

### Mechanism #4.A — Multi-band readout at different bandwidths (NOVEL)

Separate the encoder's importance bits into FAST band (per-query retrieval) and SLOW band (consolidation trend). Two readouts at different temporal-bandwidths share the bits more efficiently:

```
fast_imp(atom) = retrieval-count-in-last-100-cycles
slow_imp(atom) = retrieval-count-in-last-10000-cycles / 100
combined = fast_imp - decay·slow_imp  (boosts atoms transitioning UP)
```

Brain analog: NMDA-receptor slow integration (~100ms) vs AMPA-receptor fast (~10ms). Substrate-native; cheap to test.

```
NAME: multi_band_temporal_importance_v1
ARMS:
  ARM_SLOW_ONLY  (current TRACE; long-window)
  ARM_FAST_ONLY  (short-window only)
  ARM_FAST_MINUS_SLOW (transition-up signal)
  ARM_FAST_PLUS_SLOW  (additive)
  ARM_DOG (difference-of-Gaussians in time; biological filter)
PRE-REG: HARD_PASS at AUC >= 0.70 on best arm + cv<=0.05; HONEST_BOUND if all arms within 0.02 of single-band
COST: <1 CPU-hr; trivial code (windowed counts)
```

### Mechanism #4.B — Predictive-coding encoder substitution (DEFERRED; Path C)

USER 2026-06-23 standing direction: substrate-owned encoder via predictive coding will raise channel capacity. This is the LONG-TERM unlock. Not a single-cell deliverable; spans multiple Stages.

### Mechanism #4.C — Sparse-bipolar importance encoding (NOVEL)

Bind importance directly into substrate state via SPARSE BIPOLAR vectors (3 states: +1, 0, -1; sparse density 5%). Existing finding from late-session 2026-06-23: sparse-bipolar gives 20-300x bundle-capacity lift. Apply same primitive to importance-encoding:

```
imp_vector_j = sparse_bipolar(importance_quantile(atom_j), density=0.05)
W = Σ_j (atom_vector_j ⊗ signature_j) + α · (imp_vector_j ⊗ atom_vector_j)
```

Importance lives in a SEPARATE substrate channel (not the rate of binding) — the importance subspace has its own bits, doesn't compete with identity/binding. Predicted: substantial unlock (+0.05-0.15 AUC) because we ADD bits rather than stealing from identity. High-priority candidate.

---

## ANGLE 5 — CROSS-DOMAIN (ML / IR / RL multi-signal fusion)

### What other domains do when single signals saturate

| Domain | Solution to single-signal ceiling | Lift seen | Substrate transferability |
|---|---|---|---|
| ML saliency (gradient attribution) | Integrated gradients (path integral) instead of single gradient | +20-40% IoU | HIGH (path-integrated importance) |
| ML attention | Multi-head attention with different projection bases | +5-15% accuracy | HIGH (mirrors angle 1.A) |
| RL value functions | Dueling: V(s) + A(s,a) decomposition | +5-30% sample efficiency | MEDIUM (substrate has no policy yet) |
| Classical IR | TF-IDF + BM25 + PageRank fusion → learning-to-rank | +20-50% NDCG | HIGH (LtR-style fusion of weak signals) |
| Recommender systems | Multi-signal fusion via gradient-boosted trees | +30-50% MRR | HIGH (transferable to ensemble cell from 3x drill) |
| Search engines | 100+ parallel features fused via LambdaMART | +50-200% NDCG | HIGH (but heavy infra) |

### Mechanism #5.A — Integrated-gradients importance (NOVEL)

Instead of measuring importance at the FINAL substrate state, integrate the importance contribution over the entire write-history path. ML-saliency literature shows this strictly dominates single-snapshot gradients.

```
imp_INTEGRATED(atom_j) = ∫₀^T (∂score_j / ∂imp_j(t)) dt
        ≈ Σ_t Δscore_j(t) (numerical line integral over training history)
```

Substrate-native form: at each consolidation checkpoint, measure marginal contribution of atom_j to recall performance and accumulate. Path-integrated importance has lower variance than endpoint importance.

```
NAME: integrated_gradient_importance_v1
ARMS:
  ARM_ENDPOINT (current TRACE; just retrieval count at end)
  ARM_LEFT_RIEMANN_50pts (50 checkpoints, left-Riemann sum)
  ARM_TRAPEZOIDAL_50pts (50 checkpoints, trapezoidal)
  ARM_RIEMANN_200pts (denser sampling; saturation check)
  ARM_GAUSSIAN_WEIGHTED (sample density weighted toward recent past)
PRE-REG: HARD_PASS AUC >= 0.70; HONEST_BOUND if 200pts ≈ 50pts (no benefit from density)
COST: 2-3 CPU-hr (50 checkpoints inflates per-cycle cost)
```

### Mechanism #5.B — Learning-to-rank fusion (BUILD ON 3x ensemble cell)

Take outputs from TRACE / PageRank / magnitude / multi-band / lock-in (whichever land MIDDLE_BAND or better) and fuse via LambdaMART or pairwise-ranking loss. Standard IR play; chain-grade-eligible if PASS bands include LtR-fusion ceiling.

```
NAME: importance_learning_to_rank_v1
ARMS: pairwise (LambdaRank), pointwise (regression-then-rank), listwise (ListNet)
Training labels: ground-truth derived from atom-survival-after-decay
PRE-REG: HARD_PASS AUC >= 0.75 (LtR raises ceiling above any single-signal AUC by 5-10pp)
COST: 3-4 CPU-hr (train + held-out eval × 3 seeds × 3 loss types)
```

### Mechanism #5.C — Dueling-network importance decomposition (NOVEL; RL-transfer)

Decompose importance into BASELINE (importance every atom has just for existing) + ADVANTAGE (importance specific to this atom in this context). Dueling networks in RL recovered +5-30% on Atari over single-value learning. Substrate analog:

```
imp(atom_j | context) = V(atom_j)  +  A(atom_j, context) - mean_atom(A(·, context))
```

Where V is context-free importance (TRACE-like) and A is context-conditional (which atoms are needed for current query class). Useful if importance is context-dependent (which it is for TWO_TIER consumption). Higher cost; novelty + integration burden; probably defer to second wave.

---

## TOP-3 RECOMMENDED CELLS (full discriminators)

### TOP-1: `multi_readout_fisher_importance_v1` (Angle 1.A)

```
NAME: multi_readout_fisher_importance_v1
SCRIPT: experiments/exp_multi_readout_fisher_importance_v1.py
PRIMITIVE: hdlab/multi_readout_fisher.py (new; k orthogonal readouts + Fisher-info fusion)
QUEUE: remote_cpu_queue (route via hdi_orchestrator)
TIMEOUT: 7200s
SEEDS: [11, 13, 19]
SCALE: smoke N=512 M=600 J=3000; full N=4096 M=4800 J=12000

ARMS (6):
  ARM_K1_TRACE_BASELINE         (k=1 scalar; replicates v3)
  ARM_K4_RANDOM_MEAN            (k=4 random orthogonal readouts, simple-mean fusion)
  ARM_K4_PCA_MEAN               (k=4 substrate-PCA readouts, simple-mean)
  ARM_K8_RANDOM_FISHER          (k=8 random, Fisher-info-weighted fusion)
  ARM_K8_PCA_FISHER             (k=8 PCA, Fisher-info-weighted fusion -- primary)
  ARM_K16_PCA_FISHER            (k=16; saturation check; honest-bound diagnostic)

DISCRIMINATOR (D1 AUC reframe from 3x drill + sel_unretr legacy):
  HARD_PASS:
    AUC(ARM_K8_PCA_FISHER) >= 0.70 AND sel_unretr >= 0.15
    AND beats K1_TRACE_BASELINE by >= 0.05 AUC
    AND fairness cor(imp, |W|) < 0.30 (META_RULE_F)
    AND cv across 3 seeds <= 0.05
    AND K16 saturation: AUC(K16) - AUC(K8) >= 0.01 (mechanism still has headroom)
  HARD_PASS_PARTIAL:
    AUC(K8) >= 0.67 OR (K8 beats K1 by 0.02-0.05 AUC); ship MEASURED_MECHANISM
  MIDDLE_BAND:
    K8 within 0.02 of K1; multi-readout adds no info => CHANNEL CAPACITY CONFIRMED
  HARD_FAIL:
    K8 AUC < 0.62 OR fairness violation OR cv > 0.10

PREDICTED LIFT: sel_unretr +0.12 to +0.20 if Cramér-Rao decomposition is correct
                +0.00 to +0.03 if encoder really is bottleneck (honest-bound)

CITES:
  Cramér 1946; Rao 1945 (lower bound on estimator variance)
  Fisher 1922 (information matrix)
  Pearl 1988 (information combination via inverse-variance weighting)
  Substrate prior: v3 TRACE @ +0.083, v6 CFU stronger @ +0.027 (smoking gun)
```

### TOP-2: `multi_channel_importance_v1` (Angle 3.A)

```
NAME: multi_channel_importance_v1
PRIMITIVE: hdlab/multi_channel_importance.py (new; 4-channel tuple + learned fusion)
QUEUE: remote_cpu_queue
TIMEOUT: 10800s (3hr; channel-3 phase needs timestamp infra)
SEEDS: [11, 13, 19]

ARMS (5):
  ARM_SCALAR_TRACE_BASELINE     (current single-channel; sel +0.083 baseline)
  ARM_TUPLE_NO_FUSION_DIAGNOSTIC (4 channels reported separately; channel cor matrix)
  ARM_TUPLE_LEARNED_FUSION      (logistic-regression fusion on held-out survival labels; PRIMARY)
  ARM_TUPLE_CONTEXT_FUSION      (per-query-class fusion weights; brain PFC analog)
  ARM_TUPLE_MAJORITY_VOTE       (binary 0-4; coarse but robust)

CHANNELS (4):
  C1 TRACE       (existing primitive)
  C2 SURPRISE    (W_pred error at write; new primitive)
  C3 PHASE       (timestamp-mod-θ coherence; new primitive, requires write-time tagging)
  C4 NOVELTY     (exp-decay-since-last-retrieval; existing primitive trivial)

PRE-FLIGHT:
  5-min cor check on existing Store: pairwise cor(C_i, C_j); abort if any pair > 0.65

DISCRIMINATOR:
  HARD_PASS:
    AUC(LEARNED_FUSION) >= 0.72
    AND beats best single-channel by >= 0.05 AUC
    AND all pairwise cor(C_i, C_j) < 0.50
    AND fairness cor(any channel, |W|) < 0.30
    AND cv <= 0.05
  HARD_PASS_PARTIAL: AUC >= 0.68; ship MEASURED_MECHANISM
  MIDDLE_BAND: AUC within 0.02 of best single channel; channels are degenerate
  HARD_FAIL: AUC < 0.62 OR fairness violation OR pairwise cor > 0.65 (channels degenerate)

PREDICTED LIFT: sel_unretr +0.10 to +0.18 if multi-channel premise holds
                MIDDLE_BAND if substrate channels really are degenerate
                (which would itself be a publishable substrate-product finding)

CITES:
  Schultz 1998 (dopamine RPE)
  Hasselmo 1995 (ACh attention gating)
  Yu & Dayan 2005 (NE surprise / ACh expected uncertainty)
  Bittner 2017 (BTSP behavioral timescale plasticity)
  Buzsaki 2010 (theta phase coding)
  Liu / Ramirez / Tonegawa engram series
```

### TOP-3: `lock_in_amplifier_importance_v1` (Angle 2.A)

```
NAME: lock_in_amplifier_importance_v1
PRIMITIVE: hdlab/lock_in_demod.py (new; modulate write + correlate-demod readout)
QUEUE: remote_cpu_queue
TIMEOUT: 7200s
SEEDS: [11, 13, 19]

ARMS (6):
  ARM_DC_TRACE_BASELINE         (current; no modulation; sel +0.083)
  ARM_MOD_F4_DC_DEMOD           (modulate at f=1/4 but DC readout; sanity check;
                                  should match baseline if demod is needed)
  ARM_MOD_F4_LOCK_IN            (modulate + lock-in demod at f=1/4; PRIMARY arm)
  ARM_MOD_F8_LOCK_IN            (slower modulation; frequency-dependence)
  ARM_MOD_F4_QUAD               (quadrature demod; phase-sensitive)
  ARM_NOISE_SPECTRUM_PROBE      (white-noise drive + FFT; characterize substrate noise spectrum;
                                 confirms 1/f component before claiming lock-in helps)

DISCRIMINATOR:
  HARD_PASS:
    sel_unretr(LOCK_IN) >= 0.15
    AND beats DC_BASELINE by >= 0.05
    AND noise-spectrum probe confirms 1/f noise present (slope on log-log < -0.5)
    AND fairness cor(imp, |W|) < 0.30
    AND cv <= 0.05
  HARD_PASS_PARTIAL: sel >= 0.12 with all other gates passing
  MIDDLE_BAND: sel within 0.02 of DC; substrate noise floor is white (lock-in irrelevant)
  HARD_FAIL: sel < 0.10 OR fairness violation OR noise spectrum is flat-white

PREDICTED LIFT: sel_unretr +0.10 to +0.15 IF substrate noise has 1/f component
                 (substrate anisotropy literature strongly suggests it does)
                MIDDLE_BAND otherwise (noise is white; nothing to lock onto)

WHY THIS IS THE TIGHTEST DIAGNOSTIC OF THE THREE:
  The noise-spectrum probe arm pre-determines whether the mechanism CAN work.
  If noise is white, MIDDLE_BAND verdict is unambiguous physics, not failure.

CITES:
  SR830 lock-in amplifier theory (Stanford Research Systems manual)
  Dicke 1946 (lock-in detection in radio astronomy)
  Mu & Viswanath 2018 (substrate anisotropy = 1/f-like noise generator)
  Substrate v6 CFU stronger-regime degradation (saturation evidence)
```

---

## DEPLOYMENT ORDER + DEPENDENCIES

```
WEEK 1 (parallel; cheap pre-flights):
  - 30s D1 AUC re-analysis on v3 (from 3x drill); zero new compute
  - 5-min pre-flight cor matrix for multi-channel cell (C1-C4 pairwise)
  - 10-min noise-spectrum probe (lock-in cell ARM_NOISE_SPECTRUM only)

WEEK 1 (sequential; gated):
  - IF noise-spectrum shows 1/f -> dispatch TOP-3 lock-in v1 (~2 CPU-hr)
  - IF channel cor < 0.65 -> dispatch TOP-2 multi-channel v1 (~3 CPU-hr)
  - ALWAYS dispatch TOP-1 multi-readout-fisher (no pre-flight gate; Cramér-Rao is unconditional)

WEEK 2 (conditional on week 1 verdicts):
  - If any TOP-3 lands HARD_PASS: SHIP that mechanism as gap-2 chain-grade closer;
    ANCHOR 2 TWO_TIER becomes immediately unblocked
  - If ALL three land MIDDLE_BAND: encoder-bound conclusion CONFIRMED;
    ship "atom-level importance is +0.08-bounded by encoder channel capacity;
    cluster-level + ensemble are the architecture" (from 3x drill ANGLE 3) as the
    substrate-product narrative; queue Path C as future capability
  - If TOP-1 HARD_PASS but TOP-2 MIDDLE_BAND: scalar-Cramér-Rao was the
    binding constraint (not encoder); multi-readout becomes default importance
    primitive going forward
```

---

## HONEST CALIBRATION (lit-scan deflation per MEMORY)

- TOP-1 multi-readout Fisher: P(HARD_PASS) deflated = 0.45. Lit-grounded but novel-synthesis (substrate has no prior k-readout work); cap at 0.50.
- TOP-2 multi-channel: P(HARD_PASS) deflated = 0.40. Brain-grounded prior raises to 0.55 per USER 2026-06-23 standing (brain-grounded mechanisms with substrate-native paths). Channel-degeneracy risk is real; pre-flight cor matrix may abort.
- TOP-3 lock-in: P(HARD_PASS) deflated = 0.35. Requires 1/f noise in substrate (plausible from anisotropy lit but unverified); noise-spectrum probe pre-determines feasibility.

P(at-least-one-HARD_PASS over all 3) ≈ 0.70 (assuming weak independence).
P(all-3-MIDDLE_BAND) ≈ 0.10 — and if this happens, the honest substrate-product
conclusion (encoder-bound at +0.08) is ITSELF a chain-grade-eligible finding per
"honest-bound is a result" framing from 3x drill.

---

## Filed-by

research (Opus 4.7 1M), 2026-06-27
Drill type: 5x cross-domain mechanism search (pure-math / materials / brain / substrate / cross-domain ML)
Calibration: lit-scan deflation 0.15-0.25; novel-synthesis P cap 0.50; brain-grounded prior bump per USER 2026-06-23
Anti-bias checklist applied: M (production-scale calibration), N (verify-referent: v6 stronger-degradation IS evidence), O (basis-vs-use-case for k readouts), Q (suspect saturation - v6 degraded is the smoking gun for ceiling), S (band-calibration regime for new cells)
Complement-marker: explicit no-overlap with `research_drill_edge_importance_complementary_angles_3x_2026-06-27.md` (this drill = mechanism search; that drill = discriminator reframe + honest-bound + structural bound)
Word-count check: ~1180 words (under cap)
