"""Codebook builders for SubstrateMemory.

Three families:
  bsc      - random plus/minus 1, any N, any C
  kerdock  - structured 4-coset MM construction, requires log2(N) even
  gaussian - random N(0, 1/sqrt(N)), any N, any C

Each builder returns a torch.Tensor of shape (C, N), float32.
The dispatcher get_codebook(kind, N, C, seed) selects the builder.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent


def _build_bsc(N: int, C: int, seed: int = 0) -> torch.Tensor:
    """Random plus/minus 1 codebook of shape (C, N), float32.

    Matches make_bsc_codebook in experiments/exp_kf1_hallu_rescue_v4_n8192_bsc.py.
    Seed is offset by 999999 to match the historical convention there.
    """
    gen = torch.Generator(device="cpu").manual_seed(seed + 999999)
    raw = torch.randint(0, 2, (C, N), generator=gen).float() * 2.0 - 1.0
    return raw


def _build_kerdock(N: int, seed: int = 0) -> torch.Tensor:
    """Kerdock 4-coset MM codebook, shape (4N, N), float32.

    Raises ValueError if log2(N) is odd. Wraps make_kerdock_4coset_codebook from
    experiments/exp_wave14y_erase_kerdock_v3.py. Seed is unused (construction is
    deterministic given N).
    """
    n_log2 = int(round(math.log2(N)))
    if 2 ** n_log2 != N:
        raise ValueError(f"Kerdock requires N power of 2; got N={N}")
    if n_log2 % 2 != 0:
        raise ValueError(
            f"Kerdock requires log2(N) even; got N={N} (log2={n_log2})"
        )

    v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
    if not v3_path.exists():
        raise RuntimeError(f"Kerdock builder source not found: {v3_path}")
    spec = importlib.util.spec_from_file_location("kerdock_v3_testbed", v3_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    device = torch.device("cpu")
    cb, _info = mod.make_kerdock_4coset_codebook(N, device)
    return cb.float()


def _build_gaussian(N: int, C: int, seed: int = 0) -> torch.Tensor:
    """Random N(0, 1/sqrt(N)) codebook of shape (C, N), float32."""
    gen = torch.Generator(device="cpu").manual_seed(seed + 999999)
    raw = torch.randn(C, N, generator=gen) / math.sqrt(N)
    return raw.float()


def get_codebook(kind: str, N: int, C: int, seed: int = 0) -> torch.Tensor:
    """Dispatch to the named codebook builder.

    kind in {bsc, kerdock, gaussian}. For Kerdock, C is ignored (always 4N).
    """
    if kind == "bsc":
        return _build_bsc(N, C, seed)
    if kind == "kerdock":
        return _build_kerdock(N, seed)
    if kind == "gaussian":
        return _build_gaussian(N, C, seed)
    raise ValueError(
        f"unknown codebook kind: {kind!r} (expected bsc, kerdock, gaussian)"
    )


if __name__ == "__main__":
    # Self-test: each builder produces the expected shape.
    for kind, N, C in [("bsc", 128, 512), ("gaussian", 128, 512)]:
        cb = get_codebook(kind, N, C, seed=7)
        assert cb.shape == (C, N), f"{kind} shape {cb.shape}"
        assert cb.dtype == torch.float32, f"{kind} dtype {cb.dtype}"
    # Kerdock requires log2(N) even AND primitive poly registered (t in {5,6,7}).
    try:
        _build_kerdock(N=512, seed=0)
        raise AssertionError("Kerdock log2(N)=9 odd should have raised")
    except ValueError:
        pass
    # Smallest registered Kerdock N: t=5 -> N=2^10=1024.
    cb_k = _build_kerdock(N=1024, seed=0)
    assert cb_k.shape == (4 * 1024, 1024), f"kerdock shape {cb_k.shape}"
    print("codebooks self-test OK")
