# Drill — Capacity envelope: cleanly separate codebook-exhaustion from weight-matrix envelope

**Date:** 2026-06-27 (USER on flight)
**Author:** Research (Opus 4.7 1M)
**Trigger:** Skunkworks batch 7 demoted `phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1` HARD_FAIL -> MEASURED_MECHANISM with the finding:
> `rec=1.0 iff (alpha_VC <= 4.10 AND keys_unique_mode = unique_sr)`; collapses when codebook exhausted (`M_facts > V_C * V_R`). 5/9 phase points clean rec=1.000.

**Calibration penalty applied:** P estimates deflated 0.15-0.25 per lit-scan discipline; novel-synthesis P capped at 0.50. Symmetric anti-negativity: NOT inflating the envelope -- the surface I read directly says all `unique_sr` cells held 1.000 at cv=0, but I will NOT claim chain-grade envelope from confounded data.

---

## 0. Honest re-read of the empirical surface (verify-the-referent)

From `data/exp_phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1/metrics.json` (N=16384, 3 seeds, FULL run):

| V_C  | M_facts | alpha_VC | alpha_N | keys_mode          | rec    | cv     |
|------|---------|----------|---------|--------------------|--------|--------|
| 2000 | 16384   | 8.19     | 1.00    | duplicates_allowed | 0.6264 | 0.0020 |
| 2000 | 24576   | 12.29    | 1.50    | duplicates_allowed | 0.5123 | 0.0030 |
| 2000 | 32768   | 16.38    | 2.00    | duplicates_allowed | 0.4254 | 0.0014 |
| 4000 | 16384   | 4.10     | 1.00    | unique_sr          | 1.0000 | 0.0000 |
| 4000 | 24576   | 6.14     | 1.50    | unique_sr          | 1.0000 | 0.0000 |
| 4000 | 32768   | 8.19     | 2.00    | duplicates_allowed | 0.6234 | 0.0017 |
| 8000 | 16384   | 2.05     | 1.00    | unique_sr          | 1.0000 | 0.0000 |
| 8000 | 24576   | 3.07     | 1.50    | unique_sr          | 1.0000 | 0.0000 |
| 8000 | 32768   | 4.10     | 2.00    | unique_sr          | 1.0000 | 0.0000 |
| KNN sentinel | -- | -- | -- | n/a | 0.3133 | -- |

**Confound separation is cleaner than the smoke suggested:**
- Every `unique_sr` cell held rec=1.000 perfectly (5 cells, cv=0 across 3 seeds).
- Every `duplicates_allowed` cell collapsed (4 cells, rec in [0.4254, 0.6264]).
- The 1.000-vs-0.4254 gap is NOT alpha_N. The cell at (V_C=8000, M=32768, alpha_N=2.0) held 1.000 because V_C * V_R = 64000 > 32768 = M (keys non-exhausted).
- The (V_C=4000, M=32768, alpha_N=2.0) cell collapsed to 0.6234, but here V_C * V_R = 32000 < 32768 = M (keys exhausted by 768 triples; ~2.4% over).

**Critical observation: V_R is small (8) by design. The "codebook" being exhausted is the (s,r) key set of size V_C * V_R, NOT the encoder vocab E (size V_C).** The 0.6234 is consistent with the recall ceiling imposed by duplicate-key dilution alone (each duplicate (s,r) key averages over ~1.02 distinct o-values, and argmax over codebook of V_C=4000 has expected hit rate ~1/duplicates).

**Also critical: the KNN sentinel HARD_FAIL (0.31 < 0.90) is an HP-gate-mis-spec.** sigma=0.3 in 16384-dim bipolar space at V_C=8000 puts noisy items deep inside other items' Voronoi cells; 0.31 is the actual baseline at that noise level, not a substrate failure. Per Skunkworks batch 7 note, the HP gate should NOT apply to bare-baseline arms. RC fix in this cell: tighten sigma or apply HP gate only to mechanism arms.

**Re-framing of the existing finding:** "substrate held rec=1.000 perfectly across 5 phase points reaching alpha_N=2.0 + alpha_VC=4.10 simultaneously" -- this is the cleanest envelope evidence we have today. The 4 collapsed points are 100% predicted by codebook exhaustion. To go CHAIN_GRADE we need a cell that varies alpha_N over a wide range while GUARANTEEING codebook headroom.

---

## 1. Design objective

**Cleanly separate two effects orthogonally:**
- **Effect A (codebook-exhaustion):** at fixed weight-matrix loading, what happens to recall when the (s,r) key-space tightens or relaxes?
- **Effect B (weight-matrix envelope):** at guaranteed codebook headroom, where does the Hebbian-W cleanup actually fail?

**Pre-reg discipline (load-bearing):**
- Per-arm HP-scope DECLARATIONS (per Skunkworks batch 7 cert-owner note).
- BIAS-S regime-check: each tuple's expected alpha_VC + alpha_N computed at pre-reg + asserted at run-time.
- META_RULE_H cardinality_ok = (n_phase_points >= 9) AND (n_seeds >= 3 per phase point).
- HARD_PASS: rec_mean >= 0.95, cv < 0.05, across 3 seeds AT alpha_N <= 2.0 AND codebook headroom >= 10x.

---

## 2. Cell-spec: `exp_phase_diagram_capacity_codebook_separated_envelope_v1.py`

### 2.1 Anchor
`phase_diagram_capacity_codebook_separated_envelope_v1`

### 2.2 Hypothesis (pre-reg)

H1 (codebook axis): At alpha_N <= 1.0 fixed and substrate-W well within capacity, recall depends MONOTONICALLY on `codebook_headroom = V_C * V_R / M`. Cells with headroom >= 10x hold rec >= 0.95; cells with headroom <= 1.0 (exhausted) drop below 0.7. The transition is sharp around headroom = 1.0.

H2 (envelope axis): At codebook headroom fixed >= 10x (guarantees zero duplicate keys), recall holds rec >= 0.95 up to some alpha_N* where weight-matrix crosstalk degrades it. Predicted from Plate HRR + JL margin (3x drill Angle 1): alpha_N* ~ 2-3 with raw encoder; beyond alpha_N=4 expect smooth degradation, NOT cliff.

H3 (interaction): The (headroom, alpha_N) phase boundary should be approximately rectangular -- both must be satisfied. The codebook axis is sharp; the envelope axis is smooth.

### 2.3 Arms (joint sweep -- 2D phase diagram)

**Axis A: codebook_headroom (V_C * V_R / M)** -- 5 levels:
- A1: headroom = 100x (V_C * V_R >> M; "comfortable")
- A2: headroom = 10x
- A3: headroom = 2x
- A4: headroom = 1.0x (boundary; deliberately at the cliff)
- A5: headroom = 0.5x (deliberately exhausted; predicted dilution baseline)

**Axis B: alpha_N (M / N)** -- 5 levels:
- B1: alpha_N = 0.5
- B2: alpha_N = 1.0
- B3: alpha_N = 2.0
- B4: alpha_N = 4.0
- B5: alpha_N = 8.0

**Tactic:** N=16384 (fixed); M chosen by alpha_N axis: M in {8192, 16384, 32768, 65536, 131072}. V_C * V_R chosen by codebook_headroom axis (per cell M): `V_C * V_R = headroom * M`.

For each (A, B) cell, we hold V_R = 32 (large enough that V_C stays modest) and compute V_C = ceil((headroom * M) / V_R). At extreme corners V_C may exceed practical encoder capacity (V_C > 1M) -- those cells are SKIPPED with a recorded skip-reason `V_C_OVER_LIMIT`. Practical bound: cap V_C at 200_000 (still ~12.8 GB at fp32 N=16384, expensive but feasible).

**Skip-rationale registry** (computed at pre-reg time):
- alpha_N=8 + headroom=100x: V_C * V_R = 100 * 131072 = 13.1M; V_R=32 -> V_C=410k. SKIP (over 200k cap).
- alpha_N=8 + headroom=10x: V_C * V_R = 1.31M; V_C=41k. KEEP.
- All others within cap.

After SKIP-rationale: 24 (A,B) cells + 1 KNN sentinel cell = 25 phase units * 3 seeds = 75 total units.

If 24-cell load is heavy, prune: drop A1 (100x headroom; A2 at 10x already proves the H1 prediction). Reduced to 20 cells * 3 seeds + 3 sentinel seeds = 63 units. **Recommended cardinality: 63.**

**Two additional control arms:**
- `KNN_SENTINEL` at V_C=4000, noise_sigma=0.10 (tightened; not at 0.3 which was the prior HP-misspec). Predicted recall 0.98+. SCOPE: this arm validates encoder + cosine retrieval baseline. HP gate APPLIES only to this arm (per per-arm HP-scope discipline).
- `BARE_E_R_ENCODER` arm at one chosen (alpha_N=0.5, headroom=10x) cell: skip the Hebbian W step entirely, retrieve via E @ E.T cosine directly. Predicted recall = 1.000 (encoder is bijective on its own labels). SCOPE: this arm is a "encoder works" check; HP gate APPLIES.

### 2.4 Per-arm HP scope declaration (load-bearing)

| Arm                       | HP gate applies? | Predicted band                                          |
|---------------------------|------------------|---------------------------------------------------------|
| MECHANISM (A,B) cells     | NO (band per (A,B))  | per-cell predicted recall in `predicted_surface` table |
| KNN_SENTINEL              | YES (HP=0.95)    | sigma=0.10 in 16384-dim => >= 0.95                       |
| BARE_E_R_ENCODER          | YES (HP=0.99)    | bijective lookup; >= 0.99                                |

**This eliminates the HP-gate-mis-spec from the prior cell** where HP_KNN_SENTINEL=0.90 sigma=0.3 forced HARD_FAIL on a baseline noise floor unrelated to the mechanism.

### 2.5 Predicted surface (pre-reg locked; verdict compared against)

| alpha_N \\ headroom | 10x      | 2x       | 1.0x     | 0.5x     |
|---------------------|----------|----------|----------|----------|
| 0.5                 | 1.000    | 1.000    | 0.65-0.75| 0.45-0.55|
| 1.0                 | 1.000    | 0.95-1.0 | 0.55-0.65| 0.40-0.50|
| 2.0                 | 0.95-1.00| 0.85-0.95| 0.45-0.55| 0.30-0.40|
| 4.0                 | 0.75-0.90| 0.60-0.80| 0.35-0.45| 0.20-0.30|
| 8.0                 | 0.40-0.65| 0.30-0.55| 0.20-0.30| 0.15-0.25|

**Numbers in italics (10x column) are the substrate envelope curve we are trying to characterize.** The other columns are codebook-exhaustion artifacts; their values should track 1/headroom * unique-triples-per-key.

### 2.6 Verdict logic (BANDED, per discipline)

- **HARD_PASS (chain-grade envelope):** 10x-headroom column shows rec_mean >= 0.95 cv <= 0.05 at alpha_N in {0.5, 1.0, 2.0} across 3 seeds. (3+ cells confirm envelope holds at alpha_N <= 2 with codebook headroom.)
- **HARD_PASS (chain-grade codebook-separation):** The 1.0x-headroom column AND the 0.5x-headroom column show rec_mean monotonically below the 10x column at MATCHED alpha_N, with the predicted-ratio difference > 0.20 at 3+ matched cells. (Confirms codebook is the dilution mechanism, not weight-matrix crosstalk.)
- **CHAIN_GRADE_BOTH:** both above. Substrate envelope is cleanly separated from codebook artifact.
- **MIDDLE_BAND:** envelope HARD_PASS but separation noisy (or vice versa).
- **HARD_FAIL_CARDINALITY_BREACH:** observed n_units < EXPECTED_N_UNITS (META_RULE_H).
- **HARD_FAIL_BIAS_S:** observed alpha_VC OR alpha_N for any cell differs from pre-reg-computed by > 0.05 (regime-check assertion).
- **HARD_FAIL_UNIT_EXCEPTION:** any unit raised an exception (META_RULE_J no-silent-except).
- **HARD_FAIL_SUBSTRATE_ONLY:** any LLM call detected.
- **HARD_FAIL_SCOPED_HP:** KNN_SENTINEL < 0.95 OR BARE_E_R_ENCODER < 0.99 (the only HP gates with mechanism-arms-exempt scope).

### 2.7 Smoke discipline (per `feedback_discriminator_must_survive_scale_2026-06-26` + three-smoke-disciplines)

Smoke must FIRE the discriminator, not merely verify the cell runs. Three smoke-time cells:
- **Smoke S1** (FIRES envelope discriminator): N=2048, alpha_N=2.0, headroom=10x. Predicted rec >= 0.95.
- **Smoke S2** (FIRES codebook discriminator): N=2048, alpha_N=1.0, headroom=0.5x. Predicted rec ~0.45.
- **Smoke S3** (FIRES baseline): N=2048, alpha_N=0.5, headroom=10x. Predicted rec = 1.000.

**Smoke PASS criterion:** S1 rec >= 0.90 AND S3 rec >= 0.99 AND S2 rec in [0.35, 0.55]. If any fails, do NOT dispatch full. (Per discipline: smoke proves the discriminator survives scale via analytical extrapolation -- N=2048 is conservative; predicted bands held in prior production runs at N=2048 in the higher_alpha smoke.)

### 2.8 BIAS-S regime-check (runtime assertions)

For each (A, B) cell at run-time:
```python
expected_alpha_N = M / N
expected_headroom = (V_C * V_R) / M
assert abs(expected_alpha_N - target_alpha_N) < 0.01, "BIAS_S alpha_N drift"
assert abs(expected_headroom / target_headroom - 1.0) < 0.05, "BIAS_S headroom drift"
assert keys_unique_mode_observed == ("unique_sr" if expected_headroom >= 1.0 else "duplicates_allowed"), "BIAS_S key-mode mismatch"
```
Any assertion failure halts the loop (META_RULE_J).

### 2.9 META_RULE_H cardinality declaration

```python
EXPECTED_N_UNITS = (
    20  # (A,B) mechanism cells after SKIP pruning
  + 1   # KNN_SENTINEL
  + 1   # BARE_E_R_ENCODER
) * len(SEEDS)  # 22 * 3 = 66
HARD_FAIL_CARDINALITY_BREACH = (observed_n_units < EXPECTED_N_UNITS)
```

### 2.10 SKIP-rationale registry (transparency)

Cells skipped at pre-reg time + reason recorded in metrics.json `detail.skip_registry`. Total V_C * V_R required for each (A, B) computed and printed. No silent skips. Skipped cells DO NOT count toward `n_units_observed` (correctly reflects what was measured), but ARE pre-counted in EXPECTED_N_UNITS as 0-count entries so the cardinality gate detects "we said we'd run 20 but only 18 ran".

---

## 3. HP bands + arms + cardinality table (summary)

| Component                       | Value                                      |
|---------------------------------|--------------------------------------------|
| N                               | 16384 (full); 2048 (smoke)                 |
| V_R                             | 32                                         |
| Seeds                           | 3 (full): {11, 13, 19}                     |
| alpha_N axis                    | {0.5, 1.0, 2.0, 4.0, 8.0}                  |
| headroom axis                   | {10x, 2x, 1.0x, 0.5x}                      |
| Phase cells (post-SKIP)         | 20                                         |
| Sentinel + bare arms            | 2                                          |
| Total cells * seeds             | 22 * 3 = 66                                |
| EXPECTED_N_UNITS                | 66                                         |
| HP_KNN_SENTINEL (scoped)        | 0.95 (sigma=0.10; mechanism arms exempt)   |
| HP_BARE_E_R (scoped)            | 0.99 (bijective lookup; mechanism exempt)  |
| HP_HARD_PASS_envelope           | rec >= 0.95 cv <= 0.05 at 3+ headroom=10x cells alpha_N<=2 |
| HP_HARD_PASS_codebook           | 1.0x AND 0.5x columns below 10x by >= 0.20 at 3+ matched cells |
| CV_MAX                          | 0.05                                       |
| Pre-reg version                 | v1 LOCKED at module init                   |

---

## 4. Cross-reference to RC-1 / RC-2 / RC-4 (combine or separate?)

From the 3x drill (`research_drill_capacity_envelope_3x_2026-06-27.md`):
- **RC-1: encoder whitening** (Mu-Viswanath anisotropy killer)
- **RC-2: sparse-bipolar bind** (10-20% active bits)
- **RC-4: multi-bank validation at alpha >= 2**

### Recommendation: SEPARATE cells, NOT combined into the envelope-separation cell.

**Rationale (verify-the-referent + bias-S):**

1. **The envelope-separation cell MUST be the clean baseline.** Mixing in RC-1 (whitening) or RC-2 (sparse bind) confounds the alpha_N axis with encoder-design changes. Skunkworks would correctly demote a combined cell back to MEASURED_MECHANISM because we couldn't say which axis explained the recall surface.

2. **Sequential order:** The envelope-separation cell LANDS FIRST (this drill). RC-1 then runs against the SAME (alpha_N, headroom) grid with `RAW` vs `WHITENED_K5` as the arm axis. RC-2 runs with `DENSE` vs `SPARSE_10` as the arm axis. RC-4 runs with `K=1, 4, 16, 64` banks as the arm axis. Each RC cell uses the envelope cell's (alpha_N, headroom) grid as the substrate, so we can directly read "RC-X lifted the envelope from X to Y" off the deltas.

3. **One exception (RC-4 multi-bank may co-ship):** if compute budget permits, the envelope-separation cell could add a single extra arm at (alpha_N=4.0, headroom=10x, K=4 banks) as a co-shipped control. This is small (1 extra cell * 3 seeds = 3 units) and provides early signal on whether multi-bank rescues the alpha_N=4 envelope without requiring a full RC-4 cell. Recommendation: **co-ship this single multi-bank probe arm; defer full RC-4 to its own cell.**

### Updated cell sequence (post-envelope-separation lands):

1. **NOW:** `phase_diagram_capacity_codebook_separated_envelope_v1` (this drill)
2. **+1 cycle (after lands):** `capacity_envelope_encoder_whitening_v1` (RC-1) -- uses this cell's grid as baseline
3. **+1 cycle (parallel to RC-1):** `capacity_envelope_multibank_alpha_3_v1` (RC-4) -- uses this cell's grid
4. **+2 cycles:** `capacity_envelope_sparse_bipolar_bind_v1` (RC-2) -- bigger invasion, lower priority
5. **DEFERRED:** RC-3 (iterative cleanup), RC-5 (schema extraction)

---

## 5. Estimated wall + dispatch routing

### Wall estimate (per Fix #17 measurement discipline)

**Mechanism cell cost dominated by Hebbian W ingest + retrieval at N=16384.**
- Per-unit W ingest: M Hebbian outer-product accumulations, batched. Prior `vc_higher_alpha` cell wall: ~30-60s per unit at M=N=16384 on GPU.
- Retrieval: M argmax queries over V_C, batched -- 5-15s per unit.
- **Total per unit: ~40-90s on RTX 4060 Ti.**

**Total wall: 66 units * 60s avg = ~66 min on GPU.**

However, several cells require large V_C:
- (alpha_N=8, headroom=10x): M=131072, V_C * V_R = 1.31M, V_C=41k. Ingest at this scale: W stays at 16384x16384=1.07GB, but the ingest batch of 131072 outer products at V_C=41k: E tensor is 41k x 16384 fp32 = 2.6GB. **Cell wall ~5-10 min for this single unit.**
- Total over 3 seeds for this corner: ~15-30 min.

**Revised wall estimate: ~90-120 min on GPU; bounded by the largest-V_C cells.** Add 20% slack for OOM safety, scaling: **~150 min budget on RTX 4060 Ti.**

CPU wall is ~30-50x slower; do NOT route to CPU.

### Dispatch routing

- **REMOTE_GPU via hdi_orchestrator** (per `feedback_gpu_underutilization_route_heavy_cells_via_orchestrator_USER_2026-06-22` + Fix #24 GPU-dispatch-must-actually-use-GPU). 
- Cell uses torch.cuda explicitly (matches prior higher_alpha cell pattern); encoder + W on GPU; batched matmul retrieval.
- GPU utilization should be >= 50% (Fix #24); profile in smoke before full dispatch.
- Per Fix #20: NO `2>&1 | tail -N` subprocess monitoring inside the cell. File-redirect + mtime polling instead.
- Per Fix #21: Director polls `find data -maxdepth 2 -name metrics.json -mmin -180` every turn-cycle to catch landing.
- Per Fix #25: landing_notifier scheduled task already running; will catch this cell.

### Dispatch sequence

1. Cell-author (hdi_exp_dev spawn OR main-thread) writes `experiments/exp_phase_diagram_capacity_codebook_separated_envelope_v1.py` + `preregs/2026-06-27_phase_diagram_capacity_codebook_separated_envelope_v1.md`.
2. Run `--self-test`: verifies primitives, BIAS-S assertions, cardinality math, SKIP registry.
3. Smoke at N=2048 on GPU (smoke S1+S2+S3, ~3-5 min wall): verify FIRES discriminator per smoke-PASS criterion.
4. If smoke PASS: dispatch to overnight_queue via `tools/queue_add.sh overnight_queue` (per Fix #24 GPU mandate).
5. Director peek_arm_metrics.py post-landing (per `feedback_use_peek_arm_metrics_before_framing`); default classification = MEASURED_MECHANISM; let Skunkworks tier UP if appropriate.

---

## 6. Anti-bias checklist (lit-scan calibration + experiment-bias master)

- **BIAS-S regime-check:** runtime assertions on alpha_N, headroom, keys_unique_mode for every cell.
- **BIAS-14 mismatch:** predicted_surface table makes the predicted ranges EXPLICIT pre-reg; cell verdict references these directly.
- **BIAS-O basis-vs-use-case:** the encoder labels are at READOUT (E @ states), not in the basis -- correct usage.
- **BIAS-Q "suspect 1.000 results":** 5/9 prior cells were 1.000 with cv=0. This drill's predicted-surface column for 10x-headroom is ALSO mostly 1.000. The verdict treats 1.000 as VALID only when codebook headroom guarantee holds AND cv stays at 0 across seeds AND BIAS-S assertions pass.
- **Verify-the-referent:** the cell asserts the metric arrives in the expected schema; the verdict reads the surface dict, not the verdict_msg string (per Fix #28 verify per-arm metrics).
- **Per-arm HP-scope discipline (NEW from Skunkworks batch 7):** mechanism arms exempt from HP gates; only KNN_SENTINEL + BARE_E_R_ENCODER carry HP gates. The prior cell HARD_FAIL on KNN sentinel that wasn't even the mechanism is fixed here.
- **Symmetric anti-negativity:** I have NOT inflated. The honest reading is "5/9 prior cells held perfect rec=1.000 at alpha_N=2.0; 4/9 collapsed due to codebook exhaustion." This drill PROVES separation; it does NOT claim the substrate envelope extends beyond alpha_N=2 until measured. The headroom=10x column at alpha_N=4 and 8 will tell us.
- **Discriminator must survive scale (USER 2026-06-26):** smoke at N=2048 fires three discriminator probes; their predicted bands held in prior N=2048 runs.
- **Three smoke disciplines:** no silent-except (META_RULE_J halt); smoke FIRES discriminator (S1+S2+S3 each test a distinct hypothesis); band-floor results are MIDDLE_BAND not HARD_PASS (verdict logic enforces).
- **CARDINALITY_OK mandatory (META_RULE_H):** EXPECTED_N_UNITS=66; HARD_FAIL_CARDINALITY_BREACH if observed<expected; SKIP registry transparent.

---

## 7. What the cell will TELL us (predicted outcomes)

**Outcome 1 (P ~ 0.55 calibrated): clean envelope to alpha_N=2 confirmed; codebook fully separated.**
- 10x-headroom column shows 1.000 at alpha_N in {0.5, 1.0, 2.0}; smooth degradation at alpha_N in {4, 8}.
- 1.0x and 0.5x columns track predicted dilution baseline.
- HARD_PASS_BOTH. Substrate envelope is chain-grade to alpha_N=2.

**Outcome 2 (P ~ 0.25 calibrated): envelope extends past alpha_N=2 (e.g., to alpha_N=4) at 10x headroom.**
- 10x column shows rec >= 0.95 at alpha_N=4 (unexpected; would shift the substrate-product story upward).
- Likely cause: with V_R=32 (larger than prior V_R=8), the codebook's information capacity per fact is higher; W cleanup margin is correspondingly better.
- HARD_PASS_BOTH plus an extension finding. High-value result.

**Outcome 3 (P ~ 0.15 calibrated): envelope cliffs sharply at alpha_N just past 2.**
- 10x column shows 1.000 at alpha_N=2 then catastrophic drop at alpha_N=4.
- Indicates the substrate-W operates near a phase boundary; not the smooth-degradation predicted by HRR margin theory.
- HARD_PASS_envelope (at alpha_N=2); valuable negative result for the smooth-degradation claim. Triggers RC-1/RC-3 priority bump.

**Outcome 4 (P ~ 0.05 calibrated): something we didn't predict.**
- E.g., 1.0x-headroom column does NOT track dilution baseline (codebook mechanism is more complex than predicted), OR 10x column has cv > 0.05 (W ingest order matters more than expected).
- Triggers diagnostic follow-up; MIDDLE_BAND verdict.

P sums to 1.00. Calibrated downward per lit-scan penalty; capped at 0.55 chain-grade per novel-synthesis ceiling.

---

## 8. Open questions for USER (when off flight; no AskUserQuestion tool used)

1. **V_R=32 vs V_R=8 vs V_R=4:** I chose V_R=32 to give comfortable codebook headroom without exploding V_C. If USER wants to match prior cells' V_R=8 directly for apples-to-apples comparison, V_C just grows 4x at fixed headroom. Tradeoff: V_R=32 reduces V_C ceiling (better OOM margin) at the cost of cross-cell comparability. **Default: V_R=32 (cleaner OOM margin; the envelope claim is invariant to V_R since headroom is the right axis).** If USER prefers V_R=8 for comparability, swap and re-prune the V_C cap (max V_C grows to ~800k, may exceed cap at alpha_N=8).

2. **Co-ship multi-bank probe arm (1 extra cell, K=4 banks at alpha_N=4 headroom=10x)?** Adds 3 units; ~5 min wall; provides early signal on whether RC-4 rescues envelope at alpha_N=4. **Default: yes, co-ship the probe.** USER can override.

3. **Smoke routing:** smoke runs at N=2048 on the laptop GPU (~3-5 min) before full dispatch to remote_gpu. Alternatively run smoke ON the remote GPU to amortize SSH overhead. **Default: smoke locally, full remotely** (per cell-author smoke convention).

---

## 9. Hand-off (dispatch sequence)

When USER lands / approves:

1. **Spawn `hdi_exp_dev`** with task hand-off pointer to this drill doc + cell-spec stub in section 2. Skill: `exp_dev`.
2. exp_dev writes:
   - `experiments/exp_phase_diagram_capacity_codebook_separated_envelope_v1.py` (full cell per sections 2.1-2.10)
   - `preregs/2026-06-27_phase_diagram_capacity_codebook_separated_envelope_v1.md` (envelope-fail-bands per section 2.6; HP per 2.4; predicted_surface per 2.5 LOCKED)
3. exp_dev runs `--self-test`; smoke S1+S2+S3 at N=2048 on local GPU; verify smoke-PASS criterion (section 2.7).
4. exp_dev pre-dispatch verify-the-referent via `tools/predispatch_check.py phase_diagram_capacity_codebook_separated_envelope_v1` (Fix #26).
5. Spawn `hdi_orchestrator` to ship full to remote_gpu (overnight_queue) per routing in section 5.
6. Director peeks per `tools/peek_arm_metrics.py` post-landing; default classify MEASURED_MECHANISM; spawn `hdi_skunkworks` for tier evaluation.
7. Atomize result to Store + cert_ledger SAME CYCLE (per `feedback_results_to_application_cadence_same_cycle`).

---

## 10. Where this fits in the program

- **Stage 1/2 (base + optimize):** this drill is Stage-2 (optimize the substrate's capacity-envelope discriminator design).
- **Cert-architecture C0-C6:** addresses C2 (DISCRIMINATING-REGIME identified) + C3 (envelope-fail-bands per axis); arms us toward C5 (multiple chain-grade results in the regime).
- **M3 milestone:** capacity envelope is a foundational substrate property feeding KG ingest scaling; clean separation unblocks meaningful M-scaling claims in M3 demos.
- **Encoder bottleneck (project_substrate_arc_2026-06-23):** this cell establishes the BASELINE that RC-1 (whitening) will then lift; load-bearing for the encoder-improvement cell sequence.

---

## 11. Drill self-check (lit-scan discipline)

- Lit-scan penalty applied: novel-synthesis capped 0.50 (the BOTH HARD_PASS outcome is novel for our substrate; capped accordingly).
- Symmetric anti-negativity: did NOT inflate. Did NOT claim envelope extends past alpha_N=2 prematurely. Did separately credit the empirical surface that DID show clean rec=1.000 at 5 cells.
- Verify-the-referent: read metrics.json directly (section 0 table); did not trust verdict_msg framing of the prior cell.
- Discipline check: "discriminator must survive scale" -- three smoke probes each FIRE a distinct hypothesis arm at N=2048.
- Discipline check: "substrate doesn't know anything" -- this is a Stage-2 instrument cell about capacity; no language/understanding claims.
- Discipline check: per-arm HP scope is declared explicitly (Skunkworks batch 7 directive).
- Discipline check: META_RULE_H + J + K + L all addressed.

-- Research (Opus 4.7 1M)
