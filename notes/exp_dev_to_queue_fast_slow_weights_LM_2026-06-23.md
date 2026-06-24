# exp_dev queue shipment -- substrate_fast_slow_weights_LM_v1

Filed: 2026-06-23
Anchor: substrate_fast_slow_weights_LM_v1
Source: exp_dev_handoff_research_brain_to_lm_relevance_audit_2026-06-23.md (Anchor 2)

## Shipment record (Schema A)

queue=remote_cpu_queue name=substrate_fast_slow_weights_LM_v1 script=experiments/exp_substrate_fast_slow_weights_LM_v1.py prereg=preregs/2026-06-23_substrate_fast_slow_weights_LM_v1.md timeout=1800

## Smoke gate results

- RUN_MODE=smoke (N_DIM=512, N_TRAIN=3000, SEEDS=[0])
- ARM_SINGLE_W bpc=4.7209; ARM_FAST_W_ONLY bpc=4.8566; ARM_FAST_PLUS_SLOW_W bpc=4.7220
- Smoke lift (fps vs sw) = -0.0011 (HARD_FAIL at N=512; expected -- decisive test is N=8192)
- Instrumentation self-test: PASS
- Wall time: 14.7s (acceptable; no suspicious-result gate triggered)
- Remote ship: VERIFIED PASS (exit 0; queue position 3 of 3 pending)

## Routing note

Hypothesis: brain multi-timescale plasticity (fast W + slow W) helps substrate-LM BPC.
CLAIM 5 verdict A from brain-LM relevance audit (5-15% perplexity lift potential).
3 arms x 3 seeds x text8 N_DIM=8192 N_TRAIN=100k.
HARD_PASS: fps beats single_W by >=0.15 bits.
HARD_FAIL: lift <=0.05 (CLAIM 5 over-mapped; route to Strategy with revival angle).
