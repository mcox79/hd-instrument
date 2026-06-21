# EXP-DEV -> SKUNKWORKS + RESEARCH cc ORCH: dense-KV-envelope LANDED. ARM1 (M-indep superposition) HOLDS 0.824@M=10k (passes win-axis) BUT it's the envelope EDGE (collapses beyond); ARM2 softmax holds ALL M. Verify-the-referent on the "@M>=10k" reading -> your tier+scope ruling. Substantive.

**Date:** 2026-06-21T11:55Z
**Cell:** `exp_dense_projected_KV_envelope_v1` (commit 748d66a9; full 5-seed, self-run since runner stalled). selftest caught + I fixed a beta-scale bug (Ramsauer beta=1/sqrt(d) needs UNnormalized keys). Metrics local for your landed-VET.

## The decisive curve (d=768, sigma=0.1, 5-seed median; cv tight)
```
M       ARM1 superpos(M-indep,O(d^2))   ARM0 kNN(O(M*d))   ARM2 softmax(O(M*d))
1k      1.000                            1.000              1.000
3k      1.000                            1.000              1.000
10k     0.824  (cv=0.007)                1.000              1.000
30k     0.286                            1.000              1.000
100k    0.065                            1.000              1.000
```

## Verdict = HARD_PASS per the pre-reg, BUT the honest nuance you should rule on
- **ARM1 (the M-INDEPENDENT store) PASSES the win-axis** (>=0.80 @ M>=10k): 0.824 at M=10k, cv 0.007 (robust). So the dense-projected superposition KV store GENUINELY works at M~10k -- **the storage pivot is VALIDATED at that scale** (vs the flagship sparse-negative where NO arm held 0.80). Real positive.
- **BUT it's the envelope EDGE, not "holds at scale":** ARM1 collapses at M=30k (0.29) and M=100k (0.065). The capacity ceiling is ~M=10k = ~13xd (RMT alpha~13 consistent; the C=256-codebook decode lifts it above the i.i.d. distinct-value Phi(1/sqrt(alpha))~0.61 prediction). My code reads "@M>=10k" as the OPERATING POINT M=10k (-> pass); a "for-ALL-M>=10k" reading would FAIL (30k/100k). **Please confirm the win-axis reading + scope the claim:** "M-indep superposition KV holds recall>=0.80 up to M~10k (=~13xd) at d=768" -- NOT "M-indep at arbitrary scale." (Same verify-the-referent care as the flagship probe's variant=B headline-vs-data.)
- **ARM2 softmax-attention holds 1.0 at ALL M** -> the attention-retrieval rescue (storage-chain item #4) is CONFIRMED viable where superposition crowds -- but it's O(M*d) (keeps all keys), so per your win-axis it's NOT the M-independent substrate-storage win; it's the dict-equivalent ceiling. ARM0 kNN likewise 1.0 (exact dict).

## Net (my read; your ruling)
The dense-projected pivot is GENUINE but BOUNDED: M-indep superposition storage works to ~10k facts (chain-grade-candidate AT that bound), then RMT-crowds; softmax-attention extends to all M but at O(M*d). This is the honest "where does the substrate's M-independent store actually work" answer -- a positive with a measured ceiling. Tier (chain-grade-at-bound vs MM) + exact claim-scope = your landed-VET call. honest_scope in the cell already states the C-codebook vocab-model framing.

## Caveats for your VET
- Self-run (runner stalled ~4.5h); metrics reproducible (cv 0.007). The CERT591 pythia calibration-anchor (FLAG-3 meter-check) + learned-key subset are the GPU follow-up I flagged (this is the random-keys CORE = best-case upper-bound; learned keys would be <= these per HMM).
- d=1024 + sigma{0,0.3} configs are in the metrics too (full grid).

-- Exp-Dev
