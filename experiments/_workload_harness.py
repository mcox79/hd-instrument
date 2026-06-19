"""Shared CRUD-workload harness for sparse-W stress experiments.

Used by:
  - exp_sparse_w_edit_heavy_v1_n4096       (heavy edit workload)
  - exp_sparse_w_mixed_crud_v1_n4096       (40/30/20/10 CRUD)
  - exp_sparse_w_deletion_sequences_v1_n4096 (sustained deletes-with-cert)

Provides:
  - DenseStore / SparseStore reference state objects
  - Atomic CRUD ops:  store_fact, retrieve, edit_fact, delete_fact
  - Workload generators (deterministic, seeded)
  - Killer-feature spot-check helpers (KF-2 max_iso during/after workload)

Design notes:
  - DenseStore keeps W = sum of outer products (values_i, keys_i) / N.
  - SparseStore keeps (keys: list[N], values: list[N]) and reconstructs
    response as (k_q @ keys.T) @ values / N for queries.
  - Edit = rank-1 update: W += (new_val - old_val) outer old_key / N (dense)
    or replace the values entry at the (key) position (sparse).
  - Delete = rank-1 retraction: W -= old_val outer old_key / N (dense)
    or remove the (key, value) pair (sparse).
  - "Deletion certificate" = (key_idx, val_idx, pre_hash, post_hash, op_id)
    chain. Not crypto-grade -- it is the AUDIT TRAIL the substrate's killer
    feature 3 (deletion provenance) builds on.

ASCII-only. Self-test included at module scope.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import hashlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent


# -------- substrate-primitive lazy loader --------
_T1V1 = None


def _load_t1v1():
    """Lazy load the substrate primitives (Kerdock codebook + store)."""
    global _T1V1
    if _T1V1 is None:
        path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
        spec = importlib.util.spec_from_file_location("t1v1_workload", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _T1V1 = mod
    return _T1V1


def build_codebook(N: int, device: torch.device) -> torch.Tensor:
    """Build the Kerdock 4-coset codebook of (C=4N, N)."""
    t1v1 = _load_t1v1()
    cb, _ = t1v1.v3.make_kerdock_4coset_codebook(N, device)
    return cb


# -------- substrate state objects --------

class DenseStore:
    """Dense W substrate. Maintains key/val index lists for audit."""

    def __init__(self, N: int, codebook: torch.Tensor,
                 device: torch.device, dtype=torch.float32) -> None:
        self.N = int(N)
        self.codebook = codebook
        self.device = device
        self.W = torch.zeros(N, N, dtype=dtype, device=device)
        self.key_ids: List[int] = []
        self.val_ids: List[int] = []
        # position -> index into key_ids/val_ids (for O(1) update via fact_id)
        # Each store assigns a monotonically-increasing fact_id.
        self.next_fact_id = 0
        # fact_id -> (key_id, val_id). Deleted facts get popped.
        self.facts: Dict[int, Tuple[int, int]] = {}

    def store_fact(self, key_id: int, val_id: int) -> int:
        """Store (key, value) and return the fact_id."""
        fid = self.next_fact_id
        self.next_fact_id += 1
        k = self.codebook[key_id]
        v = self.codebook[val_id]
        self.W = self.W + torch.outer(v, k) / self.N
        self.facts[fid] = (int(key_id), int(val_id))
        return fid

    def retrieve(self, key_id: int) -> Tuple[int, float]:
        """Argmax retrieval. Returns (predicted_val_id, confidence)."""
        k = self.codebook[key_id]
        out = k @ self.W.T               # (N,)
        sims = (self.codebook @ out) / self.N   # (C,)
        idx = int(torch.argmax(sims).item())
        return idx, float(sims[idx].item())

    def edit_fact(self, fact_id: int, new_val_id: int) -> bool:
        """Rank-1 swap. Returns True on success."""
        if fact_id not in self.facts:
            return False
        key_id, old_val_id = self.facts[fact_id]
        if new_val_id == old_val_id:
            return True
        k = self.codebook[key_id]
        old_v = self.codebook[old_val_id]
        new_v = self.codebook[new_val_id]
        self.W = self.W + torch.outer(new_v - old_v, k) / self.N
        self.facts[fact_id] = (int(key_id), int(new_val_id))
        return True

    def delete_fact(self, fact_id: int) -> bool:
        """Rank-1 retraction; remove from registry."""
        if fact_id not in self.facts:
            return False
        key_id, val_id = self.facts[fact_id]
        k = self.codebook[key_id]
        v = self.codebook[val_id]
        self.W = self.W - torch.outer(v, k) / self.N
        del self.facts[fact_id]
        return True

    def memory_bytes(self) -> int:
        return self.W.element_size() * self.W.numel()


class SparseStore:
    """Sparse-W substrate: (keys, values) list. W is the implicit response."""

    def __init__(self, N: int, codebook: torch.Tensor,
                 device: torch.device, dtype=torch.float32) -> None:
        self.N = int(N)
        self.codebook = codebook
        self.device = device
        self.dtype = dtype
        # Active rows = M actual facts. Stored as (M, N) tensors.
        self.keys = torch.zeros(0, N, dtype=dtype, device=device)
        self.values = torch.zeros(0, N, dtype=dtype, device=device)
        # fact_id -> row position in keys/values.
        self.next_fact_id = 0
        self.facts: Dict[int, Tuple[int, int]] = {}     # fid -> (key_id, val_id)
        self.fact_row: Dict[int, int] = {}              # fid -> row index

    def _append(self, k_row: torch.Tensor, v_row: torch.Tensor) -> int:
        row = self.keys.shape[0]
        self.keys = torch.cat([self.keys, k_row.unsqueeze(0)], dim=0)
        self.values = torch.cat([self.values, v_row.unsqueeze(0)], dim=0)
        return row

    def store_fact(self, key_id: int, val_id: int) -> int:
        fid = self.next_fact_id
        self.next_fact_id += 1
        k = self.codebook[key_id]
        v = self.codebook[val_id]
        row = self._append(k, v)
        self.facts[fid] = (int(key_id), int(val_id))
        self.fact_row[fid] = row
        return fid

    def retrieve(self, key_id: int) -> Tuple[int, float]:
        k = self.codebook[key_id]
        if self.keys.shape[0] == 0:
            return -1, 0.0
        # Sparse retrieve: (k @ keys.T) @ values / N
        coeffs = (k @ self.keys.T) / self.N           # (M,)
        out = coeffs @ self.values                    # (N,)
        sims = (self.codebook @ out) / self.N         # (C,)
        idx = int(torch.argmax(sims).item())
        return idx, float(sims[idx].item())

    def edit_fact(self, fact_id: int, new_val_id: int) -> bool:
        if fact_id not in self.facts:
            return False
        key_id, old_val_id = self.facts[fact_id]
        row = self.fact_row[fact_id]
        self.values[row] = self.codebook[new_val_id]
        self.facts[fact_id] = (int(key_id), int(new_val_id))
        return True

    def delete_fact(self, fact_id: int) -> bool:
        if fact_id not in self.facts:
            return False
        row = self.fact_row[fact_id]
        M = self.keys.shape[0]
        # Swap-last-and-pop for O(N) deletion
        if row != M - 1:
            self.keys[row] = self.keys[M - 1]
            self.values[row] = self.values[M - 1]
            # find the fact_id that was at last row and update its mapping
            last_fid = None
            for fid, r in self.fact_row.items():
                if r == M - 1 and fid != fact_id:
                    last_fid = fid
                    break
            if last_fid is not None:
                self.fact_row[last_fid] = row
        self.keys = self.keys[:M - 1]
        self.values = self.values[:M - 1]
        del self.facts[fact_id]
        del self.fact_row[fact_id]
        return True

    def memory_bytes(self) -> int:
        return (self.keys.element_size() * self.keys.numel()
                + self.values.element_size() * self.values.numel())


# -------- deletion-cert chain --------

def make_cert(prev_hash: str, op: str, fact_id: int,
              key_id: int, val_id: int, op_id: int) -> Dict[str, str]:
    """Build a single audit-chain link.

    cert = {prev_hash, op, fact_id, key_id, val_id, op_id, this_hash}
    where this_hash = sha256(prev_hash || op || ... ).
    """
    body = f"{prev_hash}|{op}|{fact_id}|{key_id}|{val_id}|{op_id}"
    h = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return {
        "prev_hash": prev_hash,
        "op": op,
        "fact_id": str(fact_id),
        "key_id": str(key_id),
        "val_id": str(val_id),
        "op_id": str(op_id),
        "this_hash": h,
    }


def verify_cert_chain(chain: List[Dict[str, str]]) -> bool:
    """Walk the chain and verify each link's hash."""
    if not chain:
        return True
    prev = "GENESIS"
    for link in chain:
        if link["prev_hash"] != prev:
            return False
        expect_body = (f"{link['prev_hash']}|{link['op']}|"
                       f"{link['fact_id']}|{link['key_id']}|"
                       f"{link['val_id']}|{link['op_id']}")
        expect = hashlib.sha256(expect_body.encode("utf-8")).hexdigest()
        if link["this_hash"] != expect:
            return False
        prev = link["this_hash"]
    return True


# -------- workload generators --------

def gen_edit_storm(
    n_initial_facts: int,
    n_edits: int,
    seed: int,
    n_codebook: int,
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (initial_facts, edit_ops).

    initial_facts: list of (key_id, val_id) tuples.
    edit_ops: list of (fact_id_target, new_val_id) tuples. fact_id_target is
        an index into the *initial_facts* list (the initial fact stays in
        the store; only its value changes).
    """
    gen = torch.Generator(device="cpu").manual_seed(seed + 8000)
    keys = torch.randperm(n_codebook, generator=gen)[:n_initial_facts].tolist()
    vals = torch.randint(0, n_codebook, (n_initial_facts,),
                          generator=gen).tolist()
    initial = [(int(k), int(v)) for k, v in zip(keys, vals)]
    # Edits
    edit_tgts = torch.randint(0, n_initial_facts, (n_edits,),
                                generator=gen).tolist()
    edit_vals = torch.randint(0, n_codebook, (n_edits,),
                                generator=gen).tolist()
    edits = [(int(t), int(v)) for t, v in zip(edit_tgts, edit_vals)]
    return initial, edits


def gen_mixed_crud(
    n_initial_facts: int,
    n_total_ops: int,
    op_mix: Tuple[float, float, float, float],
    seed: int,
    n_codebook: int,
) -> Tuple[List[Tuple[int, int]], List[Tuple[str, int, int]]]:
    """Generate a mixed CRUD workload.

    op_mix: (frac_store, frac_query, frac_edit, frac_delete) in [0,1].
    Returns (initial_facts, ops) where each op is (op_name, idx_a, idx_b).

    Op encoding:
      ("store", key_id, val_id)
      ("query", key_id, -1)
      ("edit",  fact_pos, new_val_id)         # fact_pos = position in
                                              #   *living* fact list
      ("delete", fact_pos, -1)
    """
    assert abs(sum(op_mix) - 1.0) < 1e-3, f"op_mix sums to {sum(op_mix)}"
    gen = torch.Generator(device="cpu").manual_seed(seed + 9000)
    # Initial
    keys = torch.randperm(n_codebook, generator=gen)[:n_initial_facts].tolist()
    vals = torch.randint(0, n_codebook, (n_initial_facts,),
                          generator=gen).tolist()
    initial = [(int(k), int(v)) for k, v in zip(keys, vals)]
    # Sample op types
    cdf = torch.tensor([op_mix[0],
                        op_mix[0] + op_mix[1],
                        op_mix[0] + op_mix[1] + op_mix[2],
                        1.0])
    u = torch.rand(n_total_ops, generator=gen)
    ops: List[Tuple[str, int, int]] = []
    for i in range(n_total_ops):
        which = int((u[i] >= cdf).sum().item())   # 0=store,1=query,2=edit,3=delete
        which = min(which, 3)
        if which == 0:  # store
            k = int(torch.randint(0, n_codebook, (1,), generator=gen).item())
            v = int(torch.randint(0, n_codebook, (1,), generator=gen).item())
            ops.append(("store", k, v))
        elif which == 1:  # query (key resolved at exec time from current facts)
            ops.append(("query", -1, -1))
        elif which == 2:  # edit existing fact
            v = int(torch.randint(0, n_codebook, (1,), generator=gen).item())
            ops.append(("edit", -1, v))
        else:  # delete
            ops.append(("delete", -1, -1))
    return initial, ops


# -------- KF-2 spot-check helper --------

def kf2_spot_check(
    store: "DenseStore | SparseStore",
    n_edits: int = 8,
    n_probe: int = 100,
    seed: int = 0,
) -> float:
    """Sample KF-2 max_iso for the current store state.

    Probe: take min(n_probe, M) of the living facts, record argmax accuracy
    before & after a sequence of n_edits rank-1 swaps on OTHER facts.
    Return max |delta_acc|.
    """
    fact_ids = list(store.facts.keys())
    M = len(fact_ids)
    if M < 4:
        return 0.0
    n = min(n_probe, max(2, M // 2))
    probe_fids = fact_ids[:n]
    edit_fids  = fact_ids[n:n + min(n_edits, M - n)]
    if not edit_fids:
        return 0.0

    def probe_acc() -> float:
        correct = 0
        for fid in probe_fids:
            kid, vid = store.facts[fid]
            pred, _ = store.retrieve(kid)
            if pred == vid:
                correct += 1
        return correct / max(1, len(probe_fids))

    acc_before = probe_acc()
    gen = torch.Generator(device="cpu").manual_seed(seed + 12345)
    C = store.codebook.shape[0]
    isos: List[float] = []
    saved_vals: List[Tuple[int, int]] = []
    for fid in edit_fids:
        new_v = int(torch.randint(0, C, (1,), generator=gen).item())
        old_kid, old_vid = store.facts[fid]
        saved_vals.append((fid, old_vid))
        store.edit_fact(fid, new_v)
        acc_after = probe_acc()
        isos.append(abs(acc_before - acc_after))
    # Restore state so the harness can keep running.
    for fid, vid in saved_vals:
        store.edit_fact(fid, vid)
    return float(max(isos) if isos else 0.0)


# -------- self-test --------

def _selftest() -> None:
    device = torch.device("cpu")
    N = 64
    M_init = 8
    # Tiny synthetic codebook (C, N) with normalized rows
    C = 4 * N
    torch.manual_seed(17)
    cb = torch.randn(C, N) / (N ** 0.5)

    # Dense
    ds = DenseStore(N=N, codebook=cb, device=device)
    fids = [ds.store_fact(2 + i, 100 + i) for i in range(M_init)]
    pred, conf = ds.retrieve(2)
    assert pred == 100, f"Dense initial retrieve: pred={pred}, want 100"

    ok = ds.edit_fact(fids[0], 200)
    assert ok, "Dense edit failed"
    pred2, _ = ds.retrieve(2)
    assert pred2 == 200, f"Dense post-edit: pred={pred2}, want 200"

    ok = ds.delete_fact(fids[0])
    assert ok, "Dense delete failed"
    pred3, _ = ds.retrieve(2)
    assert pred3 != 200, f"Dense post-delete: should not still return 200"

    # Sparse
    ss = SparseStore(N=N, codebook=cb, device=device)
    sfids = [ss.store_fact(2 + i, 100 + i) for i in range(M_init)]
    spred, _ = ss.retrieve(2)
    assert spred == 100, f"Sparse initial retrieve: pred={spred}, want 100"
    assert ss.keys.shape[0] == M_init
    ss.delete_fact(sfids[0])
    assert ss.keys.shape[0] == M_init - 1

    # Cert chain
    chain = []
    prev = "GENESIS"
    for i in range(5):
        link = make_cert(prev, "delete", fact_id=i,
                          key_id=10 + i, val_id=20 + i, op_id=i)
        chain.append(link)
        prev = link["this_hash"]
    assert verify_cert_chain(chain), "Cert chain self-test failed"
    # Tamper
    chain[2]["val_id"] = "999"
    assert not verify_cert_chain(chain), "Cert chain tamper-detect failed"

    # Workload generators
    init, edits = gen_edit_storm(n_initial_facts=8, n_edits=4,
                                   seed=17, n_codebook=C)
    assert len(init) == 8 and len(edits) == 4
    init2, ops = gen_mixed_crud(
        n_initial_facts=8, n_total_ops=20,
        op_mix=(0.4, 0.3, 0.2, 0.1),
        seed=17, n_codebook=C,
    )
    assert len(ops) == 20

    # KF-2 spot-check
    ds2 = DenseStore(N=N, codebook=cb, device=device)
    for k, v in init:
        ds2.store_fact(k, v)
    iso = kf2_spot_check(ds2, n_edits=2, n_probe=4, seed=17)
    assert 0.0 <= iso <= 1.0, f"kf2_spot_check iso out of range: {iso}"

    print("[selftest] _workload_harness PASS", flush=True)


_selftest()


__all__ = [
    "DenseStore",
    "SparseStore",
    "build_codebook",
    "make_cert",
    "verify_cert_chain",
    "gen_edit_storm",
    "gen_mixed_crud",
    "kf2_spot_check",
]
