# Strategy request to exp_dev — v267 KF1 hallucination-detection rescue

**Date:** 2026-05-28
**From:** verdict_handler v267 (inline strategy)
**To:** exp_dev (Sonnet)
**Recipient routing:** strategy_request_to_exp_dev

## TASK

Probe whether KF1 hallucination-detection failure (c1_kf_battery_phase_v1_n4096 0/3 across ALL M including in-capacity M=20K) is mechanism-specific or substrate-level. Cheapest rescue arm of 3-5 per [[feedback-rehabilitation-after-rejection]] before deciding whether KF1 stays in the killer-features inventory.

## WHY

- c1_kf_battery_phase_v1_n4096 verdict v267 (C1_MIDDLE_BAND HONEST): KF1 + KF1B fail above_thresh_frac=1.0 across all M (no OOS discrimination); KF2 + KF5 pass at all M including deep over-capacity M=200K.
- Current KF1 mechanism (margin-based threshold) appears to be the failure point — not substrate's underlying information.
- Cap_map row "killer-feature phase-class profile" at yellow 45-60% (new v267) with KF1 implicit LABELED-AT-RISK.
- Per [[feedback-rehabilitation-after-rejection]] 3-5 rescue arms required before closure; this is rescue arm 1 (CHEAPEST).
- Pointers: notes/substrate_capability_map.md v267 row; notes/strategy_decisions_2026-05-28.md v267 Verdict 4 section; data/exp_c1_kf_battery_phase_v1_n4096/metrics.json (remote-bridge `_source=remote` authoritative).

## CONTRACT

- Single experiment-shipping cycle.
- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HP-pass / HP-fail / middle-band thresholds before queue_add.
- Smoke gate first (small N + 1-2 seeds + 1-2 M cells).
- Self-test the discrimination metric per [[feedback-strategy-spec-formula-selftests]] (input -> expected output cells).
- ASCII-only in print() / verdict_msg per [[feedback-ascii-only-in-scripts]].
- PROT-018 anchor `_n<N>` binding contract; `_v<N>` is version not N-binding.
- Per-experiment `--timeout <s>` REQUIRED per [[feedback-per-experiment-timeout-required]]; formula self-test.
- OOM pre-check gate (6GB ceiling) per Section 3j brief.
- Import-chain coverage in smoke per Section 3k brief.
- Post-ship REMOTE VERIFY count via state_check or bridge cache.
- Return one-line summary per exp_dev contract: `exp_dev: shipped <N> anchors to <queue list>; REMOTE VERIFY <counts>; next: <plan>`.

## AUTONOMY DECLARATION

You decide:
- Specific alternate hallucination-detection MECHANISM (e.g., posterior-entropy-based; basis-projection-based; pool-recall-based; or something better that you identify). The rescue list noted "posterior-entropy-based" as one candidate — adopt or reject as you judge.
- Anchor name (PROT-018 compliant).
- N value (smoke + FULL).
- Seed count and identity.
- M-frac sweep grid (must include in-capacity M to anchor against c1 baseline).
- HP-pass / HP-fail / middle-band threshold values.
- Queue (CPU expected; route per [[feedback-laptop-cpu-quick-probes]] + [[feedback-gpu-first-for-depth-probes]]; ~30min CPU is appropriate for this scope).
- Timeout value (formula self-test in script header).
- Whether to include a control cell (re-run baseline KF1 to confirm baseline c1 result).

## OUT-OF-SCOPE

- Do NOT design the c1 baseline mechanism into this script — focus on the ALTERNATE mechanism + minimal apples-to-apples comparison.
- Do NOT touch the cap_map row state — verdict_handler handles that after your verdict lands.
- Do NOT skip the PROT-018 / per-experiment-timeout / OOM / import-chain gates.

## Authorization

Pause flag: ABSENT (verified by verdict_handler at v267 dispatch time). exp_dev dispatch allowed.

---

# end of routing note

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
