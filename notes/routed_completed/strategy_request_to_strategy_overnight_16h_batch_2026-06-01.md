# Strategy request: overnight 16h CPU + 16h GPU batch (2026-06-01)

**To:** strategy
**From:** research
**Subject:** Consolidated overnight batch design — Round 6 follow-ons + v321 verdict-rescue tests
**Status:** PROPOSAL (not authorized — orchestrator approval gates queue_add)

---

## Why now

Two converging research deliverables on 2026-06-01:

1. **Round 6 broad-exploration synthesis** (10 drills, full quantitative content): 4 novel substrate primitives surfaced (tr(W₁W₂) set-algebra, CSP-with-learning, L=2 Hadamard-binding composition, arc-cosine NTK identity), 5 hard structural ceilings confirmed (no burst recovery, Write-DP unreachable, no continuous-time stationarity without decay, energy-function-bound 0.138N ceiling, L≥4 nesting threshold).

2. **v321 cap_map verdict batch landed**: 5 HP / 1 HF / 3 MID. PP-33 (non-eq stat-mech class) did NOT LIFT (band stays 0.40-0.55); MT N=16384 ZERO_LEAKAGE 5/5 unlocked N=32768 staging. Four verdict-research drills (NE-1 MCT rescue, NE-2 DMFT rescue, large-N envelope, PP-31 refusal-cert) characterize the rescue paths for the MIDDLE results and the new capability axes opened by N=32768 staging.

Both research streams converge on the same next-adjacency signal: **5 of the 10 Round 6 drills + 3 of the 4 verdict-research drills independently flag free-probability / Tracy-Widom edge as the highest-yield next axis**. The overnight batch is the right vehicle to test this convergence empirically while parallel-running the other high-P capability characterizations.

User direction (2026-06-01): "let's propose to orchestration a large overnight (16 hours) for cpu and gpu experiments."

---

## Capability axes proposed for this batch (TASK, not cell design)

Strategy + exp_dev resolve cell counts, sweep ranges, seed counts, anchor names, exact HF/HP numerical bands, and queue placement. Research provides the TASK + WHY + CONTRACT + AUTONOMY frame per [[feedback-no-experiment-design-in-prompts]].

### Tier 1 — Highest P × highest gain (recommended for GPU primary, parallel-cell-compatible)

**A. Multi-tenancy depth scaling at N=32768.** WHY: 5/5 zero-leakage at N=16384 unlocks the question "how many concurrent tenants at N=32768?" Theory predicts ~2× depth (P_deflated = 0.47 — highest single-test P). HP criterion (research-flagged, strategy to authorize): 5/5 zero-leakage at T=2× the passing T at N=16384, with adequate gap to nearest wrong tenant. WHAT IT ENABLES IF HP: direct product capability characterization for isolation depth row.

**B. PP-33 framework-class lift via N-scaling collapse.** WHY: DMFT cliff at MIDDLE is mathematically expected via Tracy-Widom N^(-2/3) (Wishart N^(-1/3)) rounding at N=8192, but the substrate's Lévy-OU SDE may make the transition continuous rather than discontinuous (heavy-tailed DMFT). Decisive test: 4-point scaling collapse of an FDT-violation order parameter X(t,t') across N ∈ {4096, 8192, 16384, 32768}, fitting the best collapse exponent x. x = 2/3 → DMFT-TW confirmed; x < 0.5 → Lévy-continuous-transition class. Sharper than q_EA at finite N because X(t,t') gives a dimensionless O(1) jump. WHAT IT ENABLES IF HP: lifts PP-33 band from 0.40-0.55 to 0.65-0.75; closes framework-class question OR confirms Lévy-DMFT direction.

**C. CK strong-ergodicity-breaking discriminator (parametric FDT plot).** WHY: NE-1 MCT MIDDLE is most likely substrate in CK class (p=2 SK/FRSB mean-field glass, P_deflated = 0.40-0.47). Decisive observable: parametric χ vs C plot — KINK at q_EA → CK class confirmed; straight line slope -1/T_eff → MCT canonical; slope -1/T → equilibrium. q_EA measurement (long-time C(t,t_w) plateau at t_w ∈ {tens, hundreds, thousands} write cycles) is the companion test. WHAT IT ENABLES IF HP: framework-class identification (CK class) gives the substrate a NAMED non-equilibrium phase, supports PP-33 lift.

**D. L=2 nested composition at production N (Hadamard-binding).** WHY: Round 6 drill 3 found Hadamard binding DOMINATES top-K eigenvector encoding (avoids 20% binarization penalty per level; ~0.88-0.93 end-to-end at conservative load). Confirm at N_outer = N_inner = 8192 (with optional N=16384 × N=4096 asymmetric variant). HP criterion (research-flagged): end-to-end accuracy > ~0.88 across 5 seeds at conservative inner load. WHAT IT ENABLES IF HP: closes UNSURE row for substrate composition; supports hierarchical-memory product direction.

### Tier 2 — High P, novel-primitive empirical validation (mixed CPU/GPU)

**E. tr(W₁ W₂) set-intersection cardinality estimator.** WHY: Round 6 drill 4 derived exact identity tr(W₁W₂) = K·N² + (M₁M₂ − K)·N with noise σ_K ≈ 0.035 at M=50, N=2048. Predicted SNR ~1448 → HP threshold should be Pearson r > 0.9999 with MAE < 0.5 cardinality units. Cheap CPU test. WHAT IT ENABLES IF HP: empirically confirms a NOVEL substrate primitive (privacy-preserving set algebra, O(N²) cost beats enumeration when M > √N). Cap_map enters NOVEL row.

**F. CSP-with-learning interference envelope.** WHY: Round 6 drill 7 — substrate IS bipolar Ising machine; W = W_csp + W_data dual-objective is NOVEL (zero published precedent). Smoke setup: planted bipartite MAX-CUT in W_csp + M=20 concurrent random Hebbian writes in W_data, N=1024, 5 seeds × 20 restarts. Modal expected outcome is MID (cut quality OK, retrieval OK, but neither HP); explicit MIDDLE_BAND should NOT be pre-framed as failure. WHAT IT ENABLES IF HP: empirical evidence for novel dual-objective capability. Cap_map enters NOVEL row.

**G. Sparse-W K² capacity advantage.** WHY: Round 6 drill 8 — NTK scaffold predicts capacity M_max ~ K²·log(N/K)/log(K), quadratic over dense 0.138N. Predicted curve: flat retrieval until near capacity then sharp cliff (vs dense gradual degradation). Sweep K ∈ {1, 2, 4, 8} (dense → f=1/8 sparse) × M/N ∈ {0.01, 0.05, 0.10, 0.20, 0.30} at N=2048 confirm. Include held-out test set per M checkpoint for the train/test-gap-independent-of-M prediction. WHAT IT ENABLES IF HP: validates sparse-W capacity advantage; opens Path B (sparse codes) as scaling-law direction.

### Tier 3 — Compliance-track + confirmatory (mostly CPU)

**H. PP-31c precision-coverage knee calibration at N=8192.** WHY: Prior batch returned MIDDLE_BAND (avg_knee=0.740, 2/5 seeds at HP); compliance-grade refusal-cert needs stable knee. Verdict-research drill flagged: overlap-based thresholding is algebraically dominant; deletion-refusal composition is algebraically clean and free. HP criterion (research-flagged): knee_std < 0.05, 4/5 seeds show stable knee, avg_knee ∈ [0.65, 0.85]. WHAT IT ENABLES IF HP: compliance-grade refusal-cert + deletion-refusal pair (GDPR erasure audit pair).

**I. Continuous-time τ_mem N-scaling.** WHY: Round 6 drill 6 derived τ_mem = (1/γ)·log(1 + Nγ/(2λ)) with regimes τ ~ N/(2λ) (write-noise-limited) and τ ~ 1/γ (decay-limited). Pin the constant of proportionality across N ∈ {8192, 16384, 32768} for product-spec retention curves. HP criterion: R² > 0.95 on log-log linear fit, C within ±20% across N values. WHAT IT ENABLES IF HP: closed-form γ-tuning prescription for per-fact retention policy.

**J. Tracy-Widom spectral edge at N=32768 (CPU-only).** WHY: 5 Round 6 drills + 3 verdict-research drills converge on free-probability / TW edge as next adjacency. CPU eigendecomposition at N=32768 is ~1h. Test: does λ_max obey Marchenko-Pastur upper edge with TW fluctuation envelope at M/N < 0.05? WHAT IT ENABLES IF HP: validates the substrate's spectral universality class; enables substrate-health-check diagnostic (eigenvalue spectrum) as product feature.

**K. Symbolic primitive battery (rule + disjunction + forward chain + backward 1-step).** WHY: Round 6 drill 5 — substrate is partial native inference engine. Combine smokes S1+S2+S3+S5 in one experiment at N=2048 (shares pattern generation). HP criteria (research-flagged): rule-fire K=8 all-correct gap > 0.3; disjunction K=4 fires from single-antecedent at gap > 0.2; 4-step forward chain T1→T4 in ≤5 iterations cos > 0.25; backward 1-step both hops cos > 0.25. WHAT IT ENABLES IF HP: substrate-as-inference-substrate row populated with quantitative bounds.

**L. Bursty-write step-down empirical.** WHY: Round 6 drill 1 — closed-form prediction Δm ≈ (B/N)·φ(1/√α₀)/α₀^(3/2) and no-recovery theorem. Setup: M=500 steady-rate writes, B=100 burst writes, 1000-step read-only probe; N=2048. HP: drop within 2× theory, m flat at step 1000 vs step 0 post-burst (Δ < 0.005). WHAT IT ENABLES IF HP: confirms burst-tolerance envelope row CANNOT-without-extension; validates rate-conditioned gain as the only within-algebra fix.

### Cells research recommends DEFERRING for this batch (out of scope for 16h overnight)

- **Unification via resonator network** (Round 6 drill 5 Smoke 5D): requires resonator network implementation not yet in substrate codebase. Defer until rule-fire baseline establishes (post-K).
- **ETF/Kerdock vs random retrieval comparison** (Round 6 drill 10 Smoke): P_deflated = 0.18 (already heavily deflated; Kerdock IS the binary ETF; further gain is bounded). Low priority vs Tier 1-2 cells.
- **Tensor-network MPS compression empirical** (Round 6 drill 9): structured-library generator needs design work; orthogonal to the immediate capacity questions.
- **Write-DP attack vector mapping** (Round 6 drill 2): Write-DP confirmed structurally CANNOT at strong ε — no rescue path to test; instead, schedule a Query-DP at ε=1 sanity-check smoke (zero predicted audit cost) as a cheap rider-cell if budget permits.

---

## Contract (what strategy commits to in the batch design)

1. **Each cell has explicit HP / MID / HF bands per design** — no batch-level expected-PASS framing per [[feedback-no-preframe-batch-all-pass]]. Research has flagged HP criteria where it has predictive content; strategy adjusts as needed based on cost / measurement-noise calibration.
2. **Anchor names + sweep grids resolved by exp_dev**, not by research. Research's mapping above is capability-question framing, not anchor-design.
3. **Cells span ≥ 8 distinct capability axes** per [[feedback-keep-research-exploratory-not-narrowing]] — the 12-cell candidate set above already does this (multi-tenancy, framework-class, composition, set-algebra, CSP-with-learning, sparse-W, refusal-cert, continuous-time, spectral edge, symbolic, burst — 11 axes).
4. **Batched cloud execution** per [[feedback-batch-cloud-experiments]]: shared bootstrap / model load across cells where possible. GPU = depth probes (large-N tests, framework-class measurements); CPU = cheap algebraic-identity sweeps, eigenvalue computation, set-algebra trace check.
5. **Pre-PROT-018 anchor-name discipline**: every shipped anchor name must reflect the `_n<N>` binding contract.
6. **No padding** per [[feedback-no-padding-experiments]]: if a cell's prerequisite is missing (e.g., Hadamard-binding implementation, planted MAX-CUT generator), the cell drops from the batch rather than gets padded. Surface to orchestrator if budget would fall short of meaningful coverage.
7. **Per-experiment `--timeout`** per [[feedback-per-experiment-timeout-required]]: smoke wall-time formula applied; >14400s requires review.
8. **ASCII-only in print/verdict_msg** per [[feedback-ascii-only-in-scripts]]; remote dispatch uses verbose tracing per [[feedback-always-verbose-remote-dispatch]].
9. **Snapshot + reconcile before any state-changing cloud-API call** per [[feedback-cloud-launch-snapshot-reconcile]].

---

## Autonomy

Strategy + exp_dev are authorized to:
- Drop any of the 12 candidate cells from the batch (with reason filed) — research does not require all 12 to ship.
- Add cells research did not propose if they advance a cap_map row that strategy judges higher-priority — surface to orchestrator before queue_add.
- Choose GPU type (A100 vs A10G) and queue placement based on cost / wall-time trade-off; research has no preference except that depth-probes should not run on laptop CPU per [[feedback-gpu-first-for-depth-probes]].
- Modify HP / MID / HF numerical bands within the spirit of the capability question — if research's flagged threshold turns out to be measurement-noise-limited, strategy widens the bands; if it's too generous, strategy tightens.
- Sequence cells to share pattern-generation / model-load overhead where dependencies allow.

Strategy + exp_dev are NOT authorized to:
- Pre-frame the batch as expected-PASS (per [[feedback-no-preframe-batch-all-pass]]).
- Authorize the queue_add itself — that gate is the orchestrator's (per [[feedback-obey-user-pause-explicitly]] and the orchestrator-only cap_map-write rule from [[project-multi-session-architecture]]).
- Skip the pre-dispatch checklist (search for project-internal anchor names in any committed dispatch prompts; numerical results in prompt bodies; combination fingerprints).

---

## Budget envelope (research-side estimate; strategy verifies)

Approximate compute cost for the 12 candidate cells:
- GPU (~16h budget): Tier 1 A–D (multi-tenancy + DMFT 4-point + CK parametric + L=2 composition) ≈ 6-9h GPU; Tier 2 F+G (CSP + sparse-W) ≈ 1-2h GPU; Tier 3 I+L (τ_mem + bursty) ≈ 0.5-1h GPU; total ≈ 8-12h GPU. Headroom for cell extension or re-runs on MIDDLE results.
- CPU (~16h budget): Tier 2 E (set-algebra trace) ≈ <30 min CPU; Tier 3 H (PP-31c knee) ≈ 1-3h CPU; Tier 3 J (TW spectral edge N=32768) ≈ 1-2h CPU (large-matrix eig at N=32768 may push to GPU); Tier 3 K (symbolic primitive battery) ≈ 0.5-1h CPU; total ≈ 3-7h CPU. Substantial headroom.

If budget tight, strategy drops in this priority order: K (symbolic, can defer to next batch) → L (bursty, confirms theory but doesn't open new row) → I (τ_mem N-scaling, confirmatory) → J (TW edge, can run separately) → G (sparse-W, scope wider than this batch).

If budget loose, strategy adds: Query-DP ε=1 zero-cost validation (Round 6 drill 2 follow-on) and/or deletion-refusal joint composition (combine PP-31c with explicit delete + re-query).

---

## Expected cap_map updates if batch lands per research's P estimates

(Strategy uses this as priority signal; orchestrator writes cap_map.)

**If Tier 1 mostly HP:**
- PP-33 framework-class band lifts from 0.40-0.55 to 0.65-0.75 (CK strong-EB or Lévy-DMFT class identified).
- Multi-tenancy depth row populated at N=32768 with quantitative depth ceiling.
- L=2 composition row enters CAN at production N with Hadamard binding.

**If Tier 2 mostly HP:**
- 2 new NOVEL primitive rows enter cap_map: tr(W₁W₂) set-algebra + CSP-with-learning.
- Sparse-W K² capacity advantage row enters CAN with quantitative scaling.

**If Tier 3 mostly HP:**
- PP-31c knee calibration row enters CAN at production N (compliance-grade refusal-cert).
- Continuous-time τ_mem row enters CAN with constant pinned.
- TW spectral universality row enters CAN.
- Symbolic primitive sub-rows populated at quantitative levels.

**If most cells MID** (a real possibility — research has not pre-framed as PASS): rescue-path discipline applies per [[feedback-rehabilitation-after-rejection]]; verdict_handler re-reads bands honestly; cap_map decisions honor MIDDLE as informative (not failure).

---

## Provenance + discipline declarations

- Research framings in this routing use only generic substrate descriptions; no project-internal anchor names in any cell descriptions to be passed to exp_dev (this routing file itself uses sub-property labels PP-31a/b/c, PP-33, etc. internally — those are cap_map row identifiers, not committed-to-dispatch-prompts content).
- Per-cell HP/MID/HF bands research flagged are capability-content (e.g., "knee_std < 0.05") not pre-framed expected-PASS.
- This routing does NOT authorize queue_add — orchestrator gates the actual ship.
- Status_log entry kind=research_delivery importance=HIGH to be written by visibility side per [[feedback-for-you-tab-primary-channel]] (research files routing; orchestrator/visibility logs the event).
- LABEL-VS-HONEST: this routing distinguishes research's PROPOSAL (12 candidate cells, with capability rationales) from strategy's AUTHORITY (final cell selection, anchor naming, HF/HP calibration, queue_add). Research has zero authority to ship cells; strategy + orchestrator are the gates.

---

## Cross-references

- `notes/research_round6_10_drills_broad_exploration_2026-06-01.md` — full Round 6 synthesis (10 drills).
- `notes/research_pp8_v1b_and_path_a_synthesis_2026-06-01.md` — prior PP-8 routing reference.
- `notes/research_csp_with_learning_2026-06-01.md` — CSP-with-learning drill output (auto-filed by drill).
- `notes/exp_dev_handoff_research_csp_with_learning_2026-06-01.md` — exp_dev handoff (auto-filed by drill).
- `notes/exp_dev_handoff_research_refusal_certificate_threshold_coverage_2026-06-01.md` — refusal-cert exp_dev handoff (auto-filed by verdict-research drill).
- Cap_map v321 + recent verdict summary (orchestrator-side reference).

Acted-on 2026-06-02: 12-cell overnight batch processed across v322-v324; superseded by 5-wave plan in v325+
