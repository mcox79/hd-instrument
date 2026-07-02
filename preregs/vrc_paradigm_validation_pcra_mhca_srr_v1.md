# vrc_paradigm_validation_pcra_mhca_srr_v1 -- VRC evaluation-paradigm validation cell

## Cell
`experiments/vrc_paradigm_validation_pcra_mhca_srr_v1.py`

## Purpose
Validate that the Verifiable-Retrieval-Composition (VRC) paradigm is a
DISCRIMINATING measurement framework on clean synthetic data. Not testing
substrate physics; testing that the METHODOLOGY itself distinguishes
mechanism-present from mechanism-ablated across three orthogonal metrics:
PCRA (Partial-Cue Retrieval Accuracy), MHCA (Multi-Hop Composition Accuracy),
SRR (Sound-Refuse Rate). If all three HARD_PASS on this cell, VRC is a valid
paradigm for substrate-native LM evaluation; subsequent VRC cells (NLP fact
stores / commercial-scale / two-paradigm vs LLM) become sound to author.

## Prior evidence
- Sonnet drill filing:
  `notes/research_optimal_substrate_native_lm_evaluation_paradigm_2026-07-02.md`
- USER-authorized 2026-07-02: "if we need a new paradigm for our substrate so
  be it, but let's make sure to build it in the most optimal way for
  performance, not to fit into any pre-existing benchmark."
- Substrate-KB concept-query 2026-07-02 (`bash tools/substrate_query.sh "VRC
  paradigm PCRA SRR MHCA verifiable retrieval composition partial-cue"`):
  top hit cosine=0.2725 = L1 partition routing (unrelated substrate topic);
  no prior VRC / PCRA / MHCA / SRR paradigm work at cosine>=0.30. NOVEL.
- Chain-grade primitives composed: SequenceMatrix S (bind_pair CG per c3
  cell-land 2026-06-22 commit a27939c5), Codebook cleanup (CG), refuse_gate
  (V_REL=256 CG per exp_substrate_refuse_gate_v_rel_extension_v1 2026-06-26
  commit 6e2ff698).

## Mechanism
Synthetic fact store: 500 (A, R, B) triples, each stored as
`bind(A_hd, R_hd) -> B_hd` in SequenceMatrix S plus registration of
{A_hd, B_hd, bind(A_hd,R_hd)} atoms in Codebook. HRR bind (real bipolar FFT-
convolution) at N_DIM=4096. Deterministic-hash bipolar vectors from
(seed, entity_string) -> +/-1 vector, so no encoder confound.

Three arms x three seeds x three metrics = 9 units of comparison (per-arm-
per-metric-per-seed = 27 data points).

**ARM_MECHANISM:** full substrate. S matrix populated with all 500 triples;
Codebook contains B atoms and query-key atoms; refuse_gate calibrated on
in-store cosine margins.

**ARM_ABLATED_RETRIEVE:** substrate has NO stored bindings (S initialized to
random matrix with matched Frobenius norm). Codebook only contains generic
distractor atoms. Tests that PCRA/MHCA gap is mechanism-genuine, not by-
construction.

**ARM_ABLATED_REFUSE:** substrate mechanism ON but refuse_gate tau=0
(always accept). Tests that SRR is the refuse_gate contribution, not incidental.

## Metrics + pre-registered bands

### PCRA (Partial-Cue Retrieval Accuracy)
Given (A, R, B) stored: query bind(A_hd, R_hd), retrieve top-1 from Codebook,
score correct if top-1 name == B_name. Evaluate on all 500 stored triples.
- **HP_PCRA HARD_PASS:** ARM_MECHANISM mean PCRA >= 0.85 (min-seed) AND
  ARM_ABLATED_RETRIEVE mean PCRA <= 0.05 (max-seed). Gap = MECH - ABL >= 0.80.
- **MIDDLE_BAND:** MECH in [0.50, 0.85) OR ABL in (0.05, 0.20].
- **HARD_FAIL:** MECH < 0.50 OR ABL > 0.20 OR gap < 0.30.

### MHCA (Multi-Hop Composition Accuracy)
Chains A -> B -> C -> D -> E stored as 4 sequential (X, R_next, Y) triples;
query only A, iterate chain_predict depth K=4 with codebook cleanup at each
step, score correct if final == E. 50 held-out chains per seed.
- **HP_MHCA HARD_PASS:** ARM_MECHANISM mean MHCA >= 0.70 (min-seed) AND
  ARM_ABLATED_RETRIEVE mean MHCA <= 0.10 (max-seed). Gap >= 0.60.
- **MIDDLE_BAND:** MECH in [0.40, 0.70) OR ABL in (0.10, 0.20].
- **HARD_FAIL:** MECH < 0.40 OR ABL > 0.30 OR gap < 0.20.

### SRR (Sound-Refuse Rate)
Two sets: IN_STORE (500 stored triples) and OOD (500 unstored triples). Score
each query's top-1 cosine margin. Calibrate tau via `calibrate_refuse_threshold`;
refuse iff margin < tau.
- **HP_SRR HARD_PASS:** ARM_MECHANISM refuse_rate_OOD >= 0.85 (min-seed) AND
  false_accept_rate_IN <= 0.15 (max-seed); ARM_ABLATED_REFUSE (tau=0)
  false_accept_rate_OOD >= 0.80 (mechanism-attributes-source verified).
- **MIDDLE_BAND:** refuse_OOD in [0.70, 0.85) OR false_accept_IN in (0.15, 0.25].
- **HARD_FAIL:** refuse_OOD < 0.70 OR false_accept_IN > 0.30 OR ABLATED_REFUSE
  false_accept_OOD < 0.70.

### VRC_PARADIGM_PASS
All three (HP_PCRA + HP_MHCA + HP_SRR) HARD_PASS. Else PARTIAL_VRC (with
per-metric verdict).

## Cardinality
- `EXPECTED_N_UNITS = 3 arms x 3 seeds = 9 units` (per-metric)
- `SEEDS = [7, 13, 19]`; `ARMS = [ARM_MECHANISM, ARM_ABLATED_RETRIEVE,
  ARM_ABLATED_REFUSE]`
- `HARD_FAIL_CARDINALITY_BREACH` if fewer units complete (META_RULE_H)
- `cardinality_ok: bool` written in metrics.json

## Discriminator-must-survive-scale
Smoke at N_DIM=4096, M=500 (full test scale for this cell). ARM_MECHANISM vs
ARM_ABLATED_RETRIEVE gap on PCRA must exceed 0.30 in smoke (mechanism-
discriminator survives at smoke config, which IS the full config here). If
gap in smoke < 0.30, ABORT full dispatch. (Smoke uses only 20 chains for
MHCA + 50 OOD queries for SRR to keep wall <60s; FULL expands to full
50 chains + 500 OOD queries.)

## Schema-vet pre-dispatch checklist
- `cardinality_ok`: verified in verdict logic (META_RULE_H)
- `arms_differ_verified`: sよha256 hash on per-arm S matrices; MECHANISM S vs
  ABLATED S should differ (META_RULE_AF)
- `final_metrics_atomicity`: "tmp_replace" via write_metrics helper
- `except SystemExit: raise` before `except Exception` in outer try
- `crlb_n/a`: no continuous quantitative floor; discriminator is
  binary-classification gap so CRLB does not apply; declared explicitly
- `baseline_in_band`: ABLATED_RETRIEVE PCRA expected ~1/M ~= 0.002 which is
  BELOW 0.05 band - this is BY DESIGN for ablation (random-matrix baseline
  MUST be near-zero to demonstrate mechanism-genuine gap). Not a
  META_RULE_AG violation because ABLATED is not the "baseline" in the
  MEASURE-MECHANISM sense - it is the CONTROL. The interpretable-in-band
  arm is ARM_MECHANISM at 0.85 (well within 0.05 < x < 0.95).
- `calibration_check`: "default_ok_for_this_regime" - synthetic bipolar
  vectors at N_DIM=4096, M=500 puts M/N=0.122 well below alpha_c capacity;
  no adaptive calibration needed
- `discriminator_reachability`: all 3 HP thresholds are on the achievable
  side of physics; ARM_ABLATED_RETRIEVE PCRA <= 0.05 achievable because
  random matrix gives cosine ~ 0 to stored atoms (chance ~ 1/500 = 0.002)
- HP_SCOPE: PCRA HP applies to (MECH, ABLATED_RETRIEVE); MHCA HP applies to
  (MECH, ABLATED_RETRIEVE); SRR HP applies to (MECH, ABLATED_REFUSE). NOT
  cross-applied.

## Functional requirements (Gate E)
1. Store (A, R, B) fact -> substrate holds it retrievably given partial cue.
   Primitive: `SequenceMatrix.bind_pair(bind(A,R), B)` + `Codebook.add`.
2. Retrieve stored B given (A, R) partial cue.
   Primitive: `S.predict_next(bind(A,R))` + `Codebook.lookup`.
3. Compose chain via multi-hop.
   Primitive: `S.chain_predict(A, depth=4, codebook=CB)`.
4. Reject OOD queries via cosine-margin gate.
   Primitive: `calibrate_refuse_threshold` + `apply_refuse`.

All 4 requirements map to chain-grade primitives -- no new mechanism.

## Wall + timeout
- Smoke wall estimate: ~5-30 min (numpy bipolar HRR at N_DIM=4096; 3 arms x
  3 seeds x reduced grid). Sonnet drill estimated <30 min local CPU.
- FULL wall estimate: same order (500 triples is trivially small). ~30 min.
- Timeout: 3600s per seed (huge margin per task).
- progress_logging: `print_flush_true` on every arm/metric completion.

## Sweep alignment (Gate A)
No sweep axis in this cell; arms are categorical (mechanism / ablated /
ablated). `sweep_alignment_verdict: N/A`.

## Composition edges (Gate C)
- `bind(A,R)` -> `S.bind_pair` input: SHAPE_MATCH (both N_DIM real bipolar).
- `S.predict_next` -> `Codebook.lookup` input: SHAPE_MATCH (both N_DIM).
- `Codebook.lookup` cosine margin -> `calibrate_refuse_threshold` input:
  SHAPE_MATCH (both scalar-per-query).
No SHAPE_MISMATCH.

## Positive-control arms (Gate D)
ARM_MECHANISM IS the positive-control reproducer for all three primitives at
this cell's regime. Prior CG evidence: refuse_gate V_REL=256 CG at N_DIM=8192;
sequence_memory bind_pair CG at N_DIM=4096 K=20. Regime here (N_DIM=4096,
M=500 pair-store) is a SHAPE_MATCH extension of both prior CG regimes.
Tolerance: PCRA >= 0.85 in MECHANISM = tolerance of 0.10 vs prior CG top1
range of ~0.90-0.95 at bipolar HRR of this capacity ratio.

## REQUIRED_FIELDS in metrics.json
- `anchor_name`, `verdict`, `verdict_msg`, `run_mode`, `elapsed_s`, `summary`
- `n_seeds`, `expected_n_seeds`, `cardinality_ok`
- `arms_differ_verified`, `arms_hashes` (per-arm S-matrix sha256)
- `per_arm`: 3 arm entries, each with per-seed PCRA / MHCA / SRR metrics
- `pcra`: {mech_min_seed, ablated_max_seed, gap, hp_pcra}
- `mhca`: {mech_min_seed, ablated_max_seed, gap, hp_mhca}
- `srr`: {mech_refuse_ood_min_seed, mech_false_accept_in_max_seed,
   ablated_refuse_false_accept_ood_min_seed, hp_srr}
- `vrc_paradigm_pass`: bool (all 3 HPs)

## Anti-bias notes
- BIAS-M (production-scale calibration): full at M=500 N_DIM=4096; no
  scaling extrapolation - smoke IS full config for capacity.
- BIAS-N (verify-referent-verdict-field): per-metric HP with gap requirements,
  not single-value.
- BIAS-Q (suspect 1.000): ARM_MECHANISM PCRA=1.0 is plausible at M/N=0.122;
  will be reported but not treated as suspect.
- BIAS-R (contamination): ARM_MECHANISM and ARM_ABLATED use the SAME query
  set + SAME seed; only the substrate storage differs.

## Ship route
- SMOKE: local_cpu_queue (USER-locked 2026-07-01: SMOKE ONLY on local; numpy
  CPU; ~5-30 min wall).
- FULL: `remote_cpu_queue` per USER-locked 2026-07-01 (local = smoke only).
  Requires Orchestrator push (harness-DENIED to exp_dev).
