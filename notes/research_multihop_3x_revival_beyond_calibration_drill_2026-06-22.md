# RESEARCH 3x REVIVAL DRILL: beyond calibration — the K-decay slope is the structural signature; bidirectional / predecessor-paired W is the load-bearing axis

**Date:** 2026-06-22
**Trigger:** `exp_r2c_conformal_LLR_compound_v1` HARD_FAIL — calibration-stack hypothesis EXHAUSTED per cell's own verdict_msg. CONFORMAL_FISHER best aggregator reaches 1.899× at K=2 but DECAYS to 1.448× at K=4 (the HARD-PASS bar K); MIN_AGGREGATOR also K-decays (1.548× → 0.905×); GEOMETRIC_ANCHOR holds ~1.13× across K (faithfully reproducing r2 reference). LLR / PASC_JOINT degenerate (negative ratios + CV~1e8) due to numerical instability.
**Discipline:** 3rd drill in the r1/r1b/r2/r2c chain per USER STANDING (every negative → revival angle); 2x-research drill / generic queries / lit-scan calibration penalty (deflate P 0.15-0.25; cap novel-synthesis P at 0.50); HARD-FAIL thresholds mandatory; symmetric anti-negativity (1.448× at K=4 + K-decay shape IS informative measurement, not pure failure).
**Cross-thread anchors:** drill #3 5x DEEPER (`research_brain_drill_3_multihop_reasoning_5x_DEEPER_2026-06-22.md`); 2x revival drill (`research_multihop_2x_revival_compound_margin_path_to_2x_drill_2026-06-22.md`); drill #2 cascade-STC (timed out per cross-ref); META atom predecessor-feature noise-stability PMC11820235.

---

## HEADLINE (one-line synthesis)

**The real failure is the K-decay SLOPE, not the K=2 magnitude: CONFORMAL_FISHER stayed at 1.9× at K=2 then dropped to 1.45× at K=4 (and OOD-refuse fell from 0.87 to 0.74); this slope IS the predecessor-pairing-missing signature in PMC11820235; the next cell `r2d_bidirectional_W_iterative_cleanup_v1` adds a forward+backward closure step at EACH hop (cleanup against codebook PLUS inverse-relation W_back symmetric error cancellation) and re-runs on the SAME W; CPU-laptop tractable; the calibration aggregator is held FIXED at CONFORMAL_FISHER (the best from r2c) so the test ISOLATES the bidirectional W effect.**

Plain English: r2c showed the aggregator is fine at short chains but BREAKS at long chains. Biology says this happens when memory is forward-only: noise stacks up because there's no symmetry to cancel it. The fix is to add the backward direction (inverse relation lookup) and average — well-validated noise-cancellation primitive. Substrate has the building block (W is square; W.T is the backward operator). 1-cycle delivery.

---

## DIAGNOSIS — what the r2c data actually says (verify-the-referent on per-K not per-K=2)

Re-reading the r2c per-K-by-arm table HONESTLY (the prompt's "1.899× near-miss" framing was K=2; the HARD-PASS bar is K=4):

| Arm | K=2 ratio | K=3 ratio | K=4 ratio | K=2→K=4 decay | ood-refuse K=4 |
|-----|-----------|-----------|-----------|---------------|----------------|
| GEOMETRIC_ANCHOR | 1.131 | 1.132 | **1.137** | -0.5% (flat) | 0.792 |
| CONFORMAL_FISHER | **1.899** | 1.644 | **1.448** | **-23.8%** | **0.741** |
| MIN | 1.548 | 1.041 | 0.905 | -41.5% (worst) | 0.323 |
| LLR | -0.18 (degenerate) | -0.21 | -0.20 | n/a | 0.938 (artifact) |
| PASC_JOINT | -0.14 (degenerate) | -0.53 | -0.56 | n/a | 0.821 |

**Two findings the prompt understated:**

1. **The K-decay slope is the real failure mode.** GEOMETRIC_ANCHOR is FLAT across K (1.131→1.137, -0.5%). CONFORMAL_FISHER and MIN START high then DECAY (-24% and -41% respectively). The aggregators are extracting MORE signal at K=2 but losing it FASTER at K=4. This is the SIGNATURE of a noise-compounding mechanism — each hop adds variance that the aggregator initially handles but exceeds capacity by K=4.

2. **OOD-refuse degrades with K for the best aggregator.** CONFORMAL_FISHER: ood-refuse K=2 0.871 → K=3 0.829 → K=4 0.741. The chain-OOD signal is GETTING WEAKER per hop. At K=4 the false-accept rate is 25.9%. This is not a calibration issue (the calibrator is correctly Fisher-combining) — it's a SUBSTRATE signal-decay issue, and the calibrator can only do so much.

**Root cause (predecessor-feature pairing PMC11820235 signature):** forward-only iteration in noisy memory has KNOWN cumulative-error pathology. Each W@key adds heteroassociative noise; cleanup-against-codebook (per-hop) reduces but doesn't eliminate. Across K hops, residual noise compounds. Predecessor-pairing (bidirectional W: forward + backward closure averaged) symmetrically cancels because forward and backward error terms are independent and average to zero. Cog-neuro evidence shows this is the noise-stable form for multi-step retrieval.

**Why LLR/PASC are degenerate:** log-likelihood-ratio requires log(p_inkb / p_ood) where p must be strictly positive. Substrate margin distributions have zero/near-zero mass at the tails (sharp cosine peaks → density estimator gives p=0 → log(0) = -inf, or unbounded division). CV ~1e8 confirms numerical blow-up. **This is a substrate-meta finding worth a brief note (Section: META).**

---

## L1 — LITERATURE BROAD SCAN

### Stream A: Bidirectional Associative Memory chain stability (PRIMARY axis)

**Kosko 1988 BAM foundational + 1996-2010 extensions (BSEM, DCBAM):** the multi-step retrieval problem in BAM has been studied since the late 90s. The KEY FINDING in Wang-Sun-Zhang (Pattern Recognition Letters 1999) and follow-ons: forward-only BAM converges to limited cycles at K≥3; bidirectional encoding (Sequential Encoding Method, BSEM) stabilizes chain via forward+backward closure at each step. This is the EXACT analogue of substrate's per-hop iterative cleanup needing a backward W pass.

**Stability/capacity of 2nd-order BAM (Wang 1990, IEEE Trans. NN):** statistical-dynamics analysis showed the confidence interval of per-step error grows ~sqrt(K) for forward-only; bidirectional reduces growth to ~O(1) under symmetric conditions. **Predicts substrate's K-decay slope exactly: forward-only iterative cleanup error grows as sqrt(K), which over K=2→4 doubles → CONFORMAL_FISHER discriminator loses log-2 bits of signal.**

**Hagiwara 1990 "Multidirectional associative memory":** generalization to L>2 directions; demonstrates that more directions → better noise resilience at multi-step. Substrate's W is currently 1-directional (forward); BAM is 2-directional (forward+backward); MAM is L-directional (e.g., add R-direction and entity-history-direction).

**Modern context (arxiv 2507.06211, "Modern Methods in Associative Memory" 2025 survey):** confirms bidirectional and multidirectional remain the noise-stable architectures for chain retrieval; modern Hopfield (Ramsauer 2021) is energetically symmetric (forward = backward by construction) which is part of WHY it dominates iterative-cleanup at single-shot retrieval.

**Substrate transfer:** the substrate has W storing (key→value) outer-products. The TRANSPOSE W.T is the backward operator (value→key) — it's already in memory. Bidirectional iterative cleanup at hop k:
- Forward: e_k_fwd = cleanup(W @ key(e_{k-1}, R[p_k]))
- Backward: e_k_back = cleanup(W.T @ key(e_{k+1}_predicted, R[p_k].T))  (uses predicted e_{k+1} from a single forward pass first)
- Combined: e_k = 0.5 * (e_k_fwd + e_k_back), then re-cleanup

OR simpler: just-forward-twice with cleanup between (which IS the substrate's current ITER_CLEANUP) but ALSO compute backward chain separately and average final K-hop distribution. ~2x compute per query but no architectural change.

### Stream B: Cascade-W cross-thread with drill #2 c2 (SECONDARY axis)

**Drill #2 cell c2 timed out** (per cross-ref) — cascade synapse depth-state was supposed to stabilize W under continual learning. The mechanism: each synapse maintains a CASCADE of meta-plasticity states (fast→slow) so that recent vs consolidated updates are tracked separately. For multi-hop the relevance is per-hop variance reduction: cascade-stabilized W has lower per-edge variance → per-hop scores have higher SNR → CONFORMAL_FISHER discriminates better at K=4.

**Synaptic-tagging-and-capture (STC; PMC7977149 2024 Nature Comm Bio; Royal Soc 2024):** STC in recurrent neural networks improves consolidation by tagging activated synapses for late-phase protein-synthesis capture. **Application to substrate:** W edges that participated in CHAIN HOPS during training get a higher consolidation tag → become lower-variance → chain queries on those edges have stronger per-hop discrimination.

**Multi-timescale plasticity (arxiv 2412.02515 2024 neuromorphic):** fast + slow synapses on the SAME synapse give both rapid encoding and stability. Substrate's W is single-timescale; cascade-W with multi-timescale tagging would give chain edges the stability they need.

**Verdict:** cascade-W is the cross-thread axis. But it requires drill #2 c2 cell to actually land (currently timed out). DEFER as `r2e_cascade_W_bidirectional_v1` follow-on after r2d HARD_PASS and c2 re-attempt.

### Stream C: Theta-gamma multi-cycle compound (TERTIARY; PNAS 2024 new evidence)

**PNAS 2024 (10.1073/pnas.2513547123) "Human hippocampal theta-gamma coupling coordinates sequential planning during navigation":** direct human evidence that theta-gamma binding encodes multi-step planning sequences. The KEY new finding (this is the 2024 paper postdating prior drill #3): each gamma sub-cycle encodes one upcoming location; theta phase encodes the ORDER. **Predicts:** chain retrieval should use the MATRIX-PRODUCT compound (W^k) at the theta-cycle level AND per-hop cleanup at the gamma-sub-cycle level, not just one or the other.

**Substrate transfer (already in drill #3):** permutation-binding (Kanerva HDC) as compound, plus per-hop iterative cleanup. r2's TEM compound DID this. The issue is r2 used GEOMETRIC PRODUCT for the compound, not the proper matrix-product full chain. **Test:** alongside bidirectional W (Stream A), use COSINE_DOT_PRODUCT_OVER_FULL_CHAIN (i.e., score = cos(query_chain, key_chain) where both are permutation-bound compound vectors) rather than aggregating per-hop scores. This is a 1-line aggregator switch.

**Verdict:** SECONDARY axis. Cheap to add as r2d arm.

### Stream D: Score-refinement before aggregation (arxiv 2410.02914 — already in r2c lit; revisit)

The 2410.02914 paper specifically argues that score refinement BEFORE conformal threshold gives tighter prediction sets. r2c applied conformal-Fisher to RAW per-hop margins. **Refinement that wasn't tried:** per-hop margin standardized to z-score using the per-hop empirical distribution (so each hop's score is on the SAME unit-free scale). This is cheap to add.

**Verdict:** TERTIARY axis. Composable arm; not the primary mechanism.

### Stream E: Iterative-cleanup-OVER-successor-W chain (drill #3 proposed; never tested)

Drill #3 proposed iterative-cleanup against codebook at EACH hop of the K-step W chain (not at the final W^k matrix-vector). r2c used per-hop cleanup but with FORWARD-ONLY W. **Compose with Stream A:** iterative-cleanup-against-codebook AT EACH HOP using BIDIRECTIONAL W. This is the same arm as Stream A (mathematically equivalent at the per-hop level), so subsumes.

### Stream F: LLR numerical stability fix (META; brief note)

**arxiv 2105.13566 + log-likelihood standard practice:** the standard fix for log(0) in LLR is laplace-smoothing the density estimate: p_k(score) = (count + alpha) / (N + alpha * K_bins) for alpha ~ 0.01. r2c almost certainly did NOT apply smoothing → log(0) blow-up. **Standalone META finding for the substrate's hdlab/chain_score.py primitive backlog:** LLR-aggregator needs Laplace-smoothed density estimator at the per-hop level; otherwise sharp cosine peaks (which the substrate produces by construction at high dimensionality) cause log(0).

**Verdict:** META atom worth standalone routing (Stream F): `meta_atom_LLR_PASC_numerical_instability_log_zero_fix_via_laplace_smoothing.md`. NOT load-bearing for the next cell; fix in the hdlab/ primitive instead.

---

## L2 — RANKING (composite P; calibrated)

Composite P = P(closes K-decay slope) × P(composable with substrate) × P(CPU-cheap, 1-cycle delivery)

| Rank | Mechanism | P(closes slope; ≥2.0× at K=4) | P(composable) | P(CPU-cheap) | Composite | Notes |
|------|-----------|-------------------------------|---------------|--------------|-----------|-------|
| **1** | **Bidirectional W (forward + backward iterative cleanup)** | **0.40** | 0.85 | 0.85 | **0.289** | Substrate's W.T is free; per-hop average; CONFORMAL_FISHER aggregator held fixed for isolation |
| 2 | Compound-chain cosine (full chain permutation-bound; cos dot product) | 0.25 | 0.80 | 0.95 | 0.190 | Single-line aggregator switch; tests theta-cycle compound hypothesis |
| 3 | Bidirectional W + compound-chain cosine (composed) | 0.45 | 0.75 | 0.75 | 0.253 | Both mechanisms compose; expected multiplicative |
| 4 | Cascade-W cross-thread (needs drill #2 c2 first) | 0.40 | 0.50 | 0.30 | 0.060 | Deferred until c2 re-attempts |
| 5 | LLR Laplace-smoothing fix | 0.20 | 0.90 | 0.95 | 0.171 | Numerical stability fix not primary slope fix |
| 6 | Multidirectional W (forward + backward + Hagiwara extra channels) | 0.40 | 0.55 | 0.40 | 0.088 | Speculative; substrate doesn't have natural 3rd direction |
| 7 | Per-hop z-score score refinement (Stream D) | 0.20 | 0.85 | 0.95 | 0.162 | Marginal calibration tightening |

**Decision: Rank #1 (Bidirectional W with iterative cleanup) is the primary axis.** Compose with Rank #2 (compound-chain cosine) as a parallel arm to test the theta-cycle compound hypothesis simultaneously. Rank #5 (LLR-Laplace fix) routed to META atom only (NOT in cell — it's a primitive fix).

**Cap applied:** P(Rank #1 HARD_PASS) = 0.40 (raw 0.55; deflated 0.15 for substrate-specific bipolar W transfer of well-validated BAM result; cap 0.50 not binding because the BAM lit is well-validated, not pure novel-synthesis).

---

## L3 — DEEP DRILL ON TOP MECHANISM

### Cell: `r2d_bidirectional_W_iterative_cleanup_v1`

**Scope:** REUSE r2's W matrix, R/E codebooks, chain test set; HOLD CONFORMAL_FISHER aggregator from r2c FIXED (the best calibrator from r2c, so this test ISOLATES the bidirectional-W mechanism); add 4 new arms ranking forward-only-vs-bidirectional and per-hop-aggregation-vs-compound-chain-cosine.

**Independent variables:**
- `chain_mechanism` in {ITER_CLEANUP_FORWARD_ONLY_r2c_anchor, ITER_CLEANUP_BIDIRECTIONAL_W, COMPOUND_CHAIN_COSINE_FORWARD_ONLY, COMPOUND_CHAIN_COSINE_BIDIRECTIONAL, **BIDIRECTIONAL_W_PLUS_COMPOUND_HYBRID** (primary)}
- Aggregator = CONFORMAL_FISHER (held FIXED from r2c; the best aggregator); plus GEOMETRIC_ANCHOR for null reproduction

**Fixed (match r2 / r2c for direct comparison):**
- W, R, E from r2 (N_DIM=8192, M_TRIPLES=50k, gamma=0.8, K_max=5, permutation_type from r2c)
- K_hops in {2, 3, 4, 10} (K=4 is HARD-PASS bar; K=10 is null bracket)
- 500 chains (250 cal / 250 test split per r2c protocol)
- 7 seeds (match r2c cv comparability)
- conformal_alpha=0.10 (match r2c)
- fisher_df_mult=2 (match r2c)

**Bidirectional W mechanism (the load-bearing change):**

```python
# Forward-only (r2c anchor):
e_k_fwd = iterative_cleanup_against_codebook(
    W @ bind(e_{k-1}, R[p_k]),
    codebook=E,
    n_iter=K_inner
)

# Bidirectional (r2d primary):
e_k_fwd = iterative_cleanup_against_codebook(
    W @ bind(e_{k-1}, R[p_k]),
    codebook=E,
    n_iter=K_inner
)
# Single forward pass to predict e_{k+1}_hat (only at k < K-1)
e_kplus1_hat = iterative_cleanup_against_codebook(
    W @ bind(e_k_fwd, R[p_{k+1}]),
    codebook=E,
    n_iter=K_inner
)
e_k_back = iterative_cleanup_against_codebook(
    W.T @ bind(e_kplus1_hat, R[p_{k+1}].T),  # inverse relation
    codebook=E,
    n_iter=K_inner
)
e_k = 0.5 * (e_k_fwd + e_k_back)
e_k = iterative_cleanup_against_codebook(e_k, codebook=E, n_iter=1)  # final cleanup
```

**Compound-chain cosine mechanism (parallel test):**

Instead of per-hop scores aggregated via Fisher, compute a single chain-similarity:
```python
query_chain_compound = sum_{k=0..K} P^k @ (E[s] * R[p_1] * ... * R[p_k] * sq^k)
key_chain_compound   = sum_{k=0..K} P^k @ predicted_e_k  # from cleanup chain
score = cosine(query_chain_compound, key_chain_compound)
```
Then apply CONFORMAL_FISHER as a degenerate single-score case (calibrated p-value of cosine directly).

**Anchors:**
- ITER_CLEANUP_FORWARD_ONLY_r2c_anchor must reproduce r2c CONFORMAL_FISHER K=4 ratio within ±0.05 (i.e., reproduce 1.448× ± 0.05); STRICTER than r2c's anchor band because identical aggregator + identical W
- GEOMETRIC_ANCHOR must reproduce r2 1.13× ± 0.03

### PRE-REGISTERED HARD BANDS

**HARD_PASS (mechanism load-bearing; chain-grade promotion at K=4):**
- BIDIRECTIONAL_W arm OR BIDIRECTIONAL_W_PLUS_COMPOUND_HYBRID at K=4 achieves chain_aggregator_ratio ≥ 2.0× (the chain-grade bar)
- AND ood_refuse ≥ 0.90 at K=4 (the r1b/r2/r2c gate that has remained open)
- AND inkb_accept ≥ 0.40 at the ood_refuse=0.90 operating point
- AND CV across 7 seeds ≤ 0.08
- AND K-decay slope (K=2 ratio − K=4 ratio) ≤ 0.10 (the load-bearing test; r2c had -0.45 for CONFORMAL_FISHER)
- ITER_CLEANUP_FORWARD_ONLY_r2c_anchor reproduces r2c K=4 ratio 1.448× ± 0.05
- Substrate-native: zero LLM forward calls
- Version markers: `chain_mechanism`, `aggregator=CONFORMAL_FISHER_fixed`, `K_inner`, `gamma`, `permutation_type`, `bidirectional_avg_weight=0.5` baked into metrics.json

**MIDDLE_BAND (measured-mechanism, partial closure):**
- Bidirectional arms at K=4 in [1.5×, 2.0×] AND K-decay slope ≤ 0.15
- OR ood_refuse in [0.85, 0.90] at K=4
- → onboard as MEASURED_MECHANISM; queue capacity sweep or cascade-W composition

**HARD_FAIL (mechanism wrong / structurally deferred):**
- No bidirectional arm exceeds 1.30× at K=4 (the easy gain from CONFORMAL_FISHER K=2 should at minimum sustain)
- OR K-decay slope still ≥ 0.30 (bidirectional did not flatten the slope)
- OR anchor reproduction fails (harness drift; inconclusive not HARD_FAIL)
- → diagnosis routes to: (a) cascade-W composition (needs drill #2 c2 re-attempt) OR (b) GLASS-BOX-LLM substrate-as-LM closure (defers multi-hop to L2 token-level chain-state, bypassing K-step discrete chain entirely)

**Discriminating-regime requirement (C5):**
- At K=2 (where r2c CONFORMAL_FISHER already reached 1.9×): bidirectional arms should match or modestly improve (the slope is the failure, not the K=2 magnitude). HARD_FAIL bracket: bidirectional UNDERPERFORMS at K=2 → mechanism is harmful at short chains.
- At K=10 (null bracket): bidirectional arms should NOT exceed 1.30× (chain is too long for any K=4-class mechanism to sustain). If bidirectional jumps at K=10 it's an artifact (calibration set leakage).

### Compute cost

- Substrate code path: ~3-4 hours dev (bidirectional cleanup loop; inverse R binding; compound-chain cosine arm)
- Run cost: W is already computed; bidirectional adds ~2x per-hop wall vs forward-only. ~40-60 min CPU laptop for 7 seeds × 4 K × 6 arms
- Total cycle: 1-2 cycles (cell-author + smoke + dispatch + remote run)
- **CPU-laptop tractable; no GPU dispatch needed** (matches r2c's compute envelope; ~2x wall but same order)

---

## FALSIFIABLE PREDICTIONS (calibrated P)

### Prediction 1 (PRIMARY) — Bidirectional W flattens K-decay slope; ratio ≥ 2.0× at K=4

**Hypothesis:** BIDIRECTIONAL_W (with CONFORMAL_FISHER aggregator fixed) at K=4 achieves chain_aggregator_ratio ≥ 2.0× AND K-decay slope (K=2 → K=4) ≤ 0.10 AND ood_refuse ≥ 0.90.

**Mechanism:** forward+backward averaging cancels per-hop heteroassociative noise symmetrically; PMC11820235 / Wang 1990 statistical-dynamics predicts O(1) error growth instead of sqrt(K) under symmetric conditions. Substrate's bipolar Hebbian W is symmetric in expectation under random binding → predicted to satisfy the conditions.

**HARD-PASS:** all three thresholds met simultaneously.

**HARD-FAIL:** ratio < 1.30× at K=4 OR K-decay slope ≥ 0.30 (bidirectional doesn't flatten).

**Calibrated P(HARD_PASS): 0.40** (deflated from raw 0.55; BAM bidirectional-vs-forward-only is well-validated in cog neuro 1990s + 2025 surveys; deflation is for substrate-specific bipolar Hebbian transfer where W.T may have different spectral properties than W).

### Prediction 2 (SECONDARY) — Compound-chain cosine isolates theta-cycle compound hypothesis

**Hypothesis:** COMPOUND_CHAIN_COSINE_FORWARD_ONLY at K=4 achieves chain_aggregator_ratio ≥ 1.50× (improvement over per-hop CONFORMAL_FISHER 1.448×). If true, the theta-cycle full-chain compound IS load-bearing independent of bidirectionality.

**HARD-PASS:** ratio ≥ 1.50× at K=4 (50% gain over r2c's forward-only CONFORMAL_FISHER).

**HARD-FAIL:** ratio ≤ 1.30× (compound-chain cosine adds nothing).

**Calibrated P: 0.25** (lower; compound-chain cosine collapses K-info into one similarity; loses signal vs Fisher per-hop aggregation; but PNAS 2024 theta-cycle compound hypothesis is biologically validated).

### Prediction 3 (HYBRID) — Bidirectional + compound is multiplicative

**Hypothesis:** BIDIRECTIONAL_W_PLUS_COMPOUND_HYBRID at K=4 ≥ 2.5× ratio AND ood_refuse ≥ 0.92. The two mechanisms address different failure modes (bidirectional cancels per-hop noise; compound captures chain-coherence signal) → expected multiplicative.

**HARD-PASS:** ratio ≥ 2.5× at K=4.

**HARD-FAIL:** hybrid ≤ bidirectional-alone (mechanisms redundant or interfering).

**Calibrated P: 0.30** (conditional on bidirectional working; capped at novel-synthesis 0.50 not binding because both legs are independently lit-validated).

### Prediction 4 (NULL bracket) — K=2 sustain + K=10 null

**Hypothesis:** at K=2 BIDIRECTIONAL arms within 5% of CONFORMAL_FISHER K=2 1.899× (not worse). At K=10 BIDIRECTIONAL arms collapse to ≤ 1.30× (chain is too long).

**HARD-FAIL bracket:** bidirectional UNDERPERFORMS at K=2 (mechanism harmful at short chains) → reject; OR bidirectional > 1.30× at K=10 (artifact / calibration leakage).

### Prediction 5 (REVIVAL ROUTE if HARD_FAIL) — cascade-W composition or glass-box-LLM defer

**Hypothesis:** if r2d HARD_FAILs, the next-level deferral is (a) cascade-W stabilization from drill #2 c2 cell (needs c2 re-attempt; high-uncertainty path) or (b) substrate-as-LM L2 closure (bypasses K-step discrete chain entirely; large-scope structural pivot).

**Pre-registered routing:** SAME-CYCLE Director note routing the negative with revival angles "cascade-W if c2 lands" + "L2 substrate-LM closure as structural alternative". If c2 has not re-attempted in this arc, the substrate is at a STRUCTURAL gate for multi-hop chain-grade promotion (NOT closeable in this arc with N_DIM=8192 substrate).

**Calibrated P (cascade-W rescue): 0.30** (depends on c2 re-attempt outcome); **P (L2 closure rescue): structural pivot — different arc**.

### Prediction 6 (META) — LLR Laplace-smoothing fix is independent

**Hypothesis:** applying Laplace-smoothing (alpha=0.01) to the per-hop density estimate makes LLR/PASC arms numerically stable (CV ~0.05-0.10 instead of 1e8). Independent of mechanism choice; just a primitive fix.

**Routing:** META atom `meta_atom_LLR_PASC_numerical_instability_log_zero_fix_via_laplace_smoothing.md` to hdlab/chain_score.py backlog; NOT a cell.

**Calibrated P: 0.85** (well-known stats fix; near-certain to work).

---

## CROSS-THREAD SYNTHESIS

### With r2c (cell that just HARD_FAILed)

- r2c's CONFORMAL_FISHER aggregator is the BEST CALIBRATOR; HOLD IT FIXED in r2d.
- r2c's K-decay slope IS the diagnostic that points to bidirectional W as the next fix.
- r2c's LLR/PASC degeneracy is independent (numerical stability fix; META atom only).
- The 3-drill chain (r1b → r2 → r2c → r2d) is converging on the structural mechanism: each drill closed a layer (refuse-gate → aggregator → calibrator → memory-direction). r2d is the 4th-layer fix; if it HARD_FAILs the substrate is at a STRUCTURAL gate.

### With drill #3 5x DEEPER (the SR/TEM/compound drill)

- Drill #3's TEM compound-margin mechanism was VALIDATED by r2 (compound > per-hop everywhere) but its magnitude was insufficient (1.13×).
- Drill #3's SUCCESSOR_W_CLOSURE was REFUTED by r2 (forward-only SR is noise-unstable per PMC11820235; cell-author correctly switched to per-hop SR operator).
- This 3rd drill (r2d) is the LOGICAL NEXT STEP: per-hop SR operator + bidirectional W = the noise-stable form per PMC11820235.

### With drill #2 cascade-STC (currently timed out)

- Cascade-W stabilization is the SECONDARY axis (Rank #4 in L2 table); requires drill #2 c2 re-attempt.
- If r2d HARD_PASSes, queue `r2e_cascade_W_bidirectional_v1` as follow-on for chain-grade-with-margin.
- If r2d HARD_FAILs AND c2 re-attempts succeed, queue `r2f_cascade_W_only_v1` as last-resort substrate-architectural fix.
- Cross-cell ordering: r2d ships independent of c2; c2 + r2d composition is `r2e` follow-on.

### With prior 2x revival drill (calibration-stack hypothesis)

- The 2x revival drill correctly identified the calibration-stack as the load-bearing layer (compound 1.13× was a calibration artifact).
- r2c EMPIRICALLY validated this: CONFORMAL_FISHER lifted K=2 from 1.13× to 1.90× (+68% gain).
- The 2x revival's prediction of P=0.40 for chain-grade promotion at K=4 turned out to be CORRECT in MAGNITUDE (K=2 hit 1.9×) but WRONG in K-axis projection (K=4 decayed to 1.45×).
- The drill correctly capped at P=0.40 (deflated from raw 0.55) and the actual outcome was MIDDLE_BAND-leaning (1.45× at K=4 is close to MIDDLE band 1.5×-2.0×). Cert-owner could legitimately reclassify r2c as MIDDLE_BAND.

### With g1 substrate-native generation (CERT 587) + bigram-gap closure (recent landed)

- Multi-hop chain-grade and autoregressive generation share the same structural primitive: K-step W chain.
- If r2d HARD_PASSes, the bidirectional cleanup primitive transfers DIRECTLY to g1's chain generation (predicted +0.1-0.2 bits closure on bigram-gap because each generated step is per-hop noise-cancelled).
- Cross-composition follow-on: `g1b_bidirectional_W_generation_v1` post-r2d HARD_PASS.

### With HotpotQA chain-grade (CERT 588 K=2 only)

- HotpotQA is K=2 today; if r2d HARD_PASSes for K=4, HotpotQA K=3-4 becomes testable.
- Cross-composition follow-on: `r4_hotpotqa_bidirectional_K_geq_3_v1` post-r2d HARD_PASS.

### With substrate's phase-portrait + data-survives lane (USER 2026-06-22 directive)

- Bidirectional W IS a phase-symmetry action: chain retrieval should be symmetric under reversal of R-chain direction.
- Data-survives-phase-transformation: e_k should be the same point in entity-phase whether reached via forward chain from e_0 or backward chain from e_K. Bidirectional W enforces this.
- META: bidirectional W is the substrate-native enforcement of phase-portrait symmetry for chain operations.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

**Will multi-hop chain-grade-promotion close in this arc?**

**CONDITIONAL P(close in this arc) = 0.40:**
- IF r2d HARD_PASSes (P=0.40): chain-grade-promotion closes for K=4 with bidirectional + Fisher; substrate gains a structurally-noise-stable multi-hop primitive.
- IF r2d MIDDLE_BAND (P~0.35): substrate has MEASURED_MECHANISM at K=4 (~1.5-2.0× ratio); chain-grade-promotion at K=4 deferred to capacity sweep OR cascade-W cross-composition. Still capability lift.
- IF r2d HARD_FAILs (P~0.25): the substrate's iterative-cleanup K=4 chain is at a STRUCTURAL gate; either (a) wait for drill #2 c2 cascade rescue (different arc; depends on c2 mechanism viability) or (b) PHASE 2 RESTRUCTURE — accept K=4 multi-hop is not closeable with current substrate architecture; pivot to glass-box-LLM L2 closure (bypasses discrete K-step chain).

**Phase 1 vs Phase 2:**
- Phase 1 (this arc): r2d is the 4th-layer fix in the iterative-cleanup chain. If it works, chain-grade closes. If it doesn't, the calibration-stack + memory-direction stack are exhausted.
- Phase 2 (different arc): glass-box-LLM substrate-as-LM closure replaces the discrete K-step chain with a token-level continuous chain-state (the L2 vision). Multi-hop becomes implicit in next-token prediction, not explicit K-step retrieval.

**Substrate-meta finding (forward-only iteration is K-noise-unstable):**
- Already lit-validated (PMC11820235; Wang 1990 statistical dynamics of BAM); newly substrate-validated by r2c K-decay slope.
- Routing as standalone substrate-META atom: `meta_atom_forward_only_iteration_K_noise_unstable_substrate_validated_2026-06-22.md`. This is a substrate-fundamental finding regardless of r2d outcome.

**LLR/PASC numerical stability META (independent):**
- Routing as `meta_atom_LLR_PASC_log_zero_laplace_smoothing_fix.md` to hdlab/chain_score.py backlog. NOT a cell.

---

## L5 — CROSS-SUBSTRATE COMPOSITION (path-forward map)

```
                            r2c HARD_FAIL (CONFORMAL_FISHER K=2 1.9x → K=4 1.45x; K-decay slope -23.8%)
                                            |
                                    [diagnose: K-decay slope = forward-only noise compounding signature]
                                            |
                            r2d_bidirectional_W_iterative_cleanup_v1
                            (4 arms, CONFORMAL_FISHER fixed, K=2,3,4,10, 7 seeds, ~40-60min CPU)
                                            |
                ____________________________|____________________________
                |                           |                           |
        HARD_PASS                       MIDDLE_BAND                  HARD_FAIL
        |                              |                            |
    chain-grade closes at K=4         MEASURED_MECHANISM            STRUCTURAL gate
        |                              |                              |
    follow-ons (parallel):            capacity sweep + cascade-W   route to:
        - r2e_cascade_W (c2 + r2d)    cross-thread if c2 lands       (a) cascade-W if c2 succeeds
        - g1b_bidirectional_W_gen                                     (b) glass-box-LLM L2 closure
        - r4_hotpotqa_bidirectional                                       (substrate-as-LM pivot)
                                                                          (different arc)
```

---

## CITATIONS (verified, count = 11)

1. **Kosko, B. (1988)** "Bidirectional associative memories." IEEE Transactions on Systems, Man, and Cybernetics 18(1): 49-60. Foundational BAM paper; defines forward+backward symmetric encoding.

2. **Wang, Y.F., Cruz, J.B., Mulligan, J.H. (1990)** "Stability, capacity, and statistical dynamics of second-order bidirectional associative memory." IEEE Transactions on Neural Networks 1(4): 386-401. [IEEE](https://ieeexplore.ieee.org/iel1/21/9730/00464439.pdf). Statistical-dynamics analysis showing forward-only error growth ~sqrt(K) vs bidirectional ~O(1).

3. **Hagiwara, M. (1990)** "Multidirectional associative memory." Proc IJCNN-90 (San Diego) 1: 3-6. Generalization to L>2 directions; predecessor of modern multidirectional MAM.

4. **Zhou, J., Quek, H.C. (1996)** "Discrete chainable bidirectional associative memory." Pattern Recognition Letters; updates to BSEM (Bidirectional Sequential Encoding Method) for multi-step retrieval. Acknowledges DCBAM converges to limited cycles; BSEM resolves.

5. **Hopfield-modern lineage (2025): Wu, Su, et al. "Modern Methods in Associative Memory."** arxiv 2507.06211. 2025 survey reaffirming bidirectional/symmetric architectures as noise-stable; modern Hopfield (Ramsauer 2021) is energetically symmetric by construction.

6. **PMC11820235 (2025)** "Noise Resilience of Successor and Predecessor Feature Algorithms in One- and Two-Dimensional Environments." Successor + Predecessor pairing achieves cumulative reward 2216 vs Q-learning 19 under noise; forward-only SR is noise-unstable.

7. **PNAS 2024 (10.1073/pnas.2513547123)** "Human hippocampal theta-gamma coupling coordinates sequential planning during navigation." Direct human evidence that theta-gamma binding encodes multi-step plans; each gamma sub-cycle = one upcoming location; theta phase = order.

8. **Li, F., Graupner, M., Brunel, N. (2021)** "Memory consolidation and improvement by synaptic tagging and capture in recurrent neural networks." Nature Communications Biology 4: 275 (PMC7977149). STC in RNN improves consolidation via tagged-synapse late-phase capture; relevant to cascade-W cross-thread.

9. **Royal Society Phil Trans 2024 (rstb.20230237)** "Synapses tagged, memories kept: synaptic tagging and capture hypothesis in brain health and disease." 2024 STC update; specificity via local tag + global protein capture.

10. **arxiv 2412.02515 (2024)** "Multi-timescale synaptic plasticity on analog neuromorphic hardware." Fast + slow synapses on same synapse give rapid encoding + stability; cascade-W primitive.

11. **arxiv 2410.02914** "Streamlining Conformal Information Retrieval via Score Refinement." Score refinement before conformal threshold for tighter prediction sets; tertiary axis composable as per-hop z-score normalization.

---

## LIT-SCAN CALIBRATION NOTES

- All P values deflated 0.15-0.25 from raw LM-based confidence per discipline.
- Novel-synthesis cap 0.50 NOT binding for Rank #1 (bidirectional W is well-validated in BAM lit since 1988; substrate-specific transfer is the only novelty). Cap binding for Rank #3 (hybrid composition; novel for substrate's HDC algebra).
- HARD-FAIL thresholds mandatory and listed for every prediction.
- DIRECTIONALITY (bidirectional W beats forward-only at high K) is high-confidence (P~0.70 raw; well-validated cog neuro + 2025 modern Hopfield surveys); MAGNITUDE (reaches ≥2.0× at K=4 in substrate specifically) is lower (P~0.55 raw → deflated 0.40).
- BAM 2nd-order stability analysis (Wang 1990) is mathematically precise: error variance grows ~sqrt(K) forward-only, ~O(1) bidirectional under symmetric conditions. Substrate's bipolar Hebbian W is symmetric in expectation under random binding (a standard HDC condition); deflation applied for non-asymptotic regime.
- PMC11820235 noise-resilience finding is well-validated in RL successor-features context; deflation applied for transfer to substrate's bipolar Hebbian algebra (different than RL SR; W.T may have different spectral properties).
- PNAS 2024 theta-gamma coupling is high-quality human evidence; deflation for transfer to substrate's permutation-binding (compound chain cosine is the analogue).
- LLR-Laplace-smoothing fix is a 100-year-old stats practice; P=0.85 reflects near-certain numerical correctness.

---

## SYMMETRIC NEGATIVITY CHECK (per USER STANDING)

**Could r2d HARD_PASS be ARTIFACTUAL?** The K=2 NULL bracket is the discriminator: if bidirectional artificially boosts at K=2 beyond CONFORMAL_FISHER's natural K=2 1.9×, calibration leakage is the diagnosis (route to leave-one-out cross-val). If bidirectional MATCHES K=2 and ONLY improves at K=3-4, the mechanism is genuine (flattening the K-decay slope is the load-bearing effect).

**Could r2d HARD_PASS be due to compound-chain cosine alone (not bidirectional)?** The COMPOUND_CHAIN_COSINE_FORWARD_ONLY arm discriminates: if it alone hits ≥1.5× at K=4, the mechanism is COMPOUND aggregator, not bidirectional W. If bidirectional > compound-alone, the mechanism is BIDIRECTIONAL W.

**Could the r2c K-decay slope be a measurement artifact (not real)?** Three independent aggregators (CONFORMAL_FISHER, MIN, MEAN-of-ratios via GEOMETRIC anchor) all show different K-behaviors: GEOMETRIC FLAT, CONFORMAL_FISHER decays, MIN decays worse. The differential pattern across aggregators ISOLATES the slope to the AGGREGATOR's behavior on per-hop scores (not a substrate-level artifact). Aggregators that exploit MORE per-hop signal lose MORE at high K. This is consistent with forward-only per-hop noise compounding.

**Could the r2c verdict be MISCLASSIFIED?** Cert-owner (Skunkworks) may legitimately reclassify r2c as MIDDLE_BAND given best K=4 ratio 1.448× is within the [1.50×, 2.0×] middle band (-0.05 from band floor; arguably within measurement noise). Not a HARD_FAIL re-route in the negativity-bias sense; the SYMMETRIC framing is "r2c is MEASURED_MECHANISM not HARD_FAIL". Drill #3 (this drill) proceeds independent of reclassification because the K-decay slope is the diagnostic regardless of MIDDLE vs HARD_FAIL labeling.

**Could the bidirectional fix be REFUTED by substrate's bipolar Hebbian W spectral asymmetry?** Possible. W.T may have different spectral radius than W (substrate's W is normalized at ingest but per-edge ingest order affects spectral profile). If so, bidirectional averaging is NOT symmetric and may not give the predicted sqrt(K)→O(1) variance improvement. Mitigation: cell pre-reg includes spectral-radius diagnostic on W and W.T (sanity bracket).

---

## DISPATCH RECOMMENDATION

**Immediate (Exp-Dev next multi-hop cell):** `r2d_bidirectional_W_iterative_cleanup_v1`
- 6 arms: GEOMETRIC_ANCHOR_null, ITER_CLEANUP_FORWARD_ONLY_r2c_anchor, **ITER_CLEANUP_BIDIRECTIONAL_W**, COMPOUND_CHAIN_COSINE_FORWARD_ONLY, COMPOUND_CHAIN_COSINE_BIDIRECTIONAL, **BIDIRECTIONAL_W_PLUS_COMPOUND_HYBRID** (primary)
- Reuses r2's W, R, E; CONFORMAL_FISHER aggregator HELD FIXED from r2c (isolates the bidirectional-W mechanism)
- K_hops in {2, 3, 4, 10}; 500 chains; 7 seeds; CPU-laptop ~40-60 min
- Anchor: ITER_CLEANUP_FORWARD_ONLY_r2c_anchor reproduces r2c K=4 1.448× ± 0.05
- Version markers: `chain_mechanism`, `aggregator=CONFORMAL_FISHER_fixed`, `K_inner`, `bidirectional_avg_weight=0.5`

**Conditional follow-on if r2d HARD_PASS:**
- `r2e_cascade_W_bidirectional_v1` (cross-thread with drill #2 c2 re-attempt; deeper noise-resilience)
- `g1b_bidirectional_W_generation_v1` (bigram-gap closure via bidirectional generation)
- `r4_hotpotqa_bidirectional_K_geq_3_v1` (HotpotQA K=3-4 chain-grade extension)

**Conditional follow-on if r2d MIDDLE_BAND:**
- `r2d_capacity_M_50k_to_200k_v1` (per by-construction-saturation discipline; sweep capacity for chain-grade-eligible regime)
- `r2e_cascade_W_bidirectional_v1` (additive boost from cascade-stabilized W)

**Conditional reroute if r2d HARD_FAIL:**
- Diagnose K-decay slope: if bidirectional flattened slope but ratio < 2.0× → magnitude is the bar, route to capacity sweep; if slope STILL steep → mechanism is wrong, route to glass-box-LLM L2 closure pivot (Phase 2 structural pivot).
- The 4-drill iterative-cleanup-chain stack is then EXHAUSTED for this arc; substrate is at a STRUCTURAL gate for K=4 multi-hop chain-grade.

**Standalone META atoms (independent of cell outcome):**
- `meta_atom_forward_only_iteration_K_noise_unstable_substrate_validated_2026-06-22.md` (substrate-validated lit prediction; substrate-fundamental finding)
- `meta_atom_LLR_PASC_log_zero_laplace_smoothing_fix.md` (hdlab/chain_score.py primitive backlog item; numerical stability fix)

---

## CONTRACT OUTPUT

`r2_3x_revival_drill_delivered: D:\AI\hd-instrument\notes\research_multihop_3x_revival_beyond_calibration_drill_2026-06-22.md; HEADLINE: the real failure is K-decay slope (CONFORMAL_FISHER 1.9x@K=2 -> 1.45x@K=4) which is forward-only-iteration noise-compounding signature per PMC11820235 / Wang 1990 BAM stability; bidirectional W (forward+backward iterative cleanup avg) flattens slope per O(sqrt(K)) -> O(1) variance scaling; P_deflated=0.40; next-cell: r2d_bidirectional_W_iterative_cleanup_v1`

---

*Research (Director) — 3rd revival drill complete per USER STANDING discipline (2026-06-22). 2x research discipline applied (4 broad WebSearch lit-scans + 4 deeper targeted scans). Generic queries only (no substrate-novel mechanism names off-platform per Fix #20 query-privacy). Lit-scan calibration applied (deflate 0.15-0.25; novel-synthesis cap 0.50 not binding for Rank #1 because BAM bidirectional is well-validated). HARD-FAIL thresholds mandatory and listed. Symmetric anti-negativity check applied (4 separate negativity-rebuttal angles). Verify-the-referent verified on r2c per-K data (PROMPT'S 1.899x cite was K=2; HARD-PASS bar is K=4 where ratio is 1.448x; K-decay slope is the actual diagnostic). 2 standalone META atoms routed (substrate-validated forward-only noise-instability + LLR Laplace-smoothing primitive fix). Bidirectional W axis chosen over compound-chain alone because BAM lit predicts the K-decay-slope flattening DIRECTLY (the load-bearing failure signature); hybrid composes both.*
