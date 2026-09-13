"""SCRATCH diagnostic (not a landed cell): anatomy of conj failures on UD-EWT test 700, gold categories, current asset.
Traces WHERE the signal is lost on the coordination arc:
  (1) does the current `coord` construction even fire on the gold conj arc?
  (2) is the second conjunct's head (the dependent of conj) mis-identified by "nearest content word"?
  (3) is the FIRST conjunct's own attachment already wrong (the conjunct inherits the error)?
  (4) what does the arm currently assign the conj dependent to?
  (5) does the TEACHER posterior (the acquisition signal) ever put mass on the gold conj arc?
"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "3")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.attachment_arm as AA
from tools.build_attachment_validities import sentences, TEST
from collections import Counter

test = sentences(TEST, cap=700, maxlen=10**6)
tab = AA.load_attachment_validities()

CONTENT = AA.CONTENT
n_conj = 0
fires = 0            # coord construction proposes the exact gold arc
dep_is_head_of_run = 0   # the conj dependent (2nd conjunct) is the head of its nominal/verbal run
first_conj_ok = 0    # the gold head of conj (1st conjunct) is itself correctly attached by the arm
arm_correct = 0
cross_cat = 0        # gold: 1st and 2nd conjunct different UPOS
dep_starts_with_mod = 0  # the token right after cc is a modifier (DET/ADJ/NUM), so "min content after cc" != head
teacher_mass = []    # teacher posterior mass on the gold conj arc

# build the teacher once (co-occurrence + semantic bootstrapping, same as the asset build)
from experiments.exp_parser_selfsup_em_v1 import SelfSupEM
from hdlab.graded_parser import single_root_marginals
train = sentences(os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu"), cap=1500)
tr = [[(0, t, p, 0, "_") for t, p in zip(toks, pos)] for toks, pos, _, _ in train]
m = SelfSupEM(lam=0.3, prior_weight=0.0, lex_weight=0.0).learn_raw(tr)
for _ in range(2):
    m.em_round(tr)
meaning = AA.SemanticBootstrapTeacher(beta=10.0, lam=m.lam)

for toks, pos, gold, rels in test:
    n = len(toks)
    hd = AA.heads(toks, pos, tab)
    # teacher posterior for this sentence
    A0, _ = m._score_matrix(toks, pos); Ac = meaning.combined_scores(A0, n, toks, pos)
    tmarg = single_root_marginals(Ac.copy(), n, 1.0)
    for i, (g, r) in enumerate(zip(gold, rels), start=1):
        if r != "conj":
            continue
        n_conj += 1
        # g = gold head (first conjunct); i = dependent (second conjunct head)
        if 1 <= g <= n and pos[g-1] != pos[i-1]:
            cross_cat += 1
        # is i the head of its run? (no same-or-higher content word immediately after that governs it in gold)
        # proxy: token right after the nearest preceding cc is a modifier
        cc = max([k for k in range(1, i) if pos[k-1] == "CCONJ"], default=None)
        if cc:
            after = cc + 1
            if after <= n and pos[after-1] in ("DET", "ADJ", "NUM", "ADV"):
                dep_starts_with_mod += 1
        if hd.get(i) == g:
            arm_correct += 1
        if 1 <= g <= n and hd.get(g) == gold[g-1]:
            first_conj_ok += 1
        # does the coord construction propose (g, i)?
        cmap = AA.construction_map(toks, pos)
        if cmap.get((g, i)) == "coord":
            fires += 1
        teacher_mass.append(tmarg.get(i, {}).get(g, 0.0))

print(f"n_conj gold arcs: {n_conj}")
print(f"arm correct (conj recall): {arm_correct/n_conj:.3f}")
print(f"coord construction fires the EXACT gold arc: {fires}/{n_conj} = {fires/n_conj:.3f}")
print(f"cross-category conjuncts (different UPOS): {cross_cat}/{n_conj} = {cross_cat/n_conj:.3f}")
print(f"2nd conjunct run starts with a modifier (min-content-after-cc != head): {dep_starts_with_mod}/{n_conj} = {dep_starts_with_mod/n_conj:.3f}")
print(f"first conjunct itself correctly attached by arm: {first_conj_ok}/{n_conj} = {first_conj_ok/n_conj:.3f}")
import numpy as np
tm = np.array(teacher_mass)
print(f"teacher posterior mass on gold conj arc: mean {tm.mean():.3f}, median {np.median(tm):.3f}, frac>0.3: {(tm>0.3).mean():.3f}, frac~0 (<0.05): {(tm<0.05).mean():.3f}")
