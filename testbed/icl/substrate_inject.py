"""SubstrateInjector: residual-stream forward-hook for substrate retrieval.

Used by Probe 2 (substrate-pre-loaded ICL) to inject `alpha * retrieval` into
the hidden state output of a chosen transformer layer.  The retrieval is
computed per-query as `retrieval = sign(W @ xi_q)` and then optionally
projected from substrate-dim N to model-dim D via a fixed Rademacher matrix.

Usage:

    inj = SubstrateInjector(model.gpt_neox.layers[17], W=W, N=1024,
                            d_model=1024, alpha=0.1, proj_seed=2026)
    with inj:                              # registers the hook
        for q in queries:
            xi_q = encode_text_bipolar(q, N=1024, proj_seed=1729)
            inj.set_query(xi_q)
            out = model.generate(...)      # hook fires, adds alpha*retrieval

When N == d_model, the projection is the identity (efficient, no allocation).
When N != d_model, a fixed Rademacher matrix N -> d_model is built once and
reused.

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

try:
    import torch
    _HAS_TORCH = True
except ImportError:
    torch = None  # type: ignore
    _HAS_TORCH = False


class SubstrateInjector:
    """Forward-hook context manager that adds a substrate-retrieval term to
    a transformer layer's hidden state output.

    Args:
        layer:    The target nn.Module (e.g., model.gpt_neox.layers[17]).
        W:        (N, N) substrate matrix (numpy float32).
        N:        Substrate dimensionality.
        d_model:  Transformer hidden dim.  If equal to N, projection is identity.
        alpha:    Injection strength scalar.
        proj_seed:Seed for the N -> d_model projection (only used if N != d_model).
        device:   Torch device for the cached retrieval tensor.
        dtype:    Torch dtype for the injected tensor (default: match hidden).

    If `layer` is None (smoke / mock testing), the injector is INERT but still
    tracks set_query / __enter__ / __exit__ so plumbing tests can run.
    """

    def __init__(self, layer, W: np.ndarray, N: int, d_model: int,
                 alpha: float = 0.1, proj_seed: int = 2026,
                 device: str = "cpu", dtype: Optional[object] = None) -> None:
        self.layer = layer
        self.W = np.asarray(W, dtype=np.float32)
        assert self.W.shape == (N, N), f"W shape mismatch: {self.W.shape} vs ({N},{N})"
        self.N = int(N)
        self.d_model = int(d_model)
        self.alpha = float(alpha)
        self.device = device
        self.dtype = dtype

        # Build (or skip) projection N -> d_model
        if self.N == self.d_model:
            self._proj: Optional[np.ndarray] = None  # identity
        else:
            rng = np.random.default_rng(int(proj_seed))
            # Rademacher projection / sqrt(N) for variance control
            self._proj = (rng.choice([-1, 1], size=(self.N, self.d_model))
                          .astype(np.float32)) / float(np.sqrt(self.N))

        # Current query retrieval (cached as tensor when torch is present)
        self._retrieval_np: Optional[np.ndarray] = None
        self._retrieval_t: Optional[object] = None  # torch.Tensor when torch

        # Hook handle
        self._handle = None

        # Bookkeeping
        self.n_fires: int = 0
        self.enabled: bool = False

    # ------------------------------------------------------------------ API
    def set_query(self, xi_q: np.ndarray) -> None:
        """Update the substrate query vector.  Computes retrieval = sign(W @ xi_q)
        and projects to d_model.  Subsequent forward passes through the hooked
        layer will receive alpha * retrieval added to the hidden state.
        """
        assert xi_q.shape == (self.N,), f"xi_q shape: {xi_q.shape}"
        # retrieval in N-space
        r = self.W @ xi_q.astype(np.float32)
        # Sign-normalize (matches Hopfield-style readout).  We also keep a soft
        # version (just r) on a side path; tests + experiments use the sign.
        r_sign = np.sign(r).astype(np.float32)
        # Project to d_model
        if self._proj is None:
            r_d = r_sign  # identity
        else:
            r_d = r_sign @ self._proj  # (d_model,)
        self._retrieval_np = r_d
        if _HAS_TORCH and torch is not None:
            self._retrieval_t = torch.from_numpy(r_d.astype(np.float32)).to(self.device)
        else:
            self._retrieval_t = None

    def clear_query(self) -> None:
        """Drop the current retrieval -- next forward will inject nothing."""
        self._retrieval_np = None
        self._retrieval_t = None

    # ------------------------------------------------------------------ hook
    def _hook_fn(self, module, inputs, output):
        """Forward hook: add alpha * retrieval to the layer's hidden state.

        Transformer layers in HF typically return either a Tensor or a tuple
        (hidden, ...).  We add to the first element.

        Broadcasts retrieval (d_model,) across batch and sequence dims.
        """
        if self._retrieval_t is None and self._retrieval_np is None:
            return output  # no-op
        self.n_fires += 1

        # Resolve hidden tensor
        if isinstance(output, tuple):
            h = output[0]
            rest = output[1:]
            return_tuple = True
        else:
            h = output
            rest = None
            return_tuple = False

        if _HAS_TORCH and torch is not None and isinstance(h, torch.Tensor):
            # Build injection tensor with matching dtype/device
            ret = self._retrieval_t
            if ret is None:
                ret = torch.from_numpy(self._retrieval_np.astype(np.float32)).to(h.device)
            else:
                ret = ret.to(h.device)
            ret = ret.to(h.dtype)
            # Broadcast: ret shape (d_model,); h shape (..., d_model)
            h_new = h + self.alpha * ret
            if return_tuple:
                return (h_new,) + rest
            return h_new

        # Numpy / mock-module path: assume output is ndarray with last dim = d_model
        if isinstance(h, np.ndarray):
            ret = self._retrieval_np
            h_new = h + self.alpha * ret.astype(h.dtype)
            if return_tuple:
                return (h_new,) + rest
            return h_new

        # Unknown output type -- pass through (no-op)
        return output

    # ------------------------------------------------------------------ ctx
    def __enter__(self):
        if self.layer is None:
            self.enabled = True
            return self
        # Register the hook
        if hasattr(self.layer, "register_forward_hook"):
            self._handle = self.layer.register_forward_hook(self._hook_fn)
        else:
            # Mock layer that exposes a `forward_hooks` list (for tests)
            if not hasattr(self.layer, "_inj_hooks"):
                self.layer._inj_hooks = []
            self.layer._inj_hooks.append(self._hook_fn)
            self._handle = ("mock", self._hook_fn)
        self.enabled = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._handle is not None:
            if isinstance(self._handle, tuple) and self._handle[0] == "mock":
                # Mock cleanup
                self.layer._inj_hooks.remove(self._handle[1])
            else:
                self._handle.remove()
        self._handle = None
        self.enabled = False
        return False


# -----------------------------------------------------------------------------
# Self-test
# -----------------------------------------------------------------------------
def _selftest() -> None:
    """PROT-022: hook attach/detach mechanics + injection math correctness."""
    print("[selftest] testbed.icl.substrate_inject")

    # T1: N == d_model identity projection
    N = 32
    rng = np.random.default_rng(0)
    Xi = rng.choice([-1.0, 1.0], size=(5, N)).astype(np.float32)
    W = (Xi.T @ Xi) / float(N)
    inj = SubstrateInjector(layer=None, W=W, N=N, d_model=N, alpha=0.5)
    inj.set_query(Xi[0])
    assert inj._proj is None, "identity projection should be None"
    assert inj._retrieval_np is not None and inj._retrieval_np.shape == (N,)
    print("  T1 PASS: identity projection, retrieval shape OK")

    # T2: N != d_model -> Rademacher projection
    inj2 = SubstrateInjector(layer=None, W=W, N=N, d_model=16, alpha=0.5)
    inj2.set_query(Xi[0])
    assert inj2._proj is not None and inj2._proj.shape == (N, 16)
    assert inj2._retrieval_np.shape == (16,)
    print("  T2 PASS: projection N=32 -> d_model=16, shapes OK")

    # T3: clear_query nulls retrieval
    inj.clear_query()
    assert inj._retrieval_np is None
    print("  T3 PASS: clear_query nulls retrieval")

    # T4: torch path with a tiny nn.Module forward hook
    if _HAS_TORCH:
        import torch.nn as nn

        class TinyLayer(nn.Module):
            def __init__(self, d):
                super().__init__()
                self.lin = nn.Linear(d, d)

            def forward(self, x):
                return self.lin(x)

        d = N
        layer = TinyLayer(d)
        # Zero out linear so we can read out injection cleanly
        with torch.no_grad():
            layer.lin.weight.zero_()
            layer.lin.bias.zero_()

        inj3 = SubstrateInjector(layer=layer, W=W, N=N, d_model=d, alpha=1.0)
        inj3.set_query(Xi[2])
        x = torch.zeros(1, d)
        with inj3:
            y_inj = layer(x).detach().numpy()
        y_no_inj = layer(x).detach().numpy()  # hook removed on exit

        # With injection: should equal alpha * retrieval (since lin produces zero)
        retr = inj3._retrieval_np
        assert np.allclose(y_inj.squeeze(0), retr, atol=1e-5), \
            f"injected output mismatch: {y_inj.squeeze(0)[:5]} vs {retr[:5]}"
        # Without injection: zero
        assert np.allclose(y_no_inj, 0.0, atol=1e-5), \
            f"hook leaked after __exit__: {y_no_inj}"
        assert inj3.n_fires == 1, f"n_fires: {inj3.n_fires}"
        print("  T4 PASS: torch nn.Module hook fires, math correct, detaches on __exit__")

        # T5: hook re-attach + multiple fires
        inj4 = SubstrateInjector(layer=layer, W=W, N=N, d_model=d, alpha=0.1)
        with inj4:
            for k in range(3):
                inj4.set_query(Xi[k % 5])
                _ = layer(x)
        assert inj4.n_fires == 3, f"n_fires multi: {inj4.n_fires}"
        print("  T5 PASS: 3 forward passes -> 3 hook fires, detach clean")
    else:
        print("  T4-T5 SKIP: torch unavailable")

    # T6: tuple output path (mock module that returns a 2-tuple)
    class MockTupleLayer:
        def register_forward_hook(self, fn):
            self._h = fn
            class H:
                def __init__(self, owner):
                    self.owner = owner
                def remove(self):
                    self.owner._h = None
            return H(self)

        def fire(self, x_np):
            out = (x_np.copy(), {"meta": "ok"})
            return self._h(self, None, out)

    mock = MockTupleLayer()
    inj5 = SubstrateInjector(layer=mock, W=W, N=N, d_model=N, alpha=0.25)
    inj5.set_query(Xi[1])
    with inj5:
        x = np.zeros((1, N), dtype=np.float32)
        out = mock.fire(x)
    assert isinstance(out, tuple) and len(out) == 2 and out[1] == {"meta": "ok"}
    assert np.allclose(out[0].squeeze(0), 0.25 * inj5._retrieval_np, atol=1e-5)
    assert mock._h is None, "mock hook did not detach"
    print("  T6 PASS: tuple-output layer; injection on element 0; rest preserved; detach OK")

    print("[selftest] testbed.icl.substrate_inject ALL PASS")


_selftest()


if __name__ == "__main__":
    _selftest()
