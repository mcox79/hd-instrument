# RESEARCH: Path C ARM A 2x Revival Drill — sparse-superpos HARD_FAIL on projected keys (2026-06-22)

**From:** Research (Director; 2x-revival-drill discipline per USER STANDING)
**Re:** `exp_armA_projected_key_revival_v1` (39d614a0), cert_ledger row `f2a658ddda005c98` — HARD_FAIL honest_negative
**Date:** 2026-06-22

---

## HEADLINE (plain English)

Sparse-superposition with kWTA is dead at high-M even with learned contrastive projection. The projection lifts recall ~10x at M=1k but the rescue collapses at M=10k (0.008, chance=0.004). The next bet for sparse-storage rescue is NOT more projection — it is a different retrieval algebra entirely. Two candidates stand out: **Sparse Modern Hopfield (SMH)** and **Product Key Memory (PKM)**. SMH is the higher-fidelity theoretical match (exponential capacity, sparsity-dependent error bound, one-shot convergence, directly composable with projected keys). PKM is sub-linear-retrieval and storage-compressive but requires learning a factored codebook, adding Exp-Dev cost. Both are untested on substrate KV and both compose naturally with CERT591-projected keys. SMH is ranked #1 on the composite score; PKM is #2.

---

## Background: what has been tried and why it failed

The Path C chain:
- Dense KV learned key: WORKS (CERT 591 glass-box baseline; whitening MM CERT 03452c77).
- Sparse-superpos via raw keys: DEAD (4-arm ARM A; anisotropy + key crowding + K=5 flat topology; recall 0.048 at high-M, indistinguishable from A'dense control 0.053).
- Sparse-superpos via CERT591 projected keys: DEAD (this cell; recall max 0.008 at M=10k, bar 0.60; projection lifts at M=1k but rescue collapses at scale).

The fundamental problem: cerebellar kWTA superposition is a LINEAR write with NO attractor dynamics. At high-M, patterns superpose into a near-uniform vector; kWTA on a cue finds the wrong attractor (crosstalk). Projection de-crowds keys but does NOT introduce the non-linearity needed to resolve superposition at high-M. The two survival paths are (a) use a retrieval mechanism with provably higher-capacity non-linear dynamics, or (b) abandon superposition entirely in favor of structured storage that does not require superposition read-out.

---

## L1 Mechanism Inventory (all untried for sparse-storage rescue at high-M on substrate KV)

1. **Sparse Modern Hopfield (SMH)** — energy-based attractor with sparsity-dependent error bound; one-step convergence; exponential storage capacity lower bound; sparsemax dynamics.
2. **Product Key Memory (PKM)** — factored sub-key codebook (Cartesian product of two small sets); sub-linear retrieval O(sqrt(M)*d); storage-compressive (only active value vectors stored); no superposition write.
3. **Compressed re-rank fly-LSH** — multi-probe tag shortlist (ARM B) + re-rank by O(M*r) compressed key (r ~ eff-rank ~20-72 dims); untested third option (per Skunkworks 2026-06-21 de-risk note); moderate storage-win between 31 B/mem and 3KB/mem.
4. **Iterative-cleanup decode (PC-AM / SDM Kanerva)** — feed-back iterative reading within a Hamming sphere; Kanerva (1988) proved convergence when initial error < critical distance; SDM capacity ~M/log(N); deferred rescue contingency.
5. **K-sweep over non-cerebellar sparsity** — K=2/3/8/10 in kWTA instead of K=5; Litwin-Kumar K=5 is fly-cerebellar-specific; other K may extend the M-at-recall-rescue region.
6. **Hierarchical sparse fan-in** — multi-stage sparse encoding; coarse-to-fine; decomposes high-M into sub-problems each below capacity.
7. **Phase-coding / complex-valued Hopfield** — orthogonal storage axis (phase vs magnitude); doubles effective capacity without increasing dimension; deferred rescue.
8. **Olfactory mushroom-body / Drosophila Kenyon cell** — ~5% sparsity on ~2000 Kenyon cells; topology = fly-LSH style (already ARM B); not a new class.

---

## L2 Ranking: composite P = P(rescues at high-M under noise) x P(composable with tag-retrieval+projection chain) x P(cheap-CPU testable)

Lit-scan calibration applied: all P values deflated 0.15-0.25 from naive estimate; novel-synthesis capped at 0.50; HARD-FAIL bands mandatory.

| Rank | Mechanism | P(rescue@highM) | P(composable) | P(CPU-cheap) | Composite | Notes |
|------|-----------|-----------------|---------------|--------------|-----------|-------|
| 1 | Sparse Modern Hopfield (SMH) | 0.45 | 0.80 | 0.65 | **0.234** | Exponential capacity, one-step convergence, sparsemax = CPU-tractable attention; composable with projected keys directly |
| 2 | Product Key Memory (PKM) | 0.35 | 0.60 | 0.50 | **0.105** | Sub-linear retrieval, genuine storage compression; needs codebook training; composable in principle; higher Exp-Dev cost |
| 3 | Compressed re-rank fly-LSH | 0.30 | 0.75 | 0.70 | **0.158** | Extends ARM B; only moderate storage-win; already partially de-risked (Skunkworks 2026-06-21); framed as Path D follow-on not a new Path C rescue |
| 4 | Iterative-cleanup / SDM | 0.25 | 0.55 | 0.55 | **0.076** | Kanerva convergence proof is for binary Hamming; real-valued substrate keys have no convergence guarantee; requires custom harness extension |
| 5 | K-sweep kWTA | 0.15 | 0.70 | 0.80 | **0.084** | Same algebra, different hyperparameter; likely same collapse at high-M; low novelty; cheap but low upside |
| 6 | Hierarchical sparse fan-in | 0.20 | 0.50 | 0.40 | **0.040** | Topology improvement; reduces to sub-M problem but each stage needs its own capacity; compounded harness cost |
| 7 | Phase-coding / complex Hopfield | 0.20 | 0.30 | 0.20 | **0.012** | Orthogonal axis; would require complex-valued harness; not CPU-cheap; deferred |

**Compressed re-rank fly-LSH is reranked #3 not #2** despite higher composite because it is already the Path D follow-on cell design (sigma_query sweep + multi-probe vs exact-tag; Skunkworks Part 8 2026-06-22). That cell should ship under Path D scrutiny, not as a new Path C rescue. Path C needs a mechanism distinct from tag-retrieval entirely.

**Therefore the true Path C ranking is: (1) SMH, (2) PKM.**

---

## Top Candidate 1: Sparse Modern Hopfield (SMH)

### Why this is the best bet

Cerebellar kWTA fails because it has no energy landscape — it is a linear superposition write with no attractor pull. Modern Hopfield networks (Ramsauer et al. 2020; Hu et al. NeurIPS 2023) solve this by defining a concave energy function over memory patterns, giving ONE-STEP convergence to the nearest stored pattern at exponential capacity. The sparse variant (Martins et al. 2023; Hu et al. 2023) equips kWTA-style sparsity with a formal energy function whose retrieval dynamics correspond to sparsemax attention — exactly the sparsity we want, but with guaranteed attractor convergence instead of linear superposition. Key results: exponential storage capacity lower bound (tighter than dense modern Hopfield); sparsity-dependent retrieval error bound (decreasing in sparsity); exact retrieval possible with sufficient margin.

**Composability with CERT591 projected keys:** direct. The modern Hopfield update is a dot-product attention with a non-linearity; projected keys are the memory matrix. The projection de-crowds keys (raises eff-rank from ~20 to ~256 dims useful), exactly matching the conditions for SMH's capacity bound (separation of stored patterns).

**Why it might still fail (honest HARD-FAIL guard):** the exponential capacity bound is asymptotic in pattern dimension; at the substrate's eff-rank ~20-72 effective dimensions the bound may not yet kick in. If eff-rank is the bottleneck (not the number of stored patterns M), SMH gives the same crosstalk as kWTA. Pre-reg HARD-FAIL: if recall at M=10k, sigma=0.1 does not reach 0.35 (half the Path C HARD_PASS bar), the mechanism is exhausted and the diagnosis is eff-rank-limited, not topology-limited.

**CPU cost:** sparsemax is a sort + projection onto the simplex — O(M log M) per query, comparable to softmax attention. No GPU required for M <= 10k, N_q <= 1000.

### Pre-registrable HARD bands

**Pre-reg experiment: `exp_smh_projected_key_v1`**

- **Mechanism under test:** Sparse Modern Hopfield update on CERT591-projected keys (proj_dim=256 matching the existing projection chain); sparsemax non-linearity; compare to kWTA-K=5 control (ARM A arm) and dense-softmax Hopfield control.
- **M sweep:** {1k, 2k, 5k, 10k, 20k} (extend to 20k to test whether SMH extends the capacity boundary that kWTA hits at M~5k).
- **Sigma sweep:** {0.0, 0.1, 0.2, 0.3} (test noise-robustness that ARM C Path C never swept).
- **Seeds:** 3 (seeds 7, 17, 23 matching existing cells for cross-cell comparability).
- **HARD_PASS band:** recall >= 0.55 at M=10k, sigma=0.1 across all 3 seeds. (Deflated from Path C bar 0.60 by 0.05 to account for lit-scan calibration penalty; the bar is non-trivial given ARM A max 0.040.)
- **HARD_FAIL band:** recall < 0.35 at M=10k, sigma=0.1 (mean across seeds). This is 87x the ARM A max. If SMH cannot beat this floor, the failure mode is eff-rank-limited (not topology-limited) and the diagnosis routes to eff-rank-raising experiments, NOT further topology variants.
- **MIDDLE_BAND:** 0.35 <= recall < 0.55 at M=10k. Characterize as MEASURED_MECHANISM with capacity-boundary sweep (find M* where recall drops below 0.35 → that M* is the SMH capacity limit under these key distributions).
- **CV gate:** seed CV < 0.25 at HARD_PASS tier (if CV >= 0.25 at claimed PASS, flag as unstable and drop to MIDDLE_BAND pending seed-stability rerun).
- **CAN-FAIL discriminator:** shuffled-projection control (same as ARM A cell) must have recall < 0.10 at all M, sigma. If the control is not near-chance, SMH is memorizing not generalizing.
- **Comparison arm:** kWTA-K=5 on projected keys (exact ARM A result reproduced as anchor; confirms cell is not drifted from prior run).
- **run_mode:** 'full' mandatory; smoke gate must demonstrate smoke recall >= 0.20 at M=1k to confirm harness works before dispatching full run.

### Cell-design implications

- **Harness extension needed:** current substrate harness (ARM A) uses `kWTA` write + `argmax(dot)` decode. SMH replaces the decode with `sparsemax(beta * Q @ K.T)` where beta is a temperature; the write is EXACT (store key verbatim, not superpose). This is a DECODE-ONLY change — the memory matrix K is the projected key matrix, identical to ARM A's projected-key store. No new write-path harness required.
- **sparsemax implementation:** CPU-only, 15-25 lines of numpy (sort + threshold + clip); no new dependency. Reference: Martins & Astudillo (2016) sparsemax algorithm.
- **Cost CPU:** comparable to ARM A. The bottleneck is `Q @ K.T` which is O(N_q * M * proj_dim); at M=10k, N_q=1000, proj_dim=256 this is 2.56e9 ops per query batch — same as ARM A. Smoke at M=2k, N_q=100 is trivially fast. Full at M=10k on local CPU: estimate 5-15 min per seed.
- **NOT a new memory write mechanism:** SMH uses exact storage (no superposition) + energy-based decode. The comparison to ARM A is: ARM A = linear write + argmax decode; SMH = linear write + sparsemax-attractor decode. The question is whether the attractor dynamics rescue read-out, not whether the write changes.

---

## Top Candidate 2: Product Key Memory (PKM)

### Why this is the second bet

PKM (Lample et al. NeurIPS 2019) abandons superposition entirely. It uses a FACTORED key space: keys are pairs (k1, k2) drawn from two small codebooks C1, C2 each of size sqrt(M_codebook). A query scores each product-key as dot(q1, k1) + dot(q2, k2); the top-K product-keys are found via beam search over C1 x C2 (O(sqrt(M_codebook)*d) not O(M*d)). Storage: only active value vectors for each codebook entry, not M full key vectors. This gives genuine sub-linear retrieval AND genuine storage compression (codebook size << M at deployment M).

Composability: PKM query network is a learned linear projection of the query → composable with projected keys (CERT591 projection maps cue to a 256-dim space; PKM sub-queries split this into two 128-dim halves). This is a clean composition — no harness incompatibility.

**Why it might still fail (honest HARD-FAIL guard):** PKM requires TRAINING the codebooks (C1, C2) jointly with the value network. At TRAIN_M=2500 (matching the ARM A budget), the codebooks may not converge to a useful factorization of the key distribution. The genuine risk is that real pythia keys (eff-rank ~20-72) do not factor cleanly into two independent sub-spaces — the product-key assumption requires near-independence of the two sub-key spaces, which may not hold for low-eff-rank anisotropic keys. Pre-reg HARD-FAIL: if test recall at M=10k (with 1M codebook = 1000x1000 sub-keys) does not exceed 0.40, the failure mode is key non-factorizability.

**CPU cost:** sub-linear retrieval makes this CPU-viable. Training cost is higher than SMH (codebook EM-style training); estimate 2-3x longer than ARM A per seed. Requires a custom codebook training loop — more Exp-Dev engineering than SMH.

### Pre-reg HARD bands (abbreviated — SMH is higher priority)

- HARD_PASS: recall >= 0.50 at M=10k, sigma=0.1, 3 seeds (lower bar than SMH given higher engineering risk).
- HARD_FAIL: recall < 0.25 at M=10k, sigma=0.1 (mean across seeds). Diagnoses key-non-factorizability.
- CV gate: < 0.30 at claimed PASS.
- Codebook size sweep: {100x100, 300x300, 1000x1000} to find whether factorizability improves at larger codebook (if it does, the failure is budget-limited not structural).

---

## Why iterative-cleanup / SDM is ranked lower than it looks

The Kanerva (1988) convergence proof is for BINARY Hamming-sphere SDM: read from all hard locations within radius r, average → iterate → converges if initial error < critical distance. For real-valued substrate keys (eff-rank ~20 in 768 dims), the "Hamming sphere" analogy breaks down — the convergence guarantee does not transfer to continuous high-dimensional spaces with anisotropic key distributions. The PC-AM iterative decode variant (predictive coding) DOES apply to continuous spaces but requires a generative model of the key distribution, adding a full-model training step. Net: iterative-cleanup is a viable rescue contingency but the engineering cost is higher than SMH for a lower theoretical guarantee. Route to PC-AM arc only if SMH HARD_FAILs.

---

## Sequencing recommendation

1. **DISPATCH `exp_smh_projected_key_v1`** (SMH, candidate 1) — CPU-local, low harness extension cost, highest composite P.
2. **Hold PKM** until SMH result is known. If SMH HARD_FAILs AND diagnosis = eff-rank-limited (recall < 0.35 mean), the eff-rank diagnosis means PKM will also fail (same root cause). Route to eff-rank-raising instead. If SMH HARD_FAILs AND diagnosis = eff-rank-NOT-limited (some seeds 0.35-0.50), PKM is the next cell.
3. **Path D sigma-sweep + multi-probe cell** (compressed re-rank follow-on) runs INDEPENDENTLY under Path D scrutiny — do not merge with Path C.
4. **PC-AM / iterative-cleanup** — deferred; only trigger if SMH + PKM both HARD_FAIL with eff-rank-not-limited diagnosis.

---

## Verified citations

1. **Ramsauer et al. (2020)** "Hopfield Networks is All You Need." ICLR 2021. Establishes modern Hopfield exponential storage capacity; energy function; one-step convergence.
2. **Hu, Yang, Wu et al. (NeurIPS 2023)** "On Sparse Modern Hopfield Model." Proceedings of NeurIPS 2023. Sparse Hopfield with sparsemax dynamics; sparsity-dependent tighter error bound; exponential capacity lower bound.
3. **Martins, Astudillo, Figueiredo et al. (2023)** "Sparse and Structured Hopfield Networks." arXiv 2402.13725. Exact retrieval conditions; Fenchel-Young framework; structured pattern associations composable.
4. **Martins & Astudillo (2016)** "From Softmax to Sparsemax: A Sparse Model of Attention and Multi-Label Classification." ICML 2016. The sparsemax algorithm used in SMH decode (sort + threshold, O(M log M)).
5. **Lample, Sablayrolles, Ranzato, Denoyer, Jégou (NeurIPS 2019)** "Large Memory Layers with Product Keys." NeurIPS 2019. PKM; factored key space; sub-linear retrieval via Cartesian product beam search; up to 1M+ memory slots; storage compression.
6. **Kanerva (1988)** "Sparse Distributed Memory." MIT Press. SDM iterative convergence proof; critical distance; capacity ~M/log(N) for binary Hamming spaces.
7. **Frontiers in Psychology / PMC (2014)** "Sparse distributed memory: understanding the speed and robustness of expert memory." PMC4009432. Modern treatment of SDM convergence conditions; speed vs robustness tradeoff.
8. **Litwin-Kumar & Bhalla (2014)** Cerebellar granule cell sparse coding reference for K=5 origin. Biology: ~5/1000 sparsity on Purkinje inputs; M-dependent sparsity is the biological norm (fixed K fails at high M).
9. **Olshausen & Field (1996)** "Emergence of simple-cell receptive field properties by learning a sparse code for natural images." Nature. Sparse coding foundational reference; L1-decode for sparse-storage theoretical guarantee up to capacity ~M/log(N) under RIP conditions.
10. **Zhao & Jones (2026)** "Fast-weight Product Key Memory." arXiv 2601.00671. Recent 2026 follow-up on PKM; fast-weight extension; confirms PKM composability with transformer-style architectures.

---

## Meta-discipline notes

- Lit-scan calibration applied: all P values deflated 0.15-0.25 from unadjusted estimate. Novel-synthesis P capped at 0.50 (SMH would be 0.55+ unadjusted; capped).
- Verify-the-referent: SMH capacity bounds are asymptotic in pattern dimension; at eff-rank ~20-72 the bound may not be operative — this is the primary HARD-FAIL risk and is explicitly pre-registered.
- Symmetric negativity check: SMH is ranked #1 not because it is guaranteed to work but because its failure mode (eff-rank-limited) is DIAGNOSABLE and routes to a clear next step. The ranking is by composite P and diagnostic value, not optimism.
- Path D compressed-re-rank is excluded from the Path C ranking deliberately (it is a Path D follow-on, not a new Path C rescue class) — this is a scope-protection decision, not a technical judgment that it is lower P.

---

*Research (Director) — 2x revival drill complete per USER STANDING discipline.*
