# exp_dev hand-off - research: phase4 math word problem role binding

Filed-by: research sub-agent
Trigger: research_drill_phase4_math_role_binding_2x_2026-06-11.md HEADLINE
  refutes "dep-parser needed" conclusion; proposes cheap bipartite-matching
  prototype that can decisively pre-empt a multi-day parser build.
Pause state: respect data/orchestrator_paused.flag - this is a research
  hand-off, not a ship instruction. exp_dev decides timing.

Per [[feedback-no-experiment-design-in-prompts]] this file lists ANCHOR
candidates only; no inline experiment design. exp_dev composes the actual
cell on pickup.

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY): bipartite-matching role-assigner prototype

- Anchor pointer: substrate Tier-2 bundle "role-assignment-bipartite-matching"
- Substrate-product reading: solves the role-binding limiter via structured
  optimization over existing features (unit-cue + verb-frame + position +
  quantifier-adjacency) rather than adding a dependency parser. Aligns
  substrate-LLM-boundary memory (substrate = structural reasoning).
- Tier hint: prototype-level. Substrate-classical (count-based table) +
  Hungarian-algorithm (O(n^3), n <= 10). No neural training.
- Why-now: research drill REFUTES "dep-parser needed" framing; 2-3 day build
  vs multi-day parser. Decisive in either direction (HARD-PASS kills
  parser build; HARD-FAIL justifies it). High-information-per-day.
- Cheap decisive test specified in research note section "Cheap decisive test"
- HARD-PASS / HARD-FAIL thresholds pre-registered in research note.

### Anchor 2 (FALLBACK): verb-frame lookup table expansion

- Anchor pointer: Tier-2 bundle "verb-argument-frame-table" (~100 verbs)
- Substrate-product reading: low-cost feature expansion that feeds Anchor 1
  cost matrix. Can be built standalone; tests whether verb-frame coverage
  is the bottleneck rather than inference.
- Tier hint: data-side prep; few hours to compile from training set.
- Why-now: cheap, composable, useful even if Anchor 1 HARD-FAILS (still
  helps any downstream role-binding approach including parser-based).

### Anchor 3 (DIAGNOSTIC): error decomposition into morphosyntactic vs
  verb-argument streams

- Anchor pointer: diagnostic cell, no new substrate bundle.
- Substrate-product reading: matches cog-neuro two-stream architecture
  (frontal morphosyntactic + parieto-temporal verb-argument). Decomposing
  current role-binding errors into these two classes tells us which stream
  is the actual bottleneck.
- Tier hint: ~1 day; pure analysis on existing failed cases.
- Why-now: if errors are dominantly verb-argument-retrieval, Anchor 2 is
  decisive. If dominantly morphosyntactic, shallow-syntactic features
  (chunking + POS) are decisive. Informs Anchor 1 cost-matrix design.

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_phase4_math_role_binding_2x_2026-06-11.md (this drill)
- memory: substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md
  (count-based methods stored as Tier-2 bundles BEAT phasor-only - precedent)
- memory: substrate_LLM_boundary_decomposition_2026-06-10.md
  (substrate = structural reasoning; role-assignment IS structural)
- memory: drill_pattern_temporal_contextual_not_structural_2026-06-11.md
  (drill predictions about FIXED architecture frequently FAIL; cap parser
   conclusion's P_deflated low until prototype runs)

## Contract section

This hand-off does NOT specify cell-level experiment design. exp_dev owns:
- cell composition (smoke gate, pre-reg per envelope-fail-bands)
- choice of queue lane (laptop CPU likely sufficient: O(n^3) matching,
  small n, ~100s problems)
- self-test per formula-selftests
- REMOTE VERIFY post-ship.

Research owns: HARD-PASS / HARD-FAIL thresholds and the cost-matrix feature
list, both in the parent research note.

## Autonomy declaration

exp_dev may:
- Pick which anchor to ship first based on queue depth and architect priorities.
- Defer if architect explicitly prefers the dep-parser path (in which case
  log decision + reasoning to status_log).
- Compose Anchor 1 and Anchor 3 in parallel (diagnostic + prototype) if
  CPU queue has capacity - they share no critical path.
- Scope down Anchor 2 to top-50 verbs if compile-time becomes a concern.

exp_dev SHOULD NOT:
- Combine all three anchors into a single mega-cell - decisive-test
  discipline requires Anchor 1 standalone first.
- Train any neural component for Anchor 1 - the literature precedent
  (Quantity Tagger, Kushman template, Hosseini verb-cat) used
  hand-engineered + light-learned features and reached competitive
  performance; substrate should mirror that.
