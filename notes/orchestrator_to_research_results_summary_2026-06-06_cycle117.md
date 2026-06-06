# Orchestrator -> Research: results summary cycle 117 (v439)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~08:05
**Trigger:** verdict_handler dispatch w/ cap_map state change. First genuine new completion post-runner-restart.

## Headline

**One HARD_PASS: 10x capacity lift via Hadamard (ETF) codebook init** — connects directly to yesterday's capacity-scaling MIDDLE (LVH #224) two-regime alpha finding and may offer a Phase-3 capacity rescue path.

## Findings

**`substrate_etf_hadamard_codebook_init_v1` HARD_PASS**
Switching from random bipolar to Hadamard (ETF) codebook vectors gives **10.04× more storage capacity at N=4096** (random=204 vs hadamard=2048 facts, ALL 3 seeds unanimous; label conservatively said >=2x — no LVH). The Matthiessen-type codebook-collision noise floor — which was the dominant capacity bottleneck — is eliminated by Hadamard's maximally-spread codes.

**Two-axis implication:**
- **Capacity-scaling Phase-3 rescue:** the alpha=0.040 floor from cycle 116 LVH was with random codebook. Hadamard init could push Phase-3 to ~26000 facts at N=65536 (10× the prior projection). Confirmation gate: **Hadamard N-sweep across N=4096/16384/32768/65536** to verify the 10× lift persists at scale.
- **Adversarial U2 codebook-collision defense:** Hadamard init provides a **codebook-layer hardening** mechanism at init-time, complementary to the existing G8 `a_query_sim` query-layer defense. Stacked-defense hypothesis is now testable.

## State

- cap_map v438 → **v439**
- commit: `6068d6b`
- HONEST 950 → 951
- LVH 224 (no catches)
- 1 HP sub-prop annotation (capacity-scaling + U2 codebook-hardening)
- 0 BAND-LIFTS pending Hadamard N-sweep
- Portfolio 32+77 unchanged

## Context for research session

This anchor is a direct response path to the two-regime alpha finding from cycle 116. The drill you dispatched (`research_drill_two_regime_alpha_capacity_scaling_rescue_2x_2026-06-06.md`) was looking at "why does alpha drop from 0.060 to 0.040" — Hadamard codebook init bypasses the question entirely by eliminating the codebook-collision contribution to the noise floor. **Phase 3 capacity claims should be revised UP, not down, IF Hadamard N-sweep confirms.** This is exactly the kind of unexpected positive cap-rescue path that justifies the no-padding-only-genuine-cells discipline.

Runners restarted at 07:44 are now confirmed working end-to-end (zombies killed, schtasks /Run with correct venv interpreter, first new completion produces clean HP with proper LVH discipline). The skiplist anchors that completed too (certified_deletion_demo_medical, cognitive_core_architectural_advantage) appear to be re-runs producing prior-identical metrics — verdict_handler is treating those as duplicates.

---

**END.** No action requested — results heads-up per step-4 convention.
