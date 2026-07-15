# Pre-registration: Paralog-CRISPR (Dede 2020 enCas12a) near-zero-singles CURATED pocket -> IVF + symmetric-bind transfer (2026-07-15)

Author: hdi_exp_dev. Fixed BEFORE running. HIGH-SNR replacement for the exhausted Costanzo per-pair epsilon (conjunction
module #1, the relocated thesis test). Cell: `experiments/exp_paralog_crispr_nearzero_singles_curated_ivf_v1.py`. All compute
REMOTE; the network-independent planted `--self-test` (raw-count->SMF/DMF pipeline + near-zero-singles selector + IVF
discriminator + transfer/readability gates on synthetic MOESM4-format data) is the gate. exp_dev ran static gates only
(py_compile/AST/ASCII/no-bare-except/no-hash-seed); the remote `--self-test` is the compute gate per the USER all-remote lock.

## Why (the discriminating experiment)
Three prior real-data negatives (chem MMP / LLM-narrated epistasis / genome-wide Costanzo epsilon) AND the committed Costanzo
near-zero-singles curated cell (`exp_costanzo_nearzero_singles_curated_ivf_v1`, commit 613fa311a) share ONE root cause: bulk
SGA epsilon is measured at ~1.8 cells/pair -- NOISE-DOMINATED in every pocket (Costanzo curated readable_rel ~0.0029). FIX =
a HIGHER-SNR MEASUREMENT CLASS, not another bulk source: a purpose-built combinatorial paralog-CRISPR synthetic-lethality
screen where the AND-gate interaction is measured with high replication. Dede et al. 2020 (enCas12a, Genome Biology 21:262,
PMC7558751) reports replicate Pearson r=0.87-0.94 (18 clones/pair x 3 reps x 3 cell lines). Near-zero-singles paralog pairs are
the CLEANEST real non-additivity: both single KOs ~neutral (main effect ~0 by DIRECT measurement) yet the double is lethal ->
the additive escape-hatch (Hill-Goddard-Visscher allele-frequency projection) structurally cannot apply (full KOs, no
segregating alleles). CITED@notes/research_dataset_scout_high_snr_conjunction_module1_replacement_2026-07-15.md +
notes/drill_negative_why_real_interactions_additive_capturable_where_genuine_2026-07-15.md.

## Prior-work check
Prior-work check: NONE at cosine>0.30 (substrate_query.sh: top hit `CN_addition_reaction` @0.2998, a chemistry concept node; no
prior paralog-CRISPR / synthetic-lethality / IVF arc cell). REDISCOVERY vs NOVEL: a SOURCE-ADAPTER swap of the committed
Costanzo near-zero-singles curated cell -- REUSES its VALIDATED target-agnostic machinery (real FHRR bind, 8 regression arms,
IVF via shared out-of-fold additive residual, planted pos_ctrl ~0.908 / neg_ctrl ~-0.018, signal-readability gate, must-fails,
seen/novel split). GENUINELY NEW: (1) the Dede MOESM4 raw-count -> SMF/DMF adapter, (2) TARGET = DMF (double-mutant fitness),
NOT a GI-score, (3) UNITS-ADAPTIVE near-zero band (log2FC vs WT-normalized). NEW cell (does not clobber the Costanzo metrics).

## SCHEMA BRANCH (the ONE thing to resolve; resolved at authoring by opening the columns)
The STRONG-additive baseline REQUIRES the RAW constituents SMF-A, SMF-B + DMF: the additive predicts DMF from per-gene main
effects and the INTERACTION = DMF beyond additive-of-singles. A GI-score-only target (zdLFC) makes "SYM beats additive" VACUOUS
(a GI score is already the interaction residual with main effects removed -- the trap the task forbids). exp_dev opened the Dede
supplementary columns 2026-07-15:
- **Additional File 3 (MOESM3, `13059_2020_2173_MOESM3_ESM.txt`)** = per-pair zdLFC, rows="geneA_geneB", cols=3 cell lines
  (A549/HT29/OVCAR8). SCORES-ONLY -> the vacuous trap; NOT used as target (fetched only as a cross-check).
- **Additional File 4 (MOESM4, `13059_2020_2173_MOESM4_ESM.txt`)** = RAW guide-pair read counts:
  `GENE_CLONE | GENE | A549.T2{A,B,C}.Ex | HT29.T2{A,B,C}.Ex | OVCAR8.T2{A,B,C}.Ex | plasmid.T0.Ex`, GENE="geneA.pos:geneB.pos".
  Carries the raw constituents. **BRANCH TAKEN = MOESM4 raw-count processing** -> per-construct log2FC (endpoint CPM vs plasmid
  T0), pooled over the 9 endpoint columns (the SNR lever). SMF = mean log2FC of single-KO-vs-control constructs; DMF (= TARGET)
  = mean log2FC of double (neither-control) constructs; interaction = DMF beyond additive-of-SMFs.
- **Rank-1 (Benchmarking-GI-Scores harmonized compendium, private figshare /s/ link)** DEPRIORITIZED: not programmatically
  resolvable this session AND its per-pair tables are MOESM3-class (scores-only, per scout's open concern) -> would need the
  SAME raw processing MOESM4 supplies directly. Documented as the higher-N ESCALATION target if Dede is underpowered.
- Static ESM URLs verified publicly reachable (2 successful fetches of MOESM3/MOESM4 headers).

CONTROL-GUIDE DETECTION (needed to isolate single-KO constructs -> SMF): PRIMARY = an explicit control/safe token set
(SAFE/NT/CONTROL/AAVS1/OLFR/CHR2/... + prefixes). BACKUP = a conservative degree-OUTLIER (a library-wide control pairs with many
genes; token degree >= 4x the 75th-percentile gene degree, min 8), which SELF-DISABLES if it would flag > 40% of tokens (dense
network -> degree cannot discriminate) so it can NEVER destroy real hub genes. If NO controls / NO single-KO constructs are found
-> `ESCALATE_NEED_RAW_CONSTITUENTS` with a diagnostic listing the top-degree candidate-control tokens (honest, fast-fix, NOT a
mechanism refute). RESIDUAL RISK (all-remote): the actual Dede control-guide token was NOT visible via fetch summaries; if it is
outside the token set AND not a degree outlier, the remote run escalates with the candidate tokens surfaced for a one-line fix.

## Data / target (module-registry conventions: provenance/versioning per row)
- Source: Dede et al. 2020, Genome Biology 21:262 (PMC7558751); DOI 10.1186/s13059-020-02173-2; static-content.springer.com ESM.
  Cell records provenance.json (URLs tried, bytes, retrieval ts, interaction definition, control diagnostics).
- Entity = native (gene_A, gene_B) paralog pair (canonical unordered; tokens = HGNC symbols). Held-out TARGET = **DMF**
  (double-mutant fitness log2FC), continuous regression target (MAE); NOT a narrated label, NOT the zdLFC GI-score.
- Constituents = the two genes; per-gene SMF (single-mutant fitness log2FC) from single-KO-vs-control constructs.
- CURATION selector (UNITS-ADAPTIVE): a gene is NEAR-ZERO-SINGLE iff mean SMF within the NEUTRAL band -- log2FC units
  (auto-detected by median SMF <= 0.5): |mean SMF| <= NZ_LFC=0.5 ; WT-normalized fallback: SMF in [SMF_WT_LO=0.90, SMF_WT_HI=1.10].
  CURATED pocket = double-mutant pairs where BOTH genes are near-zero-singles. MATCHED-RANDOM = size-matched random from ALL pairs.
- Slice controls: TOP_ORF=800 subnetwork, MAX_PAIRS=12000, MIN_PAIRS=60 (Dede ~400 pairs), PSEUDO=0.5 CPM pseudocount.

## PRIMARY discriminating statistic (interaction-variance-fraction, IVF) -- UNCHANGED machinery
IVF(subset) = Var(oof_additive_residual[subset]) / Var(y[subset]); ONE shared out-of-fold (k=5) per-gene-main-effects ridge
(l2=1.0) on the FULL pair network. Reported SIDE BY SIDE for (a) the curated near-zero-singles subset and (b) a size-matched
random subset, averaged over 8 seeds. Shared-model design is confound-robust (identical main-effect estimates; the RATIO isolates
WHICH pairs). IVF may exceed 1.0 for a pure-interaction subset (out-of-fold additive predictions can anti-correlate with the
interaction signal) -- expected, not a bug; the curated/random RATIO is the well-behaved discriminator.

## Held-out slice (reserved BEFORE fitting)
Transfer proof runs on the CURATED near-zero-singles ARENA (reindexed tokens). Entity-level query split (QUERY_FRAC=0.40); report
SEEN vs NOVEL separately. Each measured pair appears once -> seen stratum empty -> NOVEL = all query pairs (the honest stratum).
Leak guard asserted per seed (leak_ok).

## Arms (regression MAE, lower better) -- UNCHANGED from the validated Costanzo/native-pair cell
LEARN_SYM (shared code + elementwise PRODUCT = substrate symmetric bind; WINNER hypothesis) ; LEARN_ADD (shared code + SUM) ;
ADD_RIDGE (closed-form ridge on per-token count design; STRONG categorical additive) ; ADD_LSTSQ ; LEARN_ROLE (role-keyed
product; ALGEBRA contrast) ; MEAN (regression frequency floor) ; MEMORIZE (collapses to MEAN on NOVEL) ; ORACLE.
strong_additive = min-MAE(LEARN_ADD, ADD_RIDGE, ADD_LSTSQ). rel = (STRONG_ADD_mae - SYM_mae)/STRONG_ADD_mae. On near-zero-singles
pairs the additive-of-SMFs predicts ~neutral DMF (both singles ~0) so the additive is a GENUINELY STRONG null capturing the
main effects; SYM must beat it on the irreducible AND-gate interaction (non-vacuous by the DMF-target design).

## FIXED genuineness gate (positive AND negative control; not saturation-vacuous)
- POSITIVE control: planted SYMMETRIC-interaction arena -> SYM beats strong-additive (pos_rel >= POS_CTRL_REL=0.30; expected ~0.908).
- NEGATIVE control: planted ADDITIVE arena -> SYM must NOT beat additive (neg_rel <= NEG_CTRL_REL=0.10; expected ~-0.018).
- IVF-discriminator positive control (self-test): a planted arena with a pure-interaction half + pure-additive half ->
  IVF(interaction) >> 3x IVF(additive) -- proves the primary statistic FIRES. Plus an END-TO-END self-test: the synthetic-MOESM4
  curated pocket (AND-gate planted only on both-near-zero pairs) must be IVF-enriched vs matched-random (discriminator survives
  the full raw-count->DMF pipeline, not just the parser running).

## SIGNAL-READABILITY GATE (VET a57067090 revival criterion; precondition)
readable_rel = max(strong_additive_vs_MEAN, SYM_vs_MEAN) on the curated pocket >= READABILITY_REL=0.15 else UNREADABLE_ESCALATE
(a DATASET-SNR null, NOT a thesis result). The high-SNR Dede replication (r=0.87-0.94, reps pooled) is the SNR lever that
Costanzo's ~1.8 cells/pair lacked. Self-test fires it on planted readable (additive AND interaction) arenas and REJECTS noise.

## Pre-registered bands (fixed BEFORE running)
- HARD_PASS (`HARD_PASS_CURATED_NEARZERO_POCKET_NONADDITIVE_AND_TRANSFERS`): IVF(curated) >= IVF_RATIO_HP=3.0x IVF(matched-random)
  AND IVF(curated) >= IVF_CURATED_FLOOR=0.30 AND readability PASSES AND NOVEL curated rel_MAE (SYM vs strong-additive) >=
  HP_REL_CURATED=0.30 AND pos_ok(>=0.30) AND neg_ok(<=0.10) AND must-fails fire (SHUFFLE all + ARBITRARY novel rel_sym_vs_mean
  <= 0.08) AND oracle MAE<=1e-6 AND leak_ok AND novel_curated_n >= 8 AND n_curated >= MIN_CURATED=50. => the high-SNR curated
  paralog pocket is genuinely non-additive AND the symmetric bind reads it on novel pairs => module #1 real on measured data.
- HARD_FAIL_UNDERPOWERED_CURATED_N: < MIN_CURATED=50 clean near-zero-singles pairs -> insufficient N (directional-only per task;
  clearing the gate at N<50 is directional, not a HARD_PASS). ESCALATE to the Benchmarking-GI-Scores harmonized compendium
  (~8000 pairs) OR pool Dede+Parrish/pgPEN by hand. IVF still reported but flagged UNDERPOWERED.
- ESCALATE_NEED_RAW_CONSTITUENTS: acquired file has no raw SMF/DMF constituents (GI-scores-only / no single-KO controls found)
  -> re-run with a verified control token or a per-pair table retaining SMF-A/SMF-B/DMF (Horlbeck GSE116198). Diagnostic lists
  top-degree candidate-control tokens.
- ACQUIRE_FAILED: MOESM4 undownloadable from any candidate URL.
- UNREADABLE_ESCALATE: readability FAILS on the curated pocket -> DATASET-SNR null -> higher-SNR/higher-N pocket.
- REFUTE_GENUINE_RARITY_EVEN_IN_CURATED_NEARZERO_POCKET: readability PASSES but IVF(curated) within noise of matched-random
  (ratio <= IVF_RATIO_INDISTINCT=1.30) AND novel curated rel_MAE <= REFUTE_REL=0.05 -> genuine rarity dominates even in the
  best-available real HIGH-SNR pocket (a deep foundation finding: the interaction-reader may only be exercisable on constructed
  data). This is the honest outcome that separates "Costanzo was an SNR artifact" from "conjunctions are structurally rare".
- MIDDLE_BAND: partial (IVF enriched but transfer weak / transfer OK but IVF not enriched) / low-power novel curated.

Verdict gate ORDER: control-gate -> ACQUIRE/parse -> [ESCALATE_NEED_RAW_CONSTITUENTS] -> [HARD_FAIL underpowered N] ->
control/oracle/mustfail/leak -> READABILITY (UNREADABLE_ESCALATE if fail) -> power -> hard_pass / rarity_refute / middle.

HP_SCOPE: HARD_PASS gates apply to LEARN_SYM vs strong_additive + the IVF ratio ONLY; MEAN/MEMORIZE/ORACLE/LEARN_ROLE are contrast.

## Compute architecture
Class: (b) sequential-CPU with justification. Arena = O(1e2-1e4) native gene-pairs (bounded TOP_ORF=800 / MAX_PAIRS=12000) x tiny
(<=Nx32) Adam fits (ms) + numpy ridge solves (5 folds x 8 seeds = trivial); GPU yields no speedup on sub-ms matmuls. Dominant
cost = the small (~1.5MB) MOESM4 download + two-pass CPM parse (cached after first run). torch thread-capped. Storage: no_storage /
no_composition (single-hop readout). progress_logging: ACQUIRE candidate lines + PATH-A summary + per-seed IVF + per-seed
curated-arena done lines, all flush=True.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED units = n_seeds(8) IVF folds + n_seeds(8) x n_regimes(3) curated-arena scores; verdict counts
  per_seed_regime lengths.
- arms_differ_verified: self-test META_RULE_AF float-hash arms-differ on planted arena (arms_sig_count>=5).
- final_metrics_atomicity: tmp_replace (single-shot os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except -- grep-gate clean).
- crlb_n/a: "regression MAE floor is data-noise-defined (guide-count assay noise); no closed-form CRLB for the bilinear-readout
  arm. The IVF-ratio>=3x-vs-matched-random + rel-MAE-reduction gates substitute for a capacity-feasibility cap."
- discriminator_reachability: true (self-test IVF ratio and pos_ctrl rel target above their gates at plant scale; end-to-end
  self-test requires the synthetic curated pocket to be IVF-enriched -- discriminator survives the full raw-count->DMF pipeline).
- baseline_in_band: STRONG additive MAE measured (not saturated); planted pos/neg controls bound the gate 0.10..0.30.
- calibration_check: adaptive_with_discriminator_gate (UNITS-ADAPTIVE near-zero band auto-detected by median SMF; the
  IVF-ratio>=3x-vs-matched-random gate is the discriminator-still-fires verification; MIN_CURATED=50 is the insufficient-N guard;
  the SIGNAL-READABILITY gate certifies a readable target EXISTS before the SYM-vs-additive test is interpretable).
- cell_chunked: false (single-cell multi-seed; total compute < 3min post-download; per-seed logging = observability).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback).
- heartbeat_present: per-seed IVF + per-seed curated-arena + parse summary flush logs.
- defensive_error_checking: acquire/parse/control/underpower failures -> explicit ACQUIRE_FAILED /
  ESCALATE_NEED_RAW_CONSTITUENTS / HARD_FAIL_UNDERPOWERED_CURATED_N verdicts; no silent continue.
- deterministic_seeding: FIXED int seeds; sorted(set()) token ids + sorted gene ranking + deterministic stride subsample +
  strided IVF folds; NO hash(), NO list(set()) (static scan: 0 ERROR findings; WARN hits are comment/docstring prose only).
- real_code_path: self-test builds a synthetic Dede MOESM4-format raw-count TSV WITH control constructs and runs it through the
  REAL parse_dede_encas12a (CPM -> log2FC -> control detection -> SMF/DMF -> subnetwork -> reindex) + near_zero_singles_mask +
  oof_additive_residual/ivf_of + planted arenas through the REAL score()/arm code; hd_bind exercised on complex64 phasors; an
  END-TO-END check requires the synthetic curated pocket to be IVF-enriched. (exp_dev ran STATIC gates only; the REMOTE
  --self-test executes this -- USER all-remote lock.)
- effective_vs_nominal_parameter_audit: no swept param (fixed regimes/seeds); ALIGNED (n/a).
- bracket_includes_discriminating_band: n/a (no sweep axis); the near-zero-singles curation + IVF ratio + planted controls
  provide the discriminating stratum.
- positive_control_arm: planted-interaction arena reproduces SYM>>additive AND the planted mixed arena reproduces
  IVF(interaction)>>3x IVF(additive) AT the plant regime (not just citation).
- signal_shape_compatibility_audit: single-hop readout, no primitive->primitive composition edges; SHAPE_MATCH (n/a).
- functional_requirement: read a measured symmetric 2-way interaction (AND-gate synthetic-lethality) on novel curated paralog
  pairs -> LEARN_SYM (shared code + product); quantify irreducible-pairwise variance -> IVF via shared out-of-fold additive
  residual; isolate the pocket where additive-of-singles structurally fails -> near-zero-singles selector on measured SMF.

## Dispatch
Target queue: remote_cpu_queue (CPU-only; numpy solves + sub-ms Adam fits). Timeout: 1800s (small ~1.5MB MOESM4 download +
two-pass CPM parse + 8 IVF folds + 24 curated-arena fits, with download variance headroom). >= 5 seeds satisfied (8 full /
3 smoke). Remote --self-test is the gate BEFORE the multi-seed full. exp_dev does NOT run the remote SCP ship (GATE_FAILs
mid-ship); orchestrator ships + owns post-ship REMOTE VERIFY.
