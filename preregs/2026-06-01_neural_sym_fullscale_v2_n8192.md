# Pre-registration: neural_sym_fullscale_v2_n8192

**Date:** 2026-06-01
**Anchor:** neural_sym_fullscale_v2_n8192
**Script:** experiments/exp_neural_sym_fullscale_v2.py
**Queue:** overnight_queue
**N:** 8192 (_n8192 PROT-018 binding)

## Hypothesis

Neural-symbolic bridge at full scale N=8192. XOR-bound KV store encoding
(subject, relation) -> object triples. Sweep F (number of triples) up to N/2=4096.
Cell A: P_correct at F_max=N/8, N/4, N/2. Cell B: deletion isolation.
Expected: P_correct > 0.95 at F=N/8, degrading to ~0.60 at F=N/2.

## Pre-registered thresholds

- **HARD-PASS:** mean P_correct@N/8 > 0.95 AND mean del_P < 0.10
- **HARD-FAIL:** P_correct@N/8 < 0.70 OR del_P > 0.30
- **MIDDLE-BAND:** P_correct in [0.70, 0.95] or del_P in [0.10, 0.30]

## Smoke result (2026-06-01)

Smoke MIDDLE_BAND: acc@N/8=0.895 (< HP=0.95), del_P=0.104. Ships to GPU.
Smoke at N=1024 (N/8 of full), wall ~138s at 2 seeds. Expected FULL ~2600s.

## Cap-map rows

- Neural-symbolic bridge capability at N=8192
- Triple-store KV with deletion isolation
