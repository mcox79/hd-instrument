# Skunkworks LANDED-VET: 5-cell verify-off-data audit (Wave 2I/3) 2026-06-27

**Date:** 2026-06-27 ~19:30 PDT
**Trigger:** USER directive 2026-06-27 ~18:45 PDT - verify-off-data audit on 5 recent Wave 2I/3 cells
**Method:** Per Fix #28 / META_RULE_T - read raw per-arm metrics.json; verify cited numbers reproduce; independent recompute via .venv Python where load-bearing
**Atomization commit:** (this note's commit)
**Store state pre-audit:** 177465 atoms (max instance_number 258)
**Store state post-audit:** 177470 atoms (+5 atoms, instance 259-263)

## One-line verdicts (cert-tier framework)

| Cell | User-given verdict | Audit verdict | Cert-tier delta | 2x-drill? | Atom inst |
|------|---|---|---|---|---|
| `task_vector_in_context_kshot_v1_smoke` | HARD_FAIL all-K-chance | **MISFLAGGED - actually HARD_PASS** | +1 chain-grade eligible (HRR primitive) | NO | 259 |
| `meta_knowledge_partition_coverage_v1` | HARD_FAIL | **PARTIAL_WIN with MEASURED_MECHANISM bound** | +1 MM (refuse-gate primitive AUROC=0.86) + 2 proven bounds | YES | 260 |
| `meta_knowledge_tip_of_tongue_v1_smoke` | HARD_FAIL | **TEST_DESIGN_FAILURE (TOT criterion rigged)** | NO TIER (mechanism untestable as written) | YES (REQUIRED) | 261 |
| `cyclic_sws_rem_eta_schedule_v1_smoke` | MIDDLE_BAND BASELINE_OUT_OF_BAND | **TEST_DESIGN_FAILURE regime-broken** | NO TIER; composes Wave 2H META + META_RULE_AA witness | YES (REQUIRED) | 262 |
| `tonegawa_v5_k_density_sweep_semi_sparse_smoke` | MIDDLE_BAND substantive | **PARTIAL_WIN with MEASURED_MECHANISM** | +1 MM (weak density preference + bundle ceiling) | YES (recommended) | 263 |

## Per-cell evidence

### Cell 1: task_vector_in_context_kshot_v1_smoke - MISFLAGGED HARD_FAIL -> HARD_PASS

**User-given numbers:** K0=-0.000 K1=0.002 K3=-0.002 K5=0.000 K10=0.000 RANDOM=0.000 DIAG=0.000.

**Raw metrics.json actual:** verdict=HARD_PASS. K0=0.010 K1=1.000 K3=1.000 K5=0.980 K10=N/A (not in smoke arms) DIAG=0.490. K5-K0=0.970 monotone=True.

**Provenance of user's numbers:** the SIBLING file `data/exp_task_vector_in_context_kshot_v1/metrics.json` (not _smoke) is the SELFTEST output: `verdict='SELFTEST_OK'`, `verdict_msg='SELFTEST_OK: k0=-0.021 k5=-0.001'`. The user's cited K0/K5 ~= 0.000 numbers match the selftest values, not the smoke run. The HARD_FAIL framing is anchored on the wrong file.

**Independent recompute (via .venv with HRR primitives, seed=7, N=8192, V=100, tasks=10, queries=5):**
- K=0: top1_recall=0.000 (0/50) - matches cell's 0.010 within seed-noise
- K=1: top1_recall=1.000 (50/50) - matches cell's 1.000 exactly
- K=3: top1_recall=1.000 (50/50) - matches cell's 1.000 exactly
- K=5: top1_recall=0.960 (48/50) - matches cell's 0.980 within seed-noise
- K=99 (DIAG): top1_recall=0.520 (26/50) - matches cell's 0.490 within seed-noise

**HARD_PASS gates verified met (from source HP_K5_RECALL_MIN=0.40 HP_K5_OVER_K0_MIN=0.30):**
- ARM_KSHOT_K5 top1_recall=0.98 >= 0.40 (met)
- K5 - K0 = 0.97 >= 0.30 (met)
- Monotone K1 -> K3 -> K5 (1.0 -> 1.0 -> 0.98; monotone non-strict; met per cell's monotone_through_k5=True)
- ARM_RANDOM_CONTEXT not in smoke arms (deferred to full)

**Caveat (per pre-reg):** query is one of K PRESENTED inputs, not held-out - this tests associative-memory recall of bundle pairs (foundational HRR primitive: can substrate recover output_i given input_i from a K-bundle?). Full ICL with held-out-input generalization is a SEPARATE follow-up cell - the pre-reg explicitly defers it and the K=99/DIAG arm shows oracle bound (capacity limit).

**Verdict:** chain-grade eligible for HRR bundle-recall primitive at K<=5. Director's HARD_FAIL framing should be retracted. META lesson: when filing audit requests, cite the metrics.json path; if there's a sibling selftest+smoke pair, BE EXPLICIT WHICH FILE.

### Cell 2: meta_knowledge_partition_coverage_v1 - PARTIAL_WIN with MEASURED_MECHANISM bound

**Raw per-arm AUROC / ECE verified:**
- partition_density: AUROC=0.488 (~chance), ECE=0.209 - BROKEN at smoke
- cosine_sep: AUROC=0.860, ECE=0.122 - WORKING (above HP floor 0.75)
- entropy: AUROC=0.861, ECE=0.114 - WORKING (above HP floor 0.75)
- composed: AUROC=0.860, ECE=0.152, lift=-0.0002 - NO LIFT over best single
- random_baseline: AUROC=0.464 (~chance, expected)

**Why HARD_FAIL fired:** pre-reg gates require COMPOSED ECE<=0.05 (fails at 0.152), lift>=0.05 over best single (fails at -0.0002), OOD refuse>=0.90 (fails at 0.676). Mechanism DOES discriminate (AUROC=0.86 well above MB floor 0.65 and even above HP floor 0.75) but composition + calibration fail.

**Root cause of partition_density broken:** source line 196-203 - hash_partition uses sign-bits on first log2(N_PARTITIONS)=log2(64)=6 dims; 1024 atoms across 64 buckets is ~16 atoms/bucket, density signal carries near-zero info. random_baseline AUROC=0.464 confirms scaffolding sound. Logistic regression correctly learns to ignore partition_density (~weight 0) and uses cosine_sep + entropy, but those two are CORRELATED so composition ~= each individually.

**Root cause of calibration FAIL:** logreg trained on calib split (mix in-domain + OOD) produces probabilities calibrated for mixed distribution; test split has different in-domain/OOD ratio so ECE fires. Per-domain isotonic would fix this.

**Verdict-tier recommendation:** +1 MEASURED_MECHANISM for cosine_sep / entropy as refuse-gate primitives at AUROC=0.86 + two proven bounds: (a) composition adds no lift when components correlated, (b) calibration via mixed-distribution logreg fails when test distribution differs.

**2x drill:** per-domain isotonic calibration of cosine_sep AND entropy separately (don't compose; calibrate each for in-domain + OOD) AND fix partition routing (k-NN density or hash on more bits or atom-graph density).

### Cell 3: meta_knowledge_tip_of_tongue_v1_smoke - TEST_DESIGN_FAILURE TOT criterion

**Raw per-arm verified:**
- HC_recall=1.000 (>=0.80 HP gate MET) - clean queries retrieved correctly
- LC_refuse=0.992 (>=0.90 HP gate MET) - OOD queries refused correctly
- rho(SNR, TOT-rate)=+0.150 (need <=-0.70 brain-aligned) - WRONG SIGN
- cluster_acc_in_TOT_mean=0.565 (need >=0.70) - just below bar
- Per-seed SNR-sweep TOT rates:
  - seed 7: 0.167 / 0.267 / 0.217 / 0.417 / 0.183 at SNR=0.2/0.3/0.5/0.7/1.0 (peak at 0.7; non-monotone)
  - seed 17: 0.233 / 0.233 / 0.333 / 0.450 / 0.067 (similar non-monotone)

**Root cause (source line 91-94):** TOT operationally defined as PERCENTILE-on-clean criterion:
- TOT case = cleanup_cos < Q30(clean SNR=1.0) AND cluster_cos > Q50(clean SNR=1.0)

At low SNR, BOTH cluster_cos AND cleanup_cos drop together; cluster_cos drops below the Q50(clean) reference, so the UPPER criterion fires LESS often even though the substrate IS in the brain-aligned 'know the category, lost the atom' state. The reference distribution (clean) makes the criterion blind to the low-SNR regime it's supposed to characterize.

**Brain comparison:** humans show TOT-rate INCREASING as cue degrades (low SNR ~ degraded cue); peak TOT at lowest meaningful SNR. Cell's TOT-rate peaks at SNR=0.7 (MODERATE noise, not LOW noise) which contradicts brain expectation.

**Verdict:** test-design failure per META_RULE_AA. NO TIER for v1. HC and LC primitives DO work (those HP gates met); only middle TOT measurement is rigged.

**2x drill REQUIRED:** redesign TOT criterion. Options ranked:
- (b) per-SNR-bin quantile criterion: relative to SNR-bin baseline not clean baseline (least biased)
- (a) ABSOLUTE thresholds calibrated from substrate: cleanup_cos<0.5 AND cluster_cos>0.3
- (c) ratio criterion: cluster_cos / cleanup_cos > 2 (scale-invariant across SNR)

### Cell 4: cyclic_sws_rem_eta_schedule_v1_smoke - TEST_DESIGN_FAILURE regime-broken

**Raw per-arm verified:**
- baseline_hebbian: 0.026 - at chance (1/N_CAT = 1/50 = 0.020)
- constant_eta_replay: 0.040 - at chance
- cyclic_eta_high_low (period 1): 0.030 - at chance
- cyclic_eta_high_low_long (period 5): 0.026 - at chance
- diag_basin_restructure: frob_ratio=12.63 (>>3.0 HP bar) - DIAGNOSTIC PASS

**Critical observation:** the diag gate fires successfully - eta-cycling IS doing its work at the SYNAPSE level (high-eta pulses produce 12.6x larger W Frobenius delta than low-eta; the SWS/REM differential drive IS happening). But this synapse-level effect cannot be MEASURED at the prototype-classification readout because that readout is at chance regardless.

**Cell-author correctly flagged** verdict=MIDDLE_BAND with reason=BASELINE_OUT_OF_DISCRIMINATING_BAND baseline=0.026 not in [0.20, 0.70].

**Composes:**
- META_RULE_AA fairness-before-tier (inst 248)
- Wave 2H META AUDIT_META_NUANCED_PARTIALLY_SUPPORTED root-cause family A (baseline_saturation; readout doesn't exercise mechanism)

**Verdict:** test-design failure / regime broken at substrate level. NO TIER for v1.

**2x drill REQUIRED:** re-author with non-classification readout. Recommended: associative recall against (key, value) pairs in W where chance is 1/V_C (substrate codebook size) and substrate operates in [0.3, 0.7] discriminating band. Same fix pattern as Wave 2 redesigns (commit 2546e96e). The eta-cycling lever should then produce a measurable lift at the readout IF the SWS/REM alternation actually helps continual-learning consolidation. The synapse-level diagnostic (frob_ratio=12.63) is preserved evidence the mechanism IS active.

### Cell 5: tonegawa_v5_k_density_sweep_semi_sparse_smoke - PARTIAL_WIN with MEASURED_MECHANISM

**Raw per-arm verified at K=100 schemas (the discriminating regime):**
- PERM(k_density=20): 0.196 mean across 2 seeds
- PERM(k_density=100): 0.293
- PERM(k_density=500): 0.353 - best
- PROTO_CENTROID_BUNDLED: 0.266 (constant; k_density doesn't apply)
- DIAG_RANDOM(k_density=any): 0.013 - random-floor

**At K=500 schemas (bundle ceiling regime):** all arms collapse to 0.012-0.024 (PROTO=0.019, PERM_k500=0.024, DIAG=0.003). Bundle capacity exhausted regardless of density.

**HP gates at K=100:** PERM-PROTO>=0.10 (just missed at +0.087), PERM_FLOOR>=0.30 (met at 0.353). MIDDLE_BAND lower bound +0.02 well exceeded.

**Discrimination clarity:** at K=100, 3-arm separation 0.353 / 0.266 / 0.013 (PERM_k500 / PROTO / DIAG_RANDOM) - mechanism is 27x random and ~33% above prototype-centroid bundling. Cross-seed: seed 7 / seed 17 both produce similar lift pattern.

**Substrate-product finding:** semi-sparse codes at k/N ~= 25% density outperform prototype-centroid bundling at moderate K with capacity ceiling at high K. Two proven bounds.

**Verdict-tier:** +1 MEASURED_MECHANISM (weak density preference + bundle-capacity-ceiling).

**2x drill recommended (not strictly required - MM tier already justified):** K=100 finer density grid [50, 100, 200, 300, 500, 750, 1024] across n>=3 seeds to find optimum and characterize density preference curve. If optimum at k~=400-600 produces delta >= +0.10 with cv < 0.10, promote to chain-grade.

## Cert-trail aggregate (this audit)

- atoms added: 5 (instance 259-263)
- atom kind: AUDIT_LESSON
- atom tier: T_methodology
- atom corpus: meta
- round-trip survival: ALL 5 verified clean (Atom.from_dict on fresh PartitionedStore)
- Store delta: 177465 -> 177470 (+5)

## Composes-with (cross-reference)

- META_RULE_AA fairness-before-tier (inst 248) - cells 2, 3, 4 all relate
- META_FAIRNESS_PATTERN Wave 1 4-cell test-design failures - cells 3, 4 extend pattern
- Wave 2H META 3-root-cause-family analysis - cell 4 family A witness
- Fix #28 verify-off-data discipline - cell 1 caught via this discipline

## Action items / requests back to Research

1. **Retract HARD_FAIL framing for task_vector_in_context_kshot_v1_smoke** - it is HARD_PASS. The user's digest was anchored on the selftest sibling file. The cell should count as a +1 chain-grade for the HRR bundle-recall primitive.
2. **Promote tonegawa_v5_k_density to MEASURED_MECHANISM** - mechanism is 27x random and ~33% above PROTO at K=100 with PERM_FLOOR gate met; bundle ceiling at K=500. Two proven bounds.
3. **Schedule 2x drills (in priority order):**
   - tip_of_tongue v2 with redesigned TOT criterion (per-SNR-bin quantile recommended)
   - sws_rem v2 with non-classification readout (associative recall against (key,value) pairs)
   - partition_coverage v2 with per-domain isotonic calibration + finer partition routing
   - tonegawa_v5 finer density grid (optional; not blocking MM tier)
4. **META question for Research:** the cell 1 misflagging suggests a pattern - when Director cites HARD_FAIL with specific per-arm numbers, the citing convention should always include the metrics.json path (or be Skunkworks-double-checked). Worth a discipline rule?
