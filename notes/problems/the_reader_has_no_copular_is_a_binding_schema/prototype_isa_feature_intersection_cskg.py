"""Feature-INTERSECTION is-a on ConceptNet semantic PROPERTIES (the McRae feature-norm hypothesis, glass-box,
static KG asset -- NOT an LLM). Does semantic-property feature-inclusion capture is-a where distributional
co-occurrence (WeedsPrec 0.685) fails? Compares: (1) SYMBOLIC IsA edge (upper bound, hierarchy=not brain-
faithful), (2) FEATURE-INTERSECTION over NON-IsA property edges (hyponym inherits hypernym's properties + more)."""
import os, sys, gzip, math
import numpy as np
REPO="C:/AI/hd-instrument"; sys.path.insert(0, REPO)
from collections import defaultdict
from nltk.corpus import wordnet as wn
CSKG=os.path.join(REPO,"data/grounding_testbed/cskg.tsv.gz")
# property relations (semantic features that inherit down an is-a); EXCLUDE IsA for the feature test
PROP_RELS={"HasA","HasProperty","CapableOf","UsedFor","AtLocation","PartOf","MadeOf","HasPart","ReceivesAction","Desires","CreatedBy"}
feats=defaultdict(set)        # word -> set of (rel, node2label)  [non-IsA property features]
isa=defaultdict(set)          # word -> set of hypernym labels via IsA
def enw(uri):  # /c/en/doctor/n -> doctor ; only single english words
    p=uri.split("/")
    if len(p)>=4 and p[1]=="c" and p[2]=="en":
        w=p[3]
        return w if w.isalpha() else None
    return None
n=0
with gzip.open(CSKG,"rt",encoding="utf-8",errors="ignore") as f:
    next(f)
    for line in f:
        c=line.rstrip("\n").split("\t")
        if len(c)<7: continue
        a=enw(c[1]); b=enw(c[3]); rel=c[2].split("/")[-1]
        if not a or not b or a==b: continue
        if rel=="IsA": isa[a].add(b)
        elif rel in PROP_RELS: feats[a].add((rel,b))
        n+=1
print("CSKG edges scanned=%d ; words w/ props=%d ; words w/ IsA=%d"%(n,len(feats),len(isa)),flush=True)
# eval set: category nouns with a WordNet hypernym that ALSO appears as a ConceptNet node with properties
import re, glob
paths=glob.glob(os.path.join(REPO,"data/corpora/*/cleaned/*.clean.txt"))
raw=" ".join(open(p,encoding="utf-8",errors="ignore").read() for p in paths[:6]).lower()
from collections import Counter
freq=Counter(re.findall(r"[a-z]{3,}",raw))
cats=[]
for w in list(feats.keys()):
    if freq.get(w,0)<5: continue
    hyps=set()
    for s in wn.synsets(w,'n')[:2]:
        for path in s.hypernym_paths():
            for h in path[:-1][-3:]:
                for l in h.lemmas():
                    ln=l.name().lower()
                    if ln!=w and (ln in feats or ln in isa): hyps.add(ln)
    if hyps: cats.append((w,hyps))
print("eval category nouns=%d"%len(cats),flush=True)
def feat_incl(C,H):  # fraction of H's property-features included in C's (hyponym inherits hypernym's + more)
    fh=feats.get(H,set())
    if not fh: return 0.0
    return len(fh & feats.get(C,set()))/len(fh)
def symbolic_isa(C,H):  # is there an IsA path C->...->H within 3 hops?
    seen={C}; frontier={C}
    for _ in range(3):
        nxt=set()
        for x in frontier: nxt|=isa.get(x,set())
        if H in nxt: return 1.0
        frontier=nxt-seen; seen|=nxt
        if not frontier: break
    return 0.0
rng=np.random.default_rng(42)
allw=[w for w,_ in cats]
def matched(hyps,C):
    band=[w for w in allw if w not in hyps and w!=C]
    return band[int(rng.integers(0,len(band)))] if band else C
for name,f in [("SYMBOLIC IsA (hierarchy)",symbolic_isa),("FEATURE-INTERSECTION (properties)",feat_incl)]:
    afc=[]
    for C,hyps in cats:
        for H in hyps:
            D=matched(hyps,C)
            sh=f(C,H); sd=f(C,D)
            afc.append(1.0 if sh>sd else (0.5 if sh==sd else 0.0))
    afc=np.array(afc); se=afc.std()/math.sqrt(max(len(afc),1))
    informative=sum(1 for x in afc if x!=0.5); print("  %-34s 2AFC=%.3f +/-%.3f (n=%d, informative=%d)"%(name,afc.mean(),1.96*se,len(afc),informative),flush=True)
