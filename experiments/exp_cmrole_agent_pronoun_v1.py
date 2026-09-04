"""PROTOTYPE: lift the 70%-pronoun ceiling on the board's who-did-what AGENT arm by admitting SUBJECT
PRONOUNS as agent candidates.

The SOLVED fix (exp_cmrole_agent_board_v1) recovered the agent to 0.2519 -- but that is 85% of a hard
ceiling of 0.299, because 70.1% of the gold AGENT heads are PRONOUNS (he/she/they) and the reader's
`_sentence_nominals` filters ALL pronouns out of the role-candidate set, so pronoun-subject golds are
UNREACHABLE for every arm.

BRAIN-FOUNDATIONAL basis (why a pronoun is a legitimate -- indeed the STRONGEST -- agent candidate):
a subject pronoun is the maximally-GIVEN mention of the salient discourse entity. Centering Theory's core
claim is that the backward-looking center (Cb) is realized by the MOST REDUCED expression -- i.e. it is
PRONOMINALIZED (Grosz, Joshi & Weinstein 1995; Gordon 1993 -- the repeated-name penalty is the same fact
from the other side). So a preverbal subject pronoun is the single most given/topical/animate agent
candidate there is. Filtering it out is exactly backwards. Admitting it (and letting the SAME Competition-
Model competition -- preverbal + animate + given -- pick it) is the brain-faithful move.

ARMS (referent_per_np ON except the floor; board scorer, LitBank 19c, load_docs(16)):
  pos_OFF     positional agent, ref OFF                 -> pre-referent baseline (0.2257)
  cm_ON       CM agent over tracked set, NO pronouns    -> the SOLVED fix (0.2519), capped by the pronoun filter
  cm_pron     CM agent over tracked set + SUBJECT PRONOUNS  -> THE PROTOTYPE (lifts the ceiling)
  twin_pron   cm_pron with shuffled cue supports        -> info-free, MUST LOSE

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_pronoun_v1.py [--docs 16] [--nboot 2000]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader
from hdlab.coref import parse_litbank_conll
from experiments.exp_cmrole_agent_board_v1 import CMAgentReader, AGENT_W, _score_doc, _boot

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_pronoun_v1")
_SUBJ_PRON = frozenset(("he", "she", "they", "we", "i", "you", "it"))


def _reader(arm, gaz):
    if arm == "pos_OFF":
        return SituationReader(gaz=gaz, role_route="positional", referent_per_np=False)
    twin = SEED if arm == "twin_pron" else None
    pron = arm in ("cm_pron", "twin_pron")
    return CMAgentReader(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W,
                         cm_gaz=gaz, cm_twin_seed=twin, agent_source="coref", include_pron_agents=pron)


def _ceilings(docset, gaz, wdw):
    """Reachable-gold ceilings: (a) NO-pronoun reader (the old 0.299 ceiling) vs (b) WITH-pronoun reader."""
    n = pron = tracked = new = 0
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        coref, _ = parse_litbank_conll(path, name_gender_map=gaz)
        freq = Counter(m.get("cluster") for m in coref if not m.get("is_pronoun"))
        tracked_heads = {m["head"].lower() for m in coref
                         if not m.get("is_pronoun") and freq.get(m.get("cluster"), 0) >= 2}
        for m in wdw[doc].get("stream", []):
            if m.get("role") != "SUBJECT" or not m.get("gov_verb"):
                continue
            g = str(m["head_text"]).lower(); n += 1
            if g in _SUBJ_PRON or g in ("him", "her", "them", "us", "me"):
                pron += 1
            elif g in tracked_heads:
                tracked += 1
            else:
                new += 1
    return {"n": n, "pron_%": 100 * pron / n, "no_pron_ceiling": (tracked + new) / n,
            "with_pron_ceiling": (tracked + new + pron) / n}


def run(n_docs=16, nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    docs = SITQA.load_docs(n_docs)
    docset = [d for d in docs if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]

    ceil = _ceilings(docset, gaz, wdw)
    arms = ["pos_OFF", "cm_ON", "cm_pron", "twin_pron"]
    per_doc = {a: [] for a in arms}
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        for a in arms:
            sm = _reader(a, gaz).read(path)
            c, _ps = _score_doc(sm, wdw[doc])
            per_doc[a].append(np.array(c, dtype=np.float64))
    acc = {a: float(np.concatenate(per_doc[a]).mean()) for a in arms}
    n = int(sum(len(x) for x in per_doc["cm_ON"]))

    print("=" * 96)
    print("PRONOUN-SUBJECT PROTOTYPE on the board who-did-what AGENT arm")
    print("  LitBank 19c, load_docs(%d), n=%d agent questions   (%.0fs)" % (len(docset), n, time.time() - t0))
    print("-" * 96)
    print("  gold AGENTs that are PRONOUNS: %.1f%%   |   reachable ceiling  no-pronoun=%.4f  WITH-pronoun=%.4f"
          % (ceil["pron_%"], ceil["no_pron_ceiling"], ceil["with_pron_ceiling"]))
    print("-" * 96)
    for a in arms:
        tag = {"pos_OFF": "pre-referent baseline (bar)", "cm_ON": "SOLVED fix (no pronouns, ceiling-capped)",
               "cm_pron": "PROTOTYPE (+ subject pronouns)", "twin_pron": "info-free twin"}[a]
        print("  %-10s acc=%.4f   %s" % (a, acc[a], tag))
    print("-" * 96)
    tests = {}
    for label, a, b in [("cm_pron - cm_ON   (pronouns lift it)", "cm_pron", "cm_ON"),
                        ("cm_pron - pos_OFF (>> baseline now)", "cm_pron", "pos_OFF"),
                        ("cm_pron - twin_pron (beats info-free)", "cm_pron", "twin_pron")]:
        d = _boot(per_doc[a], per_doc[b], nboot, SEED, doc_level=True)
        tests[label] = d
        print("  %-40s d=%+.4f  doc-CI[%+.4f,%+.4f] hw=%.4f p<=0=%.3f sep=%s"
              % (label, d["delta"], d["lo"], d["hi"], d["ci_hw"], d["p_le_0"], d["ci_sep"]))
    print("  pronoun arm reaches %.0f%% of the WITH-pronoun ceiling" % (100 * acc["cm_pron"] / ceil["with_pron_ceiling"]))
    print("=" * 96)

    out = {"anchor_name": "cmrole_agent_pronoun_v1", "n_docs": len(docset), "n_questions": n,
           "acc": acc, "ceilings": ceil, "tests": tests, "elapsed_s": round(time.time() - t0, 1),
           "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs -> %s" % (time.time() - t0, os.path.join(OUT_DIR, "metrics.json")))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", type=int, default=16)
    ap.add_argument("--nboot", type=int, default=2000)
    args = ap.parse_args()
    run(args.docs, args.nboot)
