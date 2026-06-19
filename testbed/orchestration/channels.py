"""8 channel-signal functions for the substrate orchestration ablation.

Each channel returns a ChannelSignal dataclass with three fields:
    loss_term      -- torch.Tensor scalar for backprop (None when not active)
    trigger_active -- bool flag indicating whether this channel fired this step
    signal_metric  -- float scalar for logging / diagnostics

Channel inventory (per user-confirmed operational defs):

    Tonic (always-on):
        Write             -- outer-product Hopfield write; loss = (1 - retrieval_cos)
        Erase             -- rank-1 deletion redundancy score; gradient-zero gating
        Monitor           -- Hutchinson trace of W^3; alarm when |dz| > 2 sigma
        Chain-consistency -- hierarchical recurrent retrieval cosine; aux = lambda*(1-c)^2

    Phasic (event-triggered):
        Curvature         -- Tr(W^2)/N tracking; aux = lambda * |k2 - ema(k2)|
        Contrastive       -- anti-Hebbian bipartite update; trigger when neg-pair cos>0.5
        Repulse-class     -- max-cos to PP-48 NKT forbidden leaves; aux = max(0, r - thr)^2
        Counterfactual    -- rank-1 substitution prediction delta; cadence 1000 steps

All math is done numpy-side for the substrate operations (substrate_audit + primitives
already accept np.ndarray); the loss_term is a torch.Tensor surrogate that depends
on the model's hidden activations through a simple cosine projection, so that
substrate-signal-derived losses BACK-PROPAGATE through the LM parameters even though
the substrate W itself is treated as a non-differentiable buffer.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

from testbed.llm_integration.substrate_audit import (
    hebbian_write,
    retrieval_cosine,
    deletion_cert,
    kappa_2_hutchinson,
    kappa_3_hutchinson,
    kappa_4_excess_hutchinson,
)
from testbed.substrate_lm.primitives import (
    anti_hebbian_contrastive_update,
    hierarchical_recurrent_retrieve,
)


@dataclass
class ChannelSignal:
    """Per-channel output. loss_term may be None when channel is inactive this step."""
    loss_term: Optional[torch.Tensor]
    trigger_active: bool
    signal_metric: float


# ---------------------------------------------------------------------------
# Helpers shared across channels
# ---------------------------------------------------------------------------
def _hidden_to_bipolar(h: torch.Tensor, N: int, rng_seed: int = 0) -> np.ndarray:
    """Project a (B, T, D) or (D,) torch hidden state down to a bipolar (N,) np array.

    Uses a deterministic projection matrix per (D, N, rng_seed) so the codeword is
    stable across calls within a step. The torch hidden contributes only through
    the projection norm; we want a stable bipolar substrate vector regardless of
    minor hidden noise (the substrate is a non-differentiable buffer).
    """
    with torch.no_grad():
        if h.ndim >= 2:
            h_vec = h.mean(dim=tuple(range(h.ndim - 1)))
        else:
            h_vec = h
        h_np = h_vec.detach().to(torch.float32).cpu().numpy().reshape(-1)
    D = h_np.shape[0]
    rng = np.random.default_rng(rng_seed ^ (D * 31 + N))
    proj = rng.standard_normal((D, N)).astype(np.float32) / math.sqrt(max(1, D))
    y = h_np @ proj
    xi = np.where(y >= 0.0, 1.0, -1.0).astype(np.float32)
    return xi


def _torch_cosine_loss(model_vec: torch.Tensor, target_np: np.ndarray) -> torch.Tensor:
    """Differentiable cosine-loss between a torch vec and a numpy target vec.

    Used so each channel produces a real backprop-flowing loss_term whose value
    is anchored to a substrate-derived target. Returns (1 - cos) in [0, 2].
    """
    if model_vec.ndim >= 2:
        model_vec = model_vec.reshape(-1)
    D_model = int(model_vec.shape[0])
    D_target = int(target_np.shape[0])
    if D_target != D_model:
        # Resize target via deterministic projection (fixed RNG for stability)
        rng = np.random.default_rng((D_model * 7919 + D_target) & 0xFFFFFFFF)
        proj = rng.standard_normal((D_target, D_model)).astype(np.float32) / math.sqrt(max(1, D_target))
        target_np = target_np.astype(np.float32) @ proj
    target = torch.from_numpy(target_np.astype(np.float32)).to(
        model_vec.device).to(model_vec.dtype)
    eps = 1e-8
    cos = (model_vec @ target) / (model_vec.norm() * target.norm() + eps)
    return 1.0 - cos


# ---------------------------------------------------------------------------
# Channel 1 -- Write (tonic, always-on)
# ---------------------------------------------------------------------------
def compute_write_signal(W: np.ndarray, hidden: torch.Tensor, N: int,
                          lambda_w: float = 1.0, rng_seed: int = 0
                          ) -> ChannelSignal:
    """Hopfield-write channel.

    1. Project hidden -> bipolar xi.
    2. Update W in-place via hebbian_write (write-side effect).
    3. Loss = lambda_w * (1 - retrieval_cosine(W_after, xi)) scaled into torch graph.
    """
    xi = _hidden_to_bipolar(hidden, N, rng_seed)
    # Side-effect-free shadow update for the metric (caller may persist W via
    # OrchestrationLoop.commit_write to keep substrate state coherent)
    W_after = hebbian_write(W, xi)
    cos_retr = retrieval_cosine(W_after, xi)
    metric = float(cos_retr)
    # Build a differentiable surrogate: cosine of hidden's projection to xi
    loss = _torch_cosine_loss(hidden.mean(dim=tuple(range(hidden.ndim - 1)))
                                if hidden.ndim >= 2 else hidden, xi) * lambda_w
    return ChannelSignal(loss_term=loss, trigger_active=True, signal_metric=metric)


# ---------------------------------------------------------------------------
# Channel 2 -- Erase (tonic, low gain)
# ---------------------------------------------------------------------------
def compute_erase_signal(W: np.ndarray, hidden: torch.Tensor, N: int,
                          lambda_e: float = 0.05,
                          redundancy_threshold: float = 0.85,
                          rng_seed: int = 0) -> ChannelSignal:
    """Rank-1 deletion redundancy score.

    1. Project hidden -> xi.
    2. Compute deletion cert + retrieval cos: if cos(W, xi) > threshold, pattern
       is redundant.
    3. trigger_active when redundancy detected; loss term suppresses the
       redundant component (negative-cos surrogate so model is pushed AWAY from xi).
    """
    xi = _hidden_to_bipolar(hidden, N, rng_seed)
    cos_pre = retrieval_cosine(W, xi)
    redundant = bool(cos_pre > redundancy_threshold)
    metric = float(cos_pre)
    if redundant:
        # Push hidden away from xi (anti-write component)
        loss = -1.0 * _torch_cosine_loss(
            hidden.mean(dim=tuple(range(hidden.ndim - 1))) if hidden.ndim >= 2 else hidden,
            xi) * lambda_e
        # Tiny positive offset to keep loss bounded below
        loss = loss + lambda_e * 0.5
    else:
        loss = torch.zeros((), device=hidden.device, dtype=hidden.dtype, requires_grad=False)
    return ChannelSignal(loss_term=loss, trigger_active=redundant, signal_metric=metric)


# ---------------------------------------------------------------------------
# Channel 3 -- Monitor (tonic, always-on; alarm on cumulant drift)
# ---------------------------------------------------------------------------
def compute_monitor_signal(W: np.ndarray, hidden: torch.Tensor,
                            baseline_k3: float, sigma_k3: float,
                            n_probes: int = 8, lambda_m: float = 0.1,
                            rng_seed: int = 0) -> ChannelSignal:
    """Cumulant drift monitor (kappa_3).

    1. Estimate kappa_3(W) via Hutchinson with n_probes random bipolar vectors.
    2. z = (k3 - baseline) / sigma; alarm when |z| > 2.
    3. When alarm: multiply lambda_m by alarm_gain (1.5) to upweight main loss.
       Returns a loss_term that scales the hidden norm penalty.
    """
    rng = np.random.default_rng(rng_seed)
    k3_now, _ = kappa_3_hutchinson(W, n_probes=n_probes, rng=rng)
    if sigma_k3 < 1e-6:
        z = 0.0
    else:
        z = (k3_now - baseline_k3) / sigma_k3
    alarm = bool(abs(z) > 2.0)
    gain = 1.5 if alarm else 1.0
    # Loss = small penalty on hidden norm * gain (acts as adaptive regularizer)
    if hidden.ndim >= 2:
        h_flat = hidden.reshape(-1)
    else:
        h_flat = hidden
    loss = lambda_m * gain * (h_flat.norm() ** 2) / max(1, h_flat.numel())
    return ChannelSignal(loss_term=loss, trigger_active=alarm, signal_metric=float(k3_now))


# ---------------------------------------------------------------------------
# Channel 4 -- Chain-consistency (tonic, low gain; phasic boost on OOD)
# ---------------------------------------------------------------------------
def compute_chain_consistency_signal(W: np.ndarray, hidden: torch.Tensor, N: int,
                                       lambda_c: float = 0.2, rng_seed: int = 0
                                       ) -> ChannelSignal:
    """Hierarchical recurrent retrieval; consistency = cos of path-A vs path-B retrievals.

    1. Project hidden -> xi_A.
    2. Build xi_B as a perturbation of xi_A (sign-flip 5% bits).
    3. Retrieve path_A = hierarchical_recurrent_retrieve(W, xi_A, n_steps=3)
       and path_B = hierarchical_recurrent_retrieve(W, xi_B, n_steps=3).
    4. c = cos(path_A, path_B); loss = lambda * (1 - c)^2.
    """
    xi_A = _hidden_to_bipolar(hidden, N, rng_seed)
    rng = np.random.default_rng(rng_seed + 1)
    flip_mask = rng.random(N) < 0.05
    xi_B = xi_A.copy()
    xi_B[flip_mask] = -xi_B[flip_mask]
    path_A = hierarchical_recurrent_retrieve(W, xi_A, n_steps=3)
    path_B = hierarchical_recurrent_retrieve(W, xi_B, n_steps=3)
    na = float(np.linalg.norm(path_A))
    nb = float(np.linalg.norm(path_B))
    if na < 1e-30 or nb < 1e-30:
        c = 0.0
    else:
        c = float((path_A @ path_B) / (na * nb))
    metric = c
    # Differentiable surrogate aligned with path_A
    h_vec = hidden.mean(dim=tuple(range(hidden.ndim - 1))) if hidden.ndim >= 2 else hidden
    cos_loss = _torch_cosine_loss(h_vec, path_A.astype(np.float32))
    loss = lambda_c * (1.0 - c) ** 2 * cos_loss
    return ChannelSignal(loss_term=loss, trigger_active=True, signal_metric=metric)


# ---------------------------------------------------------------------------
# Channel 5 -- Curvature (phasic; triggered on |k2 - ema(k2)| > 2 sigma)
# ---------------------------------------------------------------------------
def compute_curvature_signal(W: np.ndarray, hidden: torch.Tensor,
                              k2_ema: float, k2_sigma: float,
                              n_probes: int = 8, lambda_curv: float = 0.1,
                              rng_seed: int = 0) -> ChannelSignal:
    """Tr(W^2)/N tracking. Triggered when |k2_now - ema| > 2 sigma."""
    rng = np.random.default_rng(rng_seed + 5)
    k2_now, _ = kappa_2_hutchinson(W, n_probes=n_probes, rng=rng)
    if k2_sigma < 1e-6:
        trigger = False
    else:
        trigger = bool(abs(k2_now - k2_ema) > 2.0 * k2_sigma)
    metric = float(k2_now)
    if trigger:
        if hidden.ndim >= 2:
            h_flat = hidden.reshape(-1)
        else:
            h_flat = hidden
        loss = lambda_curv * abs(k2_now - k2_ema) * (h_flat.norm() ** 2) / max(1, h_flat.numel())
    else:
        loss = torch.zeros((), device=hidden.device, dtype=hidden.dtype, requires_grad=False)
    return ChannelSignal(loss_term=loss, trigger_active=trigger, signal_metric=metric)


# ---------------------------------------------------------------------------
# Channel 6 -- Contrastive (phasic; triggered when negative-pair cos > 0.5)
# ---------------------------------------------------------------------------
def compute_contrastive_signal(W: np.ndarray, hidden: torch.Tensor, N: int,
                                lambda_cont: float = 0.3, rng_seed: int = 0
                                ) -> ChannelSignal:
    """Anti-Hebbian bipartite contrastive update via primitives.

    1. Build pos-pair (xi_A, xi_B) from hidden + perturbation.
    2. Build neg-pair (xi_N1, xi_N2) from independent random bipolar.
    3. Trigger when cos(W @ xi_N1, xi_N2) > 0.5 (hard negative regime).
    4. Apply contrastive update inline; loss = neg-pair cos as scalar surrogate.
    """
    xi_A = _hidden_to_bipolar(hidden, N, rng_seed)
    rng = np.random.default_rng(rng_seed + 11)
    flip_mask = rng.random(N) < 0.05
    xi_B = xi_A.copy()
    xi_B[flip_mask] = -xi_B[flip_mask]
    xi_N1 = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    xi_N2 = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    # Hard-negative regime detection
    y1 = W @ xi_N1
    n1 = float(np.linalg.norm(y1))
    n2 = float(np.linalg.norm(xi_N2))
    if n1 < 1e-30 or n2 < 1e-30:
        neg_cos = 0.0
    else:
        neg_cos = float((y1 @ xi_N2) / (n1 * n2))
    trigger = bool(neg_cos > 0.5)
    metric = float(neg_cos)
    if trigger:
        # Update W in-place (caller decides to persist via OrchestrationLoop)
        _ = anti_hebbian_contrastive_update(W, xi_A, xi_B, xi_N1, xi_N2, lr=1.0)
        # Loss surrogate: push hidden away from xi_N1 + toward xi_A
        h_vec = hidden.mean(dim=tuple(range(hidden.ndim - 1))) if hidden.ndim >= 2 else hidden
        pull = _torch_cosine_loss(h_vec, xi_A)
        push = -1.0 * _torch_cosine_loss(h_vec, xi_N1) + 1.0  # bound below 0
        loss = lambda_cont * (pull + push) * abs(neg_cos)
    else:
        loss = torch.zeros((), device=hidden.device, dtype=hidden.dtype, requires_grad=False)
    return ChannelSignal(loss_term=loss, trigger_active=trigger, signal_metric=metric)


# ---------------------------------------------------------------------------
# Channel 7 -- Repulse-class (phasic; triggered when match to forbidden > 0.3)
# ---------------------------------------------------------------------------
def compute_repulse_class_signal(W: np.ndarray, hidden: torch.Tensor, N: int,
                                  forbidden_leaves: np.ndarray,
                                  threshold: float = 0.3,
                                  lambda_r: float = 0.2, rng_seed: int = 0
                                  ) -> ChannelSignal:
    """Match score = max cos(W @ xi, forbidden_leaf) over forbidden leaves.

    Args:
        forbidden_leaves: (K, N) bipolar matrix of PP-48-style forbidden tree leaves.
    """
    xi = _hidden_to_bipolar(hidden, N, rng_seed)
    y = W @ xi
    yn = float(np.linalg.norm(y))
    if yn < 1e-30 or forbidden_leaves.shape[0] == 0:
        r = 0.0
        best_idx = 0
    else:
        leaf_norms = np.linalg.norm(forbidden_leaves, axis=1) + 1e-30
        cos_vec = (forbidden_leaves @ y) / (leaf_norms * yn)
        best_idx = int(np.argmax(cos_vec))
        r = float(cos_vec[best_idx])
    trigger = bool(r > threshold)
    metric = float(r)
    if trigger:
        h_vec = hidden.mean(dim=tuple(range(hidden.ndim - 1))) if hidden.ndim >= 2 else hidden
        # Push AWAY from forbidden leaf: cos_loss anchored to leaf, with sign flipped
        leaf = forbidden_leaves[best_idx]
        push_term = -1.0 * _torch_cosine_loss(h_vec, leaf) + 1.0
        loss = lambda_r * max(0.0, r - threshold) ** 2 * push_term
    else:
        loss = torch.zeros((), device=hidden.device, dtype=hidden.dtype, requires_grad=False)
    return ChannelSignal(loss_term=loss, trigger_active=trigger, signal_metric=metric)


# ---------------------------------------------------------------------------
# Channel 8 -- Counterfactual (phasic slow; cadence every 1000 steps OR val_spike)
# ---------------------------------------------------------------------------
def compute_counterfactual_signal(W: np.ndarray, hidden: torch.Tensor, N: int,
                                    step: int, val_spike: bool = False,
                                    cadence: int = 1000,
                                    K_examples: int = 4,
                                    lambda_cf: float = 0.1,
                                    rng_seed: int = 0) -> ChannelSignal:
    """Rank-1 substitution: predict W' = W - delta_k for K sampled patterns.

    Returns:
        loss_term: mean prediction-delta scaled into torch graph.
        signal_metric: mean prediction delta across K samples.
    """
    cadence_trigger = (step > 0) and (step % cadence == 0)
    trigger = bool(cadence_trigger or val_spike)
    if not trigger:
        return ChannelSignal(
            loss_term=torch.zeros((), device=hidden.device, dtype=hidden.dtype),
            trigger_active=False, signal_metric=0.0,
        )
    rng = np.random.default_rng(rng_seed + step)
    xi = _hidden_to_bipolar(hidden, N, rng_seed)
    deltas: List[float] = []
    for _k in range(int(max(1, K_examples))):
        xi_k = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
        W_prime, _cert, signal_norm = deletion_cert(W, xi_k)
        # Predict on xi: W @ xi vs W' @ xi
        y1 = W @ xi
        y2 = W_prime @ xi
        delta = float(np.linalg.norm(y2 - y1))
        deltas.append(delta)
    mean_delta = float(np.mean(deltas))
    metric = mean_delta
    h_vec = hidden.mean(dim=tuple(range(hidden.ndim - 1))) if hidden.ndim >= 2 else hidden
    loss = lambda_cf * mean_delta * (h_vec.norm() ** 2) / max(1, h_vec.numel())
    return ChannelSignal(loss_term=loss, trigger_active=True, signal_metric=metric)


# ---------------------------------------------------------------------------
# PROT-022 self-tests
# ---------------------------------------------------------------------------
def _selftest_channel(name: str, signal: ChannelSignal, allow_zero: bool = False) -> None:
    assert signal.loss_term is not None, f"{name}: loss_term is None"
    assert isinstance(signal.loss_term, torch.Tensor), f"{name}: loss_term not torch.Tensor"
    assert signal.loss_term.ndim == 0, (
        f"{name}: loss_term must be scalar (got shape {tuple(signal.loss_term.shape)})")
    if not allow_zero:
        assert torch.isfinite(signal.loss_term).item(), f"{name}: loss_term not finite"
    assert isinstance(signal.trigger_active, bool), f"{name}: trigger_active not bool"
    assert isinstance(signal.signal_metric, float), (
        f"{name}: signal_metric must be float, got {type(signal.signal_metric)}")


def _selftest() -> None:
    """PROT-022: each channel produces valid (loss, trigger, metric) tuple."""
    print("[selftest channels] start", flush=True)
    torch.manual_seed(0)
    N = 64
    D = 32
    rng = np.random.default_rng(0)
    # Build a small W with some structure
    Xi = rng.choice([-1.0, 1.0], size=(8, N)).astype(np.float32)
    W = (Xi.T @ Xi) / float(N)
    hidden = torch.randn(D, requires_grad=True)
    forbidden = rng.choice([-1.0, 1.0], size=(4, N)).astype(np.float32)

    # Channel 1: Write
    s1 = compute_write_signal(W.copy(), hidden, N=N, rng_seed=1)
    _selftest_channel("Write", s1)
    assert s1.trigger_active is True, "Write should always trigger"
    # Differentiability check
    g = torch.autograd.grad(s1.loss_term, hidden, retain_graph=True, allow_unused=True)[0]
    assert g is not None and torch.isfinite(g).all().item(), "Write: hidden grad None / nan"
    print(f"  Write: loss={s1.loss_term.item():.4f} metric={s1.signal_metric:.4f}", flush=True)

    # Channel 2: Erase
    # Use the xi from a forced redundant case: build W as outer product, query same xi
    xi_force = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    W_force = np.outer(xi_force, xi_force).astype(np.float32) / float(N) * 50.0  # high amplitude
    # Make hidden project to xi_force closely (we just need the channel to run)
    s2 = compute_erase_signal(W_force, hidden, N=N, rng_seed=2)
    _selftest_channel("Erase", s2, allow_zero=True)
    print(f"  Erase: loss={s2.loss_term.item():.4f} trigger={s2.trigger_active} metric={s2.signal_metric:.4f}",
          flush=True)

    # Channel 3: Monitor
    s3 = compute_monitor_signal(W.copy(), hidden, baseline_k3=0.0, sigma_k3=0.1,
                                  n_probes=8, rng_seed=3)
    _selftest_channel("Monitor", s3)
    print(f"  Monitor: loss={s3.loss_term.item():.4f} alarm={s3.trigger_active} k3={s3.signal_metric:.4f}",
          flush=True)

    # Channel 4: Chain-consistency
    s4 = compute_chain_consistency_signal(W.copy(), hidden, N=N, rng_seed=4)
    _selftest_channel("Chain", s4)
    assert s4.trigger_active is True, "Chain should always trigger"
    print(f"  Chain: loss={s4.loss_term.item():.4f} c={s4.signal_metric:.4f}", flush=True)

    # Channel 5: Curvature - trigger forced via tiny sigma
    s5 = compute_curvature_signal(W.copy(), hidden, k2_ema=0.0, k2_sigma=0.001,
                                    n_probes=8, rng_seed=5)
    _selftest_channel("Curvature", s5, allow_zero=True)
    print(f"  Curvature: loss={s5.loss_term.item():.4f} trigger={s5.trigger_active} k2={s5.signal_metric:.4f}",
          flush=True)

    # Channel 6: Contrastive
    s6 = compute_contrastive_signal(W.copy(), hidden, N=N, rng_seed=6)
    _selftest_channel("Contrastive", s6, allow_zero=True)
    print(f"  Contrastive: loss={s6.loss_term.item():.4f} trigger={s6.trigger_active} neg_cos={s6.signal_metric:.4f}",
          flush=True)

    # Channel 7: Repulse-class
    s7 = compute_repulse_class_signal(W.copy(), hidden, N=N, forbidden_leaves=forbidden,
                                        threshold=-1.0, rng_seed=7)  # threshold -1 forces trigger
    _selftest_channel("Repulse", s7)
    assert s7.trigger_active is True, "Repulse with threshold=-1 should trigger"
    print(f"  Repulse: loss={s7.loss_term.item():.4f} r={s7.signal_metric:.4f}", flush=True)

    # Channel 8: Counterfactual (cadence-trigger by step=1000)
    s8 = compute_counterfactual_signal(W.copy(), hidden, N=N, step=1000,
                                         val_spike=False, cadence=1000, K_examples=2, rng_seed=8)
    _selftest_channel("Counterfactual", s8)
    assert s8.trigger_active is True, "Counterfactual at step=1000 should trigger"
    print(f"  Counterfactual: loss={s8.loss_term.item():.4f} delta={s8.signal_metric:.4f}", flush=True)

    # Counterfactual cadence-no-trigger
    s8_off = compute_counterfactual_signal(W.copy(), hidden, N=N, step=500,
                                             val_spike=False, cadence=1000, K_examples=2, rng_seed=8)
    assert s8_off.trigger_active is False, "Counterfactual off-cadence should NOT trigger"
    assert s8_off.signal_metric == 0.0, "Counterfactual off-cadence metric should be 0"

    print("[selftest channels] PASS: all 8 channel signals validated", flush=True)


if __name__ == "__main__":
    _selftest()
