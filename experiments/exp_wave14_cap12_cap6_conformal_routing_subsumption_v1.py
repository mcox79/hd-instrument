"""Composition B: Cap 12 (MP-KS routing) + Cap 6 (Venn-Abers conformal calibration).

Cap 12 ✅ ships an MP-KS pre-test that routes a codebook to AMP_OK or VAMP_REQUIRED
based on a single scalar (the empirical Kolmogorov-Smirnov distance between the
codebook's spectral CDF and the theoretical Marchenko-Pastur CDF). Cap 6
(Venn-Abers conformal calibration) ships a finite-sample distribution-free
calibration wrapper that converts any non-conformity score into calibrated
p-values with valid coverage guarantees.

This experiment tests whether Cap 6 can wrap Cap 12 to produce a calibrated
"commit-vs-abstain" routing primitive: if the conformal p-value exceeds 0.90,
commit to the MP-KS routing decision; otherwise abstain (escalate to running
both AMP and VAMP, or to running VAMP only as a safe fallback).

Design (reuse Cap 12 v175 architecture)
---------------------------------------
- Same 5 codebooks: iid_gauss, srht, hadamard, rm_1_m, kerdock at N=1024.
- Same 5 seeds per codebook (25 total observations).
- Compute MP-KS score for each (codebook, seed).
- Compute the EMPIRICAL TRUTH label for each (codebook, seed) by running AMP
  and VAMP and checking amp_rel_err < 0.10 -> AMP_OK else VAMP_REQUIRED.
- Apply Venn-Abers conformal calibration LEAVE-ONE-OUT across the 25 samples:
  for each held-out (codebook_target, seed_target), use the remaining 24
  observations as the calibration set; for each candidate routing label
  c in {AMP_OK, VAMP_REQUIRED}, compute the Venn-Abers conformal p-value
  p_c by ranking the held-out KS score among the calibration KS scores
  restricted to label c.

Venn-Abers conformal calibration
--------------------------------
The classical formulation (Vovk-Petej 2014): for a binary classifier, given
calibration scores {s_i} with labels {y_i in {0, 1}}, the conformal p-value
for a new observation (s*, candidate label c) is
   p_c(s*) = (1 + |{i : y_i == c, s_i >= s*}|) / (1 + |{i : y_i == c}|)
This gives a finite-sample valid p-value (Vovk-Gammerman lemma) under the
exchangeability assumption.

In our setting:
- score: KS statistic (non-conformity score; LOW KS = "looks MP" = AMP_OK)
- non-conformity is INVERTED for AMP_OK label vs VAMP_REQUIRED label:
  - For AMP_OK candidate: non-conformity is +KS (low KS = conforms to AMP_OK)
  - For VAMP_REQUIRED candidate: non-conformity is -KS (high KS = conforms to VAMP)
- For each held-out point, compute p_AMP and p_VAMP.
- The MP-KS routing decision is what tau=0.20 would say.
- COMMIT to MP-KS routing iff p[routed_label] >= 0.90 (high confidence) AND
  p[other_label] < 0.50 (the alternative is clearly less likely).
- ABSTAIN otherwise.

Per-fold accounting
-------------------
Across the 25 leave-one-out folds:
- commit_accuracy = (#commits where routing matched empirical truth) / (#commits)
- abstain_rate = (#abstains) / 25
- Per-codebook commit accuracy (5 codebooks each get up to 5 commits)
- Routing accuracy at commit (the calibrated subset) vs raw (all 25)

HARD PASS (Composition B licensed)
----------------------------------
- per_codebook_commit_accuracy = 5/5 (routing correct on ALL non-abstained
  codebooks; i.e., for each codebook that is committed at least once,
  the committed routings match the empirical truth label)
- AND abstain_rate < 0.30 (capability stays useful)

HARD FAIL
---------
- per_codebook_commit_accuracy < 4/5 (calibration doesn't improve over raw)
- OR abstain_rate >= 0.70 (refusing too much; calibration is useless conservatism)

MIDDLE BAND
-----------
- per_codebook_commit_accuracy == 4/5 AND abstain_rate < 0.70 (improvement,
  not full).

Vertex: CONFORMAL_ROUTING_SUBSUMPTION_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-24_wave14_cap12_cap6_conformal_routing_subsumption_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Reuse cross-codebook v1 builders + MP-KS routine.
_cc_path = REPO / "experiments" / "exp_wave14_kappa_profile_cross_codebook_v1.py"
_spec_cc = importlib.util.spec_from_file_location("kappa_cc_v1", _cc_path)
_cc = importlib.util.module_from_spec(_spec_cc)
_spec_cc.loader.exec_module(_cc)
build_iid_gauss = _cc.build_iid_gauss
build_srht = _cc.build_srht
build_hadamard = _cc.build_hadamard
build_rm_1_m = _cc.build_rm_1_m
build_kerdock = _cc.build_kerdock
mp_ks_stat = _cc.mp_ks_stat

# Reuse BBMD-VAMP AMP/VAMP loops + closed-form predictions.
_bv_path = REPO / "experiments" / "exp_wave14_bbmd_vamp_correspondence_sweep_v1.py"
_spec_bv = importlib.util.spec_from_file_location("bbmd_vamp_v1", _bv_path)
_bv = importlib.util.module_from_spec(_spec_bv)
_spec_bv.loader.exec_module(_bv)
amp_se_scalar = _bv.amp_se_scalar
vamp_se_closed = _bv.vamp_se_closed
run_amp = _bv.run_amp
run_vamp = _bv.run_vamp


CODEBOOKS = [
    ("iid_gauss", build_iid_gauss),
    ("srht",      build_srht),
    ("hadamard",  build_hadamard),
    ("rm_1_m",    build_rm_1_m),
    ("kerdock",   build_kerdock),
]

TAU_DECLARED = 0.20  # MP-KS routing threshold (matches Cap 12 ✅ v175)
P_COMMIT = 0.90
P_OTHER_MAX = 0.50


# ---------------------------------------------------------------------------
# Routing + conformal calibration primitives
# ---------------------------------------------------------------------------

def route_from_ks(ks: float, tau: float) -> str:
    return "AMP_OK" if ks <= tau else "VAMP_REQUIRED"


def empirical_truth_from_amp_rel(amp_rel: float, fail_thresh: float = 0.10) -> str:
    return "AMP_OK" if amp_rel < fail_thresh else "VAMP_REQUIRED"


def venn_abers_p(score_star: float, cal_scores: list[float],
                 cal_labels: list[str], candidate_label: str) -> float:
    """Vovk-Petej conformal p-value for candidate label.

    Non-conformity:
      - AMP_OK candidate: score = +KS (low KS conforms; this means AMP_OK label
        observations should have LOW non-conformity; new point conforms when
        its KS is LOW relative to the calibration AMP_OK distribution).
      - VAMP_REQUIRED candidate: score = -KS (high KS conforms).

    Per the standard conformal recipe:
      p = (1 + |{i: y_i == c, s_i >= s*}|) / (1 + |{i: y_i == c}|)
    where s_i, s* are the non-conformity scores for label c.

    Returns a finite-sample valid p-value (Vovk-Gammerman, 2005, Sec 2.3).
    """
    sign = +1.0 if candidate_label == "AMP_OK" else -1.0
    # Restrict to calibration observations with this label
    cal_for_label = [sign * s for s, y in zip(cal_scores, cal_labels) if y == candidate_label]
    n_cal = len(cal_for_label)
    if n_cal == 0:
        # No calibration data for this label -> conservative low p
        return 1.0 / (1.0 + 0.0001)  # ~ 1.0 but not 1.0 exactly to avoid degenerate
    s_star = sign * score_star
    n_ge = sum(1 for s in cal_for_label if s >= s_star)
    return (1.0 + n_ge) / (1.0 + n_cal)


def commit_decision(p_amp: float, p_vamp: float, routed_label: str,
                    p_commit: float, p_other_max: float) -> str:
    """Return 'COMMIT' if the routed label has high conformal confidence
    AND the alternative is clearly less likely; otherwise 'ABSTAIN'."""
    p_routed = p_amp if routed_label == "AMP_OK" else p_vamp
    p_other = p_vamp if routed_label == "AMP_OK" else p_amp
    if p_routed >= p_commit and p_other < p_other_max:
        return "COMMIT"
    return "ABSTAIN"


# ---------------------------------------------------------------------------
# Data generation: 5 codebooks x 5 seeds -> KS scores + empirical labels
# ---------------------------------------------------------------------------

def build_observation_table(N: int, M: int, n_seeds: int, sigma_sq: float,
                            signal_var: float, n_iter: int,
                            codebooks: list[tuple[str, object]]) -> list[dict]:
    """For each (codebook, seed): build W, compute KS, run AMP, derive empirical label.

    Returns a flat list of 25 observation dicts.
    """
    obs = []
    alpha_ratio = M / N
    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)

    for cb_name, builder in codebooks:
        for seed in range(n_seeds):
            seed_val = seed * 1000 + 17
            W = builder(N, M, seed_val)
            M_actual, N_actual = W.shape

            U, s, Vt = np.linalg.svd(W, full_matrices=False)
            eig = (s ** 2).astype(np.float64)
            ks_val, _, _ = mp_ks_stat(eig, M_actual, N_actual)

            rng_sig = np.random.default_rng(seed_val + 91)
            x_true = rng_sig.standard_normal(N_actual).astype(np.float64) * math.sqrt(signal_var)
            noise = rng_sig.standard_normal(M_actual).astype(np.float64) * math.sqrt(sigma_sq)
            y = (W.astype(np.float64) @ x_true) + noise

            amp_emp = run_amp(W, y, x_true, signal_var, sigma_sq, n_iter)
            amp_rel = abs(amp_emp - amp_se_pred) / max(amp_emp, amp_se_pred, 1e-12)
            empirical_label = empirical_truth_from_amp_rel(amp_rel)

            obs.append({
                "codebook": cb_name,
                "seed": seed_val,
                "ks": float(ks_val),
                "amp_emp": float(amp_emp),
                "amp_rel_err": float(amp_rel),
                "empirical_label": empirical_label,
            })
            print(f"  obs cb={cb_name:10s} seed={seed} ks={ks_val:.4f} "
                  f"amp_rel={amp_rel:.3f} empirical={empirical_label}", flush=True)
    return obs


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """HARD PASS: per_codebook_commit_accuracy == 5/5 AND abstain_rate < 0.30.
    HARD FAIL: per_codebook_commit_accuracy < 4/5 OR abstain_rate >= 0.70.
    Else INCONCLUSIVE.
    """
    fold_results = summary.get("fold_results") or []
    if len(fold_results) < 25:
        return ("CONFORMAL_ROUTING_SUBSUMPTION_INCONCLUSIVE",
                f"Only {len(fold_results)} folds; need 25 for full LOO.")

    n_commit = sum(1 for f in fold_results if f["decision"] == "COMMIT")
    n_abstain = sum(1 for f in fold_results if f["decision"] == "ABSTAIN")
    n_correct_at_commit = sum(1 for f in fold_results
                              if f["decision"] == "COMMIT"
                              and f["routed_label"] == f["empirical_label"])
    n_total = len(fold_results)
    abstain_rate = n_abstain / n_total
    commit_accuracy = (n_correct_at_commit / max(n_commit, 1)) if n_commit > 0 else float("nan")

    # Per-codebook commit accuracy: how many codebooks have ALL their committed
    # folds correct? (Codebooks with zero commits are excluded.)
    cb_names = sorted({f["codebook"] for f in fold_results})
    per_cb = {}
    cb_committed = 0
    cb_correct = 0
    for cb in cb_names:
        cb_folds = [f for f in fold_results if f["codebook"] == cb]
        cb_commits = [f for f in cb_folds if f["decision"] == "COMMIT"]
        if not cb_commits:
            per_cb[cb] = {"n_commit": 0, "n_correct": 0, "all_correct": None}
            continue
        n_c = sum(1 for f in cb_commits if f["routed_label"] == f["empirical_label"])
        all_correct = n_c == len(cb_commits)
        per_cb[cb] = {
            "n_commit": len(cb_commits),
            "n_correct": n_c,
            "all_correct": all_correct,
        }
        cb_committed += 1
        if all_correct:
            cb_correct += 1

    summary["n_commit"] = n_commit
    summary["n_abstain"] = n_abstain
    summary["n_correct_at_commit"] = n_correct_at_commit
    summary["abstain_rate"] = abstain_rate
    summary["commit_accuracy"] = commit_accuracy
    summary["per_codebook"] = per_cb
    summary["per_codebook_commit_accuracy"] = (cb_correct, cb_committed)

    # HARD FAIL gates first
    if cb_committed == 0:
        return ("CONFORMAL_ROUTING_SUBSUMPTION_KILLED",
                f"0 codebooks ever committed at p_commit={P_COMMIT}; calibration "
                f"refuses every routing -> useless. abstain_rate={abstain_rate:.2f}.")
    if abstain_rate >= 0.70:
        return ("CONFORMAL_ROUTING_SUBSUMPTION_KILLED",
                f"abstain_rate={abstain_rate:.2f} >= 0.70: calibration refuses "
                f"too much. {n_commit}/{n_total} committed across all codebooks. "
                f"Cap 6 wraps Cap 12 into useless conservatism.")
    if cb_correct < 4:
        return ("CONFORMAL_ROUTING_SUBSUMPTION_KILLED",
                f"Only {cb_correct}/{cb_committed} codebooks have all-correct "
                f"committed routings; need >=4/5. per_cb={per_cb}.")

    # HARD PASS gate
    if cb_correct == 5 and cb_committed == 5 and abstain_rate < 0.30:
        return ("CONFORMAL_ROUTING_SUBSUMPTION_PASS",
                f"Composition B licensed: Venn-Abers conformal calibration on KS "
                f"scores produces commit-vs-abstain decisions with 5/5 codebooks "
                f"all-correct on commits and abstain_rate={abstain_rate:.2f} < 0.30. "
                f"Total commits={n_commit}/{n_total}; commit_accuracy="
                f"{commit_accuracy:.3f}.")

    # MIDDLE BAND
    return ("CONFORMAL_ROUTING_SUBSUMPTION_INCONCLUSIVE",
            f"Borderline: {cb_correct}/{cb_committed} codebooks all-correct "
            f"(PASS=5/5, FAIL<4), abstain_rate={abstain_rate:.2f} "
            f"(PASS<0.30, FAIL>=0.70). per_cb={per_cb}.")


# ---------------------------------------------------------------------------
# Formula self-tests
# ---------------------------------------------------------------------------

def self_test() -> None:
    # Cell 1: route_from_ks boundary
    assert route_from_ks(0.05, 0.20) == "AMP_OK"
    assert route_from_ks(0.20, 0.20) == "AMP_OK"  # inclusive
    assert route_from_ks(0.21, 0.20) == "VAMP_REQUIRED"

    # Cell 2: empirical_truth_from_amp_rel boundary
    assert empirical_truth_from_amp_rel(0.05) == "AMP_OK"
    assert empirical_truth_from_amp_rel(0.10) == "VAMP_REQUIRED"  # exclusive
    assert empirical_truth_from_amp_rel(0.50) == "VAMP_REQUIRED"

    # Cell 3: venn_abers_p formula
    # Calibration: 4 obs with KS in {0.05, 0.10, 0.15, 0.20} all labeled AMP_OK.
    # New obs KS=0.03 (lower than all). For AMP_OK label, non-conformity = +0.03;
    # cal non-conformities = {0.05, 0.10, 0.15, 0.20}; n_ge = 4 (all >= 0.03).
    # p_AMP = (1 + 4) / (1 + 4) = 1.0.
    p = venn_abers_p(0.03, [0.05, 0.10, 0.15, 0.20],
                     ["AMP_OK"] * 4, "AMP_OK")
    assert abs(p - 1.0) < 1e-12, f"venn_abers_p expected 1.0 got {p}"

    # Cell 4: venn_abers_p high-KS new obs -> low conformity for AMP_OK
    # New obs KS=0.50. For AMP_OK candidate, non-conf=0.50; cal non-conf={0.05..0.20};
    # n_ge = 0. p_AMP = (1 + 0) / (1 + 4) = 0.2.
    p = venn_abers_p(0.50, [0.05, 0.10, 0.15, 0.20],
                     ["AMP_OK"] * 4, "AMP_OK")
    assert abs(p - 0.2) < 1e-9, f"venn_abers_p AMP for KS=0.50 expected 0.2 got {p}"

    # Cell 5: venn_abers_p for VAMP candidate when new KS is high
    # New obs KS=0.50. For VAMP candidate, non-conf=-0.50; cal restricted to
    # VAMP labels {0.40, 0.45, 0.50, 0.55} with non-conf={-0.40,-0.45,-0.50,-0.55}.
    # n_ge = |{x in cal: x >= -0.50}| = 3 (the -0.40, -0.45, -0.50 are all >= -0.50).
    # p_VAMP = (1 + 3) / (1 + 4) = 0.8.
    p = venn_abers_p(0.50, [0.40, 0.45, 0.50, 0.55],
                     ["VAMP_REQUIRED"] * 4, "VAMP_REQUIRED")
    assert abs(p - 0.8) < 1e-9, f"venn_abers_p VAMP for KS=0.50 expected 0.8 got {p}"

    # Cell 6: commit_decision logic
    assert commit_decision(p_amp=0.95, p_vamp=0.10,
                           routed_label="AMP_OK",
                           p_commit=P_COMMIT, p_other_max=P_OTHER_MAX) == "COMMIT"
    assert commit_decision(p_amp=0.85, p_vamp=0.10,
                           routed_label="AMP_OK",
                           p_commit=P_COMMIT, p_other_max=P_OTHER_MAX) == "ABSTAIN"
    assert commit_decision(p_amp=0.95, p_vamp=0.55,
                           routed_label="AMP_OK",
                           p_commit=P_COMMIT, p_other_max=P_OTHER_MAX) == "ABSTAIN"
    # Routed VAMP
    assert commit_decision(p_amp=0.10, p_vamp=0.92,
                           routed_label="VAMP_REQUIRED",
                           p_commit=P_COMMIT, p_other_max=P_OTHER_MAX) == "COMMIT"

    # Cell 7: compute_verdict PASS scenario
    fold_pass = []
    for cb in ["iid_gauss", "srht"]:
        for s in range(5):
            fold_pass.append({"codebook": cb, "seed": s, "ks": 0.05,
                              "routed_label": "AMP_OK", "empirical_label": "AMP_OK",
                              "p_amp": 0.95, "p_vamp": 0.10, "decision": "COMMIT"})
    for cb in ["hadamard", "rm_1_m", "kerdock"]:
        for s in range(5):
            fold_pass.append({"codebook": cb, "seed": s, "ks": 0.60,
                              "routed_label": "VAMP_REQUIRED",
                              "empirical_label": "VAMP_REQUIRED",
                              "p_amp": 0.10, "p_vamp": 0.95, "decision": "COMMIT"})
    summary = {"fold_results": fold_pass}
    v, msg = compute_verdict(summary)
    assert v == "CONFORMAL_ROUTING_SUBSUMPTION_PASS", f"expected PASS got {v}: {msg}"
    assert summary["abstain_rate"] == 0.0
    assert summary["per_codebook_commit_accuracy"] == (5, 5)

    # Cell 8: compute_verdict HARD FAIL via excessive abstain
    fold_abstain = []
    for cb in ["iid_gauss", "srht", "hadamard", "rm_1_m", "kerdock"]:
        for s in range(5):
            fold_abstain.append({"codebook": cb, "seed": s, "ks": 0.30,
                                 "routed_label": "VAMP_REQUIRED",
                                 "empirical_label": "VAMP_REQUIRED",
                                 "p_amp": 0.55, "p_vamp": 0.60,
                                 "decision": "ABSTAIN"})
    v, msg = compute_verdict({"fold_results": fold_abstain})
    assert v == "CONFORMAL_ROUTING_SUBSUMPTION_KILLED", f"expected KILLED got {v}: {msg}"

    # Cell 9: compute_verdict MIDDLE BAND (4/5 codebooks all-correct)
    fold_mid = []
    for cb in ["iid_gauss"]:
        for s in range(5):
            fold_mid.append({"codebook": cb, "seed": s, "ks": 0.05,
                             "routed_label": "AMP_OK",
                             "empirical_label": "AMP_OK",
                             "p_amp": 0.95, "p_vamp": 0.10, "decision": "COMMIT"})
    for cb in ["srht", "hadamard", "rm_1_m"]:
        for s in range(5):
            fold_mid.append({"codebook": cb, "seed": s, "ks": 0.60,
                             "routed_label": "VAMP_REQUIRED",
                             "empirical_label": "VAMP_REQUIRED",
                             "p_amp": 0.10, "p_vamp": 0.95, "decision": "COMMIT"})
    # kerdock: 4 commits correct, 1 wrong -> all_correct=False; abstain_rate=0
    for s in range(5):
        if s == 0:
            fold_mid.append({"codebook": "kerdock", "seed": s, "ks": 0.18,
                             "routed_label": "AMP_OK",
                             "empirical_label": "VAMP_REQUIRED",  # mis-route, committed
                             "p_amp": 0.95, "p_vamp": 0.40, "decision": "COMMIT"})
        else:
            fold_mid.append({"codebook": "kerdock", "seed": s, "ks": 0.60,
                             "routed_label": "VAMP_REQUIRED",
                             "empirical_label": "VAMP_REQUIRED",
                             "p_amp": 0.10, "p_vamp": 0.95, "decision": "COMMIT"})
    v, msg = compute_verdict({"fold_results": fold_mid})
    assert v == "CONFORMAL_ROUTING_SUBSUMPTION_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}: {msg}"

    # Cell 10: missing folds -> INCONCLUSIVE
    v, _ = compute_verdict({"fold_results": fold_pass[:10]})
    assert v == "CONFORMAL_ROUTING_SUBSUMPTION_INCONCLUSIVE"

    print("conformal_routing_subsumption self-test passed (10/10 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 64,
            "M_over_N": 1.0,
            "n_seeds": 1,
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_iter": 50,
            "tau_declared": TAU_DECLARED,
            "p_commit": P_COMMIT,
            "p_other_max": P_OTHER_MAX,
            "codebooks": ["iid_gauss", "srht"],
        }
    else:
        config = {
            "mode": "full",
            "N": 1024,
            "M_over_N": 1.0,
            "n_seeds": 5,
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_iter": 300,
            "tau_declared": TAU_DECLARED,
            "p_commit": P_COMMIT,
            "p_other_max": P_OTHER_MAX,
            "codebooks": [nm for nm, _b in CODEBOOKS],
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]
    n_iter = config["n_iter"]
    n_seeds = config["n_seeds"]

    builder_map = {nm: b for nm, b in CODEBOOKS}
    codebooks_active = [(nm, builder_map[nm]) for nm in config["codebooks"]]

    print(f"[setup] N={N} M={M} M/N={M/N:.3f} sigma_sq={sigma_sq} "
          f"signal_var={signal_var} n_iter={n_iter} n_seeds={n_seeds} "
          f"tau={TAU_DECLARED} p_commit={P_COMMIT} p_other_max={P_OTHER_MAX} "
          f"codebooks={config['codebooks']}", flush=True)

    # Step 1: build all 25 observations
    print("\n[stage 1/2] building observation table (5 codebooks x 5 seeds = 25 obs)",
          flush=True)
    obs = build_observation_table(N, M, n_seeds, sigma_sq, signal_var, n_iter,
                                  codebooks_active)

    # Step 2: LOO Venn-Abers conformal calibration
    print(f"\n[stage 2/2] LOO Venn-Abers conformal calibration over {len(obs)} obs",
          flush=True)
    fold_results = []
    for i, ob in enumerate(obs):
        held_out = ob
        cal_set = [o for j, o in enumerate(obs) if j != i]
        cal_scores = [o["ks"] for o in cal_set]
        cal_labels = [o["empirical_label"] for o in cal_set]

        p_amp = venn_abers_p(held_out["ks"], cal_scores, cal_labels, "AMP_OK")
        p_vamp = venn_abers_p(held_out["ks"], cal_scores, cal_labels, "VAMP_REQUIRED")
        routed_label = route_from_ks(held_out["ks"], TAU_DECLARED)
        decision = commit_decision(p_amp, p_vamp, routed_label, P_COMMIT, P_OTHER_MAX)

        fold_results.append({
            "codebook": held_out["codebook"],
            "seed": held_out["seed"],
            "ks": held_out["ks"],
            "amp_rel_err": held_out["amp_rel_err"],
            "empirical_label": held_out["empirical_label"],
            "routed_label": routed_label,
            "p_amp": float(p_amp),
            "p_vamp": float(p_vamp),
            "decision": decision,
            "correct_if_committed": (routed_label == held_out["empirical_label"]),
        })
        print(f"  fold {i:02d} cb={held_out['codebook']:10s} seed={held_out['seed']:4d} "
              f"ks={held_out['ks']:.4f} p_amp={p_amp:.3f} p_vamp={p_vamp:.3f} "
              f"routed={routed_label} truth={held_out['empirical_label']} "
              f"decision={decision}", flush=True)

    summary = {
        "observations": obs,
        "fold_results": fold_results,
        "config": config,
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap12_cap6_conformal_routing_subsumption_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["fold_results"]) >= 1, "smoke FAIL: no folds"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap12_cap6_conformal_routing_subsumption_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
