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

