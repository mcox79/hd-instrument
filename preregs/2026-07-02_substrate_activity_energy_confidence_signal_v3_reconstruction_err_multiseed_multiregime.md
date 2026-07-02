# Pre-reg — substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime

**Filed:** 2026-07-02 evening (Director main-thread; sister to M1.10 pre-reg drafted alongside)
**Author:** Director
**Anchor:** `substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime`
**Design note:** `notes/design_M1_11_confidence_header_v3_reconstruction_err_5seed_2regime_2026-07-02.md`
**Prior atoms:**
- v1 (aa8030): MB CG at 3-seed FULL, AUC=0.571
- v2 extended (0a456c030): MM_TENTATIVE, combined_5 AUC=0.754 but Skunkworks proved combiner not lifting

## Framing discipline (LOAD-BEARING)

This cell tests substrate CONFIDENCE READOUT — a signal that predicts, per query, whether the substrate's cleanup output is likely on a contaminated cluster vs a legitimate cluster. Contamination is deliberate false-fact injection into the knowledge base at fixed rate p. No English, no tokens; this is a mechanism on HDs.

Per USER-locked stochastic-noise directive 2026-06-30 + Kool 2018 PFC-effort-tracking brain analog, the substrate needs a substrate-native confidence signal to power the M1.11 Cortex Confidence Header primitive (deferred pending this cell's CG verdict).

## Regime constants (v2-identical, held for controlled comparison)

- N_DIM = 8192
- N_ITEMS_KB = 3600 (facts stored in KB)
- INTRA_COS = 0.35 (item-cluster spread)
- TOPK = 10 (contamination top-K target rate mechanism)
- N_test = 200 per (seed × regime)

## Regime constants (CHANGED vs v2 — the point of v3)

**(A) Deterministic contamination — p is FIXED per query, not observed-noisy.**

v2 rate mechanism: `n_false = int(round(p_target * n_items_kb / (topk * (1.0 - p_target))))` produces an INJECTION rate; observed per-test-query contamination rate drifts (v2 observed 0.45/0.22/0.24 across seeds despite p_target=0.40).

v3 rate mechanism: per test query, hash-of-(seed, regime, query_idx) deterministically decides whether this query lands on a contaminated cluster. Observed `contamination_rate` MUST equal target `p` EXACTLY. Skunkworks noted this as prerequisite for CG.

**(B) Two contamination regimes.**

- REGIME_LOW: p = 0.20 (moderate contamination — realistic KB noise)
- REGIME_HIGH: p = 0.50 (aggressive contamination — stress test)

Bracketed around v2's 0.40. Two regimes catch mechanism-narrowness that single-p testing hides.

**(C) Five seeds — {11, 17, 23, 29, 37}** (adds 29 + 37 over v2's {11, 17, 23}).

## Arms (4 arms × 5 seeds × 2 regimes = 40 units expected)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_RECONSTRUCTION_ERR | AUC on ||cleanup(cleanup(q)) − cleanup(q)||^2 as per-query risk score | LOAD-BEARING (target CG) |
| ARM_DELTA_E | AUC on ||cleaned − q||^2 (v1 baseline) | Report-only continuity |
| ARM_SIGMA_J | AUC on power-iteration sigma_max(J) at cleaned | Report-only continuity |
| ARM_ABLATED_RANDOM | AUC on uniform random per-query risk | Positive control: → 0.50 by construction |

**Explicitly REMOVED vs v2:** ARM_TEMP_ENTROPY, ARM_MULTI_SAMPLE_VOTE, ARM_COMBINED_5. Combiner falsified (Skunkworks); keeping falsified arms wastes compute + misleads framing.

**Cardinality target:** `EXPECTED_N_UNITS = 4 * 5 * 2 = 40`; `arms_differ_verified` required across all 40 arm-seed-regime digests.

## Metrics per arm × seed × regime

- `auc`: ROC AUC over N_test binary contamination labels
- `contamination_rate`: observed fraction of test queries on contaminated clusters (MUST equal p target)
- `arm_digest`: hash of per-query risk vector

## HP bands (HP_SCOPE: ARM_RECONSTRUCTION_ERR LOAD-BEARING; others report + control)

**HARD_PASS (CG target):**
- ARM_RECONSTRUCTION_ERR AUC ≥ 0.65 in BOTH regimes
- cross-seed cv(AUC) < 0.15 in EACH regime independently
- ARM_ABLATED_RANDOM AUC ∈ [0.45, 0.55] each of 5 × 2 = 10 combos (verifies scoring rig)
- ARM_RECONSTRUCTION_ERR arm-per-seed-per-regime digests unique (arms_differ_verified across 40 units)
- observed `contamination_rate` == target `p` EXACTLY across all 40 units (deterministic contamination verified)

**HARD_FAIL:**
- ARM_RECONSTRUCTION_ERR mean AUC < 0.60 in either regime OR
- cv ≥ 0.25 in either regime OR
- ARM_ABLATED_RANDOM AUC outside [0.40, 0.60] any unit (rig broken) OR
- observed contamination_rate deviates from target by > 0 (determinism failed)

**MIDDLE_BAND (partial):**
- AUC ∈ [0.60, 0.65) OR cv ∈ [0.15, 0.25); path forward to v4 required

## Sanity + integration gates

- ARM_ABLATED_RANDOM AUC ∈ [0.45, 0.55] every unit — pins scoring at chance
- Regime dispersion ratio: mean_AUC(REGIME_HIGH) / mean_AUC(REGIME_LOW) ∈ [0.67, 1.5] — flag regime-narrow if outside
- Cross-seed cv < 0.15 per regime — the strict test that reconstruction_err is a stable signal

## Substrate primitives called

- `k_NN_lookup` (cleanup step, called twice per query — the reconstruction operation)
- No `hd_bind` / `hd_unbind` (reconstruction is pure cleanup composition)
- Storage strategy: `SHARDED` (per USER-locked storage-strategy CG_META)

## CELL-TEMPLATE MANDATORY compliance

- `arms_differ_verified: True` (40 distinct per-unit digests)
- `final_metrics_atomicity: tmp_replace` (via `_seed_checkpoint.write_metrics`)
- `except SystemExit: raise` BEFORE `except Exception`
- `crlb_n/a`: "AUC discriminator on binary contamination; no closed-form CRLB"
- `baseline_in_band`: ARM_ABLATED_RANDOM = 0.50 by construction
- `discriminator_survives_scale`: N_DIM=8192 (matches v2 CG regime)
- HP strictly above floor: 0.65 vs 0.50 floor (0.15 margin)
- `HP_SCOPE`: ARM_RECONSTRUCTION_ERR load-bearing; others report + control
- `cardinality_ok`: 40 units
- `calibration_check`: default_ok (no learned parameters; deterministic risk score)
- `progress_logging: print_flush_true`
- `start_marker + heartbeat + crash_diagnostic`: standard

## Compute architecture

- (a) batched-CPU-torch or NumPy vectorized
- Per-(seed × regime) wall: ~10-30s (v2 was ~15s at 3 seeds)
- FULL total: ~5-10 min wall (10 combos, sequential inside one dispatch)
- Route: `remote_cpu_queue` single-dispatch; well within 1800s timeout

## Dispatch prerequisites

1. Stage 1 substrate-KB closure complete (testbed af135622)
2. Pre-reg SCHEMA-VET by Skunkworks
3. Smoke gate on local_cpu_queue (USER-locked SMOKE_ONLY_LOCAL_CPU 2026-07-01)
4. Push cell commit to origin/main before remote dispatch

## Post-verdict routing

- **HARD_PASS at CG:** author `hdlab/confidence_header.py` following M1.9 SemanticParser extraction pattern (INPUT REGIME discipline, 10 selftests, ASCII-only, no cortex.py wiring at first extract). Cortex primitive stack: M1.3-M1.10 + M1.11.
- **HARD_FAIL:** file CG_HONEST_NEGATIVE closing Option C activity/energy branch. Pivot to alternative confidence mechanism families (posterior-entropy, attention-dispersion, residual-norm per Skunkworks pointers).
- **MIDDLE_BAND:** file MM_TENTATIVE; propose v4 with either mechanism swap or scale-up (N_test 500, or 10-seed).

## Composability + META candidates

- Composes with v1 MB atom (aa8030) and v2 MM_TENTATIVE (0a456c030). v3 supersedes if CG.
- If CG at BOTH regimes with cv<0.15: candidate META atom `CONFIDENCE_SIGNAL_RECONSTRUCTION_ERR_REGIME_AGNOSTIC` — regime-invariance is a physics-law-shaped claim.
- No new META candidate at v1 if only single-regime HP.

## Priors (composable atoms already CG'd)

- Option C v1 substrate_activity_energy_confidence_signal_v1 MB CG (aa8030)
- Storage-strategy CG_META (SHARDED for compositional cells)
- k_NN_lookup primitive (CG long-standing)

## Estimated timeline (post-Stage-1-closure)

- Cell authoring: ~30-45 min (hdi_exp_dev; v2 refactor into v3 form)
- Smoke on local_cpu: ~5-15 min
- SCHEMA-VET: ~5 min (Skunkworks)
- FULL dispatch: ~10 min wall
- Landed-VET: ~5 min
- If CG → hdlab extraction: ~30 min

Total: ~1.5-2 hours end-to-end to potential M1.11 primitive.
