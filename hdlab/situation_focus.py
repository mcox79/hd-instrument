"""Active FOCUS of attention: a bounded-capacity superposition of event bundles + chunking.

Brain basis (Cowan 2001): human working memory holds ~4 (+/-1) chunks in the FOCUS OF
ATTENTION, hierarchically chunked -- each chunk is itself a bundle. This module maintains
the ~most-recent event/entity bundles as the focus; when the number of active units would
exceed CAPACITY, the OLDEST units are compressed into a higher-level CHUNK (the hierarchical
Level-2), so the active focus holds ~CAPACITY units with GRACEFUL degradation (recent items
stay accessible; older items are chunked and degrade), NOT an unbounded pool nor a hard cutoff.

Two focus classes give the fair chunking-ablation contrast on the SAME event stream:
  * FlatFocus    : chunking OFF. All n events superposed in one vector, each bound to a
                   position key. As n grows the superposition interference grows -> the raw
                   capacity limit (Cowan degradation).  focus = quantize(sum_j bind(pos_j, ev_j))
  * ChunkedFocus : chunking ON. Active buffer holds <= CAPACITY entries (EVENT or CHUNK).
                   Pushing past CAPACITY compresses the oldest `fanout` entries into one
                   nested CHUNK vector, keeping the ACTIVE superposition small -> recent
                   items stay accessible at any total load (recovery via chunking).

Both are GLASS-BOX: retrieval unbinds the position/chunk address(es) then unbinds the role
(via the EventBundleCodec) and cleans up to the filler. REUSES the bipolar bind/quantize
primitives from hdlab.role_slot_summarizer (byte-identical to the M1.7 validated binding).

ASCII-only. torch.Tensor bipolar {-1,+1} float32.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import torch

from hdlab.event_bundle import EventBundleCodec
from hdlab.role_slot_summarizer import _bipolar_bind, _bipolar_quantize, _bipolar_random


class FlatFocus:
    """Chunking OFF: single unbounded superposition of event bundles bound to position keys."""

    def __init__(self, codec: EventBundleCodec, max_items: int, seed: int = 0) -> None:
        self.codec = codec
        gen = torch.Generator(); gen.manual_seed(int(seed))
        self.pos_keys = _bipolar_random((max_items, codec.n_dim), gen)
        self.focus: torch.Tensor = torch.zeros(codec.n_dim, dtype=torch.float32)
        self.n = 0

    def build(self, event_vecs: Sequence[torch.Tensor]) -> torch.Tensor:
        acc = torch.zeros(self.codec.n_dim, dtype=torch.float32)
        for j, ev in enumerate(event_vecs):
            acc = acc + _bipolar_bind(self.pos_keys[j], ev)
        self.focus = _bipolar_quantize(acc)
        self.n = len(event_vecs)
        return self.focus

    def query(self, j: int, role: str) -> Tuple[str, float]:
        probe = _bipolar_bind(self.focus, self.pos_keys[j])  # unbind position
        return self.codec.query_role_vec(probe, role)


class _Entry:
    """One active-focus entry: an EVENT (depth 0) or a CHUNK (holds sub-entries)."""

    __slots__ = ("vec", "index", "is_chunk")

    def __init__(self, vec: torch.Tensor, index: Dict[int, List[int]], is_chunk: bool):
        self.vec = vec                 # (n_dim,)
        self.index = index            # global_event_idx -> inner unbind path (list of inner-key idxs)
        self.is_chunk = is_chunk


class ChunkedFocus:
    """Chunking ON: bounded active buffer (<= capacity); oldest units compress into chunks."""

    def __init__(self, codec: EventBundleCodec, capacity: int = 4, fanout: int = 2,
                 seed: int = 0) -> None:
        if fanout < 2:
            raise ValueError("fanout must be >= 2")
        if capacity < fanout:
            raise ValueError("capacity must be >= fanout")
        self.codec = codec
        self.capacity = int(capacity)
        self.fanout = int(fanout)
        gen = torch.Generator(); gen.manual_seed(int(seed))
        self.slot_keys = _bipolar_random((self.capacity, codec.n_dim), gen)  # active addresses
        self.inner_keys = _bipolar_random((self.fanout, codec.n_dim), gen)   # within-chunk addresses
        self.active: List[_Entry] = []

    def _make_chunk(self, subs: List[_Entry]) -> _Entry:
        acc = torch.zeros(self.codec.n_dim, dtype=torch.float32)
        new_index: Dict[int, List[int]] = {}
        for k, sub in enumerate(subs):
            acc = acc + _bipolar_bind(self.inner_keys[k], sub.vec)
            for gidx, path in sub.index.items():
                new_index[gidx] = [k] + path  # prepend this level's inner address
        return _Entry(_bipolar_quantize(acc), new_index, is_chunk=True)

    def push(self, event_vec: torch.Tensor, global_idx: int) -> None:
        if len(self.active) >= self.capacity:
            subs = self.active[: self.fanout]
            rest = self.active[self.fanout:]
            chunk = self._make_chunk(subs)
            self.active = [chunk] + rest
        self.active.append(_Entry(event_vec, {global_idx: []}, is_chunk=False))

    def focus_vec(self) -> torch.Tensor:
        acc = torch.zeros(self.codec.n_dim, dtype=torch.float32)
        for i, entry in enumerate(self.active):
            acc = acc + _bipolar_bind(self.slot_keys[i], entry.vec)
        return _bipolar_quantize(acc)

    def locate(self, global_idx: int) -> Tuple[int, List[int]]:
        for i, entry in enumerate(self.active):
            if global_idx in entry.index:
                return i, entry.index[global_idx]
        raise KeyError(f"event {global_idx} not in active focus")

    def is_direct(self, global_idx: int) -> bool:
        """True if the event is a direct (recent) EVENT slot (depth 0), not inside a chunk."""
        _i, path = self.locate(global_idx)
        return len(path) == 0

    def depth(self, global_idx: int) -> int:
        _i, path = self.locate(global_idx)
        return len(path)

    def query(self, global_idx: int, role: str) -> Tuple[str, float]:
        i, path = self.locate(global_idx)
        probe = _bipolar_bind(self.focus_vec(), self.slot_keys[i])  # unbind active slot
        for k in path:
            probe = _bipolar_bind(probe, self.inner_keys[k])        # unbind each chunk level
        return self.codec.query_role_vec(probe, role)


# ===================== formula self-tests ==========================================

def _selftest_chunked_keeps_active_bounded() -> None:
    codec = EventBundleCodec(n_dim=512, seed=1)
    codec.prime_symbols([f"w{i}" for i in range(40)])
    cf = ChunkedFocus(codec, capacity=4, fanout=2, seed=5)
    for g in range(8):
        rf = {"PRED": "w0", "AGENT": f"w{g+1}", "PATIENT": f"w{g+10}", "TENSE": "w0"}
        cf.push(codec.encode_event(rf), g)
        assert len(cf.active) <= cf.capacity, f"active grew past capacity at push {g}"
    # the 8th (last) event must be a direct recent slot (depth 0); an early event must be chunked
    assert cf.is_direct(7), "most recent event should be a direct slot"
    assert cf.depth(0) >= 1, "oldest event should be chunked (depth >= 1)"


def _selftest_flat_degrades_chunked_recovers_recent() -> None:
    """Small deterministic check: at high load, chunked-recent beats flat-all."""
    n_dim = 256
    codec = EventBundleCodec(n_dim=n_dim, seed=2)
    vocab = [f"w{i}" for i in range(50)]
    codec.prime_symbols(vocab)
    gen = torch.Generator(); gen.manual_seed(7)
    roles = codec.roles
    n = 8
    trials = 60
    flat_hit = 0; flat_tot = 0
    recent_hit = 0; recent_tot = 0
    for _ in range(trials):
        events = []
        picks = []
        for _g in range(n):
            p = [vocab[int(torch.randint(0, len(vocab), (1,), generator=gen))] for _ in roles]
            picks.append(p)
            events.append(codec.encode_event({roles[i]: p[i] for i in range(len(roles))}))
        ff = FlatFocus(codec, max_items=n, seed=11); ff.build(events)
        cf = ChunkedFocus(codec, capacity=4, fanout=2, seed=11)
        for g in range(n):
            cf.push(events[g], g)
        for g in range(n):
            for ri in (1, 2):  # AGENT, PATIENT
                s, _ = ff.query(g, roles[ri])
                flat_tot += 1
                if s == picks[g][ri]:
                    flat_hit += 1
            if cf.is_direct(g):
                for ri in (1, 2):
                    s, _ = cf.query(g, roles[ri])
                    recent_tot += 1
                    if s == picks[g][ri]:
                        recent_hit += 1
    flat_acc = flat_hit / flat_tot
    recent_acc = recent_hit / recent_tot
    # Chunked recent (in-focus) items must be retrievable well above the flat mean at load 8.
    assert recent_acc - flat_acc >= 0.10, (
        f"chunking gave no recovery: recent={recent_acc:.3f} flat={flat_acc:.3f}")


def _run_all_selftests() -> dict:
    _selftest_chunked_keeps_active_bounded()
    _selftest_flat_degrades_chunked_recovers_recent()
    return {"capacity_default": 4, "fanout_default": 2}


if __name__ == "__main__":
    r = _run_all_selftests()
    print(f"[situation_focus selftest] PASS {r}")
