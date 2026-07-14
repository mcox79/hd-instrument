# Pre-registration: relational_inference_neighbor_vs_unbind_structured_cskg_v1

Filed 2026-07-14 (exp_dev). Cell: `experiments/exp_relational_inference_neighbor_vs_unbind_structured_cskg_v1.py`.
DECISIVE zero-shot held-out-RELATION inference on REAL commonsense knowledge (CSKG dense core). Decomposes agent
a6bbdfd0's "inference flat at chance" (MEASURED@data/real_kg_constraint_curve_metrics.json:taskB_infer_heldout_relation
~0.0000-0.0005) into a 2x2 factorial READOUT x CODES.

## Question class + compute proportionality
Genuine substrate experiment (mechanism + controls + dispatch), NOT a lightweight directional gate. ONE structured
SGD fit per seed (the additive-map coord source) = the only heavy compute -> GPU. Everything else is cheap CPU
graph+matmul. Compute is proportional to the claim (structured-codes-enable-inference magnitude on the real task).

## The 2x2 (arms; all PAIRED on the same held-out (concept, r*, gold) query edges)
- RANDOM_UNBIND (RU): random bipolar codes x self-unbind (a6bbdfd0's op). Predicted DEGENERATE (<= marginal).
- STRUCT_UNBIND (SU): learned additive codes x self-unbind (= TransE inductive self-inference). Measured.
- RANDOM_NEIGHBOR (RN): random codes x CA3 neighbor-vote. Exact-match regime.
- STRUCT_NEIGHBOR (SN): learned codes x CA3 neighbor-vote. THE hypothesized mechanism.
Controls/refs: SHUFFLE_NEIGHBOR (profile-permuted, correlation destroyed; must-fail), BASELINE_POP (honest marginal
floor = per-relation tail frequency), UNIFORM_CHANCE (~1/N), ORACLE_NEIGHBOR (reachability info-ceiling; strictly >= SN).

## Codes (no leakage)
STRUCTURED = AdditiveKGMap learned coords via `fit_kge_anchor1` (k=24 TransE), fit on TRAIN edges ONLY. The specific
held-out (concept, r*, gold) triples are NEVER in the fit; concept bundle = mean_k(X[t_k]-D[r_k]) over KNOWN edges.
Leakage guard: query triples asserted disjoint from train_int (res.leak==0 required; HARD_FAIL otherwise).

## Held-out-RELATION split
Among concepts with >= k_min_rel=4 distinct relations, hold out ONE edge each as a query; the concept stays SEEN via
its other edges (a6bbdfd0's taskB framing). 90/5/5 CSKG core split via build_cskg_core_triples (reused verbatim).

## Stratification (coordinator refinement 2026-07-14) + graded metric
- NOVEL vs SEEN: SEEN if some TRAIN concept sharing >= match_min=2 EXACT known edges with the query concept ALSO has
  (r*, gold) (=> exact-match retrieval can fire); NOVEL otherwise (only graded interpolation can help). match_min=2
  avoids counting a coincidental single-edge overlap as reachable (self-test: balanced ~240/260 split).
- GRADED value-similarity: NEUTRAL, arm-agnostic train-graph neighbor-set Jaccard between predicted-top1 tail and
  gold (credits predicting a semantic neighbor of the true value). Purely-categorical relations => tiny Jaccard for
  all arms; reported honestly. The structured advantage is expected here (LOWER value-distance on NOVEL combos), NOT
  in exact hit@1 (validated on the planted arena: SN novel graded 0.029 vs RN 0.0).

## PRE-REGISTERED BANDS (decisive contrasts; NOT tuned on real data)
(i) INFERS: STRUCT_NEIGHBOR_mrr - POP_mrr >= 0.02 (HARD-PASS) ; <= 0.005 => NO_INFERENCE.
(ii) STRUCTURE_ADDS (headline; NOVEL stratum, graded): (SN_valsim - RN_valsim)/max(RN_valsim,1e-4) on NOVEL >= 0.10
     AND seed-sign consistent in >= 66% of seeds (HARD-PASS structured-codes-enable-inference) ; relative gain
     <= 0.02 => REFUTED (structured adds nothing on the novel stratum -- the most valuable falsification).
(iii) SHUFFLE collapse (must-fail): SHUF_mrr - POP_mrr <= 0.01 (one-sided; below-marginal OK). > 0.02 => BROKEN leak.
(iv) UNBIND sanity: RANDOM_UNBIND_mrr - POP_mrr <= 0.005 (reproduces a6bbdfd0 = the READOUT, not a hard limit).
REFUTATION statement: if STRUCTURED does not beat RANDOM on the NOVEL stratum under the graded metric (rel gain <=
0.02, or seed-sign inconsistent), the structured-codes-enable-inference claim is REFUTED. Reported plainly.
Verdict = STRUCTURED_CODES_ENABLE_INFERENCE | NEIGHBOR_INFERS_BUT_STRUCTURE_ADDS_NOTHING_REFUTED |
NEIGHBOR_INFERS_STRUCTURE_MIDDLE_BAND | NO_INFERENCE_EVEN_WITH_NEIGHBOR | MIDDLE_BAND | INCONCLUSIVE(control/leak).

## Fairness (info-ceiling; do not celebrate sub-ceiling)
ORACLE_NEIGHBOR = perfect ranking of gold WHEN the struct-neighbor voted set contains it (strict SN upper bound).
Per-relation headroom (ORACLE - SN) reported; ORACLE ~ POP for a relation => low info-ceiling (no signal to find)
=> that relation's SN result is NOT celebrated.

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds (FULL 3). Verdict HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if < expected.
- arms_differ_verified: true (>= 5 distinct score signatures asserted per seed + self-test).
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- except SystemExit: raise BEFORE except Exception; no BaseException / no bare except (grep-gated PASS).
- crlb_n/a: "decisive band (ii) is RELATIVE (>= 10% of the random-neighbor graded metric) + seed-sign consistency ->
  robust to the unknown real value-similarity SCALE; discriminator_reachability OK by construction. Info-ceiling
  (ORACLE_NEIGHBOR) reported per relation." discriminator_reachability: true.
- baseline_in_band: POP is the honest structurally-low floor (not saturated); SN must clear it; ORACLE > SN; verified
  on the planted arena (POP 0.242, SN 0.523, ORACLE 0.588, RU 0.013).
- discriminator_survives_scale: FULL runs the a6bbdfd0 regime (dense CSKG core, n_dim=1024, k=24 = anchor_compose
  landed-code regime); self-test fires all discriminators on a planted latent-KIND arena (option C preview + B analytical).
- HP_SCOPE: (i) SN vs POP; (ii) SN vs RN on NOVEL graded; (iii) SHUF vs POP; (iv) RU vs POP. UNIFORM/ORACLE = refs.
- calibration_check: default_ok_for_this_regime (all bands pre-registered; fit config = anchor_compose FULL verbatim k=24/epochs=500/n_neg=128).
- cell_chunked: false (per-seed loop with write_partial checkpoint + FitCheckpoint resumable; seeds independent, one fit each).
- start_marker_written: true. crash_diagnostic_present: true (CELL_CRASHED + traceback). heartbeat_present: true (_heartbeat.jsonl).
- defensive_error_checking: passed_all_4_patterns.
- real_code_path_exercised: [fit_kge_anchor1, neighbor_scores, build_struct_bundles, compute_novel_mask] (self-test EXERCISES the real additive-map fit at k=8 on planted triples).
- substrate_signature_checked: [fit_kge_anchor1] (base/portable kwargs; advisory WARN on optional kwargs is precedented by the landed anchor_compose + isolation cells).
- functional_requirements: (1) zero-shot infer a never-stored relation-value -> neighbor-vote (CA3) over structured codes; (2) honest floor -> POP; (3) correlation-necessity -> SHUFFLE must-fail; (4) info-ceiling -> ORACLE_NEIGHBOR; (5) interpolation visibility -> NOVEL stratum + graded metric.
- composition_edges: n/a (no primitive->primitive shape adapter; single readout over codes).
- progress_logging: print_flush_true (line_buffered stdout + per-seed/per-phase flush + heartbeat). timeout>=1800 honored.

## Self-test result (LOCAL .venv, planted latent-KIND arena)
SELFTEST_PASS (17s): RU=0.013 (chance) SU=0.231 RN=0.241(~POP) SN=0.523(>>POP 0.242) SHUF=0.229(<=POP, collapses)
ORACLE=0.588(>SN) ; neighbor_beats_unbind=True, struct_novel_gain=True (novel graded SN 0.029 vs RN 0.0),
shuffle_collapses=True, vp_ok=True (6 validity-preflight checks declared + pass), arms_differ (>=5 sigs), fits finite.

## Dispatch
MEMSMOKE (real CSKG reduced: k_core=6, max_nodes=800, k=16, epochs=200, 1 seed) -> remote_cpu_queue, name contains
'memsmoke' (triggers MEMSMOKE_CFG via HDLAB_EXP_NAME). FULL (k_core=12 whole core, k=24, epochs=500, 3 seeds) ->
overnight_queue (GPU; the additive fit is the anchor_compose gpu1024 workload). exp_dev cannot push; orchestrator ships.
