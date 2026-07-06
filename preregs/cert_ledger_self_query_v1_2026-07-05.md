# Pre-reg: exp_cert_ledger_self_query_v1

Date: 2026-07-05
Author: hdi_exp_dev (spawned by Director)
Design source: notes/research_self_reasoning_capability_gap_2026-07-05.md (Sec 2, Task A/B bands)
Cell: experiments/exp_cert_ledger_self_query_v1.py
Referent: data/substrate_index/meta/cert_ledger.jsonl (# KB_REFERENT declared in cell)

## What / why

FIRST narrow self-reasoning cell: the substrate reasons over its OWN cert-ledger using
its CHAIN_GRADE multi-hop KG-retrieval (KGStore, n8/U1 CERT-585). Two INDEPENDENT
discriminators (report both; do NOT collapse):

- TASK A -- CURRENCY RETRIEVAL: walk SUPERSEDED_BY edges (multi-hop) from any ledger row
  to the current (non-superseded) version. Oracle = fold_supersedes() in
  tools/cert_ledger_query.py.
- TASK B -- CONFLICT FLAGGING: group rows by referent (SAME_SUBJECT, exact-match),
  retrieve each row's cert_status (HAS_STATUS), flag genuine same-referent contradictions
  (a PASS-family tier and a FAIL-family tier where NEITHER supersedes the other).
  Brain-grounding: dorsal-ACC conflict-monitoring (van Veen 2009; Botvinick/Yeung).

Reuses hdlab.kg_traversal.KGStore UNMODIFIED. Constructed synthetic test set (multi-hop
supersedes chains depth 1-5 + 5 conflict-subject types) drives the discriminator; a real
cert-ledger sample is a false-positive check.

## Honest real-data scope (measured on disk 2026-07-05)

- 1431 ledger rows; 58 with `supersedes` set; 32 supersedes targets resolve to a real
  row-hash. ALL 32 real supersedes chains are depth-2 (no real depth>=3 chain exists).
  MEASURED@/tmp analysis (reproducible via tools/cert_ledger_query.py fold_supersedes).
- 45 atom_ids have >1 row; 12 have >1 distinct cert_status, but 11 of those are
  None-vs-assigned backfill/pending pairs (NOT tier contradictions); 1 is a resolved
  revision (supersedes link); genuine same-referent PASS-vs-FAIL unresolved conflicts on
  the real ledger are essentially ZERO. Therefore the real ledger is used as a
  false-positive check (expect 0 flags); the CONSTRUCTED set drives Task B recall.
- Consequence: genuine MULTI-HOP currency (depth>=3) is provable only on constructed
  chains; the cell reports depth>=3 accuracy separately as the multi-hop discriminator.

## Compute architecture

- Class: (b) sequential-CPU with justification. Graph is tiny (~175 entities smoke /
  larger full); the currency walk has genuine sequential dependency (hop N depends on
  hop N-1); total wall time < 10s. Seed permutes only the random codebook (E, R).
- Storage: KGStore Hebbian multi-value W (the n8/U1 CERT-585 chain-grade mechanism,
  reused unmodified). This IS the proven KG-retrieval store; no bundled-vs-sharded
  composition-collapse risk (single-hop and iterative single-follow, not bundled chain).
- Device: cpu (CUDA_VISIBLE_DEVICES="" set before torch import).

## Bands (pre-registered)

Task A (currency) HARD_PASS: substrate acc >= 0.90 AND depth>=3 multihop acc >= 0.90
  AND gap(substrate - scrambled) >= 0.50 AND scrambled <= 0.40.
Task A HARD_FAIL: substrate acc <= 0.60 OR scrambled > 0.40.
Task A MIDDLE: otherwise.

Task B (conflict) HARD_PASS: precision == 1.0 (zero FP on constructed non-conflicts)
  AND recall >= 0.90 AND scrambled recall <= 0.30 AND real false-positives == 0.
Task B HARD_FAIL: recall <= 0.30 OR precision < 1.0.
Task B MIDDLE: otherwise.

Top-level: HARD_PASS iff both HARD_PASS; HARD_FAIL iff both HARD_FAIL; else PARTIAL.

HP_SCOPE: {taskA_substrate: [HP_A_ACC, HP_A_MULTIHOP, HP_A_GAP],
           taskB_substrate: [HP_B_PRECISION, HP_B_RECALL, MAX_REAL_FP]}.
  Scrambled + naive_self + posctrl arms are floors/controls, NOT subject to HP gates.

## SCHEMA-VET fields

- cardinality_ok: true (EXPECTED_N_QUERIES / EXPECTED_N_SUBJECTS asserted per seed;
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H raised on mismatch).
- arms_differ_verified: true (META_RULE_AF; per-query prediction arrays hashed;
  taskA/taskB substrate != scrambled asserted).
- final_metrics_atomicity: tmp_replace (write_metrics; crash path uses tmp+os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / bare except; grep-gated).
- crlb_n/a: "retrieval-accuracy discriminator; no continuous noise floor. The floor is the
  scrambled-control collapse (edges permuted -> retrieval near chance), verified per seed."
- discriminator_reachability: true (HP thresholds far from the scrambled floor).
- baseline_in_band: true (META_RULE_AG; naive-return-self baseline lands in (0.05,0.95):
  MEASURED@data/exp_cert_ledger_self_query_v1_smoke/metrics.json = 0.250; scrambled near chance).
- calibration_check: adaptive_with_discriminator_gate (tau termination gate calibrated
  from ingested-graph edge/sink conf separation, logged as tau_calib; scrambled-collapse
  verifies the discriminator still fires -- not tuned-for-pass).
- positive_control_arms: ARM_POSCTRL single-hop edge recall reproduces KGStore at test
  regime; cited prior n8 CERT-585 setrecall=1.000; tolerance 0.10; if < 0.90 ->
  HARD_FAIL_POSCTRL_INVOCATION_MISMATCH (downstream suspect).
- sweep_alignment_verdict: ALIGNED (the "sweep" axis is chain depth; effective walk depth
  == nominal chain depth).
- discriminating_fraction: n/a-by-gap (discriminator is mechanism-vs-scrambled gap, not a
  per-point band; scrambled ~chance, mechanism ~1.0).
- composition_edges: SUPERSEDED_BY-walk output (row idx) -> HAS_STATUS input (row idx):
  SHAPE_MATCH (same entity codebook). SAME_SUBJECT members -> HAS_STATUS: SHAPE_MATCH.
- functional_requirements: (1) resolve current version = multi-hop SUPERSEDED_BY chain
  follow (KGStore iterative single-follow + tau gate). (2) detect contradiction =
  SAME_SUBJECT multi-value retrieval + HAS_STATUS retrieval + tier-family compare
  (lightweight symbolic layer; deeper numeric entailment is a FUTURE math-gated cell).
- cell_chunked: false (single-file; <10s; seed only permutes codebook; per-seed loop
  with start-marker + heartbeat + crash-diagnostic present).
- start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- progress_logging: n/a (timeout_s << 1800; cell runs in seconds).

## Dispatch

- SMOKE: LOCAL ONLY (USER-lock). Gate run directly (--self-test + --smoke); HARD_PASS.
- FULL: stage FULL to remote_cpu_queue via Orchestrator (push is harness-denied to exp_dev).
  Timeout estimate: 300s (cell runs in seconds; generous margin for 3 seeds + real load).
- Expected run_mode of landed FULL metrics: "full" (verify per META_RULE §16).

## SMOKE RESULT (MEASURED@data/exp_cert_ledger_self_query_v1_smoke/metrics.json, 2026-07-05)

- run_mode=smoke, N_DIM=2048, n_records=120, n_ent=175, n_queries=40, n_subjects=20.
- posctrl single-hop recall = 1.000 (54 real edges) -> KGStore reproduces at test regime.
- TaskA: substrate acc=1.000, multihop(depth>=3, n=12) acc=1.000, scrambled=0.250,
  naive_self=0.250, gap=0.750 -> HARD_PASS.
- TaskB: precision=1.000, recall=1.000 (tp=4 fp=0 fn=0 tn=16), scrambled_recall=0.000
  (collapses), real false-positives=0 (20 real subjects) -> HARD_PASS.
- tau separation = mean_edge_conf 4.20e6 vs mean_sink_conf 2.95e5 (~14x); clean gate.
- Example (multi-hop currency, depth-5): walk chain_d5_c0_r0 -> r1 -> r2 -> r3 -> r4 -> r5
  == oracle sink r5 (5 SUPERSEDED_BY hops resolved).
- Example (conflict): syn::conf::true_0 {chain_grade, hard_fail, no-link} FLAGGED;
  syn::conf::resolved_0 {hard_fail superseded-by chain_grade} NOT flagged (revision);
  syn::conf::passdiff_0 {chain_grade, measured_mechanism} NOT flagged (both PASS-family);
  syn::conf::nullpair_0 {chain_grade, None} NOT flagged (pending).
