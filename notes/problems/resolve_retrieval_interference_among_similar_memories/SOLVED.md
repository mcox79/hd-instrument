---
problem: resolve_retrieval_interference_among_similar_memories
status: SOLVED
bar: "On a retrieval task with genuinely SIMILAR competitors (same-cluster / near-duplicate memories), floor recomputed on its population: context-based interference resolution (add the encoding CONTEXT to the additive activation, and/or separate at ENCODING) must recover the correct competitor CI-separated over the CONTEXT-FREE additive baseline's UPPER bound, with the info-free twin (SHUFFLED / RANDOM context) LOSING CI-separated, CI half-width + null p95 reported. AND it must still EXHIBIT the residual fan effect (recovery/latency degrades gracefully as competitor count rises -- report the curve; a model that shows ZERO fan cost has leaked the answer, not resolved interference). Sweep context weight / separation level / competitor similarity."
result: "Adding the encoding CONTEXT to the additive Lewis-Vasishth activation (CTX_ADD = content + w_ctx*context) resolves interference among genuinely similar memories CI-separated over the CONTEXT-FREE additive baseline at EVERY competitor count. Headline K=8 fan (cluster of 9 near-identical memories): CTX_ADD hit@1 = 0.9278 [0.8804, 0.9573] vs the context-free additive baseline (== the landed hdlab.content_addressable_retrieval.AdditiveCueRetrieval) 0.4000 [0.3312, 0.4729], paired delta +0.5278 CI[+0.4500, +0.6056]. CI-separated at K=1 (+0.2500), K=2 (+0.3000), K=4 (+0.3333), K=8 (+0.5278). Scorer = FHRR filler recovery hit@1; n = 180 trials per K (60 clusters x 3 TEST seeds); population = same-content-cluster interference instrument (members share entity-prototype, event and role; differ only in TCM encoding context + payload) on REAL hdlab FHRR ops."
floor: "The bar's named floor is the CONTEXT-FREE additive baseline (bit-identical to the live AdditiveCueRetrieval argmax); its UPPER-95 bound by K is 0.7825/0.7262/0.6529/0.4729 (K=1/2/4/8) and CTX_ADD's LOWER bound (0.9366/0.9219/0.8671/0.8804) clears each. Info-free twins: SHUFFLED-context upper-95 = 0.4050 and RANDOM-context upper-95 = 0.4165 (K=8), both cleared (CTX_ADD-SHUFFLE +0.5944 CI[+0.5222,+0.6667]; CTX_ADD-RANDOM +0.5833 CI[+0.5000,+0.6667]). Chance = 1/(K+1) (0.111 at K=8). Null p95 = the twin upper-95 (0.4050). CI half-widths reported per cell in metrics.json."
controls: "(1) INFO-FREE TWIN SHUFFLE (stored context codes permuted across items) LOSES CI-separated at every K -> the win is a real context signal, not a free extra channel. (2) INFO-FREE TWIN RANDOM (cue context is fresh noise, no reinstatement) LOSES CI-separated at every K. (3) LEAK GUARD CTX_ALONE (retrieve by context similarity ONLY) sits far below the exact-context oracle (0.306 vs 0.994 at K=8) and at/below content-only -> context BIASES, does not IDENTIFY; the win is genuine CUE COMBINATION (neither cue alone resolves it). (4) POSITIVE CONTROL / DV VALIDITY CTX_ORACLE (exact eta=0 context) near ceiling (0.994) -> the DV can detect resolution. (5) BASELINE == LIVE ORGAN: CONTENT_ONLY asserted bit-identical to hdlab AdditiveCueRetrieval argmax (0 mismatches). (6) RESIDUAL FAN EFFECT EXHIBITED: CTX_ADD degrades 0.972->0.928 as K 1->8 (content-only steeper 0.722->0.400) -> resolution reduces but does NOT eliminate interference. (7) BOUNDARY (bar's decisive negative branch): competitors encoded ADJACENT in time (NON-separable context) collapses CTX_ADD 0.928->0.494 -> context resolves ONLY when it is separable. (8) CMR content-correlated context: the win SURVIVES CI-separated at content-mix 0/0.3/0.6 but degrades gracefully (0.95->0.77) -> not dependent on context being independent of content. (9) ADDITIVE vs GATE: CTX_ADD (additive) > CTX_GATE (multiplicative) at every K -> context enters ADDITIVELY. (10) ENCODING-SEP: ENC_SEP alone fails (~content), ENC_SEP_CTX ties CTX_ADD -> the lever is context-at-RETRIEVAL, encoding-separation is only a substrate needing the same context key."
files_changed: "experiments/exp_context_interference_resolution_v1.py, verification/test_context_interference_resolution.py, notes/problems/resolve_retrieval_interference_among_similar_memories/DESIGN_brain_analysis.md, notes/problems/resolve_retrieval_interference_among_similar_memories/SOLVED.md, data/exp_context_interference_resolution_v1/metrics.json"
reverify: ".venv/Scripts/python.exe verification/test_context_interference_resolution.py"
---

# CONTEXT reinstatement is the missing organ for interference resolution -- and it is the SAME additive rule, given a context feature

## Headline in plain language

Our memory can now look things up by a rough description, but when two stored memories are genuinely
SIMILAR it confidently returns the wrong one -- the fan effect. People have this weakness too, so a
faithful model must still SHOW some of it. But the brain resolves WHICH similar memory far better than we
do, using a variable our cue throws away: the CONTEXT a memory was formed in ("the bank by the river,"
not "the bank"). I built the brain's fix -- add the encoding context to the retrieval -- on top of the
REAL memory rule, and stressed it with clusters of near-identical memories. It works: with up to 8
look-alike competitors, adding context lifts recovery from ~40% right to ~93% right, a shuffled/random
context does NOT help (so it is a real signal, not a free channel), and -- crucially -- context ALONE
cannot do it either (it only biases; the win comes from COMBINING the weak content cue with the weak
context cue). It still shows a graceful fan cost (recovery slips as competitors pile up), and when the
competing memories genuinely SHARE a context (encoded at the same time), the fix correctly collapses --
context resolves interference only when there IS separable context to reinstate.

## What I built

`experiments/exp_context_interference_resolution_v1.py` -- a same-content-cluster interference instrument
on the REAL hdlab additive retrieval organ. Each memory is per-feature FHRR codes {entity, event, role}
+ a CONTEXT code + a payload filler. A CLUSTER = several memories that share the entity-prototype, event
AND role (genuinely similar -- content underdetermines the choice), differing only in their encoding
CONTEXT and payload. Context is a TCM slowly-drifting vector (Howard & Kahana): members encoded at
different times get distinct contexts. The retrieval cue is a PARTIAL content cue (a noisy version of the
target's entity, event+role shared -> ambiguous among the cluster) plus a NOISY reinstatement of the
target's encoding context (it BIASES, does not identify). The CONTENT_ONLY arm is bit-identical to the
live `AdditiveCueRetrieval` argmax. Every arm's decision is an ACT-R read (activation + logistic noise ->
argmax), so the residual fan effect emerges from the mechanism, not a penalty. Full brain-fidelity dive
in `DESIGN_brain_analysis.md`.

## What I measured (all CI'd; reverify = the scaffold-free witness, 6 assertions, PASS)

1. **THE BAR MET: context reinstatement resolves interference CI-separated at every fan level.** CTX_ADD
   beats the context-free additive baseline by +0.25 (K=1), +0.30 (K=2), +0.33 (K=4), +0.53 (K=8), each
   CI-separated over the floor's upper bound. Headline K=8: 0.928 [0.880, 0.957] vs 0.400 [0.331, 0.473].

2. **The info-free twins LOSE CI-separated.** A SHUFFLED-context twin (stored contexts permuted) and a
   RANDOM-context twin (cue context is noise) both track content-only (0.33 / 0.34 at K=8), so the
   context term carries a real signal, not just an extra channel. CTX_ADD - twin > +0.58 at K=8.

3. **Leak-safe -- the win is genuine CUE COMBINATION.** Context ALONE (retrieve by context similarity
   only) is 0.31 at K=8, far below the exact-context oracle (0.994) and at/below content-only (0.40).
   Neither the weak content cue nor the weak context cue resolves it alone; adding them accumulates
   evidence and does. (This is why the leak-conservative operating point -- high reinstatement noise --
   is the headline: it makes context alone clearly non-identifying.)

4. **The residual fan effect is EXHIBITED, not eliminated.** Recovery degrades gracefully as competitors
   pile up: content-only 0.72 -> 0.40 (K=1 -> 8, steep), CTX_ADD 0.97 -> 0.93 (gentle). Context REDUCES
   the fan cost but does not abolish it -- brain-correct (a zero-fan model would have leaked).

5. **BOUNDARY (the bar's decisive negative branch, characterised): context resolves ONLY when it is
   separable.** When competitors are encoded ADJACENT in time so their contexts overlap, CTX_ADD collapses
   0.928 -> 0.494 (K=8) and context-alone falls to 0.13. The mechanism is not magic: it needs separable
   context to reinstate. This says WHY interference can be irreducible (the context codes are themselves
   too similar) -- exactly the failure the brief asked to name.

6. **CMR robustness: the win survives content-correlated context.** When the encoding context CARRIES the
   item's own content (a harder, more faithful CMR retrieved-context, so similar memories have
   partly-similar contexts), CTX_ADD still beats content-only CI-separated at content-mix 0/0.3/0.6, but
   degrades gracefully (0.95 -> 0.77). The mechanism does not depend on context being magically
   independent of content.

7. **Two OUR-INVENTION questions answered.** (a) HOW context enters: ADDITIVE (CTX_ADD) beats the
   MULTIPLICATIVE gate (CTX_GATE) at every K -- consistent with the landed additive organ; context is one
   more Lewis-Vasishth cue feature. (b) ENCODING vs RETRIEVAL separation: ENC_SEP (bind context into the
   stored trace, no retrieval context) fails ~content; ENC_SEP_CTX (separate AND reinstate) ties CTX_ADD
   -> the lever is context-at-RETRIEVAL; encoding-separation is only a substrate that needs the same
   context key. This corrects the DG story: the faithful separator is context-INDEXING (Teyler-Rudy), not
   sparsification (which the prior work found HURTS).

## DEEPER BRAIN-FIDELITY DRILL (second pass, owner-directed: "is the machinery in PROXIMITY faithful too?")

I read the proximity organs (`dg_pattern_separation.py`, `grounding_acquisition_loop.context_vector`)
and ran three probes the headline missed (`--deep` mode; console evidence, not landed to metrics.json):

8. **The REAL DG organ (`hdlab.dg_pattern_separation.dg_separate`) applied at ENCODING to the content code
   is NEUTRAL here -- it does not resolve interference.** Canonical DG (expand to 8*d + ~5% kWTA sparsify,
   the Leutgeb/Guzman/McHugh mechanism) on the entity code: DG_CONTENT 0.367 ~ CONTENT_ONLY 0.372, and
   DG+CTX 0.944 ~ CTX_ADD 0.944 (K=8). So decorrelating CONTENT buys nothing when the memories differ in
   CONTEXT, not content -- it extends the prior DG-at-retrieval negative to DG-at-encoding-on-content, and
   confirms the faithful encoding separator is context-INDEXING (Teyler-Rudy), not content-sparsification.
   I had SUBSTITUTED a convenient context-bind for the canonical DG in `ENC_SEP`; testing the real organ
   shows that was the right call, and canonical DG-on-content is simply the wrong tool for this regime.
9. **Context reinstatement survives from a partial FRAGMENT -- it does NOT need a handed-over copy.** When
   the cue reinstates only a FRACTION of the context components (rest randomised; the rest must
   pattern-complete via the additive match -- the Nakazawa CA3 partial-cue regime applied to CONTEXT), the
   win holds: at 60% of the context CTX_ADD 0.978 (+0.65 over content), at 30% 0.917 (+0.59), at 15% 0.706
   (+0.38). This addresses the deepest fidelity gap (where does the reinstated context come from) -- a
   fragment suffices; the mechanism is robust to partial reinstatement, exactly as hippocampal completion
   predicts.
10. **The fan effect shows up in LATENCY, not just accuracy (the bar named "recovery/latency").** The
    winner-minus-runnerup activation MARGIN (ACT-R retrieval-time correlate: time decreases in margin)
    SHRINKS with competitor count for the context arm: 0.987 (K=1) -> 0.902 -> 0.823 -> 0.722 (K=8). So
    even where accuracy stays high, retrieval gets slower/less confident as competitors pile up -- the
    graded fan cost in the latency dimension, brain-correct.

**Proximity-machinery fidelity notes (from reading the organs):** the substrate's REAL context vector
(`context_vector`) is a bag-of-content-words bundle (Kanerva/BEAGLE) -- it is CONTENT-DERIVED and
`sign()`-quantized. So (a) my CMR content-correlated regime (mix>0, finding 6) is the FAITHFUL operating
point for the real wiring (the win is weaker there but survives), and (b) `sign()` makes the real context
lossy -- a GRADED (non-sign) context would be more separable and is the recommended wiring (the organ
already exposes `graded=True`).

## KEY REALIZATIONS (the enabling moves)

- **The discriminating information is not content -- it is a DIFFERENT variable.** The prior additive
  rule failed on similar competitors CORRECTLY (content underdetermines the choice). The move was to stop
  trying to fix the content match and add the variable the memories actually differ on: context. Framing
  the problem as "which variable separates these memories" rather than "how to match content better" is
  the whole solution.
- **The win had to be CUE COMBINATION, not a second key.** The single biggest design risk was context
  leaking the target identity (an oracle). Locating an operating point (via the regime sweep) where
  context ALONE is far below ceiling AND content alone is far below ceiling, yet their SUM resolves,
  turned a possible leak into the strongest evidence -- genuine Bayesian cue integration, which is what
  the brain does.
- **A twin that TIES content is as informative as one that loses.** The shuffled/random-context twins
  TRACK content-only exactly -- proof the added dimension carries signal only when it is the REAL context.
- **The fan effect should EMERGE from the read, not be added.** Switching the decision to an ACT-R
  noisy-argmax made the residual fan cost a consequence of the pinned mechanism (more competitors -> noise
  flips the winner), so I never had to add the regime-specific fan penalty the prior work rejected.
- **Auditing my OWN machinery caught a soft oracle.** The diagnosticity-control arm beat the exact-context
  oracle -- impossible unless it was peeking. Computing cue weights from the candidate set, when the cue
  is target-derived, up-weights the feature the target is an outlier on. Demoting it to a labelled ceiling
  (headline = fixed-weight CTX_ADD) is what keeps the result honest. The owner's "is the machinery in
  proximity brain-faithful?" prompt forced this check.

## What I did NOT establish (and would withdraw first if wrong)

- **This is a SYNTHETIC construction proof on FHRR codes + a synthetic TCM context, not a comprehension
  win on real text.** Same honest limit as the content_addressable SOLVED it builds on. The FIRST thing I
  would withdraw is any claim that wiring this moves a live reading/coref number -- it must be measured on
  the live task with the substrate's REAL context first.
- **The context is engineered to BE separable at the headline operating point.** Whether the substrate's
  actual situation-model / reading-loop context is separable across genuinely similar memories is OPEN --
  the boundary population shows the mechanism collapses when it is not, so this is the load-bearing open
  question for the real instrument.
- **CTX_CONTROL (diagnosticity-weighted) is an OPTIMISTIC CEILING, not a result** -- it peeks at the
  candidate set. Do NOT quote it as a win over CTX_ADD; the faithful non-peeking version reduces to
  choosing w_ctx, which CTX_ADD already does.
- **The competitive read is noisy-argmax, not normalisation/inhibition.** A divisive-normalisation or
  attractor read is untested here (flagged; prior work found attractor recurrence buys nothing over argmax
  in the separated regime).
- **Reinstatement is injected, not completed.** I feed a noisy target context directly; a fuller model
  would pattern-COMPLETE the context from a partial cue before retrieval. Untested.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- E2/E3, section 2b)

1. **The open problem the content_addressable SOLVED handed over (similarity-interference / fan effect) is
   RESOLVED in principle: the missing organ is CONTEXT REINSTATEMENT at retrieval.** Adding the encoding
   context to the additive Lewis-Vasishth activation resolves interference among similar memories
   CI-separated over the context-free baseline (0.93 vs 0.40 at 8 competitors), twins losing, leak-safe,
   while still exhibiting the residual fan effect. E2/E3 should record: the additive cue-retrieval rule is
   complete only WITH a context cue; without it, similar-competitor interference is irreducible.
2. **Context enters ADDITIVELY (one more Lewis-Vasishth cue feature), not as a multiplicative gate** --
   answers the brief's OUR-INVENTION question and keeps it consistent with the landed additive organ.
3. **DG separation should be re-framed as context-INDEXING at ENCODING (Teyler-Rudy), NOT content
   sparsification -- now tested with the REAL organ.** The prior DG-sparsify negative + this cell's
   ENC_SEP results + the deep drill (finding 8: the real `dg_separate` at encoding is NEUTRAL,
   DG_CONTENT 0.367 ~ CONTENT_ONLY 0.372): canonical DG expand+sparsify on the content code does not
   resolve context-separable interference. Binding the episode to its context/index is what pulls similar
   traces apart; the lever is still context-at-RETRIEVAL (ENC_SEP alone fails).
5. **The substrate's REAL context vector is content-derived (bag-of-words, Kanerva/BEAGLE) and
   `sign()`-quantized.** Two consequences for E2/E3: (a) the honest operating regime for wiring is the
   CONTENT-CORRELATED one (finding 6), where the win is weaker but survives; (b) `sign()` makes context
   lossy -- use the organ's GRADED context (`graded=True`) for reinstatement (more separable, more
   faithful). This also ties the interference-resolution organ to the CLS FAST/hippocampal tier (the fan
   effect is a fast-system property; consolidation extracting the shared schema is the slow-tier
   complement -- flagged, not built).
4. **NEW pinned mechanism for the audit's decision rule: the ACT-R noisy competitive read (activation +
   logistic noise -> argmax) is what makes the residual fan effect intrinsic** -- do NOT use the ACT-R fan
   PENALTY (regime-specific, prior finding 9). The fan effect is a consequence of the read, not a knob.

## What would change in hdlab (proposed; the strategy session lands it, Q111 -- I did NOT write hdlab/)

- **STORE THE ENCODING CONTEXT AS A PER-ITEM FEATURE in the register, and include it in the additive
  `decode_cue`.** Because the landed `AdditiveCueRetrieval` is feature-agnostic, context reinstatement
  needs NO new math -- add a `context` slot to each stored item ({entity, event, role, CONTEXT}) and pass
  a (partial, reinstated) context in the cue. The single well-supported change. Default-OFF flag. The
  context source is the situation-model / reading-loop context vector -- and use its GRADED form
  (`context_vector(graded=True)`), NOT the `sign()`-quantized default (finding 8-note: sign makes context
  lossy/less separable). A partial-fragment reinstatement suffices (finding 9), so exact context recovery
  is not required.
- **Weight the context cue (w_ctx) as a fixed goal-driven parameter; do NOT ship the per-trial
  diagnosticity-weighting** -- it peeks (an optimistic ceiling here); the faithful contribution is
  choosing w_ctx, which the fixed additive rule already captures.
- **Do NOT ship the multiplicative gate** (additive wins) and **do NOT ship the ACT-R fan penalty**
  (regime-specific; the fan effect already emerges from the noisy read).
- **Encoding-separation is OPTIONAL and redundant with retrieval-side context here** -- if used, it must
  be context-INDEXING at encoding (bind the episode to its context), not DG sparsification, and it still
  needs the context reinstated at retrieval.
- **MEASURE ON THE LIVE coref / situation-model task before any capability claim** -- this is a synthetic
  construction proof; the real question is whether the substrate's actual context is separable across
  similar memories (the boundary population shows the mechanism collapses when it is not).

---

## TLDR
Our memory gets fooled when two stored memories are very alike -- it grabs the wrong one. That is the
known "fan effect," and a faithful model should still show a bit of it. The brain does better by using
the CONTEXT a memory was formed in ("the bank by the river"). I built exactly that -- add the encoding
context to our existing memory-lookup rule -- and tested it with clusters of near-identical memories. It
works cleanly: with up to 8 look-alikes, adding context lifts getting the right one from ~40% to ~93%; a
scrambled context does NOT help (so it is a real signal); context by itself is NOT enough either (the win
comes from combining the weak content clue with the weak context clue, so it is not cheating); it still
slips gracefully as look-alikes pile up (the honest fan effect); and it correctly gives up when the
competing memories genuinely share a context. The proposed change is small -- store each memory's context
as one more feature and include it in the lookup -- but it must be tested on real reading, with the
system's real context, before we claim it helps comprehension.

## QUESTIONS
None blocking. One judgement call for the owner at integration: I read the bar as MET (a WIN --
context reinstatement resolves interference CI-separated, twins lose, leak-safe, fan effect exhibited) and
filed SOLVED. It is a SYNTHETIC construction proof on the real retrieval rule, not a live-text result -- if
you require a real-context/coref demonstration before SOLVED, mark it PARTIAL on that sub-clause; the
mechanism and all controls stand either way.

## NEXT STEPS
1. Wire the encoding CONTEXT as a per-item feature into the register + additive `decode_cue` (default-off),
   using the situation-model / reading-loop context vector as the source. Fixed w_ctx; no gate, no fan
   penalty, no per-trial diagnosticity weighting.
2. Build the REAL instrument: coref-under-ambiguity / situation-model retrieval with genuinely similar
   competing referents, and test whether the substrate's ACTUAL context is separable (the load-bearing
   open question -- the boundary population shows the mechanism needs separable context).
3. Optional deeper fidelity: a competitive/normalised (divisive-norm) read instead of noisy-argmax; and
   context PATTERN-COMPLETION from a partial cue before retrieval.
4. Coordinate with the content_addressable landing -- this composes directly on top of it (same additive
   rule, one more feature).

---

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT / SOLVED (owner-DONE). Full SOLVED re-read FRESH (standing rule).
Re-verified scaffold-free FIRST-HAND (test_context_interference_resolution.py, 6 assertions PASS: CONTENT_ONLY==live
organ 0 mismatches; CTX_ADD 0.928 vs 0.400 @K=8 CI-sep at every K; twins lose; leak guard CTX_ALONE 0.306<<oracle 0.994;
residual fan effect; boundary collapse 0.494 when context non-separable). The missing organ for similar-competitor
interference is CONTEXT REINSTATEMENT at retrieval -- the SAME additive Lewis-Vasishth rule + one context feature (TCM
Howard-Kahana). Brain-faithful (Teyler-Rudy indexing, ACT-R noisy read -> fan cost emerges, not a penalty). Genuine
leak-safe CUE COMBINATION; solver caught + demoted its OWN soft-oracle (diagnosticity-weighting peeks). Closes the open
loop the content_addressable integration handed over. SYNTHETIC construction proof -- live capability (is the substrate's
REAL context separable across similar memories?) GATED on p1 wire-and-measure. NO new hdlab organ (AdditiveCueRetrieval
already feature-agnostic; context is just another feature) -> the live wiring (store the GRADED situation-model context
as a per-item feature) folds into p1's retrieval-first composition, NOT pre-landed. AUDIT UPDATEs folded (§2b new entry;
E2/E3 fan-effect RESOLVED; DG re-framed to context-indexing; context_vector sign()/graded note). Review EXCELLENT +
SOLVER REVIEW in PROBLEM.md; priority cleared. Committed (no push).
