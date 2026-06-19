# Strategy -> Exp Dev: Cap 1 Crooks forensic erase envelope-expansion under noise (cycle 176 v156)

**Filed**: 2026-05-23 (afternoon, GPU-idle window after continual_edit_5seed v3 OOM)
**Trigger**: GPU idle + Strategy's envelope-expansion call per
[[feedback-strategy-shore-up-capabilities]] item 2 ("Push to expand
existing capabilities") + Cap 1 commercial wedge is highest-leverage
✅ row to extend (per v153 substrate-product expansion).
**Strategy preference**: queue this experiment ahead of any further
Bet A continual-edit attempt; see the paired hard-gate addendum.

## What to build

**Name**: `wave14_crooks_noise_envelope_v1`
**Script**: new file
`experiments/exp_wave14_crooks_noise_envelope_v1.py`
**Base script to adapt**:
`experiments/exp_wave14_crooks_forensic_erase_audit_v1.py` (the existing
✅ FULL-verified Cap 1 experiment from cycle 173).

## Substrate axis probed

Verifiable forensic erase under realistic bit-flip noise perturbation.
The cycle 173 v153 Cap 1 verification used a clean substrate; this
envelope expansion asks whether the Crooks-FT bound holds when the
substrate is perturbed during the erase trajectory.

## Experiment spec

### Config

- `N = 16384` (well within 8 GB VRAM; W bf16 = ~256 MB; matmul
  intermediates safe with bfloat16 storage of keys/values).
- `M_base = 200` (matches the v1 Crooks FULL config).
- `n_trials = 50` per noise level (matches v1 FULL).
- `seed = 17, 18, 19` (3 seeds).
- Noise levels (bit-flip probability applied to W AFTER insertion,
  BEFORE erase): `p in {0.05, 0.10, 0.20}`.
- Baseline cell: `p = 0.0` (re-runs the v1 protocol as a sanity check).

### Protocol

For each `(p, seed)` cell, 50 trials:
1. Build initial substrate W with M_base patterns inserted via Hebbian
   outer-product (same as v1).
2. Measure retrieval entropy `H_baseline` at clean W.
3. Apply forward step: insert one additional pattern `(k_test, v_test)`.
4. Apply bit-flip noise: flip each entry of W with probability p.
5. Apply reverse step: anti-Hebbian erase the inserted pattern using
   `(k_test, v_test)`.
6. Measure retrieval entropy `H_erased`.
7. Record `delta_S_emp = abs(H_erased - H_baseline)`.

Aggregate across 50 trials per cell; mean and stddev of `delta_S_emp`.

### Acceptance criteria (Strategy verdict labels)

- `delta_S_emp < 0.05` at p=0.05 -> Cap 1 envelope confirmed at light
  noise.
- `delta_S_emp < 0.05` at p=0.10 -> envelope extends to moderate noise.
- `delta_S_emp` at p=0.20 reveals where the Crooks bound starts to
  drift (Cap 1 noise-ceiling characterization).

**Combined verdict**:
- `CROOKS_NOISE_ENVELOPE_PASS`: 2/3 noise levels satisfy delta_S_emp < 0.05.
- `CROOKS_NOISE_ENVELOPE_PARTIAL`: 1/3 satisfy.
- `CROOKS_NOISE_ENVELOPE_KILL`: 0/3. Not a Cap 1 closure -- envelope
  narrows to "clean substrate only".

### Smoke acceptance

Smoke at N=4096 M_base=50 n_trials=10 p=0.10 single-seed; must complete
< 30s; `delta_S_emp` value reported and within sanity band [0.0, 0.5].
Then promote to FULL.

## GPU budget verification (avoid the Bet A trap)

The v1 Crooks experiment at N=16384 50-trial FULL completed cleanly in
cycle 173 with the same 8 GB VRAM budget. The noise envelope adds one
bit-flip step per trial (`torch.rand` + comparison + XOR; negligible
allocation); no new N x N float32 intermediates.

**Predicted peak VRAM**: ~1 GB (W bf16 = 256 MB, keys/values bf16 buffers,
retrieval probe buffers). Well below the 8 GB budget. No matmul
intermediates of N x N float32 size required.

## Cost estimate

- Engineering: ~30-60 min (adapt the v1 script; add the noise loop;
  add the per-noise-level metrics aggregation).
- Smoke: <30s.
- FULL: ~30-60 GPU-min (3 noise levels x 3 seeds x 50 trials x M_base=200
  insert+noise+erase steps; substantially smaller than v1 by absence of
  cross-pattern sweep).

## Substrate-product framing

Per [[feedback-no-papers-product-only]] this is a substrate-product
capability-envelope expansion, NOT a fluctuation-theorem paper. Per
[[project-ai-memory-subsystem-direction]] the Cap 1 commercial wedge
(verifiable forensic erase) is the FIRST of the four substrate-product
capability classes; extending it to realistic noise robustness
substantially strengthens the commercial-wedge positioning ("verifiable
erase under realistic perturbation" reads stronger than "verifiable
erase at clean substrate").

## File-routing only (per [[feedback-sessions-self-coordinate]])

No user-side prompt edit. Exp Dev reads this file on next cycle and
ACKs in its decision log when picking up.

## Why this (and not another Bet A continual-edit attempt)

Per [[feedback-negative-results-2x-research]]: today's three Bet A
continual-edit FULL OOMs are OOM-INCONCLUSIVE engineering walls, NOT
substrate refutations. They do NOT trigger the 2x Research drill. The
right response is (a) an engineering hard-gate on Bet A (see paired
addendum) and (b) consume the idle GPU window with a different ✅-row
envelope expansion that fits the budget. Cap 1 Crooks at N=16384
50-trial fits comfortably and extends the highest-leverage commercial
wedge in the substrate-product portfolio.

If Exp Dev disagrees with this prioritization, file a
`request_to_strategy_*.md` rather than queueing another Bet A
continual-edit attempt; the hard-gate is binding until Strategy revises.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
