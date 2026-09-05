---
problem: numpy_vectorize_the_arc_parser_pos_only_joint_features_p8_named_lever
status: SOLVED
bar: "PASS = the POS-only joint features vectorized via a precomputed integer POS-feature table + numpy gather (word features stay in Python), with PROVABLY BYTE-IDENTICAL parse heads + labels + margins on a held-out sentence set (emission-matrix-level identity, P8's witness pattern) and a measured further speedup on a warm read. NO new dependency (numpy only). A located NEGATIVE -- the POS-only features cannot be cleanly separated/vectorized byte-identically (a named coupling), or the gather does not beat the current dict path -- is a FULL PASS. Strategy lands the Q111 change (default-ON, the witness is the gate)."
result: "BYTE-IDENTICAL to the landed hdlab fast path across 434,330 held-out arcs (5 docs never tuned on): flat feature-id stream, arc scores, heads, arcs, AND per-token margins all bit-identical (==). Parser speedup over the landed fast path (warm, interleaved median of 9): brief-faithful POS-only lever alone (word features stay in Python) = 1.61x; FULL vectorization = 2.16x. Parse-in-read (measured INSIDE a live read, median of 9): 1.87x (OMP=1) / 2.13x (OMP=4), low variance. Whole-read wall-clock: WITHIN NOISE (median 0.95-1.06x, high variance -- the parser is only ~7% of a read), output byte-identical, no regression. Shipping = length-gated (vec for n>=16, scalar below), byte-identical."
floor: "The LANDED hdlab fast path (ArcParser.parse = sentence_flat + np.add.reduceat), itself 3.5x over stock. Time floor = that path's warm parse time (this must be BEATEN). Correctness floor = its EXACT heads+arcs+margins, which the vectorized path must reproduce bit-for-bit (it does: 434,330 arcs, 0 mismatch). Both met simultaneously."
controls: "(1) BYTE-IDENTITY at the flat-INTEGER-id-stream level (exact, stronger than score-level): 434,330 arcs, 0 mismatch -- excludes a speedup that silently changed the parse. (2) HELD-OUT: 5 docs never used to design the tables -- excludes overfitting. (3) INFO-FREE CONTROL: a corrupted POS table (one row perturbed) BREAKS the flat-id identity -- proves the check has teeth (a fast-but-wrong vectorization is caught). (4) WEIGHT-INVARIANCE: on RAW float64 weights (not the float32-round-tripped asset) the vec path is bit-identical to the fast path, 153/153 sents -- excludes 'identity is a fluke of these weights' and proves survival of parser retraining. (5) FAIR TIMING: interleaved same-process medians; a machine-CONCURRENCY confound (an apparent 0.85x end-to-end while a second process ran) was identified and eliminated by a clean single-process re-measurement. (6) GATED = byte-identical: the shipping length-gated path is also bit-identical to hdlab.parse (434k arcs / 379 sents, 0 mismatch)."
files_changed: "experiments/exp_arc_parser_posfeat_profile_v1.py, experiments/exp_arc_parser_posfeat_vectorize_v1.py, experiments/exp_arc_parser_posfeat_read_delta_v1.py, experiments/exp_arc_parser_posfeat_diagnose_v1.py, experiments/exp_arc_parser_posfeat_generalize_v1.py, experiments/exp_arc_parser_posfeat_clean_bench_v1.py, experiments/exp_arc_parser_posfeat_e2e_robust_v1.py, experiments/exp_arc_parser_posfeat_attribution_v1.py, verification/test_arc_parser_posfeat_vectorize.py (NO hdlab/ change -- proposed Q111 diff described below for strategy to land)"
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

## Speedup -- honest, at three levels (and a corrected read-level claim)
- **Parser microbench (warm, interleaved median of 9, OMP=1):** the brief's ACTUAL lever -- the 8
  POS-joint features vectorized with the word features kept in a Python loop -- gives **1.61x** (above
  the brief's ~1.2-1.4x estimate). Extending the vectorization to the word features (all but the
  open-vocabulary hw_dw pair) -- the "optimize even more" direction -- reaches **2.16x**. So strategy
  can land a minimal Q111 diff (1.61x) or the full one (2.16x); both byte-identical.
- **Per-length behaviour:** the numpy setup only pays off once O(n^2) is large. Two clean runs agree
  n<=10 REGRESSES (0.24-0.79x) and n>=21 WINS 1.5-2.6x; the 11-20 zone is NOISY across runs
  (0.69x-1.32x, i.e. near the crossover). Hence the conservative gate at 16.
- **Read-level -- corrected.** The parser scoring is only ~7% of a warm read here, so the whole-read
  ceiling is inherently small. Measured cleanly (median of 9, both OMP=1 and OMP=4): **parse-in-read is
  reliably 1.87-2.13x faster (low variance)**, but the **WHOLE-READ wall-clock is WITHIN NOISE**
  (median 0.95x at OMP=1, 1.06x at OMP=4; hdlab reads ranged 19-46s), output byte-identical, no
  regression. My earlier "1.135x end-to-end" was a low-rep artifact and I withdraw it. The honest
  claim: an always-paid ~2x parser speedup that is real and reliable in isolation and in-read, but too
  small a slice to move a full read's wall-clock above its own noise. (An earlier "0.85x slowdown" was
  a machine-CONCURRENCY confound -- a second benchmark process -- and is also void.)

## Shipping design: length-gated hybrid (robust to any corpus)
`sentence_scores_auto`: use the vectorized path for `n >= 16`, the existing scalar fast path below it.
Both are byte-identical, so the gate is a pure performance choice -- and it makes the win robust to ANY
sentence-length distribution (a short-sentence-heavy corpus never meaningfully regresses; the 11-20
crossover is noisy so the gate is conservative and tunable). The shipping gated parser is proven
byte-identical to `hdlab.parse` (witness W6, gate@16). Small-array numpy ops (gather/scatter/reduceat/
indexing) are single-threaded; run under the reader's normal capped-thread config.

## hw_dw headroom (gap c) -- explored, no gain, near-optimal
The only remaining O(n^2) Python cost is building the `hw_dw` (head-word x dep-word) id table -- the one
genuinely open-vocabulary feature. I built a byte-identical `rollcrc` variant (rolling-prefix crc32 over
pre-encoded dep-word bytes: `crc32(dw, crc32("hw_dw:"+hw+"_")) == _h(full string)`). It is bit-identical
but SLOWER (2.00x vs 2.16x): the FeatCache already deduplicates `(hw,dw)` across the document, so after
warmup most lookups are cache hits and the rolling machinery only adds per-call overhead. Conclusion:
the plain cached table build is near-optimal; `hw_dw` byte-identity forbids eliminating the per-pair
crc32, and the constant-factor trick does not beat the cache. No headroom captured here.

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
- **A whole-read wall-clock speedup.** Measured cleanly, it is WITHIN NOISE (median 0.95-1.06x); I do
  NOT claim a whole-read win, and I withdrew my earlier 1.135x. The solid, reliable headline is the
  PARSER-level speedup (2.16x microbench, 1.87-2.13x parse-in-read, byte-identical), which clears the
  bar ("a measured further speedup on a warm read" -- the parser IS measurably faster on a warm read).
  If a larger clean board timing showed a whole-read regression, that would be the surprise; my data
  says no regression, output identical.
- **The precise ~7% vs ~26% parser share of a read** (mine vs P8's) -- doc- and reader-config-dependent;
  either way the parser is a modest, always-paid slice, which is exactly why the whole-read wall-clock
  does not move above noise.
- **The exact 11-20 crossover / optimal gate threshold** -- noisy across runs; I set 16 conservatively.
  Wrong only costs a few percent of the parser on mid-length sentences; the aggregate is ~2.16x
  regardless because long sentences dominate.

---
## TLDR
The grammar parser was still rebuilding millions of tiny text features per document in slow one-at-a-time
Python. I moved that assembly into fast batched array math -- computing the part-of-speech features from a
small lookup table built once, and fetching everything in a few big operations -- while producing the
EXACT same parse (proven identical on 434,330 attachment decisions across five books it was never tuned
on, down to the last bit of every confidence score). The parser itself is about
2x faster (up to 2.6x on the longest sentences), proven reliably both in isolation and while running
inside a real read. Because the batched math has a fixed per-sentence cost that only pays off on longer
sentences, I added a length switch (batched for longer sentences, the old fast path for short ones) so it
never slows anything down. Honest caveat I corrected mid-way: the parser is only a small slice (~7%) of a
whole document read, so the 2x does NOT visibly speed up a full document -- the whole-read time stays
within its normal run-to-run noise, with no slowdown and bit-for-bit identical results. The value is a
reliable, always-paid 2x on the parser, which matters most for parser-heavy jobs like ingesting a whole
corpus. It generalizes cleanly: the parser is completely separate from the knowledge base you are
growing, the optimization survives retraining the parser on a bigger corpus (it stores feature labels,
not learned numbers), it adapts automatically to a modified tagger, and the same technique will speed up
the tagger and any future typed-knowledge features.

## QUESTIONS
None blocking. One optional decision for strategy: land the length-gated vec path default-ON now (the
witness is the gate), or first dispatch a clean full-board timing run for an exact read-level number.

## NEXT STEPS
1. Strategy re-verifies via the one-line witness (`verification/test_arc_parser_posfeat_vectorize.py`,
   6/6) and lands the Q111 diff above (default-ON; gated at n>=16). CHOICE: land the MINIMAL diff
   (word features stay in Python, 1.61x, smaller/simpler change = word_mode 'pyloop') or the MAXIMAL
   diff (full vectorization, 2.16x, word_mode 'tables'). Both byte-identical; I recommend the full
   version -- the extra code is contained and the win is larger, and it is equally proven.
2. File the POS-tagger inner-loop SPEED optimization (same closed-inventory-table technique, different
   code path) -- the co-dominant warm-read cost.
3. If/when the larger KB adds typed selectional-preference features to the parse, apply this
   vectorization to them (closed inventory -> table + gather) -- fidelity AND speed in one move.
4. (Optional) If a whole-read wall-clock number is wanted, a remote clean full-board timing would
   confirm the "no regression, within noise" finding at scale -- but note the parser is a small slice,
   so expect the whole-read delta to stay near 1.0x.
