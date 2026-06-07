# exp_dev hand-off -- research: wish-we-had 3x drill (counterfactual, multimodal, preferences)

Filed-by: research sub-agent
Trigger: notes/research_drill_wish_we_had_3x_2026-06-07.md (3x deep drill on top-3 wish-we-had substrate characteristics)
Pause state: check data/orchestrator_paused.flag before dispatching any anchor

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY. Exp_dev designs anchors, sweep parameters, thresholds, and queue placement. NOT this file.

---

## WHY NOW

The 3x drill establishes three implementable capability extensions ordered by risk and
engineering cost:

1. Wish 1 (counterfactual generation): builds directly on cycle 162 causal_gdpr_erasure_composition
   HP and cycle 162 deterministic replay HP. The constructive extension (substitute X' for X
   rather than erase X) is a small algebraic step. A 2-3 hour pre-test validates it before
   any engineering commitment. This is the lowest-risk capability extension available.

2. Wish 3 (customer preferences): extends existing continual learning + sleep defrag
   mechanisms. T-POP 2025 establishes that 20 feedback examples give 65%+ preference
   accuracy in continuous space. The open question is whether bipolar binarization
   preserves this. A 2-3 hour pre-test gates engineering authorization.

3. Wish 2 (multimodal): binary CLIP literature confirms < 0.003 nDCG loss at N=512.
   The substrate-specific risk is the PCA upsampling step (512 -> 4096). Pre-test on
   MSCOCO-val MUST happen before any engineering work begins. This is the highest-risk
   wish and should not proceed to engineering without HARD-PASS on the pre-test.

If Anchor 1 HARD-PASS: Wish 1 counterfactual generation gets v1.5 engineering authorization.
If Anchor 2 HARD-PASS: Wish 3 preference learning gets v2.0 engineering authorization.
If Anchor 3 HARD-PASS: Wish 2 multimodal gets v2.5 engineering authorization.
If Anchor 3 MID-BAND: revisit N=512 architecture (skip PCA upsampling) before committing.
If Anchor 3 HARD-FAIL: multimodal requires a redesign of the quantization pathway.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 -- Counterfactual generation pre-test (CPU, ~2-3 hrs)
Pointer: research note Section 1.6 (Wish 1 cheap decisive test)
Substrate-product reading: 20 synthetic counterfactual scenarios on a 500-fact KB.
Each scenario specifies original_binding, replacement_binding, expected_delta.
Measures: (a) derivation correctness (delta matches expected), (b) audit integrity
(Merkle replay succeeds on CF chain), (c) latency (< 5ms per scenario).
Tier hint: laptop CPU; no API needed; ~2-3 hrs wall
Why now: this is the lowest-risk gate in the entire wish-we-had roadmap. Cycle 162
erasure + deterministic replay are both HP'd. Constructive substitution is a small
algebraic extension. If this fails, something is wrong with the underlying machinery
(which is unlikely given existing HP evidence); if it passes, v1.5 is unblocked.

HARD-PASS: 100% derivation correctness + all Merkle replays succeed + < 5ms median
HARD-FAIL: any derivation error > 5% OR any Merkle replay failure

### Anchor 2 -- Customer preference pre-test (CPU, ~2-3 hrs)
Pointer: research note Section 3.8 (Wish 3 cheap decisive test)
Substrate-product reading: 100 synthetic QA pairs across 3 style preferences (concise /
verbose / tabular). 2 synthetic customers. Submit 20 rated answers per customer to
substrate preference layer. Query with 30 held-out questions per customer: measure
whether substrate routes toward historically preferred style.
Tier hint: laptop CPU; no API needed; ~2-3 hrs wall
Why now: T-POP 2025 establishes 65%+ preference accuracy from 20 examples in continuous
space. Bipolar binarization may degrade this. The pre-test is the only way to know.
If preference accuracy >= 65%, v2.0 preference learning architecture is validated.

HARD-PASS: preference accuracy >= 65% on held-out 30 questions per customer
MID-BAND: 50-65% (signal exists; may need more feedback examples or architecture tweak)
HARD-FAIL: < 50% (chance level; binarized preference binding not working)

### Anchor 3 -- Multimodal binary CLIP pre-test (CPU, ~2-3 hrs)
Pointer: research note Section 2.7 (Wish 2 cheap decisive test)
Substrate-product reading: CLIP ViT-B/32 on MSCOCO-val (5000 images, 25000 captions).
Binarize CLIP embeddings to bipolar at N=512 (no PCA upsampling).
Store 5000 image-text binding pairs in substrate.
Query with text: measure Recall@10 for image retrieval.
Query with image: measure Recall@10 for text retrieval.
Tier hint: laptop CPU (CLIP ViT-B/32 runs at ~50ms/image); ~2-3 hrs wall
Why now: binary CLIP literature says < 0.003 nDCG loss at N=512. The substrate-specific
risk is the bipolar sign-binarization step (not just floating-point binary). This test
determines whether CLIP + BSC is viable before committing 3-4 weeks of engineering.

HARD-PASS: Recall@10 >= 0.70 cross-modal in bipolar BSC at N=512
MID-BAND: 0.50-0.70 (architecture adjustment needed; N=512 may work with re-training)
HARD-FAIL: < 0.50 (binarization destroys CLIP alignment; major quantization redesign)

---

## CONTEXT POINTERS

Research note: d:/AI/hd-instrument/notes/research_drill_wish_we_had_3x_2026-06-07.md

Wish 1 (counterfactuals) detail: research note Sections 1.1-1.6
Wish 2 (multimodal) detail: research note Sections 2.1-2.8
Wish 3 (preferences) detail: research note Sections 3.1-3.8
Commercial impact ranking: research note Section 7
Engineering risk matrix: research note Section 8
Honest bounds: research note Section 9

Prior HP that motivates Anchor 1:
  data/exp_causal_gdpr_erasure_composition/metrics.json (cycle 162 HP)
  data/exp_deterministic_replay/metrics.json (cycle 162 deterministic replay HP)

Prior afternoon brief (state-of-day context):
  d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

---

## CONTRACT

Exp_dev owns: anchor design (which benchmark, which domains, which KB subset for Anchor 1;
which style types for Anchor 2; which MSCOCO split for Anchor 3), sweep parameters,
threshold calibration, queue placement, timing.

Research owns: the theoretical framework, the falsifiable predictions, and the
go/no-go interpretations (HARD-PASS / MID / HARD-FAIL bands in research note Sections
4 and 5).

If Anchor 1 HARD-PASS: escalate to orchestrator for v1.5 counterfactual engineering
authorization. The counterfactual generation feature moves from theoretical to roadmap-committed.

If Anchor 2 HARD-PASS: escalate to orchestrator for v2.0 preference learning engineering
authorization.

If Anchor 3 HARD-PASS: escalate to orchestrator for v2.5 multimodal engineering authorization.

If Anchor 3 MID-BAND: route back to research for N=512 direct-storage architecture
assessment before proceeding. Do not begin multimodal engineering until architecture
is clarified.

If Anchor 3 HARD-FAIL: route back to research for quantization redesign. No multimodal
engineering until a passing quantization path is identified.

---

## AUTONOMY DECLARATION

Exp_dev has full autonomy to sequence Anchors 1-3 in any order that fits the queue.
Anchors are independent (no dependency between them). Suggested sequence: 1 -> 2 -> 3
(ascending risk; confirms lowest-risk items first).

Exp_dev should NOT pad these anchors with unrelated experiments. Each anchor is a
targeted pre-test with a specific go/no-go gate. Run exactly the test described.
Return verdict with measured values vs HARD-PASS / MID / HARD-FAIL bands.
