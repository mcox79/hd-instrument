# Pipeline Dispatched: n10_whitening_projection_revival_v1

**Date:** 2026-06-22 UTC
**Disposition (partial):** SMOKE_GREEN; FULL DISPATCHED + QUEUED; awaiting cell-land
**Cell commit:** cb43a625
**Smoke metrics commit:** cb43a625 (same commit as cell)
**Cert_ledger row hash:** (deferred to full-VET completion)
**Pipeline-agent template field-test:** Fix #11 SECOND USE (TODO #6 #8 #9 patches in cell)

## Plain English

N10 ZCA-whitens the contrastive-projected key matrix before storage + retrieval to test whether decorrelating dimensions lifts effective rank enough to re-open Path C ARM A. Local smoke (1 seed, M=1000, sigma=0.0) ran cleanly in 242s on this laptop: the cell wiring is OK, eff_rank lifts MASSIVELY from 16.71 (before) to 230.29 (after whitening; random-rotation control preserves at 16.71 as expected for the rank-invariant null). proj_recall_sanity is at 0.145 in smoke (not the 0.010 chance-baseline of the n9 full); smoke does NOT lift sanity because the smoke grid is too easy (TRAIN_M=600 small, M=1000 only, no held-out stress). The discriminator is M=10k full-scale, where n9 hit 0.010. Full was dispatched to remote_cpu_queue at queue position 3 (behind c1_cls_replay full+smoke); ETA-to-start ~1h45m, ETA-to-finish ~3h15m total. Awaiting cell-land for full-VET + atomization.

## Smoke results (load-bearing diagnostic confirmed wiring + raised eff-rank)

| metric | value | interpretation |
|---|---|---|
| eff_rank before whitening | 16.71 | smoke baseline; tightly clustered |
| eff_rank after whitening | 230.29 | massive lift toward full-d=256 isotropy |
| eff_rank after random rotation | 16.71 | rank-invariant; control valid |
| proj_recall_sanity before (n=200) | 0.145 | smoke easy regime, ABOVE chance |
| proj_recall_sanity after whitening | 0.130 | smoke: whitening does NOT help here (too-easy regime) |
| proj_recall_sanity after rotation | 0.145 | rotation preserves; control valid |
| Arm A unwhite argmax @ M=1k sig=0 | 0.022 | smoke chance |
| Arm B zca argmax @ M=1k sig=0 | 0.020 | smoke chance; lift -0.003 (no signal in too-easy smoke) |
| Arm C unwhite SMH @ M=1k sig=0 | 0.040 | smoke chance |
| Arm D random-rot argmax @ M=1k sig=0 | 0.020 | smoke chance |
| Smoke wall | 242s | encoding-dominated; runs OK |

**Critical reading:** smoke validates that the cell PIPELINE WORKS + eff_rank-lift mechanism FIRES under whitening (the load-bearing diagnostic). Smoke recall values cannot discriminate the rescue because the smoke grid (M=1000, single seed, sigma=0) is well below the discriminator regime where n9 found the chance-baseline. The HARD_PASS / HARD_FAIL test is full-scale at M=10k sigma=0.1 across 3 seeds.

## Pre-reg bands (echo from spawn-prompt; Skunkworks recommendation P~0.45-0.55)

- **HARD_PASS:** Arm B recall >= 0.35 at M=10k sig=0.1 AND proj_recall_sanity_after >= 0.15 (3x revival WORKS; sparse-superposition + decode-algebra families RE-OPEN)
- **MIDDLE_BAND:** 0.10 <= Arm B recall < 0.35 at M=10k sig=0.1 (partial mechanism; whitening helps but not enough)
- **HARD_FAIL:** Arm B recall < 0.10 at M=10k sig=0.1 OR proj_recall_sanity_after < 0.05 (whitening insufficient; route to encoder upgrade pythia-1B -> 2.8B per CERT 591 precedent)

## Dispatch state

- Queue: remote_cpu_queue (marsh@home; SCP done; VERIFIED in queue.json)
- Cell: experiments/exp_n10_whitening_projection_revival_v1.py (commit cb43a625)
- Pre-reg referent: notes/n9_smh_landed_vet_skunkworks_2026-06-22.md (commit 9ac12d79; section "2x -> 3x revival route")
- Wall budget: 10800s (3h; per Fix #11 TODO #8 conservative encoding-dominant pattern)
- Queue position: 3 (behind c1_cls_replay smoke + c1_cls_replay full RUNNING)
- c1 deadline (its own 7200s timeout, started 03:35:49 remote-time): ~05:35:49 remote-time
- n10 ETA-to-start: ~1h45m after dispatch
- n10 ETA-to-completion: ~3h15m after dispatch (encoding 1900s/seed x 3 seeds = ~95min compute + queue wait)

## Fix #11 template field-test report (SECOND USE; patches from n9 lessons)

| Patch | Status | Notes |
|---|---|---|
| TODO #6 in-cell smoke detection | INSTRUMENTED | `_NAME_SAYS_SMOKE = "_smoke" in os.environ.get("HDLAB_EXP_NAME","").lower()`; falls into RUN_MODE if env var or arg flag don't fire. Not exercised by the dispatch (full mode; HDLAB_EXP_NAME = "n10_whitening_projection_revival_v1" -- no _smoke suffix); will exercise next time we dispatch a smoke through queue_add.sh. |
| TODO #8 conservative wall budget | APPLIED | 10800s = 3 * max(measured 1900s, 1500s) * 1.5 safety margin. n9 timed out at 3600s; doubled. Will verify post-cell-land. |
| TODO #9 atexit/SIGTERM synthesize-from-partials | INSTRUMENTED | `atexit.register(_synthesize_on_exit)` + SIGTERM handler registered BEFORE main loop; will fire if the runner SIGKILLs mid-run (testing the pattern n9 had as a gap). Not exercised by smoke (normal exit); will validate IF full run hits any timeout. |
| Pre-flight smoke ran locally (NOT through queue_add) | NEW VARIANT | Saved an SSH round-trip; gave faster local feedback. Validates that local-smoke + remote-full split is viable when wall is well-understood. |

**New observation (queue-position dependency):** The pipeline-template Section 5c "post-dispatch verify-it-starts (within 5 min)" assumed minimal queue contention. With c1_cls_replay full running and c1 smoke + n10 both queued, n10's ETA-to-start depends on c1's actual wall (could be up to 2h). This is a TODO #11 for the template: queue-position visibility + ETA-to-start surfacing before deciding to enter poll loop.

## Honest Scope

- Smoke validates wiring + eff_rank-lift mechanism on M=1k single-seed CPU pythia-160m. Does NOT yet test the discriminator regime where n9 found chance-baseline.
- Full run will test M=1k/5k/10k x sigma=0/0.1/0.3 x 3 seeds on remote_cpu_queue (CPU only; ~3h total wall).
- IF HARD_FAIL: route to encoder upgrade (pythia-160m -> 1B -> 2.8B) per CERT 591 precedent (skunkworks recommendation #2 in n9 landed-VET 2026-06-22).
- IF HARD_PASS: sparse-superposition + decode-algebra rescue families RE-OPEN; sparsemax-attractor (n9) + Hopfield-class (n9) + PKM (deferred) become testable on whitened keys.

## Cert Ledger Row (deferred until full-VET)

Will be built after full lands + verify-off-data + verdict-disposition. Atom ID candidate: `math::T3/EXP_n10_whitening_projection_revival_v1`. Cert_class: depends on verdict (chain_grade_ruling for HARD_PASS / measured_mechanism for MIDDLE_BAND / honest_negative for HARD_FAIL).

## Artifacts

- Cell: experiments/exp_n10_whitening_projection_revival_v1.py (commit cb43a625)
- Smoke metrics: data/exp_n10_whitening_projection_revival_v1/metrics.json (commit cb43a625; LOCAL smoke; run_mode=smoke)
- Pre-reg referent: notes/n9_smh_landed_vet_skunkworks_2026-06-22.md (commit 9ac12d79)
- Composes-with ledger rows:
  - 2caf2f8f6cf148ab (n9 HONEST_NEGATIVE; the immediate referent for the 3x revival)
  - f2a658ddda005c98 (Path C ARM A HARD_FAIL; the layer-below referent)
  - CERT591_kv_learned_projection_v1 (the projection-lineage origin)

## Asks (deferred until cell-land)

- Skunkworks: independent landed-VET when data lands (re-derive Arm B from per_unit; verify proj_recall_sanity_after; check eff_rank diagnostic; verify Arm A anchor reproduces n9's 0.0081 and Arm C reproduces n9's 0.0194 as cross-cell sanities; ratify or adjust inline disposition; A5 atomize if chain-grade)
- Research: pre-stage 3x-revival-of-3x-revival angle on encoder upgrade pythia-1B IF n10 HARD_FAILs (don't wait until verdict; can be drafted in parallel)

## 2x-Revival Angle (mandatory iff HARD_FAIL; pre-staged)

If n10 HARD_FAILs the discriminator OR the proj_recall_sanity_after stays below 0.05, the revival route is **encoder upgrade**:
- Phase 1: pythia-160m -> pythia-1B with the SAME whitened-projection pipeline (cheaper than 2.8B; tests whether the issue is encoder rank-deficiency).
- Phase 2: pythia-1B -> pythia-2.8B if Phase 1 still HARD_FAILs (CERT 591 used 2.8B successfully on held-out facts; established precedent).
- Composes-with: any future encoder-upgrade cell can re-use n10's whitening machinery + arm structure (A/B/C/D); just swap ENCODER constant.

PKM remains GATED behind eff-rank-raising (per Skunkworks's n9 landed-VET ranking; cannot dispatch until either n10 HARD_PASS or encoder upgrade succeeds).
