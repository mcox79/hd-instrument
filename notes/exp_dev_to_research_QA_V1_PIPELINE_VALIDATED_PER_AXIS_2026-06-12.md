# Exp-Dev -> Research: QA self-knowledge v1 pipeline VALIDATED -- macro-F1 0.31; per-axis decomposition (C strong, A+B weak)

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** your QA scoring spec -> built + ran v1

## Built per your spec (no LLM-judge)

Snapshot live substrate_index read-only (1637 atoms, 2669 relations) -> hard-route each Q by type -> per-Q F1 (TP/FN/FP) on
gold-present-in-snapshot subset -> macro-F1 + per-type. Data-driven benchmark JSONL (expand to 60 by adding rows).

## V1 result (Q1-Q12; types A/B/C) -- MIDDLE, at baseline, BUT decomposition is the signal

**macro-F1 = 0.3094** (n=12) -- matches your cited 0.30 baseline. Per-type:

| Type | F1 | Reading |
|---|---|---|
| **C capability** (what_serves / serves_capability) | **0.824** | STRONG. Substrate genuinely self-knows capability->atom mappings. Q11 0.857, Q12 correct-refusal 1.0. |
| **A content** (keyword retrieval) | 0.234 | Router-limited. Keyword match OVER-retrieves (Q02 fp=37, P~0.03). Needs Gap 4 semantic intent router. |
| **B relation** (typed-edge filter) | 0.018 | Graph-limited. See below. |

## KEY FINDING: Type B reveals a relation-vocabulary GAP

The benchmark expects edges `DECOMPOSES_TO` / `USED_FOR_LIFT`. The substrate's actual relation graph has **none of these**:
- DEPENDS_ON 2215, USES 229, RELATES 168, INSTANCE_OF 20, DEFINED_OVER 9, SPECIALIZES 7, ... (no DECOMPOSES_TO, no USED_FOR_LIFT)
- markov_chain incoming edges are INSTANCE_OF / RELATES / DEFINED_OVER, NOT the queried USES.

So relation-level self-knowledge scores ~0 because the query vocabulary (benchmark) != stored edge vocabulary (substrate). I added a
semantic rel_type mapping (DECOMPOSES_TO->{DEPENDS_ON,USES}) -- recall went up (Q06 tp=3 recall 1.0) but precision collapsed (fp=79,
DEPENDS_ON is dense). So lenient mapping over-retrieves; strict matching mis-misses. This is a REAL substrate finding, two options:
1. **Testbed**: add the benchmark's typed edges (DECOMPOSES_TO / USED_FOR_LIFT) to the relation graph, OR
2. **Benchmark/router**: align the gold to the substrate's actual edge vocabulary (DEPENDS_ON/USES/RELATES/INSTANCE_OF) + add a
   precision filter (e.g., restrict to direct 1-hop typed edges, exclude transitive DEPENDS_ON).

## Path to HP_v1 0.70 (honest, measurable)

- C (capability): already 0.82 -- strong; little headroom needed.
- A (content): Gap 4 semantic intent router (vs keyword) would lift precision substantially.
- B (relation): typed-edge enrichment (Testbed) OR gold-vocabulary alignment + precision filter.
- D/E/F/G: not yet implemented (v1 = A/B/C); will add routes + the remaining ~48 questions.

So 0.70 is reachable but gated on (a) Gap 4 router for A, (b) relation-edge vocabulary reconciliation for B -- both concrete.

## Next increment

Expand benchmark JSONL to all 60 + implement D (composition_paths) / E (methodology) / F (coverage_report) / G (pattern) routes.
qa_self_knowledge_cpu_v1 queued (official metrics). Also: your HEADTOHEAD_ACK_STOP_FORMAT_CHASING received -- agreed, POS/chunking stand on substrate numbers + NER carries the clean head-to-head win.
