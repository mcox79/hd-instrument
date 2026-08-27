"""VETTED loaders for the modern contextual-sense benchmarks acquired 2026-08-26.

WHY THIS EXISTS: `the_meaning_win_is_offline_context_free_and_unwired` (integrated
2026-08-26, PARTIAL) found that whether CONTEXT can override the frequency PRIOR for a
word's SUBORDINATE (rarer) sense is UN-TESTABLE on the ~200-year-old McGuffey corpus,
because there each subordinate sense is attested ~ONCE (prototype n=6). These benchmarks
remove that data block. Use a VETTED loader rather than re-deriving the parse (the first
hand-rolled SemCor parse returned 0 mentions -- the nltk Tree label must be `.label()`
then `.synset()`; that bug is fixed here).

ASSETS
  - SemCor      : sense-tagged running text (WordNet senses). THE key asset -- subordinate
                  senses attested MANY times in real sentences (`point` 9 subordinate
                  senses each >=2x; `field` 10; `light` 8). Via nltk_data (user home),
                  NOT in the repo: `python -c "import nltk; nltk.download('semcor'); nltk.download('wordnet'); nltk.download('omw-1.4')"`.
  - WiC         : modern balanced BINARY contextual-sense benchmark (same-sense? T/F),
                  human-judged. In-repo at data/wsd_benchmarks/{train,dev,test}/.
                  5428 / 638 / 1400 pairs, perfectly balanced, 1200+ distinct target lemmas.
  - SCWS        : graded contextual word-similarity (the continuous-modulation frame) --
                  NOT acquired; its canonical Stanford/HF mirrors are dead (404/401) as of
                  2026-08-26. Optional follow-up; needs a deliberate mirror hunt.

DISCIPLINE REMINDERS (from BRAIN_FOUNDATIONAL_AUDIT.md / STATUS.md):
  - Grade meaning on HUMAN judgement (WiC labels / graded human sim), NOT taxonomic WordNet
    distance. SemCor's WordNet senses are the SENSE INVENTORY + the source of multiply-
    attested contexts, NOT the scorer.
  - Recompute every floor on the scored population; no number crosses populations/scorers.
  - Restrict to GROUNDED-COVERED targets when comparing to the grounded read-out (the
    submission's requirement); compute that overlap against the grounded norms vocab first.
"""
from __future__ import annotations

import os
from collections import defaultdict, Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
WIC_BASE = os.path.join(_REPO, "data", "wsd_benchmarks")


def load_wic(split="dev", base=WIC_BASE):
    """Return a list of dicts for a WiC split.

    Each item: {lemma, pos, idx1, idx2, sent1, sent2, gold} where gold is True (same
    sense), False (different), or None if the gold file is absent (the test gold is
    withheld upstream in some releases; here all three ship gold).
    """
    dp = os.path.join(base, split, f"{split}.data.txt")
    gp = os.path.join(base, split, f"{split}.gold.txt")
    if not os.path.exists(dp):
        raise FileNotFoundError(f"WiC split not found: {dp}")
    golds = None
    if os.path.exists(gp):
        golds = [l.strip() for l in open(gp, encoding="utf-8") if l.strip() != ""]
    out = []
    for i, line in enumerate(open(dp, encoding="utf-8")):
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        lemma, pos, idx, s1, s2 = parts[0], parts[1], parts[2], parts[3], parts[4]
        try:
            i1, i2 = (int(x) for x in idx.split("-"))
        except ValueError:
            i1 = i2 = -1
        g = None
        if golds is not None and i < len(golds):
            g = True if golds[i] == "T" else (False if golds[i] == "F" else None)
        out.append({"lemma": lemma, "pos": pos, "idx1": i1, "idx2": i2,
                    "sent1": s1, "sent2": s2, "gold": g})
    return out


def semcor_sense_contexts(max_files=None, tag="sem"):
    """lemma(str) -> {synset_name: [list of context sentences (token lists)]}.

    Correct nltk parse: each sense-tagged chunk is an nltk.tree.Tree whose `.label()`
    is a WordNet Lemma; `.label().synset()` is the synset. Only chunks with a synset
    label are kept. The first token of the chunk (lowercased) keys the lemma.
    """
    from nltk.corpus import semcor
    from nltk.tree import Tree
    files = semcor.fileids()
    if max_files is not None:
        files = files[:max_files]
    lemma_sense_ctx = defaultdict(lambda: defaultdict(list))
    for fn in files:
        try:
            sents = semcor.tagged_sents(fn, tag=tag)
        except Exception:
            continue
        for sent in sents:
            # flat token list for the whole sentence (context)
            flat = []
            for ch in sent:
                flat.extend(ch.leaves() if isinstance(ch, Tree) else ch)
            for chunk in sent:
                if not isinstance(chunk, Tree):
                    continue
                lab = chunk.label()
                if not hasattr(lab, "synset"):
                    continue
                try:
                    syn = lab.synset()
                except Exception:
                    continue
                if syn is None:
                    continue
                words = chunk.leaves()
                if not words:
                    continue
                key = words[0].lower()
                lemma_sense_ctx[key][syn.name()].append(flat)
    return lemma_sense_ctx


def _vet():
    print("== WiC ==")
    for sp in ("train", "dev", "test"):
        rows = load_wic(sp)
        gold = Counter(str(r["gold"]) for r in rows)
        lem = len({r["lemma"] for r in rows})
        print(f"  {sp:5s}: {len(rows):5d} pairs | {lem:4d} lemmas | gold {dict(gold)}")
    print("== SemCor (first 80 files) ==")
    lsc = semcor_sense_contexts(max_files=80)
    multi3 = sum(1 for w, d in lsc.items() if len(d) >= 3)
    total = sum(len(v) for d in lsc.values() for v in d.values())
    print(f"  sense-tagged mentions: {total} | lemmas with >=3 senses in context: {multi3}")
    for w in ("point", "field", "light", "line"):
        if w in lsc:
            counts = sorted((len(v) for v in lsc[w].values()), reverse=True)
            sub = sum(1 for c in counts[1:] if c >= 2)
            print(f"    {w:6s}: {len(counts)} senses; counts={counts[:8]}; subordinate>=2x: {sub}")


if __name__ == "__main__":
    _vet()
