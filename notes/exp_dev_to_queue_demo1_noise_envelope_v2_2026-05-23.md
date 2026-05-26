# Exp Dev -> Queue: wave14_demo1_noise_envelope_v2

**Filed**: 2026-05-23
**Routing trigger**: User directive -- Demo 1 Lane D capstone noise envelope expansion at FULL; v1 (observation-stream noise) already queued; v2 covers the inter-stage W noise axis.

---

## Queue entry

```
queue=overnight_queue name=wave14_demo1_noise_envelope_v2 script=experiments/exp_wave14_demo1_noise_envelope_v2.py prereg=preregs/2026-05-23_wave14_demo1_noise_envelope_v2.md timeout=3600
```

---

## Smoke gate

- Self-test: 7/7 cases passed
- Smoke run at N=8192 device=cpu seeds=[17] noise_levels=[0.0, 0.10]:
  - p=0.00: composed=1.000 (S=1.000 T=1.000 X=1.000) n=10
  - p=0.10: composed=1.000 (S=1.000 T=1.000 X=1.000) n=10
  - Verdict: DEMO1_NOISE_ENVELOPE_PASS
  - metrics.json written; oracle.assert_baseline_high passed
- SMOKE OK

---

## Axis description

Noise axis: inter-stage W bit-flip. After Stage U accumulates clean B_q,
each downstream stage (S, T) receives an independently drawn noisy copy of B_q
at flip rate p. Stage X receives no direct W read; noise propagates to X only
through Stage T's hypothesis prediction. This is structurally DIFFERENT from v1
(which flips observation triples before EMA accumulation). Together v1 + v2
characterize both ends of the noise chain: input-side corruption (v1) vs
memory-bus corruption (v2).

---

## Memory budget

Peak VRAM at N=65536 FULL: ~62 MB (5 codebooks + B + 2 noise views + mask temp).
Well within 8 GB VRAM budget.

---

## Expected elapsed

~30-60 min FULL (N=65536, 3 seeds x 5 noise levels x 40 trials = 600 total trials).

---

## Verdicts

- DEMO1_NOISE_ENVELOPE_PASS: composed_acc(p=0.00) >= 0.80 AND composed_acc(p=0.10) >= 0.40
- DEMO1_NOISE_ENVELOPE_NARROW: composed_acc(p=0.00) >= 0.80 AND composed_acc(p=0.10) < 0.40
- DEMO1_NOISE_KILL: composed_acc(p=0.00) < 0.80 (regression from capstone 1.000)

Pre-registered P estimates (calibration-deflated per uncharted regime):
P(PASS)=0.60, P(NARROW)=0.30, P(KILL)=0.10.
