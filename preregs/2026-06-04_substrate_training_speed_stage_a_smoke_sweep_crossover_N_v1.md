# Prereg: substrate_training_speed_stage_a_smoke_sweep_crossover_N_v1
## Anchor
substrate_training_speed_stage_a_smoke_sweep_crossover_N_v1
## Routing
change_request_stage_a_smoke_sweep_crossover_N_2026-06-04 (responds to Stage A N=256 small-N artifact).
Finds the empirical crossover N* where substrate first beats the Adam-softmax baseline at matched BPC.
CPU numpy. SUPERSEDES the standalone substrate_training_speed_ladder_stage_a_charlm_v1_n2048 (which is removed;
its N=2048 question is one cell of this sweep). 5 N x 2 tasks x 3 seeds.
## Pre-registered bands (N* = smallest N with median speedup>=1.0 across both tasks)
HARD-PASS: N*<=2048 (advantage at substrate-class scale -> proceed to full run). MIDDLE: N*==4096.
HARD-FAIL: no crossover (substrate never beats Adam -> iterate trick selection; routes to REVISED comprehensive Stage A).
## Formula self-tests (PROT-022)
Adam lowers CE / cf-RPE shrinks / roll-bind order-sensitive / uniform=ln(V). [PASS]
## Smoke gate
Smoke (N=256,512): mechanics PASS; speedup<1 at low N (expected -- Adam wins where substrate capacity-starved).
NOTE: substrate W is O(N^2)/step vs Adam head O(VN) -> sweep is genuinely decisive about whether any crossover exists.
## PROT-018/021
swept-N anchor (no _nN binding). 3 seeds, per-seed partials. timeout 14400s.
## Queue
remote_cpu_queue (numpy).
