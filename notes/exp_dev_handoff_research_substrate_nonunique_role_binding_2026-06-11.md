# exp_dev hand-off -- research: substrate non-unique-role binding (multi-occurrence) 2x DEEP

Filed-by: research sub-agent (2x DEEP drill)
Date: 2026-06-11
Trigger: research drill at notes/research_drill_substrate_nonunique_role_binding_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag (CPU-only experiments are routinely allowed during pause; check flag)

Per [[feedback-no-experiment-design-in-prompts]]: this file lists pointers and anchor-candidates; exp_dev owns the experiment design and pre-registration.

Per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]] and
[[feedback-dont-parrot-drill-defeatism-2026-06-11]]: empirical multi-occurrence
ASDiv HARD_FAIL is a CLEANUP CHOICE failure, not a substrate ceiling. Six
substrate-only paths enumerated; three executable as Tier-2 prototypes now.

## Anchor candidates (rank-ordered)

### Anchor 1 -- RESON-1 resonator-network triple-binding decoder (CPU, ~1-2 days)
- Pointer: research note section "RANK 1 -- Resonator network over (role x occurrence x filler)"
- Substrate-product reading: validates that substrate FHRR binding NATIVELY handles multi-occurrence via iterative factor cleanup (Frady-Kent 2020). If passes, substrate ships multi-instance role-decoding as Tier-2 bundle without architectural extension. Multi-occurrence ASDiv lifts from 0.108 -> >= 0.258. This is the strategic feature: "substrate decodes multi-instance bundles via biologically-grounded iterative cleanup, not LLM attention."
- Tier hint: Tier A (highest decisive value; lowest novelty risk; direct literature precedent)
- Why now: substrate Path-1 multi-hop selector test just HARD_FAILED on multi-occurrence ASDiv (0.108 vs heuristic 0.376); this is the next-step substrate-only rescue, not a closure

### Anchor 2 -- PERM-1 permutation-indexed occurrence binding (CPU, ~1 day)
- Pointer: research note section "RANK 2 -- Permutation-indexed occurrence binding (P^k for k-th instance)"
- Substrate-product reading: validates that random-permutation binding (Recchia-Jones 2015 -- 3x paired-associate capacity gain over circular convolution) handles multi-occurrence. Parallel candidate to Anchor 1; both can run in same lane.
- Tier hint: Tier B (parallel candidate; cheaper than Anchor 1)
- Why now: complements Anchor 1 by testing whether the win is iterative-cleanup (RANK 1) or distinct-bind-targets (RANK 2); informs substrate-product positioning

### Anchor 3 -- GHRR-1-MULTI extension of authorized GHRR pilot (CPU, ~half day)
- Pointer: notes/research_to_exp_dev_GHRR_NONCOMMUTATIVE_PILOT_2026-06-11.md (already authorized) + this drill section "RANK 3 -- GHRR noncommutative matrix binding"
- Substrate-product reading: validates substrate v4.0 architectural lineage. Noncommutative binding gives NATIVE order-sensitivity; k-th occurrence is bound at matrix position k. Compose with already-authorized GHRR pilot.
- Tier hint: Tier B (substrate-v4.0 exploration; cheap)
- Why now: GHRR pilot already filed; multi-occurrence variant is a small extension

### Anchor 4 -- BUMP-1 cleanup-to-K-nearest (CPU, ~2 days)
- Pointer: research note section "RANK 4 -- Bump-attractor cleanup over filler-subspace"
- Substrate-product reading: simplest possible fix -- replace argmax cleanup with top-K threshold cleanup. May suffice when number of same-role items is small (K <= 3). Run if Anchors 1-3 ambiguous.
- Tier hint: Tier C (defer unless Anchors 1-3 are mixed)
- Why now: very cheap, near-zero implementation risk; useful as a floor

### Anchor 5 -- PHASOR-BAND-1 sub-band phase coding (CPU, ~2 days) -- substrate-novel
- Pointer: research note section "RANK 6 -- Phasor sub-band phase coding"
- Substrate-product reading: substrate-novel mechanism (no direct VSA literature precedent); brain-grounded in theta-gamma sub-cycles. Would be PUBLISHABLE if it works. Run only after Anchors 1-3 if positive momentum.
- Tier hint: Tier C (substrate-novel; speculative)
- Why now: lit-scan returned no direct VSA precedent; substrate-product novelty value if HP

## Pre-registered thresholds (per research drill section c)

| Anchor | HARD-PASS (abs pt lift over 0.108) | HARD-FAIL | MIDDLE | P_deflated |
|---|---|---|---|---|
| RESON-1 | >= 15 (>= 0.258) | < 3 | 3-15 | 0.45 |
| PERM-1 | >= 10 (>= 0.208) | < 3 | 3-10 | 0.40 |
| GHRR-1-MULTI | >= 12 on SVAMP asym | < 3 | 3-12 | 0.32 |
| BUMP-1 | >= 8 | < 2 | 2-8 | 0.30 |
| PHASOR-BAND-1 | >= 8 | < 2 | 2-8 | 0.28 |

Ensemble: P(>= 1 of top-3 HARD-PASSES) = 0.65.

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_substrate_nonunique_role_binding_2x_2026-06-11.md (this drill)
- d:/AI/hd-instrument/notes/research_drill_phase4_math_role_binding_2x_2026-06-11.md (bipartite-matching composes downstream of resonator decode)
- d:/AI/hd-instrument/notes/research_to_exp_dev_GHRR_NONCOMMUTATIVE_PILOT_2026-06-11.md (Anchor 3 base)
- d:/AI/hd-instrument/notes/research_drill_position_binding_symmetric_w_trigram_explanation_2x_2026-06-11.md (heteroassociative capacity precedent; beta~3-7 margin)
- d:/AI/hd-instrument/notes/research_drill_operator_algebras_subfactor_theory_2x_2026-06-11.md (GHRR theory ground)
- d:/AI/hd-instrument/notes/research_drill_substrate_proposed_architectures_2x_2026-06-11.md (substrate-v3.2 wrapper context)
- Substrate FHRR primitives: hdlab/fhrr.py (bind, unbind, cleanup -- exp_dev knows location)

## Contract

- Pre-reg per envelope-fail-bands; HP/HF thresholds specified in research drill section (c); exp_dev may tighten further at design time
- Smoke gate before full ASDiv-1op multi-occurrence-subset eval
- Ship via queue_add per local-CPU queue convention (cpu_runner_local on FrameworkMPC if home is busy)
- Post-ship REMOTE VERIFY
- Self-test per formula-selftests
- Honest re-read of verdict_msg vs per-cell metrics

## Autonomy declaration

exp_dev owns:
- exact ASDiv multi-occurrence subset definition (multi-COUNT vs multi-RATE vs mixed)
- N value (research suggests N=4096 per prior heteroassociative capacity drill; exp_dev may sweep)
- codebook construction for role / occurrence / filler (research suggests small ~10/5/7 codebooks per-problem; exp_dev refines)
- resonator iteration count + convergence criterion (research suggests 50 iter; exp_dev sweeps)
- explaining-away threshold for multi-triple recovery
- permutation choice for PERM-1 (research suggests fixed-random; exp_dev may try cyclic-shift as cheaper alternative)
- GHRR m-dial value for Anchor 3 (research suggests m=4 per prior pilot; exp_dev may sweep)
- ordering and lane allocation across the 5 anchors
- whether to compose with bipartite-matching downstream (research recommends yes for RESON-1; exp_dev may run standalone first)

Research declines to specify these.

## Cross-thread synthesis note

This hand-off is the RESCUE PATH for the multi-occurrence HARD_FAIL on Path-1
multi-hop selector test. It is NOT a re-run of the failed test. It is the
next-step substrate-only enumeration per
[[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]]: 6 paths
enumerated, 3 executable now, 3 in pipeline; biology has theta-gamma +
bump-attractor + parietal-cardinality + ant-task-allocation existence proofs
for ALL of them.

The architectural conclusion "FHRR binding cannot disambiguate non-unique
role assignments" is REVISED per literature-is-not-oracle to: "FHRR
single-shot cleanup cannot disambiguate; FHRR iterative resonator-network
cleanup CAN, and at problem-scale codebook sizes the literature shows >= 90%
factor recovery."
