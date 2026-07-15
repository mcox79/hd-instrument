# Pre-registration: Costanzo near-zero-singles CURATED pocket -> interaction-variance-fraction + symmetric-bind transfer (2026-07-15)

Author: hdi_exp_dev. Fixed BEFORE running. Subset-curated real-data DISCRIMINATOR (conjunction module #1). Cell:
`experiments/exp_costanzo_nearzero_singles_curated_ivf_v1.py`. All compute REMOTE; the network-independent planted
`--self-test` (near-zero-singles selector + IVF discriminator + transfer/readability gates on synthetic data) is the gate.

## Why (the discriminating experiment)
The three prior real-data negatives (chem MMP / LLM-narrated epistasis / the FAIR genome-wide Costanzo epsilon test,
commit bcd66a6d8) all measured at the BULK/genome-wide scale. The negative-drill
`notes/drill_negative_why_real_interactions_additive_capturable_where_genuine_2026-07-15.md` shows genuine molecular
non-additivity is MEASUREMENT-HIDDEN at that scale (Hill-Goddard-Visscher allele-frequency projection + Simpson's-paradox
aggregation dilution), and CONCENTRATED in identifiable high-confidence pockets. FIX = subset-curation, NOT domain
abandonment. This cell restricts Costanzo to the NEAR-ZERO-SINGLES synthetic-lethal / AND-gate pocket -- pairs where BOTH
single-mutant fitness (SMF) values are within noise of wild-type (main effect ~0 by DIRECT measurement, computable from
Costanzo SMF columns ALONE per the drill's option (ii); NO external protein-complex DB needed) yet the double-mutant
|epsilon| is large -- the one pocket where the additive escape-hatch (allele-frequency projection) structurally cannot apply.

## Prior-work check
Prior-work check: NONE at cosine>0.30 (substrate_query.sh: top hit is the generic wordnet synset "interaction" at 0.3066; no
prior near-zero-singles / curated-epistasis / IVF arc cell exists). Genuinely novel: a subset-curation + IVF-statistic
modification of the landed native-pair cell `exp_costanzo_epistasis_nativepair_bind_readout_v1` (REFUTE bcd66a6d8, VET
a89fbd90 = additive-capturable conditional at genome-wide scale). Reuses that cell's VALIDATED machinery (real FHRR bind,
regression arms, planted pos_ctrl 0.908 / neg_ctrl -0.018, signal-readability gate); NEW = the near-zero-singles selector +
the IVF primary statistic. NEW cell (does not clobber the landed native-pair metrics).

## Pocket / data (provenance/versioning per module-registry conventions)
- Source: Costanzo et al. 2016, Science 353:aaf1420; thecellmap.org/yeast/costanzo2016. REQUIRES the PAIRWISE zip (521MB) --
  the single-mutant-fitness columns needed for the near-zero-singles selector are pairwise-only. The MATRIX fallback lacks SMF
  -> ESCALATE_NEED_PAIRWISE_FOR_SMF (honest, not a mechanism refute). Cell records provenance.json.
- Entity = native (query_gene, array_gene) pair (canonical unordered; tokens = systematic ORF ids).
- Constituents = the two genes. Held-out TARGET = measured epsilon (double-mutant fitness minus the multiplicative
  single-mutant expectation), mean-aggregated per ORF-pair. Continuous regression target (MAE); NOT a narrated label.
- CURATION selector: per-gene mean SMF accumulated over all rows; a gene is NEAR-ZERO-SINGLE iff mean SMF in
  [SMF_WT_LO=0.90, SMF_WT_HI=1.10] (<=~10% single-mutant fitness DEFECT). CURATED pocket = significant pairs where BOTH genes
  are near-zero-singles. MATCHED-RANDOM = size-matched random draw from ALL significant pairs.
- SNR levers (retained): |epsilon|>0.12 STRINGENT tier AND p<0.05; >=2 replicate measurements/pair; TOP_ORF=500 subnetwork,
  MAX_PAIRS=12000 (RAISED so the curated subset clears MIN_CURATED). MIN_PAIRS=200.

## PRIMARY discriminating statistic (interaction-variance-fraction, IVF)
IVF(subset) = Var(oof_additive_residual[subset]) / Var(y[subset]), where oof_additive_residual is a SINGLE shared out-of-fold
(k=5) per-gene-main-effects ridge (l2=1.0) model fit on the FULL significant subnetwork. Reported SIDE BY SIDE for (a) the
curated near-zero-singles subset and (b) a size-matched random subset of all pairs, averaged over 8 seeds. Shared-model design
is confound-robust: identical per-gene main-effect estimates for both subsets -> the ratio isolates WHICH pairs (no
subset-sparsity artifact). NOTE: IVF may exceed 1.0 for a pure-interaction subset (out-of-fold additive predictions can be
anti-correlated with the interaction signal and ADD variance) -- this is expected, not a bug; the curated/random RATIO is the
well-behaved discriminator (self-test: IVF(interaction)=1.66, IVF(additive)=0.26, ratio=6.40).

## Held-out slice (reserved BEFORE fitting)
Transfer proof runs on the CURATED near-zero-singles ARENA (reindexed tokens). Entity-level query split (QUERY_FRAC=0.40);
report SEEN vs NOVEL separately. On real data each unique pair appears once -> seen stratum empty -> NOVEL = all query pairs
(the honest stratum). Leak guard asserted per seed (leak_ok). The whole curated pocket is the high-interaction target, so the
transfer target = the NOVEL curated stratum (sub='full').

## Arms (regression MAE, lower better) -- UNCHANGED from the validated native-pair cell
LEARN_SYM (shared code + elementwise PRODUCT = substrate symmetric bind; WINNER hypothesis) ; LEARN_ADD (shared code + SUM) ;
ADD_RIDGE (closed-form ridge on per-token count design; STRONG categorical additive) ; ADD_LSTSQ ; LEARN_ROLE (role-keyed
product; ALGEBRA contrast) ; MEAN (regression frequency floor) ; MEMORIZE (collapses to MEAN on NOVEL) ; ORACLE.
strong_additive = min-MAE(LEARN_ADD, ADD_RIDGE, ADD_LSTSQ). rel = (STRONG_ADD_mae - SYM_mae)/STRONG_ADD_mae.

## FIXED genuineness gate (positive AND negative control; not saturation-vacuous)
- POSITIVE control: planted SYMMETRIC-interaction arena -> SYM beats strong-additive (pos_rel >= 0.30; self-test 0.9078).
- NEGATIVE control: planted ADDITIVE arena -> SYM must NOT beat additive (neg_rel <= 0.10; self-test -0.0179).
- IVF-discriminator positive control (self-test): a planted arena with a pure-interaction half and a pure-additive half ->
  IVF(interaction) >> 3x IVF(additive) (self-test ratio 6.40) -- proves the primary statistic FIRES.

## SIGNAL-READABILITY GATE (VET a57067090 revival criterion; precondition)
readable_rel = max(strong_additive_vs_MEAN, SYM_vs_MEAN) on the curated pocket >= READABILITY_REL=0.15 else UNREADABLE_ESCALATE
(a DATASET-SNR null, NOT a thesis result). Self-test fires it on planted readable (additive AND interaction) arenas and
REJECTS a planted pure-noise arena.

## Pre-registered bands (fixed BEFORE running)
- HARD_PASS (`HARD_PASS_CURATED_NEARZERO_POCKET_NONADDITIVE_AND_TRANSFERS`): IVF(curated) >= IVF_RATIO_HP=3.0x
  IVF(matched-random) AND IVF(curated) >= IVF_CURATED_FLOOR=0.30 AND readability PASSES AND NOVEL curated rel_MAE (SYM vs
  strong-additive) >= HP_REL_CURATED=0.30 AND pos_ok(>=0.30) AND neg_ok(<=0.10) AND must-fails fire (SHUFFLE all + ARBITRARY
  novel rel_sym_vs_mean <= 0.08) AND oracle MAE<=1e-6 AND leak_ok AND novel_curated_n >= 8. => curated pocket is genuinely
  non-additive AND the symmetric bind reads it on novel pairs => prior bulk REFUTEs were measurement artifacts + module #1 real.
- HARD_FAIL_UNDERPOWERED_CURATED_N_ESCALATE_ENCAS12A: < MIN_CURATED=50 clean near-zero-singles pairs -> insufficient N ->
  ESCALATE to the enCas12a paralog-buffering compendium (Dede et al. PMC7558751) / Benchmarking-GI-Scores harmonized
  compendium (higher-N fallbacks; same near-zero-singles logic). IVF still reported but flagged UNDERPOWERED.
- ESCALATE_NEED_PAIRWISE_FOR_SMF: acquired file has no SMF columns (matrix format / SMF absent) -> re-run on the pairwise zip.
- UNREADABLE_ESCALATE: readability FAILS on the curated pocket -> DATASET-SNR null -> higher-SNR pocket.
- REFUTE_GENUINE_RARITY_EVEN_IN_CURATED_NEARZERO_POCKET: readability PASSES but IVF(curated) within noise of matched-random
  (ratio <= IVF_RATIO_INDISTINCT=1.30) AND novel curated rel_MAE <= REFUTE_REL=0.05 -> genuine rarity dominates even in the
  best-available real pocket (a deep foundation finding: the interaction-reader may only be exercisable on constructed data).
- MIDDLE_BAND: partial (IVF enriched but transfer weak / transfer OK but IVF not enriched) / low-power novel curated.

Verdict gate ORDER: control-gate -> oracle -> mustfail/leak -> [ESCALATE_NEED_PAIRWISE_FOR_SMF] -> [HARD_FAIL underpowered N]
-> READABILITY (UNREADABLE_ESCALATE if fail) -> power -> hard_pass / rarity_refute / middle.

HP_SCOPE: HARD_PASS gates apply to LEARN_SYM vs strong_additive + the IVF ratio ONLY; MEAN/MEMORIZE/ORACLE/LEARN_ROLE are
contrast arms.

## Compute architecture
Class: (b) sequential-CPU with justification. Arena = O(1e3-1e4) native gene-pairs (bounded TOP_ORF=500 / MAX_PAIRS=12000) x
tiny (<=Nx32) Adam fits (ms) + numpy ridge solves (design dim <=1001, 5 folds x 8 seeds = trivial); GPU yields no speedup on
sub-ms matmuls. Dominant cost = the 521MB pairwise download + streaming parse (cached after first run). torch thread-capped.
Storage: no_storage / no_composition (single-hop readout). progress_logging: ACQUIRE candidate lines + streaming-parse row
counter (every 1M rows) + per-seed IVF + per-seed curated-arena done lines, all flush=True (§17, timeout_s >= 1800).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED units = n_seeds(8) IVF folds + n_seeds(8) x n_regimes(3) curated-arena scores; verdict counts
  per_seed_regime lengths.
- arms_differ_verified: self-test META_RULE_AF float-hash arms-differ on planted arena (arms_sig_count=6).
- final_metrics_atomicity: tmp_replace (single-shot os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except -- grep-gate clean).
- crlb_n/a: "regression MAE floor is data-noise-defined (epsilon replicate/assay noise); no closed-form CRLB for the bilinear
  -readout arm. The IVF-ratio>=3x-vs-matched-random + rel-MAE-reduction gates substitute for a capacity-feasibility cap."
- discriminator_reachability: true (self-test IVF ratio 6.40 >= 3.0 and pos_ctrl rel 0.908 >= 0.30 demonstrate both gates
  attainable at plant scale).
- baseline_in_band: STRONG additive MAE measured (not saturated); planted pos/neg controls bound the gate 0.10..0.30.
- calibration_check: adaptive_with_discriminator_gate (near-zero-singles SMF band [0.90,1.10] is data-scale-invariant; the
  IVF-ratio>=3x-vs-matched-random gate is the discriminator-still-fires verification; MIN_CURATED=50 is the insufficient-N
  guard; the SIGNAL-READABILITY gate certifies a readable target EXISTS before the SYM-vs-additive test is interpretable).
- cell_chunked: false (single-cell multi-seed; total compute < 3min post-download; per-seed logging = observability).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback).
- heartbeat_present: per-seed IVF + per-seed curated-arena + parse-progress flush logs.
- defensive_error_checking: acquire/parse/SMF/underpower failures -> explicit ACQUIRE_FAILED / ESCALATE_NEED_PAIRWISE_FOR_SMF /
  HARD_FAIL_UNDERPOWERED_CURATED_N verdicts; no silent continue.
- deterministic_seeding: FIXED int seeds; sorted(set()) token ids + sorted ORF ranking + deterministic stride subsample +
  strided IVF folds; NO hash(), NO list(set()) (PROT-023 static scan: 0 ERROR findings; the WARN hits are comment/docstring
  prose only).
- real_code_path: self-test builds a synthetic Costanzo pairwise TSV WITH SMF columns and runs it through the REAL
  parse_costanzo/detect_costanzo_columns (SMF accumulation + subnetwork + reindex) + near_zero_singles_mask +
  oof_additive_residual/ivf_of + planted arenas through the REAL score()/arm code; hd_bind exercised on complex64 phasors.
  (Self-test PASSED locally: all 14 checks true.)
- effective_vs_nominal_parameter_audit: no swept param (fixed regimes/seeds); ALIGNED (n/a).
- bracket_includes_discriminating_band: n/a (no sweep axis); the near-zero-singles curation + IVF ratio + planted controls
  provide the discriminating stratum.
- positive_control_arm: planted-interaction arena reproduces SYM>>additive AND the planted mixed arena reproduces
  IVF(interaction)>>3x IVF(additive) AT the plant regime (not just citation).
- signal_shape_compatibility_audit: single-hop readout, no primitive->primitive composition edges; SHAPE_MATCH (n/a).
- functional_requirement: read a measured symmetric 2-way interaction on novel curated gene-pairs -> LEARN_SYM (shared
  code + product); quantify irreducible-pairwise variance -> IVF via shared out-of-fold additive residual.

## Dispatch
Target queue: remote_cpu_queue (CPU-only; numpy solves + sub-ms Adam fits). Timeout: 3600s (521MB pairwise download +
streaming parse of ~23M rows + 8 IVF folds + 24 curated-arena fits, with download variance headroom; progress_logging
present). >= 5 seeds satisfied (8 full / 3 smoke). Remote --self-test is the gate BEFORE the multi-seed full.
