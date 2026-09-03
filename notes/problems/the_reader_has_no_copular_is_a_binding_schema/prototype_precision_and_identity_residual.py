import os, sys
REPO="C:/AI/hd-instrument"; sys.path.insert(0, REPO)
import experiments._copular_nominal_events as M
import experiments.exp_copular_is_a_binding_readout_v1 as E
from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser
from hdlab.arc_labeler import ArcLabeler
from collections import defaultdict
pos=PosTagger.load(M._POS_ASSET); arc=ArcParser.load(M._ARC_ASSET); lab=ArcLabeler.load(M._LAB_ASSET)
sents=E.load_ud(E.UD_TEST)

# ---- (1) DEFLATION test: of the FIX's "false positives" (fired pairs not in narrow typed_gold), how many are
#          a REAL copular clause excluded from typed_gold? (any cop arc in the gold parse -> a real predication) ----
def all_gold_cop_pairs(sent):
    """EVERY gold cop predication (holder=any nsubj/expl subject, property=cop head) -- the WIDE gold, incl. the
    types typed_gold excludes (PP/clausal/expletive/pron-heavy)."""
    by={r[0]:r for r in sent}; out=set(); props=set()
    for r in sent:
        if r[6]!="cop": continue
        ph=r[5]
        if ph not in by: continue
        props.add(ph-1)
        subj=[s for s in sent if s[5]==ph and s[6] in ("nsubj","nsubj:pass","csubj","expl")]
        if subj: out.add((subj[0][0]-1, ph-1))
    return out, props

fp_real_pred=fp_real_holder=fp_spurious=0
id_not_det=id_wrong_holder=0; id_n=0
for sent in sents:
    toks=[r[1] for r in sent]; up=pos.tag(toks)
    heads=arc.parse(toks,up).heads
    base=set(M.extract_entity_states(toks,up,arc,lab))
    fix=base | E.robust_cop(toks,up,heads,gate=True)
    narrow=set((h,p) for (h,p,_t) in E.typed_gold(sent))
    wide, wide_props = all_gold_cop_pairs(sent)
    for (h,p) in fix:
        if (h,p) in narrow: continue          # true positive vs narrow gold
        if (h,p) in wide: fp_real_pred+=1      # exact real cop pair excluded by narrow gold
        elif p in wide_props: fp_real_holder+=1  # real cop PREDICATE, holder differs (a real clause, holder err)
        else: fp_spurious+=1                    # not a gold cop predicate at all -> genuine over-fire
    # identity residual decomposition
    fix_props={p for (_h,p) in fix}
    for (h,p,t) in E.typed_gold(sent):
        if t!="ident": continue
        id_n+=1
        if (h,p) in fix: continue
        if p in fix_props: id_wrong_holder+=1
        else: id_not_det+=1
tot_fp=fp_real_pred+fp_real_holder+fp_spurious
print("(1) FIX precision-cost DEFLATION (of %d non-narrow-gold fires):"%tot_fp)
print("    real cop pair excluded by narrow gold : %d (%.1f%%)"%(fp_real_pred,100*fp_real_pred/tot_fp))
print("    real cop PREDICATE, holder differs     : %d (%.1f%%)"%(fp_real_holder,100*fp_real_holder/tot_fp))
print("    genuinely spurious (not a cop pred)    : %d (%.1f%%)"%(fp_spurious,100*fp_spurious/tot_fp))
print("    => %.1f%% of the 'precision cost' is real copular clauses my narrow gold excluded, not error"
      %(100*(fp_real_pred+fp_real_holder)/tot_fp))
print("\n(2) IDENTITY residual (n=%d, fix recall 0.712 -> %d missed):"%(id_n,id_not_det+id_wrong_holder))
print("    not detected (no cop pred found) : %d (%.1f%% of all identity)"%(id_not_det,100*id_not_det/id_n))
print("    detected, wrong holder           : %d (%.1f%% of all identity)"%(id_wrong_holder,100*id_wrong_holder/id_n))
