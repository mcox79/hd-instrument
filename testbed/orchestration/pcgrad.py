"""PCGrad pairwise conflict projection.

Implements Yu et al. NeurIPS 2020 (arXiv:2006.06520) gradient surgery:
when cos(g_i, g_j) < 0, project g_i onto subspace orthogonal to g_j:

    g_i_proj = g_i - (g_i . g_j / ||g_j||^2) * g_j

For K gradient lists this is O(K^2) pairwise projection; we shuffle the order
each call as recommended by the paper to avoid bias toward later channels.
"""
from __future__ import annotations

import random
from typing import List, Sequence

import torch


class PCGradProjector:
    """Pairwise conflict projection over a list of gradient vectors.

    Each input gradient is a single torch.Tensor (flattened or any shape that
    supports .reshape(-1) for dot products); the projector returns the same
    shapes.

    NOTE: the actual model.backward()-driven workflow takes per-parameter
    gradients in many tensors. For simplicity here we project FLATTENED
    per-channel gradients (one big tensor per channel), and downstream callers
    can reshape or re-assemble as needed. The orchestrator integrates this with
    parameter-wise grads via apply_pcgrad_to_param_lists().
    """

    def __init__(self, shuffle: bool = True, eps: float = 1e-12) -> None:
        self.shuffle = bool(shuffle)
        self.eps = float(eps)

    def project(self, grad_list: Sequence[torch.Tensor]) -> List[torch.Tensor]:
        """Return projected gradients (no in-place mutation of inputs).

        Per Yu et al. 2020: each g_i is projected against the ORIGINAL g_j (not
        the in-progress projection of g_j). Order of pairing is shuffled to
        avoid bias toward later channels.
        """
        if len(grad_list) == 0:
            return []
        K = len(grad_list)
        # Flatten ORIGINAL gradients (for dot-product targets)
        original_flats = [g.reshape(-1).clone() for g in grad_list]
        # Working copies that get projected
        proj_flats = [g.clone() for g in original_flats]

        for i in range(K):
            order = [j for j in range(K) if j != i]
            if self.shuffle:
                random.shuffle(order)
            for j in order:
                g_j = original_flats[j]
                norm_j_sq = (g_j @ g_j)
                if norm_j_sq.item() < self.eps:
                    continue
                g_i = proj_flats[i]
                dot_ij = (g_i @ g_j)
                if dot_ij.item() < 0.0:
                    proj_flats[i] = g_i - (dot_ij / (norm_j_sq + self.eps)) * g_j

        # Reshape back
        out: List[torch.Tensor] = []
        for k in range(K):
            out.append(proj_flats[k].reshape(grad_list[k].shape))
        return out


def apply_pcgrad_to_param_lists(
    grad_per_channel_per_param: List[List[torch.Tensor]],
    projector: PCGradProjector,
) -> List[List[torch.Tensor]]:
    """Apply PCGrad to a list-of-lists structure (channel -> per-param-grads).

    Flattens each channel into a single vector for pairwise projection, then
    reshapes back into the per-parameter structure. This is the standard PCGrad
    integration for PyTorch models.
    """
    K = len(grad_per_channel_per_param)
    if K == 0:
        return []
    n_params = len(grad_per_channel_per_param[0])
    # Flatten each channel
    shapes = [g.shape for g in grad_per_channel_per_param[0]]
    flats = []
    for k in range(K):
        chan = grad_per_channel_per_param[k]
        if len(chan) != n_params:
            raise ValueError(f"channel {k} has {len(chan)} grads, expected {n_params}")
        flats.append(torch.cat([g.reshape(-1) for g in chan]))

    projected_flats = projector.project(flats)

    out: List[List[torch.Tensor]] = []
    for k in range(K):
        chan_flat = projected_flats[k]
        chan_out = []
        offset = 0
        for shape in shapes:
            n = 1
            for d in shape:
                n *= int(d)
            chan_out.append(chan_flat[offset:offset + n].reshape(shape))
            offset += n
        out.append(chan_out)
    return out


# ---------------------------------------------------------------------------
# PROT-022 self-tests
# ---------------------------------------------------------------------------
def _selftest() -> None:
    """PROT-022: anti-parallel -> projected magnitude reduced; orthogonal -> unchanged."""
    print("[selftest pcgrad] start", flush=True)
    torch.manual_seed(0)
    proj = PCGradProjector(shuffle=False)

    # Test 1: two anti-parallel vectors -> after projection both should reduce in magnitude
    g1 = torch.tensor([1.0, 0.0])
    g2 = torch.tensor([-1.0, 0.0])
    out = proj.project([g1, g2])
    # g1 projected against g2 (which is anti-parallel) -> g1 - (g1.g2 / ||g2||^2) * g2
    #   = [1,0] - (-1 / 1) * [-1,0] = [1,0] - [1,0] = [0,0]
    # Similarly g2 -> g2 - (g2.g1 / ||g1||^2) * g1 = [-1,0] - (-1) * [1,0] = [-1,0] + [1,0] = [0,0]
    assert torch.allclose(out[0], torch.zeros(2), atol=1e-6), f"anti-parallel g1 -> {out[0]}"
    assert torch.allclose(out[1], torch.zeros(2), atol=1e-6), f"anti-parallel g2 -> {out[1]}"
    print(f"  anti-parallel: g1_proj={out[0].tolist()} g2_proj={out[1].tolist()} (both zero -> conflict resolved)",
          flush=True)

    # Test 2: orthogonal vectors -> unchanged
    g1 = torch.tensor([1.0, 0.0])
    g2 = torch.tensor([0.0, 1.0])
    out = proj.project([g1, g2])
    assert torch.allclose(out[0], g1, atol=1e-6), f"orth g1 changed: {out[0]}"
    assert torch.allclose(out[1], g2, atol=1e-6), f"orth g2 changed: {out[1]}"
    print(f"  orthogonal: g1_proj={out[0].tolist()} g2_proj={out[1].tolist()} (unchanged)",
          flush=True)

    # Test 3: positive-cos -> unchanged
    g1 = torch.tensor([1.0, 0.5])
    g2 = torch.tensor([0.5, 1.0])
    out = proj.project([g1, g2])
    assert torch.allclose(out[0], g1, atol=1e-6), f"positive-cos g1 changed: {out[0]}"
    assert torch.allclose(out[1], g2, atol=1e-6), f"positive-cos g2 changed: {out[1]}"
    print(f"  positive-cos: unchanged (positive-cos pair)", flush=True)

    # Test 4: K=4 mix
    grads = [
        torch.tensor([1.0, 0.0, 0.0]),   # x-axis
        torch.tensor([-1.0, 0.0, 0.0]),  # anti-x
        torch.tensor([0.0, 1.0, 0.0]),   # y-axis (orth)
        torch.tensor([0.5, 0.5, 0.0]),   # mixed
    ]
    out = proj.project(grads)
    assert all(torch.isfinite(g).all().item() for g in out), "K=4 produced nan"
    print(f"  K=4 mix: out_norms={[g.norm().item() for g in out]}", flush=True)

    # Test 5: parameter-list interface (3 grads, 2 params each)
    pc = PCGradProjector(shuffle=False)
    g_per_chan = [
        [torch.tensor([1.0, 2.0]), torch.tensor([[3.0, 4.0], [5.0, 6.0]])],
        [torch.tensor([-1.0, -2.0]), torch.tensor([[-3.0, -4.0], [-5.0, -6.0]])],
        [torch.tensor([0.1, 0.2]), torch.tensor([[0.3, 0.4], [0.5, 0.6]])],
    ]
    out_chan = apply_pcgrad_to_param_lists(g_per_chan, pc)
    assert len(out_chan) == 3 and all(len(c) == 2 for c in out_chan), "param-list shape wrong"
    # Anti-parallel pair should collapse to ~zero
    pair0_norm = out_chan[0][0].norm().item() + out_chan[0][1].norm().item()
    print(f"  param-list K=3: chan0 norm={pair0_norm:.6f} (anti-parallel partner should collapse)",
          flush=True)
    assert pair0_norm < 0.5, f"anti-parallel partner not collapsed: {pair0_norm}"

    print("[selftest pcgrad] PASS", flush=True)


if __name__ == "__main__":
    _selftest()
