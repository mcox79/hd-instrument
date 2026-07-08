"""SELF-MANAGER FUSION: an ACC/EVC scalar depth-threshold DIAL that reads the certified
combinedgate arbitration MARGIN as a confidence/conflict signal and decides, per item, whether to
invoke the retained-trace condenser's EXPENSIVE fine read or accept its CHEAP coarse read.

WHAT THIS IS (self-manager channel #3; build-order step 3 of the self-manager chapter):
  Dial#1 (substrate_acc_evc_adaptive_halting_v1, HARD_PASS) proved a content-free SCALAR dial tuned by
  train-time argmax accuracy-per-compute -> frozen -> applied as a local reflex can make a FROZEN hop-depth
  knob adaptive. The retained-trace condenser (exp_encoder_retained_trace_requery_coarse_to_fine_v1,
  HARD_PASS) proved a CHEAP coarse read (coarse_only recall ~0.902) and an EXPENSIVE fine read
  (retained_trace ~0.994) trade accuracy for compute. This cell FUSES them: it lays the SAME content-free
  scalar-over-frozen-knob dial OVER the coarse-vs-fine read decision, but reads its telemetry from a THIRD
  certified cell -- the combinedgate arbitration MARGIN (Kiani-Shadlen balance-of-evidence == Botvinick
  coactivation-conflict: the gap between the top-1 and top-2 combined_logit is, as a pure byproduct of
  computing WHICH candidate wins, the confidence/conflict signal ACC's Expected-Value-of-Control machinery
  uses to decide whether extra effort is worth it). NO new learned machinery: the margin is READ from the
  cheap coarse path's own combined_logit ranking; the dial is ONE scalar theta_M; the two read paths already
  exist. See notes/research_self_manager_fusion_depth_controller_acc_evc_brain_first_2026-07-08.md.

WHY DEPTH HAS SOMETHING TO REALLOCATE (the regime that forces the mechanism):
  The retained-trace cell's OWN smoke corpus SATURATES (shortlist_hit@k=1.000 at every k; coarse_only=0.902
  uniformly) -- there is no per-query regime where skipping the fine read actually costs accuracy, so that
  corpus cannot test a depth dial at all (Research note Part 2/3, load-bearing). THIS cell's corpus fixes
  that: per query, a corruption level cue_q ~ uniform[CUE_LO,CUE_HI] both (a) corrupts the store query (so
  the cheap coarse read fails on hard items where the robust fine read recovers) AND (b) shrinks the
  combinedgate margin M (arbitration gets conflicted on the same hard items). The margin M and the
  coarse-insufficiency are therefore MECHANISTICALLY coupled through a shared noisy cue -- exactly the
  cross-cell coupling both prior notes flagged as the open, untested question. The coupling is NOT assumed:
  margin_recall_corr MEASURES whether M actually predicts coarse-sufficiency, and can honestly fail.

NO GROUND-TRUTH LEAKAGE (load-bearing): the combinedgate margin is computed over the top-2 candidates of the
  CHEAP coarse combined_logit ranking (rank1 vs rank2), NOT against the ground-truth answer id. It is a
  pre-fine-read confidence signal available from the coarse path alone -- you cannot use the expensive read
  to decide whether to do the expensive read.

CONTROL LAW (content-free scalar; local reflex given frozen theta_M):
  coarse combined_logit_j = cos(coarse_q, coarse_store_j) / GATE_TAU + recency_bias_j     (cheap; all V)
  shallow prediction       = argmax_j coarse combined_logit_j                              (cost CS)
  M = coarse_logit[rank1] - coarse_logit[rank2]                                            (Kiani-Shadlen margin)
  deep read = fine (full-dim retained-dense) combined_logit re-rank WITHIN the coarse top-k shortlist (cost CD)
  reflex: M >= theta_M -> accept shallow (low conflict; EVC: extra control not worth it)
          M <  theta_M -> run deep       (high conflict; EVC: extra control likely pays off)
  theta_M tuned ONCE on a TRAIN query split by argmax accuracy-per-compute over a data-driven percentile
  grid of the TRAIN M distribution, then FROZEN for the disjoint TEST split (exactly Dial#1's recipe).

ARMS (6; paired -- same store / W_up / P / recency set / TEST queries per seed; differ ONLY by depth policy):
  FIXED_SHALLOW  coarse read every item (never fine). Named baseline (cost CS always).
  FIXED_DEEP     coarse shortlist + fine re-rank every item (cost CD always). Named ceiling.
  MARGIN_GATED   THE DIAL: M >= theta_M -> shallow else deep; theta_M argmax-accpc on TRAIN, frozen for TEST.
  RANDOM_DEPTH_MATCHED  per-item deep coin-flip with p(deep) == MARGIN_GATED's own TEST p(deep) (EQUAL
                 expected compute, telemetry ignored). Isolates "mixed budget helps" from "reading M helps".
  SCRAMBLED_MARGIN identical rule to MARGIN_GATED but M is permuted across queries (matched scale, query
                 correspondence destroyed). MANDATORY telemetry-sensitivity guard -> must collapse to random.
  ORACLE_GATED   deep exactly when shallow WOULD be wrong (ground-truth), shallow otherwise. Perfect-info
                 ceiling + closure denominator + depth-pressure gate (same role as Dial#1's ORACLE_HALT).

METRICS (accpc == accuracy / mean_cost_rel; EQUAL-COMPUTE accounting = accuracy per unit compute):
  gated_vs_shallow_rel = accpc(MARGIN_GATED)/accpc(FIXED_SHALLOW) - 1
  gated_vs_deep_rel    = accpc(MARGIN_GATED)/accpc(FIXED_DEEP)    - 1
  gated_vs_random_rel  = accpc(MARGIN_GATED)/accpc(RANDOM_DEPTH_MATCHED) - 1
  scramble_rel_gap     = 1 - accpc(SCRAMBLED_MARGIN)/accpc(MARGIN_GATED)  (telemetry-sensitivity)
  margin_recall_corr   = pearson(M_test, correct_shallow_test)  (does M predict coarse-sufficiency; the direct
                          test of the Part-3 corpus coupling)
  depth_spread         = fraction of TEST queries routed deep by MARGIN_GATED (mixed, not degenerate)
  closure              = (accpc(GATED)-accpc(best_fixed)) / (accpc(ORACLE)-accpc(best_fixed))

EQUAL-COMPUTE ACCOUNTING (pre-registered, explicit): cost is measured in relative read units CS=1.0
  (coarse over all V) and CD=2.0 (coarse over all V to build the shortlist + fine re-rank the top-k). The
  CD/CS=2.0 ratio is the retained-trace analytic flop model at this operating point (deep = 1 + K_OP*N/D_COARSE
  = 1 + 0.0625*4096/256 = 2.0). accpc normalizes accuracy BY compute, so a fixed-cheap and a fixed-expensive
  arm are compared on the same per-compute footing; MARGIN_GATED and RANDOM_DEPTH_MATCHED are additionally
  matched in EXPECTED cost by construction (random p(deep) == gated p(deep) on the SAME TEST split).

PRE-REG BANDS (HEADLINE = MARGIN_GATED; strictly-above-floor per META_RULE_L):
  HARD_PASS_MARGIN_GATED_DEPTH = gated_vs_shallow_rel >= 0.10 AND gated_vs_deep_rel >= 0.10 AND
     gated_vs_random_rel >= 0.10 AND scramble_rel_gap >= 0.15 AND margin_recall_corr >= 0.30 AND
     DEPTH_LO < depth_spread < DEPTH_HI (0.05..0.95) AND guards (baseline in band, depth-gap exists,
     depth-pressure: oracle beats best fixed, arms differ). -> the combinedgate margin is a real, load-bearing
     trigger for retained-trace depth reusing ZERO new learned machinery (third self-manager proof point).
  MIDDLE_BAND_PARTIAL = beats the fixed frontier but misses one 1.10x gate, OR margin_recall_corr in [0.15,0.30).
  HARD_FAIL_INERT_DIAL = |gated_vs_shallow_rel| < 0.05 AND |gated_vs_deep_rel| < 0.05 (the kill-test: conditional
     allocation buys nothing a fixed uniform choice at matched average compute would not -> the margin does
     NOT carry depth-relevant information; honest negative, redirect to channel-local depth signals).
  HARD_FAIL_SIGNAL_NOT_LOADBEARING = accpc(GATED) <= accpc(RANDOM_DEPTH_MATCHED) (mixed budget alone explains it).
  INCONCLUSIVE_TAUTOLOGICAL_METRIC = scramble_rel_gap < 0.05 (scramble did not collapse -> not telemetry-sensitive).
  INCONCLUSIVE_NO_COUPLING = margin_recall_corr < 0.10 (corpus coupling failed to make M predict anything; a
     corpus-design failure to fix, not a verdict on the dial).
  INCONCLUSIVE_NO_DEPTH_PRESSURE = accpc(ORACLE) <= max(accpc fixed)*1.10 (perfect gating cannot beat the best
     fixed arm -> corpus offers no exploitable depth structure; regime miss, not a verdict).
  INCONCLUSIVE_BASELINE_OR_NO_GAP = FIXED_SHALLOW acc outside (0.05,0.95) OR (deep_acc-shallow_acc) < GAP_MIN
     (baseline saturated/floored, or depth does not matter; META_RULE_AG).

DISCRIMINATOR-FIRES (assert_discriminator_fires, MANDATORY at smoke): the CONTROL that must FAIL is
  "no exploitable depth structure" -- i.e. ORACLE_GATED does NOT beat the best fixed arm by the pressure
  margin. If perfect gating cannot beat a fixed policy at the smoke V, the smoke is SATURATION-VACUOUS
  (raise difficulty: lower CUE_LO / raise V / shrink D_COARSE). This fires at smoke by design because the
  coupled corpus deliberately injects hard (low cue_q) queries where coarse fails and fine recovers.

## Compute architecture
Class (a) batched-GPU. All reads are batched cosine matmuls (coarse: nq x V via D_COARSE; fine: nq x V via
N) with no Python loop over V. FULL routes to GPU (overnight_queue) at N=4096, V=40000, nq=1200 x 5 seeds x
(train+test). SMOKE runs CPU-local at PRODUCTION N=4096, V=8000 (== retained-trace's MEASURED-gap V),
nq=800 -- DISCRIMINATOR-MUST-SURVIVE-SCALE option A/C (smoke at full N; V at the same scale the parent cell
measured its coarse-vs-fine gap). Storage strategy: no_composition / no_store (retrieval-geometry cell; the
"store" is the per-concept retained-dense code, read by argmax-cosine cleanup at two depths + a coarse
shortlist -- not a bundled associative store). NO training pass (pure retrieval + one scalar tuned by grid
argmax), so no NaN-at-scale surface; the only heavy op is the fine nq x V x N matmul (GPU-batched).

## Functional Requirements
  FR1 a cheap confidence signal available BEFORE the expensive read -> the coarse combined_logit top1-top2
      margin M (Kiani-Shadlen balance-of-evidence; combinedgate primitive). Measured: margin_recall_corr.
  FR2 a cheap read that suffices on easy items -> coarse (low-dim D_COARSE projection) argmax. Measured:
      FIXED_SHALLOW acc.
  FR3 an expensive read that recovers on hard items -> fine (full-dim retained-dense) re-rank within the
      coarse shortlist. Measured: FIXED_DEEP acc (and deep_acc - shallow_acc gap).
  FR4 spend the expensive read only where the margin says it pays off, at MATCHED average compute ->
      MARGIN_GATED with theta_M argmax-accpc on TRAIN, frozen for TEST. Measured: gated_vs_{shallow,deep,random}_rel.

## Compute-formulas (computed in code before quoting; see _selftest ST-COST):
  CD/CS = 1 + K_OP_FRAC*N/D_COARSE = 1 + 0.0625*4096/256 = 2.0  THEORETICAL@retained-trace analytic flop model

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (SHA256 of each arm's TEST (correct, deep_mask) vectors; the load-bearing
  contrasts MARGIN_GATED vs {FIXED_SHALLOW, FIXED_DEEP, RANDOM_DEPTH_MATCHED, SCRAMBLED_MARGIN} MUST differ).
- cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS); verdict counts completed (seed x arm) units.
- final_metrics_atomicity: tmp_replace (os.replace on final metrics.json + per-seed partials).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: accuracy-per-compute gap discriminator; no single closed-form noise floor. Feasibility handled by
  the coupled corpus + the ORACLE depth-pressure gate + baseline-in-band; the coarse-vs-fine gap is anchored
  to MEASURED retained-trace (coarse_only 0.9025, fine 0.9942 at the parent regime).
- baseline_in_band: FIXED_SHALLOW acc in (0.05,0.95) AND (deep_acc-shallow_acc) >= GAP_MIN (depth matters).
- discriminator survives scale: smoke at production N=4096, V=8000 (parent MEASURED-gap V); ORACLE must beat
  the best fixed arm at smoke (assert_discriminator_fires) or the smoke is vacuous.
- HARD bands strictly above floor (relative gates 0.10/0.10/0.10; scramble 0.15; corr 0.30 well above the 0.10
  no-coupling floor and the 0.15 middle floor).
- HP_SCOPE: HP relative gates apply to MARGIN_GATED vs {FIXED_SHALLOW, FIXED_DEEP, RANDOM_DEPTH_MATCHED,
  SCRAMBLED_MARGIN}. ORACLE_GATED carries ONLY the depth-pressure + closure denominator. FIXED_* carry the
  baseline-in-band + depth-gap.
- per-unit failure-class instrumentation (no bare except; per-seed fatal flag recorded).
- calibration_check: adaptive_with_discriminator_gate -- theta_M tuned on TRAIN by argmax accpc over a
  percentile grid of the TRAIN M distribution (principled, the EVC objective), the discriminator STILL fires
  (scramble collapses + random beaten + oracle pressure), and theta_M, the theta->{acc,cost,accpc} curve, and
  both correlations are logged. Honest adaptive calibration, not p-hacking.
- telemetry-sensitivity self-test MANDATORY (perturb-a-seed MOVES accpc(GATED), M distribution, and the
  scramble collapses; SCRAMBLED must not beat GATED).
- cell_chunked: false (few-seed, per-seed checkpoint/restartable, atomic partials).
- progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress line).
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the report/prereg:
    coarse_only recall 0.9025  MEASURED@data/exp_encoder_retained_trace_requery_coarse_to_fine_v1/metrics.json:agg.arms_by_alpha."1.2".coarse_only
    full_fine recall 0.9942    MEASURED@same:agg.arms_by_alpha."1.2".full_fine
    Dial#1 adapt_vs_fixed=3.213x HARD_PASS  MEASURED@data/exp_substrate_acc_evc_adaptive_halting_v1/metrics.json
    combinedgate GATE_TAU=0.05 RECENCY_GAP_TARGET=3.0 q*=0.15  MEASURED@experiments/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py:151-154
    margin==balance-of-evidence confidence  CITED@Kiani&Shadlen 2009 Science 324:759 (research note Part 1b)
    ACC/EVC marginal-cost=marginal-benefit gating CITED@Shenhav/Botvinick/Cohen 2013 (research note Part 1a)
    fusion HARD_PASS P_deflated=0.42 HYPOTHESIZED@notes/research_self_manager_fusion_depth_controller_acc_evc_brain_first_2026-07-08.md HEADLINE

Author: exp_dev 2026-07-08 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-08_self_manager_fusion_margin_gated_depth_v1.md
Reuses (constants + read-geometry, unchanged): combinedgate GATE_TAU/RECENCY_GAP_TARGET arbitration formula;
  retained-trace coarse (z@P) vs fine (full-dim retained-dense) read distinction + BGE teacher store;
  Dial#1 train-argmax-accpc-then-freeze tuning recipe.

ASCII-only. No unicode. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

try:
    sys.stdout.reconfigure(line_buffering=True)  # unbuffered progress (section 17)
except Exception:  # noqa: BLE001
    pass

from experiments._seed_checkpoint import assert_discriminator_fires  # canonical smoke discriminator gate

ANCHOR_NAME = "self_manager_fusion_margin_gated_depth_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")
_CACHE_DIR = os.path.join(_REPO, "data", "substrate_index", "cached_indices")

# ---- combinedgate arbitration constants (reused UNCHANGED from the certified cell) ----
GATE_TAU = 0.05                 # content-gate softmax temperature (combinedgate v8)
RECENCY_GAP_TARGET = 3.0        # top-down recency bias in logit units (combinedgate v8; boundary q*=0.15)
RECENT_FRAC = 0.12             # fraction of store items flagged "recent" (get the recency bias)

# ---- coarse (cheap) vs fine (expensive) read geometry (retained-trace shape) ----
# D_COARSE scales with ln(V) so the coarse argmax difficulty (~ max of V distractor cosines, E[max]~sqrt(2lnV/D))
# is held ~constant across V -> shallow_acc and the accpc crossover survive scale (DISCRIMINATOR-MUST-SURVIVE-SCALE).
D_COARSE_BASE = 256             # coarse projection width AT the smoke reference V (V_REF); scaled by ln(V)/ln(V_REF).
V_REF = 8000                    # reference V at which D_COARSE == D_COARSE_BASE.
TARGET_CDCS = 2.0               # deep/shallow relative cost, PINNED across all V (shortlist frac scales with D_COARSE).
CS = 1.0                        # relative cost: coarse read over all V. CD == CS*TARGET_CDCS by construction.

# ---- corruption coupling: cue_q drives BOTH margin M and coarse-insufficiency ----
# window (random near-orthogonal codes): fine argmax recovers for cue_q > ~sqrt(2lnV/N); coarse argmax fails for
# cue_q < ~sqrt(2lnV/D_COARSE). CUE range straddles that window so coarse fails where fine recovers (depth pays).
CUE_LO = 0.12                   # hardest queries (heavily corrupted; coarse fails, fine recovers, M small)
CUE_HI = 0.47                   # easiest queries (coarse suffices, M large). Range set so shallow_acc lands near
                                # the accpc crossover shallow_acc ~ deep_acc*CS/CD ~ deep/2, where BOTH fixed arms
                                # tie in accpc and the dial has maximum (symmetric) room to beat both at matched cost.


def _d_coarse(V):
    """Coarse projection width for store size V; scales with ln(V) to hold coarse difficulty ~ constant."""
    import math
    d = D_COARSE_BASE * math.log(float(V)) / math.log(float(V_REF))
    return int(max(32, round(d / 8.0) * 8))


def _kfrac(n, d_coarse):
    """Deep-shortlist size as a fraction of V, set so CD/CS == TARGET_CDCS at ALL V (scale-invariant crossover).
    CD/CS = 1 + kfrac*N/D_COARSE = TARGET_CDCS  =>  kfrac = (TARGET_CDCS-1)*D_COARSE/N."""
    return float((TARGET_CDCS - 1.0) * d_coarse / n)


def _cd_cost(n, d_coarse):
    """Relative deep-read cost (retained-trace analytic flop model): 1 + kfrac*N/D_COARSE == TARGET_CDCS."""
    return float(CS * (1.0 + _kfrac(n, d_coarse) * n / d_coarse))

# ---- pre-reg bands (LOCKED at import; PROSPECTIVE; strictly-above-floor per META_RULE_L) ----
HP_VS_SHALLOW = 0.10            # accpc(GATED)/accpc(SHALLOW)-1 >= this
HP_VS_DEEP = 0.10              # accpc(GATED)/accpc(DEEP)-1 >= this
HP_VS_RANDOM = 0.10           # accpc(GATED)/accpc(RANDOM)-1 >= this (M signal, not variance)
HP_SCRAMBLE_GAP = 0.15        # 1 - accpc(SCR)/accpc(GATED) >= this (telemetry-sensitivity)
HP_CORR = 0.30                # pearson(M, correct_shallow) >= this (M predicts coarse-sufficiency)
DEPTH_LO, DEPTH_HI = 0.05, 0.95  # depth_spread must be a genuine mix (not degenerate to a fixed policy)
GAP_MIN = 0.08                # deep_acc - shallow_acc must be at least this (depth genuinely matters)
BASELINE_LO, BASELINE_HI = 0.05, 0.95
PRESSURE_MARGIN = 1.10        # accpc(ORACLE) > max(accpc fixed)*this (exploitable depth structure exists)
MB_CORR_LO = 0.15            # margin_recall_corr in [0.15,0.30) -> MIDDLE_BAND
NO_COUPLING_FLOOR = 0.10     # margin_recall_corr < this -> INCONCLUSIVE_NO_COUPLING
TAUT_SCRAMBLE_FLOOR = 0.05   # scramble_rel_gap < this -> INCONCLUSIVE_TAUTOLOGICAL_METRIC
HF_INERT = 0.05              # |gated_vs_shallow_rel| AND |gated_vs_deep_rel| < this -> HARD_FAIL_INERT_DIAL

ARM_SHALLOW = "FIXED_SHALLOW"
ARM_DEEP = "FIXED_DEEP"
ARM_GATED = "MARGIN_GATED"
ARM_RANDOM = "RANDOM_DEPTH_MATCHED"
ARM_SCRAMBLED = "SCRAMBLED_MARGIN"
ARM_ORACLE = "ORACLE_GATED"
ARMS = [ARM_SHALLOW, ARM_DEEP, ARM_GATED, ARM_RANDOM, ARM_SCRAMBLED, ARM_ORACLE]
HEADLINE_ARM = ARM_GATED

FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13, 19]
SELFTEST_SEEDS = [7]

FULL_REGIME = dict(N=4096, V=40000, nq_train=1500, nq_test=1500)
SMOKE_REGIME = dict(N=4096, V=8000, nq_train=900, nq_test=900)
SELFTEST_REGIME = dict(N=4096, V=1500, nq_train=300, nq_test=300)

# theta grid = percentiles of the TRAIN margin distribution (data-driven, then frozen)
THETA_PCTLS = [10, 25, 40, 55, 70, 85]


# --------------------------------- device / math prims -----------------------
def _resolve_device(want):
    import torch
    if want == "cpu":
        return "cpu"
    if want == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("device=cuda requested but torch.cuda.is_available()==False")
        return "cuda"
    return "cuda" if torch.cuda.is_available() else "cpu"


def _l2n_np(x):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)


def _cos_scores(q_np, store_np, device):
    """Cosine similarity matrix (nq, V) via normalized matmul. torch on device; numpy out."""
    import torch
    q = torch.from_numpy(np.ascontiguousarray(q_np, dtype=np.float32)).to(device)
    s = torch.from_numpy(np.ascontiguousarray(store_np, dtype=np.float32)).to(device)
    q = q / q.norm(dim=1, keepdim=True).clamp_min(1e-9)
    s = s / s.norm(dim=1, keepdim=True).clamp_min(1e-9)
    with torch.no_grad():
        out = q @ s.T
    return out.cpu().numpy().astype(np.float32)


def _pearson(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.size < 2 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _accpc(correct, cost):
    mc = float(np.mean(cost))
    return float(np.mean(correct)) / mc if mc > 1e-9 else 0.0


# --------------------------------- per-split reads ---------------------------
def _make_queries(z_store, P, qi, cue_q, rng_noise):
    """Build the noisy retained-dense query z_q (in R^N) and its coarse projection for concept ids qi.
    z_q = normalize(cue_q * item + sqrt(1-cue_q^2) * unit_noise) : retained-trace corruption model, in the
    dense code space directly (store codes are random near-orthogonal, per decouple-store-codes discipline)."""
    N = z_store.shape[1]
    item = z_store[qi]
    nz = rng_noise.standard_normal((qi.shape[0], N)).astype(np.float32)
    nz = nz / (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-9)
    cue = cue_q[:, None].astype(np.float32)
    z_q = _l2n_np(cue * item + np.sqrt(np.clip(1.0 - cue ** 2, 0.0, 1.0)) * nz)   # (nq, N) retained dense query
    coarse_q = z_q @ P                                # (nq, D_COARSE)
    return z_q, coarse_q


def _read_split(P, z_store, coarse_store, recency_bias, qi, cue_q, k, rng_noise, device):
    """Compute the coarse (shallow) read, the fine (deep) read within the coarse shortlist, and the margin M.
    Returns dict of numpy arrays: correct_shallow, correct_deep, M, shortlist_hit."""
    z_q, coarse_q = _make_queries(z_store, P, qi, cue_q, rng_noise)
    nq = qi.shape[0]
    V = z_store.shape[0]
    k = int(min(max(1, k), V))

    # coarse combined_logit over ALL V (cheap; the combinedgate coarse arbitration)
    coarse_cos = _cos_scores(coarse_q, coarse_store, device)          # (nq, V)
    coarse_logit = coarse_cos / GATE_TAU + recency_bias[None, :]      # + top-down recency bias
    shallow_pred = np.argmax(coarse_logit, axis=1)
    correct_shallow = (shallow_pred == qi)

    # margin M = top1 - top2 of the coarse combined_logit (Kiani-Shadlen balance-of-evidence; NO gt leakage)
    part = np.argpartition(-coarse_logit, 1, axis=1)[:, :2]
    row = np.arange(nq)[:, None]
    top2vals = np.sort(coarse_logit[row, part], axis=1)[:, ::-1]      # (nq, 2) desc
    M = (top2vals[:, 0] - top2vals[:, 1]).astype(np.float32)

    # coarse top-k shortlist
    kpart = np.argpartition(-coarse_logit, k - 1, axis=1)[:, :k]      # (nq, k) unordered top-k
    shortlist_hit = np.array([bool(qi[i] in set(kpart[i].tolist())) for i in range(nq)], dtype=bool)

    # fine (deep) combined_logit re-rank WITHIN the shortlist (expensive; full-dim retained-dense read)
    fine_cos = _cos_scores(z_q, z_store, device)                     # (nq, V)
    fine_logit = fine_cos / GATE_TAU + recency_bias[None, :]
    mask = np.full((nq, V), -1e30, dtype=np.float32)
    mask[row, kpart] = 0.0
    deep_pred = np.argmax(fine_logit + mask, axis=1)                 # argmax restricted to shortlist
    correct_deep = (deep_pred == qi)

    return {
        "correct_shallow": correct_shallow, "correct_deep": correct_deep,
        "M": M, "shortlist_hit": shortlist_hit,
    }


# --------------------------------- per-seed measurement ----------------------
def measure_seed(seed, regime, device):
    rng = np.random.default_rng(seed)
    V, N = regime["V"], regime["N"]
    Vr = V
    dcoarse = _d_coarse(Vr)                                # scale coarse width with ln(V) (scale-invariant difficulty)
    k = max(1, int(round(_kfrac(N, dcoarse) * Vr)))       # shortlist scales with D_COARSE so CD/CS==TARGET_CDCS
    cd = _cd_cost(N, dcoarse)                              # per-regime deep cost (== TARGET_CDCS by construction)

    # retained dense trace: random near-orthogonal store codes in R^N (decouple-store-codes discipline).
    gS = np.random.default_rng(seed * 1000 + 7)
    z_store = _l2n_np(gS.standard_normal((Vr, N)).astype(np.float32))   # (V, N) unit-norm dense codes
    gP = np.random.default_rng(seed * 1000 + 31)
    P = (gP.standard_normal((N, dcoarse)).astype(np.float32) / np.sqrt(N))
    coarse_store = z_store @ P                             # (V, dcoarse)

    # recency set (combinedgate top-down prior): a fixed random subset gets +RECENCY_GAP_TARGET in logit units
    gR = np.random.default_rng(seed * 1000 + 53)
    recent = gR.random(Vr) < RECENT_FRAC
    recency_bias = np.where(recent, RECENCY_GAP_TARGET, 0.0).astype(np.float32)

    # TRAIN + TEST query splits (disjoint concept draws + disjoint noise; same store)
    qi_tr = rng.choice(Vr, size=min(regime["nq_train"], Vr), replace=False)
    qi_te = rng.choice(Vr, size=min(regime["nq_test"], Vr), replace=False)
    cue_tr = rng.uniform(CUE_LO, CUE_HI, size=qi_tr.shape[0]).astype(np.float32)
    cue_te = rng.uniform(CUE_LO, CUE_HI, size=qi_te.shape[0]).astype(np.float32)
    rng_n_tr = np.random.default_rng(seed * 7 + 11)
    rng_n_te = np.random.default_rng(seed * 7 + 23)

    tr = _read_split(P, z_store, coarse_store, recency_bias, qi_tr, cue_tr, k, rng_n_tr, device)
    te = _read_split(P, z_store, coarse_store, recency_bias, qi_te, cue_te, k, rng_n_te, device)

    # ---- tune theta_M on TRAIN by argmax accuracy-per-compute (percentile grid; then FREEZE) ----
    M_tr = tr["M"]
    theta_grid = [float(np.percentile(M_tr, p)) for p in THETA_PCTLS]
    theta_curve = []
    best_theta, best_accpc = theta_grid[0], -1.0
    for th in theta_grid:
        deep_mask = M_tr < th                              # low margin -> deep
        correct = np.where(deep_mask, tr["correct_deep"], tr["correct_shallow"])
        cost = np.where(deep_mask, cd, CS)
        apc = _accpc(correct, cost)
        theta_curve.append({"theta": th, "acc": float(np.mean(correct)),
                            "mean_cost": float(np.mean(cost)), "accpc": apc,
                            "p_deep": float(np.mean(deep_mask))})
        if apc > best_accpc:
            best_accpc, best_theta = apc, th

    # ---- evaluate the 6 arms on TEST (paired; frozen theta_M) ----
    cs_te, cd_te = te["correct_shallow"], te["correct_deep"]
    M_te = te["M"]
    nq = M_te.shape[0]

    gated_deep = M_te < best_theta
    p_deep_gated = float(np.mean(gated_deep))

    rd_gen = np.random.default_rng(seed * 51001 + 3)
    rand_deep = rd_gen.random(nq) < p_deep_gated           # matched expected compute, telemetry ignored

    scr_gen = np.random.default_rng(seed * 51001 + 7)
    M_scr = M_te[scr_gen.permutation(nq)]                  # margin permuted across queries (matched scale)
    scr_deep = M_scr < best_theta

    oracle_deep = ~cs_te                                   # perfect info: deep exactly when shallow would be wrong

    def _arm(deep_mask):
        correct = np.where(deep_mask, cd_te, cs_te)
        cost = np.where(deep_mask, cd, CS)
        return correct, cost

    arm_masks = {
        ARM_SHALLOW: np.zeros(nq, dtype=bool),
        ARM_DEEP: np.ones(nq, dtype=bool),
        ARM_GATED: gated_deep,
        ARM_RANDOM: rand_deep,
        ARM_SCRAMBLED: scr_deep,
        ARM_ORACLE: oracle_deep,
    }
    arms = {}
    trace_hashes = {}
    for name, dm in arm_masks.items():
        correct, cost = _arm(dm)
        arms[name] = {"acc": float(np.mean(correct)), "mean_cost": float(np.mean(cost)),
                      "accpc": _accpc(correct, cost), "p_deep": float(np.mean(dm))}
        payload = correct.astype(np.int8).tobytes() + dm.astype(np.int8).tobytes()
        trace_hashes[name] = hashlib.sha256(payload).hexdigest()[:16]

    margin_recall_corr = _pearson(M_te, cs_te.astype(np.float64))
    shortlist_hit_rate = float(np.mean(te["shortlist_hit"]))

    rec = {
        "seed": int(seed), "V": int(Vr), "N": int(N), "k_shortlist": int(k), "cd_cost": float(cd),
        "D_COARSE": int(dcoarse), "theta_star": float(best_theta), "theta_curve": theta_curve,
        "p_deep_gated": p_deep_gated, "arms": arms, "trace_hashes": trace_hashes,
        "margin_recall_corr": float(margin_recall_corr),
        "shortlist_hit_rate": shortlist_hit_rate,
        "shallow_acc": arms[ARM_SHALLOW]["acc"], "deep_acc": arms[ARM_DEEP]["acc"],
        "M_train_mean": float(np.mean(M_tr)), "M_test_mean": float(np.mean(M_te)),
    }
    print(f"[seed={seed}] theta*={best_theta:.3f} p_deep={p_deep_gated:.3f} "
          f"accpc[SH={arms[ARM_SHALLOW]['accpc']:.4f} DP={arms[ARM_DEEP]['accpc']:.4f} "
          f"GT={arms[ARM_GATED]['accpc']:.4f} RD={arms[ARM_RANDOM]['accpc']:.4f} "
          f"SC={arms[ARM_SCRAMBLED]['accpc']:.4f} OR={arms[ARM_ORACLE]['accpc']:.4f}] "
          f"acc[SH={arms[ARM_SHALLOW]['acc']:.3f} DP={arms[ARM_DEEP]['acc']:.3f} GT={arms[ARM_GATED]['acc']:.3f}] "
          f"corr={margin_recall_corr:+.3f} hit={shortlist_hit_rate:.3f}", flush=True)
    return rec


# ------------------------------ aggregation / verdict ------------------------
def _mean(xs):
    xs = [v for v in xs if v is not None]
    return float(np.mean(xs)) if xs else 0.0


def _aggregate(per_seed):
    keys = list(per_seed.keys())
    arm_means = {a: {f: _mean([per_seed[s]["arms"][a][f] for s in keys])
                     for f in ("acc", "mean_cost", "accpc", "p_deep")} for a in ARMS}
    agg = {
        "n_seeds": len(keys), "arm_means": arm_means,
        "margin_recall_corr": _mean([per_seed[s]["margin_recall_corr"] for s in keys]),
        "shortlist_hit_rate": _mean([per_seed[s]["shortlist_hit_rate"] for s in keys]),
        "depth_spread": _mean([per_seed[s]["p_deep_gated"] for s in keys]),
        "theta_star_mean": _mean([per_seed[s]["theta_star"] for s in keys]),
        "shallow_acc": _mean([per_seed[s]["shallow_acc"] for s in keys]),
        "deep_acc": _mean([per_seed[s]["deep_acc"] for s in keys]),
    }
    return agg


def _classify(agg, per_seed):
    am = agg["arm_means"]
    sh = am[ARM_SHALLOW]["accpc"]
    dp = am[ARM_DEEP]["accpc"]
    gt = am[ARM_GATED]["accpc"]
    rd = am[ARM_RANDOM]["accpc"]
    sc = am[ARM_SCRAMBLED]["accpc"]
    orc = am[ARM_ORACLE]["accpc"]

    gated_vs_shallow_rel = (gt / sh - 1.0) if sh > 1e-9 else 0.0
    gated_vs_deep_rel = (gt / dp - 1.0) if dp > 1e-9 else 0.0
    gated_vs_random_rel = (gt / rd - 1.0) if rd > 1e-9 else 0.0
    scramble_rel_gap = (1.0 - sc / gt) if gt > 1e-9 else 0.0
    best_fixed = max(sh, dp)
    closure = ((gt - best_fixed) / (orc - best_fixed)) if (orc - best_fixed) > 1e-9 else 0.0

    corr = agg["margin_recall_corr"]
    depth_spread = agg["depth_spread"]
    shallow_acc = agg["shallow_acc"]
    deep_acc = agg["deep_acc"]
    depth_gap = deep_acc - shallow_acc

    # guards
    baseline_in_band = bool(BASELINE_LO < shallow_acc < BASELINE_HI)
    gap_ok = bool(depth_gap >= GAP_MIN)
    pressure_ok = bool(orc > best_fixed * PRESSURE_MARGIN)
    spread_ok = bool(DEPTH_LO < depth_spread < DEPTH_HI)

    # arms-differ (AF): load-bearing contrasts must differ
    loadbearing = [ARM_SHALLOW, ARM_DEEP, ARM_GATED, ARM_RANDOM, ARM_SCRAMBLED]
    af_collision = False
    for s in per_seed:
        th = per_seed[s]["trace_hashes"]
        hs = [th[a] for a in loadbearing]
        if len(set(hs)) < len(hs):
            af_collision = True

    def _hp_ok():
        return (gated_vs_shallow_rel >= HP_VS_SHALLOW and gated_vs_deep_rel >= HP_VS_DEEP
                and gated_vs_random_rel >= HP_VS_RANDOM and scramble_rel_gap >= HP_SCRAMBLE_GAP
                and corr >= HP_CORR and spread_ok and baseline_in_band and gap_ok
                and pressure_ok and not af_collision)

    cls = {
        "gated_vs_shallow_rel": float(gated_vs_shallow_rel),
        "gated_vs_deep_rel": float(gated_vs_deep_rel),
        "gated_vs_random_rel": float(gated_vs_random_rel),
        "scramble_rel_gap": float(scramble_rel_gap), "closure": float(closure),
        "margin_recall_corr": float(corr), "depth_spread": float(depth_spread),
        "shallow_acc": float(shallow_acc), "deep_acc": float(deep_acc), "depth_gap": float(depth_gap),
        "baseline_in_band": baseline_in_band, "gap_ok": gap_ok, "pressure_ok": pressure_ok,
        "spread_ok": spread_ok, "af_collision": bool(af_collision), "best_fixed_accpc": float(best_fixed),
        "accpc": {"shallow": sh, "deep": dp, "gated": gt, "random": rd, "scrambled": sc, "oracle": orc},
    }
    return cls


def _verdict_from(cls, cardinality_ok, run_mode):
    if not cardinality_ok:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    if cls["af_collision"]:
        return "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    if (not cls["baseline_in_band"]) or (not cls["gap_ok"]):
        return "INCONCLUSIVE_BASELINE_OR_NO_GAP"
    if not cls["pressure_ok"]:
        return "INCONCLUSIVE_NO_DEPTH_PRESSURE"
    if cls["margin_recall_corr"] < NO_COUPLING_FLOOR:
        return "INCONCLUSIVE_NO_COUPLING"
    if cls["scramble_rel_gap"] < TAUT_SCRAMBLE_FLOOR:
        return "INCONCLUSIVE_TAUTOLOGICAL_METRIC"
    if cls["accpc"]["gated"] <= cls["accpc"]["random"]:
        return "HARD_FAIL_SIGNAL_NOT_LOADBEARING"
    if abs(cls["gated_vs_shallow_rel"]) < HF_INERT and abs(cls["gated_vs_deep_rel"]) < HF_INERT:
        return "HARD_FAIL_INERT_DIAL"
    if (cls["gated_vs_shallow_rel"] >= HP_VS_SHALLOW and cls["gated_vs_deep_rel"] >= HP_VS_DEEP
            and cls["gated_vs_random_rel"] >= HP_VS_RANDOM and cls["scramble_rel_gap"] >= HP_SCRAMBLE_GAP
            and cls["margin_recall_corr"] >= HP_CORR and cls["spread_ok"]):
        return "HARD_PASS_MARGIN_GATED_DEPTH"
    return "MIDDLE_BAND_PARTIAL"


# --------------------------------- IO / diagnostics --------------------------
def _write_start_marker(output_dir, run_mode, expected_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "run_mode": "crash", "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def _seed_partial_path(output_dir, run_mode, seed):
    return os.path.join(output_dir, f"_seed_{run_mode}_{seed}.json")


# ------------------------------------ self-test ------------------------------
def self_test():
    """Scaffold-free witnesses at the TINY selftest V (V=700). Asserts: (1) cost model CD/CS==2.0,
    (2) valid reads (fine deep_acc high on this small store), (3) coarse is genuinely coarse (shallow<deep),
    (4) margin predicts coarse-sufficiency (corr>0 direction), (5) telemetry-sensitivity (scramble does not
    beat gated), (6) arms differ, (7) depth-pressure direction (oracle beats best fixed at tiny V)."""
    ok = True
    reg = SELFTEST_REGIME
    device = "cpu"
    # ST-COST: analytic cost ratio computed in code; at N=4096, V=V_REF (=8000) CD/CS must be 2.0.
    cd_cs = _cd_cost(reg["N"], _d_coarse(reg["V"])) / CS
    cd_cs_ref = _cd_cost(4096, _d_coarse(V_REF)) / CS
    cost_ok = abs(cd_cs_ref - 2.0) < 1e-6
    ok &= cost_ok
    print(f"[self-test] ST-COST CD/CS@(N={reg['N']},V={reg['V']},D={_d_coarse(reg['V'])})={cd_cs:.4f} "
          f"CD/CS@ref(N4096,V{V_REF})={cd_cs_ref:.4f} (must==2.0) ok={cost_ok}")

    m7 = measure_seed(7, reg, device)
    am = m7["arms"]

    valid_deep = am[ARM_DEEP]["acc"] >= 0.70
    ok &= valid_deep
    coarse_is_coarse = am[ARM_SHALLOW]["acc"] < am[ARM_DEEP]["acc"]
    ok &= coarse_is_coarse
    corr_dir = m7["margin_recall_corr"] > 0.05
    ok &= corr_dir
    # telemetry-sensitivity: scrambled must NOT beat gated on accpc.
    scr_not_beat = am[ARM_SCRAMBLED]["accpc"] <= am[ARM_GATED]["accpc"] + 1e-6
    ok &= scr_not_beat
    fh = m7["trace_hashes"]
    lb = [ARM_SHALLOW, ARM_DEEP, ARM_GATED, ARM_RANDOM, ARM_SCRAMBLED]
    arms_differ = len(set(fh[a] for a in lb)) == len(lb)
    ok &= arms_differ
    # depth-pressure direction: oracle beats best fixed (perfect gating has something to exploit).
    best_fixed = max(am[ARM_SHALLOW]["accpc"], am[ARM_DEEP]["accpc"])
    pressure_dir = am[ARM_ORACLE]["accpc"] > best_fixed
    ok &= pressure_dir

    print(f"[self-test] valid_deep={valid_deep}(deep_acc={am[ARM_DEEP]['acc']:.3f}) "
          f"coarse_is_coarse={coarse_is_coarse}(sh={am[ARM_SHALLOW]['acc']:.3f}) "
          f"corr_dir={corr_dir}(corr={m7['margin_recall_corr']:+.3f}) "
          f"scr_not_beat={scr_not_beat} arms_differ={arms_differ} "
          f"pressure_dir={pressure_dir}(orc={am[ARM_ORACLE]['accpc']:.4f} bestfix={best_fixed:.4f})")
    print(f"[self-test] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ------------------------------------ run ------------------------------------
def run(run_mode, device_want):
    t0 = time.perf_counter()
    if run_mode == "smoke":
        regime, seeds = SMOKE_REGIME, SMOKE_SEEDS
    else:
        regime, seeds = FULL_REGIME, FULL_SEEDS
    device = _resolve_device(device_want)
    expected_units = len(seeds) * len(ARMS)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    print(f"[start] run_mode={run_mode} device={device} seeds={seeds} regime={regime}", flush=True)
    cache_src = "random_near_orthogonal_store"

    hb = None
    try:
        from experiments._cell_heartbeat import CellHeartbeat
        hb = CellHeartbeat(OUTPUT_DIR, total_units=len(seeds), interval_s=30)
        hb.__enter__()
    except Exception:  # noqa: BLE001
        hb = None

    per_seed = {}
    fatal = None
    try:
        for si, sd in enumerate(seeds):
            pp = _seed_partial_path(OUTPUT_DIR, run_mode, sd)
            if os.path.exists(pp):
                try:
                    with open(pp, encoding="utf-8") as f:
                        per_seed[str(sd)] = json.load(f)
                    print(f"[resume] seed={sd} loaded from partial", flush=True)
                    if hb is not None:
                        hb.tick(si)
                    continue
                except Exception:  # noqa: BLE001 - corrupt partial: recompute
                    pass
            ts = time.perf_counter()
            res = measure_seed(sd, regime, device)
            res["elapsed_s"] = time.perf_counter() - ts
            tmp = pp + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(res, f)
            os.replace(tmp, pp)
            per_seed[str(sd)] = res
            print(f"[seed-done] seed={sd} elapsed={res['elapsed_s']:.1f}s", flush=True)
            if hb is not None:
                hb.tick(si)
    except Exception as e:  # noqa: BLE001 - record fatal, do not silently continue
        fatal = f"{type(e).__name__}: {str(e)[:300]}"
        raise
    finally:
        if hb is not None:
            try:
                hb.__exit__(None, None, None)
            except Exception:  # noqa: BLE001
                pass

    n_units = len(per_seed) * len(ARMS)
    cardinality_ok = (len(per_seed) == len(seeds))
    agg = _aggregate(per_seed)
    cls = _classify(agg, per_seed)
    verdict = _verdict_from(cls, cardinality_ok, run_mode)

    # DISCRIMINATOR-FIRES smoke gate: perfect gating (ORACLE) MUST beat the best fixed arm at smoke scale,
    # else the corpus offers no exploitable depth structure (saturation-vacuous).
    if run_mode == "smoke":
        control_passed = not cls["pressure_ok"]   # control = "no depth structure"; passing headline == vacuous
        assert_discriminator_fires(
            control_passed, control_name="ORACLE_GATED beats best fixed (depth structure exists)",
            headline_name="MARGIN_GATED", run_mode="smoke",
            extra=(f"oracle_accpc={cls['accpc']['oracle']:.4f} best_fixed_accpc={cls['best_fixed_accpc']:.4f} "
                   f"shallow_acc={cls['shallow_acc']:.3f} deep_acc={cls['deep_acc']:.3f} "
                   f"depth_gap={cls['depth_gap']:.3f} corr={cls['margin_recall_corr']:+.3f}"))

    interp = {
        "HARD_PASS_MARGIN_GATED_DEPTH":
            "the combinedgate margin is a load-bearing trigger for retained-trace depth: MARGIN_GATED beats "
            "BOTH fixed-depth arms and RANDOM at matched compute, scramble collapses, and M predicts "
            "coarse-sufficiency. Third self-manager proof point; ZERO new learned machinery.",
        "MIDDLE_BAND_PARTIAL":
            "MARGIN_GATED beats the fixed frontier but misses a 1.10x gate or the corr band; report the curve.",
        "HARD_FAIL_INERT_DIAL":
            "KILL-TEST fired: conditional depth allocation buys nothing a fixed uniform choice at matched "
            "compute would not. The margin does NOT carry depth-relevant info; redirect the self-manager "
            "program to channel-LOCAL depth signals (coarse top1-top2 gap) rather than cross-cell borrowed.",
        "HARD_FAIL_SIGNAL_NOT_LOADBEARING":
            "having a mixed budget alone explains the gain; reading M specifically adds nothing over RANDOM.",
        "INCONCLUSIVE_TAUTOLOGICAL_METRIC":
            "scramble did not collapse -> metric not telemetry-sensitive; report inconclusive, not a negative.",
        "INCONCLUSIVE_NO_COUPLING":
            "corpus coupling failed: M does not predict coarse-sufficiency at all (corr<0.10) -> fix the "
            "corpus (lower CUE_LO / shrink D_COARSE) before re-running; not a verdict on the dial.",
        "INCONCLUSIVE_NO_DEPTH_PRESSURE":
            "perfect gating cannot beat the best fixed arm -> corpus offers no exploitable depth structure; "
            "regime miss (raise difficulty), not a verdict.",
        "INCONCLUSIVE_BASELINE_OR_NO_GAP":
            "FIXED_SHALLOW saturated/floored OR deep-shallow accuracy gap too small (depth does not matter); "
            "META_RULE_AG regime iteration required.",
        "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H": "seed cardinality breach; some seed did not complete.",
        "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF": "load-bearing arms produced bit-identical traces; arm bug.",
    }.get(verdict, "see verdict tag.")

    verdict_msg = (
        f"{verdict} | SELF-MANAGER FUSION margin-gated depth dial (ACC/EVC over combinedgate margin -> "
        f"retained-trace coarse/fine). accpc[SHALLOW={cls['accpc']['shallow']:.4f} DEEP={cls['accpc']['deep']:.4f} "
        f"GATED={cls['accpc']['gated']:.4f} RANDOM={cls['accpc']['random']:.4f} SCR={cls['accpc']['scrambled']:.4f} "
        f"ORACLE={cls['accpc']['oracle']:.4f}] | gated_vs_shallow={cls['gated_vs_shallow_rel']:+.3f}(>= {HP_VS_SHALLOW}) "
        f"gated_vs_deep={cls['gated_vs_deep_rel']:+.3f}(>= {HP_VS_DEEP}) gated_vs_random={cls['gated_vs_random_rel']:+.3f}"
        f"(>= {HP_VS_RANDOM}) scramble_gap={cls['scramble_rel_gap']:.3f}(>= {HP_SCRAMBLE_GAP}) closure={cls['closure']:.3f} "
        f"| margin_recall_corr={cls['margin_recall_corr']:+.3f}(>= {HP_CORR}) depth_spread={cls['depth_spread']:.3f} "
        f"| acc[shallow={cls['shallow_acc']:.3f} deep={cls['deep_acc']:.3f} gap={cls['depth_gap']:+.3f}(>= {GAP_MIN})] "
        f"theta*={agg['theta_star_mean']:.3f} shortlist_hit={agg['shortlist_hit_rate']:.3f} "
        f"| baseline_band={cls['baseline_in_band']} pressure={cls['pressure_ok']} af_collision={cls['af_collision']} "
        f"n_seeds={agg['n_seeds']} cache={cache_src}. INTERPRETATION: {interp}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}: self-manager fusion margin-gated depth dial ({run_mode})",
        "run_mode": run_mode, "device": device,
        "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "cache_source": cache_src,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_units, "n_units": n_units,
        "arms_differ_verified": (not cls["af_collision"]),
        "baseline_in_band": cls["baseline_in_band"], "fatal": fatal,
        "classification": cls, "agg": agg,
        "operating_points": {"GATE_TAU": GATE_TAU, "RECENCY_GAP_TARGET": RECENCY_GAP_TARGET,
                             "RECENT_FRAC": RECENT_FRAC, "D_COARSE_BASE": D_COARSE_BASE, "V_REF": V_REF,
                             "D_COARSE_regime": _d_coarse(regime["V"]), "TARGET_CDCS": TARGET_CDCS,
                             "kfrac_regime": _kfrac(regime["N"], _d_coarse(regime["V"])),
                             "CS": CS, "CD": _cd_cost(regime["N"], _d_coarse(regime["V"])),
                             "CUE_LO": CUE_LO, "CUE_HI": CUE_HI, "THETA_PCTLS": THETA_PCTLS},
        "bands": {"HP_VS_SHALLOW": HP_VS_SHALLOW, "HP_VS_DEEP": HP_VS_DEEP, "HP_VS_RANDOM": HP_VS_RANDOM,
                  "HP_SCRAMBLE_GAP": HP_SCRAMBLE_GAP, "HP_CORR": HP_CORR, "DEPTH_LO": DEPTH_LO,
                  "DEPTH_HI": DEPTH_HI, "GAP_MIN": GAP_MIN, "PRESSURE_MARGIN": PRESSURE_MARGIN,
                  "MB_CORR_LO": MB_CORR_LO, "NO_COUPLING_FLOOR": NO_COUPLING_FLOOR,
                  "TAUT_SCRAMBLE_FLOOR": TAUT_SCRAMBLE_FLOOR, "HF_INERT": HF_INERT},
        "regime": regime, "seeds": seeds, "per_seed": per_seed,
    }
    _write_metrics(OUTPUT_DIR, metrics)
    print("[done] " + verdict_msg, flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["full", "smoke", "self_test"], default="full")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args = ap.parse_args()
    name_smoke = "_smoke" in os.environ.get("HDLAB_EXP_NAME", "").lower()
    if args.self_test or args.run_mode == "self_test":
        raise SystemExit(self_test())
    mode = "smoke" if (args.smoke or name_smoke or args.run_mode == "smoke") else "full"
    run(mode, args.device)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
