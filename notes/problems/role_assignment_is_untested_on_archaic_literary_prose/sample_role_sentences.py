"""Emit length-stratified archaic (LitBank) + modern (textbook) sentences with inline token indices,
for blind hand-annotation of the main finite verb's grammatical subject. Deterministic (seeded)."""
import os, sys, re, random, glob, json
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _REPO)
from hdlab.scene_segment import parse_conll_sentences

random.seed(20260829)
BINS = [(8, 15), (15, 25), (25, 40), (40, 70)]
PER_BIN = 14

FINITE = re.compile(r"\b(is|are|was|were|had|has|have|did|does|said|came|went|saw|took|made|"
                    r"gave|told|found|knew|thought|looked|turned|stood|sat|ran|fell|held|"
                    r"began|felt|seemed|grew|spoke|cried|walked|opened|left|met|heard|"
                    r"would|could|should|must|will|shall)\b", re.I)


def stratify(sents, tag):
    buckets = {b: [] for b in BINS}
    for toks in sents:
        n = len(toks)
        txt = " ".join(toks)
        if not any(lo <= n < hi for lo, hi in BINS):
            continue
        if not FINITE.search(txt):          # needs a plausible finite main verb
            continue
        if sum(c.isalpha() for c in txt) < n:  # skip heading/number-heavy
            continue
        if txt.isupper():
            continue
        for lo, hi in BINS:
            if lo <= n < hi:
                buckets[(lo, hi)].append(txt)
    out = []
    for b in BINS:
        random.shuffle(buckets[b])
        for txt in buckets[b][:PER_BIN]:
            out.append({"src": tag, "len_bin": f"{b[0]}-{b[1]}", "text": txt})
    return out


def split_modern(path, limit=4000):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    raw = re.sub(r"#+ .*", " ", raw)           # drop markdown headings
    raw = re.sub(r"\s+", " ", raw)
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", raw)
    out = []
    for s in sents[:limit]:
        toks = s.split()
        if 8 <= len(toks) < 70:
            out.append(toks)
    return out


# archaic: several LitBank novels
arch_sents = []
for fp in sorted(glob.glob(os.path.join(_REPO, "data", "corpora", "litbank_coref_conll", "*.conll")))[:12]:
    try:
        arch_sents += parse_conll_sentences(fp)
    except Exception:
        pass
archaic = stratify(arch_sents, "archaic_litbank")

# modern: two OpenStax textbooks
mod_sents = []
for tb in ["textbook_biology_2e", "textbook_psychology_2e"]:
    p = os.path.join(_REPO, "data", "corpora", tb, "cleaned")
    for f in glob.glob(os.path.join(p, "*.clean.txt")):
        mod_sents += split_modern(f)
modern = stratify(mod_sents, "modern_textbook")

out = os.path.join(_REPO, "scratch", "role_candidates.txt")
with open(out, "w", encoding="utf-8") as f:
    for tag, items in [("ARCHAIC", archaic), ("MODERN", modern)]:
        f.write(f"\n===== {tag} (n={len(items)}) =====\n")
        for i, it in enumerate(items):
            toks = it["text"].split()
            indexed = " ".join(f"{j}:{t}" for j, t in enumerate(toks))
            f.write(f"[{tag[:4]}-{i:02d}] bin={it['len_bin']} src={it['src']}\n  {indexed}\n")
# also dump machine-readable
with open(os.path.join(_REPO, "scratch", "role_candidates.jsonl"), "w", encoding="utf-8") as f:
    for tag, items in [("archaic", archaic), ("modern", modern)]:
        for i, it in enumerate(items):
            it["cid"] = f"{tag[:4]}-{i:02d}"
            f.write(json.dumps(it) + "\n")
print(f"archaic={len(archaic)} modern={len(modern)} -> {out}")
