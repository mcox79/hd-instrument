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
# FIX pipeline signal-loss waterfall, per type: gold -> detected(pred found) -> bound(holder+prop) ; + typing
d=defaultdict(lambda: defaultdict(int))
for sent in sents:
    toks=[r[1] for r in sent]; up=pos.tag(toks)
    heads=arc.parse(toks,up).heads
    base=set(M.extract_entity_states(toks,up,arc,lab))
    fix=base | E.robust_cop(toks,up,heads,gate=True)
    fix_props={p for (_h,p) in fix}
    for (h,p,t) in E.typed_gold(sent):
        d[t]["gold"]+=1
        det = p in fix_props
        if det: d[t]["detected"]+=1
        if (h,p) in fix: d[t]["bound"]+=1
        elif det: d[t]["det_wrong_holder"]+=1
        else: d[t]["not_detected"]+=1
        pt=E.predicted_type(toks,up,h,p); pc="ident" if pt=="ident" else "pred"; gc="ident" if t=="ident" else "pred"
        if pc==gc: d[t]["typed_ok"]+=1
TOT=defaultdict(int)
print("FIX signal-loss waterfall (the best system), per Higgins type:")
print("  type       gold  detected  bound  | lost@detect  lost@holder  typed_ok")
for t in ("pred_adj","pred_nom","ident"):
    x=d[t]
    for k in x: TOT[k]+=x[k]
    print("  %-9s %4d  %6d  %5d  | %6d      %6d      %.3f"%(
        t,x["gold"],x["detected"],x["bound"],x["not_detected"],x["det_wrong_holder"],x["typed_ok"]/x["gold"]))
g=TOT["gold"]
print("  %-9s %4d  %6d  %5d  | %6d      %6d      %.3f"%("ALL",g,TOT["detected"],TOT["bound"],TOT["not_detected"],TOT["det_wrong_holder"],TOT["typed_ok"]/g))
print("\nWATERFALL (fraction of gold retained):")
print("  gold clauses (brain ~1.0)      : %d (1.000)"%g)
print("  after DETECTION                : %d (%.3f)  -> lost %.3f to detection (labeler cop-recall / hard equatives)"%(TOT["detected"],TOT["detected"]/g,1-TOT["detected"]/g))
print("  after HOLDER binding (= fix)    : %d (%.3f)  -> lost %.3f more to holder attach (equative reversal)"%(TOT["bound"],TOT["bound"]/g,(TOT["detected"]-TOT["bound"])/g))
print("  typing accuracy (separate axis): %.3f"%(TOT["typed_ok"]/g))
