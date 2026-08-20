"""Does the co-occurrence floor RANK the hand-scored CLEAN items better than the WEAK ones?

**WRITTEN TO CHECK ONE OF MY OWN CLAIMS, AND IT WITHDREW IT.** The 2026-08-21 F5-bar commit listed
three "independent confirmations that the item set is sound", the third being *"co-occurrence
surprisal separates the 102 hand-scored CLEAN items from the 17 hand-scored WEAK ones, so an
independent machine measure agrees with the human pass."*

**IT DOES NOT SEPARATE AT THIS n.** mean(WEAK) - mean(CLEAN) = **+0.54, 95% CI [-1.34, +2.60]**,
Mann-Whitney **p = 0.535**. The DIRECTION is right -- WEAK items rank worse, median 5.0 vs 4.0 --
but 17 WEAK items cannot resolve a gap that size.

**TWO SEPARATE FAULTS, AND THE FIRST IS THE ONE THAT MATTERS:**

1. **THE NUMBER I ORIGINALLY QUOTED CAME FROM THE LEAKED RUN** (CLEAN 2.5 vs WEAK 4.0), and I kept
   the CONCLUSION after fixing the leak without re-running the comparison that produced it. *Fixing
   an input invalidates every number downstream of it, including the ones that still look right.*
2. **I READ AN UNDERPOWERED POSITIVE AS A CONFIRMATION** -- the mirror of the recorded
   most-expensive error in this project (reading an underpowered NULL as a capability statement,
   three times in one night). A median gap with no CI is not a finding in either direction.

**WITHDRAWN, NOT REFUTED.** An underpowered test is not evidence the hand-scores disagree with the
floor; it is evidence the question was not asked with enough items. The other two confirmations in
that commit are unaffected and stand: FREQUENCY's delta is +0.00/+0.50/+0.75/+0.50 across four sets
(the matching worked), and POSITION/LENGTH/CONSTANT read EXACTLY +0.00 (no positional or length
artifact) -- that one is exact arithmetic, not a statistic.

Promoted from `scratch/` because a durable claim now cites it (CLAUDE.md: a scratch script cited as
the provenance of a number is no longer throwaway).
"""
import os, json, sys, math, collections, random
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np
sys.path.insert(0,"."); sys.path.insert(0,"tools")
from rank_with_ties import rank_with_ties
from hdlab.corpus_registry import CorpusRegistry
from hdlab.reading_grounding_loop import content_lemmas, normalize_lemma
S=json.load(open("data/anomaly_set_frequency_matched_v8.json",encoding="utf-8"))["items"]
V={v["index"]:v["verdict"] for v in json.load(open("data/anomaly_set_frequency_matched_v8_handscores.json",encoding="utf-8"))["verdicts"]}
sents=list(CorpusRegistry().handles["simplewiki"].take(8000))
held={i["sentence_original"] for i in S}
kept=[s for s in sents if s not in held]
df,co,n=collections.Counter(),collections.defaultdict(collections.Counter),0
for s in kept:
    u=set(content_lemmas(s)); n+=1; df.update(u)
    for w in u: co[w].update(u)
def pmi(w,ctx):
    o=[c for c in ctx if c!=w]
    if not o: return 0.0
    pw=df[w]/n; v=[]
    for c in o:
        pc,pj=df[c]/n,co[w][c]/n
        if pw>0 and pc>0: v.append(math.log(pj/(pw*pc)) if pj>0 else -8.0)
    return float(np.mean(v)) if v else 0.0
def _lem(t):
    """LEMMATISE: df/co are keyed by content_lemmas output, so a SURFACE lookup misses every
    inflected form. This whole file's first result was computed WITHOUT this and is superseded."""
    return normalize_lemma("".join(c for c in t.lower() if c.isalpha()))


def mids(group):
    out=[]
    for it in group:
        t=it["sentence_anomalous"].split()
        cand=sorted({j for j,x in enumerate(t) if _lem(x) in df}|{it["anomaly_token_index"]})
        if len(cand)<3: continue
        w=[_lem(t[j]) for j in cand]
        sc=[-pmi(x,w) for x in w]
        out.append(rank_with_ties(sc,cand.index(it["anomaly_token_index"])).midpoint)
    return out
A=mids([it for i,it in enumerate(S) if V[i]=="CLEAN"])
B=mids([it for i,it in enumerate(S) if V[i]=="WEAK"])
print("CLEAN n=%d median %.2f mean %.2f | WEAK n=%d median %.2f mean %.2f"%(len(A),np.median(A),np.mean(A),len(B),np.median(B),np.mean(B)))
rng=random.Random(7)
d=[np.mean([rng.choice(B) for _ in B])-np.mean([rng.choice(A) for _ in A]) for _ in range(20000)]
lo,hi=np.percentile(d,[2.5,97.5])
print("bootstrap mean(WEAK)-mean(CLEAN) = %+.2f, 95%% CI [%+.2f, %+.2f]"%(np.mean(B)-np.mean(A),lo,hi))
# Mann-Whitney U via normal approx with tie correction
allv=A+B; ranks={}
srt=sorted(range(len(allv)),key=lambda i:allv[i]); i=0
while i<len(srt):
    j=i
    while j+1<len(srt) and allv[srt[j+1]]==allv[srt[i]]: j+=1
    r=(i+j)/2.0+1
    for k in range(i,j+1): ranks[srt[k]]=r
    i=j+1
RA=sum(ranks[i] for i in range(len(A)))
U=RA-len(A)*(len(A)+1)/2.0
mu=len(A)*len(B)/2.0; sd=math.sqrt(len(A)*len(B)*(len(A)+len(B)+1)/12.0)
z=(U-mu)/sd; p=2*(1-0.5*(1+math.erf(abs(z)/math.sqrt(2))))
print("Mann-Whitney U=%.1f z=%+.2f p=%.3f"%(U,z,p))
print("VERDICT:", "SEPARATES (CI excludes 0)" if lo>0 else "DOES NOT SEPARATE at this n -- CI includes 0")
