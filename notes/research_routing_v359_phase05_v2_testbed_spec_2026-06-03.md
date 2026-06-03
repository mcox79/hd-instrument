# RESEARCH ROUTING — Phase 0.5 v2 testbed spec (updated post-drill-battery)

**From:** Research session
**To:** Testbed / Orchestrator / exp_dev / user
**Date:** 2026-06-03
**Trigger:** User explicit ask — share updated full Phase 0.5 experiment design incorporating drill-battery findings. Phase 0.5 v1 is currently running on cloud H100 (started 2026-06-03 00:51 UTC, ~6.5h in). This routing provides the v2 spec for either (a) replacing v1, (b) extending v1 on the same H100, or (c) running as separate v2 dispatch post-v1-verdict.
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell design parameters fully spec'd (testbed deliverable — engineering-actionable per `feedback_testbed_progress_logging_and_restart`). Per-PROT compliance.

---

## 0. WHAT CHANGED FROM v1 (testbed integration summary)

| Change | v1 spec | v2 spec | Source |
|---|---|---|---|
| **Sub-test A observable** | κ_3 spectral fingerprint only | κ_3 + BBP eigenspectrum dual-observable | PP-58 2x deep dive |
| **Sub-test A HP bands** | σ_sep ≥ 5 (Wave-2 leading-order) | σ_sep ≥ 5 OR BBP ratio ≥ 4.0 (NLO corrected; 4.6× wider envelope) | Wave-2 NLO drill |
| **Sub-test B primitive** | PP-46 rank-1 W subtraction only | PP-46 + PP-56 Sherman-Morrison dual | PP-56 cycle-26 founding |
| **Sub-test B protocol** | Predecessor-start (implicit) | Predecessor-start + root-start dual | PP-49 2x deep dive |
| **Sub-test C depth** | depth-3 (odd; parity-risk) | depth-4 (even; defensive) + depth-3 backup | PP-49 1x parity finding |
| **NEW Sub-test D** | not present | Multi-bank B=4 capacity-expansion demo | Q-B1 2x deep dive |
| **Architecture-level** | Single-bank substrate | Single-bank + multi-bank options exposed | Q-B1 architectural fix |
| **Isochoric measurement** | not specified | Hold α fixed across noise sweeps | Arrhenius deep dive |

**Net delta:** 1 new sub-test (D), 3 sub-tests upgraded with dual-variant cells, 1 new measurement discipline (isochoric).

---

## 1. SUB-TEST A — κ_3 + BBP drift detection (UPGRADED, dual-observable)

**Anchor name:** `tier7_mvp_hyperprobe_llama31_drift_detection_v2_kappa3_plus_bbp`

**Capability question:** does the substrate's spectral fingerprint detect fact-injection adversarial drift in LLM activation streams at production scale, comparing κ_3 (original) vs BBP eigenspectrum (new) observables under isochoric measurement protocol?

**Architectural setup:**
1. LLM forward pass on prompt corpus; intercept residual at layer ℓ = round(L × 0.7) on final-token position
2. Hyperprobe encoder E_ℓ : R^d → {-1,+1}^D maps LLM residual to substrate bipolar codes (D = 4096 published OR D = 32768 retrained per Wave 2)
3. Substrate streaming write: W_t ← W_{t-1} + (1/N) ξ_t ξ_t^T with bounded-window decay (window = 200 patterns; α ≈ 200/4096 = 0.049)
4. Whitening applied per κ_3-mixing drill recommendation: Σ^{-1/2} factorization

**Test corpus:** 1000 prompts split 800 in-distribution control + 200 fact-injection adversarial (crafted to inject specific factual claims; adversarial set derived from TruthfulQA + custom fact-corruption prompts).

**Dual-observable measurement (run BOTH on the same prompt stream):**

**Observable 1 — κ_3 spectral fingerprint (NLO-corrected):**
- Hutchinson trace estimator: n_probes = 5000 complex
- Whitened κ_3 = Tr((Σ^{-1/2} W Σ^{-1/2})^3) / N
- Measure κ_3 distribution per population (in-distribution / adversarial)
- σ_sep(κ_3) = |μ_kappa3_adv - μ_kappa3_ID| / sqrt(σ_ID² + σ_adv²)

**Observable 2 — BBP eigenspectrum bulk-edge merging:**
- Compute spectral edge λ_max via Lanczos (matvec=20 sufficient per BBP theory)
- BBP signal: gap between λ_max and bulk edge λ_+ = (1+√α)²
- BBP ratio = (λ_max_adv - λ_+) / (λ_max_ID - λ_+) — should approach 0 for adversarial drift
- Alternative metric: (1-√α-α) / (1+3α+α²) = predicted N-independent BBP ratio at α=0.05 = 0.726/3.0 = 0.242

**Isochoric protocol:** hold α fixed at 0.05 across all conditions. If LLM-side noise σ_LLM and substrate-side noise σ_substrate need separate measurement, run additional cells at α=0.10 + α=0.15 for transition characterization.

**Pre-registered bands (NLO-corrected):**

For κ_3:
- **HARD-PASS:** σ_sep ≥ 5 across 5 seeds (NOTE: this is the same threshold as v1; substrate's NLO envelope is 4.6× wider than Wave-2 said, so HP becomes ACHIEVABLE under more diverse noise conditions)
- **MIDDLE:** σ_sep ∈ [2, 5] (signal present but weaker than predicted; rescue via tighter whitening or N=32768 retrained probe)
- **HARD-FAIL:** σ_sep < 2

For BBP:
- **HARD-PASS:** |BBP_ratio_adv - BBP_ratio_ID| ≥ 5σ AND BBP_ratio_adv approaches predicted 0.242 at adversarial fact-injection rate
- **MIDDLE:** discrimination ∈ [2σ, 5σ]
- **HARD-FAIL:** BBP_ratio identical across populations (no spectral signature)

**Discriminator outcome:**
- κ_3 HP AND BBP HP: substrate dual-observable confirmed; product API offers both
- κ_3 MIDDLE/HF AND BBP HP: **BBP becomes substrate-product audit primitive (κ_3 deprecated for production); PP-58 row LIFT**
- κ_3 HP AND BBP MIDDLE/HF: κ_3 remains primary; BBP needs further work
- Both HF: substrate algebra doesn't transfer to LLM-mapped patterns; substrate-LLM coupling broken at audit-primitive layer

**Cost:** ~1 GPU-day at H100 (dominant cost: probe encoding 1000 prompts + Hutchinson n_probes=5000 + Lanczos matvec=20; minimal additional GPU vs v1 single-observable).

---

## 2. SUB-TEST B — Deletion cert dual-primitive dual-protocol (UPGRADED)

**Anchor name:** `tier7_mvp_hyperprobe_llama31_deletion_cert_v2_pp46_plus_pp56_dual_protocol`

**Capability question:** can substrate produce verifiable per-fact deletion certificates against an LLM's live internal state using PP-46 AND PP-56 deletion primitives, under both predecessor-start and root-start counterfactual-recovery protocols?

**Test design:**

**Storage phase:** store 100 facts encoded as LLM residual at fact-mention token via probe → substrate. Track substrate state W_0.

**Deletion cells (2 × 2 = 4 conditions):**

| Cell | Primitive | Recovery protocol | Algebra |
|---|---|---|---|
| B1 | PP-46 rank-1 W subtraction | Predecessor-start | W' = W - (1/N) ξ_f ξ_f^T; query via predecessor-pattern retrieval |
| B2 | PP-46 rank-1 W subtraction | Root-start | Same W' update; query via root-pattern multi-hop retrieval |
| B3 | PP-56 Sherman-Morrison | Predecessor-start | W' = W - (W ξ_f ξ_f^T W) / (1 + ξ_f^T W ξ_f); predecessor-pattern query |
| B4 | PP-56 Sherman-Morrison | Root-start | Same W' update; root-pattern multi-hop query |

For each cell:
- Delete 25 randomly-selected facts via the cell's primitive
- Verify (a) deleted-fact residual; (b) retained-fact retention; (c) cert chain reproducibility
- 5 seeds per cell = 20 total runs

**Pre-registered bands per cell:**
- **HARD-PASS:** deleted-fact residual < 2σ noise floor AND retained-fact retention > 0.85 across 5 seeds; cert chain reproducible to byte-exact
- **MIDDLE:** deleted residual ∈ [2σ, 5σ] OR retention ∈ [0.65, 0.85]
- **HARD-FAIL:** deleted residual > 5σ OR retention < 0.65 OR cert chain non-reproducible

**Discriminator outcomes:**
- All 4 cells HP: substrate's deletion cert works at LLM coupling under any (primitive, protocol) combination; product API maximally flexible
- B1 + B3 MIDDLE/HF; B2 + B4 HP: **predecessor-start has the rank-1 1-hop ceiling artifact (PP-49 2x finding confirmed at LLM coupling); product API must specify root-start**
- B1 + B2 MIDDLE/HF; B3 + B4 HP: PP-46 has LLM-coupling issue; **PP-56 Sherman-Morrison becomes the substrate-product deletion primitive (PP-56 row lifts to flagship)**
- B1 MIDDLE/HF + B3 HP + B2/B4 mixed: complex; protocol AND primitive matter
- All HF: substrate cannot algebraically erase from LLM-mapped patterns; **substrate's #1 product moat broken at LLM coupling** (substrate-novel HARD-FAIL — would refute Drill 5 mechanism-class separation argument empirically)

**Cost:** ~1.5 GPU-days at H100 (4 cells × 5 seeds × storage+deletion+verification; roughly 4× v1 sub-test B due to cell expansion).

---

## 3. SUB-TEST C — Refusal cert via PP-48 NKT (DEPTH-DEFENSIVE)

**Anchor name:** `tier7_mvp_hyperprobe_llama31_refusal_cert_v2_pp48_even_depth_defensive`

**Capability question:** can substrate produce hierarchical refusal certificates when LLM emits activations matching forbidden patterns using PP-48 NKT at EVEN depth (defensive against parity-class regime per PP-49 1x finding)?

**Test design:**

**Primary cell C1 — depth-4 NKT (even, defensive):**
- Build 16-leaf PP-48 NKT at depth-4 (2^4 = 16 forbidden categories; e.g., 4 PII + 4 decision-class + 4 legal + 4 medical) from forbidden-prompt activations
- 5 seeds × 5 forbidden + 25 allowed test prompts = 150 prompts/seed

**Backup cell C2 — depth-3 NKT (odd, original v1 spec for comparison):**
- Build 8-leaf PP-48 NKT at depth-3
- Same prompt corpus + seeds

**Optional cell C3 — depth-6 NKT (even, larger):**
- Build 64-leaf PP-48 NKT at depth-6
- Same prompt corpus + seeds — tests scaling

**Pre-registered bands per cell:**
- **HARD-PASS:** precision = 1.0 (zero false-allow on forbidden) AND false-refusal rate ≤ 0.10
- **MIDDLE:** precision ∈ [0.9, 1.0] OR false-refusal ∈ (0.1, 0.25]
- **HARD-FAIL:** precision < 0.9 (negative-knowledge algebra leaks through probe-mapping noise — PP-48 LLM-coupling broken)

**Discriminator outcomes:**
- C1 HP AND C2 HP: parity-class concern unfounded; PP-49 1x mechanism refuted; PP-49 2x protocol-artifact mechanism more likely; substrate at arbitrary depth
- C1 HP AND C2 MIDDLE/HF: parity-class regime confirmed at LLM coupling; **product API must specify even-depth NKT trees**
- C1 MIDDLE/HF AND C2 HP: anomalous (would suggest different mechanism); needs investigation
- C3 HP corroborates C1 (even-depth holds at scale)

**Cost:** ~0.5 GPU-day at H100 (NKT construction is algebraically cheap; prompt corpus is ~150 prompts/seed × 5 seeds × 3 cells).

---

## 4. SUB-TEST D (NEW) — Multi-bank capacity expansion via PP-12 primitive

**Anchor name:** `tier7_mvp_hyperprobe_llama31_multibank_b4_capacity_test`

**Capability question:** does multi-bank B=4 addressing (substrate's existing PP-12 multi-bank primitive) raise the operational α envelope for LLM-coupled substrate by ~4× as Q-B1 2x deep dive predicts (P=0.80)?

**Test design:**

**Cell D1 — single-bank baseline at α=0.20 (near-capacity stress):**
- 800 prompts → substrate single-bank (M=800, N=4096, α=0.195)
- Run deletion cert (PP-46) on 25 deleted; measure as sub-test B HP gates
- Measure κ_3 drift signal on adversarial subset; sub-test A HP gates
- 5 seeds

**Cell D2 — multi-bank B=4 at α=0.50 (4× single-bank load, but α_bank=0.125):**
- 2000 prompts distributed across 4 banks (M_bank=500 per bank, N=4096; α_per_bank=0.122)
- Same deletion cert + κ_3 drift measurements as D1
- 5 seeds

**Pre-registered bands:**
- **HARD-PASS:** multi-bank B=4 at α=0.50 matches single-bank at α=0.125 across deletion + drift metrics within 5%; sub-test A and sub-test B HP gates met for D2
- **MIDDLE:** multi-bank degrades 5-15% vs single-bank-at-α_bank baseline
- **HARD-FAIL:** multi-bank at α=0.50 performs like single-bank at α=0.50 (i.e., near-capacity collapse); architectural fix doesn't work at LLM coupling

**Discriminator outcomes:**
- D2 HP: **multi-bank product extension validated at LLM coupling; PP-12 primitive scales substrate's operational envelope 4× at LLM-coupled deployment**; product API exposes multi-bank as a knob
- D1 HF + D2 HP: substrate's single-bank LLM-coupling envelope IS at α=0.20 ceiling; multi-bank is required for production deployment
- Both HP: substrate single-bank handles α=0.20 at LLM coupling AND multi-bank works for further scaling

**Cost:** ~1 GPU-day at H100 (5 cells of 5 seeds each across 2 cell-design conditions; similar to sub-test B scope).

---

## 5. SEQUENCING + COST OPTIONS

### Option 2 (RECOMMENDED) — Extension on running H100 instance

Phase 0.5 v1 completes its current run (sub-tests A/B/C v1); verdict_handler processes verdicts; orchestrator dispatches v2 sub-tests as EXTENSIONS on the same H100 instance.

**v2 extensions to dispatch post-v1 verdict (selective based on v1 outcomes):**

| v1 outcome | v2 extension to dispatch | Incremental cost |
|---|---|---|
| Sub-test A HP | Add BBP eigenspectrum observable on same probe stream (sub-test A part 2 only) | ~$2-5 |
| Sub-test A MIDDLE/HF | Add BBP as alternative observable + isochoric protocol | ~$5-10 |
| Sub-test B HP | Add PP-56 Sherman-Morrison variant on same fact corpus (sub-test B cells B3+B4) | ~$3-8 |
| Sub-test B MIDDLE/HF | Add dual-primitive + dual-protocol full 4-cell matrix | ~$10-15 |
| Sub-test C HP | (no action needed; v1 depth-3 passing means parity-class isn't an issue at LLM coupling) | $0 |
| Sub-test C MIDDLE/HF | Add depth-4 even-defensive cell C1 | ~$2-5 |
| (Any) | Sub-test D multi-bank (new architectural test) | ~$5-10 |

**Total Option 2 cost ceiling: ~$30-50 incremental** on top of v1 (which is currently accumulating at $4.29/hr — running scope determines v1 total).

### Option 1 — Full v2 replacement (if v1 not yet committed)

If v1 hasn't actually committed to spec yet (still in bring-up), replace with full v2:
- All 4 sub-tests fresh dispatch
- Total cost: ~$60-100 (1 + 1.5 + 0.5 + 1 = 4 GPU-days at H100)
- Engineering: ~3 eng-days incremental on top of v1 bring-up (~2 eng-days for dual-observable + dual-protocol + multi-bank wiring)

### Option 3 — Separate v2 dispatch post-v1-verdict

If v1 hardware/instance is shut down before v2 dispatches, bootstrap a new H100 instance for v2:
- Bootstrap cost: ~$10-20 (re-load Llama-3.1-8B + hyperprobe weights)
- v2 sub-test cost: ~$40-80 (full 4-sub-test battery)
- Total: ~$50-100

**Recommendation:** Option 2. Maximizes shared-bootstrap savings, allows selective extension based on v1 verdict, lowest incremental engineering effort.

---

## 6. PRE-LAUNCH WAVE-5 EXPERIMENTS (queued from drill battery; CPU-only; would inform v2 design)

If feasible to run the 3 Wave-5 decisive CPU experiments BEFORE v2 sub-tests dispatch (all <2h CPU, $0), v2 would have strongest theoretical foundation:

1. **MFPT N-scaling probe** → confirms or refutes 1-RSB phase → informs sub-test A noise envelope interpretation
2. **BBP eigenspectrum calibration** → validates BBP observable against substrate-only baseline before LLM-coupled test → de-risks sub-test A part 2
3. **HRC depth-parity discriminator** → resolves PP-49 1x-vs-2x mechanism → informs sub-test B protocol choice + sub-test C depth choice

Dispatching Wave-5 NOW (parallel to v1 running) gives all 3 results before v2 extensions need to launch. Net cost: $0; net engineering: ~30 min orchestrator queue dispatch.

---

## 7. INTEGRATION CHECKLIST (for testbed)

When user authorizes Phase 0.5 v2:

- [ ] Confirm v1 verdict state (which sub-tests HP / MIDDLE / HF)
- [ ] Confirm H100 instance still running (or bootstrap option)
- [ ] Dispatch Wave-5 3 CPU experiments in parallel (if not already done)
- [ ] Apply Option 2 selective extension based on v1 verdicts + Wave-5 results
- [ ] Pre-register HP/MIDDLE/HF bands per sub-test per Section 1-4 above
- [ ] Whitening pipeline per κ_3-mixing drill recommendation (sub-test A)
- [ ] Dual-observable wiring (κ_3 + BBP) per sub-test A
- [ ] Dual-primitive (PP-46 + PP-56) + dual-protocol (predecessor + root) wiring per sub-test B
- [ ] Even-depth (depth-4) PP-48 NKT defensive default per sub-test C
- [ ] Multi-bank B=4 substrate variant wiring per sub-test D
- [ ] Isochoric measurement discipline (α fixed across noise sweeps in sub-test A) — Arrhenius protocol
- [ ] Cost tracker monitoring; cap at $50 incremental for Option 2
- [ ] Cell-level partial JSON output per `feedback_testbed_progress_logging_and_restart`

---

## 8. CAP_MAP IMPACT EXPECTATIONS (if Phase 0.5 v2 all-HP)

- **PP-50 BAND-LIFT** (κ_3 OR BBP audit primitive empirically validated at LLM coupling)
- **PP-46 + PP-56 cross-protocol validation** (substrate's deletion cert family lifts at LLM-coupled deployment)
- **PP-48 + PP-49 LIFTs** (refusal cert + counterfactual abduction lift at LLM-coupled)
- **PP-12 multi-bank LIFT** (architectural primitive validated at LLM coupling; substrate-product depth expansion)
- **NEW: PP-58 BBP protocol LIFT** if BBP HP independently
- **NEW: PP-55/56/58 founding-LIFT** if all dual-primitive cells pass
- **3 NEW Tier-7 EXPLORATORY ROWS founded:**
  - N1 cert-grade live-LLM audit primitive 0.65-0.80
  - N2 per-fact LLM erasure cert 0.65-0.80
  - N3 counterfactual LLM-state abduction 0.65-0.80
- **Phase 0.5b empirical-launch authorization** triggered if Phase 0.5 v2 = 3-of-3 sub-test all-HP OR 3-of-4 with sub-test B HP (B is the load-bearing piece)

---

## 9. DISCIPLINE DECLARATIONS

- **Capability questions only;** HP/MIDDLE/HARD-FAIL bands pre-registered per sub-test per cell.
- **Per `feedback_no_padding_experiments`:** each cell justified by drill-battery finding (BBP observable from PP-58 deep dive; PP-56 from cycle-26 founding; dual-protocol from PP-49 2x; even-depth from PP-49 1x; multi-bank from Q-B1 2x; isochoric from Arrhenius).
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** all HARD-FAIL trip-wires explicit; verdict_handler does honest re-read.
- **Per `feedback_strategy_spec_formula_selftests`:** sub-test A NLO bands include PROT-022 self-test (`σ_g_crit = sqrt(ln(1+0.15/(3α)))` = 0.833 at α=0.05; testable in BOTH sub-test A directly AND Wave-5 BBP calibration).
- **Per `feedback_testbed_progress_logging_and_restart`:** all sub-tests must emit per-cell partial JSON for restart capability.
- **Per `feedback_obey_user_pause_explicitly`:** v2 dispatch requires USER EXPLICIT GO-BEYOND-v1 authorization beyond the original Phase 0.5 v1 authorization (which was for 3 sub-tests not 4).
- **Per `feedback_short_cloud_runs_preferred`:** Option 2 ($30-50 incremental) preserves under standing per-case threshold; Option 1 ($60-100) and Option 3 ($50-100) require explicit user auth.
- **Per `feedback_batch_cloud_experiments`:** all v2 sub-tests on same H100 instance bootstrap; no parallel separate dispatches.
- **PROT-018:** all v2 anchor names use `tier7_mvp_hyperprobe_llama31_*_v2_*` family; no `_n<N>` suffix needed (LLM-native d=4096 / D=32768 depending on probe variant).
- **Per-experiment `--timeout`:** sub-test A 2400s; B 3600s; C 1200s; D 2400s (scaled from v1 + dual-cell expansion).

---

## 10. WHAT THIS ROUTING DOES NOT TOUCH

- **Phase 0.5b distillation MVP** — separate decision-gate per `research_routing_v359_drill_battery_synthesis_2026-06-03.md` Section 7; this routing is for the Phase 0.5 v2 design update only.
- **Cell-level engineering details** (data loader, probe weight loading, exact tokenizer setup) — testbed engineering scope.
- **LLM choice** — Llama-3.1-8B-Instruct via vLLM (locked from v1; v2 inherits).
- **Hyperprobe checkpoint source** — assumed self-trained per Wave 2 retrain path (v1 inherited; v2 same).

---

**END.** 

**To user:** v2 spec is testbed-ready. Review Sections 1-4 sub-test designs + Section 5 sequencing options + Section 8 cap_map impact expectations. Edit as needed; then dispatch via testbed once v1 verdict lands (Option 2 recommended).

**Testbed:** pick up this spec when v1 verdict triggers Option 2 extension OR when user authorizes Option 1/3. Integration checklist in Section 7.

**Orchestrator:** queue 3 Wave-5 CPU experiments NOW per Section 6 (parallel to v1 running on cloud; CPU + GPU bandwidth available; $0).
