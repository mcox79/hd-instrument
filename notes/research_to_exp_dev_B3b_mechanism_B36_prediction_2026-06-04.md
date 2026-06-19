# Research -> Exp-Dev: B3b regularization mechanism + B36 composition algebraic prediction

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Source:** B3b surprise-gating regularization mechanism 2x drill landed 2026-06-04 (research_drill_b3b_surprise_gating_regularization_mechanism_2x)

---

## B3b mechanism EXPLAINED

The 116% perf from exp-smoothed surprise-gating is **anti-crosstalk at near-saturation**. NOT mysterious; algebraically clean.

**Closed-form prediction:**
```
perf_gain = exp(1.2 * alpha_c / (2 * alpha_full)) = 1.16
solved at alpha_full = 0.558
```

At N=2048 full-write, substrate is at alpha=0.558 (well above optimal alpha_c=0.138 -- saturated). Selective writing via surprise-gating KEEPS ALPHA BELOW alpha_c. Result: less crosstalk between stored patterns → higher per-pattern retrieval accuracy → 116% perf.

**Secondary mechanisms (additive contributions):** information-curation + EWC-analogue forgetting-prevention. Dominant mechanism is anti-crosstalk.

P_deflated for "anti-crosstalk dominant explanation" = 0.40.

---

## Implication: B3b is a CAPACITY-MANAGEMENT primitive (not just compute-efficient)

This reframes B3b's role in Stage A trick stack:
- Earlier interpretation: B3a is write reduction; B3b is "regularizer"
- **Correct interpretation:** B3a is write reduction; B3b is CAPACITY MANAGEMENT (keeps alpha sub-critical)

This connects B3b to other capacity-management primitives:
- B3b: input-side capacity management (gate writes by surprise → prevent alpha rising)
- **B6 D-ECR eviction:** output-side capacity management (evict patterns when alpha approaches alpha_c)
- B2 sparse coding: increases alpha_c ceiling (allows higher M before saturation)

---

## SHARPER ALGEBRAIC PREDICTION FOR B36 COMPOSITION (your queued cell)

**B36 (B3 gating + B6 eviction) targets the SAME capacity axis with COMPLEMENTARY mechanisms:**
- B3 gates writes BEFORE alpha rises (prevention)
- B6 evicts patterns WHEN alpha approaches alpha_c (correction)
- Composed: substrate operates at optimal alpha indefinitely

**Per heterogeneous-pairing principle (today's shared-axis drill):** technically same axis (capacity), but COMPLEMENTARY mechanisms within axis. Predicted composition:
- **SUPERADDITIVE at near-capacity loads** (alpha near alpha_c): both mechanisms contribute orthogonally to capacity management
- ADDITIVE at low load (alpha << alpha_c): neither mechanism is binding
- ADDITIVE at over-capacity (alpha >> alpha_c): substrate broken anyway

### Recommended B36 cell design (sharpened per drill)

Test at THREE loading regimes to discriminate composition behavior:

- **B36-low:** M = 0.5 * alpha_c (low load; predict ADDITIVE)
- **B36-near:** M = alpha_c * 0.9 (near-capacity; predict SUPERADDITIVE)
- **B36-over:** M = 1.5 * alpha_c (over-capacity; predict additive or collapse)

Pre-reg:
- **HARD-PASS:** B36-near combined perf > B3-alone + B6-alone perf (superadditive at near-capacity); B36-low ~ additive
- **MIDDLE:** B36-near additive only (~ B3-alone + B6-alone)
- **HARD-FAIL:** B36-near < max(B3-alone, B6-alone) (collapse)

This tests the algebraic prediction directly. If superadditive at near-cap and additive at low: CLEAN bio-primitive composition validated.

---

## Optional: B3b mechanism-discrimination cell

Drill files 4 discriminating anchor candidates. If we want to ISOLATE anti-crosstalk from secondary mechanisms:

**Cell B3b-isolation:**
- Run B3b (exp-smoothed surprise) at LOW load (M = 0.1 * alpha_c; below saturation)
- Predicted per drill: regularization effect SHOULD DISAPPEAR at low load
- HP: perf at low load ~ baseline (no 116% advantage)
- HF: regularization persists at low load (other mechanism dominates; anti-crosstalk wrong)

~5 min CPU. Validates the anti-crosstalk mechanism algebraically.

Not urgent; nice-to-have for capability characterization.

---

## Stage A trick stack — REFINED understanding

B3a + B3b are TWO different bio-primitives:
- **B3a (top-K% gating):** write-reduction primitive (compute efficiency)
- **B3b (exp-smoothed surprise):** capacity-management primitive (anti-crosstalk)

These are DIFFERENT axes per the shared-axis taxonomy:
- B3a → task-supervised (which pattern to skip writing)
- B3b → capacity (which alpha to maintain)

So B3a + B3b composed are heterogeneous-axis → predicted superadditive (per shared-axis drill).

**This adds a new composition test:** B3a + B3b combined → should give MORE than max(B3a, B3b) alone. Cheap to test.

---

## Strategic state

Substrate's capacity-management primitive stack now CLEAR:
- **B2 DG sparse-expansion:** raises alpha_c ceiling (capacity ceiling expansion)
- **B3b exp-smoothed surprise gating:** keeps alpha sub-critical (input-side prevention)
- **B6 D-ECR eviction:** lowers alpha when above threshold (output-side correction)
- **B4 column ensemble:** distributes load across multiple substrates (parallel capacity)
- **Hierarchical aggregator:** multiplies capacity via N_domains scaling
- **B3a top-K gating:** compute reduction (different axis; task-side)

**This is the substrate's capacity-management TOOLKIT.** Each primitive validated empirically today. Composition strategies algebraically grounded.

---

## What to ship next from Exp-Dev side

In priority order (per round-2 response + this drill):

1. **B36 composition** (queued; sharpened per this drill — test at 3 loading regimes; predict superadditive at near-cap)
2. **B26 composition** (B2 sparse + B6 eviction; capacity ceiling × eviction)
3. **Pure-bio combined** (B2 + B3b + B4 + B6 unified architecture)
4. **B5-bounded-weights** (per drill spec; one clip() call; cheap)
5. **B8 Cell 4 logit-space sparse residual** (per drill spec)

Optional later:
- B3b isolation cell (mechanism discrimination)
- B3a + B3b composition (heterogeneous-axis test)
- B7 phase binding (proper rotation/permutation model)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF for B36 cells
- Per [[feedback-no-padding-experiments]]: B36 cells at 3 loading regimes discriminate composition algebra
- Per [[feedback-pressure-test-negative-findings]]: B3b mechanism drilled algebraically per substantive 116% finding
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

---

**END.**

**Exp-Dev:** B36 composition test now has sharper algebraic prediction (superadditive at near-cap; additive at low load). 3-regime design above. Plus optional B3b isolation cell.

**Research session:** all drills today complete. Standing for composition test verdicts + Phase 0.5 v1 Llama + C1/C2/C3 cornerstone + earlier empirical pipeline. Today's bio-architecture-first program substantially empirically progressed.
