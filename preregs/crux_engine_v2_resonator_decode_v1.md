# Pre-registration: crux_engine_v2_resonator_decode_v1

Anchor: `crux_engine_v2_resonator_decode_v1`
Cell: `experiments/exp_crux_engine_v2_resonator_decode_v1.py`
Author: exp_dev | 2026-07-10 | Base: `exp_crux_engine_fb15k237_vsa_gt_v1.py` (v1 HARD_FAIL)

## Hypothesis
The v1 crux HARD_FAILed at the COMPOSE decode: single-shot VSA candidate-recall bled to bundle
crosstalk (`vsa_recall@10`=0.203 vs symbolic 0.491), while verify+rank were HEALTHY conditioned on
recall (cond_mrr 0.415 >= 0.377). MEASURED@`data/exp_crux_engine_fb15k237_vsa_gt_v1/metrics.json`.
FIX (this cell): replace the single-shot unbind+argmax-cleanup decode with an ENTITY-CODEBOOK
RESONATOR-RECOVERY decode -- per query (h,r3) the substrate forms a bundle q superposing rule-reached
tail entity codes (via bind/unbind through a head-memory), and recovers the buried tails by
batched-restart iterative-deflation cleanup against the entity codebook, with a residual re-bind gate.

## Topology note (verified against v1 code + Director "N_DIM x N_entities" + drill)
The compose leak is SUPERPOSITION RECOVERY (simultaneous, resonator's home turf), NOT sequential
hop-chaining. Decode = recover tail entities from a superposed bundle; single-shot argmax buries
lower-SNR true tails; the resonator deflation recovers them.

## Arms
RESONATOR_GT (fix; residual-gated), RESONATOR_RAW (ungated diagnostic), SINGLE_SHOT_CLEANUP (the
comparator that buries tails), SYMBOLIC_GT (graph-traversal + conf; recall reference), POP_RELFREQ
(THE bar), POP_DEGREE, BIND_ABLATED (head-memory built with V+E; recovery must collapse),
BROKEN_VERIFIER (must fail), RANDOM (floor).

## Pre-registered two-stage bands (drill: notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md)
- STAGE-1 (fix works): residual-gated res_recall@10 >= 0.35 at N=2048 AND >= single_shot + 0.10 AND
  non-convergence rate < 0.20.  SNR-floor HARD_FAIL_A if residual-gated < 0.25.
- STAGE-2 (ultimate): RESONATOR_GT.h@1 >= POP_RELFREQ.h@1 + 0.02 AND mrr >= POP + 0.02.
- HARD_PASS = STAGE1 and STAGE2 and bind-load-bearing and broken-fails.
- HARD_FAIL_A = decode does not recover (SNR floor) -> fix moves UPSTREAM (bigger N / sparse-decorrelated
  codebooks / reduced compose-time bundling load), NOT more decode iteration.
- HARD_FAIL_B = recall recovered but still loses frequency -> wall is rank/knowledge (valuable).

## Folded-in drill requirements
1. Anti-spurious-convergence: RESIDUAL RE-BIND GATE (MAD-robust chance floor; report raw AND gated
   recall; gap = spurious-inflation). 2. Batched random restarts (R=8/16), init-only dither.
3. Codebook decoupling: entity codes are random near-orthogonal (NOT embedding-derived); pairwise
   cosine logged. 4. ACF hook: resonator_recover takes E_recon (asymmetric reconstruction codebook) so
   ACF (exp_wave14b_acf_resonator.py, cap_map row 51) wires in without redesign.

## Compute architecture
Class: mixed. Graph path-enumeration = sequential-CPU (justified: dict traversal). Resonator cleanup =
batched matmul on DEVICE (CUDA when available; local venv is torch+cpu so smoke runs device=cpu; GPU
exercised only on remote overnight_queue runner). device + cuda_avail logged to metrics.

## Self-test discriminators (must fire; PASS confirmed local)
D6 resonator recovers a buried superposition single-shot drops (res golds > single-shot golds);
D6b residual gate rejects spurious on pure noise; D7 bind decode recovers planted rule, add-ablation
collapses (bind load-bearing). D6/D6b/D7 PASS at N=256/512.

## SMOKE OUTCOME (local; two runs)
- N=512 tiny smoke: res_gated_recall@10=0.020 (single_shot=0.147 sym=0.347), nonconv=0.993 -> HARD_FAIL_A.
- N=2048 full-N discriminator-preview (120 queries, R=16, T=20): res_gated_recall@10=0.058
  (single_shot=0.175 sym=0.347), nonconv=0.950, resonator WORSE than single-shot -> HARD_FAIL_A robust.
Conclusion: the resonator entity-decode does NOT recover recall in this instantiation -- SNR-floor /
compose-time bundling-load limited (all rule-paths' tails superposed into ONE bundle q, K >> resonator
capacity even at N=2048). Per the SNR-floor branch, the fix is UPSTREAM. FULL NOT dispatched (a 3-seed
FULL would reconfirm HARD_FAIL_A + burn GPU). Next lever: v3 = SHARDED per-rule-path recovery (cut
bundling load per the substrate's sharded>bundled composition law), then bigger N / ACF if still short.

## cardinality / atomicity / error-checking
EXPECTED_N_UNITS = n_seeds (3 full). final_metrics_atomicity: tmp_replace. except SystemExit: raise
before except Exception (no BaseException/bare except). start_marker + crash_diagnostic + heartbeat
present. progress_logging: print_flush_true. crlb_n/a: rank-based KG completion (no closed-form floor);
reachability via ceiling. calibration_check: adaptive_with_discriminator_gate (residual re-bind gate;
self-test D6/D6b verify it fires).
