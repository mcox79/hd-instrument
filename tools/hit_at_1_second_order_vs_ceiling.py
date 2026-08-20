"""How often does plain SECOND-ORDER counting put the anomalous word FIRST?

**THIS DECIDES WHETHER THE F5 EVALUATION CAN DISCRIMINATE AT ALL.** The F5 design pre-committed:
*"IT FAILS IF co-occurrence surprisal matches it -- then the monitor is re-deriving counting."*
The bar was set with FIRST-order PMI (median rank 4.0 of ~9). Second-order counting -- comparing
each word's whole co-occurrence PROFILE with its neighbours' -- reads median rank **1.0 under BOTH
tie conventions** on four independently-built sets, with ~0 tie mass. This prints the hit@1 rate,
which is the number a human can act on, beside the item set's own ~86% ceiling.
"""
import os, json, sys, math, collections
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np
sys.path.insert(0,"."); sys.path.insert(0,"tools")
from rank_with_ties import rank_with_ties
from hdlab.corpus_registry import CorpusRegistry
from hdlab.reading_grounding_loop import content_lemmas, normalize_lemma

SET=os.environ.get("DIAG_SET","data/anomaly_set_frequency_matched_v8.json")
S=json.load(open(SET,encoding="utf-8"))["items"]
HAND=SET.replace(".json","_handscores.json")
# ALL_ITEMS forces every item to be scored even when hand-scores exist. Needed for REPLICATION:
# the seed-variant sets have no hand-scores, so a CLEAN-only run on v8 against all-items runs on the
# others would compare two different populations -- "no number crosses populations" is the standing
# rule, and a replication that silently does so is worse than no replication.
ALL_ITEMS = os.environ.get("DIAG_ALL_ITEMS","0")=="1" or not os.path.exists(HAND)
V=({i:"CLEAN" for i in range(len(S))} if ALL_ITEMS else
   {v["index"]:v["verdict"] for v in json.load(open(HAND,encoding="utf-8"))["verdicts"]})
print("POPULATION: %s (%d items)"%("ALL ITEMS" if ALL_ITEMS else "hand-scored CLEAN only",
      sum(1 for x in V.values() if x=="CLEAN")))
sents=list(CorpusRegistry().handles["simplewiki"].take(8000))
held={i["sentence_original"] for i in S}
kept=[s for s in sents if s not in held]
print("LEAK CONTROL: %d item sentences excluded, %d remain"%(len(sents)-len(kept),len(kept)))
df,co,n=collections.Counter(),collections.defaultdict(collections.Counter),0
for s in kept:
    u=set(content_lemmas(s)); n+=1; df.update(u)
    for w in u: co[w].update(u)
cache={}
def _lem(t): return normalize_lemma("".join(c for c in t.lower() if c.isalpha()))
def prof(w):
    v=cache.get(w)
    if v is None:
        pw=df[w]/n; v={}
        for c,j in co[w].items():
            if c==w: continue
            pc=df[c]/n
            if pw>0 and pc>0 and j>0:
                p=math.log((j/n)/(pw*pc))
                if p>0: v[c]=p
        nrm=math.sqrt(sum(x*x for x in v.values())) or 1.0
        v={k:x/nrm for k,x in v.items()}; cache[w]=v
    return v
def fit(w,ctx):
    vw=prof(w)
    if not vw: return 0.0
    o=[]
    for c in ctx:
        if c==w: continue
        vc=prof(c)
        if not vc: continue
        a,b=(vw,vc) if len(vw)<len(vc) else (vc,vw)
        o.append(sum(x*b.get(k,0.0) for k,x in a.items()))
    return float(np.mean(o)) if o else 0.0
def run(items,field,per_item=None):
    hit=tot=0
    for it in items:
        t=it[field].split()
        # LEMMATISE BEFORE LOOKUP. `docfreq`/`cooc` are keyed by `content_lemmas` output, so a SURFACE
        # lookup misses every inflected form: "achievements" is absent while "achievement" is present. Two
        # consequences, both measured 2026-08-21: inflected words were silently EXCLUDED from the candidate
        # slate (a hidden population restriction), and any that slipped in scored the unknown-word value and
        # outranked real candidates. **Fixing it moved second-order counting's discrimination from +10.9 pp
        # to +28.3 pp and dropped its ORIGINAL-sentence hit rate from 42.6% to 12.5%** -- so the "most of
        # the floor's skill is a slot effect" reading was substantially an artifact of this bug.
        cand=sorted({j for j,x in enumerate(t) if _lem(x) in df}|{it["anomaly_token_index"]})
        if len(cand)<3: continue
        w=[_lem(t[j]) for j in cand]
        r=rank_with_ties([-fit(x,w) for x in w],cand.index(it["anomaly_token_index"]))
        tot+=1; ok=(r.pessimistic==1); hit+=ok
        if per_item is not None: per_item.append(ok)
    return hit,tot
clean=[it for i,it in enumerate(S) if V[i]=="CLEAN"]
A=[];B=[]
h,t=run(clean,"sentence_anomalous",A); ho,to=run(clean,"sentence_original",B)
print()
print("SECOND-ORDER COUNTING, %d CLEAN items, hit@1 under the PESSIMISTIC convention"%t)
print("  anomalous sentence : %3d of %3d  = %5.1f%%   <- how often counting puts the PLANTED word first"%(h,t,100*h/t))
print("  original  sentence : %3d of %3d  = %5.1f%%   <- the same slot holding the CORRECT word (must be LOW)"%(ho,to,100*ho/to))
print()
print("  item-set ceiling   : ~86%% (17 of 120 items hand-scored WEAK -- no anomaly to find)")
print("  headroom for F5    : %5.1f percentage points"%(86.0-100*h/t))
print()
print("*** THE NUMBER THAT ACTUALLY MATTERS -- PAIRED, SAME ITEMS, SAME SLOTS ***")
print("The floor flags that slot first %.1f%% of the time EVEN WHEN THE WORD IS CORRECT, so most of"%(100*ho/to))
print("its apparent skill is a property of the SLOT, not of the anomaly. Median rank 1.0 is NOT")
print("saturation of the task. The DISCRIMINATION is the paired difference:")
import random
rng=random.Random(11)
pairs=list(zip(A,B))
d=[]
for _ in range(20000):
    smp=[pairs[rng.randrange(len(pairs))] for _ in pairs]
    d.append(100.0*(sum(a for a,_ in smp)-sum(b for _,b in smp))/len(smp))
lo,hi=np.percentile(d,[2.5,97.5])
print("  anomalous %.1f%% - original %.1f%% = %+.1f pp, 95%% CI [%+.1f, %+.1f]"%(100*h/t,100*ho/to,100*h/t-100*ho/to,lo,hi))
# McNemar on the discordant pairs
b_=sum(1 for a,x in pairs if a and not x); c_=sum(1 for a,x in pairs if x and not a)
import math as _m
chi=(abs(b_-c_)-1)**2/(b_+c_) if (b_+c_)>0 else 0.0
pv=_m.erfc(_m.sqrt(chi/2)) if chi>0 else 1.0
print("  McNemar discordant: %d anomaly-only, %d original-only, chi2=%.2f p=%.4f"%(b_,c_,chi,pv))
print("  VERDICT:", "REAL DISCRIMINATION (CI excludes 0)" if lo>0 else "NOT DISCRIMINATIVE at this n")
