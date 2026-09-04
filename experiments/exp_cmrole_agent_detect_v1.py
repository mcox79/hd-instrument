"""NEXT-FOCUS PROBE (owner push on the 47.8% bucket): the biggest post-structure residual is (~58%) event
DETECTION @ the queried sentence (predicate not detected / lemma mismatch, often have/be copulas), and (~40%)
the competition picking the wrong agent at a detected event. Two EXISTING, glass-box levers, measured end-to-end
on the board who-did-what AGENT arm (structure cue ON as the baseline):
  predicate_recall  -- the landed register-robust event-recovery organ (default OFF; promotes tagger-dropped
                       verbs with a WordNet verb-reading back to events; hdlab.predicate_detector). Addresses
                       the DETECTION half.
  animacy_fix       -- the collective-human animacy coverage patch (section 6). Addresses part of the
                       competition half (people/crowd mislabelled inanimate flip the agent cue).

Run: .venv/Scripts/python.exe experiments/exp_cmrole_agent_detect_v1.py [--nboot 2000]
"""
from __future__ import annotations
import argparse, json, os, sys, time
from datetime import datetime, timezone
import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.coref import parse_litbank_conll
from hdlab.scene_segment import parse_conll_sentences
from experiments.exp_cmrole_agent_board_v1 import AGENT_W, _boot, _nominals_keep_pron, NOMINATIVE_PRON
from experiments.exp_cmrole_agent_readout_v1 import answer_instanced
from experiments.exp_cmrole_agent_struct_v1 import StructAgentReader, _questions_full, classify_slice
from experiments.exp_cmrole_agent_struct_v2 import StructV2Reader

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_detect_v1")


def _reader(arm, gaz):
    common = dict(gaz=gaz, role_route="positional", referent_per_np=True, cm_weights=AGENT_W, cm_gaz=gaz,
                  agent_source="coref", include_pron_agents=True, clause_local=True, case_filter=True)
    if arm == "struct":
        return StructAgentReader(struct=True, **common)
    if arm == "struct_predrec":
        return StructAgentReader(struct=True, predicate_recall=True, **common)
    if arm == "struct_animfix":
        return StructV2Reader(animacy_fix=True, **common)
    if arm == "struct_both":
        return StructV2Reader(animacy_fix=True, predicate_recall=True, **common)
    raise ValueError(arm)


ARMS = ["struct", "struct_predrec", "struct_animfix", "struct_both"]


def run(nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    docs = [d for d in SITQA.load_docs(16) if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    per = {a: {"tie": [], "canon": [], "all": []} for a in ARMS}
    for doc in docs:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        sents = parse_conll_sentences(path)
        coref, ncoref = parse_litbank_conll(path, name_gender_map=gaz)
        psf = _nominals_keep_pron(coref, ncoref)
        pcf = [[m for m in lst if (not m.get("is_pronoun")) or m["head"].lower() in NOMINATIVE_PRON] for lst in psf]
        qs = _questions_full(wdw[doc]); labels = [classify_slice(q, sents, pcf, gaz) for q in qs]
        for a in ARMS:
            sm = _reader(a, gaz).read(path)
            b = {"tie": [], "canon": [], "all": []}
            for q, lab in zip(qs, labels):
                if not lab.get("valid"):
                    continue
                c = int(SITQA._match(answer_instanced(sm, q), q["gold"], "events"))
                b["all"].append(c); b["tie" if lab["tie"] else "canon"].append(c)
            for k in b:
                per[a][k].append(np.array(b[k], float))
    acc = {a: {k: float(np.concatenate(per[a][k]).mean()) for k in per[a]} for a in ARMS}
    print("=" * 92)
    print("NEXT-FOCUS PROBE: predicate_recall (detection) + animacy_fix (competition) over the structure cue")
    print("   %-16s %8s %8s %8s" % ("arm", "TIE", "CANON", "ALL"))
    for a in ARMS:
        print("   %-16s %8.4f %8.4f %8.4f" % (a, acc[a]["tie"], acc[a]["canon"], acc[a]["all"]))
    out = {"acc": acc, "tests": {}}
    for lab, a, b, k in [("predrec - struct (ALL)", "struct_predrec", "struct", "all"),
                         ("predrec - struct (TIE)", "struct_predrec", "struct", "tie"),
                         ("animfix - struct (ALL)", "struct_animfix", "struct", "all"),
                         ("both - struct (ALL)", "struct_both", "struct", "all"),
                         ("both - struct (TIE)", "struct_both", "struct", "tie")]:
        d = _boot(per[a][k], per[b][k], nboot, SEED, doc_level=True)
        out["tests"][lab] = d
        print("   %-26s d=%+.4f CI[%+.4f,%+.4f] sep=%s" % (lab, d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    print("=" * 92)
    out.update({"elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()})
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs" % (time.time() - t0))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--nboot", type=int, default=2000)
    run(ap.parse_args().nboot)
