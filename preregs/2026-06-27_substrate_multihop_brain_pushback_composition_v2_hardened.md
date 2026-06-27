# Prereg: substrate_multihop_brain_pushback_composition_v2_hardened

Date: 2026-06-27
Anchor: substrate_multihop_brain_pushback_composition_v2_hardened
Cell: experiments/exp_substrate_multihop_brain_pushback_composition_v2_hardened.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive; runners idle)
Wave: Cycle 1 RERUN — load-bearing test that META_BARRIER_1 was prematurely declared
Timeout: 28800s (8h)
Supersedes: 2026-06-27_substrate_multihop_brain_pushback_composition_v1.md (silent-died)

## Motivation: v1 silent-death + hardening rerun

V1 (commit e1614b4f) dispatched Cycle 1 but DIED SILENTLY: output directory
`data/exp_substrate_multihop_brain_pushback_composition_v1/` was never created;
no metrics.json; no stderr/stdout captured by the runner. Root cause could not
be distinguished between:
- module-import crash (e.g. numpy load failure, _seed_checkpoint import)
- selftest assertion fail (e.g. HRR involutive sanity)
- main-loop OOM-kill (W=8192x8192 float32 = 256MB; 3 matrices live = 768MB; PFC
  scratchpads per query)
- runner-launch failure (HDLAB_EXP_NAME mismatch / queue config bug)
- silent OS process kill

Per Orchestrator recommendation: re-author with hardening so silent death is
IMPOSSIBLE. Mechanism is identical; only operational visibility added.

## Hardening delta (this is the entire DIFF from v1)

### L1: EARLY-WRITE on main entry

Before any compute, `_main_inner()`:
- creates `data/exp_<anchor>/` (mkdir parents=True, exist_ok=True)
- writes `metrics.json` with verdict=UNKNOWN, verdict_msg=STARTED, pid, ts_iso,
  expected_n_units, completed_units=0

After this point, silent death is VISIBLE in the filesystem (metrics.json exists
with STARTED verdict telling you we got past module init + path setup).

### L2: PER-ARM PROGRESS updates

After EACH arm-depth-seed completes (5 arms x 2-4 depths x 1-3 seeds), a
`progress_writer` closure rewrites metrics.json with:
- verdict=UNKNOWN, verdict_msg=PROGRESS
- completed_units (running count)
- last_seed / last_arm / last_depth
- list of seeds with any partial data

Mid-run death now exposes how far we got via metrics.json inspection.

### L3: OUTER try/except around entire main

`__main__` wraps `_main_inner()` in `try/except BaseException`. On any
exception:
- get_output_dir + mkdir (best-effort) if not already set
- write metrics.json with verdict=UNKNOWN, verdict_msg="CRASHED: <class>: <msg>",
  full traceback under _exception_traceback
- re-raise the original exception (META_RULE_J record-and-halt)

### L4: IMPORT-CRASH SENTINEL

The module-level `_selftest()` call is wrapped in try/except. On crash:
- best-effort guess of output dir (HDLAB_EXP_NAME or anchor name)
- write metrics.json + import_crash.json with verdict=UNKNOWN,
  verdict_msg="IMPORT_CRASH: <class>: <msg>"
- re-raise

### atexit handler updated to be PROGRESS-aware

Only synthesizes metrics from partials when current metrics.json verdict is
empty/UNKNOWN. Won't overwrite a HARD_PASS/HARD_FAIL/MIDDLE_BAND/RAIL_SANITY_BREACH
final write.

## Mechanism: IDENTICAL to v1 (search file for V1_MECHANISM_IDENTICAL marker)

5 arms (BASELINE, R1_REPLAY_INTO_W_C, R2_PFC_SCRATCHPAD, R3_BIDIRECTIONAL,
COMBINED_R1_R2_R3) per drill
`notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md`.

### R1: NREM-replay-into-W_C (composes B1 + B5 + B7)

Brain mechanism: complementary-learning-systems + sharp-wave-ripple replay +
schema chunking. Substrate-native: build W_H (hippocampal) via Hebbian binding;
simulate offline NREM replay; compute CONTINUOUS trace amplitude (per v4 drill
correction); M-CFU-style cohort top-K with amp >= 0.55; write A->C shortcuts
into SEPARATE W_C. Multi-hop tries W_C first; fall back to per-hop W_H walk.

### R2: PFC-scratchpad-SEPARATE-W (B2)

Brain mechanism: Miller-Cohen 2001 PFC persistent-activity store. Substrate-
native: dedicated W_PFC matrix (init zeros per query); each hop reads W_H,
writes cleaned intermediate to W_PFC at slot i+1; next hop queries W_H using
the clean intermediate. W_H is READ-ONLY across hops (SEPARATE-W discipline).

### R3: Bidirectional-meet-in-middle (B3)

Brain mechanism: Foster-Wilson 2006 reverse SWR replay. Substrate-native:
forward walk from start + backward walk from goal via HRR-involutive unbinding
(bipolar self-inverse). Meet criterion: exact match OR cosine >= 0.30 at any
(fwd_step k, bwd_step depth-k).

### COMBINED arm (R1 + R2 + R3 stacked)

Try R1 W_C shortcut first; on miss run R3 bidirectional with R2 W_PFC
scratchpad. Commit on shortcut OR meet OR forward final == goal.

## ARMS (5 mandatory; IDENTICAL to v1)

- ARM_BASELINE
- ARM_R1_REPLAY_INTO_W_C
- ARM_R2_PFC_SCRATCHPAD
- ARM_R3_BIDIRECTIONAL
- ARM_COMBINED_R1_R2_R3

## Pre-reg bands (HARD-LOCKED PROSPECTIVE; IDENTICAL to v1)

Target depth: 5.

HARD_PASS_BARRIER_BROKEN (chain-grade-eligible; CERT +1):
- ARM_COMBINED depth-5 mean >= 0.65
- AND ARM_COMBINED > MAX(R1, R2, R3) + 0.001
- AND ARM_COMBINED > BASELINE + 0.45
- AND cv across seeds <= 0.08
- AND BASELINE depth-5 in [0.10, 0.20] on majority of seeds

HARD_PASS_INDIVIDUAL_WINS:
- Any individual R1/R2/R3 depth-5 mean >= 0.50
- AND > BASELINE + 0.30
- AND cv <= 0.08

MIDDLE_BAND:
- ARM_COMBINED depth-5 in [0.45, 0.65)
- OR any individual R-arm depth-5 in [0.30, 0.50)

HARD_FAIL:
- ARM_COMBINED depth-5 < 0.25 (pivot to X1 primitive replacement)
- OR ARM_COMBINED within 0.05 of ARM_BASELINE

RAIL_SANITY_BREACH (uninterpretable):
- ARM_BASELINE depth-5 outside [0.10, 0.20] on majority of seeds

## Cardinality (META_RULE_H mandatory)

EXPECTED_N_UNITS_FULL = 5 arms * 3 seeds * 4 depths = 60 arm-depth-seed entries.
EXPECTED_N_UNITS_SMOKE = 5 arms * 1 seed * 2 depths = 10 entries.
HARD_FAIL_CARDINALITY_BREACH = observed != expected (verdict flag).

## Discriminator-must-survive-scale (D1)

Smoke uses FULL-N parameters (N=8192, V_C=200, P=10) with reduced
n_chains=50 + 2 depths + 1 seed. The 5-arm separation at depth-5 is the
discriminator; baseline at depth-5 must reproduce 0.145 +/- 0.05 even at smoke
scale.

Note: USER 2026-06-27 NO LOCAL directive => no full local smoke. Cell-author
selftest (small-N=1024 V=60) PASSED locally on v1 e1614b4f and is unchanged
in v2 (validates mechanism correctness + SEPARATE-W assertions + HRR
involutive sanity). Full smoke runs on remote_cpu.

## Substrate-only-decode gate (load-bearing)

n_llm_calls per seed = 0 (numpy-only mechanism; substrate primitives only).

## BRAIN_MECHANISM_VS_CARICATURE checks (load-bearing per drill; IDENTICAL to v1)

Runtime assertions (cell raises RuntimeError on violation):
- W_H is READ-ONLY during all arm executions; SEPARATE W_C / W_PFC matrices.
- R3 backward direction uses bipolar HRR-involutive unbinding.
- R1 replay uses CONTINUOUS amplitude gating (min_amp=0.55), NOT binary.

## META_RULE_J (no silent except) — UPGRADED in v2

V2 has FIVE structured try/except blocks; ALL re-raise or print-and-halt:
1. `_write_minimal_metrics`: prints to stderr on failure, does not raise
   (last-ditch helper; raising would mask the original exception in L3 handler).
2. `_write_import_crash_sentinel`: prints to stderr on failure, does not raise.
3. `_selftest()` wrapper: writes sentinel, then re-raises (BaseException).
4. `_atexit_synth`: prints + re-raises on partial-aggregation failure.
5. `_main_inner` L3 wrapper: writes CRASHED metrics, re-raises (BaseException).

Zero silent swallows in mechanism code. The helpers swallow to stderr because
re-raising would lose information about the real failure.

## Real data / synthetic provenance

Random bipolar key/value pairs (matches v1; mechanism is about composition of
architectural fixes, NOT corpus semantics). allow_synthetic=True.

## Compute budget

Per seed (full): 5 arms * 4 depths * 200 test_chains. W_H build ~1-2s; W_C build
~5-10s; per-arm-per-depth ~10-30s. Total per seed ~450s nominal; 3 seeds ~1400s;
add 4x safety => ~5600s expected; cap at 8h (28800s) timeout.

PROT-019 compliance: anchor name does NOT contain `_n<N>` suffix.
PROT-021 compliance: cell imports experiments._seed_checkpoint (resumable_seeds,
write_partial_key, aggregate_partials, write_metrics). Long timeout requires
checkpoint per PROT-021.

L2 progress-writes add minor I/O (per-arm metrics.json rewrite, ~6KB each, 60
writes max full mode = ~360KB total). Negligible vs compute.

## Decision tree (post-verdict; IDENTICAL to v1)

- HARD_PASS_BARRIER_BROKEN: BARRIER 1 BROKEN; chain-grade-eligible; atomize.
- HARD_PASS_INDIVIDUAL_WINS: one of R1/R2/R3 alone is the lever; ablate.
- MIDDLE_BAND: queue N1 isolation audit + R4 attractor.
- HARD_FAIL_PIVOT: pivot to X1 primitive replacement.
- HARD_FAIL_FLAT: composition adds no value; debug SEPARATE-W or meet-criterion.
- RAIL_SANITY_BREACH: cell uninterpretable; re-design.

NEW failure modes (silent-death-rerun): if metrics.json has
- verdict=UNKNOWN msg=STARTED -> died during W_H/W_C build or first arm
- verdict=UNKNOWN msg=PROGRESS -> died mid-run; check last_seed/arm/depth
- verdict=UNKNOWN msg=CRASHED:* -> exception captured; read _exception_traceback
- verdict=UNKNOWN msg=IMPORT_CRASH:* -> import-time crash; read _traceback

## SCHEMA-VET 5b per-arm HP scope (IDENTICAL to v1)

Each arm's metrics fully reported in metrics.json per_seed as
`arm_<name>_depth_<d>` with top1, elapsed_s_arm, mechanism-specific extras.

## Reference

V1 prereg: `preregs/2026-06-27_substrate_multihop_brain_pushback_composition_v1.md`
V1 cell: commit e1614b4f
Drill: `notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md`
