# Pre-registration: Costanzo yeast SGA native gene-pair epistasis -> symmetric-bind transfer proof (2026-07-15)

Author: hdi_exp_dev. Fixed BEFORE running. Native-pair real-data linchpin (conjunction module). Cell:
`experiments/exp_costanzo_epistasis_nativepair_bind_readout_v1.py`. All compute REMOTE; the network-independent remote
`--self-test` (planted arenas) is the gate.

## REVISION 2026-07-15b -- SIGNAL-READABILITY GATE added (VET a57067090 revival criterion)
The v1 run REFUTED, but VET a57067090 adjudicated it a NARROW encoding/SNR null, NOT a thesis refutation: at cells/pair~1.8 the
per-pair epsilon is noise-dominated and the strong additive beat a MEAN-predictor by only ~2.9% -- so NO readable non-additive
target existed and SYM was never given a readable target. This revision adds a SIGNAL-READABILITY GATE as the FIRST
interpretability gate and readable-slice SNR levers so the SYM-vs-additive comparison is interpretable BEFORE it is scored.

## Why the switch from ALMANAC (FIRM CAP honored)
NCI-ALMANAC's CellMiner file is a human-formatted PRESENTATION spreadsheet with three compounding format quirks (combo-score
payload is an xlsx nested in the outer zip; a CellMiner banner/title preamble sits above the real header; the ComboScore is
WIDE-format across ~60 footnote-suffixed per-cell-line columns, not one long column). Per the firm no-3rd-ALMANAC-parser cap,
switched to Costanzo 2016 yeast SGA -- a CLEAN machine-readable research TSV (zip of tab-delimited .txt), native-pair by
construction, no xlsx/banner/wide traps.

## Prior-work check
Same arc as `exp_kramer_mmp_nonadd_bind_readout_v1` (chem, fragmentation-blocked) and `exp_almanac_synergy_nativepair_bind_
readout_v1` (ALMANAC, format-blocked). The LLM-generated `exp_epistasis_bind_readout_integration_v1` / `exp_generated_
epistasis_nonadditive_v1` used NARRATED class-pair severity -- the failure mode the pivot rejects. This cell is genuinely
novel: first REAL-MEASURED continuous native-pair epistasis ingest (query_gene x array_gene + measured epsilon), no narration.

## Pocket / data (provenance/versioning per module-registry conventions)
- Source: Costanzo et al. 2016, Science 353:aaf1420; thecellmap.org/yeast/costanzo2016. Retrieval (URLs orchestrator
  web-verified 2026-07-15 -- filenames carry NO "Data File S1." prefix): ACQUIRE tries the PAIRWISE zip (521MB, drop-in for
  parse_costanzo) first, then the MATRIX zip (35MB, lighter; parse_costanzo_matrix reads the gene-x-gene symmetric epsilon
  matrix, |eps|-only filter since matrix has no p-value) as an in-cell fallback if the large pairwise download fails/stalls;
  honest ACQUIRE_FAILED with the tried-URL errors if both fail. Cell records `provenance.json` (kind, url_used, urls_tried,
  retrieval_ts, bytes, filter, slice controls, epsilon definition) in `data/foundation_clusters/costanzo2016_sga/`.
- Entity = native (query_gene, array_gene) pair (canonical unordered; tokens = systematic ORF ids extracted from strain-id
  prefix, e.g. 'YAL001C_tsq123' -> 'YAL001C').
- Constituents = the two genes.
- Held-out TARGET = the MEASURED genetic-interaction score epsilon (double-mutant fitness minus the expected multiplicative
  product of the two single-mutant fitnesses), aggregated to one scalar per ORF-pair (mean epsilon over multi-strain rows).
  Continuous regression target (MAE); NOT a narrated label.
- Tractability + capacity + READABLE-SLICE SNR levers (REVISION 2026-07-15b): filter to STRINGENT-confidence measured
  interactions |epsilon| > 0.12 (RAISED from 0.08 -> Costanzo stringent tier, stronger cleaner eps) AND p < 0.05; require
  >= 2 replicate measurements per ORF-pair (MIN_CELLS_PER_PAIR=2; drop the noisiest singletons -> mean-of->=2 = cleaner per-pair
  target); restrict to a DENSER subnetwork (top-400-frequency ORFs, RAISED density from 500) capped at 8000 pairs so per-token
  main effects are better-defined. These levers raise per-pair SNR to give a readable non-additive target its best chance.
- Why genuinely non-additive vs a strong additive: epsilon IS the measured pairwise deviation from the multiplicative
  single-mutant expectation -- specific gene PAIRS interact beyond each gene's average interaction-proneness (per-gene main
  effect). A per-gene main-effects additive provably loses the irreducible pairwise epsilon; a bilinear (shared code +
  product) can read it.

## Held-out slice (reserved BEFORE fitting)
Entity-level query split (QUERY_FRAC=0.40); report SEEN vs NOVEL gene-pair strata separately. NOVEL = both constituent genes
seen in train but the PAIR unseen (honest generalization stratum). Leak guard: query disjoint from train AND novel pairs
absent from train (asserted per seed; `leak_ok`). SUBSET (magnitude-defined, scale-free, pre-registered): hi = |epsilon -
median| > HI_Z*robust_sigma (robust_sigma = 1.4826*MAD), HI_Z=1.0 = genuine interaction; lo = otherwise (moderate control).

## Arms (regression MAE, lower better)
LEARN_SYM (shared code + elementwise PRODUCT = substrate symmetric bind; WINNER hypothesis) ; LEARN_ADD (shared code + SUM;
matched-capacity learned additive) ; ADD_RIDGE (closed-form ridge on per-token count design; STRONG categorical additive) ;
ADD_LSTSQ (closed-form lstsq additive) ; LEARN_ROLE (role-keyed product; ALGEBRA contrast, must NOT beat SYM on a symmetric
target) ; MEAN (train-mean = regression frequency floor) ; MEMORIZE (per-pair mean; collapses to MEAN on NOVEL) ; ORACLE.
strong_additive = min-MAE(LEARN_ADD, ADD_RIDGE, ADD_LSTSQ). rel(s,sub) = (STRONG_ADD_mae - SYM_mae)/STRONG_ADD_mae.

## FIXED genuineness gate (positive AND negative control; not saturation-vacuous)
- POSITIVE control: planted SYMMETRIC-interaction arena -> SYM beats strong-additive by its own bar (pos_rel >= 0.30;
  validated ~0.908). Proves the gate can DETECT genuine non-additivity.
- NEGATIVE control: planted ADDITIVE arena -> SYM must NOT beat additive (neg_rel <= 0.10; validated ~-0.018). Proves the
  gate is NOT saturation-vacuous.
- Ingested-real signal gate: frac_hi >= MIN_HI_FRAC=0.15 else HARD_FAIL_INSUFFICIENT -> escalate (larger slice; domain NOT
  closed).

## SIGNAL-READABILITY GATE (VET a57067090 revival criterion; the FIRST interpretability gate)
BEFORE the SYM-vs-additive transfer verdict can mean anything, a READABLE non-additive target must be certified to EXIST on the
hi-|epsilon| subset. readable_rel = max(strong_additive_vs_MEAN, SYM_vs_MEAN) on the hi subset (all==novel on real data, since
each unique pair appears once -> seen stratum empty). The max() is the "or oracle-ish readable-signal proxy" the VET permitted:
it is robust to a PURE-interaction target that the additive alone would miss (if only SYM reads it, the gate still fires and the
downstream SYM-beats-additive test is the correct HARD_PASS; if neither reads it, the target is noise-dominated). Threshold
READABILITY_REL = 0.15 (root-cause observed additive-vs-mean ~0.029 -> require ~5x more readable signal). Self-test validates
the gate FIRES on planted readable (additive AND interaction) arenas and REJECTS a planted pure-noise arena.

## Pre-registered bands (fixed BEFORE running)
- HARD_PASS_TRANSFER: READABILITY GATE PASSES (readable_rel_hi >= 0.15) AND novel_hi rel_MAE >= 0.30 AND (novel_hi rel -
  novel_lo rel) >= 0.15 AND pos_ok (>=0.30) AND neg_ok (<=0.10) AND must-fails fire (SHUFFLE all rel_sym_vs_mean <= 0.08 ;
  ARBITRARY novel rel_sym_vs_mean <= 0.08) AND oracle MAE <= 1e-6 AND leak_ok AND frac_hi >= 0.15 AND novel_hi_n >= 4.
- UNREADABLE_ESCALATE: readability gate FAILS (readable_rel_hi < 0.15) -> no readable non-additive target on this Costanzo
  slice -> ESCALATE to a higher-SNR dataset (Kramer QSAR Nonadd_pC per-CIRCLE [closed-form from 4 measured potencies = cleaner
  than genetic-interaction epsilon]; or DrugComb synergy [more replicates across cell-lines]). This is a DATASET-SNR null, NOT
  a thesis result -- SYM was never given a readable target. Distinguished from REFUTE (which requires readability to PASS).
- HARD_FAIL_INSUFFICIENT_SIGNAL: frac_hi < 0.15 -> ESCALATE (larger slice / DrugComb fallback).
- REFUTE_NO_TRANSFER: readability PASSES but novel_hi rel_MAE <= 0.05 (real measured epistasis IS readable yet ALSO
  additive-capturable = a deep foundation finding) with valid must-fails + oracle + controls.
- MIDDLE_BAND: partial / low-power novel_hi (novel_hi_n < 4) / advantage not materially larger on hi than lo.

Verdict gate ORDER (readability is a precondition for BOTH hard_pass and refute): control-gate -> oracle -> mustfail/leak ->
frac_hi noise-floor -> READABILITY GATE (UNREADABLE_ESCALATE if fail) -> power -> hard_pass / refute / middle.

HP_SCOPE: HARD_PASS gates apply to LEARN_SYM vs strong_additive ONLY; MEAN/MEMORIZE/ORACLE/LEARN_ROLE are contrast arms.

## Compute architecture
Class: (b) sequential-CPU with justification. Arena = O(1e3-1e4) native gene-pairs (bounded by TOP_ORF=400 / MAX_PAIRS=8000) x
tiny (<=Nx32) Adam fits (ms each) + numpy solves; total compute wall < 3min over 8 seeds; GPU yields no speedup on sub-ms
matmuls. Dominant cost = the pairwise dataset download + streaming parse (cached after first run). torch thread-capped.
Storage: no_storage / no_composition (single-hop readout). progress_logging: ACQUIRE candidate lines + streaming-parse row
counter (every 1M rows) + per-seed done lines, all flush=True (§17, timeout_s >= 1800).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds(8) x n_regimes(3) = 24; verdict counts per_seed_regime lengths.
- arms_differ_verified: self-test META_RULE_AF float-hash arms-differ on planted arena.
- final_metrics_atomicity: tmp_replace (single-shot os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
- crlb_n/a: "regression MAE floor is data-noise-defined (epsilon replicate/assay noise); no closed-form CRLB for the bilinear
  -readout arm. The HI_Z*robust_sigma hi subset + rel-MAE-reduction gate substitute for a capacity-feasibility cap."
- discriminator_reachability: true (planted positive control demonstrates rel>=0.30 attainable at the same arm scale).
- baseline_in_band: STRONG additive MAE measured (not saturated); planted pos/neg controls bound the gate 0.10..0.30.
- calibration_check: adaptive_with_discriminator_gate (HI_Z*robust_sigma magnitude split = data-scale-invariant; discriminator
  -still-fires verification = hi-minus-lo >= 0.15; insufficient-signal guard = frac_hi >= 0.15; SIGNAL-READABILITY gate
  readable_rel_hi >= 0.15 certifies a readable target EXISTS before the SYM-vs-additive test is interpretable -- self-test
  fires it on readable arenas [additive + interaction] and rejects a pure-noise arena).
- cell_chunked: false (single-cell multi-seed; total compute < 3min; per-seed logging provides observability).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback).
- heartbeat_present: per-seed + parse-progress flush logs (short run + logs every seed).
- defensive_error_checking: acquire/parse failures -> explicit ACQUIRE_FAILED / ESCALATE verdicts; no silent continue.
- deterministic_seeding: FIXED int seeds; sorted(set()) token ids + sorted ORF ranking + deterministic stride subsample; NO
  hash(), NO list(set()) (PROT-023 static scan passes).
- real_code_path: self-test builds a synthetic Costanzo pairwise TSV (zip-of-txt) and runs it through the REAL parse_costanzo/
  detect_costanzo_columns PATH-A code (filter + ORF extraction + subnetwork + reindex) + runs planted arenas through the REAL
  score()/arm code; hd_bind exercised on complex64 phasors.
- effective_vs_nominal_parameter_audit: no swept param (fixed regimes/seeds); ALIGNED (n/a).
- bracket_includes_discriminating_band: n/a (no sweep axis); the hi/lo magnitude split + planted controls provide the
  discriminating stratum.
- positive_control_arm: planted-interaction arena reproduces SYM>>additive AT the plant regime (not just citation).
- signal_shape_compatibility_audit: single-hop readout, no primitive->primitive composition edges; SHAPE_MATCH (n/a).
- functional_requirement: read a measured symmetric 2-way interaction on novel gene-pairs -> LEARN_SYM (shared code + product).

## Dispatch
Target queue: remote_cpu_queue (CPU-only; sequential Adam fits + numpy). Timeout: 3600s (larger download than ALMANAC +
521MB-scale streaming parse + 24 fits, with download variance headroom; progress_logging present). >= 5 seeds satisfied
(8 full / 3 smoke).
