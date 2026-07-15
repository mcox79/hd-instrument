# Pre-registration: JOINT_OPERATOR_CAPSTONE_SELECTIVE_READOUTS (v1)

Anchor: `joint_operator_capstone_selective_readouts_v1`
Cell: `experiments/exp_joint_operator_capstone_selective_readouts_v1.py`
Filed: 2026-07-15 (exp_dev). Arena/determinism reuse the VET-clean discovery/bilinear/transition arena.

## Question (WHAT)

Does ONE shared content code, read by TWO SELECTIVE readouts built from the TWO VET'd operators, solve BOTH
symmetric (PARITY) AND asymmetric (DOMINANCE) on NOVEL combos WITHOUT the cross-channel interference that left the
prior joint-dual at MIDDLE? This is the brain's one-code-two-readouts design (Bernardi/Fusi/Salzman 2020: one shared
mixed-selectivity population, different selective linear readouts extract different task variables).

## Prior arc (all MEASURED@disk; no re-hunt)

- SYM (LEARN_SYM), parity specialist: PARITY novel=0.9919; DOMINANCE=0.4768 (structural swap-invariance fails
  dominance). MEASURED@data/exp_interaction_bilinear_wall_break_v1/metrics.json (commit 29b53e63b).
- TRANSITION_OP, dominance specialist: DOMINANCE novel=1.0000, order-attributed (std-vs-shuffled gap=0.4222),
  HARD_PASS. MEASURED@data/exp_interaction_asymmetric_directed_operators_v1/metrics.json (commit 290400320).
- Joint-dual MIDDLE to beat: PARITY JD_CONFIG=0.8162 (rel_drop=0.1636 vs SYM_PROD 0.9758 -> over 0.15 tol, G5 fail);
  DOMINANCE JD_ORDER=1.0000. Interference lived on the PARITY channel via a lossy product-of-unbinds lens on a
  linearly-superposed bundle (its pure dual-head cost CFG_SOLO dualhead_drop was only 0.0288).
  MEASURED@data/exp_joint_dual_channel_readout_v1/metrics.json (commit 947d8c913).
- Rank drill: SYM rank-1-diagonal degrades with interaction rank (0.975->0.693); cheap CP-identity fix = learned
  rank-R (R in {2,4,8}), NOT blind expansion. CITED@notes/research_rank_vs_dimensionality_brain_check_2026-07-15.md
  (P_deflated 0.42).

## Mechanism (the joint code + two selective readouts)

Shared REAL content code `emb` (L=4, D=48). Both validated operators read that SAME emb through their OWN native
composition, trained JOINTLY on DIFFERENT targets:
- CONFIG readout (parity): `z_sym = prod_i emb[x_i]` (commutative product fold == LEARN_SYM). feats = [z_sym (linear,
  carries product SIGN = parity), rank-R CP quad terms (z_sym@A_r)(z_sym@B_r)] -> linear head. DESIGN-CRITICAL: a pure
  rank-R bilinear (quadratic) is sign-blind, so the LINEAR z_sym term is retained (it carries parity); the rank-R
  quad terms add higher-order symmetric capacity. Provably swap-invariant -> structurally cannot read dominance.
- ORDER readout (dominance): `s_i = (M_i @ s_{i-1}) * emb[x_i]` (TRANSITION chain; M init ~ I; at init s == z_sym
  EXACTLY) -> linear head. Non-commutative once M leaves I.
- Trained jointly: loss = CE(config_logits, y_parity) + CE(order_logits, y_dominance) + tiny L2 on M. The ONLY
  interference channel is the shared emb (both ops native/lossless -- no unbind lens, no superposition).

## Compute architecture

Class: (b) sequential-CPU with justification. Wall time is small (FULL 5 seeds ~2 min; smoke ~45s). Cell IS the
substrate-operator comparison (glass-box CPU, bit-reproducible), and each training is a tiny Adam fit (N~121 train,
D=48). No GPU batching gain worth the complexity at this scale. Storage: no_storage / no_composition-store (learned
readouts, not a KG store). No KGStore / substrate-index objects constructed (F.1-F.4 N/A; see below).

## Pre-registered bands (fixed BEFORE running)

All NOVEL CLEAN, multi-seed (5) mean. HARD_PASS = ALL of:
- G1 parity_solved:   JOINT_CONFIG(parity) >= 0.88                         (near SYM spec ~0.99; clears prior 0.816)
- G2 dom_solved:      JOINT_ORDER(dom) >= 0.90 AND (JOINT_ORDER - FREQ_dom) >= 0.10   (FREQ_dom ~0.778)
- G3 parity_no_interf: parity_rel_drop_vs_SYM_RANKR_SPEC <= 0.10           (BEATS prior joint-dual 0.164 / its 0.15 tol)
- G4 dom_no_interf:    dom_rel_drop_vs_TRANSITION_SPEC <= 0.10
- G5 config_headdisc:  HEADDISC_CONFIG_ON_DOM <= FREQ_dom + 0.07           (wrong readout fails dominance; structural)
- G6 order_headdisc:   HEADDISC_ORDER_ON_PAR  <= chance_p + 0.15           (wrong readout fails parity; MEASURED)
- G7 order_attributed: JOINT_ORDER - JOINT_ORDER_SHUF >= 0.20              (order non-commutativity load-bearing)
- G8 mustfails fire on BOTH readouts (arb_gap<=0.10 AND shuf_gap<=0.10, both channels); G9 oracle ceiling ok.

MIDDLE_BAND = both solved + head-disc clean + order attributed, but interference on EITHER channel in (0.10, 0.30]
  (both-solver still costs; joint-dual MIDDLE improved-not-beaten). Reported per-channel.

REFUTE = channel dead (JOINT_CONFIG(parity)<=0.60 OR JOINT_ORDER(dom)<=FREQ_dom) OR interference>0.30 either channel
  OR head-disc hard-fail (config_on_dom>FREQ_dom+0.15 OR order_on_par>chance_p+0.25) OR order not attributed
  (gap<0.05) OR mustfail breach.

Interference tol 0.10 (tighter than the prior cell's 0.15) is chosen to genuinely BEAT the prior MIDDLE: the prior
parity interference was 0.164, and its measured pure-dual-head cost was only 0.029, so native lossless readouts on a
shared code are expected well under 0.10. This is band-authority judgment documented here a priori.

## Ablations (REPORTED, NOT gating HARD_PASS)

- Rank-R sweep: config readout R in {1,2,4,8} on PARITY and on COUNT (# top-half bits, symmetric 5-class).
  rank_recovers_count = COUNT_acc(R=8) - COUNT_acc(R=1) >= 0.05. HONEST CAVEAT (pre-registered): this arena's
  symmetric targets are read off the product fold, where parity is a rank-1 sign and COUNT may also be rank-1-solvable
  by a linear head on z_sym -> the sweep may SATURATE (uninformative). The dedicated rank-degradation reproduction
  requires the drill's tunable-interaction-rank synthetic plant and is a SEPARATE operator-enrichment cell per the
  drill's own next-drill recommendation; it is NOT this capstone. A saturated sweep here is an honest
  "this-arena's-symmetric-targets-are-rank-1-readable" finding, consistent with SYM=0.99.
- Order-shuffle: JOINT_ORDER_SHUF (deranged slot order at TEST time) + TRANSITION_SPEC_SHUF must collapse dominance.

## SCHEMA-VET checklist

- cardinality_ok: true. EXPECTED_N_UNITS = len(REGIMES)=3 joint runs per seed; verdict sets cardinality_ok = (n_units
  == 3 * n_seeds).
- Per-unit failure-class: no bare except; outer try `except SystemExit: raise` / `except KeyboardInterrupt: raise` /
  `except Exception` -> CELL_CRASHED metrics + traceback + re-raise.
- Discriminator-fires (META_RULE_K): the discriminators are (a) interference gap joint-vs-specialist and (b) head-disc
  cross-probe accuracy; both are MEASURED at full arena-N in self-test (99 novel) and multi-seed in smoke. Not vacuous.
- Strictly-above-floor (META_RULE_L): HP_PARITY_FLOOR 0.88, HP_DOM_FLOOR 0.90; smoke parity 0.995 / dom 1.0 clear by
  wide margin (not band-floor-hugging).
- HP_SCOPE: G1/G3/G6 apply to CONFIG/parity + SYM spec; G2/G4/G5/G7 to ORDER/dominance + TRANS spec. Baselines
  (FREQ/POP/MEMO/ORACLE) inherit NO HARD_PASS gates.
- calibration_check: "default_ok_for_this_regime" -- EMB_D=48, EPOCHS=500, LR=0.05, TRANS_INIT_NOISE=0.05,
  TRANS_REG=1e-5 all inherited VERBATIM from the two landed operator cells (fairness/comparability), not tuned here.
- CRLB: crlb_n/a -- discriminator is a relative gap (joint-vs-specialist) + a linear-decodability probe, not a
  noise-floor detection; no Cramer-Rao noise floor applies. Capacity feasibility: FREQ_dom (0.778) not saturated
  (<0.85 self-test gate); parity chance ~0.52, dom chance ~0.62 -> discriminating band. Baseline-in-band verified.
- arms_differ_verified: true. STRICT set = the two JOINT readouts (cross-target, must differ). arms_differ_exempted:
  [(JOINT_ORDER, TRANSITION_SPEC), (JOINT_CONFIG, SYM_RANKR_SPEC)] -- a specialist legitimately equals the joint
  readout when the family is solved to the oracle (perfect dominance preds == gold == identical vectors).
- final_metrics_atomicity: "tmp_replace" (metrics.json.tmp -> os.replace).
- start_marker_written: true; crash_diagnostic_present: true; heartbeat_present: true (per seed); cell_chunked: false
  (5-seed loop in one cell; each seed is a tiny fast fit, single-cell acceptable at this scale).
- defensive_error_checking: "passed_all_4_patterns".
- real_code_path (F.1-F.4): N/A -- no KGStore / substrate-index / fit-module objects; the cell is self-contained torch
  (product fold + matmul chain) + a single `hdlab.binding.bind` call exercised in the self-test construction sanity
  (FHRR homomorphism). The self-test EXERCISES the real operator code paths (_product_fold, _transition_fold,
  _config_feats, _train_joint, _train_*_solo, _fit_linear_probe) at full arena-N. F.5 nondeterminism: STATIC SCAN
  clean (all seeds from integer indices + fixed torch.Generator / np.default_rng; no hash(), no list(set())).
- positive_control (Gate D): SYM_RANKR_SPEC reproduces parity specialist AND TRANSITION_SPEC reproduces dominance
  specialist AT THE TEST REGIME (self-test asserts sym_spec>=0.85, trans_spec>=0.90); interference is measured against
  these same-regime reproductions, not cross-cited prior atoms.

## Predicted outcome (HYPOTHESIZED@this prereg)

Self-test (single seed, 250 epochs, full arena-N) and 2-seed smoke both landed clean HARD_PASS: joint parity ~0.99
(>= specialist, negative interference), dominance 1.0 (zero interference), head-disc clean both directions
(config->dom ~0.49-0.55 vs FREQ_dom 0.77-0.86; order->par ~0.44-0.52 vs chance 0.52), order attributed (gap ~0.58),
must-fails fire. FULL 5-seed expected to confirm HARD_PASS. If interference on either channel drifts into (0.10,0.30]
at 5 seeds -> MIDDLE (still an improvement over the prior). Rank sweep expected to saturate (COUNT rank-1-solvable).
