# Prereg: substrate_md_chunk_config_sweep_E3_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Wave 3B TOP-2
**Drill source:** notes/research_drill_3x_wm_k_scaling_and_substrate_vs_md_2026-06-27.md (Gap 2 Extension E3)
**Stage:** Stage 3 (substrate-vs-MD calibration; pre-1M-atom-ingest config-choice)
**P_deflated:** 0.65 (standalone)

## HYPOTHESIS

Optimal chunk-config (chunk_size, overlap_fraction) for substrate content-chunk-KB exists in the sweep space chunk_size in {64, 128, 256, 512, 1024} tokens x overlap_fraction in {0.0, 0.25, 0.50}. At the best config, substrate-KB recall@5 on 50 held-out queries against the existing 152-file content-chunk KB matches or exceeds an MD-file-grep baseline. This informs Wave 4 v2 full ingest config BEFORE 1M-atom commit.

## ARMS (3 per config, 15 configs = 45 arms total)

For each of 15 (chunk_size, overlap) configs:
1. **ARM_SUBSTRATE_KB_QUERY** -- cosine-search over substrate-KB with this chunk-config (rebuilt locally over a synthetic corpus matched to substrate-content-chunk shape).
2. **ARM_MD_FILE_GREP_BASELINE** -- grep-based search over the source MD files; recall@5 over the same 50 queries.
3. **ARM_DIAG_RANDOM** -- random ranking; chance recall@5 (expect ~5/n_chunks).

## PRE-REG BANDS (LOCKED; PROSPECTIVE)

- **HARD_PASS**: At the Pareto-optimal config, ARM_SUBSTRATE_KB_QUERY recall@5 >= 0.70 AND (substrate recall@5) >= (MD baseline recall@5) AND ARM_DIAG_RANDOM recall@5 <= 0.20 (sanity).
- **MIDDLE_BAND**: substrate recall@5 in [0.50, 0.70] OR within 0.05 of MD baseline at best config.
- **HARD_FAIL**: NO config achieves substrate recall@5 >= 0.40 OR ALL configs underperform MD by >= 0.20 OR ARM_DIAG_RANDOM recall@5 >= 0.30 (chance floor too high = corpus too small).

## FAIRNESS GATES

- Same 50 query set across ALL configs (held-out from corpus indexing).
- Same N_DIM encoder dimensions across configs.
- Same scoring metric (recall@5 with hard ground-truth ranking).
- MD baseline uses simple grep + return top 5 by match-count; not pre-filtered or magically-augmented.
- Configs share the same source corpus (cell builds a synthetic corpus matched in shape to actual substrate-content-chunk source).

## CARDINALITY (META_RULE_H)

- EXPECTED_N_UNITS_FULL = 15 configs * 3 arms * 3 seeds * 50 queries = 6750
- EXPECTED_N_UNITS_SMOKE = 4 configs (smoke subset) * 3 arms * 2 seeds * 10 queries = 240

## DISCRIMINATOR-SURVIVES-SCALE

Smoke runs a 4-config subset (smallest + largest chunk_size at 0 and 0.50 overlap) to verify recall@5 monotone-or-Pareto behavior fires at smoke scale.

## HARDENING

L1 STARTED + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel.

## COMPUTE

CPU on remote_cpu; ~2 CPU-hr full; <15 min smoke. Forward-only numpy. char-trigram encoder in-cell.

## SUBSTRATE PREREQS

- char-trigram encoder (existing chain-grade primitive shape; reimplemented in-cell self-contained)
- Cosine-search over content-chunk atoms (existing substrate-KB v1/v2 primitive shape; in-cell)
- MD baseline via grep + match-count ranking (no external deps)
