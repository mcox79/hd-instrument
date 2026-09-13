"""SCRATCH (right-not-easy): anatomy of the RESIDUAL conj errors under the full coordination fix. For every gold conj arc the
full asset gets WRONG, classify WHY: (a) gold-L was the nearest-same-parallel-class content head before cc -> the construction
OFFERED it but the decode lost it in competition (lever = stronger/again coord strength, or chain-top); (b) gold-L was NOT the
nearest-same-class -> L mis-identified (lever = chain-top / co-argument L). Also: is gold-L the TOP of gold-L's own head chain
of the same class (the 0.589 ceiling rule), and what did full attach R to instead. Build full (cap 2500)."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "3")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.attachment_arm as AA
from tools.build_attachment_validities import sentences, TEST
from experiments.exp_attachment_coordination_v1 import _TeacherWrap, build_asset, _CoordConstr, pclass, right_head, left_head

train = sentences(os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu"), cap=2500)
test = sentences(TEST, cap=700, maxlen=10**6)
tw = _TeacherWrap(train); bm = tw.base_matrices(train)
full = build_asset(train, tw, bm, coord_teacher=True, coord_constr=True, coarse=True, gamma=4, rounds=2, mode="parallel")
print("asset built", flush=True)
AA.DECODE = "map1"

def chain_top_same_class(gold, pos, start, cls, k):
    """top of start's head chain (gold tree) staying left of cc at k and same parallel class."""
    top = start; cur = start; seen = 0
    while cur and cur < k and seen < len(pos) + 1:
        if pclass(pos[cur-1], True) == cls:
            top = cur
        cur = gold[cur-1] if 1 <= cur <= len(gold) else 0; seen += 1
    return top

n_wrong = 0; offered_lost = 0; L_misid = 0; goldL_is_nearest = 0; goldL_is_chaintop = 0; total = 0
attach_hist = {}
for toks, pos, gold, rels in test:
    n = len(toks)
    with _CoordConstr(True, True, "parallel"):
        Af, _ = AA.arc_scores(toks, pos, full); hf, _ = AA.decode(toks, pos, Af, n, table=full)
    for i, (g, r) in enumerate(zip(gold, rels), start=1):
        if r != "conj" or not (1 <= g <= n):
            continue
        total += 1
        cc = max([k for k in range(1, i) if pos[k-1] == "CCONJ"], default=None)
        cls = pclass(pos[i-1], True)
        nearest_L = left_head(pos, cc, cls, True) if (cc and cls) else None
        if nearest_L == g:
            goldL_is_nearest += 1
        if cc and cls and chain_top_same_class(gold, pos, g, cls, cc) == g:
            goldL_is_chaintop += 1
        if hf.get(i) == g:
            continue
        n_wrong += 1
        if nearest_L == g:
            offered_lost += 1                     # construction offered gold-L, decode lost it
        else:
            L_misid += 1
        # what did full attach R to?
        h = hf.get(i)
        rel = "root" if h == 0 else ("nearer_than_L" if (g and h and abs(h-i) < abs(g-i)) else "other")
        attach_hist[rel] = attach_hist.get(rel, 0) + 1

print(f"gold conj n={total}; full correct={total-n_wrong} ({(total-n_wrong)/total:.3f}); wrong={n_wrong}")
print(f"gold-L IS the nearest-same-class head: {goldL_is_nearest}/{total} = {goldL_is_nearest/total:.3f} (the nearest-L ceiling)")
print(f"gold-L IS the top of its own same-class head chain: {goldL_is_chaintop}/{total} = {goldL_is_chaintop/total:.3f} (chain-top ceiling)")
print(f"ERRORS: construction OFFERED gold-L but decode LOST it (competition): {offered_lost}/{n_wrong} = {offered_lost/max(1,n_wrong):.3f}")
print(f"ERRORS: gold-L MIS-identified (not nearest-same-class): {L_misid}/{n_wrong} = {L_misid/max(1,n_wrong):.3f}")
print(f"what full attached the missed R to: {attach_hist}")
