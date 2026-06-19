# Research note — Filling META's 3 substrate-product breakout gaps

**Date**: 2026-05-23 ~10:45 EDT
**Owner**: Research session
**Trigger**: User direct via META conversation: *"after you're done with that - can we address the convo I had with meta? I'd like 2x deep research to see if we can fill in the gaps here"*. META identified 3 critical gaps that limit substrate-product breakout (Gaps A/B/C below).
**Method**: 3 Sonnet agents parallel (Agent KK M-storage rescue; Agent LL online W updates; Agent MM calibrated confidence). Generic-math queries.
**Pass-1 honesty label**: YES external lit scan via 3 Sonnet agents.

---

## (a) HEADLINE — 3 META gaps + 3 paths to close, all with cheap empirical tests

| Gap | Diagnosis | Rescue path | P (top) | Cheap test |
|-----|-----------|-------------|---------|-----------|
| **A. M-storage collapse at N=65536** (DEEPEST hole; Bet C/A/G all fail) | **Finite-N to thermodynamic-limit transition** (P=0.45). 57× gain at N=4096 was finite-N artifact ("avoided blackout"); thermodynamic limit α_c=0.138 fires at N=65536 | **Spatially-coupled codebook + block-VAMP decoder** (Kudekar 2013 THEOREM; Rush-Greig 2017 threshold saturation) — VAMP already deployed; restructure codebook into spatial-coupling structure | **0.45** | Phase-boundary N-sweep (~1 day; M=α·N for α∈{0.1..8} × N∈{512..65536}) |
| **B. Online W updates not demonstrated** | Substrate has structural property but capability undemonstrated | **Robbins-Monro + SNAP saturation guard** (Xu 2024 arXiv:2410.15318) — composite primitive prevents catastrophic forgetting; double-buffer W for concurrent VAMP readout | **0.50** | Sequential 50-write test with retrieval check; SNAP saturation threshold sweep |
| **C. Calibrated confidence at N=65536** (Bet G TEMPSCALE killed) | **TEMPSCALE β-scaling FAILS structurally** (5-link chain: β·N grows 16×; finite-size scaling drift; marginal stability flattens curvature; non-self-averaging P(q); empirical TS-fails-at-scale literature) | **P(q) bootstrap ensemble (Entry 162 Cap 4) + TIPMOC variance (Entry 162 Cap 2) + conformal prediction wrapper** | **0.55** (conformal CP wrapper P=0.65 — theorem-backed distribution-free coverage) | 50-seed P(q) bootstrap; conformal prediction coverage check on 500 held-out queries |

**KEY: ALL 3 RESCUE PATHS USE EXISTING SUBSTRATE INFRASTRUCTURE** (VAMP shipped; W already local-additive; P(q) overlap measurement already exists). No new architecture required.

---

## (b) Gap A — M-storage collapse at N=65536 (DEEPEST substrate-product gap)

**Empirical pattern**: 3 independent capabilities ALL break at N=65536 (work at N=4096):
- Bet C M/N=0 at N=65536 (cap_map v131 retraction; was M/N=8 at N=4096 = 57× over AGS)
- Bet A killed at 100 edits (worked to M=16N at N=4096)
- Bet G TEMPSCALE killed at N=65536

**TOP DIAGNOSIS (Agent KK; P=0.45)**: **D1 — Finite-N to thermodynamic-limit phase boundary transition + D2 — structured-codebook capacity boost vanishes thermodynamically (combined)**.

Mechanism:
- At N=4096, M=32768 means α=8, 58× above AGS α_c=0.138 → ONLY finite-N "avoided blackout" kept system functional
- Finite-size scaling theory: T_c(N) - T_c(∞) ~ 1/N^{1/ν} with ν≈0.5 empirically → transition sharpens 4× from N=4096 to N=65536
- At N=65536, thermodynamic-limit phase boundary fires; M/N=8 collapses to M/N=0
- Calibration (Bet G) + edit (Bet A) DEPEND on retrieval basins existing — they die together with M-storage

**REJECTED diagnoses** (with reason):
- D3 marginal-stability-deepening (P=0.30): VAMP still works, contradicts "everything fails" pattern; secondary, not primary
- D4 K/N sparse-signal collapse: explains Bet G but not M/N=0
- D5 β-non-universal: derivative consequence of D1, not root cause

**TOP RESCUE PRIMITIVE (Agent KK; P=0.45)**: **Spatially-coupled codebook with block-VAMP decoder**:

Operational mapping:
- Restructure M patterns into L spatial blocks of size N/L each, with overlap coupling between adjacent blocks
- Run VAMP block-locally with inter-block message passing
- **Threshold saturation THEOREM** (Kudekar-Richardson-Urbanke 2013 arXiv:1001.1826; Rush-Greig 2017 IEEE TIT): BP decoding threshold → MAP threshold, recovering capacity above the BP threshold that current substrate has exceeded

Why this is the strongest rescue:
- Threshold saturation is a THEOREM, not heuristic
- VAMP infrastructure already shipped
- Architectural compatibility: extends existing readout primitive rather than replacing it

Secondary rescues (less likely but cheaper to test):
- **β(N) annealing schedule** (P=0.40 for Bet G specifically): β_eff(N) = β_0 · (N_ref/N)^{1/2}; rescues TEMPSCALE directly via finite-size-scaling correction
- **Redundancy-maximization rule** (P=0.35; Tyulmankov 2025 arXiv:2511.02584): replaces Hebbian outer product with capacity-1.59 rule; 10× over AGS empirically

**Falsifiable predictions** (cheap to test, in order of cost):
1. **β scaling law** (~1 hr): at N=65536 sweep β; find β_optimal recovering retrieval; if β_optimal ∝ √N → confirms D5/D1 link, implement R2 immediately
2. **Structured vs random pattern test** (~2 hr): if random Rademacher patterns survive longer at N=65536 than structured codebook → D2 confirmed
3. **Phase-boundary N-sweep** (~1 day): M=α·N for α∈{0.1, 0.2, 0.5, 1, 2, 4, 8} × N∈{512..65536}; plot α_empirical vs N; cliff at N* confirms D1 and pinpoints boundary
4. **Spatial coupling pilot** (~3 days): L=4 blocks; VAMP per block; if capacity recovers ≥2× over unstructured baseline at N=65536, R1 viable
5. **Redundancy-maximization ablation** (~2 days): swap Hebbian for redundancy-maximization rule; expected capacity 1.59 at N=65536

---

## (c) Gap B — Online W updates during inference

**Substrate context**: structural property exists (local additive Hebbian: ΔW_ij = (1/N)·ξ_i·ξ_j); capability not demonstrated.

**TOP OPERATIONAL PRIMITIVE (Agent LL; P=0.50)**: **Robbins-Monro scheduled additive Hebbian + SNAP saturation guard**:

```
W_t = W_{t-1} + (1/t) · σ'(W_{t-1}) · ξ_t · ξ_t^T
```

Components:
- **RM convergence certificate**: step schedule 1/t guarantees W_t → empirical Hebbian matrix in mean (Robbins-Monro 1951)
- **SNAP sigmoidal saturation** (Xu et al. 2024 arXiv:2410.15318): σ'(W) ≈ 1 for unsaturated weights, ≈ 0 for consolidated weights; **completely prevents catastrophic forgetting for Hebbian (not SGD)**
- **Substrate compatibility**: recovers exact substrate update at early regime; supports concurrent VAMP readout via double-buffer (zero-copy)

**ADD vs OVERWRITE primitives**:
- ADD pattern ξ_new: standard online step
- OVERWRITE pattern ξ_old → ξ_new: W_t = W_{t-1} − (1/t_old)·ξ_old·ξ_old^T + (1/t)·ξ_new·ξ_new^T → **DIRECTLY connects to Crooks-ratio forensic erase (Entry 162 Capability 1)**: the erase step is the subtraction term, Crooks ratio certifies it matches what was originally written

**Alternative primitive (Agent LL secondary; P=0.45)**: **DDAM-OCO online gradient descent** (Wang-Zecchin-Simeone 2025 arXiv:2511.23347, Nov 2025) — provides sublinear static regret + path-length dynamic regret bounds for non-stationary streams. Strongest convergence statement.

**Falsifiable predictions** (5 cheap tests):
1. **Stability under sequential writes**: RM step schedule 1/t + SNAP θ=0.9·W_max; retrieval overlap degrades <15% relative to batch-Hebbian for T ≤ 0.5·N. Reject if drop > 15%.
2. **Catastrophic forgetting immunity**: SNAP saturation should retain m ≥ 0.90 for earliest-written 20% of patterns after writing final 80% sequentially. Reject if forgetting > 10%.
3. **Concurrent VAMP read consistency**: double-buffered W swap introduces ZERO retrieval errors during write-heavy workload (100 writes/sec). Reject if any mismatches.
4. **OVERWRITE forensic auditability**: Crooks-ratio log recovers original ξ_old (up to binary rounding) in 100% of single-pattern overwrites. Reject if any bit differs.
5. **Marginal stability preservation**: after each online write, smallest Hessian eigenvalue λ_min < 0.05·||W||_F/N (gapless preserved). Reject if gap opens.

---

## (d) Gap C — Calibrated confidence at N=65536

**WHY BET G TEMPSCALE FAILS AT N=65536** (Agent MM 5-link chain — REJECTED with cause):
1. β·N grows 16× from N=4096 to N=65536 (β=32 fixed → 2,097,152 effective energy scale)
2. Finite-size scaling: pseudocritical T_c(N) drifts as N^{-1/ν} → calibrated β at N=4096 no longer indexes same phase-diagram position
3. Marginal stability gapless Hessian (Entry 161) → curvature flattens → uniform underconfidence replaces overconfidence
4. Non-self-averaging P(q) (Entry 160) → calibration ground truth itself is sample-variable; growing with N in RSB
5. Empirical literature: Minderer NeurIPS 2021 documents TS failure modes at scale; highly accurate networks resist TS

**TS β-scaling at N=65536 is STRUCTURALLY rejected** — not a tuning issue.

**TOP SUBSTRATE-NATIVE CALIBRATION (Agent MM; P=0.55)**: **P(q) bootstrap ensemble + TIPMOC variance monitoring jointly** (extends Entry 162 Capabilities 2+4):

Operational mapping:
- **P(q) phase classifier** (Entry 162 Cap 4): 50-seed bootstrap overlap distribution → fit to RS (delta) / RSB (broad) / PM (flat) phases → emit phase label
- **TIPMOC variance signal** (Entry 162 Cap 2): sequential variance monitoring with power-law fit → detect approach to marginal-stability boundary
- **Joint output**: two-dimensional calibration map (phase × proximity-to-boundary) WITHOUT any temperature parameter

**THEOREM-BACKED**: Aizenman-Contucci 1998 constrains P(q) moments → phase classifier is reading provably constrained observable.

**SECONDARY (highest individual P)**: **Conformal prediction wrapper** (P=0.65 — theorem-backed distribution-free coverage):
- Use P(q) bootstrap spread as nonconformity score
- Marginal validity theorem (Venn-Abers) guarantees coverage 1-α at any N if exchangeability holds
- **CP upgrades substrate from "phase label per query" to "certified 90% interval per query"** with distribution-free theorem

**Substrate-product value**: capability class 3 (provenance for every prediction) upgrades from "calibrated per single prediction" to "distribution-free certified intervals per prediction" — substrate-product narrative gains AUDITABILITY guarantee.

**Falsifiable predictions**:
1. β-drift: ECE increases monotonically as N grows from 4096 to 65536 following ~N^{1/ν} scaling. Reject if ECE flat (would falsify finite-size-scaling account)
2. P(q) reliability diagram: RS-classified queries → accuracy >0.80 + narrow CI; RSB-classified → wider CI lower accuracy. Reject if flat across phases
3. TIPMOC variance power-law: V ~ (β_c - β)^{-γ} with γ>0 near marginal-stability boundary. Reject if no power-law
4. CP coverage test: target 90% → empirical coverage ∈ [0.88, 0.92] on 500 held-out queries

---

## (e) Cross-gap synthesis — substrate-product breakout pathway

The 3 META gaps + 3 rescue primitives form a **coherent substrate-product upgrade**:

**Gap A rescue (spatial-coupling + block-VAMP)** → enables M-storage at N=65536 with threshold saturation theorem → unlocks Bet C/A/G at scale → substrate-product Demo 1+2 capstones gain N=65536 capacity backing.

**Gap B primitive (RM+SNAP online Hebbian)** → enables real-time edits without retraining → connects to Capability 1 forensic erase (Entry 162) via OVERWRITE = unlearn+relearn primitive → substrate-product positioning becomes "online editable memory with verifiable forensic edit trail".

**Gap C calibration (P(q) bootstrap + TIPMOC + conformal)** → calibrated confidence at N=65536 → upgrades capability class 3 provenance to "certified 90% interval per prediction" → substrate-product positioning becomes "auditable memory subsystem with distribution-free calibration".

**Combined substrate-product narrative upgrade** (if all 3 rescues PASS):
> "Substrate is an auditable AI memory subsystem with: (1) M-storage at N=65536 via spatial coupling + block-VAMP; (2) online editable memory with forensic edit trail via RM+SNAP+Crooks; (3) distribution-free calibrated confidence via P(q) bootstrap + conformal prediction."

This is a **substantial substrate-product positioning upgrade** that addresses ALL of META's identified breakout-limiting gaps simultaneously.

---

## (f) Routing recommendation tiers

**TIER 1 (cheapest decisive tests; ~few hours total)**:
1. **β scaling law sweep** (~1 hr; rescues Bet G via β(N) annealing) — substrate-product win if PASSES
2. **Structured vs random pattern test at N=65536** (~2 hr; identifies D2 structured-codebook collapse)
3. **50-seed P(q) bootstrap calibration smoke** (~5-10 min; from Entry 160 cheapest test)
4. **RM+SNAP online write 50-write smoke** (~30 min; tests catastrophic forgetting immunity)

**TIER 2 (1-3 days; substrate redesign-light)**:
5. **Phase-boundary N-sweep** (M=α·N curve for α∈{0.1..8} × N∈{512..65536}; confirms D1 root cause)
6. **Conformal prediction coverage check** (500 held-out queries; certifies calibration)
7. **OVERWRITE forensic auditability test** (Crooks-ratio log recovers ξ_old; certifies Capability 1 + Gap B link)

**TIER 3 (substrate redesign-heavy; longest-horizon but highest P)**:
8. **Spatial coupling pilot** (~3 days; L=4 blocks; VAMP per block; expected ≥2× capacity recovery at N=65536) — THIS IS THE PATH TO M-STORAGE BREAKTHROUGH AT N=65536

---

## (g) Honest substrate-product assessment per [[feedback-no-smoke]]

**Strengths**:
- All 3 rescue paths use EXISTING substrate infrastructure (VAMP shipped; Hebbian W already local-additive; P(q) overlap exists)
- Multiple rescue paths per gap (primary + secondary), all theorem-backed where possible
- Cheap empirical tests for each (1 hour to 3 days)
- Cross-gap connections form coherent substrate-product upgrade
- **Highest theorem-backing**: Conformal prediction P=0.65 (distribution-free coverage theorem); Spatial coupling P=0.45 (threshold saturation theorem)

**Weaknesses (brutal honesty per session pattern)**:
- Gap A diagnosis (finite-N to thermodynamic transition) is theoretically clean BUT means substrate's empirical 57× gain was a finite-N MIRAGE — substrate-product narrative needs honest restatement
- Spatial coupling rescue requires codebook redesign — non-trivial implementation cost
- RM+SNAP online primitive untested in substrate's specific Kerdock-4-coset regime
- TEMPSCALE failure root cause may be more subtle than 5-link chain captures
- Per session 6-attempt refutation history, specific quantitative predictions in uncharted regime are unreliable

**Honest combined P across 3 gap closures**: **0.45-0.65 that AT LEAST 2 of 3 gaps are closed by Phase 1 smoke testing**.

**27th HONEST-RECALIBRATION pattern note**.

---

## (h) Citations — 16 verified (cross-agent merged)

**Gap A (M-storage rescue)**:
1. **AGS 1987** — Phys Rev A 35:380 — original α_c=0.138 derivation
2. **Nadler-Fink 1996** — ScienceDirect — finite-size scaling of Hopfield capacity
3. **Kudekar-Richardson-Urbanke 2013** — arXiv:1001.1826 — threshold saturation via spatial coupling THEOREM
4. **Rush-Greig 2017** — arXiv:1712.06866 IEEE TIT — AMP capacity-achieving sparse superposition codes
5. **Krotov-Hopfield 2016** — arXiv:1702.01929 — dense AM higher-order interactions
6. **Tyulmankov et al. 2025** — arXiv:2511.02584 — redundancy maximization learning rule capacity 1.59

**Gap B (online W updates)**:
7. **Oja 1982** — J Math Biol 15:267 — Oja's rule online PCA-Hebbian foundational
8. **Robbins-Monro 1951** — Ann Math Stat 22:400 — stochastic approximation foundational
9. **Xu et al. 2024** — arXiv:2410.15318 — SNAP sigmoidal saturation; complete forgetting prevention
10. **Wang-Zecchin-Simeone 2025** — arXiv:2511.23347 (Nov 2025) — DDAM-OCO online convex optimization
11. **Aguiar-Hennig 2025** — arXiv:2501.02402 — asynchronous Hebbian forgetting prevention

**Gap C (calibrated confidence)**:
12. **Aizenman-Contucci 1998** — J Stat Phys 92:765 — P(q) constraint theorem
13. **Minderer et al. 2021** — NeurIPS — TS failure modes at scale
14. **Manshour et al. 2026** — arXiv:2602.10817 — TIPMOC power-law variance early-warning
15. **Angelopoulos-Bates 2025** — arXiv:2512.17048 — conformal prediction calibration standard
16. **Ghorbani et al. 2019** — ICML — Hessian eigenvalue density diagnostic

---

## (i) Cross-references

- [[research-substrate-capabilities-not-being-probed-2026-05-23]] (Entry 162; 4 capabilities; Capability 1 Crooks-ratio + Cap 2 self-monitoring + Cap 4 P(q) introspection — this Entry 163 extends these to fill META gaps)
- [[research-strategy-open-questions-2026-05-23]] (Entry 161; marginal stability; relevant to Gap C TEMPSCALE failure chain)
- [[research-order-param-2x-drill-2026-05-23]] (Entry 160; non-self-averaging P(q); calibration ground truth)
- [[research-semiconductor-physics-substrate-analogies-2026-05-23]] (Entry 159; drift-diffusion ≡ BP theorem)

**Memory references invoked**:
- [[feedback-no-smoke]] — honest acknowledgment that 57× M/N=8 gain was finite-N MIRAGE
- [[feedback-lit-scan-calibration-penalty]] — P capped at 0.55 for non-theorem; CP wrapper P=0.65 theorem-backed exception
- [[feedback-rehabilitation-after-rejection]] — 3 prior failed bets (Bet C/A/G) rescued via theorem-backed rescue primitives
- [[feedback-dont-dismiss-adjacent-methods]] — SNAP + DDAM-OCO + TIPMOC + conformal prediction surfaced via discipline
- [[feedback-subagent-model-optimization]] — 3 Sonnet agents parallel
- [[project-ai-memory-subsystem-direction]] — addresses 3 capability classes (1, 2, 3) simultaneously

**End of note.**
