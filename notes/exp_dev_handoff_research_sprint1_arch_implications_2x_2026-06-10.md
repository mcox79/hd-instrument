# exp_dev hand-off -- research: sprint1_arch_implications_2x

Filed-by: research sub-agent (sonnet)
Date: 2026-06-10
Trigger: notes/research_drill_sprint1_arch_implications_2x_2026-06-10.md

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: sprint1_multiseed_promotion_v1 (SPRINT1-MULTISEED)

Anchor pointer: Research note Section 6.1 GAP-1 + Section 10 GATE-1; all five sprint-1 result files in data/exp_*/metrics.json.
Substrate-product reading: Re-run all five sprint-1 experiments (comm1_paragraph_compose, math1_algebra_simplify, code1_function_compose, math3_calculus_derivative, math4_proof_chains) with n_seed=5 each. Reports mean and std per metric. If all five achieve mean > 0.95 and std < 0.05, the single-seed promotion gate is cleared and these results are defensible for product claims. This is the BLOCKING gate before any downstream benchmark or comparison work.
Tier hint: CPU-local laptop. All five are pure numpy/pure substrate operations (sub-1-second each at n=400). Five seeds x five experiments = 25 runs, each under 5 seconds. Total wall time under 5 minutes. Zero cloud, zero GPU.
Why-now: Single-seed results cannot appear in any product claim. This is the cheapest ($0, 5 min) path to converting exploratory rung-1/2 results into defensible multi-seed benchmarks. Highest priority of all anchors in this handoff.

Pre-reg bands:
  HARD-PASS: mean >= 0.95, std <= 0.05 for ALL five tests across n_seed=5
  MIDDLE-BAND: mean 0.85-0.95 OR std 0.05-0.10 for any test (single-seed ceiling was lucky; variance present but manageable)
  HARD-FAIL: mean < 0.85 OR std > 0.10 for any test (n=1 artifact; results not generalizable; exploratory claims must be downgraded to "preliminary existence proof only")

### Anchor 2: math4_proof_chains_full_depth_v2 (MATH4-FULL)

Anchor pointer: Research note Section 8 PRIORITY 2 + Section 9 PATH-1 + Section 11 PRED-2; math4_proof_chains_cpu_v1 metrics.json (SMOKE only, lengths 2/4/6).
Substrate-product reading: Run math4 proof chains at lengths 2/4/6/8/10 with at least 3 seeds. Extend the proof rule vocabulary to include disjunctive syllogism and hypothetical syllogism in addition to modus ponens. The SMOKE run covered modus ponens at lengths 2/4/6 only. Biology (ACT-R / working-memory model) predicts failure at length > 7. This is the most directly falsifiable prediction from the research drill and directly probes the upper boundary of substrate-only deductive reasoning.
Tier hint: CPU-local. Pure substrate operation. All lengths up to 10 are trivially fast on CPU. The branching (disjunctive syllogism) requires a forked-workspace mechanism -- exp_dev should assess whether this requires new code or can be done within existing cleanup chains.
Why-now: math4 is on SMOKE verdict only. FULL run at length 10 with branching is required before any claim about substrate deductive reasoning depth. The biological ceiling prediction (failure at length > 7) is the key test of whether the sprint-1 results scale or plateau.

Pre-reg bands:
  HARD-PASS: mean accuracy >= 0.80 at length 10 (straight modus ponens) AND >= 0.65 on disjunctive syllogism
  MIDDLE-BAND: accuracy 0.50-0.80 at length 10 (degradation present but not catastrophic; characterize the length at which accuracy crosses 0.80)
  HARD-FAIL: accuracy < 0.50 at length 8 (biological working-memory ceiling hit earlier than predicted; substrate cannot sustain long deductive chains without hierarchical cleanup; MATH4 claim must be bounded to length <= 7)

### Anchor 3: math1_algebra_adversarial_v1 (MATH1-OOD)

Anchor pointer: Research note Section 9 PATH-3 + Section 10 GATE-3 + Section 11 PRED-3; math1_algebra_simplify_cpu_v1 metrics.json (clean inputs only).
Substrate-product reading: Run algebra test with 20% of inputs constructed to be near-OOD: expressions using notation variants not in the training rule set (e.g., a*a instead of a^2, or equivalent forms that require a rewrite before the stored rule matches). Measures two things: (1) OOD accuracy (does substrate gracefully degrade or confabulate?); (2) uncertain-flag rate (does the cleanup margin correctly signal low confidence on OOD inputs?). The worst case is confident-wrong (high cleanup margin + incorrect answer); a rate > 20% on OOD would require retracting the "zero hallucination on in-distribution" product claim.
Tier hint: CPU-local. Requires constructing the OOD test cases (the main work), not a new algorithm. OOD construction is a data-engineering task.
Why-now: The current HARD_PASS at 1.000 is on fully-in-distribution inputs by construction. Before any product claim about algebra accuracy, OOD robustness must be characterized. This is the single most important gap identified in the research drill.

Pre-reg bands:
  HARD-PASS: OOD accuracy >= 0.40 AND uncertain-flag rate on OOD >= 0.70 (substrate gracefully degrades; uncertain signal is reliable)
  MIDDLE-BAND: OOD accuracy 0.20-0.40 OR uncertain-flag rate 0.40-0.70 (partial graceful degradation; needs improvement but not catastrophic)
  HARD-FAIL: confident-wrong rate > 0.20 on OOD inputs (substrate produces wrong answers with high confidence; product claim on in-distribution accuracy must be paired with explicit OOD caveat in all external communications)

### Anchor 4: code1_function_compose_scale_v2 (CODE1-SCALE)

Anchor pointer: Research note Section 9 PATH-2 + Section 8 PRIORITY 3; code1_function_compose_cpu_v1 metrics.json (prog_len=5, n=300).
Substrate-product reading: Extend code1 to prog_len=7 and prog_len=10 at n_seed=3. At prog_len=5, cleanup is within single-level range (biology predicts no failure below length 7). At prog_len=10, the biological model predicts the need for hierarchical cleanup between composition levels. If correctness stays at 1.000 through prog_len=10, the substrate's composition architecture is more robust than the biological model predicts. If it drops below 0.80 at prog_len=8-10, the failure onset characterizes the maximum reliable composition depth without mid-chain cleanup.
Tier hint: CPU-local. Pure substrate operation. Very fast at all lengths (sub-second per run). Can be bundled with math4 FULL in the same dispatch.
Why-now: CODE-1 at prog_len=5 is the shortest realistic program. Production code tasks (HumanEval, real function composition) require prog_len=10-20. Scaling test is the first rung toward production-grade code composition claims.

Pre-reg bands:
  HARD-PASS: correctness >= 0.95 at prog_len=10 across n_seed=3
  MIDDLE-BAND: correctness 0.70-0.95 at prog_len=10 (degradation present; characterize failure onset length)
  HARD-FAIL: correctness < 0.60 at prog_len=8 (substrate cannot reliably compose programs beyond trivial length; code composition claim must be bounded to prog_len <= 7)

### Anchor 5: math1_math3_benchmark_subset_v1 (MATH-BENCHMARK)

Anchor pointer: Research note Section 8 PRIORITY 4 + Section 11 PRED-4; Hendrycks et al. 2021 MATH dataset.
Substrate-product reading: Select 50 level-1 algebra problems and 50 level-1 calculus problems from the MATH benchmark dataset. Build a rule store from common algebraic identities and derivative rules (the same rules used in sprint-1). Run substrate on the 100 benchmark problems. Report accuracy vs published LLM baselines on MATH level-1 (GPT-4: ~50%; Qwen-7B: ~30%). If substrate exceeds 0.70 on benchmark problems, the product claim is anchored to a published external standard. If below 0.40, the codebook coverage is too thin for real math problems and the claim must be retracted.
Tier hint: CPU-local. Requires (a) downloading/subset-selecting MATH dataset and (b) running the existing math1/math3 experiments on those inputs. The MATH dataset is publicly available. Main engineering cost is input parsing (convert LaTeX expression to substrate codebook representation -- this is a non-trivial NLP step that may require LLM assistance for parsing, not for problem-solving).
Why-now: Without a benchmark anchor, the sprint-1 results exist in isolation. A single published benchmark comparison converts "substrate achieves 1.000 on constructed inputs" to "substrate achieves X on standard benchmark vs Y for LLMs" -- a claim with real competitive context.

Pre-reg bands:
  HARD-PASS: accuracy >= 0.70 on MATH level-1 natural problems
  MIDDLE-BAND: accuracy 0.40-0.70 (coverage gaps exist; need to expand rule store; document which rule types are missing)
  HARD-FAIL: accuracy < 0.40 (natural math expressions are too far from substrate codebook; production math claim requires substantial rule-store engineering work before any benchmark comparison is honest)

---

## Context pointers

- Research note: notes/research_drill_sprint1_arch_implications_2x_2026-06-10.md
- Sprint-1 results: data/exp_comm1_paragraph_compose_cpu_v1/metrics.json, data/exp_math1_algebra_simplify_cpu_v1/metrics.json, data/exp_code1_function_compose_cpu_v1/metrics.json, data/exp_math3_calculus_derivative_cpu_v1/metrics.json, data/exp_math4_proof_chains_cpu_v1/metrics.json
- Biology architecture reference: notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md
- Compositional cliff crossing: memory entry "Substrate v3.0 compositional cliff crossed 2026-06-10"
- Primitives-yes-integration-no: memory entry "Substrate primitives YES integration NO 2026-06-10"
- Long-form generation framing: notes/research_drill_substrate_long_form_generation_2x_2026-06-10.md
- Reasoning/math/code prior drill: notes/research_drill_reasoning_math_code_2x_2026-06-07.md

---

## Contract

Research has identified the architectural significance of the sprint-1 ceiling results and established the specific gap analysis. Exp_dev's task is to validate those results to production-grade standards using the ranked anchors above. The most urgent item (Anchor 1: multi-seed promotion) is a 5-minute CPU run that can be dispatched immediately. Anchors 2-5 follow in order of the production-gate criteria in Section 10 of the research note.

## Autonomy declaration

Exp_dev selects which anchors to dispatch in which order based on queue depth, runner availability, and the production-gate priority sequence. Research does not prescribe dispatch timing. Exp_dev may bundle Anchors 1+2+4 in a single CPU dispatch (all are fast, pure-substrate operations). Anchors 3 (OOD test construction) and 5 (MATH benchmark parsing) require additional data engineering that exp_dev should assess before dispatch.
