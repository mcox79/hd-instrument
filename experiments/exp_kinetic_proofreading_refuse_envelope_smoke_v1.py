"""Kinetic Proofreading + Refuse-Gate envelope (Gap 4 substrate-product strategy; smoke v1).

USER framing (lock-in-amplifier / Hopfield 1974): biological ribosomes hit ~0.001% error despite
thermal noise that would give ~10% single-shot. Mechanism: two sequential energetic gates in
coherence; mismatched tRNAs fall off between steps; error_eff = error_0^2 at cost of accept_rate.
Substrate analog: argmax twice with INDEPENDENT noise realizations + agreement-gate.

Cell tests four arms over production-regime noise sigmas:
  ARM_SINGLE_SHOT    -- current substrate; pure argmax, no proofreading
  ARM_KP_2STEP       -- sample cue twice (independent noise); accept iff both argmax agree
  ARM_KP_3STEP       -- sample 3x; 2-of-3 majority vote
  ARM_REFUSE_GATED   -- single-shot + max-cosine threshold tau (refuse_gate.calibrate at sigma=0.5)

Per arm, per sigma:
  recall_at_1_accepted   recall on the accepted subset
  accept_rate            fraction of in-dist queries NOT refused
  silent_error_rate      fraction in-dist WRONG-but-accepted (KEY safety metric)
  ood_refuse_rate        fraction of OOD random_bipolar cues correctly refused

Pre-reg HARD-PASS (chain-grade-eligible envelope-OR-refuse META):
  KP_2STEP silent_error_rate @ sigma=1.5 <= 0.05
  AND KP_2STEP recall_accepted @ sigma=0.5 >= 0.80
  AND REFUSE_GATED ood_refuse_rate @ sigma=1.5 >= 0.90

Pre-reg HARD-FAIL (refuse-aware strategy dead; substrate must descope to sigma<=1.0 strict):
  KP_2STEP silent_error_rate @ sigma=1.5 > 0.20
  OR REFUSE_GATED ood_refuse_rate @ sigma=1.5 < 0.50

Sanity self-tests (mandatory before atomize):
  sigma=0.0: all arms accept_rate==1.0 AND recall_accepted==1.0 (clean cue endpoint)
  sigma=10.0: REFUSE_GATED accept_rate <= 0.10 (refuses appropriately under extreme noise)

ASCII-only; numpy-only.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    aggregate_partials,
    get_output_dir,
    write_metrics,
    write_partial_key,
)

ANCHOR_NAME = "kinetic_proofreading_refuse_envelope_smoke_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full" if not _ARGS.self_test else "smoke")

# Config per USER spec
M_FULL = 200
M_SMOKE = 50
N_DIM_FULL = 4096
N_DIM_SMOKE = 1024
N_EVAL_FULL = 200
N_EVAL_SMOKE = 50
N_OOD_FULL = 50
N_OOD_SMOKE = 20
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [7]
SIGMAS = [0.0, 0.5, 1.0, 1.5, 2.0]
SIGMA_EXTREME = 10.0  # sanity self-test endpoint
SIGMA_CAL = 0.5        # refuse_gate tau calibrated on sigma=0.5 paired (in-dist vs OOD)

if RUN_MODE == "smoke":
    M = M_SMOKE; N_DIM = N_DIM_SMOKE; N_EVAL = N_EVAL_SMOKE; N_OOD = N_OOD_SMOKE; SEEDS = SEEDS_SMOKE
else:
    M = M_FULL; N_DIM = N_DIM_FULL; N_EVAL = N_EVAL_FULL; N_OOD = N_OOD_FULL; SEEDS = SEEDS_FULL


def random_bipolar(rows: int, n: int, rng: np.random.Generator) -> np.ndarray:
    return (rng.integers(0, 2, (rows, n)) * 2 - 1).astype(np.float32)


def build_codebook(m: int, n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 9001 + 13)
    return random_bipolar(m, n, rng)


def noisy_cue(atom: np.ndarray, sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Additive gaussian noise on a bipolar cue. sigma=0 -> clean atom."""
    if sigma <= 0.0:
        return atom.copy()
    return atom + (sigma * rng.standard_normal(atom.shape)).astype(np.float32)


def argmax_with_score(cb: np.ndarray, cue: np.ndarray) -> tuple[int, float]:
    """Return (argmax_idx, max_cosine_score). Codebook bipolar so ||row||=sqrt(N); cue norm divides."""
    # cosine via dot/(||cb||*||cue||); cb rows are bipolar so ||cb_i||=sqrt(N)
    cue_n = float(np.linalg.norm(cue))
    if cue_n < 1e-12:
        return 0, 0.0
    scores = (cb @ cue) / (np.sqrt(cb.shape[1]) * cue_n)
    idx = int(np.argmax(scores))
    return idx, float(scores[idx])


def calibrate_refuse_tau_np(in_scores: np.ndarray, ood_scores: np.ndarray, split: float = 0.5) -> float:
    """Numpy port of hdlab/refuse_gate.calibrate_refuse_threshold.

    Maximizes 0.5*(accept_rate_on_in + refuse_rate_on_ood) on a calibration split; returns tau.
    """
    if in_scores.size == 0 or ood_scores.size == 0:
        raise ValueError("calibrate_refuse_tau_np requires non-empty in_scores and ood_scores")
    h_in = max(1, int(in_scores.size * split))
    h_ood = max(1, int(ood_scores.size * split))
    cal_in = in_scores[:h_in]
    cal_ood = ood_scores[:h_ood]
    cands = np.unique(np.concatenate([cal_in, cal_ood]))
    best_tau = float(cands[0])
    best_bal = -1.0
    for tau in cands:
        acc = float((cal_in >= tau).mean())
        ref = float((cal_ood < tau).mean())
        bal = 0.5 * (acc + ref)
        if bal > best_bal:
            best_bal = bal
            best_tau = float(tau)
    return best_tau


def per_arm_metrics(
    cb: np.ndarray,
    sigma: float,
    n_eval: int,
    n_ood: int,
    tau: float,
    rng: np.random.Generator,
) -> dict:
    """Run all four arms at a fixed sigma; return per-arm metric dict."""
    m, n = cb.shape
    # in-dist queries: pick random atom idx; cue = atom + noise(sigma); ground truth = idx
    in_idx = rng.integers(0, m, size=n_eval)
    # ood queries: random_bipolar cues; ground truth = REFUSE (no correct answer in codebook)
    ood_cues = random_bipolar(n_ood, n, rng)

    # Pre-compute single-shot argmax + score for in-dist (used by SINGLE and REFUSE arms)
    single_pred = np.zeros(n_eval, dtype=np.int64)
    single_score = np.zeros(n_eval, dtype=np.float32)
    for i in range(n_eval):
        cue = noisy_cue(cb[in_idx[i]], sigma, rng)
        idx, sc = argmax_with_score(cb, cue)
        single_pred[i] = idx; single_score[i] = sc

    # Second + third independent noise realizations for KP arms
    kp2_pred = np.zeros(n_eval, dtype=np.int64)
    kp3_pred = np.zeros(n_eval, dtype=np.int64)
    for i in range(n_eval):
        cue2 = noisy_cue(cb[in_idx[i]], sigma, rng)
        idx2, _ = argmax_with_score(cb, cue2)
        kp2_pred[i] = idx2
        cue3 = noisy_cue(cb[in_idx[i]], sigma, rng)
        idx3, _ = argmax_with_score(cb, cue3)
        kp3_pred[i] = idx3

    # OOD scores via single-shot argmax max-cosine
    ood_score = np.zeros(n_ood, dtype=np.float32)
    ood_pred = np.zeros(n_ood, dtype=np.int64)
    for j in range(n_ood):
        idx, sc = argmax_with_score(cb, ood_cues[j])
        ood_pred[j] = idx; ood_score[j] = sc

    # ARM_SINGLE_SHOT: accept everything; recall = pred==in_idx; silent_err = wrong-but-accepted = 1-recall
    single_correct = (single_pred == in_idx)
    arm_single = {
        "accept_rate": 1.0,
        "recall_at_1_accepted": float(single_correct.mean()),
        "silent_error_rate": float((~single_correct).mean()),  # all accepted; all wrongs are silent
        "ood_refuse_rate": 0.0,  # never refuses
    }

    # ARM_KP_2STEP: accept iff single_pred == kp2_pred (agreement gate); recall on accepted
    kp2_agree = (single_pred == kp2_pred)
    kp2_accept_count = int(kp2_agree.sum())
    if kp2_accept_count > 0:
        kp2_correct_accepted = (single_pred[kp2_agree] == in_idx[kp2_agree])
        kp2_recall_accepted = float(kp2_correct_accepted.mean())
        kp2_silent_err = float((~kp2_correct_accepted).mean())  # wrong-but-accepted / accepted
    else:
        kp2_recall_accepted = 0.0; kp2_silent_err = 0.0
    # OOD on KP_2STEP: agreement on two independent ood evals
    ood_pred2 = np.zeros(n_ood, dtype=np.int64)
    for j in range(n_ood):
        # second independent eval -- for OOD random_bipolar cues, "agreement" means both single-shots
        # pick the SAME spurious atom. Generate a fresh cue with noise eps to mimic independent
        # realization (OOD baseline: same OOD cue + small noise jitter so single-shots differ).
        cue2 = ood_cues[j] + (0.0 * np.random.default_rng(j * 7 + 1).standard_normal(n)).astype(np.float32)
        idx, _ = argmax_with_score(cb, cue2)
        ood_pred2[j] = idx
    # Honest OOD: ood_cues passed through argmax once + once again is the SAME (deterministic).
    # For KP arms, OOD refuse comes from agreement-rate -- if two independent samples STILL agree
    # on the same spurious atom, KP_2STEP would accept the OOD answer (failure of the gate).
    # Substrate-honest reading: random_bipolar OOD cues are deterministic -> single-shot is deterministic
    # -> two-step always agrees on the same spurious idx. KP arms have ZERO native ability to refuse
    # raw-random OOD; that is the REFUSE_GATED arm's job.
    ood_refuse_kp2 = 0.0
    arm_kp2 = {
        "accept_rate": float(kp2_accept_count / n_eval),
        "recall_at_1_accepted": kp2_recall_accepted,
        "silent_error_rate": kp2_silent_err,
        "ood_refuse_rate": ood_refuse_kp2,
    }

    # ARM_KP_3STEP: majority vote 2-of-3 on {single_pred, kp2_pred, kp3_pred}
    kp3_accept = np.zeros(n_eval, dtype=bool)
    kp3_majority_pred = np.zeros(n_eval, dtype=np.int64)
    for i in range(n_eval):
        votes = [single_pred[i], kp2_pred[i], kp3_pred[i]]
        # 2-of-3 agreement: any pair equal
        from collections import Counter
        c = Counter(votes)
        top_idx, top_count = c.most_common(1)[0]
        if top_count >= 2:
            kp3_accept[i] = True
            kp3_majority_pred[i] = top_idx
    kp3_accept_count = int(kp3_accept.sum())
    if kp3_accept_count > 0:
        kp3_correct_accepted = (kp3_majority_pred[kp3_accept] == in_idx[kp3_accept])
        kp3_recall_accepted = float(kp3_correct_accepted.mean())
        kp3_silent_err = float((~kp3_correct_accepted).mean())
    else:
        kp3_recall_accepted = 0.0; kp3_silent_err = 0.0
    arm_kp3 = {
        "accept_rate": float(kp3_accept_count / n_eval),
        "recall_at_1_accepted": kp3_recall_accepted,
        "silent_error_rate": kp3_silent_err,
        "ood_refuse_rate": 0.0,
    }

    # ARM_REFUSE_GATED: single-shot + tau threshold; accept iff single_score >= tau
    refuse_accept = (single_score >= tau)
    refuse_accept_count = int(refuse_accept.sum())
    if refuse_accept_count > 0:
        refuse_correct_accepted = (single_pred[refuse_accept] == in_idx[refuse_accept])
        refuse_recall_accepted = float(refuse_correct_accepted.mean())
        refuse_silent_err = float((~refuse_correct_accepted).mean())
    else:
        refuse_recall_accepted = 0.0; refuse_silent_err = 0.0
    ood_refuse_refuse = float((ood_score < tau).mean())
    arm_refuse = {
        "accept_rate": float(refuse_accept_count / n_eval),
        "recall_at_1_accepted": refuse_recall_accepted,
        "silent_error_rate": refuse_silent_err,
        "ood_refuse_rate": ood_refuse_refuse,
    }

    return {
        "sigma": float(sigma),
        "tau": float(tau),
        "ARM_SINGLE_SHOT": arm_single,
        "ARM_KP_2STEP": arm_kp2,
        "ARM_KP_3STEP": arm_kp3,
        "ARM_REFUSE_GATED": arm_refuse,
    }


def run_seed(seed: int) -> dict:
    """Run all sigmas + sanity-extreme for one seed. Calibrates tau at sigma=SIGMA_CAL."""
    rng = np.random.default_rng(seed)
    cb = build_codebook(M, N_DIM, seed)

    # Calibrate tau on sigma=0.5 in-dist + OOD scores (paired distribution)
    n_cal = max(64, N_EVAL)
    in_cal_idx = rng.integers(0, M, size=n_cal)
    in_cal_scores = np.zeros(n_cal, dtype=np.float32)
    for i in range(n_cal):
        cue = noisy_cue(cb[in_cal_idx[i]], SIGMA_CAL, rng)
        _, sc = argmax_with_score(cb, cue)
        in_cal_scores[i] = sc
    ood_cal_cues = random_bipolar(n_cal, N_DIM, rng)
    ood_cal_scores = np.zeros(n_cal, dtype=np.float32)
    for j in range(n_cal):
        _, sc = argmax_with_score(cb, ood_cal_cues[j])
        ood_cal_scores[j] = sc
    tau = calibrate_refuse_tau_np(in_cal_scores, ood_cal_scores)

    # Production sigmas
    by_sigma = {}
    for sigma in SIGMAS:
        by_sigma[("s%.2f" % sigma).replace(".", "p")] = per_arm_metrics(cb, sigma, N_EVAL, N_OOD, tau, rng)

    # Sanity-extreme sigma=10 for REFUSE_GATED accept_rate check
    extreme = per_arm_metrics(cb, SIGMA_EXTREME, N_EVAL, N_OOD, tau, rng)
    by_sigma["s10p00"] = extreme

    return {
        "seed": seed,
        "M": M,
        "N_DIM": N_DIM,
        "N_EVAL": N_EVAL,
        "N_OOD": N_OOD,
        "sigmas": SIGMAS + [SIGMA_EXTREME],
        "tau_calibrated_at_sigma": SIGMA_CAL,
        "tau": float(tau),
        "by_sigma": by_sigma,
        "run_mode": RUN_MODE,
    }


def _r(x):
    return None if x is None else round(float(x), 4)


def compute_verdict(per_seed_list: list) -> tuple[str, str, dict]:
    """Score the cell per pre-registered HARD-PASS / HARD-FAIL bands."""
    if not per_seed_list:
        return ("HARD_FAIL", "no seed results", {})

    def avg(key_path, sigma_key, arm):
        vals = []
        for s in per_seed_list:
            v = s["by_sigma"].get(sigma_key, {}).get(arm, {}).get(key_path)
            if v is not None:
                vals.append(v)
        return float(np.mean(vals)) if vals else None

    # Pre-reg metrics
    kp2_silent_err_15 = avg("silent_error_rate", "s1p50", "ARM_KP_2STEP")
    kp2_recall_acc_05 = avg("recall_at_1_accepted", "s0p50", "ARM_KP_2STEP")
    refuse_ood_15 = avg("ood_refuse_rate", "s1p50", "ARM_REFUSE_GATED")

    # Sanity
    sigma0_accepts = {
        arm: avg("accept_rate", "s0p00", arm)
        for arm in ["ARM_SINGLE_SHOT", "ARM_KP_2STEP", "ARM_KP_3STEP", "ARM_REFUSE_GATED"]
    }
    sigma0_recalls = {
        arm: avg("recall_at_1_accepted", "s0p00", arm)
        for arm in ["ARM_SINGLE_SHOT", "ARM_KP_2STEP", "ARM_KP_3STEP", "ARM_REFUSE_GATED"]
    }
    refuse_accept_extreme = avg("accept_rate", "s10p00", "ARM_REFUSE_GATED")

    detail = {
        "kp2_silent_err_at_1p5": _r(kp2_silent_err_15),
        "kp2_recall_accepted_at_0p5": _r(kp2_recall_acc_05),
        "refuse_ood_refuse_at_1p5": _r(refuse_ood_15),
        "sigma0_accept_rates_per_arm": {k: _r(v) for k, v in sigma0_accepts.items()},
        "sigma0_recall_accepted_per_arm": {k: _r(v) for k, v in sigma0_recalls.items()},
        "refuse_accept_rate_at_extreme_sigma_10": _r(refuse_accept_extreme),
        "n_seeds": len(per_seed_list),
        "per_seed_summaries": [
            {
                "seed": s["seed"],
                "tau": _r(s["tau"]),
                "kp2_silent_err_1p5": _r(s["by_sigma"].get("s1p50", {}).get("ARM_KP_2STEP", {}).get("silent_error_rate")),
                "kp2_recall_acc_0p5": _r(s["by_sigma"].get("s0p50", {}).get("ARM_KP_2STEP", {}).get("recall_at_1_accepted")),
                "refuse_ood_1p5": _r(s["by_sigma"].get("s1p50", {}).get("ARM_REFUSE_GATED", {}).get("ood_refuse_rate")),
            }
            for s in per_seed_list
        ],
    }

    # Sanity self-test: at sigma=0 all arms should accept=1 and recall=1
    sanity_clean_ok = all(
        (a is not None and a >= 0.99) for a in sigma0_accepts.values()
    ) and all(
        (r is not None and r >= 0.99) for r in sigma0_recalls.values()
    )
    # Sanity extreme: REFUSE_GATED accept_rate at sigma=10 must be <= 0.10
    sanity_extreme_ok = (refuse_accept_extreme is not None and refuse_accept_extreme <= 0.10)
    detail["sanity_clean_endpoint_ok"] = bool(sanity_clean_ok)
    detail["sanity_extreme_endpoint_ok"] = bool(sanity_extreme_ok)

    if not sanity_clean_ok:
        return ("HARD_FAIL", "sanity self-test FAIL: at sigma=0 not all arms accept_rate==1 or recall==1 "
                "(implementation bug; do not interpret main bands)", detail)
    if not sanity_extreme_ok:
        return ("HARD_FAIL", "sanity self-test FAIL: at sigma=10 REFUSE_GATED accept_rate > 0.10 "
                "(tau mis-calibrated)", detail)

    # Pre-reg HARD-FAIL trip-wires
    hf_silent = (kp2_silent_err_15 is not None and kp2_silent_err_15 > 0.20)
    hf_ood = (refuse_ood_15 is not None and refuse_ood_15 < 0.50)
    if hf_silent or hf_ood:
        return ("HARD_FAIL", "HARD_FAIL pre-reg: refuse-aware strategy refuted "
                "(kp2_silent_err@1.5=%s > 0.20: %s ; refuse_ood@1.5=%s < 0.50: %s). "
                "Substrate must descope to sigma<=1.0 strict envelope."
                % (_r(kp2_silent_err_15), hf_silent, _r(refuse_ood_15), hf_ood), detail)

    # Pre-reg HARD-PASS gates
    hp_silent = (kp2_silent_err_15 is not None and kp2_silent_err_15 <= 0.05)
    hp_recall = (kp2_recall_acc_05 is not None and kp2_recall_acc_05 >= 0.80)
    hp_ood = (refuse_ood_15 is not None and refuse_ood_15 >= 0.90)
    if hp_silent and hp_recall and hp_ood:
        return ("HARD_PASS", "HARD_PASS pre-reg: envelope-OR-refuse META chain-grade-eligible. "
                "KP_2STEP silent_err@1.5=%s <= 0.05 ; recall_accepted@0.5=%s >= 0.80 ; "
                "REFUSE_GATED ood_refuse@1.5=%s >= 0.90 ; sanity endpoints PASS."
                % (_r(kp2_silent_err_15), _r(kp2_recall_acc_05), _r(refuse_ood_15)), detail)

    # MIDDLE_BAND: partial (1 or 2 of 3 pre-reg gates fire; HF not tripped)
    n_hp = int(hp_silent) + int(hp_recall) + int(hp_ood)
    return ("MIDDLE_BAND", "MIDDLE_BAND: %d of 3 HARD-PASS gates fire (kp2_silent_err@1.5=%s, "
            "kp2_recall_acc@0.5=%s, refuse_ood@1.5=%s); tune-then-revisit (per-sigma stratified tau "
            "OR widen KP step count)." % (n_hp, _r(kp2_silent_err_15), _r(kp2_recall_acc_05), _r(refuse_ood_15)),
            detail)


def _selftest():
    """Smoke self-test: build small codebook, verify clean-cue endpoint + tau calibration produces valid threshold."""
    rng = np.random.default_rng(123)
    cb = build_codebook(20, 256, 1)
    # clean cue must hit argmax = stored idx
    idx0, sc0 = argmax_with_score(cb, cb[5])
    assert idx0 == 5, "clean argmax must recover stored idx"
    assert sc0 > 0.99, "clean cue cosine must be ~1.0; got %.3f" % sc0

    # Noisy at sigma=0.5 should still mostly recover (substrate envelope)
    correct = 0
    n = 30
    for _ in range(n):
        i = int(rng.integers(0, 20))
        cue = noisy_cue(cb[i], 0.5, rng)
        idx, _ = argmax_with_score(cb, cue)
        correct += int(idx == i)
    rate = correct / n
    assert rate >= 0.5, "sigma=0.5 recall should be >0.5 on small codebook; got %.2f" % rate

    # Tau calibration must produce a finite threshold
    in_s = np.array([0.9, 0.85, 0.8, 0.95, 0.88, 0.92], dtype=np.float32)
    ood_s = np.array([0.1, 0.12, 0.08, 0.15, 0.11, 0.09], dtype=np.float32)
    tau = calibrate_refuse_tau_np(in_s, ood_s)
    assert 0.15 < tau < 0.95, "tau in plausible range; got %.3f" % tau
    print("[selftest] PASS: clean argmax=stored; sigma=0.5 recall=%.2f; tau=%.3f" % (rate, tau), flush=True)


_selftest()
if _ARGS.self_test:
    raise SystemExit(0)


# ---------------- main run ----------------
print(
    "[config] %s mode=%s M=%d N_DIM=%d N_EVAL=%d N_OOD=%d sigmas=%s seeds=%s"
    % (ANCHOR_NAME, RUN_MODE, M, N_DIM, N_EVAL, N_OOD, SIGMAS + [SIGMA_EXTREME], SEEDS),
    flush=True,
)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM, "M": M}
t0 = time.time()

for seed in SEEDS:
    key = "seed_%d" % seed
    existing = aggregate_partials(out_dir, [key], run_config=run_config)
    if key in existing:
        print("[ckpt] %s done; skip" % key, flush=True)
        continue
    result = run_seed(seed)
    write_partial_key(out_dir, key, result)
    print(
        "[seed %d] tau=%.4f kp2_silent_err@1.5=%.3f refuse_ood@1.5=%.3f"
        % (
            seed,
            result["tau"],
            result["by_sigma"]["s1p50"]["ARM_KP_2STEP"]["silent_error_rate"],
            result["by_sigma"]["s1p50"]["ARM_REFUSE_GATED"]["ood_refuse_rate"],
        ),
        flush=True,
    )

keys = ["seed_%d" % s for s in SEEDS]
per_seed = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(per_seed)
print("\n[VERDICT] " + msg, flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": msg,
    "run_mode": RUN_MODE,
    "M": M,
    "N_DIM": N_DIM,
    "N_EVAL": N_EVAL,
    "N_OOD": N_OOD,
    "sigmas": SIGMAS + [SIGMA_EXTREME],
    "seeds": SEEDS,
    "detail": detail,
    "metrics_source": "measured_cpu_kinetic_proofreading_refuse_envelope_smoke_v1",
    "per_seed": per_seed,
    "elapsed_s": time.time() - t0,
}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
