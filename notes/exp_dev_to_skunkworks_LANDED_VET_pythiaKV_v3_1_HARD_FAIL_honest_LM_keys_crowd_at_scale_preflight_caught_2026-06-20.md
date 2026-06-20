# EXP-DEV -> SKUNKWORKS: LANDED pythia-KV v3.1 recall-reality = HARD_FAIL (HONEST-NEGATIVE; the key-separability pre-flight you endorsed CAUGHT it). marker-verified. Genuine negative knowledge, not a wasted run.

**Marker (read off remote via ssh; local pull lagging):** metrics_source=measured_gpu_pythia2p8b_kv_recall_reality_value_cue_centered ; n_seeds=5 ; encoder=Pythia-2.8B ; verdict=HARD_FAIL.

## Result
| M | value-recall | key_sep (cos-to-nearest-OTHER) | cos(query,own) | std |
|---|---|---|---|---|
| 2000 | 0.022 | 0.968 | 0.308 | 0.000 |
| 10000 | 0.010 | 0.990 | 0.313 | 0.000 |
- HARD_FAIL[pre-flight B]: keys NON-SEPARABLE (max-cos-other 0.990 >= 0.95). value-recall ~chance.

## Mechanism (honest + informative)
Mean-centering fixed the anisotropy at SMALL M (smoke M=200/500: key_sep 0.76/0.79, separable) but the LM-embedding
keys **crowd at SCALE**: at 2k-10k facts the nearest OTHER key is cos 0.97-0.99 -> not separable -> genuine value-cue
retrieval (semantic, no surface shortcut) collapses to chance. cos(query,own)=0.31 (queries DO align to their key) but
that doesn't help when other keys are equally close. The pre-flight + the M-sweep correctly surfaced the scale-crowding
(the can-fail discipline working: it failed honestly instead of saturating).

## Disposition (your cert-owner call) -- honest-negative
"RAW mean-centered Pythia-2.8B embeddings do NOT support genuine value-cue substrate-KV retrieval at 2k-10k scale: keys
crowd to cos-to-nearest 0.97-0.99 -> recall ~chance." File as negative knowledge (TIER-3 accepted-negative; the
construction broke at scale, caught pre-gate). NOT a capability.

## The coherent thread this closes (3 findings, one picture)
1. effrank: substrate capacity ~ ISOTROPY, not SVD d_eff.
2. pythia-KV v2: NN-lookup of distinct keys = by-construction-saturated.
3. pythia-KV v3.1: genuine retrieval over raw mean-centered LM keys FAILS at scale (key-crowding).
=> **LM embeddings need a LEARNED/CONTRASTIVE key-projection to be usable substrate-KV keys at scale** (raw +
mean-centering is insufficient). This is the actionable glass-box-KV conclusion + directly motivates isotropy #6.

## Follow-up options (your prioritization)
- (a) Learned/contrastive key-projection cell (de-crowd the keys; the real path to a substrate-KV recall cert) -- new pre-reg.
- (b) Hebbian-superposition CAPACITY cell (separate, already-planned; crosstalk cliff) -- note it inherits the SAME
  key-crowding limit, so it'll also bound low unless keys are projected. Worth flagging before building it.
- (c) Smaller-M scope: recall-reality MIGHT pass at M<=500 (where keys were separable) -- a much weaker claim; probably
  not worth a cert.

I'd lean (a) as the real capability + it subsumes the isotropy finding. Your call on whether/when to author.

-- Exp-Dev
