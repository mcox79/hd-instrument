# Pre-reg: ingest-gate DECONFOUND -- within-trained-relation derivability (v3 VET promotion criterion)

Anchor: `ingest_gate_deconfound_within_relation_derivability_v1`
Script: `experiments/exp_ingest_gate_deconfound_within_relation_derivability_v1.py`
Date: 2026-07-16
Queue: remote_cpu_queue (CPU cell)

## Question (decisive)
Does the ingest-gate SURPRISE signal detect genuine semantic-UNDERIVABILITY, or just RELATION-IDENTITY
(an untrained relation row)? The v3 VET (abe682c7 / MEASURED@data/exp_ingest_gate_knee_locate_real_regime_v3/metrics.json)
found the load-bearing confound: withholding relation r* ENTIRELY makes "r* row untrained" == "facts are novel", so the
v3 KEY-AUC ~0.835 could be a pure relation-identity artifact (a random D[r*] row scores every fact high-surprise
regardless of derivability). This runs the VET's PROMOTION CRITERION: the WITHIN-TRAINED-RELATION novel-fact split.

## Design (relation-row-state held CONSTANT)
- TRAIN the r* row: fit the foundation INCLUDING a random subset (train_frac_rstar=0.5) of r*'s edges -> D[r*] trained.
- r* is a COMPOSED relation r* = ra o rb (2-hop nearest composition on v2's functional-TransE arena), so
  compositional derivability is GROUND-TRUTH by construction.
- Split HELD-OUT r* facts (row-state identical for both) by structural derivability oracle:
  - DERIVABLE   = tail t reachable from head h within reach_k=2 hops over FOUNDATION base-train edges (known path).
  - UNDERIVABLE = no such path (info to place t absent from trained structure).
  Oracle uses reachability_audit BFS over base-train ONLY (no r*, no held-out base) -> non-circular, independent of surprise.
- DECISIVE METRIC: DECONF_AUC = AUC(surprise; UNDERIVABLE vs DERIVABLE), both held-out, SAME trained r* row.
- Classes balanced within 1.5x (subsample majority) so AUC is not a class-size artifact.

## Arms (all in one cell, per seed)
1. DECONF (decisive): FOUNDATION_T (r* row trained) -> DECONF_AUC on held-out derivable-vs-underivable r*.
2. CONF-REPLAY (reproduce v3 confound): FOUNDATION_U (base-train only, r* row UNTRAINED) -> CONF_AUC = AUC(all-r* novel
   vs inferable held-out trained-rel). Must reproduce high (~v3 0.835) else the arena has no confound to deconfound.
3. POS-CONTROL (must fire): FOUNDATION_T -> AUC(random-corrupt-r* vs in-train-r*). Metric MUST separate here.
4. MUST-FAIL RANDOM-LABEL: shuffle derivable/underivable labels -> AUC ~chance (label-blind separator guard).
5. Secondary: DECONF via exact generative 2-hop path label (tighter). Reported.
6. REAL-CSKG proxy (NON-GATING): same design on real k-core; 2-hop-reachable derivability; reported for external validity.

## Envelope-fail-bands (pre-registered)
- HARD_PASS = harness-valid AND DECONF_AUC >= 0.65 (strict; chance=0.50, +0.15 margin > META_RULE_L 5% band)
  => surprise separates derivable-vs-underivable WITH row trained => semantic-novelty DECONFOUNDED from relation-identity
  => the ingest-gate surprise IS genuine semantic-novelty (CHAIN_GRADE-eligible). ROUTE TO SKUNKWORKS VET.
  BRAIN: aligned -- schema-consistent/derivable consolidates fast (low surprise), schema-inconsistent high (Tse 2007).
- MEASURED_BOUND = harness-valid AND DECONF_AUC <= 0.58 (~chance) WHILE CONF_AUC high AND POSCTRL fires
  => the v3 0.835 WAS the untrained-row artifact; surprise detects WHOLE-RELATION-ABSENCE only, NOT within-relation
  derivability. An honest bound on the foundation-builder's novelty-criterion.
  BRAIN: our surprise is COARSER than the brain's (relation-presence, not schema-composition-fit); fix = schema-
  composition-aware surprise readout.
- MIDDLE_BAND = harness-valid AND 0.58 < DECONF_AUC < 0.65 (straddle; ambiguous).
- INCONCLUSIVE = NOT harness-valid.

Harness-valid gate (ALL required): POSCTRL_AUC>=0.75, CONF_AUC>=0.70, RANDLABEL in [0.40,0.60], rstar_train_mrr>=0.30
(row genuinely trained), infer_mrr>=0.40 AND in (0.05,0.95) (foundation generalizes so derivable CAN rank),
class_balance min-frac>=0.20, all seeds OK, cardinality_ok.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds * 2 (1 synthetic block + 1 real block per seed). Verdict counts observed.
- arms_differ_verified: True (deriv/underiv/conf-novel/posctrl surprise vectors hash-distinct, META_RULE_AF).
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise BEFORE except Exception (no BaseException). Grep-gate clean.
- crlb_n/a: DECONF_AUC is a rank statistic over two measured surprise distributions; chance=0.50 self-checked by the
  RANDOM-LABEL must-fail control; no closed-form noise floor.
- discriminator_reachability: True. HARD_PASS 0.65 is on the achievable side (v3 CONF-analog hit 0.835 with an
  untrained row; the open question is whether ANY within-row signal survives). Either outcome is a clean finding.
- baseline_in_band: infer_mrr in (0.05,0.95) AND >= 0.40 (strong); rstar_train_mrr >= 0.30 (row functional).
- discriminator survives scale: multi-seed smoke (3 seeds, MANDATORY for AUC discriminator per META
  smoke_single_seed_inflates_AUC) at reduced N; FULL confirms at N=600/ep=350.
- calibration_check: default_ok_for_this_regime -- chance floor self-calibrated by RANDLABEL control; POSCTRL/CONF
  validate the metric fires; no tuned thresholds.
- real_code_path: self_test constructs AdditiveKGMap.fit/score_all/compose_entity/insert_entity + gen_composed_arena
  + derivability_labels + deconf_seed at N~16. Exercised set machine-checked. Self-test PASS.
- substrate_signature: AdditiveKGMap + fit_kge_anchor1 bound against live signature (device kwarg advisory only --
  identical to v2/v3 which shipped remote fine).
- deterministic seeding: fixed int seeds + np.random.default_rng(seed*const+offset); no hash()-seeded RNG, no list(set()).
- start_marker_written / crash_diagnostic_present / heartbeat: start-marker + CELL_CRASHED atomic metrics present;
  per-seed logs flush=True (progress_logging=print_flush_true; timeout>=1800 so required per §17).
- effective_vs_nominal / bracket / signal_shape / positive_control: N/A (no primitive-parameter sweep); the CONF-REPLAY
  arm IS the positive-control reproducing the v3 signal AT THIS REGIME (same arena, untrained row).

## Compute architecture
- Class: (b) sequential-CPU with justification. AdditiveKGMap is small-N SGD (N<=600 synthetic, <=3000 real k-core);
  arena nearest-neighbor is numpy brute-force at N<=600. No GPU batching speedup (fits are tiny; real arm is I/O + small
  SGD). Wall < 10s per synthetic fit; real-CSKG fit dominates (minutes). No sequential-dependency other than fit->score.
- Storage strategy: no_storage (retrieval-scoring only; no bundled/sharded item store).

## Positive control + must-fails (recap)
- POS-control (must fire): corrupt-r* vs in-train-r* under trained row.
- Must-fail 1: RANDOM-LABEL -> chance.
- Must-fail 2 (contrast): CONF-REPLAY must reproduce the v3 confound (else vacuous arena).

## Dispatch
- SMOKE: 3 seeds, N=400 ep=200, real max_nodes=1200 ep=120. timeout 2400s.
- FULL: 3 seeds, N=600 ep=350, real max_nodes=3000 ep=250. timeout 5400s.
- On HARD_PASS -> route to skunkworks landed-VET. Report either way with the brain-check.
