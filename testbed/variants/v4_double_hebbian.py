"""Substrate v4: double Hebbian write (cyclic-shifted redundancy).

Hypothesis: At high M / N (above-capacity regime), point recall degrades
because the cross-talk noise floor on retrieve grows like sqrt(M/N).
Adding a second redundant outer-product, anchored on a deterministically
shifted partner atom for the same logical key, may raise the signal-to-
noise margin at retrieve time without changing the codebook geometry.

Mechanism on store:
    W += outer(val_atom, key_atom) / N
    W += outer(val_atom_shift, key_atom_shift) / N
where shift = next codebook row cyclically (row + 1) mod C for both
the key and the value. edit() and delete() mirror the store() shape so
the redundancy is undone exactly. retrieve() is unchanged: it still
snaps to the nearest atom and reads via softmax, so the second copy
acts purely as a noise-margin amplifier.

Caveat: This doubles the effective fan-out of each write into the
codebook. It will degrade KF-1 hallucination guarantees (more atoms
are tied into any one write) and will burn through codebook capacity
twice as fast. Suitable for testing the recall / hallucination
tradeoff but not a free win.

Override surface: store, edit, delete. retrieve and audit inherited.
"""

from __future__ import annotations

import time

import numpy as np
import torch

from testbed.api import DeletionCertificate
from testbed.substrate_memory import SubstrateMemory, _stable_hash_int


class SubstrateV4DoubleHebbian(SubstrateMemory):
    """Dual outer-product writes for redundancy under high M/N."""

    name = "substrate_v4_double_hebbian"

    def _shift_row(self, row: int) -> int:
        return (int(row) + 1) % self.C

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        if key_id in self.key_registry:
            self.edit(key_id, value)
            return

        key_row = self._atom_for_key_id(key_id, key_vec)
        val_row = self._atom_for_value(key_id, value)

        key_atom = self.codebook[key_row]
        val_atom = self.codebook[val_row]

        # Primary Hebbian write.
        self.W = self.W + torch.outer(val_atom, key_atom) / self.N

        # Secondary cyclic-shifted Hebbian write.
        key_atom_s = self.codebook[self._shift_row(key_row)]
        val_atom_s = self.codebook[self._shift_row(val_row)]
        self.W = self.W + torch.outer(val_atom_s, key_atom_s) / self.N

        self.key_registry[key_id] = key_row
        self.value_registry[key_id] = value
        self.value_atom_registry[key_id] = val_row
        self._insertion_order.append(key_id)

    def edit(self, key_id: str, new_value: str) -> None:
        if key_id not in self.key_registry:
            raise KeyError(f"unknown key_id: {key_id}")
        key_row = self.key_registry[key_id]
        old_val_row = self.value_atom_registry[key_id]
        new_val_row = self._atom_for_value(key_id, new_value)

        key_atom = self.codebook[key_row]
        old_atom = self.codebook[old_val_row]
        new_atom = self.codebook[new_val_row]
        key_atom_s = self.codebook[self._shift_row(key_row)]
        old_atom_s = self.codebook[self._shift_row(old_val_row)]
        new_atom_s = self.codebook[self._shift_row(new_val_row)]

        self.W = self.W - torch.outer(old_atom, key_atom) / self.N
        self.W = self.W + torch.outer(new_atom, key_atom) / self.N
        self.W = self.W - torch.outer(old_atom_s, key_atom_s) / self.N
        self.W = self.W + torch.outer(new_atom_s, key_atom_s) / self.N

        self.value_registry[key_id] = new_value
        self.value_atom_registry[key_id] = new_val_row

    def delete(self, key_id: str) -> DeletionCertificate:
        if key_id not in self.key_registry:
            raise KeyError(f"unknown key_id: {key_id}")
        key_row = self.key_registry[key_id]
        val_row = self.value_atom_registry[key_id]
        key_atom = self.codebook[key_row]
        val_atom = self.codebook[val_row]
        key_atom_s = self.codebook[self._shift_row(key_row)]
        val_atom_s = self.codebook[self._shift_row(val_row)]

        resp_pre = self.W @ key_atom
        var_pre = float(torch.var(resp_pre).item())

        # Mirror the double write on erase.
        self.W = self.W - torch.outer(val_atom, key_atom) / self.N
        self.W = self.W - torch.outer(val_atom_s, key_atom_s) / self.N

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
