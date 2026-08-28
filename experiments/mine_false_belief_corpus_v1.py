"""mine_false_belief_corpus_v1 -- mine candidate PERCEPTUAL-ACCESS windows from LitBank (100 novels).

Pulls short windows around HIGH-PRECISION dramatic-irony / perceptual-access markers that name a character
(a proper noun), for MANUAL curation into a corpus false-belief / perceptual-access gold. The narrator's
epistemic/perception statement is the LABEL (observed vs not-observed); the extractors are tested on the
surrounding SPATIAL/PRESENCE prose. Markers chosen to be about a CHARACTER'S KNOWLEDGE of an EVENT, filtering
the idiom/dialogue noise the raw counts carry.

NOT the deliverable gold -- a candidate dump. Writes to data/mine_false_belief_corpus_v1/candidates.jsonl.
ASCII only. Read-only over data/litbank/original.
"""
from __future__ import annotations
import os, re, glob, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(REPO, "data", "litbank", "original")
OUT = os.path.join(REPO, "data", "mine_false_belief_corpus_v1")

NAME = r"(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"  # a proper-noun character surface (1-2 caps tokens)

# (label, precision-tier, pattern). label True=observed(knew/saw), False=not-observed(ignorant/absent/occluded).
MARKERS = [
    (False, "irony", rf"\bunbeknown(?:st)?\s+to\s+({NAME})"),
    (False, "irony", rf"\bunknown\s+to\s+({NAME})"),
    (False, "irony", rf"\bwithout\s+({NAME})'s\s+knowledge\b"),
    (False, "absence", rf"\bin\s+({NAME})'s\s+absence\b"),
    (False, "absence", rf"\bduring\s+({NAME})'s\s+absence\b"),
    (False, "absence", rf"\bwhile\s+({NAME})\s+was\s+(?:away|out|gone|absent|asleep|abed|abroad)\b"),
    (False, "occlusion", rf"\bunseen\s+by\s+({NAME})"),
    (False, "occlusion", rf"\bunobserved\s+by\s+({NAME})"),
    (False, "ignorant", rf"\b({NAME})\s+(?:did\s+not|never)\s+(?:see|notice|perceive|observe|suspect|know|dream|guess)\b"),
    (False, "ignorant", rf"\b({NAME})\s+(?:knew|dreamed|suspected)\s+nothing\b"),
    (False, "ignorant", rf"\blittle\s+did\s+({NAME})\s+(?:know|dream|suspect|think)\b"),
    (True, "witness", rf"\b({NAME})\s+(?:watched|beheld|observed|witnessed|saw)\b"),
    (True, "witness", rf"\bbefore\s+({NAME})'s\s+(?:eyes|face|very eyes)\b"),
    (True, "witness", rf"\bin\s+({NAME})'s\s+presence\b"),
]

# an EVENT/CHANGE hint near the marker (a concrete happening the character may or may not perceive)
EVENT_HINT = re.compile(
    r"\b(moved|move|took|take|carried|carry|placed|place|put|hid|hide|removed|remove|stole|steal|slipped|"
    r"changed|change|left|entered|came|went|opened|shut|brought|fell|dropped|turned|seized|snatched|"
    r"crept|arrived|departed|died|struck|threw|pushed|pulled|locked|unlocked|written|wrote|sent)\b", re.I)


def sents_of(txt):
    txt = re.sub(r"\s+", " ", txt)
    return re.split(r"(?<=[.!?\"])\s+(?=[A-Z\"'])", txt)


def run():
    files = sorted(glob.glob(os.path.join(ORIG, "*.txt")))
    os.makedirs(OUT, exist_ok=True)
    cands = []
    for f in files:
        book = os.path.basename(f)
        txt = open(f, encoding="utf-8", errors="ignore").read()
        sents = sents_of(txt)
        for i, s in enumerate(sents):
            for label, tier, pat in MARKERS:
                m = re.search(pat, s)
                if not m:
                    continue
                name = m.group(1)
                # 3-sentence window: the marker sentence + one before + one after (the event context)
                lo, hi = max(0, i - 1), min(len(sents), i + 2)
                window = " ".join(sents[lo:hi]).strip()
                if len(window) < 60 or len(window) > 700:
                    continue
                # require a concrete event hint in the window (filters "I never saw him" style non-events)
                if not EVENT_HINT.search(window):
                    continue
                # skip dialogue-dominated windows (quote marks dominate) -- perceptual access needs narration
                if window.count('"') + window.count("'") >= 6:
                    continue
                cands.append({"book": book, "sent_idx": i, "name": name, "label_observed": label,
                              "tier": tier, "marker": m.group(0), "window": window})
    # dedupe by (book, window)
    seen = set(); uniq = []
    for c in cands:
        k = (c["book"], c["window"][:80])
        if k in seen:
            continue
        seen.add(k); uniq.append(c)
    with open(os.path.join(OUT, "candidates.jsonl"), "w", encoding="utf-8") as fh:
        for c in uniq:
            fh.write(json.dumps(c) + "\n")
    from collections import Counter
    by_tier = Counter((c["tier"], c["label_observed"]) for c in uniq)
    print(f"novels={len(files)}  raw={len(cands)}  unique candidates={len(uniq)}")
    for (tier, lab), n in sorted(by_tier.items()):
        print(f"  {tier:10s} observed={lab!s:5s} {n:4d}")
    print(f"wrote {OUT}/candidates.jsonl")


if __name__ == "__main__":
    run()
