---
owner_verdict: DONE
---

SOLVER SUBMISSION — replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop

STATUS: SOLVED. Glass-box, NO LLM, NO hdlab/ writes (Q111 — a verified result + proposed change; strategy lands).
Reverify: .venv/Scripts/python.exe verification/test_graded_read_ranker.py (23/23). Threads were capped (OMP/OpenBLAS/
MKL/NumExpr=2) on all runs. Deliverables in the problem folder: SOLVED.md, BF_AUDIT.md (top-down math-verified BF audit +
non-BF register), KNOWLEDGE_LEVER.md (idea-database catalog); 7 tagged experiment cells + witness.

WHAT IT FOUND (the arc):
1. LOCATED NEGATIVE on the brief's premise (disk-verified): the live grounding-loop RANKING is ALREADY a graded cosine
   population read (canonicalize_fast, GRADED_COMPARATOR on since 2026-08-14); the attractor is confined to the exact-match
   recognition gate — its correct job — where swapping it for a population read is a measured no-op (-1.4e-5, CI incl 0),
   and hub over-promotion only appears at soft temps the gate never uses. "Replace the attractor readout" buys nothing.
2. THE REAL LOSS IS THE REPRESENTATION, not the computation. On the loop's own sense-assignment ranking (independent
   SimLex gold, rank the true synonym), the live random-symbol cue carries ~0 identity signal; feeding real meaning lifts
   it far above incumbent + info-free twin.
3. THE KEY KNOWLEDGE = RELATIONAL / IS-A IDENTITY. Knowledge moves the bar ~214x (full fusion 0.342 vs shuffled 0.0016),
   and ONE kind carries it: relational is-a identity (alone MRR 0.318; removing it collapses the fusion 3x, leave-one-out
   +0.227 CI[+0.178,+0.280]). Grounded adds a small real +0.013; learned-substitutability and raw co-occurrence are
   redundant/null with the taxonomy present. It is LEARNABLE from reading (a no-ontology dependency channel recovers ~half
   the ceiling and RISES monotonically with reading volume; well-read words reach 0.21 approaching the ontology's 0.35).
4. FULLY-BF COMPOSITION IS THE BEST CHAIN. Top-down math audit verified every operation (cosine=divisive normalization;
   fusion=Bayes cue integration; PPMI=Hebbian-predictive; z-score/IDF/random-projection all BF). Composing ONLY the
   BF/BF_SPIRIT components with equal-weight Bayes (NO fitted params) BEATS the mixed chain that keeps the NOT_BF bag +
   gold-calibrated weights (+0.028 CI-sep) and the pre-audit fix (~5.7x), twin losing. Owner's thesis confirmed on the
   number: all-BF is the best chain and needs zero tuned knobs.

NON-BF ITEMS FOUND + WHAT I DID (full register in BF_AUDIT.md): DROPPED/REPLACED in-experiment — the unordered bag channel
(→ learned structured channel; all-BF then won) and per-item peakedness precision (→ equal-weight Bayes). PARTIAL LEARNED
REPLACEMENT BUILT — dependency-learned identity for the WordNet-supplied taxonomy (foundation-plus-grow). TESTED, MEASURED
NULL, KEPT — Euclidean-in-z grounded read (-0.012) and labeled deprels (-0.013, + costs BF). PROPOSED (Q111/architecture) —
wire the relational-identity channel into the ranking; online Hebbian learning; a probabilistic population-code
representation. GAP (no BF replacement exists) — a BF GENERAL dependency parser (incremental_parser is role-specialized).
NO CHANGE NEEDED — the attractor-as-ranker (already remediated). Naming convention applied: all mechanism cells carry the
machine-checkable __bf_status__ tag (VERIFIED_BF_LEDGER convention; checker passes); per-organ hdlab tag values proposed in
BF_AUDIT.md.

HIGH-PRIORITY NEXT STEPS:
1. (biggest live lever — strategy, Q111) Wire the RELATIONAL / IS-A IDENTITY channel into canonicalize_fast's ranking
   (fused equal-weight with grounded); reserve the attractor for recall; de-sign the reference canonicalize fallback.
   Recall path byte-identical.
2. (brain-foundational trajectory) GROW the learned identity channel by structured reading at volume — it converges toward
   the supplied ontology's ceiling with no ontology (the grow-by-reading north-star).
3. (the one measurement not yet done) End-to-end: after wiring, re-run a grounding pass and measure downstream grounding
   COVERAGE (the growth metric), info-free twin losing.
4. (deep BF residuals, mapped) a BF general dependency parser; a probabilistic population-code meaning representation.

HONEST BOUNDS: absolute performance is GOOD not EXCELLENT (MRR 0.34, hit@10 0.58 — below a competent reader); the chain is
brain-foundational with named BF_SPIRIT residuals (not a finished 100%-BF endpoint); the win is proven on the sense-
assignment RANKING (faithful proxy, independent gold), NOT yet on the live end-to-end grounding-coverage outcome; nothing
landed in hdlab (by design). QUESTIONS: none blocking.

TLDR (plain English): The step we were told to fix was already fixed — the system ranks meaning the right, brain-like way.
Digging in, what holds it back isn't HOW it computes but WHAT IT KNOWS: give it a database of which concepts ARE the same
kind of thing (is-a / synonym relations) and its accuracy jumps ~200x; take that one knowledge away and it collapses.
Grounded "how it looks/feels" helps a little, raw word-company nothing, and two tempting engineering tweaks measured as no
help. The more it reads, the more it learns that same knowledge itself. So the fix is a relational identity "idea database"
— supplied now, grown by reading — and the fully brain-foundational build (no tuned knobs) is the best-performing one.
