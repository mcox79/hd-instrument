"""Unproduced/naturalistic-text probe sample builder (USER refinement, 2026-08-10, folded into
notes/design_extraction_quality_gate_neural_foundation_2026-08-10.md): does extraction quality
degrade PRODUCED -> UNPRODUCED text? Source: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
(already in-repo, CC BY-SA 4.0, "English Web Treebank -- weblogs, newsgroups, emails, reviews,
Yahoo! Answers. General web register" per its own PROVENANCE.md -- genuinely naturalistic/informal
written text, NOT edited news or literature, the closest already-available in-repo proxy for the
USER's tier-3 "real unproduced / naturalistic mess" register). Held out: never used for training
anything in this repo (PROVENANCE.md confirms test-only usage elsewhere too).

Selects a deterministic (no RNG) stride-sampled set of sentences spanning MULTIPLE newdoc
documents/genres, grouped into short passages (for the coref/shape check), restricted to
sentences whose ROOT (or a VERB token) carries a UD Tense feature (Past/Pres) so the
coverage-by-tense check has a real reference on this unproduced text too (a bonus: UD gold
morphology serves as the tense reference here, no new hand-authoring needed).

Produces: sample_unproduced_ud_ewt_v1.jsonl -- one record per PASSAGE:
  {"passage_id", "genre", "sentences": [str,...], "tenses": [str,...]}  (tenses parallel to
  sentences; "unk" if no VERB token in that sentence carries a Tense feature)
"""
from __future__ import annotations

import json
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONLLU_PATH = os.path.join(REPO_ROOT, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_unproduced_ud_ewt_v1.jsonl")

N_PASSAGES = 8
SENTS_PER_PASSAGE = 4
DOC_STRIDE = 35  # spreads picks across the 2077-sentence file's many newdoc groups


def parse_conllu(path: str):
    """Yield (newdoc_id, sent_text, tense) per sentence. tense = Tense feat of a VERB token
    (prefers the syntactic root if it is itself a VERB with Tense; else first VERB token with
    Tense) or "unk" if no VERB token carries Tense."""
    cur_doc = None
    text = None
    rows = []  # (upos, deprel, feats)

    def flush():
        if text is None:
            return None
        root_tense = None
        first_verb_tense = None
        for upos, deprel, feats in rows:
            if upos != "VERB":
                continue
            m = re.search(r"Tense=([A-Za-z]+)", feats or "")
            if not m:
                continue
            if first_verb_tense is None:
                first_verb_tense = m.group(1)
            if deprel == "root":
                root_tense = m.group(1)
        tense = root_tense or first_verb_tense or "unk"
        return (cur_doc, text, tense)

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# newdoc id"):
                cur_doc = line.split("=", 1)[1].strip()
            elif line.startswith("# text = "):
                if text is not None:
                    rec = flush()
                    if rec:
                        yield rec
                text = line[len("# text = "):]
                rows = []
            elif line and not line.startswith("#"):
                cols = line.split("\t")
                if len(cols) >= 10 and "-" not in cols[0] and "." not in cols[0]:
                    upos, feats, deprel = cols[3], cols[5], cols[7]
                    rows.append((upos, deprel, feats))
    rec = flush()
    if rec:
        yield rec


def main() -> None:
    all_sents = list(parse_conllu(CONLLU_PATH))
    tensed = [s for s in all_sents if s[2] in ("Past", "Pres")]
    print(f"parsed {len(all_sents)} sentences total, {len(tensed)} with a Past/Pres VERB tense")

    # group consecutive (in file order) tensed sentences that share a newdoc id into passages
    by_doc: dict = {}
    order = []
    for doc, text, tense in tensed:
        if doc not in by_doc:
            by_doc[doc] = []
            order.append(doc)
        by_doc[doc].append((text, tense))

    docs_with_enough = [d for d in order if len(by_doc[d]) >= SENTS_PER_PASSAGE]
    # even index-spread across the FULL doc list (not a fixed small stride) so the sample
    # reaches multiple genres instead of clustering on whichever genre appears first in the file.
    n_avail = len(docs_with_enough)
    if n_avail <= N_PASSAGES:
        picked_docs = docs_with_enough
    else:
        picked_docs = [docs_with_enough[round(i * (n_avail - 1) / (N_PASSAGES - 1))]
                       for i in range(N_PASSAGES)]
        picked_docs = list(dict.fromkeys(picked_docs))  # dedupe, preserve order

    passages = []
    for i, doc in enumerate(picked_docs):
        items = by_doc[doc][:SENTS_PER_PASSAGE]
        genre_guess = doc.split("-")[0] if "-" in doc else doc.split(".")[0]
        passages.append({
            "passage_id": f"unproduced_{i:02d}",
            "genre": genre_guess,
            "sentences": [t for t, _ in items],
            "tenses": [tn for _, tn in items],
        })

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    n_sent = sum(len(p["sentences"]) for p in passages)
    print(f"wrote {len(passages)} passages / {n_sent} sentences -> {OUT_PATH}")
    for p in passages:
        print(f"  {p['passage_id']} [{p['genre']}] tenses={p['tenses']}")


if __name__ == "__main__":
    main()
