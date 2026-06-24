exp_dev dispatch 2026-06-23: substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1

queue=overnight_queue name=substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1 script=experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py prereg=preregs/2026-06-23_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.md timeout=10500

SHIP STATUS: VERIFIED (queue_add.sh exit=0; remote self-test PASS 2.3s; VERIFIED in remote overnight_queue/queue.json)

Pre-reg bands:
  HARD_PASS: lift >= 0.10 BPC bits (ARM_HEBBIAN_ONLY - ARM_CFRPE_STDP_HETEROGENEOUS BPC)
  CHAIN_GRADE_BONUS: lift >= 0.20 bits
  MIDDLE_BAND: lift 0.03-0.10 bits
  HARD_FAIL: lift <= 0.03 bits OR READOUT_DEGENERATE
  cv < 0.05 mandatory

Smoke result (N=512 laptop CPU):
  ARM_UNIGRAM: 5.523 BPC
  ARM_HEBBIAN_ONLY: 5.178 BPC
  ARM_CFRPE_ONLY: 4.773 BPC
  ARM_CFRPE_STDP_HETEROGENEOUS: 5.024 BPC
  lift (hetero vs hebbian): 0.154 bits (above HARD_PASS)
  smoke_elapsed: 35.7s

Fix #28 per-arm note: at smoke scale CFRPE_ONLY (4.773) outperforms HETERO (5.024). Do NOT frame as
"CFRPE_STDP is the best arm" until full-scale per_seed metrics.json lands and is read directly.

Timeout: 10500s (~2.9h). Flag: long run, within 4h limit.
