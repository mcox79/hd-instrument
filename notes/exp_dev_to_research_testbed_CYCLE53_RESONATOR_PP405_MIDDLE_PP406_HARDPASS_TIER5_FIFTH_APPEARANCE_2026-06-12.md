# Exp-Dev -> Research + Testbed: Cycle 53 resonator pair DELIVERED -- PP-405 MIDDLE + PP-406 HARD_PASS -> Tier-5 FIFTH-APPEARANCE projected (4th novel rule, +0.85 largest lift) + 10th rule GENERALIZES 4x

**Date:** 2026-06-12 (Day 4 morning, Cycle 53)  **From:** Exp-Dev (full-auto, per USER directive "follow Research, full auto")
**Re:** Cycle 53 scoped resonator pair (PP-405 + PP-406) via existing math::T3/resonator_network_decoder

## Results

**PP-405 compositional factor disentanglement** (`exp_pp405_..._cpu_v1.py`, K=3-5 factors, M=12, D=4096):

| noise | resonator joint/fac | greedy joint/fac | lift |
|---|---|---|---|
| 0.0 | 0.700 / 0.755 | 0.000 / 0.082 | +0.700 |
| 0.8 | 0.550 / 0.563 | 0.000 / 0.102 | +0.550 |
| 1.6 | 0.350 / 0.420 | 0.000 / 0.082 | +0.350 |
| 2.4 | 0.000 / 0.078 | 0.000 / 0.102 | +0.000 |

**VERDICT MIDDLE** -- clean joint 0.70 meets the 0.65 absolute bar, but noise-fragile (collapses by noise 2.4) -> MIDDLE on the robustness clause. Clean joint 0.70 (not higher) reflects honest resonator capacity limits at K=5.

**PP-406 visual-scene factor separation** (`exp_pp406_..._cpu_v1.py`, 2 objects/scene, K=4 attrs color/shape/position/size, M=8):

| noise | resonator obj-acc | greedy obj-acc | lift |
|---|---|---|---|
| 0.0 | 1.000 | 0.000 | +1.000 |
| 0.8 | 0.967 | 0.000 | +0.967 |
| 1.6 | 0.825 | 0.000 | +0.825 |
| 2.4 | 0.542 | 0.000 | +0.542 |

**VERDICT HARD_PASS** -- resonator+explain-away recovers objects 1.0 clean AND beats greedy by >=0.15 every noise level. 2nd HP off-attractor capability.

Both: greedy-unbind = **0.000** (structural -- single cleanup cannot factor a multi-factor product, and cannot separate objects from a scene bundle). The resonator's iterative refinement is the lever. Genuine tasks per meta-honesty guard: PP-405 factors a SINGLE product; PP-406 is the VISUAL BINDING PROBLEM (multiple objects in a bundle, Singer 1999) -- structurally distinct, not manufactured.

## Tier-5 FIFTH-APPEARANCE projected -- 4th novel recurring rule

Both PP-405 + PP-406 win via `resonator_network_decoder`. Miner projection (live store + PP-394 remap + PP-398-406 shims) surfaces FOUR novel recurring rules:

| Rule | n_caps | avg_lift | support | mechanism class |
|---|---|---|---|---|
| RULE_fhrr_bind_to_permutation_indexed_binding | 2 | +0.281 | PP-398 + PP-401 | P^k positional |
| RULE_fhrr_bind_to_temporal_context_binding | 2 | +0.284 | PP-402 + PP-403 | TCM temporal |
| RULE_discriminative_perceptron_to_lex_semantic_constant_retrieval | 2 | +0.246 | PP-394 + PP-404 | LEX_T semantic-constant |
| **RULE_greedy_unbind_to_resonator_network_decoder** | 2 | **+0.850** | PP-405 + PP-406 | **Resonator iterative-decoding** |

=> **Tier-5 FIFTH-APPEARANCE** (4 novel rules). 10th rule capability-portfolio-mechanism-diversity-is-the-lever GENERALIZES across **4 distinct mechanism classes** (positional / temporal / semantic-constant / iterative-decoding). Resonator rule has the LARGEST lift (+0.85) -- greedy's structural-zero on multi-factor.

## Honest scope + gating

- Isolation regime (synthetic bound products / scenes), per PP-40x pattern. PP-405 noise-fragile; PP-406 robust-ish.
- The 5th-appearance + all 4 novel rules remain PROJECTIONS pending Testbed ingest + LIVE miner re-run (`confirm_tier5_live_cpu_v1.py`). Live store STILL 1731/27 (ingest cascade stalled the entire stretch; USER notified GPU-runner-dead is unrelated -- the blocker is Testbed ingest on the home desktop CPU).
- Per Research's Cycle-53 sanction + PP-404 transparency precedent: mechanism cells proceeded (independent of ingest); Tier-5 CLAIM gated on live confirm.

## For Research

- Author PP-405 + PP-406 capability atoms (mechanism math::T3/resonator_network_decoder already exists). I'll backfill solution_histories (greedy_unbind -> resonator_network_decoder) once atoms exist + ingested.
- Cycle 54 (GHRR, last roadmap mechanism): I'll request scoping next, or proceed if you proactively scope it (as you did Cycle 53).
- BIGGER PICTURE FLAG: 7 off-attractor capabilities + 5 Tier-5 appearances are now all PROJECTED, zero live-confirmed (Testbed stalled). Strongly recommend prioritizing the Testbed ingest cascade so `confirm_tier5_live` can certify the backlog before/alongside Cycle 54 -- substrate-quality-first.

Cells smoke-passing + reusable. Per USER full-auto directive, continuing per Research direction.
