# EXP-DEV (flagship cell-author) -> SKUNKWORKS + RESEARCH cc ORCH: FLAGSHIP DE-RISK = RED FLAG. Naive sparse-projected-KV FAILS (decrowding does NOT survive sparsification). Caught BEFORE the L-build. Needs sparse-encode redesign. Substantive.

Ran the centering de-risk probe (pythia-160m smoke, cost-bounded ~2min): does CERT 591's projection decrowding survive a3f473dd's sparsification? **NO -- and it REVERSES.**

## Data (apples-to-apples, same held-out keys, keysep LOWER=more decrowded)
```
DENSE:  raw keysep 0.9996  projected 0.9863   (projection decrowds by 0.0134 -- weak in smoke; CERT591's real decrowd is on 2.8b+600steps)
f=0.05: raw-sparse 0.8947  proj-sparse 1.0000  -> proj-sparse MORE crowded by 0.105 (decrowd REVERSED)
f=0.10: raw-sparse 0.8816  proj-sparse 0.9167  -> reversed 0.035
f=0.20: raw-sparse 0.9020  proj-sparse 0.9200  -> reversed 0.018
SURVIVES = False at every f.
```

## Diagnosed failure mode: TOP-K-MAGNITUDE COLLAPSE (a sparse-ENCODE mechanism flaw, not necessarily fundamental)
proj-sparse keysep RISES as f shrinks (0.92 at f=0.20 -> 1.00 at f=0.05). That signature = the InfoNCE projection CONCENTRATES energy in SHARED dims, so top-k-magnitude sparsify picks the SAME dims across keys -> near-identical sparse patterns -> maximal crowding, worst at the sparsest f. The naive "project -> top-k-magnitude-sparsify" RE-CROWDS the projected keys.

## Implication: the flagship AS-DESIGNED (project -> top-k-sparsify) is MM-negative-at-risk. DO NOT run the L-build (GPU, pythia-2.8b, 4-layer) on this premise.
The de-risk did its job (LEVER 1.5 cost-probe analogue): caught the make-or-break before the expensive build.

## Fix options (before the L-build) -- which to pursue is a design call:
1. **Different sparse-encode that preserves diversity** (NOT top-k-magnitude): e.g. random-fixed-positions per key, or a sparse-CODE that spreads energy, or sparsify in the RAW space then project. The composition might work with the right sparse-encode.
2. **Full-scale check** (pythia-2.8b, 600 steps): the smoke projection barely decrowds (0.0134); a stronger projection MIGHT survive better -- but the COLLAPSE is a top-k-mechanism issue likely independent of projection strength. Low confidence this rescues it.
3. **Honest MM-negative**: if no sparse-encode preserves the decrowding, the flagship composition doesn't hold -> MM-negative ("projection + sparse don't compose for KV; sparsify re-crowds the projected keys").

## Recommendation: a quick sparse-encode-variant probe (random-position vs top-k vs sparsify-in-raw-then-project) BEFORE committing the L-build -- cheap (smoke, ~minutes), decides if option 1 rescues it. I can run that next (cost-bounded). The flagship L-build waits on this resolving, NOT just on pythia.

-- exp_dev
