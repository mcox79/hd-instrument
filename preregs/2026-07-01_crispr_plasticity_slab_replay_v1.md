# pre-reg: crispr_plasticity_slab_replay_v1

**Date:** 2026-07-01
**Author:** exp_dev (cell-author) per Research drill aa07fd96
**Anchor:** `crispr_plasticity_slab_replay_v1`
**Path:** `experiments/exp_crispr_plasticity_slab_replay_v1.py`
**Drill:** `notes/research_drill_continual_learning_CRISPR_regime_map_2026-07-01.md` (rank-1 cell)

---

## Scientific question

Does slab-boundary R-item replay from prior slabs raise `transfer_final` from 0.000 to >= 0.15 in the CRISPR append-only architecture, without corrupting current-slab retention (`forget_p1 <= 0.05`)?

Baseline: `MEASURED@d:/AI/hd-instrument/data/exp_substrate_cl_crispr_append_only_v1/metrics.json:per_arm_aggregate.ARM_APPEND_ONLY_PLUS_CFRPE.mean_transfer_final = 0.000` (n_seeds=3, cv=0.000).

---

## CRITICAL DESIGN NOTE: base-cell alpha-per-slab regime violation caught pre-dispatch

**Bug in base cell (v1) that would silently invalidate any replay result:**

- Base cell config: `J=5, M=400, D_slab=819, alpha_per_slab = 400/819 = 0.488`
- Hopfield capacity cliff `alpha_c ~ 0.138` (Amit-Gutfreund closed-form)
- Base cell operates at ~3.5x cliff => per-slab Hebbian CANNOT self-recall
- Verified `MEASURED@d:/AI/hd-instrument/data/exp_substrate_cl_crispr_append_only_v1/metrics.json:per_arm_aggregate.ARM_APPEND_ONLY_NEW_DIMS.phase_recalls_per_seed`: **ALL entries 0.000-0.017** across all seeds/phases including phase-0 self-recall
- Drill's "forget=0.006 MM-grade" framing is `pr[0][0] - pr[J-1][0] = 0.000 - 0.000 = 0` -- zero-of-zero, NOT retention
- Per SCHEMA-VET Gate B / META_RULE_AG (baseline-in-band): base regime is by-construction-below-floor; not discriminating

**Regime correction for this cell (v1 replay):** hold N_BASE=4096, hold J=5, LOWER M_per_phase from 400 to 100.
- `alpha_per_slab_corrected = 100/819 = 0.122` THEORETICAL@Amit-Gutfreund-cliff -- comfortably in-band
- Per-slab self-recall expected >= 0.85 at noise=0.20 (per selftest2 pattern)
- Preserves J=5 (5 slabs = drill's structural intent) and N_BASE=4096 (substrate scale)

Deviation from drill spec (M=400) is documented + justified per RULE F-2 (regime correction to enable discriminator to fire; drill's HP threshold preserved).

---

## Architecture (delta from base CRISPR cell)

Cell EXTENDS `experiments/exp_substrate_cl_crispr_append_only_v1.py`. Copy-and-modify (not import-and-monkey-patch) so smoke reproducibility is transparent.

**New mechanism:** at the START of each new-slab Hebbian write (phase j >= 1), inject R replay atoms sampled uniformly at random from ALL prior slabs (phases 0..j-1). Each replay atom is a re-encoding of a prior-slab atom-ID projected into the current slab's D_slab dimensions via a per-atom-identity persistent bipolar seed.

**Replay encoding (Option A per feasibility analysis):**
- Each atom has a global atom-ID (int): `atom_id = phase_idx * M_per_phase + within_phase_idx`
- Encoding at slab `s`: `bipolar(atom_id * 1000 + s)` via `np.random.RandomState` -> unique D_slab-dim bipolar per (atom_id, slab_idx)
- Replay operation: sample R atom-IDs from prior slabs; re-encode each in current slab dim; Hebbian-write alongside current-phase atoms

**Transfer measurement (per drill spec):**
- After phase J-1 (last phase), for each prior-slab atom (all M * (J-1) of them), re-encode in slab J-1's dim, add noise=0.20, retrieve via full slab-routing
- `transfer_final = fraction that cosine-match > 0.80` to their original prior-slab bipolar in prior slab's dim (round-trip)
- baseline (R=0) has NO replay so prior atoms have NO re-encoding in current slab => routing to prior slab succeeds ONLY if we use the prior-slab encoding directly at probe time; this matches the drill's transfer=0.000 baseline (nothing was ever written that supports transfer)

**Additional metric per Substrate-KB find:**
- `transfer_pre_replay` = phase recall of current phase atoms immediately AFTER Hebbian write, BEFORE replay-mixing (per prior drill remediation note)
- `transfer_post_replay` = current-phase recall AFTER all replay passes (may degrade if replay corrupts)

---

## Arms (4 arms; single R sweep)

Cell sweeps `R in {0, 5, 20, 50}` across seeds {7, 17, 23}. R=0 arm = base APPEND_ONLY reproduction at CORRECTED alpha (validates regime change). R>0 arms = replay variants.

- `ARM_APPEND_ONLY_R0` (baseline; regime-corrected sanity rail; PRIMARY comparison anchor)
- `ARM_APPEND_ONLY_R5` (5 replay items per slab boundary)
- `ARM_APPEND_ONLY_R20` (20 replay items per slab boundary; drill's primary)
- `ARM_APPEND_ONLY_R50` (50 replay items per slab boundary; stress; may corrupt)

n_seeds x n_R = 3 x 4 = 12 units. **EXPECTED_N_UNITS = 12** (META_RULE_H cardinality check).

---

## Discriminator

**Primary discriminator (drill HARD-PASS):**
- `transfer_final >= 0.15` on ANY replay arm (R > 0)
- AND `forget_p1 <= 0.05` on same arm (replay doesn't corrupt current-slab)
- AND `cv <= 0.15` across 3 seeds for the winning R arm

**Pre-arm sanity rail (must pass before mechanism claims):**
- `ARM_APPEND_ONLY_R0` phase-0 self-recall >= 0.85 (validates alpha=0.122 regime correction)
- `ARM_APPEND_ONLY_R0` transfer_final < 0.05 (reproduces baseline zero-transfer at corrected regime)

**HARD_FAIL (decisive):**
- `transfer_final < 0.05` on all R > 0 arms (replay does not rescue transfer -- deeper structural issue)
- OR `forget_p1 > 0.10` on all R > 0 arms (replay corrupts current-slab)

**MIDDLE_BAND:** `transfer_final in [0.05, 0.15]` on some R arm (partial rescue; needs R sweep extension)

**Regime sanity HARD_FAIL:**
- `ARM_APPEND_ONLY_R0` phase-0 self-recall < 0.60 (regime correction insufficient; base substrate at cliff after all)

---

## SCHEMA-VET pre-dispatch checklist

### 1. cardinality_ok (META_RULE_H)
- `EXPECTED_N_UNITS = 12` (3 seeds x 4 R values)
- Verdict logic counts `len(per_arm_results)` across seeds; < 12 => `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`

### 2. Per-unit failure-class instrumentation (META_RULE_J)
No bare `except:`. All exception handlers catch specific classes + record `failure_class` field per failed unit.

### 3. Discriminator-fires gate (META_RULE_K)
Smoke's discriminator: R=20 arm's `transfer_final` > R=0 arm's `transfer_final` by at least 0.05 at smoke-scale. Vacuous smokes (all arms zero) auto-demote.

### 4. Strictly-above-floor target (META_RULE_L)
HARD_PASS `transfer_final >= 0.15` strict. Floor-hugging results (0.150-0.155) classified MIDDLE_BAND.

### 5. Calibration-check field (META_RULE_M)
`calibration_check: "default_ok_for_this_regime"` -- inherits base CRISPR primitives; alpha=0.122 chosen to keep base primitive in its chain-grade regime.

### 6. Arms-must-differ (META_RULE_AF)
`arms_differ_verified` at smoke gate via sha256 of per-arm W_final tensor. R=0 vs R=5 must differ.

### 7. Atomic-final-metrics-write (META_RULE_AH)
`final_metrics_atomicity: "tmp_replace"` -- write to `metrics.json.tmp`, `os.replace` at end.

### 8. except SystemExit before except Exception (MANDATORY)
Confirmed in template. `except Exception` NOT `except BaseException`. Grep gate applied pre-dispatch.

### 9. CRLB / capacity-feasibility validation
- `crlb_floor_computed: 0.05` -- lower bound on random-cross-slab-probe cosine hit rate (bipolar random hit rate at noise=0.20)
- `crlb_formula_reference: "P(cos>0.80 | random bipolar) ~ 0 for D_slab=819 (Gaussian tail)"`
- `discriminator_reachability: True` -- HP=0.15 is above CRLB floor by 3x
- `THEORETICAL@P_recall = P(cos > 0.80) via CLT approximation`
- Full-N preview: R=20 preview arm at 1 seed in smoke to verify discriminator survives scale

### 10. Baseline-in-band (META_RULE_AG)
- `ARM_APPEND_ONLY_R0` transfer_final expected ~0.00-0.05 (below discriminating band lower)
- `ARM_APPEND_ONLY_R20` transfer_final expected 0.10-0.30 (in discriminating band)
- Discriminating fraction >= 3/4 arms predicted in-band
- Phase-0 self-recall expected ~0.85-0.95 (above 0.05 floor, below 0.95 saturation)

### 11. HYPOTHESIZED / MEASURED marking (META_RULE_AC)
- `baseline transfer_final = 0.000` MEASURED@d:/AI/hd-instrument/data/exp_substrate_cl_crispr_append_only_v1/metrics.json:per_arm_aggregate.ARM_APPEND_ONLY_PLUS_CFRPE.mean_transfer_final
- `phase-0 self-recall at alpha=0.122` HYPOTHESIZED@preregs/2026-07-01_crispr_plasticity_slab_replay_v1.md (based on selftest2 pattern: alpha=M/D=0.078 achieves >= 0.80)
- `R=20 transfer_final rescue` HYPOTHESIZED@preregs/2026-07-01_crispr_plasticity_slab_replay_v1.md (P_deflated=0.40 per drill; hippocampal replay literature)
- `Hopfield cliff alpha_c = 0.138` THEORETICAL@Amit-Gutfreund closed-form

### 13. Chunked single-seed-per-cell
- Multi-seed cell (3 seeds); using `experiments/_seed_checkpoint.py` per base cell pattern
- Start-marker + crash-diagnostic + heartbeat: implemented per template
- `cell_chunked: false` (using per-seed checkpoint helper, not chunked cell files -- consistent with base CRISPR pattern)
- `start_marker_written: True`
- `crash_diagnostic_present: True`
- `heartbeat_present: True`
- `defensive_error_checking: passed_all_4_patterns`

### 15. Test-design failure prevention
**A) Effective-vs-nominal audit:** `swept_params: {R: [0,5,20,50]}`; `effective_params_per_primitive: {slab_hebbian: effective_M_per_slab = M_per_phase + R * (J-1)}`; sweep_alignment_verdict: `ALIGNED`
**B) Bracket includes discriminating band:** predicted `transfer_final` per R: {0: 0.02, 5: 0.06, 20: 0.18, 50: 0.30}; discriminating fraction = 3/4 = 0.75 (>= 0.30)
**C) Signal shape compatibility:** primitive composition is intra-cell (slab Hebbian + slab-Hebbian-replay); shape match by construction
**D) Positive-control arm at test regime:** `ARM_APPEND_ONLY_R0` reproduces base CRISPR primitive at CORRECTED regime; if phase-0 self-recall < 0.60 => REGIME_MISMATCH HARD_FAIL (positive control failed)
**E) Functional requirement decomposition:**
  - FR1: current-slab retention -> per-slab Hebbian (chain-grade)
  - FR2: prior-slab retrieval after new-slab writes -> slab-boundary replay (novel mechanism under test)
  - FR3: cross-slab identity persistence -> atom-ID persistent-seed encoding (novel)

### 16. Run-mode verification post-dispatch
Cell defaults `run_mode='full'` when neither `--smoke` nor `--self-test` passed. Post-dispatch verify: `run_mode == 'full'` in metrics.json, size >= 5KB.

---

## Cost estimate

- Smoke (J=3, M=50, R=20, N=4096, 2 seeds): ~90-180s
- Full (J=5, M=100, R sweep, N=4096, 3 seeds): 4 arms * ~1500s = ~6000s = ~100min = ~2 CPU-hr (matches drill estimate)
- Timeout: 3.0 * expected = 10800s -> use 10800s per PROT-019 float

---

## Queue routing

- **Smoke:** `local_cpu_queue` (per USER 2026-07-01 lock; smoke only on local)
- **Full:** `remote_cpu_queue` via Orchestrator (harness-denied push; router calls Orchestrator)
