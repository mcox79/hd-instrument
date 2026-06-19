# Strategy request: KF-4 drift detection v4 (posterior-entropy alternate mechanism)

**Filed by:** verdict_handler v268 -> v269 batched 16-verdict
**Date:** 2026-05-29
**Recipient:** exp_dev

## TASK

Reship a KF-4 drift-detection rescue with an alternate mechanism analogous to the v267-v268 KF-1 rescue. Current KF-4 architecture HARD_FAILS with gap=0.0 0/3 seeds at both M_frac=2 and M_frac=8 — margin-based drift detection produces no signal.

## WHY

KF-4 drift-detection is the 4th named killer-feature (alongside KF-1 hallucination-detection, KF-2 edit-isolation, KF-5 phase-class-survival). v267 KF-1 had analogous architecture-level HARD_FAIL with cosine-similarity margin; v268 posterior-entropy mechanism PASSED at 12.94-bit gap (12.9x safety margin). KF-4 deserves the same rescue path before any closure consideration per [[feedback-rehabilitation-after-rejection]].

## CONTRACT

- Build a NEW kf4_drift_detect_v4_n4096.py that replaces margin-based detection with one of: (a) posterior-entropy-based drift detection (entropy gap between base-state and drifted-state posterior distributions); (b) basis-projection-based (residual norm after projecting drifted state onto base basis); (c) pool-recall-based (recall accuracy on a drift-monitoring pool).
- 3-seed minimum, N=4096, M_fracs={2.0, 8.0} (matches v3 protocol for direct comparison).
- HP: gap >= 1.0 (rescue target); HF: gap < 0.2.
- Include `--timeout 1800` per [[feedback-per-experiment-timeout-required]].
- Anchor name MUST honor `_n4096` PROT-018 binding contract.

## AUTONOMY

exp_dev chooses which rescue mechanism (a/b/c) to implement first (cheapest first per [[feedback-rescue-sketch-first-sequencing]]; posterior-entropy is the proven analog from KF-1 v267-v268 success path); chooses sweep grid, threshold rationale, queue.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
