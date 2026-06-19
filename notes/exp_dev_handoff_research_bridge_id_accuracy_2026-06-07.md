# exp_dev hand-off -- research: bridge-ID accuracy improvement strategies

**Filed by:** research sub-agent
**Date:** 2026-06-07
**Trigger:** 2x drill on bridge-ID accuracy bottleneck; user multi-hop revival mandate
**Research note path:** d:/AI/hd-instrument/notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md

---

## Pause state

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and why-now context. Exp-Dev designs the experiment implementation internally. No inline experiment code or parameter values are specified here.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- bridge_id_pretest_ner_comparison (PRIORITY)
**Anchor pointer:** Run the 200-question bridge-ID pre-test comparing DistilBERT-NER vs spaCy-lg vs current-1.5B-LLM on HotpotQA bridge questions.
**Substrate-product reading:** This pre-test is the gate for all v1.1 bridge-ID engineering. It answers whether the bottleneck is NER quality (fix with drop-in upgrade) or question understanding (fix with LoRA training). Running without this pre-test wastes 3-10 eng-days on the wrong path.
**Tier hint:** CPU, ~2 hr wall, no GPU needed. HotpotQA dev set is public download.
**Why-now:** The self-improving routing drill (3x, 2026-06-07) established bridge coverage growth is achievable. Bridge-ID is now the confirmed separate bottleneck. Pre-test cost is minimal; delay cost is the next sprint wasted on the wrong architecture.
**HARD-PASS:** DistilBERT-NER >= 72% on bridge-200.
**HARD-FAIL:** All extractors below 65%; OR DistilBERT-NER no better than spaCy-lg.

---

### Anchor 2 -- bridge_cascade_v1 (if Anchor 1 HARD-PASS)
**Anchor pointer:** Implement the 4-stage bridge prediction cascade: DistilBERT-NER + substrate-frequency-rerank + Pattern-B-algebraic-bridge + LLM-verify-fallback.
**Substrate-product reading:** This is the v1.1 engineering implementation. No training required. Expected bridge-ID lift from ~62% to ~72-76%. Expected P(2hop) improvement from ~0.54 to ~0.57-0.61. Sets the baseline that v1.5 LoRA head improves on.
**Tier hint:** CPU (DistilBERT-NER inference), remote-CPU for scale testing. Substrate bindings lookup is already implemented.
**Why-now:** Cascade requires Anchor 1 to confirm DistilBERT-NER achieves >= 72% before committing to this path.
**HARD-PASS:** End-to-end bridge-ID >= 73% on the same bridge-200 test set; P(2hop) >= 0.57 on HotpotQA distractor dev sample (50 questions).
**HARD-FAIL:** Bridge-ID < 68% after full cascade; indicates fundamental decomposition problem.

---

### Anchor 3 -- bridge_lora_head (if Anchor 1 HARD-FAIL OR v1.5 sprint)
**Anchor pointer:** Fine-tune a LoRA bridge-entity extraction head on top of the existing 1.5B LLM using HotpotQA bridge annotations. Token classification objective (BIO tags on bridge entity spans).
**Substrate-product reading:** This is the v1.5 path. Requires one training run (~2 hr H100). Pre-trained artifact ships with the substrate package (Option 11 productization). Achieves bridge-ID ~78-82%; P(2hop) ~0.63-0.68 at warm coverage=0.90. Needed to reach the 0.70 target.
**Tier hint:** Cloud GPU (H100, ~2 hr). HotpotQA training data download required first.
**Why-now:** Run only if Anchor 1 HARD-FAIL (DistilBERT-NER insufficient), OR after v1.1 cascade ships and the gap to 0.70 target is confirmed measurably.
**HARD-PASS:** LoRA bridge head >= 78% on held-out 500 HotpotQA bridge questions.
**HARD-FAIL:** LoRA bridge head < 70% after training; indicates 1.5B model is too small for supervised bridge extraction (escalate to 3B or 7B).

---

### Anchor 4 -- algebraic_bridge_integration (substrate-side, parallel to Anchors 1-3)
**Anchor pointer:** Integrate Pattern-B unbind as the fast-path bridge predictor in the multi-hop pipeline. At bridge coverage >= 0.70, route bridge prediction through Pattern-B instead of NER.
**Substrate-product reading:** This is the substrate's native bridge prediction capability. Requires no external NER or LLM for bridge-ID on covered bridges. Closes both bridge-ID and latency simultaneously for covered queries. This is the long-run moat: substrate self-improves bridge coverage AND uses that coverage for high-accuracy bridge prediction.
**Tier hint:** CPU, no training. Integration work (connect Pattern-B output to bridge-ID step of multi-hop pipeline).
**Why-now:** Pattern-B HARD-PASS confirmed at cycle 158. Bridge cache component confirmed at cycle 167. The integration connecting these to the bridge-ID step has not been built yet.
**HARD-PASS:** Pattern-B algebraic bridge achieves >= 85% bridge-ID on covered entities at simulated bridge-coverage = 0.85 (300 test questions, bridge entities pre-loaded into substrate).
**HARD-FAIL:** Pattern-B bridge-ID < 75% even at coverage = 0.85; indicates SNR degradation is corrupting bridge unbind in realistic bundle sizes.

---

## Context pointers

- Research drill (full findings): d:/AI/hd-instrument/notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md
- Prior self-improving routing drill: d:/AI/hd-instrument/notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md
- User multi-hop revival mandate: d:/AI/hd-instrument/notes/testbed_to_research_user_multihop_revive_mandate_2026-06-07.md
- Cycle 157 entity_bridge_decomp HARD-FAIL (empirical baseline for bridge-ID): scorecard
- Cycle 158 Pattern-B HARD-PASS (unbind foundation confirmed): scorecard
- Cycle 167 Phase-1 integration HARD-PASS (bridge cache + adversarial contradiction confirmed): scorecard
- BridgeRAG paper: arXiv:2604.03384 (April 2026; bridge-conditioned retrieval; analogous architecture)

---

## Contract

Exp-Dev reads this file, designs and ships the anchors per the why-now sequencing, routes results back via verdict files. Orchestrator reviews verdicts and updates cap_map. Research does not re-drill until Anchor 1 pre-test verdict is filed.

**Anchor 1 is a CPU pre-test. It should be runnable immediately (no cloud, no training, ~2 hr wall). Anchor 2 depends on Anchor 1 HARD-PASS. Anchor 3 can be prepared in parallel but should not run until Anchor 1 verdict is known.**

---

## Autonomy declaration

Exp-Dev has full autonomy to implement, sequence, and tune the anchors above within the constraints stated. No further orchestrator approval needed for Anchor 1 (pre-test). Anchors 2 and 4 (v1.1 cascade + algebraic integration) can be dispatched after Anchor 1 HARD-PASS. Anchor 3 (LoRA training, cloud spend) requires Anchor 1 verdict first per feedback-drill-pretest-required.

---

**END.**
