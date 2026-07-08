# Pre-registration: glass_box_micro_loop_retrieve_gate_audit_requery_v1

Date: 2026-07-08
Author: exp_dev (Opus 4.8 1M, agent-spawn)
Cell: experiments/exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1.py
Anchor: glass_box_micro_loop_retrieve_gate_audit_requery_v1
Priority: director_plan.json glass_box_reasoning_loop_architecture_2026-07-08
Tier: CPU (remote_cpu_queue). NOT a GPU cell. Does not touch the encoder.

## One-line claim
A minimal GLASS-BOX reasoning micro-loop -- retrieve -> gate(self-audit) -> re-query -> commit, every hop
Merkle-audited -- in which a gated, WORKING-MEMORY-mediated re-query resolves a deliberately weak-first
retrieval regime that a single shot cannot, and the audit log is causally faithful AND hand-editable
(editing one logged step changes the downstream recompute and fires the tamper flag).

## Prior-work check (substrate KB concept-query, mandatory)
Query "glass box reasoning loop retrieve gate audit re-query working memory multi-hop self-audit merkle
tamper". Top hits:
- cosine=0.3242 PER-HOP-AUDIT engineering anchor (notes/research_drill_compliance_maximization_2x_2026-06-09.md):
  "complete hop_record for every hop; Merkle root covers full chain." -> prior DESIGN of the audit sub-component,
  NOT a landed cell running the composed loop. This cell REALIZES that anchor for its audit layer.
- cosine=0.30/0.29 multi-hop-reasoning barrier notes (assessment notes), not landed loop cells.
Verdict: the audit layer rediscovers/realizes the PER-HOP-AUDIT anchor; the COMPOSED LOOP (gated WM re-query
resolving a falsifiable weak-first regime + causal hand-edit demonstration) is genuinely novel.

## Brain grounding (notes/research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md)
- PFC->hippocampus retrieval-in-service-of-inference; the arbitration/match-mismatch signal is the
  "stop vs re-query" evaluator (thread 1). Realized as the cleanup arbitration MARGIN (top1-top2).
- Working memory holds the partial result (active slot); it is BOUND with the retrieval store to bias the
  second completion over the SAME stored weights (threads 2 + 4).
- Cortico-BG-thalamic Go/NoGo value-gate: high margin => Go (commit shot); low margin => NoGo (re-query)
  (thread 3).

## Composed certified parts (mechanism-level reuse; the GPU cells are NOT re-run)
- (A) Merkle audit-replay: exp_reasoning_chain_replay_v1 / exp_khop_audit_replay_v1 (HARD_PASS 100pct
  det/verify/tamper). Helpers `h/merkle_root/merkle_verify` transcribed verbatim (those cells run _selftest
  at import => not import-safe). This IS the glass-box wrapper.
- (B) attention-routing arbitration gate: exp_substrate_gen_lm_combinedgate_recency_content_v8 (CHAIN_GRADE).
  The arbitration margin is the same biased-competition quantity its content-relevance softmax arbitrates;
  realized here as the CPU cleanup margin (the v8 cell is GPU/not import-safe).
- (C) basal-ganglia Go/NoGo value-gate: exp_pfc_bg_composed_attention_value_gate_v1. The margin-threshold
  accept/re-query decision is the Go/NoGo actor (commit vs gather-more).

## The falsifiable weak-first regime ("B beats A" is NOT tautological)
Each trial is one of two types, MIXED so the gate cannot tell them apart a priori:
- EASY (frac_easy=0.5): answer bound DIRECTLY to the query anchor in the hop-2 store -> single shot resolves,
  HIGH margin.
- HARD (0.5): answer bound to a BRIDGE concept, not the anchor. A single shot from the anchor lands on NOISE
  (LOW margin, wrong). Only a WM-mediated re-query resolves it: retrieve the bridge from the hop-1 store
  (WM active-slot content), BIND it into the hop-2 store, unbind the answer. Up to 2 hops.
Because the two types are mixed, the arbitration-margin gate is load-bearing in BOTH directions:
- ARM_A_SINGLE_SHOT (always commit shot):        resolves EASY, fails HARD   -> acc ~ frac_easy
- ARM_ALWAYS_REQUERY (always re-query):           resolves HARD, BREAKS EASY  -> acc ~ 1-frac_easy
- ARM_B_WM_REQUERY (gated: margin>=tau => Go):    resolves BOTH               -> acc ~ 1.0
The gated loop dominates BOTH always-accept AND always-re-query. If a single shot could solve HARD trials,
ARM_A would already win and resolve_lift ~ 0 (the HARD_FAIL branch). This is MEASURED, not assumed.

## Arms (paired; all arms evaluated on the SAME trials per seed)
1. ARM_A_SINGLE_SHOT   -- one gate-fire, commit argmax. BASELINE / "loop adds nothing" null.
2. ARM_B_WM_REQUERY    -- gated: margin>=TAU => accept shot, else WM re-query. THE TEST.
3. ARM_B_SCRAMBLE      -- gated, but re-query with a RANDOM bridge code. TELEMETRY-SENSITIVITY guard.
4. ARM_ALWAYS_REQUERY  -- always re-query (never accept the shot). Isolates whether GATE ROUTING matters.
5. ARM_ORACLE_BRIDGE   -- hand the TRUE bridge to hop-2 (skip hop-1). Retrieval ceiling / positive control
                          (measured on HARD trials, where the bridge is the correct key).

## Discriminators
- resolve_lift    = accB - accA                         (loop adds real capability)
- gate_route_margin = accB - accALWAYS                  (gated routing beats always-requery)
- scramble_gap    = accB - accB_scramble                (WM content is what resolves; telemetry-sensitivity)
- gate_separation = margin(EASY) - margin(HARD)         (self-audit signal is telemetry-sensitive)
- gate_routing_acc = frac trials routed correctly       (easy->accept, hard->requery)
- oracle_bridge_acc / hop1_retrieve_acc                 (positive control + WM content correctness)
- deterministic_replay / merkle_verify / tamper_detect  (audit soundness)
- causal_edit_flip = frac HARD+correct trials where hand-editing the logged bridge (true->distractor) flips
                     the downstream recompute correct->wrong                       (glass-box hand-edit)

## Contract (bands; strictly above floor per META_RULE_L)
HARD_PASS: resolve_lift >= 0.25 AND gate_route_margin >= 0.25 AND paired sign-test p < 0.05 AND
  gate_separation >= 0.10 AND gate_routing_acc >= 0.90 AND scramble_gap >= 0.25 AND oracle_bridge_acc >= 0.90
  AND hop1_retrieve_acc >= 0.90 AND deterministic_replay == 1.0 AND merkle_verify == 1.0 AND
  tamper_detect == 1.0 AND causal_edit_flip >= 0.80 AND arms_differ.
MIDDLE_BAND: resolve_lift in [0.10,0.25) OR gate_separation in [0.05,0.10) OR causal_edit_flip in [0.50,0.80).
HARD_FAIL: resolve_lift < 0.10 (loop adds nothing) OR tamper_detect < 1.0 OR deterministic_replay < 1.0.
INCONCLUSIVE_TAUTOLOGICAL_METRIC: scramble_gap < 0.10 OR gate_separation < 0.05.
INCONCLUSIVE_RETRIEVAL_BROKEN: oracle_bridge_acc < 0.90 OR hop1_retrieve_acc < 0.90.

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = len(SEEDS); verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if completed < expected.
- arms_differ_verified: true (SHA256 of committed answer-ID streams; 4 core arms distinct).
  arms_differ_exempted: [["ARM_ALWAYS_REQUERY","ARM_ORACLE_BRIDGE"]] -- these coincide exactly when
  hop1_retrieve_acc==1.0 (retrieved bridge == true bridge), a MEASURED property not a bug.
- final_metrics_atomicity: tmp_replace (os.replace on metrics.json.tmp).
- except SystemExit: raise BEFORE except Exception (no BaseException). Grep gate: clean.
- crlb_n/a: accuracy-gap discriminator; no single closed-form noise floor. Reachability by bundle-SNR:
  hop bundle M/N = 20/4096 << capacity so a clean unbind top1 ~ 1.0; a raw-anchor unbind of a bridge-keyed
  answer is orthogonal to the codebook => argmax near chance 1/V = 1/256. Discriminator gates well inside.
  HARD noise-floor margin ~ sqrt(M/N) = 0.070; EASY clean margin ~ 0.93 THEORETICAL. TAU_GATE=0.30 between.
- discriminator_reachability: true.
- baseline_in_band: true. BASELINE = ARM_A; accA ~ frac_easy = 0.5 in (0.05,0.95). ARM_B is mechanism (ceiling ok).
- discriminator survives scale: OPTION A -- smoke holds N == FULL N (4096); full differs only in n_trials
  (40->200) and seeds (3->5). Deterministic substrate retrieval; more trials only tighten the estimate.
- calibration_check: default_ok_for_this_regime. TAU_GATE=0.30 a-priori between HARD/EASY margins; NOT tuned.
- progress_logging: print_flush_true (line-buffered stdout + flush per line + per-seed heartbeat). FULL wall << 1800s.
- cell_chunked: false (5 seeds in-cell; per-seed heartbeat + start-marker + crash-diagnostic present;
  wall ~ tens of seconds so single-cell is safe).
- start_marker_written: true. crash_diagnostic_present: true. heartbeat_present: true.
  defensive_error_checking: passed_all_4_patterns.

### Composition / sweep gates (Section 15)
- sweep_alignment_verdict: N/A (no parameter sweep axis; seeds only).
- discriminating_fraction: N/A (not a sweep). The mixed corpus is engineered so the discriminator is
  measurable by construction: accA ~ 0.5 (in band), accB ~ 1.0.
- composition_edges:
  - hop1_retrieve (WM active-slot) -> gate: SHAPE_MATCH (bridge id + margin scalar).
  - gate (Go/NoGo) -> hop2_requery: SHAPE_MATCH (accept-vs-requery boolean routes the commit).
  - hop retrieval -> Merkle audit log: SHAPE_MATCH (each hop -> one hop_record string; chained root).
- positive_control_arms:
  - ARM_ORACLE_BRIDGE reproduces clean bound retrieval AT THE TEST REGIME (N=4096, V=256, M=20);
    if oracle_bridge_acc < 0.90 => INCONCLUSIVE_RETRIEVAL_BROKEN (downstream arms untrustworthy).
  - the deterministic_replay + merkle_verify + tamper_detect == 1.0 reproduces exp_reasoning_chain_replay_v1's
    HARD_PASS (100pct det/verify/tamper) IN-CELL at this regime.
- functional_requirements:
  1. retrieve a partial result and hold it in WM        -> hop1 bundled associative unbind (bridge_hat).
  2. self-audit "can I answer yet?"                      -> cleanup arbitration margin (v8-style why-signal).
  3. decide commit vs gather-more                        -> margin-threshold Go/NoGo (BG value-gate).
  4. re-query by binding WM content into the store       -> bind(bridge_hat, hop2_store) unbind.
  5. print an inspectable + hand-editable why-trail      -> per-hop Merkle audit log (reasoning_chain_replay).

## Compute architecture
Class (b) sequential-CPU with justification: genuinely SEQUENTIAL chained retrieval (hop-2 depends on the
hop-1 WM result) AND the cell IS validating the substrate-primitive loop; wall time is a few seconds/seed
(V=256 x N=4096 cleanup is a tiny matvec). No GPU, no torch, no encoder. Storage: MIXED -- each hop is a
per-hop BUNDLED single-hop associative memory (exemption (a): pure single-hop read, no downstream composition
within a hop); cross-hop composition is SHARDED via WM re-binding (bridge carried in WM, never fused into one
global chain bundle).

## Config
FULL:    N=4096, V=256, M=20, n_trials=200, frac_easy=0.5, seeds=[7,17,23,31,41]. EXPECTED_N_UNITS=5.
SMOKE:   N=4096 (== FULL N), V=256, M=20, n_trials=40, seeds=[7,17,23].
SELFTEST:N=512,  V=32,  M=6,  n_trials=8,  seeds=[7].

## SMOKE RESULT (MEASURED, this dispatch)
MEASURED@data/exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1_smoke/metrics.json (3 seeds, full N):
- verdict: HARD_PASS (size 9822B, run_mode=smoke, cardinality_ok=true, arms_differ=true)
- accA=0.500 accB=1.000 accAlways=0.500 accScr=0.500 accOracle=1.000
- resolve_lift=0.500 gate_route_margin=0.500 scramble_gap=0.500 gate_separation~0.784 gate_routing_acc=1.000
- hop1_retrieve_acc=1.000 deterministic_replay=1.000 merkle_verify=1.000 tamper_detect=1.000
- causal_edit_flip=1.000 causal_edit_tamper=1.000 sign_p=0.0000
Every discriminator clears its HARD_PASS band by a wide margin (resolve/route/scramble each 0.50 vs 0.25 floor
= 100pct above floor; NOT floor-hugging -> genuine HARD_PASS, not MIDDLE_BAND). gate_separation varies by seed
(0.760-0.814) confirming telemetry-sensitivity.

## FULL dispatch
queue: remote_cpu_queue. timeout_s: 600 (smoke wall ~3s at 3 seeds; FULL 5 seeds x 5x trials at same N ~ tens
of seconds; 600s is a generous CPU-contention safety margin, well under the 14400 cap).
