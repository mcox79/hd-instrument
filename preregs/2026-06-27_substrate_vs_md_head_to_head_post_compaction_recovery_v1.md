# Pre-registration: substrate_vs_md_head_to_head_post_compaction_recovery_v1

**Date:** 2026-06-27
**Anchor:** substrate_vs_md_head_to_head_post_compaction_recovery_v1
**Queue:** remote_cpu_queue
**N:** n/a (no vector-dim production parameter; this is a tooling-comparison cell), **Seeds:** 1, **Param:** 20 queries x 4 buckets (A directive / B state / C mechanism / D gotcha)

## Scientific question

Does the substrate-KB (v2 content-chunk + continuous-ingest) outperform direct
Markdown file Read on the four operational axes that gate USER's MEMORY.md
POST-COMPACTION RITUAL switch from "Read BACKUP file directly" to "Query
substrate-KB FIRST"? Specifically, on a frozen 20-query post-compaction-recovery
corpus (5 each from directive/state/mechanism/gotcha buckets), does substrate
(1) return answers within 2x MD wall-clock, (2) return content matching ground-
truth at >= 0.95 macro Jaccard, (3) stay within 10 min of filesystem freshness,
and (4) degrade gracefully to filesystem-fallback under simulated KB partition
fault?

## Pre-registered bands

**HARD-PASS** (ALL four primary axes must hold AND no axis trips HARD-FAIL):
- ARM_LATENCY_HEAD_TO_HEAD: substrate median wall-clock <= 2.0x MD median over 20 queries
- ARM_CONTENT_COMPLETENESS: macro Jaccard(substrate-returned-content tokens, ground-truth-section tokens) >= 0.95 across 20 queries
- ARM_FRESHNESS_SAMPLE: max(FS_mtime - KB_ingest_ts) <= 10 minutes across 5 sample files (BACKUP 06-26, BACKUP 06-27, fleet_waiting_on, director_plan, CLAUDE.md)
- ARM_ROBUSTNESS_PARTITION_FAULT: filesystem-fallback returns correct answer in 100% of induced-fault arms (5 queries; >= 30% token-overlap with GT)

**MIDDLE:** any single primary axis falls into the MIDDLE band (between hp and hf thresholds) while other 3 hold; cell verdict MIDDLE_BAND. Per META_RULE_L: band-floor results are MIDDLE_BAND not HARD_PASS.

**HARD-FAIL** (any axis trips):
- substrate median latency > 5.0x MD median
- OR macro Jaccard < 0.70
- OR max freshness lag > 60 minutes
- OR fallback-success ratio < 0.80

## Calibration rationale

Latency 2.0x HP / 5.0x HF: USER will tolerate moderate slowdown if substrate is sufficiently useful but not a 5x+ penalty when MD Read is the actual workflow. The 2026-06-26 honest finding measured substrate v1 at ~38s vs MD at ~1s (~38x); v2 content-chunk needs to close most of that gap to be ritual-flip-worthy. 2x is generous given USER's "make substrate the definitive source" directive.

Content match 0.95 HP / 0.70 HF: Jaccard on lowercase alnum 2+ char tokens. 0.95 is strict (chunk-content must materially overlap the actual ground-truth paragraph) but the substrate's stated purpose is to return content, not pointers; if Jaccard < 0.7 the substrate fundamentally is not providing the content USER asked for and ritual flip would degrade recovery. The 0.70 HARD-FAIL is calibrated to "substrate returned at least 70% of relevant tokens, which is information rather than misinformation."

Freshness 10 min HP / 60 min HF: continuous-ingest scheduled task runs every 5 min; 10 min HP allows for one missed cycle. 60 min HF catches scheduled-task-dead failure modes (the 2026-06-26 known bug where MEMORY ingest stalled; this arm is the load-bearing canary for that class).

Robustness 1.0 HP / 0.80 HF: USER's recovery scenario MUST work even under partial KB corruption. If filesystem-fallback returns the right answer for >= 4 of 5 fault arms, the substrate is "sufficient if available, graceful if absent." Below 80% the fallback path itself is broken (this would be a substrate-system regression, not just a substrate-KB regression).

## N-suffix section

No _n<N> suffix on anchor; no PROT-018 binding required. Cell parameter is N_QUERIES=20 (or 5 in smoke) drawn from a frozen ground-truth corpus.

## Timeout estimate

Smoke wall expected ~120s (5 queries x ~12s substrate + ~1s MD + KB load 30s + selftests 10s).
FULL wall expected ~1500-2400s (20 queries x ~12s substrate + ~1s MD per arm x 4 arms with 2 substrate-arms + ARM 5 sample of 5 x ~12s + freshness + robustness fault arms ~60s).

formula: ceil(1.5 * 120 * (20/5)^1.0 * (1/1)) = 720s minimum from smoke scaling. Adding ARM 3+4+5 overhead and conservative buffer for KB-load variance on remote_cpu:

timeout_s = 3600 (1 hour; cell is mostly I/O + cosine queries; well under PROT-019 4h floor since no _n suffix triggers it).

## Anti-rigging discipline

Ground-truth sections were extracted by exp_dev at cell-author time (2026-06-27) from the frozen 2026-06-26 BACKUP file (and 7 memory directive files). SHA-256 hashes of each `ground_truth_text` are stored in `experiments/_ground_truth/substrate_vs_md_v1.jsonl` alongside the text. Cell re-verifies all 20 hashes at run time via `_selftest_antirigging`; any mismatch HALTS the cell with verdict UNKNOWN (BIAS-13 contamination defense per USER 2026-06-24 master checklist).

## Disciplines built into cell

- META_RULE_H: `cardinality_ok` field set true in summary only if `len(arm1.per_query) == n_queries_expected` AND `len(arm3.per_file) == 5`. Mismatch -> verdict UNKNOWN.
- META_RULE_J: no silent except. Any subprocess error in substrate path is appended to `halts` and surfaces as verdict UNKNOWN per `verdict_compute`.
- META_RULE_K: smoke variant fires the discriminator (substrate vs MD latency + content) not just verifies the cell runs.
- META_RULE_L: band-floor results are MIDDLE_BAND, not HARD_PASS.
- META_RULE_M (production-scale): ARM 5 SCALE_PROBE diagnostic surfaces scale degradation in verdict_msg even when primary arms HARD_PASS; if scale-probe degrades (latency > 2x ARM 1 OR jaccard < 70% ARM 2) the flag appears in verdict_msg as `ARM5_SCALE_DEGRADATION_FLAG` so USER ritual-flip review can incorporate it.
- BIAS-N (verify-the-referent): `_selftest_verify_referent` re-Reads each substrate-returned snippet's first-5-tokens probe across notes/+memory/ to confirm provenance.
- SCHEMA-VET 5b (per-arm HP scope): each primary arm has its own ok/hp_threshold/hf_threshold/hf_tripped fields; verdict logic does not collapse across arms.

## Decision tree on outcomes

- HARD_PASS (all 4 axes + ARM 5 OK): Director reports to USER and proposes MEMORY.md edit; auto_flip_disabled is True per drill Sec 9; USER reviews before flip.
- HARD_PASS (all 4 axes) + ARM 5 SCALE_DEGRADATION_FLAG: ritual-flip BLOCKED pending ARM 5 root-cause cell.
- MIDDLE_BAND: cap_map decision; identify failing axis; route remediation (e.g., freshness axis fail -> debug continuous-ingest cadence).
- HARD_FAIL: MD stays canonical; substrate-KB is not yet production-recovery-grade; defer ritual-flip indefinitely until v3.

USER directive: do NOT auto-flip MEMORY.md on HARD_PASS. Cell emits proposal, not action.
