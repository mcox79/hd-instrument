"""Substrate v3: Kerdock-structured codebook.

Hypothesis: The Kerdock 4-coset MM codebook has near-optimal pairwise
inner-product bounds (Welch bound regime). Better isolation between atoms
should improve KF-2 max_isolation under edits and TCFT var_ratio under
deletes, with no penalty to point recall.

Constraint: Kerdock requires log2(N) to be EVEN. We do not crash at odd
log2(N); instead we degrade to a BSC codebook and emit a single-line
warning on stderr. This keeps smoke tests (which default to N=512,
log2=9 odd) green while still exercising the variant subclass machinery.

Override surface: __init__ only. Every other operation is inherited.
"""

from __future__ import annotations

import math
import sys

from testbed.substrate_memory import SubstrateMemory


class SubstrateV3Kerdock(SubstrateMemory):
    """Kerdock codebook variant; falls back to BSC at odd log2(N)."""

    name = "substrate_v3_kerdock"

    def __init__(
        self,
        N: int = 4096,
        codebook_kind: str = "kerdock",
        codebook_scale: int = 4,
        beta: float = 32.0,
        hallu_threshold: float = 0.5,
        device: str = "cpu",
        seed: int = 0,
    ) -> None:
        # Guard rail: Kerdock construction needs N a power of 2 with even
        # log2. Degrade to BSC otherwise so smoke (N=512) does not crash.
        kind = codebook_kind
        if kind == "kerdock":
            n_log2 = int(round(math.log2(N))) if N > 0 else -1
            is_pow2 = (N > 0) and (2 ** n_log2 == N)
            if not is_pow2 or (n_log2 % 2 != 0):
                print(
                    f"[v3_kerdock] WARNING: log2(N={N}) not even; "
                    "falling back to BSC codebook.",
                    file=sys.stderr,
                )
                kind = "bsc"

        super().__init__(
            N=N,
            codebook_kind=kind,
            codebook_scale=codebook_scale,
            beta=beta,
            hallu_threshold=hallu_threshold,
            device=device,
            seed=seed,
        )
