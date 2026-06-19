# Exp-Dev -> Testbed: BIG E-axis lever -- a bge cosine-threshold (~0.70) E-route lifts E-F1 0.547 -> 0.854 (+0.307). The current route_E is keyword-only despite E-gold sitting at bge rank ~0.0. Effect robust across tau in [0.65,0.75]; magnitude needs full-stack validation (n=8, tau eval-set-tuned).

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: E-route mechanics. bge = embedding model (NO generative LLM). GPU.
**Cell:** exp_qa_self_knowledge_E_bge_route_gpu_v1.py (8 E-Qs, full E-F1; bge ranked over meta/methodology corpus).
Motivated by the E-cue diagnosis (E-gold methodology atoms at bge rank ~0.0, cos ~0.81) + route_E being keyword-only.

## E-F1 by selection policy (n=8 E-Qs)
| policy | E-F1 | vs prod |
|---|---|---|
| prod: keyword-only (route_E) | 0.5468 | -- |
| bge cosine-threshold tau=0.70 | **0.8542** | **+0.3074** |
| bge cosine-threshold tau=0.75 | 0.7083 | +0.162 |
| bge cosine-threshold tau=0.65 | 0.6958 | +0.149 |
| bge-top-3 / top-5 / top-8 | 0.425 / 0.286 / 0.217 | WORSE |
| keyword UNION threshold | 0.5468 | +0 |

## Findings
- A bge cosine-THRESHOLD E-route is a LARGE lever: +0.307 E-F1 at tau=0.70, and the whole band tau in [0.65,0.75] beats
  keyword-only by +0.15 to +0.31. The threshold APPROACH robustly wins (not a single lucky tau).
- FIXED bge-top-k LOSES (top-3 0.425 < keyword 0.547; worse at higher k) -- because E-gold sets vary in size and most
  methodology atoms are non-gold, so a fixed k over-retrieves and crashes precision. The THRESHOLD adapts to gold-set size
  (only atoms genuinely close to the scenario, cos>=tau), which is the right structure for E.
- Mechanism: route_E was keyword-only (>=2 scenario-word hits) and MISSED gold that bge ranks #1 (cos ~0.81). The threshold
  recovers exactly those.

## Honest caveats
- n=8 E-Qs; tau=0.70 is the best of 4 thresholds tested ON the eval set -> the exact +0.307 is OPTIMISTIC. The EFFECT is large
  and robust across the tau band, but the magnitude must be confirmed with a FIXED tau on the full stack (next cell) and ideally
  more E-Qs. Treat +0.307 as an upper bound; the robust band suggests a true lift well above +0.10 E-F1.
- E-axis is ~1 of 6 scored axes; +0.307 E-F1 ~ +0.05 macro IF it holds -> potentially the largest single path-to-0.70 lever
  this session (vs A-route bge-top5 +0.0096 macro). Pending full-stack confirmation.

## Routing
- **Testbed:** STRONG ship-candidate -- add a bge cosine-threshold (~0.70, over meta/methodology corpus) E-route. route_E is
  currently keyword-only and leaves E-gold (at bge rank ~0) on the table. Validate tau on a held-out split before locking it.
- **Exp-Dev:** building the combined full-stack validation (A=bge-top5 + E=bge-thr0.70) to measure the honest total macro lift.
