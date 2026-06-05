# Substrate Composition Matrix

**Explicit tracking of which capabilities compose with which.** Living document; update per composition test verdict.

**Created:** 2026-06-04 per continuous-exploration system design 2x drill
**Cell legend:** MULT (multiplicative) / SUPER (superadditive) / ADD (additive) / SUB (subsumed/collinear) / HARM (combined worse than alone) / UNTESTED / CONDITIONAL (works under specific conditions)

---

## Composition axes

Per shared-axis taxonomy (today's drills):
- **Capacity** (ceiling expansion / pattern storage): B2 DG sparse, B4 ensemble, Hierarchical aggregator, Modern Hopfield p=4 (untested)
- **Task-supervised** (write filtering / supervised signal): cf-RPE, B3a top-K gating, Drosophila MB sparse f=0.05
- **Capacity-management** (alpha control): B3b exp-smoothed surprise (input-side), B6 D-ECR (output-side)
- **Sequence** (temporal/order): Position-binding, STDP-asymmetric
- **Compositional** (depth): L=10000 stacked W

---

## Matrix (12 validated bio-primitives + composition principles)

|  | B2 sparse | B3a gating | B3b surprise | B4 ensemble | B6 D-ECR | B8 logit-residual | cf-RPE | DG f=0.05 | Hierarchical | Position-binding | STDP-asym | SQ2 iter-retr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **B2 sparse** | self | UNTESTED | UNTESTED | **MULT (100x)** | **SUB** | UNTESTED | UNTESTED | UNTESTED | **MULT (125k)** | **HF (1.0x; sparse no help for sequence)** | UNTESTED | UNTESTED |
| **B3a gating** | UNTESTED | self | **SUB-MULT (16x; MIDDLE)** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| **B3b surprise** | UNTESTED | **SUB-MULT (16x; MIDDLE)** | self | UNTESTED | **SUB (single-stream); SUPER (mixed-stream HP)** | UNTESTED | INVERTS (drill) | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| **B4 ensemble** | **MULT (100x)** | UNTESTED | UNTESTED | self | UNTESTED | UNTESTED | UNTESTED | UNTESTED | **MULT** | UNTESTED | UNTESTED | UNTESTED |
| **B6 D-ECR** | **SUB** | UNTESTED | **SUB (single); SUPER (mixed)** | UNTESTED | self | UNTESTED | UNTESTED | UNTESTED | **MULT** | UNTESTED | UNTESTED | UNTESTED |
| **B8 logit-residual** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | self | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| **cf-RPE** | UNTESTED | UNTESTED | INVERTS | UNTESTED | UNTESTED | UNTESTED | self | **ADD (Bundle A)** | UNTESTED | UNTESTED | **SUPER (3/5 seeds)** | UNTESTED |
| **DG f=0.05** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | **ADD (Bundle A)** | self | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| **Hierarchical** | **MULT (125k)** | UNTESTED | UNTESTED | **MULT** | **MULT** | UNTESTED | UNTESTED | UNTESTED | self | UNTESTED | UNTESTED | UNTESTED |
| **Position-binding** | **HF (1.0x; sparse-modality-specific)** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | self | **HP at trigram (Bundle E E1/E2)** | UNTESTED |
| **STDP-asym** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | **SUPER (3/5)** | UNTESTED | UNTESTED | **HP (E1/E2)** | self | UNTESTED |
| **SQ2 iter-retr** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | **HP (audit-preserving reasoning; K=12 + del-cert at capacity)** | UNTESTED | **HP (preserved K=12)** | UNTESTED | **HP MULT (24-hop at 2x alpha_c)** | UNTESTED | UNTESTED | self |

---

## Untested composition priority (high information value)

### Priority 1 (highest expected information gain)

- **SQ2 x cf-RPE** — reasoning + task gating; does cf-RPE preserve SQ2 K=12 capability?
- **SQ2 x Hierarchical** — multi-substrate reasoning; predicted multiplicative reasoning capacity
- **B6 x SQ2** — audit-preserving reasoning chains; combines flagship audit with flagship reasoning
- **Position-binding x B2** — sequence + capacity; both validated; untested combined
- **STDP x B2** — sequence + capacity; both validated; untested combined
- **B8 x SQ2** — sparse residual + iterated retrieval; tests Mode 4 + capacity compression
- **EFFICIENCY composition** (B3a x B3b x DeltaNet on wall-to-target-BPC) — counterpart to capacity MULT

### Priority 2

- **cf-RPE x Hierarchical** — task gating at hierarchical scale
- **Position-binding x Hierarchical** — multi-substrate sequence encoding
- **STDP x Hierarchical** — multi-substrate sequence
- **B2 x SQ2** — sparse capacity + reasoning at K=12
- **B4 x SQ2** — ensemble reasoning
- **B8 x cf-RPE** — sparse residual + task gating

---

## Confirmed composition rules (today)

1. **Same-axis (capacity)** → SUBSUMED (B2 + B6; B3b + B6 single-stream)
2. **Same-axis (parallel capacity within hierarchical)** → MULTIPLICATIVE (B2 x B4 x hierarchical = 125k patterns HP; full N=2048 confirmed)
3. **Heterogeneous (task + temporal)** → SUPERADDITIVE at 3/5 (cf-RPE x STDP)
4. **Heterogeneous (sequence + sequence)** → HP at trigram (position-binding + STDP)
5. **INPUT-REGIME SPECIFICITY** → B36-MIXED-stream SUPERADDITIVE (50% redundant + 50% novel); B3b filters redundant + B6 evicts novel; complementary
6. **Efficiency same-axis-with-overlap** → SUB-MULTIPLICATIVE (B3a x B3b = 16x; > best-single but gates overlap; not full product)
7. **METRIC must match axis** — capacity primitives on M_crit; efficiency on wall-to-target; not BPC

---

## Mixed-stream composition CONFIRMED (per B36-mixed HP 2026-06-04)

For B3b + B6 (input-filter + capacity-correction):
- Single-stream: SUBSUMED
- **Mixed-stream (50% redundant + 50% novel patterns): SUPERADDITIVE HARD_PASS**
- gains: gate=+0.01, evict=-0.06, both=+0.19 >> sum
- B3b filters redundant; B6 evicts novel; complementary

INPUT-REGIME SPECIFICITY is a validated composition principle.

---

## Update protocol

- Per composition test verdict: update matrix cell
- New primitive added to scorecard: add row + column to matrix; default UNTESTED
- LVH catches: update with honest read; note in cell
- Periodic: every 24-48h, scan UNTESTED Priority 1 cells; dispatch cheapest informative test

**Total tested compositions: 11 (of 66 possible pairs) = 17% coverage**
**Priority 1 untested: 7 high-EIG compositions**

## Recent updates (per system protocol)

- 2026-06-04 20:42: B36-MIXED-stream SUPERADDITIVE HP confirmed (input-regime-specificity validated)
- 2026-06-04 20:42: B3a x B3b SUB-MULTIPLICATIVE MIDDLE (16x; gates overlap on high-error examples)
- 2026-06-04 20:42: Capacity multiplicative full N=2048 GPU HP at 125k patterns (confirmed from smoke)
