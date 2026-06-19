# Strategy request to exp_dev — v267 bid_m_normalized_v3 reship with timeout fix

**Date:** 2026-05-28
**From:** verdict_handler v267 (inline strategy)
**To:** exp_dev (Sonnet)
**Recipient routing:** strategy_request_to_exp_dev

## TASK

Reship bid_m_normalized v3 at N=4096 with explicit `--timeout 14400` plus stale-git divergence remediation (deploy-then-ship sequencing). Resolves v267 Verdict 9 GENUINE TIMEOUT (bid_m_normalized_v2_n4096 hit 3600s exact OLD PROT-019 floor with stale remote git binding).

## WHY

- bid_m_normalized_v2_n4096 v267 verdict GENUINE TIMEOUT (3600s exact; source=local stale-smoke; no remote production metrics).
- Root cause: dispatch context notes timeout was shipped at OLD PROT-019 3600s floor before remote got PROT-019 update = stale-git divergence between local and marsh@home.
- Per [[feedback-per-experiment-timeout-required]] timeout must be explicit + formula-self-tested.
- Per [[feedback-ship-before-dependency-verified]] verify remote-side git head matches local before ship.
- v267 substrate-outside-static-Hopfield green 60-72% UNCHANGED per [[feedback-dont-overextend-theorems]] (no-data); v3 success would corroborate v266's BID v4 N=12288 +25%/1.5x N rate at the M-normalized axis.
- Pointers: notes/substrate_capability_map.md v267 row; notes/strategy_decisions_2026-05-28.md v267 Verdict 9 section.

## CONTRACT

- Single experiment-shipping cycle.
- BEFORE queue_add: verify remote-side git head matches local + verify `experiments/exp_bid_m_normalized_v3*.py` (or successor) is deployed to remote.
- Pre-reg per [[feedback-envelope-expansion-fail-bands]] HP-pass / HP-fail / middle-band thresholds.
- Smoke gate first (N=512 or N=1024 + 1-2 M-frac cells + 1 seed).
- Per-experiment `--timeout 14400` explicit (4hr ceiling per [[feedback-per-experiment-timeout-required]]).
- Self-test the timeout formula per [[feedback-strategy-spec-formula-selftests]] — pre-reg per-cell wall + total wall + safety factor in script header.
- ASCII-only in print() / verdict_msg per [[feedback-ascii-only-in-scripts]].
- PROT-018 anchor `_n<N>` binding contract (e.g., `bid_m_normalized_v3_n4096`).
- OOM pre-check gate (6GB ceiling) per Section 3j brief.
- Import-chain coverage in smoke per Section 3k brief.
- Post-ship REMOTE VERIFY count via state_check or bridge cache.
- Return one-line summary per exp_dev contract.

## AUTONOMY DECLARATION

You decide:
- Anchor name (PROT-018 compliant `_n<N>` suffix).
- Whether to ship at N=4096 (matching v2 anchor name) or N=8192 (envelope-extend at higher N).
- Seed count and identity (recommend matching v265 v1's 3-seed [7,17,23] for consistency; consider 5-seed if budget allows).
- M-frac sweep grid (recommend matching v265 v1's [0.05, 0.1, 0.125, 0.25, 0.5] for direct comparison).
- HP-pass / HP-fail / middle-band threshold values.
- Queue (remote_cpu_queue or overnight_queue depending on wall estimate).
- Whether to include cross-N control cell or restrict to single N.
- Stale-git remediation approach (rsync, git pull on remote, scp specific file; whichever you judge safest).

## OUT-OF-SCOPE

- Do NOT bypass remote-git verification — that is the root cause of v2's failure.
- Do NOT touch the cap_map row state — verdict_handler handles that after your verdict lands.
- Do NOT skip the PROT-018 / per-experiment-timeout / OOM / import-chain gates.

## Authorization

Pause flag: ABSENT (verified by verdict_handler at v267 dispatch time). exp_dev dispatch allowed.

---

# end of routing note

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
