"""Tiny smoke test for Workstream B baselines.

Exercises store/retrieve/edit/delete/audit on dict + faiss + sqlite_vec.
Chroma is opt-in via SMOKE_CHROMA=1 because its install can be flaky on Windows.

Run from repo root:
    python testbed/smoke_baselines.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import numpy as np

from testbed.api import DeletionCertificate, RetrievalResult


def _check_basic(backend, dim: int) -> None:
    rng = np.random.default_rng(7)
    vecs = rng.standard_normal((8, dim)).astype(np.float32)
    for i, v in enumerate(vecs):
        backend.store(f"k{i}", v, f"value_{i}")
    assert len(backend) == 8, f"{backend.name}: expected 8 items, got {len(backend)}"

    r = backend.retrieve(vecs[3])
    assert isinstance(r, RetrievalResult), f"{backend.name}: bad RetrievalResult type"
    assert r.key_id == "k3", f"{backend.name}: argmax mismatch {r.key_id}"
    assert r.value == "value_3", f"{backend.name}: value mismatch {r.value}"

    backend.edit("k3", "edited_3")
    r2 = backend.retrieve(vecs[3])
    assert r2.value == "edited_3", f"{backend.name}: edit not visible"

    cert = backend.delete("k3")
    assert isinstance(cert, DeletionCertificate)
    assert cert.erased, f"{backend.name}: delete cert erased=False"
    assert len(backend) == 7, f"{backend.name}: post-delete count {len(backend)}"

    audit = backend.audit()
    assert audit.n_items == 7, f"{backend.name}: audit n_items {audit.n_items}"
    assert audit.storage_bytes >= 0


def main() -> int:
    dim = 64
    failures: list[str] = []

    # dict
    try:
        from testbed.baselines.dict_adapter import DictMemory

        m = DictMemory(dim=dim)
        _check_basic(m, dim)
        with tempfile.TemporaryDirectory() as td:
            m.save(Path(td))
            m2 = DictMemory(dim=dim)
            m2.load(Path(td))
            assert len(m2) == 7
        print("[smoke] dict OK")
    except Exception as exc:
        failures.append(f"dict: {type(exc).__name__}: {exc}")
        print(f"[smoke] dict FAIL: {exc}")

    # faiss
    try:
        from testbed.baselines.faiss_adapter import FaissMemory

        m = FaissMemory(dim=dim)
        _check_basic(m, dim)
        with tempfile.TemporaryDirectory() as td:
            m.save(Path(td))
            m2 = FaissMemory(dim=dim)
            m2.load(Path(td))
            assert len(m2) == 7
        print("[smoke] faiss OK")
    except ImportError as exc:
        print(f"[smoke] faiss SKIP (not installed): {exc}")
    except Exception as exc:
        failures.append(f"faiss: {type(exc).__name__}: {exc}")
        print(f"[smoke] faiss FAIL: {exc}")

    # sqlite_vec
    try:
        from testbed.baselines.sqlite_vec_adapter import SqliteVecMemory

        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "smoke.db"
            m = SqliteVecMemory(db_path=db, dim=dim)
            _check_basic(m, dim)
            m.save(db)
            m2 = SqliteVecMemory(db_path=db, dim=dim)
            assert len(m2) == 7
        print("[smoke] sqlite_vec OK")
    except ImportError as exc:
        print(f"[smoke] sqlite_vec SKIP (not installed): {exc}")
    except Exception as exc:
        failures.append(f"sqlite_vec: {type(exc).__name__}: {exc}")
        print(f"[smoke] sqlite_vec FAIL: {exc}")

    # chroma (opt-in)
    if os.environ.get("SMOKE_CHROMA") == "1":
        try:
            from testbed.baselines.chroma_adapter import ChromaMemory

            with tempfile.TemporaryDirectory() as td:
                m = ChromaMemory(persist_dir=Path(td), dim=dim)
                _check_basic(m, dim)
            print("[smoke] chroma OK")
        except ImportError as exc:
            print(f"[smoke] chroma SKIP (not installed): {exc}")
        except Exception as exc:
            failures.append(f"chroma: {type(exc).__name__}: {exc}")
            print(f"[smoke] chroma FAIL: {exc}")
    else:
        print("[smoke] chroma SKIP (set SMOKE_CHROMA=1 to enable)")

    if failures:
        print("[smoke] FAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("[smoke] all OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
