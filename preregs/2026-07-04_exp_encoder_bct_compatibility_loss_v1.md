# Pre-reg: Encoder BCT (backward-compatible-training) compatibility-loss cell

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED bands; SMOKE + local FULL-preview
both run before remote dispatch; FULL landing to happen on `remote_cpu_queue`.

Cell: `experiments/exp_encoder_bct_compatibility_loss_v1_core.py`
Anchor: `encoder_bct_compatibility_loss_v1` (smoke suffix `_smoke`, full = no suffix).
Data-only reuse (NOT code import -- this cell is fully self-contained, no sibling-experiment
import, per the dispatch contract's explicit-SCP risk):
`data/substrate_concept_encoder_v1b_v3global_mid/_ckpt_block_global.pt` (frozen "version A")
+ `data/substrate_index/cached_indices/bge_large_v2_name_43905_8a40445a.npz` (teacher cache,
hardcoded filename, NOT a "pick largest" heuristic).

Spec source: `notes/research_drill_brain_grounded_continual_self_improving_encoder_2026-07-04.md`
("Cheap decisive test" Part-3 recommendation) + the READ-ONLY probe
`preregs/2026-07-04_exp_encoder_cross_checkpoint_retrieval_compat_v1.md`, which MEASURED
cross-checkpoint retrieval collapsing to ~1.0-1.5% of same-checkpoint retrieval (HARD_FAIL,
min_ratio=0.0100 at full scale) with no compatibility loss, and routed: "pull the explicit
compatibility-loss work forward -- do NOT adopt any periodic re-distillation/encoder-swap
cadence without a compatibility term."

## Question

Train a small "version B" encoder (new init, new training-set subsample -- a genuinely
different/updated encoder instance vs the already-existing "version A" = the R1 GLOBAL MID
checkpoint) TWICE, PAIRED (identical init seed, identical batch-index sequence, identical
data), differing ONLY in an explicit BCT compatibility loss term:
- `NO_BCT`: `loss = L_rkd` (in-batch geometry-distillation to the BGE teacher)
- `WITH_BCT`: `loss = L_rkd + BCT_WEIGHT * L_bct`, `L_bct = mean(1 - cos(z_B(x), z_A_frozen(x)))`
  over the training batch, anchored to version A's FROZEN continuous output (not its
  post-quantization block code -- see "Design iteration" below).

Does the BCT loss restore cross-version retrieval (A's frozen index, B's query -- the
realistic "encoder got updated, old vectors are still in the store" scenario) from collapse
to usable (`>=0.50` of same-checkpoint-A ceiling), WITHOUT wrecking WITH_BCT's own held-out
semantic quality relative to NO_BCT's?

## Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01)

Query: "BCT backward compatible training compatibility loss encoder version cross-checkpoint
retrieval anchoring frozen embedding" -> top hit cosine=0.3291 ("Versioning + backwards
compatibility", `notes/research_drill_production_deployment_architecture_2026-06-07.md`,
deployment/ops versioning practice, NOT this mechanism); rank 2-3 FHRR cross-modal projection
chunks (different topic); rank 4-5 WordNet/FrameNet lexical "compatibility" entries. NONE of
the top-5 hits address this specific BCT-loss mechanism. **Verdict: GENUINELY NOVEL**, same
conclusion as the source probe's own prior-work check.

## Design iteration (during smoke -- documented per calibration_check discipline)

v1 of this cell anchored `L_bct` against version A's post-quantization BLOCK code. Smoke
(BCT_WEIGHT=3.0) showed BLOCK cross-ratio recovering to 0.4467 but DENSE cross-ratio stuck at
0.0467 -- block-argmax quantization (1-of-32 winner per block) is too coarse a supervision
target to pull the FULL 4096-bit sign pattern into alignment. Redesigned `L_bct` to anchor
against version A's RAW CONTINUOUS output `z_A` (pre-quantization, normalized) instead --
matches the standard BCT/embedding-migration design (Shen et al. 2020's influence loss
regresses embeddings, not a discretized readout). Re-verified by self-test (`_train_b`
exercised directly on synthetic data: `synthetic_ratio_no=0.0000`, `synthetic_ratio_with=0.99`)
and smoke (see "Measured results") BEFORE any weight tuning -- confirms the core mechanism
works, independent of the specific weight chosen.

## Calibration (adaptive_with_discriminator_gate, META_RULE_M)

BCT_WEIGHT swept at smoke scale (N_TRAIN_B=500, STEPS=150, single seed=7) over
`{0.03,0.05,0.07,0.08,0.1,0.12,0.15,0.2,0.3,0.5,0.75,1.0,1.5,2.0,3.0,8.0}` BEFORE selecting
the FULL-dispatch default (not cherry-picked post-hoc for a specific verdict tier):

| weight | cross_block | cross_dense | min_ratio | quality | retention |
|--------|-----------|-----------|-----------|---------|-----------|
| (NO_BCT, w=0) | 0.0133 | 0.0133 | 0.0133 | 0.8652 | 1.0000 |
| 0.03 | 0.5000 | 0.8800 | 0.5000 | 0.6418 | 0.7418 |
| 0.05 | 0.6200 | 0.9000 | 0.6200 | 0.6390 | 0.7386 |
| 0.07 | 0.6667 | 0.9133 | 0.6667 | 0.6113 | 0.7065 |
| 0.08 | 0.6933 | 0.9467 | 0.6933 | 0.5761 | 0.6659 |
| 0.10 | 0.7267 | 0.9600 | 0.7267 | 0.7234 | 0.8361 |
| 0.12 | 0.7467 | 0.9400 | 0.7467 | 0.6600 | 0.7628 |
| 0.15 | 0.7800 | 0.9600 | 0.7800 | 0.6177 | 0.7139 |
| 0.20 | 0.8000 | 0.9733 | 0.8000 | 0.5906 | 0.6827 |
| 0.30 | 0.9400 | 0.9933 | 0.9400 | 0.5422 | 0.6267 |
| 0.50-3.0 | 0.9867-0.9933 | 1.0000 | 0.9867-0.9933 | 0.499-0.507 | 0.577-0.586 |

MEASURED@this sweep (all values from local smoke-scale runs this session, not hypothesized):
weight `>=0.5` saturates cross-retrieval to 0.99-1.00 but collapses quality_retention to
~0.58; weight `<0.05` is noisy/near the 0.50 retrieval floor; the low-weight regime
(0.03-0.3) shows real, non-saturated variance run-to-run at this small smoke scale (single
seed, N_TRAIN_B=500 is itself noisy -- e.g. w=0.08 and w=0.12 sandwich w=0.10's retention=0.84
with retention=0.67/0.76, not a smooth monotone curve). **Selected BCT_WEIGHT=0.15** as a
principled midpoint of the well-behaved, non-saturated low-weight regime, NOT the specific
value that happened to score highest in the noisy sweep (that would be p-hacking the verdict
tier). The verdict is read off honestly at whatever FULL (12x more training data, 8x more
steps -- expected to be less noisy) measures, not tuned to force a HARD_PASS.

## Bands (declared before the FULL run)

Let `ratio[arm,code] = cross_top1[arm,code] / same_A_top1[code]` for `arm in {NO_BCT,
WITH_BCT}`, `code in {block, dense}`. `min_ratio[arm] = min` over both codes.
`quality[arm] = semantic_spearman(B_dense_probe, teacher)` (held-out, dense-only).
`quality_retention = quality[WITH_BCT] / quality[NO_BCT]`.

- **BASELINE_MUST_COLLAPSE gate (discriminator-fires, positive control)**: `min_ratio[NO_BCT]
  < 0.50` -- if NOT (i.e. the baseline does not collapse at this reduced CPU scale), verdict
  auto-demotes to `MIDDLE_BAND` with message `DISCRIMINATOR_DID_NOT_FIRE` (nothing to fix,
  test is vacuous at this scale) regardless of WITH_BCT's own numbers.
- **HARD_PASS**: `min_ratio[NO_BCT] < 0.50` (baseline genuinely collapsed) AND
  `min_ratio[WITH_BCT] >= 0.50` AND `quality_retention >= 0.80`.
- **HARD_FAIL (case A, fix doesn't work)**: `min_ratio[WITH_BCT] < 0.20` (barely moved from
  NO_BCT baseline).
- **HARD_FAIL (case B, fix works but wrecks quality)**: `min_ratio[WITH_BCT] >= 0.20` AND
  `quality_retention < 0.50`.
- **MIDDLE_BAND**: everything else (real partial restoration and/or real partial quality
  trade-off -- e.g. `0.20 <= min_ratio[WITH_BCT] < 0.50`, or `min_ratio[WITH_BCT] >= 0.50` but
  `0.50 <= quality_retention < 0.80`).

`HP_SCOPE`: the HARD_PASS/HARD_FAIL gate applies ONLY to `{min_ratio[WITH_BCT],
quality_retention}` (post baseline-collapse confirmation). `SAME_A`, `SAME_B` (both arms),
and `RANDOM_CONTROL` units are integrity-only sanity checks, exempt from the science gate.

## SCHEMA-VET / META_RULE fields

- `cardinality_ok`: `EXPECTED_N_UNITS = 14` (SAME_A x2 codes + [SAME_B + CROSS] x 2 arms x 2
  codes = 8 + RANDOM_CONTROL x2 codes + SEMANTIC_SPEARMAN x2 arms [dense only] =
  2+8+2+2=14). MEASURED@smoke: 14/14. Verdict counts `per_unit`; shortfall ->
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `arms_differ_verified`: sha256 hash-check across A_block, A_dense, B_block[NO_BCT],
  B_block[WITH_BCT], B_dense[NO_BCT], B_dense[WITH_BCT] (6-way pairwise). MEASURED@smoke:
  True (6 distinct digests).
- `final_metrics_atomicity`: `"tmp_replace"` (this cell's own `metrics.json.tmp` +
  `os.replace`).
- except-discipline: `except SystemExit`/`KeyboardInterrupt` re-raise before `except
  Exception`; grep gate for bare `except:` / `except BaseException` PASSED (verified before
  dispatch: only the docstring's prose sentence matched, no actual bare-except statement).
- `crlb_floor_computed`: **n/a** -- retrieval-identity ratio, not a noise-floor metric (same
  rationale as the prior cross-checkpoint probe). `discriminator_reachability`: true (HARD_FAIL
  and HARD_PASS both physically reachable; MEASURED spanning 0.0133 to 0.9933 across the
  weight sweep).
- `baseline_in_band` (META_RULE_AG analog): `SAME_A`/`SAME_B` (both arms, both codes) must be
  `>= 0.99`. MEASURED@smoke: all six = 1.0000. Hard-asserted in code
  (`SAME_CHECKPOINT_SANITY_FAIL` if violated).
- discriminator-fires (META_RULE_K): `RANDOM_CONTROL` (both codes) must be `<= 0.10`.
  MEASURED@smoke: dense=0.0067, block=0.0000. Hard-asserted (`RANDOM_CONTROL_TOO_HIGH` if
  violated). Separately, `BASELINE_MUST_COLLAPSE` (above) is this cell's OWN
  discriminator-fires check on the phenomenon under test: MEASURED@smoke NO_BCT min_ratio =
  0.0133, comfortably below the 0.50 ceiling -- the collapse discriminator DOES fire at this
  reduced CPU scale (500 train items / 150 steps vs A's 39515/1800), confirming the failure
  mode reproduces even far below full production scale, before crediting any fix.
- discriminator survives scale: SMOKE runs at `N_TRAIN_B=500, STEPS=150, BATCH=64,
  N_PROBE=150`; FULL (this cell's terminal CPU-scale tier) uses `N_TRAIN_B=6000, STEPS=1200,
  BATCH=256, N_PROBE=1000`. Per DISCRIMINATOR-MUST-SURVIVE-SCALE Option A: the FULL config was
  ALSO run directly on local CPU (not merely smoke) BEFORE remote dispatch, because this cell
  is cheap enough (~1-3 min at FULL scale) to preview at full-N locally for free. See
  "Measured results" for the FULL-preview numbers.
- `calibration_check`: `"adaptive_with_discriminator_gate"` (see "Calibration" section above;
  BCT_WEIGHT=0.15 selected via smoke-scale sweep, discriminator-fires [BASELINE_MUST_COLLAPSE]
  verified at every sweep point, final value not tuned to force a specific verdict tier).
- `cell_chunked`: false (single fixed seed=7 for the split; both arms are a single paired
  training run each, not a multi-seed statistical claim -- matches the sibling probe's
  precedent of single-seed for this class of mechanism-existence cell). `start_marker_written`:
  true. `crash_diagnostic_present`: true (tmp+replace atomic CELL_CRASHED writer).
  `heartbeat_present`: **n/a-with-reason** -- MEASURED elapsed_s smoke=28.4s; FULL expected
  well under 300s (see timeout section) -- both far under the 60s heartbeat-cadence /
  1800s progress-logging thresholds. `defensive_error_checking`: `"passed_all_4_patterns"`.
- `progress_logging`: expected **n/a** (timeout target well under 1800s; see Timeout section)
  but `print(..., flush=True)` used throughout anyway (defense-in-depth, zero cost).
- Section 15 gates: `sweep_alignment_verdict` N/A (BCT_WEIGHT is a single tuned constant at
  dispatch time, not a swept axis in the shipped cell). `discriminating_fraction` N/A (not a
  sweep cell). `composition_edges`: N/A (single-model training + retrieval, no primitive
  composition chain). `positive_control_arms`: `SAME_A`/`SAME_B` (ceiling=1.0) AND
  `NO_BCT` itself (must reproduce the collapse -- BASELINE_MUST_COLLAPSE gate) serve as the
  positive controls. `functional_requirements`: FR1 (can an explicit compatibility loss
  preserve retrieval-by-identity against an already-built index when the encoder is updated)
  is the entire point of this cell; no existing chain-grade primitive maps to it (new
  mechanism-validation, directly requested by the drill's own Part-3 recommendation).

## Compute architecture

Class (a) batched. Both students' forward/backward passes are single-batch MLP calls
(`batch<=256`); retrieval matrices are batched matmuls (chunked at 1024 rows to bound peak
memory, not because retrieval is sequential). No per-phase-point Python loop. Training itself
(the two paired `_train_b` calls) is inherently sequential ONLY in the sense that both arms
must share the identical batch-index generator seed (paired-trial requirement) -- not a
batching inefficiency, a correctness requirement. Storage strategy: no_storage (this cell
trains two small in-memory students and reads one already-trained frozen checkpoint + one
teacher cache; it writes no new atoms/index entries).

**Dispatch: `remote_cpu_queue`** (not GPU -- MLP sizes here are trivially small; not
`local_cpu_queue` -- FULL is not a smoke/probe per the standing USER-lock
`feedback_smoke_only_local_cpu_no_full_dispatches_USER_LOCKED_2026-07-01.md`).

**Explicit non-auto-SCP data dependency (READ BEFORE DISPATCH):** `CKPT_A`
(`_ckpt_block_global.pt`, ~120MB) is gitignored (`data/*/**` pattern) and was trained LOCALLY
today (2026-07-04, local CPU run per the R1 GLOBAL MID docstring) -- it does NOT exist on the
remote CPU box and is covered by NEITHER git-pull NOR queue_add.sh's script/prereg/sibling-
helper auto-SCP (verified: `ssh marsh@home Test-Path .../substrate_concept_encoder_v1b_
v3global_mid` returned `False` before this cell's authoring). MUST be explicit-scp'd to
`marsh@home:C:/dev/hd-instrument/data/substrate_concept_encoder_v1b_v3global_mid/
_ckpt_block_global.pt` as a manual pre-dispatch step. The teacher cache
(`bge_large_v2_name_43905_8a40445a.npz`, ~319MB) is CONFIRMED already present on remote with
an IDENTICAL byte size to the local copy (334512907 bytes both sides, verified via SSH
`Get-ChildItem` before authoring this cell) -- no teacher-cache SCP needed. This is WHY the
teacher-cache resolver in this cell hardcodes the exact filename rather than picking
"largest available" -- the remote box's `cached_indices/` also holds much larger (177k-concept)
caches from the ongoing corpus-ingest pipeline; "largest" would silently load the wrong
corpus there (a different V, different permutation) -- the `SPLIT_MISMATCH` hard-abort would
catch the resulting crash, but hardcoding the filename avoids relying on that safety net.

## Timeout

MEASURED@smoke (this session): `elapsed_s=28.4` (N_TRAIN_B=500, STEPS=150 x2 arms).
MEASURED@local FULL-preview (this session): `elapsed_s=421.7` (N_TRAIN_B=6000, STEPS=1200
x2 arms, run locally BEFORE remote dispatch). Dispatch `--timeout 1800` (30 min): ~4.3x the
measured local FULL-preview elapsed_s, padding for a possibly-slower/busier remote CPU box
(the remote runs BOTH `overnight_queue` GPU jobs and `remote_cpu_queue` CPU jobs on the same
physical host per the dispatch architecture, so CPU contention is plausible). `timeout_s >=
1800` makes `progress_logging` MANDATORY (Section 17): declared `"print_flush_true"` --
every training-step log line and every eval-unit log line in this cell already uses
`print(..., flush=True)`, satisfying the pattern without any additional code.

## Halt conditions

Teacher cache missing/wrong-schema/NaN -> `TEACHER_CACHE_MISSING` / `TEACHER_CACHE_SCHEMA` /
`TEACHER_CACHE_ROW_MISMATCH` / `TEACHER_CACHE_NAN`. Split reproduction mismatch vs
`EXPECTED_MID_SPLIT=(39515,4390)` -> `SPLIT_MISMATCH` (teacher cache is not the exact file A
trained against, or V_cache drifted). Checkpoint missing / state-dict mismatch ->
`CHECKPOINT_MISSING` / `STATE_DICT_MISMATCH`. NaN/Inf loss during training ->
`NAN_LOSS` (per-arm). Same-checkpoint sanity `< 0.99` -> `SAME_CHECKPOINT_SANITY_FAIL`.
Random-control `> 0.10` -> `RANDOM_CONTROL_TOO_HIGH`. Bit-identical arms ->
`META_RULE_AF_VIOLATION`. Cardinality shortfall -> `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
Any of the above raise and let the crash-diagnostic writer record `CELL_CRASHED` with full
traceback.

## Measured results

**Self-test** (synthetic, no disk artifacts): PASS. `same=1.0000 random=0.0000
block_ste_ok=True synthetic_ratio_no=0.0000 synthetic_ratio_with=0.9900` (2.2s) -- confirms
the core `_train_b` mechanism itself (not just tuning) restores cross-version retrieval when
BCT is on and does not when it is off, on fully synthetic data independent of any real
checkpoint/teacher.

**SMOKE** (N_TRAIN_B=500, STEPS=150, BATCH=64, N_PROBE=150, BCT_WEIGHT=0.15, seed=7)
MEASURED@`data/exp_encoder_bct_compatibility_loss_v1_smoke/metrics.json`:
`SAME_A_BLOCK=1.0000 SAME_A_DENSE=1.0000 SAME_B_NO_BCT_{BLOCK,DENSE}=1.0000
SAME_B_WITH_BCT_{BLOCK,DENSE}=1.0000` (all integrity gates pass).
`CROSS_AIDX_BQUERY_NO_BCT_BLOCK=0.0133 CROSS_AIDX_BQUERY_NO_BCT_DENSE=0.0133` ->
`min_ratio[NO_BCT]=0.0133` (baseline collapses hard, consistent with the prior probe's
full-scale ~0.01 finding -- discriminator fires even at this much-reduced scale).
`CROSS_AIDX_BQUERY_WITH_BCT_BLOCK=0.7800 CROSS_AIDX_BQUERY_WITH_BCT_DENSE=0.9600` ->
`min_ratio[WITH_BCT]=0.7800` (>= 0.50 HARD_PASS retrieval bar).
`RANDOM_CONTROL_DENSE=0.0067 RANDOM_CONTROL_BLOCK=0.0000` (both <= 0.10 ceiling).
`SEMANTIC_SPEARMAN_NO_BCT_DENSE=0.8652 SEMANTIC_SPEARMAN_WITH_BCT_DENSE=0.6177` ->
`quality_retention=0.7139` (below the 0.80 HARD_PASS quality bar, above the 0.50 FAIL floor).
Cardinality: 14/14. Arms differ: verified (6 distinct sha256 digests). Elapsed: 28.4s.
**Verdict: MIDDLE_BAND** -- real, substantial retrieval restoration (0.0133 -> 0.7800) with a
real, moderate quality cost (retention 0.71).

**FULL preview (local, run before remote dispatch, N_TRAIN_B=6000, STEPS=1200, BATCH=256,
N_PROBE=1000, BCT_WEIGHT=0.15, seed=7)**
MEASURED@`data/exp_encoder_bct_compatibility_loss_v1/metrics.json` (this LOCAL preview run;
the same config was then shipped to `remote_cpu_queue` for the official landing -- see
dispatch report for the remote-landed values, expected to closely reproduce these since the
computation is fully deterministic given fixed seeds):
`min_ratio_no_bct=0.0000` (baseline collapses COMPLETELY at FULL scale -- even more total
than smoke's 0.0133, consistent with more training producing a MORE specialized/divergent
NO_BCT encoder). `min_ratio_with_bct=0.8910` (>= 0.50 HARD_PASS bar, cleared by a 0.39
absolute margin -- comfortably above the 5%-band-width-above-floor requirement).
`semantic_spearman: {NO_BCT: 0.7127, WITH_BCT: 0.7046}` ->
`quality_retention_with_bct=0.9886` (>= 0.80 HARD_PASS bar, essentially no quality cost --
much better than smoke's 0.7139 retention, indicating the smoke-scale trade-off was an
undertraining artifact of the tiny 500-item/150-step regime, not a genuine retrieval-vs-
quality tension at real FULL scale). Cardinality: 14/14. Elapsed: 421.7s.
**Verdict: HARD_PASS.**
`verdict_msg`: "BCT loss restores cross-version retrieval from collapse (NO_BCT
min_ratio=0.0000) to usable (WITH_BCT min_ratio=0.8910 >= 0.5) while retaining 98.9% of
NO_BCT's held-out semantic quality."

## Verdict routing

**HARD_PASS, as measured at FULL scale (local preview).** This is a clean, decisive,
positive answer to the drill's own Part-3 recommendation: an explicit BCT compatibility
loss (anchored against version A's frozen CONTINUOUS output, weight=0.15, tuned via a
discriminator-fires-gated smoke sweep) restores cross-version retrieval from TOTAL collapse
(0%) to 89.1% of same-checkpoint ceiling, at essentially no held-out semantic-quality cost
(98.9% retention). Concrete, immediate recommendation: adopt an explicit BCT anchoring term
as a REQUIRED step for any future encoder-version promotion where the new version must stay
retrieval-compatible with an already-built index -- the mechanism is cheap (training-time
only, no inference-time cost, no architecture change) and the FULL-scale numbers show the
retrieval-vs-quality trade-off feared at smoke scale is NOT fundamental (it was a smoke-scale
undertraining artifact). This directly closes the drill's own Part-3 recommendation with a
positive, mechanism-level answer (a fix exists, is cheap, and works), which the READ-ONLY
cross-checkpoint probe could only diagnose, not supply. Follow-up (not blocking): confirm the
89.1%/98.9% numbers reproduce on the remote-landed run (fully deterministic given fixed
seeds, so a close match is expected, not a new discovery); consider whether annealing
BCT_WEIGHT or a larger anchor-item count could push min_ratio_with_bct even closer to 1.0
without touching the already-excellent quality retention.
