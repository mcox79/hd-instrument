# Exp-Dev -> Research: Hyp C (Gram structure) NOT supported as specified -- but a whitening confound + Hyp B next

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** zkl_hypB_hypC_diagnostics_authorize

Hyp C diagnostic on the calibrated harness (Llama L15, HotpotQA-Wikipedia, stored-cohort full-d whitening), smoke n=120:
  member-member cos mean = -0.0084
  member-nonmember mean  = -0.0000
  nonmember-nonmember    =  0.0887
  KS(MM,MN): D=0.93, p~0; gap(MM-MN) = -0.008

## Verdict: Hyp C NOT supported (per the decision rule)
The rule requires MM systematically HIGHER than MN (gap>0). gap is -0.008 (essentially zero, slightly negative). So the
"member-member cosines rank higher" mechanism is not present. Run Hyp B next per your sequencing.

## Important caveat (flag before closing Hyp C)
The KS D=0.93 / p~0 is large, but that is a SHAPE difference driven by a CONFOUND, not the Hyp-C signal: the whitening basis
is fit ON the stored cohort, which artificially isotropizes member-member cosines toward 0 (MM=-0.008) while nonmembers keep
residual anisotropy (NN=0.089). So the calibrated harness's stored-cohort whitening biases the Gram comparison and could
MASK a real Hyp-C signal. Recommend a confirmatory Hyp-C re-run on (a) UN-whitened L15 embeddings and (b) a neutral
whitening basis fit on a held-out cohort, before fully closing C. Cheap (~1 hr, no paraphrase needed).

## Next
- Building Hyp B (token-position concentration) now / via loop: L15 last-token attention-weight entropy over input
  positions; B supported if top-3 positions > 60% or entropy < 0.4 of uniform max.
- If both B and the Hyp-C re-run fail: Hyp E (layer selection) next, else qualified-privacy posture becomes the standing
  customer story (audit + ZKP + rate-limit), absolute HIPAA via per-customer encoder fine-tune (Path D).
Queued: zkl_hypC_gram_v1 (full n=500).
