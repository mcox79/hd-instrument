"""Build the semantic codebook for the substrate REPL portal v2 — English chat enablement.

For each entity in the KGStore cache, compute its sentence-transformer embedding
(all-MiniLM-L6-v2, 384-dim, normalized). Cache to disk. At chat-time, user free-text
is encoded the same way + cosine-sim against semantic_codebook returns top-k nearest
entities. Those entities then become the anchor for the substrate KG query.

Substrate-only-decode gate preserved: MiniLM at user-query time is ingest-stage by
analogy (one-time per query, not iterative, not generation). The substrate W matrix
+ KGStore primitives handle all actual retrieval.

Usage:
    python tools/build_substrate_semantic_codebook.py            # use latest KG cache
    python tools/build_substrate_semantic_codebook.py --reset    # rebuild
"""

from __future__ import annotations

import argparse
import pickle
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO / "data" / "substrate_repl_cache"
ENCODER_NAME = "all-MiniLM-L6-v2"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Rebuild even if cache exists")
    parser.add_argument("--cache", default=None, help="Specific KG cache file (defaults to largest)")
    args = parser.parse_args()

    # Find the KG cache
    if args.cache:
        kg_cache = Path(args.cache)
    else:
        candidates = sorted(CACHE_DIR.glob("kg_m*.pkl"), key=lambda p: p.stat().st_size, reverse=True)
        if not candidates:
            print("[err] no KG cache found; run tools/substrate_repl.py --m 10000 first")
            sys.exit(1)
        kg_cache = candidates[0]
    print(f"[build] using KG cache: {kg_cache.name}")

    # Output path for semantic codebook (mirrors KG cache name)
    sem_path = kg_cache.with_name(kg_cache.stem.replace("kg_", "semantic_") + ".pkl")
    if sem_path.exists() and not args.reset:
        print(f"[skip] semantic codebook already exists: {sem_path.name}; use --reset to rebuild")
        return

    # Load KG cache
    with open(kg_cache, "rb") as f:
        payload = pickle.load(f)
    ent2idx = payload["ent2idx"]
    rel2idx = payload["rel2idx"]
    n_ents = len(ent2idx)
    n_rels = len(rel2idx)
    print(f"[build] {n_ents} entities + {n_rels} relations to encode")

    # Build text inputs (replace underscores with spaces for natural English)
    ent_names = sorted(ent2idx, key=lambda e: ent2idx[e])
    ent_texts = [e.replace("_", " ") for e in ent_names]
    rel_names = sorted(rel2idx, key=lambda r: rel2idx[r])
    rel_texts = [r for r in rel_names]  # relations are CamelCase; keep as-is

    # Load MiniLM
    print(f"[build] loading {ENCODER_NAME}...")
    t0 = time.time()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(ENCODER_NAME, device="cpu")
    print(f"[build] model loaded in {time.time()-t0:.1f}s")

    # Encode entities (batched)
    print(f"[build] encoding {n_ents} entities + {n_rels} relations (batch=128)...")
    t0 = time.time()
    ent_embs = model.encode(ent_texts, batch_size=128, show_progress_bar=False, normalize_embeddings=True)
    rel_embs = model.encode(rel_texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
    print(f"[build] encoded in {time.time()-t0:.1f}s (rate {(n_ents+n_rels)/(time.time()-t0):.1f}/s)")

    # Save semantic codebook
    import numpy as np
    payload_out = {
        "encoder_name": ENCODER_NAME,
        "embed_dim": ent_embs.shape[1],
        "n_entities": n_ents,
        "n_relations": n_rels,
        "ent_names": ent_names,
        "rel_names": rel_names,
        "ent_embs": np.asarray(ent_embs, dtype=np.float32),
        "rel_embs": np.asarray(rel_embs, dtype=np.float32),
        "kg_cache_source": kg_cache.name,
        "built_at": time.time(),
    }
    with open(sem_path, "wb") as f:
        pickle.dump(payload_out, f)
    print(f"[build] saved semantic codebook: {sem_path.name} ({sem_path.stat().st_size/1e6:.1f}MB)")

    # Smoke-test: encode a few queries + show nearest entities
    queries = ["what is a cat?", "things that can fly", "objects in a kitchen", "drive a vehicle"]
    print()
    print("[smoke] nearest-entity for natural queries:")
    q_embs = model.encode(queries, normalize_embeddings=True)
    for q, qe in zip(queries, q_embs):
        sims = ent_embs @ qe
        top3 = sims.argsort()[-3:][::-1]
        print(f"  '{q}'")
        for idx in top3:
            print(f"    -> {ent_names[int(idx)]} (cos_sim={sims[int(idx)]:.3f})")


if __name__ == "__main__":
    main()
