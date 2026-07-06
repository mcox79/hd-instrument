# Pre-registration: cert_ledger_source_direct_entailment_v1

Date: 2026-07-06
Anchor: `cert_ledger_source_direct_entailment_v1`
Cell: `experiments/exp_cert_ledger_source_direct_entailment_v1.py`
Author: hdi_exp_dev
Predecessor: `exp_cert_ledger_numeric_entailment_v1` (Tier-2; landed HARD_PASS but `retrieval_hit_rate=0.0328`)
Sibling negative: `exp_cert_ledger_retrieval_coverage_v1` (content-addressable ceiling ~0.15-0.17, structurally bounded)
Drill: `notes/research_ledger_coverage_negative_revival_2026-07-06.md` (route #1: retrieval-free direct entailment)

## One-line
REPLACE the near-vacuous ledger-retrieval leg of the Tier-2 self-audit with SOURCE-DIRECT metric lookup: audit each
cited `NUM op NUM` claim DIRECTLY against ITS OWN citing cell's metrics.json (every metrics.json is its own exact,
non-fuzzy referent), and measure honest COVERAGE + op_agreement + the un-auditable residual.

## Motivation (all numbers MEASURED off-disk 2026-07-06)
- `CITED@data/exp_cert_ledger_numeric_entailment_v1/metrics.json:arms.7.retrieval_hit_rate = 0.0328` -- the Tier-2
  audit retrieves a backing LEDGER record for only ~3.3% of the numeric citations it checks (near-vacuous coverage).
- The drill proved the bottleneck is NOT retrieval quality: the cert_ledger schema has NO numeric slot, so most
  cited claims have NO backing record to retrieve at all (the content-addressable successor's ceiling ~0.15-0.17).
- INSIGHT (route #1): skip retrieval entirely. Each cited number's TRUE referent is the citing cell's OWN
  metrics.json -- glob gives full, exact, non-fuzzy access; nothing needs to be found in a lossy index. Open the
  same file, walk its numeric leaves, resolve the cited measured value to a persisted metric, re-check the
  entailment on the PERSISTED value via the VET'd `decode_then_compare` comparator (reused verbatim).

## Design (only the retrieval leg is replaced; harvest + comparator reused verbatim from numeric_entailment_v1)
- HARVEST: identical `NUM op NUM` regex over verdict_msg (same high-precision guards: left word-boundary,
  sci-notation-as-unit, relative-threshold-coefficient drop). One claim per unique (exp_key, name, lhs, op, rhs).
- RESOLVE (the REPLACED leg): walk the SAME citing metrics.json numeric leaves; find a leaf ~= lhs within a
  PRECISION-AWARE tolerance derived from the cited decimals (`0.5 * 10^-decimals`, floored by rel-tol 1e-4). Prefer
  a leaf whose key contains the cited NAME. No cross-file join, no cosine cleanup, no ambiguity gate.
- AUDIT: re-evaluate `resolved_value op rhs` via `decode_then_compare` (two exact CRT decodes) AND the Python oracle.

## Arms (per comparator seed; coverage is seed-invariant, comparator/controls salt the seed)
- `source_direct` -- MECHANISM: lhs resolves to a persisted numeric leaf in the SAME citing metrics.json. HP_SCOPE.
- `scrambled_source` -- CONTROL (the FIRING control): resolve lhs against a WRONG file (per-seed derangement). Must
  COLLAPSE. This is the load-bearing discriminator: it proves resolution is source-SPECIFIC, not coincidental.
- `random_value` -- CONTROL: resolve a RANDOM value (same precision) against the correct file (collision floor).
- `op_agreement_guard` -- GUARD: decode_then_compare op-eval == Python oracle on resolved in-range values (exact CRT
  decode; source-INDEPENDENT by construction -> a GUARD, not the discriminator).
- `scram_residue` -- CONTROL: derange residues before CRT -> comparator op-agreement collapses (CRT load-bearing).
- `entailment_holds_rate` (+ quant-faithful variant) -- REPORTED: fraction of resolved in-range cited entailments
  that evaluate TRUE vs source.
- `structured_gate` -- REPORTED (secondary): recompute op(measured,threshold)==gate_verdict for the
  structured_gate_claims adopters (retrieval-free, machine-clean; the drill's literal route-#1 demonstration).

## Pre-registered bands. HP_SCOPE = source_direct mechanism arm (scrambled_source/random_value are FLOOR controls).
HARD_PASS (mechanism; ALL required):
- `coverage_source_direct_nontrivial >= 0.60` AND `>= 5x` the 0.0328 ledger-retrieval baseline (>= 0.164)
- `coverage_lift_nontrivial_min >= 0.40` (correct-source resolution beats scrambled-source by >= 0.40)
- `scrambled_source_coverage_nontrivial_max <= 0.15` (firing control collapses)
- `op_agreement_guard_min >= 0.99` (comparator exact on resolved values)

HARD_FAIL (any):
- `coverage_source_direct_nontrivial < 0.20` (source-direct not meaningfully above the retrieval baseline)
- `coverage_lift_nontrivial_min <= 0.10` (correct-source no better than scrambled -> resolution coincidental)
- `op_agreement_guard_min < 0.90` (comparator broke on real quantized data)

CONTROL_DID_NOT_COLLAPSE: `scrambled_source_nontrivial_max > 0.15` OR `scram_residue_max > 0.72`.
DISCRIMINATOR_DID_NOT_FIRE: `n_claims < MIN_CLAIMS` (smoke 100 / full 300) OR `n_resolved_nontrivial < 30`.
MIDDLE_BAND: above HARD_FAIL floor but below HARD_PASS on >= 1 gate.

Strictly-above-floor (META_RULE_L): HP coverage 0.60 clears HF 0.20 by 0.40 (>> 5% band-width). Strict, not `>=`.

REPORTED (never gated): coverage_all, coverage_multiple_vs_ledger_retrieval, entailment_holds_rate (+ quant-faithful),
name_match_rate, source_confirmed_rate + its scrambled collapse, residual buckets, structured_gate recompute,
not_holding + unbacked audit candidates.

## The three headline numbers the Director asked for (MEASURED@local smoke 2026-07-06; canonical = remote FULL)
`MEASURED@data/exp_cert_ledger_source_direct_entailment_v1/metrics.json` (3 seeds smoke, wall 7-65s):
- COVERAGE (source-direct vs 3.3% baseline): coverage_nontrivial = 0.8151 = 24.9x the 0.0328 ledger-retrieval
  ceiling (coverage_all = 0.8561). The majority of cited claims ARE directly auditable from their source metrics.
- OP_AGREEMENT (do they hold): comparator op-agreement = 1.0000 (decode_then_compare == oracle, exact CRT decode);
  entailment_holds_rate = 0.9759 (raw) / 0.9896 (quant-faithful) of cited inequalities actually hold vs source.
- UN-AUDITABLE RESIDUAL (measured, not hidden): ~18.5% of nontrivial claims do NOT resolve (no_leaf_match=115),
  plus 22 trivial-excluded and 27 resolved-but-out-of-comparator-range. Bucketed in metrics.
- FIRING CONTROL: scrambled-source resolution collapses to nontrivial max 0.0514 (lift_min 0.7637); scram-residue
  comparator collapses to 0.4772. source_confirmed_rate 0.7894 (correct) -> 0.0466 (scrambled).
- SECONDARY: structured_gate_claims recompute agreement 1.0 (45 claims / 3 files -- the SOUND-but-tiny route #1).

## SCHEMA-VET fields
- `cardinality_ok`: EXPECTED_N_UNITS = len(seeds) (smoke=3, full=5); coverage is seed-invariant (JSON-walk), seeds
  salt the comparator codebook + scramble/random controls. Verdict counts per_unit (4 arms x seeds).
- `arms_differ_verified`: source-resolved flags hash-distinct from scrambled-source AND random-value flags (AF).
- `final_metrics_atomicity`: tmp_replace; per-seed checkpoint partials (_partial_seed_<s>.json) atomic + resumable.
- `except SystemExit: raise` before `except Exception` (no BaseException; grep-gate clean).
- `crlb_n/a`: coverage/correctness/detection test; discriminators are CONTRASTS (coverage vs scrambled collapse +
  comparator exactness), not a Gaussian noise floor. `discriminator_reachability = True`.
- `baseline_in_band` (META_RULE_AG): AG discriminator = scrambled-source collapse (not a difficulty gradient); the
  ledger-retrieval baseline (0.0328) it beats is INTENTIONALLY LOW (that low coverage is the problem being fixed),
  so AG's 0.05 floor is EXEMPT for the baseline. coverage_nontrivial is the in-band mechanism metric.
- `calibration_check`: default_ok_for_this_regime -- resolution tolerance is PRECISION-AWARE (from cited decimals;
  no tuned-for-pass free parameter). The scrambled-source collapse (0.813 -> 0.047 nontrivial) verifies the
  tolerance is not so loose that unrelated files match. Logged. Exact CRT decode for the comparator leg.
- `defensive_error_checking`: passed_all_4_patterns -- start_marker + per-seed heartbeat + crash-diagnostic
  (CELL_CRASHED metrics) + atomic metrics + run_mode assert + checkpoint/resume.
- `cell_chunked`: false -- single cell runs all seeds; coverage seed-invariant + harvest-once + wall < 5 min, so
  chunk-per-seed is unnecessary; per-seed checkpoint partials still guard against mid-run death.
- `progress_logging`: line_buffered_stdout -- sys.stdout.reconfigure(line_buffering=True) + per-seed flushed prints
  + per-seed heartbeat. Cell wall < 5 min so the 30-min heartbeat mandate does not bind.
- `positive_control`: op_agreement_guard reproduces the VET'd decode_then_compare exactness (1.0) on resolved
  claims; the comparator_selftest reproduces round-trip + op-eval + scram-residue-collapse before any full run.
- Gates A-E (composition): the cell REUSES the comparator primitive verbatim. Signal-shape: cited number -> quantize
  -> CRT phasor encode -> decode -> compare (comparator natural input) = SHAPE_MATCH. No new mechanism; the
  resolution leg is a plain deterministic JSON-walk (no HD encoding). effective_params: none swept (fixed regime).

## Compute architecture
Class (b) sequential-CPU with justification: pure numpy complex64 phasor comparator (the VET'd bit-identical CPU
reference primitive) + a deterministic JSON-walk resolution over ~950 claims. No batchable large matmul (per-claim
CRT decode is scalar; source resolution is float-compare over per-file leaf lists). Harvest (glob + json.load of
~5800 metrics.json) dominates wall (~1-3 min cold); comparator over ~790 in-range claims x 5 seeds is a few seconds.
Local smoke wall 7-65s. Not a GPU candidate. Storage strategy: no_storage_algebraic (comparator uses CRT/bind; the
source lookup is a direct file read -- no bundling, no sharding, no HD store).

## Dispatch
- SMOKE locally first (clean synthetic resolution self-test [present/absent/precision/name] + real-corpus smoke).
  DONE: HARD_PASS (see headline numbers above).
- FULL -> `remote_cpu_queue` via `tools/orchestrator/queue_add.sh` (SCP transport; comparator dependency
  `exp_math_rns_subtract_compare_v1` auto-shipped via Pattern-6 import-parse; verified). >= 5 seeds. timeout 1200s
  (well under the 14400s/4h cap; wall ~2-4 min on the remote).
- REMOTE-CORPUS NOTE: coverage is measured over whatever data/**/metrics.json the REMOTE holds (drifted repo). The
  mechanism (source-direct resolution + scramble collapse + comparator exactness) is corpus-size-invariant; the
  discriminator-fires gate (n_claims >= 300) guards against a too-sparse remote tree. If the remote harvest yields
  < 300 claims, expect DISCRIMINATOR_DID_NOT_FIRE (a valid, honest outcome, not a mechanism failure).
- FRAMING (USER-LOCKED): NARROW glass-box MONITOR -- the audit READS cell metrics + verdicts and CHECKS entailment;
  it NEVER edits the ledger, the cells, or any code; re-encode HELD. Not fluent-language, not self-improvement.

## Honest acceptable outcomes
- HARD_PASS: source-direct makes the self-audit MEANINGFUL (coverage a large multiple of 3.3%, scramble collapses,
  comparator exact) -- the expected outcome given the strong smoke.
- MIDDLE_BAND / HARD_FAIL: if the remote corpus differs enough that coverage or lift falls below band, that is a
  real bounded finding reported honestly (no smoke).
