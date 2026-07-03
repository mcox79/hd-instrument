"""Verification: M1.7 RoleSlotSummarizer reproduces role_binding closure CG."""

from __future__ import annotations

import pytest
import torch

from hdlab.role_slot_summarizer import (
    BUNDLED_COLLAPSE_ALPHA_WALL,
    L2_ROLES_DEFAULT,
    S_ROLES_DEFAULT,
    RoleSlotSummarizer,
    _bipolar_random,
    _run_all_selftests,
)


def test_run_all_selftests_pass() -> None:
    """All module selftests reproduce M1.7 v1 seed_7/13/19 CG (2026-07-01)."""
    result = _run_all_selftests()
    assert result["s_roles_default"] == 4
    assert result["l2_roles_default"] == 5
    assert result["bundled_collapse_wall"] == 0.138
    assert result["smoke_role_lift_at_1600"] == 0.500


def test_role_default_slot_count() -> None:
    """S=4 roles (SUBJECT/OBJECT/TEMPORAL/SCHEMA) per M1.7 CG envelope."""
    assert S_ROLES_DEFAULT == 4
    assert L2_ROLES_DEFAULT == 5


def test_bundled_collapse_wall_at_amit_gutfreund() -> None:
    """BUNDLED collapse wall aligns with 0.138 (Amit-Gutfreund; math4_v2 physics law)."""
    assert BUNDLED_COLLAPSE_ALPHA_WALL == 0.138


def test_reject_n_dim_below_cg_threshold() -> None:
    """Constructor refuses n_dim below CG-anchored THRESHOLD (8192)."""
    with pytest.raises(ValueError):
        RoleSlotSummarizer(n_dim=4096)


def test_sharded_role_lift_at_k1600_reproduces_smoke() -> None:
    """Reproduce M1.7 v1 seed_7 smoke: ROLE arm recovers at K=1600 where FLAT collapses.

    MEASURED@data/exp_cortex_summarization_role_slot_v1_seed_7_smoke/metrics.json:
      FLAT@1600 top1 = 0.000  (BUNDLED collapse: alpha=1600/8192=0.195 > 0.138)
      ROLE@1600 top1 = 0.500  (SHARDED per-slot alpha=400/8192=0.049 safe)
    """
    summ = RoleSlotSummarizer(n_dim=8192, seed=7)
    gen = torch.Generator().manual_seed(1601)
    K = 1600
    item_keys = _bipolar_random((K, summ.n_dim), gen)
    role_assign = torch.arange(K) % summ.n_roles
    role_assign = role_assign[torch.randperm(K, generator=gen)]
    val_indices = torch.randint(0, summ.v_cb, (K,), generator=gen)
    target = int(torch.randint(0, K, (1,), generator=gen).item())
    true_val = int(val_indices[target])
    slot_bundles_q = summ.summarize_role(item_keys, role_assign, val_indices)
    target_role_key = summ._role_keys[int(role_assign[target])]
    role_pred = summ.read_role(target_role_key, item_keys[target], slot_bundles_q)
    assert role_pred == true_val


def test_summarize_role_output_shape() -> None:
    """summarize_role returns (S, n_dim) sharded slot buffers."""
    summ = RoleSlotSummarizer(n_dim=8192, seed=13)
    gen = torch.Generator().manual_seed(19)
    K = 32
    item_keys = _bipolar_random((K, summ.n_dim), gen)
    role_assign = torch.arange(K) % summ.n_roles
    val_indices = torch.randint(0, summ.v_cb, (K,), generator=gen)
    out = summ.summarize_role(item_keys, role_assign, val_indices)
    assert out.shape == (summ.n_roles, summ.n_dim)


def test_summarize_recursive_output_shape() -> None:
    """summarize_recursive returns (L2, S, n_dim) nested-sharded buffers."""
    summ = RoleSlotSummarizer(n_dim=8192, seed=19)
    gen = torch.Generator().manual_seed(101)
    K = 40
    item_keys = _bipolar_random((K, summ.n_dim), gen)
    role_assign = torch.arange(K) % summ.n_roles
    val_indices = torch.randint(0, summ.v_cb, (K,), generator=gen)
    out = summ.summarize_recursive(item_keys, role_assign, val_indices, chunk_size=10)
    assert out.shape == (summ.l2_roles, summ.n_roles, summ.n_dim)
