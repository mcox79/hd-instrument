import os
os.environ.setdefault("OMP_NUM_THREADS","1"); os.environ.setdefault("OPENBLAS_NUM_THREADS","1")
import sys; sys.path.insert(0,"."); sys.path.insert(0,"experiments")
import numpy as np, json
import exp_hub_spoke_word_representation_v1 as HS
codes = HS.spoke_codes(256, 7)
S=HS.shared(); n=len(S["words"])
out={"V":n}
for s in HS.SPOKES4:
    C=codes[s]
    u=np.unique(C,axis=0)
    out[s]={"distinct_codes":int(u.shape[0]),"V":n,
            "max_per_spoke_completion_ceiling":round(float(u.shape[0])/n,4)}
ceil=np.mean([out[s]["max_per_spoke_completion_ceiling"] for s in HS.SPOKES4])
# exact ceiling: a word is recoverable from spoke s only if its code is UNIQUE
uniq={}
for s in HS.SPOKES4:
    C=codes[s]
    _,inv,cnt=np.unique(C,axis=0,return_inverse=True,return_counts=True)
    uniq[s]=round(float(np.mean(cnt[inv]==1)),4)
out["frac_words_with_a_UNIQUE_code_per_spoke"]=uniq
out["mean_over_spokes_ceiling_on_per_spoke_completion"]=round(float(np.mean(list(uniq.values()))),4)
print(json.dumps(out,indent=2))
