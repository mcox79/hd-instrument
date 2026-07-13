# PRE-REG: PER-RELATION INFO-CEILING REFRAME (anchor_per_relation_info_ceiling_cskg_v1)

Cell: `experiments/exp_anchor_per_relation_info_ceiling_cskg_v1.py`
Anchor: `anchor_per_relation_info_ceiling_cskg_v1`
Author: exp_dev | Date: 2026-07-13 | Queue: overnight_queue (GPU) | Seeds: [7, 13]

## Purpose
Magnitude-VET lever #1. Re-run the CONFIRMED additive best-arm pipeline (identical split/fits/controls) and
separate WINNABLE (determined) relations from mathematically-UNWINNABLE (one-to-many) relations, instead of hiding
both in the 0.14 aggregate. Establishes WHERE the additive map-builder is already best-in-class.

## Prior-work check (substrate-KB concept query)
`bash tools/substrate_query.sh "per-relation info ceiling cardinality determined one-to-many oracle filtered MRR"`
-> top hit cosine=0.3145 is the WordNet/lexical token "determined" (ANTONYM_OF undetermined); NO prior arc-cell at
cosine>0.30. Substrate knows-nothing (foundational anchor). This per-relation reframe of the confirmed best-arm run
is genuinely novel analysis; not a rediscovery.

## Design (reuse, zero extra fits)
Imports `fit_and_score`, `build_heldout_entity_split_ac`, all arm names + bands from
`exp_anchor_compose_magnitude_opt_cskg_v1` UNCHANGED (identical fit behavior). Adds only:
- `compute_rel_cardinality`: tph[r] = mean valid tails per (head,rel) pair, from the filtered `all_true` set.
  tph IS the filtered-set size = the exact quantity that caps filtered-MRR-vs-all. THEORETICAL: tph~1 => additive
  centroid z[h]+w[r] IS the tail (winnable); tph high => centroid is a foreign point far from any specific tail,
  non-true entities outrank the held-out tail => capped even at oracle.
- `per_relation_eval` + `determined_split_eval`: stratify the ALREADY-COMPUTED per-query `arm_scores` by relation /
  by determined-mask. No new fits (only masked filtered-MRR calls).

## Cardinality cut (pre-registered)
Determined := tph <= CARD_THRESH=2.0; underdetermined := tph > 2.0. Robustness re-reported at {1.5, 2.0, 3.0}.

## PRE-REGISTERED "best-in-class on the determined subset" (ALL four; picked before the run)
1. determined best-arm (ANCHOR_PEEL_HARDNEG) pooled filtered-MRR >= DET_SOTA_NEAR=0.17 (in/near SOTA 0.18-0.22).
2. determined subset is material: determined_query_frac >= DET_FRAC_MIN=0.20.
3. near the winnable ceiling: PEELHN_det / ORACLE_HN_det >= DET_CEIL_FRAC_MIN=0.80.
4. underdetermined ORACLE-capped (drag is genuinely unwinnable): ORACLE_HN_underdet <= UNDERDET_ORACLE_CAP=0.13.
Verdict head `PER_RELATION_INFO_CEILING_REFRAME`; tag `BEST_IN_CLASS_ON_DETERMINED` iff all four; `DET_IN_SOTA_BAND`
iff PEELHN_det >= 0.18. Also decompose gap-to-SOTA: `unwinnable_gap_share` = underdetermined-mass share of the
(0.18 - aggregate) gap.

## GUARD FIX (the VET filed it)
Source verdict was `BROKEN_TEST_CONTROL_BEATS_POP` -- FALSE break: `BASELINE_POP` is structurally ~0 on held-out
entities (train-freq 0), so any control trivially "beats POP". This cell ports the self-test `pop_at_floor` semantics
to the FULL verdict: controls are governed vs the RANDOM arm-floor (scramble/peelscr/idshuf gates already do this);
POP is an at-floor SANITY (pop_at_floor: POP <= max(RANDOM,0.02)+eps) NOT a bar. `broken := not pop_at_floor`. The
old POP-based test is reported as `old_broken_via_pop` (transparency; does NOT gate).

## PASS / FAIL BANDS (envelope)
- PASS (headline): verdict `PER_RELATION_INFO_CEILING_REFRAME__BEST_IN_CLASS_ON_DETERMINED[...]` with all four
  determined conditions AND must-fails intact. Reports the WHERE-best-in-class answer.
- PARTIAL: `PER_RELATION_INFO_CEILING_REFRAME__PARTIAL_DETERMINED_<which-failed>` -- still a valid reframe; the
  sub-flags localize which condition missed (below-SOTA-near / not-material / below-ceiling-frac / underdet-not-capped).
- FAIL / INCONCLUSIVE (run untrustworthy): `INCONCLUSIVE_BASELINE_DID_NOT_REPRODUCE_v1` (|ANCHOR-0.1282|>0.02),
  `INCONCLUSIVE_ORACLE_UNDERFIT` (oracle not >=3x RANDOM), `BROKEN_POP_NOT_AT_FLOOR` (POP leaking = real confound),
  `BROKEN_MUST_FAIL_CONTROL_FIRED` (scramble/peelscr/idshuf leaked or <8 sigs), `INCONCLUSIVE_TOO_FEW_HELDOUT`.

## Must-fails (guard-fixed)
oracle_fires; scramble_controlled + peelscr_controlled (<=0.25*ANCHOR-margin-over-RANDOM); idshuf_collapses
(<=0.20*ANCHOR-margin); pop_at_floor; arms_differ (>=8 sigs); Gate-D reproduce ANCHOR within 0.02 of 0.1282.

## Self-test (PASS, MEASURED@data/exp_anchor_per_relation_info_ceiling_cskg_v1_selftest/metrics.json)
Planted MIXED arena (functional determined relations + spread one-to-many). Separation fires:
det_oracle=0.43195, multi_oracle=0.06572, sep=0.36623 (>=0.10). Guard-fix fires: old_broken_via_pop=True,
new_broken=False, pop_at_floor=True. All 4 validity-preflight ok; arms_differ; 40.6s.

## Compute architecture
class (b/c) MIXED (inherited): 4 additive fits = batched minibatch SGD (matmul-heavy; GPU-proven); per-relation
stratification reuses computed arm_scores (no extra fits). Storage SHARDED. device=auto (cuda on GPU host).

## Routing note (timeout)
Source `exp_anchor_compose_magnitude_opt_cskg_v1` ran this EXACT regime (k=24/ep=500/2 seeds/4 fits) on **cuda in
8399s** (MEASURED@source metrics: device=cuda, elapsed_s=8399.7). This cell adds only cheap masked-MRR overhead.
GPU-batching-mandatory (matmul SGD). timeout_s=14400 (1.5x margin over 8400 GPU source, cap). remote_cpu would risk
a timeout-kill (CPU multiples slower than the 2.3h GPU source) and violate GPU-batching discipline -> route GPU.

## progress_logging
print_flush_true (line-buffered stdout + per-seed / per-relation flush prints; heartbeat.jsonl per seed).
