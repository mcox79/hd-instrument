"""hdlab/hub_spoke_word.py -- a word as ONE vector that is internally ADDRESSED.

WHAT THIS IS
------------
A word representation that is a SINGLE hypervector but whose facets stay separately
askable. Each facet ("spoke") is bound to its own key before the spokes are summed:

    word_vector(w) = Q( SUM_s  bind( SPOKE_KEY[s], spoke_code_s(w) ) )
    ask_for(w_vec, s) = unbind( w_vec, SPOKE_KEY[s] )      # bipolar bind is self-inverse

BRAIN CLAIM, AND WHICH HALF IS OURS
-----------------------------------
PINNED-BY-EVIDENCE: word FORM (visual word form area) and word MEANING (modality spokes in
sensory and motor cortex) are separate brain systems tied together by an anterior-temporal
hub, and each piece keeps its OWN address. The evidence is a double dissociation -- hub
damage degrades meaning across all modalities at once, focal spoke damage produces
modality-specific loss with the rest intact. A single blended store predicts only the first.

OUR-INVENTION-BEING-TESTED: implementing "ask for one facet" as unbind-by-role-key. We do
NOT claim the brain performs elementwise multiplication. Any writeup using this module must
carry that tag.

THE EXTENSION PROPERTY IS THE LOAD-BEARING DESIGN CHOICE
--------------------------------------------------------
`spoke_key` derives a key from blake2b(seed || spoke_name) AND NOTHING ELSE -- deliberately
NOT from a shared torch.Generator whose stream depends on how many spokes were requested
first. That is the whole reason a spoke can be added later: adding a fifth spoke leaves the
four existing keys BIT-IDENTICAL, so every word vector already written stays readable and
its facet answers do not change. `add_spoke()` returns an extended codec and asserts that
invariant rather than trusting it.

REUSE, NOT REIMPLEMENTATION
---------------------------
The binding primitives here are the numpy twins of the validated torch primitives in
`hdlab.role_slot_summarizer` (`_bipolar_bind`, `_bipolar_quantize`), which
`hdlab.event_bundle.EventBundleCodec` already reuses for role-slot event binding. This
module is the SAME algebra applied to word facets instead of event roles. The equality is
ASSERTED, not asserted-in-prose: `selftest_reuse_is_bit_identical()` checks both the
primitives and a full bundle against `EventBundleCodec.encode_event`.

NOT A STORE. One word, one vector. Whether many of these survive being superposed together
is a different question (component #2) and this module makes no claim about it.

ASCII-only. numpy float32 throughout; bipolar spoke codes are exactly {-1,+1}.
"""
from __future__ import annotations

import hashlib
from typing import Dict, Iterable, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "spoke_key",
    "bipolar_bind",
    "bipolar_quantize",
    "HubSpokeWord",
    "selftest_reuse_is_bit_identical",
    "selftest_extension_does_not_invalidate",
    "run_selftests",
]


# ----------------------------------------------------------------------------------
# primitives -- numpy twins of hdlab.role_slot_summarizer._bipolar_bind / _quantize
# ----------------------------------------------------------------------------------
def bipolar_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Elementwise multiply. Self-inverse for bipolar vectors, so unbind IS bind."""
    return np.asarray(a, dtype=np.float32) * np.asarray(b, dtype=np.float32)


def bipolar_quantize(x: np.ndarray) -> np.ndarray:
    """sign() with zeros mapped to +1 -- the same tie convention as role_slot_summarizer."""
    x = np.asarray(x, dtype=np.float32)
    return np.where(x >= 0.0, np.float32(1.0), np.float32(-1.0)).astype(np.float32)


def spoke_key(name: str, d: int, seed: int) -> np.ndarray:
    """Bipolar {-1,+1} key for a spoke, a pure function of (name, d, seed).

    ORDER-INDEPENDENT BY CONSTRUCTION. This is the extension guarantee: the key for a spoke
    added tomorrow is computed without touching the keys of the spokes added today, because
    nothing here consumes a shared random stream.
    """
    h = hashlib.blake2b(f"{int(seed)}:{name}".encode("utf-8"), digest_size=8).digest()
    rng = np.random.default_rng(int.from_bytes(h, "big"))
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=int(d)).astype(np.float32)


# ----------------------------------------------------------------------------------
# the codec
# ----------------------------------------------------------------------------------
class HubSpokeWord:
    """One word -> one vector, internally addressed by spoke.

    Args:
        d: dimensionality
        spokes: ordered spoke names (order affects NOTHING; kept only for reporting)
        seed: key-derivation seed
        quantize: apply a terminal sign() to the bundle (the production shape) or leave it
                  graded. Both are measured; neither is assumed.
        role_keys: optional explicit {name: vector} injection, for reuse-verification against
                   another codec's keys.

    Shapes: `bundle` takes (F, n, d) or {spoke: (n, d)} and returns (n, d).
    """

    def __init__(self, d: int, spokes: Sequence[str], seed: int = 7,
                 quantize: bool = False,
                 role_keys: Optional[Dict[str, np.ndarray]] = None) -> None:
        if len(set(spokes)) != len(spokes):
            raise ValueError(f"duplicate spoke names: {list(spokes)}")
        self.d = int(d)
        self.spokes: Tuple[str, ...] = tuple(spokes)
        self.seed = int(seed)
        self.quantize = bool(quantize)
        if role_keys is None:
            self.keys: Dict[str, np.ndarray] = {
                s: spoke_key(s, self.d, self.seed) for s in self.spokes}
        else:
            missing = [s for s in self.spokes if s not in role_keys]
            if missing:
                raise KeyError(f"role_keys missing spokes {missing}")
            self.keys = {s: np.asarray(role_keys[s], dtype=np.float32) for s in self.spokes}
        for s, k in self.keys.items():
            if k.shape != (self.d,):
                raise ValueError(f"key for {s!r} has shape {k.shape}, expected ({self.d},)")

    # ---- construction -----------------------------------------------------------
    def key(self, spoke: str) -> np.ndarray:
        return self.keys[spoke]

    def bundle(self, spoke_codes: Dict[str, np.ndarray]) -> np.ndarray:
        """Bind each spoke code to its key and sum. Returns (n, d)."""
        missing = [s for s in self.spokes if s not in spoke_codes]
        if missing:
            raise KeyError(f"spoke_codes missing {missing}")
        acc = None
        for s in self.spokes:                       # deterministic order; sum is commutative
            c = np.asarray(spoke_codes[s], dtype=np.float32)
            if c.ndim == 1:
                c = c[None, :]
            if c.shape[1] != self.d:
                raise ValueError(f"spoke {s!r} code has d={c.shape[1]}, expected {self.d}")
            term = c * self.keys[s][None, :]
            acc = term if acc is None else acc + term
        return bipolar_quantize(acc) if self.quantize else acc

    def flat_sum(self, spoke_codes: Dict[str, np.ndarray]) -> np.ndarray:
        """The SAME content with NO binding -- the unaddressed control. Returns (n, d)."""
        acc = None
        for s in self.spokes:
            c = np.asarray(spoke_codes[s], dtype=np.float32)
            if c.ndim == 1:
                c = c[None, :]
            acc = c.copy() if acc is None else acc + c
        return bipolar_quantize(acc) if self.quantize else acc

    # ---- read-out ---------------------------------------------------------------
    def ask_for(self, vecs: np.ndarray, spoke: str) -> np.ndarray:
        """Unbind one spoke out of the single word vector. Returns (n, d)."""
        v = np.asarray(vecs, dtype=np.float32)
        if v.ndim == 1:
            v = v[None, :]
        return v * self.keys[spoke][None, :]

    # ---- the extension path -----------------------------------------------------
    def add_spoke(self, name: str) -> "HubSpokeWord":
        """Return a codec with one more spoke, asserting every existing key is unchanged.

        This is the owner's constraint made executable: 'something we can add how it looks
        later'. The assertion is here rather than in a test so that an extension which WOULD
        invalidate stored vectors fails loudly at the moment it is attempted.
        """
        if name in self.spokes:
            raise ValueError(f"spoke {name!r} already present")
        ext = HubSpokeWord(self.d, self.spokes + (name,), self.seed, self.quantize)
        for s in self.spokes:
            if not np.array_equal(ext.keys[s], self.keys[s]):
                raise AssertionError(
                    f"EXTENSION INVALIDATED STORED VECTORS: key for existing spoke {s!r} "
                    f"changed when adding {name!r}. Key derivation must not depend on the "
                    f"spoke set.")
        return ext


# ----------------------------------------------------------------------------------
# self-tests -- run BEFORE this module is used by any cell
# ----------------------------------------------------------------------------------
def selftest_reuse_is_bit_identical() -> dict:
    """Assert this module IS hdlab.role_slot_summarizer / hdlab.event_bundle algebra.

    Proves reuse rather than re-transcription: the numpy primitives must agree bit-for-bit
    with the torch ones, and a HubSpokeWord bundle must equal EventBundleCodec.encode_event
    on a matched configuration (same keys, same fillers, terminal quantise on).
    """
    import torch
    from hdlab.role_slot_summarizer import _bipolar_bind, _bipolar_quantize
    from hdlab.event_bundle import EventBundleCodec

    g = torch.Generator()
    g.manual_seed(11)
    d = 1024
    a_t = torch.where(torch.rand((d,), generator=g) < 0.5, -1.0, 1.0).to(torch.float32)
    b_t = torch.where(torch.rand((d,), generator=g) < 0.5, -1.0, 1.0).to(torch.float32)
    if not np.array_equal(bipolar_bind(a_t.numpy(), b_t.numpy()),
                          _bipolar_bind(a_t, b_t).numpy()):
        raise AssertionError("bipolar_bind is NOT bit-identical to role_slot_summarizer")
    x_t = torch.randn((d,), generator=g)
    if not np.array_equal(bipolar_quantize(x_t.numpy()), _bipolar_quantize(x_t).numpy()):
        raise AssertionError("bipolar_quantize is NOT bit-identical to role_slot_summarizer")

    # full-bundle equality against the event codec, keys and fillers injected on both sides
    roles = ("PRED", "AGENT", "PATIENT", "TENSE")
    keys = {r: spoke_key(r, d, 7) for r in roles}
    fill = {r: spoke_key("filler:" + r, d, 99) for r in roles}
    codec = EventBundleCodec(
        n_dim=d, roles=roles, seed=0,
        role_keys=torch.from_numpy(np.stack([keys[r] for r in roles])),
        symbols=[f"F_{r}" for r in roles],
        symbol_codebook=torch.from_numpy(np.stack([fill[r] for r in roles])))
    ref = codec.encode_event({r: f"F_{r}" for r in roles}).numpy()
    hsw = HubSpokeWord(d=d, spokes=roles, seed=7, quantize=True)
    got = hsw.bundle({r: fill[r] for r in roles})[0]
    if not np.array_equal(got, ref):
        raise AssertionError("HubSpokeWord.bundle is NOT bit-identical to "
                             "EventBundleCodec.encode_event")
    # and the read-out agrees on which facet comes back
    for r in roles:
        q = hsw.ask_for(got, r)[0]
        sims = np.array([float(q @ fill[s]) for s in roles])
        if roles[int(np.argmax(sims))] != r:
            raise AssertionError(f"ask_for({r}) recovered the wrong spoke")
    return {"d": d, "roles": list(roles), "reuse_verified":
            "role_slot_summarizer primitives + EventBundleCodec.encode_event"}


def selftest_extension_does_not_invalidate() -> dict:
    """Adding a spoke must leave existing keys, existing vectors and existing answers alone."""
    d = 512
    spokes = ("FORM", "SENSORY", "ACTION", "CONCRETE")
    rng = np.random.default_rng(3)
    n = 64
    codes = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(n, d))
             for s in spokes}
    base = HubSpokeWord(d=d, spokes=spokes, seed=7, quantize=False)
    stored = base.bundle(codes)

    def facet_acc(codec, vecs, spoke_set):
        hits = 0
        tot = 0
        pool = np.stack([codes[s] for s in spoke_set], 0)          # (F, n, d)
        for si, s in enumerate(spoke_set):
            q = codec.ask_for(vecs, s)                              # (n, d)
            sims = np.einsum("fnd,nd->nf", pool, q)
            hits += int(np.sum(np.argmax(sims, axis=1) == si))
            tot += q.shape[0]
        return hits / float(tot)

    before = facet_acc(base, stored, spokes)
    ext = base.add_spoke("VISION")                                  # asserts key stability
    after = facet_acc(ext, stored, spokes)      # SAME stored vectors, EXTENDED codec
    if after != before:
        raise AssertionError(
            f"extension changed the answers for already-stored vectors: {before} -> {after}")
    if before < 0.99:
        raise AssertionError(f"4-spoke facet recovery too low to be a valid check: {before}")
    # newly written 5-spoke vectors still answer the four ORIGINAL spokes
    codes5 = dict(codes)
    codes5["VISION"] = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(n, d))
    new_vecs = ext.bundle(codes5)
    pool5 = np.stack([codes5[s] for s in ext.spokes], 0)
    hits = 0
    tot = 0
    for si, s in enumerate(ext.spokes):
        if s == "VISION":
            continue
        q = ext.ask_for(new_vecs, s)
        sims = np.einsum("fnd,nd->nf", pool5, q)
        hits += int(np.sum(np.argmax(sims, axis=1) == si))
        tot += q.shape[0]
    acc5 = hits / float(tot)
    if acc5 < 0.95:
        raise AssertionError(f"5-spoke recovery of the ORIGINAL spokes too low: {acc5}")
    return {"d": d, "acc_4spoke": before, "acc_after_extension": after,
            "acc_5spoke_on_original_spokes": acc5}


def run_selftests() -> dict:
    out = {"reuse": selftest_reuse_is_bit_identical(),
           "extension": selftest_extension_does_not_invalidate()}
    return out


if __name__ == "__main__":
    import json
    print("[hub_spoke_word selftest] PASS " + json.dumps(run_selftests()))
