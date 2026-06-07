# exp_dev hand-off -- research: bridge-ID categorical closure (3x)

**Filed by:** research sub-agent
**Date:** 2026-06-07
**Trigger:** 3x deep drill on bridge-ID categorical barrier; synthesis of Paths A/B/C; user mandate
**Research note path:** d:/AI/hd-instrument/notes/research_drill_bridge_id_categorical_closure_3x_2026-06-07.md

---

## Pause state

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and why-now context. Exp-Dev designs the experiment implementation internally. No inline experiment code, parameter values, or training configurations are specified here.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- bridge_id_pretest_4way (PRIORITY; run before any v1.1 code)
**Anchor pointer:** Run the bridge-200 pre-test comparing four extractors on HotpotQA bridge questions: spaCy-lg, DistilBERT-NER, current-1.5B-LLM, and GLiNER with bridge-concept label.
**Substrate-product reading:** This pre-test is the gate for ALL v1.1 bridge-ID engineering. It answers: (a) does NER-upgrade help (DistilBERT vs spaCy), (b) does schema-free open-NER (GLiNER) outperform fixed-schema NER, (c) is the bottleneck extractable by any current method or requires training. Failure to run this wastes the entire v1.1 sprint budget on the wrong architecture.
**Tier hint:** CPU-only, approximately 2 hr wall. HotpotQA dev set is public. No GPU. No training.
**Why-now:** Self-improving routing drill (cycle 168 sim) confirmed bridge coverage is closeable by usage. Bridge-ID is the CONFIRMED separate bottleneck. Pre-test cost is 2 hr; delay cost is 3-5 eng-days wasted.
**HARD-PASS:** DistilBERT-NER >= 72% on bridge-200 top-1 accuracy.
**HARD-FAIL:** All four extractors < 65%; or DistilBERT-NER no better than spaCy-lg.
**GLiNER bonus threshold:** GLiNER >= DistilBERT + 5pp; if so, substitute GLiNER as Stage 1.

---

### Anchor 2 -- bridge_cross_encoder_ranker (if Anchor 1 HARD-PASS; +1 day add-on)
**Anchor pointer:** On the bridge-200 set, after Stage 1 NER produces top-3 candidates, apply cross-encoder (22M parameter MiniLM-derived model) to score each (question, candidate) pair. Measure bridge-ID accuracy: NER-only vs NER + cross-encoder rerank.
**Substrate-product reading:** Cross-encoder ranker adds 4-8pp over NER-alone at 100-150ms CPU overhead (per SIGIR 2025 literature). It is the most underrated option across all three bridge-ID drills. Zero training required. If this pre-test passes, Stage 2 of the v1.1 cascade should be cross-encoder rerank, not substrate-frequency-only. These can be composed (cross-encoder rerank then substrate-frequency filter).
**Tier hint:** CPU-only, approximately 3 hr wall. Model is a HuggingFace drop-in.
**Why-now:** The 3x drill surfaced this as a new angle. Literature confirms it adds 5-10 nDCG points consistently. Pre-test is cheap and the result directly changes v1.1 architecture Stage 2 design.
**HARD-PASS:** Cross-encoder adds >= 5pp over DistilBERT-alone on bridge-200.
**HARD-FAIL:** Cross-encoder adds < 2pp; Stage 2 reverts to substrate-frequency rerank only.

---

### Anchor 3 -- pre_seeded_bridge_dict_coverage (parallel with Anchor 2; 1 hr CPU)
**Anchor pointer:** Build a bridge entity dictionary from HotpotQA + 2WikiMultiHopQA public bridge annotations. Test coverage against a held-out sample of bridge-200 (or a separate 200-question sample from the same distribution).
**Substrate-product reading:** Pre-seeded bridge dictionary (New Direction 4 in 3x drill) provides cold-start bridge-ID at near-100% accuracy for covered entities. Coverage of 60-70% would lift cold-start bridge-ID to approximately 82% (60-70% exact from dictionary + 30-40% NER-cascade). This is the cheapest large lift. If coverage >= 60%, this should ship with v1.1.
**Tier hint:** CPU-only, approximately 1 hr wall. Data processing and dictionary build from public JSON files.
**Why-now:** Cold-start v1.1 P(2hop) is capped at approximately 0.59 without this. With it, approximately 0.66. The difference is material for the product benchmark claim.
**HARD-PASS:** Dictionary covers >= 60% of ground-truth bridge entities in held-out sample.
**HARD-FAIL:** Coverage < 40%; dictionary approach does not add meaningfully; Path A NER cascade is the only cold-start option.

---

### Anchor 4 -- bridge_substrate_copilot_zero_training (parallel; 2 hr CPU)
**Anchor pointer:** On 100 HotpotQA bridge questions, test substrate co-pilot: prepend top-3 substrate relation entries for the query to the LLM bridge-prediction prompt ("these entities may be relevant: [A, B, C]"). Compare bridge-ID: LLM-only vs LLM + substrate co-pilot.
**Substrate-product reading:** This is the zero-training alternative to Path C. If the co-pilot adds >= 5pp, it validates a zero-training lighter-weight Path C for v1.5 (no adapter training needed). If it fails, Path C requires the cross-attention adapter, which is 2-3 weeks of engineering.
**Tier hint:** CPU-only, approximately 2 hr wall. Uses existing substrate infrastructure and LLM.
**Why-now:** Path C decision (adapter vs prompt-conditioning) is binary and the answer is cheap to obtain now.
**HARD-PASS:** Substrate co-pilot adds >= 5pp over LLM-only on bridge-100 subset.
**HARD-FAIL:** Co-pilot adds < 2pp; Path C requires cross-attention adapter training (scope to v2.0).

---

### Anchor 5 -- bridge_cascade_v1 (gated on Anchor 1 HARD-PASS; v1.1 primary)
**Anchor pointer:** Implement the full bridge-ID cascade pipeline: (Stage 1) GLiNER or DistilBERT-NER based on Anchor 1 result, (Stage 2) cross-encoder rerank or substrate-frequency based on Anchor 2 result, (Stage 3) Pattern-B algebraic bridge fast-path, (Stage 4) LLM verify fallback, (Stage 5) substrate adversarial rejection filter.
**Substrate-product reading:** This is the v1.1 deliverable. Expected bridge-ID: 74-80% depending on Anchor 1-2 results. Expected P(2hop): 0.59-0.65 at cold start with pre-seeded dictionary. This closes the first engineering gap on multi-hop revival.
**Tier hint:** CPU-level serving (DistilBERT/GLiNER inference is CPU-feasible). Remote-CPU for scale testing with larger bridge question sets.
**Why-now:** All upstream pre-tests must pass first. This anchor is the implementation gate.
**HARD-PASS:** End-to-end bridge-ID >= 75% on bridge-200; P(2hop) >= 0.59 on HotpotQA distractor dev sample (50 questions).
**HARD-FAIL:** Bridge-ID < 68% after full cascade; indicates fundamental question-decomposition problem (not NER quality); route to LoRA path immediately.

---

### Anchor 6 -- bridge_lora_head_v1p5 (v1.5 sprint; after 500+ failure logs accumulated)
**Anchor pointer:** Fine-tune a LoRA bridge-entity extraction head on the existing 1.5B LLM using HotpotQA bridge annotations + accumulated deployment failure triplets. LoRA rank-4, InfoNCE contrastive objective on (query, gold-bridge-fact, retrieved-wrong-fact) triplets.
**Substrate-product reading:** Path B of the 3x drill. This is the v1.5 training investment. Expected bridge-ID: 78-82% at warm substrate. Expected P(2hop): 0.65-0.67 at coverage=0.92. Required training data: HotpotQA annotations (public) + 500+ deployment failure triplets (from v1.1 log).
**Tier hint:** Remote GPU (H100), approximately 2-4 hr training. Local eval on bridge-200 post-training.
**Why-now:** Cannot start until N_fail >= 500 from v1.1 deployment. Schedule: approximately 2-3 weeks after v1.1 ships at production query rate.
**HARD-PASS:** Post-LoRA bridge-ID >= 78% on held-out bridge-200 (not in training set).
**HARD-FAIL:** Post-LoRA bridge-ID improvement < 5pp over v1.1 cascade baseline; indicates encoder is not the binding bottleneck; route to larger LLM evaluation (Path D).

---

## Context pointers (file paths, not summaries)

- Primary research note: d:/AI/hd-instrument/notes/research_drill_bridge_id_categorical_closure_3x_2026-06-07.md
- Prior 2x bridge-ID drill: d:/AI/hd-instrument/notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md
- Prior 2x handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_bridge_id_accuracy_2026-06-07.md
- Self-improving routing drill (bridge coverage context): d:/AI/hd-instrument/notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md
- Authorization file: d:/AI/hd-instrument/notes/research_to_exp_dev_bridge_id_pretests_AUTHORIZE_2026-06-07.md
- Multi-hop research context: d:/AI/hd-instrument/notes/wave14e_multi_hop_reasoning_research.md

---

## Contract

Exp-Dev owns ALL implementation decisions:
- Which exact HuggingFace models to load (DistilBERT vs GLiNER vs spaCy versions)
- Exact threshold values for bridge confidence, entropy trigger, and co-pilot firing
- Test set construction details (how the bridge-200 sample is drawn and verified)
- Training configuration for Anchor 6 LoRA (rank, learning rate, batch size, epochs)
- Queue routing (CPU for Anchors 1-4; remote GPU for Anchor 6)

This file provides anchor pointers and HARD-PASS/HARD-FAIL bands. Exp-Dev does not reference specific numerical configurations from this file in experiment code.

## Autonomy declaration

Exp-Dev may sequence Anchors 1-4 in any parallel or serial order it judges optimal. Anchors 2-4 are designed to run concurrently with each other after Anchor 1 HARD-PASS confirmation. Anchor 5 blocks on Anchors 1-2. Anchor 6 blocks on v1.1 deployment and failure-log accumulation.

If Anchor 1 returns HARD-FAIL (all extractors < 65%), Exp-Dev should route directly to the pre-trained bridge predictor path (Anchor 6 equivalent without failure-log dependency, using HotpotQA annotations only) and skip Anchor 5 cascade architecture.
