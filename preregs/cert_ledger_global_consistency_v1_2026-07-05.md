# Pre-reg: exp_cert_ledger_global_consistency_v1

Date: 2026-07-05
Author: hdi_exp_dev (spawned by Director)
Design source: notes/research_self_reasoning_next_rungs_ladder_2026-07-05.md (Sec 2, Rung 1 spec + bands)
Cell: experiments/exp_cert_ledger_global_consistency_v1.py
Referent: data/substrate_index/meta/cert_ledger.jsonl (# KB_REFERENT declared in cell)
Reuse: ~65-70% from experiments/exp_cert_ledger_self_query_v1.py (functions COPIED verbatim,
  not imported -- that module runs _selftest() + sys.exit(--self-test) at import time).

## What / why

Rung 1 of the self-reasoning ladder: extend Tier 1 (single hand-picked currency/conflict
query) to a GLOBAL SWEEP over the WHOLE supersede/tier graph. The substrate audits its OWN
cert-ledger for three structural inconsistency classes, each via its own CHAIN_GRADE KGStore
retrieval (n8/U1 CERT-585), each reported as an INDEPENDENT discriminator (do NOT collapse):

- GS-1 CYCLE DETECTION: follow SUPERSEDED_BY (multi-hop) with the currency-walk's visited-set
  break promoted to an explicit cycle flag (A supersedes B supersedes C supersedes A -> impossible).
- GS-2 FORK DETECTION: count DISTINCT current-versions a subject's rows resolve to via
  currency-walk; >1 distinct sink == two unlinked claimed lineages under one subject == a FORK.
- GS-3 TIER-MONOTONICITY: walk the LINKED chain oldest -> newest and flag a PASS-family ->
  FAIL-family regression carrying NO explicit override annotation (retrieved via HAS_OVERRIDE).
  The documented-override negative is the Goodhart/precision trap: flagging it is a HARD_FAIL.

Discriminator (all three): reuse self_query_v1's exact scrambled-SUPERSEDED_BY-target-permutation
control, unmodified. Under scramble each task's balanced-accuracy must collapse toward chance (0.5).

Brain-grounding (CITED, honest analog not task analog): Thagard Explanatory Coherence/ECHO
(joint/set-level coherence); de Kleer ATMS n-ary nogoods + Doyle TMS global-acyclicity (GS-1);
dorsal-ACC conflict-monitoring as retrieval-margin byproduct (van Veen 2009); Nelson & Narens
1990 monitoring-vs-control (the honest-scope boundary). Full citation set in the design note Sec 4.

## HONEST SCOPE (USER-LOCKED)

Nelson & Narens (1990) monitoring-not-control: this cell only ever WRITES ITS OWN metrics.json
(a report). It NEVER edits cert_ledger.jsonl, never re-labels a cert_status, never edits code,
never auto-dispatches a fix. Narrow glass-box SELF-CHECK, explicitly NOT self-improvement /
self-rewriting. Real inconsistencies found are an AUDIT BYPRODUCT reported with the honest
atom_id-collision caveat; the CONSTRUCTED overlay (not the real data) drives the discriminator.

## Honest real-data scope (measured on disk 2026-07-05)

- cert_ledger.jsonl: 1446 rows / 1362 unique atom_ids; 44 multi-row atoms (real lineage candidates).
  MEASURED@notes/research_self_reasoning_next_rungs_ladder_2026-07-05.md Sec 0.
- Real supersede-links are sparse-to-absent as resolvable row-hashes; genuine PASS-vs-FAIL
  regressions and genuine cycles are essentially ZERO on real data (same limitation self_query_v1
  disclosed). The real ledger is therefore a NULL / false-positive check; CONSTRUCTED data drives
  recall. GS-2 real fork candidates are REPORTED (unconfirmed; atom_id-collision caveat), NOT gated.
- The naive fork-heuristic 12/44 the design note measured uses a DIFFERENT definition (count
  rootless rows) than this cell's distinct-sink definition; at smoke sample-40 the loaded real
  multi-row atoms are all properly-linked revision pairs -> 0 forks by the distinct-sink method
  (MEASURED, this drill). Different, arguably-stricter definition; reported honestly, not gated.

## Compute architecture

- Class: (b) sequential-CPU with justification. Graph is tiny (~443 entities smoke); the currency
  walk has a genuine sequential dependency (hop N depends on hop N-1); total wall time ~2.6s smoke.
  Seed permutes ONLY the random KGStore codebook (E, R); the constructed graph is seed-invariant.
- Storage: KGStore Hebbian shared-W (the n8/U1 CERT-585 chain-grade KG-retrieval mechanism, reused).
  This IS the proven store; iterative single-follow, not a bundled compositional chain -> no
  bundled-vs-sharded collapse risk. N_REL extended 3 -> 4 for HAS_OVERRIDE (GS-3).
- Device: cpu (CUDA_VISIBLE_DEVICES="" set before torch import).

## Bands (pre-registered; three INDEPENDENT tasks, NOT collapsed to one)

Per task T in {GS-1, GS-2, GS-3}:
- HARD_PASS: recall >= 0.90 on constructed positives AND zero false-positives on constructed
  negatives (fp == 0) AND scrambled balanced-accuracy <= 0.65 AND
  (mechanism_balacc - scrambled_balacc) >= 0.30. PLUS the task's gated real-data null check
  (GS-1: real cycles == 0; GS-3: real silent-regressions == 0; GS-2: NOT gated -- reported only).
- HARD_FAIL: recall <= 0.60 OR any constructed fp > 0 OR scrambled balanced-accuracy > 0.75
  OR the gated real-data null check fails.
- MIDDLE_BAND: otherwise.

Top-level: HARD_PASS iff all three HARD_PASS; HARD_FAIL iff all three HARD_FAIL; else PARTIAL.
GS-1 HARD_PASS + GS-2 MIDDLE + GS-3 HARD_PASS is a legitimate honestly-reportable partial.

HP_SCOPE: {gs1_mechanism: [HP_RECALL, MAX_CONSTRUCTED_FP, MAX_SCRAMBLED_BALACC, MIN_DISCRIM_GAP,
  MAX_REAL_CYCLE_FP], gs2_mechanism: [HP_RECALL, MAX_CONSTRUCTED_FP, MAX_SCRAMBLED_BALACC,
  MIN_DISCRIM_GAP], gs3_mechanism: [HP_RECALL, MAX_CONSTRUCTED_FP, MAX_SCRAMBLED_BALACC,
  MIN_DISCRIM_GAP, MAX_REAL_REGRESSION_FP]}. Scrambled + posctrl arms are floors/controls,
  NOT subject to HP gates.

## SCHEMA-VET fields

- cardinality_ok: true (EXPECTED gs1=2*N_PER_CLASS, gs2=2*N_PER_CLASS, gs3=4*N_PER_CLASS asserted
  per seed; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H raised on mismatch).
- arms_differ_verified: true (META_RULE_AF; per-subject prediction arrays hashed; per task
  mechanism != scrambled asserted; abs(gap)>1e-9 guard).
- final_metrics_atomicity: tmp_replace (write_metrics; crash path uses tmp+os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / bare except; grep-gated, clean).
- crlb_n/a: "retrieval-accuracy discriminator; no continuous noise floor. The floor is the
  scrambled-control collapse (SUPERSEDED_BY edges permuted -> per-atom lineage walk terminates ->
  detection near chance), verified per seed. balanced-accuracy chance = 0.5."
- discriminator_reachability: true (HP thresholds far from the scrambled chance floor; measured gap 0.5).
- baseline_in_band: true (META_RULE_AG; the scrambled control is the floor -- lands at exactly
  chance balacc=0.500 for all three; mechanism at 1.000; wide separation, no saturation).
- calibration_check: adaptive_with_discriminator_gate (tau termination gate calibrated from
  ingested edge/sink confidence separation, logged as tau_calib; scrambled-collapse verifies the
  discriminator still fires -- not tuned-for-pass. sep MEASURED = 3.78e6, ~1.6x tau).
- positive_control_arms: single-hop SUPERSEDED_BY edge recall reproduces KGStore at test regime;
  cited prior n8 CERT-585 setrecall=1.000; tolerance 0.10; if < 0.90 ->
  HARD_FAIL_POSCTRL_INVOCATION_MISMATCH (downstream suspect). MEASURED smoke = 1.000 (212 edges).
- sweep_alignment_verdict: ALIGNED (no discriminating sweep axis; N_PER_CLASS is a sample count,
  not a swept discriminator; effective walk depth == constructed chain/cycle depth).
- discriminating_fraction: n/a-by-gap (discriminator is mechanism-vs-scrambled balanced-accuracy
  gap, not a per-point corruption band; scrambled at chance 0.5, mechanism at 1.0, gap 0.5).
- composition_edges: SUPERSEDED_BY walk output (row idx) -> HAS_STATUS input (row idx): SHAPE_MATCH.
  walk output -> HAS_OVERRIDE input: SHAPE_MATCH. SAME_SUBJECT membership -> walk member_set:
  SHAPE_MATCH (all share the row-entity codebook).
- functional_requirements: (1) detect impossible lineage loop = SUPERSEDED_BY multi-hop follow +
  visited-set revisit flag (walk_full cycle flag). (2) detect split lineage = distinct-sink count
  via currency-walk (KGStore iterative single-follow). (3) detect silent tier regression =
  ordered-chain walk (root->sink) + HAS_STATUS retrieval + tier-family compare + HAS_OVERRIDE
  retrieval (documented-override exemption). All three are per-atom lineage invariants: the walk is
  SUBJECT-SCOPED (terminates on leaving the audited atom's own row-set).
- discriminator_survives_scale: EMPIRICAL (option A), CORRECTED 2026-07-06. The v1 field claimed
  option B ("N_DIM=4096 FULL only sharpens fidelity; discriminator is structural, not scale-
  fragile"). That analytical claim was WRONG for the MECHANISM's argmax exactness (the scrambled
  DISCRIMINATOR gap is structural and did hold; the mechanism's retrieval exactness is not). KGStore
  is a Hebbian shared-W associative memory: retrieval fidelity is set by loading ratio
  n_triples/n_dim, NOT N_DIM alone. Smoke (337 rec, ~1348 tri) at N_DIM=2048 -> ratio 0.66; FULL
  (691 rec, ~2760 tri) at N_DIM=4096 -> ratio 0.67 -- IDENTICAL loading, so 4096 bought ZERO SNR
  over smoke, and FULL hit occasional override/status argmax collisions (GS-3 constructed_fp=2
  seed 23; recall 0.95 via a seed-7 FN). FIX: FULL N_DIM 4096 -> 8192 (ratio 0.34). VERIFIED
  option-A at full-N across all three seeds [7,17,23] via the cell's own retrieval functions
  (MEASURED@scratchpad/probe_result.txt, disk-verified): status_err=0/691 all seeds,
  override_err=0-1/691 (verdict-irrelevant), gs3 fp=0 recall=1.000, gs1/gs2 fp=0 recall=1.000.
  N_DIM=16384 (ratio 0.17) drove override_err to 0/691 but was too slow (O(n_dim^2) score_all
  x O(n_rows); self-test alone > 5 min) -- 8192 is the pragmatic choice meeting the target FP fix.
- cell_chunked: false (single-file; ~2.6s; seed only permutes codebook; per-seed loop with
  start-marker + heartbeat + crash-diagnostic present).
- start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- structured_gate_claims: true (adopts the Tier-2 gate_claims field via record_gate; 15 gates
  written; contributes to the gate_claims adoption wave that Rung 3 is sequenced behind).
- progress_logging: print_flush_true (timeout_s << 1800; cell runs in seconds; per-seed progress
  line + all VERDICT prints flush=True regardless).

## Design refinement during smoke (transparent; NO band change)

Smoke v1 (monotonicity walk followed SUPERSEDED_BY GLOBALLY) gave GS-3 = MIDDLE_BAND: mechanism
balacc 1.000 but scrambled balacc 0.683 (> the 0.65 HP floor). Root-cause inspection: under
scramble the walk wandered OUT of the audited atom into unrelated atoms' rows and injected foreign
PASS/FAIL statuses (scrambled tp=6, fp=7). A per-atom lineage invariant must depend ONLY on that
atom's own rows -- the global walk was a genuine scoping imprecision, wrong independent of any
verdict. Fix: SUBJECT-SCOPE the walk (terminate on leaving the subject's member-set), applied
UNIFORMLY to all three heads (a lineage invariant is always within-subject). Mechanism results
unchanged (recall 1.0, fp 0 preserved); GS-3 scrambled collapsed 0.683 -> 0.500. The
pre-registered BANDS were NOT changed -- only the detector scope was corrected. This is design
refinement in the smoke-iteration phase, not threshold-tuning-for-pass.

## SMOKE RESULT (MEASURED@data/exp_cert_ledger_global_consistency_v1_smoke/metrics.json, 2026-07-05)

- run_mode=smoke, N_DIM=2048, seed=1, n_records=337, n_ent=443, n_edges=212, elapsed=2.62s, size=7584B.
- posctrl single-hop recall = 1.000 (212 edges) -> KGStore reproduces at test regime.
- GS-1 cycle:        mechanism balacc=1.000 recall=1.000 fp=0 | scrambled balacc=0.500 recall=0.000 -> HARD_PASS. real cycles=0.
- GS-2 fork:         mechanism balacc=1.000 recall=1.000 fp=0 | scrambled balacc=0.500 spec=0.000 -> HARD_PASS. real fork candidates=0 (reported).
- GS-3 monotonicity: mechanism balacc=1.000 recall=1.000 fp=0 | scrambled balacc=0.500 recall=0.000 -> HARD_PASS. real regressions=0.
- All 15 structured_gate_claims gate_verdict=True. gap=0.500 for all three (>= MIN_DISCRIM_GAP 0.30).
- Goodhart trap correctly avoided: the documented-override chain (PASS->FAIL WITH override) is
  NOT flagged (T4b selftest asserts it; GS-3 fp=0 over all 30 negatives incl. 10 override chains).
- Real audit (sample-40): 20 real subjects, all multi-row, all properly-linked revision pairs ->
  0 cycles, 0 forks, 0 regressions (honest null; the loaded real pairs are consistent).
- Overall verdict: HARD_PASS (all three independent tasks HARD_PASS).

## v1.1 FIX (2026-07-06): FULL PARTIAL -> N_DIM capacity fix

- v1 FULL landed PARTIAL (MEASURED@scratchpad/PARTIAL_canonical_metrics_backup.json, backup of the
  landed data/exp_cert_ledger_global_consistency_v1/metrics.json): GS-1 HARD_PASS, GS-2 HARD_PASS,
  GS-3 HARD_FAIL with constructed_fp=2. Disk-verified the two FP were at seed 23 ONLY (fp=0 at
  seeds 7,17); the FP subjects were override_2 (a documented-override negative) AND upgrade_18 (a
  FAIL->PASS negative -- NOT an override form). GS-3 recall was 0.95 (a seed-7/17 FN on regress_9/
  regress_c). real_fp=0 (the real ledger has override=False on all rows and produced ZERO GS-3
  flags -- so the failure was NOT "real-ledger override forms the check misses"; it was constructed-
  set retrieval noise on ONE seed).
- ROOT CAUSE: KGStore Hebbian loading (see discriminator_survives_scale above). The seed-7 FN =
  override-misretr(False->True) made a genuine silent regression look documented; the seed-23 FPs =
  override-misretr(True->False) + a status-misretr made negatives look like silent regressions.
  Both the override exemption LOGIC and the PASS->FAIL detection LOGIC are correct; the argmax
  RETRIEVALS they call collided under capacity starvation. NOT a Goodhart/over-flag boundary.
- FIX: FULL N_DIM 4096 -> 8192 (regime-only; GS-1/GS-2/GS-3 detection LOGIC byte-identical). Also
  deduped a doubled calibrate_tau() call (perf; same tau value). Smoke regime unchanged (N_DIM=2048).
- POST-FIX VERIFICATION (this drill): --self-test PASS at 8192 (114s; constructed-set fp=0
  recall>=0.90 hold). --smoke HARD_PASS (gs3 fp=0 recall=1.000). probe (cell's real functions,
  full-N, 3 canonical seeds) -> gs3 fp=0 recall=1.000 status_err=0 override_err=0-1 (verdict-
  irrelevant); gs1/gs2 fp=0 recall=1.000. Local FULL at 8192 -> [pending / see report].

## Dispatch

- SMOKE: LOCAL ONLY (USER-lock), run directly (--self-test + --smoke); HARD_PASS at N_DIM=2048.
- FULL: STAGE to remote_cpu_queue via tools/queue_add.py (SCP/sync propagation owned by
  orchestrator). Re-dispatches the SAME anchor (cert_ledger_global_consistency_v1) at N_DIM=8192
  via --allow-duplicate; the corrected FULL replaces the PARTIAL landing. The cell declares
  KB_REFERENT data/substrate_index/meta/cert_ledger.jsonl; the remote referent-staleness gate that
  PARKED v1 is FIXED as of the 2026-07-06 queue_add.py deploy, so this cert_ledger-referent cell
  dispatches cleanly now.
  Timeout: 1800s (self-test-at-import ~114s at 8192 + 3 seeds full at 8192; generous margin;
  triggers section 17 flush requirement -- SATISFIED: per-seed progress prints flush=True +
  _heartbeat.jsonl). Anchor has no _n suffix so PROT-018/019 do not gate.
- Expected run_mode of landed FULL metrics: "full" (verify per META_RULE section 16).
