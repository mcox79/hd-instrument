"""PROBE v22 -- INDUCED item-based CONSTRUCTIONS (Tomasello 2003) from reading, with DISTRIBUTIONAL HEAD identification (Harris),
as the attachment competition's coalition cue -- replacing the four hand-coded detectors (verbarg / coord / npmod / clausal).

What a child does: frequent multi-word schemas over categories ("DET ADJ NOUN", "ADP DET NOUN", "VERB DET NOUN") are stored as
chunks; the chunk's HEAD is the element the whole chunk can be SUBSTITUTED by -- the member whose own left/right category contexts
match the chunk's external contexts best (Harris's substitution test; no labels). Inside a chunk every other member attaches to the
head; across chunks, the competition's other cues (locality, category pair, form, boundary) decide.
Acquisition corpus: Simple-Wikipedia lines tagged with the substrate's tagger (the categories rung's stand-in). Chunk inventory:
category n-grams (n = 2..4) above a frequency threshold, kept if their head is identifiable (margin), greedy longest-match
chunking left to right at read time. The cue value for arc (h -> j) = the chunk schema it realises ("DET_ADJ_[NOUN]:dep@0") or
"none"; strengths learned within the category-pair configuration exactly like the other cues (probe v18).
Arms (UD-EWT test UAS, gold categories, reference only): competition with hand-coded constructions vs INDUCED constructions vs
both; per-relation view; twin = shuffled strengths. References: no constructions r0 0.4715 / r2 0.4834; hand-coded r0 0.4941.
Run: .venv/Scripts/python.exe experiments/probe_induced_constructions_v22.py [--smoke] [--lines 200000] [--both]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import json
import pickle
import sys
import time
from collections import Counter, defaultdict

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

CONTENT = {"NOUN", "PROPN", "PRON", "VERB", "ADJ", "ADV", "NUM", "AUX", "ADP", "DET", "SCONJ", "CCONJ", "PART", "INTJ", "SYM", "X"}


def tagged_wiki(n_lines, tagger, minlen=4, maxlen=30):
    out = []
    with open(SIMPLEWIKI, encoding="utf-8", errors="ignore") as f:
        for line in f:
            toks = [m.group(0) for m in _TOK.finditer(line.strip())]
            if not (minlen <= len(toks) <= maxlen):
                continue
            out.append(list(tagger.tag(toks)))
            if len(out) >= n_lines:
                break
    return out


def induce_constructions(pos_seqs, nmax=4, min_count=200, margin=0.15):
    """Frequent category n-grams -> {schema tuple: head index} by the SUBSTITUTION test: the member whose own (left, right)
    context distribution is most similar (cosine over category contexts) to the n-gram's external context distribution."""
    ctx_word = defaultdict(Counter)        # category -> Counter over (L, R) contexts
    ngram_ctx = {n: defaultdict(Counter) for n in range(2, nmax + 1)}
    ngram_cnt = {n: Counter() for n in range(2, nmax + 1)}
    for seq in pos_seqs:
        s = ["<S>"] + list(seq) + ["</S>"]
        for i in range(1, len(s) - 1):
            ctx_word[s[i]][(s[i - 1], s[i + 1])] += 1
        for n in range(2, nmax + 1):
            for i in range(1, len(s) - n):
                g = tuple(s[i:i + n])
                if any(c == "PUNCT" for c in g):
                    continue
                ngram_cnt[n][g] += 1; ngram_ctx[n][g][(s[i - 1], s[i + n])] += 1
    def vec(counter, keys):
        v = np.array([counter.get(k, 0) for k in keys], dtype=float); return v / (np.linalg.norm(v) + 1e-9)
    cons = {}
    for n in range(2, nmax + 1):
        for g, c in ngram_cnt[n].items():
            if c < min_count:
                continue
            keys = list(set(ngram_ctx[n][g]) | set().union(*[set(ctx_word[m]) for m in g]))
            gv = vec(ngram_ctx[n][g], keys)
            sims = [float(gv @ vec(ctx_word[m], keys)) for m in g]
            order = sorted(range(n), key=lambda k: -sims[k])
            if sims[order[0]] - (sims[order[1]] if n > 1 else 0) >= margin:
                cons[g] = order[0]
    return cons


def chunk_arcs(pos, cons, nmax=4):
    """Greedy longest-match chunking; returns {(h, j): schema_label} for within-chunk arcs (1-based)."""
    n = len(pos); i = 0; out = {}
    while i < n:
        placed = False
        for L in range(min(nmax, n - i), 1, -1):
            g = tuple(pos[i:i + L])
            if g in cons:
                hidx = cons[g]; h = i + hidx + 1
                label = "_".join(("[%s]" % c) if k == hidx else c for k, c in enumerate(g))
                for k in range(L):
                    if k != hidx:
                        out[(h, i + k + 1)] = label + ":d%d" % k
                i += L; placed = True; break
        if not placed:
            i += 1
    return out


def main():
    smoke = "--smoke" in sys.argv
    lines = int(sys.argv[sys.argv.index("--lines") + 1]) if "--lines" in sys.argv else (20000 if smoke else 200000)
    both = "--both" in sys.argv
    t0 = time.time()
    tg, _, _ = V11._fe()
    pos_seqs = tagged_wiki(lines, tg)
    cons = induce_constructions(pos_seqs, min_count=(50 if smoke else 200))
    print("induced constructions:", len(cons), "| examples:", [("_".join(g), h) for g, h in list(sorted(cons.items(), key=lambda kv: -len(kv[0])))[:8]], flush=True)
    # plug the induced chunk cue into the v18 competition via construction_arcs (monkeypatch), optionally union with hand-coded
    hand = V18.construction_arcs
    def induced_arcs(toks, pos):
        out = dict(hand(toks, pos)) if both else {}
        for (h, j), lab in chunk_arcs(list(pos), cons).items():
            out[(h, j)] = lab if not both else out.get((h, j), lab)
        return out
    V18.construction_arcs = induced_arcs; V18.USE_CONSTR = True; V18._CONSTR_CACHE.clear()
    train = load_ud(UD_TRAIN, cap=1500 if smoke else 6000, maxlen=40)
    test = load_ud(UD_TEST, cap=150 if smoke else 700)
    floor = _adj_right_uas([[(i + 1, "x", p, {x[0]: x[3] for x in s}.get(i + 1, 0), "_") for i, p in enumerate([x[2] for x in s])] for s in test])[0]
    teacher = pickle.load(open(V18.TEACHER, "rb"))
    frames = V18.verb_frames(train)
    stu = V18.AttachmentCompetition(frames)
    for s in train:
        toks = [x[1] for x in s]; pos = [x[2] for x in s]
        A, n = teacher._score_matrix(toks, pos)
        stu.accrue(toks, pos, single_root_marginals(A, n, 1.0))
    stu.finalize()
    out = {"lines": lines, "n_constructions": len(cons), "both": both, "floor": round(floor, 4),
           "student_r0": round(V18.uas(stu.parse, test), 4)}
    print("student r0 (induced constructions%s):" % (" + hand-coded" if both else ""), out["student_r0"], flush=True)
    for r in (1, 2):
        nxt = V18.AttachmentCompetition(frames)
        for s in train:
            toks = [x[1] for x in s]; pos = [x[2] for x in s]
            A, n = teacher._score_matrix(toks, pos); mt = single_root_marginals(A, n, 1.0); ms = stu.marginals(toks, pos)
            mix = {j: {h: 0.5 * ms.get(j, {}).get(h, 0.0) + 0.5 * mt.get(j, {}).get(h, 0.0) for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
            nxt.accrue(toks, pos, mix)
        stu = nxt.finalize()
        out["student_r%d" % r] = round(V18.uas(stu.parse, test), 4); print("student r%d:" % r, out["student_r%d" % r], flush=True)
        if smoke:
            break
    out["elapsed_s"] = round(time.time() - t0, 1); out["smoke"] = smoke
    print(json.dumps(out, indent=1))
    from experiments._seed_checkpoint import get_output_dir
    od = str(get_output_dir("probe_induced_constructions_v22" + ("_both" if both else "") + ("_smoke" if smoke else ""))); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)
    json.dump({"_".join(g): h for g, h in cons.items()}, open(os.path.join(od, "constructions.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
