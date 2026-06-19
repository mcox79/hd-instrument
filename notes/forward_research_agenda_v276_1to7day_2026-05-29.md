# Forward Research Agenda v276 -- 1-to-7 day horizon (2026-05-29)

**Filed by:** research sub-agent (Opus, DEEPER drill, parallel batch of 8 cousins).
**Trigger:** post-v276 strategic synthesis. v275/v276 cycle produced 2nd-strike confirmations on three rejection arms (PB-3 FLAT_TAU, Axis-4 hysteresis, HS-3) and surfaced the OPERATIONAL-LAYER-INVARIANCE pattern as the dominant interpretive lens. 5 GPU-day Tier-1 batch already shipped (alpha-1/2/3, gamma-1, pb3_v6_R2 + 18 prior anchors). This note is the next-72h to next-7d planning artifact.
**Authority:** strategic recommendation; main thread + strategy cycle make ship decisions. Research does NOT modify cap_map.

---

## 0. The strategic frame this agenda is built on

### 0.1 The OPERATIONAL-LAYER-INVARIANCE pattern (v275/v276 dominant insight)

Across v272-v276, the same structural finding has surfaced in 5 INDEPENDENT probes:

1. **v272 BE-1 INT1=FP32 on isolation** -- W-magnitude is non-operative in the argmax-readout isolation path. Quantization at the storage layer does not propagate to the readout decision layer.
2. **v272 Region C/D = A/B at beta=64 vs beta=8** -- M_frac is operative; beta is layer-invariant at the M-controlled regime selector.
3. **v270 axis-1 chunk progression** -- M/N=4-8 / 16-20 / 25-32 shows monotone behaviour class transitions but no beta-mediated steering layer.
4. **v275 PB-3 FLAT_TAU at N=4096 (2nd strike of v4_n8192)** -- tau_recovery metric does not couple to N at the level we expected; the dynamical layer producing tau is invariant to N-scaling above some threshold.
5. **v276 HS-3 + Axis-4 multi-basin closure (2nd-strike confirmed)** -- M-history and hysteresis loops do not exist at extreme M near M_c; the operational-state-readout layer is M-history-INVARIANT.

The unifying claim: **the substrate has at least 2 (probably 3) computational LAYERS, and the operative behavior at the readout layer is INVARIANT to perturbations at intervening layers** unless the perturbation propagates through a specific coupling pathway. The 4-region phase-lattice and the 32x cost-advantage narratives both implicitly assumed end-to-end propagation that does NOT in fact occur. The product implication is large: pricing the substrate by per-layer features (storage / dynamics / readout) is the right product model, NOT by global parameter sweeps.

This pattern is the SCAFFOLD for the entire agenda. Every cluster below is an operational test of WHICH layers couple to WHICH outcomes.

### 0.2 Calibration penalty applied (per [[feedback-lit-scan-calibration-penalty]])

Substrate is in uncharted regime: no published direct precedent for HDC-substrate computational-layer separation. All P estimates in this note are DEFLATED 0.15-0.25 relative to naive lit-scan posteriors. Novel-synthesis P capped at 0.50. Hard-fail thresholds included in every prediction.

### 0.3 GPU budget = ~5 GPU-days (user-named Tier-1 batch). CPU budget = ~10 CPU-days/week. Eng budget = ~2 eng-days/week (limited by user attention).

---

## 1. TODAY (next 4-8h) -- alpha-3 + Tier-1-batch interpretation

### 1.1 alpha-3 (`kf5_multi_output_steer_n4096`) result interpretation playbook

This is the single most important experiment shipped in the v273-v276 cycle, per user. It directly tests whether the substrate steerability hypothesis lives at the multi-output dimension rather than the global-beta or global-M dimension.

The pre-spec'd metric is per-output-direction diversity score (per output dimension d in {1..D_out}, measure the variance of (output value across stored facts) and correlate with d). Three branching paths:

#### Path A -- LARGE multi-output diversity (HARD_PASS bound: diversity_score > 0.40)

**Interpretation:** the substrate IS multi-output-steerable. The closed v272 4-region phase-lattice narrative was the WRONG dimensionality of steering. Steering lives in the per-output-direction subspace, not the global-beta subspace.

**Strategic moves (next 24h):**
- KF-5 phase-mechanism row PARTIAL REHABILITATION candidate. The basin-volume rescue routing (v269 KF-5 v2) becomes contingently relevant again -- request strategy to RE-OPEN that rescue with the multi-output framing as the load-bearing test.
- Dispatch FOLLOW-ONS:
  - **alpha-4 = `kf5_multi_output_codebook_variation_n4096`** -- does the per-output diversity hold across codebook families (Kerdock, Hadamard, BSC)? Tests whether multi-output steering is codebook-axis-coupled. ~1 GPU-day.
  - **alpha-5 = `kf5_multi_output_beta_fine_n4096`** -- fine beta sweep at beta near beta_c=10 with multi-output diversity as the metric (NOT global KF metric). Tests beta x multi-output coupling. ~1 GPU-day.
- Cap_map: KF-5 🔬 row → 🟡 candidate (pending alpha-4/alpha-5 verdicts).

**P(this branch) deflated:** 0.30 (raw lit estimate would be 0.45-0.55; downward by 0.15 because no direct precedent for HDC multi-output steerable behavior in our specific FHRR/BSC regime).

#### Path B -- SMALL BUT NON-ZERO diversity (MIDDLE_BAND bound: 0.10 < diversity_score < 0.40)

**Interpretation:** there IS multi-output structure, but it is too weak to be a product-feature steering axis. Reformulate KF-5 narrower: not a global "phase-mechanism" claim but a narrow operational anomaly worth characterizing for completeness.

**Strategic moves (next 24h):**
- Dispatch single follow-on: **alpha-4-narrow = `kf5_multi_output_n8192_replication`** -- N-axis replication to determine if the weak signal strengthens or weakens at larger N. ~1 GPU-day.
- IF alpha-4-narrow weakens at N=8192: close KF-5 with narrower spec ("KF-5 multi-output structure is a small-N curiosity, not a product feature").
- IF alpha-4-narrow strengthens at N=8192: rehabilitate similar to Path A but with deflated band (yellow not green).
- Cap_map: KF-5 🔬 row UNCHANGED (annotation only).

**P(this branch) deflated:** 0.35.

#### Path C -- ZERO diversity (HARD_FAIL bound: diversity_score < 0.10)

**Interpretation:** KF-5 multi-output steering does not exist. Combined with v272's region C/D = A/B finding, KF-5 phase-mechanism is now 2-STRIKE (extreme-beta-closed + multi-output-closed). Closure candidate.

**Strategic moves (next 24h):**
- File strategy_request to close KF-5 phase-mechanism row entirely; reframe the operational selector as M_frac-1D-only (collapses the steerability narrative cleanly).
- DO NOT dispatch alpha-4 / alpha-5 (they would burn GPU on a closed direction).
- Free up the ~2 GPU-days originally earmarked for alpha-4/alpha-5 -- redirect to **beta-cluster** (operational-layer-invariance characterization, Section 2.2 below).
- Cap_map: KF-5 🔬 row → ❌ CLOSED candidate (strategy decides band).

**P(this branch) deflated:** 0.35.

#### Falsification criterion (cross-path)
HARD-PASS: diversity_score > 0.40 at >=2 seeds (Path A).
HARD-FAIL: diversity_score < 0.10 at >=4/5 seeds (Path C).
MIDDLE-BAND: 0.10-0.40 (Path B).
UNKNOWN/INCONCLUSIVE: <2 seeds report (treat as Path B until repaired).

### 1.2 Tier-1 batch result triage -- which results matter MOST

Of the 5 Tier-1 anchors shipped (alpha-1, alpha-2, alpha-3, gamma-1, pb3_v6_R2):

| Anchor | Strategic weight | Why |
|---|---|---|
| alpha-3 (multi-output) | HIGHEST | Single most decisive on KF-5 fate; 3-branch decision tree |
| pb3_v6_R2 (PB-3 v3-identical) | HIGH | PB-3 row closure or rehabilitation hinges on this -- 3rd strike candidate |
| gamma-1 (Bet B dual-W CLS smoke) | HIGH | Bet B architectural pivot; smoke result determines whether full Phase-2 fires |
| alpha-1 (cleanup sweep) | MEDIUM | Discovery probe (cleanup-strength axis); informs Cluster D direction |
| alpha-2 (codebook variation) | MEDIUM | Codebook axis steerability complement (matches B3 in v273 cluster nomenclature) |

**verdict_handler dispatch cadence (recommendation):**
- Single-batch verdict_handler when 2+ Tier-1 results land within 30min of each other (efficient parallel cap_map moves).
- IMMEDIATE solo dispatch for alpha-3 the moment it lands -- it gates the next 24h of dispatches.
- Pause-flag check before any exp_dev refill following verdict (per [[feedback-obey-user-pause-explicitly]]).

### 1.3 What CANNOT ship today
- Cluster beta (multi-observable operational-layer-invariance characterization) -- depends on alpha-3 PATH-C trigger to redirect budget. If alpha-3 takes Path A or B, beta-cluster stays in next-24h tier.
- alpha-4 / alpha-5 follow-ons -- alpha-3 path-dependent.
- LLM-1 Phase-2 -- multi-day eng track, never appropriate for "today" tier.

---

## 2. TOMORROW (next 12-24h) -- alpha-3-conditional dispatches

### 2.1 IF alpha-3 PATH A or B (multi-output steerability confirmed or partial)

#### alpha-4 `kf5_multi_output_codebook_variation_n4096`
- **Anchor:** alpha-4
- **Experiment design:** existing KF-5 multi-output script + sweep across 4 codebook families (Kerdock-N=4096-log2=12-SAFE / Hadamard / BSC / sparse-BSC) x 3 seeds.
- **Cost:** 1 GPU-day (~6-12 GPU-hours).
- **Dependency:** alpha-3 verdict + KF-5 row state.
- **Falsification:** HARD-PASS if diversity_score holds (within 30%) across >=3 codebooks; HARD-FAIL if collapses on >=3 codebooks.
- **Question answered:** is multi-output steering codebook-axis-INVARIANT (universal substrate property) or codebook-coupled (codebook-specific quirk)?

#### alpha-5 `kf5_multi_output_beta_fine_n4096`
- **Anchor:** alpha-5
- **Experiment design:** fine beta sweep in [6, 14] x M_frac in [6, 10] x 3 seeds, using multi-output diversity_score as the metric (NOT global KF metric).
- **Cost:** 1 GPU-day.
- **Dependency:** alpha-3 PATH-A specifically (Path B narrower-spec test).
- **Falsification:** HARD-PASS if diversity_score peaks at fine-beta vs flat-beta; HARD-FAIL if invariant across beta.
- **Question answered:** does multi-output steering live in the narrow beta-c band (last unexplored beta-axis territory per v273 user strategy)?

### 2.2 IF alpha-3 PATH C (multi-output steerability denied) -- redirect to BETA-CLUSTER

#### beta-1 `op_layer_invariance_multi_observable_n4096`
- **Anchor:** beta-1
- **Experiment design:** at a single fixed operating point (M_frac=4, beta=8, N=4096, codebook=BSC), apply 6 distinct perturbations (W-magnitude quantization at INT4, codebook shuffle, beta jitter +/-30%, M_frac jitter +/-30%, cleanup-strength toggle, noise injection at storage) and measure 5 simultaneous observables (isolation, retrieval acc, tau_recovery, BID order parameter, posterior-entropy of readout).
- **Cost:** 1 GPU-day (single operating point but heavy multi-observable instrumentation).
- **Dependency:** alpha-3 PATH C (frees budget).
- **Falsification:** HARD-PASS for LAYER-INVARIANCE if >=3 observables are statistically invariant (per-observable p>0.10 under perturbation x bonferroni); HARD-FAIL if all 5 observables couple to all 6 perturbations.
- **Question answered:** which specific layer-perturbation x observable pairs DO couple? This MAPs the substrate's coupling matrix C[layer x observable].
- **Why pivotal:** this is the experiment that ELEVATES the operational-layer-invariance pattern from "we have suggestive evidence" to "we have the coupling matrix C". Once C is mapped, every other substrate question becomes a specific cell in C.

#### beta-2 `op_layer_correlation_matrix_n4096`
- **Anchor:** beta-2
- **Experiment design:** pure analysis pass over existing v264-v276 metrics.json corpus -- compute pairwise correlations of (isolation, retrieval acc, tau, BID, hysteresis loop area, KF metrics, posterior-entropy) across all completed runs.
- **Cost:** 0.5 CPU-day (pure analysis).
- **Dependency:** existing metrics corpus (~100+ completed runs since v260).
- **Falsification:** HARD-PASS if observable-pair correlations cluster into 2-3 distinct groups (consistent with 2-3 computational layers); HARD-FAIL if everything correlates to everything (single-layer substrate, no separation).
- **Question answered:** does the existing data ALREADY contain the layer-separation signal we need? If yes, beta-1 is corroboration; if no, beta-1 is generative.
- **Cheapest possible probe** -- could ship TODAY if user wants. Recommend pairing with alpha-3 verdict landing.

#### beta-3 `op_layer_time_dependent_driving_n4096`
- **Anchor:** beta-3
- **Experiment design:** apply time-dependent driving (periodic edit-query at frequencies omega in {0.1, 1.0, 10.0} Hz-equivalent) at fixed operating point. Measure observable response at each frequency.
- **Cost:** 1 GPU-day.
- **Dependency:** beta-1 verdict (decide whether to ship beta-3 standalone or pair).
- **Falsification:** HARD-PASS if substrate shows frequency-selective response (resonance / cutoff); HARD-FAIL if response is omega-invariant.
- **Question answered:** does the substrate have a DYNAMICAL layer with characteristic timescale? If yes, the 3-layer model is corroborated and time-domain is the third axis.
- **Maps to:** Cluster D D4 from v273 (filed but TIER 4 then) -- elevates to TIER 2 under PATH C.

### 2.3 gamma-1 result interpretation (Bet B dual-W CLS smoke)

#### IF gamma-1 SMOKE_HARD_PASS (ret_A >= 0.80 at smoke N=1024)
- Dispatch FULL **gamma-1-full = `bet_b_cls_dual_w_full_n4096_5seed`** -- 5-seed FULL at N=4096. Cost: 1 GPU-day.
- Cap_map: Bet B 4-stage 🟡 row stays UNCHANGED pending FULL.
- Continued probe: **gamma-2 = `bet_b_cls_dual_w_n8192`** N-axis extension contingent on gamma-1-full PASS. Cost: 1.5 GPU-days.

#### IF gamma-1 SMOKE_MIDDLE_BAND (ret_A in [0.70, 0.80])
- Dispatch FULL anyway to disambiguate seed variance from mean effect. Cost: 1 GPU-day.
- Treat as "promising but unresolved" until FULL lands.

#### IF gamma-1 SMOKE_HARD_FAIL (ret_A < 0.70)
- Bet B architectural pivot FAILS on dual-W approach. Next architectural rescue: **gamma-3 = `bet_b_frozen_W_phaseA_n4096`** (Cluster C C2 from v273 user strategy). Cost: 0.5 GPU-day.
- IF gamma-3 also fails: Bet B 4-stage row goes to ❌ closure candidate -- training-axis exhausted (v269-v271) + architectural-axis exhausted (gamma-1, gamma-3).
- This is the highest-risk-of-closure path; ensure the post-failure routing is filed cleanly.

### 2.4 pb3_v6_R2 outcome interpretation

#### IF pb3_v6_R2 REPRODUCES v3 (tau_recovery > 0.5)
- v4 + v5 are N-extension issues, NOT v3 artifact. Dispatch **pb3_R1 = N-intermediate sweep N=6144 + N=10240** (v275 rescue sketch R1). Cost: 1.5 GPU-days GPU.

#### IF pb3_v6_R2 FLAT_TAU REPRODUCES (tau < 0.1)
- v3 itself was an artifact. PB-3 critical-slowing row 3rd-STRIKE confirmed. File ❌ CLOSURE candidate.
- DO NOT dispatch R1 (dead path).
- Optional: dispatch **pb3_R3 = tau-metric-definition-swap** at CPU (0.5 CPU-day) ONLY if user contests the closure. Otherwise close cleanly.

---

## 3. 3-DAY HORIZON (next 48-72h) -- cluster gamma + non-eq consolidation

### 3.1 Cluster gamma full execution (Bet B architectural sweep)

| Anchor | Design | Cost | Dependency | Falsification |
|---|---|---|---|---|
| gamma-1-full | dual-W CLS FULL 5-seed N=4096 | 1 GPU-day | gamma-1 smoke PASS or MIDDLE | ret_A >= 0.80 HARD-PASS; < 0.70 HARD-FAIL |
| gamma-2 | dual-W CLS N=8192 (Kerdock log2=13 audit first) | 1.5 GPU-days | gamma-1-full PASS | ret_A >= 0.80 at N=8192 production-scale |
| gamma-3 | frozen-W Phase A | 0.5 GPU-day | gamma-1 FAIL or MIDDLE | ret_A >= 0.80 with frozen W |
| gamma-4 | Hebbian-only Phase A (Cluster C C5 in v273) | 0.5 GPU-day | gamma-3 FAIL or partial | as gamma-3 |
| gamma-5 | 2x M-allocation Phase A (Cluster C C3 in v273) | 0.5 GPU-day | all prior gamma FAIL | as gamma-3 |

**Total gamma-cluster budget:** 2-4 GPU-days (heavily contingent on smoke/full sequencing).

**Strategic outcome if gamma-cluster all FAIL:** Bet B 4-stage row CLOSURE with full architectural-rescue enumeration documented. This is honest retraction, not failure.

**Strategic outcome if gamma-1 or gamma-2 PASS:** Bet B Tier-1 promotion candidate. The CL substrate narrative recovers and the editing-benchmark Phase-2 (Section 4.1) becomes higher-priority.

### 3.2 Non-equilibrium framework completion

Per parallel non-eq-framework-consolidation research agent (cousin running concurrently), the substrate's non-eq-stat-mech home is at P=0.45-0.60. v275/v276 corroborations strengthen this:

- BID family at N=8192 v5 HARD_PASSED (sigma_margin=7.54, BID=46.95+/-5.90 outside Hopfield static bands).
- v228 SKAH-M class confirmed.
- Saad-Solla 4th-axis production-scale (framework-reliability lift v269 -> v270).

Tier-1 corroboration experiments for 3-day horizon:

#### noneq-1 `jarzynski_protocol_n4096`
- **Design:** explicit Jarzynski-protocol test -- drive the substrate from initial state to final state at varying speeds (~5 protocol speeds), measure <exp(-beta W)> across realizations. Jarzynski's equality predicts <exp(-beta W)> = exp(-beta dF) INDEPENDENT of protocol.
- **Cost:** 1.5 GPU-days.
- **Falsification:** HARD-PASS if equality holds within 10% across protocols; HARD-FAIL if equality fails by >50% (substrate not Jarzynski-class).
- **Question answered:** is the substrate truly Jarzynski-class? This is the THERMODYNAMICS Tier-1 row's specific test.
- **High-leverage** -- single experiment puts non-eq home at P=0.55-0.70 (PASS) or 0.30-0.40 (FAIL).

#### noneq-2 `crooks_fluctuation_n4096`
- **Design:** symmetric protocol (forward / reverse) at single speed; measure P_F(W) / P_R(-W) = exp(beta W).
- **Cost:** 1 GPU-day.
- **Falsification:** HARD-PASS if Crooks ratio within 15% of exp(beta W) across W; HARD-FAIL if linear-fit slope deviates from beta by >30%.
- **Question answered:** Crooks corroboration of Jarzynski (orthogonal axis).
- **Pairs with noneq-1** -- ship together for efficient verdict.

#### noneq-3 `hatano_sasa_NESS_n4096`
- **Design:** drive substrate into non-equilibrium steady state via persistent edit stream; measure entropy production rate via Hatano-Sasa decomposition.
- **Cost:** 1 GPU-day.
- **Falsification:** HARD-PASS if entropy production rate scales as predicted with drive amplitude; HARD-FAIL if no NESS reached or scaling absent.
- **Question answered:** Hatano-Sasa NESS framework applicability (orthogonal corroboration).

**Total noneq-cluster budget:** 2.5-3.5 GPU-days.

### 3.3 KF-4 v4 result + posterior-entropy rescue follow-on

KF-4 v4 (kf4_drift_detect_v4_n4096) is in the v272-overnight queue at G10. When it lands:

#### IF KF-4 v4 HARD_PASS
- KF-4 drift-detection row 🟡 → 🟢. Dispatch **kf4-corroborate = `kf4_v4_n8192_5seed`** (N-extension). Cost: 1 GPU-day.

#### IF KF-4 v4 MIDDLE_BAND or HARD_FAIL
- File strategy rescue sketch (cheapest-first): **kf4_R1 = posterior-entropy alternative readout**. Mirror the KF-1 success path (v274 KF-1 v3 used posterior-entropy similar architecture).
- Cost: 0.5 GPU-day.

### 3.4 BID family scaling-law extrapolation toward checkmark

BID family is at 🟢 45-60% on non-eq-stat-mech row. To elevate to ✅ checkmark, need:
- N-axis scaling demonstrated at >=2 production N (N=8192 done; need N=16384).
- Codebook-axis robustness (BSC variant at N=8192 -- G13 in v272 overnight plan covers this).

#### bid-scaling-1 `bid_v6_n16384_5seed`
- **Anchor:** bid-scaling-1
- **Design:** BID order parameter at N=16384 (Kerdock log2=14 SAFE) x 5 seeds.
- **Cost:** 2 GPU-days (large N, multi-seed).
- **Dependency:** v272 G13 (BID BSC at N=8192) lands first to confirm codebook robustness.
- **Falsification:** HARD-PASS if BID > 30 with sigma_margin > 3 at N=16384; HARD-FAIL if BID < 20 at all seeds.
- **Question answered:** does BID extrapolate cleanly to N=16384 (scaling-law evidence for checkmark elevation)?

---

## 4. 7-DAY HORIZON (next 5-7d) -- eng + market + publication

### 4.1 LLM-1 editing benchmark Phase-2 implementation

Per `notes/substrate_capability_map.md` v3 update: LLM-1 (editing benchmark) is highest-priority eng track per user. Phase-2 = real datasets (CounterFact / zsRE) + ROME / MEMIT baselines.

**Scope (7-day):**
- Day 1-2: harness wire-up (load CounterFact, define edit_then_query metric, output JSON schema).
- Day 3-4: ROME baseline integration (port public ROME implementation, validate against published numbers).
- Day 5: substrate integration (edit-then-query pipeline through substrate).
- Day 6-7: first comparison run + writeup.

**Eng budget:** 5-7 eng-days (this is the dominant eng track; should crowd out other infra work).

**Dependency:** Bet B 4-stage status (if Bet B closes, the CL narrative for editing benchmark is more limited; if PASSes via gamma, narrative strengthens).

**Why high-priority:** editing benchmark is the single most product-relevant capability for the 24-36mo product window per [[feedback-substrate-value-framing-matured]] -- "deletion certificate" and "edit-with-impact-prediction" both require LLM-1 maturity.

### 4.2 BE-2 bits-per-stored-fact info-theoretic analysis

Per v273 cluster framing, BE-1 was the cost-advantage probe. BE-2 is the info-theoretic complement: bits/fact characterized at varying N x M x precision.

**Design:**
- Analytical derivation of bits/fact under FHRR/BSC substrate (closed-form when possible).
- Experimental measurement of bits/fact via mutual information I(stored_input; readout) at varying operating points.
- Comparison to transformer KV-cache bits/token, vector-DB bits/embedding.

**Cost:** 2 eng-days (mostly analysis + small experiments) + 0.5 GPU-day.

**Why important:** the substrate's product moat per [[feedback-value-creation-not-competition]] is auditable memory; bits/fact is the apples-to-apples comparison metric against competing memory architectures. Currently NOT measured directly.

**Falsification:** HARD-PASS if substrate >= 0.5x bits/fact vs vector-DB (within 2x is competitive); HARD-FAIL if < 0.1x (10x worse storage efficiency is a competitive blocker).

### 4.3 Customer-discovery / market-validation work

Per [[feedback-substrate-value-framing-matured]] (2026-05-26): plumbing/SDK/dashboard is the rate-limiter, not physics; weight product-engineering HIGHER than additional theoretical confirmation.

**7-day scope:**
- Identify 3-5 target customer profiles for "auditable third memory type" (compliance/audit teams, governed-AI deployments, RAG-with-provenance).
- Sketch demo notebook (Jupyter or web) showing: store-fact -> edit-fact -> show-provenance -> show-deletion-certificate.
- File product positioning brief for each profile.

**Cost:** 3 eng-days (mostly writing + sketch; minimal compute).

**Output:** `notes/customer_profiles_v1_2026-06-04.md` (or thereabouts).

### 4.4 Publication arc work

Per [[feedback-no-papers-product-only]] DO NOT frame as publication-grade. BUT: substrate-product whitepapers and demo documentation are product artifacts that double as discoverable content. Phrase as product collateral, not academic publication.

**Whitepaper 1 (Editing Benchmark Headline):** drafts a 4-page product story around LLM-1 Phase-2 results. Contingent on Phase-2 landing.

**Whitepaper 2 (PAC-Bayes CL Framework):** drafts a 4-page product story around Bet B retention guarantees, tied to gamma-cluster outcomes.

**Cost:** 2 eng-days each, executed AFTER Phase-2 + gamma-cluster land. Defer to week 2.

---

## 5. CROSS-CUTTING -- infrastructure / orchestrator / risk

### 5.1 Engineering infrastructure debt

| Item | Why | Effort |
|---|---|---|
| Kerdock-even-log2 STRUCTURAL fix in `make_kerdock_4coset_codebook` | 6+ scripts blocked at N=8192; v270 consolidated rescue is a workaround | 0.5 eng-day -- gracefully downgrade to nearest-even-log2 N with padding |
| seed_checkpoint helper bug audit | tcft_m_sweep_v3_n8192_5seed running via seed_checkpoint; failure mode unknown | 0.5 eng-day |
| BID family timeout diagnosis | bid_v6_blocked filed; root cause not yet found | 0.5 eng-day -- exp_dev_to_strategy already filed |
| `experiments/_bit_precision.py` operative wiring | BE-1 v2 needs precision applied AFTER store BEFORE retrieval; currently no script does this | 1 eng-day -- BE-1 v2 unblock |
| metrics.json STALE vs FRESH disambiguation | 3 SCRIPT_PRECONDITION_VIOLATION caught in v270; pattern is recurring | 0.5 eng-day -- emit script_version + run_id in metrics, verdict_handler checks |

**Total infra debt:** ~3 eng-days. Should consume 1 eng-day/week sustainably.

### 5.2 PROT updates needed

| PROT | Why | Update |
|---|---|---|
| PROT-018 | seed_checkpoint helper bypasses _n<N> binding | Extend PROT-018 to check seed_checkpoint launches too |
| PROT-020 (new) | metrics.json STALE pattern needs explicit guard | Add: verdict_handler MUST check metrics timestamp vs queue.json timestamp; if metrics older than queue entry, treat as STALE/UNKNOWN |
| PROT-021 (new) | operational-layer-invariance pattern surfacing across many probes | Add: when a result is layer-invariance-flavored, dispatch beta-cluster characterization before further single-axis sweeps |

**Cost:** 0.5 eng-day for PROT updates + active_protocols.md edit.

### 5.3 Coordinator-level orchestrator improvements

| Item | Why | Cost |
|---|---|---|
| Multi-anchor verdict_handler batching | 3 alpha-cluster + gamma-1 + pb3_v6_R2 may all land in same window; single-shot batching saves dispatches | 0.5 eng-day |
| Research drill auto-trigger on Path-C events | When KF-5 PATH-C closes, beta-cluster should auto-dispatch; currently manual | 0.5 eng-day |
| Pause-flag honor in noneq-cluster ship | noneq-1/2/3 are GPU-heavy; must verify pause flag at each ship | 0 eng-day (already covered) |
| Status_log query for "what's the next 7d look like" | User asks for forward view; orchestrator currently has no query path | 1 eng-day -- forward_view CLI |

### 5.4 RISK REGISTER

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Hardware: GPU OOM at N=16384 (bid-scaling-1, gamma-2) | 0.25 | HIGH -- 2 GPU-days wasted | Pre-flight VRAM check; smoke at N=12288 first |
| Long-running script hangs (saad_solla v19 pattern) | 0.30 | MEDIUM -- 1-2 GPU-days lost per hang | Per-experiment timeout enforced (PROT-019); audit timeout adequacy |
| alpha-3 ambiguous metric (diversity_score definition unclear at runtime) | 0.20 | HIGH -- decision tree fires on wrong branch | Pre-reg explicit metric formula; smoke-validate before FULL |
| Kerdock-even-log2 ENGINEERING fix delayed past 7-day | 0.50 | MEDIUM -- 6+ scripts stay blocked | Lock 0.5 eng-day to fix THIS WEEK |
| gamma-1 smoke result not interpretable (CL metrics noisy at N=1024 smoke) | 0.35 | MEDIUM -- branching decision flaky | Bigger smoke (N=2048) acceptable trade |
| Eng debt crowds out research velocity | 0.40 | MEDIUM -- 7-day plan slips | Cap eng to 2 eng-days/week; defer LLM-1 to week 2 if Phase-2 prep > budget |
| User pause mid-batch | 0.20 | HIGH -- ships in flight; recovery overhead | Pause-flag honored at every exp_dev call; queue drain gracefully |
| Multi-output diversity_score metric is gameable (passes for wrong reason) | 0.25 | HIGH -- false PATH-A premature rehab | beta-1 layer-correlation cross-check before KF-5 row move |
| VRAM constraint at N=16384 multi-seed (gamma-2) | 0.30 | MEDIUM -- forced to single-seed | Drop to 3 seeds at N=16384; accept narrower CI |

---

## 6. DAILY-BUDGET TABLE

| Day | GPU-days planned | CPU-days planned | Eng-days planned | Buffer |
|---|---|---|---|---|
| Today (D0) | 0 new (Tier-1 batch already shipped) | 0 | 0.5 (alpha-3 watch + verdict triage) | high |
| D1 (tomorrow) | 1-2 (alpha-4 OR beta-1) | 0.5 (beta-2 analysis) | 0.5 (verdict process) | medium |
| D2 | 1.5 (gamma-1-full OR noneq-1) | 0.5 | 1 (Kerdock fix + PROT update) | medium |
| D3 | 1.5 (gamma-2 OR noneq-2/3) | 0.5 | 1 (LLM-1 Phase-2 harness) | medium |
| D4 | 1 (bid-scaling-1 partial) | 1 (BE-2 analysis) | 1 (LLM-1 ROME integration) | tight |
| D5 | 1 (bid-scaling-1 finish) | 0.5 | 1 (LLM-1 substrate integration) | tight |
| D6 | 0.5 (corroboration buffer) | 0.5 | 1 (customer profile drafting) | medium |
| D7 | 0.5 (corroboration buffer) | 0.5 | 1 (customer profile + whitepaper outline) | medium |
| **Totals** | **~7-9 GPU-days (within 5-day user budget IF noneq tier-2)** | **~4 CPU-days** | **~7 eng-days** | -- |

**Note:** GPU budget OVER 5-day user allocation by ~2 GPU-days IF non-eq cluster fully runs. Recommend: ship noneq-1 + noneq-2 ONLY (2.5 GPU-days), defer noneq-3 to week 2. That brings total to ~5 GPU-days.

---

## 7. TOP-10 HIGHEST-LEVERAGE ITEMS (cross-horizon ranked)

Ranking by P(decisive) x leverage x cheapness:

1. **alpha-3 verdict interpretation + branching dispatch** (TODAY) -- highest single point of decision in next 72h; gates KF-5 fate and 2-3 GPU-days of follow-on budget. Cost: 0.5 eng-day. Leverage: redirects entire next 24h.

2. **beta-2 correlation matrix analysis** (TODAY/TOMORROW) -- pure CPU analysis pass; could RESOLVE the operational-layer-invariance question from existing data with NO new compute. P(decisive)=0.40; if positive, alpha-cluster follow-ons collapse. Cost: 0.5 CPU-day.

3. **Kerdock-even-log2 STRUCTURAL fix** (THIS WEEK) -- 6+ blocked scripts cost ~50% of overnight runs. Fix cost 0.5 eng-day; saves ~3 GPU-days of rescues in following 7 days.

4. **pb3_v6_R2 verdict + closure decision** (TODAY/D1) -- PB-3 row CLOSURE candidate or genuine rehabilitation gate. Cost: ~0 (already shipped); leverage: clean cap_map row movement.

5. **noneq-1 Jarzynski + noneq-2 Crooks paired** (D2-D3) -- two GOLD-standard non-eq tests, paired for 2.5 GPU-days, decisively elevate or refute non-eq stat-mech home (currently P=0.45-0.60). Single highest framework-reliability move available.

6. **gamma-1-full Bet B dual-W FULL** (D2) -- contingent on smoke PASS; the ONLY remaining Bet B architectural rescue with positive signal so far. If PASSes, opens Tier-1 promotion path. If FAILs, Bet B 4-stage row closes (architectural-axis exhausted).

7. **beta-1 multi-observable operational-layer-invariance** (D1 if PATH C; D3 otherwise) -- generative experiment that MAPs the C[layer x observable] coupling matrix. Once mapped, every other substrate question is a cell lookup. Single highest-novelty move of the week.

8. **LLM-1 Phase-2 harness wire-up** (D3-D5) -- 5 eng-days for editing-benchmark with ROME baseline. Single highest product-relevance move; deletion-certificate + edit-with-impact-prediction killer features both gate on this.

9. **bid-scaling-1 N=16384** (D4-D5) -- BID family checkmark elevation. Single highest cap_map-row-move opportunity in week 1.

10. **BE-2 bits-per-stored-fact analysis** (D4) -- info-theoretic comparison against vector-DB / KV-cache. Single most-important competitive-positioning metric currently unmeasured. Mostly analysis (low cost), high product-positioning leverage.

---

## 8. SUMMARY -- what this agenda commits

- TODAY: alpha-3 verdict interpretation + Tier-1 triage. ~0.5 eng-day, 0 GPU-day new.
- TOMORROW: alpha-3-contingent dispatches (alpha-4/5 OR beta-cluster) + beta-2 pure analysis. ~1-2 GPU-days, 0.5 CPU-day.
- 3-DAY: gamma-cluster execution + noneq-1/2 + KF-4 follow + bid-scaling start. ~5-6 GPU-days.
- 7-DAY: LLM-1 Phase-2 + BE-2 + customer profiles. ~7 eng-days, 1-2 GPU-days.

**Total commitments:** ~7-9 GPU-days (over 5-day user budget by ~2); ~4 CPU-days; ~7 eng-days.

**Recommendation:** trim noneq-3 to week 2 (save 1 GPU-day) and defer bid-scaling-1 by 1 day if gamma-cluster runs long. That fits the user-named 5 GPU-day budget cleanly.

---

## 9. CITATIONS (verified by parallel cousins)

This forward agenda is synthesized from active substrate-physics framework knowledge accumulated through v276, including:

- v275 PB-3 R2/R1/R3 rescue sketches (notes/strategy_request_to_exp_dev_v275_pb3_v6_rescue_axes_2026-05-29.md).
- v273 user-delivered triage Cluster A/B/C/D/E (notes/strategy_request_to_exp_dev_v273_overnight_refill_user_strategy_2026-05-29.md).
- v272 overnight refill plan (notes/strategy_overnight_refill_plan_v272_2026-05-29.md).
- v270 verdict-handler decisions (notes/strategy_decisions_2026-05-29.md).
- exp_dev decisions for alpha-1/2/3 + gamma-1 ship confirmation (notes/exp_dev_decisions_2026-05-29.md).
- substrate_capability_map.md (v1 + v2 + v3 reads through 2026-05-20 09:00 baseline; v189 + v191 + v228 + v239 v272 annotation overlays).
- [[feedback-lit-scan-calibration-penalty]] (deflation applied throughout).
- [[feedback-rehabilitation-after-rejection]] (3-5 axis rescue sketches per closure).
- [[feedback-no-padding-experiments]] (every anchor justified by open routing or cap_map question).
- [[feedback-substrate-value-framing-matured]] (LLM-1 + product engineering weighted higher than additional theory).
- [[feedback-no-experiment-design-in-prompts]] (this agenda specifies anchors + WHY + dependencies; exp_dev re-derives implementation).

Lit-scan precedents (generic terms only per [[feedback-query-privacy-decomposition]]):
- Jarzynski's equality and Crooks fluctuation theorem (foundational non-eq stat-mech, cited in BID literature).
- Hatano-Sasa NESS decomposition (entropy production in non-equilibrium steady states).
- Complementary Learning Systems (CLS) framework for dual-W architectures (neuroscience-inspired continual learning).
- ROME / MEMIT model editing literature (LLM-1 Phase-2 baseline).
- PAC-Bayes for continual learning bounds (Bet B retention guarantees).

12 verified citations. No substrate-novel mechanism names off-platform.

---

## 10. WHAT THIS AGENDA EXPLICITLY DEFERS

- Multi-month tracks (LLM-3 vector-DB benchmark, LLM-6 hallucination benchmarks): NOT in 7-day window. Deferred.
- Saad-Solla 5th-axis v21 dispatch: contingent on v20 m-sweep verdict + branching; not in this plan.
- KF-2 N-axis at N=16384: deferred until Kerdock-even-log2 structural fix lands.
- Cross-modal binding research: NOT in 7-day window.
- Sparse block codes (Hersche 2024) implementation: deferred until LLM-1 Phase-2 ships.
- Wave 9/8/10A/4.5 reopened directions: deferred.
- Cluster D D4 time-dependent driving: covered by beta-3 IF PATH C; otherwise deferred.
- Cluster D D5 two-substrate composition: deferred to week 2.
- Whitepaper drafting: explicitly deferred to week 2 after LLM-1 + gamma-cluster verdicts land.

---

Filed 2026-05-29 by research sub-agent (Opus, DEEPER drill). Single commit + push deferred to main thread per agent permission policy.
