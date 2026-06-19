# exp_dev hand-off - research: substrate vs 7B/70B-class LLM head-to-head benchmarking methodology

Filed-by: research:opus
Date: 2026-06-11
Trigger: 2x DEEP research drill on cross-scale benchmarking methodology
Research note: notes/research_drill_substrate_vs_larger_llm_methodology_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHOR CANDIDATES with substrate-product reading + tier hint + why-now. exp_dev OWNS the exact cell design, smoke gate, queue routing.

## Anchor candidates (rank-ordered)

### Anchor 1 - Cross-scale measurement-harness pilot (highest priority)

Pointer: research note section (b) and section (c) Axes 1-4
Substrate-product reading: builds the substrate-side measurement infrastructure (RAPL/IPMI J/inference reader, RSS profiler, p50/p99 latency capture, deterministic-bit-exactness self-test) that the four-axis cost-normalization table requires. Without this harness no head-to-head claim is publishable.
Tier hint: TIER-1 infrastructure; needed for ALL subsequent commercial-claim work
Why now: substrate accuracy results (PP-225 kb25k 0.996, POS 0.906, SVAMP 0.30+) are real but currently unaccompanied by normalized cost/latency/energy numbers; commercial demo within 5-7 weeks requires the table
Decisive HARD-PASS: harness produces stable J/inference (variance less than 10%), p99 ms, RSS MB on three test benchmarks (IMDB, SST-2, kb25k closed-recall) in under 4 CPU-hours
Decisive HARD-FAIL: any one measurement column has variance above 50% across 5 runs

### Anchor 2 - Llama-3-8B accuracy-parity probe on saturating benchmarks

Pointer: research note section (b) step 3 and section (c) Axes 1-4 HARD-PASS thresholds
Substrate-product reading: produces the iso-accuracy point for IMDB / SST-2 / closed-KB-recall against Llama-3-8B; this is the row in the public 4-axis table. Single H100 hour budget.
Tier hint: TIER-1 once Anchor 1 ships
Why now: the relative-size-match comparison (Qwen2.5-0.5B) is too weak to make the commercial claim breadth; 8B is the credible upper anchor
Decisive HARD-PASS: substrate matches Llama-3-8B within 2pp accuracy on at least 2 of 3 saturating benchmarks AND wins at least 3 of 4 cost-axes at the HARD-PASS thresholds in research-note section (c)
Decisive HARD-FAIL: substrate loses more than 5pp accuracy on all 3 benchmarks (means saturation premise is wrong; need to rescope benchmark set)

### Anchor 3 - Closed-KB fact-recall MB-per-fact comparison

Pointer: research note section (c) Axis 4
Substrate-product reading: closed-KB MB-per-fact is the most defensible commercial axis (audit-trail per fact, deletable, regulator-friendly) and connects to EU AI Act Article 12 timeline. Run substrate on kb25k AND kb100k (once genuine kb100k extraction resolves) vs. parametric LLM recall on the same fact set.
Tier hint: TIER-1 commercial differentiator; regulator-facing
Why now: substrate kb25k genuine 0.996 is validated; the comparison number is missing
Decisive HARD-PASS: substrate MB-per-fact at least 10x more efficient than Llama-3-8B parametric recall at iso-accuracy on closed-KB benchmark (lit anchor: 125M params -> 1M Wikidata triples at 95%)
Decisive HARD-FAIL: substrate within 3x; rescope to per-fact provenance / deletability axis instead of pure storage

### Anchor 4 - Conformal coverage + determinism scale-invariant axes

Pointer: research note section (c) Axes 5-6; reuses conformal mechanism from notes/research_drill_substrate_conformal_calibration_2x_2026-06-11.md
Substrate-product reading: ships the calibrated-abstention column and the bit-exact-determinism column of the public 4+3 axis table. Both are scale-invariant (no amount of 70B parameter scaling closes either gap).
Tier hint: TIER-1 differentiator; pairs with Anchor 1 harness
Why now: conformal drill (today) gave the substrate-side mechanism; now extend that to head-to-head reporting
Decisive HARD-PASS: substrate produces coverage in [0.88, 0.92] at alpha=0.10 with n_cal=500 AND bit-identical output across 10 runs; Llama-3-8B at temperature=0 shows non-zero accuracy variance across 5 seeds on same prompts
Decisive HARD-FAIL: substrate coverage outside [0.85, 0.95]

## Context pointers (file paths, no summaries)

- notes/research_drill_substrate_vs_larger_llm_methodology_2x_2026-06-11.md (this drill)
- notes/research_drill_substrate_conformal_calibration_2x_2026-06-11.md (Axis 5 mechanism)
- notes/research_drill_substrate_frontier_scale_interaction_2x_2026-06-11.md (scaling argument)
- notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md (spectral observability)
- notes/substrate_capability_map.md
- memory: NORTH STAR FUNCTIONAL SYSTEM BEATS LLMS
- memory: Substrate-LLM BOUNDARY DECOMPOSITION 2026-06-10
- memory: PRODUCTION ARCHITECTURE LOCKED 2026-06-07

## Contract section

- pause-gated: respect data/orchestrator_paused.flag for cell dispatch
- self-tests required per formula-selftests for any new measurement primitive
- pre-reg envelope-fail-bands per anchor before dispatch
- smoke gate before any multi-hour run
- REMOTE VERIFY after queue_add for any cell touching production substrate

## Autonomy declaration

exp_dev owns:
- exact cell design (whether to colocate harness with existing eval cells or build standalone)
- queue routing (CPU lane for substrate measurements; GPU lane only for the 8B accuracy-parity probe)
- whether to defer 70B comparison until cheap GH/H200 access vs. use published TokenPowerBench numbers as initial stand-in
- which 3 saturating benchmarks to start with (research-note recommends IMDB / SST-2 / closed-KB-recall but exp_dev can substitute)
- HP/seed counts at the boundary

research:opus owns:
- methodology framework (the 4+3 axis split)
- HARD-PASS / HARD-FAIL thresholds in research-note section (c)
- update if any axis HARD-FAILs (file follow-on drill)
