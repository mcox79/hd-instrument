"""Scaffold-free witness for exp_cmrole_agent_board_v1 -- the brain-foundational Competition-Model AGENT
role assigner that recovers the board's who-did-what AGENT arm after referent_per_np went default-ON.

Two independent checks:
  A. MECHANISM CANARY (fast, deterministic, corpus-free): the CM agent competition MUST resolve hand-built
     canonical sentences correctly AND differ from the positional rule -- proving the mechanism is real and
     non-vacuous independent of the corpus (the HARD_FAIL-cell discipline: arms-must-differ witness).
  B. BOARD ORDERINGS (8 LitBank docs, the live scorer): the regression is real, the CM-over-tracked-set
     recovers to >= the pre-referent baseline, the DENSE agent set does NOT, the info-free twin loses, and
     the PATIENT is byte-identical (the +0.336 preserved).

Run: .venv/Scripts/python.exe verification/test_cmrole_agent_board_organ.py
"""
import os
import sys

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.pos_tagger import PosTagger
from hdlab.situation_reader import _FRONTEND_POS_ASSET, _assign_roles, _sentence_nominals
from experiments.exp_cmrole_agent_board_v1 import cm_agent_pick, AGENT_W, _reader, _score_doc

_PASS = []


def _ok(name, cond, detail=""):
    _PASS.append(bool(cond))
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("  -- " + detail) if detail else ""))


def _noms(toks, heads_positions, cluster_of=None):
    """Build tracked-mention dicts (freq>=2 so the givenness cue is uniform and the OTHER cues decide)."""
    return [{"head": toks[p].lower(), "wtok_start": p, "cluster": (cluster_of or {}).get(p, p),
             "is_pronoun": False} for p in heads_positions]


def canary():
    print("A. MECHANISM CANARY (corpus-free; CM must be correct AND differ from positional)")
    tagger = PosTagger.load(_FRONTEND_POS_ASSET)
    gaz = SITQA.load_given_gazetteer()
    cf = {}  # give every candidate freq 2 (uniform salience) so word-order/animacy/voice/core_arg decide

    # (tokens, verb_idx, candidate_positions, gold_agent, must_differ_from_positional, note)
    cases = [
        ("in the morning the captain sailed away .".split(), 5, [2, 4], "captain", False,
         "PP-governed sentence-initial 'morning' loses to the core subject 'captain' (clause-locality)"),
        ("the letter was written by mary .".split(), 3, [1, 5], "mary", True,
         "PASSIVE voice flip: agent = the by-phrase 'mary', not the surface subject 'letter'"),
        ("the ship of the line fired .".split(), 5, [1, 4], "ship", True,
         "'line' is PP-governed by 'of' -> the head 'ship' is the subject (positional grabs 'line')"),
        ("the dog chased the cat .".split(), 2, [1, 4], "dog", False,
         "canonical SVO: preverbal 'dog' is the agent"),
    ]
    for toks, v0, cand_pos, gold, must_differ, note in cases:
        up = tagger.tag(list(toks))
        noms = _noms(toks, cand_pos, {p: p for p in cand_pos})
        pos, pt = _assign_roles(v0, noms, lemma=toks[v0])   # positional agent + patient (stock rule)
        cm = cm_agent_pick(toks, up, v0, noms, pt, gaz, AGENT_W, cluster_freq={p: 2 for p in cand_pos})
        cond = (cm == gold) and (cm != pos if must_differ else True)
        _ok("canary: %s" % " ".join(toks), cond,
            "CM=%r gold=%r positional=%r%s | %s"
            % (cm, gold, pos, " (must differ)" if must_differ else "", note))


def board(n_docs=8):
    print("\nB. BOARD ORDERINGS (%d LitBank docs, live who-did-what AGENT scorer)" % n_docs)
    gaz = SITQA.load_given_gazetteer()
    import json
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    docs = SITQA.load_docs(n_docs)
    docset = [d for d in docs if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    acc, pat = {}, {}
    for arm in ("pos_OFF", "pos_ON", "cm_dense", "cm_ON", "twin_ON"):
        per, sigs = [], []
        for doc in docset:
            path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
            sm = _reader(arm, gaz).read(path)
            c, ps = _score_doc(sm, wdw[doc])
            per += c; sigs.append(ps)
        acc[arm] = float(np.mean(per)); pat[arm] = sigs
        print("    %-9s acc=%.4f" % (arm, acc[arm]))
    _ok("regression is real (pos_ON < pos_OFF)", acc["pos_ON"] < acc["pos_OFF"] - 0.05,
        "pos_ON=%.4f pos_OFF=%.4f" % (acc["pos_ON"], acc["pos_OFF"]))
    _ok("CM-over-tracked recovers >= baseline", acc["cm_ON"] >= acc["pos_OFF"] - 0.02,
        "cm_ON=%.4f pos_OFF=%.4f" % (acc["cm_ON"], acc["pos_OFF"]))
    _ok("recovery over regression is large", acc["cm_ON"] > acc["pos_ON"] + 0.10,
        "cm_ON=%.4f pos_ON=%.4f" % (acc["cm_ON"], acc["pos_ON"]))
    _ok("DENSE agent set does NOT recover (set matters)", acc["cm_dense"] < acc["cm_ON"] - 0.05,
        "cm_dense=%.4f cm_ON=%.4f" % (acc["cm_dense"], acc["cm_ON"]))
    _ok("info-free twin loses (cues carry info)", acc["twin_ON"] < acc["cm_ON"] - 0.02,
        "twin=%.4f cm_ON=%.4f" % (acc["twin_ON"], acc["cm_ON"]))
    _ok("PATIENT byte-identical (cm_ON == pos_ON; +0.336 preserved)",
        all(pat["cm_ON"][i] == pat["pos_ON"][i] for i in range(len(docset))))


if __name__ == "__main__":
    canary()
    board()
    n = len(_PASS); k = sum(_PASS)
    print("\n%d/%d PASS" % (k, n))
    sys.exit(0 if k == n else 1)
