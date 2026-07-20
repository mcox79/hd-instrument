# exp_dev hand-off — research: lexicon richness (subcategorization/selectional) as the real-prose-parsing barrier

**Filed-by:** research (Sonnet lit-scan x3 + synthesis), 2026-07-17.
**Trigger:** `notes/research_lexicon_richness_subcategorization_barrier_real_prose_parsing_2026-07-17.md` — full findings, falsifiable predictions, and cited mechanism recipe live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** `data/orchestrator_paused.flag` absent at filing time (NOT PAUSED) — but re-check at pickup time before shipping anything to remote/GPU queues.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below — the cited research note's section (b)/(c) has the falsifiable predictions and HARD-PASS/HARD-FAIL bars; the cell-author owns translating those into concrete pre-reg + code.

---

## Anchor candidates (rank-ordered)

1. **[Primary, cheapest, no-build] Coverage-audit — what fraction of real-prose verb tokens are inside symbolic subcat/selectional resource coverage, and at what granularity (type vs. instance) do selectional needs resolve.**
   - Anchor pointer: research note section (b) part 1.
   - Substrate-product reading: this is a measurement, not a build — answers whether the lexicon-richness barrier is genuinely separable from the foundation/world-fact-size barrier (Prediction 2) BEFORE committing build effort to a subcat table. Cheapest possible next step; should run before anchor 2.
   - Tier hint: near-zero engineering risk (corpus tagging + counting), but the *interpretation* threshold (type-level vs instance-level selectional need) requires a judgment call per case — cell-author should sample and hand-audit a subset (order 100-200 verb tokens) rather than attempt full automation on the first pass.
   - Why now: directly gates whether anchor 2 below is worth building at all, and at what resource-priority (VerbNet-first per the note's implication #4).

2. **[Secondary, build required] Three-arm glass-box parse test — isolate lexicon-richness contribution from grammar/category-granularity contribution on structural-ambiguity sentences.**
   - Anchor pointer: research note section (b) parts 2-3 + section (c) Prediction 1.
   - Substrate-product reading: this is the decisive test for whether "add a subcat lexicon" is sufficient on its own, or whether (per the Klein & Manning 2003 caution cited in the note) a chunk of any observed gain is actually attributable to under-specified grammar/category granularity in the existing scaffold, not the lexicon. Getting this wrong risks repeating a documented 20-year-old field-level attribution error.
   - **Three arms required, not two:** NO-LEXICON (current baseline, undifferentiated grammar), LEXICON-ONLY (subcat/selectional table added, grammar unchanged), LEXICON+GRAMMAR (subcat table + linguistically-motivated category splitting). A 2-arm test cannot distinguish which lever produced any observed gain — this is the note's central methodological warning, not optional scope.
   - Tier hint: risk concentrated in (a) constructing a genuinely testing set of structural-ambiguity sentences (PP-attachment, reduced-relative, verb-frame-bias — the note cites the Trueswell verb-bias literature and the classic "horse raced past the barn" construction as concrete templates), and (b) deciding what "linguistically-motivated category splitting" means concretely for the existing scaffold's grammar (cell-author's call, informed by Klein & Manning's actual splits — VP subtypes, finite/nonfinite — as a starting reference, not a mandate to copy exactly).
   - Why now: sequenced behind anchor 1's coverage-audit result, but not strictly blocked by it — could run in parallel if capacity allows, since the two anchors test different predictions (2 vs 1/3).

3. **[Tertiary, gates Prediction 3, cheap given anchor 2 exists] Glass-box-purity check on the subcat/selectional lookup table.**
   - Anchor pointer: research note section (c) Prediction 3.
   - Substrate-product reading: confirms the subcat table can be consumed via pure symbolic lookup + type-compatibility check (no dense/opaque similarity fallback needed) to hit anchor 2's HARD-PASS bar — this is what keeps the whole pipeline glass-box, matching the discipline already applied to the 07-16 semantic-lexicon table.
   - Tier hint: this is largely an audit of anchor 2's implementation, not a separate build — if anchor 2 is implemented as specified (pure lookup + type-check, no embedding fallback), this anchor is close to automatically satisfied; only needs an explicit inspectability check (can every parse decision be traced to a specific table entry + type-constraint check, with no learned/opaque step).
   - Why now: cheap add-on verification once anchor 2 exists; do not build as a standalone cell.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_lexicon_richness_subcategorization_barrier_real_prose_parsing_2026-07-17.md` — this drill's full findings, decisive test, falsifiable predictions, citations.
- `notes/research_word_grounding_lexicon_structure_content_unification_2026-07-16.md` — the SEMANTIC lexicon (word-form -> foundation-concept) this drill's SYNTACTIC lexicon (word-form -> subcat frame) is complementary to, not redundant with; both attach to the same proven role-filler scaffold. Note the cross-thread synthesis point that VerbNet uniquely fuses both (syntactic frames + thematic roles/selectional restrictions in one class entry) and so should be the first resource ingested for BOTH lexicons.
- `notes/exp_dev_handoff_research_word_grounding_lexicon_2026-07-16.md` — sibling hand-off for the semantic-lexicon anchor; the CoDEx-anchoring correction documented there (real on-disk foundation, no entity2text label files exist yet) applies equally here if this drill's cell needs to reference concept-level selectional constraints against the same foundation graph.
- `notes/research_early_reader_language_acquisition_curriculum_2026-07-16.md` — the graded early-reader curriculum; the structural-ambiguity test sentences for anchor 2 should be constructed at a comparable difficulty rung, not full adult-newspaper-prose complexity, for the first pass.
- `project_PIVOT_build_ideal_knowledge_foundation_from_existing_tools_USER_AUTHORIZED_2026-07-14` (memory ref) — frames general-knowledge ingestion as a GENERATION problem; this drill's headline finding is that subcategorization/selectional lexicon-building is by contrast an INTEGRATION problem (VerbNet/FrameNet/PropBank/WordNet already exist, free, symbolic, non-LLM) — a materially cheaper lever than foundation scale-up, per the note's substrate-product implication #2.
- `project_focus_recreate_brain_factorization_structure_content_two_thrusts_USER_2026-07-14` (memory ref) — the structure-content factorization thrust this drill adds a further factorization layer to (syntactic combinatorial potential vs. semantic content, both indexed per lexical entry, per VerbNet/HPSG/LFG design).

---

## Contract section

- Cell-author owns: concrete pre-reg (exact verb list for the subcat table — order 100-300 highest-frequency verbs per the note's Zipf-dominance argument, exact VerbNet-class-to-table mapping, exact structural-ambiguity test-sentence set, exact operationalization of "linguistically-motivated category splitting" for arm 3), smoke gate, dispatch.
- Must implement all three arms named in anchor 2 (NO-LEXICON, LEXICON-ONLY, LEXICON+GRAMMAR) if anchor 2 is picked up — the note is explicit that a 2-arm test cannot isolate the lexicon-specific contribution from the grammar-granularity contribution.
- Must report per-arm structural-ambiguity resolution accuracy against the constructed test-sentence set, not a proxy metric.
- HARD-PASS/HARD-FAIL bars are pre-registered in the research note section (b)/(c) — do not loosen them at pre-reg time without flagging the deviation explicitly in the pre-reg file.
- Anchor 1 (coverage-audit) has no HARD-PASS/HARD-FAIL gate of its own beyond Prediction 2's thresholds in the research note (>=90% token coverage / >=80% type-level-sufficient for HARD-PASS; <60% coverage or <50% type-level-sufficient for HARD-FAIL) — cell-author should report the raw measured fractions even if they fall in the ambiguous middle band between these bars.

## Autonomy declaration

Research does not prescribe exact code, exact verb-list cutoff, exact test-sentence corpus, or exact "grammar refinement" implementation beyond the order-of-magnitude anchors and the Klein & Manning reference point named above. Cell-author has full autonomy over implementation detail, exact resource-ingest scope (VerbNet-first per the note's ranking, but PropBank/FrameNet/WordNet backfill choices are the cell-author's call), and smoke-scale parameters, subject to the falsifiable predictions and HARD-PASS/HARD-FAIL bars pre-registered in the cited research note.
