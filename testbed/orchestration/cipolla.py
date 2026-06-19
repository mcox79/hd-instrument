"""Cipolla precision-vector for multi-task uncertainty weighting.

Implements Kendall-Gal-Cipolla 2018 (arXiv:1705.07115) homoscedastic uncertainty
weighting:

    L_total = sum_k [ (1 / (2*sigma_k^2)) * L_k + log(sigma_k) ]

sigma_k is learned jointly via log_sigma_k = log(sigma_k) as a torch parameter
to keep it positive without explicit clipping. Higher sigma_k -> lower
contribution from channel k (high task uncertainty).
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import torch
import torch.nn as nn


class CipollaPrecisionVector(nn.Module):
    """Per-channel learnable log_sigma scalars implementing Cipolla 2018 weighting.

    Forward returns (total_loss, log_sigma_reg, per_channel_weights) where:
        total_loss        = sum_k (1/(2*sigma_k^2)) * L_k + sum_k log(sigma_k)
        log_sigma_reg     = sum_k log(sigma_k)  (already included in total_loss)
        per_channel_weights = {channel_name: 1/(2*sigma_k^2)} for logging
    """

    def __init__(self, channel_names: List[str],
                  log_sigma_init: float = 0.0,
                  log_sigma_min: float = -5.0,
                  log_sigma_max: float = 5.0) -> None:
        super().__init__()
        if len(channel_names) == 0:
            raise ValueError("channel_names must be non-empty")
        self.channel_names = list(channel_names)
        self.log_sigma_min = float(log_sigma_min)
        self.log_sigma_max = float(log_sigma_max)
        self.log_sigma = nn.Parameter(
            torch.full((len(channel_names),), float(log_sigma_init), dtype=torch.float32)
        )

    def sigma(self) -> torch.Tensor:
        """sigma_k = exp(log_sigma_k), clamped to (exp(min), exp(max))."""
        return torch.exp(torch.clamp(self.log_sigma, self.log_sigma_min, self.log_sigma_max))

    def precision(self) -> torch.Tensor:
        """precision_k = 1 / (2 * sigma_k^2)."""
        sig = self.sigma()
        return 1.0 / (2.0 * sig.pow(2) + 1e-10)

    def forward(self, channel_losses: Dict[str, torch.Tensor]
                ) -> Tuple[torch.Tensor, torch.Tensor, Dict[str, float]]:
        """Compute Cipolla-weighted total loss.

        Args:
            channel_losses: {channel_name: scalar torch.Tensor}.
                            Channels not present in self.channel_names are ignored.
                            Channels in self.channel_names but not present in dict
                            are treated as zero (no contribution).
        """
        sig = self.sigma()
        prec = 1.0 / (2.0 * sig.pow(2) + 1e-10)
        log_sig_term = torch.log(sig + 1e-10).sum()

        total = log_sig_term
        weights_log: Dict[str, float] = {}
        for k, name in enumerate(self.channel_names):
            w_k = prec[k]
            weights_log[name] = float(w_k.item())
            L_k = channel_losses.get(name)
            if L_k is None:
                continue
            if not isinstance(L_k, torch.Tensor):
                continue
            total = total + w_k * L_k
        return total, log_sig_term, weights_log


# ---------------------------------------------------------------------------
# PROT-022 self-tests
# ---------------------------------------------------------------------------
def _selftest() -> None:
    """PROT-022: sigma_k initialization, log-sigma regularization, learnability."""
    print("[selftest cipolla] start", flush=True)
    torch.manual_seed(0)
    names = ["A", "B", "C"]
    cv = CipollaPrecisionVector(names, log_sigma_init=0.0)

    # Initialization: sigma_k = exp(0) = 1.0, precision = 1/2
    sig = cv.sigma()
    prec = cv.precision()
    assert torch.allclose(sig, torch.ones(3), atol=1e-4), f"sigma init: {sig}"
    assert torch.allclose(prec, torch.full((3,), 0.5), atol=1e-4), f"prec init: {prec}"
    print(f"  init sigma={sig.tolist()} precision={prec.tolist()}", flush=True)

    # Forward with three losses
    losses = {
        "A": torch.tensor(1.0, requires_grad=True),
        "B": torch.tensor(2.0, requires_grad=True),
        "C": torch.tensor(0.5, requires_grad=True),
    }
    total, log_reg, weights = cv(losses)
    # Expected: 0.5 * 1.0 + 0.5 * 2.0 + 0.5 * 0.5 + 3 * log(1) = 0.5+1.0+0.25+0 = 1.75
    expected_total = 0.5 * 1.0 + 0.5 * 2.0 + 0.5 * 0.5 + 0.0
    assert abs(total.item() - expected_total) < 1e-3, (
        f"total mismatch: got {total.item()}, expected {expected_total}")
    print(f"  total={total.item():.4f} log_reg={log_reg.item():.4f} weights={weights}", flush=True)

    # log_sigma is learnable
    total.backward()
    assert cv.log_sigma.grad is not None, "log_sigma.grad is None after backward"
    assert torch.isfinite(cv.log_sigma.grad).all().item(), "log_sigma.grad has nan"
    print(f"  log_sigma.grad={cv.log_sigma.grad.tolist()}", flush=True)

    # Verify sigma stays positive after a few gradient steps
    cv2 = CipollaPrecisionVector(names, log_sigma_init=0.0)
    opt = torch.optim.SGD([cv2.log_sigma], lr=0.1)
    for _ in range(20):
        losses_step = {
            "A": torch.tensor(1.0),
            "B": torch.tensor(5.0),  # B has high loss -> sigma_B should grow
            "C": torch.tensor(0.1),
        }
        total_s, _, _ = cv2(losses_step)
        opt.zero_grad()
        total_s.backward()
        opt.step()
    sig_after = cv2.sigma()
    assert (sig_after > 0.0).all().item(), f"sigma went non-positive: {sig_after}"
    assert sig_after[1].item() > sig_after[0].item(), (
        f"sigma_B should grow above sigma_A; got A={sig_after[0]} B={sig_after[1]}")
    print(f"  after 20 steps: sigma={sig_after.tolist()} (B should be > A: {sig_after[1] > sig_after[0]})",
          flush=True)

    # Channel-not-present case
    losses_partial = {"A": torch.tensor(1.0)}
    total_p, _, _ = cv(losses_partial)
    # Should not crash; B/C contribute 0 to weighted sum (but log_reg still has 3 terms)
    assert torch.isfinite(total_p).item(), "partial-losses gave nan"

    print("[selftest cipolla] PASS", flush=True)


if __name__ == "__main__":
    _selftest()
