"""SCRATCH: why does nsubj give back -0.017 under the coordination fix? Build base + full (cap 2500), and for every gold
nsubj arc find base-correct -> full-wrong flips; report how many are within 4 tokens of a coordinator (coordination-coupled,
gateable) vs diffuse. If coupled, the coord cue can be restricted off subject arcs to remove the give-back."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "3")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.attachment_arm as AA
from tools.build_attachment_validities import sentences, TEST
from experiments.exp_attachment_coordination_v1 import _TeacherWrap, build_asset, eval_table, _CoordConstr

CAP = 2500
train = sentences(os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu"), cap=CAP)
test = sentences(TEST, cap=700, maxlen=10**6)
tw = _TeacherWrap(train); bm = tw.base_matrices(train)
print("teacher ready", flush=True)
base = build_asset(train, tw, bm, coord_teacher=False, coord_constr=False, coarse=True, gamma=4, rounds=2, mode="parallel")
full = build_asset(train, tw, bm, coord_teacher=True, coord_constr=True, coarse=True, gamma=4, rounds=2, mode="parallel")
print("assets built", flush=True)

AA.DECODE = "map1"
flips = 0; coupled = 0; total_nsubj = 0
for toks, pos, gold, rels in test:
    n = len(toks)
    Ab, _ = AA.arc_scores(toks, pos, base); hb, _ = AA.decode(toks, pos, Ab, n, table=base)
    with _CoordConstr(True, True, "parallel"):
        Af, _ = AA.arc_scores(toks, pos, full); hf, _ = AA.decode(toks, pos, Af, n, table=full)
    cc_pos = [k for k in range(1, n+1) if pos[k-1] == "CCONJ"]
    for i, (g, r) in enumerate(zip(gold, rels), start=1):
        if r != "nsubj":
            continue
        total_nsubj += 1
        if hb.get(i) == g and hf.get(i) != g:
            flips += 1
            if any(abs(i-k) <= 4 for k in cc_pos):
                coupled += 1
print(f"gold nsubj: {total_nsubj}")
print(f"base-correct -> full-wrong flips: {flips} ({flips/total_nsubj:.3f})")
print(f"  of those, within 4 tokens of a coordinator (coordination-coupled): {coupled}/{flips}" + (f" = {coupled/flips:.2f}" if flips else ""))
