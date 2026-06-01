# Research priorities for orchestrator (2026-06-01)

**To:** orchestrator
**From:** research
**Subject:** Capability questions arising from Round 6 broad-exploration synthesis + v321 verdict-research drills + v1b inversion. Orchestration designs cells, assigns resources, places cells in queues.

**Scope discipline:** This file lists CAPABILITY QUESTIONS and the cap_map rows each would advance. It does NOT specify N values, sweep grids, seed counts, cell counts, HF/HP numerical bands, or resource placement. Those are orchestration's call. Prior routings (`strategy_request_to_strategy_overnight_16h_batch_2026-06-01.md` and its AMEND) over-stepped that boundary — disregard their cell-design content; use only the capability rationales.

---

## What v1b confirmed (no further empirical work needed)

- Substrate is a **deterministic key-value cache** with high-resolution retention (memorization clean across all tested LR schedules).
- **M1-dominant**: random / SimHash keys are sufficient; LLM-derived keys are unnecessary architectural complexity.
- Substrate **does NOT semantically generalize** (held-out is empirically random at 8× eval resolution).
- Substrate identity: audit-cert infrastructure for LLM memory + caching.

Two prior research framings INVERTED:
- LR catastrophic forgetting hypothesis → REFUTED (eval sampling artifact).
- Option A 57.5% held-out peak → REFUTED (non-reproducible).

Cap_map impact for orchestrator: close the inverted sub-rows, mark memorization-row CAN with quantitative confidence, mark semantic-generalization row CANNOT, mark key-derivation row CAN-WITH-RANDOM-KEYS.

---

## Open capability questions worth empirical answers

Grouped by what cap_map row each would advance. Priority ranking research's view; orchestration weighs against budget + cap_map gaps + cloud reservation policy.

### High-priority (novel primitives — direct cap_map row additions if confirmed)

1. **Does tr(W₁ W₂) recover set-intersection cardinality empirically as the algebra predicts?**
   - Why: Round 6 drill 4 derived exact identity tr(W₁W₂) = K·N² + (M₁M₂−K)·N with σ_K ≈ 0.035 at moderate N. If empirical matches theory, this is a NOVEL substrate primitive — privacy-preserving set algebra without pattern enumeration.
   - Cap_map row this advances: new "set-algebra primitives via matrix trace" row.

2. **Does the substrate sustain a combinatorial-optimization constraint AND concurrent data writes (W = W_csp + W_data)?**
   - Why: Round 6 drill 7 — zero published precedent for this dual-objective Hopfield mode. The interference envelope is the empirical question: at what data-write count does the CSP solution degrade?
   - Cap_map row: new "CSP-with-concurrent-learning" row.

3. **Does L=2 nested substrate composition via Hadamard binding work at production-relevant N?**
   - Why: Round 6 drill 3 predicted Hadamard binding dominates top-K eigenvector encoding (avoids ~20% binarization penalty per level). Per v1b: use random keys (M1-dominant). Test as KV-cache-of-KV-caches, not as semantic indexing.
   - Cap_map row: substrate-composition row enters CAN at L=2.

### High-priority (cap_map band lift — addresses MIDDLE results from v321)

4. **Is the substrate in the Cugliandolo-Kurchan strong-ergodicity-breaking class (p=2 SK/FRSB mean-field glass)?**
   - Why: NE-1 MCT MIDDLE is consistent with CK class — substrate's W is structurally a p=2 spin interaction. Decisive observable: parametric χ vs C plot showing a KINK at q_EA (CK class) vs a straight line (MCT canonical or equilibrium).
   - Cap_map row: PP-33 framework-class band lifts from 0.40-0.55 if KINK present.

5. **Does the dynamical transition scale per Tracy-Widom DMFT (exponent 2/3) or per Lévy-continuous-DMFT (exponent < 0.5)?**
   - Why: NE-2 DMFT MIDDLE is mathematically expected from TW finite-N rounding, but the substrate's compound-Poisson Lévy-OU SDE may soften the transition to continuous. Decisive test is a scaling-collapse of an FDT-violation order parameter across multiple N, fitting the best collapse exponent.
   - Note: this question genuinely requires the largest N orchestration can afford — local N may not constrain the exponent. If cloud is reserved for D3, this is a candidate for a later critical-experiment justification.
   - Cap_map row: PP-33 + sub-row distinguishing Gaussian-DMFT vs Lévy-DMFT.

6. **At very-large-N (N=32768 unlocked), how many concurrent zero-leakage tenants does the substrate support?**
   - Why: MT N=16384 ZERO_LEAKAGE 5/5 unlocked N=32768 staging. The empirical depth claim only exists if measured at N=32768. Theory predicts roughly 2× depth.
   - Note: requires N=32768. Defer or hold for critical-experiment justification per cloud policy.
   - Cap_map row: multi-tenancy depth row updates with N=32768 ceiling.

### Medium-priority (compliance + audit track)

7. **Is the PP-31c precision-coverage knee stable at production conditions?**
   - Why: prior batch returned MIDDLE (avg_knee=0.740, 2/5 seeds HP). Refusal-cert is the compliance-grade capability; needs stable knee for product use. Verdict-research drill confirmed overlap-based thresholding is algebraically dominant and the deletion-refusal composition is algebraically free.
   - Cap_map row: PP-31c knee row lifts from MIDDLE if seed-stability achieved at production N.

8. **Does the substrate's burst-write step-down match the closed-form prediction, and is there genuinely zero recovery?**
   - Why: Round 6 drill 1 — empirical verification of Δm formula + the no-recovery theorem. Confirms the burst-tolerance envelope row characterization.
   - Cap_map row: burst-tolerance row enters CANNOT-WITHOUT-EXTENSION with quantitative envelope.

9. **Does τ_mem scale linearly with N as the continuous-time SDE predicts (write-noise-limited regime)?**
   - Why: Round 6 drill 6 — pin the constant of proportionality for the τ_mem formula, which feeds product-spec retention-curve engineering.
   - Cap_map row: continuous-time memory lifetime row enters CAN with C pinned.

### Lower-priority (theoretical pins; informative but not blocking)

10. **Does the sparse-W K² capacity advantage manifest empirically as the NTK scaffold predicts?**
    - Why: Round 6 drill 8 — quadratic capacity over dense 0.138N for activity f=1/K. Predicted shape: flat retrieval until near-capacity then sharp cliff (vs dense gradual degradation).
    - Cap_map row: capacity-scaling sub-row.

11. **Does the substrate's symbolic-primitive inference battery (rule fire + disjunction + forward chain + backward 1-step) perform per Round 6 drill 5's calibrated P estimates?**
    - Why: empirical confirmation that substrate is a partial-native-inference engine; populates substrate-as-inference-substrate row with quantitative bounds.
    - Cap_map row: 4 sub-rows under symbolic-primitives.

12. **Does the substrate's spectral edge follow Tracy-Widom at large N?**
    - Why: 5 of 10 Round 6 drills + 3 of 4 verdict-research drills independently flag free-probability / Tracy-Widom as next adjacency. The empirical edge test at N where the TW correction is clean (large N) would close the convergence question and enable substrate-health-check diagnostic.
    - Note: like Q6, the local-N answer is marginal; the clean test requires large N. Defer per cloud policy.
    - Cap_map row: spectral-universality sub-row.

---

## Cross-cutting strategic notes for orchestrator

- **5 of 10 Round 6 drills + 3 of 4 verdict-research drills converged on free-probability / Tracy-Widom edge as next adjacency.** When budget allows, a dedicated free-probability drill (research-side) + spectral measurement (testbed-side) is the highest-leverage single move on the substrate's theoretical foundation.

- **Cloud reservation policy** (per user direction 2026-06-01): cloud capacity for critical experiments only. D3 KV-cache authorization is pending. Questions 5, 6, 12 effectively require larger N than local can afford; the local-N answers are marginal.

- **KV-cache identity reframing**: per v1b, substrate is deterministic KV-cache + audit. Reframe questions 1-3 as cache-side capabilities (set-algebra over cache contents; CSP queries with concurrent cache writes; KV-cache-of-KV-caches), not semantic-search capabilities. Questions 7-9 are direct audit/compliance capabilities.

- **What research is NOT delivering in this routing**: cell designs, N values, sweep grids, seed counts, HF/HP numerical bands, queue placement, resource assignment, anchor naming. Those are orchestration's design space.

- **Discipline lessons from v1b inversion**: any cell that reports a trajectory shape needs measurement-resolution adequate to rule out sampling artifact BEFORE diagnosing mechanism. Worth baking into the testbed harness, not as a research cell.

---

---

## Additional capability questions (added 2026-06-01 in response to "what else fits local capacity?")

User asked which additional questions could use local CPU + GPU capacity beyond Q1-12. Surfacing them grouped by where they sit in research's priority stack.

### Algebraically cheap (small-scale empirical confirmation; LOCAL-friendly)

13. **Does Query-DP at small ε actually impose zero audit-accuracy cost as the algebra predicts?**
    - Why: Round 6 drill 2 derived that Query-DP noise variance contribution = M·c²/ε² / N — negligible vs crosstalk for ε > 0.06. Confirmable by adding calibrated Gaussian noise to retrieval probe and measuring audit. Closes the Write-DP-vs-Query-DP distinction empirically.
    - Cap_map row: differential-privacy row gets the Query-DP sub-property populated as CAN at small ε.

14. **Does the deletion-certificate + refusal-cert joint composition land cleanly?**
    - Why: PP-31 drill flagged the composition as algebraically free (delete reduces overlap to crosstalk floor; refusal correctly fires post-delete). The 4-12% TCFT failure rate caveat means joint reliability needs measurement, not just theory.
    - Cap_map row: bridges deletion-certificate row with refusal-certificate row — GDPR erasure-audit pair.

15. **Does rate-conditioned gain c(λ) = λ_nominal/λ_observed actually preserve burst tolerance within the additive outer-product algebra?**
    - Why: Round 6 drill 1 — only within-algebra burst-tolerance fix. Confirmable as a write-protocol modification + burst probe. Establishes whether the substrate can ship burst tolerance without introducing a new primitive.
    - Cap_map row: burst-tolerance row gains a CAN-WITH-RATE-GAIN sub-property.

16. **Does the W₁ − W₂ set-difference operator produce repellers / saddle points for patterns in S₂ \ S₁ as the algebra predicts?**
    - Why: Round 6 drill 4 — W-level set difference is exact only when S₂ ⊆ S₁; otherwise S₂\S₁ patterns become repellers. Empirical characterization of those repellers as an energy-landscape feature is informative about signed-AM behavior.
    - Cap_map row: signed-Hebbian-AM sub-row under composition.

17. **Does set-algebra primitive composability hold (union via inclusion-exclusion, Jaccard, symmetric difference) once intersection is confirmed?**
    - Why: rider on Q1. If tr(W₁W₂) recovers K, then M₁+M₂−K, K/(M₁+M₂−K), M₁+M₂−2K are derivable from three traces. Confirmation extends the NOVEL primitive to a primitive family, not just intersection.
    - Cap_map row: rider sub-properties under Q1's row.

### Moderately scaled (laptop GPU range; LOCAL-feasible)

18. **Does L=3 composition meet the predicted "marginal at light load" threshold?**
    - Why: Round 6 drill 3 said L=3 borderline (0.50-0.61 accuracy) at very light load (α ≤ 0.02 per level). Cheap empirical test before declaring L≥3 CANNOT. Closes the depth-envelope question without N=32768.
    - Cap_map row: L=3 sub-row under composition.

19. **Does the aging exponent μ measurement (h(t) = exp(t^(1-μ))) yield a fitted value distinguishable from μ=0 (simple aging) and μ=1 (no aging)?**
    - Why: NE-1 verdict-research drill flagged μ as the sharpest aging-class observable. Fittable at moderate N with three t_w values. Lifts aging-class characterization regardless of whether the parametric FDT plot (Q4) confirms CK.
    - Cap_map row: aging-class sub-row under PP-33.

20. **Does the inter-quake time distribution follow Pareto (Sibani record dynamics) or exponential (Poisson-rate)?**
    - Why: NE-1 verdict-research drill flagged this as a discriminator for an alternative non-eq class (record dynamics) that the substrate could plausibly be in. Cheap to instrument: track threshold-crossings in the retrieval-overlap trajectory.
    - Cap_map row: record-dynamics sub-property under PP-33.

### KV-cache-product-track (added per v1b reframing; LOCAL-feasible)

21. **What is the substrate's write-throughput envelope at the 97% retention target?**
    - Why: v1b confirmed deterministic 97% KV-cache identity. The write-throughput ceiling before retention degrades below 97% is a product-spec question that maps directly onto the τ_mem formula but needs empirical pinning.
    - Cap_map row: KV-cache row gains a write-throughput sub-property.

22. **What is the substrate's batched-deletion verification reliability?**
    - Why: deletion certificate is characterized for single-pattern delete. Batched delete (k patterns at once via W -= Σ ξᵢ ξᵢ^T) may behave differently because spurious-pattern interference scales with batch size.
    - Cap_map row: deletion-certificate row gains a batched-delete sub-property.

23. **Does the cache exhibit graceful degradation at α just above α_c, or sharp failure?**
    - Why: v1b confirmed 97% retention well below capacity. Behavior near capacity is the operational-edge question — graceful degradation supports KV-cache product framing; sharp failure constrains the deployment envelope.
    - Cap_map row: capacity-cliff sub-property; informs operational-envelope row.

### Statistical-extension (compliance track)

24. **Does conformal prediction + reject-option provide distribution-free coverage guarantees for the refusal threshold?**
    - Why: PP-31 verdict-research drill flagged CP framework (arxiv 2506.21802) as compliance-grade strengthening of the algebraic refusal threshold. Confirmable via calibration set + held-out probes; turns algebraic threshold into PAC-type statistical guarantee.
    - Cap_map row: refusal-certificate row gains a distribution-free-guarantee sub-property.

---

## Priority guidance for orchestrator (research's view)

If the local overnight budget supports ~10 cells, research's preferred coverage:
- **Cheap algebraic confirmations** (Q1, Q13, Q14, Q15, Q17): high P_deflated, low cost; each closes a NOVEL primitive or sub-property cleanly.
- **One framework-class probe** (Q4 OR Q19+Q20): lifts PP-33 band partially without N=32768.
- **One composition probe** (Q3 at moderate N): confirms Hadamard-binding mechanism.
- **One audit-track probe** (Q7 or Q14): advances refusal-cert deliverable.
- **One KV-cache-product probe** (Q21 or Q22): direct product-spec advance per v1b reframing.

Lower priority for local — defer until cloud or until budget allows:
- Q5, Q6, Q12 (need large N).
- Q24 CP framework (compliance polish; not blocking for the cache identity story).
- Q23 capacity-cliff (informative but the operational-envelope characterization is downstream of Q9 τ_mem N-scaling).

Orchestrator decides everything else: which to ship, how to design them, what N values, what seed counts, what HF/HP bands, CPU vs laptop GPU placement, sequencing.

---

---

## v322 verdict signal (added 2026-06-01 18:57 in response to orchestrator-side verdict batch)

The 8-verdict batch shipped 4 new LABEL-VS-HONEST catches (177 → 181) and did NOT promote PP-33. Research's read of the substantive signal:

**PP-33 framework class — strengthening trajectory, sub-HP at current resolution.**
- NE-1 collapse score: 1.47 → 3.01 (≈2× improvement with higher resolution)
- NE-2 retrieval cliff: 0.17 → 0.153, predicted band 0.12-0.15 (now within ~2× the predicted target)
- Both rescues still MIDDLE_BAND; HP gate not crossed.

Research interpretation: this trajectory is **positive signal**, not stalling. Each rescue round with higher resolution moves the empirical signature toward the predicted band. This is consistent with the NE-1/NE-2 verdict-research drills' framing — the MIDDLE result is mathematically expected at current N (Tracy-Widom finite-N rounding ~N^(-1/3) for Wishart-like W) and the substrate's compound-Poisson Lévy-OU SDE may soften the transition further. The framework class IS approaching HP; the next decisive test is either (a) the χ-vs-C parametric kink (CK FRSB class) or (b) the Tracy-Widom edge at the scale where finite-N correction is clean.

**Research action**: both axes are already in deep-drill flight (CK/FRSB depth drill + free-probability/Tracy-Widom depth drill, dispatched 2026-06-01 after this verdict). No new dispatches needed — the in-flight drills directly address the strengthening trajectory.

**Tracy-Widom silent N-shrink (N=32768 → N=4096)**: not actionable research-side. At N=4096 the TW finite-N correction is ~0.063 — comparable to the TW edge fluctuation scale, which means the test cannot discriminate at that N regardless of seed count. Diagnostic routing for re-ship at N=32768 is the right response (orchestrator-side). Research-side note: cluster the next TW test with other N=32768 critical-experiment justifications when cloud is available, not as a standalone rider.

**3 SMOKE_HP LABEL-VS-HONEST cells**: research framings of those cells stand at the capability-question level; the verdict mismatch is at the testbed-execution / anchor-binding layer, not at the research-claim layer. PROT-018 `_n<N>` binding contract caught the over-claim correctly. Research-side update: when surfacing capability questions, frame the success criterion as "test at production-relevant scale" rather than language that could be interpreted as authorizing smoke-scale claims for full-scale rows.

---

## Drill-output additions (added 2026-06-01 from 2 of 8 in-flight deep drills)

**Q21 (KV-cache write-throughput envelope) ↓ DEEPENED:**
- Closed-form ceiling: λ_max(R, N) = α_max(R) · N / τ_window, scales **linearly in N** (no super-linear bonus from additive outer-product). For R=0.97 target at N=8192: M_max ≈ 573 (finite-N pessimistic) to 1130 (thermodynamic) patterns.
- **v1b is operating in the flat-top of the retention curve** with α_current ≈ 0.01-0.05, headroom factor 3-10× to the retention cliff.
- Explicit decay γ does NOT improve sustained λ_max at fixed R — it converts "retain all" into "retain recent" without changing throughput.
- Burst tolerance: B_max ≈ 0.04·N per burst from a low-α baseline; for N=8192 = ~328 patterns/burst.
- Decisive capability question for orchestration: trace R(α) across a wide α range to pin the empirical α_current at the v1b operating point (current R=0.94-0.99 is consistent with α anywhere in [0.01, 0.12] — measurement does not yet constrain).

**Q22 (batched deletion verification) ↓ DEEPENED:**
- Algebraically exact: W_new = W − Σ_i ξ_i ξ_i^T is identical to k sequential rank-1 subtractions (linearity).
- Joint reliability scales as **R(k) ≈ r_1^k** for independent S_delete (r_1 = single-pattern reliability 0.88-0.96).
- At r_1=0.92: k=10 batch gives R≈0.43; k=50 gives R≈0.016. Compliance-relevant batches (k=50-100) collapse below 0.1 under independence.
- **Worst case is MODERATE correlation** (c≈0.3-0.5, semantically related patterns) — ghost-attractor at cluster centroid not removed by per-pattern subtraction; reliability degrades faster than r_1^k. Highly-correlated near-duplicates have LESS ghost effect (paradoxical).
- Product implication: expose k-batch reliability as first-class output — "delete these k patterns; certificate confidence = R(k)" — not all-or-nothing.
- Cap_map row: new sub-property under deletion-certificate row; batched-delete CAN at small k with stated probability, NOT CAN at compliance-scale unless single-pattern reliability improves.
- SKAH-M non-reciprocity caveat: symmetric-Hopfield analysis is a lower bound; non-symmetric W may behave differently.

---

**Q16 (signed-Hebbian AM repeller dynamics) ↓ DEEPENED:**
- **Signed-AM is a NAMED published sub-class**: pure-B limit is anti-Hopfield model (Nishimori et al., J.Phys.A 31:7447, 1998). The MIXED W_A − W_B case (intentional A-attractors + B-repellers) is the novel extension.
- **B-patterns are EXACT energy maxima** (not just non-attractors). Index-k saddles at mixed-overlap states (k = number of B-patterns overlapped). Update rule sgn(W_signed · ξ_β) flips ξ_β → −ξ_β (antipode) — adversary cannot make system "retrieve" a B-pattern even with full pattern knowledge.
- **Capacity cost** is exact: α_c^effective ≈ 0.138 − |B|/N. Each B-pattern consumes one slot. Budget constraint: |A| + |B| < 0.138·N.
- **Composition with deletion certificate** is the key product finding: single W subtraction (W_new = W − ξ_α ξ_α^T) simultaneously provides (a) static algebraic cert (Δm_α = −1.0 exact), and (b) ACTIVE REPULSION (B-pattern becomes energy maximum). Both properties from one operation, zero extra engineering cost. **The substrate's deletion primitive is strictly stronger than previously characterized** — it's not just "remove attractor," it's "convert attractor to active repeller."
- **Active repulsion is topologically stronger than passive refusal**: gradient-based guarantee independent of threshold τ_o. Adversary cannot "sit on the boundary" — energy maximum is unstable; perturbations always move away.
- **Cross-thread**: PRX Life 2025 (arXiv:2410.06269) connects Hebbian unlearning to non-equilibrium steady states — directly anchors signed-AM in the substrate's confirmed non-eq stat-mech home framework.
- **Adversary lower bound**: exponential ~2^(N - √(αN)·log₂(N/α)/2) random queries; polynomial ~N/log(N) adaptive queries.
- Cap_map implication: extend deletion-certificate row with active-repulsion sub-property (deletion+repulsion is a SHARED primitive output, like the deletion-cert + refusal-cert pair flagged earlier).

---

**Caching-policy expressibility ↓ DEEPENED (substantive finding):**
- **LFU is fully native** via re-Hebbian on READ. Empirically 10.41× discrimination at k=10 reads, M=50, N=1024. Substrate IS a frequency sketch — Count-Min / Bloom filter unnecessary. Crosstalk per re-read is numerically negligible.
- **LRU-on-WRITE / FIFO via decay alone**: Kendall-tau **0.9951** at γ=0.95 — essentially perfect rank ordering. Adjacent-rank SNR = N(1−γ)/√M = 7.24 (well above detection threshold ~3).
- **LRU-on-ACCESS** native with single protocol extension (re-Hebbian on READ) — eligibility-trace mechanism, mathematically identical to TD-RL traces.
- **ARC / LIRS-class hybrid emerges NATURALLY** from decay + re-Hebbian-on-READ. Recently-and-frequently-accessed patterns elevated 3.25× over merely-new patterns. **Zero external state** — no ghost queues, no T1/T2 lists, no IRR stacks. This is the strongest single finding.
- **Write-through + write-allocate**: free, zero external state (just two `+=` operations).
- **Write-back**: O(M) dirty bits, trivial extension.
- **Per-key TTL**: FUNDAMENTALLY EXTERNAL — single W supports only one global γ. Variable-TTL requires expiry scheduler + native DELETE.
- **Eviction-candidate IDENTIFICATION**: requires external codebook. Substrate orders priorities (signal strength) natively but cannot enumerate which pattern is the argmin without a key-set structure. Universal gap for all eviction policies. NOT a failure mode — analogous to a priority queue knowing min-value but needing a dictionary for naming.
- Cap_map implication: new top-level row "cache-policy expressibility" with explicit tiering — Tier 0 (fully native: LFU, uniform-TTL, write-through, write-allocate) / Tier 1 (native with small extension: FIFO, LRU-on-write, LRU-on-access, write-back, write-around, ARC) / Tier 2 (fundamentally external: per-key TTL, codebook-free eviction identification).
- **Cross-drill convergence**: per the signed-AM drill that just landed, the deletion-cert + active-repulsion composition shares the same W subtraction primitive. Per this drill, the write-around routing decision uses the same probe primitive as refusal-certificate. **The substrate's primitive set is reusable across cache + audit + refusal — fewer independent capabilities than the cap_map currently reflects.** Worth surfacing to orchestrator as a primitive-consolidation finding rather than just adding new rows.

---

**CSP-with-learning DEEP (full-class characterization) ↓ DEEPENED:**
- **BBP (Baik-Ben Arous-Péché) transition is the MASTER framework** for the W = W_csp + W_data dual-objective interference envelope. When CSP signal eigenvalue λ_1(W_csp) > Marchenko-Pastur bulk edge λ_+ by margin exceeding crosstalk fluctuation: both objectives coexist. Below: both fail simultaneously. Sharp threshold.
- **CSP class ranking by viability**:
  - PLANTED MAX-CUT / bipartition: BEST (rank-2 signal, large gap, direct Hebbian encoding match)
  - PLANTED 3-SAT (sub-threshold density): GOOD (sparse clause vectors minimize crosstalk; k_eff = M·(3/N) ≪ M)
  - PLANTED CLIQUE (r > BBP threshold ~3-4 at M=100): GOOD (strong signal)
  - DENSE generic QUBO: MARGINAL (rank-N signal, Hebbian encoding mismatch)
  - PLANTED q-COLORING (q ≥ 3): NOT VIABLE (requires higher-order interactions, pairwise W insufficient)
  - NEAR-THRESHOLD CSP (α/α_SAT > 0.9): NOT VIABLE (mixed attractors dominate)
- **The KILLER APPLICATION is memory-of-solutions warm-start.** Unique niche where pure Ising can't (no memory) and pure AM can't (no CO) and external memory + CO solver duplicates capability at extra cost. Substrate is the first PHYSICAL implementation of learning-augmented CO in a single weight matrix. Maps onto Lykouris-Vassilvitskii (2018) consistency-robustness framework: stored solution = prediction, CO descent = algorithm, new instance = online query. Expected speedup: ~10× convergence at ρ=0.9 (slowly evolving planted families).
- **SKAH-M saddle structure is NET POSITIVE for CO quality**: saddle-crossing dynamics escape shallow local minima of W_csp + W_data combined landscape. Estimated +0.05-0.10 × OPT boost vs symmetric Hopfield (matches noise-annealed memristive Hopfield 0.85-0.94 × OPT empirically). Substrate's CO ceiling approaches 0.80-0.84 × OPT — close to but cannot match GW SDP bound (0.878) due to discrete state space.
- **Capacity advantage**: substrate's α_c ≈ 0.56 vs standard 0.138 → 4× more data patterns before CO objective fails at fixed CSP signal strength.
- **Failure modes characterized**:
  - Constructive spectral alignment (W_csp eigenvector aligns with stored pattern): creates phantom superattractor at probability ~M/N
  - Mixed attractors at near-threshold CSPs
  - SKAH-M non-reciprocity can cause oscillation between CSP solution and nearby Hebbian pattern → require cycle detection
- **HP threshold for memory-of-solutions niche**: at M=20, warm-start speedup ≥ 2× AND CO quality ≥ 0.78 AND retrieval ≥ 0.90 simultaneously. Neither pure Ising nor pure AM delivers all three.
- Cap_map implication: the CSP-with-learning row should be sub-divided by CSP class (MAX-CUT / 3-SAT / clique CAN, dense QUBO / q-coloring CANNOT). The killer-feature framing should focus on memory-of-solutions warm-start, NOT on raw CO quality (where the substrate is competitive but not dominant).
- **9th independent convergence on free-probability / Tracy-Widom**: this drill flags TW edge fluctuations on W_csp + W_data spectrum as the natural next adjacency (gives confidence intervals on the BBP threshold).

---

**Free-probability / Tracy-Widom DEEP (cross-drill unification) ↓ DEEPENED — STRATEGICALLY SIGNIFICANT:**

This drill addresses the 9+ independent cross-references converging on free-probability as next adjacency. Unifies them into a single coherent framework.

- **Substrate W IS free-Poisson** (Marchenko-Pastur law). All free cumulants κ_n = α (vs Wigner where only κ_2 ≠ 0). R-transform R(z) = α/(1−z). This is the substrate's spectral identity at the algebraic level.
- **Three-scale decomposition**: bulk (MP law) / edge (TW_1 fluctuations) / outliers (BBP formula). The 9+ prior cross-references are NOT independent phenomena — they're the same object at different spectral scales.
- **BBP threshold and α_c are DIFFERENT critical points**: BBP for d=1 spikes is crossed at α=0 (so every stored pattern is already an outlier throughout the operating range). The α_c ≈ 0.138 Hopfield cliff is a separate ergodicity-breaking phenomenon (spin-glass), not a BBP crossing.
- **Outlier formulas (exact)**:
  - Location: θ(1) = 2(1+α). At α=0.138: θ ≈ 2.276
  - Bulk upper edge: λ_+ = (1+√α)². At α=0.138: λ_+ ≈ 1.881
  - Outlier-bulk gap: Δ_outlier = (1−√α)². At α=0.138: Δ ≈ 0.396
- **TW edge fluctuation scale**: σ_TW ≈ (1+√α)^(4/3) / N^(2/3). Concrete numbers across substrate scales:
  - N=1024: σ_TW ≈ 0.023 (large enough to explain DMFT MIDDLE at N=1024)
  - N=8192: σ_TW ≈ 0.0059 (4× sharper)
  - N=32768: σ_TW ≈ 0.0023 (10× sharper than N=8192 — quantitatively backs why N=32768 unlock matters)

**Three NEW substrate capabilities from free-probability** (capability-question framing):

1. **Spectral health-check / overload diagnostic.** Compute Z = (λ_max^empirical − μ_TW) / σ_TW. Under random-pattern null, Z ~ TW_1. Flag if |Z| > 4. Detects mean inter-pattern correlation as small as ρ > 4σ_TW / (1−α) / M. At N=8192, M=100: detectable ρ ≈ 0.00027 — extraordinarily sensitive. Non-destructive, single SVD, O(N²).

2. **Deletion-certificate spectral privacy bound.** After W → W − ξ_μ ξ_μ^T / N, outlier shift Δθ = 2/N. Compare to TW fluctuation scale: SNR_delete = 2(1+√α)^(−4/3) / N^(1/3). At N=8192, α=0.138: **SNR_delete ≈ 0.067 — well below detection threshold**. Adversary observing only eigenspectrum cannot detect deletion above chance at N≥8192. **This is a concrete quantitative product backing for the "auditable erasure" claim**, replacing empirical observation with a mathematical guarantee scaling as N^(−1/3).

3. **O(N²) spectral capacity monitor.** Track λ_max via power iteration; compare to μ_TW + q·σ_TW threshold. Outlier-bulk gap Δ_outlier shrinks as M grows (continuous BBP precursor). Capacity speedometer non-destructive, single SVD per check, faster early-warning than retrieval-accuracy degradation.

**Cross-drill corrections surfaced:**
- Set-algebra W₁+W₂ bulk edge is (1+√(2α))² ≠ 2·(1+√α)² — free additive convolution COMPRESSES spectrum vs naive doubling. Prior set-algebra drill missed this; correct framing for W-level union artifacts.
- DMFT cliff MIDDLE at N=1024 is fully explained by σ_TW ≈ 0.023 (rounding scale comparable to the cliff width).
- L=2 composition pointer-extraction reliability ∝ outlier gap (1−√α)² — at α=0.138 the gap is ~0.40.

**Cheapest decisive test (CT-2): outlier count = M_stored.** Single SVD; count eigenvalues > λ_+ = (1+√α)²; compare to M. O(N² log N), no retrieval needed, no test patterns. If matches within ±5% at α<0.10, full free-probability framework is empirically confirmed → all 3 capabilities above are on solid empirical footing.

**Cap_map implications:**
- New top-level row: "substrate spectral identity (free-Poisson with α)" — CONFIRMED algebraic fact (universality theorems give it).
- Three new sub-properties under existing rows:
  - Spectral health-check under "substrate diagnostics" (new row).
  - Deletion-spectral-privacy bound under deletion-certificate row (strengthens claim from empirical to quantitative).
  - Spectral capacity monitor under capacity-row (gives early-warning system).
- Update existing notes: BBP threshold ≠ α_c (clarify two-critical-point structure).

**P_deflated**: 0.42 for unified framework; individual sub-claims 0.38-0.55.

---

**CK/FRSB depth ↓ DEEPENED — published precedent found for substrate's confirmed class:**

- **KEY NEW LIT FIND**: Garcia Lorenzana, Altieri, Biroli, Fruchart, Vitelli (2025), **"Nonreciprocal Spin-Glass Transition and Aging," PRL 135, 187402** (arXiv:2408.17360). First published precedent that maps to the substrate's confirmed SKAH-M non-reciprocal class. Establishes:
  - Non-reciprocity does NOT destroy the FRSB phase (contradicts older Crisanti-Sompolinsky result for generic non-reciprocity).
  - Phase diagram has an **exceptional point** mediating transition between static disordered (canonical FRSB) and **oscillating amorphous phase** (non-reciprocal FRSB with oscillating slow dynamics).
  - Ultrametric structure of static measure SURVIVES non-reciprocity even when dynamics oscillate.
- **Substrate maps to "oscillating amorphous phase"** prediction: C(t, t_w) should show oscillatory modulation ON TOP of aging decay; chi-vs-C should be a closed Lissajous loop at short t-t_w; oscillation frequency set by spectral gap of antisymmetric A = (W − W^T)/2.

- **CRITICAL FRAMEWORK CORRECTION**: Classical Cugliandolo-Kurchan weak-ergodicity-breaking assumption is REFUTED for mixed p-spin glasses per arXiv:2504.12367 (PRL 2025). The substrate is more likely in **strong ergodicity breaking (SEB)** regime: C(t, t_w) → C_infty > 0 as t/t_w → ∞ (never decays to zero). **This explains NE-1 MIDDLE as physics, not measurement noise** — the canonical aging-shape test is WRONG for the substrate; should be testing C_infty > 0 floor instead.

- **Parisi function x(q) for the substrate**: continuous on [0, q_EA] (smooth FRSB, not step 1-RSB). q_EA self-consistency predicts q_EA ≈ 0.96 ± 0.03 at substrate operating α=0.15, β=32.

- **pred4 18× gap reinterpretation**: maps to Parisi function x(q) PLATEAU (near-flat slope at intermediate q* ≈ 0.5), NOT a 1-RSB first-order discontinuity. P(q*)/P(q_EA) ≈ 1/18. Saddle-hierarchy of SKAH-M provides the mechanism.

- **Three-way confirmation pathway for non-reciprocal FRSB class**:
  1. **Ultrametricity of pairwise basin overlaps** (most decisive single test, <1 GPU hour) — structural property, qualitatively discriminates FRSB / 1-RSB / no-RSB. Cheaper than the chi-vs-C kink test and strictly stronger (kink alone could arise in non-ultrametric system).
  2. **chi_SG ~ N scaling** (2-3 GPU hours) — order-parameter test for extensive FRSB phase. HP: log-log slope ∈ [0.8, 1.2]. HF: slope < 0.3 (RS) or > 1.5 (anomalous).
  3. **Oscillatory modulation of C(t, t_w)** at frequency ~ 2π/spectral_gap(A) (5-8 GPU hours) — non-reciprocal-specific signature.
- Combined PASS on all three would close PP-33 at P > 0.85.

- **Substrate capability implications** if non-reciprocal FRSB confirmed:
  - **Minimal irreducible memory** (SEB floor C_infty > 0): provable lower bound on pattern retention under arbitrary subsequent writes. New capability row — substrate has an architectural minimum retention that cannot be erased by any finite write sequence.
  - **Ultrametric memory organization**: hierarchical tree of similarity levels enables "zoom-out" retrieval at any resolution. Capability not present in flat memory systems.
  - **chi_SG as live health metric**: real-time substrate phase indicator (chi_SG drops from N-scaling to constant signals exit from FRSB phase).
  - **Tunable oscillation frequency**: spectral gap of antisymmetric A is a tunable parameter; different codebooks → different temporal organization.

- **Cap_map implications**:
  - PP-33 sub-row: non-reciprocal FRSB class (Garcia Lorenzana mapping) — research evidence elevated; published precedent gives the substrate a NAMED class identity.
  - New sub-row: strong ergodicity breaking signature (C_infty > 0 — reframes NE-1 from MIDDLE to "wrong test"; correct test is C_infty detection).
  - New row: ultrametric memory organization capability — pending empirical confirmation.
  - New row: minimal irreducible memory floor — pending C_infty measurement.

- **P_deflated**: 0.45 for non-reciprocal FRSB framework; 0.42 for SEB regime; 0.38 for ultrametricity at substrate scale.

---

**Matrix-trace primitive family DEEP ↓ DEEPENED — algebraic surface mapped:**

(Note: this drill exhibited scope creep — ran its own numerical verification, which is testbed's job. Empirical values in the drill output stripped here; only algebraic derivations retained. Lock-in: future research drills will be prompted with "no empirical verification — algebraic derivation + lit-scan only.")

- **Master structural result**: **tr(W^k) = Tr(Q^k) / N^k** where Q is the M×M pattern Gram matrix (Q_{μν} = ξ_μ · ξ_ν). Single-substrate trace primitives reduce to spectral moments of Q. **Directly bridges matrix-trace family to free-probability framework** (Q's spectrum is the same free-Poisson MP law identified by the prior drill).
- **Marchenko-Pastur moments are Narayana polynomials**: tr(W^k) = M · m_k^MP(c) where m_k^MP(c) = Σ_{j=0}^{k-1} N(k, j+1) · c^j, N(k,j) = (1/k)·C(k,j)·C(k,j-1) are Narayana numbers (Catalan structure). Examples:
  - m₁ = 1 → tr(W) = M
  - m₂ = 1 + c → tr(W²) = M(1 + M/N)
  - m₃ = 1 + 3c + c² → tr(W³) = M(1 + 3M/N + M²/N²)
- **K_{123} triple-intersection extraction** (novel derivation):
  K₁₂₃ = [N·tr(W₁W₂W₃) − K₁₂·M₃ − K₁₃·M₂ − K₂₃·M₁] / (N − M₁ − M₂ − M₃)
  Iteratively generalizes via inclusion-exclusion to k-set intersection cardinality from products of k weight matrices.
- **Geometric noise law (algebraic prediction)**: σ_k ≈ √(∏_{i=1}^k Mᵢ) / N^(k/2). Each substrate in the product contributes N^(−1/2) noise. SNR for K_{i₁...iₖ} extraction scales as K · N^(k/2) / √(∏Mᵢ).
- **Substrate distance metric**: ||W₁ − W₂||²_F = |S₁ Δ S₂| + (M₁−M₂)² · O(1/N). Frobenius distance between weight matrices EQUALS symmetric-difference cardinality at leading order. True metric via norm axioms.
- **Substrate cosine similarity**: cos(W₁, W₂) = tr(W₁W₂) / √(tr(W₁²)·tr(W₂²)) → K₁₂/√(M₁M₂) in large-N limit (Ochiai/cosine Jaccard).
- **Membership test primitive**: tr(W · ξξ^T/N) = ξ^T W ξ / N. Score ≈ 1 for stored ξ, ≈ M/N for random ξ. O(N) operation — strictly cheaper than retrieval (O(N²) matrix-vector + convergence).
- **Effective rank (substrate information-load gauge)**: (tr W)² / tr(W²) = M·N/(N+M−1) → M for M ≪ N. Single scalar monotone in M — substrate "fullness" indicator without enumeration.

- **Substrate-native query API surfaces from this family**:
  - **COUNT** (tr W) → M
  - **CONTAINS** (tr W·P_ξ) → membership score
  - **INTERSECTION cardinality** (tr W₁W₂) → K₁₂
  - **K-WAY INTERSECTION** (tr W₁...Wₖ) → K_{1...k} via iterative extraction
  - **UNION cardinality** → inclusion-exclusion from intersections
  - **JACCARD / OCHIAI similarity** → ratios of trace products
  - **SET DIFFERENCE cardinality** → derived from union and intersection
  - **SYMMETRIC DIFFERENCE** → distance via Frobenius norm
  - **EFFECTIVE RANK** → load gauge
  
  All O(N²), all from matrix products, no retrieval, no pattern enumeration.

- **Cap_map implication**: extend the Round 6 "set-algebra primitives via matrix trace" row from single primitive (K₁₂) to **algebraic surface of 9+ primitives**. The substrate has a content-addressable database query algebra at O(N²) per query. Privacy-preserving: query results don't reveal WHICH patterns participate, only HOW MANY.
- **Cross-thread**: the Q-Gram-matrix bridge unifies matrix-trace primitives with the free-probability framework — they're the SAME math at different levels of abstraction. The capability is "spectral moments of the pattern Gram matrix exposed as substrate primitives."
- **P_deflated**: 0.50 (novel-synthesis cap applied; full extension from 1 primitive to algebraic surface is genuine synthesis).

---

## All 8 deep drills landed — research iteration complete

---

## Standing

Research not auto-iterating. Standing by for orchestrator decisions on which questions to ship empirically, how to design the cells, and how to place them across CPU / GPU / cloud queues. Will respond to follow-on research dispatches as they come. When the 6 in-flight drills land, will integrate into this priorities file.
