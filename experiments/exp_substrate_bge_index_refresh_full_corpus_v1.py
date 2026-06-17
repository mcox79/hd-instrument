"""Action A: bge semantic-index FULL refresh over the full substrate corpus (~31k atoms incl. the 1229 STEP-B RF atoms).

Director RATIFY (Q1-Q6, 2026-06-17) of the USER-ratified DURABILITY+FINDABILITY Action A. Makes the substrate's own
retrieval semantic over the FULL corpus -- so the 1229 RESEARCH_FINDING atoms (STEP-B today) + the 3695 EXPERIMENT_RECORD
atoms become bge-retrievable (the "easy to find" directive). Prereg = the DURABILITY/FINDABILITY notes (Q5; DECISION 200c).

WHAT IT DOES: build one Retriever over the PartitionedStore (spans all corpora) + rebuild_index_cached(force_rebuild=True)
   -> bge-encodes all atoms -> writes data/substrate_index/cached_indices/bge_large_v2_name_<n>_<hash>.npz (Q2 FULL/one-cache).
COMPUTE (Q3): HEAVY (bge-large encode of ~31k atoms) -> REMOTE GPU overnight_queue. The bge model + 31k encode is NOT
   laptop-safe (USER compute policy 180b). LAPTOP runs only --smoke (wiring-check; no heavy encode).
CADENCE (Q4): ONE-SHOT now; recurring hd_index_refresh task designed after this validates clean.
MANIFEST (Q6): Orchestrator extends remote_metrics_tar.py to include cached_indices/*.npz -> hd_metrics_sync pulls the
   new cache to local -> local substrate retrieval becomes semantic for the full corpus.

GATING: Skunkworks SCHEMA-VET (cert-owner) on this cell before Orchestrator queue_add (overnight GPU); Testbed invariant
   verify of the cache (coverage = n_atoms; no substrate-atom mutation -- this writes a CACHE, not atoms).
Run: REMOTE GPU (full); laptop `--smoke` for wiring-check. ASCII-only.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
DATA_ROOT = REPO / "data" / "substrate_index"
ANCHOR = "substrate_bge_index_refresh_full_corpus_v1"
OUT = REPO / "data" / ANCHOR


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="wiring-check only (no heavy bge encode; laptop-safe)")
    args, _ = ap.parse_known_args()
    smoke = args.smoke or os.environ.get("HDLAB_RUN_MODE", "full") == "smoke"
    t0 = time.time()

    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.retrieve_cache import list_caches, _cache_path, _compute_content_hash

    pstore = PartitionedStore(DATA_ROOT)
    atoms = pstore.all_atoms()
    n_atoms = len(atoms)
    id_order = [a.id for a in atoms]
    content_hash = _compute_content_hash(id_order)
    target_cache = _cache_path(DATA_ROOT, n_atoms, content_hash).name
    existing = list_caches(DATA_ROOT)

    OUT.mkdir(parents=True, exist_ok=True)
    if smoke:
        # wiring-check ONLY (laptop-safe): corpus enumerates + cache target resolves + Retriever/rebuild_index_cached
        # are importable. We do NOT construct AtomEncoder() -- it EAGERLY loads bge (sentence-transformers + the
        # bge-large model) which is REMOTE-GPU-ONLY by design (not installed locally per compute policy 180b). So the
        # laptop smoke verifies everything EXCEPT the bge encoder; the FULL encode is the remote run.
        import importlib
        retr_mod = importlib.import_module("backend.substrate_index.retrieve")
        cache_mod = importlib.import_module("backend.substrate_index.retrieve_cache")
        ok = (hasattr(retr_mod, "Retriever") and hasattr(cache_mod, "rebuild_index_cached") and n_atoms > 0)
        try:
            importlib.import_module("backend.substrate_index.encode")          # module importable (encoder construct = remote)
            enc_import_ok = True
        except Exception:
            enc_import_ok = False
        metrics = {"anchor_name": ANCHOR, "run_mode": "smoke", "wiring_ok": bool(ok), "encode_module_importable": enc_import_ok,
                   "n_atoms": n_atoms, "target_cache_file": target_cache, "existing_caches": existing,
                   "elapsed_s": round(time.time() - t0, 2),
                   "note": "wiring-check; AtomEncoder NOT constructed (bge eager-loads sentence-transformers = REMOTE-only); FULL = remote GPU."}
        (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        print(f"[{ANCHOR}] SMOKE wiring-check: ok={ok} (Retriever+rebuild_index_cached importable; n_atoms={n_atoms}; "
              f"encode-module-importable={enc_import_ok}) target={target_cache}")
        print(f"  existing caches: {existing}")
        print("  AtomEncoder NOT constructed locally (bge eager-loads sentence-transformers = REMOTE-only). FULL run = REMOTE GPU overnight.")
        return 0 if ok else 1

    # FULL (REMOTE GPU): bge-encode the full corpus + write the cache.
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    encoder = AtomEncoder()
    retriever = Retriever(pstore, encoder)
    from_cache = rebuild_index_cached(retriever, DATA_ROOT, force_rebuild=True)   # force = fresh FULL refresh
    elapsed = time.time() - t0
    # coverage = rows in the rebuilt semantic matrix
    sem = getattr(retriever, "_semantic_matrix", None)
    indexed = int(sem.shape[0]) if sem is not None else 0
    cache_now = list_caches(DATA_ROOT)
    metrics = {
        "anchor_name": ANCHOR, "run_mode": "full", "n_atoms": n_atoms, "atoms_indexed": indexed,
        "index_coverage_pct": round(100.0 * indexed / max(1, n_atoms), 2),
        "from_cache": bool(from_cache), "force_rebuild": True, "target_cache_file": target_cache,
        "caches_after": cache_now, "elapsed_s": round(elapsed, 2),
        "verdict": "OK" if indexed == n_atoms else "COVERAGE_GAP",
        "note": "FULL bge refresh; cache -> cached_indices/*.npz; hd_metrics_sync pulls to local (Q6 manifest).",
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[{ANCHOR}] FULL refresh: indexed {indexed}/{n_atoms} ({metrics['index_coverage_pct']}%) "
          f"in {elapsed:.1f}s -> {target_cache}  verdict={metrics['verdict']}")
    return 0 if indexed == n_atoms else 1


if __name__ == "__main__":
    raise SystemExit(main())
