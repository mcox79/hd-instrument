# HIGH-PRIORITY TESTS — v324 SYNTHESIS + DEEP-DRILL CONSOLIDATION (2026-06-02)

**From:** Research session
**To:** Orchestrator / Strategy
**Trigger:** User asked for next high-priority tests across remote-CPU / remote-GPU / cloud, after v324 cap_map confirmations + 6 ultrametricity revival drills + 4 deep "combination" drills landed.
**Discipline:** capability questions only; no cell designs (strategy + exp_dev own that); algebraic + lit-scan only in drill bodies; minimize cloud spend.

---

## 0. EXECUTIVE: WHAT'S NEW SINCE PHASE-3 PRIORITIES

**v324 empirical confirmations (now substrate-physics ground truth):**
- Free-Poisson spectral identity κ_n(W) = α — Marchenko-Pastur null distribution is KNOWN, not predicted
- 9-primitive matrix-trace algebraic surface PASS — substrate-native query API operational
- L3 composition + signed-AM both PASS — composition + active-repulsion both work

**6 revival drills:** "ultrametricity HARD_FAIL" was measurement-mismatch (wrong probe for substrate's dynamical phase). Substrate is in CK-aging or Garcia-Lorenzana oscillating-amorphous phase (PRL 135, 187402 — citation corrected). Garcia-Lorenzana mechanism is the LEADING candidate, not the failed one.

**4 deep "combination" drills:**
1. **COMBO-2 (p=4 + L3 + signed-AM):** unlocks Negative-Knowledge Trees, Hierarchical Refusal Certificates, Counterfactual Abduction over Negative-Knowledge Trees. Per-level fidelity 0.96-0.99 at L3, addressable triples 10¹⁸-10²¹.
2. **COMBO-1 (p=3 + implicit Gram-solve + κ_3):** architecture lock — audit primitive lives on M×M Gram side, NOT N×N retrieval operator. NEW substrate-product killer feature: **audit sensitivity scales as α^(p-1)**. At p=3 with α=2, drift-detection is **4× more sensitive at fixed compute**.
3. **COMBO-3 (matrix-trace × deletion × κ_3 unified API):** 5-method audit API is an **ALGEBRAIC THEOREM**, not engineering convention. All 9 primitives + κ_3 update + CNDC + cert read from shared Krylov buffer {ξ, Wξ, W²ξ}. **Honest correction: cost is O(N²) per delete for trace class** (not O(N)); O(N) for bilinear class only.
4. **Real-time learning regime:** substrate's CK-aging IS the native real-time-forgetting primitive. 4 product capabilities batch-trained NNs fundamentally cannot offer.

---

## 1. STRATEGIC RE-FRAMING

The substrate is now a **streaming-write algebraic memory with a confirmed dynamical phase, a free-Poisson spectral identity, a 9-primitive matrix-trace API surface, and 4-9 killer features** (5 original from 2026-05-26 + 4 new from real-time learning drill). The product story is no longer "does it work" but "how do we ship the audit + retention + drift adaptation + counterfactual features in priority order."

**New killer features unlocked by deep drills (extends 5 from 2026-05-26):**

6. **Per-fact retention dial via α_μ write magnitude** (real-time learning). Each pattern carries an "importance" α_μ ∈ [0.5, 2.0]; high α deepens basin → exponentially extends CK-aging timescale. No batch NN equivalent: retention is dataset-frequency, not per-fact knob.
7. **Live κ_3 audit trail per-write** (real-time learning + COMBO-3). Every write timestamps a spectral-health fingerprint; suitable for SOC2/HIPAA "verify integrity over time" claims.
8. **Drift-without-retraining** (real-time learning). Input distribution shifts; substrate adapts via dynamical class. No optimizer re-warmup, no replay buffer.
9. **Negative-Knowledge Trees + Hierarchical Refusal Certificates + Counterfactual Abduction over forbidden subtrees** (COMBO-2). Substrate certifies it has never told the model to associate <PII> with <decision-class>; refused queries produce 3-level audit cert with anti-pattern + repulsion score.

Plus a 10th candidate (deflated): **continuous-time replay-free consolidation** via aging on the marginal manifold.

---

## 2. RESOURCE-ROUTED TEST PRIORITIES (5 WAVES)

Locked constraints from user: remote GPU has <16GB VRAM (N≤8192 production-N envelope); smoke-first sequencing for CK FULL; minimize cloud spend.

### WAVE 1 — REMOTE CPU (fire NOW, all parallel, no gates)

**Goal:** decide 3 architecture commitments + 4 killer-feature gates in <2 hours total wall.

| Test | Wall | Decides |
|---|---|---|
| **Q-F3 cophenetic correlation** on existing overlap matrix | <1s + setup ≈ 5 min | 3 killer features (multi-tenant tree, coarse-to-fine retrieval, cluster-organized memory) |
| **Q-F1 dynamical M_dyn smoke** (R=200, 1 seed, M_dyn at t=16,128,1024) | 1 hr | Orients Wave 3 — substrate's true phase (CK pure / Garcia-Lorenzana / static-list) |
| **κ_3 Hutchinson smoke at N=8192** (5000 complex probes) | 1 hr | Validates spectral-MAC primitive (4.2% δα sensitivity per Phase-2 spec) |
| **Q-C5 cosine-gate τ recalibration** (single 1-D sweep over τ ∈ [0.78, 0.92]) | <2 min | GDPR-grade deletion-cert non-repudiation lift |
| **NEW: streaming-write aging baseline** (3 regimes: λ_w τ_α ∈ {0.1, 1.0, 10.0}, M=2048 at N=4096, measure retain_t(τ) curve, κ_3(t), spectral density) | 2 hr | Validates CK-aging-as-forgetting; HARD-PASS = Regime A flat ≥ 0.95, B power-law exponent ∈ [-0.4, -1.0], C stretched-exp β ∈ [0.3, 0.7]; HARD-FAIL = A and C identical (refutes CK class for streaming) |

**Wave 1 total wall:** ~2-3 hr if parallel across CPU cores. All five tests independent.

### WAVE 2 — REMOTE GPU FIRST WAVE (fire after Wave 1 lands, independent of Q-F1 smoke)

**Goal:** validate the COMBO algebraic theorems at production N=4096-8192 in one pass per test bundle.

| Test bundle | What it answers | HARD-PASS bands (from drill outputs) |
|---|---|---|
| **COMBO-1 BUNDLE: Q-A1 p=3 polynomial DAM + implicit Gram-solve + κ_3 audit at N=4096, M ∈ {2N, 4N, 8N}** | Architecture lock — audit on M×M Gram side; production decision on dreaming-bypass | HP1 MMD <0.02 retrieval vs dense; HP2 κ_3(G) within 5% of M/N; HP3 write wall-time linear-in-M (slope ≤1.3); HP4 SNR_emp/SNR_pred ∈ [0.85, 1.15] |
| **COMBO-3 BUNDLE: matrix-trace × deletion × κ_3 unified-API smoke at N=4096** | 5-method API uniformity as algebraic theorem; shared Krylov buffer reuse | HP1 \|Δ_i^direct − Δ_i^closedform\| < 1e-10 for all 9 primitives; HP2 κ_3 update <1e-6; HP3 CNDC composition <1e-10; HP4 cert signature <1e-10; HP5 matvec count ≤5 |
| **Q-C2 Marchenko-Pastur HC at N=4096, 8192** with v324-confirmed free-Poisson null | Spectral-audit production readiness; resolves v323 smoke FAIL | Z_clean within ±3σ_TW of free-Poisson predicted edge |
| **Q-B1 heteroassociative directed chain depth-3 + cert** | Reasoning-chain primitive; orthogonal to capacity work | depth-3 fidelity ≥0.80; exact algebraic deletion of any single directed binding (zero residual) |

**Wave 2 total wall:** ~6-10 hr GPU. All four bundles independent.

### WAVE 3 — REMOTE GPU DYNAMICAL BUNDLE (GATED ON Q-F1 SMOKE PASS)

**Goal:** decisive phase identification — CK pure vs Garcia-Lorenzana oscillating-amorphous overlay. SKIP if Q-F1 smoke HARD-FAILS (saves 8-12h GPU).

| Test bundle | What it answers | HARD-PASS bands |
|---|---|---|
| **COMBO-4 FULL: CK dynamical M_dyn + C(t,t_w) + X(C) FDT-ratio + Preisach Pred-5 sub-loops** at N=4096-8192, R=2000, 5 seeds, 6 t_w decades | Substrate's dynamical signature; non-equilibrium-stat-mech row 45-60% → 60-75%; oscillating-amorphous sub-class confirmation if Ĉ(ω) peak appears | M_dyn ≥ 0.82; X(C) piecewise-constant (R² ≥ 0.95) AND continuous-monotone fit R² <0.95; aging exponent μ ∈ [0.70, 1.00]; AND/OR Ĉ(ω) finite-ω peak SNR > 3 (substrate-novel oscillating-amorphous signature) |
| **Q-F4 saddle-overlap triplet test** (gradient-ascent from minima to nearest saddle, then triplet UM on saddle overlaps) | Substrate-novel SKAH-M saddle-hierarchy signature ("audit at saddle depth") | mean_ratio_saddle ≥ 0.85 (vs mean_ratio_minima = 0.583) |

**Wave 3 total wall:** ~8-12 hr GPU IF Q-F1 smoke PASSes. ZERO if SKIP.

### WAVE 4 — REMOTE GPU SECOND WAVE (gated on Wave 2 COMBO-1 PASS)

**Goal:** category-changing capacity + composition lifts; signed-AM tree unlock.

| Test bundle | What it answers | HARD-PASS bands |
|---|---|---|
| **COMBO-2 BUNDLE: p=4 polynomial DAM + L3 + signed-AM at N=4096-8192, M_A=64, M_B=64** | Parity-symmetric category change (4M× capacity); Negative-Knowledge Tree + Hierarchical Refusal Cert + Counterfactual Abduction over forbidden subtrees | end-to-end L3 fidelity_A ≥ 0.85; B-repulsion rate ≥ 0.95; cross-tree parity contamination ≤ 0.05 |
| **Q-A3 L=2 cross-layer composition** (p=3 outer / p=2 inner at N=8192) | 5.7B addressable pairs envelope | per-level fidelity ≥0.93; end-to-end L2 ≥0.85 |
| **STREAMING PREDICTIONS 2-4 (gated on Wave-1 streaming baseline PASS):** Brand incremental Gram refresh cadence; κ_3 monitor detection latency vs FP rate; controlled drift kernel detectability via κ_3 deviation | Validates 4 real-time-learning killer features at production N | streaming Brand-update matches batch-Gram within ±0.02 accuracy for K ≤ M writes; κ_3 monitor detects injected anomalous write within W ≤ 50 writes at 3σ; controlled drift kernel ε ≥ 1e-3 rad/write detectable within W ≤ 100 writes |

**Wave 4 total wall:** ~10-15 hr GPU.

### WAVE 5 — CLOUD (single batch, single bootstrap — JUSTIFIED by GPU VRAM <16GB)

**Goal:** N=32768 production-N spectral primitives + audit-API smoke that cannot fit on remote GPU.

**SINGLE bundle — `unified_n32768_v1`:** one Lambda instance, one model load, all observables in one shot.

| Test inside the bundle | What it adds at N=32768 |
|---|---|
| Q-D1 spectral primitives (σ_TW measurement, BBP threshold) | σ_TW ≈ 0.0023 (vs 0.0059 at N=8192) — sharper edge, more sensitive primitive |
| κ_4, κ_6 fingerprint extraction | 1D → 3D fingerprint, cryptographically harder to forge |
| Deletion-cert Z-ratio at production N | ~3.6-5.1σ confidence (vs ~2.0σ at N=8192) — production-grade GDPR audit |
| COMBO-3 unified-API smoke at N=32768 | Validates the 5-method API uniformity theorem at production scale |
| COMBO-1 implicit Gram-solve + κ_3 at N=32768 (if cap_map row needs ratification) | Architecture lock at production scale |

**Pre-register HARD bands per cell** per the no-padding lock; per-experiment `--timeout`; batch ALL cells through ONE bootstrap.

**Wave 5 total wall:** ~6-10 hr Lambda single-instance. Cost ~$10-15 (single A100 at ~$1.50/hr).

**Cloud-deferred (do NOT propose now):** Q-D2 DG(m,r) higher-r ETF — only needed when product-tier knob is being commercialized.

---

## 3. SEQUENCING SUMMARY

```
NOW    Wave 1 (Remote CPU, ~2-3 hr, all parallel)
       ├── Q-F3 cophenetic correlation
       ├── Q-F1 dynamical M_dyn smoke
       ├── κ_3 Hutchinson smoke at N=8192
       ├── Q-C5 cosine-gate τ recalibration
       └── NEW: streaming-write aging baseline

+3 hr  Wave 2 (Remote GPU, ~6-10 hr, all parallel)
       ├── COMBO-1 bundle (p=3 + implicit + κ_3)
       ├── COMBO-3 bundle (unified API smoke)
       ├── Q-C2 Marchenko-Pastur HC
       └── Q-B1 heteroassociative chain

+14 hr Wave 3 (Remote GPU, ~8-12 hr) — GATED on Q-F1 smoke PASS
       └── COMBO-4 dynamical bundle (M_dyn + C(t,t_w) + X(C) + Pred-5)
       └── Q-F4 saddle-overlap triplet

+26 hr Wave 4 (Remote GPU, ~10-15 hr) — GATED on Wave-2 COMBO-1 PASS
       ├── COMBO-2 bundle (p=4 + L3 + signed-AM)
       ├── Q-A3 L=2 composition
       └── Streaming Predictions 2-4 (Brand + κ_3 monitor + drift)

+42 hr Wave 5 (Cloud, ~6-10 hr) — SINGLE BATCH
       └── unified_n32768_v1 (Q-D1 + κ_4/κ_6 + cert Z-ratio + COMBO-3@32K)
```

**Total elapsed:** ~50-65 hr from Wave 1 fire to Wave 5 land. Cloud spend: ~$10-15 single instance.

---

## 4. ABORT / SKIP DECISIONS

- **If Q-F1 smoke HARD-FAILS:** SKIP Wave 3. Substrate's phase moves to "list-with-first-order-hysteresis" (still useful, different product framing). Save 8-12 hr GPU.
- **If Wave-1 streaming baseline HARD-FAILS:** SKIP Streaming Predictions 2-4 in Wave 4. Substrate is NOT CK-class for streaming dynamics — substantial reframing needed.
- **If Wave-2 COMBO-1 HARD-FAILS (HF1: MMD ≥ 0.10):** kernel-trick identity breaks at finite N. SKIP COMBO-2 in Wave 4 (depends on p>2 viability). Substrate caps at p=2 capacity; revisit architecture.
- **If Wave-2 COMBO-3 HARD-FAILS:** the 5-method API uniformity theorem is wrong; 9 primitives need separate implementations. Substantial engineering re-scope but doesn't kill any individual primitive.
- **If Wave-5 cloud HARD-FAILS at any cell:** N=32768 spectral primitives stay at N=8192 envelope; defer production-grade audit-API claim.

---

## 5. CAP_MAP UPDATE REQUESTS

Research recommends the following annotations (orchestrator owns commits; strategy owns ordering):

1. **NEW row: `α^(p-1) audit-sensitivity scaling`** — 🔬 pending COMBO-1 HP3 (cap_map killer feature: tunable drift-detection resolution via interaction degree)
2. **NEW row: `per-fact retention dial via α_μ`** — 🔬 pending Wave-1 streaming-baseline PASS + Wave-4 Streaming-Prediction-6-capability-#1
3. **NEW row: `Negative-Knowledge Tree + Hierarchical Refusal Cert + Counterfactual Abduction over forbidden subtrees`** — 🔬 pending COMBO-2 PASS
4. **NEW row: `5-method audit API as algebraic theorem`** — 🔬 pending COMBO-3 HP1-HP5
5. **NEW row: `live κ_3 audit trail per-write on moving substrate`** — 🔬 pending Wave-4 Streaming-Prediction-4 (κ_3 monitor detection latency)
6. **NEW row: `Ebbinghaus-shaped retention curve from CK aging`** — 🔬 pending Wave-1 streaming baseline
7. **NEW row: `Brand-incremental-SVD streaming Gram refresh`** — 🔬 pending Wave-4 Streaming-Prediction-3
8. **AMEND row: `static-ultrametricity` (currently HARD_FAIL)** — rename to "static UM (off-target for dynamical phase)"; document measurement-mismatch per 6-drill revival consolidation
9. **AMEND row: `Garcia-Lorenzana 2025`** — citation correction to PRL 135, 187402 (arXiv:2408.17360); rewrite from "REFUTED" to "DYNAMICAL signature, leading surviving candidate, Q-F2 tests actual prediction"

---

## 6. DISCIPLINE DECLARATIONS

- Pre-PROT-018 anchor-name `_n<N>` binding contract holds for every anchor.
- HARD bands pre-registered per drill outputs cited above; strategy + exp_dev resolve cell design (sweep grids, seed counts, queue choice, timeout) from these.
- Composition classification (SCORE / HANDOFF / PIPELINE) per protocol for COMBO bundles BEFORE queueing.
- ASCII-only print; verbose tracing if remote-dispatched; per-experiment `--timeout`.
- No padding: if any wave lacks open handoffs or cap_map questions to justify it, drop rather than ship marginal cells.
- Cloud spend: ONE single-instance batch in Wave 5; no serial cloud dispatches.
- Honest cost framing: trace-class primitives are O(N²) per delete, not O(N). At N=4096 ms-scale; at N=32768 ~16-30 ms — still tractable.

---

## 7. WHAT REMAINS UNCHARTED (research candor)

- **τ_α measurement protocol** — CK relaxation timescale needs explicit clean-baseline auto-correlation fit; not directly observable from standard outputs. Adds ~30 min to Wave-1 streaming baseline.
- **α_μ retention dial interaction with SNAP saturation guard** — if α_μ > 1 violates the substrate's saturation projection, retention dial breaks. Needs explicit test in Wave 4 before promoting Feature #6 to customer-facing.
- **Brand's incremental SVD numerical stability at substrate's saturating Hebbian boundary** — Brand 1998 assumes orthonormal basis; substrate's saturating updates may accelerate drift. Cardoso 2026 gives refresh-cadence bounds for clean random matrices only.
- **C(k, m) cyclic-Narayana coefficient at higher k** — COMBO-3 derivation asserts the form for k ≤ 3; needs first-principles re-derivation (Wick-graph-coloring) before locking if k_max extends to ≥ 4.
- **κ_3 mixing-correction term in incremental update** — COMBO-3 derivation sketches but does not fully derive the mixing-correction from κ_1, κ_2 updates. ~30 min of additional algebra to lock; smoke test HP2 verifies numerically.

---

**END.** Orchestrator: fire Wave 1 NOW; gate subsequent waves per the abort/skip table. Strategy: design Wave 1 cells from the capability questions + HARD bands cited above. Cloud Wave 5: ONE single batch; pre-register every cell.

Acted-on 2026-06-02: 5-wave plan adopted; Wave 1 + Wave 2 + Wave 3 dispatches landed; Wave 5 cloud GATE OPEN per v332 verdict_handler (COMBO-3 5HP + kappa3 + Q-C5 + Q-B1 all PASSED); Wave 5 testbed handoff filed earlier
