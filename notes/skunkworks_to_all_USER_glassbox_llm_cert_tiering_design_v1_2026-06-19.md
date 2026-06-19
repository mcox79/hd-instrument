# SKUNKWORKS (cert-owner) -> ALL + USER: GLASS-BOX LLM cert-tiering design v1 (USER-authorized "yes on the glass box llm"). The differentiator = a generative system where EVERY output carries its own honesty-tier (KNOWN / COMPOSED / PREDICTED) + provenance + calibrated confidence. The cert-handle: PREDICTED is a NEW provenance tier QUARANTINED from the cert-count; the integration-check gains a no-masquerade rule (no PREDICTED dressed as KNOWN). Builds on substrate-native LM pieces we already have + the B1/B3 better-decoding lever. (Filename has to_all_USER.)

**From:** Skunkworks (cert-owner)  **To:** ALL + USER  **Date:** 2026-06-19  **Re:** Glass-box LLM cert-tiering design (Barrier-2 architecture).

## The thesis (USER's correction of my Barrier-2 framing)
The ConceptNet completion HARD_FAIL was a CORPUS-SIZE artifact (bge has a huge pretraining corpus; the substrate doesn't yet), NOT a prediction-incapacity. The substrate CAN predict given corpus. So instead of "be a verifier not a predictor," the prize is: **an LLM-equivalent that is fully INSPECTABLE -- you can track/see every prediction's basis.** Nobody has a fully-inspectable LLM. The substrate's invertible algebra (bind/unbind) + cert-architecture make it uniquely possible.

## The 3-tier integrity model (the core innovation)
Every token / claim the system emits is TAGGED:

| Tier | What it is | Confidence signal | Provenance |
|---|---|---|---|
| **KNOWN** | backed by a cert-grade atom | geometric resonance + cert-tier | unbind -> the exact backing atoms |
| **COMPOSED** | derived via substrate algebra from KNOWN atoms | composition-depth-discounted resonance (cleanup-augmented, B1) | the composition path (which atoms, which binds) |
| **PREDICTED** | corpus/LM probability estimate, ungrounded | the LM probability | "predicted from corpus statistics, NOT a backed claim" |

The user's "track/see if we want to" = you can inspect any output's tier + provenance + confidence on demand.

## Architecture (4 layers)
1. **Prediction layer** (the corpus/probability part -- the gap the substrate lacks alone): EITHER (a) HYBRID with a light LM for the next-token distribution, OR (b) substrate-NATIVE n-gram/bundling LM. We ALREADY have substrate-native LM pieces (value-mine, mostly smoke/middle): `substrate_direct_gen_lm_2ndorder_trigram`, `hoc1_word_bigram`, `substrate_friston_fep_trigram`, `kgram_xor`. So the native path has precedent.
2. **Grounding/verification layer** (the substrate's edge): each predicted token/claim is checked against cert-grade knowledge via geometric resonance. Resonates with a cert-grade atom -> tag KNOWN + provenance. Doesn't -> tag PREDICTED.
3. **Composition layer**: multi-step reasoning via the substrate algebra WITH cleanup-between-hops (the B1 resonator solution, smoke 6x -> cert via the q_b1 A/B-iterate) -> tag COMPOSED + the path + depth-discounted confidence.
4. **Refuse-gate**: low-confidence + ungrounded -> REFUSE (the cert-grade refuse-gate, 0.81-0.96 AUROC multi-corpus).

## The cert-architecture extensions (MY lane -- the integrity-handle)
1. **NEW provenance tier: `LM_PREDICTED`** -- below SMOKE_ONLY (an LM-estimate is not even a smoke-experiment). QUARANTINED from the cert-count + from cap-int Track-A (I1 cert-grade-required already blocks it). An LM-guess NEVER counts as a cert atom. Strict tier-separation.
2. **NEW integration-check rule (v1.3 candidate): no-masquerade** -- no output tagged PREDICTED may be presented/stored as KNOWN or COMPOSED. The no-Goodhart discipline (inst-239) applied to generation: an LM-guess dressed as a backed fact is the worst failure mode for a trust-product. Gate it structurally.
3. **Per-output cert-tagging** -- the glass-box-LLM's outputs are tiered token-by-token (KNOWN/COMPOSED/PREDICTED), each with its confidence + provenance. The integrity-layer is the OUTPUT contract, not a wrapper.

## Why this is best-in-class (uniquely enabled)
- Geometric confidence (refuse-gate, cert-grade) -> the KNOWN/PREDICTED boundary is MECHANICAL, not a softmax guess.
- Algebraic provenance (unbind) -> KNOWN/COMPOSED outputs carry their EXACT decomposition (explainability by construction).
- Structural integrity (cert-architecture) -> PREDICTED can't masquerade as KNOWN.
- = a generative system that always knows, and shows, which of its words are known vs composed vs guessed. No LLM / RAG / KG does this.

## Honest risks / open questions (for the team + USER)
- **Hybrid relaxes the no-LLM-in-loop methodology rule** -- but ONLY for the PRODUCT's prediction-layer, with PREDICTED outputs quarantined (tagged, never cert). The agent-sessions' own reasoning stays no-LLM. (USER authorizing the product direction.)
- **Calibration:** the geometric-confidence -> KNOWN/PREDICTED threshold must be cert-VET'd (a pre-reg'd AUROC band, like the refuse-gate) -- else the tiering is vibes. This is a cert-gated sub-experiment.
- **Native-vs-hybrid prediction-layer:** native (substrate n-gram) avoids LLM-dependency but needs corpus; hybrid is faster. A/B-testable.

## Routing (a parallel thread; not derailing the current 20h lanes)
- **Skunkworks (me):** own the cert-tiering spec (the LM_PREDICTED tier + the no-masquerade integration-check rule + the calibration cert-band). I'll draft the v1.3 integration-check extension when this thread activates.
- **Research:** scope the prediction-layer (native LM value-mine vs hybrid light-LM) + the corpus question.
- **Exp-Dev:** a calibration pilot (geometric-confidence -> KNOWN/PREDICTED separation AUROC) when prioritized.
- **USER:** steer -- native vs hybrid prediction-layer? priority vs the current 20h (q_b1 / 5-MM / Track-A)?

-- Skunkworks (cert-owner)
