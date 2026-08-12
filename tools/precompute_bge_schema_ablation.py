"""Precompute bounded BGE-small embeddings for the schema-relation-transform-estimator
ablation cell (the SEMANTIC encoding arm).

BOUNDED probe (NOT a full-store re-encode): encodes ONLY the entities the ablation cell
references -- the codebook-mapped subjects + top-V objects for the 3 test relations
(AtLocation, CausesDesire, DerivedFrom). Saves a git-trackable npz (float16, ~7MB) so the
cell loads deterministic cached embeddings with ZERO model dependency at runtime (works
identically on the remote_cpu_queue box, which may not have the BGE model cached).

The entity-enumeration logic here MUST match the cell's load_relation exactly (same V,
same top-V object selection, same pair-filter). Kept inline (duplicated ~15 lines) so the
cell stays self-contained + SCP-safe (no sibling-module import).

Usage:
  .venv/Scripts/python.exe tools/precompute_bge_schema_ablation.py

ASCII-only.
"""
from __future__ import annotations
import sys
import json
import collections
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
DATASET = REPO / "data" / "datasets" / "conceptnet5_en_100k.jsonl"
OUT_NPZ = REPO / "data" / "datasets" / "bge_small_schema_ablation_entities_v1.npz"
RELATIONS = ["AtLocation", "CausesDesire", "DerivedFrom"]
V_CODEBOOK = 100
BGE_MODEL = "BAAI/bge-small-en-v1.5"


def load_relation_entities(relation: str, V: int):
    """Return the set of entities the cell touches for one relation:
    (codebook-mapped subjects) UNION (top-V codebook objects). Mirrors the cell."""
    objc = collections.Counter()
    pairs = []
    with open(DATASET, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("predicate") != relation:
                continue
            s, o = d.get("subject"), d.get("object")
            if s is None or o is None or s == o:
                continue
            pairs.append((str(s), str(o)))
            objc[str(o)] += 1
    codebook = [o for o, _ in objc.most_common(V)]
    cb_set = set(codebook)
    subj = {s for s, o in pairs if o in cb_set}
    return subj | cb_set


def main():
    import os
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer

    t0 = time.time()
    ents = set()
    for rel in RELATIONS:
        e = load_relation_entities(rel, V_CODEBOOK)
        print(f"[enum] {rel}: {len(e)} entities", flush=True)
        ents |= e
    ents = sorted(ents)
    print(f"[enum] TOTAL unique entities to encode: {len(ents)}", flush=True)

    print(f"[bge] loading {BGE_MODEL} (offline, cpu)...", flush=True)
    model = SentenceTransformer(BGE_MODEL, device="cpu")
    # BGE convention: entities are short lemmas; encode the raw string (conceptnet uses
    # underscores for multiword -> replace with space for the sentence encoder).
    texts = [e.replace("_", " ") for e in ents]
    emb = model.encode(texts, batch_size=256, normalize_embeddings=True,
                       show_progress_bar=True, convert_to_numpy=True)
    emb = emb.astype(np.float16)
    print(f"[bge] encoded {emb.shape} in {time.time() - t0:.1f}s", flush=True)

    # sanity cosines (float32 for the check)
    e32 = emb.astype(np.float32)
    idx = {e: i for i, e in enumerate(ents)}
    def cos(a, b):
        if a not in idx or b not in idx:
            return float("nan")
        va, vb = e32[idx[a]], e32[idx[b]]
        return float(va @ vb / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-12))
    for a, b in [("dog", "house"), ("sofa", "house"), ("dog", "physics")]:
        print(f"[sanity] cos({a},{b})={cos(a, b):.3f}", flush=True)

    OUT_NPZ.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT_NPZ, entities=np.array(ents, dtype=object), emb=emb,
                        model=BGE_MODEL, dim=emb.shape[1])
    sz = OUT_NPZ.stat().st_size
    print(f"[save] {OUT_NPZ} ({sz/1e6:.2f} MB, n={len(ents)}, dim={emb.shape[1]})", flush=True)


if __name__ == "__main__":
    main()
