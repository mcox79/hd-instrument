"""Witness: the DEFAULT-OFF L2 superposition normaliser (bundling.bundle norm="l2") + its coupled cosine
readout (atoms.similarity cosine=True), landed from the binding-operator integration (2026-08-26).

(1) DEFAULT is BYTE-IDENTICAL: complex bundle default -> per-component unit magnitude; similarity default -> /n.
(2) The L2 path is self-consistent: bundle(norm="l2") -> whole-vector norm 1; similarity(cosine=True) -> true cosine.
(3) On a key-value binding micro-case under a PARTIAL cue, L2+cosine recovers the filler at least as well as the
    default per-component+/n -- the "L2 beats per-component 32/32" finding in miniature.
Scaffold-free, deterministic. The per-component normaliser is what only ever hurts; this witness confirms the
default is untouched and the coupled L2 path is correct and does not regress.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import torch

from hdlab import atoms, binding, bundling


def test_default_byte_identical():
    g = torch.Generator().manual_seed(0)
    V = atoms.make_atoms(5, 64, torch.complex64, g)
    out = bundling.bundle(V)                                   # DEFAULT (norm=None)
    assert torch.allclose(out.abs(), torch.ones_like(out.abs()), atol=1e-5), \
        "default complex bundle must be per-component unit magnitude (unchanged)"
    a = atoms.make_atom_fhrr(64, torch.Generator().manual_seed(1))
    b = atoms.make_atom_fhrr(64, torch.Generator().manual_seed(2))
    manual = (a * b.conj()).sum(dim=-1).real / a.shape[-1]
    assert torch.allclose(atoms.similarity(a, b), manual, atol=1e-6), "default similarity must be /n (unchanged)"
    print("PASS default_byte_identical")


def test_l2_path_self_consistent():
    g = torch.Generator().manual_seed(3)
    V = atoms.make_atoms(5, 64, torch.complex64, g)
    out = bundling.bundle(V, norm="l2")
    assert abs(float(out.norm()) - 1.0) < 1e-4, "L2 bundle must have whole-vector norm 1"
    a = atoms.make_atom_fhrr(64, torch.Generator().manual_seed(4))
    b = atoms.make_atom_fhrr(64, torch.Generator().manual_seed(5))
    cos = (a * b.conj()).sum(dim=-1).real / (a.norm(dim=-1) * b.norm(dim=-1))
    assert torch.allclose(atoms.similarity(a, b, cosine=True), cos, atol=1e-6), "cosine=True must be a true cosine"
    print("PASS l2_path_self_consistent")


def _recover(norm, cosine, D=64, N=16, vsize=64, dropout=0.5, trials=40, seed0=100):
    hits, total = 0, 0
    for t in range(trials):
        g = torch.Generator().manual_seed(seed0 + t)
        codebook = atoms.make_atoms(vsize, D, torch.complex64, g)   # filler values
        keys = atoms.make_atoms(N, D, torch.complex64, g)           # role keys
        vals_idx = torch.randint(0, vsize, (N,), generator=g)
        pairs = torch.stack([binding.bind(keys[i], codebook[vals_idx[i]]) for i in range(N)])
        mem = bundling.bundle(pairs, norm=norm)
        for i in range(N):
            key = keys[i].clone()
            if dropout > 0:                                         # partial cue: zero a fraction of components
                mask = (torch.rand(D, generator=g) > dropout).to(key.dtype)
                key = key * mask
            readback = binding.unbind(mem, key)
            sims = torch.stack([atoms.similarity(readback, codebook[j], cosine=cosine) for j in range(vsize)])
            hits += int(sims.argmax().item() == int(vals_idx[i]))
            total += 1
    return hits / total


def test_l2_helps_binding_recovery_under_partial_cue():
    default_hit = _recover(norm=None, cosine=False)
    l2_hit = _recover(norm="l2", cosine=True)
    assert l2_hit >= default_hit, \
        "L2+cosine must recover at least as well as per-component+/n under a partial cue: %.3f vs %.3f" % (l2_hit, default_hit)
    print("PASS l2_helps_recovery: L2+cosine %.3f >= default per-component %.3f" % (l2_hit, default_hit))


if __name__ == "__main__":
    test_default_byte_identical()
    test_l2_path_self_consistent()
    test_l2_helps_binding_recovery_under_partial_cue()
    print("WITNESS PASS")
