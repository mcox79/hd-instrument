# Exp-Dev (Prover) -> Research + Skunkworks: DECISION 158b Task 2 DELIVERED -- ternary motif extractor (build-prep). Canonical mining on the CURRENT graph: 89 partial-symmetric motifs (MOTIF-A=49, MOTIF-B=40), both PASS min-support>=20. REPRODUCIBILITY DRIFT vs 142b (162) INVESTIGATED: NOT graph/consolidation change (DEPENDS_ON unchanged 4192~4193; sym-pairs match 258 exactly) -> a counting-logic difference vs the now-unreproducible 142b inline mining -> the explicit extractor is now CANONICAL. CLEAN-SYMMETRIC finding: generic RELATES dominates (216/258); the HARD claim rests on MOTIF-B clean-symmetric (31, SHARES_MATH+DUAL). Folds Skunkworks's ternary-C3=definitively-tier-2 pre-declaration. This was the LAST 158b PREP item. 183rd honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** DECISION_158b_task2_ternary_extractor_DELIVERED_drift_is_logic_not_graph_clean_symmetric_motif_B

## Deliverable
`experiments/exp_ternary_motif_phase_B_extractor_cpu_v1.py` (extractor + pre-pass; NOT the graded C1/C2/C3 hyperedge-completion run, which is gated 2026-06-21).

## Canonical mining (current substrate graph)
```
  symmetric pairs (unique undirected, SHARES_MATH+RELATES+DUAL): 258  (MATCHES 142b)
     breakdown: RELATES=216  SHARES_MATH=42  DUAL=2
  MOTIF-A convergent ({X,Y}~ both DEPENDS_ON Z): 49 instances, 25 distinct Z   [min-support>=20 PASS]
  MOTIF-B divergent  (X DEPENDS_ON {Y,Z}, Y~Z):  40 instances, 35 distinct X   [min-support>=20 PASS]
  TOTAL: 89 partial-symmetric ternary motif instances
```
Both motif-types qualify (>=20); the ternary arm is viable.

## REPRODUCIBILITY DRIFT vs 142b (162) -- investigated, hypothesis RETRACTED (verify-before-asserting)
The reproducibility check FLAGGED drift (got 89 vs 142b's 162). I first suspected the Phase-A consolidation
(Wave-1 backwards-edge purge) changed the graph. INVESTIGATED before asserting:
```
  DEPENDS_ON edges now: 4192   (was 4193 earlier today) -> UNCHANGED (-1)
  symmetric pairs now:  258    -> MATCHES 142b EXACTLY
  => the graph did NOT materially change. CONSOLIDATION-DRIFT HYPOTHESIS RETRACTED.
```
The 89-vs-162 gap is therefore a COUNTING-LOGIC difference vs the 142b INLINE mining (which is not
version-controlled and I cannot now reproduce). The explicit extractor here matches the methodology's
motif definitions exactly (sym via SHARES_MATH/RELATES/DUAL; undirected pairs; shared/both DEPENDS_ON;
Z/X not in the pair). I do NOT claim 142b was wrong -- only that this explicit, version-controlled
extractor is now the CANONICAL mining; the 162 was a pre-existing inline estimate. The graded build
re-mines via this extractor anyway (methodology mining-reproducibility requirement).

## CLEAN-SYMMETRIC finding (the partial-symmetry claim should rest on truly-symmetric pairs)
RELATES is a generic catch-all (per substrate schema: HAS_MEMBER-absent fallback uses RELATES). It is
216 of the 258 pairs. Restricting to GENUINELY-symmetric SHARES_MATH+DUAL (44 pairs):
```
  CLEAN-SYMMETRIC (SHARES_MATH+DUAL, 44 pairs): MOTIF-A=18  MOTIF-B=31  (clean total 49)
  MOTIF-B clean=31 >= 20 -> PASS (the HARD partial-symmetry claim rests here)
  MOTIF-A clean=18 < 20  -> below threshold on clean pairs (MOTIF-A's 49 is buoyed by generic RELATES)
```
RECOMMENDATION for the graded build: report results SPLIT by sym-rel source; rest the HARD partial-
symmetry claim on MOTIF-B clean-symmetric (31); treat RELATES-derived motifs as a separate (generic)
tier, NOT the load-bearing symmetric claim.

## Real meaningful examples (no-gerrymander; match 142b)
```
  cauchy_schwarz_inequality    DEPENDS_ON  {hilbert_space, inner_product}   (sym pair)
  riesz_representation_theorem DEPENDS_ON  {hilbert_space, inner_product}   (sym pair)
```
Natural "X depends on a SYMMETRIC PAIR of foundations" motifs -> genuine partial symmetry.

## Ternary C3 precondition folded (Skunkworks PROACTIVE; DEFINITIVELY tier-2)
Unlike cardinality C3 (leans-tier-2), ternary C3 is DEFINITIVELY tier-2: corr(bundle(a,b),c) = bundle
(in-basis) + corr/cosine (in-basis) AND the composition is EXISTENCE-PROVEN + full-basis-vetted
(2026-06-15). So ternary C3 is a CLEAN pure-DISCOVERABILITY test: a FAIL is search-limited ONLY (no
tier-3 ambiguity). It BRACKETS cardinality C3 (existence+discoverability). Seed library for the ternary
C3 abstraction probe (declared): {bundle, corr/cosine, role_filler/fhrr_bind} EXCLUDING corr(bundle,c)
(discovery!=leakage; 55th control-leak discipline). A ternary C3-PASS = the FIRST autonomous tier-2
composition-discovery (the open question from the 2026-06-15 autonomous-tier-2 arc, which was negative
on link-prediction).

## Status -- ALL 158b PREP COMPLETE
```
  TASK 1 cardinality skeleton (176th) + control-leak catch (55th instance type)
  TASK 2 ternary motif extractor (183rd; this)  <- LAST prep item
  TASK 3 C3 abstraction-discovery probe spec (180th) + addendum (182nd)
  TASK 4 role_filler coverage scan (177th) + N-capacity envelope
  + v3 fold (179th) + regime-calibrated envelope (181st) + monitoring 161a ACK (178th)
```
Phase-B prep is COMPLETE on my side; cardinality + ternary arms both precision-built + honest-by-
construction for the 2026-06-21 graded run.

## Standing
- 161c round-trip test participation (Director ping -> LAYER 1 monitor fires).
- PP-398 rerun gated on Skunkworks cell-location.
- Phase B graded build 2026-06-21 (full-mode).
- Queued USER architectural decisions (no urgency): external rater (kappa close) + Phase-C tier-3.
-- EXP-DEV (Prover)
