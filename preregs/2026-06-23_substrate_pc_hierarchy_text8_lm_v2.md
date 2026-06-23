# Pre-registration: substrate_pc_hierarchy_text8_lm_v2 (V2 bug-fix re-dispatch)

**Date:** 2026-06-23
**Anchor:** substrate_pc_hierarchy_text8_lm_v2
**Queue:** overnight_queue (GPU)
**N:** 8192, **Seeds:** [7, 17, 23], **PC layer depth grid:** {rank1-baseline, 2, 5}
**Predecessor cell:** experiments/exp_substrate_pc_hierarchy_text8_lm_v1.py
**Predecessor verdict:** HARD_FAIL smoke artifact (PC_2 == PC_5 to 4 decimals
because PC primitive was inert; sign(W @ in) at W=zeros -> all-ones outputs).

## Why a v2

v1 shipped as a **smoke artifact only** (laptop CPU; N_TRAIN=1500; never ran on
actual GPU at full scale) and contained a **single substantive bug** that made
the PC primitive completely inert: the per-layer W was zero-initialized, so
`sign(W @ input) = sign(0)` via `_safe_sign_t` saturated to +1 EVERYWHERE,
making the layer output the all-ones vector regardless of input. Every PC
layer behaved identically; recon_err stayed at 1.0 (random init); PC_2 and
PC_5 produced identical BPC.

## V2 bug fixed

### Bug 1 (PC primitive sign(0) saturation)

**v1 symptom:** `Ws = [torch.zeros((dim, dim), ...) for _ in range(n_layers)]`
followed by `layer_out = _safe_sign_t(layer_in_n @ Ws[li].T)`. With W=zeros,
the inner product is exactly zero -> sign(0) -> tied to +1 by `_safe_sign_t`.
EVERY layer produced the all-ones row; layer outputs were independent of
input.

**Fix:** each PC layer W initialized with variance-scaled Gaussian:
```
W = 0.01 * randn(N_DIM, N_DIM) / sqrt(N_DIM)
```
This is the substrate-native version of He / Xavier init; breaks the sign(0)
degeneracy while keeping initial activation magnitudes O(1) for unit-norm
inputs. The Hebbian additions still dominate over the random init within a
few hundred steps.

**Sanity test (T11):** at small dim_t11=128 and 2-layer stack:
- T11a: layer outputs must NOT be the all-ones row (v1 degeneracy signature)
- T11b: distinct inputs must produce >= 2 distinct layer-output rows
- T11c: recon_err_end must be finite (no NaN)

PASS at selftest.

### Secondary v1 bug fixed (recon_err_end NaN reporting)

v1's `recon_err_end_count` was 0 when `b >= n_pairs * 0.9` happened to skip
the final chunk (small n_pairs in selftest / smoke). v2 also includes the
final chunk regardless of the 10% threshold to avoid NaN reporting.

## Pre-registered bands (unchanged from v1)

**HARD-PASS:**
- ARM_PC_5_LAYER bpc_best < ARM_RANK1_HEBBIAN_NO_HIERARCHY bpc_best - 1.0 bits
- AND ARM_PC_5_LAYER bpc_best < 7.5 (beats unigram floor 7.738 by 0.24+ bits)
- AND ARM_PC_5_LAYER bpc_best CV across 3 seeds <= 0.10

**MIDDLE:** ARM_PC_5_LAYER beats rank-1 baseline (lift > 0) but does not meet
HP criteria.

**HARD-FAIL:** ARM_PC_2_LAYER bpc_best >= ARM_RANK1_HEBBIAN bpc_best AND
ARM_PC_5_LAYER bpc_best >= ARM_RANK1_HEBBIAN bpc_best.

## Smoke gate (executed locally 2026-06-23)

```
.venv/Scripts/python.exe experiments/exp_substrate_pc_hierarchy_text8_lm_v2.py --smoke
```
- N_DIM=1024 (smoke override; full uses 8192), N_TRAIN=1500, N_HELD=300, VOCAB_CAP=300
- 12 self-tests PASS (incl. new T11 PC-primitive non-degeneracy)
- Smoke verdict: HARD_FAIL (expected; at smoke scale with alpha/dim too small to
  converge in 1.5k tokens, PC arms produce ~same BPC as rank-1; full GPU is the
  decisive regime).
- Critical: PC_2 (bpc=7.801) is NOW DIFFERENT from PC_5 (bpc=7.976) -- the v1
  identical-to-4-decimals signature is gone. Mechanism is no longer inert.

## Sanity self-tests (T1-T12)

T1. char-trigram encoder bipolar
T2. _safe_sign_t (zero -> +1; nonzero sign preserved)
T3. Hebbian sign correct
T4. PC error decomposition
T5. rank1_hebbian_W shape + nonzero
T6. PC layer stack shape
T7. forward_pc_layers correct shape + finite logits
T8. zero-logits BPC near log2(V)
T9. unigram analytic max-class
T10. verdict bands HP / HF / MID
T11. **PC primitive non-degeneracy (Bug 1 fix)**: not-all-ones + distinct rows + finite recon
T12. LLM counter clean

## Timeout estimate

Same as v1: 21600s (6h) per PROT-019 N=8192 floor.

## Brain-existence-proof asymmetric calibration

Per USER 2026-06-23 (brain-as-existence-proof): the V2 fix is implementation
correctness, NOT a feasibility test. The decisive question is whether
multi-layer sign-based PC (now that it actually executes correctly) can lift
over rank-1 at full GPU scale. A HARD_FAIL here is informative (says
sign-based PC at N_DIM=8192 + alpha grid is the wrong combination) but NOT a
refutation of brain-as-existence-proof.

## Cites

- preregs/2026-06-23_substrate_pc_hierarchy_text8_lm_v2.md (this file)
- preregs/2026-06-23_substrate_pc_hierarchy_text8_lm_v1.md (predecessor)
- experiments/exp_substrate_pc_hierarchy_text8_lm_v2.py (this cell)
- experiments/exp_substrate_pc_hierarchy_text8_lm_v1.py (predecessor; smoke artifact)
- Skunkworks 4-bug audit 2026-06-23
- Diagnostic agent findings 2026-06-23
- USER 2026-06-23 (brain-as-existence-proof reframe; iterate fixes, don't pivot)
- USER 2026-06-22 (Fix #24 GPU dispatch must use GPU)

-- Exp-Dev
