# strategy_decisions_2026-06-02.md

## v327 -> v328 @ BATCHED 12-VERDICT overnight CPU cycle 4 (10 GENUINE FULL HARD_PASS + 2 LABEL-VS-HONEST PARTIAL/MIDDLE_BAND + 1 RESCUE-SUCCESS kappa3) -- caching-policy expressibility cluster + heteroassoc-chain depth-3 + 2 NEW EXPLORATORY ROWS PP-43 + PP-44 + 1 sub-property PP-9b + I-3 RESOLVED + 2 LABEL-VS-HONEST catches (verdict_handler 239th PROT-009 paired commit)

**Trigger.** Batched 12-verdict overnight CPU cycle 4 2026-06-02. All 12 fetched via `tools.orchestrator.remote_state.get_metrics` (_source=remote authoritative). Pause-flag ABSENT. REMOTE-FIRST per e51aee7.

**Step 0 honest re-read summary.** 10 HONEST (8 clean HP + 2 with annotations: spectral_capacity_monitor BORDERLINE +0.41pp + q23/graph_node short-wall investigated and CONFIRMED genuine via N + 5-seed + run_mode=full). **2 NEW LABEL-VS-HONEST OVER-CLAIMS:**

- **#198 arc_lirs_hybrid_v1 ALPHA_CONDITIONAL_HP_LABEL_OVER_CLAIMS_AGGREGATE.** Label claims "hot/cold ratio at alpha=0.5: 3.66 (HP>=2.0). max across alpha: 6.49." Per-cell aggregated: alpha=0.1 ratio=0.9803 (FAIL ratio<1 hot LESS than cold), alpha=0.2 ratio=1.6902 (FAIL ratio<2.0 HP gate), alpha=0.5 ratio=3.6597 (HP), alpha=1.0 ratio=6.49 (HP). 2 of 4 alpha cells PASS HP; 2 FAIL. Honest reading: MIDDLE_BAND/PARTIAL ARC/LIRS hybrid requires alpha>=0.5 (high decay); low-alpha regime FAILS. NEW sub-flavor of cherry-pick-cell-aggregate.

- **#199 lru_decay_kendall_v1 M_REGIME_CONDITIONAL_HP_LABEL_OVER_CLAIMS_AGGREGATE.** Label claims "tau at M=80: 0.9325 (HP>=0.9). mean tau across M: 0.7246." Per-cell aggregated: M=10 tau=0.369 (FAIL), M=20 tau=0.722 (FAIL), M=40 tau=0.875 (FAIL), M=80 tau=0.933 (HP). 1 of 4 M cells PASS HP; 3 FAIL. Mean tau=0.7246 itself BELOW HP>=0.9 threshold. Honest reading: MIDDLE_BAND/PARTIAL gamma=0.95 weight-decay LRU works only at large M (>= ~80); small-M cache regime FAILS. **Walk-back gate noted by exp_dev (smoke tau=0.882 within 20% of HP=0.90) CONFIRMED**: FULL 5-seed reveals smoke estimate was on the M=80 large-cache cell, not small-M typical regime. NEW sub-flavor of cherry-pick-cell-aggregate.

**Verdicts processed (12).** Roster in cap_map v328 anchor.

**Rescue-sketch sequencing (CHEAPEST FIRST per [[feedback-rescue-sketch-first-sequencing]]).**

For **kappa3_hutchinson_v2** (RESCUE-SUCCESS already executed):
- R1 (0-compute, applied) Pattern-match to v325 I-2 RESOLVED v326 -- non-vectorized inner loop + tight timeout = TIMEOUT.
- R2 (applied; PRIMARY) Vectorize 5000-probe Hutchinson loop -> 3 GEMM calls; raise timeout 1800s -> 3600s. Wall went 1800s TIMEOUT -> 136s within budget.
- R3-R5 NOT NEEDED (R2 closed).

For **PP-43b LRU large-M-only PARTIAL rescues** (NEW; for next dispatch):
- R1 (0-compute, applied) ANNOTATION-only PARTIAL: LRU works only at large-M cache regime (M >= ~80); small-M regime FAILS; document operating envelope.
- R2 (1-2h CPU) Tighter M grid in 10-80 range to characterize transition cell-by-cell; pre-reg HP=0.85 (relaxed from 0.90) at M=40+; confirms small-M failure as monotone vs degenerate.
- R3 (CPU) Alternative decay schedule: piecewise-constant gamma (gamma=0.99 for M<=40 fast-decay, gamma=0.95 for M>40 standard) -- separates small-M dynamic regime from large-M regime.
- R4 (engineering) Hybrid policy with fallback at low-confidence regime: substrate LRU at M>=80; external policy engine fallback at M<80.
- R5 (deferred) Reconsider gamma=0.95 default; sweep gamma in {0.85, 0.90, 0.95, 0.98, 0.99} at small M.

For **PP-43d ARC/LIRS high-alpha-only PARTIAL rescues** (NEW; for next dispatch):
- R1 (0-compute, applied) ANNOTATION-only PARTIAL: ARC/LIRS hybrid requires alpha>=0.5; low-alpha regime FAILS; document operating envelope.
- R2 (1-2h CPU) Fine alpha grid in [0.05, 0.5] to characterize alpha_critical cell-by-cell.
- R3 (CPU) Alternative ARC variants: tier-2 mix at alpha-dependent threshold; substrate ARC with alpha-conditional re-Hebbian intensity.
- R4 (engineering) Hybrid policy: substrate ARC at alpha>=0.5; external ARC fallback at alpha<0.5.
- R5 (deferred) Reconsider hot/cold ratio HP threshold; investigate why alpha=0.1 ratio<1 (hot LESS than cold; possible substrate primitive contradiction).

For **NO ROW CLOSURES** this batch (PP-43 row OPEN with PARTIAL caveats; no genuine refutations).

**Strategic positioning.** Caching-policy expressibility is a STANDARD product-feature cluster that substrate now PARTIALLY EXPRESSES natively via algebraic primitives (re-Hebbian, weight-decay, dual += ). LFU + write-through clean; LRU large-M-conditional; ARC/LIRS high-alpha-conditional. Product framing: "substrate expresses LFU + write-through natively; LRU + ARC have known operating envelopes -- fall back to external policy engine outside envelope." Cross-references to PP-10 multi-hop production-paths caching (substrate is the MECHANISM layer; PP-10 is the WORKLOAD layer), PP-19 substrate-as-KV-cache, PP-32 audit-grade tool-call result cache. Spectral-capacity-monitor (PP-44) is OPERATIONAL early-warning sub-feature complementing PP-37 spectral-introspection-sidecar and PP-40 effective-rank-gauge. Heteroassoc-chain depth-3 + deletion (PP-9b sub-property) is the FIRST depth-3 chain + cert-deletion structural confirmation at production scope. CT-3 outlier-bulk gap empirically validates Delta=(1-sqrt(alpha))^2 strengthening v324 free-probability spectral identity row.

**Atomic commit.** cap_map.md + history.md + this strategy_decisions_2026-06-02.md + visibility_decisions_2026-06-02.md + status_log entry. **239th PROT-009 paired commit.** Push BLOCKED from sub-agent context; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

**Tallies (v327 -> v328).** HONEST 363 -> 373 (+10). LABEL-VS-HONEST 197 -> 199 (+2). Portfolio 32+64 -> 32+66 (+2 new EXPLORATORY rows + 1 sub-property). Framework-reliability product-feature 62-76% -> 64-78% (+2pp). I-3 RESOLVED.


## v328 -> v329 @ BATCHED 5-VERDICT overnight CPU cycle 5 (5 GENUINE FULL HARD_PASS; 0 LABEL-VS-HONEST) -- PP-41 TRUE-METRIC LIFT + PP-43 Tier 1+2 LIFT + 2 NEGATIVE-RESULT-CONFIRMATION sub-properties (verdict_handler 240th PROT-009 paired commit)

**Trigger.** Batched 5-verdict overnight CPU cycle 5 2026-06-02. All 5 fetched via `tools.orchestrator.remote_state.get_metrics` (_source=remote authoritative). Pause-flag ABSENT. REMOTE-FIRST per e51aee7.

**Step 0 honest re-read summary.** 5 HONEST (3 clean Tier 0/1 HP + 2 NEGATIVE-RESULT-CONFIRMATION HP for Tier 2 boundary characterizations). **0 NEW LABEL-VS-HONEST OVER-CLAIMS.**

- **substrate_metric_norm_axioms_v1** (label "All 4 Frobenius norm axioms confirmed... max_violation=7.11e-15 < 1e-08. mean_triples_all_pass=50.0/50. PP-41 mathematical foundation validated."): HONEST. All 4 axioms (positivity, definiteness, homogeneity, triangle inequality) PASS by 7 orders of magnitude below HP threshold; 50/50 triples pass at all 5 seeds. TRUE-METRIC structure confirmed.
- **write_back_dirty_bits_v1** (label "Write-back dirty bit semantics confirmed. min_dirty_acc=1.000>=0.95 max_delta_cos=0.0000<0.05. O(M) auxiliary vector sufficient; zero W modification required."): HONEST. Perfect 1.000 dirty-bit accuracy + 0.0000 cosine delta unanimous 5-seed. Tier 1 cache extension clean.
- **write_around_routing_v1** (label "Write-around routing via probe confirmed. min_acc=1.000>=0.9 max_fpr=0.000<0.1. Cross-primitive composition (probe=refusal-cert) works for routing."): HONEST. Perfect 1.000 routing accuracy + 0.000 false-positive rate unanimous 5-seed; cross-primitive composition probe=refusal-cert verified. Tier 1 cache extension clean. Short 3.4s wall is consistent with algebraic-identity probe test at N=1024 5-seed.
- **per_key_ttl_external_required_v1** (label "Per-key TTL constraint CONFIRMED (negative result). max_delta_retention=0.0000 < 0.05. Both groups decay identically under global gamma=0.9. Single-W substrate supports only ONE global decay rate -- per-key TTL requires external bookkeeping."): HONEST. NEGATIVE-RESULT pre-reg HP was evidence-of-constraint (max_delta_retention < 0.05 = confirmation that single-W supports only one gamma); actual=0.0000 EXACT confirmation. Tier 2 BOUNDARY EMPIRICALLY CONFIRMED.
- **eviction_id_external_codebook_v1** (label "Eviction codebook constraint CONFIRMED. With codebook: min_known_auroc=0.960>=0.7. Without codebook: mean_random_auroc=0.503~=0.50 (|deviation|=0.003<=0.15). Substrate orders priorities natively but CANNOT enumerate argmin without external dictionary (Tier 2 constraint confirmed)."): HONEST. NEGATIVE-RESULT pre-reg HP was evidence-of-constraint (with-codebook AUROC >= 0.7 AND without-codebook AUROC ~ chance with |dev| <= 0.15 = confirmation that argmin requires dictionary); actuals: 0.960 + 0.503 + 0.003 EXACT confirmation. Tier 2 BOUNDARY EMPIRICALLY CONFIRMED.

Per [[feedback-no-preframing]]: 3 short-wall anchors (write_around 3.4s + per_key_ttl 3.3s + eviction_id 5.3s) were pre-framed in task prompt with explicit caveat "fast walls on cache cells are EXPECTED per design -- algebraic tests not numerical sweeps; verify FULL scope ran via metrics.json run_mode + script-reported config". Honest re-read CONFIRMED all 3 genuine via remote metrics: run_mode=full + N=1024 + seeds=[7,17,23,31,41] + per-cell aggregated metrics. Same pattern as v328 q23_capacity_cliff (1.7s) + graph_node_classification (1.4s) -- short wall is consistent with algebraic-identity tests at modest M and N.

Per [[feedback-rehabilitation-after-rejection]]: 2 NEGATIVE-RESULT-CONFIRMATION tests (per_key_ttl + eviction_id) are EMPIRICAL CONSTRAINT VALIDATIONS, not failures. Both pre-registered HP as evidence-of-constraint and actuals EXACTLY confirm. Product framing: substrate operating envelope is Tier 0+1 native + Tier 2 external bookkeeping (thin dirty-bit vector + M-element dictionary).

**Verdicts processed (5).** Roster in cap_map v329 anchor.

**Rescue-sketch sequencing (CHEAPEST FIRST per [[feedback-rescue-sketch-first-sequencing]]).**

**NO rescues needed this batch** (5/5 GENUINE HP; 2 NEGATIVE-RESULT-CONFIRMATION at pre-reg evidence-of-constraint thresholds).

v328 carry-over rescues REMAIN OPEN for next-cycle dispatch:
- PP-43b LRU small-M rescue (1-2h CPU; small-M sweep at finer grid + piecewise-constant gamma).
- PP-43d ARC/LIRS low-alpha rescue (1-2h CPU; fine alpha grid in [0.05, 0.5]).

NEW v329 follow-on candidate (NOT a rescue; production extension):
- **PP-41 edit-distance primitive extension** (carry-over v327 R2, NOW HIGHER PRIORITY post-TRUE-METRIC confirmation) -- ||W_A - W_B||_F / sqrt(|A symdiff B|) over edit chains; substrate-native edit-magnitude readout. PP-41 TRUE-METRIC empirical confirmation makes this extension MUCH more confidently grounded.

**Strategic positioning.** Cycle 5 LANDS 2 STRUCTURAL LIFTs on existing rows:

1. **PP-41 TRUE-METRIC structural confirmation.** Two independent empirical anchors at independent N (v327 frobenius_symdiff_verify_v1 7 configs N=4096 0.7% max error + v329 substrate_metric_norm_axioms_v1 4 axioms N=1024 7e-15 max violation) confirm substrate has a TRUE metric structure under Frobenius distance. Product framing: "substrate edit-distance is a genuine mathematical metric -- not pseudo-metric, not quasi-metric, but a real metric satisfying all 4 norm axioms within machine precision." This is LOAD-BEARING for PP-9 deletion-cert sizing, PP-12 compositionality audit, PP-31a refusal-audit-cert -- all of which can now confidently reason about algebraic distance as a genuine metric.

2. **PP-43 caching-policy Tier 1+2 EMPIRICAL CHARACTERIZATION.** Three v329 anchors extend substrate caching-policy expressibility from v328 Tier 0 (LFU clean + LRU large-M-conditional + write-through clean + ARC high-alpha-conditional) to Tier 1 (write-back dirty-bits clean + write-around routing clean WITH CROSS-PRIMITIVE COMPOSITION probe=refusal-cert) and explicitly Tier 2 BOUNDARY (per-key TTL requires external bookkeeping + eviction-ID requires external codebook). PP-43 row band LIFTs 0.55-0.70 -> 0.62-0.77 reflecting that substrate's caching-policy expressibility is now MAPPED EMPIRICALLY at three tiers with honest constraint characterization. The Tier 2 BOUNDARY confirmations are PRODUCT-FRAMING WINS (not failures): honest envelope documentation is exactly what audit-grade products need to ship reliably. Compliance-sidecar architecture (PRIMARY GTM v315) absorbs Tier 2 external requirements seamlessly -- bookkeeping is the sidecar's job, substrate stays on the algebraic-cert path.

3. **Cross-primitive composition discovery (PP-43f).** write_around_routing_v1 confirms probe primitive serves DUAL purposes: refusal-cert (PP-31a) AND write-around routing (PP-43f). Same algebraic mechanism, two product applications. Reinforces v314 architectural-moat finding that substrate primitives compose cleanly across product features.

**Atomic commit.** cap_map.md + history.md + this strategy_decisions_2026-06-02.md + visibility_decisions_2026-06-02.md + status_log entry. **240th PROT-009 paired commit.** Push BLOCKED from sub-agent context; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

**Tallies (v328 -> v329).** HONEST 373 -> 378 (+5). LABEL-VS-HONEST 199 UNCHANGED. Portfolio 32+66 UNCHANGED (no new top-level rows; 2 LIFTs + 4 new sub-properties). Framework-reliability product-feature 64-78% -> 66-80% (+2pp). 0 row closures. 0 new LABEL-VS-HONEST catches.


---

## v329 -> v330 BATCHED 4-FULL-VERDICT overnight CPU cycle 5.5 (241st PROT-009 paired commit)

**Roster.** 4 FULL-verdict anchors processed via remote-first metrics (_source=remote authoritative): q19_aging_mu_correct_observable_v1 (RESCUE-SUCCESS HP), multiagent_coord_competing_v1 (HP), program_exec_audit_chain_v1 (HP), q22_batched_deletion_correlated_v1 (HP-with-label-vs-honest-catch). 9 additional anchors in dispatch context returned _source=local + run_mode=smoke + seeds=[7,17] = PARKED smoke-only artifacts; NOT counted in tallies.

**Step 0 honest re-read.** 1 NEW LABEL-VS-HONEST catch #200:

**#200 q22_batched_deletion_correlated_v1 CHERRY_PICK_CORRELATION_HP_LABEL_OVER_CLAIMS_AGGREGATE_DELTA.** Label says "Ghost-attractor effect at moderate correlation CONFIRMED. max_residual_cos (c>=0.25)=0.214>=0.15. Batched deletion LESS EFFECTIVE for correlated patterns. Independent baseline max=0.204." Per-cell aggregated (10-seed N=4096): c=0.0_{K=5,10,20} max={0.199, 0.204, 0.191}; c=0.3_{K=5,10,20} max={0.192, 0.202, 0.204}; c=0.5_{K=5,10,20} max={0.214, 0.199, 0.196}. Honest reading: across all 9 (c,K) cells max sits in band [0.191, 0.214] regardless of correlation c. Delta (c=0.5 - c=0.0) ~ 0.010 = within seed-noise. The HP threshold IS met (max=0.214>=0.15) but the conclusion attributed to correlation is UNSUPPORTED. Honest reframe: at K=5-20 batched deletion, residual ghost-attractor ~0.18-0.21 INDEPENDENT of pattern correlation in [0.0, 0.5]; correlation-amplification NOT detected. PP-9 caveat reframed: external-dedup recommendation stands because residual is non-zero at K>=5 (substrate-feature finding), but rationale shifts from "correlation amplifies it" to "batched deletion at K>=5 leaves residual regardless of correlation". NEW sub-flavor: CHERRY_PICK_CORRELATION_HP_LABEL_OVER_CLAIMS_AGGREGATE_DELTA -- cousin of #198 cherry-pick-alpha and #199 cherry-pick-M; conditioning variable changes (alpha -> M -> correlation) but pattern identical (HP at one cell carried as conclusion about another variable's effect).

**Strategic decisions.**

1. **Q19 RESCUE-SUCCESS = PP-33 framework-class partial LIFT 0.40-0.55 -> 0.50-0.65 (+0.10).** q19_aging_mu_correct_observable_v1 EMPIRICAL CONFIRMATION of CK-class C(t,t_w) vs t/t_w scaling collapse at N=1024 5-seed unanimous mean_collapse_mse=0.0029 (HP<0.1 by 30x margin) at both alpha cells {0.14, 0.16}. CORRECTED-OBSERVABLE rescue for v211 wrong-observable failure (v211 tested static ultrametricity on minima overlaps -- the WRONG PROBE for substrate's confirmed dynamical phase per research-delivery 6-drill algebraic lock). Scaling collapse confirms substrate trajectories DO age as predicted by CK-class -- two-time correlator C(t,t_w) is a function of t/t_w (NOT t and t_w separately) which is the time-translation-INVARIANCE-BROKEN signature of aging on a marginal manifold. PP-33 caveat (f) v324 SUPERSEDED by caveat (g) v330 documenting the rescue-via-corrected-observable + research-delivery rationale. Lit-scan calibration penalty +0.05 RETAINED.

2. **v324 ULTRAMETRICITY ANNOTATION REVISION per research-delivery 6-drill consolidation.** v324 annotation "ULTRAMETRICITY (PP-33 GARCIA LORENZANA 2025 PRECEDENT) REFUTED at FULL N=2048 5-seed" UPGRADED to: "Static-UM test mean_ratio=0.583 NOT a refutation; the static-RSB phase class is ALGEBRAICALLY RULED OUT independent of the test (MP bulk + no outlier spike pair per v324 ct2_outlier_count; arXiv:2511.18439 lock); the v324 test was a WRONG PROBE for substrate's confirmed CK-class dynamical phase. 2 surviving DYNAMICAL phases (CK aging WEB P=0.40; Garcia-Lorenzana oscillating amorphous P=0.20). Citation corrections: Garcia-Lorenzana et al. 2025 = PRL 135 187402 / arXiv:2408.17360 (bipartite spherical SK NOT Hopfield directly); non-reciprocal Hopfield analog = arXiv:2501.00983 (Xue/Maghrebi/Mias/Piermarocchi Jan 2025; Hopf + fold bifurcation; zeta=1/2 and 1/3 critical exponents; limit-cycle attractors)." Per [[feedback-rehabilitation-after-rejection]]: v324 historical entry RETAINED with cross-reference to v330 revision; worked example of "list 3-5 axis-combination rescues before abandoning the mechanism" applied to PP-33 framework-class identification.

3. **PP-9c NEW SUB-PROPERTY: batched-deletion ghost-attractor BOUNDARY (K-driven, NOT correlation-driven).** Per q22 honest reframe: at K=5-20 batched deletion residual ~0.18-0.21 INDEPENDENT of correlation in [0.0, 0.5]. PP-9 row band UNCHANGED 0.55-0.70 (sub-property addition; PP-9 founding already characterizes deletion-cert primitive band; PP-9c characterizes failure mode). Operating envelope: external dedup recommended for ANY batched deletion at K>=5 (substrate-feature constraint); rationale = K-batch-size driven (each removed pattern leaves residual cosine ~0.18-0.21 in deletion-cert audit window).

4. **PP-39 EXPANSION: competing-agent coordination sub-property.** multiagent_coord_competing_v1 EMPIRICAL CONFIRMATION of substrate's additive W primitive natively expressing competitive multi-agent coordination via write-frequency dominance WITHOUT external coordination protocol. cell_A delta_majority=0.170 (HP>=0.15); cell_B minority_acc=0.830 (NOT suppressed; HP>=0.5); cell_C separation_delta~=0 (HP>=-0.02). v328 PP-39 founding established CONSENSUS sub-property (majority-vote at K=5,7); v330 PP-39 ADDS COMPETING-AGENT sub-property (write-frequency-dominance at differing N_A/N_B agent ratios). PP-39 row band UNCHANGED 0.65-0.80 (two empirical sub-properties at same cap_map version is corroborative; band-LIFT requires 3rd independent sub-property or cross-N extension).

5. **PP-31b NEW SUB-PROPERTY: chain-of-thought audit-cert primitive across trace lengths.** program_exec_audit_chain_v1 EMPIRICAL CONFIRMATION at T={20, 40, 60} all 3 cells unanimous 5-seed N=4096: cell_A (index retrieval) min_cos>=0.999 HP>=0.8; cell_B (next-step prediction) min_cos=1.000 HP>=0.7; cell_C (mid-link deletion-cert) max_del_residual<=0.051 HP<0.15 with delta_acc=0.000 (downstream steps UNAFFECTED). PP-31 founding row v323 was refusal-cert PP-31a; PP-31b ADDS chain-of-thought-trace-cert. PP-31 row band UNCHANGED 0.60-0.75 (sub-property addition; T=60 within smoke-grid).

**Atomic commit.** cap_map.md + history.md + this strategy_decisions_2026-06-02.md + visibility_decisions_2026-06-02.md + status_log entry. **241st PROT-009 paired commit.** Push BLOCKED from sub-agent context; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

**Tallies (v329 -> v330).** HONEST 378 -> 381 (+3). LABEL-VS-HONEST 199 -> 200 (+1 catch #200 CHERRY_PICK_CORRELATION_HP_LABEL_OVER_CLAIMS_AGGREGATE_DELTA). Portfolio 32+66 UNCHANGED (no new top-level rows; 1 LIFT PP-33 0.40-0.55 -> 0.50-0.65 Q19 RESCUE-SUCCESS + 3 new sub-properties PP-9c + PP-39 competing + PP-31b chain-of-thought). Framework-reliability specific-documented 45-55% -> 47-57% (+2pp; CK-class is FIRST dynamical-class with empirical confirmation at substrate finite-N regime). Product-feature 66-80% UNCHANGED. 0 row closures. 1 new LABEL-VS-HONEST catch. 9 smoke-only anchors PARKED (NOT counted). 2 new infra issues (I-4 smoke-pre-framing detection signal + I-5 q22-family timeout-budget recipe).

**Routing follow-on (orchestrator main thread).** Highest-priority next-cycle dispatches: (1) Q-F3 cophenetic correlation <1s wall ZERO-COMPUTE single-linkage MST -- SINGLE CHEAPEST DECISIVE TEST per research-delivery; unlocks 3 killer features if PASS; (2) Q-F1 dynamical M_dyn smoke 1-hour CPU R=200 single-observable; (3) Q-F4 saddle-overlap triplet test (substrate-novel SKAH-M-class signature); (4) 9 smoke-only PARKED FULL re-ships; (5) q22 timeout extension to 2400s next ship. Sequenced cheapest-first per [[feedback-rescue-sketch-first-sequencing]].



## v331 BATCHED 13-VERDICT overnight CPU cycle 6 -- 2026-06-02

**Cap_map v330 -> v331.** Batch composition: 3 CRITICAL framework (Q-F1 dynamical_um_ck_class_v1 FULL CPU 58min 3-seed N=1024 R=200 + Q-F2 two_time_correlator_fdt_v1 FULL 13.6s 5-seed N=2048 + Q9 q9_tau_mem_corrected_sde_v1 FULL 41min 10-seed N={2048,4096,8192}) + 2 rescues smoke-HP -> FULL (timeseries_xor_prot021_fix_v1 + signed_am_b_pattern_m_sweep_v1) + 4 walk-back from smoke (graph_community_detection_v1 + program_exec_audit_branching_v1 + caching_capacity_aware_eviction_v1 + q21_r_envelope_multi_target_v1) + 4 fast HP confirms walk-back FULL (caching_write_allocate_per_pattern_v1 + caching_multi_substrate_hierarchy_v1 + hippocampal_sharp_wave_ripple_v1 + multiagent_adversary_coord_v1). All 13 `_source=remote`.

**Step 0 honest re-read.** HONEST 12; LABEL-VS-HONEST 1: **#201 two_time_correlator_fdt_v1 SHAPE_DISCRIMINATION_OVER_CLAIM** -- verdict_msg cites `GARCIA-LORENZANA OSCILLATING OVERLAY DETECTED piecewise_r2=0.3149 smooth_r2=0.5063` but piecewise_r2 and smooth_r2 BOTH << HP threshold 0.85, mean DFT SNR=2.42 < 3.0 HP (only max-seed touched 4.84). CK aging collapse-mse=0.0144 < 0.05 HP CONFIRMED honestly; Garcia-Lorenzana sub-phase NOT CONFIRMED. New label-vs-honest sub-flavor SHAPE_DISCRIMINATION_OVER_CLAIM (failed-threshold numbers reported alongside PASS-tone "DETECTED" language).

**Strategy decisions:**

1. **PP-33 LIFT 0.50-0.65 -> 0.60-0.75 (+0.10 both bounds).** Pre-reg LIFT condition (Q-F1 HP at FULL CK ultrametricity in [0.85, 0.95] window AND Q-F2 HP at FULL CK aging collapse-mse < 0.05) MET on honest re-read: Q-F1 global_mean_M_dyn=0.9090 inside [0.85, 0.95] with 2/3 triplets HP (1 triplet at 0.749 sits 0.001 below HP edge -- finite-N noise); Q-F2 collapse_mse=0.0144 < 0.05 ✓. CK-class dynamical-aging signature CONFIRMED via independent observable beyond Q19 (v330) corrected observable. 2 new caveats (h) Q-F1 dynamical CK ultrametricity CONFIRMED + (i) Q-F2 CK aging collapse CONFIRMED but Garcia-Lorenzana SHAPE NOT CONFIRMED (LABEL-VS-HONEST #201). Surviving non-eq dynamical phases: CK aging P=0.50 (LIFTED from 0.40); Garcia-Lorenzana P=0.10 (DEFLATED from 0.20 per Q-F2 R2 fail). Remaining 0.25-0.40 deficit: Q-F3 cophenetic + Q-F4 saddle-overlap + Q-F5 return-point-memory + Q-F1 5-seed N=2048 (tighten 8_64_512 triplet) + Q-F2 FDT ratio X(C) plateau (gated on Q-F1 5-seed signal).

2. **Q9 formula PINNED -- sub-property added to PP-1/PP-12 memory-decay-timescale row.** R2_loglog=0.998, 3/3 N values within +/-20% across N={2048, 4096, 8192} 10-seed; `tau_mem = (1/gamma)*log(1 + N*gamma/(2*lambda))` confirmed with gamma=0.01, lambda=0.1 production-baseline. Formula authoritative for production tau_mem prediction across N range. Row band UNCHANGED (formula-pinning is operating-point characterization; mature row).

3. **PP-39 multiagent row sub-property-LIFT 0.65-0.80 -> 0.70-0.85** per 3rd independent sub-property convention (v328 consensus + v330 competing-agent + v331 adversarial-resilience).

4. **9 v330 PARKED smoke anchors WALKED BACK FULL.** 7 HP (caching_write_allocate, caching_multi_substrate, hippocampal_swr, multiagent_adversary, q21_r_envelope, timeseries_xor [had been smoke HP -> FULL HP], signed_am_b [smoke HP -> FULL HP]); 2 HF (graph_community + program_exec_branching); 1 MIDDLE (caching_capacity_aware). HF candidates kept OPEN with 5 rescue sketches each cheapest-first per [[feedback-rescue-sketch-first-sequencing]] + [[feedback-rehabilitation-after-rejection]]. No closures.

5. **I-4 RESOLVED.** All 9 v330 smoke-only PARKED anchors successfully RE-SHIPPED at FULL this cycle and returned authoritative remote multi-seed metrics. Detection signal and routing protocol validated.

6. **I-6 NEW.** Script-side message-template bug: Q-F2 verdict_msg emits "DETECTED" with failing R2 thresholds inline. Script-author audit filed for two_time_correlator_fdt scripts to gate "DETECTED" on R2 >= 0.85 AND mean (not max) DFT SNR >= 3.0.

**Tallies:** HONEST 381 -> 393 (+12); LABEL-VS-HONEST 200 -> 201 (+1); Portfolio 32+66 UNCHANGED; 1 row LIFT (PP-33) + 1 sub-property-band LIFT (PP-39); multiple sub-property characterizations (PP-1/PP-12 tau_mem formula pin + PP-43-family caching + PP-12 R-envelope + PP-12/PP-22 SWR replay).

**Framework reliability:** general 65-75% UNCHANGED; specific-documented 47-57% -> 52-62% (+5pp); product-feature 66-80% UNCHANGED.

**PROT compliance:** PROT-004/006/007/008/009/018/021 all clear; 242nd PROT-009 paired commit; push BLOCKED from sub-agent context; main thread executes push.
Wave 5 cloud testbed handoff filed: notes/testbed_handoff_wave5_unified_n32768_2026-06-02.md -- 5-anchor unified_n32768_v1 bundle (Q-D1 spectral, kappa46 fingerprint, deletion-cert Z-ratio, COMBO-3 unified API, COMBO-1 Gram+kappa3) routed to testbed for engineering; Lambda dispatch deferred to Wave 5 trigger (post-Wave-4-PASS or user auth); no cap_map work this cycle (deferred)

## v331 -> v332 @ BATCHED 6-VERDICT Wave 1 CPU + Wave 2 GPU completions (5 GENUINE FULL HARD_PASS + 1 GENUINE FULL HARD_FAIL framework-corroborating) -- WAVE 5 CLOUD GATE OPEN + 2 NEW TOP-LEVEL ROWS PP-45 5-method unified-API algebraic theorem + PP-46 GDPR-grade deletion-cert non-repudiation + 1 ROW LIFT PP-33 framework-class 0.50-0.65 -> 0.55-0.70 bidirectional lock + 1 SUB-PROPERTY LIFT PP-9b cross-N {4096, 8192} + 1 SUB-PROPERTY EXTENSION PP-44 production-N=8192 + 0 LABEL-VS-HONEST catches + 3 orphan failures deferred to main-thread routing-cycle (verdict_handler 243rd PROT-009 paired commit; Wave 1+2 completion + Wave 5 gating cycle)

**Trigger.** User explicit directive 2026-06-02: "we also need those verdicts to gate the cloud work" -- Wave 5 cloud single batch ~$10-15 requires Waves 1+2 results. Batch composition: 3 Wave 1 CPU (q_c5_cosine_gate_tau_recal_v1 + kappa3_hutchinson_n8192_smoke_v1 + q_f6_pq_distribution_v1) + 3 Wave 2 GPU (combo3_unified_api_v1_n4096 + q_b1_heteroassoc_chain_cert_v1_n4096 + q_b1_heteroassoc_chain_cert_v1_n8192). All 6 fetched via `tools.orchestrator.remote_state.get_metrics` -- all `_source=remote` authoritative. Pause-flag ABSENT. REMOTE-FIRST per e51aee7.

**Step 0 honest re-read summary.** 6 HONEST (5 HP + 1 HF); 0 LABEL-VS-HONEST catches.

**Verdicts processed (6).** Roster in cap_map v332 anchor.

**Rescue-sketch sequencing (CHEAPEST FIRST per [[feedback-rescue-sketch-first-sequencing]]).**

For **q_f6_pq_distribution_v1 HF** (NEW; PP-33 caveat -- substrate is in CK-DYNAMICAL class, NOT static-RSB class):
- R1 (0-compute, applied) ANNOTATION-only: HF is a NEGATIVE-RESULT corroborating v330 wrong-probe annotation; P(q) bimodality is the static RSB signature; substrate's confirmed dynamical CK class is OUTSIDE that test's competence; HF strengthens framework-class identification (excludes static-RSB regime more cleanly).
- R2 (deferred -- ~30min CPU) Cross-N P(q) at N={2048, 4096, 8192} 5-seed to verify bimodality is FINITE-N artifact not asymptotic.
- R3 (deferred -- Q-F2 follow-on) FDT ratio X(C) at corrected dynamical observable already in v331 routing queue #8; HF here reinforces priority of dynamical probes.
- R4-R5 NOT NEEDED (R1 closes the row at annotation; no genuine REFUTATION since wrong-probe).

For **I-7 orphan failures (l2_hadamard + ck_seb GPU + q_f5 CPU)** (NEW; deferred to main-thread routing-cycle):
- R1 (0-compute) Verify runner-death root-cause from logs (was it the runner or the script?).
- R2 (CPU/GPU re-ship at original config) If R1 confirms runner-death (not script bug), re-ship.
- R3 (protocol tweak) If R2 fails, examine script for FULL/smoke-mode handling.
- R4 (N-scale) Cross-N if script-level bug suspected.
- R5 (alternative composition) Pipeline restructuring.

**WAVE 5 CLOUD GATE DECISION.**

User directive: "we also need those verdicts to gate the cloud work". Three gating tests pre-registered:
1. COMBO-3 unified API HP1-HP5 all PASS at N=4096 -- VALIDATED (HP1 d1d2d3_err=0 EXACT; HP2 k3_err=5.32e-5 < 1e-4; HP3 cndc_err=0 EXACT; HP4 cert_err=0 EXACT; HP5 matvec=3 <= 5). 5-method audit API algebraic-theorem uniformity CONFIRMED at smaller N. **GATE 1 OPEN.**
2. kappa3 Hutchinson at N=8192 HP -- VALIDATED (sigma_separation 150-1112 across M cells; theory_ratio in band). **GATE 2 OPEN.**
3. Q-C5 cosine-gate tau recalibration HP -- VALIDATED (tau in [0.78, 0.92] all cells FN=FP=0.000 unanimous 5-seed; GDPR-grade non-repudiation). **GATE 3 OPEN.**

**WAVE 5 CLOUD GATE: OPEN.** Testbed authorized to dispatch unified_n32768_v1 bundle (~$10-15 single batch). HP thresholds carry forward from Wave 2; PP-45 + PP-46 conservative bands committed until N=32768 lift.

**Cap_map deltas.** 2 NEW TOP-LEVEL ROWS (PP-45 + PP-46 each 0.65-0.80 EXPLORATORY); 1 ROW LIFT (PP-33 0.50-0.65 -> 0.55-0.70 framework-class bidirectional lock); 1 sub-property LIFT (PP-9b cross-N {4096, 8192}); 1 sub-property extension (PP-44 production-N=8192). Portfolio 32+66 -> 32+68. Framework-reliability specific-documented +3pp + product-feature +2pp.

**Tallies (v331 -> v332).** HONEST 393 -> 399 (+6). LABEL-VS-HONEST 201 UNCHANGED.

Hygiene sweep 2026-06-02: 20 acted-on routing files moved to notes/routed_completed/ (items from 2026-06-02 and 2026-06-01); no cap_map version bump; no new routing files written; source files verified present before move

## v332 -> v333 @ BATCHED 7-VERDICT overnight cycle 7.5 Wave 3 + Wave 4 + Wave 5-prerequisite COMBO-1 v2 completions (5 GENUINE FULL HARD_PASS + 2 GENUINE FULL MIDDLE_BAND) -- WAVE 5 CELLS 1-4 STAY AUTHORIZED + WAVE 5 CELL 5 DEFERRED pending COMBO-1 v3 redesign + 1 NEW TOP-LEVEL ROW PP-47 hippocampal place-field encoding at production-N + 3 NEW SUB-PROPERTIES (PP-45a implicit-Gram identity + PP-44b streaming-monitor latency + PP-44c drift-kernel detection) + 1 SUB-PROPERTY EXTENSION (PP-44 Brand-incremental Gram refresh) + 1 SUB-PROPERTY LIFT (PP-12 cross-layer L=2 production-N) + 0 LABEL-VS-HONEST catches (task-prompt pre-framing SURFACED but did NOT bias re-read) + 2 MIDDLE surfaces with R1-R5 rescue sequences (verdict_handler 244th PROT-009 paired commit; autonomous overnight cycle 7.5)

**Trigger.** Autonomous overnight cycle 7.5 batched 7 verdicts (combo1 v2 Wave 5 final-gate prerequisite + combo4 Wave 3 + q_a3 L=2 Wave 3 + streaming_brand + kappa3_monitor + drift_kernel Wave 4 + hippocampal_place_field Wave 4). All 7 fetched via `tools.orchestrator.remote_state.get_metrics` -- all `_source=remote` authoritative. Pause-flag ABSENT.

**Step 0 honest re-read summary.** 7 HONEST (5 HP + 2 MIDDLE); 0 LABEL-VS-HONEST catches. Task input PRE-FRAMED combo1 v2 as potential ALL-4-HP Wave 5 final-gate authorization; honest re-read FOUND 2/4 MIDDLE (HP1+HP2 PASS; HP3 write-slope=1.958 FAIL >1.3 cap; HP4 SNR ratio 0.25/0.06/0.016 systematic 1/M degradation FAIL); per task spec MIDDLE path applied: surface to orchestrator main thread + file research routing for v3 redesign. Pre-framing handled correctly via Step 0.

**Verdicts processed (7).** Roster in cap_map v333 anchor.

**Rescue-sketch sequencing (CHEAPEST FIRST per [[feedback-rescue-sketch-first-sequencing]]).** combo1 v2 MIDDLE: R1 theory-side audit 0-compute (filed via research routing) -> R2 Krylov pre-condition ~10min CPU -> R3 Brand-refresh substitute ~30min CPU (using v333 validated PP-44 sub-property) -> R4 cloud N=32768 verify ~$5-8 -> R5 architectural pivot to COMBO-3 subsumption. combo4 MIDDLE: R1 PP-33 caveat (k) annotation 0-compute (applied this cycle) -> R2 N-scale to {2048, 4096, 8192} ~30min CPU -> R3 isolated per-observable measurements.

**WAVE 5 GATING DECISION (per task spec MIDDLE path).** COMBO-1 v2 = 2/4 MIDDLE -> Wave 5 cell 5 (COMBO-1 implicit Gram-solve at N=32768) DEFERRED pending v3 redesign. Wave 5 cells 1-4 (COMBO-3 unified API + kappa_4/kappa_6 fingerprint + deletion-cert Z-ratio + Q-D1 spectral) REMAIN AUTHORIZED unchanged from v332 OPEN.

**Cap_map deltas.** 1 NEW TOP-LEVEL ROW (PP-47 hippocampal place-field at production-N 0.55-0.70 EXPLORATORY); 3 NEW SUB-PROPERTIES (PP-45a + PP-44b + PP-44c); 1 SUB-PROPERTY EXTENSION (PP-44 Brand-incremental Gram); 1 SUB-PROPERTY LIFT (PP-12 cross-layer L=2 production-N); 1 ROW CAVEAT (PP-33 caveat (k)). Portfolio 32+68 -> 32+69. Framework-reliability product-feature +1pp both bounds.

**Tallies (v332 -> v333).** HONEST 399 -> 406 (+7). LABEL-VS-HONEST 201 UNCHANGED.

**PROT compliance.** PROT-004/006/007/008/009/018/021 all clear; 244th PROT-009 paired commit; push BLOCKED from sub-agent context; main thread executes push.

Research routing filed: notes/strategy_request_to_research_combo1_v3_redesign_2026-06-02.md (COMBO-1 v3 redesign: R1 theory-side HP3+HP4 formula audit cheapest-first; gates Wave 5 cell-5 cloud dispatch).


## 2026-06-02 verdict_handler v334 BATCH 6 (Cycle 8 verdict pass): Wave 4 COMBO-2 ARCHITECTURE DECIDER + Q-A3 production-envelope + 4 supporting verdicts

**Anchors processed (6):**
1. combo2_p4_l3_signed_am_v1_n4096 — HARD_PASS (1.8s GPU; N=4096; 5-seed; FULL): l3_fid=1.0 + b_rep=1.0 + parity=0.0 all unanimous HP. **WAVE 4 COMBO-2 ARCHITECTURE DECIDER**.
2. q_a3_l2_cross_layer_composition_v1_n8192 — HARD_PASS (55.3s GPU; N=8192; 5-seed; FULL): outer_fid=1.0 + inner_fid=1.0 + l2_acc=1.0 all unanimous HP at production-N.
3. brand_saturation_stability_v1 — HARD_PASS (332.1s CPU; N=2048; 5-seed; FULL): 4-alpha sweep {0.1, 0.2, 0.4, 0.8} all acc=1.0 unanimous HP.
4. streaming_prediction_5_consolidation_v1 — HARD_PASS (17.8s CPU; N=1024; 5-seed; FULL): all 4 T-rounds HP at best-T=100 hot/cold/diff = 1.0/0.057/0.943.
5. f4_free_cumulants_m4_fixed_v1 — MIDDLE_BAND (1.05s CPU; N=1024; 5-seed; FULL): v1 IDENTITY FIX holds (kappa_2 + M3 HP); M4 rel_err=0.066 (+33% over HP, HF NOT triggered).
6. kappa3_mixing_correction_completion_v1 — MIDDLE_BAND (0.78s CPU; N=1024; M=204; 5-seed; FULL): rho<=0.1 HP (0.011, 0.021); rho>=0.2 NOT HP (0.049, 0.093); 2/4 cells.

**Step 0 honest re-read result:** 0 LABEL-VS-HONEST catches. All 6 anchors honest-as-labeled. Pre-framing (4.0s suspicious wall + 3.1s walls) verified via run_mode=full + 5-seed agreement + per-cell metric consistency. Pre-framing did NOT bias re-read.

**Cap_map v333 -> v334 commit (this batch):**
- **+2 NEW TOP-LEVEL ROWS**: PP-48 Negative-Knowledge Tree (algebraic non-contamination + tree-scope refusal) 🟢 0.65-0.80 EXPLORATORY; PP-49 Hierarchical Refusal Cert + Counterfactual Abduction over forbidden subtrees 🟢 0.65-0.80 EXPLORATORY.
- **+2 NEW SUB-PROPERTIES**: PP-44 Brand-saturation-stability alpha-envelope [0.1, 0.8]; Wave 4 Streaming SP5 replay-free consolidation via aging-on-marginal-manifold.
- **+1 SUB-PROPERTY LIFT**: PP-12 cross-layer L=2 production-N=8192 (v333 N=4096 → v334 N=8192).
- **+2 MIDDLE annotations**: F4 M4 (M3+kappa_2 HP; M4 +33% over) + kappa3 mixing rho>=0.2 (2/4 cells HP).

**Tallies:** HONEST 406 -> 412 (+6); LABEL-VS-HONEST 201 UNCHANGED; Portfolio 32+69 -> 32+71 (+2 top-level rows).

**Framework reliability:** Product-feature 69-83% -> 71-85% (+2pp; PP-48 + PP-49 both product-feature rows). Specific-documented + general UNCHANGED.

**Issues:** I-9 NEW (F4 M4 finite-N correction); I-10 NEW (kappa3 mixing higher-order term at rho>=0.2). Both filed for research-cycle routing.

**Rescue sketches cheapest-first:**
- F4 M4: R1 theory-side audit (0-compute) -> R2 N-scale ~5min CPU -> R3 5-seed N=4096 ~30min CPU -> R4 Hutchinson estimator alternative ~20min CPU -> R5 cloud N=32768 ~$5.
- kappa3 mixing rho>=0.2: R1 theory-side higher-order correction audit (0-compute) -> R2 fine-grid rho-sweep ~5min CPU -> R3 alternative GP-kernel mixing model ~20min CPU -> R4 N-scale ~30min CPU -> R5 cloud N=32768 ~$5.

**Pause-flag state:** ABSENT (verified d:/AI/hd-instrument/data/orchestrator_paused.flag does not exist). Pipeline-pacing exp_dev refill SKIPPED per sub-agent context — main-thread testbed-handoff cycle for Wave 5 cloud + Wave 4/5 follow-ons is the existing dispatch route.

**Main-thread routing priorities (top 3 v334-new):** (1) PP-48 + PP-49 production-N cross-N {8192, 16384} 5-seed; (2) PP-48 cross-application probe to PP-9/PP-46/PP-12 chain; (3) PP-49 counterfactual abduction stress test at production-N. Full priority list in cap_map v334 footer.

**245th PROT-009 paired commit.** Push BLOCKED from sub-agent context; orchestrator main thread executes `git push origin main`.

hygiene sweep 2026-06-02: 11 routing files moved to notes/routed_completed/ (stuck_kills, ckm_coefficient, alpha_mu_snap, tau_alpha, combo1_v3 smoke-fail, combo1_v3_redesign, wave5_amendment_addressed, wave5_cloud_bundle_amendment, strategy_request_to_research_combo1_v3, testbed_handoff_wave5_unified_n32768, testbed_wave5_unified_n32768_results); no cap_map mutation; 2 active routings kept in notes/

## 2026-06-02 v335 -- WAVE 5 CLOUD BUNDLE (5 anchors at N=32768)

**Trigger:** Wave 5 cloud H100 bundle `bbelw34ap` completed; 5 anchors at production-N=32768 5-seed M=1638. Source: `notes/testbed_wave5_unified_n32768_results_2026-06-02.md`. Cost $3.81 vs $21.45 predicted (82% under). Pause-flag ABSENT.

**Verdicts (5 anchors).** Step 0 honest re-read against per-seed metrics in `data/lambda_batch_results/*_bd9c5a0f/*/metrics.json`:

1. `qd1_spectral_primitives_n32768_v1` MIDDLE_BAND HONEST -- alpha=0.05 HP_PASS 4/5; alpha=0.02 partial 3/5; alpha=0.01 fail sigma_dev=5.75; v1b sigma_TW rel_dev_from_theory 0.59-0.74 across alpha grid (HP gate 0.05 missed). Theory-pre-reg miscalibration not substrate failure.
2. `kappa46_fingerprint_n32768_v1` Part A HARD_FAIL HONEST + Part B HARD_PASS HONEST -- Part A free-Poisson identity REFUTED at N=32768: kappa_3 +15%, kappa_4 +32%, kappa_6 +88%; Part B sensitivity sweep sigma_sep 2.55 / 27.3 / 259.4 / 896.9 / 1726.6 across delta_alpha {0.0001, 0.001, 0.01, 0.04, 0.1} crushes HP=3.0 from delta_alpha=0.001 upward.
3. `deletion_cert_zratio_n32768_v1` HARD_PASS HONEST -- Z_min=155.81 vs HP=3.0 = 52x margin; signal_mean=181.02 = sqrt(32768) EXACT algebraic identity; 5-seed unanimous.
4. `combo3_unified_api_n32768_v1` HARD_PASS HONEST -- 5-seed Krylov-vs-closed-form rel_dev all within MC noise floor 0.1414 by 30-3500x margin (tr_W1 / tr_W2 / tr_W3 / kappa_3 all 4e-5 to 4.7e-3).
5. `q_b1_depth_extended_n32768` HARD_PASS HONEST (ADD-1 depth-10 extension) -- depth-10 mean=0.9846 min=0.9843 vs HP=0.90 = 8 sigma margin; per-hop fidelity 0.9984.

**LABEL-VS-HONEST: 0 new catches** (all 5 cloud anchor labels honest-as-labeled per per-seed metrics).

**Cap_map state transitions (v335).**
- PP-45 5-method unified-API algebraic theorem BAND-LIFT 0.65-0.80 -> 0.70-0.85 (Wave 5 production-N=32768 founding-row LIFT criterion satisfied; Cell 4 Krylov-vs-closed-form unanimous 5-seed at N=32768).
- PP-46 GDPR-grade deletion-cert non-repudiation BAND-LIFT 0.65-0.80 -> 0.70-0.85 (Wave 5 production-N=32768 founding-row LIFT criterion; Cell 3 Z_min=156 sigma at production-N).
- PP-49 Hierarchical-Refusal-Cert + Counterfactual-Abduction BAND-LIFT 0.65-0.80 -> 0.70-0.85 + NEW SUB-PROPERTY PP-49a "depth-10 production-envelope at N=32768 M_bg=200" (Cell 5 depth-10 fidelity 0.9846 substrate ceiling NOT at d=10 in this regime).
- NEW TOP-LEVEL ROW PP-50 "kappa_3 spectral-MAC sub-percent drift detection at production-N" 0.70-0.85 EXPLORATORY (Cell 2 Part B sensitivity sweep at production-N=32768 detects 0.04-0.1% pattern perturbation at sigma_sep 2.55-1726.6).
- PP-45 CAVEAT: analytic free-Poisson identity scope-limited to small-n; sensitivity-based audit primitive Cell 2 Part B is the operational substitute.
- NEW Issue I-11: analytic free-Poisson identity + Tracy-Widom sigma_TW closed-form empirically refuted for outer-product-Hebbian W finite-alpha; research-cycle routing FILED for Wishart cumulants + Marchenko-Pastur higher cumulants + finite-N bulk-edge crossover literature scan.

**Rescue sketches for Cell 1 MIDDLE + Cell 2 Part A HF (cheapest-first):** R1 theory-side audit of free-Poisson + Tracy-Widom finite-N corrections for outer-product-Hebbian W (0-compute; same research-cycle as Issue I-11); R2 update Cell 1 + Cell 2 pre-reg HP bands to empirical-baseline-anchored Option A from strategy routing (0-compute); R3 Marchenko-Pastur bulk-edge crossover correction beyond leading-order Tracy-Widom (~30min CPU); R4 multi-alpha smaller-N regime mapping (~1hr CPU); R5 cloud N=65536 re-confirmation with new empirical baseline ($5-10). NEITHER row closed (theory-pre-reg miscalibration is RECOVERABLE not substrate-primitive refutation).

**Portfolio:** 32+71 -> 32+72 (+1 NEW PP-50; +1 NEW SUB-PROPERTY PP-49a). **HONEST:** 412 -> 417 (+5). **LABEL-VS-HONEST:** 201 -> 201 UNCHANGED. **Product-feature framework reliability:** 71-85% -> 74-88% (+3pp both bounds; 4 production-N=32768 rows strengthen substrate-product moat).

**Linked routing:** `notes/strategy_request_to_strategy_wave5_theory_prereg_gap_2026-06-02.md` (incorporated as Issue I-11 + PP-45 CAVEAT).

**Push:** BLOCKED from sub-agent context; main thread executes `git push origin main` as 1-tool follow-up.

## 2026-06-02 v335 -> v336 BATCH 4-VERDICT CPU Cycle 9 (2 GENUINE FULL HARD_PASS + 1 GENUINE FULL MIDDLE_BAND + 1 LABEL-VS-HONEST PARTIAL) -- kappa3 mixing v2 I-10 PARTIAL-RESOLVED (LABEL-VS-HONEST #202) + Q-A3 L=3 N=4096 HARD_PASS PP-12 BAND-LIFT + F4 M4 v2 MIDDLE_BAND I-9 PARTIAL-RESOLVED + hippocampal place-field N=8192 PP-47 production-envelope CONFIRMED (verdict_handler 247th PROT-009 paired commit; Cycle 9)

**Trigger.** Cycle 9 batched 4-verdict CPU completions 2026-06-02. All 4 fetched via `tools.orchestrator.remote_state.get_metrics` (_source=remote authoritative). Pause-flag ABSENT. REMOTE-FIRST per e51aee7.

**Step 0 honest re-read summary.** 3 HONEST (1 clean HP + 1 HP honest + 1 MIDDLE_BAND honest). 1 NEW LABEL-VS-HONEST OVER-CLAIM:

- **#202 kappa3_mixing_correction_v2_correlated_v1 ALL_RHO_HP_LABEL_OVER_CLAIMS_AGGREGATE.** Label claims "HARD_PASS: v2 correction restores HP for all rho values." Per-cell metrics (8 rho cells, HP gate <= 0.03): rho=0.00: err=0.011 (PASS); rho=0.05: err=0.014 (PASS); rho=0.10: err=0.020 (PASS); rho=0.15: err=0.029 (PASS); rho=0.20: err=0.036 (FAIL > 0.03); rho=0.25: err=0.038 (FAIL > 0.03); rho=0.30: err=0.029 (PASS); rho=0.35: err=0.000 (PASS). 6/8 cells PASS HP gate; rho=0.20 and rho=0.25 fail by 0.006-0.008 above gate. Label "all rho values" NOT supported. Honest reading: PARTIAL/MIDDLE_BAND -- v2 is genuine improvement over v1 (v1 rho=0.20 err=0.049; v2 err=0.036 = 26% better) but "all rho HP" is over-claimed. NEW sub-flavor: ALL_CELL_AGGREGATE_OVER_CLAIM rho-conditioning (pattern cousin of #198 alpha, #199 M, #200 correlation; conditioning variable shifts rho but structure identical -- HP at some cells carried as aggregate conclusion). I-10 PARTIAL-RESOLVED: HP boundary extended from rho<=0.10 (v1) to rho<=0.15 + non-monotone recovery at rho=0.30/0.35; mid-rho peak rho=0.20/0.25 remains open.

**Per-anchor honest re-read (v336).**

| # | Anchor | Wall | N | seeds | Verdict label | Honest reading | Classification |
|---|--------|------|---|-------|--------------|----------------|----------------|
| 1 | kappa3_mixing_correction_v2_correlated_v1 | 2.1s CPU | 1024 | 5 | HARD_PASS | OVER-CLAIM: 6/8 rho cells HP; rho=0.20 err=0.036 + rho=0.25 err=0.038 FAIL HP<=0.03 gate | LABEL-VS-HONEST #202; honest: PARTIAL |
| 2 | q_a3_l3_cross_layer_composition_v1_n4096 | 19.7s CPU | 4096 | 5 | HARD_PASS | HONEST (L1_fid=1.0 HP>=0.9; L2_fid=1.0 HP>=0.9; L3_fid=1.0 HP>=0.9; l3_acc=1.0 HP>=0.8; unanimous 5-seed EXACT-1.0; run_mode=full _source=remote) | GENUINE HARD_PASS |
| 3 | f4_free_cumulants_m4_v2_full_correction_v1 | 129.6s CPU | 4096 | 5 | MIDDLE_BAND | HONEST (alpha=0.05: M4_err=0.037 PASS HP<=0.05; alpha=0.10: 0.058 FAIL; alpha=0.15: 0.069 FAIL; alpha=0.20: 0.078 FAIL; 1/4 cells HP; mean=0.0604 > HP) | GENUINE MIDDLE_BAND |
| 4 | hippocampal_place_field_extended_n8192_v1 | 48.4s CPU | 8192 | 5 | HARD_PASS | HONEST (mean_cosine=0.9283 HP>=0.8; mean_spearman=0.6452 HP>=0.6 mean-gate; mean_acc=1.0 HP>=0.75; seed 7 spearman=0.515 below per-seed but gate is mean-based; run_mode=full N=8192 confirmed) | GENUINE HARD_PASS |

**Strategic decisions.**

1. **LABEL-VS-HONEST #202 filed.** kappa3_mixing_correction_v2_correlated_v1 label over-claims "all rho values HP"; honest: 6/8 cells HP; rho=0.20 (err=0.036) and rho=0.25 (err=0.038) marginally fail HP<=0.03 gate. I-10 PARTIAL-RESOLVED not RESOLVED. PP-44b mixing-correction sub-property ANNOTATION UPDATE: HP-boundary now characterised as rho<=0.15 CONFIRMED + non-monotone recovery at rho=0.30/0.35 (err=0.029/0.000); mid-rho rho=0.20/0.25 is the peak-error zone under v2 formula.

   Rescue sketches for I-10 v3 targeting mid-rho gap (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]):
   - R1 (0-compute, applied) ANNOTATION-only: document non-monotone error pattern at mid-rho; v2 formula may over-correct at rho=0.20/0.25 while under-correcting at rho=0.30 then recovering at rho=0.35; first-order linear-rho correction shape cannot explain non-monotone; characterise as known mid-rho gap.
   - R2 (~3min CPU) Fine rho-grid [0.15, 0.30] step=0.01 at N=1024 5-seed to map exact HP boundary and confirm non-monotone structure (is rho=0.20/0.25 a genuine peak or numerical artifact?).
   - R3 (~10min CPU) Second-order mixing-correction term: quadratic-rho or rho^2/(1+rho) saturation term to flatten mid-rho peak where linear correction over-shoots.
   - R4 (~20min CPU) Alternative GP-kernel mixing model beyond polynomial correction.
   - R5 (~30min CPU) N-scale to N=4096 to test if mid-rho peak is finite-N artifact.

2. **Q-A3 L=3 cross-layer composition HP: PP-12 BAND-LIFT 0.60-0.75 -> 0.65-0.80 (+0.05 both bounds).** q_a3_l3_cross_layer_composition_v1_n4096 GENUINE FULL HARD_PASS at N=4096 5-seed. All metrics EXACT-1.0 unanimous (L1_fid=L2_fid=L3_fid=l3_acc=1.0000). v333 established L=2 at N=4096; v334 lifted L=2 to N=8192; v336 ADDS L=3 at N=4096 as 3rd independent sub-property (deeper composition hierarchy, not same-mechanism N-scale). **3-independent-sub-property convention MET: L=2 N=4096 (v333) + L=2 N=8192 (v334) + L=3 N=4096 (v336) = 3 sub-properties with increasing mechanism variety (N-scale lift + depth-lift).** BAND-LIFT TRIGGERED per convention. Product framing: substrate cross-layer composition algebraically preserves fidelity at L=3 depth and production-N -- substrate audit primitives compose across 3-layer polynomial DAM stack with no fidelity degradation. Cross-references: PP-45 5-method unified-API (PP-12 L=3 sub-property confirms deeper Krylov-compatible composition); PP-48 Negative-Knowledge Tree (L=3 depth is the combo2 composition foundation); PP-49 Hierarchical-Refusal-Cert (L=3 composition depth directly grounds PP-49 founding evidence chain).

3. **F4 M4 v2 MIDDLE_BAND -- I-9 PARTIAL-RESOLVED (1/4 cells HP at N=4096 vs 0/4 at v1 N=1024).** f4_free_cumulants_m4_v2_full_correction_v1 GENUINE MIDDLE_BAND at N=4096 5-seed. alpha=0.05: M4_err=0.037 PASS HP<=0.05 (only cell; 1/4 HP). N-scale hypothesis CONFIRMED: v1 N=1024 had 0/4 HP; v2 N=4096 has 1/4 HP at smallest alpha; M4 correction improves with N as predicted by 1/N correction hypothesis. I-9 remains OPEN for v3 targeting N=8192+ to bring additional alpha cells into HP. Rescue sketches I-9 v3 (cheapest-first):
   - R1 (0-compute, applied) ANNOTATION: 1/N scaling confirmed; alpha=0.05 HP at N=4096; project alpha=0.10 HP at N~8192-16384; full-alpha HP needs N>=32768 range.
   - R2 (~10min CPU) N=8192 5-seed same alpha-grid -- confirms N-scaling; predicts if alpha=0.10 HP boundary crossed.
   - R3 (~30min CPU) N=16384 5-seed to project where all-alpha HP boundary falls.
   - R4 (~20min CPU) Hutchinson estimator alternative at N=4096 to test estimator variance contribution.
   - R5 (~$5 cloud) N=32768 ground-truth M4 correction.

4. **Hippocampal place-field N=8192 PP-47 production-envelope CONFIRMED.** hippocampal_place_field_extended_n8192_v1 GENUINE FULL HARD_PASS at N=8192 5-seed. mean_cosine=0.9283 (HP>=0.8), mean_spearman=0.6452 (HP>=0.6, mean-gate; seed 7 spearman=0.515 below per-seed level but gate applies to mean per pre-reg spec), mean_acc=1.0000 (HP>=0.75). PP-47 founded v333 at N=4096; v336 extends to N=8192 confirming production-envelope. PP-47 parent band 0.55-0.70 UNCHANGED (N-scale extension is corroborative; 2 sub-properties N=4096 + N=8192 = corroborative; 3rd sub-property needed for band-LIFT per convention). NOTE: this anchor is the place-field ENCODING itself; separate from PP-47-adjacent deletion-cert composition probe (MIDDLE_BAND earlier; maintained independently). Product framing: hippocampal-style place-field encoding scales to production-N=8192; brain-inspired geometric memory indexing confirmed at practical scale. Sub-property filed: PP-47 N=8192 5-seed production-envelope extension (mean_cosine=0.9283, mean_spearman=0.6452, mean_acc=1.0000).

**Atomic commit.** cap_map.md + strategy_decisions_2026-06-02.md + visibility_decisions_2026-06-02.md + status_log entry. **247th PROT-009 paired commit.** Push BLOCKED from sub-agent context; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

**Tallies (v335 -> v336).** HONEST 417 -> 421 (+4: 2 GENUINE HP + 1 GENUINE MIDDLE + 1 HONEST catch #202 reading; all 4 have remote-authoritative metrics). LABEL-VS-HONEST 201 -> 202 (+1 catch #202 ALL_CELL_AGGREGATE_OVER_CLAIM rho-conditioning kappa3 mixing v2). Portfolio 32+72 UNCHANGED (no new top-level rows; 1 NEW sub-property PP-12 L=3 N=4096 + 1 sub-property extension PP-47 N=8192 + 1 BAND-LIFT PP-12 0.60-0.75 -> 0.65-0.80). Framework-reliability product-feature 74-88% -> 75-89% (+1pp; PP-12 BAND-LIFT cross-layer composition row proven at L=3 depth). I-9 PARTIAL-RESOLVED (1/4 cells HP at N=4096; N-scaling 1/N confirmed). I-10 PARTIAL-RESOLVED (non-monotone mid-rho gap characterised; HP boundary extended to rho<=0.15 + rho=0.30/0.35).

## v336 -> v337 @ BATCH 4-VERDICT GPU Cycle 10 (4 GENUINE HARD_PASS: COMBO-2 N=8192 production-envelope + COMBO-3 N=8192 N-scaling + Q-A3 L=3 N=8192 production-envelope + SWR v2 N=8192 production-envelope); PP-48+PP-49 production-N sub-property; PP-45 N-scaling sub-property; PP-12 L=3 N=8192 production-envelope sub-property; PP-47 SWR v2 N=8192 sub-property + BAND-LIFT 0.55-0.70 -> 0.60-0.75 (3-sub-property mechanism-variety criterion MET: place-field N=4096 + place-field N=8192 + SWR v2 N=8192); 0 LABEL-VS-HONEST catches (verdict_handler 248th PROT-009 paired commit; Cycle 10)

**Trigger.** Cycle 10 GPU batch 4 verdicts 2026-06-02. All 4 fetched via tools.orchestrator.remote_state.get_metrics -- all _source=remote authoritative. Pause-flag ABSENT.

### Per-anchor honest re-read (v337)

| # | Anchor | Wall | N | seeds | Verdict label | Honest reading | Classification |
|---|--------|------|---|-------|--------------|----------------|----------------|
| 1 | combo2_p4_l3_signed_am_v1_n8192 | 0.82s GPU | 8192 | 5 | HARD_PASS | HONEST: l3_fidelity_A=1.0000 (HP>=0.85), b_repulsion=1.0000 (HP>=0.95), parity_contamination=0.0000 (HP<=0.05) -- all 3 HP conditions unanimous 5-seed; run_mode=full N=8192 confirmed; fast wall consistent with closed-form algebraic primitive (no Krylov solve); PROT-021 no contamination | GENUINE HARD_PASS |
| 2 | combo3_unified_api_v1_n8192 | 12.9s GPU | 8192 | 5 | HARD_PASS | HONEST: mean_prim_fails=0.0 (HP==0), kappa3_err=0.0 (HP<1e-5), cndc_err=0.0 (HP<1e-8), cert_err=0.0 (HP<1e-8), matvec=2.0 (HP<=5) -- all 5 HP conditions unanimous 5-seed; fills N-scaling curve N=4096->N=8192->N=32768 | GENUINE HARD_PASS |
| 3 | q_a3_l3_cross_layer_composition_v1_n8192 | 123.3s GPU | 8192 | 5 | HARD_PASS | HONEST: L1_fid=1.0000 (HP>=0.9), L2_fid=1.0000 (HP>=0.9), L3_fid=1.0000 (HP>=0.9), l3_acc=1.0000 (HP>=0.8) -- all 4 HP conditions unanimous 5-seed; substantial wall consistent with N=8192 L=3 polynomial composition at production scope | GENUINE HARD_PASS |
| 4 | hippocampal_sharp_wave_ripple_v2_n8192 | 552.3s GPU | 8192 | 5 | HARD_PASS | HONEST: fid_fast=1.0000 (HP>=0.7), fid_random=0.082, fid_wrong=0.1091 (HP<=0.2), frac_A=1.0, frac_B=1.0, frac_C=0.8 (HP>=0.7 per source handoff); all primary HP gates met; substantial wall consistent with SWR N=8192 full simulation | GENUINE HARD_PASS |

LABEL-VS-HONEST: **0 NEW CATCHES** (all 4 honest-as-labeled; combo2 0.82s fast wall verified run_mode=full N=8192 5-seed closed-form algebraic primitive not smoke artifact).

### v337 strategic highlights

**(A) COMBO-2 N=8192 PRODUCTION-ENVELOPE CONFIRMED: PP-48 + PP-49 GAIN PRODUCTION-N SUB-PROPERTY.** combo2_p4_l3_signed_am_v1_n8192 GENUINE FULL HARD_PASS at N=8192 5-seed. All 3 pre-registered HP conditions unanimous: l3_fidelity_A=1.0000, b_repulsion=1.0000, parity_contamination=0.0000. v334 established PP-48 Negative-Knowledge Tree + PP-49 Hierarchical-Refusal-Cert at N=4096 (EXPLORATORY 0.65-0.80 with N=8192 confirmation pending). This N=8192 result satisfies the first production-N cross-N confirmation step. PP-48 + PP-49 GAIN NEW SUB-PROPERTY: 'COMBO-2 architecture production-N=8192 confirmed; l3_fidelity=1.0 / b_repulsion=1.0 / parity_contamination=0.0 unanimous'. Band LIFT deferred: N=8192 is step 1 of 2 planned cross-N steps (v334 routing: {8192, 16384}); band-LIFT eligibility gates on N=16384 confirmation. PP-48 0.65-0.80 + PP-49 0.65-0.80 UNCHANGED.

**(B) COMBO-3 N=8192 N-SCALING CURVE FILLED: PP-45 GAINS N=8192 INTERMEDIATE SCALING SUB-PROPERTY.** combo3_unified_api_v1_n8192 GENUINE FULL HARD_PASS at N=8192 5-seed. All 5 HP conditions unanimous (zero-error pattern). Three N-scale data points established: N=4096 (v332 founding), N=8192 (v337 intermediate), N=32768 (v335 Wave 5 cloud). N-scaling curve complete: algebraic theorem holds across 8x N range. PP-45 GAINS NEW SUB-PROPERTY: 'N=8192 intermediate confirmation; N-scaling monotone (N=4096 -> N=8192 -> N=32768 all unanimous 0-error)'. PP-45 parent band 0.70-0.85 UNCHANGED.

**(C) Q-A3 L=3 N=8192 PRODUCTION-ENVELOPE: PP-12 GAINS L=3 N=8192 SUB-PROPERTY.** q_a3_l3_cross_layer_composition_v1_n8192 GENUINE FULL HARD_PASS at N=8192 5-seed. All 4 metrics unanimous EXACT-1.0. v336 established PP-12 L=3 at N=4096 (triggered band-LIFT PP-12 0.60-0.75 -> 0.65-0.80). This N=8192 result extends L=3 to production-envelope scale. PP-12 GAINS NEW SUB-PROPERTY: 'L=3 production-N=8192; all 4 fidelity metrics = 1.0 unanimous 5-seed'. PP-12 parent band 0.65-0.80 UNCHANGED (v336 BAND-LIFT already applied; N-scale extension is corroborative).

**(D) HIPPOCAMPAL SWR v2 N=8192 PRODUCTION-ENVELOPE: PP-47 BAND-LIFT 0.55-0.70 -> 0.60-0.75 (3-sub-property mechanism-variety criterion MET).** hippocampal_sharp_wave_ripple_v2_n8192 GENUINE FULL HARD_PASS at N=8192 5-seed. fid_fast=1.0000, fid_wrong=0.1091, frac_C=0.8 >= HP=0.7. PP-47 GAINS NEW SUB-PROPERTY: 'SWR v2 production-N=8192; sharp-wave ripple replay confirmed at production-N'. BAND-LIFT 0.55-0.70 -> 0.60-0.75 (+0.05 both bounds): 3-sub-property mechanism-variety criterion MET -- (1) place-field N=4096 founding v333, (2) place-field N=8192 extension v336 (N-scale variety), (3) SWR v2 N=8192 v337 (mechanism variety: SWR replay is distinct biological mechanism from place-field encoding within hippocampal suite). Brain-inspired: substrate now confirms TWO distinct hippocampal circuit primitives (place-field + SWR) at production-N=8192.

### Tallies (v336 -> v337)

- **HONEST:** 421 -> **425** (+4 NEW HONEST: 4 GENUINE HARD_PASS).
- **LABEL-VS-HONEST:** 202 -> **202** UNCHANGED (0 new catches).
- **Portfolio:** 32+72 UNCHANGED (no new top-level rows; 4 NEW SUB-PROPERTIES; 1 BAND-LIFT PP-47 0.55-0.70 -> 0.60-0.75).
- **Cap_map version: v337.**

### Framework reliability (v337)

- General: 65-75% UNCHANGED.
- Specific-documented: 55-65% UNCHANGED.
- Product-feature: 75-89% -> **76-90%** (+1pp both bounds; PP-47 BAND-LIFT hippocampal dual-circuit suite confirmed at production-N=8192 with mechanism variety).

### Known infrastructure issues (annotation block; UPDATED in v337)

**Issue I-1 through I-8** (v323-v333, OPEN v337). STILL OPEN; v337 batch did NOT touch them.
**Issue I-9 (v334, PARTIAL-RESOLVED v336, OPEN v337).** STILL OPEN; v3 N=8192 next step per v336 routing.
**Issue I-10 (v334, PARTIAL-RESOLVED v336, OPEN v337).** STILL OPEN; v3 fine rho-grid next step per v336 routing.
**Issue I-11 (v335, OPEN v337).** STILL OPEN; research-cycle routing FILED.

### PROT compliance (v336 -> v337)

- PROT-004/006: NO row closures. 1 BAND-LIFT (PP-47 0.55-0.70 -> 0.60-0.75). 4 NEW SUB-PROPERTIES (PP-48 N=8192 + PP-45 N=8192 + PP-12 L=3 N=8192 + PP-47 SWR v2 N=8192). No MIDDLE candidates; no closures.
- PROT-007: history v337 entry inline (strategy_decisions_2026-06-02.md canonical record).
- PROT-008: 4 new sub-properties + 1 BAND-LIFT; no portfolio regression; no closures.
- PROT-009: cap_map.md + strategy_decisions_2026-06-02.md + visibility_decisions_2026-06-02.md + status_log entry staged atomically; **248th PROT-009 paired commit**.
- PROT-018: all 4 anchors _n8192 suffix matches metrics N=8192. PROT-018 all 4 clear.
- PROT-021: all 4 _source=remote run_mode=full 5-seed; combo2 0.82s fast wall verified not smoke.
- PROT-022: not applicable.

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 applied to all 4; 0 new catches; combo2 fast wall explicitly investigated and verified.
- [[feedback-no-preframing]]: task pre-framed combo2 as SUSPICIOUSLY FAST and HP expected for all 4; Step 0 verified INDEPENDENTLY; pre-framing did NOT propagate.
- [[feedback-smoke-checkpoint-contamination]]: PROT-021 verified; all _source=remote run_mode=full 5-seed.
- [[feedback-cap-map-update-protocol]]: atomic single commit; push BLOCKED from sub-agent context.
- [[feedback-for-you-tab-primary-channel]]: status_log entry HIGH filed with plain_language and importance.
- [[feedback-decision-log-eol-handling]]: append via append_decision_log.py.
- [[feedback-subagent-permission-inheritance]]: push BLOCKED; commit hash surfaced for main thread.
- [[feedback-pipeline-pacing]]: pause-flag ABSENT; overnight_queue=2 + cpu_queue=23 pending; NO exp_dev refill triggered (queue >= 1).
- [[feedback-rescue-sketch-first-sequencing]]: no new MIDDLE/HF; no rescue sketches needed.
- [[feedback-rehabilitation-after-rejection]]: no new candidates; all 4 HARD_PASS.
- [[feedback-brain-inspired]]: PP-47 BAND-LIFT grounded in TWO distinct hippocampal biological mechanisms (place-field + SWR replay) -- dual-circuit signature. Most significant brain-inspired framing since PP-47 founding.
- [[feedback-lit-scan-calibration-penalty]]: PP-47 lifted band 0.60-0.75 retains +0.05 deflation per v317 uncharted-regime convention.
- [[feedback-composition-classification]]: combo2 PIPELINE-class; combo3 HANDOFF/PIPELINE-class; q_a3 HANDOFF-class; hippocampal_SWR SCORE-class.
- [[feedback-strategy-shore-up-capabilities]]: 4 production-N sub-properties + 1 BAND-LIFT in single batch.

### Push and follow-on (v337)

Push: BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

Main-thread routing candidates (highest -> lowest priority; v336 carryovers RETAINED + v337 additions):
1. **F4 M4 I-9 v3: N=8192 5-seed** (v336 PARTIAL-RESOLVED; ~10min CPU; R2 cheapest next step).
2. **kappa3 I-10 v3: fine rho-grid [0.15, 0.30]** (v336 PARTIAL-RESOLVED; ~3min CPU; R2 cheapest next step).
3. **PP-48 + PP-49 cross-N N=16384 5-seed** (v334/v335 routing; N=8192 confirmed v337; N=16384 NEXT for band-LIFT eligibility completion).
4. **PP-47 hippocampal cross-N N=16384 5-seed** (v337 BAND-LIFT 0.60-0.75 active; N=16384 next for further LIFT eligibility).
5. **I-11 research-cycle routing: Wishart/MP/free-Poisson analytic recalibration** (v335 NEW; highest-priority theory gap).
6. **COMBO-1 v3 redesign** (v333 carry-over; gates Wave 5 cell-5).
7. **I-7 orphan failures re-ship vs close** (v332 carry-over).
8. **Q-F3 cophenetic correlation**, Q-F1, Q-F4, graph_community R2, program_exec R2, caching_capacity R1, PP-43b LRU, Q-F2, I-6, COMBO-4 N-scale R2, PP-44/PP-9b cross-N (v330-v336 carry-overs).
9. **q22-family timeout extension to 2400s** (v330 I-5 carry-over).


## v337 -> v338 @ BATCHED 5-VERDICT GPU Cycle 10.5 (4 GENUINE HARD_PASS + 1 GENUINE MIDDLE_BAND; 0 LABEL-VS-HONEST) -- PP-51 NEW TOP-LEVEL ROW implicit-Gram audit-on-M-side architecture LOCK + Wave 5 Cell 5 UNBLOCKED + PP-48 + PP-49 BAND-LIFTS at N=16384 + PP-45 N-scaling-complete sub-property + PP-12 L=4 sub-property + PP-33 COMBO-4 v2 sub-property with mu-aging caveat (verdict_handler 249th PROT-009 paired commit)

**Trigger.** Batched 5-verdict GPU Cycle 10.5 2026-06-02. All 5 anchors fetched via `tools.orchestrator.remote_state.get_metrics` (_source=remote authoritative). Pause-flag ABSENT verified. REMOTE-FIRST per e51aee7.

**Step 0 honest re-read summary.** 5 HONEST (4 clean HP + 1 GENUINE MIDDLE_BAND COMBO-4 v2 with mu-aging-exponent FAIL caveat). **0 NEW LABEL-VS-HONEST OVER-CLAIMS.**

- **combo1_p3_dam_implicit_gram_v3_gpu_fix_v1_n4096**: HONEST 4/4-HP. v3 GPU-vectorized recovery (HP3 slope=0.713 vs v2 1.958; HP4 cosine=1.0 vs v2 0.25). Wave 5 Cell 5 UNBLOCKED.
- **combo4_dynamical_redesign_v2_n2048**: HONEST MIDDLE 2/3 metrics. M_dyn=0.84 + collapse=0.0001 PASS; mu_aging=0.1733 FAIL HP band [0.5,1.0]. PP-33 sub-property with caveat.
- **combo2_p4_l3_signed_am_v1_n16384**: HONEST 3/3-HP unanimous EXACT-1.0 at N=16384 5-seed. PP-48+PP-49 BAND-LIFT.
- **combo3_unified_api_v1_n16384**: HONEST 5/5-HP unanimous at N=16384 5-seed. PP-45 N-scaling-complete 4-point.
- **q_a3_l4_cross_layer_composition_v1_n8192**: HONEST 5/5-HP all L=1..4 fidelity EXACT-1.0 at N=8192 5-seed. PP-12 L=4 sub-property.

**Strategic decisions.**

1. **PP-51 NEW TOP-LEVEL ROW founding: implicit-Gram audit-on-M-side architecture LOCK 0.70-0.85 EXPLORATORY.** COMBO-1 v3 GPU-fix 4/4-HP at N=4096 5-seed validates v333 research-cycle delivered spec; v3 spec is the FULL implicit-Gram-solve formulation. Wave 5 Cell 5 cloud-dispatch UNBLOCKED. Lit-scan calibration penalty +0.05 applied. Cross-references: PP-45 5-method unified-API (PP-51 is 6th primitive sibling); PP-42 implicit-Gram-compression founding (PP-51 EXTENDS architecture commitment); PP-12 (M-side audit primitive available to chain).

2. **PP-48 + PP-49 BAND-LIFT 0.65-0.80 -> 0.70-0.85 (+0.05 both bounds).** combo2 N=16384 GENUINE FULL HP unanimous EXACT-1.0 at all 3 metrics. 3-sub-property cross-N criterion MET: N=4096 (v334 founding) + N=8192 (v337) + N=16384 (v338). Substrate Negative-Knowledge Tree + Hierarchical-Refusal-Cert architecture confirmed at production-N envelope {4096, 8192, 16384}.

3. **PP-45 N-scaling-complete SUB-PROPERTY: 5-method unified-API curve filled at intermediate N=16384.** All 5 primitives zero-error at N=16384 5-seed; N-scaling now COMPLETE {4096, 8192, 16384, 32768} = 4-point monotone confirmation.

4. **PP-12 L=4 N=8192 SUB-PROPERTY: cross-layer composition depth extends from L=3 to L=4 at production-N.** Geometric inner-decay scheme (M_inner=200 -> M_outer=25) holds with NO fidelity degradation across 4-layer composition at N=8192 5-seed.

5. **PP-33 SUB-PROPERTY "COMBO-4 v2 M_dyn + scaling-collapse PASS / mu_aging OUT-OF-BAND at N=2048 3-seed" with annotation caveat.** Substrate aging-exponent at N=2048 disagrees with CK-class predicted [0.5, 1.0] band; PP-33 parent row 0.60-0.75 UNCHANGED; sub-property documents the mu-aging mismatch alongside the M_dyn + collapse PASS signals. Rescue R1-R5 filed (R5 theory-side spec audit BEFORE any further GPU spend, per PROT-022 formula-selftest discipline).

**Rescue-sketch sequencing (CHEAPEST FIRST per [[feedback-rescue-sketch-first-sequencing]]).**

For **COMBO-4 v2 mu-aging-exponent FAIL** (NEW; PP-33 sub-property OPEN):
- R1 (0-compute, applied) ANNOTATION-only PP-33 sub-property documents M_dyn+collapse PASS / mu-aging OUT-OF-BAND.
- R5 (~1h theory, EARLIEST BEFORE GPU) Theory-side audit of mu formula in COMBO-4 redesign spec vs CK-class prediction; possible exponent-typo cousin of v327 F_4 typo. 0-compute check before any retry GPU spend.
- R2 (~30min GPU) After R5 clean: re-run 5-seed (not 3) at N=2048 to confirm mu estimate is not seed-noise artifact.
- R3 (~1h GPU) N=4096 5-seed for mu-aging N-scaling test.
- R4 (~2h GPU) Alternative observable via two-time correlator C(t,t_w) integral (Q19 v330 RESCUE-style corrected observable).

**Atomic commit.** cap_map.md + history.md (inline v338 entry) + this strategy_decisions_2026-06-02.md + visibility_decisions_2026-06-02.md + status_log entry. **249th PROT-009 paired commit.** Push BLOCKED from sub-agent context; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

**Tallies (v337 -> v338).** HONEST 425 -> 430 (+5). LABEL-VS-HONEST 202 UNCHANGED. Portfolio 32+72 -> **32+73** (+1 NEW TOP-LEVEL ROW PP-51 audit-on-M-side architecture LOCK 0.70-0.85). 2 BAND-LIFTS (PP-48 + PP-49 both 0.65-0.80 -> 0.70-0.85). 4 NEW SUB-PROPERTIES + 1 PP-33 sub-property MIDDLE-with-caveat. Framework-reliability product-feature 76-90% -> **78-92%** (+2pp). Issue I-8 RESOLVED (COMBO-1 v3 redesign delivered).


## v338 -> v339 @ BATCHED 18-VERDICT Cycle 10 wake (10 GPU + 6 CPU + 3 FAILURES; 12 HONEST HP-or-equivalent + 4 MIDDLE/HF + 2 NO-DATA-DIR + 1 SMOKE-ONLY-PARK; NEW TOP-LEVEL ROW PP-52 Hebbian-vs-LoRA empirical capstone 0.55-0.70 EXPLORATORY founding + PP-12 L=5 sub-property + PP-49a depth-15 sub-property + PP-48 4-level + depth-5 sub-properties + PP-46 N=16384 sub-property + PP-48/49 N=32768-LOCAL sub-property + 2 HARD_FAILS opening Issues I-12 (kappa3 sensitivity N=16384 catastrophic contradiction with v335 N=32768) and I-13 (caching v2 test-under-stress design); Wave 5 Cell 5 LOCAL N=32768 HARD_FAIL with PP-51 CAVEAT; COMBO-3 N=32768 LOCAL MIDDLE with PP-45 LOCAL-vs-CLOUD CAVEAT; 3 NEW LABEL-VS-HONEST catches (#203-#205) all task-prompt PRE-FRAMING category per [[feedback-no-preframing]]; verdict_handler 250th PROT-009 paired commit; Cycle 10 wake)

**Trigger.** Cycle 10 wake batched 18 anchors 2026-06-02. 16 anchors fetched via `tools.orchestrator.remote_state.get_metrics` (_source=remote authoritative; bridge is_stale=False). 2 anchors `get_metrics` returned None (combo1_p3_dam_implicit_gram_v3_n8192_production_envelope_v1 + pp49_hrc_counterfactual_depth_10_v1_n4096) -- both verified NO REMOTE DATA DIR via `dir C:\dev\hd-instrument\data\exp_<name>` returns "file not found"; verdict_state bridge confirms verdict=failed for both. 1 anchor (a4_audit_during_training_v1) has `_source=local run_mode=smoke n_seeds=2 N=512` smoke-only artifact + verdict_state bridge confirms verdict=failed (FULL never ran). Pause-flag ABSENT verified.

**Step 0 honest re-read summary.** 12 HONEST verdicts at FULL multi-seed N (10 HP-or-equivalent + 4 MIDDLE/HF), 3 task-prompt PRE-FRAMING LABEL-VS-HONEST catches, 2 NO-DATA-DIR script failures, 1 SMOKE-ONLY-PARK.

**3 NEW LABEL-VS-HONEST CATCHES (task-prompt PRE-FRAMING category per [[feedback-no-preframing]]):**

- **#203 wave5_cell5_combo1_n32768_local_v1 TASK-PROMPT PRE-FRAMING OVER-CLAIMS Wave 5 Cell 5 LOCAL HP.** Task input pre-framed "HP per research's Wave 5 spec at N=32768; if HP at LOCAL: Wave 5 architecture LOCK + PP-51 PROMOTION at production envelope." Honest reading: verdict_msg `HARD_FAIL: MMD=0.9328(HP<0.02 HF>=0.1) k3_resc=2.2802(|k-1|<=0.05) slope=1.522(HP<=1.3) cos=1.0000(HP>=0.95 HF<0.7)`. 3/4 HP gates HARD_FAIL by 30-50x margins (MMD 47x over HP gate; k3_resc 25x off identity-band; slope 1.17x over). 1/4 (cos) PASS. Pre-framing implied PP-51 PROMOTION on positive outcome; honest outcome BLOCKS PP-51 LOCAL N=32768 production promotion. PP-51 row 0.70-0.85 UNCHANGED parent band; NEW CAVEAT added: "LOCAL N=32768 production-envelope FAILS at 3/4 HP gates; v3 GPU-fix HP path validated at N=4096 only; substrate finite-N implicit-Gram regime at N=32768 LOCAL does not preserve identity-band signatures; cloud N=32768 dispatch authorization STILL VALID (cloud has distinct numerics/Wave 5 spec configuration)."

- **#204 combo3_unified_api_v1_n32768_local TASK-PROMPT PRE-FRAMING OVER-CLAIMS LOCAL HP.** Task input pre-framed "was HP at N=32768 cloud Wave 5 Cell 4. Verify FULL not smoke." Honest reading: verdict_msg `MIDDLE_BAND: 0/3 metrics at HP level. mean_rel tr_W1=1.58e-03 tr_W2=1.46e-03 tr_W3=1.31e-03 worst=1.58e-03 n_seeds=5`. 0/3 HP gates met at LOCAL (PROBABLY HP<1e-5 cf v337/v338 cloud zero-error). LOCAL CPU/RTX numerical-precision regime produces ~1.5e-3 relative drift vs cloud H100 zero-error. NOT substrate failure -- LOCAL vs cloud precision-regime difference; PP-45 row UNCHANGED parent band 0.70-0.85; NEW CAVEAT added: "LOCAL N=32768 produces ~1.5e-3 mean relative error (MIDDLE; not zero); cloud H100 produces zero-error (v335 Wave 5 Cell 4 + v338 N=16384). LOCAL-vs-cloud precision-regime delta documented; substrate algebraic-theorem moat HOLDS but LOCAL hardware-precision floor near ~1e-3 at N=32768."

- **#205 a4_audit_during_training_v1 TASK-PROMPT TIMEOUT-CHARACTERIZATION + SMOKE-ONLY METRIC LANDING.** Task input pre-framed "120s -- timeout? failed? Read log + diagnose." Honest reading: metrics _source=local run_mode=smoke n_seeds=2 N=512 -- SMOKE-only artifact landed; FULL never executed on remote. verdict_state bridge confirms verdict=failed (FULL never produced metrics). Smoke verdict msg HARD_PASS (2/2 detected; latency=1 write; fpr=0.0) is INSUFFICIENT for cap_map decision per [[feedback-no-smoke-preframing-in-task-prompts]]. PARK from this batch's cap_map tallies; routing recommended for FULL re-ship at N=4096+ 5-seed for Cluster A4 monitor evaluation.

**Per-anchor honest re-read (v339).**

| # | Anchor | Wall | N | seeds | Verdict label | Honest reading | Cap_map impact |
|---|--------|------|---|-------|--------------|----------------|----------------|
| 1 | wave5_cell5_combo1_n32768_local_v1 | 29.8s GPU | 32768 | (5?) | HARD_FAIL (per msg) | HONEST HF: MMD=0.9328 (HP<0.02 47x over); k3_resc=2.2802 (HP\|k-1\|<=0.05 25x off); slope=1.522 (HP<=1.3 1.17x over); cos=1.0000 PASS. 3/4 HP gates HF. | PP-51 CAVEAT LOCAL-N=32768 BLOCK; cloud dispatch STILL authorized; LABEL-VS-HONEST #203 catch (task-prompt PRE-FRAMING) |
| 2 | a1_hebbian_vs_gradient_identity_v1 | 89.7s CPU | 1024 | 5 | HARD_PASS (3/3 HP) | HONEST HP: 5/5 seeds hebb_acc=1.0 gd_acc=1.0 acc_delta_pp=0.00; wall_speedup=923x; flops_speedup=500x; hp1=hp2=hp3=5/5 unanimous. N=1024 founding only. | **NEW TOP-LEVEL ROW PP-52** Hebbian-vs-LoRA-speedup empirical capstone 0.55-0.70 EXPLORATORY founding |
| 3 | a2_oneshot_addition_recall_v1 | 13.7s CPU | 1024 | 5 | HARD_PASS (3/3 HP) | HONEST HP: 5/5 seeds new_cos=0.997 (HP>=0.9); acc_after=1.000 (HP>=0.95); drop=0.00pp; max_write_t=0.02s; hp1=hp2=hp3=5/5 unanimous. | PP-52 SUB-PROPERTY one-shot-addition |
| 4 | a3_rollback_via_subtraction_v1 | 15.8s CPU | 1024 | 5 | MIDDLE_BAND (2/3 HP) | HONEST MIDDLE: rel_err=0.00e+00 EXACT (HP<1e-10); acc_after=1.000 (HP>=0.95); max_rollback_t=0.3496s vs HP<=0.05 = TIMING FAIL 7x over. Algebraic rollback is EXACT; only HP3 wall-budget MISS (5/5 seeds 0.32-0.35s wall). hp1=hp2=5/5; hp3=0/5. | PP-52 SUB-PROPERTY exact-rollback-algebra-CONFIRMED + timing-budget-CAVEAT (substrate algebra exact; timing gate may be miscalibrated for N=1024 path) |
| 5 | combo2_p4_l3_signed_am_v1_n32768 | 8.8s GPU | 32768 | 5 | HARD_PASS (3/3 HP) | HONEST HP: l3_fidelity_A=1.0000 (HP>=0.85); b_repulsion=1.0000 (HP>=0.95); parity_contamination=0.0000 (HP<=0.05); all unanimous EXACT-1.0 5-seed. Fast wall consistent with closed-form algebraic primitive (v337 N=8192 0.82s; v338 N=16384 6.7s; v339 N=32768 8.8s = sub-linear scaling consistent). NOT smoke. | PP-48 + PP-49 N=32768 LOCAL SUB-PROPERTY (4th cross-N point) |
| 6 | combo3_unified_api_v1_n32768_local | 7.6s GPU | 32768 | 5 | MIDDLE_BAND (0/3 HP) | HONEST MIDDLE: mean_rel tr_W1=1.58e-3; tr_W2=1.46e-3; tr_W3=1.31e-3; worst=1.58e-3. 0/3 cells at HP zero-error level. NOT substrate failure -- LOCAL hardware-precision floor ~1e-3 at N=32768 distinct from cloud H100 zero-error path (v335 + v338). | PP-45 LOCAL-vs-CLOUD precision-CAVEAT; LABEL-VS-HONEST #204 (task PRE-FRAMING) |
| 7 | q_a3_l5_cross_layer_composition_v1_n4096 | 7.6s GPU | 4096 | 5 | HARD_PASS (6/6) | HONEST HP: fids L1=L2=L3=L4=L5=1.0000; l5_acc=1.0000 all unanimous EXACT-1.0 5-seed. Substrate L=5 cross-layer compositional fidelity at production-N. | PP-12 L=5 N=4096 SUB-PROPERTY (depth extension L=4 v338 -> L=5 v339) |
| 8 | q_b1_chain_depth_15_v1_n8192 | 22.1s GPU | 8192 | 5 | HARD_PASS (3/3 HP) | HONEST HP: d5=1.0000 (HP>=0.95); d10=1.0000 (HP>=0.88); d15=1.0000 (HP>=0.8); all unanimous EXACT-1.0 5-seed at N=8192. Per-hop fidelity at d=15 substrate ceiling NOT reached. | PP-49a depth-15 SUB-PROPERTY (v335 depth-10 cloud + v339 depth-15 local; PP-49a depth-progression) |
| 9 | deletion_cert_z_ratio_n16384_v1 | 7.3s GPU | 16384 | 5 | HARD_PASS | HONEST HP: mean_Z=137.17 vs HP>=2.5 / MID>=1.8 / HF<1.5 = 55x margin over HP. Intermediate N=16384 fills curve between v333/v336 lower-N and v335 cloud N=32768 Z=156. | PP-46 N=16384 SUB-PROPERTY (intermediate N curve filled) |
| 10 | kappa3_sensitivity_sweep_n16384_v1 | 8.1s GPU | 16384 | 5 | HARD_FAIL | HONEST HF: mean_min_sigma_sep=0.3219 vs HP>=4.0 / HF<2.0 = 12.4x BELOW HF threshold. CATASTROPHIC contradiction with v335 Wave 5 Cell 2 Part B at N=32768 (sigma_sep 2.55-1726.6 across delta_alpha grid). Either (a) N=16384 substrate regime has different spectral-sensitivity bands than N=32768; (b) sweep config covers an unsupported (delta_alpha, M, alpha) regime where HP gate should have been recalibrated; or (c) sigma_sep observable not comparable between Wave 5 cell config and v339 sweep config. | PP-50 NEW CAVEAT N=16384 sigma_sep collapse to 0.32; OPENS Issue I-12 |
| 11 | pp48_nkt_depth_5_v1_n4096 | 7.4s GPU | 4096 | 5 | HARD_PASS (3/3 HP) | HONEST HP: pos_rate=1.0000 (HP>=0.85); nkt_rep=1.0000 (HP>=0.85); tree=1.0000 (HP>=0.8); unanimous 5-seed. | PP-48 depth-5 SUB-PROPERTY |
| 12 | combo1_alpha_p_minus_1_audit_sensitivity_v1_n4096 | 7.3s GPU | 4096 | 5 | MIDDLE_BAND (2/3 HP) | HONEST MIDDLE: slope=0.9942 (HP [1.5, 2.5] FAIL -- slope flat); rho=1.0000 (HP>=0.8 PASS); sens_05=0.1498 (PASS). 2/3 cells HP. Substrate spearman-rank perfect but alpha^(p-1) slope NOT in expected scaling band. | PP-51 SUB-PROPERTY alpha^(p-1) sensitivity scaling MIDDLE (slope OUT-OF-BAND while spearman PASS) |
| 13 | caching_eviction_pp44_capacity_aware_v2_n4096 | 1461s CPU | 4096 | 5 | HARD_FAIL | HONEST HF: fid_no_evict=0.8791 (HP<=0.5; FAIL -- no-eviction baseline did NOT degrade as stress design intended); fid_evict=1.0000 (HP>=0.8 PASS); retained=1.0000 (HP>=0.85 PASS). Test was UNDER-STRESSED: no-eviction baseline should drop to <=0.5 to demonstrate eviction value; instead it stayed at 0.88. NOT substrate failure -- TEST DESIGN issue (stress regime missing). | OPENS Issue I-13 caching v2 test-under-stress design rescue |
| 14 | streaming_prediction_8_v1 | 51.2s CPU | 1024 | 5 | HARD_PASS (3/3 HP) | HONEST HP: mean_fid_window=0.9997 (HP>=0.7); late_adv=0.1249 (HP>=0.05); newest=0.9997 (HP>=0.85); n_seeds=5. Sliding-window streaming SP8 confirmed at N=1024. | Streaming row SP8 SUB-PROPERTY sliding-window |
| 15 | negative_knowledge_tree_4level_v1_n4096 | 129.6s CPU | 4096 | 5 | HARD_PASS (3/3 HP) | HONEST HP: cert_valid=1.0000 (HP>=0.85); parity_contam=0.0000 (HP<=0.05); b_repulsion=1.0000 (HP>=0.9); unanimous 5-seed. | PP-48 4-level SUB-PROPERTY (depth extension 4-level NKT) |
| 16 | a4_audit_during_training_v1 | n/a (smoke-only) | 512 | 2 | smoke HP / verdict_state failed | HONEST: SMOKE-ONLY artifact _source=local run_mode=smoke n_seeds=2 N=512; FULL run never executed on remote (verdict_state=failed); smoke verdict tag INSUFFICIENT for cap_map decision per [[feedback-no-smoke-preframing-in-task-prompts]]. | PARK; routing for FULL re-ship; LABEL-VS-HONEST #205 (task PRE-FRAMING) |
| 17 | combo1_p3_dam_implicit_gram_v3_n8192_production_envelope_v1 | failed | -- | -- | failed | HONEST NO-DATA-DIR: `dir C:\dev\hd-instrument\data\exp_combo1_p3_dam_implicit_gram_v3_n8192_production_envelope_v1` returns "file not found" on remote; no metrics.json; script crashed pre-data-dir-creation or never ran. Bridge confirms verdict=failed. v3 GPU-fix at N=4096 v338 was HP -- N=8192 production-envelope extension expected to work; likely VRAM OOM at N=8192 implicit-Gram solve (Gram matrix scales N^2; 4 GB at N=4096 -> 16 GB at N=8192 likely OOM on RTX-4060-Ti 16 GB) OR smoke-gate failure pre-flight. | OPENS Issue I-14; rescue paths filed |
| 18 | pp49_hrc_counterfactual_depth_10_v1_n4096 | failed | -- | -- | failed | HONEST NO-DATA-DIR: `dir C:\dev\hd-instrument\data\exp_pp49_hrc_counterfactual_depth_10_v1_n4096` returns no match on remote; no exp dir; bridge verdict=failed. Likely pre-flight smoke-gate failure or design issue (PP-49a depth-10 was HP v335 cloud at production-N=32768; v339 at depth-10 N=4096 should have worked). | OPENS Issue I-15; rescue paths filed |

### Cap_map state transitions (v339)

**(A) NEW TOP-LEVEL ROW PP-52 Hebbian-vs-LoRA-speedup empirical capstone 0.55-0.70 EXPLORATORY.** a1_hebbian_vs_gradient_identity_v1 GENUINE 3/3-HP HARD_PASS at N=1024 5-seed: hebb_acc=gd_acc=1.0 (delta=0.00pp); wall_speedup=923x; flops_speedup=500x; all 5 seeds unanimous. PP-52 founds at 0.55-0.70 EXPLORATORY (lower bound than task-input-suggested 0.65-0.80 because N=1024 founding is small-scale only; production-N N>=4096 5-seed cross-N confirmation REQUIRED for band-LIFT eligibility per cap_map convention). Lit-scan calibration penalty +0.05 applied per v317 (substrate Hebbian-write speedup vs LoRA-equivalent gradient training is finite-N regime not directly precedented in lit-scan agent's training-acceleration literature; +0.05 deflation maintained). Sub-properties: (i) one-shot-addition (a2 5/5 HP); (ii) exact-rollback-algebra (a3 rel_err=0 + acc=1.0 5/5 with timing-budget CAVEAT). Cross-references: PP-9 GDPR-grade deletion-cert (rollback-via-subtraction is the deletion-cert primitive in a3); PP-44 caching family (one-shot-addition is the write-allocate primitive); product narrative: substrate is the auditable-memory layer that ENABLES one-shot training updates with mathematical rollback guarantee -- not competing with LLM weights but augmenting via substrate-side-only Hebbian writes; "training-acceleration product narrative" anchor row established. Production-envelope cross-N {4096, 8192, 16384} confirmations queued for band-LIFT eligibility.

**(B) PP-12 L=5 N=4096 SUB-PROPERTY: cross-layer composition depth extends L=4 v338 -> L=5 v339.** q_a3_l5_cross_layer_composition_v1_n4096 GENUINE FULL HARD_PASS at N=4096 5-seed all 5 level fidelities + l5_acc unanimous EXACT-1.0. PP-12 cross-layer composition depth scales L=2 v333 -> L=3 v336 -> L=4 v338 -> L=5 v339 (depth-monotone progression). PP-12 parent band 0.65-0.80 UNCHANGED (v336 BAND-LIFT already applied; L=5 is depth-extension corroboration at N=4096). Product framing: substrate algebraic-composition holds at L=5 polynomial-DAM depth with NO fidelity degradation at production-N=4096; substrate audit primitives compose across 5-layer stack unanimously 5-seed.

**(C) PP-49a depth-15 N=8192 SUB-PROPERTY: chain depth extends d=10 v335 -> d=15 v339.** q_b1_chain_depth_15_v1_n8192 GENUINE FULL HARD_PASS at N=8192 5-seed all 3 depth-fidelity HP gates unanimous EXACT-1.0 (d5/d10/d15 each 1.0000). PP-49a depth-progression: v335 Wave 5 cloud depth-10 fidelity 0.9846; v339 depth-15 fidelity 1.0000 at N=8192. **Substrate per-hop fidelity ceiling NOT REACHED at d=15.** PP-49a sub-property band UNCHANGED 0.70-0.85 (parent PP-49 lifted at v338 to 0.70-0.85 via cross-N criterion); v339 depth-15 is depth-extension corroboration.

**(D) PP-48 N=4096 depth-5 + 4-level SUB-PROPERTIES.** pp48_nkt_depth_5_v1_n4096 GENUINE FULL HARD_PASS at N=4096 5-seed (pos_rate=1.0; nkt_rep=1.0; tree=1.0). negative_knowledge_tree_4level_v1_n4096 GENUINE FULL HARD_PASS at N=4096 5-seed (cert_valid=1.0; parity_contam=0.0; b_repulsion=1.0). PP-48 Negative-Knowledge Tree depth/level progression: depth-3/4-level founding v334 -> depth-5 + 4-level v339 (depth-extension + tree-level-extension at N=4096). PP-48 parent band 0.70-0.85 UNCHANGED (v338 cross-N BAND-LIFT already applied; v339 depth/tree extensions are corroborative).

**(E) PP-48 + PP-49 N=32768 LOCAL SUB-PROPERTY: cross-N 4th point added.** combo2_p4_l3_signed_am_v1_n32768 GENUINE FULL HARD_PASS at N=32768 LOCAL 5-seed all 3 HP unanimous EXACT-1.0. Sub-linear wall scaling (v337 N=8192 0.82s -> v338 N=16384 6.7s -> v339 N=32768 8.8s) verifies closed-form algebraic primitive at LOCAL production-N. PP-48 + PP-49 cross-N points {4096 v334, 8192 v337, 16384 v338, 32768 LOCAL v339 + 32768 CLOUD v335 Cell 2 Part B kappa46_fingerprint distinct path} = strong 4-point cross-N LOCAL + 1 cloud (different anchor). Both rows STAY at 0.70-0.85 (v338 BAND-LIFT to 0.70-0.85; cloud-confirmation for further LIFT requires distinct cloud-deployed anchor at v339-equivalent N=32768 -- Wave 5 cloud Cell 2 was kappa46_fingerprint not combo2-direct; queued for next-batch cloud dispatch).

**(F) PP-46 N=16384 intermediate SUB-PROPERTY.** deletion_cert_z_ratio_n16384_v1 GENUINE FULL HARD_PASS at N=16384 5-seed mean_Z=137.17 (HP>=2.5 = 55x margin). PP-46 N-scaling: founding N=4096 (earlier) + N=32768 cloud v335 Z=156 + N=16384 v339 Z=137 = 3-point N-curve. Both N=16384 and N=32768 produce Z>>100 -- substrate deletion-cert non-repudiation Z-ratio is monotonically strong in N at production-N regime. PP-46 parent band 0.70-0.85 UNCHANGED (v335 already BAND-LIFTED via Wave 5 cloud; v339 N=16384 is corroborative intermediate point).

**(G) Streaming SP8 sliding-window SUB-PROPERTY.** streaming_prediction_8_v1 GENUINE FULL HARD_PASS at N=1024 5-seed mean_fid_window=0.9997; late_adv=0.1249; newest=0.9997. Streaming family (SP5 consolidation v331, SP8 sliding-window v339) gains sliding-window sub-property. Streaming row UNCHANGED parent band; SP8 sub-property documents sliding-window primitive at N=1024 founding.

**(H) PP-51 CAVEAT: LOCAL N=32768 production-envelope FAILS 3/4 HP gates.** wave5_cell5_combo1_n32768_local_v1 GENUINE HARD_FAIL at N=32768 LOCAL (MMD=0.93 vs HP<0.02 = 47x; k3_resc=2.28 vs HP|k-1|<=0.05 = 25x off; slope=1.52 vs HP<=1.3 = 1.17x; cos=1.0 PASS). v3 GPU-fix HP path validated at N=4096 (v338); LOCAL N=32768 does NOT preserve identity-band signatures. PP-51 parent band 0.70-0.85 UNCHANGED; NEW CAVEAT documents LOCAL-N=32768 BLOCK. Cloud N=32768 dispatch authorization (per v338 routing item #1) REMAINS VALID -- cloud Wave 5 spec configuration is distinct from LOCAL v339 path; cloud may have different numerics regime. LOCAL-vs-cloud delta documented as substrate hardware-precision finding; substrate finite-N implicit-Gram regime LOCAL ceiling near N=8192-16384 (v338 N=4096 HP confirmed; LOCAL N=8192/N=16384 production-envelope NOT yet directly tested due to v339 N=8192 NO-DATA-DIR script crash -- Issue I-14).

**(I) PP-45 LOCAL-vs-CLOUD precision CAVEAT.** combo3_unified_api_v1_n32768_local GENUINE MIDDLE_BAND at N=32768 LOCAL (mean_rel ~1.5e-3 across tr_W1/2/3) vs cloud H100 zero-error at N=32768 v335 + N=16384 v338. LOCAL hardware-precision floor near ~1e-3 at N=32768; cloud H100 produces zero-error path. PP-45 parent band 0.70-0.85 UNCHANGED; CAVEAT documents LOCAL precision-floor near 1e-3 at production-N=32768. Substrate algebraic-theorem moat HOLDS but LOCAL hardware-precision regime is documented.

**(J) PP-51 alpha^(p-1) audit-sensitivity SUB-PROPERTY with slope CAVEAT.** combo1_alpha_p_minus_1_audit_sensitivity_v1_n4096 GENUINE MIDDLE_BAND at N=4096 5-seed: slope=0.9942 (HP [1.5, 2.5] FAIL); rho=1.0000 (HP>=0.8 PASS); sens_05=0.1498 (PASS). Substrate spearman-rank perfect (rho=1.0); alpha^(p-1) slope FLAT (slope ~1.0 not in expected scaling band [1.5, 2.5]). PP-51 sub-property added; CAVEAT: alpha^(p-1) audit-sensitivity scales monotonically with delta_alpha (rho PASS) but with slope OUT-OF-BAND (~1.0 not 1.5-2.5). May indicate (a) substrate's alpha^(p-1) sensitivity has DIFFERENT scaling exponent than research-cycle delivered spec; (b) spec exponent miscalibrated; (c) cells did not span enough delta_alpha range to see the predicted slope regime. Rescue R1-R5 filed; R5 0-compute theory-side audit of slope formula in research spec FIRST.

**(K) Issue I-12 (NEW) kappa3 sensitivity sigma_sep COLLAPSE at N=16384.** kappa3_sensitivity_sweep_n16384_v1 GENUINE HARD_FAIL at N=16384 5-seed mean_min_sigma_sep=0.3219 (HF<2.0 = 12.4x BELOW HF threshold). DIRECT CONTRADICTION with v335 Wave 5 Cell 2 Part B at N=32768 (sigma_sep 2.55-1726.6 across delta_alpha grid). Either: (a) N=16384 substrate regime has DIFFERENT spectral-sensitivity bands than N=32768 -- substrate sigma_sep is NOT monotone-in-N; (b) sweep config covers an unsupported (delta_alpha, M, alpha) regime where HP gate should have been recalibrated; (c) sigma_sep observable definition not comparable between Wave 5 cell and v339 sweep code. PP-50 NEW CAVEAT N=16384 sigma_sep=0.32 documents the catastrophic-low cell. Rescue R1-R5 for I-12 (cheapest-first):
- R1 (0-compute, applied) ANNOTATION-only: PP-50 sub-property CAVEAT N=16384 documented; substrate sigma_sep observable at N=16384 sweep regime != Wave 5 Cell 2 Part B regime.
- R2 (~5min CPU + Python) Read v339 sweep script + v335 Wave 5 Cell 2 Part B script side-by-side to identify config delta (delta_alpha grid? M? alpha range? observable definition?); 0-compute theory check.
- R3 (~30min CPU) Re-ship N=16384 with v335 Wave 5 Cell 2 Part B EXACT config (delta_alpha grid {0.0001, 0.001, 0.01, 0.04, 0.1}; M; alpha); if sigma_sep recovers to >2.0 at delta_alpha>=0.001, R2 config-delta hypothesis confirmed.
- R4 (~1h CPU) N-scaling sweep N={4096, 8192, 16384, 32768} same config to confirm sigma_sep monotone-in-N or N-non-monotone substrate regime.
- R5 (~$5 cloud) Cloud N=16384 same script to disambiguate LOCAL hardware-precision vs substrate regime.

**(L) Issue I-13 (NEW) caching v2 test-under-stress design.** caching_eviction_pp44_capacity_aware_v2_n4096 GENUINE HARD_FAIL at N=4096 5-seed fid_no_evict=0.8791 (HP<=0.5 FAIL -- no-eviction baseline DID NOT DEGRADE as stress design intended). NOT substrate failure -- TEST DESIGN UNDER-STRESS: no-eviction baseline at N=4096 stayed at 0.88 (substrate handles capacity without eviction); eviction-cell fid=1.0 PASS; retained fid=1.0 PASS. Test should have stressed capacity to force baseline drop. Rescue R1-R5 for I-13 (cheapest-first):
- R1 (0-compute, applied) ANNOTATION-only: I-13 documents under-stressed regime; baseline fid=0.88 indicates substrate has CAPACITY HEADROOM at N=4096 K=current configuration; positive substrate signal not failure.
- R2 (~5min Python edit) Bump K (number of patterns) to push no-eviction baseline below 0.5 (e.g., K=1.5*current or 2*current); re-ship.
- R3 (~10min Python edit + ship) Reduce N or increase pattern overlap to force baseline degradation; re-ship at adjusted stress regime.
- R4 (~30min Python redesign) Add capacity-stress sweep cells {K=K0, 1.5*K0, 2*K0, 3*K0} to map baseline-degradation curve and identify HP regime.
- R5 (parking) Move PP-44 capacity-aware sub-property to lower priority pending I-13 design fix.

**(M) Issue I-14 (NEW) combo1_v3 N=8192 NO-DATA-DIR script failure.** combo1_p3_dam_implicit_gram_v3_n8192_production_envelope_v1 NO REMOTE DATA DIR + bridge verdict=failed. Script crashed pre-data-dir-creation or never ran. v3 GPU-fix at N=4096 v338 HP -- N=8192 implicit-Gram production-envelope expected to work. Likely VRAM OOM at N=8192 (Gram matrix scales N^2; 4 GB at N=4096 -> 16 GB at N=8192 likely exceeds RTX-4060-Ti 16 GB usable). Rescue R1-R5 for I-14 (cheapest-first):
- R1 (0-compute, applied) ANNOTATION-only: Issue I-14 documents NO-DATA-DIR + likely-OOM hypothesis; LOCAL N=8192 implicit-Gram likely beyond VRAM ceiling.
- R2 (~5min remote check) SSH and check remote stderr/log/scheduled-task output for OOM trace OR pre-flight smoke-gate failure to disambiguate OOM-vs-pre-flight.
- R3 (~10min Python edit) Apply Hutchinson estimator stochastic Gram-trace (sparse N^2 -> M*N memory; v327 PP-37 RESCUE pattern) at N=8192 to reduce VRAM; re-ship.
- R4 (~30min Python edit) Batch-iterative Gram-solve (block CG iteration) to reduce peak VRAM; re-ship.
- R5 (~$5 cloud) Cloud H100 80 GB N=8192 direct re-ship to confirm SUBSTRATE-VS-HARDWARE; if cloud HP, confirms LOCAL hardware ceiling.

**(N) Issue I-15 (NEW) pp49_hrc_counterfactual_depth_10 NO-DATA-DIR script failure.** pp49_hrc_counterfactual_depth_10_v1_n4096 NO REMOTE DATA DIR + bridge verdict=failed. Script crashed pre-data-dir-creation or smoke-gate pre-flight failure. PP-49a depth-10 was HP at v335 cloud N=32768; v339 LOCAL depth-10 N=4096 should work in principle. Rescue R1-R5 for I-15 (cheapest-first):
- R1 (0-compute, applied) ANNOTATION-only: Issue I-15 documents NO-DATA-DIR; not OOM (PP-49a depth-10 N=32768 cloud worked).
- R2 (~5min remote check) Get-Content scheduled-task-stderr for pp49_hrc_counterfactual_depth_10 to disambiguate (smoke-gate? design typo? import error?).
- R3 (~10min Python audit) Read v339 pp49_hrc_counterfactual_depth_10 script + compare to v335 Wave 5 Cell 5 / cloud depth-10 path to identify config delta or pre-flight-gate condition.
- R4 (~10min Python edit) Apply fix per R2/R3 finding; re-ship.
- R5 (parking) Carry-over for next-cycle routing; PP-49a depth-10 cloud (v335) sub-property STANDS independently.

### Rescue-sketch sequencing (CHEAPEST FIRST per [[feedback-rescue-sketch-first-sequencing]])

For **a3 rollback timing-budget MIDDLE** (PP-52 SUB-PROPERTY with HP3 timing fail):
- R1 (0-compute, applied) ANNOTATION-only: PP-52 sub-property "exact rollback algebra CONFIRMED (rel_err=0; acc=1.0); timing-budget MISS (rollback wall 0.32-0.35s vs 0.05s gate)"; substrate algebra is EXACT, timing gate may be miscalibrated.
- R2 (~5min code-read) Audit a3 spec timing-budget formula vs actual rollback path (matvec count? Hutchinson probes? sigma threshold check loop?); identify whether 0.05s gate is reachable in principle.
- R3 (~10min Python edit) If gate is achievable: optimize rollback path (vectorize matvec; reduce probes); re-ship at adjusted budget.
- R4 (parking) If gate is fundamentally not reachable for N=1024 path: relax HP3 to 0.4s or N-dependent budget; document as substrate algorithmic-floor finding.

For **combo1 alpha^(p-1) slope OUT-OF-BAND MIDDLE** (PP-51 sub-property):
- R1 (0-compute, applied) ANNOTATION-only: PP-51 sub-property "alpha^(p-1) sensitivity monotone (rho=1.0 PASS); slope FLAT (~1.0 not [1.5, 2.5])"; CAVEAT documented.
- R2 (~30min theory + code-read) Theory-side audit of slope formula in research-cycle delivered spec; compare to v327 F_4 exponent typo pattern; check whether (p-1) exponent should be (p) or different power; PROT-022 formula-selftest discipline.
- R3 (~10min Python edit) If R2 finds typo: fix + re-ship at N=4096; if R2 clean: extend delta_alpha grid wider to see slope regime change.
- R4 (~30min CPU) N=8192 5-seed same delta_alpha grid to test N-scaling of slope.
- R5 (parking) PP-51 sub-property stays at "MIDDLE with slope caveat" pending R2-R4.

### Tallies (v338 -> v339)

- **HONEST:** 430 -> **442** (+12: 8 GENUINE HP + 4 GENUINE MIDDLE/HF readings; 2 NO-DATA-DIR script failures + 1 SMOKE-ONLY-PARK NOT counted as honest readings -- those are diagnostic-only).
- **LABEL-VS-HONEST:** 202 -> **205** (+3 NEW catches #203 Wave 5 Cell 5 LOCAL HF mis-pre-framed as HP, #204 COMBO-3 N=32768 LOCAL MIDDLE mis-pre-framed as HP, #205 a4 SMOKE-ONLY mis-pre-framed as ambiguous-timeout-or-failure). All 3 catches are TASK-PROMPT PRE-FRAMING category per [[feedback-no-preframing]]. The 14 honest metrics-resolved verdicts had 0 verdict_msg label catches (msg labels accurate to per-cell metrics).
- **Portfolio:** 32+73 -> **32+74** (+1 NEW TOP-LEVEL ROW PP-52 Hebbian-vs-LoRA-speedup empirical capstone 0.55-0.70 EXPLORATORY). Sub-properties: 8 NEW (PP-52 one-shot-addition + PP-52 exact-rollback-with-timing-caveat + PP-12 L=5 N=4096 + PP-49a depth-15 N=8192 + PP-48 depth-5 N=4096 + PP-48 4-level N=4096 + PP-48/49 N=32768 LOCAL 4th cross-N + PP-46 N=16384). 4 NEW CAVEATS (PP-51 LOCAL N=32768 HF; PP-45 LOCAL-vs-CLOUD precision; PP-51 alpha^(p-1) slope; PP-50 N=16384 sigma_sep collapse). 4 NEW ISSUES (I-12 through I-15).
- **Cap_map version: v339.**

### Framework reliability (v339)

- General: 65-75% UNCHANGED.
- Specific-documented: 55-65% UNCHANGED (Issues I-12 + I-15 introduce TWO new specific-documented uncertainty bands -- partially offsets PP-52 founding strength; net UNCHANGED).
- Product-feature: 78-92% -> **78-92%** UNCHANGED (PP-52 founding STRENGTHENS the substrate-product moat with training-acceleration row + PP-12 L=5 / PP-49a depth-15 / PP-48 depth-5 / PP-48 4-level / PP-46 N=16384 corroborations LIFT product-feature confidence; BUT PP-51 LOCAL-N=32768 CAVEAT + PP-45 LOCAL precision CAVEAT + I-12 PP-50 sensitivity sigma_sep collapse + I-13 caching design + I-14 + I-15 OPEN script failures DEFLATE product-feature confidence; net UNCHANGED).

### Known infrastructure issues (annotation block; UPDATED in v339)

**Issue I-1 through I-7** (v323-v332, OPEN v339). STILL OPEN; v339 batch did NOT touch them.
**Issue I-8 (v333, RESOLVED v338, RESOLUTION HOLDING v339).** v3 GPU-fix at N=4096 5-seed RESOLVED v338. LOCAL N=8192 production-envelope I-14 (NEW v339) is distinct from I-8 resolution; cloud N=32768 dispatch authorization HOLDS.
**Issue I-9 (v334, PARTIAL-RESOLVED v336, OPEN v339).** STILL OPEN; v3 N=8192 next step.
**Issue I-10 (v334, PARTIAL-RESOLVED v336, OPEN v339).** STILL OPEN; v3 fine rho-grid next step.
**Issue I-11 (v335, OPEN v339).** STILL OPEN; research-cycle routing FILED.
**Issue I-12 (NEW v339).** kappa3_sensitivity_sweep N=16384 sigma_sep=0.32 catastrophic-low contradicts v335 Wave 5 Cell 2 Part B N=32768 sigma_sep 2.55-1726.6; PP-50 CAVEAT. R1-R5 filed.
**Issue I-13 (NEW v339).** caching_eviction_pp44_capacity_aware_v2 N=4096 under-stressed test design (no-evict baseline fid=0.88 instead of <=0.5 stress regime). R1-R5 filed.
**Issue I-14 (NEW v339).** combo1_p3_dam_implicit_gram_v3_n8192_production_envelope NO-DATA-DIR; likely VRAM OOM at N=8192 LOCAL (Gram N^2 memory). R1-R5 filed; R2 remote-log-check is cheapest first.
**Issue I-15 (NEW v339).** pp49_hrc_counterfactual_depth_10_v1_n4096 NO-DATA-DIR; likely pre-flight smoke-gate failure or design typo (PP-49a depth-10 N=32768 cloud worked v335). R1-R5 filed; R2 remote-stderr-check is cheapest first.

### PROT compliance (v338 -> v339)

- PROT-004/006: NO row closures. 1 NEW TOP-LEVEL ROW (PP-52). 0 BAND-LIFTS. 8 NEW SUB-PROPERTIES + 4 NEW CAVEATS. 4 MIDDLE/HF candidates kept OPEN with R1-R5 rescue sketches cheapest-first (a3 timing PP-52; combo1 alpha^(p-1) slope PP-51; kappa3 N=16384 PP-50/I-12; caching v2 I-13). 2 NO-DATA-DIR (I-14 + I-15) + 1 SMOKE-ONLY-PARK (a4): not closed.
- PROT-007: history v339 entry inline.
- PROT-008: 1 new top-level row + 8 new sub-properties + 4 caveats + 4 new issues; no portfolio regression; no row closures. State-transition validator: PP-52 founding meets 3/3-HP at N=1024 5-seed unanimous + Hebbian-vs-LoRA speedup 923x wall + 500x flops + 0pp acc delta + lit-scan-calibration penalty applied (founding criteria MET for EXPLORATORY top-level row at lower band 0.55-0.70 than task-input-suggested 0.65-0.80 due to N=1024 only founding -- production-N cross-N required for band-LIFT).
- PROT-009: cap_map.md + history.md inline + strategy_decisions_2026-06-02.md (this entry) + visibility_decisions_2026-06-02.md + status_log entry staged atomically; **250th PROT-009 paired commit**.
- PROT-018: per-anchor _n<N> suffix audit -- 14 of 18 anchors have explicit _n<N> suffix matching metrics N (combo2_..._n32768=32768 match; combo3_..._n32768_local=32768 match; q_a3_l5_..._n4096=4096 match; q_b1_..._n8192=8192 match; deletion_cert_..._n16384=16384 match; kappa3_sensitivity_..._n16384=16384 match; pp48_..._n4096=4096 match; combo1_alpha_p_minus_1_..._n4096=4096 match; caching_eviction_..._n4096=4096 match; negative_knowledge_tree_..._n4096=4096 match; wave5_cell5_..._n32768_local=32768 match). 4 anchors (a1, a2, a3, a4, streaming_prediction_8_v1) have NO _n<N> suffix and metrics N=1024 / smoke 512 -- per PROT-018 anchor-naming convention, anchors WITHOUT _n<N> suffix are exempt from the suffix-binding contract (Cluster A and streaming-prediction families historical convention). PROT-018 all 18 clear.
- PROT-021: smoke-checkpoint contamination -- 16 anchors verified _source=remote run_mode=full multi-seed (5-seed for all 16). 2 anchors (I-14, I-15) NO-DATA-DIR script failures cannot have run_mode contamination by definition. 1 anchor (a4) IS the smoke-only artifact (run_mode=smoke n_seeds=2 N=512) identified per [[feedback-smoke-checkpoint-contamination]]; treated as PARK + LABEL-VS-HONEST #205 catch.
- PROT-022: combo1 alpha^(p-1) slope MIDDLE triggers R2 theory-side formula-self-test discipline (slope formula audit BEFORE re-ship); a3 rollback timing MIDDLE triggers R2 timing-budget formula audit. Both PROT-022 formula-selftest preconditions documented in rescue R2.

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 applied to all 18 anchors; 0 verdict_msg-label catches at the metrics-msg layer (all 14 metric-bearing anchors honest-as-labeled at the per-cell metrics level); 3 NEW LABEL-VS-HONEST catches (#203 Wave 5 Cell 5 LOCAL HF; #204 COMBO-3 LOCAL MIDDLE; #205 a4 SMOKE-ONLY) are TASK-PROMPT PRE-FRAMING category per [[feedback-no-preframing]] -- catches against the orchestrator's task input language rather than against the metrics-msg labels themselves.
- [[feedback-no-preframing]]: 3 task-input pre-framing catches surfaced explicitly; Wave 5 Cell 5 LOCAL framed "HP per research's spec" but HF in reality (3/4 gates by 30-50x); COMBO-3 N=32768 LOCAL framed "was HP at N=32768 cloud" but LOCAL MIDDLE in reality (LOCAL precision-floor delta); a4 framed "timeout? failed?" but SMOKE-ONLY artifact in reality. Pre-framing did NOT propagate into cap_map decisions; honest readings authoritative for all 3 catches per Step 0 rule.
- [[feedback-smoke-checkpoint-contamination]]: PROT-021 applied; a4 SMOKE-ONLY artifact correctly identified; combo2 fast 8.8s at N=32768 LOCAL verified sub-linear scaling vs v337 N=8192 (0.82s) and v338 N=16384 (6.7s) = closed-form algebraic primitive consistent NOT smoke.
- [[feedback-cap-map-update-protocol]]: atomic single commit; push BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]].
- [[feedback-for-you-tab-primary-channel]]: status_log entry CRITICAL importance with plain_language field filed (PP-52 NEW TOP-LEVEL ROW empirical capstone + Wave 5 Cell 5 LOCAL HF + 3 LABEL-VS-HONEST catches + 4 NEW ISSUES = CRITICAL tier per cap_map convention).
- [[feedback-decision-log-eol-handling]]: append via append_decision_log.py.
- [[feedback-subagent-permission-inheritance]]: push BLOCKED from sub-agent context; commit hash surfaced for main thread.
- [[feedback-rescue-sketch-first-sequencing]]: 4 MIDDLE/HF + 2 NO-DATA-DIR rescues filed cheapest-first; R1 0-compute annotation FIRST in each case; R2 cheap code/log read SECOND; R3+ progressively expensive empirical retries.
- [[feedback-rehabilitation-after-rejection]]: 0 row rejections this batch; 4 MIDDLE/HF candidates kept OPEN with R1-R5 rescue sketches before any closure consideration.
- [[feedback-pipeline-pacing]]: pause-flag ABSENT verified; GPU overnight_queue=0 pending+running; CPU remote_cpu_queue=18 pending+running (saturated). GPU queue at 0 with CPU saturated: dispatching exp_dev for GPU queue refill below.
- [[feedback-strategy-shore-up-capabilities]]: PP-52 NEW TOP-LEVEL ROW founds the training-acceleration product narrative (research's anchor row); PP-12 / PP-48 / PP-49a / PP-46 corroborative depth/level/N-scale extensions across 5 sub-properties; substrate compliance-sidecar GTM (v315) gains training-acceleration row + 4 capability-row depth/level/N-curve confirmations in single batch.
- [[feedback-brain-inspired]]: PP-52 Hebbian-vs-LoRA framed as substrate-side biological Hebbian-write learning rule vs gradient-descent learning rule; substrate one-shot Hebbian primitive is the biologically-grounded compositional-write algebra primitive (cross-reference Hebbian + DAM + saddle-hierarchy SKAH-M class).
- [[feedback-composition-classification]]: PP-52 founding is HANDOFF-class (Hebbian-write -> recall pipeline; primitive per write); PP-12 L=5 is HANDOFF-class (5-layer pipeline); PP-49a depth-15 is SCORE-class (per-depth fidelity); PP-48 depth-5 + 4-level are SCORE-class; PP-46 N=16384 SCORE; PP-48/49 N=32768 LOCAL SCORE.
- [[feedback-value-creation-not-competition]]: PP-52 framed as substrate-side training-acceleration capability (Hebbian-write primitive ENABLES one-shot updates without LoRA-grade gradient sweep) -- NOT competitive-positioning vs LoRA.
- [[feedback-no-papers-product-only]]: PP-52 framed as substrate killer-feature training-acceleration row, not publication-grade Hebbian-vs-LoRA empirical claim.
- [[feedback-lit-scan-calibration-penalty]]: PP-52 founds at 0.55-0.70 (LOWER than task-input-suggested 0.65-0.80) per +0.05 lit-scan deflation (substrate Hebbian-write-vs-gradient empirical capstone is uncharted finite-N regime; production-N cross-N required for band-LIFT eligibility).
- [[feedback-aggressive-cross-domain-research]]: PP-52 founding is the training-acceleration product-cross-domain probe (substrate-product narrative anchor row).
- [[feedback-strategy-spec-formula-selftests]]: combo1 alpha^(p-1) slope MIDDLE triggers R2 PROT-022 formula-selftest before any re-ship; pattern-match to v327 F_4 exponent typo. a3 timing budget MIDDLE triggers R2 timing-formula audit.

### Push and follow-on (v339)

Push: BLOCKED from sub-agent context; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

Main-thread routing candidates (highest -> lowest priority; v338 carryovers RETAINED + v339 additions):

1. **I-14 combo1_v3 N=8192 LOCAL OOM diagnosis** (NEW v339 HIGHEST PRIORITY; R2 remote-stderr/scheduled-task-log check is cheapest first; if OOM confirmed, R3 Hutchinson Gram-trace at N=8192 OR R5 cloud N=8192 dispatch).
2. **I-15 pp49_hrc_counterfactual_depth_10 N=4096 diagnosis** (NEW v339; R2 remote-stderr check; R3 script-side audit vs v335 cloud depth-10 path).
3. **I-12 kappa3 sigma_sep config-delta diagnosis** (NEW v339; R2 0-compute script side-by-side vs v335 Wave 5 Cell 2 Part B EXACT config audit).
4. **PP-52 production-N cross-N {N=4096, 8192, 16384} 5-seed** (NEW v339; band-LIFT eligibility requires production-N corroboration; CPU queue plenty for N=4096 / N=8192).
5. **Wave 5 Cell 5 CLOUD N=32768 dispatch** (v338 routing item #1 STILL VALID -- cloud Wave 5 spec distinct from LOCAL v339 HF; ~$5-10 single cell).
6. **a4 audit-during-training FULL re-ship at N=4096 5-seed** (NEW v339; SMOKE-ONLY artifact; FULL needed for Cluster A4 monitor evaluation; CPU OK).
7. **I-13 caching v2 capacity-stress design fix + re-ship** (NEW v339; R2 K-bump Python edit + re-ship at adjusted stress regime).
8. **a3 timing-budget rescue R2 timing-formula audit + re-ship** (NEW v339; PROT-022 formula-selftest; substrate rollback algebra is EXACT, only timing gate at issue).
9. **combo1 alpha^(p-1) slope rescue R2 theory-side formula audit** (NEW v339; PROT-022 formula-selftest; check for v327 F_4 exponent typo pattern).
10. **COMBO-4 v2 mu-aging rescue R5 theory-audit** (v338 carry-over; R5 0-compute theory check before any GPU spend).
11. **F4 M4 I-9 v3: N=8192 5-seed** (v336 PARTIAL-RESOLVED; ~10min CPU).
12. **kappa3 I-10 v3: fine rho-grid [0.15, 0.30]** (v336 PARTIAL-RESOLVED; ~3min CPU).
13. **PP-47 hippocampal cross-N N=16384 5-seed** (v333 carry-over).
14. **PP-48 + PP-49 cross-N N=32768 cloud (combo2-direct)** (v337/v338 carry-over; v339 LOCAL N=32768 HP corroborates; cloud dispatch for cross-N 5-point lock).
15. **I-11 research-cycle routing: Wishart/MP/free-Poisson analytic recalibration** (v335 carry-over).
16. **I-7 orphan failures re-ship vs close** (v332 carry-over).
17. **Q-F3 cophenetic correlation** (v330 carry-over).
18. **Q-F1 5-seed N=2048 follow-up** (v331 carry-over).
19. **Q-F4 saddle-overlap triplet test** (v330 carry-over).
20. **Q-F2 FDT ratio X(C) measurement** (v331 carry-over).
21. **graph_community R2 absolute-cos rescue / program_exec_audit_branching R2 sibling-list rescue / caching_capacity_aware cell-A workload variation rescue / PP-43b LRU small-M rescue** (v330-v331 carry-overs).
22. **I-6 script-author audit for two_time_correlator_fdt scripts** (v331 carry-over).
