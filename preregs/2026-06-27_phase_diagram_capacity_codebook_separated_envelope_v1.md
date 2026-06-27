# Pre-registration: phase_diagram_capacity_codebook_separated_envelope_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M)
**Trigger:** Research drill 2026-06-27 Section 6 (`notes/research_drill_capacity_codebook_vs_envelope_separation_2026-06-27.md`). Skunkworks batch 7 demoted prior `phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1` HARD_FAIL -> MEASURED_MECHANISM with finding `rec=1.0 iff (alpha_VC<=4.10 AND keys_unique_mode=unique_sr)`. The envelope axis is confounded with codebook-exhaustion axis; this cell separates them orthogonally.

## Anchor

`phase_diagram_capacity_codebook_separated_envelope_v1`

## Routing

- **Queue:** `overnight_queue` (GPU; remote_gpu via hdi_orchestrator) — USER 2026-06-27 NO LOCAL directive
- **Reason:** N_DIM=16384 -> Hebbian W is 16384x16384 fp32 = 1.07GB per arm; largest mech cell (alpha_N=8 headroom=10x) has V_C=40960, E tensor ~2.6GB at fp32. Matmul-heavy at N=16384.
- **GPU mandate (Fix #24):** module declares `DEVICE='cuda'` and full branch asserts `torch.cuda.is_available()` (fails with `[FATAL] full-mode requires CUDA` if not). Smoke uses N=2048 (W=16MB).
- **Push gate:** harness-DENIED to exp_dev; cell + pre-reg COMMITTED locally; Orchestrator handles push + `tools/queue_add.py overnight_queue`.
- **NO LOCAL smoke** (USER 2026-06-27): smoke runs on remote via queue_add `_smoke` variant; drill's "smoke locally first" superseded.

## Source

Inherits primitives + harness structure from `experiments/exp_phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1.py` (bipolar codebook, Hebbian W, argmax cleanup, per-key resumable checkpoint, atexit metrics synth). Extends per drill Section 6:
- Replaces 1D (V_C, M_FACTS) sweep with joint 2D (alpha_N, codebook_headroom) phase diagram
- Adds per-arm HP-scope declaration (NEW SCHEMA-VET item)
- Adds BIAS-S runtime regime assertions (META_RULE_J halt on drift)
- Adds BARE_E_R_ENCODER + MULTI_BANK_PROBE arms
- Tightens KNN_SENTINEL sigma 0.30 -> 0.10 (drill: prior was HP mis-spec)
- Locks PREDICTED_SURFACE dict per drill Section 2.5

## Hypotheses (drill Section 2.2)

- **H1 (codebook axis):** at alpha_N<=1 + W well within capacity, recall depends monotonically on `codebook_headroom = V_C*V_R/M`. Headroom>=10x -> rec>=0.95; headroom<=1.0 -> rec<0.7. Sharp transition near headroom=1.0.
- **H2 (envelope axis):** at headroom fixed >=10x (zero duplicate keys), recall holds rec>=0.95 up to alpha_N* where W-crosstalk degrades. Predicted alpha_N* ~2-3 with raw encoder; smooth (NOT cliff) beyond alpha_N=4.
- **H3 (interaction):** (headroom, alpha_N) phase boundary approximately rectangular; codebook axis is sharp; envelope axis is smooth.

## Arms (joint 2D sweep — 23 cells * 3 seeds = 69 units)

### Mechanism phase cells (20)

Axis A (codebook_headroom): `{10x, 2x, 1.0x, 0.5x}`
Axis B (alpha_N = M/N): `{0.5, 1.0, 2.0, 4.0, 8.0}`
N=16384 (fixed), V_R=32 (fixed)

| alpha_N | M_facts | headroom=10x V_C | headroom=2x V_C | headroom=1.0x V_C | headroom=0.5x V_C |
|---------|---------|------------------|-----------------|-------------------|-------------------|
| 0.5 | 8192 | 2560 | 512 | 256 | 128 |
| 1.0 | 16384 | 5120 | 1024 | 512 | 256 |
| 2.0 | 32768 | 10240 | 2048 | 1024 | 512 |
| 4.0 | 65536 | 20480 | 4096 | 2048 | 1024 |
| 8.0 | 131072 | 40960 | 8192 | 4096 | 2048 |

All 20 mech cells within V_C_CAP=200k. No SKIPs (drill predicted; cell asserts `n_skipped == 0` in selftest).

### Sentinel + control arms (3 cells * 3 seeds = 9 units)

- **KNN_SENTINEL**: sigma=0.10 (drill tightening); V_C=4000; predicted rec>=0.95. **HP_KNN_SENTINEL=0.95 SCOPED to this arm**.
- **BARE_E_R_ENCODER**: skip W; retrieve via E @ E.T cosine directly; predicted rec=1.000. **HP_BARE_E_R=0.99 SCOPED to this arm**.
- **MULTI_BANK_PROBE**: K=4 banks at (alpha_N=4.0, headroom=10x); RC-4 co-ship probe (drill Section 4). NO HP gate; early signal only.

### Total

```
EXPECTED_N_UNITS = (20 mech + 1 KNN + 1 BARE + 1 multi-bank) * 3 seeds = 69
```

META_RULE_H: `HARD_FAIL_CARDINALITY_BREACH` if observed_units < 69.

## Per-arm HP scope DECLARATION (NEW SCHEMA-VET item, drill 2.4)

```yaml
HP_SCOPE:
  MECH:         []  # mechanism cells exempt; band per PREDICTED_SURFACE
  KNN_SENTINEL: [HP_KNN_SENTINEL >= 0.95]   # scoped this arm
  BARE_E_R:     [HP_BARE_E_R     >= 0.99]   # scoped this arm
  MULTI_BANK:   []  # probe; no gate
  SMOKE:        []  # smoke probes; verdict via SMOKE_PASS criterion
```

Mechanism arms exempt from HP gates — this eliminates the prior cell's HP-gate-mis-spec where `HP_KNN_SENTINEL=0.90 sigma=0.3` HARD_FAILed on a noise floor unrelated to the mechanism.

## Predicted surface (drill 2.5; LOCKED at module init as `PREDICTED_SURFACE` dict)

| alpha_N \ headroom | 10x | 2x | 1.0x | 0.5x |
|---|---|---|---|---|
| 0.5 | 0.99-1.00 | 0.99-1.00 | 0.65-0.75 | 0.45-0.55 |
| 1.0 | 0.99-1.00 | 0.95-1.00 | 0.55-0.65 | 0.40-0.50 |
| 2.0 | 0.95-1.00 | 0.85-0.95 | 0.45-0.55 | 0.30-0.40 |
| 4.0 | 0.75-0.90 | 0.60-0.80 | 0.35-0.45 | 0.20-0.30 |
| 8.0 | 0.40-0.65 | 0.30-0.55 | 0.20-0.30 | 0.15-0.25 |

Verdict compares per-cell rec_mean to predicted band (+/- 0.05 tolerance). Stored in metrics.json `detail.surface[<cell>].in_predicted_band`.

## Verdict logic (drill 2.6)

| Verdict | Condition |
|---------|-----------|
| `CHAIN_GRADE_BOTH` | envelope HP (10x-headroom column, alpha_N in {0.5, 1.0, 2.0}: 3 cells, rec_mean>=0.95 cv<=0.05) AND codebook separation (1.0x AND 0.5x columns each below 10x by delta>=0.20 at 3+ matched alpha_N) |
| `MIDDLE_BAND_ENVELOPE_PASS_CODEBOOK_NOISY` | envelope HP but codebook matches<3 |
| `MIDDLE_BAND_CODEBOOK_PASS_ENVELOPE_NOISY` | codebook separation but envelope misses |
| `MIDDLE_BAND_NEITHER_CRITERION` | neither (band-floor result; META_RULE_L) |
| `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` | observed_units < 69 |
| `HARD_FAIL_UNIT_EXCEPTION` | any per-unit exception (META_RULE_J; halts loop) |
| `HARD_FAIL_SUBSTRATE_ONLY` | LLM calls > 0 |
| `HARD_FAIL_SCOPED_HP_KNN_SENTINEL` | KNN_SENTINEL mean < 0.95 (scoped) |
| `HARD_FAIL_SCOPED_HP_BARE_E_R` | BARE_E_R mean < 0.99 (scoped) |

Default verdict-classification = MIDDLE_BAND per band-floor discipline; Skunkworks tiers UP to CHAIN_GRADE_BOTH only when BOTH criteria satisfied.

## BIAS-S regime-check (runtime assertions, META_RULE_J halt)

For each mechanism cell at run-time:

```python
observed_alpha_N    = M / N
observed_headroom   = (V_C * V_R) / M
assert abs(observed_alpha_N - target_alpha_N)    < 0.01      # BIAS_S_ALPHA_N_DRIFT
assert abs(observed_headroom / target_headroom - 1.0) < 0.05  # BIAS_S_HEADROOM_DRIFT
assert keys_unique_mode == ("unique_sr" if target_headroom >= 1.0
                             else "duplicates_allowed")        # BIAS_S_KEY_MODE_MISMATCH
```

Any drift halts the loop (META_RULE_J no silent-except).

## Smoke discipline (drill 2.7; three smoke-disciplines 2026-06-26)

Three smoke discriminator probes at N=2048 (smoke variant; runs on remote per USER NO LOCAL):
- **S1 (envelope discriminator)** alpha_N=2.0 headroom=10x: predicted rec >= 0.95
- **S2 (codebook discriminator)** alpha_N=1.0 headroom=0.5x: predicted rec ~ 0.45
- **S3 (baseline)** alpha_N=0.5 headroom=10x: predicted rec = 1.000

Plus KNN_SENTINEL + BARE_E_R_ENCODER at smoke scale = 5 smoke units total (`EXPECTED_N_UNITS` smoke = 5; selftest verifies).

**SMOKE_PASS criterion (LOCKED):** S1 >= 0.90 AND S3 >= 0.99 AND S2 in [0.35, 0.55] AND substrate_only_ok AND knn_ok AND bare_ok AND cardinality_ok.

Smoke FIRES the discriminator at three distinct hypothesis points — META_RULE_K compliant.

## Discriminator-must-survive-scale (USER 2026-06-26)

**Check option B (analytical justification):** Drill predicts alpha_N=2 headroom=10x: rec in [0.95, 1.00] at N=16384 (envelope holds); alpha_N=1.0 headroom=0.5x: rec ~ 0.45 (codebook dilution at any N because the 1/duplicates ratio is N-invariant). Both discriminator predictions are analytically grounded; smoke at N=2048 verifies the prediction floor and full at N=16384 carries the same discriminator physics.

**Check option C (full-N preview):** Smoke S1 at N=2048 predicts >=0.95 because alpha_N=2 with headroom=10x is comfortably within W capacity at any N; if S1 fails substrate has a fundamental envelope problem detectable at any scale.

## Self-test (selftest discipline; required pre-dispatch)

```bash
python experiments/exp_phase_diagram_capacity_codebook_separated_envelope_v1.py --self-test
```

Tests (T1-T12 in `_selftest`):
- T1: bipolar codebook shape + norm
- T2: unique_sr branch in make_facts
- T3: duplicates_allowed branch fires at M > V_C*V_R
- T4: eval_recall_at_cell end-to-end correctness + alpha_N + headroom + keys_unique_mode fields
- T5: KNN_SENTINEL at tightened sigma=0.10 -> rec>=0.95
- T6: BARE_E_R_ENCODER -> rec>=0.99
- T7: BIAS-S regime-check (positive + 3 negative cases)
- T8: bands LOCKED (HP_KNN, HP_BARE, CV_MAX, KNN_SIGMA, V_R)
- T9: LLM call counter = 0
- T10: cardinality + SKIP registry math (full: 20 phase + 0 skipped + 1 KNN + 1 BARE + 1 multi-bank = 69 units)
- T11: PREDICTED_SURFACE covers full 4x5 grid
- T12: multi-bank ingest path works

**SELFTEST RESULT (laptop CPU 2026-06-27):**
```
[selftest] PASS unique_sr_rec=1.000 knn=1.000 bare=1.000 multibank=1.000 n_phase=20 n_skip=0 EXPECTED_N_UNITS=69 gpu=False
[self-test] PASS; exiting
```

All T1-T12 GREEN.

## Config (LOCKED)

- N_DIM = 16384 (full); 2048 (smoke)
- V_R = 32 (drill default; clean OOM margin vs prior V_R=8)
- ALPHA_N_AXIS = [0.5, 1.0, 2.0, 4.0, 8.0]
- HEADROOM_AXIS = [(10x, 10.0), (2x, 2.0), (1.0x, 1.0), (0.5x, 0.5)]
- V_C_CAP = 200_000 (OOM safety; max V_C in this sweep = 40960)
- Seeds: [11, 13, 19] (full); [11] (smoke)
- HP_KNN_SENTINEL = 0.95 (scoped)
- HP_BARE_E_R = 0.99 (scoped)
- HP_ENVELOPE_REC_MIN = 0.95
- HP_ENVELOPE_ALPHAS = [0.5, 1.0, 2.0] (at headroom=10x)
- HP_CODEBOOK_DELTA = 0.20
- HP_CODEBOOK_MIN_MATCHES = 3
- CV_MAX = 0.05
- KNN_SENTINEL_SIGMA = 0.10 (tightened from prior 0.30)
- MULTI_BANK_PROBE_K = 4 at (alpha_N=4.0, headroom=10x)
- Encoder provenance: SUBSTRATE_NATIVE
- Substrate-only decode (zero LLM calls asserted)

## ETA + Timeout (drill Section 5)

Per-unit GPU walltime estimates:
- Small cells (alpha_N <= 2, headroom <= 2x, V_C <= 10240): ~40-60s per unit
- Mid cells (alpha_N = 4 or headroom = 10x small V_C): ~60-90s per unit
- Large cells (alpha_N = 8 headroom = 10x: V_C=40960, M=131072): ~5-10 min per unit
- KNN_SENTINEL + BARE_E_R: ~2-5s per unit
- MULTI_BANK at K=4: ~4x mech cell wall ~4-8 min

Total estimate: ~90-150 min on RTX 4060 Ti.

**Timeout: 12000s (200 min)** — generous margin over 150-min upper estimate; covers per-key resume + atexit synth. Anchor name contains no `_n<N>` suffix; PROT-019 floor not triggered.

## Skip-rationale registry (transparency)

At V_R=32 V_C_CAP=200k all 20 (alpha_N, headroom) mech cells fit (`len(_SKIP_REGISTRY)==0` asserted in T10). Skip registry persisted to `metrics.json detail.skip_registry` regardless. If V_R is later tuned downward or V_C_CAP changes, SKIPs would appear and be transparent.

## Anti-bias checklist (drill Section 6)

- **BIAS-S regime-check:** runtime assertions on every mech cell (above)
- **BIAS-14 mismatch:** PREDICTED_SURFACE locked pre-reg; verdict references directly
- **BIAS-O basis-vs-use-case:** encoder labels at READOUT (E @ states), not basis
- **BIAS-Q "suspect 1.000":** verdict treats 1.000 as valid only when codebook headroom guarantees it AND cv=0 AND BIAS-S passes
- **Verify-the-referent:** cell asserts metric schema; verdict reads `surface` dict not `verdict_msg` string (Fix #28)
- **Per-arm HP-scope (Skunkworks batch 7):** mechanism arms exempt; only KNN + BARE carry HP gates
- **Symmetric anti-negativity:** does NOT inflate; envelope claim past alpha_N=2 NOT pre-claimed
- **Discriminator survives scale (USER 2026-06-26):** option B analytical justification (above)
- **Three smoke disciplines (USER 2026-06-26):** no silent-except (META_RULE_J halt); smoke fires discriminator (S1+S2+S3); band-floor is MIDDLE_BAND not HARD_PASS
- **CARDINALITY_OK mandatory (META_RULE_H):** EXPECTED_N_UNITS=69; SKIP registry transparent

## Why this matters

Prior cell (`phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1`) demoted to MEASURED_MECHANISM because its 9 phase points confounded codebook-exhaustion with weight-matrix envelope. The 5/9 cells holding rec=1.000 were ALL `unique_sr` (codebook un-exhausted); the 4/9 collapsed cells were ALL `duplicates_allowed`. This cell orthogonally varies both axes so the substrate envelope claim is no longer confounded.

Outcomes (drill Section 7; P calibrated, sum=1.00):
- **Outcome 1 (P~0.55):** clean envelope to alpha_N=2 confirmed; codebook fully separated. CHAIN_GRADE_BOTH.
- **Outcome 2 (P~0.25):** envelope extends past alpha_N=2 (e.g. to alpha_N=4) at 10x headroom. CHAIN_GRADE_BOTH + extension finding.
- **Outcome 3 (P~0.15):** envelope cliffs sharply just past alpha_N=2. CHAIN_GRADE_envelope-at-alpha=2; valuable negative result for smooth-degradation claim.
- **Outcome 4 (P~0.05):** unexpected (codebook mechanism more complex than predicted; OR cv>0.05 at 10x). MIDDLE_BAND + diagnostic follow-up.

This cell unblocks RC-1 (encoder whitening) and RC-4 (multi-bank) follow-on cells (drill Section 4) by establishing the clean (alpha_N, headroom) baseline grid against which RC interventions are measured.
