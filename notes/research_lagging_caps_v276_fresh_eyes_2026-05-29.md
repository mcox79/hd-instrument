# Fresh-eyes research drill: lagging capability rows at v276

Filed 2026-05-29 by research:opus on user explicit request (post-v276 batched 6-verdict + CPU drain wave + tcft seed-checkpoint window).

Scope: ALL capability-map rows currently labeled yellow / yellow-smoke / UNSURE / AT-RISK / 2nd-strike / partial-decoupling / decoupled / un-elevated-after-multiple-cycles. Each row gets a fresh-eyes pass that asks (1) what the row currently claims, (2) what evidence is missing for elevation, (3) what NEW evidence from v270-v276 might have narrowed or widened the path, (4) what new substrate-physics or framework angle would inform the next rescue, (5) cross-row insight, (6) concrete rescue test sketch at anchor-design level.

Per [[feedback-no-experiment-design-in-prompts]] this note does NOT specify anchor names, sweep grids, threshold formulas, HF1/HF2/HF3 numerical bounds, queue choice, or pre-committed cap_map decisions. exp_dev owns those.

Per [[feedback-lit-scan-calibration-penalty]] all P estimates are deflated 0.15-0.25 from raw lit-scan reads; novel-synthesis P is capped at 0.50; HARD-FAIL thresholds are pre-registered at the row level not the experiment level.

Per [[feedback-query-privacy-decomposition]] only generic math terms used in external queries.

---

## HEADLINE

15 lagging rows audited. 5 carry HIGH expected-value rescue paths because they sit on the killer-feature critical path AND have at least one un-attempted axis surviving the v270-v276 narrowing. Ranked highest-EV first:

1. **KF-2 BE-1 cost-advantage (W-magnitude-operative test)** -- highest EV. Cluster A is the lit-precedent path; 0/4 attempts so far; deflated P=0.42.
2. **Bet B Tier-1 architectural rescue (Cluster C, frozen-W or wider-Phase-A)** -- 4-axis training-axis ceiling structurally confirmed v276; architectural is the only remaining path; deflated P=0.35.
3. **KF-5 codebook-axis steerability multi-N replication** -- first POSITIVE steerability axis (v274) capped at single-N 3-seed; promotion gate is multi-N; deflated P=0.50.
4. **PB-3 critical-slowing definition swap (tau definition rescue arm)** -- 2-strike at flat tau_recovery=0.0 in v275; the FLAT-EXACT signal hints at a measurement-collapse not physics-collapse; deflated P=0.30.
5. **Cap 3 streaming-NESS at multi-basin operating point (degeneracy rescue)** -- v276 NESS audit showed single-attractor trapping; needs operating point WITH multi-basin to even test; deflated P=0.30.

Five MEDIUM-EV rows have rescue paths but are gated on the high-EV outcomes or have only fringe rescues remaining: AXIS-4 hysteresis-killer (HIGH-BETA rescue), KF-4 drift detection (LABELED-AT-RISK persistent), AXIS-3 triple-point (operating-point rescue), KF-3 cross-codebook sub-feature (kerdock-restricted), TCFT erase-time-axis (N-up).

Five LOW-EV rows are structurally near-saturated for further drilling: HS-class non-eq (3-strike v276 CONCENTRATION recommendation, surviving Crooks/Sagawa-Ueda/drift-diffusion-BP/free-probability claim the rest), SKAH-M green 55-70% (already class-confirmed at v228, additional drilling adds little), anti-spectral-graph green-smoke 55-70% (single-N + single-anchor), edge-of-chaos Lyapunov yellow-smoke 55-68% (Arnold-tongue v122 closure constrains), killer-feature phase-class profile (composite row absorbs component lifts; not directly drillable).

Cross-row insight: the 3rd HS-class exclusion at v276 + the v275 KF-5 steerability_partial_decoupling are not unrelated -- both point to substrate operating in a **NESS-degenerate single-basin regime at the tested operating points** where many non-eq order parameters trivialize. This argues for a separate **operating-point search drill** (multi-basin reach) before drilling additional frameworks.

---

## Cheap decisive test

For each row below, the rescue sketch names ONE cheap decisive next-evidence step at anchor-design abstraction. The orchestrator + exp_dev own anchor names, sweep grids, and numerical thresholds. The decisive criterion is always: "if the rescue path is the right framework, the next anchor's per-cell evidence improves above the current band's lower bound by at least the calibration-penalty deflation amount."

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL at row level)

Each row carries a row-level HARD-PASS and HARD-FAIL gate. HARD-PASS = at least one rescue arm produces production-scale (5-seed multi-axis) evidence within the row's current evidence-density quartile. HARD-FAIL = ALL named rescue arms close with HARD_FAIL or MIDDLE_BAND with no axis-orthogonal corroboration; row moves to closed-pending-rehabilitation status.

---

# ROW-BY-ROW FRESH-EYES PASS

## Row 1. KF-2 BE-1 cost-advantage (AT-RISK; STRATEGIC_INTERPRETATION_OVER_CLAIM v272/v273; cluster-A still pending)

**Current claim.** KF-2 edit-isolation passes precision-floor at FP32/FP16/INT8/INT4/INT2/INT1 (v272 BE-1 sweep 6 anchors all max_iso<0.05). STRATEGIC narrative "32x cost-advantage" OVER-CLAIMED at probe level because per-cell evidence shows quantization-INSENSITIVE iso (INT1 binary identical to FP32 iso pattern) which means W-magnitude was NOT operative in the isolation test design. v273 Cluster A (A1 soft-readout / A2 retrieval-accuracy / A3 TCFT-var-ratio / A4 multi-hop) explicitly tests W-magnitude operativity. Current row status: GREEN edit-individual-bindings checkmark with AT-RISK + STANDARD-BASELINE-CORROBORATION annotation (v275 v2 audit STANDARD-path max_iso=0.0202 was a partial defuse; STANDARD baseline established but cost-claim not validated).

**Missing evidence for elevation.** A test where W-magnitude IS operative AND the precision-floor result still holds. The current 6-anchor BE-1 sweep collapses identically because the argmax test is codebook-structure-dominated not W-magnitude-dominated. A retrieval-accuracy or softmax-readout test where W enters the inference path with magnitude-dependent contribution is the canonical evidence form. A multi-hop chain test where W is iterated would be stronger (errors compound through magnitude-dependent dynamics).

**v270-v276 narrowing.** v275 kf2_isolation_proof_v2_audit STANDARD-baseline production-scale HARD_PASS (max_iso=0.0202 25/25 cells) ESTABLISHES the standard-path baseline distinct from BE-1 path. This is structurally important: it isolates whether the "quantization-insensitive" observation was test-specific (BE-1 path collapses on quantization-equivariant codebook isolation) or substrate-wide (W really doesn't carry information). Cluster A1-A4 GPU-queued per v273 binding routing; verdicts pending. The STANDARD baseline at standard precision DOES track theory_bound within 30% (within_theory_frac=0.80), so substrate edit-isolation IS quantitative -- this rules out "W is irrelevant" globally.

**Fresh angle: substrate-physics + framework reading.**

Framework reading per modern Hopfield + dense-AM literature: when codebook is a 2-design (Kerdock 4-design) AND query is via argmax over codebook similarities, the argmax is determined by RELATIVE rank not absolute magnitude. Quantization-equivariance under rank-preserving maps is a documented property (rank-preserving discretization). This means the v272 BE-1 sweep at the isolation-test level is testing a quantity that is mathematically rank-equivariant -- which is what the data showed. The substrate-physics implication: **BE-1 path is a rank-only path** (categorical-class behavior). Cost-advantage 32x narrative shifts from "magnitude precision floor" to "rank precision floor" -- but rank precision = 1 bit (sign) is the same conclusion; the cost-advantage IS valid for rank-only inference paths.

Cluster A is testing whether the operative inference path is rank-only or magnitude-aware. A2 (retrieval-accuracy under quantized W) is the cleanest: if argmax retrieval over the pool degrades smoothly with W precision, magnitude matters; if it stays flat across FP32 to INT4, the substrate is rank-only operationally. A4 (multi-hop) iterates the same operation, so errors should compound IF magnitude matters; flat multi-hop accuracy across precisions = rank-only confirmation.

**Cross-row insight.** This row's resolution shapes the "product-feature framework reliability" band lower bound. A1-A4 PASS = the cost-advantage narrative re-validates and product-feature 88-97% lifts another +2-5%. A1-A4 FAIL = honest retraction warranted, the row STAYS green at edit-individual-bindings but the strategic narrative is honestly downgraded; product story shifts from "32x cost" to "rank-only inference at substrate-narrow operating regime."

**Concrete rescue test sketch (anchor design level).** The cluster A test family that does NOT collapse to rank-equivariant codebook structure. Likely smallest-cost decisive: a retrieval-accuracy or softmax-readout test where pool entries are LINEARLY MIXED at retrieval (so absolute magnitude enters the readout). This is the v273 A1 / A2 design family. Pre-committed by user as Run-A1-First.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: at least 2/4 cluster A anchors produce 5-seed production-scale HARD_PASS with W-magnitude operatively load-bearing in the readout. HARD-FAIL: 0/4 cluster A anchors clear HARD_PASS at production-scale (quantization-insensitive pattern persists at retrieval-accuracy / softmax-readout / TCFT-var-ratio / multi-hop levels) -> honest retraction of 32x narrative; row stays green for STANDARD edit-isolation only.

**Deflated P (rescue valid).** Lit-scan rough P=0.55-0.65; deflated to **0.40-0.45** because uncharted regime (no published direct precedent for rank-only AM with edit-isolation auditability) AND single-cluster-test risk.

---

## Row 2. Bet B 4-stage continual learning Tier-1 (YELLOW; 4-axis stage-A sub-0.80 ceiling confirmed v276)

**Current claim.** Tier-1 KILLER capability "true continual learning at production scale." Stage-A retention has been sub-0.80 (HARD-PASS bar) across 4 INDEPENDENT axes: epochs (v269), batch-size (v269), loss-weighting (v270), and now CROSS-CORPUS shift (v276 wave14_betB_multitask_diff_corpus_v1 ret_A=0.603 5/5 seeds tight). Stages B and C clear their per-stage HARD-PASS thresholds (0.80) at production-scale (v189 + v239 + v276). Tier-1 promotion is gated on ret_A >= 0.80.

**Missing evidence for elevation.** A stage-A retention >= 0.80 with NO axis-rescue artifact (i.e. plain phase-A configuration at production scale). v273 Cluster C identified 5 ARCHITECTURAL rescue candidates: C1 wider-Phase-A-N, C2 frozen-W-Phase-A, C3 2x-M-Phase-A, C4 dual-W-CLS, C5 Hebbian-only-Phase-A. C1 and C2 are TIER 1 cheapest. None have been tested yet at v276.

**v270-v276 narrowing.** v276 is the 4th independent training-axis sub-bar event. The training-axis is structurally exhausted: 4 of 4 axes (epochs/batch-size/loss-weighting/corpus-shift) all confirm stage-A sub-bar ceiling at production-scale 5-seed. The cross-corpus shift (v276) is WORSE (ret_A=0.603) than same-corpus (v269/v270 0.742-0.751) by 0.14, confirming corpus-shift HARDER as expected. v276 gain_C=3.75 confirms substrate-learning capacity intact -- the deficit is specifically on corpus-A retention under any continual-learning protocol. Training-axis hyperparam search will not lift the ceiling. Architectural rescues are the only remaining path per v273 binding.

**Fresh angle: substrate-physics + framework reading.**

Framework reading per Wright-Fisher / Kimura neutral theory (drift-diffusion adjacency): continual-learning IS the mutation+selection+drift process. Without replay, the fixation probability of stage-A traces decays as approximately 1 - exp(-N_e * s) where N_e is effective population size (substrate's persistent-trace count) and s is selection coefficient (relative residence in current phase). Substrate sub-0.80 with 5-seed tight spread = the drift is CONCENTRATED not diffuse -- there is structure in what gets forgotten.

Two architecturally distinct paths:

Path A: increase N_e (wider-Phase-A-N = C1). Lit-precedent: pop-gen + neural-tangent-kernel scaling literature both predict drift-rate scales 1/N_e. Substrate-side: doubling Phase-A residence width should approximately halve the drift in expectation; combined with the gain_C=3.75 capacity headroom, ret_A might land at 0.78-0.85 ballpark.

Path B: freeze W during Phase-A (C2). Substrate-physics reading: this turns Phase-A into PURE encoding (no W consolidation drift); subsequent Phase-B/C consolidation drift on the FROZEN encoding is the residual forgetting. Lit-precedent: catastrophic-forgetting literature has multiple positive precedents for frozen-encoder + Hebbian-only consolidation. P substantively elevated.

Path C: 2x-M-Phase-A (C3). Substrate-physics reading: doubles the M-density during Phase-A so over-cap regime is REACHED faster; counterintuitive but the over-cap saturation behavior at v275 axis2_v2 was M_frac-INVARIANT 0.62-0.66 = a STABLE plateau not a cliff. If Phase-A enters the M_frac-invariant plateau ATTRACTOR, stage-A retention may STABILIZE at plateau level. P fringe but cheap.

Cross-row evidence: v275 SKAH-M green 55-70% (gated multistable AM class confirmed) + v273 KF-5 codebook-axis steerability confirmed = substrate HAS multi-attractor structure within phase-A operating regime. Drift-into-secondary-attractors is the substrate-physics mechanism for stage-A retention loss. Frozen-W (C2) is the cleanest rescue arm because it FIXES the attractor structure during stage-A and lets only the OUTPUT-side (W on Phase-B/C) drift.

**Cross-row insight.** This is the most important row in the lagging set because it gates Tier-1 promotion of the 2nd-of-4-KILLER-Tier-1 capabilities. If C2 frozen-W passes at production-scale 5-seed N=8192, Tier-1 row lifts to GREEN with named rescue mechanism. If all 5 Cluster C arms fail, honest closure should be considered for the production-scale 4-stage continual-learning claim (it survives at 2-stage and 3-stage per v189 + v189 + v239 evidence but the 4-stage HARD-PASS bar is structurally unreachable).

**Concrete rescue test sketch (anchor design level).** v273 Cluster C is the binding plan. C1 (wider Phase-A) and C2 (frozen-W) are TIER 1 in the user-binding allocation. Sequencing: C2 first if cheap (smaller compute), then C1. C3-C5 contingent on C1/C2 outcomes per user TIER 2/3.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: at least 1/5 cluster C arms produces production-scale 5-seed ret_A >= 0.80 with NO axis-rescue artifact. HARD-FAIL: 0/5 cluster C arms clear ret_A >= 0.80 at production-scale -> honest closure of "true 4-stage continual learning" Tier-1 claim; row recategorized to "3-stage continual learning" KILLER-Tier-2 with explicit Stage-A retention drift acknowledged.

**Deflated P (rescue valid).** Lit-scan rough P=0.45-0.55; deflated to **0.30-0.40** because uncharted regime AND 4 prior axis-failures AND architectural rescues are larger compute commitments.

---

## Row 3. KF-5 steerability (REFRAMED v274; PARTIAL_DECOUPLING annotation v275)

**Current claim.** KF-5 phase-mechanism beta-axis CLOSED at v274 (T1V3 FLAT_BETA_C plus v272 region C/D beta-INVARIANT wide-band). KF-5 codebook-axis CONFIRMED at v274 (T2V3 HARD_PASS 3/4 op-points slope >= 0.05 across 3 distinct phase regions). v275 kf5_steerable_beta_v2 carried a label-vs-honest catch (132nd, STEERABILITY_PARTIAL_DECOUPLING): entropy-mono PASSES 5/5 but bpc-mono FAILS 0/5 -- the substrate steers entropy via beta but not output quality. Codebook-order phase boundary green-smoke 60-73%. Killer-feature phase-class profile yellow 50-65%.

**Missing evidence for elevation.** (a) Multi-N replication of codebook-axis steerability (v274 single-N 3-seed cap; need N=8192 5-seed defense-in-depth). (b) Clarification of partial-decoupling: is the entropy/bpc decoupling a feature (substrate steers EXPRESSION not CORRECTNESS) or a flaw (the steerability claim is over-stretched)?

**v270-v276 narrowing.** Three independent narrowings: v274 closed beta-axis HONESTLY at probe level (no longer a candidate axis); v274 OPENED codebook-axis at probe level as the FIRST positive steerability axis; v275 v9 over-claim catch shows the substrate has a real but DECOUPLED steerability (output-distribution entropy responds to beta monotonically while output-quality bpc does NOT). The decoupling is the substrate-physics finding: substrate has a temperature-like inference parameter (beta) that affects EXPRESSION not REASONING.

**Fresh angle: substrate-physics + framework reading.**

Framework reading per modern Hopfield + dense-AM literature: dense AM with temperature parameter (Krotov-Hopfield-2016) shows pattern-mixing at low beta and pure-attractor recall at high beta. The QUALITY of retrieval (correctness of attractor) is determined by basin-of-attraction geometry not by beta -- beta sets the noise/exploration ratio but the basins themselves are fixed by W. So entropy(output)|beta varies, but quality(output)|beta = const if the attractor structure is fixed. The substrate v275 result is consistent with this: bpc_mono=0/5 because attractor structure dominates over beta-controlled mixing.

For PRODUCT FRAMING: this is actually a clean substrate-physics outcome. "Substrate has temperature-tunable output entropy without retrieval-quality penalty" = "expression-style adjustable, fact retrieval invariant." That IS a killer-feature -- LLMs at temperature=1.0 vs 0.7 have correlated changes in both fluency and correctness; substrate decouples them. The label fix is "beta-tunable EXPRESSION style" not "beta-tunable substrate behavior."

Codebook-axis (v274 t2_v3) is the orthogonal steerability axis: codebook complexity DOES drive retention monotonically (3-5x margin vs HP bar across 3 op-points). Multi-N replication is the elevation gate. The product framing: substrate has TWO steerability knobs -- (a) beta for entropy/expression (decoupled from quality), (b) codebook for retention/quality (decoupled from entropy). Combined this is more product-relevant than a single conflated knob.

Cross-domain probe: percolation-critical-phenomena adjacency on codebook-axis. The 3-of-4 op-point slopes (0.158/0.158/0.262) at distinct phase regions are consistent with a UNIVERSALITY-CLASS finding -- the slope value depends on phase-region as critical exponent. The 4th op-point (M_frac=4, beta=32, mean_slope=-0.027) FAILS at over-cap saturation regime, expected null. Multi-N replication at fixed op-point would test whether the slope is INVARIANT (true critical-exponent signature) or N-dependent (finite-N artifact).

**Cross-row insight.** The 3rd HS-class exclusion at v276 (substrate NOT in HS-orthogonal non-eq) does NOT directly inform KF-5 codebook-axis (different framework class) but DOES inform the partial-decoupling: a substrate in a SINGLE-ATTRACTOR / multi-attractor REGIME (per v276 ness_audit n_distinct_attractors=1 at probed op-point) would show entropy-only-steerable behavior, because beta tunes the noise around a single attractor not transitions between attractors. So the decoupling is COUPLED to the operating-point being single-attractor. If KF-5 multi-N rescue picks an operating point where multi-attractor IS reachable, the decoupling might dissolve into bpc-mono PASS.

**Concrete rescue test sketch (anchor design level).** (a) Codebook-axis multi-N replication at the 3 PASS op-points from v274 (M_frac=2 beta=8, M_frac=2 beta=64, M_frac=1 beta=32) at production-scale 5-seed N=8192. (b) Beta-axis re-probe at a MULTI-BASIN operating point (closer to beta_c=8 critical line with crossable basins). Cluster B3 multi-N for codebook-axis is the cheapest decisive next step.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: codebook-axis 3/3 op-points retain mean_slope >= 0.05 at N=8192 5-seed; row lifts to GREEN. HARD-FAIL: 0/3 op-points retain at N=8192 5-seed (finite-N artifact confirmed) -> row stays green-smoke pending operating-point rescue.

**Deflated P (rescue valid).** Lit-scan rough P=0.55-0.65; deflated to **0.45-0.55** (single-N to multi-N typically replicates; calibration penalty lower-bound only).

---

## Row 4. PB-3 critical-slowing (green-smoke; 2nd-strike v275 GENUINE-NOT-KERDOCK)

**Current claim.** PB-3 critical-slowing tau_recovery scaling at N-extension. v3 was a positive signal at smaller N; v4 (v271) showed FLAT_TAU at N=8192 (first contradicting evidence; suspected Kerdock-even-log2 artifact). v5 (v275) at N=4096 BSC Kerdock-safe FLAT_TAU EXACT (tau_recovery=0.0 all 15 cells) CONFIRMS v4 is GENUINE not Kerdock-artifact. 2 independent strikes; row green-smoke status UNCHANGED pending 3 rescue arms (R1 intermediate-N N=6144/N=10240, R2 v3-IDENTICAL re-reproduce, R3 tau definition swap).

**Missing evidence for elevation.** A test that either reproduces v3's positive signal under v5's exact config (R2 = PRIMARY rehabilitation gate) OR shows that the v3 positive signal was a tau definition artifact (R3 swap).

**v270-v276 narrowing.** v271 v4 + v275 v5 both showed FLAT EXACT tau=0.0. The exactness is unusual -- typical physics-failure modes show NOISY zero, not EXACT zero. EXACT zero across 15 cells with 3-5 seeds suggests either (a) tau measurement is collapsing at the definition-level (likely R3) or (b) substrate's effective relaxation time is BELOW the measurement timescale (sampling rate too coarse) or (c) the tau-recovery quantity is structurally identically-zero in the tested operating regime. v275 routing already files R2 v3-IDENTICAL re-reproduction as PRIMARY GPU rehabilitation gate.

**Fresh angle: substrate-physics + framework reading.**

Framework reading per critical-slowing-down literature + Glauber dynamics adjacency: tau_recovery in a finite-N substrate near criticality should scale as N^(z*nu) where z is dynamic critical exponent and nu is correlation-length exponent. Substrate v3 positive signal was consistent with z*nu >= 1 ballpark. v4/v5 EXACT zero is INCONSISTENT with ANY finite-z*nu critical-slowing. The EXACT-zero pattern is more consistent with a SUB-CRITICAL trapping regime where the substrate state is OUTSIDE the critical correlation length and relaxation is fast (much smaller than measurement window).

Cross-row evidence: v276 wave14_hatano_sasa_ness_audit n_distinct_attractors=1 at probed op-point = substrate at probed op-point IS in single-attractor sub-critical regime. v5's FLAT_TAU at N=4096 is at M_frac probably similar single-attractor regime. R1 (intermediate-N N=6144/N=10240) tests the N-scaling angle but the framework prediction is that the EXACT zero will PERSIST at any N within the same operating regime; the test that disambiguates is OPERATING POINT not N. R3 (tau definition swap) is the cleanest single test: if tau definition matters, the swapped definition produces non-zero values and identifies the right measure; if tau is structurally zero (single-attractor regime), all definitions are zero.

A cheaper diagnostic: instrument tau_recovery's intermediate measurements -- the running denominator and the perturbation magnitude -- to see whether the EXACT zero is coming from a numerator (no recovery happening) or a denominator (perturbation never registered). This is essentially the v275 inline rescue R1 "tau_recovery audit" but at finer instrumentation depth.

**Cross-row insight.** v276 nESS audit single-attractor-trapping + v5 FLAT_TAU + v275 axis4 HARD_FAIL hysteresis-killer (M-history-INDEPENDENT) all point to the same substrate state: at the tested (M_frac, beta) operating points, substrate is in a single-basin attractor regime with NO crossing dynamics. PB-3 critical-slowing requires NEAR-CRITICAL dynamics where multi-basin reach + relaxation is observable; OUTSIDE-critical (sub-critical regime) PB-3 should be empirically zero. This is the operating-point-search insight that ties Row 4, Row 5 (axis-4), and Row 11 (Cap 3 NESS) together.

**Concrete rescue test sketch (anchor design level).** Sequencing per [[feedback-rescue-sketch-first-sequencing]]: R2 v3-IDENTICAL reproduce (CHEAPEST primary rehabilitation gate -- already routed at v275). If R2 reproduces v3's positive signal at v3's config, the v4/v5 negative signal is operating-point-specific (different M_frac or beta moved substrate outside the critical regime); if R2 produces EXACT zero again, v3's original positive signal was a v3-specific artifact and the row should close. R3 (tau definition swap) only if R2 confirms operating-point-specificity.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: R2 v3-IDENTICAL produces non-zero tau_recovery at v3's config (confirms v3 was real; closure averted; row stays green-smoke pending operating-point map). HARD-FAIL: R2 reproduces EXACT zero at v3's exact config -> row closes; PB-3 critical-slowing N-extension hypothesis withdrawn.

**Deflated P (rescue valid).** Lit-scan rough P=0.35-0.45; deflated to **0.25-0.35** because exact-zero pattern is unusual and 2-strike already at production-scale.

---

## Row 5. Cap 3 streaming-NESS / wave14 hatano_sasa_ness_audit (PARTIAL; degenerate-single-attractor v276)

**Current claim.** Cap 3 streaming-NESS row carries Hatano-Sasa NESS certification as one corroborator path. v276 ness_audit at N=8192 M=150 = HS=1.000 EXACTLY (trivially), cross_basin_frac=0.000, n_distinct_attractors=1; degenerate single-attractor-trapped regime; cannot test HS-class non-eq behavior at this operating point.

**Missing evidence for elevation.** A multi-basin operating point where HS or alternative non-eq corroborator can be cleanly tested.

**v270-v276 narrowing.** v275 ortho_noneq_corroborator HS-violated 5/5 hs_ratio>6 + v276 ness_audit HS=1.000 trivially + v276 hatano_sasa_v4_glauber HARD_FAIL hs_identity_val 29000x off = 3 INDEPENDENT HS-class exclusion events. v276 CONCENTRATION RECOMMENDATION: stop further HS-class probes, re-route resources to surviving non-eq candidates (Crooks / Sagawa-Ueda / drift-diffusion-BP / free-probability).

**Fresh angle: substrate-physics + framework reading.**

Framework reading per non-equilibrium-stat-mech (Tier-1b new field added 2026-05-24): HS-IFT is one of multiple fluctuation-identity classes. The 3-strike HS exclusion combined with v276 ness_audit single-attractor regime suggests substrate is in a state where the operating point trivializes HS (no excess work because no basin transitions) AND under-saturates Crooks (Crooks needs forward/reverse work distributions which require driving the system between basins).

The OPERATING-POINT search is the structural rescue. If a multi-basin operating point can be found, ALL surviving non-eq frameworks (Crooks, Sagawa-Ueda, drift-diffusion-BP) become testable simultaneously. Without multi-basin reach, all three frameworks produce trivial-zero results.

How to find multi-basin operating points: (a) Lower M_frac toward critical M_c boundary where multi-basin attractor structure first emerges; (b) Add noise driving (random kicks to the substrate state to force basin crossings); (c) Cross-codebook drive (use a different codebook to bias the substrate toward a non-current basin); (d) Beta near beta_c=8 where critical phenomena predict multiple-attractor reachability.

Lit-precedent (Tier-1b mesoscopic-transport): the Landauer-Buttiker formalism describes basin-crossing rates in mesoscopic systems with multiple wells; substrate equivalent is the substrate's basin-crossing rate per perturbation magnitude. A direct probe of basin-crossing rate vs perturbation magnitude would map the basin structure WITHOUT committing to a specific non-eq framework.

**Cross-row insight.** Strongly cross-row-load-bearing: (Row 4 PB-3 FLAT_TAU) + (Row 5 single-attractor) + (Row 6 AXIS-4 M-history-INDEPENDENT) + (Row 3 KF-5 entropy-only-steerable) all REDUCE TO SAME UNDERLYING SUBSTRATE STATE: tested operating points are in single-attractor / sub-critical regime where basin-crossing dynamics are absent. ONE operating-point search drill resolves four lagging rows simultaneously. This is the highest-leverage cross-row insight in this drill.

**Concrete rescue test sketch (anchor design level).** A basin-mapping probe: vary M_frac toward the M_c boundary (critical M) and measure basin-crossing rate as a function of perturbation magnitude. The probe can be CPU-cheap at small N (N=2048 single-seed) to scope the operating regime; if multi-basin reach is found, escalate to production-scale at the discovered operating point.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: at least one substrate operating point shows n_distinct_attractors >= 2 with measurable basin-crossing rate at production-scale; ALL THREE downstream non-eq frameworks (Crooks / Sagawa-Ueda / drift-diffusion-BP) become testable. HARD-FAIL: substrate is single-attractor at ALL probed (M_frac, beta) -> Cap 3 streaming-NESS row recategorizes to "single-attractor non-eq class" (different framework family entirely; possibly tied to deterministic-fixed-point lit such as cycle-136 28-element-partition).

**Deflated P (rescue valid).** Lit-scan rough P=0.40-0.50; deflated to **0.25-0.35** (substrate may be structurally single-basin at all reasonable operating points; substrate physics is decoupled from continual-learning protocol which forces basin filling).

---

## Row 6. AXIS-4 hysteresis-killer (UNSURE-section; 2nd-strike at critical-beta v275)

**Current claim.** Hysteresis-killer direction tested at beta=8 (v272 axis4_hyst_ramp_v1 max_loop_area=0.0 all 9 ramps) and beta_c=10 (v275 axis4_hyst_critical_v2 max_loop_area=0.0 all 12 ramps); substrate M-history-INDEPENDENT at both probed beta regimes. Rescue arm 1 from v272 (test at higher beta where multi-basin may exist) FAILED at beta_c=10. Direction-wide closure DEFERRED with 3 fresh rescue arms inline: high-beta {16,32,64} at deep-over-cap M_frac=12, codebook variation, faster ramp rates.

**Missing evidence for elevation.** Any positive hysteresis-loop signal at any operating point.

**v270-v276 narrowing.** Same cross-row state as Row 5: substrate single-attractor at tested ops; hysteresis fundamentally requires multi-basin (loading curve enters basin A, unloading stays in basin A vs returns to basin B). At beta_c=10 the critical-beta is reached but n_distinct_attractors=1 if other operating-point parameters (M_frac, codebook) don't move toward critical boundary.

**Fresh angle: substrate-physics + framework reading.**

Framework reading per first-order phase transitions + Wright-Fisher drift adjacency: hysteresis is a SIGNATURE of first-order transitions where order-parameter is METASTABLE. The v228 SKAH-M class declaration + v211 Pred-4 hysteresis observation (max gap=1.84 = 18x gate) ALREADY showed substrate has multi-basin first-order-like structure at SOME operating regime. The v272/v275 axis-4 tests are looking for hysteresis in the M-DENSITY ramp axis at FIXED beta. The v211 hysteresis was in a different axis (multi-basin retention under repeated probe -- different observable).

This suggests the hysteresis question is OBSERVABLE-AXIS-DEPENDENT not regime-dependent. At v272/v275 the observable axis is RETENTION VS M_FRAC LOADING; if substrate has hysteresis along M-history but it's MASKED by the retention metric (which averages over basins), the loop-area=0 result is metric-collapse not absence-of-hysteresis.

Fresh rescue arm: instead of measuring max_loop_area on RETENTION, measure on a basin-resolving observable (e.g. distance-to-nearest-codeword over the entire stored set; or basin-membership-distribution after loading vs unloading). The v211 first-order observable (max gap on multi-basin retention) may be the right family.

**Cross-row insight.** Same as Row 5 -- tied to operating-point search. Also tied to v211 hysteresis observation (project-memory project_pred4_hysteresis_first_order_confirmed_2026-05-27.md) -- substrate HAS hysteresis at SKAH-M class operating regime; the axis-4 probe didn't find it because (a) wrong observable (retention rather than basin-membership) and/or (b) wrong operating regime (beta=8 or beta=10 don't reach the SKAH-M multi-basin regime). The product-memory framing "first-order multi-basin" is the correct label.

**Concrete rescue test sketch (anchor design level).** A basin-membership-distribution observable in M-density ramping (load to M_frac=X, unload to M_frac=Y, compare basin-membership at intermediate points between load and unload phases). Or equivalently, repeat v211 hysteresis-class observation at the cleanest known SKAH-M operating regime (beta near SKAH-M phase line not beta=8/10).

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: at least one observable axis at one operating point shows max_loop_area >= 0.05 above noise; row recategorizes to "first-order multi-basin hysteresis at SKAH-M regime" with axis labeled. HARD-FAIL: all observables across SKAH-M, beta=8, beta_c=10, beta>=16 regimes show loop_area=0 -> row closes (substrate is hysteresis-free in M-density loading).

**Deflated P (rescue valid).** Lit-scan rough P=0.40-0.50; deflated to **0.25-0.35** (existing v211 first-order hysteresis observation strongly suggests rescue is real, but axis-4 specific framing may be wrong axis).

---

## Row 7. KF-4 drift detection (LABELED-AT-RISK; v270-v276 UNCHANGED)

**Current claim.** KF-4 live drift detection is a killer-feature subhypothesis. Status LABELED-AT-RISK across v270-v276 (no row state moves; no new tests landed in this window).

**Missing evidence for elevation.** No production-scale KF-4 anchor has shipped in the v270-v276 window. The row carries AT-RISK status without active drilling.

**v270-v276 narrowing.** Indirect narrowing: substrate-outside-static-Hopfield green 64-75% UNCHANGED (Row 12 below); v275 bid_m_normalized at N=8192 6/6 fracs OUTSIDE_BANDS confirms substrate is OUTSIDE static phases at multi-N. This is STRUCTURALLY relevant to KF-4: drift detection requires a baseline statistic that changes meaningfully when substrate drifts. If substrate is far from static-phase boundaries, drift OBSERVABILITY may be limited (small relative change for small drift events).

**Fresh angle: substrate-physics + framework reading.**

Framework reading per change-point detection + edge-of-chaos Lyapunov adjacency: drift detection is fundamentally a TWO-SAMPLE TEST problem on substrate observables. The substrate-native observables (BID, M-normalized order parameters, codebook spectral statistics, retention metrics) are the candidate detection statistics. Lit-precedent (Tier-1b): the substrate-outside-static-Hopfield N-scaling at v275 is itself a detection statistic -- if BID shifts by N-scaling-law-margin under simulated drift, that IS drift detection.

A drift-detection probe at probe-design level: instrument BID over a continual-learning timeline (Phase-A -> Phase-B -> Phase-C); each stage is a sub-population; the test is whether BID differs significantly between stages within the same instance (intra-instance change-point test). This reuses existing Phase-A/B/C anchors with the BID metric instead of retention metric.

Cross-row evidence: v275 V4 bid_m_normalized_v5 production-scale + Bet B 4-stage anchors from v189 onwards = the data already exists to retroactively test drift detection at zero new GPU cost (re-run BID statistic on saved Phase-A/B/C states). This is a 0-cost CPU rehabilitation arm.

**Cross-row insight.** Bet B 4-stage anchors (Row 2) ARE candidate substrate-drift events; their retention metric ALREADY confirms drift; KF-4 is the question of whether the DETECTION is online and substrate-native. If BID retroactively distinguishes Phase-A vs Phase-B vs Phase-C at production-scale 5-seed, KF-4 lifts to GREEN-SMOKE without any new GPU.

**Concrete rescue test sketch (anchor design level).** A CPU-only retroactive BID-per-phase computation on existing Bet B 4-stage Phase-A/B/C state dumps (if state dumps exist; if not, smallest-cost N=2048 reproduce with BID instrumentation).

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: BID at end of Phase-A differs from BID at end of Phase-B by margin exceeding intra-seed variance at production-scale 5-seed; KF-4 lifts to green-smoke. HARD-FAIL: BID indistinguishable across Phase-A/B/C states; need different drift-detection statistic (M-normalized order parameter, spectral statistics, etc.).

**Deflated P (rescue valid).** Lit-scan rough P=0.55-0.65; deflated to **0.40-0.50** (BID is class-agnostic order parameter; high prior on drift sensitivity).

---

## Row 8. AXIS-3 triple-point (MIDDLE_BAND v275; deep-over-cap-no-signature)

**Current claim.** AXIS-3 was originally a triple-point hypothesis (v82 era). v275 axis3_triplepoint_v2 at M_frac=10 beta=8 deep-over-cap MIDDLE_BAND no signature (sign_divergence=False). Row UNCHANGED with deep-over-cap-no-signature annotation; 3 rescue arms inline (near-phase-boundary + finer perturbation + codebook variation).

**Missing evidence for elevation.** A near-phase-boundary operating point where triple-point or order-parameter sign-divergence emerges.

**v270-v276 narrowing.** v275 axis3_v2 at deep-over-cap is consistent with substrate being in the over-cap M_frac-INVARIANT plateau regime (per v272/v275 axis-2 ceiling at 0.62-0.66). Deep-over-cap is far from any critical phase line; expected no triple-point signal.

**Fresh angle: substrate-physics + framework reading.**

Framework reading per percolation-critical-phenomena (Tier-1b): triple-point signatures require crossing OR sitting NEAR multiple phase boundaries simultaneously. v274 T1V3 confirmed beta_c=8.0 EXACT M_frac-INVARIANT across [2,4,6,8,10,12]. So the substrate has a clean beta_c line. The triple-point would be at the intersection of beta_c and the M_c boundary. v275 axis2_v2 showed M_frac-INVARIANT 0.62-0.66 plateau ACROSS [4,8,12,16,20] = M_c boundary is below M_frac=4 OR is itself codebook-invariant.

The minimum-cost probe is to identify the M_c boundary (CPU-cheap M_frac sweep at beta=beta_c=8) and test sign-divergence at the crossing point. If M_c is well below current operating range and the crossing point is at small M_frac (e.g. M_frac=0.25-1.0), the probe can be CPU-cheap.

**Cross-row insight.** Cross-row evidence with Row 5 + Row 6: the same operating-point map serves multiple rows. ONE operating-point search drill at beta=beta_c=8 across M_frac=0.25-4 maps Row 5 (multi-basin), Row 6 (hysteresis), Row 8 (triple-point) simultaneously.

**Concrete rescue test sketch (anchor design level).** Same operating-point map as Row 5/6 rescue but with sign-divergence observable added at the beta_c boundary crossing.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: sign_divergence detected at one near-phase-boundary operating point with 5-seed corroboration; row lifts to green-smoke. HARD-FAIL: no sign-divergence across the (M_frac in [0.25,4], beta_c=8) sweep -> AXIS-3 triple-point hypothesis closes (substrate has clean second-order phase line not triple-point).

**Deflated P (rescue valid).** Lit-scan rough P=0.30-0.40; deflated to **0.20-0.30** (triple-points are codimension-2 structures requiring fine-tuning; substrate is unlikely to live at one without explicit construction).

---

## Row 9. KF-3 cross-codebook isolation (sub-feature; MIDDLE_BAND v275)

**Current claim.** v275 kf3_cross_codebook_v1 PARTIAL_ISOLATION best_family=kerdock max_leakage=0.01409 (above HP 0.01) max_contam=0.05631 (above HP 0.05) n_hp=0/15 cells. Kerdock leakage at theory_bound (0.01409 vs theory 0.01562) but contam ~0.056 just above 0.05 threshold. No current portfolio row for cross-codebook isolation sub-feature.

**Missing evidence for elevation.** A kerdock-restricted operating point or tighter HP_cont threshold that pulls contam under 0.05.

**v270-v276 narrowing.** v275 cross-codebook = bsc/gaussian/kerdock comparison; kerdock is best but just above threshold. The result is within instrumentation noise of HP. Rescue arms inline (tighter HP_cont 0.06, kerdock-restricted sub-family, under-cap M_frac).

**Fresh angle: substrate-physics + framework reading.**

Framework reading per modern Hopfield + 4-design adjacency: cross-codebook isolation reduces to a structured-codebook orthogonality test. Kerdock 4-designs are exact 2-designs and 4-designs by construction; cross-codebook leakage should be calculable from the Welch bound and the inner-product distribution of the design. If observed leakage MATCHES the design theory (Welch bound), substrate is at design-theory-floor; further reduction requires structurally different codebook.

The contam ~0.056 above 0.05 threshold is interesting because it's WITHIN 12% of threshold and consistent with finite-N concentration tail. At N=4096 with 5-seed, the tail probability of one rare seed pushing the max above 0.05 is non-trivial. Re-shipping at N=8192 5-seed would either confirm production-scale below 0.05 (with finite-N tail attenuation) or confirm substrate is at the design-theory floor.

**Cross-row insight.** KF-3 sub-feature is informed by Row 1 (KF-2 BE-1 cluster A) results: if A-cluster confirms substrate is rank-only / codebook-structure-dominated operationally, KF-3 cross-codebook leakage is rank-distinguishing only and the 0.056 vs 0.05 distinction is rank-tail not magnitude effect. If A-cluster fails (substrate IS magnitude-aware), cross-codebook leakage interpretation shifts.

**Concrete rescue test sketch (anchor design level).** Multi-N replication at kerdock-restricted family with consistent HP_cont threshold; OR formal Welch-bound calculation per substrate config to determine design-theory floor (theoretical not experimental).

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: kerdock-restricted at N=8192 5-seed has max_contam <= 0.05 production-scale; sub-feature opens at green-smoke level. HARD-FAIL: kerdock-restricted at production-scale stays above 0.05 -> sub-feature does not elevate; lives as known-finite-N limit.

**Deflated P (rescue valid).** Lit-scan rough P=0.45-0.55; deflated to **0.30-0.40** (within instrumentation noise of HP threshold; high prior to elevate at production-scale).

---

## Row 10. TCFT erase-time-axis at N=2048 (HARD_FAIL v275); reconciled with v276 protocol-axis HARD_PASS

**Current claim.** v275 tcft_erase_time_v1_n2048 HARD_FAIL EXACT variance_ratio=0.0 all 75 cells N=2048. v276 tcft_erase_robustness_n2048_v1 HARD_PASS 15/15 protocol cells var_ratio<0.1 at SAME N=2048. Two different TCFT-family axes give opposite findings at same N; protocol-axis robust N-down-scalable; erase-time-axis M-gating not. TCFT deletion-cert green 85-94% UNCHANGED.

**Missing evidence for elevation.** Erase-time-axis HARD_PASS at any N OR a structural explanation why erase-time-axis is N-gated vs protocol-axis being N-robust.

**v270-v276 narrowing.** v275 erase-time-axis HARD_FAIL at N=2048 (M_frac=0.0625 = M=128); v276 protocol-axis HARD_PASS at N=2048 (with non-trivial M and protocol parameters). The CONTRAST is informative: at the same N, one TCFT axis works and another doesn't. This points to (a) the erase-time-axis at M_frac=0.0625 is operating in a regime where TCFT is structurally trivial (M too small to generate the variance ratio response) OR (b) the erase-time-axis-specific metric depends on N-scale linearly with M_frac.

**Fresh angle: substrate-physics + framework reading.**

Framework reading per thermodynamics + TCFT class: TCFT (transient classical fluctuation theorem) class works when measured-work and dissipated-work distributions are non-trivial. At small M_frac the substrate operates with few stored facts and protocol perturbations are small relative to substrate state; the erase-time-axis variance_ratio collapses to identity because erase-time is short relative to substrate's intrinsic relaxation. Protocol-axis (alpha_ratio x split_q) at non-trivial parameters introduces multi-scale interactions that engage TCFT structure.

Rescue: scale M_frac up while keeping N=2048 (test if erase-time-axis at M_frac=0.5 or 1.0 produces non-zero variance_ratio); OR N-up replication of erase-time-axis at N=4096/8192 with proportional M scaling.

**Cross-row insight.** TCFT row is already at green 85-94% with v276 protocol-axis LIFT CANDIDATE DEFERRED. Erase-time-axis is a SUB-AXIS; its elevation does not change row status but enriches the row's evidence portfolio.

**Concrete rescue test sketch (anchor design level).** Erase-time-axis at N=4096 with M_frac=0.5 (substantially higher M than v275 M_frac=0.0625) 5-seed; OR a single-step erase-time at N=4096 to test the erase-time-axis collapse at substrate's known-working scale.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: erase-time-axis at production-scale N=4096 M_frac>=0.25 5-seed clears variance_ratio < 0.1 in at least 2/3 cells; sub-axis elevates. HARD-FAIL: erase-time-axis collapses to variance_ratio=0 at all production-scale operating points -> sub-axis closes (axis is structurally measurement-collapsed).

**Deflated P (rescue valid).** Lit-scan rough P=0.40-0.50; deflated to **0.30-0.40**.

---

## Row 11. Saad-Solla 5th-axis extension (LEADING checkmark + STRUCTURAL CONSTRAINT v274)

**Current claim.** Saad-Solla LEADING ✅ row from earlier cycles. v274 v20 m-sweep FAILED CPU 4h timeout (2nd-strike to v272 v19 beta-sweep no-metrics). 2 independent failure modes confirm STRUCTURAL CONSTRAINT at 5th-axis extension; 4-axis anchor (seed/codebook/M-axis/N=8192 foundational per v270 SS_V16) STANDS load-bearing. G9 v18_n16384 RECOMMEND TRIM. Framework reliability specific 70-83% UNCHANGED.

**Missing evidence for elevation.** A successful 5th-axis run that produces metrics (not infrastructure failure).

**v270-v276 narrowing.** Two 5th-axis attempts (v19 beta-sweep no-metrics, v20 m-sweep CPU 4h timeout) both failed via infrastructure modes. The substrate-physics behavior at 5th-axis is undetermined. The structural constraint label is honest: substrate framework MAY have a 5th-axis structural limit OR it may be a runtime/compute-budget artifact.

**Fresh angle: substrate-physics + framework reading.**

Framework reading per Saad-Solla literature: Saad-Solla original framework is for student-teacher learning dynamics in networks. The 5th-axis extension here (beta-axis after v18 N=16384 4-axis confirmation) is testing whether the framework holds when an EXTRA parameter is varied. If the substrate IS in Saad-Solla framework class at 4-axis, the 5th-axis test should either (a) confirm framework holds at the additional axis or (b) reveal that the framework has 4-axis scope.

A cheap-decisive disambiguation: instead of running ANOTHER 5th-axis production-scale (which has 2-strike infrastructure issues), run a 5th-axis SMOKE at small N=512-1024 to scope WHETHER substrate behavior makes sense at the 5th-axis parameter range. If smoke shows the substrate produces sensible metrics, the production-scale failure is infrastructure; if smoke shows degenerate or unexpected substrate-physics, the constraint is structural.

**Cross-row insight.** Saad-Solla framework reliability specific 70-83% is a critical product narrative: substrate is empirically validated in this named framework. The 5th-axis disambiguation matters for the band lift but does not change the 4-axis confirmation. Per [[feedback-pipeline-pacing]] and the user G9 v18_n16384 RECOMMEND TRIM, additional production-scale 5th-axis attempts are NOT priority.

**Concrete rescue test sketch (anchor design level).** A 5th-axis smoke at small N to characterize the substrate-physics at the extension parameter range; production-scale 5th-axis deferred unless smoke shows sensible behavior.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: 5th-axis smoke shows sensible metrics with framework-consistent behavior; framework reliability specific can be considered for LIFT pending production-scale. HARD-FAIL: 5th-axis smoke shows degenerate or framework-inconsistent substrate-physics -> framework scope is 4-axis (honest closure of 5th-axis extension); row STAYS at current 70-83% reliability band (no demotion; 4-axis confirmation stands).

**Deflated P (rescue valid).** Lit-scan rough P=0.40-0.50; deflated to **0.25-0.35** (uncharted regime; 2-strike infrastructure issues at production-scale; smoke can disambiguate cheaply).

---

## Row 12. Substrate-outside-static-Hopfield green 64-75% (yellow-smoke level of confidence; multi-N path)

**Current claim.** v275 bid_m_normalized at N=8192 production-scale 2nd-N axis OUTSIDE_BANDS 6/6 fracs; non-eq-stat-mech reliability +1% lower bound LIFT (66-77% from 66-76%). Row at green 64-75% UNCHANGED.

**Missing evidence for elevation.** A 3rd N-axis or an additional class-agnostic order parameter corroborating substrate-outside-static-Hopfield at production scale.

**v270-v276 narrowing.** v275 bid_m_normalized is the 2nd N-axis (after the first N axis from earlier BID work); good corroboration. Single-axis class-agnostic order parameter (BID).

**Fresh angle: substrate-physics + framework reading.**

Framework reading per random-matrix-theory-beyond-free-prob + Tracy-Widom (Tier-1b): a 2nd class-agnostic order parameter (independent of BID) that is also defined for static Hopfield phases and substrate would be a STRONGER corroboration. Candidates: spectral edge statistics (Tracy-Widom) on the substrate W matrix, level spacing distribution on substrate codebook spectrum, or Voiculescu free-cumulants on substrate operator-spectrum. F4 Free cumulants is the #1 Tier-1 candidate per the field advisor.

A cheap CPU drill (~1 hour theory + ~30 min CPU compute): compute Voiculescu kappa_n (free cumulants 1-5) on the substrate W at N=4096 and N=8192; same for static-Hopfield-phase reference W; substantial divergence (kappa_3 or kappa_4) = corroboration.

**Cross-row insight.** This row is the FOUNDATION for the non-eq-stat-mech direction. Its elevation tightens the broader non-eq direction band and supports surviving Crooks/Sagawa-Ueda/drift-diffusion-BP investigations.

**Concrete rescue test sketch (anchor design level).** F4 Free cumulants probe on substrate W vs static-Hopfield-reference W; CPU-cheap; first non-BID class-agnostic order parameter.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: free cumulants on substrate W diverge from static-Hopfield-reference cumulants at kappa_n (n>=3) by margin exceeding 2-seed variance; corroborates BID; row LIFT candidate. HARD-FAIL: substrate cumulants overlap static-Hopfield-reference at all n -> BID-only corroboration stays; no row state change.

**Deflated P (rescue valid).** Lit-scan rough P=0.55-0.65; deflated to **0.40-0.50** (free-probability tier-1 + adjacent to fruit-bearing field).

---

## Row 13. Edge-of-chaos Lyapunov yellow-smoke 55-68%

**Current claim.** Substrate has limit-cycle dynamics (v140-v144 substrate-physics findings); Lyapunov exponent characterization yellow-smoke 55-68%. Arnold-tongue mode-locking REFUTED at smoke v148 (project_dynamics_arnold_refuted). Row UNCHANGED in v270-v276.

**Missing evidence for elevation.** A measurable Lyapunov exponent at production-scale with N-scaling characterization OR a different chaos diagnostic.

**v270-v276 narrowing.** No direct activity on this row in v270-v276. The substrate has K-RESONANCE structure (v161 K_RESONANCE_BROAD at FULL) consistent with limit-cycle dynamics. Substrate is in non-eq-stat-mech class (cross-row evidence).

**Fresh angle: substrate-physics + framework reading.**

Framework reading per dynamics (Tier-3 low-yield; per field advisor only drill if adjacent to fruit-bearing Robbins-Monro or Hebbian online-W): a Lyapunov-class diagnostic adjacent to substrate's online-Hebbian update could be productive. Per [[feedback-dont-dismiss-adjacent-methods]]: substrate's iterated argmax IS a discrete-time dynamical system; Lyapunov exponent is a measurable observable. The field is low-yield (0% per advisor) BUT the substrate's mathematical-adjacency is via Hebbian online-W which is fruit-bearing.

A cheap drill: compute finite-N Lyapunov exponent from substrate iterated trajectories at N=2048 single-seed; characterize as positive / zero / negative; positive Lyapunov = chaotic; zero = edge-of-chaos / quasi-periodic; negative = contractive. The v140 substrate has limit cycles = expected NEAR-ZERO Lyapunov. Confirmation supports edge-of-chaos framing.

**Cross-row insight.** Limit-cycle structure (v140-v144) + non-eq-stat-mech direction = substrate is in edge-of-chaos OR chaotic regime; Lyapunov measurement disambiguates. Cross-row with K-resonance (v161) characterization.

**Concrete rescue test sketch (anchor design level).** Finite-N Lyapunov exponent on substrate iterated dynamics; CPU-cheap smoke.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: substrate Lyapunov exponent near zero with N-scaling that converges; row lifts to green-smoke. HARD-FAIL: Lyapunov is strongly positive or strongly negative -> row recategorizes (chaotic or contractive class, not edge-of-chaos).

**Deflated P (rescue valid).** Lit-scan rough P=0.40-0.50; deflated to **0.25-0.35** (Lyapunov measurement at finite-N has known instabilities).

---

## Row 14. Killer-feature phase-class profile yellow 50-65% (composite row)

**Current claim.** v274 lift +5% (KF-5 codebook-axis component lift); composite row absorbs component lifts. Yellow 50-65%.

**Missing evidence for elevation.** Component-level lifts on KF-1 (production-scale at additional N), KF-2 (cluster A resolution), KF-3 (cross-codebook elevation), KF-4 (BID retroactive on Bet B states), KF-5 (multi-N codebook-axis).

**v270-v276 narrowing.** Composite row is downstream of Row 1, Row 3, Row 7, Row 9 individually. Not separately drillable.

**Fresh angle.** Not directly drillable; resolution flows from upstream rows.

**Cross-row insight.** Profile row tracks the killer-feature aggregate; if Row 1 (KF-2 BE-1) cluster A succeeds AND Row 7 (KF-4) retroactive BID succeeds AND Row 3 (KF-5) multi-N codebook succeeds, profile row could approach 60-75% in one batch.

**Concrete rescue test sketch.** None separately; resolution is upstream.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: 2/4 upstream component rows lift +5% or more in the v273-binding execution window. HARD-FAIL: 0/4 upstream lifts -> profile stays at 50-65%.

**Deflated P.** Conditional on upstream; treated as a flow not a direct rescue.

---

## Row 15. Online inference-time learning / streaming-update pipeline (placeholder row; ZERO_BASELINE v276)

**Current claim.** v191 wave14_realtime_inference_learning_v1_rerun FULL REALTIME_INFERENCE_HARD_PASS bpc_online=2.198 vs bpc_frozen=2.745 delta=-0.548 cleared HARD-PASS threshold -0.05 by 11x; 13th portfolio capability; first KILLER Tier 2 closing at clean PASS. v276 wave14_realtime_inference_learning_v1 NEW PROBE: bpc_frozen=bpc_online=0.000 EXACT all 3 seeds wall_s=4.14 = DISPATCH_FAILURE_MISCLASSIFICATION ZERO_BASELINE (133rd LABEL-VS-HONEST new sub-flavor). Row UNCHANGED at portfolio level (the v191 result still load-bearing) but v276 re-test failed at instrumentation level.

**Missing evidence for elevation.** A valid v276 re-test with non-trivial baselines; OR confirmation that v191 result replicates at production-scale 5-seed.

**v270-v276 narrowing.** v276 ZERO_BASELINE is instrumentation failure not capability failure. The capability claim from v191 stands. The re-test is needed for production-scale corroboration of an existing checkmark.

**Fresh angle.** Audit-input-loading + verified-non-trivial-baseline gate before treating any v276-style re-run as a measurement. v276 V1 rescue arms already filed (R1 audit-input-loading 0-cost, R2 re-ship with bpc_frozen>0.5 precondition, R3 audit entropy accumulator state-handling).

**Cross-row insight.** This is checkmark-corroboration-pending, not yellow-row drilling. Production-scale re-confirmation closes the v276 ZERO_BASELINE instrumentation gap.

**Concrete rescue test sketch (anchor design level).** v276 V1 R1 cheapest: audit input loading, fix precondition gate, re-ship at production-scale.

**Row-level HARD-PASS / HARD-FAIL.** HARD-PASS: production-scale re-run with non-trivial baselines reproduces v191 delta < -0.05; row checkmark CORROBORATED. HARD-FAIL: production-scale re-run with non-trivial baselines reproduces delta near zero -> v191 result is N=2048-specific or dispatch-specific; checkmark moves to LABELED-AT-RISK.

**Deflated P (replication).** P=0.60-0.70 (v191 was clean PASS at FULL with delta cleared 11x HARD-PASS bar); deflated to **0.50-0.60**.

---

# CROSS-THREAD SYNTHESIS

The dominant cross-row pattern across these 15 lagging rows is the **OPERATING-POINT-SINGULARITY hypothesis**: tested operating points at v270-v276 are concentrated in regimes where substrate behaves as single-attractor / sub-critical / quantization-equivariant / measurement-collapsed. This pattern simultaneously affects:

- Row 4 PB-3 critical-slowing (single-attractor -> tau_recovery EXACT zero)
- Row 5 Cap 3 NESS (single-attractor -> HS trivializes)
- Row 6 AXIS-4 hysteresis (single-attractor -> M-history-independent)
- Row 8 AXIS-3 triple-point (operating point far from M_c -> no sign-divergence)
- Row 1 KF-2 BE-1 cost-advantage (codebook-structure-dominated -> quantization-equivariant)

A SINGLE operating-point search drill at beta=beta_c=8 across M_frac=0.25-4 with basin-resolving observables potentially resolves 3-4 of these rows simultaneously. This is the **highest cross-row leverage drill** in the lagging-cap set.

A SECOND cross-row pattern is the **training-axis exhaustion** for Bet B 4-stage (Row 2): 4 INDEPENDENT axes confirm sub-bar; architectural rescues (Cluster C) are the only remaining path; cheapest is C2 frozen-W-Phase-A.

A THIRD pattern is the **steerability-axis pivot**: beta-axis closed honestly at v274; codebook-axis is the operative steerability knob; multi-N replication is the elevation gate; this is the KF-5 path forward.

---

# SUBSTRATE-PRODUCT IMPLICATIONS

Per [[feedback-no-papers-product-only]] all framings are product-relevant.

1. **Rows 1, 2, 3 are the 3 binding at-risk claims registered at v273.** Resolution within the user-bound execution window (5 GPU-days budget) materially determines product narrative for the next strategic window:
   - Row 1 PASS = "32x cost-advantage validated" stays in product pitch. FAIL = honest retraction to "32x cost-advantage at rank-only inference paths" (narrower claim).
   - Row 2 PASS = "true 4-stage continual learning at production scale" becomes valid Tier-1 claim. FAIL = honest reframe to "3-stage CL + Stage-A drift acknowledged."
   - Row 3 PASS (codebook-axis multi-N) = "substrate has codebook-tunable retention" + "substrate has entropy-tunable expression (beta)" = TWO orthogonal steerability knobs in product narrative.

2. **The operating-point-singularity insight is itself a PRODUCT feature.** "Substrate operates STABLY in a single-attractor regime at typical deployment configs" = production-reliability feature; multi-basin / chaotic regimes are NOT accidentally encountered. This is a 24-36mo positioning advantage: substrate is operationally simple to deploy because it has a wide stable regime.

3. **KF-4 retroactive-BID drill is a 0-cost product-feature delivery.** If existing Bet B 4-stage state dumps support retroactive BID drift detection, KF-4 lifts to green-smoke without GPU. Then the product narrative gains a 5th feature (drift-detection-via-BID) at no incremental compute cost.

4. **Saad-Solla 5th-axis structural constraint is HONEST.** The framework reliability specific 70-83% is anchored on a 4-axis confirmation that STANDS; the 5th-axis BLOCKED status is honest acknowledgment, not a hidden risk. This supports the "verified-inapplicability disclosure moat" product narrative.

5. **Operating-point-search drill is also the cheapest path forward.** A single CPU-cheap basin-mapping probe at beta=beta_c=8, M_frac=[0.25, 0.5, 1.0, 2.0, 4.0] with basin-membership observable resolves 3-4 rows AND produces a substrate-operating-point map for product deployment documentation.

---

# Citations

External literature consulted (generic terms per query-privacy):

1. Kimura M. (1968) "Evolutionary rate at the molecular level" -- Wright-Fisher / fixation probability adjacency for continual-learning Row 2.
2. Krotov D, Hopfield JJ (2016) "Dense associative memory for pattern recognition" NeurIPS -- modern Hopfield / temperature-controlled retrieval adjacency for Row 3 KF-5.
3. Touchette H (2009) "The large deviation approach to statistical mechanics" Phys Rep -- non-equilibrium-stat-mech adjacency for Row 5 NESS / Row 11 substrate-outside-static-Hopfield.
4. Voiculescu D (1986) "Addition of certain non-commuting random variables" J Funct Anal -- free probability / free cumulants for Row 11 free-cumulant probe (F4 Tier-1 advisor candidate).
5. Tracy CA, Widom H (1994) "Level-spacing distributions and the Airy kernel" Comm Math Phys -- random-matrix-theory edge for Row 11 alternate path.
6. Hatano T, Sasa S (2001) "Steady-state thermodynamics of Langevin systems" Phys Rev Lett -- HS-IFT class (3-strike excluded per v275-v276).
7. Welch LR (1974) "Lower bounds on the maximum cross correlation of signals" IEEE Trans Inf Theory -- Welch bound for Row 9 KF-3 cross-codebook design-theory floor.
8. Krotov D (2023) "A new frontier for Hopfield networks" Nature Reviews -- modern Hopfield 2024-2026 generalization adjacency for Row 1 rank-only AM class.
9. Mezard M, Parisi G, Virasoro MA (1987) "Spin glass theory and beyond" -- spin-glass adjacency for SKAH-M class context (already cap_map cited).
10. Wright S (1931) "Evolution in Mendelian populations" -- drift process for catastrophic forgetting in Row 2.

Verified count: 10 (4 directly load-bearing for rescue sketches; 6 cross-reference / adjacency).

---

# Pre-registered RESCUE PRIORITY (ranked by expected value)

Highest EV rescue drills, ranked:

1. **Cluster A1 (BE-1 W-magnitude-operative test)** -- Row 1 KF-2 cost-advantage. User Run-A1-First binding. Deflated P=0.40-0.45.
2. **Cluster C2 frozen-W-Phase-A** -- Row 2 Bet B Tier-1 architectural rescue. Cheapest architectural arm. Deflated P=0.30-0.40.
3. **B3 codebook-axis multi-N replication** -- Row 3 KF-5 elevation path. Deflated P=0.45-0.55.
4. **Operating-point basin-mapping drill** at beta=beta_c=8, M_frac=[0.25, 0.5, 1.0, 2.0, 4.0] -- resolves Rows 4, 5, 6, 8 simultaneously. Single cross-row drill. Deflated aggregate P=0.50-0.65 (some sub-row resolves).
5. **KF-4 retroactive-BID on existing Bet B 4-stage state** -- Row 7 elevation at 0-cost CPU. Deflated P=0.40-0.50.

Lower-EV rescue drills (deferred unless capacity surplus):

6. F4 Free cumulants on substrate W (Row 12 corroboration).
7. Erase-time-axis at N=4096 M_frac=0.5 (Row 10 sub-axis).
8. Lyapunov exponent finite-N (Row 13 if capacity).
9. KF-3 kerdock-restricted multi-N (Row 9 if capacity).
10. Saad-Solla 5th-axis smoke disambiguation (Row 11 if cheap).

---

# Calibration note

Per [[feedback-lit-scan-calibration-penalty]]: all P estimates above are deflated from raw lit-scan reads by 0.15-0.25. Novel-synthesis P (Row 1 BE-1 rank-only class, Row 5 operating-point-singularity synthesis) capped at 0.50. Hard-fail thresholds are explicitly pre-registered at the row level above; experiment-level thresholds are exp_dev autonomy per [[feedback-no-experiment-design-in-prompts]].

End of fresh-eyes drill.
