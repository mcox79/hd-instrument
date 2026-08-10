"""Event-bundle codec: situation-model EVENT as ONE role-slot-bound hypervector.

A reader-extracted predicate-argument tuple (PRED, AGENT, PATIENT, TENSE) is encoded
into a SINGLE event vector by role-slot binding:

    event_vec = quantize( sum_r  bind(role_key[r], filler_vec[r]) )

and is GLASS-BOX / UNBINDABLE: querying a role recovers its filler by unbinding then
cleanup:

    filler_hat = cleanup( unbind(event_vec, role_key[role]) )   # -> the AGENT / PATIENT / ...

This is exactly the M1.7 RoleSlotSummarizer FLAT role-slot binding (bipolar bind =
elementwise multiply, self-inverse; bundle = sign of the sum; cleanup = matmul + argmax).
This module REUSES those byte-identical primitives from hdlab.role_slot_summarizer
(_bipolar_bind / _bipolar_quantize / _bipolar_random) so the event-bundle format is the
same validated substrate binding, not a re-transcription. See
`_selftest_reuses_role_slot_summarizer_flat` which asserts bit-identity vs
RoleSlotSummarizer.summarize_flat / read_flat at N_DIM=8192.

Baselines for the fairness contrast (both stored in the SAME substrate, both CANNOT
answer a role query):
  * THIN-LABEL   : the event as ONE atomic random vector (an opaque event id / string
                   label). Unbinding a role gives noise -> cleanup ~ chance.
  * BAG-OF-ARGS  : quantize(sum of filler vecs) with NO role binding (a bag of arguments,
                   roles discarded). The fillers are present but WHICH role each plays is
                   gone -> role-query ~ chance.

Storage strategy (per USER-locked storage-strategy substrate physics law, CG_META
2026-07-02): an event bundle is a SMALL fixed superposition (~4 role-filler pairs) at
alpha = 4/N_DIM << the 0.138 bundle-collapse wall, so a single-vector (bundled) event is
the correct, high-fidelity representation at this level -- it round-trips cleanly. The
capacity limit lives one level up, in the FOCUS (hdlab.situation_focus), where many event
bundles are superposed; that is where sharded/chunked storage earns its place.

ASCII-only. All vectors torch.Tensor bipolar {-1,+1} float32.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import torch

# REUSE the validated M1.7 role-slot binding primitives (byte-identical).
from hdlab.role_slot_summarizer import (
    _bipolar_bind,
    _bipolar_quantize,
    _bipolar_random,
)

DEFAULT_ROLES: Tuple[str, ...] = ("PRED", "AGENT", "PATIENT", "TENSE")


class EventBundleCodec:
    """Encode/query events as role-slot-bound hypervectors + the thin-label baselines.

    Args:
        n_dim: substrate dimensionality (bipolar vectors of length n_dim)
        roles: ordered role names; each gets a fixed random bipolar role key
        seed: torch.Generator seed for role keys + lazily-grown symbol codebook
        role_keys: optional (R, n_dim) tensor to inject role keys (for reuse-verification
                   / pluggability); if None, generated from seed
        symbols / symbol_codebook: optional initial (symbol -> vector) codebook to inject

    Public API:
        encode_event(role_fillers) -> (n_dim,) bundle vector
        query_role_vec(vec, role)  -> (filler_symbol, score)   [glass-box unbind + cleanup]
        encode_thin_label()        -> (n_dim,) atomic baseline vector
        encode_bag_of_args(fillers)-> (n_dim,) no-role-binding baseline vector
        codebook() / symbols()     -> the current symbol codebook / symbol list
    """

    def __init__(
        self,
        n_dim: int,
        roles: Sequence[str] = DEFAULT_ROLES,
        seed: int = 0,
        role_keys: Optional[torch.Tensor] = None,
        symbols: Optional[Sequence[str]] = None,
        symbol_codebook: Optional[torch.Tensor] = None,
    ) -> None:
        self.n_dim = int(n_dim)
        self.roles = tuple(roles)
        self.seed = int(seed)
        self._gen = torch.Generator()
        self._gen.manual_seed(self.seed)
        if role_keys is None:
            role_keys = _bipolar_random((len(self.roles), self.n_dim), self._gen)
        if role_keys.shape != (len(self.roles), self.n_dim):
            raise ValueError(
                f"role_keys shape {tuple(role_keys.shape)} != "
                f"({len(self.roles)}, {self.n_dim})")
        self.role_keys = role_keys.to(torch.float32)
        self._role_idx = {r: i for i, r in enumerate(self.roles)}
        self._sym2idx: Dict[str, int] = {}
        self._idx2sym: List[str] = []
        self._rows: List[torch.Tensor] = []
        self._cb_cache: Optional[torch.Tensor] = None
        if symbols is not None and symbol_codebook is not None:
            for s, row in zip(symbols, symbol_codebook):
                self._register(str(s), row.to(torch.float32))

    # ---- symbol codebook (lazily grown; deterministic given seed + insert order) ----
    def _register(self, sym: str, vec: torch.Tensor) -> int:
        idx = len(self._rows)
        self._sym2idx[sym] = idx
        self._idx2sym.append(sym)
        self._rows.append(vec)
        self._cb_cache = None
        return idx

    def _sym_vec(self, sym: str) -> torch.Tensor:
        sym = str(sym)
        if sym not in self._sym2idx:
            v = _bipolar_random((self.n_dim,), self._gen)
            self._register(sym, v)
        return self._rows[self._sym2idx[sym]]

    def prime_symbols(self, symbols: Sequence[str]) -> None:
        """Pre-register a vocabulary (deterministic codebook order = sorted caller input)."""
        for s in symbols:
            self._sym_vec(str(s))

    def codebook(self) -> torch.Tensor:
        if self._cb_cache is None:
            self._cb_cache = (torch.stack(self._rows, 0) if self._rows
                              else torch.empty((0, self.n_dim), dtype=torch.float32))
        return self._cb_cache

    def symbols(self) -> List[str]:
        return list(self._idx2sym)

    def vocab_size(self) -> int:
        return len(self._rows)

    def role_key(self, role: str) -> torch.Tensor:
        return self.role_keys[self._role_idx[role]]

    # ---- event bundle (PRIMARY) ------------------------------------------------------
    def encode_event(self, role_fillers: Dict[str, str]) -> torch.Tensor:
        """role_fillers: {role_name: filler_symbol}. Returns the (n_dim,) event bundle."""
        acc = torch.zeros(self.n_dim, dtype=torch.float32)
        for role, filler in role_fillers.items():
            if role not in self._role_idx:
                raise KeyError(f"unknown role {role!r}; known={self.roles}")
            acc = acc + _bipolar_bind(self.role_key(role), self._sym_vec(filler))
        return _bipolar_quantize(acc)

    def query_role_vec(self, vec: torch.Tensor,
                       role: str) -> Tuple[Optional[str], float]:
        """GLASS-BOX unbind: filler_hat = unbind(vec, role_key); cleanup -> (symbol, score)."""
        if not self._rows:
            return None, 0.0
        filler_hat = _bipolar_bind(vec, self.role_key(role))  # bipolar unbind == bind
        scores = self.codebook() @ filler_hat  # (V,)
        j = int(torch.argmax(scores).item())
        return self._idx2sym[j], float(scores[j].item())

    # ---- baselines (fairness contrast; both CANNOT answer a role query) --------------
    def encode_thin_label(self) -> torch.Tensor:
        """Event as ONE atomic random vector (opaque id / string label). No role structure."""
        return _bipolar_random((self.n_dim,), self._gen)

    def encode_bag_of_args(self, fillers: Sequence[str]) -> torch.Tensor:
        """Bag of arguments: quantize(sum of filler vecs), roles DISCARDED (no binding)."""
        acc = torch.zeros(self.n_dim, dtype=torch.float32)
        for f in fillers:
            acc = acc + self._sym_vec(f)
        return _bipolar_quantize(acc)

    def encode_scrambled_event(self, role_fillers: Dict[str, str],
                               perm: Sequence[int]) -> torch.Tensor:
        """P2 control: bind each filler to a PERMUTED role key (role<->filler binding
        destroyed). perm is a permutation of range(len(roles)); filler for roles[i] is
        bound to role_keys[perm[i]]. Querying the TRUE role then recovers the WRONG filler.
        """
        acc = torch.zeros(self.n_dim, dtype=torch.float32)
        role_list = list(role_fillers.keys())
        for i, role in enumerate(role_list):
            filler = role_fillers[role]
            acc = acc + _bipolar_bind(self.role_keys[perm[i]], self._sym_vec(filler))
        return _bipolar_quantize(acc)


# ===================== formula self-tests ==========================================

def _selftest_reuses_role_slot_summarizer_flat() -> None:
    """Assert the event bundle IS RoleSlotSummarizer.summarize_flat role-slot binding.

    Inject RoleSlotSummarizer's own role keys (as item keys) + value codebook into the
    codec, then assert encode_event == rss.summarize_flat bit-for-bit AND query_role_vec
    == rss.read_flat for every role. This proves the reuse (not re-transcription).
    """
    from hdlab.role_slot_summarizer import RoleSlotSummarizer

    n_dim = 8192
    rss = RoleSlotSummarizer(n_dim=n_dim, seed=7)
    cb = rss.value_codebook()          # (V, n_dim) value vectors
    # Use the first 4 value vectors as our four role KEYS (arbitrary fixed bipolar keys).
    role_keys = cb[:4].clone()
    roles = ("PRED", "AGENT", "PATIENT", "TENSE")
    # Fillers = 4 distinct value indices (later rows of the codebook).
    val_idx = [10, 20, 30, 40]
    symbols = [f"S{v}" for v in val_idx]
    sym_cb = torch.stack([cb[v] for v in val_idx], 0)
    codec = EventBundleCodec(n_dim=n_dim, roles=roles, seed=0,
                             role_keys=role_keys, symbols=symbols,
                             symbol_codebook=sym_cb)
    role_fillers = {roles[i]: symbols[i] for i in range(4)}
    ev = codec.encode_event(role_fillers)
    # rss.summarize_flat(item_keys=role_keys, val_indices=val_idx) is the SAME computation.
    ref = rss.summarize_flat(role_keys, torch.tensor(val_idx))
    if not torch.equal(ev, ref):
        raise AssertionError("event bundle NOT bit-identical to RoleSlotSummarizer.summarize_flat")
    # query_role_vec must recover each filler (== rss.read_flat over the full value codebook).
    for i, role in enumerate(roles):
        sym, _ = codec.query_role_vec(ev, role)
        if sym != symbols[i]:
            raise AssertionError(f"role-query FAIL for {role}: got {sym}, want {symbols[i]}")
        ref_val = rss.read_flat(role_keys[i], ref)  # cleanup over the FULL value codebook
        if ref_val != val_idx[i]:
            raise AssertionError(
                f"rss.read_flat mismatch for {role}: got {ref_val}, want {val_idx[i]}")


def _selftest_event_roundtrip_and_baselines_fail() -> None:
    """P1 (bundle round-trips) + baselines cannot answer a role query, at N=1024."""
    n_dim = 1024
    codec = EventBundleCodec(n_dim=n_dim, seed=3)
    vocab = [f"w{i}" for i in range(60)]
    codec.prime_symbols(vocab)
    gen = torch.Generator(); gen.manual_seed(99)
    roles = codec.roles
    n_ev = 40
    hits = 0
    thin_hits = 0
    bag_hits = 0
    total = 0
    for _ in range(n_ev):
        pick = [vocab[int(torch.randint(0, len(vocab), (1,), generator=gen))] for _ in roles]
        rf = {roles[i]: pick[i] for i in range(len(roles))}
        ev = codec.encode_event(rf)
        thin = codec.encode_thin_label()
        bag = codec.encode_bag_of_args(pick)
        for i, role in enumerate(roles):
            total += 1
            s, _ = codec.query_role_vec(ev, role)
            if s == pick[i]:
                hits += 1
            st, _ = codec.query_role_vec(thin, role)
            if st == pick[i]:
                thin_hits += 1
            sb, _ = codec.query_role_vec(bag, role)
            if sb == pick[i]:
                bag_hits += 1
    p1 = hits / total
    thin_acc = thin_hits / total
    bag_acc = bag_hits / total
    if p1 < 0.98:
        raise AssertionError(f"P1 round-trip FAIL: bundle role-query acc {p1:.3f} < 0.98")
    if thin_acc > 0.20:
        raise AssertionError(f"thin-label baseline NOT at chance: {thin_acc:.3f} > 0.20")
    if bag_acc > 0.40:
        raise AssertionError(f"bag-of-args baseline too high: {bag_acc:.3f} > 0.40")


def _run_all_selftests() -> dict:
    _selftest_reuses_role_slot_summarizer_flat()
    _selftest_event_roundtrip_and_baselines_fail()
    return {"roles": list(DEFAULT_ROLES), "reuse_verified": "RoleSlotSummarizer.summarize_flat"}


if __name__ == "__main__":
    r = _run_all_selftests()
    print(f"[event_bundle selftest] PASS {r}")
