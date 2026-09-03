"""PROTOTYPE of the IDEAL system's Stage 4 (is-a INHERITANCE) via brain-faithful FEATURE-OVERLAP.

Cited in SOLVED.md / IDEAL_copular_is_a_architecture_2026-09-02.md. Tests whether a glass-box distributional
feature-overlap space (PPMI-SVD built from raw reading, NO LLM) can support is-a INHERITANCE from a copular
binding ("X is a doctor" -> doctor IS-A person). Gold = WordNet hypernym chains (a static lexical EVAL asset).

Brain frame (PINNED, from the drill): the ATL hub represents category membership as EMERGENT feature-overlap,
NOT a symbolic hierarchy (Rogers 2004; Patterson 2007). But is-a is DIRECTIONAL (doctor IS-A person, not the
reverse), and directionality comes from FEATURE GENERALITY / INCLUSION -- a superordinate has a broader, more-
shared context distribution than its hyponyms (distributional-inclusion hypothesis; Geffet & Dagan 2005; Weeds
& Weir; Santus). So we compare symmetric cosine (relatedness) vs directional generality vs WeedsPrec feature
inclusion. Fair test: FREQUENCY-MATCHED 2AFC (superordinates are frequent -- a raw 2AFC is confounded).

Run: .venv/Scripts/python.exe notes/problems/the_reader_has_no_copular_is_a_binding_schema/prototype_isa_inheritance_feature_overlap.py
"""
import os, sys, re, glob, math
import numpy as np
REPO="C:/AI/hd-instrument"; sys.path.insert(0, REPO)
from collections import Counter, defaultdict
from hdlab.distributional_meaning_channel import ppmi_svd
import scipy.sparse as sp
from nltk.corpus import wordnet as wn
paths=glob.glob(os.path.join(REPO,"data/corpora/*/cleaned/*.clean.txt"))
raw=" ".join(open(p,encoding="utf-8",errors="ignore").read() for p in paths).lower()
toks=re.findall(r"[a-z]{3,}",raw)[:1200000]
freq=Counter(toks)
STOP=set("the and that was with his her had for you not are but she him they this then them all who its from have were said one out into upon what been their would could very".split())
vocab=[w for w,c in freq.items() if c>=20 and w not in STOP]
vset=set(vocab); vidx={w:i for i,w in enumerate(vocab)}
W=4; rows=defaultdict(Counter)
for i,w in enumerate(toks):
    if w not in vset: continue
    for j in range(max(0,i-W),min(len(toks),i+W+1)):
        if j!=i and toks[j] in vset: rows[w][toks[j]]+=1
M=sp.lil_matrix((len(vocab),len(vocab)))
for w,ctr in rows.items():
    r=vidx[w]
    for c,n in ctr.items(): M[r,vidx[c]]=n
M=M.tocsr(); phi=ppmi_svd(M,svd_k=100); phin=phi/(np.linalg.norm(phi,axis=1,keepdims=True)+1e-9)
gen={}; ctxset={}
for w in vocab:
    ctr=rows[w]; tot=sum(ctr.values())
    ps=np.array(list(ctr.values()),float)/max(tot,1)
    gen[w]=float(-(ps*np.log(ps+1e-12)).sum()) if tot else 0.0
    ctxset[w]=ctr
def cos(a,b): return float(phin[vidx[a]]@phin[vidx[b]])
# WeedsPrec: fraction of C's context MASS that is INCLUDED in cand's contexts (feature inclusion, asymmetric)
def weedsprec(C,cand):
    cc=ctxset[C]; dd=ctxset[cand]; tot=sum(cc.values())
    if tot<1: return 0.0
    return sum(v for k,v in cc.items() if k in dd)/tot
cats=[]
for w in vocab:
    if freq[w]<30: continue
    ss=wn.synsets(w,'n')
    if not ss: continue
    hyps=set()
    for s in ss[:2]:
        for path in s.hypernym_paths():
            for h in path[:-1][-3:]:
                for l in h.lemmas():
                    ln=l.name().lower()
                    if ln in vset and ln!=w and freq.get(ln,0)>=20: hyps.add(ln)
    if hyps: cats.append((w,hyps))
byfreq=sorted(vocab,key=lambda w:freq[w])
def matched_distractor(rng,hyps,C,hf):
    # random vocab word with freq within 1.5x of hf, not a hypernym
    band=[w for w in vocab if w not in hyps and w!=C and 0.66*hf<=freq[w]<=1.5*hf]
    if not band: band=[w for w in vocab if w not in hyps and w!=C]
    return band[int(rng.integers(0,len(band)))]
rng=np.random.default_rng(42)
def evalf(scoref):
    afc=[]; tops=[]
    for C,hyps in cats:
        for h in hyps:
            d=matched_distractor(rng,hyps,C,freq[h])   # FREQUENCY-MATCHED distractor
            sh=scoref(C,h); sd=scoref(C,d)
            afc.append(int(sh>sd))
        sc=sorted(((scoref(C,w),w) for w in vocab if w!=C),reverse=True)[:10]
        tops.append(int(any(h in [w for _,w in sc] for h in hyps)))
    return np.mean(afc),np.mean(tops),len(afc)
scorers=[("SYMMETRIC cosine",cos),
         ("DIRECTIONAL sim x generality",lambda C,w: cos(C,w)*(1/(1+math.exp(-(gen.get(w,0)-gen.get(C,0)))))),
         ("WeedsPrec (feature inclusion)",weedsprec),
         ("cosine x WeedsPrec",lambda C,w: cos(C,w)*weedsprec(C,w))]
print("is-a recovery, FREQUENCY-MATCHED 2AFC (removes the frequency confound; chance=0.5), n_cats=%d:"%len(cats))
for name,f in scorers:
    a,t,n=evalf(f); print("  %-32s 2AFC=%.3f  top10=%.3f  (n_afc=%d)"%(name,a,t,n))
