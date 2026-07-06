# Pre-registration: cert_ledger_retrieval_coverage_v1

Date: 2026-07-06
Anchor: `cert_ledger_retrieval_coverage_v1`
Cell: `experiments/exp_cert_ledger_retrieval_coverage_v1.py`
Author: hdi_exp_dev
Predecessor: `exp_cert_ledger_numeric_entailment_v1` (Tier-2; landed HARD_PASS but `retrieval_hit_rate=0.0328`)

## One-line
Replace the near-vacuous exact-string retrieval leg of the Tier-2 self-audit with a CONTENT-ADDRESSABLE retrieval
(the substrate's OWN HD char-trigram encode + cosine cleanup) that connects a cited numeric claim to its backing
CERTIFIED ledger record by content; MEASURE the coverage lift AND the honest ceiling.

## Motivation (all numbers MEASURED off-disk 2026-07-06)
- `MEASURED@data/exp_cert_ledger_numeric_entailment_v1/metrics.json:arms.7.retrieval_hit_rate = 0.0328` — the
  Tier-2 audit retrieves a backing record for only ~3.3% of the numeric citations it checks, so the audit is
  near-vacuous even though the downstream numeric check is exact (op_agreement=1.0).
- `MEASURED@off-disk oracle-join`: distinct cited-inequality source cells vs ledger exp-key overlap =
  exact ~0.10, normalized(strip _smoke/_seed) ~0.15, fuzzy-substring ceiling ~0.17 (per-claim weighted; local
  tree). 548/660 (~83%) citing cells have NO backing ledger record even under fuzzy matching.
- `MEASURED@cert_ledger.jsonl schema`: rows carry {atom_id, verdict, cert_status, referent_pointer} — NO measured
  numeric value, NO threshold. `MEASURED@corpus survey`: structured `gate_claims` present in 0/5817 metrics.json.
  So a cited number has NO numeric home in the ledger; the only shared content between a claim and a record is the
  CELL IDENTITY. Content-addressable retrieval must join on cell-identity, not on the number.

## The three candidate causes (the cell MEASURES all three; Director-flagged)
- (a) CAPACITY — record-identity strings are highly near-duplicate (exp_wave14_betA_... vs exp_wave14_betZ_...);
  cleanup is a HIGH-INTERFERENCE associative readout. Diagnosed by sweeping N_DIM {4096, 8192, 16384} and reporting
  whether content recall/precision rise with dimension (`capacity_sensitive` flag).
- (b) THE LEG — exact string membership drops format-variant records (a `..._v1_smoke` claim whose backing record
  is `..._v1`). Content-addressable HD cleanup can recover them. Quantified by `coverage_lift = content - exact`.
- (c) THE CEILING — the recoverable fraction (oracle normalized-join) is the measured coverage ceiling (~0.15-0.17
  local). REPORTED, never gated. Dominant bound: ~83% of citations are non-atomized; the real fix is emitting
  structured gate_claims + atomizing more cells, NOT a cleverer retrieval mechanism.

## CROSS-CELL LAW scoping (REQUIRED, honest)
This is a NOISY ASSOCIATIVE READOUT (cleanup over encoded near-duplicate identity strings), exactly the regime where
`reference_crt_residue_helps_clean_encoding_hurts_noisy_readout_2026-07-06` predicts associative retrieval can
HARD_FAIL. If content-addressable cannot beat exact-match, or lands on the WRONG near-duplicate sibling record
(precision collapse), that is a REAL, internally-publishable bounded finding reported honestly — NOT forced to pass.

## Arms (per seed x N_DIM unit; over the SAME real claims + real ledger records)
- `exact_match` — BASELINE: raw citing exp-key is a member of the ledger key set. AG-EXEMPT low baseline (~0.03-0.10).
- `content_addressable` — MECHANISM: HD char-trigram encode of citing-cell identity; cosine top-1 cleanup over the
  HD-encoded ledger record-identity codebook; ACCEPT iff (top1_cos >= tau=0.45) AND (top1_cos - top2_cos >=
  margin=0.12) [the AMBIGUITY REFUSE-GATE: reject when the top-1 record is not clearly separated from the runner-up
  = the substrate's own confidence signal, brain-grounded]; HIT iff ACCEPT and retrieved record canon == claim
  canon (same experiment family). The naive flat-tau precision is ALSO reported (`flat_tau_precision`) as a
  transparent diagnostic exposing the CROSS-CELL-LAW near-duplicate failure the refuse-gate is designed to correct.
  NOTE (smoke-iteration provenance, honest): the flat-tau-only accept HARD_FAILed precision (~0.55) at first smoke
  2026-07-06 exactly as the CROSS-CELL LAW predicts; the margin refuse-gate was added as the principled fix and the
  cell reports BOTH so the failure mode is visible, not hidden.
- `scrambled_index` — CONTROL: permute record-identity<->slot; retrieval must collapse.
- `random_baseline` — CONTROL: random record pick; ~ recoverable_frac / n_records.
- `op_agreement_guard` — GUARD: on in-range content-ACCEPTED claims, the VET'd decode_then_compare op-eval must
  still equal the Python oracle (~1.0), so coverage is not bought by dropping hard-to-check claims.
- `ceiling` — REPORTED: recoverable fraction (the measured coverage ceiling).

## Pre-registered bands (RELATIVE; robust to remote-vs-local corpus-size drift). HP_SCOPE = content_addressable arm.
HARD_PASS (mechanism):
- `content_recall_within_recoverable_min >= 0.80` (recovers >=80% of records that EXIST)
- `content_precision_min >= 0.90` (of accepted matches, >=90% land on the correct experiment)
- `coverage_lift_min >= +0.03` (content beats exact per-claim by >= 3 pts absolute)
- `scrambled_index_hit_rate_max <= 0.03` (control collapses)
- `op_agreement_guard_min >= 0.99` (comparator still exact on retrieved claims)

HARD_FAIL (any):
- `coverage_lift_min <= 0.0` (content-addressability adds nothing — the gap is NOT the leg)
- `content_precision_min < 0.75` (noisy readout returns wrong sibling records — CROSS-CELL LAW failure)
- `content_recall_within_recoverable_min < 0.50` (cannot find half the existing records)
- `scrambled_index_hit_rate_max > 0.10` (control did not collapse — retrieval not load-bearing)

MIDDLE_BAND: above the HARD_FAIL floor but below HARD_PASS on >=1 gate.

Strictly-above-floor (META_RULE_L): HP recall 0.80 clears HF 0.50 by 0.30 (>> 5% band-width); HP precision 0.90
clears HF 0.75 by 0.15. Bands strict, not `>=` floors.

REPORTED (never gated): `ceiling_recoverable_frac` (the measured coverage ceiling), `capacity_sensitive`,
per-N_DIM recall/precision, mean cosine (recoverable vs unrecoverable).

## Discriminator-fires gates (all modes)
- `n_claims >= MIN_CLAIMS=120`; `n_recoverable >= MIN_RECOVERABLE=20` (else DISCRIMINATOR_DID_NOT_FIRE).
- scrambled-index control MUST collapse (<= HF_SCRAMBLED_HIT=0.10) or HARD_FAIL.
- smoke must show `content > exact` (lift_min > 0) AND scrambled collapse AT FULL-family N_DIM {2048, 4096}.

## SCHEMA-VET fields
- `cardinality_ok`: EXPECTED_N_UNITS = len(seeds) * len(n_dims). smoke=2*2=4, full=5*3=15. Verdict counts per_unit.
- `arms_differ_verified`: content vs scrambled retrieved-id hashes distinct in >=1 unit (META_RULE_AF).
- `final_metrics_atomicity`: tmp_replace.
- `except SystemExit: raise` before `except Exception` (no BaseException; grep-gate clean).
- `crlb_n/a`: retrieval-coverage / associative-readout test; discriminators are CONTRASTS (lift + scrambled
  collapse + precision), not a Gaussian noise floor. `discriminator_reachability = True`.
- `baseline_in_band` (META_RULE_AG): AG discriminator = scrambled-control collapse (not a difficulty gradient); the
  exact_match baseline is INTENTIONALLY LOW (that low coverage is the finding), so AG's 0.05 floor is EXEMPT for it.
- `calibration_check`: default_ok_for_this_regime — the content ACCEPT gate is a FIXED cosine floor tau=0.45 + a
  FIXED ambiguity margin=0.12 (no label leakage). Self-test measures bag-of-trigram cosine: suffix-variant-of-self
  (min_same ~0.67) >> unrelated (max_cross ~0.21); tau sits cleanly between, and the margin gate REFUSES an
  ambiguous unbacked-sibling claim (perfect synthetic precision) that flat-tau would false-accept. Logged;
  scrambled-collapse verifies the discriminator still fires.
- `positive_control`: op_agreement_guard reproduces the VET'd decode_then_compare exactness on the retrieved subset.
- `defensive_error_checking`: start_marker + heartbeat + crash-diagnostic + atomic metrics + run_mode assert.
- `progress_logging`: print_flush_true (line_buffered stdout + per-unit flushed prints); cell wall < 30 min so the
  30-min heartbeat mandate does not bind, but per-unit heartbeat + prints are emitted.
- `positive_control_arms` / gates A-E (composition): the cell COMPOSES char_trigram_v1 + cleanup + the comparator
  guard. Signal-shape: identity-string -> HD vector (encoder natural output) -> cosine top-1 (cleanup natural
  input) = SHAPE_MATCH. Comparator guard reproduces its MEASURED_MECHANISM exactness at this regime (op guard >=0.99).

## Compute architecture
Class (b) sequential-CPU with justification: pure numpy bipolar HD + one batched cosine matmul per unit (no matmul
in a python loop — encode_batch then a single `claims_unit @ rec_unit.T`). n_records ~950, n_claims ~500-950,
N_DIM <= 16384; per-unit wall ~1-3s. Not a GPU candidate (small; the substrate primitive here is text-encode +
cosine, not a large batched sweep). Storage strategy: SHARDED (each ledger record its own HD identity vector; no
bundling) — correct per the composition-depth storage law (retrieval over distinct records).

## Dispatch
- SMOKE locally first (clean synthetic separation self-test + real-ledger smoke). On clearance, >=5-seed FULL.
- FULL -> `remote_cpu_queue` via `tools/orchestrator/queue_add.sh` (referent-declaring cell; PROT-022 referent
  `data/substrate_index/meta/cert_ledger.jsonl` resolved on-remote after this session's deploy). No `_n<N>` suffix
  (no PROT-018/019). timeout well below PROT-021 4h floor.
- FRAMING (USER-LOCKED): NARROW glass-box MONITOR — retrieves + checks OWN certified records; never edits the
  ledger or any code; re-encode HELD. Not fluent-language, not self-improvement.

## Local smoke result (MEASURED 2026-07-06; preview, canonical = remote FULL)
`MEASURED@data/exp_cert_ledger_retrieval_coverage_v1_smoke/metrics.json` (2 seeds x N_DIM {2048,4096}, wall 95.6s):
- exact=0.1102, content=0.1427, ceiling=0.1563, lift_min=+0.0325 -> content-addressable DOES beat exact (leg (b)
  recovers format-variant records; recall_min within-recoverable = 0.913).
- precision (margin-gated) min=0.687; precision (naive flat-tau) min=0.546 -> the refuse-gate lifts precision by
  ~0.14 but it STILL falls below HF_CONTENT_PRECISION=0.75 -> HARD_FAIL. mean margin: recoverable 0.42 vs
  unrecoverable 0.046 (clean on average, but an unbacked tail of version/rescue-variant siblings passes the gate).
- scrambled_max=0.0000 (control collapses cleanly); op_guard=1.0 (comparator exact on retrieved claims).
- cap[recall 0.913->0.913, precision 0.692->0.689]; capacity_sensitive=FALSE -> raising N_DIM does NOT help.
- HONEST READ: this is the CROSS-CELL-LAW noisy-readout bound. Content-addressable identity retrieval gives a real
  recall lift but is NOT a trustworthy audit leg (precision 0.69 << needed), and the gap is NOT capacity. The FULL
  extends N_DIM to 16384 + 5 seeds as the canonical confirmation of capacity-insensitivity + variance.

## Expected outcome (HYPOTHESIZED, not measured)
- content_addressable recovers the format-variant records exact-string drops -> a real but SMALL lift
  (HYPOTHESIZED@this prereg: exact ~0.10 -> content ~0.15 per-claim locally).
- The MEASURED CEILING (~0.15-0.17 local) is the honest headline bound: the audit's coverage is dominated by
  finding (c) genuine claim-to-record mismatch (non-atomized cells), NOT by the retrieval mechanism.
- Capacity (a): near-duplicate cleanup MAY be capacity-sensitive; the N_DIM sweep measures it.
- Honest acceptable outcomes: a measured lift (HARD_PASS/MIDDLE_BAND) OR a measured bound (HARD_FAIL if content
  cannot beat exact or returns wrong siblings). Either is a real finding.
