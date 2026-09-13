"""OFFLINE FOUNDATION EXPORT (2026-09-13): every WordNet noun lemma -> its most-frequent-sense SUPERSENSE (the lexicographer file
name, e.g. 'noun.person'), written once to data/frontend_assets/noun_supersense_mfs_v1.json so the typed-plausibility organ
(hdlab/typed_selectional_preference.noun_supersense) reads a DICT at inference instead of importing nltk.corpus.wordnet at read
time (an off-the-shelf tool on the live path = a defect that blocks; it was also the heads rung's cold cost: ~0.8 s/sentence).
Same regime as the glass-box morphology export: the knowledge foundation is built offline from the tool, the runtime is glass-box.
Usage: python tools/build_noun_supersense_asset.py  (needs nltk + the wordnet corpus ONLY here, never at inference)"""
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "data", "frontend_assets", "noun_supersense_mfs_v1.json")


def main() -> int:
    from nltk.corpus import wordnet as wn
    t0 = time.time(); table = {}
    for syn in wn.all_synsets(pos=wn.NOUN):
        for lem in syn.lemma_names():
            key = lem.lower()
            if key in table:
                continue
            # MFS = the first synset wn.synsets(lemma, NOUN) returns (WordNet's sense order); resolve exactly as the runtime did
            syns = wn.synsets(key, pos=wn.NOUN)
            if syns:
                table[key] = syns[0].lexname()
    doc = {"source": "WordNet 3.0 via nltk, exported offline by tools/build_noun_supersense_asset.py; value = lexname of the first "
                     "noun synset of the lemma (most frequent sense), keys lowercased lemma names (underscores kept)",
           "n_lemmas": len(table), "supersenses": sorted(set(table.values())), "table": table}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=0, sort_keys=True)
    print(json.dumps({"asset": os.path.relpath(OUT, REPO), "n_lemmas": len(table), "n_supersenses": len(doc["supersenses"]),
                      "bytes": os.path.getsize(OUT), "elapsed_s": round(time.time() - t0, 1)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
