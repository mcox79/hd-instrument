# exp_dev queue routing note -- dual trace neuromod LM

Filed: 2026-06-23
By: exp_dev (Sonnet sub-agent)

## Shipment record

queue=overnight_queue name=substrate_dual_trace_sequential_neuromod_LM_v1 script=experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py prereg=preregs/2026-06-23_substrate_dual_trace_sequential_neuromod_LM_v1.md timeout=5400

## Context

Anchor 1 from notes/exp_dev_handoff_research_neuromodulator_orthogonal_composition_2026-06-23.md

Tests brain-correct dual-trace sequential neuromodulator mechanism (Brzosko 2017 + Huertas 2016)
against naive-multiplicative and single-trace baseline. Decisive test for sparse-bipolar envelope
cap (+0.44 bits BPC): either dual-trace breaks it (substrate-as-LM viable) or confirms rank-1
Hebbian cap structural (pivot to refuse-aware-knowledge-store).

HARD_PASS pre-reg: ARM_DUAL_TRACE >= +0.20 bits vs ARM_BASELINE AND >= +0.10 bits vs ARM_NAIVE_MULT
HARD_FAIL: ARM_DUAL_TRACE within +/-0.05 of ARM_BASELINE OR fails to beat ARM_NAIVE_MULT

Smoke result: READOUT_DEGENERATE (expected on laptop without gensim; char-trigram fallback at
N=512 N_TRAIN=2000 produces lambda=0 optimal; same as 3-axis cell ARM_DOPAMINE_ONLY behavior).
Remote --self-test PASS in 2.9s on GPU machine .venv.

REMOTE VERIFY: queue_add.sh exit 0 + confirmed present in marsh@home remote overnight_queue/queue.json.
Commit: 7f450ce7 (branch: main)
