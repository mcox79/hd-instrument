"""PROBE v20 (heads rung, lever 1 = EXPERIENCE VOLUME): the attachment cue-competition learner (probe v18's AttachmentCompetition)
accrues its soft arc counts from MANY MORE sentences -- modern Simple-Wikipedia lines tagged by the substrate's own tagger (the
categories rung's stand-in until the reading-induced categories hand down a usable functional inventory) -- with the teacher's
(treebank-free cached scorer's) tree posterior as the outcome signal, then one anchored self-teaching round.
Budgets swept: UD-EWT 6k sentences (the v18 baseline) vs 20k / 60k Simple-Wiki sentences. UAS on UD-EWT test (700, gold
categories, reference only); adjacent-right floor; twin = shuffled strengths at the largest budget.
Run: .venv/Scripts/python.exe experiments/probe_attachment_scale_reading_v20.py [--budgets 20000,60000]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import argparse
import json
import pickle
import sys
import time

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.probe_attachment_competition_v18 as V18
import experiments.probe_parse_rung_loss_affected_entity_v11 as V11
from experiments.exp_parser_graded_decode_regimes_v1 import load_ud, UD_TRAIN, UD_TEST
from experiments.exp_parser_selfsup_em_v1 import _adj_right_uas
from experiments.exp_reading_induced_categories_v1 import SIMPLEWIKI, _TOK
from hdlab.graded_parser import single_root_marginals


def wiki_sentences(n, tagger, minlen=4, maxlen=30):
    """Simple-Wiki lines -> (idx, form, UPOS, 0, '_') tuples with the substrate tagger (cased tokens for the tagger)."""
    out = []
    with open(SIMPLEWIKI, encoding="utf-8", errors="ignore") as f:
        for line in f:
            toks = [m.group(0) for m in _TOK.finditer(line.strip())]
            if not (minlen <= len(toks) <= maxlen):
                continue
            pos = list(tagger.tag(toks))
            out.append([(i + 1, toks[i], pos[i], 0, "_") for i in range(len(toks))])
            if len(out) >= n:
                break
    return out


def learn(train, teacher, frames, alpha=0.5, log=print):
    stu = V18.AttachmentCompetition(frames)
    for s in train:
        toks = [x[1] for x in s]; pos = [x[2] for x in s]
        A, n = teacher._score_matrix(toks, pos)
        stu.accrue(toks, pos, single_root_marginals(A, n, 1.0))
    stu.finalize()
    r0 = stu
    nxt = V18.AttachmentCompetition(frames)
    for s in train:
        toks = [x[1] for x in s]; pos = [x[2] for x in s]
        A, n = teacher._score_matrix(toks, pos); mt = single_root_marginals(A, n, 1.0); ms = r0.marginals(toks, pos)
        mix = {j: {h: alpha * ms.get(j, {}).get(h, 0.0) + (1 - alpha) * mt.get(j, {}).get(h, 0.0)
                   for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
        nxt.accrue(toks, pos, mix)
    return r0, nxt.finalize()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--budgets", default="20000,60000"); a = ap.parse_args()
    t0 = time.time()
    tg, _, _ = V11._fe()
    test = load_ud(UD_TEST, cap=700)
    teacher = pickle.load(open(V18.TEACHER, "rb"))
    floor = _adj_right_uas([[(i + 1, "x", p, {x[0]: x[3] for x in s}.get(i + 1, 0), "_") for i, p in enumerate([x[2] for x in s])] for s in test])[0]
    out = {"floor": round(floor, 4), "teacher": round(V18.uas(teacher.parse_cle, test), 4), "arms": []}
    print("floor", out["floor"], "teacher", out["teacher"], flush=True)
    ud = load_ud(UD_TRAIN, cap=6000, maxlen=40)
    frames = V18.verb_frames(ud)
    r0, r1 = learn(ud, teacher, frames)
    row = {"source": "UD-EWT train 6k (tagged gold)", "n": len(ud), "r0": round(V18.uas(r0.parse, test), 4), "r1": round(V18.uas(r1.parse, test), 4)}
    out["arms"].append(row); print(row, flush=True)
    for b in [int(x) for x in a.budgets.split(",") if x]:
        t1 = time.time(); wiki = wiki_sentences(b, tg)
        frames_w = V18.verb_frames(wiki)
        r0, r1 = learn(wiki, teacher, frames_w)
        row = {"source": "Simple-Wiki (substrate tagger)", "n": len(wiki), "r0": round(V18.uas(r0.parse, test), 4), "r1": round(V18.uas(r1.parse, test), 4), "elapsed_s": round(time.time() - t1)}
        out["arms"].append(row); print(row, flush=True)
    rng = np.random.default_rng(1)
    for c in list(r1.strength):
        keys = list(r1.strength[c]); vals = [r1.strength[c][k] for k in keys]; rng.shuffle(vals); r1.strength[c] = dict(zip(keys, vals))
    out["twin_shuffled_strengths_largest"] = round(V18.uas(r1.parse, test), 4)
    out["elapsed_s"] = round(time.time() - t0)
    print(json.dumps(out, indent=1))
    from experiments._seed_checkpoint import get_output_dir
    od = str(get_output_dir("probe_attachment_scale_reading_v20")); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
