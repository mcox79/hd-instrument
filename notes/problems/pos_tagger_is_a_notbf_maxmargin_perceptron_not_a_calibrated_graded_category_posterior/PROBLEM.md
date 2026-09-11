# PROBLEM — the reader's POS tagger is a NOT_BF max-margin perceptron, and the "POS third" of the who-was-affected signal loss is unexplained

**slug:** `pos_tagger_is_a_notbf_maxmargin_perceptron_not_a_calibrated_graded_category_posterior`
**opened:** 2026-09-10 (solver full-auto), as the POS cluster brief named in
`harm_help_valence_.../HANDOFF_POS_PARSER_PLAN.md` §3 Step A. **status:** OPEN.
Solver writes `experiments/`, `verification/`, this folder only. NO `hdlab/` (Q111 — strategy lands; propose diffs).
Glass-box, **NO external LLM at inference**; a persisted offline-trained static model is admissible. THE DISK OUTRANKS
THE BRIEF. Full report discipline (TLDR / QUESTIONS / NEXT STEPS, plain language).

## The defect
The reader tags POS with `hdlab/pos_tagger.py` (`__bf_status__ = NOT_BF`): a supervised averaged **max-margin
perceptron** (Collins 2002) with **hard Viterbi** that — per its own `__bf_note__` — "discards marginals." The brain's
lexical category is not a hard max-margin label; it is a **graded, calibrated, distributionally-acquired belief that
syntax resolves jointly** (Harris 1954 distributional category; Kuperberg-Jaeger 2016 calibrated graded category;
MacDonald/Pearlmutter/Seidenberg 1994 constraint satisfaction — category and structure decided together, not
tag-then-parse). The signal-loss trace (`exp_fd_harm_help_signal_trace_v1`, from the harm/help cluster) attributes
**~30 % of the lost who-was-affected undergoers to POS** (full 0.7895 → gold-POS 0.8581).

## The bar
PASS = rebuild the tagger's category decision brain-foundationally (a distributional/calibrated **graded** category
posterior, not a supervised max-margin hard commit) and **recover the who-was-affected POS third CI-separated over the
current live perceptron floor** on modern gold, info-free twin LOSING, no downstream regress — **OR a rigorous LOCATED
NEGATIVE** that names + quantifies exactly why a standalone tagger cannot recover it (with numbers, the brain-faithful
stronger version actually tested), routing the residual to the responsible component. Grade on MODERN gold (UD-EWT;
19c banned as load-bearing). Report CI half-width; recompute floors on the item's own population.

## First steps (discipline)
- **PRIOR-WORK CHECK (mandatory):** the owner-**DONE** `upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior`
  already (a) built the calibrated glass-box CRF (`hdlab/crf_tagger.py`, pure-numpy forward-backward marginals),
  (b) found the JOINT parse-decode a **located negative** on the 19c verb-AUROC axis (+0.0017 over the calibrated
  posterior), (c) established the CRF is **default-off / gated on a live consumer**. Read that SOLVED.md IN FULL first —
  this cluster must EXTEND, not re-discover it (the open angle is the *who-was-affected undergoer* metric + the general
  tag set, which that problem did not measure).
- Understand the organs in the read chain: `pos_tagger`, `crf_tagger`, `arc_parser`/`graded_parser`, `arc_labeler`,
  `causation_typing._frontend`, and the signal-trace scoreboard.

> **BRAIN-FOUNDATIONAL CHECKLIST (ordered):** 1) which brain structure computes lexical category, replicate or
> substitute? 2) is the computation copied EXACTLY (distributional acquisition; graded calibrated posterior; joint
> category-syntax resolution) and every PARAMETER swept, never adopted? 3) is each upstream/downstream organ in the
> chain BF, or is a non-BF component silently capping this? 4) measure vs the strongest floor on its OWN population,
> CI-separated; info-free twin must lose. 5) FULL-STACK-UPSTREAM: if the lever is upstream (the arc scorer) or
> downstream, name + quantify it and route it. **PHASE-DIAGRAM note:** the substrate may move anywhere on the
> density/dim/binding/scorer phase diagram per organ — a wall "at this config" = MOVE the operating point, not a ceiling.


<!-- GUARD SECTIONS (appended by strategy 2026-09-11 for brief-cert conformance; the fleet brief above is the primary statement, SOLVED.md is authoritative). -->
## THE PROBLEM IN PLAIN LANGUAGE
The reader tags parts of speech with a hard max-margin perceptron (NOT_BF) that throws away its graded confidence. The brain's lexical category is a graded, calibrated, distributionally-acquired belief that syntax resolves jointly. See the fleet statement above and SOLVED.md.

## WHY THIS ONE
pos_tagger is one of the NOT_BF defects and part of the shared parser-cluster wall that caps who-was-affected recall.

## MEASURED vs INFERRED
MEASURED: pos_tagger NOT_BF, hard Viterbi discards marginals. INFERRED (now found): a standalone calibrated-tagger fix is REFUTED as the lever; the residual routes to a JOINT POS+parse graded decode consuming the CRF marginals. See SOLVED.md.

## ALREADY TRIED
The standalone calibrated-graded-tagger fix (refuted as a standalone lever). Do not re-run it in isolation. See SOLVED.md + HANDOFF_POS_PARSER_PLAN.

## VERIFY BEFORE YOU START
A persisted offline-trained static model is admissible; no external tagger/LLM at inference. Read SOLVED.md + harm_help_valence.../HANDOFF_POS_PARSER_PLAN.md IN FULL. Cap cores (OMP_NUM_THREADS=4 ...).

## THE BAR
See "## The bar" above: deliver the calibrated graded category posterior / the joint decode with a number, or a rigorous located negative naming exactly why standalone POS is not the lever.

## FILES AND ENTRY POINTS
hdlab/pos_tagger.py; hdlab/crf_tagger.py; the parser cluster (hdlab/arc_parser.py, hdlab/graded_parser.py); experiments/ POS cells + witnesses.

## DO NOT QUOTE
Retired figures (notes/reference_retired_claims_never_requote.md); no external tagger / LLM at inference; no 19c corpora.
