# Round 6 broad-exploration synthesis — FULL CONTENT (10 drills, 2026-06-01)

**Scope:** ten parallel research drills spanning distinct capability axes of the substrate's design space — deliberately broad, NOT a narrowing into the most-recent-empirical-result topic. All findings are capability characterizations.

**Substrate (generic).** Binary associative memory over {-1,+1}^N (typical N=8192) with additive outer-product Hebbian writes W = Σ_μ ξ_μ ξ_μ^T. Bindings via element-wise Hadamard product; bundling via majority-vote sign(Σ); retrieval via sign(W·query).

---

## HEADLINE CROSS-CUTTING FINDINGS

**A. Three structural hard ceilings are CONFIRMED — algebraically derivable.**

1. **No burst recovery** (drill 1). Writes are additive; burst damage is permanent. Step-down magnitude: Δm ≈ (B/N)·φ(1/√α)/α^(3/2); amplifier grows ~1000× as α → α_c. Safe burst budget: B_safe < (0.138 − M/N)·N before crossing capacity. Only **within-algebra fix is rate-conditioned gain** c(λ) = λ_nominal/λ_observed — keeps the operation in the additive outer-product family. Decay / clipping / orthogonality gating all require new primitives.

2. **Write-DP structurally unreachable** (drill 2). L2 sensitivity Δ_2 = N forces ε_min ∝ N^(3/2). At M=50, N=8192: ε_min ≈ **7.8 million** for 97.5%-bit audit; ε_min GROWS with N — Write-DP is a non-starter at every scale. **But Query-DP is freely reachable**: add Gaussian noise to the retrieval probe (Δ_2 = √N). At ε=1, σ_q ≈ 480 contributes noise variance Mc²/ε² ≈ negligible vs crosstalk for ε > 0.06. **Query-DP at ε=1 has zero audit-accuracy cost.** Algebraic deletion certificate and DP are ORTHOGONAL (not ordered): deletion gives exact removal but leaks via eigenspectrum (rank-1 perturbation → Tracy-Widom); DP bounds statistical inference but is unreachable under Write-DP. Novel composition: deletion + query-DP gives provable removal AND private retrieval simultaneously.

3. **Continuous-time has no stationary regime without decay** (drill 6). Process is matrix **compound-Poisson Lévy-OU**, not pure matrix-OU. Closed-form lifetime: **τ_mem = (1/γ)·log(1 + Nγ/(2λ))** with regimes (a) write-noise-limited τ ~ N/(2λ) when γ << 2λ/N and (b) decay-limited τ ~ 1/γ when γ >> 2λ/N. Critical rate **λ_c = 0.138·γ·N**. Stationary spectrum is Marchenko-Pastur with ratio λ/(γN). Connects directly to NESS / non-eq stat-mech framework class.

**B. Four NOVEL primitives surfaced — no published direct precedent.**

| Primitive | Drill | P_deflated | Status |
|---|---|---|---|
| tr(W₁ W₂) = K·N² + (M₁M₂ − K)·N, exact set-intersection cardinality estimator | 4 | 0.35 | algebraically exact; O(N²) beats enumeration when M > √N; privacy-preserving (reveals HOW MANY, not WHICH) |
| CSP-with-learning via W = W_csp + W_data superposition | 7 | 0.35 | zero published precedent for dual-objective Hopfield; interference envelope: M << α_c·N stable coexistence |
| L=2 nested substrate composition via Hadamard binding | 3 | 0.38 (eigenvector) / higher with Hadamard | end-to-end retrieval 0.88-0.93 per level with Hadamard binding (DOMINATES top-K eigenvector encoding by avoiding 20% binarization penalty); L=3 marginal; L≥4 below useful threshold |
| Arc-cosine NTK algebraic identity for sign-readout outer-product writes | 8 | 0.55 | confirmed algebraic fact; substrate IS kernel regression with the linear/arc-cosine kernel; rank-1 outer products ARE the kernel feature maps |

**C. Three sharp REFINEMENTS to earlier framings (with quantitative content).**

1. **Symbolic-inference primitives** (drill 5): substrate is a PARTIAL native inference engine. Rule application (P=0.72, K/N capacity ≈ 0.138N), disjunction encoding (P=0.65, bundling = approximate disjunction), forward chaining (P=0.58, no native loop detection) are NATIVE. Unification (P=0.22) requires resonator network dynamics (~10-50 iterations, NOT one-shot). Backward chaining (P=0.15) supports only 1-step lookup; multi-step proof search requires external stack management.

2. **Tensor-network compression is STRUCTURE-CONDITIONAL** (drill 9): for random patterns, volume-law entanglement forces D ~ M (no gain over explicit W). For structured patterns with d_eff << M, MPS achieves D ~ √(d_eff/ε), giving 10-1000× compression. MERA further wins for hierarchical L-level libraries (D_MERA ~ d_eff^(1/(2L))). **The 0.138N capacity ceiling and MPS compressibility are ORTHOGONAL constraints** — a substrate can be at capacity AND uncompressible.

3. **Codebook engineering has a TIGHT ceiling** (drill 10): finite-N correction is O(1/N) Gaussian-tight (NOT √N as previously framed). Kerdock IS the binary ETF for N=2^k (achieves Welch bound at M=N²). True ETFs beyond Kerdock at N=8192 with M<<N² are NOT constructible. **ETF advantage over random is 2-5pp at M/N=0.10 (tail-event elimination only); vanishes asymptotically.** Crucially: **0.138N crowding ceiling is energy-function-bound, not codebook-bound** — to raise the ceiling, change the energy function (modern Hopfield / polynomial energy), NOT the codebook. Near the ceiling, Kerdock actually slightly REDUCES capacity (α_c(Kerdock) ≈ 0.118N) via constructive interference.

**D. Sparse-W gives quadratic capacity gain — quantitatively characterized** (drill 8). NTK scaffold valid at M/N < 0.10 (lazy regime); substrate enters feature-learning regime at M/N > 0.15. Sparse activity f=1/K: Gram matrix has block-diagonal-like structure (off-diagonals O(f²)); λ_min(K) larger → tighter Rademacher complexity → train/test gap independent of M in sub-capacity regime. Capacity M_max ~ K²·log(N/K)/log(K) — quadratic improvement over dense 0.138N for K >> 1. Predicted curve: flat retrieval until near capacity, then sharp cliff (vs gradual degradation for dense).

---

## PER-AXIS QUANTITATIVE CHARACTERIZATIONS

### Axis 1 — Bursty / burst-recovery write dynamics

**SDE / sensitivity.** Each Hebbian write contributes a rank-1 outer product with Tr(ξ ξ^T) = N > 0. Pure additive accumulation has no absorbing set; the process drifts to infinity in trace norm. Burst event of B patterns produces:
- Signal term ξ_1 invariant.
- Burst crosstalk variance grows by B/N.
- Permanent step-down: **Δm ≈ (B/N) · φ(1/√α₀) / α₀^(3/2)**, where φ is Gaussian PDF.
- Amplifier (preceding fraction) is ~negligible at α₀ << 0.138 and ~1000× larger at α₀ = 0.138.

**No-recovery theorem.** After burst, continued steady writes only compound the damage: m(t) is monotonically non-increasing because the burst crosstalk is baked into W and each new write adds further interference. Recovery requires SNR increasing, which requires M decreasing — impossible without a forgetting operator.

**Extension candidates ranked by algebraic compatibility:**
| Extension | Type | Burst tolerance | New primitive? |
|---|---|---|---|
| Rate-conditioned gain c(λ) = λ_nom/λ_obs | scaled outer product | reduces burst impact by rate ratio r | **NO** (stays in additive family) |
| Exponential decay (palimpsest) | W ← γW + outer | partial (pre-burst also decays) | YES |
| Synaptic clipping | elementwise clamp | prevents collapse, not recovery | YES |
| Orthogonality gating | inner-product scan + conditional write | reduces correlated-burst redundancy | YES |

**Capability status.** Burst tolerance: CANNOT for pure substrate; CAN-WITH-RATE-GAIN within algebraic identity; CAN-WITH-EXTENSION via decay/clipping (new primitives). P_deflated = 0.20.

### Axis 2 — Differential privacy

**Write-DP sensitivity.** Δ_2 = ‖ξξ^T‖_F = N (addition); 2N (replacement). Gaussian mechanism noise σ = N·c/ε where c = √(2 ln(1.25/δ)) = 5.30 at δ=1e-6. For audit ≥ 95% on full patterns at M=50, N=8192: σ_max_entry ≈ 0.006. Required σ at ε=10: 4341. **Ratio: 780,000×.** Structural incompatibility.

**Write-DP minimum ε.** ε_min(M,N) = N^(3/2) · c · z / √(N · budget) where budget = 1/z² − (M−1)/N. At M=50, N=8192, z=1.96: ε_min ≈ 7.8 × 10⁶. ε_min scales as N^(3/2) — gets WORSE with larger substrate.

**Query-DP sensitivity.** Δ_2(query) = √N. σ_q = √N · c / ε. Noise variance contribution to retrieval field: Var(W·η) = σ_q² · ‖W_i‖² ~ σ_q² · M/N. **DP-noise / crosstalk ratio = M·c²/ε² / ((M-1)·N) → c²/(ε²·N).** Negligible for ε > 0.06.

**Empirical envelope at M=50, N=8192, δ=1e-6:**
| Mechanism | ε=1 | ε=10 | ε=50 | ε=100 |
|---|---|---|---|---|
| Write-DP audit accuracy | ~0% | ~0% | ~0% | ~0% |
| Query-DP audit accuracy | 99.9999% | 99.9999% | 99.9999% | 99.9999% |
| Algebraic deletion | 100% (deterministic) | — | — | — |

**Algebraic deletion vs DP**: ORTHOGONAL. Deletion gives exact weight removal but residual eigenspectrum leakage. DP bounds statistical inference but is unreachable under Write-DP. NOVEL COMPOSITION: algebraic deletion + query-DP simultaneously delivers provable removal + private retrieval. No published analog.

**Capability status.** Write-DP: CANNOT at all useful ε. Query-DP: CAN at ε=1 zero cost. Algebraic deletion: CAN (deterministic). P_deflated = 0.78.

### Axis 3 — Multi-substrate composition (depth-L nesting)

**L=2 construction comparison:**
| Construction | End-to-end accuracy/level | Binarization penalty | Eigendecomp required | Capacity advantage |
|---|---|---|---|---|
| Top-K eigenvector pointer | 0.82-0.88 (binarization ~20% loss compounds) | YES | YES | Linear (same as Hopfield) |
| **Hadamard binding (VSA-style key-value)** | **0.88-0.93** | NO | NO | Linear (tighter by ~2-3× — bundling capacity) |
| Row-block hashing | directory-lookup only | NO | NO | sub-linear |
| Spectral fingerprint Tr(W^k) | certificate-only | NO | NO | N/A |
| Dense modern-Hopfield outer + binary inner | 0.90-0.95 | NO | NO | **exponential outer**, eliminates outer-capacity bottleneck |

**Depth-accuracy scaling (Hadamard-binding):**
- L=1: ≈ 0.95
- L=2: ≈ 0.88-0.93
- L=3: ≈ 0.65-0.75 (marginal; requires α ≤ 0.02 per level)
- L=4: < 0.50 (below threshold without error correction)

**Optimal budget split.** For total parameter budget T = N²_outer + N²_inner with both substrates at load fraction α, optimal split is **f* = α_outer² / (α_outer² + α_inner²)** — 50/50 when loads match. Bottleneck is the smaller store.

**Capability status.** L=2: CAN (Hadamard preferred). L=3: PARTIAL with light loading. L≥4: CANNOT without error correction. P_deflated = 0.38.

### Axis 4 — Set-algebra primitives via matrix trace

**Exact identity.** tr(W₁ W₂) = K·N² + (M₁M₂ − K)·N (exact for i.i.d. random ±1 patterns; ‖ξ‖² = N).

**Cardinality estimator.** K̂ = [tr(W₁ W₂) − M₁M₂N] / [N(N-1)]. Noise σ_K = √(2M₁M₂/[N(N-1)]). At M=50, N=2048: σ_K ≈ 0.035. At N=8192: σ_K ≈ 0.009. Essentially exact at substrate scale.

**Crossover M > √N where matrix-trace beats enumeration:**
| N | Crossover M |
|---|---|
| 1024 | 32 |
| 2048 | 45 |
| 4096 | 64 |
| 8192 | 91 |

**Set operations table:**
| Operation | Formula | Complexity | Exact? |
|---|---|---|---|
| Intersection cardinality K | [tr(W₁W₂) − M₁M₂N] / [N(N-1)] | O(N²) | YES (σ_K < 0.04) |
| Union cardinality | M₁ + M₂ − K | O(N²) | YES |
| Jaccard similarity | K / (M₁ + M₂ − K) | O(N²) | YES |
| Sym-diff cardinality | M₁ + M₂ − 2K | O(N²) | YES |
| W-level union AM (W₁+W₂) | — | O(N²) | NO (double-counts intersection) |
| W-level diff (W₁−W₂) | — | O(N²) | EXACT only if S₂ ⊆ S₁; else S₂\S₁ become REPELLERS / saddles |
| W-level intersection AM | NOT computable from W₁,W₂ alone | — | NO |

**Privacy property.** tr(W₁ W₂) reveals HOW MANY shared patterns, not WHICH — substrate-native overlap audit without disclosure of pattern identity.

**Composition with deletion certificate.** After W_new = W − ξξ^T, tr(W_new · W_ref) differs from tr(W_old · W_ref) by exactly (ξ · ξ_ref)² = N² if ξ_ref = ξ (deletion confirmed) or ≈ N if different. **O(N²) deletion verification certificate.**

**Capability status.** Set-algebra primitives via matrix trace: CAN, NOVEL. W-level set difference: PARTIAL (pure only when S₂ ⊆ S₁). W-level union and intersection as AMs: CANNOT (only at scalar/cardinality level). P_deflated = 0.35.

### Axis 5 — Symbolic reasoning primitives

| Sub-primitive | P(native) | Native? | Mechanism | Key limit |
|---|---|---|---|---|
| Rule application (modus ponens) | 0.72 | YES | rule_vec = ant_role ⊙ A ⊙ cons_role ⊙ C; unbind via element-wise (self-inverse for ±1) | K/N ≈ 0.138N rules |
| Disjunction encoding | 0.65 | YES | sign(A + B) bundling; cos ≈ 0.71 to each | threshold-dependent; degrades at K=100+ |
| Conjunction in antecedent | included with rule app | YES | A_bind ⊙ B_bind element-wise product | noise accumulates from both antecedents |
| Forward chaining | 0.58 | PARTIAL | iterated re-query — Hopfield fixed-point as inference | NO loop detection, NO halting condition; works for acyclic |
| Unification | 0.22 | NO native (resonator) | resonator dynamics to factor predicate ⊙ X ⊙ arg; ~10-50 iterations | requires recurrent architecture extension |
| Backward chaining | 0.15 | NO native | 1-step consequent → antecedent lookup only | NO call stack; multi-step requires external orchestration |
| Occurs check, MGU computation, loop detection | — | ABSENT | — | outside algebraic core |

**Architecture implication.** Substrate maps cleanly onto **parallel RETE matching** (forward-chaining inference with rules stored as Hebbian bundle, fired in parallel via cosine-similarity selection), NOT sequential Prolog-style resolution. Conflict resolution, agenda, halting remain external.

**Capability status.** Symbolic primitives: PARTIAL native engine. Forward inference: CAN. Backward inference: 1-STEP-ONLY. Unification: CAN-WITH-EXTENSION (resonator). Mean P_deflated ≈ 0.46.

### Axis 6 — Continuous-time write dynamics

**SDE class.** dW = -γW dt + ξξ^T dN(t) where dN is Poisson rate λ. This is a **matrix compound-Poisson Lévy-OU process** — NOT Wiener-driven, NOT pure matrix-OU.

**Without decay:** Tr(W(t)) = Tr(W(0)) + λtN — drifts unboundedly. No stationary distribution.

**With decay γ > 0:** stationary measure exists; W_∞ = Σ_μ e^{-γ(t-t_μ)} ξ_μ ξ_μ^T (exponentially weighted sum). Stationary spectrum **Marchenko-Pastur with ratio λ/(γN)**.

**Memory lifetime:**
- General: **τ_mem = (1/γ) · log(1 + Nγ/(2λ))**
- Write-noise-limited regime (γ << 2λ/N): τ ~ **N/(2λ)**
- Decay-limited regime (γ >> 2λ/N): τ ~ **1/γ**
- Crossover at γ ~ 2λ/N

**Critical write rate (capacity collapse):** **λ_c = 0.138 · γ · N**. Above this, W_∞ in spin-glass phase; retrieval fails.

**At critical rate:** τ_mem(λ_c) ≈ 3.6/γ — memory lifetime set entirely by decay constant.

**Product-engineering implication.** Given target retention duration T, solve γ = 2λ/(N·T) (small-α regime) for the closed-form decay parameter prescription. Per-fact retention policy is then a γ-tuning operation. Deletion certificate timing: t_delete = (1/γ)·log(1/ε) gives an algebraic effective-deletion confidence interval.

**Capability status.** Continuous-time operation: CAN-WITH-DECAY. τ_mem characterized exactly. λ_c = 0.138γN is structural ceiling. P_deflated = 0.65.

### Axis 7 — Combinatorial optimization (CSP-with-learning)

**Pure CO (W = W_csp only):** substrate IS a bipolar Ising machine. Standard mappings: MAX-CUT (J = -L/2N), QUBO (J = -Q/4), 3-SAT (rank-3 outer products per clause via WA method). Solution quality on MAX-CUT: 0.70-0.85 × OPT for synchronous descent — competitive but not step-change vs SA / SDP. SKAH-M saddle-hierarchy gives marginal advantage via saddle-crossing dynamics.

**CSP-with-learning (W = W_csp + W_data):** GENUINELY NOVEL — zero published precedent for dual-objective.

**Interference envelope:**
- CO side: W_data contributes near-uniform global energy shift (mean -M/2, fluctuations √(M/N)). CO optimum survives when CSP signal gap >> √(M/N). At M=20, N=1024: √(M/N) ≈ 0.14 — well-planted MAX-CUT (gap O(1)) survives.
- Retrieval side: W_csp contributes O(1/√N) crosstalk for sparse W_csp (CLT), O(1) for dense — dangerous case.
- Stable coexistence: **M << α_c · N** (substrate's effective α may be higher than 0.138 per SKAH-M, extending coexistence ~4×).

**Smoke target.** N=1024, M=20, planted bipartite MAX-CUT, 5 seeds × 20 restarts.
- HP: cut_ratio ≥ 0.80 AND retrieval ≥ 0.90 on ≥ 4/5 seeds.
- MID (modal): one passes, other middling.
- HF: cut_ratio < 0.50 OR retrieval < 0.50 on ≥ 3/5 seeds.

**Capability status.** Pure CO: CAN (standard Ising). CSP-with-learning: CAN (with interference envelope characterized), NOVEL. P_deflated = 0.35.

### Axis 8 — Sparse-coding NTK

**Algebraic identity (Axis 5 of drill 8).** Substrate W = Σ_μ ξ_μ ξ_μ^T / N is EXACTLY kernel regression with linear kernel; rank-1 outer products are kernel feature maps. sign(W·x) readout shifts kernel to arc-cosine K_arc1(x,x') = (1/π)(π − θ). **EXACT algebraic identity — confirmed fact, not novel synthesis.**

**Sparse-W advantage (Axis 2).** Activity f = 1/K patterns have block-diagonal-like Gram matrix (off-diagonals O(f²) — Suzuki et al. JMLR 2025). Larger λ_min(K) → tighter Rademacher complexity. Capacity scaling: **M_max ~ K²·log(N/K)/log(K)** — quadratic improvement over dense 0.138N.

**Generalization gap (Axis 4).** Under sparse coding, gen_gap ~ √(N/(K · λ_min_sparse)) — INDEPENDENT of M in sub-capacity regime. Predicted curve: flat train/test gap until near capacity, then sharp cliff. Dense substrate shows gradual degradation.

**Scope (Axis 3).** Substrate is in feature-learning regime (W drifts O(M/N) from W_0=0 per write); NTK lazy-regime bounds are valid only at M/N < 0.10. Beyond M/N > 0.15, mean-field / replica / SKAH-M scaffolds are correct.

**SG-NTK extension for sign activation (Axis 1).** Standard NTK ill-defined at sign(·); surrogate-gradient NTK (Bacho-Bhatt NeurIPS 2024) replaces sign'(x) with smooth h(x); SG-NTK convergence proven for iterative training. Substrate uses single-shot Hebbian writes; outer-product Hebb is equivalent to one Newton step of linear autoencoder → SG-NTK collapses to fixed kernel.

**Sequencing recommendation.** Axis 5 (algebraic fit) first; if HP, Axis 2 (sparse capacity) is immediate follow-on; Axis 4 (train/test gap) rides on same experiment with held-out set added. All three in one synthetic sweep.

**Capability status.** Arc-cosine NTK identity: CONFIRMED algebraic fact. Sparse-W K² capacity advantage: CAN, quantitatively characterized. Mean P_deflated ≈ 0.46.

### Axis 9 — Tensor-network compression

**MPS bond-dimension bounds:**

For RANDOM ±1 patterns at midpoint cut: entanglement entropy S_cut ~ (M/2)·log(2), forcing D_min ~ 2^(M/2) — exponential in M. Even at M=283 (capacity at N=2048), D_min ~ 2^141. SVD route gives D ~ M/ε for generic matrices — at M=283, ε=0.01: D ~ 28,300 (N/3 — no gain).

For STRUCTURED patterns with intrinsic dimension d_eff: W has rank d_eff; MPS bond dimension **D ≤ ⌈√(d_eff/ε)⌉** (Oseledets TT bound). At d_eff=10, ε=0.01: D ≤ 32 — practical compression.

**MERA advantage for hierarchical libraries:** D_MERA ~ d_eff^(1/(2L)) for L levels — exponential reduction over MPS. At L=4, d_eff=10: D_MERA ≈ 4 vs D_MPS ≈ 32 (8× reduction; ~6× cheaper compute).

**Compression-retrieval trade-off:**
- Structured (rank d_eff): D = d_eff retains all signal; D < d_eff produces sharp-cliff degradation.
- Random (rank M): D = M/2 gives ~5-8% error; D = M/4 ~ 15-25%; D=1 ~ 50% (random).

**0.138N capacity ceiling is ORTHOGONAL to MPS compressibility.** A substrate can be at capacity AND uncompressible (the typical random-pattern case).

**Capability status.** Tensor-network compression: CAN-FOR-STRUCTURED-LIBRARIES (D ~ √d_eff); CANNOT-FOR-RANDOM (volume-law obstruction). P_deflated = 0.32.

### Axis 10 — Hypersphere geometry / ETF codebooks

**Finite-N curvature correction: O(1/N) Gaussian-tight** (not √N). Binary hypercube and continuous sphere are in same universality class for inner-product concentration; correction comes from discretization rounding (inner products quantized to multiples of 2/N).

**Welch bound:** μ_Welch(M,N) = √((M-N)/(N(M-1))). For M = 8N (Kerdock subset): μ_Welch ≈ √(7/8N) ≈ 0.935/√N.

**Kerdock coherence:** |ξ_μ · ξ_ν|/N ∈ {0, 1/√N}. Achieves Welch bound AT M = N² (full Kerdock family); equiangular subset for M < N². **Kerdock IS the binary ETF for N=2^k.**

**Coherence comparison at N=1024, M/N=0.10:**
- Random ±1 max coherence: √(2 log(M)/N) ≈ 0.102
- Kerdock: 1/√N = 0.0313
- Ratio: ~3×

**Retrieval advantage (tail-elimination only):** at M/N=0.10, N=1024 Kerdock beats random by **2-5pp** in retrieval accuracy. Variance ratio σ²_ETF / σ²_random = N·μ² = 1 for Kerdock — **same mean variance as random**; advantage is purely tail elimination.

**Capacity ceiling:** **energy-function-bound, not codebook-bound.** Near capacity, Kerdock SLIGHTLY REDUCES capacity (α_c(Kerdock) ≈ 0.138 · (1 − μ²·M) ≈ 0.118N at M=0.138N) via constructive interference. Random patterns benefit from random cancellations.

**To raise crowding ceiling:** change energy function (modern Hopfield / polynomial energy), NOT codebook. Hu 2024 / Demircigil polynomial-energy direction is the correct path.

**Capability status.** Kerdock codebook: CAN, already used by substrate. Further codebook engineering beyond Kerdock: NEGLIGIBLE-GAIN. Finite-N correction O(1/N): CHARACTERIZED. P_deflated = 0.18.

---

## RECOMMENDED CAP_MAP UPDATES (consolidated, write through orchestrator)

**New top-level rows (4):**
1. **Burst-tolerance / write-rate envelope** — pure substrate CANNOT; CAN-WITH-RATE-GAIN within algebraic identity; CAN with external decay (new primitive). Reference: rate-conditioned gain c(λ) preserves additive outer-product family.
2. **Set-algebra primitives via matrix trace** — CAN, NOVEL primitive. tr(W₁ W₂) exact cardinality estimator. Beats enumeration when M > √N.
3. **CSP-with-concurrent-learning** — CAN, NOVEL primitive. Stable coexistence at M << α_c·N. W = W_csp + W_data dual-objective.
4. **Continuous-time memory lifetime** — CAN with explicit decay; CANNOT without. τ_mem = (1/γ)·log(1 + Nγ/(2λ)) characterized; λ_c = 0.138·γ·N structural.

**New sub-properties (8):**
1. **Sparse-W K² capacity advantage** under capacity-scaling row — CAN, quantitatively characterized.
2. **Arc-cosine NTK algebraic identity** — CONFIRMED theoretical fact.
3. **Tensor-network compression for structured libraries** — CAN bounded by D = √(d_eff); CANNOT for random.
4. **ETF / Kerdock codebook construction** — CAN, but advantage is 2-5pp and asymptotically vanishing.
5. **Symbolic primitive: rule application** — CAN native, K up to 0.138N.
6. **Symbolic primitive: disjunction encoding via bundling** — CAN native.
7. **Symbolic primitive: forward chaining** — PARTIAL (acyclic only).
8. **L=2 nested composition via Hadamard binding** — CAN, end-to-end 0.88-0.93.

**Edits to existing rows (3):**
- **Write-DP at strong ε** — update DP row to CANNOT at ε < 10 with audit ≥ 95%; reframe privacy capability around deletion certificate + Query-DP.
- **Substrate composition row** — add L=2 CAN with Hadamard preferred; L≥4 CANNOT without error correction.
- **Codebook engineering row** — note Kerdock is the ceiling for binary codebooks; further gain requires energy-function change (modern Hopfield direction).

**Capabilities NOT recommended for elevation:** ETF beyond Kerdock; Write-DP; backward chaining beyond 1-step; L≥4 nesting without error correction.

---

## SUMMARY OF NOVEL PRIMITIVES vs CONFIRMED LIMITS

**Novel primitives (4):**
- tr(W₁ W₂) set-cardinality estimator (privacy-preserving)
- CSP-with-learning superposition
- L=2 Hadamard-bound nested composition
- Arc-cosine NTK identity

**Hard structural ceilings (5):**
- No burst recovery without decay primitive
- Write-DP ε_min ~ N^(3/2) (unreachable at every N)
- No continuous-time stationarity without decay
- 0.138N crowding ceiling is energy-function-bound (codebook engineering cannot lift it)
- L≥4 nesting below useful threshold without external error correction

**Capability extensions available but not single-shot primitive (3):**
- Unification via resonator network dynamics (~10-50 iterations)
- Backward proof search via external stack management
- Algebraic deletion + query-DP composition for provable+private retrieval

---

## NEXT-DRILL CANDIDATES (cross-drill convergence)

Five of the ten drills independently flagged **free-probability / Tracy-Widom on substrate eigenspectrum** as the next adjacency:
- Drill 2 (DP): membership-inference leakage via rank-1 perturbation of eigenspectrum
- Drill 3 (composition): spectral gap between top-K eigenvectors and Marchenko-Pastur bulk controls pointer-extraction reliability
- Drill 4 (set-algebra): free-probability spectral analysis of W₁+W₂ double-count artifact
- Drill 6 (continuous-time): stationary Marchenko-Pastur spectrum at λ/(γN), Tracy-Widom edge at criticality
- Drill 7 (combinatorial): spectral gap between W_csp spike and W_data bulk controls interference envelope

This convergence is STRONG signal that free-probability is the right next adjacency — but it is also the SAME adjacency, so dispatching it should be ONE drill not five.

Other distinct next-drill candidates (one per drill that didn't converge on free-probability):
- Drill 1 (bursty): nonequilibrium-stat-mech (burst as NESS perturbation)
- Drill 5 (symbolic): resonator network implementation feasibility study
- Drill 8 (sparse-NTK): replica calculation for feature-learning regime at M/N > 0.15
- Drill 9 (tensor): compressed-sensing phase transitions for structured-library compression
- Drill 10 (hypersphere): modern Hopfield / polynomial-energy direction for raising crowding ceiling

---

## DISCIPLINE NOTES

- All drill prompts used GENERIC substrate descriptions; no project-internal anchor names committed to this file.
- All findings framed as CAPABILITY characterizations; no product positioning / moat / GTM language.
- Pre-registered HP/MID/HF bands accompany every smoke proposal; no batch-level expected-PASS framing.
- This synthesis is exploratory across 10 distinct axes; no narrowing into the most-recent-empirical-result topic.
- LABEL-VS-HONEST: synthesis explicitly distinguishes CAN vs CANNOT vs PARTIAL; numerical bounds are claimed only where derived; lit-scan deflations applied throughout.

Acted-on 2026-06-02: Round 6 + 10 drills processed across v322-v325 cap_map bumps
