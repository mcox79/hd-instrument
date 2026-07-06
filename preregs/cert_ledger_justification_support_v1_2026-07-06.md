# Pre-registration: cert_ledger_justification_support_v1

Date: 2026-07-06
Anchor: `cert_ledger_justification_support_v1`
Cell: `experiments/exp_cert_ledger_justification_support_v1.py`
Author: hdi_exp_dev
Predecessor (leaf resolution + comparator reused verbatim): `exp_cert_ledger_source_direct_entailment_v1` (MM,
coverage_nontrivial 0.813 canonical; proved each cited NUMBER resolves against its citing metrics.json)
Comparator primitive (reused verbatim): `exp_math_rns_subtract_compare_v1` (MEASURED_MECHANISM; decode_then_compare)
Scoping: `notes/research_justification_retrieval_rung_scoping_unblocked_by_source_direct_2026-07-06.md`

## One-line
The next self-audit rung ABOVE source-direct: for a CERT CLAIM C (a cert_ledger entry's tier/verdict, whose
referent_pointer names a citing cell's metrics.json), ASSEMBLE C's machine-clean gating evidence and RE-DERIVE
whether C's recorded verdict is actually SUPPORTED by its own evidence -- flag any UNSUPPORTED certification.
Monitor-not-control: re-derives verdicts from persisted evidence, NEVER edits the ledger/cells/code.

## Prior-work check (substrate-KB concept-query, mandatory)
`bash tools/substrate_query.sh "justification retrieval assemble cert claim verdict supported by evidence ..."` ->
top hit a wordnet gloss at cosine 0.3213; nearest actual prior artifacts (a testbed brief, a routing prereg) at
0.248 (< 0.30). GENUINELY NOVEL vs the indexed substrate, not a rediscovery. It is the natural composition of
source-direct (leaf resolution) + Tier-2 numeric entailment (comparator) + the cert_ledger join (NEW).

## Design (only the ledger-join + per-claim aggregation + band-scramble control are new; resolution + comparator reused)
- TARGET: cert_ledger.jsonl entries with a `referent_pointer.metrics_path` ending metrics.json (the cert CLAIMS).
- ASSEMBLE machine-clean gating evidence per claim (two clean paths ONLY -- unambiguous, no name-match guessing):
  - PATH A structured_gate_claims: the cell's OWN declared gates {measured, threshold, op, gate_verdict}. Recompute
    op(measured,threshold) via the VET'd decode_then_compare comparator and check it reproduces gate_verdict.
  - PATH B verdict_msg cited `NUM op NUM`: REUSE source-direct's harvest + precision-aware resolution VERBATIM --
    resolve the cited measured value to a persisted leaf in the SAME citing metrics.json (quant-faithful, in-range),
    re-check the cited-as-true inequality HOLDS on the resolved source value.
- A claim is ASSEMBLABLE iff it yields >= 1 clean check; SUPPORTED iff ALL its clean checks hold.
- support_recall = supported / assemblable = fraction of cert claims whose verdict is re-derivable from (consistent
  with) its own assembled evidence.

## Why the prereg-band + bands-dict paths are DELIBERATELY EXCLUDED from the clean check (honest residual)
Recon (2026-07-06) showed a naive prereg/bands-dict re-derivation produces FALSE unsupported flags because prereg
PASS bands are multi-clause boolean (`recall>=0.90 AND fp==0 AND ...`), verdicts often gate at 3-SEED AGGREGATION
(a per-seed metrics.json legitimately fails a top-level clause), and band-key -> leaf name-matching is ambiguous.
These are NOT genuine unsupported certifications; they are the un-machine-parseable residual. So prereg bands are
EXCLUDED from the support-check and instead REPORTED (prereg_residual_probe): how many non-assemblable claims map to
a prereg + how many carry any parseable single-clause band + the naive-conflict count -- to quantify the coverage gap.

## Arms (per comparator seed; support/assembly seed-invariant, comparator codebook + deranged-band control salt seed)
- `support` -- MECHANISM: re-derive each cert claim's verdict-support from assembled evidence. HP_SCOPE.
- `adversarial_band` -- FIRING CONTROL (primary): replace each check's band with a threshold the recorded
  expectation provably VIOLATES (moved ADV_DELTA_Q=5 quantized units to the wrong side). support MUST collapse ~0.
  Load-bearing: proves the support-check actually READS the band, not vacuously passing.
- `deranged_band` -- CONTROL (secondary): replace each check's (op, threshold) with a MISMATCHED real band from
  another claim (per-seed derangement). support collapses partially.
- `op_agreement_guard` -- GUARD: decode_then_compare op-eval == Python oracle on the assembled checks (exact CRT
  decode; source-independent by construction -> a GUARD, not the discriminator).
- `scram_residue` -- CONTROL: derange residues before CRT -> comparator op-agreement collapses (CRT load-bearing).
- `genuine_unsupported` -- REPORTED headline byproduct: PASS-family claims whose OWN clean evidence does NOT hold.
- `ledger_metrics_verdict_consistency`, `assembly_buckets`, `prereg_residual_probe` -- REPORTED residual.

## Pre-registered bands. HP_SCOPE = `support` mechanism arm (adversarial_band/deranged_band are FLOOR controls).
HARD_PASS (mechanism; ALL required):
- `support_recall >= 0.95` (verdict re-derivable/consistent for >= 95% of assemblable claims)
- `n_assemblable >= 25` (enough machine-parseable gating referents; MEASURED 38)
- `adversarial_band_support_max <= 0.10` (firing control collapses; MEASURED 0.0)
- `op_agreement_guard_min >= 0.99` (comparator exact on assembled checks; MEASURED 1.0)
- `deranged_band_collapse_min >= 0.40` (secondary control collapses; MEASURED 0.53)

HARD_FAIL (any):
- `support_recall < 0.70` (assembled cited-as-true evidence mostly fails on source -> resolution/comparator fault)
- `op_agreement_guard_min < 0.90` (comparator broke on real quantized data)

CONTROL_DID_NOT_COLLAPSE: `adversarial_band_support_max > 0.10` OR `scram_residue_max > 0.72`.
DISCRIMINATOR_DID_NOT_FIRE: `n_cert_claims < 300` OR `n_assemblable < 25`.
MIDDLE_BAND: above HARD_FAIL floor but below HARD_PASS on >= 1 gate (may itself be a real finding: genuine
unsupported certifications lower support_recall -> see audit_candidates).

Strictly-above-floor (META_RULE_L): HP support 0.95 clears HF 0.70 by 0.25 (>> 5% band-width); MEASURED 1.0 clears
HP by 0.05 (> 5% of the 0.25 band). Strict, not `>=`.

REPORTED (never gated): assembly_coverage, deranged_band_support, scram_residue, ledger_metrics_verdict_consistency,
assembly_buckets, prereg_residual_probe, genuine_unsupported audit candidates.

## The headline numbers the Director asked for (MEASURED@local smoke 2026-07-06; canonical = remote FULL)
`MEASURED@data/exp_cert_ledger_justification_support_v1/metrics.json` (3 seeds smoke, wall 8.9s):
- SUPPORT-RECALL: 1.0000 over 38 assemblable cert claims (all re-derive consistent with their own evidence).
- GENUINE unsupported certifications: 0 (the meaningful positive -- where evidence is machine-assemblable, the
  substrate's certifications ARE backed by it; matches source-direct finding that records are self-consistent).
- UNSUPPORTED/UNPARSEABLE RESIDUAL (measured, bucketed): assembly_coverage 0.0396. Buckets: prose_only_no_machine_band
  920, metrics_missing 28, no_verdict_msg 2, assemblable 38. Prereg residual: 484 claims map to a prereg but only 43
  carry any parseable single-clause band (0 naive false-positives) -> prereg bands are overwhelmingly prose/multi-clause.
- FIRING CONTROL: adversarial band-flip collapses support to 0.0000; deranged-band collapse_min 0.5263; comparator
  op-agreement min 1.0000; scram_residue 0.5000. ledger_metrics_verdict_consistency 0.8698 (reported).

## SCHEMA-VET fields
- `cardinality_ok`: EXPECTED_N_UNITS = len(seeds) (smoke=3, full=5); support/assembly is seed-invariant (JSON-walk),
  seeds salt the comparator codebook + the deranged-band control. Verdict counts per_unit (4 arms x seeds).
- `arms_differ_verified`: real-band vs adversarial-band vs deranged-band supported-flag vectors hash-distinct (AF).
- `final_metrics_atomicity`: tmp_replace; per-seed checkpoint partials (_partial_seed_<s>.json) atomic + resumable.
- `except SystemExit: raise` before `except Exception` (no BaseException; grep-gate clean).
- `crlb_n/a`: coverage/re-derivation/detection test; discriminators are CONTRASTS (support vs adversarial-band
  collapse + comparator exactness), not a Gaussian noise floor. `discriminator_reachability = True`.
- `baseline_in_band` (META_RULE_AG): AG discriminator = the adversarial/deranged-band collapse (not a difficulty
  gradient). support_recall SATURATES near 1.0 BY DESIGN -- that saturation IS the meaningful positive, meaningful
  ONLY BECAUSE the band-scramble control collapses it to ~0. AG's 0.05 floor is EXEMPT for support_recall; the
  scrambled-band support (the "baseline") collapses to ~0 = well in band.
- `calibration_check`: default_ok_for_this_regime -- the cited-value resolution tolerance is PRECISION-AWARE
  (reused verbatim from source-direct; no tuned-for-pass free parameter). The adversarial collapse (1.0 -> 0.0)
  verifies the support-check reads the band. Exact CRT decode for the comparator leg.
- `defensive_error_checking`: passed_all_4_patterns -- start_marker + per-seed heartbeat + crash-diagnostic
  (CELL_CRASHED metrics) + atomic metrics + run_mode assert + checkpoint/resume.
- `cell_chunked`: false -- single cell runs all seeds; support/assembly seed-invariant + load-once + wall < 1 min,
  so chunk-per-seed is unnecessary; per-seed checkpoint partials guard against mid-run death.
- `progress_logging`: line_buffered_stdout -- sys.stdout.reconfigure(line_buffering=True) + per-seed flushed prints
  + per-seed heartbeat. Cell wall < 1 min so the 30-min heartbeat mandate does not bind.
- `positive_control`: op_agreement_guard reproduces the VET'd decode_then_compare exactness (1.0) on assembled
  checks; comparator_selftest + support_selftest (holds/not-holds/adversarial-flip/sgc) run before any full.
- Gates A-E (composition): the cell REUSES the source-direct resolution + the comparator primitive verbatim.
  Signal-shape: cited number -> quantize -> CRT phasor encode -> decode -> compare (comparator natural input) =
  SHAPE_MATCH. New leg is a deterministic ledger-join + per-claim aggregation + band-scramble (no HD encoding).
  effective_params: none swept (fixed comparator regime; seeds salt codebook + control derangement).

## Compute architecture
Class (b) sequential-CPU with justification: pure numpy complex64 phasor comparator (the VET'd bit-identical CPU
reference primitive) + a deterministic JSON-walk over 1477 ledger lines + ~900 cited metrics.json (loaded once,
cached across seeds). No batchable large matmul (per-check CRT decode is scalar; assembly is float-compare over
per-file leaf lists). Local smoke wall 8.9s. Not a GPU candidate. Storage strategy: no_storage_algebraic (comparator
uses CRT/bind; ledger + source lookups are direct file reads -- no bundling, no sharding, no HD store).

## Dispatch
- SMOKE locally first (clean synthetic support self-test [holds/not-holds/adversarial-flip/sgc] + real-corpus smoke).
  DONE: HARD_PASS (see headline numbers above).
- FULL -> `remote_cpu_queue` via `tools/orchestrator/queue_add.sh` (SCP transport). >= 5 seeds. timeout 1200s (well
  under the 14400s cap; wall ~< 1 min; corpus is SMALLER than source-direct's 5800-file glob).
- SIBLING DEPS: Pattern-6 import-parse auto-ships the DIRECT import `exp_cert_ledger_source_direct_entailment_v1.py`;
  its TRANSITIVE import `exp_math_rns_subtract_compare_v1.py` is EXPLICIT-SCP'd (Pattern-6 is non-transitive). Both
  are likely already on the remote from source-direct's own dispatch.
- REMOTE-CORPUS NOTE: support/assembly is measured over whatever cert_ledger.jsonl + data/**/metrics.json the REMOTE
  holds (drifted repo). The mechanism (support re-derivation + adversarial collapse + comparator exactness) is
  corpus-size-invariant; the discriminator-fires gate (n_cert_claims >= 300, n_assemblable >= 25) guards a too-sparse
  remote. If the remote yields < 25 assemblable, expect DISCRIMINATOR_DID_NOT_FIRE (a valid, honest outcome).
- FRAMING (USER-LOCKED): NARROW glass-box MONITOR -- re-derives verdicts from persisted evidence, NEVER edits the
  ledger/cells/code; re-encode HELD. Not fluent-language, not self-improvement. NEVER git add -A (explicit pathspec).

## Expected tier (cert-owner tiers; do NOT self-tier)
MEASURED_MECHANISM (by-construction re-derivation, monitor-not-control convention) -- same tier convention as the
rest of the self-audit ladder (source-direct + Tier-1/2/3). NOT CG (the assembly is machine-clean but the residual
is large; the meaningful positive is zero genuine unsupported + the honest coverage gap).

## Honest acceptable outcomes
- HARD_PASS: support re-derivation is meaningful (support_recall clears band, adversarial collapses, comparator
  exact, zero or few genuine unsupported) -- the expected outcome given the strong smoke.
- MIDDLE_BAND: genuine unsupported certifications lower support_recall below HP -- a REAL, honestly-reported finding
  (the audit did its job = it FOUND them); surface as VET candidates.
- HARD_FAIL / DISCRIMINATOR_DID_NOT_FIRE: comparator broke, or the remote corpus is too sparse -- reported honestly.
