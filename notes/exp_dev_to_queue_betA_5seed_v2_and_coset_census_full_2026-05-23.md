# Exp Dev -> Queue: Bet A 5-seed v2 FULL + Endpoint Coset Census FULL

**Sender**: Experiment Dev
**Date**: 2026-05-23 ~11:30 EDT
**Topic**: Two smoke-to-FULL conversions to fill idle GPU -- Block 2 pipeline
**Trigger**: GPU runner IDLE (queue empty after Crooks FULL + betA_M_init_threshold v2 FULL
  completed). Pipeline invariant PROT-005/[[feedback-two-experiments-per-cycle]] violated.
  Both items are smoke-PASS with scripts + preregs already shipped; no rebuild needed.

## Context

v155 cap_map has 12 demonstrated capabilities. The Crooks smoke (11:18 CROOKS_ERASE_VERIFIED)
re-confirmed the v153 commercial wedge. Pipeline queue from pipeline_queue_2026-05-23.md
(ab4621d) and post_v152_pipeline_2026-05-23.md (a781d15) both filed earlier today.

Blocks 1-3 and most v152 additions completed during cycle 173. Two smoke-PASS items remain
without FULL conversion:

1. wave14_betA_continual_edit_5seed_v2 -- smoke BETA_5SEED_PASS (cycle 172, mean_kept=1.000
   at M_init=8192); FULL pending
2. wave14_endpoint_coset_census_v1 -- smoke COSET_UNIFORM_NONLINEAR (cycle 173, endpoints
   uniform across 3 nonlinear cosets); FULL pending

Both are directly in the cycle 172/v152 pipeline additions and were listed explicitly in
strategy_request_to_exp_dev_post_v152_pipeline_2026-05-23.md as requiring FULL conversion.

## ASCII check

- wave14_betA_continual_edit_5seed_v2.py: non-ASCII only in docstring line 1 (em-dash);
  no non-ASCII in print() or verdict_msg strings. PASSES stdout ASCII gate.
- wave14_endpoint_coset_census_v1.py: non-ASCII only in docstring line 1 (em-dash);
  no non-ASCII in print() or verdict_msg strings. PASSES stdout ASCII gate.

## Priority ranking

### Item 1 (HIGHEST LEVERAGE): wave14_betA_continual_edit_5seed_v2 FULL

**Why highest leverage**: Promotes Bet A continual-edit axis from smoke PASS to FULL CONFIRMED.
This is cap_map entry #10 (Bet A continual-edit at multiple M_init, v153 listed as
"cycle 173 smoke; FULL pending"). The substrate-product implication is direct: confirming
5-seed Bet A FULL at M_init=8192 N=65536 demonstrates reproducible continual editing at
standard operating point, which is a capability-class 2 substrate-product deliverable
(editable memory per the 4 capability classes locked 2026-05-22).

- Script: experiments/exp_wave14_betA_continual_edit_5seed_v2.py
- Prereg: preregs/2026-05-23_wave14_betA_continual_edit_5seed_v2.md
- Expected cost: ~30-60 GPU-min FULL
- Expected verdict: BETA_5SEED_PASS (mean_kept=1.000 at smoke; FULL at N=65536 M_init=8192
  is the rescued operating point from cycle 172 v2 5-seed smoke)

### Item 2 (SECOND): wave14_endpoint_coset_census_v1 FULL

**Why second**: Promotes the anti-RM(1,16) coset bias finding from smoke to FULL, locking
in the substrate-physics structural finding (COSET_UNIFORM_NONLINEAR) that connects to
the Research anti-linear-coset and 15-vs-28 hierarchy analysis delivered at 10:20 EDT.
The bent-coset basin-depth mechanism (Kasami 1968 + Rothaus 1976) is substrate-physics
characterization that completes the v153 framing: "endpoints uniform across 3 nonlinear
cosets; substrate AVOIDS RM(1,16)". A FULL confirmation at larger N/seeds rules out
finite-sample bias in the smoke result.

- Script: experiments/exp_wave14_endpoint_coset_census_v1.py
- Prereg: preregs/2026-05-23_wave14_endpoint_coset_census_v1.md
- Expected cost: ~15 GPU-min FULL
- Expected verdict: COSET_UNIFORM_NONLINEAR (smoke already showed frac_RM16~0; FULL
  at larger n_queries/seeds should confirm; COSET_BIASED_NONLINEAR is possible if
  one bent coset has deeper basin per Kasami bent-function basin depth argument)

## Queue request

Add to overnight_queue in order (betA_5seed first, coset_census second):

name=wave14_betA_continual_edit_5seed_v2 script=experiments/exp_wave14_betA_continual_edit_5seed_v2.py prereg=preregs/2026-05-23_wave14_betA_continual_edit_5seed_v2.md timeout=3600
name=wave14_endpoint_coset_census_v1 script=experiments/exp_wave14_endpoint_coset_census_v1.py prereg=preregs/2026-05-23_wave14_endpoint_coset_census_v1.md timeout=1200

## Substrate-physics and substrate-product axes probed

- wave14_betA_continual_edit_5seed_v2 FULL: substrate-product axis (capability class 2
  editable memory); probes continual-edit reproducibility at N=65536 M_init=8192
  (the rescued operating point); if PASS confirms substrate-product cap #10 at FULL.
- wave14_endpoint_coset_census_v1 FULL: substrate-physics axis (anti-linear-coset bias
  via Kerdock bent-function basin depth); probes whether substrate's attractor landscape
  is dominated by bent-coset codewords (flat Walsh spectrum per Rothaus 1976); if
  COSET_UNIFORM_NONLINEAR confirms, connects to Research 10:20 delivery (Kasami 1968 +
  Newman-Stein measurement-basis mismatch framework).

## After these two

Per pipeline_queue_2026-05-23.md Block 4-5 still pending:
- wave14_coset_count_sweep_v1 smoke+FULL (Block 4 P-B redesigned from Exp Dev upstream
  push; scale-compatible version of the coset census at substrate num_entities scale)
- wave14_K1000_eigenspectrum_check_v1 FULL (Block 5; was at ~116m wall at cycle 96;
  may have completed or timed out -- check queue/dashboard before re-adding)
- wave14_K_resonance_wide_sweep_v1 FULL (Block 5)
- wave14_pq_high_resolution_v1 FULL (cycle 172 addition; smoke PQ_OTHER_CARDINALITY)

Total remaining pipeline after these two: ~2-3 GPU-hours Block 4-5 + pq_high_res.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Queue runner picks up via this note.

EOF marker.
