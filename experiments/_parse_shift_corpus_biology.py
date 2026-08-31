"""One-off: spaCy-parse the modern BIOLOGY textbook (distribution-shift domain for the live-canary) into the
SAME JSONL format as exp_structured_context_learner_v1.parse_and_cache, so S.load_parsed can read it. Modern,
scientific-prose domain distinct from simplewiki general knowledge -- the lifelong-learning stress test
(integrate a new domain without forgetting). Caps at ~1.5M tokens. Writes ONLY to the cell's own data dir."""
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "data", "corpora", "textbook_biology_2e", "cleaned", "biology_2e.clean.txt")
OUT = os.path.join(REPO, "data", "exp_learner_live_canary_continual_growth_v1", "parsed_biology_shift.jsonl")
MAX_TOKENS = 1_500_000


def main():
    if os.path.exists(OUT):
        ntok = 0
        with open(OUT, encoding="utf-8") as fh:
            for ln in fh:
                ntok += len(json.loads(ln))
        if ntok >= MAX_TOKENS * 0.8:
            print("[parse] cache HIT %s (%d tokens)" % (OUT, ntok)); return 0
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    nlp.max_length = 2_000_000
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    t0 = time.time(); ntok = 0; n_sent = 0
    tmp = OUT + ".tmp"
    with open(SRC, encoding="utf-8") as fin, open(tmp, "w", encoding="utf-8") as fout:
        buf = []
        def flush():
            nonlocal ntok, n_sent
            for doc in nlp.pipe(buf, batch_size=64):
                for sent in doc.sents:
                    start = sent[0].i
                    rec = [[t.text.lower(), t.head.i - start, t.dep_, t.pos_] for t in sent if t.text.strip()]
                    if len(rec) >= 2:
                        fout.write(json.dumps(rec) + "\n"); ntok += len(rec); n_sent += 1
            buf.clear()
        for ln in fin:
            ln = ln.strip()
            if ln:
                buf.append(ln)
            if len(buf) >= 2000:
                flush()
                if ntok >= MAX_TOKENS:
                    break
        if buf and ntok < MAX_TOKENS:
            flush()
    os.replace(tmp, OUT)
    print("[parse] wrote %s: %d sent / %d tok in %.0fs" % (OUT, n_sent, ntok, time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
