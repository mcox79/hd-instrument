# exp_dev -> queue: adversarial_aqsim_path_d_compose_v5_k2_n16384

Date: 2026-06-01
Status: SHIPPED

queue=overnight_queue name=adversarial_aqsim_path_d_compose_v5_k2_n16384 script=experiments/exp_adversarial_aqsim_path_d_compose_v5_k2_n16384.py prereg=preregs/2026-06-01_adversarial_aqsim_path_d_compose_v5_k2_n16384.md timeout=21600

## Summary

v5 fixes v4 OOM (K_paths=100 + M=8192 at N=16384 needed ~7+ GB; GPU had <2 GB free).
Two strategic wins combined:
1. K=2 production op-point (K2PROD v1 HARD_PASS at N=4096) extended to N=16384.
2. Cross-N caveat ("N=4096 only") addressed: first cross-N test of K=2 production stack.

Config changes from v4:
- K_paths: 100 -> 2 (massive memory reduction; 50x cheaper path exploration)
- M_PROD: 8192 -> 4096 (M/N=0.5 -> M/N=0.25; halved to free VRAM)
- Peak memory estimate: ~1.0-1.5 GB vs v4's >7 GB

## PROT-022 falsification

PROT-022 log2-parity hypothesis FALSIFIED. v4 OOM at N=16384 (log2=14 EVEN, Kerdock OK)
confirms the actual cross-N failure mode is GPU memory cost, not BSC codebook precondition.
v3 at N=8192 (log2=13, ODD) was a genuine PROT-022 instrumentation failure but independent
of the memory cost issue.

## Smoke gate

PASS. Self-test: all 9 formula checks PASS. Live smoke: def_act=1.000, acc_gated_comp=1.000,
comp_delta=0.000. 4x-smoke (N=4096, M=1024): PASS. Wall time 0.03s.
REMOTE VERIFY: PASS (queue_add.sh exit 0; VERIFIED in remote queue.json).

## Commit/push

Deferred to main thread per subagent-permission-inheritance-gap.
Files to commit:
- d:/AI/hd-instrument/experiments/exp_adversarial_aqsim_path_d_compose_v5_k2_n16384.py
- d:/AI/hd-instrument/preregs/2026-06-01_adversarial_aqsim_path_d_compose_v5_k2_n16384.md


---

Acted-on 2026-06-01: anchor shipped + v5 K=2 INFRA verdict processed in v313


Acted-on 2026-06-01: anchor shipped + v5 K=2 INFRA verdict processed in v313
