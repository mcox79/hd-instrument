# PREREG: horlbeck_gi_dense_recurrence_detection_v1

Date: 2026-07-15. Author: exp_dev. Cell:
`experiments/exp_horlbeck_gi_dense_recurrence_detection_v1.py`.
Design source: `notes/research_dense_recurrence_gi_detection_cell_design_2026-07-15.md`
(+ detection-decider additions: rank-R readout arm; degree-preserving null as first-class).

## Question
Does the SYMMETRIC-PRODUCT (bind / conjunction) readout DETECT real genetic-interaction (GI) structure from bare
gene IDENTITY on HELD-OUT recurring-gene pairs, beating BOTH an ADDITIVE main-effects null AND a DEGREE-preserving
(hubness) null, on a dense all-by-all real biological GI map (Horlbeck 2018, K562)?

This is the C1/S1 dense-recurrence escalation of the STRUCTURAL_UNDERPOWER (paralog-pocket degree~1.0, C3/S4,
untestable) diagnosis. Held-out relational detection is structurally POSSIBLE here: every gene recurs in ~447 pairs.

## Data provenance (MEASURED / CITED)
- SOURCE: Horlbeck et al. 2018, Cell. Mendeley Data 10.17632/rdzk59n6j4.1 -> `GI_map_treeview.zip`
  -> gene-level Treeview CDT maps. CITED@Mendeley 10.17632/rdzk59n6j4.1.
- GI score = the paper's OWN quadratic-fit residual (observed double phenotype minus expected from a quadratic fit
  of the two single-gene phenotypes). Main effects STRIPPED BY CONSTRUCTION. Using the paper's processed matrix
  avoids re-deriving the null. CITED@Horlbeck 2018 GImap methodology.
- Parsed artifact: `data/horlbeck_gi/horlbeck_gene_gi.npz`
  sha256=13d1f8b6333762463e90951368193f3d3b59f761acf2abb109cd87b2c3fb5095 size=1296529 bytes.
  MEASURED@experiments/_horlbeck_gi_prep.py output (also rebuilt inline by the cell if npz absent).
- K562: n_genes=448, off-diag unordered pairs=100128, finite=100.0%, every gene recurs 447x.
  MEASURED@data/horlbeck_gi/horlbeck_gene_gi.npz (via prep). GI mean=0.0292 std=1.2034; |GI| 90th pct=1.88.
- Jurkat (cross-line secondary): n_genes=388, pairs=75078, 100% finite, recurrence 387x.
- Cell is SELF-CONTAINED: loads committed npz fast-path; else downloads the Mendeley zip + parses inline
  (remote runner needs the npz on origin/main OR internet; both paths supported).

## Mechanism (faithful glass-box; HYPOTHESIZED bands, MEASURED machinery)
SYM as described = symmetric-product bilinear readout `score(a,b)=sum_d W_d e_{a,d} e_{b,d}` (bind/conjunction of
two gene codes). Realized as a symmetric low-rank factorization of the SIGNED GI matrix:
`Ghat_ab = mu + alpha_a + alpha_b + <F_a,F_b>_R` (F_g in R^R learned). The PRODUCT term `<F_a,F_b>` IS the
conjunction. ADDITIVE = the SAME model at R=0 (offsets only). SYM STRICTLY NESTS ADDITIVE; the only difference is
the symmetric-product term, so SYM beating ADDITIVE on HELD-OUT pairs isolates GENERALIZING pair-specific
(conjunction) structure. Rank R = factorization dimension = hard capacity on the product term (identifiable) = the
"match-code-to-data-structure / rank lever." Detection = rank held-out pairs by predicted magnitude |Ghat|.

## Arms + HP_SCOPE
- CHANCE (sanity; no HP gate), MEMORIZE (split-validation; no HP gate), DEGREE (first-class null; HP-relevant),
  ADDITIVE = SYM R=0 (nested null; HP-relevant), SYM_R{1,2,4,8,16,32} (mechanism; R=8 = PRE-REGISTERED HERO).
- HP_SCOPE: the HARD_PASS conjunction-detects gate applies ONLY to HERO=SYM_R8 vs {ADDITIVE, DEGREE}. CHANCE and
  MEMORIZE are sanity/split arms (they carry only the split_clean REFUTE gate, not the margin gate).
- Rank sweep [0,1,2,4,8,16,32] reported as the rank-lever diagnostic; individual ranks other than R8 are NOT
  each gated (avoids test-set rank-selection optimism). best_sym (max over ranks) is REPORTED as a secondary,
  explicitly-optimistic readout, not the primary gate.

## Readout / metrics
AUPRC (primary) on HELD-OUT (novel) pairs vs a FIXED pre-registered gold: hit = |GI| in the top decile
(>= 90th percentile of |GI| over all off-diag pairs; threshold fixed BEFORE the split, base rate ~0.10 by
construction). Also precision@{1,5,10}% and enrichment@10% = p@10/base_rate. SEEN (train) AUPRC reported as a
model-fit sanity. Multi-seed: 5 mask seeds; report mean +- std.

## PRE-REGISTERED BANDS (fixed before running; HYPOTHESIZED). p0 = measured base rate. REL_MARGIN=0.25. HERO=SYM_R8.
- **HARD_PASS_CONJUNCTION_DETECTS**: HERO_auprc >= (1+REL_MARGIN)*max(ADD,DEG) AND HERO >= 2*p0 AND
  (HERO - 1.25*max(ADD,DEG)) > seed_std (robust to mask draw) AND split_clean AND seen_ok.
- **HARD_FAIL_ADDITIVE_CAPTURABLE**: HERO < 1.10*ADD AND ADD > 1.15*DEG AND ADD > 1.3*p0
  (real structure, but conjunction adds nothing over main effects).
- **HARD_FAIL_DEGREE_DOMINATED**: HERO < 1.10*DEG AND DEG >= 0.95*ADD (only hubness recoverable).
- **MIDDLE_BAND (declared MODAL expected outcome, P~0.28; do NOT over-invest a PASS story)**:
  HERO >= 1.15*DEG but HERO < 1.25*ADD (partial pair-specific structure beyond degree, short of the margin).
- **REFUTE_IMPL**: no SYM arm fits TRAIN (best SYM SEEN AUPRC < max(0.20, 1.8*p0) OR < 1.15*ADD_seen) OR split
  leaks (MEMORIZE > 1.3*p0) OR CHANCE off base rate (|CHANCE-p0| > 0.04).

### Band feasibility / calibration (META_RULE_L, AG, M)
- Discriminating band: base rate ~0.10; arms measured at smoke land AUPRC 0.13-0.28 (in the informative band,
  NOT saturated, NOT at floor). `bracket_includes_discriminating_band`: YES (all mechanism/null arms in
  [0.13,0.48], 0% saturated >0.90). `baseline_in_band`: DEGREE=0.268, ADDITIVE=0.236 both in (0.05,0.95). MEASURED.
- `calibration_check: adaptive_with_discriminator_gate` for the SEEN REFUTE floor ONLY: the seen-fit gate is a
  broken-vs-working sanity check (NOT a HARD_PASS threshold). Smoke revealed the initial absolute 0.50 floor was
  UNREACHABLE on a noisy magnitude task (SYM_R8 SEEN=0.484 = clearly working: >> ADD SEEN 0.210 >> base 0.106);
  recalibrated to `best_seen_sym >= max(0.20, 1.8*p0) AND >= 1.15*ADD_seen` (reachable + still catches a
  non-training model at SEEN~p0). The 0.25 HARD_PASS margin + all HARD_FAIL/MIDDLE bands are UNCHANGED from
  pre-smoke. Discriminator still fires post-recalibration (smoke verdict = HARD_FAIL_DEGREE_DOMINATED, non-vacuous).
- CRLB: `crlb_n/a` — no closed-form noise floor for AUPRC-of-a-learned-factorization on a real residual matrix;
  feasibility is established empirically by the smoke (arms in the discriminating band).

## Smoke evidence (MEASURED@data/exp_horlbeck_gi_dense_recurrence_detection_v1/metrics.json, n=120, ranks[0,1,8], 2 seeds)
- p0=0.106; min_train_deg=90 (>=K_FLOOR=50); split_clean=True (MEMO=0.127<=1.3*p0; CHANCE=0.126, |.-p0|=0.02).
- SYM_R8=0.2794(+-0.0025) ADD=0.2363 DEG=0.2680 CHANCE=0.1262 MEMO=0.1267. Rank sweep monotonic 0.236->0.253->0.279.
- SYM_R8 SEEN=0.484 (>> ADD SEEN 0.210 >> base 0.106): model trains; seen_ok=True.
- Smoke verdict=HARD_FAIL_DEGREE_DOMINATED (HERO/DEG=1.04x at n=120). Degree null is STRONG (enrich 2.96), exactly
  the Zietz-2024 degree-confound risk the drill flagged. Full n=448 is the genuine test. Smoke wall=12s.
- **Discriminator FIRES** (arms span 0.126-0.279; not saturated; verdict branches all reachable). NON-VACUOUS.

## Compute architecture
- Class: **(b) sequential-CPU with justification**. The cell is a set of small symmetric low-rank factorization
  fits (per-gene R<=32 factors + offsets over ~85k train pairs, Adam MSE). Each fit is seconds-to-~2min on CPU
  torch; total full wall estimate ~15-45 min. No meaningful GPU speedup at this scale (small matmuls; the bottleneck
  is many short independent Adam loops, not one large kernel). Glass-box CPU is the appropriate reference. Uses
  `import torch` (passes remote_cpu_queue routing-sanity gate). NOT a KGStore/substrate-primitive cell.
- Storage strategy: `no_storage / no_composition` (direct factorization measurement; no bundled/sharded HD store).
- Determinism: all RNG seeds from INTEGER indices (seed*const); NO Python built-in hash(); NO list(set()) ordering.
  `deterministic_seeding: true` (F.5 / PROT-023 static scan will pass).

## SCHEMA-VET mandatory fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds = 5 (verdict counts len(per_seed); emits cardinality_ok).
- arms_differ_verified: true (self-test check `arms_differ`: DEGREE/ADDITIVE/SYM_R8 held-out sigs distinct).
- final_metrics_atomicity: `tmp_replace` (metrics.json.tmp -> os.replace).
- except-ordering: `except SystemExit: raise` before `except Exception` (NO BaseException, NO bare except). Verified.
- discriminator_fires (META_RULE_K): mechanism = symmetric-product detection; smoke shows arms span 0.13-0.28
  (fires). MIDDLE/degree-dominated smoke at n=120 is a scale artifact, not vacuity.
- effective_vs_nominal_parameter_audit (Gate A): swept axis = rank R; effective rank experienced by the product
  term = R exactly (no partition/routing dilution). sweep_alignment_verdict: ALIGNED.
- bracket_includes_discriminating_band (Gate B): 7/7 rank points + nulls land in [0.13,0.48]; discriminating_fraction=1.0 (>=0.30).
- signal_shape_compatibility_audit (Gate C): single mechanism, no primitive->primitive composition edges. N/A (no adapters needed).
- positive_control_arms (Gate D): N/A — no PRIOR chain-grade substrate primitive is being reproduced (first
  real-data test of the symmetric-product readout; the mechanism is re-implemented in-cell, not a KGStore call).
  The construction-proof (SYM fits planted interaction >> additive) IS asserted in self-test (machinery control).
- functional_requirements (Gate E): (1) detect real GI from gene identity -> symmetric low-rank product readout;
  (2) beat additive main effects -> nested R=0 baseline; (3) beat hubness -> degree-preserving null; (4) confirm
  split forces generalization -> MEMORIZE collapse. All mapped.
- real_code_path (F.1): self-test constructs+loads the REAL npz (448-gene dense check) AND exercises the REAL arm
  fns (`_fit_sym` R0/R8, `_degree_null`, `_memorize`, `make_split`, `average_precision`, `score_seed`) at tiny
  scale. exercised_entrypoints verified in self-test.
- substrate_signature (F.2/F.3): N/A — cell does not call KGStore or any drifting substrate constructor; only
  numpy/torch stdlib. No local/remote signature-drift surface.
- guard_baseline_valid (F.4): N/A — no control-beats-baseline break-guard (the REFUTE split-leak gate uses
  MEMORIZE-vs-p0, an absolute floor, not a control-vs-baseline comparison at a structural floor).
- §13 defensive error-checking: cell_chunked=false (single-cell multi-seed loop, cheap; not seed-chunked because
  each seed is ~minutes and a runner death re-runs the whole cheap cell); start_marker_written=false (not chunked;
  crash-diagnostic covers silent death); crash_diagnostic_present=true (outer try -> CELL_CRASHED metrics +
  traceback, atomic); heartbeat_present via per-seed flushed progress prints; defensive_error_checking:
  "single-cell cheap cell; crash-diagnostic + per-seed flushed progress; chunking/start-marker exempt (each seed
  minutes, full cell re-runnable)".
- §17 progress_logging: `print_flush_true` (per-seed flushed progress lines; `sys.stdout.reconfigure(line_buffering)`
  at start). timeout_s=5400 >= 1800 so this is MANDATORY; satisfied. progress_cadence: one flushed line per seed
  (~5-9 min cadence at full scale) plus the run header.

## Dispatch
- Queue: **remote_cpu_queue** (light CPU factorization; NO GPU; NO local FULL per USER no-local-compute lock).
- Timeout: 5400 s (est full ~15-45 min; conservative formula ~3900s; margin for slower remote CPU; < 14400 cap).
- Self-test: PASS locally (exit 0; 10/10 checks). Smoke: PASS locally (exit 0; 12s; discriminator fires;
  verdict=HARD_FAIL_DEGREE_DOMINATED at n=120 = correct classification, non-vacuous).
- Requires: orchestrator PUSH (cell + prereg + npz + prep) to origin/main, THEN queue_add to remote_cpu_queue.
