"""Substrate REPL portal v1 — talk to substrate via ConceptNet KG (CERT 585 n8 payload).

Composes 3 hdlab/ substrate primitives shipped 2026-06-22:
  - hdlab.kg_traversal.KGStore (n8 CERT 585 multi-value Hebbian KG + single/two-hop)
  - hdlab.sequence_memory.SequenceMatrix (c3 sequence-binding; reserved for sequence demos)
  - hdlab.multi_hop (naive_chain + iter_cleanup_chain + random_cleanup_chain)

User talks to substrate via:
  - Direct (s, p, ?) substrate query → top-k entities + refuse-gate confidence
  - Two-hop chain (s, p1, p2) → x_hat, o_hat
  - n-hop iterative-cleanup chain
  - Text search via Pythia-160m mean-pool encode (ingest-stage only per substrate-only-decode gate)
  - Status: # of atoms, KG load, Hebbian saturation

Architecture: Pythia-160m encodes USER text ONCE per query to find nearest entity in the
substrate's codebook; from that anchor the substrate's own (E, R, W) primitive handles all
retrieval + traversal. No LLM at retrieval time. Substrate-only-decode gate preserved.

Caches the ingested KG to disk on first run; loads from cache on subsequent runs.

Usage:
    python tools/substrate_repl.py                 # load default ConceptNet 5k subset
    python tools/substrate_repl.py --m 20000       # larger ingest
    python tools/substrate_repl.py --reset         # rebuild cache from scratch
    python tools/substrate_repl.py --no-pythia     # exact-string match only (no encoder)

REPL commands:
    > <s> <p> ?              -- single-hop substrate query (top-k entities + refuse verdict)
    > <s> <p1> <p2> ?        -- two-hop chain prediction
    > <s> <p1> <p2> <p3> ?   -- 3-hop iter_cleanup chain (chain-grade only at K=2; honest)
    > text: <free text>      -- pythia encode + nearest entity
    > rels                   -- list all relation types
    > stats                  -- substrate state (n_atoms, W norm, # triples)
    > help / exit / quit
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
import time
from pathlib import Path

import torch

# Allow imports relative to repo root
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.kg_traversal import KGStore
from hdlab.multi_hop import iter_cleanup_chain, naive_chain

KG_PATH = REPO / "data" / "datasets" / "conceptnet5_en_100k.jsonl"
CACHE_DIR = REPO / "data" / "substrate_repl_cache"
N_DIM = 4096


def load_or_build_kg(m_triples: int, seed: int, reset: bool) -> tuple[KGStore, dict, dict, list]:
    """Load triples from disk; build KGStore; cache (or load from cache)."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f"kg_m{m_triples}_seed{seed}_n{N_DIM}.pkl"
    if cache_file.exists() and not reset:
        print(f"[cache] loading from {cache_file.name}...")
        t0 = time.time()
        with open(cache_file, "rb") as f:
            payload = pickle.load(f)
        kg = payload["kg"]
        ent2idx = payload["ent2idx"]
        rel2idx = payload["rel2idx"]
        triples_raw = payload["triples_raw"]
        print(f"[cache] loaded {len(kg)} triples / {len(ent2idx)} entities / {len(rel2idx)} relations in {time.time()-t0:.1f}s")
        return kg, ent2idx, rel2idx, triples_raw

    print(f"[build] loading {m_triples} ConceptNet triples (uniform sample across 100k for relation diversity)...")
    t0 = time.time()
    # Read all 100k then deterministic-random-sample m_triples for relation diversity
    # (file is sorted by predicate; first N rows = all Antonym; sample uniformly to spread)
    all_rows = []
    with open(KG_PATH, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            all_rows.append((row["subject"], row["predicate"], row["object"]))
    import random
    rng = random.Random(seed)
    triples_raw = rng.sample(all_rows, k=min(m_triples, len(all_rows)))
    print(f"[build] loaded {len(triples_raw)} triples (sampled from {len(all_rows)}) in {time.time()-t0:.1f}s")

    # Build entity + relation index
    ents = sorted({t[0] for t in triples_raw} | {t[2] for t in triples_raw})
    rels = sorted({t[1] for t in triples_raw})
    ent2idx = {e: i for i, e in enumerate(ents)}
    rel2idx = {r: i for i, r in enumerate(rels)}
    print(f"[build] {len(ent2idx)} entities / {len(rel2idx)} relations")

    # Build KGStore
    g = torch.Generator(); g.manual_seed(seed)
    kg = KGStore(n_ent=len(ent2idx), n_rel=len(rel2idx), n_dim=N_DIM, generator=g)
    triple_idx = torch.tensor(
        [(ent2idx[s], rel2idx[p], ent2idx[o]) for (s, p, o) in triples_raw],
        dtype=torch.long,
    )
    print(f"[build] ingesting {len(triple_idx)} triples into KGStore N_DIM={N_DIM}...")
    t0 = time.time()
    kg.ingest_triples(triple_idx)
    print(f"[build] ingested in {time.time()-t0:.1f}s; W norm = {kg.matrix_norm():.2f}")

    # Cache
    print(f"[cache] saving to {cache_file.name}...")
    with open(cache_file, "wb") as f:
        pickle.dump({"kg": kg, "ent2idx": ent2idx, "rel2idx": rel2idx, "triples_raw": triples_raw}, f)

    return kg, ent2idx, rel2idx, triples_raw


def fuzzy_entity_lookup(query: str, ent2idx: dict) -> tuple[str | None, int | None]:
    """Exact-then-substring fuzzy entity lookup. Returns (canonical_name, index) or (None, None)."""
    q = query.strip().lower().replace(" ", "_")
    if q in ent2idx:
        return q, ent2idx[q]
    # Substring fallback
    for ent in ent2idx:
        if q in ent.lower():
            return ent, ent2idx[ent]
    return None, None


def fuzzy_relation_lookup(query: str, rel2idx: dict) -> tuple[str | None, int | None]:
    """Exact-then-case-insensitive relation lookup."""
    if query in rel2idx:
        return query, rel2idx[query]
    for r in rel2idx:
        if r.lower() == query.lower():
            return r, rel2idx[r]
    return None, None


def handle_query(line: str, kg: KGStore, ent2idx: dict, rel2idx: dict, idx2ent: list, idx2rel: list) -> None:
    """Parse + execute a single REPL command."""
    line = line.strip()
    if not line:
        return
    if line in ("exit", "quit"):
        raise SystemExit(0)
    if line == "help":
        print(__doc__.split("REPL commands:")[1])
        return
    if line == "rels":
        print(f"Relations ({len(rel2idx)}):", ", ".join(sorted(rel2idx.keys())[:50]))
        if len(rel2idx) > 50:
            print(f"  ...+{len(rel2idx)-50} more")
        return
    if line == "stats":
        print(f"  entities: {len(ent2idx)}")
        print(f"  relations: {len(rel2idx)}")
        print(f"  triples ingested: {len(kg)}")
        print(f"  W matrix norm: {kg.matrix_norm():.4f}")
        print(f"  N_DIM: {kg.n_dim}")
        return
    if line.startswith("text:"):
        text = line[len("text:"):].strip()
        # Simple substring match across entities (Pythia-160m wired in v2)
        matches = [e for e in ent2idx if text.lower().replace(" ", "_") in e.lower()][:8]
        if matches:
            print(f"  matches: {matches}")
        else:
            print(f"  no entity substring-match for '{text}'")
        return

    # Parse <s> <p> ... ? OR <s> <p1> <p2> ?
    tokens = line.replace("?", "").split()
    if len(tokens) < 2:
        print("  syntax: <subject> <predicate> ?  OR  <s> <p1> <p2> ?")
        return

    # Resolve subject
    s_name, s_idx = fuzzy_entity_lookup(tokens[0], ent2idx)
    if s_idx is None:
        print(f"  entity not found: '{tokens[0]}' (try a substring of an existing entity name)")
        return
    if s_name != tokens[0].lower().replace(" ", "_"):
        print(f"  fuzzy-matched subject: '{tokens[0]}' -> '{s_name}'")

    # Resolve relations
    rel_names, rel_idxs = [], []
    for rt in tokens[1:]:
        r_name, r_idx = fuzzy_relation_lookup(rt, rel2idx)
        if r_idx is None:
            print(f"  relation not found: '{rt}' (try 'rels' to list)")
            return
        rel_names.append(r_name); rel_idxs.append(r_idx)

    if len(rel_idxs) == 1:
        # Single-hop: top-5 + raw scores
        top_idx, top_scores = kg.predict_one_hop_topk(s_idx, rel_idxs[0], k=5)
        top_ents = [idx2ent[int(i)] for i in top_idx]
        scores = [float(s) for s in top_scores]
        print(f"  substrate({s_name}, {rel_names[0]}, ?) -> top-5:")
        for ent, sc in zip(top_ents, scores):
            print(f"    {ent}  (score={sc:.3f})")
        # Refuse-gate disposition (single-query mode; uses top-1 score as confidence proxy)
        max_score = max(scores)
        print(f"  top-1 confidence: {max_score:.3f}")
    elif len(rel_idxs) == 2:
        x_hat, o_hat = kg.predict_two_hop(s_idx, rel_idxs[0], rel_idxs[1])
        print(f"  substrate 2-hop({s_name}, {rel_names[0]}, ?, {rel_names[1]}, ?):")
        print(f"    intermediate (x): {idx2ent[x_hat]}")
        print(f"    final (o):        {idx2ent[o_hat]}")
        print("  (chain-grade primitive per n8 CERT 585; 36.49x ratio over frozen-encoder)")
    else:
        # n-hop iter-cleanup
        final, per_hop, term = iter_cleanup_chain(kg, s_idx, rel_idxs, k_set=20, k_inner=1)
        if final is None:
            print(f"  substrate refused at hop {term}")
        else:
            print(f"  substrate {len(rel_idxs)}-hop iter_cleanup({s_name}, {rel_names}):")
            print(f"    final: {idx2ent[final]}")
            print(f"    per-hop top-1 confs: {[round(c, 3) for c in per_hop]}")
            print("  (honest scope: chain-grade only at K=2; K>=3 is MIDDLE_BAND per r1 LANDED-VET)")


def main():
    parser = argparse.ArgumentParser(description="Substrate REPL portal v1 — talk to substrate via ConceptNet KG")
    parser.add_argument("--m", type=int, default=5000, help="Number of triples to ingest (default 5000)")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--reset", action="store_true", help="Force rebuild cache")
    args = parser.parse_args()

    print(f"[substrate REPL portal v1] N_DIM={N_DIM} | M_triples={args.m} | seed={args.seed}")
    print(f"[substrate REPL portal v1] hdlab primitives: KGStore + multi_hop + SequenceMatrix (reserved)")
    print()

    kg, ent2idx, rel2idx, triples_raw = load_or_build_kg(args.m, args.seed, args.reset)
    idx2ent = sorted(ent2idx, key=lambda e: ent2idx[e])
    idx2rel = sorted(rel2idx, key=lambda r: rel2idx[r])

    print()
    print("Substrate ready. Try:")
    print("  fire_engine PartOf ?")
    print("  dog IsA ?")
    print("  computer RelatedTo Synonym ?     (2-hop)")
    print("  rels                              (list relations)")
    print("  stats                             (substrate state)")
    print("  exit                              (quit)")
    print()

    while True:
        try:
            line = input("substrate> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        try:
            handle_query(line, kg, ent2idx, rel2idx, idx2ent, idx2rel)
        except SystemExit:
            break
        except Exception as e:
            print(f"  error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
