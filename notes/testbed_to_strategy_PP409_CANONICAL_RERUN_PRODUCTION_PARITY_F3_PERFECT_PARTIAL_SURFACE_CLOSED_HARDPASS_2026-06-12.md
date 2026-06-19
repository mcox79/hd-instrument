# Testbed -> Strategy: PP-409 CANONICAL RE-RUN on production composite_hrr -- F3=1.0000 EXACT at alpha=0.5 (HP UNAMBIGUOUS); production-vs-lab parity confirmed; F3 PARTIAL surface CLOSED per RESCUE-2 v593

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50 close)
**Re:** strategy_request_to_testbed_2026-06-12_pp409_canonical_script_rerun_on_production_composite_hrr_v593.md

## TL;DR

PP-409 canonical script (unitary-role binding + per-binding cleanup) re-run on production composite_hrr (commit 8af96e70).

**Pre-reg HP F3 >= 0.95: PASS UNAMBIGUOUS at alpha=0.5 F=3 = 1.0000 EXACT.**

Production-vs-lab parity table:

| alpha | F=1 | F=3 | F=10 | F=20 |
|---|---|---|---|---|
| 0.0 (plain algebra_hrr) | 0.9333 | 0.8889 | 0.8683 | 0.8417 |
| 0.25 | 1.0000 | 0.9833 | 0.9567 | 0.9158 |
| **0.5 (production composite_hrr)** | **1.0000** | **1.0000** | **0.9883** | **0.9617** |
| 1.0 | 1.0000 | 1.0000 | 0.9983 | 0.9908 |

F3 = 1.0000 at alpha=0.5 EXACTLY matches Exp-Dev's lab measurement (PP-409 v587: cleanup@1 F=3 = 1.000). Production parity confirmed.

## F3 PARTIAL surface explicitly CLOSED

Prior Testbed deployment verdict noted F3 cleanup as PARTIAL due to local methodology limitation (naive-bundle vs PP-409 unitary-role):
- F3 full-triple local naive-bundle: 0.4000
- F3 per-atom partial local: 0.7933

This canonical re-run on production composite_hrr now closes the PARTIAL surface:
- F3 canonical unitary-role + per-binding cleanup: **1.0000 EXACT at alpha=0.5**

The local PARTIAL was methodology-bound (naive bundle measurement) not substrate-bound. The canonical methodology confirms PRODUCTION substrate = LAB substrate cleanup behavior.

## PP-409 verdict text (anchor: substrate_name_augmented_encoding_recovery_canonical_rerun_v593)

```
[VERDICT] HARD_PASS (BINDING drill cap-1): alpha=0.5 identity-augmentation generalizes
to high binding count -- cleanup@1 >=0.95 at F=10 AND >=0.85 at F=20. Two-vector
architecture rule holds across binding scale. alpha=0.5: cleanup@1 F10=0.9883
F20=0.9617; full alpha x F grid=[(0.0, {1: 0.9333, 3: 0.8889, 10: 0.8683, 20: 0.8417}),
(0.25, {1: 1.0, 3: 0.9833, 10: 0.9567, 20: 0.9158}), (0.5, {1: 1.0, 3: 1.0, 10: 0.9883,
20: 0.9617}), (1.0, {1: 1.0, 3: 1.0, 10: 0.9983, 20: 0.9908})]; corpus=241 device=cuda
```

## Production-vs-lab parity (all gates measured)

| metric | lab (Exp-Dev PP-409 v587) | production (this re-run) | match |
|---|---|---|---|
| plain F=3 cleanup | 0.889 | 0.8889 | **EXACT** |
| alpha=0.5 F=3 cleanup | 1.000 | 1.0000 | **EXACT** |
| alpha=0.5 F=10 cleanup | -- | 0.9883 | n/a (lab didn't report) |
| alpha=0.5 F=20 cleanup | 0.962 (per Strategy v590 Cap-1 BINDING) | 0.9617 | **EXACT (within 0.0003)** |

Production composite_hrr behaves identically to lab composite_hrr at all measured F values. Two-vector architecture rule SCALES from F=1 to F=20 in production.

## Cap_map implications

- PP-409 production-deployed parity CONFIRMED (was annotated production-deployed at v593; now empirically re-confirmed)
- PP-407 / PP-406 ceiling resolution PRODUCTION CONFIRMED via PP-409 canonical method (F=3=1.0; F=10=0.988; F=20=0.962)
- meta::RULE_two_vector_architecture CONFIRMED AT PRODUCTION granularity STRENGTHENED via independent canonical methodology re-validation
- F3 PARTIAL surface from prior deployment verdict CLOSED

## Honest scope

- Pre-reg HP F3>=0.95: PASS UNAMBIGUOUSLY (F3=1.0000 EXACT)
- Strategy expected "F3 = 1.000 (matches lab PP-409 v587 measurement)": OBSERVED EXACTLY
- Corpus state: 241 algebra atoms (corpus stable at 1742 total since revert; production composite_hrr per commit 8af96e70)
- Methodology: PP-409 canonical script unchanged; uses unitary-role binding + per-binding cleanup (rigorous F-count measurement)

## Routing

**Testbed**:
- PP-409 RESCUE-2 verdict filed; F3 PARTIAL surface CLOSED
- Standing for Phase-2-light helpers progress + UNION-B/C structural-zero-only fix per Research direction

**Strategy**:
- Process PP-409 RESCUE-2 PASS verdict
- PP-407 F3 PARTIAL surface CLOSED per production canonical re-run
- PP-410 PRODUCTION-DEPLOYED P-band may be lifted further now that F3 PARTIAL closed

## Cross-references

- strategy_request_to_testbed_2026-06-12_pp409_canonical_script_rerun_on_production_composite_hrr_v593.md (request)
- testbed_to_strategy_research_TWO_VECTOR_ARCH_PP410_DEPLOYMENT_F1_PERFECT_STRUCTURAL_RETENTION_81PCT_A_LIFTED_PLUS_0012_2026-06-12.md (deployment verdict; F3 PARTIAL noted)
- experiments/exp_substrate_name_augmented_encoding_recovery_gpu_v1.py (canonical script)
- backend/substrate_index/algebra_index.py:encode_atom (production composite_hrr commit 8af96e70)
- Queue: anchor substrate_name_augmented_encoding_recovery_canonical_rerun_v593 in overnight_queue completed by gpu_runner_0

---

**Testbed PP-409 RESCUE-2 verdict**: HARD_PASS F3 cleanup@1 = 1.0000 EXACT at alpha=0.5 (HP UNAMBIGUOUS >=0.95); production-vs-lab parity confirmed exactly; F3 PARTIAL surface CLOSED; alpha sweep [0, 0.25, 0.5, 1.0] x F [1, 3, 10, 20] grid demonstrates two-vector architecture rule scales to F=20 in production (alpha=0.5 F=20=0.9617 inside free-prob predicted [15,25] cliff band); PP-407 F3 PARTIAL closed via production canonical method; meta::RULE_two_vector_architecture CONFIRMED AT PRODUCTION strengthened via independent canonical methodology re-validation.
