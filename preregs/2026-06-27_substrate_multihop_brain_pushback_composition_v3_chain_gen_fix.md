# Prereg: substrate_multihop_brain_pushback_composition_v3_chain_gen_fix

Date: 2026-06-27
Anchor: substrate_multihop_brain_pushback_composition_v3_chain_gen_fix
Cell: experiments/exp_substrate_multihop_brain_pushback_composition_v3_chain_gen_fix.py
Queue: remote_cpu_queue
Wave: Cycle 1 RERUN #2 — chain-gen feasibility fix on top of v2 hardening
Timeout: 28800s (8h)
Supersedes: 2026-06-27_substrate_multihop_brain_pushback_composition_v2_hardened.md (chain-gen infeasibility)

## Motivation: v2_hardened chain-gen infeasibility + bundled fix

V2_hardened (commit 442708b9) dispatched Cycle 1 with full L1-L4 visibility but
CRASHED at module init. The L4 IMPORT_CRASH sentinel captured the exception:

```
RuntimeError: BLOCKING make_deep_chains: only 0/200 generated for V=200
disallow|=200 max_depth=8
```

ROOT CAUSE: The `make_deep_chains` function uses a `disallow_s` set to prevent
test chains from sharing a start node with training chains. After 200 training
chains in V_C=200, every node has been "used" — so when test-chain generation
runs with `disallow_s = train_starts`, every candidate start is blocked and the
function raises after `tries < n_chains * 200` budget runs out (0/200 succeed).

The same root cause took down multi-hop combined v1 (200/500 generated, ~40%
yield) and v2 (180/200, ~90% yield with the function eventually succeeding by
luck). v2_hardened crossed the threshold to FULL infeasibility (0/200) because
the training generation now uses 100% of V; nothing left for test.

## V3 chain-gen fix (drill bundle option 1+2; cheap + safe)

DELTA over v2_hardened (this is the entire DIFF):

| Parameter | v2 | v3 | Rationale |
|---|---|---|---|
| V_CONCEPTS | 200 | **1000** | 5x vocab; even after 200 train + 200 test starts blocked, ~600 candidates free |
| HOP_DEPTHS (full) | [2,3,5,8] | **[2,3,5]** | drop depth-8; max_depth=5 still tests multi-hop discriminator |
| max_depth (per chain) | 8 | **5** | each chain consumes max_depth+1 unique nodes; 6 vs 9 |
| EXPECTED_N_UNITS (full) | 60 | **45** | 5 arms * 3 seeds * 3 depths |
| HOP_DEPTHS (smoke) | [2,5] | [2,5] | unchanged |
| EXPECTED_N_UNITS (smoke) | 10 | 10 | unchanged |

EVERYTHING ELSE IDENTICAL TO V2_HARDENED:
- Mechanism: 5 arms (BASELINE, R1_REPLAY_INTO_W_C, R2_PFC_SCRATCHPAD,
  R3_BIDIRECTIONAL, COMBINED_R1_R2_R3)
- Hardening: L1 early-write + L2 per-arm-progress + L3 outer try/except +
  L4 import-crash sentinel
- Pre-reg bands (HARD_PASS / MIDDLE_BAND / HARD_FAIL / RAIL_SANITY_BREACH)
- BASELINE_SANITY_DEPTH = 5 (still in HOP_DEPTHS)
- BASELINE_SANITY band [0.10, 0.20]
- R1/R3 tuning params (top_K=30, cohorts=5, min_amp=0.55, meet_tau=0.30)
- N_DIM=8192, N_PREDICATES=10, SEEDS=[7,17,23]
- N_CHAINS_TRAIN=200, N_CHAINS_TEST=200
- substrate-only-decode gate
- META_RULE_J no-silent-except discipline

Search the v3 cell file for marker "V2_MECHANISM_IDENTICAL" to confirm mechanism
preservation. Search for "V3 CHAIN-GEN FIX" for the 3 changed parameters.

## V3 selftest STRENGTHENED (new feasibility check)

V3's `_selftest()` adds a FULL-CONFIG feasibility check that runs `make_deep_chains`
at V=V_CONCEPTS, max_depth=max(HOP_DEPTHS), n_chains_train=N_CHAINS_TRAIN, then
n_chains_test=N_CHAINS_TEST (with train-starts disallowed). If either generation
fails, selftest raises AssertionError → L4 sentinel captures it → cell never
queues a doomed run.

LOCAL VERIFICATION 2026-06-27:
- selftest PASS at full-config: V=1000 max_depth=5 train=200 test=200 OK
- All 5 arm functions return finite top1 in [0,1]
- All SEPARATE-W discipline assertions hold
- HRR involutive bipolar self-inverse holds
- Shortcut counts correct (8/8)

## Mechanism (IDENTICAL to v2_hardened; IDENTICAL to v1)

5 arms per drill notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md.

### R1: NREM-replay-into-W_C (composes B1 + B5 + B7)

Brain mechanism: complementary-learning-systems + sharp-wave-ripple replay +
schema chunking. Substrate-native: build W_H (hippocampal) via Hebbian binding;
simulate offline NREM replay; compute CONTINUOUS trace amplitude; M-CFU-style
cohort top-K with amp >= 0.55; write A->C shortcuts into SEPARATE W_C. Multi-hop
tries W_C first; fall back to per-hop W_H walk.

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

## ARMS (5 mandatory; IDENTICAL to v2/v1)

- ARM_BASELINE
- ARM_R1_REPLAY_INTO_W_C
- ARM_R2_PFC_SCRATCHPAD
- ARM_R3_BIDIRECTIONAL
- ARM_COMBINED_R1_R2_R3

## Pre-reg bands (HARD-LOCKED PROSPECTIVE; IDENTICAL to v2/v1)

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

EXPECTED_N_UNITS_FULL = 5 arms * 3 seeds * 3 depths = 45 arm-depth-seed entries.
EXPECTED_N_UNITS_SMOKE = 5 arms * 1 seed * 2 depths = 10 entries.
HARD_FAIL_CARDINALITY_BREACH = observed != expected (verdict flag).

## Discriminator-must-survive-scale (D1) — RE-CALIBRATED for V3

V3 raises V_C 5x. This affects baseline expectation:
- BASELINE at depth-5 with V=200 was empirically ~0.145 (sanity rail v2/v1).
- BASELINE at depth-5 with V=1000 is expected to be LOWER (5x more candidates
  for argmax cleanup; harder discrimination per hop).

Two possibilities:
1. BASELINE depth-5 stays in [0.10, 0.20] → rail holds, verdict logic clean.
2. BASELINE depth-5 drops below 0.10 → RAIL_SANITY_BREACH triggers.

We KEEP the rail at [0.10, 0.20] as PROSPECTIVE; if breach occurs, the verdict
is RAIL_SANITY_BREACH and we re-calibrate the rail in v4. This is honest
behavior per pre-reg discipline: don't widen rails post-hoc to absorb V_C
change.

ALTERNATIVE: If RAIL_SANITY_BREACH triggers WITH ARM_COMBINED >= 0.65, the
finding is STILL substantive (composition wins even with harder baseline),
but cell-author MUST re-author v4 with calibrated rail before chain-grade
claim per A5 cert-owner discipline.

Note: USER 2026-06-27 NO LOCAL directive => no full local smoke. Cell-author
selftest validates mechanism + chain-gen feasibility at full config.

## Substrate-only-decode gate (load-bearing)

n_llm_calls per seed = 0 (numpy-only mechanism; substrate primitives only).

## BRAIN_MECHANISM_VS_CARICATURE checks (load-bearing per drill; IDENTICAL to v2)

Runtime assertions (cell raises RuntimeError on violation):
- W_H is READ-ONLY during all arm executions; SEPARATE W_C / W_PFC matrices.
- R3 backward direction uses bipolar HRR-involutive unbinding.
- R1 replay uses CONTINUOUS amplitude gating (min_amp=0.55), NOT binary.

## META_RULE_J (no silent except) — UPGRADED in v2; preserved in v3

V3 has FIVE structured try/except blocks; ALL re-raise or print-and-halt:
1. `_write_minimal_metrics`: prints to stderr on failure, does not raise.
2. `_write_import_crash_sentinel`: prints to stderr on failure, does not raise.
3. `_selftest()` wrapper: writes sentinel, then re-raises (BaseException).
4. `_atexit_synth`: prints + re-raises on partial-aggregation failure.
5. `_main_inner` L3 wrapper: writes CRASHED metrics, re-raises (BaseException).

Zero silent swallows in mechanism code.

## Real data / synthetic provenance

Random bipolar key/value pairs (matches v2/v1; mechanism is about composition
of architectural fixes, NOT corpus semantics). allow_synthetic=True.

## Compute budget

V3 has 75% the work of v2 (45 vs 60 arm-depth-seed entries; 3 vs 4 depths).
V_C=1000 vs 200 increases per-hop matmul cost by 5x (E @ ... is V_C x N).

Per seed (full): 5 arms * 3 depths * 200 test_chains. W_H build ~1-2s; W_C
build ~5-15s (V=1000 increases cleanup cost); per-arm-per-depth ~15-40s.
Total per seed ~500s nominal; 3 seeds ~1500s; add 4x safety => ~6000s
expected; cap at 8h (28800s) timeout same as v2.

PROT-019 compliance: anchor name does NOT contain `_n<N>` suffix.
PROT-021 compliance: cell imports experiments._seed_checkpoint (resumable_seeds,
write_partial_key, aggregate_partials, write_metrics). Long timeout requires
checkpoint per PROT-021.

L2 progress-writes: 45 writes max full mode ~270KB total. Negligible.

## Decision tree (post-verdict; IDENTICAL to v2/v1)

- HARD_PASS_BARRIER_BROKEN: BARRIER 1 BROKEN; chain-grade-eligible; atomize.
- HARD_PASS_INDIVIDUAL_WINS: one of R1/R2/R3 alone is the lever; ablate.
- MIDDLE_BAND: queue N1 isolation audit + R4 attractor.
- HARD_FAIL_PIVOT: pivot to X1 primitive replacement.
- HARD_FAIL_FLAT: composition adds no value; debug SEPARATE-W or meet-criterion.
- RAIL_SANITY_BREACH:
  - If baseline TOO LOW (< 0.10): expected with V_C=1000 5x; re-calibrate
    rail in v4 to [0.05, 0.15] or similar empirical band; finding still
    interpretable if ARM_COMBINED high.
  - If baseline TOO HIGH (> 0.20): unexpected; cell uninterpretable.

NEW failure modes (silent-death-rerun; from v2):
- verdict=UNKNOWN msg=STARTED -> died during W_H/W_C build or first arm
- verdict=UNKNOWN msg=PROGRESS -> died mid-run; check last_seed/arm/depth
- verdict=UNKNOWN msg=CRASHED:* -> exception captured; read _exception_traceback
- verdict=UNKNOWN msg=IMPORT_CRASH:* -> import-time crash; read _traceback
  (V3 strengthens this with full-config feasibility check)

## SCHEMA-VET 5b per-arm HP scope (IDENTICAL to v2/v1)

Each arm's metrics fully reported in metrics.json per_seed as
`arm_<name>_depth_<d>` with top1, elapsed_s_arm, mechanism-specific extras.

## Reference

V2 prereg: `preregs/2026-06-27_substrate_multihop_brain_pushback_composition_v2_hardened.md`
V2 cell: commit 442708b9
V1 prereg: `preregs/2026-06-27_substrate_multihop_brain_pushback_composition_v1.md`
Drill: `notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md`
