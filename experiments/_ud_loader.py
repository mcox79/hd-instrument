"""Shared CoNLL-U loader for the bundled UD-English-EWT corpus (dep-parser RESCUE-1).
Returns sentences as lists of (id, form, upos, head, deprel). Use to unblock dep-parser / pos_oov without runtime download."""
from pathlib import Path
UD_DIR = Path(__file__).resolve().parent / "data" / "ud_english_ewt"
def load_conllu(split):
    """split in {train,dev,test} -> list of sentences; each sentence = list of (idx:int, form:str, upos:str, head:int, deprel:str)."""
    fp = UD_DIR / ("en_ewt-ud-%s.conllu" % split)
    sents = []; cur = []
    with open(fp, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur: sents.append(cur); cur = []
                continue
            if line.startswith("#"): continue
            c = line.split("\t")
            if len(c) < 8 or "-" in c[0] or "." in c[0]: continue   # skip multiword/empty nodes
            try: idx = int(c[0]); head = int(c[6])
            except Exception: continue
            cur.append((idx, c[1], c[3], head, c[7]))
    if cur: sents.append(cur)
    return sents
