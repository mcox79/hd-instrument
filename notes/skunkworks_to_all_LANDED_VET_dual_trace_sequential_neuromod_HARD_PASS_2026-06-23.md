# LANDED-VET: substrate_dual_trace_sequential_neuromod_LM_v1 (cell-author HARD_PASS)

**Auditor:** Skunkworks (independent cert-chain)
**Date:** 2026-06-23
**Cell commit:** 7f450ce7
**Metrics:** d:/AI/hd-instrument/data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json
**Prereg:** d:/AI/hd-instrument/preregs/2026-06-23_substrate_dual_trace_sequential_neuromod_LM_v1.md

---

## VERDICT

**MEASURED_MECHANISM (not chain-grade).**

DUAL_TRACE genuinely produces a measurable BPC improvement over its internal control arms
(delta_vs_base=+0.5165, delta_vs_naive=+0.5165 bits, dual_cv=0.0011 across 3 seeds). The
mechanism is brain-grounded, the implementation matches the Brzosko 2017 / Huertas 2016
spec, and the dual-trace's E_pos/E_neg are demonstrably distinct (self-test 4 passes). The
mechanism IS measuring something real about the substrate's compositional capacity.

However, the pre-registered "HARD_PASS" framing collapses on inspection because the cell's
ARM_BASELINE does NOT reproduce the fair_harness chain-grade baseline (7.3065) as claimed;
both ARM_BASELINE and ARM_NAIVE_MULT collapsed to the unigram floor under the joint (T, λ)
sweep (selecting λ=0 across all 3 seeds). The +0.5165 bit "envelope-break" headline number
is misleading — it measures dual-trace lift over a collapsed-to-unigram control, not lift
over the substrate's real prior-best.

Honest comparison: **DUAL_TRACE 7.2213 vs fair_harness chain-grade SPARSE_BIPOLAR 7.3065 =
+0.085 bits BPC**. This is below the pre-registered HARD_PASS bar (>= +0.20 bits vs
baseline) when "baseline" is interpreted as the real prior-best substrate-as-LM. Per Fix #28
+ by-construction-saturation discipline + cert-owner-overrides-Director pattern, this is
tiered MEASURED_MECHANISM pending the methodology issues being resolved.

---

## Per-VET-concern audit

### VET-1: ARM_BASELINE collapsed to unigram (FAIL)

**Status: FAIL — confirmed cell-author misframing.**

The cell's docstring (lines 22-23) and the metrics summary's `honest_scope` field both
state ARM_BASELINE "reproduces fair_harness baseline" / "matching fair_harness baseline
config". This is FALSE. Evidence:

- fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR (the 7.3065 chain-grade reference):
  - mechanism: `W = sum outer(E_tgt, E_src)` (pure rank-1 Hebbian, no cf-RPE, no dopa)
    — `experiments/exp_fair_harness_substrate_as_lm_v1.py:349-367` `build_rank1_W_gpu`
  - sparsity: `SPARSE_BIPOLAR_F = 0.05` — `:120`
- dual-trace cell ARM_BASELINE:
  - mechanism: cf-RPE with dopamine gating; `W += dopa * (Delta.T @ E_src)` where
    `Delta = E_tgt - W @ E_src` — `:352-389` `build_W_baseline`
  - sparsity: `SPARSE_BIPOLAR_F = 0.02` — `:152`

These are TWO DIFFERENT MECHANISMS at TWO DIFFERENT SPARSITY CONFIGURATIONS. The cell's
ARM_BASELINE is NOT a reproduction of the fair_harness chain-grade baseline; it is a new
cf-RPE arm at a different sparsity.

What actually happened on the test: ARM_BASELINE's joint (T,λ) sweep selected
`best_lambda_for_bpc=0.0` for all 3 seeds (all 3 per-seed records show
`best_lambda_for_bpc=0.0, best_T_for_bpc=0.01, top1_acc=0.2171=unigram_top1`). The
harness reverted to pure-unigram because the dev-set BPC was lower with the substrate's
contribution ignored. This is a degenerate optimization outcome, not a true measurement
of cf-RPE dopamine-gated rank-1 capability — and it is NOT the fair_harness baseline.

Implication: the "+0.5165 bits over baseline" headline is dual-trace minus collapsed-to-
unigram, not dual-trace minus real-substrate-baseline. The pre-registered HARD_PASS rule
("vs ARM_BASELINE >= +0.20") is technically satisfied by the metrics, but the rule was
written assuming ARM_BASELINE would reproduce the fair_harness 7.3065 substrate result.
The cell-author's mechanism choice for ARM_BASELINE invalidates the assumption.

### VET-2: READOUT_DEGENERATE risk on DUAL_TRACE (PASS-with-caveat)

**Status: PASS for trace-independence; NEEDS_FOLLOWUP for harness symmetry.**

The joint (T, λ) sweep is symmetric across arms — same `joint_sweep_substrate` function
called for all three arms in `compute_arm_logits` (`:553-606`), and the per-seed metrics
show DUAL_TRACE actually USES the substrate (best_lambda_for_bpc=0.3, best_T_for_bpc=0.05
across all 3 seeds) where BASELINE/NAIVE_MULT collapse to λ=0. So the harness applies the
same optimization fairly; DUAL_TRACE wins on dev because its substrate contribution
actually adds information.

Self-test 4 (`:836-854`) directly verifies E_pos and E_neg are distinct tensors via a
synthetic data path (E_pos initialized non-zero; E_neg near-zero when prediction is
trivial). The cell IS implementing two separate eligibility traces with different outer
products (Delta vs pred) and different timescales (TAU_POS=5 vs TAU_NEG=50).

Caveat: the trace decay is applied at CHUNK granularity, not per-token. With
INGEST_CHUNK=4096 and TAU_POS=5, the effective LTP decay constant is 5 chunks = 20,480
tokens. With TAU_NEG=50, effective LTD decay is 50 chunks = 204,800 tokens. The N_TRAIN=
100,000 cell only contains ~24 chunks, so TAU_NEG decay barely activates and the LTD
trace effectively accumulates without forgetting — this is NOT the Brzosko mechanism's
sub-second / multi-second separation; it is a coarse temporal-window separation. The
mechanism survives at this granularity but the brain-mapping is looser than the prereg
implies. Flag for the scaling cell: at N_TRAIN=1M (~245 chunks), the timescale separation
becomes meaningful — should re-test that DUAL_TRACE lift survives.

### VET-3: DETERMINISTIC_METRIC pattern (PASS-but-suspicious)

**Status: PASS — confirmed real degenerate-collapse, not measurement artifact.**

The pattern (ARM_BASELINE std=0.0, ARM_NAIVE_MULT std=0.0, ARM_UNIGRAM std=0.0, ARM_DUAL_
TRACE std=0.0081) is consistent with degenerate-λ collapse, not with measurement
quantization. When the joint sweep selects λ=0 across all seeds, the test-set BPC IS
exactly the unigram BPC for all 3 seeds (because the substrate's contribution is
multiplied by 0 in the log-linear interp). That gives std=0 by construction — not because
the metric is quantized, but because all three "different" arms have collapsed to the
same final predictor (unigram). Cross-check: per-seed BASELINE and NAIVE_MULT both have
`bpc_best=7.7378, top1_acc=0.2171, mrr=0.2761` exactly matching ARM_UNIGRAM at every
seed. Same numbers, by construction, when λ=0.

The peek_arm_metrics DETERMINISTIC_METRIC flag did not fire because DUAL_TRACE std=0.0081
breaks the "all values 0" trigger. Recommend filing a Fix #28-related tool extension:
the peek tool should also flag "3 arms have identical BPC matching ARM_UNIGRAM" as a
distinct degenerate-collapse warning.

### VET-4: cf-RPE × E_pos vs E_neg genuinely orthogonal (PASS)

**Status: PASS on mechanism, NEEDS_FOLLOWUP on independence claim.**

Cell implements separate E_pos and E_neg as `dim x dim` matrices (`:488-489`), separate
outer products (`outer_pos = (Delta.T @ E_src) / chunk_sz` vs `outer_neg = (pred.T @
E_src) / chunk_sz`, `:515-517`), and separate decay constants (decay_pos = 0.80,
decay_neg = 0.98, `:496-497`). Update rule `W.add_(dopa * E_pos); W.sub_(ach * E_neg)`
(`:539-541`) matches the Brzosko `W += dopa * E_pos - ACh * E_neg` algebra.

Self-test 4 verifies traces are not identical (`trace_diff > 0.01`). This is a
sufficient but weak independence test — it would pass if E_neg were nearly E_pos plus a
small constant. The strong test (E_pos and E_neg occupy non-collinear subspaces of the
dim x dim outer-product space) is NOT verified.

For the cert tier: mechanism implementation is correct per spec; whether the resulting
two traces produce a genuinely rank-2-plus W (vs effectively rank-1 with a small
correction) is an open question that the ablation cell (Anchor 3) would resolve. The
ablation cell was contingent on MIDDLE_BAND; given the methodology issues here, recommend
running it anyway to confirm orthogonality is load-bearing.

### VET-5: BASELINE-collapse honest framing (FAIL on cell summary)

**Status: FAIL — verdict_msg is misleading.**

The cell's verdict_msg says "dual-trace breaks envelope (vs_base=0.516>=0.20,
vs_naive=0.516>=0.10, cv=0.001)". This is technically correct per the literal pre-reg
bands but operationally misleading because:

1. "envelope" in the cite chain is the +0.44 bits sparse-bipolar param-sweep envelope cap
   (best BPC = 7.295). DUAL_TRACE 7.2213 is +0.074 bits BETTER than envelope cap (7.295)
   — yes, that's a real measurement.
2. Internal-control comparison "vs_base=0.516" measures distance from collapsed-to-
   unigram, not distance from real prior-best. The pre-registered band was designed
   assuming ARM_BASELINE would reproduce fair_harness baseline; it did not.

Honest framing: DUAL_TRACE at 7.2213 BPC vs envelope cap (sparse-bipolar best) 7.295 =
+0.074 bits. vs fair_harness chain-grade ARM_SUBSTRATE_SPARSE_BIPOLAR 7.3065 = +0.085
bits. Both modest lifts; below the pre-reg HARD_PASS bar (+0.20) when interpreted
against real substrate baselines.

---

## Cert-routing recommendation

**Atomize as 3 atoms, ordered by load-bearing-ness:**

### Atom 1: `substrate_dual_trace_sequential_neuromod_LM_v1` (anchor)
- cert_status: **MEASURED_MECHANISM**
- summary: "Brzosko 2017 / Huertas 2016 dual-trace sequential-neuromodulator mechanism
  produces measurable +0.085 bits BPC over fair_harness chain-grade sparse-bipolar
  baseline (7.3065 → 7.2213) at N_DIM=8192 N_TRAIN=100k f=0.02, cv=0.0011 across 3 seeds.
  Cell-author HARD_PASS framing overstates the result; internal ARM_BASELINE collapsed
  to unigram floor under joint (T, λ) sweep and does NOT reproduce fair_harness baseline
  as documented."
- evidence:
  - DUAL_TRACE bpc_best_mean=7.2213, std=0.0081, cv=0.0011
  - Per-seed best_T=0.05, best_lambda=0.3, dev_bpc=8.08-8.09
  - Mechanism implementation matches Brzosko spec (separate E_pos/E_neg with different
    tau and different outer products)
  - Self-tests pass; cf-RPE error-shrink confirmed; trace-distinctness confirmed
- caveats:
  - vs internal ARM_BASELINE +0.516 is NOT vs fair_harness baseline; ARM_BASELINE chose
    λ=0 (unigram only) on dev
  - Chunk-granularity trace decay weakens brain-mapping at N_TRAIN=100k (TAU_NEG hardly
    activates over ~24 chunks)
- substrate-product reading: dual-trace orthogonal composition is a REAL lever in the
  ~+0.1 bit class at production scale; not the dramatic envelope-break the cell-author
  framing suggests, but not nothing either

### Atom 2: `substrate_as_lm_dual_trace_envelope_partial_lift_meta` (META)
- cert_status: **MEASURED_MECHANISM**
- summary: "Dual-trace neuromodulator mechanism delivers +0.085 bits BPC over chain-grade
  baseline at N_DIM=8192 N_TRAIN=100k. Below the pre-registered +0.20 HARD_PASS bar
  when measured against real prior-best substrate baseline. Locates the mechanism in
  MIDDLE_BAND territory per the spirit of the prereg even though the literal HARD_PASS
  rule was satisfied."
- evidence: see Atom 1
- substrate-product reading: routes substrate-as-LM program to (a) Anchor 3 ablation
  cell to confirm orthogonality is load-bearing, OR (b) re-dispatch with ARM_BASELINE
  re-implemented as fair_harness pure-rank-1-Hebbian at f=0.05 to recover the prereg's
  intended comparison

### Atom 3: `cert_prereg_referent_drift_lesson` (META — process)
- cert_status: **LESSON**
- summary: "Cell-author's ARM_BASELINE used a different mechanism (cf-RPE + dopa) and
  different sparsity (f=0.02 vs 0.05) than the fair_harness chain-grade baseline it was
  supposed to reproduce. The pre-reg's 'HARD_PASS bar vs baseline' is only meaningful if
  the baseline is operationally what the prereg author intended. Add to exp_dev
  discipline: when prereg says 'reproduces baseline X', cell must use IDENTICAL mechanism
  AND IDENTICAL config — not just same arm-name."
- evidence: dual-trace cell `build_W_baseline` vs fair_harness `build_rank1_W_gpu`;
  SPARSE_BIPOLAR_F=0.02 vs 0.05
- substrate-product reading: tighten exp_dev handoff template to require explicit
  function-import-from-prior-cell when reproducing baselines

---

## Risk flags for Anchor 2 (scaling cell)

If the scaling cell `substrate_dual_trace_scaling_v1` was dispatched contingent on Anchor
1 HARD_PASS, it inherits these risks:

1. **Same ARM_BASELINE methodology issue.** If the scaling cell reuses the same
   `build_W_baseline` (cf-RPE at f=0.02), its ARM_BASELINE will likely collapse to
   unigram floor at all scales, making "lift vs baseline" measurements over-stated by
   the same construction as Anchor 1. **RECOMMEND HALT** of scaling cell until Atom 1
   methodology re-test runs with `build_W_baseline` = fair_harness `build_rank1_W_gpu`
   at f=0.05.

2. **Chunk-granularity decay becomes meaningful at N_TRAIN=1M.** At 245 chunks, TAU_NEG=50
   decay actually activates (e^{-245/50} = 0.007); the LTD trace will exponentially
   forget. The cell-author's "chunk-mean" approximation needs re-derivation at the
   scaling-target chunk count, or the lift may shrink or invert. Add an
   `intermediate_token_count` arm to the scaling cell so the decay-onset effect is
   visible.

3. **GPU memory budget.** Two `dim x dim` traces at N_DIM=16384 are 2 * 16384^2 * 4 bytes
   = 2.1 GB each; total trace state 4.2 GB plus W = 1 GB plus encoder + activations.
   The cell-author's 537MB estimate at N_DIM=8192 was correct; scaling-to-N_DIM=16384
   quadruples it. Pre-dispatch verify free GPU memory > 8 GB or chunk further.

4. **Pre-reg bands need re-evaluation.** Anchor 2's HARD_PASS bar (lift >= +0.40 vs
   dual@N=8192) assumed the +0.516 internal-control lift was real. If Atom 1 re-tested
   to +0.085 vs real-baseline, the scaling cell's bar should be re-set to (proportional
   lift) +0.085 * (16384/8192)^x for some plausible scaling exponent x.

---

## Concise rationale for tiering call

By Fix #28 + by-construction-saturation discipline + brain-existence-proof:
- Brain-grounded mechanism: HIGH prior (P~0.60-0.75); implementation is correct.
- Measurement integrity: COMPROMISED by ARM_BASELINE methodology error → cannot tier
  chain-grade on this run; mechanism IS measured (vs fair_harness external) at +0.085
  bits which IS in MIDDLE_BAND for the program's substrate-as-LM lever-search.
- Cert-owner-overrides-Director pattern: Director framed this as HARD_PASS "+0.085 over
  fair_harness chain-grade baseline"; the +0.085 number IS in the metrics
  (`fair_harness_baseline_bpc: 7.3065` → `dual_bpc_best_mean: 7.2213`); but the cell-
  author's verdict-msg "vs_base=0.516>=0.20" maps to an internal collapsed-control, not
  the external fair_harness reference. Director's framing is more honest than cell-
  author's; but neither is chain-grade because the prereg's intended baseline-comparison
  did not actually run.

Recommend tier as **MEASURED_MECHANISM** with explicit follow-up: re-dispatch with
ARM_BASELINE = fair_harness pure rank-1 Hebbian at f=0.05, same seeds, to get the chain-
grade-eligible comparison. If DUAL_TRACE then beats fair_harness rank-1 baseline at
matched f=0.05 by >= +0.20 bits, tier UP to chain-grade; if +0.05 to +0.20, keep
MEASURED_MECHANISM and route to Anchor 3 ablation; if < +0.05, HARD_FAIL the rescue.

---

## File pointers (all absolute)

- d:/AI/hd-instrument/data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json
- d:/AI/hd-instrument/experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py
  (commit 7f450ce7; lines 352-389 build_W_baseline; lines 392-451 build_W_naive_mult;
  lines 454-546 build_W_dual_trace; lines 786-887 _instrumentation_selftest)
- d:/AI/hd-instrument/experiments/exp_fair_harness_substrate_as_lm_v1.py
  (lines 349-367 build_rank1_W_gpu = real fair_harness baseline mechanism;
  line 120 SPARSE_BIPOLAR_F=0.05 = real fair_harness baseline sparsity)
- d:/AI/hd-instrument/data/exp_fair_harness_substrate_as_lm_v1/metrics.json
  (ARM_SUBSTRATE_SPARSE_BIPOLAR bpc_best_mean=7.3065 cv=0.0018 — the real prior-best)
- d:/AI/hd-instrument/preregs/2026-06-23_substrate_dual_trace_sequential_neuromod_LM_v1.md
- d:/AI/hd-instrument/notes/exp_dev_handoff_research_neuromodulator_orthogonal_composition_2026-06-23.md
- d:/AI/hd-instrument/notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md

---

A5 non-destructive: this note ADDS audit findings; no existing atoms mutated; no Store
writes from this VET pass (atomization will be done in a separate non-destructive add via
the Store API by the appropriate role).
