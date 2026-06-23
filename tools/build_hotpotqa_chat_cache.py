"""Build a HotpotQA chat cache pickle for the dashboard.

Loads `data/datasets/hotpot_qa_distractor_dev_1k.jsonl`, extracts Wikipedia
article titles as entities, builds relations between supporting-fact titles
that co-occur per question, ingests into a KGStore, and pickles to
`data/substrate_repl_cache/kg_hotpotqa_dev_1k_n4096.pkl` in the same payload
format the dashboard's `_ensure_chat_kg_loaded` expects.

The dashboard picks the LARGEST cache file in `data/substrate_repl_cache/`
by glob `kg_m*.pkl` — so the filename here uses `kg_m{m_triples}` prefix
(per the loader's expected pattern) with `_hotpotqa` infix for clarity.

Run from repo root:
    .venv/Scripts/python tools/build_hotpotqa_chat_cache.py
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

HOTPOT_PATH = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
CACHE_DIR = REPO / "data" / "substrate_repl_cache"
N_DIM = 4096
SEED = 7


def normalize_entity(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def extract_triples_from_hotpotqa(path: Path) -> tuple[list[tuple[str, str, str]], dict, dict]:
    """Build (s, p, o) triples from supporting_facts + context.

    Two relation types:
    - COSUPPORTS — two titles that BOTH appear in the same question's supporting_facts
                   (these are the multi-hop bridge articles; chain-grade signal per h_hotpotqa CERT 588)
    - CONTEXT_OF — supporting-fact title → other context-article title for the same question
                   (broader association; weaker than COSUPPORTS but adds vocabulary coverage)
    """
    triples: list[tuple[str, str, str]] = []
    n_questions = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                q = json.loads(line)
            except json.JSONDecodeError:
                continue
            n_questions += 1
            sf_titles = q.get("supporting_facts", {}).get("title", [])
            ctx_titles = q.get("context", {}).get("title", [])
            sf_set = {normalize_entity(t) for t in sf_titles if t}
            ctx_set = {normalize_entity(t) for t in ctx_titles if t}
            # COSUPPORTS: bidirectional between supporting facts (the multi-hop bridge)
            sf_list = sorted(sf_set)
            for i in range(len(sf_list)):
                for j in range(i + 1, len(sf_list)):
                    triples.append((sf_list[i], "COSUPPORTS", sf_list[j]))
                    triples.append((sf_list[j], "COSUPPORTS", sf_list[i]))
            # CONTEXT_OF: each supporting fact → each other context article (one direction)
            for sf in sf_set:
                for ctx in ctx_set:
                    if ctx == sf:
                        continue
                    triples.append((sf, "CONTEXT_OF", ctx))
    print(f"[hotpot-build] processed {n_questions} questions; raw triples={len(triples)}")
    # Dedupe while preserving order
    seen = set()
    unique = []
    for t in triples:
        if t in seen:
            continue
        seen.add(t)
        unique.append(t)
    print(f"[hotpot-build] unique triples={len(unique)}")
    ents = sorted({t[0] for t in unique} | {t[2] for t in unique})
    rels = sorted({t[1] for t in unique})
    ent2idx = {e: i for i, e in enumerate(ents)}
    rel2idx = {r: i for i, r in enumerate(rels)}
    print(f"[hotpot-build] entities={len(ents)} relations={len(rels)}")
    return unique, ent2idx, rel2idx


def main():
    t0 = time.time()
    if not HOTPOT_PATH.exists():
        print(f"missing: {HOTPOT_PATH}", file=sys.stderr)
        sys.exit(1)
    triples_raw, ent2idx, rel2idx = extract_triples_from_hotpotqa(HOTPOT_PATH)

    n_ent = len(ent2idx)
    n_rel = len(rel2idx)
    generator = torch.Generator().manual_seed(SEED)
    kg = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=N_DIM, generator=generator)

    idx_triples = [(ent2idx[s], rel2idx[r], ent2idx[o]) for (s, r, o) in triples_raw]
    triples_t = torch.tensor(idx_triples, dtype=torch.long)
    print(f"[hotpot-build] ingesting {len(idx_triples)} triples into KGStore (N_DIM={N_DIM})...")
    kg.ingest_triples(triples_t)
    print(f"[hotpot-build] ingest done in {time.time()-t0:.1f}s; W_norm={kg.matrix_norm():.2f}")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out = CACHE_DIR / f"kg_m{len(idx_triples)}_hotpotqa_dev_1k_n{N_DIM}.pkl"
    payload = {
        "kg": kg,
        "ent2idx": ent2idx,
        "rel2idx": rel2idx,
        "triples_raw": triples_raw,
    }
    with open(out, "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"[hotpot-build] wrote {out.name} ({size_mb:.1f} MB) total={time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
