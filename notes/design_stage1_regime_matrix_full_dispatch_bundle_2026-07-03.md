# Stage 1 Regime Matrix FULL Dispatch Bundle — 2026-07-03

## Purpose

Pre-authored FULL dispatch spec for the Stage 1 CG_META regime matrix. Fires
after USER restores Tailscale on `marsh@home` (currently DOWN, blocking remote
GPU dispatch). Wrappers s7+s13+s19 already exist for every probe below; SELFTEST_OK
verified 2026-07-03 (14/14 s13+s19 pass first pass; +4/4 s13+s19 for P13/P14
added 2026-07-03 post-SMOKE-HP; s7 was pre-existing).

**Composition rule:** 3 seeds per probe (arc-continuation-vs-arc-closure
discipline; `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-06-27` +
follow-on `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03`).
Multi-seed reproduces or reveals seed-sensitivity; SMOKE-only-verdicts do NOT
constitute arc closure.

**Source signature discipline:** each probe cited by the metric-source-signature
it extends (`feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03`).
No probe re-frames from scratch — all framing is Skunkworks-authoritative as
CITED@ `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-03_LATE.md`
Amendments 21:15Z / 21:30Z / 21:45Z / 21:55Z / 22:05Z.

## Per-probe FULL dispatch spec

| Probe | Anchor slug (per-seed cell) | FULL cardinality | seeds | TR | timeout/seed (s) | Wall estimate/seed | Queue |
|---|---|---|---|---|---|---|---|
| P4 | `exp_stage1_regime_probe_4_storage_x_N_v1_s{7,13,19}` | 48 pts | 3 | 100 | 5400 | ~30-45 min GPU | overnight_queue |
| P5 | `exp_stage1_regime_probe_5_storage_x_topology_v1_s{7,13,19}` | 48 pts | 3 | 100 | 5400 | ~30-45 min GPU | overnight_queue |
| P6v2 | `exp_stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1_s{7,13,19}` | 217 pts | 3 | 100 | 10800 | ~90-150 min GPU | overnight_queue |
| P7v2 | `exp_stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_s{7,13,19}` | 109 pts | 3 | 100 | 7200 | ~50-90 min GPU | overnight_queue |
| P8 | `exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s{7,13,19}` | 25 pts | 3 | 100 | 3600 | ~20-30 min GPU | overnight_queue |
| P9v2 | `exp_stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1_s{7,13,19}` | 17 pts | 3 | 100 | 2700 | ~15-25 min GPU | overnight_queue |
| P12 | `exp_stage1_regime_probe_12_L_marginal_effect_sweep_v1_s{7,13,19}` | 25 pts | 3 | 100 | 3600 | ~20-30 min GPU | overnight_queue |
| P13 | `exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s{7,13,19}` | 19 pts | 3 | 100 | 3600 | ~20-30 min GPU | overnight_queue |
| P14 | `exp_stage1_regime_probe_14_L_x_F_non_saturated_v1_s{7,13,19}` | 20 pts | 3 | 100 | 3600 | ~20-30 min GPU | overnight_queue |
| P10 v2 | (SKIP; see §Skip decision) | -- | -- | -- | -- | -- | -- |

**Total: 27 cell dispatches (9 probes x 3 seeds); ~17-27h serial GPU wall on
`marsh@home` overnight_queue.** Timeouts padded ~1.5x expected wall as
runner-death safety per §13 CHUNKED discipline.

Cardinalities MEASURED@ `experiments/exp_stage1_regime_probe_<N>_*_s7.py:CONFIG_VERSION`
field `expected_n_full=...` for each cell.

## Skunkworks-authoritative per-probe framing

**Adopted from BACKUP file 2026-07-03_LATE.md amendments; do NOT re-frame.**

### P4 STORAGE x N (SCALE_FREE)
- Question: does SHARDED-vs-BUNDLED gap scale with N at fixed CLEANUP=iterative_cosine?
- Source signature: extends `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1`
  + Probe 1 CG_META regime-cross-term.
- Note: STORAGE column already partly covered by Skunkworks atom
  `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1`; this probe adds the
  N-cross-term. Framing correction from BACKUP Amendment 21:15Z Fix#28 hit #13:
  do NOT frame "huge STORAGE main effect" as novelty — the STORAGE gap partly
  restates prior atom. Novel content = the *N cross-term interaction* only.

### P5 STORAGE x F (TOPOLOGY, aliased)
- Question: does SHARDED-vs-BUNDLED gap scale with F fan-out?
- Source signature: same primitive family as P4; F-axis instead of N-axis.
- Note per BACKUP Amendment 21:30Z axis-aliasing: **TOPOLOGY = ALGEBRA = F fan-out**
  in current substrate primitives. P5 and P10 originally intended to test
  distinct axes; they test the SAME cross-term (STORAGE x F). Since P10 v2
  SKIP HONEST_NO_MATCHED_CLIFF (see §Skip below), P5 is the sole STORAGE x F
  cross-term measurement. Frame HP result as "STORAGE x F cross-term
  characterization at F in {1,2,4,8}", NOT "TOPOLOGY axis distinct from ALGEBRA".

### P6v2 F(TOPOLOGY) x CLEANUP
- Question: F x CLEANUP_MECHANISM cross-term at non-saturated cliff-adjacent regime.
- Source signature: extends Probe 1 CG_META with F axis; corr grid {0.70, 0.85, 0.90}
  brackets the saturation edge deliberately.
- Note: FIRST-PRIORITY LOAD-BEARING: paired with P8 for ranking-crossover
  claim. BACKUP Amendment 21:30Z ALIASING NOTE: P6v2 tests F x CLEANUP; P3 and
  P8 test the SAME cross-term at different F-grid resolutions. Convergent
  evidence at cliff-adjacent = "F x CLEANUP replicates (P6v2 + P8) both show
  mech_var >= 0.10" — that's 2-way replication of a cross-term, not 3-axis
  independent evidence.

### P7v2 N x CLEANUP
- Question: N x CLEANUP_MECHANISM at fixed corr grid {0.88, 0.90, 0.92}, L=8.
- Source signature: extends Probe 2 (N x CLEANUP) at non-saturated corr grid
  after P2 SMOKE was saturation-vacuous.
- Note: BACKUP Step 9 / Amendment 21:15Z lineage. Includes SATURATION_PC
  positive-control arm (`iterative_cosine, M=800, N=2048, corr=0.20`) — that
  arm must reproduce prior sigma0 >= 0.95 cleanup or downstream N x CLEANUP
  arms are suspect (Gate D positive-control discipline).

### P8 ALGEBRA(F, aliased) x CLEANUP
- Question: ranking-crossover between iterative_cosine and modern_hopfield across
  F at CLIFF (N=512, M=6400, corr=0.85, L=2, SHARDED) and DEEP_SAT (N=8192,
  M=800, corr=0.60, L=2, SHARDED).
- Source signature: F x CLEANUP cross-term (aliased with P3/P6 axis-wise;
  distinct regime signatures = CLIFF + DEEP_SAT explicit).
- Note: FIRST-PRIORITY LOAD-BEARING. Ranking crossover is the atom-candidate
  claim. Skunkworks noted at Amendment 21:30Z: "P6+P8 share
  CLIFF-N512-M6400-corr0.85 regime — the reason they share is BECAUSE they test
  same axis pair (F x CLEANUP)." Post-FULL VET must verify the crossover
  reproduces at 3-seed variance — if crossover collapses within noise, the
  ranking-crossover claim demotes.

### P9v2 N x L (in-band L / N_cliff sweep, BUNDLED)
- Question: does BUNDLED+modern_hopfield show non-monotonic L peak at
  cliff-adjacent N ratios?
- Source signature: extends P9 v1 (endpoints-only smoke was HP-saturated); v2
  sweeps L in {2, 4, 8, 16} at N in {1024, 2048, 4096} = 0.5x/1x/2x N_cliff.
- **Fix#28 hit #15 applies (BACKUP Amendment 21:55Z):** SMOKE only tested
  L in {2, 16} at 1 seed; the "non-monotonic peak at L=8" pattern comes from
  `bracket_verify` SCRATCHPAD prior (L in {2,4,8,16} at 3-seed TR=100), NOT
  from SMOKE. Cite bracket_verify EXPLICITLY as the pattern source in FULL
  dispatch spec; do NOT carry "SMOKE observed non-monotonic" narrative into
  FULL. FULL 3-seed TR=100 is the *decisive* test; H2 vs H1 vs MIDDLE_BAND
  fork resolves there.
- Corrected framing (Skunkworks-authoritative, verbatim from Amendment 21:55Z):
  > "SMOKE HP with clean gates + SATURATION_PC sanity + SHARDED positive
  > control. Bracket_verify scratchpad shows suggestive non-monotonic pattern
  > at L=8 (0.65 vs 0.37, 0.47, 0.59) with max|additive residual|_in_band=0.162
  > exceeding H1 top-bucket threshold 0.15. FULL is the decisive test."

### P12 L-marginal effect sweep at SHARDED cliff-adjacent
- Question: does chain-depth L moderate SHARDED capacity at cliff-adjacent
  regime beyond what atom #3 already characterizes?
- Source signature: **REGIME_EXTENSION of atom #3
  `SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1`** (M1.9/M1.10 K=5
  roundtrip). NOT a 5th axis discovery.
- **Fix#28 hit #16 applies (BACKUP Amendment 22:05Z):** Cell-author's original
  framing "L is 5th CG_META axis" DOWNGRADED. L is already CG_META-covered at
  atom #3; P12 extends the regime (sharded FHRR, cliff-adjacent, F=1, TR=40).
- Additional catch: L=1 -> L=16 total spread of 0.875 is *theory-trivial* (SNR
  decays geometrically per AGS + Plate). The **band-only spread 0.45**
  (L=1 -> L=4) is the substantive signal to look for in FULL.
- Post-FULL atom candidate (only fileable if 3-seed FULL confirms):
  `EMPIRICAL_L_MODERATES_CAPACITY_AT_SHARDED_CLIFF_ADJACENT_v1` -> MM_STANDARD,
  COMPOSES atom #3, classification = REGIME_EXTENSION.

### P13 L x CLEANUP cross-term at cliff-adjacent SHARDED
- Question: does today's F x CLEANUP mech-moderation pattern (P6v2 + P8) hold
  across L in {1, 2, 4}, or is it L=2-specific?
- Source signature: **REGIME_EXTENSION of atom #3** into the L x CLEANUP
  interaction; extends F x CLEANUP finding (P6v2 + P8) with the L axis at
  cliff-adjacent SHARDED F=1.
- SMOKE HP verdict landed 2026-07-03; Skunkworks VET a6730405b2b50c6c0
  `HOLD_PENDING_FULL`. MM_TENTATIVE at SMOKE.
- Skunkworks-authoritative framing (VERBATIM from VET a6730405b2b50c6c0):
  > "L x CLEANUP cross-term at cliff-adjacent SHARDED. mech_spread trajectory
  > noise-artifact at SMOKE; 3-seed FULL TR=100 to distinguish 'mech
  > convergence with L' physics from single-seed noise."
- Post-FULL atom candidate (only fileable if 3-seed FULL confirms cv<0.15):
  `EMPIRICAL_L_x_CLEANUP_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1` -> MM_STANDARD,
  REGIME_EXTENSION of atom #3.

### P14 L x F cross-term at cliff-adjacent SHARDED
- Question: are L (chain-depth) and F (fan-out) truly independent axes, or do
  they interact at cliff-adjacent SHARDED FHRR?
- Source signature: theory-consistent Frady/Sommer near-capacity coupling
  (per Skunkworks VET abd4d2af06f49f6bb); NOT novel-mechanism. Skunkworks atom
  #48 addendum flagged "L cross-terms unmapped."
- SMOKE HP verdict landed 2026-07-03; Skunkworks VET abd4d2af06f49f6bb
  `HOLD_PENDING_FULL`. Fix#28 hit #17: SMOKE reported interaction=0.20 but
  noise-corrected (L=1 ceiling-confounded row excluded) drops to 0.05 which is
  BELOW H1 threshold. MM_TENTATIVE at SMOKE.
- Skunkworks-authoritative framing (VERBATIM from VET abd4d2af06f49f6bb):
  > "L x F cross-term theory-consistent Frady/Sommer; L=1 ceiling-confounded at
  > SMOKE inflating interaction_metric to 0.20 (noise-corrected 0.05); FULL
  > 3-seed TR=100 essential; consider raising L=1 corruption OR re-report on
  > {L=2,L=4} only."
- Post-FULL atom candidate (only fileable if 3-seed FULL confirms surviving
  interaction and cv<0.15): `EMPIRICAL_L_x_F_CROSS_TERM_CLIFF_ADJACENT_SHARDED_v1`
  -> MM_STANDARD + Skunkworks atom #48 amendment. If noise-corrected metric
  fails to survive at FULL: NULL, no atom, Fix#28 hit #17 stands.

## FULL dispatch ORDER

Total 7 probes; not blocked-serial (each is independent phase-point work). But
ORDER-of-queue-add matters for prioritization when GPU wall is finite and
Skunkworks landed-VET fires per-completion.

**Priority 1 — F x CLEANUP replicates confirmation (LOAD-BEARING ranking crossover):**
1. **P6v2 F(TOPOLOGY) x CLEANUP** (3 seeds; expected ~90-150 min/seed) — biggest cell but
   discriminator core.
2. **P8 ALGEBRA(F) x CLEANUP** (3 seeds; expected ~20-30 min/seed) — CLIFF + DEEP_SAT
   crossover claim; smaller/faster; paired with P6v2 for 2-way replication.

**Priority 2 — STORAGE x MECH replication (P1 CG_META regime-cross-term extension):**
3. **P4 STORAGE x N** (3 seeds; ~30-45 min/seed)
4. **P5 STORAGE x F** (3 seeds; ~30-45 min/seed) — sole remaining STORAGE x F
   measurement after P10 v2 SKIP.

**Priority 3 — N x CLEANUP moderation:**
5. **P7v2 N x CLEANUP** (3 seeds; ~50-90 min/seed) — extends P2 with in-band corr grid.

**Priority 4 — N x L novel signal test (cite bracket_verify per Fix#28 hit #15):**
6. **P9v2 N x L** (3 seeds; ~15-25 min/seed) — decisive H2/H1/MIDDLE_BAND fork; smallest
   grid so cheap.

**Priority 5 — L marginal regime-extension of atom #3 (per Fix#28 hit #16):**
7. **P12 L-marginal SHARDED cliff-adjacent** (3 seeds; ~20-30 min/seed) — REGIME_EXTENSION
   framing, not axis discovery.

**Priority 6 — SKIP P10 v2 FULL entirely** (see next section).

## Skip decision — P10 v2

**SKIPPED per HONEST_NO_MATCHED_CLIFF discipline (BACKUP Amendments 21:15Z + 21:45Z).**

P10 v2 re-bracket search (Skunkworks task a7808cd4d2fe53f16) proved no
in-band BUNDLED arm exists across the reasonable design space (100+ phase
points x multi-seed x multi-TR probed at corr in {0.05, 0.10}). Filed
Skunkworks atom `EMPIRICAL_BUNDLED_FHRR_CHAIN_COMPOSITION_L2_F1_FIRST_ORDER_TRANSITION_NO_MIDBAND_v1`
+ meta atom `META_when_cross_term_bracket_search_exhausts_design_space_file_HONEST_NO_MATCHED_CLIFF_and_SKIP_FULL_v1`.

Dispatching P10 v2 FULL now would be a confounded cross-term measurement
(BUNDLED arm at floor everywhere) that cannot discriminate cross-term
hypotheses. Aliasing note: STORAGE x F is instead covered by P5 above.

## Post-FULL Skunkworks landed-VET expectations per probe

**Common gates for all probes** (per SCHEMA-VET + META_RULE_L strict-above-floor):
- `cardinality_ok` observed == expected (48 / 48 / 217 / 109 / 25 / 17 / 25 respectively)
- `arms_differ_verified` hash-check
- `run_mode == "full"` (per §16 RUN_MODE VERIFICATION)
- `elapsed_s >> 1.0` (typical FULL is 20-100min; 668B selftest-sized landings = DISPATCH_BUG)
- Per-seed metrics variance: cv < 0.15 for HP claims; cv >= 0.15 -> MIDDLE_BAND
  or MM_TENTATIVE

**Per-probe atom-candidate framing (only fileable if 3-seed FULL confirms):**
- **P4**: extends `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1` with
  N cross-term characterization. NOT a fresh atom unless the N-cross-term
  interaction is genuine and independent of the STORAGE main effect.
- **P5**: STORAGE x F cross-term characterization. If HP + cv<0.15 + P4 also HP:
  strengthens the STORAGE column into a paired cross-term (not just main-effect).
- **P6v2**: F x CLEANUP characterization at cliff-adjacent — pair with P8.
- **P7v2**: N x CLEANUP at in-band corr — extends Probe 1 CG_META regime-cross-term
  arc. Novelty = regime extension, not fresh mechanism.
- **P8**: candidate atom = `CLEANUP_MECH_RANKING_CROSSOVER_AT_CLIFF_vs_DEEP_SAT_F_v1`
  IF (a) crossover reproduces at 3-seed variance AND (b) P6v2 F x CLEANUP
  agrees on the cliff-side ranking. If either fails: MIDDLE_BAND, no fresh atom.
- **P9v2**: candidate atom = one of `BUNDLED_MH_L_MONOTONIC_at_Ncliff_v1`
  (H1) or `BUNDLED_MH_NON_MONOTONIC_L_at_Ncliff_v1` (H2) or MIDDLE_BAND.
  Cite `bracket_verify` scratchpad prior explicitly in framing.
- **P12**: candidate atom = `EMPIRICAL_L_MODERATES_CAPACITY_AT_SHARDED_CLIFF_ADJACENT_v1`
  as REGIME_EXTENSION of atom #3, MM_STANDARD (NOT CG_META; NOT axis
  discovery — per BACKUP Amendment 22:05Z Fix#28 hit #16 correction).

## Total GPU wall estimate + serialization strategy

**Serial wall estimate (single overnight_queue GPU on marsh@home):**
- Priority 1 (P6v2 + P8): 3 x (90-150) + 3 x (20-30) = 330-540 min = 5.5-9.0h
- Priority 2 (P4 + P5): 3 x (30-45) + 3 x (30-45) = 180-270 min = 3.0-4.5h
- Priority 3 (P7v2): 3 x (50-90) = 150-270 min = 2.5-4.5h
- Priority 4 (P9v2): 3 x (15-25) = 45-75 min = 0.75-1.25h
- Priority 5 (P12): 3 x (20-30) = 60-90 min = 1.0-1.5h
- **Total serial estimate: ~13-21h**

Serialization strategy: queue all 21 cells in the ORDER above (Priority 1 first,
Priority 5 last). Runner processes strictly sequentially. Landed-VET fires
per-cell on completion; if Priority 1 (P6v2+P8) fails ranking-crossover, the
downstream Priorities may pivot — but that's a Director decision AFTER Priority
1 VETs complete, not pre-authorized here.

**Batching consideration:** if `hdi_orchestrator` can batch same-probe seeds
(s7/s13/s19) into a single GPU session (models re-used across seeds), wall
drops modestly. Current runner processes each cell as its own subprocess so no
in-process batching. Wall estimate above assumes cold-start per seed.

## Non-goals (do NOT do)

- **NO composite CG_META atom filing** until FULL cv < 0.15 AND multi-seed
  reproduces. Per BACKUP Amendment 21:45Z META_TENTATIVE meta-rule + Skunkworks
  discipline atom `META_cross_term_measurement_requires_both_arms_in_band_probe10_v1`.
- **NO axis-aliasing re-labeling** at atom-filing time. TOPOLOGY and ALGEBRA
  are aliased with F fan-out; if FULL fires HP on P5/P6v2/P8, atoms MUST use
  "F cross-term" language, not "TOPOLOGY" or "ALGEBRA" independently.
- **NO L-as-5th-axis atom filing** for P12. L is REGIME_EXTENSION of atom #3;
  post-FULL atom candidate is `EMPIRICAL_L_MODERATES_CAPACITY_AT_SHARDED_CLIFF_ADJACENT_v1`
  MM_STANDARD REGIME_EXTENSION, NOT `L_AXIS_CG_META_v1`.
- **NO P10 v2 FULL** as compute-recovery. Skip decision is scientifically
  correct; STORAGE column is covered by P4+P5.
- **NO "5-axis convergent evidence" framing** on landing summaries. True axis
  count is 4 (STORAGE, N, F, CLEANUP_MECH); L is coupling of atom #3, not 5th
  axis.

## Dispatch handoff to `hdi_orchestrator`

Once Tailscale is restored:
1. Push origin/main via `hd_metrics_sync` (this exp_dev cannot push; harness-DENIED).
2. `hdi_orchestrator` runs `tools/queue_add.sh` per cell in Priority 1..5 order.
3. Each cell dispatched with `HDLAB_EXP_NAME=<anchor_slug_full>` env (no `_smoke`
   suffix) so cell reads `RUN_MODE=full` (default per cell wrapper).
4. Per-cell `--timeout` values above.
5. Landed-VET dispatched to `hdi_skunkworks` per-completion (parallel is fine
   once >=2 cells have landed).

## References

- BACKUP: `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-03_LATE.md`
  Amendments 21:15Z / 21:30Z / 21:45Z / 21:55Z / 22:05Z
- Discipline rules (memory): `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03.md`,
  `feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03.md`,
  `feedback_cloud_gpu_once_per_stage_last_run_USER_LOCKED_2026-07-01.md`
- Wrapper files: `experiments/exp_stage1_regime_probe_{4,5,6,7,8,9v2,12}_*_s{7,13,19}.py`
  (21 files total; SELFTEST_OK verified 2026-07-03)
- Pre-reg files: per-probe under `preregs/2026-07-03_stage1_regime_probe_*.md`
  (owned by cell-author, referenced from cell docstrings)
