# exp_dev hand-off — research: glass-box robust-parsing path + honest coverage ceiling

**Filed-by:** research (Sonnet lit-scan x3 + Opus synthesis), 2026-07-16.
**Trigger:** `notes/research_glass_box_reading_robust_parsing_ceiling_2026-07-16.md` — full findings, cheap decisive test, falsifiable predictions (A-D) with HARD-PASS/HARD-FAIL bars, and the pre-registered "good-enough glass-box reading" definition all live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** `data/orchestrator_paused.flag` absent at filing time (NOT PAUSED) — re-check at pickup time before shipping anything to remote/GPU queues.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below — the cited research note's section (b)/(c) has the falsifiable predictions and HARD-PASS/HARD-FAIL bars; the cell-author owns translating those into concrete pre-reg + code.

---

## Anchor candidates (rank-ordered)

1. **[Primary, near-zero-cost, do FIRST] The cheap decisive test itself (research note section (b)): triage `exp_read_grow_foundation_endtoend_v1.py`'s own logged extraction misses against the literature's predicted failure taxonomy.**
   - Anchor pointer: research note section (b) "Cheap decisive test" — bucket every extraction miss into `coordination` / `relative-clause` / `passive-voice` / `nominalization` / `coreference-unresolved` / `parse-structure-error-other` / `lexicon-mapping-error` / `unclassifiable`.
   - Substrate-product reading: this is a RE-ANALYSIS of output the in-flight cell already produces (or will produce on its next run), not a new build — cheapest possible next step, and it is DECISIVE: HARD-PASS (>=60% of misses fall into the named literature-predicted buckets) means the roadmap below (items 2-4) is directly actionable; HARD-FAIL (<30%) means the positional-SVO parser itself is the priority fix, not the extraction-rule layer, and items 2-4 should wait.
   - Tier hint: near-zero risk, near-zero cost — this should gate whether the rest of this hand-off's anchors are worth building at all. Do not skip straight to anchor 2 without running this first.
   - Why now: the in-flight cell's own header already documents its parser as "positional SVO" (word-order only, not a real dependency/clause-type parse) — this triage step is the fastest way to confirm whether that gap is actually where the coverage loss concentrates before investing further engineering time.

2. **[Secondary, contingent on anchor 1 HARD-PASS] A small, hand-written, glass-box clause-type classifier (ClausIE-style SV/SVA/SVC/SVO/SVOA/SVOC/SVOO decision tree) restricted to the closed grammar of curriculum Rungs 3-4** (per `research_early_reader_language_acquisition_curriculum_2026-07-16.md`'s own rung definitions — agreement/past-tense/possessive at Rung 3, one-subordinate-clause-max/passive-avoidance at Rung 4).
   - Anchor pointer: research note section (e) point 1, Prediction A (section c).
   - Substrate-product reading: tests whether a real (even if hand-built, non-neural) dependency/clause-type parse recovers passive-voice facts a positional parser misses — directly operationalizes the strongest, best-evidenced single finding in the classical-IE lane (ClausIE's own paper credits its dependency-based approach with "inherently capturing" passive constructions).
   - Tier hint: novel-synthesis for the porting-to-this-substrate step (capped P=0.40 per note); the underlying mechanism (clause-type classification via dependency roles) is well-precedented in the NLP literature, so risk is concentrated in the port, not the concept.
   - Why now: this is the concrete trigger point the curriculum ladder itself identifies (Rung 3+) — building it before the curriculum reaches that rung is premature; building it after is a coupled, expected dependency, not a surprise.

3. **[Tertiary, cheapest single upgrade if pursued alone] Rule-based coordination pre-splitting pass (CALM-style rewrite: "X eats seeds and worms" -> two atomic sentences BEFORE extraction).**
   - Anchor pointer: research note section (e) point 3, Prediction B (section c).
   - Substrate-product reading: the ONE upgrade in the whole scan with a documented PRECISION-POSITIVE yield gain in the primary literature (not a trade-off, unlike ClausIE's own in-line CC handling) — highest evidence-to-effort ratio of any anchor in this hand-off.
   - Tier hint: capped P=0.35 per note (real precedent on Web/newswire text, not yet demonstrated precision-positive specifically on graded/simple prose or on this substrate).
   - Why now: can be built and tested independently of anchor 2 (it's a pre-processing rewrite step, not a parser swap) — a genuinely parallel-track option if anchor 1's triage shows coordination misses are a large bucket on their own.

4. **[Fourth, gates curriculum scaling past Rung 3] Rule-based coreference pass (Hobbs' algorithm or centering-theory resolver).**
   - Anchor pointer: research note section (e) point 4, Prediction D (section c).
   - Substrate-product reading: the ONE failure mode in the entire scan that does NOT shrink with grammar simplification (plausibly worsens, since simplified prose substitutes pronouns for long NPs) and is unaddressed by every classical IE technique reviewed. Left unbuilt, this becomes an increasingly binding coverage ceiling exactly as the curriculum introduces more natural prose.
   - Tier hint: capped P=0.42 per note; Prediction D's own HARD-PASS/HARD-FAIL bars are about CONFIRMING the gap is real and load-bearing on this substrate's actual curriculum-style sentences before committing to building the resolver — run that confirmation sub-test first, not the full resolver build.
   - Why now: not urgent for Rungs 1-2 (SVO-only, no clause embedding) but should be scoped/prototyped before curriculum work reaches Rung 3, per the coupled-dependency note in the research note's cross-thread synthesis.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_glass_box_reading_robust_parsing_ceiling_2026-07-16.md` — this drill's full findings, cheap decisive test, falsifiable predictions A-D, cross-thread synthesis, pre-registered "good-enough glass-box reading" definition, coverage-ceiling estimates, and full citation list.
- `experiments/exp_read_grow_foundation_endtoend_v1.py` — the in-flight cell this drill informs; its own header already documents the current parser as "positional SVO" (word-order only), the specific gap anchor 1's triage test targets.
- `notes/research_early_reader_language_acquisition_curriculum_2026-07-16.md` — the graded early-reader curriculum ladder (Rungs 0-5); this drill found its grammar progression maps almost exactly onto ClausIE's own clause-type taxonomy — a load-bearing convergence that should drive the SEQUENCING of anchor 2 (build clause-type parsing exactly when the curriculum reaches Rung 3+, not before, not after).
- USER directive (memory, referenced descriptively in the dispatching prompt): glass-box-the-reading-no-LLM — rule-based IE, provenance, accept lower coverage, gate cleans up, narrow-neural-syntax-parser carve-out. This hand-off's anchor 2 sequencing (defer any neural parser component to curriculum Rung 5+, per research note section (e) point 2) is this drill's concrete operationalization of that carve-out — the cell-author should treat "no neural parser before Rung 5" as the current recommended boundary, not an open question.

---

## Contract section

- Cell-author owns: concrete pre-reg (exact miss-bucketing taxonomy applied to real logged output for anchor 1; exact clause-type rule set, exact test-sentence construction for anchor 2; exact coordination-pattern rewrite rules for anchor 3; exact coreference test-sentence sampling for anchor 4's confirmation sub-test), smoke gate, dispatch.
- Anchor 1 MUST run before anchors 2-4 are prioritized — its HARD-PASS/HARD-FAIL result (research note section (b)) is a genuine fork in what to build next, not a formality.
- HARD-PASS/HARD-FAIL bars for anchors 2-4 are pre-registered in the research note sections (b)/(c) — do not loosen them at pre-reg time without flagging the deviation explicitly in the pre-reg file.
- All four predictions (A-D) carry deflated P estimates (0.35-0.42) per lit-scan calibration penalty — treat as genuinely uncertain, not near-certain, going into pre-reg.

## Autonomy declaration

Research does not prescribe exact code, exact clause-type rule implementation, exact coordination-pattern regex/rule set, or exact coreference-resolver algorithm choice beyond naming Hobbs'-algorithm/centering-theory as the literature-precedented glass-box options. Cell-author has full autonomy over implementation detail, exact rule specification, and smoke-scale parameters, subject to the falsifiable predictions and HARD-PASS/HARD-FAIL bars pre-registered in the cited research note, and subject to the anchor-1-first sequencing constraint above.
