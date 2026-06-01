# Pre-registration: anchor_novel_class_declaration_probe_v1

**Date:** 2026-05-27
**Script:** experiments/exp_anchor_novel_class_declaration_probe_v1.py
**Queue:** overnight_queue (GPU; N=2048 with N-sweep; ~1.5-2h)
**Trigger:** exp_anchor_novel_phase_battery_v1 HARD_FAIL (< 3/6 documented) OR NOVEL (>= 4/6 novel)

## Hypothesis

5-step novel-class characterization per research methodology (Finding 2).
Tests whether substrate deserves novel SKAH-M declaration vs documented-class call.

## Design

5-probe battery: S1 (Z3 symmetry), S2 (q_EA N-scaling), S3 (Goldstone gap),
S4 (free-energy wells), S5 (response susceptibility). N=2048, 5 seeds.

## Pre-registered bands

- **NOVEL_CONFIRMED:** novel_score >= 4/5 AND S2=ANOMALOUS -> SKAH-M declaration warranted
- **DOCUMENTED_CONFIRMED:** documented_score >= 4/5 -> gated multistable AM confirmed
- **FINITE_N_CONFIRMED:** S2=FINITE_N + S4=FEW_WELLS -> substrate dissolves at thermodynamic limit
- **MIXED_EVIDENCE:** < 3 probes clearly classify
