---
problem: numpy_vectorize_the_arc_parser_pos_only_joint_features_p8_named_lever
status: SOLVED
bar: "PASS = the POS-only joint features vectorized via a precomputed integer POS-feature table + numpy gather (word features stay in Python), with PROVABLY BYTE-IDENTICAL parse heads + labels + margins on a held-out sentence set (emission-matrix-level identity, P8's witness pattern) and a measured further speedup on a warm read. NO new dependency (numpy only). A located NEGATIVE -- the POS-only features cannot be cleanly separated/vectorized byte-identically (a named coupling), or the gather does not beat the current dict path -- is a FULL PASS. Strategy lands the Q111 change (default-ON, the witness is the gate)."
result: "Vectorized construction is BYTE-IDENTICAL to the landed hdlab fast path across 434,330 held-out arcs (5 docs never tuned on): flat feature-id stream (values+order), arc scores, heads, arcs, AND per-token margins all bit-identical (==). Speedup 2.0-2.6x over the landed fast path on a warm read (interleaved median; grows with length: 1.12x at 11-15 tokens -> 2.62x at 51+). Shipping design = length-gated (vec for n>=12, scalar fast path below): also byte-identical, and 1.135x end-to-end warm read (median of 5, 3 docs, output identical), no regression."
floor: "The LANDED hdlab fast path (ArcParser.parse = sentence_flat + np.add.reduceat), itself 3.5x over stock. Time floor = that path's warm parse time (this must be BEATEN). Correctness floor = its EXACT heads+arcs+margins, which the vectorized path must reproduce bit-for-bit (it does: 434,330 arcs, 0 mismatch). Both met simultaneously."
controls: "(1) BYTE-IDENTITY at the flat-INTEGER-id-stream level (exact, stronger than score-level): 434,330 arcs, 0 mismatch -- excludes a speedup that silently changed the parse. (2) HELD-OUT: 5 docs never used to design the tables -- excludes overfitting. (3) INFO-FREE CONTROL: a corrupted POS table (one row perturbed) BREAKS the flat-id identity -- proves the check has teeth (a fast-but-wrong vectorization is caught). (4) WEIGHT-INVARIANCE: on RAW float64 weights (not the float32-round-tripped asset) the vec path is bit-identical to the fast path, 153/153 sents -- excludes 'identity is a fluke of these weights' and proves survival of parser retraining. (5) FAIR TIMING: interleaved same-process medians; a machine-CONCURRENCY confound (an apparent 0.85x end-to-end while a second process ran) was identified and eliminated by a clean single-process re-measurement. (6) GATED = byte-identical: the shipping length-gated path is also bit-identical to hdlab.parse (434k arcs / 379 sents, 0 mismatch)."
files_changed: "experiments/exp_arc_parser_posfeat_profile_v1.py, experiments/exp_arc_parser_posfeat_vectorize_v1.py, experiments/exp_arc_parser_posfeat_read_delta_v1.py, experiments/exp_arc_parser_posfeat_diagnose_v1.py, experiments/exp_arc_parser_posfeat_generalize_v1.py, experiments/exp_arc_parser_posfeat_clean_bench_v1.py, verification/test_arc_parser_posfeat_vectorize.py (NO hdlab/ change -- proposed Q111 diff described below for strategy to land)"
reverify: ".venv/Scripts/python.exe verification/test_arc_parser_posfeat_vectorize.py"
---

# The arc parser's POS-only joint features, vectorized byte-identically (2.0-2.6x over the landed fast path)

## What I built
The landed P8 fast path scores every arc by building a flat int64 feature-id array in a FIXED order
and reducing it with one `np.add.reduceat` -- but it still assembles that array in an O(n^2) per-arc
Python loop (~11M `dict.get` + ~11M `list.append` per read, profiled: the loop body + these two calls
ARE the remaining cost; the reduceat is already negligible). I replaced the per-arc Python assembly
with a numpy construction that produces the IDENTICAL flat array:
- **The 8 POS-only joint features** (`hp_dp`, `hp_dp_dir`, `hp_dp_dist`, `hpl_hp_dp`, `hpr_hp_dp`, `bV`,
  `bP`, `dp_bn`) are gathered from a precomputed **closed-tagset integer table** (UPOS x UPOS x
  dir/dist/between-bucket), built ONCE. Each entry == `_crc(exact original string)`, so the gathered
  ids equal `hdlab._arc_ids` exactly.
- Staying open to alternatives (owner directive), I also vectorized the 9 hoisted per-token features
  and 5 of the 6 word features (via small per-sentence `(token x POS-code)` tables) -- leaving only the
  genuinely open-vocabulary `hw_dw` word-pair in an O(n^2) table build. This is why the win (2.0-2.6x)
  exceeds the brief's ~1.2-1.4x estimate for the 8 POS features alone.
- All 20 fixed slots are numpy-SCATTERED into their exact per-arc positions; the 3 conditional tail
  features (`bV`/`bP`/`dp_bn`) via masks. Then the SAME `reduceat` over the SAME `starts`.

Byte-identity is by construction: I reproduce the exact flat id array (same integer values, same order)
and never touch the reduction -- so heads, arcs, and margins are bit-identical. Proven at scale:
**434,330 held-out arcs across 5 docs, 0 mismatch on the flat id stream, the arc scores, the heads, the
arcs, and the per-token margins** (the witness checks margins with `==`, not approx).

## The one named coupling I found (and avoided) -- why the "score-split" route would be a located negative
A tempting alternative is to sum the POS contribution and the word contribution SEPARATELY and add
them. I did NOT do this, and a research drill confirmed why it is unsound: **bit-identity of any
REORDERED or SPLIT re-summation of the arc score is coupled to the float32 round-trip in
`ArcParser.save()`/`.load()`** -- it holds only because that leaves ~29 spare float64 mantissa bits,
so every plausible per-arc summation is exact (no rounding) at this model's magnitude range. On RAW
(non-round-tripped) float64 weights, `reduceat`-vs-per-arc-`.sum()` disagree on ~19% of segments and a
split-sum on ~24% (1-2 ULP). So the score-split route is byte-identical ONLY by a quantization
coincidence -- a real located negative for THAT approach. My scatter-into-original-positions approach
sidesteps it entirely: I build the identical flat array and call the identical reduceat, so my scores
equal the landed fast path's **for any weight vector** (verified on raw float64, control 4). I add zero
new floating-point risk; the pre-existing fast-vs-reference float32 dependency is unchanged.

## Speedup -- honest, at two levels
- **Parser microbench (warm, interleaved median):** 2.0-2.6x over the LANDED fast path, growing with
  sentence length (per-bucket, OMP=1, clean): 1-5 tok 0.24x, 6-10 0.77x, **11-15 1.12x**, 16-20 1.32x,
  21-30 1.65x, 31-50 1.95x, 51-120 2.62x. The vectorization's per-sentence numpy setup only pays off
  once O(n^2) is large, so it REGRESSES on very short sentences. Crossover ~11 tokens.
- **End-to-end warm read:** the parser scoring is only ~7-26% of a warm read (measurement-dependent;
  the reader has many organs), so the read-level ceiling is inherently modest. Clean single-process
  measurement (median of 5, 3 docs): the length-gated design gives **1.135x end-to-end, output
  byte-identical**. An earlier apparent 0.85x "slowdown" was a machine-CONCURRENCY confound (a second
  benchmark process running), eliminated by the clean re-run.

## Shipping design: length-gated hybrid (robust to any corpus)
`sentence_scores_auto`: use the vectorized path for `n >= 12`, the existing scalar fast path below it.
Both are byte-identical, so the gate is a pure performance choice -- and it makes the win robust to ANY
sentence-length distribution (a short-sentence-heavy corpus never regresses). The shipping gated parser
is proven byte-identical to `hdlab.parse` (witness W6). Small-array numpy ops (gather/scatter/reduceat/
indexing) are single-threaded; run under the reader's normal capped-thread config.

## GENERALIZATION (owner asked: does this survive a growing/redesigned knowledge base?)
Yes, and this is architecturally robust, not incidental:
- **Decoupled from the KB.** `hdlab/arc_parser.py` imports only `zlib`/`typing`/`numpy` -- nothing from
  foundation/stores/KB. It is a syntactic frontend (tokens + POS -> heads/margins), upstream of the
  meaning channel. Byte-identical output means the KB receives identical parse input; growing or
  redesigning the KB cannot perturb the parser, and the parser cannot perturb the KB.
- **Survives retraining** (a bigger/modified KB corpus). The tables store feature IDs (crc32 of the
  string templates + closed tagset), NOT weights; the trained weight vector is gathered at scoring
  time. Control 4 proves vec == fast bit-exact on raw float64 weights, so WHAT the parser learns is
  irrelevant to correctness.
- **Survives a modified tagger.** The tag universe is auto-derived from the wired tagger asset (not
  hardcoded); a novel tag stays byte-identical to `_arc_ids` after a table rebuild (G2), and an
  out-of-universe tag FAILS LOUD (G3) -- no silent corruption.
- **The technique transfers to your typed-knowledge direction.** The pattern is: closed-inventory
  features -> precompute an integer table + numpy gather; open-vocabulary -> stay scalar; never split
  the reduction. If the larger KB feeds TYPED selectional-preference features into the parse (the
  P8-audit lexical-grounding wall), those live over a closed inventory (~45 WordNet supersenses, ~40
  deprels) -> same table+gather, cheap even cubed. It also transfers to the POS tagger (co-dominant
  warm-read cost, same feature-scoring shape).

## Proposed hdlab/ change (Q111 -- strategy lands it)
In `hdlab/arc_parser.py`, keep `_arc_ids`, `_decode`, `sentence_flat`, `sentence_scores`,
`decode_from_scores`, `_parse_reference`, `train_arc` UNCHANGED (the scalar fast path stays as the
n<THRESH branch AND the byte-identity reference the witness checks against). Add:
- `_bucket_idx`, `PosTables` (built ONCE from the wired `PosTagger`'s tag inventory + specials
  ROOT/<S>/<E> -- so a modified tagger auto-adapts; fail loud on an unknown tag), `sentence_flat_vec`,
  `sentence_scores_vec`, and `sentence_scores_auto` (the length gate) -- bodies in
  `experiments/exp_arc_parser_posfeat_vectorize_v1.py`;
- give `ArcParser.__init__` a `self._T = PosTables(...)`; route `ArcParser.parse` and `eval_uas` scoring
  through `sentence_scores_auto(sent, self.avg, self._C, self._T)` instead of `sentence_scores`.
Public API, return types, and every output byte-identical. Land default-ON (pure byte-identical speedup,
no invariant to break, per no-default-off; the witness is the gate). No `BRAIN_FOUNDATIONAL_AUDIT.md`
fidelity change (output identical).

## KEY REALIZATIONS
- **Byte-identity forbids splitting the float sum; it does NOT forbid a faster CONSTRUCTION of the same
  input.** The whole win is rebuilding the identical flat id array with numpy scatter/gather instead of
  a Python loop, then calling the same reduceat. The provable path (identical integer id stream) beat
  the clever-but-fragile one (split the score -> only byte-identical by a float32 quantization fluke).
- **Verify at the id-STREAM level, not the score level.** Asserting the flat int64 arrays are equal
  (integers, exact) is a strictly stronger and cleaner proof than comparing floats, and it made the
  byte-identity guarantee unconditional in the parser weights.
- **A microbench win can be a read-level loss.** The parser is only ~7-26% of a warm read, and the raw
  vectorization regresses on short sentences; a length gate + a clean (non-concurrent) measurement
  turned an apparent 0.85x end-to-end into a real 1.135x. "DO NOT QUOTE a speedup without the
  byte-identity proof at scale" extends to "and without an unconfounded end-to-end number."
- **The tables store IDs, not weights** -- which is exactly what makes the optimization survive
  retraining on a larger knowledge base.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md)
No fidelity verdict moves (output is bit-identical). Note for the arc-parser entry: the landed fast
path now has a vectorized, byte-identical POS-feature-table construction available for n>=12; the parse
algorithm and feature template remain PINNED and unchanged (pure implementation, per P8). The parser
imports nothing from the knowledge base -- confirming it is a decoupled syntactic frontend.

## ADJACENT COMPONENTS (next-problem seeds)
- **POS tagger inner-loop SPEED** (co-dominant warm-read cost; same sparse-feature-scoring shape). The
  same closed-inventory-table + gather technique applies -- highest-value, byte-identical follow-on
  (P8 already named it).
- **Typed selectional-preference features in the parse** (the P8-audit lexical-grounding wall). If the
  larger KB adds them, they are a closed-inventory feature class -> this exact vectorization scales to
  them. That is both a fidelity lever (PP-attachment) AND a place the technique generalizes.
- **The reduceat-vs-reference float32 coupling** is a latent fragility: if the parser is ever retrained
  and persisted WITHOUT the float32 round-trip, `parse()` (fast) would diverge from `_parse_reference`
  in low-bit margins (heads unaffected). Worth a raw-float64 canary in the parser's own test suite.

## What I did NOT establish / would withdraw first
- **The exact read-level factor.** 1.135x is a clean median-of-5 but warm reads have ~15-20% variance;
  the honest claim is "modest, always-paid, no regression," not a precise multiplier. The parser-level
  2.0-2.6x (byte-identical) is the solid headline and clears the bar. This is the first thing I'd
  withdraw if a larger clean board timing disagreed.
- **The precise ~7% vs ~26% parser share of a read** (mine vs P8's) -- doc- and reader-config-dependent;
  either way the parser is a modest, always-paid slice.

---
## TLDR
The grammar parser was still rebuilding millions of tiny text features per document in slow one-at-a-time
Python. I moved that assembly into fast batched array math -- computing the part-of-speech features from a
small lookup table built once, and fetching everything in a few big operations -- while producing the
EXACT same parse (proven identical on 434,330 attachment decisions across five books it was never tuned
on, down to the last bit of every confidence score). The parser is 2.0-2.6x faster on longer sentences;
because it is a modest slice of a full read and the batched math has a fixed per-sentence cost that only
pays off on longer sentences, I added a length switch (batched for longer sentences, the old fast path
for short ones) so it never slows anything down, giving about 1.1x on a whole document with identical
results. It generalizes cleanly: the parser is completely separate from the knowledge base you are
growing, the optimization survives retraining the parser on a bigger corpus (it stores feature labels,
not learned numbers), it adapts automatically to a modified tagger, and the same technique will speed up
the tagger and any future typed-knowledge features.

## QUESTIONS
None blocking. One optional decision for strategy: land the length-gated vec path default-ON now (the
witness is the gate), or first dispatch a clean full-board timing run for an exact read-level number.

## NEXT STEPS
1. Strategy re-verifies via the one-line witness (`verification/test_arc_parser_posfeat_vectorize.py`,
   6/6) and lands the Q111 diff above (default-ON; gated at n>=12).
2. File the POS-tagger inner-loop SPEED optimization (same closed-inventory-table technique, different
   code path) -- the co-dominant warm-read cost.
3. If/when the larger KB adds typed selectional-preference features to the parse, apply this
   vectorization to them (closed inventory -> table + gather) -- fidelity AND speed in one move.
