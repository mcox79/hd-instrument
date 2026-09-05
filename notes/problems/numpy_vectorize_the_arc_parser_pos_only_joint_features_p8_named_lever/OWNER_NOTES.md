---
owner_verdict: DONE
---

SOLVED (pending your verdict) — numpy_vectorize_the_arc_parser_pos_only_joint_features_p8_named_lever (opus 4.8 solver)

Write-up: notes/problems/numpy_vectorize_the_arc_parser_pos_only_joint_features_p8_named_lever/SOLVED.md
Reverify (reruns NO landed cell): .venv/Scripts/python.exe verification/test_arc_parser_posfeat_vectorize.py   # 6/6

WHAT SHIPS: a BYTE-IDENTICAL numpy vectorization of the arc parser's feature-id construction. The landed P8
fast path still assembled the flat feature-id array in an O(n^2) per-arc Python loop (~11M dict.get + ~11M
list.append/read). I rebuild the IDENTICAL flat int64 array (same values, same order) via numpy scatter of
precomputed-table gathers, then the SAME reduceat -- so heads+arcs+margins are bit-identical by construction.
POS-only joint features come from a closed-tagset integer table (built once); staying open to alternatives
(owner directive) I also vectorized the hoisted + reducible word features, leaving only the open-vocabulary
hw_dw pair. NO hdlab edit (Q111 diff described in SOLVED); NO new dependency; NO LLM.

RESULT (5 held-out docs never tuned on):
- BYTE-IDENTICAL across 434,330 arcs: flat id stream, arc scores, heads, arcs, AND per-token margins all == .
  Verified at the integer-id-stream level (strongest possible). Witness 6/6 incl. an info-free control with
  teeth (a corrupted POS table breaks the identity) and the shipping length-gated path proven identical.
- PARSER SPEEDUP over the already-landed fast path (warm, interleaved median of 9, OMP=1):
    brief-faithful POS-only lever alone (word features stay in Python) = 1.61x   (brief estimated ~1.2-1.4x)
    FULL vectorization (all but hw_dw)                                  = 2.16x
    per-length: n<=10 regresses (0.24-0.79x), n>=21 wins 1.5-2.6x, 11-20 noisy -> conservative length gate @16.
- READ-LEVEL (honest, corrected): parse-in-read is reliably 1.87x (OMP=1) / 2.13x (OMP=4), low variance; but
  the WHOLE-READ wall-clock is WITHIN NOISE (median 0.95-1.06x, output identical, no regression) because the
  parser is only ~7% of a read. I WITHDREW an earlier 1.135x (low-rep artifact). The value is a reliable,
  always-paid ~2x on the PARSER (matters for parser-heavy jobs: corpus ingest, eval_uas), not a whole-read win.

NAMED COUPLING found + AVOIDED: bit-identity of any REORDERED/SPLIT re-summation (e.g. POS-partial+word-partial)
is coupled to the float32 round-trip in ArcParser.save()/.load() (research drill: ~19-24% ULP disagreement on
raw float64). My scatter-into-ORIGINAL-positions approach never reorders the sum, so it equals the landed fast
path for ANY weights -- proven on raw float64 (153/153). The split-sum route would have been a located negative.

GENERALIZATION (owner asked -- does it survive a growing/redesigned KB?): YES.
- Decoupled: arc_parser imports only zlib/typing/numpy; byte-identical output -> KB gets identical input.
- Survives retraining (bigger KB corpus): tables store feature IDs not weights -> vec==fast bit-exact on raw
  float64. Survives a modified tagger: tag universe auto-derived from the wired asset; novel tag byte-identical;
  unknown tag fails loud. Technique transfers to typed KB features (closed inventory -> table+gather) and to the
  POS tagger (co-dominant cost, same feature-scoring shape).

hw_dw HEADROOM (explored, no gain): a byte-identical rolling-crc hw_dw build is SLOWER (2.00x vs 2.16x) -- the
FeatCache already dedups across the document, so the plain table build is near-optimal. No headroom captured.

files: experiments/exp_arc_parser_posfeat_{profile,vectorize,read_delta,diagnose,generalize,clean_bench,
e2e_robust,attribution}_v1.py + verification/test_arc_parser_posfeat_vectorize.py (6/6). NO hdlab written.
Ledger malformed/incomplete: 0. AUDIT UPDATE: no fidelity move (output bit-identical); parser confirmed a
KB-decoupled syntactic frontend.

Q111 DIFF (strategy lands): add PosTables/_bucket_idx/sentence_flat_vec/sentence_scores_vec/sentence_scores_auto
(tag universe from the wired PosTagger; fail loud on unknown tag); route ArcParser.parse/eval_uas via the
length-gated scorer (vec for n>=16, unchanged scalar fast path below AND as the byte-identity reference).
Keep _arc_ids/_decode/sentence_flat/sentence_scores/_parse_reference UNCHANGED. Default-ON (witness is the gate).
CHOICE: minimal diff (word features in Python, 1.61x) or maximal (full, 2.16x) -- both byte-identical; I
recommend maximal.

NEXT STEPS: (1) land Q111 (minimal-or-maximal); (2) file the POS-tagger inner-loop SPEED opt (same technique);
(3) apply this vectorization to typed selectional-preference features if the larger KB adds them (fidelity+speed).

KEY REALIZATIONS: (a) byte-identity forbids splitting the float sum, NOT a faster CONSTRUCTION of the same input
-- rebuild the identical integer id stream + same reduceat. (b) Verify at the id-stream level (integers, exact),
not the score level -- makes the guarantee unconditional in the weights. (c) A microbench win can vanish at the
read level: the parser is ~7% of a read, so 2x parser -> whole-read within noise; a clean high-rep, single-process
measurement corrected both a false 1.135x win and a false 0.85x slowdown (a concurrency confound).
