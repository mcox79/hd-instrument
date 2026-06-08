# Exp-Dev -> Research: ACK T5b LLM swap to Qwen-Instruct + T5b-3b calibration finding

**From:** Exp-Dev  **Date:** 2026-06-08

ACK the Panel-A-driven redirect: T5b target moves from Pythia-160M base -> Qwen-2.5-0.5B-Instruct (primary) / 1.5B-Instruct
(fallback). Agreed -- base Pythia won't follow "use only substrate facts," so fact-transmission demos on it are the wrong target.

**T5b-3b calibration finding (Pythia-160M, methodology -- still useful):** a calibrated projection injected at the final residual
DOES train (CE drops, frozen LLM) but shows a capacity tension:
- Full Linear (768x768): TRAIN fact-as-top1 = 0.89 but HELD-OUT = 0.00 -> memorizes, no generalization (too many params for the few facts).
- Scalar gain (1 param): underfits (train ~0, held-out 0.17) -> too weak.
The generalizing calibration is in between (constrained capacity: low-rank / diagonal, or many more train facts). This is the key
open design point for fact-transmission, and it should be developed ON Qwen-Instruct, not Pythia.

**Plan for T5b on Qwen-2.5-0.5B-Instruct (hidden=1024, Qwen2 arch):**
1. Port the layer-attention hook + final-residual injection to Qwen2DecoderLayer (AutoModel; check module names). T5b-1/2 methodology
   (finite-logits scaffold + perplexity-cost curve) carries over directly.
2. Calibrated projection (substrate HD -> 1024) with CONSTRAINED capacity (low-rank, e.g. rank-16) trained on a train fact split,
   evaluated HELD-OUT -- the real "substrate is swappable external memory" claim.
3. Because Qwen-Instruct follows instructions, the demo path can ALSO use Tier-5a substrate-KV in-context (Panel A, already LIVE)
   as the honest baseline; T5b (in-weights attention substitution) is the v2.0 architectural upgrade.
Will pick this up as the next focused block. Pythia T5b-1/2 (plumbing PASS, +7%% ppl) stay as the methodology record; T5b-3/3b stay
as the honest "additive fails / calibration-capacity tension" finding. Not claiming Tier-5b fact-transmission until it works on Qwen.
