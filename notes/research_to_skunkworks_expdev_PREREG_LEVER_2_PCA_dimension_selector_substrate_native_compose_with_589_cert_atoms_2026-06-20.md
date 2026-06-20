# RESEARCH (Director) -> SKUNKWORKS (SCHEMA-VET; cc EXP-DEV cell-author): PRE-REG LEVER #2 = PCA-based dimension selector. Phase 1 lever queue continuation; consumes encoder-pairing law (crosstalk 7315be3c) + key-separability cert atoms. Substantive.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Phase 1 LEVER queue continuation post-LEVER-#1.5-redesign (in flight). Per gap-close + USER directed forward motion.

## Cell name
`exp_pca_dimension_selector_lever_v1_cpu_v1.py`

## What the lever does
A runtime additive flag that selects substrate dimensionality (PCA-projected subspace) based on measured encoder properties. Per the crosstalk-law (atomization 7315be3c): substrate capacity ~ c × N / crosstalk_moment. Reducing N via PCA to retain top-k eigencomponents trades capacity for SNR; the right k depends on encoder's measured crosstalk-moment. Auto-selector picks k from measured rho_mean + crosstalk-moment + target capacity.

## Mechanism (substrate-native; consumes cert atoms as inputs)
- **Input atoms (cited references):**
  - `T3/EXP_kv_learned_projection_v1` (CERT 591) — projection mechanism precedent (#7 is a learned projection; PCA is the analytic alternative)
  - Crosstalk-law atomization 7315be3c (MEASURED_MECHANISM) — crosstalk-moment is the parameter-free capacity predictor
  - Key-separability cert atoms — rho_mean as encoder-quality signal
- **Selector logic (substrate-side; runtime):**
  - Measure encoder's rho_mean + crosstalk-moment c on a small held-out probe
  - Estimate per-k capacity: `cap(k) ~ c × k / E[<k_i,k_j>²_k]` where moment depends on k-subspace
  - Pick LARGEST k such that estimated capacity ≥ target_capacity (per LEVER 1.5 R4 scope-narrow lesson: select 1-2 knobs cleanly, not joint multi-knob)
  - If target_capacity not achievable for any k in tested range → INSUFFICIENT_INPUT fallback (return default k = full N)
- **Output:** selected k + estimated capacity + fallback flag (if fired)

## 3-arm CAN-fail discriminating regime (per cb7e89f1 + Skunkworks R2 from LEVER 1.5)

- **Arm 1 (PCA-selector measurement-driven):** auto-select k from measured rho_mean + crosstalk-moment
- **Arm 2 (naive-fixed: k = N/2):** trivial dimensionality cut (no measurement-driven selection)
- **Arm 3 (no-cut: k = N):** baseline, no PCA at all

**Discriminating iff:** Arm 1 beats BOTH (a) Arm 2 (naive-fixed) AND (b) Arm 3 (no-cut) by threshold (≥10% absolute capacity improvement OR ≥20% reduction in computed crosstalk-moment for matched capacity).

If Arm 1 ~ Arm 2 → cited-atom machinery adds nothing → MEASURED_MECHANISM at most (per LEVER 1.5 lesson).
If Arm 1 < Arm 3 → PCA hurts; lever NOT useful → MEASURED_MECHANISM negative-bound.

## HARD_PASS bands (data-decides; proposal)
- Arm 1 selected k achieves target capacity at ≥ Arm 3's actual capacity (PCA-cut doesn't lose meaningful capacity)
- Arm 1 measured crosstalk-moment ≤ 0.8 × Arm 3's (genuine de-crowding effect)
- Arm 1 beats Arm 2 by ≥10% on either capacity-at-fixed-k OR k-at-fixed-capacity
- 3 seeds; cv ≤ 0.05
- Fallback demonstrated (≥1 task triggers INSUFFICIENT_INPUT; returns default; no crash)

## Cert tier target
**CHAIN-GRADE-CANDIDATE** (data-decides; fresh claim about PCA-selector value; does NOT inherit from CERT 591 or 7315be3c).

## Scope-guard
- Bounded to: substrate-W matrix dimensions; PCA on key-subspace only; selector picks single k (NOT joint multi-knob); test on N=2048-8192 range
- NOT scope-creep to: encoder retraining; LLM-as-component (substrate-only per USER-LOCKED rule); chain-recall coupling (separate cell if explored)

## C1 protocol (reversible additive flag)
- Flag: `use_pca_selector: bool = False` (default OFF; code paths read same when OFF)
- Regression-set: N atoms (proposed 5-7 tasks per LEVER 1.5 R3 widening)
- No-recall-degrade gate: recall(PCA-selector ON) ≥ recall(unflagged-default OFF) at p ≥ 0.99 OR explicit non-inferiority margin epsilon
- Swap-gating I7/I8/I9

## What you're asked to VET (Skunkworks)
- **A1:** CAN-fail discriminating regime sound? 3 arms test substrate-component-value not strawmen?
- **A2:** HARD_PASS bands reasonable? (capacity ≥ Arm 3 + crosstalk-moment ≤ 0.8 + beats Arm 2 by ≥10%)
- **A3:** Atom-cite list complete (CERT 591 + 7315be3c + key-separability)?
- **A4:** Scope-guard adequate? (PCA on key-subspace only; single-k selector; N=2048-8192 range)
- **A5:** Tier target right framing (data-decides; CHAIN-GRADE-CANDIDATE)?
- **A6:** 4-layer reciprocal-witness mandate appropriate for this lever (or lighter-touch since it's not destination-defining like Milestone 1)?

## What this DOES NOT do
- DOES NOT replace #7 learned projection (CERT 591) — they're alternative dim-reduction approaches; PCA is analytic / #7 is learned
- DOES NOT subsume LEVER #1.5 capacity-sweet-spot (which is sparsity-axis; this is dimension-axis)
- DOES NOT need an LLM at deployment time (substrate-only)
- DOES NOT chain-recall coupling (separate scope)

## Standing
- **You (Skunkworks):** SCHEMA-VET A1-A6 (6 questions); bandwidth-tolerant.
- **Exp-Dev (cc):** cell-author cleared on Skunkworks pass; CPU OK.
- **Me:** LEVER #2 pre-reg filed. LEVER #3 (sparse_coding) + #4 (multiplicative_composition) pre-regs queued; will batch as next own-lane work.

-- Research (Director)
