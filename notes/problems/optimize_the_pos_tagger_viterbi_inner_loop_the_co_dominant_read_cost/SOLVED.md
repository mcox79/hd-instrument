---
problem: optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost
status: SOLVED
bar: "PASS = a materially faster POS tagger (target: tagger per-call cost at least halved on a warm read; report the measured factor on a warm read AND the read-level delta) with PROVABLY BYTE-IDENTICAL tags on a held-out sentence set (a witness that asserts tag-sequence equality pre/post, at scale, on documents NOT used to tune), glass-box, NO new runtime dependency (no C-extension unless the owner approves) and NO LLM."
result: "POS tagger 4.4-5.25x faster on a warm run (per-call cost cut 77-81%), BYTE-IDENTICAL: on 694 HELD-OUT LitBank sentences / 15,684 tokens the optimized tagger reproduces the stock EMISSION MATRIX bit-for-bit (np.array_equal, 0 mismatch) AND the tag sequence exactly (0 mismatch); read-level delta 1.19x (16% of a whole warm SituationReader.read cut) with BYTE-IDENTICAL read output (events/entities/coref/targets/causal/timeline all identical)."
floor: "the live stock Collins-Viterbi averaged-perceptron tagger (hdlab/pos_tagger.py -> hdlab/perceptron._viterbi); warm median 0.44s / 58 sents (same-process), 2.57s / 694 held-out sents; the optimization must beat this AND reproduce its output exactly."
controls: "BYTE-IDENTITY (emission-matrix np.array_equal + tag-sequence equality, 0/694 held-out sents mismatch) -- excludes a faster-but-different tagger; HELD-OUT (8 LitBank docs distinct from the profiling doc 1023_bleak_house) -- excludes tuning to the measured slice; FAIR-TIMING (interleaved same-process medians, OMP/threads pinned to 2 on the shared box) -- excludes machine-noise inflation; OUTPUT-IDENTITY (whole warm SituationReader.read output byte-identical stock-vs-fast) -- excludes any downstream-consumer regression; CONSERVATIVE-FALLBACK (variant A, provably identical by construction, also 0 mismatch) -- excludes reliance on the compensated-sum argument."
files_changed: "experiments/exp_pos_tagger_profile_v1.py, experiments/exp_pos_tagger_fastfeat_v1.py, experiments/exp_pos_tagger_read_delta_v1.py, experiments/exp_pos_tagger_brain_foundational_chain_v1.py, verification/test_pos_tagger_speedup_byte_identical.py, notes/problems/optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost/BRAIN_FOUNDATIONAL_CHAIN_FINDING.md, notes/problems/optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost/SOLVED.md  (NO hdlab/ written -- Q111 proposed diff below)"
reverify: ".venv/Scripts/python.exe verification/test_pos_tagger_speedup_byte_identical.py"
---

# SOLVED — the POS tagger's per-call Viterbi is 4.4–5.25x faster, byte-identical

## What I built (the mechanism)
First-hand cProfile of a warm tag loop (`exp_pos_tagger_profile_v1`) confirms the brief: ~70% of the
tag cost is EMISSION-MATRIX construction — `pos_features` is called **n_tokens × n_tags** times (per
token, PER TAG: 34,340 calls on a 2,020-token slice), each rebuilding ~22 feature STRINGS, then
`sum(weights.get(f,0.0) for f in feats)`. The `_viterbi` DP itself is only ~6% and the transition
matrix is rebuilt per sentence though it is CONSTANT.

The key structural fact: **every emission feature is `<base>~<tag>` where `<base>` is TAG-INDEPENDENT.**
So the per-tag rebuild is pure redundancy. The fast tagger (`exp_pos_tagger_fastfeat_v1.FastTagger`),
reusing P8's parser pattern adapted to the DICT weight structure:
1. **Precompute** the transition matrix TM (17×17) and start vector SV ONCE from the model (constant).
2. **Split** the weight dict ONCE into per-tag emission dicts (`Wtag[k]: base -> weight`) and a
   `base_contrib` map (`base -> [(tag_idx, weight)]`). Byte-identical: `Wtag[k].get(base,0.0) ==
   weights.get(base+"~"+tag_k, 0.0)` exactly (rsplit on the last '~'; `tt:` keys are transitions;
   verified: 148,163 emission + 305 transition keys, 0 unparseable).
3. **Build each token's tag-independent base list ONCE** (in the EXACT order `pos_features` emits).
4. **Emission (variant C, sparse per-lane):** collect the PRESENT weights per tag lane in base order,
   then `sum()` each. The per-lane lists are allocated once per sentence and cleared per token.
5. **DP:** the stock numpy Viterbi verbatim, fed the fast emission + precomputed TM/SV → identical V,
   bp, argmax tie-breaking → identical tags.

Two byte-identical variants shipped: **C (sparse per-lane, 4.4–5.25x)** and **A (per-tag full-sum,
~2.6x, provably identical by construction — the conservative fallback)**.

## The numbers (with floor, controls, scorer, population)
- **Warm per-call speedup (same-process interleaved medians, threads pinned):** variant C **4.37x** on
  the 58-sent / 2,020-tok profiling slice; **5.25x** on the 694-sent / 15,684-tok held-out set
  (stock 2.571s → fast 0.490s). Variant A: 2.55–2.60x.
- **BYTE-IDENTITY at scale (the bar):** 694 HELD-OUT LitBank sentences / 15,684 tokens from 8 docs
  distinct from the profiling doc — emission matrix bit-identical (np.array_equal, **0 mismatch**),
  tag sequence identical (**0 mismatch**). Variant A also 0/0. (`verification/test_pos_tagger_speedup_byte_identical.py`, 4/4.)
- **Read-level delta:** warm `SituationReader.read()` on a real LitBank doc **1.19x (16% of the whole
  read cut)**, with the read OUTPUT **byte-identical** (events, entities, coref_acc, n_targets, causal,
  timeline all equal) — this is simultaneously the read-level number AND the no-regression proof.
  (`exp_pos_tagger_read_delta_v1`.) Consistent with the tagger being ~28% of a warm read × a ~5x
  tagger speedup, on top of P8's parser fix — the two front-end costs now both optimized.

## Controls — what each EXCLUDED
- **BYTE-IDENTITY (emission + tags, 0/694):** excludes a faster-but-different tagger. Emission equality
  (np.array_equal) is STRONGER than tag equality — it proves the computation is identical, not that the
  argmax happened to land the same.
- **HELD-OUT (8 docs ≠ the profiling doc):** excludes tuning to the measured slice.
- **FAIR-TIMING (interleaved same-process medians, OMP/OPENBLAS/MKL/THINC=2):** excludes shared-box
  noise (the stock baseline wandered 0.32–0.44s across runs; interleaving cancels it).
- **OUTPUT-IDENTITY (whole-read byte-identical):** excludes ANY downstream-consumer regression — tags
  feed the parser and every organ, so identical tags ⇒ identical everything, verified end-to-end.
- **CONSERVATIVE-FALLBACK (variant A, identical by construction, 0/0):** excludes reliance on the
  compensated-sum argument — if the strategy session wants a proof-free-of-float-reasoning path, A is it.

## KEY REALIZATIONS (the enabling moves)
- **CPython 3.12's built-in `sum()` is Neumaier-COMPENSATED, not left-to-right.** An earlier sparse
  variant (plain `row[k] += w` loop) produced byte-identical TAGS but a ~1e-15-different emission
  matrix — a latent regression that a tag-only witness would have MISSED (one day it flips an argmax on
  a tie). Byte-identity REQUIRES routing the final reduction through the same `sum()` the stock path
  uses. Both shipped variants (A full-sum, C per-lane sum) do; the plain-loop variant was dropped. *The
  witness asserts the EMISSION MATRIX bit-identical, not just tags, precisely to catch this class.*
- **Dropping the 0.0-default terms is safe** *because* it is a no-op inside Neumaier's compensated sum
  (empirically confirmed at scale, 0/694), which is what makes the sparse-per-lane variant both fast
  AND identical.
- **Reuse is at the BASE grain, not the (token,tag) grain:** the tag-independent bases are rebuilt
  n_tags-times redundantly; factoring them out (and splitting the dict per tag) is the whole win. Same
  lesson as P8's parser, different data structure (dict, not a 2^21 hashed vector).

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md)
No fidelity-map change is warranted: the tagger's model, feature template, and Viterbi decode are
UNCHANGED (output byte-identical). One note worth folding: research this session (hdi_research) PINS
that the tagger's bottom-up cue integration IS brain-faithful — the Collins-2002 perceptron update is
in the Widrow–Hoff/delta-rule family = the **Rescorla–Wagner** family (error-driven, cue-competition),
which is *why* a generative P(word|tag) tagger regresses (it double-counts correlated cues). So this
byte-identical speed win preserves a brain-faithful computation. The remaining fidelity gap is the
DECODE (single 1-best Viterbi vs the brain's graded ranked-parallel + top-down decode) — see the
finding doc; it is a decode/grounding matter, not touched by this speed change.

## PROPOSED hdlab CHANGE (strategy lands, Q111 — default-ON, byte-identical, the witness is the gate)
Route `hdlab/pos_tagger.PosTagger.tag` (and thereby `hdlab/perceptron.StructuredPerceptron.predict`)
through the fast path:
1. At load (`PosTagger.load`), precompute from `self._perc.weights`: (a) TM `[n_tags×n_tags]` + SV
   `[n_tags]` (constant transition potentials); (b) per-tag emission dicts + `base_contrib` (split keys
   on the last '~'; `tt:` = transition). Cache on the tagger instance.
2. Replace the emission-matrix build in `_viterbi` with the variant-C sparse-per-lane construction
   (`token_bases` + `base_contrib` + per-lane `sum()`); keep the numpy DP verbatim. Body is in
   `experiments/exp_pos_tagger_fastfeat_v1.py` (`FastTagger._em_C`, `token_bases`, DP in `.tag`).
3. Default-ON. The gate is `verification/test_pos_tagger_speedup_byte_identical.py` (emission + tags
   bit-identical on held-out + ≥2x). If strategy prefers a float-reasoning-free path, land variant A
   (`_em_A`, ~2.6x) instead — same witness passes.
This is the SAME memoization/hoist axis as P8's parser but a DISTINCT code path (dict weights, not the
crc32 2^21 vector), and DISTINCT from the SOLVED tagger CALIBRATION problem (that changed the posterior
for accuracy; this changes NOTHING about the output).

## Brain-foundational chain (owner directive — full detail in BRAIN_FOUNDATIONAL_CHAIN_FINDING.md)
Per *"make EVERY component, you and upstream, brain-foundational,"* I prototyped the chain around the
tagger and report honestly:
- **The bottom-up model is faithful** (perceptron = delta-rule = Rescorla–Wagner; the speed win is
  byte-identical so it preserves this) — PINNED by research.
- **Where we lose signal is MEANING, measured fresh** (UD-EWT gold, 24,120 tok): **85.1% of tagger
  errors touch a content class**; the biggest bucket is **PROPN↔NOUN (28% of all errors)** — a
  referential/world-knowledge call surface form can't make. Same wall the arc-parser finding and the
  reader's WSD work hit; independently confirmed (Altmann-Kamide 1999; Trueswell 1994).
- **What the speed ENABLES (the genuinely new point):** the strictly-more-brain-foundational GRADED
  ranked-parallel decode (Viterbi 1-best + forward–backward marginal posterior — exactly P7's CRF
  representation) is **byte-identical on the 1-best AND runs at 0.632s vs the stock hard-1-best 1.099s
  — cheaper than what we ship today.** The ~5x headroom makes the brain-faithful graded decode
  affordable per read. HONEST CAVEAT: mechanism-fidelity ≠ accuracy; the graded candidates convert to
  accuracy only once top-down MEANING (grounding) re-ranks them (the prior joint tag↔parse loop
  regressed without it). Speed ENABLES the brain-foundational decode; grounding CASHES it.
- **No consumer regresses** (read output byte-identical, verified). Adjacent-component map: every
  consumer gates on a HARD 1-best tag (`consequence_learning_loop` VERB-gate; `referent_per_np` NP
  detection — where the PROPN↔NOUN error lands in entity/coref); with the tagger fast and the posterior
  now affordable, revisiting them to consume the GRADED posterior (uncertainty-aware, brain-foundational
  ranked-parallel) is a FAMILY of follow-on problems, highest-leverage `referent_per_np` first.

## What I would withdraw first if wrong
The read-level 1.19x figure (single doc, whole-read timing includes many organs and machine noise). If
wrong, the load-bearing claims stand: the per-call 4.4–5.25x speedup and the byte-identity at scale
(0/694 emission + tags) are the witnessed result, and the no-regression proof is byte-identical read
OUTPUT (not a timing number).

---
### TLDR (plain English)
The step that labels each word's part of speech was one of the two slowest parts of reading a
document. It was slow because, for every word, it rebuilt the same little bag of text clues once for
every possible label and looked each one up in a big table — the same wasted work seventeen times over.
I made it compute those clues once and add up only the ones that matter, so it now produces the EXACT
same labels (checked letter-for-letter on ~15,700 words from books it wasn't tuned on) about **5x
faster**, cutting ~16% off a whole read on top of the earlier grammar-parser speedup. Because the
output is identical, nothing downstream can break — I confirmed a full read comes out byte-for-byte the
same. I also checked how a real brain does this: it keeps several ranked guesses alive and uses meaning
to settle hard cases; our labeller commits to one guess with no meaning. Interestingly, the speed-up
makes the more brain-like "several ranked guesses" version cheaper than the one guess we use now — but
that only helps once we give it word-meaning, which is the real remaining wall (85% of its mistakes are
meaning-dependent, like telling a surname from an ordinary noun).

### QUESTIONS
None. (The speed win is byte-identical and witnessed; the brain-foundational chain is a direction, not
a claim on this problem's bar.)

### NEXT STEPS
1. Land the Q111 change (variant C default-ON; witness is the gate) — free ~5x tagger speedup on every
   read, byte-identical, compounding with P8.
2. File the GRADED-CONSUMPTION follow-on: let hard-1-best consumers (start with `referent_per_np`)
   consume the now-affordable FB/CRF posterior (brain-foundational ranked-parallel; attacks the
   PROPN↔NOUN error directly). Verdict-independent adjacent-component work.
3. The meaning wall itself remains the typed-grounding problem named by the arc-parser finding — the
   one component whose brain-foundational grounding lifts the whole chain.
