# Pre-registration: relational_inference_neighbor_vs_unbind_structured_cskg_v1

Filed 2026-07-14 (exp_dev). Cell: `experiments/exp_relational_inference_neighbor_vs_unbind_structured_cskg_v1.py`.
DECISIVE zero-shot held-out-RELATION inference on REAL commonsense knowledge (CSKG dense core). Decomposes agent
a6bbdfd0's "inference flat at chance" (MEASURED@data/real_kg_constraint_curve_metrics.json:taskB_infer_heldout_relation
~0.0000-0.0005) into a 2x2 factorial READOUT x CODES.

## REVISION v2 (2026-07-14, exp_dev) -- CONTROL FIX after memsmoke_v2 INCONCLUSIVE
memsmoke_v2 landed INCONCLUSIVE: the SHUFFLE positive-control "leaked" (SHUF_mrr-POP=+0.048, gate iii wanted <=0.01).
DIAGNOSIS (verified against code + MEASURED@data/exp_..._memsmoke_v2/metrics.json): the neighbor-vote MECHANISM beats
POP for NON-RELATIONAL reasons (candidate-restriction to reachable r*-tails + similarity-weighted frequency smoothing);
MEASURED RN=0.152 ~= SN=0.153 ~= codeSHUF=0.139, all >> POP=0.091 -- random codes AND a code-shuffled control BOTH
beat POP with ZERO relational content. So the OLD gate "SHUFFLE collapses to within 0.01 of POP" was UNPHYSICAL (the
non-relational neighbor floor sits ~0.05 ABOVE POP), NOT a broken run. Director hypothesis #1 (SN~=RN) CONFIRMED;
hypothesis #2 mechanism ("permutes relation labels preserving value set") REFUTED as stated -- the code permutes concept
BUNDLE vectors, not relation labels -- but its SPIRIT (a non-relational leak) is CONFIRMED. FIX (mechanism untouched;
CONTROL + BASELINE only): (a) added HOMOPHILY_NEIGHBOR (value-set-Jaccard retrieval, no learned codes = graph-homophily
baseline); (b) added SHUFFLE_VOTE_NEIGHBOR (real retrieval + freq-preserving value permutation = proper must-fail);
(c) reframed the crux to SN vs the STRONGEST NON-RELATIONAL NULL {RN/codeSHUF/HOM/voteSHUF} with a RANK-INVERSION guard;
(d) pos_controls_ok = INTEGRITY ONLY (a STRUCT~=HOMOPHILY tie is an honest VERDICT, not a control failure).
EXPECTED real-data outcome (coordinator controlled-world 2026-07-14): STRUCT ~= HOMOPHILY -- single held-out-relation is
homophily-solvable (neighbor-retrieval IS a homophily predictor). Reported STRAIGHT, NOT rescued.

## Question class + compute proportionality
Genuine substrate experiment (mechanism + controls + dispatch), NOT a lightweight directional gate. ONE structured
SGD fit per seed (the additive-map coord source) = the only heavy compute -> GPU. Everything else is cheap CPU
graph+matmul. Compute is proportional to the claim (structured-codes-enable-inference magnitude on the real task).

## The 2x2 (arms; all PAIRED on the same held-out (concept, r*, gold) query edges)
- RANDOM_UNBIND (RU): random bipolar codes x self-unbind (a6bbdfd0's op). Predicted DEGENERATE (<= marginal).
- STRUCT_UNBIND (SU): learned additive codes x self-unbind (= TransE inductive self-inference). Measured.
- RANDOM_NEIGHBOR (RN): random codes x CA3 neighbor-vote. Exact-match regime.
- STRUCT_NEIGHBOR (SN): learned codes x CA3 neighbor-vote. THE hypothesized mechanism.
Controls/refs (v2): SHUFFLE_NEIGHBOR (code/bundle-permuted, retrieval destroyed = NON-RELATIONAL NULL), SHUFFLE_VOTE_NEIGHBOR
(real retrieval + FREQ-PRESERVING value permutation = proper must-fail; head->value link destroyed), HOMOPHILY_NEIGHBOR
(value-set-Jaccard retrieval, NO learned codes = pure graph-homophily/frequency baseline), BASELINE_POP (honest marginal
floor = per-relation tail frequency), UNIFORM_CHANCE (~1/N), ORACLE_NEIGHBOR (reachability info-ceiling; strictly >= SN).
10 arms total. The 4 NON-RELATIONAL NEIGHBOR NULLS {RN, SHUF, HOM, SHUFV} share SN's mechanism but carry NO learned
relational structure -- the decisive crux is SN vs the STRONGEST of these.

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
  all arms; reported honestly. On the ideal small-vocab arena a structured advantage appears here (LOWER value-distance
  on NOVEL combos): SN novel graded 0.029 vs HOMOPHILY 0.0. On real large-vocab single-relation CSKG this is EXPECTED to
  vanish (STRUCT ~= HOMOPHILY), gated by the rank-inversion guard so a graded-only win is not over-claimed.

## PRE-REGISTERED BANDS v2 (decisive contrasts; NOT tuned on real data; reframed 2026-07-14)
(i) NECESSARY sanity -- neighbor INFERS above marginal: SN_mrr - POP_mrr >= 0.02 ; <= 0.005 => NO_INFERENCE.
(ii) THE CRUX -- STRUCTURE beats the NON-RELATIONAL FLOOR (frequency/homophily):
     (a) aggregate: SN_mrr - max(RN, codeSHUF, HOM, voteSHUF)_mrr >= 0.02 (STRUCT_OVER_NULL_MARGIN) ; <= 0.005 => TIES/LOSES.
     (b) NOVEL graded: (SN_valsim - HOM_valsim)/max(HOM_valsim,1e-4) on NOVEL >= 0.10, seed-sign consistent >= 66%.
     (c) RANK-INVERSION guard: SN novel-MRR must be >= max(null novel-MRR) - 0.02 (NOVEL_MRR_TOL), else a graded-only
         "win" the rank metric contradicts is DEMOTED (caught the memsmoke_v2 red flag: SN novel-graded led but SN
         novel-MRR=0.244 < codeSHUF=0.399). structure_adds requires (a) AND (b) AND (c) AND seed-sign.
     REFUTED if (a)<=0.005 OR (b) rel-gain<=0.02 OR (c) rank inverted.
(iii) voteSHUFFLE proper must-fail (DIAGNOSTIC, non-blocking): SHUFV_mrr - POP <= max(0.01, 0.40*(SN-POP)) => collapses
      toward POP. A high residual = high non-relational floor = INFORMATION (does NOT block the verdict).
(iv) UNBIND sanity: RANDOM_UNBIND_mrr - POP_mrr <= 0.005 (reproduces a6bbdfd0 = the READOUT, not a hard limit).
pos_controls_ok = INTEGRITY ONLY: fits finite + leak==0 + ceiling well-formed (ORACLE>=SN). NOT gated on structure
beating the null or the shuffle collapsing -- those are the SCIENTIFIC RESULT (fixes the memsmoke_v2 spurious INCONCLUSIVE).
Verdict = STRUCTURED_CODES_BEAT_HOMOPHILY | NEIGHBOR_INFERS_BUT_STRUCTURE_TIES_HOMOPHILY_REFUTED |
NEIGHBOR_INFERS_STRUCTURE_MIDDLE_BAND | NO_INFERENCE_EVEN_WITH_NEIGHBOR | MIDDLE_BAND | INCONCLUSIVE_INTEGRITY_OR_LEAK.
EXPECTED real single-relation CSKG outcome: NEIGHBOR_INFERS_BUT_STRUCTURE_TIES_HOMOPHILY_REFUTED (homophily-solvable).

## Fairness (info-ceiling; do not celebrate sub-ceiling)
ORACLE_NEIGHBOR = perfect ranking of gold WHEN the struct-neighbor voted set contains it (strict SN upper bound).
Per-relation headroom (ORACLE - SN) reported; ORACLE ~ POP for a relation => low info-ceiling (no signal to find)
=> that relation's SN result is NOT celebrated.

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds (FULL 3). Verdict HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if < expected.
- arms_differ_verified: true (>= 8 distinct score signatures asserted per seed + self-test; 10 arms, self-test got 10).
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- except SystemExit: raise BEFORE except Exception; no BaseException / no bare except (grep-gated PASS).
- crlb_n/a: "decisive band (ii) is RELATIVE (>= 10% of the random-neighbor graded metric) + seed-sign consistency ->
  robust to the unknown real value-similarity SCALE; discriminator_reachability OK by construction. Info-ceiling
  (ORACLE_NEIGHBOR) reported per relation." discriminator_reachability: true.
- baseline_in_band: POP is the honest structurally-low floor (not saturated); SN must clear it; ORACLE > SN; verified
  on the planted arena (POP 0.242, SN 0.523, ORACLE 0.588, RU 0.013).
- discriminator_survives_scale: FULL runs the a6bbdfd0 regime (dense CSKG core, n_dim=1024, k=24 = anchor_compose
  landed-code regime); self-test fires all discriminators on a planted latent-KIND arena (option C preview + B analytical).
- HP_SCOPE (v2): (i) SN vs POP; (ii) SN vs max{RN,codeSHUF,HOM,voteSHUF} aggregate + SN vs HOM on NOVEL-graded (rank-inversion-guarded); (iii) voteSHUF vs POP (diagnostic, non-blocking); (iv) RU vs POP. UNIFORM/ORACLE = refs.
- calibration_check: default_ok_for_this_regime (all bands pre-registered; fit config = anchor_compose FULL verbatim k=24/epochs=500/n_neg=128).
- cell_chunked: false (per-seed loop with write_partial checkpoint + FitCheckpoint resumable; seeds independent, one fit each).
- start_marker_written: true. crash_diagnostic_present: true (CELL_CRASHED + traceback). heartbeat_present: true (_heartbeat.jsonl).
- defensive_error_checking: passed_all_4_patterns.
- real_code_path_exercised: [fit_kge_anchor1, neighbor_scores, build_struct_bundles, compute_novel_mask] (self-test EXERCISES the real additive-map fit at k=8 on planted triples).
- substrate_signature_checked: [fit_kge_anchor1] (base/portable kwargs; advisory WARN on optional kwargs is precedented by the landed anchor_compose + isolation cells).
- functional_requirements: (1) zero-shot infer a never-stored relation-value -> neighbor-vote (CA3) over structured codes; (2) honest floor -> POP; (3) NON-RELATIONAL-null battery -> RN/codeSHUF/HOM/voteSHUF (the crux is beating the strongest); (4) proper must-fail -> voteSHUFFLE (freq-preserving value permutation); (5) info-ceiling -> ORACLE_NEIGHBOR; (6) interpolation visibility -> NOVEL stratum + graded metric + rank-inversion guard.
- composition_edges: n/a (no primitive->primitive shape adapter; single readout over codes).
- progress_logging: print_flush_true (line_buffered stdout + per-seed/per-phase flush + heartbeat). timeout>=1800 honored.

## Self-test result v2 (LOCAL .venv, ideal small-vocab planted latent-KIND arena)
SELFTEST_PASS (15s): RU=0.013(chance) SU=0.231 RN=0.241(~POP) SN=0.523(>>POP 0.242) codeSHUF=0.229 voteSHUF=0.505
HOM=0.304 ORACLE=0.588(>SN). Gates: neighbor_beats_unbind=True, hom_beats_pop=True(0.304>0.242), struct_beats_hom_novel=
True (SN novel-MRR 0.504 vs HOM 0.121 = +0.38), struct_novel_graded=True (SN novel-graded 0.029 vs HOM 0.0), ceiling_ok,
arms_differ (10 distinct sigs), fits finite, memsmoke_split_sizing_ok, vp_ok (6 validity-preflight checks). NOTE: the
DEFAULT small-vocab (vals_per_rel=16) arena is the ONE regime where structure BEATS homophily (proves the apparatus CAN
detect it); a vocab sweep (probe 2026-07-14) confirms HOM >= SN at realistic vocab (vpr>=96) -- i.e. the real CSKG
memsmoke is EXPECTED to show STRUCT ~= HOMOPHILY. decisive_selftest_verdict = NEIGHBOR_INFERS_STRUCTURE_MIDDLE_BAND
(aggregate struct-over-null thin on planted because voteSHUF inflates at small vocab; PASS gated on explicit gates).

## Dispatch
MEMSMOKE (real CSKG reduced: k_core=6, max_nodes=800, k=16, epochs=200, 1 seed) -> remote_cpu_queue, name contains
'memsmoke' (triggers MEMSMOKE_CFG via HDLAB_EXP_NAME). FULL (k_core=12 whole core, k=24, epochs=500, 3 seeds) ->
overnight_queue (GPU; the additive fit is the anchor_compose gpu1024 workload). exp_dev cannot push; orchestrator ships.
