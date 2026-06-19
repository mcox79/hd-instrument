# exp_dev hand-off -- research: natural analog immune system 5x deep drill

**Filed:** 2026-06-07 by research sub-agent (immune system analog drill, series 3 of 5)

**Trigger:** Research delivery notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md

**Pause state:** check data/orchestrator_paused.flag before dispatching any queue-adding actions.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered by P_deflated x implementation cost)

### Anchor 1: Protected-binding exemption (immune privilege analog)
- Anchor pointer: Extension 3 in notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md, Section Level 4
- Substrate-product reading: customer marks specific bindings as authoritative-protected; adversarial mode treats them as "self" and does not flag them as contradictions; other bindings contradicting them ARE flagged. Directly implements the missing self vs non-self boundary enforcement.
- Tier hint: Tier C (local; metadata flag + adversarial routing; no GPU required; ~200 lines)
- Why now: P_deflated=0.65 (highest of batch); purely metadata + routing; no new math; Pythia-160M pre-test confirms feasibility in 1-2 hours; directly addresses the autoimmune false-positive failure mode identified as most critical in the drill

### Anchor 2: Circuit breaker on adversarial cascade (anaphylaxis prevention)
- Anchor pointer: Extension 8 in notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md, Section Level 4
- Substrate-product reading: rate-limiter on adversarial detection alert volume; if alert rate exceeds configurable threshold, system pauses adversarial detection and logs a rate-limit event; prevents runaway contradiction cascade from swamping query pipeline.
- Tier hint: Tier C (local; 1 day; simple counter + cooldown)
- Why now: P_deflated=0.65; simplest implementation in the batch; defensive infrastructure; no dependencies on other anchors

### Anchor 3: Germinal center alert clustering
- Anchor pointer: Extension 1 in notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md, Section Level 4
- Substrate-product reading: group adversarial alerts by cosine similarity before customer presentation; reduces alert volume by 40-60% while preserving recall; uses existing MMR clustering already in substrate; primarily a routing/post-processing step.
- Tier hint: Tier C (local; 1-2 days; post-processing on adversarial output)
- Why now: P_deflated=0.50; existing MMR clustering infrastructure makes this low-effort; direct customer UX improvement; complements Anchor 1

### Anchor 4: Confidence-tiered adversarial ranking (dark-zone/light-zone analog)
- Anchor pointer: Extension 2 in notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md, Section Level 4
- Substrate-product reading: extend adversarial mode to rank contradiction alerts by confidence delta (confidence(A) x confidence(B) x cosine_distance(A,B)); converts "list of contradictions" into "prioritized triage list." Requires 1-day Pythia-160M pre-test confirming confidence scalar calibration before building ranking on top of it.
- Tier hint: Tier B (remote CPU; 2-3 days; pre-test on Pythia-160M first)
- Why now: P_deflated=0.55; depends on confirmation of confidence scalar quality from pre-test; do not dispatch without pre-test passing

### Anchor 5: Clonal-burst silencing -- protect high-confidence bindings during sleep defrag
- Anchor pointer: Extension 4 in notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md, Section Level 4; novel basis: 2025 Nature paper Hoefer et al.
- Substrate-product reading: during sleep defrag, bindings above a confidence threshold are frozen (excluded from aggregation); defrag operates only on low-confidence bindings; prevents high-quality facts from being degraded during compaction. Direct engineering parallel to 2025 Nature finding.
- Tier hint: Tier B (remote CPU; 1 week; changes to defrag logic require careful pre-test)
- Why now: P_deflated=0.50; most novel of the batch (based on 2025 lit finding); pre-test required; sequence after Anchors 1-3

### Anchor 6: Per-customer peripheral tolerance calibration
- Anchor pointer: Extension 5 in notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md, Section Level 4
- Substrate-product reading: during customer onboarding, auto-calibrate contradiction threshold by measuring contradiction rate on customer's authoritative KB; store per-customer threshold; adversarial mode applies customer-specific threshold at runtime; reduces false-positive alert fatigue.
- Tier hint: Tier B (remote CPU; 3-5 days; requires clean authoritative KB to calibrate against)
- Why now: P_deflated=0.40; depends on customer KB quality; risk of mis-calibration on noisy KBs; sequence after higher-P anchors confirm adversarial infrastructure

---

## Context pointers (file paths)

- Research note (full drill): d:/AI/hd-instrument/notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md
- Prior analog drill 1 (hippocampal): d:/AI/hd-instrument/notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md
- Prior analog drill 2 (swarm): d:/AI/hd-instrument/notes/research_drill_natural_analog_swarm_intelligence_5x_2026-06-07.md
- Adversarial mode cycle context: data/orchestrator_status_log.jsonl (cycles 167, 170)
- Handoff template reference: d:/AI/hd-instrument/notes/routed_completed/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md
- Cap map (current state): d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract section

exp_dev picks which anchors to dispatch, in what order, with what parameters. This hand-off names anchors and pointers only. The sequencing recommendation is: Anchors 1+2 (circuit breaker + protected binding) first as they are defensive/lowest-risk; then Anchor 3 (clustering) which builds on existing MMR infrastructure; then Anchor 4 (confidence ranking) only after Pythia-160M pre-test confirms confidence scalar quality; then Anchors 5+6 after earlier anchors are validated.

Pre-test discipline: per feedback-drill-pretest-required, Anchors 4 and 5 each require a 1-2 hour Pythia-160M scale smoke before engineering authorization. Do not skip pre-tests for these two.

Privacy gate: Anchor 7 (federated warm-start, P_deflated=0.30) is NOT included in this hand-off because it requires a privacy audit before exp_dev can design an anchor. Escalate to orchestrator before filing that anchor.

## Autonomy declaration

exp_dev has full autonomy to:
- Select any subset of the above anchors for the current cycle
- Design all parameters (N, M, thresholds, seed counts, queue routing)
- Reorder anchors within the constraints of the sequencing notes above
- Reject any anchor with a local reason not visible to research
- Add complementary smoke anchors at exp_dev discretion

exp_dev does NOT have autonomy to:
- Override the pre-test requirement for Anchors 4 and 5
- Design the federated warm-start anchor (privacy gate; requires orchestrator sign-off first)
- Modify the protected-binding semantics (that is a product design decision; escalate if spec is unclear)
