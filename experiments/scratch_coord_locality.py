"""SCRATCH (right-not-easy): 26% of gold conj arcs span 9+ tokens, where LOCALITY fights the parallel link. The brain's
parallelism PREDICTION resists locality decay -- the coordinator holds the slot open regardless of intervening material. Test:
a distance-invariant coordination bonus at decode on the coord-construction arcs (L->R, R->cc), swept, analogous to the
function-word convention bonus. Report conj OVERALL and split by distance (<9 vs 9+), and UAS + neighbors (must not regress)."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "3")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import numpy as np
import hdlab.attachment_arm as AA
from collections import Counter
from tools.build_attachment_validities import sentences, TEST
from experiments.exp_attachment_coordination_v1 import _TeacherWrap, build_asset, _CoordConstr, coord_sites

train = sentences(os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu"), cap=2500)
test = sentences(TEST, cap=700, maxlen=10**6)
tw = _TeacherWrap(train); bm = tw.base_matrices(train)
full = build_asset(train, tw, bm, coord_teacher=True, coord_constr=True, coarse=True, gamma=4, rounds=2, mode="parallel")
print("asset built", flush=True)
AA.DECODE = "map1"
RELS = ("conj", "cc", "nsubj", "obj", "nmod", "root")

for bonus in (0.0, 1.0, 2.0, 3.0, 5.0):
    tot = ok = 0; rt = Counter(); rk = Counter(); cj = {"near": [0, 0], "far": [0, 0]}
    with _CoordConstr(True, True, "parallel"):
        for toks, pos, gold, rels in test:
            n = len(toks)
            A, _ = AA.arc_scores(toks, pos, full)
            if bonus:
                for (L, R, k) in coord_sites(toks, pos, True, "parallel"):
                    if np.isfinite(A[L][R]):
                        A[L][R] += bonus
                    if np.isfinite(A[R][k]):
                        A[R][k] += bonus
            hd, _ = AA.decode(toks, pos, A, n, table=full)
            for i, (g, r) in enumerate(zip(gold, rels), start=1):
                if not (0 <= g <= n):
                    continue
                hit = int(hd.get(i, -1) == g); ok += hit; tot += 1
                if r in RELS:
                    rt[r] += 1; rk[r] += hit
                if r == "conj" and 1 <= g <= n:
                    b = "far" if abs(i - g) >= 9 else "near"
                    cj[b][0] += hit; cj[b][1] += 1
    print("bonus %3.1f | conj %.3f (near %.3f[n=%d] far %.3f[n=%d]) cc %.3f | UAS %.4f | nsubj %.3f obj %.3f nmod %.3f root %.3f" % (
        bonus, rk["conj"]/max(1,rt["conj"]), cj["near"][0]/max(1,cj["near"][1]), cj["near"][1],
        cj["far"][0]/max(1,cj["far"][1]), cj["far"][1], rk["cc"]/max(1,rt["cc"]), ok/max(1,tot),
        rk["nsubj"]/max(1,rt["nsubj"]), rk["obj"]/max(1,rt["obj"]), rk["nmod"]/max(1,rt["nmod"]), rk["root"]/max(1,rt["root"])), flush=True)
