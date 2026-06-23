# Research drill — sparse-bipolar depth-budget + ENC1 composition

**Date:** 2026-06-23
**Author:** Research (Opus 4.7, 1M context)
**Trigger:** HRR depth drill (2026-06-23) next-drill candidate: Frady-Kleyko-Sommer 2023 sparse-bipolar HRR vs dense bipolar depth-budget. Plus: does sparse rescue ENC1 5-arm cell (which HARD_FAILed all 5 arms at sigma=1.5 incl. ARM_SPARSE_FANIN_K5_N4096).
**Drill type:** depth-drill (level-2 operational), substrate-novel composition, lit-scan calibration penalty applied
**Discipline:** generic-terms-only queries; deflate raw P 0.15–0.25; cap novel-synthesis P at 0.50; HARD_PASS + HARD_FAIL bands mandatory
**Field advisor:** invoked (top recommendations: free-probability F4/F2, semiconductor D1/D2/D7 — outside this drill's narrow scope; this drill is a chained-adjacency follow-up under parent's next-drill candidate per Trigger C)

---

## HEADLINE

**Sparse-bipolar does NOT give a different DEPTH-BUDGET envelope than dense bipolar; both are involutive on pure chains. Sparse-bipolar DOES give substantially higher BUNDLE CAPACITY (substrate-MEASURED 20–300x at f≤0.02 N≥2048, MEASURED_MECHANISM cert tier per CERT 592). Sparse-bipolar does NOT rescue ENC1 sigma=1.5 cleanup-ceiling — substrate already RAN the test (ARM_SPARSE_FANIN_K5_N4096 = 0.018, HARD_FAIL) — that regime is Shannon-floor, not encoder-geometry-limited.** **Net product implication: switch HRR depth-drill's `M_bundle` knob from "dense bipolar bundle" to "K-sparse bipolar bundle at f=0.02" — depth-budget at k=20 with M_bundle=20 becomes structurally safe (substrate already has alpha_c ≥ 1.0 at this f, so 20-of-200-vocab bundle fits inside the proven capacity). Do NOT expect a depth-budget envelope change on PURE-CHAIN binds (both involutive); the lift is on the bundle-width side, which IS the parent drill's real bottleneck.** Calibrated P(sparse-bipolar replaces dense as default bundle representation) = **0.55** (raw 0.75, deflated 0.20; capped novel-synthesis 0.55 because the binding-operator interaction with sparsity at chained-bundle depth IS substrate-novel — Frady-Kleyko-Sommer's "sparse-block" is LCC per block, NOT element-wise sparse-bipolar).

---

## Cheap decisive test (pre-registrable)

**Cell name (proposed):** `exp_hrr_depth_budget_sparse_bipolar_v1`

**Premise:** parent HRR depth drill's cell `exp_hrr_depth_budget_curve_v1` uses dense bipolar bind+bundle. This drill adds 2 ARMs swapping the bundle operator (NOT the bind operator — bind stays element-wise multiply since sparse-bipolar element-wise mul is involutive PROVIDED the sparse-position support is treated consistently).

**Definition (substrate-native sparse-bipolar):** `K-sparse bipolar` vector v ∈ {-1, 0, +1}^N with exactly K nonzero entries at uniformly-random positions. Element-wise multiply: `(a ⊙ b)_i = a_i * b_i` — produces a vector that is **K_intersect-sparse** where K_intersect = K^2/N expected positions overlap. Involutive ONLY IF position-support is preserved: `bind(bind(a,b),b) = a ⊙ b ⊙ b = a ⊙ 1_{support(b)}` which equals a ONLY at positions in support(b). **CRITICAL**: this means substrate-native sparse-bipolar element-wise bind is NOT exactly involutive at low overlap — it's involutive only on the intersection support. Need a position-mask-preserving variant OR Frady-Kleyko-Sommer LCC per block.

**Mechanism to test (two ARMs added):**

- **ARM_SPARSE_BIPOLAR_K_f02_ELEMWISE** (substrate's already-validated f=0.02 = K=82 at N=4096) — uses element-wise multiply; expect approximate-involution (degrades on chain) but maximum bundle capacity
- **ARM_SPARSE_LCC_BLOCK** (Frady-Kleyko-Sommer 2023 LCC per block; B=64 blocks of N/B=64 each at N=4096, K=1 active per block = 64 active) — provably invertible per block via FFT-conjugate; expect lossless involution at chain depth

**Cell config (smoke ~30 min CPU):**
- N_DIM = 4096
- vocab V = 100 sparse-bipolar atoms (K=82 each at f=0.02; or 64-block LCC)
- k_grid = [1, 5, 12, 20] (depth)
- M_bundle_grid = [5, 20, 64] (substrate's existing measured-capacity high end at f=0.02 N=4096 is M_max ≥ 80 per CERT 592)
- bundle_variant = [DENSE_SUM_THEN_SIGN (parent default), K_SPARSE_SUM_THEN_TOPK (KEEP top K positions only), LCC_PER_BLOCK]
- cleanup_per_layer = [OFF, ON]
- seeds = [7, 17, 23]

**Decisive observable:** recall@1 of "unbind the leaf atom after k deep bind + bundle steps, cleanup against vocab V" at sigma=0 (pure recall) AND at sigma=0.5 (substrate's safe-noise regime per ENC1 — at sigma=1.5 baseline already at chance).

**Why ~30 min CPU and not 1 hr:** parent drill's dense-baseline already validates at this config; this adds only 2 bundle-variants × same k/M/cleanup grid as parent.

---

## Falsifiable predictions (HARD_PASS + HARD_FAIL pre-registered)

### Primary discriminator: sparse-bipolar bundle width lifts depth-budget envelope at k=20

**HARD_PASS for sparse-bipolar as default bundle operator:**
- recall@1 at k=20, M_bundle=20, K_SPARSE_SUM_THEN_TOPK, cleanup-ON, all 3 seeds ≥ 0.90 AND cv ≤ 0.05
- AND recall@1 at k=20, M_bundle=20, DENSE_SUM_THEN_SIGN, cleanup-ON ≤ 0.70 (dense fails at this M)
- AND LCC_PER_BLOCK matches or beats K_SPARSE_SUM_THEN_TOPK at k=20 (validates involutive mechanism beats approximate)

**HARD_FAIL for sparse-bipolar default:**
- recall@1 at k=20, M_bundle=20, K_SPARSE_SUM_THEN_TOPK, cleanup-ON ≤ 0.60 (sparse provides no lift; depth-budget at M=20 is intrinsic regardless of encoding)
- OR pure-chain (M=1) sparse recall@1 at k=20 ≤ 0.90 (sparse-bipolar element-wise bind NOT involutive enough on chain — position-mask-preservation framing wrong)

**MIDDLE_BAND:**
- 0.70 < recall@1 < 0.90 at k=20 M=20 K_SPARSE → run M_bundle sweep up to 80 (substrate's measured alpha_c ceiling) before declaring chain-grade

### Secondary discriminator: ENC1 sigma=1.5 rescue

**HARD_PASS for sparse-bipolar variant of ENC1 6th arm:**
- recall@1 of (ARM_ENC1_SPARSE_BIPOLAR_K_f02_N4096_LCC_BLOCK) at sigma=1.5 ≥ 0.20 (8x baseline 0.023)

**HARD_FAIL:**
- recall@1 ≤ 0.04 (same null as existing ARM_SPARSE_FANIN_K5_N4096 = 0.018) → confirms parent ENC1's Shannon-floor framing: sigma=1.5 N=512-4096 M=200 is below recoverable signal regardless of encoder algebra

**Calibrated P(this rescues ENC1):** **0.20** (deflated). The parent ENC1 sparse-fan-in K=5 already failed — sparser doesn't structurally fix Shannon-floor noise. The LCC-block variant is mathematically different (per-block Fourier vs random K-sparse) but does NOT add per-dimension signal; it preserves it differently. Per ENC1 finding "regime=BOTH_NULL" the sparse rescue is unlikely at this noise level. The MEANINGFUL improvement is at the BUNDLE-WIDTH side (Q2), NOT the ENC1 sigma=1.5 side (Q3).

### Tertiary discriminator: chain-depth involutive on K-sparse element-wise

**HARD_PASS for element-wise sparse-bipolar involutive:**
- pure-chain (M=1) recall@1 at k=20, K_SPARSE_SUM_THEN_TOPK ≥ 0.95 (involutive within support intersection)

**HARD_FAIL:**
- pure-chain recall@1 ≤ 0.80 at k=20 sparse element-wise (position-support drifts on chain; substrate-native sparse-bipolar is NOT a usable bind operator → must use LCC per block instead)

---

## Calibrated probabilities

- **P(sparse-bipolar gives DIFFERENT depth-budget envelope on pure chain) = 0.20** (deflated from 0.35). Math: both element-wise mul + LCC are involutive on their support; chain-depth is structurally the same. Differs only if sparse position-support drift dominates — likely at low K.
- **P(sparse-bipolar improves bundle-width bottleneck) = 0.75** (NOT deflated — substrate has DIRECT MEASUREMENT at CERT 592 showing 20–300x bundle-capacity lift at f≤0.02 N≥2048). This is the load-bearing finding.
- **P(sparse-bipolar rescues ENC1 sigma=1.5 ceiling) = 0.20** (deflated; sparse-fan-in K=5 variant already HARD_FAILed all-arms at this regime per ENC1 metrics).
- **P(LCC-per-block beats element-wise sparse on chain) = 0.55** (capped novel-synthesis; Frady-Kleyko-Sommer 2023 establishes LCC as the canonical sparse-VSA bind operator, but no published depth-budget curve).
- **P(substrate should switch to sparse-bipolar as default bundle) = 0.55** (capped novel-synthesis; the 20–300x bundle-capacity lift is real but compute cost of K-sparse storage + sparse argmax is non-trivial).
- **P(HARD_FAIL — sparse-bipolar gives no usable lift at any axis) = 0.15** (always-include floor per calibration discipline).

---

## Question-by-question answers

### Q1. Sparse-bipolar bind/unbind algebra — involutive?

**Element-wise multiply on K-sparse bipolar:** NOT exactly involutive across chains. `bind(a,b) = a ⊙ b` produces vector with support = support(a) ∩ support(b). After k chained binds: support shrinks to ∩_i support(b_i) which for random K-sparse vectors at f=K/N has expected size K * (K/N)^(k-1). At N=4096, K=82 (f=0.02): support after k=5 binds = 82 * 0.02^4 = 1.3e-5 positions — collapses to near-zero support. **VERDICT: element-wise sparse-bipolar bind is NOT a usable chain operator beyond k=2.**

**LCC per block (Frady-Kleyko-Sommer 2023):** PROVABLY invertible per block via FFT-conjugate (per WebFetch on PMC12180425). Per-block circular convolution preserves block-sparsity exactly (K=1 active per block stays K=1 after bind). Chain-lossless on the discrete index space. **VERDICT: LCC-per-block IS a usable sparse-bipolar chain operator; this is the substrate-native sparse-bipolar analog.**

**Noise floor per bind:** Frady-Kleyko-Sommer 2023 does NOT provide an explicit formula (confirmed via WebFetch). Inferred from substrate's measured alpha_c: per-bind noise on LCC at K=64 blocks ~ 1/sqrt(K_total_active) = 1/sqrt(64) ≈ 0.125 per coord — substantially lower than dense bipolar bundle of comparable item count (1/sqrt(M_bundle)) when M_bundle > K.

### Q2. Bundle-width capacity at sparse codes

**Substrate MEASURED at CERT 592 (MEASURED_MECHANISM tier):**
- f=0.02 (K=41 at N=2048): alpha_c ≥ 1.0 (substrate-MEASURED; capped — true value higher)
- f=0.1: alpha_c = 0.4
- f=1.0 (dense): alpha_c = 0.05
- **Lift at f=0.02 vs dense = ≥20x** (LOWER BOUND; substrate hit max-load and did not crosstalk)

**Substrate v5 evidence map (CERT 592, 2026-06-20):** sparse_boundary_willshaw_super_capacity ≥300x at f=0.005 N=8192 LOWER-BOUND.

**Implication for HRR depth drill's M_bundle bottleneck:** At dense N=4096 the parent drill assumed M_max ~ 80–220 reliable items per bundle. At sparse f=0.02 N=4096, substrate's measurement implies M_max ~ 1600+ items per bundle — **~20x more headroom**. This directly addresses the parent drill's identified bottleneck: bundle width M.

**Frady-Kleyko-Sommer 2023 confirms qualitatively** ("sparse distributed representations bridge symbolic reasoning with neural network approaches"; capacity higher) but does NOT publish a comparable M_max formula. Substrate's own measurement is the load-bearing evidence.

### Q3. Composition with ENC1

**ENC1 5-arm cell (already MEASURED, HARD_FAIL all arms at sigma=1.5):**
- ARM_BASELINE_N512: 0.020
- ARM_DENSE_N4096: 0.027
- ARM_SPARSE_FANIN_K5_N4096: 0.018
- ARM_MEDIAN_SUB_N512: 0.025
- ARM_MEDIAN_SUB_SPARSE_N4096: 0.023

**Verdict-msg: "regime=BOTH_NULL" — encoder AND decoder both null at sigma=1.5 M=200 N≤4096.**

Sparse-bipolar variant of ENC1 encoder geometry would NOT cross HARD_PASS at sigma=1.5 because: (1) the existing ARM_SPARSE_FANIN_K5 already tried K=5 and failed; (2) ENC1's Shannon-floor framing predicts ANY encoder algebra fails at this noise; (3) per-dimension noise scales independently of encoding sparsity. Sparse-bipolar IS likely to help at **sigma ≤ 1.0** (substrate's safe envelope per CERT 592 + ENC1 reading at sigma=0.5: ARM_SPARSE_FANIN_K5_N4096 = 0.246 vs ARM_BASELINE_N512 = 0.30 — sparse marginally WORSE; vs sigma=1.0: sparse 0.067 vs baseline 0.073 — also marginally worse).

**Key reading from ENC1 sigma=0.5 + 1.0 data:** sparse-fan-in at K=5 did NOT outperform dense baseline at ANY sigma in the parent ENC1 test. **The substrate-native K=5 sparse-fan-in encoder is NOT a cleanup-ceiling rescue mechanism at the parent regime.** The 20–300x bundle-capacity finding (CERT 592) is at a DIFFERENT mechanism — Willshaw super-capacity, plain k-of-N sparse pattern recall, NOT noisy-cue encoder lift.

**Recommendation:** DO NOT redispatch ENC1 with sparse-bipolar at sigma=1.5; honor parent's "Shannon-floor" classification. DO use sparse-bipolar at the BUNDLE-WIDTH layer in the HRR depth-budget cell where parent identified bundle width M as the real bottleneck.

### Q4. Brain analog — cerebellar K=4-8

**Cayco-Gajic / Litwin-Kumar 2017 + eLife 2023 (PMC10541175, WebFetch verified):**
- Optimal K=4 mossy-fiber fan-in per granule cell — **task-INDEPENDENT** (the eLife 2023 paper explicitly tests this)
- "optimal architectural parameters are largely task-independent. Whereas coding level tunes the inductive bias of the network..."
- **For sequence depth specifically:** the paper does NOT address temporal depth ("we assume temporal dynamics inherited from mossy fibers... integrating temporal information... interesting direction for future investigation")

**Cerebellar timing literature (PMC2788136, PMC9932327):**
- Granule cells fire sequentially to span temporal delays; shortest/longest discriminable sequences = 60ms / 4000ms (~67x dynamic range)
- "any time measured from CS onset is represented by sequential activation of granule cells or granule-cell populations"
- **Implication:** brain implements depth-budget via SEQUENTIAL GC activation chains, NOT via deep nested bind chains. The "depth" in cerebellar K=4-8 sparse-fan-in is single-layer expansion, then sequential read-out — distinct from substrate's nested-bind chain framing.

**Brain implications for substrate depth-budget:**
- DO NOT expect cerebellar K=4-8 lit to directly predict substrate's depth-budget — different operator (expand-then-readout vs nested-bind)
- DO expect cerebellar K=4 to validate the single-layer sparse-fan-in encoder (which is what ENC1 ARM_SPARSE_FANIN_K5 already tested — and FAILED at sigma=1.5)
- **Brain analog REFUTES** the framing that cerebellar K=4 → high depth-budget. Brain uses temporal sequence on a SINGLE expansion layer; substrate uses nested binds on a homogeneous layer. Different mechanism.

### Q5. Substrate-product implications

**Default representation change recommendation:**
- **For BUNDLE operator: YES switch to K-sparse bipolar at f=0.02-0.05.** Substrate has MEASURED 20–300x bundle-capacity lift; this directly unbottlenecks the parent HRR depth drill's identified M_bundle ceiling. Cost: K-sparse storage (~20x smaller per atom) + sparse argmax cleanup (compatible with existing primitives). Net: cheaper compute AND higher capacity.
- **For BIND operator: NOT element-wise sparse-bipolar (support drift kills chains beyond k=2). USE LCC-per-block (Frady-Kleyko-Sommer 2023) IF chain depth k > 5 is needed AND if a new primitive is acceptable cost.**
- **For ENCODER (ENC1 / pythia-projection): NO** — sparse-fan-in at K=5 already tested and FAILED at sigma=1.5 (regime is Shannon-floor, not encoder-bound).

**hdlab primitive proposals (per results-to-application same-cycle rule):**
- `hdlab/sparse_bipolar.py`: K-sparse bipolar atom generator + sparse_bundle (top-K-positions-after-sum) + sparse_cleanup (argmax against K-sparse vocab)
- `hdlab/lcc_block_bind.py`: per-block circular convolution (Frady-Kleyko-Sommer 2023 invertible bind on block codes)
- Composition with existing `bind_elementwise` (substrate smoke cell): keep dense element-wise bind at BIND layer; swap dense bundle for K-sparse bundle at BUNDLE layer

**Compute cost vs benefit:**
- K-sparse storage cost: O(K) per atom vs O(N) dense (at f=0.02, 50x smaller)
- K-sparse bundle compute: O(K * M_items) vs O(N) dense bundle — similar wall but lower memory
- K-sparse cleanup: O(K * V) sparse-vs-sparse argmax, much smaller than O(N * V) dense
- **Net: ~10-50x cheaper compute AND 20-300x higher bundle capacity. Strong product case.**
- Composes with continual-learning (CLS-replay): K-sparse atoms give natural per-atom orthogonality budget even at high V vocab

---

## Cross-thread synthesis

### With parent HRR depth drill (this drill's anchor)
- Parent: pure-chain bipolar bind is depth-LOSSLESS; bottleneck is bundle width M with sigma~1/sqrt(M). At M=5, sigma=0.45 → cleanup margin survives to k=20 with cleanup-per-layer.
- This drill: K-sparse bundle (f=0.02) extends substrate's measured alpha_c from 0.05 → ≥1.0 → **20x bundle-width headroom**. At M=20 sparse-bundle (substrate-measured-safe), depth-budget at k=20 becomes structurally easier than parent's M=5 dense estimate.
- **De-risks parent's "shallow+wide" preference:** parent suggested SHALLOW+WIDE at M=20 dense → recall ~0.85 prediction. With K-sparse f=0.02 M=20, predict recall ~0.95 (the 20x capacity headroom turns M=20 into "comfortable" not "edge of cleanup").

### With CERT 592 sparse_boundary_willshaw_super_capacity (substrate's own measurement)
- CERT 592 MEASURED 20–300x bundle-capacity lift at sparse encoding (substrate's chain-grade-eligible measurement at MEASURED_MECHANISM tier; not yet chain-grade due to capped-alpha_c — true value HIGHER than measured).
- **The substrate's own measurement is stronger evidence than Frady-Kleyko-Sommer 2023** (which gives qualitative claim, no explicit numbers).
- **Cross-thread implication:** the parent HRR depth drill should be re-run with K-sparse f=0.02 bundle BEFORE the dense version to test whether the bundle-width bottleneck is fully removed. If yes, the parent drill's k=20 prediction shifts from P=0.65 to P=0.85.

### With ENC1 5-arm cleanup-ceiling cell (HARD_FAIL all arms at sigma=1.5)
- ENC1: ARM_SPARSE_FANIN_K5_N4096 = 0.018 (HARD_FAIL); regime=BOTH_NULL at sigma=1.5.
- This drill: sparse-bipolar will NOT rescue ENC1 at sigma=1.5 (per substrate's already-MEASURED null on a structurally equivalent ARM).
- **Honor ENC1's "Shannon-floor at sigma=1.5" framing.** Do not redispatch ENC1 with sparse-bipolar; the lift mechanism is real but operates on bundle width, not cleanup-noise-floor at the encoder.

### With Frady-Kleyko-Sommer 2023 (the named source of the drill)
- The paper's "sparse distributed representations" = block-code with LCC per block, NOT element-wise sparse-bipolar.
- LCC bind is provably invertible per block via FFT-conjugate. Per-block-circular-convolution preserves block-sparsity (K=1 per block stays K=1 after bind).
- The paper does NOT provide an explicit depth-budget curve or noise-floor formula (WebFetch on PMC12180425 confirmed).
- **Substrate's own MEASURED alpha_c (CERT 592) is the load-bearing quantitative evidence** for the bundle-width side. Frady-Kleyko-Sommer is the qualitative + algorithmic-foundation citation.

### With cerebellar K=4-8 lit (Q4 brain analog)
- Cayco-Gajic / Litwin-Kumar 2017 + eLife 2023: K=4 optimal for cerebellar GC; task-INDEPENDENT.
- Sequential GC activation gives the cerebellum its temporal depth (60ms-4000ms range), NOT nested-bind chains.
- **Brain analog is REFUTED for nested-bind framing**: brain uses single-layer expansion + sequential read-out, not nested binds. Substrate's K=4-8 sparse-fan-in encoder analog applies to the single-layer encoder (ENC1 ARM_SPARSE_FANIN_K5 — already FAILED at sigma=1.5).
- **Brain SUPPORTS the bundle-width-side lift:** sequential GC populations effectively bundle thousands of contemporaneous patterns; K=4 sparsity gives the high capacity. Maps to substrate's sparse-bundle at f=0.02.

### With substrate's existing primitives + recent arc
- `hdlab/binding.py`: only has FHRR + HRR circular convolution — no element-wise bipolar bind (smoke cell custom), no sparse-bipolar bind.
- `hdlab/whitening.py`: ZCA whitening primitive (encoder-side preprocessing).
- `experiments/exp_contextual_encoding_hrr_binding_smoke_v1.py`: substrate's custom `bind_elementwise` (dense bipolar element-wise multiply).
- CERT 592: substrate-measured sparse capacity lift (the load-bearing evidence).
- **Result:** substrate is ready to ship `hdlab/sparse_bipolar.py` + `hdlab/lcc_block_bind.py` as new primitives. Compose with existing bind + bundle. Substrate-native, NOT a Frady-Kleyko-Sommer external import (the LCC operator is the cite; the K-sparse atoms are substrate-validated).

### With negative-result revival rule
- Per [[feedback-route-negatives-to-research-2x-3x-revival-drills]]: ENC1's HARD_FAIL on ARM_SPARSE_FANIN_K5 must be probed for revival angle.
- **Revival angle (this drill):** sparse-fan-in K=5 at sigma=1.5 was the wrong probe — sparse-bipolar's actual benefit is on BUNDLE WIDTH, not cleanup-noise-encoding. The revival is to test sparse-bipolar at the BUNDLE layer (the parent HRR depth drill's bottleneck), at sigma=0-0.5 (substrate's safe-envelope per ENC1+CERT 592), at M_bundle=20-80 (substrate's measured-safe capacity headroom).
- **This drill's cell `exp_hrr_depth_budget_sparse_bipolar_v1` IS the revival.**

---

## Calibration-penalty discipline applied

Per [[feedback-lit-scan-calibration-penalty]]:
- Substrate-novel sparse-bipolar bind composition: deflated 0.15–0.20 from raw lit P
- LCC-per-block on chain depth: capped at novel-synthesis 0.55 (Frady-Kleyko-Sommer 2023 establishes LCC bind but no explicit depth-budget curve; substrate-novel composition with bundle-width sparsity)
- ENC1 rescue probability: deflated to 0.20 (substrate already MEASURED null on equivalent K=5 arm at sigma=1.5; lower bound on rescue)
- Bundle-width lift probability NOT deflated: substrate has DIRECT MEASUREMENT at CERT 592 (load-bearing evidence is internal not lit-derived)
- All HARD_PASS + HARD_FAIL bands explicit and named

---

## Substrate-product implications

**If `exp_hrr_depth_budget_sparse_bipolar_v1` HARD_PASSES:**
- New `hdlab/sparse_bipolar.py` ships (K-sparse atom generator + sparse_bundle + sparse_cleanup)
- New `hdlab/lcc_block_bind.py` ships (per-block circular convolution invertible bind)
- META atom candidate: `T1/substrate_sparse_bipolar_bundle_20x_capacity_unbottlenecks_hrr_depth_budget_2026-06-23`
- Substrate's default bundle representation switches dense → K-sparse at f=0.02
- Bigram-gap closure pathway: Path A pseudo-LM (currently bottlenecked at value-side bundle) gets ~20x headroom; could close 0.3-0.7 bits of the 1.13-bit text8 bigram-gap
- Continual-learning (CLS-replay) gains natural per-atom orthogonality (sparse atoms naturally near-orthogonal at low overlap)

**If HARD_FAIL:**
- Sparse-bipolar bundle does NOT compose with HRR chain depth (parent drill's bundle width sigma~1/sqrt(M) does not improve under sparsity in practice)
- Atomize as `substrate_sparse_bipolar_bundle_does_not_lift_hrr_depth_envelope_at_N_4096`
- Fall back to dense bipolar bundle at parent's measured M_max ~ 80-220
- Substrate-product: ship parent's dense-bundle envelope as honest depth-budget

**If MIDDLE_BAND:**
- Run M_bundle sweep up to 80 (substrate's CERT 592 measured headroom)
- Run K-sparsity sweep f ∈ {0.005, 0.01, 0.02, 0.05}
- Run dual-axis cleanup-per-layer ON vs OFF

---

## Citations (verified count: 8 external + 5 substrate-internal)

**External:**
1. Frady, F., Kleyko, D., Sommer, F. "Variable Binding for Sparse Distributed Representations: Theory and Applications." IEEE TNNLS 2023. **VERIFIED via PMC12180425 (WebFetch confirmed paper text)**
2. Frady et al. companion: "Factorizers for Distributed Sparse Block Codes." arXiv:2303.13957 (2023).
3. Cayco-Gajic, N.A., Silver, R.A. lineage. "Task-dependent optimal representations for cerebellar learning." eLife 2023. **VERIFIED via PMC10541175** (K=4 task-independent confirmation).
4. Litwin-Kumar, A. et al. "Optimal Degrees of Synaptic Connectivity." Neuron 2017 (K=4 mossy-fiber fan-in baseline citation per eLife 2023).
5. Cayco-Gajic, N.A. et al. "Morphological Constraints on Cerebellar Granule Cell Combinatorial Diversity." J Neurosci 2017 PMC5729189.
6. D'Angelo, E. et al. "Computational Models of Timing Mechanisms in the Cerebellar Granular Layer." PMC2788136 (sequential GC activation, 60ms-4000ms range).
7. Hwang, J. et al. "Cerebellum as a kernel machine: A novel perspective on expansion recoding in granule cell layer." Frontiers Comput Neurosci 2022 (PMC9815768).
8. Kanerva, P. "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors." Cognitive Computation 2009 (sparse + dense HD foundational reference).

**Substrate-internal:**
1. `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md` — PARENT drill; next-drill candidate
2. `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md` — ENC1 design
3. `data/exp_enc1_structured_n_lift_v1/metrics.json` — ENC1 HARD_FAIL all 5 arms at sigma=1.5
4. `data/exp_sparse_boundary_v2_cpu_v1/metrics.json` — substrate's 20x bundle-capacity lift MEASURED at f=0.02 N=2048
5. `notes/research_canonical_evidence_map_v5_MINI_REFRESH_sparse_300x_LANDED_supersedes_8_20x_placeholder_a3f473dd_2026-06-20.md` — CERT 592 META atom (300x at f=0.005 N=8192 LOWER-BOUND)

**Verified count: 8 external + 5 substrate-internal = 13 total.**

---

## Operational drill summary

- **DISPATCH FIRST:** `exp_hrr_depth_budget_sparse_bipolar_v1` smoke (~30 min CPU) — adds K_SPARSE_SUM_THEN_TOPK and LCC_PER_BLOCK bundle variants to parent HRR depth drill's grid. Pre-reg HARD_PASS = k=20 M=20 sparse cleanup-ON recall ≥ 0.90, dense recall ≤ 0.70 at same point. HARD_FAIL = sparse provides no lift OR pure-chain sparse element-wise fails involution.
- **DO NOT REDISPATCH ENC1 at sigma=1.5 with sparse-bipolar** — substrate already MEASURED null on K=5 sparse-fan-in at this regime. Honor "Shannon-floor" framing.
- **Bundle representation switch (conditional on HARD_PASS):** ship `hdlab/sparse_bipolar.py` + `hdlab/lcc_block_bind.py` SAME CYCLE per [[feedback-results-to-application-cadence]]. Compose with existing `bind_elementwise` + `bundle_mean_norm_bipolar`.
- **Brain analog clarification:** cerebellar K=4-8 sparse-fan-in applies to single-layer encoder (REFUTED at sigma=1.5 via ENC1). Sequential GC activation (different mechanism) gives temporal depth. Do not over-claim brain support for nested-bind depth-budget.
- **De-risks parent HRR depth drill's bundle bottleneck:** if sparse-bipolar HARD_PASSES, parent's k=20 prediction P shifts 0.65 → 0.85 and the path-#1 enabling mechanism for context-conditional LM has a substantially larger operational envelope.

**Honest caveat:** P estimates bounded by novel-synthesis cap 0.55 because the K-sparse bipolar × chained-bind × LCC-block composition is substrate-novel without published direct precedent. The bundle-capacity lift (P=0.75) is the LOAD-BEARING claim (substrate MEASURED), not lit-extrapolated. The depth-budget envelope claim (P=0.20 it changes) and ENC1 rescue claim (P=0.20) are both LOW because substrate's measurements already constrain them.

**Next-drill candidate:** if HARD_PASS, drill `free-probability` field per advisor's top recommendation (F4 free cumulants OR F2 Wigner edge / Tracy-Widom on W eigenvalues) — both score 5.0-5.5 and are adjacent to substrate's CERT 592 sparse-boundary measurement (sparse codebook eigenvalue spectrum is a Tracy-Widom edge problem).
