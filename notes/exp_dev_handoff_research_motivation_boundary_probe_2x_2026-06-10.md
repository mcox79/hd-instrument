# exp_dev hand-off -- research: intrinsic motivation architecture boundary probe 2x

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** Research drill confirmed that 4 of 5 intrinsic motivation primitives exist in the substrate, empowerment is computable from binding-space geometry, and the gap from "primitives exist" to "working motivation architecture" is a concrete build gap with 6 CPU-only empirical anchors. Research note at:
`notes/research_drill_motivation_boundary_probe_2x_2026-06-10.md`

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Why now

Research confirmed six empirical anchors that are:
- All CPU-only (no GPU, no cloud)
- All use existing substrate primitives (no new substrate code)
- The only new code is a small integration layer (~100-200 lines)
- Each anchor has pre-registered HARD-PASS + HARD-FAIL thresholds

This is low-cost, high-clarity work. Blocking on it delays confirming whether the motivation architecture is viable.

---

## Anchor candidates (rank-ordered)

### 1. MOTIV-CURIOSITY
- **Anchor pointer:** Research note Level 3, Section MOTIV-CURIOSITY; anomaly-margin-driven exploration test.
- **Substrate-product reading:** Validates that anomaly margin is a reliable novelty signal capable of driving spontaneous exploration without external reward. If this passes, self-directed knowledge acquisition is a confirmed product behavior.
- **Tier hint:** CPU local (50-trial simulation, synthetic two-chamber environment).
- **Why now:** Curiosity is the most foundational drive; without this, the entire architecture assumption collapses. Cheapest to test first.

### 2. MOTIV-MASTERY
- **Anchor pointer:** Research note Level 3, Section MOTIV-MASTERY; schema-consolidation-rate-driven skill selection.
- **Substrate-product reading:** Validates that partial consolidation is a useful signal for directing practice effort. If this passes, the substrate can self-optimize retrieval quality without external training signal.
- **Tier hint:** CPU local (30 practice-session trials, 3 synthetic schemas at different consolidation stages).
- **Why now:** Second cheapest; uses existing consolidation rate metrics that are already instrumented.

### 3. MOTIV-IDENTITY
- **Anchor pointer:** Research note Level 3, Section MOTIV-IDENTITY; self-model alignment drive test.
- **Substrate-product reading:** Validates that a self-model can function as a behavioral stabilizer. If this passes, identity drive is a noise-resistance mechanism at behavioral level.
- **Tier hint:** CPU local (30 trials after 50-interaction warmup).
- **Why now:** Identity is needed for arbitration conflict tests; this is the prerequisite.

### 4. MOTIV-SOCIAL
- **Anchor pointer:** Research note Level 3, Section MOTIV-SOCIAL; convention-conformity convergence in multi-agent setup.
- **Substrate-product reading:** Validates single-step social adaptation. If this passes, personalized response adaptation is a confirmed product behavior without explicit fine-tuning.
- **Tier hint:** CPU local (two-agent simulation, 20 turns, synthetic conventions).
- **Why now:** Lower priority than the single-agent drives; depends on multi-agent substrate scaffolding being available.

### 5. MOTIV-EMPOWER
- **Anchor pointer:** Research note Level 3, Section MOTIV-EMPOWER; channel-capacity-driven action selection.
- **Substrate-product reading:** Validates the binding-space empowerment approximation. If this passes, option-preserving behavior (avoid dead ends, maintain degrees of freedom) is a confirmed product behavior.
- **Tier hint:** CPU local (20 trials, toy environment with constructed W geometry).
- **Why now:** Requires computing a channel capacity estimate from W matrix geometry -- slightly more engineering than the margin-based tests. Lower priority than curiosity and mastery.

### 6. MOTIV-ARBITRATION
- **Anchor pointer:** Research note Level 3, Section MOTIV-ARBITRATION; drive conflict test across all 5 arbitration architectures.
- **Substrate-product reading:** Validates that drive arbitration architecture matters and identifies the best-performing design. Prerequisite for exposing drive weights as a product configuration parameter.
- **Tier hint:** CPU local (100 trials, 5 architectures, 3 seeds each). Largest of the 6 anchors but still CPU-only.
- **Why now:** Run after MOTIV-CURIOSITY and MOTIV-IDENTITY pass, since those two drives are the ones in conflict in the arbitration setup.

---

## Context pointers

- `notes/research_drill_motivation_boundary_probe_2x_2026-06-10.md` -- full research note with primitives, architecture designs, pre-registered thresholds, and citations.
- `notes/substrate_capability_map.md` -- current cap_map; check for any open motivation-related rows.
- Research note Level 2 contains all 5 arbitration architecture designs (weighted-sum, argmax, context-modulated, learned, hierarchical); exp_dev should read before designing MOTIV-ARBITRATION.

---

## Pre-registered thresholds (from research note Level 3)

exp_dev designs the exact bands, but the research note has pre-specified the directional thresholds. These are listed for reference; exp_dev may tighten or adjust based on implementation specifics:

| Anchor | Direction HARD-PASS | Direction HARD-FAIL |
|--------|---------------------|---------------------|
| MOTIV-CURIOSITY | novel > 2x familiar visit rate | <= 1x (chance) |
| MOTIV-MASTERY | intermediate selected > 2x each other | uniform |
| MOTIV-IDENTITY | self-consistent > 70% | <= 55% |
| MOTIV-SOCIAL | alignment > 0.7, monotone increase | delta < 0.05 |
| MOTIV-EMPOWER | Option A > 70% | <= 55% |
| MOTIV-ARBITRATION | hierarchical oscillation < 2/10 steps | all equivalent |

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke.
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance.
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code (5 = post-ship verification failed).
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, M, K, seed count, threshold bands (HARD-PASS + HARD-FAIL), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, and the exact integration layer design. The pre-registered directional thresholds above are from research; exp_dev may tighten them based on implementation. If exp_dev determines that a different ordering of anchors is better based on queue state, that is exp_dev's call.

---

*Filed: 2026-06-10 by research sub-agent. Research note path:*
*`notes/research_drill_motivation_boundary_probe_2x_2026-06-10.md`*
