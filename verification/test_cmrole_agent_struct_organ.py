"""Scaffold-free witness for the register-general incremental STRUCTURE cue (the embedded-clause AGENT tie
residual). Writes NOTHING to any landed data dir. Run:

    .venv/Scripts/python.exe verification/test_cmrole_agent_struct_organ.py

Checks, in order:
  1. CANARY -- the structure cue reproduces hdlab.incremental_parser.incremental_build's subject bind, and
     the RC-pop upgrade re-attaches the MATRIX subject after a relative clause.
  2. BOARD -- on a few LitBank docs, the structure cue BEATS the live full-P2-stack competition on the
     embedded-clause TIE slice, the shuffled-structure twin LOSES, and the canonical slice does NOT regress.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.candidate_generator import NOMINAL
from hdlab.incremental_parser import incremental_build
from hdlab.coref import parse_litbank_conll
from hdlab.scene_segment import parse_conll_sentences
from experiments.exp_cmrole_agent_struct_v1 import (
    incremental_subject_before, _questions_full, classify_slice, _reader as _reader_v1,
)
from experiments.exp_cmrole_agent_struct_v2 import incremental_subject_rcpop, _is_animate_fixed
from experiments.exp_cmrole_agent_board_v1 import _nominals_keep_pron, NOMINATIVE_PRON
from experiments.exp_cmrole_agent_readout_v1 import answer_instanced

FAILS = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (("  -- " + detail) if detail else ""))
    if not cond:
        FAILS.append(name)


def canary():
    print("[1] CANARY: structure cue == incremental_build subject bind; RC-pop re-attaches matrix subject")
    # subj_before matches incremental_build's subj at each verb
    toks = ["the", "man", "who", "saw", "the", "boy", "ran", "."]
    pos = ["DET", "NOUN", "PRON", "VERB", "DET", "NOUN", "VERB", "PUNCT"]
    sb = incremental_subject_before(toks, pos)
    frames = incremental_build(toks, pos, use_predict=False)
    buf, exp = [], {}
    for i in range(len(toks)):
        if pos[i] == "VERB":
            exp[i] = buf[-1] if buf else None
        if pos[i] in NOMINAL:
            buf.append(i); buf = buf[-3:]
    for v in [i for i, t in enumerate(pos) if t == "VERB"]:
        check("left-corner subj@%d matches incremental_build" % v, sb[v] == exp[v], "got %s exp %s" % (sb[v], exp[v]))
    # incremental_build returns 1-BASED verb indices (per its docstring); exp keys are 0-based
    check("incremental_build produced a frame for each verb", all((v + 1) in frames for v in exp),
          "frames=%s exp_verbs(0-based)=%s" % (sorted(frames), sorted(exp)))
    # RC-pop re-attaches the matrix subject ("ran" -> man, not boy)
    rc = incremental_subject_rcpop(toks, pos)
    check("RC-pop: matrix 'ran' binds 'man' (flat left-corner binds 'boy')", rc[6] == 1 and sb[6] == 5,
          "rcpop=%s flat=%s" % (rc[6], sb[6]))
    # object relative + embedded complement
    t2 = ["the", "man", "whom", "the", "boy", "saw", "ran", "."]
    p2 = ["DET", "NOUN", "PRON", "DET", "NOUN", "VERB", "VERB", "PUNCT"]
    check("RC-pop object-relative: 'ran' binds 'man'", incremental_subject_rcpop(t2, p2)[6] == 1)
    check("upstream animacy fix: 'people' -> animate", _is_animate_fixed("people", "NOUN", None) == 1.0)


def board():
    print("[2] BOARD: structure cue beats the live competition on the tie slice; twin loses; canon no-regress")
    gaz = SITQA.load_given_gazetteer()
    import json
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    docs = [d for d in SITQA.load_docs(6) if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    arms = ["base", "struct", "twin_struct"]
    per = {a: {"tie": [], "canon": []} for a in arms}
    for doc in docs:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        sents = parse_conll_sentences(path)
        coref, ncoref = parse_litbank_conll(path, name_gender_map=gaz)
        psf = _nominals_keep_pron(coref, ncoref)
        pcf = [[m for m in lst if (not m.get("is_pronoun")) or m["head"].lower() in NOMINATIVE_PRON] for lst in psf]
        qs = _questions_full(wdw[doc])
        labels = [classify_slice(q, sents, pcf, gaz) for q in qs]
        for a in arms:
            sm = _reader_v1(a, gaz).read(path)
            for q, lab in zip(qs, labels):
                if not lab.get("valid"):
                    continue
                c = int(SITQA._match(answer_instanced(sm, q), q["gold"], "events"))
                per[a]["tie" if lab["tie"] else "canon"].append(c)
    acc = {a: {k: (float(np.mean(per[a][k])) if per[a][k] else float("nan")) for k in per[a]} for a in arms}
    print("     tie:   base=%.3f struct=%.3f twin=%.3f  (n=%d)"
          % (acc["base"]["tie"], acc["struct"]["tie"], acc["twin_struct"]["tie"], len(per["base"]["tie"])))
    print("     canon: base=%.3f struct=%.3f              (n=%d)"
          % (acc["base"]["canon"], acc["struct"]["canon"], len(per["base"]["canon"])))
    check("struct > base on the tie slice", acc["struct"]["tie"] > acc["base"]["tie"] + 1e-9)
    check("struct > shuffled-structure twin on the tie slice", acc["struct"]["tie"] > acc["twin_struct"]["tie"] + 1e-9)
    check("struct does NOT regress the canonical slice", acc["struct"]["canon"] >= acc["base"]["canon"] - 1e-9)


if __name__ == "__main__":
    canary()
    board()
    print("\n%d checks failed" % len(FAILS) if FAILS else "\nALL CHECKS PASS")
    sys.exit(1 if FAILS else 0)
