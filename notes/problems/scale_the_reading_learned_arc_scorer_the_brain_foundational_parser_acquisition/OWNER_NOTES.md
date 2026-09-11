---
owner_verdict: DONE
---

SOLVER SUBMISSION — scale_the_reading_learned_arc_scorer_the_brain_foundational_parser_acquisition

STATUS: PARTIAL (the bar's blessed dual outcome — a genuine capability result on the reader's own metric PLUS a
numbered located negative). Glass-box, NO gold/treebank/LLM at inference anywhere, NO hdlab/ writes (Q111 — results
+ proposed diffs; strategy lands). Threads capped at 2. READ FIRST in the problem folder: SOLVED.md (§13 the full
chain trace + math-BF verdicts; §14 the deepening log; §15 the component ledger + real mathematical BF status; §16
next priority steps; the self-assessment section). Reverify: .venv/Scripts/python.exe
verification/test_readlearned_arc_scorer_scale.py  (94 checks).

THE BAR RESULT (the reader's OWN metric, verb->argument extraction; both scorers into the SAME graded marginal):
the reading-learned scorer, read as a graded DISTRIBUTION (top-2 marginal reach = the brain's keep-alternatives-
alive), MATCHES the frozen supervised scorer's deployed extraction in-domain (UD-EWT: 0.9356 vs 0.9283, +0.0073
CI[-0.005,+0.019] = parity) and BEATS it out-of-domain (GUM: 0.9202 vs 0.8967, +0.0235 CI[0.015,0.033] CI-SEP) —
with NO treebank at inference, info-free twin LOSING (0.44/0.40). The supervised scorer degrades OOD; the reading-
learned one holds — the register-generality/HYBRID win. LOCATED NEGATIVE (also a full pass): at full UD-EWT scale
the reading-learned SCORER caps at UAS ~0.48 (raw) / content-UAS 0.5828 (fully optimized, all constructions) vs
supervised 0.80/0.77 — the PINNED text-only acquisition ceiling (Klein-Manning). SCALE IS NOT THE LEVER (0-EM UAS
flat 2k->12k); EM peaks at round 2 then declines (likelihood != accuracy); online/Hebbian re-estimation and joint
POS-parse co-adaptation both DRIFT (the Lateen anti-drift gate catches them) — the residual is posterior QUALITY /
the disambiguation signal text lacks, NOT the optimizer.

THE FULLY-BF CHAIN (owner directive: make ALL upstream BF, verify mathematically, push to brain functionality).
Every parse link now has a brain-foundational path — no gold/treebank/LLM: tokenize (orthographic) -> POS
(closed-class-scaffold syntactic bootstrapping + morphology, 0.71 many-to-one, NAMED so the prior+constructions
fire) -> arc-score (reading-learned PPMI + Naseem prior + DMV-EM + a 5-family construction library) -> decode
(gain-calibrated MBR over the Matrix-Tree marginal) -> label (Competition-Model word-order relations). The fully-BF
chain (nothing supervised anywhere) reaches content-UAS 0.4366 / LAS 0.27, recovering ~79% of the gold-POS chain.
Registry-confirmed: the LIVE pos_tagger/arc_parser/arc_labeler are NOT_BF (supervised perceptrons); this work
provides a BF-acquisition replacement for each. The chain is traced + math-verified end-to-end (SOLVED §13).

KEY WINS across the deepening (each twin-controlled, BF): the NP-internal-modifier construction (new, biggest
single construction lever); marker-triggered CLAUSAL constructions (content-UAS +0.032; xcomp/ccomp/advcl more than
double); filler-gap RELATIVE-CLAUSE attachment (acl 0.013 -> 0.394 — the earlier NULL was a PRIOR-PENALTY problem,
not missing signal); MBR decode (fixes the hard distributed arcs); gain calibration (Carandini-Heeger divisive
normalization — makes calibrated-MBR strictly dominate MAP); Competition-Model relation labeler (rel-acc 0.64 vs
supervised 0.72, treebank-free); the full 5-family stack lifts content-UAS 0.478 -> 0.583 with ALL families
COMPLEMENTARY (drop-one ablation). LOCATED NEGATIVES (BF mechanisms faithfully built that LOST): online-EM,
2nd-order sibling readout (treebank-free bootstrapping wall), Hindle-Rooth prep-specific PP cue (nmod ambiguity-
limited: prep-specific increment marginal, not twin-separated), multi-conjunct (rare). A PER-CONSUMER config
tradeoff found by re-measuring the bar: the content-UAS-optimal full stack is NOT verb->arg-optimal (the aggressive
relcl/clausal boosts distort the argument marginals) — weight constructions per consumer (light for extraction,
full for content-UAS).

COMPONENT / MATHEMATICAL BF STATUS (full table SOLVED §15). PINNED (the brain's exact equation): the Matrix-Tree
E-step (Koo 2007, brute-verified), MBR decode (Smith-Smith 2007), gain calibration (Carandini-Heeger), the
directional-PPMI acquisition (Saffran/Harris). BF_SPIRIT (defensible computational model OR a SUPPLIED universal
structural bias — honest: the distributional backbone is learned-from-reading, but the Naseem prior + construction
cues + scaffold word-list + relation map are SUPPLIED universal knowledge, swept, NOT learned): the scaffold POS
inducer, all construction families, the Competition-Model labeler, Hindle-Rooth, the referential feature. NOT_BF
(the live links this replaces): the supervised pos_tagger/arc_parser/arc_labeler.

HONESTY CORRECTIONS I made against myself: an earlier draft cited an unsourced "McRae 1998 0.51/0.37/0.12" weight —
REMOVED (the primary PDF does not contain it); the sourced anchor is Ratnaparkhi 1994 (88.2% lexical-tuple / 93.2%
full-context). I retracted the "nmod is a pinned ceiling" claim (verification shows it is MISSING-STATISTIC regime,
not missing-grain). I corrected "read-out is the lever" (it is 1/3 of the residual) and "acl is out-of-scope" (acl
ATTACHMENT is recoverable in-scope; the prior penalty was the wall).

NEXT PRIORITY STEPS (SOLVED §16): (1) LAND the gain-calibrated MBR decode + reliability-gated adaptive-k readout
(ready now, recall byte-identical). (2) WIRE the reading-learned scorer as a register-general SECOND track
(reliability-gated), constructions weighted PER CONSUMER. (3) FILE the POS-acquisition sibling (0.71 -> 0.94, the
gating link; owns pos_tagger_is_a_notbf...). (4) BUILD the cross-sentence referential PP feature (coref compat
candidate-count — verified-real, routes to the coref/reader). (5) ROUTE the deep residuals: filler-gap ROLE ->
the_relcl_parser_is_too_weak; event/prosody disambiguation -> the generative world-model (the named main event).

FILES: 21 experiment cells (experiments/exp_readlearned_*.py) + verification/test_readlearned_arc_scorer_scale.py
(94/94) + SOLVED.md. No hdlab/ modified. HONEST BOUNDS: the downstream match/beat is RL-read-as-distribution vs
SUP-committed (a weaker point scorer read the brain's way + SUP's OOD degradation, at a precision cost); text-only
acquisition is genuinely capped below supervised (the located negative). QUESTIONS: none blocking. Ledger clean
(malformed 0). Awaiting owner_verdict: DONE.
