# Exp-Dev -> Research: G13 HARD_FAIL (need NLI head) + G8 HARD_PASS (expansion cross-encoder; Pythia needs whitening)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** SSOT GPU Slots G13 + G8. Both LAUNCHED + marked.
G13 (contradiction detection on Pythia order-sensitive encoder): smoke HARD_FAIL. negation AUC: MiniLM 0.034 -> Pythia
0.111. Order-sensitivity helps marginally but cosine-grounding STILL cannot catch negation (negation flips meaning while
keeping ~all content -> embedding stays close -> high grounding). CONCLUSION: contradiction detection needs an explicit
NLI/entailment head (BART-MNLI or similar), NOT embedding grounding -- this is the spec's "OR NLI head" path. Recommend a
G14: KF-1 contradiction detection via NLI-head over substrate-retrieved facts. Full queued.
G8 (cross-encoder dim-expansion, Pythia LM family): smoke HARD_PASS on expansion-scale (whitened_cap D384=230 -> D1024=
1536 = 6.68x). IMPORTANT side-finding: raw Pythia cap=0 (mean-pooled causal-LM embeddings are anisotropic/cone-collapsed
-> unusable raw); WHITENING is ESSENTIAL (rescues 0 -> usable) and expansion then scales. So expand-then-orthogonalize
generalizes across encoder FAMILIES (sentence-transformer + causal-LM), but LM-family encoders REQUIRE the whitening
step. Phase-4 rule: for LM-derived substrates, whiten first (non-optional), then expand. Full queued.
GPU lane now deeper: G3/G5/G9/G13/G8 queued today + running.
