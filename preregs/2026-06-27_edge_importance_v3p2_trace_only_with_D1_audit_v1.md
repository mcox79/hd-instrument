# Prereg: edge_importance_v3p2_trace_only_with_D1_audit_v1

Date: 2026-06-27
Anchor: edge_importance_v3p2_trace_only_with_D1_audit_v1
Cell: experiments/exp_edge_importance_v3p2_trace_only_with_D1_audit_v1.py
Primitives composed:
  - hdlab/edge_importance.py (chain-grade; 2026-06-26)

## Motivation (drill 2026-06-27 ANGLE 3 finding)

v3 ULTRA composition collapsed to ZERO coreness atoms across all 3 seeds
(synthetic threshold too tight). v3.1 loosened ULTRA_COS 0.85 -> 0.70 +
MIN_SIZE 5 -> 3; synthetic selftest at sigma=0.02 passes (cosines 0.91+)
but on the REAL substrate atom geometry at ULTRA_COS=0.7 / MIN_SIZE=3 we
get coreness_atoms=0 across all seeds again. Real cluster geometry is
LOOSER than the synthetic test predicted.

Per drill (notes/research_drill_edge_importance_complementary_angles_3x_
2026-06-27.md): SHIP HONEST-BOUND + ENSEMBLE rather than chase ULTRA
composition further. The D1 audit (exp_edge_importance_v3_D1_alternative
_discriminators_v1) showed TRACE-only alone hits D1_AUC=1.000 (perfect
ranking under partition-AUC scoring) with cv=0.000 across seeds. The
ULTRAMETRIC composition adds no signal on real substrate -- drop it.

## v3.2 mechanism (TRACE-only)

```
importance_score[atom] = retrieval_trace_score[atom]
```

- `retrieval_trace_score[atom]` = per-atom cleanup-argmax hit counter
  during composite-query operation (brain STC analog).
- Pruning: prune LOWEST-importance N_PRUNE atoms (same as v3 / v3.1).
- No ULTRA arm; no composition arm. TRACE-only is the primary mechanism.

## Regime (inherits v3/v3.1)

- N = 512, M_OLD = 600, M_RECENT = 400, alpha = 1.953
- J_composite = 3000, arity = 3, USE_FRAC = 0.40, N_USE = 240
- DOWNSCALE_SCALE = 0.20, N_PRUNE_FRAC = 0.30
- SEEDS = [7, 17, 23], N_QUERIES = 200 per subset per arm

## Arms (2 mandatory)

- ARM_BASELINE_RANDOM_IMPORTANCE -- random importance (control rail)
- ARM_TRACE_ONLY                  -- importance = retrieval_trace_score
                                     (the mechanism; primary verdict)

## Primary discriminators (D1 audit; from D1 cell)

D1: partition AUC -- atoms-by-retrieved-vs-unretrieved labels, AUC of
  importance ranking.
D2: top-K precision at K=N_USE (240) and K=50 -- fraction of top-ranked
  atoms that are retrieved.
D3: KM-proxy quantile gap top-10% vs bot-10% importance -- robust
  separation metric.

## Pre-reg bands (load-bearing; from drill recommendation)

### HARD_PASS (all must hold across 3 seeds)
- TRACE D1_partition_AUC mean >= 0.65 across 3 seeds
- TRACE D1_AUC cv <= 0.05 across 3 seeds (stability)
- TRACE D1_AUC - RAND D1_AUC >= 0.05 (lift over random baseline)
- mechanism fires (n_downscaled > 0 in TRACE arm)
- cor(importance, |W|) < 0.30 (USER fairness gate)

### MIDDLE_BAND
- TRACE D1_AUC >= 0.55 (above-chance ranking) AND cv <= 0.10 AND
  mechanism fired; full PASS bands not all cleared.

### HARD_FAIL (any one trips)
- Both arms within 0.05 of each other on D1_AUC (saturation)
- cor(importance, |W|) >= 0.30 (fairness regression)
- n_downscaled == 0 in TRACE arm (mechanism inert)
- H_n_edges < 50 (workload did not populate H)
- TRACE D1_AUC < 0.55 (mechanism does NOT rank retrieved above
  unretrieved)
- any caught exception (META_RULE_J no-silent-except)
- META_RULE_H cardinality_ok breach (per-seed arm count != 2)

## Substrate-only-decode gate

n_llm_calls = 0 by structural-guarantee. Decode is sign(W @ key) cosine
cleanup against value matrix.

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`.

## New disciplines applied

- META_RULE_H cardinality_ok: per-seed expected arm count = 2.
- META_RULE_J no-silent-except: setup + each arm wrapped; any exception
  RECORDED + HARD_FAIL.
- META_RULE_K smoke fires discriminator: smoke must produce
  trace_total > 0 AND H_n_edges >= 50 AND mean D1_AUC strictly above
  0.5 baseline.
- META_RULE_L band-floor strictly-above-floor (use > and >=, not just
  "in band").

## Composition rationale (why drop ULTRA)

Drill ANGLE 1 finding: TRACE-only alone hits D1_AUC=1.000 with perfect
top-K precision. ULTRAMETRIC adds no MEASURED signal because real
substrate geometry doesn't form tight bipolar clusters under cosine.
HONEST-BOUND ship: TRACE-only is the chain-grade-evidence mechanism;
ULTRA composition was speculative and degenerate.

Future work (NOT this cell): if a substrate-native clustering geometry
emerges (e.g., NREM-replay produces measurable cluster manifolds),
revisit composition with the REAL geometry as the basis for the
selftest -- not synthetic sigma=0.02 mock data.

## ASCII-only; no unicode; no emojis; no em-dashes.
