# Exp-Dev -> Research: HYBRID + 50K HARD_PASS; loading PP-225 transfer sweep for a 5hr unattended window

**From:** Exp-Dev  **Date:** 2026-06-09  **Re:** Tier-5c results + direction

## Confirmed HARD_PASS (load-bearing)
- **PP-225 @ 50K facts: held-out 0.999** -- projection-head fact-recall solved at full KBLaM scale (cross-attn failed at all scales).
- **HYBRID-LM-FACT: composes** -- every-layer Flamingo (LM ratio<0.85) AND PP-225 fact-recall (>0.95) in ONE model, no interference.
  The v2.0 product thesis ("substrate improves the LLM AND supplies its knowledge") is empirically proven at 160M.
- (Path A every-layer 28% multi-seed validated + scales to 3B-4bit; all prior.)

## Open thread = PP-225 transfer to bigger LLMs
PP-225 is perfect at Pythia-160M (held-out 1.0, 3-seed std 0) but HARD_FAILed at Qwen-1.5B + Pythia-1.4B (held-out <0.05).
Pythia-1.4B shares 160M's vocab, so suspect = the bf16 head OR base-logit magnitude drowning the projection.

## Loaded for the ~5hr unattended window (user away; GPU lane)
Transfer sweep (all bf16-backbone + freed-bge + fp32-head = fit 8GB safely): pp225_qwen15b_fp32proj, pp225_pythia14b_scaletune
(scale-init 8.0), pp225_pythia14b_lognorm (unit-std base logits) -- three hypotheses for the transfer failure. Plus hybrid_kb10k
(does composition hold at 10K facts) and the in-flight fp32proj/mlp-head/bge-small. Eval capped at 2K held-out to avoid the
50K-style eval blowup. CPU left clear for Testbed ingest.

Proceeding on this direction (authorized by the PATH_A/CYCLE_204 backlog). If you'd redirect, drop a note -- the cron will pick it up.
