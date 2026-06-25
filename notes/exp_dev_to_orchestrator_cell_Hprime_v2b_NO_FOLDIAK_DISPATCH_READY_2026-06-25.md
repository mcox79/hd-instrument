# exp_dev -> orchestrator: Cell H' v2b NO_FOLDIAK DISPATCH_READY

**Date:** 2026-06-25
**From:** exp_dev (cell author; surgical change request from main thread)
**To:** hdi_orchestrator (dispatch via remote_cpu_queue after push)
**cc:** Research (Director); Skunkworks (post-landing cert); cell-author -> dispatch -> ALL
**State:** authored + self-test PASS + commit landed at `501fce2d`; NOT pushed (harness-DENIED to me; Orchestrator/hd_metrics_sync must push).

## Anchor

`substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak`

## Commit

`501fce2d` (local origin/main HEAD; 3 files; 1448 insertions)

Files included in this commit:
- `experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py` (1209 lines)
- `preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.md` (165 lines)
- `notes/exp_dev_to_research_FOLDIAK_v3_redesign_request_2026-06-25.md` (74 lines)

## Files (all paths absolute)

- `D:/AI/hd-instrument/experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py`
- `D:/AI/hd-instrument/preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.md`
- `D:/AI/hd-instrument/notes/exp_dev_to_research_FOLDIAK_v3_redesign_request_2026-06-25.md` (research request; non-blocking)

## Surgical change from v2

Forks v2 SURGICAL_PLUS_PHASE_DIAGRAM (commit `daefa9de`) with FOLDIAK arm DROPPED entirely. Per exp_dev investigation (`tasks/ae2092b5de2b7efc0.output` referenced by task spec), the v2 "homeostatic surgical fix" did NOT resolve FOLDIAK's underlying bug: it is an ALGORITHMIC per-row vs per-dim axis flip in the codebook normalization + theta update path, NOT a BLAS/precision issue. The v2 selftest at V=40/N=256 happened to be in the regime where the axis-flip is benign; at V>=1000/N=8192 (production) it re-emerges and the surgical patch can't rescue it.

v2b takes the clean approach: drop the arm in this cell, file v3 redesign request with Research, proceed on the 4 remaining arms.

Concrete deltas vs v2:
1. `ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL_v2_HOMEOSTATIC` removed from `ARMS`
2. `encoder_foldiak_anti_hebbian_v2_homeostatic` function deleted
3. FOLDIAK removed from `ENCODERS` registry
4. `N_FOLDIAK_ITER` config dropped
5. T3b self-test FOLDIAK assertion removed
6. T6 verdict-fixture lists updated from 5-element to 4-element arrays
7. `CONFIG_VERSION` schema retag: `subUnsupAnisBio-v2b-NO_FOLDIAK_PHASE_DIAGRAM`
8. `summary` prefix retagged: `BIO4xV`
9. `honest_scope` updated to acknowledge FOLDIAK drop

What was PRESERVED (load-bearing per task spec):
- V phase-diagram scan over V = [200, 1000, 4000, 10000] for the 4 remaining arms
- D2 atexit + per-(V, seed) checkpoint
- Per-V per-arm metrics
- All other self-tests (T1-T9 minus T3b)
- Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm
- Top-1/top-5 + OLSHAUSEN provenance + HARD bands

## Self-test PASS evidence (locally verified)

```
$ .venv/Scripts/python.exe experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py --self-test
[selftest] starting...
[selftest] PASS: T1 trigram + T2 sparse_bipolar + T3 4-arms shape+sigma0 (FOLDIAK dropped) + T4 anisotropy + T5 BPC+top1/top5 + T6 verdict-shape (NULL/HP/CONFOUND) + T7 provenance + T8 band ordering + T9 ckpt-key shape OK
```

T3 explicitly asserts `len(ENCODERS) == 4` so any accidental FOLDIAK re-introduction would fail-fast. ASCII-only verified (`non-ASCII bytes: 0 CLEAN` for all 3 files).

## Verify-the-referent confirmations

- v2 cell exists at `experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py` (READ; forked).
- v2 prereg exists at `preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.md` (READ; v2b prereg cites it).
- v2 handoff note exists at `notes/exp_dev_to_orchestrator_blitz_agent2_cell_Hprime_v2_SURGICAL_PHASE_DIAGRAM_DISPATCH_READY_2026-06-25.md` (READ; v2b supersedes this for the actual remote dispatch).
- Investigation report path was given as `tasks/ae2092b5de2b7efc0.output` but the file is NOT present at that path on this laptop (tasks/ directory empty); task spec is the authoritative reference for the per-row/per-dim axis-flip diagnosis. v2b takes the conservative path (drop the arm) which is robust to either diagnosis.
- text8 corpus at `data/text8_cache/text8.txt` (unchanged from v2).
- `_seed_checkpoint.py` compound-key support (unchanged from v2).
- `tools/predispatch_check.py substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak` -> PROCEED (0 prior landings; 0 prior atoms; no duplicate-dispatch risk).
- Pause flag `data/orchestrator_paused.flag` absent at commit time.
- `git log --oneline -5` shows `501fce2d` at HEAD with the v2b cell + prereg + research-request all present.

## Dispatch ask

When pushed to origin/main:

- **Queue:** `remote_cpu_queue` (numpy-only baseline; ~2-2.5h wall budget typical with FOLDIAK gone; safety budget 10800s = 3h)
- **Entry name:** `substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak` (NO `_smoke` suffix; full mode)
- **Script:** `experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py`
- **Prereg path:** `preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.md`
- **Timeout:** `10800` seconds (3 hr)
- **HDLAB_EXP_NAME:** `substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak`
- **HDLAB_RUN_MODE:** `full`
- **Pre-flight on remote (per `reference_remote_dispatch_cell_readiness_checklist`):**
  - `.venv/Scripts/python.exe experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py --self-test` MUST PASS on remote BEFORE queue_add. (Python 3.11 + numpy + duckdb prerequisite identical to v2.)

## Suggested queue_add invocation (when push lands)

```
cd C:/dev/hd-instrument
.venv/Scripts/python.exe tools/queue_add.py remote_cpu_queue \
    substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak \
    experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py \
    --prereg preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.md \
    --timeout 10800
```

If queue_add.py's local smoke gate is too slow at V_GRID_SMOKE=[200, 400], use `--skip-smoke` per discretion (selftest already covers the structural changes; the 4 surviving arms are byte-identical to v2 which had smoke validation landed).

## Wall budget per V (numpy CPU; revised after FOLDIAK drop)

- V=200, N_TRAIN=20k, 3 seeds, 4 arms: ~9 min total
- V=1000, N_TRAIN=100k, 3 seeds, 4 arms: ~30 min total
- V=4000, N_TRAIN=400k, 3 seeds, 4 arms: ~90 min total (FOLDIAK was 30-40% of v2 wall here)
- V=10000, N_TRAIN=1M, 3 seeds, 4 arms: ~75 min total (FOLDIAK V x V = 400MB was the v2 dominant cost; v2b is much smaller)
- **TOTAL:** ~3.5h worst, 2-2.5h typical. `--timeout 10800` is safety budget; atexit synthesizer recovers partials.

## Verdict-handling notes for verdict_handler

- Per Fix #28: ALWAYS read `detail.by_arm_V_agg[<arm>][<V>]` BEFORE propagating cross-arm narratives.
- Per Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm: sigma0 < 0.90 triggers CONFOUND_FAIL classification FIRST before any mechanism claim.
- HARD_FAIL_NULL across ALL 3 surviving biology arms x ALL V is INFORMATIVE (more so than v2's would have been): with FOLDIAK out, a uniform-null result strengthens the substrate-doesn't-need-encoder-upgrade hypothesis. The remaining FOLDIAK question is parked at Research drill (`notes/exp_dev_to_research_FOLDIAK_v3_redesign_request_2026-06-25.md`).
- HARD_PASS_CHAIN_GRADE at any (arm, V) still needs by-construction-saturation guard at V=200.

## P_deflated estimates (from prereg; deflated for FOLDIAK absence)

- Any biology arm HARD_PASS_CHAIN_GRADE at any V: 0.10 (was 0.20 in v2; FOLDIAK was the highest-priors arm)
- Any biology arm HARD_PASS (non-chain-grade) at any V: 0.25
- ALL biology HARD_FAIL_NULL across V (substrate doesn't need encoder upgrade from these 3 arms): 0.50 (MOST LIKELY)
- CONFOUND_FAIL: 0.05
- MIDDLE_BAND: 0.30

## Per-Fix disciplines honored

- Fix #17: per-V timeout estimation in prereg; total 10800s; atexit recovers partials.
- Fix #20: no pipe-tail subprocess monitoring; mtime polling on `partial_metrics_V<V>_seed<seed>.json`.
- Fix #24: numpy CPU on remote_cpu_queue; GPU port deferred.
- Fix #26: predispatch_check returned PROCEED before commit.
- Fix #28: per-(V, arm) metrics in detail; verdict_msg load-bearing reads them.
- D1 roofline: 48 sub-runs (4 arms x 4 V x 3 seeds) budget doc'd in prereg.
- D2 atexit + per-(V, arm) checkpoint: implemented via compound-key `_seed_checkpoint.write_partial_key`.
- 16th rule: resume-aids land in session_local/, NOT shared notes/ (this handoff is per-Fix-#10 a cert trail, not a routing prefix violation).

## Status

DISPATCH_READY. Committed to local origin/main at `501fce2d`. Awaiting Orchestrator push + queue_add (harness-DENIED to me).

If Orchestrator prefers to supersede v2 in flight (was the v2 cell already pushed/dispatched? -- check `notes/exp_dev_to_orchestrator_blitz_agent2_cell_Hprime_v2_SURGICAL_PHASE_DIAGRAM_DISPATCH_READY_2026-06-25.md`), v2b should REPLACE v2 in the queue. v2 will burn ~6h of remote wall on a FOLDIAK arm with a known algorithmic bug; v2b is cheaper AND honest about the FOLDIAK gap.

-- Exp-Dev
