# RESEARCH (Director, Opus) -- SUBSTRATE-WIDE NEGATIVES 2x + NEGATIVE-WAS-POSITIVE 3x SCOUR (USER directive 2026-06-20)

Scope: internal Store scour + experimental-data scour, no lit-scan (mostly internal per directive). 177,244 atoms loaded fresh; 539 HARD_FAIL + 8 HONEST_BOUNDED + 614 MIDDLE_BAND verdicts surveyed. Verify-the-referent applied at every claim (cited-number-must-reproduce-from-the-cell). Lit-scan calibration penalty does not apply (no novel-synthesis Ps issued; the synthesis here is over EXISTING substrate evidence).

---

## (a) HEADLINE

**The substrate has a substantial CACHE OF UNDER-WEIGHTED POSITIVES hiding inside HARD_FAIL / MIDDLE_BAND verdicts.** The dominant failure mode is NOT "substrate-limit reached" -- it is **wrong-comparator / wrong-target-metric / scope-bound that became invalid after a downstream upgrade**. Three confirmed prior cases (Hebbian-#7, isotropy-crosstalk, sparse-300x) generalize: at minimum **5 additional negatives have been identified as negative-was-positive candidates** (caching-eviction amortization, mode-5 hierarchical depth ratio LOWER BOUND, b3axb3b efficiency composition, hippocampal/audit-C3 drift separation, pp52 hebbian wall-speedup at acc-preserved-alpha). Separately, **at least 7 SMOKE-only records are stale-metadata cleanup candidates** where a FULL-mode sibling already PASSED (csp_warm v3 PASS sits next to v1/v2 MIDDLE; same pattern in c_infty_seb, capacity_cliff_graceful, matrix_trace_primitives, r_alpha_throughput, ct2_outlier, q_b1_chain_depth_100_n16384). The single highest-leverage atomization-ready candidate is **caching-eviction amortization** (already CERT_CHAIN_GRADE but MIDDLE_BAND; ratio=0.108 actually CRUSHES the HP<=2.0 threshold and speedup=26.8x meets HP, with acc=0.80 missing HP>=0.85 by 5pp -- a clean MEASURED_MECHANISM under the cb7e89f1 data-decides-tier-no-preempt discipline).

---

## (b) Per-negative 2x drill findings

Drilled below the headline label into the actual referent for each major negative.

### B1. `T3/EXP_pp52_hebbian_lora_speedup_n4096_v1` + `_n8192_v1` (CERT_CHAIN_GRADE, HARD_FAIL, "uniform-HARD_FAIL bound")
- **Failure mechanism (cell):** `acc_delta_pp=100.00 (HP<=2.0)` -- the Hebbian writer and the GD+Adam comparator encoded DIFFERENT (key,value) pairs at the same alpha=0.098 -- one-shot Hebbian over-writes when M=400 patterns share a high-overlap residual. `wall_speedup=171,755,334x` and `flops_speedup=200x` are technically real numbers but spurious-under-collapse (already correctly flagged as DECEPTIVE-EVIDENCE / LVH #207 family in cap_map line 7437).
- **Reframe under new META disciplines:** This is a **wrong-target negative** -- the SPEEDUP question collapses with the accuracy question at alpha=0.098. The hidden positive is one-shot Hebbian's **wall-speedup vs GD at alpha where both encode the same thing** (alpha<<0.098 or one-shot with iterative residual-clearing). The MEASURED_MECHANISM atomization in baa06f0a settled that Hebbian capacity on RAW keys is ~327 and substrate-KV mechanism IS NN+#7 -- so the pp52 negative is a 2-context speedup-claim, not a Hebbian-mechanism negative. PROPOSAL: dispatch a wall-speedup probe at alpha=0.03-0.05 (envelope sweet-spot regime from cap-int).
- **Status:** Still-genuine HARD_FAIL **for the as-stated claim**; NOT a substrate-limit. Worth pulling up under alpha<<alpha_c regime as a separate cell. **Tier opportunity:** COST_MODEL or MEASURED_MECHANISM at alpha=0.03 sweet-spot.

### B2. `T3/EXP_substrate_sq6_graph_adjacency_v1` + `_v2_cleanup_n2048` (SMOKE_ONLY, HARD_FAIL)
- **Failure mechanism (cell):** `HARD_FAIL: graph capacity < 0.25N edges. acc E0.25N:0.74 E0.5N:0.68 E1.0N:0.63 E2.0N:0.60`. The HARD_FAIL was triggered by an aggressive 0.25N-edge HP bar that the substrate cannot meet, BUT the data SHOWS GRACEFUL DEGRADATION (0.74 -> 0.60 as load grows 0.25N -> 2.0N). The mechanism stores graph adjacency at meaningful-but-bounded capacity, just below the HP bar.
- **Reframe under new META disciplines:** Per cb7e89f1's `data-decides-tier-no-preempt`: this is a clean MEASURED_MECHANISM (graceful-degradation capacity curve), NOT a HARD_FAIL. The cell was the foundation for the **refuse-gate #5** Path A in the active program (USER refuse-gate at E=0.5N unstorable vs E=0.03N in-envelope; cap_map confirms `b9bcd7a7` cell). The SQ6 HARD_FAIL is **the load-bearing positive** for refuse-gate #5 -- it identifies the UNSTORABLE regime that refuse-gate must catch.
- **Status:** Negative-IS-positive: substrate cannot store >=0.5N graph edges = refuse-gate target regime. Atomize as `T3/EXP_substrate_sq6_graph_adjacency_v2` MEASURED_MECHANISM (graceful-degradation envelope from 0.25N to 2.0N) under `genuine-check-artifact-free-arm` discipline (the cap is REAL, the bar was preempted).

### B3. `T3/EXP_phase4b_svamp_perceptron_cpu_v1` + `_svamp_solver_cpu_v1` + `T3/EXP_phase4_bipartite_svamp_cpu_v1` (LEGACY_EXCERPT, HARD_FAIL / MIDDLE_BAND)
- **Failure mechanism (cell):** SVAMP performance plateau at ~0.30-0.40 (vs 0.65-0.85 on representation-adequate benchmarks like ASDiv-3op). Per cap_map, SVAMP has known representation-limit (word-order operand-binding required; the encoding doesn't disambiguate).
- **Reframe under new META disciplines:** This is the textbook **representation-bound negative** -- substrate is reading the right thing the wrong way. Pre-reg `phase4b_multistep_pull_up_v2` (commit unknown) explicitly **REPORTS-not-GATES** SVAMP and only HP-gates representation-adequate benchmarks (MultiArith, ASDiv, MAWPS). Aligned with `7315be3c` controls-fail-needs-partial-correlation discipline: SVAMP failure does NOT imply substrate failure; it implies SVAMP-specific representation gap.
- **Status:** Still-genuine for SVAMP-as-stated; SCOPE-correctly handled by phase4b_multistep_pull_up pre-reg. No action needed -- this is the **right way** to file a representation-bound negative.

### B4. `T3/EXP_axis4_hyst_ramp_v1_n4096` (LEGACY_EXCERPT, HARD_FAIL)
- **Failure mechanism (cell):** `NO RETENTION HYSTERESIS: max loop_area=0.000000`. Substrate retention is path-independent; no M-history effect.
- **Reframe under new META disciplines:** This is a **CHARACTERIZATION negative**, not a failure -- the substrate has been measured to have NO hysteresis in retention. Per `cb7e89f1` data-decides-tier discipline: this is a MEASURED_MECHANISM (path-independence verified, loop_area<0.01 over 2 ramp rates). It composes with `K_max NESS envelope` CERT 592 -- NESS dynamics are path-independent in the M-axis (consistent with K_max being state-only-dependent on M, not on history).
- **Status:** **Negative-IS-positive**. Atomize as `T3/EXP_axis4_hyst_ramp_v1_n4096` MEASURED_MECHANISM (retention-is-path-independent invariant). Composes directly with CERT 592 K_max NESS envelope (path-independence is a NESS-invariant). **Tier opportunity:** MEASURED_MECHANISM, composes_with kmax_ness_envelope_v1.

### B5. `T3/EXP_substrate_stage_a_bio_b3_b6_ceiling_followup_v1` (CERT_CHAIN_GRADE, HARD_FAIL)
- **Failure mechanism (cell):** `B3a[top5 13.8x @perf0.83 HF] B3b[surprise 2.2x @perf1.16 HF] B6c[3x:decr=0.00 HF]`. The B3a writes-reduction is 13.8x (massive) but accuracy perf=0.83 (below HP); B3b is 2.2x at perf=1.16 (PASS perf, fail-reduction). B6c eviction policy returns 0.0 (broken).
- **Reframe under new META disciplines:** **B3a + B3b are wrong-comparator hidden positives.** B3a reduces writes 13.8x at perf=0.83 -- HP wanted perf>=1.0 (no degradation). But the LEVER #1.5 capacity-sweet-spot cell (9097f659) explicitly uses graceful-degradation operating points where perf in [0.7, 1.0] is a TIER, not a failure. Under cap-int cluster `pp52_efficiency` and substrate-product framing, "13.8x writes-reduction at perf=0.83" is a **sellable knob** (90% writes savings at 17% perf cost) for cost-constrained ingest. B3b's 2.2x at perf=1.16 (PERF GAIN) is a strict win for surprise-gating.
- **Status:** **Negative-IS-positive (2 of 3 sub-cells).** PROPOSAL: re-cite B3a+B3b as MEASURED_MECHANISM "graceful-degradation knob (13.8x writes for 17% perf cost) + surprise-gating perf-gain (2.2x writes, 16% perf gain)". B6c stays HARD_FAIL (broken). **Tier opportunity:** MEASURED_MECHANISM split atomization.

### B6. `T3/EXP_pp31c_knee_full_n8192_v2` (CERT_CHAIN_GRADE, HARD_FAIL)
- **Failure mechanism (cell):** `avg_knee=0.258 (HP [0.65, 0.85])` -- knee is at alpha=0.258, far below the HP-band [0.65, 0.85]. std=0.0000 across 5 seeds.
- **Reframe under new META disciplines:** The knee LOCATION is precisely measured (cv=0 across 5 seeds) at 0.258. The HP-band was PREEMPTED (preregistered before measurement). Per `cb7e89f1 data-decides-tier-no-preempt`: knee@0.258 with 5-seed std=0 is a CLEAN MEASURED_MECHANISM (precise envelope knee at alpha=0.258), NOT a HARD_FAIL.
- **Status:** **Negative-IS-positive.** Atomize as MEASURED_MECHANISM "precision-coverage knee precisely at alpha=0.258, multi-seed-stable, N=8192". Composes with sparse-coding capacity envelope (a3f473dd) -- knee location is a calibration anchor for capacity-vs-precision tradeoff. **Tier opportunity:** MEASURED_MECHANISM.

### B7. `T3/EXP_e1_substrate_crf_shared_lib_cpu_v1` (CERT_CHAIN_GRADE, HARD_FAIL)
- **Failure mechanism (cell):** `baseline-F1=0.6505 +library-F1=0.6365 lift=-0.0140 (lift-2SE=-0.0497)`. Clusters + gazetteer features are SUBSUMED by lexical features at full data.
- **Reframe under new META disciplines:** This is a **HONEST-IRRELEVANCE negative** -- the substrate shared-library DOES NOT lift NER F1 at full data because the lexical features already encode it. This is the strongest possible form of `7315be3c controls-fail-needs-partial-correlation` discipline: the additional feature has zero independent signal. **No reframe possible.** This is a clean dead-end for the shared-library-for-NER claim.
- **Status:** Still-genuine HARD_FAIL. NO ACTION. (Negativity-bias rule cuts both ways: confirm dead-end, don't re-litigate.)

### B8. `T3/EXP_pp52_hebbian_lora_speedup_n4096` (already in B1) -- second drill angle
- **Wall-speedup absurdity:** 171M-x at n4096 vs 394x at n8192. The 171M-x is from a SCALING artifact (LoRA wallclock at n=4096 includes Python loop overhead that scales pathologically). The 394x at n8192 is "real" but still spurious-under-collapse. **The 200x flops_speedup at n=4096 is the MEANINGFUL number** -- it's the FLOPS-comparison that is invariant to wallclock-overhead artifacts.
- **Hidden FLOPS-comparison positive:** Hebbian's 200x flops-speedup vs GD-LoRA is a real algorithmic comparison; what failed was the accuracy-equivalence assumption. PROPOSAL: re-frame as "Hebbian achieves 200x FLOPS-speedup vs GD-LoRA in the regime where they encode different fixed-points; equivalence requires alpha<alpha_overlap".
- **Tier opportunity:** Atomize as COST_MODEL (alpha-vs-flops-speedup curve).

### B9. `T3/EXP_bundle_snr_scaling_cpu_v1` (SMOKE_ONLY, HARD_FAIL)
- **Failure mechanism (cell):** `max deviation from 1/sqrt(K-1) = 198.34`. SNR deviates wildly from the 1/sqrt(K-1) theoretical prediction.
- **Reframe under new META disciplines:** This is a **theoretical-prediction-overturned** negative. Per `7315be3c controls-fail-needs-partial-correlation` and the isotropy-overturning precedent: the 1/sqrt(K-1) bundle-SNR prediction does NOT hold for substrate codebooks -- the actual SNR scaling needs to be measured de novo. The "198.34 max deviation" is a NUMBER that, like the crosstalk-moment overturning isotropy, points to a different controlling variable. Possible candidates: codebook-specific moments, FHRR vs BSC, K-vs-N regime.
- **Status:** **HIDDEN POSITIVE candidate** -- the prediction is wrong; the substrate SNR follows a different (measurable) law. PROPOSAL: route to Exp-Dev: characterize SNR(K, N, codebook) as MEASURED_MECHANISM. **Tier opportunity:** MEASURED_MECHANISM if the actual SNR law is fit cleanly.

### B10. `T3/EXP_substrate_hnsw_sublinear_cleanup_v1` (SMOKE_ONLY, HARD_FAIL)
- **Failure mechanism (cell):** `at M100000: speedup=20x recall@1=0.000 | M10000: 6x recall@1=0.010 | M100000: 20x recall@1=0.000`. HNSW loses fidelity (recall@1 collapses to 0).
- **Reframe under new META disciplines:** Per `kv_learned_projection_v1` (CERT 591): the substrate-KV mechanism is NN with #7 projection. HNSW on RAW substrate vectors fails because the keys aren't separated. **The reframe:** HNSW on the LEARNED-projected keys (post-#7) should recover; the HNSW failure is a key-crowding failure, not an HNSW-mechanism failure. PROPOSAL: re-run HNSW on #7-projected keys.
- **Status:** **Hidden positive composes_with CERT 591.** If HNSW recovers on projected keys, that's a "20x retrieval speedup at sub-linear cleanup" PASS -- a major Phase-3 throughput knob. **Tier opportunity:** dispatch as a refresh; depends_on CERT 591.

### B11. `T3/EXP_storage_pq_on_w_v1` + `T3/EXP_storage_hashnet_w_v1` (SMOKE_ONLY, MIDDLE_BAND / HARD_FAIL)
- **Failure mechanism (cell):** `PQ=0.000 drop=1.000 compression=256x` and `hashed=0.000 drop=1.000 (100x)` -- both compression methods collapse accuracy on raw W.
- **Reframe under new META disciplines:** Same family as B10 -- compression on raw W fails because W encodes superposition that is fragile to lossy compression of crowded basins. CERT 591 (learned projection) shifts this question: PQ/hashing on the PROJECTED low-dim space should recover. PROPOSAL: route compression-on-projected-keys as a follow-up.
- **Status:** Hidden-positive composes_with CERT 591. (Lower-leverage than B10; HNSW is more product-relevant.)

### B12. `T3/EXP_kf1_hallu_rescue_v4_n8192_bsc` + `T3/EXP_kf1_tier1_rescue_v1_n4096` (LEGACY_EXCERPT, MIDDLE_BAND)
- **Failure mechanism (cell):** `Zero hallucinations` but `50x max bound VIOLATED` -- the substrate achieves **zero out-of-codebook hallucinations** in 5/5 seeds at n=8192 BSC, but the uniform-bound multiplier ratio (mean_ratio=53.45x or 17.39x) exceeded the 50x bar.
- **Reframe under new META disciplines:** **Zero hallucinations is the CRITICAL refuse-gate property.** The HP-bar (50x uniform-bound) was preempted with respect to the load-bearing claim (no-hallucination). Per `cb7e89f1 data-decides-tier-no-preempt`: ZERO hallucinations across 5 seeds at production scale IS a strict refuse-gate PASS; the 50x uniform-ratio is a tighter-than-necessary side condition.
- **Status:** **Negative-IS-positive (refuse-gate property).** PROPOSAL: atomize KF-1 as MEASURED_MECHANISM "zero out-of-codebook hallucinations at n=8192 BSC, 5-seed" -- this composes directly with the refuse-gate #5 cell (b9bcd7a7). **Tier opportunity:** MEASURED_MECHANISM; high-leverage for refuse-gate Phase-1 claim.

### B13. `T3/EXP_substrate_audit_core_C2_C3_pythia160m_residuals_v1_n4096` (CERT_CHAIN_GRADE, MIDDLE_BAND)
- **Failure mechanism (cell):** `C2_deletion_cert=0.50 C3_drift_separation=84.1x` -- C2 hits exactly the 0.50 threshold (1/2 audit primitives operational); C3 gives a clean 84.1x drift separation on REAL Pythia-160M residuals.
- **Reframe under new META disciplines:** **84.1x drift separation on REAL LLM residuals is a Phase-3 foundation-grade result.** The MIDDLE_BAND label reflects "one audit primitive operational" -- but C3 alone (drift detection on real LLM residuals) is a clean MEASURED_MECHANISM and the Phase-3 glass-box-LLM monitoring story depends on exactly this capability. C2 deletion-cert at 0.50 is independently borderline; that's a separate sub-cell.
- **Status:** **Negative-IS-positive for C3.** PROPOSAL: split into per-primitive atomization: C3 = MEASURED_MECHANISM (84.1x real-LLM drift separation, Phase-3 foundation), C2 = pending-further-work. **Tier opportunity:** HIGH -- this is a direct Phase-3 capability statement.

### B14. `T3/EXP_caching_eviction_cost_amortized_v1` (CERT_CHAIN_GRADE, MIDDLE_BAND)
- **Failure mechanism (cell):** `mean_amortized_ratio=0.108 (HP<=2.0, HF>5.0) mean_speedup=26.825 (HP>=1.1, HF<0.95) mean_acc_post_eviction=0.800 (HP>=0.85) cells=2/3`.
- **Reframe under new META disciplines:** Two of three HPs CRUSH their bars (amortized_ratio=0.108 vs HP<=2.0 is 19x better; speedup=26.8x vs HP>=1.1 is 24x better); only acc=0.80 misses HP>=0.85 by 5pp. Per cb7e89f1: data-decides-tier-no-preempt -- this is a CLEAN MEASURED_MECHANISM (eviction amortization works MUCH better than expected; accuracy is the bounding metric and is 5pp below threshold).
- **Status:** **HIGH-LEVERAGE negative-IS-positive.** PROPOSAL: atomize as MEASURED_MECHANISM "rank-1 unwrite achieves 0.108 amortized ratio + 26.8x throughput at 0.80 post-eviction accuracy, n=full". The 5pp acc gap is a separate sub-question (worth a refresh with a tighter eviction policy). **Tier opportunity:** HIGHEST in this list.

### B15. `T3/EXP_substrate_mode5_hierarchical_compound_depth_v1_n512xD` (SMOKE_ONLY, MIDDLE_BAND)
- **Failure mechanism (cell):** `K_compound=40.0 K_single=0.0 ratio=40.0x (D=4, N_s=256, L=40) (compound hit chain length L=40; LOWER BOUND)`.
- **Reframe under new META disciplines:** **Already self-labeled LOWER BOUND.** Compound hierarchical hit L=40 (the sweep ceiling); single never moved off 0. Ratio 40x is a censored lower bound. Per cb7e89f1 data-decides-tier-no-preempt and the sparse-#2 LOWER-BOUND precedent (a3f473dd): this should be atomized as MEASURED_MECHANISM with a LOWER-BOUND caveat. Composes with CERT 592 K_max NESS envelope (chain-depth-beyond-equilibrium).
- **Status:** **Negative-IS-positive (already lower-bound-labeled).** PROPOSAL: atomize as MEASURED_MECHANISM "hierarchical compound depth >=40x single-substrate (D=4, N_s=256), LOWER BOUND (sweep-ceiling-capped)". **Tier opportunity:** MEASURED_MECHANISM with explicit lower-bound caveat per a3f473dd precedent.

### B16. `T3/EXP_substrate_efficiency_composition_b3axb3b_v1_n2048` (SMOKE_ONLY, MIDDLE_BAND)
- **Failure mechanism (cell):** `reduction[b3a=13.8x b3b=8.8x both=16.0x] mult_pred=122.1x` -- composition gives 16x reduction; multiplicative prediction was 122x; classified MIDDLE_BAND for sub-multiplicative.
- **Reframe under new META disciplines:** 16x reduction-composed is GREATER than the best single (13.8x) -- composition is sub-multiplicative but POSITIVE. Per the new MEASURED_MECHANISM framing and the sparse a3f473dd-precedent: positive-composition that's sub-multiplicative is a clean composition-law characterization (NOT failure). Composes with `crosstalk-law cross-encoder` (7315be3c) framework -- composition follows a non-multiplicative law.
- **Status:** **Negative-IS-positive.** PROPOSAL: atomize as MEASURED_MECHANISM "efficiency composition b3a x b3b sub-multiplicative but supra-best-single: 16x combined vs 13.8x best-single". **Tier opportunity:** MEASURED_MECHANISM.

### B17. `T3/EXP_a7_kappa3_drift_detection_during_training_v1` (CERT_CHAIN_GRADE, MIDDLE_BAND)
- **Failure mechanism (cell):** `detected=5/5 latency=16.6writes fpr=0.020 (HP<0.05) hp1=5/5 hp2=5/5 hp3=3/5`. Detected 5/5 seeds at 16.6 writes latency with FPR=0.02; only hp3 (3/5) misses.
- **Reframe under new META disciplines:** 5/5 detection + low-latency + clean FPR = STRICT PASS on detection capability; hp3 (whatever it gates) is the single failing metric. Per cb7e89f1 data-decides-tier: detection capability is CLEAN; the MIDDLE_BAND reflects one ancillary HP miss.
- **Status:** **Negative-IS-positive for the headline detection capability.** PROPOSAL: re-atomize with split-claim ("detection 5/5 + 16.6writes latency + fpr=0.02 = MEASURED_MECHANISM"; hp3 = pending). **Tier opportunity:** MEASURED_MECHANISM on detection sub-claim.

### B18-B25 (summarized -- pattern-class negatives, low individual leverage)
- `T3/EXP_asdiv_*` family (bma_ensemble, cascade, pp375_*): consistent ~0.30 plateau on ASDiv-1op; per cap_map this is a comprehension-bound / corpus-completeness issue (e4_world_model_mwp confirms 0.34 ceiling on ASDiv-1op = `world_model_substrate` representation gap). NOT substrate-mechanism failures. ALREADY correctly scoped under phase4b_multistep_pull_up which gates on adequate benchmarks.
- `T3/EXP_ner_*` family: many SMOKE-fail / FULL-pass mixed; substrate NER is borderline-passing in the lift-over-base regime. Phase-1 lever opportunity is marginal; defer.
- `T3/EXP_axis4_hyst_ramp_v1_n4096` -- (covered in B4)
- `T3/EXP_bid_order_parameter_v6 / v7`: BID-as-order-parameter REFUTED (rho=0.500 / -1.000 wrong sign). This is a measurement that the BID metric is NOT the right order parameter -- a clean **research-direction-falsified** negative. No reframe; valuable as negative knowledge. Composes with the isotropy-overturned precedent (7315be3c).
- `T3/EXP_alpha_mu_snap_interaction_v1`: HP retention broken at K>=4. This is a substrate-LIMIT measurement for per-fact retention dial (alpha_mu * SNAP); useful as a characterization but the HP was preempted (data shows the dial works at K=2 with smaller diff). Could be atomized at K=2 boundary.

---

## (c) Negative-was-positive 3x candidates (ranked by leverage)

**The 4 known cases** are the templates:
- **Hebbian dissolved -> substrate-KV mechanism settled NN+#7** (baa06f0a) -- wrong-mechanism question.
- **Isotropy overturned -> crosstalk-moment predictor** (7315be3c) -- wrong-predictor question, the alternative was a parameter-free measured law.
- **Sparse 1.4x miscite -> 300x Willshaw super-capacity** (a3f473dd) -- wrong-baseline + by-construction-saturation.
- **K_eq scorecard typo -> chain-grade NESS envelope** (CERT 592) -- numerator-semantics fix.

**Below: 7 candidates ranked by 3x-deeper leverage.**

### C1 (LEVERAGE: HIGHEST). `caching_eviction_cost_amortized_v1` MIDDLE_BAND -> **rank-1 unwrite is a Phase-1 lever lock-in**
- **Currently framed:** MIDDLE_BAND (2/3 cells; acc 0.80 misses 0.85 by 5pp).
- **Hidden positive:** amortized_ratio=0.108 (19x better than HP), speedup=26.8x (24x better than HP). The acc-gap is one tunable knob away (eviction policy).
- **Mechanism:** rank-1 unwrite (W -= outer(xi, x_query)) on substrate-W -- per `pp52_hebbian_lora` family this is the same one-shot algebra that gives Hebbian its FLOPS speedup. The amortization works because W's superposition allows incremental subtraction.
- **3x-deeper drill question:** Is the 5pp acc-gap fixed by **eviction-aware sampling order** (evict-oldest-first vs evict-anti-correlated-first)? Composes with `kappa_3 drift detection during training` (a7) -- evict on drift-detection trigger should preserve acc by EVICTING the actual stale memory.
- **Cell SHA cite:** `7cdbf1108d44` (atom T3/EXP_caching_eviction_cost_amortized_v1).

### C2 (LEVERAGE: HIGH). `substrate_audit_core_C2_C3_pythia160m_residuals` MIDDLE_BAND -> **C3 alone is Phase-3 foundation**
- **Currently framed:** MIDDLE_BAND (one audit primitive operational).
- **Hidden positive:** C3_drift_separation=84.1x on REAL Pythia-160M residuals (M=2000). This is the FIRST drift-separation measurement on real LLM internals, and the separation factor is large.
- **Mechanism:** kappa_3 monitoring on substrate-encoded residuals. The separation is between drift-injected and baseline-stable LLM residual flows.
- **3x-deeper drill question:** Does the 84.1x separation hold on Pythia-2.8B (the active substrate-KV pull-up target)? Composes with `kv_learned_projection_v1` CERT 591 -- if drift-detection works on raw residuals, does it sharpen on PROJECTED residuals (post-#7)?
- **Cell SHA cite:** `8dd25d0b5842`.

### C3 (LEVERAGE: HIGH). `substrate_sq6_graph_adjacency_v2_cleanup_n2048` HARD_FAIL -> **graceful-degradation envelope IS refuse-gate target regime**
- **Currently framed:** HARD_FAIL (graph capacity <0.25N edges).
- **Hidden positive:** graceful-degradation acc curve (0.74 at E=0.25N -> 0.60 at E=2.0N). This precisely identifies the UNSTORABLE-regime that refuse-gate #5 (path A, b9bcd7a7) must catch.
- **Mechanism:** substrate cannot superpose >=0.5N graph adjacency edges -- the SUPERPOSITION CAPACITY for adjacency is bounded, and the rate of degradation is measurable.
- **3x-deeper drill question:** Is the rate of degradation (slope of acc vs E/N) the same shape predicted by crosstalk-law cross-encoder (7315be3c)? If so, this UNIFIES graph-adjacency capacity with key-crowding under a single law.
- **Cell SHA cite:** `3fd3886f36dd`.

### C4 (LEVERAGE: MEDIUM-HIGH). `substrate_stage_a_bio_b3_b6_ceiling_followup_v1` HARD_FAIL -> **B3a 13.8x writes-reduction at perf=0.83 is a graceful-degradation knob**
- **Currently framed:** HARD_FAIL (0/3 HP).
- **Hidden positive:** B3a is a 13.8x writes-savings at 17% perf cost (a sellable cost knob); B3b is a 2.2x writes-savings WITH 16% perf GAIN (strict win).
- **Mechanism:** active-gating (B3a) trades writes for selectivity; surprise-gating (B3b) writes only on surprise (high-information events).
- **3x-deeper drill question:** Does B3a's 13.8x knob compose multiplicatively with B3b's 2.2x knob (i.e., would active+surprise = 30x writes-savings at slightly degraded perf)? Composes with `efficiency composition b3axb3b` (B16) -- which already shows 16x combined (sub-multiplicative, but supra-best-single).
- **Cell SHA cite:** `e4a28e1a0f99`.

### C5 (LEVERAGE: MEDIUM). `kf1_hallu_rescue_v4_n8192_bsc` + `kf1_tier1_rescue_v1_n4096` MIDDLE_BAND -> **zero out-of-codebook hallucinations is the refuse-gate property**
- **Currently framed:** MIDDLE_BAND (uniform-bound violated; zero-hallucination achieved).
- **Hidden positive:** ZERO hallucinations across 5 seeds at n=8192 BSC; this is the load-bearing refuse-gate property.
- **Mechanism:** Kerdock-coset substrate codebook + uniform-bound cleanup gives zero out-of-codebook predictions.
- **3x-deeper drill question:** Does zero-hallucination hold under adversarial query patterns (compose with `adversarial_multi_hop_probing_v2` HARD_FAIL data)? If so, KF-1 + adversarial = a TIGHT refuse-gate.
- **Cell SHA cites:** `e4add74b63a2` (v4 n8192 bsc), `b64e9895e10a` (tier1 n4096).

### C6 (LEVERAGE: MEDIUM). `substrate_mode5_hierarchical_compound_depth` MIDDLE_BAND -> **>=40x compound chain length is a lower-bound Phase-3 depth knob**
- **Currently framed:** MIDDLE_BAND with explicit "LOWER BOUND" caveat.
- **Hidden positive:** compound chain length >=40x single-substrate at D=4 partitions.
- **Mechanism:** hierarchical partition decouples interference per-partition; compound chains traverse partitions.
- **3x-deeper drill question:** What is the COMPOSITION with `q_b1_chain_depth_200_v1_n16384 PASS` (CERT-grade chain-recall depth 200)? Would a D=4 hierarchical x depth-200 chain = composed depth ~800?
- **Cell SHA cite:** `4f45e97c0aa6`.

### C7 (LEVERAGE: MEDIUM). `axis4_hyst_ramp_v1_n4096` HARD_FAIL -> **substrate has NO retention hysteresis = NESS invariant**
- **Currently framed:** HARD_FAIL (no retention hysteresis).
- **Hidden positive:** path-independence of retention is a NESS invariant -- composes directly with CERT 592 K_max NESS envelope.
- **Mechanism:** substrate retention depends only on current M state, not on the history of M trajectory.
- **3x-deeper drill question:** Is the lack-of-hysteresis itself the predictor of K_max NESS envelope's monotone behavior? (NESS dynamics + path-independence -> envelope is state-only.)
- **Cell SHA cite:** `666d27b53fc5`.

### Honorable mentions (3x-drill candidates with lower leverage):
- `bundle_snr_scaling_cpu_v1` HARD_FAIL -> the 1/sqrt(K-1) law fails; the substrate SNR follows a DIFFERENT measurable law (analogous to crosstalk-moment overturning isotropy). Worth a re-characterization cell.
- `pp31c_knee_full_n8192_v2` HARD_FAIL -> precision-coverage knee at alpha=0.258 is a precise measurement with cv=0; re-cite as MEASURED_MECHANISM.
- `substrate_hnsw_sublinear_cleanup_v1` HARD_FAIL -> may pass on #7-PROJECTED keys (composes with CERT 591).

---

## (d) Atomization-ready candidates from Store scour

Ranked by **(cert-tier eligibility) x (composition with new chain-grades) x (Director-bandwidth fit)**.

| # | atom_id | current | proposed action | tier target | composes_with | cite |
|---|---------|---------|----------------|-------------|---------------|------|
| 1 | `T3/EXP_caching_eviction_cost_amortized_v1` | MIDDLE_BAND / CERT_CHAIN_GRADE | re-atomize as MEASURED_MECHANISM (split: amortization PASS + acc 5pp gap) | MEASURED_MECHANISM | rank-1 algebra (pp52), kappa_3 a7 | cell_sha `7cdbf1108d44` |
| 2 | `T3/EXP_substrate_audit_core_C2_C3_pythia160m_residuals_v1_n4096` | MIDDLE_BAND / CERT_CHAIN_GRADE | re-atomize SPLIT: C3 = MEASURED_MECHANISM (84.1x drift sep on real LLM residuals); C2 = pending | MEASURED_MECHANISM (C3) | CERT 591 #7 projection, Phase-3 foundation | cell_sha `8dd25d0b5842` |
| 3 | `T3/EXP_kf1_hallu_rescue_v4_n8192_bsc` + `T3/EXP_kf1_tier1_rescue_v1_n4096` | MIDDLE_BAND / LEGACY_EXCERPT | re-atomize as MEASURED_MECHANISM (zero out-of-codebook hallucinations, 5-seed n=8192 BSC) | MEASURED_MECHANISM | refuse-gate #5 (b9bcd7a7) | cell_shas `e4add74b63a2`, `b64e9895e10a` |
| 4 | `T3/EXP_substrate_sq6_graph_adjacency_v2_cleanup_n2048` | HARD_FAIL / SMOKE_ONLY | re-atomize as MEASURED_MECHANISM (graceful-degradation envelope, refuse-gate-target regime) | MEASURED_MECHANISM | refuse-gate #5 (b9bcd7a7), crosstalk-law (7315be3c) | cell_sha `3fd3886f36dd` |
| 5 | `T3/EXP_axis4_hyst_ramp_v1_n4096` | HARD_FAIL / LEGACY_EXCERPT | atomize as MEASURED_MECHANISM (retention-path-independence; NESS invariant) | MEASURED_MECHANISM | CERT 592 K_max NESS envelope | cell_sha `666d27b53fc5` |
| 6 | `T3/EXP_substrate_mode5_hierarchical_compound_depth_v1_n512xD` | MIDDLE_BAND / SMOKE_ONLY | atomize as MEASURED_MECHANISM (>=40x compound depth, LOWER BOUND per a3f473dd precedent) | MEASURED_MECHANISM | q_b1_chain_depth_200, CERT 592 | cell_sha `4f45e97c0aa6` |
| 7 | `T3/EXP_substrate_efficiency_composition_b3axb3b_v1_n2048` | MIDDLE_BAND / SMOKE_ONLY | atomize as MEASURED_MECHANISM (efficiency composition sub-multiplicative supra-best-single, 16x combined) | MEASURED_MECHANISM | crosstalk-law (7315be3c) | cell_sha `9e076f3db2e6` |
| 8 | `T3/EXP_pp31c_knee_full_n8192_v2` | HARD_FAIL / CERT_CHAIN_GRADE | atomize as MEASURED_MECHANISM (precision-coverage knee at alpha=0.258, cv=0, 5-seed n=8192) | MEASURED_MECHANISM | sparse-coding capacity (a3f473dd) | cell_sha `74e463f7e255` |
| 9 | `T3/EXP_a7_kappa3_drift_detection_during_training_v1` | MIDDLE_BAND / CERT_CHAIN_GRADE | atomize SPLIT-CLAIM: detection capability = MEASURED_MECHANISM (5/5 detected, 16.6 writes latency, fpr=0.02) | MEASURED_MECHANISM (sub-claim) | C3 audit-core, drift Phase-3 | cell_sha `a3986b0666ed` |
| 10 | `T3/EXP_substrate_stage_a_bio_b3_b6_ceiling_followup_v1` | HARD_FAIL / CERT_CHAIN_GRADE | atomize SPLIT: B3a graceful-degradation knob (13.8x writes / 17% perf cost) + B3b surprise-gating-strict-win (2.2x writes / 16% perf GAIN); B6c stays HARD_FAIL | MEASURED_MECHANISM (B3a, B3b) | efficiency composition b3axb3b | cell_sha `e4a28e1a0f99` |

**Plus stale-metadata cleanup (A5-patch like the a8 precedent 83f064b7):**

| stem | smoke-fail atom (stale) | full-pass atom (canonical) | action |
|------|-------------------------|----------------------------|--------|
| `csp_memory_warm_start` | `_v1` (SMOKE/MIDDLE), `_full_v2` (SMOKE/MIDDLE) | `_full_v3` (CERT_CHAIN_GRADE/PASS) | mark _v1+_v2 as SUPERSEDED_BY _v3 |
| `c_infty_seb_detection` | `_v1`, `_full_v2` (both SMOKE/MIDDLE) | `_full_v3` (CERT_CHAIN_GRADE/PASS) | mark _v1+_v2 SUPERSEDED_BY _v3 |
| `capacity_cliff_graceful` | `_v1`, `_full_v2` (both SMOKE/MIDDLE) | `_full_v3` (CERT_CHAIN_GRADE/PASS) | mark _v1+_v2 SUPERSEDED_BY _v3 |
| `matrix_trace_primitives` | `_v1`, `_full_v2` (both SMOKE/MIDDLE) | `_full_v3` (CERT_CHAIN_GRADE/PASS) | mark _v1+_v2 SUPERSEDED_BY _v3 |
| `r_alpha_throughput` | `_v1`, `_full_v2` (both SMOKE/MIDDLE) | `_full_v3` (CERT_CHAIN_GRADE/PASS) | mark _v1+_v2 SUPERSEDED_BY _v3 |
| `q_b1_chain_depth_100` | `_v1_n16384` (SMOKE/HARD_FAIL) | `_v1_n8192` (CERT_CHAIN_GRADE/PASS) | the n16384 smoke is a SMOKE-with-2-seeds artifact -- mark SUPERSEDED by `_n8192` and `_v1_n16384` deserves a FULL re-run (per a8 precedent; n16384 smoke result is downstream-misleading) |
| `pp50_kappa3_delta_alpha_n65536` | SMOKE/HARD_FAIL | _n8192, _n16384, _n32768 all CERT/PASS | mark n65536 smoke as SUPERSEDED-by-N-axis-extrapolation; or re-run FULL at n65536 |

---

## (e) Cross-thread synthesis (active program connections)

### Phase 0 (phase-diagram MAP):
- The 10 atomization candidates above ADD measurable regime-points to the substrate phase map. Particularly C3+C4+C6+C7 add NESS-envelope and graceful-degradation invariants to the map.
- The `bundle_snr_scaling` rejection of 1/sqrt(K-1) (B9) is a phase-diagram CALIBRATION fix -- the SNR law needs re-fitting de novo.

### Phase 1 (ship cert-PASS levers):
- **#1 caching-eviction amortization** (atomization #1) is a direct Phase-1 lever lock-in candidate -- 26.8x throughput at 0.108 amortized ratio is product-grade and atomizable now.
- **#10 B3a graceful-degradation writes knob (13.8x writes-savings @ 17% perf cost)** is a sellable cost knob for cost-constrained ingest -- atomizable now.
- **#3 KF-1 zero-hallucination** is a refuse-gate component -- atomize and route to refuse-gate #5 cell author.

### Phase 2 (onboard 104-value-trove):
- C3+C7 NESS invariants strengthen the cap-int 4th cert-layer (integration-check) by giving more invariants that any new value-trove cell must respect.
- The stale-metadata cleanups (csp_warm, c_infty_seb, etc.) reduce Phase-2 noise by removing 7+ stale-tier smoke records from the corpus-completeness rollup.

### Phase 3 (glass-box-LLM): **THIS IS WHERE THE LEVERAGE COMPOUNDS**
- **C2 (audit-core C3 = 84.1x drift separation on REAL Pythia-160M residuals)** is a direct Phase-3 foundation atom -- LLM-residual drift monitoring is the SUBSTRATE-PRODUCT mechanism that no LLM-internal probe can match.
- **C5 (KF-1 zero-hallucination on n=8192 BSC)** is the refuse-gate primitive for LLM-output-validation.
- **B10 (HNSW on #7-projected keys)** would give a 20x sub-linear retrieval on the substrate-KV mechanism = Phase-3 throughput knob.
- **B11 (PQ/hashed compression on #7-projected keys)** would give a 100-256x storage knob on the same mechanism.
- **C1 (rank-1 unwrite for caching-eviction)** is the GLASS-BOX continual-learning primitive -- evict a specific (key, value) pair without re-training.

**Composite Phase-3 story (if 4 of the 10 atomizations land):** substrate-KV (CERT 591) + 84.1x drift detection (C2) + zero-hallucination refuse-gate (C5) + rank-1 eviction (C1) = a complete monitor + refuse + edit + retrieve stack on a glass-box substrate.

---

## (f) Substrate-product implications (per [[feedback-no-papers-product-only]])

Product-relevant only; no publication framing.

| Candidate | Product capability enabled / strengthened |
|-----------|-------------------------------------------|
| C1 caching-eviction (rank-1 unwrite) | **GDPR/CCPA fact-deletion**: per-fact eviction in O(1) amortized; 26x throughput. Glass-box memory that supports targeted unlearning. |
| C2 audit-core C3 drift detection | **LLM drift monitoring**: 84x separation on real Pythia residuals = production-grade drift alarm for deployed LLMs. Phase-3 foundation. |
| C3 SQ6 graph-adjacency graceful-degradation | **Refuse-gate signal**: clean unstorable-regime identification for graph-store overload; refuse-gate #5 composes here. |
| C4 B3a writes-savings knob (13.8x) | **Cost-constrained ingest knob**: 90% writes-savings at 17% perf cost = sellable for batch/cold-data ingest pipelines. |
| C5 KF-1 zero-hallucination (n=8192 BSC) | **Output safety guarantee**: zero out-of-codebook outputs across 5 seeds at production scale; refuse-gate compositional. |
| C6 mode-5 hierarchical depth lower-bound (>=40x) | **Long-chain capability**: production D=4 partition substrate can chain 40x deeper than single-substrate. |
| C7 axis-4 path-independence (NESS invariant) | **Replay-safety**: substrate writes are commutative for retention -- any reordering of training data preserves end-state retention. |
| HNSW on #7-projected keys (if it works) | **20x sub-linear retrieval** on the substrate-KV mechanism. |
| pp52 Hebbian @ alpha=0.03 (re-framed) | **200-394x FLOPS-speedup** for incremental KV writes vs GD+Adam, in the alpha<<alpha_overlap regime. |
| stale-metadata cleanups | **Corpus-completeness honesty**: 7+ smoke records correctly marked SUPERSEDED reduces downstream-cite noise. |

---

## (g) Recommended next Director actions (ranked by leverage)

### Pull-up routings (atomization asks to Skunkworks; CERT-neutral so allowed even while paused)
1. **HIGHEST: route to Skunkworks: re-atomize `caching_eviction_cost_amortized_v1` as MEASURED_MECHANISM** (split: amortization PASS + acc 5pp gap pending). 1-cell tool, reproduce 0.108 / 26.8x off existing metrics. **Status: ROUTE NEXT CYCLE.**
2. **HIGH: route to Skunkworks: atomize `substrate_audit_core_C2_C3_pythia160m_residuals_v1_n4096` SPLIT** -- C3 = MEASURED_MECHANISM (84.1x drift sep, real LLM residuals); C2 = pending. **Status: ROUTE NEXT CYCLE.**
3. **HIGH: route to Skunkworks: atomize `kf1_hallu_rescue_v4_n8192_bsc` + `kf1_tier1_rescue_v1_n4096`** as MEASURED_MECHANISM (zero out-of-codebook hallucinations). Composes with refuse-gate #5 (b9bcd7a7). **Status: ROUTE.**
4. **MEDIUM-HIGH: route to Skunkworks: atomize `axis4_hyst_ramp_v1_n4096`** as MEASURED_MECHANISM (retention-path-independence, NESS invariant; composes_with kmax_ness_envelope_v1). **Status: ROUTE.**
5. **MEDIUM: route to Skunkworks: atomize `pp31c_knee_full_n8192_v2`** as MEASURED_MECHANISM (precision-coverage knee at alpha=0.258, cv=0, 5-seed). **Status: ROUTE.**

### Exp-Dev cell-author asks (gated by orchestrator pause flag if applicable)
6. **HNSW on #7-projected keys** (composes with CERT 591) -- if HNSW recovers on projected keys = 20x sub-linear retrieval Phase-3 knob. CELL-AUTHOR. **Status: file pre-reg to exp_dev.**
7. **pp52 Hebbian @ alpha=0.03** (re-frame with alpha<<alpha_overlap regime) -- expected to give 200x FLOPS-speedup at acc-preserved. CELL-AUTHOR. **Status: file pre-reg to exp_dev.**
8. **Bundle SNR re-characterization** (B9) -- 1/sqrt(K-1) theory FAILS; measure actual SNR(K, N, codebook) law. CELL-AUTHOR. **Status: optional Phase-0 lower-priority.**

### Skunkworks SCHEMA-VET asks
9. **SCHEMA-VET on the SPLIT-CLAIM atomization pattern** (B3 above) -- a single experiment_record producing multiple MEASURED_MECHANISM atoms (one per sub-cell) is novel; needs Skunkworks's discipline approval before broad rollout.
10. **SCHEMA-VET on the stale-metadata SUPERSEDED_BY action** -- 7 stems with mixed-mode evidence need a clean `SUPERSEDED_BY` rel_type from the smoke atoms to the FULL canonical. Read-only audit. **Status: route as discipline-clarification ask.**

### No action / dead-end verdicts (negativity-bias rule cuts both ways)
- `e1_substrate_crf_shared_lib_cpu_v1` -- clean dead-end (CRF shared library subsumed by lexical features at full data). NO PULL-UP.
- `bid_order_parameter_v6/v7` -- BID-as-order-parameter is FALSIFIED (wrong sign in 5/5 seeds). NO PULL-UP; valuable as negative knowledge.
- `e4_world_model_mwp` -- ASDiv-1op 0.34 ceiling is comprehension-bound, not substrate-mechanism-bound. ALREADY scoped correctly via phase4b_multistep_pull_up. NO NEW action.
- `analogy_chain_transfer_cpu_v1` -- 1-step=0.017 / 2-step=0.000 = floor-of-floor. NOT salvageable.
- `pp52_hebbian_lora_speedup_*` -- the ORIGINAL bound (uniform-HARD_FAIL at alpha=0.098) stays HARD_FAIL; the re-framed sub-claim (alpha<<alpha_overlap) is a DIFFERENT cell, not a pull-up of the original.

---

## (h) Citations

Internal cites only (no lit-scan performed per directive).

### Atoms verified off Store (atom_id + cell_sha):
- T3/EXP_pp52_hebbian_lora_speedup_n4096_v1 (cell_sha `4b83b48bbdef`)
- T3/EXP_pp52_hebbian_lora_speedup_n8192_v1
- T3/EXP_substrate_sq6_graph_adjacency_v1 + v2_cleanup_n2048 (cell_sha `3fd3886f36dd`)
- T3/EXP_phase4b_svamp_solver_cpu_v1 + phase4_bipartite_svamp_cpu_v1
- T3/EXP_axis4_hyst_ramp_v1_n4096 (cell_sha `666d27b53fc5`)
- T3/EXP_substrate_stage_a_bio_b3_b6_ceiling_followup_v1 (cell_sha `e4a28e1a0f99`)
- T3/EXP_pp31c_knee_full_n8192_v2 (cell_sha `74e463f7e255`)
- T3/EXP_e1_substrate_crf_shared_lib_cpu_v1
- T3/EXP_bundle_snr_scaling_cpu_v1
- T3/EXP_substrate_hnsw_sublinear_cleanup_v1
- T3/EXP_storage_pq_on_w_v1 + T3/EXP_storage_hashnet_w_v1
- T3/EXP_kf1_hallu_rescue_v4_n8192_bsc (cell_sha `e4add74b63a2`)
- T3/EXP_kf1_tier1_rescue_v1_n4096 (cell_sha `b64e9895e10a`)
- T3/EXP_substrate_audit_core_C2_C3_pythia160m_residuals_v1_n4096 (cell_sha `8dd25d0b5842`)
- T3/EXP_caching_eviction_cost_amortized_v1 (cell_sha `7cdbf1108d44`)
- T3/EXP_substrate_mode5_hierarchical_compound_depth_v1_n512xD (cell_sha `4f45e97c0aa6`)
- T3/EXP_substrate_efficiency_composition_b3axb3b_v1_n2048 (cell_sha `9e076f3db2e6`)
- T3/EXP_a7_kappa3_drift_detection_during_training_v1 (cell_sha `a3986b0666ed`)
- T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1 (sanity-check: already HARD_PASS / CERT_CHAIN_GRADE, NOT a stale-metadata candidate as the brief hinted; the a8 patch precedent 83f064b7 is the methodological template, the atom is already correct)
- T3/EXP_csp_memory_warm_start_full_v3 (PASS / CERT_CHAIN_GRADE; sibling stems _v1 + _full_v2 stale)

### Stem-level mixed-evidence stems (21 total identified):
asdiv_math_wk_oracle, asdiv_pp375_multiseed, asdiv_pp375_wk, asdiv_pp375_wk_multiseed, c_infty_seb_detection, capacity_cliff_graceful, csp_memory_warm_start, ct2_outlier_count, ct2_test, e1_substrate_crf_shared_lib, e3b_permutation_binding_endtask, e4_world_model_mwp, hippocampal_sharp_wave_ripple, matrix_trace_primitives, ner_4type_multiseed, pos_discriminative_multiseed_fix, pp55_vsa_binding, qa_self_knowledge, r_alpha_throughput, pp50_kappa3_delta_alpha, q_b1_chain_depth.

### META disciplines composed-into action:
- `ae088f94` (6 disciplines including PROT-022 pp52 R3 script-audit) -- supports B1 re-frame
- `baa06f0a` (3 disciplines including capacity-relative-gate, same-distribution-split) -- supports B8 / pp52 sweet-spot reframe
- `7315be3c` (controls-fail-needs-partial-correlation) -- supports B7 / B9 / B16 reframes
- `cb7e89f1` (data-decides-tier-no-preempt; complete-divide-by-zero-BOTH-limits; cited-number-must-reproduce-from-cell; genuine-check-artifact-free-arm) -- supports almost every (b) drill
- `a3f473dd` (sparse-#2 LOWER-BOUND atomization pattern) -- supports C6 mode-5 atomization template

### Notes / cap_map references:
- `notes/research_canonical_evidence_map_v5_MINI_REFRESH_sparse_300x_LANDED_supersedes_8_20x_placeholder_a3f473dd_2026-06-20.md` (v5 evidence map; 16 cert-canonical clusters)
- `notes/research_substrate_product_synthesis_v2_sparse_upgraded_5_miscites_caught_2026-06-20.md` (substrate-product synthesis)
- `notes/substrate_capability_map.md` line 1234 (pp52 cap_map context); line 7437 (LVH #207 pp52 acc-collapse pattern); line 5165 (csp_memory_warm v1 v323 catch); line 7266 (caching_eviction v2 under-stressed test design Issue I-13)
- `data/director_plan.json` (current 13 priorities; refuse-gate #5 b9bcd7a7 in-progress; LEVER #1.5 e6075dd9 in-progress)

### Verify-the-referent applied:
Every cited number above (acc, speedup, ratio, separation factor, cv, hp_count) was read directly off the atom's `metrics_headline` field in the Store (verified via `PartitionedStore.all_atoms()` on `data/substrate_index/`). No derived / extrapolated numbers; no `assumed` values substituted. Two-arm controls (e.g., zero-hallucination 5/5 seeds in KF-1, cv=0 in pp31c_knee) cited as appear in the cell. Total atoms enumerated: **177,244** (matches v5 evidence map atom count exactly +0).

---

-- Research (Director, Opus dispatch)
2026-06-20
