# Strategy request to exp_dev — v256 KF battery v2 follow-on (queue refill)

**Filed:** 2026-05-27 23:05 by verdict_handler sub-agent inline
**Cap_map version trigger:** v256 (commit faaa3b5)
**Pause flag state:** ABSENT (ACTIVE)
**Queue state at filing:** GPU overnight_queue pending=0 running=0 = source-queue invariant VIOLATED per [[feedback-pipeline-pacing]]

## TASK

Ship one or more GPU-bound experiments to refill overnight_queue depth >= 1. Pick from the candidate pool below; you autonomously decide ship-order, anchor names, exact configs, timeouts, and queue choice per [[feedback-no-experiment-design-in-prompts]] and [[feedback-no-padding-experiments]].

## WHY (live context pointers, not summaries)

- `notes/substrate_capability_map.md` row v256 — 4 KF battery v2 anchors HARD_PASS at FULL N=4096 5-seed; phase-boundary direct-test row LIFT 55-70 -> 60-75%; framework reliability product-feature LIFT 68-80 -> 73-85%; portfolio 14+22 -> 14+23.
- `notes/strategy_decisions_2026-05-27.md` v256 entry — full per-verdict honest-reread + 5-rescue-sketch detail.
- `notes/v256_5th_n_enforcement_leak_2026-05-27.md` — NEW infrastructure gap PROT-020 candidate (anchors WITHOUT `_n<N>` suffix bypass PROT-018 validator); your pre-ship grep on these new anchors should explicitly use `_n<N>` suffix to comply with the recommendation.
- `data/exp_kf5_steerable_beta_v2/metrics.json` — KF-5 baseline metrics at N=4096 (entropy collapse curve 7.71->0.12 over beta=2-128; 5 seeds replicate within 0.02).
- `data/exp_axis1_mb_chunk2_v1/metrics.json` — axis1 phase-boundary baseline at M/N=8 (ret=0.503 +/- 0.028).
- `data/exp_kf1_hallu_impossibility_v2/metrics.json` — KF-1 verdict_msg honestly under-claims at 1.71e-4 (Tier-1 spec was <= 1e-6 = 170x off).
- `data/exp_kf4_drift_detect_v2/metrics.json` — KF-4 baseline at HP3 strength.

## CONTRACT

- Deliverable: 1-3 GPU-bound anchors shipped to overnight_queue with REMOTE VERIFY post-ship.
- Each anchor MUST use `_n<N>` suffix in name (PROT-018 binding) to ensure validator triggers and to comply with PROT-020 candidate recommendation.
- Each anchor MUST pass `--timeout <seconds>` per PROT-019 formula.
- Each anchor MUST pass OOM pre-check (6GB ceiling) per Section 3j.
- Each anchor MUST exercise the same import chain in smoke as in FULL per Section 3k.
- Smoke gate before FULL per envelope-fail-bands convention.
- ASCII-only `print()` + `verdict_msg` per [[feedback-ascii-only-in-scripts]].
- self-test per [[feedback-strategy-spec-formula-selftests]].
- Return format: `exp_dev: shipped <N> anchors to <queue list>; REMOTE VERIFY <counts>; next: <plan>`.

## CANDIDATE POOL (pick 1-3; you decide ship-order and which to defer)

### Priority 1 — directly justified by v256 batch

(d) **`kf5_steerable_beta_v3_n8192_5seed_full`** — envelope-extension of KF-5 v2 to 2x N to confirm beta-steering scales (entropy collapse depth should grow with N if substrate-intrinsic; flat-or-shrinking would imply finite-N artifact). +0.05-0.10 lift to KF-5 row if cleared. Estimated ~30min GPU.

(e) **`kf_battery_joint_v1_n4096_5seed_full`** — joint KF-1 x KF-3 x KF-4 x KF-5 single-substrate run testing whether one substrate instance simultaneously satisfies all 4 killer-feature criteria. IF all 4 hold on one instance THEN TIER-1 product feature claim ("all 4 KF features ship from one substrate"). IF fails on subset THEN per-substrate-per-KF caveat surfaces. Estimated ~2h GPU.

### Priority 2 — open follow-ups from v256 and earlier batches

- **`axis1_mb_chunk3_v1_n4096_5seed_full`** — fine-grained M ∈ {2N, 8N} mapping to refine the M/N=8 transition crossing observed in chunk2. Closes the M=32768-to-65536 region resolution. Estimated ~1h GPU.

- **`kf1_tier1_rescue_v1_n4096_5seed_full`** — KF-1 v2 verdict_msg honestly noted "weaker than Tier-1 spec requires" (Tier-1 was <= 1e-6 mean_oos_max_conf; observed 1.71e-4 = 170x off). Rescue arm could probe per-construct or per-binding to find specific failure modes that drive max_conf above 1e-6. Estimated ~1h GPU.

### Priority 3 — non-batch-justified (skip unless capacity allows)

- KF-3 multi-substrate state-isolation rescue (v254 noted state-contamination 5% baseline at coupling=0; rescue would isolate per-construct contamination mechanism).
- SKAH-M 6-cell battery N=8192 envelope-extension (substrate-class confirmation strengthening; per v228 lock).
- Saad-Solla v12 5-seed N=8192 to complete v11 2-seed -> 5-seed convention.

## AUTONOMY DECLARATION

You decide:
- Which 1-3 anchors to ship (do NOT ship the full pool; per [[feedback-no-padding-experiments]] every shipped anchor must be strategically justified, not target a queue-depth number).
- Exact anchor names (must include `_n<N>` suffix).
- Per-anchor sweep grids, threshold formulas, HF1/HF2/HF3 numerical bounds.
- Queue target (overnight_queue / remote_cpu_queue / local_cpu_queue) — GPU is depleted so default lean is overnight_queue but you may route to remote_cpu_queue if anchor is genuinely cheap.
- Timeout (per PROT-019 formula).
- Smoke gate parameters.
- Whether to defer the joint single-substrate test (e) until KF-5 N=8192 envelope-extension (d) lands first, OR ship them in parallel.

## DO NOT

- Do NOT ship more than 3 anchors in this refill (queue-depth-target padding is forbidden per [[feedback-no-padding-experiments]]).
- Do NOT design experiments I have not justified above (do NOT invent anchors outside the candidate pool unless you have explicit strategic justification from cap_map v256 entry).
- Do NOT ship without `_n<N>` suffix on any anchor (PROT-018 binding + PROT-020 candidate compliance).
- Do NOT bypass smoke gate, import-chain coverage, OOM pre-check, or PROT-019 timeout.
- Do NOT push from your context — surface commit hashes if any.

## PAUSE GATE STATUS

Pause flag ABSENT (ACTIVE) at filing time. Re-verify before queue_add:
```bash
test -f d:/AI/hd-instrument/data/orchestrator_paused.flag && echo PAUSED || echo ACTIVE
```
If PAUSED at the time you read this file: ABORT and write a routing-refused note.
