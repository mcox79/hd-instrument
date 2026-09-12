"""Build the attachment arm's cue-validity asset (data/frontend_assets/attachment_validities_v1.json) WITHOUT a treebank and
WITHOUT a hand-authored prior -- the knowledge-free acquisition measured as the landing gate (spec s7 gate 1):
  1. TEACHER = a prior-free reading-learned scorer (exp_parser_selfsup_em_v1.SelfSupEM, prior_weight=0, 2 EM rounds) over the
     training SENTENCES (tokens + categories only; the trees in the file are never read) -- its exact tree posterior is the first
     outcome signal (the posterior teaches the cue statistics);
  2. the attachment arm accrues SOFT arc counts from that posterior (round 0), then re-teaches itself for R rounds anchored on the
     teacher (mix alpha * own posterior + (1-alpha) * teacher posterior) -- pure self-posterior drifts;
  3. verb frames (transitivity propensity) are accrued from the same tokens; the counts + frames are saved as the plastic asset.
Categories: the training file's UPOS column is the categories rung's STAND-IN until the reading-induced categories hand down a
usable functional inventory (ledger). Parameters (rounds, alpha, training cap) are swept, never adopted -- defaults = the measured
gate configuration. Run: python tools/build_attachment_validities.py [--rounds 2] [--alpha 0.5] [--cap 6000] [--eval]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import argparse
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import attachment_arm as AA
from hdlab.graded_parser import single_root_marginals

TRAIN = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
TEST = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")


def sentences(path, cap=None, maxlen=40):
    out = []; toks = []; pos = []; heads = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks and len(toks) <= maxlen:
                    out.append((toks, pos, heads))
                toks, pos, heads = [], [], []
                if cap and len(out) >= cap:
                    break
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            toks.append(c[1]); pos.append(c[3]); heads.append(int(c[6]))
    if toks and len(toks) <= maxlen and (not cap or len(out) < cap):
        out.append((toks, pos, heads))
    return out


def knowledge_free_teacher(train, rounds=2):
    from experiments.exp_parser_selfsup_em_v1 import SelfSupEM
    tr = [[(0, t, p, 0, "_") for t, p in zip(toks, pos)] for toks, pos, _ in train]
    m = SelfSupEM(lam=0.3, prior_weight=0.0, lex_weight=0.0).learn_raw(tr)
    for _ in range(rounds):
        m.em_round(tr)
    return m


def uas(parse_fn, test):
    c = t = 0
    for toks, pos, gold in test:
        hd = parse_fn(toks, pos)
        for i, g in enumerate(gold, start=1):
            if 0 <= g <= len(toks):
                c += int(hd.get(i, -1) == g); t += 1
    return c / max(1, t)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=2); ap.add_argument("--alpha", type=float, default=0.5)
    ap.add_argument("--cap", type=int, default=6000); ap.add_argument("--eval", action="store_true")
    ap.add_argument("--out", default=AA.ASSET)
    a = ap.parse_args(argv)
    t0 = time.time()
    train = sentences(TRAIN, cap=a.cap)
    frames = AA.verb_frames_from_reading([(t, p) for t, p, _ in train])
    teacher = knowledge_free_teacher(train)
    print("teacher (prior-free, 2 EM rounds) ready in %.0fs" % (time.time() - t0), flush=True)
    tmarg = {}
    counts = AA.new_counts()
    for i, (toks, pos, _) in enumerate(train):
        A, n = teacher._score_matrix(toks, pos); mt = single_root_marginals(A, n, 1.0); tmarg[i] = mt
        AA.accrue_sentence(counts, AA.SentenceCues(toks, pos, frames), mt)
    table = {"counts": counts, "frames": frames, "strength": AA.strengths_from_arc_counts(counts)}
    print("round 0 accrued (%d sentences) in %.0fs" % (len(train), time.time() - t0), flush=True)
    for r in range(1, a.rounds + 1):
        nxt = AA.new_counts()
        for i, (toks, pos, _) in enumerate(train):
            ms = AA.head_posterior(toks, pos, table); mt = tmarg[i]; n = len(toks)
            mix = {j: {h: a.alpha * ms.get(j, {}).get(h, 0.0) + (1 - a.alpha) * mt.get(j, {}).get(h, 0.0)
                       for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
            AA.accrue_sentence(nxt, AA.SentenceCues(toks, pos, frames), mix)
        table = {"counts": nxt, "frames": frames, "strength": AA.strengths_from_arc_counts(nxt)}
        print("round %d re-estimated in %.0fs" % (r, time.time() - t0), flush=True)
    path = AA.save_attachment_validities(a.out, table)
    print("wrote", path, flush=True)
    if a.eval:
        test = sentences(TEST, cap=700, maxlen=10**6)
        print("UAS on UD-EWT test (gold categories; reference only): teacher %.4f | attachment arm %.4f" % (
            uas(teacher.parse_cle, test), uas(lambda t, p: AA.heads(t, p, table), test)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
