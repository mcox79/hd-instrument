# RESEARCH ROUTING AMENDMENT — LLM-integration program Phase 0.5 (Tier-7 MVP)

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev / testbed
**Date:** 2026-06-02
**Trigger:** USER EXPLICIT AUTHORIZATION for Phase 0.5 Tier-7 MVP private decisive test (~$50-100 cloud + 8 engineering-days). Authorization received 2026-06-02 in response to Hyperdimensional Probe Tier-7 drill findings (arXiv:2509.25045 uses MAP-Bipolar in {-1,+1}^4096 — substrate's native BSC algebra).
**Supersedes:** Phase 4 scope in `research_routing_llm_integration_program_2026-06-02.md` (Tier-7 was deferred-pending-Tier-1+2+6); promotes Tier-7 to Phase 0.5 strategic-gate test.
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell design (anchor names full form, sweep grids, queue specifics, timeout numerics, log format) resolved by strategy + exp_dev. Per-PROT compliance.

---

## 0. STRATEGIC REFRAME — Tier-7 as flagship via private decisive test

The Hyperdimensional Probe drill confirmed three load-bearing facts:

1. **MAP-B = substrate's native BSC algebra** — arXiv:2509.25045 chose {-1,+1}^4096 without knowing about substrate. Convergent design: the field has independently arrived at substrate's data type. No algebraic adapter required; substrate operates NATIVELY on probe output.

2. **3 Tier-7-only capabilities have no published competitor:**
   - **N1 cert-grade live-activation audit** (substrate κ_3 + deletion-cert + refusal-cert; EigenTrack arXiv:2509.15735 only does κ_2)
   - **N2 per-fact erasure verification against deployed LLM**
   - **N3 counterfactual abduction on LLM internal state via PP-49 hierarchical refusal tree**

3. **Substrate is one cumulant deeper than current SOTA** (EigenTrack achieves AUROC 0.82-0.94 hallucination / 0.85-0.96 OOD using κ_2; substrate's κ_3 fingerprint is the third-cumulant generalization with σ_sep up to 1727 at production N=32768).

**Strategic positioning shift:** if Phase 0.5 Tier-7 MVP HARD-PASSes, substrate's product narrative moves from "auditable AI memory" to **"the missing audit layer for the LLM industry."** Tier-1/2/6 deployment paths become alternatives, not flagship.

**Window of relevance:** arXiv:2509.25045 published September 2025 — 3 months ago. After 12-18 months, follow-on probe variants will commoditize the mapping; substrate's audit-cert advantage shrinks if Tier-1/2 ship first as public face. Phase 0.5 fires NOW to lock the positioning.

---

## 1. PHASE 0.5 SPEC — Tier-7 MVP private decisive test

**Goal:** validate whether substrate's algebraic audit primitives operate correctly on hyperprobe-mapped LLM residual streams, via 3 sub-tests on Llama-3.1-8B with public hyperprobe checkpoint.

**Architecture (Tier-7 passive read-side companion):**
```
1. LLM forward pass; intercept residual at layer ℓ = L*0.6..0.8 on final-token position
2. Hyperprobe encoder E_ℓ : R^d → {-1,+1}^D maps LLM residual to substrate codes
   (d = 4096 Llama-3.1-8B hidden; D = 4096 published or N = 32768 retrained)
3. Substrate streaming write: W_t ← W_{t-1} + (1/N) ξ_t ξ_t^T with bounded-window decay
4. Substrate audit primitives operate on rolling W:
   (a) κ_3 spectral fingerprint after whitening (per I-10 mitigation from κ_3-mixing drill)
   (b) Per-fact deletion cert via rank-1 subtraction
   (c) Refusal cert via PP-48 negative-knowledge tree
   (d) COMBO-3 bilinear primitives Tr(W A W B) — correlation-agnostic backup
5. Output: substrate-native audit signals at <10ms/forward-pass (parallel to token emission)
```

**Substrate is NEVER in the LLM forward graph.** Cannot disturb generation. Audit signals stream-paralleled to token output.

### 1.a CAPABILITY QUESTIONS (3 sub-tests, all pre-registered)

**Sub-test A — κ_3 drift detection with whitening rescue**

*Capability question:* does the substrate's κ_3 spectral fingerprint (after whitening per I-10 mitigation) detect fact-injection adversarial drift in LLM activation streams at production scale?

*Algebraic basis:* hyperprobe achieves cos-sim 0.89 / binary acc 0.94 decoding LLM residuals into bipolar codes. After whitening (Σ^{-1/2} factorization per the κ_3-mixing drill recommendation), the κ_3 fingerprint should operate at its production-scale σ_sep up to 1727 demonstrated at v333 cap_map for substrate-internal patterns. Adversarial fact-injection should produce a detectable spectral shift.

*Test design:* 1000 prompts — 800 in-distribution (control), 200 fact-injection adversarial (prompts crafted to inject specific factual claims). For each prompt, hyperprobe-encode the LLM residual stream, write to substrate W, compute whitened-κ_3 estimate via Hutchinson (n_probes = 5000 complex). Compare κ_3 distributions across the two populations.

*Pre-registered bands:*
- **HARD-PASS:** σ_sep ≥ 5 between in-distribution κ_3 and adversarial κ_3 across 5 seeds
- **MIDDLE:** σ_sep ∈ [2, 5] (signal present but weaker than predicted; rescue via tighter whitening or N=32768 retrained probe)
- **HARD-FAIL:** σ_sep < 2 (algebra doesn't transfer to LLM-mapped patterns OR whitening rescue fails empirically)

**Sub-test B — Deletion cert verification against live LLM state**

*Capability question:* can the substrate produce verifiable per-fact deletion certificates against an LLM's live internal state, with downstream queries reflecting the deletion?

*Algebraic basis:* COMBO-3 P9 deletion cert hit machine precision (cert=0 exact) at substrate-internal patterns. Rank-1 subtraction W' = W − (1/N) ξ_f ξ_f^T should produce algebraically clean deletion on hyperprobe-encoded fact representations. Per Cell 5 Wave 5 result, substrate supports depth-10 chains at 0.984 fidelity — the cert chain primitive scales.

*Test design:* Store 100 facts (encoded as LLM residual at fact-mention token) via probe → substrate. Issue deletion cert for 25 randomly-selected facts. Verify:
- Deleted-fact residual (cosine of W' · ξ_f vs ξ_f) is below noise floor
- Retained-fact retention (cosine of W' · ξ_g vs ξ_g for g ∈ retained set) is above threshold

*Pre-registered bands:*
- **HARD-PASS:** deleted-fact residual < 2σ noise floor AND retained-fact retention > 0.85, across 5 seeds
- **MIDDLE:** deleted residual ∈ [2σ, 5σ] OR retention ∈ [0.65, 0.85]
- **HARD-FAIL:** deleted residual > 5σ noise floor (substrate cannot algebraically erase from LLM-mapped patterns — substrate's #1 product moat broken at LLM coupling) OR retention < 0.65

**Sub-test C — Refusal cert via PP-48 negative-knowledge tree on forbidden activations**

*Capability question:* can the substrate produce 3-level hierarchical refusal certificates when LLM emits activations matching forbidden patterns (PP-48 negative-knowledge tree composed with hyperprobe-mapped LLM state)?

*Algebraic basis:* COMBO-2 v334 confirmed unanimous HARD-PASS (l3_fid=1.0, b_rep=1.0, parity=0.0) at N=4096 for PP-48 negative-knowledge tree composition. Hyperprobe maps LLM activations into substrate-compatible bipolar codes; PP-48's signed-AM + L3 composition should produce active-repulsion + refusal cert on forbidden coordinates.

*Test design:* Build 30-leaf PP-48 negative-knowledge tree from forbidden-prompt activations (e.g., PII-related, decision-class-related per the v334 KSP framing). Send 5 forbidden + 25 allowed test prompts. Verify substrate issues refusal cert iff forbidden tree triggers.

*Pre-registered bands:*
- **HARD-PASS:** precision = 1.0 (zero false-allow on forbidden) AND false-refusal rate ≤ 0.10 (zero or near-zero allowed-refusal)
- **MIDDLE:** precision ∈ [0.9, 1.0] OR false-refusal ∈ (0.1, 0.25]
- **HARD-FAIL:** precision < 0.9 (negative-knowledge algebra leaks through probe-mapping noise — PP-48 LLM-coupling broken)

### 1.b GATING LOGIC FOR PHASE 0.5

**Tier-7 viable IFF all three sub-tests HARD-PASS or MIDDLE (no HARD-FAIL):**
- 3 HARD-PASS → Tier-7 is FLAGSHIP READY; substrate-product positioning shifts to "the missing audit layer for the LLM industry"; cap_map row candidates PP-50 "live LLM audit primitive" + PP-51 "live LLM erasure cert" + PP-52 "live LLM hierarchical refusal cert" all founded
- 2 HARD-PASS + 1 MIDDLE → Tier-7 viable at restricted scope; the MIDDLE sub-test gets a follow-on N-scale or whitener-tighten rescue at next iteration
- 1 HARD-PASS + 2 MIDDLE → Tier-7 viability uncertain; defer flagship positioning until rescues confirm
- ANY HARD-FAIL on A or B → Tier-7 archived; pursue Tier-1/2/6 as originally planned. The HARD-FAIL diagnostic tells us where the algebraic coupling breaks (whitening rescue failure / per-fact erasure failure / algebraic-adapter requirement)
- HARD-FAIL on C alone → restricted-scope Tier-7 (live LLM audit + erasure cert; no refusal cert) — still substantial product value, just without PP-49 spatial-refusal extension

**Three Tier-7-only capabilities cap_map outcome:**

| Outcome | N1 cert-grade live-audit | N2 per-fact LLM erasure | N3 counterfactual LLM-state abduction |
|---|---|---|---|
| 3 HARD-PASS | ✅ founded | ✅ founded | ✅ founded |
| HARD-FAIL on A | ❌ key claim broken | restricted | restricted |
| HARD-FAIL on B | restricted | ❌ key claim broken | restricted |
| HARD-FAIL on C | ✅ | ✅ | ❌ tree-mediated extension broken; flat refusal still viable |

### 1.c PRE-PROT-018 ANCHOR NAMES

Strategy + exp_dev resolve cell design; suggested anchor structure:
- `tier7_mvp_hyperprobe_llama31_kappa3_drift_v1` (sub-test A, no _nN; LLM-native d=4096 by default)
- `tier7_mvp_hyperprobe_llama31_deletion_cert_v1` (sub-test B, no _nN)
- `tier7_mvp_hyperprobe_llama31_refusal_cert_v1` (sub-test C, no _nN)

OR single composite anchor `tier7_mvp_hyperprobe_llama31_v1` with 3 sub-cells per metric.json.

---

## 2. ENGINEERING SETUP (8 days, parallel to Phase 0 substrate-only fires)

### 2.a Build phases

| Task | Resource | Cost |
|---|---|---|
| Clone `Ipazia-AI/hyperprobe` from GitHub; integrate substrate API | 1 eng-day | $0 |
| Build whitening pipeline (Σ-estimator + Σ^{-1/2} factorization helper per κ_3-mixing drill recommendation) | 1 eng-day | $0 |
| Build test harness for 3 sub-tests (prompt corpus + ground-truth labels for adversarial / forbidden cases) | 2-3 eng-days | $0 |
| Cloud bring-up: Lambda A100 instance + Llama-3.1-8B via vLLM + hyperprobe checkpoint | 1 eng-day | minimal cloud time |
| MVP test runs: 3 sub-tests + 5-seed each | 4-7 GPU-days | **$30-80 cloud** |
| (Optional, post-MVP) Path-(i) probe retrain at D=N=32768 for production deploy | 1 GPU-day + 2 eng-days | **+$15 cloud** |

**Total Phase 0.5 cost:** ~$50-100 cloud + ~8 engineering-days for decisive yes/no.

### 2.b Single-bootstrap commit per `feedback_batch_cloud_experiments`

The 3 sub-tests share the same Llama-3.1-8B instance + hyperprobe checkpoint + substrate runtime. One bootstrap, three test cells. Do NOT split into separate cloud dispatches.

### 2.c LLM choice rationale

**Llama-3.1-8B-Instruct via vLLM** — locked rationale:
- Smallest published-probe LLM in arXiv:2509.25045 → MVP cost minimized
- Matches Drill B's Tier-6 testbed LLM choice → cross-test consistency
- Function-call support documented (matches Phase 2 future bring-up)
- Fits Lambda A100 single instance at Q4 quantization with hyperprobe overhead

**Pythia-1.4B as smoke fallback** if cost overruns; **Llama 4 Scout 109B / Phi-4** as scaling targets if MVP HARD-PASSes.

---

## 3. SEQUENCING (updated 5-phase + 0.5 program)

```
NOW (parallel)
├── Phase 0 (substrate-only composition pre-checks, ~1 hr CPU, $0) [filed]
│     0a: pp47_deletion_cert_composition_v1
│     0b: pp47_pp48_negative_spatial_tree_v1
│     0c: pp47_pp49_counterfactual_spatial_v1
└── Phase 0.5 ENGINEERING START (8 eng-days build, ~$0 cloud during build)
      tier7_mvp_hyperprobe_llama31_v1 bring-up

+8 days
└── Phase 0.5 CLOUD DISPATCH (single bootstrap, 4-7 GPU-days, $30-80 cloud)
      Sub-tests A + B + C in one instance
      
+15-22 days (post Phase 0.5 verdict)
├── IF Phase 0.5 = 3 HARD-PASS: Tier-7 FLAGSHIP positioning; cap_map PP-50/51/52 founded
│     Optional: probe retrain at D=N=32768 (~$15 cloud + 2 days)
│     Optional: cross-LLM probe-of-probe transfer drill (level-3)
└── IF Phase 0.5 ≠ 3 HARD-PASS: pursue original 4-phase program
      Phase 1: Tier-1 RAG-baseline (2-3 days, $0)
      Phase 2: Tier-2 function-call generic (5-7 days, $5)
      Phase 3: Tier-6 flagship StepGame composite (7-10 days, $5-10)
      Phase 4: Tier-6 stretch (15-20 days, $20-50)
```

**Total program cost:** 
- Optimistic (Phase 0.5 HARD-PASS): ~$45-115 cloud + ~10-12 eng-days
- Pessimistic (Phase 0.5 FAIL, full 4-phase): ~$50-115 cloud + ~30-35 eng-days
- Worst case (Phase 0.5 + full 4-phase as defensive depth): ~$100-150 cloud + ~35-40 eng-days

Phase 0.5 is the **strategic lever** — at $50-100 it derisks the entire program AND potentially shortcuts to flagship positioning.

---

## 4. DEPENDENCIES + RISK ANALYSIS

### 4.a Phase 0 → Phase 0.5 dependency

Phase 0 fires NOW (~1 hr CPU); Phase 0.5 engineering proceeds in parallel for 8 days. **Phase 0 results land well before Phase 0.5 cloud dispatch.** Specifically:
- If Phase 0b (PP-47 × PP-48 negative spatial tree) HARD-FAILs → reconsider Phase 0.5 sub-test C; scope down or defer
- If Phase 0a (PP-47 × PP-9 deletion cert) HARD-FAILs → reconsider Phase 0.5 sub-test B; scope down or defer

Phase 0 IS the substrate-only validation that the composition algebra works. Phase 0.5 is the LLM-coupling validation. The two are sequential dependencies; Phase 0 fires first, Phase 0.5 dispatches after Phase 0 results inform.

### 4.b Three risk modes per Drill findings

**Risk (a) — Algebraic coupling breaks under hyperprobe mapping.** Substrate's free-Poisson identity at N=32768 was confirmed on iid bipolar codes. Probe output is NOT iid (codebook structure + supervised training induce correlations).
- *Mitigation:* whitening rescue (per κ_3-mixing drill); COMBO-3 bilinear primitives correlation-agnostic backup
- *Sub-test A directly tests this*

**Risk (b) — LLM residual streams have HIGH ρ (per I-10 + Ethayarajh anisotropy lit).** Raw LLM hidden states cluster in narrow cone with ρ > 0.3.
- *Mitigation:* hyperprobe paper reports cos-sim 0.89 reconstruction INTO bipolar codebook (suggests probe output DOES spread the cone)
- *Empirical question for sub-test A; whitening rescue applies if needed*

**Risk (c) — Hyperprobe is per-LLM trained.** Each new LLM requires probe retrain (55-71M params).
- *Mitigation:* cross-model transferability lit (arXiv:2501.02009 Platonic concepts, arXiv:2506.06609 model stitching) suggests linear transformations preserve concept structure. Probe-of-probe (small MLP from new-LLM residual → existing-LLM residual) may transfer in O(1 GPU-hour)
- *Productization risk only; doesn't affect Phase 0.5 MVP outcome*

---

## 5. CAP_MAP UPDATE REQUESTS (research recommendation; orchestrator commits)

On Phase 0.5 HARD-PASS (3/3), file:
- **NEW row: PP-50 live LLM audit primitive** 0.65-0.80 EXPLORATORY (with +0.05 calibration deflation)
- **NEW row: PP-51 live LLM per-fact erasure cert** 0.65-0.80 EXPLORATORY
- **NEW row: PP-52 live LLM hierarchical refusal cert** 0.65-0.80 EXPLORATORY
- **PP-47 LIFT to 🟢 0.75-0.90** (PP-47 spatial encoding empirically extended to LLM-internal state)
- **PP-48 LIFT to 🟢 0.75-0.90** (negative-knowledge tree empirically extends to LLM-coupled deployment)
- **PP-49 LIFT to 🟢 0.75-0.90** (HRC + counterfactual abduction empirically extends to LLM-coupled deployment)

On Phase 0.5 MIDDLE or FAIL, file detailed sub-test breakdown; do not commit PP-50/51/52 until rescues confirm.

---

## 6. DISCIPLINE DECLARATIONS

- **Capability questions only; HP/MIDDLE/FAIL bands pre-registered.** Strategy + exp_dev resolve cell design (anchor names full form, sweep grids, queue specifics, timeout, log format).
- **Pre-PROT-018 anchor-name `_n<N>` binding contract** — Phase 0.5 sub-tests have NO _nN suffix because they operate at LLM-native d=4096 (or N=32768 if retrained). PROT-018 rule 3 default applies.
- **ASCII-only print; per-experiment `--timeout`.** Set generous timeout for cloud sub-test cells (~14400s per the per-experiment-timeout-required lock for >5-min walls).
- **Single-bootstrap cloud dispatch** per `feedback_batch_cloud_experiments`. Do NOT split sub-tests A/B/C into separate cloud instances.
- **No padding** — 3 sub-tests, each load-bearing for one Tier-7-novel capability. No exploratory padding.
- **Per `feedback_lit_scan_calibration_penalty`:** Phase 0.5 P_deflated = 0.42 (novel-synthesis cap applied; substrate-novel LLM-coupling regime).
- **Per `feedback_obey_user_pause_explicitly`:** Phase 0.5 cloud spend AUTHORIZED by user 2026-06-02; no further user gate needed for Phase 0.5 sub-tests A/B/C. Phases 3+ still require explicit per-case auth.
- **Per `feedback_short_cloud_runs_preferred`:** $50-100 is above standing per-case threshold but explicitly authorized for this dispatch.
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** task prompts to verdict_handler MUST NOT pre-frame sub-tests A/B/C as HARD-PASS. Pre-register HARD-FAIL conditions explicitly; verdict_handler does honest re-read.

---

## 7. WHAT THIS AMENDMENT DOES NOT TOUCH

- COMBO-1 v3 redesign (separate research routing; awaits exp_dev cell design)
- I-9 F4 M4 + I-10 κ_3 mixing rescues (separate strategy v334 routing; whitening rescue from κ_3-mixing drill informs Phase 0.5 sub-test A directly)
- Wave 5 Cell 1 σ_TW detail check + Cell 2 Part A theory recalibration (separate testbed routing)
- Cap_map v334 → v335 transition (strategy owns)
- Phase 0 sub-tests 0a/0b/0c (filed in separate routing; fire on next CPU queue refill)
- Original Phase 1+2+3+4 (4-phase program) — conditional on Phase 0.5 outcome; if Tier-7 FLAGSHIP positioning lands, Phases 1+2 become alternative deployment paths but stay in queue

---

## 8. CROSS-THREAD SYNTHESIS

**Phase 0.5 INTEGRATES findings from:**
- **κ_3 mixing drill (2026-06-02):** whitening rescue baked into sub-test A. If sub-test A HARD-FAILs, distinguishes "algebra doesn't transfer at all" from "whitening rescue insufficient" — first failure is fatal, second is rescuable with tighter whitening.
- **Hyperdimensional Probe drill (2026-06-02):** MAP-B = substrate's native BSC; Path-(i) retrain at D=N=32768 is the production path; cross-LLM probe-of-probe is the productization scaling story.
- **v334 PP-48 + PP-49 confirmation:** sub-test C composes PP-48 negative-knowledge tree with hyperprobe-mapped LLM state; if HARD-PASSes, lifts PP-48 + PP-49 from 0.65-0.80 EXPLORATORY → 0.75-0.90 LIVE-LLM-COUPLED.
- **Cell 5 Wave 5 (Q-B1 depth-extended) HARD-PASS at production N=32768:** depth-10 chain fidelity 0.9846 at 8σ over threshold; substrate supports the deep-chain primitives that sub-test B's deletion-cert chain replay depends on.
- **EigenTrack arXiv:2509.15735 (Sept 2025):** spectral activation monitoring of LLM hidden states works (κ_2 only, AUROC 0.82-0.94 hallucination). Substrate κ_3 is third-cumulant generalization — substrate is one cumulant deeper than current SOTA. Sub-test A is the empirical anchor for this claim.

---

**END.** Orchestrator: queue Phase 0 (0a/0b/0c) on next CPU queue refill; start Phase 0.5 engineering bring-up in parallel; cloud dispatch authorized for Phase 0.5 sub-tests A+B+C as single bootstrap when engineering ready (estimated +8 days). Strategy: fold Phase 0 into v334 priority #2 cross-application probe queue; track Phase 0.5 as priority #4 (after the three substrate-only Phase 0 tests). exp_dev: cell design for Phase 0.5 from capability questions + HARD/MIDDLE/FAIL bands above; LLM choice locked Llama-3.1-8B; single-bootstrap commit.
