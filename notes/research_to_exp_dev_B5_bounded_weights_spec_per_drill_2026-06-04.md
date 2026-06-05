# Research -> Exp-Dev: B5 BOUNDED WEIGHTS spec (drill answer; revises earlier "accept negative")

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Source:** Minimal nonlinearity for replay-consolidation 2x drill landed 2026-06-04 (research_drill_minimal_nonlinearity_for_replay_consolidation_2x)

---

## Revision to earlier B5 recommendation

Earlier round-2 response said "ACCEPT NEGATIVE; research is drilling on minimal nonlinearity."

Drill landed. **Update:** Don't accept-negative. Try B5-BOUNDED-WEIGHTS first. **Cost: ONE clip() call.** Direct Lazaro 2025 lit precedent. ~5 min CPU. Worth the trivial engineering effort.

Specifically: my earlier hope that B2's sparse k-WTA might provide enough nonlinearity was wrong. SQHN 2024 (Nature Comms) shows sparse Hopfield is order-insensitive in online continual learning regime. The PRINCIPLED cheapest nonlinearity = bounded synaptic weights.

---

## Cell B5-bounded specification

### Architecture (add to existing B5 scaffold)

```python
# Existing B5 update (per palimpsest spec):
W = W * (1 - alpha)              # palimpsest decay alpha=0.003
W += x_i * x_j^T                 # Hebbian write

# NEW: add bounded-weights clip after Hebbian write:
W = clip(W, [-W_max, W_max])     # bounded weights
```

That's it. One additional clip() call. Tuning parameter W_max.

### W_max tuning recipe (per drill)

Critical saturation threshold: **eta * N * f^2 / W_max > 0.1** for order-dependence to be significant.

For N=2048, f=0.02 (B2 sparse), typical eta (Hebbian update magnitude per pattern) ~ 1:
- Saturation regime: W_max < 8.2 * eta
- Recommended W_max = 4-8 (well within saturation regime)
- Test multiple values: W_max in {4, 6, 8, 12} (vary nonlinearity strength)

### Sub-cells

- **5-bounded-a:** No bounding (baseline; reproduces earlier B5 HF as sanity check)
- **5-bounded-b:** W_max = 4 (strong saturation regime)
- **5-bounded-c:** W_max = 8 (medium saturation regime)
- **5-bounded-d:** W_max = 12 (weak saturation regime)

For each sub-cell:
- None / random replay / STDP-ordered (recent-first) replay
- 3 seeds; M = 50 patterns (low load per drill recommendation)
- 10% replay time budget

### Pre-reg HP/MID/HF

- **HARD-PASS:** ordered-recent-first replay retention >= 1.3x no-replay retention at W_max in saturation regime (W_max in {4, 6, 8}) AND ordered > random by >= 2-sigma
- **MIDDLE:** ordered > random + ordered > no-replay by 1.1-1.3x at some W_max
- **HARD-FAIL:** ordered <= random across all W_max values (in saturation regime; verified via energy check)

### WHY-DRILL on HF

1. Verify saturation actually happening: measure fraction of W elements at W_max boundary; should be 10%+ during replay phase. If < 5%: W_max too high; reduce.
2. Verify replay-order encoding: random vs ordered should differ in temporal trajectory of W changes. Check ||delta_W_random - delta_W_ordered|| over replay sequence; should grow with time.
3. If both check out but still HF: escalate to dreaming-phase (Cell B5-dreaming; ~6-8h engineering with sleep/wake alternation).

---

## Why this is worth the small effort

**P_deflated = 0.45 for HP** (B2+bounded-W composition; ordered >= 1.3x vs no-replay)
**P_deflated = 0.20 for HP via B2 k-WTA alone** (low; SQHN 2024 contradicts naive hope)

**Engineering cost:** ~30 min (add clip(); test W_max values)
**Wall:** ~5 min CPU per sub-cell × 4 sub-cells × 3 seeds = ~60 measurements ≈ 10-15 min total

**Lit precedent:** Lazaro et al. 2025 arxiv:2603.09384 "Dreaming improves memorization in a Hopfield model with bounded synaptic strength" -- demonstrates EXACTLY this mechanism in published 2025 work.

---

## Compose with B2 sparse architecture

Test on B2 SPARSE patterns (f=0.02), not dense baseline. Per drill: bounded-W effect compounds with sparse architecture because:
- Sparse patterns create fewer per-step weight changes (less aggressive saturation pressure)
- Saturation reaches specific high-frequency-feature synapses preferentially
- Replay order matters more when saturation is selective

If B5-bounded HP on B2 sparse architecture: this is the FIRST validation of replay-consolidation at substrate-class scale + composition with sparse coding.

---

## What this changes about Stage A trick stack

Earlier round-2 trick stack dropped B5 (HF in linear regime). With B5-bounded HP path validated:

**ADD to Stage A trick stack:**
- B5-bounded (W_max ~ 6) with ordered-recent-first replay
- Composes with B2 sparse architecture for highest predicted effect
- Provides Tier 2 hippocampal-replay primitive (per bio-tier-scaling drill)

This unlocks the Tier 2 transition empirically.

---

## What this is NOT

- NOT the dreaming-phase escalation (that's Cell B5-dreaming; ~6-8h engineering; later)
- NOT a replacement for B2 + B6 + B4 + B3 primitives (those still HP independently)
- NOT a cloud test ($0 CPU)
- NOT urgent (current empirical pipeline + Phase 0.5 v1 Llama have higher priority)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF with multiple W_max sub-cells
- Per [[feedback-no-padding-experiments]]: sub-cells discriminate saturation regime
- Per [[feedback-pressure-test-negative-findings]]: revised earlier "accept-negative" based on drill landing; WHY-DRILL has 3 specific fix paths
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-change-request-protocol]]: revises earlier B5 acceptance
- ASCII-only

PROT-018: anchor uses `_b5_bounded_v1`
PROT-021: source=local CPU, run_mode=smoke, n_seeds=3

---

**END.**

**Exp-Dev:** ~30 min engineering (single clip() addition + tuning loop) + ~10-15 min CPU wall for 4 sub-cells × 3 seeds. P_deflated=0.45 for HP. Compose with B2 sparse architecture for highest effect.

Lower-priority than current composition tests (B36 + B26 + pure-bio combined), but cheap enough to dispatch whenever there's bandwidth.

**Research session:** B3b regularization drill still in flight (~10-20 min remaining); will inform additional optimization recommendations when lands.
