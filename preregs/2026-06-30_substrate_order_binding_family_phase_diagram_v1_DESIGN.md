# Design pre-reg: substrate_order_binding_family_phase_diagram_v1

**Date:** 2026-06-30
**Author:** exp_dev (Opus 4.7 1M, agent-spawn, outer-axis fill)
**STATUS:** DESIGN-ONLY — cell not yet authored. Filed for follow-up exp_dev spawn.

**USER directive (2026-06-30 ~17:35 UTC):** Phase-diagram outer-axis fill —
cell #2 of 4. Currently substrate uses circular-convolution HRR binding for
order; permutation untested. Substrate's order primitive — if permutation
dominates, substantial finding.

## Reason for DESIGN-ONLY status

Same as cell #1: scope ceiling for one spawn. Filing as design for follow-up
author to pick up cleanly.

## Outer axis (proposed; LOCKED at module init at author-time)

4 order binding families:
1. **`circular_convolution_hrr`** -- HRR default: order = X *circ* Y where
   *circ* is cyclic convolution. POSITIVE CONTROL (the substrate default).
2. **`permutation`** -- Order = perm_left(X) elementwise* perm_right(Y) where
   perm is a fixed seeded permutation. Tests whether the order information
   needs full cyclic structure or only bijective shuffle.
3. **`phase_rotation`** -- FHRR-style: order = X * exp(i * theta_k) (complex
   bipolar; or equivalently HD vectors rotated by position-dependent angle).
   Tests phase-coded order (biologically motivated; phase-precession).
4. **`learned_position_outer`** -- order = outer(X, P_k) where P_k is a
   position-specific vector; bind via averaging over outer. Tests product-style
   order vs convolution-style.

## Inner axis (proposed)

K-sweep (sequence/binding length): `{20, 50, 100, 200, 500}` (5 K values)
- FULL: N=8192
- SMOKE: N=2048; 3 K values
- Per K: bind K (item, order) pairs; query at random k; recall item at order k.

CARDINALITY:
- FULL: 4 bindings * 5 K = 20 phase points per seed
- SMOKE: 4 bindings * 3 K = 12 phase points per seed

## Discriminator (load-bearing)

Per (binding, K): `unbind_acc` = mean(unbind_K_th(composite, position_k) ==
item_k). K_cliff localization per binding family.

Cell-level chain-grade: any 2 bindings differ in K_cliff by >= 0.3 log2 K
OR any binding achieves >= 0.05 absolute recall lift over HRR baseline at
any K.

## Bands

- HARD_PASS: unbind_acc >= 0.90
- MIDDLE_BAND: 0.30 <= unbind_acc < 0.90
- FLOOR: unbind_acc <= 1/V (V=codebook-size; effectively 0)
- SATURATED: unbind_acc >= 0.999

## Smoke discriminator-survives-scale plan

Smoke at N=2048, K in {20, 100, 500}; verify all 4 bindings produce
DIFFERENT K_cliffs. HRR (positive control) should hit K_cliff between K=100-200
at N=2048 (cited from prior cells); other bindings should ideally show
different K_cliff localization. If 4/4 collapse to identical cliffs at smoke,
the family is degenerate — abort.

## Dispatch plan (when authored)

- **Destination:** `overnight_queue` (GPU; HRR involves FFT; complex
  arithmetic for phase-rotation; both GPU-amenable)
- **Seeds:** 7, 13, 19
- **Timeout:** ~7200s per seed
- Helper modules SCP to remote before queue_add

## Hand-off

Author should fork from `experiments/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_7.py` for the K-sweep harness and the 4-arm structure, but the binding primitives need fresh implementation per family. HRR primitives exist in `hdlab/` (cite specific module on author).

## Reference primitives needed

- HRR cyclic convolution: `hdlab.binding.hrr_bind` (likely)
- Bipolar permutation: `numpy.random.RandomState.permutation` + apply across axis
- FHRR phase rotation: complex64 multiplication `vec * exp(1j * theta)`
- Learned position outer: simple `torch.outer(item, pos_vec)` -> projected to N
- Unbind: per-family inverse (HRR circ-correl / permutation inverse / phase
  conjugate / outer-trace).

## Cell-template mandates (apply at author time)

- ASCII-only; META_RULE_AE / AF / AH / H; except SystemExit ordering;
  start_marker / crash-diag / per-unit ckpt / heartbeat; arms-must-differ
  via per-binding W-hash; positive-control gate; CARDINALITY_OK mandatory.
