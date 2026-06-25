# Pre-registration: substrate_audit_trail_pipeline_v2_3seed_proper_power

**Date:** 2026-06-24
**Anchor:** substrate_audit_trail_pipeline_v2_3seed_proper_power
**Queue:** local_cpu_queue
**Lane:** 4 (substrate-product axis; auditability)
**N_DIM:** 2048; **V_CONCEPTS:** 100; **V_PREDICATES:** 8; **M_TRIPLES:** 500; **M_UNKNOWN:** 200; **Seeds:** [7, 17, 23]; **n_eval:** ~100 per arm per seed (50/50 dev/eval split)

## Scientific question

The prior cell (`substrate_audit_trail_pipeline_integration_v1`) verdict = HARD_FAIL on smoke regime (N=1024, V_C=60, V_P=5, M=80, 1 seed). Skunkworks audit 2026-06-24 cell 5 + Research synthesis identified:

- V3 prov = 0.825 in smoke; HARD_PASS bar = 0.85.
- At 1-seed smoke with n_eval=40 emitted, binomial 95% CI = +/- 0.118 around p=0.825 -> CI = [0.71, 0.94].
- The HARD_PASS bar 0.85 sits well INSIDE the CI. The smoke had no statistical power to discriminate HP from MIDDLE_BAND.
- V5-V3 delta = -0.133 is within single-seed noise floor (~6pp at this scale).

**Question this cell answers:** at properly-powered regime (binomial CI ~ +/-0.029 around HP=0.85), does the audit-trail V3/V5 mechanism clear chain-grade `provenance >= 0.85` AND `lift over NAIVE >= 0.10` AND `refuse_on_unknown >= 0.50`?

## Pre-registered HARD bands (sacrosanct)

PRIMARY: best of (`V3 provenance_accuracy`, `V5 provenance_accuracy`) mean across 3 seeds.
SECONDARY: `refuse_accuracy on unknowns` mean across 3 seeds; `lift_vs_NAIVE` derived.

- **HARD_PASS_CHAIN_GRADE**: best arm provenance >= 0.85 AND lift over NAIVE >= 0.10 AND refuse >= 0.50 AND sanity NAIVE in band.
- **MIDDLE_BAND**: best arm provenance in [0.75, 0.85) OR refuse in [0.20, 0.50).
- **HARD_FAIL_DECISIVE**: best arm provenance <= 0.70 (no lift over NAIVE within CI even at proper power; mechanism does not transfer).
- **SANITY**: ARM_NAIVE_NO_AUDIT provenance in [0.55, 0.75]. The prior cell measured 0.65 at smoke; widened band to admit moderate noise.

## Apples-to-apples checklist (master bias)

- **Lane 4 declared** (substrate-product axis; auditability).
- **ONE knob varies per arm = pipeline stage.** ALL arms share same N_DIM, V_CONCEPTS, V_PREDICATES, M_TRIPLES, seeds, codebook generation (gaussian unit-norm), tau-calibration discipline (split-half no-leakage). The only difference per arm:
  - NAIVE: no slot binding; implicit (s,p,o_pred) -> triple_id lookup.
  - V1: explicit per-triple slot_id + 2-part bundle (slot->sp key + slot->o payload).
  - V3: V1 + cleanup-verify (refuse below tau).
  - V5: V3 + payload-consistency rerank over top-K slots.
- **SINGLE primary metric** per arm: provenance_accuracy (correct source triple ID for emitted queries).
- **Pre-registered PRIMARY arm**: BEST of V3 and V5 (V3 = the audit's prior under-powered result was solidly MIDDLE; V5 = full pipeline). Best-of decision pre-registered, NOT post-hoc, because the prior cell showed V5 may not lift over V3 at smoke -> we want the BEST claim on either arm.
- **Single sanity rail**: NAIVE provenance in [0.55, 0.75] reproduces audit's 0.65 baseline +/- 0.10.
- **No transformer / LLM**: numpy + FFT-based HRR only.

## CONFOUND_AUDIT (per master bias checklist 2026-06-24)

- **F1 Fix #28 over-claim**: cell logs per-seed per-arm provenance + refuse + false_refuse; verdict_msg cites per-arm numerics; aggregate cv computed. Cert-owner re-derives off `per_seed`.
- **G1 OR-gated metric (the prior cell's bias)**: PRIMARY in this cell is best-of-(V3, V5) on a SINGLE metric (provenance); refuse is SECONDARY (also gating but on its own band, not OR'd with primary). This avoids the prior cell's OR-gate Garden-of-Forking-Paths.
- **G3 below-threshold framing**: HP_PROV_MIN 0.85 is the same bar as prior cell; we are testing the SAME claim with proper power, not lowering the bar.
- **H1 capacity-respecting tier**: M=500 triples in a (V_C * V_P * V_C) = 100*8*100 = 80000-key space gives density 0.006 (compared to v1 smoke 0.0044). At N=2048 the effective capacity is well above M; M/N ratio = 500/2048 = 0.24 (cleanup-friendly).
- **H2 saturated discriminator**: the prior cell's 1-seed n_eval=40 was the saturation; this cell explicitly de-saturates with 3 seeds x ~100 eval samples each = ~300 samples per arm in the V3/V5 eval slice.
- **H6 single-knob variation**: pipeline stage is the only knob; verified in code.
- **K-corpus**: synthetic; chance for source ID = 1/M = 0.002 (very low); NAIVE 0.65 is ~325x over chance; HP 0.85 is +20pp absolute.
- **No-padding**: 4 arms = control + V1 + V3 + V5; each informative (V1 isolates slot-binding contribution; V3 isolates cleanup-verify; V5 isolates payload-rerank).

## Power analysis (the load-bearing pre-reg)

At HP_PROV_MIN = 0.85, with 3 seeds and n_eval ~ 100 per arm per seed (50/50 dev/eval split of 200 sampled queries), total samples per arm = ~300. Binomial 95% CI around p=0.85:
- CI = 1.96 * sqrt(0.85 * 0.15 / 300) = 1.96 * 0.0206 = +/- 0.040.

The prior smoke CI was +/- 0.118 at n=40. This cell's CI is +/- 0.040 at n=300 -- can discriminate HP (0.85) from MIDDLE (0.825) at 0.6-sigma. Stricter discrimination (HP vs MB at 1-sigma): need CI <= 0.025, requiring n >= ~800. We accept the 0.6-sigma margin given local CPU time budget; if v2 lands MIDDLE_BAND with V3=0.825, v3 (a future cell) can dispatch with 5 seeds x 200 eval samples = 1000 samples for tighter discrimination.

The cell's `_selftest()` asserts the binomial CI is < 0.05 at n=3*100=300 with HP=0.85; this gates the smoke against under-powered re-dispatch.

## Smoke evidence

Smoke at N=1024, V_C=60, V_P=5, M=100, 1 seed, n_eval=100. Expected (from v1 cell precedent):
- NAIVE ~ 0.65 (within sanity)
- V1 ~ 0.70-0.75
- V3 ~ 0.80-0.85 (mid-band; structural margin from emission gate)
- V5 ~ similar to V3 or slightly lower (rerank at smoke is noise-dominated)

Smoke wall expected ~30-60s (4 arms, 1 seed, FFT-dominated).

## Timeout estimate

Per-arm operations: M-bundle build (M FFT-binds, each O(N log N) ~ 0.3ms at N=2048) = ~150ms; per-query 2 unbinds + cleanup ~ 0.5ms; per-seed-arm wall = ~150ms + 100 queries * 0.5ms = ~200ms + dev-calibration ~50ms = ~250ms per arm. V5 extra: top-K=5 rerank on ~10% of eval queries adds ~5 extra unbinds = +negligible.

Per-seed wall = 4 arms * ~250ms + setup + M_UNKNOWN evals = ~2-5s. 3 seeds = ~6-15s.

Add safety 100x: **timeout_s = 1800** (30 min budget). Realistic FULL wall ~30s.

Below PROT-021's 14400s floor; PROT-018 N/A (no _n suffix); local_cpu_queue (not GPU).

## REQUIRED_FIELDS

Cell emits: `verdict`, `verdict_msg`, `elapsed_s`, `summary`, `anchor_name`, `run_mode`, `n_seeds`, `config_version`, `config`, `aggregate`, `per_seed`.

## D1 / D2 disciplines

- **D1 roofline**: smoke at v1-precedent regime measures per-arm wall; FULL scales sub-linearly (per-arm dominated by M-bundle build at O(M N log N)). FULL_wall = smoke_wall * (2048/1024) * log(2048)/log(1024) * (500/100) = smoke_wall * 2 * 1.1 * 5 = smoke_wall * 11.
- **D2 atexit + per-seed checkpoint**: uses `_seed_checkpoint.resumable_seeds` + `write_partial` with `run_config = {"N": N_DIM, "M": M_TRIPLES, "run_mode": RUN_MODE}` PROT-021 contamination guard. `atexit` writes a heartbeat JSON on any exit path.

## How the cell's verdict maps to the Wave A scientific decision

- HARD_PASS_CHAIN_GRADE: re-classify v1 prior cell as `MIDDLE_BAND under-powered`; promote V3 audit-trail mechanism to hdlab/ as substrate-native provenance primitive.
- MIDDLE_BAND: V3 lands in the 0.75-0.85 band with proper power; the mechanism is partial. Route follow-up for a 5-seed N=4096 version (or alternative slot-binding scheme per Research drill).
- HARD_FAIL_DECISIVE: provenance <= 0.70 at proper power confirms the audit-trail substrate-native solution does NOT transfer at substrate-bipolar HRR regime; revert to META audit's L7-alt list.

## Note on cell-author honesty (Fix #28)

Verdict logic reads per-seed per-arm provenance + refuse and aggregates explicitly. Verdict_msg includes:
- NAIVE prov + sanity-in-band
- V1 prov (slot-binding alone)
- V3 prov + cv + refuse + false_refuse
- V5 prov + cv + refuse + false_refuse
- V5-V3 delta
- BEST arm + lift vs NAIVE

Cert-owner re-derives off `per_seed`; cv > 0.10 demotes any PASS to MIDDLE.

Pre-reg complete. Cell + this prereg committed BEFORE dispatch.
