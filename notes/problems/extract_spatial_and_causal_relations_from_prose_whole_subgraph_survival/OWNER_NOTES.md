---
owner_verdict: DONE
---

PARTIAL (pending your verdict) -- extract_spatial_and_causal_relations_from_prose_whole_subgraph_survival  (opus 4.8 solver)

Write-up: notes/problems/extract_spatial_and_causal_relations_from_prose_whole_subgraph_survival/SOLVED.md
 + FULL_CHAIN_BRAIN_FIDELITY_SCAN_2026-09-07.md + WALLS_FULLY_UNDERSTOOD_2026-09-08.md (same folder).
Reverify (scaffold-free; recomputes every headline from source; NO hdlab write, Q111):
  .venv/Scripts/python.exe verification/test_joint_spatial_causal_survival.py     # 11/11

THE PROBLEM: extend the joint parse-once front-end to SPATIAL (Figure-Ground/RCC8) + CAUSAL edges; headline =
whole-subgraph survival CI-sep over the incumbent on modern gold, twin losing, extraction isolated, full-stack
upstream, NO external LLM.

CORE RESULT (the original bar):
- SPATIAL = WIN on the brain-faithful axis. Building the brain's actual mechanisms (event-figure binding + deixis +
  coordination + partitive + Herskovits preposition-semantics + thematic-event nested binding, over an exact-MAP
  parse) beats the incumbent CI-sep on whole-subgraph containment survival (6/123 -> 16->20/123) AND, decisively, beats
  a no-semantics DENSITY floor +0.386 on precision-sensitive QA where that floor collapses (0.185). Precision held
  exactly. The semantic Figure-Ground TYPING is load-bearing; recall-survival alone was density-confounded.
- CAUSAL = the bar's blessed LOCATED NEGATIVE, mechanistically resolved. Retrieval refuted (CSKG 2% coverage on MAVEN,
  an EDGE gap not a vocab gap); the content-sensitive generative simulator is the right mechanism (beats twin +
  class-level on precision-on-fired) but coref-capped; the recency/iconicity prior is a strong brain-foundational
  baseline. Score causal at the EDGE level (multi-hop causal networks are shallow -- 30 chains/710 MAVEN docs).

THE FULL-CHAIN FIDELITY INVESTIGATION (owner-directed: scan all, drill all walls, prototype all fixes even out of scope):
- A 3-segment brain-fidelity scan + "do all" prototypes CONVERGED, via the owner's principle (a brain-foundational
  component that under-performs is starved by a non-brain-foundational UPSTREAM), on ONE keystone: the MEANING/ENTITY
  channel is built but never CONSUMED in read() (the reader reads meaning-blind).
- The UNIFYING LAW (measured): a channel clears the bar iff its cheap positional prior solves its sub-task. TEMPORAL
  (ORDER): iconicity 84% correct -> detection wins. CAUSAL (EXISTENCE): no cheap prior is both high-coverage +
  high-precision -> needs world-knowledge. SPATIAL (TYPE): proximity collapses to 18.5% -> needs the semantic typer.
- PROVEN LEVER: participant COREF lifts the causal simulator 3.29x (86->221 fires) with precision UP 0.465->0.535.
- FULL-FIX FINDING (measured): the meaning channel's read()-time value is CHANNEL-SPECIFIC -- coref carries CAUSAL,
  thematic binding carries SPATIAL (coref a no-op there), and the SENSE-consumption/control half pays off on the
  MEANING READOUT, not extraction. Not one blanket wire; three distinct consumers.
- 8 of 9 walls fully understood (WALLS doc); each a proven WIN, a proven located negative with residual named, or a
  refuted dead-end. A real bug was found + fixed in my own causal cell (valence double-centering; caught by verify-on-disk).

THE FIXES (next high-priority, SOLVED "NEXT STEPS"):
  A. LAND NOW (proven, default-off/additive, no-regress; strategy owns the hdlab wire, Q111):
     P1 unified one-parse front-end (4x fewer parses, byte-identical); P2 spatial thematic binding + learned
     construction inventory (recall 0.298->0.369, precision held, generalizes); P3 nominal-event detection flip-on
     (detectable ceiling 0.61->0.85); P4 exact-MAP decode default (removes 7.2% invalid trees); P5 coref->causal
     simulator (proven 3.29x).
  B. BUILD (the two residuals, out of solver write-scope):
     P6 the read()-time meaning-consumption + control-network stage (word-sense/meaning-channel problem) -- the
     meaning-READOUT fix; P7 the spatial parser residual (span-head canonicalization, participle-as-head, PP-scope +
     the incremental/predictive parser); P8 the full causal reader = recency prior (recall) + coref-unlocked simulator
     (precision) as a graded graph, ACCEPTING the causal-recall ceiling on unmarked abstract edges as the honest
     no-LLM limit.
  C. DO NOT land: CSKG/bigger-KB (2%), parse-marginal-attachment (parse already 99.9% confident), object-affordance
     grounding (register-bound), connective causal extractor (0.5%), POS memoization (0.94x); recall-survival as the
     spatial metric; whole-subgraph survival as the causal metric.

CONTROLS: shuffled-relation twin loses on both channels; the density floor (proximity/contiguity) matches on recall
but COLLAPSES on precision (the binding axis); incumbent floor per channel; reasoner held at gold (extraction
isolated); marked-vs-unmarked split; no-regress (witness 11/11; nothing landed in hdlab).

FILES: ~17 experiment cells + verification/test_joint_spatial_causal_survival.py (11/11) + 3 notes. NO hdlab written
(Q111 -- proposed diffs in SOLVED Sec 7). Every mechanism proven in experiments/; strategy lands.

KEY REALIZATIONS: (1) the unifying law -- a channel wins iff its cheap prior solves its sub-task; (2) recall-survival
is density-confounded, precision-on-fired is the binding axis; (3) the owner's principle held to the root -- every
under-performing brain-foundational component traces to the meaning/entity channel; (4) retrieval is coverage-bounded
by construction (the brain simulates, not retrieves); (5) verify on disk caught a real bug in my own cell.

QUESTIONS: one -- SOLVED vs PARTIAL. SPATIAL clears the bar (survival CI-sep + precision) and every wall is understood
with its fix proven or refuted, so SOLVED is defensible; I deflated to PARTIAL because causal has no CI-sep survival
WIN (it is the blessed located negative) and the keystone wire is strategy's to land. Science identical either way.
