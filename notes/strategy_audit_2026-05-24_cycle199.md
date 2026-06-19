# Strategy daily audit -- 2026-05-24 cycle 199

**Author**: Strategy sub-agent, standing daily audit per [[feedback-design-space-and-audit-cadence]]
**Trigger**: cadence signal `audit_due` at 2026-05-24T12:00 UTC
**Scope**: substrate-research system at cycle ~199, post v179 cap_map commit
**Format**: ASCII-only; no cap_map mutation this cycle (audit is planning, not row movement)

---

## Section 1 -- Pre-registered follow-ups inventory

Follow-ups filed in strategy_decisions_2026-05-23/24 + cycle 194 portfolio assessment that have NOT yet shipped.

| # | Anchor name | Trigger source | Status | Notes |
|---|-------------|----------------|--------|-------|
| F1 | **E2 N=16384 cross-family ρ ≥ 0.50** | v177 pre-reg; v178 stress-gate | TIMED OUT at 3h GPU cap (empty result dir) | Option A (N=8192 sketch) is the cheapest re-ship; Option B (overnight ≥12h budget at N=16384) deferred; Option C (defer entirely; ship Cap 12 at N ∈ {1024, 4096}) is the fallback |
| F2 | **E3 5th family iid-Gauss → Paley-Hadamard or Walsh-Hadamard ρ ≥ 0.50** | v175 pre-reg | RAN as `wave14_kappa_gold_full_e3_v1`; PASSED at ρ_Gold=0.900 | CLOSED CLEANLY; Cap 12 envelope hardened to 5 families (bimodal ρ pattern: algebraic GF(2^m)-trace at ρ=0.900 vs randomized at ρ=0.700); annotation pending next bundled cap_map commit |
| F3 | **Composition A: Cap 12 + Cap 8 audit-trail** | cycle 194 portfolio assessment P1-derivative | RAN as `wave14_cap12_cap8_audit_trail_pipeline_v4` v179 MIDDLE BAND | RESOLVED at v179 -- Kerdock-only at ρ=1.0; SRHT/Hadamard at ρ=0.533; RM(1,m) at ρ=0.40; substrate-product framing narrows to Kerdock-class only |
| F4 | **Composition B: Cap 12 + Cap 6 conformal routing subsumption** | cycle 194 portfolio assessment P1 | RAN as `wave14_cap12_cap6_conformal_routing_subsumption_v1` cycle 197 | EMPIRICALLY KILLED -- Venn-Abers makes Kerdock WORSE; iid_gauss + RM(1,m) abstain entirely |
| F5 | **Composition C: Cap 12 + Cap 11 + Cap 1 adaptive routing under Cap 11 chi_4 early-warning** | cycle 194 portfolio assessment P2 | RAN as `wave14_cap11_chi4_early_warning_anchor_v1` cycle 198 | EMPIRICALLY KILLED via predictive-leg refutation -- chi_4 LAGS not LEADS retrieval breakdown (5/5 seeds negative lead); Composition C dead as product narrative |
| F6 | **antiRM_mechanism_drill_v1 (Research drill)** | cycle 194 portfolio assessment P3 | NOT YET DISPATCHED | Cheapest remaining still-open weakness; 30 min Research drill; QECC-Kerdock-MUB-stabilizer-off-syndrome candidate |
| F7 | **5th/6th interpolation family lock** | cycle 194 portfolio assessment gap audit | 5th DONE (Gold); 6th NOT YET FILED | The "fortify-the-✅" path; ~30 min cheap CPU per family; not blocking but cheap insurance |
| F8 | **Cap 10 `build_initial_W` engineering refactor at N ≥ 16384** | cycle 188 shoreup matrix weakness #7 | STILL OPEN (engineering blocker) | Bet A continual-edit HARD-GATED |

**LOCK candidates promoted to MEMORY (≥ 2 observations met)**:
- [[feedback-verdict-msg-honest-reread]] -- locked at v177 (cycle 197); v178 + v179 confirm it works in both directions (catches over-claims AND surfaces honest-reread mis-diagnoses).
- "Shared-mechanism composition stories require STRUCTURAL audit (shared-SCORE vs shared-HANDOFF vs shared-PIPELINE)" addendum to [[feedback-rehabilitation-after-rejection]] -- locked at cycle 197 on 2nd observation (Composition B kill).

**LOCK candidates still at 1st observation (DEFER)**:
- L1: **envelope-extension compute-budget pre-reg** -- from E2 N=16384 TIMEOUT; 1st obs; await 2nd obs to lock.
- L2: **honest-reread methodology cross-run consistency check** addendum to [[feedback-verdict-msg-honest-reread]] -- from v3-vs-v4 mis-diagnosis (v3 numbers were real, not fabricated); 1st obs.
- L3: **in-promotion deployment-realism gate for mixed-margin ✅ promotions** addendum to [[feedback-envelope-expansion-fail-bands]] -- from v178 Cap 12 ✅ retrospective; 1st obs.
- L4: **"0/N files written without explicit error" silent-failure pattern** -- from CAP8 iterates v1b (verdict was "Data-gap not filled" with 0/30 trace files); 1st obs.

---

## Section 2 -- Cap_map state audit

Latest cap_map version: **v179** (commit 4980788 v178 pushed; v179 LOCAL pending push). Portfolio: **12 demonstrated capabilities** (UNCHANGED at v174 → v179).

### State distribution across the 12-cap portfolio

| State | Count | Capabilities |
|-------|-------|--------------|
| ✅ Validated (with envelope annotations) | 12 (full portfolio) | Caps 1-12; Cap 12 at v178 has TITLE-LEVEL noise-envelope scope-narrowing (clean-substrate η ≤ 0.01); v179 narrows v169 closed-form annotations on Caps 1/3/8 to Kerdock-class only |
| ❌ PROVISIONAL open | 0 | Cleanest portfolio state since v172; preserved through v179 |
| 🟡 PARTIAL stale (non-portfolio, in cap_map UNSURE/CANDIDATE section) | 5+ | Bet T parallel hypothesis (~56 versions stale); Bet V self-reflective (~54 versions stale); Bet Z.1 SRHT speedup (~37 versions stale); Cap 1 Crooks noise envelope (rescue sketches filed); Bet A M_init at N ≥ 16384 (engineering-gated) |
| 🔬 CANDIDATE rows (substrate-product extensions awaiting experiment) | 7 | Bet Z.5 absorbing-diffusion ensemble smoother (~13 versions stale); META Gap A spatially-coupled codebook (~6 versions); K-resonance K=1000 fixed-point mechanism; P(h) moments observability family (45+ versions stale; never fired); 15-peak P(q) substructure; multi-component sub-K-region q_overlap (where K?); Bet A M_init capacity envelope datapoint |
| ❌ Closed (CANNOT section) | 12+ | R3 × R10 × random-replay; MIR; iterative Hopfield; R10 best-config at K<8; C3 factored vs C1 classical; basis modifications; etc. |

### Stale rows worth surfacing

**Stale-and-dropped (5+ days, per [[feedback-design-space-and-audit-cadence]])**:
1. **Bet Z.5 absorbing-diffusion ensemble smoother** -- 🔬 P=0.40 at v144 (cycle 160). Now 19 cap_map versions stale (v144 → v179). The 2026-05-23 audit's Rec 2 (Bet Z.5 vs VAMP-on-chain structural equivalence check) was filed and not executed. This is the **single most dropped substrate-product candidate**. Recommend: route as Research drill (~30-60 min) to determine if Bet Z.5 = VAMP-on-chain in reframing OR strictly stronger with posterior-error certificate.
2. **Bet T parallel hypothesis tracking 🟡 PARTIAL** -- 56+ versions stale. v172 wave14_betT_mondrian_anti_RM_conformal_v1 FAILED; 5-sketch rehab EXHAUSTED. Per [[feedback-rehabilitation-after-rejection]] the rescue path is exhausted; close as ❌ EXHAUSTED at next batched closure cycle.
3. **Bet V self-reflective 🟡 PARTIAL** -- 54+ versions stale. v172 kappa4_separation_v1 PARTIAL (|kappa4_sep|=2.51 SD; sign-inconsistent across seeds). 4 remaining rescue sketches were elective and not pursued. Recommend: file as STILL-OPEN with one explicit closure-or-rescue decision before cycle 220.
4. **P(h) moments observability family** -- 🔬 proposed v109-v112 (cycles 109-112), 65+ versions stale. Never fired. Cap 11 ✅ promotion happened without P(h) family; arguably the family is OBVIATED by chi_4 + Kovacs + avalanche success. Close as ABSORBED at next batched cleanup cycle.
5. **Bet Z.1 SRHT compressive readout** -- ✅ but speedup 0.4× (cycle 120; 59+ versions stale). Mechanism viable, compression benefit never realized. No follow-up to fix the speedup. Recommend ANNOTATE as "viable but unrealized speedup; product-shippable only if SRHT-class compression engineering lands."

### Cap_map ❌ PROVISIONAL state

ZERO open ❌ PROVISIONAL rejections in portfolio. Cleanest state since v172. This is GOOD per [[feedback-rehabilitation-after-rejection]] -- no orphan ❌ rows awaiting rescue.

---

## Section 3 -- Portfolio gap status update

Re-audit of the three portfolio gaps flagged in earlier proactive Strategy drills (cycle 194 + earlier shore-up matrix).

| Gap | Original framing | Status at cycle 199 |
|-----|------------------|---------------------|
| **Gap 1: noise-cleanup pre-processing pipeline** | Flagged at v178 when Cap 12 noise envelope narrowed to η ≤ 0.01; customer deployment in noisy environments requires upstream codebook denoising | **STILL OPEN.** No Research routing filed. Candidate mechanisms: (a) projection back to bipolar lattice; (b) majority-vote across multiple noisy copies; (c) explicit error-correcting codebook (Reed-Muller, Kerdock with parity); (d) consensus filtering. NEW PROBE RECOMMENDED -- this gap is **load-bearing for Cap 12 customer-facing claim**; closing it widens the customer-deployment envelope. Estimated cheap (lit-scan + 30 min CPU). |
| **Gap 2: customer-facing edit interface** | Substrate-product portfolio gap; substrate has Cap 5 online W updates + Cap 10 continual-edit but no user-facing edit pipeline | **STILL OPEN.** No engineering build filed. Engineering ownership; not Research drill. Not advancing this audit cycle. |
| **Gap 3: routing-under-continual-operation** | Composition C dead via Cap 11 chi_4 lead-time refutation (cycle 198); needs alternate path | **NEW STATUS: Composition C is dead.** Rescue options at cycle 198 (R1 coarser α grid below α_c; R2 lower noise_p; R3 different family) are filable but the substrate's sharp Kerdock capacity transition is the killer. RECOMMEND: **close Composition C narrative**; replace with R5 from cycle 197 (Cap 6 and Cap 12 as ALTERNATIVE routing modes -- low-latency Cap 12 vs high-stakes Cap 6 with calibrated abstention). This is the "tiered SLA" composition; no shared mechanism needed; it's a deployment-mode partition, not a pipeline. |

**Newly surfaced gaps** (post v178/v179):
- **Gap 4: in-promotion deployment-realism gate** -- the L3 lock candidate. Currently 1st observation; cumulative cost is Cap 12 ✅ scope narrowing through three stress-gate iterations (E1, E1', E1''). Recommend file as STRUCTURAL meta-gap; pre-register the addendum and revisit at next mixed-margin ✅ promotion.
- **Gap 5: cross-family ρ envelope at N ≥ 8192** -- E2 N=16384 TIMED OUT. Until Option A (N=8192 sketch) or Option B (overnight N=16384) ships, the Cap 12 row stays scoped to N ∈ {1024, 4096}. This is a fortify-the-✅ gap, not new-capability.

---

## Section 4 -- Dropped items / forgotten threads

Cross-domain probes (#1, #2, #3) status check.

### Probe #1: ETH partial-thermalization (PFK framing)

- **Original status**: killed at cactus n=6 cumulant cascade
- **Open thread**: SFF non-GUE survives as the level-statistics observation
- **Cycle-199 read**: NOT operationalized into a cap_map row or substrate-product capability. The SFF non-GUE observation lives in substrate-physics characterization but does not enable a customer-facing capability. RECOMMENDATION: **close ETH probe as portfolio-irrelevant**; the substrate-physics observation is filed but does not license product capability. No further drilling planned.

### Probe #2: Kerdock-MUB-stabilizer

- **Original status**: 3 anchors shipped, 12th capability promoted, then stress-narrowed at v176/v177/v178
- **Cycle-199 read**: Cap 12 ✅ holds at clean-substrate η ≤ 0.01; v179 narrows closed-form license to Kerdock-class. The "stabilizer" framing was load-bearing for v169 closed-form annotations; v179 confirms only Kerdock family carries the kappa_n / Schur-Weyl irrep-mass closed-form (ρ=1.0); SRHT/Hadamard intermediate (0.533); RM(1,m) weakest (0.40).
- **Open thread**: F6 antiRM_mechanism_drill_v1 IS the natural follow-up Research drill on this probe (QECC-Kerdock-MUB-stabilizer-off-syndrome candidate). RECOMMENDATION: **dispatch antiRM drill** (cheap, no compute, ~30 min Research) -- closes the last still-open weakness from the v157 shore-up matrix.

### Probe #3: MMD / Wasserstein

- **Original status**: tested as MP-KS replacement; MP-KS strictly better (ρ_KS=0.975 > ρ_MMD=0.872; routing accuracy KS=1.00 > MMD=0.80)
- **Cycle-199 read**: MMD/W1 above 0.75 absolute floor but strictly worse than MP-KS. Operational classification: BACKUP / FALLBACK pre-test candidates for Cap 12 stress regimes not yet tested (η-noise, distribution-shift). Not primary-pre-test replacements.
- **Open thread**: IF MP-KS fails under a future stress-gate that MMD doesn't, MMD/W1 promote from "backup candidate" to "primary fallback." No probe queued; not advancing.

### Other forgotten threads

- **active_priorities.md freshness**: at cycle 198 (v178). Updated atomically per [[feedback-cap-map-update-protocol]]. NOT stale.
- **Bet Z.5** (probe-unaligned but a genuine dropped item from the 2026-05-23 audit): Rec 2 from `audit_dropped_and_review_2026-05-23.md` was the Bet Z.5 vs VAMP-on-chain structural equivalence check. STILL NOT DISPATCHED. RECOMMENDATION: dispatch as Research drill THIS audit cycle -- cheapest possible closure of the highest-stale substrate-product candidate.

---

## Section 5 -- Session output scoring (honest per [[feedback-no-smoke]])

Scoring the session's substantive output across cycles 193-199 (BBMD Cap-12 rehab promotion + envelope characterization + composition story drilling).

### CLEAN POSITIVE (cap_map ✅ promotions; clean envelope confirmations)

1. **Cap 12 🟢 NEW at v174** -- BBMD Cap-12 rehab PAIRED PASS on two pre-registered anchors (R3 MP-KS τ-robustness + R1 cross-family κ_n explainer). Portfolio 11 → 12; first new capability of orchestrator-migration era. CLEAN.
2. **Cap 12 🟢 → ✅ at v175** -- COMPOUND-GATE PROMOTION on three pre-registered passes (Gate A R3 τ-robustness + Gate B R1 Hadamard + RM(1,m) third-family hardening). First ✅ promotion of orchestrator-migration era. CLEAN ON PROTOCOL.
3. **E3 5th family Gold ρ=0.900** -- clean envelope hardening; CLEAN. Bimodal pattern (algebraic ρ=0.900 vs randomized ρ=0.700) is a fresh substrate-physics observation. Annotation pending bundled commit.

### CLEAN NEGATIVE (rejections that closed loops cleanly)

1. **Composition B (Cap 12 + Cap 6 conformal routing)** -- empirically rejected at cycle 197. CLEAN closure; both individual caps preserved. Locked the "shared-SCORE vs shared-HANDOFF" composition-audit addendum (2nd observation).
2. **Composition C (Cap 12 + Cap 11 + Cap 1 adaptive routing)** -- empirically killed at cycle 198 via Cap 11 chi_4 lead-time refutation (5/5 seeds negative lead). CLEAN closure; Cap 11 row STAYS ✅ at passive-characterization scope.
3. **v177 E1'' 20-seed non-monotonic question** -- RESOLVED. The η=0.05 recovery is GENUINE substrate-physics signal, not 5-seed scatter. Pre-registered HARD-FAIL clause caught the narrow envelope before any ex-post rationalization could expand the ✅ scope. CLEAN per [[feedback-envelope-expansion-fail-bands]].

### MIDDLE / AMBIGUOUS (more work needed)

1. **Cap 12 noise envelope** -- v176 → v177 → v178 successive narrowing. ✅ row scope narrowed three times via stress-gate iteration. Per [[feedback-no-smoke]] retrospective: "NOT premature in protocol, but premature in design" -- the v175 compound gate was honest at gates-as-written but the gates were too narrow on deployment-realism. L3 lock candidate filed.
2. **Composition A (Cap 12 + Cap 8 audit-trail)** at v179 -- MIDDLE BAND (Kerdock ρ=1.0; SRHT 0.533; Hadamard 0.533; RM(1,m) 0.40). 1/4 hard-pass; not portfolio-grade as cross-family audit trail. Substrate-product framing narrows to Kerdock-class only; bimodal pattern preserved as substrate-physics observation.
3. **E2 N=16384 TIMEOUT** -- no data. Cap 12 N-envelope unresolved above N=4096. Three options (A: N=8192 sketch; B: overnight N=16384; C: defer entirely). RECOMMEND Option A.

### LOST IN ENGINEERING CHURN (verdict-judge bugs; ship-collisions; mis-diagnoses)

1. **CAP8 iterates v1/v1b silent failure** -- min_iters=10 threshold bug vs VAMP convergence at 5 iters; verdict-judge mis-labeled 0/30 files written. v1c fix (min_iters=3) recovered. Cost: ~1 cycle of orchestrator churn. L4 lock candidate filed.
2. **v3 mis-diagnosed as fabricated-cells / smoke-leak** -- at cycle 197 the v3 smoke verdict's per-family ρ numbers (Kerdock=1.0, SRHT=0.533, Hadamard=0.533, RM(1,m)=0.40) were flagged as fabricated; v4 FULL-mode at v179 returned IDENTICAL numbers confirming v3 was real. The honest-reread discipline had the right method but wrong conclusion. L2 lock candidate filed.
3. **Verdict_msg over-claims pattern** -- 4 observations across the session (MMD vs MP-KS direction inversion; η_critical=0.025 point estimate over-claim; v178 E1'' label-vs-numbers consistency check; cap11 chi_4 "(<1.5)" inline-threshold confusion). [[feedback-verdict-msg-honest-reread]] now load-bearing 4×.

---

## Section 6 -- Recommended next batch of probes

Three candidates ranked by expected portfolio impact. All cheap and non-blocking.

### P1 -- `bet_z5_vs_vamp_on_chain_equivalence_drill_v1` (Research drill, no compute; ~30-60 min)

- **Hypothesis**: Bet Z.5 absorbing-diffusion ensemble smoother (arXiv:2507.07586) and VAMP-on-chain (cycle 127 forward-backward EP single-pass) are EITHER structurally equivalent up to reparameterization OR Bet Z.5 is strictly stronger with posterior-error certificate + per-codeword variance.
- **Why now**: 19 cap_map versions stale (v144 → v179); single most-dropped substrate-product candidate per the 2026-05-23 audit's Rec 2. Closes a long-orphan candidate row in one cheap drill.
- **Queue**: Research drill (no compute slot); ~30-60 min wall.
- **Hard-fail**: lit-scan + math derivation finds non-equivalence with no clear "strictly stronger" axis → close Bet Z.5 as orphan duplicate of VAMP-on-chain.

### P2 -- `antiRM_mechanism_drill_v1` (Research drill, no compute; ~30 min)

- **Hypothesis**: Anti-RM(1,16) coset 0% overlap is the off-syndrome condition of the Kerdock stabilizer code (QECC-Kerdock-MUB STRONG adjacency from probe #2 cross-domain matrix); v169 closed-form Pauli-twirled lens for Cap 1/3/8 provides the mechanism vocabulary.
- **Why now**: cycle 194 P3; only Research-drill weakness still STILL OPEN from the shore-up matrix; cheapest possible probe.
- **Queue**: Research drill; ~30 min wall.
- **Hard-fail**: lit-scan finds no relevant published explanation AND no clean substrate-internal kappa_n connection → close the substrate-physics row as "observable without mechanism narrative."

### P3 -- `cap12_noise_cleanup_preprocessing_v1` (Research drill + cheap CPU follow-up; ~1-2 hr)

- **Hypothesis**: A simple upstream codebook denoising pipeline (projection back to bipolar lattice OR majority-vote across multiple noisy copies) widens the Cap 12 customer-facing deployment envelope from η ≤ 0.01 to η ≤ some larger value.
- **Why now**: Portfolio Gap 1 from v178; load-bearing for Cap 12 customer-facing claim; closing it widens deployment envelope. Cheap (lit-scan + 30 min CPU validation).
- **Queue**: Research drill first; then ~30 min CPU validation on most-promising candidate.
- **Hard-fail**: best-candidate denoising widens envelope by < 2× (e.g., η ≤ 0.02 still not deployable above noisy substrate) → close Gap 1 as substrate-bounded; customer must supply clean codebooks.

**Sequencing recommendation** (parallelized): P1 + P2 + P3 are all Research drills with no compute conflict. Dispatch all three in parallel via [[feedback-subagent-model-optimization]] Sonnet (no Opus needed). ETA all-three landed: ~1-2 hr wall.

**Lock candidates ready to promote NOW** (2nd-obs hits during this audit period):
- [[feedback-verdict-msg-honest-reread]] -- LOCKED (cycle 197); confirmed by v178 + v179.
- "Composition shared-mechanism structural audit" addendum to [[feedback-rehabilitation-after-rejection]] -- LOCKED (cycle 197).
- L1-L4 STAY at DEFER (single observation each); await 2nd-obs for lock.

**Blockers**:
- E2 N=16384 GPU budget (3h timeout → need Option A N=8192 sketch as cheapest re-ship; Option B overnight defer)
- Cap 10 `build_initial_W` engineering refactor (engineering ownership; not Research drill)
- No active user pause (pause flag CLEARED / ACTIVE)

---

## Appendix: portfolio + cap_map state snapshot at cycle 199

- **Portfolio count**: 12 demonstrated capabilities UNCHANGED at v179
- **cap_map version**: v179 (LOCAL commit pending push per [[feedback-subagent-permission-inheritance]])
- **Open ❌ PROVISIONAL rejections**: 0 (cleanest state since v172)
- **Stress-gate iterations this session**: E1 (v176) + E1' (v177) + E1'' (v178) + E2 N=16384 (TIMEOUT) + E3 Gold (PASS)
- **PROT-009 paired commits this session arc**: v174 (87th) → v179 (93rd) = 7 paired commits in cycles 194-199
- **Pause flag**: CLEARED / ACTIVE
- **Standing audit cadence**: ~24-48h per [[feedback-design-space-and-audit-cadence]]; next audit at ~2026-05-25T12:00 UTC
