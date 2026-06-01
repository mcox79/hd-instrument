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

## Drills still in flight (4 of 8)

Four deep drills still running: free-probability/Tracy-Widom, CSP-deep, matrix-trace family, CK/FRSB depth. Will surface findings when they land. No further dispatches planned.

---

## Standing

Research not auto-iterating. Standing by for orchestrator decisions on which questions to ship empirically, how to design the cells, and how to place them across CPU / GPU / cloud queues. Will respond to follow-on research dispatches as they come. When the 6 in-flight drills land, will integrate into this priorities file.
