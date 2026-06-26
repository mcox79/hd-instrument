"""Standalone refuse-gate calibration. Independent of KGStore.

Calibrate a confidence threshold tau on paired in-distribution / out-of-distribution
score arrays; tau maximizes 0.5*(accept_rate + refuse_rate) on the calibration split.

Extracted from KGStore.refuse_gate_calibrate (which exercised this on n8/U1; CERT 584/585)
so any cell that produces confidence scores (KG retrieval, sequence-memory prediction,
multi-hop chain, generation step) can apply the same margin-discipline.

V_REL envelope (the audit library size of relations the gate can discriminate over)
is chain-grade-confirmed at V_REL=256 (32x extension over the v2 chain-grade baseline
at V_REL=8). At V_REL=256 with N_DIM=8192 and 600 in/out concept atoms, the
relation_check arm holds 1.0 cv=0.0 refuse on NEAR_DOMAIN_MIXED queries across 3 seeds;
the naive_plus_intent arm degrades monotonically 0.99 -> 0.18 across V_REL=8..512,
providing genuine discriminator headroom (NOT by-construction-saturated). Validated by
exp_substrate_refuse_gate_v_rel_extension_v1 cell-land 2026-06-26 (commit 6e2ff698;
HARD_PASS chain-grade per Skunkworks landed-VET; ledger row 6479edf0b1db245a).

Above V_REL=256: the relation_check arm REMAINS at 1.0 refuse through V_REL=512 in the
v1 cell; envelope extension to V_REL>=512 is plausible but not yet chain-grade-ratified
(would need a separate cell with appropriately scaled negative-control fan-out).

Composes-with: KV learned projection (M=1M chain-grade) for refuse-gated KG retrieval
product positioning.
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


# Chain-grade-confirmed envelope; see module docstring for cell-land provenance.
V_REL_CHAIN_GRADE_ENVELOPE = 256
V_REL_PRIOR_BASELINE_v2 = 8


def assert_v_rel_within_chain_grade_envelope(v_rel: int) -> None:
    """Raise ValueError if v_rel exceeds the chain-grade-confirmed envelope.

    Callers building refuse-gated retrievers over a relation library should call
    this before claiming the gate's NEAR_DOMAIN_MIXED refusal property holds for
    their config. v_rel <= 256 is chain-grade-ratified; v_rel > 256 is plausible
    but un-ratified per the exp_substrate_refuse_gate_v_rel_extension_v1 cell.
    """
    if v_rel > V_REL_CHAIN_GRADE_ENVELOPE:
        raise ValueError(
            f"v_rel={v_rel} exceeds chain-grade envelope V_REL_CHAIN_GRADE_ENVELOPE="
            f"{V_REL_CHAIN_GRADE_ENVELOPE} (32x extension over v2 baseline V_REL={V_REL_PRIOR_BASELINE_v2}); "
            f"refuse-gate NEAR_DOMAIN_MIXED refuse property NOT chain-grade-ratified at this size. "
            f"Either reduce v_rel or dispatch a new chain-grade-extension cell for your regime."
        )
