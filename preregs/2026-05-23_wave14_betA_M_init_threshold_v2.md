# Pre-reg: Bet A M_init capacity envelope respec v2 (Strategy cycle 174 v154)

**Filed**: 2026-05-23
**Trigger**: wave14_betA_M_init_threshold_v1 FULL = BETA_M_INIT_UNIFORM_KILL
  was an OOM artifact (all 6 M_init values hit CUDA OOM at N=65536).
  Strategy cycle 174 classified as NOT a substrate refutation.
**Script**: experiments/exp_wave14_betA_M_init_threshold_v2.py

## Research question

What is the M_init capacity envelope of the Bet A anti-Hebbian substrate at
N=65536? Specifically: does the substrate retain memories across the lower half
of the M_init range {1024, 2048, 4096, 8192} at the rescued operating point
(N=65536, n_edits=100)? And what is the M_init/N ratio at which retention
degrades when tested at lower N (N=8192)?

## Design

### Sweep A (primary) -- lower-half capacity envelope at N=65536
- N = 65536
- M_init_grid = {1024, 2048, 4096, 8192}
- n_edits = 100
- seeds = {17, 23, 31, 41, 53} (5 seeds)
- Memory fix: torch.cuda.empty_cache() BEFORE each M_init iteration
- Upper bound rationale: M_init=8192 at N=65536 was the cycle 172 v2 5-seed
  PASS anchor. Sweep A characterizes the region below that anchor.

### Sweep B (upper-end extension) -- capacity ceiling vs N at lower VRAM cost
- N = 8192
- M_init_grid = {16384, 32768, 65536}
- n_edits = 100
- seeds = {17, 23, 31, 41, 53} (5 seeds)
- Upper rationale: at N=8192 the W matrix is 512MB (bf16), fitting easily in
  8GB VRAM even at M_init=65536. This characterizes the M_init/N ratio for
  the upper half without the N=65536 VRAM pressure.

## Substrate-physics axis probed

M_init capacity ceiling of an anti-Hebbian outer-product associative memory:
the fraction alpha = M_init/N above which retained-pair accuracy degrades.
This is the Amit-Gutfreund-Sompolinsky (AGS) storage capacity axis for Hebbian
associative networks -- specifically whether the substrate's kept_acc >= 0.85
threshold holds across the {1024, 2048, 4096, 8192} regime at N=65536.

## Predicted outcomes (falsifiable)

P1 (Sweep A): M_init=8192 at N=65536 replicates the cycle 172 v2 PASS
  (mean_kept >= 0.85, sd < 0.05). Confidence: 0.85 (direct replication of
  prior anchor; OOM was the failure mode in v1, not substrate physics).

P2 (Sweep A threshold): A KILL->PASS transition exists somewhere in
  {1024, 2048, 4096} -> {8192}. Confidence: 0.50 (unknown whether all
  lower M_init values also pass or whether there is a threshold below 8192).

P3 (Sweep A lower floor): M_init=1024 at N=65536 may KILL
  (alpha=1024/65536 ~ 0.016; very low load, but edit operations may interfere).
  Confidence: 0.35 that M_init=1024 kills.

P4 (Sweep B upper-end): At N=8192, at least M_init=16384 (alpha=2.0) will
  produce a non-OOM measurement. Confidence: 0.90 (W is 512MB at N=8192;
  16384 stored vectors; should fit 8GB VRAM).

P5 (Sweep B): A KILL->PASS transition will appear in {16384, 32768, 65536}
  at N=8192, establishing the M_init/N capacity ratio for the upper regime.
  Confidence: 0.55.

## Verdict definitions

Both sweeps use the same verdict taxonomy (computed independently per sweep):

| Verdict | Condition |
|---|---|
| BETA_M_INIT_OOM_INCONCLUSIVE | All M_init points hit CUDA OOM; no measurement possible |
| BETA_M_INIT_UNIFORM_PASS | All non-OOM M_init points: mean_kept >= 0.85 |
| BETA_M_INIT_UNIFORM_KILL | All non-OOM M_init points: mean_kept < 0.50 |
| BETA_M_INIT_BOUND_FOUND | Clear KILL (mean_kept < 0.50) -> PASS (mean_kept >= 0.85) transition detected |
| BETA_M_INIT_MIXED | Intermediate / no clean transition |

The combined metrics.json verdict reflects the Sweep A (primary) verdict.
Sweep B verdict is reported separately in summary.sweep_B.verdict.

## Acceptance criteria (from Strategy cycle 174 respec request)

- At least one M_init at N=65536 produces 5 seeds of data with mean_kept >= 0.85 sd < 0.05
- At least three M_init points at N=65536 produce non-OOM measurements
- Sweep B covers M_init >= 16384 with non-OOM measurements at N=8192

## What this respec is NOT

This is a substrate-product capacity-envelope measurement per
[[feedback-no-papers-product-only]]. It is NOT a scaling-law paper. It
extends the M_init/N operating envelope for Bet A substrate-product claims;
it does not gate any existing capability (axis already confirmed at
M_init=8192 N=65536 in cycle 172).

## Hardware budget estimate

- Sweep A: ~25-35 GPU-min (4 M_init x 5 seeds x 100 edits at N=65536)
- Sweep B: ~5-10 GPU-min (3 M_init x 5 seeds x 100 edits at N=8192)
- Total: ~30-45 GPU-min (matches Strategy estimate)

## Hard-fail thresholds (per [[feedback-lit-scan-calibration-penalty]])

- If Sweep A still returns BETA_M_INIT_OOM_INCONCLUSIVE after memory hygiene
  fix: escalate to Option B (chunked allocation); file upstream note to Strategy.
- If Sweep A M_init=8192 does NOT replicate mean_kept >= 0.85 despite non-OOM:
  genuine substrate failure -- file to Strategy as new REFUTATION evidence.
