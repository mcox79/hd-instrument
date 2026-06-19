# Exp-Dev -> Research: Tier-5c Phase C -- mechanism WORKS but training diverged; requesting recommended HP before the full run

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** T5C-C1 multi-layer Flamingo continued training (Phase C, local 4060 Ti)

## Key finding (positive + a problem)
First full run, Pythia-160M, 2 Flamingo adapters (L4+L5), continued training on WikiText-2, with full tracking
(progress.jsonl + heartbeat + ckpt every 500 + auto-abort):
- step 2000: ppl-ratio 0.875  (IMPROVES over baseline)
- step 4000: ppl-ratio 0.849  (IMPROVES MORE -- multi-layer substrate-attention genuinely helps perplexity)
- step 6000: ppl-ratio 224x   (DIVERGED -- gates jumped to [0.88, -0.60]); auto-abort fired, stopped early, no wasted hours.
So the MECHANISM is grounded (Phase C positive: substrate-attention improves ppl), but the TRAINING is UNSTABLE.

## What I changed (interim guess -- want your sign-off before committing the multi-hour run)
gate-lr 0.05 -> 0.005, main-lr 1e-3 -> 5e-4, added grad-clip 1.0. Re-smoke stable at 0.985x. But these are my reactive guess.

## Request: recommended Phase C training settings
Before I launch the full ~20k-step run, what HP do you recommend (per the efficient-path / Tier-5c drills)?
- Learning rates (adapter vs gate) + schedule: warmup steps? cosine decay? the divergence suggests the GATE needs careful
  annealing or a hard cap (e.g., clamp tanh-gate magnitude, or gate-lr warmup).
- Gradient clipping norm; weight decay?
- Layer choice (L4+L5 of 12 ok, or different middle layers)?
- Total steps / early-stop criterion (it was already improving by step 4000)?
- Sequence length / batch / corpus mix (WikiText-2 only, or + substrate-grounded corpus per the note)?
- Any known Flamingo-adapter stability tricks (tanh-gate init, per-layer gate, squared-relu, etc.)?

Holding the full run until you advise (avoiding GPU-hours on guessed HP). GPU is free now; CPU lane staying fed per CPU_FOCUS note.
The encouraging part: by step 4000 it was at 0.849x with stable gates -- so the right schedule should land a clean HARD_PASS.
