# exp_dev hand-off -- research: LLM boundary is engineering (parse + fluency)

**Filed:** 2026-06-11 by research sub-agent
**Trigger:** Research drill `notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md` found substrate-native parse + fluency is engineering (not fundamental), with 10 architectures and two cheap decisive tests.
**Pause state:** Check `data/orchestrator_paused.flag` before queuing experiments.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## What was found (research summary)

The "LLM-only for English parse + fluency" claim is engineering, not fundamental. Key findings:

1. Published existence proof: HRR was used to implement Fluid Construction Grammar (FCG) for parsing AND production (VSA Survey Part II, Kleyko et al. ACM Computing Surveys 2022). FHRR is algebraically equivalent to HRR. Therefore the FCG-on-substrate port is a concrete engineering project, not a research question.

2. Biological existence proof: brain parses + generates fluent English in one unified system (Broca + Wernicke + STG + predictive coding). No separate "LLM" module. Sign language uses the same regions. The substrate architecture (compositional cleanup hierarchy) is more brain-like than a transformer.

3. Pre-LLM NLP existence proof: MaxEnt POS taggers achieve 97.3% accuracy on Penn Treebank (no neural net). Collins parser achieves 92%+ F1 (no neural net). Statistical MT (phrase tables + 5-gram LM) was production-deployed for 10 years. None of these required a transformer.

4. Temporal policy connection: substrate-native generation via temporal policy (integ_temporal_policy, already authorized) is mathematically equivalent to the biological predictive coding generation mechanism AND to n-gram LM generation. One architecture serves both.

---

## Anchor candidates (rank-ordered; exp_dev picks across queues)

### Anchor 1: SUBSTRATE-POS-TAGGER (cheap decisive test)
- Anchor pointer: `notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md` Section 4 (Cheap Decisive Test)
- Substrate-product reading: If substrate-native POS tagging on Penn Treebank WSJ section 24 achieves >= 88% accuracy, the context-binding disambiguation mechanism is validated and Phase 2 substrate-native parse is authorized. This gates the entire substrate-native English path.
- Tier hint: CPU-local (Penn Treebank is text; FHRR lookup is fast; no GPU required)
- Why now: Cheapest possible gate experiment. One day of engineering. Binary pass/fail with clear threshold. If it fails, saves months of wasted parse architecture work. If it passes, authorizes 10x engineering investment.
- HARD-PASS threshold: >= 88% POS accuracy on WSJ section 24
- HARD-FAIL threshold: < 75% POS accuracy on WSJ section 24

---

### Anchor 2: SUBSTRATE-BIGRAM-FLUENCY (n-gram superposition store)
- Anchor pointer: `notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md` Section 3, Architecture 3 + Section 4 (secondary decisive test)
- Substrate-product reading: Store top-100K English bigrams in substrate superposition; generate text via temporal policy; measure bigram coverage vs reference corpus. This tests the fluency path (Architecture 3) independently of parse. If it passes, structured-domain generation is unlocked without any LLM.
- Tier hint: CPU-local (corpus processing + FHRR superposition storage + generation sampling)
- Why now: Architecture 3 has the highest P_deflated (0.55) of all non-hybrid architectures. It is also the lowest engineering cost (2-3 months). This anchor validates the core mechanism in 1-2 days.
- HARD-PASS threshold: >= 70% bigram coverage in generated text vs reference
- HARD-FAIL threshold: < 40% bigram coverage (generation producing unnatural sequences)

---

### Anchor 3: FHRR-FCG-SMOKE (FCG-on-FHRR construction binding accuracy)
- Anchor pointer: `notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md` Section 3, Architecture 1
- Substrate-product reading: Port 3-5 English constructions from FCG to FHRR. Test: does FHRR binding correctly encode/decode role-filler pairs for SVO, ditransitive, caused-motion constructions? This is the pre-test gate for Architecture 1 (FCG-on-FHRR), which is the highest-value parse architecture (P_deflated 0.50, directly maps to 70% of English sentences).
- Tier hint: CPU-local (pure algebra; no corpus needed; construction schemas are small)
- Why now: The published existence proof is for HRR, not FHRR. The binding operations differ (circular convolution vs phase addition). This smoke test checks whether the port is straightforward before authorizing the 3-4 month FCG-on-FHRR project.
- HARD-PASS threshold: >= 80% decode accuracy for the 3-5 test constructions (role-filler round-trip)
- HARD-FAIL threshold: < 60% decode accuracy (FHRR binding incompatible with FCG-style schemas; need different binding scheme)

---

### Anchor 4: TEMPORAL-POLICY-GENERATION-ENGLISH (Architecture 5 connection)
- Anchor pointer: `notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md` Section 3, Architecture 5; also cap_map integ_temporal_policy (authorized, WAVE-5)
- Substrate-product reading: The integ_temporal_policy anchor is already authorized. The research note grounds it in biological predictive coding + n-gram LM theory. The experiment is: use temporal policy to generate English phrases from a substrate trained on a small domain corpus (50-100 sentences). Measure phrase naturalness (human eval on 20 generated phrases) and bigram coverage.
- Tier hint: CPU-local or remote CPU (corpus-trained substrate is small at domain scale)
- Why now: This is the convergence point between the authorized temporal policy work and the English-generation research finding. One experiment validates both the temporal policy mechanism AND the fluency path. Double-dipping on experimental value.
- HARD-PASS threshold: >= 70% bigram coverage + >= 60% phrases rated "natural" by human eval
- HARD-FAIL threshold: < 40% bigram coverage OR < 40% phrases rated natural

---

## Context pointers (file paths, not summaries)

- Research note: `d:/AI/hd-instrument/notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md`
- Prior LLM capability separation note: `d:/AI/hd-instrument/notes/research_drill_llm_capability_separation_substrate_5x_2026-06-08.md`
- Prior LLM integration survey: `d:/AI/hd-instrument/notes/research_drill_llm_substrate_integration_survey_5x_2026-06-09.md`
- Temporal policy authorization: WAVE-5 brief at `d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-10.md` (integ_temporal_policy listed as authorized)
- Cap map: `d:/AI/hd-instrument/notes/substrate_capability_map.md`
- VSA Survey Part II (external): https://dl.acm.org/doi/10.1145/3558000

---

## Contract

exp_dev is authorized to design and queue any of the above anchors. Anchor 1 (SUBSTRATE-POS-TAGGER) is the gate experiment and should be prioritized if CPU-local capacity is available. Anchors 2, 3, 4 can run in parallel with each other and with Anchor 1 if queue depth allows.

exp_dev does NOT need to consult research before designing experiment parameters for these anchors. The research note has established the mechanism and the HARD-PASS/HARD-FAIL bands. exp_dev owns the implementation.

## Autonomy declaration

exp_dev decides: all numerical parameters (N, M, K, seeds), queue routing (Tier A/B/C), smoke profile design, anchor naming convention, and whether to combine anchors into a single cell. This hand-off names mechanisms and thresholds only.
