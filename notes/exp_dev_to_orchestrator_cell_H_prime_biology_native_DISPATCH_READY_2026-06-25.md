# exp_dev -> orchestrator: Cell H' (biology-native unsupervised anisotropic encoder) DISPATCH_READY

**Date:** 2026-06-25
**From:** exp_dev (cell author)
**To:** hdi_orchestrator (dispatch)
**cc:** Research (Director); cell-author -> dispatch -> ALL (via fleet tracker)
**State:** authored + self-test PASS + pre-reg committed; NOT dispatched (USER decides timing per Director spec sequencing-recommendation).

## Anchor

`substrate_unsupervised_anisotropic_encoder_biology_native_v1`

## Files

- `experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py` (cell)
- `preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v1.md` (pre-reg)
- `notes/director_cell_H_prime_biology_unsupervised_encoder_spec_2026-06-25.md` (Director spec; cited)
- `notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md` (3x drill; cited)

## What it tests

5-arm biology-native UNSUPERVISED anisotropic encoder shotgun (per USER 2026-06-25 basis-vs-use-case: NO labels at basis layer):

1. ARM_RANDOM_BIPOLAR_BASELINE (control)
2. ARM_OLSHAUSEN_FIELD_SPARSE_CODING (V1 analog; forward-only SoftHebb; NaN-guarded)
3. ARM_DEEPWALK_ON_BIGRAM_GRAPH (place-cell analog; substrate-native cooccurrence graph; NO external taxonomy)
4. ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL (decorrelation; lateral inhibition; NaN-guarded)
5. ARM_KOHONEN_SOM_TOPOGRAPHIC (substrate-native variant with position-tag XOR-bind to preserve sigma=0 identity)

Two metrics per arm:
- BPC on text8 held (vs fair_harness rail 7.3065)
- A3' label-free heldout-word generalization (cluster IDs from substrate-native k-means on bigram-cooccurrence; NO external labels)

Plus anisotropy diagnostic (eigenspread + cosine-spread + mechanism_fired) per Fix #28 + by-construction-saturation guard.

## Self-test PASS evidence

Run `.venv/Scripts/python.exe experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py --self-test`

```
[selftest] starting...
[selftest] T3b: production-scale NaN probe on ARM_OLSHAUSEN_FIELD...
[selftest] T3b PASS: ARM_OLSHAUSEN_FIELD finite at N=2048 V=400 idx=2000
[selftest] PASS: T1 trigram + T2 sparse_bipolar fraction + T3 all-5-arms shape+sigma0 + T4 anisotropy +
                 T5 BPC pipeline + T6 cluster+A3' + T7 verdict-shape (HF/MB/HP/CONFOUND) + T8 band ordering OK
```

Coverage:
- T1: char-trigram bipolar output
- T2: sparse_bipolar fraction-f exactness
- T3: all 5 arms produce (V, N_DIM) shape + sigma=0 cleanup recall=1.000 + np.isfinite all-true (NaN/Inf guard)
- T3b: production-scale NaN probe on ARM_OLSHAUSEN_FIELD at N=2048 V=400 idx=2000 (matmul kernels identical to N=8192 production)
- T4: anisotropy_diagnostic returns required keys
- T5: build_hebbian_W_np + path_a_bpc finite + positive
- T6: substrate-native cluster IDs + target_clusters + A3' label-free metric
- T7: compute_verdict handles HARD_FAIL / MIDDLE_BAND / HARD_PASS / CONFOUND_FAIL all correctly
- T8: band-ordering well-formed (HP_FULL < HP_PART < HF; A3 lift bands monotone)

Supplemental NaN probe (heavier than selftest):
- N=8192, V=2000, text8 10k tokens, ARM_OLSHAUSEN_FIELD -> 30.8s wall, output finite, shape (2000, 8192). Confirms NO NaN class bug at production-scale matmul (Wave F Cell 1 heads-up addressed).

## Verify-the-referent confirmations

- Director spec exists at `notes/director_cell_H_prime_biology_unsupervised_encoder_spec_2026-06-25.md` (READ; bands verbatim).
- 3x drill exists at `notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md` (READ; arms + P_deflated absorbed).
- Both cited notes are committed in origin/main per `git log --oneline --all -- ...` (visible to remote runners).
- fair_harness rail at `experiments/exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1.py` (verified file exists; sanity_T=0.05 reference 7.3065).
- text8 corpus at `data/text8_cache/text8.txt` (verified; absent in smoke prevents silent fallback).
- _seed_checkpoint.py PROT-021 config-mismatch guard active.
- predispatch_check.py `substrate_unsupervised_anisotropic_encoder_biology_native_v1` returned PROCEED (0 prior landings, 0 prior atoms; no duplicate-dispatch risk).
- pause flag `data/orchestrator_paused.flag` absent at author-time.

## Heads-up-handled (Wave F Cell 1 SoftHebb-NaN at N=8192/V=4000/text8)

Per coordinator heads-up mid-authoring (2026-06-25):
- Added explicit NaN/Inf detection to selftest T3 + T3b (production-scale probe).
- Added per-batch NaN guard in ARM_OLSHAUSEN_FIELD training loop (update-clipping at +/- 1.0; Frobenius-norm clipping; early-fallback to char-trigram if W goes non-finite).
- Added per-iter NaN guard in ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL (same fallback pattern).
- Verified Olshausen finite at N=8192/V=2000 in heavier supplemental probe.
- SOM redesigned to bind per-position bipolar XOR-tag (substrate-native; preserves sigma=0 distinctness through neighborhood updates).

## Dispatch ask (when USER green-lights)

Per Director spec sequencing-recommendation:
1. Wait for Wave F Cell 1 v3 hub-spoke MRC landing (coordinator says Wave F Cell 1 just HARD_FAILed with SoftHebb NaN; Wave F Cell 5 HYBRID HARD_PASS_CHAIN_GRADE).
2. If hub-spoke is stuck on SoftHebb NaN, Cell H' is now the natural alternative (tests 4 OTHER biology mechanisms, only ARM_OLSHAUSEN shares SoftHebb math family AND has independent NaN guard).
3. USER decides timing.

**When green-lit:**
- **Queue:** overnight_queue (per Director spec) OR remote_cpu_queue (numpy-only baseline; no actual GPU usage without torch port -- Fix #24 caveat). Author recommendation: **remote_cpu_queue first** (numpy works; GPU port is follow-up optimization).
- **Timeout:** 10800s (3 hr; matches Director spec sequencing wall budget).
- **HDLAB_EXP_NAME:** `substrate_unsupervised_anisotropic_encoder_biology_native_v1` (NO `_smoke` suffix; full mode).
- **HDLAB_RUN_MODE:** `full`.
- **Commit-first:** cell + prereg + this handoff note must be on origin/main BEFORE remote dispatch (uncommitted laptop notes invisible to autonomous pipeline -> GATE_FAIL prereg-not-found).
- **Pre-flight on remote (per reference_remote_dispatch_cell_readiness_checklist):**
  - `.venv/Scripts/python.exe experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py --self-test` MUST PASS on remote BEFORE queue_add. (Python 3.11 + numpy + duckdb prerequisite; identical to other recent numpy-only cells.)

## Verdict-handling notes for verdict_handler

- Per Fix #28: ALWAYS read `detail.by_arm_agg[<arm>]` BEFORE propagating cross-arm narratives. Don't read verdict_msg alone -- it summarizes, doesn't load-bear.
- Per Fix #28 + USER 2026-06-23: do NOT over-claim from a single arm passing; biology-native lift = at least ONE biology arm beats random by >= +0.05 on A3'.
- By-construction-saturation guard active: if ALL arms reach A3' >= 0.95, tier as MEASURED_MECHANISM not chain-grade and require larger V=16000 follow-up (saturation regime).
- CONFOUND_FAIL gate: if sigma=0 cleanup recall < 1.000 for any arm, the verdict is CONFOUND_FAIL (implementation bug suspected; NOT mechanism rejection). Re-author/debug before re-dispatch.

## P_deflated rollup (from Director spec)

- Any-arm HARD_PASS: 0.45
- DeepWalk best: 0.35
- Olshausen-Field best: 0.30
- Foldiak best: 0.25
- Kohonen SOM best: 0.20
- All-arms HARD_FAIL: 0.15

## Sequencing observation

Coordinator says Wave F Cell 1 hub-spoke v3 HARD_FAILed with `RuntimeError: FIX_1_BROKEN_SPOKE: spoke[0] softhebb: spoke_recon_err is NaN` -- the SoftHebb spoke produces NaN at this exact regime. If the Director sequencing rule was "ship Cell H' AFTER hub-spoke v3 HARD_PASSes," that conditional is now resolved differently: hub-spoke v3 FAILed on SoftHebb-NaN, which means encoder-side biology mechanisms become the *more urgent* path (federation hit a wall at the same encoder-NaN bug). Cell H' tests 5 mechanisms with independent NaN guards in the 2 affected (Olshausen + Foldiak); 3 others (Random, DeepWalk, SOM) are mechanically immune to the SoftHebb-class bug.

Suggestion: USER may want to dispatch sooner (de-prioritizing the hub-spoke-v3-PASS conditional) given hub-spoke v3 closed via NaN-bug rather than scientific outcome.

## Status

DISPATCH_READY. Awaiting USER green-light + Orchestrator dispatch action.

-- Exp-Dev
