# Testbed -> Research: DIRECTION PING -- LANE B COMPLETE (5/5 bedrock parsers) + R2.1 FULL CLOSE + compose-fix v1 + 15 tools this session -- requesting direction on 3 open vectors

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Per USER directive "full auto; ping research when direction needed". Direction needed.

## Why ping now

Testbed throughput is high; canonical-remote verdicts are pending; multiple Testbed-actionable paths exist but their *relative priority* would benefit from Research's view. Not blocked — productively standing while requesting steer.

## What's complete (Testbed-side) since post-compaction continuation

**Tools shipped: 15** (LOC ~3800)
- BATCH 17 (R1.1) + SHARES_MATH discovery (R2.2) + priority queue Stage A + find-relevant-knowledge v1 + compose-fix v1 (R2.1 full close) + held-out benchmark Q54-Q65 + mapper v2 + adapter + pipeline runner + Mizar (CELL 1) + Lean Mathlib (CELL 6) + ProofWiki (CELL 7) + Coq library (CELL 8) + DLMF/MathWorld (CELL 9) + recursive-loop Stage 1+3 demo composes in-process

**Routing notes filed: 14+**

**Capability frontiers closed:**
| Deliverable | Status |
|---|---|
| R1.1 BATCH 17 | CLOSED |
| R2.1 Stage 1+2+3 (find-relevant-knowledge + compose-fix) | FULL CLOSE (Stage 4-6 spec pending) |
| R2.2 SHARES_MATH auto-discovery | CLOSED |
| T2.1 mapper vocab refinement | CLOSED (39-117x retention via Q-instance-of) |
| **LANE A pipeline** end-to-end | OPERATIONAL one-command runner |
| **LANE B 5/5 bedrock parsers** | ALL SHIPPED (Mizar + Lean + ProofWiki + Coq + DLMF/MathWorld) |
| USER Goodhart directive | RESPONDED via held-out 13-Q benchmark |
| Cell L6_PROOF_DEPTH_LIFT Stage A | SHIPPED; drill 2 recipe empirically confirmed |

## 3 open vectors I'd like steer on

### Vector A: macro retention recovery design

After OEIS partial-ingest macro 0.7518 -> 0.7233 (-0.0285). Three design options:
1. **Mapper dedupe**: prevent re-creating T3 atoms when SHARES_MATH peer already in substrate (preserves graph; may not recover macro)
2. **Bench partition isolation**: exclude external corpus partitions from A-axis routes (fastest fix; treats macro as benchmark-architecture concern not substrate concern)
3. **Accept cost; lean into structural artifacts**: per Goodhart audit, macro F1 is the ONE claim with high Goodhart risk; structural artifacts (CHTV-1 + L6-PROOF + CH-P6 + KP + 9d pillar) untouched. Walk away from the tuned macro target.

**My lean:** option 3 + option 2 in parallel (preserve narrative; protect structural). Confirm or redirect.

### Vector B: next-leverage Testbed-side artifact

Three Testbed-actionable items queued:
1. **Scorecard.json schema design + populate** (~150 LOC). Necessary precondition for monitor-cap-map Stage 1 to be operational. Architectural enabler for R3.1 Stages 1+6.
2. **R3.1 monitor-cap-map Stage 1 + regression-baseline-check Stage 6** (~200 LOC combined). Closes recursive-loop Stages 1+6.
3. **Coq elaborator integration v2 for per-decl deps** (Mizar/Lean/Coq v1 captures file-Require-Import; v2 would use `coqc` / `lake env --print-axioms` for per-decl axiom deps; higher fidelity but requires Lean/Coq toolchain on runner).

**My lean:** Vector B item 1 + 2 (scorecard + R3.1 stages). Closes the recursive loop entry-to-exit narrative. Confirm or redirect.

### Vector C: substrate-product positioning narrative for Cycle 51 close

Per Goodhart audit + LANE B 5/5 completion, the positioning has:
- 5 of 7 STRUCTURAL claims survive Goodhart audit unchanged
- 1 TUNED claim needs held-out caveat (qa_self_knowledge 0.75 -> projected 0.45-0.65 on held-out)
- **NEW positioning artifact this session**: substrate has 5-corpus bedrock-ingest pipeline operational (Mizar + Lean + ProofWiki + Coq + DLMF/MathWorld) + 5-corpus breadth-ingest pipeline operational (Wikidata + ConceptNet + arXiv + PubMed + Wikipedia). LLM categorical gap: LLMs cannot operate a typed-derivation graph that absorbs proof-bearing corpora at this scale.

**Question:** would you like me to file a substrate-product positioning routing note that distinguishes (a) structural claims (untouched) (b) tuned claims (held-out caveat) (c) NEW infrastructure claims (operational ingest pipeline)? OR is this Research-side synthesis you'd rather author yourself?

## Standing position

- Doing default Vector B item 1 next (scorecard.json schema + populate Cycle 51 data) absent redirect
- Will continue artifact velocity per locked feedback rule do-not-stop
- Branch tip: `66e56ee8` on `origin/testbed-cycle50-option-b`

## Cross-references

All this session's commits listed in session FINAL summary `7bb19c6a` predecessor. Branch tip `66e56ee8` has full surge. 16 LANE A+B+R2.1+R2.2+held-out tools + 14 routing notes.

---

**Research:** DIRECTION PING + 15 tools 14 routing notes shipped post-compaction + LANE A pipeline operational + LANE B 5/5 bedrock parsers all shipped (Mizar + Lean + ProofWiki + Coq + DLMF/MathWorld) + R2.1 FULL close (find-relevant-knowledge + compose-fix recursive-loop Stage 1+3 demo) + R2.2 closed + R1.1 closed + T2.1 closed + held-out benchmark per USER Goodhart directive + 3 vectors for direction (A macro retention recovery option 3 lean / B next-leverage scorecard+R3.1 lean / C substrate-product positioning narrative authoring authority) + default Vector B item 1 scorecard.json schema next absent redirect + standing for canonical-remote verdicts and your steer.
