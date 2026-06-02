# AMENDMENT: overnight 16h batch — LOCAL ONLY (2026-06-01)

**Supersedes:** scope of `strategy_request_to_strategy_overnight_16h_batch_2026-06-01.md`
**Constraint (user direction 2026-06-01):** Cloud capacity reserved for critical experiments (D3 KV-cache authorization pending). Overnight batch runs on **local CPU + local GPU only.**
**Standing:** prior STOP-after-deliverable / no-auto-iterate constraint stands; this routing surfaces a re-scoped batch for strategy/orchestrator consideration, not for auto-ship.

---

## Re-ranking by local-feasibility

The 12 cells from the prior routing are re-grouped by **whether they fit local resources** and whether **the local-N answer is informative**.

### Group LOCAL — fits laptop CPU or laptop GPU at N ≤ 8192; the local-scale answer is informative

| Cell | Resource | Why local-scale answer is informative |
|---|---|---|
| E. tr(W₁W₂) set-cardinality estimator | laptop CPU, ~30 min at N=2048 M=50 | Algebraic identity predicts Pearson r > 0.9999 from σ_K=0.035; doesn't need large N. Cheap definitive confirmation of NOVEL primitive. |
| F. CSP-with-learning interference envelope | laptop CPU, ~30 min at N=1024 M=20 | NOVEL primitive smoke; small-N intentional per drill design. |
| K. Symbolic primitive battery (rule + disjunction + forward chain + backward 1-step) | laptop CPU, ~1h at N=2048 | Substrate-as-inference characterization; N=2048 sufficient for the predicted gaps (cosine > 0.25 etc.). |
| L. Bursty-write step-down empirical | laptop CPU, ~30 min at N=2048 | Verifies closed-form Δm and no-recovery theorem; N=2048 gives clear predicted drop. |
| H. PP-31c knee calibration | laptop CPU at N=2048 → laptop GPU at N=8192 if VRAM permits | Compliance-track; production-N (8192) is the actual deliverable target. CPU run at N=2048 establishes the knee shape; GPU run at N=8192 is the deliverable. |
| C. CK strong-EB parametric FDT (χ vs C kink test) | laptop GPU at N=8192 | N=8192 is sufficient for the FDT-violation observable to discriminate CK vs MCT canonical vs equilibrium per NE-1 drill. Doesn't need N=32768. |
| D. L=2 nested composition (Hadamard-binding, RANDOM KEYS) | laptop GPU at N_outer = N_inner = 8192 | Two W matrices ~1GB float32 total — easily fits laptop GPU. Use RANDOM keys per M1-dominant confirmation from v1b (no Phi-3 dependency). |
| G. Sparse-W K² capacity advantage (light version) | laptop GPU at N=2048 confirm + N=8192 endpoint | Sweep K ∈ {1, 2, 4, 8} × M/N ∈ {0.05, 0.10, 0.20, 0.30}; the K² scaling is detectable already at N=2048. |
| I. Continuous-time τ_mem (light version) | laptop GPU at N ∈ {2048, 4096, 8192} | Three-point fit; τ_mem(N) linear-in-N is detectable without N=32768 endpoint. Constant of proportionality is the deliverable. |
| Sanity rider: **eval_every_k regression test** | laptop CPU | New addition per v1b inversion lesson. Verify that any future memorization-trajectory cell has measurement resolution adequate to rule out sampling artifact BEFORE diagnosing mechanism. Bake into testbed harness, not as a research cell. |

### Group CRITICAL-ONLY — strictly require N=32768 staging unlock; HOLD for cloud budget when justified

| Cell | Why local cannot answer | When to ship |
|---|---|---|
| A. Multi-tenancy depth at N=32768 (HP threshold = T = 2× passing-T at N=16384) | The capability question IS the N=32768 envelope; local-N runs don't unlock the depth claim. Float32 W = 4GB — may fit a 8GB+ laptop GPU but the test setup needs T tenants each holding K patterns, blowing VRAM well before T=2× is reached. | Bundle with D3 KV-cache cloud dispatch IF the dispatch already pays the bootstrap. Otherwise hold for separate critical-experiment justification. |
| B. DMFT 4-point N-scaling collapse {4096, 8192, 16384, 32768} | The collapse test fundamentally needs the N=32768 endpoint to constrain the scaling exponent x (DMFT-TW=2/3 vs Lévy-continuous <0.5). 3-point fit at {4096, 8192, 16384} is suggestive only. | Ride alongside D3 OR hold until PP-33 framework-class is a flagged research priority. |
| J. Tracy-Widom spectral edge at N=32768 | Eigendecomp at N=32768 is ~tens of GB on CPU, hours on GPU. The 35% finite-N correction improvement is what makes the test clean — without it, marginal at N=8192. | Hold for free-probability adjacency batch (multi-drill convergence flagged TW as next-axis; deserves its own dedicated cloud justification). |

### Group DEFER from this batch entirely (no overnight need)

- **Unification via resonator network** (Round 6 drill 5 Smoke 5D) — requires resonator implementation not in codebase.
- **ETF/Kerdock retrieval comparison** — P_deflated=0.18; Round 6 drill 10 already established substrate uses Kerdock; further gain bounded; low ROI for overnight.
- **Tensor-network MPS empirical** — structured-library generator out of scope; orthogonal to immediate KV-cache + audit characterization.
- **Write-DP rescue path** — structurally CANNOT at strong ε; no test target.

---

## Recommended LOCAL overnight batch (research's view, strategy authorizes)

10 cells across 10 capability axes, all local:

1. **E** — set-algebra tr(W₁W₂) cardinality estimator (laptop CPU, N=2048).
2. **F** — CSP-with-learning interference envelope (laptop CPU, N=1024).
3. **K** — symbolic primitive battery (laptop CPU, N=2048).
4. **L** — bursty-write step-down + no-recovery (laptop CPU, N=2048).
5. **H-cpu** — PP-31c knee at N=2048 (laptop CPU) — pilot for the production-N test.
6. **H-gpu** — PP-31c knee at N=8192 (laptop GPU) — production deliverable.
7. **C** — CK parametric FDT plot at N=8192 (laptop GPU).
8. **D** — L=2 Hadamard-binding composition at N=8192² (laptop GPU, RANDOM keys per M1-dominant).
9. **G-light** — sparse-W K² scaling at N=2048 confirm, N=8192 endpoint (laptop GPU).
10. **I-light** — τ_mem at N ∈ {2048, 4096, 8192} (laptop GPU).

**Compute estimate:**
- Laptop CPU: cells 1-5 sequentially ≈ 3-4h total. CPU runner has slack overnight.
- Laptop GPU: cells 6-10 sequentially ≈ 6-9h total. Fits comfortably in 16h overnight.
- Cloud: ZERO spend.

If laptop GPU VRAM is tight (e.g., <8GB): drop D back to N_outer = N_inner = 4096 (still informative for the Hadamard-binding mechanism) and run G-light at N=4096 endpoint instead of N=8192.

---

## What the LOCAL batch can and CANNOT close

**Can close (HP would land):**
- 2 NOVEL primitive empirical confirmations (E set-algebra; F CSP-with-learning).
- L=2 Hadamard-binding composition row at production-relevant N (D at N=8192² or fallback N=4096²).
- Symbolic-primitive sub-rows at quantitative levels (K).
- Burst-tolerance envelope row (L confirms theory).
- PP-31c knee calibration at production N (H-gpu).
- CK strong-EB framework class IF parametric FDT shows the KINK (C).
- Sparse-W K² advantage as scaling prediction (G-light).
- τ_mem constant-of-proportionality pin (I-light).

**Cannot close (requires cloud / N=32768):**
- Multi-tenancy depth scaling claim at N=32768.
- DMFT vs Lévy-DMFT discrimination via 4-point N-scaling collapse.
- Free-probability / TW edge clean test (J).

**The PP-33 framework-class band CAN partially lift from local C cell alone**: if the parametric FDT plot at N=8192 shows the kink, that is evidence for CK strong-EB without needing the N=32768 endpoint. Lift would be 0.40-0.55 → 0.55-0.65 (less than the full 0.65-0.75 that the 4-point collapse would deliver, but informative).

---

## Cloud reservation policy (research's understanding, awaiting orchestrator confirmation)

- **Next cloud spend = D3 KV-cache authorization** per user direction + v1b deliverable's standing-by note.
- **Cloud cells from Group CRITICAL-ONLY (A, B, J)** ride alongside D3 if the bootstrap can be shared, OR queue as separate critical-experiment justifications.
- **No cloud overnight padding** per [[feedback-no-padding-experiments]] and current explicit user constraint.
- Headroom $28.51 (out of $50 budget after $21.49 spend) preserved for D3 + any rider critical cells.

---

## Discipline declarations (unchanged from prior routing)

- Each cell has HP/MID/HF bands per design; no batch-level expected-PASS framing.
- Anchor names + sweep grids resolved by exp_dev.
- Cells span ≥ 8 distinct capability axes (this re-scoped local batch covers 10 axes).
- Per-experiment `--timeout` required; ASCII-only print; verbose tracing if remote-dispatched.
- Pre-PROT-018 anchor-name `_n<N>` binding contract.
- No silent idle for laptop runners.

---

## Net effect of the constraint

The cloud-off constraint **eliminates the N=32768 staging-unlock payoff cells from this batch**, but preserves 10 of 12 originally-proposed capability axes. The 2 cells held back (A multi-tenancy + B DMFT collapse + J TW edge as a related rider) are the ones where the local-N answer is genuinely UNINFORMATIVE relative to the N=32768 answer; deferring them avoids wasting laptop GPU hours on a measurement that doesn't unlock the capability claim.

The KV-cache identity confirmed by v1b (97% memorization, M1-dominant, deterministic; semantic generalization CANNOT) sharpens what matters: NOVEL primitives (E set-algebra, F CSP-with-learning, D L=2 composition) and AUDIT capabilities (H PP-31c refusal-cert, L burst-tolerance, I τ_mem retention) are the cache + audit story. This batch advances exactly those.

<!-- routing-completed: Acted-on 2026-06-01: local-only overnight batch shipped Round 8 + Round 9 + Round 10 series -->
