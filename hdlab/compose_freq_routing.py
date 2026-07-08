"""Compose-frequency routing: gate stored associative traces by target composition-frequency.

Promotes the Stage-2 chain-grade primitive substrate_compose_freq_routing v5 DEFINITIVE
(5-seed cross-N HARD_PASS_CHAIN_GRADE_DEFINITIVE 2026-06-25; math CG atom
EXP_substrate_compose_freq_routing_v5_DEFINITIVE; family partition_routing) into hdlab.

Mechanism (certified, unchanged from the cell): a next-item associator stores sequential
(context -> target) traces. Instead of one shared transition operator, the targets are split
by their composition-frequency rank -- high-frequency (rank < threshold) vs rare -- and TWO
kernels are trained by a masked delta rule (cf-RPE):

    W_freq  <- W_freq + lr_high * mean_over_high_targets[(tgt - ctx@W_freq^T) outer ctx]
    W_rare  <- W_rare + lr_rare * mean_over_rare_targets[(tgt - ctx@W_rare^T) outer ctx
                                    + stdp_w * (tgt outer ctx - ctx outer tgt)]

At readout the logits are ROUTED per candidate by its frequency class:

    logits = high_mask * (norm(ctx@W_freq^T) @ E^T) + (1 - high_mask) * (norm(ctx@W_rare^T) @ E^T)

Why it wins: when high-frequency targets have high in-degree (function-word-like: successors of
many contexts) they dominate a single shared kernel's gradient, and delta cross-talk of magnitude
lr*<ctx_h, ctx_r> corrupts rare-target predictions (see verification.theory
compose_freq_single_kernel_crosstalk). Routing gives rare targets a dedicated kernel that never
sees a high-frequency update, lifting rare-target recall at a small high-frequency cost for a net
next-item gain. The advantage requires context correlation and frequency-in-degree asymmetry; with
orthonormal contexts or no in-degree asymmetry a single delta kernel suffices (the discriminator is
telemetry-sensitive, not by-construction).

Convention: torch at boundaries (matches the certified torch.cuda cell and the CLAUDE.md core
convention). float32 internally; accepts a passed-in torch.Generator for reproducible mini-batch
sampling. ASCII-only; no substrate tracing state (scaffold-free -- the kernels are pure linear
associators).

Storage strategy: SHARDED-COMPATIBLE two-kernel associative store; each kernel is a dense linear
operator over the shared code space. No bundled compositional collapse (the routed readout keeps
the two operators separate). Any downstream L-composition inherits the readout's storage verbatim.
"""
from __future__ import annotations

from typing import Optional, Tuple

import torch


def _l2_normalize(x: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    """Row-wise (or vector) L2 normalization; shape-preserving."""
    if x.dim() == 1:
        return x / (x.norm() + eps)
    return x / (x.norm(dim=1, keepdim=True) + eps)


def composition_frequency_ranks(indices: torch.Tensor, n_items: int) -> torch.Tensor:
    """Frequency ranks of items in a 1-D index sequence; rank 0 = most frequent. Returns (n_items,) long."""
    if indices.dim() != 1:
        raise ValueError(f"composition_frequency_ranks: indices must be 1-D; got {tuple(indices.shape)}")
    if n_items < 1:
        raise ValueError(f"composition_frequency_ranks: n_items must be >= 1; got {n_items}")
    counts = torch.zeros(n_items, dtype=torch.long, device=indices.device)
    counts.scatter_add_(0, indices.long(), torch.ones_like(indices, dtype=torch.long))
    order = torch.argsort(counts, descending=True)
    ranks = torch.empty(n_items, dtype=torch.long, device=indices.device)
    ranks[order] = torch.arange(n_items, device=indices.device)
    return ranks


def high_frequency_mask(ranks: torch.Tensor, threshold: int) -> torch.Tensor:
    """Boolean mask (ranks < threshold): True where the item is high-frequency; shape matches ranks."""
    if threshold < 0:
        raise ValueError(f"high_frequency_mask: threshold must be >= 0; got {threshold}")
    return ranks < int(threshold)


def build_hebbian_kernel(
    E: torch.Tensor,
    ctx_idx: torch.Tensor,
    tgt_idx: torch.Tensor,
) -> torch.Tensor:
    """Raw outer-product Hebbian transition operator sum_i E[tgt_i] outer E[ctx_i]; returns (n_dim, n_dim).

    This is the compose-frequency-ignoring, non-iterative control (the certified cell's baseline arm).
    """
    _check_pairs(E, ctx_idx, tgt_idx)
    return E[tgt_idx].T @ E[ctx_idx]


def build_single_kernel(
    E: torch.Tensor,
    ctx_idx: torch.Tensor,
    tgt_idx: torch.Tensor,
    n_steps: int,
    batch: int,
    lr: float,
    generator: Optional[torch.Generator] = None,
) -> torch.Tensor:
    """Single shared cf-RPE (delta-rule) transition operator over all pairs; returns (n_dim, n_dim).

    Compose-frequency-IGNORING control: same iterative delta training as the routed kernels but with
    one kernel for every target regardless of frequency class.
    """
    _check_pairs(E, ctx_idx, tgt_idx)
    n_dim = E.shape[1]
    n_pairs = ctx_idx.shape[0]
    W = torch.zeros((n_dim, n_dim), dtype=E.dtype, device=E.device)
    if n_pairs == 0 or n_steps < 1:
        return W
    for _ in range(int(n_steps)):
        st = torch.randint(0, n_pairs, (int(batch),), generator=generator, device=E.device)
        ctx = E[ctx_idx[st]]
        tgt = E[tgt_idx[st]]
        error = tgt - ctx @ W.T
        W = W + float(lr) * (error.T @ ctx) / float(batch)
    return W


def build_freq_routed_kernels(
    E: torch.Tensor,
    ctx_idx: torch.Tensor,
    tgt_idx: torch.Tensor,
    high_mask: torch.Tensor,
    n_steps: int,
    batch: int,
    lr_high: float,
    lr_rare: float,
    stdp_w: float,
    generator: Optional[torch.Generator] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Two frequency-gated cf-RPE kernels (W_freq, W_rare); each (n_dim, n_dim).

    high_mask is a per-item boolean tensor (True=high-frequency). W_freq is delta-trained only on
    pairs whose target is high-frequency; W_rare is delta-trained on rare-target pairs plus an
    antisymmetric STDP term (weight stdp_w) at learning rate lr_rare.
    """
    _check_pairs(E, ctx_idx, tgt_idx)
    if high_mask.dim() != 1:
        raise ValueError(f"build_freq_routed_kernels: high_mask must be 1-D; got {tuple(high_mask.shape)}")
    n_dim = E.shape[1]
    n_pairs = ctx_idx.shape[0]
    W_freq = torch.zeros((n_dim, n_dim), dtype=E.dtype, device=E.device)
    W_rare = torch.zeros((n_dim, n_dim), dtype=E.dtype, device=E.device)
    if n_pairs == 0 or n_steps < 1:
        return W_freq, W_rare
    is_high = high_mask.to(dtype=E.dtype)
    for _ in range(int(n_steps)):
        st = torch.randint(0, n_pairs, (int(batch),), generator=generator, device=E.device)
        ctx = E[ctx_idx[st]]
        tgt = E[tgt_idx[st]]
        is_high_b = is_high[tgt_idx[st]]
        wh = is_high_b.unsqueeze(1)
        error_freq = tgt - ctx @ W_freq.T
        W_freq = W_freq + float(lr_high) * ((error_freq * wh).T @ ctx) / float(batch)
        wr = (1.0 - is_high_b).unsqueeze(1)
        error_rare = tgt - ctx @ W_rare.T
        dW_cf = ((error_rare * wr).T @ ctx) / float(batch)
        dW_stdp = ((tgt * wr).T @ ctx - (ctx * wr).T @ tgt) / float(batch)
        W_rare = W_rare + float(lr_rare) * (dW_cf + float(stdp_w) * dW_stdp)
    return W_freq, W_rare


def single_kernel_logits(E: torch.Tensor, ctx_idx: torch.Tensor, W: torch.Tensor) -> torch.Tensor:
    """Next-item logits from one shared kernel: norm(E[ctx]@W^T) @ E^T; returns (n_ctx, n_items)."""
    if ctx_idx.dim() != 1:
        raise ValueError(f"single_kernel_logits: ctx_idx must be 1-D; got {tuple(ctx_idx.shape)}")
    pred = _l2_normalize(E[ctx_idx] @ W.T)
    return pred @ E.T


def routed_logits(
    E: torch.Tensor,
    ctx_idx: torch.Tensor,
    W_freq: torch.Tensor,
    W_rare: torch.Tensor,
    high_mask: torch.Tensor,
) -> torch.Tensor:
    """Frequency-routed next-item logits: high candidates read W_freq, rare read W_rare; (n_ctx, n_items)."""
    if ctx_idx.dim() != 1:
        raise ValueError(f"routed_logits: ctx_idx must be 1-D; got {tuple(ctx_idx.shape)}")
    if high_mask.dim() != 1 or high_mask.shape[0] != E.shape[0]:
        raise ValueError(
            f"routed_logits: high_mask must be (n_items,)={E.shape[0]}; got {tuple(high_mask.shape)}")
    pred_freq = _l2_normalize(E[ctx_idx] @ W_freq.T)
    pred_rare = _l2_normalize(E[ctx_idx] @ W_rare.T)
    logit_freq = pred_freq @ E.T
    logit_rare = pred_rare @ E.T
    mask = high_mask.to(dtype=E.dtype).unsqueeze(0)
    return mask * logit_freq + (1.0 - mask) * logit_rare


def _check_pairs(E: torch.Tensor, ctx_idx: torch.Tensor, tgt_idx: torch.Tensor) -> None:
    """Validate embedding matrix and paired index tensors; raises ValueError on misuse."""
    if E.dim() != 2:
        raise ValueError(f"E must be 2-D (n_items, n_dim); got {tuple(E.shape)}")
    if ctx_idx.dim() != 1 or tgt_idx.dim() != 1:
        raise ValueError("ctx_idx and tgt_idx must be 1-D")
    if ctx_idx.shape[0] != tgt_idx.shape[0]:
        raise ValueError(
            f"ctx_idx and tgt_idx must have equal length; got {ctx_idx.shape[0]} vs {tgt_idx.shape[0]}")


# ----- Formula selftests (reproduce the certified cell's instrumentation selftests) ----------


def _selftest_delta_rule_contracts_error() -> None:
    """ST1: one cf-RPE update on a unit-norm context shrinks the residual by exactly (1 - lr)."""
    from verification import theory
    gen = torch.Generator().manual_seed(42)
    n_dim = 64
    ctx = _l2_normalize(torch.randn(1, n_dim, generator=gen))
    tgt = _l2_normalize(torch.randn(1, n_dim, generator=gen))
    W = torch.zeros((n_dim, n_dim))
    lr = 0.9
    err_before = float((tgt - ctx @ W.T).norm())
    W = W + lr * ((tgt - ctx @ W.T).T @ ctx)
    err_after = float((tgt - ctx @ W.T).norm())
    predicted = theory.compose_freq_delta_touch_contraction(lr) * err_before
    if abs(err_after - predicted) > 1e-4:
        raise AssertionError(f"delta contraction: got {err_after:.5f} expected {predicted:.5f}")


def _selftest_stdp_term_antisymmetric() -> None:
    """ST2: the rare-kernel STDP term (tgt outer ctx - ctx outer tgt) is exactly antisymmetric."""
    gen = torch.Generator().manual_seed(1)
    b, n_dim = 4, 48
    ctx = torch.randn(b, n_dim, generator=gen)
    tgt = torch.randn(b, n_dim, generator=gen)
    dW = (tgt.T @ ctx - ctx.T @ tgt) / float(b)
    if float((dW + dW.T).abs().max()) > 1e-4:
        raise AssertionError("STDP term not antisymmetric")


def _selftest_freq_ranks_and_mask() -> None:
    """ST3: most-frequent item gets rank 0; high_frequency_mask picks the top-k."""
    idx = torch.tensor([1, 2, 1, 3, 1, 2, 1], dtype=torch.long)
    ranks = composition_frequency_ranks(idx, n_items=5)
    if int(ranks[1]) != 0:
        raise AssertionError(f"most-frequent item rank != 0; got {int(ranks[1])}")
    mask = high_frequency_mask(ranks, threshold=2)
    if int(mask.sum()) != 2:
        raise AssertionError(f"high_frequency_mask top-2 count != 2; got {int(mask.sum())}")


def _selftest_kernels_differ() -> None:
    """ST4/AF: raw-Hebbian, single-delta, and routed kernels produce distinct logits (arms differ)."""
    gen_np = torch.Generator().manual_seed(0)
    V, n_dim = 12, 96
    E = _l2_normalize(torch.randn(V, n_dim, generator=gen_np))
    ctx_idx = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.long)
    tgt_idx = torch.tensor([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=torch.long)
    ranks = composition_frequency_ranks(tgt_idx, n_items=V)
    hmask = high_frequency_mask(ranks, threshold=3)
    g1 = torch.Generator().manual_seed(5)
    g2 = torch.Generator().manual_seed(5)
    Wh = build_hebbian_kernel(E, ctx_idx, tgt_idx)
    Ws = build_single_kernel(E, ctx_idx, tgt_idx, n_steps=20, batch=4, lr=0.5, generator=g1)
    Wf, Wr = build_freq_routed_kernels(E, ctx_idx, tgt_idx, hmask, n_steps=20, batch=4,
                                       lr_high=0.5, lr_rare=0.2, stdp_w=0.5, generator=g2)
    ec = torch.arange(V, dtype=torch.long)
    lh = single_kernel_logits(E, ec, Wh)
    ls = single_kernel_logits(E, ec, Ws)
    lr_ = routed_logits(E, ec, Wf, Wr, hmask)
    if float((lh - ls).abs().mean()) < 1e-6 or float((ls - lr_).abs().mean()) < 1e-6:
        raise AssertionError("kernels produce identical logits (arms not differentiated)")


def _selftest_crosstalk_matches_oracle() -> None:
    """ST5: one high-freq delta update perturbs a correlated rare prediction by ~lr*rho (oracle)."""
    from verification import theory
    n_dim = 256
    gen = torch.Generator().manual_seed(3)
    base = torch.randn(n_dim, generator=gen)
    c_high = _l2_normalize(base)
    noise = torch.randn(n_dim, generator=gen)
    # construct c_rare with a controlled correlation rho to c_high
    rho = 0.4
    c_rare = _l2_normalize(rho * c_high + (1.0 - rho) * _l2_normalize(noise))
    t_high = _l2_normalize(torch.randn(n_dim, generator=gen))
    lr = 0.5
    W = torch.zeros((n_dim, n_dim))
    pred_rare_before = W @ c_rare
    W = W + lr * torch.outer(t_high - W @ c_high, c_high)
    pred_rare_after = W @ c_rare
    actual = float((pred_rare_after - pred_rare_before).norm())
    real_rho = float(c_high @ c_rare)
    predicted = theory.compose_freq_single_kernel_crosstalk(real_rho, lr)  # residual_h is unit-norm
    if abs(actual - predicted) > 1e-3:
        raise AssertionError(f"crosstalk oracle: actual {actual:.5f} vs predicted {predicted:.5f}")


def _run_all_selftests() -> dict:
    _selftest_delta_rule_contracts_error()
    _selftest_stdp_term_antisymmetric()
    _selftest_freq_ranks_and_mask()
    _selftest_kernels_differ()
    _selftest_crosstalk_matches_oracle()
    return {
        "primitive": "compose_frequency_routing",
        "routing": "target-frequency-gated two-kernel cf-RPE associator with routed readout",
        "storage_strategy": "two-kernel associative store (routed readout keeps operators separate)",
        "cg_source": (
            "substrate_compose_freq_routing v5 DEFINITIVE 5-seed cross-N "
            "HARD_PASS_CHAIN_GRADE_DEFINITIVE 2026-06-25; math atom "
            "EXP_substrate_compose_freq_routing_v5_DEFINITIVE"),
    }


if __name__ == "__main__":
    result = _run_all_selftests()
    print(f"[compose_freq_routing selftest] PASS {result}")
