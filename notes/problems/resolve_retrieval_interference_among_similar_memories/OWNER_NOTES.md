---
owner_verdict: DONE
---

SUBMISSION -- SOLVER RESULT: resolve_retrieval_interference_among_similar_memories
STATUS: SOLVED (bar met -- a WIN) | ledger malformed/incomplete: 0
REVERIFY: .venv/Scripts/python.exe verification/test_context_interference_resolution.py  (PASS, 6 assertions)
NO hdlab/ MODIFIED (proposed diff below; strategy lands it, Q111). Integrate only on owner_verdict: DONE.

THE ANSWER IN ONE LINE
The missing organ for "which of several SIMILAR memories" is CONTEXT reinstatement at retrieval -- and it
is the SAME additive rule we already have, given one more feature. Adding the encoding context to the
landed additive Lewis-Vasishth activation resolves fan-effect interference CI-separated over the
context-free baseline at every competitor count, with the info-free twins losing, leak-safe (neither cue
alone resolves it -- it is genuine cue COMBINATION), while still EXHIBITING the residual fan effect and
correctly COLLAPSING when the competing memories share a context.

THE BAR (verbatim, PROBLEM.md S7): "On a retrieval task with genuinely SIMILAR competitors (same-cluster /
near-duplicate memories), floor recomputed on its population: context-based interference resolution (add
the encoding CONTEXT to the additive activation, and/or separate at ENCODING) must recover the correct
competitor CI-separated over the CONTEXT-FREE additive baseline's UPPER bound, with the info-free twin
(SHUFFLED / RANDOM context) LOSING CI-separated, CI half-width + null p95 reported. AND it must still
EXHIBIT the residual fan effect ... Sweep context weight / separation level / competitor similarity."
DECISIVE EITHER WAY: a WIN -> context reinstatement is the missing organ; strategy wires it (default-off).

INSTRUMENT: a same-content-cluster interference instrument on the REAL hdlab additive retrieval organ
(hdlab.content_addressable_retrieval.AdditiveCueRetrieval). Each memory = per-feature FHRR codes
{entity,event,role} + a CONTEXT code + a payload filler. A CLUSTER = memories sharing the entity-prototype,
event AND role (genuinely similar -- content underdetermines the choice), differing only in encoding
CONTEXT (a TCM Howard-Kahana drifting vector; members encoded at different times -> distinct contexts) and
payload. Cue = a PARTIAL content cue (noisy target entity; event+role shared -> ambiguous among the
cluster) + a NOISY reinstatement of the target's context (it BIASES, does not identify). Every arm's
decision is an ACT-R read (activation + logistic noise -> argmax), so the fan effect EMERGES from the rule
(NOT the ACT-R fan penalty, which prior work found regime-specific). CONTENT_ONLY is asserted
bit-identical to the live AdditiveCueRetrieval argmax. Operating point (eta=1.6 x content_sigma=0.6) LOCATED
by a regime sweep, leak-conservative, and the win holds across the WHOLE swept grid (robust, not tuned).

THE DECISIVE TABLE (filler recovery hit@1; n=180 per K = 60 clusters x 3 TEST seeds; d=256):
  fan K (competitors)          1        2        4        8
  CONTENT_ONLY (context-free)  0.722    0.661    0.583    0.400    <- steep fan collapse
  CTX_ADD (content+context)    0.972    0.961    0.917    0.928    <- resolves, gentle fan
  CTX_ADD - CONTENT (paired)  +0.250   +0.300   +0.333  +0.528    all CI-separated (>0)
    CI at K=8: [+0.4500,+0.6056]; CONTENT upper-95 = 0.4729, CTX_ADD lower-95 = 0.8804 (clears)
  CTX_ALONE (leak check)       0.706    0.578    0.461    0.306    << oracle (never identifies)
  CTX_ORACLE (exact ctx, DV)   1.000    1.000    0.994    0.994    DV can detect resolution
  SHUFFLE twin / RANDOM twin   ~track CONTENT_ONLY; CTX_ADD - twin > +0.58 at K=8, CI-separated

ROBUST FINDINGS
1. CONTEXT RESOLVES SIMILAR-COMPETITOR INTERFERENCE, and it is the SAME additive rule + a context feature.
   CTX_ADD beats the context-free additive baseline CI-separated at every fan level (up to +0.53 at 8
   competitors). The landed AdditiveCueRetrieval is feature-agnostic, so context reinstatement needs NO new
   math -- it is a stored "context" slot + a "context" cue.
2. LEAK-SAFE -- the win is genuine CUE COMBINATION. Context ALONE (0.31 at K=8) is far below the exact-
   context oracle (0.99) and at/below content-only; neither the weak content cue nor the weak context cue
   resolves it alone, their SUM does. Both info-free twins (shuffled stored context; random cue context)
   LOSE CI-separated -> the context term carries a real signal, not a free extra channel.
3. RESIDUAL FAN EFFECT EXHIBITED, not eliminated. Content-only collapses 0.72->0.40 with competitor count
   (steep); CTX_ADD degrades 0.97->0.93 (gentle) -- resolution REDUCES but does not abolish interference,
   brain-correct. A zero-fan model would have leaked.
4. BOUNDARY (the bar's decisive negative branch, characterised): competitors encoded ADJACENT in time
   (NON-separable context) collapse CTX_ADD 0.928->0.494 and context-alone to 0.13 -- context resolves
   interference ONLY when the memories HAVE separable context. This names WHY interference can be
   irreducible.

BRAIN DRILL, PASS 1 (owner: "confirm brain-foundational"):
- HOW context enters: ADDITIVE (CTX_ADD, one Lewis-Vasishth cue feature) BEATS a MULTIPLICATIVE gate
  (CTX_GATE) at every K -> consistent with the landed additive organ.
- ENCODING vs RETRIEVAL separation: ENC_SEP (bind context into the stored trace, no retrieval context)
  FAILS ~content; ENC_SEP_CTX (separate AND reinstate) ties CTX_ADD -> the lever is context-at-RETRIEVAL;
  encoding-separation is only a substrate needing the same context key.
- The fan effect EMERGES from the ACT-R noisy competitive read (activation + logistic noise), so I did NOT
  add the regime-specific ACT-R fan penalty (prior finding 9).
- CMR robustness: when context CARRIES content (content-correlated, the faithful case), the win SURVIVES
  CI-separated at content-mix 0/0.3/0.6 but degrades gracefully (0.95->0.77) -- not dependent on context
  being independent of content.
- A FIDELITY FIX I MADE UNDER THE DRILL: the diagnosticity-weighted "cognitive control" arm (CTX_CONTROL)
  BEAT the exact-context oracle (0.972 > 0.856) in the boundary -- impossible without a peek. It computes
  cue weights from the candidate set, so with a target-derived cue it up-weights the feature the target is
  an outlier on (a soft oracle). DEMOTED to a labelled ceiling; the headline/bar arm is fixed-weight
  CTX_ADD. The faithful non-peeking control reduces to choosing w_ctx, which CTX_ADD already does.

BRAIN DRILL, PASS 2 (owner: "is the machinery in PROXIMITY faithful? optimizations?") -- `--deep` mode,
read the real organs (dg_pattern_separation.py, grounding_acquisition_loop.context_vector):
- (A) The REAL DG organ (dg_separate) at ENCODING on the content code is NEUTRAL: DG_CONTENT 0.367 ~
  CONTENT_ONLY 0.372, DG+CTX 0.944 ~ CTX_ADD 0.944 (K=8). Canonical DG expand+sparsify does not resolve
  context-separable interference -- extends the prior DG-at-retrieval NEGATIVE to encoding, and confirms
  the faithful separator is context-INDEXING (Teyler-Rudy), not content-sparsification. (I had substituted
  a convenient context-bind for canonical DG in ENC_SEP; testing the real organ shows that was correct.)
- (B) Context reinstatement SURVIVES from a partial FRAGMENT (15-60% of components, the rest
  pattern-completes -- the Nakazawa CA3 partial-cue regime applied to CONTEXT): +0.65 at 60%, +0.59 at
  30%, +0.38 at 15%. No handed-over context copy is needed -- closes the "where does the reinstated context
  come from" gap.
- (C) The fan effect appears in LATENCY too (the bar said "recovery/latency"): the winner-runnerup
  activation MARGIN (ACT-R retrieval-time correlate) SHRINKS with fan, 0.99->0.72 (K=1->8).
- PROXIMITY NOTE: the substrate's REAL context (context_vector) is a content-derived bag-of-words,
  sign()-quantized -> the CONTENT-CORRELATED regime is the faithful operating point (win weaker but
  survives), and GRADED (non-sign) context is more separable -> the recommended wiring.

CONTROLS (what each EXCLUDED): SHUFFLE twin (stored contexts permuted) + RANDOM twin (cue context is noise)
both LOSE CI-separated -> real context signal, not a free channel; CTX_ALONE << oracle -> context BIASES not
identifies (leak guard), the win is cue combination; CTX_ORACLE near ceiling -> DV validity; CONTENT_ONLY
== live organ argmax (0 mismatches) -> the baseline IS the live rule; fan curve -> residual fan exhibited;
BOUNDARY (adjacent context) collapse -> context must be separable; CMR content-mix -> not dependent on
independent context; CTX_GATE < CTX_ADD -> context is additive; ENC_SEP alone fails / DG-on-content neutral
-> the lever is context-at-retrieval; CTX_CONTROL demoted (peeks).

AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, E2/E3 + section 2b):
1. The open problem the content_addressable SOLVED handed over (similarity-interference / fan effect) is
   RESOLVED in principle: the missing organ is CONTEXT REINSTATEMENT at retrieval (0.93 vs 0.40 at 8
   competitors, twins losing, leak-safe, residual fan exhibited). The additive cue-retrieval rule is
   complete only WITH a context cue.
2. Context enters ADDITIVELY (one Lewis-Vasishth cue feature), not as a multiplicative gate.
3. DG separation should be re-framed as context-INDEXING at ENCODING (Teyler-Rudy), NOT content
   sparsification -- now tested with the REAL organ (dg_separate at encoding is NEUTRAL); the lever is
   context-at-RETRIEVAL.
4. NEW pinned mechanism for the audit's decision rule: the ACT-R noisy competitive read (activation +
   logistic noise -> argmax) makes the residual fan effect intrinsic -- do NOT use the ACT-R fan PENALTY.
5. The substrate's REAL context vector is content-derived (bag-of-words) and sign()-quantized -> the
   content-correlated regime is the faithful operating point; use the GRADED context; ties the organ to the
   CLS fast/hippocampal tier (consolidation-to-schema is the slow-tier complement -- flagged, not built).

PROPOSED hdlab CHANGE (strategy lands it, Q111 -- I did NOT write hdlab/):
1. STORE THE ENCODING CONTEXT AS A PER-ITEM FEATURE in the register and include it in the additive
   decode_cue (no new math -- the rule is feature-agnostic; add a {entity,event,role,CONTEXT} slot + a
   partial reinstated context in the cue). Default-OFF flag. Context source = the situation-model /
   reading-loop context; use its GRADED form (context_vector(graded=True)), NOT the sign()-quantized
   default. A partial-fragment reinstatement suffices (finding 9), so exact context recovery is not needed.
2. Fixed goal-driven w_ctx; do NOT ship the per-trial diagnosticity weighting (it peeks -- an optimistic
   ceiling here).
3. Do NOT ship the multiplicative gate (additive wins) and do NOT ship the ACT-R fan penalty (the fan
   effect already emerges from the noisy read).
4. Encoding-separation is OPTIONAL and redundant with retrieval-side context here; if used it must be
   context-INDEXING, not DG content-sparsification (neutral/negative with the real organ).
5. MEASURE ON THE LIVE coref / situation-model task before any capability claim -- this is a SYNTHETIC
   construction proof; the load-bearing open question is whether the substrate's ACTUAL context is
   separable across similar memories (the boundary population shows the mechanism needs separable context).

KEY REALIZATIONS: (a) the discriminating info is not content -- stop matching content better, add the
variable the memories actually differ on (context). (b) The win had to be CUE COMBINATION, not a second
key -- locating an operating point where context ALONE and content ALONE both fail but their SUM resolves
turned a possible leak into the strongest evidence. (c) A twin that TIES content is as informative as one
that loses. (d) The fan effect should EMERGE from a noisy competitive read, not be added as a penalty.
(e) Auditing my OWN machinery caught a soft oracle (the control arm beat the exact-context oracle) -- the
owner's "is the proximity machinery faithful?" prompt forced it. (f) Reading the real organs showed
canonical DG-on-content is NEUTRAL here and the real context is content-derived+sign-quantized -- the
faithful separator is context-indexing and the faithful context is graded.

WHAT I DID NOT ESTABLISH / DO NOT QUOTE: SYNTHETIC construction proof (FHRR + synthetic TCM context), NOT
a live-text/coref win -- withdraw first any claim it moves a live reading number; measure on the live task.
The context is engineered separable at the headline point; whether the substrate's REAL context is
separable across similar memories is OPEN (the boundary shows collapse when it is not). CTX_CONTROL is an
OPTIMISTIC CEILING (peeks) -- do NOT quote it as a win over CTX_ADD. The competitive read is noisy-argmax,
not divisive-normalisation/attractor (untested). All numbers on the synthetic instrument; none crosses to a
real coref/text task.

FILES: experiments/exp_context_interference_resolution_v1.py (+ --sweep / --fidelity / --deep modes);
verification/test_context_interference_resolution.py;
notes/problems/resolve_retrieval_interference_among_similar_memories/DESIGN_brain_analysis.md;
data/exp_context_interference_resolution_v1/metrics.json. NO hdlab/.

TLDR (plain language): Our memory gets fooled when two stored memories are very alike -- it grabs the
wrong one (the known "fan effect," which a faithful model should still show a bit of). The brain does
better by using the CONTEXT a memory was formed in ("the bank by the river"). I built exactly that -- add
the encoding context to our existing lookup rule -- and tested it with clusters of near-identical memories.
It works: with up to 8 look-alikes, adding context lifts getting the right one from ~40% to ~93%; a
scrambled context does NOT help (so it is a real signal); context by itself is NOT enough either (the win
comes from COMBINING the weak content clue with the weak context clue, so it is not cheating); it still
slips gracefully as look-alikes pile up (the honest fan effect); and it correctly gives up when the
competing memories genuinely share a context. Pushing deeper: only a FRAGMENT of the context is needed, the
brain's dedicated "pull-apart" tool (DG) does nothing here because the memories differ in context not
content, and the slowdown-with-more-competitors shows up too. The change is small -- store each memory's
context as one more feature and include it in the lookup -- but it must be tested on real reading, with the
system's real context, before we claim it helps comprehension.

QUESTIONS: none blocking. One judgement call: I filed SOLVED (a WIN -- CI-separated, twins lose, leak-safe,
fan effect exhibited). It is a SYNTHETIC construction proof on the real retrieval rule; if you require a
real-context/coref demonstration before SOLVED, mark PARTIAL on that sub-clause -- the mechanism and all
controls stand either way.

NEXT STEPS: (1) wire the encoding CONTEXT as a per-item feature into the register + additive decode_cue
(default-off), using the GRADED situation-model/reading-loop context; fixed w_ctx, no gate, no fan penalty,
no peeking diagnosticity. (2) Build the REAL instrument: coref-under-ambiguity / situation-model retrieval
with genuinely similar competing referents, and test whether the substrate's ACTUAL context is separable
(the load-bearing open question). (3) Optional deeper fidelity: a divisive-normalisation/attractor
competitive read; context pattern-completion from a partial cue. (4) Coordinate with the content_addressable
landing -- this composes directly on top of it (same additive rule, one more feature).
