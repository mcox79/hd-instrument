# Pre-registration: NCI-ALMANAC native drug-pair synergy -> symmetric-bind transfer proof (2026-07-15)

Author: hdi_exp_dev. Fixed BEFORE running. Conjunction MODULE #2 (also the module-#1 fallback if the Kramer per-compound
cell escalates for lack of R1,R2 cycle structure). Cell: `experiments/exp_almanac_synergy_nativepair_bind_readout_v1.py`
(committed 18eb164bf). All compute REMOTE; the network-independent remote `--self-test` (planted arenas) is the gate.

## Prior-work check
`tools/substrate_query.sh` (semantic KB) timed out under the no-local-compute lock; substituted a filesystem grep of
`experiments/` + `preregs/`. Closest prior cells:
- `exp_kramer_mmp_nonadd_bind_readout_v1` (real chem, but PER-COMPOUND MOESM CSVs -> needs RDKit+MMP fragmentation to
  recover R1,R2; escalation risk this cell is the fallback for).
- `exp_epistasis_bind_readout_integration_v1` + `exp_generated_epistasis_nonadditive_v1` (BOTH LLM-GENERATED class-pair
  severity -- the exact narration failure mode the pivot rejects; not real-measured).
This cell is genuinely NOVEL: first REAL-MEASURED continuous-interaction NATIVE-PAIR ingest (drug1 x drug2 + measured
ComboScore), no narration, no fragmentation. NOT a rediscovery.

## Why native-pair is cleaner than Kramer
Kramer per-compound rows lack cycle/transformation columns; constituents need RDKit + MMP fragmentation. NCI-ALMANAC has
the constituent-pair structure DIRECTLY: `NSC1 x NSC2 + SCORE` (ComboScore). The bind reads code(drugA) (x) code(drugB) ->
measured ComboScore natively.

## Pocket / data (provenance/versioning per module-registry conventions)
- Source: NCI-ALMANAC (Holbeck et al. 2017, Cancer Research 77(13):3564; PMC5499996). Retrieval: direct unauthenticated ZIP
  `https://discover.nci.nih.gov/cellminer/download/processeddataset/DTP_NCI60_ALMANAC_COMBO_SCORE.zip`. Cell records
  `provenance.json` (URL, retrieval_ts, zip_bytes, interaction definition) in `data/foundation_clusters/nci_almanac_combo/`.
- Entity = native (drug1, drug2) NSC pair (canonical unordered min/max token ids; tokens namespaced `NSC::<id>`).
- Constituents = the two drugs (per-drug identity tokens).
- Held-out TARGET = the MEASURED per-pair ComboScore (modified Bliss-independence EXCESS-over-additivity), aggregated to one
  scalar per native pair via two-level mean (per (pair, cell-line) mean, then mean over cell lines -> collapses the 3rd axis,
  reduces per-measurement noise). Continuous regression target (MAE); NOT a narrated label.
- Why genuinely non-additive vs a strong categorical additive: synergy is intrinsically a PAIRWISE excess -- specific drug
  PAIRS synergize/antagonize beyond each drug's average synergy-proneness (per-drug main effect). A per-drug main-effects
  additive provably loses the irreducible pairwise term; a bilinear (shared code + product) can read it.

## Held-out slice (reserved BEFORE fitting)
Entity-level query split (QUERY_FRAC=0.40); report SEEN vs NOVEL drug-pair strata separately. NOVEL = both constituent
drugs seen in train but the PAIR unseen (honest generalization stratum). Leak guard: query disjoint from train AND novel
pairs absent from train (asserted per seed; `leak_ok`). SUBSET (magnitude-defined, scale-free, pre-registered):
hi = |ComboScore - median| > HI_Z*robust_sigma (robust_sigma = 1.4826*MAD), HI_Z=1.0 = genuine interaction; lo = otherwise
(near-additive control). Stratification defined on the REAL ComboScore magnitude (regime-invariant).

## Arms (regression MAE, lower better)
LEARN_SYM (shared code + elementwise PRODUCT = substrate symmetric bind; WINNER hypothesis) ; LEARN_ADD (shared code + SUM;
matched-capacity learned additive) ; ADD_RIDGE (closed-form ridge on per-token count design; STRONG categorical additive) ;
ADD_LSTSQ (closed-form lstsq additive) ; LEARN_ROLE (role-keyed product; ALGEBRA contrast, must NOT beat SYM on a symmetric
target) ; MEAN (train-mean = regression frequency floor) ; MEMORIZE (per-pair mean; collapses to MEAN on NOVEL) ; ORACLE.
strong_additive = min-MAE(LEARN_ADD, ADD_RIDGE, ADD_LSTSQ). rel(s,sub) = (STRONG_ADD_mae - SYM_mae)/STRONG_ADD_mae.

## FIXED genuineness gate (positive AND negative control; not saturation-vacuous)
- POSITIVE control: planted SYMMETRIC-interaction arena -> SYM beats strong-additive by its own bar (pos_rel >= 0.30). Proves
  the gate can DETECT genuine non-additivity.
- NEGATIVE control: planted ADDITIVE arena -> SYM must NOT beat additive (neg_rel <= 0.10). Proves the gate is NOT
  saturation-vacuous (won't crown SYM on additive data).
- Ingested-real signal gate: frac_hi >= MIN_HI_FRAC=0.15 (enough high-interaction pairs) else HARD_FAIL_INSUFFICIENT ->
  escalate (domain NOT closed).

## Pre-registered bands (fixed BEFORE running)
- HARD_PASS_TRANSFER: novel_hi rel_MAE >= 0.30 AND (novel_hi rel - novel_lo rel) >= 0.15 AND pos_ok (>=0.30) AND neg_ok
  (<=0.10) AND must-fails fire (SHUFFLE all rel_sym_vs_mean <= 0.08 ; ARBITRARY novel rel_sym_vs_mean <= 0.08) AND oracle
  MAE <= 1e-6 AND leak_ok AND frac_hi >= 0.15 AND novel_hi_n >= 4.
- HARD_FAIL_INSUFFICIENT_SIGNAL: frac_hi < 0.15 -> ESCALATE to Costanzo yeast SGA (epsilon) / DrugComb.
- REFUTE_NO_TRANSFER: novel_hi rel_MAE <= 0.05 (real measured synergy ALSO additive-capturable = a deep foundation finding)
  with valid must-fails + oracle + controls.
- MIDDLE_BAND: partial / low-power novel_hi (novel_hi_n < 4) / advantage not materially larger on hi than lo.

HP_SCOPE: HARD_PASS gates apply to LEARN_SYM vs strong_additive ONLY; MEAN/MEMORIZE/ORACLE/LEARN_ROLE are contrast arms.

## Compute architecture
Class: (b) sequential-CPU with justification. Arena = O(1e3) native drug-pairs x tiny (<=Nx32) Adam fits (ms each) + numpy
solves; total compute wall < 3min over 8 seeds; GPU yields no speedup on sub-ms matmuls. Dominant cost = single ALMANAC ZIP
download + streaming parse of the combo CSV (cached after first run). torch thread-capped. Storage: no_storage /
no_composition (single-hop readout). progress_logging: ACQUIRE line + streaming-parse row counter (every 1M rows) + per-seed
done lines, all flush=True (§17, timeout_s >= 1800).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds(8) x n_regimes(3) = 24; verdict counts per_seed_regime lengths.
- arms_differ_verified: self-test META_RULE_AF float-hash arms-differ on planted arena (tolerates ADD_RIDGE/ADD_LSTSQ
  coinciding on simple data).
- final_metrics_atomicity: tmp_replace (single-shot os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
- crlb_n/a: "regression MAE floor is data-noise-defined (ComboScore replicate/assay noise); no closed-form CRLB for the
  bilinear-readout arm. The HI_Z*robust_sigma hi subset + rel-MAE-reduction gate substitute for a capacity-feasibility cap."
- discriminator_reachability: true (planted positive control demonstrates rel>=0.30 is attainable at the same arm scale).
- baseline_in_band: STRONG additive MAE is measured (not saturated); planted pos/neg controls bound the gate 0.10..0.30.
- calibration_check: adaptive_with_discriminator_gate (HI_Z*robust_sigma magnitude split = data-scale-invariant; discriminator
  -still-fires verification = hi-minus-lo >= 0.15; insufficient-signal guard = frac_hi >= 0.15).
- cell_chunked: false (single-cell multi-seed; total compute < 3min; per-seed logging provides observability).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback).
- heartbeat_present: per-seed + parse-progress flush logs (not the jsonl helper; run is short + logs every seed).
- defensive_error_checking: acquire/parse failures -> explicit ACQUIRE_FAILED / ESCALATE verdicts; no silent continue.
- deterministic_seeding: FIXED int seeds; sorted(set()) / sorted(keys) token+pair ordering; NO hash(), NO list(set())
  (PROT-023 static scan passes).
- real_code_path: self-test builds a synthetic ALMANAC ZIP and runs it through the REAL parse_almanac/detect_almanac_columns
  PATH-A code + runs planted arenas through the REAL score()/arm code; hd_bind exercised on complex64 phasors.
- effective_vs_nominal_parameter_audit: no swept param (fixed regimes/seeds); ALIGNED (n/a).
- bracket_includes_discriminating_band: n/a (no sweep axis); the hi/lo magnitude split + planted controls provide the
  discriminating stratum.
- positive_control_arm: planted-interaction arena reproduces SYM>>additive AT the plant regime (not just citation).
- signal_shape_compatibility_audit: single-hop readout, no primitive->primitive composition edges; SHAPE_MATCH (n/a).
- functional_requirement: read a measured symmetric 2-way interaction on novel pairs -> LEARN_SYM (shared code + product).

## Dispatch
Target queue: remote_cpu_queue (CPU-only; sequential Adam fits + numpy). Timeout: 2700s (download + parse + 24 fits, with
download variance headroom; progress_logging present). >= 5 seeds satisfied (8 full / 3 smoke).
