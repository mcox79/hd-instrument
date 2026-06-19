# RESEARCH ROUTING — PP-47 + deletion-cert composition test (Phase 0 for LLM-integration testbed)

**From:** Research session
**To:** Orchestrator → Strategy → exp_dev (cell design)
**Date:** 2026-06-02
**Trigger:** PP-47 2x deep drill (Drill A — algebraic mechanism) landed with critical decomposition finding. PP-47's 0.879 Spearman ρ is ~100% explained by the encoding kernel itself (top-K thresholding produces piecewise-linear distance-similarity), NOT by Hopfield retrieval. The substrate's REAL spatial-coding contribution is the algebraic composition of place-field codes with substrate-novel primitives (deletion cert, refusal cert, counterfactual abduction) — none of which the current PP-47 test exercises.

**Strategic priority:** this is **Phase 0** for the Tier-6 LLM-integration testbed sequence. The substrate-novel claim that distinguishes substrate from vector DBs / position embeddings is algebraic-deletion-with-cert on spatial memories — Drill B's Tier-6 testbed depends on this primitive working. Before spending 3-4 weeks engineering on Tier-1+2+6 LLM integration (~$10-15 cloud, ~3-4 weeks engineering), validate that the substrate-novel primitive composes correctly with place-field encoding at substrate-only test scale.

**Cost:** ~15 min CPU at N=4096. Local laptop or remote CPU.

---

## 1. CAPABILITY QUESTION

Does the substrate's algebraic deletion certificate (PP-46 / COMBO-3 P9) compose correctly with PP-47 place-field encoding, such that:

(a) deleting one specific location ξ_X via rank-1 subtraction is verifiable via cert (consistent with COMBO-3's machine-precision cert=0 result at p=2 dense W), AND

(b) nearby locations (within Gaussian receptive-field overlap with X) remain retrievable above their pre-deletion threshold, AND

(c) the deleted location ξ_X is no longer retrievable above the noise floor, AND

(d) the κ_3 fingerprint of the place-field-encoded W exhibits a detectable shift after deletion (per COMBO-3 + κ_3 incremental update theorem), AND

(e) the Spearman ρ between location distance and pattern overlap is preserved on the post-deletion stored set (the structural property survives algebraic editing)?

---

## 2. ALGEBRAIC BASIS

**Setup:** N=4096, K=204 locations with PP-47 place-field encoding (Gaussian σ=2, PLACE_FRAC=0.30), Hopfield W = Σ ξ_k ξ_k^T / N. Pick location index X ∈ [K/4, 3K/4] (interior to avoid boundary effects).

**Deletion operation:** W' = W − (1/N) ξ_X ξ_X^T (exact rank-1 subtraction).

**Algebraic predictions (per COMBO-3 P9 + Phase-2 deletion-cert drill):**
- Cert signature ξ_X^T (W' − W) ξ_X = −(1/N) ||ξ_X||⁴ — closed-form scalar (independent of N for ||ξ_X||² = N, gives cert = −1 exactly)
- Retrieval at deleted location: h(ξ_X | W') is dominated by crosstalk from M−1 remaining patterns; SNR_post-deletion ≈ √(M−1)/N at α=0.05 ≈ √203/4096 ≈ 0.0035 — should retrieve NOISE not ξ_X
- Retrieval at adjacent location X±1: cosine overlap to ξ_(X±1) should be preserved within finite-N corrections (~5% per Phase-2 deletion-cert drill); Gaussian-shifted retrieval cosine ≈ 0.879 (the same as pre-deletion baseline minus epsilon)
- κ_3(W') − κ_3(W) is computable in closed form via the COMBO-3 incremental formula (Section 2c of combo-3 drill output); expected shift Δκ_3 ≈ −3α·ξ_X^T z_2 / N + 3α²·||ξ_X||²·ξ_X^T z_1 / N − α³·||ξ_X||⁶ / N (using shared Krylov buffer)
- Post-deletion Spearman ρ on the remaining K−1 patterns: should match pre-deletion ρ within finite-N noise (since the encoding kernel structure is preserved)

---

## 3. PRE-REGISTERED HARD/MIDDLE/FAIL BANDS

**Anchor name (pre-PROT-018):** `pp47_deletion_cert_composition_v1` — N default 4096, no `_n<N>` suffix needed unless N differs.

### HARD-PASS (5 conditions must all hold)

| # | Test | Threshold |
|---|---|---|
| HP1 | Cert signature exact | \|ξ_X^T (W' − W) ξ_X + 1\| < 1e-10 (machine precision at N=4096 fp64) |
| HP2 | Deleted location no longer retrievable | post-deletion retrieval cosine at ξ_X is < 0.20 (well below the pre-deletion 0.879) |
| HP3 | Nearby location preservation | retrieval cosine at ξ_(X±1) and ξ_(X±2) preserved within ±0.05 of pre-deletion baseline |
| HP4 | κ_3 fingerprint shift detectable | \|Δκ_3_observed − Δκ_3_predicted\| / κ_3(W) < 1e-2 (Hutchinson-noise-allowing) |
| HP5 | Spatial structure preservation | post-deletion Spearman ρ on K−1 patterns within ±0.05 of pre-deletion 0.879 |

### HARD-FAIL (any one closes the test)

| # | Test | Threshold | Implication |
|---|---|---|---|
| HF1 | Cert signature wrong | \|cert + 1\| > 1e-4 | Algebra of P9 deletion-cert + place-field encoding inconsistent |
| HF2 | Deleted location still retrievable | cosine at ξ_X > 0.50 | Rank-1 subtraction insufficient at p=2 dense W (would contradict COMBO-3 v332 cert=0 exact result) |
| HF3 | Nearby location destroyed | cosine at ξ_(X±1) drops > 0.20 below baseline | Deletion has spillover damage — substrate-novel claim broken |
| HF4 | κ_3 fingerprint blind | \|Δκ_3_observed − Δκ_3_predicted\| / κ_3(W) > 0.10 | κ_3 fingerprint cannot detect spatial-memory deletion — drift-detection moat damaged |
| HF5 | Spatial structure collapses | post-deletion Spearman ρ drops > 0.20 below baseline | Deletion damages topological order globally — substrate's spatial coding is fragile to editing |

### MIDDLE BAND

Any test in [HP threshold − 0.05, HP threshold] OR [HP threshold + 0.05, HF threshold] — flag for finite-N investigation; re-run at N=8192 5-seed before promoting to HARD-PASS.

---

## 4. WHY THIS IS PHASE 0 FOR THE LLM-INTEGRATION TESTBED

Drill B (PP-47 Tier-6 testbed design) recommended a 3-4 week engineering sequence:
- Tier-1 (RAG-baseline, 2-3 days, $0)
- Tier-2 (function-call generic, 5-7 days, $5)
- Tier-6 flagship (StepGame k=4, 7-10 days, $5-10)
- Tier-6 stretch (BabyAI, 15-20 days, $20-50)

Drill A established that the substrate's REAL contribution to spatial cognition is NOT the encoding accuracy (any embedding scheme can produce ρ ≈ 0.879 on Gaussian-thresholded patterns) — it is the **algebraic composition of substrate-novel primitives with place-field codes**. The deletion-cert primitive is the most concrete and testable of these.

**If Phase 0 HARD-PASSes:** the substrate-novel claim that Tier-6 testbed will market ("auditable spatial memory with algebraic deletion + refusal + counterfactual that no vector DB / position embedding can do") has firm algebraic foundation. Proceed to Tier-1+2+6 with confidence.

**If Phase 0 HARD-FAILs (HF2 or HF3 in particular):** the substrate-novel deletion-on-spatial-memory claim is suspect. Tier-6 testbed should NOT spend engineering days on a product story whose algebraic foundation is broken. Either redesign the deletion mechanism for place-field codes OR retreat the substrate's product positioning from "spatial cognition + audit" to "auditable RAG + place-field encoding as encoding scheme only."

**If Phase 0 MIDDLE-BAND:** finite-N corrections present at N=4096; re-test at N=8192 before Tier-6 commits.

---

## 5. RECOMMENDED ROUTING

**Queue:** Remote CPU (laptop CPU also works; <15 min wall, ~3·10⁷ FLOPs).

**Per-experiment timeout:** 300s (per PROT-019; generous margin for <15 min expected wall).

**Seed count:** 5 seeds (standard; matches PP-47 v333 protocol).

**SCORE-class composition** per `feedback_composition_classification`: tests are independent algebraic checks (cert + retrieval + Spearman + κ_3 each is a standalone score). No PIPELINE / HANDOFF gating between checks.

**Dependencies:** none. v324 COMBO-3 P9 cert=0 confirmed at p=2 dense W; v333 PP-47 confirmed at N=4096 5-seed. Both prerequisites locked.

---

## 6. SUBSTRATE-PRODUCT IMPLICATIONS

If HARD-PASS, Phase 0 founds a new cap_map sub-property candidate:
- **PP-47a: deletion-cert composition with place-field codes** (research recommendation: 0.55-0.70 band, with +0.05 calibration deflation; matches PP-47 base band)

This sub-property is the load-bearing algebraic claim for the substrate's spatial-cognition product narrative. Substrate-product moat: **"the only memory subsystem that can algebraically delete a specific spatial memory with verifiable cert AND preserve nearby spatial structure."** Vector DBs, position embeddings, and brain-inspired transformer architectures (Tolman-Eichenbaum Machine) cannot do this without retraining.

For Tier-6 LLM-integration testbed: Phase 0 PASS unlocks the substrate-novel sub-cell of the flagship test (spatial deletion cert HARD-PASS at ≥95% verifiable across inferences). Phase 0 FAIL forces redesign of the flagship test or retreat from spatial-cognition product positioning.

---

## 7. DISCIPLINE DECLARATIONS

- Capability questions only; HP/MIDDLE/FAIL bands pre-registered. Strategy + exp_dev resolve cell design (sweep grids, queue specifics, seed numerics, log format).
- Pre-PROT-018 anchor-name `_n<N>` binding contract: default N=4096, no suffix needed.
- ASCII-only print; per-experiment `--timeout=300`.
- HARD-FAIL conditions explicit; MIDDLE BAND resolution path specified (re-test at N=8192).
- No padding: 5 specific tests, each load-bearing for one substrate-novel claim. No exploratory padding.
- Per `feedback_lit_scan_calibration_penalty`: no novel-synthesis cap applied here — the composition is two confirmed primitives (PP-47 + COMBO-3 P9 + κ_3 incremental update) where each component HARD-PASSes at machine-precision in prior tests. Joint composition has well-defined algebraic form.
- Per `feedback_no_smoke_preframing_in_task_prompts`: do NOT pre-frame Phase 0 as "expected HARD-PASS"; pre-register the falsifying conditions explicitly.

---

## 8. EXPECTED OUTCOME (research's honest expectation, not pre-framing)

Phase 0 is testing the COMPOSITION of two confirmed primitives:
- PP-47 place-field encoding: ρ=0.879 confirmed at v333 (FULL N=4096 5-seed)
- COMBO-3 P9 deletion cert: cert=0 exact at v332 (machine-precision)
- κ_3 incremental update: COMBO-3 HP2 confirmed at v332

The composition algebra is well-defined; each primitive composes via the shared Krylov buffer {ξ_X, Wξ_X, W²ξ_X} per COMBO-3. **Research's honest P_deflated estimate for HARD-PASS: 0.60** (high prior — confirmed primitives, established algebra, no novel synthesis). MIDDLE-BAND risk: ~0.25 (finite-N corrections at boundary cases). HARD-FAIL risk: ~0.15 (only if the place-field encoding's structured-pattern correlation interacts badly with rank-1 subtraction in a way the algebra doesn't predict).

---

**END.** Orchestrator: queue at remote CPU (or laptop CPU); strategy + exp_dev design the cell from capability questions + HP/HF bands above. If HARD-PASS, file PP-47a sub-property + unlock Tier-1 LLM-integration testbed scoping per Drill B sequence.
