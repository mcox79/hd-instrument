"""Build the attachment arm's cue-validity asset (data/frontend_assets/attachment_validities_v1.json) WITHOUT a treebank and
WITHOUT a hand-authored prior -- the knowledge-free acquisition measured as the landing gate (spec s7 gate 1):
  1. TEACHER = a prior-free reading-learned scorer (exp_parser_selfsup_em_v1.SelfSupEM, prior_weight=0, 2 EM rounds) over the
     training SENTENCES (tokens + categories only; the trees in the file are never read) + SEMANTIC BOOTSTRAPPING (2026-09-12:
     attachment_arm.SemanticBootstrapTeacher -- the predicate heads its plausible participants; --beta, 0 = off) as ONE tree
     posterior -- the first outcome signal (the posterior teaches the cue statistics);
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


def induced_categorizer(asset_path):
    """HAND-OFF categories -> heads (2026-09-12): token categories from the READING-INDUCED inventory instead of the UPOS column.
    The asset (exp_reading_induced_categories_v1) maps word type -> cluster; clusters are NAMED by their majority UPOS (gold used
    ONLY to name, so the arm's category-keyed constructions keep working) -- the probe-v15 'collapsed' reading, the one the
    categories brief (pri-15) must make usable. Unknown words fall back to form classes (punctuation / numerals) or the open
    class NOUN. Returns f(tokens) -> list of category names."""
    import json
    import re
    with open(asset_path, encoding="utf-8") as f:
        d = json.load(f)
    w2c = d["word2cat"]; names = d.get("cluster_to_upos_name", {})
    def name_of(c):
        n = names.get(str(c), names.get(c, None)) if isinstance(names, dict) else None
        return n if isinstance(n, str) and n else "NOUN"
    def cat(tok):
        c = w2c.get(tok.lower())
        if c is not None:
            return name_of(c)
        if re.fullmatch(r"[^\w\s]+", tok):
            return "PUNCT"
        if re.fullmatch(r"[\d.,:/-]+", tok):
            return "NUM"
        return "NOUN"
    return lambda toks: [cat(x) for x in toks]


def recategorize(sents, categorizer):
    """Replace every sentence's category column with categorizer(tokens); the heads column is untouched (measuring instrument)."""
    return [(toks, categorizer(toks), heads, rels) for toks, pos, heads, rels in sents]


def sentences(path, cap=None, maxlen=40):
    out = []; toks = []; pos = []; heads = []; rels = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks and len(toks) <= maxlen:
                    out.append((toks, pos, heads, rels))
                toks, pos, heads, rels = [], [], [], []
                if cap and len(out) >= cap:
                    break
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            toks.append(c[1]); pos.append(c[3]); heads.append(int(c[6])); rels.append(c[7].split(":")[0])
    if toks and len(toks) <= maxlen and (not cap or len(out) < cap):
        out.append((toks, pos, heads, rels))
    return out


def knowledge_free_teacher(train, rounds=2, beta=0.0, tsp_asset=None):
    """Co-occurrence teacher (phrase internals; prior-free SelfSupEM) + SEMANTIC BOOTSTRAPPING (beta > 0: the predicate heads its
    plausible participants; attachment_arm.SemanticBootstrapTeacher) as ONE tree posterior."""
    from experiments.exp_parser_selfsup_em_v1 import SelfSupEM
    tr = [[(0, t, p, 0, "_") for t, p in zip(toks, pos)] for toks, pos, _, _ in train]
    m = SelfSupEM(lam=0.3, prior_weight=0.0, lex_weight=0.0).learn_raw(tr)
    for _ in range(rounds):
        m.em_round(tr)
    if beta <= 0:
        return m
    meaning = AA.SemanticBootstrapTeacher(beta=beta, lam=m.lam, tsp_asset=tsp_asset)

    class Combined:
        def _score_matrix(self, toks, pos):
            A, n = m._score_matrix(toks, pos); return meaning.combined_scores(A, n, toks, pos), n

        def parse_cle(self, toks, pos):
            from hdlab.graded_parser import chu_liu_edmonds
            A, n = self._score_matrix(toks, pos); return chu_liu_edmonds(A, n)
    return Combined()


CORE_RELS = ("root", "nsubj", "obj", "obl", "nmod", "xcomp", "ccomp", "advcl", "conj", "case", "punct")


def uas(parse_fn, test, per_relation=False):
    c = t = 0; rt = {}; rh = {}
    for toks, pos, gold, rels in test:
        hd = parse_fn(toks, pos)
        for i, g in enumerate(gold, start=1):
            if 0 <= g <= len(toks):
                ok = int(hd.get(i, -1) == g); c += ok; t += 1
                r = rels[i - 1]
                if r in CORE_RELS:
                    rt[r] = rt.get(r, 0) + 1; rh[r] = rh.get(r, 0) + ok
    if per_relation:
        return c / max(1, t), {r: round(rh[r] / rt[r], 3) for r in CORE_RELS if r in rt}
    return c / max(1, t)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3); ap.add_argument("--alpha", type=float, default=0.8)   # the measured gate configuration
    ap.add_argument("--cap", type=int, default=6000); ap.add_argument("--eval", action="store_true")
    ap.add_argument("--out", default=AA.ASSET)
    ap.add_argument("--beta", type=float, default=10.0, help="semantic-bootstrapping weight (0 = co-occurrence only); 10 = the measured operating point")
    ap.add_argument("--tsp-asset", default=None, help="alternative plausibility asset for the semantic-bootstrapping teacher (e.g. the self-grown store's typed asset)")
    ap.add_argument("--categories", default=None, help="reading-induced category asset (word2cat + cluster names) to use INSTEAD of the UPOS column -- the categories->heads hand-off test")
    a = ap.parse_args(argv)
    t0 = time.time()
    train = sentences(TRAIN, cap=a.cap)
    categorizer = induced_categorizer(a.categories) if a.categories else None
    if categorizer:
        train = recategorize(train, categorizer)
        print("categories = reading-induced (%s) in place of UPOS" % os.path.basename(a.categories), flush=True)
    frames = AA.verb_frames_from_reading([(t, p) for t, p, _, _ in train])
    pp_assoc = AA.pp_assoc_from_reading([(t, p) for t, p, _, _ in train])    # Hindle-Rooth preposition association (treebank-free)
    print("pp association: %d verb|prep, %d noun|prep cells" % (len(pp_assoc["fv"]), len(pp_assoc["fn"])), flush=True)
    teacher = knowledge_free_teacher(train, beta=a.beta, tsp_asset=a.tsp_asset)
    if a.tsp_asset:
        print("plausibility asset =", os.path.basename(a.tsp_asset), flush=True)
    print("teacher (prior-free co-occurrence, 2 EM rounds%s) ready in %.0fs" % (" + semantic bootstrapping beta=%g" % a.beta if a.beta > 0 else "", time.time() - t0), flush=True)
    tmarg = {}
    counts = AA.new_counts()
    for i, (toks, pos, _, _) in enumerate(train):
        A, n = teacher._score_matrix(toks, pos); mt = single_root_marginals(A, n, 1.0); tmarg[i] = mt
        AA.accrue_sentence(counts, AA.SentenceCues(toks, pos, frames, pp_assoc), mt)
    table = {"counts": counts, "frames": frames, "pp_assoc": pp_assoc, "strength": AA.strengths_from_arc_counts(counts)}
    print("round 0 accrued (%d sentences) in %.0fs" % (len(train), time.time() - t0), flush=True)
    for r in range(1, a.rounds + 1):
        nxt = AA.new_counts()
        for i, (toks, pos, _, _) in enumerate(train):
            ms = AA.head_posterior(toks, pos, table); mt = tmarg[i]; n = len(toks)
            mix = {j: {h: a.alpha * ms.get(j, {}).get(h, 0.0) + (1 - a.alpha) * mt.get(j, {}).get(h, 0.0)
                       for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
            AA.accrue_sentence(nxt, AA.SentenceCues(toks, pos, frames, pp_assoc), mix)
        table = {"counts": nxt, "frames": frames, "pp_assoc": pp_assoc, "strength": AA.strengths_from_arc_counts(nxt)}
        print("round %d re-estimated in %.0fs" % (r, time.time() - t0), flush=True)
    path = AA.save_attachment_validities(a.out, table)
    print("wrote", path, flush=True)
    if a.eval:
        test = sentences(TEST, cap=700, maxlen=10**6)
        if categorizer:
            test = recategorize(test, categorizer)
            gold = sentences(TEST, cap=700, maxlen=10**6); agree = tot = 0
            for (_, pp, _, _), (_, gp, _, _) in zip(test, gold):
                for x, y in zip(pp, gp):
                    agree += int(x == y); tot += 1
            print("induced-category agreement with UPOS on the test slice: %.4f (%d tokens)" % (agree / max(1, tot), tot), flush=True)
        u, per = uas(lambda t, p: AA.heads(t, p, table), test, per_relation=True)
        print("UAS on UD-EWT test (gold categories; reference only): teacher %.4f | attachment arm %.4f" % (uas(teacher.parse_cle, test), u), flush=True)
        print("attachment arm per-relation (core structure = the consumers' signal):", per, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
