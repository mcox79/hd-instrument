# Research -> Exp-Dev: Priority 1 untested compositions (per composition matrix)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Source:** composition_matrix.md identifies 7 Priority 1 untested compositions; 5 specified below as load-bearing next tests

---

## Strategic context

Per the just-built composition_matrix.md: **14% → 17%** of 66 possible compositions tested. 7 Priority 1 untested compositions identified as highest-EIG.

Per [[feedback-no-padding-experiments]]: each cell discriminates a specific composition principle. Per shared-axis drill: orthogonal composition predicted superadditive on right metric; same-axis subsumed.

5 cells specified below cover the highest-leverage Priority 1 untested compositions.

---

## Cell P1: SQ2 x cf-RPE composition (reasoning + task-gating)

**Anchor:** `substrate_sq2_x_cfrpe_composition_v1_n4096`

### Architecture
- Substrate at N=4096 with cf-RPE rank-1 substitution + iterated retrieval (Mode 4)
- Task: 5-class chain task at K=12 hops (same as SQ2 baseline)
- Measure: K-hop retrieval accuracy with cf-RPE applied during iterated query

### Pre-reg
- **HP:** cf-RPE preserves K=12 accuracy 100% (no degradation; possibly improves consolidation)
- **MIDDLE:** K=12 accuracy 80-100% (slight degradation; cf-RPE adds task noise)
- **HF:** K=12 accuracy < 80% (cf-RPE filtering breaks iterated retrieval)

### WHY-DRILL on HF
- Measure: does cf-RPE filter relevant chain links during iteration?
- Fix: apply cf-RPE only to terminal retrieval, not iteration

### Resource + cost
$0 CPU. ~10-15 min wall. Reuses SQ2 + Bundle A cf-RPE scaffolds.

### Strategic
Tests: does cf-RPE (task axis) preserve substrate's flagship reasoning capability (Mode 4 NC1 escape)? Orthogonal axes (task + iteration); predicted superadditive composition.

---

## Cell P2: SQ2 x Hierarchical composition (multi-substrate reasoning)

**Anchor:** `substrate_sq2_x_hierarchical_reasoning_multi_substrate_v1_n2048_K10`

### Architecture
- 10 parallel sub-substrates at N=2048 each (B4 ensemble)
- Each sub-substrate stores chain relations + supports iterated retrieval
- Hierarchical aggregator combines retrieval results
- Test K=12 hops across multi-substrate aggregation

### Pre-reg
- **HP:** ensemble retrieves K=20+ hops (predicted multiplicative reasoning capacity)
- **MIDDLE:** K=12-20 hops (matches single substrate; no multiplicative gain)
- **HF:** K=12 < single-substrate accuracy (hierarchical breaks reasoning)

### WHY-DRILL on HF
- Sub-substrate output aggregation may break chain continuity
- Fix: chained iterated retrieval (sub-substrate i hands result to sub-substrate i+1)

### Resource + cost
$0 CPU. ~15-20 min wall.

### Strategic
Tests: does substrate reasoning scale multiplicatively with hierarchical aggregation? Combines two flagship capabilities (SQ2 + hierarchical). Predicted SUPERADDITIVE per orthogonal axes.

---

## Cell P3: B6 x SQ2 composition (audit-preserving reasoning chains)

**Anchor:** `substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096`

### Architecture
- Substrate at N=4096 with chain task at K=12 hops + D-ECR audit eviction
- At each iteration step: check D-ECR doesn't evict chain links
- Measure: K=12 accuracy + deletion-cert preservation during reasoning

### Pre-reg
- **HP:** K=12 accuracy AND deletion-cert preservation > 95% across reasoning chain
- **MIDDLE:** K=12 accuracy with deletion-cert preservation 70-95%
- **HF:** D-ECR evicts chain links; K=12 accuracy degrades

### WHY-DRILL on HF
- D-ECR may evict by energy that doesn't reflect chain importance
- Fix: chain-aware eviction (preserve patterns that are queried recently)

### Resource + cost
$0 CPU. ~10-15 min wall.

### Strategic
Tests: substrate's flagship audit (B6) preserves substrate's flagship reasoning (SQ2). Critical for product narrative: "auditable reasoning at K=12 hops."

---

## Cell P4: Position-binding x B2 composition (sequence + capacity)

**Anchor:** `substrate_posbind_x_b2_sparse_sequence_capacity_v1_n8192`

### Architecture
- Substrate at N=8192 with DG sparse-expansion (f=0.02) + position-binding (multi-bank addressing)
- Sequence storage: K=8 extended context per Bundle E E1 scaffold
- Test: capacity for sequence storage at sparse encoding

### Pre-reg
- **HP:** sparse+position-binding stores >= 10x sequences vs dense+position-binding at same N
- **MIDDLE:** 3-10x capacity boost
- **HF:** < 3x boost (sparse + position-binding don't compose multiplicatively)

### WHY-DRILL on HF
- Sparse representations may conflict with position-binding overlap
- Fix: separate sparse positions from sparse content

### Resource + cost
$0 CPU (Wikitext-2 char-LM or Shakespeare fallback). ~15-20 min wall.

### Strategic
Tests: both validated (B2 capacity + position-binding sequence); composition predicted MULT per shared-axis (different axes). Sequence + capacity orthogonal.

---

## Cell P5: STDP x B2 composition (sequence ordering + capacity)

**Anchor:** `substrate_stdp_x_b2_sparse_sequence_storage_v1_n8192`

### Architecture
- Substrate at N=8192 with DG sparse-expansion (f=0.02) + STDP-asymmetric
- Sequence storage tests order-encoding capacity at sparse representation
- Bundle E E2 anchor for STDP at trigram

### Pre-reg
- **HP:** sparse+STDP gives >= 5x sequence-storage capacity over dense+STDP at same N
- **MIDDLE:** 2-5x boost
- **HF:** < 2x (STDP order-encoding doesn't benefit from sparsity)

### WHY-DRILL on HF
- STDP relies on temporal correlations; sparse representations may break correlations
- Fix: temporal-aware sparse encoding (preserve order-relevant components)

### Resource + cost
$0 CPU. ~15-20 min wall.

### Strategic
Tests: both validated (B2 + STDP); predicted MULT per orthogonal axes (capacity + temporal sequence). Different gain axes per shared-axis taxonomy.

---

## Priority + sequencing

Build cheapest + highest-information first:

1. **Cell P1 (SQ2 x cf-RPE)** — ~10-15 min; tests flagship reasoning composition
2. **Cell P3 (B6 x SQ2)** — ~10-15 min; product narrative anchor for auditable reasoning
3. **Cell P4 (Position-binding x B2)** — ~15-20 min; sequence + capacity composition
4. **Cell P5 (STDP x B2)** — ~15-20 min; counterpart to P4
5. **Cell P2 (SQ2 x Hierarchical)** — ~15-20 min; multi-substrate reasoning

Total: ~65-90 min CPU for all 5 cells. $0.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: each cell discriminates specific composition principle
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF with WHY-DRILL per cell
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU all 5 cells
- ASCII-only

PROT-018: `_p1_v1` through `_p5_v1` suffixes per cell
PROT-021: source=local CPU + remote CPU, run_mode=smoke/full, n_seeds=3

---

**END.**

**Exp-Dev:** 5 Priority 1 composition tests specified. Total ~65-90 min CPU; $0. Each test discriminates a specific composition principle. When verdicts land: composition_matrix.md auto-updated per system protocol (coverage 17% -> 24%).

**Research session:** 2 drills dispatched in parallel (sparse-coding-compressed-sensing D-RIP unification + Wright-Fisher / Kimura population genetics first-scheduled branch axis). Standing for these + composition test verdicts + Tier 6 Phase D + Tier 4 substitution + ongoing pipeline. ~20 min cadence continues.
