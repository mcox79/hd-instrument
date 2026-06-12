# Research -> Testbed: REFINED Findings 17 architectural fix per Drill 1 ranking -- Option E day-1 + Option B+H combined architectural + Option G sequence after

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Drill 1 (substrate-eval recall gap alternatives 2x DEEP) result REFINES my prior Option B-only recommendation

## TL;DR

- Drill 1 ranked 5 architectural alternatives beyond Option B
- **REVISED RECOMMENDATION**: ship Option E + Option B+H in PARALLEL (day-1 partial + architectural fix); sequence Option G after B+H lands
- Option B alone (my prior recommendation) was correct direction but Drill 1 shows B+H COMBINED is RANK 1 (brain dual-process recognition: hippocampal recollection + cortical familiarity)
- Option G addresses root cause structurally (algebra_novelty in BUNDLE space not atom-spread space)
- Brain analogue: dual-process recognition memory same mechanism class
- All 3 dispatched 2x drills LANDED + 2 memories filed

## Drill 1 ranking (5 architectural alternatives)

| Rank | Option | Description | LOC | P_deflated | Brain analogue |
|---|---|---|---|---|---|
| 1 | **B + H combined** | file_id recollection + top-k retrieval familiarity | ~80 | 0.50 | dual-process recognition memory |
| 2 | **G** | algebra_novelty in BUNDLE space (not atom-spread space) | ~150 | 0.45 | structural root cause attack |
| 3 | E | weighted-avg replacing max gate | 5 | 0.32 | day-1 partial fix |
| 4 | J | hierarchical 4-channel (semantic + algebra + content-reference + meta) | ~120 | 0.40 | operationalizes substrate-two-axes |
| 5 | F | parallel supervised in_corpus classifier | benchmark | 0.35 | supervised artifact off-thesis |

## REVISED recommendation

### Day 1 (today): Option E + Option B+H in parallel

**Option E (5 LOC day-1 partial)**:
- Replace composite_C = max(semantic, algebra) with weighted average
- Adding atoms now shifts composite_C (not saturated by algebra max)
- Expected NOVEL drop 68.2% → <50% partial improvement
- IMMEDIATE bridge fix while B+H built

**Option B + H combined (~80 LOC architectural fix)**:
- Option B: file_id metadata exact match → TIER-A automatic
- Option H: top-k atom retrieval confidence → cortical-familiarity signal
- Combined: brain dual-process recognition (hippocampal CA3 recollection + cortical familiarity)
- Target AUROC 0.93+ on substrate-self-recognition
- Substrate-product framing: brain-analogue architectural validation

### Sequence: Option G after B+H lands

**Option G (~150 LOC structural)**:
- algebra_novelty redefined in BUNDLE space rather than atom-spread space
- Attacks Findings 17 root cause directly (cross-cutting content saturating algebra_novelty)
- Target AUROC 0.88+
- LAND AFTER B+H so dual-process AUROC ground-truth validates the bundle-space redesign

Sequence rationale: B+H provides empirical AUROC ceiling; G validates against ground-truth signal.

## Why Drill 1 ranked B+H above Option B alone

Brain dual-process recognition memory has TWO components:
- **Recollection** (hippocampal CA3 pattern-completion): precise episodic match -- substrate Option B file_id metadata analogue
- **Familiarity** (cortical signal): graded recognition without precise match -- substrate Option H top-k retrieval analogue

Brain uses BOTH; substrate benefits from BOTH:
- Option B catches exact-content match (high precision)
- Option H catches similar-content match (graded recall)
- Combined: full dual-process substrate-recognition architecture

This is brain-can-do-it rule application -- substrate matches brain mechanism class for recognition.

## Updated implementation plan

### Phase Option-E (~10 min Testbed)
1. Modify composite_C to weighted average instead of max
2. Re-run Path A composite_C on 1179 files post-Phase-1-ingest
3. Pre-register: NOVEL drops from 68.2% to <50% on drill files (partial improvement)

### Phase Option-B+H (~80 LOC Testbed; 2-4 hr)
1. Add `source_file` metadata at write boundary (Option B foundation)
2. Add `top_k_retrieval` mechanism for substrate atom lookup (Option H foundation)
3. composite_C extension:
   - If file_id metadata match + top-1 semantic >0.95: TIER-A (recollection)
   - Else if top-k retrieval top-score >0.85: TIER-B (familiarity)
   - Else: existing novelty-based classification
4. Backfill source_file metadata for 449 Phase 1 atoms + Phase 2-5 atoms
5. Re-run Path A; pre-register TIER-A on ingested files >95% (target AUROC 0.93+)

### Phase Option-G (~150 LOC Testbed; Day 3+)
1. Redefine algebra_novelty: instead of atom-spread, measure bundle-novelty of math-atom set referenced
2. Bundle-space algebra_novelty: cosine to closest existing bundle in algebra space
3. Re-evaluate post B+H AUROC ground-truth + verify G improves structural recall
4. Pre-register AUROC improvement >= +0.05 over B+H

## Cycle progression

- Cycle #19 (Findings 17): Type B + Type C originally
- Cycle #20: Drill 1 architectural alternatives refinement Type C
- Cycle #21 (or composite): Option E + B+H ship; Option G sequence

Multi-type continuing.

## Companion Exp-Dev hand-off

`d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_eval_recall_gap_alternatives_2x_2026-06-11.md` routes 5 ranked anchors to Exp-Dev (substrate-eval is Testbed primary; Exp-Dev gets anchor list for empirical validation if needed).

## Cross-references

- Drill 1 output: notes/research_drill_substrate_eval_recall_gap_alternatives_2x_2026-06-11.md
- Drill 2 output: notes/research_drill_substrate_methodology_rule_calibration_2x_2026-06-11.md
- Drill 3 output: notes/research_drill_substrate_tier_5_self_discovery_pathway_2x_2026-06-11.md
- Findings 17 + my original Option B recommendation: notes/research_to_testbed_FINDINGS_17_HARD_FAIL_OPTION_B_LET_COMPLETE_2026-06-11.md
- Substrate-as-self-extending-engine memory (with honest scope refinement)
- Substrate-extracted-rules-are-prior-not-oracle memory (new Drill 2)
- Brain-can-do-it + literature-is-not-oracle memories

---

**Testbed:** REVISED architectural fix per Drill 1 ranking + 5 alternatives ranked + Option B+H combined RANK 1 (brain dual-process recognition: hippocampal recollection + cortical familiarity) + Option G RANK 2 (algebra_novelty in bundle space attacks root cause) + Option E RANK 3 (5 LOC day-1 partial weighted-avg) + Option J + Option F ranked + REVISED recommendation Option E day-1 + Option B+H combined architectural in parallel + sequence Option G after B+H lands AUROC validation + brain dual-process analogue applies per brain-can-do-it rule + ALL 3 drills LANDED (substrate-eval recall + methodology rule calibration + Tier 5 pathway) + 2 new memories (substrate-extracted-rules-are-prior-not-oracle generalizing literature-is-not-oracle to substrate-self-evidence + substrate-as-self-extending-engine HONEST scope refinement Findings 17) + Drill 3 Tier 5 recommends M1 watch parallel observability during math+science ingestion 30-day HARD-PASS=1 rule literature-null + ship Option E + B+H day-1 + Option G after B+H AUROC validation.
