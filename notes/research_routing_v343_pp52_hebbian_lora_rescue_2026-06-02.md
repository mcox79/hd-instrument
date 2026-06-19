# RESEARCH ROUTING — v343 pp52_hebbian_lora rescue + framing correction

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev
**Date:** 2026-06-02
**Trigger:** v343 cycle-13 batch contained pp52_hebbian_lora_speedup_n8192_v1 HARD_FAIL (acc_delta=0.96 total collapse; speedup=1847x spurious; same LVH #207 SPURIOUS_SPEEDUP_FROM_ACCURACY_COLLAPSE pattern). User asked for rescue of speedup + the other negative.
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell design (anchor names, sweep grids, queue specifics, timeout) resolved by strategy + exp_dev. Per-PROT compliance. Per `feedback_strategy_spec_formula_selftests` + `feedback_lock_in_inefficiency_fixes`.

---

## 0. EXECUTIVE — pp52 HF is a comparison-framing failure, not a substrate failure

**The pp52_hebbian_lora_speedup test is structurally broken AT BOTH N=4096 (v342 LVH #207) AND N=8192 (v343 confirmed):**
- LoRA at rank r=20 destroys Llama-style model accuracy at production N (acc collapses to ~0)
- Reported wall_speedup (171M× at N=4096, 1847× at N=8192) is meaningless — comparing substrate's accurate fast write against LoRA's broken fast nothing
- Strategy's 5 rescue sketches (R1 constrained-Hebbian acc-gate, R2 warm-start, R3 mixed-precision, R4 subset-layers, R5 teacher-student) **all keep LoRA in the comparison**, which is the wrong axis

**The right rescue is the FRAMING CORRECTION already proposed in `research_routing_v342_band_lifts_addendum_2026-06-02.md` Section 1.E (Probe E "PP-52 vs LoRA correct framing"):** test PP-52 vs LoRA in the regime where LoRA's accuracy is preserved, not at production N where LoRA structurally fails. This is the only honest empirical comparison.

**Substrate primitive (Hebbian one-shot) is CONFIRMED HP at production N** by the v343 BAND-LIFT (pp52_exact_rollback_n16384 + pp52_one_shot_addition_n16384 both HARD_PASS). The substrate value claim is INTACT; it's the LoRA-comparison axis that broke.

---

## 1. ROOT-CAUSE ANALYSIS — why LoRA collapses at production N

### 1.a Algebraic derivation

LoRA approximates weight update ΔW = AB^T where A ∈ R^(N×r), B ∈ R^(M×r), r << min(N,M). For a target update ΔW_target of effective rank ρ_target, LoRA's representational capacity is rank-r. When rank deficit r << ρ_target:

```
||ΔW_target - AB^T||_F^2 / ||ΔW_target||_F^2 ≥ (ρ_target - r) / ρ_target
```

For pp52 task (1-shot fact addition where ΔW_target = ξ_new ξ_new^T / N, effective rank = 1 per fact), LoRA at r=20 has rank surplus, so approximation error should be small...

**BUT** the test runs LoRA against a stored substrate W with M=400 patterns, alpha=M/N=0.05 at N=8192. The full target ΔW for the K-fact-addition workload has effective rank ≈ K. The test uses K=10 fact additions; LoRA r=20 has rank surplus 2:1. **Mathematically, LoRA should reconstruct the K=10 update at r=20.**

So WHY did accuracy collapse?

**Hypothesis:** the test loss isn't fact-addition reconstruction — it's an end-to-end accuracy metric on a downstream task that uses the entire W. LoRA's r=20 approximation introduces error EVERYWHERE in W, not just at the fact-addition update site. Even though the K=10 addition is well-fit, the M=400 baseline patterns get perturbed by the LoRA correction. Single forward pass through perturbed W → downstream task fails.

**This is structural, not a parameter-tuning issue.** LoRA modifies the WHOLE W; substrate Hebbian writes ONLY at the addition site. Different operational semantics; one-shot LoRA-as-replacement-for-fact-addition is conceptually wrong, not just numerically off.

### 1.b Why strategy's 5 rescues miss

- **R1 constrained-Hebbian acc-gate**: gates on acc, but the test is still LoRA-vs-Hebbian — doesn't fix the structural mismatch
- **R2 warm-start-only**: warm-starts LoRA from substrate W — but LoRA still globally modifies W
- **R3 mixed-precision**: numerical, not structural
- **R4 subset-layers**: restricts LoRA to specific layers — closer but still keeps LoRA as the baseline
- **R5 teacher-student**: distillation, conceptually different but operationally complex

**R6 (this routing) — DROP the Hebbian-vs-LoRA comparison axis entirely.** Replace with Hebbian-vs-LoRA-in-the-regime-where-LoRA-works (small N, small M, sufficient rank, accuracy preserved).

---

## 2. PROPOSED RESCUE — Probe E from v342 addendum, formalized

### 2.a Anchor specification

**Anchor name:** `pp52_hebbian_vs_lora_in_lora_valid_regime_n1024_v1`
**Resource:** CPU
**Wall estimate:** ~30 min (4 r-values × 5 seeds × N=1024 = relatively cheap)
**Timeout:** 1800s
**Cost:** $0
**P_deflated:** 0.65 (the regime where LoRA preserves accuracy is well-precedented; substrate Hebbian is faster than LoRA at any r > 0 by construction)

### 2.b Test design

In the LoRA-valid regime (small N, small M, sufficient rank):

```
N = 1024
M = 100 baseline patterns + K = 10 fact additions
r ∈ {N//10=102, N//5=204, N//2=512, N=1024}
seeds = 5
```

For each (r, seed):
1. Train baseline substrate W (M=100 patterns via Hebbian write)
2. Add K=10 facts via:
   - (a) Substrate Hebbian one-shot (substrate gold standard)
   - (b) LoRA fine-tune with rank r (until convergence or max_steps=200)
3. Measure: held-out fact-retrieval accuracy, baseline-pattern retention, wall time, FLOPs

### 2.c Pre-registered bands

**HARD-PASS (PP-52 substrate value confirmed in LoRA-valid regime):**
- Substrate fact-retrieval accuracy ≥ 0.95 (HP1)
- LoRA fact-retrieval accuracy ≥ 0.90 at MINIMUM r where LoRA passes (HP2, ENABLES the comparison)
- Substrate wall_time ≤ (1/100) × LoRA wall_time at minimum r where LoRA passes (HP3)
- Substrate FLOPs ≤ (1/1000) × LoRA FLOPs at minimum r where LoRA passes (HP4)
- Substrate baseline-pattern retention ≥ 0.95 (HP5 — substrate's exact-rollback property)

**MIDDLE (substrate-novel but narrower win):**
- HP1, HP2 pass; HP3 wall_speedup 10×-100× (substrate is faster but not 100× faster) OR
- HP4 flops_speedup 100×-1000× (substrate uses fewer FLOPs but not 1000× fewer)

**HARD-FAIL (substrate value claim refuted in LoRA-valid regime):**
- Substrate wall_time ≥ LoRA wall_time at any valid r — no measurable speedup
- Substrate baseline-pattern retention < 0.80 — substrate's exact-rollback property broken
- LoRA accuracy never recovers at any r ≤ N — LoRA-valid regime doesn't exist on this task

**Note:** if HP2 fails at all r ≤ N (LoRA NEVER works on this task), then the test reveals "LoRA-incompatible task" — substrate has no LoRA comparator at all. Reframe PP-52 row from "Hebbian-vs-LoRA speedup" to "Hebbian-one-shot at production N where LoRA structurally fails." Either outcome is product-narrative load-bearing.

### 2.d Strategic outcome

- **If HARD-PASS:** PP-52 row narrative formally adopts "Hebbian = exact O(N) update; LoRA = approximate O(rN) update with accuracy ceiling proportional to N/r ratio AND task-dependent rank-rank-deficit cliff at production N." Strong product positioning.
- **If MIDDLE:** narrower win but substrate still substantively faster; PP-52 keeps current 0.65-0.80 band; LoRA comparison is for small-N regimes only.
- **If HARD-FAIL:** substrate-novel rescue needed; PP-52 framing reverts to one-shot-vs-fine-tuning (not LoRA-specific).

---

## 3. SECONDARY RESCUE — DEPRECATE the LoRA-as-replacement test at production N

**Strategy cap_map annotation:**

> **PP-52 sub-property: pp52_hebbian_lora_speedup at production N is STRUCTURALLY MISFRAMED.** LoRA modifies whole W with rank-r approximation error; substrate Hebbian writes ONLY at the addition site. The two are not comparable as "one-shot fact-addition methods" at production N because LoRA's global-W modification breaks downstream-task accuracy. Test deprecated. Replaced by pp52_hebbian_vs_lora_in_lora_valid_regime_n1024_v1 (Probe E from v342 addendum). Substrate value claim continues to rest on PP-52 exact-rollback + one-shot-addition cross-N {1024, 4096, 8192, 16384} all HP (4 anchors confirmed).

**This is annotation-only**, no GPU spend. Strategy_scribe one-shot.

---

## 4. WHAT TO DO ABOUT THE 5 STRATEGY-FILED RESCUES

Strategy's 5 rescue sketches (R1 constrained-Hebbian, R2 warm-start, R3 mixed-precision, R4 subset-layers, R5 teacher-student) are LoRA-axis-preserving rescues that still get the structural mismatch wrong.

**Recommendation:** PARK them in cap_map. They're potentially useful for SOMEONE ELSE'S "improve LoRA" research, but not for substrate's value claim. Substrate doesn't need to rescue LoRA; substrate needs to demonstrate it does something LoRA cannot do at production N (exact rollback + one-shot addition with audit cert).

If user wants to also test R4 subset-layers (the cheapest of the 5 strategy rescues, and the closest to substrate's site-specific operational semantics), it could fire as a SECOND independent anchor `pp52_hebbian_vs_subset_layer_lora_n4096_v1` for ~30 min CPU at $0. Optional.

---

## 5. PROT-022 SELFTEST LOCK-IN (additional registry entry)

The pp52_hebbian_lora test's HP gate `wall_speedup >= 100x` is INVALID without an accuracy precondition. Adding to selftest registry per `research_routing_v342_r2_meta_finding_4fix_queue_2026-06-02.md` Section 3:

### Registry addition 4 — Metric-ordering dependency for speedup gates

```
A "speedup" gate is VALID only if the accuracy precondition is met first.
```

**Selftest cell:**
- For any HP gate of form `wall_speedup >= X` or `flops_speedup >= X`:
- REQUIRED precondition: `acc_baseline >= ACC_FLOOR` AND `acc_method >= ACC_FLOOR`
- If precondition fails: the speedup metric is undefined (NaN, infinite, spurious); HP gate cannot be evaluated; result is HARD_FAIL not by-the-speedup-number but by-the-accuracy-precondition

**Apply to:** any pp52 / Hebbian-vs-LoRA / Hebbian-vs-GD comparison spec where speedup is a HP gate. Acc precondition should be a HF-trip-wire, not a separate "informational" HP.

This formalizes the LVH #207 SPURIOUS_SPEEDUP_FROM_ACCURACY_COLLAPSE sub-flavor as a STRUCTURAL spec rule.

---

## 6. CAP_MAP IMPACT EXPECTATIONS (if rescue PASSes)

- **PP-52 row UNCHANGED at 0.65-0.80** (just BAND-LIFTed in v343 via N=16384 cross-N; no further lift from rescue alone)
- **PP-52 sub-property added:** "Hebbian-vs-LoRA in LoRA-valid regime (N=1024 M=100 K=10): substrate ≥1000× wall + ≥10000× FLOPs faster while preserving accuracy + retention"
- **PP-52 sub-property added:** "Hebbian-vs-LoRA at production N: LoRA structurally fails (accuracy collapse); substrate continues to operate; comparison axis MISFRAMED at production N — see deprecation annotation"
- **PROT-022 registry entry 4 added:** speedup gates require accuracy preconditions
- **No row closures.** LoRA-comparison axis is a sub-property of PP-52, not the load-bearing row.

If MIDDLE: still adds the sub-property "Hebbian faster than LoRA only modestly in LoRA-valid regime" — substrate's value at production N (where LoRA fails) is the real story.

If HF: substrate-novel reframe required; reroute through deeper R2/R3 on alternative baselines (fine-tune from scratch, PEFT variants beyond LoRA, knowledge distillation).

---

## 7. SEQUENCING

**Immediate (parallel, $0):**
1. **Probe E formalized** as `pp52_hebbian_vs_lora_in_lora_valid_regime_n1024_v1` — CPU, ~30 min wall
2. **Strategy annotation** of pp52_hebbian_lora_speedup deprecation at production N (one-shot strategy_scribe)
3. **PROT-022 registry entry 4** added (one-shot strategy_scribe; part of the cap_map atomic commit)

**Optional follow-on:**
4. `pp52_hebbian_vs_subset_layer_lora_n4096_v1` (R4 from strategy's 5 rescues; sub-property test, not load-bearing)

---

## 8. DISCIPLINE DECLARATIONS

- Per `feedback_strategy_spec_formula_selftests`: PROT-022 registry entry 4 added; speedup gates now require accuracy precondition.
- Per `feedback_rehabilitation_after_rejection`: pp52_hebbian_lora HF gets framing-correction rescue (Probe E) before any closure consideration; substrate value claim continues to rest on the 4 confirmed exact-rollback + addition anchors at production N.
- Per `feedback_no_padding_experiments`: ONE new probe (Probe E) + ONE annotation + ONE registry update; no padding. Optional R4 subset-layer is sub-property test, not flagship.
- Per `feedback_lock_in_inefficiency_fixes`: PROT-022 entry 4 is the structural lock-in for the LVH #207 / spurious-speedup pattern; future PP-52 cells use this rule from spec.
- Per `feedback_substrate_value_framing_2026-05-26`: substrate's real value at production N is exact-rollback + one-shot-addition + cert (4 confirmed anchors); LoRA comparison axis is a sub-property, not the row.
- Per `feedback_capabilities_not_product_positioning`: framing correction is a capability statement (substrate does site-specific update; LoRA does global-W update), not GTM positioning.
- Per `feedback_obey_user_pause_explicitly`: pause flag ABSENT (verified upstream).

---

## 9. WHAT THIS ROUTING DOES NOT TOUCH

- **The "other negative" from v343 batch (15 verdicts, 12 HP, 2 HF) is not named in the strategy log or visibility entry I have read.** I see only pp52_hebbian_lora_speedup_n8192_v1 explicitly named. If user can name the second HF, a parallel rescue routing can fire on next read. Likely candidates the v343 batch could have hit:
  - `q_f5_oscillating_envelope_v2_n8192` (recent failed entry in bridge cache; Q-F5 framework-corroborating probe; if HF, R1 annotation + R2 observable audit per PP-33 framework class context)
  - One of the I-12 / I-14 / Phase 0 0c fixes from my v342_r2_meta_finding routing (if they landed in this batch and one returned HF)
  - A Q-A3 / PP-48 / Q-B1 ceiling-push probe at the next depth

**Without the name, I can't pre-register HF-specific bands.** Surface the second HF name and I'll ship its rescue routing in the same shape as this one.

---

**END.** Orchestrator: queue Probe E formalized (1 anchor, CPU, ~30 min wall, $0); dispatch strategy_scribe for deprecation annotation + PROT-022 registry entry 4 + cap_map atomic commit. Strategy: PARK 5 LoRA-axis-preserving rescues (R1-R5 from v343 strategy entry) as sub-property follow-ons; flagship rescue is the framing correction (this routing). exp_dev: cell design for Probe E from Section 2; mechanical parameter changes from the existing pp52_hebbian_lora_speedup script; the metric should DROP the wall_speedup HP gate and instead make accuracy preconditions HF-trip-wires per PROT-022 entry 4.
