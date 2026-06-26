# Pre-registration: substrate_NESS_envelope_alpha_high_extension_v2_checkpoint_repair

**Date:** 2026-06-25
**Anchor:** substrate_NESS_envelope_alpha_high_extension_v2_checkpoint_repair
**Script:** experiments/exp_substrate_NESS_envelope_alpha_high_extension_v2_checkpoint_repair.py
**Queue:** local_cpu_queue
**Seeds:** [11, 13, 19] (cross-cell consistent with v1)
**ALPHA_FRACS (full):** [0.7, 0.8, 0.85, 0.9, 0.95]
**Supersedes:** exp_substrate_NESS_envelope_alpha_high_extension_v1 (hung 2026-06-25 19:50 PDT after 51min CPU; timeout fired 23:26 PDT)

## Repair context (v1 -> v2)

v1 (`exp_substrate_NESS_envelope_alpha_high_extension_v1`) was dispatched 2026-06-25 19:50
PDT and hung. The runner timeout (7200s = 2h) fired at 21:26 with only 2 unit
partials completed (both at af=0.7). Root-cause diagnosis (orchestrator
a0cc5b2780af0d3f7):

1. v1 inner `recall_chain_depth_numpy` is called PER K in K_GRID from the outer
   loop. K_GRID = [3,6,12,18,24,36,48,60,80,100,120]. For each K, v1 builds an
   N x N W matrix (8192 x 8192 float32 = 256 MB) and accumulates K outer-products
   of bipolar vectors per chain x N_CHAINS=24 chains.
2. v1's early-break (line 203) is `if cr < RECALL_THRESH and K > K_GRID[0]: break`.
   This fires when cand_recall drops below 0.90 at any K. At af=0.7 the cliff
   is at K~48 so early-break truncates the K sweep around K=36 -- partial
   completes in ~25-50min.
3. At af=0.85/0.9/0.95 the equilibrium capacity K_eq is TINY (0.63/0.27/0.06).
   Recall stays at 1.0 for ALL practical K (the substrate's cleanup-snap is
   strong enough that even at K=120 chain depth, cleanup-snapping >24 times
   through W still hits the target). So early-break NEVER FIRES at high alpha
   and the run iterates ALL 11 K-values, each costing ~10-15 min wall at
   N=8192 N_CHAINS=24 at K=120 (the dominant term).
4. Per-unit checkpoint at v1's (af, seed) granularity means at 7200s timeout
   the unit's partial is NEVER written -- 50+ min of K=3..K=24 work is LOST
   because K=43+ never completes within the 7200s envelope.

v1 only produced 2 partials (both at af=0.7) before the orchestrator killed
the run; af=0.85/0.9/0.95 had ZERO output because their unit-level partial
never closed.

## v2 fix axes (three together)

### Fix 1: SUB-UNIT CHECKPOINT (per-K granularity)

v1 wrote `partial_metrics_af<af>_s<seed>.json`. v2 ALSO writes
`partial_metrics_af<af>_s<seed>_K<K>.json` for EVERY K in K_GRID_AF after
each K's `recall_chain_depth_numpy` call completes. Compound _ckpt_key is
`af<af>_s<seed>_K<K>` (per `_seed_checkpoint.write_partial_key` PROT-021
contract).

On script restart:
- Existing per-unit partials short-circuit at the unit-level loop (v1
  behaviour preserved)
- For an incomplete unit, the per-K sub-unit partials are RESUMED inside
  `run_unit_progressive`: if a sub-unit partial exists at (af, seed, K) with
  matching N + run_mode, the cached cand_recall/ctrl_recall/hop_frac are
  used and the K=K compute is skipped.

Demonstration (verified in smoke):
- Run 1: 27.4s wall, 14 partials written (3 unit + 11 sub-unit)
- Run 2: 0.5s wall, `done=3/3 units` -- instant resume

### Fix 2: DYNAMIC K_GRID CAP per af

v1 used fixed `K_GRID = [3, 6, 12, 18, 24, 36, 48, 60, 80, 100, 120]` for ALL
alpha_fracs. At high alpha K_eq is tiny so K=60..120 only contributes
"cliff-already-passed" measurements (cr drops to noise floor). v2 computes:

```
K_cap_eff(af) = min(120, max(24, ceil(8 * K_eq(af) + 18)))
```

Empirical calibration: substrate K_obs is ~6-12x K_eq when working; we want
~2x the expected cliff with floor 24 (so even high-alpha gets K-grid coverage
for the ratio curve). Per-af table:

| alpha_frac | K_eq    | K_cap_eff | K_GRID_AF             |
|-----------:|--------:|----------:|-----------------------|
| 0.30       | 39.058  | 120       | full base + early-break |
| 0.50       | 11.957  | 114       | up to K=100; early-break |
| 0.70       | 3.075   | 43        | [3,6,12,24,43]        |
| 0.80       | 1.196   | 28        | [3,6,12,24,28]        |
| 0.85       | 0.633   | 24        | [3,6,12,24]           |
| 0.90       | 0.266   | 24        | [3,6,12,24]           |
| 0.95       | 0.063   | 24        | [3,6,12,24]           |

v1's K=60/80/100/120 at af>=0.8 are eliminated. v1's K=36/48 at af=0.7 are
also dropped in favour of K=43 (the cap). All K values relevant to the lift
curve (K up to ~2x K_obs) are preserved.

### Fix 3: REALISTIC `gated_at` timeout (per Fix #17 strict measurement)

Smoke measurement at N=1024 N_CHAINS=8:
- K=3 wall = 0.55s
- K=6 wall = 0.70s
- K=12 wall = 1.38s
- K=24 wall = 2.84-4.26s (varies by af)
- K=43 wall = 5.36s

Scaling to FULL N=8192 N_CHAINS=24:
- N scaling: O(N^2) for matmul + outer-product -> (8192/1024)^2 = 64x
- N_CHAINS scaling: linear -> 24/8 = 3x
- Per-K multiplier: 64 x 3 = **192x**

Predicted FULL per-K walls:
- K=3: ~106s (1.8 min)
- K=12: ~265s (4.4 min)
- K=24: ~576s (9.6 min)
- K=43: ~1029s (17.2 min)

Per-unit FULL wall = sum over K in K_GRID_AF:
- af=0.7 K_GRID=[3,6,12,24,43]: ~35 min (assuming all K complete; early-break may shorten)
- af=0.8 K_GRID=[3,6,12,24,28]: ~25 min
- af=0.85 K_GRID=[3,6,12,24]: ~18 min
- af=0.9 K_GRID=[3,6,12,24]: ~18 min
- af=0.95 K_GRID=[3,6,12,24]: ~18 min

Total full = 3 seeds x (35 + 25 + 18 + 18 + 18) min = 3 x 114 = **~342 min ~= 5.7h**.

This exceeds the 4h (14400s) max-no-justification threshold of `queue_add.py`.

Two routing options:

**OPTION A (CHOSEN): timeout 14400s + sub-unit checkpoint = safe partial-progress**

With sub-unit checkpoint, a single dispatch completes ~3-4h of compute. On
runner-timeout (Fix #25 landing notifier picks up the timeout), re-queue the
SAME anchor. The script will RESUME from existing sub-unit partials and
finish the remaining ~2h of work in the second dispatch. NO data loss.

**OPTION B (REJECTED): split into v2a and v2b by alpha_frac group**

Could split af=[0.7] and af=[0.8,0.85,0.9,0.95] into two cells. Rejected:
sub-unit checkpoint makes a single-cell resume strategy strictly simpler.

Decision: **timeout_s = 14400 (4h)**. Sub-unit checkpoint guarantees safe
partial progress; can re-queue if not completed in single dispatch.

## Pre-registered bands (UNCHANGED from v1)

Same as v1 prereg:

### HARD_PASS_ALPHA_EXTENSION
- alpha_frac = 0.85: ratio_to_eq >= 2.0 AND ext_hopfrac >= 0.95 AND ext_hopfrac cv <= 0.05

### CHAIN_GRADE_AT_ALPHA_CLIFF
- Chain-grade gate passes at one of {0.8, 0.9, 0.95} but not 0.85

### MIDDLE_BAND_PARTIAL_EXTENSION
- Some alpha above 0.7 holds ext_hopfrac >= 0.85 but no chain-grade gate fires

### HARD_FAIL_RAPID_DEGRADATION
- NO alpha above 0.7 holds ext_hopfrac >= 0.85

### HARD_FAIL_NO_EXTENSION_BEYOND_RAIL
- Chain-grades ONLY at af=0.7 rail

## Q-discipline guard (BIAS-Q; UNCHANGED)

If ext_hopfrac >= 0.995 at ALL alpha_fracs through 0.95: verdict carries
[Q-DISCIPLINE: ...; suspect saturation] flag. Documentation, not
auto-demotion.

## Cross-cell discipline

- ASCII only (verified)
- Substrate-only inference (numpy; zero LLM forward calls)
- Per-alpha metrics in verdict_msg + per_unit + per_subunit (Fix #28)
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] (cross-cell consistent with v1; FRESH seeds vs reference [1,2,3])
- META_M6: K_eq DERIVED in-cell from INDEPENDENT alpha_c=0.138
- META_M7: smoke matches full on N + N_CHAINS + RECALL_THRESH + EXT_GENUINE_THRESH;
  only K_GRID_BASE + SEEDS + ALPHA_FRACS reduce in smoke

## v1-protocol parity verification

v2's `recall_chain_depth_numpy` is VERBATIM copy of v1's:
- Same K-dependent reseeding: `g = np.random.default_rng(seed * 100003 + K * 31 + int(alpha * 1e6))`
- Same chains: N_CHAINS bipolar(K+1, N) generated fresh per K
- Same W build: K outer-product accumulations with (1 - alpha) decay per step
- Same cleanup loop: K snap steps from nodes[0] using FINAL W (built to K)
- Same control: sign-only K steps from nodes[0] using FINAL W

Smoke verdict parity verified:
- v1 smoke: af=0.85 K_obs=16.8 ratio=26.54 ext_hf=1.000
- v2 smoke: af=0.85 K_obs=16.8 ratio=26.54 ext_hf=1.000 (IDENTICAL)
- v1 smoke: af=0.95 K_obs=15.2 ratio=241.54 ext_hf=1.000
- v2 smoke: af=0.95 K_obs=15.2 ratio=241.54 ext_hf=1.000 (IDENTICAL)
- v1 smoke: af=0.7 K_obs=27.2 (K_GRID up to K=40)
- v2 smoke: af=0.7 K_obs=26.2 (K_GRID up to K=43) -- tiny diff from K_GRID endpoint

## Capacity-feasibility analysis (with K_cap)

Per-unit wall at N=8192 N_CHAINS=24:
- af=0.7: sum-K = 3+6+12+24+43 outer-products per chain = 88 ops per chain x 24 chains = 2112 ops
  Plus 88 cleanup-snap matmuls per chain (each K snaps run through codebook of size 24*44=1056)
  At ~0.011s per W outer-product at full scale: ~2112 * 0.011 = ~23s per chain, x24 chains = 9.3min per unit -- LOWER than naive estimate above
- af=0.85+: sum-K = 3+6+12+24 = 45 ops per chain x 24 chains = 1080 ops -- ~6.0min per unit

Refined total full wall estimate: 3 seeds x (9 + 6 + 6 + 6 + 6) min = 99 min = **~1.65h**.

This is well WITHIN the 4h timeout budget. The naive 5.7h above over-counted by
not accounting for the early-break + actual K-count totals.

(NB: the v1 hang happened because at af=0.85 K_GRID had ALL 11 K-values including
K=120 = sum-K = ~540 ops per chain x 24 chains = ~13200 ops; that's ~12x more
work per unit than v2's K_cap=24 schedule. v1 would have needed ~12 x 6min = 72min
per unit at af=0.85, x 3 seeds = 216min just for af=0.85 alone. v2's K_cap kills
this.)

## PROT compliance

- PROT-018 (`_n<N>` suffix): anchor has no `_n<N>` suffix.
- PROT-019 (large-N timeout floor): no `_n<N>` suffix.
- PROT-020 (GPU queue requires torch): local_cpu_queue path; numpy only.
- PROT-021 (long-timeout needs checkpoint): timeout 14400s; SUB-UNIT checkpoint
  per K + unit-level checkpoint per (af, seed). Demonstrated resume.

## Pre-flight smoke + self-test gate

- Self-test: PASSED LOCAL (T1-T8 all pass; verified)
  - T1: K_cap_eff formula correct for all af in {0.7, 0.8, 0.85, 0.9, 0.95}
  - T2: safe_gate_high admits 0.7..0.95, rejects 0.99
  - T3: bipolar shape +/-1
  - T4: k_grid_for_af truncates correctly per cap
  - T5: run_unit_progressive end-to-end at N=256 + sub-unit partial written
  - T6: HP bands locked at module init
  - T7: LLM counter = 0
  - T8: sub-unit checkpoint RESUME path (write -> resume -> same numbers)

- Smoke: PASSED LOCAL (verdict HARD_PASS_ALPHA_EXTENSION; Q-discipline fires)
  - First run: 27.4s wall, 3 unit + 11 sub-unit partials written
  - Second run: 0.5s wall, instant resume (done=3/3 units)
  - v1-protocol parity: af=0.85 K_obs=16.8 IDENTICAL to v1 smoke

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Same verdict ladder as v1; both directions reported in verdict_msg.

## Strategic significance (decision-grade)

Same as v1: extends NESS chain-recall envelope beyond [0.3, 0.7] reference rail.
If HARD_PASS_ALPHA_EXTENSION at af=0.85, NESS deep-chain recall lifts MASSIVELY
past equilibrium; if HARD_FAIL, cliff is identified between 0.7 and target alpha.

## Honest negatives possible (UNCHANGED from v1)

- ext_hopfrac may collapse below 0.85 at alpha_frac=0.80 (rapid degradation)
- K_obs may flatten at high alpha (K_eq -> 0 makes ratio trivially large)
- Per-seed variance at high alpha may push cv above 0.05
- At alpha_frac=0.95, K_eq ~ 0.06 -- ratio >> 2.0 trivially; discriminator is
  ext_hopfrac >= 0.95

## Dispatch plan

1. Author cell + prereg (this file) -- DONE
2. Self-test PASSED locally -- DONE (T1-T8 PASS)
3. Smoke PASSED locally -- DONE (verdict HARD_PASS at smoke; Q-discipline fires)
4. v1 smoke parity verified -- DONE (af=0.85 + af=0.95 IDENTICAL)
5. Path-scoped commit BEFORE dispatch (cell + prereg)
6. Dispatch via `python tools/queue_add.py local_cpu_queue substrate_NESS_envelope_alpha_high_extension_v2_checkpoint_repair experiments/exp_substrate_NESS_envelope_alpha_high_extension_v2_checkpoint_repair.py --prereg preregs/2026-06-25_substrate_NESS_envelope_alpha_high_extension_v2_checkpoint_repair.md --timeout 14400 --purpose "v1 hang repair: sub-unit checkpoint + dynamic K_cap + realistic timeout"`
7. POSITION: behind Gap 4 TWO_TIER (currently running, ~14400s budget) and any Gap 1/3 work
8. File dispatch notification

## Priority

LOWER PRIORITY than active Gap 1/3/4 work per orchestrator routing. NESS is
envelope-extension data, not load-bearing. Can run on local CPU after current
Gap cells finish.

## Test plan post-landing

- Skunkworks step-0 honest re-read of per_unit per_alpha_frac ratio_to_eq + ext_hopfrac
- Verify ext_hopfrac cv across 3 seeds at each alpha_frac
- Compare alpha_frac=0.7 slice to reference cell (parity check)
- If chain-grade extension confirmed: queue composition with c3 sequence-binding
- If HARD_FAIL: queue diagnostic per-hop curve at the cliff alpha
