# Pre-registration: gt_induction_fb15k237_dense_v1

STEP-1 GENERATE-AND-TEST inductive relation inference on a DENSE graph (FB15k-237).

- **Cell**: `experiments/exp_gt_induction_fb15k237_dense_v1.py`
- **Anchor**: `gt_induction_fb15k237_dense_v1`
- **Corpus**: FB15k-237 standard split at `data/fb15k237_testbed/` (train 272115 / valid 17535 /
  test 20466). `PROVENANCE.md` co-located. Self-provisioning via stdlib urllib if absent (fail-loud).
- **Filed**: 2026-07-10 by hdi_exp_dev.

## Prior-work check (concept-query before authoring)
`bash tools/substrate_query.sh "generate and test rule induction ... dense graph verifier"` top hits:
`graph_link_prediction_v1` (HARD_FAIL, cosine 0.378) = substrate-W EMBEDDING link discrimination on
ConceptNet (sparse), NOT rule induction. `exp_graph_inductive_ceiling_v1` = best-possible held-out AUC
from raw structure on SPARSE ConceptNet (motivates this cell). `ccc1_extra_fb15k237_kg_multihop_v1` /
`u1_fb15k237_ingest_eval_v1` = FB15k-237 STORAGE + TRAVERSAL/ingest of KNOWN edges, not INDUCTION of
UNKNOWN held-out edges via mined rules. `_tier5_rule_miner.py` = methodology-rule mining, unrelated.
**Verdict: GENUINELY NOVEL** -- first generate-and-test rule-INDUCTION cell with a density-contrast +
broken-verifier must-fail control on a dense KG. Not a rediscovery.

## Question
Does held-out relation inference work on a DENSE graph with generate-and-test (discrete propose-then-
verify), where every prior arc negative was on our ConceptNet slice (avg-deg 2.68, ~14x below the
density floor)? Isolates DENSITY (dense vs sparse) x MECHANISM (support+confidence VERIFIER).

## Mechanism (symbolic generate-and-test / AMIE-style)
- PROPOSE: mine L1 (fwd + inverse) + L2 PATH-COMPOSITION rules r1(A,B) AND r2(B,C) => r3(A,C) from the
  train graph via a streaming 2-path relational hash-join (hub-capped). [Design choice: symbolic
  compose, not the chain-grade bind/unbind vector operator -- keeps the DENSITY question free of
  substrate-cleanup-noise confounds; vector bind/unbind compose is a documented follow-up.]
- VERIFY (load-bearing): accept a rule only if support >= MIN_SUPPORT and confidence >= MIN_CONF
  (confidence = support_groundings / body_groundings). Keep top MAX_RULES_PER_HEAD by confidence.
- APPLY: forward-chain accepted rules from query head h; NOISY-OR aggregate confidences over rules
  proposing each candidate tail; rank filtered. STRICT protocol: gold counts as a hit ONLY if actually
  PROPOSED (unproposed gold = miss) -> the honest "did it INFER it" bar; makes ceiling exact.

## Arms
1. GT_DENSE -- generate-and-test on full FB15k-237 (candidate).
2. GT_SPARSE -- SAME mechanism/code on degree-downsampled FB15k-237 held to avg-deg ~3 (same node set +
   relation vocab; ONLY density changes). Density contrast; MUST-FAIL control.
3. POP_DEGREE -- rank by global target degree (the task-specified "rank by target degree" baseline).
   GATED baseline.
4. POP_RELFREQ -- rank by per-relation tail frequency (stronger REFERENCE baseline; reported, NOT
   gated; known-strong on FB15k-237).
5. BROKEN_VERIF -- SAME generator (full reach), SHUFFLED verifier (random per-entity score) -> random
   ranking within reachable set. MUST-FAIL control (verifier load-bearing).
6. RANDOM -- uniform random floor.

## Pre-registered bands (relational; robust to absolute calibration)
HARD_PASS (ALL four):
- beats_popdeg: GT_DENSE hits@10 >= 1.5x POP_DEGREE hits@10 AND gap >= 0.05
- density_contrast: GT_DENSE hits@10 >= 1.5x GT_SPARSE hits@10
- broken_fails: BROKEN mrr <= 0.5x GT_DENSE mrr AND BROKEN hits@1 <= 0.5x GT_DENSE hits@1
  (gated on MRR/hits@1: with median candidate set ~6-17, hits@10 is near-saturated for any method that
  proposes gold, so hits@10 is NOT a sensitive verifier discriminator -- ranking quality is)
- ceiling_ok: GT_DENSE hits@10 / ceiling >= 0.30 (ceiling = fraction of test queries with gold in the
  pre-verifier generator reach)
HARD_FAIL (ANY):
- ties_pop: GT_DENSE hits@10 < 1.2x POP_DEGREE hits@10
- no_density: GT_DENSE hits@10 < 1.5x GT_SPARSE hits@10
- broken_infers: BROKEN mrr > 0.7x GT_DENSE mrr
Else MIDDLE_BAND. A clean HARD_FAIL is VALUABLE (density + this pure-rule mechanism insufficient).

## FULL-params preview (discriminator-survives-scale; all 237 rels, MIN_SUPPORT=10, 3 seeds)
- GT_DENSE hits@10=0.288 mrr=0.212 hits@1=0.171
  MEASURED@data/exp_gt_induction_fb15k237_dense_v1_fullpreview/metrics.json:gates
- GT_SPARSE hits@10=0.000 (all 3 seeds)  MEASURED@ same
- POP_DEGREE hits@10=0.122 mrr=0.054     MEASURED@ same
- POP_RELFREQ hits@10=0.487 (ref; GT LOSES to per-relation freq -- honest FB15k-237 caveat)
- BROKEN_VERIF hits@10=0.163 mrr=0.102   MEASURED@ same
- ceiling=0.514 achieved/ceiling=0.560   MEASURED@ same
- Verdict HARD_PASS (all 4 gates), stable across seeds 7/17/23. Wall 29.9s.
Note: LOCAL preview is NOT canonical (canon = remote_cpu_queue run). Preview = scale-survival evidence.

## Compute architecture
- Class **(b) sequential-CPU with justification**: pure symbolic relational hash-joins + dict lookups;
  NO substrate vectors, NO bind/unbind matmul, nothing GPU-batchable. Rule mining is combinatorial
  graph traversal (hash-join over adjacency lists). CPU-friendly per task. Wall 29.9s FULL.
- Storage strategy: **no_storage / no_composition** (no substrate vector store; symbolic graph index).

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = 3 seeds (no parameter sweep axis). per_seed length checked.
- discriminator-fires (META_RULE_K): self-test D1 (planted rule recovered + inferred hits@1==1.0),
  D2 (broken recovers nothing), D3 (sparse fails), D4 (random-rule generator fails) -- ALL FIRE
  MEASURED@selftest stdout. On real data the density contrast + broken-fail both fire at FULL scale.
- baseline_in_band (META_RULE_AG): POP_DEGREE hits@10=0.122 in (0.05, 0.95); no arm saturates
  (max arm POP_RELFREQ=0.487 < 0.90). GT_SPARSE=0.000 is an intended MUST-FAIL control (not a
  saturation breach). baseline_in_band: true.
- strictly-above-floor (META_RULE_L): PASS gates use strict multiplicative margins (1.5x) + absolute
  gap (0.05), not bare >=.
- HP_SCOPE: {GT_DENSE: [beats_popdeg, density_contrast, ceiling_ok], BROKEN_VERIF: [broken_fails]}.
  Baselines (POP_DEGREE, POP_RELFREQ, RANDOM) inherit NO pass gate (reference arms). GT_SPARSE is the
  density must-fail control (expected 0).
- calibration_check (META_RULE_M): "default_ok_for_this_regime" -- MIN_SUPPORT=10 / MIN_CONF=0.10 are
  standard AMIE-family thresholds; the FULL preview confirms the discriminator fires at these values
  and the density contrast + broken-fail hold; not tuned-for-pass (relational gates).
- crlb_n/a: "no quantitative substrate noise floor -- this is symbolic rule ranking, not a
  capacity/argmax-noise-limited readout."
- arms_differ_verified: true (arms are distinct ranking functions over the SAME test queries; GT_DENSE
  vs GT_SPARSE vs POP_DEGREE vs BROKEN produce materially different per-arm metrics -- see preview:
  0.288 / 0.000 / 0.122 / 0.163). Not bit-identical.
- final_metrics_atomicity: "tmp_replace" (write_metrics + crash-diagnostic both write .tmp then
  os.replace).
- except-ordering: `except SystemExit: raise` then KeyboardInterrupt then `except Exception` (NOT
  BaseException). Grep-clean (no bare except / BaseException).
- discriminator-survives-scale: option (A/C) satisfied -- FULL-params preview (all rels, 3 seeds) run;
  discriminator fires (HARD_PASS) at full scale (not smoke-N).

## §13 defensive fields
- cell_chunked: false. JUSTIFICATION: the dominant cost (GT_DENSE rule mining over 272k edges) is
  seed-invariant and shared; per-seed variation is only the sparse downsample + broken shuffle (cheap).
  Chunking would 3x-waste the shared mining. Total wall 30s (no runner-zombie risk at this duration).
  Full crash-diagnostic + start-marker + heartbeat present. [FLAG for Skunkworks: multi-seed-in-one-cell
  exemption on a fast CPU cell.]
- start_marker_written: true (`_start_marker.json` at main() entry).
- crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback, tmp+replace).
- heartbeat_present: true (`_heartbeat.jsonl` per seed).
- defensive_error_checking: "passed_all_4_patterns".

## §15 test-design gates
- sweep_alignment_verdict: N/A (no parameter sweep; arms not a swept axis). ALIGNED-by-vacuity.
- discriminating_fraction: N/A (no sweep). All arms in measurable non-saturated band (0.000-0.487).
- composition_edges: PROPOSE(dict rules) -> VERIFY(dict rules) -> APPLY(dict scores) -> EVAL(ranks).
  All SHAPE_MATCH (Python dict/list structures; no primitive-shape adapter needed).
- positive_control_arms: N/A for substrate chain-grade primitives (this cell composes NO existing
  substrate primitive; symbolic). The planted-rule self-test D1/D1b IS the positive control at the
  test mechanism regime (miner recovers a known-inferable rule + infers its held-out edges hits@1==1.0).
- functional_requirements:
  1. propose held-out candidate edges  -> L1/L2 symbolic path-composition rule mining
  2. verify candidates                 -> support+confidence filter (the load-bearing piece)
  3. rank/score candidates             -> noisy-OR of accepted-rule confidences (AnyBURL/AMIE-standard)
  4. evaluate held-out inference        -> filtered STRICT hits@1/hits@10/MRR + info-ceiling

## §16 run_mode
RUN_MODE defaults to "full" (runner invokes `python -u script.py`, no argv; `--smoke` only local).
Post-dispatch verify landed metrics run_mode=="full", size>=5KB. Preview confirmed full/5152B.

## §17 progress_logging
`print(..., flush=True)` on every progress line + per-seed heartbeat. timeout < 1800s (fast cell), so
not mandatory, but satisfied: progress_logging = "print_flush_true".

## Dispatch
- Smoke: LOCAL (this author), HARD_PASS, all 4 gates, all 4 self-test discriminators fire.
- FULL: canonical run -> **remote_cpu_queue** via orchestrator (local_cpu_queue is SMOKE-ONLY per
  USER lock). Timeout 600s (FULL wall 30s local; generous for remote-CPU variance).
