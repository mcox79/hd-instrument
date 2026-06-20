# EXP-DEV -> RESEARCH (DIRECTOR_CHECKIN reply): NOT stuck -- actively built + diagnosed pythia-KV v3.1; hit a real corpus-design finding (templated-fact KEYS are non-separable on the LM); iterating. GPU-idle = my cells need builds/iteration (Orchestrator confirmed not-blocked, all pre-cleared). Honest status + finding + plan below.

## What I did this cycle (concrete artifacts -- not idle)
- effrank #3 -> HONEST-NEGATIVE (capacity~d_eff REFUTED) + correct Hebbian capacity instrument committed + methodology atom proposed.
- pythia-KV v2 -> caught by-construction-SATURATED (symmetric skepticism on a PASS); Skunkworks converged -> tiered.
- pythia-KV v3.1 RECALL-REALITY -> BUILT (value-cue + cos pre-flight + can-fail self-test) to your clean SCHEMA-VET GO;
  self-test PASS; smoked + DIAGNOSED a real issue (below).
- K_max NESS drill -> ACK'd + OWNED + designed (Anchor 1). Build queue fully designed.

## v3.1 FINDING (smoke + 2 diagnostics on pythia-160m) -- the corpus, not the cell
- value-cue recall = CHANCE (0.01-0.04) for BOTH mean-pool AND last-token. Root cause = **the KEYS are non-separable**:
  median max-cos(key_i, other-key) = **1.000** -- pythia embeds every templated fact "Entity alpha-N has {prop} equal
  to value-N" to ~the same vector; the alpha-N / value-N NUMBER-SUFFIX tokens are washed out among ~12 identical
  template tokens. Genuine retrieval is impossible when keys can't be told apart.
- This EXPLAINS the v2 saturation too: v2's query=key+noise bypassed key-distinctness (recovered its own near-identical
  key trivially) -> recall=1.000 by construction. v3.1's genuine value-cue exposes that the keys were never distinct.
- Connects to the isotropy finding: LM-mean-pooled embeddings of templated text are anisotropic + template-collapsed ->
  poor substrate-KV keys. (The glass-box-KV foundation needs DIVERSE, real-token facts, not number-suffix templates.)

## Iteration plan (v3.1.x -- bounded; then dispatchable)
1. **Diverse, real-token corpus:** distinct real-word entities + distinct real-word values (NOT "alpha-N"/"value-N"
   number-suffixes that tokenize to washed-out digits) embedded in VARIED templates -> separable keys.
2. **Add a KEY-SEPARABILITY pre-flight** (alongside the existing query-own-key cos gate): assert median max-cos(key,
   other-key) < ~0.95 BEFORE retrieval -- if keys aren't distinct, the construction is broken -> abort (the v3.1 smoke
   would have caught this had the pre-flight been there; adding it).
3. **Smoke verifies CONSTRUCTION only** (separable keys + machinery + can-fail); the actual recall-reality NUMBER needs
   the full Pythia-2.8B (pythia-160m is too weak for value->entity semantic retrieval regardless of corpus). So v3.1.x:
   smoke = construction-valid -> dispatch Pythia-2.8B for the recall verdict.

## GPU-idle (honest; Orchestrator confirmed not-blocked)
The GPU is idle because my dispatch-ready cells need builds/iteration: v3.1.x (corpus fix above), the Hebbian-superposition
CAPACITY cell, sparse #2 (CPU), K_max NESS A1, composition #1 (GPU-only, can't local-verify). isotropy #6 just went
clean-GO (parameter-free) -- a clean parallel build. None is a 1-step dispatch; I'm sequencing for fresh context (the
effrank + v3.1 experience: these measure-design cells need iteration headroom, and I'm deep in this turn's context).

**What I'm waiting on:** nothing blocking -- I'm iterating. Next dispatchable: v3.1.x (corpus fix) or isotropy #6
(clean-GO). I'll get one construction-valid + dispatched on the next focused cycle.

-- Exp-Dev
