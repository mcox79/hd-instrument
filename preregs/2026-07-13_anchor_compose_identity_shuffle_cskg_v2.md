# Pre-registration: ANCHOR_COMPOSE identity-shuffle leak-closure (CSKG held-out-ENTITY)

- **Cell:** `experiments/exp_anchor_compose_identity_shuffle_cskg_v2.py`
- **Anchor name:** `anchor_compose_identity_shuffle_cskg_v2`
- **Metrics path:** `data/exp_anchor_compose_identity_shuffle_cskg_v2/metrics.json`
- **Filed:** 2026-07-13 (exp_dev). **Follow-up (A)** to the VET-CONFIRMED CHAIN_GRADE cell
  `anchor_compose_inductive_entity_cskg_v1` (commit 06c50feac). Closes the LAST leak surface: a cross-entity
  IDENTITY-SHUFFLE must-fail control. Routes to `overnight_queue` (GPU); this is the FAST GATING rung.

## Why this cell (the last open loophole)
The confirmed cell already has ANCHOR_SCRAMBLE (shuffle the support RELATION ids) which fires cleanly
(MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.scramble_margin_vs_random = 0.00936,
vs ANCHOR margin 0.12773). SCRAMBLE breaks the relational signal but KEEPS t's OWN anchors, degrees, and support-edge
set -- so it does not test whether the anchor **IDENTITY** matters. Open loophole: could ANY plausible bundle (a real
entity's worth of anchor+relation structure) score like ANCHOR, i.e. the win is a generic "well-formed bundle"
artifact rather than an entity-specific construction? This cell closes that.

## Mechanism / new arm
`IDENTITY_SHUFFLE`: a single-cycle DERANGEMENT over the support-bearing held entities re-attributes each composed
code `E_derived` to the WRONG entity -- entity `t` receives a DIFFERENT held entity's fully-formed bundle (a real
donor's relations + degrees + anchors). Cold/no-support held rows keep their additive-fit (random-init) code, exactly
as ANCHOR does. Everything else is IDENTICAL to the confirmed cell: same additive fit (X, D), same held-out-ENTITY
split with disjoint per-entity SUPPORT/QUERY partition, same filtered-MRR rank-vs-ALL eval, same ORACLE-fire gate,
same 7 confirmed arms + this 8th. Config: k=24, epochs=500, k_core=12, support_frac=0.5, seeds=[7,13] (2 of the 3
confirmed seeds -> also a positive-control reproduction of the confirmed ANCHOR margin AT THE TEST REGIME, Gate D).

## Arms (8; scored PAIRED on the SAME held-out QUERY edges)
ANCHOR_COMPOSE (mechanism), ADDITIVE_TRANSE + ONESHOT_ROTATE (memorize controls), RANDOM_CODES (null),
ANCHOR_SCRAMBLE (relation-scramble must-fail), **IDENTITY_SHUFFLE (cross-entity must-fail, NEW)**,
ORACLE_ADDITIVE (positive control), BASELINE_POP (fit-independence).

## Pre-registered bands (primary metric = FILTERED MRR; H = MEASURED oracle headroom; picked BEFORE the run)
Let `collapse_ratio = (IDENTITY_SHUFFLE - RANDOM)_mrr / (ANCHOR - RANDOM)_mrr` (fraction of the ANCHOR margin that a
mis-attributed bundle retains). All confirmed-cell gates (ORACLE fires, scramble controlled, anchor margin >= 0.50*H,
form margin, fair low+mid stratum, not broken) still apply.
- **HARD-PASS (`HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE_IDENTITY_CLOSED`)**: all confirmed HARD-PASS gates hold **AND**
  `collapse_ratio <= 0.20` (the wrong-entity bundle retains <= 20% of the win -> the win IS entity-specific; leak
  closed). **PREDICTED** (identity-shuffle is a strictly stronger must-fail than scramble, which already collapses to
  0.0094 margin; predicted collapse_ratio ~ scramble_ratio 0.073 or lower).
- **HARD-FAIL / REFUTE (`HARD_FAIL_IDENTITY_NOT_SPECIFIC_REFUTES_CG`)**: ORACLE fires **AND** `collapse_ratio >= 0.50`
  (the wrong-entity bundle retains >= 50% of the win). This would mean the win is NOT entity-specific -> it REFUTES
  the CHAIN_GRADE verdict -> HARD escalation to Director + Skunkworks.
- **MIDDLE**: `0.20 < collapse_ratio < 0.50` (partial identity-specificity) or any confirmed gate short -> investigate
  via the anchor-support-degree stratification (IDSHUF is now in the localization report arms).
- **INCONCLUSIVE** if ORACLE does not fire or `< 20` held-out queries (same as confirmed).

## Self-test (MEASURED, local .venv, single-thread CPU, 44.6s) -- PASS, identity-shuffle COLLAPSES (adversarial)
Planted HIGH-intrinsic-dim TransE-consistent arena (n_ent=300, n_rel=6, k_lat=8, deg=3).
MEASURED@data/exp_anchor_compose_identity_shuffle_cskg_v2_selftest/metrics.json:mechanism_selftest:
- held-out **MRR**: ANCHOR=**0.40467**, ADDITIVE=0.00472, ONESHOT=0.01821, RANDOM=0.01338, SCRAMBLE=0.13595,
  **IDENTITY_SHUFFLE=0.01703**, ORACLE=0.93169, POP=0.00825.
- `idshuf_margin` (IDSHUF - RANDOM) = **0.00365**; `idshuf_collapse_ratio` = **0.0093** (retains <1% of the ANCHOR
  margin) -> `identity_collapses=True`. **Identity-shuffle collapses HARDER than scramble** (0.017 vs 0.136 MRR):
  mis-attributing the whole entity destroys more signal than scrambling only the relations (which keeps t's own
  anchors) -- exactly the predicted ordering. **The anchor IDENTITY matters.**
- 8 distinct score signatures; `validity_preflight_ok=True`; verdict=**SELFTEST_PASS**. The adversarial gate
  (`assert_discriminator_fires` on IDSHUF reaching ANCHOR) is fail-closed at self-test: if a wrong-entity bundle
  scored like the right one, the self-test would HARD_FAIL before any FULL dispatch.

## SCHEMA-VET / cell-template fields
- `arms_differ_verified: true` (8 arms; self-test 8 distinct sigs; >=5 gate).
- `final_metrics_atomicity: tmp_replace` (write_metrics + os.replace).
- `except SystemExit: raise` before `except Exception`; grep-clean (no bare except / no BaseException). VERIFIED.
- `crlb / info-ceiling`: inherited from confirmed cell -- primary metric FILTERED MRR + ceiling-RELATIVE bands;
  identity collapse_ratio is a RATIO of measured margins (dimensionless), reachable by construction whenever ANCHOR
  fires. `discriminator_reachability: true`.
- `baseline_in_band: true` (ORACLE-fires gate = ORACLE_mrr >= 3x RANDOM_mrr AND headroom >= 0.003).
- `discriminator_survives_scale: analytical_B_plus_selftest` (a mis-attributed per-entity bundle carries no signal
  about t's held edges at ANY N; the self-test fires the identity-collapse discriminator deterministically).
- `cell_chunked: false` (in-process seed loop + per-arm FitCheckpoint ckpt_every=20, outage-resumable; family
  pattern, matches confirmed v1).
- `start_marker_written / crash_diagnostic_present / heartbeat_present: true`; `per_unit_failure_class: true`.
- `calibration_check: adaptive_with_discriminator_gate` (IDSHUF_COLLAPSE_RATIO=0.20 / IDSHUF_REFUTE_RATIO=0.50
  pre-registered, NOT tuned on real data; the confirmed ceiling-relative bands unchanged).
- `progress_logging: print_flush_true`.
- `positive_control_arms`: ORACLE_ADDITIVE fires; ADDITIONALLY seeds 7+13 reproduce the confirmed ANCHOR margin at
  the test regime (Gate D positive-control-at-test-regime).

## Compute architecture
class (c) MIXED (identical to confirmed v1). IDENTITY_SHUFFLE adds one derangement + one index copy + one scoring
pass (~2% overhead over the confirmed arm set; no extra fit). device=auto (cuda on GPU host). FitCheckpoint
ckpt_every=20 -> outage-resumable. FULL fits fit-checkpointed.

## Run profiles
- **self_test** (LOCAL .venv gate, PASSED 44.6s): k=12, ep=350, 1 seed, planted arena, single-thread CPU.
- **full** (REMOTE GPU): k=24, ep=500, n_neg=128, neg_chunk=16, ckpt_every=20, k_core=12, support_frac=0.5,
  n_heldout_eval=3000, seeds=[7,13]. ~2/3 the confirmed 3-seed 3.35h -> ~2.2h; timeout 14400s (GPU variance + resume).

## Numbers provenance
- confirmed ANCHOR margin 0.12773, SCRAMBLE margin 0.00936, H=0.13681, ORACLE ratio 284x:
  MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.
- self-test identity-collapse (idshuf MRR 0.01703, collapse_ratio 0.0093):
  MEASURED@data/exp_anchor_compose_identity_shuffle_cskg_v2_selftest/metrics.json:mechanism_selftest.
