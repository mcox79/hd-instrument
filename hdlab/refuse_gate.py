"""Standalone refuse-gate calibration. Independent of KGStore.

Calibrate a confidence threshold tau on paired in-distribution / out-of-distribution
score arrays; tau maximizes 0.5*(accept_rate + refuse_rate) on the calibration split.

Extracted from KGStore.refuse_gate_calibrate (which exercised this on n8/U1; CERT 584/585)
so any cell that produces confidence scores (KG retrieval, sequence-memory prediction,
multi-hop chain, generation step) can apply the same margin-discipline.
"""

from __future__ import annotations

import torch


def calibrate_refuse_threshold(
    in_dist_scores: torch.Tensor,
    ood_scores: torch.Tensor,
    split: float = 0.5,
) -> dict:
    """Calibrate tau on confidence-score arrays.

    Args:
        in_dist_scores: 1-D tensor of confidence values for in-distribution items
            (e.g. max-score-over-targets on KG queries with known answer in KB).
        ood_scores: 1-D tensor of confidence values for OOD items
            (e.g. max-score-over-targets on KG queries with answer NOT in KB).
        split: fraction used for calibration; remainder is held-out eval. Default 0.5.

    Returns:
        dict with keys:
            tau: chosen threshold
            in_dist_accept: held-out accept rate (in_dist >= tau)
            ood_refuse: held-out refuse rate (ood < tau)
            balanced_acc: held-out 0.5*(accept + refuse)
            cal_balanced_acc: calibration-set 0.5*(accept + refuse)
            in_dist_mean: mean confidence on in-dist held-out
            ood_mean: mean confidence on ood held-out
            n_cal_in: calibration in-dist count
            n_cal_ood: calibration ood count
            n_eval_in: eval in-dist count
            n_eval_ood: eval ood count
    """
    if in_dist_scores.numel() == 0 or ood_scores.numel() == 0:
        raise ValueError("calibrate_refuse_threshold requires both in_dist and ood score tensors")
    if not (0.0 < split < 1.0):
        raise ValueError(f"split must be in (0,1); got {split}")

    h_in = max(1, int(len(in_dist_scores) * split))
    h_ood = max(1, int(len(ood_scores) * split))
    cal_in, ev_in = in_dist_scores[:h_in], in_dist_scores[h_in:]
    cal_ood, ev_ood = ood_scores[:h_ood], ood_scores[h_ood:]

    if ev_in.numel() == 0 or ev_ood.numel() == 0:
        raise ValueError(
            f"insufficient eval data after split={split}: "
            f"n_in={len(in_dist_scores)} n_ood={len(ood_scores)}"
        )

    cands = torch.unique(torch.cat([cal_in, cal_ood]))
    best_tau = float(cands[0])
    best_bal = -1.0
    for tau in cands:
        tau_f = float(tau)
        acc = float((cal_in >= tau_f).float().mean())
        ref = float((cal_ood < tau_f).float().mean())
        bal = 0.5 * (acc + ref)
        if bal > best_bal:
            best_bal = bal
            best_tau = tau_f

    eval_accept = float((ev_in >= best_tau).float().mean())
    eval_refuse = float((ev_ood < best_tau).float().mean())

    return {
        "tau": best_tau,
        "in_dist_accept": eval_accept,
        "ood_refuse": eval_refuse,
        "balanced_acc": 0.5 * (eval_accept + eval_refuse),
        "cal_balanced_acc": best_bal,
        "in_dist_mean": float(ev_in.mean()),
        "ood_mean": float(ev_ood.mean()),
        "n_cal_in": int(h_in),
        "n_cal_ood": int(h_ood),
        "n_eval_in": int(ev_in.numel()),
        "n_eval_ood": int(ev_ood.numel()),
    }


def apply_refuse(score: float, tau: float) -> bool:
    """Return True iff score should be ACCEPTED (score >= tau); False = REFUSE."""
    return score >= tau
