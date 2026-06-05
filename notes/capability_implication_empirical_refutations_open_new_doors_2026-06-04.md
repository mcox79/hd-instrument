# Capability-implication -- empirical refutations + new doors opened (cycles 66-69)

**From:** Research session
**To:** Orchestrator (primary); strategy_scribe (annotation execution)
**Date:** 2026-06-04 (post Cycles 66-69)
**Subject:** TWO conservative algebraic predictions empirically REFUTED today. Pressure-test-negative-findings methodology vindicated empirically. Capability map needs updates + new empirical doors opened.

---

## TL;DR

Two HARD_PASSes empirically refuted conservative algebraic predictions:
1. **Position-binding + symmetric Hebbian at TRIGRAM HP** (Bundle E E1; gap +1.291 nats; 3/3 seeds)
2. **Task-complexity sweep HP through extended-context K=8 at N=8192**

These directly refute the position-binding drill and task-complexity drill predictions (both shipped earlier today). The pressure-test-negative-findings methodology was empirically validated TWICE in single day.

Plus spectral edge finer-N landed: beta=0.513 (Gaussian class, NOT BBP-critical as drill predicted). Deletion-cert sigma recalibration is ~2-3x, NOT 5x.

---

## Empirical refutations of today's drill predictions

### Refutation 1: Position-binding drill K*=2.0 with symmetric W

**Drill prediction (2026-06-04):** Cell E1 (position-binding + symmetric Hebbian at trigram V=70 N=4096) = "predicted HF; K* stays at 2.0 per drill; capacity wall unchanged"; P_deflated=0.10 for HP

**Empirical (Cycle 69):** Cell E1 HARD_PASS at gap +1.291 nats, 3/3 seeds

P_predicted_HP=0.10; empirical HP. ~10x algebraic over-confidence in failure mode. Position-binding 2x drill's K* analysis was WRONG for symmetric W.

### Refutation 2: Task-complexity drill K* ceiling

**Drill prediction (2026-06-04):** K* = log_V(alpha_c * N) + 1. At V=70, N=8192: K*=2.8 (sub-trigram). Predicted K=8 extended-context FAIL at any N.

**Empirical (Cycle 67):** substrate_task_complexity_sweep through extended-context K=8 at N=8192 HARD_PASS

Direct refutation of K* formula. Multiple K-values tested; K=8 still HP.

### Confirmation: Friston FEP HARD_FAIL at trigram

**Drill prediction (calibration drill 2026-06-04):** FEP at trigram still HF at 10k LM due to parameter-budget defeat + NESS subsumption; recovery threshold K_LM > 50k+ params with diagonal Pi.

**Empirical (Cycle 67):** substrate_friston_fep_trigram_cell HARD_FAIL.

P_predicted_HF=0.75; empirical HF. CONFIRMS the W-modifying vs inference-overhead methodology + parameter-budget defeat hypothesis.

### Refinement: Spectral regime finer-N

**Drill prediction (intermediate-regime 2x drill 2026-06-04):** BBP-critical regime (beta~1/3); deletion-cert sigma 5x overconfident

**Empirical (Cycle 69):** beta=0.513 95%CI=[0.435, 0.599]. CI does NOT include 1/3 (BBP-critical refuted); CI DOES include 1/2 (Gaussian). Substrate is Gaussian / non-Hermitian class.

Refinement: deletion-cert sigma recalibration is ~2-3x (Gaussian regime), not 5x. Less drastic than originally claimed.

---

## NEW DOORS opened by these findings

### Door 1: substrate at K=12, K=16, K=32 extended-context (Bundle G test)

If K=8 HP at N=8192, what's the TRUE empirical task-complexity ceiling? Test K=12, K=16, K=32 at N=8192-16384 to characterize the scaling.

Predicted (per pressure-test methodology + true-scaling drill in flight): substrate may extend to K=10-20+ at substrate-class scale with combined architecture (position-binding + sparse + STDP).

If TRUE empirical K_ceiling >> 8: substrate's product narrative extends from "audit primitives at bigram-class" to "competitive language modeling at LLM-class context."

### Door 2: position-binding + symmetric W as the FOUNDATIONAL primitive

E1 HP suggests position-binding + symmetric Hebbian is the MINIMAL ARCHITECTURE for substrate-as-training at trigram. Far simpler than the combined architectures Bundle A/F/E test.

New direction: drill on WHY this minimal architecture works (in flight via "position-binding symmetric W trigram explanation" drill). Then test extension to K=4, K=5, K=8 with position-binding + symmetric W alone (isolates the position-binding contribution).

### Door 3: real Shakespeare char-LM with position-binding architecture

All today's empirical tests used synthetic Zipf vocabulary. Need real-task validation. Shakespeare char-LM (V~70 chars; real natural language) at substrate-class N=4096-16384 with position-binding + symmetric Hebbian would test:
- Real-task ceiling
- Natural language structure benefit (V_eff << V)
- Comparison to char-LM transformer baseline

If substrate matches or beats char-LM transformer on Shakespeare at N=4096-16384: substrate-as-training-mechanism is competitive at small scale.

### Door 4: heterogeneous architectural pairings for superadditive composition

cf-RPE + sparse combined was ADDITIVE (not superadditive) per Cycle 67. Per shared-axis hypothesis (drill in flight): heterogeneous pairings (cf-RPE + STDP; cf-RPE + position-binding) should compose superadditively.

New empirical: test cf-RPE + STDP + position-binding combined architecture (different from Bundle F which tests ALL primitives combined).

### Door 5: spectral regime correction informs deletion-cert product claim

Spectral edge is Gaussian class (~1/2), not BBP-critical (1/3). Deletion-cert sigma recalibration is ~2-3x, not 5x. Less drastic product impact. Update product-critical note.

---

## Sub-property foundings requested

### 1. K* formula refuted; corrected scaling law pending

Update task-complexity ceiling sub-property founding (from earlier today):

"Original K* = log_V(alpha_c * N) + 1 formula EMPIRICALLY REFUTED 2026-06-04. Empirical evidence: substrate_task_complexity_sweep_v1_512_8192_gpu HP through extctx-K=8 at N=8192; substrate_position_binding_combined_arch_trigram_v1_n4096 E1 HP at K=3 trigram with position-binding + symmetric Hebbian. Substrate's true task-complexity ceiling is EMPIRICALLY HIGHER than algebraic prediction. Architecture-dependent: position-binding raises ceiling; combined architecture raises further. Corrected scaling law pending (drill substrate_true_task_complexity_scaling_law_2x in flight)."

### 2. Position-binding + symmetric W is minimal substrate-as-training architecture

NEW founding under substrate-as-training-mechanism row:

"Position-binding + symmetric Hebbian outer-product write is the EMPIRICAL minimal architecture for substrate-as-training at trigram task. Verified at V=70 N=4096: gap +1.291 nats vs uniform_baseline; 3/3 seeds. Algebraic mechanism (per drill substrate_position_binding_symmetric_w_trigram_explanation_2x in flight): input-output type asymmetry between sentence vector S (high-dim structured) and target token t_next (low-dim) provides effective representational asymmetry even with symmetric update rule. Substrate may have higher effective K* than algebraic single-substrate K* prediction."

### 3. Spectral regime corrected to Gaussian (not BBP-critical)

Update spectral regime sub-property founding (from earlier today):

"Substrate spectral edge beta_local = 0.513 95%CI=[0.435, 0.599] at N=4096-65536 with 5+ seeds. CI EXCLUDES BBP-critical (1/3) and zero; INCLUDES Gaussian (1/2). Substrate is in Gaussian / non-Hermitian class, NOT BBP-critical. Bertini active-driven NESS framework still applies but with corrected beta. Deletion-cert sigma recalibration factor is ~2-3x (Gaussian regime), NOT 5x (BBP-critical assumption). Less drastic product impact. Lit anchors: Knowles-Yin 2014 anisotropic local laws; Cipolloni-Erdos-Schroder 2021 non-Hermitian Tracy-Widom variants."

### 4. Pressure-test-negative-findings methodology empirically validated

Reinforces feedback_pressure_test_negative_findings memory (already filed):

"Methodology empirically validated 2026-06-04 by two HARD_PASS refutations of same-day algebraic drill predictions: position-binding drill K*=2.0 refuted by Cell E1 HP at trigram; task-complexity K* formula refuted by extctx-K=8 HP at N=8192. Two distinct algebraic predictions refuted in one day; methodology lock-in justified."

---

## Updates to architectural design strategy

### Highest-priority primitives (empirically validated)

1. **Position-binding** (NEW priority elevation) — empirically minimal architecture for substrate-as-training; HP at trigram with symmetric W
2. **cf-RPE** — bigram HP at substrate-class scale; task-side gain (NOT capacity gain at N=16384)
3. **Drosophila sparse coding f=0.05** — bigram HP; capacity gain at substrate-class scale
4. **STDP-asymmetric** — bigram MIDDLE; trigram HP with position-binding (Bundle E E2)
5. **Modern Hopfield p=4** — pending Bundle F empirical; combined architecture

### Lower-priority primitives (empirically ambiguous)

- **Friston FEP** — HF at bigram + trigram; inference-overhead subject to subsumption
- **Mapper topological** — beta_0 insensitive to drift; classical TDA constrained by Adams-Virk; alternative topological signatures needed
- **Single-modulator sparse Drosophila** — K=1 modulator insufficient; need K>=3 for differentiation

### Architectural composition rules (per shared-axis hypothesis)

- HOMOGENEOUS pairings (same gain axis): ADDITIVE only (cf-RPE + sparse = task-side + task-side)
- HETEROGENEOUS pairings (different gain axes): potentially SUPERADDITIVE
- For superadditive composition: cf-RPE + STDP (task + sequence); cf-RPE + position-binding (task + context); position-binding + sparse + STDP (context + capacity + sequence)

---

## What's NOT changing

- Cap_map row structure (no top-level changes)
- W-modifying vs inference-overhead methodology (REINFORCED by FEP trigram HF)
- Lit anchor chain (additions from new drills; no removals)
- Substrate's hidden objective framework (KL[p || mu_NESS] still applies)
- Audit primitives (deletion cert + drift detection + L=10000 composition all stand)

---

## What IS changing

- Position-binding is FOUNDATIONAL (not just complementary) — promoted to primary architectural primitive
- K* formula REPLACED by empirical scaling law (TBD; drill in flight)
- Deletion-cert sigma recalibration: ~2-3x (not 5x)
- Substrate's task-complexity ceiling EMPIRICALLY HIGHER than algebraic predictions
- All future drill predictions: apply HEAVIER deflation when "substrate cannot X" claims; pressure-test methodology mandatory

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Orchestrator informed; strategy_scribe annotation execution
- Per [[feedback-pressure-test-negative-findings]]: empirical validation of methodology; future drill predictions apply heavier deflation to negative claims
- Per [[feedback-no-smoke]]: brutal honesty about today's algebraic-empirical mismatches; methodology updated
- Per [[feedback-verdicts-include-intuitive-explanation]]: plain language throughout
- ASCII-only

---

**END.**

**Orchestrator:** route to strategy_scribe for 4 sub-property foundings + 3 architectural update annotations per § above. Next visibility entry should cite the empirical refutations + methodology validation + new doors opened.

**Research session:** 3 follow-up drills dispatched in parallel (cfrpe-sparse shared-axis; position-binding symmetric W trigram explanation; true task-complexity scaling law). Plus Bundle G/H empirical routing pending separate ship.
