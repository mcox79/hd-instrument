# Pre-reg: Teacher-through-sparsifier BYPASS diagnostic (code-capacity ceiling, ZERO training)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell (single-file, no chunking, no seed wrappers -- deterministic given a fixed seed, zero
training, a crash costs nothing to retry): `experiments/exp_encoder_teacher_sparsifier_bypass_v1_core.py`
Anchor: `encoder_teacher_sparsifier_bypass_v1` (smoke suffix `_smoke`).
Parent cell (read-only import, NOT edited): `exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`.

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)

Query: "isometric random projection block sparsifier quantization ceiling teacher embedding bypass
no training code capacity" -> top hit cosine=0.2612 (WordNet 'isometry' dictionary entry, not an
arc cell), all other hits <=0.24. NONE at cosine>0.30. GENUINELY NOVEL: no prior cell in this
lineage bypasses the student entirely to isolate the quantizer's own ceiling.

## Why this cell exists

Director/VET-recommended cheapest decisive test (kept explicitly through the v3d->v3e pivot):
pass the raw teacher (BGE-large) embeddings through the SAME K-block hard-argmax+sign quantizer
every trained student in this lineage uses, with NO learned projection at all. This isolates what
the CODE FORMAT ITSELF can preserve (a quantization-capacity ceiling) from what a trained student's
additional learning error costs on top of that ceiling.

## Design

Two FIXED (non-learned) linear lifts from teacher-dim (1024) to the code's pre-quantization width:

- **ORTHO_ISOMETRIC**: QR-orthonormal-columns random matrix (`torch.linalg.qr` reduced mode) --
  W.T@W = I_1024 EXACTLY (verified: max|WtW-I| ~ 6e-7 at smoke scale). Zero information loss before
  quantization; any shortfall from 1.0 spearman is attributable PURELY to the hard block-argmax+
  sign step. This IS the code-capacity ceiling: the best any student could do at this K even with a
  perfect (zero-error) learned map.
- **RANDOM_GAUSSIAN**: i.i.d. N(0, 1/in_dim) projection, NOT orthonormalized -- the generic
  "untrained network" proxy. Explains directly (rather than leaving unexplained) the well-
  documented untrained-network SimHash-like artifact seen at step~0 in every trained run this
  lineage has landed (e.g. v3c seed_7 DENSE~0.9561@step0
  MEASURED@data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_7/metrics.json:recovery.inbatch_traj[0]).

Each lift applied at TWO code sizes (block_l=32 unchanged, only block COUNT changes):
K=128/N=4096 (current production config) and K=256/N=8192 (doubled). This folds in, at zero extra
training cost, the "how much does bigger code close the DENSE->BLOCK gap" question from the
original ceiling-attribution design -- answered here as a PURE code-capacity question, isolated
from student/objective difficulty.

Both lifts are wrapped as a frozen `torch.nn.Module` (`_FrozenLinearEncoder`, `requires_grad=False`)
so they are a drop-in for `v3._encode_hard_block` -- the EXACT SAME quantization code path every
trained student in this lineage uses (no reimplementation, no risk of a subtly-different quantizer
producing an apples-to-oranges number).

## Verdict semantics

This is a DIAGNOSTIC, not a HARD_PASS/HARD_FAIL gated experiment (there is no "student" to certify)
-- follows the precedent set by
`exp_encoder_step1b_capacity_ceiling_train_vs_held_diagnostic_v1` (`verdict: "DIAGNOSTIC_COMPLETE"`).
Reported decomposition (all in `recovery{}`):

- `quantization_ceiling_k128` = ORTHO_K128 spearman (zero-training-error ceiling at current config)
- `quantization_ceiling_k256` = ORTHO_K256 spearman (ceiling at doubled code)
- `code_capacity_gain_ortho_k128_to_k256` = ortho_256 - ortho_128 (pure code-capacity effect)
- `isometry_vs_random_gap_k128` = ortho_128 - random_128 (cost of NOT having a perfect learned map,
  isolated from quantization itself)

## Compute architecture

Class (a) batched (all matmuls; no sequential loops); zero training (no optimizer, no gradient
steps, no checkpoints). Storage strategy: no_storage/no_composition beyond the keyed-unit
integrity check (single-hop bind/unbind, not a chained composition).

## Functional requirements

| Requirement (plain English) | Existing primitive addressed by |
|---|---|
| Measure what the quantizer alone can preserve, zero learning error | fixed isometric lift + `v3._encode_hard_block` (reused verbatim) |
| Explain the untrained-network SimHash-like artifact | random-Gaussian lift, same quantizer |
| Isolate pure code-capacity gain from bigger code | ORTHO at K=128 vs K=256, same isometry construction |
| Confirm the bypass codes are genuine composable SBC codes | `v3._keyed_unit` (bind/unbind/cleanup), integrity-only |

## Effective-vs-nominal parameter audit / bracket / signal-shape

Not a sweep cell (2 lifts x 2 K's, fixed); N/A for gates A/B. Signal-shape (Gate C): teacher
embeddings [n,1024] -> `_FrozenLinearEncoder.forward` [n,out_dim] -> `v3._encode_hard_block`
[n,out_dim] (reshaped internally to [n,K,32]): SHAPE_MATCH, verified live (self-test asserts
`c_last.shape == (n, K*32)` implicitly via `_encode_hard_block`'s own internal reshape, and the
smoke run's per-unit output confirms correct shapes for both K=128 and K=256).

## Positive control / integrity (Gate D-adjacent)

`v3._keyed_unit` on ORTHO_K128 and RANDOM_K128 (J=5, `algebra="sbc"`) confirms the bypass codes
remain composable SBC-format codes (bind/unbind/cleanup) regardless of the fixed vs learned
origin -- SMOKE VERIFIED: both `acc_at1=1.0` at smoke scale. This is integrity-only (not a
recovery gate); RANDOM_BLOCK (fully random, no teacher info at all) is the calibration floor
(SMOKE VERIFIED: spearman=-0.0082, near-zero as expected).

## CRLB / capacity-feasibility

`crlb_n_a`: declared explicitly (not silently omitted) -- this is a zero-training linear-algebra
diagnostic; the learned-map CRLB formula (`r_max = sigma_teacher/sqrt(sigma_teacher^2+0.25/K)`)
governs LEARNED-map noise and does not apply to a fixed isometric/random lift.

## Baseline-in-band

CHARPOS `ret_agree10` in smoke: 0.1886 (within (0.05,0.95)). RANDOM_BLOCK spearman: -0.0082
(near-zero calibration floor, as expected).

## Cell-template mandatory fields (declared)

- `arms_differ_verified: True` (sha256 over all 6 code matrices; verified live in smoke)
- `final_metrics_atomicity: tmp_replace`
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`)
  -- grep-verified clean.
- `cell_chunked: False` (single deterministic pass; a crash costs nothing to retry, no chunking
  needed), `start_marker_written: True`, `crash_diagnostic_present: True`,
  `heartbeat_present: True`, `defensive_error_checking: passed_all_4_patterns`
- `calibration_check: default_ok_for_this_regime` (reuses the SAME K=128/N=4096 quantization
  channel validated throughout this lineage; K=256 keeps block_l=32 unchanged)

## Discriminator-survives-scale

N/A (option not applicable in the usual sense) -- there is no training to saturate; the SAME
closed-form computation runs identically at smoke (local 43905-concept cache, n_test=800) and full
(177899-concept cache, n_test=17790) scale, differing only in V and n_pairs. SMOKE=FULL code path
by construction. SMOKE VERIFIED (2026-07-04): elapsed=6.1s, all 8 units, arms differ, isometry
verified (max|WtW-I|~6e-7 at both K), inner-product preservation verified in self-test. Illustrative
smoke-scale numbers (NOT the certified FULL answer -- different corpus, different sample):
ORTHO_K128=0.8011, RANDOM_K128=0.8187, ORTHO_K256=0.8925, RANDOM_K256=0.8805,
code_capacity_gain(ortho,K128->K256)=+0.0915, isometry_vs_random_gap(K128)=-0.0177 (near-zero,
consistent with random projections already being near-isometric at these ambient dimensions per JL
concentration -- expected, not a bug).

## Timeout / dispatch estimate

Zero training; cost is a handful of matmuls (4 lifts) + one hard-argmax quantize pass at each of 2
K's + spearman over up to 400k held pairs, at V up to 177899. Smoke (n_test=800) landed in 6.1s on
CPU. FULL (n_test=17790, 400k pairs, K up to 256/N=8192) is estimated well under 5 minutes even on
CPU; GPU (per Director/VET instruction to keep the remote saturated) will be faster still.
Requested `--timeout 900` (15 min), generous margin.

## BUGFIX + RE-DISPATCH ADDENDUM (2026-07-04, post-crash)

FULL dispatch (commit e5a084fbe) CELL_CRASHED at
`data/exp_encoder_teacher_sparsifier_bypass_v1/metrics.json` (`elapsed_s=0.0`,
`RuntimeError: Expected all tensors to be on the same device, but found at
least two devices, cuda:0 and cpu!`, traceback at
`_verify_isometry` line 193, `WtW - I`).

**Root cause**: `_verify_isometry` built `I = torch.eye(in_dim,
dtype=WtW.dtype)` with no `device=` kwarg (defaults CPU), while `WtW`
inherits `enc.weight`'s device. `--device` argparse default was `"auto"`;
the runner invokes cells with **no CLI flags at all** (only env vars --
`runner_v2_prod.py:run_one` spawns `[sys.executable, "-u", script_path]`), so
the cell's own default fully governs device selection. The remote host
(marsh@home, serving both `overnight_queue` and `remote_cpu_queue`) has
`torch.cuda.is_available()==True`, so `device_arg="auto"` resolved to
`"cuda"` there -- a `SCRIPT_PRECONDITION_VIOLATION`-class bug (self-test
passed locally on a CPU-only laptop; remote has a GPU even for the CPU
queue).

**Fix** (`experiments/exp_encoder_teacher_sparsifier_bypass_v1_core.py`):
1. `_verify_isometry`: `I = torch.eye(in_dim, dtype=WtW.dtype,
   device=WtW.device)` -- correctness fix, device-agnostic regardless of
   dispatch target.
2. `--device` default changed `"auto" -> "cpu"` -- this cell is zero-training
   linear algebra with no GPU need; pinning `cpu` keeps `remote_cpu_queue`
   dispatch off the host's GPU (determinism + does not contend with any
   concurrently-running GPU job), per exp_dev's `device='cpu' at cell-init`
   convention (commit b522c755 pattern, runner-doesn't-pass-argv class).

**Re-verified locally** (`.venv`, CPU-only laptop, no CUDA available so the
crash could not be literally reproduced, but the fix is structurally
device-agnostic and cannot recur regardless of host):
- `--self-test`: PASS, 16.2s, reproduces the exact commit-message smoke
  numbers bit-for-bit (ORTHO_K128=0.8011, RANDOM_K128=0.8187,
  ORTHO_K256=0.8925, RANDOM_K256=0.8805) --
  MEASURED@d:/AI/hd-instrument/data/exp_encoder_teacher_sparsifier_bypass_v1_selftest/metrics.json.
- Standalone `--smoke`: PASS, 15.7s, `cardinality_ok=true`,
  `arms_differ_verified=true`, 8/8 units, `unit_failures=[]`, `device="cpu"` --
  MEASURED@d:/AI/hd-instrument/data/exp_encoder_teacher_sparsifier_bypass_v1_smoke/metrics.json.
  `ret_agree10` confirmed present for all 4 semantic lift arms + CHARPOS:
  ORTHO_K128=0.5958, RANDOM_K128=0.5850, ORTHO_K256=0.6689,
  RANDOM_K256=0.6779, CHARPOS=0.1886 (smoke-scale, n_test=800; NOT the
  certified FULL answer -- retrieval gets harder as the candidate pool
  grows, confirmed directly by the timing-probe below).

**Timing-probe (discriminator-preview at FULL n_test, satisfies
DISCRIMINATOR-MUST-SURVIVE-SCALE option A)**: reused the local
43905-concept cache (real 177899-concept cache not present locally) but
forced FULL-scale cost knobs (`n_test=17790`, `final_pairs=400_000`,
`charpos_cap`/`n_trials` = FULL values) onto the smoke code path -- an
apples-to-apples wall-clock measurement at the TRUE full n_test, only the
candidate-pool vocabulary differs (43905 vs 177899, held-set SIZE identical
at 17790). Result: **524.9s wall** (private scratch run, not a landed
artifact; output dir deleted after measurement, not committed).
Sanity-consistent with smoke: `ORTHO_K128 spearman=0.8019` (smoke 0.8011),
`ORTHO_K256 spearman=0.8886` (smoke 0.8925). `ret_agree10` dropped as
expected with the larger candidate pool: `ORTHO_K128=0.5291`,
`ORTHO_K256=0.6284` (vs smoke's 0.5958/0.6689) -- directionally consistent
with the ~0.48/~0.58 recollection cited in the dispatch instruction; true
FULL (V_cache=177899, more diverse vocabulary at the SAME held-set size)
is expected in a similar-to-somewhat-lower band. THEORETICAL@candidate-pool-
size-invariant-cost: cache-load is the only step that scales with V_cache
directly (encoding + retrieval cost depend on n_test, which is already
matched); the true-cache load will add a few seconds at most (1.29GB vs
334MB local, ~1.2s measured locally -> ~5s scaled), negligible against the
525s total.

**Revised timeout**: `ceil(1.5 * 525s) = 788s` per the formula in
`queue_add.sh`; setting `--timeout 1800` (>3.4x the measured full-N-matched
wall) for margin against remote-CPU-speed uncertainty (never benchmarked
against this laptop) + the larger real cache load + general safety.
Supersedes the original `--timeout 900` (which was never actually tested
against real full-scale wall time -- the original crash fired at
`elapsed_s=0.0`, before any timeout could bind).

## Composes with

- `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` / the ranked-levers drill (Rank 5:
  student-capacity question) -- this cell answers the CODE-capacity half of that question directly;
  a trained-student BLOCK spearman below `quantization_ceiling_k128` at the SAME K implicates the
  student/objective, not the code format.
- `experiments/exp_encoder_v3e_decline_vs_plateau_v1_core.py` (the plateau-vs-decline diagnostic
  this cell runs alongside, not in place of).

ASCII-only. No emojis. No em dashes.
