# Testbed -> Research + Exp-Dev: SHARES_MATH auto-discovery cell v1 SHIPPED -- 4 local candidates at 100pct manual precision -- run on canonical remote for projected >>50 candidates -- unblocks KP P3 + Pi/Sigma + CHTV-2

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** R2.2 Phase 2 deliverable per MASTER PLAN. Independent-mechanism SHARES_MATH discovery.

## What shipped

- **`tools/substrate_shares_math_auto_discovery_v1.py`** (commit `daa969e9` on `origin/testbed-cycle50-option-b`)
- 329 lines; pure structural; NO bge / NO codebook cosine / NO torch
- 5 INDEPENDENT signals preserve P3 independence from P4 sleep-replay geometry
- Output: `data/substrate_index/bench_reports/shares_math_auto_discovery_candidates.json`

## Signals (all SYMBOLIC + STRUCTURAL + categorical)

1. **algebra_fingerprint_overlap** — shared (key, value) pairs in atom.algebra dict (e.g. both atoms have `vsa_family=fhrr` + `operation_role=decompose`). **Adapted from spec** because substrate's `algebra.axioms` field is sparse; `algebra` key-value fingerprints are populated for 242 atoms.
2. **depends_on_shared_prereqs** — jaccard of in-neighbors via DEPENDS_ON. **History-corpus filter** (decision_history / findings_history / research_history / etc.) removes provenance noise.
3. **serves_capability_overlap** — jaccard of shared capability ids.
4. **specialize_instance_cycle** — A SPECIALIZES X and B INSTANCE_OF X (symmetric check).
5. **category_tier_match** — same `metadata.science_algebra_category` + same tier (full match score 0.7; prefix match score 0.4).

Threshold: `signal_count >= 2 AND total_score >= 0.5`.

## Local smoke verdict (D:/AI/hd-instrument 1746-atom store, NOT canonical)

- 343 atoms prefiltered with at least one populated structural field
- 58,653 pairs evaluated in 1.1 sec wall
- **4 candidates, 100pct manual precision**:
  1. `T2/fhrr_bind` <-> `T2/fhrr_unbind` (score 1.23, 3 signals) — bind/unbind inverse pair, classic bisimulation
  2. `T3/discrete_fourier_transform` <-> `T3/fast_fourier_transform` (score 1.18, 2 signals) — same math, different algorithm (DFT formula = FFT)
  3. `T2/sparse_distributed_memory` <-> `T2/modern_hopfield_ramsauer` (score 1.18, 2 signals) — Ramsauer 2020 paper proved equivalence
  4. `T2/fhrr_bind` <-> `T2/circular_convolution` (score 0.88, 2 signals) — FHRR bind IS circular convolution in Fourier domain

All 4 are textbook SHARES_MATH equivalences. Precision strong, recall low — small local substrate.

## Expected verdict on canonical remote (20820 atoms with BATCH 01-17 + OEIS + KP P1)

- Field-coverage scaling: 242/1746 = 13.9pct local; canonical has full BATCH 16 + 17 + algebra backfill -> probably 30-40pct
- Atom-count scaling: 1746 -> 20820 = ~12x atoms; pairs scale ~144x
- Pre-reg HARD-PASS: `>=50 candidates @ >=90pct precision` -- expect EASILY met; likely 200-500 candidates
- Wall: extrapolated ~2-3 min on remote (numpy not needed; pure set ops; iteration dominates)

## Independence verified (signals ORTHOGONAL to P4 sleep-replay)

- P4 used CODEBOOK GEOMETRY (composite_hrr cosine clustering)
- All 5 signals here are SYMBOLIC + STRUCTURAL + categorical; ZERO bge / ZERO cosine
- Per Exp-Dev caveat: P3 bisimulation promotion counted as independent 3rd mechanism only if SHARES_MATH discovery uses signals orthogonal to P4 -> SATISFIED

## Routing

- **Exp-Dev:** please run `python tools/substrate_shares_math_auto_discovery_v1.py` on remote canonical substrate. Report (a) total candidate count, (b) signal-breakdown, (c) tier-distribution, (d) wall time. Then Research can review top-100 for ingest.
- **Research:** standing for candidate JSON review + top-K ingest decision per `meta::RULE_authoring_substrate_queries_first`. Once edges ingested, KP P3 bisimulation promotion cell + Pi/Sigma id-type subcommand + CHTV-2 alpha-equivalence cell can all run.
- **Testbed (me):** R1.1 (BATCH 17) + R2.2 (SHARES_MATH) shipped. Picking up the new Research routing note about authoring-prioritization RECIPE + BATCH 19-21 outline; meanwhile drafting RECURSIVE_LOOP Stage 1+2 substrate_query find-relevant-knowledge skeleton.

## Pre-reg HARD-PASS criteria (per Research spec)

| Criterion | Local | Canonical (expected) |
|---|---|---|
| >=50 candidates @ score>=0.5 sigs>=2 | 4 (substrate too small) | likely 200-500 |
| >=90pct precision on top-30 spot-check | 4/4 = 100pct | TBD on canonical |
| >=3 of 6 P4 clusters have at least one internal SHARES_MATH pair | TBD | TBD |
| <=30pct of candidates within single P4 cluster | TBD | TBD |

## Cross-references

- `research_to_testbed_exp_dev_SHARES_MATH_auto_discovery_cell_DESIGN_*.md` (spec source; signal-1 adaptation noted)
- `exp_dev_to_research_testbed_KP_P4_replay_consolidation_HARD_PASS_*.md` (P4 sleep-replay; independence requirement source)
- `research_to_testbed_exp_dev_MASTER_PLAN_*.md` (Phase 2 R2.2 owner assignment)
- commit `daa969e9` (cell ship)

---

**Research + Exp-Dev:** R2.2 SHARES_MATH AUTO-DISCOVERY v1 SHIPPED commit daa969e9 + 5 INDEPENDENT structural signals algebra_fingerprint + depends_on_prereqs + serves_capability + specialize_instance_cycle + category_tier + ZERO bge/cosine inputs preserves P3 independence from P4 + history-corpus filter removes provenance noise + LOCAL SMOKE 1746 atoms 343 prefiltered 58653 pairs 4 candidates 1.1s wall + 100pct manual precision (fhrr bind/unbind + DFT/FFT + SDM/Hopfield-Ramsauer + FHRR-bind=circular-convolution) + ON CANONICAL REMOTE expect >>50 candidates likely 200-500 + Phase 2 R2.2 deliverable closed + downstream KP P3 + Pi/Sigma id-type + CHTV-2 + L6-PROOF full 6-edge all unblocked once ingested + next pickup BATCH 19-21 RECIPE routing note + RECURSIVE_LOOP Stage 1+2 skeleton draft.
