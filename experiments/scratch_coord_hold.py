"""SCRATCH: BF upgrade test -- coordination-aware incremental HOLD (brief item 3). When a coordinator arrives it predicts a
like phrase (Levy 2008) and should WAIT, keeping the first conjunct alive in the beam. Prototype: add a hold bonus to CCONJ
(and optionally the first content word after it). Build one `full` asset (cap 2500) and eval the incr decode at bonus 0/2/5.
Honest test -- may or may not help; report conj + UAS under incr."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "3")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import numpy as np
import hdlab.attachment_arm as AA
from tools.build_attachment_validities import sentences, TEST
from experiments.exp_attachment_coordination_v1 import _TeacherWrap, build_asset, eval_table, _CoordConstr

CAP = 2500
train = sentences(os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu"), cap=CAP)
test = sentences(TEST, cap=700, maxlen=10**6)
tw = _TeacherWrap(train); bm = tw.base_matrices(train)
full = build_asset(train, tw, bm, coord_teacher=True, coord_constr=True, coarse=True, gamma=4, rounds=2, mode="parallel")
print("asset built", flush=True)

_orig_hold = AA.hold_expectation
BONUS = {"val": 0.0}

def coord_hold(pos, table=None, A=None):
    h = _orig_hold(pos, table, A)
    if BONUS["val"]:
        for j, p in enumerate(pos, start=1):
            if p == "CCONJ":
                h[j] += BONUS["val"]        # the coordinator predicts a like phrase -> hold (wait for the right conjunct)
    return h

AA.hold_expectation = coord_hold
AA.DECODE = "incr"
for b in (0.0, 2.0, 5.0, 10.0):
    BONUS["val"] = b
    ev = eval_table(full, test, "incr", True, True, "parallel")
    print("coord-hold bonus %4.1f: conj %.3f cc %.3f UAS %.4f | root %.3f nsubj %.3f obj %.3f" % (
        b, ev["rel"].get("conj", float("nan")), ev["rel"].get("cc", float("nan")), ev["uas"],
        ev["rel"].get("root", float("nan")), ev["rel"].get("nsubj", float("nan")), ev["rel"].get("obj", float("nan"))), flush=True)
AA.hold_expectation = _orig_hold
