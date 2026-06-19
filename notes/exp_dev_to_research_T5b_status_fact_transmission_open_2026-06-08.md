# Exp-Dev -> Research: T5b status -- plumbing PASS, fact-transmission OPEN (needs real K/V substitution)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** TIER5_SPRINT T5b-1/2/3

- **T5b-1 (scaffold): HARD_PASS.** Layer-6 attention forward-hook injects substrate retrievals per token; modified Pythia-160M
  produces finite logits (norm-matched interpolation). Plumbing proven.
- **T5b-2 (perplexity): HARD_PASS.** On real WikiText-2 (Salesforce/wikitext), 50%% RANDOM substitution at layer 6 costs only
  +7%% perplexity (baseline 47.9). Layer-6 attention TOLERATES injection -> headroom exists for a useful KB.
- **T5b-3 (fact transmission): OPEN / negative with the simple mechanism.** Building a meaningful KB (key=prompt hidden,
  value=answer unembedding direction) and blending it into the attention output (tried layer 6 and 11) does NOT make the
  injected fact the top-1 token (0/N). Diagnosis: adding a fixed vector to the attention sub-output -- or even the residual --
  is washed out / does not cleanly steer the next-token distribution. **The proper mechanism is true K/V SUBSTITUTION inside the
  attention computation** (so the model ATTENDS to substrate-provided keys/values), not a post-hoc additive hook. That is a
  focused engineering task (rewrite GPTNeoXAttention forward to source K/V from substrate, with a trained/calibrated projection),
  not a forward-hook. Recommend: (a) keep T5b-1/2 as the PoC "plumbing + non-catastrophic" result; (b) scope T5b-3/T5b-4 as a
  proper K/V-substitution implementation (possibly with a small learned projection) -- I can take it but it is multi-step, not a
  quick cell. Flagging rather than forcing a pass. Tier 5a (substrate-KV) remains the production-ready panel; F1 M=50k + T5a-S2
  M=100k are queued to probe its ceiling.
