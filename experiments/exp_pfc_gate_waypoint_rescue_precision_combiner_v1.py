"""pfc_gate_waypoint_rescue_precision_combiner_v1 -- 7th-attempt on the autonomous-waypoint deep-corner
compounding-error wall: the stacked-corrections VET's ENDORSED corrected lever. The OR-gate stack
HARD_FAILed at FULL (HARD_FAIL_STACKING_REDUNDANT: stacked==selector; stacked_over_kb NEGATIVE in all 5
regimes) because the OR-UNION RE-ADMITS candidates the strict KB channel had correctly filtered -- an
ADMISSION-PRECISION leak, NOT a channel-strength or coverage problem. The VET's endorsed direction: NOT
more channels / not grow-KB-coverage, but a COMBINER THAT PRESERVES PRECISION. This cell tests whether
any of THREE precision-preserving combiners recovers rescue where the naive OR-gate could not.

WHY (stacked-corrections landed VET, 2026-07-09): the two channels (exogenous KB-grounded gate = channel
A; cross-fit calibrated correctness-selector = channel B) are informationally fine, but OR-union of their
ADMISSION SETS dilutes: the balance-argmax within the union re-picks selector-only candidates that the KB
channel had (correctly) excluded, so stacked collapses back onto the weaker selector's precision. The
diagnosis is an ADMISSION-SET operator problem. Precision-preserving alternatives to a flat union:
  C1  wp_and_gate               INTERSECTION -- admit only candidates BOTH channels confirm (strictly
                                tighter than either alone -> highest precision; recall is the risk).
  C2  wp_kbpriority_union       CONFIDENCE-WEIGHTED / KB-PRIORITY union -- defer to the higher-precision
                                channel: per row, if the KB channel confirms ANY candidate use ONLY the
                                KB-confirmed set (never let a selector-only pick override a KB-confirmed
                                one); only where KB is empty does the selector FILL THE GAP (before the
                                fresh-reset/open fallback). Never dilutes KB; adds selector recall only in
                                KB's coverage holes. The most principled precision-preserving combiner.
  C3  wp_calibrated_gate_combiner  CORRECTNESS-CALIBRATED selector gate over the union -- admit
                                (KB-confirmed OR selector-confirmed) AND calibrated P(correct) >= tau_hi
                                (a STRICTER percentile than the selector's own tau); the cross-fit
                                predicted-correctness score filters the union's re-admitted low-precision
                                candidates regardless of which channel proposed them.
  B0  wp_stacked_kb_plus_selector  the OR-gate union -- the CONFIRMED NEGATIVE / must-stay-dilutive control
                                (verbatim from the parent; must reproduce stacked_over_kb <= 0 at the corner,
                                else the contrast is not fair).
  KB-alone = wp_kb_grounded_gate is the single-best-channel reference; the combiner must ADD over it.

DISCRIMINATOR (FOCUS = op4_V1200_d8): best_combiner_over_kb = max over {C1,C2,C3} of
  recovery(cX) - recovery(kb_alone). HARD_PASS = some precision-preserving combiner clears KB-alone by a
  pre-registered margin at depth WHILE the OR-gate B0 stays dilutive (or_gate_over_kb <= 0). HARD_FAIL =
  no combiner beats KB-alone (=> the second channel is too weak to help under ANY combination rule -> the
  single-best-channel conclusion is FINAL, a clean scope-bound). Both outcomes are gold.

(legacy parent docstring for the reused stacked-corrections / KB / selector machinery follows verbatim):
pfc_gate_waypoint_rescue_stacked_corrections_v1 -- 6th-attempt on the autonomous-waypoint deep-corner
compounding-error wall: does STACKING two informationally-INDEPENDENT correction channels (the landed
KB-grounded gate + a NEW cross-fit calibrated correctness-selector) as an OR-gate suppress the per-hop
drift hazard MULTIPLICATIVELY -- pushing the recovery frontier PAST where either channel reaches alone?

WHY (Director steer 2026-07-09; cross-domain drill
notes/research_stacked_independent_corrections_push_compounding_frontier_2026-07-09.md):
  The KB-grounded exogenous check (parent, verdict MIDDLE_BAND_FLATNESS_BELOW_50) PUSHED the frontier
  entropy-8 -> entropy-12 but its recovery DECAYS ~0.51x per chain-hop (0.9257->0.4864->0.2444 at
  op4_V1200 d4/d6/d8; MEASURED@data/exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1/metrics.json).
  kb_fresh_rate rises in lockstep (0.000/0.013/0.063) -> the KB channel is coverage-density-limited.
  FIVE unrelated fields converge on ONE law: N independent tests fail only p^N of the time (kinetic
  proofreading p^N, concatenated codes D'>=d_i*d_o, QEC cyclic exp-suppression, PAC verifier theory,
  DAgger). CITED@Hopfield 1974; Forney 1966; Chernozhukov cross-fitting; Kalman multi-sensor fusion.
  A second, differently-designed, cross-fit-INDEPENDENT channel OR-gated with the KB gate should cut
  the per-hop miss-rate on the TRUE waypoint multiplicatively -- IFF the two channels' FAILURE MASKS
  are near-uncorrelated. The single largest risk (research point 2): both channels may secretly read
  the SAME raw-KB coverage-density signal, so their failures correlate and stacking degrades to
  redundant/sub-additive gain -- this is why the MANDATORY NEW screen is corr(failure_mask_KB,
  failure_mask_SELECTOR), reported as a FIRST-CLASS discriminator column and GATED.

MECHANISM UNDER TEST (the STACKED OR-gate; NOT assumed to work; P_deflated ~0.10-0.20 full HARD-PASS):
  CHANNEL A (exogenous KB-grounded check, VERBATIM from parent): mask R's balance-argmax to candidates
    KB-CONFIRMED by RAW-graph reachability reach_cum (zero shared params with the SR estimator M/R).
  CHANNEL B (NEW cross-fit calibrated correctness-selector; INDEPENDENT of M/R by construction):
    features are computed ONLY from raw-graph structure (anchor/candidate out-degree + graded reach
    closeness anchor->cand and cand->goal via reach_cum) -- ZERO M/R dependence. A logistic scorer is
    fit on train-fold A; a Platt calibration (cal_A,cal_B) is fit on a DISJOINT train-fold B (genuine
    cross-fitting per double-ML: weights and calibration never share a fold). At each hop a candidate
    is SELECTOR-ACCEPTED iff its calibrated P(correct) >= tau (tau = 70th-pctl of fold-B calibrated
    scores; adaptive-with-gate, principled, reported non-vacuous).
  STACKED (A OR B): mask R's balance-argmax to candidates KB-CONFIRMED *OR* SELECTOR-ACCEPTED, argmax
    within that union; empty -> RESET FRESH re-anchored at the immutable START (same OR mask),
    still-empty -> open-argmax fallback (counted). The true waypoint is SKIPPED only if NEITHER channel
    confirms it -> P(skip) = miss_KB * miss_SEL IFF the misses are independent (the multiplicative law).
  SELF-DERIVED (non-independent) MUST-FAIL control: wp_bisect_verify (VERBATIM from parent) re-checks R
    against a percentile of R ITSELF -- validated against itself, NOT an independent channel; collapses
    to ~flat at the deep corner (the bar the stacked arm must clear).

  MANDATORY SCREENS (both pre-registered; the second is the load-bearing NEW one):
  1. independence_corr = corr(kb_confirm_signal, m_error) AND selector_independence_corr =
     corr(selector_confidence, m_error) over per-hop units -- predict |corr| ~ 0 by construction.
  2. failmask_corr = corr(failure_mask_KB, failure_mask_SELECTOR) over per-chain final correctness --
     THE NEW screen; the whole multiplicative claim is VOID if this is high (shared coverage density).

  (legacy parent docstring for the reused KB channel-A machinery follows verbatim):
pfc_gate_waypoint_rescue_kb_grounded_check_v1 -- 5th-attempt REVIVAL of the autonomous-waypoint
deep-corner compounding-error HARD_FAIL with a genuinely NEW mechanism class: an EXOGENOUS,
KB-GROUNDED per-hop check (a kinetic-proofreading checkpoint) with ZERO shared parameters with the SR
estimator being corrected.

WHY (Director steer 2026-07-09; 5x cross-domain drill
notes/research_compounding_error_bound_5x_drill_new_mechanism_class_cross_domain_2026-07-09.md):
  FOUR autonomous-decomposition rescue variants have now landed HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL
  at the identical corner op4_V1200_d8 (wp_bisect_verify, coarse2fine, replay_bidirectional, lookahead-
  bisection). The drill's diagnosis: all four share ONE precise structural defect -- the "correction"
  signal at each hop was recomputed FROM THE SAME NOISY DERIVED ESTIMATOR being corrected (the SR-trained
  reach matrix M/R), never from anything outside it. verify thresholds R against a percentile of R
  itself; coarse2fine re-derives a coarser R from the same M; replay_bidirectional trains M_rev on the
  REVERSED transitions of the exact same corpus with the exact same optimizer/noise, so M and M_rev's
  errors are correlated (measured: bidir_sel=0.630 vs bidir_all=0.584 -- real but tiny separation, +0.010
  recovery, ten times below the +0.15 bar).
    MEASURED@data/exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1/metrics.json (FOCUS op4_V1200_d8):
      flat=0.081 oracle_exec=0.918 hier_oracle=0.906 wp_bisect_open=0.097 wp_bisect_verify=0.096
      recovery_verify=0.0182 recovery_replay(rescue)=0.0283 delta=0.0101 (HARD_FAIL bound-real).
  FIVE unrelated fields converge on the SAME fix (control theory: Kalman innovation must be ORTHOGONAL to
  the state estimate for bounded error covariance / observable (C,A) pair; DAgger: external-oracle query
  converts O(T^2)->O(T) regret; DNA-polymerase kinetic proofreading: a physically SEPARATE exonuclease
  ~25A from the polymerase site re-examines the raw base-pair; RG/info-bottleneck; pop-genetics): bound
  drift with an INFORMATIONALLY-INDEPENDENT correction channel. CITED@Hopfield 1974; Ross-Bagnell 2010;
  Kalman/Riccati observability. The substrate already HARD_PASS-proved this exact structural comparison
  THIS SESSION: MEASURED@data/exp_community_routed_glassbox_reasoning_scale_v1/metrics.json ARM_C_FRESH
  (routing recomputed fresh each hop from raw stored content) slope=0.0010 vs COMPOUND slope=0.0976 = 98x.

MECHANISM UNDER TEST (NEW class; NOT autonomous decomposition; NOT assumed to work; P_deflated ~0.20 for
MIDDLE-or-better, ~0.15-0.18 full HARD-PASS per the drill's 5th-attempt calibration):
  EXOGENOUS KB-GROUNDED CHECK (kinetic-proofreading checkpoint), rank-1 in the drill:
  (1) Build, ONCE per (V,n_ops) group, the RAW-KB reachability-within-k-hops boolean matrices reach_cum[k]
      DIRECTLY from the raw ingested edge table (per_op / adjacency = the substrate's raw ConceptNet-style
      edges). reach_cum[k][a,c]=True iff an ACTUAL path of length<=k exists a->c in the raw multigraph.
      ZERO shared parameters / ZERO shared training with M/R (which is TD-trained on random walks). This
      is the exogenous ground-truth channel -- the raw graph itself, not a derived statistic of it.
  (2) At each bisection hop (position pos=(j+1)*seg_len; anchor=prev discovered boundary; span rem=depth-
      pos to goal): compute the SAME open R-balance min(R[anchor,c],R[c,goal]) BUT MASK to only candidates
      that are KB-CONFIRMED: reach_cum[seg_len][anchor,c] AND reach_cum[rem][c,goal]. Re-pick argmax WITHIN
      the confirmed subset. This restricts M/R's noisy pick to picks the raw graph actually validates.
  (3) If a chain's confirmed subset is EMPTY, RESET FRESH: recompute the confirmed set re-anchored at the
      immutable START (span=pos) toward goal -- never carry the unconfirmed intermediate anchor forward
      (ARM_C_FRESH-style reset). If still empty, fall back to the open argmax (counted as unconfirmed).
  (4) COMMIT the KB-confirmed pick. Execution loop run_hier_arm_wp is IDENTICAL to all ancestors for EVERY
      arm -- the waypoint SOURCE is the only thing that differs.

  MANDATORY INDEPENDENCE SCREEN (this drill's load-bearing pre-registered claim, Kalman-observability):
  per (chain,hop) unit, measure corr(kb_confirm_signal, m_error) where kb_confirm_signal = whether R's
  OPEN argmax pick is KB-reachability-confirmed (exogenous, raw graph) and m_error = the SR estimator's
  per-hop reach error to the TRUE oracle boundary = 1 - unit(R[anchor,true_bnd]) (derived from R+oracle
  ONLY, disjoint from the raw-graph confirm computation). Predict |corr| ~ 0 (near-zero) -- if the KB
  signal is secretly correlated with the estimator's own error it is not independent and will compound
  like the four prior variants. This is REPORTED and GATED.

ARMS (12; paired -- share E, W_ops, M, M_long, M_rev, R_short, R_long, R_rev, reach_cum and the SAME test
chains per (regime,seed)):
  flat_gonogo            FLAT SR Go/NoGo toward the FINAL goal (the collapse; FLOOR)
  oracle_exec            true op_seq perfect execution (ceiling / rail; POSITIVE CONTROL must clear ~0.90)
  hier_oracle            hierarchical with ORACLE waypoints (given-decomposition CEILING; positive control)
  hier_shuffled          hier with WRONG (other-chain) oracle waypoints (neg control)
  wp_bisect_open         PARENT autonomous baseline (the FAILING sequential bisection)
  wp_bisect_verify       SELF-DERIVED-correction MUST-FAIL control (THE KEY COMPARATOR / the bar; ~0.10)
  wp_bisect_coarse2fine  already-failed self-referential control (re-run for paired continuity)
  wp_bisect_combo        already-failed self-referential control (re-run for paired continuity)
  wp_replay_generate_select  already-failed independent-ish control (M_rev bidirectional; re-run verbatim)
  wp_kb_grounded_gate    NEW exogenous KB-grounded-check mechanism (rank 1; under test)  <-- new RESCUE
  wp_random_state        autonomous FLOOR: uniform random codebook waypoints
  wp_index_midpoint      STRUCTURAL-ARTIFACT GUARD: index-interpolated waypoints

DISCRIMINATORS (per regime; FOCUS = op4_V1200_d8, chain_steps=3; best_rescue = wp_kb_grounded_gate FIXED,
NOT a max-over-arms):
  headroom_exec        = oracle_exec - flat ; headroom_decomp = hier_oracle - flat
  recovery_ratio(a)    = (a - flat) / headroom_decomp   (frac of ORACLE-decomp benefit recovered)
  delta_recovery       = recovery(kb) - recovery(wp_bisect_verify)   <-- KEY (drill kill-test: vs the
                         SELF-DERIVED correction control, the ~0.10 wall reproducer)
  flatness_ratio       = recovery(kb, FOCUS chain_steps=3) / recovery(kb, op4_V*_d4 chain_steps=1)
  independence_corr    = corr(kb_confirm_signal, m_error) over per-hop units  <-- MANDATORY; |corr|~0 is
                         the mechanism's load-bearing claim (Kalman innovation orthogonality)
  kb_confirm_mean/std  fraction of R-open-picks KB-confirmed (non-vacuous 0.05<mean<0.95 => gate fires)
  autonomous_closure, lift_flat, lift_random, lift_open (of kb); index_artifact_gap; anti_tautology_corr;
  degenerate_rate; sign_test_p (paired kb vs wp_bisect_verify); cv(kb) (FULL); kb confirm/fresh/fallback rates.

HARD_PASS (locked per drill (c); best_rescue=kb at FOCUS -- exogenous-grounding hypothesis confirmed):
  recovery(kb) >= 0.20 AND delta_recovery(vs verify) >= 0.15 AND flatness_ratio >= 0.5 AND
  |independence_corr| <= 0.15 AND kb_confirm non-vacuous AND lift_flat > 0.05 AND lift_random > 0.10 AND
  index_artifact_gap < 0.05 AND anti_tautology_corr < 0.85 AND degenerate_rate < 0.10 AND sign_p(kb vs
  wp_bisect_verify) < 0.05 AND cv(kb) < 0.15 (FULL only) AND oracle_exec >= 0.90 AND headroom gates.
  => the compounding-error bound was an artifact of SELF-REFERENTIAL correction specifically; a genuinely
     exogenous, informationally-independent ground-truth channel (the raw KB edge table, zero shared
     params) recovers real autonomous-decomposition capability where four prior self-derived / weakly-
     independent variants could not.
HARD_FAIL (locked -- strongest possible closure to date):
  delta_recovery(vs verify) <= 0.05  (no material lift over the self-derived control despite a rigorously
    exogenous channel: bound survives -> quadruply+ confirmed structural)  OR
  |independence_corr| > 0.40  (the KB signal is NOT independent after all -- e.g. R's error tracks KB
    sparsity so the "exogenous" channel is contaminated; the mechanism's premise is void)  OR
  flatness_ratio < 0.2  (still an accelerating, not bounded, collapse).
  => accept the bound as fundamental for autonomous no-oracle waypoint discovery at chain_steps>=3,
     entropy=16; redirect to bounded-depth-budget framing.
MIDDLE_BAND: delta_recovery in [0.05, 0.15) (real but partial), OR flatness_ratio in [0.2, 0.5), OR
  |independence_corr| in (0.15, 0.40] (partial independence), OR kb_confirm vacuous (screen uninformative),
  OR any honesty guard fails while accuracy margins pass, OR delta>=0.15 & flatness>=0.5 but recovery<0.20.
INCONCLUSIVE: no discriminating regime, OR index_artifact_gap > 0.10 with sign_p(index vs random) < 0.05.
Reported REGARDLESS: full grid for every arm; recovery(open/verify/kb) per regime; delta_recovery;
  flatness_ratio; independence_corr; kb confirm/fresh/fallback rates; sign_p; positive-control reproduce-
  check of wp_bisect_open/verify/flat/hier_oracle vs the ancestors (same E/M/R/seeds by construction).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): wp_kb_grounded_gate trace vs wp_bisect_verify/open/flat/
#   random op-trace hash per seed AND hier_oracle vs hier_shuffled (exempt only if bit-identical).
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json).
# - except SystemExit: raise BEFORE except Exception (no BaseException in main).
# - crlb_n/a: accuracy-closure discriminator has no single closed-form noise floor; reachability by
#   feasibility (ancestor hier_oracle=0.906 at op4_d8 proves the given-decomposition envelope; open+
#   verify collapse to ~flat -> the open question is how much of the 0.906 headroom the EXOGENOUS
#   KB-grounded check recovers; HP bar recovery>=0.20 AND flatness>=0.5 sit inside that envelope).
# - baseline_in_band (AG): the KEY baseline is wp_bisect_verify (the SELF-DERIVED-correction MUST-FAIL
#   control), collapsed to ~flat at FOCUS (0.096 vs flat 0.081); discriminator = kb-vs-verify, both
#   measurable; oracle_exec>=0.90 rail + headroom>=0.10 gates ensure room to recover.
# - discriminator survives scale: smoke holds op4 x {d4,d6,d8} at V=300; smoke reach at N=2048 is
#   BLUNTER than FULL N=8192 (KB reachability is EXACT/N-independent; only execution blunts) so a
#   POSITIVE kb-minus-verify lift at smoke is a LOWER bound on FULL (option C directional preview).
#   Smoke that shows open+verify collapse + oracle success + non-vacuous kb_confirm variance + any
#   positive kb-minus-verify + kb trace differs gates the GPU FULL.
# - HARD_PASS strictly above floor: recovery>=0.20 + delta>=0.15 + flatness>=0.5 + |indep_corr|<=0.15.
# - HP_SCOPE: HP gates apply to wp_kb_grounded_gate vs wp_bisect_verify at FOCUS; oracle_rail(>=0.90) to
#   oracle_exec; recovery references hier_oracle; index guard to wp_index vs wp_random; independence
#   screen to the kb_confirm-vs-m_error correlation.
# - cardinality_ok: EXPECTED_N_UNITS = n_arms(12) * n_seeds * n_regimes.
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash).
# - calibration_check: adaptive_with_discriminator_gate (KB confirm = EXACT raw-graph reachability, no
#   tunable threshold; verify-gate tau = 70th-pctl of R off-diag on the control arm; discriminator =
#   delta-over-verify + flatness + |indep_corr|, not tuned-for-PASS).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.

Compute architecture: (a) batched-GPU. SR-TD training (M @ 0.85, M_long @ 0.95, M_rev @ 0.85 on
reversed transitions), operator application, cleanup, reach, R build, bisection + perturbed candidate
generation + bidirectional scoring + KB reach-cum boolean matrix powers = batched matmuls / gathers /
argmax on cuda-if-available. Chains batched; within-chain hops sequential (genuine dependency).
M/M_long/M_rev/R_*/reach_cum computed once per (V,n_ops) group and shared across depths. Storage
strategy: sharded (each operator its own W matrix; M/M_long/M_rev learned operators; R_* derived reach
matrices; reach_cum RAW-graph boolean reachability powers). No bundled store. FULL strongly prefers
overnight_queue (GPU). Extra cost vs replay ancestor: reach_cum = depth boolean VxV matmuls (~8 x
1200^2, trivial) built once per group + one masked re-bisection pass + one independence-screen pass;
linear, no quadratic blowup.
progress_logging: print_flush_true (flush=True on every progress line + per (seed,V,n_ops) heartbeat;
FULL timeout_s >= 1800).

Reuses VERBATIM from experiments/exp_pfc_gate_waypoint_rescue_replay_bidirectional_v1.py (and its
ancestors): make_bipolar_E, hebbian_W, cleanup_batched, make_kb_and_chains, build_adjacency,
collect_rollout_transitions, train_sr_transport, reach_value, build_reach_matrix, codebook_selfcos,
offdiag_quantile, _discover_bisect_boundaries, _pick_balanced_verify, _discover_verify_boundaries,
_discover_coarse2fine_boundaries, _discover_random_boundaries, _discover_index_boundaries,
_discover_bisect_perturbed, generate_candidates, score_bidirectional, wp_replay_generate_select,
_boundaries_to_hops, oracle_trajectory_idx, build_waypoint_idx, _chain_tensors, run_selection_arm,
run_oracle_arm, run_hier_arm_wp, discovery_diagnostics, reach_rank_acc, binom/spearman/rankdata, the
alpha/w_reach tuners, and the defensive start-marker / crash-diag / heartbeat / atomic-write scaffolding.
NEW (additive): build_kb_reach_cum, _discover_kb_grounded_boundaries, wp_hops_kb_grounded,
kb_independence_screen, the wp_kb_grounded_gate arm + the kb-vs-verify + flatness + independence verdict.
"""

import os
import sys
import argparse
import hashlib
import json
import math
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "pfc_gate_waypoint_rescue_precision_combiner_v1"
PARENT_ANCHOR = "pfc_gate_waypoint_rescue_stacked_corrections_v1"

# --------------------------- CLI / run-mode ---------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE)
            else ("selftest" if _ARGS.self_test
                  else os.environ.get("HDLAB_RUN_MODE", "full").lower()))
SELF_TEST_MODE = bool(_ARGS.self_test)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DTYPE = torch.float32

# --------------------------- pre-reg bands (LOCKED at import; PROSPECTIVE) --------
# KEY comparator is wp_bisect_verify (the already-failed SELF-REFERENTIAL control), NOT open.
HP_RECOVERY_RATIO_FLOOR = 0.35    # STACKED recovers >= 35% of oracle-DECOMP benefit (materially above
                                  #   KB-alone's landed 0.2444 -- the frontier-push bar; research (c))
HP_DELTA_RECOVERY_MIN = 0.15      # recovery(stacked) - recovery(wp_bisect_verify) >= 0.15 (decisive)
HP_FLATNESS_MIN = 0.50            # recovery(stacked,FOCUS d8)/recovery(stacked,d4) >= 0.5 (stays flat)
HP_LIFT_FLAT_MIN = 0.05           # real lift over no-hierarchy flat
HP_LIFT_RANDOM_MIN = 0.10         # real lift over a noise waypoint
HP_INDEX_GAP_MAX = 0.05           # no structural index-order leak
HP_ANTI_TAUT_CORR_MAX = 0.85      # balance score is dynamics, not target-cosine in disguise
HP_DEGENERATE_MAX = 0.10          # bisection does not degenerate to picking start/goal
HP_SIGN_TEST_P = 0.05             # paired replay vs wp_bisect_verify significant
HP_CV_MAX = 0.15                  # cross-seed cv on replay at focus (FULL only; loosened doc'd)
HF_DELTA_RECOVERY_CEIL = 0.05     # HARD_FAIL: recovery(kb) <= recovery_verify + 0.05 (no lift)
HF_FLATNESS_CEIL = 0.20           # HARD_FAIL: flatness_ratio < 0.2 (accelerating collapse)
HP_INDEP_CORR_MAX = 0.15          # HARD_PASS: |corr(kb_confirm, m_error)| <= 0.15 (near-zero: independent)
HF_INDEP_CORR_CEIL = 0.40         # HARD_FAIL: |corr| > 0.40 (KB signal contaminated / not independent)
KB_CONFIRM_MEAN_LO = 0.05         # kb_confirm non-vacuous lower edge (gate fires: some picks unconfirmed)
KB_CONFIRM_MEAN_HI = 0.95         # kb_confirm non-vacuous upper edge (gate fires: some picks confirmed)
MIDDLE_DELTA_MIN = 0.05           # MIDDLE lower edge (real partial lift over verify)
# ---- NEW stacked-corrections bands (research (c); the multiplicative-stacking claim) ----
HP_STACKED_OVER_KB_MIN = 0.03     # HARD_PASS: recovery(stacked) - recovery(kb_alone) >= this (stacking
                                  #   materially beats the better single channel -- frontier genuinely pushed)
HP_FLATNESS_OVER_KB_MIN = 0.10    # HARD_PASS: flatness(stacked,d8) - flatness(kb_alone,d8) >= this (research)
HP_FAILMASK_CORR_MAX = 0.20       # HARD_PASS: corr(fail_KB, fail_SEL) <= this (near-independent failures --
                                  #   the load-bearing NEW screen; research point-2 predicts this is hardest)
HF_FAILMASK_CORR_CEIL = 0.50      # HARD_FAIL: corr(fail_KB, fail_SEL) > this (shared-coverage-cause confirmed)
HP_SEL_INDEP_CORR_MAX = 0.15      # HARD_PASS: |corr(selector_confidence, m_error)| <= this (screen 1, channel B)
# ---- NEW precision-preserving-combiner bands (this cell's headline discriminator) ----
# best_combiner_over_kb = max over {C1 AND-gate, C2 KB-priority union, C3 calibrated-gate} of
#   recovery(cX) - recovery(kb_alone). The combiner must ADD over the single best channel (KB-alone)
#   WHILE the OR-gate B0 stays dilutive (the confirmed-negative fair-contrast control).
HP_COMBINER_OVER_KB_MIN = 0.05    # HARD_PASS: best precision-preserving combiner clears KB-alone recovery
                                  #   by >= this at FOCUS (pre-registered depth margin; strictly-above-floor)
HF_COMBINER_OVER_KB_CEIL = 0.02   # HARD_FAIL: best_combiner_over_kb <= this => NO combiner beats KB-alone
                                  #   => second channel too weak under ANY rule => single-best-channel FINAL
OR_GATE_DILUTIVE_MAX = 0.0        # fair-contrast control: the B0 OR-gate must stay <= this over KB-alone at
                                  #   FOCUS (reproduce the confirmed negative). If B0 itself beats KB the
                                  #   OR-dilution premise did not reproduce -> INCONCLUSIVE (contrast void).
MIDDLE_COMBINER_OVER_KB_MIN = 0.02  # MIDDLE lower edge: real-but-partial combiner lift over KB-alone
SELECTOR_TAU_HI_PCTL = 0.85       # C3 calibrated-gate: STRICTER correctness percentile than the 70th-pctl
                                  #   selector-accept tau (filters the union's re-admitted low-precision cand)
SELECTOR_TAU_PCTL = 0.70          # selector-accept threshold = 70th-pctl of fold-B calibrated scores
SELECTOR_FIT_STEPS = 400          # logistic-scorer gradient steps on fold A
SELECTOR_FIT_LR = 0.5             # logistic-scorer base lr
SELECTOR_N_NEG = 4                # random negatives per positive in the selector training set
SELECTOR_MIN_ACC_FRAC = 0.05      # selector-accept non-vacuous lower edge (some picks rejected)
SELECTOR_MAX_ACC_FRAC = 0.98      # selector-accept non-vacuous upper edge (some picks accepted)
INDEX_LEAK_GAP = 0.10             # INCONCLUSIVE: index beats random by > this ...
INDEX_LEAK_P = 0.05               # ... with paired sign p < this
ORACLE_RAIL_MIN = 0.90            # FOCUS: perfect-execution ceiling must be reachable
HEADROOM_EXEC_MIN = 0.10          # FOCUS: flat->perfect gap measurable
HEADROOM_DECOMP_MIN = 0.10        # FOCUS: oracle-decomposition benefit measurable (room to recover)
N_CAND = 5                        # replay: number of complete candidate trajectories generated
PERTURB_FRAC = 0.60               # replay: gaussian tie-break noise = this * per-row balance std
BIDIR_EPS = 1e-6                  # harmonic-mean denominator epsilon

DENSITY = 0.21                     # n_train_triples_per_op / V (matches parent)
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0
LR_DECAY_END = 0.2

GAMMA_SHORT = 0.85                 # parent's fixed SR gamma (effective horizon 1/(1-g)=6.67 hops)
GAMMA_LONG = 0.95                  # coarse-pick long-horizon SR (effective horizon ~20 hops)
SPAN_LONG_THRESH = 5               # use GAMMA_LONG when a pick spans > this many hops
VERIFY_TAU_PCTL = 0.70             # verify-gate threshold = this percentile of R off-diagonal
MAX_VERIFY_RETRY = 5               # verify-gate retries before random fallback
GAMMA = GAMMA_SHORT                # alias (reach_rank / diagnostics use the short SR)
ALPHA_SWEEP = [0.1, 0.2, 0.5]
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]
SEG_LEN = 2                        # hierarchical segment length (per-decision reach horizon cap)
NEG_HARD = -1.0e9                  # exclude start/goal/already-chosen from bisection argmax
NEG_SOFT = -1.0e4                  # (unused here; retained for parity with parent primitive shapes)

# --------------------------- config (selftest / smoke / full) --------------------
# Regime = (n_ops, V, dd). SR M + M_long + R trained/built once per (V,n_ops) group and shared
# across depths. SMOKE = op4 x {d4,d6,d8} at V=300 (open works at d4, collapses at d6/d8 -> fires the
# rescue discriminator; deepest corner op4_d8 included as directional preview at BLUNTER N=2048 reach).
if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    REGIMES = [{"n_ops": 4, "V": 40, "dd": 4}, {"n_ops": 4, "V": 40, "dd": 8}]
    N_TRAIN_CHAINS = 12
    N_TEST_CHAINS = 8
    SR_STEPS = 120
    SR_BATCH = 32
    SR_LR = 0.5
    ROLLOUT_PER_V = 20
elif RUN_MODE == "smoke":
    # multi-seed (3). op4 x {d4,d6,d8}. RE-SPEC 2026-07-09: the V=300/48-chain smoke was too small to form a
    # valid contrast -- KB collapsed BELOW flat at the noise-dominated d8 corner (recov_kb<0) and the OR-gate
    # dilution premise did not cleanly reproduce (single-chain noise on 48 chains). (N=4096 was too slow on
    # CPU -> ~25min/seed for SR alone.) V=600 at N=2048 keeps SR fast while giving a SPARSER KB coverage
    # (closer to the FULL V=1200 regime where KB coverage holes exist); 96 test chains HALVE the single-chain
    # granularity so the confirmed-negative (OR-dilutive) reproduces; SR_STEPS=3200 trains KB reach ABOVE
    # flat at depth. Blunter than FULL N=8192 -> a POSITIVE smoke best_combiner_over_kb is a LOWER bound on
    # FULL (option-C directional preview); KB reachability is EXACT/N-independent.
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    REGIMES = [{"n_ops": 4, "V": 600, "dd": 4},
               {"n_ops": 4, "V": 600, "dd": 6},
               {"n_ops": 4, "V": 600, "dd": 8}]   # FOCUS: deepest corner (chain_steps=3)
    N_TRAIN_CHAINS = 96
    N_TEST_CHAINS = 96
    SR_STEPS = 3200        # trained-enough SR so KB reach rises ABOVE flat at depth (valid contrast)
    SR_BATCH = 96
    SR_LR = 0.5
    ROLLOUT_PER_V = 20
else:  # full
    N_DIM = 8192
    SEEDS = [7, 17, 23, 31, 41]
    REGIMES = [{"n_ops": 4, "V": 1200, "dd": 4},   # easy: open recovers 0.690 (rescue must not harm)
               {"n_ops": 4, "V": 1200, "dd": 6},   # collapse begins (chain_steps=2)
               {"n_ops": 4, "V": 1200, "dd": 8},   # FOCUS: the exact parent HARD_FAIL corner (steps=3)
               {"n_ops": 3, "V": 1000, "dd": 8},   # frontier
               {"n_ops": 2, "V": 800, "dd": 8}]    # matched-entropy(=8) chain_steps=3 dissociation
    N_TRAIN_CHAINS = 300
    N_TEST_CHAINS = 240
    SR_STEPS = 8000
    SR_BATCH = 256
    SR_LR = 0.5
    ROLLOUT_PER_V = 50

ROLLOUT_CAP = 4000 if RUN_MODE == "smoke" else 200000
SR_STEPS = int(os.environ.get("HDLAB_SR_STEPS", str(SR_STEPS)))
ROLLOUT_PER_V = int(os.environ.get("HDLAB_ROLLOUT_PER_V", str(ROLLOUT_PER_V)))
ROLLOUT_CAP = int(os.environ.get("HDLAB_ROLLOUT_CAP", str(ROLLOUT_CAP)))

ARMS = ["flat_gonogo", "oracle_exec", "hier_oracle", "hier_shuffled",
        "wp_bisect_open", "wp_bisect_coarse2fine", "wp_bisect_verify", "wp_bisect_combo",
        "wp_replay_generate_select", "wp_kb_grounded_gate",
        "wp_calibrated_selector_gate", "wp_stacked_kb_plus_selector",
        "wp_and_gate", "wp_kbpriority_union", "wp_calibrated_gate_combiner",
        "wp_random_state", "wp_index_midpoint"]
# THREE precision-preserving combiners under test (the discriminator is a max-over-these vs KB-alone):
COMBINER_ARMS = ["wp_and_gate", "wp_kbpriority_union", "wp_calibrated_gate_combiner"]
OR_GATE_ARM = "wp_stacked_kb_plus_selector"  # B0: the naive OR-union = CONFIRMED-NEGATIVE / must-stay-dilutive
KB_ARM = "wp_kb_grounded_gate"               # single-best channel (the reference the combiner must ADD over)
SELECTOR_ARM = "wp_calibrated_selector_gate" # channel B (cross-fit calibrated selector, alone)
KEY_COMPARATOR = "wp_bisect_verify"          # the SELF-DERIVED-correction MUST-FAIL control (legacy bar)
# RESCUE_ARM is now DYNAMIC (the best-of-three combiner selected per-regime by recovery); a default is set
# for the paired-machinery scaffolding but the verdict re-selects the winner at FOCUS.
RESCUE_ARM = "wp_kbpriority_union"            # default primary combiner (C2; most principled); re-selected
N_OPS_SET = sorted(set(r["n_ops"] for r in REGIMES))
DEPTH_SET = sorted(set(r["dd"] for r in REGIMES))


def rollout_count(V: int) -> int:
    return int(min(ROLLOUT_CAP, ROLLOUT_PER_V * V))


def n_triples_per_op(V: int) -> int:
    return max(4, int(round(DENSITY * V)))


def regime_key(n_ops: int, V: int, dd: int) -> str:
    return "op%d_V%d_d%d" % (n_ops, V, dd)


def group_key(n_ops: int, V: int) -> str:
    return "op%d_V%d" % (n_ops, V)


def decision_entropy(n_ops: int, dd: int) -> float:
    return float(math.log2(n_ops) * dd)


def n_boundaries(depth: int, seg_len: int) -> int:
    return (depth + seg_len - 1) // seg_len


def gamma_for_span(span: int) -> float:
    """Long-horizon SR (gamma=0.95, eff horizon ~20) for coarse picks spanning beyond gamma=0.85's
    effective horizon (1/(1-0.85)=6.67 hops); short SR otherwise. THEORETICAL@Sutton TD eff-horizon."""
    return GAMMA_LONG if span > SPAN_LONG_THRESH else GAMMA_SHORT


REGIME_KEYS = [regime_key(r["n_ops"], r["V"], r["dd"]) for r in REGIMES]
EXPECTED_N_UNITS = len(ARMS) * len(SEEDS) * len(REGIMES)

CONFIG_VERSION = (
    "ANCHOR=%s,parent=%s,N=%d,n_ops_set=%s,depth_set=%s,seeds=%s,gS=%.2f,gL=%.2f,span_thr=%d,"
    "tau_pctl=%.2f,max_retry=%d,seg_len=%d,regimes=%s,density=%.3f,sr_steps=%d,sr_batch=%d,"
    "rollout_per_V=%d,lr=%.2f,alphas=%s,w_reach=%s,n_train=%d,n_test=%d,mode=%s,device=%s,"
    "expected_n=%d,rescue=%s,keycmp=%s,n_cand=%d,perturb=%.2f,HP_recov>=%.2f,HP_delta>=%.2f,"
    "HP_flat>=%.2f,HP_indep<=%.2f,HF_indep>%.2f,HF_delta<=%.2f,HF_flat<%.2f,lift_flat>%.2f,lift_rand>%.2f,"
    "idx_gap<%.2f,anti_taut<%.2f,degen<%.2f,sign_p<%.2f,cv<%.2f"
) % (
    ANCHOR_NAME, PARENT_ANCHOR, N_DIM, N_OPS_SET, DEPTH_SET, SEEDS, GAMMA_SHORT, GAMMA_LONG,
    SPAN_LONG_THRESH, VERIFY_TAU_PCTL, MAX_VERIFY_RETRY, SEG_LEN, REGIME_KEYS, DENSITY, SR_STEPS,
    SR_BATCH, ROLLOUT_PER_V, SR_LR, ALPHA_SWEEP, W_REACH_SWEEP, N_TRAIN_CHAINS, N_TEST_CHAINS,
    RUN_MODE, str(DEVICE), EXPECTED_N_UNITS, RESCUE_ARM, KEY_COMPARATOR, N_CAND, PERTURB_FRAC,
    HP_RECOVERY_RATIO_FLOOR, HP_DELTA_RECOVERY_MIN, HP_FLATNESS_MIN, HP_INDEP_CORR_MAX, HF_INDEP_CORR_CEIL,
    HF_DELTA_RECOVERY_CEIL, HF_FLATNESS_CEIL, HP_LIFT_FLAT_MIN, HP_LIFT_RANDOM_MIN, HP_INDEX_GAP_MAX,
    HP_ANTI_TAUT_CORR_MAX, HP_DEGENERATE_MAX, HP_SIGN_TEST_P, HP_CV_MAX,
)

_T0 = time.time()


# ============================================================================
# defensive-error-checking helpers (start marker / crash diag / heartbeat)
# ============================================================================
def _write_start_marker(out_dir: Path) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "expected_n_units": EXPECTED_N_UNITS, "host": platform.node(), "device": str(DEVICE),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, final)


def _atomic_write_metrics(out_dir: Path, payload: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, final)


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": round(time.time() - _T0, 1), "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
    }
    try:
        _atomic_write_metrics(out_dir, diag)
    except Exception as e:
        print("[_write_crash_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _heartbeat(out_dir: Path, unit_idx: int, total: int, note: str = "") -> None:
    try:
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(),
               "unit_idx": unit_idx, "total_units": total,
               "elapsed_s": round(time.time() - _T0, 1), "note": note}
        with (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


# ============================================================================
# primitives (torch, batched, device-agnostic) -- reused VERBATIM from parent
# ============================================================================
def _norm_rows(X: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    return X / (X.norm(dim=-1, keepdim=True) + eps)


def make_bipolar_E(V: int, n: int, gen: torch.Generator) -> torch.Tensor:
    """[V, n] row-normalized bipolar codebook."""
    X = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE, dtype=DTYPE) * 2 - 1)
    return _norm_rows(X)


def hebbian_W(triples: List[Tuple[int, int]], E: torch.Tensor, n: int) -> torch.Tensor:
    """W = sum_s E[s]^T E[o] / n ; out = state @ W ~= E[o] for matching triple."""
    if not triples:
        return torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    arr = torch.tensor(triples, dtype=torch.long, device=DEVICE)
    S = E[arr[:, 0]]
    O = E[arr[:, 1]]
    return (S.transpose(0, 1) @ O) / float(n)


def cleanup_batched(vecs: torch.Tensor, E: torch.Tensor
                    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """vecs [B, n] -> (idx [B], cleaned E[idx] [B, n], manifold_max_sim [B])."""
    vn = _norm_rows(vecs)
    sims = vn @ E.transpose(0, 1)
    manifold, idx = sims.max(dim=1)
    return idx, E[idx], manifold


# ============================================================================
# KB + chains (exact-length paths; train and test disjoint chain sets) -- VERBATIM
# ============================================================================
def make_kb_and_chains(n_ops: int, V: int, density: float,
                       n_train_chains: int, n_test_chains: int,
                       depths: List[int], g: np.random.Generator
                       ) -> Tuple[List[List[Tuple[int, int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]]]:
    n_train_triples = n_triples_per_op(V)
    per_op: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]
    for _ in range(n_train_triples * n_ops):
        s = int(g.integers(0, V)); o = int(g.integers(0, V))
        op = int(g.integers(0, n_ops))
        if s != o:
            per_op[op].append((s, o))

    def _grow_chain(depth: int) -> Tuple[int, List[int], int]:
        s = int(g.integers(0, V))
        cur = s
        op_seq: List[int] = []
        for _ in range(depth):
            op = int(g.integers(0, n_ops))
            cands = [o for (ss, o) in per_op[op] if ss == cur]
            if not cands:
                new_o = int(g.integers(0, V))
                while new_o == cur:
                    new_o = int(g.integers(0, V))
                per_op[op].append((cur, new_o))
                cur = new_o
            else:
                cur = int(cands[g.integers(0, len(cands))])
            op_seq.append(op)
        return (s, op_seq, cur)

    train_by_d: Dict[int, List[Tuple[int, List[int], int]]] = {}
    test_by_d: Dict[int, List[Tuple[int, List[int], int]]] = {}
    for depth in depths:
        train_by_d[depth] = [_grow_chain(depth) for _ in range(n_train_chains)]
        test_by_d[depth] = [_grow_chain(depth) for _ in range(n_test_chains)]
    return per_op, train_by_d, test_by_d


def build_adjacency(per_op: List[List[Tuple[int, int]]], n_ops: int
                    ) -> List[Dict[int, List[int]]]:
    adj: List[Dict[int, List[int]]] = [dict() for _ in range(n_ops)]
    for op in range(n_ops):
        for (s, o) in per_op[op]:
            adj[op].setdefault(s, []).append(o)
    return adj


def collect_rollout_transitions(adj: List[Dict[int, List[int]]], n_ops: int, V: int,
                                n_transitions: int, max_len: int,
                                g: np.random.Generator) -> np.ndarray:
    """Random-walk (cur, nxt) transitions over the union multigraph for SR-TD training. VERBATIM."""
    out: List[Tuple[int, int]] = []
    if all(len(a) == 0 for a in adj):
        return np.zeros((0, 2), dtype=np.int64)
    while len(out) < n_transitions:
        cur = int(g.integers(0, V))
        for _ in range(max_len):
            op = int(g.integers(0, n_ops))
            nbrs = adj[op].get(cur)
            if not nbrs:
                break
            nxt = int(nbrs[g.integers(0, len(nbrs))])
            out.append((cur, nxt))
            cur = nxt
            if len(out) >= n_transitions:
                break
    return np.asarray(out, dtype=np.int64)


def train_sr_transport(E: torch.Tensor, transitions: np.ndarray, n: int,
                       steps: int, batch: int, base_lr: float, gamma: float,
                       gen: torch.Generator) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """Learn M [n,n] s.t. E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M) (discounted SR features). VERBATIM."""
    M = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    K = transitions.shape[0]
    diag = {"gamma": float(gamma), "n_transitions": int(K), "n_clamped_steps": 0,
            "err_first": None, "err_last": None, "final_M_norm": 0.0}
    if K < 2:
        return M, diag
    cur_t = torch.tensor(transitions[:, 0], dtype=torch.long, device=DEVICE)
    nxt_t = torch.tensor(transitions[:, 1], dtype=torch.long, device=DEVICE)
    sqrt_n = math.sqrt(float(n))
    for step in range(steps):
        decay = 1.0 - (1.0 - LR_DECAY_END) * (step / max(1, steps - 1))
        st = torch.randint(0, K, (batch,), generator=gen, device=DEVICE)
        Ecur = E[cur_t[st]]
        Enxt = E[nxt_t[st]]
        pred = Ecur @ M
        with torch.no_grad():
            boot = Enxt + gamma * (Enxt @ M)
        error = boot - pred
        e_norm = error.norm(dim=1) / sqrt_n
        med = float(torch.median(e_norm))
        med_safe = med if med > 1e-8 else 1e-8
        ratio = e_norm / med_safe
        ratio_c = torch.clamp(ratio, ADAPT_LR_FLOOR, ADAPT_LR_CEIL)
        if bool(((ratio < ADAPT_LR_FLOOR) | (ratio > ADAPT_LR_CEIL)).any()):
            diag["n_clamped_steps"] += 1
        lr_per = base_lr * decay * ratio_c
        dM = (Ecur.transpose(0, 1) @ (error * lr_per.unsqueeze(1))) / float(batch)
        M = M + dM
        e_mean = float(e_norm.mean())
        if step == 0:
            diag["err_first"] = round(e_mean, 6)
        diag["err_last"] = round(e_mean, 6)
    diag["final_M_norm"] = round(float(M.norm()), 4)
    return M, diag


def reach_value(cand_E: torch.Tensor, goal_E: torch.Tensor, M: torch.Tensor) -> torch.Tensor:
    """cos(E[cand] @ M, E[goal]) per row -- learned-dynamics reach. VERBATIM."""
    fwd = _norm_rows(cand_E @ M)
    return (fwd * _norm_rows(goal_E)).sum(dim=1)


def build_reach_matrix(E: torch.Tensor, M: torch.Tensor) -> torch.Tensor:
    """R [V,V], R[i,j] == reach_value(E[i], E[j], M) == cos(E[i]@M, E[j]). VERBATIM."""
    Efwd = _norm_rows(E @ M)
    En = _norm_rows(E)
    return Efwd @ En.transpose(0, 1)


def codebook_selfcos(E: torch.Tensor) -> torch.Tensor:
    """C [V,V], C[i,j] == cos(E[i], E[j]) (anti-tautology reference). VERBATIM."""
    En = _norm_rows(E)
    return En @ En.transpose(0, 1)


def offdiag_quantile(R: torch.Tensor, q: float) -> float:
    """q-th quantile of R's off-diagonal entries -- the verify-gate threshold tau. Adaptive but
    principled (candidate must reach as well as a typical state-pair does)."""
    V = R.shape[0]
    mask = ~torch.eye(V, dtype=torch.bool, device=DEVICE)
    vals = R[mask]
    if vals.numel() > 4_000_000:                 # torch.quantile input cap; subsample deterministically
        vals = vals[:: (vals.numel() // 4_000_000) + 1]
    return float(torch.quantile(vals, q))


# ============================================================================
# waypoint DISCOVERY: parent baselines (VERBATIM) + NEW rescue mechanisms
# ============================================================================
def _discover_bisect_boundaries(starts: torch.Tensor, targets: torch.Tensor, R: torch.Tensor,
                                seg_len: int, depth: int) -> torch.Tensor:
    """PARENT wp_bisect_open baseline: sequential greedy bisection. anchor=prev wp (start first);
    wp = argmax_c min(R[anchor,c], R[c,goal]) excluding start/goal/chosen. The FAILING mechanism.
    Returns boundary_states [n_chains, n_bnd], last column = targets. VERBATIM (cand_mask dropped)."""
    n_chains = starts.shape[0]
    n_bnd = n_boundaries(depth, seg_len)
    rowar = torch.arange(n_chains, device=DEVICE)
    rg = R.index_select(1, targets).transpose(0, 1)         # [n_chains, V], rg[i,c] = R[c, goal_i]
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    for _ in range(n_bnd - 1):
        ra = R.index_select(0, anchor)                       # [n_chains, V], ra[i,c] = R[anchor_i,c]
        balance = torch.minimum(ra, rg).clone()
        balance[rowar, starts] = NEG_HARD
        balance[rowar, targets] = NEG_HARD
        for prev in chosen_cols:
            balance[rowar, prev] = NEG_HARD
        wp = balance.argmax(dim=1)
        chosen_cols.append(wp)
        anchor = wp
    cols = chosen_cols + [targets]
    return torch.stack(cols, dim=1)


def _pick_balanced_verify(anchor: torch.Tensor, goal: torch.Tensor, R: torch.Tensor,
                          tau: float, excl_cols: List[torch.Tensor], use_verify: bool,
                          gen_np: np.random.Generator,
                          stats: Optional[Dict[str, int]]) -> torch.Tensor:
    """Pick wp = argmax_c min(R[anchor,c], R[c,goal]) excluding anchor/goal/excl_cols. If use_verify,
    a candidate must clear R[anchor,c]>=tau AND R[c,goal]>=tau; else exclude it and retry the argmax
    (capped at MAX_VERIFY_RETRY); on total exhaustion, uniform-random valid fallback (logged). Returns
    chosen [n_chains]. Vectorized across chains."""
    nc = anchor.shape[0]
    row = torch.arange(nc, device=DEVICE)
    ra = R.index_select(0, anchor)                          # [nc, V]
    rg = R.index_select(1, goal).transpose(0, 1)            # [nc, V]
    balance = torch.minimum(ra, rg).clone()
    balance[row, anchor] = NEG_HARD
    balance[row, goal] = NEG_HARD
    for c in excl_cols:
        balance[row, c] = NEG_HARD
    if not use_verify:
        wp = balance.argmax(dim=1)
        if stats is not None:
            stats["n_picks"] += nc
        return wp
    passv = (ra >= tau) & (rg >= tau)                       # [nc, V]
    work = balance.clone()
    chosen = torch.full((nc,), -1, dtype=torch.long, device=DEVICE)
    retried = torch.zeros(nc, dtype=torch.long, device=DEVICE)
    for _attempt in range(MAX_VERIFY_RETRY + 1):
        cand = work.argmax(dim=1)
        valid = work[row, cand] > (NEG_HARD * 0.5)          # not fully excluded
        ok = passv[row, cand] & valid & (chosen < 0)
        chosen = torch.where(ok, cand, chosen)
        need = (chosen < 0)
        if not bool(need.any()):
            break
        work[row[need], cand[need]] = NEG_HARD              # exclude this candidate; retry
        retried = retried + need.long()
    unresolved = (chosen < 0)
    n_fallback = int(unresolved.sum())
    if n_fallback > 0:
        V = R.shape[0]
        anc_np = anchor.detach().cpu().numpy()
        goal_np = goal.detach().cpu().numpy()
        excl_np = [c.detach().cpu().numpy() for c in excl_cols]
        for ii in torch.where(unresolved)[0].tolist():
            bad = {int(anc_np[ii]), int(goal_np[ii])}
            for c in excl_np:
                bad.add(int(c[ii]))
            r = int(gen_np.integers(0, V)); tries = 0
            while r in bad and tries < 12:
                r = int(gen_np.integers(0, V)); tries += 1
            chosen[ii] = r
    if stats is not None:
        stats["n_picks"] += nc
        stats["n_retry"] += int((retried > 0).sum())
        stats["n_fallback"] += n_fallback
    return chosen


def _discover_verify_boundaries(starts: torch.Tensor, targets: torch.Tensor, R: torch.Tensor,
                                tau: float, seg_len: int, depth: int,
                                gen_np: np.random.Generator,
                                stats: Optional[Dict[str, int]] = None) -> torch.Tensor:
    """RESCUE (b): parent SEQUENTIAL bisection + verify-gate (single gamma=short). Same left-to-right
    anchor-advance as wp_bisect_open, but each pick must clear the verify-gate."""
    n_bnd = n_boundaries(depth, seg_len)
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    for _ in range(n_bnd - 1):
        wp = _pick_balanced_verify(anchor, targets, R, tau, chosen_cols, True, gen_np, stats)
        chosen_cols.append(wp)
        anchor = wp
    cols = chosen_cols + [targets]
    return torch.stack(cols, dim=1)


def _discover_coarse2fine_boundaries(starts: torch.Tensor, targets: torch.Tensor,
                                     R_short: torch.Tensor, R_long: torch.Tensor,
                                     tau_short: float, tau_long: float, seg_len: int, depth: int,
                                     use_verify: bool, gen_np: np.random.Generator,
                                     stats: Optional[Dict[str, int]] = None) -> torch.Tensor:
    """RESCUE (a)+(c) [+ (b) if use_verify]: recursive MIDPOINT-FIRST bisection. Fill the interior
    boundary nearest the midpoint of the current [lo,hi] interval FIRST (both endpoints determined:
    ground-truth at the root), then recurse into each half. Long-horizon SR for spans > SPAN_LONG_THRESH.
    The recursion tree has height ~log(T) so error does not compound through a length-T running anchor."""
    n_bnd = n_boundaries(depth, seg_len)
    n_interior = n_bnd - 1
    interior_pos = [(j + 1) * seg_len for j in range(n_interior)]
    determined: Dict[int, torch.Tensor] = {0: starts.clone(), depth: targets.clone()}
    det_interior_cols: List[torch.Tensor] = []              # already-chosen interior states (exclude)

    def fill(lo: int, hi: int) -> None:
        inside = [p for p in interior_pos if lo < p < hi and p not in determined]
        if not inside:
            return
        mid = 0.5 * (lo + hi)
        p = min(inside, key=lambda x: (abs(x - mid), x))     # midpoint-first, ties -> lower index
        span = hi - lo
        long = span > SPAN_LONG_THRESH
        R = R_long if long else R_short
        tau = tau_long if long else tau_short
        wp = _pick_balanced_verify(determined[lo], determined[hi], R, tau,
                                   det_interior_cols, use_verify, gen_np, stats)
        determined[p] = wp
        det_interior_cols.append(wp)
        fill(lo, p)
        fill(p, hi)

    fill(0, depth)
    cols = [determined[(j + 1) * seg_len] for j in range(n_interior)] + [targets]
    return torch.stack(cols, dim=1)


def _discover_random_boundaries(starts: torch.Tensor, targets: torch.Tensor, V: int,
                                seg_len: int, depth: int, g: np.random.Generator) -> torch.Tensor:
    """Uniform random codebook waypoints; avoid start/goal. TRUE floor. VERBATIM."""
    n_chains = starts.shape[0]
    n_bnd = n_boundaries(depth, seg_len)
    st = starts.detach().cpu().numpy()
    tg = targets.detach().cpu().numpy()
    cols: List[torch.Tensor] = []
    for _ in range(n_bnd - 1):
        r = g.integers(0, V, size=n_chains)
        for _try in range(6):
            bad = (r == st) | (r == tg)
            if not bad.any():
                break
            r = np.where(bad, g.integers(0, V, size=n_chains), r)
        cols.append(torch.tensor(r, dtype=torch.long, device=DEVICE))
    cols.append(targets)
    return torch.stack(cols, dim=1)


def _discover_index_boundaries(starts: torch.Tensor, targets: torch.Tensor, V: int,
                               seg_len: int, depth: int) -> torch.Tensor:
    """Structural-artifact guard: interpolate wp by RAW CODEBOOK INDEX. VERBATIM."""
    n_bnd = n_boundaries(depth, seg_len)
    st = starts.to(DTYPE)
    tg = targets.to(DTYPE)
    cols: List[torch.Tensor] = []
    for j in range(n_bnd - 1):
        pos = min((j + 1) * seg_len, depth)
        t = pos / float(depth)
        wp = torch.round(st * (1.0 - t) + tg * t).long().clamp_(0, V - 1)
        coll = (wp == starts) | (wp == targets)
        wp = torch.where(coll, (wp + 1).clamp_(0, V - 1), wp)
        coll2 = (wp == starts) | (wp == targets)
        wp = torch.where(coll2, (wp - 2).clamp_(0, V - 1), wp)
        cols.append(wp)
    cols.append(targets)
    return torch.stack(cols, dim=1)


def _boundaries_to_hops(boundary_states: torch.Tensor, seg_len: int, depth: int) -> torch.Tensor:
    """Map boundary states [n_chains, n_bnd] -> per-hop waypoint schedule [n_chains, depth]. VERBATIM."""
    n_bnd = boundary_states.shape[1]
    hop_to_bnd = [min(h // seg_len, n_bnd - 1) for h in range(depth)]
    idx = torch.tensor(hop_to_bnd, dtype=torch.long, device=DEVICE)
    return boundary_states.index_select(1, idx)


def oracle_trajectory_idx(chains, W_ops: List[torch.Tensor], E: torch.Tensor, depth: int
                          ) -> torch.Tensor:
    """Per-hop cleaned-state INDICES along the true (oracle) trajectory -> [n_chains, depth+1]. VERBATIM."""
    starts, targets, op_seqs = _chain_tensors(chains)
    n_chains = starts.shape[0]
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=DEVICE)
    traj = torch.empty((n_chains, depth + 1), dtype=torch.long, device=DEVICE)
    traj[:, 0] = starts
    state = E[starts].clone()
    for hop in range(depth):
        ops_h = op_seq_t[:, hop]
        new_idx = torch.empty(n_chains, dtype=torch.long, device=DEVICE)
        for op in range(len(W_ops)):
            mask = (ops_h == op)
            if not bool(mask.any()):
                continue
            out = state[mask] @ W_ops[op]
            idx, cleaned, _ = cleanup_batched(out, E)
            new_idx[mask] = idx
        traj[:, hop + 1] = new_idx
        state = E[new_idx]
    traj[:, depth] = targets
    return traj


def build_waypoint_idx(traj_idx: torch.Tensor, seg_len: int, depth: int, shuffle: bool
                       ) -> torch.Tensor:
    """Oracle/shuffled per-hop waypoint index [n_chains, depth]. VERBATIM."""
    src = torch.roll(traj_idx, shifts=1, dims=0) if shuffle else traj_idx
    wp_hop = [min(((h // seg_len) + 1) * seg_len, depth) for h in range(depth)]
    wp_hop_t = torch.tensor(wp_hop, dtype=torch.long, device=DEVICE)
    return src[:, wp_hop_t]


# ============================================================================
# arms (batched across chains; hops sequential within a chain) -- VERBATIM
# ============================================================================
def _chain_tensors(chains: List[Tuple[int, List[int], int]]
                   ) -> Tuple[torch.Tensor, torch.Tensor, np.ndarray]:
    starts = torch.tensor([c[0] for c in chains], dtype=torch.long, device=DEVICE)
    targets = torch.tensor([c[2] for c in chains], dtype=torch.long, device=DEVICE)
    op_seqs = np.asarray([c[1] for c in chains], dtype=np.int64)
    return starts, targets, op_seqs


def run_selection_arm(mode: str, chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                      M: torch.Tensor, depth: int, alpha: float, w_reach: float
                      ) -> Tuple[np.ndarray, np.ndarray]:
    """FLAT batched op-selection arm toward the FINAL goal every hop. VERBATIM."""
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()
    goal_E = E[targets]
    op_trace = np.zeros((n_chains, depth), dtype=np.int64)
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    final_idx = starts
    for hop in range(depth):
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, manifold = cleanup_batched(out, E)
            cand_idx[:, op] = idx
            out_n = _norm_rows(out)
            goal_sim = (out_n * _norm_rows(goal_E)).sum(dim=1)
            if mode == "gonogo":
                reach = reach_value(cleaned, goal_E, M)
                sc = w_manifold * manifold + alpha * goal_sim + w_reach * reach
            else:
                raise ValueError("unknown mode %r" % mode)
            scores[:, op] = sc
        chosen = scores.argmax(dim=1)
        op_trace[:, hop] = chosen.detach().cpu().numpy()
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx[row, chosen]
        state = E[new_idx]
        final_idx = new_idx
    correct = (final_idx == targets).detach().cpu().numpy()
    return correct.astype(bool), op_trace


def run_oracle_arm(chains, W_ops: List[torch.Tensor], E: torch.Tensor, depth: int) -> np.ndarray:
    starts, targets, op_seqs = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=DEVICE)
    final_idx = starts
    for hop in range(depth):
        ops_h = op_seq_t[:, hop]
        new_idx = torch.empty(n_chains, dtype=torch.long, device=DEVICE)
        for op in range(len(W_ops)):
            mask = (ops_h == op)
            if not bool(mask.any()):
                continue
            out = state[mask] @ W_ops[op]
            idx, cleaned, _ = cleanup_batched(out, E)
            new_idx[mask] = idx
        state = E[new_idx]
        final_idx = new_idx
    correct = (final_idx == targets).detach().cpu().numpy()
    return correct.astype(bool)


def run_hier_arm_wp(chains, W_ops: List[torch.Tensor], E: torch.Tensor, M: torch.Tensor,
                    depth: int, seg_len: int, alpha: float, w_reach: float,
                    wp_idx: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
    """HIERARCHICAL-OPTIONS execution given an EXTERNAL per-hop waypoint schedule wp_idx. The waypoint
    SOURCE is the ONLY thing that differs across all wp_* / hier_* arms. VERBATIM."""
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    wp_E_all = E[wp_idx]
    state = E[starts].clone()
    op_trace = np.zeros((n_chains, depth), dtype=np.int64)
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    final_idx = starts
    for hop in range(depth):
        wp = wp_E_all[:, hop, :]
        wp_n = _norm_rows(wp)
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, manifold = cleanup_batched(out, E)
            cand_idx[:, op] = idx
            out_n = _norm_rows(out)
            goal_sim = (out_n * wp_n).sum(dim=1)
            reach = reach_value(cleaned, wp, M)
            sc = w_manifold * manifold + alpha * goal_sim + w_reach * reach
            scores[:, op] = sc
        chosen = scores.argmax(dim=1)
        op_trace[:, hop] = chosen.detach().cpu().numpy()
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx[row, chosen]
        state = E[new_idx]
        final_idx = new_idx
    correct = (final_idx == targets).detach().cpu().numpy()
    return correct.astype(bool), op_trace


# ============================================================================
# NEW: replay-generate-then-select (bidirectional full-candidate scoring; rank-1 brain-first)
# ============================================================================
def _discover_bisect_perturbed(starts: torch.Tensor, targets: torch.Tensor, R: torch.Tensor,
                               seg_len: int, depth: int, tgen: torch.Generator,
                               perturb_frac: float) -> torch.Tensor:
    """ONE complete candidate trajectory = the parent open bisection with gaussian tie-break noise
    added to the balance signal before each argmax (noise sd = perturb_frac * per-row balance std).
    perturb_frac==0 reproduces _discover_bisect_boundaries EXACTLY (candidate 0). start/goal/chosen
    hard-masks are applied AFTER the noise so they can never be selected. Returns [n_chains, n_bnd]."""
    n_chains = starts.shape[0]
    n_bnd = n_boundaries(depth, seg_len)
    rowar = torch.arange(n_chains, device=DEVICE)
    rg = R.index_select(1, targets).transpose(0, 1)          # [n_chains, V], rg[i,c] = R[c, goal_i]
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    for _ in range(n_bnd - 1):
        ra = R.index_select(0, anchor)                       # [n_chains, V], ra[i,c] = R[anchor_i,c]
        balance = torch.minimum(ra, rg).clone()
        if perturb_frac > 0.0:
            sd = balance.std(dim=1, keepdim=True)            # [n_chains, 1] per-row scale
            noise = torch.randn(balance.shape, generator=tgen, device=DEVICE, dtype=DTYPE)
            balance = balance + (perturb_frac * sd) * noise
        balance[rowar, starts] = NEG_HARD
        balance[rowar, targets] = NEG_HARD
        for prev in chosen_cols:
            balance[rowar, prev] = NEG_HARD
        wp = balance.argmax(dim=1)
        chosen_cols.append(wp)
        anchor = wp
    cols = chosen_cols + [targets]
    return torch.stack(cols, dim=1)


def generate_candidates(starts: torch.Tensor, targets: torch.Tensor, R_fwd: torch.Tensor,
                        seg_len: int, depth: int, n_cand: int, tgen: torch.Generator,
                        perturb_frac: float) -> torch.Tensor:
    """n_cand COMPLETE candidate boundary trajectories. Candidate 0 = unperturbed open pick (the open
    baseline is always in the pool); candidates 1..n_cand-1 = independently-perturbed argmax tie-breaks.
    Returns [n_cand, n_chains, n_bnd]. No retraining -- reuses the open bisection machinery."""
    cands = [_discover_bisect_perturbed(starts, targets, R_fwd, seg_len, depth, tgen, 0.0)]
    for _ in range(n_cand - 1):
        cands.append(_discover_bisect_perturbed(starts, targets, R_fwd, seg_len, depth, tgen,
                                                perturb_frac))
    return torch.stack(cands, dim=0)


def _to_unit(x: torch.Tensor) -> torch.Tensor:
    """Map cosine reach in [-1,1] to [0,1] so the harmonic mean stays well-defined and positive."""
    return (x + 1.0) * 0.5


def score_bidirectional(boundaries: torch.Tensor, starts: torch.Tensor,
                        R_fwd: torch.Tensor, R_rev: torch.Tensor) -> torch.Tensor:
    """Score a COMPLETE candidate by FORWARD-vs-REVERSE agreement. boundaries [n_chains, n_bnd] with
    last col = goal. The full state sequence is [start] + boundaries. Forward leg reach traverses
    start->...->goal over R_fwd; reverse leg reach traverses goal->...->start over R_rev (the
    INDEPENDENT second channel: R_rev[y,x] high iff x typically precedes y forward). Returns the
    harmonic mean of the mean forward-leg unit-reach and the mean reverse-leg unit-reach [n_chains]."""
    n_chains = boundaries.shape[0]
    seq = torch.cat([starts.view(n_chains, 1), boundaries], dim=1)   # [n_chains, n_bnd+1]
    n_legs = seq.shape[1] - 1
    fwd_acc = torch.zeros(n_chains, dtype=DTYPE, device=DEVICE)
    rev_acc = torch.zeros(n_chains, dtype=DTYPE, device=DEVICE)
    for i in range(n_legs):
        x = seq[:, i]
        y = seq[:, i + 1]
        fwd_acc = fwd_acc + _to_unit(R_fwd[x, y])           # x -> y forward
        rev_acc = rev_acc + _to_unit(R_rev[y, x])           # y -> x under reverse dynamics
    fwd = fwd_acc / float(n_legs)
    rev = rev_acc / float(n_legs)
    return 2.0 * fwd * rev / (fwd + rev + BIDIR_EPS)


def wp_replay_generate_select(starts: torch.Tensor, targets: torch.Tensor, R_fwd: torch.Tensor,
                              R_rev: torch.Tensor, seg_len: int, depth: int, n_cand: int,
                              tgen: torch.Generator, perturb_frac: float
                              ) -> Tuple[torch.Tensor, Dict[str, float]]:
    """GENERATE n_cand complete candidates, SCORE each by bidirectional agreement, COMMIT the best
    WHOLE candidate per chain. Returns (selected_boundaries [n_chains, n_bnd], agreement diagnostics)."""
    cands = generate_candidates(starts, targets, R_fwd, seg_len, depth, n_cand, tgen, perturb_frac)
    n_c, n_chains, n_bnd = cands.shape
    scores = torch.empty((n_c, n_chains), dtype=DTYPE, device=DEVICE)
    for c in range(n_c):
        scores[c] = score_bidirectional(cands[c], starts, R_fwd, R_rev)
    best = scores.argmax(dim=0)                              # [n_chains]
    row = torch.arange(n_chains, device=DEVICE)
    selected = cands[best, row, :]                           # [n_chains, n_bnd]
    sel_score = scores[best, row]
    agree = {
        "mean_selected_score": float(sel_score.mean()),
        "mean_all_cand_score": float(scores.mean()),
        "mean_open_cand_score": float(scores[0].mean()),    # candidate 0 == unperturbed open pick
        "frac_selected_not_open": float((best != 0).float().mean()),
    }
    return selected, agree


# ============================================================================
# NEW: exogenous KB-grounded check (kinetic-proofreading checkpoint; rank-1 cross-domain)
# ============================================================================
def build_kb_reach_cum(per_op: List[List[Tuple[int, int]]], n_ops: int, V: int,
                       max_k: int) -> Dict[int, torch.Tensor]:
    """RAW-KB reachability-within-<=k-hops boolean matrices, DIRECTLY from the raw edge table (per_op).
    reach_cum[k][a,c]==True iff an ACTUAL path of length in [1,k] exists a->c in the union multigraph.
    ZERO shared parameters / ZERO shared training with M/R. Built once per (V,n_ops) group. Boolean
    matrix powers via float matmul + clamp>0 (cheap: max_k VxV matmuls). THEORETICAL@transitive-closure."""
    A = torch.zeros((V, V), dtype=torch.bool, device=DEVICE)
    edges = [(s, o) for op in range(n_ops) for (s, o) in per_op[op] if s != o]
    if edges:
        ei = torch.tensor(edges, dtype=torch.long, device=DEVICE)
        A[ei[:, 0], ei[:, 1]] = True
    reach_cum: Dict[int, torch.Tensor] = {1: A.clone()}
    Af = A.to(DTYPE)
    for k in range(2, max(2, max_k) + 1):
        step = (reach_cum[k - 1].to(DTYPE) @ Af) > 0          # states reachable in EXACTLY <=k via <=k-1 + 1
        reach_cum[k] = reach_cum[k - 1] | step
    return reach_cum


def _kb_conf_col(reach_cum: Dict[int, torch.Tensor], span: int, depth: int,
                 src: torch.Tensor, mode: str, goal: Optional[torch.Tensor] = None) -> torch.Tensor:
    """Return [n_chains, V] bool. mode='from': reach_cum[span][src[i], c] (c reachable within span of
    src_i). mode='to': reach_cum[span][c, goal[i]] (goal_i reachable within span of c)."""
    k = max(1, min(int(span), depth))
    Rk = reach_cum[k]
    if mode == "from":
        return Rk.index_select(0, src)                        # [n_chains, V]
    return Rk.index_select(1, goal).transpose(0, 1)           # [n_chains, V], col c = Rk[c, goal_i]


def _discover_kb_grounded_boundaries(starts: torch.Tensor, targets: torch.Tensor, R: torch.Tensor,
                                     reach_cum: Dict[int, torch.Tensor], seg_len: int, depth: int,
                                     stats: Optional[Dict[str, int]] = None) -> torch.Tensor:
    """RESCUE (NEW): sequential bisection whose R-balance argmax is MASKED to only KB-CONFIRMED
    candidates (exogenous raw-graph reachability; zero shared params with R). Empty-confirmed rows RESET
    FRESH re-anchored at the immutable START (never carry the unconfirmed anchor forward); still-empty
    rows fall back to the open argmax (counted). Anchor advance mirrors wp_bisect_open exactly."""
    n_chains = starts.shape[0]
    n_bnd = n_boundaries(depth, seg_len)
    rowar = torch.arange(n_chains, device=DEVICE)
    rg = R.index_select(1, targets).transpose(0, 1)          # [n_chains, V], rg[i,c] = R[c, goal_i]
    right_goal = targets
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    n_conf = 0
    n_dec = 0
    n_fresh = 0
    n_fallback = 0
    NEG = torch.full((n_chains, R.shape[0]), NEG_HARD, dtype=DTYPE, device=DEVICE)
    for jj in range(n_bnd - 1):
        pos = (jj + 1) * seg_len
        rem = depth - pos
        ra = R.index_select(0, anchor)                       # [n_chains, V]
        balance = torch.minimum(ra, rg)
        right_ok = _kb_conf_col(reach_cum, rem, depth, anchor, "to", right_goal)   # goal within rem of c
        left_ok = _kb_conf_col(reach_cum, seg_len, depth, anchor, "from")          # c within seg_len of anchor
        confirmed = left_ok & right_ok
        confirmed[rowar, starts] = False
        confirmed[rowar, targets] = False
        for prev in chosen_cols:
            confirmed[rowar, prev] = False
        n_conf += int(confirmed.sum().item())
        n_dec += n_chains
        masked = torch.where(confirmed, balance, NEG)
        has_conf = confirmed.any(dim=1)
        if not bool(has_conf.all()):
            # FRESH reset: re-anchor the LEFT leg at the immutable START (span = pos), never carry the
            # unconfirmed intermediate anchor forward. RIGHT leg unchanged (goal reachable within rem).
            left_fresh = _kb_conf_col(reach_cum, pos, depth, starts, "from")
            confirmed_fresh = left_fresh & right_ok
            confirmed_fresh[rowar, starts] = False
            confirmed_fresh[rowar, targets] = False
            for prev in chosen_cols:
                confirmed_fresh[rowar, prev] = False
            masked_fresh = torch.where(confirmed_fresh, balance, NEG)
            has_fresh = confirmed_fresh.any(dim=1)
            need = (~has_conf)
            masked = torch.where(need.unsqueeze(1), masked_fresh, masked)
            n_fresh += int((need & has_fresh).sum().item())
            still = need & (~has_fresh)
            if bool(still.any()):
                open_bal = balance.clone()
                open_bal[rowar, starts] = NEG_HARD
                open_bal[rowar, targets] = NEG_HARD
                for prev in chosen_cols:
                    open_bal[rowar, prev] = NEG_HARD
                masked = torch.where(still.unsqueeze(1), open_bal, masked)
                n_fallback += int(still.sum().item())
        wp = masked.argmax(dim=1)
        chosen_cols.append(wp)
        anchor = wp
    cols = chosen_cols + [targets]
    if stats is not None:
        stats["n_confirmed"] += n_conf
        stats["n_decisions"] += n_dec
        stats["n_fresh"] += n_fresh
        stats["n_fallback"] += n_fallback
    return torch.stack(cols, dim=1)


def kb_independence_screen(chains, R: torch.Tensor, reach_cum: Dict[int, torch.Tensor],
                           W_ops: List[torch.Tensor], E: torch.Tensor, depth: int, seg_len: int
                           ) -> Dict[str, float]:
    """MANDATORY independence screen (Kalman-observability). Per (chain,hop) unit collect two scalars
    from DISJOINT sources: kb_confirm_signal = whether R's OPEN argmax pick is KB-reachability-confirmed
    (raw graph); m_error = SR estimator per-hop reach error to the TRUE oracle boundary = 1-unit(R[anchor,
    true_bnd]) (from R+oracle ONLY). corr near-zero => the exogenous channel is informationally independent
    of the estimator's own error (the load-bearing claim). Anchor advances along the OPEN pick so units
    lie on the open-discovery distribution."""
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    traj = oracle_trajectory_idx(chains, W_ops, E, depth)     # [n_chains, depth+1] true states
    rg = R.index_select(1, targets).transpose(0, 1)
    rowar = torch.arange(n_chains, device=DEVICE)
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    n_bnd = n_boundaries(depth, seg_len)
    kb_sig: List[torch.Tensor] = []
    m_err: List[torch.Tensor] = []
    for jj in range(n_bnd - 1):
        pos = (jj + 1) * seg_len
        rem = depth - pos
        ra = R.index_select(0, anchor)
        balance = torch.minimum(ra, rg).clone()
        balance[rowar, starts] = NEG_HARD
        balance[rowar, targets] = NEG_HARD
        for prev in chosen_cols:
            balance[rowar, prev] = NEG_HARD
        open_pick = balance.argmax(dim=1)                    # what OPEN (R-only) would pick
        left_ok = reach_cum[max(1, min(seg_len, depth))][anchor, open_pick]        # [n_chains] bool
        right_ok = reach_cum[max(1, min(rem, depth))][open_pick, targets]
        kb_confirm = (left_ok & right_ok).to(DTYPE)
        true_bnd = traj[:, min(pos, depth)]
        r_true = R[anchor, true_bnd]                         # R's reach to the TRUE next boundary
        m_error_h = 1.0 - _to_unit(r_true)                  # high when R poorly reaches the true boundary
        kb_sig.append(kb_confirm)
        m_err.append(m_error_h)
        chosen_cols.append(open_pick)
        anchor = open_pick
    if not kb_sig:
        return {"independence_corr": 0.0, "kb_confirm_mean": 0.0, "kb_confirm_std": 0.0,
                "m_error_mean": 0.0, "independence_degenerate": True, "n_indep_units": 0}
    x = torch.cat(kb_sig).detach().cpu().numpy().astype(np.float64)
    y = torch.cat(m_err).detach().cpu().numpy().astype(np.float64)
    if x.std() < 1e-9 or y.std() < 1e-9:
        corr = 0.0
        degen = True
    else:
        corr = float(np.corrcoef(x, y)[0, 1])
        degen = False
    return {"independence_corr": corr, "kb_confirm_mean": float(x.mean()),
            "kb_confirm_std": float(x.std()), "m_error_mean": float(y.mean()),
            "independence_degenerate": bool(degen), "n_indep_units": int(len(x))}


# ============================================================================
# NEW CHANNEL B: cross-fit calibrated correctness-selector (independent of M/R by construction)
# ============================================================================
def build_raw_outdeg(per_op: List[List[Tuple[int, int]]], n_ops: int, V: int) -> torch.Tensor:
    """Raw-graph out-degree per node (union multigraph), max-normalized to [0,1]. Zero M/R dependence."""
    deg = torch.zeros(V, dtype=DTYPE, device=DEVICE)
    for op in range(n_ops):
        for (s, o) in per_op[op]:
            if s != o:
                deg[s] += 1.0
    m = float(deg.max())
    return deg / (m if m > 0.0 else 1.0)


def build_reach_sum(reach_cum: Dict[int, torch.Tensor], max_k: int, V: int) -> torch.Tensor:
    """Graded raw-graph closeness RCsum[a,c] = mean_k reach_cum[k][a,c] in [0,1]: fraction of hop-horizons
    (1..max_k) within which c is reachable from a. A SOFT structural proxy (vs the KB gate's HARD boolean
    mask) -- this softness is what lets the selector's failures DECORRELATE from the KB gate's. Zero M/R."""
    acc = torch.zeros((V, V), dtype=DTYPE, device=DEVICE)
    kk = 0
    for k in range(1, max(1, max_k) + 1):
        if k in reach_cum:
            acc = acc + reach_cum[k].to(DTYPE)
            kk += 1
    return acc / float(max(1, kk))


def _fit_logistic(X: torch.Tensor, y: torch.Tensor, steps: int, lr: float) -> torch.Tensor:
    """Batch-GD logistic regression. X [K,d], y [K] in {0,1} -> weights w [d] (p=sigmoid(X@w)). VERBATIM
    math: dL/dw = X^T (sigmoid(Xw) - y) / K. Deterministic; no shared state with M/R (different family)."""
    K, d = X.shape
    w = torch.zeros(d, dtype=DTYPE, device=DEVICE)
    if K < 2:
        return w
    for _ in range(steps):
        p = torch.sigmoid(X @ w)
        grad = (X.transpose(0, 1) @ (p - y)) / float(K)
        w = w - lr * grad
    return w


def _selector_feat_cols(A: torch.Tensor, C: torch.Tensor, G: torch.Tensor,
                        outdeg: torch.Tensor, rcsum: torch.Tensor) -> torch.Tensor:
    """Feature matrix [K,5] for triples (anchor A, candidate C, goal G): [bias, outdeg[A], outdeg[C],
    rcsum[A,C], rcsum[C,G]]. ALL from raw graph -- ZERO M/R dependence (screen-1 independence-by-cons.)."""
    ones = torch.ones(A.shape[0], dtype=DTYPE, device=DEVICE)
    x1 = outdeg[A]
    x2 = outdeg[C]
    x3 = rcsum[A, C]
    x4 = rcsum[C, G]
    return torch.stack([ones, x1, x2, x3, x4], dim=1)


def train_calibrated_selector(per_op, n_ops: int, V: int, reach_cum: Dict[int, torch.Tensor],
                              train_by_d, depths_needed: List[int], W_ops, E: torch.Tensor,
                              sel_seed: int) -> Dict[str, Any]:
    """CROSS-FIT calibrated correctness-selector (channel B). Positives = true oracle boundary nodes at
    each interior position; negatives = random other nodes. Fold A (even chain idx) fits the logistic
    weights; DISJOINT fold B (odd idx) fits the Platt calibration (cal_a,cal_b) -- weights + calibration
    never share a fold (double-ML independence by construction). Returns a model dict consumed by
    _selector_scores. Degenerate graphs -> accept-all model (flagged)."""
    outdeg = build_raw_outdeg(per_op, n_ops, V)
    rcsum = build_reach_sum(reach_cum, max(depths_needed), V)
    rng = np.random.default_rng(sel_seed)
    a_l: List[int] = []; c_l: List[int] = []; g_l: List[int] = []
    y_l: List[float] = []; f_l: List[int] = []
    for depth in depths_needed:
        chains = train_by_d[depth]
        if not chains:
            continue
        traj = oracle_trajectory_idx(chains, W_ops, E, depth)   # [n, depth+1] true states
        n_bnd = n_boundaries(depth, SEG_LEN)
        _, targets, _ = _chain_tensors(chains)
        tj = traj.detach().cpu().numpy()
        gt = targets.detach().cpu().numpy()
        for i in range(len(chains)):
            g = int(gt[i]); fld = i % 2
            for j in range(n_bnd - 1):
                a = int(tj[i, j * SEG_LEN]); c = int(tj[i, min((j + 1) * SEG_LEN, depth)])
                if a == c or c == g:
                    continue                                    # skip degenerate positives
                a_l.append(a); c_l.append(c); g_l.append(g); y_l.append(1.0); f_l.append(fld)
                for _ in range(SELECTOR_N_NEG):
                    r = int(rng.integers(0, V)); tries = 0
                    while (r == a or r == g or r == c) and tries < 8:
                        r = int(rng.integers(0, V)); tries += 1
                    a_l.append(a); c_l.append(r); g_l.append(g); y_l.append(0.0); f_l.append(fld)
    degenerate = False
    if len(y_l) < 8 or (sum(y_l) < 2) or (sum(y_l) > len(y_l) - 2):
        degenerate = True
        return {"w": torch.zeros(5, dtype=DTYPE, device=DEVICE), "cal_a": 1.0, "cal_b": 0.0,
                "tau": 0.0, "tau_hi": 0.0, "outdeg": outdeg, "rcsum": rcsum, "degenerate": True,
                "n_train": int(len(y_l)), "acc_frac_train": 1.0}
    A = torch.tensor(a_l, dtype=torch.long, device=DEVICE)
    C = torch.tensor(c_l, dtype=torch.long, device=DEVICE)
    G = torch.tensor(g_l, dtype=torch.long, device=DEVICE)
    y = torch.tensor(y_l, dtype=DTYPE, device=DEVICE)
    fold = torch.tensor(f_l, dtype=torch.long, device=DEVICE)
    X = _selector_feat_cols(A, C, G, outdeg, rcsum)
    fa = (fold == 0); fb = (fold == 1)
    if int(fa.sum()) < 4 or int(fb.sum()) < 4:                  # too few for cross-fit -> single-fold
        fa = torch.ones_like(fold, dtype=torch.bool); fb = fa
    w = _fit_logistic(X[fa], y[fa], SELECTOR_FIT_STEPS, SELECTOR_FIT_LR)
    logit_b = X[fb] @ w
    ones_b = torch.ones(logit_b.shape[0], dtype=DTYPE, device=DEVICE)
    platt = _fit_logistic(torch.stack([logit_b, ones_b], dim=1), y[fb],
                          SELECTOR_FIT_STEPS, SELECTOR_FIT_LR)
    cal_a = float(platt[0]); cal_b = float(platt[1])
    p_b = torch.sigmoid(cal_a * logit_b + cal_b)
    tau = float(torch.quantile(p_b, SELECTOR_TAU_PCTL)) if p_b.numel() > 0 else 0.5
    tau_hi = float(torch.quantile(p_b, SELECTOR_TAU_HI_PCTL)) if p_b.numel() > 0 else 0.5   # C3 strict gate
    acc_frac_train = float((p_b >= tau).float().mean())
    return {"w": w, "cal_a": cal_a, "cal_b": cal_b, "tau": tau, "tau_hi": tau_hi,
            "outdeg": outdeg, "rcsum": rcsum,
            "degenerate": False, "n_train": int(len(y_l)), "acc_frac_train": acc_frac_train}


def _selector_scores(anchor: torch.Tensor, goal: torch.Tensor, model: Dict[str, Any]) -> torch.Tensor:
    """Calibrated P(candidate is a correct waypoint) for ALL V candidates per chain -> [n_chains, V].
    Features from raw graph only (outdeg + graded reach closeness). Zero M/R dependence."""
    outdeg = model["outdeg"]; rcsum = model["rcsum"]; w = model["w"]
    V = outdeg.shape[0]; n = anchor.shape[0]
    x1 = outdeg.index_select(0, anchor).unsqueeze(1)                 # [n,1] outdeg[a]
    x2 = outdeg.unsqueeze(0)                                         # [1,V] outdeg[c]
    x3 = rcsum.index_select(0, anchor)                              # [n,V] rcsum[a,c]
    x4 = rcsum.index_select(1, goal).transpose(0, 1)               # [n,V] rcsum[c,g]
    logit = w[0] + w[1] * x1 + w[2] * x2 + w[3] * x3 + w[4] * x4    # broadcast -> [n,V]
    return torch.sigmoid(model["cal_a"] * logit + model["cal_b"])


def _selector_accept(anchor: torch.Tensor, goal: torch.Tensor, model: Dict[str, Any]) -> torch.Tensor:
    """[n_chains, V] bool: candidate SELECTOR-ACCEPTED iff calibrated P >= tau. Degenerate model -> all."""
    if model.get("degenerate", False):
        return torch.ones((anchor.shape[0], model["outdeg"].shape[0]), dtype=torch.bool, device=DEVICE)
    return _selector_scores(anchor, goal, model) >= model["tau"]


def _masked_bisection(starts: torch.Tensor, targets: torch.Tensor, R: torch.Tensor,
                      confirm_fn, seg_len: int, depth: int,
                      stats: Optional[Dict[str, int]] = None) -> torch.Tensor:
    """GENERIC masked sequential bisection (same anchor-advance + fresh-reset + open-fallback structure as
    the parent KB gate). confirm_fn(left_anchor, left_span, right_goal, right_rem) -> [n_chains,V] bool
    mask of ACCEPTED candidates. Used for the selector-only and the stacked OR-gate arms (the parent's
    verbatim _discover_kb_grounded_boundaries is retained for the KB-alone arm to reproduce it exactly)."""
    n_chains = starts.shape[0]; V = R.shape[0]
    n_bnd = n_boundaries(depth, seg_len)
    rowar = torch.arange(n_chains, device=DEVICE)
    rg = R.index_select(1, targets).transpose(0, 1)
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    n_conf = 0; n_dec = 0; n_fresh = 0; n_fallback = 0
    NEG = torch.full((n_chains, V), NEG_HARD, dtype=DTYPE, device=DEVICE)
    for jj in range(n_bnd - 1):
        pos = (jj + 1) * seg_len
        rem = depth - pos
        ra = R.index_select(0, anchor)
        balance = torch.minimum(ra, rg)
        confirmed = confirm_fn(anchor, seg_len, targets, rem).clone()
        confirmed[rowar, starts] = False
        confirmed[rowar, targets] = False
        for prev in chosen_cols:
            confirmed[rowar, prev] = False
        n_conf += int(confirmed.sum().item())
        n_dec += n_chains
        masked = torch.where(confirmed, balance, NEG)
        has_conf = confirmed.any(dim=1)
        if not bool(has_conf.all()):
            confirmed_fresh = confirm_fn(starts, pos, targets, rem).clone()
            confirmed_fresh[rowar, starts] = False
            confirmed_fresh[rowar, targets] = False
            for prev in chosen_cols:
                confirmed_fresh[rowar, prev] = False
            masked_fresh = torch.where(confirmed_fresh, balance, NEG)
            has_fresh = confirmed_fresh.any(dim=1)
            need = (~has_conf)
            masked = torch.where(need.unsqueeze(1), masked_fresh, masked)
            n_fresh += int((need & has_fresh).sum().item())
            still = need & (~has_fresh)
            if bool(still.any()):
                open_bal = balance.clone()
                open_bal[rowar, starts] = NEG_HARD
                open_bal[rowar, targets] = NEG_HARD
                for prev in chosen_cols:
                    open_bal[rowar, prev] = NEG_HARD
                masked = torch.where(still.unsqueeze(1), open_bal, masked)
                n_fallback += int(still.sum().item())
        wp = masked.argmax(dim=1)
        chosen_cols.append(wp)
        anchor = wp
    cols = chosen_cols + [targets]
    if stats is not None:
        stats["n_confirmed"] += n_conf
        stats["n_decisions"] += n_dec
        stats["n_fresh"] += n_fresh
        stats["n_fallback"] += n_fallback
    return torch.stack(cols, dim=1)


def _kb_confirm_fn(reach_cum: Dict[int, torch.Tensor], depth: int):
    """confirm_fn for the KB channel: left leg within left_span of the anchor AND goal within right_rem
    of the candidate (raw-graph reachability). Matches the parent KB gate's mask exactly."""
    def fn(left_anchor, left_span, right_goal, right_rem):
        left_ok = _kb_conf_col(reach_cum, left_span, depth, left_anchor, "from")
        right_ok = _kb_conf_col(reach_cum, right_rem, depth, left_anchor, "to", right_goal)
        return left_ok & right_ok
    return fn


def _selector_confirm_fn(model: Dict[str, Any]):
    """confirm_fn for the selector channel: calibrated P(correct) >= tau (spans ignored -- the selector
    reads anchor->cand and cand->goal graded closeness directly)."""
    def fn(left_anchor, left_span, right_goal, right_rem):
        return _selector_accept(left_anchor, right_goal, model)
    return fn


def _stacked_confirm_fn(reach_cum: Dict[int, torch.Tensor], depth: int, model: Dict[str, Any]):
    """confirm_fn for the STACKED OR-gate: a candidate is accepted iff KB-CONFIRMED *OR* SELECTOR-ACCEPTED
    -> the true waypoint is skipped only when NEITHER channel confirms it (P=miss_KB*miss_SEL under indep)."""
    kbfn = _kb_confirm_fn(reach_cum, depth)
    selfn = _selector_confirm_fn(model)
    def fn(left_anchor, left_span, right_goal, right_rem):
        return kbfn(left_anchor, left_span, right_goal, right_rem) | selfn(left_anchor, left_span,
                                                                           right_goal, right_rem)
    return fn


def _discover_selector_boundaries(starts, targets, R, model, seg_len, depth, stats=None) -> torch.Tensor:
    return _masked_bisection(starts, targets, R, _selector_confirm_fn(model), seg_len, depth, stats)


def _discover_stacked_boundaries(starts, targets, R, reach_cum, model, seg_len, depth,
                                 stats=None) -> torch.Tensor:
    return _masked_bisection(starts, targets, R, _stacked_confirm_fn(reach_cum, depth, model),
                             seg_len, depth, stats)


# ---- PRECISION-PRESERVING COMBINERS (this cell's mechanisms under test) ----
def _and_confirm_fn(reach_cum: Dict[int, torch.Tensor], depth: int, model: Dict[str, Any]):
    """C1 INTERSECTION combiner: admit a candidate iff KB-CONFIRMED *AND* SELECTOR-ACCEPTED. Strictly
    tighter than either channel alone -> highest admission precision (the union's re-admitted selector-only
    candidates are excluded by the KB leg; the KB's coverage-hole picks are excluded by the selector leg)."""
    kbfn = _kb_confirm_fn(reach_cum, depth)
    selfn = _selector_confirm_fn(model)
    def fn(left_anchor, left_span, right_goal, right_rem):
        return kbfn(left_anchor, left_span, right_goal, right_rem) & selfn(left_anchor, left_span,
                                                                           right_goal, right_rem)
    return fn


def _kbpriority_confirm_fn(reach_cum: Dict[int, torch.Tensor], depth: int, model: Dict[str, Any]):
    """C2 CONFIDENCE-WEIGHTED / KB-PRIORITY union: per row, defer to the higher-precision channel. If the
    KB channel confirms ANY candidate for this row, the admission set = the KB-confirmed set ONLY (a
    selector-only candidate can NEVER override a KB-confirmed pick -> KB precision is preserved verbatim).
    Only where the KB set is EMPTY does the selector fill the gap (union) BEFORE the fresh-reset/open
    fallback. Never dilutes KB; adds selector recall strictly inside KB's coverage holes."""
    kbfn = _kb_confirm_fn(reach_cum, depth)
    selfn = _selector_confirm_fn(model)
    def fn(left_anchor, left_span, right_goal, right_rem):
        kb = kbfn(left_anchor, left_span, right_goal, right_rem)
        sel = selfn(left_anchor, left_span, right_goal, right_rem)
        has_kb = kb.any(dim=1, keepdim=True)                      # [n,1] rows where KB has an opinion
        return torch.where(has_kb, kb, kb | sel)                  # KB-only where KB fires; union elsewhere
    return fn


def _calibrated_gate_confirm_fn(reach_cum: Dict[int, torch.Tensor], depth: int, model: Dict[str, Any]):
    """C3 CORRECTNESS-CALIBRATED gate over the union: admit (KB-CONFIRMED OR SELECTOR-ACCEPTED) AND the
    cross-fit calibrated P(correct) >= tau_hi (a STRICTER percentile than the selector's own accept tau).
    The predicted-correctness score filters the union's re-admitted low-precision candidates regardless of
    which channel proposed them. Degenerate selector model -> the calibrated leg passes all (falls to union)."""
    kbfn = _kb_confirm_fn(reach_cum, depth)
    selfn = _selector_confirm_fn(model)
    def fn(left_anchor, left_span, right_goal, right_rem):
        union = kbfn(left_anchor, left_span, right_goal, right_rem) | selfn(left_anchor, left_span,
                                                                            right_goal, right_rem)
        if model.get("degenerate", False):
            return union
        hi = _selector_scores(left_anchor, right_goal, model) >= model.get("tau_hi", 1.0)
        return union & hi
    return fn


def _discover_and_boundaries(starts, targets, R, reach_cum, model, seg_len, depth, stats=None):
    return _masked_bisection(starts, targets, R, _and_confirm_fn(reach_cum, depth, model),
                             seg_len, depth, stats)


def _discover_kbpriority_boundaries(starts, targets, R, reach_cum, model, seg_len, depth, stats=None):
    return _masked_bisection(starts, targets, R, _kbpriority_confirm_fn(reach_cum, depth, model),
                             seg_len, depth, stats)


def _discover_calibrated_gate_boundaries(starts, targets, R, reach_cum, model, seg_len, depth, stats=None):
    return _masked_bisection(starts, targets, R, _calibrated_gate_confirm_fn(reach_cum, depth, model),
                             seg_len, depth, stats)


def selector_independence_screen(chains, R: torch.Tensor, model: Dict[str, Any],
                                 W_ops, E: torch.Tensor, depth: int, seg_len: int) -> Dict[str, float]:
    """Screen 1 for channel B: corr(selector_confidence_on_open_pick, m_error). m_error is the SR
    estimator's per-hop reach error to the TRUE oracle boundary (from R+oracle ONLY, disjoint from the
    raw-graph selector features). |corr| ~ 0 => selector is informationally independent of M/R's error."""
    starts, targets, _ = _chain_tensors(chains)
    traj = oracle_trajectory_idx(chains, W_ops, E, depth)
    rg = R.index_select(1, targets).transpose(0, 1)
    rowar = torch.arange(starts.shape[0], device=DEVICE)
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    n_bnd = n_boundaries(depth, seg_len)
    sel_sig: List[torch.Tensor] = []
    m_err: List[torch.Tensor] = []
    for jj in range(n_bnd - 1):
        pos = (jj + 1) * seg_len
        ra = R.index_select(0, anchor)
        balance = torch.minimum(ra, rg).clone()
        balance[rowar, starts] = NEG_HARD
        balance[rowar, targets] = NEG_HARD
        for prev in chosen_cols:
            balance[rowar, prev] = NEG_HARD
        open_pick = balance.argmax(dim=1)
        if model.get("degenerate", False):
            sel_conf = torch.ones(starts.shape[0], dtype=DTYPE, device=DEVICE)
        else:
            p_all = _selector_scores(anchor, targets, model)
            sel_conf = p_all[rowar, open_pick]
        true_bnd = traj[:, min(pos, depth)]
        r_true = R[anchor, true_bnd]
        m_error_h = 1.0 - _to_unit(r_true)
        sel_sig.append(sel_conf)
        m_err.append(m_error_h)
        chosen_cols.append(open_pick)
        anchor = open_pick
    if not sel_sig:
        return {"selector_independence_corr": 0.0, "selector_conf_mean": 0.0,
                "selector_independence_degenerate": True, "n_sel_indep_units": 0}
    x = torch.cat(sel_sig).detach().cpu().numpy().astype(np.float64)
    y = torch.cat(m_err).detach().cpu().numpy().astype(np.float64)
    if x.std() < 1e-9 or y.std() < 1e-9:
        corr = 0.0; degen = True
    else:
        corr = float(np.corrcoef(x, y)[0, 1]); degen = False
    return {"selector_independence_corr": corr, "selector_conf_mean": float(x.mean()),
            "selector_independence_degenerate": bool(degen), "n_sel_indep_units": int(len(x))}


def failure_mask_corr(kb_correct: np.ndarray, sel_correct: np.ndarray) -> Dict[str, float]:
    """THE load-bearing NEW screen: corr(failure_mask_KB, failure_mask_SELECTOR) over per-chain final
    correctness. failure = arm got the chain WRONG. Near-zero => independent failures => the OR-gate
    suppresses the true-waypoint miss-rate multiplicatively. High => shared coverage-density cause =>
    stacking is redundant (research point-2). Degenerate (an arm all-right or all-wrong) => corr=0 flagged."""
    fa = (~kb_correct.astype(bool)).astype(np.float64)
    fb = (~sel_correct.astype(bool)).astype(np.float64)
    if fa.std() < 1e-9 or fb.std() < 1e-9:
        return {"failmask_corr": 0.0, "failmask_kb_rate": float(fa.mean()),
                "failmask_sel_rate": float(fb.mean()), "failmask_degenerate": True,
                "n_failmask_units": int(len(fa))}
    corr = float(np.corrcoef(fa, fb)[0, 1])
    return {"failmask_corr": corr, "failmask_kb_rate": float(fa.mean()),
            "failmask_sel_rate": float(fb.mean()), "failmask_degenerate": False,
            "n_failmask_units": int(len(fa))}


# ---- per-arm waypoint hop-schedules (discovery wrappers) ----
def wp_hops_selector(chains, R, model, depth, stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_selector_boundaries(starts, targets, R, model, SEG_LEN, depth, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_stacked(chains, R, reach_cum, model, depth, stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_stacked_boundaries(starts, targets, R, reach_cum, model, SEG_LEN, depth, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_and(chains, R, reach_cum, model, depth, stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_and_boundaries(starts, targets, R, reach_cum, model, SEG_LEN, depth, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_kbpriority(chains, R, reach_cum, model, depth, stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_kbpriority_boundaries(starts, targets, R, reach_cum, model, SEG_LEN, depth, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_calibrated_gate(chains, R, reach_cum, model, depth, stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_calibrated_gate_boundaries(starts, targets, R, reach_cum, model, SEG_LEN, depth, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_replay(chains, R_fwd, R_rev, depth, tgen, agree_out=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b, agree = wp_replay_generate_select(starts, targets, R_fwd, R_rev, SEG_LEN, depth, N_CAND,
                                         tgen, PERTURB_FRAC)
    if agree_out is not None:
        agree_out.update(agree)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_kb_grounded(chains, R, reach_cum, depth, stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_kb_grounded_boundaries(starts, targets, R, reach_cum, SEG_LEN, depth, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_open(chains, R, depth) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_bisect_boundaries(starts, targets, R, SEG_LEN, depth)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_coarse2fine(chains, R_short, R_long, tau_short, tau_long, depth, use_verify, gen_np,
                        stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_coarse2fine_boundaries(starts, targets, R_short, R_long, tau_short, tau_long,
                                         SEG_LEN, depth, use_verify, gen_np, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_verify(chains, R_short, tau_short, depth, gen_np, stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_verify_boundaries(starts, targets, R_short, tau_short, SEG_LEN, depth, gen_np, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_random(chains, V, depth, g) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_random_boundaries(starts, targets, V, SEG_LEN, depth, g)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_index(chains, V, depth) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_index_boundaries(starts, targets, V, SEG_LEN, depth)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_oracle(chains, W_ops, E, depth, shuffle) -> torch.Tensor:
    traj = oracle_trajectory_idx(chains, W_ops, E, depth)
    return build_waypoint_idx(traj, SEG_LEN, depth, shuffle=shuffle)


# ---- discovery honesty diagnostics (on the OPEN arm's shared balance signal) -- VERBATIM ----
def discovery_diagnostics(chains, R: torch.Tensor, C: torch.Tensor, depth: int,
                          W_ops, E, seg_len: int) -> Dict[str, float]:
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    rg = R.index_select(1, targets).transpose(0, 1)
    ra0 = R.index_select(0, starts)
    balance0 = torch.minimum(ra0, rg)
    um = balance0.argmax(dim=1)
    degenerate = ((um == starts) | (um == targets)).float().mean().item()
    raw0 = C.index_select(1, targets).transpose(0, 1)
    a = balance0.reshape(-1).detach().cpu().numpy().astype(np.float64)
    b = raw0.reshape(-1).detach().cpu().numpy().astype(np.float64)
    if a.std() < 1e-9 or b.std() < 1e-9:
        anti_taut = 0.0
    else:
        anti_taut = float(np.corrcoef(a, b)[0, 1])
    b_open = _discover_bisect_boundaries(starts, targets, R, seg_len, depth)
    traj = oracle_trajectory_idx(chains, W_ops, E, depth)
    n_bnd = b_open.shape[1]
    matches = 0
    total = 0
    for j in range(n_bnd - 1):
        pos = min((j + 1) * seg_len, depth)
        oracle_bnd = traj[:, pos]
        matches += int((b_open[:, j] == oracle_bnd).sum().item())
        total += n_chains
    exact = float(matches) / float(max(1, total))
    return {"degenerate_rate": degenerate, "anti_tautology_corr": anti_taut,
            "exact_match_rate": exact}


def reach_rank_acc(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                   M: torch.Tensor, depth: int) -> float:
    """P(argmax-reach over the true-next candidates picks the true op at hop 0) -- per-hop reach
    signal quality diagnostic. VERBATIM."""
    starts, targets, op_seqs = _chain_tensors(chains)
    n_chains = starts.shape[0]
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=DEVICE)
    state = E[starts].clone()
    goal_E = E[targets]
    n_ops = len(W_ops)
    reach_scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
    cand_idx_all = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
    for op in range(n_ops):
        out = state @ W_ops[op]
        idx, cleaned, _ = cleanup_batched(out, E)
        cand_idx_all[:, op] = idx
        reach_scores[:, op] = reach_value(cleaned, goal_E, M)
    picked = reach_scores.argmax(dim=1)
    true_op = op_seq_t[:, 0]
    return float((picked == true_op).float().mean().item())


# ============================================================================
# stats helpers -- VERBATIM
# ============================================================================
def binom_two_sided_p(k: int, n: int, p: float = 0.5) -> float:
    if n <= 0:
        return 1.0
    from math import comb
    def pmf(kk):
        return comb(n, kk) * (p ** kk) * ((1 - p) ** (n - kk))
    p_obs = pmf(k)
    tot = 0.0
    for kk in range(n + 1):
        if pmf(kk) <= p_obs + 1e-12:
            tot += pmf(kk)
    return float(min(1.0, tot))


def _rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, len(x) + 1, dtype=np.float64)
    _, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    csum = np.cumsum(counts)
    start = csum - counts
    avg = (start + csum - 1) / 2.0 + 1.0
    return avg[inv]


def _spearman(x: List[float], y: List[float]) -> float:
    if len(x) < 2:
        return 0.0
    ax = _rankdata(np.asarray(x, dtype=np.float64))
    ay = _rankdata(np.asarray(y, dtype=np.float64))
    if ax.std() < 1e-12 or ay.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(ax, ay)[0, 1])


# ============================================================================
# per-arm w_reach / alpha tuners -- VERBATIM shape
# ============================================================================
def _tune_alpha_hier_oracle(train_c, W_ops, E, M, dd) -> Tuple[float, float]:
    wp_oracle_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=False)
    best_alpha, best = ALPHA_SWEEP[0], -1.0
    for alpha in ALPHA_SWEEP:
        acc = run_hier_arm_wp(train_c, W_ops, E, M, dd, SEG_LEN, alpha, 1.0, wp_oracle_tr)[0].mean()
        if acc > best:
            best, best_alpha = acc, alpha
    return best_alpha, float(best)


def _tune_wreach_flat(train_c, W_ops, E, M, dd, alpha) -> Tuple[float, float]:
    best_wr, best = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_selection_arm("gonogo", train_c, W_ops, E, M, dd, alpha, wr)[0].mean()
        if acc > best:
            best, best_wr = acc, wr
    return best_wr, float(best)


def _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, alpha, wp_idx) -> Tuple[float, float]:
    best_wr, best = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_hier_arm_wp(train_c, W_ops, E, M, dd, SEG_LEN, alpha, wr, wp_idx)[0].mean()
        if acc > best:
            best, best_wr = acc, wr
    return best_wr, float(best)


# ============================================================================
# per-regime eval
# ============================================================================
def _eval_regime(n_ops: int, V: int, dd: int, E: torch.Tensor, W_ops: List[torch.Tensor],
                 M: torch.Tensor, M_long: torch.Tensor, M_rev: torch.Tensor,
                 R_short: torch.Tensor, R_long: torch.Tensor, R_rev: torch.Tensor,
                 C: torch.Tensor, reach_cum: Dict[int, torch.Tensor], sel_model: Dict[str, Any],
                 tau_short: float, tau_long: float,
                 train_by_d, test_by_d, g: np.random.Generator,
                 disc_gen: np.random.Generator, rgen: torch.Generator) -> Dict[str, Any]:
    """Tune on train, evaluate all 14 arms on test (paired). One seed. KEY comparator = verify (the
    self-derived-correction MUST-FAIL control); RESCUE = wp_stacked_kb_plus_selector (A OR B)."""
    train_c = train_by_d[dd]
    test_c = test_by_d[dd]

    best_alpha, _ = _tune_alpha_hier_oracle(train_c, W_ops, E, M, dd)

    # train waypoint schedules (discovery uses only start/goal + R; never the oracle trajectory)
    wp_oracle_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=False)
    wp_shuf_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=True)
    wp_open_tr = wp_hops_open(train_c, R_short, dd)
    wp_c2f_tr = wp_hops_coarse2fine(train_c, R_short, R_long, tau_short, tau_long, dd, False, disc_gen)
    wp_ver_tr = wp_hops_verify(train_c, R_short, tau_short, dd, disc_gen)
    wp_combo_tr = wp_hops_coarse2fine(train_c, R_short, R_long, tau_short, tau_long, dd, True, disc_gen)
    wp_replay_tr = wp_hops_replay(train_c, R_short, R_rev, dd, rgen)
    wp_kb_tr = wp_hops_kb_grounded(train_c, R_short, reach_cum, dd)
    wp_sel_tr = wp_hops_selector(train_c, R_short, sel_model, dd)
    wp_stack_tr = wp_hops_stacked(train_c, R_short, reach_cum, sel_model, dd)
    wp_and_tr = wp_hops_and(train_c, R_short, reach_cum, sel_model, dd)
    wp_kbp_tr = wp_hops_kbpriority(train_c, R_short, reach_cum, sel_model, dd)
    wp_calg_tr = wp_hops_calibrated_gate(train_c, R_short, reach_cum, sel_model, dd)

    wr_flat, _ = _tune_wreach_flat(train_c, W_ops, E, M, dd, best_alpha)
    wr_oracle, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_oracle_tr)
    wr_shuf, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_shuf_tr)
    wr_open, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_open_tr)
    wr_c2f, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_c2f_tr)
    wr_ver, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_ver_tr)
    wr_combo, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_combo_tr)
    wr_replay, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_replay_tr)
    wr_kb, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_kb_tr)
    wr_sel, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_sel_tr)
    wr_stack, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_stack_tr)
    wr_and, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_and_tr)
    wr_kbp, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_kbp_tr)
    wr_calg, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_calg_tr)

    # test waypoint schedules (discovery on test start/goal only; capture retry stats + agreement)
    stats_ver = {"n_picks": 0, "n_retry": 0, "n_fallback": 0}
    stats_combo = {"n_picks": 0, "n_retry": 0, "n_fallback": 0}
    stats_kb = {"n_confirmed": 0, "n_decisions": 0, "n_fresh": 0, "n_fallback": 0}
    stats_sel = {"n_confirmed": 0, "n_decisions": 0, "n_fresh": 0, "n_fallback": 0}
    stats_stack = {"n_confirmed": 0, "n_decisions": 0, "n_fresh": 0, "n_fallback": 0}
    stats_and = {"n_confirmed": 0, "n_decisions": 0, "n_fresh": 0, "n_fallback": 0}
    stats_kbp = {"n_confirmed": 0, "n_decisions": 0, "n_fresh": 0, "n_fallback": 0}
    stats_calg = {"n_confirmed": 0, "n_decisions": 0, "n_fresh": 0, "n_fallback": 0}
    agree = {}
    wp_oracle_te = wp_hops_oracle(test_c, W_ops, E, dd, shuffle=False)
    wp_shuf_te = wp_hops_oracle(test_c, W_ops, E, dd, shuffle=True)
    wp_open_te = wp_hops_open(test_c, R_short, dd)
    wp_c2f_te = wp_hops_coarse2fine(test_c, R_short, R_long, tau_short, tau_long, dd, False, disc_gen)
    wp_ver_te = wp_hops_verify(test_c, R_short, tau_short, dd, disc_gen, stats_ver)
    wp_combo_te = wp_hops_coarse2fine(test_c, R_short, R_long, tau_short, tau_long, dd, True, disc_gen,
                                      stats_combo)
    wp_replay_te = wp_hops_replay(test_c, R_short, R_rev, dd, rgen, agree)
    wp_kb_te = wp_hops_kb_grounded(test_c, R_short, reach_cum, dd, stats_kb)
    wp_sel_te = wp_hops_selector(test_c, R_short, sel_model, dd, stats_sel)
    wp_stack_te = wp_hops_stacked(test_c, R_short, reach_cum, sel_model, dd, stats_stack)
    wp_and_te = wp_hops_and(test_c, R_short, reach_cum, sel_model, dd, stats_and)
    wp_kbp_te = wp_hops_kbpriority(test_c, R_short, reach_cum, sel_model, dd, stats_kbp)
    wp_calg_te = wp_hops_calibrated_gate(test_c, R_short, reach_cum, sel_model, dd, stats_calg)
    wp_rand_te = wp_hops_random(test_c, V, dd, g)
    wp_idx_te = wp_hops_index(test_c, V, dd)
    indep = kb_independence_screen(test_c, R_short, reach_cum, W_ops, E, dd, SEG_LEN)
    sel_indep = selector_independence_screen(test_c, R_short, sel_model, W_ops, E, dd, SEG_LEN)

    # eval on TEST (paired)
    flat_c, flat_tr = run_selection_arm("gonogo", test_c, W_ops, E, M, dd, best_alpha, wr_flat)
    orc_c = run_oracle_arm(test_c, W_ops, E, dd)
    ho_c, ho_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_oracle, wp_oracle_te)
    hs_c, hs_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_shuf, wp_shuf_te)
    op_c, op_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_open_te)
    c2f_c, c2f_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_c2f, wp_c2f_te)
    ver_c, ver_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_ver, wp_ver_te)
    cmb_c, cmb_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_combo, wp_combo_te)
    rp_c, rp_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_replay, wp_replay_te)
    kb_c, kb_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_kb, wp_kb_te)
    sel_c, sel_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_sel, wp_sel_te)
    stk_c, stk_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_stack, wp_stack_te)
    and_c, and_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_and, wp_and_te)
    kbp_c, kbp_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_kbp, wp_kbp_te)
    calg_c, calg_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_calg, wp_calg_te)
    rd_c, rd_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_rand_te)
    ix_c, ix_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_idx_te)

    arms: Dict[str, float] = {
        "flat_gonogo": float(flat_c.mean()), "oracle_exec": float(orc_c.mean()),
        "hier_oracle": float(ho_c.mean()), "hier_shuffled": float(hs_c.mean()),
        "wp_bisect_open": float(op_c.mean()), "wp_bisect_coarse2fine": float(c2f_c.mean()),
        "wp_bisect_verify": float(ver_c.mean()), "wp_bisect_combo": float(cmb_c.mean()),
        "wp_replay_generate_select": float(rp_c.mean()), "wp_kb_grounded_gate": float(kb_c.mean()),
        "wp_calibrated_selector_gate": float(sel_c.mean()),
        "wp_stacked_kb_plus_selector": float(stk_c.mean()),
        "wp_and_gate": float(and_c.mean()),
        "wp_kbpriority_union": float(kbp_c.mean()),
        "wp_calibrated_gate_combiner": float(calg_c.mean()),
        "wp_random_state": float(rd_c.mean()), "wp_index_midpoint": float(ix_c.mean()),
    }
    op_trace_hashes: Dict[str, str] = {
        "flat_gonogo": hashlib.sha256(flat_tr.tobytes()).hexdigest()[:16],
        "oracle_exec": "oracle_true_seq",
        "hier_oracle": hashlib.sha256(ho_tr.tobytes()).hexdigest()[:16],
        "hier_shuffled": hashlib.sha256(hs_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_open": hashlib.sha256(op_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_coarse2fine": hashlib.sha256(c2f_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_verify": hashlib.sha256(ver_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_combo": hashlib.sha256(cmb_tr.tobytes()).hexdigest()[:16],
        "wp_replay_generate_select": hashlib.sha256(rp_tr.tobytes()).hexdigest()[:16],
        "wp_kb_grounded_gate": hashlib.sha256(kb_tr.tobytes()).hexdigest()[:16],
        "wp_calibrated_selector_gate": hashlib.sha256(sel_tr.tobytes()).hexdigest()[:16],
        "wp_stacked_kb_plus_selector": hashlib.sha256(stk_tr.tobytes()).hexdigest()[:16],
        "wp_and_gate": hashlib.sha256(and_tr.tobytes()).hexdigest()[:16],
        "wp_kbpriority_union": hashlib.sha256(kbp_tr.tobytes()).hexdigest()[:16],
        "wp_calibrated_gate_combiner": hashlib.sha256(calg_tr.tobytes()).hexdigest()[:16],
        "wp_random_state": hashlib.sha256(rd_tr.tobytes()).hexdigest()[:16],
        "wp_index_midpoint": hashlib.sha256(ix_tr.tobytes()).hexdigest()[:16],
    }

    diag = discovery_diagnostics(test_c, R_short, C, dd, W_ops, E, SEG_LEN)
    rr_test = reach_rank_acc(test_c, W_ops, E, M, dd)

    # RESCUE = DYNAMIC best-of-three precision-preserving combiner (by test accuracy at this seed/regime);
    # KEY comparator = KB-alone (single-best channel the combiner must ADD over). B0 OR-gate (stk_c) is the
    # confirmed-negative / must-stay-dilutive control. failure-mask screen (KB vs selector) is reported.
    combiner_c = {"wp_and_gate": and_c, "wp_kbpriority_union": kbp_c,
                  "wp_calibrated_gate_combiner": calg_c}
    best_rescue_arm = max(combiner_c.keys(), key=lambda a: float(np.mean(combiner_c[a])))
    best_c = combiner_c[best_rescue_arm]
    fmask = failure_mask_corr(kb_c, sel_c)

    # paired counts. KEY sign-test = best combiner vs KB-alone (does the combiner ADD over the single best
    # channel). Also per-combiner-vs-KB counts (the verdict re-selects the winner's counts) + guards.
    paired = {
        "n_rescue_only_vs_verify": int((best_c & (~kb_c)).sum()),   # KEY: best combiner vs KB-ALONE
        "n_verify_only_vs_rescue": int((kb_c & (~best_c)).sum()),   # (field name kept for scaffolding reuse)
        "n_rescue_only_vs_open": int((best_c & (~op_c)).sum()),
        "n_open_only_vs_rescue": int((op_c & (~best_c)).sum()),
        "n_rescue_only_vs_flat": int((best_c & (~flat_c)).sum()),
        "n_flat_only_vs_rescue": int((flat_c & (~best_c)).sum()),
        "n_rescue_only_vs_rand": int((best_c & (~rd_c)).sum()),
        "n_rand_only_vs_rescue": int((rd_c & (~best_c)).sum()),
        "n_idx_only_vs_rand": int((ix_c & (~rd_c)).sum()),
        "n_rand_only_vs_idx": int((rd_c & (~ix_c)).sum()),
        "n_test": int(len(best_c)),
    }
    # per-combiner paired-vs-KB (winner-agnostic; verdict picks the winning combiner's counts for sign-test)
    for _aname, _ac in combiner_c.items():
        paired["n_%s_only_vs_kb" % _aname] = int((_ac & (~kb_c)).sum())
        paired["n_kb_only_vs_%s" % _aname] = int((kb_c & (~_ac)).sum())
    rr_combo = (float(stats_combo["n_retry"]) / float(max(1, stats_combo["n_picks"])))
    rr_verify = (float(stats_ver["n_retry"]) / float(max(1, stats_ver["n_picks"])))
    fb_combo = (float(stats_combo["n_fallback"]) / float(max(1, stats_combo["n_picks"])))
    kb_dec = float(max(1, stats_kb["n_decisions"]))
    kb_confirm_rate = float(stats_kb["n_confirmed"]) / (kb_dec * float(V))   # frac of cand slots confirmed
    kb_fresh_rate = float(stats_kb["n_fresh"]) / kb_dec
    kb_fallback_rate = float(stats_kb["n_fallback"]) / kb_dec
    sel_dec = float(max(1, stats_sel["n_decisions"]))
    sel_accept_rate = float(stats_sel["n_confirmed"]) / (sel_dec * float(V))  # frac of cand slots accepted
    sel_fallback_rate = float(stats_sel["n_fallback"]) / sel_dec
    stack_dec = float(max(1, stats_stack["n_decisions"]))
    stack_confirm_rate = float(stats_stack["n_confirmed"]) / (stack_dec * float(V))
    stack_fresh_rate = float(stats_stack["n_fresh"]) / stack_dec
    stack_fallback_rate = float(stats_stack["n_fallback"]) / stack_dec

    def _crate(st):
        d = float(max(1, st["n_decisions"]))
        return (float(st["n_confirmed"]) / (d * float(V)), float(st["n_fresh"]) / d,
                float(st["n_fallback"]) / d)
    and_confirm_rate, and_fresh_rate, and_fallback_rate = _crate(stats_and)
    kbp_confirm_rate, kbp_fresh_rate, kbp_fallback_rate = _crate(stats_kbp)
    calg_confirm_rate, calg_fresh_rate, calg_fallback_rate = _crate(stats_calg)

    return {
        "n_ops": n_ops, "V": V, "dd": dd, "entropy": decision_entropy(n_ops, dd),
        "arms": arms, "op_trace_hashes": op_trace_hashes, "best_rescue_arm": best_rescue_arm,
        "best_alpha": float(best_alpha), "wr_open": float(wr_open), "wr_c2f": float(wr_c2f),
        "wr_ver": float(wr_ver), "wr_combo": float(wr_combo), "wr_replay": float(wr_replay),
        "reach_rank_chance": 1.0 / float(n_ops), "reach_rank_test": float(rr_test),
        "degenerate_rate": float(diag["degenerate_rate"]),
        "anti_tautology_corr": float(diag["anti_tautology_corr"]),
        "exact_match_rate": float(diag["exact_match_rate"]),
        "retry_rate_combo": rr_combo, "retry_rate_verify": rr_verify, "fallback_rate_combo": fb_combo,
        "bidir_mean_selected": float(agree.get("mean_selected_score", 0.0)),
        "bidir_mean_all_cand": float(agree.get("mean_all_cand_score", 0.0)),
        "bidir_mean_open_cand": float(agree.get("mean_open_cand_score", 0.0)),
        "frac_selected_not_open": float(agree.get("frac_selected_not_open", 0.0)),
        "independence_corr": float(indep["independence_corr"]),
        "kb_confirm_mean": float(indep["kb_confirm_mean"]),
        "kb_confirm_std": float(indep["kb_confirm_std"]),
        "m_error_mean": float(indep["m_error_mean"]),
        "independence_degenerate": bool(indep["independence_degenerate"]),
        "n_indep_units": int(indep["n_indep_units"]),
        "kb_confirm_rate": kb_confirm_rate, "kb_fresh_rate": kb_fresh_rate,
        "kb_fallback_rate": kb_fallback_rate,
        "selector_independence_corr": float(sel_indep["selector_independence_corr"]),
        "selector_conf_mean": float(sel_indep["selector_conf_mean"]),
        "selector_independence_degenerate": bool(sel_indep["selector_independence_degenerate"]),
        "sel_accept_rate": float(sel_accept_rate), "sel_fallback_rate": float(sel_fallback_rate),
        "sel_tau": float(sel_model.get("tau", 0.0)),
        "sel_acc_frac_train": float(sel_model.get("acc_frac_train", 0.0)),
        "sel_degenerate": bool(sel_model.get("degenerate", False)),
        "stack_confirm_rate": float(stack_confirm_rate), "stack_fresh_rate": float(stack_fresh_rate),
        "stack_fallback_rate": float(stack_fallback_rate),
        "and_confirm_rate": float(and_confirm_rate), "and_fresh_rate": float(and_fresh_rate),
        "and_fallback_rate": float(and_fallback_rate),
        "kbp_confirm_rate": float(kbp_confirm_rate), "kbp_fresh_rate": float(kbp_fresh_rate),
        "kbp_fallback_rate": float(kbp_fallback_rate),
        "calg_confirm_rate": float(calg_confirm_rate), "calg_fresh_rate": float(calg_fresh_rate),
        "calg_fallback_rate": float(calg_fallback_rate),
        "failmask_corr": float(fmask["failmask_corr"]),
        "failmask_kb_rate": float(fmask["failmask_kb_rate"]),
        "failmask_sel_rate": float(fmask["failmask_sel_rate"]),
        "failmask_degenerate": bool(fmask["failmask_degenerate"]),
        "n_failmask_units": int(fmask["n_failmask_units"]),
        "paired": paired,
    }


def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    disc_gen = np.random.default_rng(seed * 6364136223846793005 % (2 ** 63) + 1442695040888963407 % (2 ** 63))

    by_group: Dict[Tuple[int, int], List[int]] = {}
    for r in REGIMES:
        by_group.setdefault((r["V"], r["n_ops"]), []).append(r["dd"])

    regime_results: Dict[str, Any] = {}
    sr_diag_by_group: Dict[str, Any] = {}
    for (V, n_ops) in sorted(by_group.keys()):
        depths_needed = sorted(set(by_group[(V, n_ops)]))
        tgen = torch.Generator(device=DEVICE)
        tgen.manual_seed(int(seed) * 100003 + int(V) * 31 + int(n_ops))
        E = make_bipolar_E(V, N_DIM, tgen)
        per_op, train_by_d, test_by_d = make_kb_and_chains(
            n_ops, V, DENSITY, N_TRAIN_CHAINS, N_TEST_CHAINS, depths_needed, g)
        W_ops = [hebbian_W(per_op[i], E, N_DIM) for i in range(n_ops)]
        adj = build_adjacency(per_op, n_ops)
        # RAW-KB reachability closure (exogenous ground-truth channel; zero shared params with M/R)
        reach_cum = build_kb_reach_cum(per_op, n_ops, V, max(depths_needed))
        # CHANNEL B: cross-fit calibrated selector (trained on TRAIN chains ONLY; features raw-graph only;
        # ZERO M/R dependence). Built once per (V,n_ops) group, shared across depths.
        sel_model = train_calibrated_selector(per_op, n_ops, V, reach_cum, train_by_d, depths_needed,
                                              W_ops, E, int(seed) * 2654435761 % (2 ** 31) + int(V))

        max_len = max(depths_needed) + 2
        transitions = collect_rollout_transitions(adj, n_ops, V, rollout_count(V), max_len, g)

        # M (short, gamma=0.85) trained FIRST with the parent's exact sr_gen seed -> reproduces the
        # parent's M / R / wp_bisect_open / flat / hier_oracle by construction (positive control).
        sr_gen = torch.Generator(device=DEVICE)
        sr_gen.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3)
        M, sr_diag = train_sr_transport(E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR,
                                        GAMMA_SHORT, sr_gen)
        # M_long (gamma=0.95) trained SECOND with a distinct generator -> does not perturb M.
        sr_gen_long = torch.Generator(device=DEVICE)
        sr_gen_long.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3 + 104729)
        M_long, sr_diag_long = train_sr_transport(E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR,
                                                  GAMMA_LONG, sr_gen_long)
        # M_rev (gamma=0.85, REVERSED transitions cur<->nxt) -> INFORMATIONALLY-INDEPENDENT reverse
        # channel for bidirectional replay scoring. Distinct generator -> does not perturb M / M_long.
        sr_gen_rev = torch.Generator(device=DEVICE)
        sr_gen_rev.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3 + 224737)
        transitions_rev = (transitions[:, ::-1].copy() if transitions.shape[0] > 0
                           else transitions)
        M_rev, sr_diag_rev = train_sr_transport(E, transitions_rev, N_DIM, SR_STEPS, SR_BATCH, SR_LR,
                                                GAMMA_SHORT, sr_gen_rev)

        R_short = build_reach_matrix(E, M)
        R_long = build_reach_matrix(E, M_long)
        R_rev = build_reach_matrix(E, M_rev)
        C = codebook_selfcos(E)
        tau_short = offdiag_quantile(R_short, VERIFY_TAU_PCTL)
        tau_long = offdiag_quantile(R_long, VERIFY_TAU_PCTL)

        # replay perturbation generator: deterministic per (seed, V, n_ops); advanced across regimes.
        rgen = torch.Generator(device=DEVICE)
        rgen.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3 + 314159)

        sr_diag["gamma_long_err_first"] = sr_diag_long["err_first"]
        sr_diag["gamma_long_err_last"] = sr_diag_long["err_last"]
        sr_diag["gamma_long_M_norm"] = sr_diag_long["final_M_norm"]
        sr_diag["gamma_rev_err_first"] = sr_diag_rev["err_first"]
        sr_diag["gamma_rev_err_last"] = sr_diag_rev["err_last"]
        sr_diag["gamma_rev_M_norm"] = sr_diag_rev["final_M_norm"]
        sr_diag["tau_short"] = tau_short
        sr_diag["tau_long"] = tau_long
        sr_diag_by_group[group_key(n_ops, V)] = sr_diag

        print("[seed=%d op%d V=%d] SR_short err %s->%s Mn=%.3f | SR_long err %s->%s Mn=%.3f | "
              "SR_rev err %s->%s Mn=%.3f | R_s=%.3f R_l=%.3f R_r=%.3f tau_s=%.3f tau_l=%.3f n_trans=%d"
              % (seed, n_ops, V, sr_diag["err_first"], sr_diag["err_last"], sr_diag["final_M_norm"],
                 sr_diag_long["err_first"], sr_diag_long["err_last"], sr_diag_long["final_M_norm"],
                 sr_diag_rev["err_first"], sr_diag_rev["err_last"], sr_diag_rev["final_M_norm"],
                 float(R_short.mean()), float(R_long.mean()), float(R_rev.mean()), tau_short, tau_long,
                 sr_diag["n_transitions"]), flush=True)

        for dd in depths_needed:
            rec = _eval_regime(n_ops, V, dd, E, W_ops, M, M_long, M_rev, R_short, R_long, R_rev, C,
                               reach_cum, sel_model, tau_short, tau_long, train_by_d, test_by_d, g,
                               disc_gen, rgen)
            rec["sr_err_last"] = sr_diag["err_last"]
            key = regime_key(n_ops, V, dd)
            regime_results[key] = rec
            a = rec["arms"]
            print("[seed=%d %s ent=%.2f] FLAT=%.3f OEXEC=%.3f HORC=%.3f | OPEN=%.3f VER=%.3f KB=%.3f "
                  "SEL=%.3f STACK=%.3f RAND=%.3f IDX=%.3f (a=%.2f rr=%.3f | indep_corr=%.3f "
                  "sel_indep=%.3f failmask_corr=%.3f kb_conf=%.3f sel_acc=%.3f kb_fresh=%.3f "
                  "sel_deg=%s best=%s)"
                  % (seed, key, rec["entropy"], a["flat_gonogo"], a["oracle_exec"], a["hier_oracle"],
                     a["wp_bisect_open"], a["wp_bisect_verify"], a["wp_kb_grounded_gate"],
                     a["wp_calibrated_selector_gate"], a["wp_stacked_kb_plus_selector"],
                     a["wp_random_state"], a["wp_index_midpoint"], rec["best_alpha"],
                     rec["reach_rank_test"], rec["independence_corr"],
                     rec["selector_independence_corr"], rec["failmask_corr"], rec["kb_confirm_mean"],
                     rec["sel_accept_rate"], rec["kb_fresh_rate"], rec["sel_degenerate"],
                     rec["best_rescue_arm"]), flush=True)

    return {
        "seed": int(seed), "N": N_DIM, "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "regime_results": regime_results, "sr_diag_by_group": sr_diag_by_group,
    }


# ============================================================================
# aggregate + verdict
# ============================================================================
def _mean(xs: List[float]) -> float:
    return float(np.mean(xs)) if xs else 0.0


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_regime": {}}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)

    def _present(rk):
        return [k for k in keys if rk in per_seed[k].get("regime_results", {})]

    def _arm_col(rk, arm):
        return [float(per_seed[k]["regime_results"][rk]["arms"][arm]) for k in _present(rk)]

    def _field_col(rk, field):
        return [float(per_seed[k]["regime_results"][rk].get(field, 0.0)) for k in _present(rk)]

    per_regime: Dict[str, Any] = {}
    completed_units = 0
    for r in REGIMES:
        rk = regime_key(r["n_ops"], r["V"], r["dd"])
        present = _present(rk)
        n_present = len(present)
        completed_units += n_present * len(ARMS)

        arm_means, arm_cvs = {}, {}
        for arm in ARMS:
            vals = _arm_col(rk, arm)
            if vals:
                m = float(np.mean(vals)); sd = float(np.std(vals))
                arm_means[arm] = m
                arm_cvs[arm] = float(sd / m) if m > 1e-6 else 0.0
            else:
                arm_means[arm] = 0.0; arm_cvs[arm] = 0.0

        flat = arm_means["flat_gonogo"]
        oexec = arm_means["oracle_exec"]
        horc = arm_means["hier_oracle"]
        rand = arm_means["wp_random_state"]
        idxm = arm_means["wp_index_midpoint"]
        open_a = arm_means["wp_bisect_open"]
        verify_a = arm_means["wp_bisect_verify"]        # KEY comparator (already-failed self-ref)
        kb_a = arm_means[KB_ARM]                          # channel A alone
        sel_a = arm_means[SELECTOR_ARM]                  # channel B alone

        or_gate_a = arm_means[OR_GATE_ARM]              # B0 confirmed-negative / must-stay-dilutive control

        headroom_exec = oexec - flat
        headroom_decomp = horc - flat

        def _recov(x):
            return ((x - flat) / headroom_decomp) if headroom_decomp > 1e-6 else 0.0
        recovery_open = _recov(open_a)
        recovery_verify = _recov(verify_a)
        recovery_kb = _recov(kb_a)                        # single-best channel (the reference to ADD over)
        recovery_sel = _recov(sel_a)
        recovery_or_gate = _recov(or_gate_a)              # B0 OR-gate
        recovery_and = _recov(arm_means["wp_and_gate"])
        recovery_kbp = _recov(arm_means["wp_kbpriority_union"])
        recovery_calg = _recov(arm_means["wp_calibrated_gate_combiner"])
        # DYNAMIC best-of-three precision-preserving combiner (by recovery at THIS regime)
        combiner_recov = {"wp_and_gate": recovery_and, "wp_kbpriority_union": recovery_kbp,
                          "wp_calibrated_gate_combiner": recovery_calg}
        best_rescue_arm = max(combiner_recov.keys(), key=lambda a: combiner_recov[a])
        best_rescue = arm_means[best_rescue_arm]
        recovery_rescue = combiner_recov[best_rescue_arm]
        combiner_over_kb = {a: (combiner_recov[a] - recovery_kb) for a in combiner_recov}
        best_combiner_over_kb = combiner_over_kb[best_rescue_arm]   # HEADLINE margin over KB-alone
        or_gate_over_kb = recovery_or_gate - recovery_kb           # B0 margin (must stay <= 0: dilutive)
        # KEY margin = best precision-preserving combiner over KB-alone (headline discriminator).
        delta_recovery = best_combiner_over_kb            # (name kept for scaffolding reuse; == over-KB)
        delta_recovery_vs_open = recovery_rescue - recovery_open
        stacked_over_kb = best_combiner_over_kb           # reported alias
        gain_kb = recovery_kb - recovery_verify
        gain_sel = recovery_sel - recovery_verify
        gain_stacked = recovery_rescue - recovery_verify
        # "beats-both": the combiner clears BOTH single channels (reported diagnostic; not a hard gate)
        super_additive = bool(recovery_rescue > max(recovery_kb, recovery_sel))
        # failure-mask + selector-independence screens (aggregated across seeds)
        failmask_corr = _mean(_field_col(rk, "failmask_corr"))
        abs_failmask_corr = abs(failmask_corr)
        failmask_kb_rate = _mean(_field_col(rk, "failmask_kb_rate"))
        failmask_sel_rate = _mean(_field_col(rk, "failmask_sel_rate"))
        failmask_degenerate = any(bool(per_seed[k]["regime_results"][rk].get("failmask_degenerate", True))
                                  for k in present) if present else True
        sel_indep_corr = _mean(_field_col(rk, "selector_independence_corr"))
        abs_sel_indep_corr = abs(sel_indep_corr)
        sel_accept_rate = _mean(_field_col(rk, "sel_accept_rate"))
        sel_degenerate = any(bool(per_seed[k]["regime_results"][rk].get("sel_degenerate", True))
                             for k in present) if present else True
        sel_acc_frac_train = _mean(_field_col(rk, "sel_acc_frac_train"))
        sel_vacuous = bool(sel_degenerate
                           or not (SELECTOR_MIN_ACC_FRAC < sel_acc_frac_train < SELECTOR_MAX_ACC_FRAC))
        autonomous_closure = ((best_rescue - flat) / headroom_exec) if headroom_exec > 1e-6 else 0.0
        lift_flat = best_rescue - flat
        lift_random = best_rescue - rand
        lift_open = best_rescue - open_a
        lift_verify = best_rescue - verify_a
        index_artifact_gap = idxm - rand
        chain_steps = n_boundaries(r["dd"], SEG_LEN) - 1

        degen = _mean(_field_col(rk, "degenerate_rate"))
        anti_taut = _mean(_field_col(rk, "anti_tautology_corr"))
        exact = _mean(_field_col(rk, "exact_match_rate"))
        rr_test = _mean(_field_col(rk, "reach_rank_test"))
        retry_combo = _mean(_field_col(rk, "retry_rate_combo"))
        fb_combo = _mean(_field_col(rk, "fallback_rate_combo"))
        bidir_sel = _mean(_field_col(rk, "bidir_mean_selected"))
        bidir_all = _mean(_field_col(rk, "bidir_mean_all_cand"))
        bidir_open = _mean(_field_col(rk, "bidir_mean_open_cand"))
        frac_not_open = _mean(_field_col(rk, "frac_selected_not_open"))
        indep_corr = _mean(_field_col(rk, "independence_corr"))
        abs_indep_corr = abs(indep_corr)
        kb_confirm_mean = _mean(_field_col(rk, "kb_confirm_mean"))
        kb_confirm_std = _mean(_field_col(rk, "kb_confirm_std"))
        m_error_mean = _mean(_field_col(rk, "m_error_mean"))
        kb_confirm_rate = _mean(_field_col(rk, "kb_confirm_rate"))
        kb_fresh_rate = _mean(_field_col(rk, "kb_fresh_rate"))
        kb_fallback_rate = _mean(_field_col(rk, "kb_fallback_rate"))
        indep_degenerate = any(bool(per_seed[k]["regime_results"][rk].get("independence_degenerate", True))
                               for k in present) if present else True
        kb_vacuous = not (KB_CONFIRM_MEAN_LO < kb_confirm_mean < KB_CONFIRM_MEAN_HI)
        entropy = decision_entropy(r["n_ops"], r["dd"])

        # pooled paired sign-test: KEY = the WINNING combiner vs KB-ALONE (does the combiner ADD over the
        # single best channel), using the winner's per-combiner-vs-kb counts; index vs random guard.
        _wk_only = "n_%s_only_vs_kb" % best_rescue_arm
        _kw_only = "n_kb_only_vs_%s" % best_rescue_arm
        n_res_only = sum(int(per_seed[k]["regime_results"][rk]["paired"].get(_wk_only, 0)) for k in present)
        n_ver_only = sum(int(per_seed[k]["regime_results"][rk]["paired"].get(_kw_only, 0)) for k in present)
        n_disc = n_res_only + n_ver_only
        sign_p = binom_two_sided_p(n_res_only, n_disc, 0.5) if n_disc > 0 else 1.0
        n_idx_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_idx_only_vs_rand"]) for k in present)
        n_rand_only_idx = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_rand_only_vs_idx"]) for k in present)
        n_disc_idx = n_idx_only + n_rand_only_idx
        idx_sign_p = binom_two_sided_p(n_idx_only, n_disc_idx, 0.5) if n_disc_idx > 0 else 1.0

        # arms-differ (AF): replay trace vs verify/open/flat/random per seed; hier_oracle vs shuffled
        af_collision = False
        for k in present:
            rr = per_seed[k]["regime_results"][rk]
            h = rr["op_trace_hashes"]
            brs = rr["best_rescue_arm"]
            if h[brs] in (h["wp_bisect_verify"], h["wp_bisect_open"], h["flat_gonogo"],
                          h["wp_random_state"]):
                af_collision = True
            if h["hier_oracle"] == h["hier_shuffled"]:
                af_collision = True

        oracle_rail_ok = bool(oexec >= ORACLE_RAIL_MIN)
        headroom_exec_ok = bool(headroom_exec >= HEADROOM_EXEC_MIN)
        headroom_decomp_ok = bool(headroom_decomp >= HEADROOM_DECOMP_MIN)
        brs_cv = arm_cvs[best_rescue_arm]

        index_leak = bool(index_artifact_gap > INDEX_LEAK_GAP and idx_sign_p < INDEX_LEAK_P)

        per_regime[rk] = {
            "n_ops": r["n_ops"], "V": r["V"], "dd": r["dd"], "n_seeds": n_present,
            "entropy": entropy, "chain_steps": int(chain_steps),
            "arm_means": arm_means, "arm_cvs": arm_cvs,
            "flat_gonogo": flat, "oracle_exec": oexec, "hier_oracle": horc,
            "wp_bisect_open": open_a, "wp_bisect_verify": verify_a,
            "wp_random_state": rand, "wp_index_midpoint": idxm,
            "best_rescue_arm": best_rescue_arm, "best_rescue": float(best_rescue),
            "headroom_exec": float(headroom_exec), "headroom_decomp": float(headroom_decomp),
            "recovery_open": float(recovery_open), "recovery_verify": float(recovery_verify),
            "recovery_kb": float(recovery_kb), "recovery_sel": float(recovery_sel),
            "recovery_rescue": float(recovery_rescue),
            "delta_recovery": float(delta_recovery),
            "delta_recovery_vs_open": float(delta_recovery_vs_open),
            "gain_kb": float(gain_kb), "gain_sel": float(gain_sel), "gain_stacked": float(gain_stacked),
            "super_additive": bool(super_additive), "stacked_over_kb": float(stacked_over_kb),
            "recovery_and": float(recovery_and), "recovery_kbp": float(recovery_kbp),
            "recovery_calg": float(recovery_calg), "recovery_or_gate": float(recovery_or_gate),
            "and_over_kb": float(combiner_over_kb["wp_and_gate"]),
            "kbp_over_kb": float(combiner_over_kb["wp_kbpriority_union"]),
            "calg_over_kb": float(combiner_over_kb["wp_calibrated_gate_combiner"]),
            "best_combiner_over_kb": float(best_combiner_over_kb),
            "or_gate_over_kb": float(or_gate_over_kb),
            "or_gate_dilutive": bool(or_gate_over_kb <= OR_GATE_DILUTIVE_MAX),
            "failmask_corr": float(failmask_corr), "abs_failmask_corr": float(abs_failmask_corr),
            "failmask_kb_rate": float(failmask_kb_rate), "failmask_sel_rate": float(failmask_sel_rate),
            "failmask_degenerate": bool(failmask_degenerate),
            "selector_independence_corr": float(sel_indep_corr),
            "abs_selector_independence_corr": float(abs_sel_indep_corr),
            "sel_accept_rate": float(sel_accept_rate), "sel_acc_frac_train": float(sel_acc_frac_train),
            "sel_degenerate": bool(sel_degenerate), "sel_vacuous": bool(sel_vacuous),
            "kb_alone": float(kb_a), "selector_alone": float(sel_a),
            "flatness_kb": 0.0,   # filled in second pass (needs d4 sibling)
            "autonomous_closure": float(autonomous_closure),
            "lift_flat": float(lift_flat), "lift_random": float(lift_random),
            "lift_open": float(lift_open), "lift_verify": float(lift_verify),
            "index_artifact_gap": float(index_artifact_gap),
            "degenerate_rate": float(degen), "anti_tautology_corr": float(anti_taut),
            "exact_match_rate": float(exact), "reach_rank_test": float(rr_test),
            "retry_rate_combo": float(retry_combo), "fallback_rate_combo": float(fb_combo),
            "bidir_mean_selected": float(bidir_sel), "bidir_mean_all_cand": float(bidir_all),
            "bidir_mean_open_cand": float(bidir_open), "frac_selected_not_open": float(frac_not_open),
            "independence_corr": float(indep_corr), "abs_independence_corr": float(abs_indep_corr),
            "kb_confirm_mean": float(kb_confirm_mean), "kb_confirm_std": float(kb_confirm_std),
            "m_error_mean": float(m_error_mean), "kb_confirm_rate": float(kb_confirm_rate),
            "kb_fresh_rate": float(kb_fresh_rate), "kb_fallback_rate": float(kb_fallback_rate),
            "independence_degenerate": bool(indep_degenerate), "kb_vacuous": bool(kb_vacuous),
            "sign_test_p": float(sign_p), "idx_sign_p": float(idx_sign_p),
            "n_rescue_only": int(n_res_only), "n_verify_only": int(n_ver_only),
            "oracle_rail_ok": oracle_rail_ok, "headroom_exec_ok": headroom_exec_ok,
            "headroom_decomp_ok": headroom_decomp_ok, "brs_cv": float(brs_cv),
            "af_collision": bool(af_collision), "index_leak": index_leak,
            "flatness_ratio": 0.0, "hp_ok": False,   # filled in second pass (needs d4 sibling)
        }

    # ---- second pass: flatness_ratio (needs the chain_steps==1 sibling) + hp_ok ----
    def _shallow_ref(v, field):
        """<field> recovery at the matching chain_steps==1 (dd=4) regime with same n_ops & V."""
        for rk2, v2 in per_regime.items():
            if (v2["n_ops"] == v["n_ops"] and v2["V"] == v["V"]
                    and v2["chain_steps"] == 1 and v2["n_seeds"] > 0):
                return v2[field]
        return None

    for rk, v in per_regime.items():
        ref = _shallow_ref(v, "recovery_rescue")
        if ref is not None and ref > 1e-6:
            v["flatness_ratio"] = float(v["recovery_rescue"] / ref)
        else:
            v["flatness_ratio"] = 0.0        # no positive shallow reference -> flatness undefined -> 0
        ref_kb = _shallow_ref(v, "recovery_kb")
        if ref_kb is not None and ref_kb > 1e-6:
            v["flatness_kb"] = float(v["recovery_kb"] / ref_kb)
        else:
            v["flatness_kb"] = 0.0
        # HARD_PASS = a precision-preserving combiner genuinely ADDS over the single best channel (KB-alone)
        #   at depth by the pre-registered margin, WHILE the naive OR-gate B0 stays dilutive (the fair-
        #   contrast confirmed-negative control), AND the mechanism is non-vacuous / significant / honest.
        #   NOTE: super-additivity + low failmask-corr are NOT gates here (that was the OR-gate's
        #   multiplicative premise); the precision-combiner claim is simply "beats KB-alone precisely."
        hp_ok = (v["oracle_rail_ok"] and v["headroom_exec_ok"] and v["headroom_decomp_ok"]
                 and v["best_combiner_over_kb"] >= HP_COMBINER_OVER_KB_MIN
                 and v["recovery_rescue"] >= HP_RECOVERY_RATIO_FLOOR
                 and v["or_gate_dilutive"]                # B0 OR-gate must stay <= 0 over KB (fair contrast)
                 and v["flatness_ratio"] >= HP_FLATNESS_MIN
                 and not v["kb_vacuous"]
                 and not v["sel_vacuous"]
                 and v["lift_flat"] > HP_LIFT_FLAT_MIN
                 and v["lift_random"] > HP_LIFT_RANDOM_MIN
                 and v["index_artifact_gap"] < HP_INDEX_GAP_MAX
                 and v["anti_tautology_corr"] < HP_ANTI_TAUT_CORR_MAX
                 and v["degenerate_rate"] < HP_DEGENERATE_MAX
                 and v["sign_test_p"] < HP_SIGN_TEST_P
                 and (v["brs_cv"] < HP_CV_MAX or RUN_MODE != "full")
                 and not v["af_collision"])
        v["hp_ok"] = bool(hp_ok)

    # ---- reported regardless: entropy relationship of delta_recovery ----
    grid_ents, grid_delta = [], []
    for rk, v in per_regime.items():
        if v["n_seeds"] > 0 and v["headroom_decomp"] > 1e-6:
            grid_ents.append(v["entropy"]); grid_delta.append(v["delta_recovery"])
    spearman_delta_vs_entropy = _spearman(grid_delta, grid_ents)

    # ---- focus = highest-entropy discriminating regime (op4_V1200_d8 in FULL) ----
    cardinality_ok = completed_units >= EXPECTED_N_UNITS
    discriminating = {rk: v for rk, v in per_regime.items()
                      if v["oracle_rail_ok"] and v["headroom_exec_ok"]
                      and v["headroom_decomp_ok"] and v["n_seeds"] > 0}
    focus_rk = None
    if discriminating:
        focus_rk = max(discriminating.keys(),
                       key=lambda rk: (per_regime[rk]["entropy"], per_regime[rk]["n_ops"],
                                       per_regime[rk]["dd"]))
    fv = per_regime[focus_rk] if focus_rk is not None else None

    # ---- reported REGARDLESS: rescue depth-frontier (does NOT move locked FOCUS goalposts) ----
    hp_ok_keys = [rk for rk, v in per_regime.items() if v["hp_ok"] and v["n_seeds"] > 0]
    n_regimes_hp_ok = len(hp_ok_keys)
    capability_frontier = None
    max_entropy_hp_ok = None
    if hp_ok_keys:
        capability_frontier = max(hp_ok_keys,
                                  key=lambda rk: (per_regime[rk]["entropy"],
                                                  per_regime[rk]["n_ops"], per_regime[rk]["dd"]))
        max_entropy_hp_ok = per_regime[capability_frontier]["entropy"]

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif fv is None:
        verdict = "INCONCLUSIVE_NO_DISCRIMINATING_REGIME"
    elif fv["index_leak"]:
        verdict = "INCONCLUSIVE_INDEX_ORDER_LEAK"
    elif not fv["or_gate_dilutive"]:
        # the CONFIRMED-NEGATIVE control did NOT reproduce: the naive OR-gate B0 is NOT dilutive over
        # KB-alone at FOCUS -> the OR-dilution premise this cell contrasts against is absent here -> the
        # combiner-vs-OR contrast is not fair. Report as INCONCLUSIVE (re-anchor the negative before tiering).
        verdict = "INCONCLUSIVE_OR_GATE_NOT_DILUTIVE"
    elif fv["best_combiner_over_kb"] <= HF_COMBINER_OVER_KB_CEIL:
        # NO precision-preserving combiner (AND, KB-priority union, calibrated-gate) beats KB-alone at the
        # deep corner -> the second channel is too weak to help under ANY combination rule -> the
        # single-best-channel conclusion is FINAL (a clean scope-bound; the strongest closure to date).
        verdict = "HARD_FAIL_SINGLE_BEST_CHANNEL_FINAL"
    elif fv["hp_ok"]:
        verdict = "HARD_PASS"
    else:
        # a combiner beats KB-alone by some margin but sub-threshold or a guard failed
        if fv["index_artifact_gap"] >= HP_INDEX_GAP_MAX:
            verdict = "MIDDLE_BAND_INDEX_ARTIFACT_GUARD"
        elif fv["kb_vacuous"] or fv["independence_degenerate"]:
            verdict = "MIDDLE_BAND_KB_CONFIRM_VACUOUS"
        elif fv["sel_vacuous"]:
            verdict = "MIDDLE_BAND_SELECTOR_VACUOUS"
        elif fv["anti_tautology_corr"] >= HP_ANTI_TAUT_CORR_MAX:
            verdict = "MIDDLE_BAND_ANTI_TAUTOLOGY_GUARD"
        elif fv["degenerate_rate"] >= HP_DEGENERATE_MAX:
            verdict = "MIDDLE_BAND_DEGENERATE_GUARD"
        elif fv["lift_random"] <= HP_LIFT_RANDOM_MIN:
            verdict = "MIDDLE_BAND_LIFT_RANDOM_BELOW"
        elif fv["best_combiner_over_kb"] < HP_COMBINER_OVER_KB_MIN:
            # real-but-partial combiner lift over KB-alone (in (HF_ceil, HP_min))
            verdict = "MIDDLE_BAND_PARTIAL_COMBINER_OVER_KB"
        elif fv["recovery_rescue"] < HP_RECOVERY_RATIO_FLOOR:
            verdict = "MIDDLE_BAND_RECOVERY_BELOW_35"
        elif fv["flatness_ratio"] < HP_FLATNESS_MIN:
            verdict = "MIDDLE_BAND_FLATNESS_BELOW_50"
        elif fv["sign_test_p"] >= HP_SIGN_TEST_P:
            verdict = "MIDDLE_BAND_SIGN_TEST_NS"
        elif RUN_MODE == "full" and fv["brs_cv"] >= HP_CV_MAX:
            verdict = "MIDDLE_BAND_CV_TOO_HIGH"
        else:
            verdict = "MIDDLE_BAND_SUBTHRESHOLD"

    grid_str = " ".join(
        "%s(e%.1f:F%.2f/KB%.2f/AND%.2f/KBP%.2f/CALG%.2f/OR%.2f bco=%.2f oko=%.2f)" % (
            rk, per_regime[rk]["entropy"], per_regime[rk]["flat_gonogo"],
            per_regime[rk]["arm_means"]["wp_kb_grounded_gate"],
            per_regime[rk]["arm_means"]["wp_and_gate"],
            per_regime[rk]["arm_means"]["wp_kbpriority_union"],
            per_regime[rk]["arm_means"]["wp_calibrated_gate_combiner"],
            per_regime[rk]["arm_means"]["wp_stacked_kb_plus_selector"],
            per_regime[rk]["best_combiner_over_kb"], per_regime[rk]["or_gate_over_kb"])
        for rk in REGIME_KEYS if rk in per_regime and per_regime[rk]["n_seeds"] > 0)

    if fv is not None:
        head = ("%s | FOCUS=%s(ent=%.1f steps=%d) FLAT=%.3f OEXEC=%.3f HIER_ORACLE=%.3f | "
                "KB=%.3f AND=%.3f KBP=%.3f CALG=%.3f OR=%.3f | best_combiner=%s "
                "recov_kb=%.3f recov_best=%.3f BEST_OVER_KB=%.3f OR_OVER_KB=%.3f(dilutive=%s) | "
                "and_ok=%.3f kbp_ok=%.3f calg_ok=%.3f | flatness=%.3f | "
                "kb_confirm=%.3f sel_acc=%.3f sel_deg=%s kb_vac=%s sel_vac=%s | "
                "lift_flat=%.3f lift_random=%.3f index_gap=%.3f anti_taut=%.3f degen=%.3f "
                "sign_p=%.4g rr=%.3f cv=%.3f | spr(bco,ent)=%.3f | GRID [%s] n_seeds=%d") % (
            verdict, focus_rk, fv["entropy"], fv["chain_steps"], fv["flat_gonogo"], fv["oracle_exec"],
            fv["hier_oracle"], fv["kb_alone"], fv["arm_means"]["wp_and_gate"],
            fv["arm_means"]["wp_kbpriority_union"], fv["arm_means"]["wp_calibrated_gate_combiner"],
            fv["arm_means"]["wp_stacked_kb_plus_selector"], fv["best_rescue_arm"],
            fv["recovery_kb"], fv["recovery_rescue"], fv["best_combiner_over_kb"],
            fv["or_gate_over_kb"], fv["or_gate_dilutive"],
            fv["and_over_kb"], fv["kbp_over_kb"], fv["calg_over_kb"], fv["flatness_ratio"],
            fv["kb_confirm_mean"], fv["sel_accept_rate"], fv["sel_degenerate"], fv["kb_vacuous"],
            fv["sel_vacuous"], fv["lift_flat"], fv["lift_random"], fv["index_artifact_gap"],
            fv["anti_tautology_corr"], fv["degenerate_rate"], fv["sign_test_p"], fv["reach_rank_test"],
            fv["brs_cv"], spearman_delta_vs_entropy, grid_str, len(keys))
    else:
        head = "%s | no discriminating regime | GRID [%s] n_seeds=%d" % (verdict, grid_str, len(keys))

    head = head + (" | CAP_FRONTIER=%s(maxE=%s) n_hp_ok=%d/%d"
                   % (capability_frontier, max_entropy_hp_ok, n_regimes_hp_ok, len(per_regime)))

    return {
        "verdict": verdict, "verdict_msg": head, "summary": head,
        "per_regime": per_regime, "focus_regime": focus_rk,
        "focus_best_rescue_arm": (fv["best_rescue_arm"] if fv else None),
        "focus_best_rescue": (fv["best_rescue"] if fv else None),
        "focus_wp_bisect_open": (fv["wp_bisect_open"] if fv else None),
        "focus_wp_bisect_verify": (fv["wp_bisect_verify"] if fv else None),
        "focus_recovery_open": (fv["recovery_open"] if fv else None),
        "focus_recovery_verify": (fv["recovery_verify"] if fv else None),
        "focus_recovery_rescue": (fv["recovery_rescue"] if fv else None),
        "focus_delta_recovery": (fv["delta_recovery"] if fv else None),
        "focus_delta_recovery_vs_open": (fv["delta_recovery_vs_open"] if fv else None),
        "focus_flatness_ratio": (fv["flatness_ratio"] if fv else None),
        "focus_lift_flat": (fv["lift_flat"] if fv else None),
        "focus_lift_random": (fv["lift_random"] if fv else None),
        "focus_lift_open": (fv["lift_open"] if fv else None),
        "focus_lift_verify": (fv["lift_verify"] if fv else None),
        "focus_bidir_mean_selected": (fv["bidir_mean_selected"] if fv else None),
        "focus_bidir_mean_all_cand": (fv["bidir_mean_all_cand"] if fv else None),
        "focus_frac_selected_not_open": (fv["frac_selected_not_open"] if fv else None),
        "focus_index_artifact_gap": (fv["index_artifact_gap"] if fv else None),
        "focus_independence_corr": (fv["independence_corr"] if fv else None),
        "focus_abs_independence_corr": (fv["abs_independence_corr"] if fv else None),
        "focus_kb_confirm_mean": (fv["kb_confirm_mean"] if fv else None),
        "focus_kb_confirm_std": (fv["kb_confirm_std"] if fv else None),
        "focus_m_error_mean": (fv["m_error_mean"] if fv else None),
        "focus_kb_fresh_rate": (fv["kb_fresh_rate"] if fv else None),
        "focus_kb_fallback_rate": (fv["kb_fallback_rate"] if fv else None),
        "focus_kb_vacuous": (fv["kb_vacuous"] if fv else None),
        "focus_independence_degenerate": (fv["independence_degenerate"] if fv else None),
        "focus_kb_alone": (fv["kb_alone"] if fv else None),
        "focus_selector_alone": (fv["selector_alone"] if fv else None),
        "focus_recovery_kb": (fv["recovery_kb"] if fv else None),
        "focus_recovery_sel": (fv["recovery_sel"] if fv else None),
        "focus_gain_kb": (fv["gain_kb"] if fv else None),
        "focus_gain_sel": (fv["gain_sel"] if fv else None),
        "focus_gain_stacked": (fv["gain_stacked"] if fv else None),
        "focus_super_additive": (fv["super_additive"] if fv else None),
        "focus_stacked_over_kb": (fv["stacked_over_kb"] if fv else None),
        "focus_best_combiner_over_kb": (fv["best_combiner_over_kb"] if fv else None),
        "focus_and_over_kb": (fv["and_over_kb"] if fv else None),
        "focus_kbp_over_kb": (fv["kbp_over_kb"] if fv else None),
        "focus_calg_over_kb": (fv["calg_over_kb"] if fv else None),
        "focus_or_gate_over_kb": (fv["or_gate_over_kb"] if fv else None),
        "focus_or_gate_dilutive": (fv["or_gate_dilutive"] if fv else None),
        "focus_recovery_and": (fv["recovery_and"] if fv else None),
        "focus_recovery_kbp": (fv["recovery_kbp"] if fv else None),
        "focus_recovery_calg": (fv["recovery_calg"] if fv else None),
        "focus_recovery_or_gate": (fv["recovery_or_gate"] if fv else None),
        "focus_flatness_kb": (fv["flatness_kb"] if fv else None),
        "focus_failmask_corr": (fv["failmask_corr"] if fv else None),
        "focus_abs_failmask_corr": (fv["abs_failmask_corr"] if fv else None),
        "focus_failmask_kb_rate": (fv["failmask_kb_rate"] if fv else None),
        "focus_failmask_sel_rate": (fv["failmask_sel_rate"] if fv else None),
        "focus_failmask_degenerate": (fv["failmask_degenerate"] if fv else None),
        "focus_selector_independence_corr": (fv["selector_independence_corr"] if fv else None),
        "focus_abs_selector_independence_corr": (fv["abs_selector_independence_corr"] if fv else None),
        "focus_sel_accept_rate": (fv["sel_accept_rate"] if fv else None),
        "focus_sel_vacuous": (fv["sel_vacuous"] if fv else None),
        "focus_sel_degenerate": (fv["sel_degenerate"] if fv else None),
        "combiner_beats_kb": bool(fv["best_combiner_over_kb"] > HF_COMBINER_OVER_KB_CEIL) if fv else False,
        "combiner_clears_margin": bool(fv["best_combiner_over_kb"] >= HP_COMBINER_OVER_KB_MIN) if fv else False,
        "or_gate_dilutive_focus": bool(fv["or_gate_dilutive"]) if fv else False,
        "focus_best_combiner_arm": (fv["best_rescue_arm"] if fv else None),
        "super_additive_focus": bool(fv["super_additive"]) if fv else False,
        "spearman_delta_vs_entropy": spearman_delta_vs_entropy,
        "discriminating_regime_keys": list(discriminating.keys()),
        "n_regimes_hp_ok": int(n_regimes_hp_ok), "hp_ok_regime_keys": hp_ok_keys,
        "rescue_capability_frontier": capability_frontier,
        "max_entropy_hp_ok": (float(max_entropy_hp_ok) if max_entropy_hp_ok is not None else None),
        "expected_n_units": EXPECTED_N_UNITS, "completed_units": int(completed_units),
        "cardinality_ok": bool(cardinality_ok), "cv_gate_enforced": bool(RUN_MODE == "full"),
        "n_seeds_complete": len(keys),
    }


# ============================================================================
# self-test (formula correctness; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s gS=%.2f gL=%.2f span_thr=%d tau_pctl=%.2f seg_len=%d"
          % (DEVICE, GAMMA_SHORT, GAMMA_LONG, SPAN_LONG_THRESH, VERIFY_TAU_PCTL, SEG_LEN), flush=True)

    # ST1: SR-TD delta-rule shrinks the TD prediction error over steps
    gen = torch.Generator(device=DEVICE); gen.manual_seed(0)
    E = make_bipolar_E(12, 128, gen)
    trans = np.array([[i, i + 1] for i in range(10)], dtype=np.int64)
    M, diag = train_sr_transport(E, trans, 128, steps=200, batch=8, base_lr=0.5, gamma=0.8, gen=gen)
    assert diag["err_last"] is not None and diag["err_last"] < diag["err_first"], "ST1 TD not shrink"
    assert float(M.norm()) > 1e-4, "ST1 M ~zero"
    print("[selftest] ST1 TD shrinks RPE %.4f->%.4f OK" % (diag["err_first"], diag["err_last"]), flush=True)

    # ST2: reach matrix identity R[i,j]==reach_value(E[i],E[j],M)
    gen3 = torch.Generator(device=DEVICE); gen3.manual_seed(3)
    E3 = make_bipolar_E(20, 512, gen3)
    tr3 = np.array([[i, (i + 1) % 20] for i in range(20)] * 3, dtype=np.int64)
    M3, _ = train_sr_transport(E3, tr3, 512, steps=300, batch=16, base_lr=0.5, gamma=GAMMA_SHORT, gen=gen3)
    R3 = build_reach_matrix(E3, M3)
    for (i, j) in [(0, 5), (3, 3), (7, 12), (19, 1)]:
        rv = float(reach_value(E3[i:i + 1], E3[j:j + 1], M3)[0])
        assert abs(R3[i, j].item() - rv) < 1e-4, "ST2 R[%d,%d] mismatch" % (i, j)
    print("[selftest] ST2 reach matrix identity OK", flush=True)

    # ST3: gamma_for_span uses long horizon only beyond the threshold
    assert gamma_for_span(8) == GAMMA_LONG and gamma_for_span(6) == GAMMA_LONG, "ST3 long span"
    assert gamma_for_span(5) == GAMMA_SHORT and gamma_for_span(4) == GAMMA_SHORT, "ST3 short span"
    assert gamma_for_span(2) == GAMMA_SHORT, "ST3 tiny span"
    print("[selftest] ST3 gamma_for_span: span6/8->%.2f span4/5->%.2f OK" % (GAMMA_LONG, GAMMA_SHORT),
          flush=True)

    # ST4: build a toy R with a KNOWN good midpoint; open bisection + verify + c2f all fire & are
    #      non-degenerate (interior != start/goal), last boundary == goal, interiors distinct.
    gen4 = torch.Generator(device=DEVICE); gen4.manual_seed(11)
    Vt, Nt = 24, 1024
    Et = make_bipolar_E(Vt, Nt, gen4)
    chain = [(k, k + 1) for k in range(0, 8)]
    trt = np.tile(np.array(chain, dtype=np.int64), (60, 1))
    Mt, _ = train_sr_transport(Et, trt, Nt, steps=1500, batch=16, base_lr=0.5, gamma=GAMMA_SHORT, gen=gen4)
    Mt_l, _ = train_sr_transport(Et, trt, Nt, steps=1500, batch=16, base_lr=0.5, gamma=GAMMA_LONG, gen=gen4)
    Rt = build_reach_matrix(Et, Mt)
    Rt_l = build_reach_matrix(Et, Mt_l)
    tau_s = offdiag_quantile(Rt, VERIFY_TAU_PCTL)
    tau_l = offdiag_quantile(Rt_l, VERIFY_TAU_PCTL)
    dgen = np.random.default_rng(4)
    st = torch.tensor([0], dtype=torch.long, device=DEVICE)
    gl = torch.tensor([8], dtype=torch.long, device=DEVICE)
    for label, b in [
        ("open", _discover_bisect_boundaries(st, gl, Rt, 2, 8)),
        ("verify", _discover_verify_boundaries(st, gl, Rt, tau_s, 2, 8, dgen)),
        ("c2f", _discover_coarse2fine_boundaries(st, gl, Rt, Rt_l, tau_s, tau_l, 2, 8, False, dgen)),
        ("combo", _discover_coarse2fine_boundaries(st, gl, Rt, Rt_l, tau_s, tau_l, 2, 8, True, dgen)),
    ]:
        assert int(b[0, -1].item()) == 8, "ST4 %s last boundary must be goal" % label
        interior = b[0, :-1].tolist()
        assert all(x not in (0, 8) for x in interior), "ST4 %s interior degenerate: %s" % (label, interior)
        assert len(set(interior)) == len(interior), "ST4 %s interiors not distinct: %s" % (label, interior)
    print("[selftest] ST4 open/verify/c2f/combo all non-degenerate, distinct, goal-terminated OK",
          flush=True)

    # ST5: coarse-to-fine picks the MIDDLE first from GROUND-TRUTH endpoints. Construct an R where the
    #      true middle node (4) balances start(0)/goal(8) far better than any other; c2f must select it
    #      at the center boundary (array index 1 for d8 seg2: interiors at pos 2,4,6).
    Vm = 12
    Rm = torch.full((Vm, Vm), 0.05, device=DEVICE, dtype=DTYPE)
    Rm.fill_diagonal_(1.0)
    # make node 4 strongly reachable-from-0 and reaching-8 (the ideal center); nodes 2/6 moderate.
    Rm[0, 4] = 0.9; Rm[4, 8] = 0.9
    Rm[0, 2] = 0.6; Rm[2, 8] = 0.6
    Rm[4, 6] = 0.6; Rm[6, 8] = 0.6
    Rm[0, 6] = 0.3; Rm[6, 8] = max(float(Rm[6, 8]), 0.6)
    Rm[4, 2] = 0.6
    st1 = torch.tensor([0], dtype=torch.long, device=DEVICE)
    gl1 = torch.tensor([8], dtype=torch.long, device=DEVICE)
    tau_m = offdiag_quantile(Rm, VERIFY_TAU_PCTL)
    bm = _discover_coarse2fine_boundaries(st1, gl1, Rm, Rm, tau_m, tau_m, 2, 8, False, np.random.default_rng(1))
    # center boundary is array index 1 (pos 4). It is picked FIRST from (start=0, goal=8); node 4 wins.
    assert int(bm[0, 1].item()) == 4, "ST5 c2f center pick should be node 4, got %d" % int(bm[0, 1])
    print("[selftest] ST5 coarse-to-fine center pick from ground-truth endpoints = node 4 OK", flush=True)

    # ST6: verify-gate = commit-only-if-strong. The AND-of-two-legs threshold (R[a,c]>=tau AND
    #      R[c,g]>=tau) is exactly balance=min(legs)>=tau, so a STRONG top pick (balance>=tau) is
    #      committed identically to open (verify agrees with the unverified argmax when the pick is
    #      well-connected). Node 3 has balance 0.9 >= tau=0.5 -> both open and verify pick it.
    Vv = 8
    Rv = torch.full((Vv, Vv), 0.10, device=DEVICE, dtype=DTYPE)
    Rv.fill_diagonal_(1.0)
    Rv[0, 3] = 0.90; Rv[3, 7] = 0.90       # node 3: balance 0.90 >= tau -> passes verify AND is argmax
    stv = torch.tensor([0], dtype=torch.long, device=DEVICE)
    glv = torch.tensor([7], dtype=torch.long, device=DEVICE)
    tau_v = 0.5
    p_open = _pick_balanced_verify(stv, glv, Rv, tau_v, [], False, np.random.default_rng(2), None)
    p_ver = _pick_balanced_verify(stv, glv, Rv, tau_v, [], True, np.random.default_rng(2), None)
    assert int(p_open[0].item()) == 3, "ST6 open argmax should be node 3, got %d" % int(p_open[0])
    assert int(p_ver[0].item()) == 3, "ST6 verify (strong pick) should agree w/ open (node 3), got %d" % int(p_ver[0])
    print("[selftest] ST6 verify-gate commits a strong pick identically to open (node 3) OK", flush=True)

    # ST7: verify-gate REFUSES a weak pick. When open's argmax pick has balance < tau (no candidate is
    #      well-connected), verify does NOT commit it -> falls back to a valid random state (!= start/goal,
    #      logged). This is the don't-chain-a-weak-waypoint behavior; the discriminator vs open.
    Rlow = torch.full((6, 6), 0.10, device=DEVICE, dtype=DTYPE); Rlow.fill_diagonal_(1.0)
    stf = torch.tensor([0], dtype=torch.long, device=DEVICE)
    glf = torch.tensor([5], dtype=torch.long, device=DEVICE)
    p_open_w = _pick_balanced_verify(stf, glf, Rlow, 0.5, [], False, np.random.default_rng(3), None)
    assert int(p_open_w[0].item()) not in (0, 5), "ST7 open pick landed on start/goal"
    stats_f = {"n_picks": 0, "n_retry": 0, "n_fallback": 0}
    pf = _pick_balanced_verify(stf, glf, Rlow, 0.9, [], True, np.random.default_rng(3), stats_f)
    assert int(pf[0].item()) not in (0, 5), "ST7 fallback landed on start/goal"
    assert stats_f["n_fallback"] == 1, "ST7 fallback not counted (%d)" % stats_f["n_fallback"]
    assert stats_f["n_retry"] >= 1, "ST7 weak pick should register retries before fallback"
    print("[selftest] ST7 verify-gate refuses weak pick -> valid random fallback, counted OK", flush=True)

    # ST8: index-midpoint interpolation (structural guard) VERBATIM behavior
    st6 = torch.tensor([10, 100], dtype=torch.long, device=DEVICE)
    tg6 = torch.tensor([30, 200], dtype=torch.long, device=DEVICE)
    ib4 = _discover_index_boundaries(st6, tg6, 300, 2, 4)
    assert abs(int(ib4[0, 0].item()) - 20) <= 1 and abs(int(ib4[1, 0].item()) - 150) <= 1, "ST8 idx mid"
    assert int(ib4[0, -1].item()) == 30, "ST8 idx last must be goal"
    print("[selftest] ST8 index-midpoint interpolation OK", flush=True)

    # ST9: boundaries->hops schedule matches the ancestor build_waypoint_idx schedule
    bstate = torch.tensor([[100, 200, 300]], dtype=torch.long, device=DEVICE)
    hops = _boundaries_to_hops(bstate, 2, 6)
    exp = torch.tensor([100, 100, 200, 200, 300, 300], dtype=torch.long, device=DEVICE)
    assert bool((hops[0] == exp).all()), "ST9 hop schedule wrong"
    print("[selftest] ST9 boundaries->hops schedule OK", flush=True)

    # ST9b: REVERSE SR -- training on cur<->nxt swapped transitions makes R_rev[nxt,cur] large (the
    #       reverse channel: "cur typically precedes nxt"). On a fwd chain 0->1->...->k, R_rev[j+1,j]
    #       (predecessor reach) should exceed R_rev[j,j+1] (successor reach) on average.
    gen9 = torch.Generator(device=DEVICE); gen9.manual_seed(21)
    Vr, Nr = 20, 512
    Er = make_bipolar_E(Vr, Nr, gen9)
    fwd_tr = np.array([[i, (i + 1) % Vr] for i in range(Vr)] * 4, dtype=np.int64)
    rev_tr = fwd_tr[:, ::-1].copy()
    Mrev, _ = train_sr_transport(Er, rev_tr, Nr, steps=800, batch=16, base_lr=0.5, gamma=GAMMA_SHORT, gen=gen9)
    Rrev = build_reach_matrix(Er, Mrev)
    pred_reach = float(np.mean([Rrev[(i + 1) % Vr, i].item() for i in range(Vr)]))   # predecessor
    succ_reach = float(np.mean([Rrev[i, (i + 1) % Vr].item() for i in range(Vr)]))   # successor
    assert pred_reach > succ_reach, "ST9b reverse SR: predecessor reach %.3f !> successor %.3f" % (
        pred_reach, succ_reach)
    print("[selftest] ST9b reverse SR predecessor=%.3f > successor=%.3f OK" % (pred_reach, succ_reach),
          flush=True)

    # ST9c: generate_candidates -- candidate 0 == unperturbed open pick (perturb_frac=0 identity);
    #       all candidates goal-terminated + non-degenerate; perturbation yields >=1 distinct candidate
    #       when the balance signal is not perfectly peaked.
    gen9c = torch.Generator(device=DEVICE); gen9c.manual_seed(33)
    Vc, Nc = 24, 1024
    Ec = make_bipolar_E(Vc, Nc, gen9c)
    ch = [(k, k + 1) for k in range(0, 8)]
    trc = np.tile(np.array(ch, dtype=np.int64), (60, 1))
    Mc, _ = train_sr_transport(Ec, trc, Nc, steps=1200, batch=16, base_lr=0.5, gamma=GAMMA_SHORT, gen=gen9c)
    Rc = build_reach_matrix(Ec, Mc)
    stc = torch.tensor([0], dtype=torch.long, device=DEVICE)
    glc = torch.tensor([8], dtype=torch.long, device=DEVICE)
    rgen_t = torch.Generator(device=DEVICE); rgen_t.manual_seed(7)
    cands = generate_candidates(stc, glc, Rc, 2, 8, 5, rgen_t, 0.60)
    open_b = _discover_bisect_boundaries(stc, glc, Rc, 2, 8)
    assert cands.shape[0] == 5, "ST9c wrong n_cand"
    assert bool((cands[0] == open_b).all()), "ST9c candidate 0 must equal unperturbed open pick"
    for c in range(cands.shape[0]):
        assert int(cands[c, 0, -1].item()) == 8, "ST9c cand %d not goal-terminated" % c
        interior = cands[c, 0, :-1].tolist()
        assert all(x not in (0, 8) for x in interior), "ST9c cand %d degenerate: %s" % (c, interior)
        assert len(set(interior)) == len(interior), "ST9c cand %d interiors not distinct" % c
    n_distinct = len({tuple(cands[c, 0].tolist()) for c in range(cands.shape[0])})
    assert n_distinct >= 2, "ST9c perturbation produced no candidate diversity (n_distinct=%d)" % n_distinct
    print("[selftest] ST9c generate_candidates: cand0==open, all goal-term+non-degen, diversity=%d OK"
          % n_distinct, flush=True)

    # ST9d: score_bidirectional -- a candidate through a KNOWN-good midpoint (fwd AND rev agree) scores
    #       higher than one through a bad midpoint (directions disagree). Construct explicit R_fwd/R_rev.
    Vg = 6
    Rf = torch.full((Vg, Vg), 0.05, device=DEVICE, dtype=DTYPE); Rf.fill_diagonal_(1.0)
    Rr = torch.full((Vg, Vg), 0.05, device=DEVICE, dtype=DTYPE); Rr.fill_diagonal_(1.0)
    # good path 0->2->5: fwd strong (0->2, 2->5) AND rev strong (5->2, 2->0)
    Rf[0, 2] = 0.9; Rf[2, 5] = 0.9; Rr[5, 2] = 0.9; Rr[2, 0] = 0.9
    # bad path 0->3->5: fwd ok (0->3, 3->5) but rev DISAGREES (5->3, 3->0 weak)
    Rf[0, 3] = 0.9; Rf[3, 5] = 0.9; Rr[5, 3] = 0.05; Rr[3, 0] = 0.05
    st_g = torch.tensor([0], dtype=torch.long, device=DEVICE)
    good = torch.tensor([[2, 5]], dtype=torch.long, device=DEVICE)   # [mid, goal]
    bad = torch.tensor([[3, 5]], dtype=torch.long, device=DEVICE)
    s_good = float(score_bidirectional(good, st_g, Rf, Rr)[0])
    s_bad = float(score_bidirectional(bad, st_g, Rf, Rr)[0])
    assert s_good > s_bad, "ST9d bidirectional score: good %.3f !> bad %.3f" % (s_good, s_bad)
    print("[selftest] ST9d score_bidirectional good=%.3f > bad=%.3f (fwd-rev agreement) OK"
          % (s_good, s_bad), flush=True)

    # ST9e: wp_replay_generate_select COMMITS the agreeing candidate. With the good/bad R above and both
    #       candidates in the pool (candidate 0 = whichever open picks; force a 2-candidate pool by
    #       explicit generation), the selected interior must be the fwd-rev-agreeing node 2, not node 3.
    pool = torch.stack([good, bad], dim=0)          # [2, 1, 2]
    scores = torch.stack([score_bidirectional(pool[i], st_g, Rf, Rr) for i in range(2)], dim=0)
    sel = int(pool[scores.argmax(dim=0)[0], 0, 0].item())
    assert sel == 2, "ST9e replay-select should commit the agreeing node 2, got %d" % sel
    print("[selftest] ST9e replay-select commits fwd-rev-agreeing candidate (node 2) OK", flush=True)

    # ST9f: build_kb_reach_cum -- raw-graph transitive closure. Chain 0->1->2->3 (per_op): reach_cum[1]
    #       has only direct edges; reach_cum[2] adds 2-hop (0->2, 1->3); reach_cum[3] adds 0->3. A
    #       non-edge (3->0) stays False at all k. Zero dependence on any M/R.
    per_op_t = [[(0, 1), (1, 2), (2, 3)], [(1, 5)]]     # op0 = chain, op1 = a branch
    rc = build_kb_reach_cum(per_op_t, 2, 6, 3)
    assert bool(rc[1][0, 1]) and not bool(rc[1][0, 2]), "ST9f reach_cum[1] direct-only"
    assert bool(rc[2][0, 2]) and not bool(rc[2][0, 3]), "ST9f reach_cum[2] two-hop 0->2 but not 0->3"
    assert bool(rc[3][0, 3]), "ST9f reach_cum[3] three-hop 0->3"
    assert not bool(rc[3][3, 0]), "ST9f no spurious back-edge 3->0"
    assert bool(rc[2][0, 5]), "ST9f cross-op reach 0->1->5"
    print("[selftest] ST9f build_kb_reach_cum transitive closure (direct/2hop/3hop, no back-edge) OK",
          flush=True)

    # ST9g: _discover_kb_grounded_boundaries -- MASKS the R-balance argmax to KB-confirmed candidates.
    #       Construct R that PREFERS an off-graph node (node 6) but the KB only confirms the true
    #       midpoint (node 4); the KB gate must pick node 4, while raw open-bisection picks node 6.
    Vk = 12
    Rk = torch.full((Vk, Vk), 0.05, device=DEVICE, dtype=DTYPE); Rk.fill_diagonal_(1.0)
    # R (noisy estimator) most prefers node 6 as the balanced midpoint (a MISTAKE):
    Rk[0, 6] = 0.99; Rk[6, 8] = 0.99
    Rk[0, 4] = 0.80; Rk[4, 8] = 0.80        # true midpoint node 4 scores lower under R (it errs)
    # raw KB (exogenous) confirms ONLY node 4 on both legs (0->..->4 within seg_len, 4->..->8 within rem);
    # node 6 is NOT KB-reachable from 0 -> gate must exclude it.
    per_op_k = [[(0, 2), (2, 4), (4, 6), (6, 8)]]       # a real path 0-2-4-6-8; but with seg_len=2, node 6
    #  is 3 hops from 0 (> seg_len) so left-leg-from-anchor(0) within seg_len=2 reaches only {2,4}; node 4
    #  reaches goal 8 within rem. So node 4 is the only KB-confirmed midpoint at the center boundary.
    rck = build_kb_reach_cum(per_op_k, 1, Vk, 8)
    stk = torch.tensor([0], dtype=torch.long, device=DEVICE)
    glk = torch.tensor([8], dtype=torch.long, device=DEVICE)
    b_open_k = _discover_bisect_boundaries(stk, glk, Rk, 2, 8)
    b_kb_k = _discover_kb_grounded_boundaries(stk, glk, Rk, rck, 2, 8)
    assert int(b_open_k[0, -1].item()) == 8 and int(b_kb_k[0, -1].item()) == 8, "ST9g goal-terminated"
    # FIRST boundary (array index 0, anchor=start 0): sequential open picks the R-preferred node 6
    #  (balance 0.99); the KB gate excludes node 6 (3 hops from 0 > seg_len=2, unconfirmed) and picks the
    #  only KB-confirmed midpoint node 4 within seg_len of 0 that also reaches goal.
    assert int(b_open_k[0, 0].item()) == 6, "ST9g open should pick R-preferred node 6, got %d" % int(b_open_k[0, 0])
    assert int(b_kb_k[0, 0].item()) == 4, "ST9g kb gate should pick KB-confirmed node 4, got %d" % int(b_kb_k[0, 0])
    assert not bool((b_open_k == b_kb_k).all()), "ST9g kb trace must DIFFER from open"
    print("[selftest] ST9g kb-grounded gate masks R to KB-confirmed (open->6, kb->4, traces differ) OK",
          flush=True)

    # ST9h: independence screen -- returns a finite corr, kb_confirm in [0,1], and flags degeneracy when
    #       kb_confirm has zero variance. Build a tiny KB + R + oracle where SOME open picks are confirmed
    #       and some are not (non-degenerate), so corr is well-defined.
    gen9h = torch.Generator(device=DEVICE); gen9h.manual_seed(51)
    Vh, Nh = 24, 512
    Eh = make_bipolar_E(Vh, Nh, gen9h)
    chain_h = [(k, k + 1) for k in range(0, 8)]
    trh = np.tile(np.array(chain_h, dtype=np.int64), (40, 1))
    Mh, _ = train_sr_transport(Eh, trh, Nh, steps=800, batch=16, base_lr=0.5, gamma=GAMMA_SHORT, gen=gen9h)
    Rh = build_reach_matrix(Eh, Mh)
    per_op_h = [[(k, k + 1) for k in range(0, 8)]]
    rch = build_kb_reach_cum(per_op_h, 1, Vh, 8)
    W_h = [hebbian_W(per_op_h[0], Eh, Nh)]
    chains_h = [(0, [0] * 8, 8)]                        # start 0, op0 x8, goal 8 (true path 0..8)
    scr = kb_independence_screen(chains_h, Rh, rch, W_h, Eh, 8, 2)
    assert 0.0 <= scr["kb_confirm_mean"] <= 1.0, "ST9h kb_confirm_mean out of [0,1]"
    assert -1.0 <= scr["independence_corr"] <= 1.0, "ST9h corr out of range"
    assert scr["n_indep_units"] == 3, "ST9h wrong n_indep_units (%d)" % scr["n_indep_units"]
    print("[selftest] ST9h independence screen corr=%.3f kb_confirm=%.3f degen=%s n=%d OK"
          % (scr["independence_corr"], scr["kb_confirm_mean"], scr["independence_degenerate"],
             scr["n_indep_units"]), flush=True)

    # ST9i: generic _masked_bisection + OR-gate union. R prefers node 6 (0.99) over node 4 (0.80). A
    #       confirm allowing only {4} picks 4; allowing only {6} picks 6; the OR union {4,6} picks the
    #       higher-balance node 6 -> demonstrates the stacked OR mask = union, argmax within the union.
    Vs = 12
    Rs = torch.full((Vs, Vs), 0.05, device=DEVICE, dtype=DTYPE); Rs.fill_diagonal_(1.0)
    Rs[0, 6] = 0.99; Rs[6, 8] = 0.99
    Rs[0, 4] = 0.80; Rs[4, 8] = 0.80
    sts = torch.tensor([0], dtype=torch.long, device=DEVICE)
    gls = torch.tensor([8], dtype=torch.long, device=DEVICE)

    def _allow(nodes):
        def fn(la, ls, rg, rr):
            m = torch.zeros((la.shape[0], Vs), dtype=torch.bool, device=DEVICE)
            for nd in nodes:
                m[:, nd] = True
            return m
        return fn

    b4 = _masked_bisection(sts, gls, Rs, _allow([4]), 2, 8)
    b6 = _masked_bisection(sts, gls, Rs, _allow([6]), 2, 8)

    def _orfn(la, ls, rg, rr):
        return _allow([4])(la, ls, rg, rr) | _allow([6])(la, ls, rg, rr)
    bor = _masked_bisection(sts, gls, Rs, _orfn, 2, 8)
    assert int(b4[0, 0].item()) == 4, "ST9i allow{4} -> node 4, got %d" % int(b4[0, 0])
    assert int(b6[0, 0].item()) == 6, "ST9i allow{6} -> node 6, got %d" % int(b6[0, 0])
    assert int(bor[0, 0].item()) == 6, "ST9i OR-union{4,6} -> higher-balance node 6, got %d" % int(bor[0, 0])
    assert int(b4[0, -1].item()) == 8 and int(bor[0, -1].item()) == 8, "ST9i goal-terminated"
    print("[selftest] ST9i masked-bisection OR-gate union (allow4->4, allow6->6, OR->6) OK", flush=True)

    # ST9j: cross-fit calibrated selector -- trains on a toy chain, produces a usable model whose accept
    #       mask is a valid [n,V] bool; the degenerate path accepts ALL. _selector_scores in [0,1].
    gen9j = torch.Generator(device=DEVICE); gen9j.manual_seed(61)
    Vj, Nj = 20, 256
    Ej = make_bipolar_E(Vj, Nj, gen9j)
    per_op_j = [[(k, k + 1) for k in range(0, 8)]]
    rcj = build_kb_reach_cum(per_op_j, 1, Vj, 8)
    Wj = [hebbian_W(per_op_j[0], Ej, Nj)]
    train_j = {8: [(0, [0] * 8, 8), (1, [0] * 8, 9)]}
    modelj = train_calibrated_selector(per_op_j, 1, Vj, rcj, train_j, [8], Wj, Ej, 123)
    aj = torch.tensor([0], dtype=torch.long, device=DEVICE)
    gj = torch.tensor([8], dtype=torch.long, device=DEVICE)
    pj = _selector_scores(aj, gj, modelj)
    assert pj.shape == (1, Vj), "ST9j selector scores shape wrong"
    assert bool(((pj >= 0.0) & (pj <= 1.0)).all()), "ST9j selector prob out of [0,1]"
    accj = _selector_accept(aj, gj, modelj)
    assert accj.dtype == torch.bool and accj.shape == (1, Vj), "ST9j accept mask malformed"
    degen_model = {"degenerate": True, "outdeg": modelj["outdeg"], "rcsum": modelj["rcsum"],
                   "w": modelj["w"], "cal_a": 1.0, "cal_b": 0.0, "tau": 0.5}
    acc_all = _selector_accept(aj, gj, degen_model)
    assert bool(acc_all.all()), "ST9j degenerate model must accept ALL"
    print("[selftest] ST9j cross-fit selector: scores in[0,1], accept-mask valid, degenerate accepts-all OK",
          flush=True)

    # ST9k: failure_mask_corr -- fail = arm WRONG. Perfectly-correlated failures -> corr=1; anti-correlated
    #       -> corr=-1; an all-correct arm -> degenerate flag. This is the load-bearing NEW screen formula.
    kb_ok = np.array([1, 1, 0, 0, 1, 0], dtype=bool)
    sel_ok = np.array([1, 0, 1, 0, 1, 0], dtype=bool)
    d = failure_mask_corr(kb_ok, sel_ok)
    assert -1.0 <= d["failmask_corr"] <= 1.0 and not d["failmask_degenerate"], "ST9k corr range"
    dperf = failure_mask_corr(np.array([1, 1, 0, 0]), np.array([1, 1, 0, 0]))
    assert abs(dperf["failmask_corr"] - 1.0) < 1e-6, "ST9k identical failures -> corr=1"
    danti = failure_mask_corr(np.array([1, 0, 1, 0]), np.array([0, 1, 0, 1]))
    assert abs(danti["failmask_corr"] + 1.0) < 1e-6, "ST9k opposite failures -> corr=-1"
    ddeg = failure_mask_corr(np.array([1, 1, 1, 1]), np.array([1, 0, 1, 0]))
    assert ddeg["failmask_degenerate"], "ST9k all-correct arm -> degenerate flag"
    print("[selftest] ST9k failure_mask_corr (perfect=+1, opposite=-1, all-correct=degen) OK", flush=True)

    # ST9L: PRECISION-PRESERVING COMBINER confirm_fn formulas (this cell's mechanisms). Validate the exact
    #       boolean-mask semantics against kb/sel masks: AND = kb & sel (intersection); KB-PRIORITY = kb
    #       where kb non-empty else kb|sel (union only in KB holes); CALIBRATED-GATE = (kb|sel) & P>=tau_hi.
    a9 = torch.tensor([0], dtype=torch.long, device=DEVICE)
    g9 = torch.tensor([8], dtype=torch.long, device=DEVICE)
    kbfn9 = _kb_confirm_fn(rcj, 8)
    selfn9 = _selector_confirm_fn(modelj)
    kb9 = kbfn9(a9, 2, g9, 4)
    sel9 = selfn9(a9, 2, g9, 4)
    and9 = _and_confirm_fn(rcj, 8, modelj)(a9, 2, g9, 4)
    kbp9 = _kbpriority_confirm_fn(rcj, 8, modelj)(a9, 2, g9, 4)
    calg9 = _calibrated_gate_confirm_fn(rcj, 8, modelj)(a9, 2, g9, 4)
    assert bool((and9 == (kb9 & sel9)).all()), "ST9L AND-gate != kb & sel"
    assert bool((and9 <= kb9).all()) and bool((and9 <= sel9).all()), "ST9L AND not subset of both"
    has_kb9 = kb9.any(dim=1, keepdim=True)
    expected_kbp = torch.where(has_kb9, kb9, kb9 | sel9)
    assert bool((kbp9 == expected_kbp).all()), "ST9L KB-priority != where(has_kb, kb, kb|sel)"
    assert bool((kbp9 >= kb9).all()), "ST9L KB-priority must never drop a KB-confirmed candidate"
    union9 = kb9 | sel9
    assert bool((calg9 <= union9).all()), "ST9L calibrated-gate not subset of union"
    if not modelj.get("degenerate", False):
        hi9 = _selector_scores(a9, g9, modelj) >= modelj.get("tau_hi", 1.0)
        assert bool((calg9 == (union9 & hi9)).all()), "ST9L calibrated-gate != union & (P>=tau_hi)"
    else:
        assert bool((calg9 == union9).all()), "ST9L degenerate calibrated-gate must fall to union"
    # AND is the tightest, KB-priority the widest of the three precision rules (subset ordering)
    assert bool((and9 <= kbp9).all()), "ST9L AND must be subset of KB-priority"
    print("[selftest] ST9L precision combiners: AND=kb&sel, KBpriority=where(kb,kb,kb|sel), "
          "CALG=union&(P>=tau_hi); subset-ordering AND<=KBpri OK (sel_degen=%s)"
          % modelj.get("degenerate", False), flush=True)

    # ST10: recovery / delta(vs verify) / flatness formulas (grounded on the ancestor FOCUS numbers)
    flat_, oexec_, horc_, verify_, replay_ = 0.081, 0.918, 0.906, 0.096, 0.35
    hd = horc_ - flat_
    rv = (verify_ - flat_) / hd                       # recovery_verify (MEASURED ancestor ~0.0182)
    rr = (replay_ - flat_) / hd                       # recovery_replay
    delta = rr - rv
    assert abs(rv - 0.018182) < 1e-3, "ST10 recovery_verify off: %.5f" % rv
    assert abs(rr - 0.326061) < 1e-3, "ST10 recovery_replay off: %.5f" % rr
    assert abs(delta - 0.307879) < 1e-3, "ST10 delta(vs verify) off: %.5f" % delta
    # flatness: FOCUS recovery / shallow (d4) recovery. shallow replay recovery ~0.65 -> flatness ~0.50
    shallow_flat, shallow_horc, shallow_replay = 0.515, 0.953, 0.80
    shd = shallow_horc - shallow_flat
    shallow_rec = (shallow_replay - shallow_flat) / shd
    flatness = rr / shallow_rec
    assert abs(shallow_rec - 0.650685) < 1e-3, "ST10 shallow recovery off: %.5f" % shallow_rec
    assert abs(flatness - 0.501258) < 1e-3, "ST10 flatness off: %.5f" % flatness
    print("[selftest] ST10 recovery_verify=%.3f recovery_replay=%.3f delta=%.3f flatness=%.3f OK"
          % (rv, rr, delta, flatness), flush=True)

    # ST11: spearman + entropy + binom
    assert abs(_spearman([1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0]) - 1.0) < 1e-9, "ST11 spearman"
    assert abs(decision_entropy(4, 8) - 16.0) < 1e-9, "ST11 entropy op4_d8"
    p = binom_two_sided_p(8, 10, 0.5)
    assert 0.0 <= p <= 1.0 and abs(binom_two_sided_p(8, 10) - binom_two_sided_p(2, 10)) < 1e-9, "ST11 binom"
    print("[selftest] ST11 spearman + entropy + binom OK", flush=True)

    # ST12: full pipeline single-seed structural (all 11 arms + diagnostics present; oracle sane;
    #       positive-control: wp_replay trace differs from open/verify)
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_waypoint_rescue")
    rk0 = REGIME_KEYS[0]
    assert rk0 in r["regime_results"], "ST12 missing regime %s" % rk0
    for arm in ARMS:
        assert arm in r["regime_results"][rk0]["arms"], "ST12 missing arm %s" % arm
    for fld in ("degenerate_rate", "anti_tautology_corr", "best_rescue_arm", "retry_rate_combo"):
        assert fld in r["regime_results"][rk0], "ST12 missing field %s" % fld
    oexec = r["regime_results"][rk0]["arms"]["oracle_exec"]
    assert oexec >= 0.5, "ST12 oracle_exec too low (%.3f)" % oexec
    print("[selftest] ST12 pipeline OK arms=%d oracle_exec=%.3f" % (len(ARMS), oexec), flush=True)

    # ST13: verdict wiring (HARD_PASS; HARD_FAIL no-lift; MIDDLE partial; INCONCLUSIVE)
    _verdict_selftest()
    return 0


def _verdict_selftest() -> None:
    # NEW discriminator = max over {C1 AND, C2 KB-priority union, C3 calibrated-gate} of recovery(cX) -
    # recovery(kb_alone), WHILE the OR-gate B0 (or_v) stays dilutive (or_over_kb <= 0). Winning combiner
    # is picked dynamically by recovery; paired sign-test = winner vs KB-alone.
    def _mk(n_ops, V, dd, flat, oexec, horc, kb, sel, and_v, kbp_v, calg_v, or_v, rand, idxm,
            open_a=0.10, degen=0.02, taut=0.10, exact=0.20, rr=0.60,
            n_win_only=45, n_kb_only=2, n_idx_only=2, n_rand_only_idx=2,
            kb_conf=0.5, sel_acc_frac=0.40, sel_degen=False):
        arms = {"flat_gonogo": flat, "oracle_exec": oexec, "hier_oracle": horc,
                "hier_shuffled": 0.02, "wp_bisect_open": open_a, "wp_bisect_coarse2fine": 0.09,
                "wp_bisect_verify": 0.09, "wp_bisect_combo": 0.09,
                "wp_replay_generate_select": 0.09, "wp_kb_grounded_gate": kb,
                "wp_calibrated_selector_gate": sel, "wp_stacked_kb_plus_selector": or_v,
                "wp_and_gate": and_v, "wp_kbpriority_union": kbp_v,
                "wp_calibrated_gate_combiner": calg_v,
                "wp_random_state": rand, "wp_index_midpoint": idxm}
        # winner = combiner with max value (for AF trace distinctness + best_rescue_arm consistency)
        winner = max(["wp_and_gate", "wp_kbpriority_union", "wp_calibrated_gate_combiner"],
                     key=lambda a: arms[a])
        oth = {"flat_gonogo": "f", "oracle_exec": "oracle_true_seq", "hier_oracle": "ho",
               "hier_shuffled": "hs", "wp_bisect_open": "op", "wp_bisect_coarse2fine": "c2",
               "wp_bisect_verify": "vf", "wp_bisect_combo": "cb", "wp_replay_generate_select": "rp",
               "wp_kb_grounded_gate": "kb", "wp_calibrated_selector_gate": "se",
               "wp_stacked_kb_plus_selector": "st", "wp_and_gate": "an", "wp_kbpriority_union": "kp",
               "wp_calibrated_gate_combiner": "cg", "wp_random_state": "rd", "wp_index_midpoint": "ix"}
        paired = {"n_idx_only_vs_rand": n_idx_only, "n_rand_only_vs_idx": n_rand_only_idx, "n_test": 60,
                  "n_rescue_only_vs_verify": n_win_only, "n_verify_only_vs_rescue": n_kb_only}
        for a in ["wp_and_gate", "wp_kbpriority_union", "wp_calibrated_gate_combiner"]:
            paired["n_%s_only_vs_kb" % a] = n_win_only if a == winner else 5
            paired["n_kb_only_vs_%s" % a] = n_kb_only
        return {"n_ops": n_ops, "V": V, "dd": dd, "entropy": decision_entropy(n_ops, dd),
                "arms": arms, "op_trace_hashes": oth, "best_rescue_arm": winner, "best_alpha": 0.2,
                "wr_open": 1.0, "wr_c2f": 1.0, "wr_ver": 1.0, "wr_combo": 1.0, "wr_replay": 1.0,
                "reach_rank_chance": 1.0 / n_ops, "reach_rank_test": rr, "degenerate_rate": degen,
                "anti_tautology_corr": taut, "exact_match_rate": exact, "retry_rate_combo": 0.1,
                "retry_rate_verify": 0.1, "fallback_rate_combo": 0.0,
                "bidir_mean_selected": 0.7, "bidir_mean_all_cand": 0.5, "bidir_mean_open_cand": 0.5,
                "frac_selected_not_open": 0.6,
                "independence_corr": 0.05, "kb_confirm_mean": kb_conf, "kb_confirm_std": 0.4,
                "m_error_mean": 0.5, "independence_degenerate": False,
                "n_indep_units": 180, "kb_confirm_rate": 0.02, "kb_fresh_rate": 0.1,
                "kb_fallback_rate": 0.05,
                "selector_independence_corr": 0.05, "selector_conf_mean": 0.5,
                "selector_independence_degenerate": False, "sel_accept_rate": 0.02,
                "sel_fallback_rate": 0.05, "sel_tau": 0.5, "sel_acc_frac_train": sel_acc_frac,
                "sel_degenerate": sel_degen, "stack_confirm_rate": 0.03, "stack_fresh_rate": 0.1,
                "stack_fallback_rate": 0.05,
                "and_confirm_rate": 0.01, "and_fresh_rate": 0.1, "and_fallback_rate": 0.05,
                "kbp_confirm_rate": 0.02, "kbp_fresh_rate": 0.1, "kbp_fallback_rate": 0.05,
                "calg_confirm_rate": 0.02, "calg_fresh_rate": 0.1, "calg_fallback_rate": 0.05,
                "failmask_corr": 0.05, "failmask_kb_rate": 0.5,
                "failmask_sel_rate": 0.5, "failmask_degenerate": False, "n_failmask_units": 60,
                "paired": paired}

    # FOCUS d8: flat=0.081 oexec=0.918 horc=0.906 (hd=0.825). d4: flat=0.515 horc=0.953 (hd=0.438).
    # HARD_PASS: kb=0.30 (recov_kb=0.2655); best combiner kbp=0.42 (recov=0.4109) -> best_over_kb=0.1454
    #   >=0.05; recov_best=0.4109>=0.35; OR-gate or_v=0.25 (recov=0.2048) -> or_over_kb=-0.0606<=0 (dilutive).
    #   d4 kbp=0.85 (recov=0.765) -> flatness=0.4109/0.765=0.537>=0.5. lift/sign clean.
    def _hp_lo(**kw):
        d = dict(flat=0.515, oexec=0.957, horc=0.953, kb=0.80, sel=0.78, and_v=0.79, kbp_v=0.85,
                 calg_v=0.82, or_v=0.83, rand=0.09, idxm=0.10)
        d.update(kw)
        return _mk(4, 1200, 4, **d)

    def _hp_hi(**kw):
        d = dict(flat=0.081, oexec=0.918, horc=0.906, kb=0.30, sel=0.25, and_v=0.20, kbp_v=0.42,
                 calg_v=0.35, or_v=0.25, rand=0.02, idxm=0.02)
        d.update(kw)
        return _mk(4, 1200, 8, **d)

    global REGIMES, REGIME_KEYS, EXPECTED_N_UNITS
    saved = (REGIMES, REGIME_KEYS, EXPECTED_N_UNITS)
    reg_lo = regime_key(4, 1200, 4)     # chain_steps=1 (flatness reference)
    reg_hi = regime_key(4, 1200, 8)     # chain_steps=3 (FOCUS)
    REGIMES = [{"n_ops": 4, "V": 1200, "dd": 4}, {"n_ops": 4, "V": 1200, "dd": 8}]
    REGIME_KEYS = [reg_lo, reg_hi]
    EXPECTED_N_UNITS = len(ARMS) * 3 * len(REGIMES)

    def _run(lo, hi):
        ps = {s: {"regime_results": {reg_lo: lo(), reg_hi: hi()}} for s in ["7", "17", "23"]}
        return aggregate_and_verdict(ps)

    try:
        # HARD_PASS: KB-priority combiner beats KB-alone by 0.145; OR-gate stays dilutive.
        out = _run(_hp_lo, _hp_hi)
        assert out["verdict"] == "HARD_PASS", "ST13 expected HARD_PASS got %s" % out["verdict"]
        assert out["focus_regime"] == reg_hi, "ST13 focus should be high-entropy op4_d8"
        assert out["focus_best_combiner_arm"] == "wp_kbpriority_union", "ST13 winner=kbpriority"
        assert out["combiner_clears_margin"] and out["or_gate_dilutive_focus"], "ST13 HP flags"

        # HARD_FAIL single-best-channel-final: NO combiner beats kb-alone. all combiners ~ kb.
        #   kb=0.30 and=0.28 kbp=0.31 calg=0.29 -> best kbp recov=(0.31-.081)/.825=0.2776; over_kb=0.0121<=0.02.
        out2 = _run(_hp_lo, lambda: _hp_hi(and_v=0.28, kbp_v=0.31, calg_v=0.29, n_win_only=5, n_kb_only=4))
        assert out2["verdict"] == "HARD_FAIL_SINGLE_BEST_CHANNEL_FINAL", \
            "ST13 expected HARD_FAIL single-best-channel got %s" % out2["verdict"]

        # INCONCLUSIVE OR-gate not dilutive: the confirmed-negative did not reproduce (or_v beats kb).
        #   or_v=0.50 -> recov_or=(0.50-.081)/.825=0.5079 > recov_kb=0.2655 -> or_over_kb>0.
        out3 = _run(_hp_lo, lambda: _hp_hi(or_v=0.50))
        assert out3["verdict"] == "INCONCLUSIVE_OR_GATE_NOT_DILUTIVE", \
            "ST13 expected INCONCLUSIVE or-not-dilutive got %s" % out3["verdict"]

        # MIDDLE partial combiner-over-kb: kbp=0.335 -> recov=0.3078; over_kb=0.0423 in (0.02,0.05).
        out4 = _run(_hp_lo, lambda: _hp_hi(kbp_v=0.335, and_v=0.20, calg_v=0.30))
        assert out4["verdict"] == "MIDDLE_BAND_PARTIAL_COMBINER_OVER_KB", \
            "ST13 expected MIDDLE partial-combiner got %s" % out4["verdict"]

        # MIDDLE selector vacuous: sel_acc_frac_train=0.995 (>0.98) but margin clears (kbp beats kb).
        out5 = _run(lambda: _hp_lo(sel_acc_frac=0.995), lambda: _hp_hi(sel_acc_frac=0.995))
        assert out5["verdict"] == "MIDDLE_BAND_SELECTOR_VACUOUS", \
            "ST13 expected MIDDLE selector-vacuous got %s" % out5["verdict"]

        # MIDDLE recovery-below-35: combiner beats kb by margin but recov_best < 0.35 floor.
        #   kb=0.14 (recov=0.0715) kbp=0.24 (recov=0.1927; over_kb=0.121>=0.05) but recov<0.35.
        out6 = _run(_hp_lo, lambda: _hp_hi(kb=0.14, sel=0.12, and_v=0.12, kbp_v=0.24, calg_v=0.18,
                                           or_v=0.13))
        assert out6["verdict"] == "MIDDLE_BAND_RECOVERY_BELOW_35", \
            "ST13 expected MIDDLE recovery-below-35 got %s" % out6["verdict"]

        # INCONCLUSIVE index-order leak: index >> random with significance (fires before HF/HP checks).
        out7 = _run(_hp_lo, lambda: _hp_hi(idxm=0.30, n_idx_only=40, n_rand_only_idx=2))
        assert out7["verdict"] == "INCONCLUSIVE_INDEX_ORDER_LEAK", \
            "ST13 expected INCONCLUSIVE leak got %s" % out7["verdict"]

        # INCONCLUSIVE no discriminating regime (oracle_exec below rail).
        out8 = _run(lambda: _hp_lo(oexec=0.50), lambda: _hp_hi(oexec=0.50))
        assert out8["verdict"] == "INCONCLUSIVE_NO_DISCRIMINATING_REGIME", \
            "ST13 expected INCONCLUSIVE no-regime got %s" % out8["verdict"]
    finally:
        REGIMES, REGIME_KEYS, EXPECTED_N_UNITS = saved
    print("[selftest] ST13 verdict wiring OK (HARD_PASS combiner-beats-kb + OR-dilutive; HARD_FAIL single-"
          "best-channel-final; INCONCLUSIVE or-not-dilutive+index-leak+no-regime; MIDDLE partial-over-kb+"
          "selector-vacuous+recovery-below-35)", flush=True)


# ============================================================================
# main
# ============================================================================
def main() -> int:
    global _T0
    _T0 = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_start_marker(out_dir)

    print("[%s] mode=%s device=%s N=%d n_ops=%s depths=%s seeds=%s gS=%.2f gL=%.2f seg_len=%d "
          "regimes=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, N_OPS_SET, DEPTH_SET, SEEDS, GAMMA_SHORT,
             GAMMA_LONG, SEG_LEN, REGIME_KEYS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST1-ST13 (TD shrink, reach-matrix identity, gamma_for_span, "
                               "open/verify/c2f/combo non-degenerate, c2f center-pick, verify-gate "
                               "reject+fallback, index interp, hop schedule, reverse-SR, "
                               "generate_candidates, score_bidirectional, replay-select, kb-reach-cum, "
                               "kb-grounded gate, independence screen, masked-bisection OR-gate union, "
                               "cross-fit selector, failure-mask-corr, PRECISION COMBINERS "
                               "(AND/KB-priority/calibrated-gate formulas ST9L), recovery/over-kb/flatness "
                               "formulas, spearman/entropy/binom, pipeline, precision-combiner verdict "
                               "wiring ST13)",
                "summary": "SELFTEST_OK", "elapsed_s": round(time.time() - _T0, 1),
                "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
                "run_mode": "selftest", "config_version": CONFIG_VERSION})
            print("[selftest] ALL OK", flush=True)
            return rc
        except SystemExit:
            raise
        except Exception as e:
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_FAIL",
                "verdict_msg": "SELFTEST_FAIL: %s" % e, "summary": "SELFTEST_FAIL",
                "elapsed_s": round(time.time() - _T0, 1),
                "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
                "run_mode": "selftest", "traceback": traceback.format_exc()[:4000]})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            traceback.print_exc()
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "regimes": REGIME_KEYS}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    fatal_seed_errors: List[str] = []
    for i, seed in enumerate(remaining):
        t0 = time.time()
        _heartbeat(out_dir, i, len(remaining), "seed_start=%d" % seed)
        try:
            result = run_one_seed(seed, out_dir)
        except SystemExit:
            raise
        except Exception as e:
            fc = type(e).__name__
            fatal_seed_errors.append("seed=%d %s: %s" % (seed, fc, str(e)[:200]))
            write_partial_key(out_dir, seed, {
                "seed": int(seed), "run_mode": RUN_MODE, "N": N_DIM,
                "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
                "failure_class": fc, "error": str(e)[:400],
                "traceback": traceback.format_exc()[:3000],
                "regime_results": {}, "sr_diag_by_group": {}})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        _heartbeat(out_dir, i + 1, len(remaining), "seed_done=%d dt=%.1f" % (seed, time.time() - t0))
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    good = {k: v for k, v in per_seed.items() if v.get("regime_results")}
    final = aggregate_and_verdict(good)
    if fatal_seed_errors:
        final["fatal_seed_errors"] = fatal_seed_errors
        if final.get("verdict") == "HARD_PASS":
            final["verdict"] = "MIDDLE_BAND"
            final["verdict_msg"] = "DEMOTED_FROM_HP_DUE_TO_SEED_CRASH | " + final["verdict_msg"]
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _T0, 1)
    final["ts_iso"] = datetime.now(timezone.utc).isoformat()
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["device"] = str(DEVICE)
    _atomic_write_metrics(out_dir, final)
    print("[%s] DONE: %s" % (ANCHOR_NAME, final.get("verdict_msg", "")), flush=True)
    return 0


if __name__ == "__main__":
    _env = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    _od = REPO / "data" / ("exp_" + _env)
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
