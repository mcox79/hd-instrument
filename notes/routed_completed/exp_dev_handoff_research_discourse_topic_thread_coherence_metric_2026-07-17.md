# exp_dev hand-off — research: discourse topic/thread coherence metric (entity-grid, non-pronoun)

**Filed-by:** research (Sonnet lit-scan x3 + Sonnet synthesis), 2026-07-17.
**Trigger:** `notes/research_discourse_topic_thread_coherence_metric_2026-07-17.md` — full biology-first findings, ranked 8-candidate list, and the pre-registered "Cheap decisive test" section (HARD-PASS/HARD-FAIL bars, one-variable isolation, non-trivial baseline, difficulty-on knobs) all live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** `data/orchestrator_paused.flag` absent at filing time (NOT PAUSED) — re-check at pickup time before shipping anything to remote/GPU queues.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below beyond what is already fixed in the cited research note's "Cheap decisive test" and "Recommended first cell" sections — the cell-author owns translating those into concrete pre-reg + code.

---

## Anchor candidates (rank-ordered)

1. **[Primary, do FIRST, near-zero annotation cost] Entity-grid role-transition coherence via sentence-permutation discrimination.**
   - Anchor pointer: research note "Cheap decisive test" section — build a per-passage entity-role grid from ALREADY-extracted role-tagged entities (S/O/X per sentence), score via role-transition coherence, test pairwise discrimination accuracy (original document vs. K random full-shuffle permutations, AND separately K adjacent-sentence-swap-only permutations) against two baselines: entity co-occurrence (role-free) and random.
   - Substrate-product reading: this is the FIRST direct, non-pronoun test of whether the substrate's Tier-1 (Cf-ranked-by-grammatical-role) discourse-tracking design choice carries real coherence information, using a 20-year-old literature-validated task (Barzilay & Lapata) that is independently correlated with human readability judgment, not a self-referential metric invented for this substrate. It replaces the pronoun-accuracy-vs-recency struggle with a metric where a real, non-trivial competitor (co-occurrence-only) is built in from the start.
   - Tier hint: novel-synthesis for the port to this substrate's register/pipeline is capped P=0.42 per note; the underlying task+metric mechanism (entity-grid, permutation discrimination) is well-precedented and mature in the NLP literature, so risk is concentrated in the port and in whether this specific register/scale shows the effect, not in the concept's soundness.
   - Why now: needs NO new parser work (reuses whatever role-tagging already exists), needs NO new gold-label annotation (permutations are self-supervised negatives), and can run in PARALLEL with continued parser/lexicon work per the ranked-barriers note's sequencing — nothing blocks it.

2. **[Secondary, contingent on anchor 1 landing (any outcome), targets a DIFFERENT WSM tier] ProPara-style entity-state tracking, register-adapted (create/moved/destroyed/location).**
   - Anchor pointer: research note section (c) candidate #2 / ranked-list item 2.
   - Substrate-product reading: directly operationalizes the WSM note's Tier-2 five-dimension situation content (protagonist state, space/location) rather than Tier-1's role-ranking; has a genuine published rule-based baseline (ProComp, Dalvi et al. 2018) as existence-proof of glass-box feasibility on the coarser sub-tasks (entity created/destroyed/moved), weaker on location-span specifically.
   - Tier hint: real (nonzero) annotation cost — either adapt the existing ProPara dataset directly, or hand-build a small analog for the curriculum register; this is real construction work, not a free re-use.
   - Why now: complementary to anchor 1 (different WSM tier, different failure mode), not a replacement — worth scoping once anchor 1's result is in, regardless of which way it lands.

3. **[Tertiary, cheap to construct, targets WSM Tier-2's discontinuity-check] Injected-inconsistency detection.**
   - Anchor pointer: research note section (a) A2 / ranked-list item 3.
   - Substrate-product reading: swap a stated property/location for an entity between two sentences of a real passage (self-supervised construction, no human annotation needed beyond picking swap candidates) and test whether the discourse-tracking mechanism flags the resulting clash, against a baseline with no cross-sentence state (which cannot detect it even in principle). Directly tests the WSM note's already-sketched Tier-2 discontinuity-check machinery and its own registered Prediction 2 (event-boundary/consolidation trigger).
   - Tier hint: less mature as a corpus-scale automated benchmark than anchor 1 (Otero & Kintsch's paradigm is a human-subjects design, not an NLP benchmark) — more design-from-scratch work than anchor 1, but still cheap relative to anchor 2's annotation cost.
   - Why now: natural pairing with the WSM note's own Prediction 2, which is currently unfulfilled (that note flagged it as blocked on a held-out multi-scene test corpus with human-placed scene breaks — this anchor's self-supervised inconsistency-injection design is a cheaper substitute that doesn't require sourcing that corpus).

4. **[Fourth, high ceiling, currently ungated — do NOT build yet] Causal-centrality-predicts-recall as a summarization-content-selection task.**
   - Anchor pointer: research note section (a) A1 / ranked-list item 4.
   - Substrate-product reading: the single strongest biological function found in this entire scan (causal-network centrality directly predicts human recall/importance) but requires a causal-relation extractor the substrate does not yet have.
   - Tier hint: flag as a longer-horizon build; do not attempt a shortcut version now.
   - Why now: listed for completeness/sequencing awareness only — not actionable until a causal-relation extractor exists.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_discourse_topic_thread_coherence_metric_2026-07-17.md` — this drill's full findings, ranked 8-candidate list, cheap decisive test with HARD-PASS/HARD-FAIL bars, one-variable isolation, difficulty-on knobs, cross-thread synthesis, and full citation list.
- `notes/research_discourse_state_of_mind_situation_model_2026-07-17.md` — the four-tier WSM architecture (Tier 0 Cb-pointer, Tier 1 Cf-ranked resonator focus, Tier 2 activated situation-model bundle, Tier 3 durable foundation); anchor 1 tests Tier-1's role-ranking design choice specifically, anchor 2 tests Tier-2's five-dimension content, anchor 3 tests Tier-2's discontinuity-check mechanism. Anchor 1 does NOT replace that note's own Prediction 1 (Cb-pointer pronoun test) — recommend running both, since they test different claims on the same underlying data structure.
- `notes/research_coreference_hobbs_centering_resolver_2026-07-16.md` — the existing role-tagging/discourse-memory shim this cell's entity extraction reuses; no new extraction machinery needed.
- `notes/research_glassbox_reading_synthesis_ranked_barriers_2026-07-17.md` — confirms anchor 1 can run in parallel with, not blocked behind, further parser/lexicon work.
- Director's brief (referenced descriptively in the dispatching prompt): prior pronoun-vs-recency tests did not clearly beat a recency baseline on natural text, and the implicit-causality/verb-semantics signal is too rare to test (n=0 in 100 LitBank books) — this hand-off's anchor 1 is the direct realignment away from pronoun-accuracy as the discourse-state value metric, toward topic/thread/coherence tracking instead.

---

## Contract section

- Cell-author owns: exact role-transition scoring formula (count-based continuity/discontinuity tally vs. frequency-weighted transition-probability score), exact permutation count K (research note recommends >=10 per passage, both full-shuffle and adjacent-swap-only conditions), exact passage-sampling procedure (needs genuine topic/entity variety — natural-prose sample, not curriculum-only corpus), and smoke-scale parameters for anchors 2-4 if pursued.
- HARD-PASS/HARD-FAIL bars for anchor 1 are pre-registered in the research note's "Cheap decisive test" section — do not loosen them at pre-reg time without flagging the deviation explicitly in the pre-reg file.
- Anchor 1's own design REQUIRES both the full-shuffle and adjacent-swap-only permutation conditions to be run (not just the easier full-shuffle case) — the note's HARD-PASS bar has a separate, smaller margin threshold for the harder adjacent-swap case; do not report only the easier condition.
- All anchors carry deflated P estimates (0.35-0.42 range per the cited note) — treat as genuinely uncertain going into pre-reg, not near-certain.

## Autonomy declaration

Research does not prescribe exact code, exact scoring-formula implementation, exact permutation-generation procedure, or exact passage-sampling beyond what is fixed in the cited research note (the one-variable isolation: role-transition vs. co-occurrence-only; the two permutation-difficulty conditions; the three-way baseline comparison against random and co-occurrence). Cell-author has full autonomy over implementation detail and exact parameters, subject to the falsifiable predictions and HARD-PASS/HARD-FAIL bars pre-registered in the cited research note.
