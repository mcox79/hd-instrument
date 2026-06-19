# Prereg: substrate_training_speed_ladder_stage_a_charlm_v1_n2048
## Anchor
substrate_training_speed_ladder_stage_a_charlm_v1_n2048
## Routing
routing_training_speed_iterative_ladder_stage_a_tiny_charLM_2026-06-04 (Stage A; user strategic direction).
CPU numpy, $0. Fair design: same task + same cb-context-features; only the trained head + algorithm differ
(substrate cf-RPE/posbind-symW + cosine readout vs standard SGD/Adam softmax head). 2 tasks (bigram, trigram),
V=70, N=2048, 3 seeds. speedup = baseline_wall_to_match_substrate_BPC / substrate_wall.
## Pre-registered bands (median speedup; substrate must be a real LM gap_sub>0.3 else cell VOID->HF)
HARD-PASS: median speedup>=10x AND both cells gap_sub>0.3. MIDDLE: 2-10x. HARD-FAIL: <2x OR a cell gap_sub<=0.3.
## Formula self-tests (PROT-022)
Adam step lowers CE / cf-RPE shrinks error / roll-bind order-sensitive / uniform=ln(V). [PASS]
## Smoke gate
Smoke (N=256,V=40): mechanics PASS; verdict HARD_FAIL (speedup 0.2x) -- EXPECTED small-N artifact: at N=256 the
substrate is capacity-starved (gap~0.5), so Adam matches that easy target in ~1 epoch. The substrate BPC (hence
the target Adam must chase) scales with N; full N=2048 is the real test of the training-speed advantage.
## PROT-018/019/021
_n2048 -> N=2048. timeout floor 14400s. 3 seeds, per-seed partials.
## Queue
remote_cpu_queue (numpy; GPU not needed). Note: cornerstone-audit-Llama-8B routing is Testbed's lane (cloud H100), not shipped here.
