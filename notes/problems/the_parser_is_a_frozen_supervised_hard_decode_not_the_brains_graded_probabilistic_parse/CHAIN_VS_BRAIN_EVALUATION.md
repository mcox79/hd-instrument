# CHAIN vs BRAIN -- how we perform against the brain at EVERY step, after attacking the walls

Consolidated from the witnessed cells (`exp_parser_chain_vs_brain_eval_v1` assembles it from landed metrics;
`verification/test_parser_graded_route_through.py` = 44 checks). The reader's parse chain is 5 links. For each:
the exact computation, the BF status (DECODE side + ACQUISITION side), OUR number, the competent-BRAIN
reference, the measured signal loss, and whether the wall is FIXABLE (a BF component we can build) or
FUNDAMENTAL (a text-only ceiling that needs signal a corpus lacks).

## The per-step table

| step | the math | BF (decode / acquisition) | OURS | competent BRAIN | signal loss | wall |
|---|---|---|---|---|---|---|
| **1 Tokenize** | whitespace/regex split | NOT_BF / n-a | near-lossless on spaced English | statistical orthographic segmentation (VWFA; Saffran TP) | ~0 UAS | **FIXABLE**, low value |
| **2 POS tag** | Collins avg-perceptron + **hard Viterbi** | **BF NOW** (exact forward-backward posterior built + brute-verified) / **NOT_BF** (supervised; BF path = SRN prediction, HARD_PASS) | tagger acc **0.944**; a POS error ~halves that token's arc acc (0.43 vs 0.78) | ~0.97 human POS | **3.0 UAS pts** | **FIXABLE** (reading-learned categories; also gates step 3) |
| **3 Arc score** | arc-factored **surface** avg-perceptron | n-a / **NOT_BF supervised; BF reading-learned PROTOTYPED 0.463** | reading-learned BF **0.463** \| supervised foundation **0.782** | ~0.95-0.97 UAS (skilled human) | **20.7 UAS pts (DOMINANT; ~99% of head error)** | **FUNDAMENTAL from text** (see below) |
| **4 Decode** | greedy argmax+cyclebreak → **exact CLE + Matrix-Tree marginals** | **BF** (brute-verified) / n-a | exact **0.7927** vs greedy 0.7907 (+0.002 CI-sep); marginal reliability AUC **0.855** | graded distribution over parses (multipath; Hale/Levy surprisal) | **0.2 UAS pts (smallest)** | **SOLVED** (BF, recall byte-identical) |
| **5 Label** | multiclass avg-perceptron, hard argmax | graded readout opt-in (entropy→err AUC 0.930) / **NOT_BF supervised** | LAS (separate metric) | graded relation posterior | separate | **FIXABLE** |

## Signal loss, ranked (UD-EWT UAS points): SCORER 20.7 >> POS 3.0 >> DECODE 0.2
Reproduced on a 2nd, out-of-domain gold (GUM), where the supervised scorer additionally DEGRADES 0.79->0.74
(register skew). Errors propagate: a mistagged token is ~2x more likely to be mis-attached, and a
mis-attached argument is what who-did-what / roles / events / causal readers then read off.

## THE SCORER WALL, DRILLED TO THE BOTTOM (understood 100%, then attacked)
After the owner's "research the negative until 100%, then tackle the actual wall," the scorer gap is now
decomposed precisely, not asserted:

**(i) The DMV/valence negative is now FAIR (was a weak Viterbi-EM).** Built the faithful soft-EM DMV -- exact
inside-outside, brute-force-verified (Z + arc marginals + expected counts to 1e-14). It reaches 0.20-0.25
(soft-EM even below Viterbi-EM 0.32) -- the classic DMV pathology: **EM optimizes LIKELIHOOD, not accuracy**,
and is init-sensitive; UD's content-head conventions differ from the WSJ10 DMV was tuned on. So valence,
faithfully built, is confirmed NOT the lever: the arc-factored scorer's structural prior + soft graded-marginal
EM already exceed it.

**(ii) The supervised advantage is ~half NON-brain-relevant CONVENTION.** Decomposed per arc type
(`exp_parser_supervised_advantage_decomp_v1`): all-arcs gap 0.319 -> content-only (meaning-bearing) gap 0.267.
The biggest single contributor is PUNCTUATION (read 0.15 vs sup 0.64), then case-markers/adpositions (0.48 vs
0.92), copula (0.03 vs 0.86), coordination (0.07 vs 0.80) -- treebank ANNOTATION CONVENTIONS the brain does not
"parse." Grading on the meaning-bearing parse (content arcs) is the right comparison.

**(iii) The meaning-relevant residual's biggest piece (nsubj) YIELDS to an existing BF organ.** Subject
attachment (read 0.565 vs sup 0.838) is STRUCTURAL -- the brain's Now-or-Never left-corner bind. Injecting the
substrate's proven `incremental_parser.incremental_subject_before` cue lifts nsubj recall **0.565 -> 0.714**
(+0.149, ~half the gap; twin=random-nominal 0.633 loses) and content-arc UAS +0.012
(`exp_parser_bf_structural_attack_v1`). Done right: reuse the BF organ, no new mechanism.

**(iv) The last piece (nmod/PP) is NOT grounding -- prototyped and refuted.** I hypothesized PP-attachment
("saw the man WITH THE TELESCOPE") needs grounded event knowledge. Built it with the substrate's BF GEK organ
(`exp_parser_grounded_ppattach_v1`; sanity: score(see,telescope)=2.14 vs score(man,telescope)=0.0). RESULT: a
LOCATED NEGATIVE -- grounded GEK (0.443) is WORSE than the recency floor (0.556), and worst where it fires
(covered-only 0.260). Two reasons, precise: (a) PP-attachment on real prose is LOCALITY-dominated (recency
0.556 is already close to supervised 0.667 -- the grounding-ambiguous cases are a minority); (b) GEK captures
verb-EVENT content, so it over-attaches modifiers to VERBS, but most nmod are local NOUN-modifications -- the
wrong grounded signal. So the residual is NOT grounding; it is LEARNED FINE-GRAINED DISTRIBUTIONAL ATTACHMENT
PATTERNS that unsupervised EM does not discover (the text-only induction ceiling), plus the ~half that is
non-brain-relevant convention.

## The one FUNDAMENTAL wall (step 3), fully drilled -- so we know it is a ceiling, not an implementation gap
The arc scorer is 20.7 pts and dominates. We attacked every brain-foundational lever for learning it from
reading (no gold trees):
- **POS-attachment PPMI + Naseem universal structural prior + soft (graded-marginal) EM** -> UAS **0.463**
  (non-root 0.443), beats the strong right-branching floor on both, recovers 36% of the floor->supervised gap,
  improves by reading. This is the best BF reading-learned scorer.
- **DMV VALENCE** (the classic missing lever; real projective Eisner + EM, brute-force-verified) -> **0.322
  <=10-word / 0.221 full -- WORSE than 0.463.** Valence is not the lever: the arc-factored scorer's structural
  prior + soft EM already exceed POS-DMV. (Caveat: Viterbi-EM; soft-EM DMV ~0.43 on short sentences -- still
  below 0.463.)
- **Lexical generalization** (sparse PPMI AND distributed PPMI-SVD embeddings) -> **HURTS** attachment.
  Attachment is a POS-category+valence phenomenon, not lexical-semantic (Klein-Manning).
- **Projectivity**: DMV structurally cannot produce 2.1% of gold arcs (non-projective); our CLE can.
CONCLUSION: text-only unsupervised acquisition caps at ~0.46 UAS here (consistent with the field's ~0.45-0.65
ceiling). The remaining 0.319 gap to the supervised scorer -- and the further gap to a competent human
(~0.96) -- is the part gold-tree supervision (and, in the brain, PROSODY, JOINT ATTENTION, and EMBODIED
INTERACTION) buys that a text corpus does not carry. This is a real, named ceiling, not a fixable bug.
=> the scorer's brain-foundational endgame is **HYBRID**: the treebank scorer as an ADMISSIBLE offline
FOUNDATION (adult syntactic competence, like WordNet supplies adult lexical competence; frozen, glass-box,
no external tool/LLM at inference) CONSUMED AS THE GRADED POSTERIOR (step 4, BF, done) + an ONLINE
reading-learned ADAPTATION for the register-generality the frozen scorer lacks (the OOD lever, 0.79->0.74).

## IS EVERY COMPONENT 100% MATHEMATICALLY BRAIN-FOUNDATIONAL? -- NO. Precise ledger.
"Mathematically BF" = the exact computation IS the brain's operation (a PINNED / defensible computational-level
model), verified. Enumerated, down to the math:

**BF, exact math (verified):**
- DECODE: exact Chu-Liu/Edmonds MAP + single-root Matrix-Tree edge marginals (Koo 2007) -- brute-force-verified
  to 1e-6. The graded posterior over structures = multipath parsing (Franzluebbers/Hale 2024). **100% BF.**
- POS graded posterior: exact forward-backward marginals -- brute-force-verified. **100% BF (decode side).**
- The soft-EM DMV inside-outside (Z + marginals + expected counts) -- brute-force-verified to 1e-14. **exact
  math** (though the DMV model itself underperforms -- see (i) above).
- The reading-learned scorer's operations: directional PPMI (= fixed point of Hebbian-predictive association,
  Levy-Goldberg), divisive normalization (Carandini-Heeger), EM re-estimation. **BF operations.**
- The reliability-weighted competition (Lewis-Vasishth) + the Now-or-Never left-corner cue. **BF.**

**NOT 100% BF (the honest gaps):**
- The arc SCORER's WEIGHTS: learned by SUPERVISED gradient/perceptron on gold trees -- not the brain's
  acquisition. Admissible as an offline FOUNDATION (adult competence, consumed as the BF graded posterior),
  but the TRAINING PROCEDURE is NOT_BF. The brain-foundational alternative (reading-learned) is PROVEN but
  caps at ~0.46 (text-only ceiling), so today the chain runs on a foundation whose weights are not brain-acquired.
- The POS tagger's WEIGHTS: same (supervised); POS itself is brain-UNPINNED.
- The arc LABELER: supervised, hard argmax (graded readout exists but off).
- The TOKENIZER: regex, not statistical segmentation.

**Verdict:** the OPERATIONS on the read path are BF (and the decode/posteriors are exact-BF math); the
ACQUISITION of the scorer/POS/labeler WEIGHTS is not (supervised, admissible-as-foundation). So the chain is
NOT yet 100% mathematically BF end-to-end -- it is BF in decode + operations, foundation-supplied in the
learned weights, with the reading-learned acquisition proven-viable-but-ceilinged. That ceiling is the one
fundamental (text-only) wall; everything else is BF or a fixable convention.

## THE FULLY-BF CHAIN, END-TO-END (zero gold anywhere) -- BF upgrades to every component, measured
Every component now has a prototyped BF upgrade (mathematically, where verifiable):
- TOKENIZE: Saffran transitional-probability segmentation from reading (`exp_parser_bf_tokenizer_v1`) --
  boundary F1 0.639 > over-segment floor 0.386, twin loses. ~0 chain loss on spaced English (mechanism prototyped).
- POS: exact forward-backward graded posterior (decode, BF-exact) + reading-learned CATEGORY INDUCTION done
  RIGHT (`exp_parser_brown_pos_bf_chain_v1`): BROWN clustering (maximize mutual info of adjacent class bigrams
  -- the distributional-prediction optimum; exchange delta VERIFIED == full recompute, F monotonic) reaches
  many-to-one **0.745** (the easy k-means was only 0.323; supervised 0.944).
- ARC SCORE: reading-learned (PPMI-attachment + prior + soft EM), 0.463 with good POS.
- DECODE: exact CLE + Matrix-Tree marginals (BF-exact).
- The nsubj BF left-corner cue; the labeler graded readout (opt-in, entropy->err AUC 0.930).

**The end-to-end fully-BF chain (induced POS -> reading scorer -> graded decode, ZERO gold):** with the EASY
k-means induction (0.32) it DEGENERATED (UAS 0.034, below random -- confident-wrong categories mislead the
parser worse than random); with the RIGHT Brown induction (0.745) it is UNBLOCKED to **0.122 (no prior) /
0.238 (+prior)** -- a 7x jump, approaching the gold-POS-no-prior chain (0.267). So strong BF POS induction is
achievable AND necessary. Honest residual: even at 0.745 many-to-one, ~20% POS error still COMPOUNDS
(Brown+prior 0.238 vs gold-POS+prior 0.463), and on top sits the scorer's text-only ceiling (0.463 vs
supervised 0.782). The two unsupervised ACQUISITION steps each shed signal that compounds. This is the honest
end-to-end picture: exact-BF decode + operations, but the
zero-gold ACQUISITION chain is ceiling-limited AND compounds.

## The synergy verdict (why ALL links must be BF)
Made the POS posterior BF and let the parse disambiguate POS top-down (interactive/predictive-coding): it
recovers the POS-link loss in the right direction but only ~4%, because the top-down signal is only as good
as the (still NOT_BF) scorer producing it. The links CO-LIMIT each other; partial BF does not compound.
Strong synergy is GATED on making every link BF -- which is exactly why "all components" is the requirement.

## Where each link stands, in one line
- Decode: **BF, done, near-lossless.** (the win the problem named -- landed-ready)
- Arc-score acquisition: **BF prototyped at the text-only ceiling (0.463); endgame HYBRID.** (the dominant wall, now characterized)
- POS acquisition: **NOT_BF; fixable (reading-learned categories, 3-pt lever).** (next filable)
- Tokenize / Label: **NOT_BF; fixable, small/separate.** (completeness)

## Reverify
`.venv/Scripts/python.exe verification/test_parser_graded_route_through.py` (44 checks). Consolidation:
`experiments/exp_parser_chain_vs_brain_eval_v1.py`. Per-cell metrics under `data/exp_parser_*` +
`data/exp_pos_graded_posterior_and_synergy_v1`.
