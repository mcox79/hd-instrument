# Pre-reg: CELL SC VSA scaling existential probe at 10M (decoupled-cue scaling curve) -- GPU

Date 2026-06-13. Cell `exp_substrate_sc_vsa_scaling_probe_partition_routing_10M_gpu_v1.py`. Research-SIGNED Option A
(notes/research_to_exp_dev_CELL_SC_DECISION_ENDORSE_Option_A_..._pre_reg_2026-06-13.md). Synthetic; no atom reads; torch->GPU (remote desktop).

Question: does the substrate's L1 partition-routing + per-partition VSA cleanup SURVIVE to 10M atoms (vs flat cleanup's tau-limit interference collapse)?

Decoupled-cue model: clean CATEGORY cue (Dc=256) drives routing; noisy IDENTITY cue (Di=1024, recovery cos=TARGET_COS=0.133) drives cleanup.
Sweep N in {1e5, 1e6, 1e7}; partition size capped at 40K (<=50K). Routed cleanup searches only the routed partition (N-invariant); flat searches all N.

Signed criteria (ALL 4 primary HARD-PASS => HARD-PASS; ANY HARD-FAIL => HARD-FAIL; else MIDDLE):
1. Routed recall@10 at N=1e7 >= 0.60 (HARD-FAIL < 0.40)
2. Flat recall@10 strictly monotone-decreasing across the N sweep (HARD-FAIL non-monotone/increasing -> cue interaction)
3. Routing accuracy at N=1e7 (P=250) >= 0.90 (HARD-FAIL < 0.70)
4. Max partition size <= 50K (HARD-FAIL > 100K)
5. (diagnostic) tau-window vs D: widens with D=2048 -- reported, not gating.

Smoke (part_size=2000, N up to 1e5) validated logic: routed 0.933 N-invariant, flat 0.825->0.675 strictly-decreasing, routing 1.0, tau-floor widens. Full result on remote GPU.
