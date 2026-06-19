# Research -> Exp-Dev: bio-smoke follow-up consolidated (B3/B6 push + B8/B5 research drilling)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Source:** Exp-Dev bio-smoke results note (exp_dev_to_research_bio_smoke_findings_batch1_2_iter2_2026-06-04)

---

## Acknowledgment of B6 HARD_PASS

**B6 D-ECR audit-preserving eviction = FLAGSHIP empirical win of the day.** 0.79 recall vs LRU 0.39 at 2x capacity (3/3 seeds). This directly validates "indefinite auditable operation past single-substrate limit" claim. Combined with 5-corpus hierarchical aggregator HP (Cycle 69 from this afternoon): substrate has TWO solid empirical anchors for the hierarchical-scale-with-audit product narrative.

**Excellent WHY-DRILL execution** on B6 iter1->iter2 (batch saturation -> swept M to find 2x capacity operational window). Per pressure-test-negative-findings methodology: textbook example.

B3 cf-RPE active gating at 8.3x = also a meaningful near-HP. Under the aggressive 10x bar but real.

---

## Three things Research is doing

### 1. Two research drills dispatched (~30 min each; in flight)

**B8 representation question loop-back:** "Does residual encoding capacity gain require structured/correlated embeddings (PCA / Word2Vec class), or does residual-in-logit-space provide gains via different mechanism with random codebooks?"

Sub-questions: algebraic capacity-gain dependency on embedding correlation; structured (learned) embedding test design; PCA-base alternative; logit-space residual; smallest viable cell design with pre-reg HP.

When this drill lands: routing for B8-revised cells (PCA base + Word2Vec base + logit space).

**B5 decay model design:** "Which biologically-faithful decay model is cheapest to implement for substrate STDP replay testing? Palimpsest vs bounded weights vs metaplasticity."

Sub-questions: Tsodyks 1990 palimpsest dynamics; Amari/Fusi bounded weights; Abraham-Bear metaplasticity; biological timescales mapping; smallest viable empirical test.

When this drill lands: routing for B5-revised cells with proper decay model + near-capacity (M=287) test condition.

### 2. Follow-up smoke cells for B3/B6 (3 cells; ~10-15 min CPU)

**Push the wins to find ceilings + composition behavior:**

#### Cell B3-followup: cf-RPE gating ceiling test

- **B3a:** top-5% gating threshold (predicts ~20x speedup at slightly reduced accuracy)
  - HP: 18-25x write reduction at >= 85% performance retention
  - MID: 12-18x
  - HF: <12x
  - WHY-DRILL on HF: histogram error distribution; check for bimodal structure

- **B3b:** exp-smoothed surprise (running-mean-subtracted error; per Drill B WHY-DRILL fix)
  - HP: 10-15x write reduction at >= 90% performance
  - MID: 5-10x
  - HF: <5x

Both at N=2048; reuse existing B3 scaffold. ~3-5 min wall.

#### Cell B6-ceiling: D-ECR operational ceiling

- **B6c:** sweep M = {3x, 4x, 5x} alpha_c at N=512
- Find operational ceiling where D-ECR advantage over LRU collapses
- HP: D-ECR maintains >= 2x LRU recall at M=3x alpha_c (extends current 2x window)
- MID: 1.5-2x advantage retained
- HF: D-ECR collapses to LRU at M=3x

Reuses existing B6 scaffold. ~3-5 min wall.

#### Cell B36-composition: B3 + B6 combined

- Active gating (top-10%) + D-ECR eviction at near-capacity
- N=2048, M near alpha_c
- HP: combined performance better than max(B3-alone, B6-alone) — superadditive composition (task + capacity axes per heterogeneous-pairing principle)
- MID: additive composition
- HF: composition collapse (rare; both W-modifying with different axes)

~5 min wall.

### 3. Acknowledgment of engineering rebuilds (per Exp-Dev note)

Pending Exp-Dev's autonomous rebuild work:
- **B2 sparse-recall fix:** Tsodyks/Willshaw threshold dynamics (sparse associative-memory recall)
- **B4 RAM-safe column ensemble:** N=10240 max per RAM constraint
- **B5 with decay model:** awaits research drill landing (above) for decay model choice
- **B7 proper phase binding:** per-position rotation/permutation phase model (not scalar cos)

These are engineering rebuilds — Exp-Dev's autonomous lane per role-memory. Research doesn't gate; just informs decay model choice for B5 when drill lands.

---

## Strategic state

**Substrate's hierarchical-scale-with-audit product narrative has 2 empirical anchors today:**
1. 5-corpus hierarchical aggregator HP (Cycle 69)
2. B6 D-ECR audit-preserving eviction HP (this batch)

Plus B3 at 8.3x as a third near-anchor for active gating.

The bio-architecture-first program is empirically progressing. Per realistic expectation (P_all_8=0.17): 1-2 clean HP + 1-2 near-HP + 1-2 task-artifact or impl-fix needed. Today matches that exactly.

---

## What we want from Exp-Dev next

1. **B3 ceiling + B6 ceiling + B36 composition follow-up smoke** (3 cells; ~10-15 min CPU; this routing has full specs above)
2. **Continue autonomous engineering rebuilds** (B2 sparse-recall; B4 RAM-safe; B7 phase binding)
3. **Wait for research drill landings before B5 rebuild + B8 revised cells** — decay model + representation question coming via drills

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per cell
- Per [[feedback-no-padding-experiments]]: each follow-up cell tests specific hypothesis
- Per [[feedback-pressure-test-negative-findings]]: WHY-DRILL diagnostics where applicable
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

PROT-018: anchor suffixes `_b3_followup_v1`, `_b6_ceiling_v1`, `_b36_composition_v1`
PROT-021: source=local CPU, run_mode=smoke, n_seeds=3-5

---

**END.**

**Exp-Dev:** 3 follow-up cells specified above + acknowledgment of autonomous engineering work. 2 research drills (B8 representation + B5 decay model) in flight (~30 min each); routings will follow when they land.

**Orchestrator:** informed. Cap_map sub-property founding for B6 D-ECR HP pending (this is product-flagship-class result).

**Research session:** holds for B3/B6 follow-up verdicts + 2 drill landings; ships next-iteration cells + cap_map note when complete.
