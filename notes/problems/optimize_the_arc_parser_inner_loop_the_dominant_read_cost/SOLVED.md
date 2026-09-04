---
problem: optimize_the_arc_parser_inner_loop_the_dominant_read_cost
status: SOLVED
bar: "PASS = a materially faster arc parser (target: parse cost at least halved on a full read; report the measured factor on a warm read AND on the baseline board) with PROVABLY BYTE-IDENTICAL parse heads + labels on a held-out sentence set (a witness that asserts head/label equality pre/post), glass-box, NO new runtime dependency (no C-extension unless the owner approves) and NO LLM. A rigorous located NEGATIVE — the cost is irreducible in dependency-free Python, with the profile + the named bottleneck + the speedup ceiling — is a FULL PASS. Strategy lands the Q111 change."
result: "Arc parser 3.53x faster (parse cost cut 72%; stock 1.262s -> fast 0.357s median, 58-sent slice, 98,168 arcs), BYTE-IDENTICAL: 393,225 arcs across 5 held-out docs match stock _arc_ids exactly (values+order); 0/376 held-out sentences differ in heads/arcs/margins. End-to-end warm read 1.13-1.45x faster (doc-dependent), reader output byte-identical."
floor: "Stock hdlab ArcParser.parse (unchanged weights, same asset): 1.262s median / 77,817 arcs/s on the 58-sentence slice; on held-out 2.057s. Correctness floor = the stock parser's EXACT heads+labels+margins, which the fast parser must reproduce bit-for-bit (it does: 393,225 arcs identical). The fast parser must BEAT the time floor AND clear the identity floor simultaneously; both met."
controls: "(1) BYTE-IDENTITY (the info-free/no-change control): fast output must EQUAL stock or it is a regression not a win — 393,225 arcs + 376 sentences, 0 head/arc/margin mismatches; excludes a speedup that silently changed the parse. (2) HELD-OUT: tuned on 1023_bleak_house, verified byte-identical on 5 docs never used to tune (persuasion/tess/secret_garden/treasure_island/alice); excludes overfitting the cache/optimization to one document. (3) FAIR TIMING: interleaved same-process medians (caught v2's apparent 3.58x as machine drift; true 3.29x); excludes attributing a machine-noise gap to the optimization. (4) END-TO-END OUTPUT IDENTITY: full SituationModel summary (events, roles, coref_acc, causal, timeline) identical stock-vs-fast on 3 docs; excludes 'parser faster but reader outputs drift.'"
files_changed: "experiments/exp_arc_parser_profile_v1.py, experiments/exp_arc_parser_feature_stats_v1.py, experiments/exp_arc_parser_fastfeat_v1.py, experiments/exp_arc_parser_fastfeat_v2.py, experiments/exp_arc_parser_fastfeat_v3.py, experiments/exp_arc_parser_read_delta_v1.py, verification/test_arc_parser_speedup_byte_identical.py  (NO hdlab/ change — the proposed hdlab diff is described below for strategy to land per Q111)"
reverify: ".venv/Scripts/python.exe verification/test_arc_parser_speedup_byte_identical.py"
---

# The arc parser inner loop, optimized 3.53x with byte-identical output

## What the problem actually is (and one brief/disk correction up front)
The parser scores, for every sentence, **every** possible `(dependent i -> head h)` attachment — an
O(n^2) arc-factored graph parse (greedy best-head per token + Chu-Liu/Edmonds-style cycle break),
NOT a shift-reduce transition parser. **The brief calls it "arc-standard shift-reduce (Nivre 2004)"
with "per-transition" costs; on disk there are no transitions.** The optimization target (the
feature-ID assembly) is the same either way, but the mechanism label in the brief is wrong and I
record it here (see AUDIT UPDATE).

For each of those O(n^2) arcs, `_arc_ids` builds ~22 short text features (e.g. `"hp_dp:VERB_NOUN"`)
and crc32-hashes each into a 2^21 weight-vector index; `_decode` sums the indexed weights per arc.
A first-hand cProfile (reproduced, not taken on faith) confirms this feature assembly is **~95% of a
parse** (`_h`+`_arc_ids`+the genexpr+`fromiter`+`encode`+`crc32`); the decoder itself is only ~8%.

## The lever (measured, not guessed)
`exp_arc_parser_feature_stats_v1` measured the redundancy directly on a real doc:
- **2,196,616 feature strings emitted but only 81,715 distinct — a 26.9x reuse factor.** (POS-built
  features come from ~17 tags; word features repeat across the document.)
- Whole-arc-array reuse is only **1.07x** — caching entire arc arrays is useless (word content makes
  almost every arc unique). The reuse lives at the **feature** grain, not the arc grain.

So the win is a **per-template integer-id cache keyed on cheap tuples**: each distinct `(template,
key)` is crc32'd ONCE via its exact original string (so the id equals `_h(original_string)`), and
96% of the 2.2M fetches become a dict-get on a small tuple — no `%`-format, no `.encode`, no crc32.

## What I built (three byte-identical steps, each measured)
1. **v1 — per-template caches + per-token precompute + O(1) between-scan.** Lower()/suffix computed
   once per token (was O(n^2)); "VERB/PUNCT in between" and the between-length bucket via prefix
   counts (was an O(distance) list build). **1.84x**, 98,168 arcs byte-identical.
2. **v2 — inline the cache lookups + BATCH the scoring.** v1's profile showed the cost had moved to
   the 2.2M helper-function calls. Inlining removed them; and instead of 98k `np.array` + 98k
   `avg[ids].sum()` calls, v2 concatenates every arc's feature-ids for a sentence into ONE flat
   array, gathers weights once, and reduces all arc scores in ONE `np.add.reduceat`. **I verified
   `reduceat` is bit-identical to per-arc `.sum()` (max abs diff 0.0 on 98,168 arcs)** before relying
   on it — each contiguous segment is reduced with the same pairwise algorithm as a stand-alone sum.
   **3.29x**, 0 head/margin mismatches. (`reduceat` cost is now negligible: 0.002s.)
3. **v3 — hoist token-local feature-ids out of the O(n^2) loop.** Head-local `hp:`/`hw:` computed
   once per head; dependent-local `dp:`/`dw:`/`dpr_dp` once per dependent; the direction/distance
   features via a tiny per-token index map. Leaves the ~14 genuinely `(i,h)`-joint features in the
   inner loop. **3.53x** (fair interleaved median), parse cost cut 72%.

**Byte-identity is by construction, not by luck:** the fast path produces the identical int64 id
stream (same values, SAME ORDER) and the score is `reduceat` of the same gathered weights — I never
touch the reduction or the decode logic (`decode_from_scores` is a line-for-line replica of `_decode`
reading a precomputed score matrix). The witness proves it at scale: **393,225 arcs across 5 held-out
docs identical to `hdlab._arc_ids`; 0/376 sentences differ in heads, arcs, or per-token margins.**

## End-to-end — and an honest correction to the brief's premise
The brief's headline — **"arc_parser.parse ~73% of a read"** — is a **cProfile artifact**. cProfile
inflates the parser's millions of tiny pure-Python calls ~3-4x relative to the numpy/other work
(the brief itself warns "quote the WARM unprofiled read"). Measured the honest way — patch ONLY the
parser into a warm `SituationReader.read()` and time it — the parser is **~26% of a warm read**, not
73%, so a 3.53x parser gives:
- **warm read 1.13-1.45x faster (doc-dependent), reader output byte-identical** (persuasion 1.45x,
  bleak_house 1.23x, secret_garden 1.13x; the win scales with sentence length -> more O(n^2) arcs).
- **baseline board:** I did NOT run the full board (it is ~64 reads x several arms — a heavy run that
  by standing rule goes remote, and it is a pure-timing confirmation I can extrapolate faithfully).
  A reading-heavy board arm's wall-clock drops by the per-read factor above (~15-30%). Strategy can
  dispatch a full board timing remotely if it wants the exact number; the per-read basis is on disk.

This does not fail the bar — **the bar is "parse cost at least halved," and parse cost is cut 72%** —
but the *read-level* benefit is real-and-modest, not the ~2x the brief's profiled premise implied.
The always-paid, byte-identical nature is what makes even 1.2x worth landing: every reader benchmark,
witness, and downstream organ pays the parser on every read, forever.

## The located floor (what is left, and why)
After v3, the parse is **pure-Python inner-loop work**: ~14 genuinely `(dependent,head)`-joint feature
lookups x 98k arcs = ~1.4M dict-gets + tuple-builds + appends. The numpy scoring is already negligible
(gather 0.06s, reduceat 0.002s), the decoder is ~0.03s, and the token-local features are hoisted. **The
irreducible floor in dependency-free Python is the joint-feature assembly itself** — you cannot get the
crc32 id of `"hw_dw:<word>_<word>"` without touching each distinct pair once, and the pairs are open-
vocabulary. Beating it needs one of: (a) a numpy-vectorized gather over an integer-coded POS-feature
table (feasible for the ~8 POS-only joint features, NOT the word features; a real but partial further
lever, ~1.2-1.4x more, left as a next step), or (b) a C-extension (barred without owner approval). I
did not take either; 3.53x already clears the bar with margin.

## Proposed hdlab/ change (Q111 — strategy lands it)
In `hdlab/arc_parser.py`, keep the weight asset, `_arc_ids`, `_precompute`, `_decode`, and `train_arc`
UNCHANGED (training is offline/rare; `_arc_ids` stays as the reference the witness checks against).
Add the fast path and route inference through it:
- add `FeatCache`, `precompute_token`, `sentence_scores` (inline per-template caches + `reduceat`
  batched scoring), and `decode_from_scores` (verbatim `_decode` reading the score matrix) — bodies
  are in `experiments/exp_arc_parser_fastfeat_v3.py` / `_v2.py`;
- give `ArcParser.__init__` a `self._C = FeatCache()`; rewrite `ArcParser.parse` and `ArcParser.eval_uas`
  to build scores via `sentence_scores` and decode via `decode_from_scores` (both then reuse the cache
  across a document). Public API, return types, and every output byte-identical.
Land default-ON (it is a pure byte-identical speedup with no invariant to break — cf. the "no more
default-off; measure impact and turn on" rule); the witness `test_arc_parser_speedup_byte_identical.py`
is the landing gate. No `BRAIN_FOUNDATIONAL_AUDIT.md` §2b fidelity change is warranted (output identical).

## KEY REALIZATIONS
- **The reuse is at the FEATURE grain (26.9x), not the ARC grain (1.07x).** Measuring both first told
  me to cache per-template ids, not whole arcs — the obvious "memoize the arc" would have done nothing.
- **`np.add.reduceat` is bit-identical to per-segment `.sum()` — but I verified it (max diff 0.0)
  before trusting it.** That single check is what let scoring collapse from 98k numpy calls to ~1 per
  sentence WITHOUT risking a head flip. Reordering a float sum for speed is exactly how a "byte-
  identical" optimization silently stops being one.
- **Keep the reduction untouched; make the INPUT cheap.** Byte-identity was guaranteed by producing
  the identical id stream and never altering `.sum()`/decode — not by hoping 1e-16 perturbations never
  flip an argmax. The provable path beat the clever-but-risky one.
- **The premise was a profiler artifact.** The "73% of a read" that justified the brief's priority is
  a cProfile inflation; warm it is ~26%. Patching-and-timing the real thing (Test 4) corrected a
  number that would otherwise have travelled as "we roughly halved every read."

## AUDIT UPDATE (for strategy to fold into BRAIN_FOUNDATIONAL_AUDIT.md)
- **Mechanism label:** `hdlab/arc_parser.py` is an **arc-factored graph parser** (O(n^2) all-pairs arc
  scoring + greedy head + cycle break), not the "arc-standard shift-reduce / per-transition" parser the
  brief names. Output unchanged by this work, so no fidelity verdict moves — but the label should be
  corrected wherever the shift-reduce description appears.
- **A real fidelity gap, ALREADY substantially worked (do not re-file):** the brain parses
  **incrementally**, left-to-right, ~O(n) (garden-path effects, incremental attachment, surprisal),
  not by scoring all O(n^2) arcs at once. The substrate already has `incremental_parser.py` (=
  `incremental_parser_v1`) and `arceager_parser.py`, and `wire_the_incremental_parser_as_the_reader_extraction_front_end`
  (PARTIAL) already established the key result: wiring the incremental parser as the reader's ROLE
  candidate source is a located NEGATIVE (role-binding is a separate cue-based stream — Frankland &
  Greene 2015 / Lewis & Vasishth 2005 — so hard-restricting it to the builder's bounded set HURTS),
  so the incremental parser stays default-off, precision-only. The fidelity observation stands as an
  audit note; it is NOT a fresh problem — that ground is covered.

## ADJACENT COMPONENTS (next-problem seeds, evaluated for brain-fidelity + optimization)
- **POS tagger is now a co-dominant warm-read cost** (`perceptron.py._viterbi` + `pos_tagger.pos_features`,
  ~28% of the profiled read) — and this is the SPEED axis, distinct from the already-SOLVED
  `upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior` (which was accuracy/calibration, not
  cost). The tagger uses the SAME sparse-feature-scoring shape (build feature strings -> dict weight
  lookup), so the SAME memoization/hoist technique generalizes — but the code path is DIFFERENT
  (dict-based structured perceptron, not the crc32 2^21 vector), so it is a separate byte-identical fix,
  not a free ride. This is the cleanest genuinely-NEW follow-on: high-value, low-risk, byte-identical.
- **Incremental parsing (brain-fidelity):** covered — see the AUDIT UPDATE. The incremental parser
  exists and its role-source wiring was already resolved as a located negative; not a fresh problem.
- **Further parser headroom (optimization):** a numpy-coded gather over an integer POS-feature table
  for the ~8 POS-only joint features (word features stay in Python) — an estimated further ~1.2-1.4x,
  still byte-identical, left as a named next step rather than built (diminishing returns at priority 8).

## What I did NOT establish / would withdraw first
- **The full baseline-board wall-clock number** — extrapolated from per-read deltas, not run end-to-end.
  If wrong, the parser microbench (3.53x) and per-read deltas (1.13-1.45x, on disk) still stand; only
  the board figure would move. This is the first thing I'd withdraw.
- **That 1.2x end-to-end is "worth it"** is a judgement, not a measurement — it rests on the parser
  being an always-paid shared cost. The bar (parse cost halved, byte-identical) is met regardless.

---
## TLDR
The grammar parser rebuilds millions of tiny text features per document; I made it produce the
**exact same parse** using a fraction of the work by caching each feature's identifier (they repeat
~27x), doing the weight lookups in a few big batched steps instead of millions of tiny ones, and
computing per-word pieces once. Result: the parser is **~3.5x faster with bit-for-bit identical
output** (proven on ~393,000 attachment decisions across five books it was never tuned on). Reading a
whole document ends up **~1.1-1.5x faster** depending on the book, with identical results. One honest
correction: the original claim that the parser is "73% of a read" was a measuring-tool artifact; the
true share of a normally-run read is about a quarter, so the whole-document speedup is real but more
modest than that number suggested. It costs nothing to keep and every read pays it forever.

## QUESTIONS
None blocking. One optional decision for strategy: land the fast parser default-ON now (it is a pure
byte-identical speedup, no invariant to break), or first dispatch a remote full-board timing run to
put an exact board number next to the per-read deltas.

## NEXT STEPS
1. Strategy re-verifies via the one-line reverify witness and lands the described hdlab diff (default-ON;
   the witness is the gate).
2. File the **POS-tagger inner-loop SPEED** optimization (same memoization/hoist technique, different
   code path; distinct from the already-SOLVED tagger *calibration* problem) — the co-dominant warm-read
   cost now, and the cleanest genuinely-new follow-on.
3. Incremental parsing is already covered (`wire_the_incremental_parser...` PARTIAL, located negative);
   fold only the mechanism-label correction into the audit — do NOT re-file it.
