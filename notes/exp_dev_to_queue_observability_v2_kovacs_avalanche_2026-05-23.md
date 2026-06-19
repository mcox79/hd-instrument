# Exp Dev -> Queue: Observability V2 Kovacs + avalanche shipped (Strategy 07:05 P-B-2 + P-B-3)

**Sender**: Experiment Dev
**Date**: 2026-05-23 ~09:00 EDT
**Topic**: New experiments ready for queue pickup — completes Strategy 07:05 P-B Observability V2 triad
**Trigger**: META cycle 93 audit (08:46) listed "Observability V2 Kovacs + avalanche probes" as open for cycle 94; user "check for priority" signal

## What landed

Two new experiment files + preregs in this commit:

1. `experiments/exp_wave14_kovacs_hump_v1.py` (Strategy 07:05 P-B-2)
   - Prereg: `preregs/2026-05-23_wave14_kovacs_hump_v1.md`
   - Double-quench: aging at beta_low=0.5 for t_w in {10, 100, 1000, 5000}, then beta_target=2.0; max overshoot ratio across t_w.
   - Smoke verdict (N=2048, t_w=[10,100]): KOVACS_RS_INDEPENDENT ratio=1.027
   - Verdicts: KOVACS_RS_INDEPENDENT (<1.2) / KOVACS_BROAD_RELAXATION (>2.0) / KOVACS_INTERMEDIATE
   - Expected ~5 min FULL at N=8192

2. `experiments/exp_wave14_avalanche_size_distribution_v1.py` (Strategy 07:05 P-B-3)
   - Prereg: `preregs/2026-05-23_wave14_avalanche_size_distribution_v1.md`
   - Argmax-relaxation avalanche P(dE) histogram, log-log power-law fit on tau.
   - Smoke verdict (N=2048, n_runs=20): AVAL_NONPOWER tau=0.107 r2=0.259 — needs FULL statistics
   - Verdicts: AVAL_ABBM_FIT (1.3-1.7) / AVAL_STEEPER (>=1.7) / AVAL_SHALLOWER (<=1.3) / AVAL_NONPOWER (r2<0.7)
   - Expected ~1 min FULL at N=8192

## Local gate

- Self-test: PASSED (4/4 Kovacs, 5/5 avalanche)
- Smoke: PASSED with valid metrics.json for both
- ASCII-only print/verdict strings per [[feedback_ascii_only_in_scripts]]

## Queue request

Add to overnight_queue:
- name=wave14_kovacs_hump_v1 script=experiments/exp_wave14_kovacs_hump_v1.py prereg=preregs/2026-05-23_wave14_kovacs_hump_v1.md timeout=600
- name=wave14_avalanche_size_distribution_v1 script=experiments/exp_wave14_avalanche_size_distribution_v1.py prereg=preregs/2026-05-23_wave14_avalanche_size_distribution_v1.md timeout=600

## Completes Strategy 07:05 P-B triad

- chi_4 (07:08): smoke=CHI4_RS_CONSISTENT peak=0.45 — queued; FULL pending in v148 batch
- Kovacs (now): ready for queue
- Avalanche (now): ready for queue

## Per [[feedback-sessions-self-coordinate]]

File-routing only. No user-side prompt edit required.

EOF marker.
