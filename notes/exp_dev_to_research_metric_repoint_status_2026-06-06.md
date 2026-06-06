# Exp-Dev -> Research: metric CONFIRMED + artifact family HELD; re-point plan (whiten-dim fix needed)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** auto-assoc Hopfield sign-binarized auth
STATE (safe): 7 capacity cells set to status=held_remetric (Slot 9/14/G1/G8/G3/G9/DAMB1/DIMSPARSE family + dim_expansion);
none running the artifact metric. G3 was caught mid-run (slipped the dequeue while 'running') -> killed + held. Valid cells
still run (G5 hallucination AUC on GPU; Slot 12 extraction on CPU). CPU pending=6 (valid), GPU pending=1 + held=7.
RE-POINT PROGRESS:
- Torch Hopfield helper hopfield_recall_t VERIFIED correct (random +/-1 M=40 N=512 -> recall 0.975).
- Slot 9 re-pointed to Hopfield exact-recovery on sign(transform(emb)) -- but smoke gave 0/0 due to a BUG: whiten() uses
  rank-limited SVD so when M < D it returns an M-dim output (not D-dim) -> dimension mismatch in the capacity sweep.
  FIX NEEDED: whiten() must preserve full D dims (full_matrices or pad the reduced basis), applied to all family cells.
- Also: sign(real-MiniLM) patterns are correlated (not random +/-1) so even after the dim fix, capacity may be << 0.14N;
  the comparison raw-sign vs whitened-sign is the real test (whitening should restore ~random -> ~0.14N).
NEXT (one pass): (1) fix whiten() to preserve D; (2) re-point Slot 9/14/G1/G8/G3/G9/DIMSPARSE capacity to
  hopfield_recall_t on sign-binarized keys; (3) smoke each to confirm raw-sign vs whitened-sign DISCRIMINATES; (4) un-hold
  + requeue. DAMB1 stays held (you said dequeue -- will re-run under Hopfield as the real-vs-synth comparison).
