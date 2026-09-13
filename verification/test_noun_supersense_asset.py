"""WITNESS: the noun-supersense FOUNDATION asset (offline export) reproduces the former read-time WordNet lookup -- on every noun of
UD-EWT test (gold NOUN/PROPN/PRON tokens) the organ's noun_supersense() equals synsets(morphy(w,'n'))[0].lexname() -- and the read
is a dictionary lookup (no nltk import on the path). Run: python verification/test_noun_supersense_asset.py"""
import os, sys, time
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.typed_selectional_preference as TSP
from hdlab import morphology as gbm
from tools.build_attachment_validities import sentences, TEST

def main():
    test = sentences(TEST, cap=700, maxlen=10**6)
    words = sorted({t.lower().strip(".,;:'\"") for toks, pos, _, _ in test for t, p in zip(toks, pos) if p in ("NOUN", "PROPN", "PRON")})
    t0 = time.perf_counter(); ours = {w: TSP.noun_supersense(w) for w in words}; t_ours = time.perf_counter() - t0
    from nltk.corpus import wordnet as wn
    def ref(wl):
        if wl in TSP._PRON_PERSON:
            return "noun.person"
        lem = gbm.morphy(wl, "n") or wl
        syns = wn.synsets(lem, pos=wn.NOUN)
        return syns[0].lexname() if syns else None
    t0 = time.perf_counter(); theirs = {w: ref(w) for w in words}; t_ref = time.perf_counter() - t0
    diff = [(w, ours[w], theirs[w]) for w in words if ours[w] != theirs[w]]
    typed = sum(1 for w in words if ours[w])
    src = open(os.path.join(REPO, "hdlab", "typed_selectional_preference.py"), encoding="utf-8").read()
    no_nltk = "from nltk" not in src.split("def noun_supersense")[1].split("class TypedSelectionalPreference")[0]
    print(f"words {len(words)} | typed {typed} | mismatches {len(diff)} | asset read {t_ours:.2f}s vs wordnet {t_ref:.2f}s | no nltk on the read: {no_nltk}")
    for d in diff[:8]:
        print("MISMATCH", d)
    ok = not diff and no_nltk
    print("PASS" if ok else "FAIL"); return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
