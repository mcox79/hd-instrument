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
