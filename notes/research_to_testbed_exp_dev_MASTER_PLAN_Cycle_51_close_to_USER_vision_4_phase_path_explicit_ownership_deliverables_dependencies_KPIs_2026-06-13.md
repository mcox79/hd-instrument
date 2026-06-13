# Research -> Testbed + Exp-Dev: MASTER PLAN Cycle 51 close to USER vision -- 4-phase path with explicit ownership + deliverables + dependencies + cost estimates + KPIs per session

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** USER directive "you're guiding this process you need clear plan"

## Plan structure

Four phases ordered by USER vision leverage (substrate-on-all-knowledge + LLM-class language mastery + recursive self-improvement loop). Each phase has:
- Explicit owner per work item
- Deliverable + cost estimate
- Dependencies (what must ship first)
- KPI / HARD-PASS gate
- Phase exit criteria (when to roll to next phase)

## Current state (anchor)

- HP_v1+ 0.75 HARD-PASS (path-to-HP_v1+ HIT 2 days early)
- L6-PROOF prover narrative COMPLETE: CHTV-1 verifier (1.0 precision) + L6-PROOF FINDER (20/20 sound) + CH-P6 capstone (substrate 0 false-accepts vs Qwen-0.5B 3/12 hallucinated)
- 144 T1 algebra atoms + BATCH 15 depth-2 + BATCH 16 supplementary INGESTED
- CELL KP P1 frequency-promotion HARD-PASS (24 T3->T2 candidates surfaced)
- 4.37M facts + 29.5GB bge-vectorized READY to ingest
- 8d mathematical-foundation pillar STANDS post-F4 re-spec
- 24+ substrate-product positioning artifacts
- LFS migration P0.3 handed to Testbed (USER authorized; Research attempt failed at 49% no corruption)

## PHASE 1 (NOW -- next 24 hours): UNBLOCK + KP path P2 + BATCH 17 depth-3+4

### Testbed work items

| # | Item | Cost | Dependencies | KPI |
|---|---|---|---|---|
| T1.1 | LFS migration P0.3 (Option A/B/C from prior handoff) | 1-2h | USER authorized | force-push succeeds; LFS ls-files populated |
| T1.2 | extract-from-facts COMMON MAPPER implementation per Research skeleton | 1-2 days build | LFS unblock | mapper runs on 1 corpus end-to-end; pre-reg <50MB shards |
| T1.3 | Promote 24 T3->T2 candidates per CELL KP P1 verdict | 30 min ingest | none | 1844 -> 1868 atoms; substrate retains 0.75+ macro post-promotion |

### Exp-Dev work items

| # | Item | Cost | Dependencies | KPI |
|---|---|---|---|---|
| E1.1 | CELL KP path P2 (DRUM/NeuralLP differentiable rule mining) build + run | ~2 days build + 4h CPU | none | >= 20 rules confidence >= 0.7 mined; >= 5 left-side predicates promoted to T1 axiom-candidate; CHTV-1 verifies at 1.0 |
| E1.2 | Standing for KP P3 SHARES_MATH gating + P4 sleep-replay approximation design | per E1.1 verdict | KP P1 + BATCH 17 ingest | n/a (design phase) |

### Research work items (mine)

| # | Item | Cost | Dependencies | KPI |
|---|---|---|---|---|
| R1.1 | BATCH 17 depth-3+depth-4 recursive DEPENDS_ON authoring (~150 edges; targets 62% authoring-gap-leaf per L6-PROOF FINDER depth caveat) | 2-3 hours | none (corpus already filed) | filed to Testbed; L6-PROOF FINDER avg depth 1.3 -> 2.5+ projected post-ingest |
| R1.2 | Memory entries for CH-P6 capstone + CELL KP P1 + 3x drill knowledge promotion operator finding | 30 min | none | 3 memory files filed |
| R1.3 | Honest re-baseline 9 macro after BATCH 15+16+17 ingest (when stable) | 15 min | BATCH 17 ingest | re-baseline macro logged |

### Phase 1 exit criteria

- LFS migration COMPLETE + force-push successful
- COMMON MAPPER end-to-end on 1 corpus
- KP path P2 HARD-PASS or MIDDLE verdict
- BATCH 17 filed
- 24 T3->T2 promotion ingested

Roll to Phase 2 when all 5 criteria met OR 24h elapsed (whichever later).

## PHASE 2 (NOW+24-72h): FIRST CORPUS INGEST AT SCALE + KP P3+P4 + L6-PROOF depth jump

### Testbed work items

| # | Item | Cost | Dependencies | KPI |
|---|---|---|---|---|
| T2.1 | First mapper run: wikidata_truthy_50m --filter math/science | 6-12h | T1.2 mapper ship | ~340K-3.4M atoms added; substrate ~2-5M total |
| T2.2 | Second mapper run: conceptnet_8m --filter all | 1-2h | T2.1 | ~458K atoms added |
| T2.3 | Promote BATCH 17 + verify L6-PROOF FINDER depth jump | 30 min eval | R1.1 ingest | avg proof depth 1.3 -> 2.5+ |

### Exp-Dev work items

| # | Item | Cost | Dependencies | KPI |
|---|---|---|---|---|
| E2.1 | CELL T1 triple-to-VSA encoding A/B test (HRR vs FHRR vs GHRR) | 30 min CPU | substrate has primitives | per-triple cleanup recall @10 + 242-atom-break per encoder logged |
| E2.2 | CELL KP path P4 sleep-replay consolidation (approximated per E1 design) | ~1 day build + 4h CPU | T2.2 ingest | 1000-atom replay produces T2 cortical reps; cleanup-recall vs original >= 0.80 @ K=5 |
| E2.3 | L6-PROOF FINDER re-run post BATCH 17 ingest | 30 min | T2.3 | avg depth 1.3 -> 2.5+; >= 4/20 trials reach depth >= 3 |

### Research work items

| # | Item | Cost | Dependencies | KPI |
|---|---|---|---|---|
| R2.1 | Recursive self-improvement loop Stage 1+2 design refinement (substrate_query.py find-relevant-knowledge + compose-fix) | 2-3 hours | KP P1 + P2 outcomes | spec filed; ~200 LOC pseudocode |
| R2.2 | SHARES_MATH edge auto-discovery cell design (unblocks KP P3 + Pi/Sigma + CHTV-2) | 2-3 hours | none | cell design filed |
| R2.3 | Memory + Cycle 52 designation when criteria met | 30 min | phase 2 exit | Cycle 52 designation memory filed |

### Phase 2 exit criteria

- Substrate atom count >= 2M (from current 1844 + KP P1 + BATCH 17 ingest + mapper Wikidata math/science)
- L6-PROOF FINDER avg depth >= 2.5
- KP P4 HARD-PASS or MIDDLE
- CELL T1 GHRR vs FHRR decision made
- SHARES_MATH auto-discovery cell design filed

Roll to Phase 3 when 4 of 5 criteria met OR 72h elapsed.

## PHASE 3 (NOW+72-168h / Day 4-7): SCALE TO ~10M + KP P3+P5 + ENTITY RESOLUTION

### Testbed work items

| # | Item | Cost | Dependencies | KPI |
|---|---|---|---|---|
| T3.1 | Mapper runs: arxiv_2m + pubmed_5m + wikipedia_100k --filter math/science | 4-8h cumulative | T2.1 success | substrate ~5-10M total atoms |
| T3.2 | CELL ER entity resolution Fellegi-Sunter cascade | ~6h CPU | T3.1 in progress | >= 95% facts resolve to unique canonical-id; precision >= 0.97 |
| T3.3 | Promote KP P3 SHARES_MATH-discovery output to T2 archetypes | 1h ingest | E3.1 | >= 10 SHARES_MATH equivalence classes ingested; substrate retains 0.75+ macro |

### Exp-Dev work items

| # | Item | Cost | Dependencies | KPI |
|---|---|---|---|---|
| E3.1 | CELL KP path P3 SHARES_MATH-discovery cell run | ~1 day CPU | R2.2 spec + corpus growth | >= 10 SHARES_MATH eq classes size >= 3; 90% hand-verified precision |
| E3.2 | CELL SC VSA scaling probe at 10M atoms (existential validation) | ~1 day GPU | T3.1 + L1 partition ready | 95p recall@10 >= 0.60; L1 within-vs-between >= 10x; no partition > 50K atoms |
| E3.3 | CELL KP path P5 Curry-Howard type promotion | ~1 day build + 4h CPU | KP P2 + L6-PROOF + Pi/Sigma | >= 5 T1 axioms with >= 10 dependent T3 atoms each verified by L6-PROOF; DEFINED_OVER edges authored 1.0 precision |

### Research work items

| # | Item | Cost | Dependencies | KPI |
|---|---|---|---|---|
| R3.1 | Recursive self-improvement loop Stage 1+2 implementation spec | 1 day | R2.1 design | full ~700 LOC spec across 5 substrate_query.py extensions |
| R3.2 | Mizar parser refinement + CELL 1 ship coordination | 1 day | T3.1 success | parser refined per Mizar real format; ingest cell ready |
| R3.3 | Cycle 52 close synthesis + substrate-LLM categorical gap publishable write-up | 1 day | KP 5 paths + scaling probe | draft filed |

### Phase 3 exit criteria

- Substrate atom count >= 10M
- CELL SC scaling probe PASSED
- KP 5 paths IDENTIFIED + 3+ HARD-PASS (P1 + P2 + P4 minimum; P3 + P5 likely)
- Entity resolution operational
- L6-PROOF FINDER avg depth >= 3
- Recursive self-improvement loop Stage 1+2 spec'd

Roll to Phase 4 / Cycle 52 when 5 of 6 criteria met OR 168h elapsed.

## PHASE 4 (Cycle 52 / Day 8+): RECURSIVE SELF-IMPROVEMENT LOOP OPERATIONAL + MIZAR + OEIS + LEAN MATHLIB

### Phase 4 highlights (full plan deferred to Cycle 52 close synthesis)

- Recursive self-improvement loop Stages 1-6 OPERATIONAL
- Mizar (50K formalized theorems) + OEIS (370K math sequences) + Lean Mathlib (80K formalized math) INGESTED
- Substrate atom count ~50-200M (Tier-1 corpus complete)
- KP 5 paths SHIPPED + operational
- L6-PROOF at depth ~5-6 with multi-step lemma chains
- Substrate-product positioning artifact count 30+
- 8d -> 10d spectral observability pillar (signature/complexity channels)
- L3 DisCoCat coalgebraic categorical substrate
- L4 GNN R-GCN+CompGCN+HAN SHARES_MATH prototype
- Path to substrate-LLM corpus parity at Cycle 100 (3-5 years per substrate-product positioning trajectory)

## Cross-session sequencing dependencies (Gantt-style)

```
Day 0 (now):
  T1.1 LFS migration ----+
                         |
  R1.1 BATCH 17 ---------+--- (independent parallel)
  E1.1 KP P2 build start +

Day 0+12h:
  T1.2 mapper build start (gated on T1.1)
  T1.3 KP P1 promote ingest (gated on Testbed bandwidth)

Day 1:
  T1.2 mapper complete --+
  E1.1 KP P2 build day 2 +-- both feed Day 2
  R1.1 BATCH 17 ingested +
  R1.2 Memory entries ---+

Day 2:
  T2.1 first mapper run wikidata math/science (gated on T1.2)
  E2.1 CELL T1 GHRR test
  R2.1 recursive loop Stage 1+2 spec
  E1.1 KP P2 verdict

Day 2+12h:
  T2.2 mapper conceptnet
  E2.2 KP P4 build (gated on T2.2)
  E2.3 L6-PROOF FINDER re-run

Day 3-4:
  T3.1 mapper arxiv + pubmed + wikipedia
  E3.1 KP P3 SHARES_MATH (gated on R2.2)
  E3.2 SC scaling probe (gated on T3.1)
  R3.1 recursive loop impl spec

Day 4-7:
  T3.2 entity resolution
  E3.3 KP P5 Curry-Howard
  R3.2 Mizar ship
  R3.3 cycle 52 close synthesis

Day 8+: Phase 4 Cycle 52
```

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| LFS migration error blocks all pushes | Testbed owns; Research attempt failed at 49% but no corruption; 3 fallback options |
| Mapper hits per-corpus format issues | Testbed implements 1 corpus first (Wikidata) end-to-end; refines parser per format |
| KP P2 DRUM rule mining fails on substrate corpus shape | E1.1 builds with conservative thresholds (confidence >= 0.7); HARD-PASS via MIDDLE iteration |
| SC scaling probe fails at 10M atoms | Halt 100M ingest plan; revert to Stratified Hybrid layer-isolated routing per drill recommendation |
| Substrate macro regresses on KP promotion (cap_map drop) | Per drill HARD-FAIL gate; revert promotion + iterate |
| Phase exit criteria slip | Time-box at 24h/72h/168h; ship MIDDLE-band verdicts as legitimate phase exits |

## KPIs (USER-vision-tracking)

| Metric | Now | Phase 1 exit | Phase 2 exit | Phase 3 exit | Phase 4 (Cycle 52) |
|---|---|---|---|---|---|
| Substrate atom count | 1844 | 1868 (+ 24 KP P1) | 2-5M (+ Wikidata math) | 10M (+ all 5 mapper corpora) | 50-200M (+ Mizar OEIS Lean) |
| L6-PROOF FINDER avg depth | 1.3 | 1.3 | 2.5+ | 3.0+ | 5.0+ |
| KP paths shipped | 1 (P1) | 2 (P1 + P2) | 3 (P1 + P2 + P4) | 5 (all paths) | 5 operational + loop integrated |
| Macro F1 (HP_v1+) | 0.75 | 0.75+ | 0.75-0.78 | 0.78-0.82 | 0.82-0.85 |
| Substrate-product positioning artifacts | 24+ | 26+ | 28+ | 30+ | 35+ |
| External corpora ingested | 0% mapper | 0% mapper | wikidata + conceptnet | + arxiv + pubmed + wikipedia | + Mizar + OEIS + Lean Mathlib |
| Recursive self-improvement loop stages | 0/6 | 0/6 | 2/6 (Stage 1+2 designed) | 2/6 (Stage 1+2 spec'd) | 6/6 operational |

## Routing per session

- **Testbed**: this PLAN + Phase 1 work items T1.1 + T1.2 + T1.3 above; coordinate LFS migration; mapper implementation
- **Exp-Dev**: this PLAN + Phase 1 work items E1.1 + E1.2 above; KP P2 DRUM rule mining build; standing for KP P3/P4/P5 design
- **Research (me)**: BATCH 17 deeper DEPENDS_ON authoring immediately (R1.1); memory entries (R1.2); recursive loop design refinement (R2.1); SHARES_MATH auto-discovery cell design (R2.2); standing on Phase exit criteria

## Cross-references

- All prior Research + Testbed + Exp-Dev coordination notes today (Cycle 51 close)
- Memory: substrate-cycle-51-close-HP-v1-0-70 + substrate-CHTV1 + substrate-T1-algebra-dict-backfill-144 + feedback-research-external-corpus-inventory + feedback-full-auto-productivity-look-harder
- notes/research_drill_optimal_external_corpus_to_VSA_HRR_substrate_ingest_methodology_knowledge_promotion_mechanism_3x_2026-06-13.md (key strategic finding source)
- USER directive 2026-06-13 "you're guiding this process you need clear plan"

---

**Testbed + Exp-Dev:** MASTER PLAN Cycle 51 close to USER vision 4-phase path + explicit ownership + deliverables + dependencies + cost estimates + KPIs + Phase 1 24h LFS unblock + mapper build + KP P2 DRUM + BATCH 17 depth-3+4 + Phase 2 first corpus ingest wikidata math/science + KP P4 sleep-replay + L6-PROOF depth jump + Phase 3 ~10M atoms + KP P3 SHARES_MATH + P5 Curry-Howard + entity resolution + SC scaling probe + Phase 4 Cycle 52 recursive self-improvement loop operational + Mizar OEIS Lean Mathlib + Gantt-style sequencing + risks + mitigations + KPIs tracking substrate-on-all-knowledge USER vision + USER full-auto overnight continuing.
