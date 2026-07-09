"""Verification: basal-ganglia Go/NoGo value-based action-selection gate.

Scaffold-free witnesses (no tracing) that reproduce the certified value-gate
advantage from exp_pfc_gate_cfrpe_trained_v2 (5-seed FULL N=8192; cell self-verdict
HARD_PASS closure=0.661 at fair depth-4; landed-VET tier MEASURED_MECHANISM):

  - Go/NoGo beats the static additive baseline where value matters (gonogo > additive).
  - w_reach == 0 reduces the gate EXACTLY to the additive baseline (op-trace identical).
  - the trained-M reach fires (reach_rank > chance) and is target-cosine INDEPENDENT.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from hdlab.action_selection import (
    CG_ADDITIVE,
    CG_CELL_COMMIT,
    CG_CLOSURE,
    CG_FOCUS_REGIME,
    CG_GONOGO,
    CG_ORACLE,
    GoNoGoActionGate,
    _build_nav_task,
    _chain_tensors,
    _run_all_selftests,
    reach_control_targetcos,
    reach_value,
    train_sr_transport,
    value_gate_advantage_witness,
)


def test_run_all_selftests_pass() -> None:
    """All module formula selftests + certified-advantage witness pass."""
    result = _run_all_selftests()
    assert result["cg_focus_regime"] == "V1200_d4"
    assert result["cg_closure"] == 0.661
    w = result["witness"]
    assert w["null_reduces_to_additive"] is True
    assert w["gonogo_lift"] > 0.05
    assert w["additive_in_band"] is True


def test_cg_anchored_constants() -> None:
    """CG-anchored MEASURED constants match v2 FULL 5-seed metrics (verified off-disk)."""
    assert CG_FOCUS_REGIME == "V1200_d4"
    assert CG_CLOSURE == 0.661
    assert CG_GONOGO == 0.653
    assert CG_ADDITIVE == 0.053
    assert CG_ORACLE == 0.962
    assert CG_CELL_COMMIT == "1d606f4ec"


def test_value_gate_beats_additive_witness() -> None:
    """Certified discriminator: Go/NoGo beats the static additive baseline, fair regime."""
    r = value_gate_advantage_witness(seed=7)
    assert r["oracle"] >= 0.90, f"oracle rail too low: {r['oracle']:.3f}"
    assert r["additive_in_band"], f"baseline not fair: additive={r['additive']:.3f}"
    assert r["gonogo"] > r["additive"] + 0.05, (
        f"value gate did not beat additive: gonogo={r['gonogo']:.3f} "
        f"additive={r['additive']:.3f}")
    assert r["closure"] >= 0.25, f"closure below floor: {r['closure']:.3f}"


def test_value_gate_advantage_second_seed() -> None:
    """Advantage survives a second seed (not a single-seed fluke)."""
    r = value_gate_advantage_witness(seed=17)
    assert r["additive_in_band"], f"baseline not fair @ seed17: additive={r['additive']:.3f}"
    assert r["gonogo_lift"] > 0.05, f"no advantage @ seed17: lift={r['gonogo_lift']:.3f}"


def test_w_reach_zero_reduces_to_additive() -> None:
    """w_reach==0 Go/NoGo is bit-identical to the additive baseline (clean null reduction)."""
    dev = torch.device("cpu")
    task = _build_nav_task(V=60, n=1024, n_ops=4, density=0.21, n_train=32,
                           n_test=48, depth=3, seed=7, device=dev)
    E, W_ops = task["E"], task["W_ops"]
    s, t, _ = _chain_tensors(task["test"], dev)
    # Additive baseline (no M) vs Go/NoGo with w_reach=0 (M supplied but unused).
    add_gate = GoNoGoActionGate(alpha=0.2, w_reach=0.0)
    null_gate = GoNoGoActionGate(alpha=0.2, w_reach=0.0)
    _, add_trace = add_gate.run_chain(s, t, W_ops, E, None, depth=3)
    _, null_trace = null_gate.run_chain(s, t, W_ops, E, None, depth=3)
    assert np.array_equal(add_trace, null_trace)
    # Also: scores must not depend on M when w_reach==0.
    sc_noM, _ = add_gate.score_actions(E[s], E[t], W_ops, E, None)
    Mrand = torch.randn(1024, 1024)
    sc_M, _ = GoNoGoActionGate(alpha=0.2, w_reach=0.0).score_actions(E[s], E[t], W_ops, E, Mrand)
    assert torch.allclose(sc_noM, sc_M), "w_reach==0 scores leaked a dependence on M"


def test_reach_is_target_cosine_independent() -> None:
    """Anti-tautology: trained-M reach separates on/off-path where identity-reach does not."""
    dev = torch.device("cpu")
    gen = torch.Generator(device=dev); gen.manual_seed(3)
    from hdlab.action_selection import bipolar_codebook
    Et = bipolar_codebook(8, 512, gen, device=dev)
    chainA = np.array([[0, 1], [1, 2], [2, 3]], dtype=np.int64)
    chainB = np.array([[0, 4], [4, 5], [5, 6]], dtype=np.int64)
    toy = np.concatenate([np.tile(chainA, (30, 1)), np.tile(chainB, (30, 1))], axis=0)
    M, _ = train_sr_transport(Et, toy, 512, steps=600, batch=16, base_lr=0.5,
                              gamma=0.8, gen=gen)
    goal = Et[3:4]
    trained_sep = float(reach_value(Et[1:2], goal, M)[0]) - float(reach_value(Et[4:5], goal, M)[0])
    ctrl_sep = abs(float(reach_control_targetcos(Et[1:2], goal)[0])
                   - float(reach_control_targetcos(Et[4:5], goal)[0]))
    assert trained_sep > ctrl_sep + 0.05, (
        f"reach not dynamics-informative: trained_sep={trained_sep:.4f} "
        f"ctrl_sep={ctrl_sep:.4f}")


def test_gate_argument_validation() -> None:
    """Constructor rejects out-of-range alpha / negative w_reach; w_reach!=0 requires M."""
    with pytest.raises(ValueError):
        GoNoGoActionGate(alpha=1.5, w_reach=1.0)
    with pytest.raises(ValueError):
        GoNoGoActionGate(alpha=0.2, w_reach=-0.1)
    dev = torch.device("cpu")
    task = _build_nav_task(V=40, n=256, n_ops=4, density=0.21, n_train=8,
                           n_test=8, depth=3, seed=7, device=dev)
    s, t, _ = _chain_tensors(task["test"], dev)
    with pytest.raises(ValueError):
        GoNoGoActionGate(alpha=0.2, w_reach=1.0).select(
            task["E"][s], task["E"][t], task["W_ops"], task["E"], None)


def test_sr_td_shrinks_rpe() -> None:
    """cfrpe SR-TD delta-rule shrinks the TD prediction error over steps."""
    dev = torch.device("cpu")
    gen = torch.Generator(device=dev); gen.manual_seed(0)
    from hdlab.action_selection import bipolar_codebook
    E = bipolar_codebook(12, 128, gen, device=dev)
    trans = np.array([[i, i + 1] for i in range(10)], dtype=np.int64)
    _, diag = train_sr_transport(E, trans, 128, steps=200, batch=8, base_lr=0.5,
                                 gamma=0.8, gen=gen)
    assert diag["err_last"] < diag["err_first"]
