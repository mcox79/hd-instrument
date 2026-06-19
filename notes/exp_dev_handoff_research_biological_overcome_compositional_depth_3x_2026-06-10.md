# exp_dev hand-off -- research: biological-overcome-compositional-depth-3x

**Filed-by:** research sub-agent
**Date:** 2026-06-10
**Trigger:** Research note at notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md
  documents nine biological mechanisms that overcome the VSA compositional SNR cliff.
  Four of these are ready for empirical test as substrate anchors (ATTRACTOR-AT-EACH-LEVEL,
  LATERAL-INHIBITION-CLEANUP, PREDICTIVE-CODING-AT-DEPTH extension, POPULATION-CODING-
  AT-EACH-LEVEL extension). This is exp_dev-actionable: concrete experiment designs
  can be pre-registered and dispatched.

**Pause state:** Check orchestrator_paused.flag before dispatching any anchors.
  If paused, hold this file for next refill cycle.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the anchors;
  this file names the mechanisms and provides substrate-product reading only.
  Do NOT inline experiment code or exact parameter values here.

---

## Anchor candidates (rank-ordered)

### ANCHOR-1: ATTRACTOR-AT-EACH-LEVEL (RANK 1)
**Substrate-product reading:** Per-level Hopfield cleanup at shard boundaries. The cheap
  decisive test in the research note is the HIERARCHICAL-CLEANUP-STRESS-TEST (L=5, K=10,
  3 conditions: flat / H=2 cleanup / H=4 cleanup). If HARD-PASS HP-1 met (accuracy >=
  0.70 at L=5 with H=4), then the multi-hop retrieval capability claim (depth 5+ chains)
  is substantiated. This is the single highest-expected-gain anchor.
**Tier hint:** CPU-viable (pure VSA algebra + Hopfield; no GPU required).
**Why now:** 5-level shard hierarchy was established in last research cycle (2026-06-10
  shard hierarchy note). The per-level cleanup is the natural next verification step.
  Substrate already has Hopfield cleanup at final level; extending it is incremental
  architecture, not novel design.
**Pre-reg band:** HP >= 0.70 accuracy at L=5, K=10, H=4; HF < 0.30 OR non-monotone
  with H. See research note Section 6 for full hard-pass/hard-fail bands.

### ANCHOR-2: LATERAL-INHIBITION-CLEANUP per level (RANK 2)
**Substrate-product reading:** Winner-take-K' applied to intermediate bundles. Compatible
  with FHRR algebra. This is the cheapest mechanism to implement (single-pass modification
  to composition pipeline) and should be tested alongside or before ANCHOR-1 as a control.
**Tier hint:** CPU-viable; can be co-dispatched with ANCHOR-1 as condition variant.
**Why now:** If ANCHOR-1 shows hierarchical cleanup works, lateral inhibition is the
  ablation that isolates whether the gain is from attractor cleanup or from bundle sparsification.

### ANCHOR-3: PREDICTIVE-CODING-AT-DEPTH (PP-267 extension) (RANK 3)
**Substrate-product reading:** Extend PP-267 (validated 3x compression flat) to a 2-level
  chain. Measure entropy reduction at each inter-level boundary. If 3x compression holds
  per level, 2-level chain gives 9x total -- this lifts the effective bundle capacity at
  each level by that factor.
**Tier hint:** CPU-viable; requires per-level linear predictor training (small dataset).
**Why now:** PP-267 is validated. Deep extension is a natural follow-on. The research note
  predicts 3x per level; a 2-level test would confirm or falsify this scaling.

### ANCHOR-4: POPULATION-CODING-AT-EACH-LEVEL sweep (RANK 4)
**Substrate-product reading:** Extend PP-249 (validated at atomic level) to L=3
  composition with M in {1, 10, 100} per level. Plot retrieval accuracy vs M at each level
  independently to measure the per-level population coding gain.
**Tier hint:** CPU-viable; M=100 adds compute but is not GPU-scale.
**Why now:** PP-249 existence is validated. Per-level extension is parameter sweep, not
  architecture change. This is the fastest way to quantify the per-level SNR gain from
  ensembling.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md
- Shard hierarchy note (immediate precursor): d:/AI/hd-instrument/notes/ (most recent research note before this date)
- PP-267 predictive coding: check cap_map for current row state
- PP-249 population coding: check cap_map for current row state
- PP-141/PP-142 sleep-defrag: check cap_map for current row state (compositional schema extension is RANK 9 in research note, lower priority)

---

## Contract

exp_dev designs anchors with preregs per envelope-fail-bands.
No inline experiment design in this file.
Dispatch via queue_add.sh (CPU queue preferred; GPU only if N >> 8192).
Post-ship REMOTE VERIFY per role contract.

## Autonomy declaration

exp_dev has full autonomy on: anchor design, parameter choices, smoke gate thresholds,
queue routing, seed selection, checkpoint interval, dispatch timing.
exp_dev should NOT: modify cap_map rows, write strategy notes, or change the research
note. Those remain in research/strategy lane.
