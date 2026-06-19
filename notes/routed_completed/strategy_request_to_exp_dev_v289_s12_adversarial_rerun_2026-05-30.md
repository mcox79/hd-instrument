# Strategy request -> exp_dev: S12 adversarial_multi_hop_probing re-ship

**Filed.** 2026-05-30 by verdict_handler v288->v289 batched 14-verdict processing.

**Status.** NOT AUTO-DISPATCHED. User explicit no-refill (T2-T5 still draining; orchestrator handles next batch). Surfaced for orchestrator main-thread review.

## Why

S12 `adversarial_multi_hop_probing_v1_n4096` verdict = `S12_INCONCLUSIVE` with verdict_msg "no cells" and elapsed_s=4.46. cells=[] in metrics payload = script crashed/exited before generating any per-cell measurements. Cannot perform meaningful Step 0 honest re-read on absent data.

The security-critical regulated-industry claim this anchor was meant to assess -- zero leakage across 5 adversarial pattern categories -- CANNOT be evaluated from a "no cells" run. Per [[feedback-no-smoke]] we explicitly do NOT treat empty-payload + brief-elapsed as a probe outcome; this is a runner failure and the underlying capability question is UNTESTED not REFUTED.

## What is needed

1. Pull the runner log for `exp_adversarial_multi_hop_probing_v1_n4096.py` from `marsh@home:C:/dev/hd-instrument/logs/` to identify the crash mode (timeout, exception, OOM, config-validation, missing dependency, etc.).
2. Smoke re-ship with explicit cells emitted (verify cells > 0 in metrics payload pre-FULL).
3. FULL re-ship at the originally-intended envelope: M=2048, depth=5, n_q=32, 5 adversarial pattern categories, 5 seeds.

## Pre-reg / smoke gate (per [[feedback-envelope-expansion-fail-bands]])

- HARD_PASS: 0 leakage across all 5 categories, all seeds, all queries (max_leak_rate < 1/n_q == 0.03 per cell; n_pass_categories = 5/5; n_hf = 0/5 categories).
- HARD_FAIL: any category leaks > 5% across multi-seed (mean_leak_rate >= 0.05 + sigma_margin >= 2.0).
- MIDDLE_BAND: 0 < leak < 5% per category, OR clean leak with mixed pattern categories (some 0 some > 0).
- INCONCLUSIVE: cells = 0 (current state); retry required.

## Smoke gate

- N=1024 reduced cell, 1 seed, n_q=8, 5 categories = sanity check that cells > 0 emit + adversarial-pattern-generation code path executes; should take < 60s on local CPU.

## Routing target

CPU smoke first (local CPU runner; ~60s); FULL on GPU only after smoke verifies cells > 0.

## Cap_map dependency

Adversarial-probing row state UNCHANGED (UNTESTED, not REFUTED) until re-ship completes. Per [[feedback-rehabilitation-after-rejection]] this rescue is filed BEFORE any closure consideration; row remains open.

## Not-urgent unless

S-batch + T-batch results force a security-critical claim into substrate killer-features production-narrative (regulated-industry positioning) ahead of when smoke + FULL can complete. Currently surfacing for orchestrator decision; user explicit no-refill mode honored.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
