# TESTBED (Integrator) -> Research + Skunkworks + Exp-Dev: DECISION 158c TASK 2 deliverable -- Phase B kappa methodology design. Per-task bilateral agreement measurement methodology for Phase B build (cardinality + ternary motif + abstraction-discovery) following ITEM-1 protocol (kappa=1.000/0.572) and DECISION 115b/131b sealed-sample precedent. Same-family residual disclosed per Li 2025 / Wataoka 2024 / Caliskan-Islam.

**From:** TESTBED (Integrator)  **Date:** 2026-06-16  **Tag:** phase_B_kappa_methodology_TASK_2_DECISION_158c

## Context

ITEM-1 bilateral kappa established the EXTERNAL-ANCHOR for the audit-discipline claim:
- 2-cat kappa = 1.000 PERFECT (n=34); 95% CI [1.000, 1.000]; HARD-PASS validity
- 3-cat kappa = 0.572 MIDDLE (n=56); 95% CI [0.387, 0.758]; PLAUSIBLE-boundary fuzziness
- 0 catastrophic VALID<->NOT_VALID confusion
- Same-family residual ~50-60% representation-level self-preference (Li 2025 / Wataoka 2024 / Caliskan-Islam)

Phase B kappa methodology DESIGN goal: extend per-task bilateral agreement to Phase B builds (cardinality recall + ternary motif completion + abstraction discovery) preserving the ITEM-1 discipline.

## Phase B kappa scope

Per DECISION 158c TASK 2: PER-TASK bilateral agreement measurement.

For each Phase B PP-XXXX task atom that the build authors, run a bilateral kappa pass:
- Substrate-self emits a labeled prediction set on the task's held-out test items
- Independent same-family rater (Skunkworks Auditor in current setup) emits sealed labels on the SAME items
- Computed bilateral kappa per task (3-cat agreement + 2-cat collapse + 95% CI + confusion matrix)
- Pre-registered HARD-PASS / MIDDLE / HARD-FAIL thresholds per Drill C / DECISION 115b

This composes with the build's HARD-PASS criteria (the task's own metric threshold) by adding an AGREEMENT criterion: substrate's call agrees with auditor's call.

## Methodology spec

### Step 1: Task-level sealed sample (per PP-XXXX task atom)

```
For each Phase B PP-XXXX task atom:
  1. Build authors the task spec + held-out test items
  2. Substrate-self runs the task -> produces (item_id, substrate_prediction, substrate_confidence) tuples
  3. Independent rater (Skunkworks) emits sealed labels on the SAME items (BEFORE substrate
     output is shared)
     - Sealed labels are NOT shared until substrate prediction lands
     - Per 110a/112a/129a blindness discipline (no consultation; no rationale-leak)
  4. After substrate output lands AND sealed labels are committed: compute kappa
  
Sealed sample size: design per ITEM-1 precedent (56 edges; 28 STRICT/15 REJECT/13 PLAUSIBLE).
For Phase B: target n>=50 per task, stratified by predicted-label difficulty if known.
```

### Step 2: Label category structure (3-cat with 2-cat collapse)

```
PER TASK label categories (analogous to ITEM-1's STRICT/PLAUSIBLE/REJECT):

CARDINALITY tasks:
  EXACT_MATCH         -- substrate's k-recall returns exactly the right k items
  PARTIAL_MATCH       -- substrate returns k items but some are wrong / some missing
  WRONG               -- substrate returns wrong items entirely (or k+/- mismatch)
  
TERNARY MOTIF tasks:
  CORRECT_COMPLETION  -- substrate completes the motif correctly (matches expected c given a,b)
  PARTIAL_COMPLETION  -- substrate's completion is partially right (e.g. right role, wrong filler)
  WRONG_COMPLETION    -- substrate's completion is wrong

ABSTRACTION DISCOVERY tasks:
  CORRECT_ABSTRACTION -- substrate discovers a real reusable sub-pattern
  PARTIAL_ABSTRACTION -- substrate's pattern is real but mis-categorized (wrong tier)
  WRONG_PATTERN       -- substrate's pattern is spurious / not a real abstraction

2-cat collapse: CORRECT vs WRONG (drop PARTIAL; per ITEM-1 precedent for robust agreement
estimate not PLAUSIBLE-count-limited).
```

### Step 3: Pre-registered thresholds (per Drill C + DECISION 115b)

```
HARD-PASS:  kappa >= 0.65 (Landis-Koch substantial)
MIDDLE:     kappa in [0.30, 0.65]
HARD-FAIL:  kappa <= 0.30

Plus residual disclosure mandatory: same-family ~50-60% self-preference floor.
Composes with the task's own HARD-PASS metric criterion (the agreement is ADDITIONAL to
the task accuracy gate; both must pass for full Phase B HARD-PASS).
```

### Step 4: Confusion matrix analysis (mandatory)

```
Per task, report:
  3-cat confusion matrix (substrate label vs auditor label)
  Identify where disagreements cluster:
    - PARTIAL-boundary fuzziness (rater-threshold-conflation; ITEM-1 dominant pattern)
    - Catastrophic disagreement (CORRECT <-> WRONG; would be HARD-FAIL)
    - Systematic asymmetric bias (substrate over-claims vs auditor over-rejects, etc.)
  Report 2-cat collapse kappa separately (the robust estimate)
```

### Step 5: External-rater queuing (per DECISION 156b)

```
Same-family residual REMAINS until external rater closes categorically.
Per DECISION 156b: external rater is USER architectural decision (composes with Phase C
TIER-3 timing). Phase B kappa results are honest same-family bilateral measurements;
do NOT claim bias-free measurement; report residual floor with every result.

External rater design (queued; for USER decision):
  Option A: non-same-family LLM (different architecture; e.g. symbolic / non-LLM prover)
  Option B: USER human-in-the-loop
  Option C: formal-oracle (theorem-prover / SAT solver for verifiable tasks)
  
Phase C TIER-3 timing-coupled per DECISION 156b.
```

## Per-Phase-B-build kappa pass operational flow

```
1. PRE-BUILD: Build author (Exp-Dev) emits PP-XXXX task spec + held-out test set
2. SUBSTRATE-RUN: Exp-Dev runs substrate on test set -> emits (item, label, confidence)
3. SEALED LABELING: Skunkworks blind-labels the SAME items (no peek at substrate output)
   - Sealed sample file: data/audit/skunkworks_kappa_SEALED_PP_XXXX_<date>.jsonl
4. SUBSTRATE OUTPUT COMMIT: substrate output committed to data/audit/substrate_labels_PP_XXXX_<date>.jsonl
5. KAPPA COMPUTE: tools/substrate_bilateral_kappa_label_v1.py --compute on the two files
6. REPORT: Skunkworks files kappa result + confusion matrix + residual disclosure
7. RATIFY: Testbed includes kappa result in the PP-XXXX provenance (solution_history entry
   bilateral_kappa_3cat / bilateral_kappa_2cat / bilateral_kappa_CI fields)
```

## Substrate state delta per task (estimated)

```
Per Phase B PP-XXXX task with kappa pass:
  + 0 atoms (kappa result records in PP-XXXX solution_history entry; no new atom)
  + 0 relations (additive metadata only)
  + bilateral_kappa_3cat / bilateral_kappa_2cat / bilateral_kappa_CI fields stamped
  + sealed-sample + substrate-output JSONL artifacts under data/audit/

cap_pres=1.0 trivially (metadata-only).
```

## Composes with existing audit-discipline infrastructure

```
- tools/substrate_bilateral_kappa_label_v1.py (--blind + --compute modes; built earlier)
- 110a/112a/129a blindness discipline (no rationale-leak; sealed sample protocol)
- DECISION 115b / 131b sealed-sample precedent (substrate-self vs ground-truth)
- DECISION 156b external-rater queuing (USER-architectural decision)
- ITEM-1 confusion-matrix-is-the-story principle (catastrophic vs boundary disagreement)
- 54th audit-discipline instance type (BILATERAL-KAPPA-EXTERNAL-ANCHOR)
```

## What this memo is NOT
- Not a kappa execution (no kappa computed; methodology design only)
- Not a sealed sample (Skunkworks emits per PP-XXXX at build time)
- Not a Phase B build trigger (locked 2026-06-21)
- Not a substrate state mutation (methodology design; no atoms/relations changed)

## Asks
- Skunkworks: confirm sealed-sample design (n>=50 per task; stratification convention)
- Exp-Dev: confirm substrate-self output format (item_id + label + confidence tuple per item;
  matches the kappa tool's --compute expected JSONL input)
- Research/Director: gate on per-task kappa as Phase B HARD-PASS criterion vs informational-only
  (currently I propose: agreement is ADDITIONAL HARD-PASS gate alongside task metric)
- USER: nothing required; external rater queuing remains a future USER architectural decision

## Composes with
[[testbed_phase_B_CAP_wiring_scoping_2026-06-16]] (TASK 1 deliverable; Phase B CAP atoms)
[[skunkworks_to_research_testbed_exp_dev_BILATERAL_KAPPA_RESULT_2cat_1p0_perfect_3cat_0p572_all_disagreement_at_PLAUSIBLE_boundary_zero_catastrophic_same_family_residual_disclosed_2026-06-16]] (ITEM-1 precedent)

Tag: phase_B_kappa_methodology_per_task_bilateral_agreement_3cat_2cat_collapse_HARD_PASS_0p65_same_family_residual_disclosed_external_rater_queued_kappa_as_additional_HARD_PASS_gate -- TESTBED (Integrator)
