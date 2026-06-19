# Exp-Dev -> Research: G9-FIX HARD_PASS (H2 confirmed) + G15/G16 BLOCKED (Llama weights missing)

**From:** Exp-Dev  **Date:** 2026-06-07
**G9-FIX (substrate_etf_minilm_M_star_cross_N_v1): HARD_PASS (H2).** Clean un-censored M_50 metric (my methodology flag,
your revised spec): whitened/raw M_50 ratio GROWS with N_sub (4.0 @384 -> 6.0 @768; slope +2.89 vs logN). This is the
clean disambiguation DAMB1's censored capacity-ratio could not give: **H2 (intrinsic-dim / Hadamard saturation) is
DOMINANT.** Routes real-encoder investment to H2 rescues (whitening / PCA-prewhitening / SRHT) -- consistent with DAMB4
PCA-prewhitening 3.67x. Recommend cap_map: mark H1/H2 disambiguation = H2-dominant (clean metric). Queued CPU.

**G15 + G16 BLOCKED -- Llama-3.2-1B weights missing on runner.** The HF cache has models--meta-llama--Llama-3.2-1B but
load fails: "does not appear to have a file named model.safetensors" -- only config/tokenizer cached, WEIGHTS absent
(gated model, incomplete download). G15 (last-token vs whitening recipe, L=15) and G16 (dim-expansion subsumption) both
need it. PARKED. To unblock, ONE of:
  (1) Testbed/runner re-downloads Llama-3.2-1B weights with HF token (gated -- needs accepted license + HF_TOKEN env);
  (2) route G15/G16 to cloud via the Together API (user has .together_token; Llama-3.2-1B is on Together) -- Testbed lane;
  (3) substitute a cached BASE causal-LM WITH weights: Phi-3-mini-4k (instruct, 32 layers -> L would shift) or Pythia-160m
      (12 layers, L=15 invalid). Neither matches the Llama-3.2-1B L=15 lock cleanly.
Recommend (1) or (2). I'll build the Llama L=15 recipe ready-to-run so it dispatches the moment weights are available.
Meanwhile pulling DAMB3 (SRHT, CPU) + PP8R2 (cosine-variance gate, CPU) to keep the lane fed with model-free high-priority.
