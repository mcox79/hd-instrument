"""PROBE v21 -- SEMANTIC BOOTSTRAPPING (Pinker 1984) as the acquisition signal for ATTACHMENT: learn structure from MEANING.

Owner (2026-09-12): the big jumps came from different brain-foundational METHODS, not gradual climbs. The attachment learner so far
learns from word co-occurrence (the prior-free gate: 0.272 -> 0.375); the hand-authored 'universal' prior was worth ~0.1 -- which is
exactly the knowledge a child gets for free from MEANING. Here the TEACHER is the substrate's own event knowledge:
  * verb -> nominal arc plausibility = typed selectional association A(v, class(noun)) (Resnik 1996 over WordNet supersenses,
    hdlab.typed_selectional_preference, grown by reading: 6,450 verbs) -- "this noun is a plausible argument of this verb";
  * ROOT preference = the verb whose arguments are most plausible (the event predicate), not a frequency prior;
  * locality = memory-limited retrieval decay (the one structural bias; PINNED);
  * form classes never head (pre-lexical).
The teacher's exact tree posterior (Matrix-Tree) gives SOFT outcomes; the attachment cue competition (probe v18) learns its
configuration-conditioned strengths from them, then self-teaches anchored on the teacher. NO treebank, NO hand-written table.
Arms: meaning teacher alone; competition r0/r1/r2 taught by it; (+constr) with the construction coalition cue; references:
prior-free co-occurrence teacher 0.272 -> student 0.375; prior-informed 0.4626 -> 0.4834; adjacent-right floor 0.285.
ALSO the CONSUMER METRIC: verb -> core-argument recall (gold nsubj/obj/iobj/nsubj:pass arcs whose head is a VERB recovered).
Run: .venv/Scripts/python.exe experiments/probe_semantic_bootstrap_attachment_v21.py [--smoke] [--constr] [--beta 2.0]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import json
import math
import sys
import time

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.probe_attachment_competition_v18 as V18
from experiments.exp_parser_graded_decode_regimes_v1 import load_ud, UD_TRAIN, UD_TEST
from experiments.exp_parser_selfsup_em_v1 import _adj_right_uas
from hdlab.graded_parser import single_root_marginals, chu_liu_edmonds
from hdlab.thematic_role_labeler import lemma_verb

NOMINAL = ("NOUN", "PRON", "PROPN")
CORE = ("nsubj", "obj", "iobj", "nsubj:pass")


class MeaningTeacher:
    """Arc scores from MEANING + locality + form only (no co-occurrence table, no hand prior)."""

    def __init__(self, beta=2.0, lam=0.3):
        from hdlab.typed_selectional_preference import get
        self.tsp = get(); self.beta = beta; self.lam = lam; self._cache = {}

    def plaus(self, verb_tok, noun_tok):
        key = (verb_tok.lower(), noun_tok.lower())
        if key not in self._cache:
            v = lemma_verb(verb_tok).lower(); s = None
            try:
                s = self.tsp.score(v, noun_tok.lower()) if self.tsp.covers(v) else None
            except Exception:
                s = None
            self._cache[key] = float(s) if s is not None else 0.0
        return self._cache[key]

    def _score_matrix(self, toks, pos):
        n = len(toks); A = np.full((n + 1, n + 1), -np.inf)
        best_arg = np.zeros(n + 1)
        for j in range(1, n + 1):
            for h in range(1, n + 1):
                if h == j or pos[h - 1] in V18.FORM:
                    continue
                sc = -self.lam * math.log(abs(h - j) + 1.0)
                if pos[h - 1] == "VERB" and pos[j - 1] in NOMINAL:
                    p = self.plaus(toks[h - 1], toks[j - 1]); sc += self.beta * p
                    best_arg[h] = max(best_arg[h], p)
                A[h][j] = sc
        for j in range(1, n + 1):
            if pos[j - 1] in V18.FORM:
                A[0][j] = -np.inf if any(pos[k] not in V18.FORM for k in range(n)) else 0.0
            else:
                A[0][j] = (self.beta * best_arg[j] if pos[j - 1] == "VERB" else -1.0) - 0.5
        return A, n

    def marginals(self, toks, pos):
        A, n = self._score_matrix(toks, pos); return single_root_marginals(A, n, 1.0)

    def parse_cle(self, toks, pos):
        A, n = self._score_matrix(toks, pos); return chu_liu_edmonds(A, n)


def core_arg_recall(parse_fn, test):
    hit = tot = 0
    for s in test:
        toks = [x[1] for x in s]; pos = [x[2] for x in s]; heads = parse_fn(toks, pos)
        for x in s:
            if x[4] in CORE and 1 <= x[3] <= len(s) and pos[x[3] - 1] == "VERB":
                tot += 1; hit += int(heads.get(x[0], -1) == x[3])
    return hit / max(1, tot), tot


def main():
    smoke = "--smoke" in sys.argv
    beta = float(sys.argv[sys.argv.index("--beta") + 1]) if "--beta" in sys.argv else 2.0
    V18.USE_CONSTR = "--constr" in sys.argv
    t0 = time.time()
    train = load_ud(UD_TRAIN, cap=1500 if smoke else 6000, maxlen=40)
    test = load_ud(UD_TEST, cap=150 if smoke else 700)
    floor = _adj_right_uas([[(i + 1, "x", p, {x[0]: x[3] for x in s}.get(i + 1, 0), "_") for i, p in enumerate([x[2] for x in s])] for s in test])[0]
    teacher = MeaningTeacher(beta=beta)
    out = {"floor": round(floor, 4), "beta": beta, "constr": V18.USE_CONSTR}
    out["meaning_teacher_uas"] = round(V18.uas(teacher.parse_cle, test), 4)
    r, n = core_arg_recall(teacher.parse_cle, test); out["meaning_teacher_core_arg_recall"] = round(r, 4); out["n_core_args"] = n
    print("floor", out["floor"], "meaning teacher UAS", out["meaning_teacher_uas"], "core-arg recall", out["meaning_teacher_core_arg_recall"], flush=True)
    frames = V18.verb_frames(train)
    stu = V18.AttachmentCompetition(frames)
    for s in train:
        toks = [x[1] for x in s]; pos = [x[2] for x in s]
        stu.accrue(toks, pos, teacher.marginals(toks, pos))
    stu.finalize()
    out["student_r0"] = round(V18.uas(stu.parse, test), 4); out["student_r0_core"] = round(core_arg_recall(stu.parse, test)[0], 4)
    print("student r0:", out["student_r0"], "core", out["student_r0_core"], flush=True)
    ALPHA = 0.5
    for r in (1, 2):
        nxt = V18.AttachmentCompetition(frames)
        for s in train:
            toks = [x[1] for x in s]; pos = [x[2] for x in s]
            mt = teacher.marginals(toks, pos); ms = stu.marginals(toks, pos); n = len(toks)
            mix = {j: {h: ALPHA * ms.get(j, {}).get(h, 0.0) + (1 - ALPHA) * mt.get(j, {}).get(h, 0.0)
                       for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
            nxt.accrue(toks, pos, mix)
        stu = nxt.finalize()
        out["student_r%d" % r] = round(V18.uas(stu.parse, test), 4); out["student_r%d_core" % r] = round(core_arg_recall(stu.parse, test)[0], 4)
        print("student r%d:" % r, out["student_r%d" % r], "core", out["student_r%d_core" % r], flush=True)
        if smoke:
            break
    rng = np.random.default_rng(1)
    for c in list(stu.strength):
        keys = list(stu.strength[c]); vals = [stu.strength[c][k] for k in keys]; rng.shuffle(vals); stu.strength[c] = dict(zip(keys, vals))
    out["twin_shuffled_strengths"] = round(V18.uas(stu.parse, test), 4)
    out["elapsed_s"] = round(time.time() - t0, 1); out["smoke"] = smoke
    print(json.dumps(out, indent=1))
    from experiments._seed_checkpoint import get_output_dir
    od = str(get_output_dir("probe_semantic_bootstrap_attachment_v21" + ("_constr" if V18.USE_CONSTR else "") + ("_smoke" if smoke else ""))); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
