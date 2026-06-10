# exp_dev hand-off -- research: Substrate Conversational Breadth Maximization 2x

**Filed-by:** Research sub-agent, 2026-06-09
**Trigger:** 2x depth drill on CONV breadth maximization; 5 anchors empirically validated (CONV-2/3/5/8/15 HP); 10 unvalidated CONV anchors with ranked acceptance gates; research note at `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md`
**Pause state:** check `data/orchestrator_paused.flag` before dispatching any anchor.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Why this hand-off exists

The research drill established:
1. 85% substrate-direct ratio is achievable for enterprise KB distributions (quantified, with taxonomy breakdown)
2. 10 unvalidated CONV anchors are all implementable with existing substrate primitives -- they are engineering tasks, not research questions
3. CONV-9 (PII detection) is a production gate -- required before any real-user data touches the system
4. CONV-4 (repair) is a trust primitive -- required for production adoption
5. Template stiffness is mitigated by variant rotation + substrate-draft + LLM-polish hybrid

This hand-off feeds the CONV anchor battery directly to exp_dev for sequenced dispatch.

---

## Anchor candidates (rank-ordered; exp_dev picks routing and sequencing)

### Anchor 1 [PRODUCTION GATE, TIER-1, CPU]: CONV-9-FULL PII detection across 5K messages

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 3
**Substrate-product reading:** compliance gate. Substrate cannot accept real user data without PII pre-write filter per OWASP LLM08:2025. spaCy NER + regex hybrid covers 6 PII categories. PP-186 PII strip-inject primitive is the substrate integration point.
**Tier hint:** CPU, local
**Why now:** production blocker -- blocks all real-user data collection and demos with actual users. Must pass before any other CONV anchor that touches user data.

### Anchor 2 [TRUST PRIMITIVE, TIER-1, CPU]: CONV-4-FULL clarification + repair across 10K queries

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 1
**Substrate-product reading:** PP-180 contradiction detection triggers clarification; PP-104 erasure + rewrite + acknowledgment for user corrections. Zero-residual repair is the HARD-FAIL gate (PP-104 semantics must hold in conversational context). This is the single highest-trust primitive for production deployment.
**Tier hint:** CPU, local
**Why now:** repair capability gates professional user adoption. Users in regulated industries who cannot correct the system will not use it.

### Anchor 3 [DEMO MOMENT, TIER-1, CPU]: CONV-1-FULL creative forms (haiku/sonnet/limerick) at production

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 2
**Substrate-product reading:** template + CMU Pronouncing Dictionary + KB lexical retrieval. Highest demo-visibility per engineering effort. Shows substrate generates creative content (not LLM). Requires one-time CMU dictionary ingest (~130K words) and template library build.
**Tier hint:** CPU, local
**Why now:** strongest single demo moment relative to implementation cost. Anchor 2 + Anchor 3 together build the "substrate IS the AI" demo.

### Anchor 4 [PERSONALIZATION, TIER-1, CPU]: CONV-10-FULL preference learning over 50-session benchmark

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 4
**Substrate-product reading:** PP-195 cross-session persistence + PP-107 confidence-graded atoms. Preferences stored as atoms (formality, verbosity, technical_level, topic_interest) with per-user tenant key. Cold-start explicit prompt at session 1; implicit inference from turns 2-10. Personalization is the mechanism by which substrate-direct responses improve over time without LLM retraining.
**Tier hint:** CPU, local
**Why now:** personalization drives repeat use and is the key differentiator vs stateless LLM-API products.

### Anchor 5 [GLOBAL COVERAGE, TIER-1, CPU]: CONV-6-FULL multilingual EN/ES/FR/DE/ZH

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 5
**Substrate-product reading:** Wikidata multilingual labels (already ingested at 185K+ facts) + grammar templates per language. Named entity translation is a direct lookup; simple sentence grammar validity is the quality gate. ZH requires jieba segmenter and separate template grammar.
**Tier hint:** CPU, local
**Why now:** commercial requirement for international markets. Wikidata ingest is already running (part of overnight chain); multilingual labels are available.

### Anchor 6 [DEVELOPER DEMO, TIER-1, CPU]: CONV-7-FULL code pattern library 100+ patterns

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 6
**Substrate-product reading:** 100+ code templates stored as substrate KB atoms (Python, JavaScript, SQL, Bash); PP-198 extracts (language, pattern_name) from query; template retrieved + parameterized. Zero hallucination advantage vs LLM code generation for standard patterns.
**Tier hint:** CPU, local
**Why now:** developer-facing use case with measurable advantage (exact syntax vs LLM hallucination risk on API names/signatures).

### Anchor 7 [INTEGRATION, TIER-2, CPU+optional API]: CONV-MULTITOOL substrate composes 3+ tools

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 7
**Substrate-product reading:** PP-123 cascade router extended to DAG execution; substrate retrieve -> SymPy -> Python sandbox -> LLM chain; intermediate results stored as substrate atoms; end-to-end audit chain via PP-184.
**Tier hint:** CPU local for retrieve+compute; API credit for LLM calls in chain
**Why now:** multi-tool composition is the ceiling claim for PP-188 Tier-5c orchestrator routing. If 3-tool chain works, the substrate-as-orchestrator categorical claim is empirically grounded.

### Anchor 8 [EMOTIONAL BREADTH, TIER-2, CPU]: CONV-3-FULL empathic at 12+ emotional categories

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 8
**Substrate-product reading:** PP-198 classifier extension to 12 emotional categories + template variant per class (5-10 variants per class to prevent stiffness). Validates whether substrate's intent classifier can be trained to discriminate 12 fine-grained emotional states at F1 >= 0.70.
**Tier hint:** CPU, local
**Why now:** extends validated CONV-3 HP to full emotional breadth. Required for substrate to feel attentive in social queries (the 8% empathic category in enterprise distribution).

### Anchor 9 [SYNTHESIS, TIER-2, CPU]: CONV-2-FULL hierarchical + cross-domain summarization

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 9
**Substrate-product reading:** extends validated CONV-2 single-entity summary to multi-document (D=50) and cross-domain. Parallel top-K retrieval per document + union ranked by PP-107 confidence. Template stitching coherence is the ceiling.
**Tier hint:** CPU, local
**Why now:** extends validated anchor to production-scale KB use case (50+ documents). Required for "summarize my entire knowledge base about X" demo.

### Anchor 10 [R&D, TIER-3, CPU, MULTI-WEEK]: CONV-11/12/13 algebra extensions (modal/probabilistic/higher-order)

**Anchor pointer:** `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` Level 7 Anchor 10
**Substrate-product reading:** genuine R&D -- new substrate algebra primitives (modal operators, Bayesian update, quantified queries). CRITICAL constraint: any new primitive must preserve PP-101 isolation and PP-184 Merkle chain integrity. Test algebraic invariants before declaring any extension ready.
**Tier hint:** CPU local; multi-week R&D
**Why now (lower priority):** these are v2+ differentiators. Ship v1 CONV battery first (Anchors 1-6), then R&D on algebra extensions.

---

## Context pointers (file paths only, no summaries)

- `notes/research_drill_conv_breadth_maximization_2x_2026-06-09.md` -- this drill's full findings (levels 1-7)
- `notes/research_drill_substrate_stateful_tool_orchestration_5x_2026-06-09.md` -- integration primitives drill (Anchors 1-7 of that note are prerequisites for Anchor 7 here)
- `notes/research_to_exp_dev_SUBSTRATE_CONVERSE_CAPABILITIES_2026-06-09.md` -- 15-anchor CONV routing note from earlier today
- `notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md` -- substrate-around-LLM architecture context
- `notes/research_to_testbed_BUILD_SUBSTRATE_CONVERSE_2026-06-09.md` -- substrate /converse build state
- `notes/substrate_capability_map.md` -- current cap_map; PP-187/188/195/198/212/104/107/184/123/180/101 rows are the load-bearing primitives for these anchors

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke.
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance (where stochastic elements exist; template fill is deterministic).
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code.
- Status_log entry per anchor with `plain_language` + `importance`.
- Anchor 1 (PII detection) is a production gate -- dispatch first regardless of queue depth.
- Anchors 1-6 are CPU-local; no cloud dispatch needed.
- Anchor 10 (algebra extensions) requires algebraic invariant preservation test before any PASS declaration.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, M, K, seed count, threshold bands (HARD-PASS + HARD-FAIL), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, and sequencing within the tier. The research sub-agent passes anchor POINTERS only. If exp_dev finds a cheaper or faster path to validate a CONV anchor (e.g., CONV-7 code patterns via a simpler template coverage test), that is exp_dev's call. The only fixed constraint is that Anchor 1 (PII) is a production gate and should be prioritized accordingly.
