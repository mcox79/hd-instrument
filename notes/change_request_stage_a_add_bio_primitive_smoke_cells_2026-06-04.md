# Change Request -- Stage A smoke sweep: add bio-primitive cells (one-shot + DG sparse + active gating + column ensemble + replay)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** Add 5 bio-architectural primitive smoke cells to Stage A sweep, alongside the N-crossover sweep. Per user strategic direction: substrate is intrinsically different from existing frameworks; biology gives 10^4-10^6x speedup ceiling, not 24x.

---

## Strategic context

User direction 2026-06-04: substrate is INTRINSICALLY DIFFERENT from existing-framework hybrids. The 24x conservative estimate anchored to PUBLISHED industrial training-trick speedups (DeltaNet + MoE + ZeRO++). Biology achieves 10^4-10^6x compute efficiency. Substrate should be tested as PURE bio-architecture, not framework-bounded hybrid.

Three 3x drills now in flight characterizing the bio-architecture ceiling + per-primitive test designs + tier-scaling principles. This change-request adds the empirical SMOKE TESTS for each bio-primitive at substrate-class N=2048 to run NOW (cheap; fast iteration).

---

## What this adds to existing Stage A smoke sweep

Existing change-request `change_request_stage_a_smoke_sweep_crossover_N_v1` shipped 10 smoke cells (N-crossover sweep).

This change-request ADDS 5 bio-primitive smoke cells at substrate-class N=2048 (the optimal capacity-realized scale per the existing sweep predictions):

### Bio-primitive smoke cells

**Cell B1: One-shot Hebbian retrieval baseline**

- N=2048; V=70 char-LM bigram contexts
- Store K=10 examples per class via SINGLE Hebbian outer-product write each (50 total writes; 5 classes)
- Test held-out per-class retrieval accuracy
- Compare to Adam-trained linear classifier needing ~1000 steps
- Metric: accuracy at single write + wall-time speedup
- **HP:** substrate accuracy >= 80% AND speedup >= 100x vs Adam baseline
- **MID:** accuracy 60-80% OR speedup 10-100x
- **HF:** accuracy < 60% OR speedup < 10x

**Cell B2: DG-class f=0.005 sparse + 20x expansion**

- Input dim 1000; expand 20x to N=20000 (substrate-class extended)
- Sparse f=0.005 binary representation
- Hebbian write at expanded sparse representation
- Compare to dense f=1.0 at N=2048
- Metric: capacity gain at same retrieval accuracy
- **HP:** 100x capacity gain at same accuracy
- **MID:** 10-100x
- **HF:** < 10x

**Cell B3: cf-RPE active gating (selective training set)**

- N=2048; V=70 char-LM
- 3 sub-cells: write every example (baseline) / write at top-10% prediction error / write at top-1% prediction error
- Metric: BPC convergence + wall-time speedup
- **HP:** Cell B3-1% achieves same BPC as B3-baseline at 1/100 wall-time
- **MID:** speedup 5-100x
- **HF:** speedup < 5x

**Cell B4: 10-column ensemble (cortical column parallelism)**

- 10 parallel substrates at N=2048 each
- Trained on different corpus subsets
- Majority vote at retrieval
- Compare to single substrate at N=20480 (equivalent total dimension)
- **HP:** ensembled achieves same accuracy at 10x faster wall-time
- **MID:** 2-10x speedup
- **HF:** < 2x speedup

**Cell B5: STDP-replay consolidation between batches**

- N=2048; Wikitext-2 char-LM
- 3 sub-cells: Hebbian write only / Hebbian + 10% time STDP replay / Hebbian + 50% time STDP replay
- Metric: retention + generalization improvement
- **HP:** replay cells achieve 1.5x+ improvement vs no-replay
- **MID:** 1.2-1.5x
- **HF:** < 1.2x

---

## Aggregate smoke sweep design (existing + new)

Combined smoke sweep:
- N-crossover sweep (S1-S10; existing): 10 cells x 30-60s = ~10-15 min
- Bio-primitive sweep (B1-B5; this CR): 5 cells x 30-90s = ~5-10 min
- **Total: 15 cells; ~15-25 min CPU; $0**

Each cell SHORT enough to iterate fast. Aggregate verdict identifies BOTH crossover N AND working bio-primitives in single pass.

## Pre-reg discipline

Per [[feedback-no-smoke-preframing-in-task-prompts]] + [[feedback-no-preframe-batch-all-pass]]:
- Each cell has explicit HP/MID/HF
- NO implicit PASS expectation
- HF triggers WHY-drill per [[feedback-pressure-test-negative-findings]]:
  - Why didn't this bio-primitive give predicted speedup?
  - Is the failure mode operating-condition-specific?
  - What alternate test would isolate the issue?

## Resource

Local CPU only.

## Cost ceiling

$0 CPU. ~15-25 min total wall for full combined sweep (existing + new).

## P_deflated per cell (per today's methodology)

| Cell | P_algebraic | P_implementation | P_joint HP |
|---|---|---|---|
| B1 one-shot | 0.85 | 0.55 | 0.47 |
| B2 DG sparse | 0.75 | 0.45 | 0.34 |
| B3 active gating | 0.65 | 0.50 | 0.33 |
| B4 column ensemble | 0.70 | 0.55 | 0.39 |
| B5 STDP replay | 0.60 | 0.50 | 0.30 |

P_joint averaged across primitives: ~0.37 for at least one HP. Likely 2-3 of 5 will HP at substrate-class scale.

## Strategic outcome

### If 3+ bio-primitives HP (most likely; per today's methodology)

- Substrate-pure-biology-architecture empirically validated at substrate-class scale
- Documented working bio-primitives become Stage A baseline trick set
- Move to Pythia-160M scale (Stage B) with these validated tricks

### If 1-2 bio-primitives HP

- Partial validation; identify which primitive(s) work
- Drill on WHY others didn't work (per pressure-test methodology)
- Iterate bio-primitive integration before Stage B

### If 0 bio-primitives HP

- Substrate's bio-primitive integration as currently configured doesn't deliver
- Substantial reassessment needed
- Drill on architectural compatibility issues

## Engineering scope

~3-4h additional (beyond existing Stage A smoke scaffolds):
- One-shot test harness (~30 min; just remove iteration loop)
- DG expansion + sparsify (~1h; new sparse-encoding step)
- Active gating threshold logic (~30 min; add prediction-error gate)
- Column ensemble (~1h; reuse 5-corpus hierarchical scaffold; 10 parallel)
- STDP replay phase (~1h; STDP-asymmetric replay loop)

Reuses Bundle A + Bundle E + 5-corpus scaffolds substantially.

---

## What this is NOT

- NOT a replacement for the N-crossover sweep (BOTH run together; complementary signals)
- NOT a full Stage A run (still ~5 min smoke per cell; not multi-hour training)
- NOT cloud (all $0 CPU)
- NOT pre-framed as HP (each cell explicit pre-reg; HF likely for some)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per cell
- Per [[feedback-no-preframe-batch-all-pass]]: no implicit PASS expectation
- Per [[feedback-pressure-test-negative-findings]]: HF triggers WHY-drill before iteration
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

PROT-018: anchors use `_bio_smoke_v1` suffix
PROT-021: source=local CPU, run_mode=smoke, n_seeds=3

---

**END.**

**Exp-Dev:** add 5 bio-primitive smoke cells to existing N-crossover sweep. ~3-4h additional engineering + ~5-10 min additional CPU wall. Verdict drives bio-pure-architecture validation at substrate-class scale + Stage B trick set selection.

**Research session:** holds for combined smoke sweep verdict + 3 new bio-architecture 3x drills landing; revises Stage A full run based on working bio-primitive set.
