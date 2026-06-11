# Pre-registration: wave1_tier1_sweep_cpu_v1

**Date:** 2026-06-11
**Anchor:** wave1_tier1_sweep_cpu_v1
**Queue:** local_cpu_queue
**N:** 8192 (per underlying wrapper cell), **Seeds:** 5 (HDLAB_SEED 1..5), **Anchors:** 3

## Scientific question
Are the remaining Sprint-4 engineered-wrapper components that were validated at n=1 (RS-parity PP-354, v3.2-unified
capstone PP-357, per-tier-importance PP-355) SEED-ROBUST at n=5? Completes the Wave-1 Tier-1 wrapper multi-seed
promotion (write-lock/per-role/3x-redundant/cls already covered by v32_multiseed_cpu_v1). Per Research
PROMOTION_CAMPAIGN_WAVES Wave-1 Tier-1.

## Pre-registered bands

**HARD-PASS:** all 3 wrapper cells CONFIRM (HARD_PASS in >=4/5 seeds).

**MIDDLE:** 2 of 3 seed-robust.

**HARD-FAIL:** <2 seed-robust (wrapper layer was an n=1 fluke -> route to Research).

## Per-anchor rule
- >=4/5 seeds HARD_PASS -> CONFIRM
- 2-3/5 -> SEED_FRAGILE
- <2/5 -> FAIL

## Calibration rationale
These three wrapper components passed cleanly at n=1 (RS-parity 1.0, v3.2-unified all-1.0, per-tier 1.0). The
engineered wrapper rides on deterministic FHRR algebra, so n=5 is expected to reproduce; any seed-fragility would
indicate a representation-collision artifact worth routing back. all-3-confirm is the bar for promoting the wrapper
layer off n=1 exploratory.

## N-suffix section
Meta-runner (no N constant of its own); each underlying wrapper cell is N=8192 multi-seed. Timeout at the n>=8192
multi-seed floor to cover 3 anchors x 5 seeds of subprocess runs (all fast numpy).
