---
owner_verdict: DONE
---

SUBMISSION — optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost
STATUS: SOLVED (byte-identical speed) + a brain-foundational chain finding. WIP until owner_verdict:
DONE. Glass-box, NO LLM, no new dependency. BYTE-IDENTICAL output. NO hdlab written (Q111; proposed
diff in SOLVED.md). Witnessed; ledger clean (malformed/incomplete: 0).
REVERIFY: .venv/Scripts/python.exe verification/test_pos_tagger_speedup_byte_identical.py   # 4/4

WHAT IT DOES (the owned problem). Profiling confirmed the brief: ~70% of the tag cost is emission-matrix
construction — pos_features is called once per token PER TAG (34,340x on a 2,020-tok slice), each
rebuilding ~22 feature strings + summing dict lookups. Every emission feature is <base>~<tag> with a
TAG-INDEPENDENT base, so 16/17 of that is redundant. Fix (P8's parser technique adapted to the DICT
weight structure): precompute the transition matrix + start vector once; split weights into per-tag
emission dicts; build each token's bases ONCE; sparse-accumulate per tag lane; keep the numpy Viterbi DP
verbatim.
RESULT: 4.4x-5.25x faster on a warm run (per-call cost cut 77-81%). PROVABLY BYTE-IDENTICAL: on 694
HELD-OUT LitBank sentences / 15,684 tokens (8 books NOT used to tune) the optimized tagger reproduces
the stock EMISSION MATRIX bit-for-bit (np.array_equal, 0 mismatch) AND the tag sequence exactly (0
mismatch). Read-level: 1.19x (16% of a whole warm read cut) on top of P8's parser fix.
FLOOR: the live Collins-Viterbi averaged-perceptron tagger (warm median 2.571s / 694 sents -> 0.490s).
CONTROLS (the "info-free twin" analog for a byte-identical problem): BYTE-IDENTITY (emission-matrix
np.array_equal + tag-sequence equality, 0/694) excludes a faster-but-DIFFERENT tagger; HELD-OUT (8 docs
!= the profiling doc) excludes tuning to the slice; FAIR-TIMING (interleaved same-process medians,
threads pinned) excludes shared-box noise; OUTPUT-IDENTITY (whole warm SituationReader.read output
byte-identical) excludes ANY downstream-consumer regression; CONSERVATIVE-FALLBACK (variant A, identical
by construction, 0/0) excludes reliance on the compensated-sum argument.

NO-REGRESSION (owner ask #2), proven not asserted: a full warm read comes out byte-identical under the
fast tagger — events, entities, coref_acc, n_targets, causal, timeline all equal. Identical tags ->
identical everything downstream, by construction, verified end-to-end on a real LitBank doc.

KEY REALIZATION (the enabling move). An early sparse variant gave byte-identical TAGS but a ~1e-15
DIFFERENT emission matrix — because CPython 3.12's sum() is Neumaier-COMPENSATED, not left-to-right. A
tag-only witness would have MISSED it (until it flips an argmax on a tie). Byte-identity REQUIRES routing
the final reduction through the SAME sum() the stock path uses; the witness asserts the EMISSION MATRIX
bit-identical (stronger than tag equality) precisely to catch this class. Corollary: dropping the
0.0-default terms is safe *because* adding 0.0 is a no-op inside Neumaier's sum (confirmed 0/694), which
is what makes the sparse-per-lane variant both fast AND identical.

BRAIN-FOUNDATIONAL CHAIN (owner ask #1: make EVERY component, self+upstream, brain-foundational; full
detail in BRAIN_FOUNDATIONAL_CHAIN_FINDING.md; research via hdi_research):
 - The tagger's BOTTOM-UP model IS brain-faithful: the Collins-2002 perceptron update is in the
   Widrow-Hoff/delta-rule family = the Rescorla-Wagner family (error-driven, cue-competition) — which is
   WHY a generative P(word|tag) tagger regresses (it double-counts correlated cues). So this byte-
   identical speed win PRESERVES a brain-faithful computation. [MacDonald 1994; Ramscar 2010; Baayen 2011]
 - WHERE WE LOSE SIGNAL is MEANING, measured fresh (UD-EWT gold, 24,120 tok): 85.1% of tagger errors
   touch a CONTENT class; the biggest bucket is PROPN<->NOUN (28% of ALL errors) — a referential/world-
   knowledge call surface form can't make. Same wall the arc-parser finding + the reader's WSD work hit;
   independently confirmed [Altmann-Kamide 1999; Trueswell 1994].
 - WHAT THE SPEED ENABLES (the new point): the strictly-more-brain-foundational GRADED ranked-parallel
   decode (Viterbi 1-best + forward-backward posterior = exactly P7's CRF representation) is byte-
   identical on the 1-best AND runs at 0.632s vs the stock hard-1-best 1.099s — CHEAPER than what we
   ship today. The ~5x headroom makes the brain-faithful graded decode affordable per read. HONEST
   CAVEAT: mechanism-fidelity != accuracy; the graded candidates cash out only once top-down MEANING
   (grounding) re-ranks them (the prior joint tag<->parse loop regressed without it). Speed ENABLES the
   brain-foundational decode; grounding CASHES it.
 - CONSUMERS TO REVISIT (owner ask #3): every consumer gates on a HARD 1-best tag (consequence_learning
   VERB-gate; referent_per_np NP detection — where the PROPN<->NOUN error lands in entity/coref). With
   the tagger fast + the posterior now affordable, consuming the GRADED posterior (uncertainty-aware,
   brain-foundational ranked-parallel) is a FAMILY of follow-on problems, referent_per_np first.

FILES (experiments/ + verification/ + own problem folder only; NO hdlab written):
  experiments/exp_pos_tagger_{profile,fastfeat,read_delta,brain_foundational_chain}_v1.py
  verification/test_pos_tagger_speedup_byte_identical.py
  notes/problems/<slug>/{SOLVED.md, BRAIN_FOUNDATIONAL_CHAIN_FINDING.md}

PROPOSED hdlab (strategy lands, Q111 — default-ON, byte-identical, the witness is the gate):
  Route PosTagger.tag / perceptron._viterbi through the fast path: at load, precompute TM+SV and split
  weights into per-tag emission dicts + base_contrib; replace the emission build with variant-C sparse-
  per-lane (token_bases + base_contrib + per-lane sum()); keep the numpy DP verbatim. Bodies in
  exp_pos_tagger_fastfeat_v1 (FastTagger._em_C, token_bases). If a float-reasoning-free path is
  preferred, land variant A (_em_A, ~2.6x) — same witness passes. SAME axis as P8's parser, DISTINCT
  code path (dict weights, not the crc32 2^21 vector); DISTINCT from the SOLVED tagger CALIBRATION.

AUDIT UPDATE: no fidelity-map change (output byte-identical). Fold one note — the perceptron bottom-up
model is brain-faithful (delta-rule = Rescorla-Wagner); the remaining gap is the DECODE (1-best vs the
brain's graded ranked-parallel + top-down), a decode/grounding matter untouched by this speed change.

TLDR: the part-of-speech labeller was rebuilding the same word-clues 17 times per word (once per
possible label). I made it do that once — same labels, checked letter-for-letter on ~15,700 words from
books it wasn't tuned on, ~5x faster, ~16% off a whole read on top of the earlier parser speedup.
Output is identical so nothing downstream can break (confirmed byte-for-byte). Against the brain: it
keeps several ranked guesses and uses meaning to settle hard cases; ours commits to one guess — and the
speed-up makes the more brain-like "several ranked guesses" version CHEAPER than what we run now, but
that only pays once we give it word-meaning (the real wall: 85% of its mistakes are meaning-dependent).

QUESTIONS: none. NEXT: (1) land the Q111 fast path (default-ON, witness-gated) — free ~5x tagger
speedup on every read, compounding with P8; (2) file the graded-consumption follow-on (referent_per_np
first, attacks PROPN<->NOUN); (3) the meaning wall remains the typed-grounding problem the arc-parser
finding named — the one component whose brain-foundational grounding lifts the whole chain.
