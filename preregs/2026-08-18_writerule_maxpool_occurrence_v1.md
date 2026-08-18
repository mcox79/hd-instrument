# Pre-registration: exp_writerule_maxpool_occurrence_v1

Cell: `experiments/exp_writerule_maxpool_occurrence_v1.py`. Replaces the killed
`exp_organ_f_noncollapsing_accumulation_v1` (spherical k-means, ~9h projected) with a clustering-free
max-pool/top-k-mean scorer. Full docstring in the cell carries the complete pre-registration; this
file states PASS/FAIL bands per envelope-fail-bands discipline.

## Question
If a word's occurrences are kept separate and scored by best match (max-pool) instead of summed, does
the store stop encoding co-occurrence and start encoding substitutability?

## Two regimes, same arm set
- REGIME A (primary): dissociation AUC on `exp_dissociation_score_instrument_v1`'s own landed matched
  population (loaded from its checkpoint, not rebuilt).
- REGIME B (secondary, reported beside, never instead): hit@1 + winner composition on
  `exp_writerule_step_ladder_v1`'s decisive-arm background-fixed convention.

## Arms
A0_SUM (regression gate), S1_SINGLE_OCC (reference), M1_MAXPOOL (the arm under test),
M2_TOPK_MEAN (k in {2,3,5}), N1_MAXPOOL_RANDOM_OCC (the control that carries the claim),
N2_MAXPOOL_SIZE_MATCHED_SHUFFLE (second guard), K1/N0 (REGIME A licensing).

## Regression gates (must reproduce; EXIT ON FAILURE at `--grid full`)
- REGIME A: A0_SUM AUC = 0.0510 +/- 0.006 (DISS RAW_COUNT_FULL_ACCUM, commit 0eb44eb1d).
  S1_SINGLE_OCC AUC = 0.4173 +/- 0.006 (DISS RAW_COUNT_SINGLE_OCC), reported not hard-gated.
- REGIME B: WR.best_single_occurrence_oracle called verbatim on this cell's own idx_decisive;
  SUM_ALL hit@1 = 0.0100 +/- 0.03, RANDOM_SINGLE hit@1 = 0.0367 +/- 0.03 (WR decisive arm, commit
  3e5fde9c0). Self-consistency: this cell's own vectorised A0_SUM/S1_SINGLE_OCC hit arrays must be
  BYTE-IDENTICAL (0 mismatches) to WR's own boolean arrays on the same item subsample.

## Licensing gate (REGIME A, must PASS or publish nothing -- SystemExit)
All four floors (F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE) AUC 95% CI must
include 0.5. KNOWN_ANSWER_WORDNET_PATH_SIM AUC >= 0.95. If either fails: INSTRUMENT_STILL_LOOSE,
STOP-IF (v), SystemExit before any store-arm number is interpreted.

## STOP-IF bands (REGIME A, evaluated via paired AUC-difference bootstrap, not independent CI overlap)
- (i) PASS band: M1 vs A0 CI-separated ABOVE **and** M1 vs N1 CI-separated ABOVE -> not-collapsing is
  the fix.
- (ii) M1 vs A0 ABOVE but M1 vs N1 NOT ABOVE -> gain is the max operator, not the occurrences; no
  mechanism claim.
- (iii) M1 vs A0 NOT_SEPARATED -> not-collapsing insufficient; suspect moves to FILTER/SUPERPOSE.
- (iv) FAIL band: every arm's AUC stays below 0.5 -> no store this corpus supports encodes
  substitutability; report loudly, redirects the programme.
- (v) K1 fails -> INSTRUMENT_STILL_LOOSE, publish nothing.

## Compute architecture
Class (b) sequential-CPU with justification: REGIME A restricts everything to `words_needed` (low
hundreds, DISS's own matched-pair union); REGIME B restricts the expensive occurrence-level arms to a
bounded N_DECISIVE=300 item subsample (same order WR's own already-landed decisive arm used). No
per-anchor clustering anywhere (the killed cell's cost driver). A0_SUM/S1_SINGLE_OCC in REGIME B are
vectorised (single sparse matmul over the full item population, no python loop). Storage strategy:
sharded-by-occurrence for M1/M2/N1/N2 (explicit trade-off under test, disclosed via STORAGE HONESTY
fields), bundled (1 vector) for A0_SUM/S1_SINGLE_OCC (the incumbent construction being tested against).

## Cardinality / schema-vet declarations
- `cell_chunked`: false (single cell, both regimes run sequentially in one process, checkpointed as
  ONE unit "MAIN").
- `arms_differ_verified`: true (sha256 digest assert, both regimes).
- `final_metrics_atomicity`: tmp_replace (experiments._seed_checkpoint.write_metrics).
- `crlb_floor_computed`: n/a -- AUC/hit@1 measurement over an existing store, not a capacity sweep;
  declared explicitly.
- `baseline_in_band`: n/a -- floors are gated at chance-by-construction (DISS's own convention), not a
  0.05-0.95 baseline band.
- `progress_logging`: print_flush_true.
- `discriminator_fires` (smoke): verified -- smoke (`--grid reduced`, 40 matched pairs, N_DECISIVE=40)
  ran the REAL code path end to end in 24s, all arms produced distinct digests, K1/N0/floors licensed,
  regression numbers in the right ballpark at reduced scale (A0_SUM AUC=0.0456 vs full-scale
  expectation 0.0510 -- not hard-gated at reduced grid, by design, since n=40 pairs is far smaller
  than the full ~240).

## Prior-work check
`bash tools/substrate_query.sh "max-pool occurrence separate substitutability co-occurrence write
rule"` returned (cosine=0.4395 top hit) generic WordNet-cache entity nodes ("occurrence",
"co-occurrence") -- not a prior cell or method. Confirmed not a rediscovery: no existing cell builds a
max-pool/top-k occurrence scorer or the two occurrence-identity controls (N1/N2).
