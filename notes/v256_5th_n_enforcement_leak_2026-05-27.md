# v256 systemic remediation note — 5th N-enforcement leak

**Date:** 2026-05-27 23:00
**Cap_map version:** v256
**Severity:** MEDIUM (no concrete harm in this batch but high systemic risk)
**Status:** OPEN — PROT-020 candidate surfaced for next strategy cycle review
**Trigger event:** orchestrator anomaly investigation on 4 GPU FULL anchors completing in 3-79s vs estimated 30min-3h

## What happened

The orchestrator flagged a suspected systemic infrastructure failure after observing
4 GPU "FULL" anchors complete in 5-90 seconds. The expected runtime was 30min-3h.
The orchestrator hypothesized four failure modes:

- (A) script error / import failure / syntax bug
- (B) script ran as SMOKE not FULL (wrong N parameter; runner-validator was supposed
      to refuse this but maybe these names lack `_n<N>` suffix so it passes)
- (C) KF battery scripts have shared dependency issue
- (D) honest substrate result at much faster compute than estimated

## Resolution

**Hypothesis (D) HONEST FAST** — verified by Step 0 honest re-read of all 4 anchors:

- All 4 metrics.json files exist on remote (via bridge `get_metrics()`)
- All 4 have 5 seeds (7, 17, 23, 31, 41) with per-cell numerical data
- All 4 ran at config.N=4096 (NOT smoke N)
- All 4 verdict_msg labels are HONEST against per-cell metrics (0 label-vs-honest catches)
- KF battery v2 anchors are inherently inference-only (no training) at N=4096 → 3-80s
  on GPU is realistic. The 30min-3h orchestrator-side estimate was over-budgeted.

Anchors:
1. kf5_steerable_beta_v2 — KF5_HARD_PASS, elapsed 9.98s, 5 seeds × 7 betas = 35 cells
2. axis1_mb_chunk2_v1 — AXIS1C2_HARD_PASS, elapsed 79.0s, 140 cells
3. kf1_hallu_impossibility_v2 — KF1_MIDDLE_BAND, elapsed 5.3s, 5 seeds × 5 M_fracs
4. kf4_drift_detect_v2 — KF4_HARD_PASS, elapsed 3.2s, 5 seeds at N=4096 M=4096

The orchestrator dispatch text ALSO noted `kf5_steerable_beta_v2 verdict:failed
ended 5s after ship 22:55:41`. This event-bus `failed` tag was INCORRECT
— actual metrics show KF5_HARD_PASS at elapsed=9.98s. This is the SECOND
infrastructure-tag-vs-honest-metrics mismatch today (first was v254 KF-5 v1
metrics-source-fallback). Different mechanism (event-bus tag-flip vs SSH-None
+ local-smoke-fallback), same recovery pattern (per-cycle remote forensics).

## The systemic gap that IS real

Even though hypotheses (A)/(B)/(C) did not fire in this specific batch, the
orchestrator's hypothesis (B) analysis exposed a **real enforcement leak in
PROT-018**:

> The runner-validator (60d2147) only enforces `_n<N>` ↔ `--N <N>` binding —
> if names like `kf5_steerable_beta_v2` lack `_n<N>` suffix, validator doesn't
> trip. So we have a 5th leak in the N-mismatch enforcement: anchors WITHOUT
> `_n<N>` suffix could still run mis-specified.

**Confirmed:** PROT-018 anchor-name `_n<N>` binding is enforced by:
- exp_dev pre-ship grep (`grep -E "(N\s*=|n\s*=)\s*<SUFFIX_N>"`) against the script
- queue_add.py exit-6 (ship-time validator rejects mismatches before smoke runs)

**However:** the validation only triggers when the anchor name CONTAINS `_n<N>`
suffix. All 4 anchors today (`kf5_steerable_beta_v2`, `axis1_mb_chunk2_v1`,
`kf1_hallu_impossibility_v2`, `kf4_drift_detect_v2`) lack `_n<N>` suffix —
validator inert. In these 4 specific cases the scripts genuinely ran at
config.N=4096 5-seed (verified by per-cell metrics having 5-seed × N=4096
evidence) so no concrete harm. **But the leak is real:** an anchor named
`bigprobe_v1` (no `_n<N>`) shipped expecting N=8192 could silently run at
smoke-leak N=512 and validator would not trip.

## PROT-020 candidate proposals

**Option A: mandate `_n<N>` suffix for any FULL-budget anchor**
- queue_add.py SHOULD require `_n<N>` suffix on any anchor with `--smoke False`
  budget > 5min (mandate-suffix-for-FULL-budget rule).
- Rejects ships at exit-8 with message:
  `ERROR: FULL-budget anchor name lacks _n<N> suffix — required by PROT-020
  for ship-time validation. Rename to <name>_n<N> or pass --allow-no-n-binding
  with justification.`
- Implementation: ~30 lines in `tools/orchestrator/queue_add.py` exit-8 branch.
- Pro: cleanest enforcement; forces structural discipline.
- Con: existing anchor naming conventions (e.g. KF battery uses `_v<N>` for
  version, not N-binding) would need rename or `--allow-no-n-binding`
  justifications threaded through every FULL ship.

**Option B: runner-side wall_anomaly_detected event**
- runner SHOULD compute expected_wall_s from the per-experiment `--timeout`
  formula (PROT-019: `1.5 × smoke_wall_s × (FULL_N/smoke_N)^exp ×
  (FULL_seeds/smoke_seeds)`).
- runner SHOULD fire `wall_anomaly_detected` event when
  `actual_wall_s < 0.1 × expected_wall_s` (10× faster than expected).
- This catches BOTH the leak this note documents AND any future smoke-leak
  failure mode independent of anchor-name suffix.
- Implementation: ~50 lines in `tools/orchestrator/runner_v2_prod.py`
  post-completion hook + new event kind in heartbeat_watchdog.py.
- Pro: structural-not-textual enforcement; no naming-convention churn.
- Con: also fires on legit honest-fast results (like this batch); needs
  whitelisting OR severity classifier OR per-anchor expected_wall_s override.

**Option C: combine A + B**
- Mandate `_n<N>` for FULL-budget anchors AS THE PRIMARY enforcement.
- Add wall_anomaly_detected event AS DEFENSE-IN-DEPTH for anchors with
  `--allow-no-n-binding` override.
- This is the most robust but most-implementation-cost option.

**Recommendation:** start with B alone (lowest naming-convention disruption;
catches the most failure modes; can be tuned to ignore legit fast results by
adjusting the 0.1× threshold or per-anchor expected_wall_s override).

## Why this is MEDIUM severity not HIGH

- No concrete harm in this batch (4 anchors verified HONEST).
- Existing PROT-018 enforcement still catches anchors WITH `_n<N>` suffix
  (which is the dominant naming convention for FULL ships since 2026-05-27 lockin).
- 77 cumulative label-vs-honest catches were caught by other means (verdict_msg
  vs per-cell honest re-read; metrics-source-fallback bridge alerts) before
  PROT-018 landed.
- The "anchor name without `_n<N>` shipped at smoke-leak" failure mode has not
  been observed in the wild yet — this is a forward-looking remediation.

## Why this is NOT LOW severity

- Anchor naming convention for product-feature-evidence anchors (KF battery,
  axis sweeps, killer-feature probes) systematically omits `_n<N>` because the
  N is documented in script config not anchor name.
- As substrate work shifts from framework-class probes (named `_n<N>` for
  N-stability tracking) to product-feature probes (named without `_n<N>`),
  the leak surface area GROWS over time.
- This batch already shipped 4 such anchors in a single GPU wave — the
  pattern is active.

## Next steps

1. Surface PROT-020 candidate to next strategy cycle for lock-in decision.
2. If accepted: implement option B (runner-side wall_anomaly_detected) as
   the lowest-disruption first step.
3. Add to post-PROT-018 backlog sweep candidate list per v235 brief
   recommendation (anchor-name-vs-actual-N reconciliation for pre-PROT-018
   anchors).
4. Cross-reference with v254 KF-5 v1 metrics-source-fallback note +
   `feedback_no_label_vs_honest_anchor_names.md` for the cumulative
   N-enforcement-failure-mode classification.

## Related notes

- `notes/orchestrator_post_compaction_brief.md` Section 3g (PROT-018)
- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_no_label_vs_honest_anchor_names.md`
- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_per_experiment_timeout_required.md`
- v254 strategy_decisions entry (1st METRICS-SOURCE-FALLBACK observation)
- v256 strategy_decisions entry (this note's parent record)
