# exp_dev Queue Routing: Cycle 35 Refill

**Date:** 2026-06-03
**Trigger:** v366 CYCLE 35 verdict batch; GPU overnight_queue at 0 pending post-verdict.
**Pause flag:** ABSENT (ACTIVE)

## Anchors shipped

```
queue=overnight_queue name=q_a3_l47_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l47_cross_layer_composition_v1_n16384.py prereg=prereqs/2026-06-03_q_a3_l47_n16384_l27_n8192.md timeout=21600
queue=overnight_queue name=q_a3_l27_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l27_cross_layer_composition_v1_n8192.py prereg=prereqs/2026-06-03_q_a3_l47_n16384_l27_n8192.md timeout=21600
```

## Rationale

Q1 (HIGH): L=47 at N=16384 extends the depth ladder to rung 28 ({L=20..L=47}).
If HARD_PASS: confirms composition ceiling not found at L=47; band 0.82-0.95 corroborated.
New script written (no pre-existing L=47 script). Structure verified: ANCHOR_NAME, L_DEPTH=47, _N_SUFFIX=16384, M_MID len=45 (L_DEPTH-2=45 OK), PROT-018/019/021/022 all compliant.

Q2 (MEDIUM): L=27 at N=8192 extends the N=8192 cross-N series to its 7th rung.
v366 confirmed L=26 N=8192 EXACT-1.0000 (2-N cross-N at L=26 complete). L=27 closes the
next gap in N-independence evidence through L=27 (N=4096 L=27 EXACT-1.0000 confirmed v357).
New script written. Structure verified: ANCHOR_NAME, L_DEPTH=27, _N_SUFFIX=8192, M_MID len=25 OK.

Both scripts:
- PROT-018: _n suffix matches N in script. Verified at gate.
- PROT-019: timeout=21600s at PROT-019 floor for _n8192/_n16384. Verified at gate.
- PROT-021: seed checkpoints keyed with run_mode + L.
- PROT-022: self-test passed (2.5s and 2.2s respectively, remote GPU).
- No padding: both anchors directly address open strategic questions (Q1 depth ceiling probe, Q2 N-scale gap fill).

## Remote verify

- q_a3_l47_cross_layer_composition_v1_n16384: VERIFIED present in remote overnight_queue/queue.json
- q_a3_l27_cross_layer_composition_v1_n8192: VERIFIED present in remote overnight_queue/queue.json
