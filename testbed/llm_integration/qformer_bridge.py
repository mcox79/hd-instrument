"""Q-Former cross-attention bridge (replaces 2-layer MLP per parent handoff).

Per `notes/routed_completed/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`
sec "Revised Deviation 1": Q-Former-style cross-attention bridge with
8-16 learnable query tokens per substrate codeword.

Architecture (smoke version, minimal viable for Phase 1 wiring test):
  - 8 learnable query tokens of dim d_model=3072
  - Single cross-attention block: queries=learnable; K,V=substrate codeword
    after linear embedding (bipolar {-1,+1}^4096 -> continuous R^4096 -> R^3072)
  - Output: 8 prefix tokens in R^3072 (one per query slot)
  - GELU + LayerNorm post-attention
  - ~30M params target

The query-readout head (separate module) converts an LLM hidden state at
the [QUERY] position to a bipolar codeword for substrate query emission.
Together: Q-Former bridge + query-readout head = the full bidirectional bridge.

Per parent handoff sec "Revised Codebook representation":
  - NEVER binarize inside the bridge during training (avoids spec'd-tanh
    train-test gap)
  - Q-Former queries are continuous; substrate keys can be bipolar without
    internal binarization since the linear embedding handles it
  - sign() only at deployment-time codeword EMISSION (query-readout head exit)

Smoke-test (`python qformer_bridge.py`): builds both modules at default
sizes, runs a synthetic forward+backward, asserts shapes + no-NaN + gradient
flow.
"""

from __future__ import annotations

import sys
from typing import Optional

import torch
from torch import nn


_N_SUBSTRATE = 4096    # substrate codeword dimensionality
_D_MODEL = 3072        # Phi-3-mini-3.8B hidden dim
_N_QUERIES = 8         # learnable query tokens per codeword
_N_HEADS = 8           # multi-head attention; d_head = d_model / n_heads
_FF_HIDDEN = 2048      # feed-forward inner dim


class CodewordEmbedder(nn.Module):
    """Map bipolar {-1, +1}^N substrate codeword to continuous R^d_model.

    Single linear layer N -> d_model. The bipolar -> continuous transition
    happens at this layer's input: no internal binarization elsewhere.
    """

    def __init__(self, n_sub: int = _N_SUBSTRATE, d_model: int = _D_MODEL):
        super().__init__()
        self.proj = nn.Linear(n_sub, d_model)

    def forward(self, codeword: torch.Tensor) -> torch.Tensor:
        # codeword: (..., n_sub) float; can be bipolar {-1,+1} or continuous tanh
        return self.proj(codeword)


class QFormerBridge(nn.Module):
    """Q-Former cross-attention bridge: substrate codeword -> 8 prefix tokens.

    Forward input: substrate codeword (B, n_sub) bipolar or continuous
    Forward output: prefix tokens (B, n_queries, d_model)

    Pipeline:
      1. CodewordEmbedder maps (B, n_sub) -> (B, d_model)
      2. Reshape to (B, 1, d_model) so it can act as a 1-token sequence of
         K/V for cross-attention
      3. Learnable queries (n_queries, d_model) broadcast to (B, n_queries, d_model)
      4. Cross-attention: queries attend to the 1-token codeword K/V
      5. Residual + LayerNorm + FFN + Residual + LayerNorm
      6. Return (B, n_queries, d_model) prefix tokens

    The 1-token K/V might feel degenerate but it's the standard pattern when
    "the visual feature" is a single dense vector (BLIP-2's image features
    after pooling). When we later route per-hop codewords from Path D depth=5,
    we'll concatenate to (B, 5, d_model) K/V instead.
    """

    def __init__(
        self,
        n_sub: int = _N_SUBSTRATE,
        d_model: int = _D_MODEL,
        n_queries: int = _N_QUERIES,
        n_heads: int = _N_HEADS,
        ff_hidden: int = _FF_HIDDEN,
    ):
        super().__init__()
        self.n_queries = n_queries
        self.d_model = d_model
        # Learnable query tokens
        self.queries = nn.Parameter(torch.randn(n_queries, d_model) * 0.02)
        # Codeword -> d_model embedding
        self.cw_embed = CodewordEmbedder(n_sub, d_model)
        # Cross-attention
        self.cross_attn = nn.MultiheadAttention(
            embed_dim=d_model, num_heads=n_heads, batch_first=True,
        )
        # Post-attention norm + FFN
        self.norm1 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, ff_hidden),
            nn.GELU(),
            nn.Linear(ff_hidden, d_model),
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, codeword: torch.Tensor) -> torch.Tensor:
        # codeword: (B, n_sub) -> kv: (B, 1, d_model)
        kv = self.cw_embed(codeword).unsqueeze(1)
        B = kv.shape[0]
        # queries: (n_q, d_model) -> (B, n_q, d_model)
        q = self.queries.unsqueeze(0).expand(B, -1, -1)
        attn_out, _ = self.cross_attn(q, kv, kv)
        h = self.norm1(q + attn_out)
        h = self.norm2(h + self.ffn(h))
        # Output: (B, n_q, d_model)
        return h


class QueryReadoutHead(nn.Module):
    """LLM hidden state R^d_model -> bipolar substrate query R^n_sub.

    Training: tanh-activated output (continuous-relaxed; gradient-friendly).
    Inference: sign() applied OUTSIDE this module at deployment time.

    Single 2-layer projection: d_model -> hidden -> n_sub, GELU activation.
    No internal binarization.
    """

    def __init__(
        self,
        d_model: int = _D_MODEL,
        n_sub: int = _N_SUBSTRATE,
        d_hidden: int = 2048,
    ):
        super().__init__()
        self.fc1 = nn.Linear(d_model, d_hidden)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(d_hidden, n_sub)

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        # hidden: (..., d_model) -> (..., n_sub) tanh-bounded
        return torch.tanh(self.fc2(self.act(self.fc1(hidden))))


def smoke_test(device: Optional[torch.device] = None) -> dict:
    """Build both modules, run synthetic forward+backward, return diagnostics.

    Acceptance criteria per orchestrator handoff
    `notes/testbed_handoff_pp8_week2_feasibility_smoke_authorized_2026-06-01.md`
    Phase 1:
      - Forward pass produces non-garbage substrate query (Hamming distance
        to expected target < threshold) -- AT SMOKE, untrained, expect ~N/2
        random; shape + no-NaN is the load-bearing check
      - Backward pass produces non-zero gradient through bridge (training will
        at least move)
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(7)

    bridge = QFormerBridge().to(device)
    readout = QueryReadoutHead().to(device)
    print(f"[qformer_smoke] device={device}")
    print(f"[qformer_smoke] bridge params: "
          f"{sum(p.numel() for p in bridge.parameters()) / 1e6:.2f}M")
    print(f"[qformer_smoke] readout params: "
          f"{sum(p.numel() for p in readout.parameters()) / 1e6:.2f}M")
    print(f"[qformer_smoke] combined: "
          f"{(sum(p.numel() for p in bridge.parameters()) + sum(p.numel() for p in readout.parameters())) / 1e6:.2f}M")

    # ---- Forward smoke: substrate result -> Q-Former -> prefix tokens ----
    B = 4
    fake_codeword = torch.sign(torch.randn(B, _N_SUBSTRATE, device=device))
    fake_codeword[fake_codeword == 0] = 1
    prefix = bridge(fake_codeword)
    assert prefix.shape == (B, _N_QUERIES, _D_MODEL), \
        f"prefix shape: got {prefix.shape}; want ({B}, {_N_QUERIES}, {_D_MODEL})"
    assert not torch.isnan(prefix).any(), "prefix has NaN"
    assert not torch.isinf(prefix).any(), "prefix has Inf"
    print(f"[qformer_smoke] FORWARD bridge: shape OK ({tuple(prefix.shape)}), "
          f"no NaN/Inf, mean={prefix.mean().item():.4f} "
          f"std={prefix.std().item():.4f}")

    # ---- Forward smoke: LLM hidden -> readout -> bipolar query ----
    fake_hidden = torch.randn(B, _D_MODEL, device=device)
    query = readout(fake_hidden)
    assert query.shape == (B, _N_SUBSTRATE)
    assert not torch.isnan(query).any()
    assert (query.abs() <= 1.0 + 1e-5).all(), "tanh output should be in [-1, 1]"
    bipolar = torch.sign(query)
    bipolar[bipolar == 0] = 1
    # Hamming distance to a random target (untrained -> expect ~N/2)
    target = torch.sign(torch.randn(B, _N_SUBSTRATE, device=device))
    target[target == 0] = 1
    hamming = (bipolar != target).float().mean(dim=-1).mean().item() * _N_SUBSTRATE
    print(f"[qformer_smoke] FORWARD readout: shape OK, tanh-bounded, "
          f"hamming-to-random={hamming:.1f}/{_N_SUBSTRATE} "
          f"(~50pct expected untrained)")

    # ---- Backward smoke: synthetic MSE loss, check gradient flow ----
    bridge.zero_grad()
    readout.zero_grad()
    # End-to-end: hidden -> readout -> tanh-query -> as-if-codeword -> bridge -> prefix
    # Use the tanh output AS the bridge input (treating it as continuous-relaxed
    # codeword), which is exactly the train-time pattern per parent handoff:
    # "NEVER binarize inside the bridge during training".
    hidden = torch.randn(B, _D_MODEL, device=device, requires_grad=False)
    soft_query = readout(hidden)
    end_to_end_prefix = bridge(soft_query)
    loss = end_to_end_prefix.pow(2).mean()
    loss.backward()
    # Verify gradient flow through ALL parameter groups
    grads_ok = []
    for name, module in [("bridge", bridge), ("readout", readout)]:
        for p_name, p in module.named_parameters():
            if p.grad is None:
                grads_ok.append((f"{name}.{p_name}", "NO GRAD"))
            elif p.grad.abs().max().item() == 0:
                grads_ok.append((f"{name}.{p_name}", "ZERO GRAD"))
            elif torch.isnan(p.grad).any():
                grads_ok.append((f"{name}.{p_name}", "NaN GRAD"))
    if grads_ok:
        print(f"[qformer_smoke] BACKWARD FAIL: {len(grads_ok)} bad-grad params:")
        for n, w in grads_ok[:8]:
            print(f"  {n}: {w}")
        raise RuntimeError("backward smoke: some params have no/zero/NaN gradient")
    print(f"[qformer_smoke] BACKWARD: all {sum(1 for _ in bridge.parameters())} "
          f"bridge params + all {sum(1 for _ in readout.parameters())} readout "
          f"params have finite non-zero gradient")
    print(f"[qformer_smoke] loss value: {loss.item():.6f}")

    return {
        "device": str(device),
        "bridge_params_M": round(sum(p.numel() for p in bridge.parameters()) / 1e6, 2),
        "readout_params_M": round(sum(p.numel() for p in readout.parameters()) / 1e6, 2),
        "bridge_forward_ok": True,
        "readout_forward_ok": True,
        "hamming_to_random": round(hamming, 1),
        "backward_ok": True,
        "loss_value": round(loss.item(), 6),
    }


if __name__ == "__main__":
    import json
    result = smoke_test()
    print()
    print("=== qformer_smoke result ===")
    print(json.dumps(result, indent=2))
    sys.exit(0)
