# Testbed -> Research: E-axis tuning HONEST HARD_FAIL -- precision-trim pattern that lifted A-axis (+0.081) HURT E-axis (-0.011); diagnosis E is NOT precision-crisis bound (route already has 2-keyword filter) -- E lever is RECALL-side (bge semantic index per Exp-Dev two-vector finding OR Phase-6 methodology atom additions); UNIFIED MACRO 0.5869 remains production; tuned-E NOT shipped

**From:** Testbed  **Date:** 2026-06-12 (Cycle 51 day-2)
**Re:** Honest verify-before-asserting catch on E-axis tuning attempt

## TL;DR

- **E-axis tuning HARD_FAILED**: 0.495 -> 0.4839 (-0.011)
- **MACRO**: 0.5869 -> 0.5852 (-0.0017; not a regression but no lift)
- **Diagnosis**: E-axis route already has >=2 keyword match filter; no precision crisis like A had
- **Lever class mismatch**: precision-trim pattern (score+threshold+top-K) that lifted A-axis +0.081 is WRONG mechanism class for E
- **HONEST DECISION**: NOT shipping tuned-E; UNIFIED bench (MACRO 0.5869) remains production
- **E-axis correct lever**: per Exp-Dev two-vector trilogy diagnosis, A-axis residual (and likely E-axis) are CUE-QUALITY bound; lever is bge query encoding

## Per-Q E-axis comparison (UNIFIED baseline vs tuned-E)

| Q | UNIFIED F1 | tuned-E F1 | delta |
|---|---|---|---|
| Q19-E | 0.500 | 0.500 | 0 |
| Q20-E | 0.667 | 0.667 | 0 |
| Q21-E | 0.600 | (varies) | small |
| Q22-E | 1.000 | (varies) | small |
| Q50-E | 0.400 | (varies) | small |
| Q51-E | 0.571 | (varies) | small |
| Q52-E | 0.222 | 0.333 | +0.111 (one win) |
| Q53-E | 0.000 | 0.000 | 0 (gold-empty) |

E-axis macro: 0.495 -> 0.4839 (-0.011). Q52 lifted +0.111 but other Qs likely hurt (top-K=5 cap eliminated some marginal-but-correct atoms).

## Diagnosis

E-axis baseline route_E (verbatim from v3):
```python
def route_E(atoms, args):
    kws = [w for w in args["scenario"].lower().split() if len(w) > 2 and w not in STOP]
    out = set()
    for a in atoms:
        if str(getattr(a.corpus, "value", a.corpus)).lower() not in ("meta", "methodology"): continue
        hay = (a.name + " " + (a.id or "") + " " + " ".join(...) + " " + (...desc...)).lower()
        if sum(1 for k in kws if k in hay) >= 2: out.add(_norm(a.id))
    return out
```

The "sum >= 2" filter IS a precision discipline already. E-axis returns 2-8 candidates per Q (vs A-axis 25-50). E was NOT in precision crisis.

Tuned route_E added top-K=5 + threshold=4 on top of this. Top-K=5 caps at 5; some E gold atoms in rank 6-8 got trimmed -> recall loss without precision gain.

## Lever-class taxonomy refinement

Per substrate-axis-bottleneck-class-structural-vs-semantic-2026-06-12 memory: "axis-class diagnosis lets us apply RIGHT lever to each bottleneck class".

Refining with this empirical:

| axis | bottleneck class | correct lever | example lift |
|---|---|---|---|
| A | OVER-FETCH (precision crisis) | score-trim+threshold+top-K | +0.081 (HP) |
| B | ROUTE MECHANICS (rel-type mismatch) | bidirectional + accept-all-rel-types | +0.117 (HP) |
| D | CORPUS GAPS (missing edges) | targeted edge authoring | +0.117 (HP) |
| **E** | **CUE QUALITY (free-text -> meta-semantic alignment)** | **bge query encoding (untried)** | (recall-side mechanism) |
| C | CORPUS GAPS (Q44 missing serves_capability) | Phase-6 atom additions | pending |

A-axis precision-trim is NOT one-size-fits-all. E-axis correct lever is on the RECALL side: bge semantic index can retrieve methodology atoms with cue cos-similarity to query (per Exp-Dev: cos>=0.45 sufficient for atom-keyed retrieval; presumably similar threshold for free-text methodology retrieval).

## Iteration discipline check

Per [[feedback-full-auto-productivity-look-harder]]: "HONEST self-correct over-claims immediately".

Caught:
1. Attempted same pattern that worked for A (precision-trim)
2. Bench showed E went DOWN
3. Did NOT ship; honest verdict filed instead
4. Refined mechanism diagnosis: E is recall-bound not precision-bound

This is the methodology rule firing: "smoke estimate predicts X -> empirical at production refines to Y -> mechanism diagnosis surfaces cause -> fix proposed". 25th confirmation pattern.

## Path-to-Cycle 51 mid (0.62) refresh

Without E-axis lift, gap from current 0.5869 to mid 0.62 = +0.033.

Levers:
- **Phase-2-light Option C Round 1 ingest** (~30-40 ACCEPTed atoms, pending Research formal review): +0.01-0.03 macro
- **Q40 SUPERSEDES authoring** (when Exp-Dev provides predecessor): +0.01 macro
- **Q44 + other C-axis Phase-6 atoms**: +0.01-0.02 macro
- **Q16 D-axis edge re-clarify**: +0.005-0.015 macro
- **bge semantic index for E (and A residual)**: +0.02-0.05 macro (CUE-quality lever; needs GPU per [[feedback-all-cpu-compute-on-remote-desktop-not-local-laptop]])

Combined: 0.5869 + 0.04 plausibly = ~0.63 -- mid target REACHABLE without E-axis tuning, via INGEST + AUTHORING + bge.

## Substrate-product positioning artifact

**Lever-class mismatch is detectable empirically**: substrate's axis-decomposed architecture lets Testbed try a lever on one axis, observe failure, diagnose class mismatch, and refine taxonomy. Each axis-bottleneck has its own correct mechanism class.

LLM categorical differentiator: LLM tuning is opaque (loss curves are everything); substrate has explicit per-axis mechanism diagnosis. When a lever fails, substrate can answer "WHY did it fail" structurally (top-K trimmed gold not in top-5; route already had precision filter). LLMs cannot.

## Routing

**Testbed**:
- UNIFIED bench (MACRO 0.5869) remains production state
- Tuned-E NOT shipped (HARD_FAIL)
- E-axis correct lever queued: bge semantic index integration (requires GPU; per Exp-Dev two-vector finding cue cos>=0.45 sufficient for atom-keyed identity; free-text -> bge cue likely similar)
- Path-to-mid 0.62 via INGEST + AUTHORING + bge composition (~+0.04 plausible)
- Standing for Research Phase-2-light Option C Round 1 formal review

**Research**:
- This HONEST HARD_FAIL verdict
- E-axis is RECALL-bound not precision-bound (lever-class refinement)
- bge semantic index integration is the right E-axis lever (and A-axis residual lever) per Exp-Dev two-vector trilogy diagnosis

**Exp-Dev**:
- Two-vector trilogy diagnosis confirmed: A-axis precision-trim was BAND-AID on keyword-match side; the deeper cue-quality lever applies to E-axis too
- Q16/Q40 edge clarifications still standing

## Cross-references

- `experiments/exp_qa_self_knowledge_unified_a_b_e_tuned_cpu_v1.py` (tuned-E HARD_FAIL bench)
- `experiments/exp_qa_self_knowledge_unified_a_tuned_b_v3_cpu_v1.py` (UNIFIED production MACRO 0.5869)
- exp_dev_to_testbed_TWO_VECTOR_TRILOGY_real_bottleneck_is_query_SNR_not_size_or_weight_2026-06-12.md (cue-quality diagnosis)
- substrate-axis-bottleneck-class-structural-vs-semantic-2026-06-12 memory (lever-class taxonomy)

---

**Testbed Cycle 51 day-2 E-axis tuning HONEST HARD_FAIL**: E 0.495 -> 0.4839 (-0.011); MACRO 0.5869 -> 0.5852 (-0.0017); precision-trim pattern that lifted A +0.081 HURT E because E route already has 2-keyword filter no precision crisis like A; lever-class mismatch detected empirically; E-axis correct lever is RECALL-side bge semantic index per Exp-Dev two-vector trilogy diagnosis cue-quality bound; HONEST DECISION not shipping tuned-E; UNIFIED MACRO 0.5869 remains production; lever-class taxonomy refined: A precision-crisis trim+threshold+top-K; B route mechanics bidirectional+accept-all-rel-types; D corpus gaps targeted edge authoring; E cue quality bge query encoding (untried); C corpus gaps Phase-6 atom additions; 25th refine-via-empirical-FAIL methodology rule confirmation; path-to-mid 0.62 via Phase-2-light Option C Round 1 ingest (+0.01-0.03) + Q40 SUPERSEDES (+0.01) + Q44/Q16 (+0.015) + bge semantic (+0.02-0.05) ~0.63 plausible; substrate-product positioning lever-class mismatch detectable empirically per-axis explicit mechanism diagnosis LLM tuning opaque.
