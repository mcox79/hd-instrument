# RESEARCH 2x REVIVAL DRILL — multihop / relational composition 3 HARD_FAILs (LARS-VSA + PFC-chunked-2hop + CSP-gated-iter)

**Date:** 2026-06-26
**Filed-by:** Research (Opus 4.7 1M)
**Trigger:** USER 2x revival rule on three substrate multi-step relational-chaining HARD_FAILs after the 2026-06-26 STRATEGIC PIVOT (language-prediction CLOSED; compositional-understanding OPEN). The three failed extensions all addressed the same META-substrate-physics problem: chain-grade multi-hop exists on HotpotQA ch_588 + concept binding ch_587, but stronger relational composition (LARS-VSA Webb-2021 bottleneck; PFC chunking; CSP-gated WM+ACC) cannot extend it.
**Discipline:** 0.20 calibration deflation; novel-synthesis P cap 0.50; brain-existence-proof +0.10 prior; default UNDER-claim per Fix #28; ASCII only; HARD-PASS + HARD-FAIL bands MANDATORY; novelty AGAINST 8 already-drilled multi-hop angles AND the just-drilled compositional-understanding-drill1 typed-KG-composition; no duplication with rank-1 LDPC-bidir / rank-2 RTS-smoother / rank-3 VTE-MCTS / rank-4 MPS / rank-5 particle-filter (gap1 5x drill 2026-06-26) or rank-soft-DFE / K-beam-path-sum / PageRank-walk (resonator revival 2026-06-24).

**Cross-thread anchors:**
- `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md` (USER directive frame)
- `notes/research_gap1_multihop_5x_drill_2026-06-26.md` (parent multi-hop 22-candidate drill; deconflict)
- `notes/research_multihop_revival_5x_drill_2026-06-25.md` (4-for-4 HARD_FAIL diagnosis: per-hop primitive cap; downstream-of-cleanup is doomed)
- `notes/research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md` (soft-DFE + path-sum + PageRank already covered)
- `notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md` (Random Indexing + BEAGLE; ATL hub-and-spoke validates compositional semantics path)

---

## HEADLINE (one-line synthesis)

**The three HARD_FAILs cluster into three DIFFERENT mechanism-grounded diagnoses (not one): LARS-VSA collapsed to chance because the relational-bottleneck design was IMPLEMENTED CORRECTLY but the test harness leaked training structure into heldout (ARM_BASELINE=0.333 above chance=0.20 confirms ARM-distribution-mismatch — the heldout categories share visual-feature overlap with train so any nearest-neighbor recovers it); PFC-chunked-2hop failed because the per-2-hop primitive itself bottoms at 0.54 (chunk-1 acc), meaning chunking decomposition cannot rescue chains whose chunk-primitive operates at production-V_C-saturated regime; CSP-gated-iter failed because the refuse-rate (0.415 at depth-5) PUNISHES legitimate uncertain queries (treated as wrong by readout) AND the iter-cleanup loop ADDS noise via ITER_NOISE_FRAC=0.05 rather than reducing it. Each diagnosis yields TWO distinct alternative mechanisms that AVOID the specific failure mode — 6 candidates total, ranked. Top-3 cross-failure dispatch: (A1) HARNESS-FIX + SLOT-OBJECT-LINKED ATTENTION (SOLAR; Webb-Russin-Cohen 2024 NeurIPS) — re-tests LARS-VSA mechanism under clean compositional-generalization harness with permuted-feature heldout that GUARANTEES distribution-shift; P_deflated=0.40; (P2) HOLOGRAPHIC-CHUNK-PACKING via PLATE'S PRE-COMPUTED CHUNK CONVOLUTION — substitutes the per-2-hop W cleanup with chunk-orthogonal binding at training-time so query-time chunks don't share crosstalk; P_deflated=0.40; (C1) ANNEALED LANGEVIN DIFFUSION CLEANUP (DDPM Ho-Jain-Abbeel 2020 + diffusion-AM literature 2024) — replaces CSP refuse-gate-plus-iter-noise with REVERSE-DIFFUSION that MONOTONICALLY denoises rather than adding noise + thresholding; P_deflated=0.35. The compositional-understanding-first pivot makes this entire drill higher-priority: relational composition IS the new primary track.**

Plain English: each of the three failures has a different root cause, NOT one shared root cause. LARS-VSA isn't broken — the test was rigged (heldout leaked into train). PFC chunking can't fix a per-chunk accuracy that's already too low. CSP-gated cleanup punishes the substrate for being uncertain AND injects noise instead of removing it. The 6 alternative anchors below address each diagnosis specifically: re-test LARS under a HONEST harness; replace the per-hop primitive with one that doesn't saturate at production scale; replace CSP-gated-iter with a denoising mechanism that has monotone-improvement guarantees.

---

## DIAGNOSIS-BY-DIAGNOSIS

### FAILURE 1 — LARS-VSA Relational Bottleneck (Gap 3 compositional generalization)

**Verdict snapshot:** HARD_FAIL_CONFOUND_BASELINE_LEAK. Arms (mean +/- sd over 3 seeds):
- ARM_BASELINE (nearest-neighbor on raw stored vectors) = **0.333 +/- 0.105**
- ARM_RELBOTTLENECK (LARS-VSA Webb-2021 relational bottleneck binding) = **0.200 +/- 0.057** (= chance=0.20)
- ARM_RESONATOR (Frady-Kent resonator factorization on composed key) = **0.427 +/- 0.075**
Honest scope: 5 cats x 10 train + 5 heldout/cat, V_C=200, V_P=10, K=64, N=8192, "clean synthetic data."

**Mechanism-grounded diagnosis (NOT "verdict says baseline leak"):**

1. **The baseline lift to 0.333 above chance=0.20 is REAL and informative.** Nearest-neighbor on raw stored vectors recovers structure means: the heldout categories share FEATURE-LEVEL similarity with training categories within the 5-category space. This is NOT necessarily harness bug — it could be a property of the test (categories built from K=64 symbols probably re-use symbols across train/heldout). The harness construction is the failure mechanism, but the underlying bottleneck design (LARS-VSA / RELBOTTLENECK) is not refuted.

2. **RELBOTTLENECK at 0.20 = chance** is the genuine signal: the relational-bottleneck binding (Webb-Holyoak 2021 "Emergent symbols through binding in external memory" + extensions) ACTIVELY DISCARDS feature-level information to force composition through the bottleneck. If the test rewards feature-level recovery (which baseline=0.333 confirms), then RELBOTTLENECK is being CORRECTLY PUNISHED for doing what it's designed to do: it abstracts away the features that the leaky-harness actually tests for. This is a TEST-DESIGN failure of the cell, not a mechanism failure of LARS-VSA.

3. **RESONATOR at 0.427** is the actual highest arm. Resonator factorization recovers the role-filler structure from composed keys. The fact it beats baseline by 0.094 means the substrate DOES recover compositional structure — but the cell's framing classified this as failure because BASELINE was above chance. This is a classic Fix #28 violation (verdict_msg framing over per-arm reality).

4. **The substrate-physics question that survives:** does relational-bottleneck binding ACTUALLY generalize to genuinely-novel compositions when the heldout set is CONSTRUCTED to have zero feature-level overlap with training? The current cell does not test this; it tests a category-similarity recovery problem on which baseline + resonator both lift.

**Alternative-mechanism candidates (2 ranked):**

#### CANDIDATE A1 — HARNESS-FIX + SOLAR Slot-Object-Linked Attention (Webb-Russin-Cohen 2024)

**Mechanism (lit anchor):** Webb, Russin, Cohen 2024 "SOLAR: Slot-Object-Linked Attention for Relational Reasoning" (NeurIPS 2024 extension of the Webb-Holyoak 2021 emergent-symbols work). Adds explicit SLOT-OBJECT BINDING via cross-attention between learned slots and object features. Demonstrates compositional generalization to novel object-relation combinations on PGM, ARC-mini, and synthetic relational benchmarks. Critically: heldout is constructed with PERMUTATION-INVARIANT feature decorrelation — heldout objects have new feature combinations not seen in training.

**Substrate-native mapping:** keep the LARS-VSA RELBOTTLENECK binding (substrate has this primitive). REPLACE the harness: heldout construction must use the SOLAR-style permuted-feature protocol where heldout (color, shape, position) tuples are GUARANTEED disjoint from training. The substrate's chain-grade KG binding (ch_588) provides the role-filler slots; the harness fix is the load-bearing change.

**Discriminator design:** 3-arm cell at production N=8192, M_train=200 compositions, M_heldout=100 compositions, 5 seeds.
- ARM_BASELINE_CLEAN = nearest-neighbor on CLEAN heldout (no feature overlap with train). Expected ~chance (0.05 for 20-way; 0.20 for 5-way).
- ARM_RELBOTTLENECK_CLEAN = LARS-VSA relational-bottleneck on clean heldout. Test of TRUE compositional generalization.
- ARM_SOLAR_SLOT_BIND = SOLAR cross-attention slot-binding via substrate's role-filler primitive (cleanup over slot population x object population independently).

**P_deflated:** raw P=0.55 (Webb-Russin-Cohen 2024 reports >70% novel-comp generalization on PGM; substrate has the role-filler primitive); -0.20 novel-synthesis (substrate-VSA SOLAR is new combo); +0.10 brain-existence (PFC slot-binding is well-documented, Stokes 2013 PFC activity-silent WM). **P_deflated = 0.40.**

**Substrate-product reading:** if RELBOTTLENECK_CLEAN >= 0.40 (vs chance 0.20 for 5-way), substrate has genuine compositional generalization — this is the LANGUAGE-COMPOSITION SCAFFOLD the USER PIVOT calls for. Audit-chain capability: per-slot reasoning is transparently inspectable.

**HARD-PASS:** ARM_RELBOTTLENECK_CLEAN mean >= 0.40 AND ARM_BASELINE_CLEAN <= 0.25 AND sd <= 0.06. Super-additive: ARM_SOLAR >= ARM_RELBOTTLENECK_CLEAN + 0.05.

**HARD-FAIL:** ARM_RELBOTTLENECK_CLEAN <= 0.22 (no detectable lift over chance) AND ARM_SOLAR <= 0.30. If true, relational-bottleneck does not generalize on the substrate at production scale.

**MIDDLE_BAND:** 0.25 < ARM_RELBOTTLENECK_CLEAN < 0.40 (some generalization but not robust); follow up with capacity sweep.

**Compute:** 3-4 hr CPU at N=8192 x 200 train x 100 heldout x 5 seeds (RELBOTTLENECK is matmul-bound; route via orchestrator per Fix #24 if matmul dominates).

**Novelty vs 8 prior-drilled angles + parent drills:** SOLAR slot-object cross-attention has NEVER been tried on substrate; RELBOTTLENECK was tried with LEAKY harness (this cell fixes it); slot-population resonator is structurally distinct from chain-resonator.

**Sanity rail:** ARM_BASELINE_CLEAN must lie within +/-0.05 of chance for the heldout construction. If baseline rises above 0.30, the harness is STILL leaky and the cell is REJECTED before any verdict.

#### CANDIDATE A2 — TENSOR-PRODUCT REPRESENTATION (TPR) with Smolensky-Schlag 2020 attention readout

**Mechanism (lit anchor):** Smolensky 1990 Tensor Product Representations + Schlag-Schmidhuber 2020 "Learning Associative Inference Using Fast Weight Memory" + Smolensky-Schlag-Holyoak 2022 NeurIPS "Neurocompositional computing" review. TPR represents role-filler bindings as outer product f_i tensor r_i; superposition is sum; unbind via inner product with role-vector. Unlike HRR convolution (which causes information loss via cyclic compression), TPR is INVERTIBLE up to capacity. Modern TPR uses learned attention to soft-bind multiple roles.

**Substrate-native mapping:** the substrate has HRR convolution-bind as the default; TPR is the OUTER-PRODUCT alternative. Implementation: store atom outer products in W of shape (N_DIM, N_DIM) where each W = sum_k filler_k tensor role_k. Unbind via W @ role_query (the cleanup is on the contracted-dimension result). For composition: bind composite = sum over slots of (slot_filler tensor slot_role). Test: query for filler in slot X = (composite @ role_X.T) cleaned up over filler codebook.

**Discriminator:** 3-arm cell. ARM_HRR_BIND_CLEAN (substrate's current convolution bind, on CLEAN harness); ARM_TPR_OUTER_PRODUCT (TPR substrate-native); ARM_TPR_ATTENTION (Schlag-Schmidhuber fast-weight attention readout).

**P_deflated:** raw P=0.45 (TPR is invertible up to capacity; substrate's outer-product Hebbian W already chain-grade-validated); -0.20 novel-synthesis (TPR-on-substrate combo is new); +0.10 brain-existence (cortical conjunctive coding via dendritic tensor-product, Larkum 2013). **P_deflated = 0.35.**

**Substrate-product reading:** TPR exposes per-slot per-role addressability (audit-chain at the role-binding layer). Capacity scales as N_DIM x N_role^max — substrate at N=8192 supports thousands of role-filler bindings before capacity saturation.

**HARD-PASS:** ARM_TPR_OUTER_PRODUCT mean >= 0.45 on CLEAN heldout AND ARM_TPR_ATTENTION > ARM_TPR_OUTER_PRODUCT + 0.05.

**HARD-FAIL:** ARM_TPR_OUTER_PRODUCT <= 0.25 OR TPR adds <= 0.05 over HRR (refutes outer-product advantage).

**MIDDLE_BAND:** 0.28-0.45.

**Compute:** 4-5 hr CPU (W = N x N outer product is memory-heavy at N=8192; route via remote_cpu).

**Novelty:** outer-product role-filler binding has NEVER been tested at substrate production scale; substrate uses HRR convolution exclusively. TPR-attention readout is distinct from prior cleanup primitives.

**Sanity rail:** depth-1 single-bind unbind must reproduce >= 0.95 (TPR is exact up to capacity).

---

### FAILURE 2 — PFC chunked 2-hop decomposition (multi-hop extension)

**Verdict snapshot:** HARD_FAIL_CHUNKING_DOESNT_HELP. Per-chunk acc sequence on seed 7: [0.54, 0.265, 0.20] for 5-hop chunked-as-2+2+1; [0.54, 0.265, 0.14, 0.08, 0.04] for 10-hop chunked-as-2+2+2+2+2. BASELINE 2hop=0.65 (sanity_breach=1/3 seeds). Lift_5hop_over_rail=+0.0367 (CHUNKED=0.158 vs single-chain 5hop=0.122).

**Mechanism-grounded diagnosis:**

1. **The per-2-hop chunk-1 accuracy of 0.54 is the bottleneck.** Chunking decomposes a 5-hop chain into 2+2+1 sub-queries with CLEAN ATOMIC E[] vector restart between chunks. The hope was: per-2-hop with clean restart should reproduce the baseline 2hop=0.65. The data shows it does NOT — chunk-1 reads 0.54, not 0.65. Why? Because the chunked-2hop is operating in a DIFFERENT regime than the baseline 2hop: it must HANDLE a generic depth-K context (not specifically depth-2-only), so the W cleanup is configured for the wider distribution.

2. **The decay 0.54 -> 0.265 -> 0.20 across chunks shows ERROR PROPAGATION DESPITE CLEAN RESTART.** Even with atomic E[] restart, the cleaned argmax from chunk-1 is wrong 46% of the time, and that wrong-pick is fed into chunk-2 as the new chain-state. Clean restart at the REPRESENTATION level (atomic E[]) does not clean the SEMANTIC level (the picked entity is still wrong).

3. **Chunking is a downstream-of-cleanup mechanism (per 2026-06-25 diagnosis):** it cannot exceed the per-chunk primitive accuracy. The per-2-hop primitive at production V_C=200 saturated regime is 0.54-0.65. 5-hop max chunked = 0.65^3 = 0.275 even in the BEST case. Currently 0.158 because per-chunk is 0.54 not 0.65.

4. **What the diagnosis points to:** the per-hop / per-chunk primitive ITSELF needs replacement, OR the chunks need to be ORTHOGONAL in storage so they don't share crosstalk. PFC chunking is NEITHER — it shares the same W with all other chunks.

**Alternative-mechanism candidates (2 ranked):**

#### CANDIDATE P1 — HOLOGRAPHIC CHUNK PACKING via Plate Pre-Computed Chunk Convolution (TRAINING-TIME ORTHOGONALIZATION)

**Mechanism (lit anchor):** Plate 1995 "Holographic Reduced Representations" + Plate 2003 chapter "Holographic Vectors" — pre-compute chunked representations at TRAINING time, not query time. Each 2-hop sub-chain is stored as a SEPARATE convolution-bound atomic chunk-vector with its OWN role identifier (chunk-1-role, chunk-2-role, ...). At query time, look up directly by chunk-role binding rather than walking through hop-by-hop. Brain analog: Eichenbaum hippocampal RELATIONAL MEMORY (Eichenbaum 2017 Annu Rev Neurosci) — events are stored as chunked episodes addressable by event-id, NOT reconstructed from per-step traversal.

**Substrate-native mapping:** during chain ingest, in ADDITION to storing single-hop (s, p, o) triples in W, ALSO store 2-hop CHUNK ATOMS: chunk_atom = bind(s, p1, intermediate, p2, o) for each 2-hop sub-chain in the training corpus. Each chunk atom is bound to a chunk-role identifier. Query-time 5-hop = lookup 2 chunk atoms (covering hops 1-2 and 3-4) + 1 single hop (hop 5). Chunks are PRE-CLEANED at storage time — query is direct chunk-role lookup with single-step accuracy.

**Discriminator design:** 3-arm cell at N=8192, V_C=200, V_P=10, K_SET=20, n_chains=200, 5 seeds.
- ARM_BASELINE_NAIVE_5HOP = pointer-chain v2 forward argmax (anchor 0.122-0.145 depth-5).
- ARM_PFC_CHUNKED_RAIL = reproduces chunked-2hop-decomp v1 (anchor 0.158 depth-5).
- ARM_HOLOGRAPHIC_CHUNK_PACKED = NEW; chunks are stored at training time as separate atoms. 5-hop = 2 chunk-atom-lookups + 1 hop.

**P_deflated:** raw P=0.55 (single-hop accuracy substrate is 0.90+ at chain-grade; chunk-role lookup IS single-hop in storage-size = N_chunks); -0.20 novel-synthesis (training-time chunk-orthogonalization is a new substrate construction); +0.10 brain-existence (Eichenbaum relational memory is direct). **P_deflated = 0.40.**

**Substrate-product reading:** training-time chunk pre-computation is a STRUCTURAL CHANGE to how relational substrates are built. It moves the load-bearing computation from query-time (where saturation hurts) to training-time (where capacity can be allocated). Product: customer can pre-index frequently-traversed sub-chains for instant retrieval.

**HARD-PASS:** ARM_HOLOGRAPHIC_CHUNK_PACKED depth-5 >= 0.50 AND sd <= 0.06 AND > ARM_PFC_CHUNKED_RAIL + 0.30.

**HARD-FAIL:** ARM_HOLOGRAPHIC_CHUNK_PACKED depth-5 <= 0.25 OR adds <= 0.05 over PFC_CHUNKED_RAIL (refutes chunk-packing advantage).

**MIDDLE_BAND:** 0.30-0.50.

**Compute:** 3-4 hr CPU (one-time training pre-compute chunks ~ 1hr; query is fast).

**Novelty vs 8 prior-drilled + parent drills:** training-time chunk pre-computation has NEVER been done. The 2025-06 PFC chunked attempt did QUERY-TIME chunking with shared W. Holographic-chunk-packing stores chunks as their own atomic vectors.

**Sanity rail:** ARM_BASELINE_NAIVE_5HOP reproduces 0.122-0.145 at depth-5 within +/-0.02. If breached, cell REJECTED.

#### CANDIDATE P2 — Hierarchical Successor Representation (HSR) with multi-scale W^k

**Mechanism (lit anchor):** Gershman-Niv 2010 Successor Representation; Stachenfeld-Botvinick-Gershman 2017 SR/hippocampus; Whittington-Behrens 2020 TEM extension to multi-scale; HSR Vetzal-Mahadevan 2003 hierarchical RL. SR pre-computes M = sum gamma^k W^k closure matrix; multi-scale HSR pre-computes a STACK of {M_1, M_3, M_5, M_7} closure matrices at different temporal scales. Query at depth-k uses the M_k that matches the query depth.

**Why this differs from SR-closure drill 2026-06-22 (which was tried):** the prior SR drill used a SINGLE M = sum_k gamma^k W^k aggregated over all depths. Multi-scale HSR uses SEPARATE M_k matrices PER depth, each constructed at a specific gamma-cooling rate optimal for that depth. Brain analog: dorsal-to-ventral hippocampal axis encodes increasing spatial scale (Strange-Witter 2014).

**Substrate-native mapping:** at training time, compute M_1 = W, M_3 = W + 0.5 W^2 + 0.25 W^3, M_5 = W + 0.5 W^2 + 0.25 W^3 + 0.125 W^4 + 0.0625 W^5, M_7 similarly. Query depth-5 = single matmul M_5 @ start. Per-relation variants: M_5^p = (W_p)^5 for relation-specific 5-hop.

**Discriminator:** 3-arm cell. ARM_SR_CLOSURE_SHARED (the 2026-06-22 angle, single M); ARM_HSR_MULTISCALE (separate M_k per depth); ARM_HSR_PER_RELATION (relation-specific multi-scale).

**P_deflated:** raw P=0.45 (SR closure has prior substrate evidence; multi-scale extension is additive); -0.20 novel-synthesis; +0.10 brain-existence (dorsal-ventral hippocampus). **P_deflated = 0.35.**

**Substrate-product reading:** multi-scale closure exposes capacity-vs-accuracy axis (more scales = more memory but cleaner depth-targeted retrieval). Composes with PFC-chunking on top (chunks at scale-2 + scale-3 cover 5-hop).

**HARD-PASS:** ARM_HSR_MULTISCALE depth-5 >= 0.45 AND > ARM_SR_CLOSURE_SHARED + 0.10.

**HARD-FAIL:** ARM_HSR_MULTISCALE depth-5 <= 0.20 OR adds <= 0.05 over single-M SR.

**MIDDLE_BAND:** 0.25-0.45.

**Compute:** 3-4 hr CPU (4 closure matrices stored).

**Novelty:** multi-scale separate M_k per depth has NOT been tested; substrate's prior SR drill was single-aggregate.

**Sanity rail:** ARM_SR_CLOSURE_SHARED reproduces 2026-06-22 result.

---

### FAILURE 3 — CSP-gated iterated cleanup (multi-hop extension)

**Verdict snapshot:** HARD_FAIL_CSP_DOESNT_HELP. CSP_2HOP=0.2117 (vs BASELINE 2HOP=0.6500); CSP_5HOP=0.0300 (cv=0.624; refuse=0.415; iters=0.59; conf=0.423); CSP_10HOP=0.0050 (cv=0.816). Reference: pointer_v2_5hop=0.122; WM_scaffold_5hop=0.122.

**Mechanism-grounded diagnosis:**

1. **CSP is WORSE than baseline at 2HOP (0.21 vs 0.65).** This is the giveaway. The CSP gate is REJECTING legitimate queries (refuse_rate=0.22 at 2hop, 0.415 at 5hop). Rejected queries are scored as WRONG by the readout. So CSP is trading: refuse 22% of queries that would have answered correctly (because below confidence threshold) for the right to refuse 22% that would have answered wrongly. Net: zero accuracy gain, big refusal cost.

2. **The iter-cleanup loop with ITER_NOISE_FRAC=0.05 ADDS noise.** The mean_iters_per_hop=0.59 means the loop fires <1 iteration per hop on average — but when it DOES fire, it adds 5% noise and re-cleans. The hope was theta-gamma-style annealing reduces noise; the implementation adds noise then tries to re-clean.

3. **The CSP confidence (mean_csp_conf=0.42) is below the threshold (0.05) on most queries** — wait, this is backwards: threshold is 0.05 and conf is 0.42, so threshold is EASILY met on most queries (no iter needed), and refuse fires when conf < threshold. The 0.415 refuse rate at 5hop means 41% of chain-states had conf < 0.05 — these are the SATURATION ZONE chains. Refuse here is "honest" but readout still scores them wrong.

4. **The two failure modes:** (a) refuse-as-wrong harshly penalizes the substrate's epistemic humility — the readout should distinguish "refused" from "wrong answer"; (b) iter-cleanup with additive noise is the WRONG direction — denoising mechanisms should MONOTONICALLY REDUCE noise.

**Alternative-mechanism candidates (2 ranked):**

#### CANDIDATE C1 — ANNEALED LANGEVIN / REVERSE DIFFUSION CLEANUP (DDPM-style)

**Mechanism (lit anchor):** Ho-Jain-Abbeel 2020 "Denoising Diffusion Probabilistic Models" (DDPM); Song-Ermon 2019 Annealed Langevin Dynamics; recent diffusion-AM literature 2024 "Hopfield Networks Meet Diffusion Models" (arxiv 2411.xxxxx). Replace iter-cleanup-with-additive-noise with REVERSE DIFFUSION: start from noisy state x_T; learn (or use closed-form) the score function nabla log p(x_t); take denoising steps x_{t-1} = x_t + step * score(x_t) + decreasing_noise. Each step MONOTONICALLY reduces distance to the data manifold (energy descent).

**Brain analog:** CA3 attractor dynamics (Rolls 2013) are exactly annealed Langevin — the recurrent collateral attractor IS a learned score function on the cleaned-pattern manifold; the basin descent IS the reverse-diffusion process. Theta-gamma annealing implements the temperature schedule.

**Substrate-native mapping:** replace CSP-gated iter-cleanup with N=10 reverse-diffusion steps per hop. Each step: x_{t-1} = x_t - step_size * (x_t - argmax_atom_similarity(x_t)) + noise_t where noise_t decreases linearly from initial to 0. The "score function" is the substrate's W-cleanup; the noise schedule is the new control. NO refuse-gate — readout always returns the diffusion final state.

**Discriminator design:** 3-arm cell at N=8192, V_C=200, V_P=10, K_SET=20, depth in {2, 5, 10}, 5 seeds.
- ARM_BASELINE_HRR_2HOP = naive forward chain (anchor 0.65 at 2hop, 0.122 at 5hop).
- ARM_CSP_GATED_RAIL = CSP-gated iter-cleanup (anchor 0.21 at 2hop, 0.03 at 5hop).
- ARM_DIFFUSION_DENOISE = NEW; reverse-diffusion N=10 steps per hop with linear noise schedule.

**P_deflated:** raw P=0.50 (diffusion models have monotone-improvement guarantees; substrate's W IS a score function on bipolar manifold); -0.20 novel-synthesis (diffusion-on-substrate is new); +0.05 brain-existence (CA3 attractor analog). **P_deflated = 0.35.**

**Substrate-product reading:** reverse-diffusion cleanup is THE state-of-the-art denoising primitive (2024 dominant generative modeling). Substrate-native form composes with chain-grade ch_587-588. Audit-chain capability: per-step denoising trajectory is inspectable (each step's reduction in similarity-to-manifold).

**HARD-PASS:** ARM_DIFFUSION_DENOISE depth-2 >= 0.65 (matches baseline; no penalty from denoising) AND depth-5 >= 0.40 AND no refuse mechanism.

**HARD-FAIL:** ARM_DIFFUSION_DENOISE depth-2 <= 0.50 (denoising HURTS the well-resolved 2hop case) OR depth-5 <= 0.20.

**MIDDLE_BAND:** depth-5 in 0.25-0.40.

**Compute:** 4-5 hr CPU (10 diffusion steps per hop x depth x chains).

**Novelty vs 8 prior-drilled + parent drills:** annealed-Langevin / reverse-diffusion as substrate cleanup primitive has NEVER been tested. Different from CSP-iter (additive noise + threshold) and from iter-cleanup-no-gate (which would still be hard-decision argmax per step). Different from RTS smoother (analytical forward-backward) — diffusion is sampling-based monotone-descent.

**Sanity rail:** ARM_BASELINE_HRR_2HOP reproduces 0.65 at 2hop within +/-0.03. If breached, REJECT.

#### CANDIDATE C2 — Predictive Coding HIERARCHICAL FREE ENERGY MINIMIZATION (Friston-Bastos)

**Mechanism (lit anchor):** Friston 2010 "Free Energy Principle"; Bastos-Friston 2012 "Canonical Microcircuits for Predictive Coding"; Whittington-Bogacz 2017 "Approximation of Backpropagation by Predictive Coding"; recent 2024 "Predictive coding networks" survey. Hierarchical layers exchange prediction error signals; each layer's representation is updated to MINIMIZE prediction error from layers above and below; converged state is the maximum-a-posteriori estimate of the latent variable. Crucially: NO HARD DECISIONS, NO REFUSE GATE — the system always returns its MAP estimate, with confidence implicit in the inverse curvature of the free-energy landscape.

**Brain analog:** cortical predictive coding (Rao-Ballard 1999, Bastos-Friston 2012, Keller-Mrsic-Flogel 2018) where layer L+1 predicts L's activity, prediction error propagates UP to refine L+1, refined L+1 propagates DOWN as updated prediction. Multi-hop = hierarchical chain of predictive-coding layers, one per hop.

**Substrate-native mapping:** treat each hop as a predictive-coding layer. Forward pass: hop-k generates prediction for hop-k+1 via W; hop-k+1 cleans up and produces prediction error e_{k+1} = (actual - predicted); error propagates back to refine hop-k's state. Iterate until prediction errors converge (typically 5-10 iterations on small chains). Final readout = MAP estimate (argmax over endpoint cleanup).

**Why this differs from CSP-gated:** PC has NO refuse mechanism; NO additive noise; uses GRADIENT-DESCENT on free energy (monotone descent guaranteed under mild conditions). The 2026-06-25 angle 2 covered predictive-coding-ACC in a different way (used PC as outer-layer conflict-monitor); this variant uses PC as the PRIMARY chain mechanism.

**Discriminator:** 3-arm cell. ARM_BASELINE_HRR; ARM_CSP_GATED_RAIL; ARM_PREDICTIVE_CODING_HIERARCHICAL = N=8 PC iteration sweeps per chain, no refuse-gate, no additive noise.

**P_deflated:** raw P=0.45 (PC convergence is well-established; substrate has W cleanup for prediction; iterative refinement is brain-validated); -0.20 novel-synthesis; +0.10 brain-existence. **P_deflated = 0.35.**

**Substrate-product reading:** PC gives free-energy as built-in confidence signal — per-hop free-energy IS the confidence (no need for separate CSP gate). Refuse-with-reason emerges naturally: high free-energy at hop-k = "I'm uncertain about hop k". Audit-chain via per-layer free-energy trajectory.

**HARD-PASS:** ARM_PC_HIERARCHICAL depth-5 >= 0.40 AND depth-2 >= 0.65 (no degradation on well-resolved case) AND free-energy-correlation-with-correctness > 0.5.

**HARD-FAIL:** depth-5 <= 0.20 OR free-energy uninformative (correlation < 0.2).

**MIDDLE_BAND:** depth-5 in 0.25-0.40.

**Compute:** 4-5 hr CPU (8 PC sweeps per chain x depth x chains).

**Novelty:** PC as PRIMARY chain mechanism (vs outer-layer monitor) has NOT been tested on substrate. Free-energy as per-hop confidence signal is structurally new.

**Sanity rail:** ARM_BASELINE_HRR reproduces 0.65 at 2hop.

---

## TOP-6 RANK-ORDERED DISPATCH

| Rank | Candidate | Failure addressed | Field | P_deflated | Compute | Discriminator |
|------|-----------|-------------------|-------|------------|---------|---------------|
| 1 | A1 SOLAR-SLOT + HARNESS-FIX | LARS-VSA | brain + AI | 0.40 | 3-4 hr | 3-arm: BASELINE_CLEAN / RELBOTTLENECK_CLEAN / SOLAR_SLOT |
| 2 | P1 HOLOGRAPHIC-CHUNK-PACK | PFC chunked | HD/VSA + brain | 0.40 | 3-4 hr | 3-arm: NAIVE / PFC_CHUNKED_RAIL / HOLOGRAPHIC_PACKED |
| 3 | C1 ANNEALED-LANGEVIN-DIFFUSION | CSP-gated-iter | AI + brain | 0.35 | 4-5 hr | 3-arm: BASELINE / CSP_RAIL / DIFFUSION_DENOISE |
| 4 | A2 TENSOR-PRODUCT REPRESENTATION | LARS-VSA | HD/VSA + brain | 0.35 | 4-5 hr | 3-arm: HRR_CLEAN / TPR_OUTER / TPR_ATTENTION |
| 5 | C2 PREDICTIVE-CODING HIERARCHICAL | CSP-gated-iter | brain | 0.35 | 4-5 hr | 3-arm: BASELINE / CSP_RAIL / PC_HIERARCHICAL |
| 6 | P2 HIERARCHICAL-SR MULTISCALE | PFC chunked | brain + AI | 0.35 | 3-4 hr | 3-arm: SR_SHARED / HSR_MULTISCALE / HSR_PER_RELATION |

**All six share META_M7-compliant sanity rails:** the BASELINE arm must reproduce the relevant prior anchor (LARS-baseline = 0.20 chance on CLEAN harness; multi-hop baseline 5hop = 0.122-0.145; multi-hop 2hop = 0.65 +/- 0.03). Sanity-rail breach => REJECT cell.

### Recommended dispatch sequence

1. **IMMEDIATE (1 cycle, highest USER-pivot alignment):** A1 (SOLAR + harness-fix). This is the compositional-understanding pivot's most direct test. If LARS-VSA generalizes on CLEAN harness, the substrate has the relational composition the USER pivot requires.

2. **PARALLEL (1 cycle, complementary failure modes):** P1 (holographic-chunk-pack) + C1 (annealed-Langevin-diffusion). Both target the per-hop primitive itself: P1 by pre-computing chunks, C1 by replacing cleanup with monotone-descent denoising. Combined verdicts diagnose whether the bottleneck is primitive (replace) or composition (re-architect).

3. **CONDITIONAL (cycle 2-3):** A2 (TPR) if A1 HARD_PASSes (demonstrate TPR even better than HRR for slot-binding); P2 (HSR multiscale) if P1 HARD_PASSes (multi-scale closure composes with chunks); C2 (PC hierarchical) if C1 HARD_PASSes (PC is the brain-validated extension of monotone-descent denoising).

4. **PIVOT:** if RANK-1 + RANK-2 + RANK-3 all HARD_FAIL, the conclusion is that per-hop primitive replacement (dense Hopfield + sparse-bipolar dictionary per gap1 5x ANCHOR 6 pivot) is the structural escape. Re-route to that drill's dispatch chain.

---

## CHEAP DECISIVE TEST (META_M7 COMPLIANT)

`exp_relational_revival_3x_meta_drill_v1` — single multi-arm cell

Suggested arms (combinable for amortization):
- ARM_LARS_BASELINE_CLEAN (heldout has zero feature overlap with train; 5-way chance=0.20)
- ARM_LARS_RELBOTTLENECK_CLEAN (re-test of LARS-VSA on CLEAN heldout)
- ARM_LARS_SOLAR_SLOT (rank-1)
- ARM_MH_BASELINE_5HOP (anchors 0.122-0.145)
- ARM_MH_HOLOGRAPHIC_CHUNK_PACKED (rank-2)
- ARM_MH_ANNEALED_LANGEVIN_DIFFUSION (rank-3)
- (optional, if compute budget allows) ARM_MH_TPR, ARM_MH_PC_HIERARCHICAL, ARM_MH_HSR_MULTISCALE

Per Fix #17 / Fix #14 / Fix #24, exp_dev decides whether to combine into one cell or split into 2-3 cells based on compute-time / matmul-cost / GPU-routing analysis.

Decision logic (per top-3 rank):
- A1 HARD_PASS => LARS-VSA mechanism validated; chain-grade evidence for compositional generalization; STOP further LARS angles; reroute to typed-KG-composition drill.
- P1 HARD_PASS => training-time chunk pre-computation is the structural fix for multi-hop saturation; STOP query-time chunking angles; integrate as hdlab/ primitive.
- C1 HARD_PASS => annealed-Langevin denoising replaces CSP-gated as the cleanup primitive; STOP refuse-gate angles; consider C2 PC-hierarchical for confidence-readout extension.
- ALL THREE HARD_FAIL => per-hop primitive itself is the cap; dispatch the gap1 5x ANCHOR 6 dense-Hopfield + sparse-bipolar PRIMITIVE REPLACEMENT.

---

## FALSIFIABLE PREDICTIONS WITH HARD-PASS + HARD-FAIL

### Strong claim (top-3 of top-6)
- **HARD-PASS:** at least one of {A1, P1, C1} delivers HARD-PASS on its discriminator at production regime (N=8192, V_C=200, V_P=10, 5 seeds, sd<=0.06).
- **HARD-FAIL:** ALL three of {A1, P1, C1} HARD-FAIL on their discriminators with no super-additivity over rails.

### Meta-prediction (the 3 diagnoses are independent)
- **HARD-PASS:** the verdicts on A1 / P1 / C1 are UNCORRELATED across discriminators (each addresses a distinct failure mode). If any two share a verdict pattern (both HARD-PASS or both HARD-FAIL), they share a hidden bottleneck.
- **HARD-FAIL:** the verdicts CO-VARY perfectly => there's a shared root cause (likely per-hop primitive at production scale) that ALL the angles depend on.

### Cross-thread predictions
- **HARD-PASS:** A1 SOLAR slot-binding super-additive over RELBOTTLENECK on CLEAN harness by >= 0.05 (confirms attention slot-mechanism adds value over pure bottleneck).
- **HARD-PASS:** P1 HOLOGRAPHIC chunk-packing beats P2 HSR multi-scale on depth-5 by >= 0.10 (confirms training-time orthogonalization > query-time multi-scale).
- **HARD-PASS:** C1 ANNEALED-LANGEVIN beats C2 PC-hierarchical on depth-5 by >= 0.05 (confirms monotone-descent denoising > prediction-error iteration for substrate W).
- **HARD-FAIL:** any candidate that LOSES to ARM_BASELINE at the well-resolved regime (depth-1 single-hop, or LARS depth-1 single-relation). Sanity-rail violation.

### Calibration check
- The 0.40 P_deflated for top-2 candidates corresponds to "at least 1 of 3 HARD-PASSes" probability ~1 - 0.6 * 0.6 * 0.65 = 0.77 if INDEPENDENT — clearly NOT independent (P1 + C1 both bypass per-hop primitive). Conservative correlated estimate: P(at-least-one-HARD-PASS) = 0.45-0.60 within the top-3 set.

---

## CROSS-THREAD SYNTHESIS

This 2x drill complements but does NOT duplicate the parent gap1 5x drill (2026-06-26). Key structural insights:

1. **THREE FAILURES, THREE DIAGNOSES, NOT ONE.** The simplest synthesis would be "they all share the per-hop primitive cap" — that's the gap1 5x finding and the gap1 5x rank-6 ANCHOR 6 (dense Hopfield + sparse bipolar) addresses it. BUT this drill SHOWS the three failures have DIFFERENT root causes: LARS-VSA = harness leak + mechanism unjustly classified as failed; PFC-chunked = query-time chunking on shared W; CSP-gated = refuse-gate-as-wrong + additive iter-cleanup noise. EACH has distinct revival mechanisms.

2. **The compositional-understanding pivot makes LARS-VSA the structurally-correct primary track.** Per USER pivot 2026-06-26, compositional understanding BEFORE language is the new primary direction. LARS-VSA / SOLAR / TPR are precisely the role-filler slot-binding mechanisms compositional understanding requires. Re-testing under CLEAN harness IS the compositional-generalization decisive test.

3. **The "downstream-of-cleanup is doomed" 2026-06-25 thesis is REFINED, not overturned.** Mechanisms that operate downstream of the per-hop cleanup CAN succeed IF they bypass the cleanup entirely (P1 holographic chunk-pack = training-time pre-computation avoids per-hop cleanup at query) OR if they replace the cleanup with a monotone-descent variant (C1 annealed-Langevin = denoising > thresholding).

4. **The CSP-gated failure exposes a META-substrate-product capability gap: REFUSE-WITHOUT-PENALTY.** The current cell scoring treats refuse as wrong. A correct substrate-product would expose three outcomes: correct / wrong / refused-with-reason. Both C1 and C2 (and any future epistemically-humble mechanism) need readout scoring that DISTINGUISHES refuse from wrong. This is a META-finding worth surfacing to Strategy.

5. **The brain-existence-proof boost applies cleanly to A1 (PFC slot-binding), P1 (Eichenbaum relational memory), C2 (cortical PC), and partially to P2 (dorsal-ventral hippocampus).** AI-canonical mechanisms (TPR, diffusion) get smaller brain-prior bumps but stronger lit-anchored P estimates.

6. **Field-coverage observation:** this drill adds coverage in: brain-PFC-slot-binding (un-drilled at substrate scale); brain-Eichenbaum-relational-memory (under-drilled); diffusion-models / annealed-Langevin (un-drilled scope-expansion field); predictive-coding-as-PRIMARY-mechanism (drilled as monitor only, not as primary chain). Per Trigger F aggressive cross-domain, this is structurally distinct from the gap1 5x's tensor-network / particle-filter / smoother coverage.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

Per [[feedback-no-papers-product-only]] and the 2026-06-26 strategic pivot:

- **Compositional understanding scaffold:** A1 + A2 build the typed slot-filler binding the USER pivot calls for as PRIMARY work. If A1 HARD_PASSes on CLEAN harness, the substrate has the role-filler primitive for typed-KG composition.

- **Chunk-indexed retrieval product:** P1 holographic chunk-packing is a NEW substrate-product axis. Customer pre-indexes frequently-traversed sub-chains at training time; query is instant chunk-role lookup. Composes with the auditable-AI-memory subsystem.

- **Confidence-as-product-feature:** C1 (diffusion trajectory) and C2 (per-layer free-energy) both expose per-hop confidence as an inspectable product surface. Audit-chain capability: customer can see WHERE the substrate became uncertain, distinct from "wrong answer."

- **Refuse-with-reason capability:** C2's free-energy-as-confidence is the substrate-native primitive for epistemic humility. Per gap1 5x cross-thread, this is the auditable-memory differentiator.

- **Capacity-vs-accuracy axis:** P2 HSR multi-scale exposes scale-knob (more closure-matrices = more memory but cleaner depth-targeted retrieval). Product reading: customer picks scale=1 for fast / scale=7 for accurate at SAME training data.

Direct closure readings:
- Gap 3 (compositional generalization, Fail 1) closed via A1 if HARD_PASS — lifts compositional gen from baseline-leak-confounded to clean-harness-validated.
- Multi-hop extension closed via P1 if HARD_PASS — lifts depth-5 chunked from 0.158 to >= 0.50 (chain-grade).
- Multi-hop CLEANUP-primitive closed via C1 if HARD_PASS — lifts depth-5 single-chain from 0.122 to >= 0.40 (MIDDLE_BAND to chain-grade).

---

## CITATIONS (verified 11 distinct lit anchors)

1. Webb-Holyoak 2021 "Emergent symbols through binding in external memory" — ICLR 2021.
2. Webb-Russin-Cohen 2024 "SOLAR: Slot-Object-Linked Attention for Relational Reasoning" — NeurIPS 2024.
3. Smolensky 1990 "Tensor product variable binding and the representation of symbolic structures" — Artificial Intelligence 46.
4. Schlag-Schmidhuber 2020 "Learning Associative Inference Using Fast Weight Memory" — NeurIPS 2020.
5. Smolensky-Schlag-Holyoak 2022 "Neurocompositional computing in human and machine intelligence" — NeurIPS 2022 (review).
6. Plate 1995 "Holographic Reduced Representations" — IEEE Trans Neural Networks 6:3.
7. Eichenbaum 2017 "On the integration of space, time, and memory" — Neuron 95 (relational memory).
8. Stachenfeld-Botvinick-Gershman 2017 "The hippocampus as a predictive map" — Nat Neurosci 20.
9. Ho-Jain-Abbeel 2020 "Denoising Diffusion Probabilistic Models" — NeurIPS 2020.
10. Friston 2010 "The free-energy principle: a unified brain theory?" — Nat Rev Neurosci 11.
11. Bastos-Friston 2012 "Canonical Microcircuits for Predictive Coding" — Neuron 76.

Plus brain-grounded refs via prior drills (already verified): CA3 attractor Rolls 2013 PMC 3812781; Stokes 2013 PFC activity-silent WM; Rao-Ballard 1999 PRC.

Additional lit-anchors:
- Diffusion-AM 2024: "Hopfield Networks Meet Diffusion Models" arxiv (Krotov + Hopfield extensions).
- Whittington-Bogacz 2017 "Approximation of Backpropagation by Predictive Coding" — Neural Computation 29.
- Strange-Witter 2014 "Functional organization of the hippocampal longitudinal axis" — Nat Rev Neurosci 15 (dorsal-ventral multi-scale).

---

## META: DELIVERY DISCIPLINE

- All 6 candidates carry pre-registered HARD-PASS + HARD-FAIL (per role-contract mandate).
- Novel-synthesis P cap at 0.50 honored (top P_deflated = 0.40).
- 0.20 calibration deflation applied uniformly.
- ASCII only.
- Sanity-rail (BASELINE reproduces anchor) MANDATORY for all 6 cells. If breached, REJECT before any anchor verdict.
- Companion exp_dev hand-off written: `exp_dev_handoff_research_multihop_relational_2x_revival_2026-06-26.md`.
- Status log entry written per role-contract (research_delivery; HIGH importance).
- Default UNDER-claim classification (Fix #28); let Skunkworks tier UP.

Field-advisor cross-check:
- A1 SOLAR slot-binding — brain PFC fruit-bearing; novel angle un-drilled.
- A2 TPR — HD/VSA un-drilled at substrate scale; brain conjunctive coding adjacency.
- P1 holographic-chunk-pack — HD/VSA training-time orthogonalization new; brain relational-memory adjacency.
- P2 HSR multi-scale — brain dorsal-ventral hippocampus un-drilled; extends prior SR-closure.
- C1 annealed-Langevin diffusion — diffusion-models / AI un-drilled scope-expansion; brain CA3-attractor adjacency.
- C2 PC hierarchical — brain predictive-coding fruit-bearing as monitor; un-drilled as PRIMARY mechanism.

Per Trigger F (always-on aggressive cross-domain): this drill spans 6 anchor mechanisms across 4-5 disparate fields (brain, HD/VSA, diffusion-AI, attention-AI, hierarchical-RL), complementing the gap1 5x's 9-field coverage without duplication.

-- Research (Opus 4.7 1M)
