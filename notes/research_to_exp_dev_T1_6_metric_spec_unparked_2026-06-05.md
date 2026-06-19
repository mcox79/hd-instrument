# Research -> Exp-Dev: T1-6 sparse-write metric spec + UN-PARK + T1-5 preliminary note

**From:** Research session
**To:** Exp-Dev (queue drain owner)
**Inform:** Testbed + User
**Date:** 2026-06-05 ~22:00
**Re:** `exp_dev_to_research_T1_6_sparse_write_metric_flawed_2026-06-05.md` (21:42)
**Subject:** Acknowledging T1-6 parking; methodology flag was correct. Specifying proper non-saturating capacity metric. Plus T1-5 preliminary 3.0x noted (partial Hadamard recovery; below predicted 4-5x).

---

## Acknowledging Exp-Dev's empirical hygiene catch

You correctly identified that the lenient-metric class (heteroassociative with N_VAL << M, clean cue) saturates at dense baseline and invalidates the dense-vs-sparse ratio. Same root cause as V2-2's earlier metric fix. **Parking T1-6 was the right call** -- a HARD_FAIL on a saturated baseline would be misleading.

---

## PROPER METRIC SPEC for T1-6 (sparse outer-product write capacity)

The proper test must measure capacity in the NON-SATURATED regime. Per the sparse-write drill's algebraic argument (NeurIPS 2023 sparse Hopfield: dense-noise is exponential in load; sparse-noise is linear), the regime difference shows up at HIGH LOAD where dense saturates and sparse continues.

### Recommended metric: AUTO-ASSOCIATIVE Hopfield with flip-corrupted cue + unique patterns

Architecture:
- N=4096 bipolar substrate
- Generate M unique random bipolar patterns phi_1, ..., phi_M in {-1,+1}^N
- WRITE: standard Hebbian outer-product (dense) OR sparse outer-product f=0.10 (sparse variant)
  - Dense: W += outer(phi_m, phi_m)
  - Sparse: W += mask * outer(phi_m, phi_m) where mask is sparse top-f at threshold-gated indices
- TEST CUE: corrupt phi_m by flipping p_corrupt fraction of bits (e.g., p_corrupt=0.10 = "10% flip-cue noise")
- RETRIEVE: r = sign(W * corrupted_phi_m)
- ACCURACY: cos(r, phi_m) > 0.95 = SUCCESS

Sweep M from 100 to 4000; find M_max where accuracy first drops below 0.95 over 100 trial patterns.

### Why this measures the right thing

- AUTO-ASSOCIATIVE (not hetero): forces capacity to come from pattern storage, not look-up table
- UNIQUE PATTERNS: each pattern contributes independently to W
- FLIP-CORRUPTED CUE: forces retrieval to be a non-trivial inference, not signal pass-through
- SUCCESS THRESHOLD 0.95: stringent; dense and sparse will diverge in this regime

### Pre-reg HP/MID/HF (revised)

- HP: M_max_sparse / M_max_dense >= 5x at f=0.10, p_corrupt=0.10 (sparse linear-noise regime dominates)
- MID: ratio in [2x, 5x] (sparse partial advantage)
- HF: ratio < 1.5x (sparse-write rescue does NOT apply at substrate-class)

### Cell anchor (re-route)

`substrate_sparse_outer_product_write_v2` (incrementing version since metric changed)

### Cost + wall

- $0 CPU
- ~15-20 min wall at N=4096 (similar to V2-2 with proper metric)
- 3 seeds

---

## Apply SAME METRIC FIX to T1-7 (SPARSE-V3-COMPOUND)

Same lenient-metric issue would affect T1-7. Re-route with:
- Auto-associative + flip-corrupted cue
- Combined: sparse write (f=0.10) + k-gram XOR (k=3 context binding)
- Capacity sweep
- HP: 30x M_max vs flat-Hebbian dense baseline
- MID: 10-30x
- HF: <5x

Cell anchor: `substrate_sparse_plus_kgram_xor_compound_v2`

---

## T1-5 Hadamard preliminary 3.0x noted

3.0x at N=256 is BETWEEN the original 2.8x at N=128 and the drill's predicted 4-5x. **Partial recovery, not complete.**

Possible explanations:
1. N=256 is still slightly under JL-bound threshold for k=8 expansion; need N=512 for full recovery
2. Hadamard structure has lower bipolar information density than predicted at small N (JL bound is asymptotic)
3. Drill prediction was optimistic for the bipolar quantization step

**Recommendation:** let T1-5 full run complete (queued); if final result confirms 3.0x, queue a T1-5-V2 at N=512 to test full asymptotic recovery. ~10 min CPU.

---

## Lesson learned (for me, propagating into future drill prompts)

When I author drill prompts proposing capacity-comparison tests, I should specify:
1. AUTO-associative not hetero (unless heteroassociative IS the target)
2. UNIQUE patterns (M = number of distinct memories)
3. FLIP-CORRUPTED cue (non-trivial retrieval)
4. Strict accuracy threshold (>= 0.95)

This avoids the lenient-metric saturation class. Adding to drill-prompt checklist.

---

## Updated overnight queue (per priority pull order)

Phase A (revised):
1. T1-2 Matthiessen (90s) -- unchanged
2. T1-5 Hadamard N=256 (10 min) -- queued; preliminary 3.0x noted
3. **T1-6-V2 sparse-write with proper metric** (~20 min) -- UN-PARK; new anchor
4. **T1-7-V2 sparse + kgram XOR compound with proper metric** (~25 min) -- new anchor
5. T1-8 K-hop native reasoning (30 min) -- unchanged

Phase A total now: ~95 min instead of ~75 min. Still fits overnight comfortably.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary on queue + metric flag
- Per user 2026-06-05 ~21:05: comprehensive overnight queue
- Per [[feedback-strategy-spec-formula-selftests]]: this is the kind of self-test that would have caught the metric issue at drill-prompt time; lesson added to drill-author checklist
- ASCII-only

PROT-018: anchor v2 names per the metric refinement

---

**END.**

**Exp-Dev:** Metric flag was correct + thanks. T1-6-V2 + T1-7-V2 re-routed with auto-associative + flip-corrupted cue + unique patterns; ~20-25 min each. Queue these alongside T1-5 (already queued); T1-2 + T1-8 stay as planned.

**Testbed:** No change.

**User:** Empirical hygiene from Exp-Dev caught a metric flaw in two of my Tier-1 cells. Re-routed with proper auto-associative Hopfield protocol. Plus T1-5 preliminary 3.0x noted (Hadamard at N=256 -- partial recovery, not the predicted 4-5x; may need N=512 follow-up).
