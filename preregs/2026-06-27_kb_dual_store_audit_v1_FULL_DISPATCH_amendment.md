# Pre-reg amendment: kb_dual_store_audit_v1 FULL dispatch (2026-06-27)

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M)
**Base prereg:** `preregs/2026-06-26_kb_dual_store_audit_v1.md` (Wave 3a ANCHOR 5)
**Trigger:** USER directive 2026-06-27 — Wave 3 USER vetting protocol requires
dual-store match >= 95% before promoting any Wave 3 anchor. ANCHOR 5 smoke landed
at MIDDLE_BAND (match_rate=0.90, exactly the lower band floor). FULL dispatch is
needed to verify dual-store implementation matches single-store reference at
production query count (100 queries vs 10 in smoke).

## Cell + script (UNCHANGED)

- Cell file: `experiments/exp_kb_dual_store_audit_v1.py` (unchanged since
  2026-06-26 atomization commit f97d675f or similar)
- Self-test: PASSES (formula self-test confirms 4-verdict-tier classification logic)
- Smoke (already landed): `data/exp_kb_dual_store_audit_v1_smoke/metrics.json`:
  - verdict: MIDDLE_BAND
  - match_rate: 0.9000 (10 queries; 9 match; 1 no_overlap_no_expected_hit)
  - user_directive_retention: 1.0000 (n=0; vacuous since smoke had no UD queries)
  - audit_log_integrity: ok
  - elapsed_s: 155.3
  - KB scope: n_entities=578104, n_atoms=1031163, encoder=char_trigram_v1

## Amendment scope

This amendment changes ONLY the dispatch routing for the FULL run.

### Original prereg routing: `local_cpu_queue`

### Amended routing: `remote_cpu_queue` (USER directive 2026-06-27)

**Reason:** Remote CPU is idle per USER directive 2026-06-27; this is a
substrate-KB consistency check (no GPU needed; matmul-free cosine query +
filesystem-grep over notes/preregs/memory dirs). Remote CPU run frees laptop
for cell-authoring + smoke gates during USER-directed dispatch burst.

Push gate: harness-DENIED to exp_dev; cell dispatched via Orchestrator.

## Why full needed (not just smoke landed)

USER vetting requires `match_rate >= 0.95` (HARD_PASS bar) before any Wave 3
bounded-capacity anchor promotes. Smoke at 10 queries landed 0.90 = exactly
at MIDDLE_BAND floor, providing no margin. Full run at 100 queries:

1. Establishes whether the 0.90 was sample-size noise (1/10 mismatch) or a
   real ceiling (likely 10/100 mismatches at 100-query scale).
2. Validates audit log integrity under concurrent-write stress (full run enables
   stress test at stress_duration=2s; smoke skips this).
3. Provides the USER_DIRECTIVE retention measurement at the >= 5 UD-query
   subset (smoke had n_user_directive=0 so retention was vacuous).
4. Stresses the filesystem-grep + substrate-KB equivalence across the full
   100-query coverage (smoke was the first 10 by ordering bias).

## Pre-reg bands (UNCHANGED from base prereg)

| Verdict | Condition |
|---------|-----------|
| HARD_PASS | match_rate >= 0.95 + ARM_AUDIT_LOG_INTEGRITY ok + USER_DIRECTIVE retention=1.0 |
| MIDDLE_BAND | match_rate in [0.90, 0.95) + both arms ok + UD retention=1.0 |
| HARD_FAIL | match_rate < 0.90 OR USER_DIRECTIVE retention < 1.0 OR audit log integrity broken OR substrate-only violation |

USER_DIRECTIVE zero-loss invariant is HARD gate (any UD query mismatch = HARD_FAIL).

## ETA + Timeout

Smoke wall: 155.3s at 10 queries -> ~15.5s per query for substrate query +
filesystem grep + audit log append. Full at 100 queries: ~1550s = ~26 min.
Plus concurrent-write stress (~5s).

**Estimated wall: ~30-35 min on remote CPU.**

**Timeout: 5400s (90 min)** — generous 3x margin over estimate. Anchor name
contains no `_n<N>` suffix; PROT-019 floor not triggered. Cell has no
checkpoint helper but the full run is bounded (no per-seed structure;
single-shot query loop); timeout < PROT-021 threshold (14400s) so checkpoint
not required.

## Why this matters

USER vetting protocol (2026-06-26): any Wave 3 bounded-capacity anchor must
clear dual-store audit at >= 95% before promotion. Without this FULL landing,
all Wave 3 anchors stay blocked. This cell is the LOAD-BEARING gate for the
whole Wave 3 work program.

## Discriminator-must-survive-scale (USER 2026-06-26)

**Check option C (full-N preview in smoke):** Smoke already ran at 10 queries
(a non-trivial fraction of the 100-query full); the dual-store match
mechanism is exercised end-to-end at smoke. The discriminator (95% vs 90%
band) DOES scale with query count (more queries = finer match-rate
resolution + lower sample variance). Smoke gave 0.90; full will give the
production-scale match-rate measurement.
