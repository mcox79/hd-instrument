# Brain-foundational design analysis: resolving retrieval interference among similar memories

**Slug:** `resolve_retrieval_interference_among_similar_memories` -- solver session, 2026-08-26.
This doc is the deep brain-fidelity dive that shaped every arm of
`experiments/exp_context_interference_resolution_v1.py`. It exists because the owner asked, twice,
for a deeper brain-foundational drill folded INTO the experiment -- not a citation added after.

## 1. The opening move: how does the brain resolve WHICH of several similar memories?

The problem is the fan effect / similarity-based interference: a cue that matches several similar
stored memories retrieves the wrong one. The prior `content_addressable_retrieval` SOLVED established
(findings 7-9, re-verified) that a CONTENT-only additive cue CANNOT resolve this -- and correctly so,
because **the discriminating information is not in the content at all.** Two memories of "the bank" are
identical in content; what separates them is the CONTEXT they were formed in ("by the river" vs "with
money").

So the brain's answer is not a better content match. It is a DIFFERENT variable:

- **CONTEXT REINSTATEMENT (PINNED).** Temporal Context Model (Howard & Kahana 2002): a slowly-drifting
  context vector is bound to each item at encoding; reinstating it at retrieval biases activation to
  the context-matched trace. CMR (Polyn/Norman/Kahana 2009) generalises context to source/semantic
  features. Lewis & Vasishth (2005) already SUM a context cue into the retrieval activation. Substrate:
  hippocampal item-to-context binding (EC/CA1).
- **PATTERN SEPARATION AT ENCODING (PINNED direction).** The dentate gyrus orthogonalises similar
  traces AS THEY ARE STORED (Yassa & Stark 2011) by binding each episode to a distinct index/context
  (Teyler-Rudy indexing) -- NOT by mangling content. DG-at-RETRIEVAL is already a rigorous NEGATIVE
  (content_addressable finding 6), so ENCODING is the only faithful place for it.
- **THE RESIDUAL FAN EFFECT IS REAL AND MUST BE EXHIBITED (PINNED).** Anderson; ACT-R: activation
  spreads thinner as more items share a cue, so retrieval slows/errs. A faithful model shows a graded
  cost with competitor count; it does not become magically immune. A ZERO-fan model has leaked.

## 2. The deeper dive (owner: "is everything brain-faithful? the machinery in proximity too?")

The first draft was a flat additive-argmax over content+context. The deeper drill found two mechanisms
that are MORE foundational than the ACT-R "fan penalty" the prior work correctly rejected, and folded
them in:

- **The read is a NOISY COMPETITIVE one, and the fan effect EMERGES from it (mechanism 2).** ACT-R
  retrieval = activation + LOGISTIC NOISE, retrieve the max. More competitors of comparable activation
  -> noise flips the winner more often -> graded cost, intrinsically. This is the same "activation is
  relative to the pool" math as divisive normalisation (Carandini & Heeger, the canonical cortical
  computation). So the residual fan effect is a CONSEQUENCE of the pinned decision rule, not a
  hand-added penalty (the penalty was regime-specific and HURT graded codes -- prior finding 9). Copied
  the COMPUTATION (activation + logistic noise); swept the PARAMETER (noise scale s).
- **The cue is weighted by DIAGNOSTICITY via cognitive control (mechanism 3).** Left VLPFC controlled
  retrieval / post-retrieval selection (Badre & Wagner 2007; Van Dyke & McElree 2006): under
  interference the brain up-weights the cue that DISCRIMINATES the current competitors and down-weights
  the non-diagnostic one -- so when content is ambiguous, weight shifts onto context automatically.

## 3. What the drill CAUGHT (fidelity problems fixed, not papered over)

1. **The diagnosticity-control arm was PEEKING.** Computing a cue's weight from how well it separates
   the current candidate set, when the cue is target-derived, silently up-weights the feature the target
   is an outlier on -- a soft oracle. Tell: `CTX_CONTROL` (noisy context) BEAT the exact-context ORACLE
   (0.972 > 0.856) in the boundary population. FIXED: `CTX_CONTROL` is demoted to a labelled OPTIMISTIC
   CEILING; the headline / bar arm is fixed-weight `CTX_ADD`. The faithful non-peeking control sets
   weights from goal/prior, which reduces to choosing `w_ctx` -- exactly what `CTX_ADD` does.
2. **Context was independent of content -- too easy.** Real context (CMR retrieved-context; the
   situation model) CARRIES the content of recent experience, so similar memories have partly-similar
   contexts. Added the CMR content-mix axis: the win SURVIVES (CI-separated at mix 0/0.3/0.6) but
   DEGRADES gracefully (CTX_ADD 0.95 -> 0.77) as context becomes less separable -- brain-correct.
3. **Encoding separation is context-INDEXING, not sparsification.** The prior DG-sparsify NEGATIVE plus
   this cell's `ENC_SEP` (bind context into the stored trace) say the faithful separator binds the
   episode to its context/index. `ENC_SEP` alone FAILS (the separated store is unaddressable without the
   context key); `ENC_SEP_CTX` ties `CTX_ADD` -- so the lever is context-at-RETRIEVAL.

## 4. Component-by-component fidelity ledger

| Component | Fidelity | Note |
|---|---|---|
| additive activation `Σ w_f sim` | PINNED | Lewis-Vasishth / ACT-R; the landed organ; CONTENT_ONLY == it bit-for-bit |
| context reinstatement (TCM drift) | PINNED (structure) | drift is faithful; the CODE is synthetic -- see gap below |
| decision = activation + logistic noise -> argmax | PINNED | ACT-R; the fan effect emerges from it |
| encoding separation = bind context^sep | PINNED direction | Teyler-Rudy indexing, NOT DG sparsify (which failed) |
| FHRR similarity kernel | inherited | the register's own metric; VSA binding is UNPINNED per our audit |
| w_ctx, rho, eta, sep, s | INVENTION-UNDER-TEST | all swept, none adopted |
| context ENTERS additively (vs gate) | measured: ADDITIVE wins | `CTX_ADD` > `CTX_GATE` at every K -- answers the brief's OUR-INVENTION question |

## 5. The biggest remaining gap (flagged, not built -- it is the wire-and-measure step)

The context here is a SYNTHETIC TCM drift vector, not the substrate's REAL context. The top fidelity
upgrade -- and the honest next instrument -- is to replace the drift code with the substrate's own
situation-model / reading-loop context (`situation_model_accumulate`, `reading_grounding_loop`) and
test on the REAL coref competing-referent case. That also directly answers the bar's decisive negative
branch: IS the substrate's real context separable across similar memories? The boundary population
(adjacent-in-time, non-separable context) already shows the failure mode when it is not.

Optional deeper reads flagged but not built (low priority): a competitive/normalised (divisive-norm /
attractor) read instead of noisy-argmax (prior work: attractor recurrence buys nothing over argmax in
the separated regime).

## 6. Second-pass drill (owner: "is the machinery in PROXIMITY faithful too?") -- TESTED, see SOLVED findings 8-10

`--deep` mode ran three probes against the real proximity machinery:
- **(A) the REAL DG organ `dg_separate` at ENCODING is NEUTRAL** (DG_CONTENT ~ CONTENT_ONLY) -- canonical
  content-sparsification does not resolve context-separable interference; confirms context-INDEXING, not
  DG-on-content, is the faithful separator (I had substituted a context-bind for canonical DG -- correct).
- **(B) context reinstatement survives from a partial FRAGMENT** (15-60% of components; the rest
  pattern-complete) -- the mechanism does not need a handed-over context copy, closing the "where does the
  reinstated context come from" gap that section 5 flagged.
- **(C) the fan effect appears in LATENCY too** (winner-runnerup margin shrinks 0.99->0.72 with fan) --
  the bar named "recovery/latency"; now both axes are covered.
Proximity read: the real `context_vector` is a content-derived bag-of-words, `sign()`-quantized -> the
CONTENT-CORRELATED regime (mix>0) is the faithful operating point, and GRADED (non-sign) context is the
recommended wiring. The one gap that remains genuinely un-built is the REAL situation-model/coref
instrument (section 5) -- the wire-and-measure step.
