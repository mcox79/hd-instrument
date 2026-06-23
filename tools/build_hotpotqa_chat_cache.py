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
    """Build (s, p, o) triples from supporting_facts + context + article-text mentions.

    Relation types (5):
    - COSUPPORTS — two titles that BOTH appear in same question's supporting_facts (bridge articles)
    - CONTEXT_OF — supporting-fact title → other context-article title for same question
    - MENTIONS — article A's text contains article B's title (substring match)
    - IS_A — article A title → noun-phrase pattern 'is a X' from first sentence
    - DIRECTED_BY / WRITTEN_BY / PRODUCED_BY / BORN_IN — pattern-extracted from article text
    """
    triples: list[tuple[str, str, str]] = []
    n_questions = 0
    all_titles: set[str] = set()
    # First pass: collect all unique titles + their sentences for substring matching
    title_to_sentences: dict[str, list[str]] = {}
    questions = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                q = json.loads(line)
            except json.JSONDecodeError:
                continue
            questions.append(q)
            n_questions += 1
            ctx_titles = q.get("context", {}).get("title", [])
            ctx_sents = q.get("context", {}).get("sentences", [])
            for t, sents in zip(ctx_titles, ctx_sents):
                if not t:
                    continue
                norm_t = normalize_entity(t)
                all_titles.add(norm_t)
                if norm_t not in title_to_sentences:
                    title_to_sentences[norm_t] = []
                # sents is a list of sentence strings for this article
                if isinstance(sents, list):
                    title_to_sentences[norm_t].extend(sents[:3])  # keep first 3 sentences
    print(f"[hotpot-build] processed {n_questions} questions; collected {len(all_titles)} unique titles")

    # Pattern compile for extraction (case-insensitive on original text; lowercased+_'d title comparison)
    import re
    P_DIRECTED = re.compile(r"\bdirected\s+by\s+([A-Z][^,\.;]{0,60})", re.IGNORECASE)
    P_WRITTEN = re.compile(r"\bwritten\s+by\s+([A-Z][^,\.;]{0,60})", re.IGNORECASE)
    P_PRODUCED = re.compile(r"\bproduced\s+by\s+([A-Z][^,\.;]{0,60})", re.IGNORECASE)
    P_BORN = re.compile(r"\b(?:was\s+)?born\s+(?:in|on)\s+([A-Z][^,\.;]{0,60})", re.IGNORECASE)
    P_ISA = re.compile(r"^([A-Z][^,\.]{2,80}?)\s+(?:is|was)\s+(?:an?\s+)?([^,\.]{2,80}?)(?:[,\.]|$)", re.IGNORECASE)

    # Build COSUPPORTS + CONTEXT_OF per question (original 2 relations)
    for q in questions:
        sf_titles = q.get("supporting_facts", {}).get("title", [])
        ctx_titles = q.get("context", {}).get("title", [])
        sf_set = {normalize_entity(t) for t in sf_titles if t}
        ctx_set = {normalize_entity(t) for t in ctx_titles if t}
        sf_list = sorted(sf_set)
        for i in range(len(sf_list)):
            for j in range(i + 1, len(sf_list)):
                triples.append((sf_list[i], "COSUPPORTS", sf_list[j]))
                triples.append((sf_list[j], "COSUPPORTS", sf_list[i]))
        for sf in sf_set:
            for ctx in ctx_set:
                if ctx == sf:
                    continue
                triples.append((sf, "CONTEXT_OF", ctx))

    # Pattern-extracted relations from article text
    n_pattern = 0
    for title_norm, sents in title_to_sentences.items():
        text = " ".join(sents)
        # DIRECTED_BY / WRITTEN_BY / PRODUCED_BY / BORN_IN — extract object as normalized entity
        for pat, rel in [(P_DIRECTED, "DIRECTED_BY"), (P_WRITTEN, "WRITTEN_BY"),
                          (P_PRODUCED, "PRODUCED_BY"), (P_BORN, "BORN_IN")]:
            for m in pat.finditer(text):
                obj_raw = m.group(1).strip()
                # Trim trailing words like "and", "with", "in", etc.
                obj_words = obj_raw.split()
                # Heuristic: keep first 1-4 capitalized words (proper-noun-like)
                kept = []
                for w in obj_words[:5]:
                    if not w:
                        break
                    if w[0].isupper() or kept:
                        kept.append(w)
                    else:
                        break
                    if len(kept) >= 4:
                        break
                if not kept:
                    continue
                obj_norm = normalize_entity(" ".join(kept))
                if obj_norm == title_norm:
                    continue
                triples.append((title_norm, rel, obj_norm))
                n_pattern += 1
        # IS_A: first sentence only
        if sents:
            m = P_ISA.match(sents[0].strip())
            if m:
                obj_raw = m.group(2).strip().split()
                kept = obj_raw[:3]
                if kept:
                    obj_norm = normalize_entity(" ".join(kept))
                    if obj_norm != title_norm and len(obj_norm) > 1:
                        triples.append((title_norm, "IS_A", obj_norm))
                        n_pattern += 1

    # MENTIONS: title A in title B's text (substring; bounded to known titles)
    # Avoid quadratic scan — for each title, check if any OTHER known title appears as substring in its sentences
    n_mentions = 0
    title_list = list(all_titles)
    # Make lowercase-space versions for substring search
    title_searchable = {t: t.replace("_", " ") for t in title_list}
    for src_title, sents in title_to_sentences.items():
        text_lower = " ".join(sents).lower()
        for tgt_title in title_list:
            if tgt_title == src_title:
                continue
            srch = title_searchable[tgt_title]
            if len(srch) < 4:  # avoid noise from very short titles
                continue
            if srch in text_lower:
                triples.append((src_title, "MENTIONS", tgt_title))
                n_mentions += 1

    print(f"[hotpot-build] pattern-extracted: {n_pattern} relations; mention-extracted: {n_mentions}")
    print(f"[hotpot-build] raw triples total={len(triples)}")
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
