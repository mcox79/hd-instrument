"""Substrate v2: soft anti-Hebbian iterative erase.

Hypothesis: Performing one full outer-product subtract (alpha=1.0) on
delete() can over-shoot when the stored value atom has acquired
cross-talk from other writes. A softer scaling (alpha=0.5) repeated
across a few corrective iterations may shrink the key-direction variance
more effectively (better TCFT var_ratio) at the cost of some structural
erase noise on neighbouring keys.

Mechanism:
  for step in range(N_STEPS):
      W -= alpha * outer(value_atom, key_atom) / N
  where alpha=0.5 and N_STEPS=3.

This is mathematically equivalent to a 1 - (1 - alpha)^N_STEPS = 0.875
fractional subtract IF the value atom is unchanged; in practice the
intermediate W after each step is what feeds back into the next
correction's reading of the residual, so the trajectory is non-trivial
when cross-talk is present.

Override surface: delete() only. Every other operation is inherited.
"""

from __future__ import annotations

import time

import torch

from testbed.api import DeletionCertificate
from testbed.substrate_memory import SubstrateMemory, _stable_hash_int


class SubstrateV2Softdelete(SubstrateMemory):
    """Soft iterative-erase delete; v1 in every other respect."""

    name = "substrate_v2_softdelete"

    # Tunable softdelete parameters. Override at subclass time if needed.
    SOFT_ALPHA = 0.5
    SOFT_STEPS = 3

    def delete(self, key_id: str) -> DeletionCertificate:
        if key_id not in self.key_registry:
            raise KeyError(f"unknown key_id: {key_id}")
        key_row = self.key_registry[key_id]
        val_row = self.value_atom_registry[key_id]
        key_atom = self.codebook[key_row]
        val_atom = self.codebook[val_row]

        # Pre-delete projection variance (key direction).
        resp_pre = self.W @ key_atom
        var_pre = float(torch.var(resp_pre).item())

        # Iterative soft erase: SOFT_STEPS subtracts each of size
        # SOFT_ALPHA * outer(val_atom, key_atom) / N.
        scale = self.SOFT_ALPHA / self.N
        for _ in range(self.SOFT_STEPS):
            self.W = self.W - scale * torch.outer(val_atom, key_atom)

        # Post-delete projections.
        rng_row = _stable_hash_int("delete_rng:" + key_id) % self.C
        random_atom = self.codebook[rng_row]
        resp_key = self.W @ key_atom
        resp_rng = self.W @ random_atom
        var_key_post = float(torch.var(resp_key).item())
        var_rng_post = float(torch.var(resp_rng).item())

        shrinkage = var_key_post / (var_pre + 1e-300)
        key_vs_rng = var_key_post / (var_rng_post + 1e-300)
        var_ratio = min(shrinkage, key_vs_rng)

        del self.key_registry[key_id]
        self.value_registry.pop(key_id)
        del self.value_atom_registry[key_id]
        try:
            self._insertion_order.remove(key_id)
        except ValueError:
            pass

        key_vec_np = key_atom.detach().cpu().numpy()
        result = self.retrieve(key_vec_np)
        erased = result.key_id != key_id

        return DeletionCertificate(
            key_id=key_id,
            var_ratio=float(var_ratio),
            erased=bool(erased),
            timestamp_ns=time.time_ns(),
        )
