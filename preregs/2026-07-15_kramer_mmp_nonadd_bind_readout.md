# Pre-registration: Kramer 2021 MMP nonadditivity bind-readout (conjunction MODULE #1 / real-data linchpin)

Cell: `experiments/exp_kramer_mmp_nonadd_bind_readout_v1.py`
Anchor: `kramer_mmp_nonadd_bind_readout_v1`
Date: 2026-07-15
Queue target: `remote_cpu_queue` (CPU-only; tiny fits; the ONLY heavy step is 3 CSV HTTP downloads at runtime)
Dispatched by: exp_dev (author + syntax/import check ONLY; ALL compute — download, parse, gate, self-test — runs REMOTE)

## Question
Does the substrate's LEARNED SYMMETRIC BIND (shared per-token code + elementwise-PRODUCT composition = swap-symmetric)
READ OUT a genuinely-non-additive REAL MEASURED 2-way interaction — the pairwise Nonadditivity of two substituent
transformations in a matched-molecular-pair double-transformation cycle (Kramer 2021, J. Cheminform. 13:48) — on NOVEL
held-out transformation-pairs, BEATING a capacity-matched STRONG categorical additive by a pre-registered relative-MAE
margin SPECIFICALLY on the noise-floor-cleared |Nonadd|>0.3 subset? Glass-box CPU, NO LLM at readout.

This is the properly-done REAL-DATA proof after 2 LLM-generated conjunction clusters came back additive-capturable. The
Nonadditivity is a MEASURED scalar (deviation from strict additivity of two transformations), not a narrated label.

## Data (acquire remote at runtime; download-if-absent + provenance)
Kramer 2021 supplementary CSVs (verified-live unauthenticated Springer static-content URLs; header
`ID,SMILES,VALUE,nOccurence,Nonadd_pC` per the scout drill
`notes/drill_real_nonadditive_experimental_datasets_for_conjunction_modules_2026-07-15.md`):
- `13321_2021_525_MOESM2_ESM.csv` (ChEMBL1613797)
- `13321_2021_525_MOESM3_ESM.csv` (ChEMBL1614027)
- `13321_2021_525_MOESM4_ESM.csv` (ChEMBL1613777)
Cached to `data/foundation_clusters/kramer2021_mmp_nonadd/`; provenance.json records URLs + retrieval ts + Nonadd def.

## DATA-STRUCTURE-ADAPTIVE (do NOT force a broken encoding)
- **PATH A** (per-circle / transformation columns present -> cycle constituents R1,R2 identifiable): entity = unordered
  transformation-pair (t1,t2); constituents = the two transformation tokens (namespaced per assay); target = the cycle
  Nonadditivity (continuous). Run the full transfer proof below.
- **PATH B** (per-compound aggregate only: `ID,SMILES,VALUE,nOccurence,Nonadd_pC` with no cycle/transformation columns;
  R1,R2 NOT reconstructible without RDKit + MMP fragmentation): emit
  `ESCALATE_KRAMER_PERCOMPOUND_NO_CYCLE_STRUCTURE` with a crisp diagnostic (columns, row counts, |Nonadd_pC|>0.3 fraction
  per ChEMBL assay) + hand off the scout fallback (KramerChristian/NonadditivityAnalysis per-circle output, or
  Costanzo/NCI-ALMANAC). This is an honest verdict about the dataset's ingestability — NOT a mechanism refute.
  NOTE (exp_dev author judgment, HYPOTHESIZED): the scout-reported header `ID,SMILES,VALUE,nOccurence,Nonadd_pC` is a
  per-COMPOUND aggregate; if the 3 MOESM files are exactly that, the remote run will most likely land PATH B (escalate to
  the per-circle NonadditivityAnalysis output). PATH A fires only if any file exposes transformation columns. Both paths
  are load-bearing deliverables (PATH B answers "is Kramer-per-compound bind-ingestable?" + routes the fallback).

## Arms (regression; MAE lower = better)
`LEARN_SYM` (shared code + PRODUCT = substrate symmetric bind; WINNER hypothesis); `LEARN_ADD` (shared code + SUM;
matched-capacity learned additive); `ADD_RIDGE` (closed-form ridge on per-token count design; STRONG closed-form
categorical additive); `ADD_LSTSQ` (closed-form lstsq additive); `LEARN_ROLE` (role-keyed product; algebra contrast);
`MEAN` (predict train-mean = regression frequency floor); `MEMORIZE` (per-token-pair mean; collapses to MEAN on novel);
`ORACLE` (true; MAE~0). `strong_additive = min-MAE(LEARN_ADD, ADD_RIDGE, ADD_LSTSQ)`.
`rel(stratum,subset) = (STRONG_ADD_mae - SYM_mae)/STRONG_ADD_mae`.

Strata: seen / novel token-pair (entity-level split, QUERY_FRAC=0.40). Subsets: hi=|Nonadd|>0.30 (genuine interaction) /
lo=<=0.30 (control). Regimes: CLEAN(real); ARBITRARY (random Nonadd per unique token-pair; must-fail on NOVEL); SHUFFLE
(target permutation; must-fail on ALL).

## FIXED GATE with GENUINE non-additive POSITIVE control (not saturation-vacuous)
- **Positive control** (planted symmetric-interaction arena, n=600): `pos_rel >= 0.30` — SYM beats strong additive by its
  OWN bar, proving the gate CAN detect real 2-way non-additivity (prior gates' addsynth control was saturation-vacuous).
- **Negative control** (planted ADDITIVE arena, n=600): `neg_rel <= 0.10` — SYM must NOT beat additive, proving the gate
  is NOT vacuous (a gate that always fires is worthless). Both computed inside `run_measurement` + gated.

## PRE-REGISTERED BANDS (fixed before running)
Primary metric: on NOVEL, |Nonadd|>0.30 (noise-floor-cleared) subset, CLEAN regime, mean over >=5 seeds.
- **HARD_PASS_TRANSFER** (module #1 confirmed): `novel_hi rel_MAE >= 0.30` AND `(novel_hi rel - novel_lo rel) >= 0.15`
  (advantage materially larger on hi than lo = reads chemistry not noise) AND pos-control passes AND neg-control ok AND
  must-fails fire (`SHUFFLE all rel_sym_vs_mean <= 0.08`, `ARBITRARY novel rel_sym_vs_mean <= 0.08`) AND `oracle MAE <=
  1e-6` AND leak_ok AND noise-floor cleared (`frac_hi >= 0.15`) AND `novel_hi mean n >= 4` (power).
- **HARD_FAIL_INSUFFICIENT_SIGNAL_ESCALATE**: `frac_hi < 0.15` -> too few genuinely-nonadditive cycles at this scale ->
  escalate to ChEMBL-bulk / Costanzo (domain NOT closed).
- **REFUTE_NO_TRANSFER**: `novel_hi rel_MAE <= 0.05` (collapses to noise) with valid must-fails + oracle + controls.
- **MIDDLE_BAND**: partial (`_LOW_POWER_NOVEL_HI` if `novel_hi n < 4`; `_ADVANTAGE_NOT_HI_SPECIFIC` if rel_hi clears but
  hi-lo gap does not).
- **INCONCLUSIVE_***: control gate invalid / oracle malformed / mustfail leak.

HP_SCOPE: `{LEARN_SYM: [HARD_PASS gates]}` — HARD_PASS applies to LEARN_SYM vs strong_additive only. MEAN/MEMORIZE/
ORACLE/LEARN_ROLE are contrast/ceiling/algebra arms (no chain-grade gate inherited).

## SCHEMA-VET fields
- Compute architecture: **(b) sequential-CPU with justification** — O(1e3) real cycles x tiny (<=Nx32) Adam fits (ms) +
  numpy solves; total compute wall < 3 min over 8 seeds; GPU yields no speedup on sub-ms matmuls; dominant cost = 3 CSV
  HTTP downloads (cached). torch thread-capped (HDI_TORCH_THREADS=2).
- Storage strategy: `no_storage / no_composition` (single-hop readout).
- `cell_chunked: false` (single-cell multi-seed; per-seed work is ms; runner-death loses at most one cheap run).
- `start_marker_written: true`; `crash_diagnostic_present: true` (Exception -> CELL_CRASHED metrics + traceback);
  `heartbeat_present: false` (per-seed flush `_log` lines serve as progress; total wall < 3 min compute).
- `defensive_error_checking: passed_all_4_patterns` (start-marker + crash-diag + per-seed flush + acquire/parse failure
  classes -> explicit ACQUIRE_FAILED / ESCALATE verdicts, never silent-continue).
- `final_metrics_atomicity: tmp_replace` (os.replace).
- `arms_differ_verified: true` (self-test float-hash arms-differ; ADD_RIDGE/ADD_LSTSQ exempted from strict-distinct — may
  legitimately coincide on simple data; catches bit-identical collapse of >=2 distinct arms).
- `baseline_in_band: true` — STRONG additive MAE measured (not saturated); planted pos/neg controls bound the gate.
- `discriminator_survives_scale: true` — self-test fires SYM >> strong-additive on planted-interaction SEEN at plant scale
  (n=600). Real-data novel-hi generalization is the empirical question (not asserted in self-test).
- `cardinality_ok: true` — EXPECTED_N_UNITS = n_seeds x n_regimes; per_seed_regime lengths recorded.
- `calibration_check: adaptive_with_discriminator_gate` — NOISE_FLOOR=0.30 from source-paper assay reproducibility
  (~0.3 log units, CITED@scout drill); the `hi-lo >= 0.15` gate is the discriminator-still-fires verification.
- `crlb_n/a`: regression MAE floor is data-noise-defined (no closed-form CRLB for the bilinear-readout arm); the
  NOISE_FLOOR subset + rel-MAE gate + planted controls substitute for a capacity-feasibility cap.
- Gate F.1 `real_code_path`: self-test parses SYNTHETIC per-circle rows through the REAL `detect_structure`+`parse_circles`
  parser AND runs planted arenas through the REAL `score()`/arm code; per-compound header asserted to route PATH B.
- Gate F.2/F.3 `substrate_signature`: only substrate call is `hd_bind` (long-stable base FHRR op; exercised on complex64
  phasors in self-test); no version-specific optional kwargs.
- Gate F.5 `deterministic_seeding: true` — FIXED int seeds; sorted(set()) token-pair ids; NO hash(), NO list(set())
  (queue_add PROT-023 static scan enforces).
- `progress_logging: print_flush_true` (line-buffered stdout + per-seed flush lines).
- `run_mode`: default (no flag) = FULL run to completion; `--self-test` = the remote gate (network-independent); `--smoke`
  = 3-seed measurement.

## Cardinality / feasibility
EXPECTED_N_UNITS = 8 seeds x 3 regimes = 24 per-seed-regime units (FULL). Timeout 3600s (justified: PATH A worst case
n_tok up to ~1500 -> O(n_tok^3) ridge solves x 24 calls; PATH B/escalate near-instant; download stalls + retries).

## Escalation contract
If PATH B (per-compound only) OR HARD_FAIL_INSUFFICIENT_SIGNAL (frac_hi<0.15): the verdict_msg names the fallback
(KramerChristian/NonadditivityAnalysis per-circle output first, then Costanzo yeast SGA epsilon / NCI-ALMANAC ComboScore).
Do NOT conclude the domain is closed — the mechanism is proven; the question is real-data ingestability at this source.
