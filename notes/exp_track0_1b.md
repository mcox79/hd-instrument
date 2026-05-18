# Pre-registration: Track 0.1b — pointer-chain HDC character LM

**Date pre-registered:** 2026-05-17 (before running)
**Experiment file:** `experiments/exp_pointerchain_charlm.py` (not yet written)
**Decision gate this feeds:** Track 0.1 follow-up; informs whether the architecture's effective context length can grow without bundle-saturation.

## Question

Track 0.1 showed that a longer bundled context window (K=8) did *not* improve over a shorter one (K=4). The bundling capacity wall (β≈1.0 across substrates, measured repeatedly in prior experiments) is biting before extra context can help.

Hypothesis: we can keep the bundled "working memory" short *and* give the model unbounded effective context length, by maintaining a **separate, addressable pool** of recent past contexts. Each past context is stored as its own hypervector. At prediction time, we cleanup against this pool to retrieve the most-similar past context, then condition the next-byte prediction on *that* retrieved context's continuation in addition to the current working-memory bundle.

This is structurally distinct from Schlag-Irie-Schmidhuber 2021 (fast weight programmers with delta rule). Their architecture *accumulates* all past key→value associations into a single weight matrix, hitting the same capacity wall we hit. Our pointer-chain *segregates* past contexts as distinct stored items and retrieves them on demand — closer to episodic memory than to associative weight memory.

## Architecture under test

Same byte-level setup as Track 0.1, plus:

- **Working memory:** unchanged. K=4 (small, capacity-respecting) FHRR bundle of recent bytes with positional binding.
- **Episodic pool:** a ring buffer of the last M context-bundle hypervectors paired with the byte that followed each one. Size M ∈ {64, 256, 1024}.
- **Retrieval at prediction:** for current context c, compute similarity against every stored hypervector h_j in the episodic pool; softmax-weight the corresponding stored next-bytes by similarity to form a retrieval distribution P_retr.
- **Final prediction:** mix the connection-matrix prediction P_W and the retrieval prediction P_retr with a learned mixing weight α. For this experiment, α is *not learned by SGD* — it's a flat hyperparameter swept ∈ {0.0, 0.3, 0.7, 1.0}. (Learning α via three-factor is a phase-2 extension.)
- **Pool update:** after each prediction step, append the current (context, true-byte) pair to the pool and drop the oldest if pool is full. No Hebbian update to the pool — it's pure storage.
- **Connection-matrix update:** unchanged from Track 0.1 — three-factor delta rule.

## Variations to test

- Pool size M ∈ {0, 64, 256, 1024} (M=0 reduces to Track 0.1 exactly)
- Mixing α ∈ {0.0, 0.3, 0.7, 1.0}
- Best K, arousal, beta from Track 0.1 (frozen at winning values to limit sweep size)

12 configs (4 pool sizes × 3 mixing values, minus M=0/α=0 trivial dupes) × 1 seed. Each run ≈ 4–5 minutes.

## Pre-registered decision criteria

| Outcome (best test bpc) | Verdict |
|---|---|
| Pointer-chain best beats single-bundle best by > 0.5 bits/char | **Effective context via addressing works.** Promote pointer-chain to the default architecture for Bet B scaling; this is the resolution of the K-saturation finding. |
| Pointer-chain best within 0.5 bits/char of single-bundle best | **Marginal.** Architecture works at small scale but the benefit isn't dramatic. Re-test at larger corpus before deciding. |
| Pointer-chain best is *worse* than single-bundle best | **Surprising.** Either retrieval is noisy beyond what cleanup tolerates at this scale, or the mixing rule needs to be learned rather than fixed. Investigate before falling back. |

## Why this matters for the strategic picture

If pointer-chain works, our architecture has a clean answer to the "how do we handle long context" question that doesn't require us to scale N exponentially. The bundle stays at the capacity-friendly small size, and the pool grows linearly in storage. Cleanup against a 1M-entry pool is the operation we already know has a 3-orders-of-magnitude hardware advantage on in-memory analog silicon (see `hardware_characterization.md`). This is the path that makes "long-context LLM at edge power" a real engineering target.

If pointer-chain doesn't help, the bundle is genuinely the limit, and we have to either accept that and scale via multi-relation matrices instead (still a real path) or rethink the substrate.

## What this is NOT testing

- Whether the retrieval mechanism itself can be improved (top-1 vs softmax-mixture; learned vs fixed projection). That's phase 2 if this looks alive.
- Whether traces of past *predictions* (not just past contexts) should be stored. Same.
- Whether pointer-chain helps at larger corpus sizes. We only know about this 38KB corpus.
- Whether it works with eligibility traces (Track 0.1c).
