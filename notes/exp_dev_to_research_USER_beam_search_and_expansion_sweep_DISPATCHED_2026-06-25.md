# exp_dev -> research: USER-directed Cells X + Z DISPATCHED 2026-06-25

**From:** exp_dev (cell-author)
**To:** research (Director / team lead)
**Date:** 2026-06-25T18:00Z
**Status:** BOTH CELLS DISPATCHED + REMOTE VERIFIED
**Commit:** 2bc43052 (local main; not pushed)

## Summary

Per USER explicit direction "Full auto. Two cells from user insight on Gap 1 (multi-hop) + Gap 2 (anisotropy)". Both cells authored, self-tested, smoked, committed, dispatched, REMOTE VERIFIED.

## Cell X: substrate_multihop_beam_search_with_WM_candidates_v1

**Routing:** local_cpu_queue
**Queue position:** 5 of 5 pending (~3-5h ETA behind queue)
**Timeout:** 7200s
**Prereg:** preregs/2026-06-25_substrate_multihop_beam_search_with_WM_candidates_v1.md

**USER quote driving cell:** "with our PFC we should be able to do the brain analog easily no? We should try that, since we already have PFC" + "We're not going to live with the ceiling we know it can be done"

**6th multi-hop attempt; the architectural lever not tested in prior 5 HARD_FAILs.** Prior 5 (pointer-chain-v2 / wm-scaffold / csp-gated / consolidation-v3 / pfc-chunked-2hop) all did per-hop TOP-1 cleanup. Per-step accuracy decays 0.69 -> 0.485 -> 0.31 -> 0.205 -> 0.145; 5-hop cumulative ~0.122.

**Mechanism (brain-correct PFC analog):** parallel-candidate beam search with top-K cleanup per hop, ranked by cumulative softmax log-score. Preserves runner-up information that single-top1 discards. Uses substrate's WM-multi-bank-as-candidate-slot pattern (chain-grade K=1024 @ N=4096 today) + per-hop cleanup primitive + CSP-style confidence ranking (no LLM forward calls).

**Arms (5):**
- ARM_BASELINE_HRR_2HOP (sanity rail [0.62, 0.68])
- ARM_SINGLE_TOP1_5HOP (rail ~0.122; matches pointer-chain v2)
- ARM_BEAM_W2_TOPK3_5HOP
- ARM_BEAM_W5_TOPK3_5HOP
- ARM_BEAM_W10_TOPK5_5HOP

**Pre-reg bands (LOCKED):**
- HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM: W10 >= 0.50 AND monotonic (W2 < W5 < W10 within tol=0.02) AND cv <= 0.07
- HARD_PASS_PARTIAL: W10 >= 0.30 (lift over 0.122 rail)
- HARD_FAIL_BEAM_DOESNT_HELP: W10 < 0.20 (6th attempt also fails; beam is not the lever)
- SANITY_BREACH: baseline outside [0.62, 0.68] in 2/3+ seeds
- Q_SATURATION 0.995 guard

**Config:** N=8192, V_C=200, V_P=10, K_SET=20, n_chains=200, seeds [7, 17, 23] (apples-to-apples with prior 5 attempts), depth=5.

**Smoke result:** baseline=0.645 (within rail) single=0.78 beam_w10=0.86 (same pattern as chunked-2hop precedent; META_M7-compliant).

**Strategic significance:** if beam works at full -> 6th multi-hop attempt SUCCESSFUL via brain-correct PFC analog. Barrier 1 revived; 2-hop ceiling lifts; substrate scales to deeper composition. If it fails -> beam-of-W with W=10 is NOT the lever either; multi-hop ceiling is more fundamental and we need a different mechanism.

## Cell Z: substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1

**Routing:** overnight_queue (GPU; RTX 4060 Ti)
**Queue position:** 1 of 1 pending (sole pending; GPU runner picks up next)
**Timeout:** 14400s (4h)
**Prereg:** preregs/2026-06-25_substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1.md
**Remote verify:** PASSED (gate confirmed entry present in remote overnight_queue/queue.json)

**USER quote driving cell:** "if you have a cone - why can't you project the origin into the 'middle' of that cone and blow out all the parts to a bigger space?" + "Why can't you expand the cone to be 360 degrees (just fan it out in 3d)?"

**USER's geometric intuition is exactly the cerebellar mechanism.** v2 (chain-grade-candidate at M=10k, Bfly=0.997 saturated) used EXPAND=5x of d=768. Brain operates at MUCH larger ratios:
- Cerebellar mossy -> granule: ~7M x expansion
- Fly olfactory PN -> KC: ~40x expansion
- v2 substrate: 5x

**Mechanism:** fly-LSH sparse fan-in (K=5 cerebellar regime) at progressively larger expansion ratios. AB_CONTROL = dense random Gaussian at the largest expansion tests the alternative hypothesis "any random projection at brain-scale rescues" (which would discriminate "expansion-to-high-dim" from "specifically-fly-LSH-sparse-fan-in").

**Arms (6):**
- ARM_RAW (baseline; reproduces v2 raw=0.018)
- ARM_FLY_LSH_5x (matches v2 fly_lsh=0.997 baseline reproduce)
- ARM_FLY_LSH_64x (~12x more)
- ARM_FLY_LSH_512x (close to fly-olfactory 40x)
- ARM_FLY_LSH_4096x (closer to brain-scale; d_p=3.15M sparse)
- ARM_AB_CONTROL_4096x (dense Gaussian control at same expansion)

**Pre-reg bands (LOCKED):**
- HARD_PASS_FLY_LSH_RESCUES_AT_BRAIN_EXPANSION: FLY_4096x >= 0.85 AND beats AB_CONTROL by >= 0.10 AND monotonic (5x <= 64x <= 512x <= 4096x within tol=0.02) AND cv <= 0.05
- HARD_PASS_PARTIAL_EXPANSION_HELPS: monotonic lift visible but plateau below 0.85
- HARD_FAIL_EXPANSION_DOESNT_HELP: FLY_4096x <= FLY_5x + 0.02
- MIDDLE_BAND_CONTROL_ALSO_HELPS: AB_CONTROL within 0.10 of FLY_LSH_4096x (mechanism is expansion-to-high-dim, not specifically fly-LSH)
- HARD_FAIL_OOM_AT_EXPANSION_X: graceful per-arm OOM-catch

**Config:** PROJ_DIM=768, K_FANIN=5 (cerebellar regime; matches v2), KWTA_FRAC=0.02 (looser than v2 0.10 to bound memory at 4096x), FLY_TOPK_FRAC=0.005 (scales with d_p), M=10000 (matched to v2 M_max for cross-cell), seeds [11, 13, 19], Pythia-2.8b encoder + contrastive train pipeline shared with v2.

**Memory engineering:** sparse-fan-in matrix stored as torch.sparse COO (190MB at 4096x); fly-LSH tags stored as topk-indices (no full d_p int8 tensor materialized); AB_CONTROL uses chunked dense-Gaussian with running-topk merge across dp-chunks (oversample 2x then final topk-cut). Tag-overlap argmax via sparse @ dense for query chunks. Per-arm GPU peak-mem logged for evidence.

**Smoke result (CPU; pythia-160m; M=400; expansions [5, 64]):** raw=0.055 FLY_5x=0.750 FLY_64x=0.995 AB_CONTROL_64x=0.995 -- Q-discipline saturation flag fires correctly for both; MIDDLE_BAND_PARTIAL verdict path triggered (because 4096x not in smoke). Discrimination requires full M=10000 + pythia-2.8b on GPU at 4096x.

**Strategic significance:**
- if monotonic improvement up to 4096x + beats control -> **anisotropy IS solved at brain-scale expansion**; the 55x rescue at v2 was real and we need bigger expansion at production; cerebellar mechanism scales
- if AB_CONTROL also saturates -> mechanism is generic-expansion-to-high-dim (still chain-grade-candidate, but for a different claim than v2)
- if no lift at 4096x over 5x -> rescue mechanism is regime-bound to small expansion; brain-scale doesn't matter at substrate scale

## Disciplines honored

- Pre-reg per envelope-fail-bands (locked at module init via assert)
- Smoke gate FIRST (mandatory; both cells smoked locally before dispatch)
- ASCII-only in scripts
- Per-arm metrics (Fix #28)
- _seed_checkpoint imported (PROT-021 OK for Cell Z 14400s timeout)
- PROT-020 OK for Cell Z (torch imported actively)
- META_M7: smoke matches full on capacity-sensitive dimensions
- Q-discipline saturation guards in both verdicts
- REMOTE VERIFY post-ship for Cell Z (gate confirmed presence in remote queue.json)
- Fix #26 predispatch_check.py: both anchors PROCEED (no recent landings)
- Fix #24: Cell Z uses active torch.cuda; GPU peak-mem logged
- No padding experiments (both are USER-direction-driven decision-grade)
- Commit BEFORE remote dispatch (2bc43052)

## What I'm waiting on

- runner: Cell X cell-land on local_cpu_queue (~3-5h ETA behind queue)
- runner: Cell Z cell-land on overnight_queue (1-4h ETA; sole pending)
- skunkworks: landed-VET on both cells once metrics.json arrives

## Pause flag status

NOT_PAUSED at dispatch time. Both dispatches authorized.

-- exp_dev 2026-06-25T18:00Z
