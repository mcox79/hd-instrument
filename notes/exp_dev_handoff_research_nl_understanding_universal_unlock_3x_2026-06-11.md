# exp_dev hand-off -- research: NL understanding universal unlock 3x

**Filed:** 2026-06-11 by research sub-agent (Sonnet, 3x breadth+synthesis).

**Trigger:** Research note at:
  d:/AI/hd-instrument/notes/research_drill_nl_understanding_universal_unlock_3x_2026-06-11.md

**Pause state:** Check data/orchestrator_paused.flag before dispatching any queued cells.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor name, ETA,
smoke profile, full profile. Research does NOT specify numerical parameters or implementation
details. Exp_dev reads the research note for mechanism rationale; designs all experiments
autonomously.

**Context summary:** NL spec interpretation (NL -> structured form) is the shared bottleneck
for math word problems + codegen + 20 other product tasks. Four independent streams (biology,
brain, physics, LLMs) converge on a three-layer architecture: (1) pattern match to stored
constructions, (2) frame-role binding of surface tokens to typed slots, (3) disambiguation
via predictive context. Substrate has native operations for all three. The gap is assembly
and domain-specific codebook population. Solving once unlocks 22 downstream tasks.

---

## Anchor candidates (rank-ordered, cheapest decisive first)

### Phase 0 -- Intent generalization diagnostic (run FIRST, 2-3 CPU hours)

**Anchor 1: NL-INTENT-50CLASS**
- Anchor pointer: Path E10 in research note (intent decoding generalization to 50+ classes)
- Substrate-product reading: PP-337 reached F1=1.000 on 8 intent classes. Does the substrate's
  cosine retrieval maintain separation at 50+ classes? This is a single-night CPU run that
  either confirms the product architecture or triggers the N-scaling path. If top-1 accuracy
  >= 0.90: substrate intent codebook scales to product-domain diversity; proceed to slot-filling.
  If top-1 accuracy < 0.75: route to N=8192 or hybrid LLM head.
- Tier hint: local_cpu_queue (PP-337 infrastructure reuse; extend intent codebook to 50 classes
  from Banking77 dataset; zero new mechanisms)
- Why now: PP-337 is the single most validated substrate NL primitive; scaling the intent
  class count is the minimum-cost generalization test before investing in full slot-filler.

---

### Phase 1 -- NL slot-filling benchmark build + frame-role baseline (after Phase 0 confirms)

**Anchor 2: NL-SLOTFILL-BENCHMARK-BUILD**
- Anchor pointer: "Cheap decisive test" section and E11 in research note
- Substrate-product reading: 500-item benchmark covering math word problems, code docstrings,
  customer support queries with ground-truth entity + quantity + intent + constraint slots.
  This is an infrastructure build (no model training); the benchmark enables ALL subsequent
  anchors in this series. Without it there is no shared evaluation standard.
- Tier hint: local_cpu_queue (data construction + annotation; no training required)
- Why now: every subsequent anchor needs this benchmark; build it first.

**Anchor 3: NL-FRAME-ROLE-BASELINE**
- Anchor pointer: Path E7 in research note (substrate frame semantics via FrameNet top-200)
- Substrate-product reading: populate W_frames from FrameNet top-200 frames (download available).
  Run frame evocation on benchmark item verbs. Measure frame evocation F1 and role-filling F1.
  If frame evocation F1 >= 0.70: FrameNet-based frame codebook is valid; proceed to product-domain
  frame augmentation (math/code/support frames). If F1 < 0.55: generic FrameNet frames are too
  broad; filter to product-domain 50 frames only and retest.
- Tier hint: remote_cpu_queue (FrameNet download + frame encoding + eval; 6-8 hours)
- Why now: frame-role binding is the Priority-1 mechanism unlocking 15 of 22 downstream tasks;
  this is the earliest possible validation of that priority.

---

### Phase 2 -- Construction grammar + bidirectional Viterbi (after Phase 1 establishes baselines)

**Anchor 4: NL-CONSTRUCTION-50**
- Anchor pointer: Path E6 in research note (substrate construction grammar, Goldberg-style)
- Substrate-product reading: encode 50 English argument-structure constructions from Goldberg
  2006 as W_construction hypervectors. Test construction identification on benchmark.
  If construction-type F1 >= 0.80: W_construction encoding is viable; integrate with frame-role
  binding for compound slot-filler. If F1 < 0.55: route to CRF-with-substrate-potentials
  (see POS-STRONG-BAR anchor PATH-1 for CRF infrastructure).
- Tier hint: local_cpu_queue (construction encoding + eval; 3-5 hours)
- Why now: construction grammar is complementary to frame semantics -- frames evoke situation
  types, constructions encode argument patterns; both are needed for robust slot extraction.

**Anchor 5: NL-BIDIR-VITERBI-DISAMBIG**
- Anchor pointer: Path E5 in research note (bidirectional Viterbi for disambiguation)
- Substrate-product reading: extend PP-346 context-binding infrastructure to bidirectional
  Viterbi over the NL spec benchmark. Compare: forward-only slot-fill F1 vs bidir slot-fill F1.
  If bidir adds >= 0.03 F1: route ALL disambiguation-sensitive tasks through bidir path.
  If bidir adds <= 0.01 F1: skip bidir investment; local frame-role binding is sufficient.
- Tier hint: local_cpu_queue (PP-346 infrastructure reuse; 2-3 hours)
- Why now: PP-346 is validated infrastructure; bidir extension is low-cost; resolves whether
  long-range disambiguation is load-bearing for product-domain specs.

---

### Phase 3 -- Compound slot-filler + downstream task validation (after Phase 2)

**Anchor 6: NL-SLOTFILL-E11-COMPOUND**
- Anchor pointer: Path E11 in research note (compound NL spec extraction -- entity + quantity +
  intent + constraint slots combined)
- Substrate-product reading: this IS the cheap decisive test. Combines: E10 intent (Anchor 1),
  E7 frame-role (Anchor 3), E6 construction (Anchor 4), E5 bidir Viterbi (Anchor 5). Run on
  500-item benchmark. Measure: entity-slot F1, intent accuracy, end-to-end solvability match.
  If entity-slot F1 >= 0.85: substrate-native NL parsing is validated at product scale;
  proceed to downstream task integration (math word problem + codegen).
  If entity-slot F1 < 0.60: route to hybrid (substrate memory + LLM parsing head).
- Tier hint: local_cpu_queue (compound pipeline; 3-4 hours)
- Why now: this is the verdict anchor for the entire NL-parsing research thread.

**Anchor 7: NL-MATH-WORDPROBLEM-LIFT**
- Anchor pointer: E12 cross-modal grounding + downstream task 1 (math word problems) in
  research note
- Substrate-product reading: run current math word problem pipeline WITH and WITHOUT E11
  slot-filler as preprocessing. Measure: equation extraction accuracy, solvability rate.
  If solvability rate improvement >= 15%: NL parsing bottleneck is confirmed as dominant;
  integrate E11 as permanent preprocessing step for math task class.
  If improvement < 5%: NL parsing is not the bottleneck; investigate equation structure
  construction as the actual gap.
- Tier hint: local_cpu_queue or remote_cpu_queue (depends on existing math pipeline state)
- Why now: math word problems are the user's stated motivation; this is the direct validation.

---

## Context pointers (file paths, not summaries)

- Research note (full synthesis):
  d:/AI/hd-instrument/notes/research_drill_nl_understanding_universal_unlock_3x_2026-06-11.md

- Prior NL/LM substrate research (5x drill):
  d:/AI/hd-instrument/notes/research_drill_substrate_only_language_model_5x_2026-06-08.md

- PP-337 intent decoding (F1=1.000 on 8 classes; direct infrastructure for Anchor 1):
  d:/AI/hd-instrument/notes/  (check cap_map for PP-337 exact file)

- PP-346 context-binding disambiguation (direct infrastructure for Anchor 5):
  d:/AI/hd-instrument/notes/  (check cap_map for PP-346 exact file)

- PP-275 within-domain entity/relation extraction (0.899; infrastructure for E2/E7):
  d:/AI/hd-instrument/notes/  (check cap_map for PP-275 exact file)

- POS-STRONG-BAR research note (CRF with substrate potentials; fallback if E6 fails):
  d:/AI/hd-instrument/notes/research_drill_pos_strong_bar_substrate_only_paths_2x_2026-06-11.md

- POS OOV diagnostic + CRF infrastructure (parallel track, shares bidir Viterbi):
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_pos_strong_bar_substrate_only_paths_2x_2026-06-11.md

- Cross-domain retraction (PP-275 cross-domain claim retracted; within-domain 0.899 valid):
  d:/AI/hd-instrument/notes/substrate_cross_domain_retraction_2026-06-10.md

---

## Contract section

Exp_dev owns: anchor naming, N/M/K choices, queue routing, smoke gate design, threshold
bands per envelope-fail, timing, cell sequencing, pre-dispatch audits (speed + harden +
progress per [[feedback-pre-dispatch-speed-harden-progress-discipline]]).

Research owns: mechanism rationale (in the research note), P_deflated estimates, hard-pass
and hard-fail thresholds (pre-registered above in research note), routing logic on failure.

Exp_dev does NOT read this file for numerical parameters -- it reads the research note for
mechanism and calibration, then designs experiments autonomously.

---

## Autonomy declaration

Exp_dev has full autonomy to:
- Reorder anchors based on current queue depth and runner availability
- Batch compatible anchors onto a single runner to reduce queue turnaround
- Skip anchors whose infrastructure prerequisites are not yet built
- Escalate back to Research if a mechanism fails in a surprising way (not just below threshold)

Exp_dev should NOT:
- Pad the queue with construction-grammar variants if E11 returns HF-1 (entity-slot F1 < 0.60)
  before routing to hybrid
- Treat the 22-task roadmap as a guaranteed outcome; treat it as an architecture hypothesis
  to be validated one anchor at a time
- Design experiments that test mechanisms not in the research note without consulting Research
