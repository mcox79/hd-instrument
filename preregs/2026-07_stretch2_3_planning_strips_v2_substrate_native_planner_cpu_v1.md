# Prereg: stretch2_3_planning_strips_v2_substrate_native_planner_cpu_v1

## Anchor
stretch2_3_planning_strips_v2_substrate_native_planner_cpu_v1

## Queue
- Smoke: local_cpu_queue
- Full: remote_cpu_queue (Director dispatches via orchestrator; author cannot push)

## v1 defect analysis (why v2)
Confirmed off-disk by cell-author 2026-07-02 against `experiments/exp_stretch2_3_planning_strips_cpu_v1.py`:
1. **NUMPY-COSTUME (Skunkworks META CG 2026-07-02).** v1 grep-count `cphasor|cidx|bind|bundle|cnorm|unbind` = 4 total in the whole file; ALL are in setup (`props`, `akeys`, `SLOTP/A/D`). The `store` dict is BUILT (lines 44-45) but NEVER READ. BFS at lines 54-65 uses raw Python `acts[a]` tuples for `pre.issubset(s)` and `(set(s) - dele) | add`. `cidx` is defined but never called. Substrate is decorative.
2. **ORACLE-GOAL (saturation trap).** v1 line 47 `cur = set(S0)` then lines 48-52 apply 2-4 random applicable actions from `S0`, then line 53 samples `G` as a subset of the reached `cur`. Every G is reachable-by-construction from S0. Plan-rate at 0.70+ is a floor artifact, not a discriminator.

Both defects mirror the stretch4_3 v1 defects that Skunkworks flagged during landed-VET. This v2 mirrors the stretch4_3 v2 rescue template.

## Design (v2 rescue path A)
- **Substrate-native retrieval at BFS action-lookup**: at BFS start, for each of NACT actions unbind action-key from substrate, unbind slot-role (SLOTP/A/D), cleanup vs `props` codebook with threshold `tau_frac * N`. Cache recovered `(pre_r, add_r, del_r)` per action (schemas don't change during search). BFS applicability + transition use RECOVERED sets, not stored Python `acts`.
- **Independent goal-sampling**: G is a random 1..3-subset of NPROP drawn INDEPENDENTLY of S0. May be unsolvable within depth_budget; solvability reported honestly and substrate-vs-symbolic gap measured on same trials.

## Arms
- **ARM_SUBSTRATE_NATIVE**: FHRR substrate mediates every planner action-lookup; pre/add/del sets RECONSTRUCTED via `cunbind + matmul + threshold` for all NACT actions before BFS begins.
- **ARM_SYMBOLIC_ORACLE**: pure Python set BFS (positive control; expected ceiling).

## Grid + parameters
- N = 8192 (both smoke and full)
- NPROP = 12
- NACT = 16
- depth_budget = 12
- tau_frac = 0.4 (THEORETICAL@analysis: 0.4*N=3277 threshold; SNR ~13 empirical at 3 slots)
- TR: smoke=15, full=150
- Single seed = 271 (embedded in run())

## Envelope-fail-bands
- **HARD_PASS**:
  - substrate_plan_rate within 0.10 of symbolic_plan_rate (`gap <= 0.10`) AND `sub >= 0.30` AND symbolic in [0.30, 0.85] (baseline_in_band). Substrate-native retrieval preserves classical STRIPS planning at real difficulty.
  - OR SUBSTRATE-NATIVE-EQUIVALENCE branch: arms_bit_identical AND all-slot retrieval p/r >= 0.95 AND symbolic in [0.30, 0.85]. (This is a positive result at N=8192 where FHRR SNR ~13 gives exact recovery.)
- **MIDDLE_BAND**:
  - Baseline saturated (`sym > 0.85`) OR baseline below floor (`sym < 0.30`)
  - Or `0.10 < gap <= 0.20`
  - Or SUBSTRATE-NATIVE-EQUIVALENCE but baseline out of band
- **HARD_FAIL**: `gap > 0.20`. Substrate cleanup LOSSY vs symbolic (CG-eligible substrate-limit negative).
- **BLOCK_DISPATCH_META_RULE_AF_SUSPECT**: arms_bit_identical WITH low retrieval fidelity (any slot p/r < 0.95). Substrate arm may be short-circuiting; investigate before dispatch.

## HP_SCOPE
- ARM_SUBSTRATE_NATIVE: gap_gate (within 0.10 of symbolic)
- ARM_SYMBOLIC_ORACLE: in_band_gate (in [0.30, 0.85])

## CELL-TEMPLATE MANDATES (META_RULE_AC/AF/AG/AH + META_RULE per Skunkworks CG 2026-07-02)
- `arms_differ_verified` at smoke gate (per-trial plan-tuple digest emitted in metrics)
- `final_metrics_atomicity = tmp_replace` (via `write_metrics` -> `os.replace`)
- `except SystemExit: raise` BEFORE `except Exception`; no `except BaseException`
- `crlb`: n/a (planner is discrete; no continuous CRLB; SNR analysis in module docstring + `_selftest` docstring)
- `baseline_in_band` at smoke: `0.30 <= sym_plan_rate <= 0.85` (recorded in metrics)
- `discriminator survives scale`: smoke uses full N=8192; only TR shrinks (15 vs 150). SNR is N-driven, not TR-driven, so retrieval fidelity does not degrade at smoke.
- `HP strictly above floor`: `gap <= 0.10 AND sym in [0.30, 0.85]`
- `cardinality_ok`: single (TR, N, NPROP, NACT) config per run_mode; not a sweep-axis cell
- `calibration_check = default_ok_for_this_regime`
- All numbers tagged with provenance in code (MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@)
- **Grep-check discipline** (Skunkworks META CG 2026-07-02): rescued cell invokes substrate primitives at planner call sites:
  - `substrate_bfs()` uses `substrate_retrieve_props()` which calls `cunbind + matmul` per (action, slot) at BFS start -> 3*NACT=48 unbind+cleanup ops per trial
  - Selftest calls `substrate_retrieve_props` 2*NACT=32 times and asserts exact-recovery >= 0.75

## Compute architecture
- **(b) sequential-CPU with justification**: BFS has genuine sequential dependencies (state N depends on state N-1 via action selection).
- Substrate retrieval cached once per trial (48 unbind+cleanup, sub-millisecond).
- BFS itself is Python-set operations (nanoseconds per expansion).
- No GPU speedup available: retrieval batch is trivial (48/trial), BFS is inherently sequential.
- Wall estimate: smoke ~5s, full ~90s (CPU inline).

## Per-experiment timeout
- Formula: `timeout_s = 4 * expected_wall + 60s buffer`
  - Smoke expected wall ~5s -> timeout 90s (use 180s for safety on shared runner)
  - Full expected wall ~90s -> timeout 600s (10 min)
- **Selftest timeout**: 60s (`_selftest` builds one 8192-dim substrate with NACT=16, does 32 retrievals; should complete in <1s locally)

## Framing warnings (per cell-author brief)
- If ARM_SUBSTRATE_NATIVE lands AT PARITY with ARM_SYMBOLIC_ORACLE (both ~100%), regime may still be saturated. Verdict logic handles this via `MIDDLE_BAND_EQUIV_SATURATED` branch and `baseline_in_band` gate.
- Cross-arc: v1 stretch2_3 was demoted from cap_map alongside stretch4_3 v1 pattern; same demote pattern likely needed. Skunkworks landed-VET should note.

## Prior-work check (substrate-KB concept query 2026-07-02)
`bash tools/substrate_query.sh "STRIPS planning substrate-native BFS action schema retrieval"` returned top hit cosine=0.361 (`substrate_operand_selection_mwp` schema-integration drill — unrelated). No exact prior work on STRIPS BFS with FHRR-substrate action library. Direct predecessor is `stretch4_3_temporal_strips_v2_substrate_native_planner_cpu_v1` (this session, CG'd); the current cell is its non-temporal sibling (planning_strips domain vs temporal_strips domain — distinct scope; drops SLOTU + durkeys + dur field on actions).

## Landed-VET framing prep (for Skunkworks)
- If HP: substrate hosts classical STRIPS planning_strips domain (Stage 3 compositional extension); cross-arc composes with stretch4_3 v2 (temporal). Together they establish substrate viability for two STRIPS variants via substrate-native BFS.
- If HP-equivalence branch: stronger claim — substrate produces BIT-IDENTICAL plans to symbolic control (perfect retrieval), certifying substrate-native equivalence for this domain.
- If HF: substrate can host temporal STRIPS (stretch4_3 v2) but not planning_strips (this cell). Informative scope-limit for cap_map.
- Cross-arc demote note: v1 stretch2_3 (numpy-costume + oracle-goal) should be flagged for cap_map demote alongside stretch4_3 v1 demote pattern.
