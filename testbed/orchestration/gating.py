"""PhasicGatingNetwork: g_theta MLP for phasic-channel gain selection.

Takes (layer_hidden, channel_loss_vector) -> softmax over K_phasic channels.
Implements Design B from the research drill: a small MLP that learns to weight
phasic channels based on current layer activations + channel-loss values.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class PhasicGatingNetwork(nn.Module):
    """Small MLP: (layer_hidden_dim + K_phasic) -> softmax(K_phasic)."""

    def __init__(self, layer_hidden_dim: int, K_phasic: int,
                  hidden_dim: int = 32) -> None:
        super().__init__()
        if K_phasic < 1:
            raise ValueError("K_phasic must be >= 1")
        if layer_hidden_dim < 1:
            raise ValueError("layer_hidden_dim must be >= 1")
        self.K_phasic = int(K_phasic)
        self.layer_hidden_dim = int(layer_hidden_dim)
        self.input_dim = layer_hidden_dim + K_phasic
        self.net = nn.Sequential(
            nn.Linear(self.input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, K_phasic),
        )

    def forward(self, layer_hidden: torch.Tensor,
                 channel_losses_vec: torch.Tensor) -> torch.Tensor:
        """Return softmax(K_phasic).

        Args:
            layer_hidden:         (D_h,) or (B, D_h) -- pooled over batch if 2D.
            channel_losses_vec:   (K_phasic,) tensor of per-phasic-channel loss values.
        """
        # Pool layer_hidden across batch if it has a batch dim
        if layer_hidden.ndim >= 2:
            h = layer_hidden.reshape(layer_hidden.shape[0], -1).mean(dim=0)
        else:
            h = layer_hidden
        # Resize h to expected dim if it doesn't match (deterministic projection)
        if h.shape[0] != self.layer_hidden_dim:
            # Adaptive average / interpolation
            target = self.layer_hidden_dim
            h_unsq = h.unsqueeze(0).unsqueeze(0)  # (1, 1, D)
            h_pool = F.adaptive_avg_pool1d(h_unsq, target).squeeze(0).squeeze(0)
            h = h_pool
        c = channel_losses_vec.reshape(-1)
        if c.shape[0] != self.K_phasic:
            raise ValueError(
                f"channel_losses_vec dim {c.shape[0]} != K_phasic {self.K_phasic}")
        x = torch.cat([h, c], dim=0)
        logits = self.net(x)
        return F.softmax(logits, dim=0)


# ---------------------------------------------------------------------------
# PROT-022 self-tests
# ---------------------------------------------------------------------------
def _selftest() -> None:
    """PROT-022: output sums to 1.0; sensitive to input changes."""
    print("[selftest gating] start", flush=True)
    torch.manual_seed(0)

    K = 4
    D = 16
    g = PhasicGatingNetwork(layer_hidden_dim=D, K_phasic=K, hidden_dim=32)

    h1 = torch.randn(D, requires_grad=True)
    c1 = torch.tensor([0.5, 0.5, 0.5, 0.5])
    w1 = g(h1, c1)
    assert w1.shape == (K,), f"output shape {w1.shape} != ({K},)"
    sum_w = w1.sum().item()
    assert abs(sum_w - 1.0) < 1e-5, f"softmax does not sum to 1: {sum_w}"
    assert (w1 >= 0.0).all().item(), "softmax has negative entries"
    print(f"  K={K} D={D} w1={[round(v, 4) for v in w1.tolist()]} sum={sum_w:.6f}",
          flush=True)

    # Sensitivity: different channel losses -> different gating
    c2 = torch.tensor([5.0, 0.1, 0.1, 0.1])  # channel 0 very high
    w2 = g(h1, c2)
    assert not torch.allclose(w1, w2, atol=1e-4), (
        "gating insensitive to channel-loss changes")
    print(f"  sensitivity: c=[5,0.1,0.1,0.1] -> w={[round(v, 4) for v in w2.tolist()]}",
          flush=True)

    # Hidden-state sensitivity
    h3 = torch.randn(D, requires_grad=True) * 5.0
    w3 = g(h3, c1)
    assert not torch.allclose(w1, w3, atol=1e-4), "gating insensitive to hidden changes"
    print(f"  hidden sensitivity: alt h -> w={[round(v, 4) for v in w3.tolist()]}",
          flush=True)

    # Gradient flow through softmax
    loss = (w2 * torch.tensor([1.0, 2.0, 3.0, 4.0])).sum()
    loss.backward()
    has_grad = any(p.grad is not None and p.grad.abs().sum().item() > 0
                   for p in g.parameters())
    assert has_grad, "no MLP params received gradient"
    print(f"  gradient flow: MLP params received grad", flush=True)

    # Dim-mismatch adaptive pooling test
    g2 = PhasicGatingNetwork(layer_hidden_dim=8, K_phasic=K)
    h_big = torch.randn(32, requires_grad=True)
    w_big = g2(h_big, c1)
    assert w_big.shape == (K,), "adaptive-pool output shape wrong"
    print(f"  adaptive pooling: D=32 -> 8 worked, sum={w_big.sum().item():.4f}",
          flush=True)

    print("[selftest gating] PASS", flush=True)


if __name__ == "__main__":
    _selftest()
