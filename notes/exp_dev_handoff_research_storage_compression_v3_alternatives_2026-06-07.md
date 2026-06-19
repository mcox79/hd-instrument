# exp_dev hand-off -- research: storage compression alternatives for v3 per-fact target

## Filed-by
Research sub-agent, 2026-06-07

## Trigger
Research note: notes/research_drill_sparse_w_alternatives_3x_2026-06-07.md
Topic: Storage compression axes beyond the validated 4-bit + N-reduction stack.
Target: reduce per-fact cost from ~4.5 KB to 200-800 bytes. Requires 6-22x additional.

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
Anchor 1 (Huffman entropy check) is CPU-only and is NOT pause-gated.
Anchors 2 and 3 require GPU; pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only.
Exp_dev designs the anchor grid, sweep parameters, threshold formulas, and queue assignment.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY -- CPU, ~30 min)
Pointer: Research note Section 8 Pre-Test 1 + Section 4a (Huffman entropy check)
Substrate-product reading: Does the 4-bit quantized pseudoinverse W matrix have a
  non-uniform codeword distribution? If the top 4 codewords cover >55% of weight
  values (indicating Gaussian bulk), Huffman or ANS entropy coding is essentially free
  and lossless, yielding 1.2-1.3x storage reduction at zero quality cost. This is the
  cheapest possible storage win in the entire v3 pipeline.
Tier hint: CPU; ~30 min; no GPU required; no training overhead; no quality risk.
Why-now: Cheapest decisive test. If HARD-PASS (H < 3.5 bits), implement immediately
  at 0.5-day engineering cost. If HARD-FAIL (H > 3.9 bits), W is near-uniform and
  entropy coding is not useful -- rules out this path for the stack.
Pre-registered bands from research note Section 8:
  HARD-PASS: Shannon entropy H < 3.0 bits on 4-bit W codeword histogram -> 1.33x+ gain
  MIDDLE-BAND: H 3.0-3.6 bits -> 1.1-1.33x gain, marginal but implementable
  HARD-FAIL: H > 3.9 bits -> near-flat distribution, Huffman gives <1.05x, skip

### Anchor 2 (GPU, ~1-2 hours)
Pointer: Research note Section 8 Pre-Test 2 + Section 1a (3-bit quantization)
Substrate-product reading: Does 3-bit scalar quantization of pseudoinverse W degrade
  recall@1 by <2% relative to the validated 4-bit baseline? If yes, this is an
  additional 1.33x storage reduction at negligible quality cost. The empirical risk
  is that pseudoinverse W may have heavier outlier weights than trained LLM weights at
  the same M, making 3-bit more fragile than published results suggest.
Tier hint: GPU; 1-2 hours wall; requires production Llama-1B encoder + N=4096 substrate
Why-now: Trivially adjacent to the existing 4-bit implementation. Cheapest GPU test.
Pre-registered bands from research note Section 8:
  HARD-PASS: recall@1 drop < 2% from 4-bit -> ship 3-bit as default storage format
  MIDDLE-BAND: recall@1 drop 2-5% -> acceptable for "compressed/lossy" mode, flag in docs
  HARD-FAIL: recall@1 drop > 5% -> do not ship 3-bit; try Path 1d (mixed precision)

### Anchor 3 (GPU, ~2-4 hours)
Pointer: Research note Section 8 Pre-Test 3 + Section 2a (product quantization of W)
Substrate-product reading: Does product quantization (PQ) at D=4, K=256 applied to
  pseudoinverse W rows produce a reconstructed W that maintains recall@1 >= 0.90?
  PQ is the highest-upside compression mechanism available: at the conservative
  operating point (D=4) it provides ~4-8x beyond 4-bit scalar; at the aggressive
  point (D=8) it could provide ~32x. The critical uncertainty is whether pseudoinverse
  W's quasi-Gaussian flat-spectrum structure is compatible with PQ codebook approximation
  (no published precedent).
Tier hint: GPU; 2-4 hours wall; requires building FAISS PQ index on production W
  matrix, then measuring recall@1 with PQ-reconstructed W.
Why-now: Highest-upside uncertain path. A HARD-PASS here changes the v3 projection
  from ~2.7 KB/fact (Huffman + 3-bit only) to potentially ~1.5 KB/fact (conservative
  PQ operating point) or lower.
Pre-registered bands from research note Section 8:
  HARD-PASS: recall@1 >= 0.92 at D=4 (proceed to test D=8 aggressive point)
  MIDDLE-BAND: recall@1 0.85-0.92 at D=4 (usable; do not push to D=8)
  HARD-FAIL: recall@1 < 0.85 at D=4 (PQ inappropriate for pseudoinverse W; close path)

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_sparse_w_alternatives_3x_2026-06-07.md
- Validated stack state: PRODUCTION ARCHITECTURE LOCKED memory note (cycle 155)
- Closed paths (do not re-test): sparse-W (cycle 155 HF), low-rank SVD (Marchenko-Pastur)
- Related earlier drill: notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md

---

## Contract

- Anchor 1 runs on CPU queue (no GPU, no pause gate)
- Anchors 2-3 run on remote_gpu_queue; check pause flag before dispatch
- No inline experiment design in this prompt; exp_dev designs anchor parameters
- Results feed verdict_handler; strategy/cap_map updates via orchestrator, not exp_dev
- If Anchor 3 HARD-PASS at D=4, exp_dev may queue D=8 sweep as follow-on (separate anchor)

## Autonomy declaration
Exp_dev owns: anchor parameter selection, queue routing, pre-reg threshold formula,
  smoke gate, post-ship remote verify.
Exp_dev does NOT own: cap_map decisions, v3 product claim adjustments, cross-anchor strategy.
