# Research -> Exp Dev: PT-cascade-analogy companion handoff (Pred-5 reframing)

**Date**: 2026-05-24
**From**: Research session (2x adjacency-cascade drill follow-up to prior hierarchical-replay + 1-RSB drill)
**To**: Exp Dev session
**Trigger**: research drill closure; orchestrator-flagged 2x follow-up per [[feedback-2x-means-depth]]; companion to research findings note `notes/research_pt_cascade_drill_2026-05-24.md`
**Pause respect**: this is a routing FILE, not a queue_add; subject to `data/orchestrator_paused.flag` gating per [[feedback-obey-user-pause-explicitly]]. Exp Dev MUST check the pause flag and confirm with user before any queue_add.

---

## TASK (what)

Validate or refute the PT-replay-cascade analogy for the substrate, with specific focus on REFRAMING the Pred-5 cascade-depth sensitivity hypothesis.

The original Pred-5 framing (as carried forward from the hierarchical-replay rescue) implied a DISCRETE optimum in cascade depth matching basin / RSB hierarchy depth. The drill finds this framing has LOW prior probability per literature (~0.20-0.30 calibration-deflated). The HIGHER-prior framing is monotone-saturating improvement with depth, modulated by WHERE timescales concentrate relative to the substrate's effective "phase transition" (sharp task-shift / forgetting boundary).

Exp Dev's job is to design an experimental contract that DISCRIMINATES between these two framings cleanly, AND to instrument the substrate-side analog of the standard PT diagnostics so the cascade-design claim is falsifiable.

---

## WHY (relevance / impact)

1. **Pred-5 design correctness**: if exp_dev queues a cascade-depth sweep without pre-registering which framing is being tested, both framings are confirmable post-hoc — that is exactly the ex-post threshold-setting risk flagged in [[feedback-envelope-expansion-fail-bands]]. Pre-registration of "discrete optimum at k+1" vs "monotone-saturating + spacing-dependent" is required.

2. **Diagnostic instrumentation gap**: standard PT failure diagnosis uses replica round-trip histograms, acceptance-rate-vs-index profiles, and adjacent-energy-histogram overlap. If we cannot construct substrate-side analogs (which task / replay-timescale an item visited; how often it cycled; histogram overlap of adjacent timescale buffers), the analogy cannot be tested rigorously — only the OUTPUT (forgetting curves) can be observed and the CAUSAL claim (cascade-depth -> retention) cannot be isolated from confounding mechanisms.

3. **Rescue-path enabling**: if the cascade-depth analog DOES work, the literature gives 6+ rescue protocols when it underperforms (adaptive densification, policy-gradient adaptive scheduler, population-annealing-style alternative, infinite-swap limit, learned-global-move augmentation, multi-Markov-chain bridging). All are concrete and benchmarked. We get a rich rehab path inventory for free.

4. **Negative-result value**: if Pred-5 cleanly REFUTES the cascade-depth lever as a substrate mechanism, that is a valuable closure — it directs Strategy's attention away from cascade-design and toward the alternative levers (densification placement, learned-move augmentation, different sampling family).

---

## CONTRACT (what exp_dev must commit to upfront, per [[feedback-no-experiment-design-in-prompts]])

The following are CONTRACT requirements. Exp Dev fills in anchor names, sweep grids, threshold formulas, HF1/HF2/HF3 numerical bounds, queue choice, and ETA per their own design judgment and per [[feedback-strategy-spec-formula-selftests]] self-test discipline.

### C1. Pre-registration of competing hypotheses

The experiment design must pre-register at least TWO competing hypotheses with quantitative thresholds:
- **H_discrete**: cascade-depth performance has a sharp local optimum at some k* and degrades on both sides (U-shape or knee). Exp dev specifies the curvature / knee criterion.
- **H_monotone**: cascade-depth performance is monotone-saturating with no sharp peak; the relevant lever is timescale-spacing concentration, not absolute depth.
- Optional third: **H_null**: cascade depth has no measurable effect within stated noise envelope; the active mechanism is elsewhere.

The contract: pre-registered hard-fail bands per [[feedback-envelope-expansion-fail-bands]] for each hypothesis BEFORE shipping; ambiguity-handling rule for the middle band must be explicit.

### C2. Cascade-depth sweep

The sweep must span enough depths to discriminate H_discrete from H_monotone. Per literature, the operating regime is ~3 to ~sqrt(K_effective) for the substrate's K range; exp_dev sizes the grid to give at least 4-5 distinguishable depth values with seed-variance tight enough to identify a knee if it exists. Multi-seed required per [[project-research-playbook]] standard.

### C3. Spacing-concentration cross-cut

A clean test of H_monotone vs the cascade-depth lever requires HOLDING cascade depth fixed at multiple values and VARYING the spacing-concentration profile (uniform-geometric vs densified-at-transition vs random control). At minimum a 2x2 sweep (depth in {low, mid} x spacing in {geometric, densified}) is required to attribute effect to depth vs to spacing.

### C4. Diagnostic instrumentation

For the substrate-side analog of each of these PT-standard diagnostics, exp_dev must EITHER instrument it or document why it cannot be instrumented:

- replica-round-trip-equivalent: trace which timescale-buffer each replayed item resides in over training; histogram its traversal frequency
- acceptance-rate-equivalent: rate at which items in buffer k get used by training step (or get displaced into buffer k+1)
- adjacent-buffer-overlap: KL or L2 divergence between samples drawn from adjacent cascade buffers; if near-identical, the spacing is too tight; if disjoint, too sparse
- bottleneck localization: identify where in the cascade-traverse-rate the slowdown occurs (analog of replica-index dip)

If exp_dev cannot instrument these in <1 day of dev work, the experiment ships with a CAVEAT note that only output (forgetting curves) will be observed, and the causal claim is restricted accordingly per [[feedback-no-smoke]].

### C5. Spec self-test pairs

Per [[feedback-strategy-spec-formula-selftests]]: any closed-form computation in the cascade-depth or spacing-profile spec (e.g., a geometric spacing rule, a sqrt(K) depth heuristic, a KL-divergence formula) must include (input -> expected output) self-test pairs that exp_dev verifies BEFORE the smoke gate.

### C6. Composition classification

Per [[feedback-composition-classification]]: this experiment touches Cap 5 (Gap B online updates), retention metrics (Cap 1 or wherever forgetting-curves live), and possibly Cap 12 (BBMD-stress related per cap_map). Exp Dev MUST classify the composition as SCORE / HANDOFF / PIPELINE before queuing and document the chosen classification in the spec.

### C7. Dependency verification

Per [[feedback-ship-before-dependency-verified]]: the diagnostic-instrumentation work (C4) is a DEPENDENCY for the cascade-design claim; if the diagnostics are not instrumentable, the cascade-design experiment must be DOWNGRADED to a forgetting-curve-only sweep with explicit claim restriction. Verify before queue_add.sh.

### C8. ASCII discipline

Per [[feedback-ASCII-only-in-scripts]]: any verdict_msg / print() / log output uses ASCII only. No emoji, no em-dash. grep before queue_add.

---

## AUTONOMY (what exp_dev decides)

The following are exp_dev's calls, not Strategy's / Research's:

- specific anchor names, queue-naming convention
- numerical sweep grids (cascade depths sampled, spacing profile parameters, K values, N values)
- exact threshold formulas for H_discrete / H_monotone / H_null hard-fail bands
- HF1 / HF2 / HF3 numerical bounds
- queue choice (laptop CPU / remote CPU / GPU) per [[feedback-gpu-first-for-depth-probes]] (this is multi-seed depth-probe-style, lean GPU)
- ETA / wave grouping
- per-cell smoke gate and self-test design
- whether to ship as a single composite anchor or split across multiple anchors per [[feedback-multi-experiment-routing-notes]] H2-header schema
- which of the 6 rescue protocols (if any) to pre-stage as Tier-2 follow-ups if Tier-1 cascade-depth probe lands negative

---

## FALSIFIABLE PREDICTIONS (research's pre-registered claims, calibration-deflated)

These are Research's prior probabilities, pre-committed before exp_dev's data lands. Recorded for honest post-hoc calibration tracking per [[feedback-verdict-msg-honest-reread]]:

- **P(H_monotone with saturation at ~sqrt(K_eff) replay-timescales) = 0.55-0.65** (literature-preferred)
- **P(H_discrete optimum at k+1 for a k-RSB-like substrate hierarchy) = 0.20-0.30** (low-prior; capped below 0.50 per novel-synthesis rule)
- **P(H_null / cascade-depth has no isolable effect) = 0.15-0.25** (cannot rule out without instrumentation per C4)
- **P(spacing-concentration matters more than absolute depth | H_monotone) = 0.65-0.75** (this is the strongest single literature claim)
- **P(homogeneous-geometric spacing fails at substrate's analog of a phase transition) = 0.55-0.70** (Katzgraber 2006 result transfers if the analogy holds at all)

If Pred-5 lands such that H_discrete is supported and H_monotone is refuted, that REVISES the calibration upward toward our substrate having genuinely unusual landscape structure not captured by mainstream PT theory — itself a substantive finding worth committing to cap_map.

---

## OPEN QUESTIONS for exp_dev to surface back to Research (if any)

If exp_dev's design pass identifies any of the following, route back as `exp_dev_request_to_research_<date>_<slug>.md`:

1. Cannot find a clean substrate-side analog of replica-round-trip-histogram (the most diagnostically valuable PT instrument). If so, request Research to drill the PT-replay-analog INSTRUMENTATION question specifically.
2. Cascade-depth sweep cost exceeds practical compute budget (cap on n_seeds x n_depths x n_spacing-profiles). If so, request Research to identify which axis to prune based on which prior probability is largest in this drill.
3. Substrate's effective K_eff is unknown or hard to estimate (needed to bound the sqrt(K) cascade-depth range). If so, request Research to drill the K_eff estimation question.

---

## REFERENCES

- Full findings + literature citations: `notes/research_pt_cascade_drill_2026-05-24.md`
- Prior hierarchical-replay + 1-RSB drill (if discoverable): grep notes/research_R*, notes/research_BetE_*, notes/research_R23_*, notes/wave14e_hierarchical_composition_research.md
- Related research drill closure inventory: notes/research_decisions_2026-05-21.md (and successors)
- Substrate capability map: notes/substrate_capability_map.md
- Closest cap_map row to bump on positive finding: Field-C (statistical physics of inference), new neighbor row "PT-replay-cascade analogy"
- Closest cap_map row to close on H_null verdict: same row, mark closed with literature justification

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
