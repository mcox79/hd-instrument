"""Empirical ceiling of GLASS-BOX distributional is-a: the state-of-the-art unsupervised hypernymy measures
(WeedsPrec, invCL/Lenci-Benotto, SLQS/Santus entropy-generality) on PPMI contexts vs WordNet is-a gold,
frequency-matched 2AFC (chance 0.5). Maps how far distributional-only is-a can go -- does a better measure
break the 0.685 wall, or is it a fundamental ceiling?"""
import os, sys, re, glob, math
import numpy as np
REPO="C:/AI/hd-instrument"; sys.path.insert(0, REPO)
from collections import Counter, defaultdict
from nltk.corpus import wordnet as wn
paths=glob.glob(os.path.join(REPO,"data/corpora/*/cleaned/*.clean.txt"))
raw=" ".join(open(p,encoding="utf-8",errors="ignore").read() for p in paths).lower()
toks=re.findall(r"[a-z]{3,}",raw)[:1400000]
freq=Counter(toks)
STOP=set("the and that was with his her had for you not are but she him they this then them all who its from have were said one out into upon what been their would could very".split())
vocab=[w for w,c in freq.items() if c>=20 and w not in STOP]; vset=set(vocab)
W=4; rows=defaultdict(Counter)
for i,w in enumerate(toks):
    if w not in vset: continue
    for j in range(max(0,i-W),min(len(toks),i+W+1)):
        if j!=i and toks[j] in vset: rows[w][toks[j]]+=1
print("corpus %d tokens, vocab %d"%(len(toks),len(vocab)),flush=True)
# PPMI weights per (word,context)
N=sum(sum(c.values()) for c in rows.values())
ctx_tot=Counter()
for w,c in rows.items():
    for k,v in c.items(): ctx_tot[k]+=v
wtot={w:sum(c.values()) for w,c in rows.items()}
def ppmi(w):
    out={}
    tw=wtot[w]
    for k,v in rows[w].items():
        p=(v/N)/((tw/N)*(ctx_tot[k]/N)+1e-12)
        if p>1: out[k]=math.log(p)
    return out
PP={w:ppmi(w) for w in vocab}
# context entropy (generality of a context): entropy over the words it co-occurs with
ctx_words=defaultdict(Counter)
for w,c in rows.items():
    for k,v in c.items(): ctx_words[k][w]+=v
def cent(k):
    c=ctx_words[k]; t=sum(c.values())
    if t<1: return 0.0
    ps=np.array(list(c.values()),float)/t
    return float(-(ps*np.log(ps+1e-12)).sum())
CE={k:cent(k) for k in ctx_tot}
def weeds(u,v):
    fu=PP[u]; fv=PP[v]; s=sum(fu.values())
    return sum(w for k,w in fu.items() if k in fv)/s if s else 0.0
def invcl(u,v):  # Lenci-Benotto: inclusion of u in v minus inclusion of v in u
    return math.sqrt(max(weeds(u,v)*(1-weeds(v,u)),0))
def slqs(u,v,topn=50):  # Santus: hypernym v is MORE general -> its top contexts have higher entropy
    tu=sorted(PP[u].items(),key=lambda x:-x[1])[:topn]; tv=sorted(PP[v].items(),key=lambda x:-x[1])[:topn]
    eu=np.median([CE[k] for k,_ in tu]) if tu else 0; ev=np.median([CE[k] for k,_ in tv]) if tv else 0
    return 1 - eu/ev if ev>0 else 0.0
def cos(u,v):
    fu=PP[u]; fv=PP[v]; keys=set(fu)&set(fv)
    num=sum(fu[k]*fv[k] for k in keys)
    du=math.sqrt(sum(x*x for x in fu.values())); dv=math.sqrt(sum(x*x for x in fv.values()))
    return num/(du*dv) if du and dv else 0.0
cats=[]
for w in vocab:
    if freq[w]<30: continue
    hyps=set()
    for s in wn.synsets(w,'n')[:2]:
        for path in s.hypernym_paths():
            for h in path[:-1][-3:]:
                for l in h.lemmas():
                    ln=l.name().lower()
                    if ln in vset and ln!=w and freq.get(ln,0)>=20: hyps.add(ln)
    if hyps: cats.append((w,hyps))
rng=np.random.default_rng(42)
def matched(hyps,C,hf):
    band=[w for w in vocab if w not in hyps and w!=C and 0.66*hf<=freq[w]<=1.5*hf]
    if not band: band=[w for w in vocab if w not in hyps and w!=C]
    return band[int(rng.integers(0,len(band)))]
measures=[("cosine (relatedness)",cos),("WeedsPrec",weeds),("invCL",invcl),("SLQS entropy",slqs),
          ("WeedsPrec x SLQS",lambda u,v: weeds(u,v)*max(slqs(u,v),0))]
print("FREQ-MATCHED 2AFC (chance 0.5), n_cats=%d:"%len(cats),flush=True)
for name,f in measures:
    afc=[]
    for C,hyps in cats:
        for h in hyps:
            d=matched(hyps,C,freq[h])
            try: afc.append(int(f(C,h)>f(C,d)))
            except Exception: pass
    afc=np.array(afc); se=afc.std()/math.sqrt(len(afc))
    print("  %-22s 2AFC=%.3f +/-%.3f (n=%d)"%(name,afc.mean(),1.96*se,len(afc)),flush=True)
