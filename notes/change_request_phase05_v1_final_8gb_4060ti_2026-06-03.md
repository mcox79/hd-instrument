# CHANGE REQUEST FINAL — Phase 0.5 v1 on 4060 Ti 8GB; no cloud

**From:** Research session
**To:** Testbed
**Date:** 2026-06-03
**Subject:** Final Phase 0.5 v1 plan after confirming remote GPU is 4060 Ti 8GB. Cloud rung C deferred indefinitely. Add rung 0 (Pythia-160M debug). Rung A is the primary science result.

**Supersedes:**
- `change_request_phase05_v1_relaunch_with_algorithm1_2026-06-03.md` (Algorithm 1 spec — still applies)
- `change_request_phase05_v1_remote_gpu_not_cloud_2026-06-03.md` (assumed 24GB; corrected here)

---

## Status check requested

Before applying:
- [ ] Are user's 3 code bug fixes done? (NaN-check + BFloat16 cast + device placement)
- [ ] Has any Phase 0.5 v1 relaunch dispatch happened? (Expected: no)
- [ ] Is the 4060 Ti currently substrate-physics-only?

---

## 4060 Ti 8GB constraints

| Model | BF16 mem | INT8 mem | Fits on 8GB? | Coexists with substrate-physics (1-2GB)? |
|---|---|---|---|---|
| Pythia-160M | ~320MB | n/a | YES easy | YES easy |
| Llama-3.2-1B | ~4-5GB | n/a | YES comfortable | YES tight |
| Llama-3.2-3B | ~9GB | ~5-6GB | INT8 only | NO (need exclusive GPU window) |
| Llama-3.1-8B | ~21GB | ~13GB | NO (not feasible) | NO |

## Three-rung plan ($0)

### Rung 0 — Pythia-160M Algorithm 1 debug

**Anchor name:** `phase05_v1_algorithm1_debug_pythia160m_v1`

**Purpose:** validate Algorithm 1 embedding pipeline implementation on the smallest available model BEFORE escalating to Llama compute cycles. Per rung-1-2-first methodology applied to engineering complexity.

**Test:**
- Pythia-160M (12 layers); ~320MB BF16; runs alongside substrate-physics
- Implement Algorithm 1: k-means over Pythia layers 6-12 (= latter half, mirroring paper's layers 16-32 of 32) + sum-pool centroids k=5
- Train a small Hyperprobe-style MLP on the resulting embedding pipeline
- ~50-100 epochs; short training run
- Test corpus: small held-out validation set
- 3 seeds

**Pre-registered bands:**
- HP at rung 0: Algorithm 1 implementation runs cleanly (no NaN, no shape mismatches, no device errors) AND val_sim trajectory monotonically improves to ≥ 0.60 by epoch 100. Pure implementation correctness gate; not a product claim.
- MIDDLE: pipeline runs but val_sim flat or noisy; implementation has subtle bugs; iterate at rung 0 (cheap)
- HF: pipeline crashes OR val_sim degrades over training; major bug; do NOT escalate to rung A

**Wall:** ~30 min remote GPU
**Cost:** $0

**Strategic outcome:** if HP, Algorithm 1 implementation is debugged and ready for rung A escalation. If HF, fix at $0 cost before any Llama runs.

### Rung A — Llama-3.2-1B (PRIMARY science result)

**Anchor name:** `phase05_v1_llama32_1b_audit_relaunch_v1`

**Purpose:** primary science test — validate substrate audit primitives (κ_3 drift, deletion cert, refusal cert) on REAL-LLM residual streams. This rung is sufficient for the product capability claim "substrate audits real LLM residuals."

**Test:**
- Llama-3.2-1B (16 layers); ~4-5GB BF16; runs alongside substrate-physics with tight coordination
- Algorithm 1 pipeline (debugged at rung 0): k-means over Llama-3.2-1B layers 8-16 + sum-pool centroids k=5
- Train Hyperprobe MLP per paper spec: ~421 epochs target, early-stop patience 100, LR=3e-5, AdamW
- After Hyperprobe converges (val_sim hopefully ≥ 0.80), test the 3 audit primitives on the resulting bipolar substrate vectors:
  - κ_3 drift detection (substrate flags distributional shift in a held-out perturbed corpus)
  - Deletion certificate (rank-1 stored-matrix substitution preserves non-target retrievals at cos ≈ 1; per drill 1 + v341 audit)
  - Refusal certificate (substrate's refusal sub-cap on a held-out adversarial probe set)
- 3 seeds for Hyperprobe; per-audit-primitive 5-seed for cleaner signal
- Save checkpoints every 50 epochs for resume

**Pre-registered bands (Hyperprobe gate):**
- HP: val_sim ≥ 0.80 at 1B scale (relaxed from paper's 8B-specific 0.89; structurally a different scale-class)
- MIDDLE: val_sim 0.65-0.80
- HF: val_sim < 0.65 → Algorithm 1 has issues OR LLM-scale mismatch; surface for research re-examination

**Pre-registered bands (audit primitive gates — independent of Hyperprobe gate):**
- κ_3 drift: HP detects drift at σ_sep > 3.0 across 5 seeds on held-out perturbed probe set; HF at σ_sep < 1.0
- Deletion cert: HP cos ≥ 0.95 for non-target retrievals after rank-1 deletion (per v341 protocol applied to 1B-derived bipolar vectors); HF cos < 0.80
- Refusal cert: HP correct refusal classification ≥ 90% on held-out adversarial probes; HF < 70%

**Wall:** ~2-4h remote GPU
**Cost:** $0

**Strategic outcome:** if Hyperprobe HP + 3 audit primitives HP → "substrate audits real LLM residuals" capability claim FULLY VALIDATED at 1B scale. Product narrative defensible. Goal #1 achieved at $0.

### Rung B — Llama-3.2-3B INT8 (OPTIONAL strengthening)

**Anchor name:** `phase05_v1_llama32_3b_int8_audit_relaunch_v1`

**Purpose:** strengthen the claim with second LLM-size data point. INT8 quantization adds noise but a positive result still meaningful.

**Test:**
- Llama-3.2-3B INT8 quantized; ~5-6GB; requires PAUSING substrate-physics queue during run (combined memory too tight)
- Algorithm 1 pipeline applied to Llama-3.2-3B layers 14-28 (latter half)
- Same Hyperprobe + audit primitive sub-tests as rung A
- Conditional dispatch: ONLY if rung A HP AND user explicitly requests rung B

**Pre-registered bands (rung B):**
- HP: val_sim ≥ 0.78 at 3B INT8 (further relaxed for quantization noise)
- MIDDLE: 0.62-0.78
- HF: < 0.62

**Wall:** ~6-10h remote GPU (exclusive)
**Cost:** $0
**Substrate-physics impact:** queue paused for run duration; substrate-physics lost ~6-10 verdicts during the window. Tradeoff: strengthen LLM claim vs maintain substrate-physics cadence.

**Strategic outcome:** if HP, claim strengthens to "validated at 1B and 3B real LLM" — two-rung independent evidence.

### Rung C — Llama-3.1-8B paper-match. DEFERRED INDEFINITELY.

**Per `feedback_cloud_only_when_absolutely_necessary`:** 8B doesn't fit on 4060 Ti 8GB at any reasonable quantization. Cloud-only path. Costs ~$50 per attempt. **NOT dispatching** unless user explicitly authorizes for a specific paper-match strategic reason (investor demo, published benchmark, etc.).

Goal #1 ("audit primitives work on real-LLM residuals") doesn't require 8B. Achievable at rung A.

---

## Dispatch sequence

1. **Rung 0** dispatches IMMEDIATELY after user's bug fixes land + Algorithm 1 engineering complete (testbed: ~4-8h engineering, then dispatch). Runs alongside substrate-physics. $0, ~30 min wall.
2. **Rung A** dispatches IF rung 0 HP. ~2-4h wall, $0. Coordinate substrate-physics for tight memory window.
3. **Rung B** dispatches IF rung A HP AND user explicitly requests. Pauses substrate-physics. $0, ~6-10h.
4. **Rung C** does NOT dispatch.

---

## What this changes vs prior plan

| Item | Prior plan | This plan |
|---|---|---|
| Cloud spend | $50 overnight | $0 total |
| Rung 0 | n/a | Pythia-160M Algorithm 1 debug, ~30 min |
| Rung A | Llama-3.2-1B on assumed 24GB | Llama-3.2-1B on confirmed 8GB (still comfortable) |
| Rung B | Llama-3.2-3B BF16 | Llama-3.2-3B INT8 (BF16 doesn't fit) |
| Rung C | Llama-3.1-8B remote GPU then maybe cloud | DEFERRED indefinitely |
| Substrate-physics impact | minimal | minimal at rungs 0+A; paused during rung B |

---

## Discipline declarations

- Per `feedback_cloud_only_when_absolutely_necessary`: $0 plan; cloud reserved for absolute necessity
- Per `feedback_small_scale_first_methodology`: rung 0 Pythia debug before rung A Llama; ladder applies to engineering complexity too
- Per `feedback_change_request_protocol`: supersedes prior two Phase 0.5 v1 change-requests with corrected GPU spec
- Per `feedback_plain_language_experiment_tracking`: rungs described by what they test
- Per `feedback_no_padding_experiments`: each rung answers a specific question (engineering correctness / 1B science / 3B strengthening); rung C is genuinely optional and skipping it loses only paper-match
- Per `feedback_obey_user_pause_explicitly`: 8GB GPU spec user-confirmed; cloud reservation user-confirmed
- PROT-018: anchor names use rung-tier-prefix + descriptor + _v1 family

---

**END.**

**Testbed:** apply this plan as the FINAL Phase 0.5 v1 routing. Engineer Algorithm 1 (small enough scope to test at Pythia first). Dispatch rung 0 when ready. Surface rung 0 verdict; research escalates to rung A. Rung B + rung C decisions deferred to research after rung A.

**Research session:** holds for rung 0 verdict; synthesizes; sequences rung A.

**User:** Phase 0.5 v1 now $0 instead of $50. Same scientific result available at rung A. Paper-match reproduction deferred until/unless strategically needed.
