# Pre-registration: wave14_demo1_noise_envelope_v2

**Date**: 2026-05-23
**Queue**: overnight_queue (GPU required; N=65536)
**Axis probed**: Cap 1 (Demo 1 Lane D S->T->X capstone) noise envelope -- inter-stage W bit-flip
**Trigger**: User directive: Demo 1 Lane D capstone noise envelope expansion at FULL; v1 already queued with observation-stream noise; v2 probes W noise BETWEEN pipeline stages (distinct axis)
**Script**: experiments/exp_wave14_demo1_noise_envelope_v2.py
**Peak VRAM**: ~61 MB (5 codebooks x 65536 x float32) -- well under 8 GB
**Expected elapsed**: ~30-60 min at FULL (N=65536, 3 seeds, 5 noise levels x 40 trials each)

---

## Scientific question

Does the Cap 1 Demo 1 Lane D S->T->X pipeline tolerate bit-flip corruption of the
working-memory vector W BETWEEN pipeline stages -- modelling memory-bus noise,
register read errors, or transmission corruption at the stage interface?

Cap 1 is FULL at clean observations (composed_acc=1.000, v153). The v1 noise
envelope (already queued) injects noise into observation triples before EMA
accumulation. This v2 experiment injects noise into B_q AFTER accumulation but
BEFORE each downstream stage reads W: Stage S gets a freshly-flipped copy of B_q,
Stage T gets an independent freshly-flipped copy. Stage X reads no W directly (only
the Stage T output hypothesis), so noise propagates to X only through Stage T accuracy.

---

## Design

- **N**: 65536 (full scale at which Cap 1 was demonstrated)
- **Noise model**: independent bipolar bit-flip on B_q at rate p BETWEEN stages.
  Each stage (S, T) receives an independently-drawn noisy copy; Stage X gets no
  additional noise (no direct W read). Noise levels: p in {0.0, 0.05, 0.10, 0.20, 0.30}.
- **Trials per cell**: 40 (per seed) x 3 seeds = 120 total per noise level
- **Seeds**: [17, 23, 31]
- **Pipeline**: Stage U (EMA, clean accumulation) -> B_q -> [flip for S] -> Stage S
  -> [flip independently for T] -> Stage T -> Stage X

---

## Falsifiable predictions

### DEMO1_NOISE_ENVELOPE_PASS
- `composed_acc(p=0.00) >= 0.80` AND `composed_acc(p=0.10) >= 0.40`
- Inter-stage noise at 10% does not collapse the composed pipeline.

### DEMO1_NOISE_ENVELOPE_NARROW
- `composed_acc(p=0.00) >= 0.80` AND `composed_acc(p=0.10) < 0.40`
- Pipeline survives clean; noise-tolerance boundary is below p=0.10.

### DEMO1_NOISE_KILL
- `composed_acc(p=0.00) < 0.80` (regression from capstone 1.000)
- Very unlikely given N=65536 substrate physics.

### Pre-registered expectation

P(PASS) = 0.60. At N=65536 the signal margin per stage is high; each stage reads
B_q independently so two fresh masks independently preserve at least 90% of
individual stage accuracy. Composed degradation: (0.9)^3 ~ 0.73 at p=0.10 -- above
the 0.40 hard threshold. P(NARROW) = 0.30. P(KILL) = 0.10.

Per [[feedback-lit-scan-calibration-penalty]]: no direct published precedent for
inter-stage W noise at N=65536 BSC substrate; P(PASS) deflated from naive 0.75 to
0.60 cap; P estimate capped below 0.75.

---

## Memory budget audit

- entity_atoms:   200 x 65536 x 4 = 52.4 MB
- relation_atoms:  20 x 65536 x 4 =  5.2 MB
- hyp_atoms:        3 x 65536 x 4 =  0.8 MB
- position_atoms:   4 x 65536 x 4 =  1.0 MB
- skill_atoms:      5 x 65536 x 4 =  1.3 MB
- B accumulator: 65536 x 4 = 0.3 MB
- B_q_S, B_q_T (noise views): 2 x 0.3 MB = 0.6 MB
- flip mask tensor (peak): 65536 x 4 = 0.3 MB (temporary)
- Total peak: ~62 MB VRAM. Well within 8 GB VRAM budget.

---

## Substrate-product positioning

If PASS: Demo 1 Lane D commercial envelope widens to include inter-stage W
corruption up to 10%. Product framing: "3-stage cognitive pipeline tolerates
moderate memory-bus noise between stages."

If NARROW: envelope boundary somewhere between p=0.0 and p=0.10; product note
"pipeline requires clean inter-stage W reads." Still FULL at clean (capstone
unchanged).

If KILL: regression -- very unlikely at N=65536.

---

## PROT compliance

Not a closure; no PROT-004/006 required. PROT-001 (exp_dev_decisions log entry) paired.
