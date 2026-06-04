# Prereg: substrate_trained_mini_lm_readout_fix_nsweep_v2_capped

## Anchor
substrate_trained_mini_lm_readout_fix_nsweep_v2_capped

## Routing / supersedes
Re-ship of substrate_trained_mini_lm_readout_fix_nsweep_v1 (routing_substrate_training_n_sweep_readout_fix),
which was KILLED after ~2h20m (intractable: N->16384 + 100k chars + per-SEED checkpointing -> hours/seed,
nothing saved until a full seed finished). Root cause = SubstrateCharLM's sequential per-char Python loop
(loop length x ~N per step), NOT matmul throughput -> GPU does not help; CPU is correct. Fix = tractability
+ per-CELL checkpointing.

## Scientific question (unchanged)
At what substrate N does the calibrated-readout SubstrateCharLM (2-layer, alpha_max=0.05) cross from
"no learning" (gap<0.3 bits) to "substantive learning" (gap>=1.0)? N in {512,1024,2048,4096,8192}, 3 seeds,
TRAIN_CHARS=30k. gap = uniform_bpc - calibrated_bpc.

## v2 changes vs v1
- N capped at 8192 (drop 16384). - TRAIN_CHARS 100k->30k. - PER-CELL checkpoint (partial after each (seed,N)).

## Pre-registered bands (BITS)
HARD-PASS: gap>=1.0 at/above N_threshold AND <0.3 below AND monotone AND threshold in {512..8192} AND 3/3 seeds.
MIDDLE: improvement but max gap<1.0, OR threshold only at 8192 edge, OR 2/3 seeds.
HARD-FAIL: gap<0.3 at all N up to 8192.

## Formula self-tests (PROT-022)
1. fit consumes >=1 pair + score_bpc finite. 2. uniform_bpc=log2(vocab)>0. 3. calibrated<=temp1. [PASS]

## Smoke gate
Smoke PASSED locally (N={128,256,512}, 5k chars, 2 seeds): per-cell checkpoint works; cells run (~1s each);
gaps ~0 at tiny scale (expected). Full N<=8192/30k est ~15-25 min wall.

## PROT-018 / 021
NO _nN suffix (N swept). Per-cell partials cell_s<seed>_N<n>.json. timeout 14400s.

## Queue
remote_cpu_queue (CPU; numpy Python-loop substrate -- GPU would NOT help this online algorithm).
