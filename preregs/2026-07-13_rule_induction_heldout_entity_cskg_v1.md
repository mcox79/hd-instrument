# Pre-reg: RULE-INDUCTION on the held-out-ENTITY CSKG arena (2026-07-13)

Anchor: `rule_induction_heldout_entity_cskg_v1`
Script: `experiments/exp_rule_induction_heldout_entity_cskg_v1.py`
Trigger: drill `notes/research_drill_neurosymbolic_logical_inference_theories_2026-07-13.md` (ranked #1 mechanism).

## Question
Do statistically-mined length<=2 Horn rules (AnyBURL/RuleN-style path-counting, ZERO training, pure graph
statistics) applied by the substrate's proven forward-chaining primitive with EXACT adjacency (oracle) grounding
predict HELD-OUT-ENTITY relations better than random / frequency / a SHUFFLED-rule must-fail, on the SAME arena
the additive map-builder scored 0.128 MRR? A learned RULE is entity-invariant reusable structure (confidence
indexed by RELATION not entity) -> generalizes to unseen entities by construction, sidestepping the per-entity-
code capacity wall that closed learned-SR / additive-TransE / structure-aware-encoder (all EMBEDDING-family).
This is the first NON-embedding mechanism class against that wall.

## Mechanism (reuses proven substrate apparatus, unchanged)
- `mine_rules` (exp_gt_induction_fb15k237_dense_v1): AnyBURL path-counting L1F/L1I/L2, conf = support/body_count.
- `propose`: forward-chain + noisy-OR aggregate over EXACT adjacency of (train + held-out entity's SUPPORT edges).
- Grounding uses an exact adjacency dict (oracle lookup), deliberately isolating this from the already-closed
  learned-router SNR wall (CITED@notes relational_capability_track_record_scour_2026-07-10 bucket D).

## Arms (PAIRED on same held-out QUERY edges + same all-N candidate set + same filtered eval)
- RULE_INDUCT  : rules mined on g_train, grounded on g_train+support. MECHANISM.
- RULE_SHUFFLE : same rules, body-pattern -> HEAD-relation mapping DERANGED (conf/counts identical). MUST-FAIL.
- RANDOM       : uniform random over all N. Null.
- BASELINE_POP : per-relation tail frequency. Held-out tails train-freq 0 -> floor.
- RULE_ORACLE  : rules mined+grounded with held-out folded in. Positive control / arena-answerable ceiling.

## Bands (primary metric = filtered MRR rank-vs-all-N, degree-unbiased; reach@2 reported per the drill)
- ORACLE-FIRES: RULE_ORACLE_mrr >= 3x RANDOM_mrr AND headroom >= 0.003.
- HARD-PASS: (RULE_INDUCT - RULE_SHUFFLE)_mrr >= 0.05 (drill real-vs-shuffled) AND (RULE_INDUCT - RANDOM)_mrr
  >= 0.05 AND ORACLE fires AND shuffle controlled AND not broken.
- HARD-FAIL: (RULE_INDUCT - RULE_SHUFFLE)_mrr <= 0.02 with ORACLE firing (clean negative: pure symbolic rule
  induction, zero embedding capacity, still cannot beat shuffled/memoryless -> bottleneck is KG relation content).
- MIDDLE: margin in (0.02, 0.05) or relation/degree-dependent partial signal.
- Corroboration: margin also reported as fraction of MEASURED oracle headroom H; degree-stratified (low/mid/high
  + fair low+mid) for weak-point localization + degree-confound control.

### Reachability (discriminator_reachability = TRUE)
The drill's absolute 0.05 MRR margin is REACHABLE on THIS arena: MEASURED@data/exp_anchor_compose_inductive_
entity_cskg_v1/metrics.json:gates.heldout_mrr ORACLE_ADDITIVE=0.13729, ANCHOR_COMPOSE=0.12821, RANDOM_CODES=
0.00048 -> oracle headroom H~0.137 >> 0.05. NOT the low-ceiling trap.

## Reference lines (tagged)
- additive ANCHOR_COMPOSE mrr = 0.12821  CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json
- ORACLE_ADDITIVE mrr        = 0.13729  CITED@same
- RANDOM_CODES mrr           = 0.00048  CITED@same

## Falsifiable predictions (from the drill; calibration-penalized)
- P(HARD-PASS, margin>=0.05) = 0.22 ; P(HARD-FAIL, <=0.02) = 0.38 ; P(MIDDLE) = 0.30 ; P(control-fails) = 0.10.
  HYPOTHESIZED@notes research_drill_neurosymbolic_logical_inference_theories_2026-07-13.md.

## SMOKE (self-test, VALIDITY_PREFLIGHT_MODE=enforce, planted rule arena, real mine_rules+propose path)
MEASURED@data/exp_rule_induction_heldout_entity_cskg_v1_selftest/metrics.json:mechanism_selftest --
RULE_INDUCT mrr=0.2623 reach@2=0.2474 | RULE_SHUFFLE mrr=0.0134 reach@2=0.0 | RANDOM mrr=0.0378 | POP mrr=0.0232
| RULE_ORACLE mrr=0.4488 reach@2=0.4433 ratio=11.9x | vs_shuffle=0.2489 vs_random=0.2245 | n_distinct_sigs=5 |
validity_preflight_ok=True (6 checks: positive_control, metric_moves, negative_control_margin, full_gates,
real_code_path, guard_baseline_valid) | aggregate verdict on planted = HARD_PASS_RULE_INDUCTION_GENERALIZES.
Top mined rules (glass-box): `rC(x,z) <= rA(x,y) & rB(y,z)` conf=1.000 supp=221 ; `rF(x,z) <= rD(x,y) & rE(y,z)`
conf=1.000 supp=242.

## SCHEMA-VET pre-reg fields
- compute_architecture: (b) sequential-CPU (pure graph statistics; no matmul/GPU primitive; device=cpu).
- storage: sharded (adjacency dicts; each entity/edge indexed individually).
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (3 for FULL); >=4 distinct arm sigs asserted per seed.
- final_metrics_atomicity: tmp_replace (write_metrics + write_partial os.replace).
- crlb_n/a: not a noise-floor cell; discriminator_reachability=TRUE via MEASURED oracle H=0.137 (above).
- baseline_in_band: RULE_ORACLE must fire (>=3x RANDOM + headroom>=0.003); RANDOM/POP near 1/N floor.
- discriminator_survives_scale: analytical (B) -- a shuffled rule cannot chain via the RIGHT relation pattern by
  construction, so the real-vs-shuffled margin is structural, N-independent; ORACLE-fires proves metric moves.
- calibration_check: adaptive_with_discriminator_gate (MIN_SUPPORT=3/MIN_CONF=0.05/frac pre-registered, not tuned).
- arms_differ_verified: True (5 arms, >=4 distinct sigs).
- guard_baseline_validated: BROKEN_SHUFFLE_BEATS_INDUCT compares SHUFFLE to RULE_INDUCT (validated above RANDOM
  floor), NOT to POP (F.4 anti-mis-fire).
- real_code_path_exercised: [Graph, mine_rules, propose, build_heldout_entity_split_ac] (self-test at N~280).
- progress_logging: print_flush_true (timeout>=1800).

## Dispatch
- SMOKE (remote_cpu): reduced core (k_core=8, cskg_max_nodes=4000), 1 seed, n_heldout_eval=800, timeout 1800s.
- FULL (remote_cpu): full core (k_core=12), seeds [7,13,17], n_heldout_eval=3000, timeout 7200s.
