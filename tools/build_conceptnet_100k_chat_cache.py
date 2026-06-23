"""Build a 100k-triple ConceptNet chat cache (10x current 10k backend).

Uses the same KGStore + Hebbian-binding mechanism that's chain-grade (CERT 585 n8).
Output: data/substrate_repl_cache/kg_m100000_conceptnet_100k_n4096.pkl

Same architecture as build_hotpotqa_chat_cache.py + substrate_repl.py — direct write,
no learning, deterministic codebook seeding.

Run from repo root:
    .venv/Scripts/python tools/build_conceptnet_100k_chat_cache.py
"""

from __future__ import annotations

import json
import pickle
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import torch  # noqa: E402

from hdlab.kg_traversal import KGStore  # noqa: E402

CONCEPTNET_PATH = REPO / "data" / "datasets" / "conceptnet5_en_100k.jsonl"
CACHE_DIR = REPO / "data" / "substrate_repl_cache"
N_DIM = 4096
SEED = 7


def load_triples(path: Path) -> tuple[list[tuple[str, str, str]], dict, dict]:
    triples: list[tuple[str, str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            s = str(r.get("subject", "")).strip()
            p = str(r.get("predicate", "")).strip()
            o = str(r.get("object", "")).strip()
            if not s or not p or not o:
                continue
            triples.append((s, p, o))
    # Dedupe
    seen = set()
    unique = []
    for t in triples:
        if t in seen:
            continue
        seen.add(t)
        unique.append(t)
    ents = sorted({t[0] for t in unique} | {t[2] for t in unique})
    rels = sorted({t[1] for t in unique})
    ent2idx = {e: i for i, e in enumerate(ents)}
    rel2idx = {r: i for i, r in enumerate(rels)}
    print(f"[conceptnet-build] unique_triples={len(unique)} entities={len(ents)} relations={len(rels)}")
    return unique, ent2idx, rel2idx


def main():
    t0 = time.time()
    if not CONCEPTNET_PATH.exists():
        print(f"missing: {CONCEPTNET_PATH}", file=sys.stderr)
        sys.exit(1)
    triples_raw, ent2idx, rel2idx = load_triples(CONCEPTNET_PATH)
    n_ent = len(ent2idx)
    n_rel = len(rel2idx)
    generator = torch.Generator().manual_seed(SEED)
    print(f"[conceptnet-build] initializing KGStore N_DIM={N_DIM} n_ent={n_ent} n_rel={n_rel}...")
    kg = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=N_DIM, generator=generator)
    idx_triples = [(ent2idx[s], rel2idx[r], ent2idx[o]) for (s, r, o) in triples_raw]
    triples_t = torch.tensor(idx_triples, dtype=torch.long)
    print(f"[conceptnet-build] ingesting {len(idx_triples)} triples...")
    kg.ingest_triples(triples_t)
    print(f"[conceptnet-build] ingest done in {time.time()-t0:.1f}s; W_norm={kg.matrix_norm():.2f}")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out = CACHE_DIR / f"kg_m{len(idx_triples)}_conceptnet_100k_n{N_DIM}.pkl"
    payload = {
        "kg": kg,
        "ent2idx": ent2idx,
        "rel2idx": rel2idx,
        "triples_raw": triples_raw,
    }
    with open(out, "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"[conceptnet-build] wrote {out.name} ({size_mb:.1f} MB) total={time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
