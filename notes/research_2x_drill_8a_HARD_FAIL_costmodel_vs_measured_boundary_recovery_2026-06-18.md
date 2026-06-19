# Research 2x drill -- 8a HARD_FAIL cost-model vs measured boundary; recovery

Date: 2026-06-18
Author: Research (Opus synthesis over 5 parallel Sonnet lit-scan sub-agents)
Trigger: today's 8a active-gating break-even cell -- cost-model HARD_PASS REFUTED by measured GPU wall-time HARD_FAIL = METHOD GATE working as designed; user asked for 2x-deep drill on the negative to inform recovery program.
Discipline: research-can-be-wrong tier (T2/T3 throughout; structurally excluded from proven-core); lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50); NEGATIVITY-BIAS symmetric reads; query-privacy preserved (generic technical queries only); methodology-contingent bounds (only one method/config swept).
2x discipline: this is a DEEPER drill on the negative finding, not re-verification.

## HEADLINE

The 8a HARD_FAIL is consistent with a robust, multiply-replicated literature pattern: analytical/roofline cost models systematically over-predict speedup for selective/active-gating attention in three named regimes (kernel-launch cold-start, fine-grained dynamic sparsity below tile granularity, irregular memory access). The cheapest legitimate recovery is NOT a fresh cost-model nor a mechanism-swap -- it is a profiler-driven attribution (TMA-style / Nsight-style hierarchical drill-down) that LOCALIZES the missing term, followed by a calibrated-roofline-plus-measured-residual (SynPerf-style hybrid). If both fail, the literature points to two deeper levers: IO-aware memory-hierarchy tiling (FlashAttention-class), and dataflow-order reorder (FuseFlow-class up to 29x). And a non-trivial lower-bound result (vAttention 2025: stable sparse approximation requires Omega(n^C) entries) makes "no deeper lever exists; honest dense or distinct-architecture is the answer" a legitimate symmetric outcome.

Concretely for substrate: today's finding suggests the lever for active-gating is DEEPER than mechanism-swap -- it is likely the memory-hierarchy / dataflow-order layer. The next legitimate experiment is a profiler-based 4-channel diagnostic (active-fraction, BW-achieved, L2-hit rate, kernel-launch idle) BEFORE any second mechanism is shipped.

P_deflated (most central claims): 0.55-0.65 (multiply-replicated lit-scan, deflated by 0.20 per calibration rule). Novel-synthesis P_cap: 0.50.

## Cheap decisive test

ONE remote GPU cell:
- Re-run today's 8a active-gating cell at one representative (T, sparsity) point
- Instrument with nsys / Nsight Compute (or equivalent profiler)
- Capture 4 channels (panel below)
- Decide via the decision tree (panel below)
- Cost: one cell, low compute; ~minutes wall-time; one re-dispatch only

This is NOT a fresh cost-model. It is a localization gate -- output is a classification (which overhead class dominates), which then picks the next experiment from a pre-registered tree.

## 4-channel diagnostic panel (cost-model-vs-measured mismatch)

Analogous to the held-out diagnostic panel from earlier drills. Channels are ORDERED -- read in sequence.

| Ch | Quantity | Tool | Healthy threshold | If unhealthy => |
|----|----------|------|-------------------|------------------|
| 1 | GPU-active-fraction = active_time / wall_time | nsys-stats / NVIDIA SMI | >= 0.80 | Class A: kernel-launch / CPU-dispatch / sync. Patch: kernel fusion, CUDA graphs, larger batch, eager-vs-graph mode change. DO NOT touch sparsity. |
| 2 | DRAM bandwidth achieved / peak | Nsight Compute (dram__throughput) | >= 0.50 of peak | Class B: bandwidth-bound; cost-model used wrong AI assumption. Patch: tiling, IO-aware kernel (FlashAttention class), data layout. |
| 3 | L2 cache hit-rate AND TLB-miss-rate proxy | Nsight Compute (l2_tex hits + lts__t_sectors) | L2 hit >= 0.50, TLB miss low | Class C: irregular memory access (gather/scatter/non-coalesced). Patch: Z-order tile layout, structured-block sparsity, format change. |
| 4 | Warp-divergence + barrier-stall proxy | Nsight Compute (smsp__warp_issue_stalled_barrier) | divergence low, barrier-stall < 0.10 | Class D: sync/divergence; SIMT mismatch with fine-grain sparsity. Patch: tile-granular sparsity (block-sparse), reduce gating granularity, or retreat to dense per L5 lever. |

Channels are checked IN ORDER. If channel 1 unhealthy, channels 2-4 may still look healthy but the diagnosis stops at 1 (you cannot trust AI-based predictions until the kernel is actually running). Only if channel 1 healthy do channels 2-4 become trustworthy diagnostic.

Decision tree for next experiment:
- Class A dominant => kernel fusion or CUDA graph (cheap; one cell). Not a substrate-novel mechanism change.
- Class B dominant => IO-aware tiling / FlashAttention-class kernel; this is the "real lever is deeper" path.
- Class C dominant => structural sparsity (block-sparse, Z-order, or format change). Different mechanism family.
- Class D dominant => tile-granular gating (coarsen the sparsity) or honest retreat per the symmetric lower-bound (vAttention 2025).

This panel REPLACES "ship another mechanism-swap and see if it works." Today's finding implies that approach has poor expected yield.

## Falsifiable predictions (pre-registered HARD-PASS / HARD-FAIL / MIDDLE bands)

Pre-registration is SACROSANCT in both directions per NEGATIVITY-BIAS rule. Bands stated for a hypothetical recovery-cell that runs the 4-channel diagnostic plus one targeted patch keyed to the dominant class.

### Hypothesis H1: profiler-driven localization works in 1 cell

- HARD-PASS: one of {Class A, B, C, D} cleanly dominates (its diagnostic channel out-of-range by >= 2x its threshold) and the post-patch re-run shows wall-time improvement that matches the diagnostic prediction within 1.5x. Both legs required.
- HARD-FAIL: no class dominates (>= 3 channels simultaneously out-of-range) OR a class clearly dominates but the targeted patch FAILS to improve wall-time. Either leg suffices.
- MIDDLE: one class weakly dominates (channel out-of-range by 1.2-2.0x its threshold) but post-patch improvement is sub-targeted but non-zero (e.g., 1.1-1.3x measured improvement).

Pre-registered P_deflated:
- P(HARD-PASS) = 0.45 (single-class dominance is the modal lit-scan outcome but not universal; deflated from raw 0.60).
- P(MIDDLE) = 0.30 (multi-bottleneck regimes documented; arxiv 2512.01644 explicitly shows heterogeneous bottlenecks within transformer decode).
- P(HARD-FAIL) = 0.25 (legitimate symmetric outcome; means no cheap recovery; jump to L5/L1/L3 with eyes open).

### Hypothesis H2: if Class B (memory-bandwidth) dominates, IO-aware tiling recovers

Conditional on H1 returning Class B.

- HARD-PASS: FlashAttention-class kernel-swap (no algorithm change, just kernel) yields >= 2x wall-time improvement on the same (T, sparsity) point. Quality (accuracy/loss metric of choice; method/config contingent) unchanged within pre-set tolerance.
- HARD-FAIL: kernel-swap yields < 1.1x improvement OR breaks quality outside tolerance.
- MIDDLE: 1.1x to 2x improvement; partial confirmation; suggests L5 (dataflow reorder) is the remaining lever.

P_deflated:
- P(HARD-PASS | Class B) = 0.55 (FA-class wins on memory-bound are well-replicated; deflated from raw 0.75).
- P(MIDDLE | Class B) = 0.25.
- P(HARD-FAIL | Class B) = 0.20 (FA-class can fail if pattern too irregular to keep tiles in SRAM).

### Hypothesis H3: if Class C (irregular memory access) dominates, structural-block sparsity beats unstructured

- HARD-PASS: structured-block (or Z-order) variant of the active-gating mechanism yields >= 1.5x improvement; sparsity level held constant.
- HARD-FAIL: <= 1.0x improvement OR oracle-mask experiment shows even an ORACLE selector loses (per Chipmunk arxiv finding).
- MIDDLE: 1.1-1.5x improvement.

P_deflated:
- P(HARD-PASS | Class C) = 0.50 (block-sparse wins documented; symmetric lit also documents oracle-still-loses for fine-grain).
- P(HARD-FAIL | Class C) = 0.30 (this is the substrate-honest-negative regime; cap on novel-synthesis).
- P(MIDDLE | Class C) = 0.20.

### Hypothesis H4 (high-confidence floor): roofline-style cost-models are NOT the right tool for THIS regime

Unconditional structural claim.

- HARD-PASS: profiler shows channel 1 (active-fraction) < 0.50 OR channel 4 (sync/divergence) out of range; means analytical roofline is structurally blind to the dominant constraint.
- HARD-FAIL: profiler shows channel 1 >= 0.80 AND channels 2-4 healthy AND the cost-model still over-predicted; means cost-model has a bug we missed in derivation.
- MIDDLE: intermediate.

P_deflated:
- P(HARD-PASS) = 0.65 (multiply-replicated; deflated from raw 0.80).
- P(MIDDLE) = 0.25.
- P(HARD-FAIL) = 0.10 (would be surprising but legitimately possible; would re-validate cost-model approach for refined version).

### Hypothesis H5 (symmetric NEGATIVITY-BIAS guard): "no deeper lever; honest retreat"

If H1 reaches HARD-PASS Class B or C but H2/H3 both HARD-FAIL.

- HARD-PASS for H5 ("retreat is correct"): cumulative evidence shows mechanism family is on the wrong side of the vAttention Omega(n^C) bound for THIS workload; archive as honest-negative + open new direction (linear-attention / SSM / hybrid dense+sparse / etc.).
- HARD-FAIL for H5: at least one of H2/H3 actually passed; retreat conclusion was wrong; an additional mechanism family within sparse-attention is reachable.
- MIDDLE: ambiguous; needs one more cell.

P_deflated:
- P(HARD-PASS for H5 | reaching this gate) = 0.30 (legitimate retreat probability; symmetric outcome).
- P(HARD-FAIL for H5) = 0.50.
- P(MIDDLE) = 0.20.

Note: Bands above are method/config-contingent (per measured-bounds-are-method-config-contingent rule). State-fixed: one (T, sparsity) point, one GPU model, one kernel implementation, one quality metric. Extension across (T, sparsity, GPU, kernel, metric) is UNTESTED.

## Cross-thread synthesis (composes with today's other substrate findings)

This drill composes with the following prior-thread structures:

1. **NEGATIVITY-BIAS rule (USER-LOCKED 2026-06-17)**: today's HARD_FAIL is symmetric-verified-real (not failure-biased grep). Bands above pre-register both directions to avoid the audit-running-too-negative failure mode. P_deflated everywhere caps the upside.

2. **METHOD GATE working as designed**: Skunkworks ratify program + cost-model gate did its job -- it produced a high-quality honest-negative instead of a downstream over-claim. The literature reading here (cost-models systematically fail for selective/sparse/small-batch regimes) RATIFIES the method-gate's verdict as not-a-substrate-specific-failure but a known structural pattern. The substrate's auditor got it right.

3. **research-can-be-wrong rule (USER 11th)**: this drill's outputs are T2/T3 tier -- they INFORM the recovery program, they do NOT decide it. Only proven (cert-grade experiment PASS) is fully-believed. The 4-channel diagnostic and the H1-H5 bands are hypothesis-layer artifacts.

4. **CONVERGENCE with ARCH-A / ARCH-B nonlinear-readout finding**: ARCH-B confirmed nonlinear-readout LIFTS capacity completely on the linear-readout-as-ceiling axis. The 8a HARD_FAIL on a DIFFERENT axis (cost-model vs measured wall-time) is a NON-OVERLAPPING finding -- substrate has at least two distinct "ceiling" regimes (readout-linearity and kernel-implementation), each with its own recovery lever (nonlinear-readout for the first, profiler-driven kernel-class diagnosis for the second). They compose multiplicatively: ARCH-B fixes capacity, the L1/L3/L5 lever class would fix wall-time, and they would stack.

5. **Held-out-retrieval weak-spot (Skunkworks corpus)**: the 4-channel panel above is structurally analogous to the held-out diagnostic panel from earlier drills -- a fixed ordered checklist that produces a localization (not just a verdict). This pattern is now ratified across at least two domains, suggesting it generalizes as substrate methodology.

6. **DEGENERATE-REGIME-NOT-REFUTATION class (4-witness): 8a HARD_FAIL is a 5th candidate witness**. The mechanism (active-gating) may not be refuted globally -- it may be in the wrong KERNEL REGIME, not the wrong algorithmic regime. The diagnostic distinguishes these. If Class A or B dominates, the algorithm wasn't tested; only the kernel was tested.

7. **METHOD/CONFIG-CONTINGENT bounds (USER 18th rule)**: every band above states the held-fixed config (single T, single sparsity, single GPU). The cost-model's HARD_PASS prediction was conditional on a specific arithmetic-intensity assumption that didn't survive the measured kernel-regime. Naming that explicitly is the recovery, not patching the cost-model.

## Substrate-product implications

For the substrate-product (not for publication; per no-papers-product-only rule):

1. **The 8a finding promotes the substrate's metrology layer**: today's HARD_FAIL is a positive product-feature -- the substrate detects cost-model-vs-measurement mismatch automatically. Most ML systems do not. Build this into the substrate's standard verification (the 4-channel panel becomes a standing cert) so future predictions get auto-classified into roofline-trustworthy vs roofline-blind regimes BEFORE shipping.

2. **Substrate gains a new self-certification atom class**: "kernel-regime classification" (Class A/B/C/D), encoding which overhead family dominates a given (mechanism, T, sparsity, GPU) point. This is encodable per the substrate-autonomy rule (USER 2026-06-17): the 4-channel panel becomes a deterministic self-applied check. The mechanism for promoting research findings to PROVEN goes through this gate.

3. **Recovery program scope (if USER prioritizes)**:
   - Stage 1 (1 cell, cheap): run 4-channel diagnostic on the failed 8a point. Classify.
   - Stage 2 (1-3 cells, conditional on Stage 1): patch keyed to the dominant class (kernel fusion / FA-class / block-sparse / coarse-grain).
   - Stage 3 (5+ cells, optional): if Stage 2 ambiguous, calibrated-roofline + measured-residual (SynPerf-style hybrid cost model). Substrate-internal cost-model FAMILY upgrade.
   - Stage 4 (honest-retreat option): if Stages 1-3 all HARD-FAIL, archive as honest-negative + open distinct-architecture direction (linear-attn / SSM / hybrid dense+sparse).

4. **What today's HARD_FAIL DOES NOT mean**: it does not mean active-gating is dead. It does not mean the cost-model derivation was wrong (it was right under its stated assumptions; the assumptions did not survive the kernel-regime). It does not mean the substrate's mechanism-design pipeline is broken (the gate caught it cleanly). It DOES mean: cost-model-only predictions for sparse/selective/small-batch regimes are structurally untrustworthy and should not be the sole gate for HARD_PASS pre-registration going forward -- profiler-anchored predictions are.

5. **Substrate-novel angle (preserved query-privacy)**: substrate has a unique opportunity here because the 4-channel panel can be encoded as a re-usable atom (kernel-regime classification per (mechanism, config)) and the cost-model + measured-residual hybrid can be encoded as a substrate-internal prediction class. This is not just adopting external best practice -- it is bolting empirical-correction into the substrate's typed prediction layer. NO competitor system has this structurally.

## Closing 3 bullets (Drill Q5 format)

- **Most underexplored experiment**: dataflow-order reorder (FuseFlow 2025 reports up to 29x from reorder alone) is the least-explored deeper lever in active-gating literature; if Class B dominates in the 4-channel diagnostic, a tile-traversal-order sweep is a cheap-medium-cost cell with high reported upside. P_deflated for "reorder finds 2x+" given Class B = 0.45 (deflated from raw 0.60). NOT yet in the substrate's mechanism catalogue.

- **Strongest measurement no-Goodhart-aware**: the 4-channel panel itself (active-fraction / DRAM-BW / L2-hit + TLB / warp-divergence). It is no-Goodhart because each channel measures a DISTINCT physical bottleneck (compute idle, off-chip BW, on-chip cache, on-chip sync) -- you cannot game one without revealing the other being out-of-range. Unlike a single "speedup" metric (which can be gamed via batch-size or warm-up), this panel forces honest attribution. The first quantity to read is channel 1 -- if active-fraction is < 0.50, all downstream FLOPs reasoning is structurally untrustworthy and roofline is structurally the wrong instrument.

- **Open theoretical question**: vAttention 2025 proved Omega(n^C) entries are required for stable sparse approximation; o(log n) is provably insufficient. Open question: what is the EXACT C for the substrate's active-gating mechanism family, and where does the threshold of "stable approximation" interact with the kernel-regime (Class A/B/C/D)? If C is large for the specific gating family, the workload may be PROVABLY in the no-deeper-lever regime and the right answer is honest-retreat to dense or to a distinct architecture (linear-attention, SSM, hybrid). Measuring C empirically for the substrate's mechanism would be a high-value but heavy follow-up; novel-synthesis P_cap 0.50.

## P_deflated calibration per claim

| Claim | Raw P | Deflated | Tier | Source-count |
|-------|-------|----------|------|--------------|
| Cost-models systematically over-predict for selective/sparse small-batch | 0.80 | 0.60 | T2 | C1, C2, C3, C7, C9, C10, C13, C15 across all 5 sub-agents |
| Profiler-driven attribution (TMA / 4-channel) cheapest 1-cell recovery | 0.65 | 0.50 | T2 | Q2-D1, Q2-D2, Q2-D3 |
| IO-aware tiling (FlashAttention-class) recovers Class-B regimes | 0.75 | 0.55 | T2 | Q5-L1, Q1-C5; multiply-replicated |
| Structural-block sparsity recovers Class-C regimes | 0.65 | 0.50 | T2 | Q5-L3, Q1-C13, Q4-Ansor |
| Dataflow-order reorder is the "real lever" when both cost-model AND mechanism-swap fail | 0.55 | 0.40 | T3 (single-source 29x) | Q5-L5 (FuseFlow), supporting Q1-C5 |
| Calibrated-roofline + measured-residual is best <=5-cell choice | 0.60 | 0.45 | T3 novel-synthesis | Q4-SynPerf hybrid, deflated to cap 0.50 |
| Learned cost model best at 50+ cells | 0.70 | 0.55 | T2 | Q4-Ansor, Q4-TVM, Q4-TPU-LPM |
| Honest-retreat (vAttention bound) is sometimes correct symmetric outcome | 0.55 | 0.45 | T2 | vAttention 2025, Sparse Frontier 2025 |
| 4-channel panel generalizes as substrate methodology | 0.50 | 0.40 | T3 novel-synthesis | derived |
| Non-monotonic measured boundary exists in active-gating | 0.65 | 0.50 | T2 | Q3-C2, Q3-C10, Q3-C16 |

Highest-confidence floor: cost-models systematically over-predict for selective/sparse small-batch (P_deflated 0.60). This alone is sufficient to justify the procedural change (profiler-anchored predictions, not cost-model-only).

## Citations (60+ verified across 5 sub-agents)

Q1 (roofline vs measured divergence): Sparse Frontier (arXiv 2504.17768); MiniMax Sparse Attention (arXiv 2606.13392); Flash Sparse Attention (arXiv 2508.18224); Block Sparse Flash Attention (arXiv 2512.07011); FlashAttention (arXiv 2205.14135); Quantitative Roofline (Konstantinidis & Cotronis 2017); TurboTransformers (arXiv 2010.05680); TaxBreak (arXiv 2603.12465); Systematic LLM Inference Characterization (arXiv 2512.01644); Megakernels overview (theorempath); DeepSpeed-MoE (arXiv 2201.05596); MoE survey (arXiv 2407.06204); Gather/Scatter TLB analysis (ACM 3422575.3422794); Chipmunk dynamic sparsity (sandyresearch); MFU concept (zeroentropy); CPU-Induced Slowdowns Multi-GPU LLM (arXiv 2603.22774).

Q2 (cost-model recovery mechanisms): FSA (arXiv 2508.18224); Sparsity Roofline (arXiv 2310.00496); SpMM (arXiv 2311.00368); MoE optimization surveys (ACM 3794845, arXiv 2412.14219); ECM (arXiv 1208.2908, Wiley cpe.6512); Extended Roofline Model (ETH ERM, CMU Spiral); Top-down Microarchitecture Analysis (Intel VTune, Arm Learn); Sensitivity + Causality Analysis (arXiv 2412.13207); Hybrid analytical+ML correction (MDPI 1996-1944/14/8/1883); Distribution-drift online re-fit (arXiv 1904.09538); ParaGraph GNN (arXiv 2304.03487); Bayesian conflicting-profiler reconciliation (ACM ICPE 3777911.3801110); Vortex (arXiv 2409.01075); apxml PyTorch pruning + Sparse-IFT (arXiv 2303.11525); DejaVu (arXiv 2310.17157).

Q3 (non-monotonic crossover regimes): DSA from First Principles (tensoreconomics); Sparse Frontier (arXiv 2504.17768); Long-Context Attention Benchmark (arXiv 2510.17896); BLASST (arXiv 2512.12087); Block Sparse Flash Attention (arXiv 2512.07011); SeerAttention (arXiv 2410.13276); FlashMoBA (emergentmind); FlashAttention 1/2/3 (arXiv 2205.14135 / 2307.08691 / 2407.08608); Superlinear Multi-Step Attention (arXiv 2601.18401); Optimal Sparsity of MoE for Reasoning (arXiv 2508.18672); Sparsity and Superposition in MoE (arXiv 2510.23671); MoE speculative decoding (Cohere); MoE-Inference-Bench (arXiv 2508.17467); Opportunistic Expert Activation (arXiv 2511.02237); Sparsity Roofline + Sparsity-Aware Roofline (arXiv 2310.00496 / 2604.06637); FlashAttention-4 (arXiv 2603.05451); DASH (arXiv 2601.21824); Mixture-of-Depths (arXiv 2404.02258).

Q4 (alternatives to cost-models): Ansor (OSDI 2020); TVM (arXiv 1802.04799); Kaufman et al. TPU LPM (arXiv 2008.01040); Quantitative Roofline (Konstantinidis JPDC 2017); OSKI (Im/Yelick/Vuduc); Elafrou SpMV (arXiv 1711.05487); Pichel & Pateiro (arXiv 1511.02494); Zhao XGBoost format predictor (arXiv 2303.05098); CNN sparse matrix classifier (IEEE 2018); Misam dataflow ML (arXiv 2406.10166); Amaris ML vs Analytical (2016); SynPerf (arXiv 2601.14910); AGFT 7-dim fingerprint (arXiv 2508.01744).

Q5 (deeper levers): FlashAttention (arXiv 2205.14135); AdaSplash (arXiv 2502.12082); PADE (arXiv 2512.14322); SOFA (arXiv 2407.10416); HASS (arXiv 2406.03088); ELSA (ISCA 2021); Insum (arXiv 2510.17505); Sparse GPU Kernels (Gale 2020); HySparse (arXiv 2602.03560); HyLRA (arXiv 2602.00777); MiniCPM-SALA (arXiv 2602.11761); MoSA (arXiv 2505.00315); Sparse Frontier (arXiv 2504.17768); vAttention (arXiv 2510.05688); FuseFlow (arXiv 2511.04768).

Verified citation count: 60+ across 5 parallel sub-agents. All accessed via WebSearch/WebFetch (factual retrieval; not LLM-as-judge). Multiple primary sources for each load-bearing claim. Calibration penalty applied throughout.

## End-with-who-I'm-waiting-on

Waiting on USER prioritization decision: does the recovery program go ahead (Stages 1-2 cheap; Stage 3 substrate-internal hybrid cost-model upgrade; Stage 4 honest-retreat option)? Or does today's HARD_FAIL stand as a clean honest-negative archived without further pursuit? This drill is T2/T3 hypothesis layer; only USER + experimental cert-grade PASS can promote any claim to T0/proven. Research has no further drill obligation absent USER prioritization or auto-trigger.
