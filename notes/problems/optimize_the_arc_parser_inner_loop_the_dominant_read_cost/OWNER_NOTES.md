---
owner_verdict: DONE
---

SUBMISSION — optimize_the_arc_parser_inner_loop_the_dominant_read_cost
STATUS: SOLVED (byte-identical speedup) + a brain-foundational DIRECTION with a proven path.
WIP until owner_verdict: DONE. Glass-box, NO LLM, BYTE-IDENTICAL output. NO hdlab written
(Q111; proposed diff in SOLVED.md). Witnessed; ledger clean (malformed/incomplete: 0).
REVERIFY: .venv/Scripts/python.exe verification/test_arc_parser_speedup_byte_identical.py   # 4/4

WHAT IT DOES (the owned problem). The arc-factored parser rebuilt ~2.2M feature strings + crc32
hashes per document (the dominant per-parse cost). Measured the redundancy (feature strings reuse
26.9x; whole-arc arrays reuse only 1.07x), then optimized the feature-ID assembly with per-template
integer caches + one batched np.add.reduceat scoring + token-local hoisting.
RESULT: 3.53x faster (parse cost cut 72%; 1.262s->0.357s, 58-sent slice). PROVABLY BYTE-IDENTICAL:
393,225 arcs across 5 held-out books match stock _arc_ids exactly; 0/376 sentences differ in
heads/arcs/margins. Warm read 1.13-1.45x faster, reader output byte-identical.
BRIEF PREMISE CORRECTED (disk > brief): the "parser = 73% of a read" is a cProfile artifact; warm,
the parser is ~26%, so the read-level win is 1.2-1.45x, not ~2x. Also corrected: the parser is
arc-FACTORED graph-based, not "arc-standard shift-reduce."

SESSION EXTENSIONS.
1) BREADTH: same byte-identical memoization applied to the brain-foundational arc-EAGER parser
   (+1.12x, 0 head/conf/margin mismatch) — a general primitive (both parsers + the POS tagger share
   the hashed-feature shape). arc-eager is O(n) and already ~8.4x faster than arc-factored AND +0.05
   UAS: the parser SWAP dominates the micro-opt.
2) NO-REGRESSION: reader consumers (events, coref_acc, pronoun targets, causal) IDENTICAL with the
   arc-eager route on vs off on 3 LitBank docs, and faster; the byte-identical opts change no output
   by construction.

BRAIN-FOUNDATIONAL DIRECTION (see BRAIN_FOUNDATIONAL_UPSTREAM_FINDING.md). "Overcome the wall by
making every component brain-foundational." Measured chain: arc-EAGER (incremental, brain-foundational)
0.842/0.805 UAS beats arc-factored 0.791/0.761. MY HYPOTHESIS REFUTED: making the upstream tagger
"brain-foundational" (one-pass generative, incremental beam, TnT morphology, trigram prediction) does
NOT exceed the live perceptron (0.924 vs 0.945, even OOV 0.737 vs 0.814) — the perceptron is already
cue-based/error-driven, so a generative swap is a fidelity DECREASE (corroborates, not refutes, the
thesis). The one new lever (joint tag<->parse) has +0.016 ORACLE headroom but REGRESSES with predicted
structure — gated on parser accuracy (circular). So the binding non-faithful component is NOT any
decode algorithm; it is the missing lexical-SEMANTIC grounding (the meaning channel).
CLEAR PATH, PROTOTYPED + GROWN: on PP-attachment (canonical grounding-sensitive decision), growing a
grounding lexicon lifts accuracy floor 0.587 -> 0.639 (+0.052), MONOTONIC in grounding size and still
RISING at 100% corpus toward the ~0.84 ideal; info-free (shuffled-prep) twin collapses to 0.512. IDEAL
verified: LEXICAL co-occurrence grounding is load-bearing; the generic topical hub does NOT help — the
ideal needs syntactically-TYPED (head, grammatical-function) selectional preference (Pado/Resnik), same
lesson as the WSD wall. Organs to grow it: grounding_acquisition_loop + cls_growth (safe growth) +
WordNet.

VS THE BRAIN: tagging 0.945 vs ~0.97 (near-parity); parsing 0.842 vs human ~0.95 (materially below);
PP-attachment 0.64 vs human ~0.88 — the deficit is concentrated exactly where meaning is required.

FILES (experiments/ + verification/ only; NO hdlab written):
  exp_arc_parser_{profile,feature_stats,fastfeat_v1,v2,v3,read_delta}_v1.py
  exp_arceager_fastfeat_v1.py, exp_brain_foundational_tagger_v1.py/_v2.py,
  exp_grow_grounding_pp_attachment_v1.py, verification/test_arc_parser_speedup_byte_identical.py

KEY REALIZATIONS.
  - Reuse is at the FEATURE grain (26.9x), not the ARC grain (1.07x) — measured both before choosing.
  - VERIFIED np.add.reduceat is bit-identical to per-arc .sum() (max diff 0.0) BEFORE relying on it;
    kept the reduction untouched so byte-identity is by construction, not luck.
  - The premise "73% of a read" was a profiler artifact; patch-and-time corrected it (Test 4).
  - "More brain-foundational" is not automatically better: a fidelity DECREASE (generative tagger)
    regresses — which is why the perceptron already being cue-based matters.
  - The wall isn't decode speed/algorithm; it's typed grounding (meaning), and it GROWS.

PROPOSED hdlab (strategy lands, Q111):
  (a) route ArcParser.parse/eval_uas through the memoized fast path (FeatCache + sentence_scores +
      decode_from_scores; bodies in exp_arc_parser_fastfeat_v3/v2); default-ON, byte-identical, witness
      is the gate. Apply the crc32 memo to arceager_parser too.
  (b) evaluate flipping the default parse to arc-eager (free +0.05 UAS + ~8x speed, consumers byte-safe).

FRONTIER / NEXT STEPS.
  1) File the TYPED-GROUNDING (meaning-channel) problem — grow (verb,role,arg)+(head,prep,object)
     selectional preference with WordNet-class backoff, online via grounding_acquisition_loop under
     cls_growth; this is where the accuracy headroom lives and it unblocks the joint tag<->parse loop.
  2) Land the two byte-identical memoizations + flip arc-eager on.
  3) Optional: remote full-board timing for the exact board-level speedup number.

TLDR: made the grammar parser 3.5x faster with byte-for-byte identical output (proven on 393k
decisions), showed the brain-style parser is both ~8x faster and more accurate (swap it in — nothing
else regresses), and — chasing "make it as good as a brain" — found the real wall is meaning, not
speed, and proved the escape route: grow a grammar-typed meaning lexicon from reading (accuracy climbs
steadily and hasn't plateaued). That last build is the meaning-channel next problem.

QUESTIONS: none. NEXT: your call to re-verify + land the byte-identical speedup and the arc-eager
flip; file the typed-grounding problem as the meaning-channel follow-on.
