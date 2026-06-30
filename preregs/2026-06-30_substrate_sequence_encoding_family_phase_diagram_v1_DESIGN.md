# Design pre-reg: substrate_sequence_encoding_family_phase_diagram_v1

**Date:** 2026-06-30
**Author:** exp_dev (Opus 4.7 1M, agent-spawn, outer-axis fill)
**STATUS:** DESIGN-ONLY — cell not yet authored. Filed for follow-up exp_dev spawn.

**USER directive (2026-06-30 ~17:35 UTC):** Phase-diagram outer-axis fill —
cell #1 of 4. Substrate uses positional-shift sequence encoding EVERYWHERE;
alternatives untested. K-cliff is Stage 1 chain-grade primitive — cleanest
place to discriminate sequence_encoding axis.

## Reason for DESIGN-ONLY status

Within the same exp_dev spawn budget I authored + smoked cell #3 (update_rule
family) and fixed cell #4 (routing_geometry). Cells #1 and #2 each require
non-trivial new sequence-encoding / binding primitives (~600 lines core each).
Filing as designs to seed follow-up authorship cleanly.

## Outer axis (proposed; LOCKED at module init at author-time)

4 sequence encoding families:
1. **`positional_shift`** -- substrate default. Position k -> shift vector by
   k positions (cyclic shift in HD). The chain-grade default; POSITIVE CONTROL.
2. **`permutation_based`** -- Position k -> apply seeded permutation^k to the
   item vector. Equivalent to shift but with non-cyclic structure; tests
   whether substrate behavior is shift-specific or permutation-invariant.
3. **`time_cell`** -- biological time-cell encoding: position k -> Gaussian
   bump centered at k in a 1D "time codebook" of size K_max; item bound
   with bump vector via outer-product. Mimics hippocampal time cells (Pastalkova
   et al. 2008; Eichenbaum 2014).
4. **`gated_lstm_like`** -- LSTM-flavored: position k -> learned gate vector
   (offline supervised: principal directions from K random LSTM states at
   position k). Tests whether learned position encoding beats random ones.

## Inner axis (proposed)

K-sweep (sequence length): `{50, 100, 200, 400, 800}` (5 K values)
- FULL: N=8192; 5 K values
- SMOKE: N=2048; 3 K values (50, 200, 800)
- Per K: bind K item-position pairs into one composite; query at random
  position; recall the item at that position.

CARDINALITY:
- FULL: 4 encodings * 5 K = 20 phase points per seed
- SMOKE: 4 encodings * 3 K = 12 phase points per seed

## Discriminator (load-bearing)

Per (encoding, K): `recall_at_pos` = mean(pred_item == true_item) over N_PROBE
position queries. K_cliff localization per encoding.

Cell-level chain-grade: any 2 encodings differ in K_cliff by >= 0.3 log2 K.

## Bands

- HARD_PASS (per-point): recall >= 0.90
- MIDDLE_BAND: 0.30 <= recall < 0.90
- FLOOR: recall <= 0.10
- SATURATED: recall >= 0.999

## Smoke discriminator-survives-scale plan

Smoke at N=2048; verify all 4 encodings produce DIFFERENT K_cliffs at smoke.
If 3+ encodings collapse to identical K_cliff at smoke (within 0.1 log2), the
mechanism family is degenerate — abort full dispatch and re-spec.

## Dispatch plan (when authored)

- **Destination:** `overnight_queue` (GPU; batched binding/encoding is GPU-amenable)
- **Seeds:** 7, 13, 19 (3-seed chunked)
- **Timeout:** ~7200s per seed (estimate; refine after smoke)
- Helper modules SCP to remote before queue_add

## Hand-off

Author should fork from `experiments/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_7.py` (MIDDLE_BAND landed 2026-06-28) which already implements positional_shift + K-sweep + 3-arm cardinality. Add the 3 new encodings as additional arms; refactor for 4-encoding outer axis with arms (SUBSTRATE_<encoding>) per family.

## Cell-template mandates (apply at author time)

- ASCII-only; META_RULE_AE constants LOCKED; META_RULE_AF arms-differ;
  META_RULE_AH atomic metrics; META_RULE_H cardinality_ok; except SystemExit
  ordering; start_marker / crash-diag / per-unit ckpt / heartbeat.
